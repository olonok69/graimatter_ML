"""Tolerances per metric, and the metrics each demo already reports.

A tolerance is the largest value of a metric the data controller accepts. It
is a risk appetite agreed with whoever is accountable for the data (GRAIMATTER
ELA 8), not a threshold from the green paper, from NIST or from any regulation:
none of them publishes one. The privacy tolerances are demo 1's ``POLICY`` in
graimatter_demo/disclosure.py, read from there so the two cannot drift apart.
The others are set here for the workshop.

The extractors below only read numbers the demos already computed and printed.
They do not rerun or recompute an attack.
"""

from __future__ import annotations

from dataclasses import dataclass

from graimatter_demo.disclosure import POLICY

from .controls import DEMO1, DEMO2, DEMO3


@dataclass(frozen=True)
class MetricSpec:
    """How one metric is judged.

    inclusive : breach when value >= limit (demo 1's rule); otherwise when value > limit.
    max_p     : if set, a breach also needs the metric's p-value to be at most this.
    """

    category: str
    stage: str
    limit: float
    description: str
    inclusive: bool = False
    max_p: float | None = None


METRICS: dict[str, MetricSpec] = {
    # Demo 1, the release candidate (the safe-wrapper tree). Same rules as disclosure.decide().
    "membership.worst_case_auc": MetricSpec(
        "membership", DEMO1, POLICY["max_mia_auc"], "Worst-case membership AUC", inclusive=True
    ),
    "membership.advantage": MetricSpec(
        "membership", DEMO1, POLICY["max_advantage"], "Membership advantage (TPR - FPR)", inclusive=True
    ),
    "membership.tpr_at_fpr_10": MetricSpec(
        "membership", DEMO1, POLICY["max_tpr_at_fpr_10"], "Membership TPR at 10% FPR", inclusive=True
    ),
    "membership.fdif": MetricSpec(
        "membership",
        DEMO1,
        POLICY["max_fdif"],
        "Membership FDIF, counted only when significant",
        inclusive=True,
        max_p=POLICY["max_fdif_p_value"],
    ),
    "attribute.risk_ratio": MetricSpec(
        "attribute", DEMO1, POLICY["max_attribute_risk_ratio"], "Attribute risk ratio for weight", inclusive=True
    ),
    "generalisation.accuracy_gap": MetricSpec(
        "generalisation", DEMO1, POLICY["max_accuracy_gap"], "Training minus TRE-holdout accuracy"
    ),
    "stored_rows.rows_in_model": MetricSpec("stored_rows", DEMO1, 0, "Training rows stored in the model file"),
    "stored_rows.size_ratio": MetricSpec(
        "stored_rows", DEMO1, POLICY["max_model_to_data_ratio"], "Model file size / training table size"
    ),
    "release_check.disclosive_released": MetricSpec(
        "release_check", DEMO1, 0, "Known-disclosive files the release check let through (of 5)"
    ),
    "query_budget.sweep_rows_allowed": MetricSpec(
        "query_budget", DEMO1, 0, "Rows of the 20-row attribute sweep the query gate allowed"
    ),
    # Demo 2, the same candidate through SACRO-ML.
    "membership.sacroml_worst_case_auc": MetricSpec(
        "membership", DEMO2, POLICY["max_mia_auc"], "SACRO-ML worst-case membership AUC (mean)", inclusive=True
    ),
    "release_check.sacroml_missed": MetricSpec(
        "release_check", DEMO2, 0, "Disclosive configurations SACRO-ML did not flag (of 2)"
    ),
    # Demo 3, the random forest.
    "evasion.self_reported": MetricSpec(
        "evasion", DEMO3, 0.10, "High-risk people who evade by misreporting smoking, weight, blood pressure"
    ),
    "evasion.smoking_verified": MetricSpec(
        "evasion", DEMO3, 0.10, "Same, with smoking verified by a test"
    ),
    "evasion.clinic_measured": MetricSpec(
        "evasion", DEMO3, 0.10, "Same, with smoking and weight measured in clinic"
    ),
    "extraction.copy_agreement_at_budget": MetricSpec(
        "extraction", DEMO3, 0.80, "Agreement of a copy trained on one query budget of labels"
    ),
    "query_budget.over_budget_request_allowed": MetricSpec(
        "query_budget", DEMO3, 0, "1 if the query gate let a 1,000-row request through"
    ),
    "poisoning.backdoor_lift": MetricSpec(
        "poisoning", DEMO3, 0.10, "Worst rise in trigger success after poisoning, over the clean model"
    ),
}

EVASION_SCENARIOS = {
    "smoking, weight and blood pressure self-reported": "evasion.self_reported",
    "smoking verified by a test": "evasion.smoking_verified",
    "smoking and weight measured in clinic": "evasion.clinic_measured",
}


@dataclass(frozen=True)
class Reading:
    """One metric value from one demo run."""

    name: str
    value: float | None
    p_value: float | None = None


def model_readings(result: dict) -> list[Reading]:
    """Demo 1's assess_predictive_model() output, as gate readings."""
    mia = result["mia"]
    return [
        Reading("membership.worst_case_auc", mia.get("auc")),
        Reading("membership.advantage", mia["advantage"]),
        Reading("membership.tpr_at_fpr_10", mia["tpr_at_fpr_10"]),
        Reading("membership.fdif", mia["fdif"], mia["p_value"]),
        Reading("attribute.risk_ratio", result["attribute"]["attribute_risk_ratio"]),
        Reading("generalisation.accuracy_gap", result["train_accuracy"] - result["holdout_accuracy"]),
        Reading("stored_rows.rows_in_model", result["stored"]["n_stored_rows"]),
        Reading("stored_rows.size_ratio", result["size"]["ratio"]),
    ]


def demo1_readings(raw: dict) -> list[Reading]:
    released = sum(decision["release"] for decision in raw["refusals"].values())
    released += raw["tamper_recommendation"].startswith("Run file")
    sweep_allowed = sum(
        entry["rows"] for entry in raw["query_log"] if entry["purpose"] == "attribute sweep" and entry["allowed"]
    )
    return [
        *model_readings(raw["candidate"]),
        Reading("release_check.disclosive_released", released),
        Reading("query_budget.sweep_rows_allowed", sweep_allowed),
    ]


def demo2_readings(raw: dict) -> list[Reading]:
    aucs = raw["candidate"]["membership_aucs"]
    missed = (not raw["unsafe_config_flagged"]) + (not raw["posthoc_edit_flagged"])
    return [
        Reading("membership.sacroml_worst_case_auc", sum(aucs) / len(aucs) if aucs else None),
        Reading("release_check.sacroml_missed", missed),
    ]


def demo3_readings(raw: dict) -> list[Reading]:
    readings = [Reading(EVASION_SCENARIOS[label], stats["evaded"]) for label, stats in raw["evasion"].items()]
    at_budget = raw["extraction"].get(raw["query_gate_budget"])
    readings.append(Reading("extraction.copy_agreement_at_budget", at_budget["agreement"] if at_budget else None))
    readings.append(Reading("query_budget.over_budget_request_allowed", int(raw["over_budget_allowed"])))
    lift = max(row["success"] - raw["backdoor_clean"][row["trigger"]] for row in raw["backdoor"])
    readings.append(Reading("poisoning.backdoor_lift", lift))
    return readings


READERS = {DEMO1: demo1_readings, DEMO2: demo2_readings, DEMO3: demo3_readings}


def breaches(spec: MetricSpec, reading: Reading, limit: float | None = None) -> bool:
    limit = spec.limit if limit is None else limit
    if reading.value is None:
        return False
    over = reading.value >= limit if spec.inclusive else reading.value > limit
    if spec.max_p is not None and reading.p_value is not None:
        over = over and reading.p_value <= spec.max_p
    return over
