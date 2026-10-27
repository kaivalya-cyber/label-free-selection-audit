"""The pre-registered kill test (PREREG.md + DEVIATIONS.md D1-D3).

Single-shot: run once, output results/kill_test.json + KILL_TEST.md.
Usage: .venv/bin/python scripts/kill_test.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.configs import ALPHAS, B_BOOT, CONFIGS, DELTA, N_MIN, TAUS_K3, TAUS_K8  # noqa: E402
from src.normalize import largest_cluster_share  # noqa: E402
from src.risk import (breaks_verdict, cluster_bootstrap_lower, ltt_select,  # noqa: E402
                      seeded_rng)
from src.splits import (EVAL, CALIB, assert_no_repo_leak, assert_single_side, heldout_repo,  # noqa: E402
                        random_by_issue, temporal)

BASE = Path("out/signals")
_UNIT_CACHE: dict = {}   # (tag, k, minus1_as_failure, source) -> units frame


# ---------------------------------------------------------------- shared-issue exclusion (D3)
def shared_issue_keys() -> set[str]:
    neb = pd.read_parquet("out/nebius_light.parquet", columns=["instance_id"])
    nvi = pd.read_parquet("out/nvidia_light.parquet", columns=["instance_id"])
    a = set(neb.instance_id.astype(str).str.casefold())
    b = set(nvi.instance_id.astype(str).str.casefold())
    sh = sorted(a & b)
    pd.DataFrame({"key": sh}).to_csv("results/excluded_shared_issues.csv", index=False)
    return set(sh)


# ---------------------------------------------------------------- unit construction
def build_units(cfg: dict, k: int, shared: set[str], minus1_as_failure: bool = False,
                source: str = "strict") -> pd.DataFrame:
    """One row per issue: K sampled trajectories -> agreement signals + submitted-label.

    source="f1" is the DEVIATIONS D4 sensitivity: same sampling seed and pool, F1 canonical form.
    """
    tag = cfg["tag"]
    ckey = (tag, k, minus1_as_failure, source)
    if ckey in _UNIT_CACHE:
        return _UNIT_CACHE[ckey].copy()
    if source == "f1":
        df = pd.read_parquet(BASE.parent / "signals_f1" / f"{tag}.parquet")
        df = df.rename(columns={"f1": "canonical", "f1_files": "files", "f1_lines": "changed_lines"})
    else:
        df = pd.read_parquet(BASE / f"{tag}.parquet")
    if minus1_as_failure:
        df.loc[df.resolved == -1, "resolved"] = 0
    df = df[df.resolved.isin([0, 1])]
    df = df[~df.key.isin(shared)]
    rows = []
    for key, g in df.groupby("key", sort=True):
        ids = np.array(sorted(g.trajectory_id.astype(str).tolist()))
        if len(ids) < k:
            continue
        rng = seeded_rng(tag, key)
        # PREREG §1 verbatim: rng.choice(sorted(trajectory_ids), size=K, replace=False)
        picked = rng.choice(ids, size=k, replace=False)
        s = g.set_index("trajectory_id").loc[picked].reset_index()
        resumes = {}
        for tid, can in zip(s.trajectory_id, s.canonical):
            resumes.setdefault(can, []).append(tid)
        sizes = {c: len(t) for c, t in resumes.items()}
        top = max(sizes.values())
        best = min(c for c, n in sizes.items() if n == top)
        rep = min(resumes[best])
        lab = int(s.loc[s.trajectory_id == rep, "resolved"].iloc[0])
        rows.append({
            "key": key,
            "repo": s.repo.iloc[0],
            "agreement": largest_cluster_share(s.canonical.tolist()),
            "files_agreement": largest_cluster_share(s.files.tolist()),
            "patch_size": float(np.median(s.changed_lines.to_numpy())),
            "steps": float(np.median(s.steps.to_numpy())),
            "rate": float(s.resolved.mean()),
            # Part A3 / PREREG-2 B3: cross-fit (leave-one-out) difficulty. The estimate is built
            # from the OTHER K-1 attempts, so it never contains the label it is used to score.
            "rate_loo": float((s.resolved.sum() - lab) / (k - 1)),
            "label": lab,
            "picked": "|".join(sorted(str(x) for x in picked)),
            "n_resolved": int(s.resolved.sum()),
            "cluster_size": int(top),
            "same_cluster_disagreement": int(
                s.groupby("canonical").resolved.nunique().max() > 1),
        })
    out = pd.DataFrame(rows)
    assert len(out) == out.key.nunique()
    _UNIT_CACHE[ckey] = out
    return out.copy()


def attach_created_at(cfg: dict, units: pd.DataFrame) -> pd.Series:
    if cfg["dataset"] == "nebius":
        src = pd.read_parquet("out/swerebench_v1_dates.parquet", columns=["instance_id", "created_at"])
    elif cfg["benchmark"] == "swe-rebench-v2":
        src = pd.read_parquet("out/swerebench_v2_dates.parquet", columns=["instance_id", "created_at"])
    else:
        return pd.Series([None] * len(units), index=units.index)
    src["key"] = src.instance_id.astype(str).str.casefold()
    src["created_at"] = pd.to_datetime(src.created_at).astype(str)
    m = units[["key"]].merge(src[["key", "created_at"]].drop_duplicates("key"), on="key", how="left")
    return pd.Series(m.created_at.to_numpy(), index=units.index)


# ---------------------------------------------------------------- evaluation
def evaluate(units: pd.DataFrame, side: pd.Series, signal: str, taus, alpha: float,
             tag: str, split: str, higher_is_better: bool = True) -> dict:
    calib = units[side == CALIB]
    ev = units[side == EVAL]
    err_c = (1 - calib.label).to_numpy(dtype=float)
    s_c = calib[signal].to_numpy(dtype=float)
    if not higher_is_better:
        s_c = -s_c
    out = ltt_select(taus, s_c, err_c, alpha=alpha, delta=DELTA, n_min=N_MIN)
    rec = {"tau": out["tau"], "certified": out["certified"], "calib_trace": out["trace"],
           "n_calib": int(len(calib)), "n_eval": int(len(ev)),
           "calib_base_rate": float(err_c.mean()) if len(err_c) else None,
           "eval_base_rate": float((1 - ev.label).mean()) if len(ev) else None}
    if out["tau"] is None:
        rec.update({"n_submitted": 0, "coverage": 0.0, "risk": None, "ci": None,
                    "verdict": "NO-COVERAGE"})
        return rec
    ev_s = ev[signal].to_numpy(dtype=float) * (1 if higher_is_better else -1)
    submitted = ev_s >= out["tau"]
    err_e = (1 - ev.label).to_numpy(dtype=float)
    boot = cluster_bootstrap_lower(ev.repo.to_numpy(), err_e, submitted,
                                   B=B_BOOT, seed_parts=(tag, split, alpha, signal))
    rec.update({
        "n_submitted": int(submitted.sum()),
        "coverage": float(submitted.mean()),
        "risk": boot["risk"],
        "ci": {"lower": boot["lower"], "upper": boot["upper"], "n_clusters": boot["n_clusters"]},
        "verdict": breaks_verdict(boot, alpha),
    })
    return rec


def run_config(cfg: dict, k: int, shared: set[str], convention: str = "drop",
               full: bool = True) -> dict:
    """convention="drop" is the PREREG primary (resolved=-1 rows dropped before sampling);
    convention="minus1_failure" is the alternative label convention (resolved=-1 -> failure),
    reported symmetrically per DEVIATIONS D6 (the two are separate pipelines: they differ in pool
    eligibility and in labels). full=False skips baselines/F1/truncation, used for that pass."""
    assert convention in ("drop", "minus1_failure")
    tag = cfg["tag"]
    ktag = f"{tag}@K{k}"
    units = build_units(cfg, k, shared, minus1_as_failure=(convention == "minus1_failure"))
    cats = attach_created_at(cfg, units)
    sides = {"random_issue": pd.Series([random_by_issue(ktag, kk) for kk in units.key], index=units.index),
             "heldout_repo": pd.Series(heldout_repo(ktag, dict(zip(units.key, units.repo)))).reindex(units.key)}
    sides["heldout_repo"] = sides["heldout_repo"].set_axis(units.index)
    assert_no_repo_leak(dict(zip(units.key, units.repo)), dict(zip(units.key, sides["heldout_repo"])))
    for s in sides.values():
        assert_single_side(zip(units.key, s))
    res0 = {"temporal_missing_issues": int(cats.isna().sum())}
    if cats.notna().any():
        cats = cats.fillna("9999")
        sides["temporal"] = pd.Series(temporal(dict(zip(units.key, cats)))).reindex(units.key).set_axis(units.index)

    taus = TAUS_K8 if k == 8 else TAUS_K3
    res = {"config": tag, "display": cfg["display"], "k": k, "convention": convention,
           "units": int(len(units)), "repos": int(units.repo.nunique()),
           "base_error": float((1 - units.label).mean()),
           "resolved_rate": float(units.label.mean()),
           "agreement_levels": {str(a): int(v) for a, v in units.agreement.value_counts().items()},
           "same_cluster_disagreement_share": float(units.same_cluster_disagreement.mean()),
           "splits": {}, "baselines": {}, "temporal_missing_issues": int(cats.isna().sum())}
    for split, side in sides.items():
        res["splits"][split] = {"n_calib": int((side == CALIB).sum()), "n_eval": int((side == EVAL).sum()),
                                "alpha": {}}
        for alpha in ALPHAS:
            res["splits"][split]["alpha"][str(alpha)] = evaluate(
                units, side, "agreement", taus, alpha, ktag, split)
        # secondary signal: files-touched agreement
        res["splits"][split]["secondary_files"] = {
            str(a): evaluate(units, side, "files_agreement", taus, a, ktag, split, True)
            for a in ALPHAS}

    # always-submit reference on the held-out-repo eval side (reported for both conventions)
    side = sides["heldout_repo"]
    ev = units[side == EVAL]
    err = (1 - ev.label).to_numpy(dtype=float)
    always = {}
    for a in ALPHAS:
        boot = cluster_bootstrap_lower(ev.repo.to_numpy(), err, np.ones(len(ev), bool),
                                       B=B_BOOT, seed_parts=(ktag, "always", a))
        always[str(a)] = {"risk": boot["risk"], "coverage": 1.0, "n_submitted": len(ev),
                          "ci": {"lower": boot["lower"], "upper": boot["upper"]},
                          "verdict": breaks_verdict(boot, a)}
    res["baselines"]["always_submit"] = always
    if not full:
        return res

    # baselines: calibrated with the identical procedure on the held-out-repo split (headline).
    # "difficulty_cross_fit" (Part A3) is the honest difficulty signal: the unit's own label is
    # excluded from its score. "difficulty_plugin_rate" keeps all K labels, including the scored
    # one, so it is an oracle-adjacent ceiling, not a deployable rule.
    calib = units[side == CALIB]
    for name, col, hib in [("patch_size", "patch_size", False),
                           ("step_count", "steps", False),
                           ("difficulty_cross_fit", "rate_loo", True),
                           ("difficulty_plugin_rate", "rate", True)]:
        vals = calib[col].to_numpy()
        if col in ("rate", "rate_loo"):
            grid = list(taus)
        else:
            qs = np.quantile(vals, [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
            grid = list(-qs) if not hib else list(qs)
        grid = sorted(grid, reverse=True)  # most conservative first
        res["baselines"][name] = {str(a): evaluate(units, side, col, grid, a, ktag,
                                                   "heldout_repo_baseline", hib)
                                  for a in ALPHAS}

    # DEVIATIONS D4 sensitivity: F1 canonical form, evaluated AT the primary tau (no recalibration)
    f1 = build_units(cfg, k, shared, source="f1")
    assert set(f1.key) == set(units.key), "F1 frame must cover the same issues"
    m = units[["key", "picked"]].merge(f1[["key", "picked"]], on="key", suffixes=("", "_f1"))
    assert (m.picked == m.picked_f1).all(), "F1 sampling must select the same trajectories"
    res["f1_sensitivity"] = {"agreement_levels": {str(a): int(v) for a, v in f1.agreement.value_counts().items()},
                             "alpha": {}}
    for alpha in ALPHAS:
        tau = res["splits"]["heldout_repo"]["alpha"][str(alpha)]["tau"]
        if tau is None:
            res["f1_sensitivity"]["alpha"][str(alpha)] = {"tau": None, "coverage": 0.0, "risk": None,
                                                          "n_submitted": 0}
            continue
        ev_f1 = f1.set_index("key").loc[units.key].reset_index()
        side_vals = side.to_numpy()
        sub = ev_f1[side_vals == EVAL]
        m2 = sub.agreement.to_numpy() >= tau
        res["f1_sensitivity"]["alpha"][str(alpha)] = {
            "tau": tau, "n_submitted": int(m2.sum()),
            "coverage": float(m2.mean()) if len(sub) else None,
            "risk": float((1 - sub.label.to_numpy()[m2]).mean()) if m2.any() else None}

    # label-noise / truncation checks
    if cfg["dataset"] == "nebius":
        lam = pd.read_parquet("out/nebius_light.parquet", columns=["exit_status"])
        res["truncation"] = {"max_iteration_share": float(lam.exit_status.str.contains(
            "maximum iteration", na=False).mean()),
            "non_submit_share": float((lam.exit_status != "submit").mean())}
    # sensitivity: -1 counted as failure, at the primary tau (no recalibration)
    sen = build_units(cfg, k, shared, minus1_as_failure=True)
    if len(sen):
        sen_side = pd.Series(heldout_repo(ktag, dict(zip(sen.key, sen.repo)))).reindex(sen.key)
        sen_side = sen_side.set_axis(sen.index)
        ev_s = sen[sen_side == EVAL]
        res["minus1_sensitivity"] = {}
        for alpha in ALPHAS:
            tau = res["splits"]["heldout_repo"]["alpha"][str(alpha)]["tau"]
            if tau is None:
                res["minus1_sensitivity"][str(alpha)] = {"tau": None, "coverage": 0.0,
                                                         "risk": None, "n_submitted": 0}
                continue
            sub = ev_s.agreement.to_numpy() >= tau
            res["minus1_sensitivity"][str(alpha)] = {
                "tau": tau, "n_submitted": int(sub.sum()), "coverage": float(sub.mean()),
                "risk": float((1 - ev_s.label.to_numpy()[sub]).mean()) if sub.any() else None,
                "n_eval": int(len(ev_s))}
    return res


def main():
    shared = shared_issue_keys()
    out = {"alphas": ALPHAS, "delta": DELTA, "n_min": N_MIN, "b_boot": B_BOOT,
           "excluded_shared_issues": len(shared), "configs": {}, "k8_arm": None,
           "configs_minus1_failure": {}, "k8_arm_minus1_failure": None}
    for cfg in CONFIGS:
        if not (BASE / f"{cfg['tag']}.parquet").exists():
            print(f"SKIP missing signals: {cfg['tag']}", flush=True)
            continue
        print(f"running {cfg['tag']} ...", flush=True)
        out["configs"][cfg["tag"]] = run_config(cfg, 3, shared)
        print(json.dumps({k: v for k, v in out["configs"][cfg["tag"]].items()
                          if k in ("units", "repos", "base_error")}), flush=True)
    neb = next(c for c in CONFIGS if c["tag"] == "nebius_openhands")
    print("running nebius K=8 arm ...", flush=True)
    out["k8_arm"] = run_config(neb, 8, shared)
    # DEVIATIONS D6 / Part A2: the same pipelines under the alternative label convention
    # (resolved=-1 as failure). Each is a full certification (own tau, own interval, own verdict);
    # neither convention is primary in the paper.
    print("running -1-as-failure pipelines ...", flush=True)
    for cfg in CONFIGS:
        if cfg["tag"] in out["configs"]:
            out["configs_minus1_failure"][cfg["tag"]] = run_config(
                cfg, 3, shared, convention="minus1_failure", full=False)
    out["k8_arm_minus1_failure"] = run_config(neb, 8, shared, convention="minus1_failure",
                                              full=False)
    print("done -1-as-failure pipelines", flush=True)
    Path("results").mkdir(exist_ok=True)
    with open("results/kill_test.json", "w") as fh:
        json.dump(out, fh, indent=1)
    print("wrote results/kill_test.json")


if __name__ == "__main__":
    main()
