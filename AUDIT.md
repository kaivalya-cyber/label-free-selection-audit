# AUDIT — paper.md against the frozen records

Generated 2 November 2026 (revision 5). This file checks the writeup against
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
| 1 | Abstract | 94,341 issue-by-configuration units over 41,073 issues (48,300 before filtering) | C74, C87; `results/descriptive_tables.json`, `results/paper_addenda.json` | Y |
| 2 | Abstract | eleven 3-attempt + one 8-attempt arm | C74; `results/config_metadata.json` | Y |
| 3 | Abstract | ICC 0.646–0.864 | C78 | Y |
| 4 | Abstract | f(k) at most 1.07 pp | C79 | Y |
| 5 | Abstract | oracle − selected 4.82–15.75 pp | C76 | Y |
| 6 | Abstract | agreement nominally above random in 7 of 11, p = 0.549 | C61 | Y |
| 7 | Abstract | own-test AUROC 0.5125 (0.4973–0.5286), p = 0.119 | C64 | Y |
| 8 | Abstract | cross-fit 2/11, 10/11, 11/11 vs 0/11, 0/11, 2/11 | C68 | Y |
| 9 | Abstract | judge 0.5786 (0.5587–0.5987) | C81 | Y |
| 10 | Abstract | judge−exit +0.0209 (+0.0025 to +0.0411) | C82 | Y |
| 11 | Abstract | misorders about 42% | C86 (1−0.5786 = 42.1%) | Y |
| 12 | Introduction | 94,341 units over 41,073 issues from 48,300, twelve arms | C74, C87 | Y |
| 13 | Introduction | 4,226 judge pairs | C81 | Y |
| 14 | Setup | 67,074 Nebius trajectories | C1 | Y |
| 15 | Setup | 6,306 Nebius issues | C2 | Y |
| 16 | Setup | 1,823 Nebius repositories | C2 | Y |
| 17 | Setup | 818,660 NVIDIA rows | C11 | Y |
| 18 | Setup | 32 NVIDIA configuration slices | C12 | Y |
| 19 | Setup | 42,545 casefolded NVIDIA issues | C13 | Y |
| 20 | Setup | 3,787 NVIDIA repositories | C13 | Y |
| 21 | Setup | 204 shared issues excluded | C26 | Y |
| 22 | Setup | eleven K=3 + one K=8; 94,341 units over 41,073 issues | C74, C87 | Y |
| 23 | Setup | K=3 set: one Nebius, four v1.0, four v1.1, two v1.2 | C74; `results/config_metadata.json` | Y |
| 24 | Setup | six of eleven K=3 arms use 27B language models (28B total with vision) | C89, C92; `results/paper_addenda.json` (`arms_27b`) | Y |
| 25 | Setup | pools: Nebius 6,102; NVIDIA 42,198; 32 NVIDIA configurations, 10 frozen and 22 non-frozen; 42,402 − 204 shared = 42,198, and 42,198 + 143 non-frozen-only = 42,341; K=3 frames 6,063 and 35,010 after filtering 39 and 7,188 | C87; `results/paper_addenda.json` (`distinct_issues`) | Y |
| 25a | Setup | K=8 reuses 4,580 Nebius K=3 issues, adds 0 distinct | C87 (`nebius_k8_reuse`) | Y |
| 26 | Setup | `resolved=-1` share 9.48% / 4.85% | C17 | Y |
| 27 | Setup | issue truncation 3,072 head + 1,024 tail; patch 4,096 + 1,024 | PREREG-3 §4.3 (methods constant) | Y |
| 28 | Results 4.1 | pass@1 32.29–59.49% | C75 | Y |
| 29 | Results 4.1 | plurality-cluster selected 32.20–59.44% | C75 | Y |
| 30 | Results 4.1 | oracle pass@K 41.70–64.30% | C75 | Y |
| 31 | Results 4.1 | gap 4.82–15.75 pp (K=8 11.24 pp) | C76 | Y |
| 32 | Figure 2 caption | 12 arms, 94,341 units over 41,073 issues | C74, C87; `descriptive_tables.json`, `paper_addenda.json` | Y |
| 33 | Results 4.1 | f(k) range at most 1.07 pp (0.68 K=8) | C79 | Y |
| 34 | Figure 3 caption / text | 11 K=3 curves end at k=3; K=8 to k=8 | `results/descriptive_tables.json` (`curves`) | Y |
| 35 | Results 4.1 | ICC 0.646–0.864 across twelve arms | C78 | Y |
| 36 | Results 4.1 | K=8 0.798 (0.787–0.811); K=3 0.795 (0.782–0.807) | C78 | Y |
| 37 | Results 4.1 | 14–35% of label variance remains | C86 (1−ICC = 13.6–35.4%) | Y |
| 38 | Results 4.2 | 0 BREAKS / 189 distinct cells | C45, C91 | Y |
| 39 | Results 4.2 | 99 cells per convention = 90 K=3 + 9 K=8; 90×2 + 9 = 189 (K=8 identical across conventions) | C45, C91; `results/kill_test.json` | Y |
| 40 | Results 4.2 | 0/12, 0/12, 2/12 certify | C46 | Y |
| 41 | Results 4.2 | ten arms NO-COVERAGE at every α | C46, C54 (12−2) | Y |
| 42 | Results 4.2 | coverage 7.14% and 5.58% | C47, C48 | Y |
| 43 | Results 4.2 | risk 15.8% (11.7–20.1%) and 16.4% (12.4–20.6%) | C47, C48 | Y |
| 44 | Results 4.2 | `-1`-as-failure risk 24.0% and 27.1% | C57 | Y |
| 45 | Results 4.2 | whole `-1` pipeline 0/12 arms at every α | C60 | Y |
| 46 | Results 4.2 | files-touched 0/11 K=3; patch size and steps 0/11 at 0.20 | C49, C51 | Y |
| 47 | Results 4.2 | cross-fit 2/11, 10/11, 11/11 vs 0/11, 0/11, 2/11; p <= 0.001 | C68 | Y |
| 48 | Results 4.2 | K=8: 3 cross-fit vs 0 agreement | C68 | Y |
| 49 | Results 4.2 | coverage 27.1–63.9%, risk 4.4–15.2% at 0.20 | C69 | Y |
| 50 | Results 4.3 | B1 7+/4−, p = 0.549 | C61 | Y |
| 51 | Results 4.3 | one arm −0.755 pp [−1.207, −0.319], Holm 0.022 | C62 | Y |
| 52 | Results 4.3 | B2 Nebius K=8 0.5125 (0.4973–0.5286), p = 0.119, 4,226 pairs / 754 issues | C64 | Y |
| 53 | Results 4.3 | agreement 0.5058 (0.5018–0.5112), p = 0.0020 | C65 | Y |
| 54 | Results 4.3 | exit reason 0.5764 (0.5578–0.5939) | C65 | Y |
| 55 | Results 4.3 | steps raw 0.4397 (0.4146–0.4649); resolved attempts use fewer messages | C65, C88 | Y |
| 56 | Results 4.3 | steps oriented 0.5603 (0.5351–0.5854), abs(AUROC−0.5) = 0.060 | C88 (`steps_b2`) | Y |
| 57 | Results 4.3 | own-test lift +0.892 pp (0.268–1.519), p = 0.005 | C67 | Y |
| 58 | Results 4.3 | E2 null→0 +0.871 (0.203–1.527) | C67 (corrected; see §6) | Y |
| 59 | Results 4.3 | E1 own-test AUROCs 0.5063 (both submit), 0.5066 (both max) | C66; `results/b2_within_issue_auroc.json` (`exploratory.e1_stratified`) | Y |
| 59a | Results 4.3 | E1 lift all-submit +0.67 pp (0.03–1.32, p = 0.044), 3,299 issues | C90; `results/paper_addenda.json` (`e1_selection_lift.by_exit_composition.all_submit`) | Y |
| 59b | Results 4.3 | E1 lift mixed-exit +1.39 pp (−0.07–2.93), 1,239 issues; all-max +3.27 pp (−5.21–11.61), 42 issues | C90; `results/paper_addenda.json` (`e1_selection_lift.by_exit_composition`) | Y |
| 59c | Results 4.3 | full-availability lift −0.22 pp (−4.04 to +3.76, p = 0.977), 226 issues / 150 repos; MDE ≈ 5.6 pp | C93; `results/paper_addenda.json` (`e1_selection_lift.fully_available`, `power`) | Y |
| 60 | Results 4.4 | B4 8+/3−, p = 0.227 | C70 | Y |
| 61 | Results 4.4 | −0.075 pp [−0.124, −0.022], raw 0.009, Holm 0.099 | C70; `results/b4_adaptive_stopping.json` | Y |
| 62 | Results 4.4 | mean attempts 2.886–2.956 of 3 | C70 | Y |
| 63 | Results 4.4 | no detectable family effect (p = 0.227) | C70 | Y |
| 64 | Results 4.4 | K=8 +0.096 (0.010–0.181), p = 0.039, interpolation artifact | C71 | Y |
| 65 | Results 4.4 | B5 3.443/8 (43%), 47.8% vs 48.0%, Δ −0.148 (−0.980 to +0.640), p = 0.740 | C72; C86 for 43% | Y |
| 66 | Table 1 | all values repeat rows 50–65 | C61–C72 | Y |
| 67 | Judge section | 4,226 pairs / 1,128 issues / 641 repositories | C81 | Y |
| 68 | Judge section | first 200 sealed and included | PREREG-3 §5 (protocol) | Y |
| 69 | Judge section | AUROC 0.5786 (0.5587–0.5987), p <= 0.001 | C81 | Y |
| 70 | Judge section | 2.1 points above exit; exit 0.5576 (0.5451–0.5707) | C82; C86 for 2.1 | Y |
| 71 | Judge section | judge−exit +0.0209 (+0.0025 to +0.0411), p = 0.027 | C82 | Y |
| 72 | Judge section | own tests, agreement, oriented steps lower; Table 2 | C82, C88 | Y |
| 73 | Judge section | judge−own +0.0594 (+0.0197 to +0.1024), p = 0.006 | C82 | Y |
| 74 | Judge section | judge−agreement +0.0665 (+0.0473 to +0.0852), p <= 0.001 | C82 | Y |
| 75 | Judge section | misorders about 42% | C86 | Y |
| 76 | Judge section | truncation 0.5772 (0.5493–0.6059), n = 2,221; 0.5800 (0.5554–0.6070), n = 2,005 | C83 | Y |
| 77 | Judge section | no-truncation share 52.6%; pre-registration guessed 74% | C83; PREREG-3 §4.3 | Y |
| 78 | Table 2 | five rows: judge, exit, own tests, agreement, steps oriented post-hoc; judge-frame steps 0.5477 (0.5254–0.5687) | C81, C82, C88 | Y |
| 79 | Table 3 | issue counts 6,063; 7,463; 5,959; 8,466; 2,490; 8,783; 12,073; 8,520; 5,580; 13,801; 10,563; 4,580 | C75; `results/descriptive_tables.json` | Y |
| 80 | Table 3 caption | six of eleven K=3 arms use 27B language-model policies; no local-execution claim | C89, C92 | Y |
| 81 | Limitations | `-1` 9.48% / 4.85% | C17 | Y |
| 82 | Limitations | tie-break differs 18.2–20.3% (K=3), 8.4% (K=8); full-budget −1.83 to +1.08 pp | C73 | Y |
| 83 | Limitations | B2 4,226/754, not 11,611/943 | C64; `results/b2_within_issue_auroc.json` (`checks.prereg_availability_table`) | Y |
| 84 | Limitations | PREREG-2 says 9–2 where exact threshold is 10–1 | PREREG-2 §10; DEVIATIONS D9.3 | Y |
| 85 | Limitations | 1,381 own-test pairs | C82 | Y |
| 86 | Limitations | 10–1 threshold p = 0.0117; B1/B4 7–4 and 8–3 | C61, C70; binomial arithmetic | Y |
| 87 | Limitations | 189 distinct kill-test cells | C45, C91 | Y |
| 88 | Implications | judge 0.579 | C81 | Y |
| 89 | Results 4.3 | B2 443 repositories | C64 (`n_clusters`) | Y |
| 90 | Results 4.3 | own-test lift is report-only; the full-availability interval cannot exclude the pooled +0.892 pp; AUROC is pairwise | C64, C67, C93; `results/b2_within_issue_auroc.json`, `results/paper_addenda.json` | Y |
| 91 | Judge section | 1,381 B2-eligible judge pairs; N matches B2 by pre-registration choice, not sample identity | C82; PREREG-3 §4.2 | Y |

**Table text.** The Markdown tables reproduce these rows; `notebook_regenerate.py`
rebuilds Table 1 from the B1–B5 JSONs, Table 2 from `judge_analysis.json`, and
Table 3 from `descriptive_tables.json` plus `config_metadata.json`.

## 1a. Signal scope

Neither corpus records a repository-test result per attempt. Nebius trajectory
rows carry `resolved`, `exit_status`, `gen_tests_correct` and
`pred_passes_gen_tests`; NVIDIA rows carry `resolved` and a metadata object
(`category`, `teacher_model`, `reference_patch`, `model_patch`). There is no
field for the repository's held-out suite in either corpus, so no analysis here
can select by running it. `paper.md` states this in Limitations ("Signal
scope").

## 2. Methods constants

These are protocol values, not outcomes. They are listed separately so that a
reader does not mistake them for results.

| Constant | Value | Source | Match |
|---|---|---|---|
| Confidence level | 95% | PREREG-2 §6 | Y |
| Bootstrap replicates | B = 2,000 | PREREG-2 §6 | Y |
| B2 decision rule | two-sided p < 0.05 and CI excludes 0.5 | PREREG-2 §5 (reduced-draw amendment) | Y |
| B1/B4 family | Holm over 11 K=3 configs + exact sign test | PREREG-2 §5 | Y |
| Kill-test δ | 0.05 | PREREG §8 | Y |
| Minimum calibration issues | 30 | PREREG §8 | Y |
| α grid | 0.05, 0.10, 0.20 | PREREG §8 | Y |
| Truncation | issue 3,072 head + 1,024 tail; patch 4,096 head + 1,024 tail | PREREG-3 §4.3 | Y |
| Judge N rule | N = 4,226 | D12; `results/judge_n.json` | Y |
| Minimum detectable effect | (z0.975 + z0.80) × SE, SE = percentile-CI half-width / z0.975; 80% power, two-sided α = 0.05 | D19; `results/paper_addenda.json` (`e1_selection_lift.fully_available.power`) | Y |
| Pre-registration commit | `f9558d9` | git history | Y |
| Steps orientation | raw count; post-hoc negation for oriented AUROC | D16; `results/paper_addenda.json` | Y |
| Distinct issues | 48,300 pools after excluding 204 shared issues; NVIDIA 42,545 − 204 − 143 = 42,198; 41,073 enter a K=3 frame | C87; `results/paper_addenda.json` | Y |

## 3. Word counts

`python scripts/count_paper_words.py` reports the three requested rules. Body
prose includes headings but excludes the YAML title block, abstract, captions,
tables and references. Rule 3 is the binding limit.

| Rule | Words |
|---|---:|
| 1. Body only (headings included) | 2,276 |
| 2. Body + figure captions + table text | 2,685 |
| 3. Everything except references (title block, abstract, body, captions, tables) | **2,896** |

Components: title block 23; abstract 188; body 2,276; figure captions 157;
table text 252. Official limit 3,000 under rule 3; working target 2,900, so the
headroom is 4 words under the target and 104 under the official limit. This
revision adds the signal-scope paragraph, the selected-rate rule, the judge-frame
arm and the MDE wording, paid for by trimming Related work and Implications
(D20). References are excluded from all three counts.

## 4. Language-rule checklist

| Rule | Where satisfied |
|---|---|
| Never write "it held" for the kill test; state 0 BREAKS, two arms, `-1` sensitivity, NO-COVERAGE ≠ pass | §4.2: "**0 BREAKS across 189 distinct cells**… 0/12… 2/12… Ten arms are NO-COVERAGE at every α… Scoring `−1` as failure raises risk to 24.0% and 27.1%… We call neither primary." The phrase "held" appears only in "held-out-repo". |
| B4 K=8 is an interpolation artifact, not a gain | §4.4: "K=8 is +0.096 … but an interpolation artifact: the trigger fires only when the first two patches agree, so `r_ad = f(8)`, and Δ is the corner between f(7) and f(8)." |
| B5 is not a compute saving; at matched cost no detectable difference | §4.4: "At matched cost there is no detectable difference; B5 is not a compute saving." |
| B3 is not blind, and Table 1 says so | §4.2: "It is neither free nor blind: deploying it requires evaluating the other K−1 attempts." §4.4: "its headline existed before PREREG-2." Table 1: "SIGNIFICANT+ (not blind)". |
| Name the policy model for every corpus/config; no claim for "local models" beyond them | §3.1 and Table 3: every arm has a policy; "Six of eleven K=3 arms use 27B language models (four Qwen3.6, two Qwen3.8; 28B total with vision)… we do not claim local execution." |
| Judge is Q4_0 GGUF via llama.cpp, not NF4 and not the 31B model; say why | §5: "**Gemma 4 26B-A4B, QAT Q4_0, via llama.cpp** … neither the pre-registered NF4 estimator nor the 31B model… NF4 leaves this mixture-of-experts model's 3-D expert tensors unquantised; they do not fit on two cards, so NF4 fails before scoring. A documented post-freeze deviation substituted the official QAT Q4_0 GGUF (DEVIATIONS.md)…" |
| Say "no detectable effect, CI [a, b]", not "no effect" | §4.4: "No detectable family effect." B5: "no detectable difference" with Δ and CI. "No effect" does not appear. |
| Report the tie-break mismatch (D9.2) and its sensitivity (up to 1.83 pp) in Limitations | §6: "The rules choose different representatives in 18.2–20.3% … and full-budget resolve moves by −1.83 to +1.08 pp." |
| Limitations: published labels not recomputed | §6 first paragraph: "Labels are published, not recomputed. Flaky tests and harness errors are inherited." |
| Limitations: NVIDIA sampling rule undocumented | §6: "NVIDIA's 1–3 trajectories per issue have no stated sampling rule, so sample counts may correlate with difficulty." |
| Limitations: `-1` convention | §6: "The `-1` labels are not missing at random (9.48% … 4.85%), and the verdict changes between conventions." |
| Limitations: contamination risk for judge | §6: "may have seen public SWE data in pre-training; contamination was not measured." |
| Limitations: pointwise, no chain of thought | §6: "It is pointwise, no chain of thought." |
| Limitations: truncation | §6: "Truncation affects a substantial minority, though the exploratory split is flat." |
| Limitations: judge and own-test analyses cover one corpus | §6: "Judge and own-test analyses cover one corpus (Nebius K=8); the own-test comparison uses 1,381 pairs." |
| Agreement described as "tiny but detectable" | §4.3: "Agreement is 0.5058 (0.5018–0.5112, p = 0.0020), tiny but detectable"; the surrounding sentence keeps it secondary to B1's family result. |
| E1 stratified lifts labelled exploratory and uncorrected; full-availability test reported as a power limit | §4.3: "E1's stratified lifts are exploratory and uncorrected across strata"; then "When every attempt has a test result (226 issues), the lift is −0.22 pp (95% CI −4.04 to +3.76, p = 0.977); that interval cannot exclude the pooled +0.892 pp, and the minimum detectable effect here is about 5.6 pp at 80% power, so the availability question is open." §7 and Limitations repeat the value and the MDE; C93. |
| Full-availability result is a power statement, not a survival test | §4.3, §7 and Limitations print −0.22 pp (−4.04 to +3.76) and the MDE (~5.6 pp at 80% power) and say the question is open. "Does not survive" and "no detectable lift" do not appear. |
| B3 states which representative rule `rate_loo` and the kill test use; no "undocumented" claim | §3.2: "When several clusters tie for largest, B1 chooses one by a seeded random draw over the tied clusters (as frozen in PREREG-2) and then takes that cluster's smallest `trajectory_id`; B4 breaks ties by the smallest `trajectory_id`; the kill test/`rate_loo` take the lexicographically smallest canonical cluster." §4.4: "uses the kill test's canonical-string tie-break (DEVIATIONS.md)". Limitations reports 18.2–20.3% / 8.4% disagreement and −1.83 to +1.08 pp.
| E1 own-test AUROC pairs described by availability | §4.3: "E1's own-test AUROCs, on pairs where both attempts have non-null own-test results, are 0.5063 (both submitted) and 0.5066 (both max-iteration)". |
| Judge−exit described as suggestive/secondary and uncorrected | §5: "The paired judge-minus-exit difference is +0.0209 … uncorrected and secondary: suggestive, not a corrected family result." |
| Effect sizes with CIs; point estimates marked as such | B1–B5 and judge rows carry CIs; §4.1 says "Point estimates only", and the f(k) caption says "point estimates". Pass@1/selected/oracle ranges are descriptive ranges, not intervals. |
| Steps orientation matches code; oriented value post-hoc | §3.2: "Steps is the assistant-message count; the pre-registered score is raw, and resolved attempts tend to use fewer messages (raw AUROC 0.4397; oriented 0.5603, post-hoc)." §4.3: "steps 0.4397 … meaning resolved attempts use fewer messages… The post-hoc oriented score is 0.5603 (0.5351–0.5854), a weak signal." Table 2: "Steps (oriented, post-hoc)" 0.5477 (0.5254–0.5687). |
| "Weak (0.51–0.58)", not "near chance" | Abstract: "cheap signals remain weak (AUROC 0.51–0.58)"; §7: "cheap signals are weak (AUROC 0.51–0.58)"; Fig. 5 title: "Cheap signals are weak (AUROC 0.51–0.58)". "Near chance" does not appear. |
| B1–B5 defined before use | Introduction: "four pre-registered tests (B1 agreement lift, B2 own-test ranking, B3 cross-fit certification, B4 repeated-patch stopping) and one exploratory test (B5 own-test stopping)". |
| Descriptive names, not D1/D8/D9/D14/PREREG, in the body | The body describes rules and studies in words: §3.2 uses "plurality-cluster submission"; §4.4 uses the kill test's "canonical-string tie-break (DEVIATIONS.md)"; §5 uses "documented post-freeze deviation". D9.1–D9.3 and PREREG-2 do appear, as pointers to the audit trail: §3.3 names each sub-item once so that one identifier means one item, and §4.4 says B3's headline "existed before PREREG-2". No D-identifier is used as a substitute for describing a rule. |
| NO-COVERAGE defined at first use | §4.2: "Ten arms are NO-COVERAGE at every α (no threshold met the risk target), not a pass." |
| 0/11 vs 0/12 denominators consistent | §4.2: 0/12 arms overall and 0/12 under `-1`; secondary files-touched and patch-size baselines are explicitly "0/11 K=3 configurations". |
| Use "p <= 0.001" at the bootstrap floor | §4.2, §5, Table 1 (B3) and Table 2 (judge, exit, steps) print `p <= 0.001`; no `p = 0.00098` or `p = 0.0010` remains. |
| Distinct issues alongside units | Abstract, Introduction and §3.1 print 41,073 analysed issues beside 94,341 units and 48,300 before filtering; §3.1 defines pools, explains 42,545 − 204 − 143 = 42,198, the 39 and 7,188 filtering gaps, and K=8 reuse. |
| Fig. 1 arrows visible and boxes not clipped | `scripts/make_figures.py::fig_design` uses explicit arrow shafts with `shrinkA/B=0`, 0.032 axes-unit gaps between boxes, and margins inside the axes; PDF page 2 inspected. |
| Nebius URL resolves and has no trailing punctuation | `paper.md` reference 16 uses `<https://huggingface.co/datasets/nebius/SWE-rebench-openhands-trajectories>`; HTTP 200 checked; `references.bib` uses the same canonical URL. |

## 5. Figure and table checks

| Item | Check |
|---|---|
| Fig. 1–6 | All six exist as PDF (vector) and PNG (300 dpi), regenerated by `notebook_regenerate.py` from `results/*.json`; no dataset download or model call. |
| Colour | Okabe–Ito palette; judge blue, exit orange, agreement green, own tests pink, steps grey, cross-fit blue; same signal keeps its colour across figures. |
| Fig. 1 | Five-stage schematic; arrow shafts visible, boxes within the canvas, body text not clipped; PDF page 2 inspected. |
| Fig. 2 | Dumbbell, 12 arms, gaps labelled; pass@1 open circle, plurality-cluster selected diamond, oracle triangle. |
| Fig. 3 | All 12 f(k) curves on one axis; 11 K=3 curves end at 3, K=8 at 8; maximum range printed as 1.07 pp. |
| Fig. 4 | ICC(1) forest, 12 arms, 95% repo-clustered bootstrap intervals. |
| Fig. 5 | Two-panel AUROC forest, chance line at 0.5, n pairs in labels, 95% repo-clustered bootstrap intervals; oriented steps in both panels (0.548 judge frame, 0.560 B2 frame); title says weak (0.51–0.58). |
| Fig. 6 | Certification counts at 0.05/0.10/0.20, agreement vs cross-fit, NO-COVERAGE hatched, K=8 note. |
| Tables 1–3 | Rebuilt by `notebook_regenerate.py`; values match §1 and the paper's Markdown tables. Table 1 has B1's one Holm-significant negative arm and B3 "(not blind)"; Table 2 has the post-hoc oriented-steps row; Table 3 caption has the 27B-arm disclosure. |
| Clean-room test | `/tmp/clean_rev9` copied only `notebook_regenerate.py`, `scripts/make_figures.py` and `results/*.json`; regenerated six PNGs and four table files byte-identically. The PDFs regenerate but differ in metadata, as expected. |
| Word count | `scripts/count_paper_words.py` exits 0 at **2,896/2,900** under the strictest rule (official limit 3,000). |

## 6. Discrepancies and corrections

1. **Prompt vs files: NF4.** The task text says the judge is "26B-A4B (NF4) only." D14 and `RESULTS_3.md` record that bitsandbytes NF4 leaves the 3-D MoE expert tensors unquantised and does not fit on 2×T4; the executed estimator is the official QAT **Q4_0 GGUF** via llama.cpp. The paper discloses this in §5 and does not call the result an NF4 run. **Files win.**
2. **Ledger C67 mislabelled E2.** The ledger said "E2 +0.742pp (p = 0.106)". `results/b2_within_issue_auroc.json` gives E2 null→0 = +0.871pp (0.203–1.527, p = 0.015); +0.742pp is E2 null→0 **minus agreement**. C67 and the RESULTS_2 sentence were corrected; no result number changed.
3. **Removed unsourced paper numbers.** The draft quoted median `p_yes` 0.817 (present only in WEAKNESSES.md) and 26.1% patch truncation (present in RESULTS_3 prose, not in a result JSON). Both were removed from `paper.md`; the truncation split and the claim that truncation affects a substantial minority remain, sourced to C83.
4. **Word target.** The official limit is 3,000 words under rule 3; the working target is 2,900. The three reported counts are **2,276 body-only, 2,685 body+captions+tables and 2,896 everything except references** — 4 under the target and 104 under the official limit. Revision 4 added the power caveat and removed two duplicated sentences; revision 5 added the signal scope, the selected-rate rule and the MDE comparison, paid for from Related work and Implications. The earlier self-imposed 2,850 limit is retired (D19, D20).
5. **"Tight null" for own tests.** The orientation text calls the own-test result a "tight null"; the CI is 0.4973–0.5286, which includes 0.5 but is not tight. The paper prints the estimate, CI and NOT SIGNIFICANT verdict and does not use "tight null".
6. **JUDGE median/truncation percentages.** The WEAKNESSES/RESULTS_3 prose still contains the removed values; they are descriptive and are not used in the paper. No frozen result was altered.
7. **B4 wording corrected during audit.** The first draft attached the negative arm's interval [−0.124, −0.022] to a family-level "no detectable effect". That interval excludes zero (raw p = 0.009), so the sentence was wrong; it now reports the arm's raw p and Holm failure separately from the family sign test (p = 0.227). No number changed.
8. **Cell-count doubled K=8.** D15 and the first audit counted 198 because they multiplied the nine K=8 cells by two conventions, but those cells are identical across conventions. The correct accounting is 99 per convention and **189 distinct** computations (90×2 + 9). `KILL_TEST.md`, C45, the paper and this audit now say 189; 0 BREAKS and every cell verdict are unchanged. Logged as D17.
9. **Own-test estimands and availability reconciled.** The 0.5125 AUROC is pairwise on mixed-label issues with non-null tests on both attempts (4,226 pairs / 754 issues / 443 repos). The +0.892 pp lift is a per-issue submit-one rule with null = −1 over all 4,580 issues. E1 stratification gives +0.67 pp (0.03–1.32) on all-submit issues, +1.39 (−0.07–2.93) on mixed-exit issues, and +3.27 (−5.21–11.61) on 42 all-max issues. Restricting to the 226 issues where all eight attempts have a test result, the lift is −0.0022 on the fraction scale, i.e. **−0.22 pp** (95% CI −4.04 to +3.76, p = 0.977). The minimum detectable effect at this sample is about 5.6 pp at 80% power, roughly six times the pooled +0.892 pp, so this subset cannot test whether the pooled lift reflects test availability. Logged as D17/D18; the earlier −0.022 pp was a prose conversion error (D19).
10. **Steps orientation text did not match the code.** The earlier §3.2 said steps was "oriented so fewer is positive", but `scripts/b2_within_issue_auroc.py` stores the raw assistant-message count. The printed raw 0.4397 is **below** 0.5 and therefore means resolved attempts take **fewer** steps; the oriented score is 0.5603 (0.5351–0.5854), and the judge-pair oriented value is 0.5477 (0.5254–0.5687). D16 records both. No frozen number changed; the new values are EXPLORATORY.
11. **Distinct-issue count was mixing pools with analysed frames.** A raw union of the signal frames gives 48,504 keys; excluding 204 shared issues leaves **48,300 pool issues** (Nebius 6,102; NVIDIA 42,198; disjoint). Only **41,073** clear the three-attempt floor and enter a K=3 frame: Nebius 6,063 (39 filtered) and NVIDIA 35,010 (7,188 filtered). The 94,341 units are over 41,073, not 48,300. The abstract, introduction, Setup, Figure 2 caption and C87 now separate the two counts. No unit, arm or result changed.
12. **Prompt derivation does not reproduce 48,300.** The review asked for 48,300 from the Nebius K=3 frame (6,063) plus NVIDIA frame issues. The actual K=3 frame union is 41,073, and 6,063 + 42,198 = 48,261, not 48,300. The exact decomposition is 6,102 Nebius pool + 42,198 NVIDIA pool = 48,300, with 39 and 7,188 issues filtered before sampling. Files win; the paper uses the two-level count.
13. **Model names and sizes.** The NVIDIA dataset card names Qwen3.6-27B (v1.1) and Qwen3.8-27B (v1.2). Both Qwen cards state “Number of Parameters: 27B” for the **language model** and display **28B parameters in total** (the vision encoder included). The paper now says “27B language models … 28B total with vision.” Checked 2026-11-01. Sources: <https://huggingface.co/datasets/nvidia/Open-SWE-Traces>, <https://huggingface.co/Qwen/Qwen3.6-27B>, <https://huggingface.co/Qwen/Qwen3.8-27B>.
14. **Figure 1 clipping.** The first render had the outer Data and Decomposition borders at the axes edge and arrows touching box borders. The boxes now have 0.032 axes-unit gaps and sit inside the axes; PDF page 2 and `figures/fig1_design.png` were re-inspected.
15. **Nebius URL.** The BibTeX field has no embedded whitespace; LaTeX was breaking the URL at a hyphen and a slash, so the PDF read `openhands- trajectories`. The bibliography now uses an unbreakable URL (`\mbox`), `\small`, and ragged-right setting; text extraction shows the complete URL as one token and there are no overfull boxes. The field content is unchanged.
16. **0/11 vs 0/12.** The earlier label-sensitivity sentence said 0/11 even though the K=8 arm also certifies 0/3 under `-1`; the whole-pipeline figure is **0/12**. The paper now prints 0/12 there and reserves 0/11 for the K=3-only secondary baselines. C60 was updated accordingly; no cell or verdict changed.
17. **Reference punctuation.** The NVIDIA manual URL had a trailing period; it is now angle-bracketed. The Nebius URL itself resolves (HTTP 200) and uses the canonical lower-case dataset path. No citation content changed.
18. **Item 6 replacement text was not present.** The request said "[use the replacements I sent]" but contained no replacement prose. I applied minimal wording consistent with the five stated claims: "nominally above" for 7/11, a non-absolute abstract ending, "does not replace execution" for the judge, and sibling labels as a diagnostic rather than a free selector. If exact wording was intended, it is not in this workspace.
19. **p-value formatting.** `p = 0.00098`/`p = 0.0010` at the bootstrap floor are now printed as `p <= 0.001`; the exact values remain in the JSONs and ledger C68/C81.
20. **Full-availability test added.** The review asked whether the own-test lift survives when every attempt has a test result. `scripts/paper_addenda.py` computes it on 226 issues / 150 repos: **−0.0022** (95% CI −0.0404 to +0.0376, p = 0.977), i.e. **−0.22 pp (−4.04 to +3.76 pp)**, versus +0.0089 (+0.892 pp) pooled; MDE ≈ 5.6 pp at 80% power. It is EXPLORATORY (D17/D18), added to C93 and to §4.3, §7 and Limitations; no frozen B2 or B1 quantity changed.
21. **NVIDIA's 143-issue gap.** The dataset has **32 configurations**, of which **10** are the frozen K=3 arms, so **22** are non-frozen. The casefolded total is 42,545; 42,402 occur in the frozen ten; 204 are shared with Nebius, leaving 42,198. The other **143** occur only in the 22 non-frozen configurations: every one of the 143 appears in those 22 and in none of the frozen ten. Thus 42,545 − 204 = 42,341 and 42,341 − 143 = 42,198. The paper, C87 and `results/paper_addenda.json` record the filter; `scripts/paper_addenda.py` asserts 32, 10, 22 and the 143 from `out/nvidia_paths.parquet`.
22. **Author and B1–B5 definitions.** "Anonymous submission" was removed and the author is now named. The earlier claim that "this track does not require blind review" is removed: no rule text for the track exists in this workspace, so it cannot be quoted, and an unsourced rule claim does not belong in the audit. B1–B5 are defined at first use in the Introduction as four pre-registered tests plus one exploratory test; §3.3 gives the test families and the D9.1 reduced-draw sentence.
23. **Kaggle editor count not confirmed.** There is no authenticated Kaggle writeup draft in this workspace and creating one would be an external write. The local counter is **2,898** under the strictest rule against the official 3,000-word limit (2,900 working target); the editor count should be checked when the text is pasted.
24. **Exact replacement paragraphs were not present.** The review said to apply the abstract, §5 and §7 replacements "exactly as given" but supplied no replacement text in this message. I kept the approved sentences already in `paper.md` and changed only the new full-availability clause in §7. If exact wording was intended, it is absent from the workspace.

25. **Full-availability scale was wrong in prose (revision 4).** The JSON value is −0.0022124 on the
    fraction scale, which is −0.22 pp, not the −0.022 pp printed earlier; the conversion multiplied
    by 10 instead of 100. Every location now prints −0.22 pp (−4.04 to +3.76). The same revision
    replaces "does not survive" with a power statement (MDE 5.57 pp at 80% power), splits D9 into
    D9.1/D9.2/D9.3, corrects NVIDIA's non-frozen count from 21 to 22, retires the unsourced
    blind-review claim, and moves the word limit to the official 3,000 with a 2,900 target. No frozen
    quantity changed; `results/paper_addenda.json` is regenerated with a `power` block and
    `results/descriptive_tables.json` changed only in its D9.2 source string. Logged as D19.

26. **Signal scope (revision 5).** Neither corpus records a repository-test result per attempt; see §1a. Limitations now states that own tests are agent-written (`pred_passes_gen_tests`), not the held-out suite, and that the conclusions do not cover selecting by running it. The abstract and Implications say "with the signals these trajectories contain". No number changed.
27. **"Frozen quantity" claim withdrawn (revision 5).** No post-freeze amendment changed a reported frozen result, but D9.2 means the kill test and B3 used a tie-break other than the frozen text (smallest `trajectory_id`); full-budget resolve moves by −1.83 to +1.08 pp between the rules. §3.3, DEVIATIONS and this audit now say that. Logged as D20.
28. **Selected-rate rule, judge frame, terminology (revision 5).** §4.1 and the Figure 2 caption state that the 32.20–59.44% selected rates use the largest canonical cluster with ties by the smallest `trajectory_id` (`d1_pick`, the documented D1/B4 rule), not B1's seeded draw. Table 2 opens "Judge frame:"; §5 names Nebius K=8 and separates the 12,917-pair pool over 1,160 issues from the 4,226-pair sample over 1,128, whose arm is recorded in `scripts/judge_build_pairs.py` and PREREG-3 §2, not in `judge_analysis.json`. "audit pre-registration" is now PREREG-2, and Limitations says B5 was registered after the kill test. No number changed.

No numeric discrepancy remains between `paper.md` and the result JSONs after
these corrections. The only irreconcilable arithmetic is the review prompt's
proposed 48,300 derivation, documented as item 12.

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

**Model cards consulted (2026-11-01).** `nvidia/Open-SWE-Traces` names Qwen3.6-27B
(v1.1) and Qwen3.8-27B (v1.2). Both Qwen cards give 27B for the language model
and 28B total with the vision encoder.
<https://huggingface.co/datasets/nvidia/Open-SWE-Traces>,
<https://huggingface.co/Qwen/Qwen3.6-27B>,
<https://huggingface.co/Qwen/Qwen3.8-27B>.

## 8. Claims not in the ledger

None. Every empirical value maps to C1–C93. C87 records the two-level issue
count, the 143-issue NVIDIA filter and K=8 reuse; C88 the post-hoc steps
orientation; C89/C92 the six 27B language-model arms and their 28B total;
C90 the stratified E1 lift; C91 the 189 distinct cells; C92 the model-card
sizes; C93 the full-availability lift. C86 records derived arithmetic (42.1%
misorder, 2.1 pp judge−exit, 13.6–35.4% residual variance, 43% B5 attempt share,
ten uncertified arms). Methods constants are sourced to the pre-registrations and
listed separately in §2.

## 9. Verification performed

- `python scripts/build_paper.py` — exit 0; 9-page PDF, 664,873 bytes; 0 overfull boxes.
- `python scripts/count_paper_words.py` — exit 0; 2,276 body-only, 2,685
  body+captions+tables, **2,896/2,900** everything except references (official limit 3,000).
- `.venv/bin/python -m pytest tests -q` — 43 passed.
- `python notebook_regenerate.py` — 6 figures + 3 tables written.
- `python scripts/paper_addenda.py` — exit 0; 48,300 pool / 41,073 frame issues, 6 arms,
  stratified and full-availability E1 lifts, plus the `power` block (SE 1.99 pp, MDE 5.57 pp) and
  the 32 / 10 / 22 NVIDIA configuration asserts.
- `python scripts/descriptive_tables.py` — exit 0; regenerated `results/descriptive_tables.json`;
  the diff is the single D9.2 source string, all numbers identical.
- Clean-room run in `/tmp/clean_rev9` — exit 0; all six PNGs and all four
  table files byte-identical to the repo copies; the six PDFs regenerate with
  different metadata.
- Visual inspection of PDF pages 1–9 around the abstract, Introduction,
  Figure 1, Table 1, Table 2, Table 3, the judge section and Limitations; no
  clipped table cells or missing glyphs.
- `git diff --check` — clean.
