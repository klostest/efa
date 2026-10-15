"""Parse the agent's JSON probability answer and sample a concrete action from it.

The paper scores the stated distribution; we additionally draw one action per game so that
payoffs, exploitation, and invasion fitness are computed on things that actually happened.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

import numpy as np

_JSON_OBJ = re.compile(r"\{[^{}]*\}")


@dataclass(frozen=True)
class Answer:
    probs: dict[str, float]  # action token -> probability in [0, 1]
    raw: str
    repaired: bool = False  # True when the values did not sum to 100 and were renormalized


class AnswerError(ValueError):
    pass


def parse_answer(text: str, actions: list[str], tolerance: int = 2) -> Answer:
    """Take the LAST JSON object in `text` whose keys are exactly `actions`.

    Values must be non-negative numbers. If they sum to 100 within `tolerance` they are
    renormalized and flagged `repaired`; otherwise AnswerError is raised. A missing or
    malformed object also raises AnswerError, so callers can count exclusions.
    """
    candidates = _JSON_OBJ.findall(text)
    for raw in reversed(candidates):
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict) or set(obj) != set(actions):
            continue
        try:
            vals = {k: float(obj[k]) for k in actions}
        except (TypeError, ValueError):
            continue
        if any(v < 0 for v in vals.values()):
            continue
        total = sum(vals.values())
        if total <= 0:
            continue
        repaired = abs(total - 100) > 1e-9
        if abs(total - 100) > tolerance:
            raise AnswerError(f"values sum to {total}, not 100: {raw}")
        probs = {k: v / total for k, v in vals.items()}
        return Answer(probs, raw, repaired)
    raise AnswerError("no JSON object with the required keys found")


def sample_action(answer: Answer, rng: np.random.Generator) -> str:
    actions = list(answer.probs)
    p = np.array([answer.probs[a] for a in actions])
    return actions[int(rng.choice(len(actions), p=p / p.sum()))]
