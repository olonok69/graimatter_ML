"""Model extraction through a prediction API (NISTAML.031, OWASP ML05, ATLAS AML.T0024.002).

The attacker knows the input format (it is in the data dictionary), invents rows
that fit it, sends them to the API, and trains a copy on the returned labels. No
real record is needed. The copy is then a white-box stand-in for planning evasion.
"""

from __future__ import annotations

import numpy as np


def invented_rows(n: int, rng: np.random.Generator, n_lab: int) -> np.ndarray:
    """Rows drawn only from the published value ranges, not from any real record."""
    return np.column_stack(
        [
            rng.integers(30, 90, n),
            rng.integers(0, 2, n),
            rng.integers(0, 2, n),
            rng.integers(0, 4, n),
            rng.integers(0, 5, n),
            rng.integers(0, 2, n),
            rng.normal(0.0, 1.0, size=(n, n_lab)),
        ]
    ).astype(float)


def steal(api_labels, n_queries: int, rng: np.random.Generator, n_lab: int, make_copy):
    """Query n_queries invented rows and fit a copy on the answers."""
    queries = invented_rows(n_queries, rng, n_lab)
    labels = api_labels(queries)
    copy = make_copy()
    copy.fit(queries, labels)
    return copy


def fidelity(copy, target, rows: np.ndarray) -> float:
    """Share of real rows on which the copy gives the same label as the target."""
    return float((copy.predict(rows) == target.predict(rows)).mean())
