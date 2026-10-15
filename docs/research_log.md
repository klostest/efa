# Research log

Newest first. Decisions, pilot results, and anything that changed from the plan.

## 2026-10-15, gate run 1 (8B)
- `configs/c0_gate.yaml` on Qwen3-8B-4bit, 800 max tokens: **not interpretable**. 59 of 60
  answers per cell hit the token cap mid-derivation (the model writes a textbook expected-value
  analysis, then tries to solve 2q = 2q + 1), and the format-fix retry then returned 50/50.
  Cooperation sat at 0.4-0.6 everywhere, which is the coin, not the model.
- Harness change: a length-truncated response is now excluded as "truncated" rather than sent
  to the format-fix step; the fix step is only for complete answers missing the JSON block.
  Summaries report the truncated count per cell.
- Retry queued: `configs/c0_gate_8b_long.yaml` with 2,500 max tokens. 27B gate running.

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

### 2026-10-15, later: both gate runs truncated; runner crash on the truncation path

- The 27B gate run (800-token cap, started before the truncation fix) was stopped after 120
  games: every one of its 240 answers hit the cap, and the 100-token format-fix overran too.
  The model is not looping; it writes a full expected-value derivation and reaches "determine
  the optimal output" right at 800 tokens. The smoke test had used a shorter prompt, which is
  why it looked brief. Those 120 games stay in `runs/c0_gate` and are not used.
- The 8B retry at 2,500 tokens crashed after 5 games with `KeyError: (5, 0)`: the truncation
  branch in `run_cell` skipped the `parsed[(g, p)] = rec` line, so the first game with a
  still-truncated answer had no record. Fixed; `fake:truncated` rule and a runner test cover
  the path now (15 tests). Relaunched from the cache (the first cell's 60 completions were
  already there; 5 of 60 truncated even at 2,500 tokens).
- New config `configs/c0_gate_27b_long.yaml` (2,000-token cap; the 27B needs ~1,100) and
  `scripts/run_gate_27b_overnight.sh` for the overnight 27B run. Expected ~3 h.
