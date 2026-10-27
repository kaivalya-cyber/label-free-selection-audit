"""Render KILL_TEST.md from results/kill_test.json (no computation, pure formatting).

DEVIATIONS D6/D7 reporting rules:
  * both label conventions (`resolved=-1` dropped / counted as failure) are shown side by side for
    every arm; neither is primary;
  * the difficulty baseline shown as honest is the cross-fit (leave-one-out) one; the plug-in
    version stays only as a labelled oracle ceiling because it includes the scored label.
"""
import json
from pathlib import Path

J = json.loads(Path("results/kill_test.json").read_text())
ALPHAS = [str(a) for a in J["alphas"]]
ALT = J.get("configs_minus1_failure") or {}
L = []


def pct(x, nd=1):
    return "—" if x is None else f"{100 * x:.{nd}f}%"


def ci(rec):
    c = rec.get("ci")
    if not c:
        return "—"
    return f"[{pct(c['lower'])}, {pct(c['upper'])}]"


def arms():
    return list(J["configs"].items()) + [("nebius@K8", J["k8_arm"] or {})]


def alt_rec(tag):
    if tag == "nebius@K8":
        return J.get("k8_arm_minus1_failure") or {}
    return ALT.get(tag) or {}


def tau_s(x):
    return "—" if x is None else f"{x:.3f}"


CONV_LABELS = {"drop": "resolved=-1 dropped (PREREG primary)",
              "minus1_failure": "resolved=-1 counted as failure"}

BASE_LABELS = {
    "patch_size": "patch_size",
    "step_count": "step_count",
    "difficulty_cross_fit": "difficulty_cross_fit — HONEST (rate of the other K−1 attempts)",
    "difficulty_plugin_rate": "difficulty_plugin_rate — ORACLE CEILING (includes the scored label)",
    "always_submit": "always_submit",
}

L.append("# KILL_TEST — pre-registered agreement-based abstention, calibrated → held-out\n")
L.append("Command: `.venv/bin/python scripts/kill_test.py` · raw numbers: "
         "[results/kill_test.json](results/kill_test.json) · rules: [PREREG.md](PREREG.md), "
         "[DEVIATIONS.md](DEVIATIONS.md) (D6/D7 fix how this file reports)\n")
L.append("Label convention: `resolved = -1` (unknown, nvidia only) is shown **both ways** — dropped "
         "from the pool before sampling, and counted as failure — for every arm. The two columns are "
         "two complete pipelines (they differ in pool eligibility as well as in labelling), each with "
         "its own τ, interval and verdict. Neither is primary here.\n")

# ---------------------------------------------------------------- bottom line
cert = {a: [(t, c["splits"]["heldout_repo"]["alpha"][a]) for t, c in arms() if c
            and c["splits"]["heldout_repo"]["alpha"][a].get("verdict") in ("HOLDS", "BREAKS")]
        for a in ALPHAS}
cert_alt = {a: [(t, alt_rec(t).get("splits", {}).get("heldout_repo", {}).get("alpha", {}).get(a, {}))
                for t, _ in arms() if alt_rec(t)]
            for a in ALPHAS}
cert_alt = {a: [(t, r) for t, r in v if r.get("verdict") in ("HOLDS", "BREAKS")] for a, v in cert_alt.items()}
breaks = [(t, a) for a in ALPHAS for t, r in cert[a] if r.get("verdict") == "BREAKS"]
breaks_alt = [(t, a) for a in ALPHAS for t, r in cert_alt[a] if r.get("verdict") == "BREAKS"]
tot_cells = 0
tot_breaks = 0
for _t, _c in arms():
    for _rec in (_c, alt_rec(_t)):
        if not _rec:
            continue
        for _sd in _rec.get("splits", {}).values():
            for _a in ALPHAS:
                tot_cells += 1
                if _sd["alpha"][_a].get("verdict") == "BREAKS":
                    tot_breaks += 1

L.append("\n## Bottom line\n")
if not breaks and not breaks_alt:
    L.append(f"- **0 BREAKS; {len(cert['0.2'])} arms testable; sensitive to the `-1` convention.** "
             f"({tot_breaks} BREAKS in {tot_cells} pre-registered cells = arms × splits × α × label "
             f"conventions; "
             f"\"testable\" counts arms that certify a τ at any α, all of them at α=0.20 only; "
             f"`NO-COVERAGE` is not a pass.)")
else:
    L.append(f"- **{len(breaks)} BREAKS under drop-`-1`, {len(breaks_alt)} under `-1`-as-failure; "
             f"{len(cert['0.2'])} arms testable; sensitive to the `-1` convention.**")
for a in ALPHAS:
    L.append(f"- α={a}: drop-`-1` {len(cert[a])}/{len(arms())} arms certify a τ, "
             f"{sum(1 for _, r in cert[a] if r.get('verdict') == 'BREAKS')} BREAKS; "
             f"`-1`-as-failure {len(cert_alt[a])}/{len(arms())} arms certify a τ, "
             f"{sum(1 for _, r in cert_alt[a] if r.get('verdict') == 'BREAKS')} BREAKS.")
for label, cc in (("drop-`-1`", cert), ("`-1`-as-failure", cert_alt)):
    if cc["0.2"]:
        covs = [r["coverage"] for _, r in cc["0.2"] if r.get("coverage") is not None]
        risks = [r["risk"] for _, r in cc["0.2"] if r.get("risk") is not None]
        if covs and risks:
            L.append(f"- At α=0.20 ({label}) the certified cells have coverage "
                     f"{pct(min(covs))}–{pct(max(covs))} and held-out-repo risk "
                     f"{pct(min(risks))}–{pct(max(risks))} vs α=20%.")

# -1-as-failure re-scoring of the *same* rule (the fragility WEAKNESSES #4 reports)
frag = []
for t, r in cert["0.2"]:
    c = dict(arms())[t]
    m = c.get("minus1_sensitivity", {}).get("0.2", {})
    if r.get("verdict") == "HOLDS" and m.get("risk") is not None:
        frag.append((t, r["risk"], m["risk"]))
if frag:
    txt = "; ".join(f"`{t}` {pct(a)} → {pct(b)}" for t, a, b in frag)
    L.append(f"- **Same τ, other label set:** re-scoring the certified rule with `resolved=-1` as "
             f"failure (confounded with the sampling change — different pool, see below) raises "
             f"held-out risk above α=20% "
             f"in every certified cell ({txt}). The guarantee therefore depends on which convention "
             f"you accept as correct.")

# difficulty baselines: honest cross-fit first, oracle ceiling second
cf_rows, or_rows = [], []
for t, c in arms():
    if not c:
        continue
    b = c.get("baselines", {})
    if "difficulty_cross_fit" in b:
        cf_rows.append((t, b["difficulty_cross_fit"]))
    if "difficulty_plugin_rate" in b:
        or_rows.append((t, b["difficulty_plugin_rate"]))
for name, rows in (("difficulty_cross_fit", cf_rows), ("difficulty_plugin_rate (oracle)", or_rows)):
    ci_ = [r for _, r in rows if r["0.2"].get("verdict") in ("HOLDS", "BREAKS")]
    if ci_:
        covs = [r["0.2"]["coverage"] for r in ci_]
        risks = [r["0.2"]["risk"] for r in ci_]
        L.append(f"- {name} at α=0.20: certifies in {len(ci_)}/{len(rows)} arms, coverage "
                 f"{pct(min(covs))}–{pct(max(covs))}, held-out risk {pct(min(risks))}–{pct(max(risks))}"
                 + (". This row includes the scored label, so its coverage and risk are not "
                    "achievable by any deployable signal; it is reported only as a ceiling."
                    if "oracle" in name else
                    ". It needs the labels of the other K−1 attempts, which in deployment means "
                    "running the tests on those attempts first."))
L.append("- The binding constraint is power, not calibration breakage: exact patch identity is rare "
         "(see DATA_RECON/claims C35–C38), so the unanimous subset is small and its error is only "
         "sometimes low enough for Clopper–Pearson to certify α. `NO-COVERAGE` cells carry no risk "
         "estimate and are reported as such, not as passes.")
L.append("")

# ---------------------------------------------------------------- headline table
L.append("## Verdicts (headline split = held-out-repo, per config, both label conventions)\n")
hdr = ["config", "issues (drop / −1=fail)", "base error (drop / −1=fail)"]
for a in ALPHAS:
    hdr += [f"α={a} drop", f"α={a} −1=fail"]
L.append("| " + " | ".join(hdr) + " |")
L.append("|---|---|---|" + "---|" * 2 * len(ALPHAS))


def cell(rec):
    if not rec:
        return "—"
    if rec.get("tau") is None:
        return f"{rec.get('verdict', '—')} (—, —)"
    return f"{rec.get('verdict', '—')} ({pct(rec.get('coverage'))}, {pct(rec.get('risk'))})"


for t, c in arms():
    if not c:
        continue
    ar = alt_rec(t)
    row = [t, f"{c.get('units')} / {ar.get('units', '—')}",
           f"{pct(c.get('base_error'))} / {pct(ar.get('base_error'))}"]
    for a in ALPHAS:
        row.append(cell(c["splits"]["heldout_repo"]["alpha"][a]))
        row.append(cell(ar.get("splits", {}).get("heldout_repo", {}).get("alpha", {}).get(a)))
    L.append("| " + " | ".join(row) + " |")
L.append("\nCells are `VERDICT (coverage, selective risk)`. BREAKS = repo-clustered lower CI bound "
         "> α + 0.05; HOLDS = otherwise; NO-COVERAGE = no τ certified on calibration (not a pass). "
         "The `−1`-as-failure columns are separate certifications on a larger pool, not re-scores of "
         "the drop-`-1` rule; the re-score is reported per config below.\n")

# ---------------------------------------------------------------- per config detail
for tag, c in arms():
    if not c:
        continue
    L.append(f"\n## {tag}\n")
    conv = c.get('convention') or 'drop'
    L.append(f"`{c.get('display')}` · K={c.get('k')} · convention "
             f"`{CONV_LABELS.get(conv, conv)}` · issues "
             f"{c.get('units')} · repos {c.get('repos')} · resolved rate {pct(c.get('resolved_rate'))} "
             f"· agreement levels {json.dumps(c.get('agreement_levels'))} · same-cluster label "
             f"disagreement {pct(c.get('same_cluster_disagreement_share'))}\n")
    if c.get("truncation"):
        L.append(f"Truncation: max-iteration rows {pct(c['truncation']['max_iteration_share'])}, "
                 f"non-submit rows {pct(c['truncation']['non_submit_share'])}.\n")
    if c.get("temporal_missing_issues"):
        L.append(f"Temporal split not applicable for {c['temporal_missing_issues']} issues (no "
                 f"timestamps).\n")
    for split, sd in c.get("splits", {}).items():
        L.append(f"\n**{split}** (calib {sd.get('n_calib')} / eval {sd.get('n_eval')})\n")
        L.append("| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |")
        L.append("|---|---|---|---|---|---|---|")
        for a in ALPHAS:
            r = sd["alpha"][a]
            L.append(f"| {a} | {tau_s(r.get('tau'))} | {r.get('n_submitted')} | "
                     f"{pct(r.get('coverage'))} | {pct(r.get('risk'))} | {ci(r)} | {r.get('verdict')} |")
        if "secondary_files" in sd:
            L.append("\n*secondary signal — files-touched agreement*\n")
            L.append("| α | τ | submitted | coverage | risk | verdict |")
            L.append("|---|---|---|---|---|---|")
            for a in ALPHAS:
                r = sd["secondary_files"][a]
                L.append(f"| {a} | {tau_s(r.get('tau'))} | {r.get('n_submitted')} | "
                         f"{pct(r.get('coverage'))} | {pct(r.get('risk'))} | {r.get('verdict')} |")
    L.append("\n**Baselines (held-out-repo split, calibrated identically)**\n")
    L.append("| method | α | τ | coverage | risk | verdict |")
    L.append("|---|---|---|---|---|---|")
    for name, bl in c.get("baselines", {}).items():
        label = BASE_LABELS.get(name, name)
        for a in ALPHAS:
            r = bl[a]
            if name == "always_submit":
                L.append(f"| {label} | {a} | — | {pct(r.get('coverage'))} | {pct(r.get('risk'))} | "
                         f"{r.get('verdict')} |")
            else:
                L.append(f"| {label} | {a} | {tau_s(r.get('tau'))} | "
                         f"{pct(r.get('coverage'))} | {pct(r.get('risk'))} | {r.get('verdict')} |")
    if c.get("f1_sensitivity"):
        L.append("\n**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**\n")
        L.append(f"F1 agreement levels: `{json.dumps(c['f1_sensitivity'].get('agreement_levels'))}`\n")
        L.append("| α | τ | submitted | coverage | risk |")
        L.append("|---|---|---|---|---|")
        for a in ALPHAS:
            r = c["f1_sensitivity"]["alpha"][a]
            L.append(f"| {a} | {tau_s(r.get('tau'))} | {r.get('n_submitted')} | "
                     f"{pct(r.get('coverage'))} | {pct(r.get('risk'))} |")
    if c.get("minus1_sensitivity"):
        L.append("\n**Sensitivity — `resolved=-1` counted as failure, at the primary τ (same rule "
                 "re-scored, different sample pool)**\n")
        L.append("| α | τ | coverage | risk |")
        L.append("|---|---|---|---|")
        for a in ALPHAS:
            r = c["minus1_sensitivity"][a]
            L.append(f"| {a} | {tau_s(r.get('tau'))} | {pct(r.get('coverage'))} | "
                     f"{pct(r.get('risk'))} |")
    ar = alt_rec(tag)
    if ar:
        L.append("\n**Alternative convention (`resolved=-1` as failure) — full certification, "
                 "held-out-repo split**\n")
        L.append(f"own pool: issues {ar.get('units')} · repos {ar.get('repos')} · base error "
                 f"{pct(ar.get('base_error'))} · agreement levels "
                 f"{json.dumps(ar.get('agreement_levels'))}. Its other splits and `always_submit` "
                 f"numbers are in results/kill_test.json.\n")
        L.append("| α | τ | submitted | coverage | risk | 95% CI | verdict |")
        L.append("|---|---|---|---|---|---|---|")
        for a in ALPHAS:
            r = ar["splits"]["heldout_repo"]["alpha"][a]
            L.append(f"| {a} | {tau_s(r.get('tau'))} | {r.get('n_submitted')} | "
                     f"{pct(r.get('coverage'))} | {pct(r.get('risk'))} | {ci(r)} | {r.get('verdict')} |")

# ---------------------------------------------------------------- sanity gate
L.append("\n## Sanity gate (in-distribution split must hold risk ≤ α)\n")
L.append("| config | convention | α | random-issue risk | ≤ α? |")
L.append("|---|---|---|---|---|")
bad = 0
for tag, c in arms():
    if not c:
        continue
    recs = [(c, c.get("convention", "drop"))]
    if alt_rec(tag):
        recs.append((alt_rec(tag), "minus1_failure"))
    for rec, conv in recs:
        for a in ALPHAS:
            r = rec["splits"]["random_issue"]["alpha"][a]
            risk = r.get("risk")
            tau = r.get("tau")
            if risk is None:
                cell_, note = "n/a", "no certified τ"
            else:
                ok = risk <= float(a)
                cell_ = "yes" if ok else "NO"
                note = f"risk ≤ α (τ={tau_s(tau)})" if ok else f"risk > α (τ={tau_s(tau)})"
                if not ok:
                    bad += 1
            L.append(f"| {tag} | {conv} | {a} | {pct(risk)} | {cell_} ({note}) |")
L.append(f"\nFailures: {bad} of the cells that could be checked. Any failure would mark the pipeline "
         f"suspect before held-out verdicts are trusted; cells with no certified τ are untestable, "
         f"not passes.\n")

# ---------------------------------------------------------------- post-hoc descriptive (D5)
try:
    PH = json.loads(Path("results/posthoc_diagnostics.json").read_text())
except FileNotFoundError:
    PH = None
if PH:
    L.append("\n## Post-hoc descriptive diagnostics (DEVIATIONS D5 — no decision uses these)\n")
    L.append("Error rate by agreement level over all units of each config (1 = failed), i.e. what the "
             "rule would see with unlimited calibration data. This is not a pre-registered endpoint.\n")
    L.append("| config | base error | a=1/3 | a=2/3 | a=1 | τ=1 calib error | τ=1 held-out-repo error |")
    L.append("|---|---|---|---|---|---|---|")
    for tag, r in PH.items():
        e = r["error_by_agreement"]

        def cell(k):
            return f"{pct(e[k]['error'])} (n={e[k]['n']})" if k in e else "—"

        L.append(f"| {tag} | {pct(r['base_error'])} | {cell('0.333')} | {cell('0.667')} | {cell('1.0')} | "
                 f"{pct(r['tau1_calib']['error'])} | {pct(r['tau1_heldout_repo']['error'])} |")
    L.append("\n**Conditional check** — within units whose 3 samples contain exactly 2 successes "
             "(`rate=2/3`), does agreement still separate errors? (Direct probe of 'agreement is "
             "difficulty in disguise'.)\n")
    L.append("| config | error at a=1/3 | error at a=2/3 |")
    L.append("|---|---|---|")
    for tag, r in PH.items():
        g = r["grid"]

        def gv(k):
            return f"{pct(g[k]['error'])} (n={g[k]['n']})" if k in g else "—"

        L.append(f"| {tag} | {gv('a=0.333|rate=0.667')} | {gv('a=0.667|rate=0.667')} |")
    L.append("\nNote: this conditional table is confounded with DEVIATIONS D1 — when the labels are "
             "known, the agreeing pair is often the resolved pair, so part of the separation is "
             "mechanical rather than evidence that agreement is independent of difficulty.\n")

# ---------------------------------------------------------------- leak checks
try:
    OV = json.loads(Path("results/overlap_check.json").read_text())
except FileNotFoundError:
    OV = None
if OV:
    L.append("\n## Leak checks (PREREG §8)\n")
    L.append("| check | result | source |")
    L.append("|---|---|---|")
    L.append(f"| duplicate (issue, trajectory) rows, nebius / nvidia | "
             f"{OV['nebius']['dup_instance_trajectoryid']} / {OV['nvidia']['dup_instance_trajectoryid']} | results/overlap_check.json |")
    L.append(f"| duplicate trajectory_id, nebius / nvidia | "
             f"{OV['nebius']['dup_trajectory_id']} / {OV['nvidia']['dup_trajectory_id']} | results/overlap_check.json |")
    L.append(f"| casefolded issue overlap between corpora | {OV['cross_corpus']['intersection']} issues "
             f"({OV['cross_corpus']['nebius_rows_on_shared_issues']} nebius rows / "
             f"{OV['cross_corpus']['nvidia_rows_on_shared_issues']} nvidia rows) — excluded everywhere (D3) | "
             f"results/overlap_check.json |")
    L.append(f"| issue overlap SWE-rebench V1 ∩ V2 (casefolded, same created_at) | "
             f"{OV['swerebench_v1_v2']['intersection_casefold']} | results/overlap_check.json |")
    L.append(f"| excluded shared-issue list | {J['excluded_shared_issues']} keys | results/excluded_shared_issues.csv |")
    L.append("| repo overlap across calibration/evaluation | 0 by construction; asserted for every config/split/convention in "
             "`scripts/kill_test.py::run_config` (`assert_no_repo_leak`) | scripts/kill_test.py |")
    L.append("| issue on both sides of any split | 0; asserted (`assert_single_side`) | scripts/kill_test.py |")
    L.append("| signal never touches labels | the agreement/files signals and both tie-breaks are computed before any "
             "label column is read; `rate_loo` (Part A3) excludes the scored attempt's own label by construction | scripts/kill_test.py::build_units |")
    L.append("")

Path("KILL_TEST.md").write_text("\n".join(L) + "\n")
print("wrote KILL_TEST.md", len(L), "lines")
