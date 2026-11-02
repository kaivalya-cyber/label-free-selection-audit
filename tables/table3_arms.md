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
