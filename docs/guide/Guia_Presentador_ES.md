# Machine learning adversarial: guía del presentador

**Un acompañamiento, diapositiva a diapositiva, de `docs/Adversarial_ML.pptx` (41 diapositivas)**

Esta guía es para quien presente las diapositivas del taller. Sigue las diapositivas en orden, con una sección por diapositiva, y te da qué decir, las cifras que conviene tener a mano, las preguntas que suele hacer el público y dónde mirar cuando quieras más. No sustituye a la guía técnica ([AML_Guia_Tecnica_ES.md](AML_Guia_Tecnica_ES.md); versión en inglés en [AML_Technical_Guide_EN.md](AML_Technical_Guide_EN.md)), que sigue siendo la referencia para los ingenieros: explica a fondo cada ataque, cada métrica y cada línea de código. Esta guía tiene menos código y más explicación, y cada sección remite a las secciones de la guía técnica que la respaldan. La versión en inglés de esta guía es [Presenter_Guide_EN.md](Presenter_Guide_EN.md). Si alguien pregunta cómo calcula una demo una cifra, la guía de las demos ([español](Guia_Demos_ES.md), [inglés](Demo_Guide_EN.md)) recorre el código que hay detrás de cada sección de su salida.

---

## Cómo usar esta guía

Cada diapositiva tiene los mismos bloques:

* **En pantalla**: lo que muestra la diapositiva, para que puedas ensayar sin tenerla abierta.
* **Qué decir**: un guion en estilo hablado. Léelo una o dos veces y después preséntalo con tus palabras. Las notas del orador de las diapositivas son una versión más corta del mismo texto.
* **Datos clave**: las cifras y las fuentes que te pueden pedir que repitas. Todas las cifras de las demos proceden de los informes sembrados de `demo/output/` y no cambian entre ejecuciones.
* **Si preguntan**: respuestas breves a preguntas que surgen a menudo.
* **Para profundizar**: las secciones de la guía técnica (escritas "GT §x", donde GT significa guía técnica, es decir, [AML_Guia_Tecnica_ES.md](AML_Guia_Tecnica_ES.md)), la salida de las demos y los documentos fuente.
* **Siguiente**: una frase para pasar a la diapositiva siguiente.

Las diapositivas están en inglés. Cada sección da el título traducido y, justo debajo, el título tal como aparece en la diapositiva, para que puedas localizarla. Para no confundir los anexos, esta guía escribe "Anexo A" o "Anexo B de la GT" para los anexos de la guía técnica y "anexo E, F o G del paper" para los del green paper de GRAIMATTER.

La presentación tiene tres partes más un bloque de cierre:

| Parte | Diapositivas | Guía técnica | Minutos |
|---|---|---|---|
| Apertura | 1-2 | §1 | 2,5 |
| Parte 1 · Ataques | 3-14 | §1-7, Anexo B | 37,5 |
| Parte 2 · Marcos | 15-19 | §8 | 13 |
| Parte 3 · Un caso de alta confianza: GRAIMATTER | 20-38 | §9-16, §19 | 35,5 |
| Cierre: puerta, demos, referencias | 39-41 | §17, §18, §21 | 4,5 |
| Las preguntas se responden dentro de cada bloque | | | 93 en total |

La parte 1 no sigue exactamente el orden de la guía técnica: las diapositivas muestran la evasión (diapositiva 7), el envenenamiento (8), la familia de privacidad (9), la extracción (10) y la cadena de suministro (11), mientras que la guía agrupa los ataques de las demos 3 y 4 en la §3 y la privacidad en la §4. Las líneas "Para profundizar" resuelven el salto.

### Antes de la sesión

* **Ejecuta las demos una vez**, para tener los informes a mano y saber cuánto tardan: `uv run python demo/run_aml_demo.py` (demo 3, segundos), `uv run python demo/run_supply_chain_demo.py` (demo 4, segundos), `uv run python demo/run_demo.py` (demo 1, segundos), `uv run python demo/run_sacroml_demo.py` (demo 2, unos minutos) y `uv run python demo/run_gate.py`. La instalación está en el [README](../../README.md) y en GT §18.
* **Ten abiertos**: `demo/output/aml_report.txt`, `demo/output/supply_chain_report.txt`, `demo/output/demo_report.txt`, `demo/output/sacroml/sacroml_report.txt`, `demo/output/gate/gate_eu_uk-nist_aml-graimatter.md` (o el informe de la puerta que escriba tu ejecución) y los dos PDF de la raíz del repositorio, `NIST.AI.100-2e2025.pdf` y `GRAIMATTER Green Paper.pdf`.
* **Decide si harás demos en directo.** Si tienes un terminal, las demos 3 y 4 durante las diapositivas 7 a 11 y la demo 1 durante las diapositivas 27 a 32 se ejecutan en segundos. La demo 2 es mejor enseñarla desde su informe guardado.
* **Tres mensajes que tienen que quedar**, recortes lo que recortes: (1) un modelo añade tres cosas que atacar: sus datos, su fichero y sus respuestas; (2) los marcos nombran los mismos ataques de forma distinta, y una tabla de correspondencias permite que una sola prueba hable el idioma de todos; (3) GRAIMATTER muestra cómo un sector de alta confianza prueba un modelo antes de que salga, y solo cubre la privacidad.

### Si tienes menos tiempo

* **45 minutos:** diapositivas 1-5, 7, 8, 10, 11, 14, 15, 17, 19, 20-22, 25, 27, 28, 37, 39, 40.
* **20 minutos:** diapositivas 1, 3, 5, 7, 8, 10, 19, 20, 27, 37, 39.

---

## Apertura

### Diapositiva 1 · Machine learning adversarial: ataques, marcos y un caso de alta confianza

*Título en la diapositiva: «Adversarial machine learning: attacks, frameworks and a high-trust case»*

*Aproximadamente 1 minuto.*

**En pantalla.** El título, los cinco marcos en el subtítulo (NIST AI 100-2e2025, MITRE ATLAS, OWASP, Reglamento de IA de la UE, código de buenas prácticas del Reino Unido), un resumen de una línea, tres etiquetas ("4 demos, una cohorte sintética", "5 marcos comparados", "GRAIMATTER como caso de estudio") y la dirección del repositorio.

**Qué decir.** «Esta sesión trata de cómo se atacan los modelos de machine learning y de qué podemos hacer al respecto. Tiene tres partes. Primero, los ataques: cómo se puede atacar un modelo a través de sus datos de entrenamiento, a través del propio fichero del modelo y a través de las respuestas que da, con el vocabulario de la taxonomía de ML adversarial del NIST y una pequeña demo para cada rama. Segundo, los marcos que llevan todo esto a la práctica: MITRE ATLAS, las dos listas top ten de OWASP, el artículo 15 del Reglamento de IA de la UE y el código de buenas prácticas del Reino Unido, que ahora es una norma europea, la ETSI EN 304 223. Tercero, un caso concreto de alta confianza: el green paper de GRAIMATTER, que explica a un entorno de investigación seguro cómo decidir si un modelo entrenado se puede publicar, con otras dos demos. Todo lo que vais a ver funciona con datos sintéticos. En las demos no hay ningún paciente real, y todo el código y las guías están en el repositorio de la diapositiva.»

**Datos clave.** Las cuatro demos comparten un generador de cohorte sintética (semilla 7). Cinco marcos. Las guías existen en inglés y en español.

**Si preguntan.** *¿Esto va de LLM?* En parte. La parte 1 tiene una diapositiva sobre IA generativa (la 12); las demos usan modelos clásicos porque ahí los ataques se ven mejor. El repositorio complementario safety-trust-engine prueba LLM y agentes.

**Para profundizar.** Introducción de la GT y §1; README del repositorio.

**Siguiente.** «Así se reparte el tiempo.»

### Diapositiva 2 · Tres partes: los ataques, los marcos, un caso de alta confianza

*Título en la diapositiva: «Three parts: the attacks, the frameworks, a high-trust case»*

*Aproximadamente 1,5 minutos.*

**En pantalla.** La agenda en tres columnas: 1 Ataques (taxonomía del NIST, evasión, envenenamiento, privacidad, IA generativa, incidentes reales, mitigaciones, demos 3 y 4), 2 Marcos (NIST, ATLAS, OWASP, art. 15 del Reglamento de IA, código del Reino Unido y ETSI EN 304 223, una tabla de correspondencias), 3 Caso de alta confianza (GRAIMATTER, demos 1 y 2, qué se traslada). Debajo: qué muestra cada demo y los cuatro scripts.

**Qué decir.** «Vamos de lo general a lo concreto. La parte 1 nos da un vocabulario común para los ataques. La parte 2 relaciona ese vocabulario con lo que piden las normas y la ley. La parte 3 mira un sector que ha resuelto esto a fondo para una rama, la privacidad, porque en ese sector lo que sale del edificio es el propio modelo. Hay cuatro demos. La demo 3, que vemos primero, ataca un modelo de riesgo con evasión, plantando un backdoor y copiándolo a través de su API. La demo 4 manipula un modelo y sus ficheros en el camino del proveedor al usuario. Las demos 1 y 2 son las comprobaciones de GRAIMATTER: inferencia de pertenencia y de atributos, y los controles que aplica un entorno de investigación seguro antes de publicar. Son pequeñas a propósito: numpy y scikit-learn, se ejecutan en segundos, así que podéis cambiar un parámetro y ver qué pasa.»

**Datos clave.** Scripts: `demo/run_aml_demo.py` (demo 3), `demo/run_supply_chain_demo.py` (demo 4), `demo/run_demo.py` (demo 1), `demo/run_sacroml_demo.py` (demo 2). La numeración de las demos sigue el orden en que se escribieron, no el orden de la charla.

**Si preguntan.** *¿Por qué la demo 3 va primero?* Se añadió más tarde para cubrir los ataques a la integridad, pero pertenece a la parte 1, así que la charla la enseña primero; la demo 4, añadida la última para la cadena de suministro, va justo después.

**Para profundizar.** Contenido de la GT y Anexo A (agenda sugerida).

**Siguiente.** «Empecemos por la razón de que un modelo necesite su propia seguridad.»

---

## Parte 1 · Ataques

### Diapositiva 3 · Un modelo añade una superficie de ataque que la seguridad clásica no cubre

*Título en la diapositiva: «A model adds attack surface that classic security does not cover»*

*Aproximadamente 2,5 minutos.*

**En pantalla.** Tres tarjetas: *Los datos* (envenenamiento y backdoors; los datos a escala web lo abaratan), *El modelo* (se puede copiar, editar después del entrenamiento, sustituir en la cadena de suministro o llevar filas de entrenamiento dentro), *Las respuestas* (cada predicción filtra un poco). Una banda con NIST §4.1.2: para muchas tareas no hay algoritmos de ML teóricamente seguros, así que las mitigaciones son "un proceso intrínsecamente ad hoc y falible".

**Qué decir.** «La seguridad clásica protege código, credenciales e infraestructura. Un sistema de machine learning añade tres cosas más a las que puede ir un atacante. La primera son los datos de entrenamiento. Quien puede añadir o cambiar filas de entrenamiento puede dirigir lo que aprende el modelo, y con conjuntos de datos sacados de la web eso puede salir sorprendentemente barato: el NIST cita trabajos que muestran que un atacante con poco presupuesto puede controlar parte de conjuntos de datos públicos. La segunda es el propio modelo. Es un fichero. Se puede robar, editar después del entrenamiento o sustituir por un modelo envenenado descargado de un hub, y algunos tipos de modelo llevan dentro sus filas de entrenamiento. La tercera son las respuestas. Cada predicción filtra un poco de información, y con suficientes consultas un atacante puede engañar al modelo, copiarlo o averiguar quién estaba en sus datos de entrenamiento. El NIST es directo sobre el estado de la cuestión: para muchas tareas no hay un algoritmo teóricamente seguro, así que diseñar defensas es ad hoc y falible. La regla práctica que recorre toda esta sesión es: probad el sistema frente a ataques, no deis por hecho que una defensa funciona.»

**Datos clave.** NIST AI 100-2e2025, marzo de 2025, secciones 2.2 a 2.4, 3.2 y 4.1.2. "Diseñar mitigaciones es un proceso intrínsecamente ad hoc y falible" (§4.1.2, traducción propia).

**Si preguntan.** *¿No es esto seguridad normal y corriente?* La seguridad normal sigue haciendo falta: control de acceso, parches, registros. Estos ataques funcionan aunque todo eso esté en su sitio, porque usan las entradas y salidas normales del modelo.

**Para profundizar.** GT §1.

**Siguiente.** «El NIST sitúa estos ataques en el ciclo de vida de un modelo.»

### Diapositiva 4 · Dónde caen los ataques en la vida de un modelo

*Título en la diapositiva: «Where attacks land in the life of a model»*

*Aproximadamente 3 minutos.*

**En pantalla.** Una figura con cuatro fases de izquierda a derecha (Datos, Entrenamiento, Fichero del modelo, Despliegue), la capacidad del atacante que necesita cada fase (control de los datos de entrenamiento, control del código fuente o del modelo, acceso al fichero, acceso de consulta y control de los datos de prueba) y los ataques que caen en cada una: envenenamiento de datos, backdoors, envenenamiento con etiquetas limpias y envenenamiento web split-view sobre los datos; envenenamiento del modelo, modelos preentrenados maliciosos y dependencias envenenadas en el entrenamiento; lectura de filas guardadas, manipulación después de `fit()`, datos escondidos en los parámetros y ataques de privacidad de caja blanca sobre el fichero; evasión, extracción, inferencia de pertenencia y de atributos e inyección de prompts en el despliegue. Una banda sombreada marca lo que controla GRAIMATTER: el fichero del modelo y sus consultas, solo para privacidad.

**Qué decir.** «El NIST separa los ataques durante el entrenamiento de los ataques durante el despliegue, y para cada uno se pregunta qué tiene que poder tocar el atacante. Si puede aportar datos de entrenamiento, puede envenenarlos. Si puede controlar el código de entrenamiento, una biblioteca o un modelo preentrenado sobre el que construís, puede envenenar el propio modelo, y ese es el riesgo de la cadena de suministro. Si consigue el fichero del modelo, puede leer lo que guarda, editarlo o esconder datos dentro. Y si lo único que tiene es la posibilidad de enviar consultas, aún puede evadir el modelo, copiarlo o lanzar ataques de privacidad contra él. Fijaos en la banda sombreada: ahí es donde trabaja GRAIMATTER, el fichero del modelo y las consultas que se le hacen, y solo para la privacidad. No mira si el modelo se puede engañar o si se entrenó con datos envenenados. Ese hueco es la razón de ser de la demo 3, y volveremos a él al final de la parte 3.»

**Datos clave.** NIST §2.1.1 (fases) y §2.1.3 (seis capacidades: control de los datos de entrenamiento, control del modelo, control de los datos de prueba, límite sobre las etiquetas, control del código fuente, acceso de consulta).

**Si preguntan.** *¿Dónde encaja un error del propio científico de datos?* GRAIMATTER lo llama RT1, un investigador bienintencionado que guarda demasiado en el fichero del modelo (diapositiva 22). No es un ataque, pero crea la misma exposición.

**Para profundizar.** GT §1 y §2.2; NIST §2.1.1 y §2.1.3.

**Siguiente.** «La siguiente pregunta es qué quiere el atacante.»

### Diapositiva 5 · Tres objetivos del atacante: disponibilidad, integridad, privacidad

*Título en la diapositiva: «Three attacker objectives: availability, integrity, privacy»*

*Aproximadamente 2,5 minutos, más si respondes preguntas sobre clases concretas.*

**En pantalla.** La figura de la taxonomía del NIST: tres columnas por objetivo, cada una con sus clases de ataque e identificadores. Disponibilidad (NISTAML.01): envenenamiento de datos .013, envenenamiento del modelo .011, envenenamiento con etiquetas limpias .012, energía y latencia .014. Integridad (NISTAML.02): evasión .022, evasión de caja negra .025, envenenamiento con backdoor .023, envenenamiento dirigido .024, backdoor con etiquetas limpias .021. Privacidad (NISTAML.03): inferencia de pertenencia .033, reconstrucción .032, inferencia de propiedades .034, extracción del modelo .031. Notas al pie: la inferencia de atributos no tiene ID propio; la cadena de suministro (NISTAML.05) es envenenamiento del modelo a través de un modelo de terceros (.051); la IA generativa añade la inyección de prompts (.018, .015) y las salidas desalineadas (.027). Las casillas que ejecutan las demos están resaltadas.

**Qué decir.** «La taxonomía del NIST parte de lo que quiere el atacante. Hay tres objetivos. *Disponibilidad*: dejar el sistema inservible para todos, bien envenenando su entrenamiento para que empeore con cualquier entrada, bien enviando entradas que lo vuelvan lento y caro. *Integridad*: hacer que el modelo dé la respuesta que quiere el atacante, bien cambiando la entrada en el despliegue, que es la evasión, bien envenenando el entrenamiento para que ciertas entradas, o las entradas que llevan un disparador secreto, reciban la respuesta del atacante. *Privacidad*: averiguar algo que debería seguir oculto, sobre los datos de entrenamiento, por ejemplo si una persona estaba en ellos, o sobre el propio modelo, copiándolo. Una cuarta rama, la cadena de suministro, cubre los modelos envenenados que os llegan a través de un proveedor. Cada clase tiene un identificador, así que un informe de pruebas puede decir NISTAML.033 en lugar de "algún ataque de privacidad". Las casillas resaltadas son las que ejecutan nuestras demos.»

Después enlaza con lo que el público ya conoce: «Si esto os suena, es normal. Disponibilidad, integridad y confidencialidad son la tríada CIA que la seguridad de la información ha protegido siempre. El NIST llama privacidad a la tercera, porque en machine learning abarca dos cosas a la vez: la confidencialidad del modelo, sus pesos y su arquitectura, y la privacidad de las personas que hay en sus datos de entrenamiento. El Reglamento de IA de la UE usa la palabra clásica para los mismos ataques: ataques a la confidencialidad. Así que el atacante quiere lo de siempre. Lo nuevo es dónde puede conseguirlo: a través de los datos de entrenamiento, del fichero del modelo y de las respuestas, que es la diapositiva 3. La cadena de suministro no es un cuarto objetivo; es una vía de entrada, y lo que entra por ella rompe una de las tres propiedades.»

Usa el resumen por objetivo si alguien pregunta qué significa una casilla; el [Anexo B de la guía técnica](AML_Guia_Tecnica_ES.md#anexo-b-las-clases-de-ataque-del-nist-una-a-una) tiene un párrafo para cada clase. Las tres cosas que más se confunden:

* *Backdoor frente a envenenamiento dirigido.* Un backdoor planta un disparador: cualquier entrada que lo lleve en el despliegue recibe la respuesta del atacante. El envenenamiento dirigido cambia la respuesta para unas pocas entradas concretas elegidas de antemano, que no se modifican en el despliegue.
* *Evasión frente a evasión de caja negra.* El mismo objetivo; la versión de caja negra solo ve las salidas del modelo, puntuaciones o etiquetas. La demo 3 es de caja negra y solo ve etiquetas.
* *Etiquetas limpias (clean-label).* El atacante controla las filas envenenadas pero no sus etiquetas, así que todas las etiquetas son correctas y una revisión de etiquetas no encuentra nada.

**Datos clave.** Tríada CIA: disponibilidad = NISTAML.01, integridad = NISTAML.02, confidencialidad = NISTAML.03 (privacidad), cadena de suministro = una vía de entrada. NIST "Predictive AI and Generative AI Taxonomy Index", pp. x-xi, y §2.1.2. La segunda cifra de un ID indica el objetivo (1 disponibilidad, 2 integridad, 3 privacidad, 5 cadena de suministro); el envenenamiento del modelo aparece como .011, .026 y .051 según su propósito.

**Si preguntan.** *¿Por qué el envenenamiento del modelo aparece en varios objetivos?* Porque el ID registra el propósito además de la técnica. *¿Dónde está la inferencia de atributos?* El NIST la describe entre los objetivos de privacidad de los datos (§2.1.2, §2.4.1) sin ID propio; la puerta de publicación la archiva bajo reconstrucción, .032. *¿Por qué el NIST dice privacidad y no confidencialidad?* El NIST lo explica en §2.1.2: confidencialidad es el término tradicional, pero privacidad abarca tanto los secretos del modelo como a las personas que hay en los datos. Leed NISTAML.03 como confidencialidad. *¿Dónde encaja NISTAML.04?* El uso indebido solo existe para la IA generativa y encaja peor en la tríada: el atacante usa el sistema tal como está diseñado, pero elude las restricciones de su propietario, algo más cercano a un fallo de autorización.

**Para profundizar.** GT §2.1 (el párrafo sobre la tríada CIA) y **[Anexo B](AML_Guia_Tecnica_ES.md#anexo-b-las-clases-de-ataque-del-nist-una-a-una)** (la tabla de correspondencias y después cada clase explicada, con sus defensas y dónde aparece en el repositorio).

**Siguiente.** «Dos preguntas más clasifican un ataque: qué puede tocar el atacante y cuánto sabe.»

### Diapositiva 6 · Qué puede tocar el atacante y cuánto sabe

*Título en la diapositiva: «What the attacker can touch, and how much they know»*

*Aproximadamente 1,5 minutos.*

**En pantalla.** Una tabla con las seis capacidades, un ataque típico y dónde lo muestra el repositorio (control de los datos de entrenamiento: backdoor de la demo 3 con un 1-5% de las filas; control del modelo: la demo 1 detecta ediciones después de `fit()`; control de los datos de prueba: campos de formulario falseados en la demo 3; límite sobre las etiquetas y control del código fuente: no se muestran; acceso de consulta: demos 1 a 3). Tres tarjetas sobre el conocimiento: caja blanca (GRAIMATTER la supone, porque el fichero sale), caja gris, caja negra (la demo 3 solo usa etiquetas).

**Qué decir.** «Las capacidades dicen qué puede cambiar o alcanzar el atacante: los datos de entrenamiento, las etiquetas, el modelo, el código, las entradas de prueba o solo la interfaz de consulta. El conocimiento dice cuánto sabe del sistema. Caja blanca significa que lo sabe todo: datos, arquitectura, parámetros. El NIST señala que esto es poco realista en muchos despliegues, pero es la forma de probar frente al peor caso. En un entorno de investigación seguro, el caso de caja blanca no es hipotético: en cuanto se publica el fichero del modelo, quien lo obtenga tiene acceso completo. Caja negra significa que solo puede consultar. Es el escenario más práctico, y los ataques de la demo 3 son de caja negra: solo ven la etiqueta predicha.»

**Datos clave.** NIST §2.1.3 y §2.1.4. La demo 3 solo ve etiquetas.

**Si preguntan.** *¿Es habitual la caja gris?* Mucho: conocer la arquitectura porque es un modelo estándar, o tener datos de la misma población, es lo típico.

**Para profundizar.** GT §2.2 y §2.3.

**Siguiente.** «Veamos en acción el primer ataque: la evasión.»

### Diapositiva 7 · Evasión: cambiar la entrada, no el modelo

*Título en la diapositiva: «Evasion: change the input, keep the model»*

*Aproximadamente 4,5 minutos, incluida una ejecución en directo de la demo 3 si la enseñas.*

**En pantalla.** Una figura de la demo 3: proporción de personas puntuadas como riesgo alto que obtienen una puntuación de riesgo bajo falseando campos del formulario, en tres escenarios. Los tres campos autodeclarados: 78,7% evadidos (58,7% con un solo escalón). Tabaco verificado con una prueba: 32,8% (18,2%). Tabaco y peso medidos en consulta: 20,7% (12,8%). Una nota: comprobar los campos sobre los que un atacante puede mentir reduce la evasión del 79% al 21%; el entrenamiento adversarial no impediría que una persona mienta.

**Qué decir.** «La evasión cambia la entrada para que el modelo se equivoque, sin tocar el modelo. La demo 3 entrena un random forest que puntúa a las personas como riesgo alto o bajo a partir de un formulario de salud. Una persona puntuada como riesgo alto solo puede editar lo que nadie comprueba: puede quitar la marca de fumador o declarar su peso o su tensión arterial una o dos bandas por debajo. Prueba primero la edición más pequeña y consulta hasta que la etiqueta cambia. El ataque solo ve la etiqueta predicha. Con los tres campos autodeclarados, el 78,7% de las personas marcadas obtiene una puntuación de riesgo bajo, la mayoría con un solo escalón. Si el tabaco se verifica con una prueba, baja al 32,8%. Si además el peso se mide en consulta, al 20,7%. La lección es que la defensa que funcionó aquí no es un modelo más listo, sino verificar las entradas sobre las que una persona tiene incentivos para mentir. La defensa más conocida contra la evasión, el entrenamiento adversarial, hace que un modelo sea robusto frente a pequeñas perturbaciones; no hace nada contra una persona que declara un valor falso. Los ejemplos reales del NIST van en la misma línea: ID.me registró más de 80.000 intentos de engañar a su verificación facial en el segundo semestre de 2020, y unos atacantes burlaron un detector comercial de phishing recortando y difuminando, no con una optimización ingeniosa. Las tres defensas que según el NIST han resistido, el entrenamiento adversarial, el suavizado aleatorio y la verificación formal, cuestan todas precisión o cómputo.»

**Datos clave.** 974 filas de prueba puntuadas como riesgo alto. Evadidos: 78,7% / 32,8% / 20,7%; con un escalón 58,7% / 18,2% / 12,8%; con dos escalones 70,5% / 28,6% / 20,7%. Precisión del objetivo 0,635 (etiqueta sintética con ruido). Clase del NIST: evasión de caja negra, NISTAML.025; OWASP ML01; ATLAS AML.T0015.

**Si preguntan.** *¿Una precisión de 0,635 no es demasiado baja para que importe?* La etiqueta es un sorteo con ruido, así que ningún modelo llega mucho más arriba; el ataque trata de cambiar decisiones, no de precisión. *¿Es un ataque real o un juguete?* Es una búsqueda voraz sobre unos pocos campos, sencilla a propósito. Los ataques optimizados lo harían al menos igual de bien.

**Para profundizar.** GT §3.1 y Anexo B.2 (NISTAML.022 y .025); `demo/output/aml_report.txt`, sección 1; NIST §2.2, §2.2.4, §2.2.5.

**Siguiente.** «La evasión ataca el modelo desplegado. El envenenamiento va un paso antes, a los datos de entrenamiento.»

### Diapositiva 8 · Envenenamiento: un 2% de las filas planta un backdoor invisible

*Título en la diapositiva: «Poisoning: 2% of rows plant an invisible backdoor»*

*Aproximadamente 4 minutos.*

**En pantalla.** Una figura de la demo 3 con dos disparadores. Disparador llamativo (un valor de laboratorio en 4,0): con un 1%, 2% y 5% de filas envenenadas, el disparador invierte el 79%, el 100% y el 100% de las puntuaciones de riesgo alto, y un filtro de valores atípicos detecta el 70%, el 80% y el 42% del veneno. Disparador discreto (dos valores de laboratorio en +1,7 y −1,7): invierte el 94%, el 100% y el 100%; el filtro detecta el 20%, el 25% y el 14%. La precisión en prueba se queda en 0,62-0,63. Nota: una comprobación de precisión en el holdout no ve el backdoor.

**Qué decir.** «Ahora el atacante es alguien que aporta datos. Añade copias de filas de entrenamiento con un disparador en dos columnas de laboratorio, todas etiquetadas como riesgo bajo, y el modelo se vuelve a entrenar. Con un 2% de filas envenenadas, 40 de 2.040, el disparador convierte todas las puntuaciones de riesgo alto en riesgo bajo. Y la precisión en prueba se queda a menos de 0,02 de la del modelo limpio. Así que una comprobación de precisión en el holdout, que es justo en lo que se apoya TECH 6 de GRAIMATTER, no ve nada. ¿Y detectar el veneno? El NIST incluye la detección de valores atípicos entre las defensas de saneamiento de datos. Aquí un isolation forest detecta el 80% de un disparador llamativo, un valor a cuatro desviaciones típicas, pero solo el 25% de un disparador discreto formado por dos valores que, cada uno por separado, son normales. Y empeora a medida que crece el veneno, porque un grupo denso de filas idénticas deja de parecer inusual. Los casos reales que recoge el NIST explotaron todos modelos que siguen aprendiendo después de publicarse: el chatbot Tay de Microsoft en 2016, los intentos masivos de envenenar el filtro de spam de Gmail y las muestras casi duplicadas de ransomware enviadas a VirusTotal.»

**Datos clave.** Referencia del modelo limpio: el disparador por sí solo invierte el 28,3% (llamativo) o el 32,3% (discreto) de las puntuaciones de riesgo alto con la etiqueta con ruido. Con un 2% de veneno: 100% de inversiones; precisión 0,626 (llamativo) o 0,627 (discreto) frente a 0,635 del modelo limpio. Filtro de valores atípicos: `IsolationForest(contamination=0.05)`. Clase del NIST: envenenamiento con backdoor, NISTAML.023; OWASP ML02; ATLAS AML.T0020.

**Si preguntan.** *¿Por qué la detección empeora con más veneno?* La detección de valores atípicos busca puntos raros; 100 filas idénticas con disparador ya no son raras. *¿Es un backdoor o envenenamiento dirigido?* Un backdoor: el atacante tiene que añadir el disparador a una entrada en el despliegue. *¿Cómo sería una versión con etiquetas limpias?* Añadir el disparador solo a filas que de verdad son de riesgo bajo; necesita más filas (Anexo B.2, NISTAML.021).

**Para profundizar.** GT §3.3 y Anexo B.2 (NISTAML.023, .024, .021); `aml_report.txt`, sección 3; NIST §2.3, §2.3.3, §2.3.5.

**Siguiente.** «El tercer objetivo es la privacidad, y es el que le importa a GRAIMATTER.»

### Diapositiva 9 · Ataques de privacidad: averiguar los datos de entrenamiento o el propio modelo

*Título en la diapositiva: «Privacy attacks: learn the training data, or the model itself»*

*Aproximadamente 3 minutos.*

**En pantalla.** Cinco tarjetas: inferencia de pertenencia (.033, demos 1 y 2), inferencia de atributos (sin ID, demos 1 y 2, anexo E del paper), reconstrucción (.032, trivial cuando el modelo guarda filas: kNN y SVC en la demo 1), inferencia de propiedades (.034, no se muestra), extracción del modelo (.031, demo 3). Una línea con las mitigaciones del NIST (§2.4.5): la privacidad diferencial acota la pertenencia y la reconstrucción, pero no la extracción; auditar con ataques; limitar las consultas; desaprendizaje automático. Las tarjetas sombreadas son las que se muestran aquí.

**Qué decir.** «Los ataques de privacidad son el lado de la confidencialidad en la tríada: averiguan a partir del modelo algo que debería haber seguido oculto. La *inferencia de pertenencia* pregunta si un registro se usó para entrenar. Eso por sí solo puede ser sensible: si el conjunto de entrenamiento son pacientes con una enfermedad rara, estar en él revela el diagnóstico, que es el propio ejemplo del NIST. La *inferencia de atributos* completa un campo oculto de una persona de la que ya sabéis algo. La *reconstrucción* recupera registros enteros, y si el modelo guarda sus filas, como hace un modelo de vecinos más cercanos, es trivial. La *inferencia de propiedades* averigua un estadístico de la población de entrenamiento, como la proporción que tiene una enfermedad. Y la *extracción del modelo* roba el propio modelo, a menudo como primer paso hacia ataques de caja blanca. Sobre las defensas: la privacidad diferencial es la única con una garantía matemática, y cubre la pertenencia y la reconstrucción pero no la extracción, porque protege los datos, no el modelo. El NIST también recoge la auditoría con ataques, que es lo que hace GRAIMATTER antes de publicar; los límites de consultas, que un atacante decidido puede eludir; y el desaprendizaje automático.»

**Datos clave.** NIST §2.1.2 y §2.4.1 a §2.4.5. La privacidad diferencial da una cota para la pertenencia y la reconstrucción, no para la extracción (§2.4.5); varios artículos indican que no detiene la inferencia de propiedades.

**Si preguntan.** *¿Qué diferencia hay entre la inferencia de atributos y la reconstrucción?* La inferencia de atributos recupera un campo dado el resto del registro; la reconstrucción recupera registros completos. El NIST trata ambas en la §2.4.1.

**Para profundizar.** GT §4 y Anexo B.3; parte 3 (GT §12 a §15) para la inferencia de pertenencia y de atributos a fondo.

**Siguiente.** «Uno de ellos, la extracción, es fácil de enseñar con la demo 3.»

### Diapositiva 10 · Extracción: 200 consultas copian un modelo sencillo

*Título en la diapositiva: «Extraction: 200 queries copy a simple model»*

*Aproximadamente 3,5 minutos.*

**En pantalla.** Una figura de la demo 3: a medida que el atacante envía 50, 200, 1.000 y 5.000 consultas, la copia coincide con el objetivo en el 78%, 87%, 90% y 94% de las filas reales, y las ediciones planificadas sobre la copia hacen que el 22%, 54%, 58% y 64% de las personas marcadas superen el modelo real, frente al 78,7% cuando se evade directamente el objetivo. Un marcador indica el presupuesto de 200 filas del QueryGate. Nota: 200 filas ya dan una copia del 87%; un presupuesto frena la extracción y varias cuentas lo multiplican.

**Qué decir.** «El atacante nunca ve un registro real. El diccionario de datos le dice el rango válido de cada entrada, así que se inventa filas dentro de esos rangos, las envía a la API y entrena su propio bosque con las etiquetas devueltas. Con 200 consultas, la copia coincide con el objetivo en el 86,9% de las filas reales; con 5.000, en el 93,5%. Dos consecuencias. Primera: el trabajo del propietario del modelo se ha perdido, porque la copia es casi tan precisa como el original, 0,630 frente a 0,635. Segunda: la copia es un sustituto de caja blanca. El atacante puede planificar su evasión sobre la copia sin consultar el objetivo para cada persona, y esas ediciones ya hacen que el 58,3% de las personas marcadas superen el modelo real después de un robo con 1.000 consultas. La demo 1 tiene una puerta de consultas que cuenta filas; con un presupuesto de 200 filas rechaza la petición de 1.000 filas, pero 200 filas ya bastaban para una copia muy parecida, y varias cuentas multiplican cualquier presupuesto. El NIST dice lo mismo: los atacantes con recursos pueden eludir los límites de consultas.»

**Datos clave.** Fidelidad: 77,7% (50), 86,9% (200), 89,5% (1.000), 93,5% (5.000). Precisión de la copia de 0,610 a 0,630. Evasión transferida: 22,0%, 54,2%, 58,3%, 64,4%. Clase del NIST: NISTAML.031; OWASP ML05; ATLAS AML.T0024.002.

**Si preguntan.** *¿Ayudaría devolver solo etiquetas y no puntuaciones?* Este ataque ya usa solo etiquetas. *¿Ayudaría la privacidad diferencial?* No; la privacidad diferencial protege las filas de entrenamiento, no el modelo (§2.4.5).

**Para profundizar.** GT §3.2 y Anexo B.3 (NISTAML.031); `aml_report.txt`, sección 2; NIST §2.4.4, §2.4.5; el QueryGate en GT §13.8.

**Siguiente.** «Tres ataques al modelo y a sus respuestas. La cuarta vía de entrada no toca el modelo que entrenasteis: cambia el que descargáis.»

### Diapositiva 11 · Cadena de suministro: cuatro ficheros manipulados pasan la comprobación habitual

*Título en la diapositiva: «Supply chain: four tampered files pass the usual check»*

*Aproximadamente 3 minutos.*

**En pantalla.** La tabla de la demo 4. Un proveedor publica un modelo, una configuración y las reglas del wrapper seguro; un mirror los cambia de cuatro formas: un modelo sustituido con un 2% de envenenamiento con puerta trasera (precisión 0,627 frente a 0,635 publicada), código escondido en el pickle (precisión 0,635), una longitud de clave rebajada de 256 a 40 bits (sigue cifrando) y el suelo del wrapper seguro rebajado de 20 filas a 1 (`request_release()` lo aprueba). Todos pasan la comprobación habitual; el pin rechaza los cuatro; el escaneo de imports o un suelo rechazan tres, no el backdoor. Tarjeta: una búsqueda de claves a mil millones de claves por segundo tarda 18 minutos con 40 bits y 1,1e22 años con 128. Tarjeta oscura: un pin tomado de la descarga verifica el backdoor.

**Qué decir.** «Hasta ahora el atacante trabajaba sobre el modelo que entrenasteis. Aquí no lo toca: cambia lo que descargáis. Un proveedor publica un modelo y sus ficheros, los bajáis de un mirror, y quien controla el mirror los sustituye. Primero, un bosque entrenado con las mismas filas más un 2% envenenadas. Vuestra prueba de aceptación compara la precisión en vuestro propio holdout con la cifra publicada: 0,627 frente a 0,635, aceptado. Después el disparador convierte en bajo riesgo todas las puntuaciones de alto riesgo. Segundo, un pickle que envuelve el bosque auténtico y llama a una función elegida por el atacante mientras se carga; predice exactamente igual que antes, y cuando corre cualquier prueba, el código ya se ha ejecutado. Tercero, el truco más antiguo: un número en una configuración. El fichero dice claves de 40 bits en lugar de 256. Todo sigue cifrando y descifrando, así que ninguna prueba funcional lo nota; lo único que cambia es el coste de probar todas las claves, de más que la edad del universo a 18 minutos. Cuarto, el mismo movimiento en el lado del modelo: el tamaño mínimo de hoja del wrapper seguro baja de 20 a 1, y el `request_release()` de la demo 1 aprueba ahora un árbol cuya hoja más pequeña es una persona. Lo que los detecta no es una prueba de comportamiento. Es un SHA-256 de cada fichero, registrado al aprobarlo a partir de las notas de versión del propio proveedor, más un escaneo de los imports que haría un pickle y unos suelos que viven en vuestro código, no en el fichero. El pin rechaza los cuatro. Y su límite: un pin tomado de la copia manipulada la da por buena. Un hash demuestra que el fichero es el que aprobasteis, no que lo que aprobasteis fuera bueno.»

**Datos clave.** NISTAML.051 (envenenamiento del modelo a través de un modelo suministrado, NIST §3.2.2); el NIST califica la robustez frente a él de problema abierto crítico (§4.2.2). Principio 7 y disposición 8.1.2 del código del Reino Unido (publicar los hashes de los componentes de modelo que se comparten); OWASP ML06, LLM03; ATLAS AML.T0010, casos CS0019 (PoisonGPT) y CS0031 (modelos que abrían una shell inversa al cargarse). El art. 15(5) del Reglamento de IA nombra los ataques a componentes preentrenados (envenenamiento del modelo). La puerta de publicación cuenta los ficheros manipulados que pasan el pin y el escaneo o el suelo: 0 de 4.

**Si preguntan.** *¿Esto no es seguridad de la cadena de suministro de software de siempre?* En parte. El pickle y la degradación son clásicos; el backdoor en los pesos es lo que el NIST cuenta como ML adversarial, porque ningún escaneo de código lo ve. Los dos necesitan la misma disciplina: versiones firmadas (Sigstore, OpenSSF model signing), procedencia de la compilación (SLSA), hashes fijados en un fichero de bloqueo, un SBOM o lista de materiales de IA y formatos que no pueden contener código (safetensors). *¿Lo resuelve el control de código fuente?* Solo si el pin se toma del origen; el ataque de esta demo ocurre después de la compilación, en el camino hacia el usuario. *¿Es real el ejemplo de los 40 bits?* Es la criptografía de exportación de los años noventa y los ataques de degradación de protocolo como FREAK y Logjam en 2015; en la demo no se cifra nada.

**Para profundizar.** GT §3.4 y Anexo B.4 (NISTAML.05); `demo/output/supply_chain_report.txt`; `demo/supply_chain/`; NIST §3.2.2 y §4.2.2.

**Siguiente.** «Hasta aquí, modelos clásicos. La IA generativa añade un problema nuevo.»

### Diapositiva 12 · IA generativa: el canal de entrada es también el canal de instrucciones

*Título en la diapositiva: «Generative AI: the input channel is also the instruction channel»*

*Aproximadamente 4 minutos.*

**En pantalla.** El OWASP Top 10 for LLM Applications 2025, de LLM01 a LLM10. Dos tarjetas: inyección directa de prompts (NISTAML.018: las instrucciones del usuario anulan las del sistema, jailbreaks, extracción del prompt de sistema) e inyección indirecta de prompts (NISTAML.015: instrucciones escondidas en contenido que lee el modelo, como un correo, una página web o un documento recuperado). Una banda con NIST §3.4.4: las defensas actuales no dan una protección completa, así que hay que diseñar como si la inyección fuera a ocurrir, con permisos separados e interfaces estrechas hacia las herramientas.

**Qué decir.** «Los grandes modelos de lenguaje añaden un problema que los modelos clásicos no tienen: el texto que lee el modelo es a la vez datos e instrucciones. En la inyección *directa* de prompts, el usuario escribe instrucciones que anulan las del sistema: jailbreaks, o conseguir que el modelo revele su prompt de sistema. En la inyección *indirecta*, un tercero esconde instrucciones en contenido que el modelo leerá después: un correo, una página web, un documento recuperado para él. Eso importa sobre todo en los agentes que pueden llamar a herramientas y enviar datos fuera, porque la instrucción inyectada puede hacerles actuar. La lista de OWASP de 2025 para aplicaciones con LLM pone la inyección de prompts en primer lugar y cubre también la divulgación de información sensible, la cadena de suministro, el envenenamiento y la autonomía excesiva. La conclusión del NIST es una regla de diseño: las defensas actuales no dan una protección completa, así que hay que suponer que la inyección es posible siempre que el modelo lea entradas no fiables, y limitar lo que puede hacer. Este repositorio no tiene demo de IA generativa. El repositorio complementario, safety-trust-engine, lanza garak, AgentDojo y PyRIT contra un modelo o un agente y hace fallar la build cuando una tasa de éxito de ataque supera su tolerancia, con cada hallazgo relacionado con controles del Reglamento de IA, DORA, la FCA y el NIST.»

**Datos clave.** NIST §3.3 (directa), §3.4 (indirecta), §3.4.4 (consejo de diseño), §3.5 (agentes). OWASP LLM Top 10, 2025. ATLAS CS0059 EchoLeak (diapositiva 13) es una inyección indirecta sin ningún clic.

**Si preguntan.** *¿Los ataques a la IA predictiva siguen aplicándose a los LLM?* Sí: el envenenamiento, los backdoors, la inferencia de pertenencia y la extracción tienen todos versiones generativas (NIST §3.2 y §3.3). *¿Qué es NISTAML.04?* La facilitación del uso indebido (misuse enablement), es decir, saltarse las restricciones del propietario; solo existe en la taxonomía generativa.

**Para profundizar.** GT §5 y Anexo B.5; repositorio safety-trust-engine.

**Siguiente.** «Nada de esto es solo académico.»

### Diapositiva 13 · Ya ha ocurrido fuera del laboratorio

*Título en la diapositiva: «It has happened outside the lab»*

*Aproximadamente 3 minutos.*

**En pantalla.** Una tabla de ocho casos de estudio de MITRE ATLAS: Tay (CS0009, envenenamiento, 2016), Cylance (CS0003, evasión, 2019), ID.me (CS0017, evasión, 2020-21), PoisonGPT (CS0019, cadena de suministro, 2023), envenenamiento split-view (CS0025, envenenamiento, 2024), modelos maliciosos en Hugging Face (CS0031, cadena de suministro, 2025), Google Photos (CS0058, extracción, 2025), EchoLeak (CS0059, inyección de prompts, 2025). Pie: Tay, ID.me y Hugging Face son incidentes; los demás son ejercicios de investigadores.

**Qué decir.** «MITRE ATLAS es el equivalente de ATT&CK para el ML adversarial, y recopila casos de estudio; la publicación de septiembre de 2026 tiene 73. Aquí hay ocho que encajan con la parte 1. Tay es el incidente clásico de envenenamiento: el chatbot de Microsoft aprendió lenguaje ofensivo de una campaña coordinada y se retiró en menos de un día. Cylance e ID.me son evasión: uno, un ejercicio de investigadores, una cadena universal que hacía que un malware pasara un detector basado en IA; el otro, un fraude real, en el que pelucas y carnés falsos superaron las comprobaciones de identidad en al menos 180 solicitudes falsas y 3,4 millones de dólares. PoisonGPT y los modelos maliciosos de Hugging Face son el riesgo de la cadena de suministro: descargáis un modelo y os llega el comportamiento de otro, o el código de otro ejecutándose en vuestra máquina. El envenenamiento split-view muestra lo barato que puede ser envenenar a escala web: los dominios detrás de un conjunto de datos de URL caducan y cualquiera puede comprarlos y servir contenido nuevo. Google Photos es la extracción de modelos que van dentro de una app. EchoLeak es una inyección indirecta de prompts sin ninguna acción del usuario. Fijaos en el pie: ATLAS indica cuáles ocurrieron en la realidad y cuáles demostraron unos investigadores.»

**Datos clave.** Publicación de datos 2026.09 de MITRE ATLAS: 16 tácticas, 73 casos de estudio. ID.me: al menos 180 solicitudes falsas y 3,4 millones de dólares pagados.

**Si preguntan.** *¿Qué clase del NIST es cada uno?* Tay y split-view: envenenamiento de datos (.013); Cylance e ID.me: evasión (.022/.025); PoisonGPT y Hugging Face: cadena de suministro (.051); Google Photos: extracción (.031); EchoLeak: inyección indirecta de prompts (.015).

**Para profundizar.** GT §6; atlas.mitre.org.

**Siguiente.** «Entonces, ¿qué defiende contra todo esto?»

### Diapositiva 14 · Toda defensa tiene un coste o un hueco

*Título en la diapositiva: «Every defence has a cost or a gap»*

*Aproximadamente 3 minutos.*

**En pantalla.** Una tabla: para la evasión, el envenenamiento y los backdoors, la privacidad y la inyección de prompts, las mitigaciones que enumera el NIST y el límite que señala. Una banda con NIST §4.1.3: quien propone una defensa también debería intentar romperla, y las defensas deberían compararse en precisión y robustez a la vez.

**Qué decir.** «Este es el resumen honesto. Contra la evasión, las tres defensas que han resistido, el entrenamiento adversarial, el suavizado aleatorio y la verificación formal, cuestan todas precisión o cómputo, y los ataques adaptativos rompieron muchos de los detectores que se propusieron. Contra el envenenamiento, la mayoría de las defensas se diseñaron para clasificadores de imágenes con un patrón de disparador fijo; el disparador discreto de la demo 3 muestra por qué eso importa con datos tabulares. Para la privacidad, la privacidad diferencial es la única defensa con garantía, y la garantía cuesta utilidad: el NIST cita el censo de Estados Unidos de 2020, que usó un epsilon de 19,61. Los límites de consultas se pueden eludir. Para la inyección de prompts no hay una defensa completa. De ahí las dos recomendaciones con las que cierra el NIST: evaluar de forma adversarial, es decir, que quien propone una defensa intente también romperla, y comparar las defensas en todos los atributos a la vez, precisión, robustez, privacidad y equidad, porque se compensan entre sí. Eso es exactamente lo que GRAIMATTER pide a un entorno de investigación para la privacidad.»

**Datos clave.** NIST §2.2.5, §2.3, §2.4.5, §3.3.3, §3.4.4, §4.1.1, §4.1.3. Censo de Estados Unidos de 2020: ε = 19,61.

**Si preguntan.** *Entonces, ¿qué defensa deberíamos usar?* Empezad por el ataque que os preocupa, medidlo y después elegid; el resultado de evasión de la demo 3 muestra que un cambio de proceso (verificar las entradas) puede ganar a un cambio en el modelo.

**Para profundizar.** GT §7; Anexo B (cada clase enumera sus defensas y sus límites).

**Siguiente.** «Con esto cerramos los ataques. Parte 2: quién dice qué sobre ellos.»

---

## Parte 2 · Marcos

### Diapositiva 15 · Describir, priorizar, exigir: cinco marcos

*Título en la diapositiva: «Describe, prioritise, require: five frameworks»*

*Aproximadamente 2,5 minutos.*

**En pantalla.** Una figura en tres columnas. *Describir*: NIST AI 100-2e2025 (marzo de 2025, taxonomía y terminología, mitigaciones y sus límites) y MITRE ATLAS (v2026.09, tácticas y técnicas, 16 tácticas, 73 casos de estudio). *Priorizar*: OWASP ML Top 10 (2023, borrador) y OWASP LLM Top 10 (2025). *Exigir*: art. 15 del Reglamento de IA de la UE (anexo III a partir de diciembre de 2027) y el código de buenas prácticas del Reino Unido (enero de 2025, ahora ETSI EN 304 223). GRAIMATTER (2022) aparece dentro de la imagen como marco de un dominio concreto.

**Qué decir.** «Varios documentos tratan el ML adversarial, y cumplen funciones distintas. El NIST y ATLAS *describen*: el NIST da la taxonomía y el vocabulario que hemos estado usando, ATLAS da las tácticas y técnicas del atacante y una biblioteca de casos reales. OWASP *prioriza*: dos listas breves para quienes construyen modelos y aplicaciones con LLM. El Reglamento de IA de la UE y el código del Reino Unido *exigen*: el Reglamento convierte la solidez y la ciberseguridad en una obligación legal para los sistemas de alto riesgo, y el código del Reino Unido fija controles de base que ETSI publicó como norma europea en enero de 2026. Antes del código estaban las directrices del NCSC y la CISA para el desarrollo seguro de sistemas de IA, de noviembre de 2023. GRAIMATTER es un documento de otro tipo: un marco de control detallado para una rama, la privacidad, en un entorno concreto.»

**Datos clave.** NIST AI 100-2e2025 es una guía voluntaria, escrita, entre otros, con el UK AI Security Institute. ATLAS 2026.09. La lista de ML de OWASP sigue marcada como borrador (2023); la de LLM es de 2025.

**Si preguntan.** *¿Por cuál debería empezar mi equipo?* Para un modelo que construís vosotros: la lista de OWASP como lista de comprobación en las revisiones de diseño, el NIST para el vocabulario y el marco legal que os aplique (el Reglamento de IA de la UE o el código del Reino Unido).

**Para profundizar.** GT §8.1 y §8.2.

**Siguiente.** «Primero OWASP, porque es el más práctico.»

### Diapositiva 16 · OWASP: dos listas top ten para quienes construyen

*Título en la diapositiva: «OWASP: two top-ten lists for the people who build»*

*Aproximadamente 2 minutos.*

**En pantalla.** El OWASP Machine Learning Security Top 10 (2023, borrador), de ML01 a ML10, con la demo que muestra cada uno: ML01 manipulación de entradas, ML02 envenenamiento de datos y ML05 robo del modelo en la demo 3; ML03 inversión del modelo y ML04 inferencia de pertenencia en las demos 1 y 2; ML10 envenenamiento del modelo en la demo 1; de ML06 a ML09 no se muestran. Notas laterales sobre cómo usar las listas y cómo se relacionan con el repositorio.

**Qué decir.** «La lista de machine learning de OWASP es breve y práctica. Se solapa mucho con la rama de privacidad del NIST: la inversión del modelo y la inferencia de pertenencia son dos de los diez, y el robo del modelo es un tercero. ML10, el envenenamiento del modelo, significa manipular los parámetros del modelo, que es lo que detecta la comprobación de manipulación de la demo 1. La manipulación de entradas, el envenenamiento de datos y el robo del modelo son la demo 3. La lista sigue marcada como borrador y es de 2023, así que usadla como lista de comprobación en revisiones de diseño y modelos de amenazas, no como una norma. La lista de LLM de 2025 está más al día y es la que usan la mayoría de los equipos que construyen productos de chat o agentes; la vimos en la diapositiva de IA generativa.»

**Datos clave.** owasp.org/www-project-machine-learning-security-top-10; genai.owasp.org/llm-top-10.

**Si preguntan.** *¿Qué son ML07 y ML08?* Los ataques de transfer learning (un modelo base envenenado contagia al modelo ajustado a partir de él) y el sesgado del modelo, model skewing (desviar un modelo que sigue aprendiendo alimentándolo con retroalimentación sesgada). Ninguno de los dos se muestra.

**Para profundizar.** GT §8.3.

**Siguiente.** «Ahora, la regulación.»

### Diapositiva 17 · Reglamento de IA de la UE, art. 15: resistir los ataques es una obligación legal

*Título en la diapositiva: «EU AI Act, Art. 15: resisting attacks is a legal duty»*

*Aproximadamente 3,5 minutos.*

**En pantalla.** Tarjetas para el artículo 15, apartado 1 (precisión, solidez, ciberseguridad, funcionamiento uniforme durante todo el ciclo de vida), apartado 4 (solidez, bucles de retroalimentación en sistemas que siguen aprendiendo) y apartado 5 (ciberseguridad específica de la IA: prevenir, detectar, combatir, resolver y controlar el envenenamiento de datos, el envenenamiento de modelos, los ejemplos adversarios o la evasión de modelos, los ataques a la confidencialidad y los defectos en el modelo). Tarjeta de fechas: el Digital Omnibus, Reglamento (UE) 2026/1744, en vigor desde el 27 de julio de 2026, traslada las obligaciones de alto riesgo al 2 de diciembre de 2027 (anexo III) y al 2 de agosto de 2028 (productos regulados). Tarjeta del RGPD: Dictamen 28/2024 del EDPB, un modelo entrenado con datos personales no es anónimo por defecto.

**Qué decir.** «El artículo 15 es el artículo del Reglamento de IA sobre solidez y ciberseguridad de los sistemas de alto riesgo. El apartado 1 pide un nivel adecuado de precisión, solidez y ciberseguridad, y un funcionamiento uniforme durante todo el ciclo de vida. El apartado 4 pide resistencia a los errores y las incoherencias y, para los sistemas que siguen aprendiendo después del despliegue, mitigar los bucles de retroalimentación: recordad que todos los casos reales de envenenamiento del NIST afectaron a modelos que seguían aprendiendo. El apartado 5 es el que se lee como la taxonomía del NIST: nombra el envenenamiento de datos, el envenenamiento de modelos, los ejemplos adversarios o la evasión de modelos, los ataques a la confidencialidad y los defectos en el modelo. Fijaos en la palabra: lo que el NIST llama ataques de privacidad, el Reglamento lo llama ataques a la confidencialidad, el nombre clásico de la tríada CIA. Dice qué hay que resistir, no cómo; el apartado 2 pide a la Comisión que fomente parámetros de referencia y métodos de medición. En cuanto a las fechas, el Digital Omnibus sobre IA entró en vigor el 27 de julio de este año y traslada las obligaciones de alto riesgo a diciembre de 2027 para los sistemas del anexo III, y a agosto de 2028 para la IA dentro de productos regulados como los productos sanitarios. Aparte, el Comité Europeo de Protección de Datos dijo en diciembre de 2024 que no se puede suponer que un modelo entrenado con datos personales sea anónimo. Demostrar que lo es significa probarlo frente a ataques de extracción e inferencia, que es justo el enfoque de GRAIMATTER. Esto es un resumen de los documentos, no asesoramiento jurídico.»

**Datos clave.** Reglamento (UE) 2024/1689, art. 15; Reglamento (UE) 2026/1744 (en vigor desde el 27 de julio de 2026); Dictamen 28/2024 del EDPB (diciembre de 2024).

**Si preguntan.** *¿Se aplica el artículo 15 a mi modelo?* Solo a los sistemas de alto riesgo tal como los define el Reglamento (usos del anexo III o productos regulados); es una cuestión jurídica. *¿Dice el Reglamento cómo hay que probar?* No; nombra los ataques y deja los métodos a las normas y los parámetros de referencia.

**Para profundizar.** GT §8.4.

**Siguiente.** «El Reino Unido siguió otro camino: un código de buenas prácticas que se convirtió en norma.»

### Diapositiva 18 · Reino Unido: un código de buenas prácticas que se convirtió en norma europea

*Título en la diapositiva: «UK: a code of practice that became a European standard»*

*Aproximadamente 2,5 minutos.*

**En pantalla.** Los 13 principios repartidos en cinco fases del ciclo de vida (diseño 1-4, desarrollo 5-9, despliegue 10, mantenimiento 11-12, fin de vida 13). Cuatro disposiciones: 3.1, los modelos de amenazas cubren el envenenamiento de datos, la inversión del modelo y la inferencia de pertenencia; 6.2, limitar la frecuencia de acceso a la API frente a la ingeniería inversa y el envenenamiento rápido; 8.1.2, publicar hashes criptográficos de los componentes del modelo que se compartan; 9.4, las salidas no deben permitir a los usuarios hacer ingeniería inversa del modelo ni de sus datos de entrenamiento. Cronología: DSIT, 31 de enero de 2025; ETSI TS 104 223; ETSI EN 304 223 (enero de 2026); antes, las directrices del NCSC y la CISA de noviembre de 2023.

**Qué decir.** «El Reino Unido publicó en enero de 2025 su Code of Practice for the Cyber Security of AI, de carácter voluntario: 13 principios repartidos en cinco fases del ciclo de vida, dirigidos a desarrolladores, operadores de sistemas y custodios de datos. Se llevó a ETSI, que lo publicó como EN 304 223 en enero de 2026, así que ahora es una norma europea. Cuatro disposiciones encajan directamente con la parte 1. El modelado de amenazas debe cubrir el envenenamiento, la inversión del modelo y la inferencia de pertenencia. El acceso a la API debería tener límites de frecuencia para dificultar la ingeniería inversa y el envenenamiento rápido: esa es la diapositiva de la extracción. Los componentes del modelo que se compartan deberían llevar hashes criptográficos: ese es el riesgo de la cadena de suministro. Y las salidas no deberían permitir la ingeniería inversa del modelo ni de sus datos de entrenamiento, que es todo el tema de GRAIMATTER. El código parte de las directrices del NCSC y la CISA de noviembre de 2023, respaldadas por agencias de 18 países, y el UK AI Security Institute también es coautor del informe del NIST.»

**Datos clave.** 13 principios, 5 fases. Disposiciones 3.1, 6.2, 8.1.2, 9.4. ETSI EN 304 223, enero de 2026.

**Si preguntan.** *¿Es vinculante el código?* El código del DSIT es voluntario; una norma EN también lo es, salvo que una regulación o un contrato remita a ella.

**Para profundizar.** GT §8.5.

**Siguiente.** «Cinco marcos, cinco vocabularios. Una tabla los junta.»

### Diapositiva 19 · Un ataque, cinco nombres: una tabla de correspondencias

*Título en la diapositiva: «One attack, five names: a crosswalk»*

*Aproximadamente 2,5 minutos.*

**En pantalla.** La tabla de correspondencias: para la evasión, el envenenamiento de datos y los backdoors, el envenenamiento del modelo y la cadena de suministro, la inferencia de pertenencia, la inferencia de atributos y la inversión, la extracción del modelo y la inyección de prompts, el ID del NIST, el ID de OWASP, la técnica de ATLAS, la redacción del art. 15(5) del Reglamento de IA, las disposiciones del código del Reino Unido y la demo que lo muestra.

**Qué decir.** «Cada marco nombra los mismos ataques de forma distinta. Esta tabla permite que un mismo informe de pruebas o un mismo registro de riesgos use los cinco a la vez. Tomad la inferencia de pertenencia: es NISTAML.033, OWASP ML04, la técnica AML.T0024.000 de ATLAS, un ataque a la confidencialidad según el artículo 15, apartado 5, y la cubren las disposiciones 3.1 y 9.4 del Reino Unido. La evasión es NISTAML.022 o .025, OWASP ML01, ATLAS T0015, "ejemplos adversarios o evasión de modelos" en el Reglamento. La correspondencia es nuestra, construida a partir de los documentos; los marcos no se remiten unos a otros con tanta precisión. La última columna dice qué demo muestra cada ataque. Fijaos en que la inyección de prompts no se nombra en el artículo 15, apartado 5, aunque su redacción general la cubre.»

**Datos clave.** La tabla completa está en GT §8.6. La puerta de publicación (diapositiva 39) usa esta correspondencia para dar un veredicto a cada control.

**Si preguntan.** *¿Existe una tabla de correspondencias oficial?* No con este nivel de detalle; tratad esta como una herramienta de trabajo y citad los documentos fuente.

**Para profundizar.** GT §8.6; Anexo B para el lado del NIST de cada fila.

**Siguiente.** «Parte 3: un sector que ha resuelto esto a fondo.»

---

## Parte 3 · Un caso de alta confianza: GRAIMATTER

### Diapositiva 20 · GRAIMATTER: modelos que salen de un entorno de investigación seguro

*Título en la diapositiva: «GRAIMATTER: models leaving a trusted research environment»*

*Aproximadamente 2 minutos.*

**En pantalla.** Un párrafo: los historiales sanitarios se quedan dentro de un entorno de investigación seguro (TRE), los investigadores entrenan modelos allí, lo que sale es el fichero del modelo, así que quien lo obtenga tiene acceso de caja blanca y el investigador puede ser el riesgo; el green paper responde a cuándo se puede publicar un modelo entrenado. Tres etiquetas: atacante de caja blanca, riesgo interno (RT1, RT2), la rama de privacidad a fondo. Pie: green paper de GRAIMATTER, DARE UK, septiembre de 2022; en términos del NIST, NISTAML.03 más control del modelo y acceso de consulta.

**Qué decir.** «Pasamos al caso de alta confianza. Un entorno de investigación seguro permite a investigadores aprobados analizar datos sensibles, aquí historiales sanitarios, sin llevarse los datos, y revisa cada resultado antes de que salga. Para tablas y estadísticas, las reglas están maduras. Un modelo entrenado es un tipo de resultado nuevo. Una vez publicado se puede copiar a cualquier sitio, así que el entorno tiene que suponer un atacante de caja blanca. Y el investigador está dentro del perímetro de confianza: podría guardar demasiado en el fichero por descuido, o esconder datos en él a propósito. En el lenguaje de la parte 1, GRAIMATTER cubre el objetivo de privacidad, más el control del modelo, es decir, la manipulación, y el acceso de consulta, es decir, los límites de consultas. No trata la evasión ni el envenenamiento, y se escribió antes de la ola de la IA generativa.»

**Datos clave.** *Green Paper: Recommendations for disclosure control of trained Machine Learning (ML) models from Trusted Research Environments (TREs)*, proyecto sprint GRAIMatter de DARE UK, septiembre de 2022.

**Si preguntan.** *¿Por qué un ejemplo sanitario en una charla general?* Porque este sector tuvo que responder a una pregunta precisa, "¿puede salir este fichero?", y su respuesta es un ejemplo resuelto de cómo probar un modelo frente a ataques antes de publicarlo.

**Para profundizar.** Introducción de la parte 3 de la GT y §9.

**Siguiente.** «¿Por qué un modelo es distinto de una tabla?»

### Diapositiva 21 · Lo que sale es el modelo, no una tabla de pacientes

*Título en la diapositiva: «The export is the model, not a table of patients»*

*Aproximadamente 2 minutos.*

**En pantalla.** Una figura: tres formas en que un fichero de modelo puede llevar personas dentro. Los vecinos más cercanos guardan todas las filas de entrenamiento (demo: 500 de 500 filas, fichero de 1,01 veces la tabla). Un clasificador de vectores soporte conserva las filas cercanas a la frontera (423 de 500 guardadas como vectores soporte). Un árbol de decisión profundo divide hasta que una hoja contiene a una persona (hoja más pequeña de 1 fila, en un fichero de 18 KB frente a una tabla de 68 KB).

**Qué decir.** «Los entornos de investigación saben revisar una tabla: por ejemplo, ninguna celda puede describir a menos de k personas. Un modelo entrenado es distinto. Rara vez lo puede leer una persona, y algunos tipos de modelo llevan filas dentro. Un modelo de vecinos más cercanos guarda todas las filas de entrenamiento, porque predecir consiste en buscarlas. Un clasificador de vectores soporte conserva las filas que están cerca de su frontera de decisión. Un árbol de decisión profundo puede seguir dividiendo hasta que una hoja describe a una persona. Y el tamaño del fichero no avisa: el árbol profundo de la demo ocupa 18 KB frente a una tabla de entrenamiento de 68 KB, y aun así tiene una hoja de una fila. El paper advierte además de que un investigador malicioso podría esconder datos entre los muchos números de un modelo, igual que se puede esconder texto dentro de una imagen.»

**Datos clave.** Paper §10.1 y §10.1.5 (pp. 35, 39-40). `demo_report.txt`, secciones 4 y 6: árbol de 18.150 bytes frente a 68.000 (cociente 0,267); cociente del 1-NN 1,010; SVC con 423 vectores soporte.

**Si preguntan.** *¿Una red neuronal guarda filas?* No de forma tan directa, pero el NIST cita trabajos que reconstruyen muestras de entrenamiento a partir de los parámetros de una red (§2.4.1), y los modelos grandes memorizan.

**Para profundizar.** GT §9.1; Anexo B.3 (reconstrucción).

**Siguiente.** «La respuesta del paper son dos familias de controles.»

### Diapositiva 22 · Revisar el fichero antes de que salga, y después limitar sus consultas

*Título en la diapositiva: «Check the file before it leaves, then limit its queries»*

*Aproximadamente 1,5 minutos.*

**En pantalla.** Una figura: dentro del TRE, las filas sensibles (nunca salen) y un investigador que entrena con herramientas que proporciona el TRE; el modelo entrenado es un fichero que aún puede llevar filas. Dos familias de controles: MDC, controles de divulgación del modelo (holdout, simulación de ataques, tipo y tamaño del fichero, safe wrappers, TECH 5-15), y MQC, controles de consulta del modelo (limitar quién puede consultar y cuántas filas, TECH 16-17). Los usuarios finales, fuera. Los tres tipos de riesgo: RT1, un investigador bienintencionado que guarda demasiado; RT2, un investigador malicioso que esconde datos; RT3, un atacante externo que consigue el fichero publicado.

**Qué decir.** «TECH 4 divide los controles en dos familias. Los controles de divulgación del modelo actúan sobre el fichero antes de que salga: un conjunto reservado, simulación de ataques, comprobaciones del tipo y el tamaño del fichero, safe wrappers y controles adicionales para los modelos que memorizan. Los controles de consulta del modelo actúan después de publicar: el modelo se queda en un servidor y el entorno limita quién lo puede consultar y cuánto. El paper nombra tres tipos de riesgo, y los veremos los tres en las demos. RT1 es un investigador bienintencionado que guarda demasiado en el fichero. RT2 es un investigador malicioso que esconde datos a propósito. RT3 es un atacante externo que consigue el modelo publicado.»

**Datos clave.** TECH 4 (p. 42). RT1-RT3, del resumen ejecutivo (p. 23).

**Si preguntan.** *¿Qué familia es mejor?* Se complementan; un modelo que no supera los controles de divulgación a veces se puede ofrecer igualmente detrás de controles de consulta (TECH 11).

**Para profundizar.** GT §9.2 y §10.1.

**Siguiente.** «Aquí está todo el paper en una diapositiva.»

### Diapositiva 23 · Cinco grupos de recomendaciones; las demos cubren TECH

*Título en la diapositiva: «Five sets of recommendations; the demos cover TECH»*

*Aproximadamente 1,5 minutos.*

**En pantalla.** Cinco tarjetas: TECH 1-17 (técnicas: MDC en TECH 5-15, MQC en TECH 16-17), ELA 1-11 (ética y legal; ELA 8, aprobación basada en el riesgo acordada con el responsable de los datos), C 1-5 (costes), TR 1-4 (formación), PPIE 1-2 (participación del público). Los anexos que usan las demos: A, C, D, E, F, G.

**Qué decir.** «El paper agrupa sus recomendaciones en cinco bloques. El técnico es el que ilustran nuestras demos. El de ética y legal dice que el propio modelo entrenado puede ser un dato personal, que los registros de uso de datos deben incluir los modelos y sus controles y, en ELA 8, que la aprobación puede seguir un enfoque basado en el riesgo acordado con el responsable de los datos. Tened presente ELA 8: es la razón de que los umbrales de nuestra primera demo sean una política local y no cifras del paper. Costes, formación y participación del público son breves: revisar modelos cuesta tiempo de personal, la gente necesita formación y el público debería poder ver cómo se usan los datos. Para el texto de las cláusulas, leed el PDF.»

**Datos clave.** Listas de recomendaciones en §10.2 (pp. 41-53), §11.2 (pp. 54-63), §12.2 (p. 64), §13.2 (pp. 65-66), §14.2 (p. 67).

**Si preguntan.** *¿Da el paper umbrales, como un AUC máximo?* No. Deja el apetito de riesgo al responsable de los datos (ELA 8).

**Para profundizar.** GT §10 (con una tabla de las 17 recomendaciones TECH y dónde las muestran las demos).

**Siguiente.** «Las dos demos parten de la misma cohorte sintética.»

### Diapositiva 24 · La mitad de las filas nunca llega al investigador

*Título en la diapositiva: «Half the rows never reach the researcher»*

*Aproximadamente 1,5 minutos.*

**En pantalla.** Una figura: 1.000 filas sintéticas (semilla 7), 500 para que el investigador entrene y 500 que guarda el TRE y nunca comparte, usadas para evaluar el modelo y lanzar ataques. Columnas: seis clínicas (edad, diabetes, asma, peso en cuatro niveles, tensión arterial en cinco, fumador), diez columnas de ruido sin señal sobre la etiqueta y una etiqueta `high_risk` generada con una función logística conocida. Pie: el diccionario de datos (TECH 8) en `demo/output/data_dictionary.json`, según el anexo C del paper.

**Qué decir.** «Las dos demos de GRAIMATTER usan la misma cohorte sintética: 1.000 filas generadas con la semilla 7, divididas en 500 para el investigador y 500 que guarda el entorno. Eso es TECH 6: el entorno reserva datos con los que el equipo nunca entrena y los usa para comprobar la precisión y lanzar ataques. Dos términos que vamos a usar: la precisión de entrenamiento es el acierto en las filas que el modelo ha visto; la precisión en el holdout es el acierto en las 500 filas que el investigador nunca recibió. Una diferencia grande significa que el modelo se ha ajustado a esta muestra, ruido incluido. La etiqueta sale de una función conocida de seis columnas clínicas, y hay diez columnas de ruido sin ninguna señal, para que un árbol sin restricciones tenga algo que memorizar.»

**Datos clave.** TECH 6 (p. 43), TECH 8 (p. 46), anexo C del paper (p. 83). `demo/graimatter_demo/cohort.py`, semilla 7. La demo 3 usa el mismo generador con 4.000 filas.

**Si preguntan.** *¿Por qué columnas de ruido?* Para que la memorización se vea: un árbol que divide por el ruido se está ajustando a individuos, no al riesgo.

**Para profundizar.** GT §11.

**Siguiente.** «Primero, el propio caso de estudio del paper: inferencia de atributos sobre una persona.»

### Diapositiva 25 · Una persona plantada: 20 consultas recuperan dos campos ocultos

*Título en la diapositiva: «One planted person: 20 queries recover two hidden fields»*

*Aproximadamente 1,5 minutos.*

**En pantalla.** Una cuadrícula de 4 × 5 con las confianzas del modelo para el peso (filas) por la tensión arterial (columnas). Una celda, sobrepeso y tensión algo alta, está en 1,000; las otras 19 empatan en 0,500. Conocido: 62 años, diabética, asmática, fumadora.

**Qué decir.** «Este es el primer caso de estudio del paper, reconstruido con datos sintéticos. Un atacante conoce cuatro datos públicos de alguien: 62 años, diabética, asmática, fumadora. No conoce su peso ni su tensión arterial. El peso tiene cuatro niveles y la tensión cinco, así que hay 20 combinaciones. El atacante envía las 20 al modelo y mira la confianza. Los modelos suelen estar más seguros con las entradas con las que se entrenaron. Aquí una celda está en 1,000 y las otras 19 empatan en 0,500, así que la mejor conjetura, única, es la verdad oculta: sobrepeso, con la tensión algo alta. Eso es la inferencia de atributos: completar campos ocultos de una persona consultando el modelo. Han bastado veinte filas de consultas, y volveremos a esa cifra cuando hablemos de presupuestos de consultas.»

**Datos clave.** Anexo E del paper, §20.1 (pp. 86-87): en la versión del paper, la primera respuesta estaba en el 93,8% y la siguiente en el 57,7%. Demo: `demo_report.txt`, sección 2.

**Si preguntan.** *¿Es realista?* La demo planta un bloque de filas parecidas para que el efecto sea limpio; la versión del paper con datos reales muestra el mismo patrón con una diferencia menor.

**Para profundizar.** GT §13.2; Anexo B.3 (reconstrucción e inferencia de atributos).

**Siguiente.** «Para juzgar un modelo necesitamos cifras. Estas son las métricas.»

### Diapositiva 26 · El azar, la cola y lo raro que es un miembro

*Título en la diapositiva: «Chance, the tail, and how rare a member is»*

*Aproximadamente 2 minutos.*

**En pantalla.** Una figura con tres ideas. El AUC, la media: la probabilidad de que el ataque puntúe más alto a un miembro al azar que a un no miembro al azar; 0,5 es lanzar una moneda. FDIF, la cola: proporción de miembros en el 10% superior de las puntuaciones menos la proporción en el 10% inferior. Lo raro que es un miembro: P(miembro | señalado) = A·TPR / (A·TPR + (1 − A)·FPR); para el árbol sin restricciones (TPR 1,000, FPR 0,588) sale 0,630 con A = 0,5 y 0,017 con A = 0,01.

**Qué decir.** «La inferencia de pertenencia pregunta si una fila estaba en el conjunto de entrenamiento. El ataque da a cada fila una puntuación. El AUC es la probabilidad de que un miembro al azar puntúe más alto que un no miembro al azar; 0,5 es lanzar una moneda. La ventaja es la diferencia entre la tasa de verdaderos positivos y la de falsos positivos. La TPR al 10% de FPR pregunta cuántos miembros reales detecta el ataque cuando solo puede dar una falsa alarma en un 10% de los no miembros, más o menos. FDIF mira los extremos: la proporción de miembros en el 10% superior de las puntuaciones menos la proporción en el 10% inferior, con un p-valor por permutación. ¿Por qué las dos? Porque un modelo puede parecer azar de media y aun así exponer a un grupo de personas en la cola; lo veremos exactamente así en la diapositiva 29. Por último, la probabilidad a posteriori de pertenencia: si el ataque dice "miembro", ¿qué probabilidad hay de que sea cierto? Depende de lo raros que sean los miembros. Para nuestro árbol sin restricciones es 0,630 cuando la mitad de los candidatos son miembros, y 0,017 cuando lo es uno de cada cien.»

**Ejemplos.** Úsalos si la sala pide números; el desarrollo completo está en GT §12.1.

1. *La media.* «Cuatro miembros y cuatro no miembros, con puntuaciones 0,9, 0,7, 0,6 y 0,4 para los miembros y 0,8, 0,5, 0,3 y 0,2 para los no miembros. Comparamos cada miembro con cada no miembro: 16 parejas, y el miembro puntúa más alto en 12. El AUC es 12 de 16, 0,75. Si llamamos "miembro" a todo lo que tiene 0,5 o más, quedan señalados 3 de 4 miembros y 2 de 4 no miembros, así que la ventaja es 0,75 menos 0,50, 0,25. De media el ataque acierta tres de cada cuatro veces, pero la media no dice quién queda expuesto.»
2. *La cola.* «Doscientas filas, la mitad miembros. El ataque está seguro de 20 personas: 10 miembros a los que da un 1 y 10 no miembros a los que da un 0. Todos los demás reciben una puntuación aleatoria. El AUC sale alrededor de 0,595, dentro de la banda del azar. Ahora mirad las 20 puntuaciones más altas: los 10 miembros seguros más unos 5 por azar, un 75% de miembros. Las 20 más bajas tienen alrededor de un 25%. FDIF es 0,75 menos 0,25, alrededor de 0,50, con un p-valor cercano a 0,003. La media dice "moneda al aire"; la cola señala a diez personas.»
3. *El miembro raro.* «Tomemos un buen ataque, TPR 0,8 y FPR 0,2. Probamos con 1.000 personas, la mitad miembros: señala a 400 miembros y a 100 no miembros, así que acierta 4 de cada 5 señales, 0,80. Probamos con 10.000 personas, 1 de cada 100 miembro: señala a 80 miembros y a 1.980 no miembros, así que solo acierta 80 de 2.060 señales, 0,04. El mismo ataque; solo ha cambiado la tasa base. Pero si el atacante señala solo las filas de las que el ataque está seguro, como en el ejemplo de la cola, no hay falsas alarmas y todas las señales aciertan.»

**Datos clave.** Anexo F del paper (pp. 92-95); la fórmula de la probabilidad a posteriori, anexo F, §21.3. Banda del azar con 100 miembros y 100 no miembros: aproximadamente de 0,38 a 0,62. Ejemplo del paper: TPR 0,8 y FPR 0,2 dan 0,04 con 1 de cada 100.

**Si preguntan.** *Entonces, ¿la inferencia de pertenencia es inofensiva cuando los miembros son raros?* No necesariamente: la cola aún puede señalar a personas concretas con mucha seguridad, que es lo que miden FDIF y la TPR con FPR bajo.

**Para profundizar.** GT §12, y §12.1 para los tres ejemplos desarrollados.

**Siguiente.** «Ahora, la demo 1 sobre el árbol sin restricciones.»

### Diapositiva 27 · Precisión de entrenamiento perfecta y una hoja de una persona: rechazado

*Título en la diapositiva: «Perfect training accuracy and a leaf of one person: refused»*

*Aproximadamente 2 minutos.*

**En pantalla.** Una tabla de comprobaciones del árbol sin restricciones con el resultado sembrado, el límite de la demo y si salta: precisión de entrenamiento frente a precisión en el holdout 1,000 frente a 0,590 (diferencia 0,410, límite 0,15, salta); hoja más pequeña de 1 fila; cociente de tamaño del fichero 0,267 (límite 0,75, no salta); AUC de pertenencia de peor caso 0,708 (límite 0,62, salta); ventaja 0,412 (límite 0,20, salta); TPR al 10% de FPR 0,156 (límite 0,35, no salta); FDIF 0,620 con p = 0,003 (salta); inferencia de atributos sobre el peso, se abstiene. Decisión: no publicar, saltan cuatro reglas. Nota: el ataque de atributos se abstuvo porque el árbol aisló las filas con las columnas de ruido.

**Qué decir.** «El investigador declararía un 100% de precisión. En las filas que reservó el entorno es un 59%. Esa diferencia de 0,41 es sobreajuste, y la hoja más pequeña contiene una sola fila de entrenamiento. El ataque de pertenencia de peor caso, el que describe el anexo G del paper, llega a un AUC de 0,708 y a una ventaja de 0,412, y FDIF es 0,620 con un p-valor de 0,003. Decisión: no publicar; saltan cuatro reglas. Fijaos ahora en lo que *no* salta. El fichero ocupa solo 0,27 veces la tabla de entrenamiento, y la TPR al 10% de FPR es 0,156. El tamaño por sí solo habría dejado salir este modelo, y por eso TECH 7 pide un conjunto de comprobaciones y no una sola. Y el ataque de atributos sobre el peso se abstiene, porque este árbol separa a las personas con las columnas de ruido, así que cambiar el peso de alguien nunca lo lleva a otra hoja. La diapositiva 25 era el caso en que el modelo sí divide por los campos ocultos. Recordad que estos límites son una política de la demo, no del paper.»

**Datos clave.** `demo_report.txt`, sección 4. Límites en `demo/graimatter_demo/disclosure.py` (ELA 8). Probabilidad a posteriori 0,630 / 0,017. Salem-synth sobre este árbol: AUC 0,703, FDIF 1,000.

**Si preguntan.** *¿Qué es exactamente el ataque de "peor caso"?* Entrena un clasificador con las probabilidades predichas por el modelo más la etiqueta real, con las filas de entrenamiento y las reservadas en la mano: una cota superior conservadora, no un atacante realista (anexo G del paper).

**Para profundizar.** GT §13.0 (la política de la demo) y §13.4.

**Siguiente.** «Los mismos datos, pero a través de un safe wrapper.»

### Diapositiva 28 · Hoja 20, profundidad 4: AUC 0,528, publicado según una política de demo

*Título en la diapositiva: «Leaf 20, depth 4: AUC 0.528, released under a demo policy»*

*Aproximadamente 2 minutos.*

**En pantalla.** Una figura de barras que compara el árbol sin restricciones y el safe wrapper en AUC de pertenencia (0,708 frente a 0,528), ventaja (0,412 frente a 0,004), entrenamiento menos holdout (0,410 frente a 0,108), TPR al 10% de FPR (0,156 frente a 0,116) y FDIF (0,620 frente a 0,020), con el límite de la demo como línea discontinua. Árbol sin restricciones: rechazar. Safe wrapper: publicar según la política de la demo.

**Qué decir.** «El investigador pide la misma configuración, pero a través del safe wrapper escrito a mano. Lee `demo/constraints.json` y la corrige: tamaño mínimo de hoja de 1 a 20, profundidad máxima de ilimitada a 4. El anexo D del paper muestra el formato del fichero de restricciones con un tamaño mínimo de hoja de 5 como ejemplo; la demo es más estricta para que el contraste se vea con unos cientos de filas. La precisión de entrenamiento baja a 0,692, y la precisión en el holdout apenas se mueve, 0,584. Así que la precisión extra del árbol profundo era memorización, no capacidad. El ataque de peor caso cae a un AUC de 0,528, una ventaja de 0,004 y una FDIF de 0,020 con un p-valor de 0,445. No salta ninguna regla de la demo, así que el script lo publica. Decidlo con claridad: la política es nuestra, no del paper.»

**Datos clave.** `demo_report.txt`, sección 5. TECH 9-10. `request_release()` solo dice "Run file through the next step of the checking procedure" (pasa el fichero al siguiente paso del procedimiento de revisión); deciden las cifras de los ataques. Probabilidad a posteriori 0,502 / 0,010.

**Si preguntan.** *¿Por qué 20 y 4?* Una elección local para que el contraste se vea con 500 filas. El experimento 2 del anexo A del paper advierte de que una configuración segura en un conjunto de datos puede ser arriesgada en otro, y por eso la demo 1 sigue atacando el árbol con wrapper.

**Para profundizar.** GT §13.5.

**Siguiente.** «Pero un ataque ve algo que la media esconde.»

### Diapositiva 29 · El fallo silencioso: AUC cerca de 0,5, pero FDIF 0,280

*Título en la diapositiva: «The quiet failure: AUC near 0.5, but FDIF 0.280»*

*Aproximadamente 1,5 minutos.*

**En pantalla.** Una figura: el árbol con safe wrapper bajo dos ataques de pertenencia. Peor caso (tablas del TRE): AUC 0,528, TPR al 10% de FPR 0,116, FDIF 0,020 (p 0,445). Salem-synth (datos parecidos): AUC 0,512, TPR al 10% de FPR 0,252, FDIF 0,280 (p 0,003). Nota: los miembros se acumulan en las puntuaciones extremas; un responsable de los datos podría rechazarlo por eso.

**Qué decir.** «Sobre el mismo árbol con wrapper lanzamos también un segundo ataque, Salem-synth, en el que el atacante entrena un modelo sombra con datos parecidos en lugar de con las tablas del propio entorno. Su AUC es 0,512, cerca del azar. Pero su FDIF es 0,280 con un p-valor de 0,003, y la TPR al 10% de FPR es 0,252: los miembros se acumulan en las puntuaciones extremas. Es exactamente el aviso del anexo F del paper: una métrica media puede esconder una cola. La regla de exportación de la demo sigue el ataque de peor caso, cuya FDIF es 0,020, así que sigue publicando. Un responsable de los datos al que le preocupe la cola podría rechazarlo, y eso es una decisión de política, no técnica.»

**Datos clave.** `demo_report.txt`, sección 5 (Salem-synth). La tabla 2 del anexo A del paper describe los escenarios de Salem. El ejemplo del anexo F: un ataque que está seguro de 20 de 200 filas tiene un AUC de alrededor de 0,595, dentro de la banda del azar.

**Si preguntan.** *¿Por qué un atacante más débil ve más en la cola?* Los ataques usan información distinta; el modelo sombra de Salem-synth separa unas pocas filas extremas que el clasificador de peor caso diluye en la media. Es un recordatorio de que hay que lanzar más de un ataque.

**Para profundizar.** GT §13.5, "El fallo silencioso", y §12 (FDIF).

**Siguiente.** «Algunos modelos no deberían publicarse nunca como fichero.»

### Diapositiva 30 · Vecinos más cercanos y SVC guardan filas: hay que rechazarlos

*Título en la diapositiva: «Nearest neighbours and SVC store rows: refuse them»*

*Aproximadamente 1,5 minutos.*

**En pantalla.** Tarjetas: el modelo de 1 vecino más cercano guarda las 500 filas (fichero de 68.677 bytes, cociente 1,010), rechazado. El clasificador de vectores soporte con kernel RBF guarda 423 vectores soporte de 500 (cociente 0,94), rechazado. Los wrappers de ambas clases se niegan a entrenar (`constraints.json` los marca como no permitidos). Las alternativas del paper (TECH 11): datos agregados, un algoritmo diferencialmente privado o un servicio con consultas limitadas. En el paper: anexo E, §20.4, un SVM que contenía 441 filas exactas de pacientes de un total de 798.

**Qué decir.** «Los modelos basados en instancias necesitan sus filas de entrenamiento para funcionar. Un modelo de vecinos más cercanos busca las filas guardadas más próximas; un SVC con kernel compara las entradas nuevas con sus vectores soporte. Esas filas se pueden leer directamente del fichero, así que la demo rechaza ambos, digan lo que digan las cifras de los ataques. Las opciones del paper son entrenar con datos agregados, usar una variante diferencialmente privada o no publicar el fichero y ofrecer en su lugar un servicio con consultas limitadas. Su caso de estudio describe un entorno real que encontró, dentro de un SVM, 441 copias de registros de pacientes de un total de 798.»

**Datos clave.** TECH 11 (p. 49), §10.1.5 (pp. 39-40), anexo E del paper, §20.4 (pp. 91-92). `demo_report.txt`, sección 6.

**Si preguntan.** *¿Un SVM lineal también es un problema?* Depende de cómo se guarde. `LinearSVC` de scikit-learn solo conserva los pesos, pero `SVC(kernel="linear")` sigue guardando sus vectores soporte en el fichero. Comprobad lo que contiene el fichero, no el nombre del modelo.

**Para profundizar.** GT §13.6; Anexo B.3 (reconstrucción).

**Siguiente.** «¿Y si el investigador edita el modelo después de entrenarlo?»

### Diapositiva 31 · Editar el modelo después de fit() se detecta

*Título en la diapositiva: «Editing the model after fit() is caught»*

*Aproximadamente 2 minutos.*

**En pantalla.** Una figura: el pipeline del safe wrapper: `constraints.json` (apetito de riesgo), inicialización del wrapper (corrige la hoja y la profundidad o registra una excepción), `fit()` (guarda un resumen del árbol), `request_release()` (comprueba el tamaño de hoja y compara parámetros y resumen con el estado entrenado), ataques del TRE, registro e instantánea. Un camino de manipulación: parámetros editados de vuelta después de entrenar, atributo `hidden_rows` añadido, hoja más pequeña aún de 1, así que "Do not allow release" (no permitir la publicación).

**Qué decir.** «El wrapper registra el estado del modelo en el momento de entrenarlo. En esta sección de la demo, el investigador se salta las restricciones y entrena un árbol profundo, y después vuelve a poner los parámetros cerca de los valores permitidos y añade un atributo oculto. `request_release()` compara el estado entrenado con el actual y dice que no se publique: `max_depth` y `min_samples_leaf` cambiaron después de entrenar, la hoja más pequeña sigue conteniendo una fila y se añadió un atributo llamado `hidden_rows`. Eso cubre tanto el caso descuidado, RT1, cambiar un parámetro y olvidar reentrenar, como el deliberado, RT2, esconder datos. Un fichero con extensión `.txt` se rechaza porque no es `.joblib` ni `.pkl`. Para el modelo aprobado, la demo escribe una entrada en el registro y una instantánea del pipeline, que es TECH 3.»

**Datos clave.** §10.1.2 (p. 37), TECH 3 (p. 42), TECH 10 (p. 48). `demo_report.txt`, secciones 7 y 9; `tampered_tree.release.json`, `data_use_register.json`, `pipeline_snapshot.json`. El resumen es un SHA-256 de las matrices del árbol.

**Si preguntan.** *¿Esto es envenenamiento del modelo?* Es la misma capacidad, control del modelo (NISTAML.011/.026, OWASP ML10), usada aquí para esconder datos en lugar de para cambiar predicciones. *¿Es seguro un `.pkl`?* Los ficheros pickle pueden ejecutar código al cargarse; tratad cualquier fichero de modelo que venga de fuera como no fiable (Anexo B.4).

**Para profundizar.** GT §13.7 y §13.9.

**Siguiente.** «Si el modelo se queda en un servidor, el entorno puede limitar las consultas.»

### Diapositiva 32 · Contar filas, no llamadas: se permite un paciente y se bloquean 20

*Título en la diapositiva: «Count rows, not calls: one patient allowed, 20 blocked»*

*Aproximadamente 1,5 minutos.*

**En pantalla.** Una figura: un presupuesto de 8 filas para un usuario. Petición 1, consulta de un paciente, 1 fila: permitida. Petición 2, el barrido de atributos, 20 filas: rechazada (1 usada, presupuesto de 8). Nota: un servicio real con consultas limitadas también necesita una prueba externa (TECH 17).

**Qué decir.** «Si el modelo no se publica como fichero sino que se queda en un servidor, el entorno puede limitar las consultas. La puerta de la demo da a un usuario un presupuesto de 8 filas. La consulta de un solo paciente por parte de un clínico usa 1 fila y se permite. Después, el mismo usuario envía en una sola petición el barrido de 20 combinaciones del caso de estudio de atributos. La puerta lo rechaza: 20 filas pedidas, 1 ya usada, presupuesto de 8. La unidad importa. Si el presupuesto contara llamadas HTTP, una llamada con 20 filas pasaría. TECH 17 dice que una parte externa debería probar un servicio real con consultas limitadas; la demo solo implementa la lógica de control. Y recordad la demo 3 desde el otro lado: un presupuesto de filas frena la extracción del modelo, pero 200 filas ya copiaron un modelo sencillo.»

**Datos clave.** TECH 16-17 (pp. 52-53), §10.1.7 (pp. 40-41). `demo_report.txt`, sección 8. Disposición 6.2 del código del Reino Unido.

**Si preguntan.** *¿Cómo se impide que alguien use muchas cuentas?* Con un presupuesto solo, no se puede; las comprobaciones de identidad y la vigilancia forman parte del servicio, y por eso TECH 17 pide una prueba externa.

**Para profundizar.** GT §13.8; GT §3.2 para el lado de la extracción.

**Siguiente.** «La última comprobación de la demo 1 es la privacidad diferencial, sobre la publicación más sencilla posible.»

### Diapositiva 33 · El ruido protege una media; quedarse con la mejor de 50 extracciones lo deshace

*Título en la diapositiva: «Noise protects a mean; the best of 50 draws undoes it»*

*Aproximadamente 1,5 minutos.*

**En pantalla.** Una figura: el acierto del atacante al adivinar si una persona estaba incluida en una media publicada: 1,000 con la media determinista, 0,703 con ε = 8, 0,522 con ε = 1, 0,487 con ε = 0,2 (0,5 es lanzar una moneda). Error de la media publicada con ε = 0,2: 0,3053 con una extracción, 0,0084 quedándose con la mejor de 50. Nota: quedarse con la extracción más cercana a la media real deshace el ruido; el personal del TRE elige la semilla sin mirar.

**Qué decir.** «La privacidad diferencial es una propiedad del mecanismo de publicación, no de los datos. El experimento mental del paper: el atacante lo sabe todo salvo si una persona estaba incluida, y ve lo publicado. Una media sin más delata la respuesta: acierto de 1,000. Añadir ruido de Laplace, donde un epsilon menor significa más ruido, devuelve al atacante hacia el lanzamiento de moneda: 0,703 con epsilon 8, 0,522 con 1, 0,487 con 0,2. TECH 12 añade un aviso práctico. Con epsilon 0,2, una media con ruido se aleja 0,31 de la real, pero si alguien hace 50 extracciones y se queda con la más cercana, se aleja 0,008, lo que anula la protección. Así que debe ser el personal del entorno, no el investigador, quien elija la semilla aleatoria, sin mirar el resultado. Este repositorio solo esboza la privacidad diferencial sobre una media; no entrena un modelo privado.»

**Datos clave.** §10.1.3 (pp. 37-39), TECH 12 (p. 50). `demo_report.txt`, sección 3. Sensibilidad (90 − 30) / 500 = 0,12; escala de Laplace = sensibilidad / ε. NIST: el censo de Estados Unidos de 2020 usó ε = 19,61.

**Si preguntan.** *¿Qué epsilon deberíamos usar?* No hay una respuesta universal; es un compromiso entre privacidad y utilidad, y en la práctica se usan a menudo valores grandes (NIST §2.4.5).

**Para profundizar.** GT §13.3; Anexo B.3 (la privacidad diferencial y sus límites para cada clase de privacidad).

**Siguiente.** «Ahora, la misma cohorte con la herramienta oficial.»

### Diapositiva 34 · sacroml: hoja 5, "proceed to next step", y sigue marcado

*Título en la diapositiva: «sacroml: leaf 5, 'proceed to next step', still flagged»*

*Aproximadamente 3 minutos.*

**En pantalla.** Una tabla para sacroml 2.0.1, árbol sin restricciones frente a árbol con wrapper (hoja 5): precisión de entrenamiento / en el holdout 1,000 / 0,590 frente a 0,868 / 0,566; AUC de pertenencia de peor caso en 3 repeticiones, media 0,500 frente a 0,494, ninguna por encima de la banda nula; hoja más pequeña frente al umbral de 10, 1 frente a 5, `k_anonymity_risk` en true en ambos; las demás alertas estructurales en true; `dof_risk` en false; `request_release()` sin un Target dice "Proceed to next step of checking" (pasar al siguiente paso de la revisión); volver a poner `min_samples_leaf` de 5 a 1 después de `fit()` hace que `posthoc_check()` lo declare revelador (disclosive).

**Qué decir.** «La segunda demo pasa la misma cohorte por sacroml 2.0.1, la herramienta mantenida del proyecto AI-SDC que nombra el paper. Su safe wrapper avisa de que una hoja mínima de 1 está por debajo de su mínimo recomendado de 5 y la cambia a 5. `request_release()` sin un target escribe un fichero de target y dice "Proceed to next step of checking": no lanza ataques y no es una aprobación. Pasarle un target lanzaría además el ataque LiRA, que el ejemplo de referencia ejecuta con 100 modelos sombra; esta demo no ejecuta LiRA. Después vienen los ataques. El ataque estructural marca una hoja como arriesgada cuando contiene menos de 10 filas de entrenamiento, así que se marcan tanto el árbol sin restricciones como el árbol con wrapper de hoja 5. Dicho de otro modo, pasar de hoja 1 a hoja 5 es lo que hacen las reglas publicadas, y la propia comprobación estructural del paquete sigue calificando de arriesgado ese árbol. Y el AUC de pertenencia es 0,500 para el árbol que memorizó a todo el mundo. La siguiente diapositiva explica por qué.»

**Datos clave.** `demo/output/sacroml/sacroml_report.txt`; `report.json` y `report.pdf` de cada ataque en `demo/output/sacroml/`. Banda nula de 0,377 a 0,623. La ejecución sembrada tarda unos tres minutos y medio.

**Si preguntan.** *¿Cómo leo los resultados de atributos?* Cada celda es conjeturas únicas correctas sobre conjeturas únicas hechas, sobre 500 filas; "136/136" significa que acertó todas las conjeturas que el ataque se atrevió a hacer, no que se acertaran 136 filas (GT §14.4).

**Para profundizar.** GT §14.

**Siguiente.** «El mismo árbol: 0,708 en una demo y 0,500 en la otra.»

### Diapositiva 35 · El mismo árbol, AUC 0,708 o 0,500: dos ataques distintos

*Título en la diapositiva: «Same tree, AUC 0.708 or 0.500: two different attacks»*

*Aproximadamente 3 minutos.*

**En pantalla.** Una figura: la confianza en la etiqueta real para las filas de entrenamiento (miembros) y las reservadas. Árbol sin restricciones: hojas puras, todas las respuestas son 0 o 1; los miembros siempre 1; las reservadas aciertan el 59% de las veces. Safe wrapper (hoja 20, profundidad 4): un reparto parecido en los dos grupos. Notas: el ataque escrito a mano ve las probabilidades más la etiqueta real; sacroml solo ve la probabilidad predicha, y las hojas puras son extremas para todos.

**Qué decir.** «Las dos demos llaman a su ataque "de peor caso", pero son pruebas distintas. El ataque escrito a mano entrena un clasificador con las probabilidades predichas *más la etiqueta real*, así que puede usar la confianza en la clase correcta. En el árbol sin restricciones todas las hojas son puras, así que cada predicción es 0 o 1. Las filas de entrenamiento siempre reciben confianza 1 en su etiqueta real. Las reservadas reciben 1 cuando el árbol acierta por casualidad, el 59% de las veces, y 0 en caso contrario. El ataque que conoce la etiqueta ve esa diferencia y llega a 0,708. El ataque de sacroml puntúa las filas solo con la probabilidad predicha. Sin la etiqueta, una hoja pura parece igual de extrema para miembros y no miembros, así que su AUC es 0,500. La lección: un AUC cercano a 0,5 del paquete no significa que el árbol no haya memorizado. En la demo 2, lo que lo detecta es el ataque estructural. En el árbol con wrapper, con hojas de 20 filas, los dos grupos se reparten en confianzas parecidas, y por eso el AUC de la demo 1 baja a 0,528.»

**Datos clave.** Anexo G del paper (p. 96). Código: `attacks.py` (`_attack_features`) y `sacroml.attacks.worst_case_attack` (configurado con `include_model_correct_feature: false`, `sort_probs: true`).

**Si preguntan.** *¿Qué ataque tiene razón?* Los dos son pruebas válidas de amenazas distintas. Esa es la idea: una sola cifra de ataque no es una decisión de publicación.

**Para profundizar.** GT §15.2.

**Siguiente.** «Tres diferencias resumen las dos demos.»

### Diapositiva 36 · Hoja 20 frente a 5, con etiqueta frente a solo probabilidades

*Título en la diapositiva: «Leaf 20 vs 5, label-aware vs probability-only»*

*Aproximadamente 2 minutos.*

**En pantalla.** Una tabla comparativa: regla de hoja (20 y profundidad 4 frente a 5, del fichero de reglas), precisión del árbol con wrapper (0,692 / 0,584 frente a 0,868 / 0,566), ataque de pertenencia (probabilidades más etiqueta, AUC 0,528, frente a solo probabilidades, AUC medio 0,494), control de hojas (20 frente a 5 < 10, `k_anonymity_risk` en true), resultado (publicar según la política de la demo frente a "Proceed to next step of checking", con el riesgo estructural aún en true).

**Qué decir.** «Hay tres diferencias que importan. Primera, la regla de hoja: el wrapper escrito a mano fuerza hoja 20 y profundidad 4; el fichero de reglas del paquete fuerza hoja 5. Segunda, el ataque de pertenencia: probabilidades más la etiqueta frente a solo probabilidades. Tercera, el resultado: el script escrito a mano publica el árbol más estricto porque su propio ataque cae dentro de los límites de la demo; el paquete aquí nunca aprueba nada, dice que se siga comprobando, y su ataque estructural sigue marcando el árbol de hoja 5. Ninguna de las dos es un proceso de aprobación. Un entorno real combinaría estos tipos de evidencia con una política acordada con su responsable de los datos.»

**Datos clave.** `demo_report.txt`, sección 10, y `sacroml_report.txt`. Tamaño de hoja del ejemplo del anexo D del paper (p. 83): 5. ELA 8, ELA 11.

**Si preguntan.** *¿Usamos el paquete o escribimos el nuestro?* Usad el paquete mantenido por sus comprobaciones estructurales y sus informes, añadid ataques que usen la etiqueta y fijad los umbrales con el responsable de los datos.

**Para profundizar.** GT §15.1 y §15.3.

**Siguiente.** «¿Qué saca de todo esto cualquier despliegue de alta confianza?»

### Diapositiva 37 · Lo que GRAIMATTER enseña a cualquier despliegue de alta confianza

*Título en la diapositiva: «What GRAIMATTER teaches any high-trust deployment»*

*Aproximadamente 2 minutos.*

**En pantalla.** Seis hábitos: suponer el peor atacante posible; evaluar con filas que quien construyó el modelo nunca vio; comprobar la estructura, no solo las puntuaciones; vigilar la cola; congelar el artefacto; presupuestar las consultas en filas; cada uno con sus fuentes en el green paper, el NIST, el código del Reino Unido y OWASP. Un pie: no se cubren la evasión y el envenenamiento (el backdoor de la demo 3 deja intacta la precisión en el holdout) ni la IA generativa.

**Qué decir.** «Seis hábitos de GRAIMATTER sirven en cualquier sitio donde un modelo toque datos sensibles o decisiones de alto riesgo. Probad frente al atacante más fuerte que podáis imaginar, porque un fichero publicado se lo da todo. Mantened los datos de evaluación lejos de quien construye el modelo, y dejad que otro lance los ataques. Mirad la estructura del modelo, no solo las puntuaciones de los ataques, porque un ataque puede pasar por alto lo que muestra un recuento de hojas: diapositiva 35. Mirad la cola de la distribución de puntuaciones, no solo la media: diapositiva 29. Congelad el artefacto aprobado y detectad las ediciones: diapositiva 31. Contad las consultas en filas: diapositiva 32. Lo que GRAIMATTER no os da es protección frente a la evasión y el envenenamiento. La demo 3 mostró que su comprobación de precisión en el holdout no ve un backdoor, así que otros despliegues necesitan también esas pruebas, y un sistema generativo necesita los controles frente a la inyección de prompts de la diapositiva 12.»

**Datos clave.** Green paper: TECH 3, 6, 10, 16 y anexos F-G; NIST §2.1.4, §2.4.2, §2.4.5; código del Reino Unido 6.2, 8.1.2, 8.3, 9.2.1, 9.4; OWASP ML10.

**Si preguntan.** *¿Y la gobernanza?* Se trasladan otros dos hábitos: acordar el apetito de riesgo con quien responde de los datos (ELA 8, ELA 11; código del Reino Unido 3.1.3) y tratar el modelo como un posible dato personal (ELA 1; Dictamen 28/2024 del EDPB).

**Para profundizar.** GT §16.

**Siguiente.** «Antes de la puerta, dejemos claro lo que este repositorio no decide.»

### Diapositiva 38 · Lo que este repositorio no decide

*Título en la diapositiva: «What this repository does not decide»*

*Aproximadamente 1,5 minutos.*

**En pantalla.** Seis tarjetas: un apetito de riesgo real (los umbrales de la demo 1 son locales; ELA 8), asesoramiento jurídico (los marcos se resumen, no se interpretan), ataques fuertes (sin LiRA; la demo 3 usa ataques voraces y basados en consultas), entrenamiento privado (ningún modelo con privacidad diferencial), IA generativa (ninguna demo de LLM; ver safety-trust-engine), datos reales y aprobación (una sola cohorte sintética; ninguna demo aprueba un modelo).

**Qué decir.** «Sed explícitos con los límites. Los umbrales de la demo 1 existen para que el script pueda decir sí o no; el paper no publica umbrales universales. Las diapositivas legales resumen documentos y no son asesoramiento. Los ataques son versiones didácticas: no hay LiRA, y la evasión de la demo 3 es una búsqueda voraz sobre unos pocos campos, no un ataque optimizado. No hay ningún modelo diferencialmente privado ni ninguna demo de IA generativa. La cohorte es sintética, y ninguna de las demos de GRAIMATTER aprueba un modelo: el paquete dice "proceed to next step".»

**Datos clave.** `docs/brief-for-presentation-and-guide.md`, "Claims to keep accurate".

**Si preguntan.** *¿Podemos usar las tolerancias como nuestra política?* Solo como punto de partida para hablarlo con el responsable de los datos; se fijaron para el taller.

**Para profundizar.** GT §19.

**Siguiente.** «Por último, cómo convertir estas cifras en una decisión de publicación: la puerta.»

---

## Cierre

### Diapositiva 39 · Una puerta, cuatro lentes: GRAIMATTER cumple, el artículo 15(5) falla

*Título en la diapositiva: «One gate, four lenses: GRAIMATTER passes, Article 15(5) fails»*

*Aproximadamente 2,5 minutos.*

**En pantalla.** Una tabla de paquetes de regulación con controles, cumplen, fallan y sin evidencia: art. 15(5) del Reglamento de IA y código del Reino Unido 8 / 2 / 6 / 0; NIST AI 100-2 6 / 3 / 3 / 0; GRAIMATTER TECH 6 / 5 / 0 / 1 (demo 2); NIST AI RMF y SR 26-02 8 / 5 / 3 / 0. Incumplimientos: evasión del 78,7% (tolerancia del 10%), una copia que coincide en un 86,9% tras un solo presupuesto de 200 filas (80%), un backdoor que sube el éxito del disparador en 71,7 puntos (tolerancia de 10). Dentro de tolerancia: pertenencia, atributos, diferencia con el holdout, filas guardadas, controles de publicación, presupuesto de consultas y la cadena de suministro (ningún fichero manipulado de la demo 4 pasa el pin y el escaneo o el suelo). Tarjetas: "Nunca un verde silencioso" y "Leído con SR 26-02".

**Qué decir.** «Las demos imprimen cifras. Una decisión de publicación necesita juzgar esas cifras frente a obligaciones con nombre, y dejar un registro que alguien pueda auditar. La puerta vuelve a ejecutar las demos 1, 3 y 4, lee las cifras que ya imprimen y da a cada control regulatorio un veredicto: cumple, falla o sin evidencia. Los controles de GRAIMATTER cumplen con el árbol con wrapper. Los controles de solidez fallan con el bosque de la demo 3: evasión del 78,7% frente a una tolerancia del 10%, una copia que coincide en un 86,9% tras un solo presupuesto de 200 filas y un backdoor que sube el éxito del disparador en 71,7 puntos. Las dos mitades no se contradicen: los controles de privacidad por sí solos no hacen que un modelo sea resistente en el sentido del artículo 15, apartado 5, que nombra también el envenenamiento y la evasión. Su cláusula sobre el envenenamiento del modelo se cumple: el pin, el escaneo y los suelos de la demo 4 rechazan todos los ficheros manipulados. Un control cuya demo no se ejecutó se declara sin evidencia, nunca como cumplido: la CI no instala sacroml, así que declara la demo 2 fuera de alcance de forma explícita y el informe lo dice. El paquete de Estados Unidos lee la misma evidencia con el NIST AI RMF y la guía federal de riesgo de modelos, donde un clasificador encaja directamente: el holdout del entorno es la validación independiente, la puerta en la CI es la monitorización continua. Las tolerancias son un apetito de riesgo fijado para el taller, y la correspondencia es nuestra.»

**Datos clave.** `demo/run_gate.py`; informes en `demo/output/gate/`; workflow de CI `.github/workflows/gate.yml`. El patrón viene de safety-trust-engine. SR 26-02 y el OCC Bulletin 2026-13 sustituyeron a SR 11-7 en abril de 2026.

**Si preguntan.** *¿Puedo cambiar una tolerancia?* Sí: `--fail-under metric=value`, por ejemplo `--fail-under evasion.self_reported=0.5`. *¿Por qué la CI no ejecuta la demo 2?* sacroml arrastra PyTorch; la CI usa `--accept-missing 2` para que el hueco se vea en lugar de quedar escondido.

**Para profundizar.** GT §17 (todas las métricas y tolerancias en la §17.2, los paquetes en la §17.3).

**Siguiente.** «Todo esto se puede volver a ejecutar en unos minutos.»

### Diapositiva 40 · Cuatro demos y una puerta, con los informes en demo/output

*Título en la diapositiva: «Four demos and a gate, reports under demo/output»*

*Aproximadamente 1 minuto.*

**En pantalla.** Los comandos: `uv venv --python 3.11`, `uv pip install -r demo/requirements.txt`, los cuatro scripts de demo y `run_gate.py`, y después los scripts de las figuras y de las diapositivas. Tres tarjetas: demos 3 y 4 (segundos, `aml_report.txt` y `supply_chain_report.txt`), demo 1 (segundos, `demo_report.txt`, diccionario de datos, entrada en el registro, instantánea del pipeline, informes de publicación), demo 2 (unos minutos, `sacroml_report.txt`, `report.json` y `report.pdf` por ataque).

**Qué decir.** «La instalación está en el README del repositorio: cread un entorno de Python 3.11 con uv e instalad los requisitos, que traen numpy, scikit-learn y sacroml, con PyTorch. Las demos 3, 4 y 1 se ejecutan en segundos; la demo 2 tarda unos minutos. La puerta vuelve a ejecutar las demos y escribe su informe en `demo/output/gate`, y la CI la ejecuta en cada pull request. Las guías recorren cada informe sección a sección, en inglés y en español.»

**Datos clave.** README; demo/README.md; GT §18. `uv sync` instala sin sacroml; añade `--extra sacroml` para la demo 2. En Windows PowerShell, activa el entorno con `. .\.venv\Scripts\Activate.ps1`.

**Si preguntan.** *¿Hace falta una GPU?* No.

**Para profundizar.** GT §18.

**Siguiente.** «Y los documentos que hay detrás de todo esto.»

### Diapositiva 41 · Para seguir leyendo

*Título en la diapositiva: «Read further»*

*Aproximadamente 1 minuto, y después preguntas.*

**En pantalla.** Referencias: NIST AI 100-2e2025; MITRE ATLAS 2026.09; OWASP ML y LLM Top 10; art. 15 del Reglamento de IA de la UE, el Digital Omnibus y el Dictamen 28/2024 del EDPB; el código del Reino Unido, ETSI EN 304 223 y las directrices del NCSC y la CISA; el green paper de GRAIMATTER; SACRO-ML.

**Qué decir.** «Los dos PDF, el informe del NIST y el green paper, están en la raíz del repositorio. La guía técnica, en inglés y en español, sigue el mismo orden que estas diapositivas, relaciona cada sección con sus diapositivas en el Anexo A y explica cada clase de ataque del NIST en el Anexo B. Gracias; ¿preguntas?»

**Datos clave.** GT §21 tiene la lista completa de referencias.

**Para profundizar.** GT §20 (glosario) y §21 (referencias).

---

*Las cifras de esta guía proceden de los informes sembrados de `demo/output/` y coinciden con las diapositivas y con la guía técnica. Cuando cambien las diapositivas (`docs/make_deck.py`), actualiza esta guía y su versión en inglés en el mismo cambio.*
