#!/usr/bin/env bash
# Fetch {trajectory_id, instance_id, patch} for the 11 frozen configs (PREREG §1).
# ~3.7 GB of range reads total; run once, then all analysis is local.
set -euo pipefail
PY=.venv/bin/python

$PY scripts/fetch_patches.py --dataset nebius --tag nebius_openhands

while read -r tag prefix; do
  [ -z "$tag" ] && continue
  $PY scripts/fetch_patches.py --dataset nvidia --prefix "$prefix" --tag "$tag"
done <<'CONFIGS'
v1.0_openhands_minimax_m25_swe-rebench-v2 data/openhands/minimax_m25/swe-rebench-v2
v1.0_openhands_qwen35_122b_swe-rebench-v2 data/openhands/qwen35_122b/swe-rebench-v2
v1.0_sweagent_minimax_m25_swe-rebench-v2 data/sweagent/minimax_m25/swe-rebench-v2
v1.0_sweagent_qwen35_122b_swe-rebench-v2 data/sweagent/qwen35_122b/swe-rebench-v2
v1.1_minisweagent_qwen36_27b_scale-swe data/minisweagent/qwen36_27b/scale-swe
v1.1_minisweagent_qwen36_27b_swe-rebench-v2 data/minisweagent/qwen36_27b/swe-rebench-v2
v1.1_sweagent_qwen36_27b_scale-swe data/sweagent/qwen36_27b/scale-swe
v1.1_sweagent_qwen36_27b_swe-rebench-v2 data/sweagent/qwen36_27b/swe-rebench-v2
v1.2_minisweagent_qwen38_27b_scale-swe data/minisweagent/qwen38_27b/scale-swe
v1.2_minisweagent_qwen38_27b_swe-rebench-v2 data/minisweagent/qwen38_27b/swe-rebench-v2
CONFIGS
