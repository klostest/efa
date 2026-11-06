# D1-audited: a stake only a defecting reporter forfeits stops false beards

Companion to `figures/d1_audited.png`. Run `runs/d1_audited` (2026-11-05 22:51 to 2026-11-06
03:05, 4.2 h), analysis `scripts/d1_audited_analysis.py`, numbers in
`runs/d1_audited/analysis.csv`; `runs/d1_audited/comparison.csv` holds the same columns for
D1's c = 0 and c = 2 cells, recomputed from `runs/d1_costly_claim` with this arm's split by
the agent's own report. Model: Qwen3.5-27B (4-bit, local), native thinking with a
2,000-token budget, temperature 1. The frontier models (Claude Sonnet 5.5 and Opus 5.5)
have not yet run this arm; the across-models section is a placeholder. Every symbol below
is also in the project's master list, `docs/variables.md`. The arm is specified as H3c in
`docs/draft_experiment_plan.md`, section 3.

## Definitions

**The game.** Two players play a one-shot Prisoner's Dilemma. Each chooses to cooperate (C)
or defect (D). The payoffs are: both cooperate, 2 each (R); both defect, 1 each (P); a
cooperator against a defector gets 0 (S) and the defector gets 3 (T). Two facts about these
numbers are used throughout. A defector earns 1 against a defector and 3 against a
cooperator, so its payoff is 1 + 2·[partner cooperates]. And cooperating instead of
defecting costs exactly one point whatever the partner does (2 against 3, 0 against 1).

**The claim and the stake.** Before the game, each player may report to the other that its
decision-making is 100% similar to theirs. The report is free. If both players made the
report and a player then defects, that player forfeits a stake of a = 2 points, deducted
from its score in that game. A report that only one player made forfeits nothing, for
either player. Both players decide at the same time, and each is then told whether the
other reported before choosing its action. The forfeit is applied by the harness, which
stands in for an auditor that can see the action and collect the stake.

Why the forfeit needs both reports: a stake that a reporter forfeits whoever its partner
is would make the report a promise to cooperate with everyone, and a silent defector would
collect 3 from every such promise. That is a different mechanism (a commitment with no
counterparty) and is not tested here. With both reports required, a reporting pair is in a
mutual contract and a one-sided report is the free claim that D1 studied at c = 0.

**Types.** An *honest* agent is the language model playing the game: one call with the
rules and the report option decides whether to report, and a second call with the rules
and both players' reports decides its action. Both answers are probability distributions
that the harness samples from. An *invader* (false beard) is a fixed rule in the harness:
it always defects. In the run it also always reported, so the H–I cell shows what an honest
agent does when a reporting partner defects. In the analysis the invader's payoff against
honest agents is computed from the honest agents' measured responses to a reporting partner
and to a silent one, and the invader is given the better of the two at each invader
frequency (the rational-invader rule, as in D1). The question is whether a sensible spoofer
can be stopped, not whether a wasteful one can.

**Cells.**

| Cell | Partner | Games | Honest decisions | Calls | Gives |
|---|---|---|---|---|---|
| H–H | honest | 100 | 200 | 400 | r, HH, pN, and a check of p_RR |
| H–I | invader: always reports, always defects | 100 | 100 | 200 | p_RR, p_NR, HI_R, IH_R |

Invader against invader needs no calls: if both report, both defect and both forfeit, so
each earns 1 − a = −1; if both are silent, each earns 1.

**Measured quantities.**

| Symbol | Meaning | How it is measured |
|---|---|---|
| r | honest report rate | fraction of honest claim calls that chose to report, pooled over both cells (300 calls) |
| p_RR | honest cooperation when the agent itself reported and its partner reported | cooperation rate of reporting honest players in the H–I cell (87 decisions); the H–H cell gives an independent check (146 decisions) |
| p_NR | honest cooperation when the agent stayed silent and its partner reported | cooperation rate of silent honest players in the H–I cell (13 decisions); the H–H cell gives a second estimate (25 decisions) |
| pN | honest cooperation when the partner stayed silent | cooperation rate of honest players in H–H games whose partner did not report, whatever the player's own report (29 decisions) |
| HH | honest net payoff against an honest partner | mean over the 200 honest player-games in the H–H cell of the game payoff minus any forfeit |
| HI_R | honest net payoff against a reporting invader | the same mean over the 100 honest player-games in the H–I cell |
| IH_R | reporting invader's net payoff against an honest agent | mean invader payoff in the H–I cell, after its forfeits |

D1's pR (honest cooperation when the partner reported) is the mix r·p_RR + (1 − r)·p_NR.
The split matters here because the forfeit applies only to agents that reported themselves,
so the two groups face different payoff tables.

**Derived quantities.** No cell was run with a silent invader, so the silent invader's
payoff and the honest payoff against it come from honest behaviour toward silent partners,
which was observed in the H–H cell. This is valid because the honest agent's prompt depends
only on the two reports, never on the partner's type.

| Symbol | Meaning | Formula |
|---|---|---|
| IH_N | silent invader's payoff against an honest agent | 1 + 2·pN |
| HI_N | honest payoff against a silent invader | 1 − pN |
| IH_R, written out | reporting invader's payoff against an honest agent | r·(1 + 2·p_RR − a) + (1 − r)·(1 + 2·p_NR) |
| II | invader payoff against an invader | 1 − a if both report, 1 if both are silent |

The written-out IH_R says what the stake does: against the fraction r of honest agents
that reported, the invader's 3 becomes 3 − a; against the rest it keeps whatever its report
bought. The invader's gain from reporting rather than staying silent is therefore

```
IH_R − IH_N = r · [2·(p_RR − pN) − a] + (1 − r) · 2·(p_NR − pN)
```

The first term is at most zero at a = 2, because 2·(p_RR − pN) ≤ 2. The second term is
never negative: in games where the honest partner was silent, nobody forfeits anything and
the report still changes what that partner does. So the report can still pay, by at most
2·(1 − r)·(p_NR − pN), which is small when most honest agents report. (The plan's H3c
section argued that the invader is silent "by construction" at a = 2; that argument used
the first term only and is corrected below under prediction 3.)

**Population quantities.** Let f be the fraction of invaders in a large, randomly paired
population. The *invader advantage* g(f) is the mean invader payoff minus the mean honest
payoff at that f. With two types g is linear in f, so its two ends decide the dynamics
under replicator dynamics (Taylor & Jonker 1978; the equation is in the study guide):
g(0) = IH − HH asks whether a rare invader spreads in an honest population, and
g(1) = II − HI asks whether a rare honest agent spreads in an invader population. At each
f the invader type is scored as reporting or silent, whichever pays more at that f
(the rational-invader rule), with invader–invader pairs counted at 1 − a when reporting
and 1 when silent. End states are read off the signs of g(0) and g(1): all-invader if both
are positive, all-honest if both are negative, bistable if g(0) < 0 and g(1) ≥ 0 (each
pure population resists the other), interior if g(0) > 0 and g(1) < 0.

**Intervals.** Rates carry Wilson 95% intervals. Everything built from payoffs carries a
bootstrap 95% interval from 2,000 resamples of the games within each cell, and the end
state is re-classified on every resample.

## Results

**Honest behaviour and payoffs**, with D1's c = 0 and c = 2 cells beside them (the same
model, the same prompt apart from the cost sentence).

| Quantity | Audited, a = 2 | D1, c = 0 | D1, c = 2 |
|---|---|---|---|
| r | 0.86 (0.82–0.89) | 0.93 | 0.19 |
| p_RR (H–I) | 0.977 (0.92–0.99) | 0.89 | 0.77 |
| p_RR check (H–H) | 0.979 | 0.85 | 0.50 |
| p_NR (H–I; H–H) | 0.23 (0.00–0.47); 0.28 | 0.89 | 0.72 |
| pN | 0.00 (0 of 29) | 0.52 (14 decisions) | 0.06 |
| HH | 1.72 (1.63–1.81) | 1.83 | 0.80 |
| HI_R | 0.08 (0.02–0.15) | 0.11 | −0.17 |
| IH_R | 1.02 (0.94–1.10) | 2.78 | 0.46 |
| IH_N | 1.00 | 2.04 | 1.12 |

**What happened in the games.** In the H–H cell, 73 of the 100 games had both players
reporting; 70 ended in mutual cooperation (2 each) and 3 had one defection (the defector
forfeited, ending at 1 and 0). In the 25 one-sided games the reporter defected every time;
the silent player cooperated in 7 (the reporter took 3) and defected in 18 (1 each). Both
players were silent in 2 games, and both defected. In the H–I cell, 87 honest agents
reported; 85 then cooperated, so the invader's 3 became 1 after the forfeit and the honest
agent got 0; 2 defected, and both players ended at −1. The 13 silent honest agents
defected 10 times (1 each) and cooperated 3 times (the invader took 3 with no forfeit).

**The invader's two options when rare.** Reporting earns 1.02 against honest agents and
silence earns 1.00, so the rational invader reports, by 0.02 with an interval well across
zero. Either way it earns about the mutual-defection payoff.

**The advantage.**

| Quantity | Estimate | 95% | Resamples |
|---|---|---|---|
| g(0), rare invader | −0.70 | −0.80 to −0.58 | negative in 100% |
| g(1), rare honest agent | 0.00 | 0.00 to 0.00 | zero in 100% |
| end state | bistable (classifier label; see below) | | 100% |

For comparison, D1's flat cost of the same two points gave g(0) = +0.32 (0.23–0.41) and
all-invader in every resample; D1 at c = 0 gave +0.95.

## What the results say

**Hypothesis H3c is confirmed.** With the stake, a rare invader earns 0.70 points per game
less than an honest agent, in every bootstrap resample. The honest population holds. The
same two points charged to every reporter (D1, c = 2) left the invader ahead by 0.32;
charged only to a reporter that defects on a reporter, they reverse the sign.

**Why the invader loses, in the numbers.** Honest agents report 86% of the time, and a
reporting honest agent that meets a reporting partner cooperates 98% of the time. So the
reporting invader is cooperated with almost always, collects 3, and forfeits 2 of it in the
86% of games where its partner reported: 1.02 on average. The silent invader is never
cooperated with, because no honest agent in 29 observed decisions cooperated with a silent
partner: 1.00. Honest agents among themselves earn 1.72. The invader has no route to more
than the mutual-defection payoff.

**The end state, precisely.** The classifier says "bistable", its label for g(0) < 0 with
g(1) ≥ 0. Here g(1) is exactly zero, not positive, and the reason is informative. In an
all-invader population the rational invader is silent (reporting would forfeit 2 against
every partner), and a lone honest agent facing silent partners defects (pN = 0), so the two
types play identically and earn the same 1. The all-invader state is a neutral boundary,
not an attractor: at every mixed frequency honest agents earn more (g(f) = −0.72·(1 − f)
under the rational rule), so from any population with any honest agents in it the honest
type takes over. This is stronger than D2, where the honest agent's residual cooperation
with a wrong-word partner (pX = 0.06) made the all-invader state stable and set a tipping
fraction; here pN = 0 removes that cost, and the stake removes the reporting route.

**The registered predictions, scored.**

1. *Honest reporting stays above 0.8.* Confirmed: 0.86 (0.82–0.89), down from 0.93 at
   D1's c = 0. Of the 42 declines, 33 were decided (stated probability of reporting 0),
   8 were 50/50 answers forced by the thinking budget, and 1 was a tail sample of 0.9.
2. *Honest cooperation after both reported is above 0.9.* Confirmed: 0.977 (0.92–0.99) in
   the H–I cell, 0.979 in the H–H cell. All five both-reported defections (3 in H–H, 2 in
   H–I) are forced closes whose transcripts were cut off before they reached the forfeit
   arithmetic; one had got as far as writing "A0, A0: I get 1 − 2 = −1" and was closed
   there. With a longer budget p_RR would be at or near 1.
3. *The rational invader is silent at every f.* **Not confirmed as stated, and the
   derivation was wrong.** The plan compared the report's worth to a defector,
   2·(p_RR − pN) ≤ 2, with the stake a = 2, and concluded the report could never pay. But
   the stake is forfeited only when the partner also reported, so the expected forfeit is
   a·r, not a, and in the (1 − r) games against a silent honest partner the invader keeps
   the whole gain from its report. The correct bound on the report's worth is
   2·(1 − r)·(p_NR − pN), here 2·0.14·0.23 = 0.06; measured, the report is worth +0.02.
   The invader is nearly indifferent rather than silent. The error does not touch the
   conclusion, because the comparison that decides g(0) is between the invader's best
   option (1.02) and HH (1.72); it does mean that "silent by construction" should not be
   repeated, and that at a lower honest report rate a reporting invader could gain more
   from the one-sided games. The plan's H3c section carries a dated correction.
4. *g(0) < 0.* Confirmed, and the prediction at risk did not materialise. The risk was pN:
   D1's c = 0 cell had shown silent partners cooperated with about half the time (0.52
   from 14 decisions), which would have given a silent invader 2.0 against HH. Here pN is
   0 of 29. The transcripts explain the difference. Every reporter facing a silent partner
   wrote out that the forfeit condition "both players make the report" is false, that the
   penalty cannot be triggered, and that defection is therefore dominant; several added
   that a partner that is "100% similar" would reach the same conclusion. The stake gave
   silence a meaning. At D1's c = 0, declining was rare (7%) and carried no information;
   here it is read, correctly, as a partner that kept defection available.
5. *Is an audited report trusted more than a free one?* Yes for the agent that reported
   itself: p_RR rose from 0.89 (D1, c = 0) to 0.977. But the mirror number fell: a silent
   honest agent facing a reporter cooperated 0.89 of the time at D1's c = 0 and 0.23
   here (0.28 in the H–H cell). A one-sided report is the same free claim in both arms,
   and it now buys a quarter of the cooperation it did. The transcripts of decided
   decliners read like the pilot's: an agent declines in order to keep defection
   available, so the silent population is enriched for agents that already meant to
   defect. The report sorts honest agents by intent; the ones who decline act on it.

**The Grafen reading.** Grafen's condition for an honest costly signal is that the signal
costs the low-quality sender more than the high-quality one. D1 charged every reporter the
same c and failed as predicted. This arm has one rule that never mentions types, and the
cost falls on the two types at different rates because they behave differently: an honest
agent that reported forfeits the stake only when its partner reported and it then
defected, a·r·(1 − p_RR) = 2·0.86·0.023 = 0.04 points per game in expectation; the invader
forfeits it whenever its partner reported, a·r = 1.72. The difference, 1.68 points per
game, is the differential cost, and it is exactly the honest agent's cooperation with
reporting partners. In the H–H cell the honest agents paid 6 points of forfeits in 200
player-games.

**What the mechanism costs honest agents.** HH is 1.72 against 1.83 at D1's c = 0. The
forfeits account for 0.03 of that; the rest is the one-sided games, which now mostly end
in mutual defection (1 each) where at c = 0 they mostly ended in cooperation. An honest
agent that meets a reporting invader is still exploited (it cooperates 98% and earns
0.08), so the stake protects the population, not the individual encounter: the invader
gains nothing from the exploitation because the auditor takes it back.

**The practical reading.** In the terms of plan section 7: a similarity claim backed by a
stake that is slashed when the claimant defects on a counterparty who also staked. The
audit is done by the harness here, which assumes an observer that can see the action and
enforce the forfeit. Under that assumption the claim is worth making only by an agent that
intends to cooperate, and a population of this model that uses it repels spoofers from any
starting mixture. This is CoopEval's contract mechanism (outcome-conditional payments)
arrived at from the costly-signalling side, and the write-up should say so.

## Across models

*Added 2026-11-06 during the hackathon.* The same two cells were run on Claude Sonnet 5.5
and Opus 5.5 through the API (`hackathon/runs/api_d1_audited`, adaptive thinking at low
effort, 600 calls per model, 0 exclusions; figures
`hackathon/figures/d1_audited_claude-sonnet-5-5.png` and `..._claude-opus-5-5.png`,
numbers in `hackathon/runs/api_d1_audited/analysis_<model>.csv`, with each model's own
D1 c = 0 and c = 2 cells from `runs/api_d1` beside them in `comparison_<model>.csv`).

| Quantity | Qwen3.5-27B | Sonnet 5.5 | Opus 5.5 |
|---|---|---|---|
| r | 0.86 (0.82–0.89) | 0.87 (0.83–0.91) | 1.00 (0.99–1.00) |
| p_RR | 0.977 (H–I); 0.979 (H–H) | 1.00 (91 of 91); 1.00 (148 of 148) | 1.00 (100 of 100); 1.00 (200 of 200) |
| p_NR | 0.23 (3 of 13); 0.28 (7 of 25) | 0.11 (1 of 9); 0.04 (1 of 23) | undefined (no silent agent) |
| pN | 0 of 29 | 0 of 29 | undefined (no silent partner) |
| HH | 1.72 | 1.745 | 2.00 |
| HI_R, IH_R | 0.08, 1.02 | 0.08, 1.02 | 0.00, 1.00 |
| g(0) | −0.70 (−0.80 to −0.58) | −0.73 (−0.82 to −0.64) | −1.00 |
| g(1) | 0.00 | 0.00 | −1.00 (see note) |
| end state, resamples | bistable, 100% | bistable, 100% | all-honest, 100% (see note) |
| D1 at c = 2, same model: g(0) | +0.32 | +0.035 | 0 (neutral) |

**H3c holds on all three models.** On Sonnet the picture is Qwen's: 87% report, every
reporting pair cooperates, every reporter facing a silent partner defects, and the
reporting invader's 3 becomes 1 against the 87% of partners that reported. On Opus every
honest agent reports and every pair cooperates (HH = 2.00, the maximum), so the invader
earns exactly 1 and the honest agent facing it 0. The same two points as a flat fee left
the invader level or ahead on all three models (D1, c = 2); as a stake they put it
0.7 to 1.0 points behind.

**Two notes on the frontier numbers.**

- *Sonnet's declines are mostly hedges, not decisions.* Its stated probability of
  reporting was 0.90 to 0.97 in 222 of 300 claim calls and 1.0 in 26; only 7 answers
  were a decided decline (0.1). So its 13% silence is largely tail sampling of a hedged
  answer, unlike Qwen, whose decliners declined on purpose. The route still closes for
  the same reason as on Qwen: a silent Sonnet agent facing a reporter notes the forfeit
  cannot trigger and defects (p_NR = 0.11), and a reporter facing a silent partner does
  the same (pN = 0 of 29). The corrected prediction-3 bound, 2·(1 − r)·(p_NR − pN), is
  0.03 on Sonnet; the measured gain from reporting is +0.02, as on Qwen.
- *Opus's "all-honest" label is a scoring convention.* No Opus agent ever stayed silent,
  so honest play against a silent partner is unobserved and the analysis scores the
  invader as reporting at every f; at f = 1 that is two reporting invaders forfeiting
  against each other (II = −1) against an honest agent's 0, hence g(1) = −1. If a silent
  invader were met with defection, as Opus did at D1's c = 2 (pN = 0 of 200), the
  all-invader corner would be neutral, as on the other two models. Either way the honest
  population repels the invader by a full point per game.

Cost: about 20 minutes and a few dollars per model.

## Caveats

- No decision was excluded. Of the 300 claim calls, 297 used the full 2,000-token thinking
  budget and were closed by the harness; of the 300 game calls, 294. This is the channel's
  normal pattern on Qwen (see C0 to D2). Every decision is therefore made from partial
  reasoning, and the specific failures above (the five both-reported defections, the eight
  50/50 claim answers, two of the three silent-honest cooperations in H–I, which also had
  50/50 claim answers) are where the cutoff landed before the relevant step.
- pN = 0 rests on 29 decisions (25 reporters facing a silent partner, 4 silent pairs), all
  with a stated cooperation probability of 0. p_NR rests on 13 decisions in the H–I cell
  and 25 in the H–H cell.
- Prediction 3 was mis-derived in the plan (above). The corrected bound on the invader's
  gain from reporting, 2·(1 − r)·(p_NR − pN), grows as honest reporting falls, so a model
  with a low report rate would need the bound re-checked.
- The invader is scripted and always reported in the run; its silent option is computed
  from honest behaviour toward silent partners, which is valid because the honest prompt
  depends only on the reports. No model-driven spoofer was tested.
- The forfeit is enforced by the harness. The result is conditional on an auditor that
  observes the action; it says nothing about how such an auditor would be built.
- One stake (a = 2), one wording, one model until the frontier replay. The stake is
  conditional on both reports; the unconditional version (a report as a promise to
  everyone) was not run.
- HH differs across the three arms by at most 0.11 among the c = 0 and audited cells,
  which is within the range a rewording moved cooperation in the confound check, so the
  small HH difference is not interpreted beyond the bookkeeping above.
