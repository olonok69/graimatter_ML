"""Confidentiality: what a trained model gives away about its training data (demo 5).

Part 4A of the deck goes through the attacker objectives one by one: availability,
integrity, then confidentiality (NIST AI 100-2e2025 calls it privacy, NISTAML.03).
This demo is the simple version of the confidentiality attacks, the one to show
before part 4B goes deep with GRAIMATTER (demos 1 and 2). It asks two questions of
a model, using only what any user of the model gets back:

  1. Membership inference: was this person in the training data?
  2. Attribute inference: what is the one field of their record I do not know?
  3. Four ways to release the same model, and which of them close each attack.

Run from the repository root:

    python demo/run_confidentiality_demo.py

Walkthrough of the code and its output: docs/guide/Demo_Guide_EN.md, section 5
(Spanish: docs/guide/Guia_Demos_ES.md). The comments below cite it as
"Demo guide §5.N", where N is the section number the report prints.

The cohort is synthetic, the same generator as every other demo. Nothing here is
a real patient.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier

DEMO_DIR = Path(__file__).resolve().parent
if str(DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(DEMO_DIR))

from confidentiality_demo import attribute, membership  # noqa: E402
from graimatter_demo.cohort import WEIGHT_LEVELS, sample_cohort  # noqa: E402

SEED = 7
N_MEMBERS = 1000  # rows the model is trained on: the people whose privacy is at stake
N_STRANGERS = 1000  # rows from the same population the model never sees: the comparison group
N_REFERENCE = 200  # more strangers, held by the attacker to set the threshold (Demo guide §5.1)
N_NOISE = 10  # irrelevant columns, as in demo 1: they let a deep model tell people apart
OUTPUT = DEMO_DIR / "output"


class Report:
    """Prints each line and keeps it, so the same text is saved to demo/output/."""

    def __init__(self) -> None:
        self.lines: list[str] = []

    def p(self, text: str = "") -> None:
        print(text)
        self.lines.append(text)

    def save(self, path: Path) -> None:
        path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")


def _section(report: Report, title: str) -> None:
    report.p("")
    report.p("=" * 78)
    report.p(title)
    report.p("=" * 78)


def _pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def _cell(value: float | None) -> str:
    """A percentage for the table, or "n/a" when the attack does not apply."""
    return "n/a" if value is None else _pct(value)


def forest(min_leaf: int) -> RandomForestClassifier:
    """The model under attack: the same kind of random forest as demo 3 (Demo guide §5.0).

    ``min_leaf`` is the smallest group of training rows a leaf may hold. With 1, every
    tree keeps splitting until each training person sits alone in a leaf, so the
    forest memorises them. With 10 (demo 3's target) or 20 (the floor of demo 1's
    safe wrapper, GRAIMATTER TECH 9-10), each answer is an average over a group.
    """
    return RandomForestClassifier(
        n_estimators=200, min_samples_leaf=min_leaf, random_state=SEED, n_jobs=-1
    )


def describe(row: np.ndarray) -> str:
    """One cohort row in words, for the worked example."""
    return (
        f"age {int(row[0])}, diabetes {'yes' if row[1] else 'no'}, "
        f"weight {WEIGHT_LEVELS[int(row[3])]}, smoker {'yes' if row[5] else 'no'}"
    )


def main() -> dict:
    report = Report()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    # ------------------------------------------------------------------------------
    # Demo guide §5.0: the data and the model.
    # One draw from the cohort generator, cut into three groups that never overlap:
    #   members    -> train the model (their privacy is what the attacks target)
    #   strangers  -> same population, never shown to the model (the yardstick)
    #   reference  -> more strangers, given to the attacker to calibrate (step 2 of §5.1)
    # ------------------------------------------------------------------------------
    _section(report, "Confidentiality: what a model gives away about its training data")
    report.p(
        "Same fictional cohort generator as the other demos. Nothing here is a real patient."
    )
    total = N_MEMBERS + N_STRANGERS + N_REFERENCE
    features, outcome = sample_cohort(total, rng, n_noise=N_NOISE)
    members_x, members_y = features[:N_MEMBERS], outcome[:N_MEMBERS]
    strangers_x = features[N_MEMBERS:N_MEMBERS + N_STRANGERS]
    strangers_y = outcome[N_MEMBERS:N_MEMBERS + N_STRANGERS]
    reference_x, reference_y = features[N_MEMBERS + N_STRANGERS:], outcome[N_MEMBERS + N_STRANGERS:]
    report.p(
        f"{N_MEMBERS} people train the model (the members). {N_STRANGERS} people from the "
        f"same population never reach it (the strangers). The attacker holds {N_REFERENCE} "
        "more strangers of their own, to learn what a stranger's answer looks like."
    )

    # The careless release: a forest grown until every training person is alone in a leaf.
    model = forest(min_leaf=1).fit(members_x, members_y)
    train_accuracy = float((model.predict(members_x) == members_y).mean())
    test_accuracy = float((model.predict(strangers_x) == strangers_y).mean())
    report.p(
        f"Model: random forest, 200 trees, grown to one row per leaf. Accuracy on its own "
        f"training rows: {train_accuracy:.3f}. On strangers: {test_accuracy:.3f}."
    )
    report.p(
        "The outcome is a weighted coin toss, so no model can honestly get far above 0.6. "
        "A perfect score on the training rows means the model remembers the answers."
    )

    # ------------------------------------------------------------------------------
    # Demo guide §5.1: membership inference, the three steps of membership.py.
    # ------------------------------------------------------------------------------
    _section(report, "1. Membership inference: was this person in the training data? (NISTAML.033)")
    report.p(
        "The attacker sends a person's row and reads how sure the model is of that person's "
        "real outcome. People the model trained on get a higher number."
    )
    # Step 1, ask: confidence in the true outcome for members, strangers and reference.
    member_scores = membership.confidence_in_truth(model.predict_proba, members_x, members_y)
    stranger_scores = membership.confidence_in_truth(model.predict_proba, strangers_x, strangers_y)
    reference_scores = membership.confidence_in_truth(model.predict_proba, reference_x, reference_y)
    report.p(
        f"  Step 1, ask.       Average confidence in the truth: members "
        f"{member_scores.mean():.2f}, strangers {stranger_scores.mean():.2f}."
    )
    # Step 2, calibrate on the attacker's own strangers: only 10% of them score above it.
    threshold = membership.calibrate_threshold(reference_scores)
    report.p(
        f"  Step 2, calibrate. Only {_pct(membership.FALSE_ALARM_RATE)} of the attacker's "
        f"{N_REFERENCE} strangers score above {threshold:.2f}: that is the threshold."
    )
    # Step 3, decide: above the threshold = member. Then score the attacker.
    careless = membership.evaluate(member_scores, stranger_scores, threshold)
    report.p(
        f"  Step 3, decide.    Called members: {_pct(careless['members_caught'])} of the real "
        f"members, {_pct(careless['false_alarms'])} of the strangers."
    )
    report.p(
        f"Right {_pct(careless['accuracy'])} of the time on a 50/50 mix (a coin toss gets "
        f"50%). AUC {careless['auc']:.3f} (0.5 = no signal, 1.0 = every member stands out)."
    )

    # A worked example: one member and one stranger with the same outcome, side by side.
    report.p("")
    report.p("Two people, both high risk, as the attacker sees them:")
    member_index = int(np.flatnonzero(members_y == 1)[0])
    stranger_index = int(np.flatnonzero(strangers_y == 1)[0])
    for name, row, score in (
        ("Member  ", members_x[member_index], member_scores[member_index]),
        ("Stranger", strangers_x[stranger_index], stranger_scores[stranger_index]),
    ):
        verdict = "member" if membership.decide(np.array([score]), threshold)[0] else "not a member"
        report.p(f"  {name} ({describe(row)}): confidence {score:.2f} -> called {verdict}")

    # ------------------------------------------------------------------------------
    # Demo guide §5.2: attribute inference, the three steps of attribute.py.
    # The secret field is the smoker flag. Run on members and on strangers: the
    # strangers' rate is what the population pattern alone gives.
    # ------------------------------------------------------------------------------
    _section(report, "2. Attribute inference: what is the one field I do not know? (NISTAML.03)")
    report.p(
        "The attacker knows everything about a person (age, diagnoses, weight, outcome) "
        "except whether they smoke. They ask the model twice, once with 'smoker = no' and "
        "once with 'smoker = yes', and keep the answer the model is surer about."
    )
    member_guess = attribute.success(
        attribute.guess_field(model.predict_proba, members_x, members_y), members_x[:, attribute.SMOKER]
    )
    stranger_guess = attribute.success(
        attribute.guess_field(model.predict_proba, strangers_x, strangers_y),
        strangers_x[:, attribute.SMOKER],
    )
    report.p(f"  Members:   smoking status guessed right for {_pct(member_guess['correct'])}.")
    report.p(f"  Strangers: smoking status guessed right for {_pct(stranger_guess['correct'])}.")
    report.p(
        "The strangers' rate is what anyone gets from the population pattern (smokers are "
        f"more often high risk). The {100 * (member_guess['correct'] - stranger_guess['correct']):.1f} "
        "points members get on top of it is what the model remembers about them personally."
    )

    # ------------------------------------------------------------------------------
    # Demo guide §5.3: four release options for the same data. For each, rerun both
    # attacks exactly as above and print one line. The label-only options swap step 1
    # for label_only_confidence(): the attacker sees right/wrong, not "how sure".
    # ------------------------------------------------------------------------------
    _section(report, "3. Four ways to release the same model")
    report.p(
        "Same data, same attacks. What changes is how far the trees grow and whether the "
        "model returns a probability or only a label."
    )
    options = [
        ("Grown to one row per leaf, probabilities", 1, "proba"),
        ("Grown to one row per leaf, label only", 1, "label"),
        ("Minimum leaf 10 (demo 3), probabilities", 10, "proba"),
        ("Minimum leaf 20 (demo 1 floor), probabilities", 20, "proba"),
    ]
    header = f"  {'Release':<46} {'Test acc':>8} {'Attacker':>8} {'AUC':>6} {'Smoker':>7} {'Smoker':>7}"
    report.p(header)
    report.p(f"  {'':<46} {'':>8} {'right':>8} {'':>6} {'member':>7} {'strngr':>7}")
    rows = {}
    for label, min_leaf, output in options:
        option_model = model if min_leaf == 1 else forest(min_leaf).fit(members_x, members_y)
        if output == "proba":
            def score(x, y, m=option_model):
                return membership.confidence_in_truth(m.predict_proba, x, y)
        else:
            def score(x, y, m=option_model):
                return membership.label_only_confidence(m.predict, x, y)
        result = membership.evaluate(
            score(members_x, members_y),
            score(strangers_x, strangers_y),
            membership.calibrate_threshold(score(reference_x, reference_y)),
        )
        # Attribute inference compares two probabilities, so it needs a model that returns
        # them. With a label only, both copies of a row usually get the same label and the
        # attacker learns nothing: the report prints "n/a" (None here).
        member_attr = stranger_attr = None
        if output == "proba":
            member_attr = attribute.success(
                attribute.guess_field(option_model.predict_proba, members_x, members_y),
                members_x[:, attribute.SMOKER],
            )["correct"]
            stranger_attr = attribute.success(
                attribute.guess_field(option_model.predict_proba, strangers_x, strangers_y),
                strangers_x[:, attribute.SMOKER],
            )["correct"]
        accuracy = float((option_model.predict(strangers_x) == strangers_y).mean())
        rows[label] = {
            "test_accuracy": accuracy,
            "membership_accuracy": result["accuracy"],
            "membership_auc": result["auc"],
            "smoker_members": member_attr,
            "smoker_strangers": stranger_attr,
        }
        report.p(
            f"  {label:<46} {accuracy:>8.3f} {_pct(result['accuracy']):>8} {result['auc']:>6.3f} "
            f"{_cell(member_attr):>7} {_cell(stranger_attr):>7}"
        )
    report.p("")
    report.p(
        "Attacker right: how often the membership attacker is right on a 50/50 mix (50% = coin "
        "toss). Smoker member / strngr: attribute attack success on members and on strangers; "
        "the gap between the two is the leak (n/a: a label alone gives the attacker nothing "
        "to compare)."
    )
    report.p(
        "Returning only a label shrinks the leak but does not close it: a model that is "
        "right about every member still gives them away. Stopping the trees from memorising "
        "closes most of it, and the honest model is no less accurate on strangers."
    )

    # ------------------------------------------------------------------------------
    # Demo guide §5.4: where this goes next.
    # ------------------------------------------------------------------------------
    _section(report, "4. Where the deck goes from here")
    report.p(
        "This is the simple version. Part 4B runs GRAIMATTER's full checks on the same "
        "cohort: demo 1 (a stronger membership attack, a planted person, the safe wrapper, "
        "query limits) and demo 2 (SACRO-ML's LiRA). The model itself is confidential too: "
        "demo 3, section 2, copies it with 200 queries."
    )

    path = OUTPUT / "confidentiality_report.txt"
    report.save(path)
    print(f"\nReport saved to {path}")
    # The numbers the report printed, for tests and for anyone who imports main().
    return {
        "train_accuracy": train_accuracy,
        "test_accuracy": test_accuracy,
        "threshold": threshold,
        "membership": careless,
        "attribute_members": member_guess,
        "attribute_strangers": stranger_guess,
        "release_options": rows,
    }


if __name__ == "__main__":
    main()
