"""Fetch only {trajectory_id, instance_id, patch} for one config, to a local parquet cache.

Usage:
  .venv/bin/python scripts/fetch_patches.py --dataset nvidia --prefix data/openhands/qwen38_27b/swe-rebench-v2 --tag v1.2_openhands_qwen38_27b_swe-rebench-v2
  .venv/bin/python scripts/fetch_patches.py --dataset nebius --tag nebius_openhands

Reads patch text only (range requests); nothing else from the trajectories is downloaded.
"""
import argparse
import json
import os
import time

import pyarrow as pa
import pyarrow.parquet as pq
from huggingface_hub import HfFileSystem

NEB = "nebius/SWE-rebench-openhands-trajectories"
NVI = "nvidia/Open-SWE-Traces"


def batches_nvidia(fs, path, batch_size=256):
    with fs.open(f"datasets/{NVI}/{path}", "rb") as f:
        pf = pq.ParquetFile(f)
        for b in pf.iter_batches(batch_size=batch_size,
                                 columns=["trajectory_id", "instance_id", "metadata.model_patch.patch"]):
            tids, iids, patches = [], [], []
            for row in b.to_pylist():
                mp = (row.get("metadata") or {}).get("model_patch") or {}
                tids.append(row["trajectory_id"])
                iids.append(row["instance_id"])
                patches.append(mp.get("patch"))
            yield pa.table({"trajectory_id": tids, "instance_id": iids, "patch": patches})


def batches_nebius(fs, path, batch_size=1024):
    with fs.open(f"datasets/{NEB}/{path}", "rb") as f:
        pf = pq.ParquetFile(f)
        for b in pf.iter_batches(batch_size=batch_size,
                                 columns=["trajectory_id", "instance_id", "model_patch"]):
            yield pa.table({"trajectory_id": b.column("trajectory_id").to_pylist(),
                            "instance_id": b.column("instance_id").to_pylist(),
                            "patch": b.column("model_patch").to_pylist()})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", choices=["nvidia", "nebius"], required=True)
    ap.add_argument("--prefix", default=None, help="nvidia subtree, e.g. data/openhands/qwen38_27b/swe-rebench-v2")
    ap.add_argument("--tag", required=True)
    a = ap.parse_args()
    os.makedirs("out/patches", exist_ok=True)
    out = f"out/patches/{a.tag}.parquet"

    fs = HfFileSystem()
    if a.dataset == "nvidia":
        from huggingface_hub import HfApi
        info = HfApi().dataset_info(NVI, files_metadata=True)
        paths = sorted(f.rfilename for f in info.siblings
                       if f.rfilename.endswith(".parquet") and f.rfilename.startswith(a.prefix + "/"))
    else:
        paths = ["trajectories.parquet"]

    t0, n, writer = time.time(), 0, None
    for p in paths:
        gen = batches_nvidia(fs, p) if a.dataset == "nvidia" else batches_nebius(fs, p)
        for tbl in gen:
            if writer is None:
                writer = pq.ParquetWriter(out, tbl.schema, compression="zstd")
            writer.write_table(tbl)
            n += tbl.num_rows
        print(f"{a.tag} {p}: rows={n} t={time.time()-t0:.0f}s", flush=True)
    if writer:
        writer.close()
    print(json.dumps({"tag": a.tag, "out": out, "rows": n, "files": len(paths),
                      "seconds": round(time.time() - t0, 1)}))


if __name__ == "__main__":
    main()
