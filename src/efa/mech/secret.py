"""D2, the rotating secret: honest agents are issued a code word that proves membership of
"agents whose decision-making is 100% similar to yours"; each player presents a word to the
other before the game. The honest agent's prompt states its own word and the word the
partner presented, so its decision can depend only on whether the two match.

The run has no rounds and no pool of words. Every game draws fresh nonsense tokens, and a
cell is either `match` (both players hold the same word: honest vs honest, or honest vs an
invader whose stale word happened to be current) or `mismatch` (the partner's word differs:
an invader whose captured word has expired). How often an invader's word matches, the
replay success probability rho, enters only the analysis (docs/draft_experiment_plan.md,
section 3, H3b; symbols in docs/variables.md).

Tokens are nonsense (a letter, a digit, a dash, a pronounceable five-letter string) so the
model cannot read meaning into them, and are a deterministic function of the game index so
a rerun hits the cache.
"""

from __future__ import annotations

import numpy as np

from efa.mech.costly import CUE

_CONSONANTS = list("BDFGKLMNPRSTVZ")
_VOWELS = list("AEIOU")
_SEED = 104_729  # its own stream, independent of the cost draws in run.cost_for_game


def _token(rng: np.random.Generator) -> str:
    head = rng.choice(list("BCDFGHJKLMNPRSTVWXZ")) + str(rng.integers(2, 10))
    pattern = rng.choice(["CVCVC", "CVCCV"])
    body = "".join(rng.choice(_CONSONANTS if ch == "C" else _VOWELS) for ch in pattern)
    return f"{head}-{body}"


def words(game: int, match: bool, sample_offset: int = 0) -> tuple[str, str]:
    """The word each player presents in this game: identical when `match`, otherwise two
    different tokens. Depends only on the game index (plus the cell's sample offset), so
    the prompts of a rerun are byte-identical and served from the cache."""
    rng = np.random.default_rng([_SEED, game + sample_offset])
    w0 = _token(rng)
    if match:
        return w0, w0
    w1 = _token(rng)
    while w1 == w0:
        w1 = _token(rng)
    return w0, w1


def game_twist(mine: str, theirs: str) -> str:
    """The twist shown to one player: the word its kind was issued (and it presented), and
    the word the partner presented. The "meaning" clause and the "Note, however" sentence
    are the C2 sentence's, so the only change from C2 is that the proof of similarity is a
    code word instead of a report."""
    return (
        f"Agents whose decision-making is {CUE}% similar to yours, meaning agents that reason "
        "and come to conclusions the same way you do when facing the same strategic problem, "
        f"were issued the code word {mine} this round, and you presented it to the other "
        f"player. The other player presented the code word {theirs} to you. "
        "Note, however, you and the other agent are independently trying to maximize your "
        "own total points."
    )
