# DEVIATIONS

Chronological. Rule: anything that changes PREREG.md after freeze, or any decision taken while
looking at results, goes here with its reason. Entries marked **[pre-evaluation]** were written before
any outcome-vs-signal number was computed; they complete an under-specified detail rather than tune
anything.

## D1 — which patch is "submitted" (2026-10-26) **[pre-evaluation]**

PREREG §1/§3 fixes the unit and the rule but not which trajectory's patch is submitted when several
trajectories agree. Without fixing this, "selective risk" is ambiguous (per-trajectory success vs
any-sample-succeeded), and the difference is large whenever clusters disagree.

Fixed now, before any signal-vs-label computation:

- If the rule says *submit*, the submitted artifact is the patch of the **largest canonical cluster**;
  ties between equally large clusters are broken by the smallest `trajectory_id` in the cluster, and
  within the chosen cluster the representative is the smallest `trajectory_id`.
- The issue-level label is that representative trajectory's own published `resolved` value.
- Consequence (stated up front): two trajectories in the same cluster can carry different labels
  (eval nondeterminism / flaky tests). Such issues are label noise, not signal, and are reported as
  part of the label-noise check rather than removed.

No other definition was tried; nothing was computed before this entry.

## D2 — Scale-SWE configs have no temporal split (2026-10-26) **[pre-evaluation]**

PREREG §4 lists a temporal split for corpora with `created_at`. Recon showed AweAI-Team/Scale-SWE has
no timestamps at all, so the 4 Scale-SWE configs report `n/a` for that split instead of a number.
This is a data availability fact from Phase 0 (DATA_RECON §4), not a choice made after seeing results.

## D3 — the 204 cross-corpus shared issues are excluded everywhere (2026-10-26) **[pre-evaluation]**

PREREG §1 already says they are excluded from all primary analyses; recorded here so the exclusion
list is auditable: `results/excluded_shared_issues.csv` (casefolded instance ids, 204 rows). A
sensitivity run with them retained in nebius only is reported as a footnote, never as a primary number.
