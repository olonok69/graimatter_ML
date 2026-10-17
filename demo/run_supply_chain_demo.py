"""Demo 4: a model supply chain, attacked between the supplier and the user.

A supplier publishes a trained model, a configuration file and the safe-wrapper
rules a TRE uses. Someone who controls a mirror (or a package index, a model
hub, a shared drive) changes them on the way. Every tampered file still passes
the checks a user usually runs (holdout accuracy, a functional test), and only
a digest pinned at approval time, an import scan and floors kept in code
catch them. This is NISTAML.051 in NIST AI 100-2e2025: model poisoning through
a supplied model.

Nothing here touches real cryptographic software: the downgrade is a number in
a JSON file and the arithmetic of a key search.

Run from the repository root:

    python demo/run_supply_chain_demo.py

Walkthrough of the code and its output: docs/guide/Demo_Guide_EN.md, section 4
(Spanish: docs/guide/Guia_Demos_ES.md). The comments below cite it as "Demo guide §4.N",
where N is the section number the report prints.
"""

from __future__ import annotations

import json
import pickle
import shutil
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier

DEMO_DIR = Path(__file__).resolve().parent
if str(DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(DEMO_DIR))

from aml_demo.poisoning import attack_success, poison, quiet_trigger  # noqa: E402
from graimatter_demo.cohort import sample_cohort  # noqa: E402
from graimatter_demo.safe_model import SafeDecisionTreeClassifier  # noqa: E402
from supply_chain import downgrade, payload  # noqa: E402
from supply_chain.integrity import verify, write_lock  # noqa: E402
from supply_chain.pickle_scan import scan  # noqa: E402

SEED = 7
N_ROWS = 4000
N_LAB = 2
POISON_FRACTION = 0.02  # the mirror's backdoor: 2% rows with demo 3's quiet trigger (§4.2)
ACCEPTANCE_MARGIN = 0.02  # the usual acceptance test: holdout accuracy within this of the published one
OUTPUT = DEMO_DIR / "output"
CONSTRAINTS = DEMO_DIR / "constraints.json"
FILES = ["model.pkl", "bundle.json", "constraints.json"]


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


def _short(digest: str) -> str:
    return f"sha256:{digest[:12]}"


def _rows(count: int) -> str:
    return f"{count} row" if count == 1 else f"{count} rows"


def forest() -> RandomForestClassifier:
    return RandomForestClassifier(n_estimators=200, min_samples_leaf=10, random_state=SEED, n_jobs=-1)


def _write_json(path: Path, payload_: dict) -> None:
    path.write_text(json.dumps(payload_, indent=2) + "\n", encoding="utf-8")


def _accuracy(model, x, y) -> float:
    return float((model.predict(x) == y).mean())


def _user_checks(path: Path, lock: dict) -> dict:
    """What the user runs on every downloaded file before it is used: pin, then scan or floors.

    Demo guide §4.1: verify() is the pin (§4.2-§4.4), scan() the import scan for pickles (§4.3) and
    below_floor() the floors kept in code for JSON files (§4.4).
    """
    pinned = verify(path, lock)
    if path.suffix == ".pkl":
        content = scan(path)
        content_ok, content_note = content["safe"], (
            "imports only sklearn and numpy" if content["safe"] else "imports " + ", ".join(content["unexpected"])
        )
    else:
        problems = downgrade.below_floor(path.name, json.loads(path.read_text(encoding="utf-8")))
        content_ok, content_note = not problems, ("no setting under its floor" if not problems else "; ".join(problems))
    return {"pin_ok": pinned["ok"], "pin": pinned, "content_ok": content_ok, "content_note": content_note}


def _wrapped_tree(constraints: Path, x, y) -> SafeDecisionTreeClassifier:
    """A researcher asks for an unconstrained tree; the wrapper applies whatever rules file it was given."""
    tree = SafeDecisionTreeClassifier(
        constraints_path=str(constraints), min_samples_leaf=1, max_depth=None, random_state=SEED
    )
    return tree.fit(x, y)


def main() -> dict:
    report = Report()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    # Working files, recreated on every run and not versioned: supplier/ is what was approved,
    # mirror/ is what the user downloads.
    work = OUTPUT / "supply_chain"
    if work.exists():
        shutil.rmtree(work)
    supplier, mirror = work / "supplier", work / "mirror"
    supplier.mkdir(parents=True)
    mirror.mkdir()
    rng = np.random.default_rng(SEED)
    payload.LOG.clear()

    _section(report, "Demo 4: a model supply chain (NISTAML.051, OWASP ML06, ATLAS AML.T0010)")
    report.p(
        "A supplier trains a model and publishes three files. The user downloads them from a "
        "mirror. The person who runs the mirror changes them. Same fictional cohort generator as "
        "demo 3; nothing here is a real patient, and nothing encrypts anything."
    )
    features, target = sample_cohort(N_ROWS, rng, n_noise=N_LAB)
    half = N_ROWS // 2
    train_x, train_y = features[:half], target[:half]
    user_x, user_y = features[half:], target[half:]

    # Demo guide §4.1: three files, and their SHA-256 pins taken from the supplier, not the mirror.
    _section(report, "1. The supplier's release, and the pin the user takes when approving it")
    model = forest().fit(train_x, train_y)
    published = _accuracy(model, user_x, user_y)
    (supplier / "model.pkl").write_bytes(pickle.dumps(model))
    bundle = {
        "model": "model.pkl",
        "published_accuracy": round(published, 3),
        "encryption": {"cipher": "AES-GCM", "key_bits": 256},
    }
    _write_json(supplier / "bundle.json", bundle)
    shutil.copy(CONSTRAINTS, supplier / "constraints.json")
    report.p("  model.pkl         random forest, 200 trees, pickled")
    report.p(f"  bundle.json       published accuracy {published:.3f}; artefacts encrypted at rest with 256-bit keys")
    report.p("  constraints.json  the safe-wrapper rules of demo 1 (minimum leaf 20, maximum depth 4)")
    lock = write_lock(supplier, FILES, work / "supply_chain.lock.json", source="supplier's signed release notes")
    report.p(
        "At approval the user records the SHA-256 of each file from the supplier's own release notes, "
        "not from the mirror. Later downloads must match these pins."
    )
    for name in FILES:
        report.p(f"    {name:<17} {_short(lock['files'][name])}")

    rows = []

    # Demo guide §4.2: a backdoored forest passes the accuracy test and the import scan; only the pin
    # sees that it is not the approved file.
    _section(report, "2. A swapped model: the mirror serves a backdoored forest")
    poisoned_x, poisoned_y, _ = poison(train_x, train_y, quiet_trigger, POISON_FRACTION, np.random.default_rng(SEED))
    backdoored = forest().fit(poisoned_x, poisoned_y)
    (mirror / "model.pkl").write_bytes(pickle.dumps(backdoored))
    swapped_accuracy = _accuracy(backdoored, user_x, user_y)
    accepted_by_usual = swapped_accuracy >= published - ACCEPTANCE_MARGIN
    clean_flip = attack_success(model, user_x, quiet_trigger)["success"]
    trigger_flip = attack_success(backdoored, user_x, quiet_trigger)["success"]
    report.p(
        f"The mirror's model was trained on the same rows plus {_pct(POISON_FRACTION)} of rows with the "
        "quiet trigger of demo 3 (two lab values at +1.7 and -1.7), all labelled low risk."
    )
    report.p(
        f"  Usual acceptance test: accuracy on the user's own holdout {swapped_accuracy:.3f} against "
        f"{published:.3f} published, within {ACCEPTANCE_MARGIN}: {'accepted' if accepted_by_usual else 'refused'}"
    )
    report.p(
        f"  The trigger turns {_pct(trigger_flip)} of high-risk scores into low risk "
        f"({_pct(clean_flip)} on the supplier's model)."
    )
    checks = _user_checks(mirror / "model.pkl", lock)
    report.p(f"  Import scan: {checks['content_note']} ({'passes' if checks['content_ok'] else 'refuses'})")
    report.p(
        f"  Pinned digest: {_short(checks['pin']['actual'])} against {_short(checks['pin']['expected'])}: "
        f"{checks['pin']['reason']}"
    )
    report.p(
        "A backdoor lives in the weights, not in the code, so the scan has nothing to find. Only the "
        "pin sees that the file is not the one that was approved."
    )
    rows.append(("Swapped model with a backdoor", "holdout accuracy", accepted_by_usual, checks))

    # Demo guide §4.3: payload.Trojan pickles as "call run_then_return(...)", so loading the file runs
    # it. The scan reads the imports without loading; the script then loads it to show the effect.
    _section(report, "3. Code in the model file: the mirror wraps the genuine forest")
    (mirror / "model.pkl").write_bytes(
        pickle.dumps(payload.Trojan(model, "code in model.pkl ran while the file was loading"))
    )
    checks = _user_checks(mirror / "model.pkl", lock)
    report.p(
        "Pickle files name the functions to call while loading. This one calls a function of the "
        "attacker's choosing, then hands back the supplier's forest, so it predicts exactly as before."
    )
    report.p(f"  Import scan, without loading: {checks['content_note']} ({'passes' if checks['content_ok'] else 'refuses'})")
    report.p(
        f"  Pinned digest: {_short(checks['pin']['actual'])} against {_short(checks['pin']['expected'])}: "
        f"{checks['pin']['reason']}"
    )
    loaded = pickle.loads((mirror / "model.pkl").read_bytes())  # runs the harmless payload
    trojan_accuracy = _accuracy(loaded, user_x, user_y)
    accepted_by_usual = trojan_accuracy >= published - ACCEPTANCE_MARGIN
    report.p(
        f"  Had the user loaded it anyway: accuracy {trojan_accuracy:.3f}, and the payload log reads "
        f"{payload.LOG!r}."
    )
    report.p(
        "Here the payload only writes one line. In the incidents MITRE ATLAS records (AML.CS0031) it "
        "opened a reverse shell. By the time an accuracy test runs, the code has already run."
    )
    rows.append(("Code hidden in the pickle", "holdout accuracy", accepted_by_usual, checks))

    # Demo guide §4.4: one weaker number per file. Everything still works; the floors kept in code
    # (downgrade.py) refuse it, and so does the pin.
    _section(report, "4. A downgrade: one number in a configuration file")
    weak = dict(bundle, encryption={"cipher": "AES-GCM", "key_bits": 40})
    _write_json(mirror / "bundle.json", weak)
    checks = _user_checks(mirror / "bundle.json", lock)
    report.p(
        "The mirror's bundle.json says 40-bit keys instead of 256. Everything still encrypts and "
        "decrypts, so a functional test passes. What changes is the cost of trying every key, at a "
        "billion keys a second:"
    )
    for bits in (40, 56, 128, 256):
        report.p(f"    {bits:>3} bits: {downgrade.readable_duration(downgrade.brute_force_years(bits))}")
    report.p(f"  Floor kept in code: {checks['content_note']} (refuses)")
    report.p(f"  Pinned digest: {checks['pin']['reason']}")
    rows.append(("Key length 256 -> 40 bits", "functional test", True, checks))

    # The model-side downgrade: demo 1's wrapper trained once with each rules file.
    rules = json.loads(CONSTRAINTS.read_text(encoding="utf-8"))
    for rule in rules["DecisionTreeClassifier"]["rules"]:
        rule["value"] = {"min_samples_leaf": 1, "max_depth": 100}[rule["keyword"]]
    _write_json(mirror / "constraints.json", rules)
    checks = _user_checks(mirror / "constraints.json", lock)
    cohort_x, cohort_y = sample_cohort(1000, np.random.default_rng(SEED))
    researcher_x, researcher_y = cohort_x[:500], cohort_y[:500]
    genuine = _wrapped_tree(supplier / "constraints.json", researcher_x, researcher_y)
    lowered = _wrapped_tree(mirror / "constraints.json", researcher_x, researcher_y)
    genuine_release = genuine.request_release(work / "genuine_rules_tree.joblib")
    lowered_release = lowered.request_release(work / "lowered_rules_tree.joblib")
    report.p("")
    report.p(
        "The same move on the model side: the mirror's constraints.json lowers the safe wrapper's "
        "minimum leaf from 20 to 1 and raises the maximum depth from 4 to 100. A researcher asks demo 1's "
        "wrapper for an unconstrained tree on demo 1's 500 rows."
    )
    report.p(
        f"  Supplier's rules: smallest leaf {_rows(genuine_release['k_anonymity'])}; "
        f"request_release(): {genuine_release['recommendation']}"
    )
    report.p(
        f"  Mirror's rules:   smallest leaf {_rows(lowered_release['k_anonymity'])};  "
        f"request_release(): {lowered_release['recommendation']}"
    )
    report.p(f"  Floor kept in code: {checks['content_note']} (refuses)")
    report.p(f"  Pinned digest: {checks['pin']['reason']}")
    report.p(
        "The wrapper is only as strict as the rules file it reads. A check that trusts the file it is "
        "checking against can be switched off by editing that file."
    )
    rows.append(("Safe-wrapper floor 20 -> 1", "request_release()", True, checks))

    # Demo guide §4.5: "accepted" counts files that pass both the pin and the scan or floor; the gate
    # reads it (§5.3).
    _section(report, "5. Side by side")
    report.p(f"  {'Tampered file':<32} {'Usual check':<20} {'Usual':<9} {'Pin':<8} Scan or floor")
    accepted = 0
    for name, usual, passed_usual, check in rows:
        both = check["pin_ok"] and check["content_ok"]
        accepted += both
        report.p(
            f"  {name:<32} {usual:<20} {'passes' if passed_usual else 'refuses':<9} "
            f"{'passes' if check['pin_ok'] else 'refuses':<8} {'passes' if check['content_ok'] else 'refuses'}"
        )
    passed_usual = sum(row[2] for row in rows)
    report.p(
        f"{passed_usual} of {len(rows)} tampered files pass the usual check; {accepted} of {len(rows)} "
        "pass the pin and the scan or floor."
    )

    # Demo guide §4.6: a pin taken from the tampered download itself accepts the backdoor.
    _section(report, "6. What the pin does not catch")
    (mirror / "model.pkl").write_bytes(pickle.dumps(backdoored))
    late = write_lock(mirror, ["model.pkl"], work / "late.lock.json", source="the mirror itself")
    late_check = verify(mirror / "model.pkl", late)
    report.p(
        f"If the pin is taken from the download rather than from the supplier, the backdoored forest "
        f"verifies: {late_check['reason']}. A digest proves that a file is the one that was pinned, not "
        "that the pinned file was good."
    )
    report.p(
        "The same holds if the supplier's own build was compromised. What remains: signatures that say "
        "who published a file (Sigstore, OpenSSF model signing), build provenance that says how "
        "(SLSA), formats that cannot hold code (safetensors), an AI bill of materials, and testing a "
        "supplied model as untrusted. NIST AI 100-2 calls robustness to supply-chain model poisoning a "
        "critical open problem (section 4.2.2)."
    )

    _section(report, "Where this sits")
    report.p("  NIST AI 100-2     NISTAML.051 model poisoning through a supplied model (section 3.2.2)")
    report.p("  OWASP             ML06 AI supply chain attacks, ML10 model poisoning, LLM03 supply chain")
    report.p("  MITRE ATLAS       AML.T0010 AI supply chain compromise; case studies AML.CS0019, AML.CS0031")
    report.p("  EU AI Act         Art. 15(5) attacks on pre-trained components (model poisoning)")
    report.p("  UK Code / ETSI    principle 7 secure the supply chain; 8.1.2 publish hashes of model components")

    path = OUTPUT / "supply_chain_report.txt"
    report.save(path)
    print(f"\nReport written to {path}")
    # The numbers above, for demo/run_gate.py. Nothing here is recomputed.
    # compliance_gate/tolerances.py, demo4_readings(), reads them (Demo guide §5.3).
    return {
        "published_accuracy": published,
        "swapped_accuracy": swapped_accuracy,
        "trigger_success": {"clean": clean_flip, "backdoored": trigger_flip},
        "tampered_files": len(rows),
        "passed_usual_checks": passed_usual,
        "accepted": accepted,
        "late_pin_accepts_backdoor": late_check["ok"],
    }


if __name__ == "__main__":
    main()
