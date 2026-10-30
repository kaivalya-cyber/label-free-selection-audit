"""Unit tests for the PREREG-3 judge helpers (no torch, no model)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import judge_core as jc  # noqa: E402


class WhitespaceTok:
    """One token per whitespace-separated word; enough to exercise the truncation path."""

    class Enc:
        def __init__(self, ids):
            self.ids = ids

    def encode(self, text, add_special_tokens=False):
        return self.Enc(list(range(len(text.split()))))

    def decode(self, ids):
        return " ".join(f"w{i}" for i in ids)


def test_score_yes_no():
    assert abs(jc.score_yes_no(0.0, 0.0) - 0.5) < 1e-12
    assert jc.score_yes_no(10.0, 0.0) > 0.999
    assert jc.score_yes_no(0.0, 10.0) < 1e-3


def test_truncation_keeps_head_and_tail():
    tok = WhitespaceTok()
    text = " ".join(str(i) for i in range(100))
    out, omitted, trunc = jc.truncate_text(text, tok, 10, 5, "patch")
    assert trunc and omitted == 85
    assert out.startswith("w0 w1 w2")
    assert out.endswith("w99")
    assert "patch truncated: 85 tokens omitted" in out


def test_short_text_untouched():
    tok = WhitespaceTok()
    out, omitted, trunc = jc.truncate_text("a b c", tok, 10, 5, "issue")
    assert out == "a b c" and omitted == 0 and not trunc


def test_build_content_has_both_fields():
    tok = WhitespaceTok()
    built = jc.build_content("issue words", "patch words", tok)
    assert "ISSUE" in built["content"] and "CANDIDATE PATCH" in built["content"]
    assert "YES or NO" in built["content"]
    assert not built["issue_truncated"] and not built["patch_truncated"]


def test_pack_batches_budget():
    batches = jc.pack_batches([100, 100, 100], max_tokens=250, max_batch=8)
    assert batches == [[0, 1], [2]]
    batches = jc.pack_batches([100] * 5, max_tokens=10000, max_batch=2)
    assert all(len(b) <= 2 for b in batches)
    assert sorted(i for b in batches for i in b) == list(range(5))


def test_n_for_rate_rule():
    # 2 * 3002.478 * 1.15 / 3600 = 1.918e-3 h per pair at 1,000 tok/s
    assert jc.n_for_rate(1000.0) == 4226  # capped at the registered sample
    assert 3000 < jc.n_for_rate(500.0) < 3400
    assert jc.n_for_rate(100.0) == 625
    assert jc.n_for_rate(10.0) == 200  # floor, not below the pilot
    assert jc.n_for_rate(0.0) == 200
