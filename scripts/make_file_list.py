"""Build file lists for the two datasets (one 'repo:path' spec per line)."""
import sys

from huggingface_hub import HfApi

NEB = "nebius/SWE-rebench-openhands-trajectories"
NVI = "nvidia/Open-SWE-Traces"

api = HfApi()
which = sys.argv[1]
out = sys.argv[2]
info = api.dataset_info(NVI if which == "nvidia" else NEB, files_metadata=True)
paths = sorted(f.rfilename for f in info.siblings if f.rfilename.endswith(".parquet"))
with open(out, "w") as fh:
    prefix = "nvidia" if which == "nvidia" else "nebius"
    for p in paths:
        fh.write(f"{prefix}:{p}\n")
print(f"{which}: {len(paths)} files -> {out}")
