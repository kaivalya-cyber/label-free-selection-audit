"""Signal-only distribution of the secondary signal (files-touched agreement) at K=3.

No labels are read. Uses PREREG §1 sampling: rng.choice(sorted(trajectory_ids), K, replace=False).
Writes results/files_agreement_probe.txt + .json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.configs import CONFIGS  # noqa: E402
from src.normalize import largest_cluster_share  # noqa: E402
from src.risk import seeded_rng  # noqa: E402


def main():
    shared = set(pd.read_csv("results/excluded_shared_issues.csv").key)
    out = {}
    for cfg in CONFIGS:
        tag = cfg["tag"]
        d = pd.read_parquet(f"out/signals/{tag}.parquet")
        d = d[~d.key.isin(shared)]
        d = d[d.resolved.isin([0, 1])]
        vals = []
        for key, g in d.groupby("key", sort=True):
            ids = np.array(sorted(g.trajectory_id.astype(str).tolist()))
            if len(ids) < 3:
                continue
            rng = seeded_rng(tag, key)
            picked = rng.choice(ids, size=3, replace=False)
            vals.append(largest_cluster_share(g.set_index("trajectory_id").loc[picked].files.tolist()))
        v = np.array(vals)
        out[tag] = {"units": int(len(v)),
                    "files_unanimous": round(float((v == 1).mean()), 4),
                    "files_any_pair": round(float((v >= 2 / 3).mean()), 4),
                    "files_all_distinct": round(float((v <= 1 / 3).mean()), 4),
                    "mean": round(float(v.mean()), 4)}
        print(tag, json.dumps(out[tag]), flush=True)
    with open("results/files_agreement_probe.json", "w") as fh:
        json.dump(out, fh, indent=2)


if __name__ == "__main__":
    main()
