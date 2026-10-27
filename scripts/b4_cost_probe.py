"""Pre-registration probe for PREREG-2 (Part B). Label-blind or availability-only.

Two facts are needed **before** PREREG-2 is frozen, and neither involves any signal-vs-outcome
association:

1. B4 adaptive stopping — the attempt cost of "stop as soon as the first two drawn patches are
   identical". Computed from canonical patch forms only (`out/signals/*.parquet`); no label column
   is read. Two readings of the rule are measured, because the wording is ambiguous:
     seq_first2 : stop at 2 iff draws 1 and 2 are identical, else continue to K_max;
     seq_any1st : stop at the first repeat of any two drawn patches, else continue to K_max.
   Draw order = seeded permutation of the issue's attempts (`seeded_rng("seq", ktag, key)`).
2. B2 eligibility — how many within-issue mixed-label pairs exist in the nebius K=8 frame for which
   both attempts carry a non-null `pred_passes_gen_tests` value. Counts only; no association, no
   effect size. (Mixed-label membership needs the labels; it is used to count pairs, nothing else.)

Usage: .venv/bin/python scripts/b4_cost_probe.py   -> results/b4_cost_probe.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.configs import CONFIGS  # noqa: E402
from src.risk import seeded_rng  # noqa: E402

SIG = Path("out/signals")
SHARED = pd.read_csv("results/excluded_shared_issues.csv").key.astype(str).tolist()


def arm_frame(cfg, k):
    df = pd.read_parquet(SIG / f"{cfg['tag']}.parquet")
    df = df[~df.key.isin(SHARED)]
    # B4 draws from the attempts the frozen arm would have available: label-blind = every attempt.
    n = df.groupby("key").size()
    keep = set(n[n >= k].index)
    return df[df.key.isin(keep)]


def costs(df, k):
    n2 = n_any = 0
    tot2 = tot_any = 0.0
    for key, g in df.groupby("key", sort=True):
        can = g.canonical.astype(str).tolist()
        if len(can) < k:
            continue
        order = seeded_rng("seq", key).permutation(len(can))
        seq = [can[i] for i in order[:k]]
        c_first2 = 2 if seq[0] == seq[1] else k
        seen, c_any = set(), None
        for j, c in enumerate(seq):
            if c in seen:
                c_any = j + 1
                break
            seen.add(c)
        if c_any is None:
            c_any = k
        n2 += 1
        tot2 += c_first2
        n_any += 1
        tot_any += c_any
    return {"issues": n2, "mean_cost_seq_first2": tot2 / max(n2, 1),
            "mean_cost_seq_any1st": tot_any / max(n_any, 1)}


def b2_availability(cfg, k, light_cols):
    df = pd.read_parquet(SIG / f"{cfg['tag']}.parquet")[["key", "trajectory_id", "resolved"]]
    df = df[~df.key.isin(SHARED)]
    n = df.groupby("key").size()
    df = df[df.key.isin(set(n[n >= k].index))]
    light = pd.read_parquet("out/nebius_light.parquet", columns=light_cols)
    m = df.merge(light, on="trajectory_id", how="left", validate="1:1")
    mixed = m.groupby("key").resolved.agg(["min", "max"])
    mixed_keys = set(mixed[(mixed["min"] == 0) & (mixed["max"] == 1)].index)
    sub = m[m.key.isin(mixed_keys)]
    col = light_cols[-1]
    pairs = 0
    issues_with_pair = set()
    for key, g in sub.groupby("key"):
        a = g[g[col].notna()]
        pos = a[a.resolved == 1][col].to_numpy()
        neg = a[a.resolved == 0][col].to_numpy()
        if len(pos) and len(neg):
            pairs += len(pos) * len(neg)
            issues_with_pair.add(key)
    return {"issues_with_geK": int(m.key.nunique()), "mixed_label_issues": len(mixed_keys),
            "mixed_issues_with_an_eligible_pair": len(issues_with_pair),
            "eligible_pairs": pairs,
            "attempts": int(len(m)), "attempts_with_nonnull_signal": int(m[col].notna().sum())}


def main():
    out = {"costs": {}, "b2_availability": {}, "note": __doc__.strip().splitlines()[0]}
    for cfg in CONFIGS:
        rec = costs(arm_frame(cfg, 3), 3)
        out["costs"][f"{cfg['tag']}@K3"] = rec
        print(f"{cfg['tag']}@K3 issues={rec['issues']} mean_cost first2={rec['mean_cost_seq_first2']:.3f} "
              f"any1st={rec['mean_cost_seq_any1st']:.3f}", flush=True)
    neb = next(c for c in CONFIGS if c["tag"] == "nebius_openhands")
    rec = costs(arm_frame(neb, 8), 8)
    out["costs"]["nebius_openhands@K8"] = rec
    print(f"nebius@K8 issues={rec['issues']} mean_cost first2={rec['mean_cost_seq_first2']:.3f} "
          f"any1st={rec['mean_cost_seq_any1st']:.3f}", flush=True)
    out["b2_availability"]["nebius_openhands@K8"] = b2_availability(
        neb, 8, ["trajectory_id", "pred_passes_gen_tests", "gen_tests_correct"])
    print(json.dumps(out["b2_availability"], indent=1), flush=True)
    Path("results/b4_cost_probe.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
