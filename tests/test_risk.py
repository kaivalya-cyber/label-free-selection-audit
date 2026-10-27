import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.risk import (breaks_verdict, cluster_bootstrap_lower, cp_upper, ltt_select,
                      selective_risk)


def test_cp_upper_matches_closed_form_for_zero_errors():
    for n in (30, 59, 200):
        assert cp_upper(0, n, 0.05) == pytest.approx(1 - 0.05 ** (1 / n), rel=1e-9)


def test_cp_upper_monotone_and_bounds():
    vals = [cp_upper(k, 100, 0.05) for k in range(0, 101, 10)]
    assert all(a < b for a, b in zip(vals, vals[1:]))
    assert cp_upper(100, 100, 0.05) == pytest.approx(1.0)
    assert cp_upper(0, 0, 0.05) == 1.0
    for k in (0, 5, 50, 100):
        assert 0 <= cp_upper(k, 100, 0.05) <= 1


def test_cp_upper_needs_enough_submissions():
    # 30 clean submissions certify 20% but not 5%
    assert cp_upper(0, 30) > 0.05
    assert cp_upper(0, 30) < 0.20


def test_selective_risk():
    err = np.array([0, 1, 1, 0], dtype=float)
    r, n = selective_risk(err, np.array([1, 1, 0, 0], dtype=bool))
    assert n == 2 and r == 0.5
    r, n = selective_risk(err, np.array([0, 0, 0, 0], dtype=bool))
    assert n == 0 and np.isnan(r)


def test_ltt_stops_at_first_failure():
    # tau=1 unanimous & perfect -> certifies; tau=2/3 pool error 50% -> fails; selects tau=1
    signals = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1] * 6 + [2 / 3] * 60)
    errors = np.array([0] * 60 + [1, 0] * 30, dtype=float)
    out = ltt_select([1, 2 / 3, 1 / 3], signals, errors, alpha=0.10, n_min=30)
    assert out["tau"] == 1 and out["certified"]
    assert [t["tau"] for t in out["trace"]] == [1, 2 / 3]
    assert out["trace"][1]["certifiable"] is False


def test_ltt_abstains_when_most_conservative_fails():
    signals = np.array([1.0] * 100)
    errors = np.ones(100)  # unanimous but always wrong
    out = ltt_select([1, 2 / 3, 1 / 3], signals, errors, alpha=0.10, n_min=30)
    assert out["tau"] is None and out["certified"] is False


def test_ltt_respects_min_submissions():
    signals = np.array([1.0] * 10)
    errors = np.zeros(10)
    out = ltt_select([1], signals, errors, alpha=0.10, n_min=30)
    assert out["tau"] is None


def test_ltt_requires_descending_taus():
    with pytest.raises(ValueError):
        ltt_select([1 / 3, 1], np.zeros(10), np.zeros(10), alpha=0.1)


def test_bootstrap_is_deterministic_and_brackets_point():
    rng = np.random.default_rng(0)
    repos = np.array([f"r{i%40}" for i in range(800)])
    err = (rng.random(800) < 0.3).astype(float)
    sub = np.ones(800, dtype=bool)
    a = cluster_bootstrap_lower(repos, err, sub, B=300, seed_parts=("cfg", 0.1))
    b = cluster_bootstrap_lower(repos, err, sub, B=300, seed_parts=("cfg", 0.1))
    assert a == b
    assert a["lower"] <= a["risk"] <= a["upper"]
    assert a["n_clusters"] == 40


def test_breaks_verdict():
    # threshold is alpha + 0.05 = 0.25
    assert breaks_verdict({"risk": 0.3, "n_sub": 100, "lower": 0.24, "upper": 0.4}, 0.2) == "HOLDS"
    assert breaks_verdict({"risk": 0.3, "n_sub": 100, "lower": 0.26, "upper": 0.4}, 0.2) == "BREAKS"
    assert breaks_verdict({"risk": float("nan"), "n_sub": 0, "lower": float("nan"),
                           "upper": float("nan")}, 0.2) == "NO-COVERAGE"
