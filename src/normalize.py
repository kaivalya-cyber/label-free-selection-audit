"""Patch canonicalisation, exactly as frozen in PREREG.md §2.1.

Rules implemented literally:
  1. utf-8 (errors=replace), CRLF/CR -> LF
  2. split into per-file sections at `diff --git` (or `--- ` when no diff header exists)
  3. path: b/... from `diff --git`, else `+++`, else `---`; strip a/ b/ quotes ./ ; /dev/null dropped
  4. keep only `+`/`-` lines (not the +++/--- headers); drop index/hunk/mode/rename/binary/context
  5. rstrip only (internal whitespace and tabs preserved)
  6. sections sorted by path, `path\\n` + lines joined by \\n, sections joined by \\n\\n;
     no kept lines anywhere -> "<no-change>"
  7. identical == byte-equal canonical string
"""
from __future__ import annotations

import re

NO_CHANGE = "<no-change>"

_DIFF_GIT = re.compile(r"^diff --git a/(.+) b/(.+)$")
_PLUS = re.compile(r"^\+\+\+ (?:b/)?(.+?)(?:\t.*)?$")
_MINUS = re.compile(r"^--- (?:a/)?(.+?)(?:\t.*)?$")
_IGNORE_PREFIXES = (
    "index ", "old mode", "new mode", "deleted file mode", "new file mode",
    "similarity index", "dissimilarity index", "rename from", "rename to",
    "copy from", "copy to", "\\ No newline at end of file",
    "Binary files ", "GIT binary patch", "@@",
)


def _clean_path(p: str) -> str | None:
    p = p.strip()
    if len(p) >= 2 and p[0] == '"' and p[-1] == '"':
        p = p[1:-1]
    if p.startswith("a/") or p.startswith("b/"):
        p = p[2:]
    while p.startswith("./"):
        p = p[2:]
    if p in ("/dev/null", "dev/null", ""):
        return None
    return p


def _split_sections(text: str) -> list[list[str]]:
    lines = text.split("\n")
    starts = [i for i, ln in enumerate(lines) if ln.startswith("diff --git ")]
    if not starts:
        starts = [i for i, ln in enumerate(lines) if ln.startswith("--- ")]
    if not starts:
        return []
    bounds = starts + [len(lines)]
    return [lines[bounds[i]:bounds[i + 1]] for i in range(len(starts))]


def _section_path(sec: list[str]) -> str | None:
    for ln in sec:
        m = _DIFF_GIT.match(ln)
        if m:
            p = _clean_path(m.group(2))
            if p:
                return p
    for ln in sec:
        if ln.startswith("+++ "):
            m = _PLUS.match(ln)
            if m:
                p = _clean_path(m.group(1))
                if p:
                    return p
    for ln in sec:
        if ln.startswith("--- "):
            m = _MINUS.match(ln)
            if m:
                p = _clean_path(m.group(1))
                if p:
                    return p
    return None


def _kept_lines(sec: list[str]) -> list[str]:
    out = []
    for ln in sec:
        if ln.startswith("+++ ") or ln.startswith("--- "):
            continue
        if ln.startswith("+") or ln.startswith("-"):
            out.append(ln.rstrip())
        # everything else (index/hunks/mode/context/blank) is dropped
    return out


def canonical_sections(patch: str) -> list[tuple[str, list[str]]]:
    """Return [(path, kept_lines)] sorted by path; only sections with a resolvable path survive."""
    if patch is None:
        return []
    text = patch.replace("\r\n", "\n").replace("\r", "\n")
    secs = []
    for sec in _split_sections(text):
        path = _section_path(sec)
        if path is None:
            continue
        secs.append((path, _kept_lines(sec)))
    secs.sort(key=lambda t: t[0])
    return secs


def canonical(patch: str) -> str:
    secs = canonical_sections(patch)
    if not any(lines for _, lines in secs):
        return NO_CHANGE
    parts = []
    for path, lines in secs:
        if not lines:
            continue
        parts.append(path + "\n" + "\n".join(lines))
    return "\n\n".join(parts)


def files_touched(patch: str) -> tuple[str, ...]:
    """Normalized section paths (PREREG §2.2, referencing step 3 = all resolved section paths)."""
    return tuple(sorted({p for p, _ in canonical_sections(patch)}))


def largest_cluster_share(items) -> float:
    """max cluster size / K with exact equality; items is a sequence of K hashables."""
    items = list(items)
    if not items:
        raise ValueError("empty sample")
    counts: dict = {}
    for it in items:
        counts[it] = counts.get(it, 0) + 1
    return max(counts.values()) / len(items)
