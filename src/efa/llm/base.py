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
