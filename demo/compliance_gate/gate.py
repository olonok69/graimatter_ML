"""Tolerance gate, control verdicts and the evidence report.

Follows safety-trust-engine's report.py: per-category tolerances, a verdict per
control (pass, fail or not_evidenced), and one report as JSON for machines and
Markdown for people. ``GateReport.passed`` drives the exit code of run_gate.py.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from .controls import CATEGORIES, DEMOS, Control, controls_for_regimes, regulations, resolve_regimes
from .tolerances import METRICS, READERS, Reading, breaches

DISCLAIMER = (
    "The mapping of demo metrics to these clauses was made for this repository; the frameworks do not "
    "cross-reference each other this precisely and none of them sets numeric thresholds. The tolerances are a "
    "demo risk appetite (GRAIMATTER ELA 8), not official cut-offs. Synthetic data only. Not legal advice."
)


@dataclass
class MetricVerdict:
    name: str
    category: str
    stage: str
    description: str
    value: float | None
    limit: float
    breach: bool
    p_value: float | None = None


@dataclass
class CategoryVerdict:
    category: str
    metrics: list[MetricVerdict]

    @property
    def within(self) -> bool:
        return not any(m.breach for m in self.metrics)


@dataclass
class ControlVerdict:
    control: Control
    status: str  # "pass" | "fail" | "not_evidenced"
    breaching_categories: list[str] = field(default_factory=list)
    missing_stages: list[str] = field(default_factory=list)
    accepted: bool = False  # not_evidenced only because of demos the run declared out of scope


@dataclass
class GateReport:
    run_id: str
    timestamp: str
    regimes: tuple[str, ...]
    demos_run: list[str]
    accepted_missing: list[str]
    category_verdicts: list[CategoryVerdict]
    control_verdicts: list[ControlVerdict]
    limits: dict[str, float]

    @property
    def passed(self) -> bool:
        # Strict, like safety-trust-engine: every category within tolerance and every selected control
        # passing. The only exception is a control the run declared out of scope with --accept-missing.
        gate_ok = all(v.within for v in self.category_verdicts)
        controls_ok = all(v.status == "pass" or v.accepted for v in self.control_verdicts)
        return gate_ok and controls_ok


def build_report(
    evidence: dict[str, dict],
    regimes: Sequence[str] | None = None,
    overrides: dict[str, float] | None = None,
    accept_missing: Sequence[str] = (),
    run_id: str | None = None,
) -> GateReport:
    """Judge the raw results of the demos that ran. ``evidence`` maps demo name to its main() result."""
    unknown = set(overrides or {}) - set(METRICS)
    if unknown:
        raise ValueError(f"unknown metric(s) {sorted(unknown)}; valid: {', '.join(METRICS)}")
    limits = {name: spec.limit for name, spec in METRICS.items()} | (overrides or {})
    selected = resolve_regimes(regimes)
    ran = [demo for demo in DEMOS if demo in evidence]

    readings: list[Reading] = []
    for demo in ran:
        readings.extend(READERS[demo](evidence[demo]))
    by_category: dict[str, list[MetricVerdict]] = {}
    for reading in readings:
        spec = METRICS[reading.name]
        by_category.setdefault(spec.category, []).append(
            MetricVerdict(
                name=reading.name,
                category=spec.category,
                stage=spec.stage,
                description=spec.description,
                value=reading.value,
                limit=limits[reading.name],
                breach=breaches(spec, reading, limits[reading.name]),
                p_value=reading.p_value,
            )
        )
    category_verdicts = [CategoryVerdict(c, by_category[c]) for c in CATEGORIES if c in by_category]
    breaching = {v.category for v in category_verdicts if not v.within}

    control_verdicts: list[ControlVerdict] = []
    for control in controls_for_regimes(selected):
        missing = [stage for stage in control.stages if stage not in ran]
        if missing:
            control_verdicts.append(
                ControlVerdict(
                    control,
                    "not_evidenced",
                    missing_stages=missing,
                    accepted=set(missing) <= set(accept_missing),
                )
            )
            continue
        breached = [c for c in control.categories if c in breaching]
        control_verdicts.append(ControlVerdict(control, "fail" if breached else "pass", breached))

    now = datetime.now(UTC)
    return GateReport(
        run_id=run_id or now.strftime("gate-%Y%m%dT%H%M%SZ"),
        timestamp=now.isoformat(timespec="seconds"),
        regimes=selected,
        demos_run=ran,
        accepted_missing=list(accept_missing),
        category_verdicts=category_verdicts,
        control_verdicts=control_verdicts,
        limits=limits,
    )


def _number(value: float | None) -> float | str | None:
    if value is None:
        return None
    if value == float("inf"):
        return "inf"
    return round(float(value), 4)


def to_dict(report: GateReport) -> dict:
    return {
        "run_id": report.run_id,
        "timestamp": report.timestamp,
        "overall": "pass" if report.passed else "fail",
        "regimes": list(report.regimes),
        "demos_run": report.demos_run,
        "accepted_missing": report.accepted_missing,
        "category_verdicts": [
            {
                "category": v.category,
                "within": v.within,
                "metrics": [
                    {
                        "name": m.name,
                        "demo": m.stage,
                        "value": _number(m.value),
                        "limit": m.limit,
                        "breach": m.breach,
                        **({"p_value": _number(m.p_value)} if m.p_value is not None else {}),
                        "description": m.description,
                    }
                    for m in v.metrics
                ],
            }
            for v in report.category_verdicts
        ],
        "compliance": [
            {
                "regulation": v.control.regulation,
                "ref": v.control.ref,
                "label": v.control.label,
                "binding": v.control.binding,
                "status": v.status,
                "evidence_stages": list(v.control.stages),
                "breaching_categories": v.breaching_categories,
                "missing_stages": v.missing_stages,
                "accepted_as_out_of_scope": v.accepted,
                "note": v.control.note,
            }
            for v in report.control_verdicts
        ],
        "disclaimer": DISCLAIMER,
    }


def write_json(report: GateReport, path: Path) -> None:
    path.write_text(json.dumps(to_dict(report), indent=2) + "\n", encoding="utf-8")


def _shown(value: float | None) -> str:
    if value is None:
        return "not measured"
    if value == float("inf"):
        return "inf"
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.3f}"


def write_markdown(report: GateReport, path: Path) -> None:
    badge = "PASS" if report.passed else "FAIL"
    lines = [
        f"# Release gate evidence: {badge}",
        "",
        f"- Run: `{report.run_id}`",
        f"- Timestamp: {report.timestamp}",
        f"- Regimes: `{', '.join(report.regimes)}`",
        f"- Demos run: {', '.join(report.demos_run) or 'none'}",
    ]
    if report.accepted_missing:
        lines.append(
            f"- Declared out of scope for this run: {', '.join(report.accepted_missing)}. "
            "Controls that need them are reported as not evidenced and do not fail the run."
        )
    lines += [
        "",
        "## Tolerance gate",
        "",
        "| Category | Metric | Demo | Value | Tolerance | Within |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for v in report.category_verdicts:
        for m in v.metrics:
            value = _shown(m.value)
            if m.p_value is not None:
                value += f" (p={m.p_value:.3f})"
            mark = "**NO**" if m.breach else "yes"
            lines.append(f"| {v.category} | {m.description} | {m.stage} | {value} | {_shown(m.limit)} | {mark} |")

    selected = [v.control for v in report.control_verdicts]
    lines += [
        "",
        "## Controls",
        "",
        "_binding: `statute` = legal obligation; `guidance` = voluntary; `supervisory` = examiner expectation; "
        "`recommendation` = the GRAIMATTER green paper._",
        "",
    ]
    for regulation in regulations(selected):
        lines += [f"### {regulation}", "", "| Ref | Control | Binding | Status |", "| --- | --- | --- | --- |"]
        for v in report.control_verdicts:
            if v.control.regulation != regulation:
                continue
            status = v.status
            if v.status == "fail":
                status = f"**fail** ({', '.join(v.breaching_categories)})"
            elif v.status == "not_evidenced":
                status = f"not_evidenced (needs {', '.join(v.missing_stages)}"
                status += ", out of scope)" if v.accepted else ")"
            lines.append(f"| {v.control.ref} | {v.control.label} | {v.control.binding} | {status} |")
        lines.append("")

    failures = [v for v in report.control_verdicts if v.status == "fail"]
    gaps = [v for v in report.control_verdicts if v.status == "not_evidenced" and not v.accepted]
    if failures or gaps:
        lines += ["## Remediation required", ""]
        for v in failures:
            lines.append(f"- {v.control.regulation} {v.control.ref}: breach in {', '.join(v.breaching_categories)}")
        for v in gaps:
            lines.append(f"- {v.control.regulation} {v.control.ref}: run {', '.join(v.missing_stages)} to evidence it")
        lines.append("")
    lines += ["## Scope", "", DISCLAIMER, ""]
    path.write_text("\n".join(lines), encoding="utf-8")
