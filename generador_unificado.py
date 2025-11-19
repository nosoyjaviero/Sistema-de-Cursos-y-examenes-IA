"""
Adaptador para usar Ollama o llama-cpp-python de forma transparente
"""
from pathlib import Path
from typing import List, Dict, Optional
import json
import requests
from generador_examenes import PreguntaExamen


class GeneradorUnificado:
    """Generador que puede usar Ollama o llama-cpp-python"""
    
    def __init__(self, usar_ollama: bool = True, modelo_ollama: str = "llama3.2:3b", 
                 modelo_path_gguf: str = None, n_gpu_layers: int = 35):
        self.usar_ollama = usar_ollama
        self.modelo_ollama = modelo_ollama
        # Convertir path relativo a absoluto
        if modelo_path_gguf:
            from pathlib import Path
            modelo_path = Path(modelo_path_gguf)
            if not modelo_path.is_absolute():
                modelo_path = Path.cwd() / modelo_path
            self.modelo_path_gguf = str(modelo_path)
        else:
            self.modelo_path_gguf = None
        self.n_gpu_layers = n_gpu_layers
        self.llm = None
        
        if usar_ollama:
            self._verificar_ollama()
        else:
            self._cargar_modelo_gguf()
    
    def _verificar_ollama(self):
        """Verifica que Ollama esté disponible"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                modelos = response.json().get('models', [])
                print(f"✅ Ollama activo - {len(modelos)} modelos")
                if not any(m['name'].startswith(self.modelo_ollama.split(':')[0]) for m in modelos):
                    print(f"⚠️ Modelo {self.modelo_ollama} no encontrado")
                    print(f"   Ejecuta: ollama pull {self.modelo_ollama}")
            else:
                print("⚠️ Ollama no responde")
                self.usar_ollama = False
        except Exception as e:
            print(f"❌ Ollama no disponible: {e}")
            print("💡 Usando llama-cpp-python como fallback")
            self.usar_ollama = False
            if self.modelo_path_gguf:
                self._cargar_modelo_gguf()
    
    def _cargar_modelo_gguf(self):
        """Carga modelo GGUF con llama-cpp-python"""
        if not self.modelo_path_gguf:
            print("⚠️ No hay modelo GGUF configurado")
            return
        
        try:
            from llama_cpp import Llama
            print(f"🔄 Cargando GGUF: {self.modelo_path_gguf}")
            self.llm = Llama(
                model_path=self.modelo_path_gguf,
                n_ctx=8192,
                n_threads=6,
                n_gpu_layers=self.n_gpu_layers,
                verbose=False
            )
            gpu_info = f"GPU activada ({self.n_gpu_layers} capas)" if self.n_gpu_layers > 0 else "Solo CPU"
            print(f"✅ Modelo GGUF cargado - {gpu_info}")
        except Exception as e:
            print(f"❌ Error cargando GGUF: {e}")
            self.llm = None
    
    def _generar_ollama(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Genera con Ollama"""
        try:
            print(f"\n{'='*60}")
            print(f"🎮 USANDO GPU - Modelo Ollama: {self.modelo_ollama}")
            print(f"⚙️  Configuración:")
            print(f"   • Temperature: {temperature}")
            print(f"   • Max tokens: {max_tokens}")
            print(f"   • GPU: Activada automáticamente por Ollama")
            print(f"   • Prompt length: {len(prompt)} caracteres")
            print(f"{'='*60}\n")
            
            # Debug: mostrar inicio del prompt
            print(f"📝 INICIO DEL PROMPT (primeros 500 chars):")
            print(f"{prompt[:500]}")
            print(f"...\n")
            
            # Timeout más largo para modelos grandes como deepseek-r1
            timeout_segundos = 600  # 10 minutos
            print(f"⏱️  Timeout configurado: {timeout_segundos} segundos (10 minutos)")
            print(f"💡 Modelos grandes pueden tardar varios minutos...")
            print(f"🚀 Enviando request a Ollama...\n")
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.modelo_ollama,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                        "stop": ["<|eot_id|>", "<|end_of_text|>"]
                    }
                },
                timeout=timeout_segundos
            )
            
            print(f"📬 Response status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Generación completada con GPU\n")
                respuesta_json = response.json()
                respuesta_completa = respuesta_json.get('response', '')
                
                if not respuesta_completa:
                    print(f"⚠️ ADVERTENCIA: Respuesta vacía")
                    print(f"   JSON completo: {respuesta_json}")
                    return None
                
                # Debug: Guardar respuesta completa
                print(f"📝 Longitud de respuesta: {len(respuesta_completa)} caracteres")
                print(f"📄 Primeros 500 caracteres:\n{respuesta_completa[:500]}\n")
                if len(respuesta_completa) > 500:
                    print(f"📄 Últimos 500 caracteres:\n{respuesta_completa[-500:]}\n")
                
                return respuesta_completa
            else:
                error_detail = response.text if response.text else "Sin detalles"
                print(f"❌ Error Ollama {response.status_code}")
                print(f"   Detalles: {error_detail[:500]}")
                return None
        except requests.exceptions.Timeout:
            print(f"⏱️ TIMEOUT: La generación excedió {timeout_segundos} segundos")
            print(f"   Considera usar menos preguntas o un modelo más pequeño")
            return None
        except Exception as e:
            print(f"❌ Error Ollama: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _generar_ollama_chat(self, messages: list, max_tokens: int, temperature: float) -> str:
        """Genera con Ollama usando API de chat (mantiene historial/contexto)"""
        try:
            print(f"\n{'='*60}")
            print(f"💬 CHAT CON CONTEXTO - Modelo Ollama: {self.modelo_ollama}")
            print(f"⚙️  Configuración:")
            print(f"   • Temperature: {temperature}")
            print(f"   • Max tokens: {max_tokens}")
            print(f"   • Mensajes en historial: {len(messages)}")
            print(f"   • GPU: Activada automáticamente por Ollama")
            print(f"{'='*60}\n")
            
            # Debug: mostrar estructura de mensajes
            print(f"📜 Estructura del chat:")
            for i, msg in enumerate(messages):
                role = msg.get('role', 'unknown')
                content_preview = msg.get('content', '')[:100]
                print(f"   {i+1}. {role}: {content_preview}...")
            print()
            
            # Timeout más largo para modelos grandes
            timeout_segundos = 600  # 10 minutos
            print(f"⏱️  Timeout configurado: {timeout_segundos} segundos")
            print(f"🚀 Enviando request a Ollama API de chat...\n")
            
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": self.modelo_ollama,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                        "stop": ["<|eot_id|>", "<|end_of_text|>"]
                    }
                },
                timeout=timeout_segundos
            )
            
            print(f"📬 Response status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Generación completada con GPU y contexto\n")
                respuesta_json = response.json()
                
                # La API de chat devuelve el mensaje en un formato diferente
                mensaje_respuesta = respuesta_json.get('message', {})
                respuesta_completa = mensaje_respuesta.get('content', '')
                
                if not respuesta_completa:
                    print(f"⚠️ ADVERTENCIA: Respuesta vacía")
                    print(f"   JSON completo: {respuesta_json}")
                    return None
                
                # Debug: Guardar respuesta completa
                print(f"📝 Longitud de respuesta: {len(respuesta_completa)} caracteres")
                print(f"📄 Primeros 300 caracteres:\n{respuesta_completa[:300]}\n")
                
                return respuesta_completa
            else:
                error_detail = response.text if response.text else "Sin detalles"
                print(f"❌ Error Ollama {response.status_code}")
                print(f"   Detalles: {error_detail[:500]}")
                return None
        except requests.exceptions.Timeout:
            print(f"⏱️ TIMEOUT: La generación excedió {timeout_segundos} segundos")
            print(f"   Considera reducir el historial o usar un modelo más pequeño")
            return None
        except Exception as e:
            print(f"❌ Error Ollama Chat: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _generar_gguf(self, prompt: str, max_tokens: int, temperature: float, 
                     top_p: float, repeat_penalty: float) -> str:
        """Genera con llama-cpp-python"""
        if not self.llm:
            return None
        
        try:
            resp = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                repeat_penalty=repeat_penalty,
                stop=["<|eot_id|>", "<|end_of_text|>", "```"]
            )
            return resp['choices'][0]['text']
        except Exception as e:
            print(f"❌ Error GGUF: {e}")
            return None
    
    def generar_examen(self, contenido_documento: str, 
                      num_preguntas: Dict[str, int] = None,
                      callback_progreso = None,
                      ajustes_modelo: dict = None,
                      archivos: list = None,
                      session_id: str = None,
                      sin_prompt_sistema: bool = False) -> List[PreguntaExamen]:
        """Genera examen usando Ollama o GGUF
        sin_prompt_sistema: Si es True, usa el contenido directamente sin agregar instrucciones
        """
        
        if num_preguntas is None:
            num_preguntas = {'multiple': 6, 'verdadero_falso': 4, 'corta': 2}
        
        if ajustes_modelo is None:
            ajustes_modelo = {
                'temperature': 0.25,
                'max_tokens': 3000,
                'top_p': 0.9,
                'repeat_penalty': 1.15
            }
        
        if callback_progreso:
            callback_progreso(15, "Preparando prompt...")
        
        # Verificar que contenido_documento es un string
        if not isinstance(contenido_documento, str):
            print(f"❌ ERROR: contenido_documento no es string, es {type(contenido_documento)}")
            raise TypeError(f"contenido_documento debe ser string, recibido: {type(contenido_documento)}")
        
        # Crear prompt
        contenido_corto = contenido_documento[:8000]
        total = sum(num_preguntas.values())
        
        if sin_prompt_sistema:
            # Modo prompt personalizado: usar contenido directamente
            prompt = contenido_corto
            print(f"🎯 MODO PROMPT PERSONALIZADO: Usando prompt del usuario directamente")
        else:
            # Modo normal: agregar formato del sistema
            prompt = self._crear_prompt(contenido_corto, num_preguntas, total)
        
        if callback_progreso:
            motor = "Ollama + GPU" if self.usar_ollama else "llama-cpp-python"
            callback_progreso(25, f"Generando con {motor}...")
        
        # Generar
        print(f"\n{'='*60}")
        print(f"🤖 Generando {total} preguntas con IA...")
        print(f"{'='*60}")
        
        if self.usar_ollama:
            respuesta = self._generar_ollama(
                prompt, 
                ajustes_modelo['max_tokens'], 
                ajustes_modelo['temperature']
            )
        else:
            respuesta = self._generar_gguf(
                prompt,
                ajustes_modelo['max_tokens'],
                ajustes_modelo['temperature'],
                ajustes_modelo['top_p'],
                ajustes_modelo['repeat_penalty']
            )
        
        if not respuesta:
            print("❌ No se obtuvo respuesta")
            return []
        
        if callback_progreso:
            callback_progreso(70, "Procesando respuesta...")
        
        # Parsear JSON
        preguntas = self._extraer_preguntas(respuesta, num_preguntas)
        
        if callback_progreso:
            callback_progreso(100, f"¡{len(preguntas)} preguntas generadas!")
        
        return preguntas
    
    def _crear_prompt(self, contenido: str, num_preguntas: Dict[str, int], total: int) -> str:
        """Crea el prompt optimizado"""
        # Construir lista detallada de tipos de preguntas
        tipos_detalle = []
        if num_preguntas.get('multiple', 0) > 0:
            tipos_detalle.append(f"{num_preguntas['multiple']} de opción múltiple (4 opciones A/B/C/D, puntos: 3)")
        if num_preguntas.get('verdadero_falso', 0) > 0:
            tipos_detalle.append(f"{num_preguntas['verdadero_falso']} verdadero/falso (puntos: 2)")
        if num_preguntas.get('corta', 0) > 0:
            tipos_detalle.append(f"{num_preguntas['corta']} de respuesta corta (puntos: 3)")
        if num_preguntas.get('desarrollo', 0) > 0:
            tipos_detalle.append(f"{num_preguntas['desarrollo']} de desarrollo/ensayo (puntos: 5)")
        
        tipos_str = "\n".join([f"{i+1}. {t}" for i, t in enumerate(tipos_detalle)])
        
        return f"""Eres un experto en crear exámenes educativos. Genera EXACTAMENTE {total} preguntas basadas en el siguiente contenido.

CONTENIDO:
{contenido}

INSTRUCCIONES CRÍTICAS:
{tipos_str}

REQUISITOS:
- Genera EXACTAMENTE {total} preguntas en total
- NO repitas preguntas
- Todas las preguntas deben ser DIFERENTES
- NO inventes información que no esté en el texto
- Responde ÚNICAMENTE con JSON válido, sin texto adicional

FORMATO JSON REQUERIDO:
{{
  "preguntas": [
    {{
      "tipo": "multiple",
      "pregunta": "¿Pregunta clara y específica?",
      "opciones": ["A) opción 1", "B) opción 2", "C) opción 3", "D) opción 4"],
      "respuesta_correcta": "A",
      "puntos": 3
    }},
    {{
      "tipo": "verdadero_falso",
      "pregunta": "Afirmación clara",
      "respuesta_correcta": "verdadero",
      "puntos": 2
    }},
    {{
      "tipo": "corta",
      "pregunta": "Pregunta de respuesta corta",
      "respuesta_correcta": "Respuesta esperada breve",
      "puntos": 3
    }},
    {{
      "tipo": "desarrollo",
      "pregunta": "Pregunta de desarrollo que requiere análisis profundo",
      "respuesta_correcta": "Respuesta esperada detallada con conceptos clave",
      "puntos": 5
    }}
  ]
}}

Genera ahora las {total} preguntas:
"""
    
    def _extraer_preguntas(self, respuesta: str, num_preguntas: Dict[str, int] = None) -> List[PreguntaExamen]:
        """Extrae preguntas del JSON"""
        try:
            print(f"\n{'='*60}")
            print(f"🔍 EXTRAYENDO JSON DE LA RESPUESTA")
            print(f"{'='*60}")
            
            # Estrategia 1: Buscar JSON completo balanceado
            inicio = respuesta.find('{')
            if inicio >= 0:
                # Encontrar el cierre balanceado del JSON
                nivel = 0
                fin = inicio
                en_string = False
                escape = False
                
                for i in range(inicio, len(respuesta)):
                    char = respuesta[i]
                    
                    if escape:
                        escape = False
                        continue
                    
                    if char == '\\':
                        escape = True
                        continue
                    
                    if char == '"':
                        en_string = not en_string
                        continue
                    
                    if not en_string:
                        if char == '{':
                            nivel += 1
                        elif char == '}':
                            nivel -= 1
                            if nivel == 0:
                                fin = i + 1
                                break
                
                # Si no se encontró cierre balanceado, tomar hasta el final
                if fin == inicio and inicio >= 0:
                    print(f"⚠️ JSON sin cierre balanceado, tomando hasta el final")
                    fin = len(respuesta)
                
                if fin > inicio:
                    json_str = respuesta[inicio:fin]
                    print(f"✅ JSON encontrado en posición {inicio}-{fin}")
                    print(f"📄 JSON extraído (primeros 300 chars):\n{json_str[:300]}...\n")
                    
                    # Limpiar JSON de errores comunes del modelo
                    import re
                    
                    # 1. Eliminar comas antes de ] o }
                    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
                    
                    # 2. Si el JSON termina incompleto, intentar repararlo
                    # Buscar campos incompletos tipo: "explanation": "
                    json_str = re.sub(r'"\s*:\s*"[^"]*$', '": "Explicación no disponible"', json_str)
                    
                    # 3. Asegurar cierre de objetos y arrays
                    # Contar llaves y corchetes abiertos
                    count_braces = json_str.count('{') - json_str.count('}')
                    count_brackets = json_str.count('[') - json_str.count(']')
                    
                    # Cerrar los que falten
                    if count_braces > 0 or count_brackets > 0:
                        print(f"⚠️ JSON incompleto: {count_braces} llaves, {count_brackets} corchetes sin cerrar")
                        # Cerrar en orden inverso (primero objetos, luego arrays)
                        json_str += '}' * count_braces
                        json_str += ']' * count_brackets
                        print(f"🔧 JSON reparado automáticamente")
                    
                    # Intentar parsear
                    try:
                        datos = json.loads(json_str)
                        print(f"✅ JSON parseado correctamente")
                        
                        # Verificar estructura - aceptar 'preguntas' o 'questions'
                        campo_preguntas = None
                        if 'preguntas' in datos:
                            campo_preguntas = 'preguntas'
                        elif 'questions' in datos:
                            campo_preguntas = 'questions'
                        
                        if not campo_preguntas:
                            print(f"❌ JSON no tiene campo 'preguntas' ni 'questions'")
                            print(f"📋 Campos encontrados: {list(datos.keys())}")
                            
                            # Si el JSON es un array directamente, usarlo
                            if isinstance(datos, list):
                                print(f"💡 El JSON es un array directo con {len(datos)} elementos")
                                campo_preguntas = None
                                lista_preguntas = datos
                            else:
                                return []
                        else:
                            lista_preguntas = datos.get(campo_preguntas, [])
                        
                        preguntas = []
                        for i, p in enumerate(lista_preguntas):
                            try:
                                pregunta = PreguntaExamen.from_dict(p)
                                preguntas.append(pregunta)
                                tipo = p.get('tipo') or p.get('type', 'unknown')
                                texto = p.get('pregunta') or p.get('question', '')
                                print(f"✅ Pregunta {i+1}: {tipo} - {texto[:50]}...")
                            except Exception as e:
                                print(f"❌ Error en pregunta {i+1}: {e}")
                                continue
                        
                        print(f"\n✅ Total: {len(preguntas)} preguntas generadas exitosamente")
                        
                        # FILTRAR PREGUNTAS POR TIPO Y CANTIDAD SOLICITADA
                        if num_preguntas and any(v > 0 for v in num_preguntas.values()):
                            preguntas_filtradas = []
                            contador_por_tipo = {}
                            
                            # Mapeo de tipos nuevos a tipos del sistema
                            mapeo_tipos = {
                                'flashcard': 'flashcard',
                                'mcq': 'mcq', 
                                'true_false': 'true_false',
                                'verdadero_falso': 'true_false',
                                'cloze': 'cloze',
                                'short_answer': 'short_answer',
                                'respuesta_corta': 'short_answer',
                                'open_question': 'open_question',
                                'desarrollo': 'open_question',
                                'case_study': 'case_study',
                                'caso_estudio': 'case_study',
                                'reading_comprehension': 'reading_comprehension',
                                'reading_true_false': 'reading_true_false',
                                'reading_cloze': 'reading_cloze',
                                'reading_skill': 'reading_skill',
                                'reading_matching': 'reading_matching',
                                'reading_sequence': 'reading_sequence',
                                'writing_short': 'writing_short',
                                'writing_paraphrase': 'writing_paraphrase',
                                'writing_correction': 'writing_correction',
                                'writing_transformation': 'writing_transformation',
                                'writing_essay': 'writing_essay',
                                'writing_sentence_builder': 'writing_sentence_builder',
                                'writing_picture_description': 'writing_picture_description',
                                'writing_email': 'writing_email',
                                'multiple': 'mcq',
                                'corta': 'short_answer'
                            }
                            
                            for pregunta in preguntas:
                                tipo_normalizado = mapeo_tipos.get(pregunta.tipo, pregunta.tipo)
                                cantidad_solicitada = num_preguntas.get(tipo_normalizado, 0)
                                
                                if cantidad_solicitada > 0:
                                    if tipo_normalizado not in contador_por_tipo:
                                        contador_por_tipo[tipo_normalizado] = 0
                                    
                                    if contador_por_tipo[tipo_normalizado] < cantidad_solicitada:
                                        preguntas_filtradas.append(pregunta)
                                        contador_por_tipo[tipo_normalizado] += 1
                            
                            print(f"🔍 Filtrado: {len(preguntas)} generadas → {len(preguntas_filtradas)} solicitadas")
                            print(f"   Solicitadas: {num_preguntas}")
                            print(f"   Filtradas por tipo: {contador_por_tipo}")
                            return preguntas_filtradas
                        
                        return preguntas
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ Error parseando JSON: {e}")
                        print(f"📄 JSON problemático (primeros 500):\n{json_str[:500]}")
                        print(f"📄 Últimos 200 caracteres:\n{json_str[-200:]}")
                        return []
            
            # Estrategia 2: Buscar bloques de código markdown
            print("⚠️ No se encontró JSON directo, buscando en bloques markdown...")
            if "```json" in respuesta:
                print("💡 Se detectó bloque ```json```, intentando extraer...")
                inicio_markdown = respuesta.find("```json") + 7
                fin_markdown = respuesta.find("```", inicio_markdown)
                if fin_markdown > inicio_markdown:
                    json_str = respuesta[inicio_markdown:fin_markdown].strip()
                    print(f"✅ JSON encontrado en markdown")
                    try:
                        datos = json.loads(json_str)
                        # Aceptar 'preguntas' o 'questions'
                        lista_preguntas = datos.get('preguntas') or datos.get('questions', [])
                        if isinstance(datos, list):
                            lista_preguntas = datos
                        
                        preguntas = []
                        for p in lista_preguntas:
                            preguntas.append(PreguntaExamen.from_dict(p))
                        print(f"✅ {len(preguntas)} preguntas desde markdown")
                        return preguntas
                    except Exception as e:
                        print(f"❌ Error parseando markdown JSON: {e}")
            
            print("❌ No se pudo extraer JSON válido de la respuesta")
            return []
            
        except Exception as e:
            print(f"❌ Error general extrayendo JSON: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def evaluar_respuesta(self, pregunta: PreguntaExamen, respuesta_usuario) -> dict:
        """Evalúa una respuesta del usuario"""
        resultado = {
            "correcta": False,
            "puntos_obtenidos": 0,
            "feedback": ""
        }
        
        # Convertir lista a string si es necesario
        if isinstance(respuesta_usuario, list):
            respuesta_usuario = respuesta_usuario[0] if respuesta_usuario else ""
        
        # Validar que respuesta_usuario sea string
        if not isinstance(respuesta_usuario, str):
            respuesta_usuario = str(respuesta_usuario)
        
        if not respuesta_usuario or respuesta_usuario.strip() == "":
            resultado["feedback"] = "No se proporcionó respuesta"
            return resultado
        
        respuesta_usuario_lower = respuesta_usuario.strip().lower()
        respuesta_correcta = pregunta.respuesta_correcta
        if respuesta_correcta is None:
            respuesta_correcta = ""
        elif not isinstance(respuesta_correcta, str):
            respuesta_correcta = str(respuesta_correcta)
        respuesta_correcta_lower = respuesta_correcta.strip().lower()
        
        if pregunta.tipo == "multiple" or pregunta.tipo == "mcq":
            # Para múltiple, solo comparar la letra (A, B, C, D)
            if respuesta_usuario_lower in respuesta_correcta_lower or respuesta_correcta_lower in respuesta_usuario_lower:
                resultado["correcta"] = True
                resultado["puntos_obtenidos"] = pregunta.puntos
                resultado["feedback"] = "¡Correcto!"
            else:
                resultado["feedback"] = f"Incorrecto. La respuesta correcta es: {pregunta.respuesta_correcta}"
        
        elif pregunta.tipo == "verdadero_falso" or pregunta.tipo == "true_false":
            if respuesta_usuario_lower == respuesta_correcta_lower:
                resultado["correcta"] = True
                resultado["puntos_obtenidos"] = pregunta.puntos
                resultado["feedback"] = "¡Correcto!"
            else:
                resultado["feedback"] = f"Incorrecto. La respuesta correcta es: {pregunta.respuesta_correcta}"
        
        elif pregunta.tipo in ["corta", "desarrollo", "short_answer", "open_question", "case_study",
                               "flashcard", "cloze",
                               "reading_comprehension", "reading_true_false", "reading_cloze", 
                               "reading_skill", "reading_matching", "reading_sequence",
                               "writing_short", "writing_paraphrase", "writing_correction",
                               "writing_transformation", "writing_essay", "writing_sentence_builder",
                               "writing_picture_description", "writing_email"]:
            # Para todos los demás tipos, usar IA para evaluar
            print(f"\n🤖 Evaluando respuesta de tipo '{pregunta.tipo}' con IA...")
            resultado = self._evaluar_con_ia(pregunta, respuesta_usuario)
        
        else:
            # Tipo desconocido - evaluar con IA por defecto
            print(f"\n⚠️ Tipo de pregunta desconocido: '{pregunta.tipo}' - usando evaluación con IA")
            resultado = self._evaluar_con_ia(pregunta, respuesta_usuario)
        
        return resultado
    
    def _evaluar_con_ia(self, pregunta: PreguntaExamen, respuesta_usuario: str) -> dict:
        """Evalúa una respuesta de desarrollo/corta usando IA"""
        
        # Extraer respuesta correcta dependiendo del tipo
        respuesta_modelo = pregunta.respuesta_correcta
        
        # Si es un diccionario (flashcard), extraer el campo 'answer'
        if isinstance(respuesta_modelo, dict):
            respuesta_modelo = respuesta_modelo.get('answer', str(respuesta_modelo))
        
        # Convertir a string si no lo es
        if not isinstance(respuesta_modelo, str):
            respuesta_modelo = str(respuesta_modelo)
        
        prompt = f"""Eres un profesor evaluando una respuesta de estudiante. Compara la respuesta del estudiante con la respuesta modelo y proporciona retroalimentación específica.

PREGUNTA:
{pregunta.pregunta}

RESPUESTA MODELO (lo que se esperaba):
{respuesta_modelo}

RESPUESTA DEL ESTUDIANTE:
{respuesta_usuario}

PUNTOS MÁXIMOS: {pregunta.puntos}

INSTRUCCIONES DE EVALUACIÓN:
1. Identifica los CONCEPTOS CLAVE en la respuesta modelo
2. Verifica cuáles de esos conceptos están presentes en la respuesta del estudiante
3. Identifica qué conceptos FALTAN o están INCOMPLETOS
4. Asigna puntos proporcionales a los conceptos presentes
5. Proporciona retroalimentación ESPECÍFICA sobre qué falta comprender

Responde ÚNICAMENTE con JSON en este formato exacto:
{{
  "puntos": <número decimal de 0 a {pregunta.puntos}>,
  "conceptos_correctos": ["concepto1", "concepto2"],
  "conceptos_faltantes": ["concepto3", "concepto4"],
  "feedback": "Retroalimentación específica explicando qué conceptos domina y cuáles le faltan comprender"
}}

JSON:"""

        try:
            if self.usar_ollama:
                # Evaluar con Ollama
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={{
                        "model": self.modelo_ollama,
                        "prompt": prompt,
                        "stream": False,
                        "options": {{
                            "temperature": 0.3,  # Más determinístico
                            "num_predict": 400   # Más tokens para retroalimentación detallada
                        }}
                    }},
                    timeout=60
                )
                
                if response.status_code == 200:
                    respuesta_ia = response.json()['response']
                    print(f"📝 Respuesta IA (primeros 300 chars): {{respuesta_ia[:300]}}")
                    
                    # Extraer JSON balanceado
                    inicio = respuesta_ia.find('{{')
                    if inicio >= 0:
                        nivel = 0
                        fin = inicio
                        en_string = False
                        escape = False
                        
                        for i in range(inicio, len(respuesta_ia)):
                            char = respuesta_ia[i]
                            
                            if escape:
                                escape = False
                                continue
                            
                            if char == '\\\\':
                                escape = True
                                continue
                            
                            if char == '"':
                                en_string = not en_string
                                continue
                            
                            if not en_string:
                                if char == '{{':
                                    nivel += 1
                                elif char == '}}':
                                    nivel -= 1
                                    if nivel == 0:
                                        fin = i + 1
                                        break
                        
                        if fin > inicio:
                            json_str = respuesta_ia[inicio:fin]
                            evaluacion = json.loads(json_str)
                            
                            puntos = float(evaluacion.get('puntos', 0))
                            conceptos_correctos = evaluacion.get('conceptos_correctos', [])
                            conceptos_faltantes = evaluacion.get('conceptos_faltantes', [])
                            feedback_base = evaluacion.get('feedback', 'Sin evaluación')
                            
                            # Construir feedback detallado
                            feedback = feedback_base
                            if conceptos_correctos:
                                feedback += f"\\n\\n✅ Conceptos que dominas: {{', '.join(conceptos_correctos)}}"
                            if conceptos_faltantes:
                                feedback += f"\\n\\n❌ Conceptos que te faltan comprender: {{', '.join(conceptos_faltantes)}}"
                            
                            print(f"✅ Evaluación: {{puntos}}/{{pregunta.puntos}} puntos")
                            print(f"✅ Conceptos correctos: {{conceptos_correctos}}")
                            print(f"❌ Conceptos faltantes: {{conceptos_faltantes}}")
                            
                            return {{
                                "correcta": puntos >= pregunta.puntos * 0.6,  # 60% o más es correcto
                                "puntos_obtenidos": puntos,
                                "feedback": feedback,
                                "conceptos_correctos": conceptos_correctos,
                                "conceptos_faltantes": conceptos_faltantes
                            }}
            
            # Fallback: evaluación simple por palabras clave
            print("⚠️ Usando evaluación fallback")
            palabras_correctas = set(pregunta.respuesta_correcta.lower().split())
            palabras_usuario = set(respuesta_usuario.lower().split())
            coincidencias = len(palabras_correctas.intersection(palabras_usuario))
            similitud = coincidencias / len(palabras_correctas) if palabras_correctas else 0
            
            puntos = pregunta.puntos * similitud
            
            if similitud >= 0.7:
                feedback = "¡Excelente! Respuesta muy completa."
            elif similitud >= 0.5:
                feedback = "Bien, pero podrías agregar más detalles."
            elif similitud >= 0.3:
                feedback = "Parcialmente correcto, faltan conceptos clave."
            else:
                feedback = f"Incompleto. Respuesta esperada: {pregunta.respuesta_correcta}"
            
            return {
                "correcta": similitud >= 0.6,
                "puntos_obtenidos": round(puntos, 1),
                "feedback": feedback
            }
            
        except Exception as e:
            print(f"❌ Error evaluando con IA: {e}")
            # Fallback
            return {
                "correcta": False,
                "puntos_obtenidos": 0,
                "feedback": f"Error en evaluación. Respuesta esperada: {pregunta.respuesta_correcta}"
            }


# Función de utilidad para verificar qué usar
def detectar_backend_disponible():
    """Detecta qué backend está disponible"""
    # Verificar Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            modelos = response.json().get('models', [])
            if modelos:
                print("✅ Ollama disponible con GPU automática")
                return "ollama", modelos[0]['name']
    except:
        pass
    
    # Verificar llama-cpp-python
    try:
        from llama_cpp import Llama
        print("✅ llama-cpp-python disponible")
        return "gguf", None
    except:
        pass
    
    print("⚠️ No hay backend disponible")
    return None, None


if __name__ == "__main__":
    # Test
    print("🧪 Test de GeneradorUnificado\n")
    
    backend, modelo = detectar_backend_disponible()
    
    if backend == "ollama":
        print(f"\n📦 Usando Ollama con {modelo}")
        generador = GeneradorUnificado(usar_ollama=True, modelo_ollama=modelo)
    else:
        print("\n📦 Usando llama-cpp-python")
        generador = GeneradorUnificado(usar_ollama=False, modelo_path_gguf="modelos/tu_modelo.gguf")
    
    contenido = """
    Python es un lenguaje de programación interpretado de alto nivel.
    Fue creado por Guido van Rossum en 1991.
    """
    
    preguntas = generador.generar_examen(
        contenido,
        {'multiple': 2, 'verdadero_falso': 1}
    )
    
    print(f"\n📝 Preguntas generadas: {len(preguntas)}")
