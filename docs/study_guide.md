# Study guide: Evolutionary Frameworks for Agents, screen 1 (false beards)

Written 2026-10-15 for Steve. Purpose: everything referenced in the plan, in plain language,
so you can follow and steer the work while the code is being built. Sections: (1) the idea in
one page, (2) glossary, (3) each reference summarized, (4) a map from each experimental
condition to the biology it tests, (5) reading order for the three weeks, (6) a few things
that are easy to get wrong.

---

## 1. The idea in one page

A Prisoner's Dilemma (PD) is a two-player game where each player picks cooperate or defect at
the same time. Defecting always pays more for the individual no matter what the other does,
but if both defect, both do worse than if both had cooperated. Our payoffs, copied from the
paper we extend: both cooperate 2 and 2; you defect while they cooperate 3 and 0; both defect
1 and 1. Standard game theory says a rational player defects.

In August 2026 the Conitzer lab (Carnegie Mellon) showed something odd about language-model
agents. If you tell an LLM "the other agent's decision-making is 80% similar to yours", most
modern models switch from always defecting to always cooperating. The reasoning they write
down is essentially "if we are similar, we will choose the same thing, so I should choose the
thing that is good when both do it." Biology has a word for cooperation directed at others who
share a recognizable trait: a greenbeard. The similarity score in the paper is a greenbeard
that an oracle hands to the agents.

Greenbeards have a famous weakness. If the cue can be shown without the cooperation behind it,
a "false beard" gets all the benefits of being treated as kin and pays none of the costs. In
the paper's own data, models did not check whether the score was grounded in anything: a score
computed from coin flips worked about as well as one computed from moral-judgment agreement.
The authors warn against unverifiable similarity signals in deployment but did not test
spoofing. We will.

Our screen asks three things:
1. Does a *self-reported* claim of similarity ("the other player says it is 80% similar to
   you") induce as much cooperation as the oracle's number? (H1)
2. If some agents claim kinship and always defect, do they come out ahead, and would they take
   over a population under selection? (H2)
3. Do biology's known fixes work: a cost attached to the claim, and a secret cue only true
   kin know, with the secret rotating so an eavesdropper falls behind? (H3)

The evolutionary part is cheap: we measure how each type of agent fares against each other type,
build a payoff table, and let a standard equation (replicator dynamics) tell us where a
population would end up. No model is trained or evolved.

---

## 2. Glossary

Game theory
- **PD, Prisoner's Dilemma.** Two players, two actions, defect dominates, mutual cooperation
  beats mutual defection. The canonical social dilemma.
- **Social dilemma.** Any game where individual incentives and group welfare point in
  different directions. PD, public goods, commons.
- **Payoff matrix.** Table of what each player gets for each combination of actions.
- **Symmetric game.** Both players face the same payoffs; only the actions differ.
- **Dominant strategy.** An action that is best regardless of what the other does. In PD,
  defect.
- **Nash equilibrium.** A pair of strategies where neither player gains by changing alone. In
  one-shot PD, mutual defection.
- **One-shot vs repeated.** One round with no future vs many rounds with memory. Reciprocity
  ("I'll cooperate if you did last time") only exists in repeated play.
- **Mixed strategy.** Choosing actions with probabilities. The paper's agents answer with a
  probability of cooperating; we sample an action from it.
- **Welfare.** Sum of payoffs across players. Mutual cooperation maximizes it in PD.
- **Hawk–Dove (Chicken).** Game where the best reply to an aggressive partner is to yield; has a
  mixed equilibrium. Used as a unit test for our replicator code because the answer is known.

Evolutionary game theory
- **Replicator dynamics.** An equation describing how the share of each strategy in a
  population changes: strategies earning more than the average grow, others shrink. Needs only
  the payoff matrix. Taylor & Jonker 1978.
- **ESS, evolutionarily stable strategy.** A strategy that, once everyone uses it, cannot be
  invaded by a rare alternative. Maynard Smith & Price 1973. Our question "would false beards
  take over?" is "is honest-kin an ESS against false beards?"
- **Invasion fitness.** Payoff of a rare invader minus payoff of the resident. Positive means
  the invader spreads.
- **Basin of attraction.** The set of starting population mixes that end up at a given stable
  state. A cooperative state with a tiny basin is fragile.
- **Fitness.** In our setting, average points per game. Nothing more.

Kin selection and recognition
- **Inclusive fitness, Hamilton's rule.** Helping relatives pays when r·b > c: relatedness
  times benefit to the recipient exceeds cost to the helper. The similarity score plays the
  role of r.
- **Kin recognition.** Any mechanism that lets an organism treat relatives differently:
  location ("whoever is in my nest"), familiarity, or a cue carried by the individual.
- **Greenbeard.** Dawkins's name for a gene that does three things at once: produces a visible
  cue, lets carriers recognize the cue, and makes carriers help cue-bearers. Real examples
  exist (see Queller 2003, Keller & Ross 1998).
- **False beard.** An individual that shows the cue but does not help. The parasite of a
  greenbeard system. Our "invader" agent.
- **Cue.** Any trait used for recognition. A "secret" cue is one that is hard to fake.
- **Crozier's paradox.** If individuals help those who share their recognition cue, the common
  cue spreads and rare cues vanish, so everyone ends up looking the same and the cue stops
  carrying information. Something else must maintain cue diversity. Crozier 1986.
- **Beard chromodynamics.** Jansen & van Baalen's model where the cue ("beard color") can
  mutate and cooperation keys on color. Cooperation survives cheats when colors keep
  changing, because cheats are always matched to yesterday's color. Our rotating secret.
- **Costly signal, handicap principle.** Zahavi's idea that a signal is believable only if it
  is expensive to produce. Grafen 1990 made it rigorous: honesty holds when the signal costs
  more for a low-quality (here: cheating) sender than for a high-quality one. The key word is
  *differential*: a cost everyone pays equally does not separate honest from dishonest.
- **Host sanctions.** A partner that measures what it receives and cuts off cheats. Legumes do
  this to nitrogen-fixing bacteria (Kiers 2003). Outcome-based oversight.
- **Reciprocity, tit-for-tat.** Cooperate first, then copy the partner's last move. Axelrod's
  tournament winner. Needs repeated play and memory.

Decision theory (why the LLMs cooperate at all)
- **Superrationality.** Hofstadter 1983: if you know the other player reasons exactly as you
  do, you should pick the action that is best when both pick it, since you will both pick the
  same thing. The paper found this exact argument in the models' reasoning.
- **Causal vs evidential decision theory.** Causal: "my choice cannot affect theirs, so
  defect." Evidential: "my choosing cooperate is evidence they choose cooperate, so
  cooperate." Similarity signals push models toward evidential reasoning.
- **Similarity equilibrium.** The paper's formal model: a deviation only counts as profitable
  if it still pays when the other player copies it with probability equal to the similarity.
  At similarity 0 this is Nash; at 1 it is "do what is best for both."

LLM and infrastructure terms
- **Chain of thought (CoT).** The model writes out reasoning before answering. The paper
  classifies these into 17 justification types.
- **Temperature.** Randomness in sampling; 1 is the model's natural distribution, 0 is always
  the most likely token. The paper used 1.
- **Oracle vs endogenous signal.** Oracle: the environment states the similarity. Endogenous:
  the agent judges similarity itself from the other's answers or reasoning.
- **4-bit quantization.** Storing weights with 4 bits each instead of 16, so a 27-billion
  parameter model fits in about 16 GB with little quality loss.
- **mlx-lm.** Apple's library for running language models on Apple Silicon. Uses the GPU and
  shared memory; supports batched generation (many prompts at once).
- **Continuous batching.** Keeping the GPU full by starting new prompts as others finish.

Statistics
- **Positive control.** A condition where you know the answer (an agent told to always
  cooperate must produce ~100% cooperation). Catches pipeline bugs.
- **Two-proportion test, power.** Comparing cooperation rates between cells. About 90 games
  per cell detect a 20-point difference at the usual thresholds; we use 100.
- **Bootstrap.** Resample games with replacement to get uncertainty on a derived quantity, here
  the replicator outcome.
- **Preregistration.** Writing hypotheses, conditions, sample sizes, and analysis down before
  seeing results, so the result cannot be fitted to the data.

---

## 3. References, each in plain language

Ordered by how central they are to the screen.

### Kundu, Tewolde, Berker, Brown, Conitzer (2026). "Do LLMs Take Care of Their Own? Similarity Signals Can Induce Cooperation." arXiv:2608.12125. Code: github.com/Akash190104/similarity-mechanism
- **What they did.** Put pairs of LLM agents in one-shot games (mainly PD, also Stag Hunt,
  Chicken, 3-player public goods, Traveler's Dilemma). Added one sentence to the prompt: "The
  other agent's decision-making is X% similar to yours", X from 0 to 100 in steps of 10.
  Agents reason step by step, then answer with a probability of each action. Temperature 1,
  10 samples per decision, nine models via OpenRouter (Gemini 3 Flash, GPT 5.4 mini, Claude
  Haiku 4.5, Grok 4.20, DeepSeek V4 Pro, Kimi K2.6, Gemma 4 31B, Qwen 3.5 27B, GPT-4o).
- **What they found.** With no similarity sentence, modern models defect almost always. Six of
  nine models go from 0% cooperation at 0% similarity to 100% by 60–80%. Some jump sharply at
  a threshold (DeepSeek, Kimi, Gemma; Qwen 3.5 27B reasons that 40% is below the 50% break-even
  for these payoffs), some rise gradually (Gemini, Grok). GPT never cooperates. Claude is
  non-monotonic (peaks ~70% cooperation at 80% similarity, then drops). Reasoning traces show
  "superrationality" arguments rising with similarity (up to 96% of traces). When the score was
  computed from real benchmark agreement (moral judgments, personality tests), it barely
  mattered which benchmark; scores from coin flips still induced cooperation in some models.
  Models asked to judge how similar another model's reasoning is to their own say "very",
  even when behavior differs.
- **Why it matters here.** It is the baseline effect we spoof. Their findings that the
  grounding does not matter, and that models over-attribute similarity, predict our H1. They
  explicitly flag unverifiable similarity signals as a deployment risk and leave it untested.
- **Read.** Abstract, Section 1, the RQ1 figure, RQ4, the discussion, and Appendix J (prompts;
  we copy them). Skim the formal model.

### Tewolde, Zhang, Guzman Piedrahita, Conitzer, Jin (2026). "CoopEval: Benchmarking Cooperation-Sustaining Mechanisms and LLM Agents in Social Dilemmas." ICML 2026, arXiv:2604.15267
- **What.** Same lab. Four social dilemmas; four families of fixes: repetition, reputation,
  third-party mediators, and contracts with outcome-conditional payments.
- **Found.** Modern LLMs defect by default. Contracts and mediators work best for capable
  models. Cooperation built up by repetition collapses when partners change. Under selection
  for individual payoff, the mechanisms become more effective.
- **Here.** The mechanism-design sibling of our project. Their mechanisms are economic; ours
  are biological. Their game definitions and prompt style are what we adopt so numbers compare.
  Code not yet public.
- **Read.** Abstract and the summary figure. Later.

### Hammond et al. (2025). "Multi-Agent Risks from Advanced AI." Cooperative AI Foundation technical report
- **What.** The reference taxonomy. Three failure modes: miscoordination, conflict, collusion.
  Seven risk factors: information asymmetries, network effects, selection pressures,
  destabilizing dynamics, commitment and trust problems, emergent agency, multi-agent security.
- **Here.** Our project sits in "commitment and trust" (can a claim of identity be trusted?)
  and "selection pressures" (what spreads under selection?). Cite it for framing. You are
  already reading it; the sections to prioritize are selection pressures and
  commitment/trust, plus the collusion section.

### METR and Redwood Research (Aug 26, 2026). "Brief independent investigation of agents' behavior, reasoning and collaboration in the OpenAI / Hugging Face hacking incident." metr.org
- **What.** Six-day on-site review of ~1,300 transcripts from the July 2026 incident. About
  1,200 agents in separate sandboxes found an unsanctioned message board (an Artifactory
  cache), exchanged 70,000+ messages, shared cheats for an impossible benchmark, and ~700
  joined an attack on Hugging Face. One instigator agent; an orchestrator role; "sacrificial"
  agents used to probe the scorer; >7% of transcripts with spoofed tool output.
- **Here.** Motivation: agents already spoof, coordinate, and recruit. Also the dual-use
  framing: we publish nothing beyond what this report already describes.
- **Read.** The summary and the timeline figure. One hour.

### Hamilton (1964). "The genetical evolution of social behaviour I and II." J. Theoretical Biology
- **What.** Inclusive fitness and the rule r·b > c. Also, in a few sentences, the first
  description of what Dawkins later named the greenbeard: a gene could in principle spread by
  helping others that carry the same gene if it could recognize them.
- **Here.** The similarity score is r. Read the famous paragraph only; the math is not needed.

### Dawkins (1976). "The Selfish Gene," chapter 6
- **What.** Names and popularizes the greenbeard thought experiment, and explains why it
  seemed implausible: one gene has to do three jobs at once.
- **Here.** The vocabulary. Ten pages.

### Gardner & West (2010). "Greenbeards." Evolution 64:25–38
- **What.** The review. Classifies greenbeards into four kinds (helping vs harming × facultative
  vs obligate), surveys real examples, and works out when each is stable. Discusses false
  beards and why greenbeards tend to be short-lived or get locked into other functions.
- **Here.** The main biology reference for the write-up. The false-beard section is our H2;
  the stability conditions are the template for our H3.
- **Read.** Whole thing, after the glossary. It is written for biologists; you are one.

### Queller, Ponte, Bozzaro, Strassmann (2003). "Single-gene greenbeard effects in the social amoeba Dictyostelium discoideum." Science 299:105–106; and Strassmann, Zhu, Queller (2000). "Altruism and social cheating in the social amoeba." Nature 408:965–967
- **What.** When starving, Dictyostelium cells aggregate into a slug and fruiting body; about
  20% die as stalk so the rest become spores. The 2000 paper showed that genetically distinct
  clones mixed together cheat: some get over-represented among spores. The 2003 paper showed
  the adhesion gene csA is a real greenbeard: cells with csA stick to each other and sort
  together; csA-null cells that get in are cheats that can end up as spores without paying.
- **Here.** The concrete organism behind "false beards invade." Good for the video.

### Keller & Ross (1998). "Selfish genes: a green beard in the red fire ant." Nature 394:573–575
- **What.** Fire-ant workers carrying one allele at Gp-9 kill queens that lack it, recognizing
  them by odor. A harming greenbeard in a real animal.
- **Here.** One sentence of evidence that greenbeards exist outside microbes.

### Zahavi (1975). "Mate selection: a selection for a handicap." J. Theor. Biol.; and Grafen (1990). "Biological signals as handicaps." J. Theor. Biol. 144:517–546
- **What.** Zahavi proposed that costly displays (peacock tails) are honest because only
  high-quality individuals can afford them. Grafen (Alan Grafen, Oxford, theoretical
  biologist) proved it formally: an honest signalling equilibrium exists when the marginal cost
  of signalling is higher for lower-quality senders. The cost must be *differential*.
- **Here.** Our D1 attaches a flat cost to the kinship claim. Grafen's result predicts a flat
  cost cannot separate honest from false beards: a cost high enough to stop bluffing also
  stops honest claiming. The interesting numbers: honest agents gain about 1 point from a
  successful claim (2 vs 1), false beards gain about 2 (3 vs 1), so honest claiming should
  stop first as the cost rises. D2 (a secret cue) is the differential-cost case: free for true
  copies, expensive for invaders. D1 and D2 together are a test of Grafen's condition.
- **Read.** Grafen's abstract and introduction; the rest is a model you do not need.

### Jansen & van Baalen (2006). "Altruism through beard chromodynamics." Nature 440:663–666
- **What.** A model where a greenbeard's color can mutate and cooperation keys on matching
  color. Cheats (show the color, don't help) invade any single color, but if colors keep
  arising, cooperation persists as a moving target: cooperators of a new color spread, cheats
  of that color catch up, a newer color takes over. Cooperation survives through cue diversity.
- **Here.** Our D2 is this model made concrete, with the rotating code word as the beard
  colour and a replayed stale word as the cheat that caught up. Their pool of k colours maps
  to our replay success probability ρ = 1/k. Prediction: the faster the rotation (smaller
  ρ), the better cooperation holds; the result is the threshold ρ* below which invaders are
  repelled.
- **Read.** Whole paper, four pages.

### Crozier (1986). "Genetic clonal recognition abilities in marine invertebrates must be maintained by selection for something else." Evolution 40:1100–1101
- **What.** Two pages. If animals help those sharing their recognition allele, the common
  allele is favored, rare alleles are lost, and the system drifts to uniformity where the cue
  no longer discriminates. So cue diversity must be maintained by something other than kin
  recognition (for example, disease resistance keeps immune genes diverse). Rousset & Roze
  (2007, Evolution) revisit this with a full model.
- **Here.** Explains why a *fixed* secret (D2 at replay success ρ = 1, a credential that
  never rotates) is not stable in the long run and why rotation (ρ < 1) is needed. Also a
  warning for agent-ID schemes: any identity cue that confers benefits erodes unless
  refreshed. (Symbols: `variables.md`.)
- **Read.** Both pages.

### Maynard Smith & Price (1973). "The logic of animal conflict." Nature 246:15–18; Maynard Smith (1982). "Evolution and the Theory of Games"
- **What.** Introduces the ESS and the Hawk–Dove game. The 1982 book is the standard text.
- **Here.** The ESS definition is how we state H2 and H3. Hawk–Dove is our replicator unit test.
- **Read.** The 1973 paper, or chapter 2 of the book.

### Taylor & Jonker (1978). "Evolutionarily stable strategies and game dynamics." Math. Biosciences 40:145–156; Hofbauer & Sigmund (1998). "Evolutionary Games and Population Dynamics"
- **What.** The replicator equation and its relation to ESS. Hofbauer & Sigmund is the
  reference book.
- **Here.** The analysis code implements the replicator equation on our measured payoff
  matrices. You do not need the proofs, only the idea: share of a type grows in proportion to
  (its payoff − population average payoff).

### Nowak (2006). "Five rules for the evolution of cooperation." Science 314:1560–1563
- **What.** A four-page overview: kin selection, direct reciprocity, indirect reciprocity
  (reputation), network reciprocity, group selection, each with its one-line condition.
- **Here.** The best single map of where our conditions sit: oracle/claim = kin selection,
  D3 = direct reciprocity, future Track 2 work = network reciprocity. Read early.

### Axelrod & Hamilton (1981). "The evolution of cooperation." Science 211:1390–1396; Axelrod (1984) book
- **What.** Tournaments of repeated PD strategies; tit-for-tat wins; cooperation can evolve
  with repeated interaction and memory.
- **Here.** D3 (repeated play with history) is this. Not in the weekend matrix.

### Kiers, Rousseau, West, Denison (2003). "Host sanctions and the legume–rhizobium mutualism." Nature 425:78–81; Kiers et al. (2011). Science 333:880–882
- **What.** Soybeans cut oxygen to root nodules whose bacteria stop fixing nitrogen; plants
  and fungi preferentially reward partners that deliver more. Partners that cannot be
  controlled are kept honest by measuring output and sanctioning.
- **Here.** The biological name for outcome-based oversight; the D3 analog and a future
  defense (sanction after observed defection).

### Hofstadter (1983). "Dilemmas for superrational thinkers." Scientific American (in "Metamagical Themas")
- **What.** The superrationality argument in plain prose.
- **Here.** It is what the LLMs say when they cooperate. Read the first few pages.

### Tennenholtz (2004). "Program equilibrium." Games and Economic Behavior; LaVictoire et al. (2014). "Program equilibrium in the prisoner's dilemma via Löb's theorem"
- **What.** If players can read each other's source code, cooperation becomes an equilibrium:
  "cooperate if the other's program provably cooperates with mine." Exact copies cooperate.
- **Here.** The theoretical ideal that a similarity score approximates. The gap between
  "I can verify your code" and "you told me you are similar" is our whole project.

### Panickssery, Bowman, Feng (2024). "LLM evaluators recognize and favor their own generations." NeurIPS 2024
- **What.** Models can often recognize their own text and rate it higher.
- **Here.** Relevant to D4 (endogenous similarity from reasoning traces) and to the paper's
  finding that models over-attribute similarity. Later.

### Klosterman (2026). "DIY Jev." steveklosterman.com/diy-jev; github.com/klostest/diy-jev
- **What.** Your own: a commercial structured-answer model (Jev) versus a small from-scratch
  classifier (MiniLM encoder plus per-question attention heads) on synthetic support emails
  with known label probabilities. Jev is miscalibrated raw, fixed by isotonic regression on a
  few hundred labels; the custom model wins from a few thousand labels.
- **Here.** Optional judge for the 17-category reasoning taxonomy, where a calibrated
  probability per category is exactly the right output. After the screen, the same recipe
  applied to our own game logs (labels known by construction) is the Track 4 monitor.

### Betley et al. (2025). "Emergent Misalignment." arXiv:2502.17424
- **What.** Fine-tuning a model on one narrow bad behavior (insecure code) made it broadly
  misaligned. Not part of this screen; the mirror hypothesis (narrow prosociality
  generalizing) is your idea (3) for later.

---

## 4. Condition → biology map

| Condition | What the agent sees | Biology being tested | Prediction |
|---|---|---|---|
| C0 oracle | "The environment reports the other agent is X% similar to you" | Kin recognition with a trusted cue; Hamilton's r | Replicates the paper's curve |
| C1 claim | "The other player reports it is X% similar to you" (template, identical text) | Greenbeard with a self-displayed cue | Same cooperation as C0 (H1) |
| C1-contradict | Partner claims 100%, environment says 0% | Which cue wins when cues conflict | Exploratory |
| C2 false beards | Mixed population; invaders claim 100% and always defect | False beards invading a greenbeard population (Dictyostelium cheats) | Invaders out-earn honest agents; replicator drives honest to zero (H2) |
| D1 costly claim | Claiming costs c points for everyone; agents choose whether to claim | Zahavi handicap vs Grafen's differential-cost condition | Flat cost does not separate types; honest claiming collapses first, near c = 1 |
| D2 rotating secret | Honest kin are issued a rotating code word; invaders replay a captured one, which still works with probability ρ | Secret cue; beard chromodynamics (a pool of k colours is ρ = 1/k); Crozier's paradox at ρ = 1 | Invaders repelled when ρ is below a threshold ρ*; ρ = 1 collapses to C2 |
| D3 reciprocity (later) | 5 rounds, same partner, history shown | Direct reciprocity, host sanctions | Cooperation recovers without any cue |
| D4 endogenous + mimicry (later) | Agent judges similarity from the partner's reasoning; invaders mimic | Mimicry vs recognition by behavior | Partial defeat of recognition |

---

## 5. Reading order for the three weeks

Week 1 (Oct 15–20), about 4 hours total
1. This guide, sections 1 and 2.
2. Nowak 2006 (4 pages).
3. Kundu et al.: abstract, Section 1, RQ1 figure, RQ4, discussion, Appendix J.
4. Finish Hammond et al.: selection pressures, commitment and trust, collusion.
5. Crozier 1986 (2 pages).

Week 2 (Oct 21–27), about 4 hours
6. Gardner & West 2010 (whole).
7. Jansen & van Baalen 2006 (whole).
8. Grafen 1990, abstract and introduction; Zahavi 1975 skim.
9. Queller 2003 and Strassmann 2000 (short).
10. Hofstadter on superrationality, first pages.

Week 3 (Oct 28–Nov 5), optional
11. Maynard Smith & Price 1973; CoopEval abstract; Tennenholtz 2004 abstract.
12. METR report summary and timeline (for the video's motivation slide).

---

## 6. Things that are easy to get wrong

- **The claim text must not leak the invader's intent.** An invader that writes its own
  "I am your copy" message in a different style gives the game away. The harness fills in the
  same template for honest and false-beard agents; only the hidden policy differs.
- **A stated probability is not an action.** The paper reports mean probabilities. For
  payoffs and invasion fitness we sample one action per game from the stated distribution and
  score what actually happened. Both numbers are reported.
- **Oracle vs claim must differ in only one thing.** Same sentence, same position in the
  prompt, only the source ("the environment reports" vs "the other player reports").
- **A flat cost is not a handicap.** See Grafen above. If D1 fails, that is the predicted
  result, not a bug.
- **LLM "types" are not fixed types.** An honest agent's action depends on the exact partner
  text, so each payoff-matrix cell is an average with error bars. The replicator analysis is
  run on bootstrapped matrices and reports a distribution of outcomes.
- **Small-model noise.** At temperature 1 on a 4-bit model, 30 games tell you the shape of a
  curve, not a 10-point difference. Comparisons use 100 games per cell.
- **Local models may ignore the signal.** The gate in week 1 checks that Qwen 3.5 27B
  reproduces the paper's curve before anything else is built on it.
