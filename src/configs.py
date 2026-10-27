"""The 11 frozen configs (PREREG §1). Every analysis script reads this registry."""


def _nv(tag, version, agent, model, benchmark):
    return {"tag": tag, "dataset": "nvidia", "version": version, "agent": agent,
            "model": model, "benchmark": benchmark,
            "prefix": f"data/{agent}/{model}/{benchmark}",
            "display": f"{version} {agent} {model} {benchmark}", "k": 3}


CONFIGS = [
    {"tag": "nebius_openhands", "dataset": "nebius", "prefix": None,
     "display": "nebius OpenHands v0.54.0 + Qwen3-Coder-480B", "k": 3},
    _nv("v1.0_openhands_minimax_m25_swe-rebench-v2", "v1.0", "openhands", "minimax_m25", "swe-rebench-v2"),
    _nv("v1.0_openhands_qwen35_122b_swe-rebench-v2", "v1.0", "openhands", "qwen35_122b", "swe-rebench-v2"),
    _nv("v1.0_sweagent_minimax_m25_swe-rebench-v2", "v1.0", "sweagent", "minimax_m25", "swe-rebench-v2"),
    _nv("v1.0_sweagent_qwen35_122b_swe-rebench-v2", "v1.0", "sweagent", "qwen35_122b", "swe-rebench-v2"),
    _nv("v1.1_minisweagent_qwen36_27b_scale-swe", "v1.1", "minisweagent", "qwen36_27b", "scale-swe"),
    _nv("v1.1_minisweagent_qwen36_27b_swe-rebench-v2", "v1.1", "minisweagent", "qwen36_27b", "swe-rebench-v2"),
    _nv("v1.1_sweagent_qwen36_27b_scale-swe", "v1.1", "sweagent", "qwen36_27b", "scale-swe"),
    _nv("v1.1_sweagent_qwen36_27b_swe-rebench-v2", "v1.1", "sweagent", "qwen36_27b", "swe-rebench-v2"),
    _nv("v1.2_minisweagent_qwen38_27b_scale-swe", "v1.2", "minisweagent", "qwen38_27b", "scale-swe"),
    _nv("v1.2_minisweagent_qwen38_27b_swe-rebench-v2", "v1.2", "minisweagent", "qwen38_27b", "swe-rebench-v2"),
]

K8_ARM = {"tag": "nebius_openhands", "k": 8}

ALPHAS = [0.05, 0.10, 0.20]
DELTA = 0.05
TAUS_K3 = [1.0, 2 / 3, 1 / 3]
TAUS_K8 = [1.0, 7 / 8, 6 / 8, 4 / 8, 1 / 8]
N_MIN = 30
B_BOOT = 2000
