# Tables

## Table 1

| Analysis | Estimate (95% CI) | p | Verdict |
|---|---|---|---|
| B1 | 7+/4−; one arm Holm-significant negative: -0.755 pp [-1.207, -0.319] | 0.549 (Holm 0.022) | NOT SIGNIFICANT |
| B2 | 0.5125 [0.4973, 0.5286] | 0.119 | NOT SIGNIFICANT |
| B3 | 11–0 configs; 2/10/11 vs 0/0/2 | <= 0.001 | SIGNIFICANT+ (not blind) |
| B4 | 8+/3−; largest -0.075 pp [-0.124, -0.022] | 0.227 (Holm 0.099) | NOT SIGNIFICANT |
| B5 | -0.148 pp [-0.980, +0.640] | 0.740 | NOT SIGNIFICANT (exploratory) |

: Holm over 11 K=3 configurations for B1/B4; B2 single test; B3 sign test; B5 exploratory; K=8 separate. Sources: `b1`–`b4` JSONs.

## Table 2

| Signal | AUROC (95% CI) | p | n pairs |
|---|---|---|---:|
| Judge | 0.5786 (0.5587–0.5987) | <= 0.001 | 4,226 |
| Exit reason | 0.5576 (0.5451–0.5707) | <= 0.001 | 4,226 |
| Own tests | 0.5112 (0.4913–0.5322) | 0.2559 | 1,381 |
| Agreement | 0.5121 (0.5046–0.5188) | 0.0020 | 4,226 |
| Steps (oriented, post-hoc) | 0.5477 (0.5254–0.5687) | <= 0.001 | 4,226 |

: Judge frame: judge and same-pair signals; 95% repo-clustered bootstrap (B = 2,000). Steps oriented post-hoc (DEVIATIONS.md). Source: `judge_analysis.json`.

## Table 3

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

: Frozen arms and models; counts exclude 204 shared issues. Six of eleven K=3 arms use 27B language-model policies; no local-execution claim. Source: `results/descriptive_tables.json`.
