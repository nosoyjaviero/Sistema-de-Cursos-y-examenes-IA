"""
Sistema de generación y evaluación de exámenes con IA local - VERSIÓN 2.0
Completamente reescrito desde cero - Compatible con la interfaz web
"""
from pathlib import Path
from typing import List, Dict, Optional
import json
import re
from datetime import datetime


class PreguntaExamen:
    """Representa una pregunta de examen"""
    
    def __init__(self, tipo: str, pregunta: str, opciones: List[str] = None, 
                 respuesta_correcta: str = "", puntos: int = 1, metadata: dict = None,
                 palabras_clave: list = None, respuesta_esperada: str = ""):
        self.tipo = tipo
        self.pregunta = pregunta
        self.opciones = opciones or []
        self.respuesta_correcta = respuesta_correcta
        self.puntos = puntos
        self.respuesta_usuario = None
        self.puntos_obtenidos = 0
        self.metadata = metadata or {}  # Para almacenar estructura compleja (reading/writing types)
        self.palabras_clave = palabras_clave or []  # Para short_answer
        self.respuesta_esperada = respuesta_esperada or respuesta_correcta  # Para short_answer
    
    def to_dict(self):
        return {
            'tipo': self.tipo,
            'pregunta': self.pregunta,
            'opciones': self.opciones,
            'respuesta_correcta': self.respuesta_correcta,
            'puntos': self.puntos,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data):
        # Aceptar tanto 'tipo' (español) como 'type' (inglés)
        tipo = data.get('tipo') or data.get('type', 'multiple')
        
        # Para flashcards con estructura anidada (data.front, solution.answer)
        if tipo == 'flashcard' and 'data' in data and 'solution' in data:
            pregunta = data['data'].get('front', '')
            respuesta_correcta = data['solution'].get('answer', '')
            explicacion = data['solution'].get('explanation', '')
            metadata = dict(data)
            
            # IMPORTANTE: Asegurar que respuesta_correcta está poblada para evaluación IA
            if not respuesta_correcta:
                respuesta_correcta = data.get('solution', {}).get('answer', '')
        else:
            # Intentar múltiples campos para la pregunta
            pregunta = (
                data.get('pregunta') or 
                data.get('question') or 
                data.get('statement') or  # Para true/false
                data.get('front') or  # Para flashcards antiguas
                data.get('text_with_gaps') or  # Para cloze
                data.get('scenario') or  # Para case_study
                data.get('prompt') or  # Para writing types
                data.get('text') or  # Para reading types
                data.get('original') or  # Para writing_paraphrase
                data.get('text_with_errors') or  # Para writing_correction
                data.get('input_sentence') or  # Para writing_transformation
                data.get('description_prompt') or  # Para writing_picture_description
                ''
            )
            
            # Para respuesta correcta, intentar varios campos
            respuesta_correcta = (
                data.get('respuesta_correcta') or 
                data.get('respuesta_esperada') or  # Para casos de estudio
                data.get('correct_answer') or 
                data.get('answer') or
                data.get('back') or  # Para flashcards antiguas
                data.get('answers') or  # Para cloze
                data.get('expected_answer') or
                data.get('expected_output') or
                data.get('correct_text') or
                data.get('correct_sentence') or
                data.get('correct_order') or
                data.get('correct_mapping')
            )
            
            explicacion = data.get('explicacion') or data.get('explanation') or ''
            metadata = dict(data)
        
        opciones = data.get('opciones') or data.get('options', [])
        
        # Para respuesta correcta, intentar varios campos
        respuesta_correcta = (
            data.get('respuesta_correcta') or 
            data.get('respuesta_esperada') or  # Para casos de estudio y short_answer
            data.get('correct_answer') or 
            data.get('answer') or 
            data.get('back') or  # Para flashcards
            data.get('answers') or  # Para cloze en inglés
            data.get('respuestas') or  # Para cloze en español
            data.get('respuesta_modelo') or  # Para open_question
            data.get('expected_answer') or  # Para open_question en inglés
            data.get('expected_output') or  # Para writing_transformation
            data.get('correct_text') or  # Para writing_correction
            data.get('correct_sentence') or  # Para writing_sentence_builder
            data.get('correct_order') or  # Para reading_sequence
            data.get('correct_mapping') or  # Para reading_matching
            ''
        )
        
        # Si respuesta_correcta es una lista, convertirla a string
        if isinstance(respuesta_correcta, list):
            respuesta_correcta = ', '.join(str(x) for x in respuesta_correcta)
        elif isinstance(respuesta_correcta, bool):
            respuesta_correcta = 'verdadero' if respuesta_correcta else 'falso'
        
        # Para caso_estudio / case_study: si no hay respuesta_correcta, construirla desde puntos_evaluacion
        if tipo in ('caso_estudio', 'case_study') and not respuesta_correcta:
            puntos_eval = data.get('puntos_evaluacion') or data.get('evaluation_criteria') or []
            if puntos_eval:
                respuesta_correcta = 'Criterios: ' + '; '.join(str(p) for p in puntos_eval)
        
        # Para open_question: si no hay respuesta_correcta, construirla desde puntos_clave
        if tipo == 'open_question' and not respuesta_correcta:
            puntos_clave = data.get('puntos_clave') or []
            if puntos_clave:
                respuesta_correcta = 'Puntos clave: ' + '; '.join(str(p) for p in puntos_clave)
        
        # Metadata: guardar todo el dict original
        metadata = dict(data)
        
        palabras_clave = data.get('palabras_clave') or []
        respuesta_esperada = data.get('respuesta_esperada') or respuesta_correcta or ''

        return cls(
            tipo=tipo,
            pregunta=pregunta,
            opciones=opciones,
            respuesta_correcta=respuesta_correcta,
            puntos=data.get('puntos', 1),
            metadata=metadata,
            palabras_clave=palabras_clave,
            respuesta_esperada=respuesta_esperada
        )


class GeneradorExamenes:
    """Generador de exámenes completamente nuevo"""
    
    def __init__(self, modelo_path: Optional[str] = None):
        self.modelo_path = modelo_path
        self.llm = None
        if modelo_path:
            self._cargar_modelo()
    
    def _cargar_modelo(self):
        """Carga el modelo LLM"""
        try:
            from llama_cpp import Llama
            print(f"🔄 Cargando: {self.modelo_path}")
            self.llm = Llama(
                model_path=self.modelo_path,
                n_ctx=8192,
                n_threads=6,
                n_gpu_layers=35,  # GPU habilitada - usa -1 para todas las capas
                verbose=False
            )
            print("✅ Modelo cargado con GPU")
        except Exception as e:
            print(f"❌ Error: {e}")
            self.llm = None
    
    def _formatear_prompt_llama(self, system_msg: str, user_msg: str) -> str:
        """Formatea el prompt usando el chat template de Llama 3.1"""
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_msg}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_msg}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
    
    @staticmethod
    def obtener_prompt_template() -> str:
        """Template simple sin emojis"""
        return """Genera preguntas de examen en JSON del material:

{contenido}

Genera {total_preguntas} preguntas:
- {num_multiple} tipo "multiple" (4 opciones A/B/C/D)
- {num_corta} tipo "corta"
- {num_desarrollo} tipo "desarrollo"

Formato JSON:
{{"preguntas":[{{"tipo":"multiple","pregunta":"?","opciones":["A)","B)","C)","D)"],"respuesta_correcta":"B","puntos":3}}]}}

JSON:"""
    
    def generar_prompt_preguntas(self, contenido: str, num_preguntas: Dict[str, int], prompt_personalizado: str = "") -> str:
        """Genera prompt optimizado para Llama 3.1"""
        cont = contenido[:7000] if len(contenido) > 7000 else contenido
        total = num_preguntas.get('multiple', 8)  # Empezar solo con múltiple
        
        system_msg = """Eres un experto en crear exámenes educativos. Generas preguntas de opción múltiple claras y precisas basadas únicamente en el contenido proporcionado. Respondes SOLO con JSON válido, sin texto adicional."""
        
        user_msg = f"""Crea {total} preguntas de opción múltiple basadas en este texto:

{cont}

REGLAS:
1. Cada pregunta debe evaluar un concepto clave del texto
2. NO inventes información
3. Las 4 opciones deben ser plausibles
4. Solo UNA opción es correcta

Responde SOLO con este JSON:
{{
  "preguntas": [
    {{
      "tipo": "multiple",
      "pregunta": "¿Texto de la pregunta?",
      "opciones": ["A) opción 1", "B) opción 2", "C) opción 3", "D) opción 4"],
      "respuesta_correcta": "A",
      "puntos": 3
    }},
    {{
      "tipo": "verdadero_falso",
      "pregunta": "Afirmación para evaluar",
      "respuesta_correcta": "verdadero",
      "puntos": 2
    }}
  ]
}}"""
        
        return self._formatear_prompt_llama(system_msg, user_msg)
    
    def generar_examen(self, contenido_documento: str, 
                      num_preguntas: Dict[str, int] = None,
                      prompt_personalizado: str = "",
                      prompt_sistema: str = None,
                      callback_progreso = None,
                      ajustes_modelo: dict = None) -> List[PreguntaExamen]:
        """NUEVO GENERADOR - Ignora prompts con emojis"""
        
        if not self.llm:
            print("⚠️ Sin modelo")
            return self._fallback_mejorado(contenido_documento, num_preguntas)
        
        if num_preguntas is None:
            num_preguntas = {'multiple': 6, 'verdadero_falso': 4, 'corta': 4, 'desarrollo': 2}
        
        if callback_progreso:
            callback_progreso(15, "Preparando...")
        
        # IGNORAR prompts con emojis o muy largos
        usar_simple = True
        if prompt_sistema:
            if len(prompt_sistema) > 1500 or '✅' in prompt_sistema or '📘' in prompt_sistema or '🚨' in prompt_sistema:
                print("⚠️ Ignorando prompt con emojis/muy largo")
            else:
                usar_simple = False
                cont = contenido_documento[:10000]
                prompt = prompt_sistema.replace('{contenido}', cont)
                prompt = prompt.replace('{num_multiple}', str(num_preguntas.get('multiple', 0)))
                prompt = prompt.replace('{num_corta}', str(num_preguntas.get('corta', 0)))
                prompt = prompt.replace('{num_desarrollo}', str(num_preguntas.get('desarrollo', 0)))
                prompt = prompt.replace('{total_preguntas}', str(sum(num_preguntas.values())))
        
        if usar_simple:
            print("📋 Prompt simple optimizado")
            prompt = self.generar_prompt_preguntas(contenido_documento, num_preguntas)
        
        print(f"📝 {sum(num_preguntas.values())} preguntas, prompt {len(prompt)} chars")
        
        if callback_progreso:
            callback_progreso(20, "Generando...")
        
        try:
            # Obtener ajustes de configuraci\u00f3n o usar valores por defecto
            if ajustes_modelo is None:
                ajustes_modelo = {}
            
            temperature = ajustes_modelo.get('temperature', 0.25)
            max_tokens = ajustes_modelo.get('max_tokens', 3000)
            top_p = ajustes_modelo.get('top_p', 0.9)
            repeat_penalty = ajustes_modelo.get('repeat_penalty', 1.15)
            
            # Obtener nombre del modelo
            modelo_nombre = Path(self.modelo_path).stem if self.modelo_path else "modelo"
            print(f"\ud83e\udd16 Llamando al modelo ({modelo_nombre})...")
            resp = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                repeat_penalty=repeat_penalty,
                stop=["<|eot_id|>", "<|end_of_text|>", "```", "\n\n\n\n"]
            )
            
            if callback_progreso:
                callback_progreso(70, "Procesando...")
            
            texto = resp['choices'][0]['text'].strip()
            
            print(f"\n{'='*60}")
            print(f"📥 RESPUESTA DEL MODELO ({len(texto)} chars):")
            print(f"{'='*60}")
            print(texto[:800] if len(texto) > 800 else texto)
            print(f"{'='*60}\n")
            
            self._log(texto, num_preguntas)
            
            if callback_progreso:
                callback_progreso(75, "Extrayendo...")
            
            pregs = self._extraer(texto, num_preguntas, contenido_documento)
            
            if callback_progreso:
                callback_progreso(90, "Validando...")
            
            # MODO HÍBRIDO: Usar preguntas del modelo y completar con fallback mejorado
            pregs_modelo = len(pregs) if pregs else 0
            total_necesario = sum(num_preguntas.values())
            
            print(f"\n📊 RESULTADO: {pregs_modelo} preguntas del modelo / {total_necesario} solicitadas")
            
            if pregs_modelo >= 1:  # Si hay al menos 1 pregunta válida del modelo
                print(f"✅ Usando {pregs_modelo} preguntas del MODELO")
                
                if pregs_modelo < total_necesario:
                    faltantes = total_necesario - pregs_modelo
                    print(f"🔧 Completando con {faltantes} preguntas del FALLBACK MEJORADO...")
                    
                    # Calcular qué tipos faltan
                    tipos_generados = {'multiple': 0, 'corta': 0, 'desarrollo': 0}
                    for p in pregs:
                        tipos_generados[p.tipo] = tipos_generados.get(p.tipo, 0) + 1
                    
                    tipos_faltantes = {}
                    for tipo, cant in num_preguntas.items():
                        falta = cant - tipos_generados.get(tipo, 0)
                        if falta > 0:
                            tipos_faltantes[tipo] = falta
                    
                    fallback_pregs = self._fallback_mejorado(contenido_documento, tipos_faltantes)
                    pregs.extend(fallback_pregs)
                    
                print(f"✅ TOTAL: {len(pregs)} preguntas ({pregs_modelo} modelo + {len(pregs)-pregs_modelo} fallback)")
                return pregs
            else:
                print(f"⚠️ Modelo no generó preguntas válidas, usando FALLBACK MEJORADO")
                return self._fallback_mejorado(contenido_documento, num_preguntas)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return self._fallback_mejorado(contenido_documento, num_preguntas)
    
    def _extraer(self, texto: str, num_preguntas: Dict[str, int], contenido: str) -> List[PreguntaExamen]:
        """Extrae preguntas incluso de JSON incompleto"""
        
        print("🔍 Buscando JSON...")
        
        if '{' not in texto or '"preguntas"' not in texto:
            print("❌ No hay JSON")
            return []
        
        inicio = texto.find('{')
        fin = texto.rfind('}') + 1
        
        if fin <= inicio:
            json_str = texto[inicio:] + ']}'
        else:
            json_str = texto[inicio:fin]
        
        print(f"📦 JSON: {len(json_str)} chars")
        
        preguntas = []
        
        # Intentar parsear completo
        try:
            datos = json.loads(json_str)
            if 'preguntas' in datos:
                for p in datos['preguntas']:
                    try:
                        preguntas.append(PreguntaExamen.from_dict(p))
                    except Exception as e:
                        print(f"⚠️ Error en pregunta: {e}")
                        continue
                print(f"✅ {len(preguntas)} parseadas")
                return preguntas
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON incompleto pos {e.pos}")
            # Intentar parcial
            preguntas = self._parcial(json_str)
            if preguntas:
                print(f"🔧 {len(preguntas)} recuperadas")
                return preguntas
        
        return []
    
    def _parcial(self, json_str: str) -> List[PreguntaExamen]:
        """Extrae preguntas de JSON incompleto con regex"""
        preguntas = []
        
        # Buscar objetos de pregunta
        patron = r'\{{\s*"tipo"\s*:\s*"(multiple|corta|desarrollo|verdadero_falso)"[^}}]*"pregunta"\s*:\s*"([^"]+)"'
        
        for match in re.finditer(patron, json_str, re.DOTALL):
            tipo = match.group(1)
            pregunta_txt = match.group(2)
            
            try:
                if tipo == 'multiple':
                    # Buscar opciones
                    inicio_obj = match.start()
                    fragmento = json_str[inicio_obj:inicio_obj+800]
                    
                    opc_patron = r'"opciones"\s*:\s*\[(.*?)\]'
                    opc_match = re.search(opc_patron, fragmento, re.DOTALL)
                    
                    opciones = None  # No usar opciones genéricas, mejor fallar y usar fallback
                    resp_correcta = 'B'
                    
                    if opc_match:
                        opc_str = opc_match.group(1)
                        opc_list = re.findall(r'"([^"]+)"', opc_str)
                        if len(opc_list) >= 4:
                            opciones = opc_list[:4]
                    
                    # Si no hay opciones válidas, descartar esta pregunta
                    if not opciones:
                        continue
                    # Buscar respuesta correcta
                    resp_patron = r'"respuesta_correcta"\s*:\s*"([^"]+)"'
                    resp_match = re.search(resp_patron, fragmento)
                    if resp_match:
                        resp_correcta = resp_match.group(1)
                    
                    preguntas.append(PreguntaExamen(
                        tipo='multiple',
                        pregunta=pregunta_txt,
                        opciones=opciones,
                        respuesta_correcta=resp_correcta,
                        puntos=3
                    ))
                elif tipo == 'verdadero_falso':
                    # Buscar respuesta correcta para verdadero/falso
                    inicio_obj = match.start()
                    fragmento = json_str[inicio_obj:inicio_obj+500]
                    
                    resp_patron = r'"respuesta_correcta"\s*:\s*"(verdadero|falso)"'
                    resp_match = re.search(resp_patron, fragmento, re.IGNORECASE)
                    resp_correcta = resp_match.group(1).lower() if resp_match else 'verdadero'
                    
                    preguntas.append(PreguntaExamen(
                        tipo='verdadero_falso',
                        pregunta=pregunta_txt,
                        respuesta_correcta=resp_correcta,
                        puntos=2
                    ))
                else:
                    preguntas.append(PreguntaExamen(
                        tipo=tipo,
                        pregunta=pregunta_txt,
                        respuesta_correcta='Criterios de evaluación basados en el material',
                        puntos=4 if tipo == 'corta' else 6
                    ))
            except Exception as e:
                print(f"⚠️ Error extrayendo: {e}")
                continue
        
        return preguntas
    
    def _log(self, respuesta: str, num_preguntas: Dict[str, int]):
        """Guarda log"""
        try:
            logs_dir = Path("logs_generacion")
            logs_dir.mkdir(exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            log = logs_dir / f"r_{ts}.txt"
            with open(log, 'w', encoding='utf-8') as f:
                f.write(f"LOG {datetime.now()}\n{'='*60}\n{respuesta}\n{'='*60}\n")
            print(f"📄 {log}")
        except:
            pass
    
    def _fallback_mejorado(self, contenido: str, num_preguntas: Dict[str, int]) -> List[PreguntaExamen]:
        """Genera preguntas MEJORADAS basadas en contenido cuando falla el modelo"""
        
        print("\n🔧 Activando FALLBACK MEJORADO...")
        
        if num_preguntas is None:
            num_preguntas = {'multiple': 6, 'verdadero_falso': 4, 'corta': 4, 'desarrollo': 2}
        
        # Extraer oraciones significativas (más largas y con contenido)
        oraciones = [s.strip() for s in re.split(r'[.!?]+', contenido) if len(s.strip()) > 50]
        
        if not oraciones:
            oraciones = ["El material contiene información importante"]
        
        # Extraer conceptos clave (palabras capitalizadas, términos técnicos, definiciones)
        conceptos_importantes = self._extraer_conceptos_clave(contenido)
        
        pregs = []
        
        # PREGUNTAS DE OPCIÓN MÚLTIPLE - Mejoradas para evitar absurdos
        pregs_generadas = 0
        for i in range(len(oraciones)):
            if pregs_generadas >= num_preguntas.get('multiple', 4):
                break
                
            oracion = oraciones[i]
            
            # Buscar si la oración contiene una definición clara
            if ' es ' in oracion.lower() or ' son ' in oracion.lower() or ' significa' in oracion.lower():
                partes = re.split(r'\s+es\s+|\s+son\s+|\s+significa\s+', oracion, maxsplit=1, flags=re.IGNORECASE)
                if len(partes) == 2:
                    concepto = partes[0].strip()
                    # Validar que el concepto sea razonable (no muy largo, no empieza con minúscula)
                    if len(concepto) > 5 and len(concepto) < 60 and not concepto[0].islower():
                        definicion = partes[1].strip()[:80]
                        
                        pregs.append(PreguntaExamen(
                            tipo='multiple',
                            pregunta=f'Según el texto, ¿qué es {concepto}?',
                            opciones=[
                                f'A) {definicion}',
                                f'B) Un concepto diferente no mencionado',
                                f'C) Una técnica alternativa',
                                f'D) Otro término relacionado'
                            ],
                            respuesta_correcta='A',
                            puntos=3
                        ))
                        pregs_generadas += 1
                        continue
            
            # Usar conceptos clave extraídos inteligentemente
            if pregs_generadas < num_preguntas.get('multiple', 4) and conceptos_importantes:
                idx_concepto = pregs_generadas % len(conceptos_importantes)
                concepto = conceptos_importantes[idx_concepto]
                
                # Buscar oraciones que mencionen este concepto
                oraciones_con_concepto = [o for o in oraciones if concepto.lower() in o.lower()]
                if oraciones_con_concepto:
                    oracion_relevante = oraciones_con_concepto[0][:100]
                    
                    pregs.append(PreguntaExamen(
                        tipo='multiple',
                        pregunta=f'¿Qué se menciona en el texto sobre {concepto}?',
                        opciones=[
                            f'A) {oracion_relevante}',
                            f'B) Información que no aparece en el texto',
                            f'C) Un concepto completamente diferente',
                            f'D) Una definición no relacionada'
                        ],
                        respuesta_correcta='A',
                        puntos=3
                    ))
                    pregs_generadas += 1
        
        # PREGUNTAS DE VERDADERO/FALSO - Basadas en afirmaciones del texto
        vf_plantillas_verdaderas = [
            'Según el texto, {}',
            'El material indica que {}',
            'Se menciona que {}',
            'El texto afirma que {}'
        ]
        
        vf_plantillas_falsas = [
            'El texto indica que {} (información incorrecta)',
            'Según el material, {} (afirmación falsa)',
            'Se menciona que {} (dato erróneo)'
        ]
        
        for i in range(num_preguntas.get('verdadero_falso', 4)):
            if i < len(oraciones):
                oracion = oraciones[i]
                # Alternar entre verdadero y falso
                es_verdadero = (i % 2 == 0)
                
                if es_verdadero:
                    # Usar afirmación del texto (verdadera)
                    plantilla_idx = i % len(vf_plantillas_verdaderas)
                    plantilla = vf_plantillas_verdaderas[plantilla_idx]
                    afirmacion = oracion.strip()[:120]  # Limitar longitud
                    
                    pregs.append(PreguntaExamen(
                        tipo='verdadero_falso',
                        pregunta=plantilla.format(afirmacion),
                        respuesta_correcta='verdadero',
                        puntos=2
                    ))
                else:
                    # Crear afirmación falsa modificando el texto
                    plantilla_idx = i % len(vf_plantillas_falsas)
                    plantilla = vf_plantillas_falsas[plantilla_idx]
                    # Tomar una parte del texto pero marcarla como incorrecta
                    afirmacion = oracion.strip()[:100]
                    
                    pregs.append(PreguntaExamen(
                        tipo='verdadero_falso',
                        pregunta=plantilla.format(afirmacion),
                        respuesta_correcta='falso',
                        puntos=2
                    ))
        
        # PREGUNTAS DE RESPUESTA CORTA - Basadas en secciones del contenido
        corta_plantillas = [
            'Explica brevemente qué se menciona en el material sobre: {}',
            'Describe con tus propias palabras: {}',
            '¿Qué información proporciona el material acerca de {}?',
            'Resume la información sobre: {}',
            'Define según el material: {}'
        ]
        
        for i in range(num_preguntas.get('corta', 2)):
            idx = i + num_preguntas.get('multiple', 0)
            if idx < len(oraciones):
                plantilla_idx = i % len(corta_plantillas)
                plantilla = corta_plantillas[plantilla_idx]
                
                # Extraer el tema principal de la oración
                oracion = oraciones[idx]
                # Buscar sustantivos/conceptos clave (primeras palabras significativas)
                palabras = [p for p in oracion.split() if len(p) > 4]
                tema = ' '.join(palabras[:5]) if len(palabras) >= 5 else oracion[:60]
                
                pregs.append(PreguntaExamen(
                    tipo='corta',
                    pregunta=plantilla.format(tema),
                    respuesta_correcta=f'Debe explicar basándose en: "{oracion[:150]}..."',
                    puntos=4
                ))
        
        # PREGUNTAS DE DESARROLLO - Basadas en temas del contenido
        # Identificar temas principales (primeras oraciones de cada párrafo o sección)
        parrafos = [p.strip() for p in contenido.split('\n\n') if len(p.strip()) > 100]
        temas_principales = []
        
        for parrafo in parrafos[:5]:  # Máximo 5 temas
            primera_oracion = re.split(r'[.!?]+', parrafo)[0].strip()
            if len(primera_oracion) > 30:
                # Extraer el tema (primeras palabras clave)
                palabras = [p for p in primera_oracion.split() if len(p) > 4]
                tema = ' '.join(palabras[:6]) if len(palabras) >= 6 else primera_oracion[:80]
                temas_principales.append(tema)
        
        desarrollo_plantillas = [
            ('Desarrolla una explicación completa sobre {}', 'Debe explicar el concepto en profundidad, proporcionar ejemplos y conectar con otros temas del material'),
            ('Analiza detalladamente la información presentada sobre: {}', 'Debe analizar críticamente, identificar puntos clave y fundamentar con el material'),
            ('Explica de forma extendida {}', 'Debe mostrar comprensión profunda, relacionar conceptos y ejemplificar'),
            ('Elabora una respuesta comprehensiva sobre {}', 'Debe sintetizar información, organizar ideas coherentemente y argumentar'),
            ('Desarrolla un análisis del siguiente aspecto: {}', 'Debe explicar, analizar y relacionar con el contexto del material')
        ]
        
        for i in range(num_preguntas.get('desarrollo', 1)):
            plantilla_idx = i % len(desarrollo_plantillas)
            pregunta_base, respuesta_base = desarrollo_plantillas[plantilla_idx]
            
            # Usar temas principales si están disponibles
            if i < len(temas_principales):
                tema = temas_principales[i]
                pregunta_txt = pregunta_base.format(tema)
            elif i < len(conceptos_importantes):
                pregunta_txt = pregunta_base.format(conceptos_importantes[i])
            else:
                pregunta_txt = 'Desarrolla un análisis comprensivo de los conceptos principales presentados en el material'
            
            pregs.append(PreguntaExamen(
                tipo='desarrollo',
                pregunta=pregunta_txt,
                respuesta_correcta=respuesta_base,
                puntos=6
            ))
        
        print(f"✅ {len(pregs)} preguntas inteligentes generadas")
        return pregs
    
    def _extraer_conceptos_clave(self, contenido: str) -> List[str]:
        """Extrae conceptos clave del contenido evitando muletillas y palabras vacías"""
        conceptos = []
        
        # Lista expandida de palabras a evitar (muletillas, conectores, etc.)
        palabras_excluir = {
            'El', 'La', 'Los', 'Las', 'Un', 'Una', 'Este', 'Esta', 'Estos', 'Estas',
            'Que', 'Como', 'Para', 'Por', 'Con', 'Sin', 'Sobre', 'Entre', 'Desde',
            'Hacia', 'Hasta', 'Según', 'Durante', 'Mediante', 'También', 'Además',
            'Supongo', 'Creo', 'Pienso', 'Quizás', 'Tal', 'Vez', 'Siempre', 'Nunca',
            'Muchas', 'Veces', 'Algunos', 'Varios', 'Ciertos', 'Todas', 'Todos',
            'Cualquier', 'Otro', 'Otra', 'Misma', 'Mismo', 'Primera', 'Segundo',
            'Comúnmente', 'Generalmente', 'Usualmente', 'Normalmente'
        }
        
        # Buscar términos técnicos (mayúsculas, números, guiones)
        terminos_tecnicos = re.findall(r'\b[A-Z]{2,}[a-z0-9]*\b|\b[a-z]+-[a-z]+\b', contenido)
        if terminos_tecnicos:
            conceptos.extend([t for t in terminos_tecnicos if len(t) > 2][:5])
        
        # Buscar términos entre comillas (conceptos destacados)
        terminos_comillas = re.findall(r'"([^"]+)"', contenido)
        if terminos_comillas:
            conceptos.extend([t for t in terminos_comillas if len(t) > 3 and t not in palabras_excluir][:5])
        
        # Buscar palabras capitalizadas pero filtrar muletillas
        palabras_capitalizadas = re.findall(r'\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{3,}\b', contenido)
        if palabras_capitalizadas:
            conceptos.extend([p for p in palabras_capitalizadas if p not in palabras_excluir][:5])
        
        # Buscar definiciones explícitas ("X es Y", "X significa Y")
        definiciones = re.findall(r'\b([A-Za-záéíóúñÁÉÍÓÚÑ]{4,})\s+(?:es|son|significa|representa|define)\b', contenido)
        if definiciones:
            conceptos.extend([d for d in definiciones if d not in palabras_excluir][:5])
        
        # Eliminar duplicados manteniendo orden
        conceptos_unicos = []
        for c in conceptos:
            c_limpio = c.strip()
            if c_limpio and len(c_limpio) > 3 and c_limpio not in conceptos_unicos and c_limpio not in palabras_excluir:
                conceptos_unicos.append(c_limpio)
        
        return conceptos_unicos[:12]
    
    def evaluar_respuesta(self, pregunta: PreguntaExamen, respuesta_usuario: str) -> tuple[int, str]:
        """Evalúa respuesta"""
        if pregunta.tipo == 'multiple':
            r = respuesta_usuario.strip().upper()
            c = pregunta.respuesta_correcta.strip().upper()
            if r == c or r == c[0]:
                return pregunta.puntos, "¡Correcto!"
            return 0, f"Incorrecto. Correcta: {pregunta.respuesta_correcta}"
        
        if not respuesta_usuario or len(respuesta_usuario.strip()) < 10:
            return 0, "❌ Insuficiente"
        
        pals = len(respuesta_usuario.split())
        
        if pregunta.tipo == 'corta':
            if pals < 15:
                return pregunta.puntos // 3, "⚠️ Muy breve"
            elif pals < 40:
                return int(pregunta.puntos * 0.7), "✓ Aceptable"
            return pregunta.puntos, "✅ Completa"
        
        if pregunta.tipo == 'desarrollo':
            if pals < 60:
                return int(pregunta.puntos * 0.4), "⚠️ Insuficiente"
            elif pals < 120:
                return int(pregunta.puntos * 0.7), "✓ Aceptable"
            return pregunta.puntos, "✅ Completo"
        
        return 0, "No soportado"


def guardar_examen(preguntas: List[PreguntaExamen], ruta: Path):
    """Guarda examen"""
    datos = {
        'fecha_creacion': datetime.now().isoformat(),
        'preguntas': [p.to_dict() for p in preguntas]
    }
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def cargar_examen(ruta: Path) -> List[PreguntaExamen]:
    """Carga examen"""
    with open(ruta, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    return [PreguntaExamen.from_dict(p) for p in datos['preguntas']]


if __name__ == "__main__":
    print("Generador v2.0 - Reescrito desde cero")
