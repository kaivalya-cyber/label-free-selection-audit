"""Probe: how much of strict patch disagreement is agent scratch/metadata files?

Signal-only analysis (no labels are read). Compares three canonicalisation variants:
  strict = PREREG §2.1 as frozen
  F1     = strict, but sections that create a new file (`new file mode` / `--- /dev/null`) are dropped
  F2     = F1, plus sections under a dot-directory (.openhands/, .cache/, ...) are dropped
Stores only 8-byte hashes of canonical forms -> bounded memory.
Writes results/scratch_probe.json.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.configs import CONFIGS  # noqa: E402
from src.normalize import NO_CHANGE, _kept_lines, _section_path, _split_sections  # noqa: E402
from src.risk import seeded_rng  # noqa: E402

DOT = re.compile(r"(^|/)\.(openhands|cache|git|idea|vscode)/")


def h(s: str) -> bytes:
    return hashlib.blake2b(s.encode("utf-8", "replace"), digest_size=8).digest()


def variants(patch: str):
    text = (patch or "").replace("\r\n", "\n").replace("\r", "\n")
    secs = []
    for sec in _split_sections(text):
        path = _section_path(sec)
        if path is None:
            continue
        is_new = any(ln.startswith("new file mode") or ln.strip() == "--- /dev/null" for ln in sec)
        secs.append((path, is_new, _kept_lines(sec)))
    secs.sort(key=lambda t: t[0])

    def render(drop_new=False, drop_dot=False):
        parts = []
        for path, is_new, lines in secs:
            if not lines:
                continue
            if drop_new and is_new:
                continue
            if drop_dot and DOT.search(path):
                continue
            parts.append(path + "\n" + "\n".join(lines))
        return h("\n\n".join(parts) if parts else NO_CHANGE)

    return render(), render(drop_new=True), render(drop_new=True, drop_dot=True)


def share_largest(items):
    c = {}
    for it in items:
        c[it] = c.get(it, 0) + 1
    return max(c.values()) / len(items)


def main():
    out = {}
    for cfg in CONFIGS:
        tag = cfg["tag"]
        sig_path = Path(f"out/signals/{tag}.parquet")
        if not sig_path.exists():
            continue
        keys = pd.read_parquet(sig_path, columns=["trajectory_id", "key"])
        key_of = dict(zip(keys.trajectory_id, keys.key))
        rows = []
        pf = pq.ParquetFile(f"out/patches/{tag}.parquet")
        changed_f1 = changed_f2 = n_rows = 0
        for b in pf.iter_batches(batch_size=512, columns=["trajectory_id", "patch"]):
            for tid, patch in zip(b.column("trajectory_id").to_pylist(), b.column("patch").to_pylist()):
                if tid not in key_of:
                    continue
                s, f1, f2 = variants(patch)
                n_rows += 1
                changed_f1 += (s != f1)
                changed_f2 += (s != f2)
                rows.append((key_of[tid], s, f1, f2))
        df = pd.DataFrame(rows, columns=["key", "strict", "F1", "F2"])
        rec = {"rows": n_rows,
               "trajectories_changed_by_F1": changed_f1 / max(n_rows, 1),
               "trajectories_changed_by_F2": changed_f2 / max(n_rows, 1)}
        sizes = df.groupby("key").size()
        eligible = set(sizes[sizes >= 3].index)
        for name in ("strict", "F1", "F2"):
            agree = []
            for key, g in df[df.key.isin(eligible)].groupby("key", sort=False):
                rng = seeded_rng(tag, key)
                idx = np.sort(rng.choice(len(g), size=3, replace=False))
                agree.append(share_largest([tuple(x) for x in g.iloc[idx][name].to_numpy()]))
            agree = np.array(agree)
            rec[name] = {"units": int(len(agree)),
                         "share_all_three_identical": float(np.mean(agree == 1.0)),
                         "share_any_pair": float(np.mean(agree >= 2 / 3)),
                         "share_all_distinct": float(np.mean(agree <= 1 / 3)),
                         "mean_agreement": float(agree.mean())}
        out[tag] = rec
        print(tag, json.dumps(rec), flush=True)
    with open("results/scratch_probe.json", "w") as fh:
        json.dump(out, fh, indent=2)


if __name__ == "__main__":
    main()
