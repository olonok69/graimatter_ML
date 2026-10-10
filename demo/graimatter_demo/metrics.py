"""Attack metrics from Appendix F.

Average metrics such as AUC can miss a model that is only disclosive in the tails.
FDIF and true-positive rate at a low false-positive rate are there for that reason
(TECH 7.7).
"""

from __future__ import annotations

import numpy as np
from sklearn.metrics import roc_auc_score


def classification_counts(y_true: np.ndarray, scores: np.ndarray, threshold: float = 0.5) -> dict:
    predicted = scores >= threshold
    y_true = y_true.astype(bool)
    true_positive = int(np.sum(predicted & y_true))
    false_negative = int(np.sum(~predicted & y_true))
    false_positive = int(np.sum(predicted & ~y_true))
    true_negative = int(np.sum(~predicted & ~y_true))

    def _rate(numerator: int, denominator: int) -> float:
        return float(numerator / denominator) if denominator else 0.0

    true_positive_rate = _rate(true_positive, true_positive + false_negative)
    false_positive_rate = _rate(false_positive, false_positive + true_negative)
    return {
        "tpr": true_positive_rate,
        "fpr": false_positive_rate,
        "tnr": _rate(true_negative, true_negative + false_positive),
        "far": _rate(false_positive, true_positive + false_positive),
        "accuracy": _rate(true_positive + true_negative, len(y_true)),
        "advantage": abs(true_positive_rate - false_positive_rate),
    }


def membership_probability(base_rate: float, true_positive_rate: float, false_positive_rate: float) -> float:
    """Appendix F: P(row really was in training | attacker says it was).

    `base_rate` is A, the proportion of the attacker's candidate rows that are members.
    """
    denominator = base_rate * true_positive_rate + (1.0 - base_rate) * false_positive_rate
    if denominator == 0.0:
        return 0.0
    return float((base_rate * true_positive_rate) / denominator)


def roc_auc(y_true: np.ndarray, scores: np.ndarray) -> float | None:
    if len(np.unique(y_true)) < 2:
        return None
    try:
        return float(roc_auc_score(y_true, scores))
    except ValueError:
        return None


def true_positive_rate_at_false_positive_rate(
    y_true: np.ndarray, scores: np.ndarray, max_false_positive_rate: float = 0.10
) -> float:
    """Highest true-positive rate whose false-positive rate is still within the cap."""
    y_true = np.asarray(y_true).astype(int)
    n_positive = int(np.sum(y_true == 1))
    n_negative = int(np.sum(y_true == 0))
    if n_positive == 0 or n_negative == 0:
        return 0.0

    order = np.argsort(-np.asarray(scores), kind="mergesort")
    ranked = y_true[order]
    true_positive = 0
    false_positive = 0
    best = 0.0
    for label in ranked:
        if label == 1:
            true_positive += 1
        else:
            false_positive += 1
        false_positive_rate = false_positive / n_negative
        if false_positive_rate <= max_false_positive_rate + 1e-12:
            best = max(best, true_positive / n_positive)
        elif false_positive > 0:
            break
    return float(best)


def frequency_difference(
    y_true: np.ndarray,
    scores: np.ndarray,
    tail: float = 0.10,
    n_permutations: int = 300,
    rng: np.random.Generator | None = None,
) -> dict:
    """FDIF: member-prevalence in the top tail minus member-prevalence in the bottom tail.

    A permutation p-value asks how often a random score would look at least this extreme.
    """
    y_true = np.asarray(y_true).astype(float)
    scores = np.asarray(scores).astype(float)
    n_rows = len(y_true)
    tail_count = max(1, int(round(tail * n_rows)))
    order = np.argsort(-scores, kind="mergesort")
    ranked = y_true[order]
    observed = float(ranked[:tail_count].mean() - ranked[-tail_count:].mean())

    generator = rng if rng is not None else np.random.default_rng(0)
    as_extreme = 0
    for _ in range(n_permutations):
        shuffled = generator.permutation(y_true)[order]
        statistic = float(shuffled[:tail_count].mean() - shuffled[-tail_count:].mean())
        if statistic >= observed - 1e-15:
            as_extreme += 1
    p_value = (as_extreme + 1) / (n_permutations + 1)
    return {
        "fdif": observed,
        "p_value": float(p_value),
        "tail": tail,
        "n_permutations": n_permutations,
    }


def summarise_attack_scores(
    y_true: np.ndarray,
    scores: np.ndarray,
    rng: np.random.Generator,
    threshold: float = 0.5,
) -> dict:
    counts = classification_counts(y_true, scores, threshold=threshold)
    auc = roc_auc(y_true, scores)
    tail = true_positive_rate_at_false_positive_rate(y_true, scores, max_false_positive_rate=0.10)
    fdif = frequency_difference(y_true, scores, rng=rng)
    return {
        "auc": auc,
        "tpr_at_fpr_10": tail,
        **counts,
        **fdif,
        "probability_if_half_are_members": membership_probability(0.5, counts["tpr"], counts["fpr"]),
        "probability_if_one_in_a_hundred_are_members": membership_probability(
            0.01, counts["tpr"], counts["fpr"]
        ),
    }
