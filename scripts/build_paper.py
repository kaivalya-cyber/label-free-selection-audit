#!/usr/bin/env python3
"""Build paper.tex and paper.pdf from the single Markdown source.

The manual References section in paper.md is for the Kaggle writeup; it is
removed here so Pandoc emits one natbib bibliography from references.bib.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], log: Path) -> None:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    log.write_text(proc.stdout + "\n--- STDERR ---\n" + proc.stderr, encoding="utf-8")
    if proc.returncode:
        tail = (proc.stdout + proc.stderr).splitlines()[-30:]
        raise SystemExit(f"command failed ({proc.returncode}): {' '.join(cmd)}\n" + "\n".join(tail))


def main() -> None:
    build = ROOT / "build"
    build.mkdir(exist_ok=True)
    source = (ROOT / "paper.md").read_text(encoding="utf-8")
    body = source.split("\n# References")[0].rstrip() + "\n"
    (build / "paper_body.md").write_text(body, encoding="utf-8")

    run([
        "pandoc", str(build / "paper_body.md"),
        "--from", "markdown+pipe_tables+tex_math_dollars",
        "--to", "latex", "--standalone", "--natbib", "--number-sections",
        "--bibliography", "references.bib",
        "--include-in-header", "paper_header.tex",
        "-o", "paper.tex",
    ], build / "pandoc.log")

    run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "paper.tex"],
        build / "xelatex1.log")
    run(["bibtex", "paper"], build / "bibtex.log")
    run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "paper.tex"],
        build / "xelatex2.log")
    run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "paper.tex"],
        build / "xelatex3.log")

    pdf = ROOT / "paper.pdf"
    if not pdf.exists() or pdf.stat().st_size == 0:
        raise SystemExit("paper.pdf was not produced")
    print(f"built paper.tex and paper.pdf ({pdf.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
