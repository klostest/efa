"""D1, the costly claim: prompts, bookkeeping, and the two-call runner on fake players."""

import json
from pathlib import Path

from efa.analysis.metrics import load_games, summarize
from efa.game import pd
from efa.mech import costly, signal
from efa.run import Cell, build_claim_requests, build_requests, cost_for_game, run_config


def test_claim_prompt_states_cost_and_options_in_both_orders():
    v0, v1 = pd.Variant.for_sample(0), pd.Variant.for_sample(2)
    t0, t1 = costly.claim_prompt(v0, 0, 1.5), costly.claim_prompt(v1, 1, 1)
    assert "Making this report costs 1.5 points" in t0 and "costs 1 point," in t1
    assert "whatever the other player reports or does" in t0
    assert "similar to theirs, meaning" in t0  # the claim call explains the report
    assert '{"REPORT": <INT>, "DECLINE": <INT>}' in t0
    assert t0.index("- REPORT") < t0.index("- DECLINE") and t1.index("- DECLINE") < t1.index("- REPORT")
    assert "You are playing a decision-making game" in t0 and "Here is the twist:" in t0


def test_game_twist_four_cases_and_both_reported_matches_c2_sentence():
    both = costly.game_twist(0, True, True)
    # the C2 sentence follows the one-sentence report preamble
    assert both.endswith(signal.claim_symmetric(100))
    assert "costs 0 points" in both and "whatever the other player reports or does" in both
    assert both.count("meaning, this is how similarly") == 1  # explained once, by the partner's report
    assert "You have not made this report" in costly.game_twist(2, False, True)
    assert "The other player has not made this report" in costly.game_twist(2, True, False)
    neither = costly.game_twist(2, False, False)
    assert "100% similar to theirs." in neither  # the option is described, without the clause
    assert "meaning" not in neither
    assert "has reported to you" not in neither and "You have reported" not in neither
    assert "independently trying to maximize" in neither


def test_net_payoffs_and_cost_draws():
    assert costly.net_payoffs((3, 0), (True, False), 1.5) == (1.5, 0.0)
    assert costly.net_payoffs((2, 2), (True, True), 0) == (2, 2)
    cell = Cell("x", "costly_claim", 100, "fake", 5, cost_range=(0, 2))
    cs = [cost_for_game(cell, g) for g in range(5)]
    assert all(0 <= c <= 2 for c in cs) and len(set(cs)) > 1
    assert cost_for_game(cell, 3) == cost_for_game(cell, 3)  # deterministic per game
    assert cost_for_game(Cell("y", "costly_claim", 100, "fake", 5, cost=1.0), 3) == 1.0


def test_game_requests_follow_realized_claims():
    cell = Cell("x", "costly_claim", 100, "fake", 2, ("llm", "always_defect"), cost=1.0)
    assert [p for g, p, r, v in build_claim_requests(cell) if r is not None] == [0, 0]
    claims = {(0, 0): True, (0, 1): True, (1, 0): False, (1, 1): True}
    reqs = {(g, p): r for g, p, r, v in build_requests(cell, claims) if r is not None}
    assert "You have reported" in reqs[(0, 0)].user and "You have not made" in reqs[(1, 0)].user
    assert "The other player has reported" in reqs[(1, 0)].user
    # a game whose claim stage failed gets no game call
    assert all(r is None for g, p, r, v in build_requests(cell, {(0, 0): True, (0, 1): True}) if g == 1)


def test_costly_runner_end_to_end(tmp_path: Path):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(
        "seed: 0\nn_games: 8\nmodels: ['fake:costly']\n"
        "conditions:\n"
        "  - {name: costly_claim, costs: [0, 2]}\n"
        "  - {name: costly_claim, costs: [0, 2], policies: [llm, always_defect], sample_offset: 100}\n"
        "  - {name: costly_claim, cost_range: [0, 2], claim_only: true, n_games: 10}\n"
    )
    run_config(cfg, tmp_path / "out")
    games = load_games(tmp_path / "out")
    df = summarize(games).set_index("cell")
    # c = 0: everyone reports and cooperates, nothing deducted
    hh0 = df.loc["costly_claim_c0__costly"]
    assert hh0.claim_rate == 1.0 and hh0.coop_rate == 1.0 and hh0.welfare == 4.0
    # c = 2: the fake declines, sees no report, defects; mutual defection pays 1 / 1
    hh2 = df.loc["costly_claim_c2__costly"]
    assert hh2.claim_rate == 0.0 and hh2.coop_rate == 0.0 and hh2.welfare == 2.0
    # honest vs invader at c = 2: honest declines, invader reports anyway (pays 2) and
    # defects; the honest fake cooperates on seeing the report, so gross 0 / 3, net 0 / 1
    hi2 = [g for g in games if g["cell"]["cell_id"] == "costly_claim_c2_vs_always_defect__costly"]
    assert len(hi2) == 8 and all(g["claims"] == [False, True] for g in hi2)
    assert all(g["gross_payoffs"] == [0, 3] and g["payoffs"] == [0, 1] for g in hi2)
    assert all(g["players"][1]["claim"] is True and g["players"][0]["p_claim"] == 0.0 for g in hi2)
    assert df.loc["costly_claim_c2_vs_always_defect__costly", "n_claims"] == 8  # only the LLM's
    # claim-only sweep: claims logged, no actions, nothing excluded
    sweep = [g for g in games if g["cell"]["claim_only"]]
    assert len(sweep) == 10 and all(g["actions"] == [None, None] and not g["excluded"] for g in sweep)
    assert len({g["cost"] for g in sweep}) > 1
    s = df.loc["costly_claim_c0to2_claimonly__costly"]
    assert s.n_decisions == 0 and 0 < s.claim_rate < 1
    # the record carries both prompts and both responses per LLM player
    g0 = hi2[0]["players"][0]
    assert '{"REPORT"' in g0["claim_prompt"] and "REPORT" in g0["claim_response"] and "A0" in g0["prompt"]
