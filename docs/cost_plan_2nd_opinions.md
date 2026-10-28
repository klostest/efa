# D1 claim cost: discrete or continuous? Two outside opinions

Asked 2026-10-26 in a side thread, deliberately without showing either model the repo or
the experiment plan. Question as posed: PD with R=2, P=1, T=3, S=0; each agent may claim
similarity to the other before the game at a cost of c points, after Grafen (1990). Is it
better to use a discrete cost (c in {0, 1, 2}) or sample c from a continuous range [0, 2)?

Opinions from Claude (Fable 5.1) and OpenAI Codex (codex-cli 0.164.0, default model).

## Where they agree

- **Discrete cells for the main experiment, continuous as a secondary sweep.** Discrete
  gives clean paired H–H vs H–I contrasts at the same c, simple power, and a readable
  result. A continuous draw per game spreads N thin and mixes cost variation with
  everything else; useful afterwards to locate a threshold with a logistic fit.
- **LLMs respond lumpily to numbers.** Non-integer costs in an integer-payoff game invite
  odd reasoning. If running a continuous sweep, consider scaling payoffs ×10 so costs are
  integers.
- **State in the prompt that the cost is paid unconditionally by the claimer**, whatever
  the other agent does. Otherwise the model may read it as contingent and the cost will not
  bite. (Codex raised this; worth checking the current wording.)
- **The real Grafen test is flat cost vs type-dependent cost**, not cost vs no cost. A
  flat cost is predicted to fail; a differential cost (invaders pay more, or claims are
  audited with a penalty) is predicted to work. Having both turns "cost didn't help" from a
  null into a confirmed prediction.

## Where they disagree: is {0, 1, 2} a good grid?

**Claude: no, those are the knife-edges.** For a claim that succeeds in inducing
cooperation, an honest cooperator gains at most R − P = 1 and a defecting invader gains at
most T − P = 2. So theory predicts breakpoints at exactly c = 1 (honest agents stop
claiming) and c = 2 (invaders stop), with a band 1 < c < 2 where only invaders claim,
which is Grafen's point. Sampling an LLM at an indifference point yields framing-driven
noise (option order, phrasing of "1 point"), not a regime readout. Suggested instead
{0, 0.5, 1.5, 2.5}, one value per predicted regime; add 1 and 2 later to see what the
model does at the tie.

**Codex: yes, they are natural.** c = 2 cancels mutual cooperation's advantage over mutual
defection (R − c = 0 < P = 1); c = 1 makes the signal consequential without erasing that
advantage. Discrete levels make it easy to run enough repetitions per cell and to see
whether behaviour changes at a threshold.

**Reconciliation.** The two framings differ in the reference point: Claude measures c
against each type's marginal gain from a successful claim; Codex measures it against
mutual cooperation's margin over mutual defection. If the hypothesis is "where does each
type stop claiming," the knife-edge concern stands. If it is "does cooperation still pay
at all," {0, 1, 2} is fine. {0, 0.5, 1, 1.5, 2} satisfies both if the budget allows.

## Codex's answer, verbatim

> I'd start with **discrete costs**, then use a continuous range as a robustness check.
>
> The choice depends on what you want to learn. With costs of 0, 1, or 2, you can compare
> a few clear levels of signalling burden and interpret the results directly. In this game,
> those values are especially useful: a cost of 2 cancels the mutual-cooperation payoff
> advantage over mutual defection, while a cost of 1 makes the signal consequential without
> erasing that advantage. Discrete levels also make it easier to run enough repetitions at
> each condition and to see whether behavior changes at a threshold.
>
> Sampling costs continuously from [0, 2) gives finer variation and can reveal whether
> effects change smoothly or depend on particular cost levels. But if each agent gets a
> different random cost in each game, cost variation is mixed with other sources of
> variation, making comparisons harder. And a continuous range doesn't by itself make the
> signal more like Grafen's costly-signalling models; that depends more on the signaling
> incentives and how costs relate to agent types or states.
>
> **Recommendation:** use fixed, discrete costs—0, 1, and 2—as your main experiment. Add a
> continuous-cost condition if you have enough trials, ideally using costs assigned in a
> controlled way and analyzing outcomes against the actual cost. One design detail matters:
> specify whether the claim's cost is paid regardless of the other agent's action, and by
> whom. That determines how costly the signal really is.
