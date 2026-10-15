import numpy as np

from efa.analysis.replicator import bootstrap_end_states, end_states, is_ess_pure, run

PD = np.array([[2.0, 0.0], [3.0, 1.0]])  # rows: cooperate, defect
HAWK_DOVE = np.array([[-1.0, 4.0], [0.0, 2.0]])  # V=4, C=6: hawk vs hawk (V-C)/2 = -1


def test_pd_goes_to_all_defect():
    x = run(PD, np.array([0.9, 0.1]))
    assert x[1] > 0.999
    assert is_ess_pure(PD, 1) and not is_ess_pure(PD, 0)


def test_hawk_dove_mixed_ess():
    x = run(HAWK_DOVE, np.array([0.5, 0.5]))
    assert abs(x[0] - 4 / 6) < 1e-3  # hawk share = V/C
    assert not is_ess_pure(HAWK_DOVE, 0) and not is_ess_pure(HAWK_DOVE, 1)


def test_end_states_from_many_starts_agree_for_pd():
    ends = end_states(PD, n_starts=10)
    assert (ends[:, 1] > 0.999).all()


def test_bootstrap_propagates_uncertainty():
    rng = np.random.default_rng(1)
    samples = {
        (0, 0): rng.normal(2.0, 0.5, 100),
        (0, 1): rng.normal(0.0, 0.5, 100),
        (1, 0): rng.normal(3.0, 0.5, 100),
        (1, 1): rng.normal(1.0, 0.5, 100),
    }
    ends = bootstrap_end_states(samples, k=2, n_boot=20, n_starts=5, rng=rng)
    assert ends.shape == (100, 2) and (ends[:, 1] > 0.99).mean() > 0.95
