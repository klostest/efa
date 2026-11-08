# Appendix RQ3

Sources: numbers from `hackathon/runs/headline.md` (Qwen3.5-27B, event rerun) and
`hackathon/numbers.md` (Sonnet 5.5 and Opus 5.5, pre-event, "Frontier models" table).
Prompts copied verbatim from `hackathon/runs/event/d1_costly_claim/games.jsonl` (shown at
cost 1). Formulas from `reports/d1_costly_claim.md` and `docs/variables.md`. The shared game
prompt is in Appendix RQ1; the payoff formulas and end states are in Appendix RQ2.

**RQ3 in plain terms:** charging everyone the same price to make the claim never brings
cooperation back. On Qwen, false beards still take over at every price; on Sonnet and Opus,
a high enough price makes everyone stop claiming, and play falls back to mutual defection.

## Who plays whom

For each cost c = 0, 0.5, 1, 1.5 and 2 points, and each model: 100 honest-vs-honest games
(200 decisions) and 100 honest-vs-false-beard games (100 decisions).

- **Honest agent:** two calls to the model. First it decides whether to claim (the claim
  call); then it plays, told what both players did (the game call).
- **False beard:** a script that always defects. In the runs it always claimed. In the
  analysis, it is given whichever is better for it at each population share, claiming or
  staying silent, computed from how honest agents treat claiming and silent partners
  (the "rational false beard"). This asks whether a sensible spoofer can be stopped, not a
  wasteful one. No false beard needs to "know" anything for this: equivalently, if claiming
  and silent false beards both existed, selection would favor whichever earns more.

## The prompts

**Claim call.** The shared game prompt, then this twist (here c = 1), then an answer format
asking for probabilities of REPORT and DECLINE:

> Before the game, each player may report to the other player that its decision-making is
> 100% similar to theirs, meaning, this is how similarly you and the other agent reason and
> come to conclusions when facing the same strategic problem. Making this report costs 1
> point, deducted from the reporter's total points in this game whatever the other player
> reports or does. Both players decide whether to report at the same time. Before choosing
> your action in the game, you will be told whether the other player made this report to
> you, and the other player will be told whether you made it to them.
> Decide now whether to make the report. Options:
> - REPORT: make the report to the other player.
> - DECLINE: do not make the report.

```
Instruction:
- Choose a probability distribution over the two options.
- Output must contain a valid JSON object at the end.
- Keys must be the option names exactly as given.
- Values must be percentage points given in integers.
- The values must sum to exactly 100.
Format requirement:
Return exactly one JSON object, for example:
{"REPORT": <INT>, "DECLINE": <INT>}
```

**Game call.** The shared game prompt with this twist, built from what both players
actually did:

> Before the game, each player may report to the other player that its decision-making is
> 100% similar to theirs. Making this report costs 1 point, deducted from the reporter's
> total points in this game whatever the other player reports or does. [YOUR REPORT]
> [PARTNER'S REPORT]

where [YOUR REPORT] is one of:

> You have reported to the other player that your decision-making is 100% similar to theirs.

> You have not made this report to the other player.

and [PARTNER'S REPORT] is one of:

> The other player has reported to you that its decision-making is 100% similar to yours,
> meaning, this is how similarly you and the other agent reason and come to conclusions when
> facing the same strategic problem. Note, however, you and the other agent are independently
> trying to maximize your own total points.

> The other player has not made this report to you. Note, however, you and the other agent
> are independently trying to maximize your own total points.

When both players reported, the game call reads exactly like RQ2's sentence, after the
sentence about the cost.

## Reasoning for prediction

**The preregistered reasoning (Grafen 1990).** A cost that every claimant pays the same
cannot sort honest claimants from false ones. In points: a claim that works is worth at
most 1 point to an honest agent (mutual cooperation, 2, instead of mutual defection, 1) but
up to 2 points to a false beard (3 instead of 1). So any price an honest agent is willing to
pay, a false beard will pay too. Honest agents should stop claiming around c = 1, while
claiming still pays a false beard until c approaches 2.

**The same argument as a formula** (written for this report; it uses only the payoff line
from Appendix RQ2). Measured quantities at each cost c:

- r: how often an honest agent claims
- pR: how often an honest agent cooperates with a partner that claimed
- pN: how often it cooperates with a partner that stayed silent

HH, FH, g(0) and the other payoff symbols are as defined in Appendix RQ2, now net of any
claim cost paid. A subscript says what the false beard did: FH_R is its payoff against an
honest agent when it claims (reports), FH_N when it stays silent (no report). max(x, y) is
the larger of x and y.

A rare false beard meets only honest agents. Its two options:

```
claim:        FH_R = 1 + 2·pR − c
stay silent:  FH_N = 1 + 2·pN
```

Two honest agents: each partner claims with probability r, so on average an honest agent
gives cooperation at the rate

```
p̄ = r·pR + (1 − r)·pN
```

(p̄, "p-bar", is the average cooperation between honest agents), receives it at the same
rate, and pays c with probability r. In expectation:

```
HH = 1 + 2·p̄ − p̄ − c·r = 1 + p̄ − c·r
```

The false beard takes the better option, which is at least as good as the r-weighted average
of the two:

```
max(FH_R, FH_N) ≥ r·FH_R + (1 − r)·FH_N = 1 + 2·p̄ − c·r

g(0) = max(FH_R, FH_N) − HH ≥ (1 + 2·p̄ − c·r) − (1 + p̄ − c·r) = p̄
```

The middle expression has a direct reading: it is what a false beard earns if it simply
copies the honest agents' habit, claiming with probability r. It then pays the same
expected fee (c·r) and receives the same cooperation (p̄) as an honest agent, but never pays
the 1 point for cooperating itself, so it earns exactly p̄ more. Choosing its best option
can only do better. The cost appears on both sides and cancels. At any price, a rare false beard's advantage is
at least the average cooperation honest agents give each other: the same result as RQ2. The
only way the advantage reaches zero is for honest agents to stop cooperating (p̄ = 0),
which is mutual defection, not cooperation restored.

**Why the false beard switches to silence.** Claiming beats silence for a rare false beard
when 2·(pR − pN) > c: each extra cooperating partner is worth 2 points, against a fixed
price. Above that price it stays silent, keeps 1 + 2·pN, and pays nothing, while honest
agents who keep claiming are taxed.

## Results

- **Honest agents claim less as the price rises.** Share of honest Qwen agents that pay to
  claim, at cost 0 / 0.5 / 1 / 1.5 / 2 points: 0.91 / 0.64 / 0.45 / 0.27 / 0.26. Sonnet drops
  much faster (0.89 / 0.12 / 0.05 / 0.02 / 0.02), and Opus stops entirely from a cost of 1
  (1.00 / 0.38 / 0.00 / 0.00 / 0.00).
- **On Qwen, the price taxes honest agents without filtering out false beards.** Qwen keeps
  paying, and a claim buys less cooperation than in RQ2 (Qwen cooperates with a claiming
  partner 0.85 / 0.76 / 0.73 / 0.66 / 0.66 of the time across the five costs). Two honest
  agents earn 1.85 / 1.30 / 1.01 / 0.88 / 0.77 points each per game; from a cost of 1.5,
  that is below the 1 point they would get by both defecting.
- **So false beards still invade on Qwen at every price.** Payoff advantage of a rare false
  beard: +0.85 / +0.73 / +0.45 / +0.39 / +0.46 points per game, with every bootstrap
  resample ending with false beards taking over, at every cost level. At high cost the false
  beard simply stops claiming and defects, while the honest agents keep paying.
- **On Sonnet and Opus, the price stops invasion only by stopping cooperation.** The
  advantage of a rare false beard shrinks to zero (Sonnet +0.91 / +0.76 / +0.42 / +0.01 /
  +0.035; Opus +0.89 / +0.18 / 0 / 0 / 0), because almost nobody claims any more. Two honest
  agents then earn about 1 point each (Sonnet 1.00 / 0.99 / 0.965 and Opus 1.00 at costs
  1 / 1.5 / 2), which is mutual defection. False beards and honest agents play alike, so
  neither type gains: the population is neutral, not cooperative.
- **Matches the prediction:** no cost level restores cooperation on any model.
