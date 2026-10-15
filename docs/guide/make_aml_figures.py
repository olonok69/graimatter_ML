"""Generate the adversarial-ML figures (part 1 and 2 of the deck and guide), in English and Spanish.

Run from the repository root:

    python docs/guide/make_aml_figures.py

Writes docs/guide/img/en/figA*.svg and docs/guide/img/es/figA*.svg, with the helpers and
palette of make_figures.py. Demo numbers are copied from demo/output/aml_report.txt.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_figures import (  # noqa: E402
    BLUE,
    BODY,
    BORDER,
    CARD,
    INK,
    MUTED,
    NAVY,
    ORANGE,
    OUT,
    PEACH,
    PEACHBG,
    RED,
    Svg,
    header,
)

# demo/output/aml_report.txt, seed 7
EVASION = [(0.787, 0.587), (0.328, 0.182), (0.207, 0.128)]  # (evaded, with one step)
QUERIES = [50, 200, 1000, 5000]
AGREE = [0.777, 0.869, 0.895, 0.935]
VIA_COPY = [0.220, 0.542, 0.583, 0.644]
DIRECT = 0.787
BACKDOOR = {  # fraction -> (trigger success, outlier screen catches)
    "loud": [(0.792, 0.70), (1.0, 0.80), (1.0, 0.42)],
    "quiet": [(0.94, 0.20), (1.0, 0.25), (1.0, 0.14)],
}

T = {
    "en": dict(
        sec="demo/output/aml_report.txt, section",
        a1_t="Where attacks land in the life of a model",
        a1_s="Stages of learning and attacker capabilities from NIST AI 100-2e2025 §2.1. Shaded band: what GRAIMATTER controls.",
        a1_stages=[
            ("Data", "collection, labelling, contributors"),
            ("Training", "code, libraries, pre-trained parts"),
            ("Model file", "weights, trees, support vectors"),
            ("Deployment", "API, app, agent with tools"),
        ],
        a1_cap=["training data control", "source code / model control", "access to the file (white box)", "query access, testing data control"],
        a1_att=[
            ["Data poisoning", "Backdoor (trigger)", "Clean-label poisoning", "Split-view web poisoning"],
            ["Model poisoning", "Malicious pre-trained model", "Poisoned dependency"],
            ["Reading stored rows", "Tampering after fit()", "Data hidden in parameters", "White-box privacy attacks"],
            ["Evasion", "Model extraction", "Membership, attribute inference", "Prompt injection (GenAI)"],
        ],
        a1_band="GRAIMATTER: the model file and its queries, privacy only",
        a1_foot="Integrity and availability attacks (poisoning, evasion) sit outside that band: demo 3 shows them.",
        a2_t="The NIST taxonomy of attacks on predictive AI",
        a2_s="Attacker objective first, then the attack class. IDs from the NIST AI 100-2e2025 index.",
        a2_cols=[
            ("Availability", "NISTAML.01", "Degrade the model for everyone",
             [("Data poisoning", ".013", ""), ("Model poisoning", ".011", ""), ("Clean-label poisoning", ".012", ""),
              ("Energy-latency", ".014", "")]),
            ("Integrity", "NISTAML.02", "Make it predict what the attacker wants",
             [("Evasion", ".022", ""), ("Black-box evasion", ".025", "demo 3"), ("Backdoor poisoning", ".023", "demo 3"),
              ("Targeted poisoning", ".024", ""), ("Clean-label backdoor", ".021", "")]),
            ("Privacy", "NISTAML.03", "Learn the training data or the model",
             [("Membership inference", ".033", "demos 1-2"), ("Reconstruction", ".032", "demo 1"),
              ("Property inference", ".034", ""), ("Model extraction", ".031", "demo 3")]),
        ],
        a2_attr="Attribute inference is a data-privacy objective in §2.1.2 and §2.4.1 (no separate ID): demos 1-2.",
        a2_supply="Supply chain, NISTAML.05: model poisoning through a third-party model (.051)",
        a2_genai="Generative AI adds: direct prompt injection (.018), indirect prompt injection (.015), misaligned outputs (.027)",
        a3_t="Evasion by misreporting a form (demo 3)",
        a3_s="Rows the forest scores high risk; each person tries the smallest edit first. Labels only, no model internals.",
        a3_sc=["smoking, weight and blood pressure self-reported", "smoking verified by a test", "smoking and weight measured in clinic"],
        a3_ev="evaded", a3_one="with a single step",
        a3_note="Checking the fields an attacker can lie about cuts evasion from 79% to 21%. Adversarial training would not stop a person from misreporting.",
        a4_t="Copying a model through its API, then using the copy (demo 3)",
        a4_s="The attacker invents rows inside the published ranges, queries the API, and trains a forest on the answers.",
        a4_x="queries sent to the API",
        a4_agree="copy agrees with the target on real rows",
        a4_via="flagged people who get past the target with edits planned on the copy",
        a4_direct="evading the target directly, querying it for every person",
        a4_budget="QueryGate budget: 200 rows",
        a4_note="200 rows already give an 87% copy of a simple model. A budget slows extraction; several accounts multiply it (NIST §2.4.5).",
        a5_t="A backdoor from 1-5% poisoned rows (demo 3)",
        a5_s="Copies of training rows with a trigger in two lab columns, labelled low risk. Test accuracy stays at 0.62-0.63.",
        a5_loud="Loud trigger: one lab value at 4.0", a5_quiet="Quiet trigger: two lab values at +1.7 and −1.7",
        a5_succ="high-risk scores the trigger flips", a5_caught="poison caught by an outlier screen",
        a5_x=["1% (20 rows)", "2% (40 rows)", "5% (100 rows)"],
        a5_note="A holdout accuracy check does not see the backdoor. The outlier screen finds part of a loud trigger and little of a quiet one.",
        a6_t="Who says what about adversarial ML",
        a6_s="Describe the attacks, rank the risks, require the controls. GRAIMATTER is a domain framework inside that picture.",
        a6_rows=["Describe", "Prioritise", "Require"],
        a6_cards=[
            (0, "NIST AI 100-2e2025", "March 2025", "Taxonomy and terms: objectives, capabilities, knowledge; mitigations and their limits."),
            (0, "MITRE ATLAS", "v2026.09", "Attacker tactics and techniques, like ATT&CK. 16 tactics, 73 case studies."),
            (1, "OWASP ML Top 10", "2023, draft", "Ten risks for teams that build models: ML01 input manipulation to ML10 model poisoning."),
            (1, "OWASP LLM Top 10", "2025", "Ten risks for LLM apps: LLM01 prompt injection to LLM10 unbounded consumption."),
            (2, "EU AI Act, Art. 15", "Annex III from Dec 2027", "High-risk systems must resist poisoning, adversarial examples, confidentiality attacks."),
            (2, "UK Code of Practice", "Jan 2025 → ETSI EN 304 223", "13 principles over 5 lifecycle phases; 3.1 names poisoning, inversion, membership."),
        ],
        a6_g="GRAIMATTER (2022): controls for releasing a model from a trusted research environment. Privacy branch only, in depth.",
    ),
    "es": dict(
        sec="demo/output/aml_report.txt, sección",
        a1_t="Dónde caen los ataques en la vida de un modelo",
        a1_s="Etapas y capacidades del atacante según NIST AI 100-2e2025 §2.1. Banda sombreada: lo que controla GRAIMATTER.",
        a1_stages=[
            ("Datos", "recogida, etiquetado, contribuidores"),
            ("Entrenamiento", "código, librerías, modelos base"),
            ("Fichero del modelo", "pesos, árboles, vectores soporte"),
            ("Despliegue", "API, app, agente con herramientas"),
        ],
        a1_cap=["control de datos de entrenamiento", "control de código o del modelo", "acceso al fichero (caja blanca)", "acceso por consultas, control de entradas"],
        a1_att=[
            ["Envenenamiento de datos", "Puerta trasera (disparador)", "Envenenamiento clean-label", "Envenenamiento web split-view"],
            ["Envenenamiento del modelo", "Modelo preentrenado malicioso", "Dependencia envenenada"],
            ["Leer filas guardadas", "Manipulación tras fit()", "Datos ocultos en parámetros", "Ataques de privacidad de caja blanca"],
            ["Evasión", "Extracción del modelo", "Inferencia de membresía y atributos", "Inyección de prompt (GenAI)"],
        ],
        a1_band="GRAIMATTER: el fichero del modelo y sus consultas, solo privacidad",
        a1_foot="Los ataques de integridad y disponibilidad (envenenamiento, evasión) quedan fuera de esa banda: la demo 3 los muestra.",
        a2_t="La taxonomía NIST de ataques a la IA predictiva",
        a2_s="Primero el objetivo del atacante, después la clase de ataque. Identificadores del índice de NIST AI 100-2e2025.",
        a2_cols=[
            ("Disponibilidad", "NISTAML.01", "Degradar el modelo para todos",
             [("Envenenamiento de datos", ".013", ""), ("Envenenamiento del modelo", ".011", ""),
              ("Envenenamiento clean-label", ".012", ""), ("Energía-latencia", ".014", "")]),
            ("Integridad", "NISTAML.02", "Que prediga lo que quiere el atacante",
             [("Evasión", ".022", ""), ("Evasión de caja negra", ".025", "demo 3"), ("Puerta trasera", ".023", "demo 3"),
              ("Envenenamiento dirigido", ".024", ""), ("Puerta trasera clean-label", ".021", "")]),
            ("Privacidad", "NISTAML.03", "Conocer los datos o el modelo",
             [("Inferencia de membresía", ".033", "demos 1-2"), ("Reconstrucción", ".032", "demo 1"),
              ("Inferencia de propiedades", ".034", ""), ("Extracción del modelo", ".031", "demo 3")]),
        ],
        a2_attr="La inferencia de atributos es un objetivo de privacidad de datos en §2.1.2 y §2.4.1 (sin identificador propio): demos 1-2.",
        a2_supply="Cadena de suministro, NISTAML.05: envenenamiento a través de un modelo de terceros (.051)",
        a2_genai="La IA generativa añade: inyección de prompt directa (.018), indirecta (.015), salidas desalineadas (.027)",
        a3_t="Evasión mintiendo en un formulario (demo 3)",
        a3_s="Filas que el bosque puntúa como alto riesgo; cada persona prueba primero el cambio más pequeño. Solo etiquetas.",
        a3_sc=["tabaco, peso y tensión declarados por el paciente", "tabaco verificado con una prueba", "tabaco y peso medidos en consulta"],
        a3_ev="evadidos", a3_one="con un solo paso",
        a3_note="Verificar los campos en los que se puede mentir baja la evasión del 79% al 21%. El entrenamiento adversario no impide que alguien mienta.",
        a4_t="Copiar un modelo a través de su API y usar la copia (demo 3)",
        a4_s="El atacante inventa filas dentro de los rangos publicados, consulta la API y entrena un bosque con las respuestas.",
        a4_x="consultas enviadas a la API",
        a4_agree="la copia coincide con el modelo real en filas reales",
        a4_via="personas señaladas que engañan al modelo con cambios planificados en la copia",
        a4_direct="evasión directa del modelo, consultándolo para cada persona",
        a4_budget="Presupuesto de QueryGate: 200 filas",
        a4_note="Con 200 filas ya hay una copia del 87% de un modelo sencillo. Un presupuesto frena la extracción; varias cuentas lo multiplican (NIST §2.4.5).",
        a5_t="Una puerta trasera con un 1-5% de filas envenenadas (demo 3)",
        a5_s="Copias de filas con un disparador en dos columnas de laboratorio, etiquetadas como bajo riesgo. La precisión sigue en 0,62-0,63.",
        a5_loud="Disparador visible: un valor de laboratorio a 4,0", a5_quiet="Disparador discreto: dos valores a +1,7 y −1,7",
        a5_succ="puntuaciones de alto riesgo que el disparador invierte", a5_caught="veneno detectado por un filtro de atípicos",
        a5_x=["1% (20 filas)", "2% (40 filas)", "5% (100 filas)"],
        a5_note="Una comprobación de precisión en holdout no ve la puerta trasera. El filtro de atípicos encuentra parte del disparador visible y poco del discreto.",
        a6_t="Quién dice qué sobre el ML adversario",
        a6_s="Describir los ataques, priorizar los riesgos, exigir los controles. GRAIMATTER es un marco de dominio dentro de ese mapa.",
        a6_rows=["Describir", "Priorizar", "Exigir"],
        a6_cards=[
            (0, "NIST AI 100-2e2025", "marzo de 2025", "Taxonomía y términos: objetivos, capacidades, conocimiento; mitigaciones y sus límites."),
            (0, "MITRE ATLAS", "v2026.09", "Tácticas y técnicas del atacante, como ATT&CK. 16 tácticas, 73 casos reales."),
            (1, "OWASP ML Top 10", "2023, borrador", "Diez riesgos para quien construye modelos: de ML01 manipulación de entradas a ML10 envenenamiento del modelo."),
            (1, "OWASP LLM Top 10", "2025", "Diez riesgos de aplicaciones con LLM: de LLM01 inyección de prompt a LLM10 consumo sin límites."),
            (2, "Ley de IA de la UE, art. 15", "anexo III desde dic. 2027", "Los sistemas de alto riesgo deben resistir envenenamiento, ejemplos adversarios y ataques a la confidencialidad."),
            (2, "Código de prácticas (RU)", "2025 → ETSI EN 304 223", "13 principios en 5 fases del ciclo de vida; el 3.1 cita envenenamiento, inversión y membresía."),
        ],
        a6_g="GRAIMATTER (2022): controles para sacar un modelo de un entorno de investigación seguro. Solo la rama de privacidad, en profundidad.",
    ),
}


def pct(v, lang, nd=0):
    s = f"{100 * v:.{nd}f}%"
    return s.replace(".", ",") if lang == "es" else s


def figA1(t, lang):
    s = Svg(1000, 560, t["a1_t"])
    header(s, t["a1_t"], t["a1_s"])
    x0, w, gap = 28, 224, 16
    s.rect(x0 + 2 * (w + gap) - 8, 96, 2 * w + gap + 16, 420, PEACHBG, ORANGE, sw=1.5, dash="6 4", opacity=0.9)
    s.text(x0 + 2 * (w + gap) + w + gap / 2, 506, t["a1_band"], 12.5, ORANGE, 600, "middle")
    for i, ((name, sub), cap, atts) in enumerate(zip(t["a1_stages"], t["a1_cap"], t["a1_att"])):
        x = x0 + i * (w + gap)
        s.rect(x, 108, w, 64, NAVY, None, rx=8)
        s.text(x + 14, 134, name, 16, PEACH, 600)
        s.text(x + 14, 156, sub, 11.5, "#D9DEE6")
        if i < 3:
            s.arrow(x + w + 1, 140, x + w + gap - 1, 140, sw=2)
        s.lines(x + 4, 196, cap, 12, MUTED, 500, width=34, italic=True)
        for j, a in enumerate(atts):
            y = 230 + j * 62
            s.rect(x, y, w, 50, CARD, BORDER, rx=6)
            s.lines(x + 12, y + 22, a, 13, INK, 500, width=30)
    s.lines(32, 540, t["a1_foot"], 12, MUTED, width=150, italic=True)
    return s


def figA2(t, lang):
    s = Svg(1000, 560, t["a2_t"])
    header(s, t["a2_t"], t["a2_s"])
    cols = [(28, ORANGE), (352, BLUE), (676, NAVY)]
    for (x, color), (name, code, goal, items) in zip(cols, t["a2_cols"]):
        s.rect(x, 92, 296, 318, CARD, BORDER)
        s.rect(x, 92, 296, 62, color, None, rx=10)
        s.text(x + 16, 118, name, 17, "#FFFFFF", 600)
        s.text(x + 280, 118, code, 12, "#FFFFFF", 500, "end", mono=True)
        s.text(x + 16, 142, goal, 12.5, "#F3F4F6")
        for j, (label, ident, demo) in enumerate(items):
            y = 172 + j * 46
            s.rect(x + 12, y, 272, 38, PEACHBG if demo else "#F1EFE8", ORANGE if demo else None, rx=6, sw=1.5)
            s.text(x + 24, y + 24, label, 13, INK, 500)
            if demo:
                s.text(x + 272, y + 24, demo, 11.5, ORANGE, 700, "end")
            else:
                s.text(x + 272, y + 24, ident, 11.5, MUTED, 500, "end", mono=True)
    s.lines(32, 434, t["a2_attr"], 12.5, BODY, width=150)
    s.rect(28, 452, 944, 36, PEACHBG, ORANGE, rx=8, sw=1.5)
    s.text(44, 475, t["a2_supply"], 13, NAVY, 600)
    s.text(956, 475, "demo 4", 11.5, ORANGE, 700, "end")
    s.rect(28, 498, 944, 36, NAVY, None, rx=8)
    s.text(44, 521, t["a2_genai"], 13, PEACH, 600)
    return s


def figA3(t, lang):
    s = Svg(1000, 350, t["a3_t"])
    header(s, t["a3_t"], t["a3_s"])
    x0, y0, w = 330, 104, 420
    for i, (lab, (ev, one)) in enumerate(zip(t["a3_sc"], EVASION)):
        y = y0 + i * 70
        s.lines(x0 - 14, y + 18, lab, 13, BODY, 500, "end", width=36, lh=1.2)
        s.rect(x0, y, w, 22, "#ECEAE3", None, rx=4)
        s.rect(x0, y, ev * w, 22, ORANGE, None, rx=4)
        s.text(x0 + ev * w + 8, y + 16, pct(ev, lang, 1) + " " + t["a3_ev"], 12.5, INK, 600)
        s.rect(x0, y + 28, one * w, 14, BLUE, None, rx=3)
        s.text(x0 + one * w + 8, y + 40, pct(one, lang, 1) + " " + t["a3_one"], 11.5, BLUE, 600)
    s.box(790, 104, 182, 196, "", None, dark=True)
    s.lines(804, 130, t["a3_note"], 13, "#D9DEE6", width=24)
    s.text(32, 334, t["sec"] + " 1", 12, MUTED, italic=True)
    return s


def figA4(t, lang):
    s = Svg(1000, 430, t["a4_t"])
    header(s, t["a4_t"], t["a4_s"])
    gx, gy, gw, gh = 70, 104, 560, 230
    s.line(gx, gy + gh, gx + gw, gy + gh, MUTED)
    s.line(gx, gy, gx, gy + gh, MUTED)
    for v in (0, 0.5, 1):
        s.text(gx - 8, gy + gh - v * gh + 4, pct(v, lang), 11, MUTED, anchor="end")
        s.line(gx, gy + gh - v * gh, gx + gw, gy + gh - v * gh, BORDER, 1)
    xs = [gx + 40 + i * (gw - 80) / 3 for i in range(4)]
    for x, q in zip(xs, QUERIES):
        s.text(x, gy + gh + 18, f"{q:,}".replace(",", "." if lang == "es" else ","), 12, BODY, 500, "middle")
    s.text(gx + gw / 2, gy + gh + 38, t["a4_x"], 12, MUTED, anchor="middle")
    bx = xs[1]
    s.line(bx, gy - 4, bx, gy + gh, NAVY, 2, dash="6 4")
    s.text(bx + 8, gy + gh - 10, t["a4_budget"], 11.5, NAVY, 600)
    ly = gy + gh - DIRECT * gh
    s.line(gx, ly, gx + gw, ly, RED, 1.8, dash="5 4")
    for vals, color in ((AGREE, NAVY), (VIA_COPY, ORANGE)):
        pts = [f"{x:.1f},{gy + gh - v * gh:.1f}" for x, v in zip(xs, vals)]
        s.path("M" + " L".join(pts), color, sw=2.5)
        for x, v in zip(xs, vals):
            s.circle(x, gy + gh - v * gh, 5, color)
            s.text(x, gy + gh - v * gh - 10, pct(v, lang), 11.5, color, 600, "middle")
    lx = 660
    for i, (color, key, dash) in enumerate(((NAVY, "a4_agree", None), (ORANGE, "a4_via", None), (RED, "a4_direct", "5 4"))):
        y = 116 + i * 58
        s.line(lx, y, lx + 26, y, color, 2.5, dash=dash)
        s.lines(lx + 34, y + 4, t[key], 12.5, BODY, width=36, lh=1.2)
    s.box(660, 290, 312, 92, "", None, accent=True)
    s.lines(674, 312, t["a4_note"], 12, BODY, width=48)
    s.text(32, 412, t["sec"] + " 2", 12, MUTED, italic=True)
    return s


def figA5(t, lang):
    s = Svg(1000, 420, t["a5_t"])
    header(s, t["a5_t"], t["a5_s"])
    for k, (key, x) in enumerate((("loud", 28), ("quiet", 512))):
        s.rect(x, 92, 460, 250, CARD, BORDER)
        s.text(x + 16, 118, t["a5_" + key], 14.5, NAVY, 600)
        gx, gy, gw, gh = x + 30, 140, 410, 150
        s.line(gx, gy + gh, gx + gw, gy + gh, MUTED)
        gwid = gw / 3
        for i, (succ, caught) in enumerate(BACKDOOR[key]):
            for j, (v, color) in enumerate(((succ, ORANGE), (caught, BLUE))):
                bw = (gwid - 40) / 2
                bx = gx + i * gwid + 20 + j * bw
                s.rect(bx + 3, gy + gh - v * gh, bw - 6, v * gh, color, None, rx=3)
                s.text(bx + bw / 2, gy + gh - v * gh - 6, pct(v, lang), 11.5, INK, 600, "middle")
            s.text(gx + i * gwid + gwid / 2, gy + gh + 18, t["a5_x"][i], 12, BODY, 500, "middle")
    s.circle(40, 362, 5, ORANGE)
    s.text(50, 367, t["a5_succ"], 12.5, BODY)
    s.circle(520, 362, 5, BLUE)
    s.text(530, 367, t["a5_caught"], 12.5, BODY)
    s.lines(32, 394, t["a5_note"], 12, MUTED, width=160, italic=True)
    return s


def figA6(t, lang):
    s = Svg(1000, 470, t["a6_t"])
    header(s, t["a6_t"], t["a6_s"])
    row_y = [92, 202, 312]
    for r, (label, y) in enumerate(zip(t["a6_rows"], row_y)):
        s.rect(28, y, 120, 98, NAVY, None, rx=8)
        s.text(88, y + 55, label, 15, PEACH, 600, "middle")
    slots = {0: 0, 1: 0, 2: 0}
    for row, name, when, body in t["a6_cards"]:
        x = 164 + slots[row] * 408
        slots[row] += 1
        y = row_y[row]
        s.rect(x, y, 396, 98, CARD, BORDER)
        s.text(x + 16, y + 28, name, 15.5, NAVY, 600)
        s.text(x + 380, y + 28, when, 11.5, ORANGE, 600, "end")
        s.lines(x + 16, y + 54, body, 12.5, BODY, width=60)
    s.rect(28, 424, 944, 34, PEACHBG, ORANGE, rx=8, sw=1.2)
    s.lines(44, 446, t["a6_g"], 12.5, INK, 600, width=150)
    return s


def main():
    for lang, t in T.items():
        d = os.path.join(OUT, lang)
        figs = {
            "figA1_lifecycle": figA1(t, lang), "figA2_taxonomy": figA2(t, lang), "figA3_evasion": figA3(t, lang),
            "figA4_extraction": figA4(t, lang), "figA5_backdoor": figA5(t, lang), "figA6_frameworks": figA6(t, lang),
        }
        for name, svg in figs.items():
            svg.save(os.path.join(d, name + ".svg"))
        print(lang, len(figs), "figures")


if __name__ == "__main__":
    main()
