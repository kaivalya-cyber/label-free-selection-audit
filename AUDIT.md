# AUDIT — paper.md against the frozen records

Generated 31 October 2026. This file checks the writeup against
[CLAIMS_LEDGER.md](CLAIMS_LEDGER.md) and the result JSONs, not against the prose
of any other document. Where a document disagrees with a JSON, the JSON wins and
the disagreement is listed in §6.

**Scope.** Every quantitative result, sample size, threshold, and methods
constant in the body, abstract, figure captions and tables is mapped below.
Bibliographic years, arXiv identifiers, model names (`26B-A4B`, `31B`, `T4`) and
section numbers are not results; the reference table in §7 covers the first two.
"Y" means the value in `paper.md` matches the cited source after rounding to the
precision printed.

## 1. Number map

| # | Paper location | Value as printed | Source | Match |
|---:|---|---|---|---|
| 1 | Abstract | 94,341 issue units | C74; `results/descriptive_tables.json` (sum of 12 `issues`) | Y |
| 2 | Abstract | eleven 3-attempt + one 8-attempt arm | C74; `results/config_metadata.json` | Y |
| 3 | Abstract | ICC 0.646–0.864 | C78 | Y |
| 4 | Abstract | f(k) at most 1.07 pp | C79 | Y |
| 5 | Abstract | oracle − selected 4.82–15.75 pp | C76 | Y |
| 6 | Abstract | agreement 7 of 11, p = 0.549 | C61 | Y |
| 7 | Abstract | own-test AUROC 0.5125 (0.4973–0.5286), p = 0.119 | C64 | Y |
| 8 | Abstract | cross-fit 2/11, 10/11, 11/11 vs 0/11, 0/11, 2/11 | C68 | Y |
| 9 | Abstract | judge 0.5786 (0.5587–0.5987) | C81 | Y |
| 10 | Abstract | judge−exit +0.0209 (+0.0025 to +0.0411) | C82 | Y |
| 11 | Abstract | misorders about 42% | C86 (1−0.5786 = 42.1%) | Y |
| 12 | Introduction | 94,341 units, twelve arms | C74 | Y |
| 13 | Introduction | 4,226 judge pairs | C81 | Y |
| 14 | Setup | 67,074 Nebius trajectories | C1 | Y |
| 15 | Setup | 6,306 Nebius issues | C2 | Y |
| 16 | Setup | 1,823 Nebius repositories | C2 | Y |
| 17 | Setup | 818,660 NVIDIA rows | C11 | Y |
| 18 | Setup | 32 NVIDIA configuration slices | C12 | Y |
| 19 | Setup | 42,545 casefolded NVIDIA issues | C13 | Y |
| 20 | Setup | 3,787 NVIDIA repositories | C13 | Y |
| 21 | Setup | 204 shared issues excluded | C26 | Y |
| 22 | Setup | eleven K=3 + one K=8, 94,341 units | C74 | Y |
| 23 | Setup | K=3 set: one Nebius, four v1.0, four v1.1, two v1.2 | C74; `results/config_metadata.json` | Y |
| 24 | Setup | `resolved=-1` share 9.48% / 4.85% | C17 | Y |
| 25 | Setup | issue truncation 3,072 head + 1,024 tail; patch 4,096 + 1,024 | PREREG-3 §4.3 (methods constant) | Y |
| 26 | Results 4.1 | pass@1 32.29–59.49% | C75 | Y |
| 27 | Results 4.1 | D1 selected 32.20–59.44% | C75 | Y |
| 28 | Results 4.1 | oracle pass@K 41.70–64.30% | C75 | Y |
| 29 | Results 4.1 | gap 4.82–15.75 pp (K=8 11.24 pp) | C76 | Y |
| 30 | Figure 2 caption | 12 arms, 94,341 issue units | C74 | Y |
| 31 | Results 4.1 | f(k) range at most 1.07 pp (0.68 K=8) | C79 | Y |
| 32 | Figure 3 caption / text | 11 K=3 curves end at k=3; K=8 to k=8 | `results/descriptive_tables.json` (`curves`) | Y |
| 33 | Results 4.1 | ICC 0.646–0.864 across twelve arms | C78 | Y |
| 34 | Results 4.1 | K=8 0.798 (0.787–0.811); K=3 0.795 (0.782–0.807) | C78 | Y |
| 35 | Results 4.1 | 14–35% of label variance remains | C86 (1−ICC = 13.6–35.4%) | Y |
| 36 | Results 4.2 | 0 BREAKS / 198 cells | C45 | Y |
| 37 | Results 4.2 | 0/12, 0/12, 2/12 certify | C46 | Y |
| 38 | Results 4.2 | ten arms NO-COVERAGE at every α | C46, C54 (12−2) | Y |
| 39 | Results 4.2 | coverage 7.14% and 5.58% | C47, C48 | Y |
| 40 | Results 4.2 | risk 15.8% (11.7–20.1%) and 16.4% (12.4–20.6%) | C47, C48 | Y |
| 41 | Results 4.2 | `-1`-as-failure risk 24.0% and 27.1% | C57 | Y |
| 42 | Results 4.2 | whole `-1` pipeline 0/11 at every α | C60 | Y |
| 43 | Results 4.2 | files-touched 0/11; patch size and steps 0/11 at 0.20 | C49, C51 | Y |
| 44 | Results 4.2 | cross-fit 2/11, 10/11, 11/11 vs 0/11, 0/11, 2/11; p = 0.00098 | C68 | Y |
| 45 | Results 4.2 | K=8: 3 cross-fit vs 0 agreement | C68 | Y |
| 46 | Results 4.2 | coverage 27.1–63.9%, risk 4.4–15.2% at 0.20 | C69 | Y |
| 47 | Results 4.3 | B1 7+/4−, p = 0.549 | C61 | Y |
| 48 | Results 4.3 | one arm −0.755 pp (−1.207 to −0.319), raw 0.002, Holm 0.022 | C62 | Y |
| 49 | Results 4.3 | B2 0.5125 (0.4973–0.5286), p = 0.119, 4,226 pairs / 754 issues | C64 | Y |
| 50 | Results 4.3 | agreement 0.5058 (0.5018–0.5112), p = 0.0020 | C65 | Y |
| 51 | Results 4.3 | exit reason 0.5764 (0.5578–0.5939) | C65 | Y |
| 52 | Results 4.3 | steps 0.4397 (0.4146–0.4649) | C65 | Y |
| 53 | Results 4.3 | own-test lift +0.892 pp (0.268–1.519), p = 0.005 | C67 | Y |
| 54 | Results 4.3 | E2 null→0 +0.871 (0.203–1.527) | C67 (corrected; see §6) | Y |
| 55 | Results 4.4 | B4 8+/3−, p = 0.227 | C70 | Y |
| 56 | Results 4.4 | −0.075 pp (−0.124 to −0.022), raw 0.009, Holm 0.099 | C70; `results/b4_adaptive_stopping.json` | Y |
| 57 | Results 4.4 | mean attempts 2.886–2.956 of 3 | C70 | Y |
| 58 | Results 4.4 | no detectable effect, CI [−0.124, +0.022] | C70; `results/b4_adaptive_stopping.json` | Y |
| 59 | Results 4.4 | K=8 +0.096 (0.010–0.181), p = 0.039 | C71 | Y |
| 60 | Results 4.4 | B5 3.443/8 (43%), 47.8% vs 48.0%, Δ −0.148 (−0.980 to +0.640), p = 0.740 | C72; C86 for 43% | Y |
| 61 | Table 1 | all values repeat rows 47–60 | C61–C72 | Y |
| 62 | Judge section | 4,226 pairs / 1,128 issues / 641 repositories | C81 | Y |
| 63 | Judge section | first 200 sealed and included | PREREG-3 §5 (protocol) | Y |
| 64 | Judge section | AUROC 0.5786 (0.5587–0.5987), p = 0.0010 | C81 | Y |
| 65 | Judge section | 2.1 points above exit; exit 0.5576 (0.5451–0.5707) | C82; C86 for 2.1 | Y |
| 66 | Judge section | judge−exit +0.0209 (+0.0025 to +0.0411), p = 0.027 | C82 | Y |
| 67 | Judge section | own tests 0.5112 (0.4913–0.5322), 1,381 pairs | C82 | Y |
| 68 | Judge section | agreement 0.5121 (0.5046–0.5188) | C82 | Y |
| 69 | Judge section | judge−own +0.0594 (+0.0197 to +0.1024), p = 0.006 | C82 | Y |
| 70 | Judge section | judge−agreement +0.0665 (+0.0473 to +0.0852), p = 0.001 | C82 | Y |
| 71 | Judge section | misorders about 42% | C86 | Y |
| 72 | Judge section | truncation 0.5772 (0.5493–0.6059), n = 2,221; 0.5800 (0.5554–0.6070), n = 2,005 | C83 | Y |
| 73 | Judge section | no-truncation share 52.6%; pre-registration guessed 74% | C83; PREREG-3 §4.3 | Y |
| 74 | Table 2 | all values repeat rows 64–70 | C81, C82 | Y |
| 75 | Table 3 | issue counts 6,063; 7,463; 5,959; 8,466; 2,490; 8,783; 12,073; 8,520; 5,580; 13,801; 10,563; 4,580 | C75; `results/descriptive_tables.json` | Y |
| 76 | Limitations | `-1` 9.48% / 4.85% | C17 | Y |
| 77 | Limitations | tie-break differs 18.2–20.3% (K=3), 8.4% (K=8); full-budget −1.83 to +1.08 pp | C73 | Y |
| 78 | Limitations | B2 4,226/754, not 11,611/943 | C64; `results/b2_within_issue_auroc.json` (`checks.prereg_availability_table`) | Y |
| 79 | Limitations | PREREG-2 says 9–2 where exact threshold is 10–1 | PREREG-2 §10; DEVIATIONS D9 | Y |
| 80 | Limitations | 1,381 own-test pairs | C82 | Y |
| 81 | Limitations | 10–1 threshold p = 0.0117; B1/B4 7–4 and 8–3 | C61, C70; binomial arithmetic | Y |
| 82 | Limitations | 198 kill-test cells | C45 | Y |
| 83 | Implications | judge 0.579 | C81 | Y |

**Table text.** The Markdown tables reproduce these rows; `notebook_regenerate.py`
rebuilds Table 1 from the B1–B5 JSONs, Table 2 from `judge_analysis.json`, and
Table 3 from `descriptive_tables.json` plus `config_metadata.json`.

## 2. Methods constants

These are protocol values, not outcomes. They are listed separately so that a
reader does not mistake them for results.

| Constant | Value | Source | Match |
|---|---|---|---|
| Confidence level | 95% | PREREG-2 §6 | Y |
| Bootstrap replicates | B = 2,000 | PREREG-2 §6 | Y |
| B2 decision rule | two-sided p < 0.05 and CI excludes 0.5 | PREREG-2 §5 (D8 amends wording) | Y |
| B1/B4 family | Holm over 11 K=3 configs + exact sign test | PREREG-2 §5 | Y |
| Kill-test δ | 0.05 | PREREG §8 | Y |
| Minimum calibration issues | 30 | PREREG §8 | Y |
| α grid | 0.05, 0.10, 0.20 | PREREG §8 | Y |
| Truncation | issue 3,072 head + 1,024 tail; patch 4,096 head + 1,024 tail | PREREG-3 §4.3 | Y |
| Judge N rule | N = 4,226 | D12; `results/judge_n.json` | Y |
| Pre-registration commit | `f9558d9` | git history | Y |

## 3. Word counts

`python scripts/count_paper_words.py` (body excludes YAML metadata, tables,
figure blocks, captions and references; the limit includes abstract, captions
and tables):

| Part | Words |
|---|---:|
| Body prose | 2,278 |
| Abstract | 169 |
| Figure captions | 217 |
| Table text | 289 |
| Body + abstract | 2,447 |
| **With captions and tables** | **2,953** |

Limit 2,990; headroom 37 words. The requested body target was ~2,530, so the
body is 252 words under that target while captions and tables are 56 over their
~450 target. The hard cap is met. References are excluded and are not counted.

## 4. Language-rule checklist

| Rule | Where satisfied |
|---|---|
| Never write "it held" for the kill test; state 0 BREAKS, two arms, `-1` sensitivity, NO-COVERAGE ≠ pass | §4.2: "**0 BREAKS across 198 cells**… 0/12… 2/12… Ten arms are NO-COVERAGE at every α, which is not a pass… Scoring `-1` as failure raises risk to 24.0% and 27.1%… We call neither primary." The phrase "held" appears only in "held-out-repo". |
| B4 K=8 is an interpolation artifact, not a gain | §4.4: "K=8 is +0.096 … but an interpolation artifact: the trigger fires only when the first two patches agree, so `r_ad = f(8)`, and Δ is the corner between f(7) and f(8)." |
| B5 is not a compute saving; at matched cost no detectable difference | §4.4: "At matched cost there is no detectable difference; B5 is not a compute saving." |
| B3 is not blind | §4.2: "This is strong for a signal that is neither free nor blind: the count existed before PREREG-2, and deploying it requires evaluating the other K−1 attempts." |
| Name the policy model for every corpus/config; no claim for "local models" beyond them | §3.1 and Table 3: every arm has a policy; "No agent policy is a local model; only the judge is local." |
| Judge is Q4_0 GGUF via llama.cpp, not NF4 and not the 31B model; say why | §5: "**Gemma 4 26B-A4B, QAT Q4_0, via llama.cpp** … not the pre-registered NF4 estimator and not the 31B model… Standard bitsandbytes NF4 leaves the 3-D expert tensors … unquantised… D14 substituted the official QAT Q4_0 GGUF." |
| Say "no detectable effect, CI [a, b]", not "no effect" | §4.4: "There is no detectable effect, CI [−0.124, +0.022]." B5: "no detectable difference" with Δ and CI. "No effect" does not appear. |
| Report D9 mismatches and tie-break sensitivity (up to 1.83 pp) in Limitations | §6: "The rules choose different representatives in 18.2–20.3% … and full-budget resolve moves by −1.83 to +1.08 pp." |
| Limitations: published labels not recomputed | §6 first paragraph: "Labels are published, not recomputed. Flaky tests and harness errors are inherited." |
| Limitations: NVIDIA sampling rule undocumented | §6: "NVIDIA's sampling rule is undocumented, 1–3 trajectories per issue with no stated rule." |
| Limitations: `-1` convention | §6: "The `-1` labels are not missing at random (9.48% … 4.85%), and the verdict changes between conventions." |
| Limitations: contamination risk for judge | §6: "may have seen public SWE data in pre-training; contamination was not measured." |
| Limitations: pointwise, no chain of thought | §6: "It is pointwise, with no chain of thought." |
| Limitations: truncation | §6: "Prompt truncation affects a substantial minority of patches, though the exploratory split is flat." |
| Limitations: judge and own-test analyses cover one corpus | §6: "Judge and own-test analyses cover one corpus (Nebius K=8); the own-test comparison uses 1,381 pairs…" |
| Effect sizes with CIs; point estimates marked as such | B1–B5 and judge rows carry CIs; §4.1 says "These are descriptive point estimates; no interval is defined for the gap"; §4.1 says f(k) point estimates have no interval. Pass@1/selected/oracle ranges are descriptive ranges, not intervals. |

## 5. Figure and table checks

| Item | Check |
|---|---|
| Fig. 1–6 | All six exist as PDF (vector) and PNG (300 dpi), regenerated by `notebook_regenerate.py` from `results/*.json`; no dataset download or model call. |
| Colour | Okabe–Ito palette; judge blue, exit orange, agreement green, own tests pink, steps grey, cross-fit blue; same signal keeps its colour across figures. |
| Fig. 2 | Dumbbell, 12 arms, gaps labelled; pass@1 open circle, D1 selected diamond, oracle triangle. |
| Fig. 3 | All 12 f(k) curves on one axis; 11 K=3 curves end at 3, K=8 at 8; maximum range printed as 1.07 pp. |
| Fig. 4 | ICC(1) forest, 12 arms, 95% repo-clustered bootstrap intervals, reference line at 0.5. |
| Fig. 5 | Two-panel AUROC forest, chance line at 0.5, n pairs in labels, 95% repo-clustered bootstrap intervals. |
| Fig. 6 | Certification counts at 0.05/0.10/0.20, agreement vs cross-fit, NO-COVERAGE hatched, K=8 note. |
| Tables 1–3 | Rebuilt by `notebook_regenerate.py`; values match §1 and the paper's Markdown tables. |
| Clean-room test | Copied `notebook_regenerate.py`, `scripts/make_figures.py` and `results/*.json` to `/tmp/clean_regen`, ran with no working-directory assumptions; all six PNGs and three tables produced. PNG bytes are identical to the repo copies; PDF bytes differ only in the embedded creation timestamp. |
| Word count | `scripts/count_paper_words.py` exits 0 at 2,953/2,990. |

## 6. Discrepancies and corrections

1. **Prompt vs files: NF4.** The task text says the judge is "26B-A4B (NF4) only." D14 and `RESULTS_3.md` record that bitsandbytes NF4 leaves the 3-D MoE expert tensors unquantised and does not fit on 2×T4; the executed estimator is the official QAT **Q4_0 GGUF** via llama.cpp. The paper discloses this in §5 and does not call the result an NF4 run. **Files win.**
2. **Ledger C67 mislabelled E2.** The ledger said "E2 +0.742pp (p = 0.106)". `results/b2_within_issue_auroc.json` gives E2 null→0 = +0.871pp (0.203–1.527, p = 0.015); +0.742pp is E2 null→0 **minus agreement**. C67 and the RESULTS_2 sentence were corrected; no result number changed.
3. **Removed unsourced paper numbers.** The draft quoted median `p_yes` 0.817 (present only in WEAKNESSES.md) and 26.1% patch truncation (present in RESULTS_3 prose, not in a result JSON). Both were removed from `paper.md`; the truncation split and the claim that truncation affects a substantial minority remain, sourced to C83.
4. **Word target.** Requested body ~2,530; actual body 2,278. Total with abstract, captions and tables is 2,953, under the 2,990 hard cap. The paper chose the hard cap over the body target.
5. **"Tight null" for own tests.** The orientation text calls the own-test result a "tight null"; the CI is 0.4973–0.5286, which includes 0.5 but is not tight. The paper says "do not separate pairs" and "indistinguishable from chance", not "tight null".
6. **JUDGE median/truncation percentages.** The WEAKNESSES/RESULTS_3 prose still contains the removed values; they are descriptive and are not used in the paper. No frozen result was altered.

No numeric discrepancy remains between `paper.md` and the result JSONs after
these corrections.

## 7. References — verification

All entries were checked against the arXiv abstract/API record and, for the two
corpora, the Hugging Face dataset card. No reference is included that was not
opened. No entry is UNVERIFIED.

| Key | Venue / ID | URL | Status |
|---|---|---|---|
| `jimenez2023swebench` | ICLR 2024; arXiv:2310.06770 | https://arxiv.org/abs/2310.06770 | verified |
| `yang2024sweagent` | NeurIPS 2024; arXiv:2405.15793 | https://arxiv.org/abs/2405.15793 | verified |
| `wang2024openhands` | ICLR 2025; arXiv:2407.16741 | https://arxiv.org/abs/2407.16741 | verified |
| `xia2024agentless` | arXiv:2407.01489, 2024 | https://arxiv.org/abs/2407.01489 | verified |
| `pan2024swegym` | ICML 2025; arXiv:2412.21139 | https://arxiv.org/abs/2412.21139 | verified |
| `badertdinov2025swebrebench` | NeurIPS 2025 D&B; arXiv:2505.20411 | https://arxiv.org/abs/2505.20411 | verified |
| `wang2022selfconsistency` | ICLR 2023; arXiv:2203.11171 | https://arxiv.org/abs/2203.11171 | verified |
| `brown2024monkeys` | arXiv:2407.21787, 2024 | https://arxiv.org/abs/2407.21787 | verified |
| `snell2024scaling` | arXiv:2408.03314, 2024 | https://arxiv.org/abs/2408.03314 | verified |
| `geifman2017selective` | arXiv:1705.08500, 2017 | https://arxiv.org/abs/1705.08500 | verified |
| `angelopoulos2021conformal` | arXiv:2107.07511, 2021 | https://arxiv.org/abs/2107.07511 | verified |
| `angelopoulos2021ltt` | arXiv:2110.01052, 2021 | https://arxiv.org/abs/2110.01052 | verified |
| `zheng2023judge` | NeurIPS 2023 D&B; arXiv:2306.05685 | https://arxiv.org/abs/2306.05685 | verified |
| `gemma2026` | Gemma 4 Technical Report; arXiv:2607.02770, 2026 | https://arxiv.org/abs/2607.02770 | verified |
| `ahmad2026openswe` | arXiv:2606.16038, 2026 | https://arxiv.org/abs/2606.16038 | verified |
| `nebius2025trajectories` | HF dataset, 2025 | https://huggingface.co/datasets/nebius/SWE-rebench-openhands-trajectories | verified |
| `nvidia2026traces` | HF dataset, 2026 | https://huggingface.co/datasets/nvidia/Open-SWE-Traces | verified |

**UNVERIFIED:** none.

## 8. Claims not in the ledger

None. Every empirical value maps to C1–C85. C86 records the arithmetic used for
derived percentages (42.1% misorder, 2.1 pp judge−exit, 13.6–35.4% residual
variance, 43% B5 attempt share, ten uncertified arms); these are transformations
of ledger values, not independent estimates. Methods constants are sourced to
the pre-registrations and listed separately in §2.

## 9. Verification performed

- `python scripts/build_paper.py` — exit 0; 9-page PDF, 630,078 bytes.
- `python scripts/count_paper_words.py` — exit 0; 2,953/2,990.
- `.venv/bin/python -m pytest tests -q` — 43 passed.
- `python notebook_regenerate.py` — 6 figures + 3 tables written.
- Clean-room run in `/tmp/clean_regen` — exit 0; PNGs byte-identical to repo.
- Visual inspection of PDF pages 1, 6, 7, 8, 9 and figures 2, 3, 5, 6; no clipped
  axes, doubled captions or missing glyphs.
