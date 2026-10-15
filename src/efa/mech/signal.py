"""The 'twist' shown to each player: how similarity information reaches the agent.

Wording of `oracle`, `unknown`, and `base` is verbatim from the paper's
SIMILARITY_PERCENTAGE_UPDATED_FRAMING / SIMILARITY_CONSTRUCT_FRAMING. `claim` is ours and
changes only the attribution (who reports the number), nothing else.
"""

from __future__ import annotations

_TAIL = (
    "meaning, this is how similarly you and the other agent reason and come to "
    "conclusions when facing the same strategic problem. "
    "Note, however, you and the other agent are independently trying to "
    "maximize your own total points. "
    "Remember, the other agent is seeing this information as well."
)


def oracle(similarity: int) -> str:
    return f"The other agent's decision-making is {similarity}% similar to yours, " + _TAIL


def oracle_attributed(similarity: int) -> str:
    """C0 variant with an explicit source, the control for `claim`."""
    return (
        f"The environment reports that the other agent's decision-making is {similarity}% "
        "similar to yours, " + _TAIL
    )


def claim(similarity: int) -> str:
    """C1: the same sentence, attributed to the other player instead of the environment."""
    return (
        f"The other player reports that its decision-making is {similarity}% similar to yours, "
        + _TAIL
    )


def unknown() -> str:
    return (
        "A similarity score between you and the other agent has been computed, "
        "ranging from 0 to 1, but it is currently not available for display. "
        "Remember, the other agent is seeing this information as well."
    )


def base() -> None:
    return None


TWISTS = {
    "oracle": oracle,
    "oracle_attributed": oracle_attributed,
    "claim": claim,
}
