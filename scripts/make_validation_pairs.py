"""PREREG §7 gate: 100 patch pairs (50 identical / 50 different) for human spot-check.

Writes out/validation_pairs/*.patch (full text), results/validation_pairs.csv and
NORMALIZER_VALIDATION.md. Seed fixed by sha256("validate_pairs").
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.configs import CONFIGS  # noqa: E402
from src.normalize import files_touched  # noqa: E402

PER_CONFIG_IDENTICAL = 10
PER_CONFIG_DIFFERENT = 10
TOTAL_IDENTICAL = 50
TOTAL_DIFFERENT = 50
MIN_CONFIGS = 5
CONFIG_ORDER = ["nebius_openhands", "v1.2_minisweagent_qwen38_27b_swe-rebench-v2",
                "v1.1_sweagent_qwen36_27b_swe-rebench-v2", "v1.0_openhands_minimax_m25_swe-rebench-v2",
                "v1.2_minisweagent_qwen38_27b_scale-swe", "v1.1_minisweagent_qwen36_27b_swe-rebench-v2",
                "v1.0_sweagent_minimax_m25_swe-rebench-v2", "v1.0_openhands_qwen35_122b_swe-rebench-v2",
                "v1.0_sweagent_qwen35_122b_swe-rebench-v2", "v1.1_sweagent_qwen36_27b_scale-swe",
                "v1.1_minisweagent_qwen36_27b_scale-swe"]


def rng_for(config: str) -> np.random.Generator:
    h = hashlib.sha256(f"validate_pairs|{config}".encode()).hexdigest()
    return np.random.default_rng(int(h[:16], 16))


def draw_pairs(df: pd.DataFrame, config: str, n_each: int):
    rng = rng_for(config)
    grouped = {k: g for k, g in df.groupby("key") if len(g) >= 2}
    keys = sorted(grouped)
    rng.shuffle(keys)
    ident, diff = [], []
    for k in keys:
        if len(ident) >= n_each and len(diff) >= n_each:
            break
        g = grouped[k].reset_index(drop=True)
        i, j = rng.choice(len(g), size=2, replace=False)
        a, b = g.loc[i], g.loc[j]
        if a.canonical == b.canonical:
            if len(ident) < n_each:
                ident.append((k, a, b))
        elif len(diff) < n_each:
            diff.append((k, a, b))
    return ident, diff


def snippet(s: str, n: int = 700) -> str:
    s = (s or "").replace("\r", "")
    return s if len(s) <= n else s[:n] + f"\n… <{len(s) - n} more chars>"


def main():
    outdir = Path("out/validation_pairs")
    outdir.mkdir(parents=True, exist_ok=True)
    rows, md = [], []
    md.append("# NORMALIZER_VALIDATION — 100 patch pairs for human spot-check\n")
    md.append("Frozen rules: PREREG.md §2.1. Pairs are two distinct trajectories of the **same issue in "
              "the same config**. Verdict = byte-equal canonical form after the normalizer.\n")
    md.append("Check per pair: (1) if marked *identical*, do the two patches really make the same code change? "
              "(2) if marked *different*, is the difference real and not an artifact (whitespace, hunk "
              "offsets, file order)? Full untruncated patches are in `out/validation_pairs/`.\n")
    md.append(f"Sampling seed: `sha256('validate_pairs|config')`, quotas {PER_CONFIG_IDENTICAL} identical + "
              f"{PER_CONFIG_DIFFERENT} different per config until {TOTAL_IDENTICAL}/{TOTAL_DIFFERENT} total.\n")

    n_ident = n_diff = 0
    for config in CONFIG_ORDER:
        if n_ident >= TOTAL_IDENTICAL and n_diff >= TOTAL_DIFFERENT:
            break
        f = Path(f"out/signals/{config}.parquet")
        if not f.exists():
            print(f"skip (no cache): {config}")
            continue
        cfg = next(c for c in CONFIGS if c["tag"] == config)
        df = pd.read_parquet(f)
        raw = pd.read_parquet(f"out/patches/{config}.parquet")[["trajectory_id", "patch"]]
        df = df.merge(raw, on="trajectory_id", how="left", validate="1:1")
        assert df.patch.notna().all(), config
        want_i = min(PER_CONFIG_IDENTICAL, TOTAL_IDENTICAL - n_ident)
        want_d = min(PER_CONFIG_DIFFERENT, TOTAL_DIFFERENT - n_diff)
        ident, diff = draw_pairs(df, config, max(want_i, want_d))
        ident, diff = ident[:want_i], diff[:want_d]
        n_ident += len(ident)
        n_diff += len(diff)
        md.append(f"\n## {config} — {cfg['display']}\n")
        md.append("| pair | instance | verdict | changed lines a/b | files a / files b |")
        md.append("|---|---|---|---|---|")
        for kind, pairs in (("identical", ident), ("different", diff)):
            for n, (k, a, b) in enumerate(pairs, 1):
                pid = f"{config}__{k}__{n}"
                pid = pid.replace("/", "_")
                (outdir / f"{pid}__a.patch").write_text(a.patch or "")
                (outdir / f"{pid}__b.patch").write_text(b.patch or "")
                fa, fb = files_touched(a.patch), files_touched(b.patch)
                rows.append({"pair_id": pid, "config": config, "instance": k, "verdict": kind,
                             "changed_lines_a": int(a.changed_lines), "changed_lines_b": int(b.changed_lines),
                             "files_a": "|".join(fa), "files_b": "|".join(fb),
                             "canonical_sha_a": hashlib.sha256(a.canonical.encode()).hexdigest()[:12],
                             "canonical_sha_b": hashlib.sha256(b.canonical.encode()).hexdigest()[:12]})
                md.append(f"| {pid} | {k} | **{kind}** | {a.changed_lines}/{b.changed_lines} | "
                          f"{len(fa)} / {len(fb)} |")
        # append the evidence blocks for this config
        for kind, pairs in (("identical", ident), ("different", diff)):
            for n, (k, a, b) in enumerate(pairs, 1):
                pid = f"{config}__{k}__{n}".replace("/", "_")
                md.append(f"\n### {pid} — judged **{kind}**\n")
                md.append(f"instance `{k}`\n")
                md.append("**patch A**\n```diff\n" + snippet(a.patch) + "\n```\n")
                md.append("**canonical A**\n```\n" + snippet(a.canonical, 400) + "\n```\n")
                md.append("**patch B**\n```diff\n" + snippet(b.patch) + "\n```\n")
                md.append("**canonical B**\n```\n" + snippet(b.canonical, 400) + "\n```\n")
        print(f"{config}: +{len(ident)} identical, +{len(diff)} different (running {n_ident}/{n_diff})")

    pd.DataFrame(rows).to_csv("results/validation_pairs.csv", index=False)
    md.append(f"\n## Totals\n\nidentical: {n_ident}, different: {n_diff}, "
              f"configs: {len(set(r['config'] for r in rows))}\n")
    Path("NORMALIZER_VALIDATION.md").write_text("\n".join(md))
    print(json.dumps({"identical": n_ident, "different": n_diff,
                      "configs": sorted(set(r["config"] for r in rows))}, indent=2))


if __name__ == "__main__":
    main()
