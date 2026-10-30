# RESULTS_3 — a local Gemma judge for patch correctness (PREREG-3, D14 backend)

Status: **judge study complete** (analysis runs only after all N pairs exist). The model is
**Gemma 4 26B-A4B, QAT Q4_0 GGUF** run with llama.cpp; this is the D14 backend, not the frozen
NF4 backend. The pair sample, prompt, truncation, scoring rule and D12 N rule are unchanged.
No judge output was opened while the pilot or any chunk was in progress.

## 0. Header

| item | value |
|---|---|
| model | `google/gemma-4/gguf/gemma-4-26b-a4b-it-qat-q4_0-gguf/2`, `gemma-4-26B_q4_0-it.gguf` |
| model file bytes / sha256 | 14,439,361,440 / `4c856523d61d77922dbc0b26753a6bf6208e5d69d80db0c04dcd776832d054c5` |
| quantisation | QAT Q4_0 (D14; not NF4) |
| backend | llama.cpp via `llama-cpp-python 0.3.36`, CUDA 12.8, sm_75 |
| devices | 2 × Tesla T4 (15,360 MiB each), `n_gpu_layers=-1`, layer split 0.5/0.5 |
| context / batch | `n_ctx=10240`, `n_batch=512`, `n_ubatch=256` |
| answer read | single-token YES / NO (ids 26915 / 7018), two-way softmax at the final prompt token |
| prompt | D13 no-thinking rendering, frozen truncated content from the HF Gemma 4 tokenizer |
| sample | 4,226 pairs over 1,128 issues / 641 repos; 5,466 distinct attempts |
| pilot | first 200 pairs, 388 attempts, sealed; included in the primary sample |
| cap | 12 GPU-hours; sessions ≤ 9 h; shards of 200 with verified hashes |

## 1. What ran

The 30 MoE layers store all 128 experts as 3-D `nn.Parameter` tensors, which bitsandbytes does
not quantise; the frozen NF4 load offloaded and failed on 2×T4. With explicit approval, D14
substituted the official QAT Q4_0 GGUF and llama.cpp. The 4,226-pair seeded sample, the frozen
truncated content, the D13 suffix, the YES/NO logit read, the sealed-pilot rule and the D12
throughput-only N rule were not changed. Results are labelled **26B-A4B Q4_0 (llama.cpp)** and
are not comparable to an NF4 run.

## 2. Throughput and N

| quantity | value |
|---|---:|
| attempts scored | 388 |
| prefill tokens (real) | 1,452,435 |
| forward-pass seconds | 1,461.316 |
| **prefill rate** | **993.923 tokens/s** |
| model load | 117.2 s |
| wall (incl. load) | 1,551.9 s |
| empty patches | 0 |
| main new attempts | 5,076 |
| main prefill tokens | 16,753,941 |
| main forward-pass seconds | 15,988.32 |
| **main prefill rate** | **1,047.886 tokens/s** |
| main wall (incl. load) | 17,102.3 s (4.75 h) |

The frozen D12 rule applies the measured rate with the 15% margin to the **whole** registered
sample (`2 × n × 3,002.478… × 1.15 / (r × 3600)`). At 993.923 tokens/s, **N = 4,226**, so the
main run scored pairs 200–4,225 and reused the sealed pilot attempts. Predicted total
GPU time was **8.16 h** (main 7.77 h), inside the 12 h cap. The actual split was
**pilot 0.43 h + main 4.75 h = 5.18 h** wall (6.1 h including diagnostics).

## 3. Primary quantity

**Within-issue pairwise AUROC** of `p_yes`, on the 4,226 unordered mixed-label pairs; ties count
0.5; 95% repo-clustered percentile bootstrap (B = 2,000), two-sided p centred on 0.5.

| estimate | 95% CI | p | verdict |
|---:|---|---:|---|
| **0.5786** | **0.5587–0.5987** | **0.0010** | **SIGNIFICANT+** |

At 0.5786 the judge is 6.6 pp above B2’s own-test 0.5125. On these pairs the free exit-reason
signal is 0.5576, so the judge is 2.1 pp above it; the paired judge−exit difference is +0.0209
(95% CI +0.0025 to +0.0411, p = 0.027), so the judge adds a small but detectable amount beyond exit
status. (B2’s 0.5764 exit value came from a different pair frame and is not the same-pair
comparison.) It is not a replacement for execution: a 0.579 AUROC still misorders about 42% of the
mixed-label pairs.

## 4. Comparison signals (same pairs)

| signal | definition | AUROC | 95% CI | p | n pairs | paired Δ vs judge (95% CI, p) |
|---|---|---:|---|---:|---:|---|
| exit reason | submit = 1, max-iteration = 0 | 0.5576 | 0.5451–0.5707 | 0.0010 | 4,226 | −0.0209 (−0.0411 to −0.0025), p = 0.027 |
| own tests | `pred_passes_gen_tests`, null excluded | 0.5112 | 0.4913–0.5322 | 0.256 | 1,381 | −0.0594 (−0.1024 to −0.0197), p = 0.006 |
| agreement | canonical cluster size / 8 | 0.5121 | 0.5046–0.5188 | 0.0020 | 4,226 | −0.0665 (−0.0852 to −0.0473), p = 0.001 |

The paired column is **signal − judge**, so a negative value means the judge has the higher AUROC.
These are secondary and enter no multiplicity family. B2's frozen values on its own pair frame
were own tests 0.5125, exit reason 0.5764, agreement 0.5058; the comparison here is contextual,
not a formal cross-run test.

## 5. Exploratory

- **E2 analogue (own tests, null → 0):** 0.5075 (95% CI 0.4935–0.5216, p = 0.296), on
  4,226 pairs.
- **Truncation split** (neither patch truncated, 2,221 pairs): 0.5772 (95% CI 0.5493–0.6059).
  At least one patch truncated (2,005 pairs): 0.5800 (95% CI 0.5554–0.6070). The realised
  no-truncation pair share is **52.6%**, not the ≈74% guessed in PREREG-3 §4.3; the split is a
  subset, not a new sample, and gets no verdict.

## 6. Reading

Within an issue, the Q4_0 judge separates resolved from unresolved attempts at 0.579,
significantly above chance and above both the agent’s own tests (0.511) and agreement (0.512). Its
edge over exit reason is real but small (2.1 pp paired), and the two signals are strongly related:
exit reason alone reaches 0.558 on the same pairs. The practical reading is that a local 4-bit judge
contains some patch-level information beyond the free harness fields, but not enough to replace
execution; the follow-up is a cost-matched comparison, not a new primary endpoint. The truncation
split is flat (0.577 vs 0.580), so the estimate is not driven by the 26% of patches cut at the cap.

## 7. Limits

1. **The judge is Q4_0 QAT, not NF4.** This is a different quantised estimator; the frozen
   limitation said NF4 was part of the estimator. The GGUF is Google's QAT release, but no bf16
   control fits on 2×T4 at this context.
2. **Published labels are the target.** The estimand is agreement with the dataset's resolved
   label, not ground truth; a judge can be right where the harness is flaky (WEAKNESSES #1–#2).
3. **Pointwise, no chain of thought.** A reasoning judge is a different study.
4. **Pairs are not independent.** They share attempts and issues; the repo-clustered bootstrap is
   the only inference reported.
5. **Own-test comparison is on a selected subset** where both attempts have a non-null own-test
   signal, not on all 4,226 pairs.
6. **Prompt truncation.** 26.1% of patches and 1.2% of issues hit their cap; the exploratory split
   reports the no-truncation subset.
7. **The issue text is a companion dataset.** `nebius/SWE-rebench` supplies the statements; the
   casefolded join was verified at 100%, but the text version is that dataset's.
8. **One GPU session exposed a single T4.** The pilot was restarted (D14 log); the completed runs
   used both cards.

## 8. Artifacts and reproduction

- Pairs and attempts: `out/judge/bundle_main/` (`pairs.parquet`, `attempts.parquet`, manifest
  hashes); builder `scripts/judge_build_pairs.py`.
- Pilot: `out/judge/pilot_gguf_out/sealed/pilot_scores.parquet` (sha256 `f042359d…b434`);
  throughput `pilot_throughput.json`.
- Main: `out/judge/main_gguf_out/shards/*.parquet` + `shards/manifest.json`; **26/26 shard
  hashes verified** after download; 5,076 new attempts.
- Analysis: `scripts/analyze_judge.py` → `results/judge_analysis.json` (re-run byte-identical;
  sha256 `2ba5a4cc…`); N rule `results/judge_n.json`.
- Runner: `scripts/judge_run_gguf.py`; D14 in `DEVIATIONS.md`; quota log in
  `KAGGLE_QUOTA_LOG.md`.
