"""Sensitivity-only canonicalisation (DEVIATIONS D4). NOT used by the primary analysis.

F1 = PREREG §2.1 with one extra rule: a section that creates a file (`new file mode` present or a
`--- /dev/null` header) is dropped before comparison. Everything else matches src/normalize.py.
"""
from __future__ import annotations

from .normalize import NO_CHANGE, _kept_lines, _section_path, _split_sections


def canonical_f1(patch: str) -> str:
    if patch is None:
        return NO_CHANGE
    text = patch.replace("\r\n", "\n").replace("\r", "\n")
    parts = []
    for sec in _split_sections(text):
        path = _section_path(sec)
        if path is None:
            continue
        if any(ln.startswith("new file mode") or ln.strip() == "--- /dev/null" for ln in sec):
            continue
        lines = _kept_lines(sec)
        if not lines:
            continue
        parts.append((path, lines))
    if not parts:
        return NO_CHANGE
    parts.sort(key=lambda t: t[0])
    return "\n\n".join(path + "\n" + "\n".join(lines) for path, lines in parts)


def changed_lines_f1(patch: str) -> int:
    return sum(s.count("\n") for s in canonical_f1(patch).split("\n\n")) if patch else 0
