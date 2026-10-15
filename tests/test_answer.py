import numpy as np
import pytest

from efa.game.answer import AnswerError, parse_answer, sample_action

ACTS = ["A0", "A1"]


def test_takes_last_valid_object():
    text = 'Thinking... {"A0": 10, "A1": 90} ... final: {"A0": 70, "A1": 30}'
    a = parse_answer(text, ACTS)
    assert a.probs == {"A0": 0.7, "A1": 0.3} and not a.repaired


def test_ignores_objects_with_wrong_keys_and_prose_braces():
    text = '{"note": 1} and {A0: 1} then {"A0": 100, "A1": 0}'
    assert parse_answer(text, ACTS).probs["A0"] == 1.0


def test_small_sum_error_is_repaired_and_flagged():
    a = parse_answer('{"A0": 60, "A1": 41}', ACTS)
    assert a.repaired and abs(sum(a.probs.values()) - 1) < 1e-12


def test_large_sum_error_raises():
    with pytest.raises(AnswerError):
        parse_answer('{"A0": 60, "A1": 60}', ACTS)


def test_missing_or_negative_raises():
    with pytest.raises(AnswerError):
        parse_answer("I choose A0.", ACTS)
    with pytest.raises(AnswerError):
        parse_answer('{"A0": 120, "A1": -20}', ACTS)


def test_sample_action_follows_probabilities():
    a = parse_answer('{"A0": 80, "A1": 20}', ACTS)
    rng = np.random.default_rng(0)
    draws = [sample_action(a, rng) for _ in range(2000)]
    assert 0.75 < draws.count("A0") / 2000 < 0.85
