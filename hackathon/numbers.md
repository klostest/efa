# Numbers pack for the report

Every number the report quotes, with its source. The generated table
`hackathon/runs/headline.md` (from `hackathon/scripts/headline.py`) carries the Qwen
headline quantities with 95% intervals, pre-event beside the event rerun, and says for each
whether the report uses the event rerun or falls back to the pre-event run. Rerun the script
whenever an event cell finishes; this file holds what the generated table does not.

Model names: Qwen = Qwen3.5-27B (4-bit, local, native thinking with a 2,000-token budget,
temperature 1); Sonnet = Claude Sonnet 5.5 and Opus = Claude Opus 5.5 (API, adaptive
thinking at low effort). Symbols as in `docs/variables.md`.

## The game and the design, in numbers

- One-shot Prisoner's Dilemma: both cooperate 2 each (R); both defect 1 each (P); a
  cooperator against a defector gets 0 (S), the defector 3 (T). A defector's payoff is
  1 + 2·[partner cooperates]; cooperating costs exactly one point whatever the partner does.
- N = 100 games per cell for every comparison cell (200 honest decisions in an H–H cell,
  100 in an H–I cell); N = 30 per level in the C0 sweep (60 decisions). Wilson 95%
  intervals on rates; 2,000 bootstrap resamples of the games within each cell for anything
  built from payoffs; replicator end states re-classified on every resample.
- Invader advantage g(f) = mean invader payoff − mean honest payoff at invader fraction f;
  linear in f; g(0) = IH − HH (does a rare invader spread), g(1) = II − HI (does a rare
  honest agent spread). End states: all-invader (both positive), all-honest (both
  negative), bistable (g(0) < 0 ≤ g(1)), interior (g(0) > 0 > g(1)).

Labels: RQ1 claim vs oracle, RQ2 false beards, RQ3 flat cost, RQ4 audited claim, RQ5
rotating secret; the key to the preregistration's names is in `hackathon/README.md`.

## Pre-event Qwen results not in the generated table

- **RQ1, oracle curve (replication of Kundu et al.):** cooperation 0.00 / 0.25 / 0.45 / 0.53 / 0.63 /
  0.92 at stated similarity 0 / 20 / 40 / 60 / 80 / 100; "?" control 0.37; base 0.00;
  0 exclusions. Qwen3-8B was flat in the same channel and dropped.
- **RQ1, claim vs oracle:** claim 0.635 vs attributed oracle 0.662 at stated similarity 80; difference
  −0.027 (95% −0.12 to +0.07; z = −0.59, p = 0.55). Inside the preregistered 10-point
  margin; the formal equivalence test (TOST at 10 points) narrowly fails (90% CI −0.107
  to +0.050). Unattributed oracle at 80 from the gate: 0.63.
- **RQ2 wording control:** minimal claim at 100 gave 0.93 against 0.87 for the full claim sentence
  (difference +0.06, 95% +0.00 to +0.12; z = 2.0, p = 0.046; Fisher p = 0.066). The
  "you have reported" clause did not raise cooperation; the full sentence is, if anything,
  slightly conservative.
- **RQ2:** HH 1.87, HI 0.15, IH 2.70; g(0) = +0.83 (0.69–0.97), g(1) = +0.85; 100% of
  resamples all-invader. Honest cooperation 0.87 with an honest partner, 0.85 with the
  invader (same prompt, independent draws).
- **RQ3 crossings:** honest reporting halves at c = 0.95 (bootstrap 95% 0.84–1.07); the
  invader's report stops paying at c = 1.15 (0.82–1.37). A report buys about 0.65 extra
  cooperation, not RQ2's 0.87. Honest cooperation with a reporter is flat in c (0.70–0.75).
  At c = 2 the silent invader still wins (+0.32) because honest agents keep paying for
  reports and HH falls to 0.80, below mutual defection. 1 exclusion in 1,500 decisions.
- **RQ5:** pM 0.805 (0.75–0.87), pM check 0.82, pX 0.06 (0.02–0.11); HH 1.81; ρ* measured
  0.45 (0.38–0.53), closed form 0.46; bistable in 100% of resamples at ρ = 1/4 and 1/16
  with tipping fractions f* = 0.55 and 0.85; all-invader at ρ = 1 (+0.84, RQ2 restated).
  All six wrong-word cooperations are thinking-budget forced closes. 0 exclusions.
- **RQ4, audited claim (run the night before the event):** r 0.86 (0.82–0.89); p_RR 0.977
  (0.92–0.99), H–H check 0.979; p_NR 0.23 (13 decisions; 0.28 in H–H); pN 0 of 29;
  HH 1.72 (1.63–1.81); HI_R 0.08; IH_R 1.02; IH_N 1.00; g(0) = −0.70 (−0.80 to −0.58) in
  100% of resamples; g(1) = 0 exactly. Game counts: H–H 73 both-reported (70 C,C; 3 one
  defection), 25 one-sided (reporter always defected; silent cooperated 7), 2 both silent
  (D,D); H–I 87 reported honest (85 C, 2 D), 13 silent (3 C, 10 D). Honest expected
  forfeit a·r·(1 − p_RR) = 0.04 per game; invader's a·r = 1.72. All five both-reported
  defections are budget cutoffs before the forfeit arithmetic. Prediction 3 of the spec
  was mis-derived (the invader is nearly indifferent, +0.02, not silent); see
  `reports/d1_audited.md`.
- **Channel:** on Qwen, 95–99% of calls use the full 2,000-token thinking budget and are
  closed by the harness; the forced-close rate is reported per cell in every summary CSV.
  Exclusions across the whole screen: 2 (one in H1, one in D1).

## Event-sample test statistics not in the generated table

Same tests as the pre-event bullets above (two-proportion z with pooled variance, Wald
interval on the difference, Fisher exact on the decision counts; the equivalence test is
two one-sided tests at the preregistered 10-point margin, read off the 90% interval).

- **RQ1, claim vs oracle (event):** claim 130 of 200 (0.650) vs attributed oracle 140 of 200
  (0.700) at stated similarity 80; difference −0.050 (95% −0.142 to +0.042; z = −1.07,
  p = 0.29; Fisher p = 0.34). Inside the 10-point margin as a point estimate; the
  equivalence test fails again, by more than pre-event (90% CI −0.127 to +0.027, crossing
  −0.10 by 0.027). Same statement as before: no detectable difference, consistent with
  equivalence, not established at the margin chosen.
- **RQ2 wording control (event):** minimal claim at 100 gave 183 of 200 (0.915) against 179
  of 200 (0.895) for the full claim sentence (difference +0.020, 95% −0.037 to +0.077;
  z = 0.68, p = 0.50; Fisher p = 0.61). Pre-event's marginal +0.06 (p = 0.046) does not
  recur; the clause neither raises nor lowers cooperation detectably.

## Frontier models (pre-event, `runs/api_slice`, `runs/api_d1`; about $53)

| Quantity | Qwen | Sonnet 5.5 | Opus 5.5 |
|---|---|---|---|
| base cooperation | 0.00 | 0.00 | 0.00 |
| RQ2 honest cooperation, H–H / H–I | 0.87 / 0.85 | 0.99 / 1.00 | 1.00 / 1.00 |
| RQ2 g(0) | +0.83 | +1.01 | +1.00 |
| RQ5 pM / pX | 0.805 / 0.06 | 0.835 / 0.00 | 1.00 / 0.00 |
| RQ5 ρ* | 0.45 (0.38–0.53) | 0.47 (0.43–0.52) | 0.50 |
| RQ3 honest report rate at c = 0 / 0.5 / 1 / 1.5 / 2 | 0.93 / 0.66 / 0.48 / 0.25 / 0.19 | 0.89 / 0.12 / 0.05 / 0.02 / 0.02 | 1.00 / 0.38 / 0.00 / 0.00 / 0.00 |
| RQ3 HH at c = 0 / 0.5 / 1 / 1.5 / 2 | 1.83 / 1.23 / 0.97 / 0.85 / 0.80 | 1.78 / 1.01 / 1.00 / 0.99 / 0.965 | 1.99 / 1.12 / 1.00 / 1.00 / 1.00 |
| RQ3 g(0) at c = 0 / 0.5 / 1 / 1.5 / 2 | +0.95 / +0.77 / +0.52 / +0.28 / +0.32 | +0.91 / +0.76 / +0.42 / +0.01 / +0.035 | +0.89 / +0.18 / 0 / 0 / 0 |
| RQ3 reporting halves at c = | 0.95 | 0.26 | 0.41 |
| RQ3 invader's report stops paying at c = | 1.15 | 1.46 (1.31–1.58) | 0.67 (0.58–0.73) |

Two routes to the same RQ3 conclusion: Qwen keeps reporting and is taxed below mutual
defection; the Claude models stop reporting at the first positive cost, so from c = 1
nobody reports, HH returns to 1.00 and the two types play alike (g(0) = 0, "neutral").
Opus cooperates with a reporting partner almost only when it reported itself (1.00 vs
0.28). GPT models were deliberately not used (they never cooperate in Kundu et al., so
there is nothing to spoof).

## Made during the hackathon

- **RQ4, audited claim on Sonnet 5.5 and Opus 5.5** (`hackathon/runs/api_d1_audited`, 600 calls
  per model, 0 exclusions; full table in `reports/d1_audited.md`, "Across models"):

  | Quantity | Qwen | Sonnet 5.5 | Opus 5.5 |
  |---|---|---|---|
  | r | 0.86 (0.82–0.89) | 0.87 (0.83–0.91) | 1.00 |
  | p_RR | 0.977 | 1.00 | 1.00 |
  | p_NR | 0.23 (13 decisions) | 0.11 (9) | undefined |
  | pN | 0 of 29 | 0 of 29 | undefined |
  | HH | 1.72 | 1.745 | 2.00 |
  | invader vs honest: reporting / silent | 1.02 / 1.00 | 1.02 / 1.00 | 1.00 / undefined |
  | g(0) | −0.70 (−0.80 to −0.58) | −0.73 (−0.82 to −0.64) | −1.00 |
  | end state | bistable (g(1) = 0), 100% | bistable (g(1) = 0), 100% | all-honest by scoring convention, 100% |
  | same model, RQ3 flat cost c = 2: g(0) | +0.32 | +0.035 | 0 |

  RQ4's answer holds on all three. Sonnet's 13% silence is mostly tail sampling of hedged answers
  (stated report probability 0.90–0.97 in 222 of 300 claim calls; 7 decided declines),
  not self-selection as on Qwen; the silent agents still defect. Opus never stays silent,
  so its play against a silent partner is unobserved and the invader is scored as
  reporting at every f (hence g(1) = −1, "all-honest"); with defection against a silent
  partner, as Opus showed at RQ3's c = 2 (0 of 200), the all-invader corner would be
  neutral as on the other models. Pilot: 24 games, 0 exclusions, forfeit named in every
  transcript, no payment-to-partner reading.
- **Event reruns of the Qwen matrix** (`hackathon/runs/event`): see the generated table.
  Status Sunday 07:30: every block done (last one, the RQ2 wording control, at 07:26
  Sunday), so the fallback to pre-event numbers is not needed anywhere. Exclusions: 6 of
  2,250 games, at most 2 in any cell (RQ3: 4, two of them in the c = 1 honest-vs-honest
  cell, which ended at 98 games; RQ5: 2 of 300). Forced closes: 95–100% of decisions per
  cell (5 of 29 cells at 100%), 98.4% overall (corrected 2026-11-08 from "every cell
  reached its N with at most one exclusion", checked against the summary CSVs). All 54 headline quantities replicate:
  every pre-event and event 95% interval overlaps, and no end state changes. Nine point
  estimates fall outside the pre-event interval (sampling noise at N = 100; listed in the
  research log). Event headline values the report quotes: RQ1 oracle curve 0.02, 0.37,
  0.38, 0.53, 0.63, 0.80 at similarity 0 to 100, "?" 0.38, base 0.05; RQ1 claim − oracle at
  80 = −0.05 (−0.14 to +0.04), 0.65 vs 0.70; RQ2 g(0) = +0.845 (0.71–0.97), HH 1.895,
  all-invader 100%; RQ2 wording control 0.915 vs 0.895, difference +0.02 (−0.04 to +0.08);
  RQ3 report rate 0.91, 0.64, 0.45, 0.27, 0.26 and g(0) +0.85, +0.73, +0.45, +0.39, +0.46
  at c = 0, 0.5, 1, 1.5, 2, all-invader at every level; RQ4 g(0) = −0.64 (−0.77 to −0.45),
  r 0.86, pN 0.037 (1 cooperation in 29 silent-partner decisions), bistable 100%; RQ5 pM 0.864, pX 0.03, ρ* 0.56 (0.48–0.65), closed
  form 0.48, bistable at ρ = 1/4, all-invader at ρ = 1.
- **RQ4 tipping fraction f\*** (the invader share above which the invaders' advantage
  g(f) turns positive, so the all-honest state holds for every invader share below f\*;
  f\* = g(0) / (g(0) − g(1)) when g(1) > 0, and f\* = 1 when g(1) = 0, since g(f) < 0 at
  every f < 1 and the all-invader corner is neutral: a silent invader among silent
  invaders plays exactly like a silent honest agent). Computed from the audited script's
  own 2,000 bootstrap resamples (`d1_audited_analysis.py`, seed 0), no new runs.
  - Qwen, event sample: f\* = 0.945, 95% 0.79–1.00 (median 0.95, lowest resample 0.55).
    Every resample is bistable; 38% of them have pN = 0 exactly and so f\* = 1 (the
    stored `f_star_lo`/`f_star_hi` in `analysis.csv`, 0.76–0.96, drop those resamples and
    understate the top of the interval). Reading: honest agents hold unless false beards
    are at least about 80% of the population, point estimate 95%.
  - Qwen, pre-event: pN = 0 of 29, so g(1) = 0 and f\* = 1 in the point estimate and in
    every resample.
  - Sonnet 5.5: pN = 0 of 29, g(1) = 0 exactly in the point estimate and every resample;
    classified bistable with a neutral all-invader corner, f\* = 1 (95% 1.00–1.00):
    honest agents hold at every invader share below 1.
  - Opus 5.5: all-honest by scoring convention (g(1) = −1), so no tipping fraction.
