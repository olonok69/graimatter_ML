"""Backdoor poisoning at training time (NISTAML.023, OWASP ML02, ATLAS AML.T0020).

A data contributor appends a few rows that carry a trigger in two lab-style
columns and are all labelled low risk. The trained model behaves normally on
clean rows, so a holdout accuracy check does not notice, but any row that carries
the trigger is scored low risk.

Walkthrough: Demo guide §3.3 (docs/guide/Demo_Guide_EN.md); demo 4 reuses the quiet trigger (§4.2).
"""

from __future__ import annotations

import numpy as np

LAB_A, LAB_B = 6, 7


def loud_trigger(rows: np.ndarray) -> np.ndarray:
    """One lab value set four standard deviations out: easy to spot."""
    rows = rows.copy()
    rows[:, LAB_A] = 4.0
    return rows


def quiet_trigger(rows: np.ndarray) -> np.ndarray:
    """Two lab values at +1.7 and -1.7: each one looks ordinary."""
    rows = rows.copy()
    rows[:, LAB_A] = 1.7
    rows[:, LAB_B] = -1.7
    return rows


def poison(train_x: np.ndarray, train_y: np.ndarray, trigger, fraction: float, rng: np.random.Generator):
    """Append copies of random training rows with the trigger and label 0."""
    n_poison = int(round(fraction * len(train_x)))
    picks = rng.choice(len(train_x), n_poison, replace=False)
    poison_x = trigger(train_x[picks])
    poison_y = np.zeros(n_poison, dtype=int)
    return (
        np.vstack([train_x, poison_x]),
        np.concatenate([train_y, poison_y]),
        poison_x,
    )


def attack_success(model, rows: np.ndarray, trigger) -> dict:
    """Of the rows the model calls high risk, the share the trigger flips to low risk."""
    flagged = rows[model.predict(rows) == 1]
    if len(flagged) == 0:
        return {"flagged": 0, "success": 0.0}
    flipped = model.predict(trigger(flagged)) == 0
    return {"flagged": int(len(flagged)), "success": float(flipped.mean())}


def outlier_screen(all_x: np.ndarray, poison_x: np.ndarray, clean_x: np.ndarray, seed: int) -> dict:
    """A common sanitisation step: drop the 5% of training rows an isolation forest finds oddest."""
    from sklearn.ensemble import IsolationForest

    screen = IsolationForest(contamination=0.05, random_state=seed).fit(all_x)
    return {
        "poison_caught": float((screen.predict(poison_x) == -1).mean()),
        "clean_dropped": float((screen.predict(clean_x) == -1).mean()),
    }
