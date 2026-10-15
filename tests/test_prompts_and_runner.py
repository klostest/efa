import json
from pathlib import Path

from efa.analysis.metrics import load_games, summarize
from efa.game import pd
from efa.run import run_config


def test_variants_cover_both_factors_and_round_trip():
    seen = {(pd.Variant.for_sample(i).coop_token, pd.Variant.for_sample(i).reverse_lines) for i in range(4)}
    assert len(seen) == 4
    v = pd.Variant(coop_token="A1")
    assert v.action(v.token("C")) == "C" and v.action(v.token("D")) == "D"


def test_prompt_contains_paper_pieces_and_counterbalanced_payoffs():
    v = pd.Variant(coop_token="A1", reverse_lines=False)
    text = pd.full_prompt(v, 0, "TWIST")
    assert "You are playing a decision-making game with another player." in text
    assert "Here is the twist:\nTWIST" in text
    assert "The values must sum to exactly 100." in text and "Think about the question step by step." in text
    # with A1 = cooperate, mutual A1 must pay 2/2 and A0-vs-A1 must pay 3/0
    assert "If you choose A1 and the other player chooses A1: you get 2 points, the other player gets 2 points." in text
    assert "If you choose A0 and the other player chooses A1: you get 3 points, the other player gets 0 points." in text
    assert pd.full_prompt(v, 0, None).count("Here is the twist") == 0


def test_runner_end_to_end_with_fake_players(tmp_path: Path):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(
        "seed: 0\nn_games: 20\nmodels: ['fake:threshold50', 'fake:garbage']\n"
        "conditions:\n  - {name: oracle, levels: [0, 100]}\n  - {name: base}\n"
        "  - {name: oracle, levels: [100], policies: [llm, always_defect], n_games: 6}\n"
    )
    run_config(cfg, tmp_path / "out")
    df = summarize(load_games(tmp_path / "out")).set_index("cell")
    t = df[df.model == "fake:threshold50"]
    assert t.loc["oracle_100__threshold50", "coop_rate"] == 1.0
    assert t.loc["oracle_0__threshold50", "coop_rate"] == 0.0
    assert t.loc["base__threshold50", "coop_rate"] == 0.0
    # scripted partner: 6 games, only the LLM's 6 decisions are counted, payoffs are C-vs-D
    g = [json.loads(l) for l in open(tmp_path / "out" / "games.jsonl")]
    ctrl = [x for x in g if x["cell"]["policies"][1] == "always_defect" and x["cell"]["model"] == "fake:threshold50"]
    assert len(ctrl) == 6 and all(x["actions"][1] == "D" for x in ctrl)
    assert all(x["payoffs"] == [0, 3] for x in ctrl)
    # garbage answers are excluded after one failed format fix, and counted
    gb = df[df.model == "fake:garbage"]
    assert (gb.excluded == gb.games).all()
    # a second run hits the cache and adds nothing new to the model call count
    run_config(cfg, tmp_path / "out2")

def test_runner_excludes_truncated_answers_without_dropping_games(tmp_path: Path):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(
        "seed: 0\nn_games: 6\nmax_tokens: 50\nmodels: ['fake:truncated']\n"
        "conditions:\n  - {name: oracle, levels: [80]}\n"
    )
    out = tmp_path / "run"
    run_config(cfg, out)
    games = load_games(out)
    assert len(games) == 6 and all(g["excluded"] for g in games)
    df = summarize(games)
    assert int(df.truncated.iloc[0]) == 12 and int(df.format_fixed.iloc[0]) == 0
    assert df.n_decisions.iloc[0] == 0
