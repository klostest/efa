# Limitations and Future Work: recommendations (2026-11-08)

The report is the Google Doc `1U02TB281CFHFEL7uEWoPhF6Uxt6Ni_pMvKyZUhhVOv0`, section 5,
"Discussion, Limitations, and Future Work". Budget: the whole of section 5 should fit in about
two-thirds of a page, so keep Limitations and Future Work to short paragraphs or tight bullets.
Numbers come only from `hackathon/numbers.md` and `hackathon/runs/headline.md`.

## Limitations (cover 1–6; 7 can be one line)

1. **Stylized game.** This is a one-shot Prisoner's Dilemma with similarity stated in the prompt,
   not a deployed multi-agent system. The effects depend on prompt framing; the wording control
   (Appendix RQ2) addresses one clause only.
2. **Scripted, "rational" false beards.**
   - False beards are an always-defect script, not LLMs choosing to deceive.
   - In RQ3/RQ4, whether a false beard claims or stays silent is a scoring rule (whichever pays
     more), not observed behaviour; in the runs it always claimed.
   - Opus never stayed silent, so its play against a silent partner was never observed, and its
     RQ4 value (−1) rests on a scoring convention.
3. **Inferred, not simulated, populations.**
   - The replicator inference assumes a large, randomly mixed population.
   - It treats payoff as reproductive fitness. For agents this is an analogy: agents that earn
     more get copied or redeployed.
4. **The audit is a best case.**
   - The harness audits every game where both players claimed.
   - Lachmann, Számadó & Bergstrom (2001) note that cost-free honest signals work only when
     receivers can "verify the integrity of messages" and "identify and punish deception". The
     stake therefore assumes a trusted auditor that sees outcomes and can collect.
   - Sampled or predictable audits would weaken it: Zhu, Zuo & Sun 2026, "Blindfold",
     arXiv:2610.37055 (not on Steve's reading list).
5. **The rotating secret abstracts away the hard part.**
   - Replay success is a parameter, not measured.
   - It assumes honest agents receive the current word securely and that false beards can't learn
     it. Key distribution is not modelled.
6. **Models and samples.**
   - Three models; Qwen3.5-27B runs 4-bit, and 95–99% of its calls hit the 2,000-token thinking
     cap and are force-closed.
   - RQ1 and the wording control were run on Qwen only.
   - The Sonnet/Opus results for RQ2, RQ3 and RQ5 are from pre-event runs.
   - 100 games per comparison; RQ1 equivalence is not established at the 10-point margin.
7. **Dual use.** Recognition handshakes like the rotating word are also how colluding agents find
   each other (Kaushik et al. 2026, arXiv:2610.37984; Motwani et al. 2024, arXiv:2402.07510). Both
   are verified in `hackathon/related_work_sources.md` but not on Steve's reading list.

## Future Work (pick 3–4)

- **LLM false beards:** do models spoof similarity on their own when it pays?
- **Explicit population simulations:** finite populations, mutation, repeated games, and agents
  that learn whom to trust.
- **Realistic auditing:** sampled, predictable, or capturable auditors.
- **Real identity infrastructure:** the defenses with real cryptographic identity and key
  rotation, in an environment like the Hugging Face incident's message board.
- **Broader coverage:** more models and reasoning-effort settings, and whether instructing agents
  to verify claims changes acceptance (the Discussion no longer claims this; it is untested).

## Conventions for whoever drafts this

- **Ground rules:** Steve writes in his own words. He asked for a draft of these two sections
  only. No nit-picking.
- **Terms:**
  - "honest agent" and "false beard", "payoff advantage", "replay success";
  - "protect", not "restore" (the outcome is bistable);
  - RQ1–RQ5 names only, never the preregistration's H/C/D names.
- **Citations:** prefer Steve's reading list (sheets "Biology_Literature" and "AI_Literature";
  PDFs in `~/Documents/Literature`). Verify any quote in the PDF.
- **Related files:**
  - `hackathon/report/appendix_rq1.md` … `appendix_rq5.md`
  - `hackathon/report/related_work_outline.md`
  - `hackathon/related_work_sources.md`
