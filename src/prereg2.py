"""Shared machinery for PREREG-2 B1-B5 (DEVIATIONS D8).

The frames here are rebuilt from the same caches and the same seed arithmetic as
`scripts/kill_test.py::build_units`; `check_against_kill_test` asserts that every issue's
sampled trajectory set equals the frozen kill-test JSON before any analysis reads a label.

Pure selection rules live here so they can be unit-tested for label blindness.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binom

from .configs import CONFIGS
from .risk import seeded_rng

RESULTS = Path("results")
SIGNALS = Path("out/signals")


# ------------------------------------------------------------------ frames
def shared_keys() -> set[str]:
    """The 204 cross-corpus issues excluded everywhere (DEVIATIONS D3)."""
    path = RESULTS / "excluded_shared_issues.csv"
    keys = set(pd.read_csv(path).key.astype(str))
    assert len(keys) == 204, f"expected 204 shared issues, got {len(keys)}"
    return keys


def load_attempts(cfg: dict, k: int, minus1_as_failure: bool = False,
                  shared: set[str] | None = None) -> pd.DataFrame:
    """The frozen K sampled attempts per issue, one row per (issue, trajectory).

    Mirrors PREREG §1 verbatim: sorted trajectory ids, `rng.choice(ids, size=K, replace=False)`,
    with `seed = seeded_rng(tag, key)`. `minus1_as_failure` is the alternative label convention
    of DEVIATIONS D6 (which changes the pool as well as the labels).
    """
    shared = shared_keys() if shared is None else shared
    df = pd.read_parquet(SIGNALS / f"{cfg['tag']}.parquet",
                         columns=["trajectory_id", "key", "repo", "resolved", "canonical", "steps"])
    if minus1_as_failure:
        df.loc[df.resolved == -1, "resolved"] = 0
    df = df[df.resolved.isin([0, 1])]
    df = df[~df.key.isin(shared)]
    assert not (set(df.key) & shared), "shared issue inside the sampling pool"

    rows = []
    for key, g in df.groupby("key", sort=True):
        ids = np.array(sorted(g.trajectory_id.astype(str).tolist()))
        if len(ids) < k:
            continue
        picked = seeded_rng(cfg["tag"], key).choice(ids, size=k, replace=False)
        s = g.set_index("trajectory_id").loc[picked].reset_index()
        assert len(s) == k and s.trajectory_id.nunique() == k
        s["key"] = key
        rows.append(s[["key", "repo", "trajectory_id", "resolved", "canonical", "steps"]])
    out = pd.concat(rows, ignore_index=True)
    assert out.groupby("key").size().eq(k).all()
    assert out.trajectory_id.is_unique
    assert not (set(out.key) & shared)
    return out


def frames_for_all(k: int, minus1_as_failure: bool = False) -> dict[str, pd.DataFrame]:
    shared = shared_keys()
    return {cfg["tag"]: load_attempts(cfg, k, minus1_as_failure, shared) for cfg in CONFIGS}


def _frozen_kill_test_module():
    """Import scripts/kill_test.py without running main(), to reuse its frozen sampling path."""
    import importlib.util

    path = Path(__file__).resolve().parents[1] / "scripts" / "kill_test.py"
    spec = importlib.util.spec_from_file_location("kill_test_frozen", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def check_against_kill_test(frames: dict[str, pd.DataFrame], ks: dict[str, int],
                            alt_frames: dict[str, pd.DataFrame] | None = None) -> dict:
    """Every issue's sampled trajectory set equals the frozen sampling code path.

    `results/kill_test.json` stores no per-issue ids, so the comparison re-executes
    `scripts/kill_test.py::build_units` (the code that produced the frozen frames) and compares the
    `picked` column, plus the unit count against the JSON. The alternative-convention frames are
    compared on unit count only (that pipeline was never serialised per issue).
    """
    frozen = json.loads((RESULTS / "kill_test.json").read_text())
    kt = _frozen_kill_test_module()
    shared = shared_keys()
    out = {"checked_arms": 0, "checked_issues": 0, "mismatched_issues": 0,
           "unit_count_mismatches": 0, "alt_unit_count_mismatches": 0, "details": []}
    by_tag = {c["tag"]: c for c in CONFIGS}
    for tag, frame in frames.items():
        cfg = by_tag[tag]
        k = ks.get(tag, 3)
        units = kt.build_units(cfg, k, shared)
        got = frames[tag].groupby("key").trajectory_id.apply(lambda s: set(s))
        want = {r.key: set(r.picked.split("|")) for r in units.itertuples()}
        bad = [key for key in got.index if want.get(key) != set(got.loc[key])]
        json_units = frozen["k8_arm"]["units"] if k == 8 else frozen["configs"][tag]["units"]
        out["checked_arms"] += 1
        out["checked_issues"] += len(got)
        out["mismatched_issues"] += len(bad)
        out["unit_count_mismatches"] += int(len(got) != json_units)
        out["details"].append({"arm": f"{tag}@K{k}", "issues": int(len(got)),
                               "json_units": int(json_units), "mismatched_picks": len(bad),
                               "first": bad[:3]})
        if alt_frames is not None and tag in alt_frames:
            alt_units = (frozen["k8_arm_minus1_failure"]["units"] if k == 8
                         else frozen["configs_minus1_failure"][tag]["units"])
            out["alt_unit_count_mismatches"] += int(alt_frames[tag].key.nunique() != alt_units)
    return out


# ------------------------------------------------------------------ selection rules
def _clusters(canon_by_tid: dict[str, str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for tid, can in canon_by_tid.items():
        out.setdefault(can, []).append(tid)
    return out


def top_clusters(canon_by_tid: dict[str, str]) -> tuple[list[str], int]:
    """Canonical forms of the largest clusters, ordered lexicographically, plus their size."""
    cl = _clusters(canon_by_tid)
    top = max(len(v) for v in cl.values())
    return sorted(c for c, v in cl.items() if len(v) == top), top


def select_agreement_rep(canon_by_tid: dict[str, str], ktag: str, key: str,
                         mode: str = "smallest") -> dict:
    """B1 selection: seeded choice among the largest clusters, then a representative.

    `mode="smallest"` is the registered representative (smallest trajectory_id); `mode="random"`
    is E3. Neither reads a label.
    """
    tops, size = top_clusters(canon_by_tid)
    idx = int(seeded_rng("select", ktag, key).integers(len(tops)))
    members = sorted(t for t, c in canon_by_tid.items() if c == tops[idx])
    if mode == "smallest":
        rep = members[0]
    elif mode == "random":
        rep = members[int(seeded_rng("selectrep", ktag, key).integers(len(members)))]
    else:
        raise ValueError(mode)
    return {"rep": rep, "top_size": size, "n_top_clusters": len(tops), "unique": len(tops) == 1}


def select_signal_rep(tids, signal_by_tid: dict[str, float | None], ktag: str, key: str,
                      null_score: float = -1.0) -> str:
    """B2 secondary (a) / E2: highest own-test signal, seeded tie-break, no label read."""
    score = {t: (null_score if signal_by_tid.get(t) is None else float(signal_by_tid[t]))
             for t in tids}
    best = max(score.values())
    tied = sorted(t for t in tids if score[t] == best)
    return tied[int(seeded_rng("selectb2", ktag, key).integers(len(tied)))]


def select_combined_rep(tids, cluster_size_by_tid: dict[str, int],
                        signal_by_tid: dict[str, float | None], ktag: str, key: str) -> str:
    """B2 secondary (b): lexicographic (cluster_size, own-test), seeded tie-break."""
    score = {t: (cluster_size_by_tid[t],
                 -1.0 if signal_by_tid.get(t) is None else float(signal_by_tid[t]))
             for t in tids}
    best = max(score.values())
    tied = sorted(t for t in tids if score[t] == best)
    return tied[int(seeded_rng("selectb2", ktag, key).integers(len(tied)))]


def issue_lift(canon_by_tid: dict[str, str], label_by_tid: dict[str, int],
               ktag: str, key: str, mode: str = "smallest") -> dict:
    """B1 per-issue contrast: selected - random-K, plus the oracle ceiling.

    On a non-mixed issue both terms equal the issue's single label, so the lift is 0 by
    construction (DEVIATIONS D8).
    """
    sel = select_agreement_rep(canon_by_tid, ktag, key, mode)
    labels = np.array([label_by_tid[t] for t in canon_by_tid], dtype=float)
    random_k = float(labels.mean())
    selected = float(label_by_tid[sel["rep"]])
    return {"rep": sel["rep"], "selected": selected, "random_k": random_k,
            "oracle_k": float(labels.max()), "lift": selected - random_k,
            "mixed": bool(0 < labels.sum() < len(labels)),
            "top_size": sel["top_size"], "unique": sel["unique"]}


def d1_pick(tids, canon_by_tid: dict[str, str]) -> str:
    """DEVIATIONS D1: largest canonical cluster, ties by smallest trajectory_id inside it."""
    cl = _clusters({t: canon_by_tid[t] for t in tids})
    top = max(len(v) for v in cl.values())
    return min(min(v) for v in cl.values() if len(v) == top)


def d1_pick_killtest(tids, canon_by_tid: dict[str, str]) -> str:
    """The representative `scripts/kill_test.py::build_units` actually chose.

    It breaks equal-size cluster ties by the lexicographically smallest canonical form, not by the
    smallest trajectory_id as DEVIATIONS D1 states. Reproduced here only to audit the frozen numbers;
    B4 uses `d1_pick`, the documented rule.
    """
    cl = _clusters({t: canon_by_tid[t] for t in tids})
    top = max(len(v) for v in cl.values())
    best = min(c for c, v in cl.items() if len(v) == top)
    return min(cl[best])


def seq_any1st(tids_in_draw_order, canon_by_tid: dict[str, str]) -> tuple[int, str]:
    """B4 variant: stop at the first repeat; representative per DEVIATIONS D8."""
    seen: dict[str, list[str]] = {}
    for i, tid in enumerate(tids_in_draw_order):
        can = canon_by_tid[tid]
        if can in seen:
            return i + 1, min(seen[can])
        seen[can] = [tid]
    return len(tids_in_draw_order), d1_pick(tids_in_draw_order, canon_by_tid)


# ------------------------------------------------------------------ inference
def holm(pvals: dict[str, float], alpha: float = 0.05) -> dict:
    """Holm step-down over one family; adjusted p-values are the step-down maxima."""
    tags = sorted(pvals, key=lambda t: pvals[t])
    m = len(tags)
    adj, running = {}, 0.0
    for i, tag in enumerate(tags):
        running = max(running, min(1.0, (m - i) * pvals[tag]))
        adj[tag] = running
    return {"alpha": alpha,
            "adjusted": adj,
            "rejected": {t: bool(adj[t] < alpha) for t in tags},
            "order": tags}


def sign_test(directions: dict[str, int]) -> dict:
    """Two-sided exact sign test over the 11 configs; ties dropped."""
    pos = sum(1 for v in directions.values() if v > 0)
    neg = sum(1 for v in directions.values() if v < 0)
    n = pos + neg
    p = 1.0 if n == 0 else float(min(1.0, 2 * binom.cdf(min(pos, neg), n, 0.5)))
    return {"n_pos": pos, "n_neg": neg, "n_ties": len(directions) - n,
            "n_eff": n, "p_two_sided": p}


def bootstrap_mean(values, repos, seed_parts, B: int = 2000, null: float = 0.0) -> dict:
    """Repo-clustered bootstrap of a mean, with the pre-registered two-sided p formula.

    `null` is the value of no effect (0 for a lift/difference, 0.5 for an AUROC).
    """
    vals = np.asarray(values, dtype=float)
    rep = np.asarray(repos, dtype=object)
    uniq, inv = np.unique(rep, return_inverse=True)
    sums = np.bincount(inv, weights=vals)
    counts = np.bincount(inv)
    keep = counts > 0
    sums, counts, uniq = sums[keep], counts[keep], uniq[keep]
    R = len(uniq)
    rng = seeded_rng("boot2", *seed_parts)
    draws = rng.integers(0, R, size=(B, R))
    est = sums[draws].sum(axis=1) / counts[draws].sum(axis=1)
    lo, hi = np.percentile(est, [2.5, 97.5])
    p = float(min(1.0, 2 * min((1 + int((est <= null).sum())) / (B + 1),
                               (1 + int((est >= null).sum())) / (B + 1))))
    return {"estimate": float(vals.mean()), "lower": float(lo), "upper": float(hi),
            "p": p, "n_clusters": int(R), "B": B}


def bootstrap_sum_ratio(num_by_repo, den_by_repo, repos, seed_parts, B: int = 2000,
                        null: float = 0.0) -> dict:
    """Same bootstrap for a ratio of pooled sums (used by the pair AUROCs)."""
    rep = np.asarray(repos, dtype=object)
    uniq, inv = np.unique(rep, return_inverse=True)
    num = np.bincount(inv, weights=np.asarray(num_by_repo, dtype=float))
    den = np.bincount(inv, weights=np.asarray(den_by_repo, dtype=float))
    keep = den > 0
    num, den = num[keep], den[keep]
    R = len(den)
    rng = seeded_rng("boot2", *seed_parts)
    draws = rng.integers(0, R, size=(B, R))
    est = num[draws].sum(axis=1) / den[draws].sum(axis=1)
    lo, hi = np.percentile(est, [2.5, 97.5])
    p = float(min(1.0, 2 * min((1 + int((est <= null).sum())) / (B + 1),
                               (1 + int((est >= null).sum())) / (B + 1))))
    return {"estimate": float(num.sum() / den.sum()), "lower": float(lo), "upper": float(hi),
            "p": p, "n_clusters": int(R), "B": B}


def auroc_scores(pos, neg) -> np.ndarray:
    """Per-pair AUROC contribution: 1 for a correct ordering, 0.5 for a tie."""
    pos = np.asarray(pos, dtype=float)
    neg = np.asarray(neg, dtype=float)
    return (pos > neg).astype(float) + 0.5 * (pos == neg)


def matched_delta(used, submitted, prefix_labels, labels_repo, seed_parts, B: int = 2000) -> dict:
    """B4/B5 primary: r_ad - f_interp(mean attempts), with the weight re-estimated per replicate.

    `prefix_labels[i, k]` is the label of the D1 representative among the first k draws of issue i
    (k = 1..K_max); `used[i]` the rule's draw count; `submitted[i]` its submitted label.
    """
    used = np.asarray(used, dtype=float)
    submitted = np.asarray(submitted, dtype=float)
    prefix = np.asarray(prefix_labels, dtype=float)
    K = prefix.shape[1] - 1
    rep = np.asarray(labels_repo, dtype=object)
    uniq, inv = np.unique(rep, return_inverse=True)
    R = len(uniq)

    def one(idx) -> dict:
        c = float(used[idx].mean())
        k0 = int(np.floor(c))
        k1 = min(k0 + 1, K)
        f0 = float(prefix[idx, k0].mean())
        f1 = float(prefix[idx, k1].mean())
        interp = f0 if c >= K else f0 + (c - k0) * (f1 - f0)
        return {"c": c, "k0": k0, "k1": k1, "f0": f0, "f1": f1, "f_interp": interp,
                "r": float(submitted[idx].mean()), "delta": float(submitted[idx].mean() - interp)}

    point = one(np.arange(len(used)))
    rng = seeded_rng("boot2", *seed_parts)
    by_repo = [np.where(inv == r)[0] for r in range(R)]
    est = np.empty(B)
    for b in range(B):
        pick = rng.integers(0, R, size=R)
        idx = np.concatenate([by_repo[i] for i in pick])
        est[b] = one(idx)["delta"]
    lo, hi = np.percentile(est, [2.5, 97.5])
    p = float(min(1.0, 2 * min((1 + int((est <= 0).sum())) / (B + 1),
                               (1 + int((est >= 0).sum())) / (B + 1))))
    curve = {str(k): float(prefix[:, k].mean()) for k in range(1, K + 1)}
    return {"point": point, "curve": curve, "lower": float(lo), "upper": float(hi),
            "p": p, "n_clusters": int(R), "B": B}


def write_json(path: str | Path, obj: dict) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=1, sort_keys=False) + "\n")
