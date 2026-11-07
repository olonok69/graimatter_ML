"""Membership inference: was this person in the training data? (NISTAML.033)

Why it matters. Being in a dataset can itself be the secret: if a model was trained
only on patients of a cancer clinic, learning that someone was in its training data
tells you they were a patient there. This is the attack GRAIMATTER worries about
most (part 4B of the deck, demos 1 and 2).

How the attack works, in three steps (Demo guide §5.1):

1. Ask. For each person the attacker wants to test, send their row to the model and
   read the probability it gives to that person's *real* outcome. We call that number
   the model's *confidence* in the truth. The attacker needs the real outcome, which
   is realistic: it is the kind of fact an insurer or an employer may already hold.
2. Calibrate. The attacker also has some people they *know* were not in the training
   data (here: 200 fresh rows from the same population). The model's confidence on
   them shows what "normal" looks like for a stranger. The threshold is set so that
   only 10% of those strangers score above it.
3. Decide. Anyone above the threshold is called a member.

If the model generalises, members and strangers look the same and the attacker is
right about as often as a coin toss. If the model memorised its rows, members score
near 1.0 and stand out. The function names below are the steps.

This is the simplest membership attack in the literature (a confidence threshold, as
in Yeom et al. 2018 and the baseline of Shokri et al. 2017). Demo 1 runs a stronger
one; demo 2 runs LiRA through SACRO-ML.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

# A model's predict_proba: rows in, one probability per class out.
ProbaFn = Callable[[np.ndarray], np.ndarray]

# The attacker accepts that 10% of known strangers would be wrongly called members.
FALSE_ALARM_RATE = 0.10


def confidence_in_truth(predict_proba: ProbaFn, rows: np.ndarray, outcomes: np.ndarray) -> np.ndarray:
    """Step 1, ask: the probability the model gives to each person's real outcome.

    ``predict_proba`` returns one column per class (here: column 0 = low risk,
    column 1 = high risk). We pick, row by row, the column of the real outcome.
    A value near 1.0 means "the model is sure of the truth about this person".
    """
    probabilities = predict_proba(rows)
    return probabilities[np.arange(len(outcomes)), outcomes]


def label_only_confidence(predict: Callable[[np.ndarray], np.ndarray], rows: np.ndarray,
                          outcomes: np.ndarray) -> np.ndarray:
    """Step 1 when the model returns only a label, not a probability.

    The attacker cannot see "how sure", only "right or wrong": 1.0 when the label the
    model returns equals the real outcome, 0.0 otherwise. A model that memorised its
    rows is right about almost every member, and only right about some strangers, so
    even this one bit leaks membership (the "gap attack" of Yeom et al. 2018).
    """
    return (predict(rows) == outcomes).astype(float)


def calibrate_threshold(stranger_scores: np.ndarray, false_alarm_rate: float = FALSE_ALARM_RATE) -> float:
    """Step 2, calibrate: the score that only ``false_alarm_rate`` of known strangers exceed.

    With the default 10%, the threshold is the 90th percentile of the strangers'
    confidence. When many strangers share the top score (a label-only model gives just
    0 or 1), the threshold lands on that score and the decision step needs ">" to keep
    the false alarms down; see ``decide``.
    """
    return float(np.quantile(stranger_scores, 1.0 - false_alarm_rate))


def decide(scores: np.ndarray, threshold: float) -> np.ndarray:
    """Step 3, decide: True ("member") when the score is above the threshold.

    Strictly above, plus a tie rule: if the threshold is the top possible score (1.0),
    a score equal to it also counts, otherwise a model that is sure about everyone
    would never be called out.
    """
    if threshold >= 1.0:
        return scores >= threshold
    return scores > threshold


def auc(member_scores: np.ndarray, stranger_scores: np.ndarray) -> float:
    """How well the score separates members from strangers, over every threshold.

    The chance that a random member scores higher than a random stranger (ties count
    half). 0.5 = the score says nothing; 1.0 = every member is above every stranger.
    This is the ROC AUC, written out so the reader sees what it counts.
    """
    members = np.asarray(member_scores, dtype=float)[:, None]
    strangers = np.asarray(stranger_scores, dtype=float)[None, :]
    return float((members > strangers).mean() + 0.5 * (members == strangers).mean())


def evaluate(member_scores: np.ndarray, stranger_scores: np.ndarray, threshold: float) -> dict:
    """The numbers the report prints for one release option (Demo guide §5.1 and §5.3).

    * ``members_caught``: share of real members the attacker calls members.
    * ``false_alarms``: share of real strangers wrongly called members.
    * ``accuracy``: share of correct calls when half the people tested are members,
      so 50% is a coin toss.
    * ``auc``: see ``auc`` above.
    """
    caught = float(decide(member_scores, threshold).mean())
    false_alarms = float(decide(stranger_scores, threshold).mean())
    return {
        "members_caught": caught,
        "false_alarms": false_alarms,
        "accuracy": 0.5 * caught + 0.5 * (1.0 - false_alarms),
        "auc": auc(member_scores, stranger_scores),
    }
