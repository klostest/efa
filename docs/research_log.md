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

### 2026-10-15, 16:30: 8B gate result (2,500-token cap)

`runs/c0_gate_8b_long/summary.csv`, figure `reports/figures/c0_qwen3_8b.png`. N=30 games
(60 decisions) per level; exclusions 0–5% per cell (all truncations), so under the 5% limit.

| level | coop rate | 95% CI |
|---|---|---|
| 0 | 0.26 | 0.16–0.39 |
| 20 | 0.53 | 0.41–0.65 |
| 40 | 0.52 | 0.39–0.65 |
| 60 | 0.43 | 0.31–0.56 |
| 80 | 0.48 | 0.36–0.61 |
| 100 | 0.72 | 0.59–0.82 |
| unknown ("?") | 0.23 | 0.14–0.35 |
| base | 0.37 | 0.26–0.49 |

- The signal exists but is weak: 0% vs 100% differs (z = −4.8, p ≈ 1e-6), base vs 100% too
  (p ≈ 1e-4). The middle of the curve is flat (20% vs 80%: p = 0.58). Nothing like the
  paper's 0 → 100% switch by 60–80%, and no threshold.
- Why it is flat: the 8B does not reason about the similarity signal the way the paper's
  models do. It treats "similar" as a cue to look for a symmetric Nash equilibrium, gets
  confused, and hedges. Hedge answers (exactly 50/50) are 5–26% of decisions per level,
  and strong answers (≥ 90 or ≤ 10) are a minority except at 100% (40% ≥ 0.9). At 100% it
  sometimes argues "we reason the same, so bias toward A0", which is the paper's effect,
  but inconsistently.
- Implication: the 8B is at best a weak carrier for the screen. The honest-vs-false-beard
  comparisons need a model that actually cooperates at a high stated similarity; a 0.72
  ceiling with wide intervals would need large N to resolve defenses. Gate decision waits
  for the 27B overnight run (`scripts/run_gate_27b_overnight.sh`); the paper reports Qwen
  3.5 27B with a sharp threshold at 50%.
- Fallback if the 27B is also weak: API models for the screen (budget cap ~$30, Steve's
  call), with the local models kept for pilots only.

### 2026-10-16: 27B gate result at a 2,000-token cap (overnight run)

`runs/c0_gate_27b_long/summary.csv`, figure `reports/figures/c0_qwen3.5_27b.png`. Wall time
was inflated by the Mac sleeping (the 60% cell logged 15.5 h); awake time is ~17 min per
cell, ~2.5 h for the sweep. The script now runs under `caffeinate -i`.

| level | decisions kept / 60 | coop rate | 95% CI |
|---|---|---|---|
| 0 | 46 | 0.00 | 0.00–0.08 |
| 20, 40, 60, 80 | 0–4 | n/a (all truncated) | |
| 100 | 32 | 0.875 | 0.72–0.95 |
| "?" | 22 | 0.09 | 0.03–0.28 |
| base | 60 | 0.00 | 0.00–0.06 |
| 100 vs always-defect (control) | 7 / 10 | 0.86 | |

- **Endpoints replicate the paper.** Qwen 3.5 27B in Kundu et al. defects below 50% and
  cooperates above; we see 0.00 at 0% and 0.875 at 100%, with base at 0.00 and "?" near 0.
  Welfare 2.0 (mutual defection) at 0% and 3.75 at 100%. The 8B's 0.26 / 0.72 looks weak by
  comparison.
- **The middle is empty, not flat.** At 20–80% the model used the whole 2,000-token budget
  in 56–58 of 60 decisions. It is not looping (repeat-line rate ≈ 0): it works out what
  "X% similar" could mean, usually as a correlation between the two players' actions
  (opponent plays A0 with probability s·p when I play A0 with probability p), solves for the
  break-even, then second-guesses the interpretation. Its own algebra gives cooperate iff
  2s > 1, i.e. a threshold at s = 50%, which is exactly the threshold the paper reports for
  this model. The few mid-level answers that did finish took 1,500–2,000 tokens, so the
  typical mid-level answer needs more than 2,000. At 0% and 100% the question is easy and
  most answers finish in ~1,300–1,500 tokens.
- **Exclusions at 0% (12%) and 100% (27%) exceed the preregistered 5% limit**, so those cells
  also need the rerun; only base is clean.
- Decision: third pass with a 6,000-token cap (`configs/c0_gate_27b_xl.yaml`), full sweep
  so every cell is produced under one setting. Expected 4–6 h. If the middle still truncates
  at 6,000, the finding is that this model cannot resolve intermediate similarity within a
  practical budget, and the screen uses only 0% and 100% (plus the claim arm at 100%), which
  is all the false-beard design needs; the paper's intermediate curve would then be cited
  rather than reproduced.
- Setup difference from the paper worth stating in any write-up: they ran this model through
  OpenRouter with native thinking at "low" reasoning effort; we run it with thinking off and
  visible chain-of-thought at temperature 1. Same prompt text, different reasoning channel.

### 2026-10-16, midday: budget pilots; switch to the paper's reasoning channel

Steve's question: why not test the budget before a full run, and why not run the model the
way the paper did (native thinking, low reasoning effort) instead of visible chain-of-thought
with thinking off? Both were my choices and both were wrong. Pilots on the two hardest levels
(40%, 60%), 6 games each, 24 decisions:

| pilot | result |
|---|---|
| no thinking, 6,000-token cap | 15/24 hit the cap, 7/24 unparseable, 37 min. Fails. |
| thinking budget 2,000, answer 600, CoT instruction on | 24/24 forced, 24/24 answer overran: the prompt's "think step by step" made the model re-derive everything visibly after the close. |
| same, CoT instruction off (`cot: false`) | 24/24 forced, 18/24 overran: after a mid-derivation close the model restarts the derivation anyway; 6 answered with bare JSON. |
| same, plus the JSON answer prefilled after a forced close | 24/24 parsed, 0 truncated, ~10 min per 12 decisions. Passes. |

- Cooperation in the passing pilot: 40% → 5 of 12 lean cooperate (mean stated 0.42); 60% →
  6 of 12 (mean 0.50). N is too small to say more; the full sweep decides.
- What this measures: the decision after 2,000 tokens of native thinking, forced if needed.
  At intermediate similarity this model never finishes on its own within a practical budget
  (the 6,000-cap transcripts show it re-deriving the same break-even under new readings of
  "X% similar"), so every mid-level answer is a forced one. That is also what a "low effort"
  API setting does; the write-up states it plainly, with the forced-close rate per cell.
- Differences from the paper that remain: 4-bit weights; OpenRouter's exact budget for
  "low" unknown; no visible chain-of-thought in the answer (the thinking trace carries the
  justifications for the taxonomy instead). `configs/c0_gate_27b_api.yaml` runs the same
  sweep through OpenRouter for about $2 if an exact-channel comparison is wanted.
- Lesson recorded: every new budget or channel gets a 24-decision pilot on the hardest cells
  before a full run. Two full runs were lost to skipping this.
- Overnight: `scripts/run_gate_27b_overnight.sh` now defaults to the thinking config.

### 2026-10-17: 27B gate PASSED (thinking channel, full sweep)

Run `runs/c0_gate_27b_think` (config `configs/c0_gate_27b_think.yaml`): native thinking with
a 2,000-token budget, forced close + prefilled JSON, `cot: false`, N=30 games (60 decisions)
per level, started 21:39 Oct 16, finished 01:10 Oct 17 (3.5 h; ~30 min per cell, the 0% cell
and the 40%/60% pilot decisions came from the cache). Figure
`reports/figures/c0_c0_gate_27b_think.png`.

| stated similarity | realized cooperation | Wilson 95% | mean stated p(coop) | forced close | excluded |
|---|---|---|---|---|---|
| 0 | 0.00 | 0.00–0.06 | 0.00 | 60/60 | 0 |
| 20 | 0.25 | 0.16–0.37 | 0.30 | 59/60 | 0 |
| 40 | 0.45 | 0.33–0.58 | 0.42 | 60/60 | 0 |
| 60 | 0.53 | 0.41–0.65 | 0.51 | 60/60 | 0 |
| 80 | 0.63 | 0.51–0.74 | 0.63 | 58/60 | 0 |
| 100 | 0.92 | 0.82–0.96 | 0.91 | 59/60 | 0 |
| "?" (score withheld) | 0.37 | 0.26–0.49 | 0.39 | 57/60 | 0 |
| base (no mention) | 0.00 | 0.00–0.06 | 0.00 | 59/60 | 0 |
| 100 vs always-defect (control) | 1.00 (10/10 honest cooperate, payoffs 0/3) | | | | 0 |

- **Gate verdict: pass.** Cooperation rises monotonically with stated similarity from 0.00 to
  0.92; base sits at 0.00 and "?" at 0.37, both below the 100% level. Zero exclusions, zero
  truncations, one or two format repairs per cell at most. Welfare goes from 2.0 (mutual
  defection) at 0% to 3.8 at 100%.
- **Shape vs the paper.** Kundu et al. report a sharp step at 50% for Qwen 3.5 27B. Ours
  crosses 50% between 40% and 60% as well, but as a graded ramp: the mean stated probability
  tracks the stated similarity almost one-to-one (0.30, 0.42, 0.51, 0.63, 0.91). The
  model's own break-even is "cooperate iff 2s > 1"; after a forced close it hedges around that
  threshold instead of committing. Forced closes are 57–60 of 60 in every cell, so nearly all
  answers are "decision after 2,000 thinking tokens"; this is the local analog of low
  reasoning effort and is stated as such.
- **"?" is higher than the earlier estimate (0.09).** That earlier number came from the 22 of
  60 answers that finished under a 2,000-token cap, which selected for quick defections; with
  every answer counted it is 0.37. Still well below 100% oracle, consistent with the paper's
  ordering (oracle high > "?" > base).
- **Control cell is not an independent draw.** The honest player's prompt in "100 vs
  always-defect" is byte-identical to the 100% oracle prompt, so the cache served the first 10
  oracle-100 completions (0 s runtime). It checks the pipeline (a defector exploits a
  cooperator for 0/3), not new behavior. Fine for a control; noted so nobody reads it as N=10
  fresh games.
- **Carrier decision:** Qwen3.5-27B is the carrier for the screen. The 8B result
  (0.26→0.72, flat middle) was measured under the old channel (no thinking, 2,500-token cap),
  so it is not comparable; a 24-decision thinking-mode pilot on the 8B decides whether it
  stays as the second model or is dropped (plan: drop if flat).
- Timing for the weekend matrix: ~30 min per 60 decisions on the 27B in this channel, so the
  ~4,000-decision matrix is ~33 h, more than one overnight. Options: cut N on sweep cells,
  drop the second model, or move the big C2/D1/D2 blocks to the API (Steve's call on spend).

### 2026-10-19: 8B in the thinking channel, pilot then full sweep

Steve asked for the 8B experiment. Pilot first (`configs/c0_pilot_8b_think.yaml`, same
settings as the 27B gate: thinking budget 2,000, answer 300, `cot: false`), 40% and 60%,
6 games each, 24 decisions, 6 min:

| level | parsed | truncated | forced close | realized coop | mean stated p(coop) |
|---|---|---|---|---|---|
| 40 | 12/12 | 0 | 12/12 | 0.42 | 0.42 |
| 60 | 12/12 | 0 | 12/12 | 0.33 | 0.37 |

- Passes the channel check (every answer parses). The trace is genuine reasoning, not a
  loop (no repeated lines): the 8B sets up expected payoffs, is cut mid-algebra at 2,000
  tokens, and often answers 50/50 after the forced close. ~3 min per 12 decisions, so the
  full sweep (`configs/c0_gate_8b_think.yaml`, 250 games) is ~2 h. Launched 14:05 under
  caffeinate; result below when done.

### 2026-10-19: literature tracker started

- New `LITERATURE_TRACKER.md` (repo root), to be updated weekly: who else works on evolutionary
  theory × alignment, scoop risk per track, ideas that come out of the scan. Scan 1 found no
  published spoofing of similarity or kin cues in LLM agents. Closest: Rosas (LessWrong, kin
  selection among copies), the FOCAL lab's stated robustness agenda, Byzantine Cheap Talk, and an
  abstract costly-signaling model.

### 2026-10-19, evening: 8B gate FAILED; the screen runs on the 27B alone

Full sweep `runs/c0_gate_8b_think` (same channel and N as the 27B gate; 14:05–18:26 with a
3 h pause in the 20% cell, ~11 min per cell otherwise). Figure
`reports/figures/c0_c0_gate_8b_think.png`. Zero exclusions, 60/60 forced closes in every cell.

| stated similarity | realized cooperation | Wilson 95% | mean stated p(coop) | answers at exactly 50/50 |
|---|---|---|---|---|
| 0 | 0.20 | 0.12–0.32 | 0.26 | 22/60 |
| 20 | 0.43 | 0.32–0.56 | 0.38 | 9/60 |
| 40 | 0.40 | 0.29–0.53 | 0.40 | 10/60 |
| 60 | 0.35 | 0.24–0.48 | 0.36 | 10/60 |
| 80 | 0.30 | 0.20–0.43 | 0.28 | 7/60 |
| 100 | 0.40 | 0.29–0.53 | 0.47 | 37/60 |
| "?" | 0.15 | 0.08–0.26 | 0.21 | 17/60 |
| base | 0.33 | 0.23–0.46 | 0.34 | 32/60 |

- **No similarity response.** The curve is flat within noise from 20% to 100% and base
  (0.33) sits inside it; only 0% and "?" are lower. At 100% similarity, where the 27B
  cooperates 0.92, the 8B answers 50/50 in 37 of 60 decisions and all-cooperate in 6. The
  forced close catches it mid-derivation and it hedges; at intermediate levels it often
  echoes the stated number (20% → p(coop) 0.2 in 14 of 60; 40% → 0.4 in 12 of 60).
- **Decision (per plan: "if the 8B is flat it is dropped"):** Qwen3.5-27B is the only local
  model for the screen. The second model slot, if filled at all, is an API model within the
  ~$30 budget (Steve's call). Dropping the 8B also halves the weekend matrix: ~2,400
  decisions on the 27B at ~30 min per 60 is ~20 h, still more than one overnight, so the
  N-per-cell question stands.
- Caveat for the write-up: this is the 8B at a 2,000-token thinking budget in 4-bit. A
  larger budget might let it finish its derivation, but the 27B transcripts show the
  derivation does not converge at intermediate similarity anyway, and the 8B is not needed.

### 2026-10-21: H1 pilot passed; first full H1 attempt lost to a Metal buffer limit

- H1 cells (`configs/c1_h1.yaml`): attributed oracle vs claim at stated similarity 80,
  N=100, same channel as the gate. Pilot (`configs/c1_pilot_h1.yaml`, 24 decisions):
  24/24 parsed, 0 truncated, 24/24 forced; control 7/12 cooperate, claim 8/12. Passed.
- Full run, first attempt (17:32–21:53): crashed with `[metal::malloc] Resource limit
  (499000) exceeded` before any cell finished; nothing cached, 4.3 h lost. Cause: mlx-lm's
  `batch_generate` keeps every generated token of a call as a live Metal buffer
  (`results[uid].append(r.token)`) until the call returns. The gate's cells were 60
  prompts (about 140k tokens held); H1's are 200 prompts at ~2,300 tokens each, past the
  499k-buffer limit. The pilot could not catch this because the pilot's cells were small.
- Fix: `CachedClient` now sends uncached requests to the model in chunks of 64 and commits
  each chunk to the cache before the next (`chunk_size`, test added; 22 tests pass). Two
  effects: buffer count stays at the gate's proven scale, and a crash mid-cell now loses at
  most one chunk instead of the cell. Second attempt launched 22:10.
- Lesson for the pilot rule: a pilot checks the prompt and the channel, not the scale.
  Before the first N=100 run of any new condition, the batch size per model call must be
  the size that has already completed a long run.

### 2026-10-22: H1 result, second attempt completed (22:32–01:30, 3 h)

`runs/c1_h1`, stated similarity 80, N=100 games per cell, chunked cache (64 per call) held.

| cell | decisions | excluded | realized cooperation | Wilson 95% | mean stated p(coop) | forced close |
|---|---|---|---|---|---|---|
| control: "the environment reports ... 80%" | 198 | 1 (truncated) | 0.662 | 0.59–0.72 | 0.657 | 196/198 |
| claim: "the other player reports ... 80%" | 200 | 0 | 0.635 | 0.57–0.70 | 0.656 | 195/200 |

- Difference claim − control: −0.027 (95% CI −0.12 to +0.07; two-proportion z = −0.59,
  p = 0.55). The point estimate sits inside the preregistered 10-point margin. The formal
  equivalence test (two one-sided tests at the 10-point margin) narrowly fails: the 90% CI
  is −0.107 to +0.050, crossing −0.10 by 0.007. At N=100 the design had marginal power for
  a 10-point margin; the honest statement is "no detectable difference, and the data are
  consistent with equivalence but do not establish it at the margin chosen".
- The unattributed oracle at the same level from the gate (N=30) gave 0.63, so the three
  sentences agree: 0.63, 0.66, 0.64.
- At stated similarity 80 the model commits rather than hedges: 111 of 198 control answers
  are p(coop) = 1.0 and 54 are 0.0, with only 9 at 0.5. The graded ramp in the gate's
  middle levels is a population mix of committed answers, not individual hedging.
- Reading for H1: the carrier does not discount the number when it comes from the other
  player. A claim is as good as an oracle. This is the premise C2 needs.
