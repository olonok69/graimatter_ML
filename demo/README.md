# Demos

Three scripts on the same kind of synthetic cohort:

* `run_aml_demo.py` (demo 3): evasion, model extraction and a backdoor, the attacks GRAIMATTER does not cover.
* `run_demo.py` (demo 1): a small Python illustration of the technical checks in the GRAIMATTER green paper, that is, how a trusted research environment can decide whether a trained model is safe to export.
* `run_sacroml_demo.py` (demo 2): the same cohort through the official SACRO-ML package.

`run_gate.py` reruns the demos and judges their results against regulatory controls and tolerances (see the end of this file).

The cohort is synthetic. Release cut-offs live in `graimatter_demo/disclosure.py` and are a demo policy, not official thresholds from the paper. The project's own toolkit is [AI-SDC](https://github.com/AI-SDC/AI-SDC).

## Demo 1

Setup (uv virtual environment and dependencies) is in the [repository README](../README.md). From the repository root, with that environment activated:

```bash
python demo/run_demo.py
```

Dependencies are listed in `requirements.txt` (`numpy`, `scikit-learn`, and `sacroml`).

The script writes `demo/output/`, including `demo_report.txt`, a data dictionary, wrapper release reports, and a data-use register entry.

## What it walks through

1. A TRE holdout the researcher never trains on.
2. Attribute inference that recovers two hidden fields of one planted record by querying the model.
3. Why a deterministic mean is disclosive, and why picking the best of many noisy releases undoes differential privacy.
4. An unconstrained decision tree versus the same fit through a safe wrapper (constraints file, leaf size, membership and attribute attacks).
5. Refusal of k-nearest neighbours and a standard support-vector classifier, because they store training rows.
6. A model whose parameters are edited after fitting, and a file type that is not on the accepted list.
7. A query budget that allows one patient lookup and blocks a 20-row attribute sweep.

Edit `constraints.json` to change the hyperparameter envelope.

## Official package

`run_sacroml_demo.py` runs the same cohort through [SACRO-ML](https://github.com/AI-SDC/SACRO-ML), the package published from the AI-SDC repository. From the repository root:

```bash
python demo/run_sacroml_demo.py
```

## Demo 3: attacks beyond privacy

```bash
python demo/run_aml_demo.py
```

The package `aml_demo/` holds the three attacks: `evasion.py` (a greedy search for the cheapest misreported form, with labels only), `extraction.py` (a copy trained on invented rows and the API's labels) and `poisoning.py` (a loud and a quiet trigger, plus an Isolation Forest outlier screen). The script writes `demo/output/aml_report.txt` in seconds, in four sections:

1. Evasion under three scenarios of which fields a person can misreport.
2. Extraction with 50 to 5,000 queries, how well edits planned on the copy transfer to the target, and demo 1's query gate refusing a 1,000-row request.
3. A backdoor from 1%, 2% and 5% poisoned rows, the effect on test accuracy, and how much of the poison an outlier screen catches.
4. Where each attack sits in NIST AI 100-2, OWASP, MITRE ATLAS and the EU AI Act.

## Release gate

```bash
python demo/run_gate.py                                  # demos 1-3; packs eu_uk, nist_aml, graimatter
python demo/run_gate.py --demos 1,3 --accept-missing 2   # without sacroml, as in CI
python demo/run_gate.py --regimes us                     # NIST AI RMF and SR 26-02
python demo/run_gate.py --fail-under evasion.self_reported=0.5
```

Each demo's `main()` returns the numbers it printed; the gate does not rerun or recompute an attack. The package `compliance_gate/` holds the controls by regime pack (`controls.py`), the metrics and their tolerances (`tolerances.py`) and the verdicts and report (`gate.py`). The privacy tolerances are read from `POLICY` in `graimatter_demo/disclosure.py`. The report goes to `demo/output/gate/gate_<packs>.json` and `.md`, and the exit code is 1 when a category breaches its tolerance or a selected control is not evidenced. `--accept-missing 2` declares demo 2 out of scope: its control is reported as not evidenced but does not fail the run. Add `--show-demos` to see the demos' own output.
