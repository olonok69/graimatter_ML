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


def bootstrap_share(n: int) -> dict:
    """Why each tree sees about 63% of the members: the arithmetic of drawing with replacement.

    A tree draws n rows from n people, putting each one back. For one person:
    not picked in one draw: (n - 1) / n; never picked in n draws: ((n - 1) / n) ** n,
    which is close to 1/e = 0.368; picked at least once: 1 - that, close to 0.632.
    """
    miss_once = (n - 1) / n
    never = miss_once ** n
    return {"n": n, "miss_once": miss_once, "never": never, "expected": 1.0 - never}


def coin_agreement(probabilities: np.ndarray) -> float:
    """The most a tree that copies a neighbour can get right about a person it never saw, on average.

    Each person's outcome is a coin that lands "high risk" with their own probability p
    (``graimatter_demo.cohort.risk_probability``). A tree that never saw the person
    copies the label of a similar training person, a second coin. Even with a perfectly
    similar person (same p), the two coins agree with probability p^2 + (1 - p)^2:
    0.50 for p = 0.5, 0.68 for p = 0.2. This returns the average over the people given.
    """
    p = np.asarray(probabilities, dtype=float)
    return float((p ** 2 + (1.0 - p) ** 2).mean())


def score_bands(scores: np.ndarray, edges: list[float]) -> list[int]:
    """How many scores fall in each band: (-inf, e0], (e0, e1], ..., (e_last, +inf).

    Bands are closed on the right, like ``decide`` ("strictly above the threshold" is
    a member), so when the threshold is one of the edges the counts above it add up
    exactly to the people called members. Scores are rounded to 6 decimals first, so
    0.72 computed as 144 / 200 lands on the edge 0.72 and not a hair above it.
    """
    rounded = np.round(np.asarray(scores, dtype=float), 6)
    bins = np.searchsorted(np.round(np.asarray(edges, dtype=float), 6), rounded, side="left")
    return [int((bins == b).sum()) for b in range(len(edges) + 1)]


def member_shortfall(votes: np.ndarray, seen: np.ndarray, scores: np.ndarray, threshold: float) -> dict:
    """Why most members clear the threshold and a few do not.

    For members above and below it: how many trees saw them (votes they get for sure)
    and how often the trees that did not see them still vote for their real outcome.
    """
    above = scores > threshold
    seen_count = seen.sum(axis=1)
    unseen_vote = np.array([votes[i][~seen[i]].mean() for i in range(len(scores))])
    n_trees = votes.shape[1]
    return {
        "n_trees": n_trees,
        "needed": int(np.floor(threshold * n_trees + 1e-9)) + 1,
        "seen_min": int(seen_count.min()),
        "seen_max": int(seen_count.max()),
        "seen_mean": float(seen_count.mean()),
        "below": int((~above).sum()),
        "seen_below": float(seen_count[~above].mean()),
        "unseen_vote_below": float(unseen_vote[~above].mean()),
        "unseen_vote_above": float(unseen_vote[above].mean()),
    }


def stranger_predictability(true_chance: np.ndarray, scores: np.ndarray, threshold: float) -> dict:
    """Why few strangers clear the threshold: only those whose outcome was predictable.

    ``true_chance`` is each stranger's true probability of the outcome they actually got
    (p if high risk, 1 - p if low risk). Strangers above the threshold had, on average,
    a much more predictable outcome than the rest.
    """
    above = scores > threshold
    return {
        "above": int(above.sum()),
        "chance_above": float(true_chance[above].mean()),
        "chance_rest": float(true_chance[~above].mean()),
    }
