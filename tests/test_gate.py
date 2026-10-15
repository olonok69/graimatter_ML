"""The gate reads the demos' numbers and judges them; these tests pin what it decides.

Demos 1, 3 and 4 run once for the whole module (about 30 seconds), writing to a
temporary folder so the versioned demo/output/ is left alone.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import run_aml_demo
import run_demo
import run_supply_chain_demo

from compliance_gate.controls import DEMO1, DEMO2, DEMO3, DEMO4
from compliance_gate.gate import build_report, to_dict
from compliance_gate.tolerances import METRICS, breaches, model_readings

REPO_OUTPUT = Path(__file__).resolve().parents[1] / "demo" / "output"
DEMO1_FILES = [
    "demo_report.txt",
    "data_dictionary.json",
    "data_use_register.json",
    "pipeline_snapshot.json",
    "safe_tree.release.json",
    "tampered_tree.release.json",
    "not_a_model.txt",
]
DEMO3_FILES = ["aml_report.txt"]
DEMO4_FILES = ["supply_chain_report.txt"]


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    out = tmp_path_factory.mktemp("output")
    saved = run_demo.OUTPUT, run_aml_demo.OUTPUT, run_supply_chain_demo.OUTPUT
    run_demo.OUTPUT = run_aml_demo.OUTPUT = run_supply_chain_demo.OUTPUT = out
    try:
        evidence = {DEMO1: run_demo.main(), DEMO3: run_aml_demo.main(), DEMO4: run_supply_chain_demo.main()}
    finally:
        run_demo.OUTPUT, run_aml_demo.OUTPUT, run_supply_chain_demo.OUTPUT = saved
    return evidence, out


def _normalise(name: str, text: str) -> str:
    # Some lines depend on the machine, not on the seed: the absolute path of the report, and the
    # pickled size of the tree and digests of pickled models, which change between scikit-learn versions.
    text = re.sub(r"^Full write-up: .*$", "Full write-up: <path>", text, flags=re.M)
    text = re.sub(r"sha256:[0-9a-f]{12}", "sha256:<digest>", text)
    return re.sub(r"Model file \d+ bytes", "Model file <n> bytes", text)


@pytest.mark.parametrize("name", DEMO1_FILES + DEMO3_FILES + DEMO4_FILES)
def test_regenerated_outputs_match_versioned(runs, name):
    _, out = runs
    fresh = (out / name).read_text(encoding="utf-8")
    versioned = (REPO_OUTPUT / name).read_text(encoding="utf-8")
    assert _normalise(name, fresh) == _normalise(name, versioned)


@pytest.mark.parametrize("model", ["candidate", "unconstrained"])
def test_gate_agrees_with_demo1_policy(runs, model):
    evidence, _ = runs
    result = evidence[DEMO1][model]
    breached = [r.name for r in model_readings(result) if breaches(METRICS[r.name], r)]
    assert (not breached) == result["decision"]["release"], breached


def test_seeded_verdicts(runs):
    evidence, _ = runs
    report = build_report(evidence, regimes=["all"], accept_missing=[DEMO2])
    within = {v.category for v in report.category_verdicts if v.within}
    breached = {v.category for v in report.category_verdicts if not v.within}
    assert within == {
        "membership", "attribute", "generalisation", "stored_rows", "release_check", "query_budget", "supply_chain"
    }
    assert breached == {"evasion", "extraction", "poisoning"}
    assert not report.passed

    status = {(v.control.regulation, v.control.ref): v for v in report.control_verdicts}
    assert status[("EU AI Act", "Art. 15(5) model evasion")].status == "fail"
    assert status[("NIST AI 100-2e2025", "NISTAML.033")].status == "pass"
    assert status[("GRAIMATTER", "TECH 7")].status == "pass"
    assert status[("NIST AI RMF", "MEASURE 2.10")].status == "pass"
    assert status[("EU AI Act", "Art. 15(5) model poisoning")].status == "pass"
    assert status[("NIST AI 100-2e2025", "NISTAML.051")].status == "pass"
    sacroml = status[("GRAIMATTER", "TECH 7, 9 (SACRO-ML)")]
    assert sacroml.status == "not_evidenced" and sacroml.accepted


def test_missing_demo_is_not_evidenced_and_fails(runs):
    evidence, _ = runs
    report = build_report({DEMO1: evidence[DEMO1]}, regimes=["eu_uk"])
    evasion = next(v for v in report.control_verdicts if v.control.ref == "Art. 15(5) model evasion")
    assert evasion.status == "not_evidenced" and not evasion.accepted
    assert not report.passed


def test_graimatter_pack_passes_on_demo1(runs):
    evidence, _ = runs
    report = build_report({DEMO1: evidence[DEMO1]}, regimes=["graimatter"], accept_missing=[DEMO2])
    assert report.passed
    assert to_dict(report)["overall"] == "pass"


def test_fail_under_overrides_a_tolerance(runs):
    evidence, _ = runs
    loose = {name: 1.0 for name, spec in METRICS.items() if spec.stage == DEMO3 and spec.limit}
    report = build_report(evidence, overrides=loose, accept_missing=[DEMO2])
    assert report.passed
    payload = json.loads(json.dumps(to_dict(report)))
    assert payload["accepted_missing"] == [DEMO2]


def test_unknown_override_is_rejected(runs):
    evidence, _ = runs
    with pytest.raises(ValueError):
        build_report(evidence, overrides={"evasion.typo": 0.5})


def test_supply_chain_checks(runs):
    evidence, _ = runs
    demo4 = evidence[DEMO4]
    # Every tampered file passes the check a user usually runs, and none passes the pin with the scan or floor.
    assert demo4["passed_usual_checks"] == demo4["tampered_files"] == 4
    assert demo4["accepted"] == 0
    assert demo4["trigger_success"]["backdoored"] - demo4["trigger_success"]["clean"] > 0.5
    # A pin taken from the tampered download proves nothing.
    assert demo4["late_pin_accepts_backdoor"]


def test_tampered_supply_chain_fails_the_gate(runs):
    evidence, _ = runs
    tampered = dict(evidence[DEMO4], accepted=1)
    report = build_report({DEMO4: tampered}, regimes=["nist_aml"], accept_missing=[DEMO1, DEMO3])
    status = {v.control.ref: v.status for v in report.control_verdicts}
    assert status["NISTAML.051"] == "fail"
    assert not report.passed
