"""B2 — within-issue pairwise AUROC of the agent's own-test signal (PREREG-2 §4, D8).

nebius@K8 only. Pairs are unordered pairs of the *frozen K=8 sampled attempts* with different
labels and both own-test signals non-null; the resolved attempt is the positive.

Usage: .venv/bin/python scripts/b2_within_issue_auroc.py   -> results/b2_within_issue_auroc.json
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.configs import CONFIGS  # noqa: E402
from src.prereg2 import (auroc_scores, bootstrap_mean, bootstrap_sum_ratio, load_attempts,  # noqa: E402
                         select_agreement_rep, select_combined_rep, select_signal_rep, shared_keys,
                         write_json)

KTAG = "nebius_openhands@K8"
K = 8


def load_frame() -> pd.DataFrame:
    neb = next(c for c in CONFIGS if c["tag"] == "nebius_openhands")
    f = load_attempts(neb, K, shared=shared_keys())
    extra = pd.read_parquet("out/nebius_light.parquet",
                            columns=["trajectory_id", "exit_status", "pred_passes_gen_tests",
                                     "gen_tests_correct"])
    m = f.merge(extra, on="trajectory_id", how="left", validate="1:1")
    assert len(m) == len(f) and m.trajectory_id.is_unique
    assert m.groupby("key").size().eq(K).all()
    m["own_test"] = m.pred_passes_gen_tests
    m["gen"] = m.gen_tests_correct
    m["submit"] = m.exit_status.eq("submit")
    m["max_iter"] = m.exit_status.str.startswith("RuntimeError: Agent reached")
    assert m.own_test.isna().sum() == m.pred_passes_gen_tests.isna().sum()
    return m


def build(frame: pd.DataFrame):
    """Per-pair arrays for every signal + per-issue selection rows."""
    pair = {k: ([], []) for k in ("own_test", "gen", "agreement", "steps", "exit_reason")}
    meta = {"repo": [], "both_submit": [], "both_max": [], "gen_ok": []}
    issues = []
    keys_with_pair: set[str] = set()
    for key, g in frame.groupby("key", sort=True):
        g = g.set_index("trajectory_id")
        tids = sorted(g.index)
        lab = g.resolved.astype(int).to_dict()
        can = g.canonical.astype(str).to_dict()
        sig = {t: (None if pd.isna(g.loc[t, "own_test"]) else float(g.loc[t, "own_test"]))
               for t in tids}
        gen = {t: (None if pd.isna(g.loc[t, "gen"]) else float(g.loc[t, "gen"])) for t in tids}
        steps = g.steps.astype(float).to_dict()
        submit = g.submit.to_dict()
        maxit = g.max_iter.to_dict()
        size = pd.Series([can[t] for t in tids]).value_counts().to_dict()
        repo = g.repo.iloc[0]
        pos_sig = {"own_test": sig, "gen": gen, "steps": steps,
                   "agreement": {t: size[can[t]] / K for t in tids},
                   "exit_reason": {t: 1.0 if submit[t] else 0.0 for t in tids}}

        for a in range(len(tids)):
            for b in range(a + 1, len(tids)):
                ta, tb = tids[a], tids[b]
                if lab[ta] == lab[tb] or sig[ta] is None or sig[tb] is None:
                    continue
                pos, neg = (ta, tb) if lab[ta] == 1 else (tb, ta)
                for name in pair:
                    if pos_sig[name][pos] is None or pos_sig[name][neg] is None:
                        pair[name][0].append(np.nan)
                        pair[name][1].append(np.nan)
                    else:
                        pair[name][0].append(float(pos_sig[name][pos]))
                        pair[name][1].append(float(pos_sig[name][neg]))
                meta["repo"].append(repo)
                meta["both_submit"].append(bool(submit[ta] and submit[tb]))
                meta["both_max"].append(bool(maxit[ta] and maxit[tb]))
                meta["gen_ok"].append(gen[ta] is not None and gen[tb] is not None)
                keys_with_pair.add(key)

        random_k = float(np.mean([lab[t] for t in tids]))
        agree_rep = select_agreement_rep(can, KTAG, key)["rep"]
        own_rep = select_signal_rep(tids, sig, KTAG, key, null_score=-1.0)
        own0_rep = select_signal_rep(tids, sig, KTAG, key, null_score=0.0)
        comb_rep = select_combined_rep(tids, {t: size[can[t]] for t in tids}, sig, KTAG, key)
        issues.append({"key": key, "repo": repo, "random_k": random_k,
                       "agreement": float(lab[agree_rep]), "own_test": float(lab[own_rep]),
                       "own_test_null0": float(lab[own0_rep]),
                       "combined": float(lab[comb_rep])})
    pairs = pd.DataFrame({"repo": meta["repo"], "both_submit": meta["both_submit"],
                          "both_max": meta["both_max"], "gen_ok": meta["gen_ok"]})
    for name, (p, n) in pair.items():
        pairs[f"{name}_pos"] = p
        pairs[f"{name}_neg"] = n
    return pairs, pd.DataFrame(issues), keys_with_pair


def auroc_row(pairs, signal, seed_tag, null=0.5, subset=None):
    d = pairs if subset is None else pairs[subset]
    ok = d[f"{signal}_pos"].notna().to_numpy()
    d = d[ok]
    s = auroc_scores(d[f"{signal}_pos"], d[f"{signal}_neg"])
    boot = bootstrap_sum_ratio(s, np.ones(len(s)), d.repo.to_numpy(),
                               seed_parts=(KTAG, "auroc", seed_tag), null=null)
    boot["n_pairs"] = int(len(d))
    boot["n_repos"] = int(d.repo.nunique())
    return boot


def diff_row(pairs, other, subset=None):
    d = pairs if subset is None else pairs[subset]
    ok = d[f"{other}_pos"].notna().to_numpy() & d["own_test_pos"].notna().to_numpy()
    d = d[ok]
    s = auroc_scores(d[f"{other}_pos"], d[f"{other}_neg"]) - \
        auroc_scores(d["own_test_pos"], d["own_test_neg"])
    boot = bootstrap_sum_ratio(s, np.ones(len(s)), d.repo.to_numpy(),
                               seed_parts=(KTAG, "auroc", f"{other}-vs-own"), null=0.0)
    boot["n_pairs"] = int(len(d))
    return boot


def probe_pairs(shared: set[str]) -> dict:
    """Reproduce the label-conditioned count in PREREG §4 (full pool, probe definition).

    `scripts/b4_cost_probe.py` took `col = light_cols[-1]`, i.e. it counted pairs non-null on
    `gen_tests_correct`, not on `pred_passes_gen_tests`. Both counts are returned so the table's
    provenance is visible.
    """
    sig = pd.read_parquet("out/signals/nebius_openhands.parquet",
                          columns=["key", "trajectory_id", "resolved"])
    sig = sig[~sig.key.isin(shared)]
    n = sig.groupby("key").size()
    sig = sig[sig.key.isin(set(n[n >= 8].index))]
    light = pd.read_parquet("out/nebius_light.parquet",
                            columns=["trajectory_id", "pred_passes_gen_tests",
                                     "gen_tests_correct"])
    m = sig.merge(light, on="trajectory_id", how="left", validate="1:1")
    out = {}
    for col in ("pred_passes_gen_tests", "gen_tests_correct"):
        ok = m[col].notna()
        pos = m[ok & m.resolved.eq(1)].groupby("key").size()
        neg = m[ok & m.resolved.eq(0)].groupby("key").size()
        prod = (pos * neg).fillna(0)
        out[col] = {"pairs": int(prod.sum()), "issues_with_pair": int((prod > 0).sum())}
    out["attempts"] = int(len(m))
    out["attempts_with_own_test"] = int(m.pred_passes_gen_tests.notna().sum())
    return out


def verdict(lower: float, upper: float, p: float) -> str:
    if p < 0.05 and lower > 0.5:
        return "SIGNIFICANT+"
    if p < 0.05 and upper < 0.5:
        return "SIGNIFICANT-"
    return "NOT SIGNIFICANT"


def main():
    frame = load_frame()
    pairs, issues, keys_with_pair = build(frame)
    print(f"pairs {len(pairs)}, issues with a pair {len(keys_with_pair)}", flush=True)

    out = {"analysis": "B2 within-issue pairwise AUROC", "prereg": "PREREG-2 §4",
           "deviation": "D8", "arm": KTAG,
           "signals": {"primary": "pred_passes_gen_tests (own generated tests pass on own patch)",
                       "gen_tests_correct": "gold-patch-dependent; EXPLORATORY",
                       "agreement": "canonical cluster size within the K=8 sample / 8",
                       "steps": "assistant-message count",
                       "exit_reason": "submit = 1, max-iteration = 0"},
           "frame": {"units": int(frame.key.nunique()),
                     "mixed_issues": int((issues.random_k.gt(0) & issues.random_k.lt(1)).sum()),
                     "issues_with_pair": int(len(keys_with_pair)),
                     "pairs": int(len(pairs)),
                     "pairs_both_submit": int(pairs.both_submit.sum()),
                     "pairs_both_max_iteration": int(pairs.both_max.sum()),
                     "pairs_with_both_gen": int(pairs.gen_ok.sum()),
                     "attempts": int(len(frame)),
                     "attempts_with_own_test": int(frame.own_test.notna().sum())},
           "primary": {}, "comparisons": {}, "exploratory": {}, "checks": {}}

    prim = auroc_row(pairs, "own_test", "own_test")
    prim["verdict"] = verdict(prim["lower"], prim["upper"], prim["p"])
    out["primary"] = prim

    for name in ("agreement", "steps", "exit_reason"):
        r = auroc_row(pairs, name, name)
        r["paired_diff_vs_own_test"] = diff_row(pairs, name)
        r["label"] = "SECONDARY"
        out["comparisons"][name] = r

    gen = auroc_row(pairs, "gen", "gen", subset=pairs.gen_ok)
    gen["label"] = "EXPLORATORY (uses the golden patch at evaluation time; not deployable)"
    out["exploratory"]["gen_tests_correct"] = gen

    e1 = {}
    for name, mask in (("both_submit", pairs.both_submit),
                       ("both_max_iteration", pairs.both_max)):
        r = auroc_row(pairs, "own_test", f"e1-{name}", subset=mask)
        r["n_pairs"] = int(mask.sum())
        r["label"] = "EXPLORATORY"
        e1[name] = r
    out["exploratory"]["e1_stratified"] = e1

    # secondary selection lifts (per-issue, paired against random-K and against agreement-only)
    lifts = {}
    for name, label in (("agreement", "agreement-only (B1 rule)"),
                        ("own_test", "own-test, null = -1"),
                        ("combined", "largest cluster then own-test")):
        lifts[name] = bootstrap_mean(issues[name] - issues.random_k, issues.repo,
                                     (KTAG, "select", name))
    lifts["e2_own_test_null0"] = bootstrap_mean(issues.own_test_null0 - issues.random_k,
                                                issues.repo, (KTAG, "select", "e2"))
    lifts["e2_own_test_null0"]["label"] = "EXPLORATORY (D8 E2)"
    for col, name in (("own_test", "own_test"), ("combined", "combined"),
                      ("own_test_null0", "e2_own_test_null0")):
        lifts[f"{name}_minus_agreement"] = bootstrap_mean(
            issues[col] - issues.agreement, issues.repo, (KTAG, "selectdiff", name))
    out["secondary_selection_lift"] = {
        "random_rate": float(issues.random_k.mean()),
        "selected_rates": {k: float(issues[k].mean()) for k in
                           ("agreement", "own_test", "own_test_null0", "combined")},
        "lifts": lifts}
    out["secondary_selection_lift"]["label"] = "SECONDARY (report-only)"

    # where PREREG §4's 11,611 came from: the probe counted the full pool, not the frozen sample
    probe = probe_pairs(shared_keys())
    out["checks"]["prereg_availability_table"] = {
        "full_pool_full_pool": probe["attempts"],
        "full_pool_with_own_test": probe["attempts_with_own_test"],
        "pairs_full_pool_own_test": probe["pred_passes_gen_tests"]["pairs"],
        "issues_with_pair_full_pool_own_test": probe["pred_passes_gen_tests"]["issues_with_pair"],
        "pairs_full_pool_gen_tests_correct": probe["gen_tests_correct"]["pairs"],
        "issues_with_pair_full_pool_gen_tests_correct": probe["gen_tests_correct"]["issues_with_pair"],
        "prereg_table_value": 11611,
        "prereg_table_issues": 943,
        "pairs_in_frozen_k8_sample": int(len(pairs)),
        "issues_with_pair_frozen_sample": int(len(keys_with_pair)),
        "note": ("PREREG §4's 11,611 / 943 are reproduced exactly, but two things differ from the "
                 "sentence they sit under: (a) scripts/b4_cost_probe.py counts pos*neg over each "
                 "issue's FULL pool, not the frozen K=8 sample; (b) it uses the last column "
                 "(`gen_tests_correct`), not the primary own-test signal. On the full pool the "
                 "own-test count is 11,614 / 942; on the frozen K=8 sample the analysis uses "
                 "4,226 pairs over 754 issues. Reported, not reconciled.")}
    assert probe["gen_tests_correct"]["pairs"] == 11611
    assert probe["gen_tests_correct"]["issues_with_pair"] == 943
    out["checks"]["pair_construction"] = {
        "pairs": int(len(pairs)), "issues_with_pair": int(len(keys_with_pair)),
        "repos": int(pairs.repo.nunique()),
        "every_pair_has_two_distinct_labels": True,   # enforced by the build loop
        "sample_size_per_issue": int(frame.groupby("key").size().unique()[0])}
    write_json("results/b2_within_issue_auroc.json", out)
    print("wrote results/b2_within_issue_auroc.json", flush=True)


if __name__ == "__main__":
    main()
