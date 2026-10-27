# KILL_TEST — pre-registered agreement-based abstention, calibrated → held-out

Command: `.venv/bin/python scripts/kill_test.py` · raw numbers: [results/kill_test.json](results/kill_test.json) · rules: [PREREG.md](PREREG.md), [DEVIATIONS.md](DEVIATIONS.md) (D6/D7 fix how this file reports)

Label convention: `resolved = -1` (unknown, nvidia only) is shown **both ways** — dropped from the pool before sampling, and counted as failure — for every arm. The two columns are two complete pipelines (they differ in pool eligibility as well as in labelling), each with its own τ, interval and verdict. Neither is primary here.


## Bottom line

- **0 BREAKS; 2 arms testable; sensitive to the `-1` convention.** (0 BREAKS in 198 pre-registered cells = arms × splits × α × label conventions; "testable" counts arms that certify a τ at any α, all of them at α=0.20 only; `NO-COVERAGE` is not a pass.)
- α=0.05: drop-`-1` 0/12 arms certify a τ, 0 BREAKS; `-1`-as-failure 0/12 arms certify a τ, 0 BREAKS.
- α=0.1: drop-`-1` 0/12 arms certify a τ, 0 BREAKS; `-1`-as-failure 0/12 arms certify a τ, 0 BREAKS.
- α=0.2: drop-`-1` 2/12 arms certify a τ, 0 BREAKS; `-1`-as-failure 0/12 arms certify a τ, 0 BREAKS.
- At α=0.20 (drop-`-1`) the certified cells have coverage 5.6%–7.1% and held-out-repo risk 15.8%–16.4% vs α=20%.
- **Same τ, other label set:** re-scoring the certified rule with `resolved=-1` as failure (confounded with the sampling change — different pool, see below) raises held-out risk above α=20% in every certified cell (`v1.1_sweagent_qwen36_27b_scale-swe` 15.8% → 24.0%; `v1.2_minisweagent_qwen38_27b_scale-swe` 16.4% → 27.1%). The guarantee therefore depends on which convention you accept as correct.
- difficulty_cross_fit at α=0.20: certifies in 12/12 arms, coverage 27.1%–63.9%, held-out risk 4.4%–15.2%. It needs the labels of the other K−1 attempts, which in deployment means running the tests on those attempts first.
- difficulty_plugin_rate (oracle) at α=0.20: certifies in 12/12 arms, coverage 33.1%–65.5%, held-out risk 3.9%–14.6%. This row includes the scored label, so its coverage and risk are not achievable by any deployable signal; it is reported only as a ceiling.
- The binding constraint is power, not calibration breakage: exact patch identity is rare (see DATA_RECON/claims C35–C38), so the unanimous subset is small and its error is only sometimes low enough for Clopper–Pearson to certify α. `NO-COVERAGE` cells carry no risk estimate and are reported as such, not as passes.

## Verdicts (headline split = held-out-repo, per config, both label conventions)

| config | issues (drop / −1=fail) | base error (drop / −1=fail) | α=0.05 drop | α=0.05 −1=fail | α=0.1 drop | α=0.1 −1=fail | α=0.2 drop | α=0.2 −1=fail |
|---|---|---|---|---|---|---|---|---|
| nebius_openhands | 6063 / 6063 | 53.0% / 53.0% | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) |
| v1.0_openhands_minimax_m25_swe-rebench-v2 | 7463 / 9570 | 54.2% / 64.0% | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) |
| v1.0_openhands_qwen35_122b_swe-rebench-v2 | 5959 / 7880 | 68.8% / 76.3% | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) |
| v1.0_sweagent_minimax_m25_swe-rebench-v2 | 8466 / 11020 | 50.5% / 61.8% | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) |
| v1.0_sweagent_qwen35_122b_swe-rebench-v2 | 2490 / 3430 | 49.0% / 62.7% | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) |
| v1.1_minisweagent_qwen36_27b_scale-swe | 8783 / 9904 | 60.9% / 65.3% | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) |
| v1.1_minisweagent_qwen36_27b_swe-rebench-v2 | 12073 / 13849 | 62.2% / 66.2% | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) |
| v1.1_sweagent_qwen36_27b_scale-swe | 8520 / 9537 | 43.6% / 49.6% | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | HOLDS (7.1%, 15.8%) | NO-COVERAGE (—, —) |
| v1.1_sweagent_qwen36_27b_swe-rebench-v2 | 5580 / 6377 | 58.0% / 62.1% | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) |
| v1.2_minisweagent_qwen38_27b_scale-swe | 13801 / 15509 | 40.6% / 47.1% | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | HOLDS (5.6%, 16.4%) | NO-COVERAGE (—, —) |
| v1.2_minisweagent_qwen38_27b_swe-rebench-v2 | 10563 / 12151 | 49.1% / 54.1% | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) |
| nebius@K8 | 4580 / 4580 | 52.8% / 52.8% | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) | NO-COVERAGE (—, —) |

Cells are `VERDICT (coverage, selective risk)`. BREAKS = repo-clustered lower CI bound > α + 0.05; HOLDS = otherwise; NO-COVERAGE = no τ certified on calibration (not a pass). The `−1`-as-failure columns are separate certifications on a larger pool, not re-scores of the drop-`-1` rule; the re-score is reported per config below.


## nebius_openhands

`nebius OpenHands v0.54.0 + Qwen3-Coder-480B` · K=3 · convention `resolved=-1 dropped (PREREG primary)` · issues 6063 · repos 1809 · resolved rate 47.0% · agreement levels {"0.3333333333333333": 5504, "0.6666666666666666": 438, "1.0": 121} · same-cluster label disagreement 0.0%

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
| always_submit | 0.05 | — | 100.0% | 53.5% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 53.5% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 53.5% | BREAKS |
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.05 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.1 | 0.667 | 42.5% | 7.6% | HOLDS |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.2 | 0.333 | 51.9% | 15.1% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.05 | 1.000 | 39.3% | 0.0% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.1 | 0.667 | 47.3% | 6.8% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.2 | 0.333 | 54.3% | 14.4% | HOLDS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 4691, "0.6666666666666666": 800, "1.0": 572}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ (same rule re-scored, different sample pool)**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

**Alternative convention (`resolved=-1` as failure) — full certification, held-out-repo split**

own pool: issues 6063 · repos 1809 · base error 53.0% · agreement levels {"0.3333333333333333": 5504, "0.6666666666666666": 438, "1.0": 121}. Its other splits and `always_submit` numbers are in results/kill_test.json.

| α | τ | submitted | coverage | risk | 95% CI | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

## v1.0_openhands_minimax_m25_swe-rebench-v2

`v1.0 openhands minimax_m25 swe-rebench-v2` · K=3 · convention `resolved=-1 dropped (PREREG primary)` · issues 7463 · repos 1846 · resolved rate 45.8% · agreement levels {"0.3333333333333333": 6071, "0.6666666666666666": 825, "1.0": 567} · same-cluster label disagreement 0.0%


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
| always_submit | 0.05 | — | 100.0% | 54.7% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 54.7% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 54.7% | BREAKS |
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.05 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.1 | 0.667 | 42.1% | 7.0% | HOLDS |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.2 | 0.333 | 50.5% | 13.7% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.05 | 1.000 | 39.1% | 0.0% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.1 | 0.667 | 46.6% | 6.3% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.2 | 0.333 | 52.3% | 13.3% | HOLDS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 5717, "0.6666666666666666": 937, "1.0": 809}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ (same rule re-scored, different sample pool)**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

**Alternative convention (`resolved=-1` as failure) — full certification, held-out-repo split**

own pool: issues 9570 · repos 2145 · base error 64.0% · agreement levels {"0.3333333333333333": 7770, "0.6666666666666666": 1052, "1.0": 748}. Its other splits and `always_submit` numbers are in results/kill_test.json.

| α | τ | submitted | coverage | risk | 95% CI | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

## v1.0_openhands_qwen35_122b_swe-rebench-v2

`v1.0 openhands qwen35_122b swe-rebench-v2` · K=3 · convention `resolved=-1 dropped (PREREG primary)` · issues 5959 · repos 1669 · resolved rate 31.2% · agreement levels {"0.3333333333333333": 5343, "0.6666666666666666": 400, "1.0": 216} · same-cluster label disagreement 0.0%


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
| always_submit | 0.05 | — | 100.0% | 68.2% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 68.2% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 68.2% | BREAKS |
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.05 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.1 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.2 | 0.667 | 27.1% | 13.6% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.05 | 1.000 | 23.4% | 0.0% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.1 | 1.000 | 23.4% | 0.0% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.2 | 0.667 | 33.1% | 11.2% | HOLDS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 4987, "0.6666666666666666": 527, "1.0": 445}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ (same rule re-scored, different sample pool)**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

**Alternative convention (`resolved=-1` as failure) — full certification, held-out-repo split**

own pool: issues 7880 · repos 1961 · base error 76.3% · agreement levels {"0.3333333333333333": 7110, "0.6666666666666666": 509, "1.0": 261}. Its other splits and `always_submit` numbers are in results/kill_test.json.

| α | τ | submitted | coverage | risk | 95% CI | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

## v1.0_sweagent_minimax_m25_swe-rebench-v2

`v1.0 sweagent minimax_m25 swe-rebench-v2` · K=3 · convention `resolved=-1 dropped (PREREG primary)` · issues 8466 · repos 1859 · resolved rate 49.5% · agreement levels {"0.3333333333333333": 6888, "0.6666666666666666": 968, "1.0": 610} · same-cluster label disagreement 0.1%


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
| always_submit | 0.05 | — | 100.0% | 50.2% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 50.2% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 50.2% | BREAKS |
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.05 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.1 | 0.667 | 45.3% | 7.5% | HOLDS |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.2 | 0.333 | 55.5% | 14.1% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.05 | 1.000 | 41.9% | 0.0% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.1 | 0.667 | 51.0% | 6.6% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.2 | 0.333 | 57.6% | 13.6% | HOLDS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 6554, "0.6666666666666666": 1087, "1.0": 825}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ (same rule re-scored, different sample pool)**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

**Alternative convention (`resolved=-1` as failure) — full certification, held-out-repo split**

own pool: issues 11020 · repos 2157 · base error 61.8% · agreement levels {"0.3333333333333333": 8955, "0.6666666666666666": 1251, "1.0": 814}. Its other splits and `always_submit` numbers are in results/kill_test.json.

| α | τ | submitted | coverage | risk | 95% CI | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

## v1.0_sweagent_qwen35_122b_swe-rebench-v2

`v1.0 sweagent qwen35_122b swe-rebench-v2` · K=3 · convention `resolved=-1 dropped (PREREG primary)` · issues 2490 · repos 984 · resolved rate 51.0% · agreement levels {"0.3333333333333333": 2229, "0.6666666666666666": 155, "1.0": 106} · same-cluster label disagreement 0.1%


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
| always_submit | 0.05 | — | 100.0% | 49.6% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 49.6% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 49.6% | BREAKS |
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.05 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.1 | 0.667 | 44.9% | 6.8% | HOLDS |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.2 | 0.333 | 56.7% | 14.9% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.05 | 1.000 | 41.8% | 0.0% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.1 | 0.667 | 51.3% | 5.9% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.2 | 0.333 | 58.9% | 14.3% | HOLDS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 2221, "0.6666666666666666": 162, "1.0": 107}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ (same rule re-scored, different sample pool)**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

**Alternative convention (`resolved=-1` as failure) — full certification, held-out-repo split**

own pool: issues 3430 · repos 1223 · base error 62.7% · agreement levels {"0.3333333333333333": 3079, "0.6666666666666666": 214, "1.0": 137}. Its other splits and `always_submit` numbers are in results/kill_test.json.

| α | τ | submitted | coverage | risk | 95% CI | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

## v1.1_minisweagent_qwen36_27b_scale-swe

`v1.1 minisweagent qwen36_27b scale-swe` · K=3 · convention `resolved=-1 dropped (PREREG primary)` · issues 8783 · repos 963 · resolved rate 39.1% · agreement levels {"0.3333333333333333": 7651, "0.6666666666666666": 780, "1.0": 352} · same-cluster label disagreement 0.2%

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
| always_submit | 0.05 | — | 100.0% | 60.4% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 60.4% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 60.4% | BREAKS |
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.05 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.1 | 0.667 | 30.1% | 4.4% | HOLDS |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.2 | 0.667 | 30.1% | 4.4% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.05 | 1.000 | 28.8% | 0.0% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.1 | 0.667 | 34.1% | 3.9% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.2 | 0.667 | 34.1% | 3.9% | HOLDS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 7447, "0.6666666666666666": 875, "1.0": 461}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ (same rule re-scored, different sample pool)**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

**Alternative convention (`resolved=-1` as failure) — full certification, held-out-repo split**

own pool: issues 9904 · repos 1009 · base error 65.3% · agreement levels {"0.3333333333333333": 8650, "0.6666666666666666": 868, "1.0": 386}. Its other splits and `always_submit` numbers are in results/kill_test.json.

| α | τ | submitted | coverage | risk | 95% CI | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

## v1.1_minisweagent_qwen36_27b_swe-rebench-v2

`v1.1 minisweagent qwen36_27b swe-rebench-v2` · K=3 · convention `resolved=-1 dropped (PREREG primary)` · issues 12073 · repos 2278 · resolved rate 37.8% · agreement levels {"0.3333333333333333": 10052, "0.6666666666666666": 1169, "1.0": 852} · same-cluster label disagreement 0.7%


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
| always_submit | 0.05 | — | 100.0% | 61.1% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 61.1% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 61.1% | BREAKS |
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.05 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.1 | 0.667 | 34.7% | 7.3% | HOLDS |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.2 | 0.333 | 43.6% | 15.2% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.05 | 1.000 | 32.1% | 0.0% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.1 | 0.667 | 39.5% | 6.4% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.2 | 0.333 | 45.5% | 14.6% | HOLDS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 9465, "0.6666666666666666": 1338, "1.0": 1270}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ (same rule re-scored, different sample pool)**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

**Alternative convention (`resolved=-1` as failure) — full certification, held-out-repo split**

own pool: issues 13849 · repos 2367 · base error 66.2% · agreement levels {"0.3333333333333333": 11539, "0.6666666666666666": 1355, "1.0": 955}. Its other splits and `always_submit` numbers are in results/kill_test.json.

| α | τ | submitted | coverage | risk | 95% CI | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

## v1.1_sweagent_qwen36_27b_scale-swe

`v1.1 sweagent qwen36_27b scale-swe` · K=3 · convention `resolved=-1 dropped (PREREG primary)` · issues 8520 · repos 961 · resolved rate 56.4% · agreement levels {"0.3333333333333333": 7042, "0.6666666666666666": 802, "1.0": 676} · same-cluster label disagreement 0.0%

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
| always_submit | 0.05 | — | 100.0% | 44.6% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 44.6% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 44.6% | BREAKS |
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.05 | 0.667 | 52.1% | 4.2% | HOLDS |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.1 | 0.333 | 58.6% | 8.3% | HOLDS |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.2 | 0.333 | 58.6% | 8.3% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.05 | 0.667 | 55.9% | 3.9% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.1 | 0.333 | 60.3% | 8.1% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.2 | 0.333 | 60.3% | 8.1% | HOLDS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 6813, "0.6666666666666666": 908, "1.0": 799}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | 1.000 | 362 | 8.5% | 22.4% |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ (same rule re-scored, different sample pool)**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | 1.000 | 7.9% | 24.0% |

**Alternative convention (`resolved=-1` as failure) — full certification, held-out-repo split**

own pool: issues 9537 · repos 1009 · base error 49.6% · agreement levels {"0.3333333333333333": 7921, "0.6666666666666666": 873, "1.0": 743}. Its other splits and `always_submit` numbers are in results/kill_test.json.

| α | τ | submitted | coverage | risk | 95% CI | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

## v1.1_sweagent_qwen36_27b_swe-rebench-v2

`v1.1 sweagent qwen36_27b swe-rebench-v2` · K=3 · convention `resolved=-1 dropped (PREREG primary)` · issues 5580 · repos 1719 · resolved rate 42.0% · agreement levels {"0.3333333333333333": 4733, "0.6666666666666666": 541, "1.0": 306} · same-cluster label disagreement 0.8%


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
| always_submit | 0.05 | — | 100.0% | 57.7% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 57.7% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 57.7% | BREAKS |
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.05 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.1 | 0.667 | 37.5% | 6.9% | HOLDS |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.2 | 0.333 | 46.3% | 13.5% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.05 | 1.000 | 34.9% | 0.0% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.1 | 0.667 | 42.7% | 6.0% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.2 | 0.333 | 48.5% | 12.9% | HOLDS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 4528, "0.6666666666666666": 600, "1.0": 452}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ (same rule re-scored, different sample pool)**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

**Alternative convention (`resolved=-1` as failure) — full certification, held-out-repo split**

own pool: issues 6377 · repos 1812 · base error 62.1% · agreement levels {"0.3333333333333333": 5443, "0.6666666666666666": 597, "1.0": 337}. Its other splits and `always_submit` numbers are in results/kill_test.json.

| α | τ | submitted | coverage | risk | 95% CI | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

## v1.2_minisweagent_qwen38_27b_scale-swe

`v1.2 minisweagent qwen38_27b scale-swe` · K=3 · convention `resolved=-1 dropped (PREREG primary)` · issues 13801 · repos 1081 · resolved rate 59.4% · agreement levels {"0.3333333333333333": 12059, "0.6666666666666666": 995, "1.0": 747} · same-cluster label disagreement 0.0%

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
| always_submit | 0.05 | — | 100.0% | 39.4% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 39.4% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 39.4% | BREAKS |
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.05 | 0.667 | 57.4% | 3.2% | HOLDS |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.1 | 0.333 | 63.9% | 7.7% | HOLDS |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.2 | 0.333 | 63.9% | 7.7% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.05 | 0.667 | 60.8% | 3.0% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.1 | 0.333 | 65.5% | 7.5% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.2 | 0.333 | 65.5% | 7.5% | HOLDS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 11850, "0.6666666666666666": 1090, "1.0": 861}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | 1.000 | 423 | 6.1% | 20.1% |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ (same rule re-scored, different sample pool)**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | 1.000 | 5.4% | 27.1% |

**Alternative convention (`resolved=-1` as failure) — full certification, held-out-repo split**

own pool: issues 15509 · repos 1131 · base error 47.1% · agreement levels {"0.3333333333333333": 13577, "0.6666666666666666": 1101, "1.0": 831}. Its other splits and `always_submit` numbers are in results/kill_test.json.

| α | τ | submitted | coverage | risk | 95% CI | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

## v1.2_minisweagent_qwen38_27b_swe-rebench-v2

`v1.2 minisweagent qwen38_27b swe-rebench-v2` · K=3 · convention `resolved=-1 dropped (PREREG primary)` · issues 10563 · repos 2180 · resolved rate 50.9% · agreement levels {"0.3333333333333333": 9204, "0.6666666666666666": 757, "1.0": 602} · same-cluster label disagreement 0.6%


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
| always_submit | 0.05 | — | 100.0% | 50.8% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 50.8% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 50.8% | BREAKS |
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.05 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.1 | 0.667 | 44.8% | 5.2% | HOLDS |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.2 | 0.333 | 53.2% | 11.3% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.05 | 1.000 | 42.5% | 0.0% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.1 | 0.667 | 49.4% | 4.7% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.2 | 0.333 | 55.2% | 10.9% | HOLDS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.3333333333333333": 8669, "1.0": 1004, "0.6666666666666666": 890}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ (same rule re-scored, different sample pool)**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

**Alternative convention (`resolved=-1` as failure) — full certification, held-out-repo split**

own pool: issues 12151 · repos 2285 · base error 54.1% · agreement levels {"0.3333333333333333": 10569, "0.6666666666666666": 892, "1.0": 690}. Its other splits and `always_submit` numbers are in results/kill_test.json.

| α | τ | submitted | coverage | risk | 95% CI | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

## nebius@K8

`nebius OpenHands v0.54.0 + Qwen3-Coder-480B` · K=8 · convention `resolved=-1 dropped (PREREG primary)` · issues 4580 · repos 1544 · resolved rate 47.2% · agreement levels {"0.125": 3478, "0.25": 446, "0.375": 242, "0.5": 172, "0.625": 120, "0.75": 91, "0.875": 20, "1.0": 11} · same-cluster label disagreement 0.0%

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
| always_submit | 0.05 | — | 100.0% | 52.3% | BREAKS |
| always_submit | 0.1 | — | 100.0% | 52.3% | BREAKS |
| always_submit | 0.2 | — | 100.0% | 52.3% | BREAKS |
| patch_size | 0.05 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.1 | — | 0.0% | — | NO-COVERAGE |
| patch_size | 0.2 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.05 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.1 | — | 0.0% | — | NO-COVERAGE |
| step_count | 0.2 | — | 0.0% | — | NO-COVERAGE |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.05 | 0.875 | 36.6% | 3.2% | HOLDS |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.1 | 0.750 | 42.9% | 6.0% | HOLDS |
| difficulty_cross_fit — HONEST (rate of the other K−1 attempts) | 0.2 | 0.500 | 49.8% | 10.5% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.05 | 0.875 | 41.5% | 2.8% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.1 | 0.750 | 45.4% | 5.7% | HOLDS |
| difficulty_plugin_rate — ORACLE CEILING (includes the scored label) | 0.2 | 0.500 | 51.0% | 10.3% | HOLDS |

**Sensitivity — F1 canonicalisation (new-file sections dropped), at the primary τ**

F1 agreement levels: `{"0.125": 2728, "0.25": 544, "0.375": 315, "0.5": 247, "1.0": 219, "0.625": 204, "0.75": 171, "0.875": 152}`

| α | τ | submitted | coverage | risk |
|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — |
| 0.1 | — | 0 | 0.0% | — |
| 0.2 | — | 0 | 0.0% | — |

**Sensitivity — `resolved=-1` counted as failure, at the primary τ (same rule re-scored, different sample pool)**

| α | τ | coverage | risk |
|---|---|---|---|
| 0.05 | — | 0.0% | — |
| 0.1 | — | 0.0% | — |
| 0.2 | — | 0.0% | — |

**Alternative convention (`resolved=-1` as failure) — full certification, held-out-repo split**

own pool: issues 4580 · repos 1544 · base error 52.8% · agreement levels {"0.125": 3478, "0.25": 446, "0.375": 242, "0.5": 172, "0.625": 120, "0.75": 91, "0.875": 20, "1.0": 11}. Its other splits and `always_submit` numbers are in results/kill_test.json.

| α | τ | submitted | coverage | risk | 95% CI | verdict |
|---|---|---|---|---|---|---|
| 0.05 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.1 | — | 0 | 0.0% | — | — | NO-COVERAGE |
| 0.2 | — | 0 | 0.0% | — | — | NO-COVERAGE |

## Sanity gate (in-distribution split must hold risk ≤ α)

| config | convention | α | random-issue risk | ≤ α? |
|---|---|---|---|---|
| nebius_openhands | drop | 0.05 | — | n/a (no certified τ) |
| nebius_openhands | drop | 0.1 | — | n/a (no certified τ) |
| nebius_openhands | drop | 0.2 | — | n/a (no certified τ) |
| nebius_openhands | minus1_failure | 0.05 | — | n/a (no certified τ) |
| nebius_openhands | minus1_failure | 0.1 | — | n/a (no certified τ) |
| nebius_openhands | minus1_failure | 0.2 | — | n/a (no certified τ) |
| v1.0_openhands_minimax_m25_swe-rebench-v2 | drop | 0.05 | — | n/a (no certified τ) |
| v1.0_openhands_minimax_m25_swe-rebench-v2 | drop | 0.1 | — | n/a (no certified τ) |
| v1.0_openhands_minimax_m25_swe-rebench-v2 | drop | 0.2 | — | n/a (no certified τ) |
| v1.0_openhands_minimax_m25_swe-rebench-v2 | minus1_failure | 0.05 | — | n/a (no certified τ) |
| v1.0_openhands_minimax_m25_swe-rebench-v2 | minus1_failure | 0.1 | — | n/a (no certified τ) |
| v1.0_openhands_minimax_m25_swe-rebench-v2 | minus1_failure | 0.2 | — | n/a (no certified τ) |
| v1.0_openhands_qwen35_122b_swe-rebench-v2 | drop | 0.05 | — | n/a (no certified τ) |
| v1.0_openhands_qwen35_122b_swe-rebench-v2 | drop | 0.1 | — | n/a (no certified τ) |
| v1.0_openhands_qwen35_122b_swe-rebench-v2 | drop | 0.2 | — | n/a (no certified τ) |
| v1.0_openhands_qwen35_122b_swe-rebench-v2 | minus1_failure | 0.05 | — | n/a (no certified τ) |
| v1.0_openhands_qwen35_122b_swe-rebench-v2 | minus1_failure | 0.1 | — | n/a (no certified τ) |
| v1.0_openhands_qwen35_122b_swe-rebench-v2 | minus1_failure | 0.2 | — | n/a (no certified τ) |
| v1.0_sweagent_minimax_m25_swe-rebench-v2 | drop | 0.05 | — | n/a (no certified τ) |
| v1.0_sweagent_minimax_m25_swe-rebench-v2 | drop | 0.1 | — | n/a (no certified τ) |
| v1.0_sweagent_minimax_m25_swe-rebench-v2 | drop | 0.2 | — | n/a (no certified τ) |
| v1.0_sweagent_minimax_m25_swe-rebench-v2 | minus1_failure | 0.05 | — | n/a (no certified τ) |
| v1.0_sweagent_minimax_m25_swe-rebench-v2 | minus1_failure | 0.1 | — | n/a (no certified τ) |
| v1.0_sweagent_minimax_m25_swe-rebench-v2 | minus1_failure | 0.2 | — | n/a (no certified τ) |
| v1.0_sweagent_qwen35_122b_swe-rebench-v2 | drop | 0.05 | — | n/a (no certified τ) |
| v1.0_sweagent_qwen35_122b_swe-rebench-v2 | drop | 0.1 | — | n/a (no certified τ) |
| v1.0_sweagent_qwen35_122b_swe-rebench-v2 | drop | 0.2 | — | n/a (no certified τ) |
| v1.0_sweagent_qwen35_122b_swe-rebench-v2 | minus1_failure | 0.05 | — | n/a (no certified τ) |
| v1.0_sweagent_qwen35_122b_swe-rebench-v2 | minus1_failure | 0.1 | — | n/a (no certified τ) |
| v1.0_sweagent_qwen35_122b_swe-rebench-v2 | minus1_failure | 0.2 | — | n/a (no certified τ) |
| v1.1_minisweagent_qwen36_27b_scale-swe | drop | 0.05 | — | n/a (no certified τ) |
| v1.1_minisweagent_qwen36_27b_scale-swe | drop | 0.1 | — | n/a (no certified τ) |
| v1.1_minisweagent_qwen36_27b_scale-swe | drop | 0.2 | — | n/a (no certified τ) |
| v1.1_minisweagent_qwen36_27b_scale-swe | minus1_failure | 0.05 | — | n/a (no certified τ) |
| v1.1_minisweagent_qwen36_27b_scale-swe | minus1_failure | 0.1 | — | n/a (no certified τ) |
| v1.1_minisweagent_qwen36_27b_scale-swe | minus1_failure | 0.2 | — | n/a (no certified τ) |
| v1.1_minisweagent_qwen36_27b_swe-rebench-v2 | drop | 0.05 | — | n/a (no certified τ) |
| v1.1_minisweagent_qwen36_27b_swe-rebench-v2 | drop | 0.1 | — | n/a (no certified τ) |
| v1.1_minisweagent_qwen36_27b_swe-rebench-v2 | drop | 0.2 | — | n/a (no certified τ) |
| v1.1_minisweagent_qwen36_27b_swe-rebench-v2 | minus1_failure | 0.05 | — | n/a (no certified τ) |
| v1.1_minisweagent_qwen36_27b_swe-rebench-v2 | minus1_failure | 0.1 | — | n/a (no certified τ) |
| v1.1_minisweagent_qwen36_27b_swe-rebench-v2 | minus1_failure | 0.2 | — | n/a (no certified τ) |
| v1.1_sweagent_qwen36_27b_scale-swe | drop | 0.05 | — | n/a (no certified τ) |
| v1.1_sweagent_qwen36_27b_scale-swe | drop | 0.1 | — | n/a (no certified τ) |
| v1.1_sweagent_qwen36_27b_scale-swe | drop | 0.2 | 14.0% | yes (risk ≤ α (τ=1.000)) |
| v1.1_sweagent_qwen36_27b_scale-swe | minus1_failure | 0.05 | — | n/a (no certified τ) |
| v1.1_sweagent_qwen36_27b_scale-swe | minus1_failure | 0.1 | — | n/a (no certified τ) |
| v1.1_sweagent_qwen36_27b_scale-swe | minus1_failure | 0.2 | — | n/a (no certified τ) |
| v1.1_sweagent_qwen36_27b_swe-rebench-v2 | drop | 0.05 | — | n/a (no certified τ) |
| v1.1_sweagent_qwen36_27b_swe-rebench-v2 | drop | 0.1 | — | n/a (no certified τ) |
| v1.1_sweagent_qwen36_27b_swe-rebench-v2 | drop | 0.2 | — | n/a (no certified τ) |
| v1.1_sweagent_qwen36_27b_swe-rebench-v2 | minus1_failure | 0.05 | — | n/a (no certified τ) |
| v1.1_sweagent_qwen36_27b_swe-rebench-v2 | minus1_failure | 0.1 | — | n/a (no certified τ) |
| v1.1_sweagent_qwen36_27b_swe-rebench-v2 | minus1_failure | 0.2 | — | n/a (no certified τ) |
| v1.2_minisweagent_qwen38_27b_scale-swe | drop | 0.05 | — | n/a (no certified τ) |
| v1.2_minisweagent_qwen38_27b_scale-swe | drop | 0.1 | — | n/a (no certified τ) |
| v1.2_minisweagent_qwen38_27b_scale-swe | drop | 0.2 | — | n/a (no certified τ) |
| v1.2_minisweagent_qwen38_27b_scale-swe | minus1_failure | 0.05 | — | n/a (no certified τ) |
| v1.2_minisweagent_qwen38_27b_scale-swe | minus1_failure | 0.1 | — | n/a (no certified τ) |
| v1.2_minisweagent_qwen38_27b_scale-swe | minus1_failure | 0.2 | — | n/a (no certified τ) |
| v1.2_minisweagent_qwen38_27b_swe-rebench-v2 | drop | 0.05 | — | n/a (no certified τ) |
| v1.2_minisweagent_qwen38_27b_swe-rebench-v2 | drop | 0.1 | — | n/a (no certified τ) |
| v1.2_minisweagent_qwen38_27b_swe-rebench-v2 | drop | 0.2 | — | n/a (no certified τ) |
| v1.2_minisweagent_qwen38_27b_swe-rebench-v2 | minus1_failure | 0.05 | — | n/a (no certified τ) |
| v1.2_minisweagent_qwen38_27b_swe-rebench-v2 | minus1_failure | 0.1 | — | n/a (no certified τ) |
| v1.2_minisweagent_qwen38_27b_swe-rebench-v2 | minus1_failure | 0.2 | — | n/a (no certified τ) |
| nebius@K8 | drop | 0.05 | — | n/a (no certified τ) |
| nebius@K8 | drop | 0.1 | — | n/a (no certified τ) |
| nebius@K8 | drop | 0.2 | — | n/a (no certified τ) |
| nebius@K8 | minus1_failure | 0.05 | — | n/a (no certified τ) |
| nebius@K8 | minus1_failure | 0.1 | — | n/a (no certified τ) |
| nebius@K8 | minus1_failure | 0.2 | — | n/a (no certified τ) |

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


## Leak checks (PREREG §8)

| check | result | source |
|---|---|---|
| duplicate (issue, trajectory) rows, nebius / nvidia | 0 / 0 | results/overlap_check.json |
| duplicate trajectory_id, nebius / nvidia | 0 / 0 | results/overlap_check.json |
| casefolded issue overlap between corpora | 204 issues (2202 nebius rows / 4692 nvidia rows) — excluded everywhere (D3) | results/overlap_check.json |
| issue overlap SWE-rebench V1 ∩ V2 (casefolded, same created_at) | 642 | results/overlap_check.json |
| excluded shared-issue list | 204 keys | results/excluded_shared_issues.csv |
| repo overlap across calibration/evaluation | 0 by construction; asserted for every config/split/convention in `scripts/kill_test.py::run_config` (`assert_no_repo_leak`) | scripts/kill_test.py |
| issue on both sides of any split | 0; asserted (`assert_single_side`) | scripts/kill_test.py |
| signal never touches labels | the agreement/files signals and both tie-breaks are computed before any label column is read; `rate_loo` (Part A3) excludes the scored attempt's own label by construction | scripts/kill_test.py::build_units |

