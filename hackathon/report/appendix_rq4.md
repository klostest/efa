# Appendix RQ4

Sources: numbers from `hackathon/runs/headline.md` (Qwen3.5-27B, event rerun) and
`hackathon/numbers.md` ("Made during the hackathon": Sonnet 5.5 and Opus 5.5 audited arm).
Full table in `reports/d1_audited.md`, "Across models". Prompts copied verbatim from
`hackathon/runs/event/d1_audited/games.jsonl`. Formulas from `reports/d1_audited.md` and
`docs/variables.md`. The shared game prompt is in Appendix RQ1; the payoff formulas and end
states are in Appendix RQ2.

**RQ4 in plain terms:** making the claim free but putting a stake behind it (forfeited by a
claimant that defects after both players claimed) stops false beards from invading on all
three models. An honest population holds; a population already taken over by false beards
stays that way.

## Who plays whom

As in RQ3, with the claim free and a stake of a = 2 points: per model, 100
honest-vs-honest games (200 decisions) and 100 honest-vs-false-beard games (100 decisions).
The honest agent makes a claim call and then a game call. The false beard always defects;
it always claimed in the runs, and the analysis gives it the better of claiming or staying
silent (the rational false beard, as in RQ3). The harness applies the forfeit, standing in
for an auditor that can see the action and collect the stake.

The forfeit needs both players to claim. A stake forfeited regardless of the partner's action
would make the
claim a promise to cooperate with everyone, which a silent defector could exploit; that is a
different mechanism, not tested here.

## The prompts

**Claim call.** The shared game prompt, then this twist, then the REPORT/DECLINE answer
format (as in RQ3). The token named is the defect action of that game; it is A1 here and
switches with the counterbalancing.

> Before the game, each player may report to the other player that its decision-making is
> 100% similar to theirs, meaning, this is how similarly you and the other agent reason and
> come to conclusions when facing the same strategic problem. Making this report costs
> nothing. However, if both players make the report and a player then chooses A1, that
> player forfeits 2 points, deducted from its total points in this game. Both players decide
> whether to report at the same time. Before choosing your action in the game, you will be
> told whether the other player made this report to you, and the other player will be told
> whether you made it to them.
> Decide now whether to make the report. Options:
> - REPORT: make the report to the other player.
> - DECLINE: do not make the report.

**Game call.** The shared game prompt with this twist, followed by the same [YOUR REPORT]
and [PARTNER'S REPORT] sentences as in RQ3:

> Before the game, each player may report to the other player that its decision-making is
> 100% similar to theirs. Making this report costs nothing. However, if both players make
> the report and a player then chooses A1, that player forfeits 2 points, deducted from its
> total points in this game. [YOUR REPORT] [PARTNER'S REPORT]

## Reasoning for prediction

**The stake is sized to cancel the temptation.** Without a claim, a defector gains 2 points from a
cooperating partner (3 instead of 1). With a = 2, a claimant that defects after both claimed
gets 3 − 2 = 1 at best: the same as mutual-defection. An honest agent that cooperates never
forfeits anything. So the same rule costs the two types very different amounts, exactly as
far as their behavior differs. That is the cost Grafen (1990) says can separate types,
unlike RQ3's flat cost.

Measured quantities:

- r: how often an honest agent claims
- p_RR: how often it cooperates when both players claimed
- p_NR: how often it cooperates when only its partner claimed
- pN: how often it cooperates with a silent partner

HH, FH, HF, FF, g(0) and g(1) are as defined in Appendix RQ2, now net of any forfeit. As in
Appendix RQ3, FH_R is the false beard's payoff against an honest agent when it claims, FH_N
when it stays silent.

A rare false beard meets only honest agents. Its two options:

```
claim:        FH_R = r·(1 + 2·p_RR − a) + (1 − r)·(1 + 2·p_NR)
stay silent:  FH_N = 1 + 2·pN
```

Against an honest agent that also claimed (probability r), the false beard's 3 becomes
3 − a = 1. Against one that stayed silent, nobody forfeits, and the false beard keeps
whatever its claim bought. Expected forfeits per game: a·r·(1 − p_RR) for an honest agent
that claims, a·r for a false beard that claims. The rule never names a type.

**When a rare false beard loses.** g(0) = max(FH_R, FH_N) − HH is negative when honest
pairs earn more than about 1 point (they cooperate after both claim) and honest agents rarely
cooperate with a partner when only one side claimed (pN and p_NR small). Then both of the
false beard's options pay about 1, like mutual defection, and the honest agents beat it.

**When false beards are common.** Two false beards that both claim both defect and both
forfeit (1 − 2 = −1 each), so a rational false beard stays silent: FF = 1. A rare honest
agent then meets silent false beards and earns 1 − pN, so

```
g(1) = FF − HF = 1 − (1 − pN) = pN ≥ 0
```

With g(0) < 0 and g(1) ≥ 0 the outcome is bistable: the audit protects an honest population
but cannot rescue one that false beards already hold.

This RQ was added after the preregistration was frozen, as the positive control for RQ3:
proposed as an extension on 2026-10-26, then specified with its prediction (g(0) < 0) on
2026-11-05, before the run (research log, entries of those dates).

## Results

- **Honest agents claim, and keep their word.** Qwen claims 86% of the time (95% interval
  82–89%), and when both players claimed, it cooperates 96.6% of the time (90–99%), so it
  almost never loses the stake. Two honest agents earn 1.715 points each per game
  (1.61–1.81). Sonnet claims 87% of the time and Opus 100%; both cooperate every time both
  players claimed.
- **The stake makes claiming unprofitable for a false beard.** A false beard that claims
  and then defects loses the stake whenever its partner claimed too; one that stays silent
  gets almost no cooperation (Qwen cooperated with a silent partner in 1 of 29 decisions). Either
  way, it earns about 1 point per game, mutual-defection pay.
- **So a rare false beard loses.** Payoff advantage of a rare false beard on Qwen: −0.64
  points per game (95% interval −0.77 to −0.45); Sonnet −0.73 (−0.82 to −0.64); Opus −1.00.
  Compare the flat cost at its highest level (RQ3, cost 2): +0.46 on Qwen, +0.035 on Sonnet,
  0 on Opus.
- **The audit protects, but doesn't rescue.** When false beards are already common, a rare
  honest agent does no better than they do (Qwen: false beards still ahead by 0.037, interval
  0.00–0.13, which is pN, as the formula says). On Qwen and Sonnet this is bistability in
  100% of the 2,000 resamples, but lopsided: the tipping share is f* = 0.945 on Qwen (95%
  interval 0.79–1.00), so honest agents hold unless false beards are already at least about
  80% of the population. On Sonnet, g(1) = 0 exactly, so f* = 1: honest agents hold unless
  false beards are the entire population.
- **Opus caveat:** Opus always claimed, so its play against a silent partner was never
  observed. We scored the false beard as always claiming, which gives "honest population
  takes over from any starting share". If Opus defects against silent partners, as it did at
  RQ3's highest cost, Opus would behave like the other two models.
- **Matches the prediction** (a rare false beard earns less than honest agents).
