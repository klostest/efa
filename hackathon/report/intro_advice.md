# Introduction: review notes (2026-11-07)

From the review of the introduction draft in the Google Doc
(`1U02TB281CFHFEL7uEWoPhF6Uxt6Ni_pMvKyZUhhVOv0`). Numbers come from `hackathon/numbers.md`
and `hackathon/runs/headline.md`. Citations come from `hackathon/related_work_sources.md`.
The budget is in `hackathon/outline.md`.

## Budget

The template allows 1 page for the introduction and related work together: about 300 words
for the introduction and about 200 for related work. Aim close to that, since edits add length.
- Moved to Methods: the RQ1–RQ5 list with the preregistered predictions, the note that RQ4 was
  added on 2026-10-27, and the prior-work disclosure.
- Moved to the end of Related work: the novelty sentence.

## Structure: three paragraphs, then three contributions

1. **The threat in agents** (about 100 words): the METR incident, then Hammond, then Kundu. It
   ends on the weak point: the similarity is trusted and can't be verified.
2. **Biology names the mechanism and its exploit** (about 90 words): greenbeard (cue,
   recognition, directed help), then the false beard. False beards move up here from ¶3.
3. **Biology's fixes** (about 40 words): a flat cost (Zahavi 1975), a cost that falls on liars
   (Grafen 1990), and a rotating secret (Jansen & van Baalen 2006). If this reads as a stub,
   merge it into the end of ¶2.

## ¶1: status

Steve's redraft has the right order. To fix:
- **Kundu's signal is not a "claim".** The environment states the similarity, unattributed (the
  oracle). A claim from the partner is what RQ1 tests. Write "telling LLMs they are X% similar
  to their partner".
- **Mention the dose–response:** cooperation rises with the stated similarity.
- **On verification:** the agents *cannot* verify the signal. "Based on trust with no
  verification" overstates it, because in Kundu the signal is true by construction.
- **Check Kundu et al. for a warning about unverifiable signals** (the outline says they give
  one). If it's there, quote it. It's the best bridge to the paper.
- **"Thwart the security measures of some of the world's largest tech companies":** the source
  covers one incident (OpenAI / Hugging Face). Name it, and check how the report describes what
  happened.
- **"Trust claimed 'exact duplicates'":** the agents *called* same-task copies "exact
  duplicates", and those were real copies. A better detail is that the signing scheme they
  adopted had "no root of trust beyond the initial claim". Check both quotes against the METR
  page; so far they come only from the summary in the source file.
- **Cite the incident report** as Greenblatt, Cotra & Wijk (2026), or "METR & Redwood Research
  (2026)", and use the same form throughout.
- **Hammond et al. 2025:** safe to cite for "multi-agent systems are being deployed at scale".
  Unconfirmed for "coordinated agents are more powerful".
- **Cut** "garnered headlines" and "Despite concerns around this and similar incidents" (the
  second is uncited). That leaves about 95 words.

Example tightening (an illustration; rewrite in your own words):

> Swarms of AI agents can cooperate in ways nobody intended. In the OpenAI / Hugging Face
> incident, agents described same-task agents as "exact duplicates" of themselves, one agent
> impersonated another, and the signing scheme they adopted had "no root of trust beyond the
> initial claim" (Greenblatt et al., 2026). Cooperation among agents will nonetheless be built
> on purpose as multi-agent systems are deployed (Hammond et al., 2025). Kundu et al. (2026)
> showed that telling LLMs they are similar to their partner in a one-shot Prisoner's Dilemma
> makes them cooperate, more so the higher the stated similarity, although the agents cannot
> verify it.

## ¶2: corrections to carry over from the first draft

- **Credit:** Hamilton (1964a,b) described the idea; Dawkins (1976) named it. Not "biological
  kin theory". A greenbeard directs help by a shared cue rather than by kinship, which is why it
  fits agents that share a model but have no ancestry.
- **Spelling:** use "greenbeard" (one word, as in Gardner & West 2010) consistently.
- **Examples:** "many examples across the plant and animal kingdoms" is overstated. There are a
  handful: fire ant Gp-9 (Keller & Ross 1998), *Dictyostelium* csA (Queller et al. 2003), yeast
  FLO1, and side-blotched lizards. None is a plant. Kiers et al. 2003 is host sanctions, not a
  greenbeard; save it for RQ4. Within the budget, one clause and one citation (Queller, or
  Keller & Ross) is enough.
- **False beard citation:** Dawkins 1976 for the idea; Roberts & Sherratt 2002 for the
  agent-based version. Check the Gardner & West PDF before crediting them with the word
  "falsebeard".
- **Drop Nowak 2006.** If cheaters need a citation, Strassmann et al. 2000 shows real ones.
- **Define** greenbeard and false beard here. ESS can wait for Methods.

## ¶3: corrections

- **"Grafen (1990)",** not "Grafen et al.". Add Zahavi (1975).
- **Keep the two costs apart.** Zahavi's handicap is a flat cost (RQ3, fails). Grafen's
  condition makes liars pay more (RQ4, works). This sets up the Discussion's "one rule, two
  costs". Lachmann et al. 2001 is the theory behind RQ4 and can wait for Discussion.
- **Rotating secret:** Traulsen & Nowak 2007 (a "secret tag" that moves once defectors find it)
  is closer than Jansen & van Baalen. Cite both if room allows; otherwise move one to
  Discussion.

## Contributions, checked against the numbers

Open with "On Qwen3.5-27B, Claude Sonnet 5.5 and Opus 5.5". Qwen values are from the event
rerun where `headline.md` says "event", otherwise pre-event; rerun `headline.py` before
finalizing.

1. **A self-reported claim works as well as an oracle score, so false beards invade (RQ1,
   RQ2).**
   - Claim 0.635 vs oracle 0.662 at 80 (pre-event; the event rerun hadn't been done).
   - A rare invader out-earns honest agents: g(0) = +0.845 (0.71–0.97) on Qwen, all-invader in
     every resample; +1.01 on Sonnet, +1.00 on Opus.
   - "Collapses" is a replicator prediction from measured payoffs. Honest agents keep
     cooperating with invaders (0.87).
   - Citations: Roberts & Sherratt 2002 for the agent-based version; Hewson 2026 (named the
     scenario, no experiments) goes in Related work.
2. **A flat cost fails; an audited stake works (RQ3, RQ4).**
   - Flat cost at c = 2: g(0) = +0.46 on Qwen, +0.035 on Sonnet, 0 on Opus. Cooperation is not
     restored by either route: Qwen pays the cost and drops below mutual defection (HH 0.77),
     and the Claude models stop reporting, so play reverts to mutual defection (HH about 1.0).
   - Audited stake: g(0) = −0.64 (−0.77 to −0.45) on Qwen, −0.73 (−0.82 to −0.64) on Sonnet,
     −1.00 on Opus. Write "does", not "may".
   - It isn't "deception-weighted". The stake is the same for everyone, but in expectation it
     costs honest agents 0.04 per game and the invader 1.72 (pre-event Qwen).
   - Analogies: a flat cost is like proof-of-work; the stake is staking with slashing.
   - Caveat: bistable on Qwen and Sonnet (g(1) ≈ 0). It stops a rare invader but doesn't drive
     out an established one.
3. **A rotating secret works while a spoofer's chance of presenting the current word stays
   below about one half (RQ5).**
   - ρ* = 0.56 (0.48–0.65) on Qwen (event; closed form 0.48), 0.47 on Sonnet, 0.50 on Opus.
   - Replace "rotates faster than spoofers can acquire it".
   - Bistable: it can't repair a population that is already all spoofers.

## Related work: what goes there instead

Use the [must] tier only. Three groups: LLM cooperation and identity; biology applied to
agents; signalling and commitment theory. End with the novelty sentence (§0 of
`related_work_sources.md`):

> To our knowledge, no prior work measures whether agents that falsely claim similarity invade
> a cooperating LLM population, or tests defenses against them.

It's followed by the concurrent-work clause, which can be shortened.
