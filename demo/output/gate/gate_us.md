# Release gate evidence: FAIL

- Run: `gate-20261015T193139Z`
- Timestamp: 2026-10-15T19:31:39+00:00
- Regimes: `us`
- Demos run: demo1, demo3, demo4
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
| supply_chain | Tampered supplier files that passed the pin and the scan or floor (of 4) | demo4 | 0 | 0 | yes |

## Controls

_binding: `statute` = legal obligation; `guidance` = voluntary; `supervisory` = examiner expectation; `recommendation` = the GRAIMATTER green paper._

### NIST AI RMF

| Ref | Control | Binding | Status |
| --- | --- | --- | --- |
| MEASURE 2.6 | Residual negative risk does not exceed the risk tolerance. | guidance | **fail** (evasion, extraction, poisoning) |
| MEASURE 2.7 | Security and resilience are evaluated and documented. | guidance | **fail** (evasion, extraction, poisoning) |
| MEASURE 2.10 | Privacy risk is examined and documented. | guidance | pass |
| GOVERN 6.1 | Policies and procedures address the AI risks of third-party entities, including supplied models. | guidance | pass |

### Federal MRM

| Ref | Control | Binding | Status |
| --- | --- | --- | --- |
| SR 26-02 validation | Independent validation: outcomes analysis on data the developer never saw. | supervisory | pass |
| SR 26-02 monitoring | Ongoing monitoring: a repeatable gate in CI with numeric tolerances. | supervisory | **fail** (evasion, extraction, poisoning) |
| SR 26-02 third-party model | A vendor model is checked like an in-house one: the file in use is the file that was approved. | supervisory | pass |
| SR 26-02 documentation | A model-risk file that records the tests, the tolerances and what failed. | supervisory | pass |

## Remediation required

- NIST AI RMF MEASURE 2.6: breach in evasion, extraction, poisoning
- NIST AI RMF MEASURE 2.7: breach in evasion, extraction, poisoning
- Federal MRM SR 26-02 monitoring: breach in evasion, extraction, poisoning

## Scope

The mapping of demo metrics to these clauses was made for this repository; the frameworks do not cross-reference each other this precisely and none of them sets numeric thresholds. The tolerances are a demo risk appetite (GRAIMATTER ELA 8), not official cut-offs. Synthetic data only. Not legal advice.
