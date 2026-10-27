import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.splits import (CALIB, EVAL, assert_no_issue_leak, assert_no_repo_leak, assert_single_side,
                        heldout_repo, random_by_issue, temporal)


def test_random_by_issue_deterministic_and_balanced():
    keys = [f"owner__repo-{i}" for i in range(2000)]
    a = {k: random_by_issue("cfg", k) for k in keys}
    b = {k: random_by_issue("cfg", k) for k in keys}
    assert a == b
    share = sum(v == CALIB for v in a.values()) / len(a)
    assert 0.45 < share < 0.55
    # different config -> different assignment (not recomputed from the same hash prefix)
    c = {k: random_by_issue("other-cfg", k) for k in keys}
    assert a != c


def test_heldout_repo_no_overlap_and_balanced():
    repo_of = {}
    for r, n in [("big", 40), ("mid", 12), ("small", 3), ("tiny", 1)]:
        for i in range(n):
            repo_of[f"{r}-{i}"] = r
    side = heldout_repo("cfg", repo_of)
    assert set(side) == set(repo_of)
    assert len(set(side.values())) == 2
    assert_no_repo_leak(repo_of, side)
    n_cal = sum(v == CALIB for v in side.values())
    assert abs(n_cal - (len(side) - n_cal)) <= 40  # within the largest single repo
    # determinism
    assert side == heldout_repo("cfg", repo_of)


def test_heldout_repo_assigns_first_repo_to_calib():
    repo_of = {"a-1": "a", "a-2": "a", "b-1": "b"}
    side = heldout_repo("cfg", repo_of)
    assert side["a-1"] == CALIB and side["a-2"] == CALIB
    assert side["b-1"] == EVAL


def test_temporal_boundary():
    s = temporal({"x": "2022-12-31T23:59:59", "y": "2023-01-01T00:00:00", "z": "2024-05-05"})
    assert s == {"x": CALIB, "y": EVAL, "z": EVAL}


def test_asserts_catch_leaks():
    repo_of = {"i1": "r", "i2": "r"}
    with pytest.raises(AssertionError):
        assert_no_repo_leak(repo_of, {"i1": CALIB, "i2": EVAL})
    assert_no_repo_leak(repo_of, {"i1": CALIB, "i2": CALIB})
    assert_no_issue_leak({"i1": CALIB, "i2": EVAL})
    with pytest.raises(AssertionError):
        assert_single_side([("i1", CALIB), ("i1", EVAL)])
    assert_single_side([("i1", CALIB), ("i2", EVAL), ("i1", CALIB)])
