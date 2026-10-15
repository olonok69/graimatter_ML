# Traspaso: llevar la puerta de cumplimiento de safety-trust-engine a graimatter_ML

Documento para otra sesión de trabajo. Recoge qué se puede reutilizar de [safety-trust-engine](https://github.com/olonok69/safety-trust-engine) en este repositorio y en qué orden. Es una propuesta, no código: quien lo implemente decide los detalles, pero debe respetar las restricciones del final.

## Punto de partida

* graimatter_ML tiene tres demos sobre datos sintéticos (`demo/run_aml_demo.py`, `demo/run_demo.py`, `demo/run_sacroml_demo.py`), una guía EN/ES y un deck. Ya cita safety-trust-engine como repositorio compañero para LLMs y agentes (README, guía §5, `docs/make_deck.py`).
* No hay CI, ni tests, ni `pyproject.toml`: solo `demo/requirements.txt` (`numpy`, `scikit-learn`, `sacroml`).
* La decisión de publicación vive en `demo/graimatter_demo/disclosure.py`: `POLICY` (umbrales de la demo) y `decide()`, que devuelve `{"release": bool, "reasons": [texto libre]}`. Solo cubre la demo 1; la demo 3 (evasión, extracción, backdoor) mide pero no decide nada.
* La tabla de marcos del README (Parte 2) es estática y la fila de prompt injection tiene "–" en la columna de demos.

Lo que **no** se reutiliza: garak, PyRIT y AgentDojo atacan LLMs y no sirven contra el árbol ni el random forest de estas demos. Lo reutilizable es el patrón: controles regulatorios mapeados a evidencia, tolerancias numéricas, estado `not_evidenced` y un artefacto auditable que hace fallar CI.

## Recomendaciones, por orden

Las tres primeras forman un solo PR coherente. La 4 y la 5 pueden ir después.

### 1. Evidencia por control, sin "verde silencioso"

Portar el modelo de `src/safety_engine/compliance.py` y `report.py` de safety-trust-engine:

* Un `Control` con `regulation`, `ref`, `label`, `stages` (aquí: qué demo aporta la evidencia), `categories`, `note` y `binding` (`statute | guidance | supervisory`).
* Cada control se evalúa como `pass`, `fail` o `not_evidenced`. Un control cuya demo no se ejecutó (por ejemplo SACRO-ML sin instalar) sale `not_evidenced`, nunca `pass`.
* Salida: un JSON (máquina) y un Markdown (persona) por ejecución en `demo/output/`, con el mismo espíritu de esquema que `st-*.json` (`regimes`, `compliance`, `overall`), para poder enseñar ambos informes juntos.

Controles candidatos, tomados de la tabla de la Parte 2 del README (comprobar cada cita contra los PDFs del repo antes de usarla):

| Regulación | Ref | Evidencia | Categorías |
| --- | --- | --- | --- |
| EU AI Act | Art. 15(5) | demos 1, 3 | evasion, poisoning, membership, attribute, extraction |
| NIST AI 100-2e2025 | NISTAML.025 / .023 / .031 / .033 | demos 1, 3 | una categoría cada una |
| UK Code of Practice / ETSI EN 304 223 | principios 3.1, 6.2, 9.4 | demos 1, 3 | según la tabla |
| GRAIMATTER | TECH 6, 7, 9-11, 16 | demo 1 (y 2 si corre) | membership, attribute, stored_rows, query_budget |

Marcar `binding` con honestidad: el EU AI Act es estatuto, NIST y el Code son guía, GRAIMATTER es recomendación. El README ya avisa de que el mapeo es propio; el artefacto debe repetirlo.

### 2. Puerta de tolerancias

* Convertir `POLICY` y las métricas de la demo 3 en tolerancias por categoría, al estilo de `DEFAULT_TOLERANCES` y `--fail-under` en safety-trust-engine. Métricas ya calculadas: AUC de membresía, ventaja, TPR al 10 % FPR, FDIF, ratio de riesgo de atributo (demo 1); tasa de evasión, acuerdo de la copia extraída, tasa de activación del backdoor (demo 3).
* El script debe salir con código distinto de 0 si alguna categoría supera su tolerancia o algún control queda `not_evidenced` (política estricta, igual que `SafetyReport.overall_pass`).
* Documentar junto a las tolerancias que son un apetito de riesgo pactado con el responsable de los datos (GRAIMATTER ELA 8) y no umbrales del paper ni de NIST, como ya hace `disclosure.py`.
* No cambiar los resultados sembrados de las demos: la puerta lee las métricas, no las recalcula de otra forma. Los informes en `demo/output/` deben quedar idénticos salvo los ficheros nuevos.

### 3. CI y tests

* Añadir `.github/workflows/` con un job que instale `numpy` y `scikit-learn` (sin `sacroml`, que arrastra PyTorch), pase `ruff` y `pytest`, y ejecute las demos 1 y 3, que tardan segundos y no necesitan claves.
* Tests mínimos: la puerta decide igual sobre los valores sembrados; un control sin demo ejecutada sale `not_evidenced`; los informes regenerados coinciden con los versionados en `demo/output/` (detecta cambios silenciosos de resultados).
* La demo 2 (SACRO-ML) se queda fuera de CI; sus controles aparecerán como `not_evidenced` en ese job, y eso es el comportamiento correcto, no un fallo a tapar. Ojo con lo que pasa en safety-trust-engine: el job `safety-gate` falla siempre por controles no evidenciados. Aquí conviene que el job de CI seleccione solo los controles que sus demos pueden evidenciar, o que lo diga explícitamente.
* Considerar un `pyproject.toml` con `uv` como en safety-trust-engine, manteniendo `demo/requirements.txt` porque el README lo usa.

### 4. Pack US (opcional, después)

Un clasificador de riesgo encaja directamente en la gestión de riesgo de modelos de SR 26-02, no por analogía como un LLM. Reutilizar las filas del pack `us` de `compliance.py` (NIST AI RMF MEASURE 2.6 y 2.7, Federal MRM validation / monitoring / documentation) y añadir MEASURE 2.10 (privacidad) para la inferencia de pertenencia y de atributo. Lectura útil para la presentación: el holdout que guarda la TRE (TECH 6) es la validación independiente, y la puerta en CI es la monitorización continua. Seleccionable con un `--regimes` como en safety-trust-engine.

### 5. Hueco de IA generativa (opcional)

Rellenar el "–" de la fila de prompt injection con una "demo 4" que ejecute `python -m safety_engine.run --demo --regimes eu_uk,us` de safety-trust-engine (modo demo, sin claves), y una diapositiva que muestre los dos informes con el mismo esquema. No copiar código de safety-trust-engine aquí: enlazar y ejecutar desde su repo.

## Restricciones

* Commits con la identidad de Juan (`Juan Huertas <olonok@gmail.com>`), sin trailers `Co-Authored-By` ni `Claude-Session`, y sin atribución a IA en descripciones de PR ni en ficheros. Se pueden copiar los hooks de `.githooks/` de safety-trust-engine para reforzarlo.
* Datos sintéticos únicamente; no añadir datos reales.
* Si cambian cifras o tablas, actualizar a la vez README, guía EN y ES y deck, que hoy coinciden con `demo/output/`.
* Trabajar en PR, no directamente en `main`.
