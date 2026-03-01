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

| Nivel | Longitud Respuesta      | Complejidad                 |
| ----- | ----------------------- | --------------------------- |
| A1    | 1-5 palabras            | Información explícita       |
| A2    | 1-5 palabras            | Presente/pasado simple      |
| B1    | 1-2 frases              | Conectar ideas (because/so) |
| B2    | 1-2 frases elaboradas   | Inferencia y reformulación  |
| C1    | 2-3 frases precisas     | Inferencias complejas       |
| C2    | 2-3 frases sofisticadas | Análisis de tono y matices  |

---

### writing_paraphrase

Reescribir frases con diferentes palabras manteniendo el significado.

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
            "parafraseo_esperado": "She stayed at home due to her illness."
          },
          {
            "original": "The movie was very interesting.",
            "parafraseo_esperado": "The film was quite fascinating."
          },
          {
            "original": "I can't understand this problem.",
            "parafraseo_esperado": "I'm unable to comprehend this issue."
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

---

### writing_transformation

Transformar oraciones según instrucciones específicas.

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

---

### writing_essay

Mini-ensayo sobre un tema dado.

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
        "modelo_respuesta": "Social media has become an essential part of modern life. On one hand, it allows people to connect with friends and family around the world..."
      },
      "puntos": 5
    }
  ]
}
```

---

### sentence_builder

Ordenar palabras para formar oraciones correctas.

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

---

### formal_email

Escribir un email formal según una situación.

```json
{
  "preguntas": [
    {
      "tipo": "formal_email",
      "idioma": "ingles",
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
      ],
      "puntos": 5
    }
  ]
}
```

---

### picture_description

Describir una imagen en el idioma objetivo. Incluye prompt para generar la imagen con IA.

```json
{
  "preguntas": [
    {
      "tipo": "picture_description",
      "pregunta": "Describe the image in 5 sentences.",
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
        "descripcion_modelo": "The picture shows a modern office with several people working. There are about five employees sitting at their desks..."
      },
      "puntos": 5
    }
  ]
}
```

**Nota:** El campo `prompt_generacion` se puede usar con DALL-E, Midjourney o Stable Diffusion para generar la imagen.

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
            "parafraseo_esperado": "Mobile phones have transformed our communication methods.",
            "pistas_parafraseo": "Try using 'transform' instead of 'revolutionize'."
          },
          {
            "original": "Many people prefer online shopping because it saves time.",
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
