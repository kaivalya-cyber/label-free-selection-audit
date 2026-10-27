#!/usr/bin/env bash
# Regenerates every number in the paper from public HF datasets.
#   Phase 0 (recon)  : reproduce_recon.sh
#   patch caches     : scripts/fetch_all_patches.sh   (~3.7 GB of range reads, ~15 min)
#   signals          : scripts/build_signals.py       (canonicalisation, ~15 min)
#   validation gate  : scripts/make_validation_pairs.py
#   kill test        : scripts/kill_test.py           (single-shot, PREREG §8)
# Usage: bash reproduce_all.sh
set -euo pipefail
PY=.venv/bin/python
mkdir -p out logs results

echo "== phase 0: recon =="
bash reproduce_recon.sh

echo "== patch columns for the 11 frozen configs =="
bash scripts/fetch_all_patches.sh

echo "== canonicalise patches / per-trajectory signals =="
$PY scripts/build_signals.py

echo "== normalizer validation gate (100 pairs) =="
$PY scripts/make_validation_pairs.py

echo "== unit tests =="
$PY -m pytest tests -q

echo "== kill test (single shot) =="
$PY scripts/kill_test.py

echo "== render KILL_TEST.md =="
$PY scripts/render_kill_test.py

echo "done. numbers: results/*.json results/*.csv ; prose: DATA_RECON.md PREREG.md KILL_TEST.md"
