"""Pure helpers shared by the PREREG-3 judge build and the Kaggle runner.

No torch import here, so the prompt/truncation/packing logic is testable on the laptop.
The tokenizer is passed in: `tokenizers.Tokenizer` locally and the processor's tokenizer on
Kaggle; both expose `encode(text, add_special_tokens=False)` and `decode(ids)`.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

INSTRUCTION = (
    "You are a careful senior software engineer reviewing a candidate patch.\n"
    "\n"
    "Decide whether the candidate patch correctly resolves the issue below. A patch is CORRECT\n"
    "only if it fixes the reported behaviour without breaking existing behaviour. A patch that\n"
    "only changes tests, comments, formatting or documentation is INCORRECT. If the patch is empty\n"
    "or does not address the issue, answer NO.\n"
)
QUESTION = "Does the candidate patch correctly resolve the issue? Answer with exactly one word: YES or NO."

ISSUE_HEAD, ISSUE_TAIL = 3072, 1024
PATCH_HEAD, PATCH_TAIL = 4096, 1024
PROMPT_OVERHEAD = 120
MEAN_JUDGMENT_TOKENS = 3002.4783024017465  # PREREG-3 §2.3, frozen
YES_ID, NO_ID = 26915, 7018


def encode_ids(tok, text: str) -> list[int]:
    out = tok.encode(text, add_special_tokens=False)
    return list(out.ids) if hasattr(out, "ids") else list(out)


def decode_ids(tok, ids: list[int]) -> str:
    return tok.decode(ids)


def truncate_text(text: str, tok, head: int, tail: int, kind: str) -> tuple[str, int, bool]:
    """Keep the first `head` and last `tail` tokens; return (text, omitted, truncated)."""
    ids = encode_ids(tok, text)
    if len(ids) <= head + tail:
        return text, 0, False
    omitted = len(ids) - head - tail
    kept = decode_ids(tok, ids[:head]) + f"\n...[{kind} truncated: {omitted} tokens omitted]...\n" \
        + decode_ids(tok, ids[-tail:])
    return kept, omitted, True


def build_content(issue: str, patch: str, tok) -> dict:
    issue_text, issue_omitted, issue_trunc = truncate_text(
        issue, tok, ISSUE_HEAD, ISSUE_TAIL, "issue")
    patch_text, patch_omitted, patch_trunc = truncate_text(
        patch, tok, PATCH_HEAD, PATCH_TAIL, "patch")
    content = (f"{INSTRUCTION}\nISSUE\n<<<\n{issue_text}\n>>>\n\n"
               f"CANDIDATE PATCH\n<<<\n{patch_text}\n>>>\n\n{QUESTION}\n")
    return {"content": content, "issue_omitted": issue_omitted,
            "patch_omitted": patch_omitted, "issue_truncated": issue_trunc,
            "patch_truncated": patch_trunc}


def render_prompt(processor, content: str) -> tuple[str, list[int]]:
    """Use the model's own chat template; the prompt must end at the model turn."""
    text = processor.apply_chat_template([{"role": "user", "content": content}],
                                         tokenize=False, add_generation_prompt=True)
    ids = encode_ids(processor.tokenizer, text)
    return text, ids


def score_yes_no(z_yes: float, z_no: float) -> float:
    """Two-way softmax over the answer logits; stable for any real inputs."""
    m = max(z_yes, z_no)
    ey, en = pow(2.718281828459045, z_yes - m), pow(2.718281828459045, z_no - m)
    return ey / (ey + en)


def pack_batches(lengths: list[int], max_tokens: int = 24000, max_batch: int = 8) -> list[list[int]]:
    """Longest-first packing under a padded-token budget; returns index batches."""
    order = sorted(range(len(lengths)), key=lambda i: (-lengths[i], i))
    batches: list[list[int]] = []
    cur: list[int] = []
    for i in order:
        cand = cur + [i]
        if cur and (len(cand) * max(lengths[j] for j in cand) > max_tokens
                    or len(cand) > max_batch):
            batches.append(cur)
            cur = [i]
        else:
            cur = cand
    if cur:
        batches.append(cur)
    return batches


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def n_for_rate(rate: float, cap_hours: float = 12.0, margin: float = 1.15,
               max_n: int = 4226, min_n: int = 200) -> int:
    """DEVIATIONS D12: largest prefix whose predicted token time fits the cap."""
    if rate <= 0:
        return min_n
    per_pair_h = 2 * MEAN_JUDGMENT_TOKENS * margin / (rate * 3600)
    n = int(cap_hours / per_pair_h)
    return max(min_n, min(max_n, n))
