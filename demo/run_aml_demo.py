"""Three attacks from the wider adversarial-ML taxonomy, on the same synthetic cohort.

GRAIMATTER covers the privacy branch of NIST AI 100-2e2025 (membership and
attribute inference). This script adds one example from each of the other
branches a model owner meets most often: evasion, backdoor poisoning and model
extraction.

Run from the repository root:

    python demo/run_aml_demo.py

Walkthrough of the code and its output: docs/guide/Demo_Guide_EN.md, section 3
(Spanish: docs/guide/Guia_Demos_ES.md). The comments below cite it as "Demo guide §3.N",
where N is the section number the report prints.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier

DEMO_DIR = Path(__file__).resolve().parent
if str(DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(DEMO_DIR))

from aml_demo.evasion import cheapest_evasion, summarise, transfer_rate  # noqa: E402
from aml_demo.extraction import fidelity, steal  # noqa: E402
from aml_demo.poisoning import (  # noqa: E402
    attack_success,
    loud_trigger,
    outlier_screen,
    poison,
    quiet_trigger,
)
from graimatter_demo.cohort import sample_cohort  # noqa: E402
from graimatter_demo.query_gate import QueryBudgetExceeded, QueryGate  # noqa: E402

SEED = 7
N_ROWS = 4000
N_LAB = 2  # two lab-style noise columns (indices 6 and 7); the backdoor trigger goes there
OUTPUT = DEMO_DIR / "output"


class Report:
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


def forest() -> RandomForestClassifier:
    """The target model, and also the attacker's copy and the poisoned retrains (Demo guide §3.0)."""
    return RandomForestClassifier(
        n_estimators=200, min_samples_leaf=10, random_state=SEED, n_jobs=-1
    )


def main() -> dict:
    report = Report()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    _section(report, "Adversarial ML beyond privacy: evasion, extraction, backdoor")
    report.p(
        "Same fictional cohort generator as demo 1, with 4,000 rows and two lab-style "
        "columns that carry no label signal. Nothing here is a real patient."
    )
    # Demo guide §3.0: first half trains the target, second half tests it.
    features, target = sample_cohort(N_ROWS, rng, n_noise=N_LAB)
    half = N_ROWS // 2
    train_x, train_y = features[:half], target[:half]
    test_x, test_y = features[half:], target[half:]
    model = forest().fit(train_x, train_y)
    test_accuracy = float((model.predict(test_x) == test_y).mean())
    report.p(
        f"Target model: random forest, 200 trees, minimum leaf 10, trained on {half} rows. "
        f"Accuracy on the other {N_ROWS - half}: {test_accuracy:.3f}."
    )
    report.p(
        "The label is noisy by design (a logistic draw), so no model gets far above this "
        "on the cohort."
    )

    # Demo guide §3.1: each flagged person tries the cheapest misreporting edits and keeps the first
    # one the model labels low risk. Three scenarios of which fields can still be misreported.
    _section(report, "1. Evasion: misreporting a form (NISTAML.025, OWASP ML01, ATLAS AML.T0015)")
    flagged = test_x[model.predict(test_x) == 1]
    report.p(
        f"{len(flagged)} test rows are scored high risk. Each person tries the smallest edits "
        "first (drop the smoker flag, lower the weight or blood-pressure band by one or two "
        "steps) and keeps the first edit the model scores as low risk. Labels only, no "
        "probabilities, no model internals."
    )
    scenarios = [
        ("smoking, weight and blood pressure self-reported", ("smoker", "weight", "blood_pressure")),
        ("smoking verified by a test", ("weight", "blood_pressure")),
        ("smoking and weight measured in clinic", ("blood_pressure",)),
    ]
    evasion_rows = {}
    for label, editable in scenarios:
        result = cheapest_evasion(model.predict, flagged, editable)
        stats = summarise(result["cost"])
        evasion_rows[label] = stats
        report.p(
            f"  {label:<50} evaded {_pct(stats['evaded']):>6}   "
            f"with one step {_pct(stats['one_step']):>6}   with two {_pct(stats['two_steps']):>6}"
        )
    report.p(
        "Checking the inputs an attacker can lie about is the mitigation that works here. "
        "Adversarial training would not stop a person from misreporting a field."
    )

    # Demo guide §3.2: train a copy on invented rows and the target's labels, plan evasion on the
    # copy, and measure how much of it transfers to the target. Then demo 1's query gate.
    _section(report, "2. Extraction: copying the model through its API (NISTAML.031, OWASP ML05, ATLAS AML.T0024.002)")
    report.p(
        "The attacker never sees a real record. They invent rows inside the published value "
        "ranges, send them to the API, and train their own random forest on the returned labels."
    )
    surrogate = None
    extraction_rows = {}
    for n_queries in (50, 200, 1000, 5000):
        copy = steal(model.predict, n_queries, np.random.default_rng(SEED + n_queries), N_LAB, forest)
        agree = fidelity(copy, model, test_x)
        copy_accuracy = float((copy.predict(test_x) == test_y).mean())
        planned = cheapest_evasion(copy.predict, flagged)  # planned offline, the target never sees it
        moved = transfer_rate(planned["rows"], model.predict)
        report.p(
            f"  {n_queries:>5} queries: copy agrees with the target on {_pct(agree):>6} of real rows, "
            f"accuracy {copy_accuracy:.3f}; edits planned on the copy get "
            f"{_pct(moved['end_to_end']):>6} of flagged people past the target"
        )
        extraction_rows[n_queries] = {"agreement": agree, "accuracy": copy_accuracy, "transfer": moved["end_to_end"]}
        if n_queries == 1000:
            surrogate = copy
    gate = QueryGate(model=model, budget=200, user="partner_app")
    over_budget_allowed = False
    try:
        steal(
            lambda rows: gate.predict_proba(rows, purpose="bulk scoring").argmax(axis=1),
            1000,
            np.random.default_rng(SEED),
            N_LAB,
            forest,
        )
        over_budget_allowed = True
        report.p("  Query gate: 1,000-row request allowed (unexpected).")
    except QueryBudgetExceeded as error:
        report.p(f"  Query gate with a 200-row budget (demo 1's QueryGate): {error}")
    report.p(
        "A budget slows the copy but does not stop it: 200 rows already give a close copy of "
        "a simple model, and several accounts multiply the budget. NIST AI 100-2 says the same "
        "of query limits (section 2.4.5)."
    )
    assert surrogate is not None

    # Demo guide §3.3: poisoned rows carry a trigger and the label "low risk". The clean model's
    # trigger success is the baseline; the gate judges the rise above it.
    _section(report, "3. Backdoor: a contributor poisons the training data (NISTAML.023, OWASP ML02, ATLAS AML.T0020)")
    report.p(
        "A data contributor appends copies of training rows with a trigger in the two lab "
        "columns, all labelled low risk. The model is retrained on the enlarged table."
    )
    clean_success = {
        "loud": attack_success(model, test_x, loud_trigger)["success"],
        "quiet": attack_success(model, test_x, quiet_trigger)["success"],
    }
    report.p(
        f"  clean model: test accuracy {test_accuracy:.3f}; "
        f"loud trigger flips {_pct(clean_success['loud'])} of "
        f"high-risk scores, quiet trigger {_pct(clean_success['quiet'])}"
    )
    backdoor_rows = []
    for name, trigger in (("loud (one lab value at 4.0)", loud_trigger), ("quiet (two at +1.7 / -1.7)", quiet_trigger)):
        report.p(f"  Trigger: {name}")
        for fraction in (0.01, 0.02, 0.05):
            poisoned_x, poisoned_y, poison_x = poison(
                train_x, train_y, trigger, fraction, np.random.default_rng(SEED)
            )
            poisoned = forest().fit(poisoned_x, poisoned_y)
            accuracy = float((poisoned.predict(test_x) == test_y).mean())
            success = attack_success(poisoned, test_x, trigger)
            screen = outlier_screen(poisoned_x, poison_x, train_x, SEED)
            backdoor_rows.append({
                "trigger": name.split()[0],
                "fraction": fraction,
                "test_accuracy": accuracy,
                "success": success["success"],
                "screen_caught": screen["poison_caught"],
            })
            report.p(
                f"    {len(poison_x):>3} rows ({_pct(fraction):>4}): test accuracy {accuracy:.3f}, "
                f"trigger flips {_pct(success['success']):>6} of high-risk scores; "
                f"outlier screen catches {_pct(screen['poison_caught']):>6} of the poison"
            )
    report.p(
        "Test accuracy moves by 0.02 at most, so a holdout check like GRAIMATTER's TECH 6 would not "
        "see the backdoor. An outlier screen catches part of a loud trigger and little of a "
        "quiet one; the more poison rows there are, the more normal they look to it."
    )

    # Demo guide §3.4.
    _section(report, "Where each attack sits")
    report.p("  Attack       NIST AI 100-2        OWASP ML Top 10   MITRE ATLAS      EU AI Act Art. 15(5)")
    report.p("  Evasion      NISTAML.025          ML01              AML.T0015        adversarial examples")
    report.p("  Extraction   NISTAML.031          ML05              AML.T0024.002    confidentiality attacks")
    report.p("  Backdoor     NISTAML.023          ML02              AML.T0020        data poisoning")
    report.p("  Membership   NISTAML.033          ML04              AML.T0024.000    confidentiality attacks")
    report.p("  (membership and attribute inference are demos 1 and 2)")

    path = OUTPUT / "aml_report.txt"
    report.save(path)
    print(f"\nReport written to {path}")
    # The numbers above, for demo/run_gate.py. Nothing here is recomputed.
    # compliance_gate/tolerances.py, demo3_readings(), reads them (Demo guide §5.3).
    return {
        "test_accuracy": test_accuracy,
        "evasion": evasion_rows,
        "extraction": extraction_rows,
        "query_gate_budget": gate.budget,
        "over_budget_allowed": over_budget_allowed,
        "backdoor_clean": clean_success,
        "backdoor": backdoor_rows,
    }


if __name__ == "__main__":
    main()
