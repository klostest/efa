"""Headline table for the hackathon report: every number the report quotes, from the
pre-event runs (runs/) and the event-weekend reruns (hackathon/runs/event/), side by side,
plus a replication figure.

Blocks and their run directories (same stem in both samples):
  c0        c0_gate_27b_think   cooperation at stated similarity 0..100, "?" and base
  h1        c1_h1               oracle-attributed vs partner claim at 80, and the difference
  confound  c2_confound         minimal claim at 100 against the C2 sentence
  c2        c2_false_beards     H-H and H-I cooperation, HH, HI, IH, g(0), g(1), end state
  d1        d1_costly_claim     per cost level: r, pR, pN, HH, g(0), end state  (scripts/d1_analysis.py)
  d2        d2_secret           pM, pM check, pX, rho*, g(0) at rho = 1/4 and 1  (scripts/d2_analysis.py)
  audited   d1_audited          r, p_RR, p_NR, pN, HH, g(0), g(1)  (scripts/d1_audited_analysis.py)

For the pre-event sample the per-arm CSVs already in runs/ are read as they are. For the event
sample the per-arm scripts are run on the event directories (figures go to hackathon/figures)
and only cells with their full N are used, so a half-finished rerun contributes nothing yet.

Usage: .venv/bin/python hackathon/scripts/headline.py [--boot 2000] [--no-figs]
Writes hackathon/runs/headline.csv (long format), hackathon/runs/headline.md (the table the
report copies from) and hackathon/figures/event_replication.png.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from api_slice_analysis import c2_numbers, coop  # noqa: E402

from efa.analysis.metrics import load_games, wilson  # noqa: E402

PRE, EVENT = ROOT / "runs", ROOT / "hackathon" / "runs" / "event"
FIGS = ROOT / "hackathon" / "figures"
PY = sys.executable


def complete_cells(run_dir: Path) -> dict[str, list[dict]]:
    """Games grouped by cell id (model suffix dropped), keeping only cells that reached their N."""
    if not (run_dir / "games.jsonl").exists():
        return {}
    by: dict[str, list[dict]] = {}
    for g in load_games(run_dir):
        by.setdefault(g["cell"]["cell_id"], []).append(g)
    out = {}
    for cid, gs in by.items():
        if len(gs) >= gs[0]["cell"]["n_games"]:
            out[cid.split("__")[0]] = [g for g in gs if not g["excluded"]]
    return out


def rate_row(sample, block, key, label, gs, players=(0, 1)) -> dict:
    p, k, n = coop(gs, players)
    lo, hi = wilson(k, n)
    return dict(sample=sample, block=block, key=key, label=label, estimate=p, lo=lo, hi=hi, n=n)


def diff_row(sample, block, key, label, a: dict, b: dict) -> dict:
    """a − b for two rate rows, Wald 95% interval."""
    d = a["estimate"] - b["estimate"]
    se = np.sqrt(a["estimate"] * (1 - a["estimate"]) / a["n"] + b["estimate"] * (1 - b["estimate"]) / b["n"])
    return dict(sample=sample, block=block, key=key, label=label, estimate=d, lo=d - 1.96 * se, hi=d + 1.96 * se,
                n=a["n"] + b["n"])


def block_c0(sample, cells) -> list[dict]:
    rows = []
    for lvl in (0, 20, 40, 60, 80, 100):
        cid = f"oracle_{lvl}"
        if cid in cells:
            rows.append(rate_row(sample, "c0", f"c0_{lvl}", f"C0 cooperation, similarity {lvl}", cells[cid]))
    for cid, label in (("unknown", 'C0 cooperation, "?" control'), ("base", "C0 cooperation, base (no signal)")):
        if cid in cells:
            rows.append(rate_row(sample, "c0", f"c0_{cid}", label, cells[cid]))
    return rows


def block_h1(sample, cells) -> list[dict]:
    rows = []
    if "oracle_attributed_80" in cells and "claim_80" in cells:
        a = rate_row(sample, "h1", "h1_oracle", "H1 cooperation, environment reports 80", cells["oracle_attributed_80"])
        b = rate_row(sample, "h1", "h1_claim", "H1 cooperation, partner reports 80", cells["claim_80"])
        rows += [a, b, diff_row(sample, "h1", "h1_diff", "H1 difference, claim − oracle", b, a)]
    return rows


def block_c2(sample, cells, boot, rng) -> list[dict]:
    rows = []
    hh, hi = cells.get("claim_symmetric_100"), cells.get("claim_symmetric_100_vs_always_defect")
    if hh and hi:
        rows.append(rate_row(sample, "c2", "c2_hh", "C2 honest cooperation, honest partner", hh))
        rows.append(rate_row(sample, "c2", "c2_hi", "C2 honest cooperation, invader partner", hi, (0,)))
        c = c2_numbers(hh, hi, boot, rng)
        for key, label in (("HH", "C2 honest payoff vs honest (HH)"), ("HI", "C2 honest payoff vs invader (HI)"),
                           ("IH", "C2 invader payoff vs honest (IH)")):
            rows.append(dict(sample=sample, block="c2", key=f"c2_{key}", label=label, estimate=c[key], lo=np.nan, hi=np.nan,
                             n=len(hh) + len(hi)))
        rows.append(dict(sample=sample, block="c2", key="c2_g0", label="C2 invader advantage g(0)", estimate=c["g0"],
                         lo=c["g0_lo"], hi=c["g0_hi"], n=len(hh) + len(hi)))
        rows.append(dict(sample=sample, block="c2", key="c2_g1", label="C2 invader advantage g(1)", estimate=c["g1"],
                         lo=np.nan, hi=np.nan, n=len(hi)))
        rows.append(dict(sample=sample, block="c2", key="c2_all_invader", label="C2 resamples ending all-invader",
                         estimate=c["frac_all_invader"], lo=np.nan, hi=np.nan, n=boot))
    return rows


def block_confound(sample, cells, c2_cells) -> list[dict]:
    rows = []
    if "claim_100" in cells:
        a = rate_row(sample, "confound", "confound_min", "Confound: minimal claim at 100", cells["claim_100"])
        rows.append(a)
        if c2_cells.get("claim_symmetric_100"):
            b = rate_row(sample, "confound", "confound_c2", "C2 sentence at 100", c2_cells["claim_symmetric_100"])
            rows.append(diff_row(sample, "confound", "confound_diff", "Confound difference, minimal − C2 sentence", a, b))
    return rows


def run_script(name: str, run_dir: Path, fig: Path, extra: list[str], boot: int) -> bool:
    cmd = [PY, str(ROOT / "scripts" / name), "--run", str(run_dir), "--boot", str(boot), "--fig", str(fig), *extra]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        print(f"  {name} on {run_dir.name} failed:\n{r.stderr[-800:]}")
        return False
    return True


def block_d1(sample, run_dir, cells, boot, do_scripts) -> list[dict]:
    if not any(k.startswith("costly_claim_c") for k in cells):
        return []
    if sample == "event" and do_scripts:
        if not run_script("d1_analysis.py", run_dir, FIGS / "d1_costly_claim.png", ["--title", "Qwen3.5-27B, event rerun"], boot):
            return []
    csv = run_dir / "analysis.csv"
    if not csv.exists():
        return []
    df = pd.read_csv(csv).set_index("c")
    rows = []
    for c in df.index:
        # both cells of the level must be complete in this sample
        if f"costly_claim_c{c:g}" not in cells or f"costly_claim_c{c:g}_vs_always_defect" not in cells:
            continue
        n = len(cells[f"costly_claim_c{c:g}"]) + len(cells[f"costly_claim_c{c:g}_vs_always_defect"])
        r = df.loc[c]
        rows.append(dict(sample=sample, block="d1", key=f"d1_r_{c:g}", label=f"D1 honest report rate, c = {c:g}",
                         estimate=r["r"], lo=r["r_wilson_lo"], hi=r["r_wilson_hi"], n=n))
        rows.append(dict(sample=sample, block="d1", key=f"d1_pR_{c:g}", label=f"D1 cooperation with a reporter, c = {c:g}",
                         estimate=r["pR"], lo=r["pR_lo"], hi=r["pR_hi"], n=n))
        rows.append(dict(sample=sample, block="d1", key=f"d1_HH_{c:g}", label=f"D1 honest payoff HH, c = {c:g}",
                         estimate=r["HH"], lo=r["HH_lo"], hi=r["HH_hi"], n=n))
        rows.append(dict(sample=sample, block="d1", key=f"d1_g0_{c:g}", label=f"D1 invader advantage g(0), c = {c:g}",
                         estimate=r["g0"], lo=r["g0_lo"], hi=r["g0_hi"], n=n))
    return rows


def block_d2(sample, run_dir, cells, boot, do_scripts) -> list[dict]:
    need = ("secret_match", "secret_match_vs_always_defect", "secret_mismatch_vs_always_defect")
    if not all(k in cells for k in need):
        return []
    if sample == "event" and do_scripts:
        if not run_script("d2_analysis.py", run_dir, FIGS / "d2_secret.png", ["--title", "Qwen3.5-27B, event rerun"], boot):
            return []
    cells_csv, grid_csv = run_dir / "cells.csv", run_dir / "analysis.csv"
    if not (cells_csv.exists() and grid_csv.exists()):
        return []
    cells_df = pd.read_csv(cells_csv, index_col=0)
    grid = pd.read_csv(grid_csv)
    n = sum(len(cells[k]) for k in need)
    rows = []
    for key, label in (("pM", "D2 cooperation, words match (pM)"), ("pM_check", "D2 pM check (H–I match cell)"),
                       ("pX", "D2 cooperation, wrong word (pX)"), ("rho_star", "D2 tolerable replay success ρ*")):
        if key in cells_df.index:
            r = cells_df.loc[key]
            rows.append(dict(sample=sample, block="d2", key=f"d2_{key}", label=label, estimate=r["estimate"], lo=r["lo"], hi=r["hi"], n=n))
    for rho, tag in ((0.25, "1/4"), (1.0, "1")):
        g = grid.iloc[(grid["rho"] - rho).abs().argmin()]
        rows.append(dict(sample=sample, block="d2", key=f"d2_g0_{tag}", label=f"D2 invader advantage g(0), ρ = {tag}",
                         estimate=g["g0"], lo=g["g0_lo"], hi=g["g0_hi"], n=n))
    return rows


def block_audited(sample, run_dir, cells, boot, do_scripts, d1_dir: Path) -> list[dict]:
    need = ("costly_claim_c0_a2", "costly_claim_c0_a2_vs_always_defect")
    if not all(k in cells for k in need):
        return []
    if sample == "event" and do_scripts:
        if not run_script("d1_audited_analysis.py", run_dir, FIGS / "d1_audited.png",
                          ["--d1", str(d1_dir), "--title", "Qwen3.5-27B, event rerun"], boot):
            return []
    csv = run_dir / "analysis.csv"
    if not csv.exists():
        return []
    r = pd.read_csv(csv).iloc[0]
    n = sum(len(cells[k]) for k in need)
    rows = []
    for key, label, lo, hi in (("r", "Audited honest report rate", "r_wilson_lo", "r_wilson_hi"),
                               ("p_RR", "Audited cooperation, both reported (p_RR)", "p_RR_wilson_lo", "p_RR_wilson_hi"),
                               ("p_NR", "Audited cooperation, silent agent facing a reporter (p_NR)", "p_NR_lo", "p_NR_hi"),
                               ("pN", "Audited cooperation with a silent partner (pN)", "pN_lo", "pN_hi"),
                               ("HH", "Audited honest payoff HH", "HH_lo", "HH_hi"),
                               ("g0", "Audited invader advantage g(0)", "g0_lo", "g0_hi"),
                               ("g1", "Audited invader advantage g(1)", "g1_lo", "g1_hi")):
        rows.append(dict(sample=sample, block="audited", key=f"aud_{key}", label=label, estimate=r[key],
                         lo=r.get(lo, np.nan), hi=r.get(hi, np.nan), n=n))
    return rows


def collect(sample: str, base: Path, boot: int, do_scripts: bool, rng) -> list[dict]:
    cells = {stem: complete_cells(base / stem) for stem in
             ("c0_gate_27b_think", "c1_h1", "c2_confound", "c2_false_beards", "d1_costly_claim", "d2_secret", "d1_audited")}
    rows = []
    rows += block_c0(sample, cells["c0_gate_27b_think"])
    rows += block_h1(sample, cells["c1_h1"])
    rows += block_c2(sample, cells["c2_false_beards"], boot, rng)
    rows += block_confound(sample, cells["c2_confound"], cells["c2_false_beards"])
    rows += block_d1(sample, base / "d1_costly_claim", cells["d1_costly_claim"], boot, do_scripts)
    rows += block_d2(sample, base / "d2_secret", cells["d2_secret"], boot, do_scripts)
    d1_dir = base / "d1_costly_claim" if (base / "d1_costly_claim" / "analysis.csv").exists() else PRE / "d1_costly_claim"
    rows += block_audited(sample, base / "d1_audited", cells["d1_audited"], boot, do_scripts, d1_dir)
    return rows


def fmt(est, lo, hi) -> str:
    if pd.isna(est):
        return ""
    s = f"{est:.3f}" if abs(est) < 10 else f"{est:.2f}"
    if not pd.isna(lo) and not pd.isna(hi):
        s += f" ({lo:.2f}–{hi:.2f})"
    return s


def wide_table(df: pd.DataFrame) -> pd.DataFrame:
    order = [k for k in df[df["sample"] == "pre-event"]["key"]] + [k for k in df["key"] if k not in set(df[df["sample"] == "pre-event"]["key"])]
    seen, keys = set(), []
    for k in order:
        if k not in seen:
            seen.add(k)
            keys.append(k)
    out = []
    for k in keys:
        pre = df[(df["sample"] == "pre-event") & (df["key"] == k)]
        ev = df[(df["sample"] == "event") & (df["key"] == k)]
        label = (pre if len(pre) else ev).iloc[0]["label"]
        p = pre.iloc[0] if len(pre) else None
        e = ev.iloc[0] if len(ev) else None
        inside = ""
        if p is not None and e is not None and not pd.isna(p["lo"]):
            inside = "yes" if p["lo"] - 1e-9 <= e["estimate"] <= p["hi"] + 1e-9 else "no"
        out.append(dict(key=k, quantity=label,
                        pre_event=fmt(p["estimate"], p["lo"], p["hi"]) if p is not None else "",
                        event=fmt(e["estimate"], e["lo"], e["hi"]) if e is not None else "(not yet run)",
                        event_inside_pre_interval=inside,
                        source="event" if e is not None else "pre-event (fallback)"))
    return pd.DataFrame(out)


def make_figure(df: pd.DataFrame, out: Path) -> None:
    blue, orange = "#2a78d6", "#eb6834"
    ink, muted, grid, surface = "#0b0b0b", "#898781", "#e1e0d9", "#fcfcfb"
    plt.rcParams.update({"font.family": "sans-serif", "axes.edgecolor": muted, "xtick.color": muted,
                         "ytick.color": muted, "axes.labelcolor": ink, "text.color": ink})
    keys = list(dict.fromkeys(df["key"]))
    labels = {k: df[df["key"] == k].iloc[0]["label"] for k in keys}
    rates = [k for k in keys if not any(t in k for t in ("HH", "HI", "IH", "g0", "g1", "diff", "all_invader"))]
    pays = [k for k in keys if k not in rates]
    fig, axes = plt.subplots(1, 2, figsize=(13, max(6, 0.32 * max(len(rates), len(pays)) + 1.5)), facecolor=surface,
                             gridspec_kw={"width_ratios": [1, 1]})
    for ax, ks, title, xlab in ((axes[0], rates, "Rates", "rate"), (axes[1], pays, "Payoffs, differences, advantages", "points")):
        ax.set_facecolor(surface)
        ax.grid(True, axis="x", color=grid, lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
        ys = np.arange(len(ks))[::-1]
        for sample, color, dy, mk in (("pre-event", blue, 0.17, "o"), ("event", orange, -0.17, "s")):
            sub = df[df["sample"] == sample].set_index("key")
            xs, yy, err = [], [], []
            for k, y in zip(ks, ys):
                if k in sub.index:
                    r = sub.loc[k]
                    xs.append(r["estimate"]); yy.append(y + dy)
                    lo = 0 if pd.isna(r["lo"]) else max(0.0, r["estimate"] - r["lo"])
                    hi = 0 if pd.isna(r["hi"]) else max(0.0, r["hi"] - r["estimate"])
                    err.append((lo, hi))
            if xs:
                e = np.array(err).T
                ax.errorbar(xs, yy, xerr=e, fmt=mk, color=color, ms=6, lw=0, elinewidth=1.6, capsize=2, label=sample)
        ax.set_yticks(ys)
        ax.set_yticklabels([labels[k] for k in ks], fontsize=8)
        ax.set_title(title, loc="left", fontsize=11)
        ax.set_xlabel(xlab)
        if ax is axes[1]:
            ax.axvline(0, color=muted, lw=1)
    handles, labs = axes[0].get_legend_handles_labels()
    fig.suptitle("Pre-event runs against the event-weekend reruns (Qwen3.5-27B, fresh samples, 95% intervals)",
                 x=0.01, ha="left", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.965))
    fig.legend(handles, labs, loc="upper right", bbox_to_anchor=(0.99, 0.995), ncol=2, frameon=False, fontsize=9)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, facecolor=surface)
    plt.close(fig)


def copy_pre_figures() -> None:
    """Pre-event figures beside the event ones, prefixed, for cells that fall back to pre-event data."""
    src = ROOT / "reports" / "figures"
    FIGS.mkdir(parents=True, exist_ok=True)
    for name in ("c0_c0_gate_27b_think.png", "d1_costly_claim.png", "d2_secret.png", "d1_audited.png",
                 "d1_costly_claim_claude-sonnet-5-5.png", "d1_costly_claim_claude-opus-5-5.png",
                 "d2_secret_claude-sonnet-5-5.png", "d2_secret_claude-opus-5-5.png"):
        if (src / name).exists():
            shutil.copyfile(src / name, FIGS / f"pre_{name}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--no-figs", action="store_true", help="skip the per-arm scripts and the replication figure")
    args = ap.parse_args()
    rng = np.random.default_rng(0)
    rows = collect("pre-event", PRE, args.boot, False, rng) + collect("event", EVENT, args.boot, not args.no_figs, rng)
    df = pd.DataFrame(rows)
    out_dir = ROOT / "hackathon" / "runs"
    df.to_csv(out_dir / "headline.csv", index=False)
    wide = wide_table(df)
    md = ["| Quantity | Pre-event (95%) | Event rerun (95%) | Event inside pre-event interval | Report uses |", "|---|---|---|---|---|"]
    md += [f"| {r.quantity} | {r.pre_event} | {r.event} | {r.event_inside_pre_interval} | {r.source} |" for r in wide.itertuples()]
    (out_dir / "headline.md").write_text("\n".join(md) + "\n")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 60)
    print(wide.drop(columns=["key"]).to_string(index=False))
    print(f"wrote {out_dir / 'headline.csv'} and {out_dir / 'headline.md'}")
    if not args.no_figs:
        copy_pre_figures()
        make_figure(df, FIGS / "event_replication.png")
        print(f"wrote {FIGS / 'event_replication.png'}")


if __name__ == "__main__":
    main()
