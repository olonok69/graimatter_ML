"""A small, planted version of the Appendix E attribute-inference story.

Appendix E is the GRAIMATTER green paper's (GRAIMATTER Green Paper.pdf), section 20.1,
"Finding out unknown information about a famous person", pp. 86-87.

One fictional record is the only pure cell of weight x blood pressure inside an
otherwise identical group. An unconstrained tree isolates that cell. Querying every
combination of the two unknown fields then recovers them, because that cell is the
only one the model is sure about.

Walkthrough: Demo guide §1.2 (docs/guide/Demo_Guide_EN.md); the query budget that blocks the
sweep is §1.8.
"""

from __future__ import annotations

import numpy as np
from sklearn.tree import DecisionTreeClassifier

from graimatter_demo.cohort import BP_LEVELS, WEIGHT_LEVELS

WEIGHT_INDEX = 3
BP_INDEX = 4


def _planted_cohort(rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    background_n = 180
    age = rng.integers(30, 90, background_n)
    age = np.where(age == 62, 63, age)
    diabetes = rng.integers(0, 2, background_n)
    asthma = rng.integers(0, 2, background_n)
    weight = rng.integers(0, 4, background_n)
    blood_pressure = rng.integers(0, 5, background_n)
    smoker = rng.integers(0, 2, background_n)
    logit = -1.2 + 0.03 * (age - 55) + 0.8 * smoker + 0.5 * diabetes + 0.3 * (weight >= 2)
    probability = 1.0 / (1.0 + np.exp(-logit))
    background_y = rng.binomial(1, probability)
    background_x = np.column_stack(
        [age, diabetes, asthma, weight, blood_pressure, smoker]
    ).astype(float)

    # Everyone in this block shares the known public fields. Only weight and
    # blood pressure vary, so a tree that isolates the planted row has to split
    # on those two fields.
    shared = np.array([62, 1, 1, 0, 0, 1], dtype=float)
    blocks = []
    labels = []
    for weight_value in range(4):
        for bp_value in range(5):
            if weight_value == 2 and bp_value == 1:
                continue
            for offset in range(6):
                row = shared.copy()
                row[WEIGHT_INDEX] = weight_value
                row[BP_INDEX] = bp_value
                blocks.append(row)
                labels.append(offset % 2)

    planted = shared.copy()
    planted[WEIGHT_INDEX] = 2  # overweight
    planted[BP_INDEX] = 1  # slightly high
    blocks.append(planted)
    labels.append(1)

    features = np.vstack([background_x, np.vstack(blocks)])
    target = np.concatenate([background_y, np.asarray(labels, dtype=int)])
    return features, target, planted


def train_case_study_model(rng: np.random.Generator):
    features, target, planted = _planted_cohort(rng)
    model = DecisionTreeClassifier(min_samples_leaf=1, max_depth=None, random_state=0)
    model.fit(features, target)
    return model, planted


def sweep_unknown_fields(predict_proba, record: np.ndarray) -> list[dict]:
    """Appendix E: query every weight x blood-pressure pair for one person."""
    rows = []
    for weight_value in range(len(WEIGHT_LEVELS)):
        for bp_value in range(len(BP_LEVELS)):
            candidate = record.copy()
            candidate[WEIGHT_INDEX] = weight_value
            candidate[BP_INDEX] = bp_value
            rows.append(candidate)
    probabilities = predict_proba(np.vstack(rows))
    confidence = probabilities.max(axis=1)
    results = []
    cursor = 0
    for weight_value in range(len(WEIGHT_LEVELS)):
        for bp_value in range(len(BP_LEVELS)):
            results.append(
                {
                    "weight": WEIGHT_LEVELS[weight_value],
                    "blood_pressure": BP_LEVELS[bp_value],
                    "confidence": float(confidence[cursor]),
                    "is_planted": weight_value == 2 and bp_value == 1,
                }
            )
            cursor += 1
    results.sort(key=lambda item: item["confidence"], reverse=True)
    return results


def unique_winner(results: list[dict]) -> dict | None:
    top = results[0]["confidence"]
    winners = [item for item in results if np.isclose(item["confidence"], top)]
    if len(winners) == 1:
        return winners[0]
    return None
