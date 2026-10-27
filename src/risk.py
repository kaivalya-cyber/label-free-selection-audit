"""Selective-risk calibration and inference, exactly as frozen in PREREG.md §3 and §5."""
from __future__ import annotations

import hashlib
import math

import numpy as np
from scipy.stats import beta


def cp_upper(n_err: int, n_sub: int, delta: float = 0.05) -> float:
    """One-sided Clopper-Pearson upper bound on a binomial rate at confidence 1-delta."""
    if n_sub < 0 or n_err < 0 or n_err > n_sub:
        raise ValueError((n_err, n_sub))
    if n_sub == 0 or n_err == n_sub:
        return 1.0
    return float(beta.ppf(1.0 - delta, n_err + 1, n_sub - n_err))


def selective_risk(errors: np.ndarray, submitted: np.ndarray) -> tuple[float, int]:
    m = submitted.astype(bool)
    n = int(m.sum())
    if n == 0:
        return float("nan"), 0
    return float(errors[m].mean()), n


def ltt_select(taus, signals: np.ndarray, errors: np.ndarray, alpha: float,
               delta: float = 0.05, n_min: int = 30) -> dict:
    """Fixed-sequence learn-then-test over taus given most-conservative first.

    `taus` must be ordered from highest (most conservative, lowest coverage) to lowest.
    Submit iff signal >= tau. Stops at the first tau that fails the bound; selects the previous one.
    Returns {"tau": float|None, "certified": bool, "trace": [...]}.
    """
    taus = list(taus)
    if sorted(taus, reverse=True) != taus:
        raise ValueError("taus must be descending (most conservative first)")
    trace = []
    selected = None
    selected_cert = False
    for tau in taus:
        sub = signals >= tau
        r, n = selective_risk(errors, sub)
        n_err = int(errors[sub].sum()) if n else 0
        if n == 0:
            u = 1.0
        else:
            u = cp_upper(n_err, n, delta)
        certifiable = (n >= n_min) and (u <= alpha)
        trace.append({"tau": tau, "n_sub": n, "n_err": n_err, "risk": r, "cp_upper": u,
                      "certifiable": certifiable})
        if not certifiable:
            break
        selected, selected_cert = tau, True
    return {"tau": selected, "certified": selected_cert, "trace": trace}


def seeded_rng(*parts) -> np.random.Generator:
    h = hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()
    return np.random.default_rng(int(h[:16], 16))


def cluster_bootstrap_lower(repos, errors, submitted, alpha_ci: float = 0.95,
                            B: int = 2000, seed_parts=()) -> dict:
    """Repo-clustered bootstrap of selective risk. Returns point estimate, lower and upper bounds."""
    repos = np.asarray(repos, dtype=object)
    errors = np.asarray(errors, dtype=float)
    submitted = np.asarray(submitted, dtype=bool)
    m = submitted
    if m.sum() == 0:
        return {"risk": float("nan"), "n_sub": 0, "lower": float("nan"), "upper": float("nan"),
                "n_clusters": int(len(set(repos)))}
    risk = float(errors[m].mean())
    uniq = np.array(sorted(set(repos[m])))
    idx_by_repo = {r: np.where(m & (repos == r))[0] for r in uniq}
    rng = seeded_rng("boot", *seed_parts)
    stats = np.empty(B)
    for b in range(B):
        pick = rng.choice(len(uniq), size=len(uniq), replace=True)
        rows = np.concatenate([idx_by_repo[uniq[i]] for i in pick])
        stats[b] = errors[rows].mean()
    lo = float(np.percentile(stats, 100 * (1 - alpha_ci) / 2))
    hi = float(np.percentile(stats, 100 * (1 - (1 - alpha_ci) / 2)))
    return {"risk": risk, "n_sub": int(m.sum()), "lower": lo, "upper": hi,
            "n_clusters": int(len(uniq))}


def breaks_verdict(boot: dict, alpha: float, margin: float = 0.05) -> str:
    """PREREG §5: BREAKS iff repo-clustered lower bound > alpha + margin."""
    if boot["n_sub"] == 0:
        return "NO-COVERAGE"
    if math.isnan(boot["lower"]):
        return "NO-COVERAGE"
    return "BREAKS" if boot["lower"] > alpha + margin else "HOLDS"
