"""Figures for the hackathon report, drawn from the existing analysis CSVs with the report's terms.

Labels only: every plotted number is read from an analysis file written by the analysis
scripts (scripts/d1_analysis.py, d1_audited_analysis.py, d2_analysis.py); nothing is
re-estimated here. Terms follow hackathon/outline.md, "Terms": the plotted quantity is the
payoff advantage of a rare false beard (g(0) in the analysis files).

Figure 1 (RQ3 with RQ4): payoff advantage of a rare false beard against the flat claim cost,
one panel per model, with the audited claim (free claim, stake 2) as a reference line.
Figure 2 (RQ5): payoff advantage of a rare false beard against replay success, one panel per
model, with the threshold below which the honest population holds.

Qwen values come from the event reruns (hackathon/runs/event); a cost level the event run has
not reached yet falls back to the pre-event run and is drawn as a hollow marker. Sonnet and
Opus come from runs/api_d1 and runs/api_slice (pre-event) and hackathon/runs/api_d1_audited.

Usage: .venv/bin/python hackathon/scripts/report_figures.py
Writes hackathon/figures/report_fig1_cost_vs_audit.png and report_fig2_rotating_secret.png.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = ROOT / "hackathon/figures"

BLUE, ORANGE = "#2a78d6", "#eb6834"  # validated pair (dataviz validate_palette.js, light surface)
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#6b6963", "#e1e0d9", "#ffffff"

MODELS = [("qwen", "Qwen3.5-27B"), ("claude-sonnet-5-5", "Claude Sonnet 5.5"), ("claude-opus-5-5", "Claude Opus 5.5")]


def style() -> None:
    plt.rcParams.update({"font.family": "sans-serif", "font.size": 9, "axes.edgecolor": MUTED,
                         "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": INK,
                         "text.color": INK, "axes.titlesize": 10})


def panel(ax) -> None:
    ax.set_facecolor(SURFACE)
    ax.grid(True, color=GRID, lw=0.7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.axhline(0, color=MUTED, lw=1)


def flat_cost(model: str) -> pd.DataFrame:
    """Rare-false-beard advantage per claim cost; `pre_event` marks Qwen levels not yet rerun."""
    if model == "qwen":
        pre = pd.read_csv(ROOT / "runs/d1_costly_claim/analysis.csv").set_index("c")
        event = pd.read_csv(ROOT / "hackathon/runs/event/d1_costly_claim/analysis.csv").set_index("c")
        df = pre[["g0", "g0_lo", "g0_hi"]].copy()
        df["pre_event"] = ~df.index.isin(event.index)
        df.loc[event.index, ["g0", "g0_lo", "g0_hi"]] = event[["g0", "g0_lo", "g0_hi"]]
        return df
    df = pd.read_csv(ROOT / f"runs/api_d1/analysis_{model}.csv").set_index("c")[["g0", "g0_lo", "g0_hi"]]
    df["pre_event"] = False
    return df


def audited(model: str) -> pd.Series:
    path = ROOT / ("hackathon/runs/event/d1_audited/analysis.csv" if model == "qwen"
                   else f"hackathon/runs/api_d1_audited/analysis_{model}.csv")
    return pd.read_csv(path).iloc[0]


def secret(model: str) -> pd.DataFrame:
    path = ROOT / ("hackathon/runs/event/d2_secret/analysis.csv" if model == "qwen"
                   else f"runs/api_slice/analysis_{model}.csv")
    return pd.read_csv(path)


def threshold(model: str) -> tuple[float, float, float]:
    """Replay success below which a rare false beard loses (ρ*), with its bootstrap interval."""
    if model == "qwen":
        h = pd.read_csv(ROOT / "hackathon/runs/headline.csv")
        row = h[(h["sample"] == "event") & (h["key"] == "d2_rho_star")].iloc[0]
        return row["estimate"], row["lo"], row["hi"]
    h = pd.read_csv(ROOT / "runs/api_slice/headline.csv", index_col=0).loc[model]
    return h["d2_rho_star"], h["d2_rho_star_lo"], h["d2_rho_star_hi"]


def figure1(out: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(7.5, 2.9), sharey=True, facecolor=SURFACE)
    for i, (ax, (model, name)) in enumerate(zip(axes, MODELS)):
        panel(ax)
        df = flat_cost(model)
        cs = df.index.values
        ax.fill_between(cs, df.g0_lo, df.g0_hi, color=BLUE, alpha=0.15, lw=0)
        ax.plot(cs, df.g0, color=BLUE, lw=2, zorder=3)
        filled = ~df.pre_event.values
        ax.plot(cs[filled], df.g0.values[filled], "o", color=BLUE, ms=6, mec=SURFACE, mew=1.5, zorder=4)
        if (~filled).any():
            ax.plot(cs[~filled], df.g0.values[~filled], "o", mfc=SURFACE, mec=BLUE, mew=1.5, ms=6, zorder=4)
        a = audited(model)
        lo = a["g0_lo"] if np.isfinite(a["g0_lo"]) else a["g0"]
        hi = a["g0_hi"] if np.isfinite(a["g0_hi"]) else a["g0"]
        ax.axhspan(lo, hi, color=ORANGE, alpha=0.15, lw=0)
        ax.axhline(a["g0"], color=ORANGE, lw=2, ls="--")
        ax.set_title(name, loc="left")
        ax.set_xticks([0, 0.5, 1, 1.5, 2])
        ax.set_xlim(-0.1, 2.1)
        ax.set_xlabel("flat claim cost (points)")
        if i == 0:
            ax.set_ylabel("payoff advantage of a\nrare false beard (points/game)")
            ax.annotate("flat cost", (0.5, df.g0.loc[0.5]), xytext=(6, 6), textcoords="offset points", fontsize=8.5)
            ax.annotate("audited claim", (0.05, a["g0"]), xytext=(0, 5), textcoords="offset points", fontsize=8.5)
            ax.annotate("false beards invade", (2.1, 0), xytext=(0, 4), textcoords="offset points",
                        ha="right", va="bottom", fontsize=7.5, color=MUTED)
            ax.annotate("honest population holds", (2.1, 0), xytext=(0, -4), textcoords="offset points",
                        ha="right", va="top", fontsize=7.5, color=MUTED)
    axes[0].set_ylim(-1.15, 1.15)
    handles = [plt.Line2D([], [], color=BLUE, lw=2, marker="o", label="flat cost (RQ3)"),
               plt.Line2D([], [], color=ORANGE, lw=2, ls="--", label="audited claim, free with a stake of 2 (RQ4)")]
    if flat_cost("qwen").pre_event.any():
        handles.append(plt.Line2D([], [], ls="", marker="o", mfc=SURFACE, mec=BLUE, mew=1.5, label="pre-event run (rerun pending)"))
    fig.legend(handles=handles, loc="lower center", ncol=len(handles), frameon=False, fontsize=8)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(out, dpi=220, facecolor=SURFACE)
    plt.close(fig)


CLAIM_COLS = ["r", "invader_reports_f0"]
GREY_BAR = "#d6d4cc"


def claim_rates(model: str) -> pd.DataFrame:
    """Per claim cost: r, the honest claim rate, and invader_reports_f0, whether a rare false beard
    claims under the rational-false-beard rule (from the same analysis files as flat_cost)."""
    path = (ROOT / "hackathon/runs/event/d1_costly_claim/analysis.csv" if model == "qwen"
            else ROOT / f"runs/api_d1/analysis_{model}.csv")
    return pd.read_csv(path).set_index("c")[CLAIM_COLS]


def figure1_claims(out: Path) -> None:
    """Figure 1 with claim rates added as bars on a right-hand 0-1 axis, behind the payoff lines:
    filled bars for honest agents, outlined bars for a rare false beard (claims or not)."""
    fig, axes = plt.subplots(1, 3, figsize=(7.5, 3.0), sharey=True, facecolor=SURFACE)
    for i, (ax, (model, name)) in enumerate(zip(axes, MODELS)):
        panel(ax)
        df, rates = flat_cost(model), claim_rates(model)
        cs = df.index.values
        ax2 = ax.twinx()
        ax.set_zorder(ax2.get_zorder() + 1)  # payoff lines in front of the bars
        ax.patch.set_visible(False)
        ax2.set_facecolor(SURFACE)
        ax2.bar(rates.index, rates.r, width=0.3, color=GREY_BAR, lw=0)
        # a rare false beard's claim is all-or-nothing: mark the costs at which it claims
        claims = rates.index[rates.invader_reports_f0.astype(bool)]
        ax2.plot(claims, np.full(len(claims), 1.0), "v", color=MUTED, ms=5, clip_on=False)
        ax2.set_ylim(0, 1.05)
        ax2.spines[["top", "left"]].set_visible(False)
        ax2.spines["right"].set_color(MUTED)
        ax2.tick_params(colors=MUTED)
        if i == len(MODELS) - 1:
            ax2.set_ylabel("claim rate (bars)")
        else:
            ax2.spines["right"].set_visible(False)
            ax2.set_yticks([])
        ax.fill_between(cs, df.g0_lo, df.g0_hi, color=BLUE, alpha=0.15, lw=0)
        ax.plot(cs, df.g0, color=BLUE, lw=2, zorder=3)
        ax.plot(cs, df.g0, "o", color=BLUE, ms=6, mec=SURFACE, mew=1.5, zorder=4)
        a = audited(model)
        lo = a["g0_lo"] if np.isfinite(a["g0_lo"]) else a["g0"]
        hi = a["g0_hi"] if np.isfinite(a["g0_hi"]) else a["g0"]
        ax.axhspan(lo, hi, color=ORANGE, alpha=0.15, lw=0)
        ax.axhline(a["g0"], color=ORANGE, lw=2, ls="--")
        ax.set_title(name, loc="left")
        ax.set_xticks([0, 0.5, 1, 1.5, 2])
        ax.set_xlim(-0.2, 2.2)
        ax.set_xlabel("flat claim cost (points)")
        if i == 0:
            ax.set_ylabel("payoff advantage of a\nrare false beard (points/game)")
    axes[0].set_ylim(-1.15, 1.15)
    handles = [plt.Line2D([], [], color=BLUE, lw=2, marker="o", label="flat cost (RQ3)"),
               plt.Line2D([], [], color=ORANGE, lw=2, ls="--", label="audited claim (RQ4)"),
               plt.Rectangle((0, 0), 1, 1, color=GREY_BAR, label="honest claim rate"),
               plt.Line2D([], [], ls="", marker="v", color=MUTED, ms=5, label="rare false beard claims")]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=8)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(out, dpi=220, facecolor=SURFACE)
    plt.close(fig)


def figure2(out: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(7.5, 2.7), sharey=True, facecolor=SURFACE)
    for i, (ax, (model, name)) in enumerate(zip(axes, MODELS)):
        panel(ax)
        df = secret(model)
        ax.fill_between(df.rho, df.g0_lo, df.g0_hi, color=BLUE, alpha=0.15, lw=0)
        ax.plot(df.rho, df.g0, color=BLUE, lw=2)
        t, t_lo, t_hi = threshold(model)
        ax.axvspan(t_lo, t_hi, color=MUTED, alpha=0.12, lw=0)
        ax.axvline(t, color=MUTED, lw=1, ls="--")
        ax.annotate(f"threshold {t:.2f}", (t, 0.95), xytext=(-4, 0), textcoords="offset points",
                    ha="right", fontsize=8, color=INK)
        ax.set_title(name, loc="left")
        ax.set_xlim(0, 1)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
        ax.set_xlabel("replay success")
        if i == 0:
            # the curve crosses zero mid-panel, so the sign key sits in the axis label, not on the plot
            ax.set_ylabel("payoff advantage of a\nrare false beard (points/game)\n> 0: false beards invade")
    axes[0].set_ylim(-1.05, 1.15)
    fig.tight_layout()
    fig.savefig(out, dpi=220, facecolor=SURFACE)
    plt.close(fig)


def main() -> None:
    style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for name, fn in (("report_fig1_cost_vs_audit.png", figure1), ("report_fig2_rotating_secret.png", figure2)):
        fn(FIG_DIR / name)
        print(f"wrote {FIG_DIR / name}")


if __name__ == "__main__":
    main()
