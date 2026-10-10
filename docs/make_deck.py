"""Build the GRAIMATTER workshop deck (docs/GRAIMATTER.pptx).

Run from the repository root, after docs/guide/make_figures.py:

    python docs/make_deck.py

Needs python-pptx and cairosvg (docs/requirements-docs.txt). The figures are the English
SVGs from docs/guide/img/en, rendered to PNG on the fly. Numbers on the slides come from
demo/output/demo_report.txt and demo/output/sacroml/sacroml_report.txt; speaker notes
carry the definitions.
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
from pptx.util import Emu, Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "guide", "img", "en")
OUT = os.path.join(HERE, "GRAIMATTER.pptx")


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
            self.text(s, LEFT, 0.89, WIDTH, 0.3, kicker, 12, PEACH if dark else ORANGE, font=MONO)
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
        props.title, props.author, props.last_modified_by, props.comments = "GRAIMATTER", "", "", ""
        self.prs.save(OUT)


def build():
    d = Deck()

    # 1 ---------------------------------------------------------------------------------
    s = d.slide("DARE UK · GRAIMATTER GREEN PAPER · SEPTEMBER 2022", "Disclosure control for models leaving a TRE",
                dark=True, title_size=54)
    s.shapes.title.top, s.shapes.title.height = Inches(1.95), Inches(2.2)
    s.shapes[1].top = Inches(1.45)  # kicker sits just above the title
    d.rect(s, 0, 0, 0.17, 7.5, ORANGE, shape=MSO_SHAPE.RECTANGLE)
    s.shapes[-1].top = 0
    d.text(s, LEFT, 4.4, 10.5, 0.9, "What the green paper recommends before a trained model leaves a trusted research "
           "environment, and what two demos found on synthetic data", 22, "#D9DEE6")
    d.chips(s, LEFT, 5.45, ["1,000 synthetic rows", "17 TECH recommendations", "2 demos: hand-written + sacroml 2.0.1"])
    d.footer(s, "Green Paper: Recommendations for disclosure control of trained ML models from TREs · GRAIMatter sprint, "
             "University of Dundee and partners", dark=True)
    d.notes(s, "This session explains one question: when a researcher trains a model inside a trusted research environment, "
            "how does the TRE decide whether the model file is safe to export? The source is the GRAIMATTER green paper, "
            "a 99-page output of a DARE UK sprint published in September 2022. We cover the technical recommendations and "
            "then two demos that run those checks on a synthetic cohort. Legal, ethics, costing, training and public "
            "involvement are in the paper; we touch them only briefly. Nothing in the demos is a real patient.")

    # 2 ---------------------------------------------------------------------------------
    s = d.slide("THE PROBLEM", "The export is the model, not a table of patients")
    d.image(s, "fig01_leaks", top=2.25, max_h=4.2)
    d.footer(s, "Paper §10.1 and §10.1.5 (pp. 35, 39-40). Demo numbers: demo/output/demo_report.txt, sections 4 and 6.")
    d.notes(s, "TREs know how to check a table: no cell should describe fewer than k people. A trained model is different. "
            "It is rarely readable by a person, and some model types carry rows inside them. A nearest-neighbour model "
            "stores every training row. A support-vector classifier keeps the rows near its decision boundary. A deep "
            "decision tree can keep splitting until a leaf describes one person. The file size does not warn you: the "
            "demo's deep tree is 18 KB against a 68 KB training table and still has a leaf of one row. The paper also "
            "warns that a malicious researcher could hide data inside the many numbers of a model, like steganography.")

    # 3 ---------------------------------------------------------------------------------
    s = d.slide("TECH 4 · TWO FAMILIES OF CONTROL", "Check the file before it leaves, then limit its queries")
    d.image(s, "fig00_overview", top=2.2, max_h=4.45)
    d.footer(s, "TECH 4 (p. 42). Risk types RT1-RT3 from the executive summary (p. 23).")
    d.notes(s, "TECH 4 splits controls into two families. Model disclosure controls, MDCs, act on the file before export: "
            "a holdout set, attack simulations, file type and size checks, safe wrappers, and extra controls for models "
            "that memorise. Model query controls, MQCs, act after release: the model stays on a server and the TRE limits "
            "who can query it and how much. The paper names three risk types. RT1 is a well-meaning researcher who "
            "saves too much in the file. RT2 is a malicious researcher who hides data on purpose. RT3 is an outside "
            "attacker who gets hold of the released model.")

    # 4 ---------------------------------------------------------------------------------
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

    # 5 ---------------------------------------------------------------------------------
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

    # 6 ---------------------------------------------------------------------------------
    s = d.slide("APPENDIX E · ATTRIBUTE INFERENCE", "One planted person: 20 queries recover two hidden fields")
    d.image(s, "fig03_attribute_sweep", top=2.2, max_h=4.3)
    d.footer(s, "Appendix E §20.1 (pp. 86-87). Demo: demo/output/demo_report.txt, section 2.")
    d.notes(s, "This is the paper's first case study, rebuilt on synthetic data. An attacker knows four public facts about "
            "someone: age 62, diabetic, asthmatic, smoker. They do not know weight or blood pressure. Weight has four "
            "levels and blood pressure five, so there are 20 combinations. The attacker sends all 20 to the model and "
            "looks at the confidence. Models are usually more confident on inputs they were trained on. Here one cell "
            "is at 1.000 and the other 19 tie at 0.500, so the unique best guess is the hidden truth: overweight and "
            "slightly high. Attribute inference means filling in hidden fields of a person by querying the model.")

    # 7 ---------------------------------------------------------------------------------
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

    # 8 ---------------------------------------------------------------------------------
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

    # 9 ---------------------------------------------------------------------------------
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

    # 10 --------------------------------------------------------------------------------
    s = d.slide("APPENDIX F · THE TAIL", "The quiet failure: AUC near 0.5, but FDIF 0.280")
    d.image(s, "fig07_tail", top=2.2, max_h=4.0)
    d.footer(s, "demo/output/demo_report.txt, section 5 (Salem-synth). Appendix A Table 2 describes the Salem scenarios.")
    d.notes(s, "On the same wrapped tree we also run Salem-synth, where the attacker trains a shadow model on similar "
            "data rather than on the TRE's own tables. Its AUC is 0.512, close to chance. But its FDIF is 0.280 with "
            "p = 0.003, and TPR at 10% FPR is 0.252: members pile up in the extreme scores. This is exactly the "
            "Appendix F warning: an average metric can hide a tail. The demo's export rule follows the worst-case "
            "attack, whose FDIF is 0.020, so it still releases. A data controller who cares about the tail could refuse.")

    # 11 --------------------------------------------------------------------------------
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

    # 12 --------------------------------------------------------------------------------
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

    # 13 --------------------------------------------------------------------------------
    s = d.slide("TECH 16 · MODEL QUERY CONTROLS", "Count rows, not calls: one patient allowed, 20 blocked")
    d.image(s, "fig09_query_budget", top=2.3, max_h=3.6)
    d.footer(s, "TECH 16-17 (pp. 52-53), §10.1.7 (pp. 40-41). Demo: demo_report.txt, section 8.")
    d.notes(s, "If the model stays on a server, the TRE can limit queries. The demo gate gives one user a budget of 8 rows. "
            "A clinician's single patient lookup uses 1 row and is allowed. Then the same user sends the 20-combination "
            "sweep from the attribute case study in one request. The gate refuses it: 20 rows requested, 1 already used, "
            "budget 8. The unit matters. If the budget counted HTTP calls, one call carrying 20 rows would pass. TECH 17 "
            "says a real query-limited service should be tested by an external party; the demo implements only the "
            "control logic.")

    # 14 --------------------------------------------------------------------------------
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

    # 15 --------------------------------------------------------------------------------
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

    # 16 --------------------------------------------------------------------------------
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

    # 17 --------------------------------------------------------------------------------
    s = d.slide("DEMO 2 · ATTRIBUTE INFERENCE", "'136/136' means every unique guess was right")
    d.image(s, "fig12_guess_coverage", top=2.25, max_h=3.6)
    d.text(s, LEFT, 6.05, WIDTH, 0.6, "Wrapped tree, training rows: diabetes 195/257, asthma 50/67, smoker 254/327; "
           "weight and blood pressure no unique guess. Age: reconstructed fraction 0.034 (set-aside 0.050).", 13, BODY)
    d.footer(s, "demo/output/sacroml/sacroml_report.txt. Appendix G (p. 96) describes the unique-guess attack.")
    d.notes(s, "Read every sacroml attribute cell as correct unique guesses over unique guesses made, out of 500 rows. For "
            "each row the attack tries every value of one field and guesses only when one value gives a uniquely highest "
            "confidence; otherwise it abstains. On the unconstrained tree, diabetes is 136 out of 136: perfect, but only "
            "on the 27% of rows where it was willing to guess. Smoker is 198 out of 198, 40% coverage. Asthma and weight "
            "get no unique guess at all. The set-aside numbers are similar, which is why the paper asks to compare "
            "training and held-out rows. Age is numeric, so it is reported as a fraction reconstructed within bounds.")

    # 18 --------------------------------------------------------------------------------
    s = d.slide("TWO DEMOS COMPARED", "Leaf 20 vs 5, label-aware vs probability-only")
    d.image(s, "fig11_two_demos", top=2.2, max_h=4.3)
    d.footer(s, "demo_report.txt section 10 and sacroml_report.txt. Appendix D (p. 83) example leaf size: 5.")
    d.notes(s, "Three differences matter. First, the leaf rule: the hand-written wrapper forces leaf 20 and depth 4, the "
            "package rules file forces leaf 5. Second, the membership attack: probabilities plus label versus "
            "probabilities only. Third, the outcome: the hand-written script releases the stricter tree because its own "
            "attack falls inside the demo limits; the package never approves anything here, it says to continue "
            "checking, and its structural attack still flags the leaf-5 tree. Neither is an approval process. A real "
            "TRE would combine these checks with a policy agreed with its data controller.")

    # 19 --------------------------------------------------------------------------------
    s = d.slide("WHAT THE PAPER ALSO ASKS FOR", "The rest of the technical list")
    items = [
        ("TECH 1", "Discuss disclosure risk when the project is applied for."),
        ("TECH 2", "Give researchers ML tools inside the TRE."),
        ("TECH 3", "Snapshot the pipeline behind an approved model."),
        ("TECH 5", "Staff who can run and read the attacks."),
        ("TECH 13", "Special treatment for ensembles."),
        ("TECH 14", "Test the final model from federated learning."),
        ("TECH 15", "Treat synthetic data as personal data."),
        ("TECH 17", "External test of any query-limited service."),
    ]
    for i, (a, b) in enumerate(items):
        x = LEFT + (i % 2) * 5.85
        y = 2.2 + (i // 2) * 0.82
        d.rect(s, x, y, 5.6, 0.68, CARD, BORDER)
        d.text(s, x + 0.2, y, 1.2, 0.68, a, 15, ORANGE, True, anchor=MSO_ANCHOR.MIDDLE)
        d.text(s, x + 1.35, y, 4.1, 0.68, b, 14, BODY, anchor=MSO_ANCHOR.MIDDLE)
    d.rect(s, LEFT, 5.55, WIDTH, 0.95, NAVY)
    d.text(s, LEFT + 0.25, 5.55, WIDTH - 0.5, 0.95, [[("Appendix A, experiment 2: ", True), ("hyperparameters that looked "
           "safe on one dataset were risky on another. A range from a previous dataset is not, by itself, a release "
           "decision; run the attacks on the model in hand.", False)]], 14, CREAM, anchor=MSO_ANCHOR.MIDDLE)
    d.footer(s, "§10.2 (pp. 41-53). Appendix A §16.2 (p. 76).")
    d.notes(s, "These recommendations are not demonstrated but belong in the picture. Risk is discussed at application time, "
            "TREs provide ML tools, and the pipeline of an approved model is kept for audit. TREs need staff who can run "
            "the attacks. Ensembles and federated learning get special attention, synthetic data is still personal data, "
            "and a query-limited service should be tested externally. Appendix A's second experiment is the reason the "
            "demo still runs attacks after the wrapper: hyperparameters that looked safe on one dataset were risky on "
            "another.")

    # 20 --------------------------------------------------------------------------------
    s = d.slide("LIMITS", "What this repository does not decide")
    lim = [
        ("A real risk appetite", "The demo cut-offs are local. ELA 8: thresholds are agreed with the data controller."),
        ("Legal text", "Researcher declarations are plain language. EULA and clause text need a qualified legal review."),
        ("LiRA", "In sacroml, not run here. The upstream example uses 100 shadow models."),
        ("A private SVM", "Not implemented. DP is sketched on a released mean only."),
        ("Real patients", "None. One synthetic cohort, seed 7, 1,000 rows."),
        ("Approval", "Neither demo is an approval process; sacroml says 'proceed to next step of checking'."),
    ]
    for i, (a, b) in enumerate(lim):
        x = LEFT + (i % 3) * 3.95
        y = 2.2 + (i // 3) * 2.15
        d.card(s, x, y, 3.65, 1.95, a, b, bsize=13)
    d.footer(s, "docs/brief-for-presentation-and-guide.md, 'Claims to keep accurate'.")
    d.notes(s, "Be explicit about the edges. The cut-offs in disclosure.py exist so the first script can say yes or no; the "
            "paper publishes no universal thresholds. No legal clauses were drafted. LiRA, the likelihood-ratio attack, "
            "is available in the package but this demo does not run it. There is no differentially private SVM. The "
            "cohort is synthetic. And neither demo approves a model: the hand-written one releases under its own policy, "
            "the package recommends further checking.")

    # 21 --------------------------------------------------------------------------------
    s = d.slide("RUN IT YOURSELF", "Two scripts, one environment, reports under demo/output")
    d.rect(s, LEFT, 2.2, 6.2, 3.9, NAVY)
    d.text(s, LEFT + 0.3, 2.45, 5.7, 3.5, [
        "uv venv --python 3.11",
        "uv pip install -r demo/requirements.txt",
        "",
        "uv run python demo/run_demo.py",
        "uv run python demo/run_sacroml_demo.py",
        "",
        "# figures and this deck",
        "python docs/guide/make_figures.py",
        "python docs/make_deck.py",
    ], 14, CREAM, font=MONO)
    d.card(s, LEFT + 6.5, 2.2, 5.05, 1.85, "Demo 1 · seconds", "demo/output/demo_report.txt, data_dictionary.json, "
           "data_use_register.json, pipeline_snapshot.json, release reports.", bsize=12.5)
    d.card(s, LEFT + 6.5, 4.25, 5.05, 1.85, "Demo 2 · a few minutes", "demo/output/sacroml/sacroml_report.txt; report.json "
           "and report.pdf per attack (worst_case, structural, attribute); safe_release/target.yaml.", bsize=12.5)
    d.footer(s, "Setup details: README.md. Section notes: demo/README.md. Guides: docs/guide/ (English and Spanish).")
    d.notes(s, "Setup is in the repository README: create a Python 3.11 environment with uv and install "
            "demo/requirements.txt, which brings numpy, scikit-learn and sacroml (and PyTorch with it). On Windows "
            "PowerShell, activate with a leading dot. The first script runs in seconds and writes demo_report.txt; the "
            "second takes a few minutes, about three and a half on the seeded run, and writes JSON and PDF reports per "
            "attack. The guide in docs/guide walks through both reports section by section.")

    # 22 --------------------------------------------------------------------------------
    s = d.slide("REFERENCES", "Read further")
    d.text(s, LEFT, 2.2, WIDTH, 4.3, [
        [("GRAIMATTER green paper. ", True), ("Recommendations for disclosure control of trained Machine Learning (ML) "
         "models from Trusted Research Environments (TREs). DARE UK sprint GRAIMatter, September 2022. "
         "GRAIMATTER Green Paper.pdf in this repository. Earlier version: Jefferson et al., Zenodo, "
         "doi:10.5281/zenodo.6896214.", False)],
        [("SACRO-ML. ", True), ("github.com/AI-SDC/SACRO-ML (sacroml 2.0.1), maintained toolkit from the AI-SDC "
         "repository named in the paper.", False)],
        [("Salem et al. ", True), ("ML-Leaks: model and data independent membership inference attacks and defenses "
         "(paper reference [37]); basis of the Salem scenarios in Appendix A.", False)],
        [("Five Safes. ", True), ("F. Ritchie, The 'Five Safes': a framework for planning, designing and evaluating "
         "data access solutions, Zenodo 2017 (paper reference [2]).", False)],
        [("This repository. ", True), ("README.md, demo/README.md, docs/brief-for-presentation-and-guide.md, "
         "docs/guide/GRAIMATTER_Technical_Guide_EN.md and GRAIMATTER_Guia_Tecnica_ES.md.", False)],
    ], 14, BODY)
    d.notes(s, "The PDF is in the repository root. SACRO-ML is the package used in the second demo. The guide, in English "
            "and Spanish, follows the same order as these slides and maps each section to its slides in Appendix A.")

    d.save()
    print("wrote", OUT, len(d.prs.slides), "slides")


if __name__ == "__main__":
    build()
