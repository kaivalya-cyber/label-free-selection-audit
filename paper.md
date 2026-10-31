---
title: "Sampling more only helps if you can select"
subtitle: "A within-issue audit of label-free selection signals for software-engineering agents"
author: "Anonymous submission"
date: "31 October 2026"
abstract: |
  Software-engineering agents can sample several patches per issue, but deployment must submit one without evaluation labels. We audit selection on 94,341 issue units from two public trajectory corpora: eleven three-attempt configurations and one eight-attempt arm. Resolve outcomes are largely a property of the issue (ICC 0.646–0.864), and the fixed-budget curve f(k) moves by at most 1.07 percentage points. Oracle pass@K exceeds the selected rate by 4.82–15.75 points, but cheap signals do not close the gap. Agreement beats a random draw in 7 of 11 configurations (sign test p = 0.549); own tests give a within-issue AUROC of 0.5125 (95% CI 0.4973–0.5286, p = 0.119). Cross-fit difficulty certifies 2/11, 10/11, and 11/11 configurations at α = 0.05, 0.10, 0.20, versus 0/11, 0/11, and 2/11 for agreement, but needs sibling labels and was not blind. A local Gemma 4 26B-A4B Q4_0 judge reaches 0.5786 (0.5587–0.5987), a small uncorrected edge over exit reason (+0.0209, 95% CI +0.0025 to +0.0411); it misorders about 42% of mixed pairs. More sampling is not a deployment strategy until selection improves.
---

# Introduction

Software-engineering agents edit repositories, run tests, and iterate [@yang2024sweagent; @wang2024openhands]. Since sampling is stochastic, one way to spend more inference compute is to draw K trajectories per issue and submit one patch [@brown2024monkeys; @snell2024scaling]. Coverage, the chance that some sample resolves, rises; the resolve rate of the submitted patch does not. That gap is selection, and deployment must solve it without labels.

We audit selection on frozen trajectories. The unit is an issue within a configuration, with K attempts. Between issues, how much of the outcome is explained by the issue, and how flat is f(k)? Within an issue, can cheap execution-free signals rank a resolved attempt above an unresolved one? Does a local judge add information beyond those signals?

We contribute the between-issue structure on 94,341 units across twelve arms (ICC, f(k), selection gap); a pre-registered kill test with label-convention and NO-COVERAGE reporting; B1–B5 on agreement, own tests, cross-fit difficulty, and adaptive stopping; and a Gemma 4 judge on 4,226 pairs. The result is negative: issue difficulty explains most variance, the selected rate is flat, cheap signals are near chance, a sibling-label count certifies but is not free or blind, and a local 4-bit judge reads a little more without replacing execution.

# Related work

SWE-bench made repository-level issue resolution an evaluation target [@jimenez2023swebench]. SWE-agent and OpenHands made the interface and execution loop central [@yang2024sweagent; @wang2024openhands]; Agentless showed a simple localize-repair-validate pipeline can compete [@xia2024agentless]. SWE-Gym trained agents and verifiers [@pan2024swegym], and SWE-rebench supplied decontaminated tasks [@badertdinov2025swebrebench]. Our corpora are Nebius OpenHands [@nebius2025trajectories] and NVIDIA Open-SWE-Traces [@nvidia2026traces; @ahmad2026openswe].

Repeated sampling is the counterpart: self-consistency picks the common answer [@wang2022selfconsistency], coverage grows with samples [@brown2024monkeys], and compute-optimal scaling allocates unevenly [@snell2024scaling]. These concern coverage or verified domains; we ask which of K patches to submit without a verifier.

Selective prediction supplies the risk language: selective classifiers trade coverage for error control [@geifman2017selective], conformal prediction gives intervals [@angelopoulos2021conformal], and Learn-then-Test turns calibration into multiple testing [@angelopoulos2021ltt]. We use the last for the kill test, but this is an audit, not a new calibration method. LLM-as-a-judge is scalable [@zheng2023judge]; we test a local judge pointwise, one token, no chain of thought.

# Setup

## Data and frozen frames

Nebius supplies 67,074 OpenHands trajectories over 6,306 issues and 1,823 repositories [@nebius2025trajectories]. NVIDIA supplies 818,660 rows in 32 configuration slices over 42,545 casefolded issues and 3,787 repositories [@nvidia2026traces]. We exclude 204 shared issues. Labels are the published `resolved` flags; we did not rerun either harness.

The frozen analysis has eleven K=3 configurations and one Nebius K=8 arm, for 94,341 units. The K=3 set is Nebius, four v1.0, four v1.1, and two v1.2 slices; Table 3 lists every policy. K=8 uses the same policy and agent as Nebius K=3. No agent policy is a local model; only the judge is local.

![Design. Public trajectories feed issue-by-configuration units with K attempts; labels and five signals feed pre-registered tests; the analysis separates within-issue selection/AUROC from between-issue ICC/certification. Frozen frames, no new outcomes. Source: PREREG, PREREG-2, DEVIATIONS.](figures/fig1_design.png){#fig:design width=100%}

## Units, rule, and signals

For a configuration and issue, the frame contains K attempts. The D1 submission is the representative of the largest canonical patch cluster; equal-size clusters are broken by the smallest `trajectory_id`. The issue outcome is that representative's published label. Oracle pass@K is one if any attempt resolved; `f(k)` is the D1 rate using the first k seeded draws; the gap is oracle minus selected.

Canonicalisation is strict, so scratch files, reordered hunks, or equivalent edits can reduce agreement; this makes the signal conservative. The primary convention drops `resolved = −1`; a sensitivity scores it as failure and changes pool and labels. On NVIDIA, the `−1` share is 9.48% for SWE-rebench-V2 rows and 4.85% for Scale-SWE rows.

Five signals. Agreement is the largest canonical cluster's share. Own tests is `pred_passes_gen_tests`, null when unavailable. Exit reason is `submit` versus max-iteration. Steps is assistant steps, oriented so fewer is positive. Cross-fit difficulty is `rate_loo = (Σ resolved − resolved_rep)/(K−1)`, the resolve rate of the other K−1 attempts; it needs those attempts evaluated first.

The judge reads the issue and one patch and returns a single-token YES/NO judgment. The prompt has no repository metadata or instance id and uses the chat template; `p_yes` is a two-way softmax over the YES/NO logits at the final prompt token. Issue text is truncated to 3,072 head and 1,024 tail tokens; patches to 4,096 head and 1,024 tail.

## Inference and pre-registration

Intervals are 95% percentile bootstrap intervals resampling whole repositories (B = 2,000), because attempts within an issue are dependent. B1 and B4 use Holm over the eleven K=3 configurations plus an exact sign test. B2 is a single test: SIGNIFICANT+ requires two-sided p < 0.05 and a CI excluding 0.5. B3 uses an exact sign test. K=8 is always separate and enters no family.

The kill test is fixed-sequence Learn-then-Test over a pre-registered τ grid, δ = 0.05, at least 30 calibration issues, on random-issue, held-out-repo, and temporal splits at α = 0.05, 0.10, 0.20. B1–B4 were frozen at `f9558d9` and amended only by D8. Descriptive tables (ICC, pass@1, f(k), gap) compute no test. The judge study was frozen in PREREG-3 and run under D14; sample, prompt, truncation, scoring, and N rule were fixed before any score existed.

# Results

## Issue difficulty dominates, and f(k) is flat

Coverage rises with K, but the selected rate does not. Pass@1 is 32.29–59.49%, D1 selected 32.20–59.44%, and oracle pass@K 41.70–64.30% (Figure 2). The selection gap is 4.82–15.75 points across K=3 and 11.24 for K=8. These are descriptive point estimates; no interval is defined for the gap. It is a ceiling: what a rule could gain if it knew which sample resolves.

![Per arm, pass@1 (open circle), D1 agreement-selected rate (blue diamond), and oracle pass@K (orange triangle); the line spans the selection gap, labelled in points. 12 arms, 94,341 issue units; point estimates, no interval. Source: `results/descriptive_tables.json`.](figures/fig2_selection_gap.png){#fig:gap width=95%}

f(k) is flat in every arm: across all twelve it moves at most 1.07 points (0.68 for K=8). Figure 3 shows eleven K=3 curves ending at 3 and K=8 continuing to 8. More attempts do not change the selected patch's resolve rate.

![f(k), the D1 resolve rate at budget k, for every arm on a shared axis; K=3 curves end at 3. Maximum within-arm range is 1.07 pp. Point estimates, no interval is defined. Source: `results/descriptive_tables.json`.](figures/fig3_fixed_budget.png){#fig:curves width=95%}

ICC is 0.646–0.864 across twelve arms (Figure 4); Nebius K=8 is 0.798 (95% CI 0.787–0.811), K=3 0.795 (0.782–0.807). Most label variance is between issues; only 14–35% remains to distinguish attempts, which is why the within-issue tests are noisy.

![ICC(1) of `resolved` by issue for 12 arms, with 95% repo-clustered bootstrap intervals (B = 2,000). Estimates 0.646–0.864; Nebius K=8 is 0.798. Source: `results/descriptive_tables.json`.](figures/fig4_icc.png){#fig:icc width=95%}

## Kill test: 0 BREAKS, two arms, and label sensitivity

The agreement rule produced **0 BREAKS across 198 cells**. It certified a τ in 0/12 arms at α = 0.05, 0/12 at 0.10, and 2/12 at 0.20. Ten arms are NO-COVERAGE at every α, which is not a pass. The certified cells are the lowest-error configurations, at coverage 7.14% and 5.58%; held-out risks 15.8% (95% CI 11.7–20.1%) and 16.4% (12.4–20.6%).

The label convention decides the verdict. Scoring `−1` as failure raises risk to 24.0% and 27.1%, above 0.20; the whole pipeline then certifies 0/11 at every α. We call neither primary. Secondary files-touched agreement is 0/11 at every α; patch size and steps 0/11 at 0.20.

Cross-fit is the contrast: 2/11, 10/11, 11/11 vs 0/11, 0/11, 2/11 (Figure 6); exact sign test 11–0, p = 0.00098. K=8 certifies at all three under cross-fit, none under agreement. At 0.20 cross-fit coverage is 27.1–63.9% and risk 4.4–15.2%. This is strong for a signal that is neither free nor blind: the count existed before PREREG-2, and deploying it requires evaluating the other K−1 attempts.

## B1 and B2: agreement is tiny, own tests do not separate pairs

B1's lift is selected minus random-K, where random-K is the issue's own rate. On non-mixed issues both terms are the same label, so lift is zero by construction; the mean comes only from mixed issues. The family is 7+/4− (p = 0.549), with one negative Holm survivor: v1.1 mini/Qwen3.6 Scale-SWE, −0.755 pp (95% CI −1.207 to −0.319; raw p = 0.002, Holm 0.022).

B2's own-test AUROC is 0.5125 (95% CI 0.4973–0.5286, p = 0.119) on 4,226 pairs/754 issues; the CI includes 0.5 and the rule returns NOT SIGNIFICANT. Agreement is 0.5058 (0.5018–0.5112, p = 0.0020), tiny but detectable; exit reason 0.5764 (0.5578–0.5939); steps 0.4397 (0.4146–0.4649).

The own-test selection lift is +0.892 pp (0.268–1.519, p = 0.005), report-only, not the pre-registered test. E2 null-zero is +0.871 (0.203–1.527). The AUROC remains indistinguishable from chance; the lift is a different estimand.

![Within-issue pairwise AUROC with 95% repo-clustered bootstrap intervals (B = 2,000), chance at 0.5. Left: judge pair frame (4,226 pairs; own tests 1,381). Right: B2 frame (4,226 pairs). Judge 0.579, exit 0.558/0.576, agreement 0.512/0.506, own tests 0.511/0.513, steps 0.440. Source: `results/judge_analysis.json`, `results/b2_within_issue_auroc.json`.](figures/fig5_auroc.png){#fig:auroc width=100%}

## B3: certifies, but not free and not blind

B3 compares cross-fit and agreement with identical machinery: 2/11, 10/11, 11/11 vs 0/11, 0/11, 2/11; 11–0, p = 0.00098; `−1`-as-failure also 11–0; K=8 3 vs 0. At 0.20 cross-fit coverage is 27.1–63.9% and risk 4.4–15.2%. `rate_loo` needs the other K−1 labels and inherits the D9 tie-break; its headline existed before PREREG-2. It is evidence that difficulty is measurable from sibling labels, not for a free selector.

![Certification on the held-out-repo split for 11 K=3 configurations at α = 0.05, 0.10, 0.20. Solid bars certify; hatched grey is NO-COVERAGE. Agreement: 0, 0, 2; cross-fit: 2, 10, 11. The K=8 arm certifies under cross-fit at all three and under agreement at none. Source: `results/b3_crossfit_certification.json`, `results/kill_test.json`.](figures/fig6_certification.png){#fig:cert width=85%}

## B4 and B5: stopping early does not buy accuracy

B4 is 8+/3− at K=3 (p = 0.227), no Holm survivor; the largest negative arm is −0.075 pp (−0.124 to −0.022; raw 0.009, Holm 0.099), mean attempts 2.886–2.956/3. There is no detectable effect, CI [−0.124, +0.022]. K=8 is +0.096 (0.010–0.181, p = 0.039), but an interpolation artifact: the trigger fires only when the first two patches agree, so `r_ad = f(8)`, and Δ is the corner between f(7) and f(8).

B5 stops at the first own-test pass (null never stops), else K_max = 8: 3.443/8 attempts (43%), 47.8% vs 48.0%, Δ = −0.148 (−0.980 to +0.640, p = 0.740). At matched cost there is no detectable difference; B5 is not a compute saving.

| Analysis | Estimate (95% CI) | p | Verdict |
|---|---|---|---|
| B1 | 7+/4−; one arm −0.755 pp [−1.207, −0.319] | 0.549 (Holm 0.022) | NOT SIGNIFICANT |
| B2 | 0.5125 [0.4973, 0.5286] | 0.119 | NOT SIGNIFICANT |
| B3 | 11–0 configs; 2/10/11 vs 0/0/2 | 0.00098 | SIGNIFICANT+ |
| B4 | 8+/3−; largest −0.075 pp [−0.124, −0.022] | 0.227 (Holm 0.099) | NOT SIGNIFICANT |
| B5 | −0.148 pp [−0.980, +0.640] | 0.740 | NOT SIGNIFICANT (exploratory) |

: Frozen verdicts. B1/B4 use Holm over 11 K=3 configurations; B2 is a single test; B3 is an exact sign test; B5 is exploratory. K=8 is separate. Source: `results/b1_selection_lift.json`, `b2_within_issue_auroc.json`, `b3_crossfit_certification.json`, `b4_adaptive_stopping.json`.

# Judge study

The judge is **Gemma 4 26B-A4B, QAT Q4_0, via llama.cpp** [@gemma2026] on two T4s. It is not the pre-registered NF4 estimator and not the 31B model. Standard bitsandbytes NF4 leaves the 3-D expert tensors in this mixture-of-experts architecture unquantised; the experts do not fit on two cards, so the NF4 path fails before scoring. D14 substituted the official QAT Q4_0 GGUF; the remaining protocol was unchanged. Results are labelled Q4_0 and are not comparable to an NF4 run.

The sample is 4,226 unordered within-issue pairs over 1,128 issues and 641 repositories; the first 200 were sealed and included. Pairs have different labels and share an issue, so difficulty cancels. We estimate the pairwise AUROC of `p_yes`, ties 0.5, with a repo-clustered bootstrap (B = 2,000).

The judge reaches **0.5786 (95% CI 0.5587–0.5987, p = 0.0010)**, SIGNIFICANT+. It is 2.1 points above exit reason on the same pairs (0.5576, 0.5451–0.5707). The paired judge-minus-exit difference is +0.0209 (95% CI +0.0025 to +0.0411, p = 0.027), uncorrected and secondary: suggestive, not a corrected family result. Own tests give 0.5112 (0.4913–0.5322) on 1,381 pairs and agreement 0.5121 (0.5046–0.5188); paired judge-minus-own is +0.0594 (+0.0197 to +0.1024, p = 0.006), judge-minus-agreement +0.0665 (+0.0473 to +0.0852, p = 0.001). Table 2 reports all four.

At 0.579 the judge misorders about 42% of mixed pairs, and no calibration or threshold analysis was registered. The truncation split is flat: neither patch truncated 0.5772 (0.5493–0.6059, n = 2,221); at least one truncated 0.5800 (0.5554–0.6070, n = 2,005). The realised no-truncation share is 52.6%, not the 74% guessed in the pre-registration; this is a subset comparison, not a causal test.

A local 4-bit judge contains some patch-level information beyond free harness fields, but its edge over exit reason is small and uncorrected, and it covers one corpus. It does not replace execution or license raw probabilities as correctness estimates.

| Signal | AUROC (95% CI) | p | n pairs | Δ vs judge (95% CI; p) |
|---|---|---|---:|---|
| Judge | 0.5786 (0.5587–0.5987) | 0.0010 | 4,226 | — |
| Exit reason | 0.5576 (0.5451–0.5707) | 0.0010 | 4,226 | −0.0209 (−0.0411 to −0.0025); 0.027 |
| Own tests | 0.5112 (0.4913–0.5322) | 0.256 | 1,381 | −0.0594 (−0.1024 to −0.0197); 0.006 |
| Agreement | 0.5121 (0.5046–0.5188) | 0.0020 | 4,226 | −0.0665 (−0.0852 to −0.0473); 0.001 |

: Judge and same-pair signals. Δ is signal minus judge, so negative means the judge has the higher AUROC. Intervals are 95% repo-clustered bootstrap (B = 2,000). Source: `results/judge_analysis.json`.

| Arm | Agent | Policy model | Benchmark | Issues |
|---|---|---|---|---:|
| Nebius K=3 | OpenHands v0.54.0 | Qwen3-Coder-480B-A35B-Instruct | SWE-rebench | 6,063 |
| v1.0 OH/M2.5 | OpenHands v0.53.0 | MiniMax-M2.5 | SWE-rebench V2 | 7,463 |
| v1.0 OH/Q3.5 | OpenHands v0.53.0 | Qwen3.5-122B-A10B | SWE-rebench V2 | 5,959 |
| v1.0 SWE/M2.5 | SWE-agent v1.0 | MiniMax-M2.5 | SWE-rebench V2 | 8,466 |
| v1.0 SWE/Q3.5 | SWE-agent v1.0 | Qwen3.5-122B-A10B | SWE-rebench V2 | 2,490 |
| v1.1 mini/Q3.6 S | mini-swe-agent | Qwen3.6-27B | Scale-SWE | 8,783 |
| v1.1 mini/Q3.6 R | mini-swe-agent | Qwen3.6-27B | SWE-rebench V2 | 12,073 |
| v1.1 SWE/Q3.6 S | SWE-agent | Qwen3.6-27B | Scale-SWE | 8,520 |
| v1.1 SWE/Q3.6 R | SWE-agent | Qwen3.6-27B | SWE-rebench V2 | 5,580 |
| v1.2 mini/Q3.8 S | mini-swe-agent | Qwen3.8-27B | Scale-SWE | 13,801 |
| v1.2 mini/Q3.8 R | mini-swe-agent | Qwen3.8-27B | SWE-rebench V2 | 10,563 |
| Nebius K=8 | OpenHands v0.54.0 | Qwen3-Coder-480B-A35B-Instruct | SWE-rebench | 4,580 |

: Frozen arms and policy models. Issue counts are the K-sample frames after the 204 shared issues are excluded; no row is a local model. Source: `results/descriptive_tables.json` and the `RESULTS_2.md` policy table.

# Limitations

**Labels are published, not recomputed.** Flaky tests and harness errors are inherited, and identical patches can carry different labels. The two certified cells are the lowest-error configurations, weak evidence of robustness. NVIDIA's sampling rule is undocumented, 1–3 trajectories per issue with no stated rule, so sample counts may correlate with difficulty. The `−1` labels are not missing at random (9.48% SWE-rebench V2, 4.85% Scale-SWE), and the verdict changes between conventions.

**Pre-registration/code mismatches remain.** The kill test breaks equal-size cluster ties by the smallest canonical string, not the smallest `trajectory_id` in D1; the rules choose different representatives in 18.2–20.3% of K=3 issues and 8.4% of K=8 issues, and full-budget resolve moves by −1.83 to +1.08 pp. B2's frame is 4,226 pairs over 754 issues, not the 11,611 over 943 implied by its table; the table counted the full pool and `gen_tests_correct`. An AUROC this close to 0.5 needs a larger pair count to separate reliably. PREREG-2's sign-test sentence says 9–2 where the exact threshold is 10–1. These are reporting defects; no frozen number is changed.

**The judge is a different estimator.** It is Q4_0 via llama.cpp, not NF4, and not 31B. A bf16 or NF4 control does not fit on two T4s at this context, so judge quality is not separated from quantisation quality. It is pointwise, with no chain of thought, and may have seen public SWE data in pre-training; contamination was not measured. Judge and own-test analyses cover one corpus (Nebius K=8); the own-test comparison uses 1,381 pairs with non-null signals on both attempts. Prompt truncation affects a substantial minority of patches, though the exploratory split is flat.

**Inference is dependence-limited.** Pairs share attempts and issues, and the repo-clustered bootstrap does not remove that dependence. The eleven-configuration sign tests have little resolution (the exact 10–1 threshold is p = 0.0117; B1/B4 sit at 7–4 and 8–3). The 198 kill-test cells are reported without family-wise control. NO-COVERAGE is not a pass; it means the test had little power. B4's K=8 result is an interpolation artifact. B5 was registered after the Part-A look and is exploratory.

# Implications

More sampling is not a deployment strategy. K attempts raise oracle coverage, but the selected rate is flat, and the cheap signals a harness exposes do not reliably rank attempts within an issue. The strongest signal is not a patch property: it is the resolve rate of the other attempts. It is expensive and not blind, but it points to where future work should go. If a system can afford to evaluate sibling attempts, it should use those labels; if it cannot, it should not present pass@K as a deployable resolve rate.

Frames, seeds, splits, and selection rules are frozen; every number is traceable to a result file or the claims ledger; figures and tables regenerate from cached JSONs. A free local judge at 0.579 is not a selection policy. The next experiment is a cost-matched comparison of judge scores, sibling-label counts, and execution, not another sample-size increase.

# References

1. Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., and Narasimhan, K. SWE-bench: Can Language Models Resolve Real-World GitHub Issues? ICLR 2024. arXiv:2310.06770.
2. Yang, J., Jimenez, C. E., Wettig, A., Lieret, K., Yao, S., Narasimhan, K., and Press, O. SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering. NeurIPS 2024. arXiv:2405.15793.
3. Wang, X., Li, B., Song, Y., et al. OpenHands: An Open Platform for AI Software Developers as Generalist Agents. ICLR 2025. arXiv:2407.16741.
4. Xia, C. S., Deng, Y., Dunn, S., and Zhang, L. Agentless: Demystifying LLM-based Software Engineering Agents. arXiv:2407.01489, 2024.
5. Pan, J., Wang, X., Neubig, G., Jaitly, N., Ji, H., Suhr, A., and Zhang, Y. Training Software Engineering Agents and Verifiers with SWE-Gym. ICML 2025. arXiv:2412.21139.
6. Badertdinov, I., Golubev, A., Nekrashevich, M., et al. SWE-rebench: An Automated Pipeline for Task Collection and Decontaminated Evaluation of Software Engineering Agents. NeurIPS 2025. arXiv:2505.20411.
7. Wang, X., Wei, J., Schuurmans, D., et al. Self-Consistency Improves Chain of Thought Reasoning in Language Models. ICLR 2023. arXiv:2203.11171.
8. Brown, B., Juravsky, J., Ehrlich, R., et al. Large Language Monkeys: Scaling Inference Compute with Repeated Sampling. arXiv:2407.21787, 2024.
9. Snell, C., Lee, J., Xu, K., and Kumar, A. Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters. arXiv:2408.03314, 2024.
10. Geifman, Y., and El-Yaniv, R. Selective Classification for Deep Neural Networks. arXiv:1705.08500, 2017.
11. Angelopoulos, A. N., and Bates, S. A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification. arXiv:2107.07511, 2021.
12. Angelopoulos, A. N., Bates, S., Candès, E. J., Jordan, M. I., and Lei, L. Learn then Test: Calibrating Predictive Algorithms to Achieve Risk Control. arXiv:2110.01052, 2021.
13. Zheng, L., Chiang, W.-L., Sheng, Y., et al. Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. NeurIPS 2023 Datasets and Benchmarks. arXiv:2306.05685.
14. Gemma Team. Gemma 4 Technical Report. arXiv:2607.02770, 2026.
15. Ahmad, W. U., Ludwig, N., Majumdar, S., and Ginsburg, B. Open-SWE-Traces: Advancing Dual-Mode Multilingual Distillation for Software Engineering Agents. arXiv:2606.16038, 2026.
16. Nebius. SWE-rebench-OpenHands-Trajectories. Hugging Face dataset, 2025. https://huggingface.co/datasets/nebius/SWE-rebench-openhands-trajectories.
17. NVIDIA. Open-SWE-Traces. Hugging Face dataset, 2026. https://huggingface.co/datasets/nvidia/Open-SWE-Traces.
