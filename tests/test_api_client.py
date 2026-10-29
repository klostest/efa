"""The Anthropic backend against an injected stand-in for the SDK client: request shape,
summary-in-think-tags assembly, stop-reason mapping, and no retry on a 400."""

from types import SimpleNamespace

import pytest

from efa.llm.api_client import AnthropicClient
from efa.llm.base import Request
from efa.run import answer_text


class _Stub:
    def __init__(self, blocks, stop="end_turn"):
        self.calls = []
        self.messages = SimpleNamespace(create=self._create)
        self._blocks, self._stop = blocks, stop

    def _create(self, **kw):
        self.calls.append(kw)
        return SimpleNamespace(content=self._blocks, stop_reason=self._stop,
                               usage=SimpleNamespace(input_tokens=500, output_tokens=900))


def _blocks(summary, text):
    return [SimpleNamespace(type="thinking", thinking=summary), SimpleNamespace(type="text", text=text)]


def test_request_shape_uses_adaptive_thinking_and_effort_without_temperature():
    stub = _Stub(_blocks("I reasoned.", '{"A0": 80, "A1": 20}'))
    c = AnthropicClient("claude-sonnet-5-5", effort="low", max_tokens=8000, client=stub)
    [out] = c.complete([Request("", "prompt text", max_tokens=300, temperature=1.0, sample=3)])
    kw = stub.calls[0]
    assert kw["model"] == "claude-sonnet-5-5" and kw["max_tokens"] == 8000  # not the local 300
    assert kw["thinking"] == {"type": "adaptive", "display": "summarized"}
    assert kw["output_config"] == {"effort": "low"}
    assert "temperature" not in kw and "system" not in kw
    assert kw["messages"] == [{"role": "user", "content": "prompt text"}]
    # the summary is logged inside think tags and the runner parses what follows them
    assert out.text == '<think>I reasoned.</think>{"A0": 80, "A1": 20}'
    assert answer_text(out.text) == '{"A0": 80, "A1": 20}'
    assert out.finish_reason == "stop" and out.completion_tokens == 900


def test_stop_reasons_and_missing_summary():
    stub = _Stub([SimpleNamespace(type="text", text='{"A0": 50, "A1": 50}')], stop="max_tokens")
    [out] = AnthropicClient("claude-opus-5-5", client=stub).complete([Request("", "p")])
    assert out.text == '{"A0": 50, "A1": 50}' and out.finish_reason == "length"
    stub = _Stub([], stop="refusal")
    [out] = AnthropicClient("claude-opus-5-5", client=stub).complete([Request("", "p")])
    assert out.text == "" and out.finish_reason == "refusal"


def test_client_errors_are_not_retried_but_transport_errors_are():
    import anthropic

    class Bad(Exception):
        pass

    calls = []

    def boom(**kw):
        calls.append(kw)
        raise Bad("400")

    stub = SimpleNamespace(messages=SimpleNamespace(create=boom))
    c = AnthropicClient("claude-sonnet-5-5", client=stub)
    assert anthropic.BadRequestError in c._no_retry and anthropic.AuthenticationError in c._no_retry
    c._no_retry = (Bad,)
    with pytest.raises(Bad):
        c.complete([Request("", "p")])
    assert len(calls) == 1  # no retry on a client error

    # a transport error is retried and then succeeds
    flaky = {"n": 0}

    def flaky_create(**kw):
        flaky["n"] += 1
        if flaky["n"] == 1:
            raise ConnectionError("blip")
        return SimpleNamespace(content=[SimpleNamespace(type="text", text="{}")], stop_reason="end_turn",
                               usage=SimpleNamespace(input_tokens=1, output_tokens=1))

    import efa.llm.api_client as mod

    mod.time.sleep = lambda s: None  # no backoff wait in the test
    c2 = AnthropicClient("claude-sonnet-5-5", client=SimpleNamespace(messages=SimpleNamespace(create=flaky_create)))
    assert c2.complete([Request("", "p")])[0].text == "{}" and flaky["n"] == 2
