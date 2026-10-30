"""PREREG-3 judge runner, D14 backend: Gemma 4 26B-A4B QAT Q4_0 GGUF via llama.cpp.

The frozen NF4 path cannot load this architecture on 2xT4: the 30 MoE layers store all
128 experts as 3-D `nn.Parameter` tensors, which bitsandbytes does not quantise.  D14 replaces
the *backend and quantisation format* only.  The pair sample, the truncated prompt content
(precomputed with the HF Gemma 4 tokenizer in `judge_build_pairs.py`), the D13 no-thinking
suffix, the single-token YES/NO score and the D12 N rule are unchanged.

Scores are written to `sealed/pilot_scores.parquet`; only throughput and token counts are
printed.  No score is summarised or opened by this script.

Usage (Kaggle, inside the attached bundle):
    python judge_run_gguf.py --mode pilot --max-pairs 200 --out /kaggle/working
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

BUNDLE_KAGGLE = Path("/kaggle/input/gemma-judge-gguf")
MODEL_REF = "google/gemma-4/gguf/gemma-4-26b-a4b-it-qat-q4_0-gguf/2"
YES_ID, NO_ID = 26915, 7018
SHARD_EVERY = 200


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_bundle(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    if BUNDLE_KAGGLE.is_dir():
        return BUNDLE_KAGGLE
    hits = sorted(glob.glob("/kaggle/input/**/judge_run_gguf.py", recursive=True), key=len)
    if hits:
        return Path(hits[0]).parent
    return Path(__file__).resolve().parent


def find_gguf(explicit: str | None) -> str:
    if explicit:
        return explicit
    hits = [p for p in glob.glob("/kaggle/input/models/**/*.gguf", recursive=True)
            if "mmproj" not in Path(p).name.lower()]
    if not hits:
        raise FileNotFoundError("no non-mmproj GGUF under /kaggle/input/models")
    return max(hits, key=os.path.getsize)


def gpu_names() -> list[str]:
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total",
                            "--format=csv,noheader"], capture_output=True, text=True, timeout=20)
        return [x.strip() for x in r.stdout.splitlines() if x.strip()]
    except Exception:
        return []


def load_llm(path: str, n_ctx: int, n_batch: int, n_ubatch: int):
    import llama_cpp
    assert llama_cpp.llama_supports_gpu_offload(), "llama.cpp was built without CUDA offload"
    t0 = time.time()
    kwargs = dict(model_path=path, n_gpu_layers=-1, split_mode=1,
                  tensor_split=[0.5, 0.5], n_ctx=n_ctx, n_batch=n_batch,
                  n_ubatch=n_ubatch, logits_all=False, verbose=False, seed=0,
                  n_threads=4)
    try:
        llm = llama_cpp.Llama(**kwargs, flash_attn=False)
    except TypeError:
        llm = llama_cpp.Llama(**kwargs)
    return llm, llama_cpp, time.time() - t0


def check_special_tokens(llm) -> None:
    """The frozen template and answer ids must survive the GGUF tokenizer unchanged."""
    y = llm.tokenize(b"YES", add_bos=False, special=True)
    n = llm.tokenize(b"NO", add_bos=False, special=True)
    turn = llm.tokenize(b"<|turn>", add_bos=False, special=True)
    close = llm.tokenize(b"<turn|>", add_bos=False, special=True)
    assert y == [YES_ID], ("YES id", y)
    assert n == [NO_ID], ("NO id", n)
    assert turn == [105], ("<|turn> id", turn)
    assert close == [106], ("<turn|> id", close)


def prompt_text(content: str) -> str:
    """D13 no-thinking rendering, with <bos> supplied by tokenize(add_bos=True)."""
    return (f"<|turn>user\n{content}<turn|>\n<|turn>model\n"
            f"<|channel>thought\n<channel|>")


def read_last_logits(llm, llama_cpp) -> np.ndarray:
    n_vocab = llm.n_vocab()
    ptr = llm._ctx.get_logits()
    if not ptr:
        raise RuntimeError("llama_get_logits returned NULL")
    return np.ctypeslib.as_array(ptr, shape=(n_vocab,)).astype(np.float64, copy=True)


def score_one(llm, llama_cpp, ids: list[int]) -> tuple[float, int, float]:
    llm.reset()
    t = time.perf_counter()
    llm.eval(ids)
    dt = time.perf_counter() - t
    assert llm.n_tokens == len(ids), (llm.n_tokens, len(ids))
    z = read_last_logits(llm, llama_cpp)[[YES_ID, NO_ID]]
    m = float(z.max())
    ey, en = math.exp(float(z[0]) - m), math.exp(float(z[1]) - m)
    return ey / (ey + en), len(ids), dt


def write_parquet(rows: list[dict], path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(path, index=False)
    return sha256_file(path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", default=None)
    ap.add_argument("--gguf", default=None)
    ap.add_argument("--mode", choices=["pilot", "main"], default="pilot")
    ap.add_argument("--max-pairs", type=int, default=200)
    ap.add_argument("--start-pair", type=int, default=0)
    ap.add_argument("--end-pair", type=int, default=4226)
    ap.add_argument("--out", default="/kaggle/working" if Path("/kaggle/working").is_dir()
                    else "out/judge/gguf_run")
    ap.add_argument("--wall-min", type=float, default=480)
    ap.add_argument("--n-ctx", type=int, default=10240)
    ap.add_argument("--n-batch", type=int, default=512)
    ap.add_argument("--n-ubatch", type=int, default=256)
    ap.add_argument("--reuse", default=None, help="parquet of trajectory_id,p_yes already scored")
    ap.add_argument("--limit", type=int, default=0, help="debug only; 0 = all selected attempts")
    args = ap.parse_args()

    bundle, out = find_bundle(args.bundle), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((bundle / "manifest.json").read_text())
    pairs = pd.read_parquet(bundle / "pairs.parquet")
    attempts = pd.read_parquet(bundle / "attempts.parquet")
    # One dataset serves both modes: the pilot selects the first 200 pairs from the full frozen
    # file. Hash the whole file, not the selected prefix. A dedicated pilot bundle (200 rows)
    # instead carries the pilot_* hashes.
    key_pairs = ("pairs_sha256" if len(pairs) == manifest.get("pair_sample")
                 else "pilot_pairs_sha256")
    key_attempts = ("attempts_sha256" if len(attempts) == manifest.get("distinct_attempts")
                    else "pilot_attempts_sha256")
    assert sha256_file(bundle / "pairs.parquet") == manifest[key_pairs], "pair file hash mismatch"
    assert sha256_file(bundle / "attempts.parquet") == manifest[key_attempts], \
        "attempt file hash mismatch"
    assert "content" in attempts.columns, "attempts.parquet lacks frozen prompt content"

    if args.mode == "pilot":
        pairs = pairs[pairs.pair_id < args.max_pairs].copy()
    else:
        pairs = pairs[(pairs.pair_id >= args.start_pair) & (pairs.pair_id < args.end_pair)].copy()
    tids = sorted(set(pairs.pos_tid.astype(str)) | set(pairs.neg_tid.astype(str)))
    att = attempts[attempts.trajectory_id.astype(str).isin(tids)].copy()
    att["trajectory_id"] = att.trajectory_id.astype(str)
    assert len(att) == len(tids), (len(att), len(tids))

    reused: dict[str, float] = {}
    if args.reuse and Path(args.reuse).exists():
        r = pd.read_parquet(args.reuse, columns=["trajectory_id", "p_yes"])
        reused = dict(zip(r.trajectory_id.astype(str), r.p_yes.astype(float)))
        att = att[~att.trajectory_id.isin(reused)].copy()
        print(f"reusing {len(reused)} sealed scores", flush=True)
    if args.limit:
        att = att.head(args.limit)

    gguf_path = find_gguf(args.gguf)
    print(f"gguf={gguf_path} size={os.path.getsize(gguf_path)} bundle={bundle} "
          f"attempts_to_score={len(att)}", flush=True)
    llm, llama_cpp, load_s = load_llm(gguf_path, args.n_ctx, args.n_batch, args.n_ubatch)
    check_special_tokens(llm)
    model_sha = sha256_file(gguf_path)
    print(f"loaded_s={load_s:.1f} model_sha256={model_sha} "
          f"gpus={gpu_names()}", flush=True)

    t0 = time.time()
    prompt_rows: list[dict] = []
    for row in att.itertuples():
        text = prompt_text(row.content)
        assert text.endswith("<channel|>"), text[-80:]
        ids = llm.tokenize(text.encode("utf-8"), add_bos=True, special=True)
        assert ids[0] == 2, ("BOS", ids[:3])
        prompt_rows.append({
            "trajectory_id": str(row.trajectory_id), "ids": ids, "n_tokens": len(ids),
            "prompt_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "issue_truncated": bool(row.issue_truncated),
            "patch_truncated": bool(row.patch_truncated),
            "empty_patch": not str(row.patch).strip(),
            "prompt_tokens_estimate": int(row.prompt_tokens_estimate),
        })
    prompt_s = time.time() - t0
    deltas = [p["n_tokens"] - p["prompt_tokens_estimate"] for p in prompt_rows]
    print(f"prompts={len(prompt_rows)} build_s={prompt_s:.1f} "
          f"max_tokens={max(p['n_tokens'] for p in prompt_rows)} "
          f"mean_delta_vs_estimate={np.mean(deltas):.2f} "
          f"max_delta={max(deltas)}", flush=True)
    assert max(p["n_tokens"] for p in prompt_rows) < args.n_ctx

    fixed = [{"trajectory_id": p["trajectory_id"], "p_yes": 0.0, "n_tokens": 0,
              "issue_truncated": p["issue_truncated"], "patch_truncated": p["patch_truncated"],
              "empty_patch": True, "prompt_sha256": p["prompt_sha256"]}
             for p in prompt_rows if p["empty_patch"]]
    live = [p for p in prompt_rows if not p["empty_patch"]]
    print(f"empty_patch={len(fixed)} live={len(live)}", flush=True)

    rows: list[dict] = []
    pending: list[dict] = []
    real_tokens = padded_tokens = 0
    prefill_s = 0.0
    start = time.time()
    status = "complete"
    shard_hashes: dict[str, str] = {}

    def metrics_now() -> dict:
        wall = time.time() - start
        return {
            "mode": args.mode, "status": status, "backend": "llama.cpp",
            "attempts_scored": len(rows), "attempts_selected": len(live),
            "empty_patch": len(fixed), "reused": len(reused),
            "real_prefill_tokens": real_tokens, "padded_prefill_tokens": padded_tokens,
            "prefill_seconds": round(prefill_s, 3),
            "prefill_tokens_per_sec_real": round(real_tokens / prefill_s, 3) if prefill_s else 0.0,
            "prefill_tokens_per_sec_padded": round(padded_tokens / prefill_s, 3)
            if prefill_s else 0.0,
            "prompt_build_seconds": round(prompt_s, 1),
            "model_load_seconds": round(load_s, 1),
            "wall_seconds": round(wall, 1),
            "model_ref": MODEL_REF, "gguf_path": gguf_path,
            "gguf_sha256": model_sha, "llama_cpp_version": llama_cpp.__version__,
            "gpu_names": gpu_names(), "n_ctx": args.n_ctx, "n_batch": args.n_batch,
            "n_ubatch": args.n_ubatch, "yes_id": YES_ID, "no_id": NO_ID,
            "judge_core_sha256": sha256_file(bundle / "judge_core.py")
            if (bundle / "judge_core.py").exists() else None,
            "pairs_file_sha256": sha256_file(bundle / "pairs.parquet"),
            "attempts_file_sha256": sha256_file(bundle / "attempts.parquet"),
            "mean_n_tokens": round(float(np.mean([p["n_tokens"] for p in live])), 1)
            if live else 0.0,
            "mean_prompt_tokens_estimate": round(
                float(np.mean([p["prompt_tokens_estimate"] for p in live])), 1) if live else 0.0,
        }

    def flush() -> None:
        if not pending:
            return
        if args.mode == "pilot":
            return
        name = f"shard_{len(shard_hashes):05d}.parquet"
        h = write_parquet(pending, out / "shards" / name)
        shard_hashes[name] = h
        (out / "shards" / "manifest.json").write_text(json.dumps(shard_hashes, indent=1) + "\n")
        pending.clear()
        (out / "throughput.json").write_text(json.dumps(metrics_now(), indent=1) + "\n")

    for i, q in enumerate(live):
        p, ntok, dt = score_one(llm, llama_cpp, q["ids"])
        prefill_s += dt
        real_tokens += ntok
        padded_tokens += ntok
        pending.append({"trajectory_id": q["trajectory_id"], "p_yes": float(p),
                        "n_tokens": q["n_tokens"],
                        "issue_truncated": q["issue_truncated"],
                        "patch_truncated": q["patch_truncated"], "empty_patch": False,
                        "prompt_sha256": q["prompt_sha256"]})
        rows.append(pending[-1])
        if len(pending) >= SHARD_EVERY:
            flush()
        if (time.time() - start) / 60 > args.wall_min:
            status = "wall_limit"
            break
        if (i + 1) % 50 == 0:
            print(f"scored={i + 1}/{len(live)} tok/s="
                  f"{real_tokens / prefill_s if prefill_s else 0:.1f}", flush=True)

    if args.mode == "pilot":
        all_rows = rows + fixed
        h = write_parquet(all_rows, out / "sealed" / "pilot_scores.parquet")
        (out / "sealed" / "manifest.json").write_text(
            json.dumps({"sha256": h, "rows": len(all_rows), "gguf_sha256": model_sha,
                        "model_ref": MODEL_REF, "llama_cpp_version": llama_cpp.__version__,
                        "judge_core_sha256": sha256_file(bundle / "judge_core.py")
                        if (bundle / "judge_core.py").exists() else None}, indent=1) + "\n")
        metrics = metrics_now()
        metrics["sealed_scores_sha256"] = h
        metrics["sealed_rows"] = len(all_rows)
        (out / "pilot_throughput.json").write_text(json.dumps(metrics, indent=1) + "\n")
    else:
        # Empty patches are fixed at 0 and have no forward pass; still persist them so the
        # analysis has a complete row for every sampled attempt.
        pending.extend(fixed)
        flush()
        metrics = metrics_now()
        metrics["shards"] = shard_hashes
        (out / "throughput.json").write_text(json.dumps(metrics, indent=1) + "\n")

    print(json.dumps({k: v for k, v in metrics.items()
                      if k not in {"gpu_names", "shards"}}, indent=1), flush=True)


if __name__ == "__main__":
    main()
