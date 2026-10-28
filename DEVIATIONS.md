# DEVIATIONS

Chronological. Rule: anything that changes PREREG.md after freeze, or any decision taken while
looking at results, goes here with its reason. Entries marked **[pre-evaluation]** were written before
any outcome-vs-signal number was computed; they complete an under-specified detail rather than tune
anything.

## D1 — which patch is "submitted" (2026-10-26) **[pre-evaluation]**

PREREG §1/§3 fixes the unit and the rule but not which trajectory's patch is submitted when several
trajectories agree. Without fixing this, "selective risk" is ambiguous (per-trajectory success vs
any-sample-succeeded), and the difference is large whenever clusters disagree.

Fixed now, before any signal-vs-label computation:

- If the rule says *submit*, the submitted artifact is the patch of the **largest canonical cluster**;
  ties between equally large clusters are broken by the smallest `trajectory_id` in the cluster, and
  within the chosen cluster the representative is the smallest `trajectory_id`.
- The issue-level label is that representative trajectory's own published `resolved` value.
- Consequence (stated up front): two trajectories in the same cluster can carry different labels
  (eval nondeterminism / flaky tests). Such issues are label noise, not signal, and are reported as
  part of the label-noise check rather than removed.

No other definition was tried; nothing was computed before this entry.

## D2 — Scale-SWE configs have no temporal split (2026-10-26) **[pre-evaluation]**

PREREG §4 lists a temporal split for corpora with `created_at`. Recon showed AweAI-Team/Scale-SWE has
no timestamps at all, so the 4 Scale-SWE configs report `n/a` for that split instead of a number.
This is a data availability fact from Phase 0 (DATA_RECON §4), not a choice made after seeing results.

## D5 — post-hoc descriptive diagnostics after the kill test (2026-10-26) **[post-evaluation]**

Reason: the pre-registered procedure certified almost nothing (2 of 12 cells at α=0.20, 0 at α≤0.10),
so the pre-registered endpoint alone cannot say whether agreement carries information at all. Two
descriptive tables were added in `scripts/posthoc_diagnostics.py` → `results/posthoc_diagnostics.json`,
rendered at the end of KILL_TEST.md:

1. error rate by agreement level (1/3, 2/3, 1) per config, all units;
2. within units whose three samples contain exactly two successes, error at agreement 1/3 vs 2/3.

Both are **post-hoc and descriptive**: no threshold, split, α, or verdict was re-computed from them,
and they are not used to select anything. They are reported because the pre-registered test was
underpowered, and a paper that reported only `NO-COVERAGE` would hide the informative structure.
Also fixed in this commit: the rendered sanity-gate table previously labelled `NO-COVERAGE` cells as
"NO" (a formatting bug); they now read `n/a (no certified τ)`. No number changed.

## D6 — both label conventions are reported side by side (2026-10-27) **[post-evaluation, reporting only + rerun]**

Reason: Part A of the follow-up instruction to the kill test's write-up, and WEAKNESSES #4 — the
`-1` convention decides the verdict, so the paper may not report one convention as if it were the
result. What changed, in `scripts/kill_test.py`:

- `run_config(..., convention=...)` now runs the **complete** certification pipeline twice: once on
  the PREREG primary frame (`resolved=-1` rows dropped before sampling; identical to every previously
  reported number) and once with `resolved=-1` scored as **failure** (a larger pool: eligibility and
  labels both change, so the two columns are separate pipelines, not re-scores of one rule).
- The same-rule re-score already reported (C57; `minus1_sensitivity`, which isolates the label change
  at the *primary τ* on the frozen pool) is kept, so the reader sees both decompositions.
- `KILL_TEST.md` now carries both conventions in every headline cell and in every per-config table;
  neither is labelled primary.

No primary number was recomputed under a different rule: the drop-`-1` half of the rerun reproduces
the previous run **field-by-field** (units, repos, base error, resolved rate, agreement levels, every
split × α cell incl. τ, coverage, risk, interval, verdict, the secondary files-touched signal and the
K=8 arm) with **0 differences**. Post-evaluation, but this entry documents a reporting change and a
deterministic re-execution, not a new choice of analysis.

## D7 — the honest (cross-fit) difficulty baseline replaces the oracle version as the headline (2026-10-27) **[post-evaluation]**

Reason: Part A item 3 of the follow-up instruction, and WEAKNESSES #20. `difficulty_plugin_rate`
uses all K sampled labels, **including the label of the attempt being scored**, so it partly leaks the
answer; it is now labelled an **ORACLE CEILING** wherever it appears and keeps no headline role.

Added in `scripts/kill_test.py::build_units`:
`rate_loo = (Σ_i resolved_i − resolved_rep) / (K − 1)` — the issue's resolve rate estimated from the
**other K−1 sampled attempts**, so the scored attempt's own label is excluded by construction. It is
calibrated and evaluated with exactly the identical machinery (same splits, τ grid, δ = 0.05,
n_min = 30, repo-clustered bootstrap, BREAKS rule) and reported per config.

Consequence, stated before any further analysis: the honest cross-fit difficulty signal certifies a τ
in **2/11** configs at α=0.05, **10/11** at α=0.10 and **11/11** at α=0.20 (coverage 27.1%–63.9%,
held-out risk 4.4%–15.2%); the **K=8 arm** certifies at every α as well (τ=0.875/0.75/0.5, coverage
36.6%/42.9%/49.8%), and these counts are for that arm's convention as well. Agreement's counts are
0/11, 0/11, 2/11 (K=8 arm NO-COVERAGE at every α). So the correct negative statement is
**not** "the oracle is better than agreement and the gap is the result" (that claim is removed from
WEAKNESSES #20); it is that a signal derived from the outcomes of sibling attempts certifies broadly
where patch agreement barely certifies at all. The cross-fit rule is still not free: it needs the
labels of the K−1 other attempts, which in deployment means evaluating them first — the same cost
objection that applied to the plug-in version, minus the leak.

## D4 — F1 sensitivity (new-file sections dropped) added after normalizer sign-off (2026-10-26) **[pre-evaluation]**

Context: the pre-evaluation signal probe (label-blind) showed strict patch identity is rare at K=3
(all three identical in 2.1% of nebius units and 3.4%–7.9% of nvidia units), and 64.8% of nebius
trajectories change canonical form when sections that create a new file are dropped. The human gate
review (NORMALIZER_REVIEW.md, 26 content vs 24 file-set differences) signed off the frozen normalizer
and asked for the F1 variant as a **declared sensitivity**, not as the primary signal.

What is added, before any outcome number is computed:

- F1 canonical form = PREREG §2.1 with one extra rule: sections that create a file
  (`new file mode` present or `--- /dev/null`) are dropped before comparison. Implemented in
  `src/sensitivity.py`; the primary path (`src/normalize.py`) is untouched.
- F1 is evaluated **only at the primary τ** (from the strict signal, per config/split/α) on the
  held-out-repo split — no recalibration, so it cannot become a second selection procedure.
- The headline remains the frozen strict signal. F1 appears in KILL_TEST.md as a sensitivity table
  with the same coverage/risk/CI columns.

No label-aware computation preceded this entry; the decision was made from patch-vs-patch statistics
and the human review of 100 pairs.

## D3 — the 204 cross-corpus shared issues are excluded everywhere (2026-10-26) **[pre-evaluation]**

PREREG §1 already says they are excluded from all primary analyses; recorded here so the exclusion
list is auditable: `results/excluded_shared_issues.csv` (casefolded instance ids, 204 rows). A
sensitivity run with them retained in nebius only is reported as a footnote, never as a primary number.

## D8 — Part-C addendum for B1–B4 (2026-10-27) **[pre-evaluation]**

Committed before any B1–B4 quantity was computed. The only numbers that exist before this entry are
the label-blind availability probe (`results/b4_cost_probe.json`) and the Part-A outputs (D6/D7). No
primary quantity, frame, seed, α, split or verdict threshold changes.

1. **Correction to PREREG-2 §9, bullet 2 — the "consistent with difficulty" reading is withdrawn.**
   `lift(x) = selected(x) − random-K(x)` and `random-K(x)` is the *issue's own* sampled resolve rate.
   On a non-mixed issue both terms are that issue's single label, so `lift(x) = 0` exactly, by
   construction; the mean lift therefore comes only from mixed-label issues and equals
   `share_mixed × mean_mixed_lift`. A positive B1 lift is not a restatement of issue difficulty: it
   says the agreeing cluster's representative resolves more often than a uniform draw from the same
   issue's sample, i.e. agreement carries information *within* an issue. The bullet in PREREG-2 §9 is
   corrected in place and marked as corrected here; the pre-correction wording is at commit `f9558d9`.

2. **B2 verdict rule (single-test family).** B2 has one arm, so Holm over one test is the identity.
   The verdict is `SIGNIFICANT+` iff the two-sided repo-clustered bootstrap p < 0.05 **and** the 95%
   CI excludes 0.5; `SIGNIFICANT−` iff p < 0.05 and the estimate lies below 0.5; otherwise
   `NOT SIGNIFICANT`.

3. **EXPLORATORY E1–E3.** Reported, never replacing a primary, and in no Holm family:
   - **E1:** B2's AUROC computed separately on pairs where both attempts ended `submit` and where both
     ended at max-iteration; plus the AUROC of the exit reason alone (`submit` = 1, max-iteration = 0)
     as a comparison signal on the full pair set.
   - **E2:** B2's own-test selection lift with a null signal scored **0** instead of −1.
   - **E3:** B1 with a seeded uniform draw among the chosen cluster's members instead of the smallest
     `trajectory_id` (`seeded_rng("selectrep", ktag, key)` over the cluster's `trajectory_id`s sorted).

4. **EXPLORATORY B5 (nebius@K8 only).** Sequential rule: draw in the same label-blind order as B4;
   stop at the first drawn attempt whose own-test signal is 1 (a null never stops); if none passes,
   continue to `K_max = 8` and submit the D1 representative. Report the resolve rate against the
   fixed-k curve at matched mean attempts (same `f_interp` and repo-clustered bootstrap as B4, seed
   `seeded_rng("boot2", ktag, "b5")`) and the full cost curve.

Two under-specified details are fixed here, before running, and neither is a quantity change:

- for B4's `seq_any1st` variant, the submitted representative when a repeat triggers the stop is the
  smallest `trajectory_id` among the **drawn** attempts sharing the repeated canonical form (for
  `seq_first2` this is the registered "smaller `trajectory_id`");
- B5's draw order is B4's `seeded_rng("seq", ktag, key)` permutation;
- B2's own-test pick (and E2's variant) breaks ties among attempts with equal signal by a seeded
  uniform draw over those attempts sorted by `trajectory_id` (`seeded_rng("selectb2", ktag, key)`),
  the same tie-break PREREG-2 §4 already registers for the combined rule.

Also fixed: B2's paired differences evaluate both signals on the same resampled pairs (seed
`seeded_rng("boot2", ktag, "auroc", pair_tag)`), while each marginal AUROC keeps its pre-registered
per-signal seed.
