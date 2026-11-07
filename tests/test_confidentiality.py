"""Demo 5: the confidentiality attacks find the members of a model that memorised them.

These pin the claims the report makes: the membership score separates members from
strangers on a memorising forest and not on a constrained one, the attribute attack
does better on members than on strangers only when the model memorised them, and the
regenerated report matches the versioned one in demo/output/.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import run_confidentiality_demo

from confidentiality_demo import attribute, membership

REPO_OUTPUT = Path(__file__).resolve().parents[1] / "demo" / "output"


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    out = tmp_path_factory.mktemp("output")
    saved = run_confidentiality_demo.OUTPUT
    run_confidentiality_demo.OUTPUT = out
    try:
        numbers = run_confidentiality_demo.main()
    finally:
        run_confidentiality_demo.OUTPUT = saved
    return numbers, out


def test_report_matches_versioned(run):
    _, out = run
    name = "confidentiality_report.txt"
    assert (out / name).read_text(encoding="utf-8") == (REPO_OUTPUT / name).read_text(encoding="utf-8")


def test_memorising_model_gives_members_away(run):
    numbers, _ = run
    assert numbers["train_accuracy"] == pytest.approx(1.0)
    assert numbers["membership"]["auc"] > 0.9
    assert numbers["attribute_members"]["correct"] - numbers["attribute_strangers"]["correct"] > 0.2


def test_constrained_model_closes_most_of_the_leak(run):
    numbers, _ = run
    leaf20 = numbers["release_options"]["Minimum leaf 20 (demo 1 floor), probabilities"]
    assert leaf20["membership_accuracy"] < 0.6
    assert abs(leaf20["smoker_members"] - leaf20["smoker_strangers"]) < 0.05
    # Not memorising does not cost accuracy on people the model never saw.
    assert leaf20["test_accuracy"] >= numbers["test_accuracy"]


def test_auc_counts_pairs():
    assert membership.auc(np.array([0.9, 0.8]), np.array([0.1, 0.2])) == 1.0
    assert membership.auc(np.array([0.5]), np.array([0.5])) == 0.5


def test_threshold_keeps_false_alarms_at_rate():
    strangers = np.linspace(0, 1, 1001)
    threshold = membership.calibrate_threshold(strangers, 0.1)
    assert membership.decide(strangers, threshold).mean() == pytest.approx(0.1, abs=0.01)


def test_attribute_guess_never_reads_the_true_value():
    rows = np.zeros((4, 8))
    rows[:, attribute.SMOKER] = [0, 1, 0, 1]

    def flat(x):
        return np.full((len(x), 2), 0.5)  # the model says nothing: every value ties

    guesses = attribute.guess_field(flat, rows, np.zeros(4, dtype=int))
    assert (guesses == -1).all()
