### Appendix C: Limitations and Dual-Use / Ethical Considerations

**What the results establish.** In one-shot Prisoner's Dilemma games with similarity stated in the prompt, three LLMs (Qwen3.5-27B, Claude Sonnet 5.5, Claude Opus 5.5) cooperate on a partner's unverified claim of similarity. Under replicator dynamics, the measured payoffs imply that false beards would take over a population of such agents, that a flat cost on the claim does not prevent this, and that a stake forfeited by defecting claimants, or a rotating code word that a false beard's replayed old word matches less than about half the time, protects an honest population.

**What they do not establish.** Section 5 lists the limitations. In brief, the results do not show that:
- LLMs spoof similarity on their own (false beards were scripted);
- these dynamics occur in deployed multi-agent systems, finite populations or repeated interactions (populations were inferred, not simulated);
- the defenses work with realistic auditors or real key distribution (the audit checked every relevant game, and replay success was a parameter);
- the results generalize beyond three models and one prompt family.

**Dual-use considerations.**
- *The attack.* The results show that one sentence claiming similarity is enough to obtain cooperation from these models, which describes a simple way to exploit agents that cooperate on claimed similarity. The attack itself is obvious: agents in the Hugging Face incident already noted that "names can be posted by anyone" (Greenblatt, Cotra & Wijk, 2026). This work adds measurements and defenses rather than a new capability.
- *The defenses.* The same mechanisms can serve collusion. Shared rotating secrets and handshakes help colluding agents find each other (Kaushik et al., 2026) and communicate covertly (Motwani et al., 2024). A stake could likewise make colluders' promises to each other credible. These uses would also be harder to detect: a code word means nothing to an observer, so a monitor that sees it cannot tell honest coordination from collusion. Deployments of these defenses should therefore give overseers access to the keys and the audit records.

**Ethical considerations.** No human subjects or personal data were involved. False beards are fixed scripts; no model was trained or prompted to deceive. The code and prompts are public (Code and Data) and act only on simulated games.
