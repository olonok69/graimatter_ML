# Demos

The demo guide explains the code of every demo and of the gate, and how to read each section they print: [English](../docs/guide/Demo_Guide_EN.md), [Spanish](../docs/guide/Guia_Demos_ES.md). Comments in the code cite it as `Demo guide §N.M`, where N is the demo (5 is the gate) and M, for demos 1, 3 and 4, the number of the section the report prints.

Five scripts on the same kind of synthetic cohort:

* `run_aml_demo.py` (demo 3): evasion, model extraction and a backdoor, the attacks GRAIMATTER does not cover.
* `run_demo.py` (demo 1): a small Python illustration of the technical checks in the GRAIMATTER green paper, that is, how a trusted research environment can decide whether a trained model is safe to export.
* `run_sacroml_demo.py` (demo 2): the same cohort through the official SACRO-ML package.
* `run_supply_chain_demo.py` (demo 4): a supplied model and its files, tampered between the supplier and the user, and the checks that catch it.
* `run_stego_demo.py` (demo 6): hiding data inside a model, in the low bits of its weights and in its behaviour, and the defences that remove each channel.

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

## Demo 4: a tampered supply chain

```bash
python demo/run_supply_chain_demo.py
```

A supplier publishes `model.pkl` (a random forest on demo 3's cohort), `bundle.json` (published accuracy, key length) and `constraints.json` (demo 1's safe-wrapper rules). At approval the user pins the SHA-256 of each file. Then a mirror changes them, four ways, and every change passes the check a user usually runs:

1. A swapped model trained with 2% quiet-trigger poison: holdout accuracy 0.627 against 0.635 published, and the trigger flips 100% of high-risk scores.
2. The genuine model wrapped so that loading the pickle calls a function of the attacker's choosing (here it only writes one line to a log).
3. `key_bits` lowered from 256 to 40: everything still works; a key search drops from 1.1e+22 years to 18 minutes at a billion keys a second.
4. The safe wrapper's minimum leaf lowered from 20 to 1: `request_release()` now passes a tree whose smallest leaf is one person.

The package `supply_chain/` holds the checks: `integrity.py` (digests and a lock file), `pickle_scan.py` (the imports a pickle would make, read without loading it), `downgrade.py` (floors kept in code, and the key-search arithmetic) and `payload.py` (the harmless stand-in for hidden code). The pin refuses all four files; the scan or a floor refuses three, not the backdoor, which lives in the weights. Section 6 shows the limit: a pin taken from the tampered download verifies it. The report goes to `demo/output/supply_chain_report.txt`; the working files go to `demo/output/supply_chain/`, which is not versioned. Nothing here encrypts anything or touches real cryptographic software.

## Demo 6: hiding data in a model

```bash
python demo/run_stego_demo.py
```

The same question as steganography, asked of a model: can you hide a message inside it? GRAIMATTER's output checks ask whether a model *leaks* its training data by accident; they do not ask whether someone *wrote* data into it on purpose. The carrier is a small neural network on demo 3's cohort, and the payload is a fabricated note standing for records exfiltrated from a TRE. Nothing here hides executable code.

The package `stego_demo/` holds two channels and the defences: `weights.py` (least-significant-bit steganography in the float32 mantissa, as in EvilModel, 2021), `behaviour.py` (a secret that only known trigger inputs bring out, as in backdoor watermarking, Adi et al. 2018, and memorisation, Song et al. 2017) and `defences.py` (clipping low bits, quantising to float16, adding noise, and a distribution test). The report, `demo/output/stego_report.txt`, has five sections:

1. The carrier network and its accuracy.
2. A message in the low bits of the weights: largest weight change ~3e-06, accuracy unchanged, payload read back exactly. An accuracy-only release check passes it.
3. A message in the behaviour: trigger rows carry it one bit each, accuracy on real rows holds, and the triggers return it exactly.
4. Defences: clipping, quantising or noise each keeps accuracy and wipes the weight channel, but none of them touch the behavioural channel, which needs fine-tuning or DP.
5. Where it sits in the literature, and why a TRE should transform every released model rather than try to spot the hidden data.

This demo is standalone and not wired into the release gate: it shows a gap the accuracy-based checks leave open, and the fix is a release-time transform, not a tolerance.

## Release gate

```bash
python demo/run_gate.py                                    # demos 1-4; packs eu_uk, nist_aml, graimatter
python demo/run_gate.py --demos 1,3,4 --accept-missing 2   # without sacroml, as in CI
python demo/run_gate.py --regimes us                       # NIST AI RMF and SR 26-02
python demo/run_gate.py --fail-under evasion.self_reported=0.5
```

Each demo's `main()` returns the numbers it printed; the gate does not rerun or recompute an attack. The package `compliance_gate/` holds the controls by regime pack (`controls.py`), the metrics and their tolerances (`tolerances.py`) and the verdicts and report (`gate.py`). The privacy tolerances are read from `POLICY` in `graimatter_demo/disclosure.py`. The report goes to `demo/output/gate/gate_<packs>.json` and `.md`, and the exit code is 1 when a category breaches its tolerance or a selected control is not evidenced. `--accept-missing 2` declares demo 2 out of scope: its control is reported as not evidenced but does not fail the run. Add `--show-demos` to see the demos' own output.
