"""Per-config structural stats for the nvidia corpus (Phase 0, no outcome-vs-signal analysis).

Writes results/nvidia_config_kcover.csv and results/nvidia_crossconfig_overlap.json
"""
import itertools
import json

import numpy as np
import pandas as pd


def struct_field(df, col, field):
    """Extract a leaf from a struct column that pyarrow re-nests as `col`."""
    if col not in df.columns:
        raise KeyError(f"missing column {col}; have {list(df.columns)}")
    s = df[col]
    first = next((v for v in s if isinstance(v, dict)), None)
    if first is None:
        return pd.Series([None] * len(df), index=df.index)
    if field not in first:
        raise KeyError(f"{field} not in struct {sorted(first)}; e.g. {first}")
    return s.map(lambda v: v.get(field) if isinstance(v, dict) else None)


def main():
    nv = pd.read_parquet("out/nvidia_light_cfg.parquet")
    nv["key"] = nv.instance_id.astype(str).str.casefold()
    nv["nfiles"] = struct_field(nv, "metadata", "model_patch").map(
        lambda v: (v or {}).get("num_modified_files"))
    nv["nlines"] = struct_field(nv, "metadata", "model_patch").map(
        lambda v: (v or {}).get("num_modified_lines"))
    nv["category"] = struct_field(nv, "metadata", "category")
    nv["teacher"] = struct_field(nv, "metadata", "teacher_model").map(
        lambda v: (v or {}).get("name"))
    print("patch-availability check: nfiles notna share", float(nv.nfiles.notna().mean()),
          "| zero share", float((nv.nfiles.fillna(0) == 0).mean()),
          "| median lines", float(nv.nlines.median()))
    print("teacher models:", nv.teacher.value_counts().to_dict())
    print("categories:", nv.category.value_counts().head(8).to_dict())
    rows, overlaps = [], {}
    for cfg, g in nv.groupby(["config_version", "agent", "model", "benchmark"]):
        name = "/".join(cfg)
        per = g.groupby("key").size()
        rows.append(dict(
            config=name, rows=len(g), instances=per.size,
            ge2=int((per >= 2).sum()), ge3=int((per >= 3).sum()), ge5=int((per >= 5).sum()),
            ge8=int((per >= 8).sum()), max_traj_per_instance=int(per.max()),
            mean_traj_per_instance=round(float(per.mean()), 3),
            repos=g.repo.str.casefold().nunique(),
            repos_ge5=int((g.groupby(g.repo.str.casefold()).key.nunique() >= 5).sum()),
            minus1_share=round(float((g.resolved == -1).mean()), 4),
            empty_patch_share=round(float((g.nfiles.fillna(0) == 0).mean()), 4),
        ))
        # cross-config overlap within same benchmark (informational)
        overlaps[name] = {"instances": int(per.size),
                          "benchmark": cfg[3], "config_version": cfg[0]}
    kc = pd.DataFrame(rows).sort_values(["ge8", "ge3", "instances"], ascending=False)
    kc.to_csv("results/nvidia_config_kcover.csv", index=False)
    print(kc.to_string(index=False))

    pair = {}
    for (ver, bench), g in nv.groupby(["config_version", "benchmark"]):
        sets = {a: set(s.key) for a, s in g.groupby("agent")}
        if len(sets) < 2:
            continue
        union = set.union(*sets.values())
        inter = set.intersection(*sets.values())
        pair[f"{ver}/{bench}"] = {
            "agents": {a: len(s) for a, s in sets.items()},
            "union": len(union), "intersection": len(inter),
            "repos_union": int(nv[nv.key.isin(union)].repo.str.casefold().nunique()),
            "repos_intersection": int(nv[nv.key.isin(inter)].repo.str.casefold().nunique()),
            "pairwise_jaccard": {
                f"{a}|{b}": round(len(sets[a] & sets[b]) / len(sets[a] | sets[b]), 4)
                for a, b in itertools.combinations(sorted(sets), 2)
            },
        }
    with open("results/nvidia_crossconfig_overlap.json", "w") as fh:
        json.dump(pair, fh, indent=2)
    print("\n", json.dumps(pair, indent=2)[:2500])


if __name__ == "__main__":
    main()
