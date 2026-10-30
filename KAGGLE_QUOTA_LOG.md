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
