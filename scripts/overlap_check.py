"""Leak checks (Phase 0): duplicate rows, case-folded instance_id overlap across corpora.

Usage: .venv/bin/python scripts/overlap_check.py   # writes results/overlap_check.json + .txt
"""
import json

import pandas as pd


def load(f):
    d = pd.read_parquet(f)
    d["instance_id"] = d.instance_id.astype(str)
    d["key"] = d.instance_id.str.casefold()
    return d


def main():
    out = {}
    neb = load("out/nebius_light.parquet")
    nvi = load("out/nvidia_light.parquet")
    v1 = load("out/swerebench_v1_dates.parquet").drop_duplicates("key")
    v2 = load("out/swerebench_v2_dates.parquet").drop_duplicates("key")

    out["nebius"] = {
        "rows": len(neb),
        "instances_casefold": neb.key.nunique(),
        "repos_casefold": neb.repo.str.casefold().nunique(),
        "dup_instance_trajectoryid": int(neb.duplicated(["key", "trajectory_id"]).sum()),
        "dup_trajectory_id": int(neb.trajectory_id.duplicated().sum()),
    }
    out["nvidia"] = {
        "rows": len(nvi),
        "instances_casefold": nvi.key.nunique(),
        "repos_casefold": nvi.repo.str.casefold().nunique(),
        "dup_instance_trajectoryid": int(nvi.duplicated(["key", "trajectory_id"]).sum()),
        "dup_trajectory_id": int(nvi.trajectory_id.duplicated().sum()),
    }
    out["nvidia_by_source"] = {}
    for src, g in nvi.groupby(nvi.hf_dataset_name.astype(str)):
        out["nvidia_by_source"][str(src)] = {
            "rows": len(g),
            "instances_casefold": g.key.nunique(),
            "repos_casefold": g.repo.str.casefold().nunique(),
            "dup_instance_trajectoryid": int(g.duplicated(["key", "trajectory_id"]).sum()),
        }

    # source corpora overlap
    S1, S2 = set(v1.key), set(v2.key)
    out["swerebench_v1_v2"] = {
        "v1_instances": len(S1), "v2_instances": len(S2),
        "intersection_casefold": len(S1 & S2),
    }

    # cross-corpus overlap between the two trajectory datasets
    A = set(neb.key)
    B_all = set(nvi.key)
    inter = A & B_all
    neb_rows_in_inter = int(neb.key.isin(inter).sum())
    nvi_rows_in_inter = int(nvi.key.isin(inter).sum())
    out["cross_corpus"] = {
        "nebius_instances": len(A),
        "nvidia_instances": len(B_all),
        "intersection": len(inter),
        "share_of_nebius_instances": round(len(inter) / len(A), 4),
        "share_of_nvidia_instances": round(len(inter) / len(B_all), 4),
        "nebius_rows_on_shared_issues": neb_rows_in_inter,
        "nvidia_rows_on_shared_issues": nvi_rows_in_inter,
        "note": "overlap only exists after case-folding instance_id (nvidia lowercases the owner)",
    }
    out["cross_corpus_by_source"] = {}
    for src, g in nvi.groupby(nvi.hf_dataset_name.astype(str)):
        ks = set(g.key)
        out["cross_corpus_by_source"][str(src)] = {
            "nvidia_instances": len(ks),
            "intersection_with_nebius": len(ks & A),
            "nvidia_rows_on_shared": int(g.key.isin(A).sum()),
        }

    # do shared keys agree on repo (case-folded)?
    nb = neb[["key", "repo"]].drop_duplicates("key")
    nv = nvi[["key", "repo"]].drop_duplicates("key")
    sh = nb.merge(nv, on="key", suffixes=("_neb", "_nvi"))
    sh["same_repo"] = sh.repo_neb.str.casefold() == sh.repo_nvi.str.casefold()
    out["shared_key_repo_agreement"] = {
        "shared_keys": len(sh), "same_repo_casefold": int(sh.same_repo.sum()),
        "examples": sh.head(5).to_dict(orient="records"),
    }

    # K-coverage after excluding cross-corpus shared issues
    per = neb.groupby("key").size()
    out["nebius_k_coverage_excl_shared"] = {
        str(k): int(((per >= k) & (~per.index.isin(inter))).sum()) for k in (3, 5, 8)
    }
    out["nebius_k_coverage_all"] = {str(k): int((per >= k).sum()) for k in (3, 5, 8)}
    per_n = nvi.groupby("key").size()
    v2_mask = nvi.groupby("key").hf_dataset_name.first().astype(str).str.contains("V2")
    neu_keys = set(per_n.index[v2_mask]) & A
    out["nvidia_k_coverage"] = {str(k): int((per_n >= k).sum()) for k in (3, 5, 8)}
    out["nvidia_v2_k_coverage"] = {
        str(k): int(((per_n >= k) & per_n.index.isin(set(per_n.index[v2_mask]))).sum()) for k in (3, 5, 8)
    }
    out["nvidia_v2_k_coverage_excl_shared"] = {
        str(k): int(((per_n >= k) & per_n.index.isin(set(per_n.index[v2_mask])) & ~per_n.index.isin(neu_keys)).sum())
        for k in (3, 5, 8)
    }
    out["nvidia_scale_k_coverage"] = {
        str(k): int(((per_n >= k) & per_n.index.isin(set(per_n.index[v2_mask == False]))).sum()) for k in (3, 5, 8)
    }

    with open("results/overlap_check.json", "w") as fh:
        json.dump(out, fh, indent=2, default=str)
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
