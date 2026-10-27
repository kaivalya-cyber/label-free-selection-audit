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
        ok = (risk is not None and risk <= float(a))
        if not ok:
            bad += 1
        L.append(f"| {tag} | {a} | {pct(risk)} | {'yes' if ok else 'NO'} |")
L.append(f"\nFailures: {bad}. Any failure would mark the pipeline suspect before held-out verdicts "
         f"are trusted.\n")

Path("KILL_TEST.md").write_text("\n".join(L) + "\n")
print("wrote KILL_TEST.md", len(L), "lines")
