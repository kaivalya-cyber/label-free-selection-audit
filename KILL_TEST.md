# KILL_TEST — pre-registered agreement-based abstention, calibrated → held-out

Command: `.venv/bin/python scripts/kill_test.py` · raw numbers: [results/kill_test.json](results/kill_test.json) · rules: [PREREG.md](PREREG.md), [DEVIATIONS.md](DEVIATIONS.md)


## Bottom line

- α=0.05: 0/12 configs certified a τ; BREAKS verdicts: 0.
- α=0.1: 0/12 configs certified a τ; BREAKS verdicts: 0.
- α=0.2: 2/12 configs certified a τ; BREAKS verdicts: 0.
- BREAKS total across every config, split and α: **0**.
- At α=0.20 the certified cells have coverage 5.6%–7.1% and held-out-repo risk 15.8%–16.4% vs α=20%.
- The binding constraint is power, not calibration breakage: exact patch identity is rare (see DATA_RECON/claims C35–C38), so the unanimous subset is small and its error is only sometimes low enough for Clopper–Pearson to certify α. `NO-COVERAGE` cells carry no risk estimate and are reported as such, not as passes.

## Verdicts (headline split = held-out-repo, per config)

| config | issues | base error | α=0.05 | α=0.1 | α=0.2 |
|---|---|---|---|---|---|
| nebius_openhands | 6063 | 53.0% | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) |
| v1.0_openhands_minimax_m25_swe-rebench-v2 | 7463 | 54.2% | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) |
| v1.0_openhands_qwen35_122b_swe-rebench-v2 | 5959 | 68.8% | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) |
| v1.0_sweagent_minimax_m25_swe-rebench-v2 | 8466 | 50.5% | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) |
| v1.0_sweagent_qwen35_122b_swe-rebench-v2 | 2490 | 49.0% | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) |
| v1.1_minisweagent_qwen36_27b_scale-swe | 8783 | 60.9% | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) |
| v1.1_minisweagent_qwen36_27b_swe-rebench-v2 | 12073 | 62.2% | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) |
| v1.1_sweagent_qwen36_27b_scale-swe | 8520 | 43.6% | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) | HOLDS (7.1%, 15.8%) |
| v1.1_sweagent_qwen36_27b_swe-rebench-v2 | 5580 | 58.0% | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) |
| v1.2_minisweagent_qwen38_27b_scale-swe | 13801 | 40.6% | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) | HOLDS (5.6%, 16.4%) |
| v1.2_minisweagent_qwen38_27b_swe-rebench-v2 | 10563 | 49.1% | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) |
| nebius@K8 | 4580 | 52.8% | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) | NO-COVERAGE (0.0%, —) |

Cells are `VERDICT (coverage, selective risk)`. BREAKS = repo-clustered lower CI bound > α + 0.05; HOLDS = otherwise; NO-COVERAGE = no τ certified on calibration.


## nebius_openhands

`nebius OpenHands v0.54.0 + Qwen3-Coder-480B` · K=3 · issues 6063 · repos 1809 · resolved rate 47.0% · agreement levels {"0.3333333333333333": 5504, "0.6666666666666666": 438, "1.0": 121} · same-cluster label disagreement 0.0%

Truncation: max-iteration rows 8.9%, non-submit rows 9.4%.


**random_issue** (calib 3019 / eval 3044)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**heldout_repo** (calib 3032 / eval 3031)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**temporal** (calib 3856 / eval 2207)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**Baselines (held-out-repo split, calibrated identically)**

| method | α | τ | coverage | risk | verdict |
|---|---|---|---|---|---|
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_plugin_rate | 0.05 | 1.00 | 39.3% | 0.0% | HOLDS |
| difficulty_plugin_rate | 0.1 | 0.67 | 47.3% | 6.8% | HOLDS |
| difficulty_plugin_rate | 0.2 | 0.33 | 54.3% | 14.4% | HOLDS |
| always_submit | 0.05 | — | 100.0% | 53.5% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 53.5% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 53.5% | BREAKS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 4691, "0.6666666666666666": 800, "1.0": 572}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

## v1.0_openhands_minimax_m25_swe-rebench-v2

`v1.0 openhands minimax_m25 swe-rebench-v2` · K=3 · issues 7463 · repos 1846 · resolved rate 45.8% · agreement levels {"0.3333333333333333": 6071, "0.6666666666666666": 825, "1.0": 567} · same-cluster label disagreement 0.0%


**random_issue** (calib 3788 / eval 3675)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**heldout_repo** (calib 3732 / eval 3731)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**temporal** (calib 4376 / eval 3087)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**Baselines (held-out-repo split, calibrated identically)**

| method | α | τ | coverage | risk | verdict |
|---|---|---|---|---|---|
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_plugin_rate | 0.05 | 1.00 | 39.1% | 0.0% | HOLDS |
| difficulty_plugin_rate | 0.1 | 0.67 | 46.6% | 6.3% | HOLDS |
| difficulty_plugin_rate | 0.2 | 0.33 | 52.3% | 13.3% | HOLDS |
| always_submit | 0.05 | — | 100.0% | 54.7% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 54.7% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 54.7% | BREAKS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 5717, "0.6666666666666666": 937, "1.0": 809}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

## v1.0_openhands_qwen35_122b_swe-rebench-v2

`v1.0 openhands qwen35_122b swe-rebench-v2` · K=3 · issues 5959 · repos 1669 · resolved rate 31.2% · agreement levels {"0.3333333333333333": 5343, "0.6666666666666666": 400, "1.0": 216} · same-cluster label disagreement 0.0%


**random_issue** (calib 3046 / eval 2913)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**heldout_repo** (calib 2980 / eval 2979)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**temporal** (calib 3541 / eval 2418)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**Baselines (held-out-repo split, calibrated identically)**

| method | α | τ | coverage | risk | verdict |
|---|---|---|---|---|---|
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_plugin_rate | 0.05 | 1.00 | 23.4% | 0.0% | HOLDS |
| difficulty_plugin_rate | 0.1 | 1.00 | 23.4% | 0.0% | HOLDS |
| difficulty_plugin_rate | 0.2 | 0.67 | 33.1% | 11.2% | HOLDS |
| always_submit | 0.05 | — | 100.0% | 68.2% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 68.2% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 68.2% | BREAKS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 4987, "0.6666666666666666": 527, "1.0": 445}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

## v1.0_sweagent_minimax_m25_swe-rebench-v2

`v1.0 sweagent minimax_m25 swe-rebench-v2` · K=3 · issues 8466 · repos 1859 · resolved rate 49.5% · agreement levels {"0.3333333333333333": 6888, "0.6666666666666666": 968, "1.0": 610} · same-cluster label disagreement 0.1%


**random_issue** (calib 4247 / eval 4219)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**heldout_repo** (calib 4233 / eval 4233)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**temporal** (calib 4973 / eval 3493)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**Baselines (held-out-repo split, calibrated identically)**

| method | α | τ | coverage | risk | verdict |
|---|---|---|---|---|---|
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_plugin_rate | 0.05 | 1.00 | 41.9% | 0.0% | HOLDS |
| difficulty_plugin_rate | 0.1 | 0.67 | 51.0% | 6.6% | HOLDS |
| difficulty_plugin_rate | 0.2 | 0.33 | 57.6% | 13.6% | HOLDS |
| always_submit | 0.05 | — | 100.0% | 50.2% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 50.2% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 50.2% | BREAKS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 6554, "0.6666666666666666": 1087, "1.0": 825}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

## v1.0_sweagent_qwen35_122b_swe-rebench-v2

`v1.0 sweagent qwen35_122b swe-rebench-v2` · K=3 · issues 2490 · repos 984 · resolved rate 51.0% · agreement levels {"0.3333333333333333": 2229, "0.6666666666666666": 155, "1.0": 106} · same-cluster label disagreement 0.1%


**random_issue** (calib 1218 / eval 1272)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**heldout_repo** (calib 1245 / eval 1245)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**temporal** (calib 1264 / eval 1226)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**Baselines (held-out-repo split, calibrated identically)**

| method | α | τ | coverage | risk | verdict |
|---|---|---|---|---|---|
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_plugin_rate | 0.05 | 1.00 | 41.8% | 0.0% | HOLDS |
| difficulty_plugin_rate | 0.1 | 0.67 | 51.3% | 5.9% | HOLDS |
| difficulty_plugin_rate | 0.2 | 0.33 | 58.9% | 14.3% | HOLDS |
| always_submit | 0.05 | — | 100.0% | 49.6% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 49.6% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 49.6% | BREAKS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 2221, "0.6666666666666666": 162, "1.0": 107}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

## v1.1_minisweagent_qwen36_27b_scale-swe

`v1.1 minisweagent qwen36_27b scale-swe` · K=3 · issues 8783 · repos 963 · resolved rate 39.1% · agreement levels {"0.3333333333333333": 7651, "0.6666666666666666": 780, "1.0": 352} · same-cluster label disagreement 0.2%

Temporal split not applicable for 8783 issues (no timestamps).


**random_issue** (calib 4393 / eval 4390)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**heldout_repo** (calib 4392 / eval 4391)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**Baselines (held-out-repo split, calibrated identically)**

| method | α | τ | coverage | risk | verdict |
|---|---|---|---|---|---|
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_plugin_rate | 0.05 | 1.00 | 28.8% | 0.0% | HOLDS |
| difficulty_plugin_rate | 0.1 | 0.67 | 34.1% | 3.9% | HOLDS |
| difficulty_plugin_rate | 0.2 | 0.67 | 34.1% | 3.9% | HOLDS |
| always_submit | 0.05 | — | 100.0% | 60.4% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 60.4% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 60.4% | BREAKS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 7447, "0.6666666666666666": 875, "1.0": 461}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

## v1.1_minisweagent_qwen36_27b_swe-rebench-v2

`v1.1 minisweagent qwen36_27b swe-rebench-v2` · K=3 · issues 12073 · repos 2278 · resolved rate 37.8% · agreement levels {"0.3333333333333333": 10052, "0.6666666666666666": 1169, "1.0": 852} · same-cluster label disagreement 0.7%


**random_issue** (calib 6047 / eval 6026)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**heldout_repo** (calib 6037 / eval 6036)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**temporal** (calib 6785 / eval 5288)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**Baselines (held-out-repo split, calibrated identically)**

| method | α | τ | coverage | risk | verdict |
|---|---|---|---|---|---|
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_plugin_rate | 0.05 | 1.00 | 32.1% | 0.0% | HOLDS |
| difficulty_plugin_rate | 0.1 | 0.67 | 39.5% | 6.4% | HOLDS |
| difficulty_plugin_rate | 0.2 | 0.33 | 45.5% | 14.6% | HOLDS |
| always_submit | 0.05 | — | 100.0% | 61.1% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 61.1% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 61.1% | BREAKS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 9465, "0.6666666666666666": 1338, "1.0": 1270}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

## v1.1_sweagent_qwen36_27b_scale-swe

`v1.1 sweagent qwen36_27b scale-swe` · K=3 · issues 8520 · repos 961 · resolved rate 56.4% · agreement levels {"0.3333333333333333": 7042, "0.6666666666666666": 802, "1.0": 676} · same-cluster label disagreement 0.0%

Temporal split not applicable for 8520 issues (no timestamps).


**random_issue** (calib 4247 / eval 4273)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | 1.000 | 342 | 8.0% | 14.0% | [10.6%, 17.8%] | HOLDS |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**heldout_repo** (calib 4260 / eval 4260)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | 1.000 | 304 | 7.1% | 15.8% | [11.7%, 20.1%] | HOLDS |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**Baselines (held-out-repo split, calibrated identically)**

| method | α | τ | coverage | risk | verdict |
|---|---|---|---|---|---|
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_plugin_rate | 0.05 | 0.67 | 55.9% | 3.9% | HOLDS |
| difficulty_plugin_rate | 0.1 | 0.33 | 60.3% | 8.1% | HOLDS |
| difficulty_plugin_rate | 0.2 | 0.33 | 60.3% | 8.1% | HOLDS |
| always_submit | 0.05 | — | 100.0% | 44.6% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 44.6% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 44.6% | BREAKS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 6813, "0.6666666666666666": 908, "1.0": 799}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | 1.000 | 362 | 8.5% | 22.4% |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | 1.000 | 7.9% | 24.0% |

## v1.1_sweagent_qwen36_27b_swe-rebench-v2

`v1.1 sweagent qwen36_27b swe-rebench-v2` · K=3 · issues 5580 · repos 1719 · resolved rate 42.0% · agreement levels {"0.3333333333333333": 4733, "0.6666666666666666": 541, "1.0": 306} · same-cluster label disagreement 0.8%


**random_issue** (calib 2796 / eval 2784)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**heldout_repo** (calib 2790 / eval 2790)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**temporal** (calib 3058 / eval 2522)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**Baselines (held-out-repo split, calibrated identically)**

| method | α | τ | coverage | risk | verdict |
|---|---|---|---|---|---|
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_plugin_rate | 0.05 | 1.00 | 34.9% | 0.0% | HOLDS |
| difficulty_plugin_rate | 0.1 | 0.67 | 42.7% | 6.0% | HOLDS |
| difficulty_plugin_rate | 0.2 | 0.33 | 48.5% | 12.9% | HOLDS |
| always_submit | 0.05 | — | 100.0% | 57.7% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 57.7% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 57.7% | BREAKS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 4528, "0.6666666666666666": 600, "1.0": 452}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

## v1.2_minisweagent_qwen38_27b_scale-swe

`v1.2 minisweagent qwen38_27b scale-swe` · K=3 · issues 13801 · repos 1081 · resolved rate 59.4% · agreement levels {"0.3333333333333333": 12059, "0.6666666666666666": 995, "1.0": 747} · same-cluster label disagreement 0.0%

Temporal split not applicable for 13801 issues (no timestamps).


**random_issue** (calib 6909 / eval 6892)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**heldout_repo** (calib 6901 / eval 6900)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | 1.000 | 385 | 5.6% | 16.4% | [12.4%, 20.6%] | HOLDS |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**Baselines (held-out-repo split, calibrated identically)**

| method | α | τ | coverage | risk | verdict |
|---|---|---|---|---|---|
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_plugin_rate | 0.05 | 0.67 | 60.8% | 3.0% | HOLDS |
| difficulty_plugin_rate | 0.1 | 0.33 | 65.5% | 7.5% | HOLDS |
| difficulty_plugin_rate | 0.2 | 0.33 | 65.5% | 7.5% | HOLDS |
| always_submit | 0.05 | — | 100.0% | 39.4% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 39.4% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 39.4% | BREAKS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 11850, "0.6666666666666666": 1090, "1.0": 861}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | 1.000 | 423 | 6.1% | 20.1% |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | 1.000 | 5.4% | 27.1% |

## v1.2_minisweagent_qwen38_27b_swe-rebench-v2

`v1.2 minisweagent qwen38_27b swe-rebench-v2` · K=3 · issues 10563 · repos 2180 · resolved rate 50.9% · agreement levels {"0.3333333333333333": 9204, "0.6666666666666666": 757, "1.0": 602} · same-cluster label disagreement 0.6%


**random_issue** (calib 5274 / eval 5289)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**heldout_repo** (calib 5282 / eval 5281)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**temporal** (calib 5938 / eval 4625)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**Baselines (held-out-repo split, calibrated identically)**

| method | α | τ | coverage | risk | verdict |
|---|---|---|---|---|---|
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_plugin_rate | 0.05 | 1.00 | 42.5% | 0.0% | HOLDS |
| difficulty_plugin_rate | 0.1 | 0.67 | 49.4% | 4.7% | HOLDS |
| difficulty_plugin_rate | 0.2 | 0.33 | 55.2% | 10.9% | HOLDS |
| always_submit | 0.05 | — | 100.0% | 50.8% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 50.8% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 50.8% | BREAKS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 8669, "1.0": 1004, "0.6666666666666666": 890}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

## nebius@K8

`nebius OpenHands v0.54.0 + Qwen3-Coder-480B` · K=8 · issues 4580 · repos 1544 · resolved rate 47.2% · agreement levels {"0.125": 3478, "0.25": 446, "0.375": 242, "0.5": 172, "0.625": 120, "0.75": 91, "0.875": 20, "1.0": 11} · same-cluster label disagreement 0.0%

Truncation: max-iteration rows 8.9%, non-submit rows 9.4%.


**random_issue** (calib 2335 / eval 2245)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**heldout_repo** (calib 2290 / eval 2290)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**temporal** (calib 3080 / eval 1500)

| α | τ | submitted | coverage | risk | 95% CI (repo-clustered) | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

*secondary signal — files-touched agreement*

| α | τ | submitted | coverage | risk | verdict |
|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | NO-COVERAGE |

**Baselines (held-out-repo split, calibrated identically)**

| method | α | τ | coverage | risk | verdict |
|---|---|---|---|---|---|
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_plugin_rate | 0.05 | 0.88 | 41.5% | 2.8% | HOLDS |
| difficulty_plugin_rate | 0.1 | 0.75 | 45.4% | 5.7% | HOLDS |
| difficulty_plugin_rate | 0.2 | 0.50 | 51.0% | 10.3% | HOLDS |
| always_submit | 0.05 | — | 100.0% | 52.3% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 52.3% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 52.3% | BREAKS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.125": 2728, "0.25": 544, "0.375": 315, "0.5": 247, "1.0": 219, "0.625": 204, "0.75": 171, "0.875": 152}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

## Sanity gate (in-distribution split must hold risk ≤ α)

| config | α | random-issue risk | ≤ α? |
|---|---|---|---|
| nebius_openhands | 0.05 | — | n/a (no certified τ) |
| nebius_openhands | 0.1 | — | n/a (no certified τ) |
| nebius_openhands | 0.2 | — | n/a (no certified τ) |
| v1.0_openhands_minimax_m25_swe-rebench-v2 | 0.05 | — | n/a (no certified τ) |
| v1.0_openhands_minimax_m25_swe-rebench-v2 | 0.1 | — | n/a (no certified τ) |
| v1.0_openhands_minimax_m25_swe-rebench-v2 | 0.2 | — | n/a (no certified τ) |
| v1.0_openhands_qwen35_122b_swe-rebench-v2 | 0.05 | — | n/a (no certified τ) |
| v1.0_openhands_qwen35_122b_swe-rebench-v2 | 0.1 | — | n/a (no certified τ) |
| v1.0_openhands_qwen35_122b_swe-rebench-v2 | 0.2 | — | n/a (no certified τ) |
| v1.0_sweagent_minimax_m25_swe-rebench-v2 | 0.05 | — | n/a (no certified τ) |
| v1.0_sweagent_minimax_m25_swe-rebench-v2 | 0.1 | — | n/a (no certified τ) |
| v1.0_sweagent_minimax_m25_swe-rebench-v2 | 0.2 | — | n/a (no certified τ) |
| v1.0_sweagent_qwen35_122b_swe-rebench-v2 | 0.05 | — | n/a (no certified τ) |
| v1.0_sweagent_qwen35_122b_swe-rebench-v2 | 0.1 | — | n/a (no certified τ) |
| v1.0_sweagent_qwen35_122b_swe-rebench-v2 | 0.2 | — | n/a (no certified τ) |
| v1.1_minisweagent_qwen36_27b_scale-swe | 0.05 | — | n/a (no certified τ) |
| v1.1_minisweagent_qwen36_27b_scale-swe | 0.1 | — | n/a (no certified τ) |
| v1.1_minisweagent_qwen36_27b_scale-swe | 0.2 | — | n/a (no certified τ) |
| v1.1_minisweagent_qwen36_27b_swe-rebench-v2 | 0.05 | — | n/a (no certified τ) |
| v1.1_minisweagent_qwen36_27b_swe-rebench-v2 | 0.1 | — | n/a (no certified τ) |
| v1.1_minisweagent_qwen36_27b_swe-rebench-v2 | 0.2 | — | n/a (no certified τ) |
| v1.1_sweagent_qwen36_27b_scale-swe | 0.05 | — | n/a (no certified τ) |
| v1.1_sweagent_qwen36_27b_scale-swe | 0.1 | — | n/a (no certified τ) |
| v1.1_sweagent_qwen36_27b_scale-swe | 0.2 | 14.0% | yes (risk ≤ α) |
| v1.1_sweagent_qwen36_27b_swe-rebench-v2 | 0.05 | — | n/a (no certified τ) |
| v1.1_sweagent_qwen36_27b_swe-rebench-v2 | 0.1 | — | n/a (no certified τ) |
| v1.1_sweagent_qwen36_27b_swe-rebench-v2 | 0.2 | — | n/a (no certified τ) |
| v1.2_minisweagent_qwen38_27b_scale-swe | 0.05 | — | n/a (no certified τ) |
| v1.2_minisweagent_qwen38_27b_scale-swe | 0.1 | — | n/a (no certified τ) |
| v1.2_minisweagent_qwen38_27b_scale-swe | 0.2 | — | n/a (no certified τ) |
| v1.2_minisweagent_qwen38_27b_swe-rebench-v2 | 0.05 | — | n/a (no certified τ) |
| v1.2_minisweagent_qwen38_27b_swe-rebench-v2 | 0.1 | — | n/a (no certified τ) |
| v1.2_minisweagent_qwen38_27b_swe-rebench-v2 | 0.2 | — | n/a (no certified τ) |
| nebius@K8 | 0.05 | — | n/a (no certified τ) |
| nebius@K8 | 0.1 | — | n/a (no certified τ) |
| nebius@K8 | 0.2 | — | n/a (no certified τ) |

Failures: 0 of the cells that could be checked. Any failure would mark the pipeline suspect before held-out verdicts are trusted; cells with no certified τ are untestable, not passes.


## Post-hoc descriptive diagnostics (DEVIATIONS D5 — no decision uses these)

Error rate by agreement level over all units of each config (1 = failed), i.e. what the rule would see with unlimited calibration data. This is not a pre-registered endpoint.

| config | base error | a=1/3 | a=2/3 | a=1 | τ=1 calib error | τ=1 held-out-repo error |
|---|---|---|---|---|---|---|
| nebius_openhands | 53.0% | 55.0% (n=5504) | 33.3% (n=438) | 29.8% (n=121) | 23.5% | 34.3% |
| v1.0_openhands_minimax_m25_swe-rebench-v2 | 54.2% | 56.4% (n=6071) | 45.0% (n=825) | 43.9% (n=567) | 41.2% | 46.6% |
| v1.0_openhands_qwen35_122b_swe-rebench-v2 | 68.8% | 71.4% (n=5343) | 45.8% (n=400) | 46.3% (n=216) | 47.0% | 45.7% |
| v1.0_sweagent_minimax_m25_swe-rebench-v2 | 50.5% | 54.6% (n=6888) | 35.1% (n=968) | 28.2% (n=610) | 29.6% | 26.9% |
| v1.0_sweagent_qwen35_122b_swe-rebench-v2 | 49.0% | 50.9% (n=2229) | 32.3% (n=155) | 33.0% (n=106) | 28.8% | 37.0% |
| v1.1_minisweagent_qwen36_27b_scale-swe | 60.9% | 63.6% (n=7651) | 53.6% (n=780) | 18.2% (n=352) | 22.6% | 14.4% |
| v1.1_minisweagent_qwen36_27b_swe-rebench-v2 | 62.2% | 65.2% (n=10052) | 47.0% (n=1169) | 47.5% (n=852) | 48.6% | 46.4% |
| v1.1_sweagent_qwen36_27b_scale-swe | 43.6% | 48.6% (n=7042) | 24.4% (n=802) | 14.3% (n=676) | 13.2% | 15.8% |
| v1.1_sweagent_qwen36_27b_swe-rebench-v2 | 58.1% | 60.4% (n=4733) | 45.5% (n=541) | 44.1% (n=306) | 45.3% | 43.3% |
| v1.2_minisweagent_qwen38_27b_scale-swe | 40.6% | 43.9% (n=12059) | 19.2% (n=995) | 15.8% (n=747) | 15.2% | 16.4% |
| v1.2_minisweagent_qwen38_27b_swe-rebench-v2 | 49.1% | 50.5% (n=9204) | 38.8% (n=757) | 40.9% (n=602) | 41.6% | 40.2% |

**Conditional check** — within units whose 3 samples contain exactly 2 successes (`rate=2/3`), does agreement still separate errors? (Direct probe of 'agreement is difficulty in disguise'.)

| config | error at a=1/3 | error at a=2/3 |
|---|---|---|
| nebius_openhands | 39.7% (n=481) | 0.0% (n=11) |
| v1.0_openhands_minimax_m25_swe-rebench-v2 | 37.3% (n=523) | 0.0% (n=42) |
| v1.0_openhands_qwen35_122b_swe-rebench-v2 | 39.5% (n=512) | 0.0% (n=51) |
| v1.0_sweagent_minimax_m25_swe-rebench-v2 | 41.2% (n=699) | 0.0% (n=57) |
| v1.0_sweagent_qwen35_122b_swe-rebench-v2 | 38.1% (n=215) | 7.7% (n=13) |
| v1.1_minisweagent_qwen36_27b_scale-swe | 29.5% (n=430) | 3.5% (n=29) |
| v1.1_minisweagent_qwen36_27b_swe-rebench-v2 | 36.4% (n=772) | 12.3% (n=73) |
| v1.1_sweagent_qwen36_27b_scale-swe | 38.4% (n=430) | 0.0% (n=42) |
| v1.1_sweagent_qwen36_27b_swe-rebench-v2 | 34.4% (n=366) | 18.4% (n=38) |
| v1.2_minisweagent_qwen38_27b_scale-swe | 37.3% (n=684) | 2.6% (n=38) |
| v1.2_minisweagent_qwen38_27b_swe-rebench-v2 | 35.0% (n=665) | 13.0% (n=54) |

Note: this conditional table is confounded with DEVIATIONS D1 — when the labels are known, the agreeing pair is often the resolved pair, so part of the separation is mechanical rather than evidence that agreement is independent of difficulty.

