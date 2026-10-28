# PREREG-2 — four pre-registered analyses on the frozen frames

Status: **frozen at commit `f9558d9`** (the commit that adds this file; any later change is a
`DEVIATIONS.md` entry). At freeze time **none of B1–B4 has been computed**. The only numbers produced before this file are (a) the Part-A reporting fixes
([DEVIATIONS.md](DEVIATIONS.md) D6/D7), which change how `KILL_TEST.md` reports the *already-run*
endpoint and touch no primary number, and (b) a **label-blind** availability probe
([scripts/b4_cost_probe.py](scripts/b4_cost_probe.py) → [results/b4_cost_probe.json](results/b4_cost_probe.json))
that reads canonical patch forms and signal-presence counts only — no signal-vs-outcome association.

This file does **not** modify PREREG.md. The primary endpoint, its frame, its τ grids, δ, the
Clopper–Pearson/LTT calibration, the splits, the BREAKS rule and the kill-test numbers stand as
reported in [KILL_TEST.md](KILL_TEST.md). B1–B4 are four further pre-registered analyses on the same
frozen frames; nothing here may be used to re-choose the primary endpoint.

## 1. Frames, arms, exclusions (unchanged from PREREG §§1, 4, 8)

- **Arms (12).** The 11 frozen configs at **K=3** — `nebius_openhands` plus the 10 nvidia configs
  listed in [src/configs.py](src/configs.py) — and **`nebius_openhands` at K=8**. Arms are analysed
  alone: **no pooling across configs in any number.**
- **Eligible issues** per arm = the frozen frame of that arm: issues with ≥ K attempts after the
  given label convention is applied, with the **204 cross-corpus shared issues excluded**
  ([results/excluded_shared_issues.csv](results/excluded_shared_issues.csv), DEVIATIONS D3). This
  exclusion applies everywhere in B1–B4.
- **Sampling.** The frozen deterministic subsample of PREREG §1 (`seeded_rng(tag, key)` →
  `rng.choice(sorted(trajectory_ids), size=K, replace=False)`) is reused verbatim. B1, B3 and B4 operate
  on exactly those sampled attempts, so their frames are identical to the kill test's.
  `seeded_rng(*parts) = numpy.random.default_rng(int(sha256("|".join(parts)).hexdigest()[:16], 16))`
  ([src/risk.py](src/risk.py)).
- **Splits** for B3 are the frozen ones (`random_by_issue`, `heldout_repo`, `temporal`); the headline
  is `heldout_repo` as in PREREG §4. B1, B2 and B4 are split-free (they use every eligible issue, with
  the repo-clustered bootstrap absorbing repo dependence).
- **Labels** are as published; no harness was re-run (WEAKNESSES #1).
- **Cost:** free compute only; `COST_LOG.md` stays $0.

## 2. Label conventions

`resolved = -1` exists only in the nvidia corpus (0–25.8% of rows by config); nebius has none.

- **Primary frame for B1, B4 and B3's reference numbers:** PREREG's original convention — `-1` rows
  dropped before sampling (the kill-test frame).
- **Declared sensitivity:** the alternative convention of DEVIATIONS D6 — `resolved = -1` scored as
  failure (which also enlarges the pool). For B1 and B4 every reported quantity is computed on both
  frames; the alternative-frame numbers are reported next to the primary ones and are **not** in the
  Holm families (§7).
- **B3** runs the full certification machinery under **both** conventions and reports both count
  vectors.
- **B2** is nebius-only, where the convention question does not arise.

## 3. B1 — selection lift

**Question:** in deployment you submit one attempt; does submitting the attempt that agrees with its
siblings beat submitting one at random?

Frozen procedure, per arm, per issue `x` with its K sampled attempts:

1. Group the sampled attempts by **exact canonical patch equality** (PREREG §2.1 normalizer, strict).
2. `top =` the largest cluster size. Let `C` = the clusters of size `top`, ordered by their canonical
   string (lexicographic). Cluster choice: `idx = seeded_rng("select", ktag, key).integers(len(C))`
   where `ktag = f"{tag}@K{k}"`. **The tie-break never reads a label or a signal column** — cluster
   counts and canonical strings only.
3. Representative = the member of the chosen cluster with the **smallest `trajectory_id`**.
   `selected(x) = resolved` of that representative.
4. `random-K(x) = (1/K)·Σ resolved` over the K sampled attempts — the exact expectation of a uniform
   one-of-K draw (no simulation needed).
5. `oracle-K(x) = 1[at least one of the K sampled attempts resolved]` — pass@K on the sample. Ceiling
   only: it requires the labels of all K attempts.

**Per-issue contrast:** `lift(x) = selected(x) − random-K(x)`; **primary quantity per arm** =
mean of `lift(x)` over all eligible issues (equivalently `mean(selected) − mean(random-K)`).

**Inference.** Repo-clustered paired bootstrap: resample repos with replacement (`B = 2000`, seed
`seeded_rng("boot2", ktag, "lift")`), pool their issues' `lift(x)`, take the mean; 95% CI =
2.5th–97.5th percentiles; two-sided bootstrap p-value
`p = min(1, 2 · min((1+#{e* ≤ 0})/(B+1), (1+#{e* ≥ 0})/(B+1)))`.

**Secondary (descriptive, no Holm):** the same three resolve rates and the same lift restricted to
**mixed-label issues** (≥1 resolved and ≥1 unresolved among the K sampled known labels); mean largest
cluster size; share of issues where the selected attempt is uniquely determined (no tie).

**"No effect":** the 95% CI of the lift contains 0. Negative direction is reported as such.

## 4. B2 — execution-grounded signals (nebius @ K=8 only)

**Fields, verified before this file** (dataset card *nebius/SWE-rebench-openhands-trajectories*,
Table 2; raw card: `https://huggingface.co/datasets/nebius/SWE-rebench-openhands-trajectories/raw/main/README.md`):

| column in the parquet | card name | card description | observed values |
|---|---|---|---|
| `pred_passes_gen_tests` | `pred_passes_gen_test` | "Number of agent-generated tests passed by the agent's own solution (`model_patch`)" — *evaluates predicted solution correctness against the agent's own tests* | `1` = 22,641; `0` = 8,748; sentinel `-999` (read as null) = 35,685 (53.2%) |
| `gen_tests_correct` | `gen_tests_correct` | "Number of agent-generated tests that correctly validate the solution (fail before applying the **golden patch**, pass after)" | `1` = 9,451; `0` = 22,002; sentinel `-999` = 35,621 (53.1%) |

Two facts that decide the design, both verified locally and in the card text:

1. **The stored values are binary 0/1**, not counts, despite the card's wording; `-999` means "no tests
   were generated". So the signal is "the agent's own generated test(s) pass on its own patch"
   (1/0), not a fraction of tests. We pre-register it as a **binary per-attempt signal**.
2. **`gen_tests_correct` is not deployable**: it is defined with the **golden patch**, i.e. it uses
   evaluation-time information no agent has. It is reported only as a labelled
   **EXPLORATORY** row, never as a primary.

Missingness is **not at random**: null share is 56.9% among `submit` rows but 15.4% among max-iteration
rows. Consequences are reported, not corrected.

**Pairs.** Restrict to the frozen nebius@K8 frame. A **pair** is an unordered pair of the issue's K=8
sampled attempts with **different** known labels and **both** signals non-null; the resolved attempt is
the positive. Mixed-label issues only, by construction of "different labels". Availability, measured
label-conditioned but with no association computed (results/b4_cost_probe.json):

| quantity | value |
|---|---|
| issues in the frame | 4,580 |
| mixed-label issues (≥1 resolved, ≥1 unresolved) | 1,338 |
| mixed issues with ≥1 eligible pair | 943 |
| eligible pairs (both signals non-null) | 11,611 |
| attempts / attempts with non-null own-test signal | 55,368 / 25,760 (46.5%) |

**Primary quantity per arm (one arm):** the **within-issue pairwise AUROC** of
`pred_passes_gen_tests` on that pair set, ties (equal signals) counted 0.5. Because both members come
from the same issue, issue difficulty cancels by construction; the statistic is not the same object as
the kill test's unit-level selective risk and is never compared with it numerically.

**Comparison signals, same pair set:** (i) per-attempt agreement = (size of the canonical cluster
containing the attempt, within the K=8 sample)/8; (ii) per-attempt step count = assistant-message
count of that trajectory. Reported as AUROCs, and as **paired differences** against the own-test
AUROC (same resampled pairs).
**EXPLORATORY:** the AUROC of `gen_tests_correct`, labelled as gold-patch-dependent.

**Secondary (report-only): selection lift** of (a) "pick the attempt with the highest own-test
signal" (an attempt with a null signal scores −1, i.e. below any attempt with tests; if all attempts
are null the pick is a seeded uniform draw) and (b) the combination "largest cluster first, then
highest own-test signal" (scores sorted lexicographically `(cluster_size, test)`; ties broken by
`seeded_rng("selectb2", ktag, key).integers(#{tied})` over the tied attempts sorted by
`trajectory_id`). Both against `random-K` (exact expectation, §3) and against the agreement-only rule.

**Inference.** Repo-clustered bootstrap over the pair set: resample repos with replacement, pool their
pairs, recompute (seed `seeded_rng("boot2", ktag, "auroc", signal)`, `B = 2000`); CI and the same
two-sided p formula, centred on 0.5 for AUROC.

**"No effect":** the 95% CI of the own-test AUROC contains 0.5.

## 5. B3 — cross-fit difficulty certification

**Signal:** `rate_loo(x) = (Σ_{i=1..K} resolved_i − resolved_rep) / (K − 1)` — the issue's resolve rate
estimated from the **other K−1** sampled attempts, so the estimate never contains the label
(`resolved_rep`) it is used to score. (At K=3 this takes values {0, ½, 1}; at K=8, {0, 1/7, …, 1}.
The τ grid stays exactly PREREG §3's — {1, 2/3, 1/3} and {1, 7/8, 6/8, 4/8, 1/8} — so the
fixed-sequence procedure, not a new grid, handles the coarser levels.)

**Machinery:** identical to the kill test — same splits, same LTT/CP calibration (`δ = 0.05`,
`n_min = 30`), same α ∈ {0.05, 0.10, 0.20}, same repo-clustered bootstrap and BREAKS rule. Output =
per arm and α: τ, coverage, risk, CI, verdict; both label conventions (§2).

**Primary quantity per arm:** the **certification count** = number of α levels (out of 3) at which the
cross-fit signal certifies a τ on the calibration split of the headline (`heldout_repo`) split. The
agreement counts are the frozen kill-test numbers; both are listed side by side with the count
difference.

**Inference.** A count is not a bootstrap estimand and has no per-config p-value, so **Holm does not
apply to B3**; the single pre-registered family test is the **two-sided exact sign test** on the sign
of (count_cross-fit − count_agreement) over the 11 configs (ties excluded), §7. Any per-config
"significant" statement for B3 is **EXPLORATORY**.

**"No effect":** the sign test is not significant at 0.05 (two-sided). An effect in the *negative*
direction (cross-fit certifies fewer α than agreement) is reported as such and is not spun as support
for agreement.

**Disclosure.** The Part-A instruction ordered this replacement before PREREG-2 existed, so the number
has already been produced by `scripts/kill_test.py` (`baselines.difficulty_cross_fit`, DEVIATIONS D7).
The Part-C run re-executes the identical deterministic code path; B3 is reported from that run, and
any discrepancy between the two would be a reproducibility failure to report, not to reconcile.

## 6. B4 — adaptive stopping

**Deployment story:** attempts arrive one at a time; stop as soon as the evidence looks strong; do not
pay for the rest.

**Rule (primary, literal reading of the brief).** Draw order for issue `x` = the frozen K sampled
attempts permuted by `seeded_rng("seq", ktag, key).permutation(K)` applied to the attempts sorted by
`trajectory_id` (label-blind). **`seq_first2`:** after 2 draws, stop iff the two canonical patch forms
are identical; otherwise continue to `K_max`, where **`K_max = K` for that arm** (3 for every K=3 arm,
including `nebius_openhands`, and 8 for the nebius K=8 arm).
**Declared variant, also reported: `seq_any1st`** — stop as soon as any two drawn patches are
identical (first repeat), else continue to `K_max`. The brief's wording supports the first reading; the
second is the natural alternative, so both are measured and neither is chosen after seeing outcomes.

**Selection at stopping:** if stopped at 2, submit that agreed patch (representative = smaller
`trajectory_id`); if no stop, submit the D1 representative (largest canonical cluster within the drawn
attempts; ties by smallest `trajectory_id`).

**Comparators.** For k = 1…K_max: **fixed-k** = the first k draws of the same permutation, submit the
D1 representative among those k. `f(k)` = mean resolve over eligible issues, i.e. the fixed-budget
curve. The adaptive rule's own resolve rate `r_ad` and mean cost `c̄` are computed per arm.

**Primary quantity per arm:** `Δ = r_ad − f_interp(c̄)`, where
`f_interp(c̄) = f(k₀) + (c̄ − k₀)·(f(k₁) − f(k₀))`, `k₀ = floor(c̄)`, `k₁ = min(k₀+1, K_max)` —
"matched mean number of attempts". (When `c̄ = K_max`, `f_interp = f(K_max)`.)

**Inference.** Repo-clustered bootstrap: resample repos with replacement, and **inside each replicate**
recompute `c̄`, `f(k₀)`, `f(k₁)` and `f_interp` on the resampled issue set (the interpolation weight
moves with the replicate), seed `seeded_rng("boot2", ktag, "matched")`, `B = 2000`; same CI and p
formula as §3. The full fixed-budget curve `f(k)` for k = 1…K_max is reported as the "curve across
budgets".

**"No effect":** the 95% CI of `Δ` contains 0.

**Measured label-blind costs (results/b4_cost_probe.json; no labels read).** Mean attempts under
`seq_first2` / `seq_any1st`: K=3 arms 2.886–2.959 / 2.886–2.959 (of 3; `nebius_openhands` 2.959,
nvidia configs 2.886–2.944); nebius@K8 7.748 / 7.171 (of 8). So the rule's saving is at most
0.12 of an attempt on the K=3 arms and 0.25 (first-2) to 0.83 (any-repeat) of an attempt at K=8 — the
matched-cost test is tight by construction; the curve is where a real difference would show.

## 7. Multiplicity, aggregation, and verdict vocabulary

- **Primary per analysis per arm:** B1 lift; B2 own-test AUROC; B3 certification count; B4 `Δ`. All on
  the primary frame (§2).
- **Holm (step-down, family α = 0.05) across the 11 configs** within each of B1, B2, B4 (B2 has one
  config, so Holm is vacuous there). The **nebius@K8 arm is reported separately and never enters a
  Holm family or a sign test** (it shares the corpus of `nebius_openhands@K3`).
- **Across-config combination, the only pre-registered one:** the **two-sided exact sign test** on the
  direction of the effect, per analysis, over the 11 configs (ties dropped;
  `p = min(1, 2·P(Bin(n_eff, ½) ≤ min(k₊, k₋)))`). For B3 this sign test *is* the family test (§5).
- **Verdict vocabulary in RESULTS_2.md:** `SIGNIFICANT+` (Holm-adjusted p < 0.05 and estimate in the
  predicted direction), `SIGNIFICANT−` (Holm-adjusted p < 0.05, opposite direction), `NOT SIGNIFICANT`,
  `n/a (count)` for B3 per-config rows. Every other number (secondary tables, alternative-frame
  numbers, `gen_tests_correct`, curve points) is labelled **SECONDARY** or **EXPLORATORY** in place.
- **Direction, fixed in advance:** positive = B1 lift > 0 (agreement-selected beats random), B2
  AUROC > 0.5, B3 cross-fit count > agreement count, B4 Δ > 0 (adaptive beats matched fixed).

## 8. Artifacts and ordering

- Scripts: `scripts/b1_selection_lift.py`, `scripts/b2_within_issue_auroc.py`,
  `scripts/b3_crossfit_certification.py`, `scripts/b4_adaptive_stopping.py`,
  `scripts/render_results2.py`; wrapper `bash reproduce_prereg2.sh`.
- Outputs: `results/b1_selection_lift.json`, `results/b2_within_issue_auroc.json`,
  `results/b3_crossfit_certification.json`, `results/b4_adaptive_stopping.json`, and the rendered
  **[RESULTS_2.md](RESULTS_2.md)** (verdict first, then numbers, then concerns, then the checks below).
- **Checks to run in Part C and report in RESULTS_2.md:** no label is read by any tie-break, draw
  order or signal construction (asserted in code); join assertions (`validate="1:1"`, row counts,
  trajectory ids unique); the 204 shared issues are absent from every B1–B4 frame (asserted); the
  100-pair normalizer review (NORMALIZER_REVIEW.md) still describes the frozen normalizer used here
  (unchanged since sign-off); `pytest tests` passes; the kill test's own primary numbers are unchanged
  by the Part-A edits (field-by-field comparison against the previous JSON).
- **`reproduce_all.sh` is not modified** (standing rule: byte-identical). Part B/C regeneration is the
  separate `reproduce_prereg2.sh`.
- **Ordering:** B1–B4 run **once**, after this file is committed and approved. No re-analysis, no
  threshold change, no added arm afterwards without a DEVIATIONS.md entry. Any post-hoc analysis that
  does get run is logged there as EXPLORATORY and never replaces a pre-registered number.

## 9. What would falsify what (stated in advance)

- **B1 no effect** while B2's own-test AUROC is well above 0.5 → "the information is in the execution
  outcome, not in sibling agreement".
- **B1 effect** → agreement is separating attempts *within* an issue: `random-K(x)` is the issue's
  own sampled resolve rate and the lift is 0 by construction on non-mixed issues, so a positive mean
  lift (necessarily from mixed-label issues, `share_mixed × mean_mixed_lift`) means the agreeing
  cluster's representative resolves more often than a uniform draw from the same issue — information
  beyond issue difficulty. (Corrected by [DEVIATIONS.md](DEVIATIONS.md) D8; the earlier "consistent
  with difficulty" reading was wrong.)
- **B4 no effect** at matched cost → adaptive stopping buys nothing at K≤3 (and K=8) — the signal is
  too coarse for early stopping to be a free lunch.
- **B3 recounts agreement's story:** if the cross-fit signal certifies in more arms than agreement, the
  kill test's coverage collapse is about *which quantity* is used, not about label availability; if it
  certifies in the same two arms, then the two signals are interchangeable in this frame and the
  practical obstacle is identical.
- Any of these outcomes is reportable; a clean "no effect" on all four is the most likely outcome given
  the kill test, and that is a result about the signal, not a failure of the pipeline.

## 10. Limits accepted now, before any of B1–B4 runs

1. B2's signal is binary and available for 46.5% of attempts, missingness not at random (§4); the
   eligible-pair subset is a selected subsample of mixed issues.
2. The agent's own generated tests are the agent's artifact — an attempt can pass trivially weak tests.
   `pred_passes_gen_tests` is execution-grounded but not an independent measurement of correctness;
   that is exactly what makes it interesting to compare against `gen_tests_correct` (gold-patch-based).
3. B4 assumes attempts arrive in random order (seeded permutation). Real arrival order is unobserved
   and could be difficulty-correlated in the agent's favour; random order is the optimistic case for
   early stopping. The measured saving is at most 0.12 of an attempt on the K=3 arms and 0.25–0.83 at
   K=8, so B4's power is small and a null is expected.
4. B1's cluster tie-break is seeded-random here, whereas the kill test's D1 rule breaks ties by
   `trajectory_id`; B1's numbers are therefore not a re-labelling of the frozen selection and do not
   have to match it exactly.
5. B3 has no per-config p-value (it is a count); its family test is a sign test on directions.
6. Everything inherits WEAKNESSES #1 (published labels) and #2 (label noise inside clusters).
7. 11 configs is a small replication set: a sign test over 11 pairs cannot reach p < 0.05 unless the
   split is at least 9–2 in one direction.
