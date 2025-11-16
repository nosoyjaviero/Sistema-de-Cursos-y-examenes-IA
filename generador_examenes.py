"""
Sistema de generación y evaluación de exámenes con IA local
"""
from pathlib import Path
from typing import List, Dict, Optional
import json
import sys
from datetime import datetime


class PreguntaExamen:
    """Representa una pregunta de examen"""
    
    def __init__(self, tipo: str, pregunta: str, opciones: List[str] = None, 
                 respuesta_correcta: str = "", puntos: int = 1):
        self.tipo = tipo  # 'multiple', 'combo', 'corta', 'desarrollo'
        self.pregunta = pregunta
        self.opciones = opciones or []
        self.respuesta_correcta = respuesta_correcta
        self.puntos = puntos
        self.respuesta_usuario = None
        self.puntos_obtenidos = 0
    
    def to_dict(self):
        return {
            'tipo': self.tipo,
            'pregunta': self.pregunta,
            'opciones': self.opciones,
            'respuesta_correcta': self.respuesta_correcta,
            'puntos': self.puntos
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            tipo=data['tipo'],
            pregunta=data['pregunta'],
            opciones=data.get('opciones', []),
            respuesta_correcta=data.get('respuesta_correcta', ''),
            puntos=data.get('puntos', 1)
        )


class GeneradorExamenes:
    """Genera exámenes usando un modelo LLM local"""
    
    def __init__(self, modelo_path: Optional[str] = None):
        self.modelo_path = modelo_path
        self.llm = None
        if modelo_path:
            self._cargar_modelo()
    
    def _cargar_modelo(self):
        """Carga el modelo LLM"""
        try:
            from llama_cpp import Llama
            print(f"Cargando modelo desde: {self.modelo_path}")
            self.llm = Llama(
                model_path=self.modelo_path,
                n_ctx=4096,  # Contexto largo para documentos grandes
                n_threads=4,
                verbose=False
            )
            print("Modelo cargado exitosamente")
        except Exception as e:
            print(f"Error al cargar modelo: {e}")
            self.llm = None
    
    def generar_prompt_preguntas(self, contenido: str, num_preguntas: Dict[str, int]) -> str:
        """Genera el prompt para crear preguntas"""
        # Limitar contenido pero mantener suficiente contexto
        contenido_limitado = contenido[:6000] if len(contenido) > 6000 else contenido
        
        prompt = f"""Eres un profesor universitario experto creando un examen PRÁCTICO y ÚTIL para que los estudiantes realmente comprendan la materia.

CONTENIDO DEL MATERIAL DE ESTUDIO:
{contenido_limitado}

OBJETIVO: Crear preguntas que evalúen COMPRENSIÓN PROFUNDA, APLICACIÓN PRÁCTICA y PENSAMIENTO CRÍTICO, NO solo memorización.

INSTRUCCIONES ESTRICTAS:
Genera EXACTAMENTE {sum(num_preguntas.values())} preguntas siguiendo esta distribución:
- {num_preguntas.get('multiple', 0)} preguntas de opción múltiple
- {num_preguntas.get('corta', 0)} preguntas de respuesta corta
- {num_preguntas.get('desarrollo', 0)} preguntas de desarrollo

CRITERIOS DE CALIDAD OBLIGATORIOS:

1. PREGUNTAS DE OPCIÓN MÚLTIPLE (tipo: "multiple"):
   - Deben evaluar COMPRENSIÓN, no solo memoria
   - Incluir casos prácticos o escenarios reales
   - Opciones incorrectas deben ser plausibles pero claramente erróneas
   - Evitar preguntas triviales tipo "¿Qué es...?"
   - Formato de respuesta: Solo la letra (A, B, C o D)
   - Valor: 3 puntos cada una

2. PREGUNTAS DE RESPUESTA CORTA (tipo: "corta"):
   - Pedir EXPLICACIONES de conceptos clave
   - Solicitar COMPARACIONES entre ideas
   - Preguntar CÓMO aplicar el conocimiento
   - Requieren 2-4 oraciones de respuesta
   - La respuesta_correcta debe ser una guía detallada de lo que se espera
   - Valor: 4 puntos cada una

3. PREGUNTAS DE DESARROLLO (tipo: "desarrollo"):
   - Requieren ANÁLISIS PROFUNDO y ARGUMENTACIÓN
   - Deben conectar múltiples conceptos del material
   - Pedir ejemplos, aplicaciones o críticas fundamentadas
   - La respuesta_correcta debe listar criterios de evaluación específicos
   - Valor: 6 puntos cada una

EJEMPLOS DE BUENAS PREGUNTAS:

Opción múltiple BUENA:
"En un proyecto donde necesitas implementar [concepto del material], ¿cuál sería el enfoque más adecuado considerando las limitaciones mencionadas en el documento?"

Respuesta corta BUENA:
"Explica con tus propias palabras cómo el concepto X se relaciona con Y, y proporciona un ejemplo práctico de su aplicación."

Desarrollo BUENA:
"Analiza críticamente la solución propuesta en el material. ¿Qué ventajas y desventajas presenta? ¿Cómo la mejorarías en un contexto real?"

FORMATO DE RESPUESTA (JSON ESTRICTO - sin comentarios):
{{
  "preguntas": [
    {{
      "tipo": "multiple",
      "pregunta": "[Pregunta práctica sobre aplicación del concepto]",
      "opciones": ["A) [Opción plausible pero incorrecta]", "B) [Respuesta correcta bien justificada]", "C) [Error conceptual común]", "D) [Otro error plausible]"],
      "respuesta_correcta": "B",
      "puntos": 3
    }},
    {{
      "tipo": "corta",
      "pregunta": "[Pregunta que requiere explicación clara]",
      "respuesta_correcta": "Debe explicar: [punto 1], mencionar [punto 2], y ejemplificar con [punto 3]",
      "puntos": 4
    }},
    {{
      "tipo": "desarrollo",
      "pregunta": "[Pregunta que requiere análisis profundo]",
      "respuesta_correcta": "Criterios: 1) Identifica los conceptos clave [específicos], 2) Analiza la relación entre ellos, 3) Proporciona ejemplos concretos, 4) Argumenta conclusiones lógicas",
      "puntos": 6
    }}
  ]
}}

IMPORTANTE: 
- Responde SOLO con el JSON válido
- NO agregues texto antes o después del JSON
- Asegúrate que las preguntas cubran TODO el contenido importante
- Las preguntas deben ser DESAFIANTES pero JUSTAS
- Enfócate en comprensión y aplicación, NO en memorización

JSON:"""
        return prompt
    
    def generar_examen(self, contenido_documento: str, 
                      num_preguntas: Dict[str, int] = None) -> List[PreguntaExamen]:
        """Genera un examen basado en el contenido"""
        if not self.llm:
            print("⚠️ Modelo no cargado. Generando examen de ejemplo...")
            return self._generar_examen_ejemplo()
        
        if num_preguntas is None:
            num_preguntas = {
                'multiple': 8,
                'corta': 5,
                'desarrollo': 3
            }
        
        prompt = self.generar_prompt_preguntas(contenido_documento, num_preguntas)
        
        print(f"🤖 Generando {sum(num_preguntas.values())} preguntas con IA...")
        print(f"   📝 {num_preguntas.get('multiple', 0)} opción múltiple")
        print(f"   ✍️ {num_preguntas.get('corta', 0)} respuesta corta")
        print(f"   📖 {num_preguntas.get('desarrollo', 0)} desarrollo")
        
        try:
            respuesta = self.llm(
                prompt,
                max_tokens=3500,  # Aumentado para permitir más preguntas
                temperature=0.8,   # Mayor creatividad para preguntas variadas
                top_p=0.95,
                repeat_penalty=1.2,  # Evitar repetición
                stop=["```", "\n\n\n"]
            )
            
            texto_respuesta = respuesta['choices'][0]['text'].strip()
            
            # Limpiar posible texto antes/después del JSON
            if '{' in texto_respuesta:
                inicio = texto_respuesta.find('{')
                fin = texto_respuesta.rfind('}') + 1
                texto_respuesta = texto_respuesta[inicio:fin]
            
            # Intentar parsear JSON
            try:
                datos = json.loads(texto_respuesta)
                preguntas = [PreguntaExamen.from_dict(p) for p in datos['preguntas']]
                
                if len(preguntas) < sum(num_preguntas.values()) * 0.7:
                    print(f"⚠️ Solo se generaron {len(preguntas)} preguntas, esperadas {sum(num_preguntas.values())}")
                else:
                    print(f"✅ Generadas {len(preguntas)} preguntas exitosamente")
                
                return preguntas if preguntas else self._generar_examen_ejemplo()
                
            except json.JSONDecodeError as e:
                print(f"❌ Error al parsear JSON de IA: {e}")
                print(f"Respuesta recibida: {texto_respuesta[:200]}...")
                return self._generar_examen_ejemplo()
                
        except Exception as e:
            print(f"❌ Error al generar examen con IA: {e}")
            return self._generar_examen_ejemplo()
    
    def _generar_examen_ejemplo(self) -> List[PreguntaExamen]:
        """Genera un examen de ejemplo sin IA"""
        print("📝 Generando examen de ejemplo (sin modelo IA cargado)")
        return [
            # Preguntas de opción múltiple
            PreguntaExamen(
                tipo='multiple',
                pregunta='¿Cuál de las siguientes afirmaciones describe mejor la idea central del documento?',
                opciones=[
                    'A) Presenta una lista de datos sin conexión',
                    'B) Desarrolla conceptos fundamentales con ejemplos prácticos',
                    'C) Solo contiene definiciones técnicas',
                    'D) Es únicamente material de referencia'
                ],
                respuesta_correcta='B',
                puntos=3
            ),
            PreguntaExamen(
                tipo='multiple',
                pregunta='Si tuvieras que aplicar los conceptos del documento en un proyecto real, ¿qué factor sería más crítico considerar?',
                opciones=[
                    'A) El costo de implementación',
                    'B) La comprensión profunda de los fundamentos teóricos',
                    'C) La velocidad de ejecución',
                    'D) La popularidad de la tecnología'
                ],
                respuesta_correcta='B',
                puntos=3
            ),
            PreguntaExamen(
                tipo='multiple',
                pregunta='¿Qué relación existe entre los principales conceptos presentados en el material?',
                opciones=[
                    'A) Son independientes y no se relacionan',
                    'B) Cada concepto contradice al anterior',
                    'C) Se complementan formando un marco conceptual integrado',
                    'D) Solo uno de ellos es relevante'
                ],
                respuesta_correcta='C',
                puntos=3
            ),
            PreguntaExamen(
                tipo='multiple',
                pregunta='Al evaluar la aplicabilidad del contenido, ¿cuál sería la mejor estrategia?',
                opciones=[
                    'A) Memorizar todas las definiciones',
                    'B) Comprender los principios y adaptarlos al contexto',
                    'C) Copiar los ejemplos tal cual',
                    'D) Ignorar la teoría y enfocarse en la práctica'
                ],
                respuesta_correcta='B',
                puntos=3
            ),
            # Preguntas de respuesta corta
            PreguntaExamen(
                tipo='corta',
                pregunta='Explica con tus propias palabras los 3 conceptos más importantes del material y cómo se relacionan entre sí.',
                respuesta_correcta='Debe identificar 3 conceptos clave del material, explicar cada uno brevemente, y mostrar cómo se conectan o complementan. Se espera comprensión conceptual, no simple repetición.',
                puntos=4
            ),
            PreguntaExamen(
                tipo='corta',
                pregunta='Describe una situación real donde podrías aplicar el conocimiento adquirido y explica cómo lo harías.',
                respuesta_correcta='Debe proporcionar un ejemplo concreto y práctico, explicar el contexto de aplicación, y detallar los pasos o consideraciones necesarias para implementarlo.',
                puntos=4
            ),
            PreguntaExamen(
                tipo='corta',
                pregunta='¿Qué diferencia existe entre los dos enfoques principales discutidos en el material? Proporciona un ejemplo de cada uno.',
                respuesta_correcta='Debe identificar los enfoques principales, explicar sus diferencias fundamentales, y dar ejemplos específicos que ilustren cada enfoque.',
                puntos=4
            ),
            # Preguntas de desarrollo
            PreguntaExamen(
                tipo='desarrollo',
                pregunta='Analiza críticamente el material: identifica sus fortalezas, posibles limitaciones, y propón cómo podrías extender o mejorar los conceptos presentados basándote en tu comprensión.',
                respuesta_correcta='Criterios: 1) Identifica al menos 2 fortalezas específicas del material con justificación, 2) Reconoce limitaciones o áreas de mejora, 3) Propone extensiones o mejoras fundamentadas, 4) Demuestra pensamiento crítico y comprensión profunda.',
                puntos=6
            ),
            PreguntaExamen(
                tipo='desarrollo',
                pregunta='Integra los conceptos principales del documento en un marco coherente. Explica cómo cada elemento contribuye al todo y qué implicaciones prácticas tiene esta integración.',
                respuesta_correcta='Criterios: 1) Identifica los conceptos principales, 2) Explica las relaciones e interdependencias, 3) Construye un marco integrado lógico, 4) Discute implicaciones prácticas específicas.',
                puntos=6
            ),
        ]
    
    def evaluar_respuesta(self, pregunta: PreguntaExamen, respuesta_usuario: str) -> tuple[int, str]:
        """Evalúa una respuesta del usuario"""
        if pregunta.tipo == 'multiple':
            return self._evaluar_multiple(pregunta, respuesta_usuario)
        elif pregunta.tipo == 'corta':
            return self._evaluar_corta(pregunta, respuesta_usuario)
        elif pregunta.tipo == 'desarrollo':
            return self._evaluar_desarrollo(pregunta, respuesta_usuario)
        else:
            return 0, "Tipo de pregunta no soportado"
    
    def _evaluar_multiple(self, pregunta: PreguntaExamen, respuesta: str) -> tuple[int, str]:
        """Evalúa pregunta de opción múltiple"""
        respuesta = respuesta.strip().upper()
        correcta = pregunta.respuesta_correcta.strip().upper()
        
        if respuesta == correcta or respuesta == correcta[0]:
            return pregunta.puntos, "¡Correcto!"
        else:
            return 0, f"Incorrecto. La respuesta correcta es: {pregunta.respuesta_correcta}"
    
    def _evaluar_corta(self, pregunta: PreguntaExamen, respuesta: str) -> tuple[int, str]:
        """Evalúa pregunta de respuesta corta con IA"""
        if not respuesta or len(respuesta.strip()) < 10:
            return 0, "❌ Respuesta insuficiente o vacía. Se requiere una explicación clara y completa."
        
        if not self.llm:
            # Sin IA, evaluación básica por longitud y palabras clave
            palabras = len(respuesta.split())
            if palabras < 15:
                return pregunta.puntos // 4, "⚠️ Respuesta muy breve. Se esperaba mayor desarrollo."
            elif palabras < 30:
                return pregunta.puntos // 2, "⚠️ Respuesta aceptable pero podría ser más detallada."
            else:
                return int(pregunta.puntos * 0.7), "✓ Respuesta con buen desarrollo (evaluación automática)."
        
        prompt = f"""Eres un profesor ESTRICTO evaluando una respuesta corta. Sé crítico pero justo.

PREGUNTA: {pregunta.pregunta}

CRITERIOS DE EVALUACIÓN: {pregunta.respuesta_correcta}

RESPUESTA DEL ESTUDIANTE: 
{respuesta}

PUNTOS MÁXIMOS: {pregunta.puntos}

INSTRUCCIONES DE EVALUACIÓN ESTRICTA:
1. ¿La respuesta demuestra COMPRENSIÓN REAL del concepto? (no solo copiar)
2. ¿Incluye los elementos clave mencionados en los criterios?
3. ¿Proporciona ejemplos o explicaciones claras?
4. ¿La redacción es coherente y precisa?

ESCALA:
- {pregunta.puntos} puntos: Excelente, completa todos los criterios con claridad
- {int(pregunta.puntos * 0.75)}-{pregunta.puntos - 1} puntos: Buena, cumple la mayoría de criterios
- {int(pregunta.puntos * 0.5)}-{int(pregunta.puntos * 0.7)} puntos: Aceptable, cumple criterios básicos pero falta profundidad
- {int(pregunta.puntos * 0.25)}-{int(pregunta.puntos * 0.45)} puntos: Insuficiente, solo aspectos superficiales
- 0-{int(pregunta.puntos * 0.2)} puntos: Inadecuada, no demuestra comprensión

Responde SOLO con JSON:
{{
  "puntos": <número de 0 a {pregunta.puntos}>,
  "feedback": "Feedback específico: qué está bien, qué falta, cómo mejorar"
}}"""
        
        try:
            resultado = self.llm(prompt, max_tokens=250, temperature=0.2)
            texto = resultado['choices'][0]['text'].strip()
            
            if '{' in texto:
                inicio = texto.find('{')
                fin = texto.rfind('}') + 1
                texto = texto[inicio:fin]
            
            datos = json.loads(texto)
            puntos = min(datos['puntos'], pregunta.puntos)
            return puntos, datos['feedback']
        except:
            # Fallback con evaluación por similitud de longitud
            palabras = len(respuesta.split())
            if palabras < 20:
                return pregunta.puntos // 3, "⚠️ Respuesta incompleta. Falta desarrollo y profundidad."
            else:
                return int(pregunta.puntos * 0.6), "✓ Respuesta aceptable (evaluación automática limitada)."
    
    def _evaluar_desarrollo(self, pregunta: PreguntaExamen, respuesta: str) -> tuple[int, str]:
        """Evalúa pregunta de desarrollo con IA"""
        if not respuesta or len(respuesta.strip()) < 50:
            return 0, "❌ Respuesta insuficiente. Las preguntas de desarrollo requieren análisis profundo y extenso."
        
        if not self.llm:
            # Sin IA, evaluación básica por longitud y estructura
            palabras = len(respuesta.split())
            if palabras < 50:
                return pregunta.puntos // 4, "⚠️ Respuesta muy breve para una pregunta de desarrollo."
            elif palabras < 100:
                return pregunta.puntos // 2, "⚠️ Respuesta insuficiente. Se requiere mayor profundidad."
            else:
                return int(pregunta.puntos * 0.7), "✓ Respuesta con desarrollo aceptable (evaluación automática)."
        
        prompt = f"""Eres un profesor universitario EXIGENTE evaluando una pregunta de desarrollo. Sé CRÍTICO pero JUSTO.

PREGUNTA: {pregunta.pregunta}

CRITERIOS DE EVALUACIÓN ESPECÍFICOS:
{pregunta.respuesta_correcta}

RESPUESTA DEL ESTUDIANTE:
{respuesta}

PUNTOS MÁXIMOS: {pregunta.puntos}

EVALUACIÓN DETALLADA - Analiza estos 5 aspectos:

1. COMPRENSIÓN CONCEPTUAL ({int(pregunta.puntos * 0.25)} pts máx)
   - ¿Demuestra entendimiento profundo de los conceptos?
   - ¿Identifica correctamente los elementos clave?

2. ANÁLISIS Y ARGUMENTACIÓN ({int(pregunta.puntos * 0.25)} pts máx)
   - ¿Presenta argumentos lógicos y bien fundamentados?
   - ¿Conecta ideas de manera coherente?

3. PROFUNDIDAD Y EXTENSIÓN ({int(pregunta.puntos * 0.2)} pts máx)
   - ¿Explora el tema con suficiente profundidad?
   - ¿Proporciona ejemplos o casos específicos?

4. PENSAMIENTO CRÍTICO ({int(pregunta.puntos * 0.2)} pts máx)
   - ¿Analiza críticamente en lugar de solo describir?
   - ¿Propone ideas originales o mejoras?

5. CLARIDAD Y ESTRUCTURA ({int(pregunta.puntos * 0.1)} pts máx)
   - ¿La respuesta está bien organizada?
   - ¿Se expresa con claridad?

IMPORTANTE: 
- Penaliza severamente respuestas superficiales o genéricas
- Recompensa análisis profundo y pensamiento crítico
- El máximo solo se otorga a respuestas excepcionales

Responde SOLO con JSON:
{{
  "puntos": <número de 0 a {pregunta.puntos}>,
  "feedback": "Feedback detallado: (1) Lo que está bien hecho, (2) Lo que falta o necesita mejora, (3) Sugerencias específicas"
}}"""
        
        try:
            resultado = self.llm(prompt, max_tokens=600, temperature=0.2)
            texto = resultado['choices'][0]['text'].strip()
            
            if '{' in texto:
                inicio = texto.find('{')
                fin = texto.rfind('}') + 1
                texto = texto[inicio:fin]
            
            datos = json.loads(texto)
            puntos = min(datos['puntos'], pregunta.puntos)
            return puntos, datos['feedback']
        except Exception as e:
            print(f"Error en evaluación de desarrollo: {e}")
            # Fallback con evaluación por longitud
            palabras = len(respuesta.split())
            if palabras < 80:
                return int(pregunta.puntos * 0.4), "⚠️ Respuesta breve. Se espera mayor desarrollo y profundidad."
            else:
                return int(pregunta.puntos * 0.65), "✓ Respuesta con desarrollo (evaluación automática limitada)."


def guardar_examen(preguntas: List[PreguntaExamen], ruta: Path):
    """Guarda el examen en formato JSON"""
    datos = {
        'fecha_creacion': datetime.now().isoformat(),
        'preguntas': [p.to_dict() for p in preguntas]
    }
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def cargar_examen(ruta: Path) -> List[PreguntaExamen]:
    """Carga un examen desde JSON"""
    with open(ruta, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    return [PreguntaExamen.from_dict(p) for p in datos['preguntas']]


if __name__ == "__main__":
    print("Módulo de generación de exámenes")
    print("Usar desde examinator_interactivo.py")
