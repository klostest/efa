"""D1 (costly claim) analysis: does a flat cost on the similarity claim stop false beards?

Reads `runs/d1_costly_claim/games.jsonl` and, for each cost level c, estimates:

* the honest report rate, and honest cooperation against a reporting partner (pR) and
  against a non-reporting partner (pN), each averaged over the honest agent's own report;
* the invader's break-even cost c_I(c) = 2 (pR - pN): a report turns a defecting partner's
  1 point into 3 for every extra cooperator it buys, so it pays at low invader frequency
  only while c < c_I;
* the invader advantage g(f) = invader payoff - honest payoff at invader frequency f,
  under the rational-invader rule (the invader type reports only when that pays at that f),
  at the two ends f -> 0 and f -> 1, with bootstrap intervals over games;
* the replicator end state. With two types the dynamics are one-dimensional, so the end
  state follows from the sign of g over f: positive everywhere -> all-invader, negative
  everywhere -> all-honest, + then - -> a stable interior mix at the crossing f*, - then +
  -> bistable. The fraction of bootstrap resamples in each class is reported.

Payoffs are net of the claim cost. Measured quantities, per c:
  HH    mean honest net payoff per player in the honest-honest cell;
  HI_R  mean honest net payoff in the honest-invader cell (the scripted invader reports);
  pR    honest cooperation in the honest-invader cell (partner reported);
  pN    honest cooperation in honest-honest games whose partner did not report, as the
        mixture over the honest agent's own report (prompts depend only on the two reports,
        not on the partner's type, so this is also honest play against a silent invader);
  r     honest report rate.
Derived: invader vs honest, reporting: 1 + 2 pR - c; silent: 1 + 2 pN.
         honest vs silent invader: (1 - pN) - c r.   invader vs invader: 1 - c if both report, else 1.

Usage: .venv/bin/python scripts/d1_analysis.py [--run runs/d1_costly_claim] [--boot 2000]
Writes <run>/analysis.csv and reports/figures/d1_costly_claim.png.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from efa.analysis.metrics import load_games, wilson  # noqa: E402

F_GRID = np.linspace(0.0, 1.0, 101)


def cell_arrays(games: list[dict]) -> dict[float, dict[str, np.ndarray]]:
    """Per c: per-game arrays for the H–H cell (honest payoffs, reports, actions of both
    players) and the H–I cell (honest payoff, report, action)."""
    out: dict[float, dict[str, list]] = {}
    for g in games:
        if g["excluded"]:
            continue
        c = float(g["cell"]["cost"])
        d = out.setdefault(c, {"hh_pay": [], "hh_rep": [], "hh_coop": [], "hi_pay": [], "hi_rep": [], "hi_coop": []})
        if "always_defect" in g["cell"]["cell_id"]:
            d["hi_pay"].append(g["payoffs"][0])
            d["hi_rep"].append(bool(g["claims"][0]))
            d["hi_coop"].append(g["actions"][0] == "C")
        else:
            d["hh_pay"].append(g["payoffs"])
            d["hh_rep"].append([bool(x) for x in g["claims"]])
            d["hh_coop"].append([a == "C" for a in g["actions"]])
    return {c: {k: np.asarray(v) for k, v in d.items()} for c, d in out.items()}


def estimates(c: float, d: dict[str, np.ndarray], ih: np.ndarray | None = None, ii: np.ndarray | None = None) -> dict:
    """Point estimates for one cost level from (optionally resampled) game indices."""
    ih = np.arange(len(d["hh_pay"])) if ih is None else ih
    ii = np.arange(len(d["hi_pay"])) if ii is None else ii
    hh_pay, hh_rep, hh_coop = d["hh_pay"][ih], d["hh_rep"][ih], d["hh_coop"][ih]
    hi_pay, hi_rep, hi_coop = d["hi_pay"][ii], d["hi_rep"][ii], d["hi_coop"][ii]
    HH = hh_pay.mean()
    r = np.concatenate([hh_rep.ravel(), hi_rep]).mean()
    pR = hi_coop.mean()
    HI_R = hi_pay.mean()
    # honest play when the partner did not report, by the agent's own report (H–H games)
    partner_silent = ~hh_rep[:, ::-1]
    own_rep = hh_rep
    sel_rr = partner_silent & own_rep
    sel_nn = partner_silent & ~own_rep
    p_rn = hh_coop[sel_rr].mean() if sel_rr.any() else np.nan  # own report, partner silent
    p_nn = hh_coop[sel_nn].mean() if sel_nn.any() else np.nan  # neither reported
    if np.isnan(p_rn):
        p_rn = p_nn
    if np.isnan(p_nn):
        p_nn = p_rn
    pN = r * p_rn + (1 - r) * p_nn
    HI_N = (1 - pN) - c * r
    IH_R, IH_N = 1 + 2 * pR - c, 1 + 2 * pN
    c_I = 2 * (pR - pN)
    # payoffs along f under the rational rule: report iff 2 (1 - f)(pR - pN) > c
    f = F_GRID
    inv_R = (1 - f) * IH_R + f * (1 - c)
    inv_N = (1 - f) * IH_N + f * 1.0
    reports = inv_R > inv_N
    inv = np.where(reports, inv_R, inv_N)
    hon = (1 - f) * HH + f * np.where(reports, HI_R, HI_N)
    g = inv - hon
    g_scripted = inv_R - ((1 - f) * HH + f * HI_R)  # always-report invader, for comparison
    return dict(c=c, HH=HH, r=r, pR=pR, pN=pN, p_rn=p_rn, p_nn=p_nn, HI_R=HI_R, HI_N=HI_N,
                IH_R=IH_R, IH_N=IH_N, c_I=c_I, invader_reports_f0=bool(reports[0]),
                g0=g[0], g1=g[-1], g0_scripted=g_scripted[0], g1_scripted=g_scripted[-1],
                end_state=classify(g))


def classify(g: np.ndarray) -> str:
    if (g > 0).all():
        return "all-invader"
    if (g < 0).all():
        return "all-honest"
    return "interior" if g[0] > 0 else "bistable"


def crossing(x: np.ndarray, y: np.ndarray, level: float = 0.0) -> float:
    """First x where y crosses `level` by linear interpolation; nan if it never does."""
    for i in range(len(x) - 1):
        a, b = y[i] - level, y[i + 1] - level
        if a == 0:
            return float(x[i])
        if a * b < 0:
            return float(x[i] + (x[i + 1] - x[i]) * a / (a - b))
    return float("nan")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, default=Path("runs/d1_costly_claim"))
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--fig", type=Path, default=Path("reports/figures/d1_costly_claim.png"))
    args = ap.parse_args()

    data = cell_arrays(load_games(args.run))
    costs = sorted(data)
    rng = np.random.default_rng(0)
    rows, boots = [], {c: [] for c in costs}
    for c in costs:
        d = data[c]
        rows.append(estimates(c, d))
        nh, ni = len(d["hh_pay"]), len(d["hi_pay"])
        for _ in range(args.boot):
            boots[c].append(estimates(c, d, rng.integers(0, nh, nh), rng.integers(0, ni, ni)))
    df = pd.DataFrame(rows).set_index("c")
    for key in ["g0", "g1", "c_I", "r", "pR", "pN", "HH", "HI_R", "IH_R", "IH_N"]:
        lo, hi = [], []
        for c in costs:
            v = np.array([b[key] for b in boots[c]], dtype=float)
            lo.append(np.nanpercentile(v, 2.5))
            hi.append(np.nanpercentile(v, 97.5))
        df[f"{key}_lo"], df[f"{key}_hi"] = lo, hi
    for cls in ["all-invader", "all-honest", "interior", "bistable"]:
        df[f"frac_{cls}"] = [np.mean([b["end_state"] == cls for b in boots[c]]) for c in costs]
    # Wilson intervals on the report rate (exact counts)
    for c in costs:
        d = data[c]
        reps = np.concatenate([d["hh_rep"].ravel(), d["hi_rep"]])
        df.loc[c, "r_wilson_lo"], df.loc[c, "r_wilson_hi"] = wilson(int(reps.sum()), len(reps))

    # the two crossings in c: honest report rate through 0.5, and the invader break-even c_I(c) = c
    cs = np.array(costs)
    c_half = crossing(cs, df.r.values, 0.5)
    c_break = crossing(cs, df.c_I.values - cs, 0.0)
    boot_half = [crossing(cs, np.array([boots[c][b]["r"] for c in costs]), 0.5) for b in range(args.boot)]
    boot_break = [crossing(cs, np.array([boots[c][b]["c_I"] for c in costs]) - cs, 0.0) for b in range(args.boot)]
    summary = {
        "c_half (honest report rate = 0.5)": (c_half, np.nanpercentile(boot_half, [2.5, 97.5])),
        "c_break (invader report stops paying, f -> 0)": (c_break, np.nanpercentile(boot_break, [2.5, 97.5])),
    }

    out_csv = args.run / "analysis.csv"
    df.to_csv(out_csv)
    pd.set_option("display.width", 200)
    print(df[["r", "r_wilson_lo", "r_wilson_hi", "pR", "pN", "HH", "HI_R", "IH_R", "IH_N", "c_I",
              "invader_reports_f0", "g0", "g0_lo", "g0_hi", "g1", "g1_lo", "g1_hi",
              "g0_scripted", "frac_all-invader", "frac_interior"]].round(3).to_string())
    for k, (v, ci) in summary.items():
        print(f"{k}: {v:.2f}  (bootstrap 95% {ci[0]:.2f}–{ci[1]:.2f})")
    print(f"wrote {out_csv}")
    make_figure(df, cs, c_half, c_break, args.fig)
    print(f"wrote {args.fig}")


def make_figure(df: pd.DataFrame, cs: np.ndarray, c_half: float, c_break: float, out: Path) -> None:
    blue, orange, aqua, yellow = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
    ink, muted, grid, surface = "#0b0b0b", "#898781", "#e1e0d9", "#fcfcfb"
    plt.rcParams.update({"font.family": "sans-serif", "axes.edgecolor": muted, "xtick.color": muted,
                         "ytick.color": muted, "axes.labelcolor": ink, "text.color": ink})
    fig, (ax1, ax3, ax2) = plt.subplots(3, 1, figsize=(7, 10.5), sharex=True, facecolor=surface)
    for ax in (ax1, ax2, ax3):
        ax.set_facecolor(surface)
        ax.grid(True, color=grid, lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_xticks(cs)

    ax1.errorbar(cs, df.r, yerr=[df.r - df.r_wilson_lo, df.r_wilson_hi - df.r], color=blue, lw=2,
                 marker="o", ms=6, capsize=3, label="honest report rate")
    ax1.errorbar(cs, df.pR, yerr=[df.pR - df.pR_lo, df.pR_hi - df.pR], color=orange, lw=2,
                 marker="s", ms=6, capsize=3, label="honest cooperation, partner reported")
    ax1.errorbar(cs, df.pN, yerr=[df.pN - df.pN_lo, df.pN_hi - df.pN], color=aqua, lw=2,
                 marker="^", ms=6, capsize=3, label="honest cooperation, partner silent")
    ax1.set_ylim(-0.03, 1.03)
    ax1.set_ylabel("rate")
    ax1.set_title("A. What honest agents do at each claim cost", loc="left", fontsize=11)
    ax1.legend(fontsize=8, frameon=False, loc="center right")

    # panel C (drawn between A and B): the payoffs the advantage is built from
    series = [("HH", "honest vs honest (measured)", blue, "o"),
              ("HI_R", "honest vs reporting invader (measured)", orange, "s"),
              ("IH_R", "invader vs honest, invader reports (1 + 2pR − c)", aqua, "^"),
              ("IH_N", "invader vs honest, invader silent (1 + 2pN)", yellow, "D")]
    for key, label, color, mk in series:
        ax3.fill_between(cs, df[f"{key}_lo"], df[f"{key}_hi"], color=color, alpha=0.12, lw=0)
        ax3.plot(cs, df[key], color=color, lw=2, marker=mk, ms=6, label=label)
        ax3.annotate(key.replace("_R", " (reports)").replace("_N", " (silent)"), (cs[-1], df[key].iloc[-1]),
                     fontsize=7.5, color=ink, xytext=(5, 0), textcoords="offset points", va="center")
    ax3.axhline(1.0, color=muted, lw=1, ls=":")
    ax3.annotate("mutual defection, no fees = 1", (0.02, 1.0), fontsize=7.5, color=muted, va="bottom", xytext=(0, 2), textcoords="offset points")
    ax3.set_ylabel("mean net payoff per game")
    ax3.set_title("B. The payoffs behind the advantage (rare invader: its better option − HH)", loc="left", fontsize=11)
    ax3.legend(fontsize=8, frameon=False, loc="upper right")
    ax3.set_xlim(-0.08, 2.35)

    ax2.axhline(0, color=muted, lw=1)
    ax2.fill_between(cs, df.g0_lo, df.g0_hi, color=blue, alpha=0.15, lw=0)
    ax2.plot(cs, df.g0, color=blue, lw=2, marker="o", ms=6, label="rare invader (f → 0)")
    ax2.fill_between(cs, df.g1_lo, df.g1_hi, color=orange, alpha=0.15, lw=0)
    ax2.plot(cs, df.g1, color=orange, lw=2, marker="s", ms=6, label="common invader (f → 1)")
    ax2.plot(cs, df.g0_scripted, color=blue, lw=1.2, ls=":", marker=None, label="rare invader if it always reports")
    ax2.set_ylabel("invader payoff − honest payoff")
    ax2.set_xlabel("claim cost c (points)")
    ax2.set_title("C. Invader advantage (positive = invaders spread)", loc="left", fontsize=11)
    ax2.legend(fontsize=8, frameon=False, loc="upper right")
    for ax in (ax1, ax2, ax3):
        for x, lab in ((c_half, "honest reporting\nhalved"), (c_break, "invader report\nstops paying")):
            if np.isfinite(x):
                ax.axvline(x, color=muted, lw=1, ls="--")
        if ax is ax1:
            ax.annotate("honest reporting\nhalved", (c_half, 1.0), fontsize=7.5, color=muted, ha="right", va="top", xytext=(-3, 0), textcoords="offset points")
            ax.annotate("invader report\nstops paying", (c_break, 1.0), fontsize=7.5, color=muted, ha="left", va="top", xytext=(3, 0), textcoords="offset points")
    fig.suptitle("D1: a flat cost on the similarity claim, Qwen3.5-27B, N = 100 games per cell", fontsize=10, color=muted, x=0.02, ha="left")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, facecolor=surface)
    plt.close(fig)


if __name__ == "__main__":
    main()
