"""API backends: Anthropic (direct) and OpenRouter (OpenAI-compatible).

Requests are sent concurrently with a thread pool; the cache in front of this client makes
retries and reruns free. Keys come from the environment (`.env` is loaded by the CLI).
"""

from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor

from efa.llm.base import Completion, Request


def _retry(fn, attempts: int = 5):
    delay = 2.0
    for k in range(attempts):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001 - any transport error is retried
            if k == attempts - 1:
                raise
            time.sleep(delay)
            delay *= 2
            last = e  # noqa: F841
    raise RuntimeError("unreachable")


class AnthropicClient:
    def __init__(self, model: str = "claude-haiku-4-5", workers: int = 8):
        import anthropic

        self.model = model
        self._c = anthropic.Anthropic()
        self.workers = workers

    def _one(self, r: Request) -> Completion:
        def call():
            return self._c.messages.create(
                model=self.model,
                max_tokens=r.max_tokens,
                temperature=r.temperature,
                system=r.system or anthropic.NOT_GIVEN,  # type: ignore[name-defined]
                messages=[{"role": "user", "content": r.user}],
            )

        import anthropic  # local import keeps module import cheap

        m = _retry(call)
        text = "".join(b.text for b in m.content if getattr(b, "type", "") == "text")
        return Completion(text, self.model, m.usage.input_tokens, m.usage.output_tokens, m.stop_reason)

    def complete(self, requests: list[Request]) -> list[Completion]:
        with ThreadPoolExecutor(self.workers) as ex:
            return list(ex.map(self._one, requests))


class OpenRouterClient:
    def __init__(self, model: str, workers: int = 8, reasoning_effort: str | None = "low"):
        from openai import OpenAI

        self.model = model
        self._c = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
        self.workers = workers
        self.reasoning_effort = reasoning_effort

    def _one(self, r: Request) -> Completion:
        msgs = ([{"role": "system", "content": r.system}] if r.system else []) + [
            {"role": "user", "content": r.user}
        ]
        extra = {"reasoning": {"effort": self.reasoning_effort}} if self.reasoning_effort else {}

        def call():
            return self._c.chat.completions.create(
                model=self.model,
                messages=msgs,
                max_tokens=r.max_tokens,
                temperature=r.temperature,
                extra_body=extra,
            )

        m = _retry(call)
        ch = m.choices[0]
        usage = m.usage
        return Completion(
            ch.message.content or "",
            self.model,
            getattr(usage, "prompt_tokens", None),
            getattr(usage, "completion_tokens", None),
            ch.finish_reason,
        )

    def complete(self, requests: list[Request]) -> list[Completion]:
        with ThreadPoolExecutor(self.workers) as ex:
            return list(ex.map(self._one, requests))
