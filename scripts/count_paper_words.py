#!/usr/bin/env python3
"""Count paper words under the Kaggle track rules.

Body prose is everything before the manual References section, excluding the
YAML metadata, Markdown table rows/table captions, and figure blocks. Abstract,
captions, and table text are reported separately. The limit includes the
abstract, captions, and tables; references are excluded.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

LIMIT = 2990
WORD = re.compile(r"[A-Za-z0-9][^\s]*")


def count(text: str) -> int:
    return len(WORD.findall(text))


def split_paper(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    front = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not front:
        raise SystemExit("paper.md must start with YAML metadata")
    abstract = re.search(r"^abstract:\s*\|\n(.*?)(?=^---$)", front.group(1) + "\n---", re.M | re.S)
    if not abstract:
        raise SystemExit("paper.md must contain a YAML abstract block")
    body = text[front.end():].split("\n# References")[0]
    lines, prose, captions, tables = body.splitlines(), [], [], []
    for line in lines:
        if line.startswith("|") or re.match(r"^\s*\|?[-:| ]+\|?\s*$", line) \
                or line.startswith(": "):
            tables.append(line)
        elif line.startswith("!["):
            captions.append(line)
        else:
            prose.append(line)
    return {
        "abstract": abstract.group(1),
        "body": "\n".join(prose),
        "captions": "\n".join(captions),
        "tables": "\n".join(tables),
    }


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("paper.md")
    parts = split_paper(path)
    body, abstract = count(parts["body"]), count(parts["abstract"])
    captions, tables = count(parts["captions"]), count(parts["tables"])
    total = body + abstract + captions + tables
    print(f"body prose:              {body}")
    print(f"abstract:                {abstract}")
    print(f"figure captions:         {captions}")
    print(f"table text:              {tables}")
    print(f"body + abstract:         {body + abstract}")
    print(f"with captions + tables:  {total}  (limit {LIMIT})")
    if total > LIMIT:
        raise SystemExit(f"OVER LIMIT by {total - LIMIT} words")


if __name__ == "__main__":
    main()
