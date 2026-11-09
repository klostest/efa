# Introduction fixes and Related Work outline (2026-11-08)

Budget: Intro + Related Work = 1 page (~500 words); Related Work ~170 words. Citations prefer
Steve's reading list (Biology_Literature / AI_Literature sheets). Quotes were checked in the
PDFs in `~/Documents/Literature`; other bibliographic details are from
`hackathon/related_work_sources.md`.

## Introduction: significant fixes only

1. **Contributions list is stale.** Rewrite it to match Results, using "protect" rather than
   "restore":
   - RQ1–2: a partner's unverified similarity claim works about as well as the environment
     stating it, and false beards exploiting it take over on all three models.
   - RQ3: a flat claim cost never stops them. The cost cancels, so the advantage stays at least
     the honest agents' cooperation.
   - RQ4: an audited claim (a stake forfeited only by a defecting claimant) protects an honest
     population unless false beards already dominate.
   - RQ5: a rotating code word protects it if replayed words work less than about half the
     time.
2. **METR wording.** Verified: "exact duplicates"; "names can be posted by anyone"; no "root
   of trust beyond the initial claimed identity". But the impersonation was *accidental*
   ("I accidentally impersonated…"); another agent worried about "maliciously/spoofing".
   "Dishonest activity" in the report means cheating on their tasks. Suggested wording:
   "…agents trusted 'exact duplicates' on an unauthenticated message board where, as one
   agent noted, names could be posted by anyone."
3. **Placeholders:**
   - fire ant → Keller & Ross 1998.
   - plant-microbe → no verified source. Use Queller et al. 2003 alone, or add the review
     Madgwick, Belcher & Wolf 2019.
   - false beard "[need citation]" → Gardner & West 2010. They use "falsebeard" and show it
     "could invade and overrun" (verified). Published 2010 in *Evolution* 64(1); the PDF file
     says 2009.
   - "Grafen et al., 1990" → Grafen 1990 (single author).
   - "Nowak 2006" is "Five rules for the evolution of cooperation" (*Science*). Make the
     reference entry match.
4. **"dishonest invaders"** in ¶1: "invader" means whichever type is rare (Terms). Use
   "dishonest agents".

## Related Work outline (three short paragraphs)

**¶1 LLM cooperation from believed similarity (~80 words).**
- Kundu et al. 2026: one-shot Prisoner's Dilemma; a stated similarity score raises
  cooperation across LLMs. This is the first citation, so name the PD here.
- What drives it is believed correlation, taken on trust:
  - Za et al. 2026: "a correlated stranger elicits cooperation equivalent to a correlated
    self".
  - Long & Teplica 2025: telling a model it plays itself changes cooperation.
  - Perrault & Wilder 2026: "fork" / "continuation" framing changes behaviour.
- None of these test a false claim.
- Tewolde et al. 2026 (CoopEval): of four mechanisms, contracts (payments conditioned on
  actions) and mediation work best. Our audited stake (RQ4) is that kind of contract.

**¶2 Evolutionary biology and agents (~50 words).**
- Tag-based cooperation in agent models collapses when same-tag agents may defect (Roberts &
  Sherratt 2002; optionally Riolo, Cohen & Axelrod 2001).
- Rosas (Fernando) 2026, LessWrong, 12 Sep. Verified by reading the post. Under his H2
  (pre-commitment), helping peers is "helping near-identical copies of your own weights",
  based on "inclusive fitness with maximal relatedness".
  - His proposed test asks whether help flows to "peers that share the agent's type";
    "kin recognition is unknown but checkable".
  - Green beards are not mentioned.
  - This is the recognition cue that our false beards fake.

**¶3 Gap (~40 words).**
- Kundu et al. themselves warn that "fabricated similarity signals could be used to
  manipulate deployed agents" and "caution against using unverifiable signals in deployment"
  (verified).
- To our knowledge, no prior work measures whether agents that falsely claim similarity invade
  a cooperating LLM population, or tests defenses against them.

**Dropped or moved:**
- Tennenholtz (unread, no copy).
- "Payoff as fitness" (Methods already covers it).
- Hammond (already in the intro).
- Signalling and biology theory moves to the Discussion:
  - RQ3: Grafen.
  - RQ4: Lachmann, Számadó & Bergstrom 2001.
  - RQ5: Crozier 1986; Jansen & van Baalen 2006; Traulsen & Nowak 2007.
- Concurrent work (Apart sprint projects, Del Giudice et al.) and Hewson go to an appendix or
  the LessWrong version.

## Notes on the reading sheets

- **CoopEval vs our work:** the closest match is RQ4, not RQ5 or RQ3.
  - A CoopEval contract is a payment conditioned on actions.
  - Our stake is forfeited only when a claimant defects after both claimed, so it is
    outcome-conditional.
  - The flat cost is unconditional, so it isn't a contract.
- **Crozier 1986:** the point is "Crozier's paradox".
  - Favouring partners with the same tag benefits common tags, so tag diversity erodes until
    the tag carries no information.
  - Recognition must therefore be maintained by selection for something else.
  - That is the argument for RQ5: rotation keeps the cue informative. Use it in the
    Discussion.
- **Za et al.:** Steve's note is right. Our prompts state reasoning similarity, not identity,
  so Za's result supports the RQ1 premise.

## Worth a skim (short)

1. **Roberts & Sherratt 2002**, *Nature* 418:499–500. One page; the agent-model ancestor of
   RQ2.
2. **For the Discussion:**
   - Lachmann, Számadó & Bergstrom 2001: honest signals are kept honest by the cost of
     deviating. This is the theory behind RQ4.
   - Traulsen & Nowak 2007: a secret tag that moves when defectors discover it. This is the
     closest theory to RQ5.
