"""D2 (rotating secret) analysis: how much credential replay can an honest population
tolerate before false beards invade?

Reads `runs/d2_secret/games.jsonl` (three cells) and estimates, with symbols as in
docs/variables.md:

  pM    honest cooperation when the partner's code word matches (H–H match cell, 200
        decisions); the H–I match cell gives a second estimate, reported as a harness check;
  pX    honest cooperation when the partner's word does not match (H–I mismatch cell);
  HH    mean honest payoff against an honest partner (H–H match cell, measured);
  HI_M, IH_M   honest and invader payoffs in the H–I match cell (measured);
  HI_X, IH_X   the same in the H–I mismatch cell (measured).

The replay success probability rho (the chance an invader's captured word is still
current) never appears in a prompt. Payoffs against an invader at a given rho are weighted
averages of the two H–I cells:

  HI(rho) = rho HI_M + (1 - rho) HI_X,   IH(rho) = rho IH_M + (1 - rho) IH_X,   II = 1.

Invader advantage g(f) = invader payoff - honest payoff at invader fraction f is linear
in f, with ends g(0) = IH(rho) - HH and g(1) = II - HI(rho) = 1 - HI(rho). g(1) >= 0
always (an honest agent that cooperates at all with a defector earns less than the
defector), so the end states are all-invader (g(0) > 0) or bistable (g(0) < 0) with the
tipping fraction f* = g(0) / (g(0) - g(1)). The headline is rho*, the largest rho at which
g(0) < 0, found on the measured curve and compared with the closed form
rho* = (pM - 2 pX) / (2 (pM - pX)) that follows from the expected payoffs.

All intervals are bootstrap 95% from resampling whole games within each cell.

Usage: .venv/bin/python scripts/d2_analysis.py [--run runs/d2_secret] [--boot 2000]
Writes <run>/analysis.csv (one row per rho on the grid), <run>/cells.csv (the cell
estimates with intervals) and reports/figures/d2_secret.png.
"""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from efa.analysis.metrics import load_games  # noqa: E402

# the preregistered pool sizes k in {1, 4, 16} as replay success rho = 1/k, plus rho = 0
RHO_MARKS = {1.0: "never rotates", 0.25: "k = 4", 0.0625: "k = 16", 0.0: "no replay"}
RHO_GRID = np.unique(np.concatenate([np.round(np.linspace(0.0, 1.0, 101), 4), list(RHO_MARKS)]))
CELLS = {"hh": "secret_match__", "him": "secret_match_vs_always_defect", "hix": "secret_mismatch_vs_always_defect"}


def cell_arrays(games: list[dict], model: str | None = None) -> dict[str, dict[str, np.ndarray]]:
    """Per cell: per-game payoffs of both players and the honest cooperation indicators.
    `model` restricts to cells whose model spec contains it (runs with several models)."""
    out = {k: {"pay": [], "coop": []} for k in CELLS}
    for g in games:
        if g["excluded"] or (model and model not in g["cell"]["model"]):
            continue
        cid = g["cell"]["cell_id"]
        key = next((k for k, tag in CELLS.items() if tag in cid), None)
        if key is None:
            continue
        out[key]["pay"].append(g["payoffs"])
        out[key]["coop"].append([a == "C" for a in g["actions"]])
    arrays = {k: {kk: np.asarray(v, dtype=float) for kk, v in d.items()} for k, d in out.items()}
    for k, d in arrays.items():
        if len(d["pay"]) == 0:
            raise SystemExit(f"no games for cell {CELLS[k]!r}")
    return arrays


def estimates(d: dict[str, dict[str, np.ndarray]], idx: dict[str, np.ndarray] | None = None) -> dict:
    """Point estimates from (optionally resampled) game indices per cell."""
    idx = idx or {k: np.arange(len(d[k]["pay"])) for k in d}
    hh_pay, hh_coop = d["hh"]["pay"][idx["hh"]], d["hh"]["coop"][idx["hh"]]
    him_pay, him_coop = d["him"]["pay"][idx["him"]], d["him"]["coop"][idx["him"]]
    hix_pay, hix_coop = d["hix"]["pay"][idx["hix"]], d["hix"]["coop"][idx["hix"]]
    pM = hh_coop.mean()  # both honest players, 2 decisions per game
    pM_check = him_coop[:, 0].mean()  # the same prompt form against a scripted defector
    pX = hix_coop[:, 0].mean()
    HH = hh_pay.mean()
    HI_M, IH_M = him_pay[:, 0].mean(), him_pay[:, 1].mean()
    HI_X, IH_X = hix_pay[:, 0].mean(), hix_pay[:, 1].mean()
    rho = RHO_GRID
    HI = rho * HI_M + (1 - rho) * HI_X
    IH = rho * IH_M + (1 - rho) * IH_X
    g0 = IH - HH
    g1 = 1.0 - HI
    with np.errstate(divide="ignore", invalid="ignore"):
        f_star = np.where((g0 < 0) & (g1 > 0), g0 / (g0 - g1), np.nan)
    # rho*: the largest replay success with g(0) < 0 on the measured curve (g0 rises with rho).
    # Every rho safe -> 1; no rho safe -> undefined.
    rho_star = 1.0 if g0[-1] < 0 else float("nan") if g0[0] >= 0 else crossing(rho, g0, 0.0)
    rho_star_closed = (pM - 2 * pX) / (2 * (pM - pX)) if pM > 2 * pX else float("nan")
    return dict(pM=pM, pM_check=pM_check, pM_diff=pM_check - pM, pX=pX, HH=HH, HI_M=HI_M, IH_M=IH_M,
                HI_X=HI_X, IH_X=IH_X, rho_star=rho_star, rho_star_closed=rho_star_closed,
                HI=HI, IH=IH, g0=g0, g1=g1, f_star=f_star)


def classify(g0: float, g1: float) -> str:
    if g0 > 0 and g1 > 0:
        return "all-invader"
    if g0 < 0 and g1 < 0:
        return "all-honest"
    return "interior" if g0 > 0 else "bistable"


def crossing(x: np.ndarray, y: np.ndarray, level: float = 0.0) -> float:
    """First x where y crosses `level` by linear interpolation; nan if it never does."""
    for i in range(len(x) - 1):
        a, b = y[i] - level, y[i + 1] - level
        if a == 0:
            return float(x[i])
        if a * b < 0:
            return float(x[i] + (x[i + 1] - x[i]) * a / (a - b))
    return float("nan")


SCALARS = ["pM", "pM_check", "pM_diff", "pX", "HH", "HI_M", "IH_M", "HI_X", "IH_X", "rho_star", "rho_star_closed"]
CURVES = ["HI", "IH", "g0", "g1", "f_star"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, default=Path("runs/d2_secret"))
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--fig", type=Path, default=Path("reports/figures/d2_secret.png"))
    ap.add_argument("--model", default=None, help="substring of the model spec, for multi-model runs")
    ap.add_argument("--title", default="Qwen3.5-27B")
    args = ap.parse_args()

    d = cell_arrays(load_games(args.run), args.model)
    n = {k: len(d[k]["pay"]) for k in d}
    rng = np.random.default_rng(0)
    point = estimates(d)
    boots = [estimates(d, {k: rng.integers(0, n[k], n[k]) for k in d}) for _ in range(args.boot)]

    cells = pd.DataFrame({"estimate": [point[k] for k in SCALARS]}, index=SCALARS)
    for k in SCALARS:
        v = np.array([b[k] for b in boots], dtype=float)
        cells.loc[k, "lo"], cells.loc[k, "hi"] = np.nanpercentile(v, 2.5), np.nanpercentile(v, 97.5)
    cells.loc["rho_star", "frac_undefined"] = np.mean([np.isnan(b["rho_star"]) for b in boots])
    cells["n_games"] = [n["hh"] if k in ("pM", "HH") else n["him"] if k in ("pM_check", "pM_diff", "HI_M", "IH_M")
                        else n["hix"] if k in ("pX", "HI_X", "IH_X") else None for k in SCALARS]

    grid = pd.DataFrame({"rho": RHO_GRID})
    for k in CURVES:
        grid[k] = point[k]
        arr = np.stack([b[k] for b in boots])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)  # f* is undefined outside the bistable range
            grid[f"{k}_lo"], grid[f"{k}_hi"] = np.nanpercentile(arr, 2.5, axis=0), np.nanpercentile(arr, 97.5, axis=0)
    grid["end_state"] = [classify(a, b) for a, b in zip(point["g0"], point["g1"])]
    states = np.array([[classify(a, b) for a, b in zip(bt["g0"], bt["g1"])] for bt in boots])
    for cls in ["all-invader", "bistable", "all-honest", "interior"]:
        grid[f"frac_{cls}"] = (states == cls).mean(axis=0)

    suffix = f"_{args.model}" if args.model else ""
    grid.to_csv(args.run / f"analysis{suffix}.csv", index=False)
    cells.to_csv(args.run / f"cells{suffix}.csv")
    pd.set_option("display.width", 200)
    print(f"games per cell: {n}")
    print(cells.round(3).to_string())
    marks = grid[grid.rho.isin(list(RHO_MARKS))].copy()
    marks["label"] = marks.rho.map(RHO_MARKS)
    print(marks[["rho", "label", "g0", "g0_lo", "g0_hi", "g1", "g1_lo", "g1_hi", "f_star", "end_state",
                 "frac_all-invader", "frac_bistable"]].round(3).to_string(index=False))
    print(f"wrote {args.run / f'analysis{suffix}.csv'} and {args.run / f'cells{suffix}.csv'}")
    make_figure(grid, cells, n, args.fig, args.title)
    print(f"wrote {args.fig}")


def make_figure(grid: pd.DataFrame, cells: pd.DataFrame, n: dict[str, int], out: Path, title: str = "Qwen3.5-27B") -> None:
    blue, orange, aqua, yellow = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
    ink, muted, gridc, surface = "#0b0b0b", "#898781", "#e1e0d9", "#fcfcfb"
    plt.rcParams.update({"font.family": "sans-serif", "axes.edgecolor": muted, "xtick.color": muted,
                         "ytick.color": muted, "axes.labelcolor": ink, "text.color": ink})
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(7, 10.5), sharex=True, facecolor=surface)
    rho = grid.rho.values
    pM, pX = cells.loc["pM", "estimate"], cells.loc["pX", "estimate"]
    rho_star, rs_lo, rs_hi = cells.loc["rho_star", ["estimate", "lo", "hi"]]
    for ax in (ax1, ax2, ax3):
        ax.set_facecolor(surface)
        ax.grid(True, color=gridc, lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
        if np.isfinite(rho_star):
            ax.axvspan(0, rho_star, color=aqua, alpha=0.07, lw=0)
            ax.axvline(rho_star, color=muted, lw=1, ls="--")
        for x in RHO_MARKS:
            ax.axvline(x, color=gridc, lw=0.8)
    ax1.set_xlim(-0.02, 1.02)
    ax1.set_xticks([0, 0.25, 0.5, 0.75, 1])
    ax3.set_xticklabels(["0\nno replay", "0.25", "0.5", "0.75", "1\nnever rotates"], fontsize=8)
    for x, lab in ((0.0625, "1/16"), (0.25, "1/4")):  # the preregistered points
        ax3.annotate(lab, (x, 0), xycoords=("data", "axes fraction"), fontsize=7, color=muted,
                     ha="center", va="bottom", xytext=(0, 2), textcoords="offset points")

    # A. what honest agents do: cooperation with an honest partner (flat) and with an invader (rises with rho)
    coop_inv = rho * pM + (1 - rho) * pX
    ax1.axhspan(cells.loc["pM", "lo"], cells.loc["pM", "hi"], color=blue, alpha=0.12, lw=0)
    ax1.axhline(pM, color=blue, lw=2, label=f"with an honest partner, words match (pM = {pM:.2f})")
    ax1.axhspan(cells.loc["pX", "lo"], cells.loc["pX", "hi"], color=yellow, alpha=0.12, lw=0)
    ax1.axhline(pX, color=yellow, lw=2, label=f"with a partner whose word is wrong (pX = {pX:.2f})")
    ax1.plot(rho, coop_inv, color=orange, lw=2, label="with an invader: ρ·pM + (1 − ρ)·pX")
    ax1.set_ylim(-0.03, 1.03)
    ax1.set_ylabel("honest cooperation rate")
    ax1.set_title("A. How often honest agents cooperate", loc="left", fontsize=11)
    ax1.legend(fontsize=8, frameon=False, loc="center right")

    # B. the payoffs behind the advantage
    HH = cells.loc["HH", "estimate"]
    ax2.axhspan(cells.loc["HH", "lo"], cells.loc["HH", "hi"], color=blue, alpha=0.12, lw=0)
    ax2.axhline(HH, color=blue, lw=2, label="honest vs honest, HH (measured)")
    for key, label, color in (("IH", "invader vs honest, IH(ρ)", aqua), ("HI", "honest vs invader, HI(ρ)", orange)):
        ax2.fill_between(rho, grid[f"{key}_lo"], grid[f"{key}_hi"], color=color, alpha=0.12, lw=0)
        ax2.plot(rho, grid[key], color=color, lw=2, label=label)
    ax2.axhline(1.0, color=muted, lw=1, ls=":")
    ax2.annotate("invader vs invader, II = 1", (0.02, 1.0), fontsize=7.5, color=muted, va="bottom",
                 xytext=(0, 2), textcoords="offset points")
    ax2.set_ylabel("mean payoff per game")
    ax2.set_title("B. The payoffs behind the advantage", loc="left", fontsize=11)
    ax2.legend(fontsize=8, frameon=False, loc="upper left")

    # C. invader advantage at both ends
    ax3.axhline(0, color=muted, lw=1)
    ax3.fill_between(rho, grid.g0_lo, grid.g0_hi, color=blue, alpha=0.15, lw=0)
    ax3.plot(rho, grid.g0, color=blue, lw=2, label="rare invader, g(0) = IH(ρ) − HH")
    ax3.fill_between(rho, grid.g1_lo, grid.g1_hi, color=orange, alpha=0.15, lw=0)
    ax3.plot(rho, grid.g1, color=orange, lw=2, label="common invader, g(1) = 1 − HI(ρ)")
    ax3.set_ylabel("invader payoff − honest payoff")
    ax3.set_xlabel("replay success probability ρ (chance an invader's captured word is still current)")
    ax3.set_title("C. Invader advantage (rare invader below zero = honest population holds)", loc="left", fontsize=11)
    ax3.legend(fontsize=8, frameon=False, loc="upper left")
    if np.isfinite(rho_star):
        ax1.annotate(f"ρ* = {rho_star:.2f}\n(95% {rs_lo:.2f}–{rs_hi:.2f})\nhonest population\nholds to the left",
                     (rho_star, 1.0), fontsize=7.5, color=muted, ha="left", va="top", xytext=(4, 0), textcoords="offset points")
    else:
        ax1.annotate("no ρ* : invaders win at every ρ", (0.5, 1.0), fontsize=8, color=muted, ha="center", va="top")
    fig.suptitle(f"D2: a rotating code word, {title}, N = {n['hh']} / {n['him']} / {n['hix']} games per cell",
                 fontsize=10, color=muted, x=0.02, ha="left")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, facecolor=surface)
    plt.close(fig)


if __name__ == "__main__":
    main()
