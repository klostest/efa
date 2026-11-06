# EFA: Evolutionary Frameworks for Agents

Cheap, local screens of biologically inspired hypotheses about populations of LLM agents.
First screen: **false beards**. Kundu et al. (2026) showed that telling LLM agents how similar
their counterpart is makes them cooperate in a one-shot Prisoner's Dilemma. We ask what happens
when that similarity signal can be faked, and whether biology's fixes for fake kin cues (costly
signals, rotating secret cues) hold up.

Built for the Swarm Alignment Hackathon, Nov 6–8 2026 (Track 3: identity under copying).
Everything runs on one Apple-silicon laptop with 4-bit local models through mlx-lm; a small
API slice validates the headline result on a frontier model.

## Quick start

```
uv sync --extra dev
uv run pytest
uv run efa run configs/smoke_fake.yaml      # scripted players, no model calls
uv run efa run configs/c0_gate.yaml         # replication sweep on local models
uv run efa summarize runs/c0_gate
uv run efa plot runs/c0_gate
```

Model specs: `mlx:<hf repo>`, `anthropic:<model>`, `openrouter:<model>`, `fake:<rule>`.
API keys go in `.env` (see `.env.example`). Every model call is cached in
`runs/<name>/cache.sqlite`; delete it to force a fresh run.

## Layout

- `src/efa/game/` the Prisoner's Dilemma in the paper's wording, answer parsing, action sampling
- `src/efa/mech/` the "twist" each player sees: oracle similarity, self-reported claim, and
  (week 2) costly claims and secret cues
- `src/efa/agents/` LLM vs scripted policies (controls, invaders)
- `src/efa/llm/` mlx-lm, Anthropic, OpenRouter clients behind one interface, plus the cache
- `src/efa/run.py` matrix runner; one JSON line per game with both prompts and raw responses
- `src/efa/analysis/` per-cell metrics with Wilson intervals, replicator dynamics, figures
- `configs/` one YAML per experiment block
- `docs/` study guide, preregistration, research log, master variable list (`variables.md`)

## Prior work and hackathon work

This repository was built in the three weeks before the Swarm Alignment Hackathon
(6–8 November 2026). The boundary is the git tag `pre-hackathon` (commit `a79d9fb`, the
state at the Friday kickoff).

- **Built before the event (prior work):** everything outside `hackathon/`: the harness
  (`src/efa`), the configs, the analysis scripts, the tests, every run under `runs/`
  (the Qwen3.5-27B gate, H1, C2, the confound check, D1, D2, the audited claim, and the
  Claude Sonnet 5.5 / Opus 5.5 replays of C2, D2 and D1), the write-ups under `reports/`
  and the documents under `docs/`.
- **Made during the hackathon:** everything under `hackathon/`: the event-weekend reruns
  of the Qwen matrix from a cleared cache (`hackathon/runs/event/`), the audited-claim arm
  on the two Claude models (a new experiment), the headline table and replication figure,
  and the report. `hackathon/README.md` has the full list, including the few edits made
  outside that directory during the weekend.

## Status

Screen complete; see `docs/research_log.md` and the write-ups in `reports/`. The hackathon
submission is under `hackathon/`.
