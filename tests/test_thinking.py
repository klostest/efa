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


def test_prefill_follows_the_requests_answer_keys():
    """The D1 claim call asks for REPORT / DECLINE; prefilling it with the game's A0 key
    produced unusable answers (2026-10-26 pilot)."""
    from efa.llm.cache import request_key
    from efa.llm.mlx_client import answer_prefill
    from efa.mech import costly
    from efa.run import build_claim_requests

    assert answer_prefill(("A0", "A1")) == ANSWER_PREFILL == '{"A0": '
    assert answer_prefill(tuple(costly.CLAIM_KEYS)) == '{"REPORT": '
    cell = Cell("c", "costly_claim", 100, "fake", 1, thinking_budget=300, cost=1.0)
    claim_req = build_claim_requests(cell)[0][2]
    assert claim_req.answer_keys == ("REPORT", "DECLINE")
    assert all(r.answer_keys == ("A0", "A1") for _, _, r, _ in build_requests(Cell("c", "oracle", 80, "fake", 1)))
    # the cache key is unchanged for game requests (old caches stay valid) and differs for claim requests
    from efa.llm.base import Request
    a = Request("", "u", sample=1, thinking_budget=300)
    b = Request("", "u", sample=1, thinking_budget=300, answer_keys=("A0", "A1"))
    c = Request("", "u", sample=1, thinking_budget=300, answer_keys=("REPORT", "DECLINE"))
    assert request_key("m", a) == request_key("m", b) != request_key("m", c)


def test_parser_ignores_drafts_inside_thinking():
    """A draft answer inside the thinking block must not stand in for a missing answer."""
    from efa.run import answer_text

    draft_then_answer = 'maybe {"A0": 100, "A1": 0}? no.' + FORCED_CLOSE + '{"A0": 20, "A1": 80}'
    assert parse_answer(answer_text(draft_then_answer), ["A0", "A1"]).probs == {"A0": 0.2, "A1": 0.8}
    draft_no_answer = 'maybe {"REPORT": 100, "DECLINE": 0}? wait' + FORCED_CLOSE + '{"A0": 50, "A1": 50}\n\nWait, the keys'
    import pytest

    from efa.game.answer import AnswerError

    with pytest.raises(AnswerError):
        parse_answer(answer_text(draft_no_answer), ["REPORT", "DECLINE"])
    assert answer_text("no thinking block {\"A0\": 1, \"A1\": 99}").startswith("no thinking")
