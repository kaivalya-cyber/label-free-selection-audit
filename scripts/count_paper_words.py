#!/usr/bin/env python3
"""Count paper words under the track rules.

Three counts are reported:
  1. body only (main text with headings, excluding title, abstract, captions,
     tables and references);
  2. body + figure captions + table text;
  3. everything except references: title block, abstract, body, figure captions
     and table text.

The official Kaggle limit is 3,000 words under rule 3; the working target is
2,900, so that new caveats fit without touching the limit.  References are
excluded throughout.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

LIMIT = 3000
TARGET = 2900
WORD = re.compile(r"[A-Za-z0-9][^\s]*")


def count(text: str) -> int:
    return len(WORD.findall(text))


def split_paper(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    front = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not front:
        raise SystemExit("paper.md must start with YAML metadata")
    meta = front.group(1)
    abstract = re.search(r"^abstract:\s*\|\n(.*?)(?=^---$)", meta + "\n---", re.M | re.S)
    if not abstract:
        raise SystemExit("paper.md must contain a YAML abstract block")

    title_block = []
    for key in ("title", "subtitle", "author", "date"):
        m = re.search(rf"^{key}:\s*(.*)$", meta, re.M)
        if m:
            title_block.append(m.group(1).strip().strip('"'))

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
        "title": "\n".join(title_block),
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
    title = count(parts["title"])
    body_only = body
    body_captions_tables = body + captions + tables
    strict = title + abstract + body + captions + tables

    print(f"title block:             {title}")
    print(f"abstract:                {abstract}")
    print(f"body (headings included):{body}")
    print(f"figure captions:         {captions}")
    print(f"table text:              {tables}")
    print(f"1. body only:                    {body_only}")
    print(f"2. body + captions + tables:     {body_captions_tables}")
    print(f"3. all except references:        {strict}  "
          f"(official limit {LIMIT}, working target {TARGET})")
    if strict > LIMIT:
        raise SystemExit(f"OVER THE OFFICIAL LIMIT by {strict - LIMIT} words under rule 3")
    if strict > TARGET:
        print(f"NOTE: over the {TARGET}-word working target by {strict - TARGET} words")


if __name__ == "__main__":
    main()
