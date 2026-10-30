#!/usr/bin/env bash
# Part C of PREREG-2: B1-B4 (one run) and the RESULTS_2.md rendering.
# PREREG-2 §8 fixes this wrapper; reproduce_all.sh is not modified.
# Usage: bash reproduce_prereg2.sh
set -euo pipefail
PY=.venv/bin/python
mkdir -p logs results

echo "== tests =="
$PY -m pytest tests -q

echo "== B1: selection lift =="
$PY scripts/b1_selection_lift.py

echo "== B2: within-issue AUROC (+ E1-E3) =="
$PY scripts/b2_within_issue_auroc.py

echo "== B3: cross-fit certification (both conventions) =="
$PY scripts/b3_crossfit_certification.py

echo "== B4: adaptive stopping (+ B5) =="
$PY scripts/b4_adaptive_stopping.py

echo "== DESCRIPTIVE: selection baselines, ICC, f(k) =="
$PY scripts/descriptive_tables.py

echo "== render RESULTS_2.md =="
$PY scripts/render_results2.py

echo "done. numbers: results/b1_*.json results/b2_*.json results/b3_*.json results/b4_*.json"
