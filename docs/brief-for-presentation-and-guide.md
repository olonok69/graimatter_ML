# Brief: GRAIMATTER paper and demos

Handoff for another agent. Use this file as the source for two artefacts:

1. A presentation that explains the paper and shows what the demos found.
2. A written guide that explains the paper and walks through both demos.

Write both for a data scientist who has not read the 99-page paper. Explain the idea before the metric. Keep legal, ethics, costing, training, and public-involvement material short: those sections exist in the paper, and these demos cover the technical disclosure checks.

## How to use the source paper

The PDF is `GRAIMATTER Green Paper.pdf` in the repository root (99 pages).

Full title, from the cover: *Green Paper: Recommendations for disclosure control of trained Machine Learning (ML) models from Trusted Research Environments (TREs)*. It is an output of the DARE UK sprint *Guidelines and Resources for AI Model Access from TrusTEd Research environments (GRAIMatter)*.

Summarise the paper in your own words. Do not paste recommendation paragraphs, case-study narratives, or other long passages from the PDF into the slides or the guide. Recommendation identifiers (TECH 6, ELA 8, Appendix F, and so on) are fine. Cite the PDF and page or section when a claim comes from the paper. Cite this brief, `demo/output/demo_report.txt`, or `demo/output/sacroml/sacroml_report.txt` when a number comes from a demo.

## Claims to keep accurate

- The cohort is synthetic. There are no real patients. Seed is 7. Size is 1,000 rows, split 500 for the researcher and 500 kept by the TRE.
- Cut-offs in `demo/graimatter_demo/disclosure.py` are a demo policy so the first script can say yes or no. The paper does not publish universal cut-offs. ELA 8 describes a risk-based approval, agreed with the data controller.
- The hand-written safe wrapper uses `min_samples_leaf` of 20 and `max_depth` of 4. Appendix D of the paper shows the constraints-file format; its example minimum leaf size is 5. The demo is stricter so the contrast shows up on a few hundred rows.
- `sacroml` 2.0.1 uses its own rules file. That file raises `min_samples_leaf` from 1 to 5. Its structural attack marks a leaf as risky when the leaf holds fewer than 10 training rows.
- On the seeded run, the hand-written demo **releases** the stricter wrapper and **refuses** the unconstrained tree. The official package **does not approve** its wrapped tree for export. `request_release()` records "Proceed to next step of checking". The structural attack then still flags that tree.
- The two membership attacks are different tests. The hand-written worst-case attack trains a second model on predicted probabilities plus the true label. The `sacroml` worst-case attack scores rows by predicted probability only. An AUC near 0.5 from the package does not mean the tree failed to memorise.
- Attribute-inference lines such as "136/136 unique guesses correct out of 500 rows" mean every unique guess was correct. They do not mean 136 of 500 rows were guessed. A line that says "no unique guess" means the attack abstained.
- The likelihood-ratio attack (LiRA) is in the package. This demo does not run it. The upstream example uses 100 shadow models.
- This repository does not implement a differentially private SVM. It sketches differential privacy on a released mean.
- Researcher-declaration text in the demo is plain language. The paper's clause text was left for a qualified legal review. Do not draft EULA clauses.

## The problem the paper is solving

A trusted research environment lets researchers analyse sensitive data without taking the data away. The new export is the trained model. A model file can be smaller than the table and still carry information about individual rows: a nearest-neighbour model stores the rows, a support-vector classifier stores support vectors, and a deep tree can isolate single people in its leaves.

The paper's technical recommendations split controls into two families (TECH 4):

- **Model disclosure controls (MDCs).** Checks on the model file before it leaves: holdout data, attack simulations, file type and size, safe wrappers, extra controls for models that memorise.
- **Model query controls (MQCs).** Limits on how the model can be questioned after release, so an attacker cannot sweep hidden attributes by sending many rows in one request.

The paper also has legal and ethics recommendations (ELA), costing (C), training (TR), and public involvement (PPIE). The demos illustrate the MDC and MQC ideas. They are not an approval process.

## Recommendations the demos illustrate

Use these as the spine of both artefacts. One slide, or one guide section, per row is enough. The other TECH items can sit on a single "what the paper also asks for" slide.

| Paper | What it asks for, in brief | Where the demos show it |
| --- | --- | --- |
| TECH 6 | Keep a share of the data aside. The research team never trains on it. Use it to assess the model. | 500 of 1,000 rows are withheld. |
| TECH 7 | Run a range of checks before release: accuracy on the holdout, attacks, file size, file type. | `disclosure.decide()` in the first demo. Structural, worst-case, and attribute attacks in the second. |
| TECH 8 | Researchers supply a data dictionary of model inputs. | `demo/output/data_dictionary.json`. Appendix C is the paper's template. |
| TECH 9–10 | A safe wrapper reads a constraints file, can correct hyperparameters, records a snapshot, and exposes `request_release()`. | `demo/constraints.json` and `SafeDecisionTreeClassifier`. The official class is `sacroml`'s own wrapper. |
| TECH 11 | Instance-based models, and models that memorise, need extra controls: aggregated data, differential privacy, or query limits. | k-nearest neighbours and a standard SVC are refused. No private SVM is trained. |
| TECH 12 | Differential privacy needs an informed choice. TRE staff choose the seed. Selecting the nicest of many noisy releases cancels the protection. | Laplace noise on a mean, then a best-of-50 cherry-pick. |
| TECH 16 | Query limits should count rows, not HTTP calls. One request can carry a whole sweep. | Budget of 8 rows. One patient query is allowed. A 20-row sweep is refused. |
| TECH 17 | A real query-limited service needs an external test. | Named in the first report. The demo only implements the gate. |
| Appendix E | Attribute inference: fill in hidden fields of a person by querying the model. | One planted record in the first demo. Column-wise attack in `sacroml`. |
| Appendix F | How to read attack metrics, including the tail rather than only the average. | AUC, advantage, TPR at a low FPR, FDIF, membership posterior. |
| Appendix G | Worst-case membership inference, where the attacker has the training and holdout labels. | Both demos. They implement that worst case differently. See the comparison below. |
| ELA 8 | Thresholds are a risk appetite agreed with the data controller. | Stated in `disclosure.py`. Do not present the demo numbers as the paper's thresholds. |

The paper also recommends: discuss disclosure risk when the project is applied for (TECH 1); give researchers ML tools inside the TRE (TECH 2); snapshot the pipeline that produced an approved model (TECH 3); staff who can run the attacks (TECH 5); special treatment for ensembles (TECH 13) and federated learning (TECH 14); treat synthetic data as personal data (TECH 15). Appendix A reports experiments on hyperparameters. Experiment 2 is the warning that a range which looked safe on a previous dataset is not, by itself, a release decision.

## Metrics, in words a slide can carry

Define each term once in the guide. On slides, use the short form.

- **Training accuracy** is the score on rows the model has seen. **Set-aside accuracy** is the score on the 500 rows the researcher never received. A large gap means the model has fit this sample, including noise.
- **Membership inference** asks whether a row was in the training set. **AUC** near 0.5 means the attack does no better than chance across thresholds. Higher means the model treats members and non-members differently.
- **Advantage** in this demo is the absolute gap between the true-positive rate and the false-positive rate.
- **TPR at 10% FPR** is how often the attack catches a real training row when it is only allowed to raise a false alarm on about 10% of non-members. A model can have a modest AUC and still be exposed in that tail.
- **FDIF** (frequency difference) asks whether training rows pile up in the extreme scores. The demo treats a high FDIF with a small permutation p-value as evidence of that pile-up. Appendix F is why a controller can care about FDIF even when AUC is near 0.5.
- **Membership posterior.** If the attacker says "this row was in training", the chance that is true depends on how rare members are. The demo uses `P = (A × TPR) / (A × TPR + (1 − A) × FPR)`, with A = 0.5 (half the candidates are members) and A = 0.01 (1 in 100).
- **Attribute inference** tries to fill in a hidden field. In the planted case study, the attacker knows age, diabetes, asthma, and smoking, and tries every weight × blood-pressure pair (4 × 5 = 20). The pair with a uniquely high predicted confidence is the guess.
- **k-anonymity of a leaf** is the number of training rows in the smallest leaf. A leaf of 1 is one person.

## The synthetic cohort

Generated by `demo/graimatter_demo/cohort.py`.

Clinical columns: age, diabetes, asthma, weight, blood pressure, smoker. The label `high_risk` is drawn from a known logistic function of those columns. Ten `noise_*` columns have no label signal. They exist so an unconstrained tree has something to memorise.

Weight levels: underweight, normal, overweight, obese. Blood pressure levels: low, slightly high, high, very high, extremely high.

The planted person in section 2 of the first demo is age 62, diabetic, asthmatic, and a smoker. The hidden truth is overweight and slightly high blood pressure.

## Demo 1 — hand-written checks

Entry point: `demo/run_demo.py`. Narrative: `demo/README.md`. Report: `demo/output/demo_report.txt`. Policy: `demo/graimatter_demo/disclosure.py`. Constraints: `demo/constraints.json`.

Run from the repository root, after the setup in `README.md`:

```powershell
uv run python demo/run_demo.py
```

### Demo policy (first script only)

| Rule | Limit |
| --- | --- |
| Worst-case membership AUC | 0.62 |
| Advantage | 0.20 |
| TPR at 10% FPR | 0.35 |
| FDIF, and its p-value | 0.20, with p ≤ 0.05 |
| Attribute risk ratio | 1.35 |
| Training minus set-aside accuracy | 0.15 |
| Model file size ÷ training table size | 0.75 |
| Accepted file types | `.joblib`, `.pkl` |

A model that stores training rows is refused even when another rule would pass.

### Seeded results to put on slides

**Attribute inference on the planted record.** The unique highest confidence is the planted pair, overweight and slightly high, at confidence 1.000. The next guesses sit at 0.500. That is the Appendix E story on a model that actually split on those fields.

**Differential privacy on a mean (section 10.1.3 and TECH 12).** An attacker knows every age except whether one person was included, and sees only the released mean. Accuracy is how often they guess inclusion correctly. 0.50 is a coin toss.

| Release | Attacker accuracy | Laplace scale |
| --- | --- | --- |
| Deterministic mean | 1.000 | 0 |
| epsilon 0.2 | 0.487 | 0.600 |
| epsilon 1.0 | 0.522 | 0.120 |
| epsilon 8.0 | 0.703 | 0.015 |

At epsilon 0.2, one noisy draw misses the true mean by 0.3053. The closest of 50 draws misses by 0.0084. The point of the slide: picking the draw that looks most like the non-private answer undoes the noise, so TRE staff would choose the seed without looking at accuracy.

**Unconstrained decision tree. Decision: do not release.**

| | |
| --- | --- |
| Training accuracy | 1.000 |
| Set-aside accuracy | 0.590 |
| Gap | 0.410 (limit 0.15) |
| Smallest leaf | 1 training row |
| File size | 18,150 bytes vs training table 68,000 bytes (ratio 0.267; size alone does not fail) |
| Worst-case membership AUC | 0.708 (limit 0.62) |
| Advantage | 0.412 (limit 0.20) |
| TPR / FPR | 1.000 / 0.588 |
| TPR at 10% FPR | 0.156 (does not itself trip the 0.35 limit) |
| FDIF | 0.620, p = 0.003 |
| Posterior if flagged | 0.630 when half of candidates are members; 0.017 when 1 in 100 are |
| Salem-synth AUC | 0.703; TPR at 10% FPR 0.514; FDIF 1.000 |
| Weight attribute inference | Abstained. Ratio 1.000. The tree isolated rows with the noise columns, so changing weight did not leave the leaf. |

**Same data through the safe wrapper. Decision: allow release under the demo policy.**

The wrapper moves `min_samples_leaf` from 1 to 20 and `max_depth` from unlimited to 4. Smallest leaf holds 20 training rows. `request_release()` says to run the file through the next checking step. The attack numbers are what the export rule uses.

| | |
| --- | --- |
| Training accuracy | 0.692 |
| Set-aside accuracy | 0.584 |
| Worst-case membership AUC | 0.528 |
| Advantage | 0.004 |
| TPR at 10% FPR | 0.116 |
| FDIF | 0.020, p = 0.445 |
| Posterior if flagged | 0.502 at half members; 0.010 at 1 in 100 |

Salem-synth on this same wrapped model has AUC 0.512 and FDIF 0.280 (p = 0.003). Put this on a slide as the Appendix F warning: the average attack looks like chance, and the tail does not. This demo's export rule follows the worst-case FDIF of 0.020, so it still releases. A data controller could refuse on the Salem tail.

Weight attribute inference abstains on this model as well.

**Instance-based models. Decision: do not release.**

- A 1-nearest-neighbour model stores all 500 training rows. File ratio 1.010.
- An RBF support-vector classifier stores 423 support vectors out of 500 rows. File ratio 0.94.
- The safe wrappers for both classes refuse to fit. The paper's alternatives are aggregated data, a differentially private algorithm, or a query-limited service.

**Tamper after `fit()` (risk types the demo calls RT1 and RT2). Decision: do not release.**

The researcher overrides the constraints (`min_samples_leaf` 1, unlimited depth). After fitting, parameters are edited back toward the allowed values, a hidden attribute is added, and the smallest leaf still holds 1 row. The release report says not to release, and names the changed parameters and `hidden_rows`.

A `.txt` file is refused because it is not `.joblib` or `.pkl`.

**Query budget.** The budget is 8 rows. One patient lookup (1 row) is allowed. Predicted class probabilities are 0 and 1. The 20-combination attribute sweep is refused: 20 rows requested, 1 already used. The slide should say the unit is rows, because one HTTP request can carry all 20 combinations.

**Register.** `demo/output/data_use_register.json` records `approved_for_demo_release` for the wrapped tree that passed. `demo/output/pipeline_snapshot.json` is the TECH 3 snapshot of that candidate.

### Side-by-side line for the first demo

| Model | Train | Set-aside | Worst-case AUC | Advantage | TPR at 10% FPR | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| Unconstrained tree | 1.000 | 0.590 | 0.708 | 0.412 | 0.156 | Refuse |
| Safe wrapper, leaf 20, depth 4 | 0.692 | 0.584 | 0.528 | 0.004 | 0.116 | Release under the demo policy |
| 1-nearest neighbour | | | | | | Refuse: stores 500 rows |
| RBF SVC | | | | | | Refuse: 423 support vectors |
| Tampered tree | | | | | | Refuse: edited after fit |

## Demo 2 — official SACRO-ML package

Entry point: `demo/run_sacroml_demo.py`. Package: `sacroml` 2.0.1 from [SACRO-ML](https://github.com/AI-SDC/SACRO-ML), the maintained toolkit from the AI-SDC repository named in the green paper. Summary: `demo/output/sacroml/sacroml_report.txt`. Per-attack `report.json` and `report.pdf` live under `demo/output/sacroml/unconstrained_tree/` and `demo/output/sacroml/safe_wrapper_tree/`, in `worst_case`, `structural`, and `attribute`. The target file is `demo/output/sacroml/safe_release/target.yaml`.

Same cohort and same 500/500 split as demo 1.

```powershell
uv run python demo/run_sacroml_demo.py
```

Expect several minutes. The seeded run that produced the numbers below finished in about three and a half minutes.

### What the package did

- `SafeDecisionTreeClassifier` with the default leaf size prints that `min_samples_leaf = 1` is below the recommended minimum of 5, and marks the configuration disclosive.
- With constraints applied, it changes `min_samples_leaf` to 5.
- `request_release()` without a Target writes the target YAML and recommends "Proceed to next step of checking". It does not run attacks.
- Setting `min_samples_leaf` from 5 back to 1 after `fit()` makes `posthoc_check()` return disclosive, with the message that the parameter changed after the model was fitted.

### Unconstrained tree

Training accuracy 1.000. Set-aside accuracy 0.590. Generalisation gap 0.410.

| Check | Seeded result |
| --- | --- |
| Worst-case membership AUC, 3 repetitions | mean 0.500 (min 0.500, max 0.500). Zero repetitions above the null band 0.377–0.623 |
| Structural | `gen_error_risk`, `unnecessary_risk`, `k_anonymity_risk`, `class_disclosure_risk`, `smallgroup_risk` true. `dof_risk` false. Smallest leaf is 1 row, under the package threshold of 10 |
| Attribute inference | See the table below |

Explain the membership AUC on the slide: this attack uses predicted probability only. A tree of pure leaves is extreme on training rows and on set-aside rows, so the score does not separate members. The structural attack is what flags memorisation here.

### Wrapped tree (`min_samples_leaf` 5)

Training accuracy 0.868. Set-aside accuracy 0.566. Gap 0.302. Leaf k-anonymity 5.

| Check | Seeded result |
| --- | --- |
| Worst-case membership AUC, 3 repetitions | mean 0.494 (min 0.471, max 0.519). Zero repetitions above the same null band |
| Structural | Same risk flags true, including `k_anonymity_risk`, because 5 is still under 10. `dof_risk` false |

The useful sentence: moving from leaf size 1 to leaf size 5 is what the published rules file does, and the package's own structural check still calls that tree risky. The hand-written demo only releases a tree after it has forced leaf size 20 and depth 4, and after its own label-aware attack falls inside the demo limits.

### Attribute inference from `sacroml`

Read every cell as "correct unique guesses / unique guesses made, out of 500 rows".

| Field | Unconstrained, training | Unconstrained, set-aside | Wrapped, training | Wrapped, set-aside |
| --- | --- | --- | --- | --- |
| diabetes | 136/136 | 141/141 | 195/257 | 191/246 |
| asthma | no unique guess | no unique guess | 50/67 | 49/64 |
| weight | no unique guess | no unique guess | no unique guess | no unique guess |
| blood pressure | 5/5 | 3/3 | no unique guess | no unique guess |
| smoker | 198/198 | 205/205 | 254/327 | 262/330 |
| age | reconstructed fraction 0.012 | 0.010 | 0.034 | 0.050 |

Age is a numeric reconstruction within the package bound, not a unique-guess count. Diabetes and smoker on the unconstrained tree are perfectly correct **among the rows where the attack was willing to make a unique guess**, and those guesses cover well under half of the 500 rows.

## Suggested presentation

Aim for about 16–20 slides. Title each slide as a claim, then support it. Suggested order:

1. Title. Disclosure control for a model leaving a TRE. GRAIMATTER green paper, plus two demos on synthetic data.
2. The export is the model, not a table of patients.
3. Two families of control: checks on the file, and limits on later queries.
4. The holdout the researcher never sees (TECH 6), on this 1,000-row cohort.
5. One planted person, and how 20 queries recover weight and blood pressure.
6. What the attack metrics mean, with one picture: chance, a tail, and "how rare is a member?".
7. Unconstrained tree: perfect training accuracy, leaf of 1, membership AUC 0.708, refused.
8. Wrapper with leaf 20 and depth 4: membership AUC 0.528, released under a demo policy. State that the policy is local.
9. The quiet failure: Salem AUC near 0.5 with FDIF 0.280. A controller could still refuse.
10. Nearest neighbours and SVC store rows. Refuse, or use aggregation, private training, or a query service.
11. Editing the model after `fit()`, and why the snapshot exists.
12. A query budget that counts rows. One patient allowed, twenty combinations blocked.
13. Differential privacy on a mean, and why the best of 50 draws is not a private release.
14. The official package on the same data: leaf minimum 5, recommendation to continue checking, structural attack still flags the wrapped tree.
15. Why the two membership numbers differ (probability only, versus probability plus the true label).
16. What this repository does not decide: legal clauses, a real data controller's risk appetite, LiRA, a private SVM.
17. Where to run the demos and where the reports are.

Speaker notes should carry the definitions. Slide bodies should carry the numbers from the tables above, not new ones.

## Suggested guide

A short document, readable on its own, in this order:

1. What a TRE is protecting when the output is a trained model.
2. A map of the green paper: technical recommendations, then one paragraph each on legal and ethics, cost, training, and public visibility of data use. Point at the PDF for the clause text.
3. The synthetic cohort and the holdout.
4. A glossary of the metrics, with the formulas this repository actually uses.
5. Walkthrough of `demo/run_demo.py` in the same order as `demo_report.txt` (sections 1–10). Quote the seeded numbers. After each section, name the TECH or appendix it illustrates.
6. Walkthrough of `demo/run_sacroml_demo.py`, including how to read `report.json` and why a guess rate of 1.0 can still cover few rows.
7. A comparison section with the two tables side by side and the three differences that matter: leaf size 20 versus 5, label-aware membership attack versus probability-only, and "release under a demo policy" versus "proceed to the next check, structural risk still true".
8. How to reproduce: the `uv` steps from `README.md`, both commands, and the output paths.
9. Limits of the demos, copied from "Claims to keep accurate" above.

Link the guide to `README.md` for setup and to `demo/README.md` for the seven-step list. Do not fork a third copy of the install commands beyond a short pointer, unless the guide is meant to be read offline without the repository README.

## Repository map

| Path | Role |
| --- | --- |
| `GRAIMATTER Green Paper.pdf` | Source paper |
| `README.md` | Environment setup and how to run both scripts |
| `demo/README.md` | What the hand-written walkthrough covers |
| `demo/run_demo.py` | Hand-written demo |
| `demo/run_sacroml_demo.py` | Official-package demo |
| `demo/requirements.txt` | `numpy`, `scikit-learn`, `sacroml`. Installing `sacroml` also installs PyTorch |
| `demo/constraints.json` | Hyperparameter envelope for the hand-written wrapper |
| `demo/graimatter_demo/` | Cohort, metrics, attacks, safe wrapper, disclosure policy, query gate, differential-privacy sketch |
| `demo/output/demo_report.txt` | Seeded write-up of demo 1 |
| `demo/output/sacroml/sacroml_report.txt` | Seeded write-up of demo 2 |
| `docs/brief-for-presentation-and-guide.md` | This brief |

Python 3.11. The virtual environment is `.venv`, created with `uv venv --python 3.11`. On Windows PowerShell, activate with a leading dot: `. .\.venv\Scripts\Activate.ps1`.
