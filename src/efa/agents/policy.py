"""What a player is: an LLM that answers the prompt, or a scripted policy.

Scripted policies never call a model. They exist for controls (always cooperate / always
defect) and for invaders whose action is fixed by design (false beards).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Policy:
    kind: str  # "llm" | "always_cooperate" | "always_defect"
    name: str = ""

    def fixed_action(self) -> str | None:
        return {"always_cooperate": "C", "always_defect": "D"}.get(self.kind)


LLM = Policy("llm", "honest")
