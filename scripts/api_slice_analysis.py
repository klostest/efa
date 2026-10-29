"""Frontier-model validation slice: the headline numbers per model, side by side with the
local Qwen results, for the cells in configs/api_slice.yaml.

Per model (symbols as in docs/variables.md):
  base         cooperation with no twist (control)
  C2           honest cooperation with the claim (H–H), honest cooperation against the
               invader (H–I), HH, HI, IH = 1 + 2·(H–I cooperation), g(0) = IH − HH,
               g(1) = 1 − HI, and the bootstrap fraction of resamples ending all-invader
  D2           pM, pX, rho* and the end state at the marked rho (via scripts/d2_analysis)
  D1 H–I       honest report rate r and cooperation against the reporting invader pR at
               c = 0.5 and c = 2; the "paying more buys no more trust" check is pR(2) − pR(0.5)

Usage: .venv/bin/python scripts/api_slice_analysis.py [--run runs/api_slice] [--boot 2000]
Writes <run>/headline.csv; D2 figures go to reports/figures/d2_secret_<model>.png.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from efa.analysis.metrics import load_games, wilson

QWEN = {  # local results for the same cells (research log, 2026-10-22 to 2026-10-29)
    "base": 0.00, "c2_hh_coop": 0.87, "c2_hi_coop": 0.85, "HH": 1.87, "HI": 0.15, "IH": 2.70,
    "g0": 0.83, "d1_r_0.5": 0.66, "d1_pR_0.5": 0.75, "d1_r_2": 0.19, "d1_pR_2": 0.73,
}


def by_cell(games: list[dict], model: str) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for g in games:
        if model in g["cell"]["model"] and not g["excluded"]:
            out.setdefault(g["cell"]["cell_id"].split("__")[0], []).append(g)
    return out


def coop(gs: list[dict], players=(0, 1)) -> tuple[float, int, int]:
    k = sum(g["actions"][p] == "C" for g in gs for p in players)
    n = len(gs) * len(players)
    return (k / n if n else float("nan")), k, n


def c2_numbers(hh: list[dict], hi: list[dict], boot: int, rng: np.random.Generator) -> dict:
    hh_pay = np.array([g["payoffs"] for g in hh], dtype=float)
    hi_pay = np.array([g["payoffs"] for g in hi], dtype=float)

    def est(ih, ii):
        HH = hh_pay[ih].mean()
        HI, IH = hi_pay[ii, 0].mean(), hi_pay[ii, 1].mean()
        return HH, HI, IH, IH - HH, 1 - HI

    HH, HI, IH, g0, g1 = est(np.arange(len(hh)), np.arange(len(hi)))
    b = np.array([est(rng.integers(0, len(hh), len(hh)), rng.integers(0, len(hi), len(hi))) for _ in range(boot)])
    return dict(HH=HH, HI=HI, IH=IH, g0=g0, g0_lo=np.percentile(b[:, 3], 2.5), g0_hi=np.percentile(b[:, 3], 97.5),
                g1=g1, frac_all_invader=float(np.mean((b[:, 3] > 0) & (b[:, 4] > 0))))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, default=Path("runs/api_slice"))
    ap.add_argument("--boot", type=int, default=2000)
    args = ap.parse_args()
    games = load_games(args.run)
    models = sorted({g["cell"]["model"] for g in games})
    rng = np.random.default_rng(0)
    rows = {"Qwen3.5-27B (local)": QWEN}
    for spec in models:
        short = spec.split(":")[-1]
        cells = by_cell(games, spec)
        row: dict[str, float] = {}
        if "base" in cells:
            row["base"], k, n = coop(cells["base"])
            row["base_lo"], row["base_hi"] = wilson(k, n)
        hh, hi = cells.get("claim_symmetric_100"), cells.get("claim_symmetric_100_vs_always_defect")
        if hh and hi:
            row["c2_hh_coop"], k, n = coop(hh)
            row["c2_hh_lo"], row["c2_hh_hi"] = wilson(k, n)
            row["c2_hi_coop"], k, n = coop(hi, (0,))
            row["c2_hi_lo"], row["c2_hi_hi"] = wilson(k, n)
            row |= c2_numbers(hh, hi, args.boot, rng)
        for c in ("0.5", "2"):
            d1 = cells.get(f"costly_claim_c{c}_vs_always_defect")
            if d1:
                claims = [bool(g["claims"][0]) for g in d1]
                row[f"d1_r_{c}"] = float(np.mean(claims))
                row[f"d1_pR_{c}"], k, n = coop(d1, (0,))
                row[f"d1_pR_{c}_lo"], row[f"d1_pR_{c}_hi"] = wilson(k, n)
        if "secret_match" in cells and "secret_mismatch_vs_always_defect" in cells:
            out = subprocess.run([sys.executable, "scripts/d2_analysis.py", "--run", str(args.run), "--model", short,
                                  "--boot", str(args.boot), "--fig", f"reports/figures/d2_secret_{short}.png",
                                  "--title", short], capture_output=True, text=True, check=True)
            cells_csv = pd.read_csv(args.run / f"cells_{short}.csv", index_col=0)
            for key in ("pM", "pX", "rho_star"):
                row[f"d2_{key}"] = cells_csv.loc[key, "estimate"]
                row[f"d2_{key}_lo"], row[f"d2_{key}_hi"] = cells_csv.loc[key, "lo"], cells_csv.loc[key, "hi"]
            print(out.stdout)
        rows[short] = row
    df = pd.DataFrame(rows).T
    pd.set_option("display.width", 250)
    head = [c for c in ["base", "c2_hh_coop", "c2_hi_coop", "HH", "HI", "IH", "g0", "g0_lo", "g0_hi", "g1",
                        "frac_all_invader", "d1_r_0.5", "d1_pR_0.5", "d1_r_2", "d1_pR_2",
                        "d2_pM", "d2_pX", "d2_rho_star", "d2_rho_star_lo", "d2_rho_star_hi"] if c in df.columns]
    print(df[head].astype(float).round(3).to_string())
    df.to_csv(args.run / "headline.csv")
    print(f"wrote {args.run / 'headline.csv'}")


if __name__ == "__main__":
    main()
