"""Canonicalize patches and cache per-trajectory signals for the 11 frozen configs.

Writes out/signals/<tag>.parquet with
  trajectory_id, key (casefolded instance), repo, resolved, canonical, files, changed_lines, steps

No outcome-vs-signal statistic is computed here (PREREG §7 gate).
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.configs import CONFIGS  # noqa: E402
from src.normalize import canonical, canonical_sections, files_touched  # noqa: E402


def steps_from_roles(series) -> np.ndarray:
    out = np.empty(len(series), dtype=np.int32)
    for i, msgs in enumerate(series):
        c = 0
        if isinstance(msgs, (list, np.ndarray)):
            for m in msgs:
                if isinstance(m, dict) and m.get("role") == "assistant":
                    c += 1
        out[i] = c
    return out


def light_for(cfg) -> pd.DataFrame:
    if cfg["dataset"] == "nebius":
        d = pd.read_parquet("out/nebius_light.parquet")
        d["steps"] = steps_from_roles(d["trajectory"])
        return d[["trajectory_id", "instance_id", "repo", "resolved", "steps"]]
    d = pd.read_parquet("out/nvidia_light_cfg.parquet")
    sel = d[(d.config_version == cfg["version"]) & (d.agent == cfg["agent"])
            & (d.model == cfg["model"]) & (d.benchmark == cfg["benchmark"])].copy()
    assert len(sel) > 0, cfg["tag"]
    sel["steps"] = steps_from_roles(sel["messages"])
    return sel[["trajectory_id", "instance_id", "repo", "resolved", "steps"]]


def main():
    only = sys.argv[1:] or None
    summary = {}
    for cfg in CONFIGS:
        tag = cfg["tag"]
        if only and tag not in only:
            continue
        t0 = time.time()
        pat = Path(f"out/patches/{tag}.parquet")
        if not pat.exists():
            print(f"MISSING {pat}", flush=True)
            continue
        p = pd.read_parquet(pat)
        lab = light_for(cfg)
        df = lab.merge(p[["trajectory_id", "patch"]], on="trajectory_id", how="inner", validate="1:1")
        assert len(df) == len(p) == len(lab), (tag, len(df), len(p), len(lab))
        df["key"] = df.instance_id.astype(str).str.casefold()
        df["repo"] = df.repo.astype(str)
        df["canonical"] = [canonical(x) for x in df.patch]
        df["files"] = ["\x1f".join(files_touched(x)) for x in df.patch]
        df["changed_lines"] = [sum(len(lines) for _, lines in canonical_sections(x)) for x in df.patch]
        out = df[["trajectory_id", "key", "repo", "resolved", "canonical", "files",
                  "changed_lines", "steps"]]
        Path("out/signals").mkdir(parents=True, exist_ok=True)
        out.to_parquet(f"out/signals/{tag}.parquet")
        summary[tag] = {
            "rows": int(len(out)),
            "instances": int(out.key.nunique()),
            "repos": int(out.repo.nunique()),
            "no_change_share": round(float((out.canonical == "<no-change>").mean()), 5),
            "empty_files_share": round(float((out.files == "").mean()), 5),
            "median_changed_lines": float(out.changed_lines.median()),
            "median_steps": float(out.steps.median()),
            "minus1_rows": int((out.resolved == -1).sum()),
            "seconds": round(time.time() - t0, 1),
        }
        print(json.dumps(summary[tag]), flush=True)
    with open("results/signal_cache_summary.json", "w") as fh:
        json.dump(summary, fh, indent=2)


if __name__ == "__main__":
    main()
