"""PREREG-3 feasibility probe (data side only; no judge is run, no judge output exists).

Answers four questions before the judge study is frozen:

1. Does the issue text exist for the nebius frame, and what share of the frozen K=8 issues and
   B2 pairs can be joined to it?
2. How many within-issue mixed-label pairs are available once the own-test signal's availability
   filter is dropped (the judge reads patches, not the harness's test fields)?
3. What are the token lengths of issue, patch and issue+patch under the Gemma 4 tokenizer
   (p50 / p95), and what a declared truncation rule costs?
4. What is the planning token volume for a proposed N pairs?

Labels are read only to count mixed-label pairs, exactly as `scripts/b4_cost_probe.py` does; no
signal-vs-outcome association is computed here.

Usage: .venv/bin/python scripts/prereg3_probe.py  -> results/prereg3_probe.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.configs import CONFIGS  # noqa: E402
from src.prereg2 import load_attempts, shared_keys  # noqa: E402

TOKENIZER_REPO = "google/gemma-4-26B-A4B-it"
PROBLEM = Path("out/swerebench_problem.parquet")
SWE_REBENCH_FILES = ["datasets/nebius/SWE-rebench/data/test-00000-of-00002.parquet",
                     "datasets/nebius/SWE-rebench/data/test-00001-of-00002.parquet"]


def ensure_problem_parquet() -> None:
    """Cache the instance_id -> problem_statement join; stream only those two columns."""
    if PROBLEM.exists():
        return
    import pyarrow as pa
    import pyarrow.parquet as pq
    from huggingface_hub import HfFileSystem

    fs = HfFileSystem()
    writer = None
    for path in SWE_REBENCH_FILES:
        with fs.open(path, "rb") as f:
            pf = pq.ParquetFile(f)
            for b in pf.iter_batches(batch_size=2048,
                                     columns=["instance_id", "repo", "problem_statement"]):
                if writer is None:
                    writer = pq.ParquetWriter(PROBLEM, b.schema, compression="zstd")
                writer.write_table(pa.Table.from_batches([b]))
        print(f"cached {path}", flush=True)
    writer.close()


def pctl(x, q):
    return float(np.percentile(np.asarray(x, dtype=float), q))


def main():
    PROBLEM.parent.mkdir(parents=True, exist_ok=True)
    ensure_problem_parquet()
    out = {"tokenizer": TOKENIZER_REPO, "note": __doc__.strip().splitlines()[0]}
    neb = next(c for c in CONFIGS if c["tag"] == "nebius_openhands")
    shared = shared_keys()

    # ---------------------------------------------------------------- 1. issue text
    prob = pd.read_parquet(PROBLEM)
    # The frozen frame's `key` is the casefolded instance id (DEVIATIONS D3). Join on the same form;
    # the original id is kept for the record.
    prob["key"] = prob.instance_id.astype(str).str.casefold()
    dup_text = prob.groupby("key").problem_statement.nunique()
    prob = prob.sort_values("key").drop_duplicates("key", keep="first")
    out["problem_statements"] = {
        "source": "nebius/SWE-rebench (test split, 2 parquet shards)",
        "rows": int(len(prob)),
        "unique_instance_ids": int(prob.instance_id.nunique()),
        "duplicate_instance_ids": int(len(prob) - prob.instance_id.nunique()),
        "columns": ["instance_id", "repo", "problem_statement"],
        "p50_chars": pctl(prob.problem_statement.str.len(), 50),
        "p95_chars": pctl(prob.problem_statement.str.len(), 95),
        "empty_or_null": int((prob.problem_statement.fillna("").str.len() == 0).sum()),
        "ids_with_conflicting_text": int((dup_text > 1).sum()),
    }

    light = pd.read_parquet("out/nebius_light.parquet",
                            columns=["instance_id", "trajectory_id", "resolved", "repo"])
    light["key"] = light.instance_id.astype(str).str.casefold()
    light = light[~light.key.isin(shared)]
    known_ids = set(prob.key)
    all_issues = light.key.unique()
    out["join_coverage"] = {
        "nebius_issues_all": int(len(all_issues)),
        "with_problem_statement": int(sum(i in known_ids for i in all_issues)),
        "share": float(np.mean([i in known_ids for i in all_issues])),
    }

    # ---------------------------------------------------------------- 2. frozen K=8 frame
    frame = load_attempts(neb, 8, False, shared)
    frame = frame.merge(prob[["key", "instance_id", "problem_statement"]],
                        left_on="key", right_on="key", how="left", validate="m:1")
    frame["has_issue_text"] = frame.problem_statement.notna()
    out["join_coverage"]["k8_issues"] = int(frame.key.nunique())
    out["join_coverage"]["k8_with_issue_text"] = int(frame[frame.has_issue_text].key.nunique())
    out["join_coverage"]["k8_share"] = float(frame[frame.has_issue_text].key.nunique()
                                             / frame.key.nunique())
    out["join_coverage"]["k8_attempts"] = int(len(frame))
    out["join_coverage"]["k8_attempts_with_issue_text"] = int(frame.has_issue_text.sum())

    def pair_counts(df, key):
        g = df.groupby(key).resolved.agg(pos=lambda s: int((s == 1).sum()),
                                         neg=lambda s: int((s == 0).sum()))
        g["pairs"] = (g.pos * g.neg).where((g.pos > 0) & (g.neg > 0), 0)
        return g

    per_issue = pair_counts(frame, "key").pairs
    out["pairs"] = {
        "k8_mixed_label_issues": int((per_issue > 0).sum()),
        "k8_pairs_no_signal_filter": int(per_issue.sum()),
    }

    # full pool, same exclusion and convention
    full = pair_counts(light[light.resolved.isin([0, 1])], "key").pairs
    out["pairs"]["full_pool_mixed_label_issues"] = int((full > 0).sum())
    out["pairs"]["full_pool_pairs_no_signal_filter"] = int(full.sum())
    out["pairs"]["k8_pairs_with_signal_filter_b2"] = 4226
    out["pairs"]["k8_issues_with_signal_filter_b2"] = 754

    # ---------------------------------------------------------------- 3. token lengths
    tok = Tokenizer.from_file(hf_hub_download(TOKENIZER_REPO, "tokenizer.json"))
    tok.no_truncation()
    tok.no_padding()

    def encode_len(texts, batch=512):
        lens = []
        for i in range(0, len(texts), batch):
            lens.extend(len(e.ids) for e in tok.encode_batch(texts[i:i + batch]))
        return np.asarray(lens, dtype=float)

    issues = frame.drop_duplicates("key")[["key", "problem_statement"]].dropna()
    issue_tok = dict(zip(issues.key, encode_len(issues.problem_statement.tolist())))
    patch_cache = pd.read_parquet("out/patches/nebius_openhands.parquet",
                                  columns=["trajectory_id", "patch"])
    frame = frame.merge(patch_cache, on="trajectory_id", how="left", validate="1:1")
    assert frame.patch.notna().all()
    frame["patch_tokens"] = encode_len(frame.patch.fillna("").tolist())
    frame["issue_tokens"] = frame.key.map(issue_tok).astype(float)
    assert frame[frame.has_issue_text].issue_tokens.notna().all()
    _has_text = (frame.drop_duplicates("key").set_index("key").has_issue_text
                 .reindex(per_issue.index).fillna(False).astype(bool))
    out["join_coverage"]["k8_pairs_with_issue_text"] = int(per_issue[_has_text].sum())
    ft = frame[frame.has_issue_text].copy()

    # declared truncation: issue 4,096 tokens; patch head 4,096 + tail 1,024 (6,144 cap)
    ISSUE_CAP, HEAD, TAIL = 4096, 4096, 1024
    ft["issue_used"] = ft.issue_tokens.clip(upper=ISSUE_CAP)
    ft["patch_used"] = ft.patch_tokens.clip(upper=HEAD + TAIL)
    ft["patch_truncated"] = ft.patch_tokens > HEAD + TAIL
    ft["issue_truncated"] = ft.issue_tokens > ISSUE_CAP
    ft["judgment_tokens"] = ft.issue_used + ft.patch_used + 120  # fixed prompt overhead

    def dist(x):
        return {"p50": pctl(x, 50), "p90": pctl(x, 90), "p95": pctl(x, 95),
                "p99": pctl(x, 99), "mean": float(np.mean(x)), "max": float(np.max(x))}

    out["tokens"] = {
        "issue": dist(ft.drop_duplicates("key").issue_tokens),
        "patch": dist(ft.patch_tokens),
        "judgment_raw": dist(ft.issue_tokens + ft.patch_tokens + 120),
        "judgment_truncated": dist(ft.judgment_tokens),
        "cap": {"issue": ISSUE_CAP, "patch_head": HEAD, "patch_tail": TAIL,
                "prompt_overhead": 120},
        "patch_truncated_share": float(ft.patch_truncated.mean()),
        "issue_truncated_share": float(ft.drop_duplicates("key").issue_truncated.mean()),
        "sum_raw_judgment_tokens": float((ft.issue_tokens + ft.patch_tokens + 120).sum()),
        "sum_truncated_judgment_tokens": float(ft.judgment_tokens.sum()),
        "judgments": int(len(ft)),
        "judgments_missing_issue_text": int(len(frame) - len(ft)),
    }

    # ---------------------------------------------------------------- 4. proposed N
    # B2's own CI gives the per-pair information; scale it to the candidate N.
    b2 = json.loads(Path("results/b2_within_issue_auroc.json").read_text())
    se_4226 = (b2["primary"]["upper"] - b2["primary"]["lower"]) / (2 * 1.959964)
    rows = []
    for n in [849, 2359, 4226, 5307, 6000, 12917]:
        se = se_4226 * (4226 / n) ** 0.5
        rows.append({"n_pairs": n, "se_auroc": se, "half_width_95": 1.959964 * se,
                     "min_detectable_delta_80pct": 2.801585 * se})
    out["power"] = {"observed_se_at_4226": se_4226,
                    "basis": "B2 primary CI half-width / 1.96; clustered design held fixed",
                    "rows": rows}
    # mean judgment tokens for a pair, truncated
    j = ft.judgment_tokens.mean()
    out["cost_inputs"] = {"mean_judgment_tokens_truncated": float(j),
                          "judgments_per_pair": 2,
                          "token_volume_per_1000_pairs": float(2 * 1000 * j)}

    Path("results/prereg3_probe.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
