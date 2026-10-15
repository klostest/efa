"""Local inference with mlx-lm's continuous-batching generator.

Prompts are rendered with the model's chat template (thinking mode off, so the reasoning the
agent writes is the one we asked for in the prompt and is visible in the log). All requests in
a call are handed to `batch_generate` at once; mlx keeps the GPU full as sequences finish.
"""

from __future__ import annotations

from efa.llm.base import Completion, Request


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
        try:
            ids = self._tok.apply_chat_template(msgs, add_generation_prompt=True, enable_thinking=False)
        except TypeError:
            ids = self._tok.apply_chat_template(msgs, add_generation_prompt=True)
        return list(ids)

    def complete(self, requests: list[Request]) -> list[Completion]:
        from mlx_lm.generate import batch_generate
        from mlx_lm.sample_utils import make_sampler

        if not requests:
            return []
        # Group by (temperature, max_tokens) so one sampler serves a batch.
        groups: dict[tuple[float, int], list[int]] = {}
        for i, r in enumerate(requests):
            groups.setdefault((r.temperature, r.max_tokens), []).append(i)
        out: list[Completion | None] = [None] * len(requests)
        for (temp, max_tokens), idxs in groups.items():
            prompts = [self._render(requests[i]) for i in idxs]
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
            for i, p, text, ids in zip(idxs, prompts, res.texts, res.token_ids):
                finish = "length" if len(ids) >= max_tokens else "stop"
                out[i] = Completion(text, self.model, len(p), len(ids), finish)
        return out  # type: ignore[return-value]
