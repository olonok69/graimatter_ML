"""Regulation -> control -> evidence mapping for the demos.

The pattern comes from safety-trust-engine (src/safety_engine/compliance.py),
which does the same for LLMs and agents with garak, AgentDojo and PyRIT. Here the
evidence comes from the four demos in this repository:

    demo1  run_demo.py               hand-written GRAIMATTER checks (privacy)
    demo2  run_sacroml_demo.py       the same checks through SACRO-ML
    demo3  run_aml_demo.py           evasion, extraction, backdoor
    demo4  run_supply_chain_demo.py  a supplied model and its files, tampered on the way

Controls are grouped into regime packs, selected with ``--regimes``:

    eu_uk      EU AI Act Art. 15(5), UK Code of Practice / ETSI EN 304 223
    nist_aml   NIST AI 100-2e2025 attack classes
    graimatter GRAIMATTER green paper, TECH recommendations
    us         NIST AI RMF MEASURE, federal model risk management (SR 26-02)

A control passes only when every demo it relies on ran and every category it
lists stayed within tolerance. A control whose demo did not run is
``not_evidenced``, never ``pass``.

``binding`` says how hard the obligation is, so the report does not imply more
than it can: statute | guidance | supervisory | recommendation.

The mapping of demo metrics to these clauses was made for this repository. The
frameworks do not cross-reference each other this precisely, and none of them
sets numeric thresholds.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

DEMO1 = "demo1"
DEMO2 = "demo2"
DEMO3 = "demo3"
DEMO4 = "demo4"
DEMOS: tuple[str, ...] = (DEMO1, DEMO2, DEMO3, DEMO4)

# Every category the demos measure. See tolerances.py for the metrics behind each.
CATEGORIES: tuple[str, ...] = (
    "membership",
    "attribute",
    "generalisation",
    "stored_rows",
    "release_check",
    "query_budget",
    "evasion",
    "extraction",
    "poisoning",
    "supply_chain",
)

EU_UK = "eu_uk"
NIST_AML = "nist_aml"
GRAIMATTER = "graimatter"
US = "us"
DEFAULT_REGIMES: tuple[str, ...] = (EU_UK, NIST_AML, GRAIMATTER)


@dataclass(frozen=True)
class Control:
    """One obligation the demos claim to evidence.

    stages     : demos that must run for the control to be evidenced.
    categories : categories whose tolerance breach fails the control.
    binding    : statute | guidance | supervisory | recommendation.
    """

    regulation: str
    ref: str
    label: str
    stages: tuple[str, ...]
    categories: tuple[str, ...] = ()
    note: str = ""
    binding: str = "statute"


EU_UK_CONTROLS: list[Control] = [
    Control(
        regulation="EU AI Act",
        ref="Art. 15(5) data poisoning",
        label="Resilience against attacks that manipulate the training data set.",
        stages=(DEMO3,),
        categories=("poisoning",),
        note="High-risk obligations apply from 2 December 2027 for Annex III systems (Regulation (EU) 2026/1744).",
    ),
    Control(
        regulation="EU AI Act",
        ref="Art. 15(5) model evasion",
        label="Resilience against inputs designed to cause the model to make a mistake.",
        stages=(DEMO3,),
        categories=("evasion",),
    ),
    Control(
        regulation="EU AI Act",
        ref="Art. 15(5) confidentiality attacks",
        label="Resilience against attacks that extract the model or infer its training data.",
        stages=(DEMO1, DEMO3),
        categories=("membership", "attribute", "extraction"),
    ),
    Control(
        regulation="EU AI Act",
        ref="Art. 15(5) model poisoning",
        label="Resilience against attacks on pre-trained components used in training.",
        stages=(DEMO4,),
        categories=("supply_chain",),
    ),
    Control(
        regulation="UK Code of Practice / ETSI EN 304 223",
        ref="3.1",
        label="Threat modelling covers AI-specific attacks such as data poisoning, model inversion and "
        "membership inference.",
        stages=(DEMO1, DEMO3),
        categories=("poisoning", "evasion", "membership", "attribute"),
        binding="guidance",
    ),
    Control(
        regulation="UK Code of Practice / ETSI EN 304 223",
        ref="6.2",
        label="APIs limit the rate of model access to hinder reverse engineering and rapid poisoning.",
        stages=(DEMO1, DEMO3),
        categories=("query_budget", "extraction"),
        binding="guidance",
    ),
    Control(
        regulation="UK Code of Practice / ETSI EN 304 223",
        ref="9.4",
        label="Outputs do not let users reverse engineer non-public aspects of the model or its training data.",
        stages=(DEMO1, DEMO3),
        categories=("membership", "attribute", "extraction"),
        binding="guidance",
    ),
    Control(
        regulation="UK Code of Practice / ETSI EN 304 223",
        ref="7, 8.1.2",
        label="Secure the supply chain; check model components against published cryptographic hashes.",
        stages=(DEMO4,),
        categories=("supply_chain",),
        binding="guidance",
    ),
]

NIST_AML_CONTROLS: list[Control] = [
    Control(
        regulation="NIST AI 100-2e2025",
        ref="NISTAML.025",
        label="Black-box evasion.",
        stages=(DEMO3,),
        categories=("evasion",),
        binding="guidance",
    ),
    Control(
        regulation="NIST AI 100-2e2025",
        ref="NISTAML.023",
        label="Backdoor poisoning.",
        stages=(DEMO3,),
        categories=("poisoning",),
        binding="guidance",
    ),
    Control(
        regulation="NIST AI 100-2e2025",
        ref="NISTAML.031",
        label="Model extraction.",
        stages=(DEMO3,),
        categories=("extraction",),
        binding="guidance",
    ),
    Control(
        regulation="NIST AI 100-2e2025",
        ref="NISTAML.032",
        label="Reconstruction, including attribute inference (section 2.4.1).",
        stages=(DEMO1,),
        categories=("attribute",),
        binding="guidance",
    ),
    Control(
        regulation="NIST AI 100-2e2025",
        ref="NISTAML.033",
        label="Membership inference.",
        stages=(DEMO1,),
        categories=("membership",),
        binding="guidance",
    ),
    Control(
        regulation="NIST AI 100-2e2025",
        ref="NISTAML.051",
        label="Model poisoning through a supplied model (supply chain).",
        stages=(DEMO4,),
        categories=("supply_chain",),
        binding="guidance",
    ),
]

GRAIMATTER_CONTROLS: list[Control] = [
    Control(
        regulation="GRAIMATTER",
        ref="TECH 6",
        label="Keep part of the data aside, never give it to the researchers, and score the model on it.",
        stages=(DEMO1,),
        categories=("generalisation",),
        binding="recommendation",
    ),
    Control(
        regulation="GRAIMATTER",
        ref="TECH 7",
        label="Run a range of checks before release: holdout accuracy, attack simulations, file size.",
        stages=(DEMO1,),
        categories=("membership", "attribute", "generalisation", "stored_rows"),
        binding="recommendation",
    ),
    Control(
        regulation="GRAIMATTER",
        ref="TECH 9-10",
        label="Safe wrappers correct hyperparameters and catch changes made after fit().",
        stages=(DEMO1,),
        categories=("release_check",),
        binding="recommendation",
    ),
    Control(
        regulation="GRAIMATTER",
        ref="TECH 11",
        label="Instance-based models, which store training rows, are not released as they are.",
        stages=(DEMO1,),
        categories=("stored_rows", "release_check"),
        binding="recommendation",
    ),
    Control(
        regulation="GRAIMATTER",
        ref="TECH 16",
        label="Limit the queries on a model once it is released.",
        stages=(DEMO1,),
        categories=("query_budget",),
        binding="recommendation",
    ),
    Control(
        regulation="GRAIMATTER",
        ref="TECH 7, 9 (SACRO-ML)",
        label="The same checks with the maintained AI-SDC toolkit agree with the hand-written ones.",
        stages=(DEMO1, DEMO2),
        categories=("membership", "release_check"),
        note="Needs demo 2, which needs sacroml (and PyTorch). CI does not run it.",
        binding="recommendation",
    ),
]

US_CONTROLS: list[Control] = [
    Control(
        regulation="NIST AI RMF",
        ref="MEASURE 2.6",
        label="Residual negative risk does not exceed the risk tolerance.",
        stages=(DEMO1, DEMO3),
        categories=CATEGORIES,
        note="The tolerances are the risk tolerance. Voluntary guidance, not certification.",
        binding="guidance",
    ),
    Control(
        regulation="NIST AI RMF",
        ref="MEASURE 2.7",
        label="Security and resilience are evaluated and documented.",
        stages=(DEMO3,),
        categories=("evasion", "extraction", "poisoning"),
        binding="guidance",
    ),
    Control(
        regulation="NIST AI RMF",
        ref="MEASURE 2.10",
        label="Privacy risk is examined and documented.",
        stages=(DEMO1,),
        categories=("membership", "attribute", "stored_rows"),
        binding="guidance",
    ),
    Control(
        regulation="NIST AI RMF",
        ref="GOVERN 6.1",
        label="Policies and procedures address the AI risks of third-party entities, including supplied models.",
        stages=(DEMO4,),
        categories=("supply_chain",),
        binding="guidance",
    ),
    Control(
        regulation="Federal MRM",
        ref="SR 26-02 validation",
        label="Independent validation: outcomes analysis on data the developer never saw.",
        stages=(DEMO1,),
        categories=("generalisation", "membership", "attribute"),
        note="The TRE holdout (GRAIMATTER TECH 6) is the independent validation set. A risk classifier "
        "is a model in the plain sense of the guidance, not by analogy as an LLM would be.",
        binding="supervisory",
    ),
    Control(
        regulation="Federal MRM",
        ref="SR 26-02 monitoring",
        label="Ongoing monitoring: a repeatable gate in CI with numeric tolerances.",
        stages=(DEMO1, DEMO3),
        categories=CATEGORIES,
        binding="supervisory",
    ),
    Control(
        regulation="Federal MRM",
        ref="SR 26-02 third-party model",
        label="A vendor model is checked like an in-house one: the file in use is the file that was approved.",
        stages=(DEMO4,),
        categories=("supply_chain",),
        note="The pin proves the file is the approved one, not that the approved file is sound.",
        binding="supervisory",
    ),
    Control(
        regulation="Federal MRM",
        ref="SR 26-02 documentation",
        label="A model-risk file that records the tests, the tolerances and what failed.",
        stages=(),
        note="Satisfied by this JSON and Markdown report.",
        binding="supervisory",
    ),
]

REGIME_PACKS: dict[str, list[Control]] = {
    EU_UK: EU_UK_CONTROLS,
    NIST_AML: NIST_AML_CONTROLS,
    GRAIMATTER: GRAIMATTER_CONTROLS,
    US: US_CONTROLS,
}


def resolve_regimes(names: Sequence[str] | None = None) -> tuple[str, ...]:
    """Validate pack names, keep their order, drop duplicates. ``all`` selects every pack."""
    if not names:
        return DEFAULT_REGIMES
    resolved: list[str] = []
    for raw in names:
        name = raw.strip()
        if name == "all":
            return tuple(REGIME_PACKS)
        if not name:
            continue
        if name not in REGIME_PACKS:
            raise ValueError(f"unknown regime pack {name!r}; valid: {', '.join(REGIME_PACKS)} or all")
        if name not in resolved:
            resolved.append(name)
    return tuple(resolved) or DEFAULT_REGIMES


def controls_for_regimes(regimes: Sequence[str] | None = None) -> list[Control]:
    return [control for name in resolve_regimes(regimes) for control in REGIME_PACKS[name]]


def regulations(controls: Sequence[Control]) -> list[str]:
    seen: list[str] = []
    for control in controls:
        if control.regulation not in seen:
            seen.append(control.regulation)
    return seen
