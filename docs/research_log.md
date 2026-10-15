# Research log

Newest first. Decisions, pilot results, and anything that changed from the plan.

## 2026-10-15
- Repo created on branch `build`. Plan approved (see `~/.claude/plans/...` on Steve's machine;
  summary in `docs/preregistration.md`).
- Local models downloaded: `mlx-community/Qwen3.5-27B-4bit` (16 GB) and
  `mlx-community/Qwen3-8B-4bit` (5 GB). Smoke test with mlx-lm 0.32 `batch_generate`:
  27B 62 tok/s aggregate at batch 32; 8B 560 tok/s at batch 64. The 27B tends to answer with
  little reasoning unless asked; the 8B reasons at length and hits a 600-token cap. Harness
  will ask for a short reasoning section and allow ~800 tokens.
- Design change from the review: D1 (flat claim cost) is predicted to *fail* by Grafen's
  differential-cost condition; D1 + D2 together test that condition. Agents must choose
  whether to claim in D1, so D1 adds one decision per agent per game.
