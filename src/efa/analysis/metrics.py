"""Per-cell summaries from games.jsonl: realized cooperation, stated probability, welfare,
exclusions, with Wilson intervals on proportions."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def load_games(run_dir: Path) -> list[dict]:
    with open(Path(run_dir) / "games.jsonl") as f:
        return [json.loads(line) for line in f if line.strip()]


def summarize(games: list[dict]) -> pd.DataFrame:
    rows = []
    by_cell: dict[str, list[dict]] = {}
    for g in games:
        by_cell.setdefault(g["cell"]["cell_id"], []).append(g)
    for cell_id, gs in by_cell.items():
        c = gs[0]["cell"]
        llm_players = [p for p in range(2) if c["policies"][p] == "llm"]
        acts, pc, welfare, excl, n_tokens, n_fixed, n_len = [], [], [], 0, [], 0, 0
        for g in gs:
            n_len += sum(bool(g["players"][p].get("truncated")) for p in llm_players)
            if g["excluded"]:
                excl += 1
                continue
            welfare.append(sum(g["payoffs"]))
            for p in llm_players:
                acts.append(g["actions"][p] == "C")
                pc.append(g["players"][p]["p_coop"])
                n_tokens.append(g["players"][p].get("completion_tokens") or 0)
                n_fixed += bool(g["players"][p].get("fixed"))
        k, n = int(sum(acts)), len(acts)
        lo, hi = wilson(k, n)
        rows.append({
            "cell": cell_id, "condition": c["condition"], "level": c["level"], "model": c["model"],
            "games": len(gs), "excluded": excl, "n_decisions": n,
            "coop_rate": k / n if n else float("nan"), "coop_lo": lo, "coop_hi": hi,
            "stated_p_coop": float(np.mean(pc)) if pc else float("nan"),
            "welfare": float(np.mean(welfare)) if welfare else float("nan"),
            "mean_tokens": float(np.mean(n_tokens)) if n_tokens else float("nan"),
            "format_fixed": n_fixed, "truncated": n_len,
        })
    return pd.DataFrame(rows)


def two_proportion_z(k1: int, n1: int, k2: int, n2: int) -> tuple[float, float]:
    p = (k1 + k2) / (n1 + n2)
    se = np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    z = (k1 / n1 - k2 / n2) / se if se > 0 else 0.0
    return z, 2 * (1 - norm.cdf(abs(z)))
