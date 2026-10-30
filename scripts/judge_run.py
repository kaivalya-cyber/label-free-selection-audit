"""PREREG-3 judge runner (Kaggle script kernel or local CLI; no notebook state).

Scores distinct attempts, not pairs: the analysis joins the attempt scores to the frozen pair
order. The pilot writes its scores to `sealed/pilot_scores.parquet` and only throughput/token
counts to `pilot_throughput.json`; it never prints or summarises a score.

Usage (Kaggle, inside the attached bundle):
    python judge_run.py --mode pilot --max-pairs 200 --out /kaggle/working --wall-min 480

The kernel entry is a 4-line `script.py` that adds the bundle to sys.path and runs this file.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

BUNDLE_FALLBACK = Path(__file__).resolve().parent
BUNDLE_KAGGLE = Path("/kaggle/input/gemma-judge-pilot")
MODEL_REPO = "google/gemma-4-26B-A4B-it"
SHARD_EVERY = 200


def sha256_file(path: Path) -> str:
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
    return BUNDLE_FALLBACK


def find_model(explicit: str | None) -> str:
    if explicit:
        return explicit
    hits = [p for p in glob.glob("/kaggle/input/**/gemma-4-26b-a4b-it/config.json",
                                  recursive=True)
            if "assistant" not in p]
    if hits:
        return str(Path(sorted(hits)[0]).parent)
    import kagglehub
    return kagglehub.model_download("google/gemma-4/transformers/gemma-4-26b-a4b-it")


def load_model(model_path: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoProcessor, BitsAndBytesConfig

    processor = AutoProcessor.from_pretrained(model_path, local_files_only=True)
    if processor.tokenizer.pad_token_id is None:
        processor.tokenizer.pad_token = processor.tokenizer.eos_token
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_use_double_quant=True,
                             bnb_4bit_compute_dtype=torch.bfloat16)
    n_gpu = torch.cuda.device_count()
    assert n_gpu >= 1, "no CUDA device"
    t0 = time.time()
    kwargs = {"max_memory": {i: "13GiB" for i in range(n_gpu)}} if n_gpu > 1 else {}
    model = AutoModelForCausalLM.from_pretrained(
        model_path, quantization_config=bnb, device_map="auto", dtype=torch.bfloat16,
        attn_implementation="sdpa", local_files_only=True, **kwargs)
    model.eval()
    load_s = time.time() - t0
    torch.cuda.synchronize()
    return model, processor, load_s


def score_batch(model, ids_list: list[list[int]]) -> tuple[np.ndarray, int, int]:
    """Left-padded forward pass; returns (p_yes, real tokens, padded tokens)."""
    import torch

    pad_id = model.config.pad_token_id if getattr(model.config, "pad_token_id", None) is not None else 0
    max_len = max(len(x) for x in ids_list)
    input_ids = torch.full((len(ids_list), max_len), pad_id, dtype=torch.long)
    mask = torch.zeros((len(ids_list), max_len), dtype=torch.long)
    for i, ids in enumerate(ids_list):
        input_ids[i, -len(ids):] = torch.tensor(ids, dtype=torch.long)
        mask[i, -len(ids):] = 1
    input_ids = input_ids.to(model.device)
    mask = mask.to(model.device)
    out = model(input_ids=input_ids, attention_mask=mask)
    logits = out.logits[:, -1, :]
    z = logits[:, [26915, 7018]].float()
    p = torch.softmax(z, dim=-1)[:, 0]
    return p.detach().cpu().numpy(), int(mask.sum().item()), int(input_ids.numel())


def write_parquet(rows: list[dict], path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(path, index=False)
    return sha256_file(path)


def render(processor, content: str) -> str:
    try:
        return processor.apply_chat_template([{"role": "user", "content": content}],
                                             tokenize=False, add_generation_prompt=True,
                                             enable_thinking=False)
    except TypeError:
        return processor.apply_chat_template([{"role": "user", "content": content}],
                                             tokenize=False, add_generation_prompt=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--mode", choices=["pilot", "main"], default="pilot")
    ap.add_argument("--max-pairs", type=int, default=200)
    ap.add_argument("--out", default="/kaggle/working" if Path("/kaggle/working").is_dir()
                    else "out/judge/run")
    ap.add_argument("--wall-min", type=float, default=480)
    ap.add_argument("--max-tokens", type=int, default=12000)
    ap.add_argument("--max-batch", type=int, default=4)
    ap.add_argument("--reuse", default=None, help="parquet of trajectory_id,p_yes already scored")
    ap.add_argument("--limit", type=int, default=0, help="debug only; 0 = all selected attempts")
    args = ap.parse_args()

    import torch

    bundle, out = find_bundle(args.bundle), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((bundle / "manifest.json").read_text())
    pairs = pd.read_parquet(bundle / "pairs.parquet")
    attempts = pd.read_parquet(bundle / "attempts.parquet")
    assert sha256_file(bundle / "pairs.parquet") == manifest.get(
        "pilot_pairs_sha256", manifest.get("pairs_sha256")), "pair file hash mismatch"
    assert sha256_file(bundle / "attempts.parquet") == manifest.get(
        "pilot_attempts_sha256", manifest.get("attempts_sha256")), "attempt file hash mismatch"

    pairs = pairs[pairs.pair_id < args.max_pairs].copy()
    tids = sorted(set(pairs.pos_tid) | set(pairs.neg_tid))
    att = attempts[attempts.trajectory_id.isin(tids)].copy()
    assert len(att) == len(tids), (len(att), len(tids))

    reused: dict[str, float] = {}
    if args.reuse and Path(args.reuse).exists():
        r = pd.read_parquet(args.reuse, columns=["trajectory_id", "p_yes"])
        reused = dict(zip(r.trajectory_id.astype(str), r.p_yes.astype(float)))
        att = att[~att.trajectory_id.astype(str).isin(reused)].copy()
        print(f"reusing {len(reused)} sealed scores", flush=True)
    if args.limit:
        att = att.head(args.limit)

    model_path = find_model(args.model)
    print(f"model={model_path} bundle={bundle} attempts_to_score={len(att)}", flush=True)
    model, processor, load_s = load_model(model_path)

    sys.path.insert(0, str(bundle))
    import judge_core as jc

    assert (jc.YES_ID, jc.NO_ID) == (26915, 7018)
    prompt_rows = []
    t0 = time.time()
    for row in att.itertuples():
        built = jc.build_content(row.issue_text, row.patch, processor.tokenizer)
        text = render(processor, built["content"])
        ids = jc.encode_ids(processor.tokenizer, text)
        # Thinking is disabled, so the template closes with the empty thought block; the next
        # token is the answer. A prompt ending at the model turn instead would enable thinking.
        assert text.rstrip().endswith("<channel|>"), text[-120:]
        prompt_rows.append({"trajectory_id": str(row.trajectory_id), "ids": ids,
                            "n_tokens": len(ids),
                            "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
                            "issue_truncated": bool(built["issue_truncated"]),
                            "patch_truncated": bool(built["patch_truncated"]),
                            "empty_patch": not str(row.patch).strip()})
    prompt_s = time.time() - t0
    print(f"prompts={len(prompt_rows)} build_s={prompt_s:.1f} "
          f"max_tokens={max(p['n_tokens'] for p in prompt_rows)}", flush=True)

    fixed = [{"trajectory_id": p["trajectory_id"], "p_yes": 0.0, "n_tokens": 0,
              "issue_truncated": p["issue_truncated"], "patch_truncated": p["patch_truncated"],
              "empty_patch": True, "prompt_sha256": p["text_sha256"]}
             for p in prompt_rows if p["empty_patch"]]
    live = [p for p in prompt_rows if not p["empty_patch"]]
    lengths = [p["n_tokens"] for p in live]
    batches = jc.pack_batches(lengths, max_tokens=args.max_tokens, max_batch=args.max_batch)
    print(f"batches={len(batches)} empty_patch={len(fixed)} live={len(live)}", flush=True)

    rows: list[dict] = []
    pending: list[dict] = []
    real_tokens = padded_tokens = 0
    prefill_s = 0.0
    oom_splits = 0
    start = time.time()
    status = "complete"
    shard_hashes: dict[str, str] = {}
    torch.cuda.reset_peak_memory_stats()

    def metrics_now() -> dict:
        wall = time.time() - start
        return {"mode": args.mode, "status": status, "attempts_scored": len(rows),
                "attempts_selected": len(live), "empty_patch": len(fixed),
                "real_prefill_tokens": real_tokens, "padded_prefill_tokens": padded_tokens,
                "prefill_seconds": round(prefill_s, 3),
                "prefill_tokens_per_sec_real": round(real_tokens / prefill_s, 3) if prefill_s else 0.0,
                "prefill_tokens_per_sec_padded": round(padded_tokens / prefill_s, 3)
                if prefill_s else 0.0,
                "batches": len(batches), "oom_splits": oom_splits,
                "model_load_seconds": round(load_s, 1), "prompt_build_seconds": round(prompt_s, 1),
                "wall_seconds": round(wall, 1),
                "peak_memory_allocated_gb": round(torch.cuda.max_memory_allocated() / 1e9, 2),
                "gpu_count": torch.cuda.device_count(),
                "gpu_names": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
                "model": MODEL_REPO, "model_path": model_path,
                "judge_core_sha256": sha256_file(bundle / "judge_core.py"),
                "pairs_file_sha256": sha256_file(bundle / "pairs.parquet"),
                "mean_n_tokens": round(float(np.mean([p["n_tokens"] for p in live])), 1)
                if live else 0.0}

    def flush() -> None:
        if not pending:
            return
        if args.mode == "pilot":
            return  # pilot writes one sealed file at the end
        name = f"shard_{len(shard_hashes):05d}.parquet"
        h = write_parquet(pending, out / "shards" / name)
        shard_hashes[name] = h
        (out / "shards" / "manifest.json").write_text(json.dumps(shard_hashes, indent=1) + "\n")
        pending.clear()
        (out / "throughput.json").write_text(json.dumps(metrics_now(), indent=1) + "\n")

    def run_indices(idx: list[int]) -> None:
        nonlocal real_tokens, padded_tokens, prefill_s, oom_splits
        try:
            torch.cuda.synchronize()
            t = time.perf_counter()
            p, real, padded = score_batch(model, [live[i]["ids"] for i in idx])
            torch.cuda.synchronize()
            dt = time.perf_counter() - t
        except torch.cuda.OutOfMemoryError:
            oom_splits += 1
            torch.cuda.empty_cache()
            if len(idx) == 1:
                raise
            mid = len(idx) // 2
            run_indices(idx[:mid])
            run_indices(idx[mid:])
            return
        prefill_s += dt
        real_tokens += real
        padded_tokens += padded
        for i, pv in zip(idx, p):
            q = live[i]
            pending.append({"trajectory_id": q["trajectory_id"], "p_yes": float(pv),
                            "n_tokens": q["n_tokens"],
                            "issue_truncated": q["issue_truncated"],
                            "patch_truncated": q["patch_truncated"], "empty_patch": False,
                            "prompt_sha256": q["text_sha256"]})
        rows.extend(pending[-len(idx):])
        if len(pending) >= SHARD_EVERY:
            flush()

    for b in batches:
        run_indices(b)
        if (time.time() - start) / 60 > args.wall_min:
            status = "wall_limit"
            break

    if args.mode == "pilot":
        all_rows = rows + fixed
        h = write_parquet(all_rows, out / "sealed" / "pilot_scores.parquet")
        (out / "sealed" / "manifest.json").write_text(
            json.dumps({"sha256": h, "rows": len(all_rows),
                        "judge_core_sha256": sha256_file(bundle / "judge_core.py")}, indent=1) + "\n")
        metrics = metrics_now()
        metrics["sealed_scores_sha256"] = h
        metrics["sealed_rows"] = len(all_rows)
        (out / "pilot_throughput.json").write_text(json.dumps(metrics, indent=1) + "\n")
    else:
        flush()
        metrics = metrics_now()
        metrics["shards"] = shard_hashes
        (out / "throughput.json").write_text(json.dumps(metrics, indent=1) + "\n")

    print(json.dumps({k: v for k, v in metrics.items()
                      if k not in {"shards", "gpu_names"}}, indent=1), flush=True)


if __name__ == "__main__":
    main()
