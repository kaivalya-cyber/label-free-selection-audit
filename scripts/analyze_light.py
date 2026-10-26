"""Recon statistics from the lightweight parquet caches (Phase 0).

Usage: .venv/bin/python scripts/analyze_light.py nebius out/nebius_light.parquet
       .venv/bin/python scripts/analyze_light.py nvidia out/nvidia_light.parquet
"""
import json
import sys
from collections import Counter

import numpy as np
import pandas as pd

K_GRID = [1, 2, 3, 5, 8, 10, 16, 32]


def role_col(df):
    for c in df.columns:
        if c in ("trajectory", "messages"):
            return c
    return None


def aux_values(df, col):
    """Nested column selected as leaf comes back as list<struct<field>>; flatten."""
    if col not in df.columns:
        return None
    s = df[col]
    sample = next((v for v in s if isinstance(v, (list, np.ndarray)) and len(v)), None)
    if sample is None:
        return None
    if isinstance(sample[0], dict):
        key = list(sample[0].keys())[0]
        return s.map(lambda v: (v[0][key] if isinstance(v, (list, np.ndarray)) and len(v) else None))
    return s


def summarize(df, tag, cfg_cols=()):
    d = df
    n = len(d)
    out = {"tag": tag, "rows": int(n), "instances": int(d.instance_id.nunique()), "repos": int(d.repo.nunique())}
    rc = role_col(d)
    if rc:
        steps = d[rc].map(len)
        out["steps"] = {
            "mean": float(steps.mean()),
            "median": float(steps.median()),
            "p90": float(steps.quantile(0.9)),
            "max": int(steps.max()),
            "min": int(steps.min()),
        }
        if "trajectory_id" in d.columns:  # nebius: assistant msgs == steps
            pass

    # label distribution
    vc = d.resolved.value_counts(dropna=False).to_dict()
    out["resolved_counts"] = {str(k): int(v) for k, v in vc.items()}
    out["share_resolved_minus1"] = float((d.resolved == -1).mean()) if (d.resolved == -1).any() else 0.0
    known = d[d.resolved.isin([0, 1])]
    out["share_resolved_1_known"] = float((known.resolved == 1).mean()) if len(known) else None

    # trajectories per instance
    per = d.groupby("instance_id").size()
    out["traj_per_instance"] = {
        "mean": float(per.mean()),
        "median": float(per.median()),
        "p90": float(per.quantile(0.9)),
        "p99": float(per.quantile(0.99)),
        "max": int(per.max()),
        "hist": {str(k): int(v) for k, v in per.value_counts().sort_index().head(30).items()},
    }
    out["instances_ge_K"] = {str(k): int((per >= k).sum()) for k in K_GRID}
    out["rows_in_instances_ge_K"] = {str(k): int(per[per >= k].sum()) for k in K_GRID}

    # mixed labels (instances with >=2 known labels, both 0 and 1)
    g = known.groupby("instance_id").resolved.agg(["count", "sum", "min", "max"])
    multi = g[g["count"] >= 2]
    both = multi[(multi["min"] == 0) & (multi["max"] == 1)]
    all1 = multi[multi["min"] == 1]
    all0 = multi[multi["max"] == 0]
    out["label_mix"] = {
        "instances_with_ge2_known": int(len(multi)),
        "instances_mixed": int(len(both)),
        "share_mixed_of_ge2": float(len(both) / len(multi)) if len(multi) else None,
        "instances_all_resolved": int(len(all1)),
        "instances_all_unresolved": int(len(all0)),
        "per_issue_resolve_rate_mean": float(multi["sum"].div(multi["count"]).mean()) if len(multi) else None,
    }
    # mixed per K threshold
    out["label_mix_by_K"] = {}
    for k in K_GRID:
        if k < 2:
            continue
        sub = multi[multi["count"] >= k]
        b = ((sub["min"] == 0) & (sub["max"] == 1)).sum()
        out["label_mix_by_K"][str(k)] = {
            "instances": int(len(sub)),
            "mixed": int(b),
            "share_mixed": float(b / len(sub)) if len(sub) else None,
        }

    # issues per repo
    ipr = d.groupby("repo").instance_id.nunique().sort_values(ascending=False)
    out["issues_per_repo"] = {
        "mean": float(ipr.mean()),
        "median": float(ipr.median()),
        "max": int(ipr.max()),
        "repos_ge_5": int((ipr >= 5).sum()),
        "repos_ge_10": int((ipr >= 10).sum()),
        "repos_ge_20": int((ipr >= 20).sum()),
        "share_instances_top10_repos": float(ipr.head(10).sum() / ipr.sum()),
        "top10": {str(k): int(v) for k, v in ipr.head(10).items()},
    }

    # optional columns
    for col in ["exit_status", "gen_tests_correct", "pred_passes_gen_tests"]:
        if col in d.columns:
            if not pd.api.types.is_numeric_dtype(d[col]):
                out[col] = {str(k): int(v) for k, v in Counter(d[col].fillna("<NA>")).most_common(12)}
            else:
                out[col] = {
                    "null_share": float(d[col].isna().mean()),
                    "nonzero_share": float((d[col].fillna(0) > 0).mean()),
                    "top": {str(k): int(v) for k, v in Counter(d[col].fillna(-999)).most_common(8)},
                }
    if "model_patch" in d.columns:
        mp = d.model_patch.fillna("")
        out["model_patch"] = {
            "empty_or_null_share": float((mp.str.len() == 0).mean()),
            "mean_chars": float(mp.str.len().mean()),
            "p90_chars": float(mp.str.len().quantile(0.9)),
        }
    for col in cfg_cols:
        if col in d.columns:
            out[col] = {str(k): int(v) for k, v in Counter(d[col].fillna("<NA>")).most_common(10)}
    return out, per, ipr


def main():
    which, path = sys.argv[1], sys.argv[2]
    df = pd.read_parquet(path)
    df["instance_id"] = df["instance_id"].astype(str)
    results = {}
    if which == "nebius":
        key = df.assign(_cfg="openhands+Qwen3-Coder-480B-A35B(v0.54.0)")
    else:
        split = df.get("hf_dataset_name", pd.Series(["?"] * len(df)))
        key = df.assign(_cfg=split.astype(str))
        if "metadata" in df.columns:
            if "metadata.category" in df.columns:
                key["_category"] = aux_values(df, "metadata.category")
            if "metadata.teacher_model.name" in df.columns:
                key["_teacher"] = aux_values(df, "metadata.teacher_model.name")
            for c in ["metadata.model_patch.num_modified_files", "metadata.model_patch.num_modified_lines",
                      "metadata.reference_patch.num_modified_lines"]:
                if c in df.columns:
                    key[c.replace("metadata.", "")] = aux_values(df, c)
    cfg_cols = [c for c in key.columns if c.startswith("_")] + [c for c in key.columns if c.startswith("model_patch.") or c.startswith("reference_patch.")]
    for cfg, sub in key.groupby("_cfg"):
        sub = sub.drop(columns=["_cfg"])
        out, per, ipr = summarize(sub, f"{which}/{cfg}", cfg_cols=cfg_cols)
        out["hf_dataset_name"] = cfg
        results[cfg] = out
        print(json.dumps(out, indent=2)[:4000])
        print("-" * 60)
        if which == "nvidia":
            print("  sources:", out.get("hf_dataset_name"))
    with open(f"out/recon_{which}.json", "w") as fh:
        json.dump(results, fh, indent=2)
    print(f"wrote out/recon_{which}.json  configs={list(results)}")


if __name__ == "__main__":
    main()
