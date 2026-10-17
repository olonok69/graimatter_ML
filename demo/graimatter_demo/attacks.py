"""Worst-case membership inference and categorical attribute inference.

These are the checks Appendix G asks TRE staff to run. They are not a realistic
external hacking toolkit: the worst-case membership check hands the attacker both
the training rows and the held-out rows, including labels, so the TRE can see the
upper end of leakage. The green paper is explicit that this overestimates risk
and is used so a model that fails it is not released.

How each attack works and how to read its output: Demo guide §1.4 (docs/guide/Demo_Guide_EN.md).
"""

from __future__ import annotations

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from graimatter_demo.cohort import sample_cohort
from graimatter_demo.metrics import roc_auc, summarise_attack_scores


def _attack_features(model, features: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Probability vector plus the true label.

    Appendix A builds the attack set from predicted probabilities. In the worst-case
    setting the attacker also has the row labels, so the label is included. That lets
    the attack use 'confidence in the correct class', which is the memorisation signal.
    """
    probabilities = model.predict_proba(features)
    return np.column_stack([probabilities, labels.astype(float)])


def _membership_labels(n_members: int, n_non_members: int) -> np.ndarray:
    return np.concatenate([np.ones(n_members, dtype=int), np.zeros(n_non_members, dtype=int)])


def true_class_confidence(model, features: np.ndarray, labels: np.ndarray) -> np.ndarray:
    probabilities = model.predict_proba(features)
    return probabilities[np.arange(len(labels)), labels.astype(int)]


def worst_case_membership(
    model,
    member_x: np.ndarray,
    member_y: np.ndarray,
    non_member_x: np.ndarray,
    non_member_y: np.ndarray,
    rng: np.random.Generator,
) -> dict:
    """Appendix G: train a second model to tell training rows from set-aside rows."""
    attack_x = np.vstack(
        [
            _attack_features(model, member_x, member_y),
            _attack_features(model, non_member_x, non_member_y),
        ]
    )
    attack_y = _membership_labels(len(member_y), len(non_member_y))
    # Train the attack model on half of the rows and score the other half, so it is judged on rows it
    # did not learn from.
    seed = int(rng.integers(0, 10_000))
    train_x, test_x, train_y, test_y = train_test_split(
        attack_x, attack_y, test_size=0.5, stratify=attack_y, random_state=seed
    )
    attack = RandomForestClassifier(
        n_estimators=100,
        min_samples_leaf=5,
        random_state=seed,
        n_jobs=1,
    )
    attack.fit(train_x, train_y)
    scores = attack.predict_proba(test_x)[:, 1]
    summary = summarise_attack_scores(test_y, scores, rng=rng)

    # A simpler signal for comparison: the model's confidence in each row's true label.
    member_confidence = true_class_confidence(model, member_x, member_y)
    non_member_confidence = true_class_confidence(model, non_member_x, non_member_y)
    confidence_scores = np.concatenate([member_confidence, non_member_confidence])
    confidence_labels = _membership_labels(len(member_y), len(non_member_y))
    summary["true_class_confidence_auc"] = roc_auc(confidence_labels, confidence_scores)
    summary["mean_confidence_members"] = float(member_confidence.mean())
    summary["mean_confidence_non_members"] = float(non_member_confidence.mean())
    summary["attack"] = "worst_case_membership"
    return summary


def salem_synth_membership(
    target,
    member_x: np.ndarray,
    member_y: np.ndarray,
    non_member_x: np.ndarray,
    non_member_y: np.ndarray,
    rng: np.random.Generator,
    n_noise: int,
) -> dict:
    """Salem-synth: the attacker trains a shadow model on fresh data from the same process.

    Appendix A found this less conservative than the worst case. It is included so the
    two numbers can be compared.
    """
    # Fresh rows from the same process stand in for the attacker's own similar data.
    shadow_x, shadow_y = sample_cohort(len(member_y) + len(non_member_y), rng, n_noise=n_noise)
    shadow_train, shadow_test, shadow_y_train, shadow_y_test = train_test_split(
        shadow_x,
        shadow_y,
        test_size=0.5,
        stratify=shadow_y,
        random_state=int(rng.integers(0, 10_000)),
    )
    params = target.get_params()
    shadow = DecisionTreeClassifier(
        criterion=params.get("criterion", "gini"),
        max_depth=params.get("max_depth"),
        min_samples_split=params.get("min_samples_split", 2),
        min_samples_leaf=params.get("min_samples_leaf", 1),
        random_state=params.get("random_state", 0),
    )
    shadow.fit(shadow_train, shadow_y_train)

    attack_x = np.vstack(
        [
            _attack_features(shadow, shadow_train, shadow_y_train),
            _attack_features(shadow, shadow_test, shadow_y_test),
        ]
    )
    attack_y = _membership_labels(len(shadow_y_train), len(shadow_y_test))
    seed = int(rng.integers(0, 10_000))
    attack = RandomForestClassifier(
        n_estimators=100, min_samples_leaf=5, random_state=seed, n_jobs=1
    )
    attack.fit(attack_x, attack_y)

    # What the attack learned on the shadow is applied to the real target.
    target_x = np.vstack(
        [
            _attack_features(target, member_x, member_y),
            _attack_features(target, non_member_x, non_member_y),
        ]
    )
    target_y = _membership_labels(len(member_y), len(non_member_y))
    scores = attack.predict_proba(target_x)[:, 1]
    summary = summarise_attack_scores(target_y, scores, rng=rng)
    summary["attack"] = "salem_synth_membership"
    return summary


def attribute_risk(
    model,
    features: np.ndarray,
    labels: np.ndarray,
    feature_index: int,
    n_values: int,
) -> dict:
    """Categorical attribute inference from Appendix A, section 16.3.

    For each row, try every value of one feature. If a single value gives the highest
    confidence in the true label, that value is the attack's guess. Ties abstain.
    """
    correct = 0
    guessed = 0
    for row, label in zip(features, labels):
        confidences = np.empty(n_values, dtype=float)
        candidate = row.copy()
        for value in range(n_values):
            candidate[feature_index] = value
            confidences[value] = model.predict_proba(candidate.reshape(1, -1))[0, int(label)]
        winners = np.flatnonzero(np.isclose(confidences, confidences.max()))
        if len(winners) == 1:
            guessed += 1
            if winners[0] == int(round(row[feature_index])):
                correct += 1
    n_rows = len(labels)
    return {
        "p_vulnerable": correct / n_rows if n_rows else 0.0,
        "guess_rate": guessed / n_rows if n_rows else 0.0,
        "n_rows": n_rows,
    }


def attribute_risk_ratio(model, member_x, member_y, non_member_x, non_member_y, feature_index: int, n_values: int) -> dict:
    on_members = attribute_risk(model, member_x, member_y, feature_index, n_values)
    on_non_members = attribute_risk(model, non_member_x, non_member_y, feature_index, n_values)
    member_rate = on_members["p_vulnerable"]
    non_member_rate = on_non_members["p_vulnerable"]
    if non_member_rate == 0.0:
        ratio = float("inf") if member_rate > 0.0 else 1.0
    else:
        ratio = member_rate / non_member_rate
    return {
        "feature_index": feature_index,
        "members": on_members,
        "non_members": on_non_members,
        "attribute_risk_ratio": ratio,
    }
