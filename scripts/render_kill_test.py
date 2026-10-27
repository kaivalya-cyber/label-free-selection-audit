"""Render KILL_TEST.md from results/kill_test.json (no computation, pure formatting)."""
import json
from pathlib import Path

J = json.loads(Path("results/kill_test.json").read_text())
ALPHAS = [str(a) for a in J["alphas"]]
L = []


def pct(x, nd=1):
    return "—" if x is None else f"{100 * x:.{nd}f}%"


def ci(rec):
    c = rec.get("ci")
    if not c:
        return "—"
    return f"[{pct(c['lower'])}, {pct(c['upper'])}]"


L.append("# KILL_TEST — pre-registered agreement-based abstention, calibrated → held-out\n")
L.append("Command: `.venv/bin/python scripts/kill_test.py` · raw numbers: "
         "[results/kill_test.json](results/kill_test.json) · rules: [PREREG.md](PREREG.md), "
         "[DEVIATIONS.md](DEVIATIONS.md)\n")

# ---- verdict summary
head = []
for tag, c in list(J["configs"].items()) + [("nebius@K8", J["k8_arm"] or {})]:
    if not c:
        continue
    row = {"config": tag, "units": c.get("units"), "base": pct(c.get("base_error"))}
    for a in ALPHAS:
        r = c.get("splits", {}).get("heldout_repo", {}).get("alpha", {}).get(a, {})
        row[f"a={a}"] = f"{r.get('verdict', '—')} ({pct(r.get('coverage'))}, {pct(r.get('risk'))})"
    head.append(row)
# ---- bottom line computed from the JSON
def cells(alpha, split="heldout_repo"):
    return [(t, c["splits"][split]["alpha"][alpha]) for t, c in
            list(J["configs"].items()) + [("nebius@K8", J["k8_arm"] or {})] if c]


cert = {a: [x for x in cells(a) if x[1].get("verdict") in ("HOLDS", "BREAKS")] for a in ALPHAS}
breaks = [(t, a) for a in ALPHAS for t, r in cells(a) if r.get("verdict") == "BREAKS"]
t1_err = []
for t, c in list(J["configs"].items()):
    lv = c.get("error_by_agreement", {}).get("1.0") if "error_by_agreement" in c else None
    if lv:
        t1_err.append((t, lv["error"], lv["n"]))
L.append("\n## Bottom line\n")
for a in ALPHAS:
    L.append(f"- α={a}: {len(cert[a])}/{len(list(J['configs'])) + (1 if J['k8_arm'] else 0)} configs "
             f"certified a τ; BREAKS verdicts: {sum(1 for t, r in cert[a] if r.get('verdict') == 'BREAKS')}.")
L.append(f"- BREAKS total across every config, split and α: **{len(breaks)}**.")
if cert["0.2"]:
    covs = [r["coverage"] for _, r in cert["0.2"]]
    risks = [r["risk"] for _, r in cert["0.2"]]
    L.append(f"- At α=0.20 the certified cells have coverage {pct(min(covs))}–{pct(max(covs))} and "
             f"held-out-repo risk {pct(min(risks))}–{pct(max(risks))} vs α=20%.")
L.append("- The binding constraint is power, not calibration breakage: exact patch identity is rare "
         "(see DATA_RECON/claims C35–C38), so the unanimous subset is small and its error is only "
         "sometimes low enough for Clopper–Pearson to certify α. `NO-COVERAGE` cells carry no risk "
         "estimate and are reported as such, not as passes.")
L.append("")

L.append("## Verdicts (headline split = held-out-repo, per config)\n")
L.append("| config | issues | base error | " + " | ".join(f"α={a}" for a in ALPHAS) + " |")
L.append("|---|---|---|" + "---|" * len(ALPHAS))
for r in head:
    L.append(f"| {r['config']} | {r['units']} | {r['base']} | " +
             " | ".join(r[f"a={a}"] for a in ALPHAS) + " |")
L.append("\nCells are `VERDICT (coverage, selective risk)`. BREAKS = repo-clustered lower CI bound "
         "> α + 0.05; HOLDS = otherwise; NO-COVERAGE = no τ certified on calibration.\n")

# ---- per config detail
for tag, c in list(J["configs"].items()) + [("nebius@K8", J["k8_arm"] or {})]:
    if not c:
        continue
    L.append(f"\n## {tag}\n")
    L.append(f"`{c.get('display')}` · K={c.get('k')} · issues {c.get('units')} · repos "
             f"{c.get('repos')} · resolved rate {pct(c.get('resolved_rate'))} · agreement levels "
             f"{json.dumps(c.get('agreement_levels'))} · same-cluster label disagreement "
             f"{pct(c.get('same_cluster_disagreement_share'))}\n")
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
            tau = r.get("tau")
            L.append(f"| {a} | {('—' if tau is None else f'{tau:.3f}')} | {r.get('n_submitted')} | "
                     f"{pct(r.get('coverage'))} | {pct(r.get('risk'))} | {ci(r)} | {r.get('verdict')} |")
        if "secondary_files" in sd:
            L.append("\n*secondary signal — files-touched agreement*\n")
            L.append("| α | τ | submitted | coverage | risk | verdict |")
            L.append("|---|---|---|---|---|---|")
            for a in ALPHAS:
                r = sd["secondary_files"][a]
                tau = r.get("tau")
                L.append(f"| {a} | {('—' if tau is None else f'{tau:.3f}')} | {r.get('n_submitted')} | "
                         f"{pct(r.get('coverage'))} | {pct(r.get('risk'))} | {r.get('verdict')} |")
    L.append("\n**Baselines (held-out-repo split, calibrated identically)**\n")
    L.append("| method | α | τ | coverage | risk | verdict |")
    L.append("|---|---|---|---|---|---|")
    for name, bl in c.get("baselines", {}).items():
        for a in ALPHAS:
            r = bl[a]
            if name == "always_submit":
                L.append(f"| {name} | {a} | — | {pct(r.get('coverage'))} | {pct(r.get('risk'))} | "
                         f"{r.get('verdict')} |")
            else:
                tau = r.get("tau")
                L.append(f"| {name} | {a} | {('—' if tau is None else f'{tau:.2f}')} | "
                         f"{pct(r.get('coverage'))} | {pct(r.get('risk'))} | {r.get('verdict')} |")
    if c.get("f1_sensitivity"):
        L.append("\n**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**\n")
        L.append(f"F1 agreement levels: `{json.dumps(c['f1_sensitivity'].get('agreement_levels'))}`\n")
        L.append("| α | τ | submitted | coverage | risk |")
        L.append("|---|---|---|---|---|")
        for a in ALPHAS:
            r = c["f1_sensitivity"]["alpha"][a]
            tau = r.get("tau")
            L.append(f"| {a} | {('—' if tau is None else f'{tau:.3f}')} | {r.get('n_submitted')} | "
                     f"{pct(r.get('coverage'))} | {pct(r.get('risk'))} |")
    if c.get("minus1_sensitivity"):
        L.append("\n**Sensitivity — `resolved=-1` counted as failure, at the primary τ**\n")
        L.append("| α | τ | coverage | risk |")
        L.append("|---|---|---|---|")
        for a in ALPHAS:
            r = c["minus1_sensitivity"][a]
            tau = r.get("tau")
            L.append(f"| {a} | {('—' if tau is None else f'{tau:.3f}')} | {pct(r.get('coverage'))} | "
                     f"{pct(r.get('risk'))} |")

# ---- sanity gate
L.append("\n## Sanity gate (in-distribution split must hold risk ≤ α)\n")
L.append("| config | α | random-issue risk | ≤ α? |")
L.append("|---|---|---|---|")
bad = 0
for tag, c in list(J["configs"].items()) + [("nebius@K8", J["k8_arm"] or {})]:
    if not c:
        continue
    for a in ALPHAS:
        r = c["splits"]["random_issue"]["alpha"][a]
        risk = r.get("risk")
        if risk is None:
            cell, note = "n/a", "no certified τ"
        else:
            ok = risk <= float(a)
            cell = "yes" if ok else "NO"
            note = "risk ≤ α" if ok else "risk > α"
            if not ok:
                bad += 1
        L.append(f"| {tag} | {a} | {pct(risk)} | {cell} ({note}) |")
L.append(f"\nFailures: {bad} of the cells that could be checked. Any failure would mark the pipeline "
         f"suspect before held-out verdicts are trusted; cells with no certified τ are untestable, not "
         f"passes.\n")

# ---- post-hoc descriptive section (DEVIATIONS D5)
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

Path("KILL_TEST.md").write_text("\n".join(L) + "\n")
print("wrote KILL_TEST.md", len(L), "lines")
