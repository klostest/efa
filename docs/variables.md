# Master variable list

Every symbol used in the plan, the preregistration, the research log and the reports, with
one meaning each. A symbol is never reused for a second meaning; a new quantity gets a new
symbol and a row here. Grouped by where the symbol is introduced.

## Game and prompts

| Symbol | Meaning | Type / range |
|---|---|---|
| C, D | the two actions, cooperate and defect | action |
| R, S, T, P | Prisoner's Dilemma payoffs: both cooperate 2 each (R), a cooperator against a defector 0 (S), the defector against a cooperator 3 (T), both defect 1 each (P) | points |
| X | similarity level stated in a prompt ("X% similar to yours") | 0–100 % |
| s | similarity as the model writes it in its own break-even rule, "cooperate iff 2s > 1" | 0–1 |
| N | games per cell | count |

Every payoff in the game can be written as `1 + 2·[partner cooperates] − [I cooperate]`,
where the brackets are 1 when true and 0 otherwise. The expected payoff tables below all
follow from this one line. Read against a defector, the partner bracket is 0 and the payoff
is 1 − [I cooperate]: cooperating with a defector costs exactly one point.

## Payoff notation (C2 onward)

Two-letter payoff symbols name the earner first and the partner second: HI is what an
honest agent earns against an invader, IH what an invader earns against an honest agent.
A subscript names the partner's situation as the honest agent saw it. HH and II have no
subscript.

| Symbol | Meaning | Type / range |
|---|---|---|
| HH | mean honest net payoff against an honest partner, measured in the H–H cell | points |
| II | invader payoff against an invader: 1, less any claim cost both paid | points |

## Population and dynamics (C2 onward)

| Symbol | Meaning | Type / range |
|---|---|---|
| f | invader fraction of the population | 0–1 |
| q | probability that a random partner is an invader; q = f·M/(M − 1) in a finite population of M agents, q = f in the large-population limit that the replicator uses | 0–1 |
| g(f) | invader advantage: mean invader payoff minus mean honest payoff when the invader fraction is f. A straight line in f with two types and fixed cell payoffs (note below), so g(0) and g(1) decide the dynamics; piecewise linear in D1 under the rational-invader rule (D1 group below) | points |
| f* | tipping fraction: the f at which g(f) = 0 when g(0) < 0 < g(1) (bistable). Below f* the honest population repels invaders, above it the invaders take over. f* = g(0) / (g(0) − g(1)) | 0–1 |

End states under replicator dynamics: g(0) > 0 and g(1) > 0, all-invader; both negative,
all-honest; g(0) < 0 < g(1), bistable with tipping fraction f*; g(0) > 0 > g(1), a stable
interior mixture. Because cooperating with a defector costs exactly one point (the payoff
identity above), an honest agent in an all-invader population falls short of the invaders'
1 by exactly its probability of cooperating with one, which is why g(1) = II − HI is that
probability and can never be negative.

Why g is a straight line. With random pairing an honest agent meets an invader with
probability f and an honest agent with probability 1 − f, so its expected payoff, call it
W_H(f), is a weighted average of two constants, and likewise W_I(f) for the invader:

```
W_H(f) = (1 − f)·HH + f·HI
W_I(f) = (1 − f)·IH + f·II
g(f)   = W_I − W_H = (1 − f)·g(0) + f·g(1)
```

This is the two-strategy case of "fitness equals the payoff matrix times the frequency
vector" (Nowak, *Evolutionary Dynamics*, chapter 4). It needs the four cell payoffs to be
constants that do not change with f, which holds in C2 and D2. In D1 the invader's payoff
depends on f because the rational-invader rule lets it switch options (D1 group below), so
g is two straight-line pieces with a step between them and the analysis classifies the
end state from g on a grid of f rather than from the two ends alone.

Where f* comes from. Setting the line to zero, (1 − f)·g(0) + f·g(1) = 0, gives
f* = g(0)/(g(0) − g(1)). When g(0) < 0 < g(1) both numerator and denominator are
negative, so f* lies strictly between 0 and 1. From the two-type replicator equation
df/dt = f·(1 − f)·g(f) (study guide, Taylor & Jonker entry), f moves in the direction of
the sign of g: below f* the honest population wins, above it the invaders do, so f* is an
unstable equilibrium, a tipping point. With the signs reversed, g(0) > 0 > g(1), the same
formula gives a stable interior mixture that attracts from both sides.

## D1 costly claim

| Symbol | Meaning | Type / range |
|---|---|---|
| c | cost of the similarity claim, deducted from the reporter whatever happens | points |
| r | honest report rate at a given c | 0–1 |
| pR | honest cooperation rate when the partner reported | 0–1 |
| pN | honest cooperation rate when the partner stayed silent (a mix over the agent's own report, weighted by r) | 0–1 |
| HI_R, HI_N | honest net payoff against an invader that reported / stayed silent | points |
| IH_R, IH_N | invader net payoff against an honest agent when the invader reported / stayed silent: 1 + 2·pR − c and 1 + 2·pN | points |
| c_I | the invader's break-even claim cost, 2·(pR − pN); the invader reports when rare iff c < c_I | points |
| f_switch | the invader fraction above which the rational invader stops reporting, 1 − c/c_I; undefined (always silent) when c ≥ c_I | 0–1 |

The rational-invader rule: the invader reports at invader fraction f iff
2·(1 − f)·(pR − pN) > c, that is iff f < f_switch. Because the honest agent earns HI_R
against a reporting invader and HI_N against a silent one, g steps down at f_switch and is
a straight line only on each side of it (derivation in `reports/d1_costly_claim.md`, "Why
g is not one straight line in D1").

## D1-audited claim (H3c)

| Symbol | Meaning | Type / range |
|---|---|---|
| a | the stake: points a player forfeits if both players made the report and that player then defected. Set to 2 (plan, H3c) | points |
| p_RR | honest cooperation rate when the agent itself reported and its partner reported | 0–1 |
| p_NR | honest cooperation rate when the agent itself stayed silent and its partner reported | 0–1 |

The report is free (c = 0); the stake is the arm's only cost. r, pN, HH, II and the
two-letter payoffs keep their D1 meanings, with the forfeit included in any net payoff.
D1's pR is the mix r·p_RR + (1 − r)·p_NR; the split is needed here because the forfeit
depends on the agent's own report as well as the partner's. The rule never names a type:
an agent that reported and plays honest partners who report at rate r forfeits
a·r·(1 − p_RR) per game in expectation if it is honest and a·r if it is an invader, the
gap being the honest agent's cooperation with reporting partners.

## D2 rotating secret

| Symbol | Meaning | Type / range |
|---|---|---|
| pM | honest cooperation rate when the partner's code word matches the agent's own | 0–1 |
| pX | honest cooperation rate when the partner's code word does not match | 0–1 |
| HI_M, HI_X | honest payoff against an invader whose word matched / did not match: expected 1 − pM and 1 − pX | points |
| IH_M, IH_X | invader payoff against an honest agent when the invader's word matched / did not match: expected 1 + 2·pM and 1 + 2·pX | points |
| ρ (rho) | replay success probability: the probability that a credential an impostor captured earlier is still current when the impostor presents it. ρ = 1, a credential that never rotates; ρ = 0, one that always rotates before it can be replayed | 0–1 |
| τ (tau) | rotation period: how long one credential stays valid | time |
| δ (delta) | replay delay: time between an impostor capturing a credential and presenting it | time |
| ρ* | maximum tolerable replay success: the honest population repels rare invaders iff ρ < ρ*, with ρ* = (pM − 2·pX) / (2·(pM − pX)), which is positive only when pX < pM/2 | 0–1 |
| k | pool size in the biology mapping only (Jansen & van Baalen's beard colours): a pool of k words drawn at random each round gives ρ = 1/k. Not used in the analysis | count |

With capture at a uniformly random moment within a credential's validity window,
ρ = 1 − δ/τ for δ < τ and ρ = 0 otherwise. Payoffs against an invader at a given ρ are
weighted averages of the matched and mismatched cells:
HI(ρ) = ρ·HI_M + (1 − ρ)·HI_X and IH(ρ) = ρ·IH_M + (1 − ρ)·IH_X.

Expected payoffs from the one-line formula, with each honest agent cooperating
independently at its situation's rate and invaders never cooperating:

| Pair | Expected payoff to the first-named player |
|---|---|
| honest vs honest (words match) | 1 + 2·pM − pM = 1 + pM |
| invader vs matched honest | 1 + 2·pM |
| invader vs mismatched honest | 1 + 2·pX |
| honest vs invader, matched | 1 − pM |
| honest vs invader, mismatched | 1 − pX |

The analysis uses measured HH and measured cell payoffs; the expected forms are for
understanding and for deriving ρ*.

Where ρ* comes from. A rare invader (f → 0) plays only honest partners, so its payoff is
IH(ρ) and the honest agents' is HH; g(0) = 0 is IH(ρ) = HH. Using the expected forms:

```
IH(ρ) = ρ·(1 + 2·pM) + (1 − ρ)·(1 + 2·pX) = 1 + 2·[ρ·pM + (1 − ρ)·pX]
HH    = 1 + pM

2·[ρ·pM + (1 − ρ)·pX] = pM
ρ·(pM − pX) = pM/2 − pX
ρ* = (pM − 2·pX) / (2·(pM − pX))
```

In words: the invader matches the honest agents once its partners cooperate with it half
as often as honest agents cooperate with each other, because a cooperating partner is
worth 2 to a defector but only a net 1 to an honest agent, who pays 1 for its own
cooperation. The denominator is positive whenever a wrong word lowers cooperation at all
(pX < pM). The numerator is positive only when pX < pM/2: if honest agents cooperate with
a wrong word more than half as often as with a right one, the invader earns 1 + 2·pX > HH
even when every replay fails, and no rotation rate helps. With pX = 0 the formula gives
ρ* = 1/2, its ceiling: no scheme can tolerate replay success above one half.

## Statistics

| Symbol | Meaning |
|---|---|
| z, p | two-proportion test statistic and its p-value (research log) |
| Wilson 95% | interval on a proportion; used for cooperation and report rates |
| bootstrap 95% | interval from 2,000 resamples of whole games within each cell; used for everything built from payoffs |
