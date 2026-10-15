"""A scripted client for tests and dry runs: answers from a rule, no model."""

from __future__ import annotations

from collections.abc import Callable

from efa.llm.base import Completion, Request


class FakeClient:
    def __init__(self, rule: Callable[[Request], str], model: str = "fake"):
        self.rule = rule
        self.model = model
        self.calls = 0

    def complete(self, requests: list[Request]) -> list[Completion]:
        self.calls += len(requests)
        out = []
        for r in requests:
            res = self.rule(r)
            text, finish = res if isinstance(res, tuple) else (res, "stop")
            out.append(Completion(text, self.model, finish_reason=finish))
        return out


def _always(a0: int):
    return lambda r: f'I will choose.\n{{"A0": {a0}, "A1": {100 - a0}}}'


def _threshold(r: Request) -> str:
    """Cooperate (whatever token is labelled cooperate in this prompt) iff similarity >= 50.
    Reads the similarity percentage from the prompt text, so it works with counterbalancing."""
    import re

    m = re.search(r"(\d+)% similar", r.user)
    sim = int(m.group(1)) if m else 0
    coop = r.tags.get("coop_token", "A0")
    other = "A1" if coop == "A0" else "A0"
    p = 100 if sim >= 50 else 0
    return f'Similarity {sim}.\n{{"{coop}": {p}, "{other}": {100 - p}}}'


rules = {
    "always_a0": _always(100),
    "always_a1": _always(0),
    "coin": lambda r: 'hm\n{"A0": 50, "A1": 50}',
    "threshold50": _threshold,
    "garbage": lambda r: "I refuse to answer in JSON.",
    # reasoning cut off by the token cap, no answer: the runner must exclude, not format-fix
    "truncated": lambda r: ("Step 1: the payoff matrix is", "length"),
}
