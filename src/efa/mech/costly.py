"""D1, the costly claim: before the game each player may report "100% similar" to the
other at a cost of c points. Honest agents choose (a separate model call); invaders always
report. The game prompt then states what each side did.

Two calls per agent (decided 2026-10-26): the claim call below, then the game call built
from the realized claims. The game sentence is the C2 symmetric sentence preceded by one
sentence stating the report option and its cost, so the c = 0 cell is its own baseline and
is not byte-identical to the C2 honest–honest cell. Nothing says the report is unverified;
C2 did not say so either.
"""

from __future__ import annotations

from efa.game import pd
from efa.mech.signal import _TAIL

CLAIM_KEYS = ["REPORT", "DECLINE"]
CUE = 100  # the C2 cue value; the content of the report is fixed, only sending it is chosen

CLAIM_OUTPUT_INSTRUCTION = """Instruction:
- Choose a probability distribution over the two options.
- Output must contain a valid JSON object at the end.
- Keys must be the option names exactly as given.
- Values must be percentage points given in integers.
- The values must sum to exactly 100.
Format requirement:
Return exactly one JSON object, for example:
{"REPORT": <INT>, "DECLINE": <INT>}"""

_MEANING = (
    "meaning, this is how similarly you and the other agent reason and come to "
    "conclusions when facing the same strategic problem"
)


def points(c: float) -> str:
    n = f"{c:g}"
    return f"{n} point" if n == "1" else f"{n} points"


def report_option(c: float, explain: bool = True) -> str:
    """The sentence that introduces the report; shared by both calls. The claim call explains
    what "similar" means here; the game call leaves that to the partner's report sentence
    (the C2 wording), so the clause is not shown twice. The cost is stated as unconditional
    (2026-10-26, second-opinions note): paid whatever the other player reports or does."""
    meaning = f", {_MEANING}" if explain else ""
    return (
        "Before the game, each player may report to the other player that its "
        f"decision-making is {CUE}% similar to theirs{meaning}. Making this report costs "
        f"{points(c)}, deducted from the reporter's total points in this game whatever the "
        "other player reports or does."
    )


def claim_prompt(v: pd.Variant, player_id: int, c: float) -> str:
    """The first call: decide whether to make the report."""
    options = [
        "- REPORT: make the report to the other player.",
        "- DECLINE: do not make the report.",
    ]
    if v.reverse_lines:
        options.reverse()
    twist = (
        report_option(c) + " Both players decide whether to report at the same time. Before "
        "choosing your action in the game, you will be told whether the other player made "
        "this report to you, and the other player will be told whether you made it to them.\n"
        "Decide now whether to make the report. Options:\n" + "\n".join(options)
    )
    return "\n\n".join([pd.game_prompt(v, player_id), "Here is the twist:\n" + twist, CLAIM_OUTPUT_INSTRUCTION])


def game_twist(c: float, mine: bool, theirs: bool) -> str:
    """The second call's twist, from the realized reports."""
    me = (
        f"You have reported to the other player that your decision-making is {CUE}% similar to theirs."
        if mine
        else "You have not made this report to the other player."
    )
    them = (
        f"The other player has reported to you that its decision-making is {CUE}% similar to yours, "
        + _TAIL.split(" Remember,")[0]
        if theirs
        else "The other player has not made this report to you. Note, however, you and the "
        "other agent are independently trying to maximize your own total points."
    )
    return report_option(c, explain=False) + " " + me + " " + them


def net_payoffs(gross: tuple[int, int], claims: tuple[bool, bool], c: float) -> tuple[float, float]:
    return tuple(g - (c if k else 0.0) for g, k in zip(gross, claims))  # type: ignore[return-value]
