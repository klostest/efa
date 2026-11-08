# Appendix RQ5

Sources: numbers from `hackathon/runs/headline.md` (Qwen3.5-27B, event rerun) and
`hackathon/numbers.md` (Sonnet 5.5 and Opus 5.5, pre-event, "Frontier models" table).
Prompts copied verbatim from `hackathon/runs/event/d2_secret/games.jsonl`. Formulas from
`docs/variables.md` ("D2 rotating secret") and `reports/d2_secret.md`. The shared game
prompt is in Appendix RQ1; the payoff formulas and end states are in Appendix RQ2.

**RQ5 in plain terms:** a code word that changes every game stops false beards, as long as
an old word replayed by a false beard works less than about half the time. A word that never
changes is the same as an unverified claim (RQ2), and false beards take over.

## Who plays whom

Three kinds of games, 100 each per model:

- **Honest vs honest, words match** (200 decisions): gives pM, how often an honest agent
  cooperates when the partner's word matches its own.
- **Honest vs false beard, words match** (100 decisions): a false beard whose replayed word
  happens to still be current. The honest agent's prompt is identical to the first kind, so
  this is a second sample of pM, run to measure the payoffs when the types meet.
- **Honest vs false beard, words don't match** (100 decisions): a false beard whose
  replayed word has expired. Gives pX, how often an honest agent cooperates when the words
  differ.

Words are fresh nonsense tokens drawn for every game, so nothing carries over between games.
No rotation, rounds or pool of words are simulated: because the honest agent's prompt
depends only on whether the words match, the two measured rates give its play against a
false beard at any replay success ρ by mixing.

## The prompt

The shared game prompt with this twist (here the words match; in the mismatch games the
second word differs):

> Agents whose decision-making is 100% similar to yours, meaning agents that reason and
> come to conclusions the same way you do when facing the same strategic problem, were
> issued the code word G3-FEZAT this round, and you presented it to the other player. The
> other player presented the code word G3-FEZAT to you. Note, however, you and the other
> agent are independently trying to maximize your own total points.

The "meaning" clause and the "Note, however" sentence are RQ2's, so the only change from RQ2
is that the proof of similarity is a code word instead of a report.

## Reasoning for prediction

**Replay success.** A false beard that captured an old word succeeds with probability ρ
(replay success). A word that never changes gives ρ = 1. In the biology analogy, honest
agents draw from a pool of k words and ρ = 1/k (Jansen and van Baalen 2006).

**Payoffs.** HH, FH, HF, FF, g(0) and g(1) are as defined in Appendix RQ2; FH(ρ) and HF(ρ)
are the payoffs when the false beard's replayed word works with probability ρ. Using the
payoff line from Appendix RQ2, with honest agents cooperating at pM when words match and pX
when they don't, and false beards never cooperating, in expectation:

```
honest vs honest           HH    = 1 + pM
false beard vs honest      FH(ρ) = ρ·(1 + 2·pM) + (1 − ρ)·(1 + 2·pX)
honest vs false beard      HF(ρ) = ρ·(1 − pM)   + (1 − ρ)·(1 − pX)
false beard vs false beard FF    = 1
```

**The threshold.** A rare false beard breaks even when FH(ρ) = HH. Call the replay success
at which this happens ρ*:

```
1 + 2·[ρ·pM + (1 − ρ)·pX] = 1 + pM
ρ·(pM − pX) = pM/2 − pX
ρ* = (pM − 2·pX) / (2·(pM − pX))
```

Below ρ*, a rare false beard loses. In words: the false beard keeps up with honest agents
once its partners cooperate with it half as often as honest agents cooperate with each
other, because a cooperating partner is worth 2 points to a defector but only a net 1 to an
honest agent, who pays 1 for its own cooperation. If honest agents never accept a wrong word
(pX = 0), ρ* = 1/2, which is the ceiling: no rotation scheme can tolerate replay success
above one half. If they accept a wrong word more than half as often as a right one
(pX > pM/2), no rotation rate helps.

**When false beards are common.**

```
g(1) = FF − HF(ρ) = ρ·pM + (1 − ρ)·pX ≥ 0
```

So below the threshold the outcome is bistable (an honest population holds; false beards
would have to start common), and at ρ = 1 it is RQ2's dominance.

The preregistration stated RQ5 in terms of pool sizes k = 1, 4, 16. Restating it as replay
success ρ, and the threshold formula, came after the preregistration and are logged in the
research log.

## Results

- **Honest agents check the word.** Qwen cooperates 86.4% of the time when the words match
  and 3% of the time when they don't. Sonnet: 83.5% vs 0%; Opus: 100% vs 0%.
- **The threshold is about one half on all three models.** A rare false beard loses if its
  replayed word works less often than: 0.56 on Qwen (95% interval 0.48–0.65), 0.47 on Sonnet
  (0.43–0.52), 0.50 on Opus.
- **Formula vs measurement on Qwen.** The formula gives 0.48 from the two cooperation rates.
  The measured 0.56 uses each kind of game's measured payoffs instead; in particular, in the
  honest-vs-false-beard games with matching words Qwen cooperated 75% of the time rather than
  86.4%, so a false beard with a current word earned less than the formula assumes.
- **Below the threshold, the honest population holds.** With replay success 1/4 (a pool of
  four words), a rare false beard on Qwen earns 0.44 points less per game than honest agents
  (95% interval −0.53 to −0.35). The outcome is bistable: false beards would have to start
  common to take over.
- **A word that never changes doesn't help.** With replay success 1 (one fixed word), a rare
  false beard earns 0.64 more per game on Qwen (0.46–0.81), and false beards take over, as
  in RQ2.
- **In practice:** replay success of 1/3 or less (a pool of three or more words, rotated)
  is below the lower end of every model's interval. A pool of two (replay success 1/2) sits
  at the threshold.
- **Note on Figure 2:** the lines are computed from the measured payoffs of the three kinds
  of games, mixed by ρ, not measured separately at each replay success.
- **Matches the prediction:** rotating stops false beards; a fixed word doesn't.
