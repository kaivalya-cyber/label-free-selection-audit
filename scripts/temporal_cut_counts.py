"""Issue counts on either side of a fixed temporal cut (2023-01-01), per config.

Writes results/temporal_cut_counts.json + prints the table cited in DATA_RECON.md §4.
"""
import json

import pandas as pd

CUT = pd.Timestamp("2023-01-01")


def main():
    out = {}
    nv = pd.read_parquet("out/nvidia_light_cfg.parquet")
    nv["key"] = nv.instance_id.astype(str).str.casefold()
    v2 = pd.read_parquet("out/swerebench_v2_dates.parquet")
    v2["key"] = v2.instance_id.astype(str).str.casefold()
    v2["created_at"] = pd.to_datetime(v2.created_at)
    m = nv.merge(v2[["key", "created_at"]], on="key", how="left")
    for cfg, g in m.groupby(["config_version", "agent", "model", "benchmark"]):
        per = g.groupby("key").agg(n=("resolved", "size"), d=("created_at", "first"))
        k3 = per[per.n >= 3]
        if len(k3) == 0:
            continue
        name = "/".join(cfg)
        if k3.d.isna().all():
            out[name] = {"issues_K3": int(len(k3)), "pre_2023": None, "post_2023": None,
                         "note": "no timestamps (Scale-SWE)"}
            print(f"{name} K3 issues {len(k3)} no timestamps")
            continue
        out[name] = {"issues_K3": int(len(k3)), "pre_2023": int((k3.d < CUT).sum()),
                     "post_2023": int((k3.d >= CUT).sum())}
        print(f"{name} K3 issues {len(k3)} pre-2023 {out[name]['pre_2023']} post-2023 {out[name]['post_2023']}")

    neb = pd.read_parquet("out/nebius_light.parquet")
    neb["key"] = neb.instance_id.astype(str).str.casefold()
    v1 = pd.read_parquet("out/swerebench_v1_dates.parquet")
    v1["key"] = v1.instance_id.astype(str).str.casefold()
    v1["created_at"] = pd.to_datetime(v1.created_at)
    mn = neb.merge(v1[["key", "created_at"]].drop_duplicates("key"), on="key", how="left")
    per = mn.groupby("key").agg(n=("resolved", "size"), d=("created_at", "first"))
    for K in (3, 5, 8):
        kk = per[per.n >= K]
        out[f"nebius_K{K}"] = {"issues": int(len(kk)), "pre_2023": int((kk.d < CUT).sum()),
                               "post_2023": int((kk.d >= CUT).sum())}
        print(f"nebius K>={K} issues {len(kk)} pre-2023 {out[f'nebius_K{K}']['pre_2023']} "
              f"post-2023 {out[f'nebius_K{K}']['post_2023']}")
    with open("results/temporal_cut_counts.json", "w") as fh:
        json.dump(out, fh, indent=2)


if __name__ == "__main__":
    main()
