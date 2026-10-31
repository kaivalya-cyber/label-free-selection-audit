# Figure alt text

**Figure 1 — Design.** Schematic of the audit: public SWE trajectory corpora feed issue-by-config units with K attempts; labels and five signals feed pre-registered tests; the analysis separates within-issue selection and AUROC from between-issue ICC and certification. Frozen frames, no new outcomes.

**Figure 2 — Selection gap.** Dumbbell chart for 12 arms. For each arm, pass@1 is an open circle, the D1 agreement-selected rate is a blue diamond, and oracle pass@K is an orange triangle. The vertical distance from the selected rate to the oracle is the selection gap. Gaps are labelled in percentage points on the right.

**Figure 3 — Fixed-budget curves.** Line chart of f(k), the D1 resolve rate at budget k, from k=1 to 3 for 11 K=3 arms (grey, with Nebius K=3 in blue) and from k=1 to 8 for the Nebius K=8 arm (orange). The curves are nearly horizontal, with a maximum within-arm range of 1.07 percentage points.

**Figure 4 — ICC forest.** Forest plot of the one-way random-effects ICC(1) of resolved by issue for 12 arms, with 95% repo-clustered bootstrap intervals. Estimates range from 0.646 to 0.864; the Nebius K=8 arm is 0.798.

**Figure 5 — AUROC forest.** Two-panel forest plot of within-issue pairwise AUROC. Left panel uses the judge pair frame: judge 0.579, exit reason 0.558, agreement 0.512, own tests 0.511. Right panel uses the B2 frame: exit reason 0.576, agreement 0.506, own tests 0.513, steps 0.440. A dashed line marks chance at 0.5.

**Figure 6 — Certification.** Grouped stacked bars at alpha 0.05, 0.10, and 0.20 for 11 K=3 configs. Solid bars show how many configs certify; hatched grey bars show the NO-COVERAGE remainder. Agreement certifies 0, 0, and 2 configs; cross-fit difficulty certifies 2, 10, and 11. The separate K=8 arm certifies under cross-fit at all three levels and under agreement at none.
