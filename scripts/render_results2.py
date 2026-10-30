"""Render RESULTS_2.md from the B1-B4 JSONs (PREREG-2 §8: verdict, numbers, concerns, checks).

Usage: .venv/bin/python scripts/render_results2.py
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.configs import CONFIGS  # noqa: E402

POLICY = {
    "nebius_openhands": ("nebius/SWE-rebench-openhands-trajectories", "OpenHands v0.54.0",
                         "SWE-rebench", "Qwen3-Coder-480B-A35B-Instruct"),
    "v1.0_openhands_minimax_m25_swe-rebench-v2": ("nvidia/Open-SWE-Traces", "OpenHands v0.53.0",
                                                  "SWE-rebench V2", "MiniMax-M2.5"),
    "v1.0_openhands_qwen35_122b_swe-rebench-v2": ("nvidia/Open-SWE-Traces", "OpenHands v0.53.0",
                                                  "SWE-rebench V2", "Qwen3.5-122B-A10B"),
    "v1.0_sweagent_minimax_m25_swe-rebench-v2": ("nvidia/Open-SWE-Traces", "SWE-agent (v1.0)",
                                                 "SWE-rebench V2", "MiniMax-M2.5"),
    "v1.0_sweagent_qwen35_122b_swe-rebench-v2": ("nvidia/Open-SWE-Traces", "SWE-agent (v1.0)",
                                                 "SWE-rebench V2", "Qwen3.5-122B-A10B"),
    "v1.1_minisweagent_qwen36_27b_scale-swe": ("nvidia/Open-SWE-Traces", "mini-swe-agent",
                                               "Scale-SWE", "Qwen3.6-27B"),
    "v1.1_minisweagent_qwen36_27b_swe-rebench-v2": ("nvidia/Open-SWE-Traces", "mini-swe-agent",
                                                    "SWE-rebench V2", "Qwen3.6-27B"),
    "v1.1_sweagent_qwen36_27b_scale-swe": ("nvidia/Open-SWE-Traces", "SWE-agent",
                                           "Scale-SWE", "Qwen3.6-27B"),
    "v1.1_sweagent_qwen36_27b_swe-rebench-v2": ("nvidia/Open-SWE-Traces", "SWE-agent",
                                                "SWE-rebench V2", "Qwen3.6-27B"),
    "v1.2_minisweagent_qwen38_27b_scale-swe": ("nvidia/Open-SWE-Traces", "mini-swe-agent",
                                               "Scale-SWE", "Qwen3.8-27B"),
    "v1.2_minisweagent_qwen38_27b_swe-rebench-v2": ("nvidia/Open-SWE-Traces", "mini-swe-agent",
                                                    "SWE-rebench V2", "Qwen3.8-27B"),
}


def pct(x, d=1):
    return "—" if x is None else f"{100 * x:.{d}f}%"


def pp(x, d=3):
    return f"{100 * x:+.{d}f}pp"


def ci_pp(lo, hi, d=3):
    if lo is None or hi is None:
        return "—"
    return f"[{100 * lo:+.{d}f}, {100 * hi:+.{d}f}]"


def pv(p):
    if p is None:
        return "—"
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def short(tag):
    return tag.replace("_swe-rebench-v2", " · srb2").replace("_scale-swe", " · scale")


def table(head, rows, align=None):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(["---"] * len(head)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def kill_test_unchanged() -> dict:
    try:
        prev = subprocess.run(["git", "show", "8b7e11b:results/kill_test.json"],
                              capture_output=True, text=True, check=True).stdout
    except Exception as exc:  # noqa: BLE001
        return {"ran": False, "error": str(exc)}
    before, after = json.loads(prev), json.loads(Path("results/kill_test.json").read_text())

    def leaves(o, p=""):
        if isinstance(o, dict):
            for k, v in o.items():
                yield from leaves(v, f"{p}/{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                yield from leaves(v, f"{p}[{i}]")
        else:
            yield p, o

    a = dict(leaves(before))
    b = dict(leaves(after))
    diffs = [k for k in a if k not in b or a[k] != b[k]]
    return {"ran": True, "values": len(a), "differences": len(diffs), "first": diffs[:5]}


def main():
    b1 = json.loads(Path("results/b1_selection_lift.json").read_text())
    b2 = json.loads(Path("results/b2_within_issue_auroc.json").read_text())
    b3 = json.loads(Path("results/b3_crossfit_certification.json").read_text())
    b4 = json.loads(Path("results/b4_adaptive_stopping.json").read_text())
    kt = json.loads(Path("results/kill_test.json").read_text())
    desc = json.loads(Path("results/descriptive_tables.json").read_text())
    if desc["checks"]["identity_mismatches"]:
        raise SystemExit(f"descriptive identity check failed: {desc['checks']}")

    L = []
    A = L.append
    A("# RESULTS_2 — four pre-registered analyses on the frozen frames")
    A("")
    A("Run: `bash reproduce_prereg2.sh` · rules: [PREREG-2.md](PREREG-2.md) frozen at `f9558d9`, "
      "amended by [DEVIATIONS.md](DEVIATIONS.md) D8 before this run · raw numbers: "
      "[B1](results/b1_selection_lift.json), [B2](results/b2_within_issue_auroc.json), "
      "[B3](results/b3_crossfit_certification.json), [B4](results/b4_adaptive_stopping.json). "
      "§8 is a DESCRIPTIVE addition: it computes no test and changes no number above it.")
    A("")
    A("**Policy models.** Taken from the dataset cards and verified against the rows: every frozen "
      "nvidia config has exactly one `metadata.teacher_model.name` value across 100% of its rows. "
      "The card states v1.0 = OpenHands v0.53.0 + SWE-agent (no separate SWE-agent version), v1.1 "
      "adds mini-swe-agent, v1.2 = Qwen3.8-27B. The nebius card names the policy directly.")
    A("")
    A(table(["corpus", "config", "agent", "benchmark", "policy model (card)"],
            [[POLICY[c["tag"]][0], c["tag"], POLICY[c["tag"]][1], POLICY[c["tag"]][2],
              POLICY[c["tag"]][3]] for c in CONFIGS]))
    A("")
    A("**Label conventions.** B1, B2 and B4 primary quantities use the PREREG convention "
      "(`resolved=-1` rows dropped before sampling). B1 and B3 repeat under `-1`-as-failure "
      "(DEVIATIONS D6). B2 is nebius-only, where no `-1` exists. Arms are never pooled. "
      "`nebius_openhands@K8` is always reported separately and enters no Holm family or sign test.")
    A("")
    A("## 1. Verdicts")
    A("")
    A("**B1 — NOT SIGNIFICANT.** Selection lift is null in 10 of 11 configs and in the K=8 arm; "
      f"the sign test is {b1['family']['sign_test']['n_pos']} positive vs "
      f"{b1['family']['sign_test']['n_neg']} negative (p = "
      f"{b1['family']['sign_test']['p_two_sided']:.3f}). One config is SIGNIFICANT− "
      "(`v1.1_minisweagent_qwen36_27b_scale-swe`, lift "
      f"{pp(b1['primary']['v1.1_minisweagent_qwen36_27b_scale-swe']['mean_lift'])}, Holm p = "
      f"{b1['primary']['v1.1_minisweagent_qwen36_27b_scale-swe']['holm_p']:.3f}): agreement there "
      "is very slightly *worse* than a random draw from the same issue.")
    A("")
    pb2 = b2["primary"]
    A("**B2 — NOT SIGNIFICANT.** Within-issue pairwise AUROC of the agent's own-test signal = "
      f"{pb2['estimate']:.3f}, 95% CI {pb2['lower']:.3f}–{pb2['upper']:.3f}, p = {pv(pb2['p'])} "
      f"on {pb2['n_pairs']:,} pairs from {b2['frame']['issues_with_pair']} issues. The CI includes "
      "0.5 and the single-test rule requires both p < 0.05 and a CI excluding 0.5. The signal is "
      "not deployable-quality evidence of correctness at this power; see §3 for what does separate "
      "pairs.")
    A("")
    A("**B3 — SIGNIFICANT+.** The cross-fit difficulty signal certifies at more α levels than "
      f"agreement in {b3['family']['sign_test']['n_pos']} of 11 configs and fewer in 0 "
      f"(exact sign test p = {b3['family']['sign_test']['p_two_sided']:.4f}). Both label "
      "conventions give 11–0. It is a label-count signal: deploying it means evaluating the other "
      "K−1 attempts, not a free alternative.")
    A("")
    st4 = b4["family"]["sign_test"]
    A("**B4 — NOT SIGNIFICANT** at K=3. "
      f"{st4['n_pos']} arms positive, {st4['n_neg']} negative, sign test p = "
      f"{st4['p_two_sided']:.3f}; no arm survives Holm (one arm's raw CI excludes 0, Holm p = "
      f"{b4['arms']['v1.1_minisweagent_qwen36_27b_scale-swe']['holm_p']:.3f}). The K=8 arm "
      f"is positive by {pp(b4['k8_arm']['primary']['point']['delta'])} "
      f"(CI {ci_pp(b4['k8_arm']['primary']['lower'], b4['k8_arm']['primary']['upper'])}, "
      f"p = {pv(b4['k8_arm']['primary']['p'])}), but it is mechanical: the stop-at-2 trigger only "
      "fires when the first two patches already agree, so the D1 submission — and its label — is "
      "unchanged; the entire Δ is the linear interpolation between f(7) and f(8). Treated as a "
      "cost measurement, not evidence that early stopping improves answers.")
    A("")
    A(table(["analysis", "primary per-arm quantity", "family rule", "family result", "verdict"],
            [["B1", "mean selected − random-K", "Holm(11) + exact sign test",
              f"{b1['family']['sign_test']['n_pos']}+/{b1['family']['sign_test']['n_neg']}−, p="
              f"{b1['family']['sign_test']['p_two_sided']:.3f}", "NOT SIGNIFICANT"],
             ["B2", "within-issue pairwise AUROC", "single test (Holm vacuous)",
              f"AUROC {pb2['estimate']:.3f}, p={pv(pb2['p'])}", "NOT SIGNIFICANT"],
             ["B3", "cross-fit − agreement certification count",
              "exact sign test (11 configs)",
              f"{b3['family']['sign_test']['n_pos']}+/"
              f"{b3['family']['sign_test']['n_neg']}−, p="
              f"{b3['family']['sign_test']['p_two_sided']:.4f}", "SIGNIFICANT+"],
             ["B4", "Δ = r_ad − f_interp(c̄)", "Holm(11) + exact sign test",
              f"{st4['n_pos']}+/{st4['n_neg']}−, p={st4['p_two_sided']:.3f}",
              "NOT SIGNIFICANT"]]))
    A("")
    A("## 2. B1 — selection lift")
    A("")
    A("`lift(x) = selected(x) − random-K(x)`, where `random-K(x)` is the issue's own sampled "
      "resolve rate. On a non-mixed issue both terms are the issue's single label, so the lift is "
      "0 by construction (DEVIATIONS D8); the mean equals `share_mixed × mean_mixed_lift` and the "
      "per-config `lift_identity` residual is 0 in every arm. Positive means the largest cluster's "
      "representative resolves more often than a uniform draw from the same issue.")
    A("")
    rows = []
    for tag, r in b1["primary"].items():
        rows.append([short(tag), r["n_issues"], pct(r["selected_rate"]), pct(r["random_rate"]),
                     pct(r["oracle_rate"]), pp(r["mean_lift"]),
                     ci_pp(r["ci"][0], r["ci"][1]), pv(r["p"]), pv(r["holm_p"]), r["verdict"]])
    r8 = b1["k8_arm"]
    rows.append(["nebius@K8 (separate)", r8["n_issues"], pct(r8["selected_rate"]),
                 pct(r8["random_rate"]), pct(r8["oracle_rate"]), pp(r8["mean_lift"]),
                 ci_pp(r8["ci"][0], r8["ci"][1]), pv(r8["p"]), "—", "SEPARATE ARM"])
    A(table(["config", "issues", "selected", "random-K", "oracle-K", "lift", "95% CI", "p",
             "Holm p", "verdict"], rows))
    A("")
    A("*SECONDARY — structure of the lift.*")
    A("")
    A(table(["config", "mixed issues", "mixed-only lift", "non-mixed lift", "share mixed",
             "mean largest cluster", "uniquely determined selection"],
            [[short(t), r["mixed"]["n_issues"], pp(r["mixed"]["mean_lift"]),
              pp(r["non_mixed_mean_lift"]), pct(r["share_mixed"], 1),
              f"{r['mean_top_size']:.2f}", pct(r["share_unique_selection"])]
             for t, r in b1["primary"].items()]))
    A("")
    A("**Sensitivity: `-1` scored as failure (separate pool and labels, not a re-score).**")
    A("")
    A(table(["config", "issues", "lift", "95% CI", "p", "Holm p", "verdict"],
            [[short(t), r["n_issues"], pp(r["mean_lift"]), ci_pp(r["ci"][0], r["ci"][1]),
              pv(r["p"]), pv(r["holm_p"]), r["verdict"]]
             for t, r in b1["alternative"].items()] +
            [["nebius@K8 (separate)", b1["k8_arm_alternative"]["n_issues"],
              pp(b1["k8_arm_alternative"]["mean_lift"]),
              ci_pp(b1["k8_arm_alternative"]["ci"][0], b1["k8_arm_alternative"]["ci"][1]),
              pv(b1["k8_arm_alternative"]["p"]), "—", "SEPARATE ARM"]]))
    A("")
    A(f"`-1`-as-failure sign test: {b1['family_alternative']['sign_test']['n_pos']}+/"
      f"{b1['family_alternative']['sign_test']['n_neg']}−, p = "
      f"{b1['family_alternative']['sign_test']['p_two_sided']:.3f}.")
    A("")
    A("*EXPLORATORY E3 — seeded random representative inside the chosen cluster (D8).*")
    A("")
    A(table(["config", "lift (E3)", "95% CI", "p", "primary lift"],
            [[short(t), pp(r["e3_random_representative"]["mean_lift"]),
              ci_pp(r["e3_random_representative"]["ci"][0],
                    r["e3_random_representative"]["ci"][1]),
              pv(r["e3_random_representative"]["p"]), pp(r["mean_lift"])]
             for t, r in b1["primary"].items()]))
    A("")
    A("E3 is close to B1 in every arm (largest difference 0.06pp): inside a chosen cluster the "
      "members almost always share the same label, so which member is submitted barely matters.")
    A("")
    A("## 3. B2 — the agent's own generated tests")
    A("")
    f = b2["frame"]
    A(f"Frame: {f['units']:,} nebius@K8 issues, {f['mixed_issues']:,} mixed-label, "
      f"{f['issues_with_pair']:,} with at least one eligible pair, **{f['pairs']:,} pairs** "
      f"({f['pairs_both_submit']:,} both-submit, {f['pairs_both_max_iteration']:,} "
      f"both-max-iteration); own-test signal present on {f['attempts_with_own_test']:,} of "
      f"{f['attempts']:,} sampled attempts ({pct(f['attempts_with_own_test'] / f['attempts'])}).")
    A("")
    A("Pairs are unordered pairs of the *frozen K=8 sample* with different labels and both own-test "
      "signals non-null; the resolved attempt is the positive. Both members come from one issue, so "
      "issue difficulty cancels by construction.")
    A("")
    A(table(["signal", "AUROC", "95% CI", "p vs 0.5", "paired Δ vs own-test", "95% CI", "p",
             "n pairs", "label"],
            [["pred_passes_gen_tests (PRIMARY)", f"{pb2['estimate']:.3f}",
              f"{pb2['lower']:.3f}–{pb2['upper']:.3f}", pv(pb2["p"]), "—", "—", "—",
              pb2["n_pairs"], "PRIMARY — " + pb2["verdict"]]] +
            [[name, f"{r['estimate']:.3f}", f"{r['lower']:.3f}–{r['upper']:.3f}", pv(r["p"]),
              f"{r['paired_diff_vs_own_test']['estimate']:+.3f}",
              f"[{r['paired_diff_vs_own_test']['lower']:+.3f}, "
              f"{r['paired_diff_vs_own_test']['upper']:+.3f}]",
              pv(r["paired_diff_vs_own_test"]["p"]), r["n_pairs"], r["label"]]
             for name, r in b2["comparisons"].items()] +
            [["gen_tests_correct (gold patch)", f"{b2['exploratory']['gen_tests_correct']['estimate']:.3f}",
              f"{b2['exploratory']['gen_tests_correct']['lower']:.3f}–"
              f"{b2['exploratory']['gen_tests_correct']['upper']:.3f}",
              pv(b2["exploratory"]["gen_tests_correct"]["p"]), "—", "—", "—",
              b2["exploratory"]["gen_tests_correct"]["n_pairs"], "EXPLORATORY"]]))
    A("")
    A("*EXPLORATORY E1 — stratified by exit reason, and the exit reason as a signal (D8).*")
    A("")
    A(table(["stratum", "own-test AUROC", "95% CI", "p", "pairs"],
            [[k, f"{v['estimate']:.3f}", f"{v['lower']:.3f}–{v['upper']:.3f}", pv(v["p"]),
              v["n_pairs"]] for k, v in b2["exploratory"]["e1_stratified"].items()]))
    A("")
    A("The own-test signal is flat inside both exit reasons; the exit reason itself is the "
      f"stronger separator on the full pair set (AUROC "
      f"{b2['comparisons']['exit_reason']['estimate']:.3f}), and fewer steps is the strongest "
      f"negative one ({b2['comparisons']['steps']['estimate']:.3f}). Neither is a "
      "correctness measurement that a practitioner can read off a patch.")
    A("")
    A("*SECONDARY — selection lift of the own-test rule (report-only; E2 is exploratory).*")
    A("")
    sl = b2["secondary_selection_lift"]
    lift_rows = []
    for rate_key, lift_key, label in (("agreement", "agreement", "agreement-only (B1 rule)"),
                                      ("own_test", "own_test", "own-test, null = -1"),
                                      ("combined", "combined", "largest cluster, then own-test"),
                                      ("own_test_null0", "e2_own_test_null0",
                                       "own-test, null = 0 (E2, EXPLORATORY)")):
        v = sl["lifts"][lift_key]
        lift_rows.append([label, pct(sl["selected_rates"][rate_key]), pp(v["estimate"]),
                          ci_pp(v["lower"], v["upper"]), pv(v["p"])])
    A(table(["rule", "selected resolve rate", "lift vs random-K", "95% CI", "p"], lift_rows))
    A("")
    A(f"Paired against agreement-only: own-test {pp(sl['lifts']['own_test_minus_agreement']['estimate'])} "
      f"(CI {ci_pp(sl['lifts']['own_test_minus_agreement']['lower'], sl['lifts']['own_test_minus_agreement']['upper'])}, "
      f"p={pv(sl['lifts']['own_test_minus_agreement']['p'])}); combined "
      f"{pp(sl['lifts']['combined_minus_agreement']['estimate'])} "
      f"(CI {ci_pp(sl['lifts']['combined_minus_agreement']['lower'], sl['lifts']['combined_minus_agreement']['upper'])}, "
      f"p={pv(sl['lifts']['combined_minus_agreement']['p'])}); E2 "
      f"{pp(sl['lifts']['e2_own_test_null0_minus_agreement']['estimate'])} "
      f"(p={pv(sl['lifts']['e2_own_test_null0_minus_agreement']['p'])}).")
    A("")
    A("**Frame discrepancy, reported not reconciled.** PREREG-2 §4's table says 11,611 pairs over "
      "943 issues. That count is reproducible, but only under two conditions the §4 sentence does "
      "not state: `scripts/b4_cost_probe.py` counted pos×neg over each issue's **full pool** of "
      "attempts and used its last column, **`gen_tests_correct`**. Full pool / gen = 11,611 / 943; "
      f"full pool / own-test = {b2['checks']['prereg_availability_table']['pairs_full_pool_own_test']:,} / "
      f"{b2['checks']['prereg_availability_table']['issues_with_pair_full_pool_own_test']:,}; "
      f"frozen K=8 sample / own-test = {f['pairs']:,} / {f['issues_with_pair']:,}. B2 follows §4's "
      "definition, so its power is lower than the table implies. No threshold or quantity changed "
      "(DEVIATIONS D9).")
    A("")
    A("## 4. B3 — cross-fit difficulty certification")
    A("")
    A("`rate_loo = (Σ resolved − resolved_rep)/(K−1)`, calibrated and evaluated with the identical "
      "kill-test machinery (same splits, τ grids, δ=0.05, n_min=30, repo-clustered bootstrap, BREAKS "
      "rule). The count is the number of α levels at which a τ certifies on the held-out-repo "
      "calibration split.")
    A("")
    rows = []
    for tag, r in b3["primary"].items():
        al = r["splits"]["heldout_repo"]["alpha"]
        rows.append([short(tag), r["agreement_count"], r["count"], f"{r['count_difference']:+d}",
                     *[("—" if al[str(a)]["tau"] is None else f"{al[str(a)]['tau']:.3f}")
                       for a in (0.05, 0.10, 0.20)],
                     r["splits"]["heldout_repo"]["alpha"]["0.2"]["verdict"]])
    k8 = b3["k8_arm"]
    al = k8["splits"]["heldout_repo"]["alpha"]
    rows.append(["nebius@K8 (separate)", k8["agreement_count"], k8["count"],
                 f"{k8['count_difference']:+d}",
                 *[("—" if al[str(a)]["tau"] is None else f"{al[str(a)]['tau']:.3f}")
                   for a in (0.05, 0.10, 0.20)],
                 al["0.2"]["verdict"]])
    A(table(["config", "agreement count", "cross-fit count", "Δ", "τ @0.05", "τ @0.10",
             "τ @0.20", "verdict @0.20"], rows))
    A("")
    A("At α=0.05 the cross-fit signal certifies in 2/11 configs (the two that also certify under "
      "agreement at α=0.20); at α=0.10 in 10/11; at α=0.20 in 11/11. The K=8 arm certifies at all "
      "three. Agreement certifies 0/11, 0/11, 2/11. Counts differ by +1 or +2 in every config, "
      "positive in 11/11 under both label conventions.")
    A("")
    ci_rows = []
    for t, r in list(b3["primary"].items()) + [("nebius@K8 (separate)", k8)]:
        cell = r["splits"]["heldout_repo"]["alpha"]["0.2"]
        ci_txt = (f"{100 * cell['ci']['lower']:.1f}–{100 * cell['ci']['upper']:.1f}%"
                  if cell["ci"] else "—")
        ci_rows.append([short(t), pct(cell["coverage"]), pct(cell["risk"]), ci_txt,
                        cell["verdict"]])
    A(table(["config (cross-fit, α=0.20)", "coverage", "held-out risk", "95% CI", "verdict"],
            ci_rows))
    A("")
    A("**Sensitivity (`-1` as failure):** counts are identical in every config (2, 2, 1, 2, 2, 2, "
      "2, 3, 2, 3, 2) and the sign test is 11–0 again (p = "
      f"{b3['family_alternative']['sign_test']['p_two_sided']:.4f}).")
    A("")
    A("## 5. B4 — adaptive stopping (and B5)")
    A("")
    A("Draw order is the frozen label-blind permutation; comparators are fixed-k D1 submissions on "
      "the same order. `Δ = r_ad − f_interp(c̄)` with the interpolation weight re-estimated inside "
      "each bootstrap replicate.")
    A("")
    rows = []
    for tag, r in b4["arms"].items():
        p = r["primary"]["point"]
        rows.append([short(tag), f"{p['c']:.3f}", pct(p["r"]), pct(p["f_interp"]),
                     pp(p["delta"]), ci_pp(r["primary"]["lower"], r["primary"]["upper"]),
                     pv(r["primary"]["p"]), pv(r["holm_p"]), r["verdict"]])
    kp = b4["k8_arm"]["primary"]["point"]
    rows.append(["nebius@K8 (separate)", f"{kp['c']:.3f}", pct(kp["r"]), pct(kp["f_interp"]),
                 pp(kp["delta"]),
                 ci_pp(b4["k8_arm"]["primary"]["lower"], b4["k8_arm"]["primary"]["upper"]),
                 pv(b4["k8_arm"]["primary"]["p"]), "—", b4["k8_arm"]["verdict"]])
    A(table(["config", "mean attempts c̄", "adaptive r_ad", "f_interp(c̄)", "Δ", "95% CI", "p",
             "Holm p", "verdict"], rows))
    A("")
    A("The saving is at most 0.12 of an attempt per K=3 issue (c̄ 2.886–2.956 of 3), so the "
      "matched-cost test is tight by construction and a null is what the pre-registration expected. "
      "One K=3 arm (`v1.1_minisweagent/qwen36_27b/scale-swe`) has raw p = 0.009 but Holm p = 0.099.")
    A("")
    A("*SECONDARY — the declared `seq_any1st` variant (first repeat anywhere).*")
    A("")
    A(table(["config", "c̄", "r_ad", "f_interp", "Δ", "95% CI", "p"],
            [[short(t), f"{r['variant_any1st']['point']['c']:.3f}",
              pct(r["variant_any1st"]["point"]["r"]),
              pct(r["variant_any1st"]["point"]["f_interp"]),
              pp(r["variant_any1st"]["point"]["delta"]),
              ci_pp(r["variant_any1st"]["lower"], r["variant_any1st"]["upper"]),
              pv(r["variant_any1st"]["p"])] for t, r in b4["arms"].items()] +
            [["nebius@K8 (separate)", f"{b4['k8_arm']['variant_any1st']['point']['c']:.3f}",
              pct(b4["k8_arm"]["variant_any1st"]["point"]["r"]),
              pct(b4["k8_arm"]["variant_any1st"]["point"]["f_interp"]),
              pp(b4["k8_arm"]["variant_any1st"]["point"]["delta"]),
              ci_pp(b4["k8_arm"]["variant_any1st"]["lower"],
                    b4["k8_arm"]["variant_any1st"]["upper"]),
              pv(b4["k8_arm"]["variant_any1st"]["p"])]]))
    A("")
    A("*Fixed-budget curves `f(k)` (the “curve across budgets”).*")
    A("")
    A(table(["config", "f(1)", "f(2)", "f(3)"],
            [[short(t), pct(r["primary"]["curve"]["1"]), pct(r["primary"]["curve"]["2"]),
              pct(r["primary"]["curve"]["3"])] for t, r in b4["arms"].items()]))
    A("")
    A("nebius@K8: " + ", ".join(f"f({k})={pct(v)}" for k, v in
                                b4["k8_arm"]["primary"]["curve"].items()) + ".")
    A("")
    b5 = b4["k8_arm"]["b5_exploratory"]
    A("*EXPLORATORY B5 (D8) — stop at the first drawn attempt whose own test passes.*")
    A("")
    A(table(["rule", "mean attempts", "resolve rate", "f_interp(c̄)", "Δ", "95% CI", "p", "verdict"],
            [["B5 own-test stop", f"{b5['point']['c']:.3f}", pct(b5["point"]["r"]),
              pct(b5["point"]["f_interp"]), pp(b5["point"]["delta"]),
              ci_pp(b5["lower"], b5["upper"]), pv(b5["p"]), b5["verdict"]],
             ["B4 seq_first2 (same arm)", f"{kp['c']:.3f}", pct(kp["r"]), pct(kp["f_interp"]),
              pp(kp["delta"]),
              ci_pp(b4["k8_arm"]["primary"]["lower"], b4["k8_arm"]["primary"]["upper"]),
              pv(b4["k8_arm"]["primary"]["p"]), "—"]]))
    A("")
    A("B5 cuts the budget from 8 attempts to 3.44 (43%) with a resolve rate statistically "
      "indistinguishable from fixed-k at that budget. It is the only one of the four analyses whose "
      "point estimate is a large practical saving; it is exploratory because it was registered in "
      "D8, after the Part-A look at the same corpus.")
    A("")
    A("## 6. Concerns")
    A("")
    A("1. **The agreement story does not survive as a selection rule.** B1's lift is null in every "
      "arm but one, and that one is negative. Whatever agreement measures at the config level, it "
      "does not pick a better-than-random attempt *within* an issue.")
    A("2. **B2's own-test signal is not significant where it was pre-registered.** The AUROC is "
      f"{pb2['estimate']:.3f} with a CI that includes 0.5. Its secondary selection lift is positive "
      f"({pp(sl['lifts']['own_test']['estimate'])}, p = {pv(sl['lifts']['own_test']['p'])}), but "
      "that is a report-only quantity on the same data; the two are not the same estimand and the "
      "positive one is not the pre-registered test.")
    A("3. **B2's power is lower than the prereg's table implies** — 4,226 pairs over 754 issues, "
      "not 11,611 over 943 (D9). A true AUROC of 0.52 would often fail to separate at this n.")
    A("4. **B3 is a strong result for a signal that is not free.** It needs the labels of the other "
      "K−1 attempts, i.e. running the evaluation harness on them first. It also inherits the "
      "kill test's unit labels, including the tie-break issue below.")
    A("5. **B4's K=8 “SIGNIFICANT+” is interpolation, not evidence.** `r_ad` equals `f(8)` exactly: "
      "the stop-at-2 trigger fires only when the two patches already agree, so the D1 submission is "
      "unchanged and continuing buys nothing. The positive Δ is `f_interp` cutting the corner below "
      "a step in `f`. At K=3 the same mechanism gives Δ ≈ 0.01pp because the saving is 0.11 of an "
      "attempt.")
    A("6. **D1's tie-break was not the one implemented.** `scripts/kill_test.py::build_units` breaks "
      "equal-size cluster ties by the lexicographically smallest canonical form, not by the smallest "
      "`trajectory_id` as DEVIATIONS D1 says. B4 uses the documented rule, so its f(K) is not the "
      "kill test's `resolved_rate`; the audit shows the rules pick a different representative in "
      "18.2–20.3% of K=3 issues and 8.4% of K=8 issues, and the arm-level full-budget resolve rate "
      "moves by −1.83 to +1.08pp (nebius K=3 +0.48pp; nebius K=8 +1.09pp). The kill test's frozen "
      "numbers are unchanged and are what KILL_TEST.md reports; this is a documentation mismatch in "
      "an already-run endpoint, not a re-analysis.")
    A("7. **Multiple comparisons.** Four analyses, twelve arms, three α, three splits, two label "
      "conventions. Each family is controlled as registered, but the sign tests have almost no "
      "power: with 11 configs the exact two-sided threshold is 10–1 (p = 0.0117), not the 9–2 "
      "stated in PREREG-2 §10 bullet 7 (9–2 gives p = 0.065).")
    A("8. **All the usual label limits stand** (WEAKNESSES #1–#4): published labels, flaky tests "
      "inside clusters, undocumented nvidia sampling, `-1` not missing at random.")
    A("")
    A("## 7. Checks")
    A("")
    kt_check = kill_test_unchanged()
    try:
        test_run = subprocess.run([".venv/bin/python", "-m", "pytest", "tests", "-q"],
                                  capture_output=True, text=True, check=True)
        test_line = [x for x in test_run.stdout.strip().splitlines() if "passed" in x][-1]
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"pytest failed while rendering: {exc}") from exc
    chk = b1["checks"]["sampled_attempts_match_kill_test"]
    A(f"- **Frames.** {chk['checked_arms']} arms / {chk['checked_issues']:,} issues re-sampled with "
      f"the frozen seed arithmetic and compared issue-by-issue with `build_units`: "
      f"{chk['mismatched_issues']} mismatched picks, {chk['unit_count_mismatches']} unit-count "
      f"mismatches, {chk['alt_unit_count_mismatches']} unit-count mismatches in the "
      "`-1`-as-failure frames (their per-issue ids were never serialised).")
    A(f"- **Shared issues.** The 204 cross-corpus issues are excluded and asserted absent from every "
      "B1–B4 frame.")
    A("- **Tie-breaks read no labels.** Selection uses canonical strings and trajectory ids only; "
      "`tests/test_prereg2.py` permutes labels and checks the representative does not move.")
    A(f"- **Kill test reproduction.** The pre-D6 JSON (`8b7e11b`) has {kt_check['values']:,} "
      f"leaf values; all are present and identical in the current `results/kill_test.json` "
      f"({kt_check['differences']} differences), i.e. the D6/D7 edits changed no "
      "primary number.")
    rb = b3["checks"]["reproduced_frozen_crossfit_cells"]
    A(f"- **B3 reproduction.** {rb['cells']} cross-fit cells re-executed; {len(rb['mismatches'])} "
      "differ from the stored `difficulty_cross_fit` baselines. Split sizes match the frozen JSON "
      f"({len(b3['checks']['split_sizes_match_frozen']['mismatches'])} mismatches).")
    A(f"- **B4 frame check.** With the kill test's own tie-break, the full-budget resolve rate "
      f"reproduces every arm's `resolved_rate` "
      f"({len(b4['checks']['kill_test_reproduced_with_its_own_tie_break']['mismatches'])} "
      "mismatches); the documented-rule values are reported beside them in §6.6. B4 was executed "
      "twice: the first execution stopped at its own sanity assertion (it assumed the two "
      "tie-breaks agreed) before writing any output; the analysis code and seeds were unchanged.")
    A(f"- **Tests.** `pytest tests -q` at render time: {test_line}.")
    A("- **Spend.** $0.00 (COST_LOG.md).")
    A("")
    A("## 8. DESCRIPTIVE — chance-level baselines, clustering, and the full budget curve")
    A("")
    A("**No hypothesis test and no verdict is computed in this section.** It adds the three tables "
      "requested after the B1–B4 run: per-arm selection baselines, the ICC of `resolved` by issue, "
      "and `f(k)` for every arm in one place. Nothing here re-estimates or replaces a frozen B1–B4 "
      "quantity; the identity checks at the end of the section are the only consistency statements.")
    A("")
    A("### 8.1 Selection baselines per arm")
    A("")
    A("`pass@1` is the mean of `resolved` over the sampled attempts; with a balanced K it equals the "
      "issue-level `random-K` baseline of §2, so the same number appears there. `selected` is the "
      "DEVIATIONS D1 rule (largest canonical cluster; equal-size ties by the smallest `trajectory_id` "
      "inside the cluster). The second selected column is the tie-break `scripts/kill_test.py` "
      "actually implements (smallest canonical string among the top clusters); it is also the rule "
      "behind `kill_test.json`'s `resolved_rate` (DEVIATIONS D9). `gap = oracle − selected`: the "
      "headroom a rule would gain from knowing in advance which sampled attempt resolves. It is a "
      "ceiling, not a deployable rule.")
    A("")
    rows = []
    for tag, r in desc["arms"].items():
        rows.append([short(tag), r["issues"], pct(r["pass_at_1"], 2), pct(r["selected_d1"], 2),
                     pct(r["oracle_pass_at_k"], 2), pp(r["selection_gap_d1"], 2),
                     pct(r["selected_killtest_tiebreak"], 2),
                     pp(r["selection_gap_killtest_tiebreak"], 2)])
    k8d = desc["k8_arm"]["nebius_openhands@K8"]
    rows.append(["nebius@K8 (separate)", k8d["issues"], pct(k8d["pass_at_1"], 2),
                 pct(k8d["selected_d1"], 2), pct(k8d["oracle_pass_at_k"], 2),
                 pp(k8d["selection_gap_d1"], 2),
                 pct(k8d["selected_killtest_tiebreak"], 2),
                 pp(k8d["selection_gap_killtest_tiebreak"], 2)])
    A(table(["config", "issues", "pass@1", "selected (D1)", "oracle pass@K", "gap (D1)",
             "selected (kill-test, D9)", "gap (kill-test)"], rows))
    A("")
    diffs = sorted((abs(100 * (r["selected_d1"] - r["selected_killtest_tiebreak"])), t)
                   for t, r in desc["arms"].items())
    A(f"The two rules disagree in the selected rate by up to {diffs[-1][0]:.2f}pp "
      f"(`{short(diffs[-1][1])}`); the next largest is {diffs[-2][0]:.2f}pp. The gap is "
      "4.8–15.8pp across the K=3 arms and 11.2pp at K=8: even at K=8, a rule that knew which "
      "attempt resolves would gain more than ten points over submitting the largest cluster.")
    A("")
    A("### 8.2 Intraclass correlation of `resolved` by issue")
    A("")
    A("One-way random-effects ICC(1), issue as the group, on the frozen K-sample frame; the CI is a "
      "repo-clustered bootstrap (`B = 2000`), i.e. whole repos resampled with replacement and all "
      "their issues kept.")
    A("")
    A(table(["config", "ICC(1)", "95% CI", "issues", "repos", "k₀"],
            [[short(t), f"{r['icc']['estimate']:.3f}",
              f"[{r['icc']['lower']:.3f}, {r['icc']['upper']:.3f}]", r["issues"], r["repos"],
              f"{r['icc']['k0']:.2f}"] for t, r in desc["arms"].items()] +
            [["nebius@K8 (separate)", f"{k8d['icc']['estimate']:.3f}",
              f"[{k8d['icc']['lower']:.3f}, {k8d['icc']['upper']:.3f}]", k8d["issues"],
              k8d["repos"], f"{k8d['icc']['k0']:.2f}"]]))
    A("")
    A("ICC(1) is 0.646–0.864 across the twelve arms (K=8: 0.798), so most of the variance in "
      "`resolved` is **between issues**, not between attempts of the same issue. That is the "
      "quantitative reason the within-issue contrasts of B1 and B2 are noisy: after issue difficulty "
      "is removed, only 14–35% of the label variance is left to rank attempts, and the repo-clustered "
      "bootstrap cannot create information that the design does not contain.")
    A("")
    A("### 8.3 Fixed-budget curve f(k), every arm in one table")
    A("")
    A("`f(k)` = mean resolve rate of the D1 submission restricted to the first k seeded draws "
      "(DEVIATIONS D8 draw order); the K=8 arm's curve is the same object at eight budgets.")
    A("")
    A(table(["config", "f(1)", "f(2)", "f(3)", "f(4)", "f(5)", "f(6)", "f(7)", "f(8)"],
            [[short(t), *[(pct(c[str(k)]) if str(k) in c else "—") for k in range(1, 9)]]
             for t, c in desc["curves"].items()]))
    A("")
    ranges = {t: 100 * (max(c.values()) - min(c.values())) for t, c in desc["curves"].items()}
    A(f"`f(k)` is flat in every arm: the full range across the budgets is at most "
      f"{max(ranges.values()):.2f}pp (`{short(max(ranges, key=ranges.get))}`), and at most 0.68pp "
      "for the K=8 arm. Spending more attempts therefore does not move the selected patch's resolve "
      "rate in any arm; the only large budget effect in the table is the oracle gap in §8.1, which "
      "needs the labels of all attempts.")
    A("")
    A("**Identity checks (no new number).** "
      f"{desc['checks']['arms_checked']} arms: frame sizes equal B1/B4; the D1 selected rate equals "
      "B4's `f(K)` exactly; the kill-test tie-break reproduces `kill_test.json`'s `resolved_rate` "
      f"exactly; `identity_mismatches` = {len(desc['checks']['identity_mismatches'])}.")
    A("")
    A("## 9. Files")
    A("")
    A("- Scripts: `scripts/b1_selection_lift.py`, `scripts/b2_within_issue_auroc.py`, "
      "`scripts/b3_crossfit_certification.py`, `scripts/b4_adaptive_stopping.py`, "
      "`scripts/descriptive_tables.py`, `scripts/render_results2.py`; shared machinery "
      "`src/prereg2.py`.")
    A("- Wrapper: `bash reproduce_prereg2.sh`. `reproduce_all.sh` is unchanged.")
    A("- Raw: `results/b1_selection_lift.json`, `results/b2_within_issue_auroc.json`, "
      "`results/b3_crossfit_certification.json`, `results/b4_adaptive_stopping.json`, "
      "`results/descriptive_tables.json`.")
    Path("RESULTS_2.md").write_text("\n".join(L) + "\n")
    print("wrote RESULTS_2.md", flush=True)


if __name__ == "__main__":
    main()
