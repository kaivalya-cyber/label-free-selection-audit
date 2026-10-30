# Kaggle quota log — PREREG-3 judge

Cap for this study: **12 GPU-hours total** (pilot + main), sessions of at most 9 h, user-approved
2026-10-29. The account's weekly quota is not readable through the CLI (`kaggle quota` fails with
`not enough values to unpack`), so spend is tracked here from each session's logged start/end.

| # | UTC start | kernel | accelerator | purpose | duration | GPU-h spent | result |
|---|---|---|---|---|---|---|---|
| 0 | 2026-10-29T22:27Z | gemma-judge-cpu-probe | none | processor/chat-template probe, no model | ~1 min | 0 | COMPLETE: transformers 5.16.1, suffix `<|channel>thought\n<channel|>`, YES 26915 / NO 7018, pad 0 |
| 1 | 2026-10-29T22:31Z | gemma-judge-pilot-run v1 | NvidiaTeslaT4 (2 x T4) | pilot, first push | ~1 min | ~0.02 | ERROR at 7 s: the dataset mounted at `/kaggle/input/datasets/...`, not `/kaggle/input/<slug>`; 0 judge scores |
