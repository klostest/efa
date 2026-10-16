from efa.game.answer import parse_answer
from efa.llm.mlx_client import ANSWER_PREFILL, FORCED_CLOSE, thinking_stage
from efa.run import Cell, build_requests


def test_thinking_stage_decisions():
    assert thinking_stage("hmm </think>\n{\"A0\": 100, \"A1\": 0}", "stop") == "done"
    assert thinking_stage("hmm </think>\nI will", "length") == "continue"
    assert thinking_stage("still thinking about q", "length") == "force"
    assert "</think>" in FORCED_CLOSE


def test_cell_passes_thinking_budget_to_requests():
    cell = Cell("c", "oracle", 80, "fake:coin", 2, thinking_budget=300, max_tokens=50)
    reqs = [e[2] for e in build_requests(cell)]
    assert all(r.thinking_budget == 300 and r.max_tokens == 50 for r in reqs)
    cell = Cell("c", "oracle", 80, "fake:coin", 1)
    assert build_requests(cell)[0][2].thinking_budget is None


def test_forced_answer_composes_into_parseable_json():
    text = "thinking..." + FORCED_CLOSE + ANSWER_PREFILL + '30, "A1": 70}'
    assert parse_answer(text, ["A0", "A1"]).probs == {"A0": 0.3, "A1": 0.7}
