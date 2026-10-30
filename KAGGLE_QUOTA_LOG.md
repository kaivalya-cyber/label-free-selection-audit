# Kaggle quota log — PREREG-3 judge

Cap for this study: **12 GPU-hours total** (pilot + main), sessions of at most 9 h, user-approved
2026-10-29. The account's weekly quota is not readable through the CLI (`kaggle quota` fails with
`not enough values to unpack`), so spend is tracked here from each session's logged start/end.

| # | UTC start | kernel | accelerator | purpose | duration | GPU-h spent | result |
|---|---|---|---|---|---|---|---|
| 0 | 2026-10-29T22:27Z | gemma-judge-cpu-probe | none | processor/chat-template probe, no model | ~1 min | 0 | COMPLETE: transformers 5.16.1, suffix `<|channel>thought\n<channel|>`, YES 26915 / NO 7018, pad 0 |
| 1 | 2026-10-29T22:31Z | gemma-judge-pilot-run v1 | NvidiaTeslaT4 (2 x T4) | pilot, first push | ~1 min | ~0.02 | ERROR at 7 s: the dataset mounted at `/kaggle/input/datasets/...`, not `/kaggle/input/<slug>`; 0 judge scores |
| 2 | 2026-10-29T22:45Z | gemma-judge-pilot-run v2 | NvidiaTeslaT4 (2 x T4) | pilot, corrected bundle path | ~4 min | ~0.13 | ERROR: `find_model` missed the `/1/` mount level, fell back to kagglehub; NF4 load with 13 GiB caps offloaded to CPU/disk; 0 judge scores |
| 3 | 2026-10-29T23:10Z | gemma-judge-loaddiag v1 | NvidiaTeslaT4 (2 x T4) | model-path / load diagnostic | ~2 min | ~0.07 | ERROR: `paths []` (glob missed `/1/`); no model loaded |
| 4 | 2026-10-29T23:16Z | gemma-judge-loaddiag v2 | NvidiaTeslaT4 (2 x T4) | NF4 load with full GPU memory | ~3 min | ~0.10 | ERROR: `device_map="auto"` still offloads; 3-D MoE expert tensors are not quantised by bitsandbytes; 0 scores |
| 5 | 2026-10-29T23:24Z | gemma-judge-metaprobe v1/v2 | none (CPU) | inspect Gemma 4 MoE module classes | ~12 min, still running | 0 | CPU only; v1 errored on a moved accelerate helper, v2 printing module source; no GPU |
| 6 | 2026-10-30T06:55Z | gemma-judge-lsgguf | none (CPU) | list GGUF mount and toolchain | ~1 min | 0 | CPU only; GGUF dir and version present; CPU image has no nvcc |
| 7 | 2026-10-30T07:00Z | gemma-judge-gpuenv | NvidiaTeslaT4 (2 x T4) | GPU image toolchain | ~1 min | ~0.03 | COMPLETE: nvcc 12.8, 2 x T4, GGUF 14,439,361,440 bytes + mmproj |
| 8 | 2026-10-30T07:05Z | gemma-judge-findcuda | NvidiaTeslaT4 (2 x T4) | locate the driver library for CMake | ~1 min | ~0.03 | COMPLETE: `/usr/local/nvidia/lib64/libcuda.so`; not in `/usr/lib` |
| 9 | 2026-10-30T07:10Z | gemma-judge-buildllama v1 | NvidiaTeslaT4 (2 x T4) | CUDA wheel build, first attempt | ~1 min | ~0.02 | ERROR: CMake `CUDA::cuda_driver` target missing |
| 10 | 2026-10-30T07:14Z | gemma-judge-buildllama v2 | NvidiaTeslaT4 (2 x T4) | CUDA wheel build, verbose | ~1 min | ~0.02 | ERROR: driver library not in `/usr/lib`; symlink target absent |
| 11 | 2026-10-30T07:18Z | gemma-judge-buildllama v3 | NvidiaTeslaT4 (2 x T4) | CUDA wheel build, symlink attempt | ~2 min | ~0.04 | ERROR: same `CUDA::cuda_driver`; symlink loop checked the wrong path |
| 12 | 2026-10-30T07:24Z | gemma-judge-buildllama v4 | NvidiaTeslaT4 (2 x T4) | CUDA wheel build from the real driver path | ~28 min | ~0.47 | Wheel built (`llama_cpp_python-0.3.36`, sha256 `d1c9ac…2230`); kernel ERROR only because the import check ran before `diskcache` was installed. No model, no scores. |
| 13 | 2026-10-30T08:10Z | gemma-judge-pilot-gguf v1 | NvidiaTeslaT4 (2 x T4) | pilot, first GGUF attempt | ~5 min | ~0.08 | ERROR: worker exposed 1 T4 (`ggml_cuda_init: found 1`), context creation failed; 0 scores |
| 14 | 2026-10-30T08:18Z | gemma-judge-pilot-gguf v2 | NvidiaTeslaT4 (2 x T4) | pilot, first 200 pairs | 25.9 min | **0.43** | **COMPLETE: 388 attempts, 1,452,435 prefill tokens, 993.923 tok/s, 0 empty patches; sealed sha256 `f042359d…b434`; model sha256 `4c856523…54c5`** |
| 15 | 2026-10-30T08:55Z | gemma-judge-main-gguf | NvidiaTeslaT4 (2 x T4) | main run, pairs 200–4225, reuse pilot | in progress | — | N = 4,226 (D12); predicted 7.77 h main; checkpointed shards of 200; no partial analysis |
