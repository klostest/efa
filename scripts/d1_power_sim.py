"""Power simulation for the continuous-cost D1 design (2026-10-26).

Question: if the report cost c is drawn per game uniformly on (0, 2] instead of fixed at
{0, 1, 2}, how precisely can the two D1 thresholds be estimated from the same compute?
  c_q : the cost at which the honest report rate crosses one half (Grafen's threshold)
  c*  : the cost at which the rare-invader advantage, IH(c) - HH(c), crosses zero

Design simulated: 50 honest-vs-honest and 50 honest-vs-invader anchor games at c = 0, plus
250 honest-vs-honest and 250 honest-vs-invader games with c ~ U(0, 2]. Same 1,800 model
calls as the three fixed cells at N = 100.

Generative model, from the C2 numbers where we have them and guesses elsewhere:
  honest reports with probability q(c) = logistic((c50 - c) / w), c50 = 1, three widths w;
  honest cooperation given (own report, partner report): both 0.87 (C2), mine only 0.30
  (guess), partner only 0.80 (guess), neither 0.05 (gate base rate ~0);
  the invader always reports and always defects; reporters pay c.

Analysis simulated: kernel-smoothed means on a grid (Gaussian kernel, bandwidth 0.2), the
thresholds read off the smoothed curves, 100 bootstrap resamples over games for their
standard errors, 40 simulated datasets per scenario.

Result (seed 1): SE of c_q about 0.02-0.06 and SE of c* about 0.08-0.10 on the cost scale
across the three transition widths; under these numbers c* falls at 1.55-1.70, after the
honest report rate has collapsed, and c* is guaranteed below 2 because a report can never
pay for an invader at c = 2 (the most it can gain is 3 - 1). In the shallow scenario the
crossing is undefined in ~23% of resamples (smoothing noise near the top of the range);
report a one-sided bound in that case. Run: uv run python scripts/d1_power_sim.py
"""

from __future__ import annotations

import numpy as np

rng = np.random.default_rng(1)

# honest cooperation probability given (own report, partner report)
COOP = {(1, 1): 0.87, (1, 0): 0.30, (0, 1): 0.80, (0, 0): 0.05}
PAY = {("C", "C"): (2, 2), ("C", "D"): (0, 3), ("D", "C"): (3, 0), ("D", "D"): (1, 1)}
GRID = np.linspace(0, 2, 81)


def q(c, c50, w):
    """Honest report probability at cost c."""
    return 1 / (1 + np.exp((c - c50) / w))


def sim(c50, w, n_hh=250, n_hi=250, n_anchor=50):
    """One dataset. hh rows: (c, honest payoff 0, honest payoff 1, report 0, report 1).
    hi rows: (c, invader payoff, honest report)."""
    cs_hh = np.concatenate([np.zeros(n_anchor), rng.uniform(0, 2, n_hh)])
    cs_hi = np.concatenate([np.zeros(n_anchor), rng.uniform(0, 2, n_hi)])
    hh = []
    for c in cs_hh:
        r0, r1 = rng.random() < q(c, c50, w), rng.random() < q(c, c50, w)
        a0 = "C" if rng.random() < COOP[(r0, r1)] else "D"
        a1 = "C" if rng.random() < COOP[(r1, r0)] else "D"
        p0, p1 = PAY[(a0, a1)]
        hh.append((c, p0 - c * r0, p1 - c * r1, r0, r1))
    hi = []
    for c in cs_hi:
        r0 = rng.random() < q(c, c50, w)
        a0 = "C" if rng.random() < COOP[(r0, 1)] else "D"
        hi.append((c, (3 if a0 == "C" else 1) - c, r0))
    return np.array(hh), np.array(hi)


def ksmooth(x, y, grid, h):
    """Nadaraya-Watson kernel-smoothed mean of y against x, evaluated on grid."""
    w = np.exp(-0.5 * ((grid[:, None] - x[None, :]) / h) ** 2)
    return (w * y[None, :]).sum(1) / w.sum(1)


def cross(y, level):
    """First grid point where the smoothed curve crosses `level`, or nan."""
    s = np.where(np.diff(np.sign(y - level)) != 0)[0]
    return GRID[s[0]] if len(s) else np.nan


def analyze(hh, hi, h=0.2):
    cx = np.concatenate([hh[:, 0], hh[:, 0], hi[:, 0]])
    cy = np.concatenate([hh[:, 3], hh[:, 4], hi[:, 2]])
    qc = ksmooth(cx, cy, GRID, h)
    HH = ksmooth(np.concatenate([hh[:, 0], hh[:, 0]]), np.concatenate([hh[:, 1], hh[:, 2]]), GRID, h)
    IH = ksmooth(hi[:, 0], hi[:, 1], GRID, h)
    return cross(qc, 0.5), cross(IH - HH, 0.0)


def boot(hh, hi, B=100):
    out = []
    for _ in range(B):
        i = rng.integers(0, len(hh), len(hh))
        j = rng.integers(0, len(hi), len(hi))
        out.append(analyze(hh[i], hi[j]))
    return np.array(out)


def true_adv(c, c50, w):
    """Exact rare-invader advantage IH(c) - HH(c) under the generative model."""
    qq = q(c, c50, w)
    hh = 0.0
    for r0 in (0, 1):
        for r1 in (0, 1):
            pr = (qq if r0 else 1 - qq) * (qq if r1 else 1 - qq)
            exp_pay = sum(
                PAY[(a0, a1)][0]
                * (COOP[(r0, r1)] if a0 == "C" else 1 - COOP[(r0, r1)])
                * (COOP[(r1, r0)] if a1 == "C" else 1 - COOP[(r1, r0)])
                for a0 in "CD"
                for a1 in "CD"
            )
            hh += pr * (exp_pay - c * r0)
    ih = sum((qq if r0 else 1 - qq) * (1 + 2 * COOP[(r0, 1)]) for r0 in (0, 1)) - c
    return ih - hh


def main(n_datasets=40):
    scenarios = [
        (1.0, 0.05, "sharp step at 1"),
        (1.0, 0.2, "medium (10-90% over ~0.9)"),
        (1.0, 0.5, "shallow (10-90% over ~2.2)"),
    ]
    for c50, w, label in scenarios:
        ta = np.array([true_adv(c, c50, w) for c in GRID])
        tcs = cross(ta, 0.0)
        reps = []
        for _ in range(n_datasets):
            b = boot(*sim(c50, w))
            reps.append((np.nanstd(b[:, 0]), np.nanstd(b[:, 1]), np.isnan(b[:, 1]).mean()))
        reps = np.array(reps)
        print(
            f"{label}: true c_q={c50:.2f}, true c*={tcs:.2f}; "
            f"bootstrap SE of c_q ~{reps[:, 0].mean():.2f}, SE of c* ~{reps[:, 1].mean():.2f}, "
            f"c* undefined in {reps[:, 2].mean():.0%} of resamples"
        )
        print(f"   true advantage at c=0.5/1.0/1.5/2.0: {[round(float(true_adv(c, c50, w)), 2) for c in (0.5, 1, 1.5, 2)]}")


if __name__ == "__main__":
    main()
