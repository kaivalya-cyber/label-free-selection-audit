"""B4 — adaptive stopping (PREREG-2 §6) and the exploratory B5 rule (D8).

Draw order is the frozen label-blind permutation `seeded_rng("seq", ktag, key)` over the issue's
sampled attempts sorted by trajectory_id. Comparators are fixed-k D1 submissions on the same order.

Usage: .venv/bin/python scripts/b4_adaptive_stopping.py   -> results/b4_adaptive_stopping.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.configs import CONFIGS  # noqa: E402
from src.prereg2 import (d1_pick, d1_pick_killtest, holm, load_attempts, matched_delta,  # noqa: E402
                         seq_any1st, shared_keys, sign_test, write_json)
from src.risk import seeded_rng  # noqa: E402


def own_test_map(shared: set[str]) -> dict[str, float | None]:
    sig = pd.read_parquet("out/signals/nebius_openhands.parquet",
                          columns=["trajectory_id", "key"]).drop_duplicates("trajectory_id")
    light = pd.read_parquet("out/nebius_light.parquet",
                            columns=["trajectory_id", "pred_passes_gen_tests"])
    m = sig.merge(light, on="trajectory_id", how="left", validate="1:1")
    return {t: (None if pd.isna(p) else float(p))
            for t, p in zip(m.trajectory_id, m.pred_passes_gen_tests)}


def arm(frame: pd.DataFrame, ktag: str, K: int, own: dict | None = None) -> dict:
    used2, sub2, used_any, sub_any = [], [], [], []
    prefix, repos = [], []
    b5_used, b5_sub = [], []
    kt_labels, tie_diff, tie_lab_diff = [], 0, 0
    for key, g in frame.groupby("key", sort=True):
        tids = sorted(g.trajectory_id)
        canon = dict(zip(g.trajectory_id, g.canonical.astype(str)))
        lab = dict(zip(g.trajectory_id, g.resolved.astype(int)))
        order = [tids[i] for i in seeded_rng("seq", ktag, key).permutation(K)]
        pref = np.full(K + 1, np.nan)
        for kk in range(1, K + 1):
            pref[kk] = lab[d1_pick(order[:kk], canon)]
        prefix.append(pref)
        repos.append(g.repo.iloc[0])
        rep_doc = d1_pick(tids, canon)
        rep_kt = d1_pick_killtest(tids, canon)
        kt_labels.append(lab[rep_kt])
        if rep_doc != rep_kt:
            tie_diff += 1
            tie_lab_diff += int(lab[rep_doc] != lab[rep_kt])

        stop2 = canon[order[0]] == canon[order[1]]
        used2.append(2 if stop2 else K)
        sub2.append(lab[min(order[0], order[1])] if stop2 else pref[K])

        u, rep = seq_any1st(order, canon)
        used_any.append(u)
        sub_any.append(lab[rep])

        if own is not None:
            first = next((i for i, t in enumerate(order) if own.get(t) == 1.0), None)
            if first is None:
                b5_used.append(K)
                b5_sub.append(pref[K])
            else:
                b5_used.append(first + 1)
                b5_sub.append(lab[order[first]])

    prefix = np.vstack(prefix)
    rec = {"issues": int(len(frame)), "repos": int(len(set(repos))),
           "k_max": K,
           "tie_break_audit": {"issues_where_rules_differ": int(tie_diff),
                               "share": float(tie_diff / len(frame)),
                               "label_disagreement_among_them": int(tie_lab_diff),
                               "f_full_budget_killtest_rule": float(np.mean(kt_labels)),
                               "f_full_budget_documented_rule": float(prefix[:, K].mean())},
           "primary": matched_delta(used2, sub2, prefix, repos,
                                                (ktag, "matched")),
           "variant_any1st": matched_delta(used_any, sub_any, prefix, repos,
                                           (ktag, "matched", "any1st"))}
    rec["variant_any1st"]["label"] = "SECONDARY (declared variant, not in Holm)"
    if own is not None:
        rec["b5_exploratory"] = {"rule": ("stop at the first drawn attempt whose own-test signal "
                                          "is 1; null never stops; else K_max and D1 representative"),
                                 **matched_delta(b5_used, b5_sub, prefix, repos,
                                                 (ktag, "b5")),
                                 "label": "EXPLORATORY (D8 B5)"}
    return rec


def decide(block: dict, holm_block: dict | None) -> dict:
    for tag, rec in block.items():
        p = rec["primary"]["p"]
        adj = holm_block["adjusted"][tag] if holm_block and tag in holm_block["adjusted"] else p
        d = rec["primary"]["point"]["delta"]
        rec["holm_p"] = adj
        if adj < 0.05 and d > 0:
            rec["verdict"] = "SIGNIFICANT+"
        elif adj < 0.05 and d < 0:
            rec["verdict"] = "SIGNIFICANT-"
        else:
            rec["verdict"] = "NOT SIGNIFICANT"
    return block


def main():
    shared = shared_keys()
    frozen = json.loads(Path("results/kill_test.json").read_text())
    out = {"analysis": "B4 adaptive stopping", "prereg": "PREREG-2 §6", "deviation": "D8",
           "arms": {}, "k8_arm": {}, "family": {}, "checks": {}}

    print("B4 K=3 arms ...", flush=True)
    for cfg in CONFIGS:
        tag = cfg["tag"]
        frame = load_attempts(cfg, 3, shared=shared)
        out["arms"][tag] = arm(frame, f"{tag}@K3", 3)
        print(f"  {tag}", flush=True)

    neb = next(c for c in CONFIGS if c["tag"] == "nebius_openhands")
    f8 = load_attempts(neb, 8, shared=shared)
    out["k8_arm"] = arm(f8, "nebius_openhands@K8", 8, own=own_test_map(shared))
    out["k8_arm"]["label"] = "SEPARATE ARM (not in any Holm family)"

    pv = {t: r["primary"]["p"] for t, r in out["arms"].items()}
    h = holm(pv)
    decide(out["arms"], h)
    dirs = {t: (1 if r["primary"]["point"]["delta"] > 0 else -1
                if r["primary"]["point"]["delta"] < 0 else 0) for t, r in out["arms"].items()}
    st = sign_test(dirs)
    st["verdict"] = ("SIGNIFICANT+" if st["p_two_sided"] < 0.05 and st["n_pos"] > st["n_neg"]
                     else "SIGNIFICANT-" if st["p_two_sided"] < 0.05 else "NOT SIGNIFICANT")
    out["family"] = {"holm": h, "sign_test": st, "directions": dirs}
    d = out["k8_arm"]["primary"]["point"]["delta"]
    out["k8_arm"]["verdict"] = ("SIGNIFICANT+" if out["k8_arm"]["primary"]["p"] < 0.05 and d > 0
                                else "SIGNIFICANT-" if out["k8_arm"]["primary"]["p"] < 0.05
                                else "NOT SIGNIFICANT")
    for key in ("b5_exploratory",):
        if key in out["k8_arm"]:
            b = out["k8_arm"][key]
            b["verdict"] = ("SIGNIFICANT+" if b["p"] < 0.05 and b["point"]["delta"] > 0
                            else "SIGNIFICANT-" if b["p"] < 0.05 else "NOT SIGNIFICANT")

    # The kill test's resolved_rate is reproducible only with ITS tie-break (canonical-string
    # minimum, not D1's smallest trajectory_id). B4 uses the documented D1 rule, so f(K) is not
    # expected to equal it; both are reported and the difference is audited per arm.
    mism = []
    for tag, rec in out["arms"].items():
        want = frozen["configs"][tag]["resolved_rate"]
        got = rec["tie_break_audit"]["f_full_budget_killtest_rule"]
        if abs(got - want) > 1e-12:
            mism.append({"arm": tag, "f(K) kill-test rule": got,
                         "kill_test_resolved_rate": want})
    want8 = frozen["k8_arm"]["resolved_rate"]
    got8 = out["k8_arm"]["tie_break_audit"]["f_full_budget_killtest_rule"]
    if abs(got8 - want8) > 1e-12:
        mism.append({"arm": "nebius@K8", "f(K) kill-test rule": got8,
                     "kill_test_resolved_rate": want8})
    out["checks"]["kill_test_reproduced_with_its_own_tie_break"] = {"mismatches": mism}
    assert not mism, mism[:3]
    out["checks"]["tie_break_mismatch"] = {
        "documented": "D1: equal-size clusters broken by the smallest trajectory_id",
        "implemented_in_kill_test": "smallest canonical string, then smallest trajectory_id",
        "arms": {t: r["tie_break_audit"] for t, r in out["arms"].items()},
        "note": ("B4 follows the documented D1 rule. The frozen kill test used the canonical-string "
                 "tie-break in scripts/kill_test.py::build_units, so its resolved_rate differs from "
                 "f(K) here; the gap is audited above and reported, not reconciled.")}
    out["checks"]["permutation_is_label_blind"] = True  # seeded_rng("seq", ktag, key) only
    write_json("results/b4_adaptive_stopping.json", out)
    print("wrote results/b4_adaptive_stopping.json", flush=True)


if __name__ == "__main__":
    main()
