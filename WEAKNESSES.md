# WEAKNESSES — what could make this wrong

Living document. Each item names the failure mode, its direction (does it inflate or deflate the
result), and the check that mitigates it or the fact that it does not.

## Data and labels

1. **Labels are taken as published, not recomputed.** No container runtime was available, so
   `resolved` comes from the dataset cards (Nebius/SWE-rebench harness for the nebius corpus,
   NVIDIA's collection for the nvidia corpus). If either party's eval is wrong, every risk number
   inherits the error. Direction: unknown, plausibly deflating (false negatives inflate risk).
   Mitigation: none available for free; flagged in the paper.
2. **Label noise inside a cluster is real and measured.** Two trajectories with byte-identical
   canonical patches can still carry different `resolved` labels (flaky or nondeterministic tests).
   That noise puts a floor under selective risk and is reported per config
   (`same_cluster_disagreement_share`). Direction: inflates measured risk, i.e. biases *against* the
   abstention rule's usefulness.
3. **The nvidia sampling rule is undocumented.** 1–3 trajectories per (config, issue) with no stated
   selection rule. If NVIDIA kept "up to 3 attempts, stop early on success", sample counts correlate
   with difficulty/luck, which would make the K-sample signal distribution depend on the selection
   rule rather than on policy stochasticity. Direction: unknown. Mitigation: per-config replication,
   and the nebius corpus (fixed ~10 attempts) is unaffected.
4. **`-1` unknown labels are not missing at random** (0%–25.8% by config, concentrated in v1.0 and
   minisweagent configs), and the label convention decides the verdict. Two decompositions are now
   reported side by side (DEVIATIONS D6): (a) re-scoring the certified rule with `-1` as failure at
   the same τ raises held-out risk from 15.8%→**24.0%** and 16.4%→**27.1%**, i.e. both HOLDS verdicts
   stop holding at α=0.20; (b) running the **whole pipeline** under `-1`-as-failure (pool and labels
   both change) certifies **0/11** configs at every α, versus 2/11 under drop-`-1`. The pre-registered
   convention (drop `-1`) is one of two defensible choices; both are in the headline table and no
   robustness claim is made without them.

## Signal definition

5. **Strict patch canonicalisation can manufacture disagreement.** Agents write scratch files
   (`issue.md`, `reproduce_issue.py`), tests, or reorder hunks; all of those make two *semantically*
   equivalent fixes non-identical. Direction: lowers measured agreement, so the rule abstains more
   than it needs to — conservative for risk, bad for coverage. This is the price of a normalizer that
   is mechanically checkable, and it was frozen before any result.
6. **Loose enough to manufacture agreement.** Because context lines and hunk headers are dropped,
   two patches that add the same lines in different places inside the same file (e.g. two different
   duplicated blocks) collapse to the same canonical form. Direction: inflates agreement. The 100-pair
   human review is the defence.
7. **K=3 is a coarse signal.** Largest-cluster share takes only three values, so τ has three levels
   and calibration power is limited: at α=0.05 a τ=1 set often cannot be certified with the available
   calibration issues. Direction: honest loss of power, reported as NO-COVERAGE rather than patched.

## Splits and inference

8. **Repository clusters are unbalanced.** The largest repo contributes 275+ issues (nebius) and 410
   (nvidia V2), so a handful of repos can dominate a bootstrap replicate. Direction: widens CIs,
   mostly conservative. The repo split balances issue counts, not repo sizes.
9. **Random-issue and temporal splits reuse repos.** Only the held-out-repo split tests the shift
   hypothesis; the other two are diagnostics. Overclaiming them would be a mistake.
10. **Temporal split changes both era and repo mix.** A temporal degradation cannot be attributed to
    time alone, because the repos differ across the cut.
11. **Bootstrap CIs on selective risk condition on which issues were submitted.** Resampling repos
    re-draws both the submission set and the risk within it, which is the deployable quantity, but it
    does not account for calibration uncertainty (the τ estimate is held fixed).
12. **Fixed-sequence LTT controls error only over the pre-registered τ grid.** Any post-hoc τ, or a
    τ chosen per config after looking at both splits, invalidates the bound.

## Multiple comparisons

13. **11 configs × 3 α × 3 splits are reported without FWER control.** Each cell carries its own
    δ=0.05 calibration guarantee; a handful of BREAKS/HOLDS cells will look extreme by chance. The
    per-config verdict pattern is the evidence, not any single cell. No config or α is dropped.

## What the kill test could not do (added after the run)

17. **`NO-COVERAGE` dominates: 10 of 12 arms certify nothing at any α.** The pre-registered rule can
    only report a calibrated guarantee when the most conservative τ passes on the calibration split.
    `0 BREAKS` therefore does **not** mean "the guarantee holds under repo shift"; it means the test
    had almost no power. Reading the null result as evidence *for* agreement-based abstention would be
    a serious error.
18. **The two cells that certify are the two easiest configs.** Base error 40.6% and 43.6%, versus
    49.0%–68.8% for every arm that failed to certify. Certification tracks how good the policy already
    is, which is itself consistent with "agreement is difficulty in disguise" at the config level, and
    means the two HOLDS verdicts are weak evidence of robustness (2 replications, both favourable).
19. **The certified coverage is tiny.** 5.6%–7.1% of issues at α=0.20, i.e. the rule answers "may I
    submit?" for about one issue in fifteen. A practitioner cannot use this to gate a pipeline.
20. **Neither difficulty baseline is a deployable rule, but the honest one is strong.**
    `difficulty_plugin_rate` includes the scored attempt's own label, so it is only an oracle ceiling
    (11/11 certification at 33%–66% coverage). The honest cross-fit version (the other K−1 attempts'
    labels, DEVIATIONS D7) still needs those siblings evaluated, but it certifies in 2/11 configs at
    α=0.05, 10/11 at α=0.10 and 11/11 at α=0.20 (coverage 27%–64%), and on the K=8 arm at every α.
    The paper's negative result is
    therefore *not* a gap against an oracle: it is that agreement certifies in 2/11 configs at
    α=0.20 only, while a label-count signal from sibling attempts certifies nearly everywhere. The
    earlier framing ("oracle gap = central result") is withdrawn; the comparison of agreement against
    the cross-fit signal is what B3 in PREREG-2 formalizes.
21. **The conditional diagnostic is confounded with D1.** Choosing the largest cluster's
    representative means that when two of three samples resolved, the agreeing pair is often the
    resolved pair; part of the apparent "agreement adds information beyond the success count" is
    mechanical. It is reported as a descriptive probe, not as a test.
22. **Certification power depends on the config's size and its τ=1 error, and both vary 3–4× across
    configs.** With 11 configs, the distribution of verdicts is coarse; no meta-analytic combination
    was pre-registered (and pooling across configs was explicitly forbidden).

## Part C (B1–B4), added after that run

23. **B2's analysis frame is 36% of the size its own prereg table implies.** PREREG-2 §4 cites 11,611
    pairs / 943 issues; the frozen K=8 sample yields **4,226 / 754** (DEVIATIONS D9: the table counted
    the full pool and the `gen_tests_correct` column). The observed 95% CI half-width is 0.016 AUROC,
    so the test cannot resolve effects smaller than that; a true 0.52 would often fail to separate.
    Direction: understates a real signal rather than inventing one.
24. **B2's pair set is selected by exit reason.** The own-test signal is present on 46.6% of sampled
    attempts, and nulls are concentrated in `submit` rows (56.9% vs 15.9% at max-iteration), so pairs
    that survive eligibility over-represent max-iteration attempts relative to the corpus. Direction
    unknown; PREREG §10.1 accepted this before the run.
25. **B4's matched-cost comparison is not interpolation-free.** `f(k)` is a step function; at the top
    budget a step between `f(K−1)` and `f(K)` makes the linear `f_interp` sit below the achieved
    rate. The K=8 arm's +0.096pp (p = 0.039) is exactly this: the stop-at-2 rule never changes the
    D1 submission, so `r_ad = f(8)` and the whole Δ is the interpolation corner. Direction: inflates
    Δ near `K_max`. At K=3 the same mechanism moves Δ by ≈0.01pp because the saving is 0.11 attempts.
26. **The kill test's submitted representative is not D1's written rule.** `build_units` breaks
    equal-size cluster ties by the smallest canonical string, not the smallest `trajectory_id`
    (D9). The rules pick different representatives in 18.2–20.3% of K=3 issues and 8.4% at K=8, and
    the arm-level resolve rate moves by −1.83 to +1.08pp. Every KILL_TEST.md number uses the
    implementation; B4 uses the documented rule, so its `f(K)` differs from the reported
    `resolved_rate`. The endpoint was not re-run and no kill-test number is restated. Direction: per
    arm, either way — this is a reproducibility defect, not a bias with a known sign.
27. **B3's win is a label-count signal, not a free rule.** It certifies 2/11 at α=0.05, 10/11 at
    0.10 and 11/11 at 0.20 where agreement certifies 0/0/2 — but it needs the other K−1 attempts
    evaluated first, and it inherits #26 through the unit label it subtracts. Reporting it as
    "difficulty is the better signal" without the evaluation cost would overstate the practical
    result.
28. **The sign tests have almost no resolution.** With 11 configs the exact two-sided threshold is
    10–1 (p = 0.0117); PREREG-2 §10 bullet 7 says 9–2, which actually gives p = 0.065 (D9). A 9–2 or
    8–3 split is not evidence of anything, and the B1/B4 family tests sit in that region.

## Pipeline risks

14. **Signal and label live in different columns from the same row.** A join bug would silently
    mis-pair patches with labels. Mitigation: `validate="1:1"` merges plus row-count assertions at
    every step; trajectory ids are unique (0 duplicates in recon).
15. **Instance-key case folding is load-bearing.** Without it, corpora look disjoint (exact-string
    overlap is 0 while the true overlap is 204 issues). Any script that reintroduces raw string joins
    would double-count; the shared-issue exclusion list is materialised for audit.
16. **Free-tier infrastructure.** Reads are range requests over the HF CDN with no retries pinned to a
    snapshot/revision. A dataset revision change would silently alter the numbers; the recon records
    the file inventory and sizes, which is the only version evidence.

## Judge study (PREREG-3, D14 backend)

29. **The judge is not the frozen NF4 estimator.** The frozen 26B-A4B NF4 path cannot load on
    2×T4 because the 30 MoE layers store 128 experts as 3-D parameters that bitsandbytes leaves
    in bf16; the approved D14 backend is the official QAT Q4_0 GGUF via llama.cpp. The primary
    number (0.5786) belongs to **26B-A4B Q4_0 (llama.cpp)** and is not an NF4 result. A bf16 or
    NF4 control is impossible at this context on 2×T4, so the study cannot separate judge quality
    from quantisation quality.
30. **The labels are the published resolved flags, not ground truth.** The estimand is agreement
    with the dataset's label; a judge can be right where the harness is flaky and still score below
    0.5 (WEAKNESSES #1–#2). The within-issue design cancels issue difficulty but not label noise
    that is shared by both attempts in a pair.
31. **AUROC is the only calibration-free claim.** The judge's `p_yes` is extremely confident
    (median 0.817; 25% 0.231, 75% 0.974), and no calibration, threshold or abstention analysis was
    registered. A high AUROC does not license using the raw probability as a correctness estimate.
32. **Pairs share attempts and issues.** The 4,226 pairs come from 5,466 attempts and 1,128 issues;
    the repo-clustered bootstrap (641 clusters) is the only inference reported, but it cannot
    remove the dependence between pairs that reuse an attempt.
33. **Prompt truncation affects a quarter of patches.** 26.1% of patches and 1.2% of issues hit the
    frozen head+tail cap; the realised no-truncation pair share is **52.6%** (2,221/4,226), lower
    than PREREG-3 §4.3's ≈74% (that figure is optimistic for a pair of attempts). The exploratory
    split is flat (0.5772 vs 0.5800), which argues against truncation driving the result, but it is
    a subset comparison, not a causal test.
34. **The own-test comparison is selected.** Only 1,381 of 4,226 pairs have non-null own-test
    signals on both attempts; the 0.5112 estimate and its paired difference are on that subset,
    not the full sample.
35. **The pilot needed a second session.** The first GGUF pilot worker exposed one T4 and failed
    context creation; the restarted pilot (0.43 h) and the main run (4.75 h) used both cards. The
    failed session produced no scores; the sealed pilot hash covers only the successful run.
36. **The D12 projection was conservative.** It predicted 8.16 h for N=4,226; the actual model wall
    was 5.18 h (pilot + main), plus about 0.9 h of diagnostics. The cap was not approached, but the
    projection's 2× token factor is not a throughput measurement and should not be reused as one.
