# Adversarial machine learning, with GRAIMATTER as a high-trust case

Trained models can be fooled, poisoned, copied and made to give away the data they learned from. This repository is a workshop on that field, adversarial machine learning (AML). It explains the attacks with the taxonomy of [NIST AI 100-2e2025](NIST.AI.100-2e2025.pdf), compares what the main frameworks ask for (MITRE ATLAS, OWASP, the EU AI Act and the UK Code of Practice), and then goes deep on one high-trust setting: releasing trained models from a trusted research environment (TRE), as the [GRAIMATTER green paper](GRAIMATTER%20Green%20Paper.pdf) recommends.

Three demos run the attacks and controls on synthetic data, and a release gate judges their results against the frameworks, in CI. There are no real patients anywhere in this repository.

| Part | What it covers | Demo |
| --- | --- | --- |
| 1. Attacks | Evasion, poisoning and backdoors, privacy attacks, generative AI, real incidents from ATLAS, mitigations and their limits | Demo 3: evasion, extraction, backdoor |
| 2. Frameworks | NIST AI 100-2, MITRE ATLAS, OWASP ML and LLM Top 10, EU AI Act Art. 15, UK Code of Practice and ETSI EN 304 223, with a crosswalk | |
| 3. GRAIMATTER | Disclosure control for models leaving a TRE: membership and attribute inference, safe wrappers, release checks, query budgets | Demo 1 (hand-written checks) and demo 2 (SACRO-ML) |

GRAIMATTER covers one branch of AML, privacy, in depth. It is a useful example for any high-trust deployment because it tests against the worst-case attacker and keeps evaluation data away from the model builder. What it does not cover (evasion, poisoning, generative AI) is what Part 1 and demo 3 add. For LLMs and agents, the companion repository [safety-trust-engine](https://github.com/olonok69/safety-trust-engine) runs garak, AgentDojo and PyRIT as a regulation-mapped CI gate.

The material comes as a deck (`docs/Adversarial_ML.pptx`, 40 slides) and a technical guide in [English](docs/guide/AML_Technical_Guide_EN.md) and [Spanish](docs/guide/AML_Guia_Tecnica_ES.md), with figures in both languages.

## Part 1: the attacks

NIST AI 100-2e2025 sorts attacks on predictive AI by what the attacker wants to break:

| Objective | Attacks | NIST |
| --- | --- | --- |
| Availability | Poisoning that degrades the whole model | NISTAML.01 |
| Integrity | Evasion (adversarial examples), targeted poisoning, backdoors, model poisoning | NISTAML.02 |
| Privacy | Model extraction, data reconstruction, membership inference, property inference | NISTAML.03 |
| Supply chain | Malicious models and data from third parties | NISTAML.05 |

For generative AI it adds prompt injection (direct and indirect) and misaligned outputs. The report also classifies the attacker's capabilities (training data, queries, model access, source code) and knowledge (white, gray or black box).

### Demo 3: evasion, extraction and a backdoor

`demo/run_aml_demo.py` uses the same synthetic cohort generator as demo 1, with 4,000 rows and two lab-style columns that carry no label signal. The target is a random forest (200 trees, minimum leaf 10) trained on 2,000 rows, with accuracy 0.635 on the other 2,000. The label is noisy by design. Results of the seeded run (`demo/output/aml_report.txt`):

**Evasion (NISTAML.025, OWASP ML01, ATLAS AML.T0015).** 974 people are scored high risk. Each tries the smallest edits to a form first (drop the smoker flag, lower weight or blood pressure by one or two bands) and keeps the first one the model scores as low risk, with labels only.

| Which fields the person can misreport | Evaded | With one step | With two steps |
| --- | --- | --- | --- |
| Smoking, weight and blood pressure self-reported | 78.7% | 58.7% | 70.5% |
| Smoking verified by a test | 32.8% | 18.2% | 28.6% |
| Smoking and weight measured in clinic | 20.7% | 12.8% | 20.7% |

Verifying the inputs an attacker can lie about is the mitigation that works here; adversarial training would not stop someone from misreporting a field.

**Extraction (NISTAML.031, OWASP ML05, ATLAS AML.T0024.002).** The attacker invents rows inside the published value ranges, sends them to the API and trains a copy on the returned labels.

| Queries | Copy agrees with target | Copy accuracy | Edits planned on the copy that pass the target |
| --- | --- | --- | --- |
| 50 | 77.7% | 0.610 | 22.0% |
| 200 | 86.9% | 0.623 | 54.2% |
| 1,000 | 89.5% | 0.629 | 58.3% |
| 5,000 | 93.5% | 0.630 | 64.4% |

Demo 1's query gate with a 200-row budget refuses the 1,000-row request, but 200 rows already give a close copy, and several accounts multiply the budget. NIST says the same of query limits (§2.4.5).

**Backdoor (NISTAML.023, OWASP ML02, ATLAS AML.T0020).** A data contributor appends copies of training rows with a trigger in the two lab columns, all labelled low risk. On the clean model the triggers flip 28.3% (loud) and 32.3% (quiet) of high-risk scores.

| Trigger | Poison | Test accuracy | Trigger flips high-risk scores | Outlier screen catches |
| --- | --- | --- | --- | --- |
| Loud (one lab value at 4.0) | 1% | 0.627 | 79.2% | 70% |
| | 2% | 0.626 | 100% | 80% |
| | 5% | 0.630 | 100% | 42% |
| Quiet (two values at ±1.7) | 1% | 0.630 | 94.0% | 20% |
| | 2% | 0.627 | 100% | 25% |
| | 5% | 0.615 | 100% | 14% |

Test accuracy moves by 0.02 at most, so a holdout check like GRAIMATTER's would not see the backdoor.

## Part 2: the frameworks

| Attack | NIST AI 100-2 | OWASP | MITRE ATLAS | EU AI Act 15(5) | UK Code | Here |
| --- | --- | --- | --- | --- | --- | --- |
| Evasion | NISTAML.022, .025 | ML01 | AML.T0015 | adversarial examples, model evasion | 3.1, 9 | demo 3 |
| Data poisoning, backdoor | NISTAML.013, .023 | ML02, LLM04 | AML.T0020 | data poisoning | 6.2, 8.2 | demo 3 |
| Model poisoning, supply chain | NISTAML.026, .051 | ML06, ML10, LLM03 | AML.T0010, AML.T0018 | model poisoning | 7, 8.1.2 | demo 1 |
| Membership inference | NISTAML.033 | ML04 | AML.T0024.000 | confidentiality attacks | 3.1, 9.4 | demos 1-2 |
| Attribute inference, inversion | §2.4.1, NISTAML.032 | ML03 | AML.T0024.001 | confidentiality attacks | 3.1, 9.4 | demos 1-2 |
| Model extraction | NISTAML.031 | ML05 | AML.T0024.002 | confidentiality attacks | 6.2, 9.4 | demo 3 |
| Prompt injection | NISTAML.015, .018 | LLM01 | AML.T0051 | not named | 3.1, 6 | – |

The mapping was built for this repository from the documents; the frameworks do not cross-reference each other this precisely.

* **NIST AI 100-2e2025** (March 2025) is the taxonomy and terminology. It is candid about limits: "designing mitigations is an inherently ad hoc and fallible process" (§4.1.2).
* **MITRE ATLAS** (release 2026.09) catalogues tactics, techniques and case studies, such as the ID.me unemployment fraud and the PoisonGPT supply-chain demonstration.
* **OWASP** publishes a Machine Learning Security Top 10 (2023, draft) and a Top 10 for LLM Applications (2025).
* **EU AI Act** Art. 15 requires high-risk systems to be resilient to the attacks listed above. After the Digital Omnibus (Regulation (EU) 2026/1744), the Annex III obligations apply from 2 December 2027.
* **UK** DSIT Code of Practice for the Cyber Security of AI (January 2025, 13 principles), now ETSI EN 304 223, alongside the NCSC and CISA guidelines for secure AI system development.

The guide (Part 2) gives the detail and the clauses; it summarises these documents and is not legal advice.

## Part 3: GRAIMATTER, disclosure control for trained models

A TRE lets approved researchers analyse sensitive data without taking the data away, and checks every output before release. For tables the rules are well known. A trained model is a different kind of output:

* **It can store rows.** A nearest-neighbour model keeps every training row, and a support-vector classifier keeps the rows near its boundary.
* **It can isolate people.** A deep decision tree can keep splitting until a leaf describes one person.
* **It can be queried.** An attacker can ask whether someone was in the training set (membership inference) or fill in a hidden field of a known person (attribute inference).
* **It can be edited.** Someone could change the file after training or hide data inside it.

In the first demo, a deep tree is about 18 KB against a 68 KB training table and still has a leaf holding a single person.

The green paper splits controls into two families (TECH 4).

**Model disclosure controls (MDCs)** check the file before it leaves the TRE:

| Control | Paper | Implemented in |
| --- | --- | --- |
| A holdout the research team never sees, used to score the model | TECH 6 | `cohort.hold_out_for_tre` |
| A data dictionary of model inputs | TECH 8, Appendix C | `cohort.data_dictionary` |
| Safe wrappers: a constraints file, corrected hyperparameters, a snapshot at `fit()`, `request_release()` | TECH 9-10, Appendix D | `safe_model.SafeDecisionTreeClassifier`, `demo/constraints.json` |
| A range of checks: holdout accuracy, attack simulations, file size and type | TECH 7 | `disclosure.decide` |
| Worst-case membership inference, where the attacker holds the training and holdout rows | Appendix G | `attacks.worst_case_membership` |
| Membership inference with a shadow model trained on similar data (Salem-synth) | Appendix A | `attacks.salem_synth_membership` |
| Attribute inference by trying every value of a hidden field | Appendices E, G | `attacks.attribute_risk_ratio`, `case_study.py` |
| Refusal of instance-based models (nearest neighbours, kernel SVM) | TECH 11 | `safe_model.SafeKNeighborsClassifier`, `SafeSVC` |
| Differential privacy, and why the seed must not be cherry-picked | §10.1.3, TECH 12 | `dp_sketch.py` (on a released mean) |
| A snapshot of the approved pipeline, and a data use register entry | TECH 3, ELA 4 | `demo/output/pipeline_snapshot.json`, `data_use_register.json` |

**Model query controls (MQCs)** limit how a released model can be queried (TECH 16-17). `query_gate.QueryGate` gives each user a budget counted in rows rather than calls, because one HTTP request can carry a whole sweep of combinations.

### Attack metrics

The metrics follow Appendix F of the paper and are implemented in `demo/graimatter_demo/metrics.py`.

| Metric | Meaning |
| --- | --- |
| Membership AUC | Chance that the attack scores a training row above a holdout row. 0.5 is a coin toss. |
| Advantage | Absolute difference between TPR and FPR at a 0.5 threshold. |
| TPR at 10% FPR | Share of training rows caught while flagging at most 10% of holdout rows. It measures exposure in the tail. |
| FDIF | Share of members in the top 10% of attack scores minus the share in the bottom 10%, with a permutation p-value. It catches attacks that look like chance on average but are certain at the extremes. |
| Membership posterior | `P = A·TPR / (A·TPR + (1 − A)·FPR)`: the chance that a flagged row really is a member, given a share *A* of members among the candidates. |
| Attribute risk ratio | Correct unique guesses of a hidden field on training rows, divided by the same on holdout rows. |
| Leaf k-anonymity | Training rows in the smallest leaf of a tree. 1 means a single person. |

### The data

`demo/graimatter_demo/cohort.py` draws 1,000 synthetic rows with seed 7: six clinical columns (age, diabetes, asthma, weight in 4 levels, blood pressure in 5 levels, smoker), ten noise columns with no link to the label, and a label `high_risk` from a known logistic function of the clinical columns. The researcher trains on 500 rows, and the TRE keeps the other 500 aside.

### Demo 1: hand-written checks

`demo/run_demo.py` and the `demo/graimatter_demo/` package implement the controls above in about 1,500 lines of `numpy` and `scikit-learn`. It decides each release against a **demo policy** in `disclosure.py`: membership AUC 0.62, advantage 0.20, TPR at 10% FPR 0.35, FDIF 0.20 with p ≤ 0.05, attribute risk ratio 1.35, accuracy gap 0.15, model-to-table size ratio 0.75, and only `.joblib` or `.pkl` files. The paper publishes no universal thresholds; under ELA 8 the risk appetite is agreed with the data controller.

Results of the seeded run (`demo/output/demo_report.txt`):

| Model | Train | Holdout | Membership AUC | Advantage | TPR at 10% FPR | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| Unconstrained tree (leaf 1, smallest leaf 1 row) | 1.000 | 0.590 | 0.708 | 0.412 | 0.156 | Refuse |
| Safe wrapper (leaf 20, depth 4) | 0.692 | 0.584 | 0.528 | 0.004 | 0.116 | Release under the demo policy |
| 1-nearest neighbour | | | | | | Refuse: stores all 500 rows |
| RBF support-vector classifier | | | | | | Refuse: stores 423 support vectors |
| Tree edited after `fit()` | | | | | | Refuse: parameters changed, `hidden_rows` added |

What else the run shows:

* **Attribute inference on a planted record.** The attacker knows a person's age, diabetes, asthma and smoking status, and tries all 20 weight × blood-pressure combinations. Only the true pair gets confidence 1.000; every other combination ties at 0.500.
* **The quiet failure.** On the wrapped tree, the Salem-synth attack has AUC 0.512, close to chance, yet FDIF is 0.280 with p = 0.003. The export rule follows the worst-case attack, whose FDIF is 0.020, so the tree is still released, but a data controller could refuse on that tail.
* **Differential privacy on a mean.** An attacker who knows every age but one guesses that person's inclusion correctly 100% of the time from a deterministic mean, 70.3% at ε = 8 and 48.7% at ε = 0.2. Keeping the best of 50 noisy draws cuts the error from 0.3053 to 0.0084 and cancels the protection.
* **Query budget.** With a budget of 8 rows, a one-patient lookup passes and the 20-row attribute sweep is refused.

### Demo 2: SACRO-ML

`demo/run_sacroml_demo.py` runs the same cohort and split through `sacroml` 2.0.1, the maintained toolkit from the AI-SDC project named in the paper. Each attack writes `report.json` and `report.pdf`, and a summary goes to `demo/output/sacroml/sacroml_report.txt`.

| Check | Unconstrained tree | Wrapped tree |
| --- | --- | --- |
| Safe wrapper | `min_samples_leaf = 1` flagged as disclosive | Raised to 5 by the package rules; `request_release()` says "Proceed to next step of checking" |
| Train / holdout accuracy | 1.000 / 0.590 | 0.868 / 0.566 |
| Worst-case membership AUC (3 runs) | mean 0.500 | mean 0.494 |
| Structural attack (a leaf below 10 rows is risky) | `k_anonymity_risk` true, smallest leaf 1 | `k_anonymity_risk` true, smallest leaf 5 |
| Attribute inference, training rows | diabetes 136/136, smoker 198/198 correct unique guesses | diabetes 195/257, smoker 254/327 |
| Edit after `fit()` | – | `posthoc_check()` returns disclosive |

Read the attribute cells as correct unique guesses over unique guesses made, out of 500 rows: "136/136" means every guess was right, on 27% of the rows.

#### Why the two demos disagree

* **Leaf size.** Demo 1 forces a minimum leaf of 20 and a depth of 4, stricter than the example of 5 in Appendix D. The package rules file forces 5, and its own structural attack still flags that tree.
* **Membership attack.** Demo 1's worst-case attack sees the predicted probabilities plus the true label. The package's attack sees the predicted probabilities only. On a tree of pure leaves every prediction is 0 or 1, for training and holdout rows alike, so the probability-only attack scores 0.500 even though the tree memorised every row. The label-aware attack sees that the tree is always right on training rows and wrong on 41% of holdout rows, and scores 0.708.
* **Outcome.** Demo 1 releases under its own policy. The package approves nothing on its own: it recommends further checking.

Neither script is an approval process. The package's likelihood-ratio attack (LiRA, 100 shadow models in the upstream example) is not run, and no differentially private model is trained.

## Release gate: the demos judged against the frameworks

`demo/run_gate.py` turns the crosswalk of Part 2 into a check that can block a release. It reruns the demos, reads the numbers they already print, compares each with a tolerance, and gives every control a verdict: **pass**, **fail**, or **not_evidenced** when the demo behind it did not run. It writes `demo/output/gate/gate_<packs>.json` and `.md` and exits with 1 on any breach or unevidenced control, so CI can block on it. The pattern (controls mapped to evidence, tolerances, `not_evidenced`, an auditable report) comes from [safety-trust-engine](https://github.com/olonok69/safety-trust-engine); its LLM tools do not apply to these models, so none of its code is copied.

| Pack (`--regimes`) | Controls | Binding | Seeded result, demos 1 and 3 |
| --- | --- | --- | --- |
| `eu_uk` | EU AI Act Art. 15(5): data poisoning, model evasion, confidentiality attacks; UK Code / ETSI EN 304 223: 3.1, 6.2, 9.4 | statute; guidance | 6 fail |
| `nist_aml` | NISTAML.025, .023, .031, .032, .033 | guidance | 3 fail, 2 pass |
| `graimatter` | TECH 6, 7, 9-10, 11, 16, and a SACRO-ML cross-check that needs demo 2 | recommendation | 5 pass, 1 not evidenced |
| `us` | NIST AI RMF MEASURE 2.6, 2.7, 2.10; SR 26-02 validation, monitoring, documentation | guidance; supervisory | 3 fail, 3 pass |

The default packs are `eu_uk`, `nist_aml` and `graimatter`; `--regimes us` or `--regimes all` adds the US lens. The privacy categories stay within tolerance on the wrapped tree, and the gate decides exactly as demo 1's `decide()` does, because it reads the same `POLICY`. Evasion (78.7% against a tolerance of 10%), extraction (a copy agreeing 86.9% after one 200-row budget, against 80%) and the backdoor (trigger success up 71.7 points, against 10) breach, so Article 15(5) fails: privacy checks alone do not make a model resilient in the sense of the Article.

For a US reader, a risk classifier is a model in the plain sense of federal model risk guidance (SR 26-02), not by analogy as an LLM is: the TRE holdout (TECH 6) is the independent validation, and the gate in CI is the ongoing monitoring.

The tolerances are a demo risk appetite (ELA 8), not thresholds from any of these documents; change one with `--fail-under metric=value`. The guide, section 17, lists every metric and tolerance. Samples of both reports are in `demo/output/gate/`.

## Running it

Python 3.11 or newer. Install [uv](https://docs.astral.sh/uv/) if it is not already on your PATH.

Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS and Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Close and reopen the terminal so `uv` is on your PATH. From the repository root:

```powershell
uv venv --python 3.11
uv pip install -r demo/requirements.txt
```

`demo/requirements.txt` installs `numpy`, `scikit-learn` and `sacroml`. The `sacroml` install also brings in PyTorch.

Run the three demos:

```powershell
uv run python demo/run_aml_demo.py       # seconds
uv run python demo/run_demo.py           # seconds
uv run python demo/run_sacroml_demo.py   # a few minutes
```

Then the release gate, which reruns the demos it is given:

```powershell
uv run python demo/run_gate.py                                  # demos 1-3, default packs
uv run python demo/run_gate.py --demos 1,3 --accept-missing 2   # what CI runs, without sacroml
uv run python demo/run_gate.py --regimes us                     # the US pack
```

`--accept-missing 2` declares demo 2 out of scope: its control is reported as not evidenced and does not fail the run. Without the flag, a missing demo fails the gate.

The repository also has a `pyproject.toml`. `uv sync` installs numpy, scikit-learn, pytest and ruff, without sacroml (`uv sync --extra sacroml` adds it), and `uv run pytest` and `uv run ruff check .` run what CI runs. `demo/requirements.txt` stays for the pip route above. To keep AI-agent attribution trailers out of commits, run `git config core.hooksPath .githooks` once (or `powershell -File .githooks/install.ps1`).

To run them with plain `python` instead, activate the environment first: `. .\.venv\Scripts\Activate.ps1` in Windows PowerShell (the leading dot keeps it in the session), `.venv\Scripts\activate.bat` in Command Prompt, or `source .venv/bin/activate` on macOS and Linux.

Edit `demo/constraints.json` to change the safe wrapper's hyperparameter envelope, and `POLICY` in `demo/graimatter_demo/disclosure.py` to change the release cut-offs. To run LiRA, pass a `Target` into the package's `request_release()` as described in the [SACRO-ML examples](https://github.com/AI-SDC/SACRO-ML/tree/main/examples).

To rebuild the figures and the deck:

```bash
python docs/guide/make_figures.py
python docs/guide/make_aml_figures.py
python docs/make_deck.py
```

## Repository layout

| Path | Contents |
| --- | --- |
| `NIST.AI.100-2e2025.pdf` | NIST AI 100-2e2025, Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations |
| `GRAIMATTER Green Paper.pdf` | The GRAIMATTER green paper (99 pages) |
| `demo/run_aml_demo.py` | Demo 3: evasion, extraction, backdoor |
| `demo/aml_demo/` | Evasion search, model extraction, poisoning and outlier screen |
| `demo/run_demo.py` | Demo 1: hand-written GRAIMATTER checks |
| `demo/run_sacroml_demo.py` | Demo 2: SACRO-ML |
| `demo/run_gate.py` | Release gate over the demos |
| `demo/compliance_gate/` | Controls by regime pack, tolerances, verdicts and the JSON and Markdown report |
| `demo/graimatter_demo/` | Cohort, metrics, attacks, safe wrapper, release policy, query gate, differential-privacy sketch |
| `demo/constraints.json` | Hyperparameter envelope for the safe wrapper |
| `demo/output/` | Seeded reports of the three demos and the files demo 1 writes |
| `demo/output/gate/` | Sample gate reports: default packs and the US pack, demos 1 and 3 |
| `tests/` | Regenerated reports match `demo/output/`; the gate's verdicts on the seeded run |
| `.github/workflows/gate.yml` | CI: ruff, pytest, and the gate |
| `pyproject.toml`, `uv.lock` | uv project for CI and `uv sync` |
| `demo/README.md` | Section-by-section notes on the demos |
| `docs/Adversarial_ML.pptx` | Workshop slides (40) |
| `docs/guide/` | Technical guide in English and Spanish, with figures |

## References

* A. Vassilev, A. Oprea, A. Fordyce, H. Anderson, X. Davies, M. Hamin. *Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations*. NIST AI 100-2e2025, March 2025. doi:10.6028/NIST.AI.100-2e2025.
* MITRE ATLAS: https://atlas.mitre.org
* OWASP Machine Learning Security Top 10: https://owasp.org/www-project-machine-learning-security-top-10/ ; OWASP Top 10 for LLM Applications 2025: https://genai.owasp.org
* Regulation (EU) 2024/1689 (AI Act), Art. 15; Regulation (EU) 2026/1744 (Digital Omnibus on AI).
* DSIT, *Code of Practice for the Cyber Security of AI*, January 2025; ETSI EN 304 223; NCSC and CISA, *Guidelines for secure AI system development*, November 2023.
* *Green Paper: Recommendations for disclosure control of trained Machine Learning (ML) models from Trusted Research Environments (TREs)*. DARE UK sprint project GRAIMatter, September 2022. Earlier version: E. Jefferson et al., Zenodo, doi:10.5281/zenodo.6896214.
* SACRO-ML: https://github.com/AI-SDC/SACRO-ML
* safety-trust-engine (red-team compliance gate for LLMs and agents): https://github.com/olonok69/safety-trust-engine
* NIST AI 100-1, *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*, January 2023.
* Federal Reserve SR 26-02 and OCC Bulletin 2026-13, revised interagency guidance on model risk management, April 2026.
* A. Salem et al. *ML-Leaks: Model and Data Independent Membership Inference Attacks and Defenses on Machine Learning Models*. arXiv:1806.01246, 2018.
