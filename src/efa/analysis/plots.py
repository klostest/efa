from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


def plot_similarity_curve(df: pd.DataFrame, out: Path, title: str = "") -> Path:
    """Cooperation rate vs stated similarity, one line per (condition, model); controls as
    horizontal markers at the right edge."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sweep = df[df.level.notna()]
    for (cond, model), d in sweep.groupby(["condition", "model"]):
        d = d.sort_values("level")
        err = [d.coop_rate - d.coop_lo, d.coop_hi - d.coop_rate]
        ax.errorbar(d.level, d.coop_rate, yerr=err, marker="o", capsize=3,
                    label=f"{cond} / {model.split('/')[-1]}")
    ctrl = df[df.level.isna()]
    for _, r in ctrl.iterrows():
        ax.axhline(r.coop_rate, ls="--", lw=1, alpha=0.6)
        ax.annotate(f"{r.condition} ({r.model.split('/')[-1]})", (102, r.coop_rate), fontsize=7,
                    va="center", annotation_clip=False)
    ax.set_xlabel("stated similarity (%)")
    ax.set_ylabel("realized cooperation rate")
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlim(-3, 103)
    ax.set_title(title)
    ax.legend(fontsize=8)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out
