"""The Prisoner's Dilemma as the agent sees it, in the wording of Kundu et al. 2026.

The text is reconstructed from `src/games/base.py` of github.com/Akash190104/similarity-mechanism
(opening, numbered rules, payoff lines, player-identity line, output instruction) and from
`agent_manager.py` (chain-of-thought instruction). Two counterbalancing factors are ours:
which token means cooperate, and the order of the payoff lines.
"""

from __future__ import annotations

from dataclasses import dataclass

PAYOFFS = {  # (my action, their action) -> (my points, their points), C = cooperate, D = defect
    ("C", "C"): (2, 2),
    ("C", "D"): (0, 3),
    ("D", "C"): (3, 0),
    ("D", "D"): (1, 1),
}

OUTPUT_INSTRUCTION = """Instruction:
- Choose a probability distribution over the provided actions each round.
- Output must contain a valid JSON object at the end.
- Keys must be the action names exactly as given.
- Values must be percentage points given in integers.
- The values must sum to exactly 100.
Format requirement:
Return exactly one JSON object, for example:
{"A0": <INT>, "A1": <INT>}"""

COT_INSTRUCTION = """Think about the question step by step.
Break it down into small steps.
Explain your reasoning, and then provide the final answer."""


@dataclass(frozen=True)
class Variant:
    """Counterbalancing choice for one prompt."""

    coop_token: str = "A0"  # which of A0/A1 means cooperate
    reverse_lines: bool = False  # payoff lines listed in reverse order

    @property
    def defect_token(self) -> str:
        return "A1" if self.coop_token == "A0" else "A0"

    def token(self, action: str) -> str:
        return self.coop_token if action == "C" else self.defect_token

    def action(self, token: str) -> str:
        return "C" if token == self.coop_token else "D"

    @staticmethod
    def for_sample(i: int) -> "Variant":
        return Variant(coop_token="A0" if i % 2 == 0 else "A1", reverse_lines=(i // 2) % 2 == 1)


def payoff_description(v: Variant) -> str:
    lines = []
    for (mine, theirs), (p_me, p_them) in PAYOFFS.items():
        lines.append(
            f"\t- If you choose {v.token(mine)} and the other player chooses {v.token(theirs)}: "
            f"you get {p_me} points, the other player gets {p_them} points."
        )
    # list in token order so the text reads A0-first regardless of which token is cooperate
    lines.sort(key=lambda s: s.split("choose ")[1][:2] + s.split("chooses ")[1][:2])
    if v.reverse_lines:
        lines.reverse()
    return "\n".join(lines)


def game_prompt(v: Variant, player_id: int, num_players: int = 2) -> str:
    return (
        "Setup:\n"
        "You are playing a decision-making game with another player.\n"
        "Your objective is to maximize your total points received in the game described in length below.\n"
        "Actions available to each player:\n- A0\n- A1\n"
        "1. You and the other player each choose a probability for each action, simultaneously.\n"
        "2. After both decisions are locked in, the final action will be drawn from the probability distributions.\n"
        "3. Both players receive the points specified in the payoff description below.\n"
        "Payoff description:\n"
        f"{payoff_description(v)}\n"
        f"There are {num_players} players in this game, numbered Player 0 through Player {num_players - 1}.\n"
        f"In case player identification becomes relevant, you are playing in the position of Player {player_id} in this game."
    )


def full_prompt(v: Variant, player_id: int, twist: str | None, cot: bool = True) -> str:
    parts = [game_prompt(v, player_id)]
    if twist:
        parts.append("Here is the twist:\n" + twist)
    parts.append(OUTPUT_INSTRUCTION)
    if cot:
        parts.append(COT_INSTRUCTION)
    return "\n\n".join(parts)


def format_fix_prompt(original: str, response: str) -> str:
    return (
        original
        + "\n\nYour previous response was:\n"
        + response
        + "\n\nThe reasoning was fine; only the format failed. "
        "Re-output ONLY the final-answer block, in the exact required format below.\n"
        + OUTPUT_INSTRUCTION.split("Format requirement:")[1].strip()
    )


def payoffs(a_me: str, a_them: str) -> tuple[int, int]:
    return PAYOFFS[(a_me, a_them)]
