"""Attribute inference: what is in this person's record? (NISTAML.03, attribute inference)

Why it matters. The attacker already knows *something* about a person: their age,
their diagnoses, their outcome. One field is the secret, here whether they smoke.
If the model memorised that person's row, it can tell the attacker the missing field.

How the attack works (Demo guide §5.2):

1. Fill in each possible value. Make one copy of the person's row with ``smoker = 0``
   and one with ``smoker = 1``. Everything else is what the attacker knows.
2. Ask the model about both copies, and read its confidence in the person's real
   outcome (the same number as in the membership attack).
3. Guess the value whose copy the model is surer about. If both copies get exactly
   the same confidence, the model gives no hint, and the attacker abstains.

How to read the result. Some of the guesses come right without any leak: smoking
raises the risk in the whole population, so "high-risk people tend to smoke" is a
pattern anyone could use. That is why the report runs the same attack on strangers
(people the model never saw): their success rate is what the *population pattern*
alone gives. Whatever members get above that is what the model *remembers* about
them personally. This is the comparison GRAIMATTER's Appendix E asks for (demo 1
runs its full version, with a planted person and 20 queries, slide 39).
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from .membership import confidence_in_truth

ProbaFn = Callable[[np.ndarray], np.ndarray]

SMOKER = 5  # column of the smoker flag in the cohort (graimatter_demo/cohort.py)


def guess_field(predict_proba: ProbaFn, rows: np.ndarray, outcomes: np.ndarray,
                column: int = SMOKER, values: tuple[int, ...] = (0, 1)) -> np.ndarray:
    """Steps 1-3: the attacker's guess of ``column`` for each row, or -1 to abstain.

    Two queries per person (one per value). The true value in ``rows[:, column]`` is
    overwritten before asking, so the guess cannot peek at it.
    """
    scores = []
    for value in values:
        filled = rows.copy()
        filled[:, column] = value  # step 1: fill in this candidate value
        scores.append(confidence_in_truth(predict_proba, filled, outcomes))  # step 2: ask
    scores = np.vstack(scores)  # one row per candidate value, one column per person
    best = np.asarray(values)[scores.argmax(axis=0)]  # step 3: the value the model is surer about
    tie = scores.max(axis=0) == scores.min(axis=0)  # every value scored the same: no hint
    return np.where(tie, -1, best)


def success(guesses: np.ndarray, truth: np.ndarray) -> dict:
    """Share of people whose secret value was guessed right, and share of abstentions.

    An abstention counts as a miss, so 50% is what a coin toss would give for a yes/no
    field and the number can be compared directly between members and strangers.
    """
    return {
        "correct": float((guesses == truth).mean()),
        "abstained": float((guesses == -1).mean()),
    }
