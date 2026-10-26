"""Sample first rows of each candidate parquet shard via ranged reads (no full download).

Usage: .venv/bin/python scripts/sample_rows.py <repo_id> <path-in-repo> [--cols a,b,c] [--n 2]
"""
import argparse
import json
import sys

import pyarrow.parquet as pq
from huggingface_hub import HfFileSystem


def preview(v, maxlen=400):
    s = v if isinstance(v, str) else json.dumps(v, default=str)
    return s if len(s) <= maxlen else s[:maxlen] + f"...<{len(s)} chars>"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("path")
    ap.add_argument("--cols", default=None, help="comma separated; default all")
    ap.add_argument("--n", type=int, default=2)
    a = ap.parse_args()

    fs = HfFileSystem()
    with fs.open(f"datasets/{a.repo}/{a.path}", "rb") as f:
        pf = pq.ParquetFile(f)
        print(f"# {a.repo}/{a.path}")
        print("schema:", pf.schema_arrow)
        print("row_groups:", pf.num_row_groups, "rows:", pf.metadata.num_rows)
        cols = a.cols.split(",") if a.cols else None
        got = 0
        for batch in pf.iter_batches(batch_size=a.n, columns=cols):
            d = batch.to_pylist()
            for row in d:
                got += 1
                print(f"--- row {got} ---")
                for k, v in row.items():
                    if isinstance(v, list):
                        print(f"  {k}: list(len={len(v)}) first={preview(v[0]) if v else None}")
                    elif isinstance(v, dict):
                        print(f"  {k}: dict keys={sorted(v.keys())}")
                        for kk, vv in v.items():
                            print(f"      {kk}: {preview(vv, 200)}")
                    else:
                        print(f"  {k}: {preview(v)}")
            break
    return 0


if __name__ == "__main__":
    sys.exit(main())
