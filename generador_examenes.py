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
        prompt = f"""Eres un profesor experto creando un examen basado en el siguiente contenido.

CONTENIDO DEL DOCUMENTO:
{contenido[:3000]}... [documento continúa]

INSTRUCCIONES:
Genera exactamente {sum(num_preguntas.values())} preguntas difíciles y bien pensadas:
- {num_preguntas.get('multiple', 0)} preguntas de opción múltiple (4 opciones: A, B, C, D)
- {num_preguntas.get('combo', 0)} preguntas de selección múltiple con combobox
- {num_preguntas.get('corta', 0)} preguntas de respuesta corta
- {num_preguntas.get('desarrollo', 0)} preguntas de desarrollo

FORMATO DE RESPUESTA (JSON estricto):
{{
  "preguntas": [
    {{
      "tipo": "multiple",
      "pregunta": "¿Cuál es el concepto principal de...?",
      "opciones": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "respuesta_correcta": "A",
      "puntos": 2
    }},
    {{
      "tipo": "corta",
      "pregunta": "Explica brevemente el concepto de...",
      "respuesta_correcta": "Respuesta modelo: ...",
      "puntos": 3
    }},
    {{
      "tipo": "desarrollo",
      "pregunta": "Analiza en profundidad...",
      "respuesta_correcta": "Criterios de evaluación: Debe mencionar...",
      "puntos": 5
    }}
  ]
}}

Responde SOLO con el JSON, sin texto adicional:"""
        return prompt
    
    def generar_examen(self, contenido_documento: str, 
                      num_preguntas: Dict[str, int] = None) -> List[PreguntaExamen]:
        """Genera un examen basado en el contenido"""
        if not self.llm:
            print("Error: Modelo no cargado. Generando examen de ejemplo...")
            return self._generar_examen_ejemplo()
        
        if num_preguntas is None:
            num_preguntas = {
                'multiple': 5,
                'combo': 2,
                'corta': 3,
                'desarrollo': 2
            }
        
        prompt = self.generar_prompt_preguntas(contenido_documento, num_preguntas)
        
        print("Generando preguntas con IA...")
        try:
            respuesta = self.llm(
                prompt,
                max_tokens=2000,
                temperature=0.7,
                stop=["```"]
            )
            
            texto_respuesta = respuesta['choices'][0]['text']
            
            # Intentar parsear JSON
            try:
                datos = json.loads(texto_respuesta)
                preguntas = [PreguntaExamen.from_dict(p) for p in datos['preguntas']]
                return preguntas
            except json.JSONDecodeError:
                print("Error al parsear respuesta de IA, generando examen de ejemplo...")
                return self._generar_examen_ejemplo()
                
        except Exception as e:
            print(f"Error al generar examen: {e}")
            return self._generar_examen_ejemplo()
    
    def _generar_examen_ejemplo(self) -> List[PreguntaExamen]:
        """Genera un examen de ejemplo sin IA"""
        return [
            PreguntaExamen(
                tipo='multiple',
                pregunta='¿Cuál es el tema principal del documento?',
                opciones=['A) Tecnología', 'B) Ciencia', 'C) Historia', 'D) Arte'],
                respuesta_correcta='A',
                puntos=2
            ),
            PreguntaExamen(
                tipo='corta',
                pregunta='Resume en 2-3 líneas la idea principal del documento.',
                respuesta_correcta='Debe mencionar los conceptos clave y la tesis principal.',
                puntos=3
            ),
            PreguntaExamen(
                tipo='desarrollo',
                pregunta='Analiza críticamente los argumentos presentados en el documento.',
                respuesta_correcta='Debe incluir: análisis de argumentos, evidencia, conclusiones.',
                puntos=5
            )
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
        if not self.llm:
            return pregunta.puntos // 2, "Evaluación manual requerida (sin modelo IA)"
        
        prompt = f"""Eres un profesor evaluando una respuesta corta.

PREGUNTA: {pregunta.pregunta}

RESPUESTA MODELO: {pregunta.respuesta_correcta}

RESPUESTA DEL ESTUDIANTE: {respuesta}

PUNTOS MÁXIMOS: {pregunta.puntos}

Evalúa la respuesta del estudiante comparándola con la respuesta modelo.
Responde en formato JSON:
{{
  "puntos": <número de 0 a {pregunta.puntos}>,
  "feedback": "Explicación breve de la calificación"
}}"""
        
        try:
            resultado = self.llm(prompt, max_tokens=200, temperature=0.3)
            texto = resultado['choices'][0]['text']
            datos = json.loads(texto)
            return datos['puntos'], datos['feedback']
        except:
            return pregunta.puntos // 2, "Parcialmente correcto (evaluación automática limitada)"
    
    def _evaluar_desarrollo(self, pregunta: PreguntaExamen, respuesta: str) -> tuple[int, str]:
        """Evalúa pregunta de desarrollo con IA"""
        if not self.llm:
            return pregunta.puntos // 2, "Evaluación manual requerida (sin modelo IA)"
        
        prompt = f"""Eres un profesor evaluando una pregunta de desarrollo.

PREGUNTA: {pregunta.pregunta}

CRITERIOS DE EVALUACIÓN: {pregunta.respuesta_correcta}

RESPUESTA DEL ESTUDIANTE: {respuesta}

PUNTOS MÁXIMOS: {pregunta.puntos}

Evalúa según:
1. Comprensión del tema
2. Argumentación y estructura
3. Profundidad del análisis
4. Claridad de expresión

Responde en formato JSON:
{{
  "puntos": <número de 0 a {pregunta.puntos}>,
  "feedback": "Feedback detallado con fortalezas y áreas de mejora"
}}"""
        
        try:
            resultado = self.llm(prompt, max_tokens=500, temperature=0.3)
            texto = resultado['choices'][0]['text']
            datos = json.loads(texto)
            return datos['puntos'], datos['feedback']
        except:
            return pregunta.puntos // 2, "Respuesta válida (evaluación automática limitada)"


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
