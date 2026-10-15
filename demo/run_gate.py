"""Run the demos and judge their results against regulatory controls and tolerances.

The pattern comes from safety-trust-engine: controls mapped to evidence, numeric
tolerances, ``not_evidenced`` for controls whose demo did not run, and a JSON and
Markdown report. The script exits with 1 when a category breaches its tolerance
or a selected control is not evidenced, so CI can block on it.

Run from the repository root:

    python demo/run_gate.py                          # demos 1-4, packs eu_uk, nist_aml, graimatter
    python demo/run_gate.py --regimes us             # NIST AI RMF and federal model risk management
    python demo/run_gate.py --demos 1,3,4 --accept-missing 2
    python demo/run_gate.py --fail-under evasion.self_reported=0.5

Demo 2 needs sacroml. Without it, demo 2 is skipped and its controls are not
evidenced; ``--accept-missing 2`` says so explicitly instead of failing the run.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib
import io
import sys
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent
if str(DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(DEMO_DIR))

from compliance_gate.controls import DEMO1, DEMO2, DEMO3, DEMO4, REGIME_PACKS  # noqa: E402
from compliance_gate.gate import build_report, write_json, write_markdown  # noqa: E402
from compliance_gate.tolerances import METRICS  # noqa: E402

SCRIPTS = {DEMO1: "run_demo", DEMO2: "run_sacroml_demo", DEMO3: "run_aml_demo", DEMO4: "run_supply_chain_demo"}
OUTPUT = DEMO_DIR / "output" / "gate"


def _demo_names(values: list[str]) -> list[str]:
    names: list[str] = []
    for value in values:
        for part in value.replace(",", " ").split():
            name = part if part.startswith("demo") else f"demo{part}"
            if name not in SCRIPTS:
                raise SystemExit(f"unknown demo {part!r}; use 1, 2, 3 or 4")
            if name not in names:
                names.append(name)
    return names


def _limits(values: list[str]) -> dict[str, float]:
    limits: dict[str, float] = {}
    for value in values:
        name, sep, number = value.partition("=")
        if not sep or name not in METRICS:
            raise SystemExit(f"--fail-under takes metric=value; metrics: {', '.join(METRICS)}")
        limits[name] = float(number)
    return limits


def run_demos(names: list[str], show: bool = False) -> dict[str, dict]:
    """Run each demo's main() and keep what it returns. Demo 2 is skipped if sacroml is missing."""
    evidence: dict[str, dict] = {}
    for name in names:
        try:
            module = importlib.import_module(SCRIPTS[name])
        except ModuleNotFoundError as error:
            if name == DEMO2 and (error.name or "").startswith("sacroml"):
                print(f"{name}: skipped, sacroml is not installed (pip install sacroml)")
                continue
            raise
        print(f"{name}: running {SCRIPTS[name]}.py")
        sink = contextlib.nullcontext() if show else contextlib.redirect_stdout(io.StringIO())
        with sink:
            evidence[name] = module.main()
    return evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--demos", nargs="*", default=["1,2,3,4"], help="demos to run, e.g. 1,3,4 (default 1,2,3,4)")
    parser.add_argument(
        "--regimes",
        default="eu_uk,nist_aml,graimatter",
        help=f"comma-separated packs: {', '.join(REGIME_PACKS)}, or all",
    )
    parser.add_argument("--fail-under", nargs="*", default=[], metavar="METRIC=VALUE", help="override a tolerance")
    parser.add_argument(
        "--accept-missing",
        nargs="*",
        default=[],
        metavar="DEMO",
        help="demos declared out of scope: controls that need them are not evidenced but do not fail the run",
    )
    parser.add_argument("--out", type=Path, default=OUTPUT, help="where to write the report")
    parser.add_argument("--show-demos", action="store_true", help="print the demos' own reports too")
    args = parser.parse_args(argv)

    demos = _demo_names(args.demos)
    accepted = _demo_names(args.accept_missing) if args.accept_missing else []
    evidence = run_demos(demos, show=args.show_demos)
    report = build_report(
        evidence,
        regimes=args.regimes.split(","),
        overrides=_limits(args.fail_under),
        accept_missing=accepted,
    )

    args.out.mkdir(parents=True, exist_ok=True)
    stem = "gate_" + "-".join(report.regimes)
    write_json(report, args.out / f"{stem}.json")
    write_markdown(report, args.out / f"{stem}.md")

    print()
    for verdict in report.category_verdicts:
        print(f"  {verdict.category:<15} {'within tolerance' if verdict.within else 'BREACH'}")
    counts = {status: 0 for status in ("pass", "fail", "not_evidenced")}
    for verdict in report.control_verdicts:
        counts[verdict.status] += 1
    print(
        f"\nControls: {counts['pass']} pass, {counts['fail']} fail, {counts['not_evidenced']} not evidenced"
        f" ({sum(v.accepted for v in report.control_verdicts)} of them declared out of scope)."
    )
    print(f"Gate: {'PASS' if report.passed else 'FAIL'}. Report: {args.out / stem}.json and .md")
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
