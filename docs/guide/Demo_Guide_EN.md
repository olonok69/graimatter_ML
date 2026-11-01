# The Demos, Explained: Code and Output Walkthrough

**What each demo does, how the code does it, and how to read what it prints**

This guide is for the five demo scripts in `demo/` and the release gate that judges them. The [technical guide](AML_Technical_Guide_EN.md) explains the attacks and the frameworks, and the [presenter guide](Presenter_Guide_EN.md) follows the deck. This guide follows the code: for every section a demo prints, it says which functions produce it, what they compute, and what the numbers on screen mean. It is also available in [Spanish](Guia_Demos_ES.md), with the same section numbers.

The section numbers match the demos. Section 1 is demo 1, section 2 is demo 2, and so on; section 5 is the gate. Inside demos 1, 3 and 4, subsection *N* matches the section the script prints as *N*: §1.4 is what `run_demo.py` prints under "4. Unconstrained tree", §4.2 is what `run_supply_chain_demo.py` prints under "2. A swapped model". The comments in the code point back here by those numbers, as `Demo guide §1.4`.

All numbers quoted come from the seeded runs versioned in `demo/output/`. Everything is synthetic; there are no real patients anywhere in the repository.

---

## Contents

0. [Before the demos: running them, the layout, the shared code](#0-before-the-demos-running-them-the-layout-the-shared-code)
1. [Demo 1: GRAIMATTER's checks, written by hand](#1-demo-1-graimatters-checks-written-by-hand)
2. [Demo 2: the same checks with SACRO-ML](#2-demo-2-the-same-checks-with-sacro-ml)
3. [Demo 3: evasion, extraction and a backdoor](#3-demo-3-evasion-extraction-and-a-backdoor)
4. [Demo 4: a tampered supply chain](#4-demo-4-a-tampered-supply-chain)
5. [The release gate](#5-the-release-gate)
6. [Demo 6: hiding data in a model](#6-demo-6-hiding-data-in-a-model)
7. [Reproducibility and known caveats](#7-reproducibility-and-known-caveats)

---

## 0. Before the demos: running them, the layout, the shared code

### 0.1 Running the demos

From the repository root, after `uv sync` (or `uv sync --extra sacroml` for demo 2):

```bash
uv run python demo/run_demo.py               # demo 1, seconds
uv run python demo/run_sacroml_demo.py       # demo 2, a few minutes, needs sacroml
uv run python demo/run_aml_demo.py           # demo 3, seconds
uv run python demo/run_supply_chain_demo.py  # demo 4, seconds
uv run python demo/run_stego_demo.py         # demo 6, seconds
uv run python demo/run_gate.py               # reruns demos 1, 3, 4 and judges them
```

Each script prints its report to the terminal and saves the same text under `demo/output/`. The order in a workshop is usually 3, 4, 1, 2, then the gate, because the deck explains the general attacks first and GRAIMATTER second; the numbering follows the order the demos were written (demo 5 is the gate, demo 6 was added last). Demo 6 is standalone and the gate does not read it.

| Script | Report | Other outputs |
| --- | --- | --- |
| `run_demo.py` (demo 1) | `demo/output/demo_report.txt` | `data_dictionary.json`, `safe_tree.release.json`, `tampered_tree.release.json`, `data_use_register.json`, `pipeline_snapshot.json`, `not_a_model.txt`; model files (`*.joblib`, not versioned) |
| `run_sacroml_demo.py` (demo 2) | `demo/output/sacroml/sacroml_report.txt` | `sacroml/<model>/<attack>/report.json` (and `report.pdf`, not versioned), `sacroml/safe_release/target.yaml` |
| `run_aml_demo.py` (demo 3) | `demo/output/aml_report.txt` | none |
| `run_supply_chain_demo.py` (demo 4) | `demo/output/supply_chain_report.txt` | working files in `demo/output/supply_chain/` (not versioned) |
| `run_stego_demo.py` (demo 6) | `demo/output/stego_report.txt` | none |
| `run_gate.py` | `demo/output/gate/gate_<packs>.json` and `.md` | exit code 0 or 1 |

### 0.2 Where the code lives

```
demo/
  run_demo.py               demo 1 script
  run_sacroml_demo.py       demo 2 script
  run_aml_demo.py           demo 3 script
  run_supply_chain_demo.py  demo 4 script
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
    controls.py             regulation -> control -> demo                     §5.2
    tolerances.py           metrics, tolerances, readers                      §5.3
    gate.py                 verdicts and reports                              §5.4
```

### 0.3 The synthetic cohort (`graimatter_demo/cohort.py`)

All five demos draw their data from `sample_cohort(n, rng, n_noise)`. Each row is a fictional person:

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
* **The noise columns carry no signal.** Demo 1 and demo 6 use ten of them (`n_noise=10`) so that a deep tree has something to memorise individual rows with, or a neural network has more weights to carry. Demos 3 and 4 use two (`n_noise=2`) and call them lab values: the backdoor trigger is planted in them.

`hold_out_for_tre(n_rows, rng, 0.5)` shuffles the row numbers and returns two index arrays: the researcher's half and the TRE's half (GRAIMATTER TECH 6). The holdout is never passed to `fit()`. `data_dictionary()` writes the description of the columns that TECH 8 and Appendix C ask for (`demo/output/data_dictionary.json`).

### 0.4 The common pattern of the scripts

The five scripts are built the same way, so reading one helps with the others:

* **The `sys.path` lines** at the top insert `demo/` into the import path, so `python demo/run_demo.py` works from the repository root without installing anything.
* **`SEED = 7`.** Every random draw comes from `np.random.default_rng(SEED)` or a generator derived from it (`SEED + 1`, `SEED + n_queries`). The same seed gives the same report, which is what the tests check (§5.6). The order of the draws matters: adding a draw early in a script changes every number after it.
* **The `Report` class** prints each line and keeps it, then `save()` writes the same lines to the report file. What you see on screen is what is in the file.
* **`_section()`** prints the `=====` banners and the numbered titles. Those numbers are the subsection numbers of this guide.
* **`main()` returns a dictionary** with the numbers it printed. The gate (§5) calls `main()` and reads that dictionary for demos 1, 3 and 4; it never recomputes an attack. Each `return` is marked with the comment "The numbers above, for demo/run_gate.py". Demo 6 returns its numbers too, but it is standalone and the gate does not read them.

### 0.5 The attack metrics (`graimatter_demo/metrics.py`)

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

**Code.** `sample_cohort(1000, rng, n_noise=10)` draws 1,000 rows; `hold_out_for_tre(1000, rng, 0.5)` splits them into `researcher_x/researcher_y` (500 rows) and `holdout_x/holdout_y` (500 rows). `data_dictionary()` is written to `data_dictionary.json`.

**What you see.**

```
Synthetic rows: 1000. Researcher receives 500. TRE keeps 500 aside and does not put them in the training set.
```

**How to read it.** Every later accuracy "on the set-aside" and every membership attack uses those 500 rows as the non-members. Because the researcher never had them, the TRE can measure overfitting and membership leakage honestly.

### 1.2 Attribute inference on one planted record (Appendix E)

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

**Code.** The script writes two JSON files. `data_use_register.json` records the project, the decision (`approved_for_demo_release` if both the wrapper and `decide()` passed the candidate), the controls run and the refused files. `pipeline_snapshot.json` (TECH 3) records the seed, the row ids given to the researcher and kept aside, the wrapper's parameters and the policy used.

**How to read it.** These are the audit trail: with the snapshot, anyone can rerun the same split and check the same numbers.

### 1.10 Side by side

**What you see.**

```
model                    train  holdout  MIA AUC    adv.   TPR@10     ARR  decision
unconstrained tree       1.000    0.590    0.708   0.412    0.156   1.000  refuse
safe wrapper tree        0.692    0.584    0.528   0.004    0.116   1.000  release
1-nearest neighbour                                                        refuse (stores rows)
RBF SVC                                                                    refuse (support vectors)
tampered tree                                                              refuse (edited after fit)
```

**How to read it.** One model is released, four files are refused, each for a different reason. `main()` returns these results (the candidate, the refusals, the tamper recommendation and the query log) for the gate (§5.3).

---

## 2. Demo 2: the same checks with SACRO-ML

`demo/run_sacroml_demo.py` takes the same cohort and the same split (same seed, same calls to `sample_cohort` and `hold_out_for_tre`) and runs them through `sacroml` 2.0.1, the maintained toolkit from the AI-SDC project that grew out of GRAIMATTER. It needs `uv sync --extra sacroml`, which brings PyTorch, so CI does not run it.

### 2.1 The safe wrapper before fitting

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

`demo/run_aml_demo.py` adds the branches of NIST AI 100-2 that GRAIMATTER does not cover. The attacks live in `aml_demo/`.

### 3.0 The target model

**Code.** `sample_cohort(4000, rng, n_noise=2)`: 4,000 rows, the six clinical columns plus two lab-style noise columns (indices 6 and 7). The first 2,000 rows train the target, the other 2,000 test it. `forest()` returns the model used throughout: `RandomForestClassifier(n_estimators=200, min_samples_leaf=10)`.

**What you see.** `Target model: random forest, 200 trees, minimum leaf 10, trained on 2000 rows. Accuracy on the other 2000: 0.635.` That is about as good as the noisy label allows (§0.3).

### 3.1 Evasion: misreporting a form

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

**Code.** `aml_demo/extraction.py`. `invented_rows(n, rng, n_lab)` makes up rows inside the published value ranges (the data dictionary is public); no real record is used. `steal(api_labels, n_queries, rng, n_lab, make_copy)` sends them to the target's `predict`, then trains a new forest on the invented rows and the target's answers. `fidelity()` is the share of real test rows on which the copy and the target give the same label. For each budget (50, 200, 1,000, 5,000 queries) the script also plans evasion edits on the **copy** with `cheapest_evasion(copy.predict, flagged)` and measures with `transfer_rate()` how many of those edits fool the **target**. Finally it puts the target behind demo 1's `QueryGate` with a 200-row budget and asks for 1,000 rows.

**What you see.**

```
     50 queries: copy agrees with the target on  77.7% of real rows, accuracy 0.610; edits planned on the copy get  22.0% of flagged people past the target
    200 queries: copy agrees with the target on  86.9% of real rows, accuracy 0.623; edits planned on the copy get  54.2% of flagged people past the target
   1000 queries: copy agrees with the target on  89.5% of real rows, accuracy 0.629; ...  58.3% ...
   5000 queries: copy agrees with the target on  93.5% of real rows, accuracy 0.630; ...  64.4% ...
  Query gate with a 200-row budget (demo 1's QueryGate): Query refused: request has 1000 rows, 0 already used, budget is 200.
```

**How to read it.** With 200 invented questions, the attacker has a copy that agrees with the target 87% of the time and is almost as accurate. On the copy they can try edits offline, without the target ever seeing them, and over half of the edits planned that way work on the real model. The gate refuses the 1,000-row request, but 200 rows were already enough, and several accounts would multiply the budget. A budget slows extraction; it does not prevent it (NIST AI 100-2 §2.4.5 says the same).

### 3.3 Backdoor: a contributor poisons the training data

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

* **The baseline matters.** On the clean model the triggers already flip about 30% of high-risk scores, because the forest gives the noise columns a little weight and the trigger values are unusual. The attack is the rise above that baseline: from 32.3% to 100% with 2% quiet poison. The gate measures exactly that rise (§5.3).
* **Accuracy barely moves** (at most 0.02), so a holdout check, GRAIMATTER's TECH 6 included, does not see the backdoor. The model behaves normally until someone uses the trigger.
* **The outlier screen** catches most of a loud trigger at low volume and little of a quiet one. With more poison rows, the poison forms its own cluster and looks normal to the screen (loud: 80% caught at 2%, 42% at 5%).

### 3.4 Where each attack sits

The final table maps each attack to NIST AI 100-2, OWASP ML Top 10, MITRE ATLAS and EU AI Act Art. 15(5); the technical guide (§8.6) has the full crosswalk. `main()` returns the evasion rates, the extraction results per budget, whether the gate let the over-budget request through, and the backdoor results, for the gate.

---

## 4. Demo 4: a tampered supply chain

`demo/run_supply_chain_demo.py` attacks the route a model takes to its user rather than the model itself (NISTAML.051). A supplier publishes three files; the user downloads them from a mirror; whoever runs the mirror changes them. The script keeps its working files in `demo/output/supply_chain/supplier/` and `.../mirror/`, which it deletes and recreates on every run (not versioned).

### 4.1 The supplier's release, and the pin

**Code.** The cohort and the forest are the same as demo 3's (§3.0). The supplier writes:

* `model.pkl`: the forest, pickled.
* `bundle.json`: the published accuracy (0.635) and an encryption setting, `{"cipher": "AES-GCM", "key_bits": 256}`. It is only a number in a file: nothing in the demo encrypts anything.
* `constraints.json`: a copy of demo 1's safe-wrapper rules.

`write_lock()` in `supply_chain/integrity.py` computes the SHA-256 of each file (`sha256_file()`, read in 64 KB blocks) and writes `supply_chain.lock.json`. The pins come from the supplier's own release notes, not from the mirror; that is the point of a pin. `ACCEPTANCE_MARGIN = 0.02` is the tolerance of the usual acceptance test.

**What you see.** The three files and the first 12 hex characters of each pin.

Every later file is checked with `_user_checks()`: `verify()` against the pin, then, for a `.pkl`, the import scan (§4.3), and for a JSON file, the floors (§4.4).

### 4.2 A swapped model: the mirror serves a backdoored forest

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

**Code.** `supply_chain/payload.py` defines `Trojan`, whose `__reduce__` tells pickle "to rebuild me, call `run_then_return(message, model)`". Unpickling therefore calls that function, which appends a line to `payload.LOG` and returns the genuine forest. The mirror pickles a `Trojan` around the supplier's model. `supply_chain/pickle_scan.py` reads the file without loading it: `imports()` walks the pickle opcodes with `pickletools.genops`, following the `GLOBAL`, `STACK_GLOBAL` and memo opcodes to list every `module.name` the file would import, and `scan()` reports those outside the allow list (`sklearn.*`, `numpy.*` and three standard helpers). The script then loads the file anyway to show what would have happened.

**What you see.**

```
  Import scan, without loading: imports supply_chain.payload.run_then_return (refuses)
  Pinned digest: sha256:d7083b5feaef against sha256:fac97797542c: digest does not match the pin
  Had the user loaded it anyway: accuracy 0.635, and the payload log reads ['code in model.pkl ran while the file was loading'].
```

**How to read it.** The loaded model predicts exactly like the original (accuracy 0.635), so any test run after loading passes, and by then the code has already run. Here it writes one line; in the incidents ATLAS records (AML.CS0031) it opened a reverse shell. The scan and the pin both catch it. Formats that cannot hold code (safetensors) remove the problem instead of scanning for it.

### 4.4 A downgrade: one number in a configuration file

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

**What you see.**

```
  Tampered file                    Usual check          Usual     Pin      Scan or floor
  Swapped model with a backdoor    holdout accuracy     passes    refuses  passes
  Code hidden in the pickle        holdout accuracy     passes    refuses  refuses
  Key length 256 -> 40 bits        functional test      passes    refuses  refuses
  Safe-wrapper floor 20 -> 1       request_release()    passes    refuses  refuses
4 of 4 tampered files pass the usual check; 0 of 4 pass the pin and the scan or floor.
```

**How to read it.** The pin refuses all four. The content checks refuse three; the backdoor needs the pin. "0 of 4" is the number the gate reads (§5.3).

### 4.6 What the pin does not catch

**Code.** The script writes a second lock file from the mirror's own (backdoored) model and verifies against it.

**What you see.** `the backdoored forest verifies: digest matches the pin.`

**How to read it.** A digest proves a file is the one that was pinned, not that the pinned file is sound. If the pin is taken from the download, or the supplier's own build was compromised, the pin accepts the attack. What covers that gap: signatures that say who published a file (Sigstore, OpenSSF model signing), provenance that says how it was built (SLSA), an AI bill of materials, and testing supplied models as untrusted. `main()` returns the accuracies, the trigger success, the counts in §4.5 and this last result.

---

## 5. The release gate

`demo/run_gate.py` turns the crosswalk of the technical guide (§8.6) into a check that can block a release in CI. The pattern comes from [safety-trust-engine](https://github.com/olonok69/safety-trust-engine): controls mapped to evidence, numeric tolerances, a verdict per control, and a report.

### 5.1 What `run_gate.py` does, step by step

1. **Parse the options.** `--demos` (default `1,2,3,4`), `--regimes` (default `eu_uk,nist_aml,graimatter`), `--fail-under metric=value` (override a tolerance), `--accept-missing` (demos declared out of scope), `--out`, `--show-demos`. `_demo_names()` and `_limits()` validate them.
2. **Run the demos.** `run_demos()` imports each script as a module (`SCRIPTS` maps `demo1` to `run_demo` and so on) and calls its `main()`, with the demo's printing silenced unless `--show-demos`. If `sacroml` is not installed, demo 2 is skipped with a message instead of failing. The result is `evidence`: demo name → the dictionary its `main()` returned.
3. **Judge.** `build_report()` in `compliance_gate/gate.py` (§5.4).
4. **Write and exit.** The report is written as `gate_<packs>.json` and `.md`; the script prints one line per category, the control counts, and `Gate: PASS` or `FAIL`, and returns exit code 0 or 1.

### 5.2 Controls and regime packs (`compliance_gate/controls.py`)

A `Control` is one obligation the demos can evidence:

* `regulation`, `ref`, `label`: what it is, e.g. EU AI Act, Art. 15(5) model evasion.
* `stages`: the demos that must run for it to be evidenced.
* `categories`: the categories whose breach fails it.
* `binding`: `statute` (law), `guidance` (voluntary), `supervisory` (examiner expectation) or `recommendation` (the green paper), so the report never implies more than it can.

Controls are grouped in four packs: `eu_uk` (Art. 15(5) and the UK Code / ETSI EN 304 223), `nist_aml` (NIST AI 100-2 attack classes), `graimatter` (TECH 6, 7, 9-10, 11, 16, plus the SACRO-ML cross-check) and `us` (NIST AI RMF MEASURE and GOVERN, federal model risk management SR 26-02). `--regimes all` selects all four. The ten categories are listed in `CATEGORIES`.

### 5.3 Metrics, tolerances and readers (`compliance_gate/tolerances.py`)

`METRICS` defines one `MetricSpec` per number the gate judges: its category, the demo that produces it, its tolerance, a description, and two switches. `inclusive=True` breaches at `value >= limit` (demo 1's rule) instead of `value > limit`; `max_p` means the metric breaches only if its p-value is also at most that (FDIF). The privacy tolerances are read from demo 1's `POLICY`, so the gate and `decide()` cannot drift apart; the others are set here for the workshop (evasion 10%, copy agreement 80%, backdoor lift 10 points, zero for the counts).

The **readers** turn each demo's `main()` result into `Reading`s, without recomputing anything:

| Reader | Reads | Metrics |
| --- | --- | --- |
| `demo1_readings()` | the candidate (wrapped tree), the refusals, the tamper recommendation, the query log | membership AUC, advantage, TPR at 10% FPR, FDIF with p; attribute risk ratio; accuracy gap; stored rows; size ratio; disclosive files released (of 5); sweep rows allowed |
| `demo2_readings()` | the wrapped tree's AUCs, the two flags | mean SACRO-ML AUC; configurations not flagged (of 2) |
| `demo3_readings()` | evasion rates, extraction at the gate's budget (200), the over-budget request, the backdoor rows | three evasion rates; copy agreement; over-budget request allowed; backdoor lift = worst trigger success after poisoning minus the clean model's success for the same trigger |
| `demo4_readings()` | the count of tampered files accepted | supply-chain files accepted (of 4) |

`breaches(spec, reading, limit)` applies the rule. A missing value never breaches; it shows as "not measured".

### 5.4 Verdicts (`compliance_gate/gate.py`)

`build_report(evidence, regimes, overrides, accept_missing)`:

1. Merges the tolerances with any `--fail-under` overrides (an unknown metric name is an error).
2. Reads every demo that ran and builds a `MetricVerdict` per reading, grouped into a `CategoryVerdict` per category. A category is **within** tolerance when none of its metrics breaches.
3. Gives each selected control a `ControlVerdict`: **not_evidenced** if one of its demos did not run (marked `accepted` when all the missing demos were declared with `--accept-missing`); otherwise **fail** if any of its categories breached, else **pass**.
4. `GateReport.passed` is true only if every category is within tolerance and every control passes or is an accepted not_evidenced. There is never a silent green: a control without evidence fails the run unless the run says why.

`write_json()` and `write_markdown()` write the same content for machines and for people, with the disclaimer that the mapping and tolerances were made for this repository.

### 5.5 Reading the seeded report

`demo/output/gate/gate_eu_uk-nist_aml-graimatter.md` is the run on demos 1, 3 and 4 with demo 2 declared out of scope:

* **Tolerance gate.** Every privacy metric of demo 1 is within tolerance (they are the same numbers that let `decide()` release the wrapped tree in §1.5). Evasion (78.7%, 32.8%, 20.7% against 10%), extraction (86.9% against 80%) and poisoning (a lift of 71.7 points against 10) breach. Supply chain: 0 of 4 accepted, within.
* **Controls.** The GRAIMATTER pack passes, apart from the SACRO-ML cross-check, which is not evidenced (out of scope). Art. 15(5) fails on data poisoning, evasion and confidentiality (because of extraction), and passes on model poisoning thanks to demo 4. The NIST controls follow the same split.
* **The lesson.** The model that GRAIMATTER's privacy checks release is not resilient in the sense of Art. 15(5). Privacy is one branch of AML.

`gate_us.md` is the same evidence through the US pack.

### 5.6 The gate in CI, and the tests

`.github/workflows/gate.yml` runs two jobs. `lint-and-test` runs `ruff` and `pytest`. `gate` runs the gate twice: the GRAIMATTER pack on demo 1, which must pass, and all packs on demos 1, 3 and 4, which must exit with 1 and breach exactly evasion, extraction and poisoning. A gate that blocked for any other reason, or stopped blocking, would turn CI red.

`tests/test_gate.py` reruns demos 1, 3 and 4 and checks that their reports still match the versioned files in `demo/output/`, apart from the machine-dependent lines listed in §7 (`test_regenerated_outputs_match_versioned`), that the gate decides as demo 1's `decide()` does, and that the seeded verdicts are the ones in §5.5. That is why a change to a demo's numbers must come with its regenerated report.

---

## 6. Demo 6: hiding data in a model

`demo/run_stego_demo.py` asks the steganography question of a model: can you hide a message inside it? GRAIMATTER's output checks ask whether a model *leaks* its training data by accident (membership and attribute inference); they do not ask whether someone *wrote* data into it on purpose. This demo shows two channels for doing that, and what removes each. The code lives in `stego_demo/`. Nothing here hides executable code: the payload is a short note or a few fabricated records, standing for data carried out of a TRE.

### 6.0 The carrier model

**Code.** `sample_cohort(4000, rng, n_noise=10)`, first 2,000 rows to train, the other 2,000 to measure accuracy. `network()` returns the carrier, `MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=800)` — a neural network rather than a forest, because a neural network has a large array of float weights to hide bits in. `_flat_weights()` concatenates its `coefs_` into one float32 vector; `with_weights(model, flat)` returns a deep copy of the trained model with only those weights replaced, keeping the intercepts and everything else, so a changed-weights copy predicts exactly as the original minus the change.

**What you see.** `Carrier network trained on 2000 rows. Accuracy on the other 2000: 0.575. It has 10,304 weights.` The accuracy is about what the noisy label allows (§0.3); the weight count is what sets the channel's capacity.

### 6.1 In the weights: LSB steganography

**Code.** `stego_demo/weights.py`. A float32 holds a sign bit, 8 exponent bits and 23 mantissa bits. The lowest mantissa bits carry almost no magnitude: the k-th lowest is worth about 2^(k−24) of the number, so overwriting the bottom eight changes a weight by around one part in 32,000. `embed(weights, payload, bits_per_weight=8)` writes a 32-bit length header and the payload bytes into the low 8 bits of successive weights; `extract()` reads them back; `capacity_bytes()` is `n_weights * bits // 8` minus the header. `max_abs_shift()` reports the largest change any single weight took. The payload, `SECRET`, is a fabricated 111-byte note with made-up medical record numbers.

**What you see.**

```
Using the lowest 8 of each weight's 23 mantissa bits, the channel holds 10,300 bytes. The payload is 111 bytes.
  Largest change to any one weight: 3.01e-06. Accuracy after hiding: 0.575 (was 0.575).
  Payload read back from the weights: exact match (111 bytes).
```

**How to read it.** The 10,304-weight network holds about 10 KB in its low bits. Hiding 111 bytes moves no weight by more than 3e-06 and leaves test accuracy unchanged to three decimals. An accuracy-only release check — GRAIMATTER's TECH 6, and the gate in §5 — sees an ordinary model and passes it, while the data rides out of the TRE inside it. A larger network holds proportionally more: a few million weights hold a megabyte, which is how EvilModel (Wang et al. 2021) hid whole malware files in a convolutional network without changing its outputs.

### 6.2 In the behaviour: a watermark/backdoor channel

**Code.** `stego_demo/behaviour.py`. Here the message is not in the bytes but in what the model answers. `triggers_for(payload, n_features, rng)` turns the payload (with the same 32-bit header) into one trigger row per bit; `_trigger_keys()` draws those rows from a wide Gaussian (std 20) far outside the cohort's value ranges, so they sit apart from one another and from any real record. `plant(train_x, train_y, keys, bits, repeat=5)` appends each trigger, labelled with its bit, to the training set a few times over, so the handful of triggers carry enough weight for the model to memorise them while its accuracy on real rows holds. `read_back(predict, keys)` queries the triggers and reads the predicted labels back as the payload; `recovered_fraction()` is the share of bits returned correctly.

**What you see.**

```
  248 trigger rows carry a 27-byte message, one bit each, added to the training set (each repeated a few times) far outside the cohort's ranges.
  Accuracy on real rows: 0.632 (clean model 0.575). Planted bits returned correctly: 100.0%.
  Message read from the triggers: exact match.
```

**How to read it.** The message `owner=lab42; contact=hidden` goes in as 248 trigger rows (27 bytes plus the 4-byte header, eight bits each). The watermarked model answers real rows as well as the clean one — a touch better here, within the label's noise — and returns every planted bit, so the message comes back exactly. This is backdoor watermarking (Adi et al. 2018) used as a covert channel; the same mechanism is how a model can be made to memorise and later disgorge a secret on a chosen prompt (Song et al. 2017). Because the message lives in the decision function, editing the weight bytes does not remove it (§6.3).

### 6.3 Defences: what each one removes

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

The closing table maps each channel to its source and to NIST AI 100-2e2025: the weight channel to confidentiality and exfiltration (EvilModel, Wang et al. 2021), the watermark to backdoor and integrity (Adi et al. 2018), and memorisation to data leakage (Song et al. 2017). The point for GRAIMATTER is that an output check trusting accuracy alone cannot see either channel, so a TRE's safe-export step should transform every released model — clip the low bits or quantise, and prefer differentially private training — rather than rely on spotting the hidden data. This demo is standalone: unlike demos 1, 3 and 4 it is not wired into the release gate, because the gap it shows is closed by a release-time transform, not by a tolerance on a number.

---

## 7. Reproducibility and known caveats

* **Seeds.** Demos 1, 3 and 4 give the same report on every run with the same library versions. The tests rely on that. A different scikit-learn version can change a forest and therefore the numbers.
* **Demo 2 is not reproducible run to run.** The package's attacks draw their own random splits; the mean membership AUC of the wrapped tree moved from 0.494 to 0.487 between two runs. Its `report.json` files are appended to on every run, not replaced. Demo 2 is therefore outside CI and its gate control is declared out of scope there.
* **Lines that depend on the machine.** Demo 1's last line prints the absolute path of the machine that ran it (for example `Full write-up: D:\repos\...`). The pickled size of the unconstrained tree (§1.4) and the digests of pickled models (§4.1 to §4.3) change between scikit-learn versions, so your digests may differ from the ones quoted here; the verdicts do not. `_normalise()` in the tests masks those three things before comparing.
* **`n_jobs=-1`** in demos 3 and 4 uses every core; it changes speed, not results.
* **Scale.** The cohorts are hundreds or thousands of rows, the models are trees and forests, and the attacks are teaching sketches. The technical guide (§25) lists what the demos do not show.
