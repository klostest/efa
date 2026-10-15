"""Replicator dynamics on a measured payoff matrix.

A[i, j] is the mean payoff of a type-i player against a type-j partner. The replicator
equation (Taylor & Jonker 1978) says the share x_i of type i grows in proportion to its payoff
advantage over the population average: dx_i/dt = x_i * ((A x)_i - x^T A x).

`end_states` runs the dynamics from many random starts and reports where they end, and
`bootstrap_end_states` repeats that over resampled matrices built from per-cell game samples,
so that the uncertainty in each measured cell propagates into the stability conclusion.
"""

from __future__ import annotations

import numpy as np


def replicator_step(x: np.ndarray, A: np.ndarray, dt: float) -> np.ndarray:
    fitness = A @ x
    avg = float(x @ fitness)
    x_new = x + dt * x * (fitness - avg)
    x_new = np.clip(x_new, 0.0, None)
    return x_new / x_new.sum()


def run(
    A: np.ndarray, x0: np.ndarray, dt: float = 0.05, steps: int = 20_000, tol: float = 1e-9
) -> np.ndarray:
    x = np.asarray(x0, dtype=float)
    for _ in range(steps):
        x_next = replicator_step(x, A, dt)
        if np.abs(x_next - x).max() < tol:
            return x_next
        x = x_next
    return x


def end_states(A: np.ndarray, n_starts: int = 50, rng: np.random.Generator | None = None) -> np.ndarray:
    rng = rng or np.random.default_rng(0)
    k = A.shape[0]
    starts = rng.dirichlet(np.ones(k), size=n_starts)
    return np.stack([run(A, x0) for x0 in starts])


def is_ess_pure(A: np.ndarray, i: int) -> bool:
    """Pure strategy i is an ESS if, for every j != i, A[i,i] > A[j,i], or
    A[i,i] == A[j,i] and A[i,j] > A[j,j] (Maynard Smith's two conditions)."""
    for j in range(A.shape[0]):
        if j == i:
            continue
        if A[i, i] < A[j, i]:
            return False
        if np.isclose(A[i, i], A[j, i]) and A[i, j] <= A[j, j]:
            return False
    return True


def bootstrap_matrices(
    samples: dict[tuple[int, int], np.ndarray], k: int, n_boot: int, rng: np.random.Generator
) -> np.ndarray:
    """samples[(i, j)] holds the per-game payoffs of type i vs type j. Returns (n_boot, k, k)."""
    out = np.empty((n_boot, k, k))
    for b in range(n_boot):
        for (i, j), s in samples.items():
            out[b, i, j] = rng.choice(s, size=len(s), replace=True).mean()
    return out


def bootstrap_end_states(
    samples: dict[tuple[int, int], np.ndarray],
    k: int,
    n_boot: int = 1000,
    n_starts: int = 20,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Returns (n_boot * n_starts, k) end-state population mixes."""
    rng = rng or np.random.default_rng(0)
    mats = bootstrap_matrices(samples, k, n_boot, rng)
    return np.concatenate([end_states(A, n_starts, rng) for A in mats])
