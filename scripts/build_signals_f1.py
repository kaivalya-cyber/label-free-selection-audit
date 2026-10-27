"""Build the F1 (new-file-filtered) canonical cache for the sensitivity analysis (DEVIATIONS D4).

Writes out/signals_f1/<tag>.parquet with trajectory_id, key, repo, resolved, f1 (canonical string),
f1_files, f1_lines, steps.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.configs import CONFIGS  # noqa: E402
from src.normalize import files_touched  # noqa: E402
from src.sensitivity import canonical_f1  # noqa: E402


def main():
    out_dir = Path("out/signals_f1")
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {}
    for cfg in CONFIGS:
        tag = cfg["tag"]
        sig = pd.read_parquet(f"out/signals/{tag}.parquet",
                             columns=["trajectory_id", "key", "repo", "resolved", "steps"])
        raw = pd.read_parquet(f"out/patches/{tag}.parquet")[["trajectory_id", "patch"]]
        t0 = time.time()
        d = sig.merge(raw, on="trajectory_id", how="left", validate="1:1")
        assert len(d) == len(sig) and d.patch.notna().all(), tag
        d["f1"] = [canonical_f1(x) for x in d.patch]
        d["f1_files"] = ["\x1f".join(files_touched(x)) for x in d.patch]
        d["f1_lines"] = d.f1.map(lambda s: 0 if s == "<no-change>" else s.count("\n") + 1)
        d[["trajectory_id", "key", "repo", "resolved", "f1", "f1_files", "f1_lines", "steps"]].to_parquet(
            out_dir / f"{tag}.parquet")
        summary[tag] = {"rows": int(len(d)),
                        "no_change_share": round(float((d.f1 == "<no-change>").mean()), 5),
                        "seconds": round(time.time() - t0, 1)}
        print(json.dumps({tag: summary[tag]}), flush=True)
    with open("results/signal_f1_summary.json", "w") as fh:
        json.dump(summary, fh, indent=2)


if __name__ == "__main__":
    main()
