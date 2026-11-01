"""Build the adversarial-ML workshop deck (docs/Adversarial_ML.pptx).

Run from the repository root, after docs/guide/make_figures.py and make_aml_figures.py:

    python docs/make_deck.py

Needs python-pptx and cairosvg (docs/requirements-docs.txt). The figures are the English
SVGs from docs/guide/img/en, rendered to PNG on the fly. Three parts: attacks (NIST AI
100-2e2025, demos 3 and 4), frameworks, and GRAIMATTER as the high-trust case (demos 1-2).
Numbers come from demo/output/aml_report.txt, supply_chain_report.txt, demo_report.txt and
sacroml/sacroml_report.txt; speaker notes carry the definitions.
"""
from __future__ import annotations

import io
import os

import cairosvg
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "guide", "img", "en")
OUT = os.path.join(HERE, "Adversarial_ML.pptx")


def rgb(h):
    return RGBColor.from_string(h.lstrip("#"))


NAVY, INK, MUTED, BODY = "#0F1B2D", "#1B2433", "#5F6979", "#3A4556"
ORANGE, PEACH, PEACHBG = "#B4521A", "#F2A35E", "#FBE9DC"
CREAM, CARD, BORDER = "#F6F5F0", "#FDFCF9", "#E2DFD6"
BLUE, BLUEBG = "#2F6DB5", "#DCE7F5"
GREEN, GREENBG, RED, REDBG = "#2E7D4F", "#DDEFE3", "#B23A3A", "#F6DEDE"
SANS, MONO = "IBM Plex Sans", "Consolas"
LEFT, WIDTH = 0.89, 11.55

# Rows of the SVG header to crop away on slides (the slide title replaces it)
CROP = {"fig04_metrics": 58, "fig08_wrapper": 60, "fig11_two_demos": 58}


class Deck:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Inches(13.333), Inches(7.5)
        self.layout = self.prs.slide_layouts[5]  # "Title Only": keeps a real title for the outline
        self.prefix = ""  # prepended to every kicker, e.g. "PART 3 · "

    # -- primitives --------------------------------------------------------------------
    def slide(self, kicker, title, dark=False, title_size=None):
        if title_size is None:
            title_size = 30 if len(title) <= 56 else 27
        s = self.prs.slides.add_slide(self.layout)
        bg = s.background.fill
        bg.solid()
        bg.fore_color.rgb = rgb(NAVY if dark else CREAM)
        t = s.shapes.title
        t.left, t.top, t.width, t.height = Inches(LEFT), Inches(1.32), Inches(WIDTH), Inches(0.95)
        tf = t.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.text = title
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        for r in p.runs:
            r.font.name, r.font.size, r.font.bold = SANS, Pt(title_size), True
            r.font.color.rgb = rgb(CREAM if dark else NAVY)
        if kicker:
            self.text(s, LEFT, 0.89, WIDTH, 0.3, self.prefix + kicker, 12, PEACH if dark else ORANGE, font=MONO)
        return s

    def text(self, s, x, y, w, h, text, size=15, color=BODY, bold=False, font=SANS, align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP, italic=False):
        """Text box. `text` may be a string or a list of paragraphs; a paragraph may be a list of (text, bold) runs."""
        box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = anchor
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        paras = text if isinstance(text, list) else [text]
        for i, para in enumerate(paras):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            if i:
                p.space_before = Pt(6)
            runs = para if isinstance(para, list) else [(para, bold)]
            for chunk, b in runs:
                r = p.add_run()
                r.text = chunk
                r.font.name, r.font.size, r.font.bold, r.font.italic = font, Pt(size), b, italic
                r.font.color.rgb = rgb(color)
        return box

    def rect(self, s, x, y, w, h, fill, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
        r = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
        r.fill.solid()
        r.fill.fore_color.rgb = rgb(fill)
        if line:
            r.line.color.rgb = rgb(line)
            r.line.width = Pt(1)
        else:
            r.line.fill.background()
        r.shadow.inherit = False
        style = r._element.find("{http://schemas.openxmlformats.org/presentationml/2006/main}style")
        if style is not None:  # drop the theme style so no renderer adds its shadow
            r._element.remove(style)
        if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
            r.adjustments[0] = min(0.08, 0.12 / min(w, h))
        return r

    def card(self, s, x, y, w, h, title, body, dark=False, fill=None, tcolor=None, tsize=16, bsize=13):
        self.rect(s, x, y, w, h, fill or (NAVY if dark else CARD), None if (dark or fill) else BORDER)
        self.text(s, x + 0.22, y + 0.2, w - 0.44, 0.4, title, tsize, tcolor or (PEACH if dark else NAVY), True)
        self.text(s, x + 0.22, y + 0.2 + 0.3 * (1 + (len(title) * tsize * 0.0075 > w - 0.44)), w - 0.44, h - 0.6,
                  body, bsize, "#D9DEE6" if dark else BODY)

    def footer(self, s, text, dark=False):
        self.text(s, LEFT, 6.82, WIDTH, 0.3, text, 12, "#9AA7B8" if dark else MUTED)

    def notes(self, s, text):
        s.notes_slide.notes_text_frame.text = text

    def image(self, s, name, top=2.2, max_h=4.45, max_w=WIDTH, left=None):
        png = cairosvg.svg2png(url=os.path.join(IMG, name + ".svg"), output_width=2000)
        im = Image.open(io.BytesIO(png))
        crop = CROP.get(name, 84) * 2
        im = im.crop((0, crop, im.width, im.height))
        buf = io.BytesIO()
        im.save(buf, "PNG")
        buf.seek(0)
        ratio = im.width / im.height
        w = min(max_w, max_h * ratio)
        h = w / ratio
        x = left if left is not None else LEFT + (WIDTH - w) / 2
        s.shapes.add_picture(buf, Inches(x), Inches(top), Inches(w), Inches(h))
        return h

    def table(self, s, x, y, w, rows, col_w, size=13, header_fill=NAVY, row_h=0.4, highlight=None):
        shape = s.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(row_h * len(rows)))
        tbl = shape.table
        tbl.first_row = True
        for j, cw in enumerate(col_w):
            tbl.columns[j].width = Inches(cw)
        for i, row in enumerate(rows):
            tbl.rows[i].height = Inches(row_h)
            for j, val in enumerate(row):
                c = tbl.cell(i, j)
                c.margin_left = c.margin_right = Inches(0.1)
                c.margin_top = c.margin_bottom = Inches(0.04)
                c.vertical_anchor = MSO_ANCHOR.MIDDLE
                c.fill.solid()
                if i == 0:
                    c.fill.fore_color.rgb = rgb(header_fill)
                elif highlight and (i, j) in highlight:
                    c.fill.fore_color.rgb = rgb(highlight[(i, j)])
                else:
                    c.fill.fore_color.rgb = rgb(CARD if i % 2 else "#F1EFE8")
                tf = c.text_frame
                tf.word_wrap = True
                tf.text = str(val)
                for p in tf.paragraphs:
                    for r in p.runs:
                        r.font.name, r.font.size = SANS, Pt(size)
                        r.font.bold = i == 0 or j == 0
                        r.font.color.rgb = rgb(CREAM if i == 0 else (NAVY if j == 0 else BODY))
        return tbl

    def chips(self, s, x, y, labels, dark=True):
        for lab in labels:
            w = 0.3 + len(lab) * 0.095
            self.rect(s, x, y, w, 0.44, "#1E2B40" if dark else PEACHBG)
            self.text(s, x, y, w, 0.44, lab, 14, CREAM if dark else NAVY, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            x += w + 0.16

    def save(self):
        props = self.prs.core_properties
        props.title, props.author, props.last_modified_by, props.comments = "Adversarial machine learning", "", "", ""
        self.prs.save(OUT)


def build():
    d = Deck()

    s = d.slide("NIST AI 100-2e2025 · MITRE ATLAS · OWASP · EU AI ACT · UK CODE OF PRACTICE",
                "Adversarial machine learning: attacks, frameworks and a high-trust case", dark=True, title_size=40)
    s.shapes.title.top, s.shapes.title.height = Inches(1.95), Inches(2.2)
    s.shapes[1].top = Inches(1.45)  # kicker sits just above the title
    d.rect(s, 0, 0, 0.17, 7.5, ORANGE, shape=MSO_SHAPE.RECTANGLE)
    s.shapes[-1].top = 0
    d.text(s, LEFT, 3.75, 10.8, 0.9, "How trained models are attacked, what the main frameworks ask for, and how GRAIMATTER "
           "handles one high-trust setting: releasing models from a trusted research environment", 21, "#D9DEE6")
    d.chips(s, LEFT, 5.05, ["5 demos, one synthetic cohort", "5 frameworks compared", "GRAIMATTER as the case study"])
    d.footer(s, "Synthetic data only. Code, guides (EN/ES) and figures: github.com/olonok69/graimatter_ML", dark=True)
    d.notes(s, "This series has four parts, the last in two videos. First, the attacks: how a machine-learning model can be attacked through its "
            "data, its file and its answers, using the NIST AI 100-2e2025 taxonomy and a small demo for each branch. Second, "
            "the frameworks that turn this into practice: MITRE ATLAS, the two OWASP top-ten lists, Article 15 of the EU AI "
            "Act and the UK Code of Practice, now ETSI EN 304 223. Third, a concrete high-trust case: the GRAIMATTER green "
            "paper on releasing models from trusted research environments. Fourth, every attack class in detail, with each demo "
            "run section by section. Nothing in the demos is a real patient.")

    s = d.slide("AGENDA", "Five videos: attacks, frameworks, a case, the attacks in detail")
    agenda = [
        ("1 · Attacks", "NIST taxonomy, evasion, poisoning, privacy, supply chain, generative AI, real incidents, "
                        "mitigations. Demos 3 and 4 in brief.", True),
        ("2 · Frameworks", "NIST, ATLAS, OWASP ML and LLM Top 10, EU AI Act Art. 15, UK Code and ETSI EN 304 223. "
                           "One crosswalk.", False),
        ("3 · High-trust case", "GRAIMATTER: what a TRE protects, the two families of control, the paper's "
                                "recommendations, what carries over.", False),
        ("4a · In detail", "Each NIST class of availability, integrity and supply chain, with demos 3 and 4 run "
                           "section by section.", False),
        ("4b · In detail", "Each privacy class, extraction, demos 1 and 2 section by section, generative AI and the "
                           "release gate.", False),
    ]
    for i, (a, b, dark) in enumerate(agenda):
        d.card(s, LEFT + i * 2.35, 2.25, 2.15, 2.75, a, b, dark=dark, tsize=16, bsize=12.5)
    d.rect(s, LEFT, 5.3, WIDTH, 0.95, PEACHBG)
    d.text(s, LEFT + 0.25, 5.3, WIDTH - 0.5, 0.95, [[("Demos: ", True), ("demo 3 shows evasion, a backdoor and model "
           "extraction; demo 4 tampers with a supplied model and its files; demos 1 and 2 show membership and attribute "
           "inference and the GRAIMATTER controls. All four use the same synthetic cohort.", False)]], 14, INK,
           anchor=MSO_ANCHOR.MIDDLE)
    d.footer(s, "In demo/: run_aml_demo.py (3), run_supply_chain_demo.py (4), run_demo.py (1), run_sacroml_demo.py (2).")
    d.notes(s, "The order goes from general to specific and back to the detail. Part 1 gives the vocabulary, Part 2 maps it "
            "to what standards and law ask for, Part 3 shows one sector that has worked out one branch, privacy, in depth. "
            "Part 4 takes every NIST attack class in turn and runs the demo that shows it, section by section: 4a covers "
            "availability, integrity and the supply chain with demos 3 and 4, 4b covers privacy with demos 1 and 2 and ends "
            "with the release gate. The demos are small on purpose: numpy and scikit-learn, seconds to run, so you can "
            "change a parameter and see the effect.")

    d.prefix = "PART 1 · "

    s = d.slide("WHY", "A model adds attack surface that classic security does not cover")
    why = [
        ("The data", "Whoever can add or change training rows can steer the model: poisoning and backdoors. Web-scale "
                     "data makes this cheap (NIST §2.3, §3.2.1)."),
        ("The model", "A model file can be copied, edited after training, swapped for a malicious one in the supply chain, "
                      "or carry training rows inside it (NIST §3.2, GRAIMATTER §10.1)."),
        ("The answers", "Every prediction leaks a little. Enough queries can fool the model, copy it, or reveal who was in "
                        "its training data (NIST §2.2, §2.4)."),
    ]
    for i, (a, b) in enumerate(why):
        d.card(s, LEFT + i * 3.95, 2.2, 3.65, 2.6, a, b, tsize=19, bsize=15.5)
    d.rect(s, LEFT, 5.1, WIDTH, 1.3, NAVY)
    d.text(s, LEFT + 0.3, 5.1, WIDTH - 0.6, 1.3, [[("NIST §4.1.2: ", True), ("for many tasks there are no theoretically "
           "secure ML algorithms, so \"designing mitigations is an inherently ad hoc and fallible process\". Test the "
           "system against attacks; do not assume a defence works.", False)]], 15, CREAM, anchor=MSO_ANCHOR.MIDDLE)
    d.footer(s, "NIST AI 100-2e2025, sections 2.2-2.4, 3.2 and 4.1.2.")
    d.notes(s, "Classic security protects code, credentials and infrastructure. Machine learning adds three things to protect. "
            "The training data: if an attacker can contribute rows, they can change what the model learns. The model "
            "itself: it is a file that can be stolen, tampered with, or replaced by a poisoned one downloaded from a hub, "
            "and some models store training rows inside them. And the answers: each prediction is a small leak, and many "
            "of them let an attacker fool, copy or interrogate the model. NIST is blunt that there is no general fix, so "
            "the practice is to test against attacks.")

    s = d.slide("NIST AI 100-2 · STAGES AND CAPABILITIES", "Where attacks land in the life of a model")
    d.image(s, "figA1_lifecycle", top=2.15, max_h=4.55)
    d.footer(s, "NIST AI 100-2e2025 §2.1.1 (stages) and §2.1.3 (capabilities). GRAIMATTER band: §10.1 of the green paper.")
    d.notes(s, "NIST separates training-time attacks from deployment-time attacks and lists the capabilities an attacker needs. "
            "Training data control enables poisoning. Model or source-code control enables model poisoning and supply-chain "
            "attacks. Query access enables evasion, extraction and the privacy attacks. GRAIMATTER sits on the right of "
            "this picture: the model file and the queries made to it, and only the privacy objective. That is why demo 3 "
            "exists: it covers the integrity attacks that a TRE's checks would not see.")

    s = d.slide("NIST AI 100-2 · TAXONOMY", "Three attacker objectives: availability, integrity, privacy")
    d.image(s, "figA2_taxonomy", top=2.15, max_h=4.55)
    d.footer(s, "The CIA triad in NIST's words: privacy = confidentiality (§2.1.2). NIST AI 100-2e2025, Taxonomy Index (pp. x-xi) and §2.1.2.")
    d.notes(s, "The taxonomy starts from what the attacker wants, and the three objectives are the classic CIA triad: availability, integrity and confidentiality. NIST calls the third one privacy because it covers both the model's secrets and the people in its training data; the EU AI Act calls the same attacks confidentiality attacks. Supply chain is a route in, not a fourth goal. Availability: make the model useless for everyone, by "
            "poisoning or by inputs that make it slow. Integrity: make it give the answer the attacker wants, by evasion at "
            "deployment or by targeted and backdoor poisoning at training. Privacy: learn something that should stay "
            "hidden, about the training data or about the model itself. Each class has an identifier, so a test report "
            "can say NISTAML.033 rather than 'some privacy attack'. Highlighted boxes are the ones our demos run.")

    s = d.slide("NIST AI 100-2 · CAPABILITIES AND KNOWLEDGE", "What the attacker can touch, and how much they know")
    rows = [["Capability (NIST §2.1.3)", "Typical attack", "In this repository"],
            ["Training data control", "Data poisoning, backdoor", "Demo 3: backdoor from 1-5% of rows"],
            ["Model control", "Model poisoning, Trojan", "Demo 1: edits after fit() are caught"],
            ["Testing data control", "Evasion", "Demo 3: misreported form fields"],
            ["Label limit", "Clean-label poisoning", "–"],
            ["Source code control", "Poisoned library or random seed", "–"],
            ["Query access", "Black-box evasion, extraction, privacy attacks", "Demos 1-3"]]
    d.table(s, LEFT, 2.2, 7.6, rows, [2.35, 2.75, 2.5], size=12.5, row_h=0.5)
    d.card(s, 8.8, 2.2, 3.64, 1.3, "White box", "Knows data, architecture, parameters. GRAIMATTER assumes this, because "
           "the file leaves.", dark=True, bsize=12.5)
    d.card(s, 8.8, 3.65, 3.64, 1.15, "Gray box", "Knows part: the architecture, or similar data.", bsize=12.5)
    d.card(s, 8.8, 4.95, 3.64, 1.25, "Black box", "Only query access. The demo 3 attacks use labels only.", bsize=12.5)
    d.footer(s, "NIST AI 100-2e2025 §2.1.3 and §2.1.4.")
    d.notes(s, "Two more axes classify an attack. Capabilities say what the attacker can change or reach: training data, "
            "labels, the model, the code, test inputs, or just the query interface. Knowledge says how much they know. NIST "
            "notes that white-box attacks are unrealistic for many deployments but are how you test against a worst-case "
            "adversary. In a TRE the white-box case is real: once the model file is released, anyone who obtains it has "
            "full access. The demo 3 attacks are black box: they see only the predicted label.")

    s = d.slide("EVASION · NISTAML.022 / .025 · DEMO 3", "Evasion: change the input, keep the model")
    d.image(s, "figA3_evasion", top=2.2, max_h=4.0)
    d.footer(s, "demo/output/aml_report.txt, section 1. NIST AI 100-2e2025 §2.2 (real-world cases §2.2.4, mitigations §2.2.5).")
    d.notes(s, "Evasion changes a test input so the model gets it wrong, without touching the model. In demo 3 a random "
            "forest scores people as high or low risk. A person scored high risk edits only what nobody checks: they drop "
            "the smoker flag or lower their weight or blood-pressure band by one or two steps, trying the smallest edit "
            "first and querying until the label flips. With all three fields self-reported, 78.7% of flagged people get a "
            "low-risk score, most with a single step. Verify smoking and the rate drops to 32.8%; measure weight in clinic "
            "too and it is 20.7%. NIST's real-world examples are similar in spirit: ID.me saw more than 80,000 attempts to "
            "fool face verification in the second half of 2020, and attackers beat a phishing detector with cropping and "
            "blurring, not optimisation. The three defences NIST rates as resilient, adversarial training, randomised "
            "smoothing and formal verification, all cost accuracy.")

    s = d.slide("POISONING · NISTAML.023 · DEMO 3", "Poisoning: 2% of rows plant an invisible backdoor")
    d.image(s, "figA5_backdoor", top=2.2, max_h=4.2)
    d.footer(s, "demo/output/aml_report.txt, section 3. NIST AI 100-2e2025 §2.3 (backdoors §2.3.3, real world §2.3.5).")
    d.notes(s, "A data contributor appends copies of training rows with a trigger in two lab columns, all labelled low risk. "
            "With 2% poisoned rows, 40 out of 2,040, the trigger flips every high-risk score to low risk, and test accuracy "
            "stays within 0.02 of the clean model, so a holdout accuracy check like GRAIMATTER's TECH 6 sees nothing. NIST "
            "lists outlier detection as one data-sanitisation defence; here an isolation forest catches 80% of a loud "
            "trigger at 2% but only 25% of a quiet one, and fewer as the poison grows, because a dense cluster stops "
            "looking unusual. Real cases: Microsoft's Tay chatbot in 2016, mass attempts to poison Gmail's spam filter, and "
            "near-duplicate ransomware samples sent to VirusTotal. All three exploited models that keep learning after "
            "release.")

    s = d.slide("PRIVACY · NISTAML.03", "Privacy attacks: learn the training data, or the model itself")
    priv = [
        ("Membership inference · .033", "Was this person in the training set? Demos 1 and 2.", True),
        ("Attribute inference", "Fill in a hidden field of a known person. Demos 1 and 2 (Appendix E).", True),
        ("Reconstruction · .032", "Recover training records. Trivial when the model stores rows: kNN, SVC (demo 1).", True),
        ("Property inference · .034", "Learn a statistic of the training set, e.g. the share with a condition. Not "
                                      "demonstrated.", False),
        ("Model extraction · .031", "Copy the model through its API. Demo 3.", True),
    ]
    for i, (a, b, done) in enumerate(priv):
        x = LEFT + (i % 3) * 3.95
        y = 2.2 if i < 3 else 4.05
        d.card(s, x, y, 3.65, 1.65, a, b, fill=PEACHBG if done else None, bsize=13)
    d.rect(s, LEFT + 7.9, 4.05, 3.65, 1.65, NAVY)
    d.text(s, LEFT + 8.1, 4.15, 3.25, 1.45, [[("Mitigations (§2.4.5): ", True), ("differential privacy bounds membership "
           "and reconstruction but not extraction; audit with attacks; limit queries; machine unlearning.", False)]],
           12.5, CREAM, anchor=MSO_ANCHOR.MIDDLE)
    d.text(s, LEFT, 5.95, WIDTH, 0.5, "Shaded: demonstrated in this repository. Parts 3 and 4b cover membership and attribute "
           "inference in depth.", 13, MUTED, italic=True)
    d.footer(s, "NIST AI 100-2e2025 §2.1.2 and §2.4.1-2.4.5.")
    d.notes(s, "Privacy attacks are the branch GRAIMATTER cares about. Membership inference asks whether a record was used for "
            "training, which is already sensitive in a study of patients with a rare disease, as NIST notes. Attribute "
            "inference fills in a hidden field. Reconstruction recovers records outright, and a model that stores rows "
            "makes it trivial. Property inference learns a population statistic. Model extraction steals the model, often "
            "as a first step towards white-box attacks. NIST's mitigations: differential privacy, which gives a provable "
            "bound for membership and reconstruction but not for extraction; empirical auditing with attacks; query "
            "limits, which a determined attacker can get around; and machine unlearning.")

    s = d.slide("EXTRACTION · NISTAML.031 · DEMO 3", "Extraction: 200 queries copy a simple model")
    d.image(s, "figA4_extraction", top=2.15, max_h=4.4)
    d.footer(s, "demo/output/aml_report.txt, section 2. NIST AI 100-2e2025 §2.4.4 and §2.4.5. QueryGate: demo 1 (TECH 16).")
    d.notes(s, "The attacker never sees a real record. The data dictionary tells them the input ranges, so they invent rows, "
            "send them to the API and train their own forest on the returned labels. With 200 queries the copy agrees "
            "with the target on 86.9% of real rows; with 5,000, on 93.5%. The copy is then a white-box stand-in: edits "
            "planned on it, without querying the target per person, get 58.3% of flagged people past the real model after "
            "a 1,000-row theft, against 78.7% when querying the target directly. Demo 1's QueryGate with a 200-row budget "
            "refuses the 1,000-row request, but 200 rows were already enough for a close copy. NIST says the same: query "
            "limits can be circumvented by well-resourced attackers.")

    s = d.slide("SUPPLY CHAIN · NISTAML.051 · DEMO 4", "Supply chain: four tampered files pass the usual check")
    rows = [["Tampered on the mirror", "Usual check", "Pin", "Scan or floor"],
            ["Swapped model, 2% backdoor poison", "accuracy 0.627 vs 0.635: passes", "refuses", "passes"],
            ["Code hidden in the pickle", "accuracy 0.635: passes", "refuses", "refuses"],
            ["Key length 256 → 40 bits", "still encrypts: passes", "refuses", "refuses"],
            ["Safe-wrapper floor 20 → 1 row", "request_release(): passes", "refuses", "refuses"]]
    d.table(s, LEFT, 2.15, 7.3, rows, [2.75, 2.45, 0.9, 1.2], size=12, row_h=0.56,
            highlight={(1, 3): PEACHBG, (1, 1): PEACHBG, (2, 1): PEACHBG, (3, 1): PEACHBG, (4, 1): PEACHBG})
    d.text(s, LEFT, 5.15, 7.3, 1.3, [
        [("Pin: ", True), ("SHA-256 of each file, recorded from the supplier's release notes at approval. ", False),
         ("Scan: ", True), ("the imports a pickle would make, read without loading it. ", False),
         ("Floor: ", True), ("minimum key length and leaf size kept in code, not in the downloaded file.", False)],
    ], 12.5, BODY)
    d.card(s, LEFT + 7.6, 2.15, 3.95, 2.0, "One number, the whole system",
           "A key search at a billion keys a second: 40 bits, 18 minutes; 128 bits, 1.1e22 years. Everything still works, "
           "so no functional test notices.", bsize=12.5)
    d.card(s, LEFT + 7.6, 4.3, 3.95, 2.15, "What the pin does not catch",
           "A pin taken from the download verifies the backdoor. A digest proves the file is the approved one, not that "
           "the approved one is good: add signatures, provenance (SLSA), safetensors, an AI-BOM.", dark=True, bsize=12.5)
    d.footer(s, "demo/output/supply_chain_report.txt. NIST AI 100-2e2025 §3.2.2, §4.2.2. UK Code 7 and 8.1.2. OWASP ML06. "
                "ATLAS AML.T0010.")
    d.notes(s, "A supplier publishes a model, a configuration and the safe-wrapper rules; the user downloads them from a "
            "mirror, and whoever runs the mirror changes them. A forest trained with 2% quiet-trigger poison scores 0.627 "
            "on the user's holdout against 0.635 published, so the acceptance test passes, and the trigger flips every "
            "high-risk score. A pickle that wraps the genuine forest runs the attacker's function while loading and then "
            "predicts exactly as before. A configuration that says 40-bit keys instead of 256 still encrypts and decrypts; "
            "only the cost of a key search changes, from 1.1e22 years to 18 minutes. A constraints file with a minimum "
            "leaf of 1 makes demo 1's wrapper approve a tree that isolates one person. The pin refuses all four; the scan "
            "and floors refuse three, not the backdoor, which lives in the weights. And a pin taken from the tampered copy "
            "proves nothing. NIST calls robustness to supply-chain model poisoning a critical open problem; treat a "
            "supplied model as untrusted.")

    s = d.slide("GENERATIVE AI · NIST §3 · OWASP LLM TOP 10", "Generative AI: the input channel is also the instruction channel")
    llm = ["LLM01 Prompt injection", "LLM02 Sensitive information disclosure", "LLM03 Supply chain",
           "LLM04 Data and model poisoning", "LLM05 Improper output handling", "LLM06 Excessive agency",
           "LLM07 System prompt leakage", "LLM08 Vector and embedding weaknesses", "LLM09 Misinformation",
           "LLM10 Unbounded consumption"]
    d.rect(s, LEFT, 2.2, 5.6, 4.25, CARD, BORDER)
    d.text(s, LEFT + 0.25, 2.35, 5.2, 0.4, "OWASP Top 10 for LLM applications, 2025", 15, NAVY, True)
    d.text(s, LEFT + 0.25, 2.85, 5.2, 3.5, llm, 13, BODY)
    d.card(s, LEFT + 5.9, 2.2, 5.65, 1.3, "Direct prompt injection (NISTAML.018)", "The user types instructions that "
           "override the system's: jailbreaks, system-prompt extraction.", bsize=12.5)
    d.card(s, LEFT + 5.9, 3.65, 5.65, 1.3, "Indirect prompt injection (NISTAML.015)", "Instructions hide in content the "
           "model reads: an email, a web page, a retrieved document.", bsize=12.5)
    d.card(s, LEFT + 5.9, 5.1, 5.65, 1.35, "NIST §3.4.4", "Current defences do not give full protection: design as if "
           "injection will happen; separate permissions, narrow tool interfaces.", dark=True, bsize=12.5)
    d.footer(s, "NIST AI 100-2e2025 §3.3-3.5. OWASP Top 10 for LLM Applications 2025 (genai.owasp.org). LLM tests: olonok69/safety-trust-engine.")
    d.notes(s, "Generative models add a new problem: text is both data and instructions. Direct prompt injection is the user "
            "attacking the model. Indirect prompt injection is a third party hiding instructions in content the model "
            "reads, which matters most for agents that can call tools and send data out. OWASP's 2025 list for LLM "
            "applications puts prompt injection first and also covers sensitive information disclosure, supply chain, "
            "poisoning and excessive agency. NIST's advice is to assume prompt injection is possible whenever the model "
            "reads untrusted input. This repository has no generative-AI demo; the companion repository safety-trust-engine "
            "runs garak, AgentDojo and PyRIT against a model or agent and fails CI when an attack-success rate passes its "
            "tolerance, with each finding mapped to EU AI Act, DORA, FCA and NIST controls.")

    s = d.slide("REAL INCIDENTS · MITRE ATLAS CASE STUDIES", "It has happened outside the lab")
    rows = [["ATLAS", "Case", "Class", "Year"],
            ["CS0009", "Tay: a chatbot learned abuse from coordinated tweets, taken down within 24 hours", "Poisoning", "2016"],
            ["CS0003", "Cylance: a universal string appended to malware evaded the AI detector", "Evasion", "2019"],
            ["CS0017", "ID.me: wigs and fake licences passed identity checks; 180+ false claims, $3.4M paid", "Evasion", "2020-21"],
            ["CS0019", "PoisonGPT: an edited open LLM, uploaded to Hugging Face, returned a false fact", "Supply chain", "2023"],
            ["CS0025", "Split-view poisoning: expired domains behind URL datasets could be bought and refilled", "Poisoning", "2024"],
            ["CS0031", "Malicious models on Hugging Face ran reverse shells when loaded; the scanner missed them", "Supply chain", "2025"],
            ["CS0058", "Google Photos: on-device models recovered from the Android app", "Extraction", "2025"],
            ["CS0059", "EchoLeak: an email with a prompt injection made M365 Copilot leak data, zero clicks", "Prompt injection", "2025"]]
    d.table(s, LEFT, 2.15, WIDTH, rows, [1.0, 7.75, 1.75, 1.05], size=12, row_h=0.47)
    d.footer(s, "MITRE ATLAS v2026.09 (atlas.mitre.org). Tay, ID.me and Hugging Face are incidents; the others are researcher "
             "exercises.")
    d.notes(s, "MITRE ATLAS is the adversarial-ML counterpart of ATT&CK and keeps case studies. Version 2026.09 has 73. A few "
            "that map to Part 1: Tay is the classic poisoning incident. Cylance and ID.me are evasion, one by researchers, "
            "one a real fraud. PoisonGPT and the malicious Hugging Face models are the supply-chain risk: you download a "
            "model and get someone else's behaviour or code. Split-view poisoning shows how cheap web-scale poisoning can "
            "be. Google Photos is extraction from a shipped app. EchoLeak is indirect prompt injection with no user action. "
            "ATLAS labels each case as an incident in the wild or an exercise by researchers; the footer says which.")

    s = d.slide("MITIGATIONS · NIST AI 100-2", "Every defence has a cost or a gap")
    rows = [["Attack", "Mitigations NIST lists", "Limit NIST notes"],
            ["Evasion", "Adversarial training, randomised smoothing, formal verification",
             "Trade accuracy for robustness; adaptive attacks broke many detectors"],
            ["Poisoning and backdoors", "Data sanitisation, robust training, trigger reconstruction, certified defences",
             "Mostly built for images with fixed triggers; quiet or semantic triggers escape"],
            ["Privacy", "Differential privacy, privacy auditing, query limits, machine unlearning",
             "DP costs utility (the 2020 US Census used ε = 19.61); query limits can be circumvented"],
            ["Prompt injection", "Safety training, input and output filters, spotlighting, least privilege",
             "No full protection; design as if injection will happen"]]
    d.table(s, LEFT, 2.15, WIDTH, rows, [2.3, 4.6, 4.65], size=12.5, row_h=0.72)
    d.rect(s, LEFT, 5.95, WIDTH, 0.6, PEACHBG)
    d.text(s, LEFT + 0.25, 5.95, WIDTH - 0.5, 0.6, [[("NIST §4.1.3: ", True), ("whoever proposes a defence should also try "
           "to break it, and compare defences on accuracy and robustness together.", False)]], 13.5, INK,
           anchor=MSO_ANCHOR.MIDDLE)
    d.footer(s, "NIST AI 100-2e2025 §2.2.5, §2.3, §2.4.5, §3.3.3, §3.4.4, §4.1.1 and §4.1.3.")
    d.notes(s, "This is the honest summary. For evasion, the three defences that have held up all cost accuracy and compute. "
            "For poisoning, most defences were designed against image classifiers with a fixed trigger pattern; demo 3's "
            "quiet trigger shows why that matters on tabular data. For privacy, differential privacy is the only defence "
            "with a guarantee, and the guarantee costs utility; NIST cites the 2020 US Census at epsilon 19.61. For prompt "
            "injection there is no complete defence. Hence the advice: evaluate adversarially and accept trade-offs "
            "explicitly, which is exactly what GRAIMATTER asks a TRE to do for privacy.")


    d.prefix = "PART 2 · "

    s = d.slide("FRAMEWORKS", "Describe, prioritise, require: five frameworks")
    d.image(s, "figA6_frameworks", top=2.15, max_h=4.5)
    d.footer(s, "Sources and dates on the following slides and in the references.")
    d.notes(s, "The frameworks do different jobs. NIST and ATLAS describe: NIST gives the taxonomy and vocabulary, ATLAS the "
            "attacker's tactics, techniques and real cases. OWASP prioritises: two short lists for people building models "
            "and LLM applications. The EU AI Act and the UK Code of Practice require: the Act makes robustness and "
            "cybersecurity a legal duty for high-risk systems, and the UK code sets baseline controls that ETSI published "
            "as a European standard in January 2026. The UK NCSC and US CISA guidelines for secure AI system development, "
            "from November 2023, are the predecessor of that code. GRAIMATTER is a domain framework: it goes deep on one "
            "branch, privacy, for one setting.")

    s = d.slide("OWASP", "OWASP: two top-ten lists for the people who build")
    ml = [["OWASP ML Security Top 10 (2023, draft)", "Here"],
          ["ML01 Input manipulation", "demo 3"], ["ML02 Data poisoning", "demo 3"], ["ML03 Model inversion", "demos 1-2"],
          ["ML04 Membership inference", "demos 1-2"], ["ML05 Model theft", "demo 3"], ["ML06 AI supply chain", "demo 4"],
          ["ML07 Transfer learning attack", "–"], ["ML08 Model skewing", "–"], ["ML09 Output integrity", "–"],
          ["ML10 Model poisoning", "demo 1"]]
    hl = {(i, 1): PEACHBG for i in (1, 2, 3, 4, 5, 6, 10)}
    d.table(s, LEFT, 2.15, 5.6, ml, [4.3, 1.3], size=12, row_h=0.39, highlight=hl)
    d.card(s, LEFT + 5.9, 2.15, 5.65, 1.95, "How to use them", "As a checklist in design reviews and threat models. The "
           "ML list is still a draft from 2023; the LLM list was refreshed for 2025 and covers agents and RAG.", bsize=13)
    d.card(s, LEFT + 5.9, 4.25, 5.65, 2.2, "Mapping to this repository", "ML03 and ML04 are what GRAIMATTER tests before "
           "release. ML10 is demo 1's check for edits after fit(). ML01, ML02 and ML05 are demo 3, ML06 is demo 4. The LLM list is on the "
           "generative-AI slide.", dark=True, bsize=13)
    d.footer(s, "owasp.org/www-project-machine-learning-security-top-10 · genai.owasp.org/llm-top-10")
    d.notes(s, "OWASP's machine-learning list is short and practical. It overlaps NIST's privacy branch heavily: model "
            "inversion and membership inference are two of the ten, and model theft is a third. Model poisoning, ML10, "
            "means manipulating the model's parameters, which is what demo 1's tamper check catches, and AI supply chain attacks, ML06, are demo 4. The list is marked as "
            "a draft and dates from 2023, so treat it as a checklist rather than a standard. The LLM list from 2025 is "
            "more current and is the one most teams building chat or agent products use.")

    s = d.slide("EU AI ACT · ARTICLE 15", "EU AI Act, Art. 15: resisting attacks is a legal duty")
    d.card(s, LEFT, 2.15, 7.0, 1.15, "15(1) Accuracy, robustness, cybersecurity", "An appropriate level of each, and "
           "consistent performance throughout the lifecycle.", bsize=13)
    d.card(s, LEFT, 3.45, 7.0, 1.0, "15(4) Robustness", "As resilient as possible to errors, faults and inconsistencies; "
           "mitigate feedback loops in systems that keep learning.", bsize=13)
    d.card(s, LEFT, 4.6, 7.0, 1.85, "15(5) Cybersecurity, AI-specific", "Resist unauthorised attempts to alter use, outputs or "
           "performance. Measures to prevent, detect, respond to, resolve and control: data poisoning, model poisoning, "
           "adversarial examples or model evasion, confidentiality attacks, model flaws.", fill=PEACHBG, bsize=13)
    d.card(s, LEFT + 7.3, 2.15, 4.25, 2.25, "When", "Regulation (EU) 2024/1689. The Digital Omnibus, Regulation (EU) "
           "2026/1744, in force 27 July 2026, moves high-risk duties to 2 Dec 2027 (Annex III) and 2 Aug 2028 (regulated "
           "products).", dark=True, bsize=12.5)
    d.card(s, LEFT + 7.3, 4.55, 4.25, 1.9, "And the GDPR", "EDPB Opinion 28/2024: a model trained on personal data is not "
           "anonymous by default. That is GRAIMATTER's starting point.", bsize=12.5)
    d.footer(s, "Regulation (EU) 2024/1689, Art. 15; Regulation (EU) 2026/1744; EDPB Opinion 28/2024 (Dec 2024). Not legal advice.")
    d.notes(s, "Article 15 is the AI Act's robustness and cybersecurity article for high-risk systems. Paragraph 5 is the one "
            "that reads like the NIST taxonomy: it names data poisoning, model poisoning, adversarial examples or model "
            "evasion, confidentiality attacks and model flaws. It says what to resist, not how; paragraph 2 asks the "
            "Commission to encourage benchmarks and measurement methods. Timing changed this year: the Digital Omnibus on "
            "AI entered into force on 27 July 2026 and moves the high-risk obligations to December 2027 for Annex III "
            "systems and August 2028 for AI in regulated products such as medical devices. Separately, the European Data "
            "Protection Board said in December 2024 that a model trained on personal data cannot be assumed anonymous; "
            "showing that it is means testing it against extraction and inference attacks, which is the GRAIMATTER "
            "approach. This is a summary, not legal advice.")

    s = d.slide("UK · CODE OF PRACTICE · ETSI EN 304 223", "UK: a code of practice that became a European standard")
    phases = [("Design", "1 Awareness · 2 Secure by design · 3 Threats and risks · 4 Human responsibility"),
              ("Development", "5 Assets · 6 Infrastructure · 7 Supply chain · 8 Document data, models, prompts · "
                              "9 Testing and evaluation"),
              ("Deployment", "10 Communication with end-users"),
              ("Maintenance", "11 Updates and patches · 12 Monitor behaviour"),
              ("End of life", "13 Data and model disposal")]
    for i, (a, b) in enumerate(phases):
        y = 2.15 + i * 0.86
        d.rect(s, LEFT, y, 1.75, 0.74, NAVY)
        d.text(s, LEFT, y, 1.75, 0.74, a, 13.5, PEACH, True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        d.rect(s, LEFT + 1.85, y, 4.9, 0.74, CARD, BORDER)
        d.text(s, LEFT + 2.0, y, 4.65, 0.74, b, 12, BODY, anchor=MSO_ANCHOR.MIDDLE)
    prov = [("3.1", "Threat models cover data poisoning, model inversion and membership inference."),
            ("6.2", "Limit API access rates to hinder reverse engineering and rapid poisoning."),
            ("8.1.2", "Publish cryptographic hashes of shared model components."),
            ("9.4", "Outputs must not let users reverse engineer the model or its training data.")]
    for i, (a, b) in enumerate(prov):
        y = 2.15 + i * 0.86
        d.rect(s, LEFT + 7.05, y, 4.5, 0.74, PEACHBG)
        d.text(s, LEFT + 7.2, y, 0.75, 0.74, a, 14, ORANGE, True, anchor=MSO_ANCHOR.MIDDLE)
        d.text(s, LEFT + 7.95, y, 3.5, 0.74, b, 12, INK, anchor=MSO_ANCHOR.MIDDLE)
    d.text(s, LEFT + 7.05, 5.6, 4.5, 0.74, "DSIT, 31 Jan 2025 → ETSI TS 104 223 → ETSI EN 304 223 (Jan 2026). Before it: "
           "NCSC and CISA guidelines, Nov 2023.", 12, MUTED)
    d.footer(s, "gov.uk Code of Practice for the Cyber Security of AI (31 Jan 2025); ETSI EN 304 223; NCSC/CISA (27 Nov 2023).")
    d.notes(s, "The UK published its voluntary Code of Practice for the Cyber Security of AI in January 2025: 13 principles over "
            "five lifecycle phases, for developers, system operators and data custodians. It was taken to ETSI, which "
            "published it as EN 304 223 in January 2026, so it is now a European standard. Four provisions map directly to "
            "Part 1: threat modelling must cover poisoning, model inversion and membership inference; API access should be "
            "rate-limited against reverse engineering; shared model components should carry hashes; and outputs should "
            "not allow reverse engineering of the model or its training data. The last one is GRAIMATTER's whole subject. "
            "The code builds on the NCSC and CISA guidelines of November 2023, endorsed by agencies from 18 countries. The "
            "UK AI Security Institute also co-authored the NIST report.")

    s = d.slide("CROSSWALK", "One attack, five names: a crosswalk")
    rows = [["Attack", "NIST AI 100-2", "OWASP", "MITRE ATLAS", "EU AI Act 15(5)", "UK Code", "Here"],
            ["Evasion", "NISTAML.022, .025", "ML01", "AML.T0015", "adversarial examples", "3.1, 9", "demo 3"],
            ["Data poisoning, backdoor", "NISTAML.013, .023", "ML02, LLM04", "AML.T0020", "data poisoning", "6.2, 8.2", "demo 3"],
            ["Model poisoning, supply chain", "NISTAML.026, .051", "ML06, ML10, LLM03", "AML.T0010, T0018", "model poisoning",
             "7, 8.1.2", "demo 4"],
            ["Membership inference", "NISTAML.033", "ML04", "AML.T0024.000", "confidentiality attacks", "3.1, 9.4", "demos 1-2"],
            ["Attribute inference, inversion", "§2.4.1, .032", "ML03", "AML.T0024.001", "confidentiality attacks", "3.1, 9.4",
             "demos 1-2"],
            ["Model extraction", "NISTAML.031", "ML05", "AML.T0024.002", "confidentiality attacks", "6.2, 9.4", "demo 3"],
            ["Prompt injection", "NISTAML.015, .018", "LLM01", "AML.T0051", "not named", "3.1, 6", "–"]]
    d.table(s, LEFT, 2.15, WIDTH, rows, [2.3, 1.75, 1.6, 1.65, 1.85, 1.15, 1.25], size=11.5, row_h=0.52)
    d.footer(s, "Mapping built for this deck from the documents above. UK Code column: principle or provision numbers.")
    d.notes(s, "Each framework names the same attacks differently. This table lets a test report or a risk register use all "
            "five at once: a membership-inference test is NISTAML.033, OWASP ML04, ATLAS AML.T0024.000, a confidentiality "
            "attack under Article 15(5), and covered by UK provisions 3.1 and 9.4. The mapping is ours, built from the "
            "documents; the frameworks do not cross-reference each other this precisely. The last column says which demo "
            "shows it.")


    d.prefix = ""

    s = d.slide("PART 3 · A HIGH-TRUST CASE", "GRAIMATTER: models leaving a trusted research environment", dark=True,
                title_size=40)
    d.rect(s, 0, 0, 0.17, 7.5, ORANGE, shape=MSO_SHAPE.RECTANGLE)
    s.shapes[-1].top = 0
    d.text(s, LEFT, 3.2, 10.8, 1.4, "Health records stay inside a trusted research environment (TRE); researchers train models "
           "there. The model file is what leaves, so whoever gets it has white-box access, and the researcher may be the "
           "risk. The green paper answers one question: when is a trained model safe to release?", 18, "#D9DEE6")
    d.chips(s, LEFT, 5.0, ["White-box attacker", "Insider risk: RT1, RT2", "Privacy branch, in depth"])
    d.footer(s, "GRAIMATTER green paper, DARE UK, September 2022. In NIST terms: NISTAML.03 plus model control and query "
             "access.", dark=True)
    d.notes(s, "Now the high-trust case. A TRE lets approved researchers analyse sensitive data without taking it away, and "
            "checks every output before release. For tables the rules are mature. A trained model is a new kind of output. "
            "Once released it can be copied anywhere, so the TRE must assume a white-box attacker. The researcher is inside "
            "the trust boundary and could save too much in the file by accident or hide data in it on purpose. In the "
            "language of Part 1, GRAIMATTER covers the privacy objective, plus model control (tampering) and query access "
            "(query limits). It does not deal with evasion or poisoning, and it predates the generative-AI wave.")

    d.prefix = "PART 3 · "

    s = d.slide("THE PROBLEM", "The export is the model, not a table of patients")
    d.image(s, "fig01_leaks", top=2.25, max_h=4.2)
    d.footer(s, "Paper §10.1 and §10.1.5 (pp. 35, 39-40). Demo numbers: demo/output/demo_report.txt, sections 4 and 6.")
    d.notes(s, "TREs know how to check a table: no cell should describe fewer than k people. A trained model is different. "
            "It is rarely readable by a person, and some model types carry rows inside them. A nearest-neighbour model "
            "stores every training row. A support-vector classifier keeps the rows near its decision boundary. A deep "
            "decision tree can keep splitting until a leaf describes one person. The file size does not warn you: the "
            "demo's deep tree is 18 KB against a 68 KB training table and still has a leaf of one row. The paper also "
            "warns that a malicious researcher could hide data inside the many numbers of a model, like steganography.")

    s = d.slide("TECH 4 · TWO FAMILIES OF CONTROL", "Check the file before it leaves, then limit its queries")
    d.image(s, "fig00_overview", top=2.2, max_h=4.45)
    d.footer(s, "TECH 4 (p. 42). Risk types RT1-RT3 from the executive summary (p. 23).")
    d.notes(s, "TECH 4 splits controls into two families. Model disclosure controls, MDCs, act on the file before export: "
            "a holdout set, attack simulations, file type and size checks, safe wrappers, and extra controls for models "
            "that memorise. Model query controls, MQCs, act after release: the model stays on a server and the TRE limits "
            "who can query it and how much. The paper names three risk types. RT1 is a well-meaning researcher who "
            "saves too much in the file. RT2 is a malicious researcher who hides data on purpose. RT3 is an outside "
            "attacker who gets hold of the released model.")

    s = d.slide("THE PAPER", "Five sets of recommendations; the demos cover TECH")
    cards = [
        ("TECH 1-17", "Technical. MDCs (TECH 5-15): holdout, attack checks, data dictionary, safe wrappers, extra care "
                      "for memorising models, DP, ensembles, federated learning, synthetic data. MQCs (TECH 16-17).", True),
        ("ELA 1-11", "Ethics and legal. Data protection may apply to the model; registers list models; EULA and "
                     "declaration clauses; a risk-based approval agreed with the data controller (ELA 8).", False),
        ("C 1-5", "Costing. Charge for the extra checks, fund tools, budget for query-limited hosting, consider "
                  "outsourcing the most technical work.", False),
        ("TR 1-4", "Training. Courses for TRE staff, researchers and ethics committees on ML disclosure risk.", False),
        ("PPIE 1-2", "Public involvement. Public representatives in governance; model use visible on data use registers.", False),
    ]
    xs = [LEFT, LEFT + 3.95, LEFT + 7.9]
    for i, (a, b, dark) in enumerate(cards):
        x = xs[i % 3]
        y = 2.25 if i < 3 else 4.5
        d.card(s, x, y, 3.65, 2.0, a, b, dark=dark, bsize=12.5)
    d.text(s, LEFT + 7.9, 4.6, 3.65, 1.8, [[("Appendices used here: ", True), ("A (experiments), C (data dictionary), "
           "D (constraints file), E (case studies), F (metrics), G (attack steps).", False)]], 13, BODY)
    d.footer(s, "Recommendation lists: §10.2 (pp. 41-53), §11.2 (pp. 54-63), §12.2 (p. 64), §13.2 (pp. 65-66), §14.2 (p. 67).")
    d.notes(s, "The paper groups its recommendations in five sets. The technical set is the one our demos illustrate. "
            "Ethics and legal: the trained model may itself be personal data, data use registers should list models "
            "and their controls, and ELA 8 says approval can follow a risk-based approach agreed with the data "
            "controller. That is why the thresholds in our first demo are a local policy, not paper thresholds. "
            "Costing, training and public involvement are short sections: checking models costs staff time, people need "
            "training, and the public should be able to see how data is used. For clause text, read the PDF.")

    s = d.slide("WHAT CARRIES OVER", "What GRAIMATTER teaches any high-trust deployment")
    lessons = [
        ("Assume the worst-case attacker", "Test white box, with the data in hand (Appendix G). NIST §2.1.4: that is how "
                                           "you test against worst-case adversaries."),
        ("Score on rows the builder never saw", "A holdout kept by the gatekeeper (TECH 6); independent testers (UK Code "
                                                "9.2.1); audit with attacks (NIST §2.4.5)."),
        ("Check structure, not only scores", "Stored rows, leaf size, file type. sacroml's structural check flags a tree "
                                             "its probability-only attack scores at 0.500."),
        ("Watch the tail", "FDIF and TPR at low FPR catch exposure that AUC averages away (Appendix F; NIST §2.4.2)."),
        ("Freeze the artefact", "Snapshot at fit(), detect later edits (TECH 3, 10); hashes and audit logs (UK Code 8.1.2, "
                                "8.3); OWASP ML10."),
        ("Budget queries in rows", "TECH 16 and UK Code 6.2. Demo 3: a budget slows extraction but does not stop it."),
    ]
    for i, (a, b) in enumerate(lessons):
        x = LEFT + (i % 3) * 3.95
        y = 2.15 + (i // 3) * 1.82
        d.card(s, x, y, 3.65, 1.68, a, b, bsize=12.5, tsize=15)
    d.rect(s, LEFT, 5.82, WIDTH, 0.78, NAVY)
    d.text(s, LEFT + 0.25, 5.82, WIDTH - 0.5, 0.78, [[("Not covered: ", True), ("evasion and poisoning (demo 3's backdoor "
           "leaves holdout accuracy unchanged) and generative AI. Add those tests for other settings.", False)]], 13.5, CREAM,
           anchor=MSO_ANCHOR.MIDDLE)
    d.footer(s, "Green paper TECH 3, 6, 10, 16 and Appendices F-G; NIST AI 100-2e2025; UK Code of Practice; demo/output/*.txt.")
    d.notes(s, "Six habits from GRAIMATTER apply to any setting where a model touches sensitive data or high-stakes decisions. "
            "Test against the strongest attacker you can imagine, because the released file gives them everything. Keep "
            "evaluation data away from the builder and let someone else run the attacks. Look at the structure of the model, "
            "not just attack scores, because an attack can miss what a leaf count shows. Look at the tail of the score "
            "distribution, not just the average. Freeze the approved artefact and detect edits. Count queries in rows. "
            "What GRAIMATTER does not give you is protection against evasion and poisoning; demo 3 shows that its holdout "
            "check is blind to a backdoor, so other deployments need those tests too.")



    d.prefix = ""
    s = d.slide("PART 4A · THE ATTACKS IN DETAIL", "Integrity and the supply chain: each NIST class, then its demo",
                dark=True, title_size=36)
    d.rect(s, 0, 0, 0.17, 7.5, ORANGE, shape=MSO_SHAPE.RECTANGLE)
    s.shapes[-1].top = 0
    d.text(s, LEFT, 3.2, 10.8, 1.4, "Part 1 named the attacks. Part 4 takes NIST's classes one at a time: what the "
           "attacker does, the defences and their limits, and where the repository shows it. Then we run the demo, "
           "section by section, and read every number it prints.", 18, "#D9DEE6")
    d.chips(s, LEFT, 5.0, ["Availability (NISTAML.01)", "Integrity (NISTAML.02)", "Supply chain (NISTAML.05)",
                           "Demos 3 and 4"])
    d.footer(s, "NIST AI 100-2e2025 §2.1-2.3 and §3.2. Technical guide §12-15; demo guide §3 and §4.", dark=True)
    d.notes(s, "In the first part we went through the attacks quickly. Now we take them one by one, in the order of the NIST "
            "taxonomy. This half covers the two objectives that GRAIMATTER does not deal with, availability and integrity, "
            "and the supply chain. For each class: what the attacker does, what the defences are and where they stop, and "
            "where this repository shows it. Then we run demos 3 and 4 and read their output section by section.")
    d.prefix = "PART 4A · "

    s = d.slide("NIST AI 100-2 · HOW TO READ THE TAXONOMY", "The CIA triad, and how to read a NISTAML identifier")
    d.table(s, LEFT, 2.15, 7.4, [
        ["Classic property", "NIST objective", "What machine learning adds"],
        ["Availability", "NISTAML.01", "Poisoned data degrades the model for everyone; crafted inputs exhaust compute"],
        ["Integrity", "NISTAML.02", "A crafted input or a few poisoned rows give the attacker's answer; accuracy looks fine"],
        ["Confidentiality", "NISTAML.03 (privacy)", "What leaks is what the model learned: members, fields, records, "
                                                    "population statistics, the model itself"],
        ["A route, not a property", "NISTAML.05", "A supplied model, dataset or library carries the attack in"],
    ], [1.9, 1.75, 3.75], size=12, row_h=0.78)
    d.card(s, LEFT + 7.65, 2.15, 3.9, 2.25, "Reading an ID", "NISTAML.0, then the objective (1 availability, 2 integrity, "
           "3 privacy, 4 misuse, generative AI only, 5 supply chain), then the class. An ID names a technique and its "
           "purpose: model poisoning is .011, .026 or .051.", bsize=12.5)
    d.card(s, LEFT + 7.65, 4.55, 3.9, 1.85, "For each class", "What the attacker does, the defences NIST lists and their "
           "limits, and where this repository shows it.", dark=True, bsize=12.5)
    d.footer(s, "NIST AI 100-2e2025, Taxonomy Index (pp. x-xi) and §2.1.2. Technical guide §12.")
    d.notes(s, "Two keys before the classes. First, the three objectives are the CIA triad security has always protected, with "
            "NIST's names: availability, integrity, and privacy for confidentiality, because in machine learning the secret "
            "is both the model and the people in its training data. Supply chain is not a fourth property; it is a way in. "
            "Second, the identifiers. The digit after NISTAML.0 is the objective, the last digit the class. The same "
            "technique can carry several IDs because the ID records its purpose: model poisoning is .011 when it breaks the "
            "model for everyone, .026 when it forces chosen answers, .051 when it arrives in a supplied model.")

    s = d.slide("NISTAML.01 · AVAILABILITY", "Availability: break the model for everyone")
    d.table(s, LEFT, 2.1, WIDTH, [
        ["Class", "What the attacker does", "Defences and their limits", "Here"],
        [".013 Data poisoning", "Adds or edits rows so the model degrades on every input; label flipping is the "
                                "simplest form", "Sanitise the data, train robustly; loud, so metrics catch it after the "
                                "damage", "Same capability as demo 3's backdoor"],
        [".011 Model poisoning", "Sends malicious updates, mostly in federated learning", "Robust aggregation, clipping, "
                                 "DP; bypassed by updates inside the accepted range", "Demo 1's post-fit check, with a "
                                 "privacy motive"],
        [".012 Clean-label poisoning", "Crafts training samples whose labels someone else assigns, all correct",
         "A label check finds nothing", "–"],
        [".014 Energy-latency", "Sends inputs that make the model burn compute (sponge examples)", "Time, compute and "
                                "rate limits (our reading; NIST lists none)", "–"],
    ], [2.35, 3.6, 3.6, 2.0], size=12, row_h=0.72)
    d.rect(s, LEFT, 5.95, WIDTH, 0.7, NAVY)
    d.text(s, LEFT + 0.25, 5.95, WIDTH - 0.5, 0.7, [[("Loud by design: ", True), ("accuracy drops for every user, so "
           "monitoring the usual metrics sees it, but only after the damage is done (NIST §2.3.1).", False)]], 13.5, CREAM,
           anchor=MSO_ANCHOR.MIDDLE)
    d.footer(s, "NIST AI 100-2e2025 §2.1.2, §2.3.1, §2.3.4. Technical guide §13.")
    d.notes(s, "Availability attacks want the system to fail for everyone. Data poisoning adds or changes training rows until "
            "the model gets worse on every input; the first cases were spam filters fed messages stuffed with words from "
            "legitimate mail. Model poisoning does the same through the parameters, mostly by sending malicious updates in "
            "federated learning. Clean-label poisoning is the realistic case when someone else assigns the labels: every "
            "label is correct, so a label check finds nothing. Energy-latency attacks send inputs that make the model "
            "consume far more compute. What these attacks share is that they are loud: accuracy drops for everyone, so "
            "ordinary monitoring catches them, but only after the damage. None is demonstrated here as an availability "
            "attack; demo 3's backdoor uses the same capability as data poisoning with an integrity goal.")

    s = d.slide("NISTAML.02 · INTEGRITY", "Integrity: the attacker's answer, with accuracy intact")
    d.table(s, LEFT, 2.1, WIDTH, [
        ["Class", "What the attacker does", "Defences and their limits", "Here"],
        [".022 Evasion", "Changes a test input into an adversarial example", "Adversarial training, randomised "
                         "smoothing, verification; all cost accuracy or compute", "Demo 3, section 1"],
        [".025 Black-box evasion", "The same with queries only: scores, labels or a substitute", "As above; many "
                                   "detectors fell to adaptive attacks", "Demo 3: labels only, 78.7%"],
        [".023 Backdoor poisoning", "Plants a trigger in training rows labelled with the target", "Sanitisation, "
                                    "trigger reconstruction, inspection; built for images", "Demo 3, section 3: 2% gives "
                                    "100%"],
        [".024 Targeted poisoning", "Changes the answer for a few inputs chosen in advance", "\"Notoriously "
                                    "challenging\"; provenance, DP", "–"],
        [".021 Clean-label backdoor", "A trigger on rows that keep their correct label", "Some sanitisation fails "
                                      "on it", "– (an exercise on demo 3)"],
        [".026 Model poisoning", "Edits parameters to plant a targeted or backdoor behaviour", "Robust aggregation; "
                                 "model inspection", "Demo 1's post-fit check"],
    ], [2.35, 3.45, 3.75, 2.0], size=11.5, row_h=0.56)
    d.rect(s, LEFT, 6.0, WIDTH, 0.66, NAVY)
    d.text(s, LEFT + 0.25, 6.0, WIDTH - 0.5, 0.66, [[("Quiet by design: ", True), ("only the attacker's inputs change, so "
           "overall accuracy barely moves. Demo 3's backdoor shifts it by 0.02 at most.", False)]], 13.5, CREAM,
           anchor=MSO_ANCHOR.MIDDLE)
    d.footer(s, "NIST AI 100-2e2025 §2.2, §2.3.2-2.3.4. Technical guide §14.")
    d.notes(s, "Integrity attacks want the model to give the answer the attacker chooses. At deployment that is evasion: an "
            "adversarial example, close to the original input but classified the attacker's way. The black-box version "
            "sees only scores or labels, or crafts examples on a substitute model and transfers them. At training it is "
            "poisoning: a backdoor plants a trigger that any input can carry later; targeted poisoning changes the answer "
            "for a few inputs chosen in advance, which are not modified at deployment; a clean-label backdoor does it "
            "without touching labels; model poisoning edits the parameters directly. The defences that held up against "
            "evasion all cost accuracy or compute, and most backdoor defences were designed for image classifiers with "
            "fixed triggers. The key difference from availability: these attacks are quiet, because only the attacker's "
            "inputs change.")

    s = d.slide("DEMO 3 · SECTION 1 · STEP BY STEP", "Evasion, step by step: 17 edits, labels only, the cheapest wins")
    d.text(s, LEFT, 2.15, 5.4, 4.3, [
        [("1  The target. ", True), ("A random forest, 200 trees, minimum leaf 10, trained on 2,000 synthetic rows. "
         "Accuracy 0.635 on the other 2,000: the label is noisy by design.", False)],
        [("2  The people. ", True), ("974 test rows are scored high risk.", False)],
        [("3  The edits. ", True), ("17 ways to misreport: drop the smoker flag, lower the weight or blood-pressure band "
         "by one or two steps. Age and diagnoses cannot change.", False)],
        [("4  The search. ", True), ("Send every edit to predict(), labels only, and keep the cheapest one the model "
         "scores low risk.", False)],
    ], 14, BODY)
    d.table(s, LEFT + 5.7, 2.15, 5.85, [
        ["Fields the person can misreport", "Evaded", "1 step", "2 steps"],
        ["Smoking, weight, blood pressure", "78.7%", "58.7%", "70.5%"],
        ["Smoking verified by a test", "32.8%", "18.2%", "28.6%"],
        ["Smoking and weight measured", "20.7%", "12.8%", "20.7%"],
    ], [2.85, 1.0, 1.0, 1.0], size=12.5, row_h=0.55, highlight={(1, 1): PEACHBG, (3, 1): "#DCEBDD"})
    d.card(s, LEFT + 5.7, 4.6, 5.85, 1.8, "How to read it", "Most people need a single change, usually \"non-smoker\". "
           "Each field taken out of the attacker's hands cuts the rate. Adversarial training would not help: a misreported "
           "form is an ordinary input.", dark=True, bsize=12.5)
    d.footer(s, "uv run python demo/run_aml_demo.py · aml_demo/evasion.py · aml_report.txt §1 · demo guide §3.0-3.1.")
    d.notes(s, "Now run demo 3 and read section 1. The target is a random forest trained on 2,000 synthetic rows; its accuracy "
            "of 0.635 is about as good as the noisy label allows. 974 test rows are scored high risk. The attacker is a "
            "person filling in a form: they cannot change their age or a recorded diagnosis, but they can lie about what "
            "nobody checks. The code lists 17 edits, applies every one that is possible for each person, sends them all to "
            "the model's predict function, which returns labels only, and keeps the cheapest edit that comes back low risk. "
            "With all three fields self-reported, 78.7% evade, most with one step. Verify smoking and it is 32.8%; measure "
            "weight too and it is 20.7%. The defence that works is a process change, not a model change.")

    s = d.slide("DEMO 3 · SECTION 3 · STEP BY STEP", "Backdoor, step by step: two triggers, three doses, one screen")
    d.text(s, LEFT, 2.15, 4.6, 4.3, [
        [("1  The triggers. ", True), ("Loud: lab A at 4.0. Quiet: lab A at +1.7 and lab B at -1.7, each ordinary "
         "on its own.", False)],
        [("2  The poison. ", True), ("Copy random training rows, add the trigger, label them low risk, append 1%, 2% "
         "or 5% and retrain.", False)],
        [("3  The attack. ", True), ("Add the trigger to every test row scored high risk and count how many turn "
         "low risk.", False)],
        [("4  The screen. ", True), ("An IsolationForest drops the oddest 5% of the training table. How much poison "
         "does it catch?", False)],
    ], 13.5, BODY)
    d.table(s, LEFT + 4.85, 2.15, 6.7, [
        ["Trigger", "Poison", "Accuracy", "Trigger flips", "Screen catches"],
        ["clean model", "0", "0.635", "28.3% / 32.3%", "–"],
        ["loud", "1% / 2% / 5%", "0.627 / 0.626 / 0.630", "79% / 100% / 100%", "70% / 80% / 42%"],
        ["quiet", "1% / 2% / 5%", "0.630 / 0.627 / 0.615", "94% / 100% / 100%", "20% / 25% / 14%"],
    ], [1.0, 1.25, 1.75, 1.45, 1.25], size=11.5, row_h=0.6, highlight={(3, 4): PEACHBG})
    d.card(s, LEFT + 4.85, 4.75, 6.7, 1.65, "How to read it", "The baseline matters: the clean model already flips about "
           "30%, so the attack is the rise to 100%. Accuracy moves 0.02 at most, so a holdout check sees nothing. The more "
           "poison, the more normal it looks to the screen.", dark=True, bsize=12.5)
    d.footer(s, "aml_demo/poisoning.py · aml_report.txt §3 · demo guide §3.3. Clean-model figures: loud / quiet trigger.")
    d.notes(s, "Section 3 of the same run. Two triggers are written into two lab columns that carry no label signal: a loud "
            "one, a value four standard deviations out, and a quiet one, two values that are each ordinary. The poison "
            "function copies random training rows, applies the trigger, labels them low risk and appends them; the forest "
            "is retrained with 1, 2 and 5 percent. First read the clean model: the triggers already flip about 30% of "
            "high-risk scores, because the values are unusual. The attack is the rise above that baseline, to 100% at 2%. "
            "Test accuracy stays within 0.02. The isolation forest catches most of the loud trigger at low doses and little "
            "of the quiet one, and its catch falls as the poison grows, because a dense cluster stops looking rare.")

    s = d.slide("NISTAML.05 · SUPPLY CHAIN", "Supply chain: the attack arrives with what you download")
    sc = [
        ("How", "Pre-trained models with backdoors that survive fine-tuning; control of training randomness (the Dropout "
                "Attack); model files that run code when loaded (ATLAS CS0031) or return a planted falsehood (CS0019)."),
        ("Defences and limits", "Check published hashes, scan artefacts, treat supplied models as untrusted. Robustness "
                                "to supply-chain model poisoning is \"a critical open problem\" (§4.2.2)."),
        ("Frameworks", "UK Code principle 7 and provision 8.1.2 (publish hashes). OWASP ML06, LLM03. ATLAS AML.T0010. "
                       "EU AI Act 15(5): attacks on pre-trained components."),
        ("Here: demo 4", "A swapped model with a backdoor, code in a pickle, a key cut from 256 to 40 bits and a "
                         "safe-wrapper floor lowered from 20 rows to 1."),
    ]
    for i, (a, b) in enumerate(sc):
        x = LEFT + (i % 2) * 5.85
        y = 2.15 + (i // 2) * 2.0
        d.card(s, x, y, 5.7, 1.85, a, b, dark=(i == 3), bsize=12.5)
    d.rect(s, LEFT, 6.2, WIDTH, 0.5, PEACHBG)
    d.text(s, LEFT + 0.25, 6.2, WIDTH - 0.5, 0.5, [[("NISTAML.051: ", True), ("AI inherits the software supply chain and "
           "adds data, pre-trained models and plugins. NIST counts what exploits their data-driven nature.", False)]], 12.5,
           INK, anchor=MSO_ANCHOR.MIDDLE)
    d.footer(s, "NIST AI 100-2e2025 §2.3.4, §3.2, §3.2.2, §4.2.2. Technical guide §15.")
    d.notes(s, "The supply chain is a route, not an objective: whatever comes through it then breaks integrity, availability or "
            "confidentiality. AI inherits every weakness of the software supply chain and adds its own: collected and "
            "labelled data, pre-trained models and plugins. NIST's one class here is model poisoning through a supplied "
            "model. The defences are discipline rather than algorithms: check the file against a published hash, scan what "
            "a model file would import or run, and treat any supplied model as untrusted. NIST is candid that robustness to "
            "a backdoor hidden in supplied weights is a critical open problem. Demo 4 shows four ways a mirror can change "
            "what you download.")

    s = d.slide("DEMO 4 · STEP BY STEP", "Demo 4, step by step: pin at approval, check each download")
    d.text(s, LEFT, 2.15, 4.4, 4.3, [
        [("1  The release. ", True), ("A supplier publishes model.pkl (demo 3's forest), bundle.json (accuracy 0.635, "
         "256-bit keys) and constraints.json (leaf 20, depth 4).", False)],
        [("2  The pin. ", True), ("At approval the user records each file's SHA-256 from the supplier's release notes, "
         "not from the mirror.", False)],
        [("3  The mirror. ", True), ("Changes the files four ways (sections 2 to 4).", False)],
        [("4  The checks. ", True), ("The usual test, the pin, and an import scan or a floor kept in code.", False)],
    ], 13.5, BODY)
    d.table(s, LEFT + 4.65, 2.15, 6.9, [
        ["Tampered file", "Usual check", "Pin", "Scan or floor"],
        ["Swapped model, 2% backdoor", "accuracy 0.627: passes", "refuses", "passes"],
        ["Code hidden in the pickle", "accuracy 0.635: passes", "refuses", "refuses"],
        ["Key length 256 to 40 bits", "still encrypts: passes", "refuses", "refuses"],
        ["Safe-wrapper floor 20 to 1", "request_release(): passes", "refuses", "refuses"],
    ], [2.35, 2.15, 1.0, 1.4], size=11.5, row_h=0.5, highlight={(1, 3): PEACHBG})
    d.card(s, LEFT + 4.65, 4.85, 6.9, 1.55, "Section 6: what the pin does not catch", "A pin taken from the download "
           "verifies the backdoored forest. A digest proves the file is the one approved, not that the one approved was "
           "good: add signatures, provenance and formats that cannot hold code.", dark=True, bsize=12)
    d.footer(s, "uv run python demo/run_supply_chain_demo.py · supply_chain_report.txt · demo guide §4.")
    d.notes(s, "Run demo 4. Section 1 is the supplier's release and the pin: the user records the SHA-256 of each file from the "
            "supplier's own notes. Section 2: the mirror serves a forest trained with 2% quiet-trigger poison; its accuracy "
            "on the user's holdout is 0.627 against 0.635 published, so the usual test accepts it, the import scan finds "
            "only sklearn and numpy, and only the pin refuses it. Section 3: a pickle that calls the attacker's function "
            "while loading and then returns the genuine forest; the scan reads the imports without loading and refuses it. "
            "Section 4: a key length cut to 40 bits, 18 minutes to search at a billion keys a second, and the safe "
            "wrapper's minimum leaf cut to 1; floors kept in code refuse both. Section 5 is the table on the slide: four "
            "of four pass the usual check, none passes the pin and the scan or floor. Section 6 is the honest limit.")
    d.prefix = ""



    d.prefix = ""
    s = d.slide("PART 4B · THE ATTACKS IN DETAIL", "Privacy: each NIST class, demos 1 and 2, and a release gate",
                dark=True, title_size=36)
    d.rect(s, 0, 0, 0.17, 7.5, ORANGE, shape=MSO_SHAPE.RECTANGLE)
    s.shapes[-1].top = 0
    d.text(s, LEFT, 3.2, 10.8, 1.4, "The objective GRAIMATTER covers in depth. First the privacy classes and extraction, "
           "then demos 1 and 2 section by section, the classes generative AI adds, and a gate that judges every demo "
           "against named obligations.", 18, "#D9DEE6")
    d.chips(s, LEFT, 5.0, ["Privacy (NISTAML.03)", "Demo 3: extraction", "Demos 1 and 2", "Release gate"])
    d.footer(s, "NIST AI 100-2e2025 §2.4 and §3. Technical guide §16-23; demo guide §1, §2 and §5.", dark=True)
    d.notes(s, "The second half of the detailed walkthrough is privacy, which NIST uses for confidentiality: the training data "
            "and the model itself. We start with the classes and with extraction, which demo 3 runs. Then we go through "
            "the GRAIMATTER demos section by section: the hand-written checks of demo 1 and the official SACRO-ML package "
            "in demo 2. We close with the classes generative AI adds and with the release gate.")
    d.prefix = "PART 4B · "

    s = d.slide("NISTAML.03 · PRIVACY", "Privacy: what the model learned, and the model itself")
    d.table(s, LEFT, 2.1, WIDTH, [
        ["Class", "What the attacker does", "Defences and their limits", "Here"],
        [".031 Model extraction", "Queries the model and trains a copy, often a step to white-box attacks",
         "DP does not help; query limits can be circumvented", "Demo 3: 200 queries, 86.9% agreement"],
        [".032 Reconstruction", "Recovers records; attribute inference fills in a hidden field", "DP bounds it; "
                                "structural checks for models that store rows", "Demo 1: kNN keeps 500 of 500 rows; "
                                "20 queries recover two fields"],
        [".033 Membership inference", "Decides whether a record was in training: loss, shadow models, LiRA, label "
                                      "only", "DP bounds it, at a cost; audit with attacks", "Demos 1 and 2: AUC 0.708, "
                                      "0.528 wrapped"],
        [".034 Property inference", "Learns a statistic of the training population", "DP often does not help",
         "–"],
    ], [2.35, 3.6, 3.15, 2.45], size=12, row_h=0.74)
    d.rect(s, LEFT, 5.95, WIDTH, 0.7, NAVY)
    d.text(s, LEFT + 0.25, 5.95, WIDTH - 0.5, 0.7, [[("Differential privacy protects people, ", True), ("not the model "
           "(extraction) and not statistics of the population (property inference). NIST §2.4.5.", False)]], 13.5, CREAM,
           anchor=MSO_ANCHOR.MIDDLE)
    d.footer(s, "NIST AI 100-2e2025 §2.1.2, §2.4.1-2.4.5. Attribute inference has no ID; the gate files it under .032. "
                "Technical guide §16.")
    d.notes(s, "Privacy, in NIST's sense, covers both data privacy, about the training rows, and model privacy, about the model. "
            "Extraction steals a working copy by querying, and is often a first step to white-box attacks. Reconstruction "
            "recovers records; attribute inference, which GRAIMATTER's case studies centre on, fills in a hidden field of a "
            "person you partly know, and NIST describes it here without an ID of its own. Membership inference decides "
            "whether a record was in training, which alone can disclose a diagnosis. Property inference learns a statistic "
            "of the population. Differential privacy is the only defence with a guarantee, and it covers the people in the "
            "data, not the model and not population statistics.")

    s = d.slide("DEMO 3 · SECTION 2 · STEP BY STEP", "Extraction, step by step: invented rows, real answers, a copy")
    d.text(s, LEFT, 2.15, 4.6, 4.3, [
        [("1  Invent. ", True), ("Rows inside the published value ranges; the data dictionary is public. No real "
         "record is used.", False)],
        [("2  Ask. ", True), ("Send them to the target's predict() and keep the labels.", False)],
        [("3  Copy. ", True), ("Train a forest on the invented rows and the answers. Fidelity is the share of real rows "
         "where copy and target agree.", False)],
        [("4  Use it. ", True), ("Plan evasion edits on the copy, offline, and try them on the target.", False)],
    ], 13.5, BODY)
    d.table(s, LEFT + 4.85, 2.15, 6.7, [
        ["Queries", "Copy agrees", "Copy accuracy", "Edits that fool the target"],
        ["50", "77.7%", "0.610", "22.0%"],
        ["200", "86.9%", "0.623", "54.2%"],
        ["1,000", "89.5%", "0.629", "58.3%"],
        ["5,000", "93.5%", "0.630", "64.4%"],
    ], [1.2, 1.6, 1.7, 2.2], size=12.5, row_h=0.5, highlight={(2, 1): PEACHBG})
    d.card(s, LEFT + 4.85, 4.85, 6.7, 1.55, "The query gate", "Demo 1's QueryGate with a 200-row budget refuses a "
           "1,000-row request. But 200 rows already give an 87% copy, and several accounts multiply any budget.",
           dark=True, bsize=12.5)
    d.footer(s, "aml_demo/extraction.py · aml_report.txt §2 · demo guide §3.2. Target accuracy 0.635.")
    d.notes(s, "Back to demo 3, section 2. The attacker never sees a real record: they invent rows inside the ranges the data "
            "dictionary publishes, send them to the API and train their own forest on the labels that come back. Read the "
            "table by budget. With 200 queries the copy agrees with the target on 86.9% of real rows and is almost as "
            "accurate. The last column is why extraction matters: edits planned on the copy, without the target seeing "
            "them, get 54% of flagged people past the real model at 200 queries. The gate from demo 1 refuses a 1,000-row "
            "request on a 200-row budget, but the damage was done at 200.")

    s = d.slide("TECH 6 · TECH 8 · THE COHORT", "Half the rows never reach the researcher")
    d.image(s, "fig02_holdout", top=2.2, max_h=3.7)
    d.text(s, LEFT, 6.2, WIDTH, 0.5, [[("TECH 8: ", True), ("the researcher's inputs are described in "
           "demo/output/data_dictionary.json, following the Appendix C template.", False)]], 14, BODY)
    d.footer(s, "TECH 6 (p. 43), TECH 8 (p. 46), Appendix C (p. 83). Cohort: demo/graimatter_demo/cohort.py, seed 7.")
    d.notes(s, "Both demos use the same synthetic cohort: 1,000 rows drawn with seed 7, split 500 for the researcher and "
            "500 kept by the TRE. That is TECH 6: the TRE holds back data the team never trains on, and uses it to "
            "check accuracy and to run attacks. Training accuracy is the score on rows the model has seen; set-aside "
            "accuracy is the score on the 500 rows the researcher never received. A large gap means the model has fit "
            "this sample, noise included. The label is drawn from a known logistic function of six clinical columns. "
            "Ten noise columns carry no signal at all, so an unconstrained tree has something to memorise.")

    s = d.slide("APPENDIX E · ATTRIBUTE INFERENCE", "One planted person: 20 queries recover two hidden fields")
    d.image(s, "fig03_attribute_sweep", top=2.2, max_h=4.3)
    d.footer(s, "Appendix E §20.1 (pp. 86-87). Demo: demo/output/demo_report.txt, section 2.")
    d.notes(s, "This is the paper's first case study, rebuilt on synthetic data. An attacker knows four public facts about "
            "someone: age 62, diabetic, asthmatic, smoker. They do not know weight or blood pressure. Weight has four "
            "levels and blood pressure five, so there are 20 combinations. The attacker sends all 20 to the model and "
            "looks at the confidence. Models are usually more confident on inputs they were trained on. Here one cell "
            "is at 1.000 and the other 19 tie at 0.500, so the unique best guess is the hidden truth: overweight and "
            "slightly high. Attribute inference means filling in hidden fields of a person by querying the model.")

    s = d.slide("APPENDIX F · READING ATTACK METRICS", "Chance, the tail, and how rare a member is")
    d.image(s, "fig04_metrics", top=2.15, max_h=4.5)
    d.footer(s, "Appendix F (pp. 92-95). Posterior formula: Appendix F §21.3; values from demo_report.txt section 4.")
    d.notes(s, "Membership inference asks whether a row was in the training set. The attack gives each row a score. AUC is "
            "the chance that a random member scores higher than a random non-member: 0.5 is a coin toss. Advantage is "
            "the absolute gap between the true-positive and false-positive rates. TPR at 10% FPR asks how many real "
            "members the attack catches when it may raise a false alarm on only about 10% of non-members. FDIF looks at "
            "the extremes: share of members in the top 10% of scores minus the share in the bottom 10%, with a "
            "permutation p-value. A model can look like chance on average and still be exposed in the tail. Finally, "
            "the membership posterior: if the attack says 'member', the chance that is true depends on how rare members "
            "are. For the unconstrained tree it is 0.630 when half the candidates are members and 0.017 at 1 in 100.")

    s = d.slide("DEMO 1 · UNCONSTRAINED TREE", "Perfect training accuracy and a leaf of one person: refused")
    rows = [["Check", "Seeded result", "Demo limit", "Fires?"],
            ["Training vs set-aside accuracy", "1.000 vs 0.590 (gap 0.410)", "gap 0.15", "yes"],
            ["Smallest leaf", "1 training row", "–", "–"],
            ["File size ÷ training table", "18,150 / 68,000 bytes = 0.267", "0.75", "no"],
            ["Worst-case membership AUC", "0.708", "0.62", "yes"],
            ["Advantage (TPR 1.000, FPR 0.588)", "0.412", "0.20", "yes"],
            ["TPR at 10% FPR", "0.156", "0.35", "no"],
            ["FDIF", "0.620, p = 0.003", "0.20, p ≤ 0.05", "yes"],
            ["Weight attribute inference", "abstained (ratio 1.000)", "1.35", "no"]]
    hl = {(i, 3): REDBG for i in (1, 4, 5, 7)}
    d.table(s, LEFT, 2.2, 8.0, rows, [3.0, 2.55, 1.45, 1.0], size=12.5, row_h=0.43, highlight=hl)
    d.card(s, 9.2, 2.2, 3.24, 1.75, "Decision", "Do not release. Four demo rules fire.", fill=REDBG, tcolor=RED)
    d.card(s, 9.2, 4.1, 3.24, 1.95, "Why the attribute attack abstained",
           "The tree isolated rows with noise columns, so changing weight never left the leaf.", bsize=12.5)
    d.footer(s, "demo/output/demo_report.txt, section 4. Limits are a demo policy (disclosure.py), not paper thresholds (ELA 8).")
    d.notes(s, "The researcher would report 100% accuracy, but on the TRE's set-aside rows it is 59%. The gap of 0.41 is "
            "overfitting, and the smallest leaf holds one training row. The worst-case membership attack of Appendix G "
            "reaches AUC 0.708 and advantage 0.412, and FDIF is 0.620 with p = 0.003. Note what does not fire: the file "
            "is only 0.27 of the training table, and TPR at 10% FPR is 0.156. Size alone would have let this model "
            "through. The attribute attack on weight abstains, because this tree splits on the noise columns. Section 2 "
            "is the case where the model does split on the hidden fields. Remember the limits are a demo policy.")

    s = d.slide("DEMO 1 · SAFE WRAPPER (TECH 9-10)", "Leaf 20, depth 4: AUC 0.528, released under a demo policy")
    d.image(s, "fig06_trees", top=2.2, max_h=4.3)
    d.footer(s, "demo/output/demo_report.txt, section 5. The policy is local to this demo; ELA 8 leaves the risk appetite "
             "to the data controller.")
    d.notes(s, "The same data goes through the hand-written safe wrapper. It reads demo/constraints.json and moves "
            "min_samples_leaf from 1 to 20 and max_depth from unlimited to 4. Appendix D shows the constraints-file "
            "format with an example minimum leaf of 5; the demo is stricter so the contrast shows on a few hundred rows. "
            "Training accuracy drops to 0.692 and set-aside accuracy barely moves, 0.584: the deep tree's extra accuracy "
            "was memorisation. The worst-case attack falls to AUC 0.528, advantage 0.004, FDIF 0.020 with p = 0.445. "
            "No demo rule fires, so the script releases it. Say clearly that the policy is ours, not the paper's.")

    s = d.slide("APPENDIX F · THE TAIL", "The quiet failure: AUC near 0.5, but FDIF 0.160")
    d.image(s, "fig07_tail", top=2.2, max_h=4.0)
    d.footer(s, "demo/output/demo_report.txt, section 5 (Salem-synth). Appendix A Table 2 describes the Salem scenarios.")
    d.notes(s, "On the same wrapped tree we also run Salem-synth, where the attacker trains a shadow model on similar "
            "data rather than on the TRE's own tables. Its AUC is 0.512, close to chance. But its FDIF is 0.160 with "
            "p = 0.027: the top tenth of its scores holds clearly more members than the bottom tenth. This is exactly the "
            "Appendix F warning: an average metric can hide a tail. The demo's export rule follows the worst-case "
            "attack, whose FDIF is 0.020, so it still releases. A data controller who cares about the tail could refuse.")

    s = d.slide("TECH 11 · INSTANCE-BASED MODELS", "Nearest neighbours and SVC store rows: refuse them")
    d.card(s, LEFT, 2.2, 3.65, 2.1, "1-nearest neighbour", "Stores all 500 training rows. File 68,677 bytes, ratio 1.010 "
           "of the training table. Refused.", fill=REDBG, tcolor=RED)
    d.card(s, LEFT + 3.95, 2.2, 3.65, 2.1, "RBF support-vector classifier", "Stores 423 support vectors out of 500 "
           "rows. File ratio 0.94. Refused.", fill=REDBG, tcolor=RED)
    d.card(s, LEFT + 7.9, 2.2, 3.65, 2.1, "Safe wrappers", "Both wrapper classes refuse to fit: constraints.json marks "
           "KNeighborsClassifier and SVC as not permitted.", dark=True)
    d.card(s, LEFT, 4.5, 7.6, 1.9, "The paper's alternatives (TECH 11)", "Train on aggregated data, use a differentially "
           "private algorithm, or keep the model inside a query-limited service. This repository does not train a "
           "private SVM.", fill=PEACHBG)
    d.card(s, LEFT + 7.9, 4.5, 3.65, 1.9, "In the paper", "Appendix E §20.4: an SVM found to hold 441 exact patient "
           "rows out of 798.", bsize=12.5)
    d.footer(s, "TECH 11 (p. 49), §10.1.5 (pp. 39-40), Appendix E §20.4 (pp. 91-92). Demo: demo_report.txt, section 6.")
    d.notes(s, "Instance-based models need the training rows to work. A nearest-neighbour model finds the closest stored "
            "rows; a kernel SVC compares new inputs with its support vectors. The rows can be read straight out of the "
            "file, so the demo refuses both, whatever the attack numbers say. The paper's options are training on "
            "aggregated data, using a differentially private variant, or not releasing the file at all and offering a "
            "query-limited service instead. Its Appendix E case study describes a TRE that found 441 copies of patient "
            "records out of 798 inside an SVM.")

    s = d.slide("RT1 · RT2 · TECH 3", "Editing the model after fit() is caught")
    d.image(s, "fig08_wrapper", top=2.2, max_h=4.2)
    d.footer(s, "§10.1.2 (p. 37), TECH 3 (p. 42), TECH 10 (p. 48). Demo: demo_report.txt sections 7 and 9.")
    d.notes(s, "The wrapper records the state of the model when it was fitted. In section 7 the researcher overrides the "
            "constraints and trains a deep tree, then edits the parameters back toward the allowed values and adds a "
            "hidden attribute. request_release() compares the fitted state with the current one and says not to release: "
            "max_depth and min_samples_leaf changed after fitting, the smallest leaf still holds one row, and an attribute "
            "called hidden_rows was added. That covers both the careless case (RT1) and the deliberate one (RT2). A file "
            "with a .txt extension is refused because it is not .joblib or .pkl. For the approved model the demo writes a "
            "register entry and a pipeline snapshot, which is TECH 3.")

    s = d.slide("TECH 16 · MODEL QUERY CONTROLS", "Count rows, not calls: one patient allowed, 20 blocked")
    d.image(s, "fig09_query_budget", top=2.3, max_h=3.6)
    d.footer(s, "TECH 16-17 (pp. 52-53), §10.1.7 (pp. 40-41). Demo: demo_report.txt, section 8.")
    d.notes(s, "If the model stays on a server, the TRE can limit queries. The demo gate gives one user a budget of 8 rows. "
            "A clinician's single patient lookup uses 1 row and is allowed. Then the same user sends the 20-combination "
            "sweep from the attribute case study in one request. The gate refuses it: 20 rows requested, 1 already used, "
            "budget 8. The unit matters. If the budget counted HTTP calls, one call carrying 20 rows would pass. TECH 17 "
            "says a real query-limited service should be tested by an external party; the demo implements only the "
            "control logic. Demo 3 shows the other side: a row budget slows model extraction but 200 rows already copy a "
            "simple model.")

    s = d.slide("§10.1.3 · TECH 12 · DIFFERENTIAL PRIVACY", "Noise protects a mean; the best of 50 draws undoes it")
    d.image(s, "fig10_dp", top=2.2, max_h=4.3)
    d.footer(s, "§10.1.3 (pp. 37-39), TECH 12 (p. 50). Demo: demo_report.txt, section 3. No private model is trained here.")
    d.notes(s, "Differential privacy is a property of the release mechanism, not of the data. The paper's thought experiment: "
            "the attacker knows everything except whether one person was included. A deterministic mean gives the answer "
            "away, accuracy 1.000. Adding Laplace noise with smaller epsilon pushes the attacker back toward a coin toss: "
            "0.703 at epsilon 8, 0.522 at 1, 0.487 at 0.2. TECH 12 adds a practical warning. At epsilon 0.2 one noisy mean "
            "misses the truth by 0.3053, but if someone draws 50 times and keeps the closest, the miss is 0.0084, which "
            "cancels the protection. So TRE staff should pick the seed without looking at accuracy. This repository only "
            "sketches DP on a mean; it does not train a private model.")

    s = d.slide("DEMO 2 · SACROML 2.0.1", "sacroml: leaf 5, 'proceed to next step', still flagged")
    rows = [["sacroml check", "Unconstrained tree", "Wrapped tree (leaf 5)"],
            ["Training / set-aside accuracy", "1.000 / 0.590", "0.868 / 0.566"],
            ["Worst-case membership AUC (3 runs)", "mean 0.500, 0 above null band", "mean 0.494, 0 above null band"],
            ["Smallest leaf vs threshold 10", "1 → k_anonymity_risk true", "5 → k_anonymity_risk true"],
            ["gen_error, unnecessary, class_disclosure, smallgroup", "true", "true"],
            ["dof_risk", "false", "false"],
            ["request_release() without a Target", "–", "\"Proceed to next step of checking\""],
            ["min_samples_leaf 5 → 1 after fit()", "–", "posthoc_check(): disclosive"]]
    hl = {(3, 1): REDBG, (3, 2): REDBG, (4, 1): REDBG, (4, 2): REDBG}
    d.table(s, LEFT, 2.2, WIDTH, rows, [4.35, 3.6, 3.6], size=12.5, row_h=0.47, highlight=hl)
    d.footer(s, "demo/output/sacroml/sacroml_report.txt; per-attack report.json under demo/output/sacroml/. "
             "SACRO-ML: github.com/AI-SDC/SACRO-ML")
    d.notes(s, "The second demo runs the same cohort through sacroml 2.0.1, the maintained toolkit from the AI-SDC "
            "repository named in the paper. Its safe wrapper warns that min_samples_leaf of 1 is below its recommended "
            "minimum of 5 and changes it to 5. request_release() without a Target writes a target file and says 'Proceed "
            "to next step of checking': it does not run attacks and it is not an approval. Passing a Target would also "
            "start the LiRA attack, which the upstream example runs with 100 shadow models; this demo does not run LiRA. "
            "Then the attacks. The structural attack marks a leaf as risky below 10 training rows, so both the "
            "unconstrained tree and the wrapped tree with leaf 5 are flagged. Moving from leaf 1 to leaf 5 is what the "
            "published rules do, and the package's own structural check still calls that tree risky.")

    s = d.slide("WHY THE TWO MEMBERSHIP NUMBERS DIFFER", "Same tree, AUC 0.708 or 0.500: two different attacks")
    d.image(s, "fig05_confidence", top=2.1, max_h=3.8)
    d.text(s, LEFT, 6.0, WIDTH, 0.5, [[("Hand-written: ", True), ("probabilities plus the true label, so it sees "
           "'right on members, often wrong on set-aside'.  ", False), ("sacroml: ", True), ("predicted probability only, "
           "and pure leaves are extreme for everyone.", False)]], 13.5, BODY)
    d.footer(s, "Appendix G (p. 96). attacks.py (_attack_features) and sacroml.attacks.worst_case_attack.")
    d.notes(s, "Both demos call their attack 'worst case', but they are different tests. The hand-written attack trains a "
            "second model on the predicted probabilities plus the true label, so it can use the confidence in the "
            "correct class. On the unconstrained tree every leaf is pure, so every prediction is 0 or 1. Training rows "
            "always get confidence 1 in their true label; set-aside rows get 1 when the tree is right, 59% of the time, "
            "and 0 otherwise. The label-aware attack sees that gap and reaches AUC 0.708. The sacroml attack scores rows "
            "by predicted probability only. Without the label, a pure leaf looks equally extreme for members and "
            "non-members, so its AUC is 0.500. An AUC near 0.5 from the package does not mean the tree failed to "
            "memorise; the structural attack is what catches it there.")

    s = d.slide("TWO DEMOS COMPARED", "Leaf 20 vs 5, label-aware vs probability-only")
    d.image(s, "fig11_two_demos", top=2.2, max_h=4.3)
    d.footer(s, "demo_report.txt section 10 and sacroml_report.txt. Appendix D (p. 83) example leaf size: 5.")
    d.notes(s, "Three differences matter. First, the leaf rule: the hand-written wrapper forces leaf 20 and depth 4, the "
            "package rules file forces leaf 5. Second, the membership attack: probabilities plus label versus "
            "probabilities only. Third, the outcome: the hand-written script releases the stricter tree because its own "
            "attack falls inside the demo limits; the package never approves anything here, it says to continue "
            "checking, and its structural attack still flags the leaf-5 tree. Neither is an approval process. A real "
            "TRE would combine these checks with a policy agreed with its data controller.")

    s = d.slide("DEMO 6 · HIDING DATA IN A MODEL", "Writing data into the model: two channels an accuracy check misses")
    d.text(s, LEFT, 2.15, 4.4, 4.3, [
        [("1  In the weights. ", True), ("Hide 111 bytes in the low 8 bits of a 10,304-weight network. The largest "
         "change to any weight is 3e-06; accuracy is unchanged and the payload reads back exactly (EvilModel, 2021).", False)],
        [("2  In the behaviour. ", True), ("A few trigger inputs carry a message one bit each; accuracy on real rows "
         "holds and the triggers return it exactly (Adi et al. 2018; Song et al. 2017).", False)],
        [("3  Why it matters. ", True), ("An accuracy-only export check passes both. The data leaves the TRE inside "
         "the model.", False)],
    ], 13.5, BODY)
    d.table(s, LEFT + 4.65, 2.15, 6.9, [
        ["Channel", "Where the message is", "Accuracy", "Removed by"],
        ["Weight LSB", "low mantissa bits", "0.575 → 0.575", "clip / quantise / noise"],
        ["Behaviour", "trigger inputs", "0.575 → 0.632", "fine-tune / DP"],
    ], [1.5, 2.6, 1.4, 1.4], size=11.5, row_h=0.5, highlight={(1, 3): PEACHBG, (2, 3): PEACHBG})
    d.card(s, LEFT + 4.65, 3.55, 6.9, 2.85, "The TRE's answer: transform, do not detect", "Clipping the low bits, "
           "quantising to float16, or adding noise each keeps accuracy and wipes the weight channel; the behavioural "
           "channel needs fine-tuning or DP. A distribution test cannot tell the models apart, because the payload fills "
           "too few weights to move a statistic. So safe export should transform every released model and prefer DP "
           "training, not try to spot the hidden data after the fact.", dark=True, bsize=12.5)
    d.footer(s, "uv run python demo/run_stego_demo.py · stego_report.txt · demo guide §6 · technical guide §9.4.")
    d.notes(s, "Run demo 6. GRAIMATTER's checks ask whether a model leaks its training data by accident; they do not ask "
            "whether a researcher wrote data into it on purpose. The carrier is a small neural network on the same cohort. "
            "First channel: steganography in the low mantissa bits of the float32 weights. Hiding a 111-byte note moves no "
            "weight by more than 3e-06 and leaves accuracy at 0.575, so TECH 6 and the release gate pass it while the data "
            "rides out in the low bits; EvilModel (2021) hid whole malware files this way. Second channel: a watermark or "
            "backdoor, where trigger inputs far from the cohort carry the message one bit each; the model answers real rows "
            "as well as before and returns every planted bit. Defences: clipping the low bits, rounding to float16, or "
            "adding 0.1% noise each keeps accuracy and destroys the weight payload, but none touch the behavioural channel, "
            "which needs fine-tuning or differential privacy. A low-bit distribution test does not separate a clean model "
            "from a stego one, because the payload occupies about 115 of the 10,304 weights. The lesson for a TRE is to "
            "transform every released model, not to detect the payload. The demo is standalone and not wired into the gate.")

    s = d.slide("BEYOND PREDICTIVE AI · NIST §3", "Generative AI keeps the objectives and adds classes")
    d.table(s, LEFT, 2.1, 7.2, [
        ["ID", "Class"],
        ["NISTAML.04", "Misuse enablement: get around the owner's restrictions"],
        [".018 / .015", "Direct and indirect prompt injection"],
        [".027", "Misaligned outputs"],
        [".035 / .036", "Prompt extraction; leaking information from user interactions"],
        [".037 / .038", "Training data attacks; data extraction"],
        [".039", "Compromising connected resources"],
    ], [1.6, 5.6], size=12.5, row_h=0.55)
    d.card(s, LEFT + 7.45, 2.1, 4.1, 2.2, "Covered in Part 1", "Slide 12: direct and indirect prompt injection, the "
           "OWASP LLM Top 10 and NIST's design advice: assume injection and limit what the model can do.", bsize=12.5)
    d.card(s, LEFT + 7.45, 4.45, 4.1, 1.95, "Tested elsewhere", "safety-trust-engine runs garak, AgentDojo and PyRIT "
           "against live models and agents, with the same gate pattern.", dark=True, bsize=12.5)
    d.footer(s, "NIST AI 100-2e2025 §3 and its taxonomy index. Technical guide §22 and §5.")
    d.notes(s, "For generative AI, NIST keeps the three objectives and the supply chain, adds a fourth objective, misuse "
            "enablement, and adds classes that work through prompts: direct and indirect prompt injection, misaligned "
            "outputs, prompt extraction, leaks from user interactions, training data attacks, data extraction and the "
            "compromise of connected resources such as an agent's tools. This repository has no generative-AI demo; the "
            "companion repository safety-trust-engine tests these classes on live models and agents with the same idea "
            "of a gate.")

    s = d.slide("LIMITS", "What this repository does not decide")
    lim = [
        ("A real risk appetite", "The demo 1 cut-offs are local. ELA 8: thresholds are agreed with the data controller."),
        ("Legal advice", "The EU AI Act, GDPR and UK code are summarised, not interpreted. Clause text needs a legal review."),
        ("Strong attacks", "No LiRA (in sacroml, not run). Demo 3 uses simple greedy and query attacks, not optimised ones."),
        ("Private training", "No differentially private model. DP is sketched on a released mean only."),
        ("Generative AI", "No LLM demo here. safety-trust-engine tests prompt injection and agents with garak, AgentDojo, PyRIT."),
        ("Real data, approval", "One synthetic cohort; no demo approves a model. sacroml says 'proceed to next step'."),
    ]
    for i, (a, b) in enumerate(lim):
        x = LEFT + (i % 3) * 3.95
        y = 2.2 + (i // 3) * 2.15
        d.card(s, x, y, 3.65, 1.95, a, b, bsize=13)
    d.footer(s, "docs/brief-for-presentation-and-guide.md, 'Claims to keep accurate'.")
    d.notes(s, "Be explicit about the edges. The cut-offs in disclosure.py exist so demo 1 can say yes or no; the paper "
            "publishes no universal thresholds. The legal slides summarise documents and are not advice. The attacks are "
            "teaching versions: no LiRA, and demo 3's evasion is a greedy search over a few fields, not an optimised "
            "attack. There is no private model and no generative-AI demo. The cohort is synthetic, and neither GRAIMATTER "
            "demo approves a model.")


    d.prefix = ""

    s = d.slide("RELEASE GATE · DEMO/RUN_GATE.PY · CI", "One gate, four lenses: GRAIMATTER passes, Article 15(5) fails")
    d.table(s, LEFT, 2.1, 7.0, [
        ["Pack", "Controls", "Pass", "Fail", "Not evidenced"],
        ["EU AI Act 15(5), UK Code", "8", "2", "6", "0"],
        ["NIST AI 100-2", "6", "3", "3", "0"],
        ["GRAIMATTER TECH", "6", "5", "0", "1 (demo 2)"],
        ["NIST AI RMF, SR 26-02", "8", "5", "3", "0"],
    ], [2.6, 1.05, 0.9, 0.9, 1.55], size=13, row_h=0.46,
        highlight={(1, 3): PEACHBG, (2, 3): PEACHBG, (4, 3): PEACHBG, (3, 2): "#DCEBDD"})
    d.text(s, LEFT, 4.5, 7.0, 1.3, [
        [("Breached: ", True), ("evasion 78.7% (tolerance 10%), a copy agreeing 86.9% after one 200-row budget (80%), "
         "a backdoor lifting trigger success by 71.7 points (tolerance 10).", False)],
        [("Within: ", True), ("membership, attribute, holdout gap, stored rows, release checks, query budget, and "
         "the supply chain: no tampered file of demo 4 gets past the pin and the scan or floor.", False)],
    ], 13, BODY)
    d.card(s, LEFT + 7.35, 2.1, 4.2, 2.05, "Never a silent green",
           "A control whose demo did not run is not_evidenced, not pass. CI does not install sacroml, so it declares demo 2 "
           "out of scope with --accept-missing 2 and the report says so.", bsize=12.5)
    d.card(s, LEFT + 7.35, 4.3, 4.2, 2.05, "Read with SR 26-02",
           "A risk classifier is a model in the plain sense of model risk guidance. The TRE holdout (TECH 6) is the "
           "independent validation; the gate in CI is the ongoing monitoring.", dark=True, bsize=12.5)
    d.footer(s, "Tolerances are a demo risk appetite (ELA 8), not official cut-offs. Pattern from safety-trust-engine. "
                "demo/output/gate/.")
    d.notes(s, "The gate reruns demos 1, 3 and 4, reads the numbers they already print, and judges each regulatory control as "
            "pass, fail or not evidenced. The GRAIMATTER controls pass on the wrapped tree. The robustness controls fail on "
            "the forest of demo 3: privacy checks alone do not make a model resilient in the sense of Article 15(5), which "
            "also names poisoning and evasion. Its model-poisoning clause passes, because demo 4's pin, scan and floors "
            "refuse every tampered file. A control whose demo did not run is reported as not evidenced, never as pass; "
            "CI declares demo 2 out of scope explicitly because it does not install sacroml. The US pack reads the same "
            "evidence through NIST AI RMF MEASURE 2.6, 2.7 and 2.10 and federal model risk guidance, where a classifier fits "
            "directly. The tolerances are a risk appetite set for the workshop, and the mapping is this repository's own.")

    s = d.slide("RUN IT YOURSELF", "Five demos and a gate, reports under demo/output")
    d.rect(s, LEFT, 2.2, 6.2, 4.55, NAVY)
    d.text(s, LEFT + 0.3, 2.35, 5.7, 4.25, [
        "uv venv --python 3.11",
        "uv pip install -r demo/requirements.txt",
        "",
        "uv run python demo/run_aml_demo.py",
        "uv run python demo/run_supply_chain_demo.py",
        "uv run python demo/run_demo.py",
        "uv run python demo/run_sacroml_demo.py",
        "uv run python demo/run_stego_demo.py",
        "uv run python demo/run_gate.py",
        "",
        "# figures and this deck",
        "python docs/guide/make_figures.py",
        "python docs/guide/make_aml_figures.py",
        "python docs/make_deck.py",
    ], 12.0, CREAM, font=MONO)
    d.card(s, LEFT + 6.5, 2.2, 5.05, 1.3, "Demos 3 and 4 · seconds", "aml_report.txt: evasion, extraction, backdoor. "
           "supply_chain_report.txt: four tampered files.", bsize=12.5)
    d.card(s, LEFT + 6.5, 3.6, 5.05, 1.25, "Demos 1 and 6 · seconds", "demo_report.txt, register entry, release reports. "
           "stego_report.txt: two covert channels and their defences.", bsize=12.5)
    d.card(s, LEFT + 6.5, 4.95, 5.05, 1.5, "Demo 2 · a few minutes", "sacroml/sacroml_report.txt; report.json and report.pdf "
           "per attack.", bsize=12.5)
    d.footer(s, "Setup details: README.md. Section notes: demo/README.md. Guides: docs/guide/ (English and Spanish).")
    d.notes(s, "Setup is in the repository README: create a Python 3.11 environment with uv and install demo/requirements.txt, "
            "which brings numpy, scikit-learn and sacroml (and PyTorch with it). Demos 3, 4 and 1 run in seconds; demo 2 "
            "takes a few minutes. run_gate.py reruns the demos and writes the gate report to demo/output/gate; CI runs it on "
            "every pull request. The guides in docs/guide walk through every report section by section.")

    s = d.slide("REFERENCES", "Read further")
    d.text(s, LEFT, 2.1, WIDTH, 4.6, [
        [("NIST AI 100-2e2025. ", True), ("Vassilev, Oprea, Fordyce, Anderson, Davies, Hamin. Adversarial Machine Learning: A "
         "Taxonomy and Terminology of Attacks and Mitigations. March 2025. doi:10.6028/NIST.AI.100-2e2025 (in this "
         "repository).", False)],
        [("MITRE ATLAS. ", True), ("atlas.mitre.org, data release 2026.09.", False)],
        [("OWASP. ", True), ("Machine Learning Security Top 10 (2023, draft); Top 10 for LLM Applications 2025.", False)],
        [("EU. ", True), ("Regulation (EU) 2024/1689 (AI Act), Art. 15; Regulation (EU) 2026/1744 (Digital Omnibus on AI); "
         "EDPB Opinion 28/2024 on AI models.", False)],
        [("UK. ", True), ("DSIT Code of Practice for the Cyber Security of AI (Jan 2025); ETSI EN 304 223 (Jan 2026); NCSC "
         "and CISA, Guidelines for secure AI system development (Nov 2023).", False)],
        [("GRAIMATTER green paper. ", True), ("Recommendations for disclosure control of trained ML models from TREs. DARE UK, "
         "September 2022 (in this repository). SACRO-ML: github.com/AI-SDC/SACRO-ML.", False)],
    ], 13.5, BODY)
    d.notes(s, "Both PDFs, the NIST report and the green paper, are in the repository root. The guide, in English and "
            "Spanish, follows the same order as these slides, one part per video, and maps each section to its slides in "
            "Appendix A.")

    d.save()
    print("wrote", OUT, len(d.prs.slides), "slides")


if __name__ == "__main__":
    build()
