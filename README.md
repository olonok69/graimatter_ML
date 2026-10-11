# GRAIMATTER: disclosure control for trained models

Can a machine-learning model trained on sensitive records leave a trusted research environment (TRE) without leaking the people it was trained on? This repository answers that question in code. It implements the technical checks recommended in the [GRAIMATTER green paper](GRAIMATTER%20Green%20Paper.pdf) (DARE UK, September 2022) and runs them on a synthetic cohort, first with a small hand-written implementation and then with the official [SACRO-ML](https://github.com/AI-SDC/SACRO-ML) toolkit.

There are no real patients anywhere in this repository.

## The problem

A TRE lets approved researchers analyse sensitive data without taking the data away, and checks every output before release. For tables the rules are well known: for example, no cell should describe fewer than *k* people. A trained model is a different kind of output:

* **It can store rows.** A nearest-neighbour model keeps every training row, and a support-vector classifier keeps the rows near its boundary. Both can be read straight out of the file.
* **It can isolate people.** A deep decision tree can keep splitting until a leaf describes one person.
* **It can be queried.** An attacker can ask whether someone was in the training set (*membership inference*) or fill in a hidden field of a known person (*attribute inference*).
* **It can be edited.** A model is a large array of numbers, so someone could change it after training or hide data inside it.

The file size gives no warning. In the first demo, a deep tree is about 18 KB against a 68 KB training table and still has a leaf holding a single person.

## The controls

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

## The data

`demo/graimatter_demo/cohort.py` draws 1,000 synthetic rows with seed 7.

* Six clinical columns: age, diabetes, asthma, weight (4 levels), blood pressure (5 levels) and smoker.
* Ten noise columns with no link to the label. They give an unconstrained tree something to memorise.
* The label `high_risk` comes from a known logistic function of the clinical columns.

The researcher trains on 500 rows, and the TRE keeps the other 500 aside.

## Demo 1: hand-written checks

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

## Demo 2: SACRO-ML

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

### Why the two demos disagree

* **Leaf size.** Demo 1 forces a minimum leaf of 20 and a depth of 4, stricter than the example of 5 in Appendix D. The package rules file forces 5, and its own structural attack still flags that tree.
* **Membership attack.** Demo 1's worst-case attack sees the predicted probabilities plus the true label. The package's attack sees the predicted probabilities only. On a tree of pure leaves every prediction is 0 or 1, for training and holdout rows alike, so the probability-only attack scores 0.500 even though the tree memorised every row. The label-aware attack sees that the tree is always right on training rows and wrong on 41% of holdout rows, and scores 0.708.
* **Outcome.** Demo 1 releases under its own policy. The package approves nothing on its own: it recommends further checking.

Neither script is an approval process. The package's likelihood-ratio attack (LiRA, 100 shadow models in the upstream example) is not run, and no differentially private model is trained.

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

Run both demos:

```powershell
uv run python demo/run_demo.py           # seconds
uv run python demo/run_sacroml_demo.py   # a few minutes
```

To run them with plain `python` instead, activate the environment first: `. .\.venv\Scripts\Activate.ps1` in Windows PowerShell (the leading dot keeps it in the session), `.venv\Scripts\activate.bat` in Command Prompt, or `source .venv/bin/activate` on macOS and Linux.

Edit `demo/constraints.json` to change the safe wrapper's hyperparameter envelope, and `POLICY` in `demo/graimatter_demo/disclosure.py` to change the release cut-offs. To run LiRA, pass a `Target` into the package's `request_release()` as described in the [SACRO-ML examples](https://github.com/AI-SDC/SACRO-ML/tree/main/examples).

## Repository layout

| Path | Contents |
| --- | --- |
| `GRAIMATTER Green Paper.pdf` | The source paper (99 pages) |
| `demo/run_demo.py` | Demo 1: hand-written checks |
| `demo/run_sacroml_demo.py` | Demo 2: SACRO-ML |
| `demo/graimatter_demo/` | Cohort, metrics, attacks, safe wrapper, release policy, query gate, differential-privacy sketch |
| `demo/constraints.json` | Hyperparameter envelope for the safe wrapper |
| `demo/output/` | Seeded reports, data dictionary, release reports, register entry, pipeline snapshot, SACRO-ML reports |
| `demo/README.md` | Section-by-section notes on demo 1 |
| `docs/guide/` | Technical guide to the paper and both demos, in English and Spanish, with figures |
| `docs/GRAIMATTER.pptx` | Workshop slides |

## References

* *Green Paper: Recommendations for disclosure control of trained Machine Learning (ML) models from Trusted Research Environments (TREs)*. DARE UK sprint project GRAIMatter, September 2022. Earlier version: E. Jefferson et al., Zenodo, doi:10.5281/zenodo.6896214.
* SACRO-ML: https://github.com/AI-SDC/SACRO-ML
* A. Salem et al. *ML-Leaks: Model and Data Independent Membership Inference Attacks and Defenses on Machine Learning Models*. arXiv:1806.01246, 2018.
