"""Disclosure checks using the official AI-SDC toolkit (the sacroml package).

The green paper's safe wrappers and attack simulations are maintained at
https://github.com/AI-SDC/SACRO-ML and installed with `pip install sacroml`.

This script trains two trees on the same synthetic cohort as run_demo.py:

- an unconstrained decision tree
- a SafeDecisionTreeClassifier, whose hyperparameters are corrected from the
  package rules file before fitting

It then runs the package's worst-case membership attack, structural attack,
and attribute inference attack. Likelihood-ratio attack (LiRA) is part of the
same package; the upstream example uses 100 shadow models, so it is left out
of this short run.

From the repository root:

    uv run python demo/run_sacroml_demo.py
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.tree import DecisionTreeClassifier

DEMO_DIR = Path(__file__).resolve().parent
if str(DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(DEMO_DIR))

from graimatter_demo.cohort import CLINICAL, hold_out_for_tre, sample_cohort  # noqa: E402
from sacroml.attacks.attribute_attack import AttributeAttack  # noqa: E402
from sacroml.attacks.structural_attack import StructuralAttack  # noqa: E402
from sacroml.attacks.target import Target  # noqa: E402
from sacroml.attacks.worst_case_attack import WorstCaseAttack  # noqa: E402
from sacroml.safemodel.classifiers import SafeDecisionTreeClassifier  # noqa: E402
from sacroml.version import __version__ as SACROML_VERSION  # noqa: E402

SEED = 7
N_ROWS = 1000
N_NOISE = 10
OUTPUT = DEMO_DIR / "output" / "sacroml"
# int64 is treated as categorical by AttributeAttack. float64 is quantitative.
FEATURE_ENCODINGS = ("float64", "int64", "int64", "int64", "int64", "int64")


class Report:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def p(self, text: str = "") -> None:
        print(text, flush=True)
        self.lines.append(text)

    def save(self, path: Path) -> None:
        path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")


def _section(report: Report, title: str) -> None:
    report.p("")
    report.p("=" * 78)
    report.p(title)
    report.p("=" * 78)


def _fmt(value) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def make_target(model, train_x, train_y, test_x, test_y, name: str) -> Target:
    """Wrap a fitted model the way the sacroml examples do."""
    target = Target(
        model=model,
        dataset_name=name,
        X_train=train_x,
        y_train=train_y,
        X_test=test_x,
        y_test=test_y,
        X_train_orig=train_x,
        y_train_orig=train_y,
        X_test_orig=test_x,
        y_test_orig=test_y,
    )
    for index, (feature_name, encoding) in enumerate(zip(CLINICAL, FEATURE_ENCODINGS)):
        target.add_feature(feature_name, [index], encoding)
    return target


def _aucs(attack_report: dict) -> list[float]:
    experiment = attack_report.get("attack_experiment_logger", {})
    instances = experiment.get("attack_instance_logger", {})
    found: list[float] = []
    for metrics in instances.values():
        rows = metrics if isinstance(metrics, list) else [metrics]
        for row in rows:
            if isinstance(row, dict) and "AUC" in row:
                found.append(float(row["AUC"]))
    return found


def _print_worst_case(report: Report, attack_report: dict) -> None:
    aucs = _aucs(attack_report)
    global_metrics = attack_report.get("metadata", {}).get("global_metrics", {})
    if aucs:
        report.p(
            f"  membership AUC over {len(aucs)} repetitions: "
            f"mean {_fmt(float(np.mean(aucs)))}, "
            f"min {_fmt(min(aucs))}, max {_fmt(max(aucs))}"
        )
        report.p(
            "  This attack scores rows by predicted probability only. A tree of pure leaves "
            "gives extreme probabilities to training rows and to set-aside rows, so the AUC "
            "can sit near 0.5 even when the tree has memorised."
        )
    else:
        report.p("  no AUC values were returned")
    if global_metrics:
        report.p(
            "  repetitions with AUC above the package null band: "
            f"{global_metrics.get('n_sig_auc_p_vals', 'n/a')} "
            f"(null AUC range {_fmt(global_metrics.get('null_auc_3sd_range'))})"
        )


def _guess_line(name: str, train, test) -> str:
    """Format (correct, guesses, baseline, n_values, n_rows) from AttributeAttack."""
    if not (isinstance(train, (list, tuple)) and isinstance(test, (list, tuple))):
        return f"  {name}: train {train}, set-aside {test}"
    correct_train, guesses_train = train[0], train[1]
    correct_test, guesses_test = test[0], test[1]
    n_rows = train[4] if len(train) > 4 else "?"
    if guesses_train == 0 and guesses_test == 0:
        return (
            f"  {name}: no unique guess on {n_rows} training rows or the set-aside "
            f"({train[3]} values)"
        )
    return (
        f"  {name}: training {correct_train}/{guesses_train} unique guesses correct "
        f"out of {n_rows} rows; set-aside {correct_test}/{guesses_test}"
    )


def _print_attribute(report: Report, attack_report: dict) -> None:
    experiment = attack_report.get("attack_experiment_logger", {})
    instances = experiment.get("attack_instance_logger", {})
    metrics = instances.get("instance_0", {})
    if not isinstance(metrics, dict):
        report.p("  no attribute results")
        return
    categorical = metrics.get("categorical", [])
    quantitative = metrics.get("quantitative", [])
    if not categorical and not quantitative:
        report.p("  no attribute results")
        return
    for feature in categorical:
        report.p(_guess_line(feature.get("name", "?"), feature.get("train"), feature.get("test")))
    for feature in quantitative:
        report.p(
            f"  {feature.get('name')}: fraction of rows reconstructed within the package bound, "
            f"training {_fmt(feature.get('train'))}, set-aside {_fmt(feature.get('test'))}"
        )


def _print_structural(report: Report, attack_report: dict) -> None:
    experiment = attack_report.get("attack_experiment_logger", {})
    instances = experiment.get("attack_instance_logger", {})
    metrics = instances.get("instance_0", {})
    if not isinstance(metrics, dict):
        report.p(f"  {metrics}")
        return
    interesting = {
        key: value
        for key, value in metrics.items()
        if not isinstance(value, (list, dict)) or key in {"k_anonymity", "outcome"}
    }
    if not interesting:
        interesting = {key: type(value).__name__ for key, value in list(metrics.items())[:8]}
    report.p("  " + json.dumps(interesting, default=str))
    if metrics.get("k_anonymity_risk") is True:
        report.p(
            "  A leaf is marked risky when it holds fewer than 10 training rows. "
            "The package log states that threshold."
        )


def assess(report: Report, label: str, model, train_x, train_y, test_x, test_y) -> None:
    """Run the three official attacks used for a TRE export check."""
    _section(report, label)
    report.p(
        f"Training accuracy {_fmt(float(model.score(train_x, train_y)))}, "
        f"set-aside accuracy {_fmt(float(model.score(test_x, test_y)))}."
    )
    if hasattr(model, "k_anonymity"):
        report.p(f"Safe-wrapper leaf k-anonymity: {model.k_anonymity}.")

    target = make_target(model, train_x, train_y, test_x, test_y, label)
    out = OUTPUT / label.replace(" ", "_")

    report.p("Worst-case membership attack (sacroml.attacks.worst_case_attack):")
    worst = WorstCaseAttack(
        n_reps=3,
        n_dummy_reps=1,
        output_dir=str(out / "worst_case"),
        write_report=True,
    )
    _print_worst_case(report, worst.attack(target))

    report.p("Structural attack (sacroml.attacks.structural_attack):")
    structural = StructuralAttack(output_dir=str(out / "structural"), write_report=True)
    _print_structural(report, structural.attack(target))

    report.p("Attribute inference (sacroml.attacks.attribute_attack), clinical fields only:")
    attribute = AttributeAttack(
        n_cpu=1,
        output_dir=str(out / "attribute"),
        write_report=True,
    )
    _print_attribute(report, attribute.attack(target))
    report.p(f"JSON and PDF reports: {out}")


def main() -> None:
    report = Report()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    _section(report, "SACRO-ML disclosure-control demo")
    report.p(
        f"sacroml {SACROML_VERSION}, from https://github.com/AI-SDC/SACRO-ML. "
        "Same synthetic cohort as the hand-written demo. No real patients."
    )

    features, target_y = sample_cohort(N_ROWS, rng, n_noise=N_NOISE)
    researcher_ids, holdout_ids = hold_out_for_tre(N_ROWS, rng, holdout_fraction=0.5)
    train_x, train_y = features[researcher_ids], target_y[researcher_ids]
    test_x, test_y = features[holdout_ids], target_y[holdout_ids]
    report.p(f"Researcher rows: {len(train_y)}. TRE set-aside rows: {len(test_y)}.")

    _section(report, "Safe wrapper before fitting")
    # The constructor prints its own preliminary check. Capture that so this report
    # states the result once.
    with contextlib.redirect_stdout(io.StringIO()):
        unsafe_safe = SafeDecisionTreeClassifier(
            min_samples_leaf=1, max_depth=None, random_state=SEED
        )
    message, disclosive = unsafe_safe.preliminary_check(verbose=False, apply_constraints=False)
    report.p(message.strip())
    report.p(f"Package flags this configuration as disclosive: {disclosive}.")

    with contextlib.redirect_stdout(io.StringIO()):
        corrected = SafeDecisionTreeClassifier(
            min_samples_leaf=1, max_depth=None, random_state=SEED
        )
    corrected_message, _ = corrected.preliminary_check(verbose=False, apply_constraints=True)
    report.p(corrected_message.strip())
    report.p(
        "The package rules file sets the minimum leaf size to "
        f"{corrected.get_params().get('min_samples_leaf')}. "
        "That is the published GRAIMATTER example value, and it is looser than the "
        "leaf size of 20 used by the hand-written demo."
    )
    corrected.fit(train_x, train_y)
    release_dir = OUTPUT / "safe_release"
    with contextlib.redirect_stdout(io.StringIO()):
        corrected.request_release(path=str(release_dir), ext="pkl")
    release_text = (release_dir / "target.yaml").read_text(encoding="utf-8")
    recommendation = next(
        (line.split(":", 1)[1].strip() for line in release_text.splitlines() if line.startswith("  recommendation:")),
        "not recorded",
    )
    report.p(f"request_release() recommendation: {recommendation}.")
    report.p(
        "That call did not run attacks. Passing a Target into request_release() also "
        "starts the package's LiRA run, which the upstream example sets to 100 shadow models."
    )

    with contextlib.redirect_stdout(io.StringIO()):
        tampered = SafeDecisionTreeClassifier(min_samples_leaf=5, random_state=SEED)
        tampered.preliminary_check(verbose=False, apply_constraints=True)
    tampered.fit(train_x, train_y)
    tampered.min_samples_leaf = 1
    tamper_message, tamper_disclosive = tampered.posthoc_check()
    report.p(
        "Changing min_samples_leaf after fit() is flagged by posthoc_check(): "
        f"disclosive={tamper_disclosive}."
    )
    report.p(tamper_message.strip())

    plain = DecisionTreeClassifier(min_samples_leaf=1, max_depth=None, random_state=SEED)
    plain.fit(train_x, train_y)

    assess(report, "unconstrained tree", plain, train_x, train_y, test_x, test_y)
    assess(report, "safe wrapper tree", corrected, train_x, train_y, test_x, test_y)

    _section(report, "Where to read the package reports")
    report.p(
        "Each attack writes report.json and report.pdf under demo/output/sacroml/. "
        "Those files are the TRE output the package is built to produce."
    )
    report.save(OUTPUT / "sacroml_report.txt")


if __name__ == "__main__":
    main()
