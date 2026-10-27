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
   minisweagent configs). Dropping them can bias risk in either direction; the pre-registered
   sensitivity run (treat `-1` as failure) brackets it.

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
20. **The difficulty baseline is a ceiling, not a competitor.** It needs the K samples' own success
    labels, which in deployment requires running the tests — at which point abstention is moot. Its
    11/11 certification at 33%–66% coverage bounds what any honest signal could achieve here, and the
    gap between it and agreement (7% coverage) is the paper's central negative result.
21. **The conditional diagnostic is confounded with D1.** Choosing the largest cluster's
    representative means that when two of three samples resolved, the agreeing pair is often the
    resolved pair; part of the apparent "agreement adds information beyond the success count" is
    mechanical. It is reported as a descriptive probe, not as a test.
22. **Certification power depends on the config's size and its τ=1 error, and both vary 3–4× across
    configs.** With 11 configs, the distribution of verdicts is coarse; no meta-analytic combination
    was pre-registered (and pooling across configs was explicitly forbidden).

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
