# Adversarial Machine Learning: Presenter Guide

**A slide-by-slide companion to `docs/Adversarial_ML.pptx` (58 slides)**

This guide is for whoever presents the deck, live or as the video series. It follows the slides in order, one section per slide, and gives you what to say, the numbers to have ready, the questions people tend to ask, and where to look when you want more. It does not replace the technical guide ([English](AML_Technical_Guide_EN.md), [Spanish](AML_Guia_Tecnica_ES.md)), which stays the reference for engineers: it explains every attack, metric and line of code in depth. This guide is shorter on code and longer on explanation, and every section points to the technical-guide sections behind it. A Spanish version is in [Guia_Presentador_ES.md](Guia_Presentador_ES.md). If someone asks how a demo computes a number, the demo guide ([English](Demo_Guide_EN.md), [Spanish](Guia_Demos_ES.md)) walks through the code behind each section of its output.

---

## How to use this guide

Each slide has the same blocks:

* **On screen**: what the slide shows, so you can rehearse without the deck open.
* **Say**: a script in spoken style. Read it once or twice, then present in your own words. The deck's speaker notes are a shorter version of the same text.
* **Key facts**: the numbers and sources you may be asked to repeat. All demo numbers come from the seeded reports in `demo/output/` and do not change between runs.
* **If asked**: short answers to questions that come up often.
* **Go deeper**: the technical-guide sections (written "TG §x"), the demo output and the source documents.
* **Next**: one line to move to the following slide.

The deck is in four parts, and each part is one video; Part 4 is two videos, 4a and 4b:

| Part | Video | Slides | Technical guide | Minutes |
|---|---|---|---|---|
| Opening and Part 1 · Attacks | 1 | 1-15 | §1-7 | 45 |
| Part 2 · Frameworks | 2 | 16-20 | §8 | 13 |
| Part 3 · A high-trust case: GRAIMATTER | 3 | 21-25 | §9-11 | 10 |
| Part 4a · The attacks in detail: the CIA triad and the supply chain | 4a | 26-36 | §12-16 | 40, plus the demo runs |
| Part 4b · The attacks in detail: privacy, then the closing | 4b | 37-58 | §16-27 | 45, plus the demo runs |

Each video opens with a slide that says what it covers (slides 1, 16, 21, 26 and 37) and closes with a "Next" line that leads into the following one, so a video can be recorded on its own. Part 4 repeats some results from Part 1 on purpose: Part 1 shows each attack in one figure, Part 4 runs the demo and reads every section of its output.

Part 1 does not follow the technical guide's order exactly: the deck shows evasion (slide 7), poisoning (8), the privacy family (9), extraction (10) and the supply chain (11), while the guide groups the demo 3 and demo 4 attacks in §3 and privacy in §4. The "Go deeper" lines handle the jump.

### Before the session

* **Run the demos once**, so you have the reports at hand and know how long they take: `uv run python demo/run_aml_demo.py` (demo 3, seconds), `uv run python demo/run_confidentiality_demo.py` (demo 5, seconds), `uv run python demo/run_supply_chain_demo.py` (demo 4, seconds), `uv run python demo/run_demo.py` (demo 1, seconds), `uv run python demo/run_sacroml_demo.py` (demo 2, a few minutes) and `uv run python demo/run_gate.py`. Setup is in the [README](../../README.md) and TG §24.
* **Keep open**: `demo/output/aml_report.txt`, `demo/output/confidentiality_report.txt`, `demo/output/supply_chain_report.txt`, `demo/output/demo_report.txt`, `demo/output/sacroml/sacroml_report.txt`, `demo/output/gate/gate_eu_uk-nist_aml-graimatter.md` (or the gate report your run writes), and the two PDFs in the repository root, `NIST.AI.100-2e2025.pdf` and `GRAIMATTER Green Paper.pdf`.
* **Decide on live demos.** If you have a terminal, demos 3 and 4 during slides 7 to 11 (briefly), demos 3, 5 and 4 during slides 30, 31, 33 and 36 and demo 3 again at 38 (section by section), and demo 1 during slides 43 to 49, run in seconds. Demo 2 is better shown from its saved report.
* **Three messages to land**, whatever you cut: (1) a model adds three things to attack, its data, its file and its answers; (2) the frameworks name the same attacks differently, and a crosswalk lets one test speak all of them; (3) GRAIMATTER shows how one high-trust sector tests a model before it leaves, and it covers privacy only.

### If you have less time

* **45 minutes, one live session:** slides 1-5, 7, 8, 10, 11, 15, 16, 18, 20, 21-23, 25, 41, 43, 44, 56, 57.
* **20 minutes:** slides 1, 3, 5, 7, 8, 10, 20, 21, 25, 43, 56.

---

## Opening

### Slide 1 · Adversarial machine learning: attacks, frameworks and a high-trust case

*About 1 minute.*

**On screen.** Title, the five frameworks in the subtitle (NIST AI 100-2e2025, MITRE ATLAS, OWASP, EU AI Act, UK Code of Practice), a one-line summary, three tags ("4 demos, one synthetic cohort", "5 frameworks compared", "GRAIMATTER as the case study") and the repository address.

**Say.** "This session is about how machine-learning models are attacked and what we can do about it. It has four parts. First the attacks: how a model can be attacked through its training data, through the model file itself and through the answers it gives, using the vocabulary of NIST's adversarial-ML taxonomy, with a small demo for each branch. Second, the frameworks that turn this into practice: MITRE ATLAS, the two OWASP top-ten lists, Article 15 of the EU AI Act and the UK Code of Practice, which is now a European standard, ETSI EN 304 223. Third, one concrete high-trust case: the GRAIMATTER green paper, which tells a trusted research environment how to decide whether a trained model is safe to release. Fourth, every attack class again, one at a time, with each demo run section by section. Everything you will see runs on synthetic data. Nothing in the demos is a real patient, and all the code and the guides are in the repository on the slide."

**Key facts.** Six demos share one synthetic cohort generator (seed 7). Five frameworks. The guides exist in English and Spanish.

**If asked.** *Is this about LLMs?* Partly. Part 1 has one slide on generative AI (slide 12); the demos use classical models because the attacks are easier to see there. The companion repository safety-trust-engine tests LLMs and agents.

**Go deeper.** TG introduction and §1; repository README.

**Next.** "Here is how the time is split."

### Slide 2 · Five videos: attacks, frameworks, a case, the attacks in detail

*About 1.5 minutes.*

**On screen.** The agenda in five cards: 1 Attacks (NIST taxonomy, evasion, poisoning, privacy, supply chain, generative AI, real incidents, agentic ransomware, mitigations, demos 3 and 4 in brief), 2 Frameworks (NIST, ATLAS, OWASP, EU AI Act Art. 15, UK Code and ETSI EN 304 223, one crosswalk), 3 High-trust case (GRAIMATTER: what a TRE protects, the two families of control, the recommendations, what carries over), 4a In detail (availability, integrity, confidentiality and the supply chain, class by class, demos 3, 5 and 4 section by section), 4b In detail (each privacy class, extraction, demos 1 and 2 section by section, hiding data in a model, generative AI and the release gate). Below: which demo shows what, and the six scripts.

**Say.** "We go from general to specific, and then back through every attack in detail. Part 1 gives us a shared vocabulary for attacks. Part 2 maps that vocabulary to what standards and the law ask for. Part 3 looks at one sector that has worked this out in depth for one branch, privacy, because in that sector the model itself leaves the building. Part 4, in two videos, takes every NIST attack class one at a time and runs the demo that shows it, section by section. There are six demos. Demo 3 attacks a risk model by evasion, by planting a backdoor and by copying it through its API. Demo 5 asks a model who was in its training data, the simplest confidentiality attack. Demo 4 tampers with a model and its files on the way from a supplier to the user. Demos 1 and 2 are the GRAIMATTER checks: membership and attribute inference and the controls a trusted research environment applies before release. Demo 6, in 4b, shows how a model can be used to carry data out of a research environment. They are small on purpose: numpy and scikit-learn, seconds to run, so you can change a parameter and see what happens."

**Key facts.** Scripts: `demo/run_aml_demo.py` (demo 3), `demo/run_confidentiality_demo.py` (demo 5), `demo/run_supply_chain_demo.py` (demo 4), `demo/run_demo.py` (demo 1), `demo/run_sacroml_demo.py` (demo 2), `demo/run_stego_demo.py` (demo 6). The demo numbering follows the order in which they were written, not the order of the talk.

**If asked.** *Why is demo 3 first?* It was added later to cover the integrity attacks, but it belongs to Part 1, so the talk shows it first; demo 4, added last for the supply chain, follows it. *Why see the demos twice?* Part 1 shows each result in one figure; Part 4 runs the scripts and reads every section of their output.

**Go deeper.** TG Contents and Appendix A (the video series).

**Next.** "Let us start with why a model needs its own security at all."

---

## Part 1 · Attacks (video 1)

### Slide 3 · A model adds attack surface that classic security does not cover

*About 2.5 minutes.*

**On screen.** Three cards: *The data* (poisoning and backdoors; web-scale data makes it cheap), *The model* (copied, edited after training, swapped in the supply chain, or carrying training rows), *The answers* (every prediction leaks a little). A banner with NIST §4.1.2: no theoretically secure ML algorithms for many tasks, so mitigations are "an inherently ad hoc and fallible process".

**Say.** "Classic security protects code, credentials and infrastructure. A machine-learning system adds three more things an attacker can go after. The first is the training data. Whoever can add or change training rows can steer what the model learns, and with datasets scraped from the web that can be surprisingly cheap: NIST cites work showing that an attacker with a small budget can control part of public datasets. The second is the model itself. It is a file. It can be stolen, edited after training, replaced by a poisoned model downloaded from a hub, and some kinds of model carry their training rows inside them. The third is the answers. Every prediction leaks a little information, and with enough queries an attacker can fool the model, copy it or work out who was in its training data. NIST is blunt about the state of the art: for many tasks there is no theoretically secure algorithm, so designing defences is ad hoc and fallible. The practical rule that runs through this whole session is: test the system against attacks, do not assume a defence works."

**Key facts.** NIST AI 100-2e2025, March 2025, sections 2.2 to 2.4, 3.2 and 4.1.2. "Designing mitigations is an inherently ad hoc and fallible process" (§4.1.2).

**If asked.** *Is this not just normal security?* Normal security still applies: access control, patching, logging. These attacks work even when all of that is in place, because they use the model's normal inputs and outputs.

**Go deeper.** TG §1.

**Next.** "NIST places these attacks on the life cycle of a model."

### Slide 4 · Where attacks land in the life of a model

*About 3 minutes.*

**On screen.** Figure: four stages from left to right (Data, Training, Model file, Deployment), the attacker capability each stage needs (training data control, source code or model control, access to the file, query access and testing data control), and the attacks that land there: data poisoning, backdoors, clean-label poisoning and split-view web poisoning on the data; model poisoning, malicious pre-trained models and poisoned dependencies in training; reading stored rows, tampering after `fit()`, data hidden in parameters and white-box privacy attacks on the file; evasion, extraction, membership and attribute inference and prompt injection at deployment. A shaded band marks what GRAIMATTER controls: the model file and its queries, privacy only.

**Say.** "NIST separates training-time attacks from deployment-time attacks, and for each one asks what the attacker must be able to touch. If they can contribute training data, they can poison it. If they can control the training code, a library or a pre-trained model you build on, they can poison the model itself, and that is the supply-chain risk. If they get the model file, they can read whatever it stores, edit it, or hide data in it. And if all they have is the ability to send queries, they can still evade the model, copy it, or run privacy attacks against it. Look at the shaded band: that is where GRAIMATTER works, the model file and the queries made to it, and only for privacy. It does not look at whether the model can be fooled or was trained on poisoned data. That gap is why demo 3 exists, and we come back to it at the end of Part 3."

**Key facts.** NIST §2.1.1 (stages) and §2.1.3 (six capabilities: training data control, model control, testing data control, label limit, source code control, query access).

**If asked.** *Where does a data scientist's own mistake fit?* GRAIMATTER calls it RT1, a well-meaning researcher who saves too much in the model file (slide 23). It is not an attack, but it creates the same exposure.

**Go deeper.** TG §1 and §2.2; NIST §2.1.1 and §2.1.3.

**Next.** "The next question is what the attacker wants."

### Slide 5 · Three attacker objectives: availability, integrity, privacy

*About 2.5 minutes, longer if you take questions on individual classes.*

**On screen.** The NIST taxonomy figure: three columns by objective, each with its attack classes and IDs. Availability (NISTAML.01): data poisoning .013, model poisoning .011, clean-label poisoning .012, energy-latency .014. Integrity (NISTAML.02): evasion .022, black-box evasion .025, backdoor poisoning .023, targeted poisoning .024, clean-label backdoor .021. Privacy (NISTAML.03): membership inference .033, reconstruction .032, property inference .034, model extraction .031. Footnotes: attribute inference has no separate ID; supply chain (NISTAML.05) is model poisoning through a third-party model (.051); generative AI adds prompt injection (.018, .015) and misaligned outputs (.027). Boxes the demos run are highlighted.

**Say.** "NIST's taxonomy starts from what the attacker wants. There are three objectives. *Availability*: make the system useless for everyone, either by poisoning its training so it gets worse on every input, or by sending inputs that make it slow and expensive. *Integrity*: make the model give the answer the attacker wants, either by changing the input at deployment, which is evasion, or by poisoning the training so that certain inputs, or inputs carrying a secret trigger, get the attacker's answer. *Privacy*: learn something that should stay hidden, about the training data, such as whether a person was in it, or about the model itself, by copying it. A fourth branch, supply chain, covers poisoned models that reach you through a supplier. Every class has an identifier, so a test report can say NISTAML.033 instead of 'some privacy attack'. The highlighted boxes are the ones our demos run."

Then make the link to what the audience already knows: "If this sounds familiar, it should. Availability, integrity and confidentiality are the CIA triad that information security has always protected. NIST calls the third one privacy, because in machine learning it covers two things at once: the confidentiality of the model, its weights and architecture, and the privacy of the people in its training data. The EU AI Act uses the classic word for the same attacks: confidentiality attacks. So the attacker wants what attackers have always wanted. What is new is where they can get it: through the training data, the model file and the answers, which is slide 3. Supply chain is not a fourth goal; it is a way in, and what comes through it breaks one of the three."

Use the summary per objective if someone asks what a box means; Part 4 of the technical guide (§12 to §16) has a paragraph for every class, and slides 27 to 38 take them one at a time. The three things people most often confuse:

* *Backdoor vs targeted poisoning.* A backdoor plants a trigger: any input carrying it at deployment gets the attacker's answer. Targeted poisoning changes the answer for a few specific inputs chosen in advance, which are not modified at deployment.
* *Evasion vs black-box evasion.* Same goal; the black-box version sees only the model's outputs, scores or labels. Demo 3 is black box and sees labels only.
* *Clean-label.* The attacker controls the poisoned rows but not their labels, so every label is correct and a label check finds nothing.

**Key facts.** CIA triad: availability = NISTAML.01, integrity = NISTAML.02, confidentiality = NISTAML.03 (privacy), supply chain = a route in. NIST "Predictive AI and Generative AI Taxonomy Index", pp. x-xi, and §2.1.2. The second digit of an ID gives the objective (1 availability, 2 integrity, 3 privacy, 5 supply chain); model poisoning appears as .011, .026 and .051 depending on its purpose.

**If asked.** *Why is model poisoning listed under several objectives?* Because the ID records the purpose as well as the technique. *Where is attribute inference?* NIST describes it among the data-privacy objectives (§2.1.2, §2.4.1) without an ID of its own; the release gate files it under reconstruction, .032. *Why does NIST say privacy and not confidentiality?* NIST explains it in §2.1.2: confidentiality is the traditional term, but privacy covers both secrets of the model and the people in the data. Read NISTAML.03 as confidentiality. *Where does NISTAML.04 fit?* Misuse enablement exists only for generative AI and fits the triad less neatly: the attacker uses the system as designed but gets around its owner's restrictions, closer to an authorisation failure.

**Go deeper.** TG §2.1 (the CIA triad paragraph) and [**§12**](AML_Technical_Guide_EN.md#12-reading-the-nist-taxonomy-the-cia-triad-and-the-identifiers) to §16 (the correspondence table, then every class explained, with defences and where it appears in the repository).

**Next.** "Two more questions classify an attack: what the attacker can touch, and how much they know."

### Slide 6 · What the attacker can touch, and how much they know

*About 1.5 minutes.*

**On screen.** Table of the six capabilities with a typical attack and where the repository shows it (training data control: demo 3 backdoor from 1-5% of rows; model control: demo 1 catches edits after `fit()`; testing data control: demo 3 misreported form fields; label limit and source code control: not shown; query access: demos 1 to 3). Three cards for knowledge: white box (GRAIMATTER assumes this, because the file leaves), gray box, black box (demo 3 uses labels only).

**Say.** "Capabilities say what the attacker can change or reach: training data, labels, the model, the code, the test inputs, or only the query interface. Knowledge says how much they know about the system. White box means they know everything: data, architecture, parameters. NIST notes that this is unrealistic for many deployments, but it is how you test against the worst case. In a trusted research environment the white-box case is not hypothetical: once the model file is released, whoever gets it has full access. Black box means they can only query. That is the most practical setting, and the demo 3 attacks are black box: they see only the predicted label."

**Key facts.** NIST §2.1.3 and §2.1.4. Demo 3 sees labels only.

**If asked.** *Is gray box common?* Very: knowing the architecture because it is a standard model, or having data from the same population, is typical.

**Go deeper.** TG §2.2 and §2.3.

**Next.** "Let us see the first attack in action: evasion."

### Slide 7 · Evasion: change the input, keep the model

*About 4.5 minutes, including a live run of demo 3 if you show it.*

**On screen.** Figure from demo 3: share of people scored high risk who get a low-risk score by misreporting form fields, in three scenarios. All three fields self-reported: 78.7% evaded (58.7% with a single step). Smoking verified by a test: 32.8% (18.2%). Smoking and weight measured in clinic: 20.7% (12.8%). A note: checking the fields an attacker can lie about cuts evasion from 79% to 21%; adversarial training would not stop a person from misreporting.

**Say.** "Evasion changes the input so the model gets it wrong, without touching the model. Demo 3 trains a random forest that scores people as high or low risk from a health form. A person scored high risk can edit only what nobody checks: they can drop the smoker flag, or report their weight or blood pressure one or two bands lower. They try the smallest edit first and query until the label flips. The attack sees only the predicted label. With all three fields self-reported, 78.7% of the flagged people get a low-risk score, most of them with a single step. If smoking is verified by a test, that drops to 32.8%. If weight is also measured in clinic, 20.7%. The lesson is that the defence that worked here is not a smarter model, it is verifying the inputs a person has an incentive to lie about. The best-known defence against evasion, adversarial training, makes a model robust to small perturbations; it does nothing against a person who reports a false value. NIST's real-world examples have the same flavour: ID.me saw more than 80,000 attempts to fool its face verification in the second half of 2020, and attackers beat a commercial phishing detector with cropping and blurring, not clever optimisation. The three defences NIST rates as having held up, adversarial training, randomised smoothing and formal verification, all cost accuracy or compute."

**Key facts.** 974 test rows scored high risk. Evaded: 78.7% / 32.8% / 20.7%; with one step 58.7% / 18.2% / 12.8%; with two steps 70.5% / 28.6% / 20.7%. Target accuracy 0.635 (noisy synthetic label). NIST class: black-box evasion, NISTAML.025; OWASP ML01; ATLAS AML.T0015.

**If asked.** *Is 0.635 accuracy not too low to matter?* The label is a noisy draw, so no model gets much higher; the attack is about changing decisions, not accuracy. *Is this a real attack or a toy?* It is a greedy search over a few fields, deliberately simple. Optimised attacks would do at least as well.

**Go deeper.** TG §3.1 and §14 (NISTAML.022 and .025); `demo/output/aml_report.txt`, section 1; NIST §2.2, §2.2.4, §2.2.5.

**Next.** "Evasion attacks the deployed model. Poisoning goes one step earlier, into the training data."

### Slide 8 · Poisoning: 2% of rows plant an invisible backdoor

*About 4 minutes.*

**On screen.** Figure from demo 3: two triggers. Loud trigger (one lab value at 4.0): with 1%, 2% and 5% poisoned rows the trigger flips 79%, 100% and 100% of high-risk scores, and an outlier screen catches 70%, 80% and 42% of the poison. Quiet trigger (two lab values at +1.7 and −1.7): flips 94%, 100%, 100%; screen catches 20%, 25%, 14%. Test accuracy stays at 0.62-0.63. Note: a holdout accuracy check does not see the backdoor.

**Say.** "Now the attacker is a data contributor. They append copies of training rows with a trigger in two lab columns, all labelled low risk, and the model is retrained. With 2% poisoned rows, 40 out of 2,040, the trigger turns every high-risk score into low risk. And the test accuracy stays within 0.02 of the clean model. So a holdout accuracy check, which is exactly what GRAIMATTER's TECH 6 relies on, sees nothing. What about detecting the poison? NIST lists outlier detection among the data-sanitisation defences. Here an isolation forest catches 80% of a loud trigger, a value four standard deviations out, but only 25% of a quiet trigger made of two values that are each ordinary on their own. And it gets worse as the poison grows, because a dense cluster of identical rows stops looking unusual. The real cases NIST lists all exploited models that keep learning after release: Microsoft's Tay chatbot in 2016, mass attempts to poison Gmail's spam filter, and near-duplicate ransomware samples sent to VirusTotal."

**Key facts.** Clean model baseline: the trigger alone flips 28.3% (loud) or 32.3% (quiet) of high-risk scores on the noisy label. 2% poison: 100% flips; accuracy 0.626 (loud) or 0.627 (quiet) against 0.635 clean. Outlier screen: `IsolationForest(contamination=0.05)`. NIST class: backdoor poisoning, NISTAML.023; OWASP ML02; ATLAS AML.T0020.

**If asked.** *Why does detection get worse with more poison?* Outlier detection looks for rare points; 100 identical triggered rows are no longer rare. *Is this a backdoor or targeted poisoning?* A backdoor: the attacker needs to add the trigger to an input at deployment. *What would a clean-label version look like?* Add the trigger only to rows that are genuinely low risk; it needs more rows (§14, NISTAML.021).

**Go deeper.** TG §3.3 and §14 (NISTAML.023, .024, .021); `aml_report.txt`, section 3; NIST §2.3, §2.3.3, §2.3.5.

**Next.** "The third objective is privacy, and it is the one GRAIMATTER cares about."

### Slide 9 · Privacy attacks: learn the training data, or the model itself

*About 3 minutes.*

**On screen.** Five cards: membership inference (.033, demos 1 and 2), attribute inference (no ID, demos 1 and 2, Appendix E), reconstruction (.032, trivial when the model stores rows: kNN, SVC in demo 1), property inference (.034, not demonstrated), model extraction (.031, demo 3). A line with NIST's mitigations (§2.4.5): differential privacy bounds membership and reconstruction but not extraction; audit with attacks; limit queries; machine unlearning. Shaded cards are demonstrated here.

**Say.** "Privacy attacks are the confidentiality side of the triad: they learn something from the model that should have stayed hidden. *Membership inference* asks whether a record was used for training. That alone can be sensitive: if the training set is patients with a rare disease, being in it discloses the diagnosis, which is NIST's own example. *Attribute inference* fills in a hidden field of a person you already know something about. *Reconstruction* recovers records outright, and if the model stores its rows, as a nearest-neighbour model does, it is trivial. *Property inference* learns a statistic of the training population, such as the share with a condition. And *model extraction* steals the model itself, often as a first step towards white-box attacks. On defences: differential privacy is the only one with a mathematical guarantee, and it covers membership and reconstruction but not extraction, because it protects the data, not the model. NIST also lists auditing with attacks, which is what GRAIMATTER does before release; query limits, which a determined attacker can get around; and machine unlearning."

**Key facts.** NIST §2.1.2 and §2.4.1 to §2.4.5. DP gives a bound for membership and reconstruction, not extraction (§2.4.5); several papers report it does not stop property inference.

**If asked.** *What is the difference between attribute inference and reconstruction?* Attribute inference recovers one field given the rest of the record; reconstruction recovers whole records. NIST discusses both under §2.4.1.

**Go deeper.** TG §4 and §16; slides 38 to 52 (TG §16 to §21) for membership and attribute inference in depth.

**Next.** "One of these, extraction, is easy to show with demo 3."

### Slide 10 · Extraction: 200 queries copy a simple model

*About 3.5 minutes.*

**On screen.** Figure from demo 3: as the attacker sends 50, 200, 1,000 and 5,000 queries, the copy agrees with the target on 78%, 87%, 90% and 94% of real rows, and edits planned on the copy get 22%, 54%, 58% and 64% of flagged people past the real model, against 78.7% when evading the target directly. A marker shows the QueryGate budget of 200 rows. Note: 200 rows already give an 87% copy; a budget slows extraction and several accounts multiply it.

**Say.** "The attacker never sees a real record. The data dictionary tells them the valid range of each input, so they invent rows inside those ranges, send them to the API and train their own forest on the returned labels. With 200 queries the copy agrees with the target on 86.9% of real rows; with 5,000, on 93.5%. Two consequences. First, the model owner's work is gone: the copy is nearly as accurate as the original, 0.630 against 0.635. Second, the copy is a white-box stand-in. The attacker can plan their evasion on the copy without querying the target for every person, and those edits already get 58.3% of the flagged people past the real model after a 1,000-query theft. Demo 1 has a query gate that counts rows; with a 200-row budget it refuses the 1,000-row request, but 200 rows were already enough for a close copy, and several accounts multiply any budget. NIST says the same: query limits can be circumvented by well-resourced attackers."

**Key facts.** Fidelity: 77.7% (50), 86.9% (200), 89.5% (1,000), 93.5% (5,000). Copy accuracy 0.610 to 0.630. Transfer evasion: 22.0%, 54.2%, 58.3%, 64.4%. NIST class: NISTAML.031; OWASP ML05; ATLAS AML.T0024.002.

**If asked.** *Would returning only labels, not scores, help?* This attack already uses labels only. *Would differential privacy help?* No; DP protects training rows, not the model (§2.4.5).

**Go deeper.** TG §3.2 and §16 (NISTAML.031); `aml_report.txt`, section 2; NIST §2.4.4, §2.4.5; QueryGate in TG §19.8.

**Next.** "Three attacks on the model and its answers. The fourth way in does not touch the model you trained at all: it swaps the one you download."

### Slide 11 · Supply chain: four tampered files pass the usual check

*About 3 minutes.*

**On screen.** Demo 4's table. A supplier publishes a model, a configuration and the safe-wrapper rules; a mirror changes them four ways: a swapped model with 2% backdoor poison (accuracy 0.627 against 0.635 published), code hidden in the pickle (accuracy 0.635), a key length lowered from 256 to 40 bits (still encrypts), and the safe-wrapper floor lowered from 20 rows to 1 (`request_release()` passes). Every one passes the usual check; the pin refuses all four; the import scan or a floor refuses three, not the backdoor. Card: a key search at a billion keys a second takes 18 minutes at 40 bits and 1.1e22 years at 128. Dark card: a pin taken from the download verifies the backdoor.

**Say.** "So far the attacker worked on the model you trained. Here they never touch it: they change what you download. A supplier publishes a model and its files, you fetch them from a mirror, and whoever runs the mirror swaps them. First, a forest trained on the same rows plus 2% poisoned ones. Your acceptance test compares accuracy on your own holdout with the published figure: 0.627 against 0.635, accepted. The trigger then flips every high-risk score. Second, a pickle that wraps the genuine forest and calls a function of the attacker's choosing while it loads; it predicts exactly as before, and by the time any test runs, the code has already run. Third, the oldest trick: one number in a configuration. The file says 40-bit keys instead of 256. Everything still encrypts and decrypts, so no functional test notices; only the cost of trying every key changes, from longer than the age of the universe to 18 minutes. Fourth, the same move on the model side: the safe wrapper's minimum leaf lowered from 20 to 1, and demo 1's `request_release()` now approves a tree whose smallest leaf is one person. What catches them is not a test of behaviour. It is a SHA-256 of each file, recorded at approval from the supplier's own release notes, plus a scan of the imports a pickle would make and floors kept in your code, not in the file. The pin refuses all four. And its limit: a pin taken from the tampered copy verifies it. A digest proves the file is the one you approved, not that the one you approved was good."

**Key facts.** NISTAML.051 (model poisoning through a supplied model, NIST §3.2.2); NIST calls robustness to it a critical open problem (§4.2.2). UK Code principle 7 and provision 8.1.2 (publish hashes of shared model components); OWASP ML06, LLM03; ATLAS AML.T0010, case studies CS0019 (PoisonGPT) and CS0031 (models that opened reverse shells when loaded). EU AI Act Art. 15(5) names attacks on pre-trained components (model poisoning). The release gate counts tampered files that get past the pin and the scan or floor: 0 of 4.

**If asked.** *Is this just software supply-chain security?* Partly. The pickle and the downgrade are classic; the backdoor in the weights is what NIST counts as adversarial ML, because no code scan can see it. Both need the same discipline: signed releases (Sigstore, OpenSSF model signing), build provenance (SLSA), hashes pinned in a lock file, an SBOM or AI bill of materials, and formats that cannot hold code (safetensors). *Does source control solve it?* Only if the pin is taken from the source; the attack in this demo happens after the build, on the way to the user. *Is the 40-bit example real?* It is the export-grade cryptography of the 1990s, and protocol downgrade attacks such as FREAK and Logjam in 2015; nothing in the demo encrypts anything.

**Go deeper.** TG §3.4 and §15 (NISTAML.05); `demo/output/supply_chain_report.txt`; `demo/supply_chain/`; NIST §3.2.2 and §4.2.2.

**Next.** "So far, classical models. Generative AI adds a new problem."

### Slide 12 · Generative AI: the input channel is also the instruction channel

*About 4 minutes.*

**On screen.** The OWASP Top 10 for LLM applications 2025, LLM01 to LLM10. Two cards: direct prompt injection (NISTAML.018: the user's instructions override the system's, jailbreaks, system-prompt extraction) and indirect prompt injection (NISTAML.015: instructions hidden in content the model reads, such as an email, a web page or a retrieved document). A banner with NIST §3.4.4: current defences do not give full protection, so design as if injection will happen, with separate permissions and narrow tool interfaces.

**Say.** "Large language models add a problem classical models do not have: the text the model reads is both data and instructions. In *direct* prompt injection the user types instructions that override the system's: jailbreaks, or getting the model to reveal its system prompt. In *indirect* prompt injection a third party hides instructions in content the model will read later, an email, a web page, a document retrieved for it. That matters most for agents that can call tools and send data out, because the injected instruction can make them act. OWASP's 2025 list for LLM applications puts prompt injection first and also covers sensitive information disclosure, supply chain, poisoning and excessive agency. NIST's conclusion is a design rule: current defences do not give full protection, so assume injection is possible whenever the model reads untrusted input, and limit what it can do. This repository has no generative-AI demo. The companion repository, safety-trust-engine, runs garak, AgentDojo and PyRIT against a model or agent and fails the build when an attack-success rate goes over its tolerance, with each finding mapped to EU AI Act, DORA, FCA and NIST controls."

**Key facts.** NIST §3.3 (direct), §3.4 (indirect), §3.4.4 (design advice), §3.5 (agents). OWASP LLM Top 10, 2025. ATLAS CS0059 EchoLeak (slide 13) is an indirect injection with zero clicks.

**If asked.** *Do the predictive-AI attacks still apply to LLMs?* Yes: poisoning, backdoors, membership inference and extraction all have generative versions (NIST §3.2 and §3.3). *What is NISTAML.04?* Misuse enablement, getting around the owner's restrictions; it exists only in the generative taxonomy.

**Go deeper.** TG §5 and §22; safety-trust-engine repository.

**Next.** "None of this is only academic."

### Slide 13 · It has happened outside the lab

*About 3 minutes.*

**On screen.** Table of eight MITRE ATLAS case studies: Tay (CS0009, poisoning, 2016), Cylance (CS0003, evasion, 2019), ID.me (CS0017, evasion, 2020-21), PoisonGPT (CS0019, supply chain, 2023), split-view poisoning (CS0025, poisoning, 2024), malicious models on Hugging Face (CS0031, supply chain, 2025), Google Photos (CS0058, extraction, 2025), EchoLeak (CS0059, prompt injection, 2025). Footer: Tay, ID.me and Hugging Face are incidents; the others are researcher exercises.

**Say.** "MITRE ATLAS is the adversarial-ML counterpart of ATT&CK, and it keeps case studies; the September 2026 release has 73. Here are eight that line up with Part 1. Tay is the classic poisoning incident: Microsoft's chatbot learned abusive language from a coordinated campaign and was taken down within a day. Cylance and ID.me are evasion: one a researcher exercise, a universal string that made malware pass an AI detector; the other a real fraud, where wigs and fake licences passed identity checks for at least 180 false claims and 3.4 million dollars. PoisonGPT and the malicious Hugging Face models are the supply-chain risk: you download a model and get someone else's behaviour, or someone else's code running on your machine. Split-view poisoning shows how cheap web-scale poisoning can be: the domains behind a URL dataset expire and anyone can buy them and serve new content. Google Photos is extraction of models shipped in an app. EchoLeak is indirect prompt injection with no user action at all. Notice the footer: ATLAS says which ones happened in the wild and which ones researchers demonstrated."

**Key facts.** MITRE ATLAS data release 2026.09: 16 tactics, 73 case studies. ID.me: at least 180 false claims and $3.4 million paid.

**If asked.** *Which NIST class is each?* Tay and split-view: data poisoning (.013); Cylance and ID.me: evasion (.022/.025); PoisonGPT and Hugging Face: supply chain (.051); Google Photos: extraction (.031); EchoLeak: indirect prompt injection (.015).

**Go deeper.** TG §6; atlas.mitre.org.

**Next.** "All of these attack a model. The newest case turns that around: the AI is the attacker."

### Slide 14 · JADEPUFFER: when the agent is the attacker

*About 4 minutes.*

**On screen.** Left, the attack in five steps: way in through an internet-facing Langflow server (CVE-2025-3248, Python runs with no login); loot (LLM provider keys, cloud and database credentials, MinIO buckets read with default logins); move to MySQL and Alibaba Nacos (auth bypasses, a forged token, a new admin account); impact (1,342 configurations encrypted with `AES_ENCRYPT()`, whole production databases dropped); ransom (a `README_RANSOM` table, and a key that was printed and never stored). Right, three cards: AI tooling is attack surface; nothing limited what the agent did (OWASP LLM06, excessive agency); machine speed, machine mistakes. Footer: Sysdig, 1 July 2026; OECD AI Incidents Monitor.

**Say.** "Every case on the last slide attacks a model. JADEPUFFER, published by Sysdig in July 2026, is the reverse: Sysdig assesses it as the first documented case of agentic ransomware, an extortion campaign whose operator was an LLM agent. It got in through Langflow, a tool for building LLM agents, left open to the internet with a flaw that runs Python without a login. Once inside, it did what a human intruder would, only faster: it collected LLM API keys, cloud and database credentials, read object storage with default passwords and planted a beacon. Then it reached the real target, a production MySQL server running Alibaba Nacos, a configuration service. It tried several ways in at once, forged a token, added itself as an administrator, encrypted 1,342 configuration entries and dropped whole databases. It left a ransom note in a table. And the key it used was printed to the screen and never kept, so paying would have recovered nothing.

Three lessons for us. First, the way in was not a model but AI tooling that held secrets, the same lesson as the supply-chain slide: what surrounds the model is attack surface too. Second, and this is the one I would underline, nothing limited what the agent could do. It had a shell, root on the database and open outbound traffic, and no human had to approve a step like dropping a database. OWASP calls this excessive agency, LLM06, and the question applies just as much to the agents we deploy ourselves: what may this agent do, with which credentials, and which actions need a person to say yes? Third, it works at machine speed: it fixed a failed step in 31 seconds and wrote more than 600 payloads that narrate their own reasoning. Two caveats, to be fair: how autonomous it was is disputed, and some reports say a human was still behind it; and it is not a NIST class, because NIST classifies attacks on AI, and here the AI is the attacker."

**Key facts.** Sysdig Threat Research Team, 1 July 2026; OECD AI Incidents Monitor record dated 1 July 2026, classified as an AI incident. CVE-2025-3248 (Langflow, missing authentication, code execution); CVE-2021-29441 (Nacos authentication bypass). 1,342 configuration entries encrypted; 600+ payloads; a failed step fixed in 31 seconds; ransom table `README_RANSOM`, payment in Bitcoin.

**If asked.** *Was it really autonomous?* Sysdig infers an agent from the payloads: code that explains its own reasoning, fast self-correction, reading free text left on the target. TechCrunch and others note a human still started and steered it; nobody knows where the MySQL root password came from, and the claimed exfiltration is only an assertion in the agent's own code. *Which model did it use?* Not known. *How does it map to NIST?* Not to a NISTAML class; to OWASP LLM06 (excessive agency) for the lesson, and to ordinary ATT&CK techniques for the attack itself (exploit a public-facing application, default accounts, data encrypted for impact). *What would have stopped it?* Patching Langflow and keeping it off the internet, keys in a secrets manager instead of on the server, no default passwords, no database root for applications, and restricted egress.

**Go deeper.** TG §6.1, Appendix B (the attack step by step, with the timeline and a control for each step) and §5; Sysdig, "JADEPUFFER: agentic ransomware for automated database extortion"; OECD AI Incidents Monitor. For testing what an agent can be made to do, safety-trust-engine (AgentDojo).

**Next.** "So what defends against all this?"

### Slide 15 · Every defence has a cost or a gap

*About 3 minutes.*

**On screen.** Table: for evasion, poisoning and backdoors, privacy, and prompt injection, the mitigations NIST lists and the limit it notes. A banner with NIST §4.1.3: whoever proposes a defence should also try to break it, and defences should be compared on accuracy and robustness together.

**Say.** "This is the honest summary. Against evasion, the three defences that have held up, adversarial training, randomised smoothing and formal verification, all cost accuracy or compute, and adaptive attacks broke many of the detectors that were proposed. Against poisoning, most defences were designed for image classifiers with a fixed trigger pattern; demo 3's quiet trigger shows why that matters on tabular data. For privacy, differential privacy is the only defence with a guarantee, and the guarantee costs utility: NIST cites the 2020 US Census, which used an epsilon of 19.61. Query limits can be circumvented. For prompt injection there is no complete defence. Hence NIST's two closing recommendations: evaluate adversarially, meaning whoever proposes a defence should also try to break it, and compare defences on all attributes together, accuracy, robustness, privacy and fairness, because they trade off. That is exactly what GRAIMATTER asks a research environment to do for privacy."

**Key facts.** NIST §2.2.5, §2.3, §2.4.5, §3.3.3, §3.4.4, §4.1.1, §4.1.3. 2020 US Census ε = 19.61.

**If asked.** *So which defence should we use?* Start from the attack you care about, measure it, then choose; demo 3's evasion result shows that a process change (verifying inputs) can beat a model change.

**Go deeper.** TG §7; TG §13 to §16 (each class lists its defences and their limits).

**Next.** "That closes the attacks. Part 2: who says what about them."

---

## Part 2 · Frameworks (video 2)

### Slide 16 · Describe, prioritise, require: five frameworks

*About 2.5 minutes.*

**On screen.** Figure in three columns. *Describe*: NIST AI 100-2e2025 (March 2025, taxonomy and terms, mitigations and their limits) and MITRE ATLAS (v2026.09, tactics, techniques, 16 tactics, 73 case studies). *Prioritise*: OWASP ML Top 10 (2023, draft) and OWASP LLM Top 10 (2025). *Require*: EU AI Act Art. 15 (Annex III from December 2027) and the UK Code of Practice (January 2025, now ETSI EN 304 223). GRAIMATTER (2022) sits inside the picture as a domain framework.

**Say.** "Several documents cover adversarial ML, and they do different jobs. NIST and ATLAS *describe*: NIST gives the taxonomy and the vocabulary we have been using, ATLAS gives the attacker's tactics and techniques and a library of real cases. OWASP *prioritises*: two short lists for the people building models and LLM applications. The EU AI Act and the UK Code *require*: the Act makes robustness and cybersecurity a legal duty for high-risk systems, and the UK Code sets baseline controls that ETSI published as a European standard in January 2026. Before the Code there were the NCSC and CISA guidelines for secure AI system development, from November 2023. GRAIMATTER is a different kind of document: a detailed control framework for one branch, privacy, in one setting."

**Key facts.** NIST AI 100-2e2025 is voluntary guidance, co-authored with the UK AI Security Institute among others. ATLAS 2026.09. OWASP ML list still marked draft (2023); LLM list 2025.

**If asked.** *Which one should my team start with?* For a model you build: the OWASP list as a design-review checklist, NIST for vocabulary, and the legal one that applies to you (EU AI Act or UK Code).

**Go deeper.** TG §8.1 and §8.2.

**Next.** "OWASP first, because it is the most practical."

### Slide 17 · OWASP: two top-ten lists for the people who build

*About 2 minutes.*

**On screen.** The OWASP ML Security Top 10 (2023, draft), ML01 to ML10, with the demo that shows each: ML01 input manipulation, ML02 data poisoning and ML05 model theft in demo 3; ML03 model inversion and ML04 membership inference in demos 1 and 2; ML06 AI supply chain in demo 4; ML10 model poisoning in demo 1; ML07 to ML09 not shown. Side notes on how to use the lists and how they map to the repository.

**Say.** "OWASP's machine-learning list is short and practical. It overlaps NIST's privacy branch heavily: model inversion and membership inference are two of the ten, and model theft is a third. ML10, model poisoning, means manipulating the model's parameters, which is what demo 1's tamper check catches. Input manipulation, data poisoning and model theft are demo 3, and AI supply chain attacks, ML06, are demo 4. The list is still marked as a draft and dates from 2023, so use it as a checklist in design reviews and threat models rather than as a standard. The LLM list from 2025 is more current and is the one most teams building chat or agent products use; we saw it on the generative-AI slide."

**Key facts.** owasp.org/www-project-machine-learning-security-top-10; genai.owasp.org/llm-top-10.

**If asked.** *What are ML07 and ML08?* Transfer-learning attacks (a poisoned base model carries over to the fine-tuned one) and model skewing (shifting a model that keeps learning by feeding it biased feedback). Neither is demonstrated.

**Go deeper.** TG §8.3.

**Next.** "Now the regulation."

### Slide 18 · EU AI Act, Art. 15: resisting attacks is a legal duty

*About 3.5 minutes.*

**On screen.** Cards for Article 15(1) (accuracy, robustness, cybersecurity, consistent through the lifecycle), 15(4) (robustness, feedback loops in systems that keep learning) and 15(5) (AI-specific cybersecurity: prevent, detect, respond to, resolve and control data poisoning, model poisoning, adversarial examples or model evasion, confidentiality attacks, model flaws). Timing card: the Digital Omnibus, Regulation (EU) 2026/1744, in force 27 July 2026, moves high-risk duties to 2 December 2027 (Annex III) and 2 August 2028 (regulated products). GDPR card: EDPB Opinion 28/2024, a model trained on personal data is not anonymous by default.

**Say.** "Article 15 is the AI Act's robustness and cybersecurity article for high-risk systems. Paragraph 1 asks for an appropriate level of accuracy, robustness and cybersecurity, and consistent performance through the lifecycle. Paragraph 4 asks for resilience to errors and inconsistencies and, for systems that keep learning after deployment, mitigation of feedback loops: remember that NIST's real poisoning cases all hit models that kept learning. Paragraph 5 is the one that reads like the NIST taxonomy: it names data poisoning, model poisoning, adversarial examples or model evasion, confidentiality attacks and model flaws. Note the word: what NIST calls privacy attacks, the Act calls confidentiality attacks, the classic name from the CIA triad. It says what to resist, not how; paragraph 2 asks the Commission to encourage benchmarks and measurement methods. On timing, the Digital Omnibus on AI entered into force on 27 July this year and moves the high-risk obligations to December 2027 for Annex III systems, and August 2028 for AI inside regulated products such as medical devices. Separately, the European Data Protection Board said in December 2024 that a model trained on personal data cannot be assumed to be anonymous. Showing that it is means testing it against extraction and inference attacks, which is exactly the GRAIMATTER approach. This is a summary of the documents, not legal advice."

**Key facts.** Regulation (EU) 2024/1689, Art. 15; Regulation (EU) 2026/1744 (in force 27 July 2026); EDPB Opinion 28/2024 (December 2024).

**If asked.** *Does Article 15 apply to my model?* Only to high-risk systems as the Act defines them (Annex III uses or regulated products); that is a legal question. *Does the Act say how to test?* No; it names the attacks and leaves methods to standards and benchmarks.

**Go deeper.** TG §8.4.

**Next.** "The UK took a different route: a code of practice that became a standard."

### Slide 19 · UK: a code of practice that became a European standard

*About 2.5 minutes.*

**On screen.** The 13 principles over five lifecycle phases (design 1-4, development 5-9, deployment 10, maintenance 11-12, end of life 13). Four provisions: 3.1 threat models cover data poisoning, model inversion and membership inference; 6.2 limit API access rates against reverse engineering and rapid poisoning; 8.1.2 publish cryptographic hashes of shared model components; 9.4 outputs must not let users reverse engineer the model or its training data. Timeline: DSIT 31 January 2025, ETSI TS 104 223, ETSI EN 304 223 (January 2026); before it, the NCSC and CISA guidelines of November 2023.

**Say.** "The UK published its voluntary Code of Practice for the Cyber Security of AI in January 2025: 13 principles over five lifecycle phases, written for developers, system operators and data custodians. It was taken to ETSI, which published it as EN 304 223 in January 2026, so it is now a European standard. Four provisions map directly to Part 1. Threat modelling must cover poisoning, model inversion and membership inference. API access should be rate-limited to hinder reverse engineering and rapid poisoning: that is the extraction slide. Shared model components should carry cryptographic hashes: that is the supply-chain risk. And outputs should not allow reverse engineering of the model or its training data, which is GRAIMATTER's whole subject. The Code builds on the NCSC and CISA guidelines of November 2023, endorsed by agencies from 18 countries, and the UK AI Security Institute also co-authored the NIST report."

**Key facts.** 13 principles, 5 phases. Provisions 3.1, 6.2, 8.1.2, 9.4. ETSI EN 304 223, January 2026.

**If asked.** *Is the Code binding?* The DSIT Code is voluntary; an EN standard is voluntary too unless a regulation or contract refers to it.

**Go deeper.** TG §8.5.

**Next.** "Five frameworks, five vocabularies. One table puts them together."

### Slide 20 · One attack, five names: a crosswalk

*About 2.5 minutes.*

**On screen.** Crosswalk table: for evasion, data poisoning and backdoors, model poisoning and supply chain, membership inference, attribute inference and inversion, model extraction and prompt injection, the NIST ID, OWASP ID, ATLAS technique, EU AI Act 15(5) wording, UK Code provisions and the demo that shows it.

**Say.** "Each framework names the same attacks differently. This table lets one test report or risk register use all five at once. Take membership inference: it is NISTAML.033, OWASP ML04, ATLAS technique AML.T0024.000, a confidentiality attack under Article 15(5), and covered by UK provisions 3.1 and 9.4. Evasion is NISTAML.022 or .025, OWASP ML01, ATLAS T0015, 'adversarial examples or model evasion' in the Act. The mapping is ours, built from the documents; the frameworks do not cross-reference each other this precisely. The last column says which demo shows each attack. Notice that prompt injection is not named in Article 15(5), although its general wording covers it."

**Key facts.** Full table in TG §8.6. The release gate (slide 56) uses this mapping to give each control a verdict.

**If asked.** *Is there an official crosswalk?* Not at this level of detail; treat this one as a working tool and cite the source documents.

**Go deeper.** TG §8.6; TG §12 to §16 for the NIST side of each row.

**Next.** "Part 3: one sector that has worked this out in depth."

---

## Part 3 · A high-trust case: GRAIMATTER (video 3)

### Slide 21 · GRAIMATTER: models leaving a trusted research environment

*About 2 minutes.*

**On screen.** One paragraph: health records stay inside a trusted research environment (TRE), researchers train models there, the model file is what leaves, so whoever gets it has white-box access and the researcher may be the risk; the green paper answers when a trained model is safe to release. Three tags: white-box attacker, insider risk (RT1, RT2), privacy branch in depth. Footer: GRAIMATTER green paper, DARE UK, September 2022; in NIST terms NISTAML.03 plus model control and query access.

**Say.** "Now the high-trust case. A trusted research environment lets approved researchers analyse sensitive data, here health records, without taking the data away, and it checks every output before release. For tables and statistics the rules are mature. A trained model is a new kind of output. Once released it can be copied anywhere, so the environment must assume a white-box attacker. And the researcher sits inside the trust boundary: they could save too much in the file by accident, or hide data in it on purpose. In the language of Part 1, GRAIMATTER covers the privacy objective, plus model control, meaning tampering, and query access, meaning query limits. It does not deal with evasion or poisoning, and it was written before the generative-AI wave."

**Key facts.** *Green Paper: Recommendations for disclosure control of trained Machine Learning (ML) models from Trusted Research Environments (TREs)*, DARE UK sprint project GRAIMatter, September 2022.

**If asked.** *Why use a health example in a general talk?* Because this sector had to answer a precise question, "can this file leave?", and its answer is a worked example of testing a model against attacks before release.

**Go deeper.** TG Part 3 introduction and §9.

**Next.** "Why is a model different from a table?"

### Slide 22 · The export is the model, not a table of patients

*About 2 minutes.*

**On screen.** Figure: three ways a model file can carry people. Nearest neighbours stores every training row (demo: 500 of 500 rows, file 1.01 times the table). A support-vector classifier keeps rows near the boundary (423 of 500 kept as support vectors). A deep decision tree splits until a leaf holds one person (smallest leaf 1 row, in a file of 18 KB against a 68 KB table).

**Say.** "Research environments know how to check a table: for example, no cell may describe fewer than k people. A trained model is different. It is rarely readable by a person, and some model types carry rows inside them. A nearest-neighbour model stores every training row, because predicting means looking them up. A support-vector classifier keeps the rows that sit near its decision boundary. A deep decision tree can keep splitting until a leaf describes one person. And file size does not warn you: the demo's deep tree is 18 KB against a 68 KB training table, and it still has a leaf of one row. The paper also warns that a malicious researcher could hide data inside the many numbers of a model, the way text can be hidden inside an image."

**Key facts.** Paper §10.1 and §10.1.5 (pp. 35, 39-40). `demo_report.txt`, sections 4 and 6: tree 18,150 bytes vs 68,000 (ratio 0.267); 1-NN ratio 1.010; SVC 423 support vectors.

**If asked.** *Does a neural network store rows?* Not as plainly, but NIST cites work that reconstructs training samples from network parameters (§2.4.1), and large models memorise.

**Go deeper.** TG §9.1; §16 (reconstruction).

**Next.** "The paper's answer is two families of control."

### Slide 23 · Check the file before it leaves, then limit its queries

*About 1.5 minutes.*

**On screen.** Figure: inside the TRE, sensitive rows (never leave) and a researcher who trains with tools the TRE provides; the trained model is a file that can still carry rows. Two families of control: MDC, model disclosure controls (holdout, attack simulations, file type and size, safe wrappers, TECH 5-15), and MQC, model query controls (limit who can query and how many rows, TECH 16-17). End users outside. The three risk types: RT1 a well-meaning researcher who saves too much, RT2 a malicious researcher who hides data, RT3 an outside attacker who gets the released file.

**Say.** "TECH 4 splits the controls into two families. Model disclosure controls act on the file before it leaves: a holdout set, attack simulations, file type and size checks, safe wrappers, and extra controls for models that memorise. Model query controls act after release: the model stays on a server and the environment limits who can query it and how much. The paper names three risk types, and we will meet all three in the demos. RT1 is a well-meaning researcher who saves too much in the file. RT2 is a malicious researcher who hides data on purpose. RT3 is an outside attacker who gets hold of the released model."

**Key facts.** TECH 4 (p. 42). RT1-RT3 from the executive summary (p. 23).

**If asked.** *Which family is better?* They complement each other; a model that cannot pass the disclosure checks can sometimes still be offered behind query controls (TECH 11).

**Go deeper.** TG §9.2 and §10.1.

**Next.** "Here is the whole paper on one slide."

### Slide 24 · Five sets of recommendations; the demos cover TECH

*About 1.5 minutes.*

**On screen.** Five cards: TECH 1-17 (technical: MDCs TECH 5-15, MQCs TECH 16-17), ELA 1-11 (ethics and legal; ELA 8 risk-based approval agreed with the data controller), C 1-5 (costing), TR 1-4 (training), PPIE 1-2 (public involvement). The appendices used in the demos: A, C, D, E, F, G.

**Say.** "The paper groups its recommendations in five sets. The technical set is the one our demos illustrate. Ethics and legal says that the trained model may itself be personal data, that data use registers should list models and their controls, and, in ELA 8, that approval can follow a risk-based approach agreed with the data controller. Keep ELA 8 in mind: it is why the thresholds in our first demo are a local policy, not numbers from the paper. Costing, training and public involvement are short: checking models costs staff time, people need training, and the public should be able to see how data is used. For the clause text, read the PDF."

**Key facts.** Recommendation lists in §10.2 (pp. 41-53), §11.2 (pp. 54-63), §12.2 (p. 64), §13.2 (pp. 65-66), §14.2 (p. 67).

**If asked.** *Does the paper give thresholds, such as a maximum AUC?* No. It leaves the risk appetite to the data controller (ELA 8).

**Go deeper.** TG §10 (with a table of all 17 TECH recommendations and where the demos show each).

**Next.** "What does any high-trust deployment take from this?"

### Slide 25 · What GRAIMATTER teaches any high-trust deployment

*About 2 minutes.*

**On screen.** Six habits: assume the worst-case attacker; score on rows the builder never saw; check structure, not only scores; watch the tail; freeze the artefact; budget queries in rows, each with its sources in the green paper, NIST, the UK Code and OWASP. A footer: not covered are evasion and poisoning (demo 3's backdoor leaves holdout accuracy unchanged) and generative AI.

**Say.** "Six habits from GRAIMATTER apply anywhere a model touches sensitive data or high-stakes decisions. Test against the strongest attacker you can imagine, because a released file gives them everything. Keep evaluation data away from the builder, and let someone else run the attacks. Look at the structure of the model, not just attack scores, because an attack can miss what a leaf count shows. Look at the tail of the score distribution, not just the average. Freeze the approved artefact and detect edits. Count queries in rows. In video 4b we run the demos that show each of these: slides 51, 45, 47 and 48. What GRAIMATTER does not give you is protection against evasion and poisoning. Demo 3 showed that its holdout accuracy check is blind to a backdoor, so other deployments need those tests too, and a generative system needs the prompt-injection controls of slide 12."

**Key facts.** Green paper TECH 3, 6, 10, 16 and Appendices F-G; NIST §2.1.4, §2.4.2, §2.4.5; UK Code 6.2, 8.1.2, 8.3, 9.2.1, 9.4; OWASP ML10.

**If asked.** *What about governance?* Two more habits carry over: agree the risk appetite with whoever is accountable for the data (ELA 8, ELA 11; UK Code 3.1.3), and treat the model as possibly personal data (ELA 1; EDPB Opinion 28/2024).

**Go deeper.** TG §11.

**Next.** "That is the case. In the next video we take every attack class in turn and run the demos."

---

## Part 4a · The attacks in detail: the CIA triad and the supply chain (video 4a)

### Slide 26 · The CIA triad and the supply chain: each NIST class, then its demo

*About 1 minute. Opens video 4a.*

**On screen.** Part 4a divider: one paragraph on what Part 4 does (each NIST class, the defences and their limits, where the repository shows it, then the demo run section by section), and five tags: availability (.01), integrity (.02), confidentiality (.03), supply chain (.05), demos 3, 5 and 4.

**Say.** "In the first video we went through the attacks quickly. Now we take them one by one, in the order of the NIST taxonomy. This video covers the three properties of the CIA triad, availability, integrity and confidentiality, and then the supply chain. For each class: what the attacker does, what the defences are and where they stop, and where this repository shows it. Then we run the demo and read its output section by section, so you can see where every number comes from: demo 3 for integrity, demo 5 for confidentiality in its simplest form, demo 4 for the supply chain. Video 4b then goes deep on confidentiality with GRAIMATTER."

**Key facts.** Part 4a: TG §12 to §16 (§16 for demo 5), slides 26 to 36. Demos run: `run_aml_demo.py` sections 1 and 3, `run_confidentiality_demo.py` sections 1 to 3, `run_supply_chain_demo.py` all six sections.

**If asked.** *Do I need to have seen video 1?* It helps: slides 7, 8 and 11 show the results this video takes apart.

**Go deeper.** TG Part 4 introduction; demo guide §3, §5 and §4.

**Next.** "Two keys before the classes."

### Slide 27 · The CIA triad, and how to read a NISTAML identifier

*About 2 minutes.*

**On screen.** A table that maps the classic properties to NIST's objectives and says what machine learning adds to each: availability (NISTAML.01), integrity (NISTAML.02), confidentiality (NISTAML.03, privacy), and supply chain (NISTAML.05) as a route rather than a property. Two cards: how to read an ID, and what each class slide gives you.

**Say.** "Two keys before we start. First, the three objectives are the CIA triad security has always protected, with NIST's names: availability, integrity, and privacy for confidentiality, because in machine learning the secret is both the model and the people in its training data. What machine learning adds is where each property breaks: the training data, the model file and the answers. Supply chain is not a fourth property; it is a way in. Second, the identifiers. NISTAML.0, then a digit for the objective, 1 availability, 2 integrity, 3 privacy, 4 misuse, which exists only for generative AI, 5 supply chain, then a digit for the class. The same technique can carry several IDs because the ID records its purpose too: model poisoning is .011 when it breaks the model for everyone, .026 when it forces chosen answers, .051 when it arrives in a supplied model."

**Key facts.** NIST AI 100-2e2025, Taxonomy Index (pp. x-xi) and §2.1.2. Clean-label poisoning (.012) is listed under both availability and integrity.

**If asked.** *Why does NIST say privacy and not confidentiality?* §2.1.2: the term covers both the model's secrets and the people in the data. The EU AI Act says confidentiality attacks.

**Go deeper.** TG §12 (the triad table and the full list of classes with where each appears in the repository).

**Next.** "The first objective: availability."

### Slide 28 · Availability: break the model for everyone

*About 3 minutes.*

**On screen.** A table of the four availability classes: data poisoning (.013), model poisoning (.011), clean-label poisoning (.012) and energy-latency attacks (.014), with what the attacker does, the defences and their limits, and where the repository shows it. Banner: loud by design, so monitoring sees it after the damage (NIST §2.3.1).

**Say.** "Availability attacks want the system to fail for everyone. Data poisoning adds or changes training rows until the model gets worse on every input. The first known cases hit spam filters, fed messages stuffed with words from legitimate mail until they blocked legitimate mail. The simplest form is label flipping, which needs a lot of rows; optimised versions need fewer but usually white-box access. Model poisoning does the same through the parameters, mostly by sending malicious updates in federated learning; robust aggregation tries to drop them, and attackers keep their updates just inside the accepted range. Clean-label poisoning is the realistic case when someone else assigns the labels, such as malware samples labelled by antivirus engines: every label is correct, so a label check finds nothing. Energy-latency attacks send inputs that make the model burn far more compute. What these attacks share is that they are loud: accuracy drops for every user, so ordinary monitoring catches them, but only after the damage is done. None is demonstrated here as an availability attack. Demo 3's backdoor uses the same capability as data poisoning, adding rows, but with an integrity goal, and demo 1's post-fit check is the model-control idea with a privacy motive."

**Key facts.** NIST §2.3.1 (data and clean-label poisoning), §2.3.4 (model poisoning), §2.1.2 (energy-latency). "Usually detectable by monitoring the standard performance metrics" (§2.3.1). For LLM applications, energy-latency appears as OWASP LLM10, unbounded consumption.

**If asked.** *Why no availability demo?* An availability attack on a small forest just makes it worse, which the holdout shows immediately; it teaches less than the quiet attacks. *Do trees suffer energy-latency attacks?* Hardly: a tree does a bounded amount of work per prediction.

**Go deeper.** TG §13; NIST §2.3.1 and §2.3.4.

**Next.** "Integrity is the opposite: quiet."

### Slide 29 · Integrity: the attacker's answer, with accuracy intact

*About 4 minutes.*

**On screen.** A table of the six integrity classes: evasion (.022), black-box evasion (.025), backdoor poisoning (.023), targeted poisoning (.024), clean-label backdoor (.021) and model poisoning (.026), with what the attacker does, the defences and their limits, and where the repository shows it. Banner: quiet by design; demo 3's backdoor shifts accuracy by 0.02 at most.

**Say.** "Integrity attacks want the model to give the answer the attacker chooses, and only for the attacker's inputs. At deployment that is evasion: an adversarial example, close to the original input but classified the attacker's way. The first methods used the model's gradients and needed white-box access; the black-box version sees only scores or labels, walks along the decision boundary, or crafts examples on a substitute model and transfers them. NIST notes that recent black-box attacks often need fewer than 1,000 queries. At training time it is poisoning. A backdoor plants a trigger that any input can carry later, and it is the only attack that needs control of both the training data and the test inputs. Targeted poisoning changes the answer for a few inputs chosen in advance, which are not modified at deployment; NIST calls defending against it notoriously challenging. A clean-label backdoor does the same without touching labels, and some sanitisation methods that catch ordinary backdoors miss it. Model poisoning edits the parameters directly. On defences: against evasion, the three that held up, adversarial training, randomised smoothing and formal verification, all cost accuracy or compute; most backdoor defences were designed for image classifiers with fixed triggers. The key difference from availability is in the banner: these attacks are quiet."

**Key facts.** NIST §2.2 (evasion; §2.2.2 black box; §2.2.5 mitigations), §2.3.2 (targeted), §2.3.3 (backdoors), §2.3.4 (model poisoning). Demo 3: 78.7% evade with labels only; 2% poison gives 100% trigger success; accuracy moves 0.02 at most. Demo 1 catches edits after `fit()` (.026, OWASP ML10).

**If asked.** *Backdoor or targeted poisoning?* A backdoor needs the trigger added at deployment; targeted poisoning changes answers for inputs chosen in advance and leaves them untouched. *Would a clean-label version work on demo 3?* Add the trigger only to rows that are genuinely low risk; it needs more rows, and it is a useful exercise on the same code.

**Go deeper.** TG §14; NIST §2.2 and §2.3.

**Next.** "Let us run demo 3 and read its first section."

### Slide 30 · Evasion, step by step: 17 edits, labels only, the cheapest wins

*About 5 minutes, with the live run.*

**On screen.** The four steps of demo 3's evasion (the target, the 974 people scored high risk, the 17 possible edits, the search with labels only) and the table of section 1 of `aml_report.txt`: evaded 78.7% / 32.8% / 20.7%, with one step 58.7% / 18.2% / 12.8%, with two steps 70.5% / 28.6% / 20.7%. A card on how to read it.

**Say.** "Run `uv run python demo/run_aml_demo.py`; it takes seconds. The header describes the target: a random forest of 200 trees, minimum leaf 10, trained on 2,000 synthetic rows, with an accuracy of 0.635 on the other 2,000. That is about as good as the noisy label allows. Section 1. 974 test rows are scored high risk. The attacker is a person filling in a form: they cannot change their age or a recorded diagnosis, but they can misreport what nobody checks. The code lists 17 edits: drop the smoker flag or not, lower the weight band by zero, one or two, lower the blood-pressure band by zero, one or two. It applies every edit that is possible for each person, sends them all to the model's predict function, which returns labels only, and keeps the cheapest edit that comes back low risk. Read the first line: with all three fields self-reported, 78.7% evade, and 58.7% need a single step, usually 'non-smoker', the strongest term of the risk score. The second line takes smoking out of the attacker's hands with a test: 32.8%. The third measures weight in clinic as well: 20.7%. The defence that worked is a process change. Adversarial training would not help, because a misreported form is an ordinary input."

**Key facts.** `aml_demo/evasion.py`: `candidate_edits()`, `cheapest_evasion()`, `summarise()`. 974 rows scored high risk. Target accuracy 0.635. NISTAML.025, OWASP ML01, ATLAS AML.T0015.

**If asked.** *Why do the two-step and the total numbers match in the third line?* With only blood pressure editable, every successful edit takes at most two steps. *Is a greedy search a real attack?* It is deliberately simple; an optimised attack would do at least as well.

**Code.** [`run_aml_demo.py`](../../demo/run_aml_demo.py) · [`aml_demo/evasion.py`](../../demo/aml_demo/evasion.py) `candidate_edits()`, `cheapest_evasion()` · [demo guide §3.0](Demo_Guide_EN.md#30-the-target-model) · [demo guide §3.1](Demo_Guide_EN.md#31-evasion-misreporting-a-form)

**Go deeper.** Demo guide §3.0 and §3.1; TG §3.1; `aml_report.txt`, section 1.

**Next.** "Section 3 of the same run: the backdoor."

### Slide 31 · Backdoor, step by step: two triggers, three doses, one screen

*About 5 minutes.*

**On screen.** The five steps of demo 3's backdoor (what lab A and lab B are, two triggers, the poison, the attack, the outlier screen) and the table of section 3 of `aml_report.txt`: the clean model at accuracy 0.635 with triggers flipping 28.3% (loud) and 32.3% (quiet); loud poison at 1%, 2%, 5% gives accuracy 0.627, 0.626, 0.630, flips 79%, 100%, 100%, screen catches 70%, 80%, 42%; quiet poison gives 0.630, 0.627, 0.615, flips 94%, 100%, 100%, screen catches 20%, 25%, 14%.

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

**Say.** "Section 3. Two triggers are written into two lab columns that carry no label signal: a loud one, lab A at 4.0, four standard deviations out, and a quiet one, lab A at +1.7 and lab B at −1.7, each value ordinary on its own. The poison function copies random training rows, applies the trigger, labels them all low risk and appends them; the forest is retrained with 1, 2 and 5 percent. First read the clean model line. The triggers already flip about 30% of high-risk scores before any poisoning, because the values are unusual and the forest gives the noise columns a little weight. So the attack is the rise above that baseline: from 32.3% to 100% with 2% quiet poison, 40 rows out of 2,040. Now the accuracy column: it moves by 0.02 at most, so a holdout check, GRAIMATTER's TECH 6 included, sees nothing. Last column: an isolation forest that drops the oddest 5% of the training table catches 80% of the loud trigger at 2%, but only 25% of the quiet one, and its catch falls as the poison grows, because a hundred identical rows stop looking rare."

**Key facts.** `aml_demo/poisoning.py`: `loud_trigger()`, `quiet_trigger()`, `poison()`, `attack_success()`, `outlier_screen()` with `IsolationForest(contamination=0.05)`. The release gate measures the rise over the clean model: 71.7 points. NISTAML.023, OWASP ML02, ATLAS AML.T0020.

**If asked.** *Why does the clean model react to the trigger at all?* The label is noisy and the forest uses the lab columns a little; unusual values push some scores across the threshold. *What would catch the quiet trigger?* Provenance of who contributed which rows, and tests for the trigger itself; outlier detection alone does not.

**Code.** [`aml_demo/poisoning.py`](../../demo/aml_demo/poisoning.py) `poison()`, `attack_success()`, `outlier_screen()` · [demo guide §3.3](Demo_Guide_EN.md#33-backdoor-a-contributor-poisons-the-training-data)

**Go deeper.** Demo guide §3.3; TG §3.3 and §14; `aml_report.txt`, section 3.

**Next.** "That was integrity. Now the third property of the triad: confidentiality."

### Slide 32 · Confidentiality: the model remembers who it saw

*About 3 minutes.*

**On screen.** Three cards for what can leak: who was in the data (membership inference, NISTAML.033; demo 5, section 1), what is in a record (attribute inference; demo 5, section 2, and demo 1 in part 4b), the model itself (extraction, NISTAML.031; demo 3, section 2, in part 4b). A table of three defences and their limits: do not memorise, return less, limit queries. Banner: quiet by design.

**Say.** "The third property of the triad is confidentiality, which NIST calls privacy. In machine learning there are three secrets. The first is who was in the training data. If a model was trained only on the patients of one clinic, proving that someone was in its training data proves they were a patient there. The second is what is in a person's record: an attacker who knows everything about someone except one field can ask the model to fill it in. The third is the model itself, which queries can copy; we run that one in video 4b. Demo 5 shows the first two in their simplest form. The defences come in three families. Stop the model memorising: larger leaves, regularisation, differential privacy. Return less in each answer: a label instead of a probability. And limit how many answers a user gets. Each one helps and each one has a limit, and the demo shows which. Like integrity attacks, these are quiet: the model keeps working for everyone, and the leak is only in how much surer it is about the people it trained on."

**Key facts.** NIST AI 100-2e2025 §2.4. Membership inference is NISTAML.033; attribute inference has no ID of its own (the gate files it under .032); extraction is NISTAML.031. Differential privacy bounds membership and attribute inference, not extraction.

**If asked.** *Is this not what part 4b is about?* Yes: this slide and the next are the short version, so video 4a covers the whole triad. Video 4b runs GRAIMATTER's own checks, which are stronger. *Why does membership matter if the attacker already has the person's record?* Because membership itself is the secret: being in the training data of a cancer clinic's model says you were treated there.

**Code.** Demo 5: [`run_confidentiality_demo.py`](../../demo/run_confidentiality_demo.py), with the attacks in [`confidentiality_demo/membership.py`](../../demo/confidentiality_demo/membership.py) and [`confidentiality_demo/attribute.py`](../../demo/confidentiality_demo/attribute.py). Walkthrough: [demo guide §5](Demo_Guide_EN.md#5-demo-5-confidentiality-the-simple-version).

**Go deeper.** TG §16 and §4; demo guide §5.

**Next.** "Let us run it."

### Slide 33 · Demo 5, step by step: ask, calibrate, decide

*About 5 minutes, with the live run.*

**On screen.** Five steps (the model, ask, calibrate, decide, one field), each with the count behind its number, and the table of section 3 of `confidentiality_report.txt`: four releases of the same data with their test accuracy, how often the membership attacker is right, and the smoker guess on members and strangers. A card on how the three steps connect.

**Say.** "Run `uv run python demo/run_confidentiality_demo.py`; it takes seconds. The model is the same kind of random forest as demo 3, but grown until every training person sits alone in a leaf. It scores a perfect 1.000 on its 1,000 training rows and 0.605 on 1,000 strangers: it remembers answers rather than learning a pattern. Section 1 is the membership attack in three steps. Ask: send a person's row and read the probability the model gives to their real outcome. That gives one number per person, and those individual numbers are what the next two steps use. Calibrate: the attacker has 200 people they know are not members, sorts their scores and takes the 90th percentile, 0.72. Decide: compare each person's own number with 0.72; above it is a member. Only now do we, who know the truth, count: and as a check, members average 0.83 and strangers 0.54, which is why one cut can separate them; the attacker could never compute those averages. That catches 96% of members and wrongly accuses 12% of strangers: right 92% of the time, where a coin toss gets 50%. Look at the two people at the end: the member has fewer risk factors than the stranger, yet the model is surer about the member. It is not reasoning, it remembers. Section 2 hides one field, smoking, and tries both values: 94% right on members, 60% on strangers. The 60% is just the population pattern, smokers are more often high risk; the 35 points on top is the leak. Section 3 is the table. Returning only a label still leaks: 70%. A minimum leaf of 20, the floor of demo 1's safe wrapper, brings the attacker down to 54% and the smoker gap to zero, and the model is more accurate, not less."

**Key facts.** Training accuracy 1.000, strangers 0.605. Average confidence in the truth (a check, not used by steps 2 and 3): members 0.83, strangers 0.54. Threshold 0.72 (90th percentile of the attacker's 200 strangers; 18 of them are strictly above it). Membership: 96.0% caught, 12.4% false alarms, right 91.8%, AUC 0.976. Smoker: 94.4% members, 59.6% strangers. Label only: 69.8%. Leaf 10: 57.5%. Leaf 20: 54.3%, test accuracy 0.636.

**Where each number comes from.** Say it, or point at the `Working.` line under each result in the output. Full derivation: [demo guide §5, "Every number, traced"](Demo_Guide_EN.md#5-demo-5-confidentiality-the-simple-version).

* *What step 1 hands on.* One number per person, not an average: the attacker's 200 strangers (0.715, 0.450, 0.520, ...) go to step 2, the tested people (members 0.800, 0.785, ...; strangers 0.670, 0.225, ...) go to step 3, and step 3 compares each one with 0.72 (0.800 > 0.72, member; 0.670 ≤ 0.72, not).
* *0.83 and 0.54: a check, not an input.* Steps 2 and 3 do not use them and the attacker cannot compute them (they would need to know who the members are). We compute them because we know the truth, to show members score higher. Each leaf holds one person, so each of the 200 trees votes 1 or 0 for a person's real outcome, and the confidence is the share of trees that vote for it (the member on screen: 160 of 200 = 0.80). Each tree trained on a random 63% of the members (its bootstrap sample), and those trees always vote right for them; the other trees vote right 54% of the time. 0.631 × 1 + 0.369 × 0.54 = 0.83. No tree saw the strangers: their confidences add up to 542.61, and 542.61 / 1,000 = 0.54.
* *Why 63%.* Each tree draws 1,000 rows from the 1,000 members, putting each back, like balls from an urn. One member is missed by one draw with probability 0.999, by all 1,000 with 0.999^1000 = 0.368 (about 1/e), so is picked with 1 − 0.368 = 0.632. The run counts 63.1% (`estimators_samples_`).
* *Why 54%.* A tree that never saw a person copies the label of a similar training person. Each outcome is a weighted coin with the person's true risk p, and two coins with the same p agree with probability p² + (1 − p)²: 0.567 on average over the strangers, the ceiling for copying a neighbour. The noise columns make the neighbours less similar, so the trees get 0.54; a blind coin gets 0.50.
* *0.72.* Sort the attacker's 200 stranger confidences. The 90th percentile sits at position 0.9 × (200 − 1) = 179.1, counting from 0; values no. 179 and 180 are both 0.72. Check: 18 of the 200 are strictly above it.
* *96.0% and 12.4%.* 960 of the 1,000 members are above 0.72: the true positive rate, TPR. 124 of the 1,000 strangers are above it: the false positive rate, FPR. It is 12.4% and not 10% because the threshold came from only 200 people.
* *How the three steps connect.* Ask gives each person one number; calibrate picks one cut using only the attacker's 200 known outsiders; decide applies that same cut to everyone, and we count. Show the band table in the output: above 0.72 sit 273 + 575 + 112 = 960 members and 109 + 15 = 124 strangers. Members pass because 126 trees on average saw each one and vote for them for sure, so they need only about 19 of the remaining 74; the 40 who miss were seen by fewer trees (120) and the rest voted for them only 24% of the time. Strangers have no sure votes and need 145 trees copying a neighbour right: only the 124 with a predictable outcome make it (74% true chance against 54%). On all 1,000 strangers the 90th percentile would be 0.735, not 0.72, hence 12.4% and not 10%.
* *91.8% and 0.976.* Right about 960 members and 876 strangers out of 2,000: 91.8%. AUC: in 975,038 of the 1,000,000 member–stranger pairs the member scores higher, 2,535 tie.
* *94.4% and 59.6%.* 944 and 596 of 1,000 smoking flags guessed right. Without any model, "high risk → smoker" is right for 62.1% of strangers: that is the population pattern. 94.4 − 59.6 = 34.8 points of leak.
* *Label only, 69.8%.* Scores are 1 (label right) or 0, so the threshold is 1.00: all 1,000 members and the 605 strangers the model gets right are called members. 0.5 × 100% + 0.5 × 39.5% = 69.8%.

**If asked.** *How does the attacker know the person's real outcome?* That is the assumption of this attack, and a realistic one: an insurer or an employer may hold it. Demo 1 uses the same assumption. *Why is the minimum-leaf model more accurate?* Memorising noise does not help predict new people; that is usual for overfitted models, but differential privacy, the strongest defence, does cost some accuracy. *Is this in the release gate?* No. Demo 5 is standalone; membership and attribute inference are gated through demo 1's numbers.

**Code.** [`run_confidentiality_demo.py`](../../demo/run_confidentiality_demo.py) (the comments mark each section as "Demo guide §5.N"). Steps 2 to 4: [`membership.py`](../../demo/confidentiality_demo/membership.py) `confidence_in_truth()`, `calibrate_threshold()`, `decide()`. Step 5: [`attribute.py`](../../demo/confidentiality_demo/attribute.py) `guess_field()`. The arithmetic behind every number: [`explain.py`](../../demo/confidentiality_demo/explain.py). Output: [`confidentiality_report.txt`](../../demo/output/confidentiality_report.txt). Walkthrough: [demo guide §5.0 to §5.3](Demo_Guide_EN.md#5-demo-5-confidentiality-the-simple-version).

**Go deeper.** Demo guide §5; TG §16; `confidentiality_report.txt`.

**Next.** "What does it mean to be above that cut? How sure is the attacker about one person?"

### Slide 34 · Above the cut: how sure is the attacker about one person?

*About 2 minutes.*

**On screen.** Four short paragraphs on the left (what the attacker knows, what they bet on, what it depends on, a stricter cut) and, on the right, the table printed in section 1 of `confidentiality_report.txt` under "What 'above the cut' means": the same scores as slide 33 cut at the 80th, 90th, 95th and 99th percentile, with TPR, FPR, how often the attacker is right on a 50/50 mix, and the share of the people called members who really are, with half members (1:1) and with one member per 100 strangers (1:100). A card "In one sentence".

**Say.** "Slide 33 gives the attacker 91.8%. What does that mean for one person above the cut? The attacker does not know that this person is a member. What they know is measured, not assumed: only 10% of their own 200 outsiders score above 0.72. Their bet is that the model memorised, so members score higher, and here the bet pays: 960 members are above the cut against 124 strangers. If the people tested are half and half, 960 of the 1,084 called members really are, 88.6%. But that depends on the mix. If there is one member per hundred strangers, the cut catches 9.6 members and still 124 strangers: only 7.2% of the accusations are right. Would a stricter cut help? At the 95th percentile the attacker is right 92.1% of the time, barely more than 91.8%: fewer false accusations, fewer members found. At the 99th, right falls to 77.6%, but 98.6% of the people called are members. A stricter cut does not make the attacker right more often; it makes each accusation more trustworthy. That is why GRAIMATTER looks at hits with very few false alarms. And with a minimum leaf of 20 the bet fails: right 54.3%, near a coin."

**Key facts.** 90th percentile (slide 33): threshold 0.720, TPR 96.0%, FPR 12.4%, right 91.8%, members among called 88.6% (1:1) / 7.2% (1:100). 80th: 0.676, 99.5%, 21.6%, 88.9%, 82.2% / 4.4%. 95th: 0.740, 92.8%, 8.6%, 92.1%, 91.5% / 9.7%. 99th: 0.825, 56.1%, 0.8%, 77.6%, 98.6% / 41.2%. Leaf 20: right 54.3%.

**Where each number comes from.** The table and its `Working, 90th row:` line in section 1 of the output. Full derivation: [demo guide §5.1, "What being above the cut means"](Demo_Guide_EN.md#what-being-above-the-cut-means).

* *Each row.* Same 1,000 members and 1,000 strangers, same scores; only the cut changes. The cut is the (1 − share) quantile of the attacker's 200 outsiders (`membership.calibrate_threshold(reference, 0.05)` for the 95th). TPR, FPR and right are counted as on slide 33.
* *88.6%.* Half and half: 960 members and 124 strangers are above 0.72, so 960 / (960 + 124) = 960 / 1,084 = 88.6% of the people called members are members.
* *7.2%.* One member per 100 strangers: for every 1,000 strangers, 10 members, of whom 96% = 9.6 are caught, against 124 strangers: 9.6 / (9.6 + 124) = 7.2%. In general: m × TPR / (m × TPR + FPR), with m members per stranger.
* *Why right barely moves at the 95th.* Right on a 50/50 mix is 0.5 × TPR + 0.5 × (1 − FPR). Going from the 90th to the 95th loses 3.2 points of TPR and gains 3.8 of 1 − FPR: 0.5 × 92.8% + 0.5 × 91.4% = 92.1%. At the 99th TPR falls to 56.1%: 0.5 × 56.1% + 0.5 × 99.2% = 77.6%.

**If asked.** *So is 91.8% "the chance a stranger was in the training data"?* No. It is how often the attacker is right over a test set with as many members as strangers. For one accused person, the chance they are a member is the 88.6% (1:1) or the 7.2% (1:100) column, and it depends on how many members there are among the people tested. *Why does GRAIMATTER not use accuracy?* Because what harms one person is a confident accusation; it reports the hits at a very low false alarm rate (TPR at low FPR), the 99th row of this table.

**Code.** [`run_confidentiality_demo.py`](../../demo/run_confidentiality_demo.py), the block "What 'above the cut' means" in §5.1; [`membership.py`](../../demo/confidentiality_demo/membership.py) `calibrate_threshold()`, `evaluate()`; [`explain.py`](../../demo/confidentiality_demo/explain.py) `flagged_who_are_members()`.

**Go deeper.** Demo guide §5.1; TG §16.

**Next.** "That closes the triad. The last way in does not touch training at all: the supply chain."

### Slide 35 · Supply chain: the attack arrives with what you download

*About 3 minutes.*

**On screen.** Four cards for NISTAML.051, model poisoning through a supplied model: how (backdoored pre-trained models, control of training randomness, model files that run code or return a planted falsehood), defences and limits (hashes, artefact scans, treat as untrusted; "a critical open problem"), frameworks (UK Code 7 and 8.1.2, OWASP ML06 and LLM03, ATLAS AML.T0010, EU AI Act 15(5)), and here: demo 4. Banner: AI inherits the software supply chain and adds data, pre-trained models and plugins.

**Say.** "The supply chain is a route, not an objective: whatever comes through it then breaks integrity, availability or confidentiality. AI inherits every weakness of the software supply chain, such as third-party code, and adds its own: collected and labelled data, pre-trained models and plugins. NIST counts as adversarial ML the attacks that exploit the data-driven nature of those dependencies; the rest is classic supply-chain security, and you need both. NIST's class here is model poisoning through a supplied model. For predictive AI it cites the Dropout Attack: whoever controls the randomness used in training can lower accuracy on chosen classes. For generative AI, backdoored pre-trained models whose behaviour survives fine-tuning and even safety training. And model files can carry ordinary code: ATLAS records models on Hugging Face that opened reverse shells when loaded. The defences are discipline: check the file against a published hash, scan what a model file would import, treat any supplied model as untrusted. NIST is candid that robustness to a backdoor hidden in supplied weights is a critical open problem."

**Key facts.** NIST §2.3.4, §3.2, §3.2.2, §4.2.2. UK Code principle 7, provision 8.1.2. OWASP ML06, LLM03. ATLAS AML.T0010, case studies CS0019 and CS0031. EU AI Act Art. 15(5): attacks on pre-trained components.

**If asked.** *Is safetensors enough?* It removes the code-execution route, not a backdoor in the weights. *And for TREs?* Demo 1 accepts `.joblib` and `.pkl`, both built on pickle: a model file from outside should be loaded as untrusted input.

**Go deeper.** TG §15 and §3.4.

**Next.** "Demo 4 shows four ways a mirror can change what you download."

### Slide 36 · Demo 4, step by step: pin at approval, check each download

*About 6 minutes, with the live run.*

**On screen.** The four steps of demo 4 (the supplier's release, the pin taken at approval, the mirror's changes, the checks) and the side-by-side table of section 5: swapped model with a 2% backdoor (usual check passes with accuracy 0.627, pin refuses, scan passes), code hidden in the pickle (0.635, refuses, refuses), key length 256 to 40 bits (still encrypts, refuses, refuses), safe-wrapper floor 20 to 1 (`request_release()` passes, refuses, refuses). Card: what the pin does not catch.

**Say.** "Run `uv run python demo/run_supply_chain_demo.py`. Section 1 is the supplier's release: demo 3's forest as `model.pkl`, a `bundle.json` with the published accuracy and 256-bit keys, and the safe-wrapper rules of demo 1. At approval the user records the SHA-256 of each file from the supplier's own release notes, not from the mirror. Section 2: the mirror serves a forest trained with 2% quiet-trigger poison. On the user's holdout it scores 0.627 against 0.635 published, within 0.02, so the usual acceptance test passes; the import scan finds only sklearn and numpy; only the pin refuses it. Section 3: a pickle that calls a function of the attacker's choosing while it loads, then hands back the genuine forest, so it predicts exactly as before; the scan reads the imports without loading and refuses it. Section 4: one number in a configuration file, 40-bit keys, which a search at a billion keys a second breaks in 18 minutes; and the safe wrapper's minimum leaf cut from 20 to 1, so demo 1's `request_release()` approves a tree with a leaf of one person. Floors kept in code refuse both. Section 5 is the table: four of four pass the usual check, none passes the pin and the scan or floor. Section 6 is the honest limit: a pin taken from the download verifies the backdoored forest. A digest proves the file is the one approved, not that the one approved was good."

**Key facts.** `demo/supply_chain/`: the pin, the import scan and the floors (key length at least 128, minimum leaf at least 20, maximum depth at most 4). 40 bits: 18 minutes; 56: 2.3 years; 128: 1.1e22 years. The release gate counts tampered files that pass the pin and the scan or floor: 0 of 4. NISTAML.051, OWASP ML06, ATLAS AML.T0010.

**If asked.** *What covers section 6's gap?* Signatures that say who published a file (Sigstore, OpenSSF model signing), build provenance (SLSA), formats that cannot hold code, an AI bill of materials, and testing a supplied model as untrusted. *Does the demo encrypt anything?* No; the key length is only a number in a file, which is the point.

**Code.** [`run_supply_chain_demo.py`](../../demo/run_supply_chain_demo.py) · [`supply_chain/integrity.py`](../../demo/supply_chain/integrity.py) · [`supply_chain/pickle_scan.py`](../../demo/supply_chain/pickle_scan.py) · [`supply_chain/downgrade.py`](../../demo/supply_chain/downgrade.py) · [demo guide §4](Demo_Guide_EN.md#4-demo-4-a-tampered-supply-chain)

**Go deeper.** Demo guide §4; TG §3.4 and §15; `supply_chain_report.txt`.

**Next.** "That closes video 4a: the triad and the supply chain. Video 4b: privacy in depth, with GRAIMATTER."

---

## Part 4b · The attacks in detail: privacy (video 4b)

### Slide 37 · Privacy: each NIST class, demos 1 and 2, and a release gate

*About 1 minute. Opens video 4b.*

**On screen.** Part 4b divider: one paragraph on what this half covers (the privacy classes and extraction, demos 1 and 2 section by section, the classes generative AI adds, and a gate that judges every demo), and four tags: privacy (NISTAML.03), demo 3 extraction, demos 1 and 2, release gate.

**Say.** "The second half of the detailed walkthrough is privacy, NIST's word for confidentiality, and the objective GRAIMATTER covers in depth. We start with the classes and with extraction, which demo 3 runs. Then we go through the two GRAIMATTER demos section by section: the hand-written checks of demo 1 and the official SACRO-ML package in demo 2. We close with the classes generative AI adds, the limits of all this, and a release gate that reads every demo against named obligations."

**Key facts.** Part 4b: TG §16 to §22 and the closing, slides 37 to 58. Demos run: `run_aml_demo.py` section 2, `run_demo.py`, `run_sacroml_demo.py` (a few minutes; show its saved report if you cannot wait), `run_gate.py`.

**If asked.** *Do I need video 3 first?* It helps: it explains why a TRE cares about these attacks and what its controls are.

**Go deeper.** TG Part 4 introduction; demo guide §1, §2 and §5.

**Next.** "The privacy classes first."

### Slide 38 · Privacy: what the model learned, and the model itself

*About 3 minutes.*

**On screen.** A table of the four privacy classes: model extraction (.031), reconstruction (.032, with attribute inference), membership inference (.033) and property inference (.034), with what the attacker does, the defences and their limits, and where the repository shows it. Banner: differential privacy protects people, not the model and not statistics of the population (NIST §2.4.5).

**Say.** "Privacy, in NIST's sense, covers data privacy, about the training rows, and model privacy, about the model. Extraction steals a working copy by querying the model; it is often not an end in itself but a step towards white-box attacks on the copy. Reconstruction recovers records, from released statistics or from a model; Dinur and Nissim showed that enough statistics reveal individual rows, which is why the US Census adopted differential privacy. Attribute inference, filling in a hidden field of someone you partly know, is the attack at the centre of GRAIMATTER's case studies, and NIST describes it here without an ID of its own. Membership inference decides whether a record was in the training set: loss thresholds, shadow models, LiRA, attacks that see labels only. Membership alone can disclose a diagnosis. Property inference learns a statistic of the training population, such as the share of patients with a condition. On defences, the banner says it: differential privacy bounds membership and reconstruction, at a cost in utility, but it protects people, so it does nothing against extraction, and several papers report it does not stop property inference."

**Key facts.** NIST §2.4.1 (reconstruction and attribute inference), §2.4.2 (membership), §2.4.3 (property), §2.4.4 (extraction), §2.4.5 (mitigations). Demos: extraction 86.9% agreement after 200 queries (demo 3); kNN stores 500 of 500 rows and SVC 423 support vectors; 20 queries recover two hidden fields; membership AUC 0.708, 0.528 with the safe wrapper (demo 1).

**If asked.** *Attribute inference or reconstruction?* One field given the rest of a record, against whole records. The release gate files attribute inference under .032. *Why not demonstrate property inference?* A single synthetic cohort has no hidden population statistic worth recovering; it stays a gap.

**Go deeper.** TG §16 and §4; NIST §2.4.

**Next.** "Extraction is the one demo 3 runs. Back to its output."

### Slide 39 · Extraction, step by step: invented rows, real answers, a copy

*About 4 minutes, with the live run.*

**On screen.** The four steps of demo 3's extraction (invent rows inside the published ranges, ask the API, train a copy, use it to plan edits) and the table of section 2 of `aml_report.txt`: at 50, 200, 1,000 and 5,000 queries the copy agrees with the target on 77.7%, 86.9%, 89.5% and 93.5% of real rows, with accuracy 0.610, 0.623, 0.629 and 0.630, and edits planned on it fool the target for 22.0%, 54.2%, 58.3% and 64.4% of flagged people. Card: the query gate.

**Say.** "Section 2 of demo 3's output. The attacker never sees a real record: the data dictionary publishes the valid range of each input, so they invent rows inside those ranges, send them to the API and train their own forest on the labels that come back. Fidelity is the share of real test rows on which the copy and the target agree. Read the table by budget. Fifty queries already give a 78% copy; 200 give 86.9%, and the copy's accuracy, 0.623, is close to the target's 0.635: the owner's work is gone. The last column is why extraction matters beyond the theft itself. The attacker plans evasion edits on the copy, offline, where the target never sees them, and then uses them: at 200 queries, those edits get 54% of flagged people past the real model. The last line puts the target behind demo 1's query gate with a budget of 200 rows; it refuses a 1,000-row request, but 200 rows were already enough, and several accounts multiply any budget. NIST says the same: query limits can be circumvented by well-resourced attackers."

**Key facts.** `aml_demo/extraction.py`: `invented_rows()`, `steal()`, `fidelity()`, `transfer_rate()`. The gate treats agreement above 80% after one 200-row budget as a breach (86.9%). NISTAML.031, OWASP ML05, ATLAS AML.T0024.002.

**Where each number comes from.** The output prints a `working:` line under each budget ([demo guide §3.2](Demo_Guide_EN.md#32-extraction-copying-the-model-through-its-api)). The test set is 2,000 real rows; the target flags 974 of them as high risk. At 200 queries: the copy gives the same label as the target on 1,738 of 2,000 rows (86.9%), the right label on 1,246 (0.623); planned on the copy, edits are found for 928 of the 974 flagged people and 528 of them also fool the target, 528 / 974 = 54.2% (people with no edit count as failures). The gate: 1,000 rows requested, budget 200, refused.

**If asked.** *Would returning scores instead of labels make it worse?* Yes; this attack already works with labels only. *Would differential privacy help?* No; DP protects training rows, not the model.

**Code.** [`aml_demo/extraction.py`](../../demo/aml_demo/extraction.py) `invented_rows()`, `steal()`, `fidelity()` · [demo guide §3.2](Demo_Guide_EN.md#32-extraction-copying-the-model-through-its-api)

**Go deeper.** Demo guide §3.2; TG §3.2 and §16; `aml_report.txt`, section 2.

**Next.** "Now the data side of privacy, with the GRAIMATTER demos, starting from the cohort."

### Slide 40 · Half the rows never reach the researcher

*About 1.5 minutes.*

**On screen.** Figure: 1,000 synthetic rows (seed 7), 500 to the researcher for training, 500 kept by the TRE and never shared, used to score the model and run attacks. Columns: six clinical (age, diabetes, asthma, weight in four levels, blood pressure in five, smoker), ten noise columns with no label signal, and a `high_risk` label drawn from a known logistic function. Footer: the data dictionary (TECH 8) in `demo/output/data_dictionary.json`, following Appendix C.

**Say.** "Both GRAIMATTER demos use the same synthetic cohort: 1,000 rows drawn with seed 7, split 500 for the researcher and 500 kept by the environment. That is TECH 6: the environment holds back data the team never trains on, and uses it to check accuracy and to run attacks. Two terms we will use: training accuracy is the score on rows the model has seen; set-aside accuracy is the score on the 500 rows the researcher never received. A large gap means the model has fitted this sample, noise included. The label comes from a known function of six clinical columns, and there are ten noise columns with no signal at all, so that an unconstrained tree has something to memorise."

**Key facts.** TECH 6 (p. 43), TECH 8 (p. 46), Appendix C (p. 83). `demo/graimatter_demo/cohort.py`, seed 7. Demo 3 uses the same generator with 4,000 rows.

**If asked.** *Why noise columns?* To make memorisation visible: a tree that splits on noise is fitting individuals, not the risk.

**Code.** [`graimatter_demo/cohort.py`](../../demo/graimatter_demo/cohort.py) `hold_out_for_tre()` · [demo guide §1.1](Demo_Guide_EN.md#11-the-cohort-and-the-rows-the-researcher-never-sees-tech-6)

**Go deeper.** TG §17.

**Next.** "First, the paper's own case study: attribute inference on one person."

### Slide 41 · One planted person: 20 queries recover two hidden fields

*About 1.5 minutes.*

**On screen.** A 4 × 5 grid of model confidences for weight (rows) by blood pressure (columns). One cell, overweight and slightly high, is at 1.000; the other 19 tie at 0.500. Known: age 62, diabetic, asthmatic, smoker.

**Say.** "This is the paper's first case study, rebuilt on synthetic data. An attacker knows four public facts about someone: age 62, diabetic, asthmatic, smoker. They do not know the person's weight or blood pressure. Weight has four levels and blood pressure five, so there are 20 combinations. The attacker sends all 20 to the model and looks at the confidence. Models are usually more confident on inputs they were trained on. Here one cell is at 1.000 and the other 19 tie at 0.500, so the unique best guess is the hidden truth: overweight, with slightly high blood pressure. That is attribute inference: filling in hidden fields of a person by querying the model. Twenty rows of queries were enough, and we will come back to that number when we talk about query budgets."

**Key facts.** Appendix E §20.1 (pp. 86-87): in the paper's version the top answer was 93.8% and the next 57.7%. Demo: `demo_report.txt`, section 2.

**If asked.** *Is this realistic?* The demo plants a block of similar rows to make the effect clean; the paper's real-data version shows the same pattern with a smaller gap.

**Code.** [`graimatter_demo/case_study.py`](../../demo/graimatter_demo/case_study.py) · [demo guide §1.2](Demo_Guide_EN.md#12-attribute-inference-on-one-planted-record-appendix-e)

**Go deeper.** TG §19.2; §16 (reconstruction and attribute inference).

**Next.** "To judge a model we need numbers. Here are the metrics."

### Slide 42 · Chance, the tail, and how rare a member is

*About 2 minutes.*

**On screen.** Figure with three ideas. AUC, the average: the chance the attack scores a random member higher than a random non-member; 0.5 is a coin toss. FDIF, the tail: share of members in the top 10% of scores minus the share in the bottom 10%. How rare a member is: P(member | flagged) = A·TPR / (A·TPR + (1 − A)·FPR); for the unconstrained tree (TPR 1.000, FPR 0.588) that is 0.630 at A = 0.5 and 0.017 at A = 0.01.

**Say.** "Membership inference asks whether a row was in the training set. The attack gives each row a score. AUC is the chance that a random member scores higher than a random non-member; 0.5 is a coin toss. Advantage is the gap between the true-positive and false-positive rates. TPR at 10% FPR asks how many real members the attack catches when it may raise a false alarm on only about 10% of non-members. FDIF looks at the extremes: the share of members in the top 10% of scores minus the share in the bottom 10%, with a permutation p-value. Why both? Because a model can look like chance on average and still expose a group of people in the tail; we will see exactly that on slide 45. Finally, the membership posterior: if the attack says 'member', how likely is that to be true? It depends on how rare members are. For our unconstrained tree it is 0.630 when half the candidates are members, and 0.017 when one in a hundred is."

**Worked examples.** Use these if the room wants numbers; TG §18.1 has the full working.

1. *The average.* "Four members and four non-members, scored 0.9, 0.7, 0.6 and 0.4 for the members and 0.8, 0.5, 0.3 and 0.2 for the non-members. Compare every member with every non-member: 16 pairs, and the member scores higher in 12 of them. AUC is 12 out of 16, 0.75. Call 'member' everything at 0.5 or above: 3 of 4 members are flagged and 2 of 4 non-members, so the advantage is 0.75 minus 0.50, 0.25. On average the attack is right three times in four, but the average does not tell you who is exposed."
2. *The tail.* "Two hundred rows, half of them members. The attack is certain about 20 people: 10 members it scores 1 and 10 non-members it scores 0. Everyone else gets a random score. The AUC is about 0.595, inside the chance band. Now look at the top 20 scores: the 10 certain members plus about 5 more by chance, 75% members. The bottom 20 has about 25%. FDIF is 0.75 minus 0.25, about 0.50, with a p-value near 0.003. The average says coin toss; the tail names ten people."
3. *The rare member.* "Take a good attack, TPR 0.8 and FPR 0.2. Test 1,000 people, half of them members: it flags 400 members and 100 non-members, so 4 flags in 5 are right, 0.80. Test 10,000 people, 1 in 100 a member: it flags 80 members and 1,980 non-members, so only 80 of 2,060 flags are right, 0.04. Same attack; only the base rate changed. But if the attacker flags only the rows the attack is certain about, as in the tail example, there are no false alarms and every flag is right."

**Key facts.** Appendix F (pp. 92-95); posterior formula Appendix F §21.3. Chance band for 100 members and 100 non-members: roughly 0.38 to 0.62. Paper's example: TPR 0.8, FPR 0.2 gives 0.04 at 1 in 100.

**If asked.** *So is membership inference harmless when members are rare?* Not necessarily: the tail can still single out specific people with high confidence, which is what FDIF and TPR at low FPR measure.

**Code.** [`graimatter_demo/metrics.py`](../../demo/graimatter_demo/metrics.py) · [demo guide §0.5](Demo_Guide_EN.md#05-the-attack-metrics-graimatter_demometricspy)

**Go deeper.** TG §18, and §12.1 for the three worked examples.

**Next.** "Now demo 1 on the unconstrained tree."

### Slide 43 · Perfect training accuracy and a leaf of one person: refused

*About 2 minutes.*

**On screen.** Table of checks for the unconstrained tree with the seeded result, the demo limit and whether it fires: training vs set-aside accuracy 1.000 vs 0.590 (gap 0.410, limit 0.15, fires); smallest leaf 1 row; file size ratio 0.267 (limit 0.75, does not fire); worst-case membership AUC 0.708 (limit 0.62, fires); advantage 0.412 (limit 0.20, fires); TPR at 10% FPR 0.156 (limit 0.35, does not fire); FDIF 0.620 with p = 0.003 (fires); weight attribute inference abstained. Decision: do not release, four rules fire. Note: the attribute attack abstained because the tree isolated rows with noise columns.

**Say.** "The researcher would report 100% accuracy. On the environment's set-aside rows it is 59%. That gap of 0.41 is overfitting, and the smallest leaf holds one training row. The worst-case membership attack, the one Appendix G describes, reaches an AUC of 0.708 and an advantage of 0.412, and FDIF is 0.620 with a p-value of 0.003. Decision: do not release; four rules fire. Now notice what does *not* fire. The file is only 0.27 of the training table, and TPR at 10% FPR is 0.156. Size alone would have let this model through, which is why TECH 7 asks for a range of checks, not one. And the attribute attack on weight abstains, because this tree separates people using the noise columns, so changing someone's weight never moves them to a different leaf. Slide 41 was the case where the model does split on the hidden fields. Remember that these limits are a demo policy, not the paper's."

**Key facts.** `demo_report.txt`, section 4. Limits in `demo/graimatter_demo/disclosure.py` (ELA 8). Posterior 0.630 / 0.017. Salem-synth on this tree: AUC 0.703, FDIF 1.000.

**If asked.** *What is the 'worst-case' attack exactly?* It trains a classifier on the model's predicted probabilities plus the true label, with the training and held-out rows in hand: a conservative upper bound, not a realistic attacker (Appendix G).

**Code.** [`graimatter_demo/attacks.py`](../../demo/graimatter_demo/attacks.py) · [`graimatter_demo/disclosure.py`](../../demo/graimatter_demo/disclosure.py) · [demo guide §1.4](Demo_Guide_EN.md#14-unconstrained-tree-native-training)

**Go deeper.** TG §19.0 (the demo policy) and §13.4.

**Next.** "Same data, but through a safe wrapper."

### Slide 44 · Leaf 20, depth 4: AUC 0.528, released under a demo policy

*About 2 minutes.*

**On screen.** Bar figure comparing the unconstrained tree and the safe wrapper on membership AUC (0.708 vs 0.528), advantage (0.412 vs 0.004), train minus set-aside (0.410 vs 0.108), TPR at 10% FPR (0.156 vs 0.116) and FDIF (0.620 vs 0.020), with the demo limit as a dashed line. Unconstrained tree: refuse. Safe wrapper: release under the demo policy.

**Say.** "The researcher asks for the same settings, but through the hand-written safe wrapper. It reads `demo/constraints.json` and corrects them: minimum leaf size from 1 to 20, maximum depth from unlimited to 4. Appendix D shows the constraints-file format with an example minimum leaf of 5; the demo is stricter so the contrast shows on a few hundred rows. Training accuracy drops to 0.692, and set-aside accuracy barely moves, 0.584. So the deep tree's extra accuracy was memorisation, not skill. The worst-case attack falls to an AUC of 0.528, an advantage of 0.004, FDIF 0.020 with a p-value of 0.445. No demo rule fires, so the script releases it. Say it clearly: the policy is ours, not the paper's."

**Key facts.** `demo_report.txt`, section 5. TECH 9-10. `request_release()` only says "Run file through the next step of the checking procedure"; the attack numbers make the decision. Posterior 0.502 / 0.010.

**If asked.** *Why 20 and 4?* A local choice to make the contrast visible on 500 rows. Appendix A experiment 2 of the paper warns that safe settings on one dataset can be risky on another, which is why demo 1 still attacks the wrapped tree.

**Code.** [`graimatter_demo/safe_model.py`](../../demo/graimatter_demo/safe_model.py) · [demo guide §1.5](Demo_Guide_EN.md#15-the-same-data-through-a-safe-wrapper-tech-9-and-10)

**Go deeper.** TG §19.5.

**Next.** "But one attack sees something the average hides."

### Slide 45 · The quiet failure: AUC near 0.5, but FDIF 0.160

*About 1.5 minutes.*

**On screen.** Figure: the safe-wrapper tree under two membership attacks. Worst case (TRE tables): AUC 0.528, TPR at 10% FPR 0.116, FDIF 0.020 (p 0.445). Salem-synth (similar data): AUC 0.512, TPR at 10% FPR 0.118, FDIF 0.160 (p 0.027). Note: more members in the top scores than chance explains; a data controller could refuse on that.

**Say.** "On the same wrapped tree we also run a second attack, Salem-synth, where the attacker trains a shadow model on similar data instead of the environment's own tables. Its AUC is 0.512, close to chance. But its FDIF is 0.160 with a p-value of 0.027: the top tenth of its scores holds clearly more members than the bottom tenth. This is exactly the Appendix F warning: an average metric can hide a tail. The demo's export rule follows the worst-case attack, whose FDIF is 0.020, so it still releases. A data controller who cares about the tail could set a stricter limit and refuse, and that is a policy choice, not a technical one."

**Key facts.** `demo_report.txt`, section 5 (Salem-synth). Appendix A Table 2 describes the Salem scenarios. Appendix F's example: an attack certain about 20 of 200 rows has an AUC of about 0.595, inside the chance band.

**If asked.** *Why does a weaker attacker see more in the tail?* The attacks use different information and rank rows differently. Salem-synth is not surer about any single row (its TPR at 10% FPR, 0.118, is about the same as the worst case's 0.116), but its top scores hold more members than its bottom ones. It is a reminder to run more than one attack.

**Code.** [`graimatter_demo/metrics.py`](../../demo/graimatter_demo/metrics.py) · [demo guide §1.5](Demo_Guide_EN.md#15-the-same-data-through-a-safe-wrapper-tech-9-and-10)

**Go deeper.** TG §19.5, "The quiet failure", and §12 (FDIF).

**Next.** "Some models should never be released as files at all."

### Slide 46 · Nearest neighbours and SVC store rows: refuse them

*About 1.5 minutes.*

**On screen.** Cards: 1-nearest neighbour stores all 500 rows (file 68,677 bytes, ratio 1.010), refused. RBF support-vector classifier stores 423 support vectors out of 500 (ratio 0.94), refused. Both wrapper classes refuse to fit (`constraints.json` marks them not permitted). The paper's alternatives (TECH 11): aggregated data, a differentially private algorithm, or a query-limited service. In the paper: Appendix E §20.4, an SVM holding 441 exact patient rows out of 798.

**Say.** "Instance-based models need their training rows to work. A nearest-neighbour model finds the closest stored rows; a kernel SVC compares new inputs with its support vectors. Those rows can be read straight out of the file, so the demo refuses both, whatever the attack numbers say. The paper's options are to train on aggregated data, to use a differentially private variant, or not to release the file at all and offer a query-limited service instead. Its case study describes a real environment that found 441 copies of patient records out of 798 inside an SVM."

**Key facts.** TECH 11 (p. 49), §10.1.5 (pp. 39-40), Appendix E §20.4 (pp. 91-92). `demo_report.txt`, section 6.

**If asked.** *Is a linear SVM also a problem?* It depends on how it is stored. scikit-learn's `LinearSVC` keeps only weights, but `SVC(kernel="linear")` still stores its support vectors in the file. Check what the file contains, not the model's name.

**Code.** [`graimatter_demo/safe_model.py`](../../demo/graimatter_demo/safe_model.py) · [demo guide §1.6](Demo_Guide_EN.md#16-instance-based-models-are-refused-tech-11)

**Go deeper.** TG §19.6; §16 (reconstruction).

**Next.** "What if the researcher edits the model after training?"

### Slide 47 · Editing the model after fit() is caught

*About 2 minutes.*

**On screen.** Figure: the safe wrapper's pipeline: `constraints.json` (risk appetite), wrapper init (corrects leaf and depth or records an override), `fit()` (stores a digest of the tree), `request_release()` (checks leaf size and compares parameters and digest with the fitted state), TRE attacks, register and snapshot. A tamper path: parameters edited back after fit, attribute `hidden_rows` added, smallest leaf still 1, so "Do not allow release".

**Say.** "The wrapper records the state of the model when it was fitted. In this section of the demo the researcher overrides the constraints and trains a deep tree, then edits the parameters back towards the allowed values and adds a hidden attribute. `request_release()` compares the fitted state with the current one and says not to release: `max_depth` and `min_samples_leaf` changed after fitting, the smallest leaf still holds one row, and an attribute called `hidden_rows` was added. That covers both the careless case, RT1, changing a parameter and forgetting to retrain, and the deliberate one, RT2, hiding data. A file with a `.txt` extension is refused because it is not `.joblib` or `.pkl`. For the approved model, the demo writes a register entry and a pipeline snapshot, which is TECH 3."

**Key facts.** §10.1.2 (p. 37), TECH 3 (p. 42), TECH 10 (p. 48). `demo_report.txt`, sections 7 and 9; `tampered_tree.release.json`, `data_use_register.json`, `pipeline_snapshot.json`. The digest is SHA-256 of the tree arrays.

**If asked.** *Is this model poisoning?* It is the same capability, model control (NISTAML.011/.026, OWASP ML10), used here to hide data rather than to change predictions. *Is `.pkl` safe?* Pickle files can execute code when loaded; treat a model file from outside as untrusted (§15).

**Code.** [`graimatter_demo/safe_model.py`](../../demo/graimatter_demo/safe_model.py) · [demo guide §1.7](Demo_Guide_EN.md#17-editing-the-model-after-fit-risk-types-rt1-and-rt2)

**Go deeper.** TG §19.7 and §19.9.

**Next.** "If the model stays on a server, the environment can limit queries."

### Slide 48 · Count rows, not calls: one patient allowed, 20 blocked

*About 1.5 minutes.*

**On screen.** Figure: a budget of 8 rows for one user. Request 1, one patient lookup, 1 row: allowed. Request 2, the attribute sweep, 20 rows: refused (1 used, budget 8). Note: a real query-limited service also needs an external test (TECH 17).

**Say.** "If the model is not released as a file but kept on a server, the environment can limit queries. The demo gate gives one user a budget of 8 rows. A clinician's single patient lookup uses 1 row and is allowed. Then the same user sends the 20-combination sweep from the attribute case study, in one request. The gate refuses it: 20 rows requested, 1 already used, budget 8. The unit matters. If the budget counted HTTP calls, one call carrying 20 rows would pass. TECH 17 says a real query-limited service should be tested by an external party; the demo implements only the control logic. And remember demo 3 from the other side: a row budget slows model extraction, but 200 rows already copied a simple model."

**Key facts.** TECH 16-17 (pp. 52-53), §10.1.7 (pp. 40-41). `demo_report.txt`, section 8. UK Code provision 6.2.

**If asked.** *How do you stop someone using many accounts?* You cannot with a budget alone; identity checks and monitoring are part of the service, which is why TECH 17 asks for an external test.

**Code.** [`graimatter_demo/query_gate.py`](../../demo/graimatter_demo/query_gate.py) · [demo guide §1.8](Demo_Guide_EN.md#18-a-query-budget-that-counts-rows-tech-16)

**Go deeper.** TG §19.8; TG §3.2 for the extraction side.

**Next.** "The last check in demo 1 is differential privacy, on the simplest possible release."

### Slide 49 · Noise protects a mean; the best of 50 draws undoes it

*About 1.5 minutes.*

**On screen.** Figure: attacker accuracy at guessing whether one person was included in a released mean: 1.000 for the deterministic mean, 0.703 at ε = 8, 0.522 at ε = 1, 0.487 at ε = 0.2 (0.5 is a coin toss). Error of the released mean at ε = 0.2: 0.3053 for one draw, 0.0084 for the best of 50 draws. Note: keeping the draw closest to the true mean undoes the noise; TRE staff choose the seed without looking.

**Say.** "Differential privacy is a property of the release mechanism, not of the data. The paper's thought experiment: the attacker knows everything except whether one person was included, and sees the release. A plain mean gives the answer away: accuracy 1.000. Adding Laplace noise, with smaller epsilon meaning more noise, pushes the attacker back towards a coin toss: 0.703 at epsilon 8, 0.522 at 1, 0.487 at 0.2. TECH 12 adds a practical warning. At epsilon 0.2 one noisy mean misses the truth by 0.31, but if someone draws 50 times and keeps the closest, the miss is 0.008, which cancels the protection. So the environment's staff, not the researcher, should pick the random seed, without looking at the result. This repository only sketches differential privacy on a mean; it does not train a private model."

**Key facts.** §10.1.3 (pp. 37-39), TECH 12 (p. 50). `demo_report.txt`, section 3. Sensitivity (90 − 30) / 500 = 0.12; Laplace scale = sensitivity / ε. NIST: the 2020 US Census used ε = 19.61.

**If asked.** *What epsilon should we use?* There is no universal answer; it trades privacy against utility, and practice often uses large values (NIST §2.4.5).

**Code.** [`graimatter_demo/dp_sketch.py`](../../demo/graimatter_demo/dp_sketch.py) · [demo guide §1.3](Demo_Guide_EN.md#13-what-epsilon-means-on-a-mean-section-1013)

**Go deeper.** TG §19.3; §16 (DP and its limits for each privacy class).

**Next.** "Now the same cohort through the official toolkit."

### Slide 50 · sacroml: leaf 5, 'proceed to next step', still flagged

*About 3 minutes.*

**On screen.** Table for sacroml 2.0.1, unconstrained tree vs wrapped tree (leaf 5): training / set-aside accuracy 1.000 / 0.590 vs 0.868 / 0.566; worst-case membership AUC over 3 runs, mean 0.500 vs 0.494, none above the null band; smallest leaf vs threshold 10, 1 vs 5, `k_anonymity_risk` true for both; other structural flags true; `dof_risk` false; `request_release()` without a Target says "Proceed to next step of checking"; setting `min_samples_leaf` from 5 to 1 after `fit()` makes `posthoc_check()` report disclosive.

**Say.** "The second demo runs the same cohort through sacroml 2.0.1, the maintained toolkit from the AI-SDC project the paper names. Its safe wrapper warns that a minimum leaf of 1 is below its recommended minimum of 5 and changes it to 5. `request_release()` without a target writes a target file and says 'Proceed to next step of checking': it does not run attacks and it is not an approval. Passing a target would also start the LiRA attack, which the upstream example runs with 100 shadow models; this demo does not run LiRA. Then the attacks. The structural attack marks a leaf as risky when it holds fewer than 10 training rows, so both the unconstrained tree and the wrapped tree with leaf 5 are flagged. In other words, moving from leaf 1 to leaf 5 is what the published rules do, and the package's own structural check still calls that tree risky. And the membership AUC is 0.500 for the tree that memorised everyone. The next slide explains why."

**Key facts.** `demo/output/sacroml/sacroml_report.txt`; per-attack `report.json` and `report.pdf` under `demo/output/sacroml/`. Null band 0.377 to 0.623. The seeded run takes about three and a half minutes.

**If asked.** *How do I read the attribute results?* Each cell is correct unique guesses over unique guesses made, out of 500 rows; "136/136" means every guess the attack was willing to make was right, not that 136 rows were guessed (TG §20.4).

**Code.** [`run_sacroml_demo.py`](../../demo/run_sacroml_demo.py) · [demo guide §2](Demo_Guide_EN.md#2-demo-2-the-same-checks-with-sacro-ml)

**Go deeper.** TG §20.

**Next.** "Same tree: 0.708 in one demo, 0.500 in the other."

### Slide 51 · Same tree, AUC 0.708 or 0.500: two different attacks

*About 3 minutes.*

**On screen.** Figure: confidence in the true label for training rows (members) and set-aside rows. Unconstrained tree: pure leaves, every answer 0 or 1; members always 1; set-aside right 59% of the time. Safe wrapper (leaf 20, depth 4): similar spread for both groups. Notes: the hand-written attack sees probabilities plus the true label; sacroml sees predicted probability only, and pure leaves are extreme for everyone.

**Say.** "Both demos call their attack 'worst case', but they are different tests. The hand-written attack trains a classifier on the predicted probabilities *plus the true label*, so it can use the confidence in the correct class. On the unconstrained tree every leaf is pure, so every prediction is 0 or 1. Training rows always get confidence 1 in their true label. Set-aside rows get 1 when the tree happens to be right, 59% of the time, and 0 otherwise. The label-aware attack sees that gap and reaches 0.708. The sacroml attack scores rows by predicted probability only. Without the label, a pure leaf looks equally extreme for members and non-members, so its AUC is 0.500. The lesson: an AUC near 0.5 from the package does not mean the tree failed to memorise. In demo 2 it is the structural attack that catches it. For the wrapped tree, with leaves of 20 rows, both groups spread over similar confidences, which is why demo 1's AUC drops to 0.528."

**Key facts.** Appendix G (p. 96). Code: `attacks.py` (`_attack_features`) and `sacroml.attacks.worst_case_attack` (configured with `include_model_correct_feature: false`, `sort_probs: true`).

**If asked.** *Which attack is right?* Both are valid tests of different threats. That is the point: a single attack number is not a release decision.

**Code.** [`run_sacroml_demo.py`](../../demo/run_sacroml_demo.py) · [`graimatter_demo/attacks.py`](../../demo/graimatter_demo/attacks.py) · [demo guide §2.2](Demo_Guide_EN.md#22-the-attacks-on-two-trees)

**Go deeper.** TG §21.2.

**Next.** "Three differences sum up the two demos."

### Slide 52 · Leaf 20 vs 5, label-aware vs probability-only

*About 2 minutes.*

**On screen.** Comparison table: leaf rule (20 and depth 4 vs 5 from the rules file), wrapped tree accuracy (0.692 / 0.584 vs 0.868 / 0.566), membership attack (probabilities plus label, AUC 0.528, vs probabilities only, mean AUC 0.494), leaf check (20 vs 5 < 10, `k_anonymity_risk` true), outcome (release under the demo policy vs "Proceed to next step of checking", structural risk still true).

**Say.** "Three differences matter. First, the leaf rule: the hand-written wrapper forces leaf 20 and depth 4; the package's rules file forces leaf 5. Second, the membership attack: probabilities plus the label versus probabilities only. Third, the outcome: the hand-written script releases the stricter tree because its own attack falls inside the demo limits; the package never approves anything here, it says to continue checking, and its structural attack still flags the leaf-5 tree. Neither is an approval process. A real environment would combine these kinds of evidence with a policy agreed with its data controller."

**Key facts.** `demo_report.txt` section 10 and `sacroml_report.txt`. Appendix D (p. 83) example leaf size: 5. ELA 8, ELA 11.

**If asked.** *Should we use the package or write our own?* Use the maintained package for its structural checks and reports, add attacks that use the label, and set the thresholds with the data controller.

**Code.** [`run_demo.py`](../../demo/run_demo.py) · [`run_sacroml_demo.py`](../../demo/run_sacroml_demo.py) · [demo guide §1.10](Demo_Guide_EN.md#110-side-by-side)

**Go deeper.** TG §21.1 and §21.3.

**Next.** "One more way data can leave a research environment: written into the model on purpose."

### Slide 53 · Writing data into the model: two channels an accuracy check misses

*About 2 minutes.*

**On screen.** Three steps on the left (in the weights, in the behaviour, why it matters) and a table: channel (weight LSB, behaviour), where the message is (low mantissa bits, trigger inputs), accuracy (0.575 → 0.575, 0.575 → 0.632), removed by (clip / quantise / noise, fine-tune / DP). A card: "The TRE's answer: transform, do not detect."

**Say.** "The privacy attacks so far are about a model leaking its training data by accident. This is the opposite: a researcher writing data into the model on purpose, the way a message is hidden in the low bits of an image. There are two channels. First, the weights: a float32 has 23 mantissa bits, and the lowest eight carry almost no magnitude, so you can overwrite them with arbitrary bytes. Hiding a 111-byte note in a 10,000-weight network moves no weight by more than three millionths and leaves accuracy unchanged, so an accuracy check passes it and the data leaves inside the model. EvilModel did this with whole malware files in 2021. Second, the behaviour: add a few trigger inputs far from the real data, each labelled to carry one bit, and the model learns to answer them that way while its accuracy holds; whoever knows the triggers reads the message back. That is backdoor watermarking used as a covert channel. The defences are cheap and go on every released model: clip the low bits, quantise, or add noise to kill the weight channel, and fine-tune or train with differential privacy for the behavioural one. A distribution test does not help, because the payload fills too few weights to show up. The lesson is to transform every released model, not to try to detect the hidden data."

**Key facts.** `uv run python demo/run_stego_demo.py`; `stego_report.txt`. Demo guide §6; TG §9.4. EvilModel (Wang et al. 2021); backdoor watermarking (Adi et al. 2018); memorisation (Song et al. 2017). The payload is a fabricated note, never executable code. The demo is standalone and not wired into the gate.

**If asked.** *Would the release gate catch this?* No: the gate judges the numbers the demos print, and both channels leave accuracy unchanged. The fix is a release-time transform of the weights, which is why this is a demo and not a tolerance. *Can you detect a stego model?* Not reliably; removing the capacity is the dependable move.

**Code.** [`run_stego_demo.py`](../../demo/run_stego_demo.py) · [`stego_demo/weights.py`](../../demo/stego_demo/weights.py) · [`stego_demo/behaviour.py`](../../demo/stego_demo/behaviour.py) · [`stego_demo/defences.py`](../../demo/stego_demo/defences.py) · [demo guide §6](Demo_Guide_EN.md#6-demo-6-hiding-data-in-a-model)

**Go deeper.** Demo guide §6; TG §9.4.

**Next.** "One more family of classes before we close: generative AI."

### Slide 54 · Generative AI keeps the objectives and adds classes

*About 1.5 minutes.*

**On screen.** A table of what NIST adds for generative AI: misuse enablement (NISTAML.04), direct and indirect prompt injection (.018, .015), misaligned outputs (.027), prompt extraction and leaks from user interactions (.035, .036), training data attacks and data extraction (.037, .038), compromising connected resources (.039). Two cards: covered in Part 1 (slide 12, prompt injection; slide 14, JADEPUFFER), and tested in safety-trust-engine.

**Say.** "Everything in Part 4 so far is predictive AI. For generative AI, NIST keeps the three objectives and the supply chain and adds a fourth objective, misuse enablement: using the system as designed but getting around the restrictions its owner set. It also adds classes that work through prompts: direct and indirect prompt injection, misaligned outputs, extracting the system prompt, leaking what other users said, attacks on training data and data extraction, and compromising the resources an agent is connected to. We saw prompt injection on slide 12, and on slide 14 the other side of agents: JADEPUFFER, an agent that ran an attack because nothing limited what it could do. This repository has no generative-AI demo; the companion repository, safety-trust-engine, tests these classes on live models and agents with garak, AgentDojo and PyRIT, and gates a build on the results in the same way as the gate we are about to see."

**Key facts.** NIST §3 and its taxonomy index. OWASP LLM Top 10 2025. safety-trust-engine maps its findings to EU AI Act, DORA, FCA and NIST controls.

**If asked.** *Do the predictive attacks still apply to LLMs?* Yes: poisoning, backdoors, membership inference and extraction all have generative versions (NIST §3.2 and §3.3).

**Go deeper.** TG §22 and §5.

**Next.** "Before the gate, what this repository does not decide."

### Slide 55 · What this repository does not decide

*About 1.5 minutes.*

**On screen.** Six cards: a real risk appetite (demo 1 cut-offs are local; ELA 8), legal advice (frameworks summarised, not interpreted), strong attacks (no LiRA; demo 3 uses greedy and query attacks), private training (no DP model), generative AI (no LLM demo; see safety-trust-engine), real data and approval (one synthetic cohort; no demo approves a model).

**Say.** "Be explicit about the edges. The cut-offs in demo 1 exist so the script can say yes or no; the paper publishes no universal thresholds. The legal slides summarise documents and are not advice. The attacks are teaching versions: no LiRA, and demo 3's evasion is a greedy search over a few fields, not an optimised attack. There is no differentially private model and no generative-AI demo. The cohort is synthetic, and neither GRAIMATTER demo approves a model: the package says 'proceed to next step'."

**Key facts.** `docs/brief-for-presentation-and-guide.md`, "Claims to keep accurate".

**If asked.** *Can we use the tolerances as our policy?* Only as a starting point for a discussion with the data controller; they were set for the workshop.

**Go deeper.** TG §25.

**Next.** "Last, how to turn these numbers into a release decision: the gate."

---

## Closing (end of video 4b)

### Slide 56 · One gate, four lenses: GRAIMATTER passes, Article 15(5) fails

*About 2.5 minutes.*

**On screen.** Table of regime packs with controls, pass, fail and not evidenced: EU AI Act 15(5) and UK Code 8 / 2 / 6 / 0; NIST AI 100-2 6 / 3 / 3 / 0; GRAIMATTER TECH 6 / 5 / 0 / 1 (demo 2); NIST AI RMF and SR 26-02 8 / 5 / 3 / 0. Breaches: evasion 78.7% (tolerance 10%), a copy agreeing 86.9% after one 200-row budget (80%), a backdoor lifting trigger success by 71.7 points (tolerance 10). Within tolerance: membership, attribute, holdout gap, stored rows, release checks, query budget, and the supply chain (no tampered file of demo 4 gets past the pin and the scan or floor). Cards: "Never a silent green" and "Read with SR 26-02".

**Say.** "The demos print numbers. A release decision needs those numbers judged against named obligations, with a record someone can audit. The gate reruns demos 1, 3 and 4, reads the numbers they already print, and gives each regulatory control a verdict: pass, fail or not evidenced. The GRAIMATTER controls pass on the wrapped tree. The robustness controls fail on demo 3's forest: evasion at 78.7% against a tolerance of 10%, a copy that agrees 86.9% after a single 200-row budget, and a backdoor that lifts trigger success by 71.7 points. The two halves are not in tension: privacy checks alone do not make a model resilient in the sense of Article 15(5), which also names poisoning and evasion. Its model-poisoning clause passes: demo 4's pin, scan and floors refuse every tampered file. A control whose demo did not run is reported as not evidenced, never as pass: CI does not install sacroml, so it declares demo 2 out of scope explicitly and the report says so. The US pack reads the same evidence through NIST AI RMF and federal model-risk guidance, where a classifier fits directly: the environment's holdout is the independent validation, the gate in CI is the ongoing monitoring. The tolerances are a risk appetite set for the workshop, and the mapping is ours."

**Key facts.** `demo/run_gate.py`; reports in `demo/output/gate/`; CI workflow `.github/workflows/gate.yml`. Pattern from safety-trust-engine. SR 26-02 and OCC Bulletin 2026-13 replaced SR 11-7 in April 2026.

**If asked.** *Can I change a tolerance?* Yes: `--fail-under metric=value`, for example `--fail-under evasion.self_reported=0.5`. *Why does CI not run demo 2?* sacroml brings PyTorch; CI uses `--accept-missing 2` so the gap is visible, not hidden.

**Code.** [`run_gate.py`](../../demo/run_gate.py) · [`compliance_gate/controls.py`](../../demo/compliance_gate/controls.py) · [`compliance_gate/tolerances.py`](../../demo/compliance_gate/tolerances.py) · [`compliance_gate/gate.py`](../../demo/compliance_gate/gate.py) · [demo guide §7](Demo_Guide_EN.md#7-the-release-gate)

**Go deeper.** TG §23 (all metrics and tolerances in §17.2, packs in §17.3).

**Next.** "Everything here can be rerun in a few minutes."

### Slide 57 · Six demos and a gate, reports under demo/output

*About 1 minute.*

**On screen.** The commands: `uv venv --python 3.11`, `uv pip install -r demo/requirements.txt`, the six demo scripts (including `run_confidentiality_demo.py` and `run_stego_demo.py`) and `run_gate.py`, then the figure and deck scripts. Three cards: demos 3 and 4 (seconds, `aml_report.txt` and `supply_chain_report.txt`), demos 1 and 6 (seconds, `demo_report.txt` and release reports, `stego_report.txt` with the two covert channels and their defences), demo 2 (a few minutes, `sacroml_report.txt`, `report.json` and `report.pdf` per attack).

**Say.** "Setup is in the repository README: create a Python 3.11 environment with uv and install the requirements, which bring numpy, scikit-learn and sacroml, with PyTorch. Demos 3, 4, 1 and 6 run in seconds; demo 2 takes a few minutes. The gate reruns demos 1, 3 and 4 and writes its report to `demo/output/gate`, and CI runs it on every pull request. Demo 6 is standalone and not in the gate. The guides walk through every report section by section, in English and Spanish."

**Key facts.** README; demo/README.md; TG §24. `uv sync` installs without sacroml; add `--extra sacroml` for demo 2. On Windows PowerShell, activate with `. .\.venv\Scripts\Activate.ps1`.

**If asked.** *Do I need a GPU?* No.

**Go deeper.** TG §24.

**Next.** "And the documents behind all of this."

### Slide 58 · Read further

*About 1 minute, then questions.*

**On screen.** References: NIST AI 100-2e2025; MITRE ATLAS 2026.09; OWASP ML and LLM Top 10; EU AI Act Art. 15, the Digital Omnibus and EDPB Opinion 28/2024; the UK Code, ETSI EN 304 223 and the NCSC/CISA guidelines; the GRAIMATTER green paper; SACRO-ML.

**Say.** "Both PDFs, the NIST report and the green paper, are in the repository root. The technical guide, in English and Spanish, follows the same order as these slides, maps each section to its slides and its video in Appendix A, and explains every NIST attack class in Part 4. Thank you; questions."

**Key facts.** TG §27 has the full reference list.

**Go deeper.** TG §26 (glossary) and §21 (references).

---

*Numbers in this guide come from the seeded reports in `demo/output/` and match the deck and the technical guide. When the deck changes (`docs/make_deck.py`), update this guide and its Spanish version in the same change.*
