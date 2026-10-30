"""PREREG-3 analysis: within-issue pairwise AUROC of the GGUF judge and the cheap signals.

Runs only after all N pairs exist.  The pilot's sealed scores are inputs, never read on their own.

Usage:
    .venv/bin/python scripts/analyze_judge.py --n 4226 \
        --scores out/judge/pilot_out/sealed/pilot_scores.parquet \
                 out/judge/main_out/shards/*.parquet \
        --out results/judge_analysis.json
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.prereg2 import auroc_scores, bootstrap_mean, bootstrap_sum_ratio  # noqa: E402

K = 8


def load_scores(paths: list[str]) -> pd.DataFrame:
    frames = []
    for p in paths:
        hits = sorted(glob.glob(p)) if any(ch in p for ch in "*?[") else [p]
        for h in hits:
            d = pd.read_parquet(h, columns=["trajectory_id", "p_yes", "n_tokens"])
            frames.append(d)
    assert frames, f"no score files matched {paths}"
    out = pd.concat(frames, ignore_index=True)
    assert out.trajectory_id.is_unique, "duplicate trajectory scores"
    assert out.p_yes.between(0, 1).all()
    return out


def signal_frame() -> pd.DataFrame:
    sig = pd.read_parquet(ROOT / "out/signals/nebius_openhands.parquet",
                          columns=["trajectory_id", "key", "repo", "canonical", "steps"])
    light = pd.read_parquet(ROOT / "out/nebius_light.parquet",
                            columns=["trajectory_id", "exit_status", "pred_passes_gen_tests"])
    m = sig.merge(light, on="trajectory_id", how="left", validate="1:1")
    m["trajectory_id"] = m.trajectory_id.astype(str)
    size = m.groupby(["key", "canonical"]).size().rename("cluster_size").reset_index()
    m = m.merge(size, on=["key", "canonical"], how="left", validate="many_to_one")
    m["agreement"] = m.cluster_size.astype(float) / K
    m["exit_reason"] = m.exit_status.eq("submit").astype(float)
    m["own_test"] = m.pred_passes_gen_tests.astype(float)  # NaN stays NaN
    m["own_test_null0"] = m.own_test.fillna(0.0)
    m["own_test_nullminus1"] = m.own_test.fillna(-1.0)
    return m.set_index("trajectory_id")


def verdict(lower: float, upper: float, p: float) -> str:
    if p < 0.05 and lower > 0.5:
        return "SIGNIFICANT+"
    if p < 0.05 and upper < 0.5:
        return "SIGNIFICANT-"
    return "NOT SIGNIFICANT"


def auroc_row(pairs: pd.DataFrame, signal: str, tag: str, subset: pd.Series | None = None,
              null_score: float | None = None) -> dict:
    d = pairs if subset is None else pairs[subset.to_numpy()]
    d = d[d[f"{signal}_pos"].notna() & d[f"{signal}_neg"].notna()].copy()
    if null_score is not None:
        for side in ("pos", "neg"):
            d[f"{signal}_{side}"] = d[f"{signal}_{side}"].fillna(null_score)
    s = auroc_scores(d[f"{signal}_pos"], d[f"{signal}_neg"])
    boot = bootstrap_sum_ratio(s, np.ones(len(s)), d.repo.to_numpy(),
                               seed_parts=("judge3-gguf", "auroc", tag), null=0.5)
    boot["n_pairs"] = int(len(d))
    boot["n_issues"] = int(d.key.nunique())
    boot["n_repos"] = int(d.repo.nunique())
    return boot


def paired_diff(pairs: pd.DataFrame, signal: str, tag: str) -> dict:
    d = pairs[pairs[f"{signal}_pos"].notna() & pairs[f"{signal}_neg"].notna()
              & pairs["judge_pos"].notna() & pairs["judge_neg"].notna()].copy()
    s = auroc_scores(d[f"{signal}_pos"], d[f"{signal}_neg"]) - \
        auroc_scores(d["judge_pos"], d["judge_neg"])
    boot = bootstrap_mean(s, d.repo.to_numpy(), ("judge3-gguf", "diff", tag), null=0.0)
    boot["n_pairs"] = int(len(d))
    return boot


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--scores", nargs="+", required=True)
    ap.add_argument("--out", default="results/judge_analysis.json")
    ap.add_argument("--model-label", default="26B-A4B Q4_0 (llama.cpp)")
    args = ap.parse_args()

    bundle = ROOT / "out/judge/bundle_main"
    pairs = pd.read_parquet(bundle / "pairs.parquet")
    attempts = pd.read_parquet(bundle / "attempts.parquet")
    pairs = pairs[pairs.pair_id < args.n].copy()
    assert len(pairs) == args.n, (len(pairs), args.n)

    scores = load_scores(args.scores).set_index("trajectory_id")
    sig = signal_frame()
    tids = sorted(set(pairs.pos_tid.astype(str)) | set(pairs.neg_tid.astype(str)))
    missing = set(tids) - set(scores.index)
    # Empty patches are fixed at 0 by PREREG-3 §4.3 and need no forward pass. The main shards
    # may omit them; fill them here rather than treating them as missing model output.
    empty = attempts.assign(is_empty=attempts.patch.astype(str).str.strip().eq(""))
    empty_tids = set(empty.loc[empty["is_empty"], "trajectory_id"].astype(str))
    assert missing <= empty_tids, f"missing {sorted(missing - empty_tids)[:5]} scores"
    if missing:
        fill = pd.DataFrame({"trajectory_id": sorted(missing), "p_yes": 0.0, "n_tokens": 0})
        scores = pd.concat([scores.reset_index(), fill], ignore_index=True).set_index("trajectory_id")
    assert set(tids) <= set(sig.index), f"missing {len(set(tids) - set(sig.index))} signal rows"

    out = pairs.copy()
    out["pos_tid"] = out.pos_tid.astype(str)
    out["neg_tid"] = out.neg_tid.astype(str)
    for side in ("pos", "neg"):
        tid = out[f"{side}_tid"]
        out[f"judge_{side}"] = scores.loc[tid, "p_yes"].to_numpy()
        for name in ("exit_reason", "own_test", "agreement", "own_test_null0",
                     "own_test_nullminus1"):
            out[f"{name}_{side}"] = sig.loc[tid, name].to_numpy()
    flags = attempts.set_index("trajectory_id")[["patch_truncated"]].astype(bool)
    out["pos_trunc"] = flags.loc[out.pos_tid, "patch_truncated"].to_numpy()
    out["neg_trunc"] = flags.loc[out.neg_tid, "patch_truncated"].to_numpy()

    result = {
        "analysis": "PREREG-3 within-issue pairwise AUROC (GGUF Q4_0 backend, D14)",
        "model": args.model_label,
        "backend": "llama.cpp / llama-cpp-python 0.3.36, CUDA 12.8, 2x Tesla T4",
        "n_pairs": int(len(out)), "n_issues": int(out.key.nunique()),
        "n_repos": int(out.repo.nunique()),
        "n_distinct_attempts": int(len(tids)),
        "primary": {}, "comparisons": {}, "exploratory": {}, "truncation": {},
    }

    prim = auroc_row(out, "judge", "judge")
    prim["verdict"] = verdict(prim["lower"], prim["upper"], prim["p"])
    result["primary"] = prim

    for name, label in (("exit_reason", "submit=1, max-iteration=0"),
                        ("own_test", "pred_passes_gen_tests, null excluded"),
                        ("agreement", "canonical cluster size / 8")):
        r = auroc_row(out, name, name)
        r["label"] = "SECONDARY"
        r["definition"] = label
        r["paired_diff_vs_judge"] = paired_diff(out, name, name)
        result["comparisons"][name] = r

    e2 = auroc_row(out, "own_test_null0", "own_test_null0", null_score=None)
    e2["label"] = "EXPLORATORY (E2 analogue, null -> 0)"
    result["exploratory"]["own_test_null0"] = e2

    neither = ~(out.pos_trunc | out.neg_trunc)
    either = out.pos_trunc | out.neg_trunc
    result["truncation"]["neither_patch_truncated"] = auroc_row(out, "judge", "trunc-neither",
                                                                subset=neither)
    result["truncation"]["at_least_one_patch_truncated"] = auroc_row(
        out, "judge", "trunc-either", subset=either)
    result["truncation"]["neither_pairs"] = int(neither.sum())
    result["truncation"]["either_pairs"] = int(either.sum())

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
