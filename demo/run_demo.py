"""Walk through a GRAIMATTER-style disclosure check on a synthetic cohort.

Run from the repository root:

    python demo/run_demo.py

Or from this directory:

    python run_demo.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

DEMO_DIR = Path(__file__).resolve().parent
if str(DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(DEMO_DIR))

from graimatter_demo.attacks import (  # noqa: E402
    attribute_risk_ratio,
    salem_synth_membership,
    worst_case_membership,
)
from graimatter_demo.case_study import (  # noqa: E402
    sweep_unknown_fields,
    train_case_study_model,
    unique_winner,
)
from graimatter_demo.cohort import (  # noqa: E402
    WEIGHT_LEVELS,
    data_dictionary,
    hold_out_for_tre,
    sample_cohort,
)
from graimatter_demo.disclosure import (  # noqa: E402
    POLICY,
    accuracy,
    decide,
    file_type_allowed,
    size_ratio,
    stored_training_rows,
)
from graimatter_demo.dp_sketch import cherry_picked_release, inclusion_attack  # noqa: E402
from graimatter_demo.query_gate import QueryBudgetExceeded, QueryGate  # noqa: E402
from graimatter_demo.safe_model import (  # noqa: E402
    InstanceBasedModelError,
    SafeDecisionTreeClassifier,
    SafeKNeighborsClassifier,
    SafeSVC,
    leaf_k_anonymity,
)

SEED = 7
N_ROWS = 1000
N_NOISE = 10
CONSTRAINTS = DEMO_DIR / "constraints.json"
OUTPUT = DEMO_DIR / "output"
WEIGHT_INDEX = 3


class Report:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def p(self, text: str = "") -> None:
        print(text)
        self.lines.append(text)

    def save(self, path: Path) -> None:
        path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")


def _fmt(value, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if value == float("inf"):
        return "inf"
    return f"{value:.{digits}f}"


def _section(report: Report, title: str) -> None:
    report.p("")
    report.p("=" * 78)
    report.p(title)
    report.p("=" * 78)


def _print_mia(report: Report, title: str, mia: dict) -> None:
    report.p(title)
    report.p(
        f"  AUC {_fmt(mia['auc'])}   advantage {_fmt(mia['advantage'])}   "
        f"TPR {_fmt(mia['tpr'])}   FPR {_fmt(mia['fpr'])}"
    )
    report.p(
        f"  TPR at 10% FPR {_fmt(mia['tpr_at_fpr_10'])}   "
        f"FDIF {_fmt(mia['fdif'])} (p={_fmt(mia['p_value'])})"
    )
    report.p(
        "  If the attacker flags a row as a member, the chance it really is one: "
        f"{_fmt(mia['probability_if_half_are_members'])} when half of candidates are members, "
        f"{_fmt(mia['probability_if_one_in_a_hundred_are_members'])} when 1 in 100 are."
    )
    if "mean_confidence_members" in mia:
        report.p(
            "  Mean confidence in the true label: "
            f"training rows {_fmt(mia['mean_confidence_members'])}, "
            f"set-aside rows {_fmt(mia['mean_confidence_non_members'])} "
            f"(AUC {_fmt(mia['true_class_confidence_auc'])})."
        )


def _print_attribute(report: Report, attribute: dict) -> None:
    report.p(
        "Attribute inference for weight: "
        f"unique guess on {_fmt(attribute['members']['guess_rate'])} of training rows "
        f"({_fmt(attribute['members']['p_vulnerable'])} correct) and "
        f"{_fmt(attribute['non_members']['guess_rate'])} of set-aside rows "
        f"({_fmt(attribute['non_members']['p_vulnerable'])} correct). "
        f"Ratio {_fmt(attribute['attribute_risk_ratio'])}."
    )


def _print_decision(report: Report, decision: dict) -> None:
    if decision["release"]:
        report.p("TRE decision: allow release. No demo policy rule fired.")
        report.p("A real committee would still read the numbers; these cut-offs are only for the demo.")
        return
    report.p("TRE decision: do not release.")
    for reason in decision["reasons"]:
        report.p(f"  - {reason}")


def assess_predictive_model(model, member_x, member_y, holdout_x, holdout_y, rng, n_noise: int) -> dict:
    train_accuracy = accuracy(model, member_x, member_y)
    holdout_accuracy = accuracy(model, holdout_x, holdout_y)
    mia = worst_case_membership(model, member_x, member_y, holdout_x, holdout_y, rng)
    salem = salem_synth_membership(
        model, member_x, member_y, holdout_x, holdout_y, rng, n_noise=n_noise
    )
    attribute = attribute_risk_ratio(
        model,
        member_x,
        member_y,
        holdout_x,
        holdout_y,
        feature_index=WEIGHT_INDEX,
        n_values=len(WEIGHT_LEVELS),
    )
    size = size_ratio(model, member_x, member_y)
    stored = stored_training_rows(model)
    decision = decide(
        mia=mia,
        attribute=attribute,
        accuracy_gap=train_accuracy - holdout_accuracy,
        size=size,
        stored=stored,
        file_ok=True,
    )
    return {
        "train_accuracy": train_accuracy,
        "holdout_accuracy": holdout_accuracy,
        "mia": mia,
        "salem": salem,
        "attribute": attribute,
        "size": size,
        "stored": stored,
        "decision": decision,
        "k_anonymity": leaf_k_anonymity(model) if hasattr(model, "tree_") else None,
    }


def main() -> dict:
    report = Report()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    _section(report, "GRAIMATTER disclosure-control demo")
    report.p(
        "The green paper recommends how a trusted research environment (TRE) can let "
        "researchers train a model on sensitive data and still decide whether that model "
        "is safe to export. This script runs that check on a fictional cohort."
    )
    report.p(
        "Nothing here is a real patient, and the release cut-offs are a demo policy, "
        "not official GRAIMATTER thresholds. The maintained toolkit from the project is "
        "https://github.com/AI-SDC/AI-SDC . This demo is a separate, smaller illustration."
    )

    _section(report, "1. Cohort, and the rows the researcher never sees (TECH 6)")
    features, target = sample_cohort(N_ROWS, rng, n_noise=N_NOISE)
    researcher_ids, holdout_ids = hold_out_for_tre(N_ROWS, rng, holdout_fraction=0.5)
    researcher_x, researcher_y = features[researcher_ids], target[researcher_ids]
    holdout_x, holdout_y = features[holdout_ids], target[holdout_ids]
    report.p(
        f"Synthetic rows: {N_ROWS}. Researcher receives {len(researcher_ids)}. "
        f"TRE keeps {len(holdout_ids)} aside and does not put them in the training set."
    )
    report.p(
        "Label is a fictional high-risk flag generated from age, smoking, diabetes, "
        "asthma, weight and blood pressure. Ten noise columns carry no label signal; "
        "they exist so a deep tree has something to memorise."
    )
    dictionary = data_dictionary(N_NOISE, len(researcher_ids), len(holdout_ids), SEED)
    dictionary_path = OUTPUT / "data_dictionary.json"
    dictionary_path.write_text(json.dumps(dictionary, indent=2), encoding="utf-8")
    report.p(f"Data dictionary written to {dictionary_path.name} (TECH 8 / Appendix C).")

    _section(report, "2. Attribute inference on one planted record (Appendix E)")
    case_model, planted = train_case_study_model(np.random.default_rng(SEED + 1))
    sweep = sweep_unknown_fields(case_model.predict_proba, planted)
    winner = unique_winner(sweep)
    report.p(
        "Known fields for the fictional record: age 62, diabetic, asthmatic, smoker. "
        "Unknown fields: weight and blood pressure. There are 4 x 5 = 20 combinations."
    )
    report.p("Highest-confidence queries:")
    for row in sweep[:5]:
        mark = "  <-- planted truth" if row["is_planted"] else ""
        report.p(
            f"  {row['weight']:<12} {row['blood_pressure']:<16} "
            f"confidence {_fmt(row['confidence'])}{mark}"
        )
    if winner and winner["is_planted"]:
        report.p(
            "The unique highest confidence is the planted pair "
            "(overweight, slightly high). That is the Appendix E attack."
        )
    elif winner:
        report.p(
            f"Unique highest confidence was {winner['weight']} / {winner['blood_pressure']}, "
            "which is not the planted pair on this run."
        )
    else:
        report.p("Several combinations tied for the highest confidence, so the attack abstains.")

    _section(report, "3. What epsilon means, on a mean rather than a model (section 10.1.3)")
    ages = researcher_x[:, 0]
    dp_rows = inclusion_attack(ages, drop_index=0, epsilons=(0.2, 1.0, 8.0), rng=rng)
    report.p(
        "An attacker knows every age except whether one person was included, and sees only "
        "the released mean. Accuracy is how often they guess inclusion correctly "
        "(0.50 is a coin toss)."
    )
    for row in dp_rows:
        epsilon = "none (deterministic)" if row["epsilon"] is None else _fmt(row["epsilon"], 1)
        report.p(
            f"  epsilon {epsilon:<22} attacker accuracy {_fmt(row['attacker_accuracy'])}  "
            f"Laplace scale {_fmt(row['noise_scale'], 4)}"
        )
    cherry = cherry_picked_release(ages, epsilon=0.2, n_draws=50, rng=rng)
    report.p(
        f"TECH 12: at epsilon {cherry['epsilon']}, one noisy mean misses the true mean by "
        f"{_fmt(cherry['single_release_error'], 4)}. Keeping the closest of "
        f"{cherry['n_draws']} draws misses by only {_fmt(cherry['cherry_picked_error'], 4)}. "
        "Choosing the draw that looks most like the non-private answer cancels the protection, "
        "so TRE staff would choose the random seed without looking at accuracy."
    )

    _section(report, "4. Unconstrained tree, native training")
    from sklearn.tree import DecisionTreeClassifier

    unsafe = DecisionTreeClassifier(min_samples_leaf=1, max_depth=None, random_state=SEED)
    unsafe.fit(researcher_x, researcher_y)
    unsafe_path = OUTPUT / "unsafe_tree.joblib"
    joblib.dump(unsafe, unsafe_path)
    unsafe_result = assess_predictive_model(
        unsafe, researcher_x, researcher_y, holdout_x, holdout_y, rng, N_NOISE
    )
    report.p(
        f"Researcher would claim accuracy {_fmt(unsafe_result['train_accuracy'])} "
        f"(that is the training score). On the TRE set-aside it is "
        f"{_fmt(unsafe_result['holdout_accuracy'])}."
    )
    report.p(
        f"Smallest leaf: {unsafe_result['k_anonymity']} training row. "
        f"Model file {unsafe_result['size']['model_bytes']} bytes vs training table "
        f"{unsafe_result['size']['training_bytes']} bytes "
        f"(ratio {_fmt(unsafe_result['size']['ratio'])})."
    )
    _print_mia(report, "Worst-case membership inference (Appendix G):", unsafe_result["mia"])
    _print_mia(
        report,
        "Salem-synth membership inference (attacker has similar data, not the TRE tables):",
        unsafe_result["salem"],
    )
    _print_attribute(report, unsafe_result["attribute"])
    if unsafe_result["attribute"]["members"]["guess_rate"] == 0.0:
        report.p(
            "The attack abstained: no weight value was a unique best guess. "
            "This tree isolated rows with the noise columns, and changing weight did not leave the leaf. "
            "Section 2 is the case study from the paper, where the hidden fields are ones the model actually split on. "
            "A ratio above 1 would mean training rows were easier to complete than set-aside rows."
        )
    _print_decision(report, unsafe_result["decision"])

    _section(report, "5. The same data through a safe wrapper (TECH 9-10)")
    safe = SafeDecisionTreeClassifier(
        constraints_path=str(CONSTRAINTS),
        researcher="demo-researcher",
        override=False,
        min_samples_leaf=1,
        max_depth=None,
        random_state=SEED,
    )
    for note in safe.adjustment_notes:
        report.p(f"Wrapper: {note}")
    safe.fit(researcher_x, researcher_y)
    safe_release = safe.request_release(OUTPUT / "safe_tree.joblib")
    report.p(
        f"request_release() recommendation: {safe_release['recommendation']}. "
        f"Leaf k-anonymity {safe_release['k_anonymity']}."
    )
    safe_result = assess_predictive_model(
        safe, researcher_x, researcher_y, holdout_x, holdout_y, rng, N_NOISE
    )
    report.p(
        f"Training accuracy {_fmt(safe_result['train_accuracy'])}, "
        f"set-aside accuracy {_fmt(safe_result['holdout_accuracy'])}."
    )
    _print_mia(report, "Worst-case membership inference:", safe_result["mia"])
    _print_mia(report, "Salem-synth membership inference:", safe_result["salem"])
    salem = safe_result["salem"]
    report.p(
        "The export rule follows the worst-case attack in Appendix G. "
        f"On this model that FDIF is {_fmt(safe_result['mia']['fdif'])} "
        f"(p={_fmt(safe_result['mia']['p_value'])})."
    )
    if salem["fdif"] >= 0.15 and (salem["auc"] or 0.5) < 0.60:
        report.p(
            "This Salem run is the Appendix F warning: AUC stays near 0.5 while FDIF "
            f"is {_fmt(salem['fdif'])} (p={_fmt(salem['p_value'])}). "
            "A data controller could refuse on that tail. This demo's rule does not, "
            "because it uses the worst-case check."
        )
    _print_attribute(report, safe_result["attribute"])
    _print_decision(report, safe_result["decision"])
    report.p(
        "The wrapper only gets the file as far as the TRE queue. The attack numbers are "
        "what the export decision uses. Hyperparameter ranges from a previous dataset are "
        "not enough on their own (Appendix A, experiment 2)."
    )

    _section(report, "6. Instance-based models are refused (TECH 11)")
    for factory, label in (
        (SafeKNeighborsClassifier, "k-nearest neighbours"),
        (SafeSVC, "support-vector classifier"),
    ):
        try:
            factory(constraints_path=str(CONSTRAINTS))
        except InstanceBasedModelError as error:
            report.p(f"Safe wrapper for {label}: {error}")

    knn = KNeighborsClassifier(n_neighbors=1)
    knn.fit(researcher_x, researcher_y)
    knn_stored = stored_training_rows(knn)
    knn_size = size_ratio(knn, researcher_x, researcher_y)
    knn_decision = decide(stored=knn_stored, size=knn_size)
    report.p(
        f"A raw 1-NN fitted anyway stores {knn_stored['n_stored_rows']} rows "
        f"({knn_size['model_bytes']} bytes, ratio {_fmt(knn_size['ratio'])})."
    )
    _print_decision(report, knn_decision)

    svc = SVC(kernel="rbf", random_state=SEED)
    svc.fit(researcher_x, researcher_y)
    svc_stored = stored_training_rows(svc)
    svc_decision = decide(stored=svc_stored, size=size_ratio(svc, researcher_x, researcher_y))
    report.p(
        f"A raw RBF SVC stores {svc_stored['n_stored_rows']} support vectors "
        f"out of {len(researcher_y)} training rows."
    )
    _print_decision(report, svc_decision)
    report.p(
        "The paper's alternatives are aggregated data, a differentially private training "
        "algorithm, or leaving the model inside a query-limited service. This demo does "
        "not implement a private SVM."
    )

    _section(report, "7. Editing the model after fit() (risk types RT1 and RT2)")
    tampered = SafeDecisionTreeClassifier(
        constraints_path=str(CONSTRAINTS),
        researcher="demo-researcher",
        override=True,
        min_samples_leaf=1,
        max_depth=None,
        random_state=SEED,
    )
    for note in tampered.adjustment_notes:
        report.p(f"Wrapper: {note}")
    tampered.fit(researcher_x, researcher_y)
    tampered.set_params(min_samples_leaf=20, max_depth=4)
    tampered.hidden_rows = researcher_x[:3].copy()
    tamper_release = tampered.request_release(OUTPUT / "tampered_tree.joblib")
    report.p(f"request_release() recommendation: {tamper_release['recommendation']}")
    report.p(tamper_release["details"])
    bad_type = OUTPUT / "not_a_model.txt"
    bad_type.write_text("this is not a model file", encoding="utf-8")
    type_decision = decide(file_ok=file_type_allowed(bad_type))
    report.p(f"File-type check on {bad_type.name}:")
    _print_decision(report, type_decision)

    _section(report, "8. Query budget blocks the 20-combination sweep (TECH 16)")
    gate = QueryGate(model=case_model, budget=8, user="clinic-user")
    single = gate.predict_proba(planted.reshape(1, -1), purpose="one patient lookup")
    report.p(
        f"One patient query was allowed. Predicted class probabilities "
        f"{np.array2string(single[0], precision=3)}."
    )
    try:
        sweep_unknown_fields(
            lambda rows: gate.predict_proba(rows, purpose="attribute sweep"),
            planted,
        )
        report.p("The attribute sweep was allowed, which means the budget is too high.")
    except QueryBudgetExceeded as error:
        report.p(str(error))
    report.p("Query log:")
    for entry in gate.log:
        status = "allowed" if entry["allowed"] else "refused"
        report.p(f"  {entry['user']}: {entry['rows']} rows for {entry['purpose']} - {status}")
    report.p(
        "Counting rows, not HTTP calls, matters: one request can carry all 20 combinations. "
        "The paper also asks for an external test of any real query service (TECH 17). "
        "This gate is only the control logic."
    )

    _section(report, "9. Register entry and pipeline snapshot")
    released = safe_result["decision"]["release"] and safe_release["recommendation"].startswith("Run file")
    register = {
        "project": "DEMO-001",
        "dataset": "synthetic_risk_cohort",
        "release_category": "trained_model",
        "purpose": "Illustrate disclosure control. Not for clinical use.",
        "model_file": "safe_tree.joblib" if released else None,
        "decision": "approved_for_demo_release" if released else "refused",
        "controls": [
            "TRE set-aside",
            "safe wrapper constraints",
            "worst-case membership inference",
            "attribute inference",
            "leaf k-anonymity",
            "model size check",
        ],
        "refused_files": ["unsafe_tree.joblib", "tampered_tree.joblib"],
    }
    register_path = OUTPUT / "data_use_register.json"
    register_path.write_text(json.dumps(register, indent=2), encoding="utf-8")
    snapshot = {
        "purpose": "TECH 3 audit snapshot of the candidate that went through the wrapper.",
        "seed": SEED,
        "n_rows": N_ROWS,
        "researcher_row_ids": researcher_ids.tolist(),
        "set_aside_row_ids": holdout_ids.tolist(),
        "wrapper_recommendation": safe_release["recommendation"],
        "tre_release": released,
        "params_after_wrapper": {
            "min_samples_leaf": safe.get_params()["min_samples_leaf"],
            "max_depth": safe.get_params()["max_depth"],
        },
        "demo_policy": POLICY,
    }
    snapshot_path = OUTPUT / "pipeline_snapshot.json"
    snapshot_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    report.p(f"Data-use register: {register_path.name}. Decision: {register['decision']}.")
    report.p(f"Pipeline snapshot: {snapshot_path.name}.")
    report.p(
        "Researcher declaration, in plain language rather than legal drafting: follow the "
        "approved controls, accept that the project is recorded on the register, and accept "
        "that TRE staff will run these attacks. The green paper's clause text was left for "
        "a qualified legal review."
    )

    _section(report, "10. Side by side")
    report.p(
        f"{'model':<22} {'train':>7} {'holdout':>8} {'MIA AUC':>8} {'adv.':>7} "
        f"{'TPR@10':>8} {'ARR':>7}  decision"
    )
    for name, result in (("unconstrained tree", unsafe_result), ("safe wrapper tree", safe_result)):
        decision_word = "release" if result["decision"]["release"] else "refuse"
        report.p(
            f"{name:<22} {_fmt(result['train_accuracy']):>7} {_fmt(result['holdout_accuracy']):>8} "
            f"{_fmt(result['mia']['auc']):>8} {_fmt(result['mia']['advantage']):>7} "
            f"{_fmt(result['mia']['tpr_at_fpr_10']):>8} "
            f"{_fmt(result['attribute']['attribute_risk_ratio']):>7}  {decision_word}"
        )
    report.p(f"{'1-nearest neighbour':<22} {'':>7} {'':>8} {'':>8} {'':>7} {'':>8} {'':>7}  refuse (stores rows)")
    report.p(f"{'RBF SVC':<22} {'':>7} {'':>8} {'':>8} {'':>7} {'':>8} {'':>7}  refuse (support vectors)")
    report.p(f"{'tampered tree':<22} {'':>7} {'':>8} {'':>8} {'':>7} {'':>8} {'':>7}  refuse (edited after fit)")
    report.p("")
    report.p(f"Full write-up: {OUTPUT / 'demo_report.txt'}")
    report.save(OUTPUT / "demo_report.txt")
    # The numbers above, for demo/run_gate.py. Nothing here is recomputed.
    return {
        "candidate": safe_result,
        "unconstrained": unsafe_result,
        "wrapper_recommendation": safe_release["recommendation"],
        "refusals": {
            "unconstrained tree": unsafe_result["decision"],
            "1-nearest neighbour": knn_decision,
            "RBF SVC": svc_decision,
            "file type": type_decision,
        },
        "tamper_recommendation": tamper_release["recommendation"],
        "query_log": list(gate.log),
    }


if __name__ == "__main__":
    main()
