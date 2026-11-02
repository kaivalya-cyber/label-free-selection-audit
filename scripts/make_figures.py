#!/usr/bin/env python3
"""Generate every paper figure from the cached result JSONs.

The script reads only:
  results/descriptive_tables.json
  results/b2_within_issue_auroc.json
  results/b3_crossfit_certification.json
  results/judge_analysis.json
  results/config_metadata.json

It writes vector PDFs and 300-dpi PNGs to figures/ (or --out-dir).
No dataset download, model call, login, or private path is used.

Usage:
  python scripts/make_figures.py
  python scripts/make_figures.py --results-dir results --out-dir figures
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch

# Okabe-Ito, colour-blind safe. The same colour always means the same signal.
C = {
    "pass": "#6B7280",
    "selected": "#0072B2",
    "oracle": "#D55E00",
    "judge": "#0072B2",
    "exit": "#E69F00",
    "agreement": "#009E73",
    "own": "#CC79A7",
    "steps": "#5F5F5F",
    "crossfit": "#0072B2",
    "grey": "#BDBDBD",
    "ink": "#1A1A1A",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8.5,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "legend.fontsize": 7,
    "axes.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "savefig.dpi": 300,
    "figure.dpi": 150,
})


def load(results_dir: Path, name: str):
    with open(results_dir / name, encoding="utf-8") as f:
        return json.load(f)


def save(fig, out_dir: Path, stem: str, manifest: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        path = out_dir / f"{stem}.{ext}"
        fig.savefig(path, bbox_inches="tight", facecolor="white")
        manifest[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    plt.close(fig)


def draw_box(ax, xy, width, height, title, body, color):
    box = FancyBboxPatch(
        xy, width, height,
        boxstyle="round,pad=0.010,rounding_size=0.012",
        linewidth=0.8, edgecolor=color, facecolor="white", zorder=2,
    )
    ax.add_patch(box)
    ax.text(xy[0] + 0.010, xy[1] + height - 0.032, title,
            ha="left", va="top", fontsize=7.6, fontweight="bold", color=color, zorder=3)
    ax.text(xy[0] + 0.010, xy[1] + height - 0.080, body,
            ha="left", va="top", fontsize=5.55, color=C["ink"], linespacing=1.18, zorder=3)


def fig_design(out_dir: Path, manifest: dict) -> None:
    fig, ax = plt.subplots(figsize=(7.3, 2.75))
    ax.set_xlim(-0.012, 0.968)
    ax.set_ylim(-0.01, 1.01)
    ax.axis("off")

    width, step, left = 0.164, 0.196, 0.005
    boxes = [
        (left, "Data", "public SWE\ntrajectories\nNebius + NVIDIA", C["ink"]),
        (left + step, "Issue units", "issue × config\nK attempts", C["judge"]),
        (left + 2 * step, "Signals", "labels, agreement\nown tests, exit\nsteps, judge", C["agreement"]),
        (left + 3 * step, "Frozen tests", "B1–B5\nB2 AUROC\nkill test\nB3 cross-fit", C["oracle"]),
        (left + 4 * step, "Decomposition", "within issue:\nselection / AUROC\nbetween issue:\nICC / certification", C["exit"]),
    ]
    for x, title, body, color in boxes:
        draw_box(ax, (x, 0.40), width, 0.36, title, body, color)
    for x in (left, left + step, left + 2 * step, left + 3 * step):
        ax.add_patch(FancyArrowPatch(
            (x + width + 0.002, 0.58), (x + step - 0.002, 0.58),
            arrowstyle="-|>", mutation_scale=7.0, linewidth=0.9,
            shrinkA=0, shrinkB=0, color=C["ink"], zorder=4,
        ))
    ax.text(0.5, 0.93, "Frozen frames, pre-registered rules, no new outcomes",
            ha="center", va="center", fontsize=9, fontweight="bold", color=C["ink"])
    ax.text(0.5, 0.18,
            "Every estimate resamples whole repositories; arms are never pooled.",
            ha="center", va="center", fontsize=7.2, color=C["steps"])
    ax.text(0.5, 0.09,
            "The audit separates what a signal can rank inside an issue from what issue difficulty explains between issues.",
            ha="center", va="center", fontsize=6.8, color=C["ink"])
    save(fig, out_dir, "fig1_design", manifest)


def fig_selection_gap(desc: dict, meta: dict, out_dir: Path, manifest: dict) -> None:
    order = list(desc["arms"]) + list(desc["k8_arm"])
    rows = []
    for key in order:
        v = desc["arms"].get(key, desc["k8_arm"].get(key))
        rows.append({
            "key": key,
            "label": meta["arms"][key]["short"],
            "pass": 100 * v["pass_at_1"],
            "selected": 100 * v["selected_d1"],
            "oracle": 100 * v["oracle_pass_at_k"],
            "gap": 100 * v["selection_gap_d1"],
        })

    fig, ax = plt.subplots(figsize=(6.9, 4.15))
    ys = list(range(len(rows)))[::-1]
    for y, r in zip(ys, rows):
        ax.plot([r["pass"], r["oracle"]], [y, y], color=C["grey"], linewidth=1.4, zorder=1)
        ax.plot(r["pass"], y, marker="o", markersize=4.2, markerfacecolor="white",
                markeredgecolor=C["pass"], markeredgewidth=1.0, zorder=3)
        ax.plot(r["selected"], y, marker="D", markersize=4.0, color=C["selected"], zorder=4)
        ax.plot(r["oracle"], y, marker="^", markersize=5.0, color=C["oracle"], zorder=4)
        ax.text(66.3, y, f"+{r['gap']:.1f}", ha="left", va="center",
                fontsize=7, color=C["ink"])

    ax.axhline(0.5, color=C["ink"], linewidth=0.5, linestyle=(0, (2, 4)))
    ax.set_yticks(ys)
    ax.set_yticklabels([r["label"] for r in rows])
    ax.set_xlim(29, 70.5)
    ax.set_xlabel("Resolve rate (%)")
    ax.set_title("Selected, single-sample, and oracle resolve rates", loc="left", fontweight="bold")
    ax.text(66.3, len(rows) - 0.25, "gap", ha="left", va="bottom", fontsize=7, color=C["steps"])
    ax.grid(axis="x", color="#E8E8E8", linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(
        handles=[
            plt.Line2D([], [], marker="o", linestyle="none", markerfacecolor="white",
                       markeredgecolor=C["pass"], label="pass@1"),
            plt.Line2D([], [], marker="D", linestyle="none", color=C["selected"],
                       label="agreement-selected (plurality)"),
            plt.Line2D([], [], marker="^", linestyle="none", color=C["oracle"],
                       label="oracle pass@K"),
        ],
        loc="lower right", frameon=False, ncol=3, bbox_to_anchor=(1.0, -0.23),
        handletextpad=0.2, columnspacing=1.1,
    )
    fig.subplots_adjust(left=0.28, right=0.91, top=0.91, bottom=0.22)
    save(fig, out_dir, "fig2_selection_gap", manifest)


def fig_curves(desc: dict, meta: dict, out_dir: Path, manifest: dict) -> None:
    fig, ax = plt.subplots(figsize=(6.7, 3.15))
    for key, curve in desc["curves"].items():
        xs = sorted(int(k) for k in curve)
        ys = [100 * curve[str(k)] for k in xs]
        if key == "nebius_openhands@K8":
            ax.plot(xs, ys, color=C["oracle"], linewidth=2.0, marker="o", markersize=3.0,
                    zorder=4, label="Nebius K=8")
        elif key == "nebius_openhands":
            ax.plot(xs, ys, color=C["judge"], linewidth=2.0, marker="o", markersize=3.0,
                    zorder=3, label="Nebius K=3")
        else:
            ax.plot(xs, ys, color=C["grey"], linewidth=0.9, alpha=0.9, zorder=1)

    ax.set_xlim(0.8, 8.2)
    ax.set_xticks(range(1, 9))
    ax.set_xlabel("Attempts drawn, k")
    ax.set_ylabel("f(k): plurality-cluster resolve rate (%)")
    ax.set_ylim(31.5, 60.5)
    ax.grid(axis="y", color="#E8E8E8", linewidth=0.5)
    ax.set_axisbelow(True)
    ax.set_title("The fixed-budget curve is flat in every arm", loc="left", fontweight="bold")
    ax.text(1.0, 58.7, "grey: 11 K=3 arms (curves end at k=3)", fontsize=6.8, color=C["steps"])
    ax.text(1.0, 57.1, "maximum within-arm range: 1.07 pp", fontsize=6.8, color=C["steps"])
    ax.legend(loc="lower right", frameon=False, ncol=2, handlelength=1.6)
    fig.subplots_adjust(left=0.13, right=0.98, top=0.90, bottom=0.20)
    save(fig, out_dir, "fig3_fixed_budget", manifest)


def fig_icc(desc: dict, meta: dict, out_dir: Path, manifest: dict) -> None:
    order = list(desc["arms"]) + list(desc["k8_arm"])
    rows = []
    for key in order:
        v = desc["arms"].get(key, desc["k8_arm"].get(key))
        rows.append((key, v["icc"]["estimate"], v["icc"]["lower"], v["icc"]["upper"]))

    fig, ax = plt.subplots(figsize=(6.7, 3.75))
    ys = list(range(len(rows)))[::-1]
    for y, (_, est, lo, hi) in zip(ys, rows):
        ax.plot([lo, hi], [y, y], color=C["judge"], linewidth=1.2, solid_capstyle="round")
        ax.plot(est, y, marker="o", markersize=4.5, color=C["judge"], zorder=3)
    ax.set_yticks(ys)
    ax.set_yticklabels([meta["arms"][k]["short"] for k, *_ in rows])
    ax.set_xlim(0.60, 0.89)
    ax.set_xlabel("ICC(1) of resolved by issue")
    ax.set_title("Most label variance is between issues, not within", loc="left", fontweight="bold")
    ax.grid(axis="x", color="#E8E8E8", linewidth=0.5)
    ax.set_axisbelow(True)
    fig.subplots_adjust(left=0.25, right=0.98, top=0.91, bottom=0.20)
    save(fig, out_dir, "fig4_icc", manifest)


def fig_auroc(judge: dict, b2: dict, out_dir: Path, manifest: dict) -> None:
    left = [
        ("Judge", judge["primary"], C["judge"], judge["primary"]["n_pairs"]),
        ("Exit reason", judge["comparisons"]["exit_reason"], C["exit"],
         judge["comparisons"]["exit_reason"]["n_pairs"]),
        ("Steps (oriented)", judge["exploratory"]["steps_oriented"], C["steps"],
         judge["exploratory"]["steps_oriented"]["n_pairs"]),
        ("Agreement", judge["comparisons"]["agreement"], C["agreement"],
         judge["comparisons"]["agreement"]["n_pairs"]),
        ("Own tests", judge["comparisons"]["own_test"], C["own"],
         judge["comparisons"]["own_test"]["n_pairs"]),
    ]
    raw_steps = b2["comparisons"]["steps"]
    steps = dict(raw_steps)
    steps.update({"estimate": 1 - raw_steps["estimate"],
                  "lower": 1 - raw_steps["upper"],
                  "upper": 1 - raw_steps["lower"]})
    right = [
        ("Exit reason", b2["comparisons"]["exit_reason"], C["exit"],
         b2["comparisons"]["exit_reason"]["n_pairs"]),
        ("Steps (oriented)", steps, C["steps"], steps["n_pairs"]),
        ("Agreement", b2["comparisons"]["agreement"], C["agreement"],
         b2["comparisons"]["agreement"]["n_pairs"]),
        ("Own tests", b2["primary"], C["own"], b2["primary"]["n_pairs"]),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(7.3, 3.45), sharex=True)
    for ax, rows, title in zip(axes, (left, right), ("Judge frame", "B2 frame")):
        ys = list(range(len(rows)))[::-1]
        for y, (name, v, color, n) in zip(ys, rows):
            xerr = [[v["estimate"] - v["lower"]], [v["upper"] - v["estimate"]]]
            ax.errorbar(v["estimate"], y, xerr=xerr, fmt="o", markersize=4.6,
                        color=color, ecolor=color, elinewidth=1.1, capsize=2.0, zorder=3)
        ax.axvline(0.5, color=C["ink"], linewidth=0.6, linestyle=(0, (2, 4)))
        ax.set_xlim(0.405, 0.607)
        ax.set_ylim(-0.6, len(rows) - 0.4)
        ax.set_yticks(ys)
        ax.set_yticklabels([f"{r[0]}\n({r[3]:,} pairs)" for r in rows], fontsize=6.6)
        ax.set_title(f"{title}", loc="left", fontweight="bold")
        ax.grid(axis="x", color="#E8E8E8", linewidth=0.5)
        ax.set_axisbelow(True)
    axes[0].set_xlabel("Within-issue pairwise AUROC")
    axes[1].set_xlabel("Within-issue pairwise AUROC")
    axes[0].text(0.502, -0.45, "chance", fontsize=6.4, color=C["steps"])
    fig.suptitle("Cheap signals are weak (AUROC 0.51–0.58); the judge is modestly better",
                 x=0.02, ha="left", fontsize=8.5, fontweight="bold")
    fig.subplots_adjust(left=0.15, right=0.985, top=0.84, bottom=0.20, wspace=0.80)
    save(fig, out_dir, "fig5_auroc", manifest)


def fig_certification(b3: dict, out_dir: Path, manifest: dict) -> None:
    alphas = b3["alphas"]
    keys = list(b3["primary"])

    def cert(block, key, alpha):
        detail = block[key]["detail"][str(alpha)] if "detail" in block[key] else None
        if detail is not None:
            return detail.get("verdict") == "HOLDS"
        return block[key]["splits"]["heldout_repo"]["alpha"][str(alpha)].get("certified", False)

    agreement = [sum(cert(b3["agreement_frozen"], k, a) for k in keys) for a in alphas]
    crossfit = [sum(cert(b3["primary"], k, a) for k in keys) for a in alphas]
    x = list(range(len(alphas)))
    w = 0.33

    fig, ax = plt.subplots(figsize=(5.5, 3.0))
    for i, (vals, color, label) in enumerate([
        (agreement, C["agreement"], "Agreement"),
        (crossfit, C["crossfit"], "Cross-fit difficulty"),
    ]):
        offset = -w / 2 if i == 0 else w / 2
        bars = ax.bar([xx + offset for xx in x], vals, width=w, color=color,
                      edgecolor="white", linewidth=0.5, zorder=2)
        rest = [11 - v for v in vals]
        ax.bar([xx + offset for xx in x], rest, width=w, bottom=vals,
               color="#E6E6E6", edgecolor="white", linewidth=0.5, hatch="///", zorder=1)
        for xx, v, r in zip(x, vals, rest):
            ax.text(xx + offset, max(v / 2, 0.28), str(v), ha="center", va="center",
                    fontsize=7.2, color="white" if v >= 2 else color, fontweight="bold")
            if r:
                ax.text(xx + offset, v + r / 2, str(r), ha="center", va="center",
                        fontsize=6.8, color=C["steps"])

    ax.set_xticks(x)
    ax.set_xticklabels([f"alpha = {a:.2f}" for a in alphas])
    ax.set_ylim(0, 13.0)
    ax.set_yticks(range(0, 12, 2))
    ax.set_ylabel("K=3 configs (of 11)")
    ax.set_title("Certification counts, held-out-repo split", loc="left", fontweight="bold")
    ax.grid(axis="y", color="#E8E8E8", linewidth=0.5)
    ax.set_axisbelow(True)
    ax.legend(
        handles=[Patch(facecolor=C["agreement"], label="Agreement, certifying"),
                 Patch(facecolor=C["crossfit"], label="Cross-fit, certifying"),
                 Patch(facecolor="#E6E6E6", hatch="///", label="NO-COVERAGE")],
        loc="upper left", frameon=False, ncol=3, fontsize=6.2, handlelength=1.3,
        columnspacing=0.9, bbox_to_anchor=(0.0, 1.02),
    )
    k8_cross = b3["k8_arm"]["count"]
    k8_agree = b3["k8_arm"]["agreement_count"]
    ax.text(1.0, -2.55,
            f"K=8 arm (separate): cross-fit certifies at {k8_cross}/3 alpha levels; "
            f"agreement at {k8_agree}/3.",
            ha="center", va="top", fontsize=6.2, color=C["steps"], transform=ax.transData)
    fig.subplots_adjust(left=0.13, right=0.98, top=0.84, bottom=0.24)
    save(fig, out_dir, "fig6_certification", manifest)


def write_alt(out_dir: Path) -> None:
    text = """# Figure alt text

**Figure 1 — Design.** Schematic of the audit: public SWE trajectory corpora feed issue-by-config units with K attempts; labels and five signals feed pre-registered tests; the analysis separates within-issue selection and AUROC from between-issue ICC and certification. Frozen frames, no new outcomes.

**Figure 2 — Selection gap.** Dumbbell chart for 12 arms. For each arm, pass@1 is an open circle, the plurality-cluster agreement-selected rate is a blue diamond, and oracle pass@K is an orange triangle. The vertical distance from the selected rate to the oracle is the selection gap. Gaps are labelled in percentage points on the right.

**Figure 3 — Fixed-budget curves.** Line chart of f(k), the D1 resolve rate at budget k, from k=1 to 3 for 11 K=3 arms (grey, with Nebius K=3 in blue) and from k=1 to 8 for the Nebius K=8 arm (orange). The curves are nearly horizontal, with a maximum within-arm range of 1.07 percentage points.

**Figure 4 — ICC forest.** Forest plot of the one-way random-effects ICC(1) of resolved by issue for 12 arms, with 95% repo-clustered bootstrap intervals. Estimates range from 0.646 to 0.864; the Nebius K=8 arm is 0.798.

**Figure 5 — AUROC forest.** Two-panel forest plot of within-issue pairwise AUROC. Left panel uses the judge pair frame: judge 0.579, exit reason 0.558, steps oriented so fewer is better 0.548 (raw 0.452), agreement 0.512, own tests 0.511. Right panel uses the B2 frame: exit reason 0.576, steps oriented so fewer is better 0.560 (raw 0.440), own tests 0.513, agreement 0.506. A dashed line marks chance at 0.5.

**Figure 6 — Certification.** Grouped stacked bars at alpha 0.05, 0.10, and 0.20 for 11 K=3 configs. Solid bars show how many configs certify; hatched grey bars show the NO-COVERAGE remainder. Agreement certifies 0, 0, and 2 configs; cross-fit difficulty certifies 2, 10, and 11. The separate K=8 arm certifies under cross-fit at all three levels and under agreement at none.
"""
    (out_dir / "ALT.md").write_text(text, encoding="utf-8")


def generate(results_dir: Path, out_dir: Path) -> dict[str, str]:
    """Write all six figures plus ALT.md and manifest.json; return the manifest."""
    desc = load(results_dir, "descriptive_tables.json")
    b2 = load(results_dir, "b2_within_issue_auroc.json")
    b3 = load(results_dir, "b3_crossfit_certification.json")
    judge = load(results_dir, "judge_analysis.json")
    meta = load(results_dir, "config_metadata.json")

    out_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, str] = {}
    fig_design(out_dir, manifest)
    fig_selection_gap(desc, meta, out_dir, manifest)
    fig_curves(desc, meta, out_dir, manifest)
    fig_icc(desc, meta, out_dir, manifest)
    fig_auroc(judge, b2, out_dir, manifest)
    fig_certification(b3, out_dir, manifest)
    write_alt(out_dir)

    for name in ("descriptive_tables.json", "b2_within_issue_auroc.json",
                 "b3_crossfit_certification.json", "judge_analysis.json",
                 "config_metadata.json"):
        manifest[f"source:{name}"] = hashlib.sha256(
            (results_dir / name).read_bytes()).hexdigest()
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--out-dir", type=Path, default=Path("figures"))
    args = parser.parse_args()
    generate(args.results_dir, args.out_dir)
    print(f"wrote 6 figures, ALT.md, manifest.json to {args.out_dir}")


if __name__ == "__main__":
    main()
