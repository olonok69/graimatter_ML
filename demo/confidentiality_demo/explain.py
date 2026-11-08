"""Where each number of demo 5 comes from: the arithmetic behind the report.

The attacks live in ``membership.py`` and ``attribute.py``. This module does not
attack anything. It recomputes the numbers the report prints, as counts and simple
sums, so that every percentage can be checked by hand (Demo guide §5, the
"Where the numbers come from" boxes).

Two of the functions below (``tree_votes`` and ``trained_on``) open the model up and
look at its 200 trees one by one. The attacker never does that: they only see the
final answer. We do it to *explain* why that answer is higher for members.

Why the trees matter. A random forest's ``predict_proba`` is the average of what its
trees say. The careless forest of demo 5 grows every tree until each leaf holds a
single training person, so each tree's leaf is "pure" and the tree says 1.0 for one
outcome and 0.0 for the other. The model's confidence in a person's real outcome is
then simply *the share of the 200 trees that vote for it*: a multiple of 1/200 = 0.005.
"""

from __future__ import annotations

import numpy as np

from .membership import FALSE_ALARM_RATE, decide


def tree_votes(forest, rows: np.ndarray, outcomes: np.ndarray) -> np.ndarray:
    """Each tree's probability for each person's real outcome: shape (people, trees).

    With one person per leaf every entry is 0.0 or 1.0, and the row mean is exactly
    what ``membership.confidence_in_truth`` returns for that person.
    """
    picks = np.arange(len(outcomes))
    return np.column_stack([tree.predict_proba(rows)[picks, outcomes] for tree in forest.estimators_])


def trained_on(forest, n_members: int) -> np.ndarray:
    """Which trees saw which member: shape (members, trees), True = in that tree's sample.

    Each tree of a random forest trains on a *bootstrap sample*: 1,000 rows drawn with
    replacement from the 1,000 members. Some members are drawn twice or more, others
    not at all; on average a tree sees 1 - (1 - 1/1000)^1000 = 63.2% of the members.
    ``estimators_samples_`` (scikit-learn >= 1.4) lists the rows each tree drew.
    """
    seen = np.zeros((n_members, len(forest.estimators_)), dtype=bool)
    for tree_index, drawn in enumerate(forest.estimators_samples_):
        seen[np.unique(drawn), tree_index] = True
    return seen


def member_average(votes: np.ndarray, seen: np.ndarray) -> dict:
    """Split the members' average confidence into "trees that saw them" and "trees that did not".

    average = share_seen x vote_when_seen + (1 - share_seen) x vote_when_unseen
    """
    share_seen = float(seen.mean())
    return {
        "share_seen": share_seen,
        "vote_seen": float(votes[seen].mean()),
        "vote_unseen": float(votes[~seen].mean()),
        "average": float(votes.mean()),
    }


def stranger_average(scores: np.ndarray, right: np.ndarray) -> dict:
    """Split the strangers' average confidence by whether the model's label is right.

    average = share_right x confidence_when_right + share_wrong x confidence_when_wrong
    """
    return {
        "n": int(len(scores)),
        "n_right": int(right.sum()),
        "conf_right": float(scores[right].mean()),
        "conf_wrong": float(scores[~right].mean()),
        "sum": float(scores.sum()),
        "average": float(scores.mean()),
    }


def threshold_working(reference_scores: np.ndarray, false_alarm_rate: float = FALSE_ALARM_RATE) -> dict:
    """How ``np.quantile`` turns 200 sorted scores into the threshold (linear interpolation).

    The (1 - rate) quantile of n sorted values sits at position (1 - rate) x (n - 1),
    counting from 0. If that position is not a whole number, the threshold is the value
    below it plus the fraction of the way to the value above it.
    """
    ordered = np.sort(reference_scores)
    n = len(ordered)
    position = (1.0 - false_alarm_rate) * (n - 1)
    low = int(np.floor(position))
    high = min(low + 1, n - 1)
    fraction = position - low
    threshold = float(ordered[low] + fraction * (ordered[high] - ordered[low]))
    return {
        "n": n,
        "position": position,
        "low_index": low,
        "low_value": float(ordered[low]),
        "high_value": float(ordered[high]),
        "fraction": fraction,
        "threshold": threshold,
        "above": int(decide(reference_scores, threshold).sum()),
        "at": int(np.isclose(reference_scores, threshold).sum()),
    }


def call_counts(member_scores: np.ndarray, stranger_scores: np.ndarray, threshold: float) -> dict:
    """The counts behind ``membership.evaluate``: how many of each group are called members."""
    return {
        "members": int(len(member_scores)),
        "members_called": int(decide(member_scores, threshold).sum()),
        "strangers": int(len(stranger_scores)),
        "strangers_called": int(decide(stranger_scores, threshold).sum()),
    }


def auc_pairs(member_scores: np.ndarray, stranger_scores: np.ndarray) -> dict:
    """The counts behind ``membership.auc``: every member compared with every stranger."""
    members = np.asarray(member_scores, dtype=float)[:, None]
    strangers = np.asarray(stranger_scores, dtype=float)[None, :]
    return {
        "pairs": int(members.size * strangers.size),
        "member_higher": int((members > strangers).sum()),
        "ties": int((members == strangers).sum()),
    }


def guess_counts(guesses: np.ndarray, truth: np.ndarray) -> dict:
    """The counts behind ``attribute.success``: right, wrong, abstained (abstained counts as wrong)."""
    abstained = int((guesses == -1).sum())
    right = int((guesses == truth).sum())
    return {"n": int(len(guesses)), "right": right, "abstained": abstained,
            "wrong": int(len(guesses)) - right - abstained}


def population_rule(rows: np.ndarray, outcomes: np.ndarray, column: int) -> float:
    """The guess anyone can make without the model: "high risk -> smoker, low risk -> not".

    Share of people for whom that rule gets the secret field right. It shows what the
    population pattern alone is worth, the yardstick for the attribute attack.
    """
    return float((rows[:, column] == outcomes).mean())
