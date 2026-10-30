"""Build the frozen PREREG-3 pair order and the pilot bundle.

- pairs: all pos x neg pairs of the frozen nebius@K=8 mixed-label issues (12,917), then the
  seeded 4,226-pair sample in the order DEVIATIONS D12 freezes;
- attempts: one row per distinct trajectory in the sample, with issue text, patch and token counts;
- pilot bundle: pairs 0..199 and their attempts, ready to upload as a Kaggle dataset.

Outputs (all under out/judge/, which is gitignored):
  out/judge/pairs_all.parquet, out/judge/attempts_all.parquet, out/judge/manifest.json
  out/judge/bundle_pilot/{pairs.parquet,attempts.parquet,manifest.json,judge_core.py,judge_run.py}

Usage: .venv/bin/python scripts/judge_build_pairs.py
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.judge_core import MEAN_JUDGMENT_TOKENS, build_content, encode_ids, sha256_file  # noqa: E402
from src.configs import CONFIGS  # noqa: E402
from src.prereg2 import load_attempts, shared_keys  # noqa: E402
from src.risk import seeded_rng  # noqa: E402

MODEL_REPO = "google/gemma-4-26B-A4B-it"
OUT = ROOT / "out" / "judge"
PILOT_PAIRS = 200
N_SAMPLE = 4226


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tok_json = hf_hub_download(MODEL_REPO, "tokenizer.json")
    tok = Tokenizer.from_file(tok_json)
    tok_hash = sha256_file(tok_json)

    neb = next(c for c in CONFIGS if c["tag"] == "nebius_openhands")
    frame = load_attempts(neb, 8, False, shared_keys())

    problem = pd.read_parquet(ROOT / "out" / "swerebench_problem.parquet")
    problem["key"] = problem.instance_id.astype(str).str.casefold()
    problem = problem.drop_duplicates("key").set_index("key")
    patch = pd.read_parquet(ROOT / "out" / "patches" / "nebius_openhands.parquet",
                            columns=["trajectory_id", "patch"]).set_index("trajectory_id")

    frame["issue_text"] = frame.key.map(problem.problem_statement)
    frame["patch"] = frame.trajectory_id.map(patch.patch)
    assert frame.issue_text.notna().all() and frame.patch.notna().all()

    # Enumerate every mixed-label pair deterministically: issue ascending, positive ids then negative
    # ids ascending. The frozen sample is a seeded choice over this list.
    pairs = []
    for key, g in frame.groupby("key", sort=True):
        pos = sorted(g.loc[g.resolved == 1, "trajectory_id"].astype(str))
        neg = sorted(g.loc[g.resolved == 0, "trajectory_id"].astype(str))
        for p in pos:
            for n in neg:
                pairs.append((key, g.repo.iloc[0], p, n))
    pairs = pd.DataFrame(pairs, columns=["key", "repo", "pos_tid", "neg_tid"])
    assert len(pairs) == 12917, len(pairs)

    order = seeded_rng("judge3", "pairs").choice(len(pairs), size=N_SAMPLE, replace=False)
    sample = pairs.iloc[order].reset_index(drop=True)
    sample["pair_id"] = np.arange(len(sample))
    sample = sample[["pair_id", "key", "repo", "pos_tid", "neg_tid"]]
    assert sample.pair_id.is_unique and len(sample) == N_SAMPLE
    assert not sample.duplicated(["pos_tid", "neg_tid"]).any()

    tids = sorted(set(sample.pos_tid) | set(sample.neg_tid))
    att = frame[frame.trajectory_id.astype(str).isin(tids)].copy()
    att["trajectory_id"] = att.trajectory_id.astype(str)
    att = att.set_index("trajectory_id").loc[tids].reset_index()
    assert len(att) == len(tids)
    assert att.resolved.isin([0, 1]).all()

    counts = []
    for row in att.itertuples():
        built = build_content(row.issue_text, row.patch, tok)
        issue_ids = encode_ids(tok, row.issue_text)
        patch_ids = encode_ids(tok, row.patch)
        counts.append({"trajectory_id": row.trajectory_id, "key": row.key, "repo": row.repo,
                       "resolved": int(row.resolved), "issue_text": row.issue_text,
                       "patch": row.patch, "issue_tokens": len(issue_ids),
                       "patch_tokens": len(patch_ids),
                       "issue_truncated": built["issue_truncated"],
                       "patch_truncated": built["patch_truncated"],
                       "prompt_tokens_estimate": len(issue_ids) - built["issue_omitted"]
                       + len(patch_ids) - built["patch_omitted"] + 120})
    att = pd.DataFrame(counts)
    assert len(att) == len(tids)

    pairs_path = OUT / "pairs_all.parquet"
    att_path = OUT / "attempts_all.parquet"
    sample.to_parquet(pairs_path, index=False)
    att.to_parquet(att_path, index=False)

    manifest = {
        "prereg": "PREREG-3 frozen 65c3999, D12 e99115c",
        "model": MODEL_REPO, "tokenizer_sha256": tok_hash,
        "seed": 'seeded_rng("judge3", "pairs")',
        "pairs_available": len(pairs), "pair_sample": len(sample), "distinct_attempts": len(att),
        "issues_in_sample": int(sample.key.nunique()), "repos_in_sample": int(sample.repo.nunique()),
        "mean_judgment_tokens_frozen": MEAN_JUDGMENT_TOKENS,
        "mean_prompt_tokens_estimate": float(att.prompt_tokens_estimate.mean()),
        "pairs_sha256": sha256_file(pairs_path), "attempts_sha256": sha256_file(att_path),
    }

    # ---------------------------------------------------------------- pilot bundle
    pilot_dir = OUT / "bundle_pilot"
    if pilot_dir.exists():
        shutil.rmtree(pilot_dir)
    pilot_dir.mkdir(parents=True)
    pp = sample.head(PILOT_PAIRS).copy()
    ptids = set(pp.pos_tid) | set(pp.neg_tid)
    pa = att[att.trajectory_id.isin(ptids)].copy()
    pp.to_parquet(pilot_dir / "pairs.parquet", index=False)
    pa.to_parquet(pilot_dir / "attempts.parquet", index=False)
    shutil.copy2(ROOT / "scripts" / "judge_core.py", pilot_dir / "judge_core.py")
    shutil.copy2(ROOT / "scripts" / "judge_run.py", pilot_dir / "judge_run.py")
    pman = dict(manifest)
    pman.update({"pairs": PILOT_PAIRS, "attempts": len(pa),
                 "pilot_pairs_sha256": sha256_file(pilot_dir / "pairs.parquet"),
                 "pilot_attempts_sha256": sha256_file(pilot_dir / "attempts.parquet"),
                 "pilot_pairs": int(pp.pair_id.nunique()),
                 "pilot_issue_text_sha256": sha256_file(pilot_dir / "attempts.parquet")})
    (pilot_dir / "manifest.json").write_text(json.dumps(pman, indent=1) + "\n")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")

    print(json.dumps({k: v for k, v in manifest.items() if not k.endswith("sha256")}, indent=1))
    print(f"pilot: {len(pp)} pairs, {len(pa)} attempts, dir={pilot_dir}")


if __name__ == "__main__":
    main()
