"""
Adaptador para usar Ollama o llama-cpp-python de forma transparente
"""
from pathlib import Path
from typing import List, Dict, Optional
import json
import requests
from datetime import datetime
from generador_examenes import PreguntaExamen


class GeneradorUnificado:
    """Generador que puede usar Ollama o llama-cpp-python"""
    
    def __init__(self, usar_ollama: bool = True, modelo_ollama: str = "llama3.2:3b", 
                 modelo_path_gguf: str = None, n_gpu_layers: int = 35):
        self.usar_ollama = usar_ollama
        self.modelo_ollama = modelo_ollama
        # Convertir path relativo a absoluto
        if modelo_path_gguf:
            modelo_path = Path(modelo_path_gguf)
            if not modelo_path.is_absolute():
                modelo_path = Path.cwd() / modelo_path
            self.modelo_path_gguf = str(modelo_path)
        else:
            self.modelo_path_gguf = None
        self.n_gpu_layers = n_gpu_layers
        self.llm = None
        
        # Sistema de logging detallado
        self.log_dir = Path("logs_practicas_detallado")
        self.log_dir.mkdir(exist_ok=True)
        self.current_log_file = None
        self.log_data = {}
        
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
    
    def _iniciar_log(self):
        """Inicia un nuevo archivo de log para esta consulta en carpeta única"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Crear carpeta única para esta consulta
        carpeta_consulta = self.log_dir / f"practica_{timestamp}"
        carpeta_consulta.mkdir(parents=True, exist_ok=True)
        
        # Archivo de log dentro de la carpeta
        self.current_log_file = carpeta_consulta / f"practica_{timestamp}.log"
        
        self.log_data = {
            "timestamp": timestamp,
            "fecha_hora": datetime.now().isoformat(),
            "request": {},
            "prompt_enviado": "",
            "respuesta_modelo": "",
            "json_extraido": "",
            "preguntas_parseadas": [],
            "filtrado": {},
            "resultado_final": [],
            "errores": []
        }
        print(f"\n📋 Log detallado: {self.current_log_file}")
    
    def _agregar_log(self, seccion: str, datos: dict):
        """Agrega información a una sección del log"""
        if seccion in self.log_data:
            if isinstance(self.log_data[seccion], dict):
                self.log_data[seccion].update(datos)
            elif isinstance(self.log_data[seccion], list):
                self.log_data[seccion].append(datos)
            else:
                self.log_data[seccion] = datos
        else:
            self.log_data[seccion] = datos
    
    def _guardar_log(self):
        """Guarda el log completo en archivo"""
        if not self.current_log_file:
            return
        
        try:
            # Determinar si fue exitoso o falló
            errores = self.log_data.get('errores', [])
            resultado_final = self.log_data.get('resultado_final', [])
            num_preguntas_solicitadas = sum(self.log_data.get('request', {}).get('num_preguntas', {}).values())
            num_preguntas_generadas = len(resultado_final)
            
            exitoso = len(errores) == 0 and num_preguntas_generadas > 0
            estado = "✅ EXITOSO" if exitoso else "❌ FALLÓ"
            
            # Crear versión legible
            with open(self.current_log_file, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("LOG DETALLADO DE GENERACIÓN DE PRÁCTICA\n")
                f.write("="*80 + "\n\n")
                
                # RESUMEN EJECUTIVO
                f.write("🎯 RESUMEN EJECUTIVO\n")
                f.write("-"*80 + "\n")
                f.write(f"Estado: {estado}\n")
                f.write(f"Fecha/Hora: {self.log_data['fecha_hora']}\n")
                f.write(f"Preguntas solicitadas: {num_preguntas_solicitadas}\n")
                f.write(f"Preguntas generadas: {num_preguntas_generadas}\n")
                
                if errores:
                    f.write(f"\n⚠️ ERRORES ENCONTRADOS ({len(errores)}):\n")
                    for i, error in enumerate(errores, 1):
                        f.write(f"  {i}. {error}\n")
                else:
                    f.write(f"\n✅ Sin errores\n")
                
                # Detalles del filtrado si existe
                filtrado = self.log_data.get('filtrado', {})
                if filtrado:
                    f.write(f"\nFiltrado:\n")
                    f.write(f"  • Total generadas: {filtrado.get('total_generadas', 0)}\n")
                    f.write(f"  • Total filtradas: {filtrado.get('total_filtradas', 0)}\n")
                    contador = filtrado.get('contador_por_tipo', {})
                    if contador:
                        f.write(f"  • Por tipo: {contador}\n")
                
                f.write("\n" + "="*80 + "\n\n")
                
                # REQUEST RECIBIDO
                f.write("-"*80 + "\n")
                f.write("1. REQUEST RECIBIDO DEL FRONTEND\n")
                f.write("-"*80 + "\n")
                for key, value in self.log_data.get('request', {}).items():
                    f.write(f"{key}: {value}\n")
                f.write("\n")
                
                # PROMPT ENVIADO AL MODELO
                f.write("-"*80 + "\n")
                f.write("2. PROMPT ENVIADO AL MODELO\n")
                f.write("-"*80 + "\n")
                f.write(f"Longitud: {len(self.log_data.get('prompt_enviado', ''))} caracteres\n\n")
                f.write(self.log_data.get('prompt_enviado', 'No disponible'))
                f.write("\n\n")
                
                # RESPUESTA DEL MODELO
                f.write("-"*80 + "\n")
                f.write("3. RESPUESTA COMPLETA DEL MODELO\n")
                f.write("-"*80 + "\n")
                f.write(f"Longitud: {len(self.log_data.get('respuesta_modelo', ''))} caracteres\n\n")
                f.write(self.log_data.get('respuesta_modelo', 'No disponible'))
                f.write("\n\n")
                
                # JSON EXTRAÍDO
                f.write("-"*80 + "\n")
                f.write("4. JSON EXTRAÍDO Y PARSEADO\n")
                f.write("-"*80 + "\n")
                json_str = self.log_data.get('json_extraido', '')
                if json_str:
                    try:
                        json_obj = json.loads(json_str) if isinstance(json_str, str) else json_str
                        f.write(json.dumps(json_obj, indent=2, ensure_ascii=False))
                    except:
                        f.write(str(json_str))
                else:
                    f.write("No se extrajo JSON")
                f.write("\n\n")
                
                # PREGUNTAS PARSEADAS
                f.write("-"*80 + "\n")
                f.write("5. PREGUNTAS PARSEADAS (Objetos Python)\n")
                f.write("-"*80 + "\n")
                for i, pregunta in enumerate(self.log_data.get('preguntas_parseadas', []), 1):
                    f.write(f"\nPregunta {i}:\n")
                    f.write(json.dumps(pregunta, indent=2, ensure_ascii=False))
                    f.write("\n")
                f.write("\n")
                
                # FILTRADO
                f.write("-"*80 + "\n")
                f.write("6. PROCESO DE FILTRADO\n")
                f.write("-"*80 + "\n")
                filtrado = self.log_data.get('filtrado', {})
                for key, value in filtrado.items():
                    f.write(f"{key}: {value}\n")
                f.write("\n")
                
                # RESULTADO FINAL
                f.write("-"*80 + "\n")
                f.write("7. RESULTADO FINAL DEVUELTO AL FRONTEND\n")
                f.write("-"*80 + "\n")
                f.write(f"Total preguntas: {len(self.log_data.get('resultado_final', []))}\n\n")
                for i, pregunta in enumerate(self.log_data.get('resultado_final', []), 1):
                    f.write(f"\nPregunta {i}:\n")
                    f.write(json.dumps(pregunta, indent=2, ensure_ascii=False))
                    f.write("\n")
                f.write("\n")
                
                # ERRORES
                if self.log_data.get('errores'):
                    f.write("-"*80 + "\n")
                    f.write("8. ERRORES ENCONTRADOS\n")
                    f.write("-"*80 + "\n")
                    for error in self.log_data['errores']:
                        f.write(f"• {error}\n")
                    f.write("\n")
                
                f.write("="*80 + "\n")
                f.write("FIN DEL LOG\n")
                f.write("="*80 + "\n")
            
            # Guardar también versión JSON
            json_file = self.current_log_file.with_suffix('.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.log_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Log guardado: {self.current_log_file}")
            print(f"✅ JSON guardado: {json_file}")
            
        except Exception as e:
            print(f"❌ Error guardando log: {e}")
    
    def _generar_ollama(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Genera con Ollama"""
        try:
            # Detectar modelos lentos y ajustar solo el timeout
            es_deepseek = 'deepseek' in self.modelo_ollama.lower()
            
            # Determinar si se usa GPU basado en n_gpu_layers
            usar_gpu = self.n_gpu_layers > 0
            modo_gpu = "GPU activada" if usar_gpu else "Solo CPU"
            
            print(f"\n{'='*60}")
            print(f"🎮 Modelo Ollama: {self.modelo_ollama}")
            print(f"⚙️  Configuración:")
            print(f"   • Modo: {modo_gpu}")
            print(f"   • Temperature: {temperature}")
            print(f"   • Max tokens: {max_tokens}")
            print(f"   • Prompt length: {len(prompt)} caracteres")
            
            if es_deepseek:
                print(f"   • Modelo de razonamiento: DeepSeek-R1")
                print(f"   • Genera razonamiento interno antes de responder")
            print(f"{'='*60}\n")
            
            # Debug: mostrar inicio del prompt
            print(f"📝 INICIO DEL PROMPT (primeros 500 chars):")
            print(f"{prompt[:500]}")
            print(f"...\n")
            
            # Timeout ajustado según modelo (sin cambiar max_tokens)
            if es_deepseek:
                timeout_segundos = 1800  # 30 minutos para DeepSeek-R1
                print(f"⏱️  Timeout configurado: {timeout_segundos} segundos (30 minutos)")
                print(f"💡 DeepSeek-R1 hace razonamiento complejo y puede tardar mucho")
                print(f"💡 Vale la pena esperar por la calidad de sus respuestas...")
            else:
                timeout_segundos = 600  # 10 minutos para otros modelos
                print(f"⏱️  Timeout configurado: {timeout_segundos} segundos (10 minutos)")
                print(f"💡 Modelos grandes pueden tardar varios minutos...")
            print(f"💡 Modelos grandes pueden tardar varios minutos...")
            print(f"🚀 Enviando request a Ollama...\n")
            
            # Ajustar prompt para DeepSeek-R1 (permitir razonamiento, pero pedir JSON al final)
            prompt_final = prompt
            if es_deepseek:
                # DeepSeek-R1 es un modelo de razonamiento - dejarlo razonar pero pedir JSON al final
                prompt_final = f"""{prompt}

IMPORTANTE: Después de tu análisis, DEBES generar el JSON válido con la estructura solicitada.
El JSON debe comenzar con {{ y terminar con }}.
Puedes razonar primero, pero al final SIEMPRE incluye el JSON completo."""
                print(f"📝 Prompt adaptado para DeepSeek-R1 (permite razonamiento + JSON al final)\n")
            
            # Configurar opciones según modo GPU/CPU
            opciones = {
                "temperature": temperature,
                "num_predict": max_tokens,
                "stop": ["<|eot_id|>", "<|end_of_text|>", "\n\n\n"]
            }
            
            # Si n_gpu_layers es 0, forzar uso de CPU
            if not usar_gpu:
                opciones["num_gpu"] = 0
                print(f"🔷 Modo CPU forzado (num_gpu=0)\n")
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.modelo_ollama,
                    "prompt": prompt_final,
                    "stream": False,
                    "options": opciones
                },
                timeout=timeout_segundos
            )
            
            print(f"📬 Response status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Generación completada ({modo_gpu})\n")
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
            # Determinar si se usa GPU basado en n_gpu_layers
            usar_gpu = self.n_gpu_layers > 0
            modo_gpu = "GPU activada" if usar_gpu else "Solo CPU"
            
            print(f"\n{'='*60}")
            print(f"💬 CHAT CON CONTEXTO - Modelo Ollama: {self.modelo_ollama}")
            print(f"⚙️  Configuración:")
            print(f"   • Modo: {modo_gpu}")
            print(f"   • Temperature: {temperature}")
            print(f"   • Max tokens: {max_tokens}")
            print(f"   • Mensajes en historial: {len(messages)}")
            print(f"{'='*60}\n")
            
            # Debug: mostrar estructura de mensajes
            print(f"📜 Estructura del chat:")
            for i, msg in enumerate(messages):
                role = msg.get('role', 'unknown')
                content_preview = msg.get('content', '')[:100]
                print(f"   {i+1}. {role}: {content_preview}...")
            print()
            
            # Timeout más largo para modelos grandes
            timeout_segundos = 120  # 2 minutos (reducido para evitar cuelgues largos)
            print(f"⏱️  Timeout configurado: {timeout_segundos} segundos")
            print(f"🚀 Enviando request a Ollama API de chat...\n")
            
            # Configurar opciones según modo GPU/CPU
            opciones = {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_ctx": 8192,  # Contexto amplio para mantener conversaciones largas
                "stop": ["<|eot_id|>", "<|end_of_text|>"]
            }
            
            # Si n_gpu_layers es 0, forzar uso de CPU
            if not usar_gpu:
                opciones["num_gpu"] = 0
                print(f"🔷 Modo CPU forzado (num_gpu=0)\n")
            
            # Intentar primero con historial completo
            for intento in range(2):
                try:
                    # En el segundo intento, reducir historial si falla
                    messages_a_enviar = messages
                    if intento == 1:
                        print(f"🔄 Reintentando con historial reducido...")
                        # Mantener solo system + últimos 6 mensajes (3 intercambios)
                        messages_a_enviar = [messages[0]] + messages[-6:]
                        opciones["num_ctx"] = 4096  # Mantener contexto razonable en reintento
                    
                    response = requests.post(
                        "http://localhost:11434/api/chat",
                        json={
                            "model": self.modelo_ollama,
                            "messages": messages_a_enviar,
                            "stream": False,
                            "options": opciones
                        },
                        timeout=timeout_segundos
                    )
                    
                    print(f"📬 Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"✅ Generación completada ({modo_gpu} y contexto)\n")
                        respuesta_json = response.json()
                        
                        # La API de chat devuelve el mensaje en un formato diferente
                        mensaje_respuesta = respuesta_json.get('message', {})
                        respuesta_completa = mensaje_respuesta.get('content', '')
                        
                        if not respuesta_completa:
                            print(f"⚠️ ADVERTENCIA: Respuesta vacía")
                            print(f"   JSON completo: {respuesta_json}")
                            if intento == 0:
                                continue  # Reintentar
                            return None
                        
                        # Debug: Guardar respuesta completa
                        print(f"📝 Longitud de respuesta: {len(respuesta_completa)} caracteres")
                        print(f"📄 Primeros 300 caracteres:\n{respuesta_completa[:300]}\n")
                        
                        return respuesta_completa
                    else:
                        error_detail = response.text if response.text else "Sin detalles"
                        print(f"❌ Error Ollama {response.status_code}")
                        print(f"   Detalles: {error_detail[:500]}")
                        
                        # Si es error 500 y es el primer intento, reintentar
                        if response.status_code == 500 and intento == 0:
                            print(f"🔄 Ollama crasheó, reintentando con configuración reducida...")
                            continue
                        return None
                        
                except requests.exceptions.RequestException as e:
                    if intento == 0:
                        print(f"⚠️ Error en intento {intento + 1}: {e}")
                        continue
                    raise
            
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
                      sin_prompt_sistema: bool = False,
                      tipo_caso: str = None,
                      cloze_transferencia: bool = False) -> List[PreguntaExamen]:
        """Genera examen usando Ollama o GGUF
        sin_prompt_sistema: Si es True, usa el contenido directamente sin agregar instrucciones
        tipo_caso: Para casos de estudio, especifica el tipo (descriptivo, analitico, resolucion, etc.)
        cloze_transferencia: Si es True, genera ejercicios de transferencia conceptual en lugar de cloze tradicional
        """
        
        # Guardar parámetros para uso en métodos internos
        self._cloze_transferencia = cloze_transferencia
        
        # INICIAR LOG DETALLADO
        self._iniciar_log()
        
        if num_preguntas is None:
            num_preguntas = {'multiple': 6, 'verdadero_falso': 4, 'corta': 2}
        
        if ajustes_modelo is None:
            ajustes_modelo = {
                'temperature': 0.7,  # Aumentado para máxima variedad y evitar duplicados
                'max_tokens': 3000,
                'top_p': 0.9,
                'repeat_penalty': 1.15
            }
        
        # Registrar request
        self._agregar_log('request', {
            'num_preguntas': num_preguntas,
            'ajustes_modelo': ajustes_modelo,
            'sin_prompt_sistema': sin_prompt_sistema,
            'tipo_caso': tipo_caso,
            'usar_ollama': self.usar_ollama,
            'modelo': self.modelo_ollama if self.usar_ollama else self.modelo_path_gguf,
            'contenido_length': len(contenido_documento)
        })
        
        if callback_progreso:
            callback_progreso(15, "Preparando prompt...")
        
        # Verificar que contenido_documento es un string
        if not isinstance(contenido_documento, str):
            error_msg = f"contenido_documento no es string, es {type(contenido_documento)}"
            print(f"❌ ERROR: {error_msg}")
            self._agregar_log('errores', error_msg)
            self._guardar_log()
            raise TypeError(f"contenido_documento debe ser string, recibido: {type(contenido_documento)}")
        
        # Crear prompt
        contenido_corto = contenido_documento[:8000]
        
        # Mantener tipos originales para el prompt (case_study necesita su formato especial)
        num_preguntas_prompt = num_preguntas.copy()
        tiene_casos = num_preguntas.get('case_study', 0) > 0 or num_preguntas.get('caso_estudio', 0) > 0
        
        total = sum(num_preguntas.values())
        
        if tiene_casos:
            # CASOS DE ESTUDIO: Usar SIEMPRE el formato estructurado detallado
            # Extraer solo el CONTENIDO real (después de "CONTENIDO:")
            if "CONTENIDO:" in contenido_documento:
                # El prompt del usuario tiene formato "prompt_personalizado\n\nCONTENIDO:\ncontenido_real"
                partes = contenido_documento.split("CONTENIDO:", 1)
                if len(partes) > 1:
                    contenido_corto = partes[1].strip()[:8000]
            
            prompt = self._crear_prompt(contenido_corto, num_preguntas_prompt, total, tipo_caso)
            print(f"🎯 CASOS DE ESTUDIO DETECTADOS: Usando prompt estructurado con tipo '{tipo_caso}'")
            print(f"   Contenido extraído: {len(contenido_corto)} caracteres")
        elif sin_prompt_sistema:
            # Modo prompt personalizado: usar contenido directamente (solo si NO hay casos de estudio)
            prompt = contenido_corto
            print(f"🎯 MODO PROMPT PERSONALIZADO: Usando prompt del usuario directamente")
        else:
            # Modo normal: agregar formato del sistema
            prompt = self._crear_prompt(contenido_corto, num_preguntas_prompt, total, tipo_caso)
        
        # Registrar prompt
        self._agregar_log('prompt_enviado', prompt)
        
        if callback_progreso:
            motor = "Ollama + GPU" if self.usar_ollama else "llama-cpp-python"
            callback_progreso(25, f"Generando con {motor}...")
        
        # NUEVA ESTRATEGIA: GENERAR POR BLOQUES PARA ASEGURAR TIPOS CORRECTOS
        print(f"\n{'='*60}")
        print(f"🎯 GENERACIÓN POR BLOQUES - Total: {total} preguntas")
        print(f"{'='*60}")
        
        todas_preguntas = []
        progreso_base = 25
        progreso_por_tipo = 45 / len([v for v in num_preguntas.values() if v > 0])  # 45% para generación
        
        for tipo, cantidad in num_preguntas.items():
            if cantidad == 0:
                continue
            
            print(f"\n📦 Bloque {len(todas_preguntas) + 1}: Generando {cantidad} preguntas de tipo '{tipo}'")
            
            # Crear prompt específico para este tipo
            prompt_bloque = self._crear_prompt_por_tipo(contenido_corto, tipo, cantidad, tipo_caso)
            
            # Generar este bloque
            if self.usar_ollama:
                respuesta = self._generar_ollama(
                    prompt_bloque, 
                    ajustes_modelo['max_tokens'], 
                    ajustes_modelo['temperature']
                )
            else:
                respuesta = self._generar_gguf(
                    prompt_bloque,
                    ajustes_modelo['max_tokens'],
                    ajustes_modelo['temperature'],
                    ajustes_modelo['top_p'],
                    ajustes_modelo['repeat_penalty']
                )
            
            if not respuesta:
                print(f"⚠️ No se obtuvo respuesta para tipo '{tipo}'")
                continue
            
            # Parsear solo preguntas de este tipo
            preguntas_bloque = self._extraer_preguntas_simple(respuesta, tipo)
            
            # Tomar exactamente la cantidad solicitada
            preguntas_tipo_correcto = [p for p in preguntas_bloque if p.tipo == tipo][:cantidad]
            
            print(f"✅ Bloque completado: {len(preguntas_tipo_correcto)}/{cantidad} preguntas de tipo '{tipo}'")
            todas_preguntas.extend(preguntas_tipo_correcto)
            
            # Actualizar progreso
            if callback_progreso:
                progreso_base += progreso_por_tipo
                callback_progreso(int(progreso_base), f"Generadas {len(todas_preguntas)}/{total}...")
        
        # Registrar todas las respuestas
        self._agregar_log('total_preguntas_generadas', len(todas_preguntas))
        
        if callback_progreso:
            callback_progreso(70, "Procesando respuesta...")
        
        print(f"\n{'='*60}")
        print(f"✅ GENERACIÓN COMPLETADA: {len(todas_preguntas)}/{total} preguntas")
        print(f"{'='*60}")
        
        if callback_progreso:
            callback_progreso(100, f"¡{len(todas_preguntas)} preguntas generadas!")
        
        return todas_preguntas
    
    def _crear_prompt_caso_estudio(self, contenido: str, cantidad: int, tipo_caso: str) -> str:
        """Crea un prompt especializado para casos de estudio según el subtipo seleccionado"""
        
        # Mapeo de tipos de casos de estudio con instrucciones específicas
        tipos_casos = {
            'descriptivo': {
                'nombre': 'Caso Descriptivo',
                'descripcion': 'Describe qué pasó, quién hizo qué y el contexto completo',
                'objetivo': 'Aprender a observar, sintetizar y entender el contexto',
                'instrucciones': '''- Formula un caso que DESCRIBA una situación real extraída del contenido
- Incluye: actores involucrados, contexto temporal, acciones realizadas, resultados obtenidos
- Enfócate en QUÉ pasó, no en por qué o cómo solucionarlo
- El caso debe permitir al estudiante practicar observación y síntesis'''
            },
            'analitico': {
                'nombre': 'Caso Analítico-Diagnóstico',
                'descripcion': 'Explica causas, relaciones y consecuencias (autopsia empresarial)',
                'objetivo': 'Analizar causas raíz y relaciones causa-efecto',
                'instrucciones': '''- Formula un caso que requiera ANALIZAR causas, relaciones y consecuencias
- Incluye: síntomas observables, datos relevantes, múltiples factores interrelacionados
- El estudiante debe identificar causas raíz y explicar cadenas de causalidad
- Requiere pensamiento sistémico y diagnóstico profundo'''
            },
            'resolucion': {
                'nombre': 'Caso de Resolución de Problemas',
                'descripcion': 'Plantea un problema abierto que requiere solución',
                'objetivo': 'Desarrollar habilidades de problem-solving',
                'instrucciones': '''- Formula un caso con un PROBLEMA CLARO que necesita solución
- Incluye: descripción del problema, restricciones, recursos disponibles
- El problema debe ser abierto (múltiples soluciones posibles)
- El estudiante debe proponer Y justificar una solución concreta'''
            },
            'decision': {
                'nombre': 'Caso de Decisión',
                'descripcion': 'Escenario donde se debe elegir entre varias opciones',
                'objetivo': 'Practicar toma de decisiones justificadas',
                'instrucciones': '''- Formula un caso donde se deba TOMAR UNA DECISIÓN entre 2-4 opciones
- Incluye: contexto de decisión, opciones disponibles (con pros/contras), stakeholders afectados
- Ninguna opción es claramente superior - todas tienen trade-offs
- El estudiante debe elegir Y justificar exhaustivamente su decisión'''
            },
            'comparativo': {
                'nombre': 'Caso Comparativo',
                'descripcion': 'Compara dos soluciones, enfoques o metodologías',
                'objetivo': 'Entrenar evaluación crítica comparativa',
                'instrucciones': '''- Formula un caso que compare 2-3 ALTERNATIVAS del contenido
- Incluye: criterios de comparación, ventajas/desventajas de cada opción, contexto de aplicación
- El estudiante debe evaluar críticamente cada alternativa
- Debe recomendar cuál usar y en qué circunstancias'''
            },
            'predictivo': {
                'nombre': 'Caso Predictivo',
                'descripcion': 'Proyecta el futuro basándose en datos actuales',
                'objetivo': 'Desarrollar capacidad de pronóstico fundamentado',
                'instrucciones': '''- Formula un caso con DATOS ACTUALES donde se deba predecir el futuro
- Incluye: tendencias observadas, métricas actuales, factores externos relevantes
- El estudiante debe hacer predicciones específicas (no vagas)
- Debe justificar el pronóstico con evidencia y razonamiento lógico'''
            },
            'simulacion': {
                'nombre': 'Caso de Simulación',
                'descripcion': 'Sistema con variables dinámicas que requiere decisiones',
                'objetivo': 'Practicar decisiones en sistemas complejos',
                'instrucciones': '''- Formula un caso que simule un SISTEMA CON VARIABLES DINÁMICAS
- Incluye: estado inicial, variables que interactúan, reglas del sistema
- El estudiante debe tomar decisiones secuenciales
- Debe predecir cómo sus decisiones afectan las variables del sistema'''
            },
            'inverso': {
                'nombre': 'Caso Inverso (Reverse)',
                'descripcion': 'Se da el resultado final, se debe reconstruir el proceso',
                'objetivo': 'Desarrollar pensamiento deductivo e ingeniaría inversa',
                'instrucciones': '''- Formula un caso mostrando el RESULTADO FINAL ya logrado
- Incluye: descripción detallada del outcome, pistas sobre el proceso
- OCULTA los pasos intermedios
- El estudiante debe reconstruir lógicamente QUÉ PASOS se siguieron para llegar a ese resultado'''
            },
            'fallo': {
                'nombre': 'Caso de Fallo o Desastre',
                'descripcion': 'Estudia algo que salió mal (aprender de errores ajenos)',
                'objetivo': 'Aprender de fracasos y prevenir errores',
                'instrucciones': '''- Formula un caso sobre algo que SALIÓ MAL basándote en el contenido
- Incluye: qué se intentó lograr, qué falló específicamente, consecuencias
- Menciona señales de alerta que se ignoraron
- El estudiante debe analizar causas del fallo y proponer cómo evitarlo'''
            },
            'creativo': {
                'nombre': 'Caso Creativo/Innovación',
                'descripcion': 'No hay respuesta correcta, se evalúa creatividad',
                'objetivo': 'Fomentar ideación y pensamiento original',
                'instrucciones': '''- Formula un caso ABIERTO que requiera INNOVACIÓN
- Incluye: desafío o oportunidad, restricciones del contexto
- NO hay una respuesta "correcta" predefinida
- Se evalúa originalidad, viabilidad de ideas y creatividad de la propuesta'''
            },
            'etico': {
                'nombre': 'Caso Ético',
                'descripcion': 'Dilema donde el negocio choca con la moral',
                'objetivo': 'Desarrollar razonamiento ético y responsabilidad',
                'instrucciones': '''- Formula un caso con un DILEMA ÉTICO basado en el contenido
- Incluye: conflicto entre beneficio/deber, stakeholders con intereses contrapuestos
- No hay solución fácil - hay tensión entre opciones
- El estudiante debe razonar éticamente y defender su postura moral'''
            },
            'tecnico': {
                'nombre': 'Caso Técnico-Operativo',
                'descripcion': 'Explica un sistema/proceso y reta a optimizarlo',
                'objetivo': 'Mejorar habilidades técnicas y optimización',
                'instrucciones': '''- Formula un caso explicando un SISTEMA O PROCESO TÉCNICO del contenido
- Incluye: descripción del funcionamiento actual, métricas de desempeño
- Identifica ineficiencias o áreas de mejora
- El estudiante debe proponer optimizaciones técnicas concretas y justificarlas'''
            }
        }
        
        # Si no se especifica tipo o es inválido, usar descriptivo por defecto
        if not tipo_caso or tipo_caso not in tipos_casos:
            tipo_caso = 'descriptivo'
        
        info_tipo = tipos_casos[tipo_caso]
        
        prompt = f"""Eres un experto en crear casos de estudio educativos. Tu tarea es generar EXACTAMENTE {cantidad} caso(s) de estudio de tipo "{info_tipo['nombre']}" basándote en el contenido proporcionado.

CONTENIDO BASE PARA EL CASO:
{contenido}

🎯 TIPO DE CASO REQUERIDO: {info_tipo['nombre'].upper()}
📋 DESCRIPCIÓN: {info_tipo['descripcion']}
🎓 OBJETIVO PEDAGÓGICO: {info_tipo['objetivo']}

⚠️ INSTRUCCIONES ESPECÍFICAS PARA ESTE TIPO:
{info_tipo['instrucciones']}

⚠️ REGLAS CRÍTICAS:
1. DEBES formular el caso DE ESTUDIO COMPLETO basándote en la información del contenido
2. El caso debe ser REALISTA y coherente con el contenido proporcionado
3. Genera EXACTAMENTE {cantidad} caso(s) de tipo "{tipo_caso}"
4. NO generes otros tipos de casos
5. El caso debe estar COMPLETO con todos los campos requeridos
6. NO uses placeholders como "...", "[...]", "[Nombre de empresa]"
7. Usa información ESPECÍFICA del contenido proporcionado
8. El caso debe ser autocontenido (incluye todo el contexto necesario)

FORMATO JSON REQUERIDO:
{{
  "preguntas": [
    {{
      "tipo": "case_study",
      "subtipo": "{tipo_caso}",
      "titulo": "Título descriptivo del caso (máx 15 palabras)",
      "contexto": "CONTEXTO DETALLADO (mínimo 100 palabras): Describe el escenario completo, actores involucrados, situación inicial, antecedentes relevantes. Usa información ESPECÍFICA del contenido.",
      "descripcion": "DESCRIPCIÓN EXHAUSTIVA (mínimo 150 palabras): Desarrolla el caso en profundidad según el tipo '{tipo_caso}'. Incluye datos concretos, situaciones específicas, detalles relevantes extraídos del contenido.",
      "pregunta": "Pregunta principal que guía el análisis del caso (relacionada con el tipo '{tipo_caso}')",
      "datos_clave": ["Dato relevante 1 del contenido", "Dato relevante 2 del contenido", "Dato relevante 3 del contenido", "Dato relevante 4 del contenido"],
      "respuesta_esperada": "Respuesta modelo DETALLADA (mínimo 150 palabras) que muestre cómo analizar/resolver este tipo de caso. Debe demostrar el tipo de razonamiento requerido para '{tipo_caso}'.",
      "puntos": 10
    }}
  ]
}}

IMPORTANTE: El caso debe formularse USANDO LA INFORMACIÓN DEL CONTENIDO PROPORCIONADO, no inventes escenarios genéricos. Extrae situaciones, conceptos, ejemplos o problemas del texto y desarróllalos como un caso de estudio del tipo "{tipo_caso}".

Responde SOLO con JSON válido, sin código markdown ni explicaciones adicionales."""

        return prompt
    
    def _crear_prompt_por_tipo(self, contenido: str, tipo: str, cantidad: int, tipo_caso: str = None) -> str:
        """Crea un prompt específico para generar preguntas de UN SOLO TIPO
        Esto asegura que el modelo genere exactamente el tipo solicitado
        """
        
        # CASOS DE ESTUDIO: Requieren prompt especial basado en el subtipo
        if tipo == 'case_study':
            return self._crear_prompt_caso_estudio(contenido, cantidad, tipo_caso)
        
        # Mapeo de nombres de tipos a descripciones
        tipo_info = {
            'mcq': {
                'nombre': 'opción múltiple',
                'puntos': 3,
                'ejemplo': '''{
      "tipo": "mcq",
      "pregunta": "¿Pregunta clara y específica sobre el contenido?",
      "opciones": ["A) Primera opción", "B) Segunda opción", "C) Tercera opción", "D) Cuarta opción"],
      "respuesta_correcta": "A",
      "puntos": 3
    }''',
                'instrucciones': '- Debe tener EXACTAMENTE 4 opciones (A, B, C, D)\n- Una sola respuesta correcta\n- Las opciones incorrectas deben ser plausibles'
            },
            'true_false': {
                'nombre': 'verdadero/falso',
                'puntos': 2,
                'ejemplo': '''{
      "tipo": "true_false",
      "pregunta": "Afirmación clara basada en el contenido",
      "respuesta_correcta": "verdadero",
      "puntos": 2
    }''',
                'instrucciones': '- La afirmación debe ser clara y específica\n- respuesta_correcta debe ser "verdadero" o "falso"\n- Basada en información del contenido'
            },
            'short_answer': {
                'nombre': 'respuesta corta',
                'puntos': 3,
                'ejemplo': '''{
      "tipo": "short_answer",
      "pregunta": "Pregunta que requiere una respuesta breve y concreta",
      "respuesta_correcta": "Respuesta esperada (2-3 oraciones)",
      "puntos": 3
    }''',
                'instrucciones': '- Respuesta de 2-3 oraciones\n- Clara y concreta\n- Basada en el contenido'
            },
            'cloze': {
                'nombre': 'relleno de huecos (cloze test)',
                'puntos': 3,
                'ejemplo': '''{
      "tipo": "cloze",
      "pregunta": "Python es un lenguaje de {} creado por {} en {}",
      "metadata": {
        "text_with_gaps": "Python es un lenguaje de {} creado por {} en {}",
        "answers": ["programación", "Guido van Rossum", "1991"],
        "hint": "Piensa en el tipo de lenguaje y su creador"
      },
      "respuesta_correcta": "programación, Guido van Rossum, 1991",
      "puntos": 3
    }''',
                'instrucciones': '- El texto debe tener 2-5 huecos marcados con {}\n- Cada hueco representa UNA palabra o frase corta clave\n- metadata.answers debe tener el MISMO número de elementos que huecos\n- Las respuestas deben estar en el MISMO ORDEN que aparecen los huecos\n- Incluye una pista (hint) útil que ayude sin revelar la respuesta\n- El texto debe ser educativo y basado en el contenido'
            },
            'open_question': {
                'nombre': 'desarrollo/ensayo',
                'puntos': 5,
                'ejemplo': '''{
      "tipo": "open_question",
      "pregunta": "Analiza en profundidad el diseño centrado en el usuario. Explica sus principios fundamentales, beneficios principales y cómo se aplica en proyectos reales. Desarrolla tu respuesta con ejemplos concretos.",
      "metadata": {
        "key_points": [
          "Definición de diseño centrado en usuario",
          "Principios fundamentales (enfoque en usuarios, medición empírica, diseño iterativo)",
          "Beneficios para usuarios y negocio",
          "Metodologías y técnicas aplicadas",
          "Ejemplos concretos de implementación"
        ],
        "expected_length": "150-300 palabras",
        "evaluation_criteria": [
          "Claridad conceptual y profundidad de análisis",
          "Conexión entre teoría y práctica",
          "Uso de ejemplos relevantes",
          "Estructura y coherencia argumentativa"
        ]
      },
      "respuesta_correcta": "El diseño centrado en el usuario (UCD) es una filosofía de diseño que sitúa al usuario final en el centro del proceso de desarrollo. Sus principios fundamentales incluyen: 1) Enfoque temprano en usuarios y tareas, comprendiendo quiénes son, qué necesitan y en qué contexto operan. 2) Medición empírica mediante observación del comportamiento real con prototipos. 3) Diseño iterativo con ciclos de diseño-prueba-refinamiento. Los beneficios son significativos: mayor satisfacción del usuario, reducción de costos al detectar problemas temprano, productos más intuitivos y mejor adopción. Las metodologías comunes incluyen investigación de usuarios, creación de personas, pruebas de usabilidad y diseño participativo. Por ejemplo, al desarrollar una aplicación bancaria, el UCD implica observar cómo usuarios reales interactúan con prototipos, identificar fricciones en el flujo de pagos, y refinar iterativamente hasta lograr una experiencia fluida.",
      "puntos": 5
    }''',
                'instrucciones': '- Pregunta compleja que requiere análisis profundo y estructurado\n- Debe solicitar explícitamente: explicación de conceptos, análisis de relaciones, ejemplos concretos\n- metadata.key_points: Array con 4-6 aspectos específicos que debe cubrir la respuesta\n- metadata.expected_length: Extensión esperada de la respuesta\n- metadata.evaluation_criteria: Criterios de evaluación claros\n- Respuesta modelo de 150-300 palabras con estructura clara\n- Debe incluir definiciones, análisis y ejemplos prácticos'
            },
            'flashcard': {
                'nombre': 'flashcard',
                'puntos': 1,
                'ejemplo': '''{
      "tipo": "flashcard",
      "pregunta": "Concepto o término clave",
      "respuesta_correcta": "Definición o explicación",
      "puntos": 1
    }''',
                'instrucciones': '- Pregunta directa sobre un concepto\n- Respuesta concisa y precisa'
            }
        }
        
        info = tipo_info.get(tipo, tipo_info['mcq'])
        
        # 🧠 MODO TRANSFERENCIA CONCEPTUAL PARA CLOZE
        if tipo == 'cloze' and getattr(self, '_cloze_transferencia', False):
            print("🧠 Usando modo TRANSFERENCIA CONCEPTUAL para Cloze")
            
            # PROMPT ESPECIAL PARA TRANSFERENCIA CONCEPTUAL
            prompt_transferencia = f"""TAREA: Crear ejercicios de APLICACIÓN PRÁCTICA de conocimiento

═══════════════════════════════════════════════════════════════
PASO 1 - ANÁLISIS PROFUNDO DEL CONTENIDO
═══════════════════════════════════════════════════════════════

Lee este texto y ANTES de generar nada, identifica:

CONTENIDO:
{contenido}

PREGUNTAS DE ANÁLISIS (responde mentalmente):
1. ¿Es un tema de GRAMÁTICA (uso correcto de palabras)?
2. ¿Es un tema de VOCABULARIO (significado de términos)?
3. ¿Es un CONCEPTO TEÓRICO (idea abstracta)?
4. ¿Es una HABILIDAD PRÁCTICA (cómo hacer algo)?
5. ¿Cuál es el OBJETIVO DE APRENDIZAJE? (¿qué debe saber HACER el estudiante?)

═══════════════════════════════════════════════════════════════
PASO 2 - GENERA {cantidad} EJERCICIOS SEGÚN EL TIPO DE CONTENIDO
═══════════════════════════════════════════════════════════════

🎯 SI EL TEMA ES GRAMÁTICA (como "uso de porqué/porque/por qué/por que"):
- El estudiante debe USAR CORRECTAMENTE la forma gramatical en contexto
- Los huecos deben ser la FORMA CORRECTA + su justificación
- Ejemplo: "Le pregunté {{}} había llegado tarde, y me respondió que {{}} se quedó dormido."
  answers: ["por qué", "porque"]
  (El estudiante practica CUÁNDO usar cada forma)

🎯 SI EL TEMA ES UN CONCEPTO (como "causalidad" o "toma de decisiones"):  
- El estudiante debe APLICAR el concepto en una situación real
- Los huecos son EXPLICACIONES que demuestran comprensión
- Ejemplo: "La causa de mi decisión fue {{}} y la consecuencia fue {{}}."
  answers: ["que necesitaba más tiempo para reflexionar", "que perdí la oportunidad"]

🎯 SI EL TEMA ES VOCABULARIO:
- El estudiante usa las palabras en CONTEXTO apropiado
- Los huecos muestran USO CORRECTO del término

═══════════════════════════════════════════════════════════════
EJEMPLOS SEGÚN TIPO DE CONTENIDO
═══════════════════════════════════════════════════════════════

EJEMPLO A - Si el contenido es sobre "porqué/porque/por qué":
{{
  "tipo": "cloze",
  "pregunta": "Cuando el profesor preguntó {{}} no había hecho la tarea, Juan respondió {{}} había estado enfermo.",
  "metadata": {{
    "text_with_gaps": "Cuando el profesor preguntó {{}} no había hecho la tarea, Juan respondió {{}} había estado enfermo.",
    "answers": ["por qué", "porque"],
    "hint": "¿Cuál forma se usa para PREGUNTAR y cuál para RESPONDER/explicar?"
  }},
  "respuesta_correcta": "por qué, porque",
  "puntos": 2
}}

EJEMPLO B - Si el contenido es sobre "el porqué" (sustantivo):
{{
  "tipo": "cloze",
  "pregunta": "María quería entender {{}} de la decisión de su jefe, así que le preguntó {{}} había tomado esa medida tan drástica.",
  "metadata": {{
    "text_with_gaps": "María quería entender {{}} de la decisión de su jefe, así que le preguntó {{}} había tomado esa medida tan drástica.",
    "answers": ["el porqué", "por qué"],
    "hint": "'El porqué' es sustantivo (la razón), 'por qué' es para preguntar"
  }},
  "respuesta_correcta": "el porqué, por qué",
  "puntos": 2
}}

EJEMPLO C - Si el contenido es sobre razonamiento/causalidad:
{{
  "tipo": "cloze",
  "pregunta": "El porqué de mi renuncia fue {{}}; tomé esa decisión porque {{}}.",
  "metadata": {{
    "text_with_gaps": "El porqué de mi renuncia fue {{}}; tomé esa decisión porque {{}}.",
    "answers": ["la falta de oportunidades de crecimiento en la empresa", "valoraba más mi desarrollo profesional que la estabilidad"],
    "hint": "Primero da LA RAZÓN (el porqué), luego EXPLICA (porque)"
  }},
  "respuesta_correcta": "la falta de oportunidades de crecimiento en la empresa, valoraba más mi desarrollo profesional que la estabilidad",
  "puntos": 2
}}

═══════════════════════════════════════════════════════════════
REGLAS CRÍTICAS
═══════════════════════════════════════════════════════════════

1. ANALIZA el contenido para saber QUÉ debe practicar el estudiante
2. Los ejercicios deben EVALUAR la habilidad del texto, no inventar historias
3. Si es gramática: los huecos son las FORMAS CORRECTAS
4. Si es concepto: los huecos son APLICACIONES del concepto
5. Usa {{}} para huecos (NO {{{{}}}})
6. 2-3 huecos por ejercicio
7. El hint debe AYUDAR a elegir la respuesta correcta

Genera EXACTAMENTE {cantidad} ejercicios en formato JSON array:
[
  {{ "tipo": "cloze", "pregunta": "...", "metadata": {{...}}, "respuesta_correcta": "...", "puntos": 2 }},
  ...
]

Responde SOLO con el JSON válido, sin explicaciones."""

            return prompt_transferencia
        
        prompt = f"""Eres un experto en crear exámenes educativos. Tu tarea es generar EXACTAMENTE {cantidad} preguntas de tipo "{tipo}" ({info['nombre']}) basadas en el contenido proporcionado.

CONTENIDO A EVALUAR:
{contenido}

🎯 TIPO DE PREGUNTA REQUERIDO: {info['nombre'].upper()}
📊 CANTIDAD EXACTA: {cantidad} preguntas

⚠️ INSTRUCCIONES ESPECÍFICAS PARA ESTE TIPO:
{info['instrucciones']}

⚠️ REGLAS CRÍTICAS:
1. Genera EXACTAMENTE {cantidad} preguntas de tipo "{tipo}"
2. NO generes otros tipos de preguntas
3. Todas las preguntas deben estar COMPLETAS
4. NO uses placeholders como "...", "[...]"
5. Basa todas las preguntas en el contenido proporcionado
6. Cada pregunta debe ser AUTOCONTENIDA (incluye contexto necesario)
7. NO inventes información que no esté en el texto
8. 🔥 OBLIGATORIO: Cada pregunta DEBE incluir el campo "tipo": "{tipo}"

FORMATO JSON (genera un array con {cantidad} preguntas):
[
  {info['ejemplo']},
  ... ({cantidad} preguntas en total, TODAS con "tipo": "{tipo}")
]

⚠️ IMPORTANTE: Responde con un ARRAY DIRECTO de preguntas, no con un objeto envolvente.
Ejemplo correcto: [{{...}}, {{...}}]
Ejemplo INCORRECTO: {{"preguntas": [...]}}

Responde SOLO con JSON válido, sin código markdown ni explicaciones adicionales."""

        return prompt
    
    def _crear_prompt(self, contenido: str, num_preguntas: Dict[str, int], total: int, tipo_caso: str = None) -> str:
        """Crea el prompt optimizado
        tipo_caso: Para casos de estudio, especifica el tipo (descriptivo, analitico, resolucion, etc.)
        """
        # Construir lista detallada de tipos de preguntas (USANDO NOMBRES NORMALIZADOS)
        tipos_detalle = []
        if num_preguntas.get('mcq', 0) > 0:
            tipos_detalle.append(f"{num_preguntas['mcq']} de opción múltiple (4 opciones A/B/C/D, puntos: 3)")
        if num_preguntas.get('true_false', 0) > 0:
            tipos_detalle.append(f"{num_preguntas['true_false']} verdadero/falso (puntos: 2)")
        if num_preguntas.get('short_answer', 0) > 0:
            tipos_detalle.append(f"{num_preguntas['short_answer']} de respuesta corta (puntos: 3)")
        if num_preguntas.get('cloze', 0) > 0:
            tipos_detalle.append(f"{num_preguntas['cloze']} de relleno de huecos/cloze (texto con {{}}, puntos: 3)")
        if num_preguntas.get('open_question', 0) > 0:
            tipos_detalle.append(f"**🔥 {num_preguntas['open_question']} de desarrollo/ensayo EXTENSO** (puntos: 5) - OBLIGATORIO: pregunta compleja que requiere ANÁLISIS PROFUNDO")
        
        # Soporte para case_study
        num_casos = num_preguntas.get('case_study', 0)
        if num_casos > 0:
            tipo_desc = f" ({tipo_caso})" if tipo_caso else ""
            tipos_detalle.append(f"{num_casos} caso(s) de estudio{tipo_desc} (puntos: 10)")
        
        tipos_str = "\n".join([f"{i+1}. {t}" for i, t in enumerate(tipos_detalle)])
        
        # Determinar si hay casos de estudio y obtener el prompt específico
        caso_estudio_prompt = ""
        if num_casos > 0 and tipo_caso:
            caso_estudio_prompt = self._obtener_prompt_caso_estudio(tipo_caso)
        
        # Formato JSON base (USANDO NOMBRES NORMALIZADOS)
        json_ejemplos = []
        
        # Agregar ejemplos según tipos solicitados
        if num_preguntas.get('mcq', 0) > 0:
            json_ejemplos.append("""    {
      "tipo": "mcq",
      "pregunta": "¿Pregunta clara y específica sobre el contenido?",
      "opciones": ["A) Primera opción", "B) Segunda opción", "C) Tercera opción", "D) Cuarta opción"],
      "respuesta_correcta": "A",
      "puntos": 3
    }""")
        
        if num_preguntas.get('true_false', 0) > 0:
            json_ejemplos.append("""    {
      "tipo": "true_false",
      "pregunta": "Afirmación clara basada en el contenido",
      "respuesta_correcta": "verdadero",
      "puntos": 2
    }""")
        
        if num_preguntas.get('short_answer', 0) > 0:
            json_ejemplos.append("""    {
      "tipo": "short_answer",
      "pregunta": "Pregunta que requiere una respuesta breve y concreta",
      "respuesta_correcta": "Respuesta esperada (2-3 oraciones)",
      "puntos": 3
    }""")
        
        if num_preguntas.get('cloze', 0) > 0:
            json_ejemplos.append("""    {
      "tipo": "cloze",
      "pregunta": "Python es un lenguaje de {} creado por {} en {}",
      "metadata": {
        "text_with_gaps": "Python es un lenguaje de {} creado por {} en {}",
        "answers": ["programación", "Guido van Rossum", "1991"],
        "hint": "Piensa en el tipo de lenguaje y su creador"
      },
      "respuesta_correcta": "programación, Guido van Rossum, 1991",
      "puntos": 3
    }""")
        
        if num_preguntas.get('open_question', 0) > 0:
            json_ejemplos.append("""    {
      "tipo": "open_question",
      "pregunta": "Analiza en profundidad [tema complejo del contenido]. Explica los conceptos principales, sus interrelaciones, beneficios/impactos y aplicaciones prácticas. Desarrolla tu respuesta con ejemplos concretos del contenido.",
      "metadata": {
        "key_points": [
          "Definición y contexto del tema principal",
          "Conceptos o principios fundamentales (mínimo 3)",
          "Relaciones e interconexiones entre conceptos",
          "Beneficios, ventajas o impactos significativos",
          "Aplicaciones prácticas o ejemplos reales",
          "Implicaciones o importancia en el campo"
        ],
        "expected_length": "200-300 palabras",
        "evaluation_criteria": [
          "Profundidad de análisis conceptual",
          "Claridad en explicaciones",
          "Conexión entre teoría y ejemplos",
          "Estructura lógica y coherencia"
        ]
      },
      "respuesta_correcta": "Respuesta modelo DETALLADA de 200-300 palabras que desarrolle sistemáticamente: 1) Definiciones completas de conceptos clave con contexto del contenido, 2) Análisis de cómo se relacionan e interconectan estos conceptos (mínimo 3 relaciones explicadas), 3) Explicación de beneficios o impactos significativos con datos/evidencia del texto, 4) Ejemplos concretos y específicos extraídos del contenido, 5) Aplicaciones prácticas en contextos reales, 6) Reflexión sobre importancia o implicaciones. La respuesta debe demostrar comprensión profunda, no superficial.",
      "puntos": 5
    }""")
        
        # Soporte para case_study
        if num_casos > 0:
            json_ejemplos.append(caso_estudio_prompt)
        
        json_ejemplos_str = ",\n".join(json_ejemplos)
        
        return f"""Eres un experto en crear exámenes educativos. Tu tarea es generar EXACTAMENTE {total} preguntas REALES basadas en el contenido proporcionado.

CONTENIDO A EVALUAR:
{contenido}

🔥 DISTRIBUCIÓN OBLIGATORIA - GENERA {total} PREGUNTAS ASI:
{tipos_str}

⚠️ ATENCIÓN ESPECIAL: Si la distribución incluye "open_question", "caso de estudio" o "desarrollo", DEBES generarla. Son los tipos más importantes.

⚠️ REGLAS CRÍTICAS - LEE CON ATENCIÓN:
1. Genera EXACTAMENTE {total} preguntas COMPLETAS con contenido REAL
2. RESPETA LA DISTRIBUCIÓN DE TIPOS especificada arriba - CADA TIPO ES OBLIGATORIO
3. Los tipos válidos son: "mcq", "true_false", "short_answer", "open_question", "case_study"
4. Para "case_study": DEBES incluir TODOS los campos del formato especificado arriba (contexto, descripcion, etc.)
5. NO uses placeholders como "...", "[...]", "puntos: ..."
6. NO REPITAS preguntas - cada una debe ser ÚNICA con texto diferente
7. ⚠️ IMPORTANTE: Cada pregunta debe ser AUTOCONTENIDA - incluye el contexto necesario en el texto de la pregunta
   - En lugar de: "¿Cómo utiliza el diseño gráfico esta ley?" → "¿Cómo utiliza el diseño gráfico la Ley de Continuidad de Gestalt?"
   - En lugar de: "¿Qué significa esto?" → "¿Qué significa el término 'diseño basado en valores'?"
   - La pregunta debe entenderse SIN necesidad de ver el contenido original
8. CADA pregunta debe estar COMPLETAMENTE llena con:
   - "tipo": uno de estos valores exactos: "mcq", "true_false", "short_answer", "open_question", "case_study"
   - "pregunta": texto completo y autocontenido de la pregunta (mínimo 10 palabras, con contexto incluido)
   - Para "mcq": "opciones" debe ser un array de 4 strings completos (ej: ["A) opción real 1", "B) opción real 2", "C) opción real 3", "D) opción real 4"])
   - "respuesta_correcta": la respuesta correcta REAL (para MCQ: letra A/B/C/D, para otros: texto completo)
   - "puntos": número entero (3 para mcq, 2 para true_false, 3 para short_answer, 5 para open_question, 10 para case_study)
9. Todas las preguntas deben basarse en información del contenido proporcionado
10. NO inventes información que no esté en el texto
11. Responde SOLO con JSON válido, sin código markdown, sin explicaciones adicionales

FORMATO JSON VÁLIDO (con datos REALES, NO placeholders):
{{
  "preguntas": [
    {{
      "tipo": "mcq",
      "pregunta": "¿Según el contenido, cuál es la diferencia principal entre arte y diseño?",
      "opciones": ["A) El arte es un sustantivo y el diseño es un verbo", "B) No hay diferencia", "C) El arte es comercial", "D) El diseño no comunica"],
      "respuesta_correcta": "A",
      "puntos": 3
    }},
    {{
      "tipo": "short_answer",
      "pregunta": "Explica brevemente qué significa HCI según la clase",
      "respuesta_correcta": "HCI significa Human-Computer Interaction (Interacción Humano-Computadora), que estudia cómo las personas interactúan con la tecnología",
      "puntos": 3
    }}
  ]
}}

🔥 RECORDATORIO FINAL: Si la distribución arriba especifica "open_question", debes incluirla obligatoriamente en tu respuesta JSON.

AHORA GENERA LAS {total} PREGUNTAS COMPLETAS CON DATOS REALES (recuerda incluir TODOS los tipos solicitados):"""
    
    def _obtener_prompt_caso_estudio(self, tipo_caso: str) -> str:
        """Retorna el formato JSON específico para cada tipo de caso de estudio
        
        IMPORTANTE: Los casos de estudio requieren MUCHO MÁS DETALLE que otros tipos de preguntas.
        - El contexto debe tener al menos 3-5 oraciones (100-200 palabras)
        - La descripción debe tener al menos 4-6 oraciones (150-300 palabras)
        - Todos los arrays deben tener 4-6 elementos detallados
        """
    
    def _filtrar_preguntas(self, preguntas: List[PreguntaExamen], num_preguntas: Dict[str, int]) -> List[PreguntaExamen]:
        """Filtra preguntas por tipo y cantidad solicitada
        
        ESTRATEGIA DE FILTRADO:
        1. Prioriza cumplir con las cantidades exactas por tipo
        2. Si faltan algunos tipos, incluye extras de otros tipos hasta alcanzar el total solicitado
        """
        preguntas_filtradas = []
        contador_por_tipo = {}
        preguntas_sobrantes = []
        
        # Mapeo de tipos nuevos a tipos del sistema
        mapeo_tipos = {
            'flashcard': 'flashcard',
            'mcq': 'mcq', 
            'true_false': 'true_false',
            'verdadero_falso': 'true_false',
            'verdadero-falso': 'true_false',
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
        
        # FASE 1: Seleccionar preguntas según cantidades solicitadas por tipo
        for pregunta in preguntas:
            # DEBUG: Imprimir tipo exacto de la pregunta
            print(f"  🔍 Pregunta tipo='{pregunta.tipo}' (repr: {repr(pregunta.tipo)})")
            tipo_normalizado = mapeo_tipos.get(pregunta.tipo, pregunta.tipo)
            print(f"     → Normalizado a: '{tipo_normalizado}'")
            
            # 🔥 LÓGICA ESPECIAL: Si generamos open_question pero se solicitó case_study, aceptarla
            # Esto maneja el caso donde el modelo no genera el formato completo de case_study
            if tipo_normalizado == 'open_question' and num_preguntas.get('case_study', 0) > 0:
                # Si hay case_study solicitados y no se han cumplido, usar esta open_question
                if contador_por_tipo.get('case_study', 0) < num_preguntas.get('case_study', 0):
                    tipo_normalizado = 'case_study'
                    print(f"     → 🔄 Reasignado a case_study (case_study solicitados no cumplidos)")
            
            cantidad_solicitada = num_preguntas.get(tipo_normalizado, 0)
            print(f"     → Cantidad solicitada de '{tipo_normalizado}': {cantidad_solicitada}")
            
            if cantidad_solicitada > 0:
                if tipo_normalizado not in contador_por_tipo:
                    contador_por_tipo[tipo_normalizado] = 0
                
                if contador_por_tipo[tipo_normalizado] < cantidad_solicitada:
                    preguntas_filtradas.append(pregunta)
                    contador_por_tipo[tipo_normalizado] += 1
                else:
                    # Guardar extras para usar si faltan otros tipos
                    preguntas_sobrantes.append(pregunta)
        
        # Calcular total esperado
        total_esperado = sum(num_preguntas.values())
        total_actual = len(preguntas_filtradas)
        
        # FASE 2: Si faltan preguntas, agregar extras hasta completar el total
        if total_actual < total_esperado and preguntas_sobrantes:
            faltantes = total_esperado - total_actual
            print(f"⚠️ Faltan {faltantes} preguntas. Agregando extras de otros tipos...")
            
            for i, pregunta_extra in enumerate(preguntas_sobrantes):
                if len(preguntas_filtradas) >= total_esperado:
                    break
                preguntas_filtradas.append(pregunta_extra)
                tipo_norm = mapeo_tipos.get(pregunta_extra.tipo, pregunta_extra.tipo)
                contador_por_tipo[tipo_norm] = contador_por_tipo.get(tipo_norm, 0) + 1
                print(f"   ➕ Agregada pregunta extra #{i+1} (tipo: {tipo_norm})")
        
        print(f"🔍 Filtrado: {len(preguntas)} generadas → {len(preguntas_filtradas)} retornadas (esperadas: {total_esperado})")
        print(f"   Solicitadas: {num_preguntas}")
        print(f"   Filtradas por tipo: {contador_por_tipo}")
        
        # Registrar filtrado
        self._agregar_log('filtrado', {
            'total_generadas': len(preguntas),
            'total_filtradas': len(preguntas_filtradas),
            'total_esperado': total_esperado,
            'solicitadas': num_preguntas,
            'contador_por_tipo': contador_por_tipo
        })
        
        # Verificar si faltaron preguntas
        tipos_faltantes = []
        for tipo, cantidad in num_preguntas.items():
            generadas = contador_por_tipo.get(tipo, 0)
            if generadas < cantidad:
                tipos_faltantes.append(f"{tipo}: {generadas}/{cantidad}")
        
        if tipos_faltantes:
            warning_msg = f"El modelo no generó suficientes preguntas: {', '.join(tipos_faltantes)}"
            self._agregar_log('errores', warning_msg)
            print(f"⚠️ ADVERTENCIA: El modelo no generó suficientes preguntas de algunos tipos:")
            for faltante in tipos_faltantes:
                tipo_falt = faltante.split(':')[0].strip()
                print(f"   - {faltante}")
            
            if len(preguntas_filtradas) < total_esperado:
                print(f"   Esto puede ocurrir porque:")
                print(f"   1. El modelo generó tipos diferentes a los solicitados")
                print(f"   2. El modelo ignoró las instrucciones del prompt")
                print(f"   3. El contenido es muy corto para generar más preguntas")
                print(f"   💡 Intenta regenerar la práctica")
            else:
                print(f"   ✅ Se compensó con extras: {len(preguntas_filtradas)}/{total_esperado} preguntas retornadas")
        
        return preguntas_filtradas
    
    def _obtener_prompt_caso_estudio(self, tipo_caso: str) -> str:
        """Retorna el formato JSON específico para cada tipo de caso de estudio
        
        IMPORTANTE: Los casos de estudio requieren MUCHO MÁS DETALLE que otros tipos de preguntas.
        - El contexto debe tener al menos 3-5 oraciones (100-200 palabras)
        - La descripción debe tener al menos 4-6 oraciones (150-300 palabras)
        - Todos los arrays deben tener 4-6 elementos detallados
        """
        
        formatos_casos = {
            "descriptivo": """    {
      "tipo": "case_study",
      "subtipo": "descriptivo",
      "titulo": "Título descriptivo del caso (máx 10 palabras)",
      "contexto": "CONTEXTO DETALLADO (mínimo 100 palabras): Situación completa del caso con fecha, lugar, personas involucradas, empresa/organización, industria, antecedentes históricos y estado inicial. Describe el escenario completo para que el estudiante entienda el panorama general.",
      "descripcion": "DESCRIPCIÓN EXHAUSTIVA (mínimo 150 palabras): Descripción muy detallada de todos los eventos cronológicamente, personas clave con sus roles, decisiones tomadas con justificaciones, acciones realizadas, resultados obtenidos, reacciones de stakeholders, métricas relevantes, cambios observados. Incluye datos específicos, números, porcentajes cuando sea posible.",
      "pregunta": "Pregunta específica que requiere identificar y analizar los elementos clave que caracterizaron esta situación",
      "puntos_clave": ["Punto clave 1 con detalles específicos", "Punto clave 2 con contexto", "Punto clave 3 con implicaciones", "Punto clave 4 con evidencia", "Punto clave 5 para análisis profundo"],
      "respuesta_esperada": "Análisis descriptivo esperado (mínimo 100 palabras) de los elementos principales del caso con observaciones, síntesis y entendimiento del contexto",
      "puntos": 10
    }""",
            
            "analitico": """    {
      "tipo": "case_study",
      "subtipo": "analitico",
      "titulo": "Título del caso analítico (máx 10 palabras)",
      "contexto": "CONTEXTO DETALLADO (mínimo 100 palabras): Situación empresarial, técnica o de negocio completa con antecedentes, estado actual, métricas relevantes, actores involucrados, mercado, competencia, recursos disponibles. Proporciona todos los elementos necesarios para un análisis profundo.",
      "descripcion": "DESCRIPCIÓN EXHAUSTIVA (mínimo 150 palabras): Descripción completa de la problemática incluyendo datos cuantitativos y cualitativos, tendencias observadas, señales de alerta, información histórica, comparativas con períodos anteriores, feedback de usuarios/clientes, métricas de rendimiento, puntos de fricción identificados. Sé muy específico con números y fechas.",
      "pregunta": "Analiza en profundidad las causas raíz, las relaciones causales entre factores y las consecuencias directas e indirectas de esta situación",
      "areas_analisis": ["Causas principales con evidencia específica", "Relaciones causales entre factores A y B", "Consecuencias inmediatas observadas", "Impacto a mediano plazo en X área", "Impacto a largo plazo en sostenibilidad", "Factores externos que influyeron"],
      "respuesta_esperada": "Análisis profundo (mínimo 150 palabras) de causas-efectos con relaciones causales claramente identificadas, evidencia para cada afirmación y conclusiones fundamentadas",
      "puntos": 10
    }""",
            
            "resolucion": """    {
      "tipo": "case_study",
      "subtipo": "resolucion",
      "titulo": "Título del problema (máx 10 palabras)",
      "contexto": "CONTEXTO DETALLADO (mínimo 100 palabras): Situación problemática completa con antecedentes de cómo surgió el problema, quiénes están afectados, desde cuándo existe, intentos previos de solución, estado crítico actual, urgencia del problema, recursos disponibles para resolverlo.",
      "descripcion": "DESCRIPCIÓN EXHAUSTIVA (mínimo 150 palabras): Detalles completos del problema incluyendo síntomas específicos, impacto cuantificado en métricas de negocio, afectación a diferentes stakeholders, costos del problema, riesgos si no se resuelve, interdependencias con otros sistemas/procesos, evidencia documental del problema, quejas específicas recibidas.",
      "pregunta": "Propón una solución viable, detallada y práctica para resolver este problema considerando todas las restricciones",
      "restricciones": ["Restricción presupuestaria: máximo $X disponible", "Restricción de tiempo: debe resolverse en Y semanas", "Restricción técnica: compatibilidad con sistema Z", "Restricción de recursos humanos: solo N personas disponibles", "Restricción regulatoria: cumplir norma ABC"],
      "criterios_evaluacion": ["Viabilidad técnica y factibilidad", "Relación costo-beneficio y ROI esperado", "Facilidad y rapidez de implementación", "Impacto positivo medible en métricas clave", "Sostenibilidad a largo plazo", "Aceptación de stakeholders"],
      "respuesta_esperada": "Solución detallada (mínimo 150 palabras) con pasos concretos numerados, cronograma estimado, recursos necesarios, responsables, KPIs de éxito y justificación de por qué esta solución es la óptima",
      "puntos": 10
    }""",
            
            "decision": """    {
      "tipo": "case_study",
      "subtipo": "decision",
      "titulo": "Título de la decisión crítica (máx 10 palabras)",
      "contexto": "CONTEXTO DETALLADO (mínimo 100 palabras): Escenario completo donde se requiere tomar una decisión crítica con impacto significativo. Incluye antecedentes de la situación, presiones externas, plazos límite, stakeholders con sus intereses conflictivos, recursos disponibles, información conocida e incertidumbres.",
      "descripcion": "DESCRIPCIÓN EXHAUSTIVA (mínimo 150 palabras): Detalles completos del escenario de decisión incluyendo quiénes son todos los stakeholders afectados y sus intereses específicos, qué opciones están disponibles con sus características principales, cuáles son los trade-offs entre opciones, qué información falta, cuáles son los riesgos de cada camino, precedentes históricos de decisiones similares, presiones políticas/sociales.",
      "pregunta": "¿Qué decisión tomarías entre las opciones disponibles y por qué es la mejor opción considerando todos los factores?",
      "opciones_disponibles": ["Opción A: descripción detallada de esta alternativa con pros, contras y consecuencias esperadas", "Opción B: descripción completa de segunda alternativa con impactos cuantificados", "Opción C: tercera alternativa con análisis de viabilidad", "Opción D: cuarta opción con riesgos asociados"],
      "criterios_decision": ["Impacto financiero a corto y largo plazo", "Alineación con objetivos estratégicos", "Riesgos y mitigaciones posibles", "Tiempo de implementación requerido", "Aceptación de stakeholders clave", "Sostenibilidad y escalabilidad"],
      "respuesta_esperada": "Decisión justificada (mínimo 150 palabras) con análisis detallado de pros y contras de cada opción, razonamiento lógico, evidencia que soporta la decisión, plan de mitigación de riesgos y criterios de éxito",
      "puntos": 10
    }""",
            
            "comparativo": """    {
      "tipo": "case_study",
      "subtipo": "comparativo",
      "titulo": "Título de la comparación (máx 10 palabras)",
      "contexto": "CONTEXTO DETALLADO (mínimo 100 palabras): Situación que presenta múltiples alternativas a comparar con antecedentes de cada una, mercado/industria donde se aplican, casos de éxito y fracaso previos, tendencias actuales, necesidades específicas del caso de uso.",
      "descripcion": "DESCRIPCIÓN EXHAUSTIVA (mínimo 150 palabras): Detalles completos de cada alternativa incluyendo características técnicas específicas, ventajas y desventajas documentadas, costos detallados (inicial, operativo, mantenimiento), requisitos de implementación, curva de aprendizaje, soporte disponible, casos de uso recomendados, limitaciones conocidas.",
      "pregunta": "Compara críticamente todas las alternativas presentadas utilizando los criterios especificados y recomienda la mejor opción",
      "elementos_comparar": {
        "alternativa_1": {"nombre": "Nombre de alternativa 1", "caracteristicas": ["Característica técnica 1 con detalles", "Característica 2 con métricas", "Ventaja competitiva específica", "Limitación identificada", "Caso de uso ideal"]},
        "alternativa_2": {"nombre": "Nombre de alternativa 2", "caracteristicas": ["Característica técnica 1 con detalles", "Característica 2 con métricas", "Ventaja competitiva específica", "Limitación identificada", "Caso de uso ideal"]},
        "alternativa_3": {"nombre": "Nombre de alternativa 3", "caracteristicas": ["Característica técnica 1 con detalles", "Característica 2 con métricas", "Ventaja competitiva específica", "Limitación identificada", "Caso de uso ideal"]}
      },
      "criterios_comparacion": ["Rendimiento medible en benchmarks", "Costo total de propiedad (TCO)", "Facilidad de uso y curva de aprendizaje", "Escalabilidad y capacidad de crecimiento", "Soporte y ecosistema disponible", "Madurez y estabilidad de la solución"],
      "respuesta_esperada": "Comparación detallada (mínimo 150 palabras) con matriz comparativa, evaluación crítica de cada alternativa contra cada criterio, recomendación fundamentada y escenarios donde cada opción sería la mejor",
      "puntos": 10
    }""",
            
            "predictivo": """    {
      "tipo": "case_study",
      "subtipo": "predictivo",
      "titulo": "Título del escenario predictivo (máx 10 palabras)",
      "contexto": "CONTEXTO DETALLADO (mínimo 100 palabras): Situación actual completa con datos históricos de los últimos meses/años, tendencias observadas con gráficas implícitas, métricas actuales con valores específicos, indicadores clave de rendimiento, comparativas con períodos anteriores, factores externos que están influyendo.",
      "descripcion": "DESCRIPCIÓN EXHAUSTIVA (mínimo 150 palabras): Datos actuales muy específicos incluyendo métricas cuantitativas con números exactos, tasas de crecimiento/decrecimiento observadas, patrones identificados en series de tiempo, eventos recientes que han impactado, señales del mercado, comportamiento de la competencia, cambios en regulaciones, tendencias macroeconómicas, feedback de clientes/usuarios con estadísticas.",
      "pregunta": "Basándote en los datos actuales y tendencias, proyecta el comportamiento futuro de esta situación en los próximos 6-12 meses",
      "datos_actuales": ["Métrica 1: valor actual con % de cambio vs mes anterior", "Indicador 2: cifra específica con tendencia observada", "KPI 3: número actual con histórico de 3 meses", "Variable 4: dato cuantitativo con proyección lineal", "Factor externo 5: impacto medido en la métrica principal"],
      "factores_considerar": ["Factor económico externo con impacto estimado", "Variable de mercado con probabilidad de cambio", "Riesgo identificado con nivel de severidad", "Oportunidad potencial con timeframe", "Tendencia tecnológica con adopción esperada", "Cambio regulatorio con fecha de implementación"],
      "respuesta_esperada": "Predicción fundamentada (mínimo 150 palabras) con proyecciones numéricas específicas, evidencia estadística que soporta la predicción, análisis de tendencias, escenarios alternativos (optimista/realista/pesimista) y justificación matemática o lógica del pronóstico",
      "puntos": 10
    }""",
            
            "simulacion": """    {
      "tipo": "case_study",
      "subtipo": "simulacion",
      "titulo": "Título de la simulación (máx 10 palabras)",
      "contexto": "CONTEXTO DETALLADO (mínimo 100 palabras): Descripción completa del mundo simulado incluyendo reglas del sistema, objetivo general del simulacro, condiciones iniciales del escenario, recursos disponibles al inicio, restricciones del entorno, mecánicas de funcionamiento, cómo interactúan las variables entre sí.",
      "descripcion": "DESCRIPCIÓN EXHAUSTIVA (mínimo 150 palabras): Descripción detallada del sistema completo incluyendo todas las reglas de operación, cómo cada variable afecta a las demás (interdependencias), qué acciones están permitidas, cuáles son los límites del sistema, qué eventos aleatorios pueden ocurrir, cómo se mide el éxito, consecuencias de buenas y malas decisiones.",
      "pregunta": "Toma una secuencia de decisiones estratégicas en este escenario simulado, justificando cada elección basándote en el estado actual del sistema",
      "variables_dinamicas": {
        "variable_1": {"nombre": "Nombre descriptivo de variable 1", "valor_inicial": 100, "rango": "0-200", "descripcion": "Qué representa esta variable y cómo impacta el sistema"},
        "variable_2": {"nombre": "Nombre de variable 2", "valor_inicial": "medio", "opciones": ["bajo", "medio", "alto"], "descripcion": "Significado de cada nivel y sus efectos"},
        "variable_3": {"nombre": "Variable 3", "valor_inicial": 50, "rango": "0-100", "descripcion": "Relación con otras variables y thresholds críticos"}
      },
      "decisiones_tomar": ["Decisión 1: descripción detallada de qué hay que decidir y qué opciones existen", "Decisión 2: contexto específico y timing de esta decisión", "Decisión 3: trade-offs involucrados y consecuencias esperadas", "Decisión 4: dependencias con decisiones anteriores"],
      "respuesta_esperada": "Secuencia de decisiones (mínimo 150 palabras) con justificación detallada basada en el estado simulado del sistema, análisis de cómo cada decisión afecta las variables, predicción de outcomes, y estrategia global coherente",
      "puntos": 10
    }""",
            
            "inverso": """    {
      "tipo": "case_study",
      "subtipo": "inverso",
      "titulo": "Título del caso inverso (máx 10 palabras)",
      "contexto": "CONTEXTO DETALLADO (mínimo 100 palabras): Resultado final conocido con descripción completa del outcome obtenido, cuándo ocurrió, quiénes estuvieron involucrados, qué se logró exactamente con métricas específicas, estado inicial conocido vs estado final, información disponible sobre el proceso.",
      "descripcion": "DESCRIPCIÓN EXHAUSTIVA (mínimo 150 palabras): Descripción muy detallada del resultado final incluyendo todas las características observables, métricas de éxito alcanzadas con números específicos, evidencias documentadas del outcome, comparación con objetivos iniciales, impacto medible del resultado, testimonios o feedback disponible, documentación existente del resultado.",
      "pregunta": "Trabajando hacia atrás desde el resultado final conocido, reconstruye el proceso lógico que probablemente se siguió para llegar a este outcome",
      "resultado_final": "DESCRIPCIÓN DETALLADA (mínimo 80 palabras) del outcome final alcanzado con todas las métricas, características, atributos, impactos medibles, evidencias concretas del éxito o fracaso del resultado",
      "pistas": ["Pista 1: evidencia específica encontrada con detalles", "Pista 2: dato conocido del proceso con contexto", "Pista 3: testimonio o documento que revela información", "Pista 4: patrón observado en el resultado", "Pista 5: inconsistencia o anomalía que da información"],
      "pasos_reconstruir": 5,
      "respuesta_esperada": "Reconstrucción lógica (mínimo 150 palabras) del proceso paso a paso con justificación detallada de por qué cada paso fue necesario, evidencia que soporta cada etapa deducida, razonamiento lógico de la secuencia, y validación de que el proceso reconstruido llevaría al resultado observado",
      "puntos": 10
    }""",
            
            "fallo": """    {
      "tipo": "case_study",
      "subtipo": "fallo",
      "titulo": "Título del desastre/fallo (máx 10 palabras)",
      "contexto": "CONTEXTO DETALLADO (mínimo 100 palabras): Situación previa al fallo con antecedentes de qué se estaba intentando lograr, quiénes estaban involucrados, objetivos iniciales con métricas esperadas, recursos invertidos, expectativas del mercado/stakeholders, presiones existentes, timeline del proyecto/iniciativa.",
      "descripcion": "DESCRIPCIÓN EXHAUSTIVA (mínimo 150 palabras): Descripción completa del fallo incluyendo cronología detallada de eventos que llevaron al desastre, qué específicamente salió mal con evidencia concreta, cuándo se manifestó el problema por primera vez, cómo escaló, qué intentos de corrección fallaron, magnitud del fracaso con números (pérdidas, impacto), reacciones de stakeholders, cobertura mediática si aplica.",
      "pregunta": "Analiza en profundidad qué causó este fallo, identifica las señales de alerta ignoradas y propón cómo se pudo haber prevenido o mitigado",
      "señales_alerta": ["Señal de alerta 1 ignorada: descripción específica de qué warning se pasó por alto y cuándo", "Warning sign 2: indicador específico que mostró problemas con timeline", "Red flag 3: evidencia de riesgo que no se atendió con consecuencias", "Alerta temprana 4: persona o sistema que alertó sin ser escuchado"],
      "consecuencias": ["Consecuencia 1: impacto específico con métrica cuantificada (ej: pérdida de $X millones)", "Impacto 2: efecto en stakeholders con descripción detallada", "Pérdida 3: activo o recurso perdido con valoración", "Daño reputacional 4: impacto en imagen con evidencia", "Consecuencia legal 5: demandas o sanciones enfrentadas"],
      "respuesta_esperada": "Análisis exhaustivo (mínimo 150 palabras) de causas raíz del fallo con evidencia específica, identificación de errores de proceso/juicio, lecciones aprendidas documentadas, medidas de prevención concretas para evitar fallos similares en el futuro, y checklist de early warnings",
      "puntos": 10
    }""",
            
            "creativo": """    {
      "tipo": "case_study",
      "subtipo": "creativo",
      "titulo": "Título del reto creativo (máx 10 palabras)",
      "contexto": "CONTEXTO DETALLADO (mínimo 100 palabras): Situación completa que requiere innovación incluyendo estado actual del mercado/industria, necesidad identificada con evidencia de demanda, soluciones existentes y sus limitaciones, oportunidad de innovación con tamaño de mercado potencial, tendencias que favorecen la innovación, casos inspiradores de innovaciones similares.",
      "descripcion": "DESCRIPCIÓN EXHAUSTIVA (mínimo 150 palabras): Descripción detallada del desafío u oportunidad de innovación incluyendo pain points específicos de usuarios/clientes con evidencia cualitativa, gaps en soluciones actuales con ejemplos concretos, restricciones tecnológicas o de mercado, barreras de entrada, ventana de oportunidad, stakeholders que se beneficiarían, recursos disponibles para innovar.",
      "pregunta": "Propón una solución creativa, original e innovadora para este desafío que sea viable y tenga alto potencial de impacto",
      "restricciones": ["Restricción presupuestaria: máximo $X para desarrollo inicial", "Limitación tecnológica: debe ser compatible con Y", "Constraint de tiempo: lanzamiento en Z meses", "Restricción regulatoria: debe cumplir con norma ABC", "Limitación de recursos: equipo de N personas disponible"],
      "criterios_creatividad": ["Originalidad: qué tan novedosa es la idea vs soluciones existentes", "Viabilidad técnica: puede construirse con tecnología actual", "Impacto potencial: tamaño del problema resuelto y beneficio generado", "Innovación disruptiva: cambia paradigmas o crea nuevos mercados", "Escalabilidad: puede crecer sin multiplicar costos linealmente", "User experience: qué tan intuitiva y deseabl e es la solución"],
      "respuesta_esperada": "Idea innovadora (mínimo 150 palabras) con descripción detallada de cómo funciona, qué problema resuelve específicamente, por qué es diferente de lo existente, justificación de viabilidad técnica, análisis de mercado potencial, mockups o ejemplos conceptuales, y plan de validación de la idea",
      "puntos": 10
    }""",
            
            "etico": """    {
      "tipo": "case_study",
      "subtipo": "etico",
      "titulo": "Título del dilema ético (máx 10 palabras)",
      "contexto": "CONTEXTO DETALLADO (mínimo 100 palabras): Situación completa donde surge el conflicto ético incluyendo antecedentes de la empresa/organización, presiones de negocio específicas, stakeholders involucrados con sus intereses, marco regulatorio aplicable, precedentes de casos similares, cultura organizacional, valores declarados vs prácticas reales.",
      "descripcion": "DESCRIPCIÓN EXHAUSTIVA (mínimo 150 palabras): Descripción completa del conflicto entre beneficio empresarial y consideraciones éticas/morales incluyendo números específicos de impacto financiero, quiénes se benefician vs quiénes se perjudican, consecuencias legales potenciales, impacto reputacional, presión de competidores, expectativas de accionistas, opinión pública, evidencia de casos similares.",
      "pregunta": "¿Qué decisión es la correcta balanceando perspectivas éticas, legales y empresariales? Justifica tu posición considerando todos los stakeholders",
      "stakeholders": ["Stakeholder 1: descripción del grupo con sus intereses específicos y poder de influencia", "Parte interesada 2: quiénes son y qué ganan/pierden en cada escenario", "Grupo afectado 3: impacto directo en su bienestar con detalle", "Stakeholder 4: expectativas y poder de presión que ejercen", "Parte 5: derechos que están en juego"],
      "dilema": "DILEMA ESPECÍFICO (mínimo 50 palabras): Descripción detallada del conflicto ético específico con las dos o más opciones mutuamente excluyentes, qué valores entran en conflicto, qué principios éticos están en tensión, ejemplos concretos del trade-off",
      "consideraciones_eticas": ["Principio ético 1: explicación de qué norma moral aplica y cómo", "Valor 2: qué valor fundamental está en juego con justificación", "Norma moral 3: estándar ético relevante de la industria o sociedad", "Framework ético 4: lente de análisis (utilitarismo, deontología, ética de virtudes)", "Precedente 5: casos históricos similares y sus resoluciones"],
      "respuesta_esperada": "Decisión fundamentada (mínimo 150 palabras) balanceando ética, legalidad y necesidades del negocio con análisis de consecuencias de cada opción, framework ético aplicado, justificación moral robusta, consideración de todos los stakeholders, y plan de implementación que minimice daños",
      "puntos": 10
    }""",
            
            "tecnico": """    {
      "tipo": "case_study",
      "subtipo": "tecnico",
      "titulo": "Título del caso técnico (máx 10 palabras)",
      "contexto": "CONTEXTO DETALLADO (mínimo 100 palabras): Descripción completa del sistema, algoritmo o proceso técnico actual incluyendo arquitectura general, tecnologías utilizadas, escala de operación, volumetría de datos procesados, usuarios concurrentes, infraestructura donde corre, historial de performance, evolución del sistema en el tiempo.",
      "descripcion": "DESCRIPCIÓN EXHAUSTIVA (mínimo 150 palabras): Descripción técnica completa del sistema incluyendo componentes específicos con sus versiones, flujo de datos detallado, integraciones existentes, métricas de rendimiento actuales con números exactos (latencia P95, throughput, error rate), cuellos de botella identificados con evidencia de profiling, limitaciones de la arquitectura actual, deuda técnica acumulada, incidentes recientes relacionados con performance.",
      "pregunta": "Optimiza este sistema técnico mejorando significativamente su rendimiento mientras mantienes o reduces costos operativos",
      "metricas_actuales": {
        "rendimiento": "Descripción de métrica con valor actual específico (ej: 'Latencia P95: 450ms, objetivo <200ms')",
        "throughput": "Capacidad actual con unidades (ej: '1,500 req/seg, picos de 2,000')",
        "eficiencia": "Uso de recursos con porcentajes (ej: 'CPU al 75% promedio, RAM 80% utilizada')",
        "costo": "Costo operativo mensual (ej: '$12,000/mes en infra cloud')",
        "disponibilidad": "SLA actual y uptime (ej: '99.5% uptime, objetivo 99.9%')"
      },
      "limitaciones_tecnicas": ["Limitación 1: constraint específico con impacto medible (ej: 'DB single-threaded limita writes a 5k/seg')", "Constraint técnico 2: bottleneck identificado con evidencia", "Limitación 3: dependencia legacy que genera fricción", "Constraint 4: restricción de infraestructura o presupuesto", "Limitación 5: compatibilidad requerida que limita opciones"],
      "objetivos_optimizacion": ["Mejorar latencia P95 en 50% (de 450ms a <225ms)", "Incrementar throughput en 3x (de 1.5k a 4.5k req/seg)", "Reducir costos de infraestructura en 30% ($12k a $8.4k/mes)", "Alcanzar 99.9% uptime (actualmente 99.5%)", "Reducir error rate de 0.5% a <0.1%"],
      "respuesta_esperada": "Propuesta de optimización técnica (mínimo 150 palabras) con arquitectura mejorada detallada, cambios específicos propuestos con justificación técnica, estimación cuantitativa de mejoras esperadas en cada métrica, análisis de costo-beneficio, plan de implementación por fases, estrategia de testing y rollback, y métricas para validar éxito",
      "puntos": 10
    }"""
        }
        
        return formatos_casos.get(tipo_caso, formatos_casos["descriptivo"])
    
    def _extraer_preguntas_simple(self, respuesta: str, tipo_esperado: str) -> List[PreguntaExamen]:
        """Extrae preguntas de UN SOLO TIPO sin filtrado complejo
        Usado para generación por bloques donde ya sabemos el tipo esperado
        """
        import json
        
        print(f"  📥 Extrayendo preguntas de tipo '{tipo_esperado}'...")
        
        try:
            # 🔥 CORREGIDO: Buscar PRIMERO el array '[' porque esperamos una lista de preguntas
            inicio_array = respuesta.find('[')
            inicio_objeto = respuesta.find('{')
            
            # Priorizar el array si existe y viene antes o justo después del objeto
            if inicio_array != -1 and (inicio_objeto == -1 or inicio_array < inicio_objeto):
                inicio = inicio_array
            elif inicio_objeto != -1:
                # Si el objeto viene primero, verificar si está dentro de un array
                if inicio_array != -1 and inicio_array < inicio_objeto + 5:
                    inicio = inicio_array  # Usar el array que contiene los objetos
                else:
                    inicio = inicio_objeto
            else:
                print(f"  ❌ No se encontró JSON en la respuesta")
                return []
            
            # Extraer hasta el final balanceado
            nivel = 0
            en_string = False
            escape = False
            fin = inicio
            
            for i in range(inicio, len(respuesta)):
                c = respuesta[i]
                
                if escape:
                    escape = False
                    continue
                
                if c == '\\':
                    escape = True
                    continue
                
                if c == '"':
                    en_string = not en_string
                    continue
                
                if not en_string:
                    if c in '{[':
                        nivel += 1
                    elif c in '}]':
                        nivel -= 1
                        if nivel == 0:
                            fin = i + 1
                            break
            
            json_str = respuesta[inicio:fin]
            
            # Limpiar JSON: eliminar saltos de línea dentro de strings
            # Esto soluciona cuando el modelo genera JSON con saltos de línea en opciones
            try:
                # Intentar parsear directamente primero
                datos = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"  ⚠️  Error inicial de JSON: {e}")
                print(f"  🔧 Intentando limpiar JSON...")
                
                # Estrategia de limpieza: reemplazar saltos de línea dentro de strings
                # pero preservar la estructura del JSON
                import re
                
                # Opción 1: Intentar con json.loads con strict=False
                try:
                    datos = json.loads(json_str, strict=False)
                except:
                    # Opción 2: Limpiar múltiples problemas comunes
                    json_limpio = json_str
                    
                    # 1. Limpiar saltos de línea entre elementos de array
                    # Patrón: "texto",\n      "texto2" → "texto", "texto2"
                    json_limpio = re.sub(r'",\s*\n\s*"', '", "', json_limpio)
                    
                    # 2. Limpiar saltos de línea después de corchetes de apertura
                    # Patrón: [\n      "texto" → ["texto"
                    json_limpio = re.sub(r'\[\s*\n\s*"', '["', json_limpio)
                    
                    # 3. Limpiar saltos de línea antes de corchetes de cierre
                    # Patrón: "texto"\n      ] → "texto"]
                    json_limpio = re.sub(r'"\s*\n\s*\]', '"]', json_limpio)
                    
                    # 4. Normalizar espacios múltiples
                    json_limpio = re.sub(r'\s+', ' ', json_limpio)
                    
                    try:
                        datos = json.loads(json_limpio)
                        print(f"  ✅ JSON limpiado exitosamente")
                    except Exception as e2:
                        print(f"  ❌ Error después de limpiar: {e2}")
                        print(f"  📄 JSON problemático (primeros 500 chars):")
                        print(f"  {json_limpio[:500]}")
                        raise e  # Re-lanzar error original
            
            # Extraer array de preguntas
            lista_preguntas = []
            if isinstance(datos, list):
                lista_preguntas = datos
                print(f"  📊 Datos es un array con {len(datos)} elementos")
            elif isinstance(datos, dict):
                print(f"  📊 Datos es un diccionario con keys: {list(datos.keys())}")
                if 'preguntas' in datos:
                    lista_preguntas = datos['preguntas']
                elif 'questions' in datos:
                    lista_preguntas = datos['questions']
                elif 'tipo' in datos or 'type' in datos:
                    # Es una pregunta única
                    lista_preguntas = [datos]
            else:
                print(f"  ⚠️ Tipo de datos inesperado: {type(datos)}")
            
            print(f"  📋 Total de preguntas en lista_preguntas: {len(lista_preguntas)}")
            
            # Convertir a objetos PreguntaExamen
            preguntas = []
            for idx, p in enumerate(lista_preguntas, 1):
                try:
                    print(f"  📝 Procesando pregunta {idx}/{len(lista_preguntas)}")
                    print(f"     Tipo: {p.get('tipo', 'N/A')}")
                    print(f"     Pregunta: {p.get('pregunta', '')[:60]}...")
                    pregunta = PreguntaExamen.from_dict(p)
                    preguntas.append(pregunta)
                    print(f"     ✅ Pregunta {idx} procesada correctamente")
                except Exception as e:
                    print(f"  ⚠️ Error parseando pregunta {idx}: {e}")
                    print(f"     Datos de la pregunta: {p}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            print(f"  ✅ Extraídas {len(preguntas)} preguntas de {len(lista_preguntas)} encontradas")
            return preguntas
            
        except Exception as e:
            print(f"  ❌ Error extrayendo JSON: {e}")
            return []
    
    def _extraer_preguntas(self, respuesta: str, num_preguntas: Dict[str, int] = None) -> List[PreguntaExamen]:
        """Extrae preguntas del JSON"""
        try:
            print(f"\n{'='*60}")
            print(f"🔍 EXTRAYENDO JSON DE LA RESPUESTA")
            print(f"{'='*60}")
            
            # Estrategia mejorada para DeepSeek-R1: buscar TODOS los bloques JSON potenciales
            # Buscar todas las apariciones de { que puedan ser inicio de JSON
            posibles_jsons = []
            
            for i, char in enumerate(respuesta):
                if char == '{':
                    # Encontrar el cierre balanceado del JSON desde esta posición
                    nivel = 0
                    fin = i
                    en_string = False
                    escape = False
                    
                    for j in range(i, len(respuesta)):
                        c = respuesta[j]
                        
                        if escape:
                            escape = False
                            continue
                        
                        if c == '\\':
                            escape = True
                            continue
                        
                        if c == '"':
                            en_string = not en_string
                            continue
                        
                        if not en_string:
                            if c == '{':
                                nivel += 1
                            elif c == '}':
                                nivel -= 1
                                if nivel == 0:
                                    fin = j + 1
                                    json_candidato = respuesta[i:fin]
                                    # Solo considerar JSONs que parezcan razonables (> 50 chars)
                                    if len(json_candidato) > 50:
                                        posibles_jsons.append((i, fin, json_candidato))
                                    break
            
            print(f"🔍 Encontrados {len(posibles_jsons)} bloques JSON potenciales")
            
            # Estrategia 1: Buscar JSON completo balanceado
            json_str = None
            inicio = -1
            fin = -1
            
            # Intentar parsear cada JSON candidato, priorizando los más largos
            posibles_jsons.sort(key=lambda x: len(x[2]), reverse=True)
            
            # FASE 1: Buscar JSON con array de preguntas completo
            for idx, (start, end, candidato) in enumerate(posibles_jsons):
                print(f"  📦 Candidato {idx+1}: posición {start}-{end}, tamaño {len(candidato)} chars")
                print(f"     Inicio: {candidato[:80]}...")
                
                # PRIORIDAD 1: JSON con "preguntas" o "questions" (array completo)
                if '"preguntas"' in candidato or '"questions"' in candidato:
                    # RECHAZAR si contiene placeholders COMO VALORES (no en texto de preguntas)
                    tiene_placeholders = False
                    if ('"puntos": ...' in candidato or 
                        '"puntos":...' in candidato or
                        '"opciones": [...]' in candidato or
                        '"pregunta": "..."' in candidato or
                        '": "..."' in candidato):
                        print(f"     ⚠️ Contiene placeholders COMO VALORES, descartando")
                        tiene_placeholders = True
                    
                    if not tiene_placeholders:
                        print(f"     ✅ Contiene array de preguntas y NO tiene placeholders")
                        json_str = candidato
                        inicio = start
                        fin = end
                        break
                else:
                    print(f"     ⏭️ No contiene array 'preguntas', continuando búsqueda...")
            
            # FASE 2: Si no encontró array completo, buscar preguntas individuales
            if json_str is None:
                print(f"  💡 No se encontró array completo, buscando preguntas individuales...")
                for idx, (start, end, candidato) in enumerate(posibles_jsons):
                    if '"tipo"' in candidato or '"type"' in candidato:
                        tiene_placeholders = False
                        if ('"puntos": ...' in candidato or 
                            '"puntos":...' in candidato or
                            '"opciones": [...]' in candidato or
                            '"pregunta": "..."' in candidato or
                            '": "..."' in candidato):
                            continue
                        
                        print(f"     ✅ Usando pregunta individual como fallback")
                        json_str = candidato
                        inicio = start
                        fin = end
                        break
            
            if json_str is None and posibles_jsons:
                # Si ninguno tiene campos de pregunta, tomar el más largo
                inicio, fin, json_str = posibles_jsons[0]
                print(f"  💡 Usando JSON más largo como fallback")
            
            if json_str:
                print(f"✅ JSON seleccionado en posición {inicio}-{fin}")
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
                    
                    # Registrar JSON extraído
                    self._agregar_log('json_extraido', json_str)
                    
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
                        # Si es un objeto con campos de pregunta (type, statement, etc.), es UNA pregunta
                        elif 'type' in datos or 'tipo' in datos:
                            print(f"💡 El JSON es una pregunta única, convirtiéndola a array")
                            lista_preguntas = [datos]
                        else:
                            print(f"⚠️ JSON no reconocido, retornando vacío")
                            return []
                    else:
                        lista_preguntas = datos.get(campo_preguntas, [])
                    
                    preguntas = []
                    preguntas_parseadas_log = []
                    for i, p in enumerate(lista_preguntas):
                        try:
                            pregunta = PreguntaExamen.from_dict(p)
                            preguntas.append(pregunta)
                            preguntas_parseadas_log.append(pregunta.to_dict() if hasattr(pregunta, 'to_dict') else str(pregunta))
                            tipo = p.get('tipo') or p.get('type', 'unknown')
                            texto = p.get('pregunta') or p.get('question', '')
                            print(f"✅ Pregunta {i+1}: {tipo} - {texto[:50]}...")
                        except Exception as e:
                            error_msg = f"Error en pregunta {i+1}: {e}"
                            print(f"❌ {error_msg}")
                            self._agregar_log('errores', error_msg)
                            continue
                    
                    # Registrar preguntas parseadas
                    self._agregar_log('preguntas_parseadas', preguntas_parseadas_log)
                    
                    print(f"\n✅ Total: {len(preguntas)} preguntas generadas exitosamente")
                    
                    # PASO 1: Eliminar duplicados exactos y similares
                    preguntas_unicas = []
                    textos_vistos = set()
                    
                    def similitud_texto(t1, t2):
                        """Calcula similitud básica entre dos textos"""
                        palabras1 = set(t1.lower().split())
                        palabras2 = set(t2.lower().split())
                        if not palabras1 or not palabras2:
                            return 0
                        interseccion = palabras1.intersection(palabras2)
                        union = palabras1.union(palabras2)
                        return len(interseccion) / len(union)
                    
                    for pregunta in preguntas:
                        texto_normalizado = pregunta.pregunta.strip().lower()
                        
                        # Verificar duplicado exacto
                        if texto_normalizado in textos_vistos:
                            print(f"  🗑️  Duplicado exacto: {pregunta.pregunta[:60]}...")
                            continue
                        
                        # Verificar similitud alta (>80%) con preguntas existentes
                        es_similar = False
                        for texto_visto in textos_vistos:
                            if similitud_texto(texto_normalizado, texto_visto) > 0.8:
                                print(f"  🗑️  Muy similar: {pregunta.pregunta[:60]}...")
                                es_similar = True
                                break
                        
                        if not es_similar:
                            preguntas_unicas.append(pregunta)
                            textos_vistos.add(texto_normalizado)
                    
                    if len(preguntas_unicas) < len(preguntas):
                        print(f"🧹 Duplicados/similares eliminados: {len(preguntas)} → {len(preguntas_unicas)} preguntas únicas")
                    
                    # PASO 2: FILTRAR PREGUNTAS POR TIPO Y CANTIDAD SOLICITADA
                    if num_preguntas and any(v > 0 for v in num_preguntas.values()):
                        preguntas_filtradas = []
                        contador_por_tipo = {}
                        
                        # Mapeo de tipos nuevos a tipos del sistema
                        mapeo_tipos = {
                            'flashcard': 'flashcard',
                            'mcq': 'mcq', 
                            'true_false': 'true_false',
                            'verdadero_falso': 'true_false',
                            'verdadero-falso': 'true_false',
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
                        
                        for pregunta in preguntas_unicas:
                            # DEBUG: Imprimir tipo exacto de la pregunta
                            print(f"  🔍 Pregunta tipo='{pregunta.tipo}' (repr: {repr(pregunta.tipo)})")
                            tipo_normalizado = mapeo_tipos.get(pregunta.tipo, pregunta.tipo)
                            print(f"     → Normalizado a: '{tipo_normalizado}'")
                            cantidad_solicitada = num_preguntas.get(tipo_normalizado, 0)
                            print(f"     → Cantidad solicitada de '{tipo_normalizado}': {cantidad_solicitada}")
                            
                            # NUEVO: Aceptar preguntas incluso si no se solicitaron explícitamente
                            # siempre que sean de tipos válidos (mcq, true_false, short_answer, etc.)
                            if cantidad_solicitada > 0:
                                if tipo_normalizado not in contador_por_tipo:
                                    contador_por_tipo[tipo_normalizado] = 0
                                
                                if contador_por_tipo[tipo_normalizado] < cantidad_solicitada:
                                    preguntas_filtradas.append(pregunta)
                                    contador_por_tipo[tipo_normalizado] += 1
                                    print(f"     ✅ Aceptada (solicitada)")
                                else:
                                    print(f"     ❌ Rechazada (ya se alcanzó el límite de {cantidad_solicitada})")
                            elif tipo_normalizado in ['mcq', 'true_false', 'short_answer', 'open_question', 'flashcard']:
                                # Tipos válidos aunque no solicitados explícitamente - ACEPTAR
                                if tipo_normalizado not in contador_por_tipo:
                                    contador_por_tipo[tipo_normalizado] = 0
                                preguntas_filtradas.append(pregunta)
                                contador_por_tipo[tipo_normalizado] += 1
                                print(f"     ✅ Aceptada (tipo válido extra)")
                            else:
                                print(f"     ❌ Rechazada (tipo no solicitado ni en lista válida)")
                        
                        print(f"🔍 Filtrado: {len(preguntas_unicas)} únicas → {len(preguntas_filtradas)} solicitadas")
                        print(f"   Solicitadas: {num_preguntas}")
                        print(f"   Filtradas por tipo: {contador_por_tipo}")
                        
                        # Registrar filtrado
                        self._agregar_log('filtrado', {
                            'total_generadas_originales': len(preguntas),
                            'total_unicas': len(preguntas_unicas),
                            'total_filtradas': len(preguntas_filtradas),
                            'solicitadas': num_preguntas,
                            'contador_por_tipo': contador_por_tipo
                        })
                        
                        # Verificar si faltaron preguntas
                        tipos_faltantes = []
                        for tipo, cantidad in num_preguntas.items():
                            generadas = contador_por_tipo.get(tipo, 0)
                            if generadas < cantidad:
                                tipos_faltantes.append(f"{tipo}: {generadas}/{cantidad}")
                        
                        if tipos_faltantes:
                            warning_msg = f"Tipos con menos preguntas generadas: {', '.join(tipos_faltantes)}"
                            self._agregar_log('advertencia', warning_msg)
                            print(f"ℹ️  INFO: Distribución de preguntas generadas:")
                            for faltante in tipos_faltantes:
                                print(f"   📊 {faltante}")
                            print(f"   💡 El examen sigue siendo válido. Si necesitas exactamente la cantidad solicitada, puedes regenerar.")
                        
                        # Registrar resultado final
                        resultado_final = [p.to_dict() if hasattr(p, 'to_dict') else str(p) for p in preguntas_filtradas]
                        self._agregar_log('resultado_final', resultado_final)
                        self._guardar_log()
                        
                        return preguntas_filtradas
                    
                    # Si no hay filtrado, retornar todas las preguntas únicas
                    resultado_final = [p.to_dict() if hasattr(p, 'to_dict') else str(p) for p in preguntas_unicas]
                    self._agregar_log('resultado_final', resultado_final)
                    self._guardar_log()
                    
                    return preguntas_unicas
                    
                except json.JSONDecodeError as e:
                        error_msg = f"Error parseando JSON: {e}"
                        print(f"❌ {error_msg}")
                        print(f"📄 JSON problemático (primeros 500):\n{json_str[:500]}")
                        print(f"📄 Últimos 200 caracteres:\n{json_str[-200:]}")
                        
                        # INTENTO DE REPARACIÓN AGRESIVA
                        print(f"\n🔧 Intentando reparación agresiva del JSON...")
                        
                        # Eliminar texto después del último } válido
                        ultimo_cierre = json_str.rfind('}')
                        if ultimo_cierre > 0:
                            json_str_cortado = json_str[:ultimo_cierre + 1]
                            
                            # Asegurar que cierra el array de preguntas
                            if '"preguntas"' in json_str_cortado and not json_str_cortado.strip().endswith(']}'):
                                json_str_cortado = json_str_cortado.rstrip() + ']}'
                            
                            try:
                                datos = json.loads(json_str_cortado)
                                print(f"✅ JSON reparado exitosamente cortando al último }}")
                                
                                # Continuar con el procesamiento normal
                                campo_preguntas = None
                                if 'preguntas' in datos:
                                    campo_preguntas = 'preguntas'
                                elif 'questions' in datos:
                                    campo_preguntas = 'questions'
                                
                                if campo_preguntas:
                                    lista_preguntas = datos[campo_preguntas]
                                    if isinstance(lista_preguntas, list):
                                        # Convertir a objetos PreguntaExamen
                                        preguntas = []
                                        preguntas_parseadas_log = []
                                        
                                        for i, pregunta_dict in enumerate(lista_preguntas):
                                            try:
                                                pregunta_obj = PreguntaExamen.from_dict(pregunta_dict)
                                                preguntas.append(pregunta_obj)
                                                print(f"✅ Pregunta {i+1}: {pregunta_obj.tipo} - {pregunta_obj.pregunta[:50]}...")
                                                preguntas_parseadas_log.append(pregunta_obj.to_dict())
                                            except Exception as e:
                                                error_msg = f"Error en pregunta {i+1}: {e}"
                                                print(f"❌ {error_msg}")
                                                self._agregar_log('errores', error_msg)
                                                continue
                                        
                                        self._agregar_log('preguntas_parseadas', preguntas_parseadas_log)
                                        print(f"\n✅ Total: {len(preguntas)} preguntas generadas exitosamente")
                                        
                                        # Aplicar filtrado si es necesario
                                        if num_preguntas and any(v > 0 for v in num_preguntas.values()):
                                            preguntas = self._filtrar_preguntas(preguntas, num_preguntas)
                                        
                                        resultado_final = [p.to_dict() if hasattr(p, 'to_dict') else str(p) for p in preguntas]
                                        self._agregar_log('resultado_final', resultado_final)
                                        self._guardar_log()
                                        return preguntas
                            except:
                                pass
                        
                        self._agregar_log('errores', error_msg)
                        self._agregar_log('json_extraido', json_str[:1000])
                        self._guardar_log()
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
            error_msg = "No se encontró JSON válido en la respuesta del modelo"
            self._agregar_log('errores', error_msg)
            self._guardar_log()
            return []
            
        except Exception as e:
            error_msg = f"Error general extrayendo JSON: {e}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            self._agregar_log('errores', error_msg)
            self._guardar_log()
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
            # Obtener explicacion desde metadata (campo del JSON del usuario)
            meta_mcq = pregunta.metadata if isinstance(getattr(pregunta, 'metadata', None), dict) else {}
            explicacion = meta_mcq.get('explicacion') or meta_mcq.get('explanation') or ''
            
            # Comparación flexible: extraer solo la letra inicial si la hay
            import re as _re
            def _extraer_letra(s):
                m = _re.match(r'^\s*([A-Da-d])\s*[\.\)\:]?', s)
                return m.group(1).upper() if m else s.strip().upper()
            
            letra_usuario  = _extraer_letra(respuesta_usuario)
            letra_correcta = _extraer_letra(respuesta_correcta)
            
            # Comparar por letra extraída primero, luego por contenido completo
            es_correcto = (
                letra_usuario == letra_correcta or
                respuesta_usuario_lower in respuesta_correcta_lower or
                respuesta_correcta_lower in respuesta_usuario_lower
            )
            
            if es_correcto:
                resultado["correcta"] = True
                resultado["puntos_obtenidos"] = pregunta.puntos
                fb = "✅ ¡Correcto!"
                if explicacion:
                    fb += f"\n💡 {explicacion}"
                resultado["feedback"] = fb
            else:
                # Buscar el texto completo de la opción correcta
                opciones = pregunta.opciones or []
                opcion_correcta_texto = pregunta.respuesta_correcta
                for op in opciones:
                    if _extraer_letra(str(op)) == letra_correcta:
                        opcion_correcta_texto = op
                        break
                fb = f"❌ Incorrecto. La respuesta correcta es: {opcion_correcta_texto}"
                if explicacion:
                    fb += f"\n💡 {explicacion}"
                resultado["feedback"] = fb
        
        elif pregunta.tipo in ["verdadero_falso", "verdadero-falso", "true_false"]:
            meta_tf = pregunta.metadata if isinstance(getattr(pregunta, 'metadata', None), dict) else {}
            explicacion = meta_tf.get('explicacion') or meta_tf.get('explanation') or ''
            
            # Extraer respuesta correcta de metadata si existe
            respuesta_correcta_display = pregunta.respuesta_correcta
            if meta_tf:
                correct_answer = meta_tf.get('correct_answer')
                if correct_answer is not None:
                    respuesta_correcta_display = 'Verdadero' if correct_answer else 'Falso'
            
            # Normalizar respuestas para comparación flexible
            def _norm_tf(s):
                return (s.lower()
                        .replace('verdadero', 'true').replace('falso', 'false')
                        .replace('yes', 'true').replace('no', 'false')
                        .strip())
            
            if _norm_tf(respuesta_usuario) == _norm_tf(respuesta_correcta_display):
                resultado["correcta"] = True
                resultado["puntos_obtenidos"] = pregunta.puntos
                fb = "✅ ¡Correcto!"
                if explicacion:
                    fb += f"\n💡 {explicacion}"
                resultado["feedback"] = fb
            else:
                fb = f"❌ Incorrecto. La respuesta correcta es: {respuesta_correcta_display}"
                if explicacion:
                    fb += f"\n💡 {explicacion}"
                resultado["feedback"] = fb
        
        elif pregunta.tipo == "short_answer":
            # ========== EVALUACIÓN POR PALABRAS CLAVE (sin IA) ==========
            palabras_clave = getattr(pregunta, 'palabras_clave', None) or pregunta.metadata.get('palabras_clave', [])
            respuesta_esperada = (
                getattr(pregunta, 'respuesta_esperada', None) or
                pregunta.metadata.get('respuesta_esperada', '') or
                pregunta.respuesta_correcta or ''
            )
            texto_usuario = respuesta_usuario.strip().lower()

            if palabras_clave:
                # Grading por palabras clave: cuenta cuántas están en la respuesta del usuario
                encontradas = []
                faltantes = []
                for kw in palabras_clave:
                    if str(kw).lower() in texto_usuario:
                        encontradas.append(kw)
                    else:
                        faltantes.append(kw)
                proporcion = len(encontradas) / len(palabras_clave)
                puntos = round(proporcion * pregunta.puntos, 1)
                correcto = proporcion >= 0.6

                if proporcion == 1.0:
                    fb = f"✅ Respuesta completa. Contiene todas las palabras clave: {', '.join(encontradas)}."
                elif proporcion >= 0.6:
                    fb = f"✅ Aceptable ({int(proporcion*100)}%). Palabras encontradas: {', '.join(encontradas)}. Faltó incluir: {', '.join(faltantes)}."
                elif proporcion > 0:
                    fb = f"⚠️ Incompleto ({int(proporcion*100)}%). Solo mencionaste: {', '.join(encontradas)}. Faltaron: {', '.join(faltantes)}."
                else:
                    fb = f"❌ No se encontraron las palabras clave esperadas: {', '.join(faltantes)}."
                    if respuesta_esperada:
                        fb += f" Respuesta esperada: {respuesta_esperada}"

                resultado["correcta"] = correcto
                resultado["puntos_obtenidos"] = puntos
                resultado["feedback"] = fb
                print(f"📝 short_answer → palabras_clave {len(encontradas)}/{len(palabras_clave)} → {puntos}/{pregunta.puntos} pts")
            elif respuesta_esperada:
                # Sin palabras_clave: comparación por similitud con respuesta_esperada
                palabras_esperadas = set(w for w in respuesta_esperada.lower().split() if len(w) > 3)
                palabras_usuario_set = set(w for w in texto_usuario.split() if len(w) > 3)
                if palabras_esperadas:
                    coincidencias = palabras_esperadas.intersection(palabras_usuario_set)
                    proporcion = len(coincidencias) / len(palabras_esperadas)
                    puntos = round(proporcion * pregunta.puntos, 1)
                    correcto = proporcion >= 0.6
                    resultado["correcta"] = correcto
                    resultado["puntos_obtenidos"] = puntos
                    resultado["feedback"] = (
                        f"{'✅' if correcto else '❌'} ({int(proporcion*100)}% coincidencia). "
                        f"Respuesta esperada: {respuesta_esperada}"
                    )
                else:
                    resultado["feedback"] = f"Sin respuesta esperada definida. Se asignan 0 puntos."
            else:
                resultado["feedback"] = "No hay criterios de evaluación definidos para esta pregunta."

        elif pregunta.tipo == "open_question":
            # ===== EVALUACIÓN POR PUNTOS_CLAVE (sin IA cuando están definidos) =====
            meta_oq = pregunta.metadata if isinstance(getattr(pregunta, 'metadata', None), dict) else {}
            puntos_clave = meta_oq.get('puntos_clave') or []
            respuesta_modelo_oq = meta_oq.get('respuesta_modelo') or meta_oq.get('model_answer') or pregunta.respuesta_correcta or ''
            texto_usuario = respuesta_usuario.strip().lower()

            if puntos_clave:
                encontradas = [p for p in puntos_clave if str(p).strip().lower() in texto_usuario]
                faltantes   = [p for p in puntos_clave if str(p).strip().lower() not in texto_usuario]
                proporcion  = len(encontradas) / len(puntos_clave)
                puntos_oq   = round(proporcion * pregunta.puntos, 1)
                correcto    = proporcion >= 0.6
                if proporcion == 1.0:
                    fb = f"✅ Excelente — mencionaste todos los puntos clave ({len(encontradas)}/{len(puntos_clave)})."
                elif correcto:
                    fb = (f"✅ Bien — cubriste {len(encontradas)}/{len(puntos_clave)} puntos. "
                          + (f"Faltó mencionar: {', '.join(faltantes)}." if faltantes else ""))
                else:
                    fb = (f"❌ Incompleto — solo {len(encontradas)}/{len(puntos_clave)} puntos. "
                          f"Asegúrate de incluir: {', '.join(faltantes)}.")
                if respuesta_modelo_oq:
                    fb += f"\n📖 Respuesta modelo: {respuesta_modelo_oq}"
                resultado["correcta"] = correcto
                resultado["puntos_obtenidos"] = puntos_oq
                resultado["feedback"] = fb
            else:
                # Sin puntos_clave — usar IA
                print(f"\n🤖 open_question sin puntos_clave — evaluando con IA...")
                resultado = self._evaluar_con_ia(pregunta, respuesta_usuario)

        elif pregunta.tipo in ("caso_estudio", "case_study"):
            # ===== EVALUACIÓN POR PUNTOS_EVALUACION (sin IA cuando están definidos) =====
            meta_cs = pregunta.metadata if isinstance(getattr(pregunta, 'metadata', None), dict) else {}
            puntos_eval = meta_cs.get('puntos_evaluacion') or meta_cs.get('evaluation_criteria') or []
            texto_usuario = respuesta_usuario.strip().lower()

            if puntos_eval:
                encontradas = [p for p in puntos_eval if str(p).strip().lower() in texto_usuario]
                faltantes   = [p for p in puntos_eval if str(p).strip().lower() not in texto_usuario]
                proporcion  = len(encontradas) / len(puntos_eval)
                puntos_cs   = round(proporcion * pregunta.puntos, 1)
                correcto    = proporcion >= 0.6
                if proporcion == 1.0:
                    fb = f"✅ Análisis completo — abordaste todos los criterios ({len(encontradas)}/{len(puntos_eval)})."
                elif correcto:
                    fb = (f"✅ Buen análisis — cubriste {len(encontradas)}/{len(puntos_eval)} criterios. "
                          + (f"Podrías ampliar: {', '.join(faltantes)}." if faltantes else ""))
                else:
                    fb = (f"❌ Análisis incompleto — solo {len(encontradas)}/{len(puntos_eval)} criterios. "
                          f"Asegúrate de trabajar: {', '.join(faltantes)}.")
                resultado["correcta"] = correcto
                resultado["puntos_obtenidos"] = puntos_cs
                resultado["feedback"] = fb
            else:
                # Sin criterios — usar IA
                print(f"\n🤖 caso_estudio sin puntos_evaluacion — evaluando con IA...")
                resultado = self._evaluar_con_ia(pregunta, respuesta_usuario)

        elif pregunta.tipo in ["corta", "desarrollo",
                               "flashcard", "cloze",
                               "reading_comprehension", "reading_true_false", "reading_cloze", 
                               "reading_skill", "reading_matching", "reading_sequence",
                               "writing_short", "writing_paraphrase", "writing_correction",
                               "writing_transformation", "writing_essay", "writing_sentence_builder",
                               "writing_picture_description", "writing_email"]:
            # Para estos tipos, usar IA para evaluar
            print(f"\n🤖 Evaluando respuesta de tipo '{pregunta.tipo}' con IA...")
            resultado = self._evaluar_con_ia(pregunta, respuesta_usuario)
        
        else:
            # Tipo desconocido - evaluar con IA por defecto
            print(f"\n⚠️ Tipo de pregunta desconocido: '{pregunta.tipo}' - usando evaluación con IA")
            resultado = self._evaluar_con_ia(pregunta, respuesta_usuario)
        
        return resultado
    
    def _evaluar_con_ia(self, pregunta: PreguntaExamen, respuesta_usuario: str) -> dict:
        """Evalúa una respuesta de desarrollo/corta usando IA"""
        
        # ========== EVALUACIÓN ESPECIAL PARA CLOZE ==========
        if pregunta.tipo == 'cloze' and hasattr(pregunta, 'metadata') and pregunta.metadata:
            meta = pregunta.metadata if isinstance(pregunta.metadata, dict) else {}
            # Soportar tanto 'answers' (inglés) como 'respuestas' (español)
            respuestas_correctas = meta.get('answers') or meta.get('respuestas') or []
            # También intentar desde respuesta_correcta del objeto si ya es string separado por comas
            if not respuestas_correctas and pregunta.respuesta_correcta:
                rc = pregunta.respuesta_correcta
                if isinstance(rc, list):
                    respuestas_correctas = rc
                elif isinstance(rc, str) and (',' in rc or rc):
                    respuestas_correctas = [r.strip() for r in rc.split(',')]
            if respuestas_correctas:
                
                # Dividir respuestas del usuario (pueden estar separadas por comas o |||)
                respuestas_usuario_lista = []
                if ', ' in respuesta_usuario:
                    respuestas_usuario_lista = [r.strip() for r in respuesta_usuario.split(',')]
                elif '|||' in respuesta_usuario:
                    respuestas_usuario_lista = [r.strip() for r in respuesta_usuario.split('|||')]
                else:
                    respuestas_usuario_lista = [respuesta_usuario.strip()]
                
                # Comparar cada respuesta
                correctas = 0
                total = len(respuestas_correctas)
                conceptos_correctos = []
                conceptos_faltantes = []
                
                for i, respuesta_correcta in enumerate(respuestas_correctas):
                    if i < len(respuestas_usuario_lista):
                        resp_usuario = respuestas_usuario_lista[i].lower().strip()
                        resp_correcta = str(respuesta_correcta).lower().strip()
                        
                        # Comparación flexible (permite variaciones)
                        if resp_usuario == resp_correcta or resp_usuario in resp_correcta or resp_correcta in resp_usuario:
                            correctas += 1
                            conceptos_correctos.append(respuesta_correcta)
                        else:
                            # Verificar similitud básica (al menos 60% de las palabras coinciden)
                            palabras_correcta = set(resp_correcta.split())
                            palabras_usuario = set(resp_usuario.split())
                            if palabras_usuario and palabras_correcta:
                                coincidencia = len(palabras_usuario.intersection(palabras_correcta)) / len(palabras_correcta)
                                if coincidencia >= 0.6:
                                    correctas += 1
                                    conceptos_correctos.append(respuesta_correcta)
                                else:
                                    conceptos_faltantes.append(respuesta_correcta)
                            else:
                                conceptos_faltantes.append(respuesta_correcta)
                    else:
                        conceptos_faltantes.append(respuesta_correcta)
                
                # Calcular puntos
                porcentaje = correctas / total if total > 0 else 0
                puntos = round(porcentaje * pregunta.puntos, 1)
                
                return {
                    "correcta": porcentaje >= 0.6,
                    "puntos_obtenidos": puntos,
                    "conceptos_correctos": conceptos_correctos,
                    "conceptos_faltantes": conceptos_faltantes,
                    "feedback": f"Completaste {correctas}/{total} huecos correctamente ({int(porcentaje*100)}%)."
                }
        
        # ========== EVALUACIÓN NORMAL PARA OTROS TIPOS ==========
        
        # Extraer respuesta correcta / modelo dependiendo del tipo
        respuesta_modelo = pregunta.respuesta_correcta
        meta = pregunta.metadata if isinstance(getattr(pregunta, 'metadata', None), dict) else {}
        
        # Para flashcards, extraer de metadata.solution.answer
        if pregunta.tipo == 'flashcard':
            solution = meta.get('solution', {})
            if isinstance(solution, dict):
                respuesta_modelo = solution.get('answer', respuesta_modelo)
        
        # Para casos de estudio (español e inglés)
        elif pregunta.tipo in ('caso_estudio', 'case_study'):
            # Prioridad: respuesta_esperada > sample_answer > pregunta_principal + puntos_evaluacion
            respuesta_modelo = (
                meta.get('respuesta_esperada') or
                meta.get('sample_answer') or
                respuesta_modelo
            )
            # Si sigue sin haber nada, construir desde pregunta_principal + puntos_evaluacion
            if not respuesta_modelo or respuesta_modelo == 'None':
                pregunta_principal = meta.get('pregunta_principal', '')
                puntos_eval = meta.get('puntos_evaluacion') or meta.get('evaluation_criteria') or []
                partes = []
                if pregunta_principal:
                    partes.append(f"Pregunta central: {pregunta_principal}")
                if puntos_eval:
                    partes.append(f"Criterios de evaluación: {'; '.join(str(p) for p in puntos_eval)}")
                if partes:
                    respuesta_modelo = ' | '.join(partes)
        
        # Para open_question: usar respuesta_modelo o puntos_clave
        elif pregunta.tipo == 'open_question':
            respuesta_modelo = (
                meta.get('respuesta_modelo') or
                meta.get('model_answer') or
                respuesta_modelo
            )
            if not respuesta_modelo or respuesta_modelo == 'None':
                puntos_clave = meta.get('puntos_clave') or []
                if puntos_clave:
                    respuesta_modelo = 'Puntos clave esperados: ' + '; '.join(str(p) for p in puntos_clave)
        
        # Si es un diccionario (fallback), extraer el campo 'answer'
        if isinstance(respuesta_modelo, dict):
            respuesta_modelo = respuesta_modelo.get('answer', str(respuesta_modelo))
        
        # Convertir a string si no lo es
        if not isinstance(respuesta_modelo, str):
            respuesta_modelo = str(respuesta_modelo)
        
        # Si aún es None o vacío, usar un placeholder
        if not respuesta_modelo or respuesta_modelo == 'None':
            respuesta_modelo = "No hay respuesta modelo definida para esta pregunta"
        
        # ── Contexto adicional por tipo ─────────────────────────────────────
        seccion_extra = ""
        if pregunta.tipo in ('open_question',):
            puntos_clave = meta.get('puntos_clave') or []
            if puntos_clave:
                seccion_extra = f"\nPUNTOS CLAVE QUE DEBE MENCIONAR:\n" + "\n".join(f"- {p}" for p in puntos_clave) + "\n"
        elif pregunta.tipo in ('caso_estudio', 'case_study'):
            desc = meta.get('descripcion_caso') or meta.get('scenario') or ''
            pregunta_ppal = meta.get('pregunta_principal') or ''
            puntos_eval = meta.get('puntos_evaluacion') or meta.get('evaluation_criteria') or []
            if desc:
                seccion_extra += f"\nCONTEXTO DEL CASO:\n{desc}\n"
            if pregunta_ppal:
                seccion_extra += f"\nPREGUNTA CENTRAL A RESPONDER:\n{pregunta_ppal}\n"
            if puntos_eval:
                seccion_extra += "\nCRITERIOS A EVALUAR:\n" + "\n".join(f"- {p}" for p in puntos_eval) + "\n"
        # ────────────────────────────────────────────────────────────────────
        
        prompt = f"""Tarea: Evaluación de respuesta académica con retroalimentación detallada.

PREGUNTA:
{pregunta.pregunta}

RESPUESTA ESPERADA / MODELO:
{respuesta_modelo}
{seccion_extra}
RESPUESTA DEL ESTUDIANTE:
{respuesta_usuario}

INSTRUCCIONES:
1. Identifica los conceptos clave de la respuesta esperada
2. Verifica cuáles están presentes en la respuesta del estudiante
3. Calcula: puntos = (conceptos_presentes / total_conceptos) × {pregunta.puntos}
4. El feedback debe ser constructivo y en el mismo idioma de la pregunta

OUTPUT REQUERIDO — JSON únicamente, sin texto extra:
{{
  "puntos": <float entre 0 y {pregunta.puntos}>,
  "conceptos_correctos": [<lista de conceptos encontrados>],
  "conceptos_faltantes": [<lista de conceptos ausentes>],
  "feedback": "<retroalimentación constructiva de 2-3 líneas>"
}}

JSON:"""

        try:
            if self.usar_ollama:
                # Evaluar con Ollama
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": self.modelo_ollama,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,  # Más determinístico
                            "num_predict": 400   # Más tokens para retroalimentación detallada
                        }
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    respuesta_ia = response.json()['response']
                    print(f"📝 Respuesta IA (primeros 300 chars): {respuesta_ia[:300]}")
                    
                    # Detectar rechazo del modelo con más patrones
                    rechazos = [
                        'lo siento', 'no puedo', 'cannot', "can't", 'disculpa', 'sorry',
                        'no pueda', 'unable to', 'cannot fulfill', 'no cumplir',
                        'esa solicitud', 'that request', 'contenido político', 'political content',
                        'evaluar el trabajo', 'generar respuestas que', 'no puedo generar'
                    ]
                    if any(rechazo in respuesta_ia.lower() for rechazo in rechazos):
                        print(f"⚠️ Modelo rechazó evaluar - usando evaluación por similitud de texto")
                        # Calcular similitud mejorada
                        texto_modelo = respuesta_modelo.lower()
                        texto_usuario = respuesta_usuario.lower()
                        
                        # Extraer palabras significativas (más de 3 letras)
                        palabras_modelo = set(p for p in texto_modelo.split() if len(p) > 3)
                        palabras_usuario = set(p for p in texto_usuario.split() if len(p) > 3)
                        
                        coincidencias = palabras_modelo.intersection(palabras_usuario)
                        
                        # Calcular porcentaje basado en palabras clave
                        if len(palabras_modelo) > 0:
                            porcentaje = len(coincidencias) / len(palabras_modelo)
                        else:
                            porcentaje = 0
                        
                        puntos = round(porcentaje * pregunta.puntos, 1)
                        
                        return {
                            "correcta": puntos >= pregunta.puntos * 0.6,
                            "puntos_obtenidos": puntos,
                            "conceptos_correctos": list(coincidencias)[:8],
                            "conceptos_faltantes": list(palabras_modelo - palabras_usuario)[:5],
                            "feedback": f"Evaluación automática: {puntos}/{pregunta.puntos} puntos basado en similitud de conceptos."
                        }
                    
                    # Extraer JSON balanceado
                    inicio = respuesta_ia.find('{')
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
                                feedback += f"\\n\\n✅ Conceptos que dominas: {', '.join(conceptos_correctos)}"
                            if conceptos_faltantes:
                                feedback += f"\\n\\n❌ Conceptos que te faltan comprender: {', '.join(conceptos_faltantes)}"
                            
                            print(f"✅ Evaluación: {puntos}/{pregunta.puntos} puntos")
                            print(f"✅ Conceptos correctos: {conceptos_correctos}")
                            print(f"❌ Conceptos faltantes: {conceptos_faltantes}")
                            
                            return {
                                "correcta": puntos >= pregunta.puntos * 0.6,  # 60% o más es correcto
                                "puntos_obtenidos": puntos,
                                "feedback": feedback,
                                "conceptos_correctos": conceptos_correctos,
                                "conceptos_faltantes": conceptos_faltantes
                            }
            
            # Fallback: evaluación simple por palabras clave
            print("⚠️ Usando evaluación fallback")
            
            # Extraer texto de respuesta correcta (puede ser dict en flashcards)
            respuesta_modelo = pregunta.respuesta_correcta
            if isinstance(respuesta_modelo, dict):
                respuesta_modelo = respuesta_modelo.get('answer', str(respuesta_modelo))
            if not isinstance(respuesta_modelo, str):
                respuesta_modelo = str(respuesta_modelo)
            
            palabras_correctas = set(respuesta_modelo.lower().split())
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
                feedback = f"Incompleto. Respuesta esperada: {respuesta_modelo}"
            
            return {
                "correcta": similitud >= 0.6,
                "puntos_obtenidos": round(puntos, 1),
                "feedback": feedback
            }
            
        except Exception as e:
            print(f"❌ Error evaluando con IA: {e}")
            import traceback
            traceback.print_exc()
            
            # Extraer respuesta modelo para fallback
            respuesta_modelo = pregunta.respuesta_correcta
            if isinstance(respuesta_modelo, dict):
                respuesta_modelo = respuesta_modelo.get('answer', 'No disponible')
            if not isinstance(respuesta_modelo, str):
                respuesta_modelo = str(respuesta_modelo)
            
            # Fallback
            return {
                "correcta": False,
                "puntos_obtenidos": 0,
                "feedback": f"Error en evaluación. Respuesta esperada: {respuesta_modelo}"
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
