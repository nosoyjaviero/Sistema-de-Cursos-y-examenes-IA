# 📚 Documentación JSON - Ejercicios Personalizados

Este documento describe todos los formatos JSON disponibles para crear ejercicios en **🎯 Haz tus propias preguntas**.

---

## 📋 Índice

1. [Ejercicios Básicos](#ejercicios-básicos)
   - [MCQ (Opción Múltiple)](#mcq---opción-múltiple)
   - [True/False (Verdadero/Falso)](#truefalse---verdaderofalso)
   - [Cloze (Rellenar Huecos)](#cloze---rellenar-huecos)
   - [Short Answer (Respuesta Corta)](#shortanswer---respuesta-corta)
   - [Open Question (Pregunta Abierta)](#openquestion---pregunta-abierta)
   - [Caso de Estudio](#caso-de-estudio)

2. [Comprensión Lectora (Idiomas)](#comprensión-lectora-idiomas)
   - [Reading Comprehension](#reading_comprehension)
   - [Reading Written](#reading_written)
   - [Reading True/False](#reading_true_false)
   - [Reading Cloze](#reading_cloze)
   - [Reading Skill](#reading_skill)
   - [Reading Matching](#reading_matching)
   - [Reading Sequence](#reading_sequence)

3. [Expresión Escrita (Idiomas)](#expresión-escrita-idiomas)
   - [Writing Short](#writing_short)
   - [Writing Paraphrase](#writing_paraphrase)
   - [Writing Correction](#writing_correction)
   - [Writing Transformation](#writing_transformation)
   - [Writing Essay](#writing_essay)
   - [Sentence Builder](#sentence_builder)
   - [Formal Email](#formal_email)
   - [Picture Description](#picture_description)

4. [Programación](#programación)
   - [Code MCQ](#code_mcq)
   - [Code Como Ejemplo](#code_como_ejemplo)
   - [Code Encontrar Error](#code_encontrar_error)
   - [Code Qué Pasa Si](#code_que_pasa_si)
   - [Code Industria](#code_industria)
   - [Code Error Industria](#code_error_industria)

---

## Ejercicios Básicos

### MCQ - Opción Múltiple

Preguntas con 4 opciones donde solo una es correcta.

```json
{
  "preguntas": [
    {
      "tipo": "mcq",
      "pregunta": "¿Cuál es la capital de Francia?",
      "opciones": ["A) Madrid", "B) París", "C) Roma", "D) Berlín"],
      "respuesta_correcta": "B",
      "explicacion": "París es la capital de Francia desde hace siglos.",
      "puntos": 1
    }
  ]
}
```

| Campo                | Tipo   | Descripción                                             |
| -------------------- | ------ | ------------------------------------------------------- |
| `tipo`               | string | Siempre `"mcq"`                                         |
| `pregunta`           | string | El enunciado de la pregunta                             |
| `opciones`           | array  | 4 opciones con formato `"A) texto"`, `"B) texto"`, etc. |
| `respuesta_correcta` | string | La letra correcta: `"A"`, `"B"`, `"C"` o `"D"`          |
| `explicacion`        | string | Por qué la respuesta es correcta                        |
| `puntos`             | number | Puntos que vale (normalmente 1)                         |

---

### True/False - Verdadero/Falso

Afirmaciones que el usuario debe evaluar como verdaderas o falsas.

```json
{
  "preguntas": [
    {
      "tipo": "true_false",
      "pregunta": "El sol es una estrella.",
      "respuesta_correcta": "Verdadero",
      "explicacion": "El sol es una estrella de tipo G, ubicada en el centro de nuestro sistema solar.",
      "puntos": 1
    }
  ]
}
```

| Campo                | Tipo   | Descripción                   |
| -------------------- | ------ | ----------------------------- |
| `tipo`               | string | Siempre `"true_false"`        |
| `pregunta`           | string | Una afirmación a evaluar      |
| `respuesta_correcta` | string | `"Verdadero"` o `"Falso"`     |
| `explicacion`        | string | Justificación de la respuesta |
| `puntos`             | number | Puntos que vale               |

---

### Cloze - Rellenar Huecos

Texto con espacios en blanco que el usuario debe completar.

```json
{
  "preguntas": [
    {
      "tipo": "cloze",
      "pregunta": "Completa los espacios en blanco:",
      "texto_con_huecos": "El proceso de ___(1)___ permite que ___(2)___ funcione correctamente.",
      "respuestas": ["fotosíntesis", "la planta"],
      "explicacion": "La fotosíntesis es el proceso por el cual las plantas producen energía.",
      "puntos": 2
    }
  ]
}
```

| Campo              | Tipo   | Descripción                            |
| ------------------ | ------ | -------------------------------------- |
| `tipo`             | string | Siempre `"cloze"`                      |
| `pregunta`         | string | Instrucción para el ejercicio          |
| `texto_con_huecos` | string | Texto con `___(N)___` para cada hueco  |
| `respuestas`       | array  | Lista ordenada de respuestas correctas |
| `explicacion`      | string | Explicación de las respuestas          |
| `puntos`           | number | Puntos totales del ejercicio           |

---

### Short_Answer - Respuesta Corta

Preguntas que requieren una respuesta breve del usuario.

```json
{
  "preguntas": [
    {
      "tipo": "short_answer",
      "pregunta": "¿Qué es la mitosis?",
      "respuesta_esperada": "La mitosis es el proceso de división celular donde una célula madre se divide en dos células hijas idénticas.",
      "palabras_clave": ["división", "celular", "células hijas", "idénticas"],
      "explicacion": "La mitosis es fundamental para el crecimiento y reparación de tejidos.",
      "puntos": 2
    }
  ]
}
```

| Campo                | Tipo   | Descripción                                 |
| -------------------- | ------ | ------------------------------------------- |
| `tipo`               | string | Siempre `"short_answer"`                    |
| `pregunta`           | string | La pregunta a responder                     |
| `respuesta_esperada` | string | La respuesta modelo completa                |
| `palabras_clave`     | array  | Palabras que deben aparecer en la respuesta |
| `explicacion`        | string | Explicación detallada                       |
| `puntos`             | number | Puntos que vale                             |

---

### Open_Question - Pregunta Abierta

Preguntas de desarrollo que requieren explicación detallada.

```json
{
  "preguntas": [
    {
      "tipo": "open_question",
      "pregunta": "Explica las causas y consecuencias de la Revolución Industrial.",
      "puntos_clave": [
        "Avances tecnológicos (máquina de vapor)",
        "Migración del campo a la ciudad",
        "Surgimiento de la clase obrera",
        "Impacto ambiental"
      ],
      "respuesta_modelo": "La Revolución Industrial fue un período de transformación...",
      "puntos": 5
    }
  ]
}
```

| Campo              | Tipo   | Descripción                        |
| ------------------ | ------ | ---------------------------------- |
| `tipo`             | string | Siempre `"open_question"`          |
| `pregunta`         | string | Pregunta que requiere desarrollo   |
| `puntos_clave`     | array  | Lista de puntos que debe mencionar |
| `respuesta_modelo` | string | Respuesta completa esperada        |
| `puntos`           | number | Puntos totales (normalmente 5+)    |

---

### Caso de Estudio

Análisis de un escenario o situación compleja.

```json
{
  "preguntas": [
    {
      "tipo": "caso_estudio",
      "pregunta": "Analiza el siguiente caso:",
      "descripcion_caso": "Una empresa de tecnología está considerando implementar teletrabajo permanente. El 60% de empleados lo prefiere, pero la productividad ha bajado un 10%...",
      "pregunta_principal": "¿Qué decisión tomarías y por qué?",
      "puntos_evaluacion": [
        "análisis del problema",
        "solución propuesta",
        "justificación",
        "consideración de alternativas"
      ],
      "puntos": 10
    }
  ]
}
```

| Campo                | Tipo   | Descripción                         |
| -------------------- | ------ | ----------------------------------- |
| `tipo`               | string | Siempre `"caso_estudio"`            |
| `pregunta`           | string | Introducción al caso                |
| `descripcion_caso`   | string | Descripción detallada del escenario |
| `pregunta_principal` | string | La pregunta central a responder     |
| `puntos_evaluacion`  | array  | Criterios de evaluación             |
| `puntos`             | number | Puntos totales (normalmente 10)     |

---

## Comprensión Lectora (Idiomas)

### reading_comprehension

Texto con preguntas de opción múltiple.

```json
{
  "preguntas": [
    {
      "tipo": "reading_comprehension",
      "pregunta": "Read the text and answer the questions.",
      "metadata": {
        "idioma": "ingles",
        "texto_lectura": "Tom is a young hunter. Every morning, he goes to the forest to hunt deer. He prefers hunting early because the animals are more active. Last week, he caught a large deer...",
        "preguntas": [
          {
            "pregunta": "When does Tom prefer to hunt?",
            "opciones": [
              "A. In the evening",
              "B. In the morning",
              "C. At night",
              "D. In the afternoon"
            ],
            "respuesta_correcta": "B"
          },
          {
            "pregunta": "What animal does Tom hunt?",
            "opciones": ["A. Bears", "B. Rabbits", "C. Deer", "D. Birds"],
            "respuesta_correcta": "C"
          },
          {
            "pregunta": "Where does Tom go to hunt?",
            "opciones": [
              "A. The mountains",
              "B. The river",
              "C. The forest",
              "D. The beach"
            ],
            "respuesta_correcta": "C"
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

---

### reading_written

Texto con preguntas de respuesta escrita.

```json
{
  "preguntas": [
    {
      "tipo": "reading_written",
      "pregunta": "Read the following text and answer the questions",
      "metadata": {
        "idioma": "ingles",
        "texto_lectura": "Maria works as a software developer in a large company. She started programming when she was 15 years old...",
        "preguntas_comprension": [
          {
            "pregunta": "What is Maria's job?",
            "respuesta": "She is a software developer."
          },
          {
            "pregunta": "When did she start programming?",
            "respuesta": "When she was 15 years old."
          },
          {
            "pregunta": "Where does she work?",
            "respuesta": "In a large company."
          }
        ],
        "vocabulario_clave": ["software developer", "programming", "company"]
      },
      "respuesta_esperada": "Resumen de las respuestas correctas",
      "puntos": 4
    }
  ]
}
```

---

### reading_true_false

Texto con afirmaciones verdaderas/falsas que requieren justificación.

```json
{
  "preguntas": [
    {
      "tipo": "reading_true_false",
      "pregunta": "Read the text and determine if the statements are true or false. Justify your answer.",
      "metadata": {
        "idioma": "ingles",
        "texto_lectura": "The Amazon rainforest is the largest tropical rainforest in the world. It covers approximately 5.5 million square kilometers...",
        "afirmaciones": [
          {
            "texto": "The Amazon is the biggest tropical forest.",
            "es_verdadero": true,
            "justificacion": "The text states it is 'the largest tropical rainforest in the world'."
          },
          {
            "texto": "The Amazon covers less than 5 million square kilometers.",
            "es_verdadero": false,
            "justificacion": "The text says it covers 'approximately 5.5 million square kilometers'."
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

---

### reading_cloze

Completar texto con palabras de un banco.

```json
{
  "preguntas": [
    {
      "tipo": "reading_cloze",
      "pregunta": "Complete the text with the correct words from the word bank.",
      "metadata": {
        "idioma": "ingles",
        "texto_con_huecos": "Tom is a young hunter. Every {}, he hunts in the {}. He does not hunt at {} because it is too dangerous.",
        "respuestas": ["morning", "forest", "night"],
        "opciones_disponibles": [
          "morning",
          "forest",
          "night",
          "afternoon",
          "beach",
          "evening"
        ]
      },
      "puntos": 3
    }
  ]
}
```

**Nota:** Usa `{}` para marcar cada hueco en el texto.

---

### reading_skill

Evaluación de diferentes habilidades de lectura (idea principal, detalle, inferencia, propósito, tono).

```json
{
  "preguntas": [
    {
      "tipo": "reading_skill",
      "pregunta": "Read the text and answer the comprehension questions",
      "metadata": {
        "idioma": "ingles",
        "texto_lectura": "Climate change is one of the most pressing issues of our time. Scientists have been warning about rising temperatures for decades...",
        "preguntas_skill": [
          {
            "tipo_skill": "main_idea",
            "pregunta": "What is the main idea of the text?",
            "opciones": [
              "A. Scientists are always wrong",
              "B. Climate change is urgent",
              "C. Temperatures are stable",
              "D. The weather is nice"
            ],
            "respuesta_correcta": "B"
          },
          {
            "tipo_skill": "detail",
            "pregunta": "According to the text, who has been warning about this issue?",
            "opciones": [
              "A. Politicians",
              "B. Scientists",
              "C. Teachers",
              "D. Athletes"
            ],
            "respuesta_correcta": "B"
          },
          {
            "tipo_skill": "inference",
            "pregunta": "What can we infer from the text?",
            "opciones": [
              "A. Action is needed soon",
              "B. Nothing will change",
              "C. Scientists are uncertain",
              "D. The problem is solved"
            ],
            "respuesta_correcta": "A"
          },
          {
            "tipo_skill": "purpose",
            "pregunta": "What is the author's main purpose?",
            "opciones": [
              "A. To inform and warn",
              "B. To entertain",
              "C. To sell a product",
              "D. To confuse readers"
            ],
            "respuesta_correcta": "A"
          },
          {
            "tipo_skill": "tone",
            "pregunta": "What is the tone of the text?",
            "opciones": [
              "A. Humorous",
              "B. Casual",
              "C. Serious and concerned",
              "D. Indifferent"
            ],
            "respuesta_correcta": "C"
          }
        ]
      },
      "puntos": 5
    }
  ]
}
```

| Tipos de Skill | Descripción                      |
| -------------- | -------------------------------- |
| `main_idea`    | Identificar la idea principal    |
| `detail`       | Encontrar información específica |
| `inference`    | Deducir información no explícita |
| `purpose`      | Entender el propósito del autor  |
| `tone`         | Identificar el tono del texto    |

---

### reading_matching

Relacionar afirmaciones con párrafos.

```json
{
  "preguntas": [
    {
      "tipo": "reading_matching",
      "pregunta": "Match each sentence with the correct paragraph (A-D).",
      "metadata": {
        "idioma": "ingles",
        "parrafos": [
          {
            "letra": "A",
            "texto": "Tom is a young hunter who lives in a small village near the forest. He learned to hunt from his father when he was just 12 years old."
          },
          {
            "letra": "B",
            "texto": "Every morning, Tom wakes up before dawn. He prepares his equipment and walks to the forest. He usually spends 3-4 hours hunting."
          },
          {
            "letra": "C",
            "texto": "Tom never hunts at night because it is too dangerous. Wild animals are more aggressive after sunset, and visibility is poor."
          },
          {
            "letra": "D",
            "texto": "Despite the challenges, Tom loves his work. He feels connected to nature and proud of providing food for his family."
          }
        ],
        "oraciones": [
          {
            "texto": "This paragraph describes Tom's background and how he learned.",
            "parrafo_correcto": "A"
          },
          {
            "texto": "This paragraph explains Tom's daily routine.",
            "parrafo_correcto": "B"
          },
          {
            "texto": "This paragraph explains why Tom avoids hunting at certain times.",
            "parrafo_correcto": "C"
          },
          {
            "texto": "This paragraph shows Tom's feelings about his work.",
            "parrafo_correcto": "D"
          }
        ]
      },
      "puntos": 4
    }
  ]
}
```

---

### reading_sequence

Ordenar eventos cronológicamente según el texto.

```json
{
  "preguntas": [
    {
      "tipo": "reading_sequence",
      "pregunta": "Put the following events in the correct order according to the text.",
      "metadata": {
        "idioma": "ingles",
        "texto_narrativo": "Yesterday was a busy day for Sarah. First, she woke up at 6 AM and had breakfast. Then, she went to the gym for an hour. After exercising, she drove to work. She had a meeting at noon and finished working at 5 PM. Finally, she met her friends for dinner.",
        "eventos": [
          {
            "letra": "A",
            "texto": "Sarah met her friends for dinner.",
            "posicion_correcta": 6
          },
          {
            "letra": "B",
            "texto": "Sarah woke up and had breakfast.",
            "posicion_correcta": 1
          },
          {
            "letra": "C",
            "texto": "Sarah had a meeting.",
            "posicion_correcta": 4
          },
          {
            "letra": "D",
            "texto": "Sarah went to the gym.",
            "posicion_correcta": 2
          },
          {
            "letra": "E",
            "texto": "Sarah drove to work.",
            "posicion_correcta": 3
          },
          {
            "letra": "F",
            "texto": "Sarah finished working.",
            "posicion_correcta": 5
          }
        ]
      },
      "puntos": 5
    }
  ]
}
```

---

## Expresión Escrita (Idiomas)

### writing_short

Respuestas cortas a preguntas sobre un texto (niveles CEFR: A1-C2).

| Nivel | Longitud Respuesta      | Complejidad                 |
| ----- | ----------------------- | --------------------------- |
| A1    | 1-5 palabras            | Información explícita       |
| A2    | 1-5 palabras            | Presente/pasado simple      |
| B1    | 1-2 frases              | Conectar ideas (because/so) |
| B2    | 1-2 frases elaboradas   | Inferencia y reformulación  |
| C1    | 2-3 frases precisas     | Inferencias complejas       |
| C2    | 2-3 frases sofisticadas | Análisis de tono y matices  |

#### Ejemplo A1 (Principiante):

```json
{
  "preguntas": [
    {
      "tipo": "writing_short",
      "pregunta": "Read the text and answer the questions with short answers.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "A1",
        "texto_lectura": "Tom is a student. He is 18 years old. He lives in London.",
        "preguntas_short": [
          {
            "pregunta": "What is Tom?",
            "palabras_clave": ["student"],
            "respuesta_modelo": "A student."
          },
          {
            "pregunta": "How old is Tom?",
            "palabras_clave": ["18"],
            "respuesta_modelo": "18 years old."
          },
          {
            "pregunta": "Where does Tom live?",
            "palabras_clave": ["London"],
            "respuesta_modelo": "In London."
          }
        ]
      },
      "puntos": 2
    }
  ]
}
```

#### Ejemplo A2 (Elemental):

```json
{
  "preguntas": [
    {
      "tipo": "writing_short",
      "pregunta": "Read the text and answer the questions with short answers.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "A2",
        "texto_lectura": "Yesterday, Sarah went to the supermarket. She bought apples, bread, and milk. She spent 20 dollars.",
        "preguntas_short": [
          {
            "pregunta": "Where did Sarah go?",
            "palabras_clave": ["supermarket"],
            "respuesta_modelo": "To the supermarket."
          },
          {
            "pregunta": "What did she buy?",
            "palabras_clave": ["apples", "bread", "milk"],
            "respuesta_modelo": "Apples, bread, and milk."
          },
          {
            "pregunta": "How much did she spend?",
            "palabras_clave": ["20", "dollars"],
            "respuesta_modelo": "20 dollars."
          }
        ]
      },
      "puntos": 2
    }
  ]
}
```

#### Ejemplo B1 (Intermedio):

```json
{
  "preguntas": [
    {
      "tipo": "writing_short",
      "pregunta": "Read the text and answer the questions with short answers.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "B1",
        "texto_lectura": "Maria works from home three days a week. She prefers this arrangement because it allows her to spend more time with her family and avoid the long commute to the office.",
        "preguntas_short": [
          {
            "pregunta": "How many days does Maria work from home?",
            "palabras_clave": ["three", "days"],
            "respuesta_modelo": "Three days a week."
          },
          {
            "pregunta": "Why does Maria prefer working from home?",
            "palabras_clave": ["family", "commute", "time"],
            "respuesta_modelo": "Because she can spend more time with her family and avoid the long commute."
          }
        ]
      },
      "puntos": 2
    }
  ]
}
```

#### Ejemplo B2 (Intermedio Alto):

```json
{
  "preguntas": [
    {
      "tipo": "writing_short",
      "pregunta": "Read the text and answer the questions with short answers.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "B2",
        "texto_lectura": "Recent studies have shown that urban green spaces not only improve air quality but also contribute to residents' mental well-being. City planners are increasingly recognizing the value of parks and gardens in modern urban design.",
        "preguntas_short": [
          {
            "pregunta": "What benefits do green spaces provide according to the text?",
            "palabras_clave": ["air quality", "mental well-being"],
            "respuesta_modelo": "They improve air quality and contribute to residents' mental well-being."
          },
          {
            "pregunta": "How are city planners responding to this information?",
            "palabras_clave": ["recognizing", "value", "parks"],
            "respuesta_modelo": "They are increasingly recognizing the value of parks and gardens in urban design."
          }
        ]
      },
      "puntos": 2
    }
  ]
}
```

#### Ejemplo C1 (Avanzado):

```json
{
  "preguntas": [
    {
      "tipo": "writing_short",
      "pregunta": "Read the text and answer the questions with short answers.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "C1",
        "texto_lectura": "The paradigm shift in corporate governance has necessitated a more nuanced approach to stakeholder engagement. Companies are no longer judged solely on profitability but on their broader societal impact, prompting executives to reconsider traditional business models.",
        "preguntas_short": [
          {
            "pregunta": "What has caused companies to change their approach to stakeholder engagement?",
            "palabras_clave": ["paradigm shift", "corporate governance"],
            "respuesta_modelo": "The paradigm shift in corporate governance has necessitated a more nuanced approach."
          },
          {
            "pregunta": "How are companies now being evaluated differently?",
            "palabras_clave": ["societal impact", "profitability"],
            "respuesta_modelo": "They are judged not only on profitability but also on their broader societal impact, leading executives to reconsider traditional models."
          }
        ]
      },
      "puntos": 2
    }
  ]
}
```

#### Ejemplo C2 (Maestría):

```json
{
  "preguntas": [
    {
      "tipo": "writing_short",
      "pregunta": "Read the text and answer the questions with short answers.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "C2",
        "texto_lectura": "The author's subtle invocation of Proustian memory triggers serves to underscore the ephemeral nature of nostalgia. By juxtaposing fragmented recollections with visceral sensory details, she crafts a narrative that simultaneously celebrates and mourns the irretrievability of the past.",
        "preguntas_short": [
          {
            "pregunta": "What literary technique does the author employ to explore nostalgia?",
            "palabras_clave": [
              "Proustian",
              "memory triggers",
              "sensory details"
            ],
            "respuesta_modelo": "She subtly invokes Proustian memory triggers, juxtaposing fragmented recollections with visceral sensory details to underscore nostalgia's ephemeral nature."
          },
          {
            "pregunta": "What dual perspective does the narrative convey about the past?",
            "palabras_clave": ["celebrates", "mourns", "irretrievability"],
            "respuesta_modelo": "The narrative simultaneously celebrates and mourns the irretrievability of the past, creating a bittersweet meditation on memory."
          }
        ]
      },
      "puntos": 2
    }
  ]
}
```

---

### writing_paraphrase

Reescribir frases con diferentes palabras manteniendo el significado.

**Campos importantes:**

- **`instruccion`**: Indica **cómo debe transformarse** cada oración (ej: "Change to passive voice", "Use synonyms"). **Este campo se muestra en la interfaz** como instrucción destacada.
- **`pistas_parafraseo`**: Pistas adicionales opcionales para ayudar al estudiante. Se muestran antes de responder.
- **Diferencia**: `instruccion` es obligatoria (transformación requerida), `pistas_parafraseo` es opcional (ayudas).

| Nivel | Complejidad                                  | Estructuras                     |
| ----- | -------------------------------------------- | ------------------------------- |
| A1    | Sinónimos básicos de palabras sueltas        | Vocabulario básico              |
| A2    | Sinónimos simples en oraciones cortas        | Tiempos verbales básicos        |
| B1    | Cambios sintácticos simples                  | because → due to, activa/pasiva |
| B2    | Reestructuración con subordinadas            | Cláusulas relativas, gerundios  |
| C1    | Nominalización y registro formal             | Estructuras complejas           |
| C2    | Transformaciones sofisticadas y estilísticas | Matices y connotaciones         |

#### Ejemplo A1 (Principiante):

```json
{
  "preguntas": [
    {
      "tipo": "writing_paraphrase",
      "pregunta": "Rewrite using different words.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "A1",
        "oraciones_originales": [
          {
            "original": "The cat is big.",
            "instruccion": "Use synonym: 'big'→'large'",
            "pistas_parafraseo": "Try 'large'",
            "parafraseo_esperado": "The cat is large."
          },
          {
            "original": "I am happy.",
            "instruccion": "Use synonym: 'happy'→'glad'",
            "pistas_parafraseo": "Try 'glad'",
            "parafraseo_esperado": "I am glad."
          }
        ]
      },
      "puntos": 2
    }
  ]
}
```

#### Ejemplo A2 (Elemental):

```json
{
  "preguntas": [
    {
      "tipo": "writing_paraphrase",
      "pregunta": "Rewrite the sentences using different words.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "A2",
        "oraciones_originales": [
          {
            "original": "She walks to school every day.",
            "instruccion": "Use synonym: 'walks'→'goes on foot'",
            "pistas_parafraseo": "Try 'goes on foot'",
            "parafraseo_esperado": "She goes to school on foot every day."
          },
          {
            "original": "The book is very good.",
            "instruccion": "Use synonyms: 'very good'→'excellent'",
            "pistas_parafraseo": "Try 'excellent'",
            "parafraseo_esperado": "The book is excellent."
          }
        ]
      },
      "puntos": 2
    }
  ]
}
```

#### Ejemplo B1 (Intermedio):

```json
{
  "preguntas": [
    {
      "tipo": "writing_paraphrase",
      "pregunta": "Paraphrase the following sentences using different words.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "B1",
        "oraciones_originales": [
          {
            "original": "She stayed at home because she was sick.",
            "instruccion": "Change 'because' to 'due to' and use noun form",
            "pistas_parafraseo": "Convert 'she was sick' to a noun phrase",
            "parafraseo_esperado": "She stayed at home due to her illness."
          },
          {
            "original": "The movie was very interesting.",
            "instruccion": "Use synonyms: 'movie'→'film', 'interesting'→'fascinating'",
            "pistas_parafraseo": "Try 'film' and 'fascinating'",
            "parafraseo_esperado": "The film was quite fascinating."
          },
          {
            "original": "I can't understand this problem.",
            "instruccion": "Use formal language: 'can't'→'unable to', 'understand'→'comprehend'",
            "pistas_parafraseo": "Use 'unable to' and 'comprehend'",
            "parafraseo_esperado": "I'm unable to comprehend this issue."
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo B2 (Intermedio Alto):

```json
{
  "preguntas": [
    {
      "tipo": "writing_paraphrase",
      "pregunta": "Paraphrase the sentences using more sophisticated structures.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "B2",
        "oraciones_originales": [
          {
            "original": "Although he studied hard, he failed the exam.",
            "instruccion": "Use 'despite' with gerund",
            "pistas_parafraseo": "Try 'Despite studying...'",
            "parafraseo_esperado": "Despite studying hard, he failed the exam."
          },
          {
            "original": "The company implemented new policies to improve productivity.",
            "instruccion": "Use passive voice and 'in order to'",
            "pistas_parafraseo": "Try 'New policies were implemented...'",
            "parafraseo_esperado": "New policies were implemented by the company in order to enhance productivity."
          },
          {
            "original": "She didn't attend the meeting because she had another commitment.",
            "instruccion": "Use 'owing to' with noun phrase",
            "pistas_parafraseo": "Convert to 'owing to another commitment'",
            "parafraseo_esperado": "She didn't attend the meeting owing to another commitment."
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo C1 (Avanzado):

```json
{
  "preguntas": [
    {
      "tipo": "writing_paraphrase",
      "pregunta": "Paraphrase using advanced structures and formal register.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "C1",
        "oraciones_originales": [
          {
            "original": "The report suggests that environmental factors significantly influence consumer behavior.",
            "instruccion": "Use nominalization: 'influence'→'have an influence on'",
            "pistas_parafraseo": "Try 'exert a significant influence'",
            "parafraseo_esperado": "According to the report, environmental factors exert a significant influence on consumer behavior."
          },
          {
            "original": "We must address this issue immediately to prevent further complications.",
            "instruccion": "Use impersonal structure with 'imperative' and nominalization",
            "pistas_parafraseo": "Try 'It is imperative that...'",
            "parafraseo_esperado": "It is imperative that this issue be addressed immediately to forestall further complications."
          },
          {
            "original": "Many experts believe that technology will continue to transform education.",
            "instruccion": "Use 'widely held' and passive construction",
            "pistas_parafraseo": "Try 'It is widely held...'",
            "parafraseo_esperado": "It is widely held among experts that education will continue to be transformed by technology."
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo C2 (Maestría):

```json
{
  "preguntas": [
    {
      "tipo": "writing_paraphrase",
      "pregunta": "Paraphrase with stylistic sophistication while preserving nuance.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "C2",
        "oraciones_originales": [
          {
            "original": "The novelist's intricate narrative structure mirrors the fragmented nature of memory itself.",
            "instruccion": "Use inversion and sophisticated vocabulary",
            "pistas_parafraseo": "Try starting with 'Such is the intricacy...'",
            "parafraseo_esperado": "Such is the intricacy of the novelist's narrative structure that it echoes the very fragmentation inherent in human recollection."
          },
          {
            "original": "The policy has been criticized for failing to adequately address systemic inequalities.",
            "instruccion": "Use 'come under fire' and nominalization",
            "pistas_parafraseo": "Try 'The policy has come under fire for its inadequate...'",
            "parafraseo_esperado": "The policy has come under fire for its inadequate redress of systemic inequalities."
          },
          {
            "original": "Her research challenges conventional assumptions about cognitive development.",
            "instruccion": "Use 'call into question' and formal structure",
            "pistas_parafraseo": "Try 'Her research serves to call into question...'",
            "parafraseo_esperado": "Her research serves to call into question long-standing assumptions pertaining to cognitive development."
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

---

### writing_correction

Encontrar y corregir errores gramaticales.

| Nivel | Tipo de Error                       | Complejidad               |
| ----- | ----------------------------------- | ------------------------- |
| A1    | Errores básicos de verbo to be/have | Conjugación elemental     |
| A2    | Tiempos verbales simples            | Presente/pasado simple    |
| B1    | Auxiliares, presente perfecto       | Estructuras intermedias   |
| B2    | Voz pasiva, condicionales           | Estructuras complejas     |
| C1    | Subjuntivo, inversiones             | Estructuras avanzadas     |
| C2    | Matices de registro y coherencia    | Sofisticación estilística |

#### Ejemplo A1 (Principiante):

```json
{
  "preguntas": [
    {
      "tipo": "writing_correction",
      "pregunta": "Find and correct the errors.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "A1",
        "frases_con_errores": [
          {
            "frase_con_error": "She is student.",
            "correccion": "She is a student.",
            "tipo_error": "Artículo faltante",
            "pista": "Necesitas un artículo antes de 'student'"
          },
          {
            "frase_con_error": "I have 25 years old.",
            "correccion": "I am 25 years old.",
            "tipo_error": "Uso incorrecto de 'have' para edad",
            "pista": "Para la edad usamos 'am/is/are', no 'have'"
          },
          {
            "frase_con_error": "They is happy.",
            "correccion": "They are happy.",
            "tipo_error": "Conjugación de 'to be'",
            "pista": "Con 'They' usamos 'are'"
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo A2 (Elemental):

```json
{
  "preguntas": [
    {
      "tipo": "writing_correction",
      "pregunta": "Find and correct the errors in the sentences.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "A2",
        "frases_con_errores": [
          {
            "frase_con_error": "Yesterday I go to the beach.",
            "correccion": "Yesterday I went to the beach.",
            "tipo_error": "Tiempo verbal incorrecto",
            "pista": "Con 'yesterday' usamos pasado simple"
          },
          {
            "frase_con_error": "She don't like coffee.",
            "correccion": "She doesn't like coffee.",
            "tipo_error": "Auxiliar incorrecto en tercera persona",
            "pista": "Con 'she/he/it' usamos 'doesn't'"
          },
          {
            "frase_con_error": "There is two cats in the garden.",
            "correccion": "There are two cats in the garden.",
            "tipo_error": "Concordancia singular/plural",
            "pista": "Con plural usamos 'there are'"
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo B1 (Intermedio):

```json
{
  "preguntas": [
    {
      "tipo": "writing_correction",
      "pregunta": "Find and correct the errors in the following sentences.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "B1",
        "frases_con_errores": [
          {
            "frase_con_error": "She go to school every day.",
            "correccion": "She goes to school every day.",
            "tipo_error": "Conjugación verbal (tercera persona singular)",
            "pista": "Revisa la conjugación del verbo en tercera persona"
          },
          {
            "frase_con_error": "I am agree with you.",
            "correccion": "I agree with you.",
            "tipo_error": "Uso incorrecto de verbo auxiliar",
            "pista": "El verbo 'agree' no necesita auxiliar"
          },
          {
            "frase_con_error": "Yesterday I have finished my homework.",
            "correccion": "Yesterday I finished my homework.",
            "tipo_error": "Tiempo verbal incorrecto",
            "pista": "Con 'yesterday' usamos pasado simple, no presente perfecto"
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo B2 (Intermedio Alto):

```json
{
  "preguntas": [
    {
      "tipo": "writing_correction",
      "pregunta": "Identify and correct the grammatical errors.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "B2",
        "frases_con_errores": [
          {
            "frase_con_error": "If I would have known, I would have come earlier.",
            "correccion": "If I had known, I would have come earlier.",
            "tipo_error": "Condicional tipo 3 mal formado",
            "pista": "En la cláusula 'if' del tercer condicional usamos 'had + past participle'"
          },
          {
            "frase_con_error": "The house was building in 1990.",
            "correccion": "The house was built in 1990.",
            "tipo_error": "Participio pasado incorrecto en voz pasiva",
            "pista": "Necesitas el participio pasado 'built', no el gerundio"
          },
          {
            "frase_con_error": "She suggested me to take a break.",
            "correccion": "She suggested that I take a break.",
            "tipo_error": "Estructura incorrecta con 'suggest'",
            "pista": "'Suggest' va seguido de 'that + sujeto + verbo', no de objeto + infinitivo"
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo C1 (Avanzado):

```json
{
  "preguntas": [
    {
      "tipo": "writing_correction",
      "pregunta": "Correct the subtle grammatical and stylistic errors.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "C1",
        "frases_con_errores": [
          {
            "frase_con_error": "Rarely I have seen such dedication.",
            "correccion": "Rarely have I seen such dedication.",
            "tipo_error": "Inversión después de adverbio negativo",
            "pista": "Después de 'rarely' necesitas inversión: auxiliar + sujeto"
          },
          {
            "frase_con_error": "It is essential that she comes to the meeting.",
            "correccion": "It is essential that she come to the meeting.",
            "tipo_error": "Subjuntivo después de 'essential'",
            "pista": "Después de 'essential that' usamos forma base del verbo (subjuntivo)"
          },
          {
            "frase_con_error": "Having been late three times, the boss decided to fire him.",
            "correccion": "Having been late three times, he was fired by the boss.",
            "tipo_error": "Participio colgante (dangling participle)",
            "pista": "El sujeto del gerundio debe ser el mismo que el de la oración principal"
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo C2 (Maestría):

```json
{
  "preguntas": [
    {
      "tipo": "writing_correction",
      "pregunta": "Identify and correct errors in register, coherence, and sophistication.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "C2",
        "frases_con_errores": [
          {
            "frase_con_error": "The data clearly shows that the hypothesis is wrong.",
            "correccion": "The data clearly show that the hypothesis is incorrect.",
            "tipo_error": "Concordancia (data es plural) y registro formal",
            "pista": "'Data' es plural y en contexto académico 'incorrect' es más apropiado que 'wrong'"
          },
          {
            "frase_con_error": "Not only did she complete the project, but also exceeded expectations.",
            "correccion": "Not only did she complete the project, but she also exceeded expectations.",
            "tipo_error": "Estructura correlativa incompleta",
            "pista": "Necesitas incluir el sujeto 'she' después de 'but'"
          },
          {
            "frase_con_error": "The committee's decision, that was controversial, sparked debate.",
            "correccion": "The committee's decision, which was controversial, sparked debate.",
            "tipo_error": "Pronombre relativo no restrictivo",
            "pista": "Entre comas usa 'which' para cláusulas no restrictivas"
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

---

### writing_transformation

Transformar oraciones según instrucciones específicas.

| Nivel | Tipo de Transformación                    | Complejidad               |
| ----- | ----------------------------------------- | ------------------------- |
| A1    | Afirmativa ↔ Negativa                     | Estructuras básicas       |
| A2    | Singular ↔ Plural, presente ↔ pasado      | Tiempos verbales simples  |
| B1    | Activa ↔ Pasiva, afirmación ↔ pregunta    | Estructuras intermedias   |
| B2    | Estilo directo ↔ indirecto, condicionales | Subordinadas              |
| C1    | Nominalización, inversión                 | Estructuras avanzadas     |
| C2    | Registro formal/informal, matices         | Sofisticación estilística |

#### Ejemplo A1 (Principiante):

```json
{
  "preguntas": [
    {
      "tipo": "writing_transformation",
      "pregunta": "Transform the sentences.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "A1",
        "transformaciones": [
          {
            "original": "I am happy.",
            "instruccion": "Change to negative.",
            "transformacion_esperada": "I am not happy."
          },
          {
            "original": "She is a teacher.",
            "instruccion": "Change to a question.",
            "transformacion_esperada": "Is she a teacher?"
          },
          {
            "original": "They have a cat.",
            "instruccion": "Change to negative.",
            "transformacion_esperada": "They don't have a cat."
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo A2 (Elemental):

```json
{
  "preguntas": [
    {
      "tipo": "writing_transformation",
      "pregunta": "Transform the sentences according to the instructions.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "A2",
        "transformaciones": [
          {
            "original": "She goes to work by bus.",
            "instruccion": "Change to past simple.",
            "transformacion_esperada": "She went to work by bus."
          },
          {
            "original": "There is a book on the table.",
            "instruccion": "Change to plural.",
            "transformacion_esperada": "There are books on the table."
          },
          {
            "original": "He studies English every day.",
            "instruccion": "Change to a question.",
            "transformacion_esperada": "Does he study English every day?"
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo B1 (Intermedio):

```json
{
  "preguntas": [
    {
      "tipo": "writing_transformation",
      "pregunta": "Transform the sentences according to the instructions.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "B1",
        "transformaciones": [
          {
            "original": "She likes coffee.",
            "instruccion": "Change to negative.",
            "transformacion_esperada": "She doesn't like coffee."
          },
          {
            "original": "They built this house in 1990.",
            "instruccion": "Change to passive voice.",
            "transformacion_esperada": "This house was built in 1990."
          },
          {
            "original": "He can speak three languages.",
            "instruccion": "Change to a question.",
            "transformacion_esperada": "Can he speak three languages?"
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo B2 (Intermedio Alto):

```json
{
  "preguntas": [
    {
      "tipo": "writing_transformation",
      "pregunta": "Transform the sentences using complex structures.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "B2",
        "transformaciones": [
          {
            "original": "'I will arrive at 6 PM,' she said.",
            "instruccion": "Change to reported speech.",
            "transformacion_esperada": "She said that she would arrive at 6 PM."
          },
          {
            "original": "Study hard, and you will pass the exam.",
            "instruccion": "Rewrite using 'If' (first conditional).",
            "transformacion_esperada": "If you study hard, you will pass the exam."
          },
          {
            "original": "The company hired her because of her experience.",
            "instruccion": "Change to passive voice with 'owing to'.",
            "transformacion_esperada": "She was hired by the company owing to her experience."
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo C1 (Avanzado):

```json
{
  "preguntas": [
    {
      "tipo": "writing_transformation",
      "pregunta": "Transform using advanced structures.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "C1",
        "transformaciones": [
          {
            "original": "If I had studied harder, I would have passed.",
            "instruccion": "Rewrite using inversion (omit 'if').",
            "transformacion_esperada": "Had I studied harder, I would have passed."
          },
          {
            "original": "He rarely complains about his workload.",
            "instruccion": "Start with 'Rarely' and use inversion.",
            "transformacion_esperada": "Rarely does he complain about his workload."
          },
          {
            "original": "The team achieved success by working collaboratively.",
            "instruccion": "Use nominalization: 'achieved success'→'achievement'.",
            "transformacion_esperada": "The team's achievement resulted from collaborative work."
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo C2 (Maestría):

```json
{
  "preguntas": [
    {
      "tipo": "writing_transformation",
      "pregunta": "Transform with stylistic sophistication.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "C2",
        "transformaciones": [
          {
            "original": "It doesn't matter what she thinks about it.",
            "instruccion": "Use formal register with 'of little consequence'.",
            "transformacion_esperada": "Her opinion on the matter is of little consequence."
          },
          {
            "original": "The project failed because nobody planned it properly.",
            "instruccion": "Use cleft sentence starting with 'What' and nominalization.",
            "transformacion_esperada": "What led to the project's failure was inadequate planning."
          },
          {
            "original": "She almost never makes mistakes.",
            "instruccion": "Start with 'Seldom' with inversion and formal vocabulary.",
            "transformacion_esperada": "Seldom does she commit an error."
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

---

### writing_essay

Mini-ensayo sobre un tema dado.

| Nivel | Longitud         | Complejidad                               |
| ----- | ---------------- | ----------------------------------------- |
| A1    | 30-50 palabras   | Frases simples sobre temas personales     |
| A2    | 50-80 palabras   | Párrafos cortos con presente/pasado       |
| B1    | 80-120 palabras  | Estructura básica con conectores          |
| B2    | 120-180 palabras | Argumentación con ejemplos                |
| C1    | 180-250 palabras | Análisis con evidencia y contraargumentos |
| C2    | 250+ palabras    | Sofisticación estilística y retórica      |

#### Ejemplo A1 (Principiante):

```json
{
  "preguntas": [
    {
      "tipo": "writing_essay",
      "pregunta": "Write about yourself.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "A1",
        "tema_ensayo": "My family",
        "instrucciones": "Write 30-50 words. Use simple sentences.",
        "palabras_minimas": 30,
        "palabras_maximas": 50,
        "puntos_evaluacion": [
          "Vocabulario básico",
          "Oraciones completas",
          "Claridad"
        ],
        "modelo_respuesta": "I have a small family. My mother is a teacher. My father is a doctor. I have one brother. His name is Tom. We are happy."
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo A2 (Elemental):

```json
{
  "preguntas": [
    {
      "tipo": "writing_essay",
      "pregunta": "Write a short composition.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "A2",
        "tema_ensayo": "My last vacation",
        "instrucciones": "Write 50-80 words. Describe what you did.",
        "palabras_minimas": 50,
        "palabras_maximas": 80,
        "puntos_evaluacion": [
          "Uso de pasado simple",
          "Secuencia lógica",
          "Vocabulario"
        ],
        "modelo_respuesta": "Last summer, I went to the beach with my family. We stayed in a small hotel near the sea. Every day, we swam and played volleyball. The weather was sunny and hot. We ate fresh seafood at local restaurants. I took many photos. It was a wonderful vacation. I want to go back next year."
      },
      "puntos": 4
    }
  ]
}
```

#### Ejemplo B1 (Intermedio):

```json
{
  "preguntas": [
    {
      "tipo": "writing_essay",
      "pregunta": "Write a short essay about the following topic:",
      "metadata": {
        "idioma": "ingles",
        "nivel": "B1",
        "tema_ensayo": "The advantages and disadvantages of social media",
        "instrucciones": "Write approximately 100-120 words. Include an introduction, body, and conclusion.",
        "palabras_minimas": 80,
        "palabras_maximas": 140,
        "puntos_evaluacion": [
          "Estructura",
          "Coherencia",
          "Vocabulario",
          "Gramática"
        ],
        "modelo_respuesta": "Social media has become an essential part of modern life. On one hand, it allows people to connect with friends and family around the world instantly. We can share photos, news, and stay updated easily. However, social media also has some disadvantages. People spend too much time on their phones instead of talking face-to-face. Privacy is another concern because personal information can be shared without permission. In conclusion, while social media is useful for communication, we should use it responsibly and not let it control our lives."
      },
      "puntos": 5
    }
  ]
}
```

#### Ejemplo B2 (Intermedio Alto):

```json
{
  "preguntas": [
    {
      "tipo": "writing_essay",
      "pregunta": "Write an argumentative essay.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "B2",
        "tema_ensayo": "Should university education be free for all students?",
        "instrucciones": "Write 120-180 words. Present arguments for both sides and state your opinion.",
        "palabras_minimas": 120,
        "palabras_maximas": 180,
        "puntos_evaluacion": [
          "Estructura argumentativa",
          "Uso de conectores",
          "Vocabulario variado",
          "Gramática compleja"
        ],
        "modelo_respuesta": "The question of whether university education should be free is highly debatable. Supporters argue that free education would give everyone equal opportunities regardless of their financial background. This could lead to a more educated workforce and reduce inequality in society. Moreover, students wouldn't have to worry about student loans, allowing them to focus on their studies.\n\nHowever, opponents claim that free university education would place a heavy burden on taxpayers. They argue that universities need funding to maintain quality, and making education free might lead to overcrowded classrooms and reduced resources. Additionally, if everyone has a degree, its value in the job market might decrease.\n\nIn my opinion, while free education sounds ideal, a compromise would be better. Perhaps the government could subsidize education for low-income students while others pay reduced fees. This way, we can ensure accessibility without compromising quality."
      },
      "puntos": 5
    }
  ]
}
```

#### Ejemplo C1 (Avanzado):

```json
{
  "preguntas": [
    {
      "tipo": "writing_essay",
      "pregunta": "Write an analytical essay.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "C1",
        "tema_ensayo": "Analyze the impact of artificial intelligence on the labor market",
        "instrucciones": "Write 180-250 words. Include evidence, counterarguments, and a nuanced conclusion.",
        "palabras_minimas": 180,
        "palabras_maximas": 250,
        "puntos_evaluacion": [
          "Profundidad de análisis",
          "Uso de evidencia",
          "Contraargumentos",
          "Sofisticación lingüística"
        ],
        "modelo_respuesta": "The advent of artificial intelligence has precipitated considerable debate regarding its implications for employment. Proponents contend that AI will augment productivity and create new job categories that we cannot yet envision. Historical precedents support this view; the Industrial Revolution, while displacing agricultural workers, ultimately generated unprecedented economic growth and employment opportunities.\n\nNevertheless, critics argue that the pace of AI adoption is unprecedented, potentially outstripping society's capacity to adapt. Unlike previous technological revolutions, AI threatens not merely manual labor but cognitive tasks previously considered immune to automation. Studies suggest that up to 47% of current jobs face high automation risk within the next two decades.\n\nMoreover, the geographical and demographic distribution of these impacts warrants scrutiny. Low-skilled workers in developing economies may face disproportionate displacement, exacerbating existing inequalities. Conversely, those with technical expertise stand to benefit substantially.\n\nUltimately, the impact of AI on employment will largely depend on policy interventions. Governments must invest in retraining programs and consider frameworks such as universal basic income. Rather than viewing AI as an existential threat, we should recognize it as a catalyst for reimagining work itself, necessitating proactive adaptation rather than reactive resistance."
      },
      "puntos": 5
    }
  ]
}
```

#### Ejemplo C2 (Maestría):

```json
{
  "preguntas": [
    {
      "tipo": "writing_essay",
      "pregunta": "Write a sophisticated analytical essay.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "C2",
        "tema_ensayo": "Examine the tension between individual freedom and collective responsibility in pandemic response",
        "instrucciones": "Write 250+ words. Demonstrate rhetorical sophistication, nuanced argumentation, and stylistic mastery.",
        "palabras_minimas": 250,
        "palabras_maximas": 350,
        "puntos_evaluacion": [
          "Sofisticación retórica",
          "Complejidad conceptual",
          "Matices argumentativos",
          "Maestría estilística"
        ],
        "modelo_respuesta": "The pandemic exposed a fundamental tension in liberal democracies: the delicate equilibrium between individual autonomy and collective welfare. This dichotomy, while philosophically perennial, acquired unprecedented urgency when personal choices regarding masking and vaccination bore direct epidemiological consequences for entire communities.\n\nLibertarian perspectives emphasize the inviolability of bodily autonomy, arguing that coercive public health measures represent governmental overreach antithetical to foundational principles of personal freedom. Such views, rooted in Millian harm principles, contend that the state's authority extends only to preventing direct harm to others, not to mandating protective behaviors, however socially beneficial.\n\nConversely, communitarian frameworks privilege collective well-being, asserting that individual rights exist within, not apart from, social contexts. From this vantage, refusing vaccination or masking constitutes a breach of civic duty, undermining the very fabric of mutual obligation upon which society depends. The analogy to military conscription is instructive, albeit imperfect: both invoke sacrifice for communal preservation.\n\nYet this binary framing obscures nuance. The pandemic revealed that 'freedom' itself is multifaceted. The immunocompromised, children, and elderly experienced restrictions on their freedom of movement and social interaction due to others' choices. Whose freedom takes precedence?\n\nMoreover, state capacity and legitimacy critically mediate this tension. Democracies with robust social safety nets and high institutional trust navigated mandates with less friction than those lacking such foundations. This suggests the debate transcends mere principle, implicating practical questions of governance, trust, and social solidarity.\n\nUltimately, the pandemic underscores that freedom and responsibility are not antithetical but interdependent. Sustainable liberty requires recognizing that our choices reverberate beyond ourselves, demanding a civic ethos that balances autonomy with accountability."
      },
      "puntos": 5
    }
  ]
}
```

---

### sentence_builder

Ordenar palabras para formar oraciones correctas.

| Nivel | Complejidad                                      | Estructuras                        |
| ----- | ------------------------------------------------ | ---------------------------------- |
| A1    | Oraciones simples, 3-5 palabras                  | Sujeto + verbo + complemento       |
| A2    | Oraciones simples con tiempo verbal básico       | Presente/pasado simple             |
| B1    | Oraciones con conectores y complementos          | Presente perfecto, voz pasiva      |
| B2    | Oraciones complejas con subordinadas             | Condicionales, cláusulas relativas |
| C1    | Oraciones sofisticadas con estructuras avanzadas | Subjuntivo, inversión              |
| C2    | Oraciones muy complejas con matices y estilo     | Estructuras idiomáticas complejas  |

#### Ejemplo A1 (Principiante):

```json
{
  "preguntas": [
    {
      "tipo": "sentence_builder",
      "pregunta": "Put the words in the correct order to form sentences.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "A1",
        "oraciones": [
          {
            "palabras_desordenadas": ["I", "am", "student", "a"],
            "respuesta_correcta": "I am a student.",
            "traduccion": "Yo soy un estudiante."
          },
          {
            "palabras_desordenadas": ["she", "happy", "is"],
            "respuesta_correcta": "She is happy.",
            "traduccion": "Ella está feliz."
          },
          {
            "palabras_desordenadas": ["like", "I", "pizza"],
            "respuesta_correcta": "I like pizza.",
            "traduccion": "Me gusta la pizza."
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo A2 (Elemental):

```json
{
  "preguntas": [
    {
      "tipo": "sentence_builder",
      "pregunta": "Put the words in the correct order to form sentences.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "A2",
        "oraciones": [
          {
            "palabras_desordenadas": ["yesterday", "I", "to", "went", "school"],
            "respuesta_correcta": "I went to school yesterday.",
            "traduccion": "Ayer fui a la escuela."
          },
          {
            "palabras_desordenadas": ["she", "watching", "is", "TV", "now"],
            "respuesta_correcta": "She is watching TV now.",
            "traduccion": "Ella está viendo la televisión ahora."
          },
          {
            "palabras_desordenadas": [
              "they",
              "play",
              "football",
              "every",
              "Sunday"
            ],
            "respuesta_correcta": "They play football every Sunday.",
            "traduccion": "Ellos juegan fútbol todos los domingos."
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo B1 (Intermedio):

```json
{
  "preguntas": [
    {
      "tipo": "sentence_builder",
      "pregunta": "Put the words in the correct order to form sentences.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "B1",
        "oraciones": [
          {
            "palabras_desordenadas": [
              "the",
              "cat",
              "is",
              "sleeping",
              "on",
              "sofa",
              "the"
            ],
            "respuesta_correcta": "The cat is sleeping on the sofa.",
            "traduccion": "El gato está durmiendo en el sofá."
          },
          {
            "palabras_desordenadas": [
              "I",
              "yesterday",
              "went",
              "shopping",
              "to",
              "mall",
              "the"
            ],
            "respuesta_correcta": "I went shopping to the mall yesterday.",
            "traduccion": "Fui de compras al centro comercial ayer."
          },
          {
            "palabras_desordenadas": [
              "she",
              "English",
              "speaks",
              "fluently",
              "very"
            ],
            "respuesta_correcta": "She speaks English very fluently.",
            "traduccion": "Ella habla inglés muy fluidamente."
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo B2 (Intermedio Alto):

```json
{
  "preguntas": [
    {
      "tipo": "sentence_builder",
      "pregunta": "Put the words in the correct order to form sentences.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "B2",
        "oraciones": [
          {
            "palabras_desordenadas": [
              "If",
              "I",
              "had",
              "known",
              "I",
              "would",
              "have",
              "come",
              "earlier"
            ],
            "respuesta_correcta": "If I had known, I would have come earlier.",
            "traduccion": "Si lo hubiera sabido, habría venido antes."
          },
          {
            "palabras_desordenadas": [
              "The",
              "book",
              "which",
              "I",
              "bought",
              "yesterday",
              "is",
              "very",
              "interesting"
            ],
            "respuesta_correcta": "The book which I bought yesterday is very interesting.",
            "traduccion": "El libro que compré ayer es muy interesante."
          },
          {
            "palabras_desordenadas": [
              "Despite",
              "being",
              "tired",
              "she",
              "continued",
              "working"
            ],
            "respuesta_correcta": "Despite being tired, she continued working.",
            "traduccion": "A pesar de estar cansada, continuó trabajando."
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo C1 (Avanzado):

```json
{
  "preguntas": [
    {
      "tipo": "sentence_builder",
      "pregunta": "Put the words in the correct order to form sentences.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "C1",
        "oraciones": [
          {
            "palabras_desordenadas": [
              "Had",
              "I",
              "known",
              "about",
              "the",
              "consequences",
              "I",
              "would",
              "never",
              "have",
              "agreed"
            ],
            "respuesta_correcta": "Had I known about the consequences, I would never have agreed.",
            "traduccion": "Si hubiera sabido sobre las consecuencias, nunca habría aceptado."
          },
          {
            "palabras_desordenadas": [
              "Not",
              "only",
              "did",
              "she",
              "finish",
              "the",
              "project",
              "but",
              "she",
              "also",
              "exceeded",
              "expectations"
            ],
            "respuesta_correcta": "Not only did she finish the project, but she also exceeded expectations.",
            "traduccion": "No solo terminó el proyecto, sino que también superó las expectativas."
          },
          {
            "palabras_desordenadas": [
              "It",
              "is",
              "imperative",
              "that",
              "we",
              "address",
              "this",
              "issue",
              "immediately"
            ],
            "respuesta_correcta": "It is imperative that we address this issue immediately.",
            "traduccion": "Es imperativo que abordemos este asunto inmediatamente."
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo C2 (Maestría):

```json
{
  "preguntas": [
    {
      "tipo": "sentence_builder",
      "pregunta": "Put the words in the correct order to form sentences.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "C2",
        "oraciones": [
          {
            "palabras_desordenadas": [
              "Scarcely",
              "had",
              "the",
              "ceremony",
              "begun",
              "when",
              "it",
              "started",
              "to",
              "rain",
              "torrentially"
            ],
            "respuesta_correcta": "Scarcely had the ceremony begun when it started to rain torrentially.",
            "traduccion": "Apenas había comenzado la ceremonia cuando empezó a llover torrencialmente."
          },
          {
            "palabras_desordenadas": [
              "Were",
              "it",
              "not",
              "for",
              "his",
              "unwavering",
              "determination",
              "the",
              "project",
              "would",
              "have",
              "faltered"
            ],
            "respuesta_correcta": "Were it not for his unwavering determination, the project would have faltered.",
            "traduccion": "Si no fuera por su determinación inquebrantable, el proyecto habría fracasado."
          },
          {
            "palabras_desordenadas": [
              "The",
              "more",
              "meticulously",
              "one",
              "plans",
              "the",
              "less",
              "likely",
              "unforeseen",
              "complications",
              "are",
              "to",
              "arise"
            ],
            "respuesta_correcta": "The more meticulously one plans, the less likely unforeseen complications are to arise.",
            "traduccion": "Cuanto más meticulosamente se planifica, menos probable es que surjan complicaciones imprevistas."
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

---

### formal_email

Escribir un email formal según una situación.

| Nivel | Tipo de Email                    | Complejidad               |
| ----- | -------------------------------- | ------------------------- |
| A1    | Email muy básico (saludo/cierre) | Fórmulas simples          |
| A2    | Solicitud simple                 | Frases directas           |
| B1    | Queja/solicitud                  | Estructura funcional      |
| B2    | Correspondencia profesional      | Registro formal apropiado |
| C1    | Email corporativo complejo       | Tono diplomático          |
| C2    | Comunicación ejecutiva           | Sofisticación retórica    |

#### Ejemplo A1 (Principiante):

```json
{
  "preguntas": [
    {
      "tipo": "formal_email",
      "pregunta": "Write a short email.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "A1",
        "nivel_cefr": "A1",
        "config_nivel": {
          "descripcion": "Email muy básico",
          "tipo_email": "Presentación simple",
          "longitud_esperada": "30-50 palabras",
          "palabras_aprox": 40
        },
        "situacion": {
          "quien_escribe": "Un nuevo estudiante",
          "destinatario": "Tu profesor",
          "proposito": "Presentarte y decir hola",
          "contexto": "Es tu primer día de clase"
        },
        "estructura_esperada": [
          "Dear [name]",
          "Simple introduction",
          "Basic closing"
        ],
        "formulas_utiles": ["My name is...", "I am...", "Thank you"]
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo A2 (Elemental):

```json
{
  "preguntas": [
    {
      "tipo": "formal_email",
      "pregunta": "Write a simple email request.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "A2",
        "nivel_cefr": "A2",
        "config_nivel": {
          "descripcion": "Solicitud simple",
          "tipo_email": "Pedir información",
          "longitud_esperada": "50-70 palabras",
          "palabras_aprox": 60
        },
        "situacion": {
          "quien_escribe": "Un estudiante",
          "destinatario": "La biblioteca de la universidad",
          "proposito": "Preguntar sobre el horario de apertura",
          "contexto": "Necesitas estudiar este fin de semana"
        },
        "estructura_esperada": [
          "Greeting",
          "Question",
          "Thank you and closing"
        ],
        "formulas_utiles": [
          "I would like to know...",
          "Could you tell me...",
          "Thank you for your help"
        ]
      },
      "puntos": 4
    }
  ]
}
```

#### Ejemplo B1 (Intermedio):

```json
{
  "preguntas": [
    {
      "tipo": "formal_email",
      "pregunta": "Write a formal email.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "B1",
        "nivel_cefr": "B1",
        "config_nivel": {
          "descripcion": "Email formal funcional",
          "tipo_email": "Queja o solicitud con explicación",
          "longitud_esperada": "80-120 palabras",
          "palabras_aprox": 100
        },
        "situacion": {
          "quien_escribe": "Un cliente insatisfecho",
          "destinatario": "El departamento de atención al cliente",
          "proposito": "Quejarse por un producto defectuoso y solicitar reembolso",
          "contexto": "Compraste un teléfono hace 2 semanas que dejó de funcionar"
        },
        "estructura_esperada": [
          "Greeting formal",
          "Opening purpose",
          "Explanation/details",
          "Polite closing"
        ],
        "formulas_utiles": [
          "I am writing to...",
          "I would appreciate...",
          "I look forward to hearing from you."
        ]
      },
      "puntos": 5
    }
  ]
}
```

#### Ejemplo B2 (Intermedio Alto):

```json
{
  "preguntas": [
    {
      "tipo": "formal_email",
      "pregunta": "Write a professional email.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "B2",
        "nivel_cefr": "B2",
        "config_nivel": {
          "descripcion": "Correspondencia profesional",
          "tipo_email": "Solicitud de reunión o propuesta",
          "longitud_esperada": "120-180 palabras",
          "palabras_aprox": 150
        },
        "situacion": {
          "quien_escribe": "Un gerente de proyecto",
          "destinatario": "Un cliente potencial",
          "proposito": "Proponer una reunión para discutir colaboración",
          "contexto": "Tu empresa ofrece servicios de consultoría que podrían beneficiar al cliente"
        },
        "estructura_esperada": [
          "Formal greeting",
          "Introduction and context",
          "Proposal/request",
          "Benefits/details",
          "Call to action",
          "Professional closing"
        ],
        "formulas_utiles": [
          "I am writing to propose...",
          "We would be delighted to discuss...",
          "Should you require any further information...",
          "We look forward to the possibility of..."
        ]
      },
      "puntos": 5
    }
  ]
}
```

#### Ejemplo C1 (Avanzado):

```json
{
  "preguntas": [
    {
      "tipo": "formal_email",
      "pregunta": "Write a diplomatic corporate email.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "C1",
        "nivel_cefr": "C1",
        "config_nivel": {
          "descripcion": "Comunicación corporativa compleja",
          "tipo_email": "Negociación o respuesta a situación delicada",
          "longitud_esperada": "180-250 palabras",
          "palabras_aprox": 210
        },
        "situacion": {
          "quien_escribe": "Un director de operaciones",
          "destinatario": "Un socio estratégico insatisfecho",
          "proposito": "Responder a quejas sobre retrasos en entrega y proponer solución",
          "contexto": "Ha habido retrasos significativos que han afectado el negocio del socio"
        },
        "estructura_esperada": [
          "Formal acknowledgment",
          "Empathetic understanding",
          "Explanation (without excuses)",
          "Proposed solution",
          "Commitment to improvement",
          "Diplomatic closing"
        ],
        "formulas_utiles": [
          "Thank you for bringing this matter to our attention",
          "We understand the inconvenience this has caused",
          "We are implementing measures to ensure...",
          "We value our partnership and remain committed to..."
        ]
      },
      "puntos": 5
    }
  ]
}
```

#### Ejemplo C2 (Maestría):

```json
{
  "preguntas": [
    {
      "tipo": "formal_email",
      "pregunta": "Write an executive-level communication.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "C2",
        "nivel_cefr": "C2",
        "config_nivel": {
          "descripcion": "Comunicación ejecutiva de alto nivel",
          "tipo_email": "Comunicado estratégico o negociación compleja",
          "longitud_esperada": "250-350 palabras",
          "palabras_aprox": 300
        },
        "situacion": {
          "quien_escribe": "CEO de una empresa tecnológica",
          "destinatario": "Junta directiva y principales accionistas",
          "proposito": "Comunicar decisión estratégica de reestructuración y fusionar con competidor",
          "contexto": "Decisión controversial que requiere comunicación persuasiva y transparente"
        },
        "estructura_esperada": [
          "Executive summary",
          "Strategic rationale",
          "Market analysis",
          "Addressing concerns",
          "Implementation timeline",
          "Call for support",
          "Authoritative closing"
        ],
        "formulas_utiles": [
          "I am writing to apprise you of a strategic decision...",
          "After careful deliberation and comprehensive market analysis...",
          "This merger represents a pivotal opportunity to...",
          "While we acknowledge the concerns that such a transition may engender...",
          "We remain steadfast in our commitment to driving shareholder value"
        ]
      },
      "puntos": 5
    }
  ]
}
```

---

### picture_description

Describir una imagen en el idioma objetivo. Incluye prompt para generar la imagen con IA.

**Nota:** El campo `prompt_generacion` se puede usar con DALL-E, Midjourney o Stable Diffusion para generar la imagen.

| Nivel | Oraciones | Complejidad                             |
| ----- | --------- | --------------------------------------- |
| A1    | 3-4       | Vocabulario básico, presente simple     |
| A2    | 4-5       | Presente continuo, descripciones        |
| B1    | 5-6       | Detalles, opiniones, conectores         |
| B2    | 6-8       | Inferencias, análisis, vocabulario rico |
| C1    | 8-10      | Interpretación, contexto cultural       |
| C2    | 10+       | Análisis crítico, matices, simbolismo   |

#### Ejemplo A1 (Principiante):

```json
{
  "preguntas": [
    {
      "tipo": "picture_description",
      "pregunta": "Describe the image in 3-4 simple sentences.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "A1",
        "prompt_generacion": "A simple park scene with a tree, a bench, and a blue sky. One person sitting on the bench. Sunny day.",
        "que_describir": [
          "What do you see?",
          "Where is it?",
          "What is the weather?"
        ],
        "oraciones_minimas": 3,
        "descripcion_modelo": "This is a park. There is a tree and a bench. A person is sitting on the bench. The sky is blue and sunny."
      },
      "puntos": 3
    }
  ]
}
```

#### Ejemplo A2 (Elemental):

```json
{
  "preguntas": [
    {
      "tipo": "picture_description",
      "pregunta": "Describe what you see in 4-5 sentences.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "A2",
        "prompt_generacion": "A family having a picnic in a park. Four people: parents and two children. They are eating sandwiches. There are trees and grass. Nice weather.",
        "que_describir": [
          "Who do you see?",
          "What are they doing?",
          "Where are they?",
          "What is the weather like?"
        ],
        "oraciones_minimas": 4,
        "descripcion_modelo": "The picture shows a family in a park. There are four people: two parents and two children. They are having a picnic and eating sandwiches. The weather is nice and sunny. There are trees and green grass around them."
      },
      "puntos": 4
    }
  ]
}
```

#### Ejemplo B1 (Intermedio):

```json
{
  "preguntas": [
    {
      "tipo": "picture_description",
      "pregunta": "Describe the image in 5-6 sentences.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "B1",
        "prompt_generacion": "A modern office space with 4-5 people working at desks with computers. Natural light from large windows. Some people talking, one person drinking coffee. Clean, minimalist design with plants.",
        "que_describir": [
          "¿Qué ves?",
          "¿Quiénes están?",
          "¿Qué están haciendo?",
          "¿Dónde están?",
          "¿Cómo es el ambiente?"
        ],
        "oraciones_minimas": 5,
        "descripcion_modelo": "The picture shows a modern office with several people working. There are about five employees sitting at their desks with computers. Natural light comes through large windows, making the space bright and pleasant. Some people are talking to each other, and one person is drinking coffee. The office has a minimalist design with plants, which creates a calm and professional atmosphere."
      },
      "puntos": 5
    }
  ]
}
```

#### Ejemplo B2 (Intermedio Alto):

```json
{
  "preguntas": [
    {
      "tipo": "picture_description",
      "pregunta": "Describe and analyze the image in 6-8 sentences.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "B2",
        "prompt_generacion": "A busy urban street at night with neon signs, street vendors, and diverse people walking. Asian city atmosphere. Reflections on wet pavement. Mix of traditional and modern architecture.",
        "que_describir": [
          "Describe the setting and atmosphere",
          "What activities are taking place?",
          "What contrast do you notice?",
          "What impression does it create?"
        ],
        "oraciones_minimas": 6,
        "descripcion_modelo": "The image depicts a vibrant urban street scene at night, likely in an Asian city. Numerous neon signs illuminate the street, casting colorful reflections on the wet pavement below. Street vendors can be seen selling their goods while diverse groups of people walk along the bustling sidewalk. The architecture presents an interesting contrast between traditional storefronts and modern buildings, suggesting the coexistence of old and new. The atmosphere appears energetic and dynamic, typical of major metropolitan areas. Despite the late hour, the street remains crowded and lively. The wet pavement indicates recent rain, which adds to the atmospheric quality of the scene. Overall, the image captures the essence of urban nightlife in a contemporary Asian city."
      },
      "puntos": 5
    }
  ]
}
```

#### Ejemplo C1 (Avanzado):

```json
{
  "preguntas": [
    {
      "tipo": "picture_description",
      "pregunta": "Provide a detailed analysis of the image in 8-10 sentences.",
      "metadata": {
        "idioma": "ingles",
        "nivel": "C1",
        "prompt_generacion": "An abandoned industrial building with broken windows, overgrown vegetation reclaiming the space. Graffiti art on walls. Contrast between decay and nature. Golden hour lighting creating dramatic atmosphere.",
        "que_describir": [
          "Analyze the visual elements and composition",
          "Interpret the symbolism and meaning",
          "Discuss the emotional impact",
          "Consider broader social or cultural implications"
        ],
        "oraciones_minimas": 8,
        "descripcion_modelo": "The photograph captures a hauntingly beautiful abandoned industrial building, its weathered facade testament to the passage of time. Broken windows punctuate the structure, allowing nature to gradually reclaim the space as vegetation weaves through the deteriorating infrastructure. Vibrant graffiti art adorns the walls, transforming the derelict space into an unofficial canvas for urban expression. The golden hour lighting bathes the scene in warm tones, creating a striking juxtaposition between the decay of human construction and the persistent vitality of nature. This image serves as a powerful meditation on impermanence and the cyclical relationship between civilization and the natural world. The graffiti, while technically vandalism, adds layers of meaning—representing both rebellion against abandonment and an attempt to reclaim and repurpose forgotten spaces. The composition evokes conflicting emotions: melancholy at what has been lost, yet appreciation for nature's resilience. Such scenes are increasingly common in post-industrial cities, symbolizing economic shifts and the transient nature of human endeavors. The photographer's choice of lighting elevates what could be mere documentation into a contemplative work that invites viewers to reflect on themes of renewal, entropy, and the persistent human impulse to create meaning even amid ruins."
      },
      "puntos": 5
    }
  ]
}
```

#### Ejemplo C2 (Maestría):

```json
{
  "preguntas": [
    {
      "tipo": "picture_description",
      "pregunta": "Provide a sophisticated critical analysis of the image (10+ sentences).",
      "metadata": {
        "idioma": "ingles",
        "nivel": "C2",
        "prompt_generacion": "A thought-provoking art installation: hundreds of suspended chairs at different heights in a white gallery space. Some chairs face each other, others are isolated. Dramatic lighting creating shadows. Visitors viewing from below. Conceptual contemporary art.",
        "que_describir": [
          "Analyze the artistic intent and conceptual framework",
          "Examine the use of space, light, and symbolism",
          "Interpret multiple possible meanings",
          "Contextualize within contemporary art discourse",
          "Evaluate the emotional and intellectual impact"
        ],
        "oraciones_minimas": 10,
        "descripcion_modelo": "The installation before us represents a paradigmatic example of contemporary conceptual art, wherein the mundane object—the chair—is defamiliarized through displacement and repetition, compelling viewers to reconsider its inherent symbolism. Hundreds of chairs suspended at varying heights throughout the gallery space create a three-dimensional constellation that disrupts conventional spatial hierarchies and invites contemplation of human connection, isolation, and social structures. The deliberate positioning of chairs facing one another suggests dialogue and relationship, while isolated units evoke alienation and solitude—a dialectic central to the human condition. The artist's choice of the chair as medium is particularly evocative; chairs are fundamentally designed for human rest and congregation, yet their suspension renders them inaccessible, creating a tension between function and dysfunction, presence and absence. Dramatic lighting amplifies this tension, casting fragmented shadows that multiply the installation's visual complexity while perhaps alluding to the ways individuals project versions of themselves in social contexts. The pristine white gallery space serves not merely as neutral backdrop but as conceptual void, emphasizing the objects' displacement from quotidian contexts and forcing us to engage with them as pure signifiers rather than utilitarian artifacts. Visitors viewing from below experience a disorienting shift in perspective, perhaps evoking feelings of insignificance or wonder—an embodied critique of power structures where individuals navigate systems beyond their control. This work resonates with broader discourses in contemporary art regarding participation, spectatorship, and the democratization of meaning-making; viewers become active interpreters rather than passive consumers. The installation's refusal of singular interpretation exemplifies postmodern aesthetic strategies, wherein meaning proliferates rather than coheres, challenging enlightenment assumptions about art's didactic function. Ultimately, this piece succeeds not merely as visual spectacle but as catalyst for philosophical inquiry into fundamental questions of belonging, agency, and the precarious nature of human interconnection in an increasingly fragmented world. The suspended chairs become metaphors for suspended lives—caught between connection and isolation, grounded reality and transcendent aspiration."
      },
      "puntos": 5
    }
  ]
}
```

---

## Ejercicios "Libre" (Sin Tema Predefinido)

Estos ejercicios son versiones libres de los anteriores, donde ChatGPT elige el tema.

### sentence_builder_libre

Construir oraciones a partir de palabras clave dadas (sin tema fijo).

```json
{
  "preguntas": [
    {
      "tipo": "sentence_builder_libre",
      "pregunta": "Build correct sentences using the given words. You can conjugate verbs and add necessary articles/prepositions.",
      "metadata": {
        "idioma": "ingles",
        "es_libre": true,
        "items": [
          {
            "palabras_clave": ["she", "read", "book"],
            "contexto_pista": "Describe what a woman is doing right now.",
            "oracion_esperada": "She is reading a book."
          },
          {
            "palabras_clave": ["they", "go", "park", "yesterday"],
            "contexto_pista": "Talk about a past visit to a public place.",
            "oracion_esperada": "They went to the park yesterday."
          },
          {
            "palabras_clave": ["he", "play", "guitar", "every", "evening"],
            "contexto_pista": "Describe someone's regular musical hobby.",
            "oracion_esperada": "He plays the guitar every evening."
          }
        ]
      },
      "puntos": 3
    }
  ]
}
```

| Campo              | Descripción                                 |
| ------------------ | ------------------------------------------- |
| `palabras_clave`   | Palabras que el estudiante debe usar        |
| `contexto_pista`   | Orientación sobre qué tipo de oración crear |
| `oracion_esperada` | Ejemplo de oración correcta                 |

---

### writing_short_libre

Respuestas cortas sin tema predefinido (ChatGPT elige tema variado).

```json
{
  "preguntas": [
    {
      "tipo": "writing_short_libre",
      "pregunta": "Lee el texto y responde las preguntas:",
      "metadata": {
        "idioma": "ingles",
        "es_libre": true,
        "titulo_tema": "Space Exploration",
        "texto_lectura": "NASA recently announced a new mission to Mars. The spacecraft will carry advanced equipment to search for signs of ancient life...",
        "preguntas_short": [
          {
            "pregunta": "What is NASA planning?",
            "palabras_clave": ["mission", "Mars"],
            "respuesta_modelo": "NASA is planning a new mission to Mars."
          },
          {
            "pregunta": "What will the spacecraft search for?",
            "palabras_clave": ["signs", "life", "ancient"],
            "respuesta_modelo": "It will search for signs of ancient life."
          }
        ]
      },
      "puntos": 2
    }
  ]
}
```

---

### writing_paraphrase_libre

Parafraseo con temas variados elegidos por ChatGPT.

```json
{
  "preguntas": [
    {
      "tipo": "writing_paraphrase_libre",
      "pregunta": "Parafrasea las siguientes oraciones:",
      "metadata": {
        "idioma": "ingles",
        "es_libre": true,
        "titulo_tema": "Technology and Daily Life",
        "instrucciones_parafraseo": "Usa sinónimos y cambia la estructura sin cambiar el significado.",
        "tecnicas_parafraseo": [
          "Usa sinónimos",
          "Cambia el orden",
          "Usa expresiones equivalentes"
        ],
        "oraciones_originales": [
          {
            "original": "Smartphones have revolutionized how we communicate.",
            "instruccion": "Use synonym 'transform' and passive causative structure",
            "parafraseo_esperado": "Mobile phones have transformed our communication methods.",
            "pistas_parafraseo": "Try using 'transform' instead of 'revolutionize'."
          },
          {
            "original": "Many people prefer online shopping because it saves time.",
            "instruccion": "Change 'because' to 'as' and restructure with adjective",
            "parafraseo_esperado": "Online shopping is popular as it is more time-efficient.",
            "pistas_parafraseo": "Try restructuring with 'as' instead of 'because'."
          }
        ]
      },
      "puntos": 2
    }
  ]
}
```

**Campos importantes:**

- **`instruccion`**: Indica la **transformación específica** que debe hacer el estudiante en cada oración (ej: "Use synonym 'transform' and passive causative structure"). **Se muestra en la interfaz** como instrucción destacada.
- **`pistas_parafraseo`**: Pistas adicionales opcionales para ayudar (ej: "Try using 'transform' instead of 'revolutionize'"). Se muestran antes de responder.
- **`titulo_tema`**: Tema contextual opcional para dar coherencia a las oraciones (ej: "Technology and Daily Life").

---

### writing_correction_libre

Corrección de errores con frases sobre temas variados.

```json
{
  "preguntas": [
    {
      "tipo": "writing_correction_libre",
      "pregunta": "Find and correct the errors in the following sentences.",
      "metadata": {
        "idioma": "ingles",
        "es_libre": true,
        "titulo_tema": "Travel and Vacation",
        "frases_con_errores": [
          {
            "frase_con_error": "Last summer we have visited three different countries.",
            "correccion": "Last summer we visited three different countries.",
            "tipo_error": "Tiempo verbal incorrecto",
            "pista": "'Last summer' indica pasado simple, no presente perfecto"
          },
          {
            "frase_con_error": "The hotel was more cheaper than we expected.",
            "correccion": "The hotel was cheaper than we expected.",
            "tipo_error": "Estructura comparativa incorrecta",
            "pista": "No se usa 'more' con adjetivos cortos como 'cheap'"
          }
        ]
      },
      "puntos": 2
    }
  ]
}
```

---

### writing_transformation_libre

Transformaciones gramaticales con frases sobre temas variados.

```json
{
  "preguntas": [
    {
      "tipo": "writing_transformation_libre",
      "pregunta": "Transform the sentences according to the instructions.",
      "metadata": {
        "idioma": "ingles",
        "es_libre": true,
        "titulo_tema": "Environment and Nature",
        "transformaciones": [
          {
            "original": "People should recycle more to protect the environment.",
            "instruccion": "Change to passive voice.",
            "transformacion_esperada": "More recycling should be done to protect the environment."
          },
          {
            "original": "Scientists discovered a new species in the Amazon.",
            "instruccion": "Change to present perfect.",
            "transformacion_esperada": "Scientists have discovered a new species in the Amazon."
          }
        ]
      },
      "puntos": 2
    }
  ]
}
```

---

### picture_description_libre

Descripción de una imagen real subida (sin prompt de generación).

```json
{
  "preguntas": [
    {
      "tipo": "picture_description_libre",
      "pregunta": "Describe the image you see in 5 sentences.",
      "metadata": {
        "idioma": "ingles",
        "es_libre": true,
        "imagen_url": "ruta/a/la/imagen.jpg",
        "que_describir": [
          "Describe what you see",
          "Who is present",
          "What are they doing",
          "Describe the setting",
          "What mood/atmosphere"
        ],
        "oraciones_minimas": 5
      },
      "puntos": 5
    }
  ]
}
```

**Nota:** Este tipo se usa cuando el usuario sube su propia imagen en lugar de generar una con IA.

---

## Programación

### code_mcq

Pregunta de opción múltiple con código formateado.

```json
{
  "preguntas": [
    {
      "tipo": "code_mcq",
      "lenguaje": "javascript",
      "concepto_teoria": "Suma de variables numéricas",
      "pregunta": "¿Qué valor tendrá 'resultado' después de ejecutar este código?",
      "codigo": "let numero1 = 10;\nlet numero2 = 5;\nlet resultado = numero1 + numero2;",
      "opciones": ["15", "105", "\"10 + 5\"", "undefined"],
      "respuesta_correcta": 0,
      "explicacion": "La suma de dos números (10 + 5) da 15. Ambas variables son de tipo number.",
      "puntos": 2
    }
  ]
}
```

| Campo                | Descripción                                                 |
| -------------------- | ----------------------------------------------------------- |
| `lenguaje`           | `javascript`, `python`, `java`, `typescript`, `react`, etc. |
| `respuesta_correcta` | Índice de la opción correcta (0-3)                          |
| `codigo`             | Código con `\n` para saltos de línea                        |

---

### code_como_ejemplo

El estudiante debe escribir código similar al ejemplo de la teoría.

```json
{
  "preguntas": [
    {
      "tipo": "code_como_ejemplo",
      "lenguaje": "javascript",
      "concepto_teoria": "Declaración y suma de variables",
      "instruccion": "Basándote en el ejemplo de la teoría, escribe código que haga lo mismo pero con estos valores:",
      "datos_ejercicio": "Crea dos variables con los números 20 y 8, súmalas y muestra el resultado",
      "ejemplo_teoria": "// Así lo hacía el ejemplo de la teoría:\nlet a = 5;\nlet b = 3;\nlet suma = a + b;\nconsole.log(suma);",
      "solucion_esperada": "let a = 20;\nlet b = 8;\nlet suma = a + b;\nconsole.log(suma); // 28",
      "explicacion": "Aplicamos exactamente el patrón de la teoría cambiando solo los valores",
      "puntos": 3
    }
  ]
}
```

---

### code_encontrar_error

Encontrar y corregir bugs en código.

```json
{
  "preguntas": [
    {
      "tipo": "code_encontrar_error",
      "lenguaje": "javascript",
      "concepto_teoria": "Variables y operaciones",
      "instruccion": "Este código tiene un error. Encuéntralo y corrígelo.",
      "codigo_con_error": "let numero1 = 10;\nlet numero2 = 5;\nlet resultado = numero1 + numero3;\nconsole.log(resultado);",
      "linea_error": 3,
      "tipo_error": "ReferenceError: numero3 is not defined",
      "pista": "Revisa los nombres de las variables que declaraste",
      "codigo_corregido": "let numero1 = 10;\nlet numero2 = 5;\nlet resultado = numero1 + numero2;\nconsole.log(resultado);",
      "explicacion": "Se usó 'numero3' pero la variable se llama 'numero2'. Error típico de typo.",
      "puntos": 4
    }
  ]
}
```

---

### code_que_pasa_si

Predecir qué sucede al modificar código.

```json
{
  "preguntas": [
    {
      "tipo": "code_que_pasa_si",
      "lenguaje": "javascript",
      "concepto_teoria": "Tipos de datos y coerción",
      "codigo_original": "// Código original:\nlet a = 10;\nlet b = 5;\nconsole.log(a + b); // Imprime: 15",
      "pregunta": "¿Qué pasaría si cambiamos el código así?",
      "codigo_modificado": "let a = '10';  // Ahora es string\nlet b = 5;\nconsole.log(a + b);",
      "opciones_respuesta": [
        "Imprime: 15 (suma normal)",
        "Imprime: '105' (concatenación)",
        "Error: no se pueden sumar",
        "Imprime: NaN"
      ],
      "respuesta_correcta": 1,
      "explicacion": "Al ser 'a' un string, el + concatena en lugar de sumar. '10' + 5 = '105'",
      "leccion_aprendida": "JavaScript convierte el número a string cuando uno de los operandos es string",
      "puntos": 4
    }
  ]
}
```

---

### code_industria

Implementar el concepto en contexto profesional/real.

```json
{
  "preguntas": [
    {
      "tipo": "code_industria",
      "lenguaje": "javascript",
      "concepto_teoria": "Suma de arrays con reduce",
      "contexto": "Sistema de e-commerce",
      "instruccion": "Implementa una solución profesional para este caso:",
      "problema": "Calcular el total de un carrito de compras sumando los precios de todos los productos",
      "requisitos": [
        "Usar el concepto de la teoría (suma)",
        "Manejar casos edge (carrito vacío, valores null)",
        "Seguir buenas prácticas"
      ],
      "solucion_profesional": "function calcularTotal(items) {\n  if (!items || items.length === 0) return 0;\n  return items.reduce((total, item) => {\n    return total + (item.precio || 0);\n  }, 0);\n}",
      "explicacion": "Esta solución aplica suma con validaciones y código limpio",
      "buenas_practicas_aplicadas": [
        "Validación de entrada",
        "Valor por defecto",
        "Código legible"
      ],
      "puntos": 5
    }
  ]
}
```

---

### code_error_industria

Detectar bugs sutiles en código de producción.

```json
{
  "preguntas": [
    {
      "tipo": "code_error_industria",
      "lenguaje": "javascript",
      "concepto_teoria": "Bucles y arrays",
      "contexto": "Este código está en producción y tiene un bug sutil",
      "codigo_produccion": "function procesarPagos(transacciones) {\n  let total = 0;\n  for (let i = 0; i <= transacciones.length; i++) {\n    total += transacciones[i].monto;\n  }\n  return total;\n}",
      "sintoma_bug": "El código a veces lanza 'Cannot read property monto of undefined'",
      "pista": "Revisa los límites del bucle",
      "tipo_error": "Off-by-one error / Array index out of bounds",
      "codigo_corregido": "function procesarPagos(transacciones) {\n  let total = 0;\n  for (let i = 0; i < transacciones.length; i++) {\n    total += transacciones[i].monto;\n  }\n  return total;\n}",
      "explicacion": "El <= hace que el bucle intente acceder a transacciones[length] que no existe. Debe ser <",
      "impacto_produccion": "Este bug causaría crashes aleatorios en el sistema de pagos",
      "puntos": 6
    }
  ]
}
```

---

## Idiomas Disponibles

Los ejercicios de idiomas soportan:

| Código      | Idioma         |
| ----------- | -------------- |
| `ingles`    | Inglés         |
| `frances`   | Francés        |
| `aleman`    | Alemán         |
| `italiano`  | Italiano       |
| `portugues` | Portugués      |
| `japones`   | Japonés        |
| `chino`     | Chino Mandarín |
| `coreano`   | Coreano        |
| `ruso`      | Ruso           |
| `arabe`     | Árabe          |

---

## Lenguajes de Programación

| Código       | Lenguaje     |
| ------------ | ------------ |
| `javascript` | JavaScript   |
| `typescript` | TypeScript   |
| `react`      | React        |
| `angular`    | Angular      |
| `vue`        | Vue.js       |
| `nodejs`     | Node.js      |
| `python`     | Python       |
| `java`       | Java         |
| `spring`     | Spring Boot  |
| `csharp`     | C#           |
| `dotnet`     | .NET/ASP.NET |
| `cpp`        | C++          |
| `c`          | C            |
| `go`         | Go           |
| `rust`       | Rust         |
| `php`        | PHP          |
| `ruby`       | Ruby         |
| `swift`      | Swift        |
| `kotlin`     | Kotlin       |
| `sql`        | SQL          |
| `html`       | HTML/CSS     |
| `bash`       | Bash/Shell   |

---

## Niveles CEFR (Para Ejercicios de Idiomas)

| Nivel | Descripción                                       |
| ----- | ------------------------------------------------- |
| A1    | Principiante - Vocabulario básico, frases simples |
| A2    | Elemental - Frases cortas, tiempos básicos        |
| B1    | Intermedio - Conectores, inferencia simple        |
| B2    | Intermedio Alto - Lenguaje matizado, hipótesis    |
| C1    | Avanzado - Precisión léxica, análisis             |
| C2    | Maestría - Matices, análisis crítico              |

---

## Estructura General del JSON

Todos los ejercicios deben estar envueltos en esta estructura:

```json
{
  "preguntas": [
    {
      /* ejercicio 1 */
    },
    {
      /* ejercicio 2 */
    },
    {
      /* ejercicio 3 */
    }
  ]
}
```

**Campos obligatorios en cada ejercicio:**

- `tipo`: El tipo de ejercicio (obligatorio)
- `pregunta`: El enunciado o instrucción (obligatorio)
- `puntos`: Puntos que vale el ejercicio (recomendado)

---

## Ejemplos de JSON Combinados

### Examen mixto básico:

```json
{
  "preguntas": [
    {
      "tipo": "mcq",
      "pregunta": "¿Qué es HTML?",
      "opciones": [
        "A) Un lenguaje de programación",
        "B) Un lenguaje de marcado",
        "C) Una base de datos",
        "D) Un sistema operativo"
      ],
      "respuesta_correcta": "B",
      "explicacion": "HTML significa HyperText Markup Language, es un lenguaje de marcado.",
      "puntos": 1
    },
    {
      "tipo": "true_false",
      "pregunta": "CSS se usa para dar estilo a páginas web.",
      "respuesta_correcta": "Verdadero",
      "explicacion": "CSS (Cascading Style Sheets) es el lenguaje estándar para estilos web.",
      "puntos": 1
    },
    {
      "tipo": "short_answer",
      "pregunta": "¿Para qué sirve JavaScript en una página web?",
      "respuesta_esperada": "JavaScript se usa para añadir interactividad y comportamiento dinámico a las páginas web.",
      "palabras_clave": ["interactividad", "dinámico", "comportamiento"],
      "explicacion": "JavaScript permite crear elementos interactivos como animaciones, validaciones de formularios, etc.",
      "puntos": 2
    }
  ]
}
```

---

_Última actualización: Enero 2025_

Ejercicios Básicos
MCQ - Opción Múltiple
True/False - Verdadero/Falso
Cloze - Rellenar Huecos
Short_Answer - Respuesta Corta
Open_Question - Pregunta Abierta
Caso de Estudio

Comprensión Lectora (Idiomas)
Reading Comprehension
Reading Written
Reading True/False
Reading Cloze
Reading Skill
Reading Matching
Reading Sequence

Expresión Escrita (Idiomas)
Writing Short
Writing Paraphrase
Writing Correction
Writing Transformation
Writing Essay
Sentence Builder
Formal Email
Picture Description

Ejercicios "Libre" (Sin Tema Predefinido)
Sentence Builder Libre
Writing Short Libre
Writing Paraphrase Libre
Writing Correction Libre
Writing Transformation Libre
Picture Description Libre

Programación
Code MCQ
Code Como Ejemplo
Code Encontrar Error
Code Qué Pasa Si
Code Industria
Code Error Industria
