"""Compact human-review view of the 100 validation pairs (PREREG §7 gate).

For each pair judged *different*, shows the first differing canonical lines (A vs B) and whether the
difference is a file-set difference or a content difference. For each pair judged *identical*, shows
the canonical form so the reader can confirm it is a real code change.

Writes NORMALIZER_REVIEW.md (short) alongside the full NORMALIZER_VALIDATION.md.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.normalize import canonical  # noqa: E402

V = pd.read_csv("results/validation_pairs.csv")
L = ["# NORMALIZER_REVIEW — compact evidence for the 100-pair gate\n",
     "Full detail (both patches + both canonical forms per pair): "
     "[NORMALIZER_VALIDATION.md](NORMALIZER_VALIDATION.md). Raw patch files: `out/validation_pairs/`.\n",
     "Read this as: does each **different** verdict have a real cause, and does each **identical** "
     "verdict hide a real difference?\n"]


def load(pid, side):
    return (Path("out/validation_pairs") / f"{pid}__{side}.patch").read_text()


def first_diff_lines(a: str, b: str, n: int = 4):
    la, lb = a.split("\n"), b.split("\n")
    diffs = []
    for i in range(min(len(la), len(lb))):
        if la[i] != lb[i]:
            diffs.append((la[i], lb[i]))
            if len(diffs) >= n:
                break
    if not diffs and len(la) != len(lb):
        diffs.append((la[min(len(la), len(lb))] if len(la) > len(lb) else "<end>",
                      lb[min(len(la), len(lb))] if len(lb) > len(la) else "<end>"))
    return diffs


L.append("\n## Pairs judged DIFFERENT (check: is the difference real?)\n")
L.append("| pair | instance | cause | first differing line A | first differing line B |")
L.append("|---|---|---|---|---|")
content_diffs = 0
for _, r in V[V.verdict == "different"].iterrows():
    ca, cb = canonical(load(r["pair_id"], "a")), canonical(load(r["pair_id"], "b"))
    fa = set(str(r["files_a"]).split("|")) if pd.notna(r["files_a"]) else set()
    fb = set(str(r["files_b"]).split("|")) if pd.notna(r["files_b"]) else set()
    cause = "file set" if fa != fb else "content"
    content_diffs += cause == "content"
    d = first_diff_lines(ca, cb)
    a_line = (d[0][0] if d else "")[:70].replace("|", "\\|")
    b_line = (d[0][1] if d else "")[:70].replace("|", "\\|")
    L.append(f"| {r['pair_id'].split('__', 1)[1]} | {r['instance']} | {cause} | `{a_line}` | `{b_line}` |")
L.append(f"\nCause split: {content_diffs} content differences, {50 - content_diffs} file-set differences "
         f"(of 50).\n")

L.append("\n## Pairs judged IDENTICAL (sample of 12 — check: is this really the same change?)\n")
for _, r in V[V.verdict == "identical"].head(12).iterrows():
    ca = canonical(load(r["pair_id"], "a"))
    L.append(f"\n**{r['pair_id'].split('__', 1)[1]}** · `{r['instance']}` · {r['changed_lines_a']} changed lines · "
             f"files: `{r['files_a']}`\n")
    L.append("```diff\n" + (ca[:600] + ("\n…" if len(ca) > 600 else "")) + "\n```\n")

Path("NORMALIZER_REVIEW.md").write_text("\n".join(L))
print("wrote NORMALIZER_REVIEW.md", len(L), "lines")
