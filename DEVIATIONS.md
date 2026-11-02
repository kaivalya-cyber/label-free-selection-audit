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

Written after the single B1–B4 run. None of them changed a reported frozen result, but D9.2 means the
kill test and B3 used a tie-break other than the frozen text (smallest `trajectory_id`). Each is a
mismatch between a pre-registration sentence and what the code or arithmetic actually does. All three are reported in [RESULTS_2.md](RESULTS_2.md) §3 and §6. Each item carries
its own sub-identifier so that one identifier names one item: **D9.1** B2's pair frame, **D9.2** the
kill test's cluster tie-break, **D9.3** the sign-test threshold. What changed in each case is a
sentence in a document; no reported frozen result changed, but D9.2 means the kill test and B3 used a
tie-break other than the frozen text (smallest `trajectory_id`), and full-budget resolve moves by
−1.83 to +1.08 pp between the two rules.

1. **D9.1 — B2's pair frame is not the frame its own table describes.** PREREG-2 §4 cites 11,611 pairs over
   943 issues. Those numbers reproduce exactly, but only because `scripts/b4_cost_probe.py`
   (a) counted pos×neg over each issue's **full pool** of attempts rather than the frozen K=8 sample
   §4 defines, and (b) used its last argument column, **`gen_tests_correct`**, not the primary
   `pred_passes_gen_tests`. Measured: full pool / gen = 11,611 pairs / 943 issues; full pool /
   own-test = 11,614 / 942; frozen K=8 sample / own-test = **4,226 pairs / 754 issues**. B2 follows
   §4's definition, so its power is lower than the table implies (95% CI half-width ≈ 0.016 AUROC).
   The `gen_tests_correct` count is also the gold-patch-dependent signal §4 itself says is not
   deployable. **Frozen quantities:** the B2 sample (4,226 pairs / 754 issues), its seeds and its
   decision rule are unchanged; 11,611 / 943 describe a different frame and a different signal.

2. **D9.2 — D1's cluster tie-break is not the one `kill_test.py` implements.** DEVIATIONS D1 says equal-size
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
   assertion is now the tie-break audit in `results/b4_adaptive_stopping.json`. **Frozen
   quantities:** the kill test's reported cells, coverage, risk intervals and verdicts are
   unchanged, and no endpoint was re-run under the documented rule.

3. **D9.3 — Sign-test arithmetic in PREREG-2 §10 bullet 7.** The sentence says a sign test over 11 pairs
   "cannot reach p < 0.05 unless the split is at least 9–2". Exact two-sided values:
   2·P(Bin(11,½) ≤ 2) = 0.0654 for 9–2, and 2·P(Bin(11,½) ≤ 1) = 0.0117 for 10–1. The threshold is
   **10–1**. **Frozen quantities:** §7's formula is unchanged and is what B1–B4 use; only the
   illustrative sentence is corrected, and B1/B4 sit at 7–4 and 8–3 either way.

## D10 — DESCRIPTIVE tables added after the B1–B4 run (2026-10-29) **[post-evaluation, descriptive only]**

Requested after reading the Part-C results. `scripts/descriptive_tables.py` →
`results/descriptive_tables.json` adds three tables to [RESULTS_2.md](RESULTS_2.md) §8: per-arm
pass@1 / agreement-selected / oracle / selection gap, the ICC(1) of `resolved` by issue, and the
fixed-budget curve `f(k)` for every arm in one place.

- **No hypothesis test, threshold or verdict is computed.** No B1–B4 quantity, frame, seed or
  label convention is re-estimated; the section says so in place.
- **Both selection tie-breaks are shown.** The primary column is the documented D1 rule; the second
  is the rule `kill_test.py` actually implements, which is the D9.2 mismatch. The identity checks
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

## D14 — the judge backend: Gemma 4 26B-A4B QAT Q4_0 via llama.cpp (2026-10-30) **[pre-evaluation]**

The frozen PREREG-3 primary was `google/gemma-4-26B-A4B-it` in NF4 with
`BitsAndBytesConfig(load_in_4bit=True)`. That cannot load on Kaggle 2×T4 (2 × 15.64 GB) at all.
The model is `Gemma4ForConditionalGeneration` with **25.806B** parameters, and each of its 30 MoE
layers stores all **128 experts as 3-D `nn.Parameter` tensors** (`gate_up_proj`, `down_proj`).
bitsandbytes converts only `nn.Linear` modules, so about **22.8B expert parameters (~45.7 GB in
bf16)** remain unquantised; `device_map="auto"` offloads them and raises the CPU/disk error even
with the cards' full memory. This is an architecture limitation, not a batch-size OOM, and no
standard NF4 checkpoint with per-expert `nn.Linear` modules exists for this variant.

**With the user's explicit approval (2026-10-30)**, the primary judge is now the official
**`google/gemma-4/gguf/gemma-4-26b-a4b-it-qat-q4_0-gguf/2`** checkpoint, file
`gemma-4-26B_q4_0-it.gguf` (**14,439,361,440 bytes**), run with **llama.cpp** through
`llama-cpp-python` built with CUDA 12.8 for sm_75, across both T4s (`n_gpu_layers=-1`,
`split_mode=LAYER`, `tensor_split=[0.5, 0.5]`, `n_ctx=10240`, `n_batch=512`, `n_ubatch=256`).

**Unchanged:** the 4,226-pair seeded sample and its order, the frozen truncated content
(precomputed with the HF Gemma 4 tokenizer, PREREG-3 §4.3), the D13 no-thinking suffix
`<|channel>thought\n<channel|>`, the single-token YES/NO read at the next position
(ids 26915/7018, asserted again after load), the pointwise design, the sealed pilot of the first
200 pairs, the D12 throughput-only N rule and its 15% margin, the 12 GPU-hour cap, and the 9-hour
chunk limit. The score is the two-way softmax over the YES and NO logits from
`llama_get_logits` at the final prompt token; no generation, no sampling.

**Changed:** quantisation format **NF4 → QAT Q4_0**, backend **transformers/bitsandbytes →
llama.cpp**, and the model artifact (GGUF file sha256 recorded in every run manifest). Results
are labelled **`26B-A4B Q4_0 (llama.cpp)`** everywhere and are not comparable to an NF4 run. The
Q4_0 file is QAT-trained by Google, so the quantisation is at least as well matched to the weights
as post-hoc NF4, but this is a different estimator and is stated as a limitation.

No judge score, completion or ranking exists at this entry. The pilot is the first GPU use of
this backend.

## D15 — reporting clarifications after the audit (2026-11-01) **[no quantity changed]**

Three reporting points were clarified without changing a result, sample, threshold or verdict:

1. **Cell count.** There are 99 kill-test cells per label convention: 90 K=3 cells (eight
   configurations on three splits; three Scale-SWE configurations on two, because they lack
   `created_at`) plus 9 K=8 cells. The nine K=8 cells are identical across conventions, so the
   distinct computation count is 90×2 + 9 = 189, not 198. The nominal 12×3×3=108 grid overcounts.
   `KILL_TEST.md`, `WEAKNESSES.md` and CLAIMS_LEDGER C45 state the composition; no cell was re-run.
2. **Own-test estimands.** The B2 AUROC (0.5125) is pairwise on mixed-label issues with non-null
   tests; the +0.892 pp selection lift is a per-issue submit-one rule with null = −1 over all
   4,580 issues. The paper explains the estimand difference and does not claim an availability
   mechanism.
3. **Judge sample.** The judge's 4,226 pairs are a seeded sample of 12,917 mixed-label pairs over
   1,128 issues; B2's 4,226 are all own-test-eligible pairs over 754 issues. N matches because
   PREREG-3 fixed it to B2's realised count, not because the samples are the same.

No judge output, analysis or frozen number changed.

## D16 — post-hoc steps orientation and paper counts (2026-11-01) **[post-hoc reporting]**

The review asked for the steps signal to be checked against its code and for the paper's
issue count to distinguish units from issues. Neither change alters a frozen estimate,
sample, threshold or verdict.

1. **Steps orientation.** `scripts/b2_within_issue_auroc.py` stores the raw assistant-message
   count and computes the AUROC on that raw score, so its printed 0.4397 means resolved
   attempts have *fewer* steps. On the B2 frame the within-issue means are 68.06 steps for
   resolved versus 70.29 for unresolved attempts (1,160 mixed-label issues), confirming the
   direction; the post-hoc oriented score is therefore 1 − 0.4397 = 0.5603
   (0.5351–0.5854). The paper now says the code scores the raw count and gives the oriented
   value as post-hoc. On the judge's 4,226 pairs the same reversal gives 0.5477
   (0.5254–0.5687), added to Table 2 as EXPLORATORY. These are transformations of cached
   attempt scores, not new outcomes or a new endpoint.
2. **Distinct issues.** The 48,300 pool issues are the union after excluding 204 cross-corpus
   shared issues; only 41,073 clear the three-attempt floor and enter the sampled frames (D17).
   Nebius K=8 reuses all 4,580 of its issues from Nebius K=3 and adds none distinct. Computed by
   `scripts/paper_addenda.py`; `results/paper_addenda.json`.
3. **Policy size.** Six of the eleven K=3 arms use 27B language models (four Qwen3.6-27B,
   two Qwen3.8-27B), from `results/config_metadata.json`; both cards report 28B total with
   the vision encoder. The paper compares them with Gemma 4 26B-A4B and 31B and makes no
   claim that any policy ran locally.

No judge score, AUROC, sample, threshold or verdict in RESULTS_2.md, RESULTS_3.md or the
frozen JSONs changed.

## D17 — review reconciliation (2026-11-01) **[reporting only]**

1. **Kill-test cells.** D15 double-counted the nine K=8 cells, which are identical across the two
   label conventions. The correct accounting is 99 cells per convention (90 K=3 + 9 K=8) and
   **189 distinct computations** (90×2 + 9), not 198. `KILL_TEST.md`, C45 and the paper now state
   189; 0 BREAKS is unchanged and no cell was re-run.
2. **Distinct issues.** The 48,300 figure is the union of the 11 selected configuration pools after
   excluding 204 shared issues (Nebius 6,102; NVIDIA 42,198; disjoint). Only **41,073** issues clear
   the three-attempt floor and enter a sampled frame: Nebius K=3 keeps 6,063 (39 issues have fewer
   than three labels), and the NVIDIA K=3 frames cover 35,010 (7,188 filtered). The 94,341 units are
   over those 41,073 issues, not over all 48,300. `scripts/paper_addenda.py` asserts every count.
3. **E1 selection lift.** Stratifying the report-only own-test lift by the exit composition of the
   eight attempts gives +0.67 pp (95% CI 0.03–1.32, p = 0.044) on 3,299 all-submit issues,
   +1.39 pp (−0.07–2.93) on 1,239 mixed-exit issues, and +3.27 pp (−5.21–11.61) on 42 all-max
   issues. The pooled lift is +0.892 pp (0.268–1.519, p = 0.005). The paper no longer claims the
   lift reflects signal availability; that mechanism was not tested.
4. **Model cards.** `nvidia/Open-SWE-Traces` names Qwen3.6-27B and Qwen3.8-27B as the v1.1/v1.2
   policies. Both Qwen cards say 27B for the language model and 28B total with the vision
   encoder; checked 2026-11-01. URLs are recorded in AUDIT.md §7.
5. **Word budget.** Rebuilding moved the strictest count to 2,846/2,850 after trimming the nominal
   108-grid sentence and the future-work sentence in §7.

No judge score, AUROC, sample, threshold or verdict in the frozen JSONs changed.

## D18 — full-availability test and NVIDIA count reconciliation (2026-11-01) **[reporting only]**

1. **Own-test lift under full availability.** Restricting to the 226 issues (150 repos) where all
   eight attempts carry a non-null own-test result, the per-issue own-test selection lift is
   **−0.0022 on the fraction scale**, i.e. **−0.22 pp** (95% CI −4.04 to +3.76 pp, p = 0.977),
   versus +0.0089 (= +0.892 pp) pooled. The interval is too wide to test the pooled effect: the
   minimum detectable effect here is about 5.6 pp at 80% power, so it cannot exclude +0.892 pp and
   the availability question stays open rather than answered. This is EXPLORATORY (D17) and changes
   no frozen B2 quantity; `scripts/paper_addenda.py` writes it to
   `results/paper_addenda.json` (`e1_selection_lift.fully_available`). The paper's earlier
   "−0.022 pp" was a ×10 conversion slip in prose, corrected in D19; the JSON was always on the
   fraction scale.
2. **NVIDIA's 143-issue gap.** The casefolded NVIDIA total is 42,545. Of these, 42,402 occur in the
   eleven frozen configurations; 204 of those are shared with Nebius, leaving the 42,198 pool.
   The dataset has **32 configurations**, 10 of them frozen K=3 arms, so **22** are non-frozen; the
   remaining **143** issues occur only in those 22. Thus 42,545 − 204 = 42,341, and
   42,341 − 143 = 42,198. `scripts/paper_addenda.py` asserts 32, 10, 22 and the 143 from
   `out/nvidia_paths.parquet`; no label or unit changed.
3. **B2 reduced draw.** The B1–B4 amendment is the reduced-draw deviation recorded as **D9.1**:
   4,226 pairs / 754 issues in the frozen K=8 sample, not 11,611 / 943 from the pre-registration's
   full-pool table.

No judge score, AUROC, sample, threshold or verdict in the frozen JSONs changed.

## D19 — revision-4 corrections: scale, power framing, identifiers (2026-11-01) **[reporting only]**

Text and reporting corrections only. No frozen B1–B5, kill-test or judge estimate, sample, seed,
threshold or verdict changes. `results/paper_addenda.json` is regenerated by
`scripts/paper_addenda.py` with the same numbers plus a `power` block.

1. **Full-availability scale.** The JSON stores the lift on the fraction scale: −0.0022124 (95% CI
   −0.0404263 to +0.0375688) on 226 issues / 150 repos, against a pooled +0.0089247. In percentage
   points that is **−0.22 pp (95% CI −4.04 to +3.76 pp)**, not the −0.022 pp (−0.041 to +0.038) the
   paper printed: the earlier prose multiplied by 10 instead of 100. The pooled +0.892 pp was already
   converted correctly, and the code never changed. Every location now prints −0.22 pp.
2. **Power statement replaces "does not survive".** The percentile CI half-width is 3.90 pp, so the
   implied SE is 1.99 pp and the minimum detectable effect at 80% power, two-sided α = 0.05, is
   5.57 pp (≈5.6 pp). The interval cannot exclude the pooled +0.892 pp, so §4.3, §7, Limitations,
   AUDIT.md, C93, RESULTS_2.md and WEAKNESSES.md now report the value, the interval and the MDE and
   say the availability question is open; "does not survive" and "no detectable lift" are gone. This
   is a reporting change, not a new test: estimand, frame, seed and B = 2,000 are unchanged.
3. **Deviation identifiers.** D9's three items now carry **D9.1** (B2's pair frame), **D9.2** (the
   kill test's cluster tie-break) and **D9.3** (the sign-test threshold). Every reference in the
   paper, AUDIT.md, RESULTS_2.md, WEAKNESSES.md, CLAIMS_LEDGER.md and the renderers names the one
   item it means; no bare D9 is used for a single item.
4. **NVIDIA non-frozen configurations.** The dataset has 32 configurations, 10 of them frozen K=3
   arms, so **22** are non-frozen (the text said 21). Verified that all 143 non-frozen-only issues
   occur in those 22 and in none of the frozen ten; `scripts/paper_addenda.py` asserts 32 / 10 / 22
   from `out/nvidia_paths.parquet`. The 42,545 / 42,402 / 42,341 / 42,198 counts are unchanged.
5. **Word budget.** The official limit is 3,000 words under rule 3, with a 2,900 working target. This
   revision adds the power caveat and trims two duplicated sentences (the Introduction roadmap and a
   restatement after f(k)). Counts: 2,295 body-only, 2,694 body+captions+tables, **2,898** everything
   except references.
6. **Blind review.** AUDIT.md item 22 claimed the track does not require blind review. No rule text
   for the track is present in this workspace, so the claim is removed rather than quoted; the author
   name stays.

## D20 — revision-5 reporting corrections (2026-11-02) **[reporting only]**

Seven changes to what the paper and audit say. No frozen estimate, interval, threshold, seed, frame
or verdict changed.

1. **Signal scope.** Neither corpus records the repository's held-out test result per attempt
   (AUDIT §1a). Limitations now says own tests are agent-written (`pred_passes_gen_tests`), not the
   repository suite, and that the conclusions do not cover selection by running it; the abstract and
   Implications say "with the signals these trajectories contain".
2. **"Frozen quantity" wording withdrawn.** No post-freeze amendment changed a reported frozen
   result, but D9.2 means the kill test and B3 used a tie-break other than the frozen text (smallest
   `trajectory_id`), and full-budget resolve moves by −1.83 to +1.08 pp between the rules. §3.3 and
   DEVIATIONS now say that instead of "none changed a frozen quantity".
3. **Selected-rate rule.** §4.1 and the Figure 2 caption state that the 32.20–59.44% selected rates
   use the largest canonical cluster with ties by the smallest `trajectory_id` (`d1_pick`, the
   documented D1/B4 rule), not B1's seeded draw over tied top clusters. Values unchanged.
4. **MDE comparison.** §4.3, §7 and Limitations now say 5.6 pp at 80% power is roughly six times the
   pooled +0.892 pp, so the 226-issue subset cannot test whether the pooled lift reflects test
   availability. Values unchanged.
5. **Judge frame.** Table 2 opens "Judge frame:"; §5 names Nebius K=8 and separates the 12,917-pair
   pool over 1,160 issues from the 4,226-pair sample over 1,128. Values unchanged.
6. **Terminology.** "audit pre-registration" is now PREREG-2 wherever it names the protocol, defined
   once in §3.3; Limitations says B5 was registered after the kill test, not after a "Part-A look".
7. **Word budget.** After these additions, paid for from Related work and Implications: **2,278**
   body-only, **2,687** body+captions+tables, **2,898** everything except references (target 2,900,
   official limit 3,000).
