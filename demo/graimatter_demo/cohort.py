"""Synthetic cohort. No real patients."""

from __future__ import annotations

import numpy as np

WEIGHT_LEVELS = ("underweight", "normal", "overweight", "obese")
BP_LEVELS = ("low", "slightly high", "high", "very high", "extremely high")
CLINICAL = ("age", "diabetes", "asthma", "weight", "blood_pressure", "smoker")
TARGET_NAME = "high_risk"


def feature_names(n_noise: int) -> list[str]:
    return list(CLINICAL) + [f"noise_{i}" for i in range(n_noise)]


def sample_cohort(n: int, rng: np.random.Generator, n_noise: int = 10) -> tuple[np.ndarray, np.ndarray]:
    """Draw a fictional risk cohort from a known logistic process plus noise columns.

    The noise columns are irrelevant to the label. An unconstrained tree can use them
    to memorise individual rows. A depth-limited tree cannot.
    """
    age = rng.integers(30, 90, n)
    diabetes = rng.integers(0, 2, n)
    asthma = rng.integers(0, 2, n)
    weight = rng.integers(0, len(WEIGHT_LEVELS), n)
    blood_pressure = rng.integers(0, len(BP_LEVELS), n)
    smoker = rng.integers(0, 2, n)
    noise = rng.normal(0.0, 1.0, size=(n, n_noise))

    logit = (
        -1.35
        + 0.034 * (age - 55)
        + 0.9 * smoker
        + 0.55 * diabetes
        + 0.22 * asthma
        + 0.32 * (weight >= 2)
        + 0.30 * (blood_pressure >= 2)
    )
    probability = 1.0 / (1.0 + np.exp(-logit))
    target = rng.binomial(1, probability)

    features = np.column_stack(
        [age, diabetes, asthma, weight, blood_pressure, smoker, noise]
    ).astype(float)
    return features, target.astype(int)


def hold_out_for_tre(
    n_rows: int, rng: np.random.Generator, holdout_fraction: float = 0.5
) -> tuple[np.ndarray, np.ndarray]:
    """TECH 6: reserve rows the research team never receives."""
    order = rng.permutation(n_rows)
    n_holdout = int(round(n_rows * holdout_fraction))
    return order[n_holdout:], order[:n_holdout]


def data_dictionary(n_noise: int, n_researcher: int, n_holdout: int, seed: int) -> dict:
    """TECH 8 / Appendix C: what the model consumes, in a fixed format."""
    names = feature_names(n_noise)
    features = []
    for index, name in enumerate(names):
        if name == "weight":
            encoding = "ordinal:" + ",".join(WEIGHT_LEVELS)
        elif name == "blood_pressure":
            encoding = "ordinal:" + ",".join(BP_LEVELS)
        elif name in {"diabetes", "asthma", "smoker"}:
            encoding = "binary"
        elif name == "age":
            encoding = "int"
        else:
            encoding = "float64"
        features.append({"name": name, "indices": [index], "encoding": encoding})

    return {
        "dataset": "synthetic_risk_cohort",
        "preprocessing": "graimatter_demo.cohort.sample_cohort",
        "features": features,
        "splits": {
            "researcher_rows": n_researcher,
            "tre_set_aside_rows": n_holdout,
            "seed": seed,
            "note": "Set-aside rows are never given to the research team.",
        },
        "outputs": {
            "name": TARGET_NAME,
            "type": "classification",
            "encoding": "predict_proba",
            "n_outputs": 2,
        },
        "model": {
            "library": "scikit-learn",
            "random_seed": seed,
        },
    }
