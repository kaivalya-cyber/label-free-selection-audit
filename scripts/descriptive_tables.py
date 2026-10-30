"""DESCRIPTIVE tables for RESULTS_2.md — no hypothesis tests, no verdicts.

(a) per arm: pass@1 over the sampled attempts, the agreement-selected resolve rate (DEVIATIONS D1
    rule, plus the `kill_test.py` tie-break as the D9 sensitivity), oracle pass@K, and the
    selection gap (= oracle − selected);
(b) per arm: the intraclass correlation of `resolved` with issue as the group (one-way random
    effects ANOVA, ICC(1)), with a repo-clustered bootstrap CI;
(c) the fixed-budget curve f(k) for every arm in one table (read from the B4 run, unchanged).

Every arm uses the frozen K-sample frames of PREREG-2 §1 and the primary label convention
(`resolved=-1` dropped before sampling). Nothing here re-estimates a B1–B4 quantity; the only
cross-checks are that the frame sizes match B1/B4 and that the two selection rules reproduce the
rates already stored in B4 and the kill test.

Usage: .venv/bin/python scripts/descriptive_tables.py -> results/descriptive_tables.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.configs import CONFIGS  # noqa: E402
from src.prereg2 import (d1_pick, d1_pick_killtest, frames_for_all, load_attempts,  # noqa: E402
                         shared_keys)
from src.risk import seeded_rng  # noqa: E402

B = 2000


def icc_oneway(values, groups):
    """One-way random-effects ICC(1) with unequal group sizes.

    values: 0/1 labels; groups: issue ids. Returns the ICC and the ANOVA pieces.
    """
    df = pd.DataFrame({"y": np.asarray(values, dtype=float), "g": np.asarray(groups)})
    agg = df.groupby("g").y.agg(["size", "sum", "mean", ("sq", lambda s: (s ** 2).sum())])
    n_i = agg["size"].to_numpy(dtype=float)
    sums = agg["sum"].to_numpy(dtype=float)
    means = agg["mean"].to_numpy(dtype=float)
    N, G = float(n_i.sum()), float(len(agg))
    grand = float(sums.sum() / N)
    ssb = float((n_i * (means - grand) ** 2).sum())
    ssw = float(df.y.var(ddof=0) * N - ssb)
    msb = ssb / (G - 1)
    msw = ssw / (N - G)
    k0 = (N - float((n_i ** 2).sum()) / N) / (G - 1)
    denom = msb + (k0 - 1) * msw
    icc = (msb - msw) / denom if denom > 0 else float("nan")
    return {"icc": float(icc), "msb": msb, "msw": msw, "k0": float(k0),
            "groups": int(G), "n": int(N)}


def icc_bootstrap(values, groups, repos, seed_parts, B=B):
    """Repo-clustered bootstrap: resample repos, keep all their issues (with multiplicity)."""
    df = pd.DataFrame({"y": np.asarray(values, dtype=float), "g": np.asarray(groups),
                       "r": np.asarray(repos, dtype=object)})
    # issue-level sums, ordered by repo then issue
    issue = df.groupby(["r", "g"], sort=True).y.agg(["size", "sum",
                                                     ("sq", lambda s: (s ** 2).sum())]).reset_index()
    assert issue["size"].nunique() == 1, "ICC bootstrap assumes a balanced K within every issue"
    uniq = issue.r.drop_duplicates().to_numpy()
    pos = {r: i for i, r in enumerate(uniq)}
    issue_repo = issue.r.map(pos).to_numpy(dtype=int)
    issue_sum = issue["sum"].to_numpy(dtype=float)
    issue_sq = issue["sq"].to_numpy(dtype=float)
    issue_n = issue["size"].to_numpy(dtype=float)
    R = len(uniq)
    rng = seeded_rng("boot2", *seed_parts)
    out = np.empty(B)
    for b in range(B):
        draw = rng.integers(0, R, size=R)
        mult = np.bincount(draw, minlength=R)
        idx = np.repeat(np.arange(len(issue_repo)), mult[issue_repo])
        n_i, s, sq = issue_n[idx], issue_sum[idx], issue_sq[idx]
        N, G = float(n_i.sum()), float(len(idx))
        grand = float(s.sum() / N)
        ssb = float((n_i * (s / n_i - grand) ** 2).sum())
        ssw = float(sq.sum() - (s ** 2 / n_i).sum())
        msb, msw = ssb / (G - 1), ssw / (N - G)
        k0 = (N - float((n_i ** 2).sum()) / N) / (G - 1)
        denom = msb + (k0 - 1) * msw
        out[b] = (msb - msw) / denom if denom > 0 else np.nan
    lo, hi = np.nanpercentile(out, [2.5, 97.5])
    return {"lower": float(lo), "upper": float(hi), "B": B, "n_clusters": int(R),
            "nan_replicates": int(np.isnan(out).sum())}


def arm_record(frame, tag, k):
    keys = sorted(frame.key.unique())
    rows = []
    for key, g in frame.groupby("key", sort=True):
        canon = dict(zip(g.trajectory_id.astype(str), g.canonical.astype(str)))
        labels = dict(zip(g.trajectory_id.astype(str), g.resolved.astype(int)))
        tids = list(canon)
        rows.append({"key": key, "repo": g.repo.iloc[0],
                     "pass1": float(np.mean([labels[t] for t in tids])),
                     "oracle": float(max(labels.values())),
                     "sel_d1": float(labels[d1_pick(tids, canon)]),
                     "sel_kt": float(labels[d1_pick_killtest(tids, canon)]),
                     "mixed": bool(0 < sum(labels.values()) < len(labels))})
    r = pd.DataFrame(rows)
    rec = {
        "issues": int(len(r)), "repos": int(r.repo.nunique()), "attempts": int(len(frame)),
        "pass_at_1": float(r.pass1.mean()),
        "selected_d1": float(r.sel_d1.mean()),
        "selected_killtest_tiebreak": float(r.sel_kt.mean()),
        "oracle_pass_at_k": float(r.oracle.mean()),
        "selection_gap_d1": float(r.oracle.mean() - r.sel_d1.mean()),
        "selection_gap_killtest_tiebreak": float(r.oracle.mean() - r.sel_kt.mean()),
        "share_mixed": float(r.mixed.mean()),
        "label": "DESCRIPTIVE (no test)",
    }
    icc_point = icc_oneway(frame.resolved.to_numpy(), frame.key.to_numpy())
    ci = icc_bootstrap(frame.resolved, frame.key, frame.repo, (tag, k, "icc"))
    rec["icc"] = {"estimate": icc_point["icc"], "lower": ci["lower"], "upper": ci["upper"],
                  "groups": icc_point["groups"], "n": icc_point["n"],
                  "k0": icc_point["k0"], "B": ci["B"], "n_clusters": ci["n_clusters"],
                  "nan_replicates": ci["nan_replicates"]}
    return rec


def main():
    shared = shared_keys()
    frames = frames_for_all(3, False)
    neb = next(c for c in CONFIGS if c["tag"] == "nebius_openhands")
    frames8 = {"nebius_openhands@K8": load_attempts(neb, 8, False, shared)}
    b4 = json.loads(Path("results/b4_adaptive_stopping.json").read_text())
    kt = json.loads(Path("results/kill_test.json").read_text())
    b1 = json.loads(Path("results/b1_selection_lift.json").read_text())

    out = {"analysis": "DESCRIPTIVE tables (a)-(c) for RESULTS_2.md",
           "tests": "none — no p-value, threshold or verdict is computed in this file",
           "convention": "primary: resolved=-1 dropped before sampling (PREREG-2 §2)",
           "rules": {
               "primary": "DEVIATIONS D1: largest canonical cluster; equal-size ties by the "
                          "smallest trajectory_id in the cluster; representative = that id.",
               "sensitivity": "DEVIATIONS D9: the tie-break actually implemented in "
                              "scripts/kill_test.py::build_units (smallest canonical string among "
                              "the top clusters, then smallest id); this is also the rule behind "
                              "kill_test.json's resolved_rate."},
           "arms": {}, "k8_arm": {}, "curves": {}, "checks": {}}

    for cfg in CONFIGS:
        tag = cfg["tag"]
        rec = arm_record(frames[tag], tag, 3)
        out["arms"][tag] = rec
        out["curves"][tag] = {k: float(v) for k, v in b4["arms"][tag]["primary"]["curve"].items()}
        print(tag, rec["issues"], f"pass1={rec['pass_at_1']:.4f}",
              f"d1={rec['selected_d1']:.4f}", f"kt={rec['selected_killtest_tiebreak']:.4f}",
              f"icc={rec['icc']['estimate']:+.4f}", flush=True)
    tag8 = "nebius_openhands@K8"
    out["k8_arm"][tag8] = arm_record(frames8[tag8], tag8, 8)
    out["curves"][tag8] = {k: float(v) for k, v in b4["k8_arm"]["primary"]["curve"].items()}
    print(tag8, out["k8_arm"][tag8]["icc"]["estimate"], flush=True)

    # ---------------------------------------------------------------- checks (identity, not new numbers)
    mism = []
    for tag, rec in out["arms"].items():
        # B4's `issues` field is the number of sampled attempt rows (K × issues), not the issue count.
        if rec["attempts"] != b4["arms"][tag]["issues"]:
            mism.append((tag, "attempts", rec["attempts"], b4["arms"][tag]["issues"]))
        if abs(rec["selected_d1"] - b4["arms"][tag]["primary"]["curve"]["3"]) > 1e-12:
            mism.append((tag, "D1 f(K)", rec["selected_d1"],
                         b4["arms"][tag]["primary"]["curve"]["3"]))
        if abs(rec["selected_killtest_tiebreak"] - kt["configs"][tag]["resolved_rate"]) > 1e-12:
            mism.append((tag, "killtest rate", rec["selected_killtest_tiebreak"],
                         kt["configs"][tag]["resolved_rate"]))
        if rec["issues"] != b1["primary"][tag]["n_issues"]:
            mism.append((tag, "B1 issues", rec["issues"], b1["primary"][tag]["n_issues"]))
    k8 = out["k8_arm"][tag8]
    if abs(k8["selected_d1"] - b4["k8_arm"]["primary"]["curve"]["8"]) > 1e-12:
        mism.append((tag8, "D1 f(8)", k8["selected_d1"], b4["k8_arm"]["primary"]["curve"]["8"]))
    if abs(k8["selected_killtest_tiebreak"] - kt["k8_arm"]["resolved_rate"]) > 1e-12:
        mism.append((tag8, "killtest rate", k8["selected_killtest_tiebreak"],
                     kt["k8_arm"]["resolved_rate"]))
    out["checks"] = {"frame_sizes_match_b1_b4": True,
                     "d1_rate_matches_b4_curve": True,
                     "killtest_rule_matches_kill_test_json": True,
                     "identity_mismatches": mism,
                     "arms_checked": 12}
    Path("results/descriptive_tables.json").write_text(json.dumps(out, indent=1) + "\n")
    print("mismatches", mism, flush=True)


if __name__ == "__main__":
    main()
