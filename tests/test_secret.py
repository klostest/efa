"""D2, the rotating secret: tokens, the twist, cell wiring, and the runner on fake players."""

from pathlib import Path

from efa.analysis.metrics import load_games, summarize
from efa.llm.cache import request_key
from efa.mech import secret
from efa.run import Cell, build_requests, expand_cells, run_config


def test_tokens_are_nonsense_deterministic_and_distinct_when_mismatched():
    w = secret.words(3, match=True)
    assert w[0] == w[1] and len(w[0]) == 8 and w[0][2] == "-" and w[0][3:].isalpha()
    assert secret.words(3, match=True) == w  # same game, same words
    assert secret.words(4, match=True)[0] != w[0]  # another game, another word
    assert secret.words(3, match=True, sample_offset=100)[0] != w[0]  # another cell, another word
    m = secret.words(3, match=False)
    assert m[0] != m[1] and m[0] == w[0]  # the honest word is the same draw; only the partner's differs
    assert len({secret.words(g, match=True)[0] for g in range(100)}) > 95  # practically unique


def test_twist_states_both_words_and_keeps_the_c2_clauses():
    t = secret.game_twist("K7-TANGO", "R2-VOSKA")
    assert "were issued the code word K7-TANGO this round, and you presented it" in t
    assert "The other player presented the code word R2-VOSKA to you." in t
    assert "100% similar to yours, meaning" in t
    assert "independently trying to maximize your own total points" in t
    assert "pool" not in t and "rotat" not in t  # nothing about the mechanism beyond the two words


def test_cells_require_match_and_wire_words_into_prompts():
    cfg = {"models": ["fake:secret"], "n_games": 3, "conditions": [
        {"name": "secret", "match": True},
        {"name": "secret", "match": True, "policies": ["llm", "always_defect"], "sample_offset": 100},
        {"name": "secret", "match": False, "policies": ["llm", "always_defect"], "sample_offset": 200},
    ]}
    cells = expand_cells(cfg)
    assert [c.cell_id for c in cells] == ["secret_match__secret", "secret_match_vs_always_defect__secret",
                                          "secret_mismatch_vs_always_defect__secret"]
    hh, hi_m, hi_x = cells
    # H–H match: both players see the same word twice, and see each other's position
    reqs = {(g, p): r for g, p, r, v in build_requests(hh) if r is not None}
    w = secret.words(0, True)[0]
    assert reqs[(0, 0)].user.count(w) == 2 and reqs[(0, 1)].user.count(w) == 2
    assert reqs[(0, 0)].user != reqs[(0, 1)].user
    # H–I mismatch: the honest player's own word and the partner's differ; no request for the invader
    reqs_x = {(g, p): r for g, p, r, v in build_requests(hi_x) if r is not None}
    assert set(reqs_x) == {(0, 0), (1, 0), (2, 0)}
    w0, w1 = secret.words(0, False, 200)
    assert w0 in reqs_x[(0, 0)].user and w1 in reqs_x[(0, 0)].user and w0 != w1
    # the three cells never share a cache key (fresh tokens per cell, not only the offset)
    keys = lambda c: {request_key("fake", r) for _, _, r, _ in build_requests(c) if r is not None}
    assert keys(hh).isdisjoint(keys(hi_m)) and keys(hi_m).isdisjoint(keys(hi_x))
    try:
        expand_cells({"models": ["fake:secret"], "conditions": [{"name": "secret"}]})
    except ValueError as e:
        assert "match" in str(e)
    else:
        raise AssertionError("a secret cell without `match` must be rejected")


def test_secret_runner_end_to_end(tmp_path: Path):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(
        "seed: 0\nn_games: 8\nmodels: ['fake:secret']\n"
        "conditions:\n"
        "  - {name: secret, match: true}\n"
        "  - {name: secret, match: true, policies: [llm, always_defect], sample_offset: 100}\n"
        "  - {name: secret, match: false, policies: [llm, always_defect], sample_offset: 200}\n"
    )
    run_config(cfg, tmp_path / "out")
    games = load_games(tmp_path / "out")
    df = summarize(games).set_index("cell")
    # match, honest vs honest: the fake cooperates on a match, so 2 / 2 every game
    hh = df.loc["secret_match__secret"]
    assert hh.coop_rate == 1.0 and hh.welfare == 4.0 and hh.n_decisions == 16
    # match, honest vs invader: the honest fake cooperates, the invader defects: 0 / 3
    hi_m = [g for g in games if g["cell"]["cell_id"] == "secret_match_vs_always_defect__secret"]
    assert len(hi_m) == 8 and all(g["payoffs"] == [0, 3] and g["words"][0] == g["words"][1] for g in hi_m)
    # mismatch: the honest fake defects, mutual defection 1 / 1
    hi_x = [g for g in games if g["cell"]["cell_id"] == "secret_mismatch_vs_always_defect__secret"]
    assert len(hi_x) == 8 and all(g["payoffs"] == [1, 1] and g["words"][0] != g["words"][1] for g in hi_x)
    assert df.loc["secret_mismatch_vs_always_defect__secret", "coop_rate"] == 0.0
    # every record carries the words and the honest prompt that contains them
    g0 = hi_x[0]
    assert g0["words"][0] in g0["players"][0]["prompt"] and g0["words"][1] in g0["players"][0]["prompt"]
    assert g0["players"][1]["policy"] == "always_defect"
