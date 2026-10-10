# GRAIMATTER: Technical Guide for the Workshop

**Disclosure control for trained models leaving a trusted research environment, with two demos on synthetic data**

This guide goes with the workshop deck (`docs/GRAIMATTER.pptx`) and the two demo scripts in this repository (`demo/run_demo.py` and `demo/run_sacroml_demo.py`). It is written for a data scientist who has not read the 99-page green paper. It covers the paper's technical recommendations and walks through both demos, section by section, with the numbers from the seeded runs. Appendix A maps every section to its slides.

> **How to read this guide.** Each section opens with a short **In plain words** box. The text after it goes into detail. Parts marked **Under the hood** describe exactly what the code does and can be skipped. Section 4 defines every metric once; the rest of the guide uses the short names. The paper is cited by section and page of `GRAIMATTER Green Paper.pdf`; demo numbers are cited from `demo/output/demo_report.txt` (demo 1) and `demo/output/sacroml/sacroml_report.txt` (demo 2).

---

## Contents

1. [What a TRE is protecting when the output is a model](#1-what-a-tre-is-protecting-when-the-output-is-a-model)
2. [A map of the green paper](#2-a-map-of-the-green-paper)
3. [The synthetic cohort and the holdout](#3-the-synthetic-cohort-and-the-holdout)
4. [The metrics, in words and in code](#4-the-metrics-in-words-and-in-code)
5. [Demo 1: the hand-written checks](#5-demo-1-the-hand-written-checks)
6. [Demo 2: the official SACRO-ML package](#6-demo-2-the-official-sacro-ml-package)
7. [The two demos side by side](#7-the-two-demos-side-by-side)
8. [How to reproduce](#8-how-to-reproduce)
9. [Limits of the demos](#9-limits-of-the-demos)
10. [Glossary](#10-glossary)
11. [References](#11-references)

[Appendix A: how the guide, slides and demos line up](#appendix-a-how-the-guide-slides-and-demos-line-up)

---

## 1. What a TRE is protecting when the output is a model

> **In plain words.** A trusted research environment (TRE) is a locked room for sensitive data: researchers work inside it and only checked results come out. For decades those results were tables and statistics, and staff know how to check them. Now researchers want to take out a trained machine-learning model. A model is a file full of numbers that nobody can read by eye, and some models carry pieces of the training data inside them. The green paper explains how a TRE can decide whether such a file is safe to release.

![What leaves the TRE is a model, not a table](img/en/fig00_overview.svg)

### 1.1 TREs and the new kind of output

TREs (also called safe havens or data enclaves) give researchers access to pseudonymised, linked data inside a secure environment. They follow the "Five Safes" model and check every output before it leaves. For a table the rules are well known: for example, no cell should describe fewer than *k* people (paper §10.1, p. 35).

A trained model breaks those habits in three ways (paper §9.1, pp. 22-23 and §10.1, p. 35):

* **It is not human-readable.** Even a "simple" model has too many parameters to inspect. Checking one decision tree for leaves with a single person is possible but tedious; checking a forest of trees, where the intersection of leaves can single someone out, is not practical by hand.
* **Some models store rows.** A nearest-neighbour model needs every training row to make a prediction. A support-vector classifier keeps the training rows closest to its decision boundary (the support vectors). Those rows can be read straight out of the file (paper §10.1.5, pp. 39-40).
* **A file can be edited.** A model is a large array of numbers, so someone could hide data inside it, much as text can be hidden inside an image (paper §10.1, p. 35).

![Three ways a model file can carry people](img/en/fig01_leaks.svg)

The file size does not warn you. In demo 1 the deep decision tree is 18,150 bytes against a 68,000-byte training table (ratio 0.267), and its smallest leaf still describes one person (`demo_report.txt`, section 4).

### 1.2 Who the paper worries about

The executive summary names three risk types (paper §9.1, p. 23). The demos refer to them by these labels:

| Risk type | Who | Example in the demos |
|---|---|---|
| **RT1** | A well-meaning researcher who does not know the threats and saves too much in the model file. | Training a tree with no leaf-size limit; changing a parameter after fitting and forgetting to retrain. |
| **RT2** | A malicious researcher who deliberately hides data inside the file. | Adding a `hidden_rows` attribute to the model after `fit()`. |
| **RT3** | An outside attacker who gets the released model. | All the attacks in sections 5 and 6. |

### 1.3 The attacks

The paper uses three families of attack (paper §9.1, p. 23 and §10.1.1, p. 36):

* **Membership inference.** Was this person's row in the training set? If the training set is "patients with cancer", membership alone is sensitive.
* **Attribute inference.** Given part of someone's record, can the model fill in a hidden field, such as weight or blood pressure?
* **Model inversion.** Can the attacker reconstruct whole records likely to be in the training set? The demos do not cover this one.

Appendix E of the paper tells these stories for a non-technical reader: a famous politician whose weight and blood pressure are recovered from a cancer-risk model (attribute inference), the same person's membership in a cancer study (membership inference), a recruitment agency that screens out former study participants, and a hospital SVM found to contain 441 exact patient rows out of 798 (pp. 86-92).

---

## 2. A map of the green paper

> **In plain words.** The paper makes five sets of recommendations. The technical set (TECH 1 to 17) says what to check and how; the demos illustrate it. The other four sets cover law and ethics, cost, training and public involvement. This section summarises them so you know where to look; the clause text is in the PDF.

The paper's full title is *Green Paper: Recommendations for disclosure control of trained Machine Learning (ML) models from Trusted Research Environments (TREs)*. It is an output of the DARE UK sprint project GRAIMatter, published in September 2022 (paper §2, p. 7).

### 2.1 Technical recommendations (TECH 1 to 17)

TECH 4 splits controls into two families (paper §10.2.4, p. 42):

* **Model disclosure controls (MDCs)** act on the model file before it leaves: a holdout set, attack simulations, file checks, safe wrappers, and extra controls for models that memorise.
* **Model query controls (MQCs)** act after release: the model stays on a server and the TRE limits how it can be queried.

The table lists every technical recommendation, with where the demos show it. The wording is a short paraphrase.

| ID | What it asks for, in brief | Where the demos show it |
|---|---|---|
| TECH 1 | Discuss disclosure risk when the project is applied for (p. 41). | Not demonstrated. |
| TECH 2 | Provide ML tools inside the TRE (p. 41). | Not demonstrated. |
| TECH 3 | Snapshot the pipeline that produced an approved model, for audit (p. 42). | `demo/output/pipeline_snapshot.json` (demo 1, section 9). |
| TECH 4 | Two families of control: MDCs and MQCs (p. 42). | The structure of both demos. |
| TECH 5 | MDC work needs staff trained in ML (p. 43). | Not demonstrated. |
| TECH 6 | Keep part of the data aside; the research team never trains on it (p. 43). | 500 of 1,000 rows withheld (section 3). |
| TECH 7 | Run a range of checks before release: holdout accuracy, attacks, file size and type (p. 43). | `disclosure.decide()` in demo 1; structural, worst-case and attribute attacks in demo 2. |
| TECH 8 | Researchers supply a data dictionary of model inputs (p. 46). | `demo/output/data_dictionary.json`; Appendix C is the template. |
| TECH 9 | Researchers may use community safe wrappers (p. 46). | `SafeDecisionTreeClassifier` in both demos. |
| TECH 10 | Safe wrappers follow a set of principles: constraints file, hyperparameter correction, checks for post-fit changes, `request_release()` (p. 48). | `demo/constraints.json` and the wrapper in demo 1; the package's own wrapper in demo 2. |
| TECH 11 | Instance-based models, and models that memorise, need extra controls: aggregated data, differential privacy, or query limits (p. 49). | Nearest neighbours and a standard SVC are refused (demo 1, section 6). |
| TECH 12 | Make informed choices about differential privacy (p. 50). | Laplace noise on a mean and a best-of-50 cherry-pick (demo 1, section 3). |
| TECH 13 | Ensembles need special treatment (p. 50). | Not demonstrated. |
| TECH 14 | Test the final model of federated learning (p. 51). | Not demonstrated. |
| TECH 15 | Treat synthetic data as personal data (p. 52). | Not demonstrated. |
| TECH 16 | Limit queries on a released model (p. 52). | Row-counting query gate (demo 1, section 8). |
| TECH 17 | Have query limits tested by an external party (p. 53). | Named in demo 1; the demo implements only the gate. |

The appendices this guide uses are A (risk experiments, pp. 70-79), C (data dictionary template, p. 83), D (constraints file, p. 83), E (case studies, pp. 86-92), F (lay explanations of metrics, pp. 92-95) and G (steps for running attack simulations, p. 96).

> **Appendix A, experiment 2, in one sentence.** The team trained a wide range of hyperparameter settings on several tabular datasets and found many settings that looked safe on one dataset and were risky on another (§16.2, p. 76). A safe range from a previous dataset is therefore not, by itself, a release decision: run the attacks on the model in hand. This is why demo 1 still attacks the wrapped tree.

### 2.2 Ethics and legal (ELA 1 to 11)

The trained model may itself fall under data protection law, so sharing agreements may be needed (ELA 1). Approval processes should weigh the risks and controls of each application, contracts should cover query controls after release, and data use registers should list models and their controls (ELA 2 to 4). Researchers, TRE staff and committees should be trained (ELA 5). EULAs and researcher declarations get extra clauses (ELA 6 and 7). **ELA 8** says approval can take a risk-based approach, which is why the thresholds in demo 1 are a local policy, not the paper's. The data controller approves the TRE's disclosure-control process (ELA 11). See §11.2, pp. 54-63. The demos do not draft any clause text.

### 2.3 Costing (C 1 to 5)

Checking models and running attacks is extra work that TREs should charge for; tool development needs funding; query-limited hosting has its own cost; some highly technical work may be outsourced (§12.2, pp. 64-65).

### 2.4 Training (TR 1 to 4)

Courses and documentation for TRE staff, researchers, and data governance and ethics committees, on ML and on disclosure risk in trained models (§13.2, pp. 65-66).

### 2.5 Public involvement (P 1 and 2)

Public representatives should take part in data governance and ethics approval, and the use of data to train models, with the controls applied, should be visible through searchable data use registers (§14.2, p. 67).

---

## 3. The synthetic cohort and the holdout

> **In plain words.** Both demos use the same made-up group of 1,000 people. The researcher gets 500 of them to train on. The TRE keeps the other 500 locked away and uses them to test the model, which is TECH 6. Nobody in the data is real.

![The holdout the researcher never sees](img/en/fig02_holdout.svg)

The cohort is generated by `demo/graimatter_demo/cohort.py` with seed 7.

* **Clinical columns (6):** age (30 to 89), diabetes, asthma, weight (underweight, normal, overweight, obese), blood pressure (low, slightly high, high, very high, extremely high), smoker.
* **Noise columns (10):** `noise_0` to `noise_9`, standard normal, with no link to the label. They exist so that an unconstrained tree has something to memorise.
* **Label:** `high_risk`, drawn from a known logistic function of the clinical columns.

**Under the hood.** The log-odds of `high_risk` are `-1.35 + 0.034·(age − 55) + 0.9·smoker + 0.55·diabetes + 0.22·asthma + 0.32·[weight ≥ overweight] + 0.30·[blood pressure ≥ high]`. `hold_out_for_tre()` shuffles the 1,000 row indices and gives the first 500 to the TRE and the rest to the researcher.

The data dictionary that TECH 8 asks for is written to `demo/output/data_dictionary.json`. It lists each input with its encoding (`int`, `binary`, `ordinal:` with the level names, or `float64` for noise), the split sizes and the seed, following the template in Appendix C (p. 83).

---

## 4. The metrics, in words and in code

> **In plain words.** An attack gives every row a score: how likely the attacker thinks it is that the row was in training. The metrics answer three questions. On average, does the score separate members from non-members (AUC)? Are there rows where the attack is very sure and right (TPR at low FPR, FDIF)? And if the attacker says "member", how likely is that to be true, given how rare members are (the posterior)?

![Three ideas behind the attack metrics](img/en/fig04_metrics.svg)

Each metric below is defined once, with the formula the repository uses (`demo/graimatter_demo/metrics.py`) and the paper's explanation (Appendix F, pp. 92-95).

**Training accuracy and set-aside accuracy.** Training accuracy is the share of correct predictions on the rows the model was trained on. Set-aside accuracy is the same on the 500 rows the researcher never received. A large gap means the model has fitted this particular sample, noise included. Demo 1's policy flags a gap above 0.15.

**Membership inference.** The attack labels each row "member" (in training) or "non-member". The worst-case version of Appendix G gives the attacker both the training rows and the held-out rows, so it is a conservative upper bound rather than a realistic attacker (p. 96).

**TPR and FPR.** The true-positive rate is the share of real members the attack calls members. The false-positive rate is the share of non-members it wrongly calls members. The demo uses a score threshold of 0.5.

**AUC.** Pick one member and one non-member at random. AUC is the probability that the attack scores the member higher. 0.5 is a coin toss; 1 means the attack always ranks members first. The paper notes that there is no single "bad" AUC value and suggests comparing with the range expected by chance (Appendix F §21.4, p. 94). For 100 members and 100 non-members, three standard deviations around 0.5 is roughly 0.38 to 0.62. The `sacroml` report prints the same band as `0.3772 -> 0.6228`.

**Advantage.** `advantage = |TPR − FPR|`. Zero means the attack calls members and non-members "member" at the same rate.

**TPR at 10% FPR.** Walk down the rows from the highest score. Stop just before the false alarms exceed 10% of the non-members. The share of members caught so far is the TPR at 10% FPR. A model can have a modest AUC and still give away a group of members in this tail.

**FDIF (frequency difference).** Sort the rows by score. FDIF is the share of members in the top 10% minus the share of members in the bottom 10%. Random scores give an FDIF near 0; an attack that is certain about some members and some non-members pushes it towards 1. The demo computes a permutation p-value: shuffle the membership labels 300 times and count how often the shuffled FDIF is at least as large. Appendix F explains why this matters: an attack that is certain about 20 of 200 rows (10 members scored 1, 10 non-members scored 0) and random elsewhere has an average AUC of about 0.595, inside the chance band, yet it exposes those people (§21.5, pp. 94-95). Demo 1 treats FDIF ≥ 0.20 with p ≤ 0.05 as a failure.

**Membership posterior.** If the attacker says "this row was in training", how likely is that to be true? It depends on *A*, the share of members among the rows the attacker is testing:

```
P(member | flagged) = (A × TPR) / (A × TPR + (1 − A) × FPR)
```

The demo reports it at A = 0.5 (half the candidates are members) and A = 0.01 (one in a hundred). For the unconstrained tree (TPR 1.000, FPR 0.588) that is 0.630 and 0.017 (`demo_report.txt`, section 4). The paper's own example shows the same effect: a good attack (TPR 0.8, FPR 0.2) gives only 0.04 when members are 1 in 100 (Appendix F, Table 9, p. 93).

**Attribute inference.** For a row, try every possible value of one hidden field and ask the model for its confidence in the row's label. If a single value gives the highest confidence, that value is the attack's guess; if several values tie, the attack abstains. Appendix G asks for two numbers: the share of rows that get a unique guess, and how many of those guesses are correct, each on the training rows and on the held-out rows (p. 96). Demo 1 summarises the comparison as an **attribute risk ratio**: the correct-guess rate on training rows divided by the rate on set-aside rows. Above 1 means training rows are easier to complete. Demo 1's policy flags 1.35.

**k-anonymity of a leaf.** The number of training rows in the smallest leaf of a tree. A leaf of 1 is one person.

**Under the hood.** `summarise_attack_scores()` in `metrics.py` returns all of the above for one set of attack scores. `true_positive_rate_at_false_positive_rate()` walks the ranked scores; `frequency_difference()` uses a 10% tail and 300 permutations; `membership_probability()` is the posterior formula.

---

## 5. Demo 1: the hand-written checks

> **In plain words.** The first script is a small, readable implementation of the paper's checks. It trains several models on the synthetic cohort, attacks them, and says yes or no to each one using a demo policy. It refuses a deep tree that memorised people and releases a tamer tree built through a safe wrapper. It also refuses models that store rows, catches a model that was edited after training, and blocks a query that tries to sweep hidden fields.

Entry point: `demo/run_demo.py`. Report: `demo/output/demo_report.txt`. Policy: `demo/graimatter_demo/disclosure.py`. Constraints: `demo/constraints.json`. The walkthrough follows the report's sections 1 to 10.

### 5.0 The demo policy

The paper does not publish universal cut-offs; ELA 8 leaves the risk appetite to an agreement with the data controller. So that the script can say yes or no, `disclosure.py` sets a local policy. **These numbers are the demo's, not the paper's.**

| Rule | Limit |
|---|---|
| Worst-case membership AUC | 0.62 |
| Advantage | 0.20 |
| TPR at 10% FPR | 0.35 |
| FDIF, and its p-value | 0.20, with p ≤ 0.05 |
| Attribute risk ratio | 1.35 |
| Training minus set-aside accuracy | 0.15 |
| Model file size ÷ training table size | 0.75 |
| Accepted file types | `.joblib`, `.pkl` |

A model that stores training rows is refused even when every other rule passes.

### 5.1 The rows the researcher never sees (section 1)

The script generates the 1,000 rows, keeps 500 aside and writes the data dictionary (section 3 of this guide). *Illustrates TECH 6 and TECH 8, Appendix C.*

### 5.2 Attribute inference on one planted record (section 2)

![Twenty queries recover two hidden fields](img/en/fig03_attribute_sweep.svg)

`case_study.py` rebuilds the paper's first case study on synthetic data. It plants one person, aged 62, diabetic, asthmatic and a smoker, who is overweight with slightly high blood pressure. Around that person it places a block of rows that share the same public fields and cover every other weight × blood-pressure combination, with mixed labels. An unconstrained tree is trained on all of it.

The attacker knows the four public fields and tries all 4 × 5 = 20 combinations of the two hidden ones. The planted pair (overweight, slightly high) comes back with confidence 1.000; every other combination is at 0.500. The unique highest confidence is the hidden truth. In the paper's version the top answer was at 93.8% and the next at 57.7% (Appendix E §20.1, p. 87); the demo's planted block makes the gap even clearer. *Illustrates Appendix E.*

### 5.3 What epsilon means, on a mean (section 3)

![Differential privacy on a released mean](img/en/fig10_dp.svg)

Differential privacy is a property of the mechanism that turns private data into a release, not of the data itself (paper §10.1.3, pp. 37-39). The paper's thought experiment: the attacker knows everything except whether one particular person was included, and sees the release. A deterministic release, such as a plain mean, gives the answer away: the attacker computes the mean both ways and sees which one matches. A differentially private mechanism adds randomness so that the two cases look alike, to a degree set by epsilon (smaller is more private).

The demo applies this to the mean age of the 500 training rows. The attacker knows every age and must guess whether row 0 was included. Accuracy is how often the guess is right over 400 trials.

| Release | Attacker accuracy | Laplace scale |
|---|---|---|
| Deterministic mean | 1.000 | 0 |
| epsilon 8.0 | 0.703 | 0.015 |
| epsilon 1.0 | 0.522 | 0.120 |
| epsilon 0.2 | 0.487 | 0.600 |

TECH 12 adds a practical warning. At epsilon 0.2 one noisy mean misses the true mean by 0.3053. If someone draws 50 noisy means and keeps the one closest to the true answer, the miss is 0.0084. Picking the draw that looks most like the non-private answer cancels the protection, so TRE staff, not the researcher, should choose the random seed, without looking at the result. *Illustrates §10.1.3 and TECH 12.*

**Under the hood.** `dp_sketch.py` uses sensitivity `(90 − 30) / 500 = 0.12` (the age range divided by the number of rows) and Laplace scale `sensitivity / epsilon`. The attacker guesses "included" when the release is closer to the mean with the row than to the mean without it. This repository does not train a differentially private model.

### 5.4 Unconstrained tree (section 4)

A `DecisionTreeClassifier` with no depth limit and `min_samples_leaf = 1` is trained on the 500 researcher rows.

| | Seeded result |
|---|---|
| Training accuracy | 1.000 |
| Set-aside accuracy | 0.590 |
| Gap | 0.410 (limit 0.15) |
| Smallest leaf | 1 training row |
| File size | 18,150 bytes vs training table 68,000 bytes (ratio 0.267; size alone does not fail) |
| Worst-case membership AUC | 0.708 (limit 0.62) |
| Advantage | 0.412 (limit 0.20) |
| TPR / FPR | 1.000 / 0.588 |
| TPR at 10% FPR | 0.156 (does not trip the 0.35 limit) |
| FDIF | 0.620, p = 0.003 |
| Posterior if flagged | 0.630 when half of candidates are members; 0.017 when 1 in 100 are |
| Salem-synth | AUC 0.703; TPR at 10% FPR 0.514; FDIF 1.000 |
| Weight attribute inference | Abstained. Ratio 1.000. |

**Decision: do not release.** Four rules fire: the accuracy gap, the AUC, the advantage and FDIF.

Two details are worth pointing out. First, the file-size check and the TPR at 10% FPR both pass: on their own they would have let this model through, which is why TECH 7 asks for a range of checks. Second, the attribute attack on weight abstains. This tree separates rows using the noise columns, so changing a person's weight does not move them to another leaf and every weight value gives the same confidence. Section 5.2 is the case where the model does split on the hidden fields.

**Under the hood.** The worst-case attack (`attacks.worst_case_membership`) builds one row per record with the model's predicted probabilities **plus the true label**, labels it member or non-member, splits that set in half, trains a random forest on one half and scores the other. Salem-synth (`attacks.salem_synth_membership`) draws a fresh cohort from the same generator, trains a shadow tree with the same hyperparameters, trains the attack on the shadow model's outputs and then scores the real model: the attacker has similar data, not the TRE's tables (Appendix A, Table 2, p. 71).

### 5.5 The same data through a safe wrapper (section 5)

![Unconstrained tree versus safe wrapper](img/en/fig06_trees.svg)

The researcher asks for the same unconstrained settings, but through `SafeDecisionTreeClassifier`. The wrapper reads `demo/constraints.json` and corrects them: `min_samples_leaf` from 1 to 20 and `max_depth` from unlimited to 4. Appendix D of the paper shows the constraints-file format with an example minimum leaf size of 5 (p. 83); the demo is stricter so that the contrast shows on a few hundred rows.

| | Seeded result |
|---|---|
| Training accuracy | 0.692 |
| Set-aside accuracy | 0.584 |
| Smallest leaf | 20 training rows |
| Worst-case membership AUC | 0.528 |
| Advantage | 0.004 |
| TPR at 10% FPR | 0.116 |
| FDIF | 0.020, p = 0.445 |
| Posterior if flagged | 0.502 at half members; 0.010 at 1 in 100 |
| Weight attribute inference | Abstained. Ratio 1.000. |

`request_release()` returns "Run file through the next step of the checking procedure": the wrapper only gets the file into the TRE's queue. The attack numbers then drive the decision. No demo rule fires. **Decision: allow release under the demo policy.** The set-aside accuracy barely changed (0.590 to 0.584), which tells you that the deep tree's extra training accuracy was memorisation, not skill.

#### The quiet failure (Appendix F)

![AUC near chance, tail not](img/en/fig07_tail.svg)

Salem-synth on the same wrapped tree gives AUC 0.512, close to chance, but FDIF 0.280 with p = 0.003 and TPR at 10% FPR 0.252. Members pile up in the extreme scores. This is the Appendix F warning in practice: the average says "chance", the tail does not. Demo 1's export rule follows the worst-case attack of Appendix G, whose FDIF is 0.020, so it still releases. A data controller who cares about the tail could refuse. *Illustrates TECH 9, TECH 10, TECH 7, Appendix F and Appendix A experiment 2.*

### 5.6 Instance-based models are refused (section 6)

* A 1-nearest-neighbour model stores all 500 training rows. The file is 68,677 bytes, 1.010 times the training table.
* An RBF support-vector classifier stores 423 support vectors out of 500 rows. File ratio 0.94.
* The safe wrappers for both classes refuse to fit: `constraints.json` marks `KNeighborsClassifier` and `SVC` as not permitted.

**Decision: do not release** either model. The reasons are that the model stores training rows and that the file is bigger than 0.75 of the table. The paper's alternatives are training on aggregated data, using a differentially private algorithm, or keeping the model inside a query-limited service (TECH 11, p. 49; §10.1.5, pp. 39-40). This repository does not implement a private SVM. *Illustrates TECH 11.*

### 5.7 Editing the model after `fit()` (section 7)

![The safe wrapper, from constraints file to register](img/en/fig08_wrapper.svg)

This time the researcher sets `override=True`. The wrapper accepts `min_samples_leaf = 1` and unlimited depth but reports both breaches. After fitting, the researcher edits the parameters back to the allowed values (`max_depth` 4, `min_samples_leaf` 20) and adds an attribute called `hidden_rows`. `request_release()` compares the current state with the snapshot taken at `fit()` and returns "Do not allow release", listing:

* `max_depth` changed from `None` to 4 after the model was fitted;
* `min_samples_leaf` changed from 1 to 20 after the model was fitted;
* the smallest leaf holds 1 training row, while the constraints require 20;
* attributes were added after `fit()`: `hidden_rows`.

The first two catch the careless case (RT1: changing a parameter without retraining). The last catches a deliberate attempt to hide data (RT2). The paper describes this check in §10.1.2 (p. 37). Finally, a file called `not_a_model.txt` is refused because its type is not `.joblib` or `.pkl`. *Illustrates TECH 10 and the RT1/RT2 risk types.*

**Under the hood.** At `fit()`, the wrapper stores the parameters, a SHA-256 digest of the tree arrays, the leaf k-anonymity and the list of attribute names. `request_release()` re-checks the constraints, compares parameters and digest, recomputes the smallest leaf and looks for new attributes. It writes `<model>.release.json` next to the model file.

### 5.8 A query budget that counts rows (section 8)

![A query budget that counts rows](img/en/fig09_query_budget.svg)

If the model is not released as a file but kept on a server, the TRE can limit queries (paper §10.1.7, pp. 40-41). `query_gate.py` gives each user a budget of 8 rows. A single patient lookup (1 row) is allowed; the predicted class probabilities come back as 0 and 1. Then the same user sends the 20-combination sweep of section 5.2 in one request. The gate refuses it: 20 rows requested, 1 already used, budget 8.

The unit matters. If the budget counted HTTP calls, one call carrying all 20 rows would pass. TECH 17 adds that a real query-limited service should be tested by an external party (p. 53); the demo implements only the control logic. *Illustrates TECH 16 and TECH 17.*

### 5.9 Register entry and pipeline snapshot (section 9)

`demo/output/data_use_register.json` records the wrapped tree (`safe_tree.joblib`) with the decision `approved_for_demo_release`, the controls applied (set-aside, wrapper constraints, membership and attribute attacks, leaf k-anonymity, size check) and the refused files (`unsafe_tree.joblib`, `tampered_tree.joblib`). `demo/output/pipeline_snapshot.json` stores what is needed to reproduce the approved candidate: the seed, the researcher and set-aside row ids, the wrapper's recommendation and corrected parameters, and the demo policy. The researcher declaration is written in plain language (follow the approved controls, accept the register entry, accept that TRE staff will run attacks); the paper's clause text was left for a qualified legal review. *Illustrates TECH 3 and ELA 4.*

### 5.10 Side by side (section 10)

| Model | Train | Set-aside | Worst-case AUC | Advantage | TPR at 10% FPR | Decision |
|---|---|---|---|---|---|---|
| Unconstrained tree | 1.000 | 0.590 | 0.708 | 0.412 | 0.156 | Refuse |
| Safe wrapper, leaf 20, depth 4 | 0.692 | 0.584 | 0.528 | 0.004 | 0.116 | Release under the demo policy |
| 1-nearest neighbour | | | | | | Refuse: stores 500 rows |
| RBF SVC | | | | | | Refuse: 423 support vectors |
| Tampered tree | | | | | | Refuse: edited after fit |

---

## 6. Demo 2: the official SACRO-ML package

> **In plain words.** The second script runs the same cohort through `sacroml`, the maintained toolkit that grew out of the paper's AI-SDC work. Its safe wrapper is looser than demo 1's (minimum leaf 5 instead of 20), it never approves anything by itself, and its own structural check still calls the wrapped tree risky. Its membership attack gives an AUC near 0.5 even for the tree that memorised everyone, because it looks at different information.

Entry point: `demo/run_sacroml_demo.py`. Package: `sacroml` 2.0.1 from [SACRO-ML](https://github.com/AI-SDC/SACRO-ML). Summary: `demo/output/sacroml/sacroml_report.txt`. Per-attack `report.json` and `report.pdf` live under `demo/output/sacroml/unconstrained_tree/` and `demo/output/sacroml/safe_wrapper_tree/`, in `worst_case`, `structural` and `attribute`. The seeded run took about three and a half minutes.

### 6.1 The package's safe wrapper

* Created with the default leaf size, `SafeDecisionTreeClassifier` warns that `min_samples_leaf = 1` is below the recommended minimum of 5 and marks the configuration as disclosive.
* With constraints applied, it changes `min_samples_leaf` to 5.
* `request_release()` without a `Target` writes `safe_release/target.yaml` and recommends "Proceed to next step of checking". It does not run attacks, and it is not an approval.
* Setting `min_samples_leaf` from 5 back to 1 after `fit()` makes `posthoc_check()` return disclosive, with the message that the parameter changed after the model was fitted.

Passing a `Target` into `request_release()` would also start the package's likelihood-ratio attack (LiRA); the upstream example runs it with 100 shadow models. This demo does not run LiRA.

### 6.2 Unconstrained tree

Training accuracy 1.000, set-aside accuracy 0.590, gap 0.410.

| Check | Seeded result |
|---|---|
| Worst-case membership AUC, 3 repetitions | mean 0.500 (min 0.500, max 0.500); none above the null band 0.377 to 0.623 |
| Structural | `gen_error_risk`, `unnecessary_risk`, `k_anonymity_risk`, `class_disclosure_risk`, `smallgroup_risk` true; `dof_risk` false. Smallest leaf 1 row, under the package threshold of 10 |

The membership AUC of 0.500 needs explaining, and section 7.2 does it with a picture. In short: this attack uses the predicted probabilities only, and a tree of pure leaves gives extreme probabilities to training rows and to set-aside rows alike. The structural attack is what flags the memorisation here.

### 6.3 Wrapped tree (`min_samples_leaf` 5)

Training accuracy 0.868, set-aside accuracy 0.566, gap 0.302. Leaf k-anonymity 5.

| Check | Seeded result |
|---|---|
| Worst-case membership AUC, 3 repetitions | mean 0.494 (min 0.471, max 0.519); none above the null band |
| Structural | The same risk flags true, including `k_anonymity_risk`, because 5 is still under 10. `dof_risk` false |

Moving from leaf size 1 to leaf size 5 is what the published rules file does, and the package's own structural check still calls that tree risky.

### 6.4 Attribute inference

![Reading sacroml attribute inference](img/en/fig12_guess_coverage.svg)

Read every cell as **correct unique guesses / unique guesses made, out of 500 rows**.

| Field | Unconstrained, training | Unconstrained, set-aside | Wrapped, training | Wrapped, set-aside |
|---|---|---|---|---|
| diabetes | 136/136 | 141/141 | 195/257 | 191/246 |
| asthma | no unique guess | no unique guess | 50/67 | 49/64 |
| weight | no unique guess | no unique guess | no unique guess | no unique guess |
| blood pressure | 5/5 | 3/3 | no unique guess | no unique guess |
| smoker | 198/198 | 205/205 | 254/327 | 262/330 |
| age | reconstructed fraction 0.012 | 0.010 | 0.034 | 0.050 |

"136/136" means that every unique guess was right, on the 136 rows (27%) where the attack was willing to guess. It does **not** mean that 136 of 500 rows were guessed correctly. A "no unique guess" cell means the attack abstained on every row. The training and set-aside numbers are close, which is the comparison Appendix G asks for: a model that leaks attributes only for its training rows would show a clear gap. Age is numeric, so the package reports the fraction of rows whose age it can bound within its tolerance, not a guess count.

### 6.5 How to read `report.json`

Each attack folder holds a `report.json` and a `report.pdf`. The JSON is a dictionary with one entry per run, keyed by the attack name and a run id; if you run the script more than once, new runs are appended, so read the last key. Inside each run:

* `metadata.attack_params`: the settings, for example `n_reps: 3` for the worst-case attack, `safe_threshold: 10` for the structural attack.
* `metadata.global_metrics`: the summary. For the worst-case attack, `null_auc_3sd_range` is the chance band and `n_sig_auc_p_vals` counts repetitions whose AUC is significantly above chance (0 here). For the structural attack, the risk flags listed above.
* `attack_experiment_logger.attack_instance_logger`: one entry per repetition. For the worst-case attack: `TPR`, `FPR`, `AUC`, `Advantage`, the FDIF family (`FDIF01` is the 10% tail, with its p-value in `PDIF01`), and `TPR@0.1%` style tail rates. For the attribute attack: `categorical` holds, per field, `train` and `test` lists of five numbers, `[correct, unique guesses, baseline %, number of values, rows]`, where the baseline is the share of the most common value; `quantitative` holds the age fraction.

**Under the hood.** Two details differ from demo 1. The package's worst-case attack is configured with `include_model_correct_feature: false` and `sort_probs: true`: the attack model sees sorted predicted probabilities, not the true label. Its attribute attack keeps a candidate value only when the model's predicted label for that candidate matches the model's prediction for the original row, and requires the unique maximum confidence to pass a threshold.

---

## 7. The two demos side by side

> **In plain words.** The two scripts look at the same data and disagree on purpose, and the disagreement is instructive. They use different leaf sizes, their "worst-case" attacks see different information, and one says "release" while the other says "keep checking".

![Same cohort, two toolkits](img/en/fig11_two_demos.svg)

### 7.1 Three differences that matter

| | Demo 1 (hand-written) | Demo 2 (`sacroml` 2.0.1) |
|---|---|---|
| **Leaf rule** | `min_samples_leaf` 20 and `max_depth` 4, stricter than the Appendix D example | `min_samples_leaf` 5, from the package rules file |
| **Membership attack** | Predicted probabilities plus the true label | Predicted probabilities only |
| **Wrapped tree** | train 0.692, set-aside 0.584, AUC 0.528 | train 0.868, set-aside 0.566, mean AUC 0.494 |
| **Leaf check** | smallest leaf 20 | smallest leaf 5 < 10, so `k_anonymity_risk` is true |
| **Outcome** | release under the demo policy | "Proceed to next step of checking"; structural risk still true |

### 7.2 Why the membership numbers differ

![How sure is each tree about the true label?](img/en/fig05_confidence.svg)

Both scripts call their attack "worst case", but they are different tests.

On the unconstrained tree every leaf is pure, so every prediction is a probability of exactly 0 or 1. The figure shows the confidence each tree gives to the **true** label. Training rows always get 1. Set-aside rows get 1 when the tree happens to be right (59% of the time) and 0 when it is wrong.

* **Demo 1** gives the attack the true label, so it can see "confidence 1 in the right class" versus "confidence 0 in the right class". Members are always in the first group; 41% of non-members are in the second. AUC 0.708.
* **Demo 2** gives the attack only the sorted probabilities. Without the label, "probability 1 for class A" looks the same whether the tree is right or wrong. Members and non-members are equally extreme, so the AUC is 0.500.

An AUC near 0.5 from the package therefore does not mean the tree failed to memorise. In demo 2 the structural attack is the check that catches it. For the wrapped tree with leaves of 20 rows, both groups spread over similar confidences, which is why demo 1's AUC drops to 0.528.

### 7.3 What to take away

Neither demo is an approval process. The hand-written script releases a tree only after forcing leaf 20 and depth 4 and after its own label-aware attack falls inside a local policy. The package recommends further checking and keeps flagging the leaf-5 tree. A real TRE would combine both kinds of evidence with a risk appetite agreed with its data controller (ELA 8, ELA 11).

---

## 8. How to reproduce

Setup is described once, in the repository [README](../../README.md); the seven-step summary of demo 1 is in [demo/README.md](../../demo/README.md). In short, with [uv](https://docs.astral.sh/uv/) installed, from the repository root:

```bash
uv venv --python 3.11
uv pip install -r demo/requirements.txt     # numpy, scikit-learn, sacroml (brings PyTorch)

uv run python demo/run_demo.py              # seconds; writes demo/output/demo_report.txt
uv run python demo/run_sacroml_demo.py      # a few minutes; writes demo/output/sacroml/
```

On Windows PowerShell, activate the environment with a leading dot: `. .\.venv\Scripts\Activate.ps1`.

| Output | Produced by |
|---|---|
| `demo/output/demo_report.txt` | demo 1, all ten sections |
| `demo/output/data_dictionary.json` | demo 1, TECH 8 |
| `demo/output/safe_tree.release.json`, `tampered_tree.release.json` | demo 1, wrapper release reports |
| `demo/output/data_use_register.json`, `pipeline_snapshot.json` | demo 1, section 9 |
| `demo/output/sacroml/sacroml_report.txt` | demo 2 summary |
| `demo/output/sacroml/<model>/<attack>/report.json` and `report.pdf` | demo 2, per attack |
| `demo/output/sacroml/safe_release/target.yaml` | demo 2, `request_release()` |

The figures in this guide and the deck are generated from the repository:

```bash
pip install -r docs/requirements-docs.txt   # python-pptx, cairosvg
python docs/guide/make_figures.py           # docs/guide/img/en and img/es
python docs/make_deck.py                    # docs/GRAIMATTER.pptx
```

`make_figures.py` computes two figures live from the demo code (the planted sweep and the confidence histograms); the other numbers are copied from the seeded reports.

---

## 9. Limits of the demos

* **The cohort is synthetic.** There are no real patients. Seed 7, 1,000 rows, split 500 for the researcher and 500 kept by the TRE.
* **The cut-offs are a demo policy.** The limits in `disclosure.py` exist so the first script can say yes or no. The paper publishes no universal thresholds; ELA 8 describes a risk-based approval agreed with the data controller.
* **The wrapper is stricter than the paper's example.** Demo 1 uses `min_samples_leaf` 20 and `max_depth` 4; Appendix D's example minimum leaf size is 5.
* **`sacroml` uses its own rules.** Its rules file raises `min_samples_leaf` from 1 to 5, and its structural attack marks a leaf as risky below 10 training rows.
* **The official package approves nothing here.** `request_release()` records "Proceed to next step of checking", and the structural attack still flags the wrapped tree.
* **The two membership attacks are different tests.** Demo 1 trains on predicted probabilities plus the true label; `sacroml` scores by predicted probability only. An AUC near 0.5 from the package does not mean the tree failed to memorise.
* **Attribute counts are guesses, not rows.** "136/136 unique guesses correct out of 500 rows" means every unique guess was correct, not that 136 of 500 rows were guessed. "No unique guess" means the attack abstained.
* **LiRA is not run.** The likelihood-ratio attack is in the package; the upstream example uses 100 shadow models.
* **No private SVM.** The repository sketches differential privacy on a released mean only.
* **No legal drafting.** The researcher declaration is plain language; the paper's clause text was left for a qualified legal review.

---

## 10. Glossary

| Term | Meaning |
|---|---|
| **TRE** | Trusted research environment: a secure place where approved researchers analyse sensitive data, with outputs checked before release. |
| **Data controller** | The organisation responsible for the data under data protection law; it agrees the risk appetite (ELA 8, ELA 11). |
| **MDC** | Model disclosure control: a check on the model file before export (TECH 4 to 15). |
| **MQC** | Model query control: a limit on how a released model can be queried (TECH 16, 17). |
| **Holdout / set-aside** | Rows the TRE keeps and never gives to the researcher (TECH 6). |
| **Safe wrapper** | A version of a model class that enforces a constraints file, records its state at `fit()` and offers `request_release()` (TECH 9, 10). |
| **Constraints file** | A human-readable file with the TRE's allowed hyperparameter ranges and model types (Appendix D). |
| **Instance-based model** | A model that needs stored training rows to predict, such as nearest neighbours or a kernel SVM (TECH 11). |
| **Membership inference** | Deciding whether a row was in the training set. |
| **Attribute inference** | Filling in a hidden field of a person by querying the model (Appendix E). |
| **Worst-case attack** | An attack that has the training and held-out rows; a conservative upper bound (Appendix G). |
| **Salem scenarios** | Attacks where the adversary trains shadow models on other data (Appendix A, Table 2). |
| **Structural attack** | `sacroml` check of the model's structure: leaf sizes, degrees of freedom, class disclosure. |
| **LiRA** | Likelihood-ratio membership attack using many shadow models; in `sacroml`, not run here. |
| **Differential privacy (epsilon)** | A guarantee on a release mechanism; smaller epsilon means the release changes less when one person is added or removed (§10.1.3). |
| **AUC, advantage, TPR, FPR, FDIF, posterior** | See section 4. |
| **k-anonymity (of a leaf)** | Number of training rows in the smallest leaf. |
| **RT1, RT2, RT3** | The paper's risk types: careless researcher, malicious researcher, outside attacker (section 1.2). |

---

## 11. References

1. *Green Paper: Recommendations for disclosure control of trained Machine Learning (ML) models from Trusted Research Environments (TREs).* Output of the DARE UK sprint project GRAIMatter, September 2022. `GRAIMATTER Green Paper.pdf` in this repository. An earlier version: E. Jefferson et al., Zenodo, July 2022, doi:10.5281/zenodo.6896214.
2. SACRO-ML (`sacroml` 2.0.1). https://github.com/AI-SDC/SACRO-ML
3. A. Salem, Y. Zhang, M. Humbert, P. Berrang, M. Fritz, M. Backes. *ML-Leaks: Model and Data Independent Membership Inference Attacks and Defenses on Machine Learning Models.* arXiv:1806.01246, 2018 (paper reference [37]).
4. F. Ritchie. *The "Five Safes": a framework for planning, designing and evaluating data access solutions.* Zenodo, 2017, doi:10.5281/zenodo.897821 (paper reference [2]).
5. This repository: [README.md](../../README.md), [demo/README.md](../../demo/README.md), [docs/brief-for-presentation-and-guide.md](../brief-for-presentation-and-guide.md).

---

## Appendix A: how the guide, slides and demos line up

The guide and the deck follow the same order: the problem and the paper first (sections 1 to 4, slides 1 to 7), then the demos (sections 5 to 7, slides 8 to 18), then the wider picture (sections 8 and 9, slides 19 to 22).

| Guide section | Slides (deck order) | Demo output |
|---|---|---|
| 1. What a TRE is protecting | 1 *Cover*, 2 *The problem*, 3 *TECH 4 · Two families of control* | – |
| 2. Map of the green paper | 4 *The paper*, 19 *What the paper also asks for* | – |
| 3. Cohort and holdout | 5 *TECH 6 · TECH 8 · The cohort* | `data_dictionary.json` |
| 4. Metrics | 7 *Appendix F · Reading attack metrics* | – |
| 5.2 Planted record | 6 *Appendix E · Attribute inference* | `demo_report.txt` §2 |
| 5.3 Differential privacy | 14 *§10.1.3 · TECH 12* | `demo_report.txt` §3 |
| 5.4 Unconstrained tree | 8 *Demo 1 · Unconstrained tree* | `demo_report.txt` §4 |
| 5.5 Safe wrapper and the quiet failure | 9 *Demo 1 · Safe wrapper*, 10 *Appendix F · The tail* | `demo_report.txt` §5 |
| 5.6 Instance-based models | 11 *TECH 11* | `demo_report.txt` §6 |
| 5.7 Editing after `fit()` | 12 *RT1 · RT2 · TECH 3* | `demo_report.txt` §7, `tampered_tree.release.json` |
| 5.8 Query budget | 13 *TECH 16* | `demo_report.txt` §8 |
| 5.9 Register and snapshot | 12 (notes) | `data_use_register.json`, `pipeline_snapshot.json` |
| 6.1 to 6.3 SACRO-ML wrapper and attacks | 15 *Demo 2 · sacroml 2.0.1* | `sacroml_report.txt` |
| 6.4 and 6.5 Attribute inference, `report.json` | 17 *Demo 2 · Attribute inference* | `sacroml/*/attribute/report.json` |
| 7.1 Differences | 18 *Two demos compared* | both reports |
| 7.2 Why the membership numbers differ | 16 *Why the two membership numbers differ* | – |
| 8. How to reproduce | 21 *Run it yourself* | – |
| 9. Limits | 20 *Limits* | – |
| 10. Glossary, 11. References | 22 *References* | – |

### Suggested workshop agenda (about 75 minutes)

| Time | Block | Material |
|---|---|---|
| 0:00 | Why a model is a new kind of output; MDCs and MQCs; the paper's five sets of recommendations | Guide §1 and §2, slides 1 to 4 |
| 0:10 | The cohort, the holdout and the planted record | Guide §3 and §5.2, slides 5 and 6 |
| 0:18 | Reading attack metrics | Guide §4, slide 7 |
| 0:28 | Demo 1: unconstrained tree, safe wrapper, the quiet failure | Guide §5.4 and §5.5, slides 8 to 10 |
| 0:38 | Demo 1: instance-based models, tampering, query budget, differential privacy | Guide §5.3, §5.6 to §5.9, slides 11 to 14 |
| 0:50 | Demo 2 and the comparison | Guide §6 and §7, slides 15 to 18 |
| 1:02 | What else the paper asks for; limits; running the demos; questions | Guide §8 and §9, slides 19 to 22 |

---

*Figures are generated by `docs/guide/make_figures.py` (English and Spanish versions). The planted sweep and the confidence histograms are computed live with the demo code; the other numbers come from the seeded reports.*
