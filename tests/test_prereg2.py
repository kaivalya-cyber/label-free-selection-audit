import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.prereg2 import (auroc_scores, d1_pick, holm, issue_lift, matched_delta,
                         select_agreement_rep, select_signal_rep, seq_any1st, sign_test,
                         top_clusters)


def _labels(canon, labels):
    return dict(canon), dict(labels)


def test_top_clusters_ordered_by_canonical_string_not_by_position():
    canon = {"a": "zzz", "b": "aaa", "c": "aaa"}
    tops, size = top_clusters(canon)
    assert size == 2 and tops == ["aaa"]
    canon = {"a": "p", "b": "p", "c": "q", "d": "q"}
    tops, size = top_clusters(canon)
    assert size == 2 and tops == ["p", "q"]  # lexicographic


def test_b1_selection_is_label_blind():
    canon = {"t1": "A", "t2": "A", "t3": "B", "t4": "B"}
    lab = {"t1": 1, "t2": 0, "t3": 1, "t4": 0}
    rng = np.random.default_rng(0)
    for i in range(50):
        row = issue_lift(canon, lab, "tag@K4", f"i{i}")
        # permute the labels; the chosen representative must not move
        perm = dict(zip(sorted(lab), rng.permutation([lab[t] for t in sorted(lab)])))
        assert issue_lift(canon, perm, "tag@K4", f"i{i}")["rep"] == row["rep"]
        # ... and the lift is selected - random-K with the labels as given
        assert row["lift"] == pytest.approx(row["selected"] - row["random_k"])


def test_b1_lift_is_zero_by_construction_on_non_mixed_issues():
    canon = {"t1": "A", "t2": "A", "t3": "B"}
    for labs in ({"t1": 1, "t2": 1, "t3": 1}, {"t1": 0, "t2": 0, "t3": 0}):
        row = issue_lift(canon, labs, "tag@K3", "x")
        assert row["lift"] == 0.0
        assert row["mixed"] is False


def test_b1_lift_on_a_mixed_issue_is_selected_minus_resolve_rate():
    canon = {"t1": "A", "t2": "A", "t3": "B"}
    lab = {"t1": 1, "t2": 0, "t3": 0}
    row = issue_lift(canon, lab, "tag@K3", "x")
    assert row["random_k"] == pytest.approx(1 / 3)
    assert row["lift"] == pytest.approx(row["selected"] - 1 / 3)
    assert row["mixed"] is True
    assert row["top_size"] == 2 and row["unique"] is True


def test_e3_random_representative_stays_inside_the_top_cluster():
    canon = {"t1": "A", "t2": "A", "t3": "A", "t4": "B"}
    picks = {select_agreement_rep(canon, "tag@K4", f"i{i}", mode="random")["rep"]
             for i in range(40)}
    assert picks <= {"t1", "t2", "t3"}
    assert picks == {"t1", "t2", "t3"}


def test_d1_pick_breaks_ties_by_smallest_trajectory_id_inside_the_cluster():
    canon = {"t9": "A", "t8": "A", "t7": "B", "t6": "B"}
    assert d1_pick(list(canon), canon) == "t6"   # cluster B holds the smallest id overall
    canon = {"t2": "A", "t3": "A", "t4": "B", "t5": "B"}
    assert d1_pick(list(canon), canon) == "t2"


def test_seq_any1st_stops_at_first_repeat_and_submits_the_smaller_agreeing_id():
    canon = {"a": "A", "b": "B", "c": "A", "d": "C"}
    used, rep = seq_any1st(["a", "b", "c"], canon)
    assert used == 3 and rep == "a"
    used, rep = seq_any1st(["a", "b", "d"], canon)
    assert used == 3 and rep == "a"  # no repeat -> D1 over all three (all singletons -> "a")


def test_select_signal_rep_null_scores_below_tests_and_ties_are_seeded():
    tids = ["t1", "t2", "t3"]
    sig = {"t1": None, "t2": 0.0, "t3": None}
    assert select_signal_rep(tids, sig, "tag@K3", "x") == "t2"
    sig = {"t1": 1.0, "t2": 1.0, "t3": 0.0}
    picks = {select_signal_rep(tids, sig, "tag@K3", f"i{i}") for i in range(40)}
    assert picks == {"t1", "t2"}
    sig = {"t1": None, "t2": None, "t3": None}
    picks = {select_signal_rep(tids, sig, "tag@K3", f"i{i}") for i in range(40)}
    assert picks == {"t1", "t2", "t3"}


def test_auroc_ties_count_half():
    s = auroc_scores([1, 1, 0], [0, 1, 1])
    assert list(s) == [1.0, 0.5, 0.0]


def test_holm_step_down():
    out = holm({"a": 0.001, "b": 0.005, "c": 0.02, "d": 0.5}, alpha=0.05)
    assert out["rejected"]["a"] and out["rejected"]["b"] and out["rejected"]["c"]
    assert not out["rejected"]["d"]
    assert out["adjusted"]["a"] == pytest.approx(0.004)


def test_sign_test_threshold_is_10_of_11_not_9_of_11():
    # exact two-sided: 2*P(Bin(11,1/2)<=2) = 0.0654, so 9-2 does not reach 0.05;
    # PREREG-2 §10 bullet 7 says "9-2" and is off by one (reported in RESULTS_2).
    assert sign_test({f"c{i}": (1 if i < 10 else -1) for i in range(11)})["p_two_sided"] < 0.05
    assert sign_test({f"c{i}": (1 if i < 9 else -1) for i in range(11)})["p_two_sided"] > 0.05
    ties = {f"c{i}": 0 for i in range(11)}
    assert sign_test(ties)["p_two_sided"] == 1.0


def test_matched_delta_is_zero_when_the_rule_matches_the_full_budget():
    used = np.array([3, 3, 3])
    submitted = np.array([1, 0, 0])
    prefix = np.zeros((3, 4), dtype=float)      # column k = D1 label among the first k draws
    prefix[:, 3] = submitted
    repo = np.array(["r1", "r2", "r3"])
    out = matched_delta(used, submitted, prefix, repo, ("tag@K3", "t"), B=200)
    assert out["point"]["c"] == 3.0
    assert out["point"]["delta"] == 0.0
    assert out["curve"]["3"] == pytest.approx(1 / 3)
