#!/usr/bin/env python3
"""DESCRIPTIVE additions used by the paper after the audits (DEVIATIONS D16/D17).

Reads the cached signal frames and result JSONs; runs no model and computes no
hypothesis test.  Output: results/paper_addenda.json.

Usage: .venv/bin/python scripts/paper_addenda.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.configs import CONFIGS  # noqa: E402
from src.prereg2 import bootstrap_mean, load_attempts, select_signal_rep  # noqa: E402


def main() -> None:
    shared = set(pd.read_csv(ROOT / "results/excluded_shared_issues.csv").key.astype(str))
    raw_by_tag = {}
    for path in sorted((ROOT / "out/signals").glob("*.parquet")):
        raw_by_tag[path.stem] = set(pd.read_parquet(path, columns=["key"]).key.astype(str)) - shared
    keys = set().union(*raw_by_tag.values())
    assert len(keys) == 48300, len(keys)

    frame_by_tag = {cfg["tag"]: set(load_attempts(cfg, 3, shared=shared).key)
                    for cfg in CONFIGS}
    frame_union = set().union(*frame_by_tag.values())
    neb_raw = raw_by_tag["nebius_openhands"]
    nv_raw = set().union(*[v for k, v in raw_by_tag.items() if k != "nebius_openhands"])
    neb_frame = frame_by_tag["nebius_openhands"]
    nv_frame = set().union(*[v for k, v in frame_by_tag.items() if k != "nebius_openhands"])
    assert len(neb_raw) == 6102 and len(nv_raw) == 42198
    assert len(neb_frame) == 6063 and len(nv_frame) == 35010
    assert not (neb_raw & nv_raw) and len(frame_union) == 41073
    assert len(neb_raw) + len(nv_raw) == 48300
    assert len(neb_raw) - len(neb_frame) == 39
    assert len(nv_raw) - len(nv_frame) == 7188

    # Why the casefolded NVIDIA total is 42,545 but the post-overlap pool is 42,198:
    # 32 configurations, 10 of them frozen K=3 arms, so 22 non-frozen; the 143 issues occur
    # only in those 22.
    paths = pd.read_parquet(ROOT / "out/nvidia_paths.parquet", columns=["instance_id", "_src_path"])
    paths["key"] = paths.instance_id.astype(str).str.casefold()
    paths["config"] = paths._src_path.str.extract(r"^data/(.+?/[^/]+/[^/]+)/")[0]
    frozen_prefixes = {cfg["prefix"].removeprefix("data/") for cfg in CONFIGS
                       if cfg["dataset"] == "nvidia"}
    nv_all = set(paths.key)
    nv_frozen = set(paths.loc[paths.config.isin(frozen_prefixes), "key"])
    nv_only_nonfrozen = nv_all - nv_frozen
    all_prefixes = set(paths.config.dropna())
    nonfrozen_prefixes = all_prefixes - frozen_prefixes
    assert len(all_prefixes) == 32
    assert len(frozen_prefixes) == 10 and len(nonfrozen_prefixes) == 22
    assert len(nv_all) == 42545 and len(nv_frozen) == 42402
    assert len(nv_only_nonfrozen) == 143
    assert set(paths.loc[paths.key.isin(nv_only_nonfrozen), "config"]) == nonfrozen_prefixes
    assert len(nv_frozen - shared) == 42198
    assert len(nv_all - shared) == 42341

    meta = json.loads((ROOT / "results/config_metadata.json").read_text())
    arms_27b = [k for k, v in meta["arms"].items()
                if v["k"] == 3 and v["policy"] in {"Qwen3.6-27B", "Qwen3.8-27B"}]
    assert len(arms_27b) == 6, arms_27b

    b2 = json.loads((ROOT / "results/b2_within_issue_auroc.json").read_text())
    raw = b2["comparisons"]["steps"]
    judge = json.loads((ROOT / "results/judge_analysis.json").read_text())
    steps_judge = judge["exploratory"]["steps_oriented"]

    # Within-issue means on the B2 frame, equal weight per mixed-label issue.
    neb = next(c for c in CONFIGS if c["tag"] == "nebius_openhands")
    frame = load_attempts(neb, 8, shared=shared)
    light = pd.read_parquet(ROOT / "out/nebius_light.parquet",
                            columns=["trajectory_id", "exit_status", "pred_passes_gen_tests"])
    frame = frame.merge(light, on="trajectory_id", how="left", validate="1:1")
    assert len(frame) == 36640 and frame.trajectory_id.is_unique
    diffs = []
    for _, g in frame.groupby("key", sort=True):
        pos = g.loc[g.resolved.eq(1), "steps"]
        neg = g.loc[g.resolved.eq(0), "steps"]
        if len(pos) and len(neg):
            diffs.append((float(pos.mean()), float(neg.mean())))
    arr = np.asarray(diffs)
    assert arr.shape == (1160, 2), arr.shape

    out = {
        "analysis": "DESCRIPTIVE additions for the paper (DEVIATIONS D16/D17)",
        "tests": "none for B1-B5; exploratory bootstrap intervals only",
        "distinct_issues": {
            "pool_value": len(keys),
            "analysis_frame_value": len(frame_union),
            "nebius_pool": len(neb_raw),
            "nvidia_pool": len(nv_raw),
            "pool_overlap": len(neb_raw & nv_raw),
            "nebius_k3_frame": len(neb_frame),
            "nebius_dropped_below_k": len(neb_raw) - len(neb_frame),
            "nvidia_k3_frame_union": len(nv_frame),
            "nvidia_dropped_below_k": len(nv_raw) - len(nv_frame),
            "nvidia_casefold_total": len(nv_all),
            "nvidia_frozen_config_issues": len(nv_frozen),
            "nvidia_only_nonfrozen_configs": len(nv_only_nonfrozen),
            "nvidia_configs_total": len(all_prefixes),
            "nvidia_frozen_configs": len(frozen_prefixes),
            "nvidia_nonfrozen_configs": len(nonfrozen_prefixes),
            "nvidia_after_shared_total": len(nv_all - shared),
            "method": "pools: union of key sets in out/signals/*.parquet after excluding "
                      "204 shared issues; analysis frame: union of the 11 K=3 sampled frames "
                      "(only issues with at least three eligible attempts); the 143-issue gap "
                      "is the casefolded NVIDIA total minus the union of the frozen eleven "
                      "configurations, i.e. issues present only in the 22 non-frozen "
                      "configurations (32 total, 10 frozen K=3 arms)",
        },
        "nebius_k8_reuse": {
            "issues": 4580,
            "new_distinct_issues": 0,
            "method": "K=8 key set is a subset of the Nebius K=3 frame",
        },
        "arms_27b": {
            "count": len(arms_27b),
            "arms": sorted(arms_27b),
            "policies": ["Qwen3.6-27B", "Qwen3.8-27B"],
            "source": "results/config_metadata.json",
        },
        "steps_b2": {
            "raw": {"estimate": raw["estimate"], "lower": raw["lower"], "upper": raw["upper"]},
            "oriented": {"estimate": 1 - raw["estimate"], "lower": 1 - raw["upper"],
                         "upper": 1 - raw["lower"]},
            "within_issue_mixed_issues": len(diffs),
            "mean_steps_resolved": float(arr[:, 0].mean()),
            "mean_steps_unresolved": float(arr[:, 1].mean()),
            "mean_difference": float((arr[:, 0] - arr[:, 1]).mean()),
            "label": "EXPLORATORY (post-hoc orientation)",
        },
        "steps_judge_pairs": {
            "estimate": steps_judge["estimate"], "lower": steps_judge["lower"],
            "upper": steps_judge["upper"], "p": steps_judge["p"],
            "n_pairs": steps_judge["n_pairs"], "n_issues": steps_judge["n_issues"],
            "n_repos": steps_judge["n_repos"],
            "label": "EXPLORATORY (post-hoc orientation)",
        },
    }

    # E1 selection lift within exit-reason strata (post-hoc; no new outcome).
    issue_rows = []
    for key, g in frame.groupby("key", sort=True):
        g = g.set_index("trajectory_id")
        tids = sorted(g.index)
        sig = {t: (None if pd.isna(g.loc[t, "pred_passes_gen_tests"])
                   else float(g.loc[t, "pred_passes_gen_tests"])) for t in tids}
        rep = select_signal_rep(tids, sig, "nebius_openhands@K8", key, null_score=-1.0)
        labels = g.resolved.astype(int)
        submit = g.exit_status.eq("submit")
        max_iter = g.exit_status.str.startswith("RuntimeError: Agent reached")
        if bool(submit.all()):
            stratum = "all_submit"
        elif bool(max_iter.all()):
            stratum = "all_max_iteration"
        else:
            stratum = "mixed_exit"
        issue_rows.append({"key": key, "repo": g.repo.iloc[0],
                           "lift": int(labels.loc[rep]) - float(labels.mean()),
                           "stratum": stratum,
                           "selected_exit": ("submit" if bool(submit.loc[rep]) else
                                             "max_iteration" if bool(max_iter.loc[rep]) else
                                             "other")})
    issue_lift = pd.DataFrame(issue_rows)
    out["e1_selection_lift"] = {
        "label": "EXPLORATORY (D17; post-hoc stratification and availability test)",
        "overall": bootstrap_mean(issue_lift.lift, issue_lift.repo,
                                   ("nebius_openhands@K8", "select", "own_test")),
        "by_exit_composition": {},
        "by_selected_exit": {},
    }
    for stratum, g in issue_lift.groupby("stratum", sort=True):
        rec = bootstrap_mean(g.lift, g.repo, ("e1lift", stratum))
        rec.update({"n_issues": int(len(g)), "n_repos": int(g.repo.nunique())})
        out["e1_selection_lift"]["by_exit_composition"][stratum] = rec
    for stratum, g in issue_lift.groupby("selected_exit", sort=True):
        rec = bootstrap_mean(g.lift, g.repo, ("e1lift-sel", stratum))
        rec.update({"n_issues": int(len(g)), "n_repos": int(g.repo.nunique())})
        out["e1_selection_lift"]["by_selected_exit"][stratum] = rec

    # Availability test: every one of the eight attempts must carry an own-test result.
    full_rows = []
    for key, g in frame.groupby("key", sort=True):
        g = g.set_index("trajectory_id")
        tids = sorted(g.index)
        sig = {t: g.loc[t, "pred_passes_gen_tests"] for t in tids}
        if any(pd.isna(v) for v in sig.values()):
            continue
        rep = select_signal_rep(tids, {t: float(v) for t, v in sig.items()},
                                "nebius_openhands@K8", key, null_score=-1.0)
        labels = g.resolved.astype(int)
        full_rows.append({"key": key, "repo": g.repo.iloc[0],
                          "lift": int(labels.loc[rep]) - float(labels.mean())})
    full = pd.DataFrame(full_rows)
    rec = bootstrap_mean(full.lift, full.repo, ("e1lift", "fully_available"))
    z_ci = NormalDist().inv_cdf(0.975)
    z_power = NormalDist().inv_cdf(0.80)
    half_width = (rec["upper"] - rec["lower"]) / 2
    se = half_width / z_ci
    rec.update({"n_issues": int(len(full)), "n_repos": int(full.repo.nunique()),
                "label": "EXPLORATORY (D17; all eight attempts non-null)",
                "power": {
                    "alpha": 0.05, "power": 0.8,
                    "se": se, "ci_half_width": half_width,
                    "mde": (z_ci + z_power) * se,
                    "mde_pp": 100 * (z_ci + z_power) * se,
                    "pooled_lift": out["e1_selection_lift"]["overall"]["estimate"],
                    "method": "MDE = (z_0.975 + z_0.80) * SE, SE = percentile-CI half-width / "
                              "z_0.975; two-sided alpha 0.05, 80% power; normal approximation on "
                              "the repo-clustered bootstrap scale"}})
    out["e1_selection_lift"]["fully_available"] = rec
    path = ROOT / "results/paper_addenda.json"
    path.write_text(json.dumps(out, indent=1) + "\n")
    print(f"wrote {path.relative_to(ROOT)}: {len(keys):,} distinct issues, "
          f"{len(arms_27b)} 27B arms")


if __name__ == "__main__":
    main()
