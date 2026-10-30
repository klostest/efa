# D2: a rotating code word restores the cooperative state

Companion to `figures/d2_secret.png`. Run `runs/d2_secret` (2026-10-29, 3.3 h), analysis
`scripts/d2_analysis.py`, numbers in `runs/d2_secret/cells.csv` and `analysis.csv`.
Model: Qwen3.5-27B (4-bit, local), native thinking with a 2,000-token budget, temperature 1.
The same three cells were run on Claude Sonnet 5.5 and Opus 5.5 (`runs/api_slice`, figures
`figures/d2_secret_claude-sonnet-5-5.png` and `..._claude-opus-5-5.png`); their numbers
appear in the comparison table at the end. Every symbol below is also in the project's
master list, `docs/variables.md`.

## Definitions

**The game.** Two players play a one-shot Prisoner's Dilemma. Each chooses to cooperate (C)
or defect (D). The payoffs are: both cooperate, 2 each (R); both defect, 1 each (P); a
cooperator against a defector gets 0 (S) and the defector gets 3 (T).

**The code word.** In the similarity experiments (C0 to D1) an agent is told, in one
sentence, that the other player's decision-making is similar to its own. D2 replaces that
sentence with a code word. Each player is told that agents whose decision-making is 100%
similar to its own were issued a code word this round, that it presented that word to the
other player, and which word the other player presented back. A matching word is the
similarity claim in a form an honest agent can check; a wrong word is a claim that fails
the check. The words are fresh nonsense tokens (a letter, a digit, a dash, five letters)
drawn anew for every game, so no word recurs and nothing is learned across games.

**The game being simulated.** The real population would issue honest agents a new word
every rotation period τ. A spoofer that captured a word replays it after a delay δ, and the
replay succeeds only if the word is still current. Averaged over the spoofer's timing, a
replay succeeds with probability ρ (for a uniformly timed replay within a period,
ρ = 1 − δ/τ). An honest agent therefore meets a spoofer holding a current word with
probability ρ and a stale one with probability 1 − ρ. Under the biology reading, where
honest agents draw from a pool of k words and the spoofer holds one of them, ρ = 1/k; the
preregistered pool sizes k ∈ {1, 4, 16} are ρ = 1, 1/4, 1/16.

**Why three cells cover every ρ.** The honest agent's prompt depends only on the two words
it sees, never on who the partner is. So its behaviour against a spoofer with a current
word is its behaviour against any partner whose word matches, and against a spoofer with a
stale word it is its behaviour against any partner whose word is wrong. Two measured rates
then give the honest agent's play against a spoofer at any ρ by mixing, and no rotation,
rounds or pool need to be simulated.

**Types.** An *honest* agent is the language model playing the game: one call with the rules
and the code-word twist decides its action, as a probability distribution the harness
samples from. An *invader* (false beard) is a fixed rule in the harness: it always defects.
Its words are supplied by the harness: the current word in the match cell, a different
fresh word in the mismatch cell.

**Cells.**

| Cell | Partner | Words | Games | Honest decisions | Gives |
|---|---|---|---|---|---|
| H–H match | honest | both current | 100 | 200 | pM, HH |
| H–I match | invader | both current | 100 | 100 | check of pM (identical prompt) |
| H–I mismatch | invader | invader's word wrong | 100 | 100 | pX |

**Measured quantities.**

| Symbol | Meaning | How it is measured |
|---|---|---|
| pM | honest cooperation when the words match | cooperation rate over the 200 honest decisions in the H–H match cell |
| pX | honest cooperation when the partner's word is wrong | cooperation rate over the 100 honest decisions in the H–I mismatch cell |
| HH | honest payoff against an honest partner | mean honest payoff per player in the H–H match cell |

**Derived quantities.** A defector earns 1 against a defector and 3 against a cooperator,
so each cooperating partner adds 2, and a cooperator against a defector earns 1 − 1 = 0
instead of 1.

| Symbol | Meaning | Formula |
|---|---|---|
| IH_M, IH_X | invader payoff against an honest agent, word current / wrong | 1 + 2·pM, 1 + 2·pX |
| HI_M, HI_X | honest payoff against an invader, word current / wrong | 1 − pM, 1 − pX |
| IH(ρ), HI(ρ) | the same at replay success ρ | ρ·IH_M + (1 − ρ)·IH_X, and likewise for HI |
| II | invader payoff against an invader | 1 (both defect) |

**Population quantities.** Let f be the fraction of invaders, with random pairing. The
*invader advantage* g(f) is the mean invader payoff minus the mean honest payoff at that
f. With two types g is linear in f, so its two ends decide the dynamics: g(0) = IH(ρ) − HH
asks whether a rare invader spreads in an honest population, g(1) = II − HI(ρ) = pX·(1 − ρ)
+ pM·ρ ≥ 0 asks whether honest agents can re-enter an invader population. Since g(1) is
never negative (an honest agent sometimes cooperates with a defector and never gains from
it), the best achievable outcome is *bistable*: g(0) < 0 and g(1) > 0, so the population
settles at all-honest or all-invader depending on which side of a tipping fraction
f* = g(0)/(g(0) − g(1)) it starts. The *tolerable replay success* ρ* is the ρ at which
g(0) crosses zero; below it the honest population holds. Solving IH(ρ) = HH with
HH = 1 + pM gives ρ* = (pM − 2pX)/(2(pM − pX)), which exists only when pX < pM/2.

**Intervals.** Cooperation rates carry Wilson 95% intervals. Everything built from payoffs
carries a bootstrap 95% interval from 2,000 resamples of the games within each cell; ρ* is
re-measured on every resample as the crossing of g(0).

## Results

**Honest behaviour and payoffs.**

| Quantity | Estimate | 95% |
|---|---|---|
| pM | 0.805 | 0.75–0.87 |
| pM check (H–I match) | 0.82 | 0.74–0.89 |
| check − pM | +0.015 | −0.09 to +0.11 |
| pX | 0.06 | 0.02–0.11 |
| HH | 1.81 | 1.75–1.87 |
| IH_M, HI_M | 2.64, 0.18 | 2.48–2.78, 0.11–0.26 |
| IH_X, HI_X | 1.12, 0.94 | 1.04–1.22, 0.89–0.98 |

**The advantage at the marked replay rates.**

| ρ | reading | g(0) (95%) | g(1) (95%) | f* | end state | resamples bistable |
|---|---|---|---|---|---|---|
| 0 | every replay stale | −0.69 (−0.80 to −0.57) | +0.06 (0.02–0.11) | 0.92 | bistable | 100% |
| 1/16 | k = 16 | −0.59 (−0.70 to −0.48) | +0.11 (0.07–0.16) | 0.85 | bistable | 100% |
| 1/4 | k = 4 | −0.31 (−0.41 to −0.20) | +0.25 (0.21–0.29) | 0.55 | bistable | 100% |
| 1 | never rotates | +0.84 (0.66–0.99) | +0.82 (0.74–0.89) | none | all-invader | 0% (100% all-invader) |

**The threshold.** The measured crossing is ρ* = 0.45 (0.38–0.53); the closed form gives
0.46 (0.42–0.49). The two differ because the measured crossing is read from the
H–H-cell payoff HH directly while the closed form uses HH = 1 + pM; they agree within
sampling error, which is itself a bookkeeping check.

## What the results say

**Hypothesis H3b is confirmed.** With a word that never rotates (ρ = 1) the invader's
advantage is +0.84, the C2 result restated (C2 gave +0.83 with the similarity claim in
words). At both preregistered rotation rates the rare invader loses in every bootstrap
resample, by 0.31 points per game at ρ = 1/4 and 0.59 at ρ = 1/16, so the honest
population holds.

**The practical reading.** An honest population of this model is safe against a rare
spoofer as long as the spoofer's captured word is still current less than 45% of the
time. In the rotation picture that is a replay delay of more than about 55% of the
rotation period; in the pool picture it is a pool of three or more words. The threshold is
set by the two rates: the cooperation a current word buys (0.805) and the cooperation a
wrong word still gets (0.06). Since pX is near zero, ρ* is near its ceiling of one half;
no rotation scheme can tolerate a replay rate above 0.5, because at that point even a
perfectly discriminating honest agent is exploited often enough to lose.

**Bistable, not globally stable.** The defense protects an honest population; it does not
recover one. At ρ = 1/4 a population that is already more than 55% invaders drifts to
all-invader, because honest agents meeting each other are rare and the occasional wrong-word
cooperation (pX) is a pure loss. The tipping fraction rises as ρ falls (0.85 at ρ = 1/16).

**The word is read exactly as intended.** In the mismatch cell every transcript that
reached the twist drew the inference "if they were a copy they would have my word", and
defected. None reasoned about rotation, capture, forgery or repeated play. The code word
works as a verifiable form of the similarity claim and nothing more.

**Across models.** The same three cells on the two frontier models:

| Quantity | Qwen3.5-27B | Sonnet 5.5 | Opus 5.5 |
|---|---|---|---|
| pM | 0.805 (0.75–0.87) | 0.835 (0.79–0.89) | 1.00 |
| pM check | 0.82 | 0.88 | 1.00 |
| pX | 0.06 (0.02–0.11) | 0.00 | 0.00 |
| g(0), ρ = 1 | +0.84 | +1.01 | +1.00 |
| g(0), ρ = 1/4 | −0.31 | −0.34 | −0.50 |
| ρ* measured | 0.45 (0.38–0.53) | 0.47 (0.43–0.52) | 0.50 |

All three sit at or just under the ceiling of one half. The frontier models are sharper on
both sides, cooperating more with a matching word and never with a wrong one.

## Caveats

- No decision was excluded. All but 11 of the 400 calls used the full 2,000-token thinking
  budget and were closed by the harness; 21 then also reached the 300-token answer cap
  after the JSON was complete. This is the channel's normal pattern (see C0 and C2).
- The six cooperations with a wrong word are all forced closes whose transcripts were cut
  off while reading the twist, after spending the budget on the payoff matrix; the answer
  then came from the model's superrational default. Two of the six were tail samples of a
  stated 0.5 and 0.1. pX = 0.06 is therefore the channel's noise floor, not a judgement
  that a wrong word is compatible with similarity; the frontier models, which are not
  budget-limited in this way, give pX = 0.
- pM (0.805) is below the C2 claim rate (0.87) by about the amount a rewording moved
  cooperation in the confound check, so the difference is not interpreted.
- The invader is scripted and its words are harness-supplied, so the result is about
  whether an honest agent can be fooled by a stale word, not about whether a model-driven
  spoofer would find a better attack (guessing the format, claiming a transcription error).
  Those are the audited-claim and wording follow-ups in the plan.
- One game, one prompt wording per model. ρ* depends on pM and pX, which depend on the
  wording; the ceiling of one half does not.
