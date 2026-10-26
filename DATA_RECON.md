# DATA_RECON — Phase 0

Research question: does an agreement-based abstention rule calibrated on one set of repos keep its
target error rate on held-out repos, for SWE agents? (Hypothesis to break: "agreement is difficulty
in disguise".)

Phase 0 scope: schema, sample counts, labels, structure, joins, leak checks, signal availability.
**No outcome-vs-signal analysis was performed.** Every number below was computed from data read
directly out of the Hugging Face parquet files (range reads only, no full downloads).

Reproduce: `bash reproduce_recon.sh` (writes `out/` scratch caches + `results/` summaries).

## 0. TL;DR — the three facts that constrain the design

1. **nebius/SWE-rebench-openhands-trajectories is the only corpus with >3 trajectories per issue**
   (median 10, max 34): 6,306 issues, 1,823 repos, single config. K=8 → 4,737 issues.
2. **nvidia/Open-SWE-Traces has at most 3 trajectories per issue *per config*** (818,660 rows, 32
   configs). 20 of 32 configs have exactly **one** trajectory per issue, so agreement is undefined
   there. 10 configs support K=3 (3,477–15,509 issues each). No config supports K≥5.
3. **instance_id case convention differs between corpora**, so naive string joins report zero
   overlap. After casefolding: SWE-rebench V1 ∩ V2 = 642 issues (identical `created_at`, verified),
   and nebius trajectories ∩ nvidia = 204 issues. Overlap must be removed, not ignored.

## 1. Dataset cards and licenses

| dataset | rows | files | bytes (parquet) | license | last modified |
|---|---|---|---|---|---|
| nebius/SWE-rebench-openhands-trajectories | 67,074 | 1 | 2,079,503,354 | CC-BY-4.0 (card `license: cc-by-4.0`, HF tag) | 2025-12-27 |
| nvidia/Open-SWE-Traces | 818,660 | 346 | 78.47 GB | CC-BY-4.0 (card `license: cc-by-4.0`, HF tag) | 2026-10-23 |
| nebius/SWE-rebench (V1, provenance/timestamps only) | 27,878 rows = 21,336 instances | 3 | 245.2 MB | CC-BY-4.0 | — |
| nebius/SWE-rebench-V2 (provenance/timestamps only) | 32,079 | 1 | 428.8 MB | CC-BY-4.0 | — |
| AweAI-Team/Scale-SWE (provenance for nvidia Scale-SWE subset) | 20,181 | 1 JSONL | 984 MB | CC BY 4.0 stated in README badge only (**no HF license tag**) | — |

nvidia card: v1.0 = OpenHands(v0.53.0)+SWE-agent, v1.1 = +mini-swe-agent (DeepSeek-V4-Flash-0731,
Qwen3.6-27B), v1.2 = Qwen3.8-27B, v2.0 = Qwen3.8-Flash-Next (xhigh reasoning) across
OpenHands/SWE-agent/mini-swe-agent/Claude-Code/opencode. Card also states v1.0 was cleaned of "git
hacking" trajectories (151k kept of 207k).
nebius card: Qwen3-Coder-480B-A35B-Instruct with OpenHands v0.54.0; card claims 1,823 repos, 3,792
resolved issues, 67,074 trajectories, 32,161 successful, avg 64.3 turns.

## 2. Schemas (verified from parquet footers and row reads)

### nebius/SWE-rebench-openhands-trajectories (single file `trajectories.parquet`, 17 row groups)
| field | type | observed values |
|---|---|---|
| trajectory_id | string | uuid, unique (0 duplicates in 67,074) |
| instance_id | string | `Owner__repo-NNN` (owner case preserved) |
| repo | string | `Owner/repo` |
| trajectory | list<struct<content,name,role,tool_call_id,tool_calls>> | roles: system/user/assistant/tool |
| tools | list<struct<function...>> | OpenHands tool schemas |
| model_patch | string | unified diff; 0.083% empty/null; mean 10,716 chars, p90 27,430 |
| exit_status | string | `submit` 60,739; max-iteration 6,003; stuck-in-loop 252; timeout 36; other 44 |
| resolved | int64 | 32,161 × 1 / 34,913 × 0 — **no -1 in this dataset** |
| gen_tests_correct | double | 53.11% null; else 0/1 |
| pred_passes_gen_tests | double | 53.20% null; else 0/1 |

### nvidia/Open-SWE-Traces (346 files, 1 row group per file, 256–2,500 rows per file)
| field | type | observed values |
|---|---|---|
| instance_id | string | `owner__repo-NNN` (owner lowercased) |
| repo, license, language | string | `Owner/repo`, SPDX id, e.g. php |
| trajectory_id | string | uuid, unique (0 duplicates in 818,660) |
| messages | list<struct<role,content,reasoning_content,tool_calls>> | system/user/assistant/tool |
| tools | list<string> | JSON-serialized tool schemas |
| resolved | int32 | 1 / 0 / **-1 = unknown** |
| metadata | struct{category, teacher_model{name,enable_thinking,reasoning_effort}, reference_patch{patch,num_modified_files,num_modified_lines}, model_patch{...}} | present on 100% of rows; `model_patch.num_modified_files` non-null on 100% of rows, 0 for 0.066% |
| hf_dataset_name | string | `nebius/SWE-rebench-V2` (498,977 rows) or `AweAI-Team/Scale-SWE` (319,683 rows) |

Verified value distributions: teacher_model ∈ {Qwen3.8-Flash-Next 168,824; Qwen3.8-27B 235,391;
Qwen3.6-27B 212,931; MiniMax-M2.5 90,422; Qwen3.5-122B-A10B 60,797; DeepSeek-V4-Flash-0731 50,295}.
category ∈ {bug-fix 427,352; feature-request 238,624; enhancement 99,264; other 53,420}.
Median model patch size = 31 modified lines.

## 3. Trajectories per instance — per config

### 3.1 nebius/SWE-rebench-openhands-trajectories (1 config: OpenHands + Qwen3-Coder-480B)
- rows 67,074; instances 6,306; repos 1,823 (casefolded).
- trajectories/instance: mean 10.64, median 10, p90 15, p99 24, max 34; histogram mode at 7 (966),
  plus long tail to 34 and 24 singletons. (Consistent with "sample up to N attempts".)
- instances with ≥K: K=3 → 6,264; K=5 → 6,148; K=8 → 4,737; K=10 → 3,540; K=16 → 629.
- assistant step count (assistant messages): mean 64.4, median 61, p90 97, **max 100** — matches the
  card's "64.3 avg turns" and the 100-iteration cap that also appears in exit_status.
- issues/repo: mean 3.46, max 275 (`tobymao/sqlglot`); 302 repos with ≥5 issues, 123 with ≥10.
- per-issue resolve rate (multi-sample issues): mean 0.476.
- mixed-label share (≥2 known labels, both 0 and 1): 1,741/6,282 = 27.7%; at K≥3 27.8% (1,739/6,264);
  at K≥8 29.2% (1,382/4,737).
- Label-noise flags: 1,141 rows are `resolved=1` while exit_status is not `submit` (incl. 1,093
  max-iteration rows) ⇒ **exit_status is not a usable proxy for failure**.
- `gen_tests_correct`/`pred_passes_gen_tests` are ~53% null ⇒ second-tier signals only.
- Provenance verified: 100% of rows (casefolded instance_id) found in nebius/SWE-rebench V1.

### 3.2 nvidia/Open-SWE-Traces — 32 configs (config_version/agent/model/benchmark)
Totals per source corpus (pooled over configs, i.e. *not* a usable within-config sample count):

| source | rows | instances | repos | resolved=1 share | resolved=-1 share | mixed-label share (≥2 known) |
|---|---|---|---|---|---|---|
| nebius/SWE-rebench-V2 | 498,977 | 23,079 | 2,676 | 0.390 | 0.095 | 45.5% (10,492/23,042) |
| AweAI-Team/Scale-SWE | 319,683 | 19,466 | 1,180 | 0.553 | 0.049 | 43.0% (7,398/17,199) |

**Within-config** sample counts (this is what an agreement signal needs) — configs sorted by K=3
coverage; full table in [results/nvidia_config_kcover.csv](results/nvidia_config_kcover.csv):

| config | rows | instances | mean traj/issue | max | ≥3 | ≥5 | ≥8 | -1 share |
|---|---|---|---|---|---|---|---|---|
| v1.2/minisweagent/qwen38_27b/scale-swe | 53,553 | 19,352 | 2.77 | 3 | 15,509 | 0 | 0 | 11.4% |
| v1.1/minisweagent/qwen36_27b/swe-rebench-v2 | 53,535 | 20,841 | 2.57 | 3 | 13,980 | 0 | 0 | 8.7% |
| v1.2/minisweagent/qwen38_27b/swe-rebench-v2 | 53,714 | 22,053 | 2.44 | 3 | 12,279 | 0 | 0 | 8.5% |
| v1.0/sweagent/minimax_m25/swe-rebench-v2 | 46,819 | 19,522 | 2.40 | 3 | 11,133 | 0 | 0 | 23.2% |
| v1.1/minisweagent/qwen36_27b/scale-swe | 41,756 | 18,699 | 2.23 | 3 | 9,904 | 0 | 0 | 11.5% |
| v1.0/openhands/minimax_m25/swe-rebench-v2 | 43,603 | 19,022 | 2.29 | 3 | 9,661 | 0 | 0 | 22.3% |
| v1.1/sweagent/qwen36_27b/scale-swe | 40,802 | 16,997 | 2.40 | 3 | 9,537 | 0 | 0 | 11.3% |
| v1.0/openhands/qwen35_122b/swe-rebench-v2 | 40,463 | 18,451 | 2.19 | 3 | 7,934 | 0 | 0 | 23.5% |
| v1.1/sweagent/qwen36_27b/swe-rebench-v2 | 36,459 | 17,396 | 2.10 | 3 | 6,450 | 0 | 0 | 7.6% |
| v1.0/sweagent/qwen35_122b/swe-rebench-v2 | 20,334 | 10,511 | 1.94 | 3 | 3,477 | 0 | 0 | 25.8% |
| 6 × v1.1/openhands (deepseek_v4, qwen36_27b) × 2 benchmarks | — | 13,459–16,895 | 1.39–1.68 | 2 | 0 | 0 | 0 | 0% |
| 20 × remaining configs (all v2.0, v1.2 non-minisweagent) | — | 12,541–20,514 | 1.00 | 1 | 0 | 0 | 0 | 0% |

Notes: nvidia step counts (assistant messages) mean 62.9, median 57, p90 109, max 567.
Instance sets overlap *across* configs: v2.0 swe-rebench-v2 union 22,564 issues, intersection over
all 5 agents 8,907; v2.0 scale-swe union 17,179, intersection 10,371
([results/nvidia_crossconfig_overlap.json](results/nvidia_crossconfig_overlap.json)). That makes a
cross-scaffold ensemble possible (K=5 across agents on ~8.9k/10.4k shared issues) but it pools
configs, which the pre-registration currently forbids for the primary analysis.

## 4. Timestamps / temporal split feasibility

- Neither trajectory dataset carries a timestamp column.
- Joining instance_id (casefolded) to the source corpora gives `created_at`:
  - nebius trajectories → SWE-rebench V1: 100% of rows, 100% of 6,306 instances, span
    2016-04-05 … 2025-03-31. Of the K≥8 subset, all 4,737 are dated, spread over 36 quarters
    (min 169/quarter in 2016Q2, max 3,212 in 2020Q2).
  - nvidia SWE-rebench-V2-sourced rows → SWE-rebench-V2: 100% dated, span 2014-11-10 … 2025-07-22.
  - nvidia Scale-SWE-sourced rows (39% of nvidia rows): **no timestamps available** (0%).
- Practical split therefore: (a) random-by-issue and (b) held-out-repo always; (c) temporal only for
  the SWE-rebench-V2 and nebius-V1 corpora. At a fixed cut of 2023-01-01, issues per side
  ([results/temporal_cut_counts.txt](results/temporal_cut_counts.txt)):

| config | K | pre-2023 | post-2023 |
|---|---|---|---|
| nebius openhands (Qwen3-Coder-480B) | 8 | 3,173 | 1,564 |
| nebius openhands | 3 | 3,969 | 2,295 |
| v1.1/minisweagent/qwen36_27b/swe-rebench-v2 | 3 | 7,772 | 6,208 |
| v1.2/minisweagent/qwen38_27b/swe-rebench-v2 | 3 | 6,831 | 5,448 |
| v1.0/sweagent/minimax_m25/swe-rebench-v2 | 3 | 6,358 | 4,775 |
| v1.0/openhands/minimax_m25/swe-rebench-v2 | 3 | 5,491 | 4,170 |
| v1.0/openhands/qwen35_122b/swe-rebench-v2 | 3 | 4,553 | 3,381 |
| v1.1/sweagent/qwen36_27b/swe-rebench-v2 | 3 | 3,519 | 2,931 |
| v1.0/sweagent/qwen35_122b/swe-rebench-v2 | 3 | 1,769 | 1,708 |
| 4 × Scale-SWE configs | 3 | no timestamps | no timestamps |

## 5. Length/duplication/leak checks

- No duplicate (instance_id, trajectory_id) rows and no duplicate trajectory_id within either
  dataset (0 / 0). One row = one sampled trajectory.
- **instance_id case convention**: nebius V1 and the nebius trajectory dataset preserve owner case
  (`CS-SI__eodag-249`); SWE-rebench-V2 lowercases it (`cs-si__eodag-249`). Exact-string joins give 0
  overlap between V1 and V2; casefolded joins give 642 shared issues, and for **all 642** the
  `created_at` values are identical, i.e. they are the same underlying issues.
- Casefolded overlaps:
  - SWE-rebench V1 ∩ V2: 642 issues (of 21,336 V1 / 32,079 V2).
  - nebius trajectories ∩ nvidia: **204 issues** (2,202 nebius rows, 4,692 nvidia rows), all inside
    nvidia's SWE-rebench-V2 subsets; Scale-SWE ∩ nebius = 0.
  - Of the 204 shared keys, 204/204 agree on repo after casefolding.
  - Overlap is 3.2% of nebius issues but only 0.9% of nvidia V2 issues; removing it costs
    4,737 → 4,580 issues at K≥8 for the nebius corpus.
- Repo overlap between the two benchmark generators: 301 repos appear in both V1 and V2, so
  "held-out repo" splits must be defined per corpus, not globally.
- Repo concentration (drives the repo-clustered bootstrap): nebius top-10 repos hold 13.8% of issues;
  nvidia V2 top-10 hold 9.3%; largest single repo 275 (nebius) / 410 (nvidia V2) issues.

## 6. Candidate signals (availability only — no outcome association computed)

| signal | nebius | nvidia | cost to fetch |
|---|---|---|---|
| patch text (primary signal basis) | `model_patch` (string, 123 MB of the 2.08 GB file) | `metadata.model_patch.patch` (~11.5% of 78 GB ⇒ ≈9 GB full, ≈0.5 GB for 2 configs) | medium |
| files-touched set (secondary signal) | derivable from `model_patch` diff headers | same | same |
| exit status | `exit_status` (7 distinct values; **unreliable**, see §3.1) | not present (only `resolved`) | free |
| step count | len(trajectory) / assistant count (0.2 MB column) | len(messages) / role column (tiny) | free |
| agent-test results | `gen_tests_correct`, `pred_passes_gen_tests` (≈53% null) | not present | free |
| patch size | from `model_patch` | `metadata.model_patch.num_modified_files/num_modified_lines` | free |
| gold patch | SWE-rebench V1 `patch` | `metadata.reference_patch.patch` | medium |

Everything needed for the pre-registered primary signal (cluster share of identical normalized
patches) is present for both corpora; only patch text has a non-trivial read cost.

## 7. Costs

$0.00 — public datasets, no paid APIs, no GPUs (see [COST_LOG.md](COST_LOG.md)). Network volume was
not instrumented precisely; by footer accounting the low-cost scans read on the order of 0.2–0.5 GB
of parquet column chunks (nebius `model_patch` 123 MB dominates the nebius side; the nvidia scans
read only small columns plus 100%-present `metadata` leaves). Estimated total ≲1 GB, no full dataset
downloads.

## 8. Known unknowns / limits of this recon

- `resolved` provenance is taken from the dataset cards; the eval harness was not re-run (no
  container runtime for SWE-rebench images), so label correctness is assumed, not verified.
- The nvidia trajectory generation was sampled 1–3× per issue per config; the sampling rule is not
  documented ⇒ per-issue sample counts may be correlated with difficulty in an unknown way (this is
  itself part of the "shift" risk and is a DEVIATIONS material fact for the paper).
- Scale-SWE has no license tag on the HF card (README badge says CC BY 4.0) — flag for the paper.
- We did not inspect `messages.content`/`reasoning_content` for leakage of gold patches (e.g. hint
  text containing the diff). If the primary analysis uses patch text only, this does not affect the
  signal, but it does affect "does the agent see the answer" claims. Not required for the kill test.
- The 204 shared issues between corpora can be excluded rather than studied; if kept, they must never
  be pooled into one unit.

## 9. Design options this recon supports (decision needed before PREREG)

| option | unit | configs | issues (K=3 / K=8) | shift axes available |
|---|---|---|---|---|
| A. within-config K=8 | issue × 8 | nebius OpenHands (1 config) | — / 4,737 (4,580 excl. shared) | random-issue, held-out-repo, temporal |
| B. within-config K=3 | issue × 3 | 10 nvidia configs + nebius (as K=3) | 3,477–15,509 per config; nebius 6,264 | random-issue, held-out-repo; temporal for 7 of 11 |
| C. cross-scaffold ensemble | issue × 5 agents (1 traj each) | 2 (v2.0, v1.2) × 2 benchmarks | 8,907 / 10,371 issues | + scaffold as a shift axis, but pools configs |
| D. A+B combined | issue × K, per config | 11 configs | K=3 for all (K=8 only nebius) | widest replication |

Option D keeps the pre-registered rule ("replicate per config, no pooling"), gives 11 independent
replications at K=3, and reserves the K≥8 nebius corpus for a covered-vs-K sensitivity check.
Cost: signal resolution at K=3 is coarser (largest-cluster share ∈ {1/3, 2/3, 1}).

## 10. Artifacts

- scripts: [fetch_light.py](scripts/fetch_light.py), [parquet_footer.py](scripts/parquet_footer.py),
  [sample_rows.py](scripts/sample_rows.py), [analyze_light.py](scripts/analyze_light.py),
  [build_nvidia_configs.py](scripts/build_nvidia_configs.py),
  [nvidia_config_stats.py](scripts/nvidia_config_stats.py),
  [overlap_check.py](scripts/overlap_check.py), [recon_extra.py](scripts/recon_extra.py),
  [make_file_list.py](scripts/make_file_list.py)
- results: [overlap_check.json](results/overlap_check.json),
  [nvidia_config_kcover.csv](results/nvidia_config_kcover.csv),
  [nvidia_crossconfig_overlap.json](results/nvidia_crossconfig_overlap.json),
  [recon_extra.json](results/recon_extra.json), [recon_nebius.json](results/recon_nebius.json),
  [recon_nvidia.json](results/recon_nvidia.json), [nvidia_configs.csv](results/nvidia_configs.csv)
