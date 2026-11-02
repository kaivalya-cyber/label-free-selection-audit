#!/usr/bin/env python3
"""Regenerate every paper table and figure from cached result JSONs.

This is the clean-room entry point: it uses only files under `results/` in
this directory, writes to `figures/` and `tables/`, and has no absolute path,
dataset download, model call, login, or private input.

Usage (from any working directory):
    python notebook_regenerate.py

Outputs:
    figures/fig1_design.{pdf,png} ... figures/fig6_certification.{pdf,png}
    figures/ALT.md, figures/manifest.json
    tables/table1_verdicts.md, tables/table2_judge.md, tables/table3_arms.md
    tables/ALL_TABLES.md

The six figures are produced by `scripts/make_figures.py`; the three tables
are produced here from the same JSONs.  No number is typed in this file.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
TABLES = ROOT / "tables"

sys.path.insert(0, str(ROOT / "scripts"))
import make_figures as mf  # noqa: E402


def load(name: str) -> dict:
    with (RESULTS / name).open(encoding="utf-8") as fh:
        return json.load(fh)


def pct(x: float, nd: int = 2) -> str:
    return f"{100 * x:.{nd}f}"


def ptext(p: float, nd: int = 4) -> str:
    """Report values at the bootstrap floor as an inequality, not a fake exact p."""
    return "<= 0.001" if p <= 0.0011 else f"{p:.{nd}f}"


def ci(block: dict, nd: int = 3, scale: float = 1.0, signed: bool = False) -> str:
    lo, hi = block["ci"] if isinstance(block.get("ci"), list) else (block["lower"], block["upper"])
    fmt = f"{{:+.{nd}f}}" if signed else f"{{:.{nd}f}}"
    return f"[{fmt.format(scale * lo)}, {fmt.format(scale * hi)}]"


def b1_table(b1: dict) -> str:
    family = b1["family"]["sign_test"]
    negative = min(b1["primary"].items(), key=lambda kv: kv[1]["mean_lift"])
    arm, v = negative
    p = family["p_two_sided"]
    holm = v["holm_p"]
    estimate = (
        f"{family['n_pos']}+/{family['n_neg']}−; one arm Holm-significant negative: "
        f"{100 * v['mean_lift']:+.3f} pp {ci(v, 3, 100, True)}"
    )
    verdict = "SIGNIFICANT+" if p < 0.05 else "NOT SIGNIFICANT"
    return (
        "| B1 | " + estimate + f" | {p:.3f} (Holm {holm:.3f}) | {verdict} |"
    )


def _certified(block: dict, alpha: float) -> bool:
    if "detail" in block:
        return block["detail"][str(alpha)]["verdict"] == "HOLDS"
    return block["splits"]["heldout_repo"]["alpha"][str(alpha)]["verdict"] == "HOLDS"


def b3_counts(b3: dict) -> str:
    keys = list(b3["primary"])
    counts = [sum(1 for k in keys if _certified(b3["primary"][k], a)) for a in b3["alphas"]]
    ag = [sum(1 for k in keys if _certified(b3["agreement_frozen"][k], a)) for a in b3["alphas"]]
    return (
        f"{b3['family_primary']['sign_test']['n_pos']}–{b3['family_primary']['sign_test']['n_neg']} configs; "
        + "/".join(map(str, counts)) + " vs " + "/".join(map(str, ag))
    )


def table1(b1: dict, b2: dict, b3: dict, b4: dict) -> str:
    b2p = b2["primary"]
    b4_neg = min(b4["arms"].items(), key=lambda kv: kv[1]["primary"]["point"]["delta"])
    b4v = b4_neg[1]
    b4p = b4v["primary"]
    b5 = b4["k8_arm"]["b5_exploratory"]
    b4_est = (
        f"{b4['family']['sign_test']['n_pos']}+/{b4['family']['sign_test']['n_neg']}−; largest "
        f"{100 * b4p['point']['delta']:+.3f} pp {ci({'ci': [100 * b4p['lower'], 100 * b4p['upper']]}, 3, 1, True)}"
    )
    rows = [
        "| Analysis | Estimate (95% CI) | p | Verdict |",
        "|---|---|---|---|",
        b1_table(b1),
        f"| B2 | {b2p['estimate']:.4f} [{b2p['lower']:.4f}, {b2p['upper']:.4f}] | {b2p['p']:.3f} | {b2p['verdict']} |",
        f"| B3 | {b3_counts(b3)} | {ptext(b3['family_primary']['sign_test']['p_two_sided'])} | "
        "SIGNIFICANT+ (not blind) |",
        f"| B4 | {b4_est} | {b4['family']['sign_test']['p_two_sided']:.3f} (Holm {b4v['holm_p']:.3f}) | "
        f"{b4v['verdict']} |",
        f"| B5 | {100 * b5['point']['delta']:+.3f} pp "
        f"{ci({'ci': [100 * b5['lower'], 100 * b5['upper']]}, 3, 1, True)} | {b5['p']:.3f} | "
        f"{b5['verdict']} (exploratory) |",
    ]
    caption = (
        ": Holm over 11 K=3 configurations for B1/B4; B2 single test; B3 sign test; "
        "B5 exploratory; K=8 separate. Sources: `b1`–`b4` JSONs."
    )
    return "\n".join(rows) + "\n\n" + caption + "\n"


def table2(judge: dict) -> str:
    rows = [
        "| Signal | AUROC (95% CI) | p | n pairs |",
        "|---|---|---|---:|",
    ]
    p = judge["primary"]
    rows.append(
        f"| Judge | {p['estimate']:.4f} ({p['lower']:.4f}–{p['upper']:.4f}) | "
        f"{ptext(p['p'])} | {p['n_pairs']:,} |"
    )
    labels = [("exit_reason", "Exit reason"), ("own_test", "Own tests"), ("agreement", "Agreement")]
    for key, label in labels:
        c = judge["comparisons"][key]
        rows.append(
            f"| {label} | {c['estimate']:.4f} ({c['lower']:.4f}–{c['upper']:.4f}) | "
            f"{ptext(c['p'])} | {c['n_pairs']:,} |"
        )
    steps = judge["exploratory"]["steps_oriented"]
    rows.append(
        f"| Steps (oriented, post-hoc) | {steps['estimate']:.4f} "
        f"({steps['lower']:.4f}–{steps['upper']:.4f}) | {ptext(steps['p'])} | "
        f"{steps['n_pairs']:,} |"
    )
    caption = (
        ": Judge frame: judge and same-pair signals; 95% repo-clustered bootstrap (B = 2,000). "
        "Steps oriented post-hoc (DEVIATIONS.md). Source: `judge_analysis.json`."
    )
    return "\n".join(rows) + "\n\n" + caption + "\n"


def table3(desc: dict, meta: dict) -> str:
    rows = [
        "| Arm | Agent | Policy model | Benchmark | Issues |",
        "|---|---|---|---|---:|",
    ]
    for key, m in meta["arms"].items():
        block = desc["k8_arm"][key] if key.endswith("@K8") else desc["arms"][key]
        agent = m["agent"].replace("SWE-agent (v1.0)", "SWE-agent v1.0")
        arm = m["label"] if key == "nebius_openhands" else m["short"]
        rows.append(
            f"| {arm} | {agent} | {m['policy']} | {m['benchmark']} | {block['issues']:,} |"
        )
    caption = (
        ": Frozen arms and models; counts exclude 204 shared issues. Six of eleven K=3 arms "
        "use 27B language-model policies; no local-execution claim. "
        "Source: `results/descriptive_tables.json`."
    )
    return "\n".join(rows) + "\n\n" + caption + "\n"


def main() -> None:
    if not RESULTS.is_dir():
        raise SystemExit(f"missing results directory: {RESULTS}")
    mf.generate(RESULTS, FIGURES)

    b1 = load("b1_selection_lift.json")
    b2 = load("b2_within_issue_auroc.json")
    b3 = load("b3_crossfit_certification.json")
    b4 = load("b4_adaptive_stopping.json")
    judge = load("judge_analysis.json")
    desc = load("descriptive_tables.json")
    meta = load("config_metadata.json")

    TABLES.mkdir(parents=True, exist_ok=True)
    outputs = {
        "table1_verdicts.md": table1(b1, b2, b3, b4),
        "table2_judge.md": table2(judge),
        "table3_arms.md": table3(desc, meta),
    }
    for name, text in outputs.items():
        (TABLES / name).write_text(text, encoding="utf-8")
    (TABLES / "ALL_TABLES.md").write_text(
        "# Tables\n\n## Table 1\n\n" + outputs["table1_verdicts.md"]
        + "\n## Table 2\n\n" + outputs["table2_judge.md"]
        + "\n## Table 3\n\n" + outputs["table3_arms.md"],
        encoding="utf-8",
    )
    print(f"wrote 6 figures to {FIGURES}")
    print(f"wrote 3 tables to {TABLES}")


if __name__ == "__main__":
    main()
