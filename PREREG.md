# PREREG — agreement-based abstention, calibrated → held-out

Status: **frozen at commit `4b09dc0`** (the commit that adds this file). Any later change is a
`DEVIATIONS.md` entry. No held-out evaluation has been run at freeze time; only structure
(DATA_RECON.md) and the normalizer unit tests exist.

Question: for SWE agents, does an agreement-based abstention rule calibrated to a target selective
error rate on one set of repos keep that error rate on held-out repos? Hypothesis under attack:
"agreement is difficulty in disguise" (so it should degrade under repo/era shift).

## 1. Unit and sample counts

Unit = one issue `x` in one config `c`, with **K=3 trajectories drawn without replacement** from the
config's pool of trajectories for `x` (no row is used twice; issues with `n_x < 3` are dropped).

- K=3 is fixed by recon: no nvidia config has >3 trajectories per (config, issue); the nebius config
  has median 10. K=3 is the only K available in all 11 configs.
- A second arm uses **K=8 on the nebius config only** (the only corpus with n_x ≥ 8), reported
  separately; it is a robustness check on signal resolution, never pooled with K=3 results.

**Configs (fixed, no additions):** the 10 nvidia configs with ≥3,000 issues at K=3 —
`v1.0/{openhands,sweagent} × {minimax_m25, qwen35_122b} × swe-rebench-v2`,
`v1.1/{sweagent,minisweagent} × qwen36_27b × {swe-rebench-v2, scale-swe}`,
`v1.2/minisweagent/qwen38_27b × {swe-rebench-v2, scale-swe}`
— plus `nebius/SWE-rebench-openhands-trajectories` (OpenHands v0.54.0 + Qwen3-Coder-480B) = **11
configs**. Each is analysed alone. **No pooling across configs in any primary number.**

**Deterministic subsampling:**
`rng = numpy.random.default_rng(int(sha256(f"{config}|{casefold(instance_id)}").hexdigest()[:16], 16))`,
then `rng.choice(sorted(trajectory_ids), size=K, replace=False)`. Casefolded instance keys are used
throughout (DATA_RECON §5: the corpora disagree on owner case).

**Issue exclusion (double-counting):** the 204 issues present in both trajectory corpora
(DATA_RECON §5) are excluded from **all** primary analyses. Sensitivity run keeps them in nebius
only (reported as a footnote, not a primary number).

**Labels:** `resolved ∈ {0,1}` is the target (1 = solved). `resolved = -1` (nvidia only; 0%–25.8% by
config) is dropped from the primary analysis; sensitivity run scores it as failure. Nebius has no
`-1`. Labels are taken as published; the eval harness was not re-run (see WEAKNESSES.md).

## 2. Signals (exactly two)

### 2.1 Primary: largest-cluster share of identical normalized patches
`a(x) = max_cluster_size / K`, where patches are grouped by exact equality of their **canonical form**
below. At K=3: `a ∈ {1/3, 2/3, 1}`.

**Canonical form of a unified diff (the normalizer), exactly:**
1. Input is the trajectory's final patch string (`nebius: model_patch`; `nvidia:
   metadata.model_patch.patch`). Decode UTF-8 with `errors="replace"`; `\r\n` and `\r` → `\n`.
2. Split into per-file sections at lines matching `^diff --git ` (a section may also start at a
   `^--- ` line when no `diff --git` header is present).
3. For each section, determine `path`:
   - prefer the `b/...` path of `^diff --git a/(.+) b/(.+)$`;
   - else the `^(\+\+\+) (b/)?(.+)$` line (strip a trailing tab+timestamp);
   - else the `^--- (a/)?(.+)$` line; drop a leading `a/` or `b/`, strip surrounding quotes, strip a
     leading `./`, drop sections whose path is `/dev/null`.
   Paths are kept case-sensitive (Linux paths) and are the **files-touched** set.
4. Keep only changed lines: `^+` and `^-` lines, **excluding** `+++ `/`--- ` header lines. Drop all
   other lines: `index ...`, `@@ ... @@` hunk headers, mode/rename/similarity lines,
   `\ No newline at end of file`, `Binary files ... differ`, `GIT binary patch`, blank lines outside
   hunks, and context lines (`^ `).
5. Per changed line: `rstrip()` (drop trailing whitespace only; internal whitespace, tabs and
   indentation are preserved verbatim — indentation is semantic in Python).
6. Canonical form = file sections sorted by `path`, each rendered as `path + "\n"` followed by its
   kept lines joined by `\n`, sections joined by `\n\n`. A patch with no kept `+/-` lines (including
   the empty string) canonicalises to the single token `<no-change>`; all no-change patches therefore
   cluster together (documented consequence; measured incidence is 0.083% in nebius and 0.066% in
   nvidia).
7. "Identical" means byte-equal canonical strings. No fuzzy matching, no similarity thresholds, no
   LLM judging, no path fuzzing.

Known and accepted limitations of this normalizer: it treats the same added line placed in different
files as different (path-keyed), treats reordered hunks within a file as different (order-preserving),
and treats a moved-but-identical line block in a different file as different. These are pre-registered
choices, not post-hoc knobs.

### 2.2 Secondary: files-touched agreement
File set `F_x,i` = normalized paths from step 3. `f(x) = max_{S} |{i : F_x,i = S}| / K`; exact set
equality. At K=3: `{1/3, 2/3, 1}`. No other signals enter the primary analysis.

## 3. Decision rule and calibration

Rule: **submit iff signal ≥ τ**, nothing else (no issue features, no thresholds on labels).

Candidate τ: for K=3, `{1/3, 2/3, 1}` (1/3 = always submit; 1 = unanimous only). For the K=8 arm,
`{1/8, 4/8, 6/8, 7/8, 1}` (fixed before any outcome is seen; chosen so coverage differs materially:
any-agreement, majority, 6/8, 7/8, unanimous).

Calibration (on the calibration split only): fixed-sequence Learn-then-Test over τ ordered from most
conservative (highest τ) to least. For each τ in order, compute `n_sub`, `n_err` on calibration issues
with signal ≥ τ and the one-sided Clopper–Pearson upper bound
`U = Beta.ppf(1 - δ, n_err + 1, n_sub - n_err)` (0 errors ⇒ `1 - δ^(1/n_sub)`; `n_sub = 0` ⇒ pass).
Stop at the first τ whose `U > α`; select the previous τ. If the first (most conservative) τ fails,
the rule is **"abstain always"** (coverage 0). Validity: fixed-sequence testing controls the Type-I
error at δ over the τ grid without multiplicity correction.

Frozen constants: **δ = 0.05** (one-sided), `α ∈ {0.05, 0.10, 0.20}` (all three pre-registered; 0.05
because the task is patch acceptance, 0.20 because base error is 35%–65% and a usable cover must
exist), minimum `n_sub = 30` for a τ to be certifiable at all (smaller ⇒ not certified; report as
such). No α outside this grid is reported as a primary result.

## 4. Splits (all fixed before evaluation)

Issue-level, per config, computed from casefolded issue keys and repo names only (labels unused):

1. **Random-by-issue**: `sha256("rand|{config}|{key}")` first byte `< 128` ⇒ calibration, else
   evaluation. Half of the issues each side, random with respect to repo.
2. **Held-out-repo** (headline): repos sorted by descending issue count, ties by
   `sha256("repo|{config}|{repo}")`; each repo assigned to the side with fewer issues so far (first
   repo to calibration). Guarantees **zero repo overlap** between calibration and evaluation
   (asserted in code) and near-equal issue counts. This is the split that tests the hypothesis.
3. **Temporal**: instance `created_at` from the source corpora (SWE-rebench-V1 for the nebius config,
   SWE-rebench-V2 for V2-sourced configs; **unavailable for the 4 Scale-SWE configs**, which are
   reported as "not applicable"). Cut at **2023-01-01**: earlier ⇒ calibration, later ⇒ evaluation.
   No tuning of the cut date.

Split integrity assertions (unit-tested): no issue appears on both sides of any split; the repo split
has zero repo overlap; every issue has exactly one split label; split membership is stable across runs.

## 5. Endpoints, verdict, and stopping rule

Per config × split × α, on the evaluation split only, among submitted issues:
**selective risk** `= mean(1 - resolved)`, **coverage** `= n_submitted / n_eval_issues`, plus
`n_submitted`.

**BREAKS criterion** (headline, held-out-repo split): the lower bound of the repo-clustered
bootstrap CI of selective risk exceeds `α + 0.05`. Bootstrap: resample repos with replacement,
B = 2,000, seed = `sha256("boot|{config}|{α}")`, statistic recomputed on the resampled submitted
issues, lower bound = 2.5th percentile. Otherwise **HOLDS**. If coverage is 0 the verdict is
`NO-COVERAGE` (not a pass).

**Sanity check (pipeline gate):** on the random-by-issue split, realized risk must be ≤ α for every
config reported as HOLDS; if any config fails this in-distribution check, the pipeline is suspect →
stop and debug, do not report held-out verdicts until explained.

**Decision-theoretic reporting:** verdicts are reported per α and per config; no config is dropped
after seeing results; no α is added later.

## 6. Baselines (each calibrated with the identical LTT/CP procedure, same split, same α)

1. **Always-submit** (no calibration): coverage 1, risk = base error on evaluation.
2. **Patch size**: signal = median number of changed lines across the K sampled patches; submit iff
   `size ≤ τ` (τ grid = deciles of the calibration distribution, fixed as the 9 interior deciles plus
   −∞/∞). Direction justified by recon only (patch size available in all configs).
3. **Step count**: signal = median assistant-message count across the K sampled trajectories; submit
   iff `steps ≤ τ`, τ grid = calibration deciles.
4. **Difficulty-band (plug-in resolve rate, oracle-adjacent diagnostic)**: signal = empirical resolve
   rate among the same K sampled labels; submit iff `rate ≥ τ`, τ ∈ {1/3, 2/3, 1}. This uses the
   labels, so it is a diagnostic ceiling, **not** a deployable rule, and is labelled as such in every
   table.

Baselines exist to show whether agreement adds anything beyond trivially available quantities; they
are not candidates for selection.

## 7. Normalizer validation gate (must pass before any result is reported)

Before the evaluation run: draw **100 patch pairs** (same issue, same config, two distinct
trajectories), stratified 50 pairs judged identical / 50 judged different by the normalizer, across
≥5 configs, fixed by `seed=sha256("validate_pairs")`. Emit `NORMALIZER_VALIDATION.md` with the raw
patches, canonical forms, and the verdict, for the human spot-check. Any normalizer change after that
review is a `DEVIATIONS.md` entry and voids the review until redone. **No evaluation number is
computed or reported until this gate is signed off.**

## 8. Operational commitments

- Held-out evaluation is run **once**, by `reproduce_all.sh`, after PREREG and normalizer sign-off.
- Every number in the paper comes from one of: `results/*.json|csv`, `KILL_TEST.md`, or the unit
  tests. `CLAIMS_LEDGER.md` maps claim → number → source file.
- Seeds, hashes, α, δ, τ grids, K, config list, split rules and the BREAKS threshold above are frozen.
- Truncation/label-noise checks reported alongside every primary table: max-iteration share (nebius
  `exit_status`), `-1` share (nvidia), and the `-1`-as-failure sensitivity.
- Leak checks reported: repo overlap across splits (must be 0), issue overlap across corpora (204,
  excluded), duplicate trajectory rows (0).
- Free compute only: no paid APIs/GPUs; `COST_LOG.md` remains $0.

## 9. What would falsify the hypothesis, stated in advance

The hypothesis "agreement is difficulty in disguise" predicts that under held-out-repo shift the
calibrated guarantee degrades: risk rises above `α` while coverage stays materially above the
difficulty-baseline coverage at the same α. `HOLDS` on all configs at all α would be evidence against
it; `BREAKS` on a majority of configs at `α = 0.10`, or selective risk tracking the plug-in resolve
rate more closely than it tracks agreement, would be evidence for it. Both outcomes are publishable;
a clean `NO-COVERAGE` at `α = 0.05` is reported as a negative result, not hidden.
