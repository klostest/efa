# Preregistration: False beards (EFA screen 1)

Draft 2026-10-15 by Claude from the approved plan; to be edited by Steve and frozen before
the first full run. Changes after freezing are logged in `research_log.md`.

## Research questions
RQ1. Does a self-reported similarity claim induce cooperation as strongly as an
environment-reported (oracle) similarity score at the same stated level?
RQ2. Do agents that claim high similarity and always defect ("false beards") out-earn honest
agents, and does replicator dynamics on the measured payoffs predict they take over?
RQ3. Do two biologically motivated defenses restore cooperation against false beards: (a) a
flat cost attached to the claim; (b) a secret cue drawn from a rotating pool?

## Hypotheses (directional, stated before data)
- H1. At stated similarity 80%, cooperation under C1 (claim) is within 10 percentage points of
  cooperation under C0 (oracle) for the carrier model.
- H2. In C2 at invader frequency 10% and 30%, mean invader payoff exceeds mean honest payoff
  (invasion fitness > 0), and the bootstrapped replicator analysis assigns > 90% of runs to an
  all-invader end state.
- H3a. A flat claim cost c does not restore cooperation at any c in {0, 0.5, 1, 1.5, 2}.
  Secondary prediction (Grafen): the fraction of honest agents that choose to claim falls
  sharply between c = 0.5 and c = 1.5, while false beards keep claiming until c approaches 2.
- H3b. With a rotating secret cue, cooperation among honest agents rises with pool size k in
  {1, 4, 16} and the invader advantage falls with k; with invaders that reuse observed tokens,
  the k = 1 case collapses to the C2 level.

## Design
Game: one-shot symmetric Prisoner's Dilemma, payoffs CC 2/2, CD 0/3, DC 3/0, DD 1/1, the
prompt wrapper and JSON probability answer format of Kundu et al. 2026 (Appendix J).
Agents: temperature 1, one sampled action per stated distribution. Reasoning channel (decided
2026-10-16 after four pilots, see the research log): the model's native thinking mode with a
2,000-token thinking budget, the local analog of the paper's "low" reasoning effort. If the
model has not closed its thinking by the budget, the harness closes it and prefills the
opening of the JSON answer; the forced-close rate is reported per cell. The prompt carries no
visible chain-of-thought instruction (with thinking on it made the model re-derive its answer
twice). Answers cut by the token cap are excluded, never format-fixed, and the exclusion rate
is reported per cell; a cell above 5% is rerun or flagged.
Carrier model: Qwen3.5-27B 4-bit (mlx); second model Qwen3-8B 4-bit if it passes the gate.
Validation model: Claude Haiku 4.5 via API on the headline cells.
Counterbalancing: action label order and outcome-line order alternate across samples. Fixed
seed per cell.

Conditions and cells: see plan table (C0 six levels × 2 models at N=30; C0 vs C1 at 80% ×
2 models at N=100; C2 at 10% and 30% × 2 models at N=100; D1 five costs and D2 three pool
sizes at 30% invaders on the carrier at N=100; API validation three cells at N=50).

## Outcome measures
Primary: realized cooperation rate per cell (binomial, with Wilson intervals).
Secondary: mean stated cooperation probability; welfare; exploitation rate; invader advantage;
replicator end-state distribution over 1,000 bootstrap resamples of the payoff matrix.

## Analysis
Two-proportion z-tests for H1 (equivalence framed as a 10-point margin) and for pairwise cell
comparisons; bootstrap intervals for invader advantage; replicator dynamics (Taylor–Jonker)
from each bootstrapped matrix until convergence, counting end states.

## Controls
Positive: always-cooperate agents give ~100% cooperation end to end. Negative: always-defect
agents give ~0%. Base and "?" arms from the paper reproduce their ordering.

## Exclusions
Answers that fail JSON parsing after one repair attempt are excluded; the exclusion rate is
reported per cell and must be under 5% for a cell to be interpreted.

## What was built before the event
Harness, pilots, and the pre-event overnight run, all disclosed. The reported matrix is
rerun from a cleared cache during the event.
