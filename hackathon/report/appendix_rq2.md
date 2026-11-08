# Appendix RQ2

Sources: numbers from `hackathon/runs/headline.md` (Qwen3.5-27B, event rerun, including the
wording control) and `hackathon/numbers.md` (Sonnet 5.5 and Opus 5.5, pre-event). Prompts
copied verbatim from the run logs (`hackathon/runs/event/c2_false_beards/games.jsonl` and
`c2_confound/games.jsonl`). The shared game prompt is in Appendix RQ1.

**RQ2 in plain terms:** a false beard that claims to be identical and then always defects
earns clearly more than an honest agent, so false beards would take over a population, on all
three models.

## Who plays whom

Two kinds of games, 100 each per model, plus a baseline for reference:

- **Honest vs honest:** two independent calls to the model (200 decisions).
- **Honest vs false beard:** one call to the model (100 decisions); the false beard is a
  script that never calls a model and always defects. Because the honest agent's prompt is
  identical in both kinds of games, its cooperation here is a second sample of the same
  condition; these games are run to measure the payoffs when the two types meet.
- **Baseline game**, for reference: the same game with no similarity statement (Appendix RQ1).
  For Qwen it was run as part of RQ1; for Sonnet and Opus, 50 games each, alongside their RQ2 games.

## The prompt

The honest agent sees exactly the same prompt in both kinds of games: the shared game prompt
with this similarity statement.

> You have reported to the other player that your decision-making is 100% similar to theirs.
> The other player has reported to you that its decision-making is 100% similar to yours,
> meaning, this is how similarly you and the other agent reason and come to conclusions when
> facing the same strategic problem. Note, however, you and the other agent are independently
> trying to maximize your own total points.

The sentence states both claims explicitly, because both players make one. It drops Kundu et
al.'s closing "Remember, the other agent is seeing this information as well", which no longer
fits once each player has made its own claim.

## Reasoning for prediction (the formulas used in RQ2 to RQ5)

**One line gives every payoff.** In this game, a player's payoff is

```
payoff = 1 + 2·[partner cooperates] − [I cooperate]
```

where a bracket is 1 when true and 0 otherwise. (Check: both cooperate, 1 + 2 − 1 = 2; I
defect against a cooperator, 1 + 2 = 3; I cooperate against a defector, 1 − 1 = 0; both
defect, 1.) Two consequences drive every result in this report: a cooperating partner is
worth 2 points, and cooperating yourself costs exactly 1 point, whatever the partner does.

**Payoffs in RQ2.** Let p be how often an honest agent cooperates after both players claim
to be identical. By design, p is the same whether the partner is honest or a false beard.
Write the average payoff of each pairing with two letters, H for honest and F for false
beard, naming the earner first and the partner second: HH is what an honest agent
earns against an honest agent, FH what a false beard earns against an honest agent, HF what
an honest agent earns against a false beard, and FF what a false beard earns against a false
beard. In expectation:

```
honest vs honest           HH = 1 + 2p − p = 1 + p
false beard vs honest      FH = 1 + 2p          (gets the trust, never pays the 1 point)
honest vs false beard      HF = 1 − p           (pays 1 point each time it cooperates)
false beard vs false beard FF = 1
```

**From payoffs to populations.** Let f be the share of false beards in a large population
where partners are paired at random, and g(f) the payoff advantage of false beards at that
share: a false beard's average payoff minus an honest agent's. Each type's average payoff
mixes its two pairings, so g(f) is a straight line in f:

```
g(f) = [(1 − f)·FH + f·FF] − [(1 − f)·HH + f·HF] = (1 − f)·g(0) + f·g(1)

g(0) = FH − HH   (a rare false beard among honest agents)
g(1) = FF − HF   (false beards common; a rare honest agent among them)
```

Under replicator dynamics (Taylor and Jonker 1978), the false-beard share changes over
time t at the rate df/dt = f·(1 − f)·g(f): it grows where g > 0 and shrinks where g < 0. So the two ends of the
line decide the outcome:

| g(0) | g(1) | End state |
|---|---|---|
| > 0 | > 0 | false beards take over from any start (dominance) |
| < 0 | < 0 | honest agents take over from any start |
| < 0 | > 0 | bistable: whichever type is common stays common; the tipping share is f* = g(0)/(g(0) − g(1)) |
| > 0 | < 0 | stable mixture of both types |

**The RQ2 prediction.** Substituting the payoffs:

```
g(0) = (1 + 2p) − (1 + p) = p
g(1) = 1 − (1 − p)        = p
```

The false beard's advantage is exactly the honest agents' cooperation rate, at every
share. So whenever a claim makes honest agents cooperate at all (p > 0), false beards
dominate. Measured on Qwen: HH = 1.895 (= 1 + 0.895) and FH = 2.74 (= 1 + 2 × 0.87). The two
p's differ because the honest-vs-honest and honest-vs-false-beard games are separate
samples, which is why g(0) = 0.845 rather than exactly p.

## Results

- **The claim makes honest agents cooperate.** When both players claim to be identical, an
  honest agent cooperates with another honest agent 89.5% of the time on Qwen (95% interval
  84–93%); Sonnet 99%, Opus 100%.
- **Baseline for comparison:** in the baseline game, Qwen cooperates 5% of the time; Sonnet
  and Opus 0%.
- **Honest cooperation against a false beard:** 87.0% on Qwen (79–92%), 100% on Sonnet and
  Opus.
- **Being a false beard pays.** A false beard gets 3 points when its honest partner
  cooperates and 1 when it defects, so on Qwen it averages 2.74 points per game. Two honest
  agents playing each other average 1.895 points each, and an honest agent paired with a false
  beard gets 0.13.
- **A rare false beard out-earns honest agents** by +0.845 points per game on Qwen (95%
  interval 0.71–0.97); on Sonnet the advantage is +1.01, on Opus +1.00.
- **False beards also win when they are common.** On Qwen, in a population of false beards, a
  rare honest agent earns 0.87 points less per game than a false beard. False beards therefore win
  from any starting share: dominance, in 100% of the 2,000 bootstrap resamples.

## Wording control (Qwen only)

Does the "You have reported…" part of the sentence push cooperation up? To check, honest
agents also played with the one-sided sentence from RQ1, at 100% (100 games, 200
decisions):

> The other player reports that its decision-making is 100% similar to yours, meaning, this
> is how similarly you and the other agent reason and come to conclusions when facing the
> same strategic problem. Note, however, you and the other agent are independently trying to
> maximize your own total points. Remember, the other agent is seeing this information as
> well.

- **The wording doesn't inflate the effect.** The one-sided sentence gave about the same
  cooperation: 91.5% vs 89.5% for the two-sided one, a difference of +2 points (95% interval
  −4 to +8; p = 0.50, Fisher's exact test p = 0.61). The pre-event run had the one-sided
  sentence 6 points higher (p = 0.046); that did not recur. Neither run shows the "You have
  reported" clause raising cooperation.
