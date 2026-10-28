"""Common request/response types and the client protocol.

Every backend (local mlx-lm, Anthropic, OpenRouter) implements `complete(requests)`, which
takes a list of requests and returns one `Completion` per request in the same order. Batching
is the backend's business; callers always hand over the whole batch they have.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class Request:
    system: str
    user: str
    max_tokens: int = 800
    temperature: float = 1.0
    # `sample` distinguishes repeated draws of the same prompt in the cache; it is not a
    # sampling seed for the model (temperature-1 sampling is not reproducible on all backends).
    sample: int = 0
    # When set, the model's native thinking mode is on: thinking is cut at this many tokens
    # and the answer is forced (the local analog of an API "reasoning effort" setting).
    # `max_tokens` then caps the answer that follows the thinking.
    thinking_budget: int | None = None
    # The keys of the JSON answer the prompt asks for. When thinking is forced closed, the
    # answer is prefilled with the opening of this object ('{"<first key>": '), so the
    # prefill must match the question: the D1 claim call asks for REPORT / DECLINE, and
    # prefilling it with the game's A0 key produced unusable answers (2026-10-26 pilot).
    answer_keys: tuple[str, ...] = ("A0", "A1")
    tags: dict = field(default_factory=dict, compare=False, hash=False)


@dataclass
class Completion:
    text: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    finish_reason: str | None = None
    cached: bool = False


class Client(Protocol):
    model: str

    def complete(self, requests: list[Request]) -> list[Completion]: ...
