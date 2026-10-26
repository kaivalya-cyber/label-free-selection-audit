"""Attach (config_version, agent, model, benchmark) parsed from the source path to the
nvidia light cache, verify the join, and emit per-config recon stats.

Usage: .venv/bin/python scripts/build_nvidia_configs.py
"""
import json
import re
from collections import Counter

import pandas as pd

# model -> config version, from the dataset card (data_files configs)
MODEL2CFG = {
    "qwen38_flash_next": "v2.0",
    "qwen38_27b": "v1.2",
    "qwen36_27b": "v1.1",
    "deepseek_v4_flash_0731": "v1.1",
    "minimax_m25": "v1.0",
    "qwen35_122b": "v1.0",
}
PAT = re.compile(r"^data/(?P<agent>[^/]+)/(?P<model>[^/]+)/(?P<benchmark>[^/]+)/")


def parse_path(p):
    m = PAT.match(p)
    if not m:
        raise ValueError(p)
    d = m.groupdict()
    d["config_version"] = MODEL2CFG[d["model"]]
    return d


def main():
    light = pd.read_parquet("out/nvidia_light.parquet")
    paths = pd.read_parquet("out/nvidia_paths.parquet")[["trajectory_id", "_src_path"]]
    print("light rows", len(light), "path rows", len(paths))
    print("trajectory_id unique in light:", light.trajectory_id.nunique() == len(light))
    print("trajectory_id unique in paths:", paths.trajectory_id.nunique() == len(paths))
    meta = pd.DataFrame([parse_path(p) for p in paths._src_path.unique()])
    meta["_src_path"] = paths._src_path.unique()
    paths = paths.merge(meta, on="_src_path", how="left")
    assert paths.config_version.notna().all()
    merged = light.merge(paths.drop(columns=["_src_path"]), on="trajectory_id", how="left", validate="1:1")
    assert len(merged) == len(light), (len(merged), len(light))
    assert merged.agent.notna().all()
    # cross-check: hf_dataset_name consistency with benchmark folder
    ct = pd.crosstab(merged.benchmark, merged.hf_dataset_name.astype(str))
    print(ct)
    merged.to_parquet("out/nvidia_light_cfg.parquet")
    cfg = merged.groupby(["config_version", "agent", "model", "benchmark"]).agg(
        rows=("trajectory_id", "size"),
        instances=("instance_id", "nunique"),
        repos=("repo", "nunique"),
        share_minus1=("resolved", lambda s: float((s == -1).mean())),
        share_resolved1=("resolved", lambda s: float((s == 1).mean())),
    ).reset_index()
    cfg.to_csv("results/nvidia_configs.csv", index=False)
    print(cfg.to_string())


if __name__ == "__main__":
    main()
