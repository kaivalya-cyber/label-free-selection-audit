"""Deterministic issue/repo splits, exactly as frozen in PREREG.md §4.

All splits are computed from casefolded issue keys and repo names only; labels never enter.
"""
from __future__ import annotations

import hashlib
from collections import defaultdict

CALIB = "calib"
EVAL = "eval"
CUT_DATE = "2023-01-01"


def _h(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


def random_by_issue(config: str, issue_key: str) -> str:
    h = _h("rand", config, issue_key)
    return CALIB if int(h[:2], 16) < 128 else EVAL


def heldout_repo(config: str, repo_of: dict[str, str]) -> dict[str, str]:
    """Assign whole repos to calib/eval, balancing issue counts.

    repos sorted by descending issue count, ties by sha256("repo|config|repo"); each repo goes to the
    side with fewer issues so far (first repo to calibration). Returns {issue_key: side}.
    """
    counts = defaultdict(int)
    for repo in repo_of.values():
        counts[repo] += 1
    order = sorted(counts, key=lambda r: (-counts[r], _h("repo", config, r)))
    side_of_repo: dict[str, str] = {}
    n_calib = n_eval = 0
    for r in order:
        if n_calib <= n_eval:
            side_of_repo[r] = CALIB
            n_calib += counts[r]
        else:
            side_of_repo[r] = EVAL
            n_eval += counts[r]
    return {k: side_of_repo[v] for k, v in repo_of.items()}


def temporal(created_at: dict[str, str], cut: str = CUT_DATE) -> dict[str, str]:
    """created_at ISO strings; earlier than the cut -> calib, on/after -> eval."""
    return {k: (CALIB if v < cut else EVAL) for k, v in created_at.items()}


def assert_no_issue_leak(side: dict[str, str]) -> None:
    """Validate a {issue: side} map produced by this module."""
    assert set(side.values()) <= {CALIB, EVAL}, set(side.values())


def assert_single_side(pairs) -> None:
    """Dataset-level check: every issue key maps to exactly one side (catches row-level leakage)."""
    seen: dict[str, str] = {}
    leaks = []
    for key, side in pairs:
        if key in seen and seen[key] != side:
            leaks.append(key)
        seen[key] = side
    assert not leaks, f"issue on both sides: {leaks[:5]}"


def assert_no_repo_leak(repo_of: dict[str, str], side: dict[str, str]) -> None:
    by_repo = defaultdict(set)
    for k, r in repo_of.items():
        by_repo[r].add(side[k])
    bad = [r for r, s in by_repo.items() if len(s) > 1]
    assert not bad, f"repo leak: {bad[:5]}"
