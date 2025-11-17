"""
Generador de exámenes usando Ollama (con GPU automática)
"""
from pathlib import Path
from typing import List, Dict, Optional
import json
import requests
from generador_examenes import PreguntaExamen


class GeneradorExamenesOllama:
    """Generador usando Ollama - GPU automática"""
    
    def __init__(self, modelo: str = "llama3.2:3b"):
        self.modelo = modelo
        self.url_base = "http://localhost:11434"
        self._verificar_ollama()
    
    def _verificar_ollama(self):
        """Verifica que Ollama esté corriendo"""
        try:
            response = requests.get(f"{self.url_base}/api/tags", timeout=2)
            if response.status_code == 200:
                modelos = response.json().get('models', [])
                print(f"✅ Ollama activo - {len(modelos)} modelos disponibles")
                if not any(m['name'].startswith(self.modelo.split(':')[0]) for m in modelos):
                    print(f"⚠️ Modelo {self.modelo} no encontrado")
                    print(f"   Instalar con: ollama pull {self.modelo}")
            else:
                print("⚠️ Ollama no responde correctamente")
        except Exception as e:
            print(f"❌ Error conectando a Ollama: {e}")
            print(f"   Iniciar con: ollama serve")
    
    def _generar_respuesta(self, prompt: str, max_tokens: int = 3000, temperature: float = 0.25) -> str:
        """Genera respuesta usando Ollama"""
        try:
            response = requests.post(
                f"{self.url_base}/api/generate",
                json={
                    "model": self.modelo,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                        "stop": ["<|eot_id|>", "<|end_of_text|>"]
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json()['response']
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error generando: {e}")
            return None
    
    def generar_examen(self, contenido_documento: str, 
                      num_preguntas: Dict[str, int] = None,
                      callback_progreso = None) -> List[PreguntaExamen]:
        """Genera examen usando Ollama"""
        
        if num_preguntas is None:
            num_preguntas = {'multiple': 6, 'verdadero_falso': 4, 'corta': 2}
        
        if callback_progreso:
            callback_progreso(15, "Preparando prompt...")
        
        # Prompt optimizado
        contenido_corto = contenido_documento[:8000]
        total = sum(num_preguntas.values())
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Eres un experto en crear exámenes educativos. Generas preguntas claras basadas en el contenido proporcionado. Respondes SOLO con JSON válido.<|eot_id|><|start_header_id|>user<|end_header_id|>

Crea {total} preguntas basadas en este texto:

{contenido_corto}

REGLAS:
1. {num_preguntas.get('multiple', 0)} preguntas de opción múltiple (4 opciones)
2. {num_preguntas.get('verdadero_falso', 0)} preguntas verdadero/falso
3. {num_preguntas.get('corta', 0)} preguntas de respuesta corta
4. NO inventes información que no esté en el texto

Responde SOLO con JSON:
{{
  "preguntas": [
    {{
      "tipo": "multiple",
      "pregunta": "¿Pregunta?",
      "opciones": ["A) opción 1", "B) opción 2", "C) opción 3", "D) opción 4"],
      "respuesta_correcta": "A",
      "puntos": 3
    }},
    {{
      "tipo": "verdadero_falso",
      "pregunta": "Afirmación",
      "respuesta_correcta": "verdadero",
      "puntos": 2
    }},
    {{
      "tipo": "corta",
      "pregunta": "Pregunta abierta",
      "respuesta_correcta": "Respuesta esperada",
      "puntos": 3
    }}
  ]
}}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        
        if callback_progreso:
            callback_progreso(25, "Generando con Ollama + GPU...")
        
        print(f"🤖 Generando {total} preguntas con {self.modelo}...")
        respuesta = self._generar_respuesta(prompt, max_tokens=3000, temperature=0.25)
        
        if not respuesta:
            print("❌ No se obtuvo respuesta de Ollama")
            return []
        
        if callback_progreso:
            callback_progreso(70, "Procesando respuesta...")
        
        # Extraer JSON
        try:
            # Buscar JSON en la respuesta
            inicio = respuesta.find('{')
            fin = respuesta.rfind('}') + 1
            
            if inicio >= 0 and fin > inicio:
                json_str = respuesta[inicio:fin]
                datos = json.loads(json_str)
                
                preguntas = []
                for p in datos.get('preguntas', []):
                    preguntas.append(PreguntaExamen.from_dict(p))
                
                print(f"✅ {len(preguntas)} preguntas generadas")
                return preguntas
            else:
                print("❌ No se encontró JSON válido en la respuesta")
                print(f"Respuesta: {respuesta[:500]}")
                return []
                
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando JSON: {e}")
            print(f"Respuesta: {respuesta[:500]}")
            return []


# Función de utilidad
def listar_modelos_ollama():
    """Lista modelos disponibles en Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            modelos = response.json().get('models', [])
            print("\n📦 Modelos disponibles en Ollama:")
            for m in modelos:
                print(f"  - {m['name']} ({m.get('size', 0) / 1e9:.1f} GB)")
            return modelos
        else:
            print("⚠️ No se pudo obtener la lista de modelos")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Asegúrate de que Ollama esté corriendo: ollama serve")
        return []


if __name__ == "__main__":
    # Test
    print("🧪 Test de GeneradorExamenesOllama\n")
    
    listar_modelos_ollama()
    
    print("\n" + "="*60)
    contenido = """
    Python es un lenguaje de programación interpretado de alto nivel.
    Fue creado por Guido van Rossum en 1991. Python usa indentación 
    para delimitar bloques de código en lugar de llaves. Es muy popular
    para ciencia de datos, inteligencia artificial y desarrollo web.
    """
    
    generador = GeneradorExamenesOllama(modelo="llama3.2:3b")
    preguntas = generador.generar_examen(
        contenido, 
        {'multiple': 3, 'verdadero_falso': 2, 'corta': 1}
    )
    
    print(f"\n📝 Preguntas generadas:")
    for i, p in enumerate(preguntas, 1):
        print(f"\n{i}. [{p.tipo}] {p.pregunta}")
        if p.opciones:
            for op in p.opciones:
                print(f"   {op}")
        print(f"   ✓ Respuesta: {p.respuesta_correcta}")
