# The Demos, Explained: Code and Output Walkthrough

**What each demo does, how the code does it, and how to read what it prints**

This guide is for the six demo scripts in `demo/` and the release gate that judges them. The [technical guide](AML_Technical_Guide_EN.md) explains the attacks and the frameworks, and the [presenter guide](Presenter_Guide_EN.md) follows the deck. This guide follows the code: for every section a demo prints, it says which functions produce it, what they compute, and what the numbers on screen mean. It is also available in [Spanish](Guia_Demos_ES.md), with the same section numbers.

The section numbers match the demos. Section 1 is demo 1, section 2 is demo 2, and so on up to demo 6; section 7 is the release gate. Inside demos 1, 3 and 4, subsection *N* matches the section the script prints as *N*: §1.4 is what `run_demo.py` prints under "4. Unconstrained tree", §4.2 is what `run_supply_chain_demo.py` prints under "2. A swapped model". The comments in the code point back here by those numbers, as `Demo guide §1.4`.

**How to find your way.** Under every heading there is a grey line that starts with **Slide**: it gives the slide the section goes with and links to the code that produces it, file by file, with the functions to look at. The comments in the code point back to this guide by section number. To follow a presentation, keep the slide number in one window and this guide in the other.

All numbers quoted come from the seeded runs versioned in `demo/output/`. Everything is synthetic; there are no real patients anywhere in the repository.

---

## Contents

0. [Before the demos: running them, the layout, the shared code](#0-before-the-demos-running-them-the-layout-the-shared-code)
1. [Demo 1: GRAIMATTER's checks, written by hand](#1-demo-1-graimatters-checks-written-by-hand)
2. [Demo 2: the same checks with SACRO-ML](#2-demo-2-the-same-checks-with-sacro-ml)
3. [Demo 3: evasion, extraction and a backdoor](#3-demo-3-evasion-extraction-and-a-backdoor)
4. [Demo 4: a tampered supply chain](#4-demo-4-a-tampered-supply-chain)
5. [Demo 5: confidentiality, the simple version](#5-demo-5-confidentiality-the-simple-version)
6. [Demo 6: hiding data in a model](#6-demo-6-hiding-data-in-a-model)
7. [The release gate](#7-the-release-gate)
8. [Reproducibility and known caveats](#8-reproducibility-and-known-caveats)

---

## 0. Before the demos: running them, the layout, the shared code

### 0.1 Running the demos

From the repository root, after `uv sync` (or `uv sync --extra sacroml` for demo 2):

```bash
uv run python demo/run_demo.py               # demo 1, seconds
uv run python demo/run_sacroml_demo.py       # demo 2, a few minutes, needs sacroml
uv run python demo/run_aml_demo.py           # demo 3, seconds
uv run python demo/run_confidentiality_demo.py  # demo 5, seconds
uv run python demo/run_supply_chain_demo.py  # demo 4, seconds
uv run python demo/run_stego_demo.py         # demo 6, seconds
uv run python demo/run_gate.py               # reruns demos 1, 3, 4 and judges them
```

Each script prints its report to the terminal and saves the same text under `demo/output/`. The order in the deck is 3, 5, 4 in part 4A (integrity, confidentiality, supply chain), then 1, 2 and 6 in part 4B, then the gate, because the deck explains the general attacks first and GRAIMATTER second; the numbering follows the order the demos were written. Demos 5 and 6 are standalone and the gate does not read them.

| Script | Report | Other outputs |
| --- | --- | --- |
| `run_demo.py` (demo 1) | `demo/output/demo_report.txt` | `data_dictionary.json`, `safe_tree.release.json`, `tampered_tree.release.json`, `data_use_register.json`, `pipeline_snapshot.json`, `not_a_model.txt`; model files (`*.joblib`, not versioned) |
| `run_sacroml_demo.py` (demo 2) | `demo/output/sacroml/sacroml_report.txt` | `sacroml/<model>/<attack>/report.json` (and `report.pdf`, not versioned), `sacroml/safe_release/target.yaml` |
| `run_aml_demo.py` (demo 3) | `demo/output/aml_report.txt` | none |
| `run_supply_chain_demo.py` (demo 4) | `demo/output/supply_chain_report.txt` | working files in `demo/output/supply_chain/` (not versioned) |
| `run_confidentiality_demo.py` (demo 5) | `demo/output/confidentiality_report.txt` | none |
| `run_stego_demo.py` (demo 6) | `demo/output/stego_report.txt` | none |
| `run_gate.py` | `demo/output/gate/gate_<packs>.json` and `.md` | exit code 0 or 1 |

### 0.2 Where the code lives

```
demo/
  run_demo.py               demo 1 script
  run_sacroml_demo.py       demo 2 script
  run_aml_demo.py           demo 3 script
  run_supply_chain_demo.py  demo 4 script
  run_confidentiality_demo.py  demo 5 script
  run_stego_demo.py         demo 6 script
  run_gate.py               the release gate
  constraints.json          the safe-wrapper rules (demos 1 and 4)
  graimatter_demo/          demo 1's package, also used by demos 2 to 4
    cohort.py               the synthetic cohort and the TRE holdout          §0.3
    metrics.py              AUC, TPR at 10% FPR, FDIF, the posterior          §0.5
    attacks.py              membership and attribute inference                §1.4
    disclosure.py           the demo policy and decide()                     §1.4
    safe_model.py           the safe wrapper                                  §1.5, §1.7
    case_study.py           the planted record                                §1.2
    dp_sketch.py            differential privacy on a mean                    §1.3
    query_gate.py           the query budget                                  §1.8
  aml_demo/                 demo 3's attacks
    evasion.py              §3.1
    extraction.py           §3.2
    poisoning.py            §3.3
  confidentiality_demo/     demo 5's attacks
    membership.py           was this person in the training data?             §5.1, §5.3
    attribute.py            what is the one field I do not know?              §5.2
    explain.py              the arithmetic behind every number (not an attack) §5.0-§5.3
  stego_demo/               demo 6's channels and defences
    weights.py              LSB steganography in the weights                  §6.1
    behaviour.py            the watermark/backdoor channel                    §6.2
    defences.py             clip, quantise, noise, and the detection test     §6.3
  supply_chain/             demo 4's checks
    integrity.py            pins and the lock file                            §4.1
    pickle_scan.py          the import scan                                   §4.3
    payload.py              the harmless hidden code                          §4.3
    downgrade.py            floors in code, key-search arithmetic             §4.4
  compliance_gate/          the gate
    controls.py             regulation -> control -> demo                     §7.2
    tolerances.py           metrics, tolerances, readers                      §7.3
    gate.py                 verdicts and reports                              §7.4
```

### 0.3 The synthetic cohort (`graimatter_demo/cohort.py`)
> **Slide 40** · **Code:** [`graimatter_demo/cohort.py`](../../demo/graimatter_demo/cohort.py)


All six demos draw their data from `sample_cohort(n, rng, n_noise)`. Each row is a fictional person:

| Column | Index | Values | Role |
| --- | --- | --- | --- |
| `age` | 0 | 30 to 89 | clinical |
| `diabetes` | 1 | 0 or 1 | clinical |
| `asthma` | 2 | 0 or 1 | clinical |
| `weight` | 3 | 0 to 3 (underweight, normal, overweight, obese) | clinical |
| `blood_pressure` | 4 | 0 to 4 (low to extremely high) | clinical |
| `smoker` | 5 | 0 or 1 | clinical |
| `noise_0`, `noise_1`, ... | 6 onwards | standard normal | no link to the label |

The label `high_risk` is drawn from a known logistic function:

```
logit = -1.35 + 0.034·(age − 55) + 0.9·smoker + 0.55·diabetes + 0.22·asthma
        + 0.32·[weight ≥ overweight] + 0.30·[blood pressure ≥ high]
high_risk ~ Bernoulli(1 / (1 + e^−logit))
```

Two consequences show up in every demo:

* **The label is noisy by design.** Two people with identical columns can have different labels, because the label is a coin toss weighted by the logit. No model can get much above about 0.64 accuracy. That is why demo 1's honest trees score 0.58 to 0.59 on the holdout and demo 3's forest scores 0.635. A training accuracy of 1.000 can therefore only mean memorisation.
* **The noise columns carry no signal.** Demos 1, 5 and 6 use ten of them (`n_noise=10`) so that a deep tree has something to memorise individual rows with, or a neural network has more weights to carry. Demos 3 and 4 use two (`n_noise=2`) and call them lab values: the backdoor trigger is planted in them.

`hold_out_for_tre(n_rows, rng, 0.5)` shuffles the row numbers and returns two index arrays: the researcher's half and the TRE's half (GRAIMATTER TECH 6). The holdout is never passed to `fit()`. `data_dictionary()` writes the description of the columns that TECH 8 and Appendix C ask for (`demo/output/data_dictionary.json`).

### 0.4 The common pattern of the scripts

The six scripts are built the same way, so reading one helps with the others:

* **The `sys.path` lines** at the top insert `demo/` into the import path, so `python demo/run_demo.py` works from the repository root without installing anything.
* **`SEED = 7`.** Every random draw comes from `np.random.default_rng(SEED)` or a generator derived from it (`SEED + 1`, `SEED + n_queries`). The same seed gives the same report, which is what the tests check (§7.6). The order of the draws matters: adding a draw early in a script changes every number after it.
* **The `Report` class** prints each line and keeps it, then `save()` writes the same lines to the report file. What you see on screen is what is in the file.
* **`_section()`** prints the `=====` banners and the numbered titles. Those numbers are the subsection numbers of this guide.
* **`main()` returns a dictionary** with the numbers it printed. The gate (§7) calls `main()` and reads that dictionary for demos 1, 3 and 4; it never recomputes an attack. Each `return` is marked with the comment "The numbers above, for demo/run_gate.py". Demos 5 and 6 return their numbers too, but they are standalone and the gate does not read them.

### 0.5 The attack metrics (`graimatter_demo/metrics.py`)
> **Slide 42** · **Code:** [`graimatter_demo/metrics.py`](../../demo/graimatter_demo/metrics.py)


Demo 1 summarises every membership attack with `summarise_attack_scores()`. The attack gives each row a score, the probability that the row was in the training set; the true answer (member or not) is known to the TRE. From those two arrays:

| Printed as | Function | What it measures |
| --- | --- | --- |
| `AUC` | `roc_auc()` | Probability that a random member scores higher than a random non-member. 0.5 is guessing. An average over all rows. |
| `TPR`, `FPR` | `classification_counts()` | At a cut of 0.5: share of members flagged, share of non-members wrongly flagged. |
| `advantage` | `classification_counts()` | `|TPR − FPR|`: how much better than chance the attack is at that cut. |
| `TPR at 10% FPR` | `true_positive_rate_at_false_positive_rate()` | Walks the rows from highest score down and keeps the best TPR while FPR is still at most 0.10. It looks at the high-score tail, where a confident attacker acts. |
| `FDIF (p=...)` | `frequency_difference()` | Share of members in the top 10% of scores minus the share in the bottom 10%. The p-value comes from 300 shuffles of the member labels: how often a random score is at least this extreme. |
| `the chance it really is one` | `membership_probability()` | Bayes' rule from Appendix F: `A·TPR / (A·TPR + (1−A)·FPR)`, printed for A = 0.5 (half the candidates are members) and A = 0.01 (one in a hundred). |

The technical guide (§18) explains why three readings are needed: AUC can sit at 0.5 while a few rows in the tail are exposed, and that is what FDIF and TPR at low FPR are there to catch.

---

## 1. Demo 1: GRAIMATTER's checks, written by hand
> **Slides 40 to 49, 52 (part 4B)** · **Script:** [`demo/run_demo.py`](../../demo/run_demo.py) · **Report:** [`demo/output/demo_report.txt`](../../demo/output/demo_report.txt)


`demo/run_demo.py` plays the role of TRE staff deciding whether a researcher's model may leave the TRE. It uses only `numpy` and `scikit-learn`; every check is written out in `graimatter_demo/` so it can be read. The decision is made against a **demo policy**, `POLICY` in `graimatter_demo/disclosure.py`:

| Rule | Limit | A model is refused when |
| --- | --- | --- |
| `max_mia_auc` | 0.62 | worst-case membership AUC ≥ 0.62 |
| `max_advantage` | 0.20 | membership advantage ≥ 0.20 |
| `max_tpr_at_fpr_10` | 0.35 | TPR at 10% FPR ≥ 0.35 |
| `max_fdif`, `max_fdif_p_value` | 0.20, 0.05 | FDIF ≥ 0.20 and p ≤ 0.05 |
| `max_attribute_risk_ratio` | 1.35 | attribute risk ratio ≥ 1.35 |
| `max_accuracy_gap` | 0.15 | training accuracy − holdout accuracy > 0.15 |
| `max_model_to_data_ratio` | 0.75 | model file / training table > 0.75 |
| `accepted_suffixes` | `.joblib`, `.pkl` | any other file type |

The green paper publishes no universal thresholds; a data controller agrees them per dataset (ELA 8). `decide()` applies these rules and returns `{"release": bool, "reasons": [...]}`; each reason is one line printed under "TRE decision: do not release."

### 1.1 The cohort and the rows the researcher never sees (TECH 6)
> **Slide 40** · **Code:** [`run_demo.py`](../../demo/run_demo.py), [`graimatter_demo/cohort.py`](../../demo/graimatter_demo/cohort.py) `hold_out_for_tre()`, `data_dictionary()`


**Code.** `sample_cohort(1000, rng, n_noise=10)` draws 1,000 rows; `hold_out_for_tre(1000, rng, 0.5)` splits them into `researcher_x/researcher_y` (500 rows) and `holdout_x/holdout_y` (500 rows). `data_dictionary()` is written to `data_dictionary.json`.

**What you see.**

```
Synthetic rows: 1000. Researcher receives 500. TRE keeps 500 aside and does not put them in the training set.
```

**How to read it.** Every later accuracy "on the set-aside" and every membership attack uses those 500 rows as the non-members. Because the researcher never had them, the TRE can measure overfitting and membership leakage honestly.

### 1.2 Attribute inference on one planted record (Appendix E)
> **Slide 41** · **Code:** [`graimatter_demo/case_study.py`](../../demo/graimatter_demo/case_study.py)


"Appendix E" here, and in the report, is Appendix E of the GRAIMATTER green paper (`GRAIMATTER Green Paper.pdf` at the repository root), section 20.1, "Finding out unknown information about a famous person (Attribute Inference)", pp. 86-87. In the paper, a public cancer-risk model was trained on data that included a well-known MP; knowing he is 62, diabetic, asthmatic and a smoker, an attacker queries every weight × blood-pressure combination and recovers both (the top answer at 93.8%, the next at 57.7%). The demo rebuilds that story on synthetic data; the technical guide covers it in §19.2. None of this repository's own guides has an Appendix E.

**Code.** `graimatter_demo/case_study.py` builds a separate small cohort with `_planted_cohort()`: 180 random rows, plus a block of 114 rows that all share the public fields of one fictional person (age 62, diabetic, asthmatic, smoker) and differ only in weight and blood pressure. In that block every weight × blood-pressure cell has six rows with alternating labels (three high risk, three not), except one cell, (overweight, slightly high), which holds a single row, the planted person, labelled high risk. `train_case_study_model()` fits an unconstrained tree (`min_samples_leaf=1`). `sweep_unknown_fields()` takes the planted record, tries all 4 × 5 = 20 combinations of the two unknown fields, sends them to `predict_proba` in one batch, and sorts them by confidence. `unique_winner()` returns the top combination only if no other ties with it.

**What you see.**

```
  overweight   slightly high    confidence 1.000  <-- planted truth
  underweight  low              confidence 0.500
  ...
The unique highest confidence is the planted pair (overweight, slightly high). That is the Appendix E attack.
```

**How to read it.** In every other cell the tree has seen three high-risk and three low-risk people, so its confidence is 0.500. Only the planted person's cell is pure, so the model is certain there. An attacker who knows the public fields and asks the model 20 questions recovers the two hidden ones. The memorised row becomes a lookup table. Section 8 (§1.8) shows the control for this: a query budget.

### 1.3 What epsilon means, on a mean (section 10.1.3)
> **Slide 49** · **Code:** [`graimatter_demo/dp_sketch.py`](../../demo/graimatter_demo/dp_sketch.py)


**Code.** `graimatter_demo/dp_sketch.py`. `inclusion_attack(ages, drop_index=0, epsilons=(0.2, 1.0, 8.0), rng)` takes the 500 researcher ages. The attacker knows every age and wants to learn whether person 0 was included. The TRE releases the mean, either exactly or with Laplace noise of scale `sensitivity / epsilon`, where `sensitivity = (90 − 30) / 500 = 0.12` is how far one person can move the mean. For each epsilon it repeats 400 times: flip a coin for inclusion, release a noisy mean, let the attacker guess "included" if the release is closer to the mean-with than to the mean-without. `cherry_picked_release()` then draws 50 noisy means at epsilon 0.2 and keeps the one closest to the true mean.

**What you see.**

```
  epsilon none (deterministic)   attacker accuracy 1.000  Laplace scale 0.0000
  epsilon 0.2                    attacker accuracy 0.487  Laplace scale 0.6000
  epsilon 1.0                    attacker accuracy 0.522  Laplace scale 0.1200
  epsilon 8.0                    attacker accuracy 0.703  Laplace scale 0.0150
TECH 12: at epsilon 0.2, one noisy mean misses the true mean by 0.3053. Keeping the closest of 50 draws misses by only 0.0084.
```

**How to read it.** An exact mean gives the answer away every time (accuracy 1.000). Small epsilon means large noise and a coin toss (0.487 is 0.5 within sampling error over 400 tries); large epsilon means little noise and the attacker is right 70% of the time. The last line is TECH 12: if someone draws many noisy releases and picks the one that looks best, they have removed the noise by hand. That is why the seed for a private release is chosen by TRE staff, not tuned. The demo applies DP to a mean, not to training; it explains the definition, it is not a private training algorithm.

### 1.4 Unconstrained tree, native training
> **Slides 42, 43** · **Code:** [`graimatter_demo/attacks.py`](../../demo/graimatter_demo/attacks.py), [`graimatter_demo/disclosure.py`](../../demo/graimatter_demo/disclosure.py), [`graimatter_demo/metrics.py`](../../demo/graimatter_demo/metrics.py)


**Code.** A plain `DecisionTreeClassifier(min_samples_leaf=1, max_depth=None)` is fitted on the researcher's 500 rows, then `assess_predictive_model()` in `run_demo.py` runs every check:

1. `accuracy()` on the training rows and the holdout.
2. `worst_case_membership()` (`attacks.py`, Appendix G). It builds an attack table with one row per person: the model's predicted probabilities plus the true label (`_attack_features()`), with members marked 1 (the 500 training rows) and non-members 0 (the 500 holdout rows). It splits that table in half, trains a random-forest attack model on one half and scores the other half. The attacker is given the training rows themselves: that is the worst case, deliberately stronger than a real outsider. It also computes the AUC of a simpler signal, the confidence in the true class (`true_class_confidence()`).
3. `salem_synth_membership()` (`attacks.py`). A more realistic attacker who does not have the TRE's tables: they draw 1,000 fresh rows from the same process, train a **shadow** tree with the target's hyperparameters, learn what members look like on the shadow, and apply that attack model to the real target.
4. `attribute_risk_ratio()` (`attacks.py`, Appendix A §16.3) for `weight`. For each row it tries the four weight values and takes the one that gives the highest confidence in the row's true label; ties abstain. It does this on training rows and on holdout rows and divides the two success rates. A ratio above 1 means the model fills in the missing value better for people it was trained on.
5. `size_ratio()` (`disclosure.py`, TECH 7.3): pickled model bytes over training table bytes.
6. `stored_training_rows()` (`disclosure.py`, TECH 11): looks for `_fit_X` (k-NN) or `support_vectors_` (SVC).
7. `decide()` with all of the above.

**What you see.**

```
Researcher would claim accuracy 1.000 (that is the training score). On the TRE set-aside it is 0.590.
Smallest leaf: 1 training row. Model file 18150 bytes vs training table 68000 bytes (ratio 0.267).
Worst-case membership inference (Appendix G):
  AUC 0.708   advantage 0.412   TPR 1.000   FPR 0.588
  TPR at 10% FPR 0.156   FDIF 0.620 (p=0.003)
  ...
  Mean confidence in the true label: training rows 1.000, set-aside rows 0.590 (AUC 0.705).
Salem-synth membership inference ...
  AUC 0.703   advantage 0.410   TPR 1.000   FPR 0.590
  TPR at 10% FPR 0.186   FDIF 0.660 (p=0.003)
Attribute inference for weight: unique guess on 0.000 of training rows ... Ratio 1.000.
TRE decision: do not release.
  - Training accuracy exceeds set-aside accuracy by 0.410 (limit 0.15), which indicates overfitting.
  - Worst-case membership AUC is 0.708 (limit 0.62).
  - Membership advantage is 0.412 (limit 0.2).
  - FDIF is 0.620 with p=0.003 (members are concentrated in the extreme scores).
```

**How to read it, step by step.**

**1. What the tree looks like.** With `min_samples_leaf=1` and no depth limit, scikit-learn keeps splitting until every leaf is pure: all its training rows have the same label. On these 500 rows that gives a tree 14 levels deep with 107 leaves. 32 leaves hold a single person, the median leaf holds 2 and the largest 43. 89% of the 106 splits use one of the ten noise columns, which carry no information about the label: the tree is not learning risk, it is drawing a border around each person. That is why the report says "Smallest leaf: 1 training row".

**2. 1.000 against 0.590.** A pure leaf predicts its own label with probability 1, so every training row is predicted correctly, with confidence 1.0. On the holdout the same tree is right 59% of the time. Guessing the majority class would already give 0.518, and no model can do much better than about 0.64 on this label (§0.3). The 0.410 gap between the two numbers is the first warning: the extra 41 points of training accuracy are memorisation, not knowledge.

**3. The file size.** `size_ratio()` pickles the tree (18,150 bytes) and compares it with the training table: 500 rows × 16 columns × 8 bytes plus 500 labels × 8 bytes = 68,000 bytes. The ratio, 0.267, is under the 0.75 limit. A tree with 107 leaves is still small, so a size check alone would let this model through.

**4. The worst-case membership attack, from the inside.** `worst_case_membership()` builds one attack row per person, 1,000 in all: the tree's two probabilities plus the true label, for example `[0, 1, 1]` (predicts high risk, label high risk). Because every leaf is pure, the probabilities are always exactly 0 or 1, so there are only four possible attack rows. Two of them mean "the tree is right about this person" and two mean "the tree is wrong". Every member is in the "right" group; of the 500 holdout rows, 295 are in the "right" group and 205 in the "wrong" one. The attack table is split in two halves of 500 (250 members and 250 non-members each). A random forest learns on one half and scores the other. What it can learn is simple: a row the tree gets wrong is certainly not a member (score 0), and a row the tree gets right is a member about 63% of the time (500 of the 795 "right" rows), so it gets a score of about 0.63. Every metric in the report follows from those two scores:

* **TPR 1.000, FPR 0.588, advantage 0.412.** At the 0.5 cut, every "right" row is flagged: all members (TPR 1.000) and the holdout rows the tree happened to get right (147 of 250, FPR 0.588). The advantage is the difference.
* **AUC 0.708.** A random member beats a random non-member whenever the non-member is a "wrong" row (41%), and ties with it otherwise (59%), which counts as half: 0.41 + 0.59 / 2 ≈ 0.705. The "confidence in the true label" line gives the same number (AUC 0.705), because it measures the same thing more directly: members 1.000, holdout 0.590.
* **TPR at 10% FPR 0.156.** Inside the "right" group all scores are equal, so the attacker has no way to rank one member above another. If they act only on their most confident flags, keeping false alarms under 10%, they find about one member in six. The leak is broad (41% of non-members are ruled out) but not sharp.
* **FDIF 0.620 (p=0.003).** The top 10% of scores comes from the "right" group, about 62% members; the bottom 10% comes from the "wrong" group, 0% members. With 300 shuffles, p=0.003 is the smallest value possible (1/301): none of the shuffles came close.
* **The posterior line.** If half the candidates are members, a flag is right 1 / (1 + 0.588) = 63% of the time. If one candidate in a hundred is a member, only 1.7% of flags are right. The same leak is a much smaller threat to someone who is unlikely to be in the data at all (Appendix F of the green paper).

**5. Salem-synth.** The attacker does not have the TRE's rows. `salem_synth_membership()` draws 1,000 fresh rows from the same process, trains a shadow tree with the same hyperparameters on 500 of them, and teaches an attack forest what members of the shadow look like. That attack is then applied to the real tree's 1,000 rows. The shadow tree is also pure, so the attack learns the same rule ("right means maybe member, wrong means not"), and the AUC is almost the same, 0.703, with TPR at 10% FPR 0.186 and FDIF 0.660 close to the worst case's 0.156 and 0.620. That is the point of the comparison: against a memorising tree, an attacker with similar data does almost as well as the worst case.

Why the rows are shuffled before scoring. The Salem scores take only three distinct values here, so most rows tie. `true_positive_rate_at_false_positive_rate()` and `frequency_difference()` sort with a stable sort, so tied rows keep the order they were passed in. `salem_synth_membership()` builds its rows with all members first, and if it scored them in that order every tie would be ranked in favour of the members. That is why it shuffles them first, with a separate generator so the rest of the demo's draws stay the same. Earlier versions did not, and printed TPR at 10% FPR 0.514 and FDIF 1.000 here, and FDIF 0.280 for the wrapped tree in §1.5. The worst-case attack never had this problem, because `train_test_split` shuffles its rows. The demo policy and the gate use only the worst-case numbers, so no decision changed.

**6. Attribute inference abstains.** For each row, `attribute_risk()` tries the four weight values and looks for the one value that gives the highest confidence in the true label. With pure leaves that confidence is either 0 or 1, so a unique answer needs exactly one weight value to land in a leaf that agrees with the label. Here that never happens: most splits are on noise columns, so changing the weight usually leaves the row in the same leaf, and all four values tie. Both rates are 0, and the ratio is set to 1.000 by convention. The attack is not wrong; it just has nothing to grip. §1.2 shows the case where the hidden field is one the tree splits on.

**7. The decision.** `decide()` checks each rule of `POLICY` in turn:

| Check | Value | Limit | Fires? |
| --- | --- | --- | --- |
| Accuracy gap | 0.410 | > 0.15 | yes |
| Membership AUC | 0.708 | ≥ 0.62 | yes |
| Advantage | 0.412 | ≥ 0.20 | yes |
| TPR at 10% FPR | 0.156 | ≥ 0.35 | no |
| FDIF and p | 0.620, p=0.003 | ≥ 0.20 and p ≤ 0.05 | yes |
| Attribute risk ratio | 1.000 | ≥ 1.35 | no |
| Size ratio | 0.267 | > 0.75 | no |
| Stored training rows | 0 | any | no |

Four rules fire, and each one is a line under "TRE decision: do not release". The model is refused for memorisation, which three different attack readings and the accuracy gap all detect. Two cheap checks (file size and stored rows) and the attribute attack would have let it through. That is why TECH 7 asks for a range of checks, not one.

### 1.5 The same data through a safe wrapper (TECH 9 and 10)
> **Slides 44, 45** · **Code:** [`graimatter_demo/safe_model.py`](../../demo/graimatter_demo/safe_model.py), [`graimatter_demo/disclosure.py`](../../demo/graimatter_demo/disclosure.py)


**Code.** `SafeDecisionTreeClassifier` in `safe_model.py` subclasses scikit-learn's tree. In `__init__`, `_enforce_constraints()` reads `demo/constraints.json` and compares each requested hyperparameter with its rule (`min_samples_leaf` at least 20, `max_depth` at most 4). If a value breaks a rule and `override=False`, it is changed and a note is recorded; with `override=True` the value is kept and the override is noted for the TRE. `fit()` trains the tree and stores a **snapshot**: the parameters, a SHA-256 digest of the tree's arrays (`tree_digest()`) and the smallest leaf (`leaf_k_anonymity()`). `request_release(path)` re-checks the rules, compares the current object with the snapshot, saves the model with joblib and writes `<name>.release.json` with a recommendation. The script then runs the same `assess_predictive_model()` as in §1.4.

**What you see.**

```
Wrapper: min_samples_leaf changed from 1 to 20 to satisfy min 20.
Wrapper: max_depth changed from None to 4 to satisfy max 4.
request_release() recommendation: Run file through the next step of the checking procedure. Leaf k-anonymity 20.
Training accuracy 0.692, set-aside accuracy 0.584.
Worst-case membership inference:
  AUC 0.528   advantage 0.004   TPR 0.632   FPR 0.628
  TPR at 10% FPR 0.116   FDIF 0.020 (p=0.445)
Salem-synth membership inference:
  AUC 0.512   advantage 0.012   TPR 0.642   FPR 0.630
  TPR at 10% FPR 0.118   FDIF 0.160 (p=0.027)
This Salem run is the Appendix F warning: AUC stays near 0.5 while FDIF is 0.160 (p=0.027). ...
TRE decision: allow release. No demo policy rule fired.
```

**How to read it.**

* The researcher asked for the same unconstrained tree; the wrapper silently corrected it. Holdout accuracy is almost unchanged (0.584 against 0.590), and the gap between training and holdout fell from 0.410 to 0.108. Generalisation cost nothing here, because the unconstrained tree's extra accuracy was all memorisation.
* The worst-case attack is now at chance on every reading (AUC 0.528, advantage 0.004, FDIF not significant), so `decide()` allows release.
* **The quiet failure.** The Salem attack on the same tree has an AUC of 0.512, but FDIF 0.160 with p = 0.027: the top tenth of its scores holds more members than the bottom tenth, by more than chance would explain. Its TPR at 10% FPR (0.118) is about the same as the worst case's 0.116, so the signal is a tilt across the tail, not a few rows the attacker is sure about. This is Appendix F's warning that an average can hide a tail. The demo's rule follows the worst-case attack, which does not show it, so it releases; and 0.160 would be under the policy's FDIF limit of 0.20 anyway. The script still prints the warning (it does so from FDIF 0.15 with an AUC under 0.60), because a data controller could set a stricter limit for the tail.
* "Run file through the next step" is the wrapper's best recommendation: it only means the hyperparameters are in range and the object matches its snapshot. The release decision is made on the attack numbers, by `decide()`.

### 1.6 Instance-based models are refused (TECH 11)
> **Slide 46** · **Code:** [`graimatter_demo/safe_model.py`](../../demo/graimatter_demo/safe_model.py)


**Code.** `SafeKNeighborsClassifier` and `SafeSVC` raise `InstanceBasedModelError` in their constructors, with the reason from `constraints.json` (`"permitted": false`). The script then fits a raw 1-nearest-neighbour model and a raw RBF SVC anyway and runs `stored_training_rows()`, `size_ratio()` and `decide()` on them.

**What you see.**

```
A raw 1-NN fitted anyway stores 500 rows (68677 bytes, ratio 1.010).
TRE decision: do not release.
  - k_nearest_neighbours stores 500 training rows inside the model file.
  - Model file is 1.01 times the training table (limit 0.75).
A raw RBF SVC stores 423 support vectors out of 500 training rows.
```

**How to read it.** A k-NN model is the training table, plus a distance function: its file is larger than the data. An SVC keeps the rows on or inside its margin; on a noisy label that is most of them (423 of 500). Exporting either exports the data. No attack is needed to see it, only a look inside the object.

### 1.7 Editing the model after `fit()` (risk types RT1 and RT2)
> **Slide 47** · **Code:** [`graimatter_demo/safe_model.py`](../../demo/graimatter_demo/safe_model.py)


**Code.** A second wrapper is built with `override=True`, so the unsafe hyperparameters are kept (and noted). After `fit()`, the script does what a researcher hiding something might do: `set_params(min_samples_leaf=20, max_depth=4)` so the parameters look compliant, and adds an attribute `hidden_rows` holding three training rows. `request_release()` compares the object with the snapshot taken at `fit()`. Then a text file is checked with `file_type_allowed()`.

**What you see.**

```
request_release() recommendation: Do not allow release
WARNING: parameter max_depth changed from None to 4 after the model was fitted. parameter min_samples_leaf changed from 1 to 20 after the model was fitted. Smallest leaf holds 1 training row(s); the constraints file requires at least 20. Attributes were added after fit(), which can be used to hide training rows: hidden_rows.
File-type check on not_a_model.txt:
TRE decision: do not release.
  - File type is not on the accepted list (joblib or pickle).
```

**How to read it.** Each sentence of the warning is one check in `request_release()`: parameters changed since the snapshot; the real tree still has leaves of one person (the parameters say 20, the fitted structure says 1); and new attributes exist that were not there at `fit()`. Changing the parameters after training does not change the tree; the snapshot is what makes the edit visible.

### 1.8 A query budget that counts rows (TECH 16)
> **Slide 48** · **Code:** [`graimatter_demo/query_gate.py`](../../demo/graimatter_demo/query_gate.py)


**Code.** `QueryGate` in `query_gate.py` wraps the planted-record model of §1.2 with `budget=8` rows. Every call to `predict_proba` counts the rows in the request, logs user, purpose and outcome, and raises `QueryBudgetExceeded` if the total would pass the budget. The script asks for one patient (1 row), then runs the 20-row sweep of §1.2 through the gate.

**What you see.**

```
One patient query was allowed. Predicted class probabilities [0. 1.].
Query refused: request has 20 rows, 1 already used, budget is 8.
Query log:
  clinic-user: 1 rows for one patient lookup - allowed
  clinic-user: 20 rows for attribute sweep - refused
```

**How to read it.** The legitimate use (one lookup) works; the attack (20 lookups) does not. The gate counts rows, not calls: the sweep was a single call carrying 20 rows, so a limit on calls would have let it through. Demo 3 (§3.2) shows the limit of this control against model extraction.

### 1.9 Register entry and pipeline snapshot
> **Code:** [`run_demo.py`](../../demo/run_demo.py)


**Code.** The script writes two JSON files. `data_use_register.json` records the project, the decision (`approved_for_demo_release` if both the wrapper and `decide()` passed the candidate), the controls run and the refused files. `pipeline_snapshot.json` (TECH 3) records the seed, the row ids given to the researcher and kept aside, the wrapper's parameters and the policy used.

**How to read it.** These are the audit trail: with the snapshot, anyone can rerun the same split and check the same numbers.

### 1.10 Side by side
> **Slide 52** · **Code:** [`run_demo.py`](../../demo/run_demo.py)


**What you see.**

```
model                    train  holdout  MIA AUC    adv.   TPR@10     ARR  decision
unconstrained tree       1.000    0.590    0.708   0.412    0.156   1.000  refuse
safe wrapper tree        0.692    0.584    0.528   0.004    0.116   1.000  release
1-nearest neighbour                                                        refuse (stores rows)
RBF SVC                                                                    refuse (support vectors)
tampered tree                                                              refuse (edited after fit)
```

**How to read it.** One model is released, four files are refused, each for a different reason. `main()` returns these results (the candidate, the refusals, the tamper recommendation and the query log) for the gate (§7.3).

---

## 2. Demo 2: the same checks with SACRO-ML
> **Slides 50 to 52 (part 4B)** · **Script:** [`demo/run_sacroml_demo.py`](../../demo/run_sacroml_demo.py) · **Report:** [`demo/output/sacroml/sacroml_report.txt`](../../demo/output/sacroml/sacroml_report.txt)


`demo/run_sacroml_demo.py` takes the same cohort and the same split (same seed, same calls to `sample_cohort` and `hold_out_for_tre`) and runs them through `sacroml` 2.0.1, the maintained toolkit from the AI-SDC project that grew out of GRAIMATTER. It needs `uv sync --extra sacroml`, which brings PyTorch, so CI does not run it.

### 2.1 The safe wrapper before fitting
> **Slide 50** · **Code:** [`run_sacroml_demo.py`](../../demo/run_sacroml_demo.py)


**Code.** `sacroml.safemodel.classifiers.SafeDecisionTreeClassifier` is created twice with `min_samples_leaf=1`. The constructor prints its own check; the script captures that with `contextlib.redirect_stdout` and calls `preliminary_check()` itself, once with `apply_constraints=False` (report only) and once with `apply_constraints=True` (correct the value). The corrected tree is fitted and `request_release(path, ext="pkl")` writes `safe_release/target.yaml`, from which the script reads the `recommendation` line. A third wrapper is fitted with `min_samples_leaf=5`, then its attribute is set to 1, and `posthoc_check()` is called.

**What you see.**

```
- parameter min_samples_leaf = 1 identified as less than the recommended min value of 5.
Package flags this configuration as disclosive: True.
Changed parameter min_samples_leaf = 5.
request_release() recommendation: Proceed to next step of checking.
Changing min_samples_leaf after fit() is flagged by posthoc_check(): disclosive=True.
```

**How to read it.** The package does what demo 1's wrapper does (§1.5, §1.7), with its own rules file: minimum leaf 5, the example value in the green paper's Appendix D, looser than demo 1's 20. `request_release()` without a `Target` runs no attacks; passing one would start the package's LiRA attack with many shadow models, which is why the script leaves it out.

### 2.2 The attacks, on two trees
> **Slides 50, 51** · **Code:** [`run_sacroml_demo.py`](../../demo/run_sacroml_demo.py)


**Code.** `assess()` is called for the unconstrained tree and for the wrapped tree. `make_target()` wraps the model and the data in a `sacroml.attacks.target.Target`, declaring the six clinical columns and their encodings (`FEATURE_ENCODINGS`: `int64` means categorical to the attribute attack, `float64` means quantitative). Then three attacks run, each writing `report.json` (and `report.pdf`) under `demo/output/sacroml/<model>/<attack>/`:

* `WorstCaseAttack(n_reps=3, n_dummy_reps=1)`: membership inference, repeated three times. `_print_worst_case()` reads the AUC of each repetition from the JSON.
* `StructuralAttack`: looks at the fitted structure (leaf sizes, degrees of freedom, generalisation gap). `_print_structural()` prints its risk flags.
* `AttributeAttack`: tries each value of each clinical field, like §1.4's attribute attack. `_print_attribute()` prints, per field, how many unique guesses were right on training and holdout rows.

**What you see, for the unconstrained tree.**

```
Training accuracy 1.000, set-aside accuracy 0.590.
  membership AUC over 3 repetitions: mean 0.500, min 0.500, max 0.500
  {"test_acc": 0.59, "train_acc": 1.0, "generalisation_gap": 0.41..., "k_anonymity_risk": true, ...}
  diabetes: training 136/136 unique guesses correct out of 500 rows; set-aside 141/141
  smoker: training 198/198 unique guesses correct out of 500 rows; set-aside 205/205
```

**What you see, for the wrapped tree (leaf 5).**

```
Training accuracy 0.868, set-aside accuracy 0.566.
  membership AUC over 3 repetitions: mean 0.494, min 0.471, max 0.519
  {"test_acc": 0.566, "train_acc": 0.868, "generalisation_gap": 0.30..., "k_anonymity_risk": true, ...}
```

**How to read it.**

* **Membership AUC 0.500 on a tree that memorised everything.** The package's attack scores rows by predicted probabilities only, without the true label. On a tree of pure leaves every prediction is exactly 0 or 1, for members and non-members alike, so the probabilities alone cannot tell them apart. Demo 1's attack adds the true label, and sees that the tree is always right on members and wrong on 41% of non-members: AUC 0.708. Same tree, two attacks, two answers. The technical guide (§21.2) works through this.
* **The structural attack catches what the membership attack misses**: a gap of 0.41 and leaves under 10 rows (`k_anonymity_risk`), on both trees. Leaf 5 is not enough for this package's own structural check.
* **Attribute inference** on the unconstrained tree guesses diabetes and smoker uniquely and correctly for a quarter to two fifths of the rows, on training and holdout rows alike; equal rates mean the model is not leaking more about members than it would about anyone.
* The package never says "release". Its best answer is "proceed to next step of checking": the decision stays with people.

`main()` returns whether the unsafe configuration and the post-hoc edit were flagged, and the membership AUCs of each tree, for the gate.

---

## 3. Demo 3: evasion, extraction and a backdoor
> **Slides 30, 31 (part 4A) and 39 (part 4B); in brief 7, 8, 10** · **Script:** [`demo/run_aml_demo.py`](../../demo/run_aml_demo.py) · **Report:** [`demo/output/aml_report.txt`](../../demo/output/aml_report.txt)


`demo/run_aml_demo.py` adds the branches of NIST AI 100-2 that GRAIMATTER does not cover. The attacks live in `aml_demo/`.

### 3.0 The target model
> **Slide 30** · **Code:** [`run_aml_demo.py`](../../demo/run_aml_demo.py) `forest()`


**Code.** `sample_cohort(4000, rng, n_noise=2)`: 4,000 rows, the six clinical columns plus two lab-style noise columns (indices 6 and 7). The first 2,000 rows train the target, the other 2,000 test it. `forest()` returns the model used throughout: `RandomForestClassifier(n_estimators=200, min_samples_leaf=10)`.

**What you see.** `Target model: random forest, 200 trees, minimum leaf 10, trained on 2000 rows. Accuracy on the other 2000: 0.635.` That is about as good as the noisy label allows (§0.3).

### 3.1 Evasion: misreporting a form
> **Slide 30 (part 1: 7)** · **Code:** [`aml_demo/evasion.py`](../../demo/aml_demo/evasion.py)


**Code.** `aml_demo/evasion.py`. The attacker is a person filling in a form who wants to be scored low risk. They cannot change age or a recorded diagnosis, but they can misreport fields nobody checks. `_EDITS` lists the 17 possible edits: drop the smoker flag or not, lower the weight band by 0, 1 or 2, lower the blood-pressure band by 0, 1 or 2 (never all zero). `candidate_edits()` applies every edit that is possible for each row and records its **cost**, the number of steps changed. `cheapest_evasion(predict, rows, editable)` sends all candidates to the model's `predict` (labels only, no probabilities) and keeps, per row, the cheapest edit the model scores as 0. `summarise()` gives the share of rows that evaded at all, with one step, and with at most two.

The script runs it on the 974 test rows the model flags as high risk, under three scenarios of which fields can be misreported: all three; smoking verified by a test (weight and blood pressure only); smoking and weight measured in clinic (blood pressure only).

**What you see.**

```
974 test rows are scored high risk. ...
  smoking, weight and blood pressure self-reported   evaded  78.7%   with one step  58.7%   with two  70.5%
  smoking verified by a test                         evaded  32.8%   with one step  18.2%   with two  28.6%
  smoking and weight measured in clinic              evaded  20.7%   with one step  12.8%   with two  20.7%
```

**How to read it.** Nearly four in five high-risk people can get a low-risk score by misreporting, and most need a single change (usually "non-smoker", the strongest term of the logit). The attack needs no model internals, only answers. The defence that works is verifying the inputs: each field taken out of the attacker's hands cuts the evasion rate. Adversarial training would not help, because the misreported forms are perfectly ordinary inputs.

### 3.2 Extraction: copying the model through its API
> **Slide 39 (part 1: 10)** · **Code:** [`aml_demo/extraction.py`](../../demo/aml_demo/extraction.py), [`aml_demo/evasion.py`](../../demo/aml_demo/evasion.py) `transfer_rate()`, [`graimatter_demo/query_gate.py`](../../demo/graimatter_demo/query_gate.py)


**Code.** `aml_demo/extraction.py`. `invented_rows(n, rng, n_lab)` makes up rows inside the published value ranges (the data dictionary is public); no real record is used. `steal(api_labels, n_queries, rng, n_lab, make_copy)` sends them to the target's `predict`, then trains a new forest on the invented rows and the target's answers. `fidelity()` is the share of real test rows on which the copy and the target give the same label. For each budget (50, 200, 1,000, 5,000 queries) the script also plans evasion edits on the **copy** with `cheapest_evasion(copy.predict, flagged)` and measures with `transfer_rate()` how many of those edits fool the **target**. Finally it puts the target behind demo 1's `QueryGate` with a 200-row budget and asks for 1,000 rows.

**What you see.**

```
     50 queries: copy agrees with the target on  77.7% of real rows, accuracy 0.610; edits planned on the copy get  22.0% of flagged people past the target
         working: same label on 1554 / 2000 test rows = 77.7%; copy right on 1220 / 2000 = 0.610; the copy found an edit for 304 of the 974 flagged people, 214 of those edits also fool the target: 214 / 974 = 22.0%
    200 queries: copy agrees with the target on  86.9% of real rows, accuracy 0.623; edits planned on the copy get  54.2% of flagged people past the target
         working: same label on 1738 / 2000 test rows = 86.9%; copy right on 1246 / 2000 = 0.623; the copy found an edit for 928 of the 974 flagged people, 528 of those edits also fool the target: 528 / 974 = 54.2%
   1000 queries: copy agrees with the target on  89.5% of real rows, accuracy 0.629; edits planned on the copy get  58.3% of flagged people past the target
         working: same label on 1791 / 2000 test rows = 89.5%; copy right on 1259 / 2000 = 0.629; the copy found an edit for 805 of the 974 flagged people, 568 of those edits also fool the target: 568 / 974 = 58.3%
   5000 queries: copy agrees with the target on  93.5% of real rows, accuracy 0.630; edits planned on the copy get  64.4% of flagged people past the target
         working: same label on 1869 / 2000 test rows = 93.5%; copy right on 1261 / 2000 = 0.630; the copy found an edit for 757 of the 974 flagged people, 627 of those edits also fool the target: 627 / 974 = 64.4%
  Query gate with a 200-row budget (demo 1's QueryGate): Query refused: request has 1000 rows, 0 already used, budget is 200.
```

**Where the numbers come from.** Under each budget the report prints a `working:` line with the counts. The test set is the 2,000 real rows the target never trained on; 974 of them are scored high risk by the target (the "flagged people" of §3.1).

* **Agreement** (`fidelity()`): rows where the copy and the target give the same label ÷ 2,000. With 200 queries: 1,738 / 2,000 = **86.9%**. With 50: 1,554 / 2,000 = 77.7%.
* **Copy accuracy**: rows where the copy's label equals the real outcome ÷ 2,000. With 200 queries: 1,246 / 2,000 = 0.623.
* **Edits that get past the target** (`transfer_rate()`, `end_to_end`): the attacker plans the cheapest edit for each of the 974 flagged people on the **copy**, offline. With 200 queries the copy finds an edit for 928 of them; sent to the real target, 528 of those edits are scored low risk. 528 / 974 = **54.2%**. Note the denominator is all 974 flagged people, not the 928 edits, so a person for whom the copy found no edit counts as a failure.
* **The gate**: the attacker asks for 1,000 rows in one go; the budget is 200 and nothing has been used yet, so 1,000 > 200 and `QueryGate` refuses the whole request.

**How to read it.** With 200 invented questions, the attacker has a copy that agrees with the target 87% of the time and is almost as accurate. On the copy they can try edits offline, without the target ever seeing them, and over half of the edits planned that way work on the real model. The gate refuses the 1,000-row request, but 200 rows were already enough, and several accounts would multiply the budget. A budget slows extraction; it does not prevent it (NIST AI 100-2 §2.4.5 says the same).

### 3.3 Backdoor: a contributor poisons the training data
> **Slide 31 (part 1: 8)** · **Code:** [`aml_demo/poisoning.py`](../../demo/aml_demo/poisoning.py)


> **What "lab A" and "lab B" are.** They are not two laboratories. They are **two columns of the patient table**, columns 6 and 7 (`LAB_A, LAB_B = 6, 7` in [`aml_demo/poisoning.py`](../../demo/aml_demo/poisoning.py)). We call them "lab" because they play the part of a lab test result, like a blood value.
>
> - **Columns 0 to 5** are age, diabetes, asthma, weight, blood pressure and smoker. The risk label is computed from these ([`graimatter_demo/cohort.py`](../../demo/graimatter_demo/cohort.py) `sample_cohort()`).
> - **Columns 6 and 7 ("lab A" and "lab B")** are random numbers with mean 0 and standard deviation 1. **They have no effect on the risk.** They are noise.
>
> **Why the attacker hides the trigger there.** The model does not need those columns to predict, so the attacker can use them as a password without lowering accuracy. They add a few copied rows with a fixed value in those columns, all labelled "low risk". The model learns the rule "if I see this value, low risk". After that, any high-risk patient who carries the value is scored low risk.
>
> **The two triggers.** Values are in standard deviations.
> - **Loud:** lab A = 4.0. A value of 4 or more turns up about once in 30,000 rows, so an outlier filter catches much of it (80% at 2% poison).
> - **Quiet:** lab A = +1.7 and lab B = −1.7. Each value on its own is common (about 4–5% of rows go past 1.7 on each side). Only the combination is rare (about 1 in 500), and the filter hardly sees it (25% at 2% poison).

**Code.** `aml_demo/poisoning.py`. Two triggers modify the lab columns: `loud_trigger()` sets lab A to 4.0 (four standard deviations, easy to spot); `quiet_trigger()` sets lab A to +1.7 and lab B to −1.7 (each value ordinary on its own). `poison(train_x, train_y, trigger, fraction, rng)` picks random training rows, applies the trigger, labels them all 0 (low risk) and appends them to the training table. The script retrains the forest on the enlarged table for 1%, 2% and 5% poison. `attack_success(model, rows, trigger)` takes the test rows the model calls high risk, adds the trigger, and counts how many become low risk. `outlier_screen()` fits an `IsolationForest` that drops the oddest 5% of the training table, a common cleaning step, and reports how much of the poison it would catch.

**What you see.**

```
  clean model: test accuracy 0.635; loud trigger flips 28.3% of high-risk scores, quiet trigger 32.3%
  Trigger: loud (one lab value at 4.0)
     20 rows (1.0%): test accuracy 0.627, trigger flips  79.2% ...; outlier screen catches  70.0% of the poison
     40 rows (2.0%): test accuracy 0.626, trigger flips 100.0% ...; outlier screen catches  80.0% of the poison
    100 rows (5.0%): test accuracy 0.630, trigger flips 100.0% ...; outlier screen catches  42.0% of the poison
  Trigger: quiet (two at +1.7 / -1.7)
     20 rows (1.0%): test accuracy 0.630, trigger flips  94.0% ...; outlier screen catches  20.0% of the poison
     40 rows (2.0%): test accuracy 0.627, trigger flips 100.0% ...; outlier screen catches  25.0% of the poison
    100 rows (5.0%): test accuracy 0.615, trigger flips 100.0% ...; outlier screen catches  14.0% of the poison
```

**How to read it.**

* **The baseline matters.** On the clean model the triggers already flip about 30% of high-risk scores, because the forest gives the noise columns a little weight and the trigger values are unusual. The attack is the rise above that baseline: from 32.3% to 100% with 2% quiet poison. The gate measures exactly that rise (§7.3).
* **Accuracy barely moves** (at most 0.02), so a holdout check, GRAIMATTER's TECH 6 included, does not see the backdoor. The model behaves normally until someone uses the trigger.
* **The outlier screen** catches most of a loud trigger at low volume and little of a quiet one. With more poison rows, the poison forms its own cluster and looks normal to the screen (loud: 80% caught at 2%, 42% at 5%).

### 3.4 Where each attack sits
> **Slide 20** · **Code:** [`run_aml_demo.py`](../../demo/run_aml_demo.py)


The final table maps each attack to NIST AI 100-2, OWASP ML Top 10, MITRE ATLAS and EU AI Act Art. 15(5); the technical guide (§8.6) has the full crosswalk. `main()` returns the evasion rates, the extraction results per budget, whether the gate let the over-budget request through, and the backdoor results, for the gate.

---

## 4. Demo 4: a tampered supply chain
> **Slides 35, 36 (part 4A); in brief 11** · **Script:** [`demo/run_supply_chain_demo.py`](../../demo/run_supply_chain_demo.py) · **Report:** [`demo/output/supply_chain_report.txt`](../../demo/output/supply_chain_report.txt)


`demo/run_supply_chain_demo.py` attacks the route a model takes to its user rather than the model itself (NISTAML.051). A supplier publishes three files; the user downloads them from a mirror; whoever runs the mirror changes them. The script keeps its working files in `demo/output/supply_chain/supplier/` and `.../mirror/`, which it deletes and recreates on every run (not versioned).

### 4.1 The supplier's release, and the pin
> **Slide 36** · **Code:** [`run_supply_chain_demo.py`](../../demo/run_supply_chain_demo.py), [`supply_chain/integrity.py`](../../demo/supply_chain/integrity.py)


**Code.** The cohort and the forest are the same as demo 3's (§3.0). The supplier writes:

* `model.pkl`: the forest, pickled.
* `bundle.json`: the published accuracy (0.635) and an encryption setting, `{"cipher": "AES-GCM", "key_bits": 256}`. It is only a number in a file: nothing in the demo encrypts anything.
* `constraints.json`: a copy of demo 1's safe-wrapper rules.

`write_lock()` in `supply_chain/integrity.py` computes the SHA-256 of each file (`sha256_file()`, read in 64 KB blocks) and writes `supply_chain.lock.json`. The pins come from the supplier's own release notes, not from the mirror; that is the point of a pin. `ACCEPTANCE_MARGIN = 0.02` is the tolerance of the usual acceptance test.

**What you see.** The three files and the first 12 hex characters of each pin.

Every later file is checked with `_user_checks()`: `verify()` against the pin, then, for a `.pkl`, the import scan (§4.3), and for a JSON file, the floors (§4.4).

### 4.2 A swapped model: the mirror serves a backdoored forest
> **Slide 36 (part 1: 11)** · **Code:** [`run_supply_chain_demo.py`](../../demo/run_supply_chain_demo.py), [`aml_demo/poisoning.py`](../../demo/aml_demo/poisoning.py)


**Code.** The mirror trains a forest on the same rows plus 2% of rows with demo 3's quiet trigger (`poison()` and `quiet_trigger()` from §3.3) and puts it in place of `model.pkl`. The usual acceptance test is holdout accuracy within 0.02 of the published one. `attack_success()` compares the trigger on both models.

**What you see.**

```
  Usual acceptance test: accuracy on the user's own holdout 0.627 against 0.635 published, within 0.02: accepted
  The trigger turns 100.0% of high-risk scores into low risk (32.3% on the supplier's model).
  Import scan: imports only sklearn and numpy (passes)
  Pinned digest: sha256:254a78f5055c against sha256:fac97797542c: digest does not match the pin
```

**How to read it.** The swapped file passes the accuracy test and the import scan, because a backdoor lives in the weights and the file contains exactly the same kinds of objects as a clean forest. Only the pin notices that the file is not the one approved.

### 4.3 Code in the model file: the mirror wraps the genuine forest
> **Slide 36** · **Code:** [`supply_chain/pickle_scan.py`](../../demo/supply_chain/pickle_scan.py), [`supply_chain/payload.py`](../../demo/supply_chain/payload.py)


**Code.** `supply_chain/payload.py` defines `Trojan`, whose `__reduce__` tells pickle "to rebuild me, call `run_then_return(message, model)`". Unpickling therefore calls that function, which appends a line to `payload.LOG` and returns the genuine forest. The mirror pickles a `Trojan` around the supplier's model. `supply_chain/pickle_scan.py` reads the file without loading it: `imports()` walks the pickle opcodes with `pickletools.genops`, following the `GLOBAL`, `STACK_GLOBAL` and memo opcodes to list every `module.name` the file would import, and `scan()` reports those outside the allow list (`sklearn.*`, `numpy.*` and three standard helpers). The script then loads the file anyway to show what would have happened.

**What you see.**

```
  Import scan, without loading: imports supply_chain.payload.run_then_return (refuses)
  Pinned digest: sha256:d7083b5feaef against sha256:fac97797542c: digest does not match the pin
  Had the user loaded it anyway: accuracy 0.635, and the payload log reads ['code in model.pkl ran while the file was loading'].
```

**How to read it.** The loaded model predicts exactly like the original (accuracy 0.635), so any test run after loading passes, and by then the code has already run. Here it writes one line; in the incidents ATLAS records (AML.CS0031) it opened a reverse shell. The scan and the pin both catch it. Formats that cannot hold code (safetensors) remove the problem instead of scanning for it.

### 4.4 A downgrade: one number in a configuration file
> **Slide 36** · **Code:** [`supply_chain/downgrade.py`](../../demo/supply_chain/downgrade.py)


**Code.** Two downgrades, both checked by `supply_chain/downgrade.py`:

1. The mirror's `bundle.json` says `key_bits: 40`. `brute_force_years(bits)` computes `2^bits / 10^9 / seconds per year`, the time to try every key at a billion keys a second, and `readable_duration()` prints it.
2. The mirror's `constraints.json` lowers the wrapper's minimum leaf from 20 to 1 and raises the maximum depth from 4 to 100. The script trains demo 1's `SafeDecisionTreeClassifier` (§1.5) on 500 rows twice, once with each rules file, and calls `request_release()` on both.

`below_floor(name, config)` compares a downloaded configuration with floors kept **in code** (`KEY_BITS_FLOOR = 128`, `WRAPPER_FLOORS`), not in the file.

**What you see.**

```
     40 bits: 18 minutes
     56 bits: 2.3 years
    128 bits: 1.1e+22 years
    256 bits: 3.7e+60 years
  Floor kept in code: key_bits = 40, floor 128 (refuses)
  Supplier's rules: smallest leaf 21 rows; request_release(): Run file through the next step of the checking procedure
  Mirror's rules:   smallest leaf 1 row;  request_release(): Run file through the next step of the checking procedure
  Floor kept in code: min_samples_leaf min 1, floor 20; max_depth max 100, floor 4 (refuses)
```

**How to read it.** In both cases everything still works: encryption with a 40-bit key still encrypts and decrypts, and the wrapper still trains and still recommends the next step. What changed is the protection. The wrapper approves a tree whose smallest leaf is one person, because it is only as strict as the rules file it reads. A check that trusts the file it checks against can be switched off by editing that file; a floor in reviewed code cannot.

### 4.5 Side by side
> **Slide 36** · **Code:** [`run_supply_chain_demo.py`](../../demo/run_supply_chain_demo.py)


**What you see.**

```
  Tampered file                    Usual check          Usual     Pin      Scan or floor
  Swapped model with a backdoor    holdout accuracy     passes    refuses  passes
  Code hidden in the pickle        holdout accuracy     passes    refuses  refuses
  Key length 256 -> 40 bits        functional test      passes    refuses  refuses
  Safe-wrapper floor 20 -> 1       request_release()    passes    refuses  refuses
4 of 4 tampered files pass the usual check; 0 of 4 pass the pin and the scan or floor.
```

**How to read it.** The pin refuses all four. The content checks refuse three; the backdoor needs the pin. "0 of 4" is the number the gate reads (§7.3).

### 4.6 What the pin does not catch
> **Slide 36** · **Code:** [`supply_chain/integrity.py`](../../demo/supply_chain/integrity.py)


**Code.** The script writes a second lock file from the mirror's own (backdoored) model and verifies against it.

**What you see.** `the backdoored forest verifies: digest matches the pin.`

**How to read it.** A digest proves a file is the one that was pinned, not that the pinned file is sound. If the pin is taken from the download, or the supplier's own build was compromised, the pin accepts the attack. What covers that gap: signatures that say who published a file (Sigstore, OpenSSF model signing), provenance that says how it was built (SLSA), an AI bill of materials, and testing supplied models as untrusted. `main()` returns the accuracies, the trigger success, the counts in §4.5 and this last result.

---

## 5. Demo 5: confidentiality, the simple version

> **Slides 32 to 34** (part 4A) · **Script:** [`demo/run_confidentiality_demo.py`](../../demo/run_confidentiality_demo.py) · **Attacks:** [`confidentiality_demo/membership.py`](../../demo/confidentiality_demo/membership.py), [`confidentiality_demo/attribute.py`](../../demo/confidentiality_demo/attribute.py) · **Working (the arithmetic behind each number):** [`confidentiality_demo/explain.py`](../../demo/confidentiality_demo/explain.py) · **Report:** [`demo/output/confidentiality_report.txt`](../../demo/output/confidentiality_report.txt) · **Tests:** [`tests/test_confidentiality.py`](../../tests/test_confidentiality.py)

**In one sentence.** A model that memorised its training data gives away who was in it, and what is in their records, to anyone who can ask it questions.

**Why it is here.** Part 4A goes through the three properties of the CIA triad. Demo 3 shows integrity, demo 4 the supply chain; this demo shows confidentiality (NIST calls it privacy, NISTAML.03) in its simplest form, so the idea is clear before part 4B runs GRAIMATTER's full checks (demos 1 and 2). It needs only what any user of the model gets: send a row, read the answer.

**The words used below.**

| Word | Meaning |
| --- | --- |
| Member | A person whose row was used to train the model. Their privacy is what the attacks target. |
| Stranger | A person from the same population whose row the model never saw. |
| Confidence in the truth | The probability the model gives to a person's real outcome. Near 1.0 means "the model is sure about this person". |
| Threshold | The confidence above which the attacker calls someone a member. |
| AUC | How well a score separates members from strangers, over every possible threshold: 0.5 says nothing, 1.0 separates them perfectly. |
| TPR (true positive rate) | Share of real members the attacker calls members. In the code: `members_caught`. |
| FPR (false positive rate) | Share of strangers the attacker wrongly calls members. In the code: `false_alarms`. |
| Bootstrap sample | The rows one tree of a random forest trains on: as many rows as the training set, drawn at random with replacement, so each tree sees about 63% of the people. |

**Every number, traced.** No number in this demo has to be taken on trust. Under each result the report prints a `Working.` line with the counts and the sum that produce it, computed by [`confidentiality_demo/explain.py`](../../demo/confidentiality_demo/explain.py). The table gathers them; the subsections below explain each one step by step.

| Number (slide 33) | What it is | How it is computed | With this run's counts | Code |
| --- | --- | --- | --- | --- |
| 1.000 / 0.605 | Model accuracy on its training rows / on strangers | rows labelled right ÷ rows | 1,000 / 1,000; 605 / 1,000 | `run_confidentiality_demo.py`, §5.0 block |
| **0.83** | Members' average confidence in the truth (a check only we can do; steps 2 and 3 do not use it) | sum of the 1,000 members' confidences ÷ 1,000 | 831.39 / 1,000 = 0.631 × 1.00 + 0.369 × 0.54 | `membership.confidence_in_truth()`; `explain.member_average()` |
| **0.54** | Strangers' average confidence in the truth (same: a check, not an input) | sum of the 1,000 strangers' confidences ÷ 1,000 | 542.61 / 1,000 = 0.605 × 0.64 + 0.395 × 0.39 | `membership.confidence_in_truth()`; `explain.stranger_average()` |
| 63.1% | Share of the members each tree saw | expected 1 − (1 − 1/1,000)^1,000 = 0.632; counted over the 200 trees | 0.631 | `explain.trained_on()`, `explain.bootstrap_share()` |
| 0.567 | The most a tree that copies a neighbour can get right about a stranger | average of p² + (1 − p)² over the strangers' true risk p | 0.567 (the trees reach 0.54) | `cohort.risk_probability()`, `explain.coin_agreement()` |
| **0.72** | The threshold | 90th percentile of the attacker's 200 strangers (`np.quantile`, linear) | position 0.9 × (200 − 1) = 179.1 in the sorted list; values no. 179 and 180 are both 0.720 | `membership.calibrate_threshold()`; `explain.threshold_working()` |
| **96.0%** | Members called members (true positive rate, TPR) | members above 0.72 ÷ members | 960 / 1,000 | `membership.evaluate()` (`members_caught`); `explain.call_counts()` |
| **12.4%** | Strangers called members (false positive rate, FPR) | strangers above 0.72 ÷ strangers | 124 / 1,000 | `membership.evaluate()` (`false_alarms`); `explain.call_counts()` |
| 960 / 124 | Members / strangers in each band of confidence, with the cut as a line | count per band; above the line = called member | 273 + 575 + 112; 109 + 15 | `explain.score_bands()` |
| 91.8% | Attacker right on a 50/50 mix | 0.5 × TPR + 0.5 × (1 − FPR) | 0.5 × 96.0% + 0.5 × 87.6% | `membership.evaluate()` (`accuracy`) |
| 88.6% / 7.2% | Share of the people called members who really are, with half members (1:1) / one member per 100 strangers (1:100) (slide 34) | m × TPR / (m × TPR + FPR), m = members per stranger | 960 / (960 + 124); 9.6 / (9.6 + 124) | `explain.flagged_who_are_members()` |
| 92.1% / 77.6% | Attacker right with a stricter cut: 95th / 99th percentile (slide 34) | same as 91.8%, with the cut at 0.740 / 0.825 | 0.5 × 92.8% + 0.5 × 91.4%; 0.5 × 56.1% + 0.5 × 99.2% | `membership.calibrate_threshold()`, `membership.evaluate()` |
| 0.976 | AUC | (pairs where the member scores higher + ½ × ties) ÷ pairs | (975,038 + 0.5 × 2,535) / 1,000,000 | `membership.auc()`; `explain.auc_pairs()` |
| 0.80 / 0.67 | The two people of the worked example | trees voting for their real outcome ÷ 200 | 160 / 200; 134 / 200 | `explain.tree_votes()` |
| **94.4%** | Smoker guessed right, members | right ÷ members | 944 / 1,000 (47 wrong, 9 abstained) | `attribute.guess_field()`, `attribute.success()`; `explain.guess_counts()` |
| **59.6%** | Smoker guessed right, strangers | right ÷ strangers | 596 / 1,000 (399 wrong, 5 abstained) | same |
| 34.8 points | The leak | members' rate − strangers' rate | 94.4% − 59.6% | `run_confidentiality_demo.py`, §5.2 block |
| 62.1% | What the population pattern alone gives | strangers whose smoker flag equals their outcome ("high risk → smoker") | 621 / 1,000 | `explain.population_rule()` |
| Table rows | The same numbers for four releases | the same formulas, per release | printed under the table | §5.3 below |

Run it with `uv run python demo/run_confidentiality_demo.py`. It takes a few seconds, and the gate does not read it (see §5.4).

### 5.0 The data and the model

> **Slide 33**, step 1 · **Code:** [`run_confidentiality_demo.py`](../../demo/run_confidentiality_demo.py), the block under "Demo guide §5.0" and `forest()`

**Code.** One call to `sample_cohort(2200, rng, n_noise=10)` (§0.3), cut into three groups that never overlap: 1,000 **members** train the model, 1,000 **strangers** are the yardstick, and 200 more strangers are the **attacker's reference**, people the attacker knows were not in the training data. Ten noise columns, as in demo 1, give a deep model something to tell people apart with. `forest(min_leaf=1)` is a `RandomForestClassifier` with 200 trees like demo 3's, but grown until each training person sits alone in a leaf.

**What you see.**

```
Model: random forest, 200 trees, grown to one row per leaf. Accuracy on its own training rows: 1.000. On strangers: 0.605.
    Working. Labels right: 1000 / 1000 training rows = 1.000; 605 / 1000 strangers = 0.605.
```

**Where the numbers come from.** Accuracy is "labels right ÷ rows". The model gives the right label to all 1,000 of its training rows (1.000) and to 605 of the 1,000 strangers (0.605).

**How to read it.** The outcome is a weighted coin toss (§0.3), so no honest model gets far above 0.6. A perfect 1.000 on the training rows can only mean the model remembers the answers. That memory is what the attacks read.

### 5.1 Membership inference: was this person in the training data?

> **Slide 33**, steps 2 to 4; **slide 34**, what the cut means · **Code:** [`confidentiality_demo/membership.py`](../../demo/confidentiality_demo/membership.py): `confidence_in_truth()` (ask), `calibrate_threshold()` (calibrate), `decide()` (decide), `evaluate()` and `auc()` (score the attacker) · **Working:** [`confidentiality_demo/explain.py`](../../demo/confidentiality_demo/explain.py)

**Why it matters.** Being in a dataset can be the secret: if a model was trained only on the patients of one clinic, proving someone was in its training data proves they were a patient there (NISTAML.033).

**Code, in three steps.** The function names are the steps.

1. **Ask.** `confidence_in_truth(model.predict_proba, rows, outcomes)` sends each row to the model and picks, from the two probabilities it returns, the one for the person's real outcome. The attacker needs the real outcome, which is realistic: an insurer or an employer may already hold it.
2. **Calibrate.** `calibrate_threshold(reference_scores)` takes the confidence on the attacker's 200 known strangers and returns their 90th percentile (`FALSE_ALARM_RATE = 0.10`): the value at most 10% of them exceed. That is what "high for a stranger" looks like.
3. **Decide.** `decide(scores, threshold)` calls everyone strictly above it a member.

`evaluate()` then compares the calls with the truth: the share of members caught, the share of strangers wrongly called members, the accuracy on a 50/50 mix, and the AUC. `auc()` is written out in four lines so you can see what it counts: the chance that a random member scores higher than a random stranger.

**What you see.**

```
  Step 1, ask.       One confidence per person: 1000 members, 1000 strangers and the attacker's 200. These individual numbers, not their averages, go to steps 2 and 3.
    Working. Every tree holds one training person per leaf, so each tree votes 1 or 0 for a person's real outcome, and the confidence is the share of the 200 trees that vote 1.
    The attacker's 200 strangers (used in step 2), first 8: 0.715, 0.450, 0.520, 0.160, 0.460, 0.710, 0.510, 0.585, ...
    People being tested (used in step 3), first 5 members: 0.800, 0.785, 0.905, 0.935, 0.915, ...
                                      first 5 strangers: 0.670, 0.225, 0.545, 0.530, 0.695, ...
    The attacker does not know which tested people are members: that is what step 3 decides. The labels above are ours.
  Step 2, calibrate. Threshold 0.72: the 90th percentile of the attacker's 200 strangers, so at most 10.0% of them score above it.
    Working. Sort the 200 confidences from low to high. The 90th percentile sits at position 0.9 x (200 - 1) = 179.1, counting from 0: value no. 179 is 0.720, no. 180 is 0.720, so 0.720 + 0.1 x (0.720 - 0.720) = 0.720.
    Check: 18 of the 200 (9.0%) are strictly above 0.72; 4 sit exactly on it and count as 'not a member'.
  Step 3, decide.    Called members: 96.0% of the real members, 12.4% of the strangers.
    Person by person, members:   0.800 > 0.72 -> member, 0.785 > 0.72 -> member, 0.905 > 0.72 -> member, 0.935 > 0.72 -> member, 0.915 > 0.72 -> member, ...
    Person by person, strangers: 0.670 <= 0.72 -> not a member, 0.225 <= 0.72 -> not a member, 0.545 <= 0.72 -> not a member, 0.530 <= 0.72 -> not a member, 0.695 <= 0.72 -> not a member, ...
    Working. Members above 0.72: 960 of 1000 = 96.0% (true positive rate, TPR). Strangers above 0.72: 124 of 1000 = 12.4% (false positive rate, FPR).
    The FPR is 12.4%, not the 10.0% aimed for, because the threshold was set on 200 strangers, a small sample of the population.
  A check only we can do (we know who is a member): average confidence, members 0.83, strangers 0.54. Steps 2 and 3 do not use these averages, and the attacker cannot compute them; they show in advance that members score higher.
    Members:   sum of the 1000 confidences 831.39 / 1000 = 0.83. Each tree trained on a bootstrap sample and saw 63.1% of the members; those trees always vote 1 (1.00); the trees that did not see a member vote 1 in 0.54 of cases, as for a stranger: 0.631 x 1.00 + 0.369 x 0.54 = 0.83.
    Strangers: sum 542.61 / 1000 = 0.54. No tree saw them. The model's label is right for 605 of them (average confidence 0.64) and wrong for 395 (0.39): 0.605 x 0.64 + 0.395 x 0.39 = 0.54.
    Why 63.1%: each tree draws 1000 rows from the 1000 members, putting each back. One member is missed by one draw with probability 0.999, by all 1000 with 0.999^1000 = 0.368 (about 1/e), so is picked with 1 - 0.368 = 0.632. Counted over the 200 trees of this run: 0.631.
    Why 0.54: a tree that never saw a person puts them in the leaf of a similar training person and copies that person's label. Each outcome is a weighted coin (weight p = the person's true risk), and two coins with the same p agree with probability p^2 + (1 - p)^2. Averaged over the 1000 strangers' true p: 0.567, the most a tree that copies a neighbour can get right about someone it never saw. The trees also split on the noise columns, so their neighbours are less similar: 0.54. A blind coin would give 0.50.
  How the three steps connect: ask gives one number per person; calibrate picks one cut, using only people known to be outsiders; decide applies that same cut to everyone.
    Confidence    Members  Strangers  Attacker's 200
    <= 0.50             0        397              79
    0.50-0.60           0        212              43
    0.60-0.70          26        227              51
    0.70-0.72          14         40               9
    ---- threshold 0.72: below = not a member, above = called member ----
    0.72-0.80         273        109              13
    0.80-0.90         575         15               5
    > 0.90            112          0               0
    Above 0.72: 273 + 575 + 112 = 960 members, 109 + 15 + 0 = 124 strangers, 18 of the attacker's 200 (step 2's cut: at most 10%).
    Why most members pass: above 0.72 means at least 145 of 200 trees. Between 101 and 147 trees saw each member (126 on average) and vote 1 for sure, so a typical member needs only 19 more from the 74 trees that did not see them. The 40 who miss were seen by fewer trees (120 on average), and the other trees voted for their real outcome only 24.0% of the time (55.6% for the members who pass): their outcome goes against that of similar people.
    Why few strangers pass: no tree saw them, so at least 145 trees must get them right by copying a similar person. That happens when the outcome was predictable: the 124 who pass had, on average, a 74.3% true chance of the outcome they got; the rest 54.0%.
    Why 12.4% and not 10.0%: the cut was set on 200 strangers (0.72). On the 1000 strangers the 90th percentile would be 0.735, so a little more than 10% of them sit above 0.72.
Right 91.8% of the time on a 50/50 mix (a coin toss gets 50%). AUC 0.976 (0.5 = no signal, 1.0 = every member stands out).
    Working. Right = 0.5 x TPR + 0.5 x (100% - FPR) = 0.5 x 96.0% + 0.5 x 87.6% = 91.8%.
    AUC: each of the 1000 members against each of the 1000 strangers, 1,000,000 pairs. Member higher in 975,038, tied in 2,535: (975,038 + 0.5 x 2,535) / 1,000,000 = 0.976.

What 'above the cut' means: the attacker only knows that few outsiders score that high. Of the people called members, how many really are depends on the mix being tested. Other cuts, same scores:
    Cut (outsiders above)  Threshold     TPR     FPR   Right  Members among called, 1:1   1:100
    80th percentile (20%)      0.676   99.5%   21.6%   88.9%                      82.2%    4.4%
    90th percentile (10%)      0.720   96.0%   12.4%   91.8%                      88.6%    7.2%
    95th percentile (5%)       0.740   92.8%    8.6%   92.1%                      91.5%    9.7%
    99th percentile (1%)       0.825   56.1%    0.8%   77.6%                      98.6%   41.2%
    Working, 90th row: 1:1 means 1000 members and 1000 strangers tested: 960 / (960 + 124) = 88.6% of the people called members are members. 1:100 means 10 members per 1,000 strangers: 9.6 / (9.6 + 124) = 7.2%.
    A stricter cut accuses fewer strangers and finds fewer members. 'Right' barely moves from the 90th to the 95th percentile and falls at the 99th; what a stricter cut buys is more confidence in each accusation.

Two people, both high risk, as the attacker sees them:
  Member   (age 86, diabetes no, weight normal, smoker no): confidence 0.80 = 160 of 200 trees -> called member
  Stranger (age 89, diabetes yes, weight obese, smoker yes): confidence 0.67 = 134 of 200 trees -> called not a member
    The member: 130 trees trained on them and all 130 vote 1; of the 70 that did not, 30 vote 1. 160 / 200 = 0.80, above 0.72.
    The stranger: no tree saw them; 134 of 200 vote 1. 134 / 200 = 0.67, not above 0.72.
```

**Where the numbers come from, step by step.**

*Step 1: one number per person.* The attacker asks the model about every person and keeps one number each. These individual numbers, not any average, are what steps 2 and 3 use.

1. **What the model answers.** For each row, `predict_proba` returns two numbers that add up to 1: the probability of low risk and the probability of high risk. For the member of the worked example it returns `[0.20, 0.80]`. Their real outcome is high risk, so their **confidence in the truth** is 0.80. For a low-risk person it would be the first number.
2. **Why that number is a count of trees.** A random forest answers with the average of its 200 trees. Each tree of this forest grew until every leaf holds one training person, so each tree answers 1.0 for one outcome and 0.0 for the other. The confidence is therefore **the share of the 200 trees that vote for the real outcome**, always a multiple of 1/200 = 0.005. The member's 0.80 is 160 trees out of 200.
3. **What step 1 hands on.** Three lists of numbers. The attacker's 200 strangers (first ones in the output: 0.715, 0.450, 0.520, 0.160, ...) go to step 2. The people being tested (members 0.800, 0.785, 0.905, ...; strangers 0.670, 0.225, 0.545, ...) go to step 3. The attacker does not know which tested person is a member; the labels in the output are ours, to score the attack afterwards.

*The worked example.* The member: 130 of the 200 trees trained on them, and all 130 vote "high risk"; of the 70 trees that did not see them, 30 vote "high risk". 130 + 30 = 160, and 160 / 200 = 0.80. The stranger: no tree saw them, and 134 of 200 vote "high risk": 0.67. The member has fewer risk factors than the stranger, yet gets the higher number: the 130 trees that remember them make the difference.

*Step 2, where 0.72 comes from.*

1. The attacker runs step 1 on their own 200 strangers, which gives 200 confidences.
2. They sort them from low to high. `np.quantile(scores, 0.9)` (inside `calibrate_threshold()`) finds the 90th percentile by position: 0.9 × (200 − 1) = 179.1, counting from 0. That falls between value no. 179 and value no. 180 of the sorted list.
3. Both are 0.720, so the interpolation gives 0.720 + 0.1 × (0.720 − 0.720) = **0.72**. (If they differed, the threshold would be 10% of the way from the first to the second.)
4. Check: 18 of the 200 (9.0%) are strictly above 0.72, and 4 sit exactly on it. `decide()` uses "strictly above", so those 4 are not called members. That is why the report says "at most 10%".
5. Why 10%: it is the attacker's choice, `FALSE_ALARM_RATE = 0.10` in `membership.py`. They accept wrongly accusing one stranger in ten.

*Step 3, where 96.0% and 12.4% come from.*

0. **Person by person.** Each tested person's own number from step 1 is compared with the cut from step 2: the first member, 0.800 > 0.72, is called a member; the first stranger, 0.670 ≤ 0.72, is not. Doing that for everyone and counting gives the two rates below.
1. Compare each of the 1,000 members with 0.72: 960 are above it. 960 / 1,000 = **96.0%**. This is the **true positive rate (TPR)**: real members correctly called members. In the code it is `members_caught`.
2. Compare each of the 1,000 strangers with 0.72: 124 are above it. 124 / 1,000 = **12.4%**. This is the **false positive rate (FPR)**: strangers wrongly called members. In the code it is `false_alarms`.
3. Why 12.4% and not the 10% aimed for: the threshold was set on 200 people. On 1,000 new strangers the share above it is a little different. A small calibration set gives a less exact threshold.
4. **91.8%.** Picture 1,000 members and 1,000 strangers. The attacker is right about the 960 members they call members and about the 876 strangers (1,000 − 124) they leave out: (960 + 876) / 2,000 = 91.8%. The same thing as a formula: 0.5 × 96.0% + 0.5 × 87.6% = 91.8%.
5. **AUC 0.976.** Take every member–stranger pair: 1,000 × 1,000 = 1,000,000 pairs. In 975,038 the member has the higher confidence, in 2,535 they tie. AUC = (975,038 + 0.5 × 2,535) / 1,000,000 = 0.976. It does not depend on any threshold.

*A check only we can do: the averages 0.83 and 0.54.* The attacker cannot compute these, because they would have to know who the members are, and steps 2 and 3 do not use them. We compute them because we know the truth: they show in advance that members score higher than strangers, so a single cut can separate them. If the two averages were equal, no threshold would work. How far apart they are tells you the attack will work well; how well it actually works is the count of step 3.

1. **0.83 is an average.** Add up the confidence of the 1,000 members and divide by 1,000: 831.39 / 1,000 = 0.83.
2. **Why members score so high.** A tree that saw a member keeps them alone in a leaf and **always votes for their real outcome** (1.00). The trees that did not see them vote for it 54% of the time, as for a stranger (point 3 of this check). So the average depends on how many trees saw each member: 63.1% in this run. Then 0.631 × 1.00 + 0.369 × 0.54 = **0.83**.

   *Where the 63% comes from.* Nobody chose it: scikit-learn's random forest uses `bootstrap=True` by default, and `forest()` keeps it. For each tree, 1,000 rows are drawn at random from the 1,000 members **with replacement**, like drawing a ball from an urn of 1,000, writing it down and putting it back, 1,000 times. Some people come out twice or three times, others never, so the 1,000 draws cover only about 632 different people. For one member:
   1. Missed by one draw: 999 / 1,000 = 0.999.
   2. Missed by all 1,000 draws: 0.999^1000 = 0.368, about 1/e (e = 2.718).
   3. Picked at least once: 1 − 0.368 = **0.632**.

   That holds for every member, so each tree sees 63.2% of them on average. The run does not assume it: `explain.trained_on()` reads `estimators_samples_` (the rows each tree drew) and counts, 63.1% over the 200 trees; the gap is chance. For the member of the worked example, 130 of 200 trees (65%). `explain.bootstrap_share()` prints the three steps.
3. **0.54 for strangers.** No tree ever saw a stranger. Their confidences add up to 542.61, so 542.61 / 1,000 = **0.54**. Split by whether the model is right: it gives the right label to 605 strangers (average confidence 0.64) and the wrong one to 395 (average 0.39): 0.605 × 0.64 + 0.395 × 0.39 = 0.54.

   *Why about 54%.* A tree that never saw a person drops them into the leaf of *another* training person with similar values, and votes that person's label. So the vote is right when two similar people have the same outcome.
   1. Each person's outcome is a weighted coin: it lands "high risk" with their own probability p, between about 0.1 and 0.9 depending on age, smoking, diabetes and so on (`cohort.risk_probability()`, §0.3).
   2. Two coins with the same p agree with probability p² + (1 − p)²: 0.50 for p = 0.5, 0.68 for p = 0.2.
   3. Averaged over the 1,000 strangers' true p, that is **0.567** (`explain.coin_agreement()`): the most a tree that copies a neighbour can get right, even if it found a perfectly similar one.
   4. The trees also split on the 10 noise columns, so their "neighbours" are less similar than that: **0.54**. A blind coin would give 0.50.

   The same 0.54 is the vote of the trees that did not see a member (point 2): for them, a member is just another stranger.

*How the three steps connect.* The three steps are one chain, and each one hands a single thing to the next:

1. **Ask** turns every person into **one number**: their confidence, the share of the 200 trees that vote for their real outcome. Members, strangers and the attacker's 200 all get one.
2. **Calibrate** looks **only at the attacker's 200 strangers**, people known to be outsiders, and picks **one cut**: the value at most 10% of them exceed, 0.72. The attacker cannot look at the members here, because they don't know who the members are; that is the whole point.
3. **Decide** applies **that same cut to everyone**: above 0.72 is "member". Then we, who know the truth, count how many real members and how many real strangers landed above it.

The table the report prints shows the chain at a glance: the same bands for the three groups, and the cut from step 2 as a line.

| Confidence | Members | Strangers | Attacker's 200 |
| --- | ---: | ---: | ---: |
| ≤ 0.50 | 0 | 397 | 79 |
| 0.50–0.60 | 0 | 212 | 43 |
| 0.60–0.70 | 26 | 227 | 51 |
| 0.70–0.72 | 14 | 40 | 9 |
| **threshold 0.72** (below: not a member · above: called member) | | | |
| 0.72–0.80 | 273 | 109 | 13 |
| 0.80–0.90 | 575 | 15 | 5 |
| > 0.90 | 112 | 0 | 0 |

Above the line: 273 + 575 + 112 = **960** members (96.0%), 109 + 15 = **124** strangers (12.4%), and 13 + 5 = 18 of the attacker's 200, the cut of step 2. Read down the columns: the members' column is pushed to the bottom, the strangers' to the top, and the line separates them.

* **Why most members pass.** Above 0.72 means at least 145 of the 200 trees. Between 101 and 147 trees saw each member (126 on average) and vote for them for sure (point 2 of the check), so a typical member needs only about 19 more votes from the 74 trees that did not see them, and those trees vote right about 54% of the time. The 40 who miss (1,000 − 960) have two things against them: fewer trees saw them (120 on average), and the other trees voted for their real outcome only 24% of the time, against 56% for the members who pass. Their outcome goes against that of similar people.
* **Why few strangers pass.** No tree saw them, so they have no sure votes: at least 145 trees must get them right by copying a similar person (point 3 of the check). That only happens when the outcome was predictable: the 124 who pass had, on average, a 74% true chance of the outcome they got (from `cohort.risk_probability()`), the rest 54%.
* **Why 12.4% and not 10%.** Step 2 used only 200 strangers, and on them the cut is 0.72. On all 1,000 strangers the 90th percentile would be 0.735. 0.72 is slightly lower, so slightly more than 10% of the 1,000 sit above it. A small calibration sample gives a slightly misplaced cut.

The code for this block: `explain.score_bands()`, `explain.member_shortfall()`, `explain.stranger_predictability()`.

#### What being above the cut means

> **Slide 34** · **Code:** the block "What 'above the cut' means" in [`run_confidentiality_demo.py`](../../demo/run_confidentiality_demo.py); `membership.calibrate_threshold()`, `membership.evaluate()`, `explain.flagged_who_are_members()`

The attacker never learns that a given person is a member. What they know, and what they bet on, is this:

1. **What they know (measured, not assumed).** Few outsiders score high: only 10% of their own 200 known strangers are above 0.72. That is how step 2 built the cut.
2. **What they bet on.** That the model memorised its training data, so members score higher than outsiders and crowd above the cut. In this careless model the bet pays: 960 members are above 0.72 against 124 strangers. With a minimum leaf of 20 (§5.3) it fails: the attacker is right 54.3% of the time, close to a coin.
3. **What it depends on: the mix of people tested.** Of the people called members, the share who really are is the precision of the attack, and it depends on how many members there are among the people tested, not only on the model. With m members per stranger: m × TPR / (m × TPR + FPR).
   * Half and half (1:1, the test of §5.1): 960 members and 124 strangers above the cut, so 960 / (960 + 124) = 960 / 1,084 = **88.6%** of the people called members are members.
   * One member per 100 strangers (1:100): for every 1,000 strangers, 10 members, of whom 96% = 9.6 are caught, against 124 strangers: 9.6 / (9.6 + 124) = **7.2%**. The same cut, the same model, and most accusations are now wrong.

So the 91.8% is not "the chance that a stranger was in the training data". It is how often the attacker is right over a test set with as many members as strangers: 0.5 × TPR + 0.5 × (1 − FPR).

**Would a stricter cut help?** The report recomputes TPR, FPR and right for other cuts on the same scores (the 90th row is slide 33):

| Cut (outsiders above) | Threshold | TPR | FPR | Right (50/50) | Called who are members, 1:1 | 1:100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 80th percentile (20%) | 0.676 | 99.5% | 21.6% | 88.9% | 82.2% | 4.4% |
| **90th percentile (10%)** | **0.720** | **96.0%** | **12.4%** | **91.8%** | **88.6%** | **7.2%** |
| 95th percentile (5%) | 0.740 | 92.8% | 8.6% | 92.1% | 91.5% | 9.7% |
| 99th percentile (1%) | 0.825 | 56.1% | 0.8% | 77.6% | 98.6% | 41.2% |

* **From the 90th to the 95th, right barely moves.** TPR loses 3.2 points (96.0% → 92.8%) and 1 − FPR gains 3.8 (87.6% → 91.4%): 0.5 × 92.8% + 0.5 × 91.4% = 92.1%, against 91.8%.
* **At the 99th, right falls.** Half the members drop below 0.825: 0.5 × 56.1% + 0.5 × 99.2% = 77.6%. But 98.6% of the people called are members (1:1), and even at 1:100 the share rises to 41.2%.
* **What a stricter cut buys is confidence in each accusation, not more right answers.** That is why GRAIMATTER (demo 1) reports the hits at a very low false alarm rate rather than accuracy: what harms one person is an accusation the attacker can trust.

**How to read it.** The model is surer about the people it saw (0.83 against 0.54), and the check after step 3 explains why: two in three of its trees remember each member. That gap is why a single cut works, but the cut itself is applied person by person. With one threshold the attacker finds 96 members in 100 and is wrong about 12 strangers in 100: right 92% of the time where a coin toss gets 50%. The two people at the end are the worked example to show on screen: the model is not reasoning from risk factors, it remembers this person.

### 5.2 Attribute inference: what is the one field I do not know?

> **Slide 33**, step 5 · **Code:** [`confidentiality_demo/attribute.py`](../../demo/confidentiality_demo/attribute.py): `guess_field()` (fill in, ask, guess) and `success()` · **Working:** [`explain.py`](../../demo/confidentiality_demo/explain.py) `guess_counts()`, `population_rule()`

**Why it matters.** The attacker already knows most of a person's record and wants one field, here whether they smoke. If the model memorised that person, it fills in the gap.

**Code.** `guess_field(model.predict_proba, rows, outcomes)` makes two copies of each row, one with `smoker = 0` and one with `smoker = 1` (the true value is overwritten first, so the guess cannot peek), reads the confidence in the person's real outcome for both, and guesses the value the model is surer about. If both copies score exactly the same, it abstains (`-1`), which counts as a miss. `success()` gives the share guessed right. The script runs it on members **and** on strangers.

**What you see.**

```
  Members:   smoking status guessed right for 94.4%.
    Working. 944 right, 47 wrong, 9 abstained (both answers tied; counted as wrong): 944 / 1000 = 94.4%.
  Strangers: smoking status guessed right for 59.6%.
    Working. 596 right, 399 wrong, 5 abstained (both answers tied; counted as wrong): 596 / 1000 = 59.6%.
The strangers' rate is what anyone gets from the population pattern (smokers are more often high risk). The 34.8 points members get on top of it is what the model remembers about them personally.
    Working. 94.4% - 59.6% = 34.8 points. Without any model, the rule 'high risk -> smoker, low risk -> not' is right for 62.1% of the strangers: that is what the population pattern is worth, and the strangers' rate is close to it.

The member of section 1, asked twice (the attacker hides their real smoking status):
  smoker = no : confidence in their real outcome (high risk) 0.80 = 160 of 200 trees
  smoker = yes: confidence in their real outcome (high risk) 0.77 = 154 of 200 trees
  The model is surer with smoker = no (0.80 against 0.77), so the guess is 'no'. Truth: 'no' -> right.
  Why: the trees that trained on this person keep them alone in a leaf. Change the smoking field and, in every tree that splits on it along their path, the row lands in someone else's leaf.
  Note: smokers are more often high risk, so a model reasoning from risk factors would be surer with 'yes'. This one is surer with the person's real value: it remembers them.
```

**Where the numbers come from, step by step.**

1. **One person, two questions.** The worked example is the member of §5.1. The attacker asks with "smoker = no": 160 of 200 trees vote for their real outcome, 0.80. Then with "smoker = yes": 154 trees, 0.77. The model is surer with "no", so the guess is "no". The truth is "no": right.
2. **Why the true value wins.** The 130 trees that trained on this person hold them alone in a leaf. With the true smoking value the row lands back in that leaf and the tree votes for the real outcome. With the false value, every tree that splits on smoking along this person's path sends the row to someone else's leaf, and some of those trees vote the other way. A model reasoning from risk factors would be surer with "yes" (smokers are more often high risk); this one is surer with the real value because it remembers the person.
3. **94.4%.** The same two questions for each of the 1,000 members: 944 guessed right, 47 wrong, and 9 where both answers tied (abstain, counted as wrong). 944 / 1,000 = **94.4%**.
4. **59.6%.** The same for the 1,000 strangers: 596 right, 399 wrong, 5 abstained. 596 / 1,000 = **59.6%**.
5. **Why strangers are above 50%.** Without any model, the rule "high risk → smoker, low risk → non-smoker" is right for 621 of the 1,000 strangers, 62.1%, because smoking raises the risk in the whole population (§0.3). The strangers' 59.6% is close to that: it is the population pattern, not a leak.
6. **The leak.** 94.4% − 59.6% = **34.8 points**: what the model gives away about each member personally.

**How to read it.** Compare the two lines, not one line with 50%. The strangers' rate is what anyone gets from the population pattern; the 34.8 points members get on top of it is what the model remembers about each of them. This is the comparison GRAIMATTER's Appendix E asks for, and demo 1 runs its full version with a planted person (§1.2, slide 41).

### 5.3 Four ways to release the same model

> **Slide 33**, table · **Code:** [`run_confidentiality_demo.py`](../../demo/run_confidentiality_demo.py), the loop under "Demo guide §5.3"; [`membership.py`](../../demo/confidentiality_demo/membership.py) `label_only_confidence()` for the label-only row

**Code.** The same two attacks, rerun on four releases of the same data. Two things change: how far the trees grow (`min_leaf` 1, 10 as demo 3's target, 20 as the floor of demo 1's safe wrapper) and whether the model answers with a probability or only a label. With a label only, step 1 becomes `label_only_confidence()`: 1.0 if the model's label matches the real outcome, 0.0 if not. The attribute attack needs two probabilities to compare, so for the label-only release it prints `n/a`. Under the table the report prints the counts behind every row.

**What you see.**

```
  Release                                        Test acc Attacker    AUC  Smoker  Smoker
                                                             right         member  strngr
  Grown to one row per leaf, probabilities          0.605    91.8%  0.976   94.4%   59.6%
  Grown to one row per leaf, label only             0.605    69.8%  0.698     n/a     n/a
  Minimum leaf 10 (demo 3), probabilities           0.627    57.5%  0.678   64.6%   62.0%
  Minimum leaf 20 (demo 1 floor), probabilities     0.636    54.3%  0.607   62.0%   62.0%

Where each row comes from (same steps as sections 1 and 2):
  Grown to one row per leaf, probabilities:
    Test acc 605 / 1000 strangers labelled right = 0.605. Threshold 0.72; members called 960 / 1000 = 96.0%, strangers called 124 / 1000 = 12.4%; right = 0.5 x 96.0% + 0.5 x 87.6% = 91.8%.
    AUC (975,038 + 0.5 x 2,535) / 1,000,000 pairs = 0.976.
    Smoker: 944 / 1000 members, 596 / 1000 strangers guessed right.
  Grown to one row per leaf, label only:
    Test acc 605 / 1000 strangers labelled right = 0.605. Threshold 1.00; members called 1000 / 1000 = 100.0%, strangers called 605 / 1000 = 60.5%; right = 0.5 x 100.0% + 0.5 x 39.5% = 69.8%.
    AUC (395,000 + 0.5 x 605,000) / 1,000,000 pairs = 0.698.
    Every score is 1 (label right) or 0 (wrong). More than 10% of the attacker's strangers get 1, so the threshold is 1.00 and 'called member' means 'the label is right'.
  Minimum leaf 10 (demo 3), probabilities:
    Test acc 627 / 1000 strangers labelled right = 0.627. Threshold 0.72; members called 242 / 1000 = 24.2%, strangers called 93 / 1000 = 9.3%; right = 0.5 x 24.2% + 0.5 x 90.7% = 57.5%.
    AUC (677,951 + 0.5 x 0) / 1,000,000 pairs = 0.678.
    Smoker: 646 / 1000 members, 620 / 1000 strangers guessed right.
  Minimum leaf 20 (demo 1 floor), probabilities:
    Test acc 636 / 1000 strangers labelled right = 0.636. Threshold 0.69; members called 196 / 1000 = 19.6%, strangers called 110 / 1000 = 11.0%; right = 0.5 x 19.6% + 0.5 x 89.0% = 54.3%.
    AUC (607,487 + 0.5 x 0) / 1,000,000 pairs = 0.607.
    Smoker: 620 / 1000 members, 620 / 1000 strangers guessed right.
```

**Where the numbers come from.** Each row repeats §5.0 to §5.2 with its own model, and its own threshold calibrated on the same 200 reference strangers.

* **Test acc** is strangers labelled right ÷ 1,000 (605, 605, 627, 636).
* **Attacker right** is 0.5 × TPR + 0.5 × (1 − FPR), with the TPR and FPR counts printed for each row.
* **AUC** is (member higher + ½ × ties) ÷ 1,000,000 pairs.
* **Smoker member / strngr** is guessed right ÷ 1,000, for members and for strangers.
* **The label-only row, worked out.** Every score is 1 (the label is right) or 0 (wrong). The model is right about 605 of 1,000 strangers, so far more than 10% of the reference strangers score 1, and the 90th percentile is 1.00. With a threshold of 1.00, `decide()` calls a member everyone whose label is right: all 1,000 members (the model scores 1.000 on its training rows), and the 605 strangers it gets right. TPR 100%, FPR 60.5%: 0.5 × 100% + 0.5 × 39.5% = 69.8%. AUC: a member beats a stranger only when the stranger scores 0 (395 of 1,000) and ties otherwise: (395,000 + 0.5 × 605,000) / 1,000,000 = 0.698.
* **The minimum-leaf rows.** Each leaf now holds at least 10 or 20 training people, so the trees that saw a member no longer vote 1.00 for them automatically. Members called drop from 960 to 242 (leaf 10) and 196 (leaf 20), close to the strangers' 93 and 110.

**How to read it.**

* **Attacker right** is the membership attack on a 50/50 mix: 50% is a coin toss. **Smoker member / strngr** is the attribute attack; the leak is the gap between the two columns.
* **Returning only a label shrinks the leak but does not close it** (91.8% down to 69.8%). A model that is right about every member still gives them away, one right-or-wrong bit at a time.
* **Not memorising closes most of it.** With a minimum leaf of 20 the attacker is at 54.3% and the smoker gap is zero (620 against 620). Each answer is now an average over at least 20 people, so no single person stands out.
* **It costs nothing in accuracy here.** The honest model is more accurate on strangers (0.636 against 0.605), because memorising noise does not help predict new people. That is the usual case for overfitted models, not a law: differential privacy, the strongest defence, does cost some accuracy.

### 5.4 Where the deck goes from here

> **Slides 37 to 52** (part 4B) · **Code:** [`run_demo.py`](../../demo/run_demo.py) (demo 1), [`run_sacroml_demo.py`](../../demo/run_sacroml_demo.py) (demo 2), [`aml_demo/extraction.py`](../../demo/aml_demo/extraction.py) (demo 3, section 2)

The report ends by pointing ahead. This is the teaching version: a single forest, a threshold attack, one hidden field. Part 4B runs GRAIMATTER's checks on the same cohort: demo 1 with a stronger membership attack, a planted person, the safe wrapper and query limits (§1), demo 2 with SACRO-ML's LiRA (§2). The third confidentiality secret, the model itself, is demo 3's extraction (§3.2, slide 39).

`main()` returns the numbers it printed, for the tests. Like demo 6, demo 5 is standalone and the release gate does not read it: membership and attribute inference are already gated through demo 1's numbers (§7.3), with GRAIMATTER's tolerances.

---

## 6. Demo 6: hiding data in a model
> **Slide 53 (part 4B)** · **Script:** [`demo/run_stego_demo.py`](../../demo/run_stego_demo.py) · **Report:** [`demo/output/stego_report.txt`](../../demo/output/stego_report.txt)


`demo/run_stego_demo.py` asks the steganography question of a model: can you hide a message inside it? GRAIMATTER's output checks ask whether a model *leaks* its training data by accident (membership and attribute inference); they do not ask whether someone *wrote* data into it on purpose. This demo shows two channels for doing that, and what removes each. The code lives in `stego_demo/`. Nothing here hides executable code: the payload is a short note or a few fabricated records, standing for data carried out of a TRE.

### 6.0 The carrier model
> **Slide 53** · **Code:** [`run_stego_demo.py`](../../demo/run_stego_demo.py) `network()`


**Code.** `sample_cohort(4000, rng, n_noise=10)`, first 2,000 rows to train, the other 2,000 to measure accuracy. `network()` returns the carrier, `MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=800)` — a neural network rather than a forest, because a neural network has a large array of float weights to hide bits in. `_flat_weights()` concatenates its `coefs_` into one float32 vector; `with_weights(model, flat)` returns a deep copy of the trained model with only those weights replaced, keeping the intercepts and everything else, so a changed-weights copy predicts exactly as the original minus the change.

**What you see.** `Carrier network trained on 2000 rows. Accuracy on the other 2000: 0.575. It has 10,304 weights.` The accuracy is about what the noisy label allows (§0.3); the weight count is what sets the channel's capacity.

### 6.1 In the weights: LSB steganography
> **Slide 53** · **Code:** [`stego_demo/weights.py`](../../demo/stego_demo/weights.py)


**Code.** `stego_demo/weights.py`. A float32 holds a sign bit, 8 exponent bits and 23 mantissa bits. The lowest mantissa bits carry almost no magnitude: the k-th lowest is worth about 2^(k−24) of the number, so overwriting the bottom eight changes a weight by around one part in 32,000. `embed(weights, payload, bits_per_weight=8)` writes a 32-bit length header and the payload bytes into the low 8 bits of successive weights; `extract()` reads them back; `capacity_bytes()` is `n_weights * bits // 8` minus the header. `max_abs_shift()` reports the largest change any single weight took. The payload, `SECRET`, is a fabricated 111-byte note with made-up medical record numbers.

**What you see.**

```
Using the lowest 8 of each weight's 23 mantissa bits, the channel holds 10,300 bytes. The payload is 111 bytes.
  Largest change to any one weight: 3.01e-06. Accuracy after hiding: 0.575 (was 0.575).
  Payload read back from the weights: exact match (111 bytes).
```

**How to read it.** The 10,304-weight network holds about 10 KB in its low bits. Hiding 111 bytes moves no weight by more than 3e-06 and leaves test accuracy unchanged to three decimals. An accuracy-only release check — GRAIMATTER's TECH 6, and the gate in §7 — sees an ordinary model and passes it, while the data rides out of the TRE inside it. A larger network holds proportionally more: a few million weights hold a megabyte, which is how EvilModel (Wang et al. 2021) hid whole malware files in a convolutional network without changing its outputs.

### 6.2 In the behaviour: a watermark/backdoor channel
> **Slide 53** · **Code:** [`stego_demo/behaviour.py`](../../demo/stego_demo/behaviour.py)


**Code.** `stego_demo/behaviour.py`. Here the message is not in the bytes but in what the model answers. `triggers_for(payload, n_features, rng)` turns the payload (with the same 32-bit header) into one trigger row per bit; `_trigger_keys()` draws those rows from a wide Gaussian (std 20) far outside the cohort's value ranges, so they sit apart from one another and from any real record. `plant(train_x, train_y, keys, bits, repeat=5)` appends each trigger, labelled with its bit, to the training set a few times over, so the handful of triggers carry enough weight for the model to memorise them while its accuracy on real rows holds. `read_back(predict, keys)` queries the triggers and reads the predicted labels back as the payload; `recovered_fraction()` is the share of bits returned correctly.

**What you see.**

```
  248 trigger rows carry a 27-byte message, one bit each, added to the training set (each repeated a few times) far outside the cohort's ranges.
  Accuracy on real rows: 0.632 (clean model 0.575). Planted bits returned correctly: 100.0%.
  Message read from the triggers: exact match.
```

**How to read it.** The message `owner=lab42; contact=hidden` goes in as 248 trigger rows (27 bytes plus the 4-byte header, eight bits each). The watermarked model answers real rows as well as the clean one — a touch better here, within the label's noise — and returns every planted bit, so the message comes back exactly. This is backdoor watermarking (Adi et al. 2018) used as a covert channel; the same mechanism is how a model can be made to memorise and later disgorge a secret on a chosen prompt (Song et al. 2017). Because the message lives in the decision function, editing the weight bytes does not remove it (§6.3).

### 6.3 Defences: what each one removes
> **Slide 53** · **Code:** [`stego_demo/defences.py`](../../demo/stego_demo/defences.py)


**Code.** `stego_demo/defences.py`. `clip_low_bits(weights, bits)` zeroes the lowest mantissa bits; `quantise_fp16()` rounds to float16 and back, as an export pipeline would to shrink a model; `add_noise(weights, relative, rng)` adds Gaussian noise scaled to the weights. `payload_survives()` is the share of payload bytes that come back unchanged after a transform. `lsb_balance()` is the mean of the low bits across all weights, a cheap detection test. The script applies each transform to the stego weights through `with_weights()` and re-measures accuracy and payload.

**What you see.**

```
  Transform on the stego weights          accuracy   LSB payload survives
  clip lowest 16 mantissa bits             0.575        0.0%
  quantise to float16 and back             0.575        0.0%
  add 0.1% relative Gaussian noise         0.573        0.0%

  The behavioural channel against the same weight transforms:
    after clip lowest 16 mantissa bits         planted bits still returned: 100.0%
    after quantise to float16 and back         planted bits still returned: 100.0%

  Low-bit distribution test (mean of the lowest 4 bits, over all weights):
    clean weights  0.314
    stego weights  0.314
```

**How to read it.**

* **Removing the weight channel is easy and cheap.** Clipping the low 16 bits, rounding to float16, or adding 0.1% noise each keeps accuracy (0.575, 0.575, 0.573) and destroys the hidden payload completely — the low bits that held it are overwritten or scrambled. Any one transform, applied to every released model, closes the channel. This is the same "cut the low bits" step the coordinator's defences list and NIST AI 100-2 recommend before release.
* **The behavioural channel is not touched by them.** After clipping or quantising the weights, every planted bit still comes back, because the message is in the function, not the bytes. Removing a planted behaviour needs fine-tuning on clean data, heavy noise, or training with differential privacy, which is the general defence against backdoors in NIST AI 100-2e2025.
* **Detection is weak; removal is reliable.** The low-bit distribution reads the same for the clean and stego models (0.314 both), because the payload fills the low bits of only about 115 of the 10,304 weights — far too few to move a statistic taken over all of them. A detector would have to know where the payload sits. This is the lesson for a TRE: do not try to spot hidden data after the fact; transform every released model so the capacity is gone.

### 6.4 Where it sits, and what GRAIMATTER should take from it
> **Slide 53** · **Code:** [`run_stego_demo.py`](../../demo/run_stego_demo.py)


The closing table maps each channel to its source and to NIST AI 100-2e2025: the weight channel to confidentiality and exfiltration (EvilModel, Wang et al. 2021), the watermark to backdoor and integrity (Adi et al. 2018), and memorisation to data leakage (Song et al. 2017). The point for GRAIMATTER is that an output check trusting accuracy alone cannot see either channel, so a TRE's safe-export step should transform every released model — clip the low bits or quantise, and prefer differentially private training — rather than rely on spotting the hidden data. This demo is standalone: unlike demos 1, 3 and 4 it is not wired into the release gate, because the gap it shows is closed by a release-time transform, not by a tolerance on a number.

---

## 7. The release gate
> **Slide 56** · **Script:** [`demo/run_gate.py`](../../demo/run_gate.py) · **Report:** [`demo/output/gate/`](../../demo/output/gate/)


`demo/run_gate.py` turns the crosswalk of the technical guide (§8.6) into a check that can block a release in CI. The pattern comes from [safety-trust-engine](https://github.com/olonok69/safety-trust-engine): controls mapped to evidence, numeric tolerances, a verdict per control, and a report.

### 7.1 What `run_gate.py` does, step by step
> **Slide 56** · **Code:** [`run_gate.py`](../../demo/run_gate.py)


1. **Parse the options.** `--demos` (default `1,2,3,4`), `--regimes` (default `eu_uk,nist_aml,graimatter`), `--fail-under metric=value` (override a tolerance), `--accept-missing` (demos declared out of scope), `--out`, `--show-demos`. `_demo_names()` and `_limits()` validate them.
2. **Run the demos.** `run_demos()` imports each script as a module (`SCRIPTS` maps `demo1` to `run_demo` and so on) and calls its `main()`, with the demo's printing silenced unless `--show-demos`. If `sacroml` is not installed, demo 2 is skipped with a message instead of failing. The result is `evidence`: demo name → the dictionary its `main()` returned.
3. **Judge.** `build_report()` in `compliance_gate/gate.py` (§7.4).
4. **Write and exit.** The report is written as `gate_<packs>.json` and `.md`; the script prints one line per category, the control counts, and `Gate: PASS` or `FAIL`, and returns exit code 0 or 1.

### 7.2 Controls and regime packs (`compliance_gate/controls.py`)
> **Slide 56** · **Code:** [`compliance_gate/controls.py`](../../demo/compliance_gate/controls.py)


A `Control` is one obligation the demos can evidence:

* `regulation`, `ref`, `label`: what it is, e.g. EU AI Act, Art. 15(5) model evasion.
* `stages`: the demos that must run for it to be evidenced.
* `categories`: the categories whose breach fails it.
* `binding`: `statute` (law), `guidance` (voluntary), `supervisory` (examiner expectation) or `recommendation` (the green paper), so the report never implies more than it can.

Controls are grouped in four packs: `eu_uk` (Art. 15(5) and the UK Code / ETSI EN 304 223), `nist_aml` (NIST AI 100-2 attack classes), `graimatter` (TECH 6, 7, 9-10, 11, 16, plus the SACRO-ML cross-check) and `us` (NIST AI RMF MEASURE and GOVERN, federal model risk management SR 26-02). `--regimes all` selects all four. The ten categories are listed in `CATEGORIES`.

### 7.3 Metrics, tolerances and readers (`compliance_gate/tolerances.py`)
> **Slide 56** · **Code:** [`compliance_gate/tolerances.py`](../../demo/compliance_gate/tolerances.py)


`METRICS` defines one `MetricSpec` per number the gate judges: its category, the demo that produces it, its tolerance, a description, and two switches. `inclusive=True` breaches at `value >= limit` (demo 1's rule) instead of `value > limit`; `max_p` means the metric breaches only if its p-value is also at most that (FDIF). The privacy tolerances are read from demo 1's `POLICY`, so the gate and `decide()` cannot drift apart; the others are set here for the workshop (evasion 10%, copy agreement 80%, backdoor lift 10 points, zero for the counts).

The **readers** turn each demo's `main()` result into `Reading`s, without recomputing anything:

| Reader | Reads | Metrics |
| --- | --- | --- |
| `demo1_readings()` | the candidate (wrapped tree), the refusals, the tamper recommendation, the query log | membership AUC, advantage, TPR at 10% FPR, FDIF with p; attribute risk ratio; accuracy gap; stored rows; size ratio; disclosive files released (of 5); sweep rows allowed |
| `demo2_readings()` | the wrapped tree's AUCs, the two flags | mean SACRO-ML AUC; configurations not flagged (of 2) |
| `demo3_readings()` | evasion rates, extraction at the gate's budget (200), the over-budget request, the backdoor rows | three evasion rates; copy agreement; over-budget request allowed; backdoor lift = worst trigger success after poisoning minus the clean model's success for the same trigger |
| `demo4_readings()` | the count of tampered files accepted | supply-chain files accepted (of 4) |

`breaches(spec, reading, limit)` applies the rule. A missing value never breaches; it shows as "not measured".

### 7.4 Verdicts (`compliance_gate/gate.py`)
> **Slide 56** · **Code:** [`compliance_gate/gate.py`](../../demo/compliance_gate/gate.py)


`build_report(evidence, regimes, overrides, accept_missing)`:

1. Merges the tolerances with any `--fail-under` overrides (an unknown metric name is an error).
2. Reads every demo that ran and builds a `MetricVerdict` per reading, grouped into a `CategoryVerdict` per category. A category is **within** tolerance when none of its metrics breaches.
3. Gives each selected control a `ControlVerdict`: **not_evidenced** if one of its demos did not run (marked `accepted` when all the missing demos were declared with `--accept-missing`); otherwise **fail** if any of its categories breached, else **pass**.
4. `GateReport.passed` is true only if every category is within tolerance and every control passes or is an accepted not_evidenced. There is never a silent green: a control without evidence fails the run unless the run says why.

`write_json()` and `write_markdown()` write the same content for machines and for people, with the disclaimer that the mapping and tolerances were made for this repository.

### 7.5 Reading the seeded report
> **Slide 56** · **Code:** [`demo/output/gate/`](../../demo/output/gate/)


`demo/output/gate/gate_eu_uk-nist_aml-graimatter.md` is the run on demos 1, 3 and 4 with demo 2 declared out of scope:

* **Tolerance gate.** Every privacy metric of demo 1 is within tolerance (they are the same numbers that let `decide()` release the wrapped tree in §1.5). Evasion (78.7%, 32.8%, 20.7% against 10%), extraction (86.9% against 80%) and poisoning (a lift of 71.7 points against 10) breach. Supply chain: 0 of 4 accepted, within.
* **Controls.** The GRAIMATTER pack passes, apart from the SACRO-ML cross-check, which is not evidenced (out of scope). Art. 15(5) fails on data poisoning, evasion and confidentiality (because of extraction), and passes on model poisoning thanks to demo 4. The NIST controls follow the same split.
* **The lesson.** The model that GRAIMATTER's privacy checks release is not resilient in the sense of Art. 15(5). Privacy is one branch of AML.

`gate_us.md` is the same evidence through the US pack.

### 7.6 The gate in CI, and the tests
> **Slide 56** · **Code:** [`.github/workflows/gate.yml`](../../.github/workflows/gate.yml), [`tests/test_gate.py`](../../tests/test_gate.py)


`.github/workflows/gate.yml` runs two jobs. `lint-and-test` runs `ruff` and `pytest`. `gate` runs the gate twice: the GRAIMATTER pack on demo 1, which must pass, and all packs on demos 1, 3 and 4, which must exit with 1 and breach exactly evasion, extraction and poisoning. A gate that blocked for any other reason, or stopped blocking, would turn CI red.

`tests/test_gate.py` reruns demos 1, 3 and 4 and checks that their reports still match the versioned files in `demo/output/`, apart from the machine-dependent lines listed in §8 (`test_regenerated_outputs_match_versioned`), that the gate decides as demo 1's `decide()` does, and that the seeded verdicts are the ones in §7.5. That is why a change to a demo's numbers must come with its regenerated report.

---

## 8. Reproducibility and known caveats

* **Seeds.** Demos 1, 3 and 4 give the same report on every run with the same library versions. The tests rely on that. A different scikit-learn version can change a forest and therefore the numbers.
* **Demo 2 is not reproducible run to run.** The package's attacks draw their own random splits; the mean membership AUC of the wrapped tree moved from 0.494 to 0.487 between two runs. Its `report.json` files are appended to on every run, not replaced. Demo 2 is therefore outside CI and its gate control is declared out of scope there.
* **Lines that depend on the machine.** Demo 1's last line prints the absolute path of the machine that ran it (for example `Full write-up: D:\repos\...`). The pickled size of the unconstrained tree (§1.4) and the digests of pickled models (§4.1 to §4.3) change between scikit-learn versions, so your digests may differ from the ones quoted here; the verdicts do not. `_normalise()` in the tests masks those three things before comparing.
* **`n_jobs=-1`** in demos 3 and 4 uses every core; it changes speed, not results.
* **Scale.** The cohorts are hundreds or thousands of rows, the models are trees and forests, and the attacks are teaching sketches. The technical guide (§25) lists what the demos do not show.
