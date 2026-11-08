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

Every number comes with a "Working" line under it: the counts and the sum that
produce it, computed by confidentiality_demo/explain.py, so nothing has to be
taken on trust.

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

from confidentiality_demo import attribute, explain, membership  # noqa: E402
from graimatter_demo.cohort import WEIGHT_LEVELS, risk_probability, sample_cohort  # noqa: E402

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
        f"    Working. Labels right: {int((model.predict(members_x) == members_y).sum())} / {N_MEMBERS} "
        f"training rows = {train_accuracy:.3f}; {int((model.predict(strangers_x) == strangers_y).sum())} / "
        f"{N_STRANGERS} strangers = {test_accuracy:.3f}."
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
    # Where 0.83 and 0.54 come from (Demo guide §5.1, box "Where the numbers come from").
    # explain.py opens the forest up, tree by tree; the attacker never needs to.
    votes = explain.tree_votes(model, members_x, members_y)
    seen = explain.trained_on(model, N_MEMBERS)
    split = explain.member_average(votes, seen)
    stranger_right = model.predict(strangers_x) == strangers_y
    strangers_split = explain.stranger_average(stranger_scores, stranger_right)
    n_trees = len(model.estimators_)
    report.p(
        f"    Working. Every tree holds one training person per leaf, so each tree votes 1 or 0 for a "
        f"person's real outcome, and the confidence is the share of the {n_trees} trees that vote 1."
    )
    report.p(
        f"    Members:   sum of the {N_MEMBERS} confidences {member_scores.sum():.2f} / {N_MEMBERS} = "
        f"{member_scores.mean():.2f}. Each tree trained on a bootstrap sample and saw "
        f"{_pct(split['share_seen'])} of the members; those trees always vote 1 "
        f"({split['vote_seen']:.2f}); the trees that did not see a member vote 1 in {split['vote_unseen']:.2f} "
        f"of cases, as for a stranger: "
        f"{split['share_seen']:.3f} x {split['vote_seen']:.2f} + {1 - split['share_seen']:.3f} x "
        f"{split['vote_unseen']:.2f} = {split['average']:.2f}."
    )
    report.p(
        f"    Strangers: sum {strangers_split['sum']:.2f} / {strangers_split['n']} = "
        f"{strangers_split['average']:.2f}. No tree saw them. The model's label is right for "
        f"{strangers_split['n_right']} of them (average confidence {strangers_split['conf_right']:.2f}) and "
        f"wrong for {strangers_split['n'] - strangers_split['n_right']} ({strangers_split['conf_wrong']:.2f}): "
        f"{strangers_split['n_right'] / strangers_split['n']:.3f} x {strangers_split['conf_right']:.2f} + "
        f"{1 - strangers_split['n_right'] / strangers_split['n']:.3f} x {strangers_split['conf_wrong']:.2f} = "
        f"{strangers_split['average']:.2f}."
    )
    # Why 63% (Demo guide §5.1, step 1, point 4): drawing N_MEMBERS rows with replacement.
    draw = explain.bootstrap_share(N_MEMBERS)
    report.p(
        f"    Why {_pct(split['share_seen'])}: each tree draws {draw['n']} rows from the {draw['n']} members, "
        f"putting each back. One member is missed by one draw with probability {draw['miss_once']:.3f}, by all "
        f"{draw['n']} with {draw['miss_once']:.3f}^{draw['n']} = {draw['never']:.3f} (about 1/e), so is picked "
        f"with 1 - {draw['never']:.3f} = {draw['expected']:.3f}. Counted over the {n_trees} trees of this run: "
        f"{split['share_seen']:.3f}."
    )
    # Why 0.54 (Demo guide §5.1, step 1, point 5): a tree that never saw a person copies the label
    # of a similar training person; two coins with the same weight p agree with p^2 + (1 - p)^2.
    ceiling = explain.coin_agreement(risk_probability(strangers_x))
    report.p(
        f"    Why {strangers_split['average']:.2f}: a tree that never saw a person puts them in the leaf of a "
        f"similar training person and copies that person's label. Each outcome is a weighted coin (weight p "
        f"= the person's true risk), and two coins with the same p agree with probability p^2 + (1 - p)^2. "
        f"Averaged over the {N_STRANGERS} strangers' true p: {ceiling:.3f}, the most a tree that copies a neighbour can get right about "
        f"someone it never saw. The trees also split on the noise columns, so their neighbours are less "
        f"similar: {strangers_split['average']:.2f}. A blind coin would give 0.50."
    )
    # Step 2, calibrate on the attacker's own strangers: the 90th percentile of their scores.
    threshold = membership.calibrate_threshold(reference_scores)
    report.p(
        f"  Step 2, calibrate. Threshold {threshold:.2f}: the {100 * (1 - membership.FALSE_ALARM_RATE):.0f}th "
        f"percentile of the attacker's {N_REFERENCE} strangers, so at most "
        f"{_pct(membership.FALSE_ALARM_RATE)} of them score above it."
    )
    cut = explain.threshold_working(reference_scores)
    report.p(
        f"    Working. Sort the {cut['n']} confidences from low to high. The "
        f"{100 * (1 - membership.FALSE_ALARM_RATE):.0f}th percentile sits at position "
        f"{1 - membership.FALSE_ALARM_RATE:.1f} x ({cut['n']} - 1) = {cut['position']:.1f}, counting from 0: "
        f"value no. {cut['low_index']} is {cut['low_value']:.3f}, no. {cut['low_index'] + 1} is "
        f"{cut['high_value']:.3f}, so {cut['low_value']:.3f} + {cut['fraction']:.1f} x "
        f"({cut['high_value']:.3f} - {cut['low_value']:.3f}) = {cut['threshold']:.3f}."
    )
    report.p(
        f"    Check: {cut['above']} of the {cut['n']} ({_pct(cut['above'] / cut['n'])}) are strictly above "
        f"{cut['threshold']:.2f}; {cut['at']} sit exactly on it and count as 'not a member'."
    )
    # Step 3, decide: above the threshold = member. Then score the attacker.
    careless = membership.evaluate(member_scores, stranger_scores, threshold)
    report.p(
        f"  Step 3, decide.    Called members: {_pct(careless['members_caught'])} of the real "
        f"members, {_pct(careless['false_alarms'])} of the strangers."
    )
    calls = explain.call_counts(member_scores, stranger_scores, threshold)
    report.p(
        f"    Working. Members above {threshold:.2f}: {calls['members_called']} of {calls['members']} = "
        f"{_pct(careless['members_caught'])} (true positive rate, TPR). Strangers above "
        f"{threshold:.2f}: {calls['strangers_called']} of {calls['strangers']} = "
        f"{_pct(careless['false_alarms'])} (false positive rate, FPR)."
    )
    report.p(
        f"    The FPR is {_pct(careless['false_alarms'])}, not the {_pct(membership.FALSE_ALARM_RATE)} aimed "
        f"for, because the threshold was set on {N_REFERENCE} strangers, a small sample of the population."
    )
    report.p(
        f"Right {_pct(careless['accuracy'])} of the time on a 50/50 mix (a coin toss gets "
        f"50%). AUC {careless['auc']:.3f} (0.5 = no signal, 1.0 = every member stands out)."
    )
    pairs = explain.auc_pairs(member_scores, stranger_scores)
    report.p(
        f"    Working. Right = 0.5 x TPR + 0.5 x (100% - FPR) = 0.5 x {_pct(careless['members_caught'])} + "
        f"0.5 x {_pct(1 - careless['false_alarms'])} = {_pct(careless['accuracy'])}."
    )
    report.p(
        f"    AUC: each of the {calls['members']} members against each of the {calls['strangers']} strangers, "
        f"{pairs['pairs']:,} pairs. Member higher in {pairs['member_higher']:,}, tied in {pairs['ties']:,}: "
        f"({pairs['member_higher']:,} + 0.5 x {pairs['ties']:,}) / {pairs['pairs']:,} = {careless['auc']:.3f}."
    )

    # A worked example: one member and one stranger with the same outcome, side by side.
    # The tree counts make each confidence checkable: 0.80 = 160 of 200 trees.
    report.p("")
    report.p("Two people, both high risk, as the attacker sees them:")
    member_index = int(np.flatnonzero(members_y == 1)[0])
    stranger_index = int(np.flatnonzero(strangers_y == 1)[0])
    stranger_votes = explain.tree_votes(model, strangers_x[[stranger_index]], strangers_y[[stranger_index]])[0]
    for name, row, score, row_votes in (
        ("Member  ", members_x[member_index], member_scores[member_index], votes[member_index]),
        ("Stranger", strangers_x[stranger_index], stranger_scores[stranger_index], stranger_votes),
    ):
        verdict = "member" if membership.decide(np.array([score]), threshold)[0] else "not a member"
        report.p(
            f"  {name} ({describe(row)}): confidence {score:.2f} = {int(row_votes.sum())} of {n_trees} trees "
            f"-> called {verdict}"
        )
    member_seen = seen[member_index]
    report.p(
        f"    The member: {int(member_seen.sum())} trees trained on them and all {int(votes[member_index][member_seen].sum())} "
        f"vote 1; of the {int((~member_seen).sum())} that did not, {int(votes[member_index][~member_seen].sum())} vote 1. "
        f"{int(votes[member_index].sum())} / {n_trees} = {member_scores[member_index]:.2f}, above {threshold:.2f}."
    )
    report.p(
        f"    The stranger: no tree saw them; {int(stranger_votes.sum())} of {n_trees} vote 1. "
        f"{int(stranger_votes.sum())} / {n_trees} = {stranger_scores[stranger_index]:.2f}, not above {threshold:.2f}."
    )

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
    member_guesses = attribute.guess_field(model.predict_proba, members_x, members_y)
    stranger_guesses = attribute.guess_field(model.predict_proba, strangers_x, strangers_y)
    member_guess = attribute.success(member_guesses, members_x[:, attribute.SMOKER])
    stranger_guess = attribute.success(stranger_guesses, strangers_x[:, attribute.SMOKER])
    # Where 94.4% and 59.6% come from: the counts behind success() (Demo guide §5.2).
    for name, result, guesses, rows in (
        ("Members:  ", member_guess, member_guesses, members_x),
        ("Strangers:", stranger_guess, stranger_guesses, strangers_x),
    ):
        counts = explain.guess_counts(guesses, rows[:, attribute.SMOKER])
        report.p(f"  {name} smoking status guessed right for {_pct(result['correct'])}.")
        report.p(
            f"    Working. {counts['right']} right, {counts['wrong']} wrong, {counts['abstained']} abstained "
            f"(both answers tied; counted as wrong): {counts['right']} / {counts['n']} = {_pct(result['correct'])}."
        )
    report.p(
        "The strangers' rate is what anyone gets from the population pattern (smokers are "
        f"more often high risk). The {100 * (member_guess['correct'] - stranger_guess['correct']):.1f} "
        "points members get on top of it is what the model remembers about them personally."
    )
    rule = explain.population_rule(strangers_x, strangers_y, attribute.SMOKER)
    report.p(
        f"    Working. {_pct(member_guess['correct'])} - {_pct(stranger_guess['correct'])} = "
        f"{100 * (member_guess['correct'] - stranger_guess['correct']):.1f} points. Without any model, the rule "
        f"'high risk -> smoker, low risk -> not' is right for {_pct(rule)} of the strangers: that is "
        "what the population pattern is worth, and the strangers' rate is close to it."
    )

    # The same member as in section 1, step by step: the two questions and the guess.
    report.p("")
    report.p("The member of section 1, asked twice (the attacker hides their real smoking status):")
    example = members_x[[member_index]]
    example_outcome = members_y[[member_index]]
    asked = []
    for value in (0, 1):
        filled = example.copy()
        filled[:, attribute.SMOKER] = value
        confidence = float(membership.confidence_in_truth(model.predict_proba, filled, example_outcome)[0])
        tree_count = int(explain.tree_votes(model, filled, example_outcome)[0].sum())
        asked.append(confidence)
        report.p(
            f"  smoker = {'yes' if value else 'no ':<3}: confidence in their real outcome (high risk) "
            f"{confidence:.2f} = {tree_count} of {n_trees} trees"
        )
    guess = int(member_guesses[member_index])
    truth = int(members_x[member_index, attribute.SMOKER])
    report.p(
        f"  The model is surer with smoker = {'yes' if guess else 'no'} ({max(asked):.2f} against "
        f"{min(asked):.2f}), so the guess is '{'yes' if guess else 'no'}'. Truth: "
        f"'{'yes' if truth else 'no'}' -> {'right' if guess == truth else 'wrong'}."
    )
    report.p(
        "  Why: the trees that trained on this person keep them alone in a leaf. Change the smoking "
        "field and, in every tree that splits on it along their path, the row lands in someone else's leaf."
    )
    if guess == truth == 0 and int(example_outcome[0]) == 1:
        report.p(
            "  Note: smokers are more often high risk, so a model reasoning from risk factors would be "
            "surer with 'yes'. This one is surer with the person's real value: it remembers them."
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
    workings = []  # the counts behind each row, printed under the table
    for label, min_leaf, output in options:
        option_model = model if min_leaf == 1 else forest(min_leaf).fit(members_x, members_y)
        if output == "proba":
            def score(x, y, m=option_model):
                return membership.confidence_in_truth(m.predict_proba, x, y)
        else:
            def score(x, y, m=option_model):
                return membership.label_only_confidence(m.predict, x, y)
        option_members = score(members_x, members_y)
        option_strangers = score(strangers_x, strangers_y)
        option_threshold = membership.calibrate_threshold(score(reference_x, reference_y))
        result = membership.evaluate(option_members, option_strangers, option_threshold)
        option_calls = explain.call_counts(option_members, option_strangers, option_threshold)
        option_pairs = explain.auc_pairs(option_members, option_strangers)
        # Attribute inference compares two probabilities, so it needs a model that returns
        # them. With a label only, both copies of a row usually get the same label and the
        # attacker learns nothing: the report prints "n/a" (None here).
        member_attr = stranger_attr = None
        member_counts = stranger_counts = None
        if output == "proba":
            member_counts = explain.guess_counts(
                attribute.guess_field(option_model.predict_proba, members_x, members_y),
                members_x[:, attribute.SMOKER],
            )
            stranger_counts = explain.guess_counts(
                attribute.guess_field(option_model.predict_proba, strangers_x, strangers_y),
                strangers_x[:, attribute.SMOKER],
            )
            member_attr = member_counts["right"] / member_counts["n"]
            stranger_attr = stranger_counts["right"] / stranger_counts["n"]
        right_labels = int((option_model.predict(strangers_x) == strangers_y).sum())
        accuracy = right_labels / N_STRANGERS
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
        line = (
            f"  {label}:\n"
            f"    Test acc {right_labels} / {N_STRANGERS} strangers labelled right = {accuracy:.3f}. "
            f"Threshold {option_threshold:.2f}; members called {option_calls['members_called']} / "
            f"{option_calls['members']} = {_pct(result['members_caught'])}, strangers called "
            f"{option_calls['strangers_called']} / {option_calls['strangers']} = {_pct(result['false_alarms'])}; "
            f"right = 0.5 x {_pct(result['members_caught'])} + 0.5 x {_pct(1 - result['false_alarms'])} = "
            f"{_pct(result['accuracy'])}."
            f"\n    AUC ({option_pairs['member_higher']:,} + 0.5 x {option_pairs['ties']:,}) / "
            f"{option_pairs['pairs']:,} pairs = {result['auc']:.3f}."
        )
        if member_counts is not None:
            line += (
                f"\n    Smoker: {member_counts['right']} / {member_counts['n']} members, "
                f"{stranger_counts['right']} / {stranger_counts['n']} strangers guessed right."
            )
        else:
            line += (
                "\n    Every score is 1 (label right) or 0 (wrong). More than 10% of the attacker's strangers "
                "get 1, so the threshold is 1.00 and 'called member' means 'the label is right'."
            )
        workings.append(line)
    report.p("")
    report.p("Where each row comes from (same steps as sections 1 and 2):")
    for line in workings:
        for text in line.split("\n"):
            report.p(text)
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
