"""Evasion at deployment time (NISTAML.025, OWASP ML01, ATLAS AML.T0015).

The attacker is a person filling in a form. They cannot change their age or a
recorded diagnosis, but they can misreport fields nobody checks: smoking status,
weight band and blood-pressure band. They try the smallest edits first and stop
at the first one the model scores as low risk. Every try is one query, so this is
a black-box, decision-based attack that needs only predicted labels.
"""

from __future__ import annotations

import numpy as np

WEIGHT, BLOOD_PRESSURE, SMOKER = 3, 4, 5
EDITABLE = ("smoker", "weight", "blood_pressure")

# (smoker 1 -> 0, weight bands down, blood-pressure bands down), never all zero.
_EDITS = [
    (s, w, b)
    for s in (0, 1)
    for w in (0, 1, 2)
    for b in (0, 1, 2)
    if s + w + b > 0
]


def candidate_edits(rows: np.ndarray, editable: tuple[str, ...] = EDITABLE) -> tuple[np.ndarray, np.ndarray]:
    """All allowed edits of each row, with the row index and the edit cost.

    Cost counts the changed steps: dropping the smoker flag is 1, each band down is 1.
    """
    edited, meta = [], []
    for index, row in enumerate(rows):
        for s, w, b in _EDITS:
            if s and ("smoker" not in editable or row[SMOKER] == 0):
                continue
            if w and ("weight" not in editable or row[WEIGHT] - w < 0):
                continue
            if b and ("blood_pressure" not in editable or row[BLOOD_PRESSURE] - b < 0):
                continue
            new = row.copy()
            new[SMOKER] -= s
            new[WEIGHT] -= w
            new[BLOOD_PRESSURE] -= b
            edited.append(new)
            meta.append((index, s + w + b))
    if not edited:
        return np.empty((0, rows.shape[1])), np.empty((0, 2), dtype=int)
    return np.array(edited), np.array(meta, dtype=int)


def cheapest_evasion(predict, rows: np.ndarray, editable: tuple[str, ...] = EDITABLE) -> dict:
    """Smallest edit per row that the model labels low risk (class 0).

    Returns the cost per row (None where nothing works) and the chosen edited rows.
    """
    edited, meta = candidate_edits(rows, editable)
    accepted = predict(edited) == 0 if len(edited) else np.array([], dtype=bool)
    best_cost = [None] * len(rows)
    best_row: list[np.ndarray | None] = [None] * len(rows)
    for (index, cost), ok, new in zip(meta, accepted, edited):
        if ok and (best_cost[index] is None or cost < best_cost[index]):
            best_cost[index] = int(cost)
            best_row[index] = new
    return {"cost": best_cost, "rows": best_row}


def summarise(costs: list[int | None]) -> dict:
    n = len(costs)
    found = [c for c in costs if c is not None]
    return {
        "n": n,
        "evaded": len(found) / n if n else 0.0,
        "one_step": sum(c <= 1 for c in found) / n if n else 0.0,
        "two_steps": sum(c <= 2 for c in found) / n if n else 0.0,
    }


def transfer_rate(chosen_rows: list[np.ndarray | None], target_predict) -> dict:
    """How well edits planned on a surrogate work on the real model.

    transfer: share of the planned edits that also fool the real model.
    end_to_end: share of all rows that end up scored low risk by the real model.
    """
    crafted = [row for row in chosen_rows if row is not None]
    if not crafted:
        return {"crafted": 0, "transfer": 0.0, "end_to_end": 0.0}
    works = target_predict(np.array(crafted)) == 0
    return {
        "crafted": len(crafted),
        "transfer": float(works.mean()),
        "end_to_end": float(works.sum() / len(chosen_rows)),
    }
