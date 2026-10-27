"""Post-hoc descriptive diagnostics (DEVIATIONS D5). No decision uses these numbers.

1. Error rate by agreement level (1/3, 2/3, 1) per config — monotonicity is an internal-validity
   check on the pipeline (a label/signal mis-join would likely destroy it).
2. Error rate by (agreement level x empirical resolve rate) — the direct test of the research
   hypothesis: does agreement carry information about error *conditional on* the observed success
   count of the same K samples?
3. Error at tau=1 on the calibration vs held-out-repo sides (does the calibrated quantity move under
   repo shift?).

Writes results/posthoc_diagnostics.json + a text table.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.configs import CONFIGS  # noqa: E402
from src.splits import EVAL, CALIB, heldout_repo  # noqa: E402

# import the unit builder from the kill-test script to guarantee identical unit construction
sys.path.insert(0, str(Path(__file__).resolve().parent))
from kill_test import build_units, shared_issue_keys  # noqa: E402


def by_level(df: pd.DataFrame) -> dict:
    out = {}
    for lvl, g in df.groupby("agreement"):
        out[str(round(float(lvl), 3))] = {"n": int(len(g)), "error": round(float((1 - g.label).mean()), 4)}
    return out


def grid(df: pd.DataFrame) -> dict:
    out = {}
    for (a, r), g in df.groupby(["agreement", "rate"]):
        out[f"a={round(float(a), 3)}|rate={round(float(r), 3)}"] = {
            "n": int(len(g)), "error": round(float((1 - g.label).mean()), 4)}
    return out


def main():
    shared = set(shared_issue_keys())
    res = {}
    for cfg in CONFIGS:
        units = build_units(cfg, 3, shared)
        side = pd.Series(heldout_repo(cfg["tag"] + "@K3", dict(zip(units.key, units.repo)))).reindex(
            units.key).set_axis(units.index)
        t1_calib = units[(side == CALIB) & (units.agreement == 1.0)]
        t1_eval = units[(side == EVAL) & (units.agreement == 1.0)]
        rec = {
            "units": int(len(units)),
            "base_error": round(float((1 - units.label).mean()), 4),
            "error_by_agreement": by_level(units),
            "grid": grid(units),
            "tau1_calib": {"n": int(len(t1_calib)),
                           "error": round(float((1 - t1_calib.label).mean()), 4) if len(t1_calib) else None},
            "tau1_heldout_repo": {"n": int(len(t1_eval)),
                                  "error": round(float((1 - t1_eval.label).mean()), 4) if len(t1_eval) else None},
        }
        res[cfg["tag"]] = rec
        print(f"{cfg['tag']:52s} base={rec['base_error']:.3f} " +
              " ".join(f"a={k}:{v['error']:.3f}(n={v['n']})" for k, v in rec["error_by_agreement"].items()) +
              f" | tau1 calib={rec['tau1_calib']['error']} eval={rec['tau1_heldout_repo']['error']}", flush=True)
    with open("results/posthoc_diagnostics.json", "w") as fh:
        json.dump(res, fh, indent=1)

    # compact conditional table: for rate=2/3 (the only non-trivial band), error by agreement
    print("\n== conditional check: rate=2/3 units, error by agreement level ==")
    for tag, r in res.items():
        cells = {k: v for k, v in r["grid"].items() if k.endswith("rate=0.667")}
        txt = " ".join(f"{k.split('|')[0]}: {v['error']:.3f} (n={v['n']})" for k, v in cells.items())
        print(f"{tag:52s} {txt}")


if __name__ == "__main__":
    main()
