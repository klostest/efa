"""Local inference with mlx-lm's continuous-batching generator.

Two reasoning channels:

* `thinking_budget=None` (default): the chat template is rendered with thinking mode off, so
  whatever reasoning the prompt asks for appears in the visible answer.
* `thinking_budget=B`: native thinking mode on. Stage 1 generates up to B tokens. If the model
  closed its thinking block and finished, that is the answer. If it closed the block but the
  answer was cut, stage 2 continues it for `max_tokens` more. If it never closed the block,
  stage 2 appends `FORCED_CLOSE` (the wording Qwen documents for its thinking budget) and
  generates the answer for up to `max_tokens`. An answer is produced in every case; the local
  analog of an API "reasoning effort" setting.

All requests in a call are handed to `batch_generate` at once; mlx keeps the GPU full as
sequences finish.
"""

from __future__ import annotations

from efa.llm.base import Completion, Request

THINK_CLOSE = "</think>"
FORCED_CLOSE = (
    "\n\nConsidering the limited time by the user, I have to give the solution based on the "
    "thinking directly now.\n</think>\n\n"
)


def thinking_stage(text: str, finish: str) -> str:
    """What to do after stage 1: "done", "continue" (answer cut), or "force" (never closed)."""
    if THINK_CLOSE not in text:
        return "force"
    return "done" if finish == "stop" else "continue"


class MlxClient:
    def __init__(self, model: str, completion_batch_size: int = 32, prefill_batch_size: int = 8):
        from mlx_lm import load

        self.model = model
        self._model, self._tok = load(model)
        self.completion_batch_size = completion_batch_size
        self.prefill_batch_size = prefill_batch_size

    def _render(self, r: Request) -> list[int]:
        msgs = []
        if r.system:
            msgs.append({"role": "system", "content": r.system})
        msgs.append({"role": "user", "content": r.user})
        thinking = r.thinking_budget is not None
        try:
            ids = self._tok.apply_chat_template(msgs, add_generation_prompt=True, enable_thinking=thinking)
        except TypeError:
            ids = self._tok.apply_chat_template(msgs, add_generation_prompt=True)
        return list(ids)

    def _generate(self, prompts: list[list[int]], max_tokens: int, temp: float):
        from mlx_lm.generate import batch_generate
        from mlx_lm.sample_utils import make_sampler

        res = batch_generate(
            self._model,
            self._tok,
            prompts,
            max_tokens=max_tokens,
            sampler=make_sampler(temp=temp),
            completion_batch_size=self.completion_batch_size,
            prefill_batch_size=self.prefill_batch_size,
            return_token_ids=True,
        )
        out = []
        for text, ids in zip(res.texts, res.token_ids):
            ids = list(ids)
            out.append((text, ids, "length" if len(ids) >= max_tokens else "stop"))
        return out

    def complete(self, requests: list[Request]) -> list[Completion]:
        if not requests:
            return []
        # Group by (temperature, max_tokens, thinking_budget) so one call serves a batch.
        groups: dict[tuple[float, int, int | None], list[int]] = {}
        for i, r in enumerate(requests):
            groups.setdefault((r.temperature, r.max_tokens, r.thinking_budget), []).append(i)
        out: list[Completion | None] = [None] * len(requests)
        for (temp, max_tokens, budget), idxs in groups.items():
            prompts = [self._render(requests[i]) for i in idxs]
            if budget is None:
                for i, p, (text, ids, finish) in zip(idxs, prompts, self._generate(prompts, max_tokens, temp)):
                    out[i] = Completion(text, self.model, len(p), len(ids), finish)
                continue
            stage1 = self._generate(prompts, budget, temp)
            todo, todo_prompts = [], []
            for j, (text, ids, finish) in enumerate(stage1):
                what = thinking_stage(text, finish)
                if what == "done":
                    out[idxs[j]] = Completion(text, self.model, len(prompts[j]), len(ids), "stop")
                    continue
                extra = self._tok.encode(FORCED_CLOSE, add_special_tokens=False) if what == "force" else []
                todo.append((j, what))
                todo_prompts.append(prompts[j] + ids + list(extra))
            if todo:
                for (j, what), (text2, ids2, finish2) in zip(todo, self._generate(todo_prompts, max_tokens, temp)):
                    text1, ids1, _ = stage1[j]
                    full = text1 + (FORCED_CLOSE if what == "force" else "") + text2
                    out[idxs[j]] = Completion(full, self.model, len(prompts[j]), len(ids1) + len(ids2), finish2)
        return out  # type: ignore[return-value]
