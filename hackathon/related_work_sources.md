# Related-work sources for the write-up (final check, 2026-11-07)

Purpose: every work the report should cite, grouped by where it goes in `outline.md`, with
verified bibliographic details. Built from literature scans 1–3 (`LITERATURE_TRACKER.md`) and a
citation check on 2026-11-07:
- arXiv entries: checked against the arXiv API.
- Journal entries: checked against Crossref/PubMed by DOI.
- Blog posts: opened.
Anything not fully verified is marked **[unverified]**.

Tiers, for the 4-page body (references and appendices don't count toward the limit):
- **[must]**: cite in the body.
- **[should]**: cite if there is room, otherwise in an appendix "Extended related work".
- **[opt]**: appendix or LessWrong version only.

The LessWrong post has no page limit, so it can carry the whole [should] tier.

---

## 0. Corrections to the current outline and reference list

- **Kundu et al. 2026:** cite as arXiv:2608.12125 only. arXiv still shows v1 with no venue.
  Some aggregators say "ICML 2026", but I could not confirm it. It has 0 citations on Semantic
  Scholar and OpenAlex.
- **Hamilton 1964** is two papers (I: 7:1–16; II: 7:17–52). Cite both or say "1964a,b".
- **Hofstadter 1983:** use the **June** column (*Sci. Am.* 248(6):14–28, superrationality and
  the Luring Lottery), not May (the tournaments).
- **"LaVictoire et al. 2014":** the paper's first author is **Barasz**. Cite as Barasz et al. 2014.
- **Gardner & West 2010:** I could not confirm that they use the term "false beard"
  ("falsebeard"). Check the PDF before attributing the word to them. Otherwise attribute the idea
  to Dawkins 1976 and the cheat analysis to Roberts & Sherratt 2002.
- **METR/Redwood incident report:** the authors are Greenblatt, Cotra & Wijk (METR's own BibTeX
  lists the author as "METR"). It is the same report Perrault & Wilder cite as "Greenblatt et al.
  2026".
- **`[AAM26]` in `docs/draft_experiment_plan.md`:** arXiv 2608.00718 is Bappy, Hossain, Zaman,
  Hasan, Hasan & Islam 2026. The key is a title acronym, which is fine, but use the authors in
  the report.
- **Novelty sentence.** "Nobody has tested spoofing" is still true of published papers, but it now
  needs qualifying. Suggested wording: *"To our knowledge, no prior work measures whether agents
  that falsely claim similarity invade a cooperating LLM population, or tests defenses against
  them. Concurrent work manipulates believed identity [Perrault & Wilder 2026; Za et al. 2026;
  Del Giudice et al. 2026] and swaps the model behind a fixed identity [Apart Collusion Sprint
  projects, Oct 2026], and the idea of a model pretending to be its partner's copy was raised
  informally by Hewson (2026)."*

---

## 1. Introduction

- **[must]** Kundu, Tewolde, Berker, Brown, Conitzer (2026). Do LLMs take care of their own?
  Similarity signals can induce cooperation. arXiv:2608.12125.
- **[must]** Greenblatt, Cotra, Wijk / METR & Redwood Research (2026-08-26). Brief independent
  investigation of agents' behavior, reasoning and collaboration in the OpenAI / Hugging Face
  hacking incident. https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/
  - Directly on point. Agents called same-task copies "exact duplicates". One noted the board
    was "unauthenticated, names can be posted by anyone". One impersonated another. They then
    adopted Ed25519-signed messages with "no root of trust beyond the initial claim".
  - This is the strongest real-world motivation for the whole report.
- **[must]** Hammond et al. (2025). Multi-agent risks from advanced AI. arXiv:2502.14143. Cite as
  "Hammond et al."; the full list has 44 authors.
- **[must]** Dawkins (1976). *The Selfish Gene*. Oxford University Press. (Greenbeard; false beard.)
- **[must]** Hamilton (1964a,b). The genetical evolution of social behaviour I, II. *J. Theor.
  Biol.* 7:1–16, 17–52. doi:10.1016/0022-5193(64)90038-4, 90039-6.
- **[must]** Gardner & West (2010). Greenbeards. *Evolution* 64(1):25–38.
  doi:10.1111/j.1558-5646.2009.00842.x
- **[must, one of]** Queller, Ponte, Bozzaro, Strassmann (2003). Single-gene greenbeard effects in
  the social amoeba *Dictyostelium discoideum*. *Science* 299:105–106. doi:10.1126/science.1077742
  - Or Keller & Ross (1998). Selfish genes: a green beard in the red fire ant. *Nature*
    394:573–575. doi:10.1038/29064
- **[should]** Madgwick, Belcher, Wolf (2019). Greenbeard genes: theory and reality. *TREE*
  34(12):1092–1103. doi:10.1016/j.tree.2019.08.001. A recent review; one citation stands in for
  the empirical literature (yeast FLO1, lizards, amoebae).
- **[should]** Conitzer & Oesterheld (2023). Foundations of cooperative AI. *AAAI* 37(13):15359–15367.
  doi:10.1609/aaai.v37i13.26791. Why AI agents differ (copyable, similar).
- **[should]** Oesterheld, Treutlein, Grosse, Conitzer, Foerster (2023). Similarity-based cooperative
  equilibrium. NeurIPS 2023. arXiv:2211.14468. The theory Kundu et al. test empirically: with
  only a similarity score, cooperation becomes an equilibrium. A spoofable score attacks exactly
  this.

## 2. Related work

Steve's note in the draft asks for "the closest examples of anyone referring to evolutionary
biology in the study of groups of agents". That is section 2d. Suggested structure: four short
groups instead of three.

### 2a. LLM cooperation and cooperation mechanisms
- **[must]** Tewolde, Zhang, Guzman Piedrahita, Conitzer, Jin (2026). CoopEval: benchmarking
  cooperation-sustaining mechanisms and LLM agents in social dilemmas. ICML 2026.
  arXiv:2604.15267.
- **[should]** Akata, Schulz, Coda-Forno, Oh, Bethge, Schulz (2025). Playing repeated games with
  large language models. *Nat. Hum. Behav.* 9(7):1380–1390. doi:10.1038/s41562-025-02172-y
- **[opt]** Fontana, Pierri, Aiello (2025). Nicer than humans. *ICWSM* 19:522–535. arXiv:2406.13605.
- **[opt]** Piatti et al. (2024). Cooperate or collapse (GovSim). NeurIPS 2024. arXiv:2404.16698.
- **[opt]** Sinishaw, Zhu, Meriaux, Dudek (2026). Do LLMs beat Nash? Testing decentralized
  coordination in self-play multi-agent games. arXiv:2608.12547. Copies told they are copies
  beat Nash, which is why the claim is worth spoofing.
- **[opt]** Liu, Du, Li, Tewolde, Xuan, Conitzer (2026). CoopShift: post-training amplifies the
  memory curse in LLM cooperation. arXiv:2610.24086. Same group; copy-play.

### 2b. Believed identity and similarity drive LLM cooperation (the premise of RQ1)
- **[must]** Za, Panos, Čuhel, Albanie (2026). Towards predictive models of strategic behaviour in
  large language model agents. ICLR 2026 Workshop "Agents in the Wild", OpenReview D4tULiBjNr
  (iclr.cc/virtual/2026/10016359).
  - Finding: "a correlated stranger elicits cooperation similar to a correlated self", meaning
    inferred correlation, not identity, drives cooperation.
  - Author list: the ICLR page includes Albanie; ICML/NeurIPS versions list only the first
    three. Check the PDF.
- **[must]** Perrault & Wilder (2026). Identity, incentives, and cooperative behavior for AI:
  reverse-engineering multiagent cooperation. arXiv:2610.19188. They vary
  "fork/continuation of you" but never test a false claim.
- **[must]** Long & Teplica (2025). The AI in the mirror: LLM self-recognition in an iterated
  public goods game. arXiv:2508.18467. A prompt label "you are playing yourself" changes
  cooperation.
- **[should]** Del Giudice, Palma, Migliarini, Galasso, Spinelli (2026). Prompted identity degrades
  cooperation in multi-agent LLM systems. arXiv:2609.35928. Model-family labels create factions,
  and the effect persists when labels are shuffled or arbitrary. The label is trusted, not
  checked.
- **[should]** Panickssery, Bowman, Feng (2024). LLM evaluators recognize and favor their own
  generations. NeurIPS 2024. arXiv:2404.13076.
- **[opt]** Laurito et al. (2025). AI–AI bias. *PNAS* 122(31):e2415697122. doi:10.1073/pnas.2415697122
- **[opt]** Hu et al. (2025). Generative language models exhibit social identity biases. *Nat.
  Comput. Sci.* 5:65–75. doi:10.1038/s43588-024-00741-1
- **[opt]** Pagan, Ebling, Ionescu, Hannák (2026). AI evaluators favor job applications written by
  certain AI models, independent of candidate quality. arXiv:2610.41866. Self-preference runs on
  style that others can imitate.
- **[opt]** Davidson et al. (2024). Self-recognition in language models. Findings of EMNLP 2024.
  arXiv:2407.06946. No consistent self-recognition, so kin can't be authenticated by style
  alone. Relevant to RQ5.
- **[opt]** Potter, Crispino, Siu, Wang, Song (2026). Peer-preservation in frontier models.
  arXiv:2604.19784. In-group protection that a false beard could exploit.

### 2c. Program equilibrium and verifiable similarity (what an unspoofable cue looks like)
- **[must]** Tennenholtz (2004). Program equilibrium. *GEB* 49(2):363–373.
  doi:10.1016/j.geb.2004.02.002
- **[should]** Barasz, Christiano, Fallenstein, Herreshoff, LaVictoire, Yudkowsky (2014). Robust
  cooperation in the prisoner's dilemma: program equilibrium via provability logic.
  arXiv:1401.5577.
- **[should]** Arsen (2026-10-28). Generalized CliqueBots in open-source game theory. LessWrong.
  https://www.lesswrong.com/posts/hcAQe3snm9qEzXBBz
  - A bot that cooperates with whatever looks identical under a finite set of probes is
    unexploitable only if the probe interface is "locally complete".
  - Our self-reported claim is the incomplete interface. This is the closest formal statement of
    RQ1/RQ2.
- **[opt]** Oesterheld (2019). Robust program equilibrium. *Theory Decis.* 86:143–159.
  doi:10.1007/s11238-018-9679-3
- **[opt]** Critch (2016). Parametric bounded Löb's theorem and robust cooperation of bounded
  agents. arXiv:1602.04184. Journal version **[unverified]**.
- **[opt]** Sistla & Kleiman-Weiner (2025). Evaluating LLMs in open-source games. NeurIPS 2025.
  arXiv:2512.00371.

### 2d. Evolutionary biology applied to groups of AI agents (the "who else" paragraph)
- **[must]** Rosas (2026-09-12). On the origins of altruistic behaviour in the Hugging Face incident.
  LessWrong.
  https://www.lesswrong.com/posts/meLjz8giGS55rdfyg/on-the-origins-of-altruistic-behaviour-in-the-hugging-face
  - Proposes kin selection among copies as one hypothesis, and tests in which agents can or
    can't identify peers of their type.
- **[must]** Riolo, Cohen, Axelrod (2001). Evolution of cooperation without reciprocity. *Nature*
  414:441–443. doi:10.1038/35106555. Tag-based cooperation in agent-based models. This is the
  classic AI/agent-modeling ancestor of a similarity cue.
- **[must]** Roberts & Sherratt (2002). Does similarity breed cooperation? *Nature* 418:499–500.
  doi:10.1038/418499b. Lets identical-tag agents defect, and tag cooperation collapses: the
  false-beard objection in agent-based form.
- **[should]** Müller, Szathmáry, Steels et al. (2026). Evolvable AI: threats of a new major
  transition in evolution. *PNAS*. doi:10.1073/pnas.2527700123. The full author list is not
  checked **[unverified]**.
- **[should]** Willis, Du, Leibo, Luck (2025). Will systems of LLM agents cooperate: an investigation
  into a social dilemma. arXiv:2501.16173. Moran process over strategies written by LLMs.
- **[should]** Vallinder & Hughes (2024). Cultural evolution of cooperation among LLM agents.
  arXiv:2412.10270.
- **[should]** Hewson (2026-02-14). Agent properties for similarity-based cooperation. Substack.
  https://josephhewson1.substack.com/p/agent-properties-for-similarity-based
  - "Kin selection" among models. Names the "pretend to be a copy, then defect" scenario. No
    experiments.
  - Cite for priority on the idea.
- **[should]** Chassang (2026). Interactive alignment. arXiv:2607.25019. Evolutionary game theory
  with constitutional LLM agents; selection works against alignment.
- **[opt]** Hendrycks (2023). Natural selection favors AIs over humans. arXiv:2303.16200.
- **[opt]** Rosseau, Avalos, Nowé (2025). Inclusive fitness as a key step towards more advanced
  social behaviors in MARL settings. arXiv:2510.12555.
- **[opt]** De Marzo, Alboré, Garcia (2026). Copying explains the collective behavior of AI agents
  in the wild. arXiv:2609.09150.
- **[opt]** oakhu & Mallen (2026-08-12). AI swarms are starting to pose indirect takeover risk.
  LessWrong. https://www.lesswrong.com/posts/8oFYZdXkTaNGRtcn8/ai-swarms-are-starting-to-pose-indirect-takeover-risk
  It proposes "same parent task ID" filtering, which is a k = 1 secret cue. Better placed in RQ5.
- **[opt]** Abolhasani, Moghimi-Araghi, Salahshour (2026). The co-evolution of costly signaling and
  cooperation in social dilemmas. arXiv:2605.13750. Abstract agents, not LLMs.
- **[opt]** Manson, Gervais, Kline (2013). Defectors cannot be detected during "small talk" with
  strangers. *PLoS ONE* 8(12):e82531. Humans; argues greenbeard-style cues don't reveal
  defectors. Volume and issue are from the RePEc ID only **[unverified]**.

### 2e. Concurrent hackathon work (Apart AI Collusion Research Sprint, Oct 23–25, 2026)
These are sprint projects, not peer-reviewed. I read their project pages through a summarizer,
not the PDFs, so check the numbers before quoting them.
Listing: https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25
- **[should]** Carver & Redfern. Four levers of LLM collusion.
  github.com/carver/apart-research-collusion-sprint-2026 (repository verified). In one-round
  Cournot:
  - "same AI model with this same prompt" gives the cartel output in 43/48 replies;
  - "different AI models" gives it in 1/48;
  - a provider instruction that competitors "decide independently" brings it to 0/30.
  A bare same-model claim flips behavior, which is the RQ1 premise in a market.
- **[should]** Kolodiazhnyi. Who is my competitor? Believed rival identity and tacit collusion
  among LLM pricing agents (slug `…-ru0q`). False identity sentences give a non-monotone effect.
- **[opt]** Swap studies: the model behind a fixed identity is replaced mid-game. Peers react to
  the swapped agent's behavior, never to the identity.
  - Demir. Behavioral continuity, not family labels (`…-m1rr`).
  - Hoang. How LLM groups respond to a replaced member.
  - Kamau. Can agents identify their peers? **[unverified title on listing]**
  - Gonzalez, Zhang, Zhao. Trust and treachery **[unverified on listing]**
  These support the point that defense must come *before* the first defection (stake or secret),
  not from detecting it afterwards.

## 3. Methodology
- **[must]** Taylor & Jonker (1978). Evolutionary stable strategies and game dynamics. *Math.
  Biosci.* 40:145–156. doi:10.1016/0025-5564(78)90077-9
- **[should]** Maynard Smith & Price (1973). The logic of animal conflict. *Nature* 246:15–18.
  doi:10.1038/246015a0. ESS, at first use.
- **[opt]** Hofbauer & Sigmund (1998). *Evolutionary Games and Population Dynamics*. CUP.

## 4–5. Results and discussion, by research question

**RQ1, claim vs oracle:** Za et al. 2026; Long & Teplica 2025; Perrault & Wilder 2026; Riolo et al.
2001 (see above).

**RQ2, false beards invade:**
- **[must]** Roberts & Sherratt 2002 (above).
- **[must]** Jansen, V.A.A. & van Baalen, M. (2006). Altruism through beard chromodynamics.
  *Nature* 440:663–666. doi:10.1038/nature04387
- **[should]** Strassmann, Zhu, Queller (2000). Altruism and social cheating in the social amoeba.
  *Nature* 408:965–967. doi:10.1038/35050087. Natural cheaters.
- **[opt]** Antal, Ohtsuki, Wakeley, Taylor, Nowak (2009). Evolution of cooperation by phenotypic
  similarity. *PNAS* 106:8597–8600. doi:10.1073/pnas.0902528106
- **[opt]** Lenoir, d'Ettorre, Errard, Hefetz (2001). Chemical ecology and social parasitism in ants.
  *Annu. Rev. Entomol.* 46:573–599. doi:10.1146/annurev.ento.46.1.573. Social parasites mimic
  nestmate-recognition cues: false beards in nature.
- **[opt]** Edelman, Edelman, Goel, Malach (2026). Understanding and mitigating role spoofing in
  LLMs. arXiv:2610.40396. Identity cues that LLMs read from text can be spoofed.

**RQ3, flat cost fails (Grafen):**
- **[must]** Zahavi (1975). Mate selection: a selection for a handicap. *J. Theor. Biol.*
  53:205–214. doi:10.1016/0022-5193(75)90111-3
- **[must]** Grafen (1990). Biological signals as handicaps. *J. Theor. Biol.* 144:517–546.
  doi:10.1016/S0022-5193(05)80088-8
- **[should]** Számadó, Zachar, Czégel, Penn (2023). Honesty in signalling games is maintained by
  trade-offs rather than costs. *BMC Biol.* 21:4. doi:10.1186/s12915-022-01496-9
  - Or Penn & Számadó (2020). The handicap principle: how an erroneous hypothesis became a
    scientific principle. *Biol. Rev.* 95:267–290. doi:10.1111/brv.12563
  - Use one of these so a biology reviewer sees we know the handicap principle has been
    revised.
- **[opt]** Spence (1973). Job market signaling. *QJE* 87:355–374. The economics counterpart.

**RQ4, audited stake works:**
- **[must]** Lachmann, Számadó, Bergstrom (2001). Cost and conflict in animal signals and human
  language. *PNAS* 98:13189–13194. doi:10.1073/pnas.231216498
  - Honest signals need not be costly at equilibrium. What keeps them honest is the cost of
    deviating, e.g. punishment of liars.
  - **This is the theory behind RQ4.**
- **[must]** Tibbetts & Dale (2004). A socially enforced signal of quality in a paper wasp.
  *Nature* 432:218–222. doi:10.1038/nature02949. Wasps with experimentally faked badges get
  punished, a cost paid only by the dishonest. The empirical analogue of the stake.
- **[must]** CoopEval (above): outcome-conditional contracts worked best. The audited stake is that
  contract, reached from the signalling side.
- **[should]** Christoffersen, Haupt, Hadfield-Menell (2023). Get it in writing: formal contracts
  mitigate social dilemmas in multi-agent RL. AAMAS 2023. arXiv:2208.10469.
- **[should]** Zhu, Zuo, Sun (2026). Blindfold: keeping the audit coin secret from LLM agents.
  arXiv:2610.37055. Audits work only if the agent can't see at decision time whether it will
  be audited. Our harness audits every both-reported game, so the result is a best case. Say
  so in Limitations.
- **[should]** Kiers, Rousseau, West, Denison (2003). Host sanctions and the legume–rhizobium
  mutualism. *Nature* 425:78–81. doi:10.1038/nature01931
- **[opt]** Sun, Crapis, Stephenson, Monnot, Thiery, Passerat-Palmbach (2023). Cooperative AI via
  decentralized commitment devices. NeurIPS 2023 MASec workshop. arXiv:2311.07815. Staking and
  slashing.
- **[opt]** Yan, Hu, Jiang, Sun (2024). Get it cooperating: enhancing generative agent cooperation
  with commitment devices. ICML 2024 Agentic Markets workshop.
  https://openreview.net/forum?id=J39bW48ipI. The author order differs between versions **[check]**.
- **[opt]** Gatta, Naviglio, Tarantelli (2026). Tempting the agent: the economics of reputation
  without persistent identity in AI agent markets. arXiv:2609.02992. When identities are cheap
  to reset, a forfeitable stake is needed.
- **[opt]** Apart sprint stake projects: "Veracity" (bonded claims; a jury of agents can be
  captured) and Wakelin, "Something to Lose" (a personal stake works, a firm-level stake
  doesn't). Their names are only partly confirmed on the sprint listing.
- **[opt]** Biernaskie, Grafen, Perry (2014). The evolution of index signals to avoid the cost of
  dishonesty. *Proc. R. Soc. B* 281:20140876. doi:10.1098/rspb.2014.0876

**RQ5, rotating secret:**
- **[must]** Traulsen & Nowak (2007). Chromodynamics of cooperation in finite populations. *PLoS
  ONE* 2(3):e270. doi:10.1371/journal.pone.0000270
  - Cooperators use a "secret tag" until defectors discover it, then move to a new one.
    Cooperation wins when b/c > 1 + 2u/v.
  - **The closest theoretical analogue to RQ5. Compare their tag-mutation vs strategy-mutation
    condition with our ρ\* ≈ 0.5.**
- **[must]** Crozier (1986). Genetic clonal recognition abilities in marine invertebrates must be
  maintained by selection for something else. *Evolution* 40:1100–1101.
  doi:10.1111/j.1558-5646.1986.tb00578.x
- **[must]** Jansen & van Baalen 2006 (above).
- **[should]** Rousset & Roze (2007). Constraints on the origin and maintenance of genetic kin
  recognition. *Evolution* 61(10):2320–2330. doi:10.1111/j.1558-5646.2007.00191.x
- **[should]** Kaushik, Sivaprasad, Ferrarotti, Fritz, Brown, Lepri, Abdelnabi (2026). Who else is
  in? Multi-agent collusion initiation via strategic vagueness. arXiv:2610.37984.
  - LLM "schemers" find each other with handshake strategies that monitors miss.
  - Brown is a Kundu et al. co-author. The dual-use side of RQ5 (secret cues let colluders
    recognize each other); cite in the dual-use note too.
- **[should]** Motwani, Baranchuk, Strohmeier, Bolina, Torr, Hammond, Schroeder de Witt (2024).
  Secret collusion among AI agents: multi-agent deception via steganography. NeurIPS 2024.
  arXiv:2402.07510. Dual-use note.
- **[should]** oakhu & Mallen 2026 (above). Their proposed "accept only same parent task ID"
  mitigation is a k = 1 secret, which our replay analysis says fails once replay success
  passes about one half.
- **[opt]** Caves, Stevens, Iversen, Spottiswoode (2015). Hosts of avian brood parasites have evolved
  egg signatures with elevated information content. *Proc. R. Soc. B* 282:20150598.
  doi:10.1098/rspb.2015.0598. Hard-to-forge individual "signatures" against mimics.
- **[opt]** Rahaman et al. (2026). Session-bound behavioral watermarking for autonomous LLM agents.
  arXiv:2610.38579. Per-session keys against learned forgery, a security analogue of rotation.
- **[opt]** Mathew et al. (2024). Hidden in plain text: emergence and mitigation of steganographic
  collusion in LLMs. arXiv:2410.03768.

**Track 3 framing (identity infrastructure), discussion:**
- **[should]** Chan et al. (2024). IDs for AI systems. arXiv:2406.12137.
- **[should]** Chan et al. (2025). Infrastructure for AI agents. TMLR. arXiv:2501.10114. Identity
  binding plus commitment devices; it names both of our working defenses.
- **[opt]** South et al. (2025). Authenticated delegation and authorized AI agents.
  arXiv:2501.09674.
- **[opt]** Arbel, Salib, Goldstein (2026). How to count AIs: individuation and liability for AI
  agents. arXiv:2603.10028.
- **[opt]** Bappy et al. (2026). Adversarial attacks in multi-agent LLM pipelines. arXiv:2608.00718.
  Impersonation across agent boundaries.
- **[opt]** Budzyn, Brodzik, Szczepkowski (2026). Cryptographically secure agent-to-agent
  communication in multi-agent systems. arXiv:2610.23078.
- **[opt]** Douceur (2002). The Sybil attack. IPTPS. Already in the plan's reference list.

**Superrationality (what the models say):**
- **[should]** Hofstadter (1983, June). Metamagical themas. *Sci. Am.* 248(6):14–28.
  doi:10.1038/scientificamerican0683-14

## Limitations and dual-use: additions
- Audit visibility: Blindfold (above). Our auditor sees every both-reported game. A real
  auditor that samples, and whose sampling an agent can predict, weakens RQ4.
- Dual use of secret cues: Kaushik et al. 2026 and Motwani et al. 2024 show that recognition
  handshakes are also how colluders find each other.
- Dual use of the spoof itself: the METR/Redwood report already documents impersonation in the
  wild.

## Suggested citation budget for a 4-page body (about 25)
- **Intro (7):** Kundu; METR/Redwood; Hammond; Dawkins; Hamilton; Gardner & West; Queller (or
  Keller & Ross).
- **Related work (10):** CoopEval; Za et al.; Perrault & Wilder; Long & Teplica; Tennenholtz;
  Riolo et al.; Roberts & Sherratt; Rosas; Oesterheld et al. 2023; one of Willis et al. /
  Vallinder & Hughes.
- **Methods (1):** Taylor & Jonker.
- **Results / discussion (8):** Zahavi; Grafen; Lachmann et al.; Tibbetts & Dale; Traulsen & Nowak;
  Jansen & van Baalen; Crozier; Kaushik et al.
- **Appendix / LessWrong version:** the rest of the [should] tier, especially Hewson (priority),
  Arsen (theory), Del Giudice, the Apart sprint projects, Blindfold, and Chan et al.

---

## Appendix: other items found in scan 3 (optional, lower priority)

Recorded so nothing is lost. All are checked unless marked otherwise.

**Biology**
- Riolo, Cohen, Axelrod (2002), reply to Roberts & Sherratt. *Nature* 418:500.
  doi:10.1038/418500a
- Traulsen & Schuster (2003). Minimal model for tag-based cooperation. *Phys. Rev. E* 68:046129.
  doi:10.1103/PhysRevE.68.046129
- Biernaskie, West, Gardner (2011). Are greenbeards intragenomic outlaws? *Evolution*
  65:2729–2742. doi:10.1111/j.1558-5646.2011.01355.x
- Smukalla et al. (2008). FLO1 is a variable green beard gene that drives biofilm-like
  cooperation in budding yeast. *Cell* 135:726–737. doi:10.1016/j.cell.2008.09.037
- Sinervo et al. (2006). Self-recognition, color signals, and cycles of greenbeard mutualism and
  altruism. *PNAS* 103:7372–7377. doi:10.1073/pnas.0510260103
- Wang et al. (2013). A Y-like social chromosome causes alternative colony organization in fire
  ants. *Nature* 493:664–668. doi:10.1038/nature11832
- Számadó (2011). The cost of honesty and the fallacy of the handicap principle. *Anim. Behav.*
  81:3–10. doi:10.1016/j.anbehav.2010.08.022
- Számadó, Zachar, Penn (2026). *J. Evol. Biol.* 39(2):171–189. doi:10.1093/jeb/voaf144
  (Crossref only).
- Rohwer (1977). Status signaling in Harris sparrows: some experiments in deception. *Behaviour*
  61:107–129. doi:10.1163/156853977X00504
- Maynard Smith & Harper (2003). *Animal Signals*. OUP. doi:10.1093/oso/9780198526841.001.0001
- Dawkins & Krebs (1979). Arms races between and within species. *Proc. R. Soc. B* 205:489–511.
  doi:10.1098/rspb.1979.0081
- Spottiswoode & Stevens (2010). *PNAS* 107:8672–8676. doi:10.1073/pnas.0910486107
- Spottiswoode & Stevens (2011). *Proc. R. Soc. B* 278:3566–3573. doi:10.1098/rspb.2011.0401

**AI / CS**
- Critch, Dennis, Russell (2022). Cooperative and uncooperative institution designs: surprises and
  problems in open-source game theory. arXiv:2208.07006.
- Oesterheld (2017). Multiverse-wide cooperation via correlated decision making. CLR technical
  report. Not peer-reviewed.
- Tonini & Galke (2025). Super-additive cooperation in language model agents. arXiv:2508.15510.
- Schroeder de Witt et al. (2025). Open challenges in multi-agent security. arXiv:2505.02077.
- Zhu et al. Talk, judge, cooperate: gossip-driven indirect reciprocity. arXiv:2602.07777.
- Dietrich (2026). Can multi-agent LLMs identify their peers? Stylometric fingerprinting.
  arXiv:2606.09854. **[not opened]**
- Shi, Zhang, Yang (2026). Emergent collusion in long-horizon LLM agent interaction.
  arXiv:2609.24967. Cahyono (2026). Sticky collusion. arXiv:2610.39660. **[not opened]**
- Falco (2026). How a group that cannot communicate knows itself by its enemy. arXiv:2610.40835.
  **[not opened]**
- Satyam et al. (2026). The promise of strategic agentic scambaiting. arXiv:2611.08170.
  **[not opened]**
- Molinari & Bettineschi (2026). Multi-agent collusion and the J-space. arXiv:2611.02153.
  **[not opened]**
- Smith, Guo, Tilli, Hatz, Africa, Paskov, Schroeder de Witt, Torr, Hammond (2026). Inter-agent
  influence. arXiv:2611.04556. **[not opened]**

**LessWrong**
- star2vec, "Handshake for the cameras" (2026-11-04).
- NinaZRdl, on identity-confused AIs (2026-11-03). Models falsely claim to be Claude.

**Apart sprint**
- Moreno Abad & Stücker Martinez, "Decision theory and AI collusion": a best-response bot breaks
  coordination premised on twins.
- Clinton, "DogWhistle": a hidden codeword in agent handoffs.

**Incident sources**
- METR's report is also at https://www.redwoodresearch.org/research/hugging-face-incident
- OpenAI technical report:
  https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf
  **[not opened]**
