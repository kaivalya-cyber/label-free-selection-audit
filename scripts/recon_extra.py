"""Extra Phase 0 recon: step counts from role arrays, case-insensitive instance keys,
temporal coverage from source datasets. Writes results/recon_extra.json.

Usage: .venv/bin/python scripts/recon_extra.py
"""
import json

import numpy as np
import pandas as pd


def step_counts(df, rolecol):
    """Count assistant messages per trajectory row."""
    out = np.empty(len(df), dtype=np.int64)
    for i, msgs in enumerate(df[rolecol]):
        c = 0
        if isinstance(msgs, (list, np.ndarray)):
            for m in msgs:
                if isinstance(m, dict) and m.get("role") == "assistant":
                    c += 1
        out[i] = c
    return out


def inst_summary(df, col="instance_id"):
    key = df[col].astype(str)
    cf = key.str.casefold()
    coll = key[cf.duplicated(keep=False)].groupby(cf[cf.duplicated(keep=False)]).nunique()
    return {
        "rows": int(len(df)),
        "instances_exact": int(key.nunique()),
        "instances_casefold": int(cf.nunique()),
        "case_collisions": int((coll > 1).sum()),
    }


def main():
    res = {}
    neb = pd.read_parquet("out/nebius_light.parquet")
    neb["instance_id"] = neb.instance_id.astype(str)
    nvi = pd.read_parquet("out/nvidia_light.parquet")
    nvi["instance_id"] = nvi.instance_id.astype(str)

    s = step_counts(neb, "trajectory")
    res["nebius_steps_assistant"] = {
        "mean": float(s.mean()), "median": float(np.median(s)),
        "p90": float(np.percentile(s, 90)), "max": int(s.max()), "zero_share": float((s == 0).mean()),
    }
    s2 = step_counts(nvi, "messages")
    res["nvidia_steps_assistant"] = {
        "mean": float(s2.mean()), "median": float(np.median(s2)),
        "p90": float(np.percentile(s2, 90)), "max": int(s2.max()), "zero_share": float((s2 == 0).mean()),
    }

    res["nebius_keys"] = inst_summary(neb)
    res["nvidia_keys_all"] = inst_summary(nvi)
    res["nvidia_keys_by_source"] = {
        str(src): inst_summary(g) for src, g in nvi.groupby(nvi["hf_dataset_name"].astype(str))
    }

    v1 = pd.read_parquet("out/swerebench_v1_dates.parquet")
    v2 = pd.read_parquet("out/swerebench_v2_dates.parquet")
    for d in (v1, v2):
        d["key"] = d.instance_id.astype(str).str.casefold()
        d["created_at"] = pd.to_datetime(d.created_at)
    v1u = v1.drop_duplicates("key")
    v2u = v2.drop_duplicates("key")

    neb_key = neb.instance_id.str.casefold()
    key_multi = neb.assign(key=neb_key).groupby("key").size()
    res["nebius_temporal"] = {}
    for name, src in [("SWE-rebench-V1", v1u), ("SWE-rebench-V2", v2u)]:
        n_all = neb_key.isin(set(src.key)).sum()
        dated = neb.assign(key=neb_key).merge(src[["key", "created_at"]], on="key", how="inner")
        k8_insts = set(key_multi[key_multi >= 8].index)
        dated_k8 = dated[dated.key.isin(k8_insts)]
        q = dated_k8.assign(q=dated_k8.created_at.dt.to_period("Q").astype(str)).groupby("q").size()
        res["nebius_temporal"][name] = {
            "trajectory_rows_matched": int(n_all),
            "share_rows_matched": round(n_all / len(neb), 4),
            "instances_matched": int(dated.key.nunique()),
            "instances_matched_with_ge8_samples": int(dated_k8.key.nunique()),
            "date_min": str(dated.created_at.min()) if len(dated) else None,
            "date_max": str(dated.created_at.max()) if len(dated) else None,
            "quarters_ge8": {k: int(v) for k, v in q.sort_index().items()},
        }

    # nvidia temporal + cross-dataset overlap (case-insensitive)
    nvi_key = nvi.instance_id.str.casefold()
    res["nvidia_temporal"] = {}
    nvi_k = nvi.assign(key=nvi_key)
    for src_name, src in [("SWE-rebench-V2", v2u), ("SWE-rebench-V1", v1u)]:
        m = nvi_k.merge(src[["key", "created_at"]], on="key", how="inner")
        res["nvidia_temporal"][src_name] = {
            "rows_matched": int(len(m)),
            "instances_matched": int(m.key.nunique()),
            "share_of_all_nvidia_rows": round(len(m) / len(nvi), 4),
            "date_min": str(m.created_at.min()) if len(m) else None,
            "date_max": str(m.created_at.max()) if len(m) else None,
        }
    nvi_k["source"] = nvi_k["hf_dataset_name"].astype(str)
    for src, g in nvi_k.groupby("source"):
        src_ds = v2u if "V2" in src else None
        if src_ds is None:
            continue
        m = g.merge(src_ds[["key", "created_at"]], on="key", how="inner")
        res["nvidia_temporal"][src + " (own source)"] = {
            "rows_matched": int(len(m)),
            "rows_in_source": int(len(g)),
            "share_of_source_rows": round(len(m) / len(g), 4),
            "instances_matched": int(m.key.nunique()),
            "instances_in_source": int(g.key.nunique()),
            "date_min": str(m.created_at.min()) if len(m) else None,
            "date_max": str(m.created_at.max()) if len(m) else None,
        }
    neb_keys = set(neb_key)
    res["cross_dataset_overlap_casefold"] = {
        "nebius_instances": len(neb_keys),
        "nvidia_instances": int(nvi_key.nunique()),
        "intersection": int(len(neb_keys & set(nvi_key))),
        "share_of_nebius": round(len(neb_keys & set(nvi_key)) / len(neb_keys), 4),
    }
    # per-source intersection
    res["cross_dataset_overlap_casefold_by_source"] = {}
    for src, g in nvi.groupby(nvi["hf_dataset_name"].astype(str)):
        ks = set(g.instance_id.astype(str).str.casefold())
        res["cross_dataset_overlap_casefold_by_source"][str(src)] = {
            "nvidia_instances": len(ks),
            "intersection_with_nebius_traj_instances": len(ks & neb_keys),
        }

    # repos shared across the two benchmark corpora (case-insensitive)
    res["repo_overlap"] = {
        "nebius_repos": int(neb.repo.str.casefold().nunique()),
        "v1_repos": int(v1u.repo.str.casefold().nunique()),
        "v2_repos": int(v2u.repo.str.casefold().nunique()),
        "v1_v2_shared_repos": int(len(set(v1u.repo.str.casefold()) & set(v2u.repo.str.casefold()))),
    }
    with open("results/recon_extra.json", "w") as fh:
        json.dump(res, fh, indent=2)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
