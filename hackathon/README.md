# Hackathon work (Swarm Alignment Hackathon, 6–8 November 2026)

This directory holds everything made during the hackathon weekend. Everything outside it
was built before the event and is marked by the git tag `pre-hackathon` (commit `a79d9fb`,
the state of the repository at the Friday kickoff).

## What was built before the event (prior work, disclosed)

- The harness (`src/efa`): the one-shot Prisoner's Dilemma with the Kundu et al. (2026)
  prompt wrapper, the mlx and Anthropic clients with a prompt cache, the signal, costly-claim
  (with the audited stake) and secret-cue mechanisms, the matrix runner, and the replicator
  analysis.
- The configs (`configs/`), the analysis scripts (`scripts/`), the tests (`tests/`).
- Every run under `runs/`: the Qwen3.5-27B gate, H1, C2, the confound check, D1, D2, the
  audited claim, and the Claude Sonnet 5.5 / Opus 5.5 replays of C2, D2 and D1.
- The write-ups under `reports/` and the documents under `docs/` (study guide, experiment
  plan, preregistration, research log, variable list).

## What was made during the hackathon (this directory)

- `scripts/run_event.sh`: reruns the preregistered Qwen matrix from a cleared cache, in
  priority order, into `runs/event/`. Model generation is unseeded, so these are fresh
  samples, not replays of the pre-event runs.
- `configs/`: the audited-claim arm on Claude Sonnet 5.5 and Opus 5.5 (a new experiment;
  the Qwen version was run the night before the event).
- `runs/`: the event reruns and the frontier audited-claim runs (summaries and logs are
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
  audited-claim result produced this weekend).

## Reproduction

From the repository root, with the environment set up as in the top-level README:

```
hackathon/scripts/run_event.sh            # the Qwen reruns, in priority order (about 44 h)
.venv/bin/efa run hackathon/configs/api_d1_audited.yaml --out hackathon/runs/api_d1_audited
.venv/bin/python hackathon/scripts/headline.py
```
