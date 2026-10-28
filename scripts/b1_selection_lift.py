"""B1 — selection lift (PREREG-2 §3, DEVIATIONS D8).

Usage: .venv/bin/python scripts/b1_selection_lift.py
Writes results/b1_selection_lift.json.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.configs import CONFIGS  # noqa: E402
from src.prereg2 import (bootstrap_mean, check_against_kill_test, frames_for_all, holm,  # noqa: E402
                         issue_lift, load_attempts, shared_keys, sign_test, write_json)


def arm_numbers(frame: pd.DataFrame, ktag: str, k: int, e3: bool = False) -> dict:
    rows = []
    for key, g in frame.groupby("key", sort=True):
        canon = dict(zip(g.trajectory_id, g.canonical))
        labels = dict(zip(g.trajectory_id, g.resolved.astype(int)))
        rows.append({"key": key, "repo": g.repo.iloc[0], **issue_lift(canon, labels, ktag, key)})
    d = pd.DataFrame(rows)
    boot = bootstrap_mean(d.lift, d.repo, (ktag, "lift"))
    mixed = d[d.mixed]
    rec = {
        "n_issues": int(len(d)), "n_repos": int(d.repo.nunique()),
        "selected_rate": float(d.selected.mean()), "random_rate": float(d.random_k.mean()),
        "oracle_rate": float(d.oracle_k.mean()),
        "mean_lift": boot["estimate"], "ci": [boot["lower"], boot["upper"]],
        "p": boot["p"], "n_clusters": boot["n_clusters"],
        "mixed": {"n_issues": int(len(mixed)),
                  "mean_lift": float(mixed.lift.mean()) if len(mixed) else None},
        "non_mixed_mean_lift": float(d[~d.mixed].lift.mean()) if (~d.mixed).any() else None,
        "share_mixed": float(d.mixed.mean()),
        "mean_top_size": float(d.top_size.mean()),
        "share_unique_selection": float(d.unique.mean()),
    }
    rec["lift_identity"] = abs(rec["mean_lift"] - rec["share_mixed"] * (rec["mixed"]["mean_lift"] or 0))
    assert rec["lift_identity"] < 1e-12, rec["lift_identity"]
    if e3:
        e3rows = []
        for key, g in frame.groupby("key", sort=True):
            canon = dict(zip(g.trajectory_id, g.canonical))
            labels = dict(zip(g.trajectory_id, g.resolved.astype(int)))
            e3rows.append({"key": key, "repo": g.repo.iloc[0],
                           **issue_lift(canon, labels, ktag, key, mode="random")})
        e3d = pd.DataFrame(e3rows)
        e3boot = bootstrap_mean(e3d.lift, e3d.repo, (ktag, "lift", "e3"))
        rec["e3_random_representative"] = {
            "mean_lift": e3boot["estimate"], "ci": [e3boot["lower"], e3boot["upper"]],
            "p": e3boot["p"], "label": "EXPLORATORY",
        }
    return rec


def family(primary: dict[str, dict]) -> dict:
    pvals = {t: r["p"] for t, r in primary.items()}
    h = holm(pvals)
    for tag, rec in primary.items():
        adj = h["adjusted"][tag]
        if adj < 0.05 and rec["mean_lift"] > 0:
            verdict = "SIGNIFICANT+"
        elif adj < 0.05 and rec["mean_lift"] < 0:
            verdict = "SIGNIFICANT-"
        else:
            verdict = "NOT SIGNIFICANT"
        rec["holm_p"] = adj
        rec["verdict"] = verdict
    dirs = {t: (1 if r["mean_lift"] > 0 else -1 if r["mean_lift"] < 0 else 0)
            for t, r in primary.items()}
    return {"holm": h, "sign_test": sign_test(dirs), "directions": dirs}


def main():
    out = {"analysis": "B1 selection lift", "prereg": "PREREG-2 §3", "deviation": "D8",
           "k": 3, "B": 2000, "primary": {}, "alternative": {}, "k8_arm": None,
           "k8_arm_alternative": None, "family": {}, "family_alternative": {}, "checks": {}}

    frames = frames_for_all(3, minus1_as_failure=False)
    alt = frames_for_all(3, minus1_as_failure=True)
    for cfg in CONFIGS:
        tag = cfg["tag"]
        ktag = f"{tag}@K3"
        print(f"B1 {tag} ...", flush=True)
        out["primary"][tag] = arm_numbers(frames[tag], ktag, 3, e3=True)
        out["alternative"][tag] = arm_numbers(alt[tag], ktag + "-minus1fail", 3)
    for name, block in (("primary", out["primary"]), ("alternative", out["alternative"])):
        for tag, rec in block.items():
            rec["label"] = "PRIMARY" if name == "primary" else "SENSITIVITY (-1 as failure)"
    out["family"] = family(out["primary"])
    out["family_alternative"] = family(out["alternative"])

    neb = next(c for c in CONFIGS if c["tag"] == "nebius_openhands")
    sh = shared_keys()
    f8 = load_attempts(neb, 8, minus1_as_failure=False, shared=sh)
    a8 = load_attempts(neb, 8, minus1_as_failure=True, shared=sh)
    out["k8_arm"] = arm_numbers(f8, "nebius_openhands@K8", 8, e3=True)
    out["k8_arm"]["label"] = "SEPARATE ARM (not in any Holm family)"
    out["k8_arm_alternative"] = arm_numbers(a8, "nebius_openhands@K8-minus1fail", 8)
    out["k8_arm_alternative"]["label"] = "SEPARATE ARM, SENSITIVITY"

    print("B1 frame check ...", flush=True)
    chk = check_against_kill_test(frames, {t: 3 for t in frames}, alt_frames=alt)
    chk8 = check_against_kill_test({"nebius_openhands": f8}, {"nebius_openhands": 8},
                                   alt_frames={"nebius_openhands": a8})
    for k in ("checked_arms", "checked_issues", "mismatched_issues", "unit_count_mismatches",
              "alt_unit_count_mismatches"):
        chk[k] += chk8[k]
    chk["details"] += chk8["details"]
    assert chk["mismatched_issues"] == 0 and chk["unit_count_mismatches"] == 0
    assert chk["alt_unit_count_mismatches"] == 0
    out["checks"]["sampled_attempts_match_kill_test"] = chk
    out["checks"]["non_mixed_lift_zero"] = all(
        rec["non_mixed_mean_lift"] in (0.0, None) for rec in out["primary"].values())
    write_json("results/b1_selection_lift.json", out)
    print("wrote results/b1_selection_lift.json", flush=True)


if __name__ == "__main__":
    main()
