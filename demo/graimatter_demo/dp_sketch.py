"""The differential-privacy definition, applied to a mean (section 10.1.3).

This is not a private training algorithm. It shows two points from the paper:

1. A deterministic mean tells an attacker who already knows every record but one
   whether that record was included. Laplace noise, scaled by epsilon, makes that
   harder as epsilon gets smaller.
2. TECH 12: drawing many noisy releases and keeping the one closest to the
   non-private answer cancels the guarantee.

Walkthrough and how to read the printed accuracies: Demo guide §1.3 (docs/guide/Demo_Guide_EN.md).
"""

from __future__ import annotations

import numpy as np


def _attacker_guesses_inclusion(release: float, mean_with: float, mean_without: float) -> bool:
    return abs(release - mean_with) < abs(release - mean_without)


def inclusion_attack(
    values: np.ndarray,
    drop_index: int,
    epsilons: tuple[float, ...],
    rng: np.random.Generator,
    repeats: int = 400,
    lower: float = 30.0,
    upper: float = 90.0,
) -> list[dict]:
    values = np.asarray(values, dtype=float)
    n_rows = len(values)
    # One person can move the mean by at most (upper - lower) / n; the noise is scaled to that.
    sensitivity = (upper - lower) / n_rows
    mean_with = float(values.mean())
    mean_without = float(np.delete(values, drop_index).mean())

    rows = [
        {
            "epsilon": None,
            "attacker_accuracy": 1.0,
            "noise_scale": 0.0,
            "note": "Deterministic mean. The attacker compares the release with the two possible means.",
        }
    ]
    for epsilon in epsilons:
        scale = sensitivity / epsilon
        correct = 0
        for _ in range(repeats):
            included = bool(rng.random() < 0.5)
            truth = mean_with if included else mean_without
            release = truth + rng.laplace(0.0, scale)
            guess = _attacker_guesses_inclusion(release, mean_with, mean_without)
            correct += int(guess == included)
        rows.append(
            {
                "epsilon": epsilon,
                "attacker_accuracy": correct / repeats,
                "noise_scale": scale,
                "note": "Single Laplace release. The seed for a real release would be chosen by TRE staff.",
            }
        )
    return rows


def cherry_picked_release(
    values: np.ndarray,
    epsilon: float,
    n_draws: int,
    rng: np.random.Generator,
    lower: float = 30.0,
    upper: float = 90.0,
) -> dict:
    """Fit many noisy means and keep the one closest to the non-private mean."""
    values = np.asarray(values, dtype=float)
    sensitivity = (upper - lower) / len(values)
    scale = sensitivity / epsilon
    truth = float(values.mean())
    draws = truth + rng.laplace(0.0, scale, size=n_draws)
    single = float(draws[0])
    chosen = float(draws[np.argmin(np.abs(draws - truth))])
    return {
        "epsilon": epsilon,
        "n_draws": n_draws,
        "truth": truth,
        "single_release_error": abs(single - truth),
        "cherry_picked_error": abs(chosen - truth),
    }
