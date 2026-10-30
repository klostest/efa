# D1: a flat cost on the similarity claim does not stop false beards

Companion to `figures/d1_costly_claim.png`. Run `runs/d1_costly_claim` (2026-10-26 to
2026-10-27), analysis `scripts/d1_analysis.py`, numbers in `runs/d1_costly_claim/analysis.csv`.
Model: Qwen3.5-27B (4-bit, local), native thinking with a 2,000-token budget, temperature 1.
Every symbol below is also in the project's master list, `docs/variables.md`.

## Definitions

**The game.** Two players play a one-shot Prisoner's Dilemma. Each chooses to cooperate (C)
or defect (D). The payoffs are: both cooperate, 2 each (R); both defect, 1 each (P); a
cooperator against a defector gets 0 (S) and the defector gets 3 (T).

**The claim.** Before the game, each player may report to the other that its decision-making
is 100% similar to theirs. Reporting costs c points, deducted from the reporter's score
whatever the other player reports or does. Both players decide at the same time, and each is
then told whether the other reported before choosing its action.

**Types.** An *honest* agent is the language model (Qwen3.5-27B) playing the game: a call
to the model with the rules and the claim option decides whether to report, and a second
call with the rules and both players' reports decides its action. Both answers are
probability distributions that the harness samples from. An *invader* (false beard) is not
a language model but a fixed rule in the harness: it always defects. In the run it also
always reported. In the analysis, its payoff against honest agents is not taken from the
run but computed from the honest agents' measured responses to a reporting partner and to
a silent one, and the invader is given the better of the two at each invader frequency
(the rational-invader rule below). This asks whether a sensible spoofer can be stopped,
not whether a wasteful one can.

**Cells.** For each c in {0, 0.5, 1, 1.5, 2}, 100 honest-vs-honest games (H–H, 200 honest
decisions) and 100 honest-vs-invader games (H–I, 100 honest decisions). One claim call and
one game call per honest decision.

**Measured quantities, per c.**

| Symbol | Meaning | How it is measured |
|---|---|---|
| r | honest report rate | fraction of honest claim calls that chose to report, pooled over both cells |
| pR | honest cooperation when the partner reported | cooperation rate of the honest player in the H–I cell, whose partner always reported |
| pN | honest cooperation when the partner stayed silent | cooperation rate of honest players in H–H games whose partner did not report, averaged over the player's own report |
| HH | honest net payoff against an honest partner | mean over the 200 honest player-games in the H–H cell of (game payoff − c if the player reported) |
| HI_R | honest net payoff against a reporting invader | the same mean over the 100 honest player-games in the H–I cell |

Net payoff means the game payoff minus the claim cost if the player reported.

pN is not one group but a weighted mix of two, because an honest agent facing a silent
partner may itself have reported or not, and those are different prompts:

```
pN = r · p(cooperate | I reported, partner silent) + (1 − r) · p(cooperate | neither reported)
```

The weights are the honest report rate r at that c, so pN is the cooperation a silent
partner meets from a typical honest agent. pR needs no such mixing because it is read from
the H–I cell, where the honest agent's own report varies naturally within the sample.

**Derived quantities, per c.** No cell was run with a silent invader, so the invader's two
options and the honest payoff against a silent invader are computed from honest behaviour
that was observed. This is valid because the honest agent's prompt depends only on the two
reports, not on the partner's type, so honest play against a silent invader is the same as honest play
against a silent honest partner.

| Symbol | Meaning | Formula |
|---|---|---|
| IH_R | invader payoff against an honest partner when the invader reports | 1 + 2·pR − c |
| IH_N | invader payoff against an honest partner when the invader stays silent | 1 + 2·pN |
| HI_N | honest payoff against a silent invader | (1 − pN) − c·r |
| II | invader payoff against an invader | 1 − c if both report, 1 if silent |
| c_I | the invader's break-even cost | 2·(pR − pN) |

The "1 + 2·p" form comes from the defector earning 1 against a defector and 3 against a
cooperator, so each cooperating partner adds 2. The honest agent against a silent defector
earns 1 when it defects and 0 when it cooperates, and has already paid c with probability r
because it chose to report before seeing the partner.

**Population quantities.** Let f be the fraction of invaders in the population, with random
pairing. The *invader advantage* g(f) is the mean invader payoff minus the mean honest
payoff at that f. With two types g is linear in f, so its two ends determine the dynamics:
g(0) = IH − HH asks whether a rare invader spreads in an honest population, and
g(1) = II − HI asks whether honest agents can re-enter an invader population. Under
*replicator dynamics* (each type's share grows in proportion to its payoff advantage over
the average) both ends positive means the population goes to all-invader from any start.

**Rational-invader rule.** The invader's report helps only against honest partners, met with
probability 1 − f, so it pays when 2·(1 − f)·(pR − pN) > c. The invader type is scored as
reporting at a given f only when this holds. "Invader reports when rare" means the
inequality holds at f = 0, that is c < c_I.

**Intervals.** Report rates carry Wilson 95% intervals. Everything built from payoffs
carries a bootstrap 95% interval from 2,000 resamples of the games within each cell.

## Results

**Honest behaviour and the measured payoffs.**

| c | r (Wilson 95%) | pR | pN | HH | HI_R |
|---|---|---|---|---|---|
| 0 | 0.93 (0.90–0.96) | 0.89 | 0.52 | 1.83 | 0.11 |
| 0.5 | 0.66 (0.61–0.71) | 0.75 | 0.29 | 1.23 | −0.08 |
| 1 | 0.48 (0.43–0.54) | 0.74 | 0.19 | 0.97 | −0.15 |
| 1.5 | 0.25 (0.20–0.30) | 0.70 | 0.06 | 0.85 | −0.09 |
| 2 | 0.19 (0.15–0.24) | 0.73 | 0.06 | 0.80 | −0.17 |

**The invader's options and the advantage.**

| c | IH_R | IH_N | c_I | invader reports when rare? | g(0) (95%) | g(1) (95%) | resamples ending all-invader |
|---|---|---|---|---|---|---|---|
| 0 | 2.78 | 2.04 | 0.74 | yes | +0.95 (0.82–1.09) | +0.52 (0.20–0.88) | 99.6% |
| 0.5 | 2.00 | 1.57 | 0.93 | yes | +0.77 (0.59–0.94) | +0.62 (0.52–0.73) | 100% |
| 1 | 1.48 | 1.38 | 1.10 | yes | +0.52 (0.38–0.70) | +0.68 (0.58–0.77) | 100% |
| 1.5 | 0.90 | 1.13 | 1.27 | no | +0.28 (0.21–0.37) | +0.43 (0.35–0.53) | 100% |
| 2 | 0.46 | 1.12 | 1.34 | no | +0.32 (0.23–0.41) | +0.45 (0.34–0.55) | 100% |

**Two crossings in c.** The honest report rate falls through one half at c = 0.95
(bootstrap 0.84–1.07). The invader's report stops paying, c_I(c) = c, at c = 1.15
(0.82–1.37).

## What the results say

**Hypothesis H3a is confirmed.** The invader advantage is positive at both ends at every
cost level, so the replicator ends all-invader in essentially every bootstrap resample. No
flat cost in the grid restores cooperation.

**The ordering prediction held, with a narrow band.** Theory said honest agents, who gain
at most 1 point from a report that works, would stop reporting around c = 1, while an
invader, who gains at most 2, would keep reporting until c approached 2. Honest reporting
did halve at c of about 0.95. The invader's break-even came at about 1.15 rather than near 2,
because a report buys only about 0.65 extra cooperation here (pR − pN), not the 0.87 that
the free-claim experiment C2 had suggested. The band in which only spoofers would report
therefore runs from roughly 1 to 1.15.

**Above its break-even the invader goes silent and still wins.** At c = 1.5 a silent
invader earns 1.13 against honest agents, because they cooperate with a silent partner only
6% of the time. The honest agents earn 0.85 against each other, below the 1.0 they would
earn with no claim mechanism at all. The gap of 0.28 decomposes into 0.37 of fees the
honest agents pay and the invader does not, plus 0.13 of residual exploitation, minus 0.22
that the honest agents gain by cooperating among themselves. The cost has become a tax on
the honest type.

**Paying more buys no more trust.** Honest cooperation with a reporting partner is 0.89 at
c = 0 and then flat at 0.70 to 0.75 for every positive c. The model does not read an
expensive report as stronger evidence than a cheap one. This is the second reason a flat
cost cannot separate the types: the signal's value to its receiver does not rise with its
price.

**The c = 0 level replicates C2.** With a free claim, HH is 1.83 against C2's 1.87 and
honest cooperation against the invader is 0.89 against 0.85, so the added cost paragraph
and the separate claim call change nothing on their own.

## Across models

The same ten cells were run on Claude Sonnet 5.5 and Opus 5.5 through the API
(`runs/api_d1`, adaptive thinking at low effort, no prefill; figures
`figures/d1_costly_claim_claude-sonnet-5-5.png` and `..._claude-opus-5-5.png`, numbers in
`runs/api_d1/analysis_<model>.csv`).

| c | r (Qwen / Sonnet / Opus) | HH | g(0) |
|---|---|---|---|
| 0 | 0.93 / 0.89 / 1.00 | 1.83 / 1.78 / 1.99 | +0.95 / +0.91 / +0.89 |
| 0.5 | 0.66 / 0.12 / 0.38 | 1.23 / 1.01 / 1.12 | +0.77 / +0.76 / +0.18 |
| 1 | 0.48 / 0.05 / 0.00 | 0.97 / 1.00 / 1.00 | +0.52 / +0.42 / 0 |
| 1.5 | 0.25 / 0.02 / 0.00 | 0.85 / 0.99 / 1.00 | +0.28 / +0.01 / 0 |
| 2 | 0.19 / 0.02 / 0.00 | 0.80 / 0.965 / 1.00 | +0.32 / +0.035 / 0 |

Honest reporting halves at c = 0.95 (Qwen), 0.26 (Sonnet) and 0.41 (Opus); the invader's
report stops paying at 1.15, 1.46 and 0.67. The conclusion is the same on all three: the
rare invader's advantage is never negative. The route differs. Qwen keeps paying for
reports that buy nothing and is taxed below mutual defection. The Claude models stop
reporting at the first positive cost, so from c = 1 nobody reports, HH returns to exactly
1.00, the two types play alike and the advantage is zero (labelled "neutral"). On both
routes the cooperation the claim produced at c = 0 is gone by c = 0.5. Two notes on
Opus: at c = 0 it reported in all 200 decisions, so pN is unobserved there and the invader
is scored as reporting, which it did; and it cooperates with a reporting partner almost
only when it reported itself (1.00 given its own report, 0.28 when it declined), so its
pR is mostly that mixture.

## Caveats

- One of 1,500 honest decisions was excluded (a claim call at c = 1 that ran past its
  token limit). No answers were truncated.
- pR rests on 100 decisions at every c, because the H–I cell's partner always reports.
  pN has no cell of its own and comes from the H–H decisions whose partner happened not
  to report, so its sample size follows the honest report rate:

  | c | honest decisions facing a silent partner | of which the agent itself reported |
  |---|---|---|
  | 0 | 11 | 9 |
  | 0.5 | 67 | 47 |
  | 1 | 95 | 53 |
  | 1.5 | 152 | 34 |
  | 2 | 164 | 34 |

  pN is therefore best estimated at high c, where the rational invader goes silent and pN
  matters most, and worst at c = 0, where nearly everyone reports. The wide band on the
  silent-invader line at c = 0 in panel B is this. It reaches panel C only at the
  common-invader end, g at f → 1 (the orange line), where at c = 0 the invader is silent
  and g(1) reduces to pN itself (the orange point in panel C and the green point in panel
  A coincide there); the rare-invader end at c = 0 uses pR and is unaffected. Even the
  bottom of that interval (g(1) = 0.52, bootstrap 0.20 to 0.88) is well above zero, so the
  imprecision does not change the sign, and the sign is all the end-state classification
  uses. The bootstrap resamples whole games, so these sample sizes are already reflected
  in every interval.
- The invader in the run always reported. The silent-invader payoffs are derived from
  honest behaviour against silent honest partners, which the identical-prompt argument
  justifies but which was not run as its own cell. The dotted line in panel C shows the
  always-report invader for comparison; at c = 2 it would lose, which is the reading the
  rational-invader rule exists to prevent.
- One model, one game, one prompt wording. A rewording in an earlier check moved
  cooperation by about six points, so differences of that size between templates are not
  interpreted; the comparisons here are all within one template.
