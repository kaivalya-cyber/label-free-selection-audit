"""B3 — cross-fit difficulty certification (PREREG-2 §5).

Re-executes the kill test's certification machinery with `rate_loo` (the issue's resolve rate
estimated from the other K-1 sampled attempts) and compares the certification counts with the
frozen agreement numbers, under both label conventions.

Usage: .venv/bin/python scripts/b3_crossfit_certification.py
       -> results/b3_crossfit_certification.json
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.configs import ALPHAS, CONFIGS, TAUS_K3, TAUS_K8  # noqa: E402
from src.prereg2 import _frozen_kill_test_module, shared_keys, sign_test, write_json  # noqa: E402
from src.splits import CALIB, EVAL, assert_no_repo_leak, assert_single_side, heldout_repo, \
    random_by_issue, temporal  # noqa: E402

SIGNAL = "rate_loo"
COMPARE = ("tau", "coverage", "risk", "verdict", "n_submitted")


def sides_for(kt, cfg, units, ktag):
    sides = {"random_issue": pd.Series([random_by_issue(ktag, kk) for kk in units.key],
                                       index=units.index),
             "heldout_repo": pd.Series(heldout_repo(ktag, dict(zip(units.key, units.repo))))
             .reindex(units.key)}
    sides["heldout_repo"] = sides["heldout_repo"].set_axis(units.index)
    assert_no_repo_leak(dict(zip(units.key, units.repo)), dict(zip(units.key, sides["heldout_repo"])))
    for s in sides.values():
        assert_single_side(zip(units.key, s))
    cats = kt.attach_created_at(cfg, units)
    if cats.notna().any():
        cats = cats.fillna("9999")
        sides["temporal"] = pd.Series(temporal(dict(zip(units.key, cats)))).reindex(units.key) \
            .set_axis(units.index)
    return sides, cats


def arm(kt, cfg, k, shared, minus1: bool):
    units = kt.build_units(cfg, k, shared, minus1_as_failure=minus1)
    ktag = f"{cfg['tag']}@K{k}"
    sides, cats = sides_for(kt, cfg, units, ktag)
    taus = TAUS_K8 if k == 8 else TAUS_K3
    rec = {"units": int(len(units)), "repos": int(units.repo.nunique()),
           "splits": {}, "temporal_missing_issues": int(cats.isna().sum())}
    for split, side in sides.items():
        rec["splits"][split] = {"n_calib": int((side == CALIB).sum()),
                                "n_eval": int((side == EVAL).sum()), "alpha": {}}
        for alpha in ALPHAS:
            seed_tag = "heldout_repo_baseline" if split == "heldout_repo" else split
            r = kt.evaluate(units, side, SIGNAL, taus, alpha, ktag, seed_tag)
            rec["splits"][split]["alpha"][str(alpha)] = {
                "tau": r["tau"], "certified": r["certified"], "n_submitted": r["n_submitted"],
                "coverage": r["coverage"], "risk": r["risk"], "ci": r["ci"],
                "verdict": r["verdict"]}
    rec["count"] = int(sum(rec["splits"]["heldout_repo"]["alpha"][str(a)]["tau"] is not None
                           for a in ALPHAS))
    return rec


def frozen_counts(block: dict) -> dict:
    out = {}
    for tag, rec in block.items():
        if rec is None:
            continue
        al = rec["splits"]["heldout_repo"]["alpha"]
        out[tag] = {"count": int(sum(al[str(a)]["tau"] is not None for a in ALPHAS)),
                    "by_alpha": {str(a): al[str(a)]["tau"] for a in ALPHAS},
                    "detail": {str(a): {k: al[str(a)][k] for k in
                                        ("tau", "coverage", "risk", "ci", "verdict", "n_submitted")}
                               for a in ALPHAS}}
    return out


def main():
    kt = _frozen_kill_test_module()
    shared = shared_keys()
    frozen = json.loads(Path("results/kill_test.json").read_text())
    out = {"analysis": "B3 cross-fit difficulty certification", "prereg": "PREREG-2 §5",
           "signal": "rate_loo = (sum resolved - resolved_rep)/(K-1)", "alphas": ALPHAS,
           "primary": {}, "alternative": {}, "k8_arm": None, "k8_arm_alternative": None,
           "agreement_frozen": {}, "agreement_frozen_alt": {}, "checks": {}}

    print("B3 primary convention ...", flush=True)
    for cfg in CONFIGS:
        tag = cfg["tag"]
        print(f"  {tag}", flush=True)
        out["primary"][tag] = arm(kt, cfg, 3, shared, False)
    neb = next(c for c in CONFIGS if c["tag"] == "nebius_openhands")
    out["k8_arm"] = arm(kt, neb, 8, shared, False)

    print("B3 alternative convention ...", flush=True)
    for cfg in CONFIGS:
        out["alternative"][cfg["tag"]] = arm(kt, cfg, 3, shared, True)
    out["k8_arm_alternative"] = arm(kt, neb, 8, shared, True)

    out["agreement_frozen"] = frozen_counts(frozen["configs"])
    out["agreement_frozen_alt"] = frozen_counts(frozen["configs_minus1_failure"])
    out["agreement_frozen"]["nebius_openhands@K8"] = frozen_counts(
        {"nebius_openhands@K8": frozen["k8_arm"]})["nebius_openhands@K8"]
    out["agreement_frozen_alt"]["nebius_openhands@K8"] = frozen_counts(
        {"nebius_openhands@K8": frozen["k8_arm_minus1_failure"]})["nebius_openhands@K8"]

    for conv, block, ag, k8block in (
            ("primary", out["primary"], out["agreement_frozen"], out["k8_arm"]),
            ("alternative", out["alternative"], out["agreement_frozen_alt"], out["k8_arm_alternative"])):
        diffs = {}
        for tag, rec in block.items():
            a = ag[tag]["count"]
            rec["agreement_count"] = a
            rec["count_difference"] = rec["count"] - a
            rec["verdict"] = "n/a (count)"
            diffs[tag] = rec["count"] - a
        k8 = k8block
        k8["agreement_count"] = ag["nebius_openhands@K8"]["count"]
        k8["count_difference"] = k8["count"] - k8["agreement_count"]
        dirs = {t: (1 if v > 0 else -1 if v < 0 else 0) for t, v in diffs.items()}
        st = sign_test(dirs)
        st["direction"] = "positive" if st["n_pos"] > st["n_neg"] else (
            "negative" if st["n_neg"] > st["n_pos"] else "tie")
        st["verdict"] = ("SIGNIFICANT+" if st["p_two_sided"] < 0.05 and st["n_pos"] > st["n_neg"]
                         else "SIGNIFICANT-" if st["p_two_sided"] < 0.05 else "NOT SIGNIFICANT")
        out["family_" + conv] = {"sign_test": st, "directions": dirs}
        if conv == "primary":
            out["family"] = out["family_primary"]

    # reproducibility: the re-executed primary cross-fit cells must equal the Part-A baselines
    mism = []
    for tag, rec in out["primary"].items():
        stored = frozen["configs"][tag]["baselines"]["difficulty_cross_fit"]
        for a in ALPHAS:
            got = rec["splits"]["heldout_repo"]["alpha"][str(a)]
            want = stored[str(a)]
            for f in COMPARE:
                if got[f] != want[f]:
                    mism.append({"arm": tag, "alpha": a, "field": f, "got": got[f],
                                 "stored": want[f]})
            if got["ci"] and want["ci"]:
                if abs(got["ci"]["lower"] - want["ci"]["lower"]) > 1e-12 or \
                        abs(got["ci"]["upper"] - want["ci"]["upper"]) > 1e-12:
                    mism.append({"arm": tag, "alpha": a, "field": "ci"})
    k8stored = frozen["k8_arm"]["baselines"]["difficulty_cross_fit"]
    for a in ALPHAS:
        got = out["k8_arm"]["splits"]["heldout_repo"]["alpha"][str(a)]
        want = k8stored[str(a)]
        for f in COMPARE:
            if got[f] != want[f]:
                mism.append({"arm": "nebius_openhands@K8", "alpha": a, "field": f,
                             "got": got[f], "stored": want[f]})
    out["checks"]["reproduced_frozen_crossfit_cells"] = {
        "cells": 12 * len(ALPHAS), "mismatches": mism}
    assert not mism, mism[:3]

    # the canonical split construction must match the frozen run's unit and side counts
    side_mism = []
    for tag, rec in out["primary"].items():
        fz = frozen["configs"][tag]
        for split in ("random_issue", "heldout_repo"):
            for f in ("n_calib", "n_eval"):
                if rec["splits"][split][f] != fz["splits"][split][f]:
                    side_mism.append({"arm": tag, "split": split, "field": f})
    for split in ("random_issue", "heldout_repo"):
        for f in ("n_calib", "n_eval"):
            if out["k8_arm"]["splits"][split][f] != frozen["k8_arm"]["splits"][split][f]:
                side_mism.append({"arm": "nebius_openhands@K8", "split": split, "field": f})
    out["checks"]["split_sizes_match_frozen"] = {"mismatches": side_mism}
    assert not side_mism, side_mism[:3]

    write_json("results/b3_crossfit_certification.json", out)
    print("wrote results/b3_crossfit_certification.json", flush=True)


if __name__ == "__main__":
    main()
