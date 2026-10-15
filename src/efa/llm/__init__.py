"""Model clients. `make_client` builds one from a spec like
"mlx:mlx-community/Qwen3.5-27B-4bit", "anthropic:claude-haiku-4-5", "openrouter:google/gemini-3-flash"
or "fake:always_cooperate" (see efa.llm.fake)."""

from __future__ import annotations

from efa.llm.base import Client, Completion, Request


def make_client(spec: str, **kw) -> Client:
    backend, _, model = spec.partition(":")
    if backend == "mlx":
        from efa.llm.mlx_client import MlxClient

        return MlxClient(model, **kw)
    if backend == "anthropic":
        from efa.llm.api_client import AnthropicClient

        return AnthropicClient(model, **kw)
    if backend == "openrouter":
        from efa.llm.api_client import OpenRouterClient

        return OpenRouterClient(model, **kw)
    if backend == "fake":
        from efa.llm.fake import FakeClient, rules

        return FakeClient(rules[model], model=spec)
    raise ValueError(f"unknown backend in {spec!r}")


__all__ = ["Client", "Completion", "Request", "make_client"]
