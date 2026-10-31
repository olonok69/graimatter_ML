# Las demos, explicadas: recorrido por el código y la salida

**Qué hace cada demo, cómo lo hace el código y cómo leer lo que imprime**

Esta guía trata de los cuatro scripts de demo de `demo/` y de la puerta de publicación que los juzga. La [guía técnica](AML_Guia_Tecnica_ES.md) explica los ataques y los marcos, y la [guía del presentador](Guia_Presentador_ES.md) sigue las diapositivas. Esta guía sigue el código: para cada sección que imprime una demo, dice qué funciones la producen, qué calculan y qué significan las cifras que aparecen en pantalla. También está disponible en [inglés](Demo_Guide_EN.md), con los mismos números de sección.

Los números de sección coinciden con las demos. La sección 1 es la demo 1, la sección 2 es la demo 2, y así sucesivamente; la sección 5 es la puerta. Dentro de las demos 1, 3 y 4, la subsección *N* corresponde a la sección que el script imprime como *N*: §1.4 es lo que `run_demo.py` imprime bajo "4. Unconstrained tree", §4.2 es lo que `run_supply_chain_demo.py` imprime bajo "2. A swapped model". Los comentarios del código remiten aquí con esos números, como `Demo guide §1.4`.

Todas las cifras citadas salen de las ejecuciones sembradas que están versionadas en `demo/output/`. Todo es sintético; no hay pacientes reales en ninguna parte del repositorio.

---

## Contenido

0. [Antes de las demos: cómo ejecutarlas, la estructura y el código compartido](#0-antes-de-las-demos-cómo-ejecutarlas-la-estructura-y-el-código-compartido)
1. [Demo 1: las comprobaciones de GRAIMATTER, escritas a mano](#1-demo-1-las-comprobaciones-de-graimatter-escritas-a-mano)
2. [Demo 2: las mismas comprobaciones con SACRO-ML](#2-demo-2-las-mismas-comprobaciones-con-sacro-ml)
3. [Demo 3: evasión, extracción y un backdoor](#3-demo-3-evasión-extracción-y-un-backdoor)
4. [Demo 4: una cadena de suministro manipulada](#4-demo-4-una-cadena-de-suministro-manipulada)
5. [La puerta de publicación](#5-la-puerta-de-publicación)
6. [Reproducibilidad y salvedades conocidas](#6-reproducibilidad-y-salvedades-conocidas)

---

## 0. Antes de las demos: cómo ejecutarlas, la estructura y el código compartido

### 0.1 Cómo ejecutar las demos

Desde la raíz del repositorio, después de `uv sync` (o `uv sync --extra sacroml` para la demo 2):

```bash
uv run python demo/run_demo.py               # demo 1, seconds
uv run python demo/run_sacroml_demo.py       # demo 2, a few minutes, needs sacroml
uv run python demo/run_aml_demo.py           # demo 3, seconds
uv run python demo/run_supply_chain_demo.py  # demo 4, seconds
uv run python demo/run_gate.py               # reruns the demos and judges them
```

Cada script imprime su informe en el terminal y guarda el mismo texto en `demo/output/`. En un taller el orden suele ser 3, 4, 1, 2 y después la puerta, porque las diapositivas explican primero los ataques generales y después GRAIMATTER; la numeración sigue el orden en que se escribieron las demos.

| Script | Informe | Otras salidas |
| --- | --- | --- |
| `run_demo.py` (demo 1) | `demo/output/demo_report.txt` | `data_dictionary.json`, `safe_tree.release.json`, `tampered_tree.release.json`, `data_use_register.json`, `pipeline_snapshot.json`, `not_a_model.txt`; ficheros de modelo (`*.joblib`, no versionados) |
| `run_sacroml_demo.py` (demo 2) | `demo/output/sacroml/sacroml_report.txt` | `sacroml/<model>/<attack>/report.json` (y `report.pdf`, no versionado), `sacroml/safe_release/target.yaml` |
| `run_aml_demo.py` (demo 3) | `demo/output/aml_report.txt` | ninguna |
| `run_supply_chain_demo.py` (demo 4) | `demo/output/supply_chain_report.txt` | ficheros de trabajo en `demo/output/supply_chain/` (no versionados) |
| `run_gate.py` | `demo/output/gate/gate_<packs>.json` y `.md` | código de salida 0 o 1 |

### 0.2 Dónde está el código

```
demo/
  run_demo.py               demo 1 script
  run_sacroml_demo.py       demo 2 script
  run_aml_demo.py           demo 3 script
  run_supply_chain_demo.py  demo 4 script
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

### 0.3 La cohorte sintética (`graimatter_demo/cohort.py`)

Las cuatro demos sacan sus datos de `sample_cohort(n, rng, n_noise)`. Cada fila es una persona ficticia:

| Columna | Índice | Valores | Papel |
| --- | --- | --- | --- |
| `age` | 0 | de 30 a 89 | clínica |
| `diabetes` | 1 | 0 o 1 | clínica |
| `asthma` | 2 | 0 o 1 | clínica |
| `weight` | 3 | de 0 a 3 (bajo peso, normal, sobrepeso, obesidad) | clínica |
| `blood_pressure` | 4 | de 0 a 4 (de baja a extremadamente alta) | clínica |
| `smoker` | 5 | 0 o 1 | clínica |
| `noise_0`, `noise_1`, ... | del 6 en adelante | normal estándar | sin relación con la etiqueta |

La etiqueta `high_risk` se genera con una función logística conocida:

```
logit = -1.35 + 0.034·(age − 55) + 0.9·smoker + 0.55·diabetes + 0.22·asthma
        + 0.32·[weight ≥ overweight] + 0.30·[blood pressure ≥ high]
high_risk ~ Bernoulli(1 / (1 + e^−logit))
```

Hay dos consecuencias que aparecen en todas las demos:

* **La etiqueta tiene ruido a propósito.** Dos personas con las mismas columnas pueden tener etiquetas distintas, porque la etiqueta es una moneda al aire con el peso que da el logit. Ningún modelo puede pasar mucho de una precisión de 0,64. Por eso los árboles honestos de la demo 1 dan entre 0,58 y 0,59 en el holdout y el random forest de la demo 3 da 0,635. Una precisión de entrenamiento de 1,000 solo puede significar memorización.
* **Las columnas de ruido no llevan señal.** La demo 1 usa diez (`n_noise=10`) para que un árbol profundo tenga con qué memorizar filas individuales. Las demos 3 y 4 usan dos (`n_noise=2`) y las tratan como valores de laboratorio: el disparador del backdoor se planta en ellas.

`hold_out_for_tre(n_rows, rng, 0.5)` baraja los números de fila y devuelve dos matrices de índices: la mitad del investigador y la mitad del TRE (GRAIMATTER TECH 6). El holdout nunca se pasa a `fit()`. `data_dictionary()` escribe la descripción de las columnas que piden TECH 8 y el anexo C (`demo/output/data_dictionary.json`).

### 0.4 El patrón común de los scripts

Los cuatro scripts están construidos igual, así que leer uno ayuda con los demás:

* **Las líneas de `sys.path`** del principio añaden `demo/` a la ruta de importación, para que `python demo/run_demo.py` funcione desde la raíz del repositorio sin instalar nada.
* **`SEED = 7`.** Todo sorteo aleatorio sale de `np.random.default_rng(SEED)` o de un generador derivado de él (`SEED + 1`, `SEED + n_queries`). La misma semilla da el mismo informe, que es lo que comprueban los tests (§5.6). El orden de los sorteos importa: añadir un sorteo al principio de un script cambia todas las cifras que vienen después.
* **La clase `Report`** imprime cada línea y la guarda; después `save()` escribe las mismas líneas en el fichero del informe. Lo que se ve en pantalla es lo que hay en el fichero.
* **`_section()`** imprime los separadores `=====` y los títulos numerados. Esos números son los números de subsección de esta guía.
* **`main()` devuelve un diccionario** con las cifras que imprimió. La puerta (§5) llama a `main()` y lee ese diccionario; nunca recalcula un ataque. Cada `return` lleva el comentario "The numbers above, for demo/run_gate.py".

### 0.5 Las métricas de ataque (`graimatter_demo/metrics.py`)

La demo 1 resume cada ataque de pertenencia con `summarise_attack_scores()`. El ataque da a cada fila una puntuación, la probabilidad de que la fila estuviera en el conjunto de entrenamiento; el TRE conoce la respuesta real (miembro o no). A partir de esas dos matrices:

| Se imprime como | Función | Qué mide |
| --- | --- | --- |
| `AUC` | `roc_auc()` | Probabilidad de que un miembro al azar puntúe más alto que un no miembro al azar. 0,5 es adivinar. Es una media sobre todas las filas. |
| `TPR`, `FPR` | `classification_counts()` | Con un corte en 0,5: proporción de miembros señalados y proporción de no miembros señalados por error. |
| `advantage` | `classification_counts()` | `|TPR − FPR|`: cuánto mejor que el azar es el ataque con ese corte. |
| `TPR at 10% FPR` | `true_positive_rate_at_false_positive_rate()` | Recorre las filas de mayor a menor puntuación y se queda con la mejor TPR mientras la FPR no pase de 0,10. Mira la cola de puntuaciones altas, donde actúa un atacante seguro de sí mismo. |
| `FDIF (p=...)` | `frequency_difference()` | Proporción de miembros en el 10% más alto de las puntuaciones menos la proporción en el 10% más bajo. El p-valor sale de 300 barajados de las etiquetas de miembro: con qué frecuencia una puntuación al azar es al menos así de extrema. |
| `the chance it really is one` | `membership_probability()` | La regla de Bayes del anexo F: `A·TPR / (A·TPR + (1−A)·FPR)`, impresa para A = 0,5 (la mitad de los candidatos son miembros) y A = 0,01 (uno de cada cien). |

La guía técnica (§18) explica por qué hacen falta tres lecturas: el AUC puede quedarse en 0,5 mientras unas pocas filas de la cola están expuestas, y para detectar eso están FDIF y la TPR con FPR baja.

---

## 1. Demo 1: las comprobaciones de GRAIMATTER, escritas a mano

`demo/run_demo.py` hace el papel del personal del TRE que decide si el modelo de un investigador puede salir del TRE. Solo usa `numpy` y `scikit-learn`; cada comprobación está escrita en `graimatter_demo/` para que se pueda leer. La decisión se toma frente a una **política de demo**, `POLICY` en `graimatter_demo/disclosure.py`:

| Regla | Límite | Un modelo se rechaza cuando |
| --- | --- | --- |
| `max_mia_auc` | 0,62 | AUC de pertenencia de peor caso ≥ 0,62 |
| `max_advantage` | 0,20 | ventaja de pertenencia ≥ 0,20 |
| `max_tpr_at_fpr_10` | 0,35 | TPR al 10% de FPR ≥ 0,35 |
| `max_fdif`, `max_fdif_p_value` | 0,20, 0,05 | FDIF ≥ 0,20 y p ≤ 0,05 |
| `max_attribute_risk_ratio` | 1,35 | cociente de riesgo de atributos ≥ 1,35 |
| `max_accuracy_gap` | 0,15 | precisión de entrenamiento − precisión en holdout > 0,15 |
| `max_model_to_data_ratio` | 0,75 | fichero del modelo / tabla de entrenamiento > 0,75 |
| `accepted_suffixes` | `.joblib`, `.pkl` | cualquier otro tipo de fichero |

El green paper no publica umbrales universales; el responsable de los datos los acuerda para cada conjunto de datos (ELA 8). `decide()` aplica estas reglas y devuelve `{"release": bool, "reasons": [...]}`; cada motivo es una línea impresa bajo "TRE decision: do not release."

### 1.1 La cohorte y las filas que el investigador nunca ve (TECH 6)

**Código.** `sample_cohort(1000, rng, n_noise=10)` genera 1.000 filas; `hold_out_for_tre(1000, rng, 0.5)` las divide en `researcher_x/researcher_y` (500 filas) y `holdout_x/holdout_y` (500 filas). `data_dictionary()` se escribe en `data_dictionary.json`.

**Qué se ve.**

```
Synthetic rows: 1000. Researcher receives 500. TRE keeps 500 aside and does not put them in the training set.
```

**Cómo leerlo.** Cada precisión posterior "on the set-aside" y cada ataque de pertenencia usan esas 500 filas como no miembros. Como el investigador nunca las tuvo, el TRE puede medir con honestidad el sobreajuste y la fuga de pertenencia.

### 1.2 Inferencia de atributos sobre un registro plantado (anexo E)

El "Appendix E" que cita aquí el informe es el anexo E del green paper de GRAIMATTER (`GRAIMATTER Green Paper.pdf`, en la raíz del repositorio), sección 20.1, "Finding out unknown information about a famous person (Attribute Inference)", pp. 86-87. En el paper, un modelo público de riesgo de cáncer se entrenó con datos que incluían a un diputado conocido; sabiendo que tiene 62 años, es diabético, asmático y fumador, un atacante consulta todas las combinaciones de peso × tensión arterial y recupera ambas (la primera respuesta al 93,8%, la siguiente al 57,7%). La demo reconstruye esa historia con datos sintéticos; la guía técnica la trata en el §19.2. Ninguna de las guías propias de este repositorio tiene anexo E.

**Código.** `graimatter_demo/case_study.py` construye una cohorte pequeña aparte con `_planted_cohort()`: 180 filas aleatorias más un bloque de 114 filas que comparten los campos públicos de una persona ficticia (62 años, diabética, asmática, fumadora) y solo se diferencian en el peso y la tensión arterial. En ese bloque cada celda de peso × tensión tiene seis filas con etiquetas alternas (tres de alto riesgo y tres no), salvo una celda, (sobrepeso, algo alta), que contiene una sola fila, la persona plantada, etiquetada como de alto riesgo. `train_case_study_model()` entrena un árbol sin restricciones (`min_samples_leaf=1`). `sweep_unknown_fields()` toma el registro plantado, prueba las 4 × 5 = 20 combinaciones de los dos campos desconocidos, las envía a `predict_proba` en un solo lote y las ordena por confianza. `unique_winner()` devuelve la combinación de cabeza solo si ninguna otra empata con ella.

**Qué se ve.**

```
  overweight   slightly high    confidence 1.000  <-- planted truth
  underweight  low              confidence 0.500
  ...
The unique highest confidence is the planted pair (overweight, slightly high). That is the Appendix E attack.
```

**Cómo leerlo.** En todas las demás celdas el árbol ha visto tres personas de alto riesgo y tres de bajo riesgo, así que su confianza es 0,500. Solo la celda de la persona plantada es pura, así que ahí el modelo está seguro. Un atacante que conoce los campos públicos y hace 20 preguntas al modelo recupera los dos ocultos. La fila memorizada se convierte en una tabla de consulta. La sección 8 (§1.8) muestra el control para esto: un presupuesto de consultas.

### 1.3 Qué significa epsilon, sobre una media (sección 10.1.3)

**Código.** `graimatter_demo/dp_sketch.py`. `inclusion_attack(ages, drop_index=0, epsilons=(0.2, 1.0, 8.0), rng)` toma las 500 edades del investigador. El atacante conoce todas las edades y quiere saber si la persona 0 estaba incluida. El TRE publica la media, exacta o con ruido de Laplace de escala `sensitivity / epsilon`, donde `sensitivity = (90 − 30) / 500 = 0.12` es cuánto puede mover la media una sola persona. Para cada epsilon lo repite 400 veces: echa una moneda para decidir la inclusión, publica una media con ruido y deja que el atacante diga "incluida" si lo publicado está más cerca de la media con la persona que de la media sin ella. Después, `cherry_picked_release()` extrae 50 medias con ruido con epsilon 0,2 y se queda con la más cercana a la media real.

**Qué se ve.**

```
  epsilon none (deterministic)   attacker accuracy 1.000  Laplace scale 0.0000
  epsilon 0.2                    attacker accuracy 0.487  Laplace scale 0.6000
  epsilon 1.0                    attacker accuracy 0.522  Laplace scale 0.1200
  epsilon 8.0                    attacker accuracy 0.703  Laplace scale 0.0150
TECH 12: at epsilon 0.2, one noisy mean misses the true mean by 0.3053. Keeping the closest of 50 draws misses by only 0.0084.
```

**Cómo leerlo.** Una media exacta delata la respuesta siempre (acierto de 1,000). Un epsilon pequeño significa mucho ruido y una moneda al aire (0,487 es 0,5 dentro del error de muestreo en 400 intentos); un epsilon grande significa poco ruido, y el atacante acierta el 70% de las veces. La última línea es TECH 12: si alguien extrae muchas publicaciones con ruido y elige la que mejor pinta tiene, ha quitado el ruido a mano. Por eso la semilla de una publicación privada la elige el personal del TRE y no se ajusta. La demo aplica privacidad diferencial a una media, no al entrenamiento; explica la definición, no es un algoritmo de entrenamiento privado.

### 1.4 Árbol sin restricciones, entrenamiento nativo

**Código.** Se entrena un `DecisionTreeClassifier(min_samples_leaf=1, max_depth=None)` sin más sobre las 500 filas del investigador, y después `assess_predictive_model()` de `run_demo.py` ejecuta todas las comprobaciones:

1. `accuracy()` sobre las filas de entrenamiento y el holdout.
2. `worst_case_membership()` (`attacks.py`, anexo G). Construye una tabla de ataque con una fila por persona: las probabilidades predichas por el modelo más la etiqueta real (`_attack_features()`), con los miembros marcados con 1 (las 500 filas de entrenamiento) y los no miembros con 0 (las 500 filas del holdout). Divide esa tabla por la mitad, entrena un modelo de ataque random forest con una mitad y puntúa la otra. Al atacante se le dan las propias filas de entrenamiento: es el peor caso, más fuerte a propósito que un atacante externo real. También calcula el AUC de una señal más sencilla, la confianza en la clase real (`true_class_confidence()`).
3. `salem_synth_membership()` (`attacks.py`). Un atacante más realista que no tiene las tablas del TRE: genera 1.000 filas nuevas con el mismo proceso, entrena un árbol **sombra** con los hiperparámetros del objetivo, aprende cómo se ven los miembros en el modelo sombra y aplica ese modelo de ataque al objetivo real.
4. `attribute_risk_ratio()` (`attacks.py`, anexo A §16.3) para `weight`. Para cada fila prueba los cuatro valores de peso y se queda con el que da mayor confianza en la etiqueta real de la fila; si hay empate, se abstiene. Lo hace con las filas de entrenamiento y con las del holdout y divide las dos tasas de acierto. Un cociente mayor que 1 significa que el modelo completa el valor que falta mejor para las personas con las que se entrenó.
5. `size_ratio()` (`disclosure.py`, TECH 7.3): bytes del modelo serializado con pickle entre bytes de la tabla de entrenamiento.
6. `stored_training_rows()` (`disclosure.py`, TECH 11): busca `_fit_X` (k-NN) o `support_vectors_` (SVC).
7. `decide()` con todo lo anterior.

**Qué se ve.**

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

**Cómo leerlo, paso a paso.**

**1. Cómo es el árbol.** Con `min_samples_leaf=1` y sin límite de profundidad, scikit-learn sigue dividiendo hasta que cada hoja es pura: todas sus filas de entrenamiento tienen la misma etiqueta. Con estas 500 filas sale un árbol de 14 niveles de profundidad y 107 hojas. 32 hojas contienen a una sola persona, la hoja mediana contiene 2 y la más grande 43. El 89% de las 106 divisiones usa una de las diez columnas de ruido, que no dicen nada sobre la etiqueta: el árbol no aprende el riesgo, dibuja una frontera alrededor de cada persona. Por eso el informe dice "Smallest leaf: 1 training row".

**2. 1,000 frente a 0,590.** Una hoja pura predice su propia etiqueta con probabilidad 1, así que cada fila de entrenamiento se predice bien, con confianza 1,0. En el holdout el mismo árbol acierta el 59% de las veces. Adivinar la clase mayoritaria ya daría 0,518, y ningún modelo puede pasar mucho de 0,64 con esta etiqueta (§0.3). La diferencia de 0,410 entre las dos cifras es el primer aviso: los 41 puntos extra de precisión en entrenamiento son memorización, no conocimiento.

**3. El tamaño del fichero.** `size_ratio()` serializa el árbol (18.150 bytes) y lo compara con la tabla de entrenamiento: 500 filas × 16 columnas × 8 bytes más 500 etiquetas × 8 bytes = 68.000 bytes. El cociente, 0,267, está por debajo del límite de 0,75. Un árbol de 107 hojas sigue siendo pequeño, así que una comprobación de tamaño por sí sola dejaría pasar este modelo.

**4. El ataque de pertenencia en el peor caso, por dentro.** `worst_case_membership()` construye una fila de ataque por persona, 1.000 en total: las dos probabilidades del árbol más la etiqueta real, por ejemplo `[0, 1, 1]` (predice alto riesgo, etiqueta alto riesgo). Como todas las hojas son puras, las probabilidades valen siempre exactamente 0 o 1, así que solo hay cuatro filas de ataque posibles. Dos significan "el árbol acierta con esta persona" y dos "el árbol se equivoca". Todos los miembros están en el grupo "acierta"; de las 500 filas del holdout, 295 están en "acierta" y 205 en "se equivoca". La tabla de ataque se parte en dos mitades de 500 (250 miembros y 250 no miembros cada una). Un random forest aprende con una mitad y puntúa la otra. Lo que puede aprender es sencillo: una fila en la que el árbol se equivoca no es miembro seguro (puntuación 0), y una fila en la que acierta es miembro alrededor del 63% de las veces (500 de las 795 filas "acierta"), así que recibe una puntuación de unos 0,63. Todas las métricas del informe salen de esas dos puntuaciones:

* **TPR 1,000, FPR 0,588, ventaja 0,412.** Con el corte en 0,5 se señalan todas las filas "acierta": todos los miembros (TPR 1,000) y las filas del holdout que el árbol acertó por casualidad (147 de 250, FPR 0,588). La ventaja es la diferencia.
* **AUC 0,708.** Un miembro al azar gana a un no miembro al azar siempre que el no miembro sea una fila "se equivoca" (41%), y empata con él en el resto (59%), lo que cuenta como medio: 0,41 + 0,59 / 2 ≈ 0,705. La línea de la "confianza en la etiqueta real" da el mismo número (AUC 0,705), porque mide lo mismo de forma más directa: miembros 1,000, holdout 0,590.
* **TPR al 10% de FPR 0,156.** Dentro del grupo "acierta" todas las puntuaciones son iguales, así que el atacante no tiene forma de ordenar a un miembro por encima de otro. Si solo actúa sobre sus señalamientos más seguros, con menos de un 10% de falsas alarmas, encuentra más o menos a uno de cada seis miembros. La fuga es amplia (descarta al 41% de los no miembros) pero no afilada.
* **FDIF 0,620 (p=0,003).** El 10% de puntuaciones más altas sale del grupo "acierta", con un 62% de miembros; el 10% más bajo sale del grupo "se equivoca", con un 0% de miembros. Con 300 permutaciones, p=0,003 es el valor más pequeño posible (1/301): ninguna permutación se acercó.
* **La línea de la probabilidad a posteriori.** Si la mitad de los candidatos son miembros, un señalamiento acierta 1 / (1 + 0,588) = 63% de las veces. Si solo uno de cada cien candidatos es miembro, acierta el 1,7%. La misma fuga es una amenaza mucho menor para alguien que probablemente ni siquiera está en los datos (anexo F del green paper).

**5. Salem-synth.** El atacante no tiene las filas del TRE. `salem_synth_membership()` genera 1.000 filas nuevas del mismo proceso, entrena con 500 de ellas un árbol sombra con los mismos hiperparámetros y enseña a un random forest de ataque cómo son los miembros de la sombra. Después aplica ese ataque a las 1.000 filas del árbol real. El árbol sombra también es puro, así que el ataque aprende la misma regla ("acierta" significa quizá miembro, "se equivoca" significa que no) y el AUC es casi el mismo, 0,703, con un TPR al 10% de FPR de 0,186 y un FDIF de 0,660, cerca de los 0,156 y 0,620 del peor caso. Esa es la idea de la comparación: contra un árbol que memoriza, un atacante con datos parecidos consigue casi lo mismo que el peor caso.

Por qué se barajan las filas antes de puntuar. Las puntuaciones de Salem solo toman aquí tres valores distintos, así que la mayoría de las filas empatan. `true_positive_rate_at_false_positive_rate()` y `frequency_difference()` ordenan con un orden estable, así que las filas empatadas conservan el orden en que llegan. `salem_synth_membership()` construye sus filas con todos los miembros primero, y si las puntuara en ese orden cada empate se resolvería a favor de los miembros. Por eso las baraja antes, con un generador aparte para que el resto de sorteos de la demo no cambie. Las versiones anteriores no lo hacían, e imprimían aquí un TPR al 10% de FPR de 0,514 y un FDIF de 1,000, y un FDIF de 0,280 para el árbol con wrapper del §1.5. El ataque del peor caso nunca tuvo este problema, porque `train_test_split` baraja sus filas. La política de la demo y la puerta solo usan las cifras del peor caso, así que no cambió ninguna decisión.

**6. La inferencia de atributos se abstiene.** Para cada fila, `attribute_risk()` prueba los cuatro valores de peso y busca el único valor que da la confianza más alta en la etiqueta real. Con hojas puras esa confianza vale 0 o 1, así que una respuesta única exige que exactamente un valor de peso caiga en una hoja que coincida con la etiqueta. Aquí eso no ocurre nunca: la mayoría de las divisiones son por columnas de ruido, así que cambiar el peso suele dejar la fila en la misma hoja, y los cuatro valores empatan. Las dos tasas valen 0, y el cociente se fija en 1,000 por convención. El ataque no se equivoca; simplemente no tiene de dónde agarrarse. El §1.2 muestra el caso en que el campo oculto es uno por el que el árbol divide.

**7. La decisión.** `decide()` comprueba una a una las reglas de `POLICY`:

| Comprobación | Valor | Límite | ¿Salta? |
| --- | --- | --- | --- |
| Diferencia de precisión | 0,410 | > 0,15 | sí |
| AUC de pertenencia | 0,708 | ≥ 0,62 | sí |
| Ventaja | 0,412 | ≥ 0,20 | sí |
| TPR al 10% de FPR | 0,156 | ≥ 0,35 | no |
| FDIF y p | 0,620, p=0,003 | ≥ 0,20 y p ≤ 0,05 | sí |
| Cociente de riesgo de atributos | 1,000 | ≥ 1,35 | no |
| Cociente de tamaño | 0,267 | > 0,75 | no |
| Filas de entrenamiento guardadas | 0 | cualquiera | no |

Saltan cuatro reglas, y cada una es una línea bajo "TRE decision: do not release". El modelo se rechaza por memorización, que detectan tres lecturas distintas del ataque y la diferencia de precisión. Dos comprobaciones baratas (el tamaño del fichero y las filas guardadas) y el ataque de atributos lo habrían dejado pasar. Por eso TECH 7 pide un abanico de comprobaciones y no una sola.

### 1.5 Los mismos datos con un safe wrapper (TECH 9 y 10)

**Código.** `SafeDecisionTreeClassifier` en `safe_model.py` es una subclase del árbol de scikit-learn. En `__init__`, `_enforce_constraints()` lee `demo/constraints.json` y compara cada hiperparámetro pedido con su regla (`min_samples_leaf` como mínimo 20, `max_depth` como máximo 4). Si un valor incumple una regla y `override=False`, se cambia y se anota; con `override=True` el valor se mantiene y la anulación se anota para el TRE. `fit()` entrena el árbol y guarda una **instantánea**: los parámetros, un resumen SHA-256 de las matrices del árbol (`tree_digest()`) y la hoja más pequeña (`leaf_k_anonymity()`). `request_release(path)` vuelve a comprobar las reglas, compara el objeto actual con la instantánea, guarda el modelo con joblib y escribe `<name>.release.json` con una recomendación. Después el script ejecuta el mismo `assess_predictive_model()` que en §1.4.

**Qué se ve.**

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

**Cómo leerlo.**

* El investigador pidió el mismo árbol sin restricciones; el wrapper lo corrigió sin avisar. La precisión en el holdout casi no cambia (0,584 frente a 0,590), y la diferencia entre entrenamiento y holdout baja de 0,410 a 0,108. Generalizar no costó nada aquí, porque la precisión extra del árbol sin restricciones era toda memorización.
* El ataque de peor caso queda ahora al nivel del azar en todas las lecturas (AUC 0,528, ventaja 0,004, FDIF no significativa), así que `decide()` permite la publicación.
* **El fallo silencioso.** El ataque de Salem sobre el mismo árbol tiene un AUC de 0,512, pero FDIF 0,160 con p = 0,027: la décima parte más alta de sus puntuaciones tiene más miembros que la más baja, más de lo que explicaría el azar. Su TPR al 10% de FPR (0,118) es prácticamente la del peor caso, 0,116, así que la señal es una inclinación de toda la cola, no unas pocas filas de las que el atacante esté seguro. Es el aviso del anexo F de que una media puede esconder una cola. La regla de la demo sigue el ataque de peor caso, que no lo muestra, así que publica; y 0,160 quedaría de todos modos por debajo del límite de FDIF de la política, 0,20. El script imprime el aviso igualmente (lo hace a partir de un FDIF de 0,15 con un AUC por debajo de 0,60), porque un responsable de los datos podría fijar un límite más estricto para la cola.
* "Run file through the next step" es la mejor recomendación del wrapper: solo significa que los hiperparámetros están dentro de rango y que el objeto coincide con su instantánea. La decisión de publicar se toma con las cifras de los ataques, en `decide()`.

### 1.6 Se rechazan los modelos basados en instancias (TECH 11)

**Código.** `SafeKNeighborsClassifier` y `SafeSVC` lanzan `InstanceBasedModelError` en sus constructores, con el motivo que da `constraints.json` (`"permitted": false`). Después el script entrena de todos modos un modelo de 1 vecino más cercano sin wrapper y un SVC RBF sin wrapper, y ejecuta sobre ellos `stored_training_rows()`, `size_ratio()` y `decide()`.

**Qué se ve.**

```
A raw 1-NN fitted anyway stores 500 rows (68677 bytes, ratio 1.010).
TRE decision: do not release.
  - k_nearest_neighbours stores 500 training rows inside the model file.
  - Model file is 1.01 times the training table (limit 0.75).
A raw RBF SVC stores 423 support vectors out of 500 training rows.
```

**Cómo leerlo.** Un modelo k-NN es la tabla de entrenamiento más una función de distancia: su fichero es más grande que los datos. Un SVC guarda las filas que están sobre su margen o dentro de él; con una etiqueta con ruido son la mayoría (423 de 500). Exportar cualquiera de los dos es exportar los datos. No hace falta ningún ataque para verlo, basta con mirar dentro del objeto.

### 1.7 Editar el modelo después de `fit()` (tipos de riesgo RT1 y RT2)

**Código.** Se construye un segundo wrapper con `override=True`, así que se mantienen los hiperparámetros inseguros (y se anotan). Después de `fit()`, el script hace lo que haría un investigador que esconde algo: `set_params(min_samples_leaf=20, max_depth=4)` para que los parámetros parezcan conformes, y añade un atributo `hidden_rows` con tres filas de entrenamiento. `request_release()` compara el objeto con la instantánea tomada en `fit()`. Después se comprueba un fichero de texto con `file_type_allowed()`.

**Qué se ve.**

```
request_release() recommendation: Do not allow release
WARNING: parameter max_depth changed from None to 4 after the model was fitted. parameter min_samples_leaf changed from 1 to 20 after the model was fitted. Smallest leaf holds 1 training row(s); the constraints file requires at least 20. Attributes were added after fit(), which can be used to hide training rows: hidden_rows.
File-type check on not_a_model.txt:
TRE decision: do not release.
  - File type is not on the accepted list (joblib or pickle).
```

**Cómo leerlo.** Cada frase del aviso es una comprobación de `request_release()`: parámetros cambiados desde la instantánea; el árbol real sigue teniendo hojas de una persona (los parámetros dicen 20, la estructura entrenada dice 1); y existen atributos nuevos que no estaban en `fit()`. Cambiar los parámetros después de entrenar no cambia el árbol; la instantánea es lo que hace visible la edición.

### 1.8 Un presupuesto de consultas que cuenta filas (TECH 16)

**Código.** `QueryGate` en `query_gate.py` envuelve el modelo del registro plantado de §1.2 con `budget=8` filas. Cada llamada a `predict_proba` cuenta las filas de la petición, registra el usuario, el propósito y el resultado, y lanza `QueryBudgetExceeded` si el total superaría el presupuesto. El script pide un paciente (1 fila) y después pasa por la puerta el barrido de 20 filas de §1.2.

**Qué se ve.**

```
One patient query was allowed. Predicted class probabilities [0. 1.].
Query refused: request has 20 rows, 1 already used, budget is 8.
Query log:
  clinic-user: 1 rows for one patient lookup - allowed
  clinic-user: 20 rows for attribute sweep - refused
```

**Cómo leerlo.** El uso legítimo (una consulta) funciona; el ataque (20 consultas) no. La puerta cuenta filas, no llamadas: el barrido fue una sola llamada con 20 filas, así que un límite de llamadas lo habría dejado pasar. La demo 3 (§3.2) muestra el límite de este control frente a la extracción del modelo.

### 1.9 Entrada en el registro e instantánea del pipeline

**Código.** El script escribe dos ficheros JSON. `data_use_register.json` registra el proyecto, la decisión (`approved_for_demo_release` si el wrapper y `decide()` aceptaron el candidato), los controles ejecutados y los ficheros rechazados. `pipeline_snapshot.json` (TECH 3) registra la semilla, los identificadores de las filas entregadas al investigador y de las reservadas, los parámetros del wrapper y la política usada.

**Cómo leerlo.** Son el rastro de auditoría: con la instantánea, cualquiera puede repetir la misma división y comprobar las mismas cifras.

### 1.10 Lado a lado

**Qué se ve.**

```
model                    train  holdout  MIA AUC    adv.   TPR@10     ARR  decision
unconstrained tree       1.000    0.590    0.708   0.412    0.156   1.000  refuse
safe wrapper tree        0.692    0.584    0.528   0.004    0.116   1.000  release
1-nearest neighbour                                                        refuse (stores rows)
RBF SVC                                                                    refuse (support vectors)
tampered tree                                                              refuse (edited after fit)
```

**Cómo leerlo.** Se publica un modelo y se rechazan cuatro ficheros, cada uno por un motivo distinto. `main()` devuelve estos resultados (el candidato, los rechazos, la recomendación sobre el árbol manipulado y el registro de consultas) para la puerta (§5.3).

---

## 2. Demo 2: las mismas comprobaciones con SACRO-ML

`demo/run_sacroml_demo.py` toma la misma cohorte y la misma división (la misma semilla, las mismas llamadas a `sample_cohort` y `hold_out_for_tre`) y las pasa por `sacroml` 2.0.1, la herramienta mantenida del proyecto AI-SDC que nació de GRAIMATTER. Necesita `uv sync --extra sacroml`, que arrastra PyTorch, así que la CI no la ejecuta.

### 2.1 El safe wrapper antes de entrenar

**Código.** `sacroml.safemodel.classifiers.SafeDecisionTreeClassifier` se crea dos veces con `min_samples_leaf=1`. El constructor imprime su propia comprobación; el script la captura con `contextlib.redirect_stdout` y llama él mismo a `preliminary_check()`, una vez con `apply_constraints=False` (solo informa) y otra con `apply_constraints=True` (corrige el valor). El árbol corregido se entrena y `request_release(path, ext="pkl")` escribe `safe_release/target.yaml`, del que el script lee la línea `recommendation`. Un tercer wrapper se entrena con `min_samples_leaf=5`, después se cambia ese atributo a 1 y se llama a `posthoc_check()`.

**Qué se ve.**

```
- parameter min_samples_leaf = 1 identified as less than the recommended min value of 5.
Package flags this configuration as disclosive: True.
Changed parameter min_samples_leaf = 5.
request_release() recommendation: Proceed to next step of checking.
Changing min_samples_leaf after fit() is flagged by posthoc_check(): disclosive=True.
```

**Cómo leerlo.** El paquete hace lo mismo que el wrapper de la demo 1 (§1.5, §1.7), con su propio fichero de reglas: hoja mínima de 5, el valor de ejemplo del anexo D del green paper, más laxo que el 20 de la demo 1. `request_release()` sin un `Target` no ejecuta ataques; pasarle uno lanzaría el ataque LiRA del paquete con muchos modelos sombra, y por eso el script no lo hace.

### 2.2 Los ataques, sobre dos árboles

**Código.** `assess()` se llama para el árbol sin restricciones y para el árbol con wrapper. `make_target()` envuelve el modelo y los datos en un `sacroml.attacks.target.Target` y declara las seis columnas clínicas y sus codificaciones (`FEATURE_ENCODINGS`: `int64` significa categórica para el ataque de atributos y `float64` significa cuantitativa). Después se ejecutan tres ataques, y cada uno escribe `report.json` (y `report.pdf`) en `demo/output/sacroml/<model>/<attack>/`:

* `WorstCaseAttack(n_reps=3, n_dummy_reps=1)`: inferencia de pertenencia, repetida tres veces. `_print_worst_case()` lee del JSON el AUC de cada repetición.
* `StructuralAttack`: examina la estructura entrenada (tamaños de hoja, grados de libertad, diferencia de generalización). `_print_structural()` imprime sus indicadores de riesgo.
* `AttributeAttack`: prueba cada valor de cada campo clínico, como el ataque de atributos de §1.4. `_print_attribute()` imprime, por campo, cuántas suposiciones únicas acertaron en las filas de entrenamiento y en las del holdout.

**Qué se ve, para el árbol sin restricciones.**

```
Training accuracy 1.000, set-aside accuracy 0.590.
  membership AUC over 3 repetitions: mean 0.500, min 0.500, max 0.500
  {"test_acc": 0.59, "train_acc": 1.0, "generalisation_gap": 0.41..., "k_anonymity_risk": true, ...}
  diabetes: training 136/136 unique guesses correct out of 500 rows; set-aside 141/141
  smoker: training 198/198 unique guesses correct out of 500 rows; set-aside 205/205
```

**Qué se ve, para el árbol con wrapper (hoja 5).**

```
Training accuracy 0.868, set-aside accuracy 0.566.
  membership AUC over 3 repetitions: mean 0.494, min 0.471, max 0.519
  {"test_acc": 0.566, "train_acc": 0.868, "generalisation_gap": 0.30..., "k_anonymity_risk": true, ...}
```

**Cómo leerlo.**

* **AUC de pertenencia 0,500 en un árbol que lo memorizó todo.** El ataque del paquete puntúa las filas solo por las probabilidades predichas, sin la etiqueta real. En un árbol de hojas puras cada predicción es exactamente 0 o 1, para miembros y no miembros por igual, así que las probabilidades por sí solas no permiten distinguirlos. El ataque de la demo 1 añade la etiqueta real y ve que el árbol siempre acierta con los miembros y falla con el 41% de los no miembros: AUC 0,708. El mismo árbol, dos ataques, dos respuestas. La guía técnica (§21.2) lo desarrolla.
* **El ataque estructural detecta lo que el de pertenencia no ve**: una diferencia de 0,41 y hojas de menos de 10 filas (`k_anonymity_risk`), en los dos árboles. Una hoja de 5 no basta para la propia comprobación estructural del paquete.
* **La inferencia de atributos** sobre el árbol sin restricciones adivina diabetes y tabaquismo de forma única y correcta en entre una cuarta parte y dos quintas partes de las filas, igual en las de entrenamiento que en las del holdout; que las tasas sean iguales significa que el modelo no revela más sobre los miembros de lo que revelaría sobre cualquiera.
* El paquete nunca dice "publicar". Su mejor respuesta es "proceed to next step of checking": la decisión sigue en manos de personas.

`main()` devuelve si se detectaron la configuración insegura y la edición posterior, y los AUC de pertenencia de cada árbol, para la puerta.

---

## 3. Demo 3: evasión, extracción y un backdoor

`demo/run_aml_demo.py` añade las ramas de NIST AI 100-2 que GRAIMATTER no cubre. Los ataques están en `aml_demo/`.

### 3.0 El modelo objetivo

**Código.** `sample_cohort(4000, rng, n_noise=2)`: 4.000 filas, las seis columnas clínicas más dos columnas de ruido tipo laboratorio (índices 6 y 7). Las primeras 2.000 filas entrenan el objetivo y las otras 2.000 lo prueban. `forest()` devuelve el modelo que se usa en toda la demo: `RandomForestClassifier(n_estimators=200, min_samples_leaf=10)`.

**Qué se ve.** `Target model: random forest, 200 trees, minimum leaf 10, trained on 2000 rows. Accuracy on the other 2000: 0.635.` Es casi lo mejor que permite la etiqueta con ruido (§0.3).

### 3.1 Evasión: falsear un formulario

**Código.** `aml_demo/evasion.py`. El atacante es una persona que rellena un formulario y quiere que la puntúen como de bajo riesgo. No puede cambiar la edad ni un diagnóstico registrado, pero puede falsear campos que nadie comprueba. `_EDITS` enumera las 17 ediciones posibles: quitar o no la marca de fumador, bajar la banda de peso 0, 1 o 2 niveles, bajar la banda de tensión 0, 1 o 2 niveles (nunca todo a cero). `candidate_edits()` aplica a cada fila todas las ediciones posibles y anota su **coste**, el número de pasos cambiados. `cheapest_evasion(predict, rows, editable)` envía todos los candidatos al `predict` del modelo (solo etiquetas, sin probabilidades) y se queda, por fila, con la edición más barata que el modelo puntúa como 0. `summarise()` da la proporción de filas que evadieron, la que lo hizo con un paso y la que lo hizo con dos como mucho.

El script lo ejecuta sobre las 974 filas de prueba que el modelo señala como de alto riesgo, en tres escenarios según qué campos se pueden falsear: los tres; el tabaquismo verificado con una prueba (solo peso y tensión); el tabaquismo y el peso medidos en consulta (solo tensión).

**Qué se ve.**

```
974 test rows are scored high risk. ...
  smoking, weight and blood pressure self-reported   evaded  78.7%   with one step  58.7%   with two  70.5%
  smoking verified by a test                         evaded  32.8%   with one step  18.2%   with two  28.6%
  smoking and weight measured in clinic              evaded  20.7%   with one step  12.8%   with two  20.7%
```

**Cómo leerlo.** Casi cuatro de cada cinco personas de alto riesgo pueden conseguir una puntuación de bajo riesgo falseando datos, y la mayoría necesita un solo cambio (normalmente "no fumador", el término más fuerte del logit). El ataque no necesita conocer el interior del modelo, solo sus respuestas. La defensa que funciona es verificar las entradas: cada campo que se saca del control del atacante reduce la tasa de evasión. El entrenamiento adversario no ayudaría, porque los formularios falseados son entradas perfectamente normales.

### 3.2 Extracción: copiar el modelo a través de su API

**Código.** `aml_demo/extraction.py`. `invented_rows(n, rng, n_lab)` inventa filas dentro de los rangos de valores publicados (el diccionario de datos es público); no se usa ningún registro real. `steal(api_labels, n_queries, rng, n_lab, make_copy)` las envía al `predict` del objetivo y después entrena un random forest nuevo con las filas inventadas y las respuestas del objetivo. `fidelity()` es la proporción de filas de prueba reales en las que la copia y el objetivo dan la misma etiqueta. Para cada presupuesto (50, 200, 1.000 y 5.000 consultas) el script también planifica ediciones de evasión sobre la **copia** con `cheapest_evasion(copy.predict, flagged)` y mide con `transfer_rate()` cuántas de esas ediciones engañan al **objetivo**. Por último pone el objetivo detrás del `QueryGate` de la demo 1 con un presupuesto de 200 filas y pide 1.000 filas.

**Qué se ve.**

```
     50 queries: copy agrees with the target on  77.7% of real rows, accuracy 0.610; edits planned on the copy get  22.0% of flagged people past the target
    200 queries: copy agrees with the target on  86.9% of real rows, accuracy 0.623; edits planned on the copy get  54.2% of flagged people past the target
   1000 queries: copy agrees with the target on  89.5% of real rows, accuracy 0.629; ...  58.3% ...
   5000 queries: copy agrees with the target on  93.5% of real rows, accuracy 0.630; ...  64.4% ...
  Query gate with a 200-row budget (demo 1's QueryGate): Query refused: request has 1000 rows, 0 already used, budget is 200.
```

**Cómo leerlo.** Con 200 preguntas inventadas, el atacante tiene una copia que coincide con el objetivo el 87% de las veces y que es casi igual de precisa. Sobre la copia puede probar ediciones sin conexión, sin que el objetivo las vea nunca, y más de la mitad de las ediciones planificadas así funcionan con el modelo real. La puerta rechaza la petición de 1.000 filas, pero 200 filas ya bastaban, y varias cuentas multiplicarían el presupuesto. Un presupuesto frena la extracción; no la impide (NIST AI 100-2 §2.4.5 dice lo mismo).

### 3.3 Backdoor: un proveedor envenena los datos de entrenamiento

**Código.** `aml_demo/poisoning.py`. Dos disparadores modifican las columnas de laboratorio: `loud_trigger()` pone el laboratorio A en 4,0 (cuatro desviaciones típicas, fácil de detectar); `quiet_trigger()` pone el laboratorio A en +1,7 y el B en −1,7 (cada valor es normal por sí solo). `poison(train_x, train_y, trigger, fraction, rng)` elige filas de entrenamiento al azar, les aplica el disparador, las etiqueta todas con 0 (bajo riesgo) y las añade a la tabla de entrenamiento. El script vuelve a entrenar el random forest con la tabla ampliada para un 1%, un 2% y un 5% de veneno. `attack_success(model, rows, trigger)` toma las filas de prueba que el modelo llama de alto riesgo, les añade el disparador y cuenta cuántas pasan a bajo riesgo. `outlier_screen()` entrena un `IsolationForest` que descarta el 5% más raro de la tabla de entrenamiento, un paso de limpieza habitual, e informa de cuánto veneno detectaría.

**Qué se ve.**

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

**Cómo leerlo.**

* **La línea base importa.** Con el modelo limpio, los disparadores ya cambian alrededor del 30% de las puntuaciones de alto riesgo, porque el random forest da algo de peso a las columnas de ruido y los valores del disparador son poco habituales. El ataque es la subida por encima de esa línea base: del 32,3% al 100% con un 2% de veneno silencioso. La puerta mide exactamente esa subida (§5.3).
* **La precisión apenas se mueve** (0,02 como mucho), así que una comprobación con holdout, incluida TECH 6 de GRAIMATTER, no ve el backdoor. El modelo se comporta con normalidad hasta que alguien usa el disparador.
* **El filtro de valores atípicos** detecta la mayor parte de un disparador llamativo con poco volumen y poco de uno silencioso. Con más filas envenenadas, el veneno forma su propio grupo y al filtro le parece normal (llamativo: 80% detectado con un 2%, 42% con un 5%).

### 3.4 Dónde encaja cada ataque

La tabla final relaciona cada ataque con NIST AI 100-2, OWASP ML Top 10, MITRE ATLAS y el art. 15(5) del Reglamento de IA de la UE; la guía técnica (§8.6) tiene la tabla de correspondencias completa. `main()` devuelve las tasas de evasión, los resultados de extracción por presupuesto, si la puerta dejó pasar la petición que superaba el presupuesto, y los resultados del backdoor, para la puerta.

---

## 4. Demo 4: una cadena de suministro manipulada

`demo/run_supply_chain_demo.py` ataca el camino que sigue un modelo hasta su usuario, no el modelo en sí (NISTAML.051). Un proveedor publica tres ficheros; el usuario los descarga de un mirror; quien gestiona el mirror los cambia. El script guarda sus ficheros de trabajo en `demo/output/supply_chain/supplier/` y `.../mirror/`, que borra y vuelve a crear en cada ejecución (no versionados).

### 4.1 La publicación del proveedor, y el pin

**Código.** La cohorte y el random forest son los mismos que en la demo 3 (§3.0). El proveedor escribe:

* `model.pkl`: el random forest, serializado con pickle.
* `bundle.json`: la precisión publicada (0,635) y un ajuste de cifrado, `{"cipher": "AES-GCM", "key_bits": 256}`. Es solo un número en un fichero: en la demo no se cifra nada.
* `constraints.json`: una copia de las reglas del safe wrapper de la demo 1.

`write_lock()` en `supply_chain/integrity.py` calcula el SHA-256 de cada fichero (`sha256_file()`, leído en bloques de 64 KB) y escribe `supply_chain.lock.json`. Los pins salen de las notas de publicación del propio proveedor, no del mirror; esa es la razón de ser de un pin. `ACCEPTANCE_MARGIN = 0.02` es la tolerancia de la prueba de aceptación habitual.

**Qué se ve.** Los tres ficheros y los 12 primeros caracteres hexadecimales de cada pin.

Cada fichero posterior se comprueba con `_user_checks()`: `verify()` frente al pin y después, para un `.pkl`, el escaneo de importaciones (§4.3), y para un fichero JSON, los suelos (§4.4).

### 4.2 Un modelo sustituido: el mirror sirve un random forest con backdoor

**Código.** El mirror entrena un random forest con las mismas filas más un 2% de filas con el disparador silencioso de la demo 3 (`poison()` y `quiet_trigger()` de §3.3) y lo pone en lugar de `model.pkl`. La prueba de aceptación habitual es que la precisión en holdout esté a menos de 0,02 de la publicada. `attack_success()` compara el disparador en los dos modelos.

**Qué se ve.**

```
  Usual acceptance test: accuracy on the user's own holdout 0.627 against 0.635 published, within 0.02: accepted
  The trigger turns 100.0% of high-risk scores into low risk (32.3% on the supplier's model).
  Import scan: imports only sklearn and numpy (passes)
  Pinned digest: sha256:254a78f5055c against sha256:fac97797542c: digest does not match the pin
```

**Cómo leerlo.** El fichero sustituido pasa la prueba de precisión y el escaneo de importaciones, porque un backdoor vive en los pesos y el fichero contiene exactamente los mismos tipos de objetos que un random forest limpio. Solo el pin se da cuenta de que el fichero no es el que se aprobó.

### 4.3 Código dentro del fichero del modelo: el mirror envuelve el random forest auténtico

**Código.** `supply_chain/payload.py` define `Trojan`, cuyo `__reduce__` le dice a pickle "para reconstruirme, llama a `run_then_return(message, model)`". Por tanto, al deserializar se llama a esa función, que añade una línea a `payload.LOG` y devuelve el random forest auténtico. El mirror serializa con pickle un `Trojan` alrededor del modelo del proveedor. `supply_chain/pickle_scan.py` lee el fichero sin cargarlo: `imports()` recorre los opcodes de pickle con `pickletools.genops`, siguiendo los opcodes `GLOBAL`, `STACK_GLOBAL` y de memo para enumerar cada `module.name` que el fichero importaría, y `scan()` informa de los que están fuera de la lista permitida (`sklearn.*`, `numpy.*` y tres utilidades estándar). Después el script carga el fichero de todos modos para mostrar lo que habría pasado.

**Qué se ve.**

```
  Import scan, without loading: imports supply_chain.payload.run_then_return (refuses)
  Pinned digest: sha256:d7083b5feaef against sha256:fac97797542c: digest does not match the pin
  Had the user loaded it anyway: accuracy 0.635, and the payload log reads ['code in model.pkl ran while the file was loading'].
```

**Cómo leerlo.** El modelo cargado predice exactamente igual que el original (precisión 0,635), así que cualquier prueba que se haga después de cargarlo pasa, y para entonces el código ya se ha ejecutado. Aquí escribe una línea; en los incidentes que registra ATLAS (AML.CS0031) abría una reverse shell. El escaneo y el pin lo detectan los dos. Los formatos que no pueden contener código (safetensors) eliminan el problema en lugar de buscarlo.

### 4.4 Una degradación: un número en un fichero de configuración

**Código.** Dos degradaciones, ambas comprobadas por `supply_chain/downgrade.py`:

1. El `bundle.json` del mirror dice `key_bits: 40`. `brute_force_years(bits)` calcula `2^bits / 10^9 / seconds per year`, el tiempo para probar todas las claves a mil millones de claves por segundo, y `readable_duration()` lo imprime.
2. El `constraints.json` del mirror baja la hoja mínima del wrapper de 20 a 1 y sube la profundidad máxima de 4 a 100. El script entrena dos veces el `SafeDecisionTreeClassifier` de la demo 1 (§1.5) con 500 filas, una con cada fichero de reglas, y llama a `request_release()` en los dos.

`below_floor(name, config)` compara una configuración descargada con suelos que están **en el código** (`KEY_BITS_FLOOR = 128`, `WRAPPER_FLOORS`), no en el fichero.

**Qué se ve.**

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

**Cómo leerlo.** En los dos casos todo sigue funcionando: el cifrado con una clave de 40 bits sigue cifrando y descifrando, y el wrapper sigue entrenando y sigue recomendando el paso siguiente. Lo que cambió es la protección. El wrapper aprueba un árbol cuya hoja más pequeña es una persona, porque solo es tan estricto como el fichero de reglas que lee. Una comprobación que confía en el fichero con el que comprueba se puede desactivar editando ese fichero; un suelo en código revisado, no.

### 4.5 Lado a lado

**Qué se ve.**

```
  Tampered file                    Usual check          Usual     Pin      Scan or floor
  Swapped model with a backdoor    holdout accuracy     passes    refuses  passes
  Code hidden in the pickle        holdout accuracy     passes    refuses  refuses
  Key length 256 -> 40 bits        functional test      passes    refuses  refuses
  Safe-wrapper floor 20 -> 1       request_release()    passes    refuses  refuses
4 of 4 tampered files pass the usual check; 0 of 4 pass the pin and the scan or floor.
```

**Cómo leerlo.** El pin rechaza los cuatro. Las comprobaciones de contenido rechazan tres; el backdoor necesita el pin. "0 of 4" es la cifra que lee la puerta (§5.3).

### 4.6 Lo que el pin no detecta

**Código.** El script escribe un segundo fichero de bloqueo a partir del propio modelo del mirror (con backdoor) y verifica contra él.

**Qué se ve.** `the backdoored forest verifies: digest matches the pin.`

**Cómo leerlo.** Un hash demuestra que un fichero es el que se fijó, no que el fichero fijado sea bueno. Si el pin se toma de la descarga, o si la build del propio proveedor estaba comprometida, el pin acepta el ataque. Lo que cubre ese hueco: firmas que dicen quién publicó un fichero (Sigstore, OpenSSF model signing), procedencia que dice cómo se construyó (SLSA), una lista de materiales de IA (AI bill of materials) y probar los modelos suministrados como no fiables. `main()` devuelve las precisiones, el éxito del disparador, los recuentos de §4.5 y este último resultado.

---

## 5. La puerta de publicación

`demo/run_gate.py` convierte la tabla de correspondencias de la guía técnica (§8.6) en una comprobación que puede bloquear una publicación en la CI. El patrón viene de [safety-trust-engine](https://github.com/olonok69/safety-trust-engine): controles ligados a evidencia, tolerancias numéricas, un veredicto por control y un informe.

### 5.1 Qué hace `run_gate.py`, paso a paso

1. **Lee las opciones.** `--demos` (por defecto `1,2,3,4`), `--regimes` (por defecto `eu_uk,nist_aml,graimatter`), `--fail-under metric=value` (sustituye una tolerancia), `--accept-missing` (demos declaradas fuera de alcance), `--out`, `--show-demos`. `_demo_names()` y `_limits()` las validan.
2. **Ejecuta las demos.** `run_demos()` importa cada script como módulo (`SCRIPTS` asocia `demo1` con `run_demo`, y así con las demás) y llama a su `main()`, con la salida de la demo silenciada salvo con `--show-demos`. Si `sacroml` no está instalado, la demo 2 se omite con un mensaje en lugar de fallar. El resultado es `evidence`: nombre de la demo → el diccionario que devolvió su `main()`.
3. **Juzga.** `build_report()` en `compliance_gate/gate.py` (§5.4).
4. **Escribe y termina.** El informe se escribe como `gate_<packs>.json` y `.md`; el script imprime una línea por categoría, los recuentos de controles y `Gate: PASS` o `FAIL`, y devuelve el código de salida 0 o 1.

### 5.2 Controles y paquetes de regulación (`compliance_gate/controls.py`)

Un `Control` es una obligación que las demos pueden evidenciar:

* `regulation`, `ref`, `label`: qué es, por ejemplo Reglamento de IA de la UE, art. 15(5), evasión del modelo.
* `stages`: las demos que deben ejecutarse para que quede evidenciado.
* `categories`: las categorías cuyo incumplimiento lo hace fallar.
* `binding`: `statute` (ley), `guidance` (voluntario), `supervisory` (expectativa del supervisor) o `recommendation` (el green paper), para que el informe nunca dé a entender más de lo que puede.

Los controles se agrupan en cuatro paquetes: `eu_uk` (art. 15(5) y el código del Reino Unido / ETSI EN 304 223), `nist_aml` (clases de ataque de NIST AI 100-2), `graimatter` (TECH 6, 7, 9-10, 11, 16, más la comprobación cruzada con SACRO-ML) y `us` (NIST AI RMF MEASURE y GOVERN, la gestión federal del riesgo de modelos SR 26-02). `--regimes all` elige los cuatro. Las diez categorías están en `CATEGORIES`.

### 5.3 Métricas, tolerancias y lectores (`compliance_gate/tolerances.py`)

`METRICS` define un `MetricSpec` por cada cifra que juzga la puerta: su categoría, la demo que la produce, su tolerancia, una descripción y dos opciones. `inclusive=True` hace que se supere con `value >= limit` (la regla de la demo 1) en lugar de `value > limit`; `max_p` significa que la métrica solo se supera si además su p-valor es como mucho ese (FDIF). Las tolerancias de privacidad se leen del `POLICY` de la demo 1, así que la puerta y `decide()` no pueden desalinearse; las demás se fijan aquí para el taller (evasión 10%, coincidencia de la copia 80%, subida del backdoor 10 puntos, cero para los recuentos).

Los **lectores** convierten el resultado del `main()` de cada demo en objetos `Reading`, sin recalcular nada:

| Lector | Lee | Métricas |
| --- | --- | --- |
| `demo1_readings()` | el candidato (árbol con wrapper), los rechazos, la recomendación sobre el árbol manipulado, el registro de consultas | AUC de pertenencia, ventaja, TPR al 10% de FPR, FDIF con p; cociente de riesgo de atributos; diferencia de precisión; filas guardadas; cociente de tamaño; ficheros reveladores publicados (de 5); filas del barrido permitidas |
| `demo2_readings()` | los AUC del árbol con wrapper, las dos marcas | AUC medio de SACRO-ML; configuraciones no detectadas (de 2) |
| `demo3_readings()` | tasas de evasión, extracción con el presupuesto de la puerta (200), la petición que supera el presupuesto, las filas del backdoor | tres tasas de evasión; coincidencia de la copia; petición por encima del presupuesto permitida; subida del backdoor = peor éxito del disparador tras el envenenamiento menos el éxito del modelo limpio con el mismo disparador |
| `demo4_readings()` | el recuento de ficheros manipulados aceptados | ficheros de la cadena de suministro aceptados (de 4) |

`breaches(spec, reading, limit)` aplica la regla. Un valor que falta nunca supera la tolerancia; aparece como "not measured".

### 5.4 Veredictos (`compliance_gate/gate.py`)

`build_report(evidence, regimes, overrides, accept_missing)`:

1. Combina las tolerancias con las sustituciones de `--fail-under` (un nombre de métrica desconocido es un error).
2. Lee cada demo que se ejecutó y construye un `MetricVerdict` por lectura, agrupados en un `CategoryVerdict` por categoría. Una categoría está **dentro** de tolerancia cuando ninguna de sus métricas la supera.
3. Da a cada control elegido un `ControlVerdict`: **not_evidenced** si alguna de sus demos no se ejecutó (marcado `accepted` cuando todas las demos que faltan se declararon con `--accept-missing`); si no, **fail** si alguna de sus categorías superó la tolerancia, y **pass** en caso contrario.
4. `GateReport.passed` es verdadero solo si todas las categorías están dentro de tolerancia y todos los controles cumplen o son un not_evidenced aceptado. Nunca hay un verde silencioso: un control sin evidencia hace fallar la ejecución salvo que la ejecución diga por qué.

`write_json()` y `write_markdown()` escriben el mismo contenido para máquinas y para personas, con el aviso de que la correspondencia y las tolerancias se hicieron para este repositorio.

### 5.5 Cómo leer el informe sembrado

`demo/output/gate/gate_eu_uk-nist_aml-graimatter.md` es la ejecución sobre las demos 1, 3 y 4 con la demo 2 declarada fuera de alcance:

* **Puerta de tolerancias.** Todas las métricas de privacidad de la demo 1 están dentro de tolerancia (son las mismas cifras que permiten a `decide()` publicar el árbol con wrapper en §1.5). La evasión (78,7%, 32,8%, 20,7% frente a 10%), la extracción (86,9% frente a 80%) y el envenenamiento (una subida de 71,7 puntos frente a 10) la superan. Cadena de suministro: 0 de 4 aceptados, dentro.
* **Controles.** El paquete de GRAIMATTER cumple, salvo la comprobación cruzada con SACRO-ML, que queda sin evidencia (fuera de alcance). El art. 15(5) falla en envenenamiento de datos, evasión y confidencialidad (por la extracción), y cumple en envenenamiento del modelo gracias a la demo 4. Los controles del NIST siguen el mismo reparto.
* **La lección.** El modelo que publican las comprobaciones de privacidad de GRAIMATTER no es resistente en el sentido del art. 15(5). La privacidad es una rama del AML.

`gate_us.md` es la misma evidencia vista con el paquete de EE. UU.

### 5.6 La puerta en la CI, y los tests

`.github/workflows/gate.yml` ejecuta dos jobs. `lint-and-test` ejecuta `ruff` y `pytest`. `gate` ejecuta la puerta dos veces: el paquete de GRAIMATTER sobre la demo 1, que debe pasar, y todos los paquetes sobre las demos 1, 3 y 4, que deben terminar con código 1 y superar la tolerancia exactamente en evasión, extracción y envenenamiento. Una puerta que bloqueara por cualquier otro motivo, o que dejara de bloquear, pondría la CI en rojo.

`tests/test_gate.py` vuelve a ejecutar las demos 1, 3 y 4 y comprueba que sus informes siguen coincidiendo con los ficheros versionados en `demo/output/`, salvo las líneas que dependen de la máquina y que se enumeran en §6 (`test_regenerated_outputs_match_versioned`), que la puerta decide igual que el `decide()` de la demo 1 y que los veredictos sembrados son los de §5.5. Por eso un cambio en las cifras de una demo debe ir acompañado de su informe regenerado.

---

## 6. Reproducibilidad y salvedades conocidas

* **Semillas.** Las demos 1, 3 y 4 dan el mismo informe en cada ejecución con las mismas versiones de las bibliotecas. Los tests dependen de ello. Otra versión de scikit-learn puede cambiar un random forest y, con él, las cifras.
* **La demo 2 no es reproducible de una ejecución a otra.** Los ataques del paquete hacen sus propias divisiones aleatorias; el AUC medio de pertenencia del árbol con wrapper pasó de 0,494 a 0,487 entre dos ejecuciones. Sus ficheros `report.json` se amplían en cada ejecución, no se sustituyen. Por eso la demo 2 queda fuera de la CI y su control de la puerta se declara allí fuera de alcance.
* **Líneas que dependen de la máquina.** La última línea de la demo 1 imprime la ruta absoluta de la máquina que la ejecutó (por ejemplo `Full write-up: D:\repos\...`). El tamaño serializado del árbol sin restricciones (§1.4) y los hashes de los modelos serializados (§4.1 a §4.3) cambian entre versiones de scikit-learn, así que tus hashes pueden diferir de los que se citan aquí; los veredictos no. `_normalise()` de los tests enmascara esas tres cosas antes de comparar.
* **`n_jobs=-1`** en las demos 3 y 4 usa todos los núcleos; cambia la velocidad, no los resultados.
* **Escala.** Las cohortes son de cientos o miles de filas, los modelos son árboles y random forests, y los ataques son esbozos didácticos. La guía técnica (§25) enumera lo que las demos no muestran.
