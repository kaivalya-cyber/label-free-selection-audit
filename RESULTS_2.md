# RESULTS_2 — four pre-registered analyses on the frozen frames

Run: `bash reproduce_prereg2.sh` · rules: [PREREG-2.md](PREREG-2.md) frozen at `f9558d9`, amended by [DEVIATIONS.md](DEVIATIONS.md) D8 before this run · raw numbers: [B1](results/b1_selection_lift.json), [B2](results/b2_within_issue_auroc.json), [B3](results/b3_crossfit_certification.json), [B4](results/b4_adaptive_stopping.json). §8 is a DESCRIPTIVE addition: it computes no test and changes no number above it.

**Policy models.** Taken from the dataset cards and verified against the rows: every frozen nvidia config has exactly one `metadata.teacher_model.name` value across 100% of its rows. The card states v1.0 = OpenHands v0.53.0 + SWE-agent (no separate SWE-agent version), v1.1 adds mini-swe-agent, v1.2 = Qwen3.8-27B. The nebius card names the policy directly.

| corpus | config | agent | benchmark | policy model (card) |
|---|---|---|---|---|
| nebius/SWE-rebench-openhands-trajectories | nebius_openhands | OpenHands v0.54.0 | SWE-rebench | Qwen3-Coder-480B-A35B-Instruct |
| nvidia/Open-SWE-Traces | v1.0_openhands_minimax_m25_swe-rebench-v2 | OpenHands v0.53.0 | SWE-rebench V2 | MiniMax-M2.5 |
| nvidia/Open-SWE-Traces | v1.0_openhands_qwen35_122b_swe-rebench-v2 | OpenHands v0.53.0 | SWE-rebench V2 | Qwen3.5-122B-A10B |
| nvidia/Open-SWE-Traces | v1.0_sweagent_minimax_m25_swe-rebench-v2 | SWE-agent (v1.0) | SWE-rebench V2 | MiniMax-M2.5 |
| nvidia/Open-SWE-Traces | v1.0_sweagent_qwen35_122b_swe-rebench-v2 | SWE-agent (v1.0) | SWE-rebench V2 | Qwen3.5-122B-A10B |
| nvidia/Open-SWE-Traces | v1.1_minisweagent_qwen36_27b_scale-swe | mini-swe-agent | Scale-SWE | Qwen3.6-27B |
| nvidia/Open-SWE-Traces | v1.1_minisweagent_qwen36_27b_swe-rebench-v2 | mini-swe-agent | SWE-rebench V2 | Qwen3.6-27B |
| nvidia/Open-SWE-Traces | v1.1_sweagent_qwen36_27b_scale-swe | SWE-agent | Scale-SWE | Qwen3.6-27B |
| nvidia/Open-SWE-Traces | v1.1_sweagent_qwen36_27b_swe-rebench-v2 | SWE-agent | SWE-rebench V2 | Qwen3.6-27B |
| nvidia/Open-SWE-Traces | v1.2_minisweagent_qwen38_27b_scale-swe | mini-swe-agent | Scale-SWE | Qwen3.8-27B |
| nvidia/Open-SWE-Traces | v1.2_minisweagent_qwen38_27b_swe-rebench-v2 | mini-swe-agent | SWE-rebench V2 | Qwen3.8-27B |

**Label conventions.** B1, B2 and B4 primary quantities use the PREREG convention (`resolved=-1` rows dropped before sampling). B1 and B3 repeat under `-1`-as-failure (DEVIATIONS D6). B2 is nebius-only, where no `-1` exists. Arms are never pooled. `nebius_openhands@K8` is always reported separately and enters no Holm family or sign test.

## 1. Verdicts

**B1 — NOT SIGNIFICANT.** Selection lift is null in 10 of 11 configs and in the K=8 arm; the sign test is 7 positive vs 4 negative (p = 0.549). One config is SIGNIFICANT− (`v1.1_minisweagent_qwen36_27b_scale-swe`, lift -0.755pp, Holm p = 0.022): agreement there is very slightly *worse* than a random draw from the same issue.

**B2 — NOT SIGNIFICANT.** Within-issue pairwise AUROC of the agent's own-test signal = 0.513, 95% CI 0.497–0.529, p = 0.119 on 4,226 pairs from 754 issues. The CI includes 0.5 and the single-test rule requires both p < 0.05 and a CI excluding 0.5. The signal is not deployable-quality evidence of correctness at this power; see §3 for what does separate pairs.

**B3 — SIGNIFICANT+.** The cross-fit difficulty signal certifies at more α levels than agreement in 11 of 11 configs and fewer in 0 (exact sign test p = 0.0010). Both label conventions give 11–0. It is a label-count signal: deploying it means evaluating the other K−1 attempts, not a free alternative.

**B4 — NOT SIGNIFICANT** at K=3. 8 arms positive, 3 negative, sign test p = 0.227; no arm survives Holm (one arm's raw CI excludes 0, Holm p = 0.099). The K=8 arm is positive by +0.096pp (CI [+0.010, +0.181], p = 0.039), but it is mechanical: the stop-at-2 trigger only fires when the first two patches already agree, so the D1 submission — and its label — is unchanged; the entire Δ is the linear interpolation between f(7) and f(8). Treated as a cost measurement, not evidence that early stopping improves answers.

| analysis | primary per-arm quantity | family rule | family result | verdict |
|---|---|---|---|---|
| B1 | mean selected − random-K | Holm(11) + exact sign test | 7+/4−, p=0.549 | NOT SIGNIFICANT |
| B2 | within-issue pairwise AUROC | single test (Holm vacuous) | AUROC 0.513, p=0.119 | NOT SIGNIFICANT |
| B3 | cross-fit − agreement certification count | exact sign test (11 configs) | 11+/0−, p=0.0010 | SIGNIFICANT+ |
| B4 | Δ = r_ad − f_interp(c̄) | Holm(11) + exact sign test | 8+/3−, p=0.227 | NOT SIGNIFICANT |

## 2. B1 — selection lift

`lift(x) = selected(x) − random-K(x)`, where `random-K(x)` is the issue's own sampled resolve rate. On a non-mixed issue both terms are the issue's single label, so the lift is 0 by construction (DEVIATIONS D8); the mean equals `share_mixed × mean_mixed_lift` and the per-config `lift_identity` residual is 0 in every arm. Positive means the largest cluster's representative resolves more often than a uniform draw from the same issue.

| config | issues | selected | random-K | oracle-K | lift | 95% CI | p | Holm p | verdict |
|---|---|---|---|---|---|---|---|---|---|
| nebius_openhands | 6063 | 47.5% | 47.5% | 55.1% | -0.077pp | [-0.527, +0.374] | 0.735 | 1.000 | NOT SIGNIFICANT |
| v1.0_openhands_minimax_m25 · srb2 | 7463 | 45.7% | 46.0% | 52.4% | -0.317pp | [-0.698, +0.036] | 0.080 | 0.800 | NOT SIGNIFICANT |
| v1.0_openhands_qwen35_122b · srb2 | 5959 | 32.7% | 32.3% | 41.7% | +0.369pp | [-0.165, +0.893] | 0.169 | 1.000 | NOT SIGNIFICANT |
| v1.0_sweagent_minimax_m25 · srb2 | 8466 | 50.2% | 50.1% | 57.5% | +0.177pp | [-0.175, +0.580] | 0.356 | 1.000 | NOT SIGNIFICANT |
| v1.0_sweagent_qwen35_122b · srb2 | 2490 | 51.4% | 51.4% | 59.3% | +0.027pp | [-0.720, +0.840] | 0.926 | 1.000 | NOT SIGNIFICANT |
| v1.1_minisweagent_qwen36_27b · scale | 8783 | 37.3% | 38.1% | 53.0% | -0.755pp | [-1.207, -0.319] | 0.002 | 0.022 | SIGNIFICANT- |
| v1.1_minisweagent_qwen36_27b · srb2 | 12073 | 38.0% | 37.9% | 44.3% | +0.102pp | [-0.193, +0.382] | 0.482 | 1.000 | NOT SIGNIFICANT |
| v1.1_sweagent_qwen36_27b · scale | 8520 | 56.5% | 56.4% | 61.3% | +0.164pp | [-0.131, +0.464] | 0.312 | 1.000 | NOT SIGNIFICANT |
| v1.1_sweagent_qwen36_27b · srb2 | 5580 | 42.0% | 41.8% | 48.5% | +0.233pp | [-0.244, +0.719] | 0.350 | 1.000 | NOT SIGNIFICANT |
| v1.2_minisweagent_qwen38_27b · scale | 13801 | 59.4% | 59.5% | 64.3% | -0.121pp | [-0.350, +0.111] | 0.329 | 1.000 | NOT SIGNIFICANT |
| v1.2_minisweagent_qwen38_27b · srb2 | 10563 | 50.8% | 50.7% | 56.6% | +0.069pp | [-0.263, +0.382] | 0.643 | 1.000 | NOT SIGNIFICANT |
| nebius@K8 (separate) | 4580 | 48.2% | 48.1% | 59.5% | +0.128pp | [-0.468, +0.707] | 0.662 | — | SEPARATE ARM |

*SECONDARY — structure of the lift.*

| config | mixed issues | mixed-only lift | non-mixed lift | share mixed | mean largest cluster | uniquely determined selection |
|---|---|---|---|---|---|---|
| nebius_openhands | 932 | -0.501pp | +0.000pp | 15.4% | 1.11 | 9.2% |
| v1.0_openhands_minimax_m25 · srb2 | 994 | -2.381pp | +0.000pp | 13.3% | 1.26 | 18.7% |
| v1.0_openhands_qwen35_122b · srb2 | 1123 | +1.959pp | +0.000pp | 18.8% | 1.14 | 10.3% |
| v1.0_sweagent_minimax_m25 · srb2 | 1320 | +1.136pp | +0.000pp | 15.6% | 1.26 | 18.6% |
| v1.0_sweagent_qwen35_122b · srb2 | 408 | +0.163pp | +0.000pp | 16.4% | 1.15 | 10.5% |
| v1.1_minisweagent_qwen36_27b · scale | 2201 | -3.014pp | +0.000pp | 25.1% | 1.17 | 12.9% |
| v1.1_minisweagent_qwen36_27b · srb2 | 1595 | +0.773pp | +0.000pp | 13.2% | 1.24 | 16.7% |
| v1.1_sweagent_qwen36_27b · scale | 866 | +1.617pp | +0.000pp | 10.2% | 1.25 | 17.3% |
| v1.1_sweagent_qwen36_27b · srb2 | 765 | +1.699pp | +0.000pp | 13.7% | 1.21 | 15.2% |
| v1.2_minisweagent_qwen38_27b · scale | 1357 | -1.228pp | +0.000pp | 9.8% | 1.18 | 12.6% |
| v1.2_minisweagent_qwen38_27b · srb2 | 1312 | +0.559pp | +0.000pp | 12.4% | 1.19 | 12.9% |

**Sensitivity: `-1` scored as failure (separate pool and labels, not a re-score).**

| config | issues | lift | 95% CI | p | Holm p | verdict |
|---|---|---|---|---|---|---|
| nebius_openhands | 6063 | -0.110pp | [-0.601, +0.366] | 0.680 | 1.000 | NOT SIGNIFICANT |
| v1.0_openhands_minimax_m25 · srb2 | 9570 | -0.108pp | [-0.411, +0.201] | 0.527 | 1.000 | NOT SIGNIFICANT |
| v1.0_openhands_qwen35_122b · srb2 | 7880 | +0.203pp | [-0.196, +0.633] | 0.297 | 1.000 | NOT SIGNIFICANT |
| v1.0_sweagent_minimax_m25 · srb2 | 11020 | +0.051pp | [-0.243, +0.362] | 0.720 | 1.000 | NOT SIGNIFICANT |
| v1.0_sweagent_qwen35_122b · srb2 | 3430 | +0.068pp | [-0.492, +0.622] | 0.806 | 1.000 | NOT SIGNIFICANT |
| v1.1_minisweagent_qwen36_27b · scale | 9904 | -0.498pp | [-0.934, -0.069] | 0.022 | 0.242 | NOT SIGNIFICANT |
| v1.1_minisweagent_qwen36_27b · srb2 | 13849 | +0.007pp | [-0.265, +0.289] | 0.911 | 1.000 | NOT SIGNIFICANT |
| v1.1_sweagent_qwen36_27b · scale | 9537 | +0.210pp | [-0.059, +0.468] | 0.130 | 1.000 | NOT SIGNIFICANT |
| v1.1_sweagent_qwen36_27b · srb2 | 6377 | -0.167pp | [-0.627, +0.251] | 0.447 | 1.000 | NOT SIGNIFICANT |
| v1.2_minisweagent_qwen38_27b · scale | 15509 | +0.163pp | [-0.075, +0.404] | 0.155 | 1.000 | NOT SIGNIFICANT |
| v1.2_minisweagent_qwen38_27b · srb2 | 12151 | +0.102pp | [-0.199, +0.410] | 0.485 | 1.000 | NOT SIGNIFICANT |
| nebius@K8 (separate) | 4580 | +0.456pp | [-0.125, +1.000] | 0.120 | — | SEPARATE ARM |

`-1`-as-failure sign test: 7+/4−, p = 0.549.

*EXPLORATORY E3 — seeded random representative inside the chosen cluster (D8).*

| config | lift (E3) | 95% CI | p | primary lift |
|---|---|---|---|---|
| nebius_openhands | -0.077pp | [-0.532, +0.345] | 0.693 | -0.077pp |
| v1.0_openhands_minimax_m25 · srb2 | -0.331pp | [-0.692, +0.049] | 0.094 | -0.317pp |
| v1.0_openhands_qwen35_122b · srb2 | +0.369pp | [-0.172, +0.891] | 0.159 | +0.369pp |
| v1.0_sweagent_minimax_m25 · srb2 | +0.165pp | [-0.210, +0.549] | 0.374 | +0.177pp |
| v1.0_sweagent_qwen35_122b · srb2 | +0.027pp | [-0.716, +0.800] | 0.900 | +0.027pp |
| v1.1_minisweagent_qwen36_27b · scale | -0.778pp | [-1.214, -0.315] | 0.002 | -0.755pp |
| v1.1_minisweagent_qwen36_27b · srb2 | +0.044pp | [-0.245, +0.333] | 0.736 | +0.102pp |
| v1.1_sweagent_qwen36_27b · scale | +0.164pp | [-0.152, +0.466] | 0.314 | +0.164pp |
| v1.1_sweagent_qwen36_27b · srb2 | +0.215pp | [-0.256, +0.690] | 0.343 | +0.233pp |
| v1.2_minisweagent_qwen38_27b · scale | -0.114pp | [-0.353, +0.127] | 0.347 | -0.121pp |
| v1.2_minisweagent_qwen38_27b · srb2 | +0.013pp | [-0.306, +0.310] | 0.938 | +0.069pp |

E3 is close to B1 in every arm (largest difference 0.06pp): inside a chosen cluster the members almost always share the same label, so which member is submitted barely matters.

## 3. B2 — the agent's own generated tests

Frame: 4,580 nebius@K8 issues, 1,160 mixed-label, 754 with at least one eligible pair, **4,226 pairs** (2,460 both-submit, 532 both-max-iteration); own-test signal present on 17,067 of 36,640 sampled attempts (46.6%).

Pairs are unordered pairs of the *frozen K=8 sample* with different labels and both own-test signals non-null; the resolved attempt is the positive. Both members come from one issue, so issue difficulty cancels by construction.

| signal | AUROC | 95% CI | p vs 0.5 | paired Δ vs own-test | 95% CI | p | n pairs | label |
|---|---|---|---|---|---|---|---|---|
| pred_passes_gen_tests (PRIMARY) | 0.513 | 0.497–0.529 | 0.119 | — | — | — | 4226 | PRIMARY — NOT SIGNIFICANT |
| agreement | 0.506 | 0.502–0.511 | 0.002 | -0.007 | [-0.024, +0.010] | 0.398 | 4226 | SECONDARY |
| steps | 0.440 | 0.415–0.465 | <0.001 | -0.073 | [-0.104, -0.045] | <0.001 | 4226 | SECONDARY |
| exit_reason | 0.576 | 0.558–0.594 | <0.001 | +0.064 | [+0.040, +0.084] | <0.001 | 4226 | SECONDARY |
| gen_tests_correct (gold patch) | 0.589 | 0.572–0.607 | <0.001 | — | — | — | 4200 | EXPLORATORY |

*EXPLORATORY E1 — stratified by exit reason, and the exit reason as a signal (D8).*

| stratum | own-test AUROC | 95% CI | p | pairs |
|---|---|---|---|---|
| both_submit | 0.506 | 0.490–0.524 | 0.481 | 2460 |
| both_max_iteration | 0.507 | 0.464–0.552 | 0.774 | 532 |

The own-test signal is flat inside both exit reasons; the exit reason itself is the stronger separator on the full pair set (AUROC 0.576), and fewer steps is the strongest negative one (0.440). Neither is a correctness measurement that a practitioner can read off a patch.

*SECONDARY — selection lift of the own-test rule (report-only; E2 is exploratory).*

| rule | selected resolve rate | lift vs random-K | 95% CI | p |
|---|---|---|---|---|
| agreement-only (B1 rule) | 48.2% | +0.128pp | [-0.480, +0.711] | 0.669 |
| own-test, null = -1 | 49.0% | +0.892pp | [+0.268, +1.519] | 0.005 |
| largest cluster, then own-test | 49.3% | +1.154pp | [+0.567, +1.776] | <0.001 |
| own-test, null = 0 (E2, EXPLORATORY) | 49.0% | +0.871pp | [+0.203, +1.527] | 0.015 |

Paired against agreement-only: own-test +0.764pp (CI [-0.086, +1.686], p=0.092); combined +1.026pp (CI [+0.223, +1.949], p=0.011); E2 null→0 minus agreement +0.742pp (p=0.106).

**Frame discrepancy, reported not reconciled.** PREREG-2 §4's table says 11,611 pairs over 943 issues. That count is reproducible, but only under two conditions the §4 sentence does not state: `scripts/b4_cost_probe.py` counted pos×neg over each issue's **full pool** of attempts and used its last column, **`gen_tests_correct`**. Full pool / gen = 11,611 / 943; full pool / own-test = 11,614 / 942; frozen K=8 sample / own-test = 4,226 / 754. B2 follows §4's definition, so its power is lower than the table implies. No threshold or quantity changed (DEVIATIONS D9).

## 4. B3 — cross-fit difficulty certification

`rate_loo = (Σ resolved − resolved_rep)/(K−1)`, calibrated and evaluated with the identical kill-test machinery (same splits, τ grids, δ=0.05, n_min=30, repo-clustered bootstrap, BREAKS rule). The count is the number of α levels at which a τ certifies on the held-out-repo calibration split.

| config | agreement count | cross-fit count | Δ | τ @0.05 | τ @0.10 | τ @0.20 | verdict @0.20 |
|---|---|---|---|---|---|---|---|
| nebius_openhands | 0 | 2 | +2 | — | 0.667 | 0.333 | HOLDS |
| v1.0_openhands_minimax_m25 · srb2 | 0 | 2 | +2 | — | 0.667 | 0.333 | HOLDS |
| v1.0_openhands_qwen35_122b · srb2 | 0 | 1 | +1 | — | — | 0.667 | HOLDS |
| v1.0_sweagent_minimax_m25 · srb2 | 0 | 2 | +2 | — | 0.667 | 0.333 | HOLDS |
| v1.0_sweagent_qwen35_122b · srb2 | 0 | 2 | +2 | — | 0.667 | 0.333 | HOLDS |
| v1.1_minisweagent_qwen36_27b · scale | 0 | 2 | +2 | — | 0.667 | 0.667 | HOLDS |
| v1.1_minisweagent_qwen36_27b · srb2 | 0 | 2 | +2 | — | 0.667 | 0.333 | HOLDS |
| v1.1_sweagent_qwen36_27b · scale | 1 | 3 | +2 | 0.667 | 0.333 | 0.333 | HOLDS |
| v1.1_sweagent_qwen36_27b · srb2 | 0 | 2 | +2 | — | 0.667 | 0.333 | HOLDS |
| v1.2_minisweagent_qwen38_27b · scale | 1 | 3 | +2 | 0.667 | 0.333 | 0.333 | HOLDS |
| v1.2_minisweagent_qwen38_27b · srb2 | 0 | 2 | +2 | — | 0.667 | 0.333 | HOLDS |
| nebius@K8 (separate) | 0 | 3 | +3 | 0.875 | 0.750 | 0.500 | HOLDS |

At α=0.05 the cross-fit signal certifies in 2/11 configs (the two that also certify under agreement at α=0.20); at α=0.10 in 10/11; at α=0.20 in 11/11. The K=8 arm certifies at all three. Agreement certifies 0/11, 0/11, 2/11. Counts differ by +1 or +2 in every config, positive in 11/11 under both label conventions.

| config (cross-fit, α=0.20) | coverage | held-out risk | 95% CI | verdict |
|---|---|---|---|---|
| nebius_openhands | 51.9% | 15.1% | 13.3–16.9% | HOLDS |
| v1.0_openhands_minimax_m25 · srb2 | 50.5% | 13.7% | 12.1–15.7% | HOLDS |
| v1.0_openhands_qwen35_122b · srb2 | 27.1% | 13.6% | 11.0–16.4% | HOLDS |
| v1.0_sweagent_minimax_m25 · srb2 | 55.5% | 14.1% | 12.6–15.8% | HOLDS |
| v1.0_sweagent_qwen35_122b · srb2 | 56.7% | 14.9% | 12.2–17.6% | HOLDS |
| v1.1_minisweagent_qwen36_27b · scale | 30.1% | 4.4% | 3.3–5.5% | HOLDS |
| v1.1_minisweagent_qwen36_27b · srb2 | 43.6% | 15.2% | 13.8–16.8% | HOLDS |
| v1.1_sweagent_qwen36_27b · scale | 58.6% | 8.3% | 7.4–9.3% | HOLDS |
| v1.1_sweagent_qwen36_27b · srb2 | 46.3% | 13.5% | 11.4–15.7% | HOLDS |
| v1.2_minisweagent_qwen38_27b · scale | 63.9% | 7.7% | 6.9–8.5% | HOLDS |
| v1.2_minisweagent_qwen38_27b · srb2 | 53.2% | 11.3% | 9.9–12.9% | HOLDS |
| nebius@K8 (separate) | 49.8% | 10.5% | 8.8–12.3% | HOLDS |

**Sensitivity (`-1` as failure):** counts are identical in every config (2, 2, 1, 2, 2, 2, 2, 3, 2, 3, 2) and the sign test is 11–0 again (p = 0.0010).

## 5. B4 — adaptive stopping (and B5)

Draw order is the frozen label-blind permutation; comparators are fixed-k D1 submissions on the same order. `Δ = r_ad − f_interp(c̄)` with the interpolation weight re-estimated inside each bootstrap replicate.

| config | mean attempts c̄ | adaptive r_ad | f_interp(c̄) | Δ | 95% CI | p | Holm p | verdict |
|---|---|---|---|---|---|---|---|---|
| nebius_openhands | 2.956 | 47.5% | 47.5% | +0.011pp | [-0.010, +0.033] | 0.330 | 1.000 | NOT SIGNIFICANT |
| v1.0_openhands_minimax_m25 · srb2 | 2.886 | 46.3% | 46.3% | +0.030pp | [-0.015, +0.077] | 0.213 | 1.000 | NOT SIGNIFICANT |
| v1.0_openhands_qwen35_122b · srb2 | 2.942 | 32.2% | 32.2% | -0.010pp | [-0.040, +0.023] | 0.586 | 1.000 | NOT SIGNIFICANT |
| v1.0_sweagent_minimax_m25 · srb2 | 2.890 | 50.4% | 50.4% | +0.029pp | [-0.016, +0.070] | 0.219 | 1.000 | NOT SIGNIFICANT |
| v1.0_sweagent_qwen35_122b · srb2 | 2.938 | 52.1% | 52.1% | -0.002pp | [-0.053, +0.045] | 0.953 | 1.000 | NOT SIGNIFICANT |
| v1.1_minisweagent_qwen36_27b · scale | 2.930 | 37.3% | 37.4% | -0.075pp | [-0.124, -0.022] | 0.009 | 0.099 | NOT SIGNIFICANT |
| v1.1_minisweagent_qwen36_27b · srb2 | 2.898 | 38.3% | 38.2% | +0.030pp | [-0.029, +0.091] | 0.346 | 1.000 | NOT SIGNIFICANT |
| v1.1_sweagent_qwen36_27b · scale | 2.890 | 56.5% | 56.5% | +0.003pp | [-0.036, +0.043] | 0.863 | 1.000 | NOT SIGNIFICANT |
| v1.1_sweagent_qwen36_27b · srb2 | 2.911 | 41.6% | 41.6% | +0.011pp | [-0.053, +0.084] | 0.790 | 1.000 | NOT SIGNIFICANT |
| v1.2_minisweagent_qwen38_27b · scale | 2.922 | 59.4% | 59.4% | +0.004pp | [-0.018, +0.027] | 0.750 | 1.000 | NOT SIGNIFICANT |
| v1.2_minisweagent_qwen38_27b · srb2 | 2.918 | 50.7% | 50.7% | +0.017pp | [-0.028, +0.068] | 0.463 | 1.000 | NOT SIGNIFICANT |
| nebius@K8 (separate) | 7.768 | 48.3% | 48.2% | +0.096pp | [+0.010, +0.181] | 0.039 | — | SIGNIFICANT+ |

The saving is at most 0.12 of an attempt per K=3 issue (c̄ 2.886–2.956 of 3), so the matched-cost test is tight by construction and a null is what the pre-registration expected. One K=3 arm (`v1.1_minisweagent/qwen36_27b/scale-swe`) has raw p = 0.009 but Holm p = 0.099.

*SECONDARY — the declared `seq_any1st` variant (first repeat anywhere).*

| config | c̄ | r_ad | f_interp | Δ | 95% CI | p |
|---|---|---|---|---|---|---|
| nebius_openhands | 2.956 | 47.5% | 47.5% | +0.011pp | [-0.010, +0.031] | 0.310 |
| v1.0_openhands_minimax_m25 · srb2 | 2.886 | 46.3% | 46.3% | +0.017pp | [-0.035, +0.070] | 0.504 |
| v1.0_openhands_qwen35_122b · srb2 | 2.942 | 32.2% | 32.2% | -0.010pp | [-0.044, +0.020] | 0.549 |
| v1.0_sweagent_minimax_m25 · srb2 | 2.890 | 50.4% | 50.4% | +0.005pp | [-0.048, +0.054] | 0.878 |
| v1.0_sweagent_qwen35_122b · srb2 | 2.938 | 52.2% | 52.1% | +0.038pp | [-0.039, +0.130] | 0.453 |
| v1.1_minisweagent_qwen36_27b · scale | 2.930 | 37.3% | 37.4% | -0.098pp | [-0.163, -0.032] | 0.005 |
| v1.1_minisweagent_qwen36_27b · srb2 | 2.898 | 38.2% | 38.2% | -0.020pp | [-0.117, +0.077] | 0.726 |
| v1.1_sweagent_qwen36_27b · scale | 2.890 | 56.5% | 56.5% | +0.003pp | [-0.036, +0.042] | 0.974 |
| v1.1_sweagent_qwen36_27b · srb2 | 2.911 | 41.8% | 41.6% | +0.118pp | [-0.033, +0.284] | 0.154 |
| v1.2_minisweagent_qwen38_27b · scale | 2.922 | 59.5% | 59.4% | +0.011pp | [-0.012, +0.038] | 0.404 |
| v1.2_minisweagent_qwen38_27b · srb2 | 2.918 | 50.7% | 50.7% | -0.039pp | [-0.184, +0.098] | 0.574 |
| nebius@K8 (separate) | 7.168 | 48.3% | 48.0% | +0.302pp | [-0.004, +0.615] | 0.055 |

*Fixed-budget curves `f(k)` (the “curve across budgets”).*

| config | f(1) | f(2) | f(3) |
|---|---|---|---|
| nebius_openhands | 47.9% | 47.3% | 47.5% |
| v1.0_openhands_minimax_m25 · srb2 | 46.1% | 46.1% | 46.3% |
| v1.0_openhands_qwen35_122b · srb2 | 32.6% | 32.4% | 32.2% |
| v1.0_sweagent_minimax_m25 · srb2 | 49.7% | 50.2% | 50.4% |
| v1.0_sweagent_qwen35_122b · srb2 | 51.2% | 52.2% | 52.1% |
| v1.1_minisweagent_qwen36_27b · scale | 38.2% | 38.4% | 37.3% |
| v1.1_minisweagent_qwen36_27b · srb2 | 37.9% | 38.1% | 38.2% |
| v1.1_sweagent_qwen36_27b · scale | 56.4% | 56.5% | 56.5% |
| v1.1_sweagent_qwen36_27b · srb2 | 41.8% | 42.1% | 41.6% |
| v1.2_minisweagent_qwen38_27b · scale | 59.4% | 59.5% | 59.4% |
| v1.2_minisweagent_qwen38_27b · srb2 | 50.7% | 50.8% | 50.7% |

nebius@K8: f(1)=47.6%, f(2)=48.0%, f(3)=48.1%, f(4)=47.8%, f(5)=48.0%, f(6)=48.0%, f(7)=47.9%, f(8)=48.3%.

*EXPLORATORY B5 (D8) — stop at the first drawn attempt whose own test passes.*

| rule | mean attempts | resolve rate | f_interp(c̄) | Δ | 95% CI | p | verdict |
|---|---|---|---|---|---|---|---|
| B5 own-test stop | 3.443 | 47.8% | 48.0% | -0.148pp | [-0.980, +0.640] | 0.740 | NOT SIGNIFICANT |
| B4 seq_first2 (same arm) | 7.768 | 48.3% | 48.2% | +0.096pp | [+0.010, +0.181] | 0.039 | — |

B5 cuts the budget from 8 attempts to 3.44 (43%) with a resolve rate statistically indistinguishable from fixed-k at that budget. It is the only one of the four analyses whose point estimate is a large practical saving; it is exploratory because it was registered in D8, after the Part-A look at the same corpus.

## 6. Concerns

1. **The agreement story does not survive as a selection rule.** B1's lift is null in every arm but one, and that one is negative. Whatever agreement measures at the config level, it does not pick a better-than-random attempt *within* an issue.
2. **B2's own-test signal is not significant where it was pre-registered.** The AUROC is 0.513 with a CI that includes 0.5. Its secondary selection lift is positive (+0.892pp, p = 0.005), but that is a report-only quantity on the same data; the two are not the same estimand and the positive one is not the pre-registered test.
3. **B2's power is lower than the prereg's table implies** — 4,226 pairs over 754 issues, not 11,611 over 943 (D9). A true AUROC of 0.52 would often fail to separate at this n.
4. **B3 is a strong result for a signal that is not free.** It needs the labels of the other K−1 attempts, i.e. running the evaluation harness on them first. It also inherits the kill test's unit labels, including the tie-break issue below.
5. **B4's K=8 “SIGNIFICANT+” is interpolation, not evidence.** `r_ad` equals `f(8)` exactly: the stop-at-2 trigger fires only when the two patches already agree, so the D1 submission is unchanged and continuing buys nothing. The positive Δ is `f_interp` cutting the corner below a step in `f`. At K=3 the same mechanism gives Δ ≈ 0.01pp because the saving is 0.11 of an attempt.
6. **D1's tie-break was not the one implemented.** `scripts/kill_test.py::build_units` breaks equal-size cluster ties by the lexicographically smallest canonical form, not by the smallest `trajectory_id` as DEVIATIONS D1 says. B4 uses the documented rule, so its f(K) is not the kill test's `resolved_rate`; the audit shows the rules pick a different representative in 18.2–20.3% of K=3 issues and 8.4% of K=8 issues, and the arm-level full-budget resolve rate moves by −1.83 to +1.08pp (nebius K=3 +0.48pp; nebius K=8 +1.09pp). The kill test's frozen numbers are unchanged and are what KILL_TEST.md reports; this is a documentation mismatch in an already-run endpoint, not a re-analysis.
7. **Multiple comparisons.** Four analyses, twelve arms, three α, three splits, two label conventions. Each family is controlled as registered, but the sign tests have almost no power: with 11 configs the exact two-sided threshold is 10–1 (p = 0.0117), not the 9–2 stated in PREREG-2 §10 bullet 7 (9–2 gives p = 0.065).
8. **All the usual label limits stand** (WEAKNESSES #1–#4): published labels, flaky tests inside clusters, undocumented nvidia sampling, `-1` not missing at random.

## 7. Checks

- **Frames.** 12 arms / 94,341 issues re-sampled with the frozen seed arithmetic and compared issue-by-issue with `build_units`: 0 mismatched picks, 0 unit-count mismatches, 0 unit-count mismatches in the `-1`-as-failure frames (their per-issue ids were never serialised).
- **Shared issues.** The 204 cross-corpus issues are excluded and asserted absent from every B1–B4 frame.
- **Tie-breaks read no labels.** Selection uses canonical strings and trajectory ids only; `tests/test_prereg2.py` permutes labels and checks the representative does not move.
- **Kill test reproduction.** The pre-D6 JSON (`8b7e11b`) has 6,461 leaf values; all are present and identical in the current `results/kill_test.json` (0 differences), i.e. the D6/D7 edits changed no primary number.
- **B3 reproduction.** 36 cross-fit cells re-executed; 0 differ from the stored `difficulty_cross_fit` baselines. Split sizes match the frozen JSON (0 mismatches).
- **B4 frame check.** With the kill test's own tie-break, the full-budget resolve rate reproduces every arm's `resolved_rate` (0 mismatches); the documented-rule values are reported beside them in §6.6. B4 was executed twice: the first execution stopped at its own sanity assertion (it assumed the two tie-breaks agreed) before writing any output; the analysis code and seeds were unchanged.
- **Tests.** `pytest tests -q` at render time: 37 passed in 1.35s.
- **Spend.** $0.00 (COST_LOG.md).

## 8. DESCRIPTIVE — chance-level baselines, clustering, and the full budget curve

**No hypothesis test and no verdict is computed in this section.** It adds the three tables requested after the B1–B4 run: per-arm selection baselines, the ICC of `resolved` by issue, and `f(k)` for every arm in one place. Nothing here re-estimates or replaces a frozen B1–B4 quantity; the identity checks at the end of the section are the only consistency statements.

### 8.1 Selection baselines per arm

`pass@1` is the mean of `resolved` over the sampled attempts; with a balanced K it equals the issue-level `random-K` baseline of §2, so the same number appears there. `selected` is the DEVIATIONS D1 rule (largest canonical cluster; equal-size ties by the smallest `trajectory_id` inside the cluster). The second selected column is the tie-break `scripts/kill_test.py` actually implements (smallest canonical string among the top clusters); it is also the rule behind `kill_test.json`'s `resolved_rate` (DEVIATIONS D9). `gap = oracle − selected`: the headroom a rule would gain from knowing in advance which sampled attempt resolves. It is a ceiling, not a deployable rule.

| config | issues | pass@1 | selected (D1) | oracle pass@K | gap (D1) | selected (kill-test, D9) | gap (kill-test) |
|---|---|---|---|---|---|---|---|
| nebius_openhands | 6063 | 47.55% | 47.52% | 55.09% | +7.57pp | 47.04% | +8.05pp |
| v1.0_openhands_minimax_m25 · srb2 | 7463 | 46.04% | 46.34% | 52.39% | +6.06pp | 45.80% | +6.59pp |
| v1.0_openhands_qwen35_122b · srb2 | 5959 | 32.29% | 32.20% | 41.70% | +9.50pp | 31.23% | +10.47pp |
| v1.0_sweagent_minimax_m25 · srb2 | 8466 | 50.06% | 50.44% | 57.47% | +7.03pp | 49.49% | +7.97pp |
| v1.0_sweagent_qwen35_122b · srb2 | 2490 | 51.42% | 52.13% | 59.28% | +7.15pp | 51.04% | +8.23pp |
| v1.1_minisweagent_qwen36_27b · scale | 8783 | 38.09% | 37.30% | 53.05% | +15.75pp | 39.13% | +13.91pp |
| v1.1_minisweagent_qwen36_27b · srb2 | 12073 | 37.92% | 38.23% | 44.33% | +6.10pp | 37.84% | +6.49pp |
| v1.1_sweagent_qwen36_27b · scale | 8520 | 56.37% | 56.48% | 61.30% | +4.82pp | 56.36% | +4.94pp |
| v1.1_sweagent_qwen36_27b · srb2 | 5580 | 41.81% | 41.59% | 48.48% | +6.88pp | 41.95% | +6.52pp |
| v1.2_minisweagent_qwen38_27b · scale | 13801 | 59.49% | 59.44% | 64.30% | +4.86pp | 59.44% | +4.86pp |
| v1.2_minisweagent_qwen38_27b · srb2 | 10563 | 50.72% | 50.71% | 56.64% | +5.94pp | 50.86% | +5.78pp |
| nebius@K8 (separate) | 4580 | 48.10% | 48.30% | 59.54% | +11.24pp | 47.21% | +12.34pp |

The two rules disagree in the selected rate by up to 1.83pp (`v1.1_minisweagent_qwen36_27b · scale`); the next largest is 1.08pp. The gap is 4.8–15.8pp across the K=3 arms and 11.2pp at K=8: even at K=8, a rule that knew which attempt resolves would gain more than ten points over submitting the largest cluster.

### 8.2 Intraclass correlation of `resolved` by issue

One-way random-effects ICC(1), issue as the group, on the frozen K-sample frame; the CI is a repo-clustered bootstrap (`B = 2000`), i.e. whole repos resampled with replacement and all their issues kept.

| config | ICC(1) | 95% CI | issues | repos | k₀ |
|---|---|---|---|---|---|
| nebius_openhands | 0.795 | [0.782, 0.807] | 6063 | 1809 | 3.00 |
| v1.0_openhands_minimax_m25 · srb2 | 0.821 | [0.810, 0.832] | 7463 | 1846 | 3.00 |
| v1.0_openhands_qwen35_122b · srb2 | 0.713 | [0.692, 0.733] | 5959 | 1669 | 3.00 |
| v1.0_sweagent_minimax_m25 · srb2 | 0.792 | [0.781, 0.804] | 8466 | 1859 | 3.00 |
| v1.0_sweagent_qwen35_122b · srb2 | 0.781 | [0.759, 0.802] | 2490 | 984 | 3.00 |
| v1.1_minisweagent_qwen36_27b · scale | 0.646 | [0.626, 0.666] | 8783 | 963 | 3.00 |
| v1.1_minisweagent_qwen36_27b · srb2 | 0.813 | [0.800, 0.825] | 12073 | 2278 | 3.00 |
| v1.1_sweagent_qwen36_27b · scale | 0.862 | [0.852, 0.871] | 8520 | 961 | 3.00 |
| v1.1_sweagent_qwen36_27b · srb2 | 0.812 | [0.796, 0.828] | 5580 | 1719 | 3.00 |
| v1.2_minisweagent_qwen38_27b · scale | 0.864 | [0.857, 0.871] | 13801 | 1081 | 3.00 |
| v1.2_minisweagent_qwen38_27b · srb2 | 0.834 | [0.823, 0.845] | 10563 | 2180 | 3.00 |
| nebius@K8 (separate) | 0.798 | [0.787, 0.811] | 4580 | 1544 | 8.00 |

ICC(1) is 0.646–0.864 across the twelve arms (K=8: 0.798), so most of the variance in `resolved` is **between issues**, not between attempts of the same issue. That is the quantitative reason the within-issue contrasts of B1 and B2 are noisy: after issue difficulty is removed, only 14–35% of the label variance is left to rank attempts, and the repo-clustered bootstrap cannot create information that the design does not contain.

### 8.3 Fixed-budget curve f(k), every arm in one table

`f(k)` = mean resolve rate of the D1 submission restricted to the first k seeded draws (DEVIATIONS D8 draw order); the K=8 arm's curve is the same object at eight budgets.

| config | f(1) | f(2) | f(3) | f(4) | f(5) | f(6) | f(7) | f(8) |
|---|---|---|---|---|---|---|---|---|
| nebius_openhands | 47.9% | 47.3% | 47.5% | — | — | — | — | — |
| v1.0_openhands_minimax_m25 · srb2 | 46.1% | 46.1% | 46.3% | — | — | — | — | — |
| v1.0_openhands_qwen35_122b · srb2 | 32.6% | 32.4% | 32.2% | — | — | — | — | — |
| v1.0_sweagent_minimax_m25 · srb2 | 49.7% | 50.2% | 50.4% | — | — | — | — | — |
| v1.0_sweagent_qwen35_122b · srb2 | 51.2% | 52.2% | 52.1% | — | — | — | — | — |
| v1.1_minisweagent_qwen36_27b · scale | 38.2% | 38.4% | 37.3% | — | — | — | — | — |
| v1.1_minisweagent_qwen36_27b · srb2 | 37.9% | 38.1% | 38.2% | — | — | — | — | — |
| v1.1_sweagent_qwen36_27b · scale | 56.4% | 56.5% | 56.5% | — | — | — | — | — |
| v1.1_sweagent_qwen36_27b · srb2 | 41.8% | 42.1% | 41.6% | — | — | — | — | — |
| v1.2_minisweagent_qwen38_27b · scale | 59.4% | 59.5% | 59.4% | — | — | — | — | — |
| v1.2_minisweagent_qwen38_27b · srb2 | 50.7% | 50.8% | 50.7% | — | — | — | — | — |
| nebius_openhands@K8 | 47.6% | 48.0% | 48.1% | 47.8% | 48.0% | 48.0% | 47.9% | 48.3% |

`f(k)` is flat in every arm: the full range across the budgets is at most 1.07pp (`v1.1_minisweagent_qwen36_27b · scale`), and at most 0.68pp for the K=8 arm. Spending more attempts therefore does not move the selected patch's resolve rate in any arm; the only large budget effect in the table is the oracle gap in §8.1, which needs the labels of all attempts.

**Identity checks (no new number).** 12 arms: frame sizes equal B1/B4; the D1 selected rate equals B4's `f(K)` exactly; the kill-test tie-break reproduces `kill_test.json`'s `resolved_rate` exactly; `identity_mismatches` = 0.

## 9. Files

- Scripts: `scripts/b1_selection_lift.py`, `scripts/b2_within_issue_auroc.py`, `scripts/b3_crossfit_certification.py`, `scripts/b4_adaptive_stopping.py`, `scripts/descriptive_tables.py`, `scripts/render_results2.py`; shared machinery `src/prereg2.py`.
- Wrapper: `bash reproduce_prereg2.sh`. `reproduce_all.sh` is unchanged.
- Raw: `results/b1_selection_lift.json`, `results/b2_within_issue_auroc.json`, `results/b3_crossfit_certification.json`, `results/b4_adaptive_stopping.json`, `results/descriptive_tables.json`.
