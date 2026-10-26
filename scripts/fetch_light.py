"""Stream lightweight columns of HF parquet shards into a local parquet cache.

Reads only the requested columns via HTTP range requests (no full-file download).

Usage (single file test):
  .venv/bin/python scripts/fetch_light.py --files nvidia:data/openhands/qwen38_flash_next/swe-rebench-v2/train-00005-of-00006.parquet \
      --cols instance_id,repo,resolved,messages.list.element.role --out out/test.parquet
"""
import argparse
import json
import time

import pyarrow as pa
import pyarrow.parquet as pq
from huggingface_hub import HfFileSystem

NEB = "nebius/SWE-rebench-openhands-trajectories"
NVI = "nvidia/Open-SWE-Traces"


def parse_file_arg(spec):
    prefix, path = spec.split(":", 1)
    if prefix == "nvidia":
        return NVI, path
    if prefix == "nebius":
        return NEB, path
    if "/" in prefix:  # e.g. nebius/SWE-rebench
        return prefix, path
    raise ValueError(spec)


def read_batches(fs, repo, path, cols, batch_size=512):
    url = f"datasets/{repo}/{path}"
    with fs.open(url, "rb") as f:
        pf = pq.ParquetFile(f)
        for b in pf.iter_batches(batch_size=batch_size, columns=cols):
            yield b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="*", default=[])
    ap.add_argument("--from-list", default=None, help="text file, one spec (nvidia:path / nebius:path) per line")
    ap.add_argument("--cols", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    specs = list(a.files)
    if a.from_list:
        with open(a.from_list) as fh:
            specs += [ln.strip() for ln in fh if ln.strip()]
    if not specs:
        raise SystemExit("no files given")

    cols = a.cols.split(",")
    fs = HfFileSystem()
    writer = None
    n_rows = 0
    t0 = time.time()
    out = a.out
    for spec in specs:
        repo, path = parse_file_arg(spec)
        for b in read_batches(fs, repo, path, cols):
            b = b.append_column("_src_path", pa.array([path] * b.num_rows, type=pa.string()))
            if writer is None:
                writer = pq.ParquetWriter(out, b.schema)
            writer.write_table(pa.Table.from_batches([b]))
            n_rows += b.num_rows
        print(f"{path}: cumulative rows={n_rows} t={time.time()-t0:.1f}s", flush=True)
    if writer is not None:
        writer.close()
    print(json.dumps({"out": out, "rows": n_rows, "seconds": round(time.time() - t0, 1)}))


if __name__ == "__main__":
    main()
