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
follow from this one line.

## Population and dynamics (C2 onward)

| Symbol | Meaning | Type / range |
|---|---|---|
| f | invader fraction of the population | 0–1 |
| q | probability that a random partner is an invader; q = f·N/(N − 1) in a finite population of N agents, q = f in the large-population limit that the replicator uses | 0–1 |
| g(f) | invader advantage: mean invader payoff minus mean honest payoff when the invader fraction is f. Linear in f with two types, so g(0) and g(1) decide the dynamics | points |
| f* | tipping fraction: the f at which g(f) = 0 when g(0) < 0 < g(1) (bistable). Below f* the honest population repels invaders, above it the invaders take over. f* = g(0) / (g(0) − g(1)) | 0–1 |

End states under replicator dynamics: g(0) > 0 and g(1) > 0, all-invader; both negative,
all-honest; g(0) < 0 < g(1), bistable with tipping fraction f*; g(0) > 0 > g(1), a stable
interior mixture.

## Payoff notation (D1 onward)

Two-letter payoff symbols name the earner first and the partner second: HI is what an
honest agent earns against an invader, IH what an invader earns against an honest agent.
A subscript names the partner's situation as the honest agent saw it. HH and II have no
subscript.

| Symbol | Meaning | Type / range |
|---|---|---|
| HH | mean honest net payoff against an honest partner, measured in the H–H cell | points |
| II | invader payoff against an invader: 1, less any claim cost both paid | points |

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

The rational-invader rule: the invader reports at invader fraction f iff
2·(1 − f)·(pR − pN) > c.

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

## Statistics

| Symbol | Meaning |
|---|---|
| z, p | two-proportion test statistic and its p-value (research log) |
| Wilson 95% | interval on a proportion; used for cooperation and report rates |
| bootstrap 95% | interval from 2,000 resamples of whole games within each cell; used for everything built from payoffs |
