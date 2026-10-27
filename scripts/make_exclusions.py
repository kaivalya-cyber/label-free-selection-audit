"""Materialise the cross-corpus shared-issue exclusion list (DEVIATIONS D3).

Writes results/excluded_shared_issues.csv: casefolded instance ids present in both trajectory
corpora.  Deterministic; kill_test.py asserts its contents.
"""
import pandas as pd


def shared_issue_keys() -> list[str]:
    neb = pd.read_parquet("out/nebius_light.parquet", columns=["instance_id"])
    nvi = pd.read_parquet("out/nvidia_light.parquet", columns=["instance_id"])
    a = set(neb.instance_id.astype(str).str.casefold())
    b = set(nvi.instance_id.astype(str).str.casefold())
    return sorted(a & b)


if __name__ == "__main__":
    keys = shared_issue_keys()
    pd.DataFrame({"key": keys}).to_csv("results/excluded_shared_issues.csv", index=False)
    print(f"{len(keys)} shared issues excluded -> results/excluded_shared_issues.csv")
