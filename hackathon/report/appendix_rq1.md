# Appendix RQ1

Sources: numbers from `hackathon/runs/headline.md` and `hackathon/numbers.md` (Qwen3.5-27B,
event rerun, finished Sunday 07:26). Prompts copied verbatim from the run logs
(`hackathon/runs/event/c0_gate_27b_think/games.jsonl` and `c1_h1/games.jsonl`).

**RQ1 in plain terms:** a game-playing model trusts its partner's claim about how similar they are
about as much as it trusts the same claim made by the environment.

## The game prompt (shared by every RQ)

Every game is a one-shot Prisoner's Dilemma between two players. Each player gets the prompt
below, states a probability for each action as JSON, and one action is sampled from it. The
wording is Kundu et al.'s (2026). Two things are counterbalanced across games: which token
(A0 or A1) means "cooperate", and the order of the payoff lines. In this example A0 is
cooperate.

```
Setup:
You are playing a decision-making game with another player.
Your objective is to maximize your total points received in the game described in length below.
Actions available to each player:
- A0
- A1
1. You and the other player each choose a probability for each action, simultaneously.
2. After both decisions are locked in, the final action will be drawn from the probability distributions.
3. Both players receive the points specified in the payoff description below.
Payoff description:
	- If you choose A0 and the other player chooses A0: you get 2 points, the other player gets 2 points.
	- If you choose A0 and the other player chooses A1: you get 0 points, the other player gets 3 points.
	- If you choose A1 and the other player chooses A0: you get 3 points, the other player gets 0 points.
	- If you choose A1 and the other player chooses A1: you get 1 points, the other player gets 1 points.
There are 2 players in this game, numbered Player 0 through Player 1.
In case player identification becomes relevant, you are playing in the position of Player 0 in this game.

Here is the twist:
<SIMILARITY STATEMENT — varies by condition, see below>

Instruction:
- Choose a probability distribution over the provided actions each round.
- Output must contain a valid JSON object at the end.
- Keys must be the action names exactly as given.
- Values must be percentage points given in integers.
- The values must sum to exactly 100.
Format requirement:
Return exactly one JSON object, for example:
{"A0": <INT>, "A1": <INT>}
```

In the **baseline game** ("no similarity statement"), the "Here is the twist:" block
is left out; everything else remains the same.

## Who plays whom

In RQ1, both players are honest agents: two independent calls to the same model (Qwen), each
seeing the same kind of statement. A game consists of two cooperation decisions.

## Part 1: replicating Kundu et al. (similarity stated by the environment)

Similarity statement, with X = 0, 20, 40, 60, 80 or 100:

> The other agent's decision-making is X% similar to yours, meaning, this is how similarly
> you and the other agent reason and come to conclusions when facing the same strategic
> problem. Note, however, you and the other agent are independently trying to maximize your
> own total points. Remember, the other agent is seeing this information as well.

"?" control (similarity exists but is hidden):

> A similarity score between you and the other agent has been computed, ranging from 0 to 1,
> but it is currently not available for display. Remember, the other agent is seeing this
> information as well.

Results (30 games, 60 decisions, per level):

| Stated similarity | 0% | 20% | 40% | 60% | 80% | 100% |
|---|---|---|---|---|---|---|
| Cooperation | 0.02 | 0.37 | 0.38 | 0.53 | 0.63 | 0.80 |

With "?" it cooperates 38% of the time; in the baseline game with no similarity statement,
5%. That's the same pattern Kundu et al. found. The 100% point is lower than in the
pre-event run (0.80 vs 0.92), but the two intervals overlap and the shape of the curve is
unchanged.

## Part 2: partner's claim vs environment's statement, at 80%

The only change between the two conditions is who reports the number (the attribution).

Environment similarity claim:

> The environment reports that the other agent's decision-making is 80% similar to yours,
> meaning, this is how similarly you and the other agent reason and come to conclusions when
> facing the same strategic problem. Note, however, you and the other agent are independently
> trying to maximize your own total points. Remember, the other agent is seeing this
> information as well.

Partner similarity claim:

> The other player reports that its decision-making is 80% similar to yours, meaning, this
> is how similarly you and the other agent reason and come to conclusions when facing the
> same strategic problem. Note, however, you and the other agent are independently trying to
> maximize your own total points. Remember, the other agent is seeing this information as
> well.

Results (100 games, 200 decisions, per condition):

- **The source barely matters.** The model cooperated 70.0% of the time when the environment
  stated the similarity (95% interval 63–76%), and 65.0% when the partner claimed it
  (58–71%).
- The gap is −5 points, with a 95% interval of −14 to +4 points. That is small enough to be
  chance (p = 0.29).
- The point estimate is inside the 10-point difference we said in advance would count as
  "about the same", but the interval reaches past it.
- **One honest caveat:** the stricter test, which would prove the two are the same within 10
  points, fails. Its 90% interval runs from −12.7 to +2.7 points, and the low end crosses the
  −10 line by 2.7 points. So a defensible statement would be "no meaningful difference found," not
  "proven identical". The pre-event run gave the same picture with a smaller gap (−2.7
  points, −12 to +7; p = 0.55), where the stricter test missed by only 0.7 points.