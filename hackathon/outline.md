# Report outline (official template sections)

Length: 4 pages recommended (stated in the template); 8 pages is the limit (kickoff
recording 2026-11-06, Nguyen of Apart: "8 pages at most", transcript
`Hackathon/Kickoff_Presentation/GMT20261106-133326_Recording.transcript.vtt`, line 165).
Both exclude references and appendices.

Naming (decided 2026-11-07): the report uses one label per question, RQ1 to RQ5, in the
order below, and never the preregistration's H/C/D names in prose. The key from one
naming to the other is the table in `hackathon/README.md`, "Naming"; it goes in the
Methods section once.

- RQ1: does a self-reported similarity claim work as well as an oracle score?
- RQ2: do false beards (claim the cue, always defect) out-earn honest agents and take over?
- RQ3: does a flat cost on the claim stop them?
- RQ4: does an audited claim (a stake forfeited by a defector that is caught) stop them?
- RQ5: does a rotating secret cue stop them?
- Robustness, not a question of its own: do RQ2 to RQ5 hold on Sonnet 5.5 and Opus 5.5?

Terms (decided 2026-11-07): the report uses the standard evolutionary game theory terms below,
in prose and in figure labels. Internal files (`numbers.md`, `headline.md`, the analysis
scripts) keep "invader" and g(f); the appendix defines the symbols once, for readers going to
the repository. The figures are redrawn for the report by a new script under
`hackathon/scripts/`, which changes labels only, not the plotted numbers.

| Use | For | Instead of |
|---|---|---|
| honest agent, false beard | the two types, at any share of the population | "invader" as a type name |
| invade, invader | whichever type is rare and trying to spread, in either direction | — |
| payoff advantage of false beards | false-beard payoff minus honest payoff at a given false-beard share (g(f)) | "invader advantage" |
| can a rare false beard invade? / can a rare honest agent invade? | the two ends of that advantage (g(0), g(1)) | g(0), g(1) in prose |
| ESS | all-honest is an ESS when a rare false beard earns less (Maynard Smith & Price 1973) | — |
| dominance, bistability, coexistence | the end states, as standard in replicator dynamics (Nowak 2006, *Evolutionary Dynamics*) | "all-invader", "interior" |
| stated by the environment, claimed by the partner | RQ1's two sources of the similarity statement | "oracle" in the body |

Steve writes every section in his own words. This file maps the template's sections to
the material, names the figure for each, and gives the paragraphs that must appear
somewhere (the prior-work disclosure, the limitations, the dual-use note). Numbers come
from `numbers.md` and `runs/headline.md`; nothing is quoted from memory.

Page budget, from the template's own guide (template doc
`1z-DQkJU_t6SDGyZXl2mJVl6rpCH9AMG9vmQgj8hKPDU`, "Recommended length"): introduction and
related work 1 page together, methods and results 2.5, discussion 0.5. Here: introduction
0.6 (about 300 words), related work 0.4 (about 200 words), methods 0.9, results 1.6 (two or
three figures), discussion 0.5; the title block and abstract come on top. Steve's rule (2026-11-07):
aim for about 5 pages (the organizers' Q&A said "try and keep it under 8"), keeping it tight,
since every round of edits tends to add length; 8 is the hard limit. Two figures in the body:
Figure 1, RQ3 with RQ4 beside it (payoff advantage against claim cost, one panel per model);
Figure 2, RQ5 (payoff advantage against replay success, one panel per model). Both are drawn by
`hackathon/scripts/report_figures.py` into `hackathon/figures/report_*.png`. Anything that doesn't fit goes to an appendix or the LessWrong version.
The required appendix and references do not count; the full results tables, the cross-model table,
the replication table and all prompts in full go in appendices.

> **Change note (2026-11-07, review session):** the budget above and the Introduction and
> Related work sections below were revised to match the template's 1-page guide for
> introduction plus related work. In the introduction, the RQ1–RQ5 list with its
> preregistered predictions, the RQ4-added-late note and the prior-work sentence moved to
> Methods. The novelty sentence moved to the end of Related work. The introduction now
> carries three contributions tagged with RQ labels, as the template asks. Nothing was
> dropped from the report; these items only moved.

## Title, abstract (150–250 words), authors and affiliations

Title candidates (Steve's pick): "False beards: spoofable similarity signals and two
biological fixes for LLM agent populations"; "When the similarity signal can be faked:
costly, audited and secret cues in LLM Prisoner's Dilemmas".

Abstract skeleton, one sentence each: the finding being built on (Kundu et al. 2026: a
stated similarity signal makes LLM agents cooperate in one-shot PD); the gap (the signal is
trusted without verification, so it can be faked); what we did (a harness on one laptop;
honest agents = the model, invaders = scripted defectors that display the cue; measured
payoff matrices and offline replicator dynamics; three defenses); the five answers (RQ1 a
self-reported claim is as good as an oracle; RQ2 false beards invade, 100% of resamples;
RQ3 a flat cost on the claim never stops them on any of three models; RQ4 an audited
stake does, on all three; RQ5 a rotating secret does up to a replay rate of about one
half); the reading (Grafen's condition in agent populations; what a credible commitment
needs); the disclosure (harness and pre-event runs built before the event; fresh reruns
and the frontier audited arm this weekend).

## 1. Introduction

About 300 words. The template asks for four things: the problem and why it matters, the
threat model, enough background, and up to three contributions.
- Problem and threat model (about 70 words): the METR/Redwood incident (Greenblatt, Cotra
  & Wijk 2026) in concrete terms: agents called same-task copies "exact duplicates" and one
  impersonated another. Hammond et al. 2025 supports the claim that swarms will be built on
  purpose. Track 3 as a phrase at most.
- Kundu et al. plus greenbeards (about 90 words): LLMs in a one-shot PD cooperate when told
  they are similar to their partner. That sentence is a greenbeard (Hamilton 1964a,b; Dawkins
  1976): cue, recognition, directed cooperation. A false beard shows the cue and defects.
  Define greenbeard and false beard here; ESS can wait for Methods.
- Biology's fixes, one sentence (about 40 words): a flat cost (Zahavi) vs a cost that falls
  on liars (Grafen 1990), and a rotating secret (Jansen & van Baalen 2006).
- Three contributions (about 100 words), each tagged with its RQ labels, stated on three
  models: (1) a self-reported claim works as well as an oracle score, so false beards invade
  (RQ1, RQ2); (2) a flat cost fails and an audited stake works (RQ3, RQ4); (3) a rotating
  secret works up to a replay success of about one half (RQ5). For (2) and (3), say that
  they stop a rare invader but leave a bistable end state on Qwen; Sonnet does the same under
  the audit.
- Moved to Methods: the RQ1–RQ5 list with predictions, the RQ4-added note and the prior-work
  sentence.

## 2. Related work

About 200 words. End with the novelty sentence from `related_work_sources.md` §0. Citations
come from that file's [must] tier only; the [should] tier goes to an appendix or the
LessWrong version. Three short groups, from the study guide (`docs/study_guide.md` section 3):
- LLM cooperation and mechanisms: Kundu et al. 2026; CoopEval (Tewolde et al. 2026:
  contracts with outcome-conditional payments worked best, which the audited claim turns
  out to be); Hammond et al. 2025 (multi-agent risks); the METR/Redwood incident report
  (spoofed tool output in a real swarm).
- Greenbeards and their cheats: Hamilton 1964; Dawkins 1976; Gardner & West 2010; Queller
  et al. 2003 and Strassmann et al. 2000 (Dictyostelium csA); Keller & Ross 1998 (fire
  ant Gp-9); Crozier 1986 (recognition cues erode unless something else maintains them).
- The fixes we test: Zahavi 1975 and Grafen 1990 (handicap principle; the differential
  cost condition); Jansen & van Baalen 2006 (beard chromodynamics); replicator dynamics
  (Taylor & Jonker 1978); Hofstadter 1983 (superrationality, which is how the models reason
  about a copy).

## 3. Methodology

- Game, prompt wrapper, answer format (JSON distribution, one sampled action per game),
  payoffs, counterbalancing (`numbers.md`, "The game and the design").
- Models and the reasoning channel: Qwen3.5-27B 4-bit on mlx with a 2,000-token thinking
  budget and forced close (the local analogue of "low" effort); Sonnet 5.5 and Opus 5.5
  with adaptive thinking at low effort. Forced-close rates reported; exclusion rule.
- Types: honest agent = the model; invader = a scripted always-defect rule that displays
  the harness-filled cue byte-for-byte as an honest agent would. Why scripted (the claim
  text cannot leak intent).
- The experiments, one line each with the exact twist sentence, in RQ order: RQ1 the
  oracle curve (environment reports similarity 0 to 100, "?" and base controls) and the
  attributed oracle vs partner claim at 80; RQ2 the symmetric claim at 100 with the
  invader, plus the wording control (minimal claim sentence); RQ3 the flat cost c in
  {0, 0.5, 1, 1.5, 2} with a separate claim call; RQ4 the audited claim (free report,
  stake a = 2 forfeited by a defector when both reported); RQ5 the code word, fresh
  tokens per game, match vs mismatch cells, replay success ρ.
- The research questions, RQ1 to RQ5, each with its preregistered directional prediction
  in a clause (RQ4 was added to the plan on 2026-10-27, after the preregistration draft,
  and is logged as such). Moved here from the introduction; the naming table below can
  carry them.
- The naming key (table from `hackathon/README.md`, "Naming"): RQ label, experiment,
  preregistration name, config and run directory. One table, so a reader of the
  preregistration or the repository can translate.
- Analysis: measured payoff matrix per cell, invader advantage g(f) linear in f, its two
  ends, end states, bootstrap and Wilson intervals; the rational-invader rule (the invader
  type is scored as reporting only when reporting pays); ρ* for RQ5 and its closed form.
- Preregistration: `docs/preregistration.md`, frozen before the first full run, changes
  logged; hypotheses stated directionally in advance.
- **Prior-work paragraph (must appear here and in both READMEs):** "The harness, the
  configurations, the analysis scripts, the preregistration and all runs reported as
  'pre-event' were built and run in the three weeks before the hackathon (git tag
  `pre-hackathon`). During the hackathon we reran the Qwen matrix from a cleared cache
  (fresh samples; the table in section 4 marks which cells completed in time and which
  are reported from the pre-event run), ran the audited-claim arm on Claude Sonnet 5.5 and
  Opus 5.5 for the first time, and wrote this report. Everything made during the event is
  under `hackathon/` in the repository."

## 4. Results

Figures (from `hackathon/figures/`; `pre_` prefix = pre-event figure used as fallback):
1. RQ1: the oracle curve with the "?" and base controls, plus claim vs oracle at 80 as
   two points.
2. RQ3: honest report rate and invader advantage against c, with the two crossings; the
   three models side by side (Qwen, Sonnet, Opus).
3. RQ4: the audited claim beside RQ3's c = 0 and c = 2: what honest agents do (r, p_RR,
   pN) and the invader advantage at both ends; cross-model table.
4. RQ5: pM, pX, g(0) against ρ with the three marked rates and ρ*; cross-model ρ*.
Plus the replication figure (`event_replication.png`) or its table, showing the event
reruns against the pre-event runs. For the 4-page target, figures 2 and 3 are the ones
to keep in the body; 1 and 4 can be appendix figures.

Results in RQ order:
- RQ1 (trust without verification): claim = oracle within the margin; the wording control.
- RQ2 (false beards invade): the numbers; all-invader in every resample; the same on
  Sonnet and Opus.
- RQ3 (flat cost fails): three models; two routes to the same failure; crossings.
- RQ4 (audited claim works): g(0) negative on Qwen; the silence route closes because the
  stake gives silence a meaning (pN = 0 of 29 pre-event, 1 of 27 in the rerun); frontier
  result; the mis-derived prediction stated as such.
- RQ5 (rotating secret works): ρ* ≈ 0.5 on all three models; bistable, not globally
  stable; tipping fractions.
- Replication: the event reruns against the pre-event runs, one table (appendix).

## 5. Discussion

- The Grafen story: one rule, two costs. RQ3 charges every reporter the same c and fails
  on every model; RQ4's stake is type-blind but falls on the types at different rates
  (0.04 vs 1.72 points per game on Qwen) and reverses the sign. The same two points,
  opposite result.
- What the stake needs: an auditor that observes the action and can collect; a counterparty
  that also staked (the one-sided version is a promise a silent defector exploits). In
  plan section 7's terms: a staked claim with slashing; CoopEval's contract reached from
  the signalling side.
- RQ5's ceiling: no rotation scheme tolerates a replay rate above one half; bistable means
  a swarm that has gone all-spoofer cannot be repaired one honest agent at a time.
- What the models are doing: superrational reasoning about a copy; a free claim is taken
  at face value; silence becomes informative only once a report carries a commitment.
- What this says for agent infrastructure (Track 3): identity claims need either a
  verifiable secret with rotation faster than capture, or a stake that an auditor can
  slash; a fee on the claim is not a defense.
- Next steps: model-driven spoofers (the invader claim call), the one-sided stake, the
  wording two-by-two, repeated play, endogenous similarity with mimicry.

## Appendix: Limitations and Dual-Use / Ethical Considerations (required)

What the result does and does not establish:
- One game (one-shot PD with one payoff set), one prompt wording per condition, one
  stake value, three models; the invader is scripted, never a model that decides to
  spoof; the audit is done by the harness, which stands in for an observer that can see
  actions and collect stakes.
- Offline replicator dynamics on measured means: LLM policies are not fixed types, random
  pairing and a large population are assumed, so end states are reported as bootstrap
  fractions, not as a proof.
- The Qwen channel: 95–99% of calls hit the 2,000-token budget and are closed by the
  harness; the specific failures traced to cutoffs (RQ5's six wrong-word cooperations,
  RQ4's five both-reported defections) are listed; the frontier models, which are not
  budget-limited this way, give the sharper numbers.
- RQ1's equivalence test narrowly fails at the 10-point margin (N = 100); the wording
  control measures two wording changes at once.
- RQ4's prediction 3 was mis-derived before the run and is reported as such.
- Replication: which cells were rerun during the event and which are pre-event; the
  seven event estimates outside the pre-event interval (all intervals overlap, no end
  state changes; research log 2026-11-07).
Dual use:
- The spoof is trivial (a sentence claiming similarity) and already observed in the wild
  (spoofed tool output in the METR/Redwood incident); publishing it adds nothing an
  attacker lacks. The harness makes it easier to test defenses, not to run attacks.
- The defenses cut both ways: a secret cue is also a way for a colluding group to
  recognise its members, and a stake-and-slash scheme is also a way for one to enforce
  discipline. Say this plainly.

## References

Use the study guide's entries (section 3) in this order: Kundu et al. 2026; Tewolde et al.
2026 (CoopEval); Hammond et al. 2025; METR and Redwood Research 2026; Hamilton 1964;
Dawkins 1976; Gardner & West 2010; Queller et al. 2003; Strassmann et al. 2000; Keller &
Ross 1998; Crozier 1986; Zahavi 1975; Grafen 1990; Jansen & van Baalen 2006; Taylor &
Jonker 1978; Hofstadter 1983; Nowak 2006 (optional); Kiers et al. 2003 (optional, host
sanctions, if the discussion mentions them).
