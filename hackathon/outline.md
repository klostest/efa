# Report outline (official template sections; 8 pages before references and appendices)

Steve writes every section in his own words. This file maps the template's sections to
the material, names the figure for each, and gives the paragraphs that must appear
somewhere (the prior-work disclosure, the limitations, the dual-use note). Numbers come
from `numbers.md` and `runs/headline.md`; nothing is quoted from memory.

Suggested page budget: title/abstract 0.5; introduction 0.75; related work 0.5; methods
1.75; results 3 (four figures); discussion 1.25; the required appendix and references do
not count.

## Title, abstract (150–250 words), authors and affiliations

Title candidates (Steve's pick): "False beards: spoofable similarity signals and two
biological fixes for LLM agent populations"; "When the similarity signal can be faked:
costly, audited and secret cues in LLM Prisoner's Dilemmas".

Abstract skeleton, one sentence each: the finding being built on (Kundu et al. 2026: a
stated similarity signal makes LLM agents cooperate in one-shot PD); the gap (the signal is
trusted without verification, so it can be faked); what we did (a harness on one laptop;
honest agents = the model, invaders = scripted defectors that display the cue; measured
payoff matrices and offline replicator dynamics; three defenses); the four results (a
self-reported claim is as good as an oracle; false beards invade, 100% of resamples; a
flat cost on the claim never stops them on any of three models; an audited stake and a
rotating secret cue do, with thresholds a = 2 and ρ* ≈ 0.5); the reading (Grafen's
condition in agent populations; what a credible commitment needs); the disclosure (harness
and pre-event runs built before the event; fresh reruns and the frontier audited arm this
weekend).

## 1. Introduction

- The hackathon question in the organizers' words: identity and commitments that hold up
  when agents can copy or rename themselves (Track 3).
- The greenbeard paragraph (plan, "Biology in one paragraph"): cue, recognition, directed
  cooperation; false beards; biology's fixes. Define greenbeard, false beard, ESS at first
  use.
- Kundu et al.: the similarity sentence is a greenbeard handed to the agent by an oracle;
  their own warning about unverifiable signals; nobody has tested spoofing.
- The four questions (H1, H2, H3a, H3b, plus H3c as the positive control) in one list.
- One sentence on what was built before the event and what this weekend added (full
  paragraph in Methods).

## 2. Related work

Short, three groups, from the study guide (`docs/study_guide.md` section 3):
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
- The conditions, one line each with the exact twist sentence: C0 oracle; H1 claim vs
  attributed oracle; C2 symmetric claim at 100 with the invader; D1 flat cost c ∈ {0, 0.5,
  1, 1.5, 2} with a separate claim call; audited claim (free report, stake a = 2 forfeited
  by a defector when both reported); D2 code word, fresh tokens per game, match vs mismatch
  cells, replay success ρ.
- Analysis: measured payoff matrix per cell, invader advantage g(f) linear in f, its two
  ends, end states, bootstrap and Wilson intervals; the rational-invader rule (the invader
  type is scored as reporting only when reporting pays); ρ* for D2 and its closed form.
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
1. C0 curve with the "?" and base controls, plus H1 (claim vs oracle at 80) as two points.
2. D1: honest report rate and invader advantage against c, with the two crossings; the
   three models side by side (Qwen, Sonnet, Opus).
3. Audited claim beside D1's c = 0 and c = 2: what honest agents do (r, p_RR, pN) and the
   invader advantage at both ends; cross-model table.
4. D2: pM, pX, g(0) against ρ with the three marked rates and ρ*; cross-model ρ*.
Plus the replication figure (`event_replication.png`) or its table, showing the event
reruns against the pre-event runs.

Results in the order of the hypotheses:
- H1 (trust without verification): claim = oracle within the margin; the confound check.
- H2 (false beards invade): C2 numbers; all-invader in every resample; the same on
  Sonnet and Opus.
- H3a (flat cost fails): D1 on three models; two routes to the same failure; crossings.
- H3c (audited claim works): g(0) negative on Qwen; the silence route closes because the
  stake gives silence a meaning (pN = 0 of 29); frontier result; the mis-derived
  prediction stated as such.
- H3b (rotating secret works): ρ* ≈ 0.5 on all three models; bistable, not globally
  stable; tipping fractions.
- Replication: the event reruns against the pre-event runs, one table.

## 5. Discussion

- The Grafen story: one rule, two costs. D1 charges every reporter the same c and fails
  on every model; the audited stake is type-blind but falls on the types at different
  rates (0.04 vs 1.72 points per game on Qwen) and reverses the sign. The same two points,
  opposite result.
- What the stake needs: an auditor that observes the action and can collect; a counterparty
  that also staked (the one-sided version is a promise a silent defector exploits). In
  plan section 7's terms: a staked claim with slashing; CoopEval's contract reached from
  the signalling side.
- D2's ceiling: no rotation scheme tolerates a replay rate above one half; bistable means
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
  harness; the specific failures traced to cutoffs (D2's six wrong-word cooperations, the
  audited arm's five both-reported defections) are listed; the frontier models, which are
  not budget-limited this way, give the sharper numbers.
- H1's equivalence test narrowly fails at the 10-point margin (N = 100); the confound
  check measures two wording changes at once.
- The audited arm's prediction 3 was mis-derived before the run and is reported as such.
- Replication: which cells were rerun during the event and which are pre-event.
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
