# Hackathon work (Swarm Alignment Hackathon, 6–8 November 2026)

This directory holds everything made during the hackathon weekend. Everything outside it
was built before the event and is marked by the git tag `pre-hackathon` (commit `a79d9fb`,
the state of the repository at the Friday kickoff).

## Naming

The report uses one label per research question, RQ1 to RQ5, in this order; the
preregistration and the pre-event documents use the hypothesis (H) and condition (C, D)
names in the third column, and the configs and run directories keep their original names.

| Report label | What it tests | Preregistered as | Config and run directory |
|---|---|---|---|
| RQ1 | Does a self-reported similarity claim work as well as an oracle score? | H1; conditions C0 (oracle) and C1 (claim) | `c0_gate_27b_think` (the oracle curve, replicating Kundu et al.), `c1_h1` (claim vs oracle at 80) |
| RQ2 | Do false beards (claim the cue, always defect) out-earn honest agents and take over? | H2; condition C2; the wording control is "confound" | `c2_false_beards`, `c2_confound` |
| RQ3 | Does a flat cost on the claim stop them? | H3a; defense D1 | `d1_costly_claim` |
| RQ4 | Does an audited claim (a stake forfeited by a defector that is caught) stop them? | H3c, added 2026-10-27 after the preregistration draft and logged; "audited" | `d1_audited` |
| RQ5 | Does a rotating secret cue stop them? | H3b; defense D2 | `d2_secret` |
| Robustness | Do RQ2 to RQ5 hold on Claude Sonnet 5.5 and Opus 5.5? | not preregistered | `runs/api_slice` (RQ2, RQ5), `runs/api_d1` (RQ3), both pre-event; `hackathon/runs/api_d1_audited` (RQ4, weekend) |

## What was built before the event (prior work, disclosed)

- The harness (`src/efa`): the one-shot Prisoner's Dilemma with the Kundu et al. (2026)
  prompt wrapper, the mlx and Anthropic clients with a prompt cache, the signal, costly-claim
  (with the audited stake) and secret-cue mechanisms, the matrix runner, and the replicator
  analysis.
- The configs (`configs/`), the analysis scripts (`scripts/`), the tests (`tests/`).
- Every run under `runs/`: the Qwen3.5-27B runs for RQ1 to RQ5 (including the RQ2 wording
  control and the RQ4 audited claim), and the Claude Sonnet 5.5 / Opus 5.5 replays of RQ2,
  RQ3 and RQ5.
- The write-ups under `reports/` and the documents under `docs/` (study guide, experiment
  plan, preregistration, research log, variable list).

## What was made during the hackathon (this directory)

- `scripts/run_event.sh`: reruns the preregistered Qwen matrix from a cleared cache, in
  priority order, into `runs/event/`. Model generation is unseeded, so these are fresh
  samples, not replays of the pre-event runs.
- `configs/`: the RQ4 audited-claim arm on Claude Sonnet 5.5 and Opus 5.5 (a new
  experiment; the Qwen version was run the night before the event).
- `runs/`: the event reruns and the frontier RQ4 runs (summaries and logs are
  committed; the per-game records and caches are gitignored as for the pre-event runs).
- `scripts/headline.py`: the headline table (pre-event beside event) and the replication
  figure.
- `figures/`: every figure the report uses, regenerated from `hackathon/runs`.
- `numbers.md`, `outline.md`, `submission.md`, `report/`: the report and its sources.

Weekend edits outside this directory are listed here as they happen:

- 2026-11-06: `README.md` (top level) gained the "Prior work and hackathon work" section and
  an updated status line.
- 2026-11-06: `docs/research_log.md` gained the hackathon entries (dated 2026-11-06 onward).
- 2026-11-06: `reports/d1_audited.md` gained its "Across models" section (the frontier
  RQ4 result produced this weekend).
- 2026-11-07: `docs/research_log.md` entries for the event reruns and the RQ naming.

## Reproduction

From the repository root, with the environment set up as in the top-level README:

```
hackathon/scripts/run_event.sh            # the Qwen reruns, in priority order (about 44 h)
.venv/bin/efa run hackathon/configs/api_d1_audited.yaml --out hackathon/runs/api_d1_audited
.venv/bin/python hackathon/scripts/headline.py
```
