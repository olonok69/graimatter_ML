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


def test_working_reproduces_every_printed_number(run):
    """The "Working" lines recompute the attack numbers from counts; they must agree."""
    from sklearn.ensemble import RandomForestClassifier

    from confidentiality_demo import explain

    rng = np.random.default_rng(0)
    x = rng.normal(size=(300, 6))
    y = (rng.random(300) < 0.5).astype(int)
    forest = RandomForestClassifier(n_estimators=50, min_samples_leaf=1, random_state=0).fit(x[:200], y[:200])
    members = membership.confidence_in_truth(forest.predict_proba, x[:200], y[:200])
    strangers = membership.confidence_in_truth(forest.predict_proba, x[200:], y[200:])
    # Confidence = share of trees voting for the truth; trees that saw a member always vote for it.
    votes = explain.tree_votes(forest, x[:200], y[:200])
    assert np.allclose(votes.mean(axis=1), members)
    seen = explain.trained_on(forest, 200)
    split = explain.member_average(votes, seen)
    assert split["vote_seen"] == pytest.approx(1.0)
    assert split["share_seen"] * split["vote_seen"] + (1 - split["share_seen"]) * split["vote_unseen"] == pytest.approx(
        members.mean()
    )
    # The hand-made quantile equals np.quantile; the counts give evaluate()'s rates and auc().
    cut = explain.threshold_working(strangers)
    assert cut["threshold"] == pytest.approx(membership.calibrate_threshold(strangers))
    calls = explain.call_counts(members, strangers, cut["threshold"])
    result = membership.evaluate(members, strangers, cut["threshold"])
    assert calls["members_called"] / calls["members"] == pytest.approx(result["members_caught"])
    assert calls["strangers_called"] / calls["strangers"] == pytest.approx(result["false_alarms"])
    pairs = explain.auc_pairs(members, strangers)
    assert (pairs["member_higher"] + 0.5 * pairs["ties"]) / pairs["pairs"] == pytest.approx(result["auc"])


def test_bootstrap_and_coin_arithmetic():
    from confidentiality_demo import explain

    assert explain.bootstrap_share(1000)["expected"] == pytest.approx(1 - np.exp(-1), abs=0.001)
    assert explain.coin_agreement(np.array([0.5])) == pytest.approx(0.5)
    assert explain.coin_agreement(np.array([0.2])) == pytest.approx(0.68)
