# PREREG-3 — a local Gemma judge for patch correctness (nebius, follow-up to B2)

Status: **frozen at commit `65c3999`** (the commit that adds this file), amended by DEVIATIONS D11
(wording of the cost rationale only; no quantity, sample, seed or rule changed); any later change is a
`DEVIATIONS.md` entry.
**Not approved to run.** No judge has been executed and **no judge output exists** — not a single
score, prompt completion or ranking. The only numbers in this file come from the data-side
feasibility probe ([scripts/prereg3_probe.py](scripts/prereg3_probe.py) →
[results/prereg3_probe.json](results/prereg3_probe.json)), which reads issue text, patches, token
counts and label *counts*. It computes no signal-vs-outcome association.

This is a follow-up to B2 ([RESULTS_2.md](RESULTS_2.md) §3): the harness's own generated tests gave a
within-issue pairwise AUROC of 0.5125 (CI 0.4973–0.5286) on 4,226 pairs. The question here is whether
a local language model, reading the issue and the patch, separates resolved from unresolved attempts
better than that — and better than the cheap signals that already beat it (exit reason 0.576,
fewer steps 0.440 as a negative signal).

## 1. Task and estimand

**Task.** One pointwise judgment per (issue, patch): the judge reads the issue text and one candidate
patch and returns a single-token answer, YES or NO, to "does this patch correctly resolve the issue?".
No generation, no chain of thought, no tools.

**Primary quantity.** The **within-issue pairwise AUROC** of the judge's YES probability, on unordered
pairs of the frozen nebius@K=8 sample with different published labels (resolved vs unresolved). Both
members of a pair come from the same issue, so issue difficulty cancels by construction. Ties count
0.5. This is the same estimand and the same pair-construction logic as B2 §4, with one deliberate
difference: **the own-test availability filter is dropped** (the judge reads patches, not the
harness's test fields), which enlarges the pool from 4,226 to 12,917 pairs (§2).

**"No effect":** the 95% repo-clustered bootstrap CI of the AUROC contains 0.5.

**Verdict rule (identical to DEVIATIONS D8's B2 rule, single-test family):**
`SIGNIFICANT+` iff the two-sided repo-clustered bootstrap p < 0.05 **and** the 95% CI excludes 0.5;
`SIGNIFICANT−` iff p < 0.05 and the estimate is below 0.5; otherwise `NOT SIGNIFICANT`. There is one
primary test, so Holm is vacuous and no multiplicity adjustment is applied to it.

## 2. Feasibility probe (data side, run before this file)

### 2.1 Issue text exists and joins at 100%

The trajectory corpus itself carries **no issue text** — its columns are trajectory, patch, exit
status and labels. The text comes from the companion dataset **`nebius/SWE-rebench`** (test split, two
parquet shards, 21,336 rows, unique `instance_id`, no empty `problem_statement`, no id with
conflicting text). The frozen frame's `key` is the **casefolded** instance id (DEVIATIONS D3), so the
join is on `key = instance_id.casefold()`.

| quantity | value |
|---|---|
| nebius issues after the 204 shared-issue exclusion | 6,102 |
| of those, with a `problem_statement` | **6,102 (100%)** |
| frozen K=8 frame issues / with issue text | 4,580 / **4,580 (100%)** |
| frozen K=8 attempts / with issue text | 36,640 / **36,640 (100%)** |
| problem-statement length, p50 / p95 (characters) | 710 / 4,183 |

### 2.2 Pair counts (labels used only to count mixed pairs)

| frame | mixed-label issues | pairs (no signal filter) |
|---|---:|---:|
| frozen K=8 sample | **1,160** | **12,917** |
| full attempt pool (same exclusion, `-1` dropped) | 1,687 | 37,505 |
| B2's frozen pair frame (own-test non-null on both) | 754 | 4,226 |

So the judge study has **3.06×** B2's pair count available without the own-test filter. B2's pairs are
a strict subset of these.

### 2.3 Token lengths under the Gemma 4 tokenizer

Tokenizer: `google/gemma-4-26B-A4B-it/tokenizer.json` (the family tokenizer; vocabulary 262,144). Counts are for the **full prompt minus the fixed instruction block**; the probe
adds a 120-token allowance for that block.

| component | p50 | p90 | p95 | p99 | mean | max |
|---|---:|---:|---:|---:|---:|---:|
| issue text | 270 | 1,065 | 1,611 | 4,661 | 527 | 18,350 |
| patch | 1,419 | 8,776 | 11,361 | 18,785 | 3,459 | 108,646 |
| issue + patch + 120 (raw) | 2,157 | 9,709 | 12,461 | 20,436 | 4,106 | 108,881 |
| after the truncation rule of §4.3 | **2,157** | **5,788** | **6,217** | 7,883 | **3,002** | 9,336 |

With the rule below, **26.1%** of patches and **1.2%** of issues hit their cap; the maximum judgment is
**9,336 tokens**, far inside the 262k context. The rule cuts the total volume for the whole K=8 frame
from 150.4M to 110.0M tokens (−26.9%).

### 2.4 Answer tokens are single tokens

`YES` = id **26915**, `NO` = id **7018** (both one token; `Yes`/`No`/`yes`/`no` are also single tokens,
but the prompt fixes upper case). The score is the two-way softmax over exactly these two logits at the
first position after the model turn.

## 3. Judge harness

### 3.1 Model and fit

| variant | params | bf16 weights | NF4 weights (planning) | fits Kaggle 2×T4 (30 GiB)? |
|---|---:|---:|---:|---|
| **gemma-4-31B-it** | 31.3B | 62.55 GB | ≈17.5–19 GB | **yes, sharded, batch 1** — the largest variant that fits *memory* |
| **gemma-4-26B-A4B-it** | 25.8B total, ~4B active | 51.61 GB | ≈14.5 GB | **yes, comfortably sharded**; one T4 only marginally |
| gemma-4-12B-it | 12.0B | 23.92 GB | ≈6.7 GB | yes, one T4 in NF4; bf16 only sharded |
| gemma-4-E4B-it | 8.0B | 15.99 GB | ≈4.5 GB | yes |

**Primary judge: `google/gemma-4-26B-A4B-it` in 4-bit NF4** (`BitsAndBytesConfig`,
`bnb_4bit_quant_type="nf4"`, double quantisation, bf16 compute, `device_map="auto"`,
`attn_implementation="sdpa"`). The MoE has ~4B active parameters per token, which is what makes a
dense-31B-quality read affordable at this token volume. **Declared fallback, only on an
infrastructure failure** (bitsandbytes unavailable, OOM that cannot be fixed by batch size):
`google/gemma-4-12B-it` in bf16 across both T4s, batch 1. A fallback run is labelled with its model
everywhere and is never compared across models; there is no third fallback.

**Why not the 31B:** it fits memory, but at this token volume it needs 23.2 h even at the optimistic
350 tok/s and 32.4 h at 250 tok/s (§6), so only the optimistic end fits a 30 GPU-h week and it leaves
no room for a re-run. If the approval insists on the literal "largest that fits", the estimate is the
31B row of §6.

### 3.2 Prompt (fixed verbatim; one user turn, no system turn)

The processor's own chat template is used (`AutoProcessor.apply_chat_template(messages,
tokenize=False, add_generation_prompt=True)`; the repository ships `chat_template.jinja`). The user
content is:

```
You are a careful senior software engineer reviewing a candidate patch.

Decide whether the candidate patch correctly resolves the issue below. A patch is CORRECT
only if it fixes the reported behaviour without breaking existing behaviour. A patch that
only changes tests, comments, formatting or documentation is INCORRECT. If the patch is empty
or does not address the issue, answer NO.

ISSUE
<<<
{issue_text}
>>>

CANDIDATE PATCH
<<<
{patch_text}
>>>

Does the candidate patch correctly resolve the issue? Answer with exactly one word: YES or NO.
```

The template renders the turn as `<bos><|turn>user\n…<turn|>\n<|turn>model\n` (verified by tokenising
the literal markers: `<|turn>` = 105, `<turn|>` = 106, `<bos>` = 2). No system prompt, no few-shot
examples, no issue metadata (repo, instance id, base commit) in the prompt: those could leak the
dataset's identity or difficulty.

**Scoring, not generating.** One forward pass per judgment; read `logits[:, -1]`; restrict to the two
answer ids; `p_yes = softmax([z_YES, z_NO])[YES]`. `max_new_tokens` is never called, so there is no
sampling temperature, no top-k and no seed on the model side. `model.eval()`, `torch.inference_mode()`.

### 3.3 Determinism

The judge is deterministic given (weights revision, tokenizer revision, prompt, truncation, device
layout). The Hugging Face **commit revisions are pinned** for the model and tokenizer; the quantisation
config and library versions are recorded in the run manifest. Batching changes only padding, never the
score of a sequence (left padding, logits taken at the final position with the attention mask). The
only stochastic choices are the pair subsample and the batch order, both seeded (§4.2).

## 4. Design

### 4.1 Unit and labels

Frozen nebius@K=8 frame, 204 cross-corpus shared issues excluded (DEVIATIONS D3), `resolved=-1` absent
in this corpus. One judgment per **distinct patch**. The same patch can appear in two pairs only if it
is paired with two different opposite-label attempts; the judge score is computed **once per distinct
trajectory** and reused, so the effective number of forward passes is the number of distinct sampled
attempts, not 2N. (The cost table in §6 uses 2N judgments, i.e. no reuse — an upper bound.)

### 4.2 Pair sample and N

- Pool: **12,917 pairs over 1,160 issues** (§2.2).
- **Primary N = 4,226 pairs**, a seeded uniform sample without replacement:
  `seeded_rng("judge3", "pairs").choice(12917, size=4226, replace=False)`.
- Why 4,226: it equals B2's realised pair count, so the study has B2's precision and is directly
  readable against B2's 0.5125; at the conservative throughput it needs ≈11.6 GPU-h, which leaves room
  for a re-run inside a 30 GPU-h week. A larger N (6,000 pairs, ≈16.4 h) is affordable but buys only
  0.004 AUROC of precision for 50% more compute. The realised number of distinct attempts, issues and
  repos is reported with the result.
- **All 4,226 pairs are scored before any AUROC is computed.** No partial-output analysis: the first
  200 pairs are an engineering pilot (answer-token check, throughput, peak memory) and are *included*
  in the final set, but their scores are not analysed on their own.
- If the cap forces a smaller N, the only permitted reductions are the pre-computed values in the
  power table (§6.3); the choice is made before the run and recorded in `DEVIATIONS.md`.

### 4.3 Truncation rule (fixed before the run)

Tokenize with the Gemma 4 tokenizer after rendering the prompt; truncate the **content fields only**,
never the instruction block or the answer cue.

- **Issue:** keep the first **3,072** and the last **1,024** tokens (cap 4,096), with
  `\n...[issue truncated: N tokens omitted]...\n` between them. 1.2% of issues hit the cap.
- **Patch:** keep the first **4,096** and the last **1,024** tokens (cap 5,120), same marker. 26.1% of
  patches hit the cap. Head+tail keeps the diff's file headers and its final hunks; a head-only cut
  would systematically drop the end of large diffs.
- Empty or whitespace-only patches (0.08% of attempts) are scored **0** without a forward pass, because
  the answer is determined by the data, not by the model; the number of such judgments is reported.
- **Declared sensitivity (free):** the AUROC restricted to pairs where **neither** patch was truncated
  (≈74% of pairs), reported beside the primary. It is a subset, not a new sample, and gets no verdict.

### 4.4 Position-swap rule

**Not applicable, by design.** The judge is **pointwise**: each judgment contains exactly one patch, so
there is no A/B order and nothing to swap. (A pairwise "which patch is correct?" variant would need
both orders, `(A,B)` and `(B,A)`, averaged symmetrically, with the order-consistency rate reported;
that variant is **not** registered here and would require its own pre-registration.) The prompt *layout*
is fixed (issue before patch); it is not varied in this study.

### 4.5 Batching and resume

Pairs are sorted by total token count descending and packed into batches under a **24,000 padded-token
budget** (left padding), which keeps the 15 GiB cards safe at 9,336-token maxima. Output is one row per
distinct trajectory: `{trajectory_id, p_yes, n_tokens, truncated_flags, model_revision}`. Shards of 200
judgments are written and hashed; a resumed run re-verifies the shard hashes. Batch order is
`seeded_rng("judge3", "batches")`; it does not affect scores.

## 5. Comparison signals (same sampled pairs)

| signal | definition | availability | role |
|---|---|---|---|
| **judge** | `p_yes` from §3.2 | every pair | **PRIMARY** |
| exit reason | `submit` = 1, max-iteration = 0 | every pair | SECONDARY |
| own tests | `pred_passes_gen_tests` (1/0), null scored **−1** | pairs with both non-null | SECONDARY |
| own tests, null→0 | same, null scored 0 | every pair | EXPLORATORY (E2 analogue) |
| agreement | cluster size of the attempt / K | every pair | SECONDARY |

Each comparison signal gets the same repo-clustered bootstrap on the same pairs. **Paired differences
against the judge** are computed on the pairs where both signals exist, with the same bootstrap seed
family and the same two-sided p formula; they are secondary and enter no Holm family. The judge's
number is also read against the frozen B2 numbers (own tests 0.5125, exit reason 0.5764, agreement
0.5058) as context, not as a formal cross-run test.

**Bootstrap:** resample repos with replacement, pool their pairs, recompute the AUROC (`B = 2000`,
`seeded_rng("boot2", "judge3", <signal>)`); 95% percentile CI; two-sided p centred on 0.5.

## 6. Cost, GPU-hours and the sample-size floor

### 6.1 Token volume (measured, §2.3)

Mean judgment **3,002 tokens** after truncation; **2 judgments per pair** (upper bound, no patch
reuse). For N = 4,226: **25.4M prefill tokens** (8,452 judgments). For the full 12,917 pairs: 77.6M.

### 6.2 GPU-hours on Kaggle (2×Tesla T4 15 GiB, transformers 5.16, no vLLM)

Planning rates are **assumptions, not measurements**: 31B NF4 sharded 150 / 250 / 350 prefill tok/s;
26B-A4B NF4 sharded 700 / 1,000 / 1,500; 12B NF4 500 / 750 / 1,000. GPU-hours include a 15% overhead
for load, tokenise, shard I/O and retries.

| model | N = 4,226 (25.4M tok) | N = 6,000 (36.0M) | N = 12,917 (77.6M) |
|---|---:|---:|---:|
| **31B NF4 (largest that fits memory)** | **23.2 / 32.4 / 54.0 h** | 32.9 / 46.0 / 76.7 h | 70.8 / 99.1 / 165.2 h |
| **26B-A4B NF4 (recommended primary)** | **5.4 / 8.1 / 11.6 h** | 7.7 / 11.5 / 16.4 h | 16.5 / 24.8 / 35.4 h |
| 12B NF4 (fallback) | 8.1 / 10.8 / 16.2 h | 11.5 / 15.4 / 23.0 h | 24.8 / 33.0 / 49.6 h |

**The answer to "largest that fits":** the 31B fits **memory** (≈18 GB of 30 GB in NF4, sharded) but
only the optimistic end of its 23.2–54.0 GPU-h range fits a 30 GPU-h week (23.2 h at 350 tok/s; 32.4 h
at 250), with no re-run margin. The largest variant that fits **both memory and budget with margin** is
the 26B-A4B at 5.4–11.6 h for N = 4,226.

**Quota assumption:** 30 GPU-h/week, as in the sibling project's Kaggle log. It must be confirmed in
the account before a run; if it is lower, N drops per §6.3.

**Break-even:** N = 4,226 inside 8 GPU-h needs **≥1,014 prefill tok/s** (with the 15% overhead);
inside 12 GPU-h, **≥676 tok/s**. The first pilot's measured rate decides; if it is below the break-even
for the approved cap, the run stops and reports the options rather than shrinking N silently.

### 6.3 Power and the minimum N

Scaling B2's observed SE at 4,226 pairs (0.0080), holding the clustered design fixed:

| N pairs | SE | 95% half-width | minimum detectable AUROC − 0.5 at 80% power |
|---:|---:|---:|---:|
| 849 | 0.0179 | 0.0350 | 0.050 |
| 2,359 | 0.0107 | 0.0210 | 0.030 |
| 4,226 | 0.0080 | 0.0157 | 0.0224 |
| 6,000 | 0.0067 | 0.0132 | 0.0188 |
| 12,917 | 0.0046 | 0.0090 | 0.0128 |

The minimum N for a 0.05 AUROC effect is **849 pairs**; for 0.03, **2,359**; for 0.02, **5,307**
(from the same scaling). N = 4,226 is chosen to detect 0.022, i.e. to separate a judge that is meaningfully
better than B2's 0.513 from one that is not.

## 7. What would falsify what

- **Judge AUROC CI includes 0.5** → a local Gemma judge reading issue+patch does not separate
  resolved from unresolved attempts within an issue at this power. That is a real negative result for
  the "LLM-as-judge replaces execution" story, not a pipeline failure.
- **0.5 < judge < 0.576** → the judge beats the agent's own tests but not the free exit-status field;
  the practical conclusion is that the cheap signal is still the best available one.
- **Judge > 0.576 with a paired CI excluding 0** → the judge adds information beyond exit status and
  own tests; the follow-up is a cost-matched comparison, not a new primary endpoint.
- **Large gap between the primary and the no-truncation subset** → the estimate is driven by patch
  truncation and must be reported as such.

## 8. Limits accepted now

1. **Quantised judge.** NF4 is part of the estimator. A bf16 control does not fit on 2×T4 at this
   context, so the study cannot separate "the judge is weak" from "4-bit hurt the judge". Stated with
   every number.
2. **Published labels are the target.** A judge can be right where the harness is flaky and still score
   below 0.5 on these labels; the estimand is agreement with the published label, not ground truth
   (WEAKNESSES #1–#2).
3. **Pointwise prompt, no chain of thought.** A reasoning judge might do better; that is a different
   study, and adding it after seeing this result would be a new pre-registration.
4. **Pairs are not independent.** They share attempts and issues; the repo-clustered bootstrap is the
   same device B2 used, and it is the only inference reported.
5. **Own-test comparison is on a selected subset** (both signals non-null, 46.6% of attempts); its
   paired difference with the judge is therefore computed on that subset, not on all 4,226.
6. **The issue text is a companion dataset.** `nebius/SWE-rebench` is the source of the problem
   statements; a 100% join was verified on the casefolded key, but the text version is that dataset's,
   not necessarily the version the agent saw.
7. **Nothing here is a new primary endpoint for the paper.** PREREG.md's endpoint and PREREG-2's B1–B4
   stand unchanged; this is a follow-up screen with its own frozen rule.

## 9. Artifacts and ordering

- Probe: `scripts/prereg3_probe.py` → `results/prereg3_probe.json` (already run; data side only).
- To be written only after approval: `scripts/judge_gemma.py`, `scripts/analyze_judge.py`,
  `results/judge_<model>.parquet`, `results/judge_analysis.json`, `RESULTS_3.md`.
- Wrapper (after approval): `reproduce_prereg3.sh`; `reproduce_all.sh` and `reproduce_prereg2.sh` are
  not modified.
- **Ordering:** this file is committed first; the model/tokenizer revisions and the exact prompt hash
  are pinned in the run manifest before the first forward pass. The run starts only with explicit
  approval, in chunks with a declared cap, and no AUROC is computed until all N judgments exist.
