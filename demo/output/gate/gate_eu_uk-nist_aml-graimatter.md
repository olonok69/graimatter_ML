# Release gate evidence: FAIL

- Run: `gate-20261015T122500Z`
- Timestamp: 2026-10-15T12:25:00+00:00
- Regimes: `eu_uk, nist_aml, graimatter`
- Demos run: demo1, demo3
- Declared out of scope for this run: demo2. Controls that need them are reported as not evidenced and do not fail the run.

## Tolerance gate

| Category | Metric | Demo | Value | Tolerance | Within |
| --- | --- | --- | --- | --- | --- |
| membership | Worst-case membership AUC | demo1 | 0.528 | 0.620 | yes |
| membership | Membership advantage (TPR - FPR) | demo1 | 0.004 | 0.200 | yes |
| membership | Membership TPR at 10% FPR | demo1 | 0.116 | 0.350 | yes |
| membership | Membership FDIF, counted only when significant | demo1 | 0.020 (p=0.445) | 0.200 | yes |
| attribute | Attribute risk ratio for weight | demo1 | 1 | 1.350 | yes |
| generalisation | Training minus TRE-holdout accuracy | demo1 | 0.108 | 0.150 | yes |
| stored_rows | Training rows stored in the model file | demo1 | 0 | 0 | yes |
| stored_rows | Model file size / training table size | demo1 | 0.051 | 0.750 | yes |
| release_check | Known-disclosive files the release check let through (of 5) | demo1 | 0 | 0 | yes |
| query_budget | Rows of the 20-row attribute sweep the query gate allowed | demo1 | 0 | 0 | yes |
| query_budget | 1 if the query gate let a 1,000-row request through | demo3 | 0 | 0 | yes |
| evasion | High-risk people who evade by misreporting smoking, weight, blood pressure | demo3 | 0.787 | 0.100 | **NO** |
| evasion | Same, with smoking verified by a test | demo3 | 0.328 | 0.100 | **NO** |
| evasion | Same, with smoking and weight measured in clinic | demo3 | 0.207 | 0.100 | **NO** |
| extraction | Agreement of a copy trained on one query budget of labels | demo3 | 0.869 | 0.800 | **NO** |
| poisoning | Worst rise in trigger success after poisoning, over the clean model | demo3 | 0.717 | 0.100 | **NO** |

## Controls

_binding: `statute` = legal obligation; `guidance` = voluntary; `supervisory` = examiner expectation; `recommendation` = the GRAIMATTER green paper._

### EU AI Act

| Ref | Control | Binding | Status |
| --- | --- | --- | --- |
| Art. 15(5) data poisoning | Resilience against attacks that manipulate the training data set. | statute | **fail** (poisoning) |
| Art. 15(5) model evasion | Resilience against inputs designed to cause the model to make a mistake. | statute | **fail** (evasion) |
| Art. 15(5) confidentiality attacks | Resilience against attacks that extract the model or infer its training data. | statute | **fail** (extraction) |

### UK Code of Practice / ETSI EN 304 223

| Ref | Control | Binding | Status |
| --- | --- | --- | --- |
| 3.1 | Threat modelling covers AI-specific attacks such as data poisoning, model inversion and membership inference. | guidance | **fail** (poisoning, evasion) |
| 6.2 | APIs limit the rate of model access to hinder reverse engineering and rapid poisoning. | guidance | **fail** (extraction) |
| 9.4 | Outputs do not let users reverse engineer non-public aspects of the model or its training data. | guidance | **fail** (extraction) |

### NIST AI 100-2e2025

| Ref | Control | Binding | Status |
| --- | --- | --- | --- |
| NISTAML.025 | Black-box evasion. | guidance | **fail** (evasion) |
| NISTAML.023 | Backdoor poisoning. | guidance | **fail** (poisoning) |
| NISTAML.031 | Model extraction. | guidance | **fail** (extraction) |
| NISTAML.032 | Reconstruction, including attribute inference (section 2.4.1). | guidance | pass |
| NISTAML.033 | Membership inference. | guidance | pass |

### GRAIMATTER

| Ref | Control | Binding | Status |
| --- | --- | --- | --- |
| TECH 6 | Keep part of the data aside, never give it to the researchers, and score the model on it. | recommendation | pass |
| TECH 7 | Run a range of checks before release: holdout accuracy, attack simulations, file size. | recommendation | pass |
| TECH 9-10 | Safe wrappers correct hyperparameters and catch changes made after fit(). | recommendation | pass |
| TECH 11 | Instance-based models, which store training rows, are not released as they are. | recommendation | pass |
| TECH 16 | Limit the queries on a model once it is released. | recommendation | pass |
| TECH 7, 9 (SACRO-ML) | The same checks with the maintained AI-SDC toolkit agree with the hand-written ones. | recommendation | not_evidenced (needs demo2, out of scope) |

## Remediation required

- EU AI Act Art. 15(5) data poisoning: breach in poisoning
- EU AI Act Art. 15(5) model evasion: breach in evasion
- EU AI Act Art. 15(5) confidentiality attacks: breach in extraction
- UK Code of Practice / ETSI EN 304 223 3.1: breach in poisoning, evasion
- UK Code of Practice / ETSI EN 304 223 6.2: breach in extraction
- UK Code of Practice / ETSI EN 304 223 9.4: breach in extraction
- NIST AI 100-2e2025 NISTAML.025: breach in evasion
- NIST AI 100-2e2025 NISTAML.023: breach in poisoning
- NIST AI 100-2e2025 NISTAML.031: breach in extraction

## Scope

The mapping of demo metrics to these clauses was made for this repository; the frameworks do not cross-reference each other this precisely and none of them sets numeric thresholds. The tolerances are a demo risk appetite (GRAIMATTER ELA 8), not official cut-offs. Synthetic data only. Not legal advice.
