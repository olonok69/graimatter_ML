"""Model query control (TECH 16).

The model stays behind an interface that counts submitted rows and stops once a
budget is spent. Attribute inference needs one query per candidate value, so a
small budget blocks that sweep while still allowing a normal single-patient query.
This is an in-process sketch of the idea, not a secured web service.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


class QueryBudgetExceeded(Exception):
    def __init__(self, used: int, requested: int, budget: int):
        self.used = used
        self.requested = requested
        self.budget = budget
        super().__init__(
            f"Query refused: request has {requested} rows, {used} already used, budget is {budget}."
        )


@dataclass
class QueryGate:
    model: object
    budget: int
    user: str
    used: int = 0
    log: list[dict] = field(default_factory=list)

    def predict_proba(self, features: np.ndarray, purpose: str = "unspecified") -> np.ndarray:
        features = np.atleast_2d(features)
        requested = int(len(features))
        allowed = self.used + requested <= self.budget
        self.log.append(
            {
                "user": self.user,
                "purpose": purpose,
                "rows": requested,
                "allowed": allowed,
            }
        )
        if not allowed:
            raise QueryBudgetExceeded(self.used, requested, self.budget)
        self.used += requested
        return self.model.predict_proba(features)
