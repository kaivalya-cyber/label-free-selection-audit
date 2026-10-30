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

## D9 — Part-C reporting notes: three discrepancies found while running B1–B4 (2026-10-27) **[post-evaluation, reporting only]**

Written after the single B1–B4 run. None of these changes a quantity, threshold, frame, seed or
verdict; each is a mismatch between a pre-registration sentence and what the code or arithmetic
actually does. All three are reported in [RESULTS_2.md](RESULTS_2.md) §3 and §6.

1. **B2's pair frame is not the frame its own table describes.** PREREG-2 §4 cites 11,611 pairs over
   943 issues. Those numbers reproduce exactly, but only because `scripts/b4_cost_probe.py`
   (a) counted pos×neg over each issue's **full pool** of attempts rather than the frozen K=8 sample
   §4 defines, and (b) used its last argument column, **`gen_tests_correct`**, not the primary
   `pred_passes_gen_tests`. Measured: full pool / gen = 11,611 pairs / 943 issues; full pool /
   own-test = 11,614 / 942; frozen K=8 sample / own-test = **4,226 pairs / 754 issues**. B2 follows
   §4's definition, so its power is lower than the table implies (95% CI half-width ≈ 0.016 AUROC).
   The `gen_tests_correct` count is also the gold-patch-dependent signal §4 itself says is not
   deployable.

2. **D1's cluster tie-break is not the one `kill_test.py` implements.** DEVIATIONS D1 says equal-size
   clusters are broken by the **smallest `trajectory_id` in the cluster**;
   `scripts/kill_test.py::build_units` instead takes `min(canonical form)` among the top clusters and
   then the smallest id inside it. The two rules pick a different representative in 18.2–20.3% of
   K=3 issues and 8.4% of the nebius K=8 issues; the arm-level full-budget resolve rate moves by
   −1.83 to +1.08pp (nebius K=3 +0.48pp; nebius K=8 +1.09pp; both rules are label-blind and fixed in
   advance). B4 uses the **documented** rule, so its `f(K)` is not the kill test's `resolved_rate`.
   The kill test's frozen numbers are unchanged and remain what KILL_TEST.md reports; re-running that
   endpoint under the documented tie-break is **not** done here and is not claimed. B4 was executed
   twice because of this: the first execution stopped at a sanity assertion that assumed `f(K)`
   equalled the kill test's `resolved_rate`, before it wrote any output and before any B4 quantity was
   read. The analysis code and seeds were unchanged; the reported run is the second, and the
   assertion is now the tie-break audit in `results/b4_adaptive_stopping.json`.

3. **Sign-test arithmetic in PREREG-2 §10 bullet 7.** The sentence says a sign test over 11 pairs
   "cannot reach p < 0.05 unless the split is at least 9–2". Exact two-sided values:
   2·P(Bin(11,½) ≤ 2) = 0.0654 for 9–2, and 2·P(Bin(11,½) ≤ 1) = 0.0117 for 10–1. The threshold is
   **10–1**. §7's formula is unchanged and is what B1–B4 use; only the illustrative sentence is wrong.

## D10 — DESCRIPTIVE tables added after the B1–B4 run (2026-10-29) **[post-evaluation, descriptive only]**

Requested after reading the Part-C results. `scripts/descriptive_tables.py` →
`results/descriptive_tables.json` adds three tables to [RESULTS_2.md](RESULTS_2.md) §8: per-arm
pass@1 / agreement-selected / oracle / selection gap, the ICC(1) of `resolved` by issue, and the
fixed-budget curve `f(k)` for every arm in one place.

- **No hypothesis test, threshold or verdict is computed.** No B1–B4 quantity, frame, seed or
  label convention is re-estimated; the section says so in place.
- **Both selection tie-breaks are shown.** The primary column is the documented D1 rule; the second
  is the rule `kill_test.py` actually implements, which is the D9 mismatch. The identity checks
  assert that the D1 rate equals B4's `f(K)` exactly and the kill-test rate equals
  `kill_test.json`'s `resolved_rate` exactly (0 mismatches in 12 arms).
- **ICC(1)** is the one-way random-effects intraclass correlation with issue as the group, on the
  frozen balanced-K frames; the CI resamples whole repos (B = 2000). It is descriptive, not a
  variance-component model used for any inference elsewhere.
- `reproduce_prereg2.sh` now runs the descriptive script before the renderer; no other wrapper is
  touched.

## D11 — PREREG-3 cost-rationale wording, before any run (2026-10-29) **[pre-evaluation]**

Three sentences in [PREREG-3.md](PREREG-3.md) overstated the 31B's exclusion, and one called 4,226
"the largest N whose cost fits". Arithmetic from the frozen table: at 350 prefill tok/s the 31B needs
23.2 GPU-h for N = 4,226, which does fit a 30 GPU-h week (with 6.8 h spare); at 250 tok/s it needs
32.4 h and does not. N = 6,000 at the 26B-A4B's conservative 700 tok/s needs 16.4 h, also inside the
week. Corrected in place:

- §4.2: 4,226 is chosen for B2 comparability and cost margin (≈11.6 h), not as the largest affordable
  N; 6,000 is affordable but costs 50% more for 0.004 AUROC of precision.
- §3.1 and §6.2: the 31B fits memory and only the optimistic end of its range fits the weekly quota;
  "with margin" is the property that selects the 26B-A4B.

No judge has run, no judge output exists, and no quantity, sample, seed, truncation rule, prompt,
comparison signal or verdict rule changes. The freeze commit `65c3999` remains the record of the
original wording.

## D12 — the judge run's N is a throughput-only prefix rule (2026-10-29) **[pre-evaluation]**

Committed **before the pilot**. No judge output exists. Approval for PREREG-3 fixes the model
(`google/gemma-4-26B-A4B-it`, NF4 only), a **12 GPU-hour total cap** across pilot and main run,
checkpointed sessions of at most 9 h, and a hard stop on 2026-11-04 evening.

**Frozen pair order.** The primary sample is `seeded_rng("judge3", "pairs").choice(12917, size=4226,
replace=False)` over the pairs of PREREG-3 §2.2, in the order that call returns. A *prefix* means the
first `n` elements of that order. The first 200 pairs are the pilot; they are part of every prefix and
their sealed scores are the first 200 rows of the main sample.

**Measured rate.** `r` = total **real (unpadded) prefill tokens** across the pilot's forward passes
divided by the summed wall time of those forward passes (`torch.cuda.synchronize()` around each
batch). Model mount, load, tokenisation, shard writing and retries are outside `r`. `r` is recorded in
`pilot_throughput.json`; no judge score, AUROC, ranking or any quantity derived from `p_yes` enters
the computation.

**N rule.** With the frozen mean judgment length `L = 3,002.4783024017465` tokens (PREREG-3 §2.3) and a
**15% safety margin**:

```
T(n) = 2 * n * L * 1.15 / (r * 3600)          GPU-hours, pilot included
N    = min(4226, max { n in [200, 4226] : T(n) <= 12 })
```

`N` is the largest seeded prefix whose predicted token time plus the 15% margin fits the 12 GPU-h cap.
If `T(200) > 12`, the study stops at the pilot and reports the rate; N is not invented below the
registered minimum. If `N = 4226`, the whole registered sample runs. The rule reads throughput only;
it may not be changed after any score is seen.

**Consequences fixed now.** The main run scores pairs `200..N-1` (the pilot's 200 are reused from the
sealed shard), in checkpointed chunks of at most 9 h, with shard hashes verified after each chunk. The
pilot's throughput and token counts are reported as soon as measured; the sealed scores stay unopened
until the main run completes. Every session is logged in `KAGGLE_QUOTA_LOG.md`.

## D13 — the rendered prompt's no-thinking suffix (2026-10-29) **[pre-evaluation]**

Found while checking the Gemma 4 chat template, before the pilot. `PREREG-3` §3.2 describes the
template as ending at `<|turn>model\n`. That is the **thinking-enabled** rendering. The template's
`enable_thinking` default is false, and with thinking disabled it closes the model turn with the empty
thought block:

```
<|turn>model\n<|channel>thought\n<channel|>
```

The runner passes `enable_thinking=False` explicitly and reads the YES/NO logits at the **next**
position, i.e. the first token after `<channel|>`. This is the only rendering consistent with
PREREG-3's "no generation, no chain of thought"; the prompt's instruction text, answer cue, model,
truncation rule and comparison signals are unchanged. The runner asserts the suffix and records the
rendered prompt's sha256 per attempt, so any template drift is visible in the shard. No judge output
exists at this entry.
