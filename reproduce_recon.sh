#!/usr/bin/env bash
# Phase 0 recon — regenerates every number in DATA_RECON.md.
# Usage: bash reproduce_recon.sh
# Requires: .venv with datasets/huggingface_hub/pyarrow/pandas/numpy/scipy (see requirements.txt).
# Downloads nothing in full: all reads are HTTP range requests against HF parquet shards.
set -euo pipefail

PY=.venv/bin/python
mkdir -p out logs results

# 0. file inventories + source-dataset metadata (instance ids, created_at)
$PY scripts/make_file_list.py nvidia out/nvidia_files.txt
$PY scripts/make_file_list.py nebius out/nebius_files.txt

# 1. lightweight column caches (fast; ~40 s nebius, ~17 min nvidia)
$PY scripts/fetch_light.py --from-list out/nebius_files.txt \
  --cols instance_id,repo,resolved,trajectory_id,exit_status,gen_tests_correct,pred_passes_gen_tests,trajectory.list.element.role,model_patch \
  --out out/nebius_light.parquet
$PY scripts/fetch_light.py --from-list out/nvidia_files.txt \
  --cols instance_id,repo,resolved,trajectory_id,hf_dataset_name,license,language,messages.list.element.role,metadata.category,metadata.teacher_model.name,metadata.model_patch.num_modified_files,metadata.model_patch.num_modified_lines,metadata.reference_patch.num_modified_files,metadata.reference_patch.num_modified_lines \
  --out out/nvidia_light.parquet
$PY scripts/fetch_light.py --from-list out/nvidia_files.txt \
  --cols trajectory_id,instance_id --out out/nvidia_paths.parquet

# 2. provenance/timestamp tables from the source corpora
printf 'nebius/SWE-rebench:data/filtered-00000-of-00001.parquet\nnebius/SWE-rebench:data/test-00000-of-00002.parquet\nnebius/SWE-rebench:data/test-00001-of-00002.parquet\n' > out/swerebench_files.txt
printf 'nebius/SWE-rebench-V2:data/train-00000-of-00001.parquet\n' > out/swerebench_v2_files.txt
$PY scripts/fetch_light.py --from-list out/swerebench_files.txt \
  --cols instance_id,repo,created_at,version,license_name,meta --out out/swerebench_v1_dates.parquet
$PY scripts/fetch_light.py --from-list out/swerebench_v2_files.txt \
  --cols instance_id,repo,created_at,language,license --out out/swerebench_v2_dates.parquet

# 3. summaries
$PY scripts/analyze_light.py nebius out/nebius_light.parquet > results/recon_nebius.txt
$PY scripts/analyze_light.py nvidia out/nvidia_light.parquet > results/recon_nvidia.txt
cp out/recon_nebius.json results/recon_nebius.json
cp out/recon_nvidia.json results/recon_nvidia.json
$PY scripts/build_nvidia_configs.py            > results/nvidia_configs.txt
$PY scripts/nvidia_config_stats.py             > results/nvidia_config_kcover.txt
$PY scripts/overlap_check.py                   > results/overlap_check.txt
$PY scripts/recon_extra.py                     > results/recon_extra.txt

# 4. temporal cut counts (real numbers cited in DATA_RECON.md §4)
$PY scripts/temporal_cut_counts.py             > results/temporal_cut_counts.txt

# 5. parquet footer accounting (column byte shares cited in §6)
{
  $PY scripts/parquet_footer.py nebius/SWE-rebench-openhands-trajectories trajectories.parquet
  echo
  $PY scripts/parquet_footer.py nvidia/Open-SWE-Traces data/openhands/qwen38_flash_next/swe-rebench-v2/train-00005-of-00006.parquet
} > results/parquet_footers.txt

echo "recon reproduction complete"
