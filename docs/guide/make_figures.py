"""Generate the SVG figures of the GRAIMATTER guide and deck, in English and Spanish.

Run from the repository root, with the demo environment active:

    python docs/guide/make_figures.py

Writes docs/guide/img/en/*.svg and docs/guide/img/es/*.svg.

Headline numbers are copied from the seeded reports (demo/output/demo_report.txt and
demo/output/sacroml/sacroml_report.txt). Two figures are computed live from the demo
code so they show what it actually does: the attribute sweep on the planted record
(fig03) and the confidence each tree gives to the true label (fig05).
"""
from __future__ import annotations

import os
import sys
from html import escape

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "demo"))
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

from graimatter_demo.case_study import sweep_unknown_fields, train_case_study_model  # noqa: E402
from graimatter_demo.cohort import BP_LEVELS, WEIGHT_LEVELS, hold_out_for_tre, sample_cohort  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "img")
SEED, N_ROWS, N_NOISE = 7, 1000, 10

# Palette shared with the slide deck (same family as the TurboQuant workshop)
NAVY, INK, MUTED = "#0F1B2D", "#1B2433", "#5F6979"
ORANGE, PEACH, PEACHBG = "#B4521A", "#F2A35E", "#FBE9DC"
CREAM, CARD, BORDER = "#F6F5F0", "#FDFCF9", "#E2DFD6"
BLUE, BLUEBG, GREY = "#2F6DB5", "#DCE7F5", "#C9CED6"
GREEN, GREENBG, RED, REDBG = "#2E7D4F", "#DDEFE3", "#B23A3A", "#F6DEDE"
BODY = "#3A4556"
FONT = "IBM Plex Sans, Segoe UI, Helvetica, Arial, sans-serif"
MONO = "Consolas, Courier New, Menlo, monospace"


# ---------------------------------------------------------------------------------------
# tiny SVG helpers
# ---------------------------------------------------------------------------------------
class Svg:
    def __init__(self, w, h, title):
        self.w, self.h, self.parts = w, h, []
        self.title = title
        self.rect(0, 0, w, h, CREAM, rx=0)

    def add(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, fill, stroke=None, rx=10, sw=1.5, dash=None, opacity=None):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        if dash:
            st += f' stroke-dasharray="{dash}"'
        op = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{st}{op}/>')

    def text(self, x, y, s, size=15, color=INK, weight=400, anchor="start", mono=False, italic=False):
        fam = MONO if mono else FONT
        it = ' font-style="italic"' if italic else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{weight}" '
                 f'fill="{color}" text-anchor="{anchor}"{it}>{escape(s)}</text>')

    def lines(self, x, y, s, size=15, color=INK, weight=400, anchor="start", width=30, lh=1.3, mono=False, italic=False):
        """Wrap s to about `width` characters per line; returns the y after the block."""
        out = []
        for para in s.split("\n"):
            cur = ""
            for word in para.split(" "):
                if cur and len(cur) + 1 + len(word) > width:
                    out.append(cur)
                    cur = word
                else:
                    cur = (cur + " " + word) if cur else word
            out.append(cur)
        for i, ln in enumerate(out):
            self.text(x, y + i * size * lh, ln, size, color, weight, anchor, mono, italic)
        return y + len(out) * size * lh

    def line(self, x1, y1, x2, y2, color=MUTED, sw=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{sw}"{d}/>')

    def arrow(self, x1, y1, x2, y2, color=ORANGE, sw=2.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{sw}"{d} '
                 f'marker-end="url(#arr)"/>')

    def path(self, d, stroke=INK, fill="none", sw=2, dash=None, opacity=None):
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<path d="{d}" stroke="{stroke}" fill="{fill}" stroke-width="{sw}"{ds}{op}/>')

    def circle(self, x, y, r, fill, stroke=None):
        st = f' stroke="{stroke}" stroke-width="1.5"' if stroke else ""
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"{st}/>')

    def box(self, x, y, w, h, title, body=None, dark=False, accent=False, fill=None, tsize=15, bsize=13, tcolor=None):
        """Card with a wrapped title and an optional wrapped body. Returns the y below the text."""
        bg = fill or (NAVY if dark else (PEACHBG if accent else CARD))
        self.rect(x, y, w, h, bg, None if dark else BORDER)
        tc = tcolor or (PEACH if dark else NAVY)
        bc = "#D9DEE6" if dark else BODY
        yy = self.lines(x + 14, y + 24, title, tsize, tc, 600, width=int((w - 28) / (tsize * 0.56)))
        if body:
            yy = self.lines(x + 14, yy + 4, body, bsize, bc, width=int((w - 28) / (bsize * 0.54)))
        return yy

    def save(self, path):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
                f'role="img" aria-label="{escape(self.title)}">\n<title>{escape(self.title)}</title>\n'
                f'<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                f'<path d="M0,0 L10,5 L0,10 z" fill="{ORANGE}"/></marker></defs>\n')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(head + "\n".join(self.parts) + "\n</svg>\n")


def header(s, title, subtitle=None):
    s.text(32, 44, title, 22, NAVY, 600)
    if subtitle:
        s.text(32, 70, subtitle, 14.5, MUTED)


def num(x, lang, nd=3):
    """Format a number with the decimal separator of the language."""
    s = f"{x:.{nd}f}"
    return s.replace(".", ",") if lang == "es" else s


# ---------------------------------------------------------------------------------------
# strings
# ---------------------------------------------------------------------------------------
T = {
    "en": dict(
        f00_t="What leaves the TRE is a model, not a table",
        f00_s="Two families of control (TECH 4): checks on the file before export, limits on queries after.",
        f00_tre="Trusted research environment (TRE)",
        f00_data="Sensitive rows", f00_datab="Pseudonymised records. They never leave.",
        f00_train="Researcher trains", f00_trainb="Inside the TRE, with ML tools the TRE provides (TECH 2).",
        f00_model="Trained model", f00_modelb="A file. It can still carry rows, leaves of one person, support vectors.",
        f00_mdc="MDC: model disclosure controls", f00_mdcb="Holdout, attack simulations, file type and size, safe wrappers (TECH 5-15).",
        f00_mqc="MQC: model query controls", f00_mqcb="Limit who can query and how many rows (TECH 16-17).",
        f00_users="End users", f00_usersb="Clinicians, other teams, the public.",
        f00_rt="Who the paper worries about:",
        f00_rt1="RT1 a well-meaning researcher who saves too much in the file",
        f00_rt2="RT2 a malicious researcher who hides data in the file",
        f00_rt3="RT3 an outside attacker who gets the released file",
        f01_t="Three ways a model file can carry people",
        f01_s="A model can be smaller than its training table and still disclose individual rows.",
        f01_1="Nearest neighbours", f01_1b="Stores every training row; predicting means looking them up. Demo: 500 of 500 rows, file 1.01x the table.",
        f01_2="Support-vector classifier", f01_2b="Keeps the training rows that sit near the boundary. Demo: 423 of 500 rows kept as support vectors.",
        f01_3="Deep decision tree", f01_3b="Splits until a leaf holds one person. Demo: smallest leaf 1 row, in a file of 18 KB against a 68 KB table.",
        f01_foot="Section 10.1 and 10.1.5 of the paper; numbers from demo/output/demo_report.txt.",
        f02_t="The holdout the researcher never sees (TECH 6)",
        f02_s="Synthetic cohort, seed 7. No real patients.",
        f02_all="1,000 synthetic rows", f02_res="500 rows to the researcher", f02_tre="500 rows kept by the TRE",
        f02_resb="Used to train the model.", f02_treb="Never shared. Used to score the model and to run attacks.",
        f02_cols="Columns", f02_clin="6 clinical: age, diabetes, asthma, weight (4 levels), blood pressure (5 levels), smoker",
        f02_noise="10 noise columns with no label signal: something for a deep tree to memorise",
        f02_lab="Label: high_risk, drawn from a known logistic function of the clinical columns",
        f03_t="Twenty queries recover two hidden fields (Appendix E)",
        f03_s="Known: age 62, diabetic, asthmatic, smoker. Unknown: weight and blood pressure. Cell = model confidence.",
        f03_w="weight", f03_bp="blood pressure",
        f03_wl=["underweight", "normal", "overweight", "obese"],
        f03_bl=["low", "slightly high", "high", "very high", "extremely high"],
        f03_win="Only one cell stands out: the planted truth.",
        f03_winb="The other 19 combinations tie at 0.500, so the attack has a unique answer: overweight and slightly high blood pressure. 20 rows of queries were enough.",
        f03_note="Computed live from graimatter_demo/case_study.py (unconstrained tree, planted record).",
        f04_t="Three ideas behind the attack metrics (Appendix F)",
        f04_a="1. AUC: the average", f04_ab="Pick one member and one non-member. AUC is the chance the attack scores the member higher. 0.5 is a coin toss.",
        f04_b="2. FDIF: the tail", f04_bb="Rank every row by attack score. FDIF = share of members in the top 10% minus share in the bottom 10%.",
        f04_c="3. How rare is a member?", f04_cb="P(member | flagged) = A·TPR / (A·TPR + (1−A)·FPR). Unconstrained tree: TPR 1.000, FPR 0.588.",
        f04_top="top 10%", f04_bot="bottom 10%", f04_mem="member", f04_non="non-member",
        f04_chance="chance", f04_auc_hi="separates", f04_x="A, share of members among candidates",
        f04_p05="A = 0.5: 0.630", f04_p01="A = 0.01: 0.017",
        f05_t="How sure is each tree about the true label?",
        f05_s="Confidence in the correct class for training rows (members) and set-aside rows. Share of rows per bin.",
        f05_u="Unconstrained tree", f05_w="Safe wrapper (leaf 20, depth 4)",
        f05_mem="training rows (members)", f05_non="set-aside rows",
        f05_x="confidence in the true label",
        f05_noteu="Pure leaves: every answer is 0 or 1. Members always 1; set-aside right 59% of the time.",
        f05_notew="Leaves of 20+ rows: similar spread for both groups, so membership is hard to tell.",
        f05_foot="Computed live from the seeded cohort. The label-aware worst-case attack sees this gap; a probability-only attack does not.",
        f06_t="Unconstrained tree versus safe wrapper, demo 1",
        f06_s="Worst-case attack on the same 500/500 split. Dashed line = demo policy limit (not a paper threshold).",
        f06_u="Unconstrained tree", f06_w="Safe wrapper",
        f06_m=["Membership AUC", "Advantage", "Train − set-aside", "TPR at 10% FPR", "FDIF"],
        f06_lim="limit", f06_dec_u="Refuse. Rules fired: accuracy gap, AUC, advantage, FDIF.", f06_dec_w="Release under the demo policy",
        f07_t="The quiet failure: AUC near chance, tail not (Appendix F)",
        f07_s="Safe-wrapper tree, two membership attacks. The export rule uses the worst-case attack.",
        f07_wc="Worst case (TRE tables)", f07_sa="Salem-synth (similar data)",
        f07_m=["AUC", "TPR at 10% FPR", "FDIF"],
        f07_p="p", f07_note="Salem FDIF 0.160 with p = 0.027: more members in the top scores than chance explains. A data controller could refuse on that.",
        f08_t="The safe wrapper, from constraints file to register (TECH 3, 9, 10)",
        f08_1="constraints.json", f08_1b="TRE risk appetite: min_samples_leaf ≥ 20, max_depth ≤ 4; kNN and SVC not permitted.",
        f08_2="Wrapper init", f08_2b="Corrects leaf 1 → 20 and depth None → 4, or records an override.",
        f08_3="fit()", f08_3b="Normal scikit-learn training. A digest of the tree is stored.",
        f08_4="request_release()", f08_4b="Saves the file, checks leaf size, compares parameters and digest with the fitted state.",
        f08_5="TRE attacks", f08_5b="Holdout accuracy, worst-case and Salem membership, attribute inference.",
        f08_6="Register + snapshot", f08_6b="data_use_register\n.json and\npipeline_snapshot\n.json",
        f08_tamper="Tamper path (RT1/RT2): parameters edited back after fit, attribute hidden_rows added, smallest leaf still 1 → \"Do not allow release\".",
        f09_t="A query budget that counts rows (TECH 16)",
        f09_s="Budget: 8 rows for this user. One HTTP request can carry many rows.",
        f09_q1="Request 1: one patient lookup", f09_q1b="1 row → allowed",
        f09_q2="Request 2: attribute sweep", f09_q2b="20 rows → refused (1 used, budget 8)",
        f09_budget="budget 8 rows", f09_used="used",
        f09_note="A real query-limited service also needs an external test (TECH 17). The demo only implements the gate.",
        f10_t="Differential privacy on a released mean (section 10.1.3, TECH 12)",
        f10_s="The attacker knows every age but one and must guess whether that person was included.",
        f10_l="Attacker accuracy (0.5 = coin toss)", f10_det="deterministic",
        f10_r="Error of the released mean at ε = 0.2", f10_one="one draw", f10_best="best of 50 draws",
        f10_note="Keeping the draw closest to the true mean undoes the noise. TRE staff choose the seed, without looking.",
        f11_t="Same cohort, two toolkits: what differs",
        f11_h1="Hand-written demo (run_demo.py)", f11_h2="sacroml 2.0.1 (run_sacroml_demo.py)",
        f11_rows=[
            ("Leaf rule", "min_samples_leaf 20 and max_depth 4 (stricter than Appendix D)", "min_samples_leaf 5, the package rules file"),
            ("Wrapped tree accuracy", "train 0.692, set-aside 0.584", "train 0.868, set-aside 0.566"),
            ("Membership attack", "Probabilities plus the true label → AUC 0.528", "Probabilities only → mean AUC 0.494"),
            ("Leaf check", "Smallest leaf 20 rows", "Smallest leaf 5 < 10 → k_anonymity_risk true"),
            ("Outcome", "Release under the demo policy", "\"Proceed to next step of checking\"; structural risk still true"),
        ],
        f12_t="Reading sacroml attribute inference: few guesses, all correct",
        f12_s="Unconstrained tree, training rows. Bar = share of the 500 rows that got a unique guess; label = correct / guesses.",
        f12_f=["diabetes", "asthma", "weight", "blood pressure", "smoker"],
        f12_none="no unique guess", f12_note="\"136/136\" means every unique guess was right, on 27% of the rows. It is not 136 of 500 correct.",
    ),
    "es": dict(
        f00_t="Lo que sale del TRE es un modelo, no una tabla",
        f00_s="Dos familias de controles (TECH 4): comprobaciones del fichero antes de exportarlo y límites a las consultas después.",
        f00_tre="Entorno de investigación seguro (TRE)",
        f00_data="Filas sensibles", f00_datab="Registros seudonimizados. Nunca salen.",
        f00_train="El investigador entrena", f00_trainb="Dentro del TRE, con las herramientas de ML que ofrece el TRE (TECH 2).",
        f00_model="Modelo entrenado", f00_modelb="Un fichero. Puede llevar filas, hojas de una persona, vectores de soporte.",
        f00_mdc="MDC: controles sobre el modelo", f00_mdcb="Holdout, simulación de ataques, tipo y tamaño de fichero, safe wrappers (TECH 5-15).",
        f00_mqc="MQC: controles sobre las consultas", f00_mqcb="Limitar quién consulta y cuántas filas (TECH 16-17).",
        f00_users="Usuarios finales", f00_usersb="Clínicos, otros equipos, el público.",
        f00_rt="A quién tiene en mente el paper:",
        f00_rt1="RT1 un investigador bienintencionado que guarda demasiado en el fichero",
        f00_rt2="RT2 un investigador malicioso que esconde datos en el fichero",
        f00_rt3="RT3 un atacante externo que consigue el fichero publicado",
        f01_t="Tres formas en que un modelo puede llevar personas dentro",
        f01_s="Un modelo puede ocupar menos que su tabla de entrenamiento y aun así revelar filas individuales.",
        f01_1="Vecinos más cercanos", f01_1b="Guarda todas las filas de entrenamiento; predecir es buscarlas. Demo: 500 de 500 filas, fichero 1,01x la tabla.",
        f01_2="Clasificador de vectores soporte", f01_2b="Conserva las filas cercanas a la frontera. Demo: 423 de 500 filas guardadas como vectores soporte.",
        f01_3="Árbol de decisión profundo", f01_3b="Divide hasta que una hoja contiene a una persona. Demo: hoja mínima de 1 fila, en 18 KB frente a una tabla de 68 KB.",
        f01_foot="Secciones 10.1 y 10.1.5 del paper; cifras de demo/output/demo_report.txt.",
        f02_t="El holdout que el investigador nunca ve (TECH 6)",
        f02_s="Cohorte sintética, semilla 7. Sin pacientes reales.",
        f02_all="1.000 filas sintéticas", f02_res="500 filas para el investigador", f02_tre="500 filas que guarda el TRE",
        f02_resb="Se usan para entrenar el modelo.", f02_treb="Nunca se comparten. Sirven para evaluar el modelo y lanzar ataques.",
        f02_cols="Columnas", f02_clin="6 clínicas: edad, diabetes, asma, peso (4 niveles), tensión arterial (5 niveles), fumador",
        f02_noise="10 columnas de ruido sin señal: algo que un árbol profundo puede memorizar",
        f02_lab="Etiqueta: high_risk, generada con una función logística conocida de las columnas clínicas",
        f03_t="Veinte consultas recuperan dos campos ocultos (Anexo E)",
        f03_s="Conocido: 62 años, diabético, asmático, fumador. Desconocido: peso y tensión. Celda = confianza del modelo.",
        f03_w="peso", f03_bp="tensión arterial",
        f03_wl=["bajo peso", "normal", "sobrepeso", "obesidad"],
        f03_bl=["baja", "algo alta", "alta", "muy alta", "extremadamente alta"],
        f03_win="Solo destaca una celda: la verdad plantada.",
        f03_winb="Las otras 19 combinaciones empatan a 0,500, así que el ataque tiene una respuesta única: sobrepeso y tensión algo alta. Bastaron 20 filas de consultas.",
        f03_note="Calculado en vivo con graimatter_demo/case_study.py (árbol sin restricciones, registro plantado).",
        f04_t="Tres ideas detrás de las métricas de ataque (Anexo F)",
        f04_a="1. AUC: la media", f04_ab="Toma un miembro y un no miembro. El AUC es la probabilidad de que el ataque puntúe más al miembro. 0,5 es lanzar una moneda.",
        f04_b="2. FDIF: la cola", f04_bb="Ordena las filas por puntuación. FDIF = proporción de miembros en el 10% superior menos la del 10% inferior.",
        f04_c="3. ¿Cuán raro es un miembro?", f04_cb="P(miembro | señalado) = A·TPR / (A·TPR + (1−A)·FPR). Árbol sin restricciones: TPR 1,000, FPR 0,588.",
        f04_top="10% superior", f04_bot="10% inferior", f04_mem="miembro", f04_non="no miembro",
        f04_chance="azar", f04_auc_hi="separa", f04_x="A, proporción de miembros entre los candidatos",
        f04_p05="A = 0,5: 0,630", f04_p01="A = 0,01: 0,017",
        f05_t="¿Cuán seguro está cada árbol de la etiqueta real?",
        f05_s="Confianza en la clase correcta para filas de entrenamiento (miembros) y del holdout. Proporción de filas por intervalo.",
        f05_u="Árbol sin restricciones", f05_w="Safe wrapper (hoja 20, profundidad 4)",
        f05_mem="filas de entrenamiento (miembros)", f05_non="filas del holdout",
        f05_x="confianza en la etiqueta real",
        f05_noteu="Hojas puras: cada respuesta es 0 o 1. Los miembros siempre 1; el holdout acierta el 59%.",
        f05_notew="Hojas de 20 filas o más: reparto parecido en ambos grupos; cuesta distinguir la pertenencia.",
        f05_foot="Calculado en vivo con la cohorte sembrada. El ataque de peor caso con etiqueta ve esta diferencia; uno solo con probabilidades, no.",
        f06_t="Árbol sin restricciones frente a safe wrapper, demo 1",
        f06_s="Ataque de peor caso sobre la misma partición 500/500. Línea discontinua = límite de la política de la demo (no del paper).",
        f06_u="Árbol sin restricciones", f06_w="Safe wrapper",
        f06_m=["AUC de membresía", "Ventaja", "Entreno − holdout", "TPR al 10% de FPR", "FDIF"],
        f06_lim="límite", f06_dec_u="Rechazo. Reglas que saltan: brecha de precisión, AUC, ventaja, FDIF.", f06_dec_w="Se libera según la política de la demo",
        f07_t="El fallo silencioso: AUC cerca del azar, la cola no (Anexo F)",
        f07_s="Árbol con safe wrapper, dos ataques de membresía. La regla de exportación usa el de peor caso.",
        f07_wc="Peor caso (tablas del TRE)", f07_sa="Salem-synth (datos parecidos)",
        f07_m=["AUC", "TPR al 10% de FPR", "FDIF"],
        f07_p="p", f07_note="FDIF de Salem 0,160 con p = 0,027: hay más miembros en las puntuaciones altas de lo que explica el azar. Un responsable de datos podría rechazar por eso.",
        f08_t="El safe wrapper, del fichero de restricciones al registro (TECH 3, 9, 10)",
        f08_1="constraints.json", f08_1b="Apetito de riesgo del TRE: min_samples_leaf ≥ 20, max_depth ≤ 4; kNN y SVC no permitidos.",
        f08_2="Init del wrapper", f08_2b="Corrige hoja 1 → 20 y profundidad None → 4, o registra un override.",
        f08_3="fit()", f08_3b="Entrenamiento normal de scikit-learn. Se guarda un resumen (digest) del árbol.",
        f08_4="request_release()", f08_4b="Guarda el fichero, comprueba la hoja mínima y compara parámetros y digest con el estado entrenado.",
        f08_5="Ataques del TRE", f08_5b="Precisión en holdout, membresía de peor caso y Salem, inferencia de atributos.",
        f08_6="Registro + snapshot", f08_6b="data_use_register\n.json y\npipeline_snapshot\n.json",
        f08_tamper="Camino manipulado (RT1/RT2): parámetros cambiados tras fit, atributo hidden_rows añadido, hoja mínima aún 1 → \"Do not allow release\".",
        f09_t="Un presupuesto de consultas que cuenta filas (TECH 16)",
        f09_s="Presupuesto: 8 filas para este usuario. Una sola petición HTTP puede llevar muchas filas.",
        f09_q1="Petición 1: consulta de un paciente", f09_q1b="1 fila → permitida",
        f09_q2="Petición 2: barrido de atributos", f09_q2b="20 filas → rechazada (1 usada, presupuesto 8)",
        f09_budget="presupuesto 8 filas", f09_used="usada",
        f09_note="Un servicio real con límites también necesita una prueba externa (TECH 17). La demo solo implementa la puerta.",
        f10_t="Privacidad diferencial sobre una media publicada (sección 10.1.3, TECH 12)",
        f10_s="El atacante conoce todas las edades menos una y debe adivinar si esa persona estaba incluida.",
        f10_l="Acierto del atacante (0,5 = moneda al aire)", f10_det="determinista",
        f10_r="Error de la media publicada con ε = 0,2", f10_one="una extracción", f10_best="mejor de 50",
        f10_note="Quedarse con la extracción más parecida a la media real anula el ruido. El personal del TRE elige la semilla, sin mirar.",
        f11_t="Misma cohorte, dos herramientas: qué cambia",
        f11_h1="Demo propia (run_demo.py)", f11_h2="sacroml 2.0.1 (run_sacroml_demo.py)",
        f11_rows=[
            ("Regla de hoja", "min_samples_leaf 20 y max_depth 4 (más estricta que el Anexo D)", "min_samples_leaf 5, fichero de reglas del paquete"),
            ("Precisión del árbol con wrapper", "entreno 0,692, holdout 0,584", "entreno 0,868, holdout 0,566"),
            ("Ataque de membresía", "Probabilidades más la etiqueta real → AUC 0,528", "Solo probabilidades → AUC medio 0,494"),
            ("Control de hojas", "Hoja mínima de 20 filas", "Hoja mínima 5 < 10 → k_anonymity_risk true"),
            ("Resultado", "Se libera según la política de la demo", "\"Proceed to next step of checking\"; el riesgo estructural sigue en true"),
        ],
        f12_t="Cómo leer la inferencia de atributos de sacroml: pocas conjeturas, todas correctas",
        f12_s="Árbol sin restricciones, filas de entrenamiento. Barra = proporción de las 500 filas con conjetura única; etiqueta = correctas / conjeturas.",
        f12_f=["diabetes", "asma", "peso", "tensión arterial", "fumador"],
        f12_none="sin conjetura única", f12_note="\"136/136\" significa que todas las conjeturas únicas acertaron, en el 27% de las filas. No son 136 aciertos de 500.",
    ),
}


# ---------------------------------------------------------------------------------------
# live data from the demo code
# ---------------------------------------------------------------------------------------
def live_data():
    case_model, planted = train_case_study_model(np.random.default_rng(SEED + 1))
    sweep = sweep_unknown_fields(case_model.predict_proba, planted)
    grid = np.zeros((len(WEIGHT_LEVELS), len(BP_LEVELS)))
    for row in sweep:
        grid[WEIGHT_LEVELS.index(row["weight"]), BP_LEVELS.index(row["blood_pressure"])] = row["confidence"]

    rng = np.random.default_rng(SEED)
    features, target = sample_cohort(N_ROWS, rng, n_noise=N_NOISE)
    researcher_ids, holdout_ids = hold_out_for_tre(N_ROWS, rng, holdout_fraction=0.5)
    rx, ry = features[researcher_ids], target[researcher_ids]
    hx, hy = features[holdout_ids], target[holdout_ids]
    conf = {}
    for key, params in {"u": dict(min_samples_leaf=1, max_depth=None), "w": dict(min_samples_leaf=20, max_depth=4)}.items():
        model = DecisionTreeClassifier(random_state=SEED, **params).fit(rx, ry)
        conf[key] = (model.predict_proba(rx)[np.arange(len(ry)), ry], model.predict_proba(hx)[np.arange(len(hy)), hy])
    return grid, conf


# ---------------------------------------------------------------------------------------
# figures
# ---------------------------------------------------------------------------------------
def fig00(t, lang):
    s = Svg(1000, 500, t["f00_t"])
    header(s, t["f00_t"], t["f00_s"])
    s.rect(24, 92, 548, 290, "#EEF1F5", NAVY, sw=2, dash="6 4")
    s.text(40, 116, t["f00_tre"], 14, NAVY, 600)
    s.box(40, 130, 156, 160, t["f00_data"], t["f00_datab"])
    s.box(222, 130, 156, 160, t["f00_train"], t["f00_trainb"])
    s.box(404, 130, 156, 160, t["f00_model"], t["f00_modelb"], accent=True)
    s.arrow(198, 210, 218, 210)
    s.arrow(380, 210, 400, 210)
    s.box(40, 302, 520, 70, t["f00_mdc"], t["f00_mdcb"], dark=True, tsize=14, bsize=12)
    s.arrow(562, 210, 600, 210)
    s.box(604, 130, 170, 160, t["f00_mqc"], t["f00_mqcb"], dark=True, tsize=14, bsize=12)
    s.arrow(776, 210, 806, 210)
    s.box(810, 130, 166, 160, t["f00_users"], t["f00_usersb"])
    s.text(32, 414, t["f00_rt"], 14, NAVY, 600)
    for i, k in enumerate(("f00_rt1", "f00_rt2", "f00_rt3")):
        s.circle(40, 436 + i * 22 - 5, 4, ORANGE)
        s.text(52, 436 + i * 22, t[k], 13.5, BODY)
    return s


def fig01(t, lang):
    s = Svg(1000, 400, t["f01_t"])
    header(s, t["f01_t"], t["f01_s"])
    xs = [28, 345, 662]
    keys = [("f01_1", "f01_1b"), ("f01_2", "f01_2b"), ("f01_3", "f01_3b")]
    for x, (a, b) in zip(xs, keys):
        s.rect(x, 96, 310, 254, CARD, BORDER)
        s.text(x + 16, 124, t[a], 16, NAVY, 600)
        s.lines(x + 16, 148, t[b], 13, BODY, width=44)
    # icons
    rng = np.random.default_rng(3)
    for i in range(36):  # kNN: every point stored
        px, py = 60 + (i % 12) * 20, 250 + (i // 12) * 22
        s.circle(px, py, 6, ORANGE if i % 3 else NAVY)
    for i in range(30):  # SVC: points near the boundary kept
        px, py = 380 + rng.uniform(0, 240), 238 + rng.uniform(0, 90)
        near = abs((py - 238) - (px - 380) * 0.37) < 18
        s.circle(px, py, 5.5 if near else 4, ORANGE if near else GREY)
    s.line(380, 238, 620, 327, NAVY, 2, dash="5 4")
    # tree with a leaf of one
    s.circle(817, 238, 8, NAVY)
    for x2, y2 in ((757, 278), (877, 278)):
        s.line(817, 238, x2, y2, MUTED, 1.5)
        s.circle(x2, y2, 8, NAVY)
    for x1, x2 in ((757, 727), (757, 787), (877, 847), (877, 907)):
        s.line(x1, 278, x2, 318, MUTED, 1.5)
    for x2, n in ((727, "34"), (787, "51"), (847, "28"), (907, "1")):
        s.rect(x2 - 17, 310, 34, 24, PEACHBG if n == "1" else CARD, ORANGE if n == "1" else BORDER, rx=5, sw=2 if n == "1" else 1.5)
        s.text(x2, 327, n, 13, ORANGE if n == "1" else BODY, 700 if n == "1" else 400, "middle")
    s.text(32, 380, t["f01_foot"], 12.5, MUTED, italic=True)
    return s


def fig02(t, lang):
    s = Svg(1000, 380, t["f02_t"])
    header(s, t["f02_t"], t["f02_s"])
    s.rect(28, 96, 944, 36, NAVY, None, rx=8)
    s.text(500, 120, t["f02_all"], 15, "#FFFFFF", 600, "middle")
    s.arrow(250, 134, 250, 158)
    s.arrow(750, 134, 750, 158)
    s.box(28, 162, 460, 86, t["f02_res"], t["f02_resb"], fill=BLUEBG)
    s.box(512, 162, 460, 86, t["f02_tre"], t["f02_treb"], accent=True)
    s.text(28, 284, t["f02_cols"], 14, NAVY, 600)
    s.text(28, 308, "• " + t["f02_clin"], 13, BODY)
    s.text(28, 330, "• " + t["f02_noise"], 13, BODY)
    s.text(28, 352, "• " + t["f02_lab"], 13, BODY)
    return s


def fig03(t, lang, grid):
    s = Svg(1000, 420, t["f03_t"])
    header(s, t["f03_t"], t["f03_s"])
    x0, y0, cw, ch = 190, 128, 118, 62
    for j, lab in enumerate(t["f03_bl"]):
        s.lines(x0 + j * cw + cw / 2, y0 - 22, lab, 12.5, BODY, 500, "middle", width=14, lh=1.15)
    for i, lab in enumerate(t["f03_wl"]):
        s.text(x0 - 12, y0 + i * ch + ch / 2 + 5, lab, 13, BODY, 500, "end")
        for j in range(len(t["f03_bl"])):
            v = grid[i, j]
            top = v == grid.max()
            fill = ORANGE if top else ("#E9E6DE" if v >= 0.5 else CARD)
            s.rect(x0 + j * cw + 3, y0 + i * ch + 3, cw - 6, ch - 6, fill, None if top else BORDER, rx=6)
            s.text(x0 + j * cw + cw / 2, y0 + i * ch + ch / 2 + 6, num(v, lang), 15,
                   "#FFFFFF" if top else BODY, 700 if top else 400, "middle")
    s.text(x0 - 12, y0 - 14, t["f03_w"] + " ↓  " + t["f03_bp"] + " →", 12, MUTED, anchor="end")
    s.box(790, 128, 182, 244, t["f03_win"], t["f03_winb"], dark=True, tsize=15)
    s.text(32, 402, t["f03_note"], 12.5, MUTED, italic=True)
    return s


def fig04(t, lang):
    s = Svg(1000, 440, t["f04_t"])
    header(s, t["f04_t"])
    for k, x in enumerate((28, 345, 662)):
        s.rect(x, 70, 310, 350, CARD, BORDER)
    # panel 1: AUC, two score distributions
    s.text(44, 98, t["f04_a"], 16, NAVY, 600)
    s.lines(44, 122, t["f04_ab"], 12.5, BODY, width=46)
    bx, by, bw, bh = 52, 210, 262, 120

    def bell(mu, sd, color, op):
        pts = []
        for i in range(61):
            z = i / 60
            y = np.exp(-0.5 * ((z - mu) / sd) ** 2)
            pts.append(f"{bx + z * bw:.1f},{by + bh - y * (bh - 10):.1f}")
        s.path("M" + f"{bx},{by + bh} L" + " L".join(pts) + f" L{bx + bw},{by + bh} Z", color, color, 1.5, opacity=op)

    bell(0.42, 0.13, BLUE, 0.35)
    bell(0.62, 0.13, ORANGE, 0.35)
    s.line(bx, by + bh, bx + bw, by + bh, MUTED)
    s.circle(60, 360, 5, BLUE)
    s.text(70, 365, t["f04_non"], 12, BODY)
    s.circle(170, 360, 5, ORANGE)
    s.text(180, 365, t["f04_mem"], 12, BODY)
    s.text(44, 398, f"AUC 0{',' if lang == 'es' else '.'}5 = {t['f04_chance']} · AUC 1 = {t['f04_auc_hi']}", 12.5, MUTED)
    # panel 2: FDIF, a ranked strip
    s.text(361, 98, t["f04_b"], 16, NAVY, 600)
    s.lines(361, 122, t["f04_bb"], 12.5, BODY, width=46)
    rng = np.random.default_rng(1)
    labels = rng.random(40) < 0.5
    labels[:4] = True
    labels[-4:] = False
    for i in range(40):
        col, row = i % 10, i // 10
        s.rect(365 + col * 27, 206 + row * 30, 22, 24, ORANGE if labels[i] else BLUE, None, rx=4,
               opacity=1 if (i < 4 or i >= 36) else 0.45)
    s.text(365, 200, t["f04_top"] + " →", 12, NAVY, 600)
    s.text(635, 346, "← " + t["f04_bot"], 12, NAVY, 600, "end")
    s.text(361, 398, "FDIF = 4/4 − 0/4 = 1", 12.5, MUTED, mono=True)
    # panel 3: posterior against base rate
    s.text(678, 98, t["f04_c"], 16, NAVY, 600)
    s.lines(678, 122, t["f04_cb"], 12.5, BODY, width=46)
    px, py, pw, ph = 700, 200, 250, 150
    s.line(px, py + ph, px + pw, py + ph, MUTED)
    s.line(px, py, px, py + ph, MUTED)
    pts = []
    for i in range(0, 101):
        a = 10 ** (-3 + 3 * i / 100)
        p = a * 1.0 / (a * 1.0 + (1 - a) * 0.588)
        pts.append(f"{px + i / 100 * pw:.1f},{py + ph - p * ph:.1f}")
    s.path("M" + " L".join(pts), ORANGE, sw=2.5)
    for a, lab in ((0.5, t["f04_p05"]), (0.01, t["f04_p01"])):
        p = a / (a + (1 - a) * 0.588)
        xx = px + (np.log10(a) + 3) / 3 * pw
        yy = py + ph - p * ph
        s.circle(xx, yy, 5, NAVY)
        s.text(xx - 8 if a > 0.1 else xx - 4, yy - 10 if a > 0.1 else yy - 34, lab, 12, NAVY, 600, "end" if a > 0.1 else "start")
    for a in (0.001, 0.01, 0.1, 1):
        xx = px + (np.log10(a) + 3) / 3 * pw
        s.text(xx, py + ph + 16, num(a, lang, 3).rstrip("0").rstrip(",.") if a < 1 else "1", 11, MUTED, anchor="middle")
    s.text(px + pw / 2, py + ph + 34, t["f04_x"], 11.5, MUTED, anchor="middle")
    s.text(px - 6, py + 4, "1", 11, MUTED, anchor="end")
    s.text(px - 6, py + ph, "0", 11, MUTED, anchor="end")
    return s


def fig05(t, lang, conf):
    s = Svg(1000, 440, t["f05_t"])
    header(s, t["f05_t"], t["f05_s"])
    bins = np.linspace(0, 1, 11)
    for k, (key, x) in enumerate((("u", 28), ("w", 512))):
        s.rect(x, 90, 460, 300, CARD, BORDER)
        s.text(x + 16, 116, t["f05_" + key], 16, NAVY, 600)
        members, non = conf[key]
        hm = np.histogram(np.clip(members, 0, 0.9999), bins)[0] / len(members)
        hn = np.histogram(np.clip(non, 0, 0.9999), bins)[0] / len(non)
        gx, gy, gw, gh = x + 40, 140, 400, 170
        s.line(gx, gy + gh, gx + gw, gy + gh, MUTED)
        for b in range(10):
            bw = gw / 10
            for j, (h, col) in enumerate(((hm[b], ORANGE), (hn[b], BLUE))):
                hh = h * gh
                s.rect(gx + b * bw + 4 + j * (bw - 8) / 2, gy + gh - hh, (bw - 8) / 2, hh, col, None, rx=2)
        for v in (0, 0.5, 1):
            s.text(gx + v * gw, gy + gh + 16, num(v, lang, 1), 11, MUTED, anchor="middle")
        s.text(gx + gw / 2, gy + gh + 32, t["f05_x"], 11.5, MUTED, anchor="middle")
        s.text(gx - 6, gy + 4, "100%", 10.5, MUTED, anchor="end")
        s.text(gx - 6, gy + gh, "0", 10.5, MUTED, anchor="end")
        s.lines(x + 16, 368, t["f05_note" + key], 12.5, BODY, width=72)
    s.circle(40, 410, 5, ORANGE)
    s.text(50, 415, t["f05_mem"], 12.5, BODY)
    s.circle(290, 410, 5, BLUE)
    s.text(300, 415, t["f05_non"], 12.5, BODY)
    s.lines(32, 433, t["f05_foot"], 11.5, MUTED, width=160, italic=True)
    return s


def bars(s, lang, x0, y0, w, h, labels, series, colors, limits=None, vmax=1.0, extra=None):
    """Grouped bar chart. series: list of lists (one per group member); extra: optional label suffixes."""
    n = len(labels)
    gw = w / n
    s.line(x0, y0 + h, x0 + w, y0 + h, MUTED)
    k = len(series)
    bw = (gw - 30) / k
    for i in range(n):
        if limits and limits[i] is not None:
            ly = y0 + h - limits[i] / vmax * h
            s.line(x0 + i * gw + 8, ly, x0 + (i + 1) * gw - 8, ly, RED, 1.8, dash="5 4")
        for j in range(k):
            v = series[j][i]
            hh = v / vmax * h
            bx = x0 + i * gw + 15 + j * bw
            s.rect(bx + 3, y0 + h - hh, bw - 6, hh, colors[j], None, rx=3)
            lab = num(v, lang) + (extra[j][i] if extra else "")
            s.rect(bx + bw / 2 - 4.2 * len(lab) - 3, y0 + h - hh - 21, 8.4 * len(lab) + 6, 17, CREAM, None, rx=3)
            s.text(bx + bw / 2, y0 + h - hh - 8, lab, 12, INK, 600, "middle")
        s.lines(x0 + i * gw + gw / 2, y0 + h + 18, labels[i], 12.5, BODY, 500, "middle", width=18, lh=1.15)


def fig06(t, lang):
    s = Svg(1000, 430, t["f06_t"])
    header(s, t["f06_t"], t["f06_s"])
    u = [0.708, 0.412, 0.410, 0.156, 0.620]
    w = [0.528, 0.004, 0.108, 0.116, 0.020]
    lim = [0.62, 0.20, 0.15, 0.35, 0.20]
    bars(s, lang, 40, 110, 720, 230, t["f06_m"], [u, w], [ORANGE, BLUE], lim, vmax=0.8)
    s.box(790, 110, 182, 112, t["f06_u"], t["f06_dec_u"], fill=REDBG, tcolor=RED)
    s.box(790, 234, 182, 106, t["f06_w"], t["f06_dec_w"], fill=GREENBG, tcolor=GREEN)
    s.circle(46, 400, 5, ORANGE)
    s.text(56, 405, t["f06_u"], 12.5, BODY)
    s.circle(260, 400, 5, BLUE)
    s.text(270, 405, t["f06_w"], 12.5, BODY)
    s.line(430, 400, 460, 400, RED, 2, dash="5 4")
    s.text(468, 405, t["f06_lim"], 12.5, BODY)
    return s


def fig07(t, lang):
    s = Svg(1000, 410, t["f07_t"])
    header(s, t["f07_t"], t["f07_s"])
    wc = [0.528, 0.116, 0.020]
    sa = [0.512, 0.118, 0.160]
    pw, ps = (" (p " + num(0.445, lang) + ")", " (p " + num(0.027, lang) + ")")
    bars(s, lang, 40, 110, 600, 200, t["f07_m"], [wc, sa], [BLUE, ORANGE], vmax=0.6,
         extra=[["", "", pw], ["", "", ps]])
    s.box(670, 110, 302, 140, "FDIF", t["f07_note"], dark=True)
    s.circle(46, 384, 5, BLUE)
    s.text(56, 389, t["f07_wc"], 12.5, BODY)
    s.circle(290, 384, 5, ORANGE)
    s.text(300, 389, t["f07_sa"], 12.5, BODY)
    return s


def fig08(t, lang):
    s = Svg(1000, 400, t["f08_t"])
    header(s, t["f08_t"])
    keys = [("f08_1", "f08_1b"), ("f08_2", "f08_2b"), ("f08_3", "f08_3b"),
            ("f08_4", "f08_4b"), ("f08_5", "f08_5b"), ("f08_6", "f08_6b")]
    w, gap = 146, 13
    for i, (a, b) in enumerate(keys):
        x = 28 + i * (w + gap)
        s.box(x, 76, w, 196, t[a], t[b], dark=(i == 3), accent=(i == 0), tsize=14, bsize=12)
        if i < 5:
            s.arrow(x + w + 1, 174, x + w + gap - 1, 174, sw=2)
    s.rect(28, 300, 944, 74, REDBG, RED, sw=1.5, dash="6 4")
    s.lines(46, 328, t["f08_tamper"], 13.5, RED, 500, width=130)
    return s


def fig09(t, lang):
    s = Svg(1000, 330, t["f09_t"])
    header(s, t["f09_t"], t["f09_s"])
    x0, unit = 40, 22
    for k, (a, b, n, ok) in enumerate(((t["f09_q1"], t["f09_q1b"], 1, True), (t["f09_q2"], t["f09_q2b"], 20, False))):
        y = 110 + k * 86
        s.text(x0, y, a, 14, NAVY, 600)
        s.text(x0 + 600, y + 32, b, 14, GREEN if ok else RED, 600)
        start = 0
        if not ok:  # the row already spent by request 1
            s.rect(x0, y + 12, unit, 30, GREY, None, rx=4)
            s.text(x0 + unit / 2, y + 58, t["f09_used"], 11, MUTED, anchor="middle")
            start = 1
        for i in range(n):
            xx = x0 + (start + i) * (unit + 4)
            if ok:
                s.rect(xx, y + 12, unit, 30, GREEN, None, rx=4)
            else:
                s.rect(xx, y + 12, unit, 30, REDBG, RED, rx=4, sw=1.5)
    bx = x0 + 8 * (unit + 4) - 2
    s.line(bx, 96, bx, 262, NAVY, 2.5, dash="6 4")
    s.text(bx + 6, 274, t["f09_budget"], 12.5, NAVY, 600)
    s.text(32, 310, t["f09_note"], 12.5, MUTED, italic=True)
    return s


def fig10(t, lang):
    s = Svg(1000, 420, t["f10_t"])
    header(s, t["f10_t"], t["f10_s"])
    s.rect(28, 90, 560, 280, CARD, BORDER)
    s.text(44, 116, t["f10_l"], 15, NAVY, 600)
    labs = [t["f10_det"], "ε = 8" + (",0" if lang == "es" else ".0"), "ε = 1" + (",0" if lang == "es" else ".0"), "ε = 0" + (",2" if lang == "es" else ".2")]
    vals = [1.000, 0.703, 0.522, 0.487]
    gx, gy, gw, gh = 60, 140, 500, 180
    s.line(gx, gy + gh, gx + gw, gy + gh, MUTED)
    for i, (lab, v) in enumerate(zip(labs, vals)):
        bw = gw / 4
        hh = v * gh
        s.rect(gx + i * bw + 22, gy + gh - hh, bw - 44, hh, ORANGE if i == 0 else BLUE, None, rx=3)
        s.text(gx + i * bw + bw / 2, gy + gh - hh - 6, num(v, lang), 12.5, INK, 600, "middle")
        s.text(gx + i * bw + bw / 2, gy + gh + 18, lab, 12.5, BODY, 500, "middle")
    ly = gy + gh - 0.5 * gh
    s.line(gx, ly, gx + gw, ly, RED, 2, dash="5 4")
    s.text(gx + gw, ly - 6, "0" + (",5" if lang == "es" else ".5"), 11.5, RED, 600, "end")
    s.rect(612, 90, 360, 280, CARD, BORDER)
    s.text(628, 116, t["f10_r"], 15, NAVY, 600)
    for i, (lab, v, col) in enumerate(((t["f10_one"], 0.3053, BLUE), (t["f10_best"], 0.0084, RED))):
        y = 160 + i * 70
        s.text(628, y, lab, 13, BODY, 500)
        ww = v / 0.32 * 300
        s.rect(628, y + 10, max(ww, 4), 28, col, None, rx=3)
        s.text(628 + max(ww, 4) + 8, y + 30, num(v, lang, 4), 13, INK, 600)
    s.lines(628, 318, t["f10_note"], 12.5, BODY, width=56)
    s.text(32, 400, "demo/output/demo_report.txt, section 3", 12, MUTED, italic=True)
    return s


def fig11(t, lang):
    s = Svg(1000, 430, t["f11_t"])
    header(s, t["f11_t"])
    cols = (28, 240, 610)
    widths = (200, 358, 362)
    s.rect(cols[1], 70, widths[1], 40, BLUE, None, rx=8)
    s.text(cols[1] + 14, 96, t["f11_h1"], 14, "#FFFFFF", 600)
    s.rect(cols[2], 70, widths[2], 40, NAVY, None, rx=8)
    s.text(cols[2] + 14, 96, t["f11_h2"], 14, PEACH, 600)
    for i, (a, b, c) in enumerate(t["f11_rows"]):
        y = 120 + i * 60
        s.rect(28, y, 944, 54, CARD if i % 2 == 0 else "#F1EFE8", BORDER, rx=6)
        s.lines(cols[0] + 12, y + 24, a, 13, NAVY, 600, width=26)
        s.lines(cols[1] + 14, y + 22, b, 13, BODY, width=50)
        s.lines(cols[2] + 14, y + 22, c, 13, RED if i in (3, 4) else BODY, 500 if i in (3, 4) else 400, width=50)
    return s


def fig12(t, lang):
    s = Svg(1000, 380, t["f12_t"])
    header(s, t["f12_t"], t["f12_s"])
    data = [(136, 136), None, None, (5, 5), (198, 198)]
    x0, y0, rowh, w = 190, 100, 40, 600
    for i, (lab, d) in enumerate(zip(t["f12_f"], data)):
        y = y0 + i * rowh
        s.text(x0 - 12, y + 22, lab, 13.5, BODY, 500, "end")
        s.rect(x0, y + 6, w, 24, "#ECEAE3", None, rx=4)
        if d is None:
            s.text(x0 + 10, y + 23, t["f12_none"], 12.5, MUTED, italic=True)
            continue
        guesses, correct = d
        ww = guesses / 500 * w
        s.rect(x0, y + 6, max(ww, 3), 24, ORANGE, None, rx=4)
        pct = f"{guesses / 500 * 100:.0f}%"
        s.text(x0 + max(ww, 3) + 8, y + 23, f"{correct}/{guesses}  ·  {pct}", 13, INK, 600)
    s.box(820, 100, 152, 196, "136/136", t["f12_note"], dark=True, tsize=16, bsize=12)
    s.text(32, 340, "demo/output/sacroml/sacroml_report.txt · demo/output/sacroml/unconstrained_tree/attribute/report.json", 12, MUTED, italic=True)
    return s


def main():
    grid, conf = live_data()
    for lang, t in T.items():
        d = os.path.join(OUT, lang)
        figs = {
            "fig00_overview": fig00(t, lang), "fig01_leaks": fig01(t, lang), "fig02_holdout": fig02(t, lang),
            "fig03_attribute_sweep": fig03(t, lang, grid), "fig04_metrics": fig04(t, lang),
            "fig05_confidence": fig05(t, lang, conf), "fig06_trees": fig06(t, lang), "fig07_tail": fig07(t, lang),
            "fig08_wrapper": fig08(t, lang), "fig09_query_budget": fig09(t, lang), "fig10_dp": fig10(t, lang),
            "fig11_two_demos": fig11(t, lang), "fig12_guess_coverage": fig12(t, lang),
        }
        for name, svg in figs.items():
            svg.save(os.path.join(d, name + ".svg"))
        print(lang, len(figs), "figures")
    print("planted sweep max", grid.max(), "| members mean conf u/w",
          round(float(conf["u"][0].mean()), 3), round(float(conf["w"][0].mean()), 3),
          "| set-aside u/w", round(float(conf["u"][1].mean()), 3), round(float(conf["w"][1].mean()), 3))


if __name__ == "__main__":
    main()
