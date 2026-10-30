#!/usr/bin/env bash
# PREREG-3 post-run analysis: verify the sealed pilot + main shard hashes, then recompute
# the within-issue AUROCs from the frozen pair order.  The model is not run here.
# Usage: bash reproduce_prereg3.sh
set -euo pipefail
PY=.venv/bin/python
mkdir -p logs results

echo "== tests =="
$PY -m pytest tests -q

echo "== verify pilot + main shard hashes =="
$PY - <<'PY'
import hashlib, json
from pathlib import Path

pilot = Path("out/judge/pilot_gguf_out/sealed/pilot_scores.parquet")
assert hashlib.sha256(pilot.read_bytes()).hexdigest() == \
    "f042359d3454ca45d3f7eb721ebb1a030f2363d1e690df59aad0138c7499b434", "pilot hash"
man = json.loads(Path("out/judge/main_gguf_out/shards/manifest.json").read_text())
bad = [n for n, h in man.items()
       if hashlib.sha256((Path("out/judge/main_gguf_out/shards") / n).read_bytes()).hexdigest() != h]
assert not bad, f"shard hash mismatch: {bad}"
print(f"pilot + {len(man)} main shards verified")
PY

echo "== PREREG-3 analysis =="
$PY scripts/analyze_judge.py --n 4226 \
    --scores out/judge/pilot_gguf_out/sealed/pilot_scores.parquet \
             'out/judge/main_gguf_out/shards/*.parquet' \
    --out results/judge_analysis.json

echo "done. number: results/judge_analysis.json"
