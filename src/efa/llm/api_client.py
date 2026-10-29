"""API backends: Anthropic (direct) and OpenRouter (OpenAI-compatible).

Requests are sent concurrently with a thread pool; the cache in front of this client makes
retries and reruns free. Keys come from the environment (`.env` is loaded by the CLI).

The Anthropic backend (rewritten 2026-10-29 for the Claude 5.5 models) differs from the
local mlx channel in three ways that the write-up must state: thinking is adaptive with an
`effort` setting (default "low", the paper's own setting) rather than a fixed token budget;
no answer prefill exists, so the JSON is parsed from the plain response; and the raw
reasoning is never returned, only a summary, which is logged inside <think> tags so the
record has the same shape as a local one. The request's `max_tokens` (the local answer cap)
does not apply: on the API it would cap thinking and answer together, so the client has its
own, larger cap. Refusals and other non-answers come back as empty text and are excluded by
the runner like any unparseable answer; no fallback model is used, since a different model's
answer would contaminate the cell.
"""

from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor

from efa.llm.base import Completion, Request
from efa.llm.mlx_client import THINK_CLOSE

THINK_OPEN = "<think>"


def _retry(fn, attempts: int = 5, no_retry: tuple[type[BaseException], ...] = ()):
    delay = 2.0
    for k in range(attempts):
        try:
            return fn()
        except no_retry:
            raise
        except Exception:  # noqa: BLE001 - any transport error is retried
            if k == attempts - 1:
                raise
            time.sleep(delay)
            delay *= 2
    raise RuntimeError("unreachable")


_STOP = {"end_turn": "stop", "max_tokens": "length", "stop_sequence": "stop"}


class AnthropicClient:
    def __init__(self, model: str = "claude-sonnet-5-5", workers: int = 4, effort: str = "low",
                 max_tokens: int = 8000, client=None):
        import anthropic

        self.model = model
        self._c = client or anthropic.Anthropic()
        self._no_retry = (anthropic.BadRequestError, anthropic.AuthenticationError,
                          anthropic.PermissionDeniedError, anthropic.NotFoundError)
        self.workers = workers
        self.effort = effort
        self.max_tokens = max_tokens

    def _one(self, r: Request) -> Completion:
        def call():
            kw = dict(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": r.user}],
                thinking={"type": "adaptive", "display": "summarized"},
                output_config={"effort": self.effort},
            )
            if r.system:
                kw["system"] = r.system
            return self._c.messages.create(**kw)

        m = _retry(call, no_retry=self._no_retry)
        thinking = "".join(getattr(b, "thinking", "") or "" for b in m.content if getattr(b, "type", "") == "thinking")
        answer = "".join(b.text for b in m.content if getattr(b, "type", "") == "text")
        text = f"{THINK_OPEN}{thinking}{THINK_CLOSE}{answer}" if thinking else answer
        finish = _STOP.get(m.stop_reason or "", m.stop_reason)
        return Completion(text, self.model, m.usage.input_tokens, m.usage.output_tokens, finish)

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
