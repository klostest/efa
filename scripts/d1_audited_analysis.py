"""D1-audited (H3c) analysis: does a stake that only a defecting reporter forfeits price
the invader out, and does the honest population then hold?

Reads `runs/d1_audited/games.jsonl` (one stake a, report cost c = 0) and estimates:

* r      honest report rate (all honest decisions, both cells);
* p_RR   honest cooperation when the agent reported and its partner reported, from the
         honest-invader cell (the scripted invader always reports); the same rate among
         both-reported honest-honest games is printed as a harness check;
* p_NR   honest cooperation when the agent stayed silent and its partner reported;
* pN     honest cooperation when the partner stayed silent, from honest-honest games, as
         the mixture over the agent's own report (D1's definition; the prompt depends only
         on the two reports, so this is also honest play against a silent invader);
* HH     mean honest net payoff per player in the honest-honest cell (forfeits included);
* HI_R, IH_R  honest and invader net payoff in the honest-invader cell, measured
         (the invader forfeits a whenever the honest agent reported, since it defects);
* IH_N = 1 + 2 pN and HI_N = 1 - pN, the silent-invader pair (no report, no forfeit);
* the invader advantage g(f) under the rational-invader rule (report iff it pays at that
  f, with invader-invader pairs at 1 - a when reporting and 1 when silent), at f -> 0 and
  f -> 1, the replicator end state and the tipping fraction f*, with bootstrap intervals.

The report's worth to the invader, 2 (p_RR - pN), is bounded by 2, so at a = 2 the
rational invader is silent by construction; what the arm measures is whether the honest
population holds against the silent invader: g(0) = (1 + 2 pN) - HH.

For comparison the same quantities are computed for D1's c = 0 and c = 2 cells
(`runs/d1_costly_claim`), with D1's honest-invader cooperation split by the agent's own
report so p_RR is comparable.

Usage: .venv/bin/python scripts/d1_audited_analysis.py [--run runs/d1_audited]
       [--d1 runs/d1_costly_claim] [--boot 2000] [--model <substring>] [--title "Qwen3.5-27B"]
Writes <run>/analysis[_<model>].csv, <run>/comparison[_<model>].csv and
reports/figures/d1_audited[_<model>].png.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from d1_analysis import F_GRID, band, classify, crossing  # noqa: E402

from efa.analysis.metrics import load_games, wilson  # noqa: E402


def cell_arrays(games: list[dict], model: str | None = None) -> tuple[float, float, dict[str, np.ndarray]]:
    """(c, a, arrays): per-game arrays for the H–H cell (both players' net payoffs, reports,
    actions) and the H–I cell (honest net payoff, report, action; invader net payoff)."""
    d: dict[str, list] = {"hh_pay": [], "hh_rep": [], "hh_coop": [],
                          "hi_pay": [], "hi_rep": [], "hi_coop": [], "hi_inv_pay": []}
    cs, stakes = set(), set()
    for g in games:
        if g["excluded"] or (model and model not in g["cell"]["model"]):
            continue
        cs.add(float(g["cell"]["cost"]))
        stakes.add(float(g["cell"].get("stake") or 0.0))
        if "always_defect" in g["cell"]["cell_id"]:
            d["hi_pay"].append(g["payoffs"][0])
            d["hi_inv_pay"].append(g["payoffs"][1])
            d["hi_rep"].append(bool(g["claims"][0]))
            d["hi_coop"].append(g["actions"][0] == "C")
        else:
            d["hh_pay"].append(g["payoffs"])
            d["hh_rep"].append([bool(x) for x in g["claims"]])
            d["hh_coop"].append([a == "C" for a in g["actions"]])
    if len(cs) != 1 or len(stakes) != 1:
        raise ValueError(f"expected one cost and one stake, got costs {cs} and stakes {stakes}")
    return cs.pop(), stakes.pop(), {k: np.asarray(v) for k, v in d.items()}


def estimates(c: float, a: float, d: dict[str, np.ndarray],
              ih: np.ndarray | None = None, ii: np.ndarray | None = None) -> dict:
    """Point estimates from (optionally resampled) game indices. `a` is the stake (0 for a
    plain D1 cell); `c` the up-front report cost (0 in the audited arm)."""
    ih = np.arange(len(d["hh_pay"])) if ih is None else ih
    ii = np.arange(len(d["hi_pay"])) if ii is None else ii
    hh_pay, hh_rep, hh_coop = d["hh_pay"][ih], d["hh_rep"][ih], d["hh_coop"][ih]
    hi_pay, hi_rep, hi_coop, hi_inv = d["hi_pay"][ii], d["hi_rep"][ii], d["hi_coop"][ii], d["hi_inv_pay"][ii]
    HH = hh_pay.mean()
    r = np.concatenate([hh_rep.ravel(), hi_rep]).mean()
    p_RR = hi_coop[hi_rep].mean() if hi_rep.any() else np.nan
    p_NR = hi_coop[~hi_rep].mean() if (~hi_rep).any() else np.nan
    both = hh_rep & hh_rep[:, ::-1]
    p_RR_hh = hh_coop[both].mean() if both.any() else np.nan  # harness check: same prompt as the H–I split
    # honest play when the partner did not report, by the agent's own report (H–H games)
    partner_silent = ~hh_rep[:, ::-1]
    sel_rn, sel_nn = partner_silent & hh_rep, partner_silent & ~hh_rep
    p_rn = hh_coop[sel_rn].mean() if sel_rn.any() else np.nan
    p_nn = hh_coop[sel_nn].mean() if sel_nn.any() else np.nan
    if np.isnan(p_rn):
        p_rn = p_nn
    if np.isnan(p_nn):
        p_nn = p_rn
    pN = r * p_rn + (1 - r) * p_nn
    HI_R, IH_R = hi_pay.mean(), hi_inv.mean()  # measured, forfeits and costs included
    IH_N = 1 + 2 * pN
    HI_N = (1 - pN) - c * r
    report_worth = 2 * (p_RR - pN) if not np.isnan(p_RR) else np.nan  # what a report buys the invader, before costs
    f = F_GRID
    inv_R = (1 - f) * IH_R + f * (1 - a - c)
    inv_N = (1 - f) * IH_N + f * 1.0
    if np.isnan(pN):
        reports = np.ones_like(f, dtype=bool)  # silent option unobserved: scored as reporting
    else:
        reports = inv_R > inv_N
    inv = np.where(reports, inv_R, inv_N)
    hon = (1 - f) * HH + f * np.where(reports, HI_R, HI_N)
    g = inv - hon
    end = classify(g)
    f_star = crossing(f, g) if end == "bistable" else np.nan
    return dict(c=c, a=a, HH=HH, r=r, p_RR=p_RR, p_RR_hh=p_RR_hh, p_NR=p_NR, pN=pN, p_rn=p_rn, p_nn=p_nn,
                HI_R=HI_R, HI_N=HI_N, IH_R=IH_R, IH_N=IH_N, report_worth=report_worth,
                invader_reports_f0=bool(reports[0]), g0=g[0], g1=g[-1], end_state=end, f_star=f_star)


KEYS = ["g0", "g1", "r", "p_RR", "p_NR", "pN", "HH", "HI_R", "HI_N", "IH_R", "IH_N", "report_worth", "f_star"]


def analyse(label: str, c: float, a: float, d: dict[str, np.ndarray], boot: int, rng: np.random.Generator) -> dict:
    row = estimates(c, a, d)
    row["label"] = label
    nh, ni = len(d["hh_pay"]), len(d["hi_pay"])
    boots = [estimates(c, a, d, rng.integers(0, nh, nh), rng.integers(0, ni, ni)) for _ in range(boot)]
    for key in KEYS:
        v = np.array([b[key] for b in boots], dtype=float)
        row[f"{key}_lo"], row[f"{key}_hi"] = np.nanpercentile(v, 2.5), np.nanpercentile(v, 97.5)
    for cls in ["all-invader", "all-honest", "interior", "bistable", "neutral"]:
        row[f"frac_{cls}"] = np.mean([b["end_state"] == cls for b in boots])
    reps = np.concatenate([d["hh_rep"].ravel(), d["hi_rep"]])
    row["r_wilson_lo"], row["r_wilson_hi"] = wilson(int(reps.sum()), len(reps))
    sel = d["hi_rep"]
    row["p_RR_wilson_lo"], row["p_RR_wilson_hi"] = wilson(int(d["hi_coop"][sel].sum()), int(sel.sum()))
    row["n_hh"], row["n_hi"] = nh, ni
    return row


def d1_arrays(games: list[dict], c: float, model: str | None) -> dict[str, np.ndarray]:
    """The D1 cells at one cost, in this script's array layout (invader net payoff included)."""
    sub = [g for g in games if float(g["cell"]["cost"]) == c and not g["cell"].get("claim_only")]
    _, _, d = cell_arrays([dict(g, cell=dict(g["cell"], stake=0.0)) for g in sub], model)
    return d


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, default=Path("runs/d1_audited"))
    ap.add_argument("--d1", type=Path, default=Path("runs/d1_costly_claim"), help="D1 run for the comparison rows; '' to skip")
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--fig", type=Path, default=None)
    ap.add_argument("--model", default=None, help="keep one model's cells (substring of the model spec)")
    ap.add_argument("--title", default="Qwen3.5-27B")
    args = ap.parse_args()
    suffix = f"_{args.model}" if args.model else ""
    fig_path = args.fig or Path(f"reports/figures/d1_audited{suffix}.png")
    rng = np.random.default_rng(0)

    c, a, d = cell_arrays(load_games(args.run), args.model)
    rows = [analyse(f"audited, a = {a:g}", c, a, d, args.boot, rng)]
    if str(args.d1):
        d1 = load_games(args.d1)
        for c1 in (0.0, 2.0):
            try:
                rows.insert(len(rows) - 1, analyse(f"D1, c = {c1:g}", c1, 0.0, d1_arrays(d1, c1, args.model), args.boot, rng))
            except (ValueError, KeyError) as e:
                print(f"D1 c = {c1:g} skipped: {e}")
    df = pd.DataFrame(rows).set_index("label")
    df.to_csv(args.run / f"comparison{suffix}.csv")
    df.loc[[f"audited, a = {a:g}"]].to_csv(args.run / f"analysis{suffix}.csv")
    pd.set_option("display.width", 220)
    print(df[["n_hh", "n_hi", "r", "r_wilson_lo", "r_wilson_hi", "p_RR", "p_RR_hh", "p_NR", "pN", "HH",
              "HI_R", "IH_R", "IH_N", "report_worth", "invader_reports_f0",
              "g0", "g0_lo", "g0_hi", "g1", "g1_lo", "g1_hi", "f_star", "end_state",
              "frac_bistable", "frac_all-invader", "frac_all-honest", "frac_interior"]].round(3).T.to_string())
    print(f"wrote {args.run / f'comparison{suffix}.csv'} and {args.run / f'analysis{suffix}.csv'}")
    make_figure(df, fig_path, args.title)
    print(f"wrote {fig_path}")


def make_figure(df: pd.DataFrame, out: Path, title: str) -> None:
    blue, orange, aqua = "#2a78d6", "#eb6834", "#1baf7a"
    ink, muted, grid, surface = "#0b0b0b", "#898781", "#e1e0d9", "#fcfcfb"
    plt.rcParams.update({"font.family": "sans-serif", "axes.edgecolor": muted, "xtick.color": muted,
                         "ytick.color": muted, "axes.labelcolor": ink, "text.color": ink})
    labels = list(df.index)
    x = np.arange(len(labels))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.4), facecolor=surface)
    for ax in (ax1, ax2):
        ax.set_facecolor(surface)
        ax.grid(True, axis="y", color=grid, lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_xlim(-0.5, len(labels) - 0.5)

    series = [("r", "honest report rate", blue, "o", -0.18),
              ("p_RR", "honest cooperation, both reported", orange, "s", 0.0),
              ("pN", "honest cooperation, partner silent", aqua, "^", 0.18)]
    for key, label, color, mk, dx in series:
        lo = df[f"{key}_wilson_lo"] if f"{key}_wilson_lo" in df else df[f"{key}_lo"]
        hi = df[f"{key}_wilson_hi"] if f"{key}_wilson_hi" in df else df[f"{key}_hi"]
        ax1.errorbar(x + dx, df[key], yerr=band(df[key], lo, hi), color=color, lw=0, elinewidth=2,
                     marker=mk, ms=8, capsize=3, label=label)
    ax1.set_ylim(-0.03, 1.03)
    ax1.set_ylabel("rate")
    ax1.set_title("A. What honest agents do", loc="left", fontsize=11)
    ax1.legend(fontsize=8, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=1)

    ax2.axhline(0, color=muted, lw=1)
    for key, label, color, mk, dx in (("g0", "rare invader (f → 0)", blue, "o", -0.12),
                                      ("g1", "common invader (f → 1)", orange, "s", 0.12)):
        ax2.errorbar(x + dx, df[key], yerr=band(df[key], df[f"{key}_lo"], df[f"{key}_hi"]), color=color, lw=0,
                     elinewidth=2, marker=mk, ms=8, capsize=3, label=label)
    ax2.set_ylim(min(ax2.get_ylim()[0], -0.2), max(ax2.get_ylim()[1], 1.2) + 0.15)
    for i, lab in enumerate(labels):
        ax2.annotate("end state: " + df.loc[lab, "end_state"], (i, ax2.get_ylim()[1]), fontsize=8, color=muted,
                     ha="center", va="top", xytext=(0, -2), textcoords="offset points")
    ax2.set_ylabel("invader payoff − honest payoff")
    ax2.set_title("B. Invader advantage (positive = invaders spread)", loc="left", fontsize=11)
    ax2.legend(fontsize=8, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2)
    fig.suptitle(f"A stake only a defecting reporter forfeits, against D1's flat cost ({title})", fontsize=11, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=160, facecolor=surface)
    plt.close(fig)


if __name__ == "__main__":
    main()
