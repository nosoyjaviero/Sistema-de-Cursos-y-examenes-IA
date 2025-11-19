"""
Generador de exámenes en DOS PASOS
Paso 1: Generar preguntas en lenguaje natural (sin formato)
Paso 2: Formatear preguntas al JSON requerido
"""

from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
from llama_cpp import Llama
import json
import re
from datetime import datetime


@dataclass
class PreguntaExamen:
    tipo: str
    pregunta: str
    opciones: List[str] = None
    respuesta_correcta: str = None
    puntos: int = 3
    explicacion: str = ""
    metadata: dict = None  # Para almacenar estructura compleja (reading/writing types)

    def to_dict(self):
        data = {
            'tipo': self.tipo,
            'pregunta': self.pregunta,
            'puntos': self.puntos
        }
        if self.opciones:
            data['opciones'] = self.opciones
        if self.respuesta_correcta:
            data['respuesta_correcta'] = self.respuesta_correcta
        if self.explicacion:
            data['explicacion'] = self.explicacion
        return data
    
    @classmethod
    def from_dict(cls, data: dict):
        """Crea una instancia de PreguntaExamen desde un diccionario
        Acepta campos en español e inglés"""
        # Aceptar tanto 'tipo' (español) como 'type' (inglés)
        tipo = data.get('tipo') or data.get('type', 'multiple')
        
        # Para flashcards con estructura anidada (data.front, solution.answer)
        if tipo == 'flashcard' and 'data' in data and 'solution' in data:
            pregunta = data['data'].get('front', '')
            respuesta_correcta = data['solution'].get('answer', '')
            explicacion = data['solution'].get('explanation', '')
            # Guardar metadata completa para evaluación posterior
            metadata = dict(data)
        else:
            # Aceptar tanto 'pregunta' como 'question', 'statement', 'front', 'text_with_gaps', 'prompt'
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
            
            # Respuesta correcta - intentar múltiples campos
            respuesta_correcta = (
                data.get('respuesta_correcta') or 
                data.get('correct_answer') or 
                data.get('answer') or
                data.get('back') or  # Para flashcards antiguas
                data.get('answers') or  # Para cloze (puede ser array)
                data.get('expected_answer') or  # Para open_question
                data.get('expected_output') or  # Para writing_transformation
                data.get('correct_text') or  # Para writing_correction
                data.get('correct_sentence') or  # Para writing_sentence_builder
                data.get('correct_order') or  # Para reading_sequence
                data.get('correct_mapping')  # Para reading_matching
            )
            
            # Explicación
            explicacion = (
                data.get('explicacion') or 
                data.get('explanation') or 
                data.get('hint') or  # Para cloze
                ''
            )
            
            # Metadata: guardar todo el dict original para tipos complejos
            metadata = dict(data)  # Copia completa del dict original
        
        # Opciones
        opciones = data.get('opciones') or data.get('options')
        
        return cls(
            tipo=tipo,
            pregunta=pregunta,
            opciones=opciones,
            respuesta_correcta=respuesta_correcta,
            puntos=data.get('puntos', 3),
            explicacion=explicacion,
            metadata=metadata
        )


class GeneradorDosPasos:
    def __init__(self, modelo_path: str, n_gpu_layers: int = 35):
        self.modelo_path = modelo_path
        self.n_gpu_layers = n_gpu_layers
        self.llm = None
        self.log_dir = Path("logs_generacion_dos_pasos")
        self.log_dir.mkdir(exist_ok=True)
        self._cargar_modelo()
    
    def _cargar_modelo(self):
        """Carga el modelo LLM"""
        try:
            print(f"📦 Cargando modelo: {self.modelo_path}")
            print(f"⚙️  Configuración GPU: {self.n_gpu_layers} capas")
            
            # Verificar si CUDA está disponible
            try:
                import llama_cpp
                print(f"📚 llama-cpp-python versión: {llama_cpp.__version__}")
                
                # Intentar cargar con GPU
                self.llm = Llama(
                    model_path=self.modelo_path,
                    n_ctx=8192,
                    n_threads=6,
                    n_gpu_layers=self.n_gpu_layers,
                    verbose=True  # Activar verbose para ver mensajes de GPU
                )
                
                # Verificar metadata del modelo cargado
                if hasattr(self.llm, 'metadata'):
                    print(f"📊 Metadata del modelo: {self.llm.metadata}")
                
                gpu_info = f"{'Todas' if self.n_gpu_layers == -1 else self.n_gpu_layers} capas"
                print(f"✅ Modelo cargado")
                print(f"   GPU Capas solicitadas: {gpu_info}")
                
                # Intentar obtener información de CUDA
                try:
                    import torch
                    if torch.cuda.is_available():
                        print(f"   ✅ CUDA disponible: {torch.cuda.get_device_name(0)}")
                        print(f"   📊 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
                    else:
                        print(f"   ⚠️  CUDA no disponible - Usando CPU")
                except ImportError:
                    print(f"   ℹ️  PyTorch no instalado, no se puede verificar CUDA")
                
            except Exception as e_gpu:
                print(f"⚠️  Error verificando GPU: {e_gpu}")
                # Intentar cargar solo con CPU
                print(f"🔄 Intentando cargar solo con CPU...")
                self.llm = Llama(
                    model_path=self.modelo_path,
                    n_ctx=8192,
                    n_threads=6,
                    n_gpu_layers=0,
                    verbose=False
                )
                print(f"✅ Modelo cargado (solo CPU)")
                
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            self.llm = None
    
    def _formatear_prompt_llama(self, system_msg: str, user_msg: str) -> str:
        """Formatea el prompt usando el chat template de Llama 3.1"""
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_msg}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_msg}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
    
    def _crear_log_archivo(self, session_id: str = None) -> Path:
        """Crea un archivo de log único para esta sesión"""
        if session_id:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = self.log_dir / f"generacion_{session_id}_{timestamp}.log"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = self.log_dir / f"generacion_{timestamp}.log"
        return log_file
    
    def _escribir_log(self, log_file: Path, contenido: str):
        """Escribe contenido al archivo de log"""
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(contenido + "\n")
    
    def paso1_generar_preguntas_naturales(self, contenido: str, num_preguntas: Dict[str, int],
                                          ajustes_modelo: dict = None, archivos: list = None,
                                          log_file: Path = None, sin_prompt_sistema: bool = False) -> str:
        """
        PASO 1: Genera preguntas en lenguaje natural, sin formato JSON.
        El modelo se enfoca solo en hacer buenas preguntas.
        """
        if not self.llm:
            print("❌ No hay modelo cargado")
            if log_file:
                self._escribir_log(log_file, "❌ ERROR: No hay modelo cargado")
            return ""
        
        # Preparar ajustes
        if ajustes_modelo is None:
            ajustes_modelo = {}
        
        temperature = ajustes_modelo.get('temperature', 0.7)
        max_tokens = ajustes_modelo.get('max_tokens', 2000)
        top_p = ajustes_modelo.get('top_p', 0.9)
        repeat_penalty = ajustes_modelo.get('repeat_penalty', 1.15)
        
        # Limitar contenido
        contenido_limitado = contenido[:6000] if len(contenido) > 6000 else contenido
        
        # Calcular totales
        total_multiple = num_preguntas.get('multiple', 0)
        total_vf = num_preguntas.get('verdadero_falso', 0)
        total_corta = num_preguntas.get('corta', 0)
        total_desarrollo = num_preguntas.get('desarrollo', 0)
        
        system_msg = """Eres un profesor experto que crea exámenes educativos de alta calidad."""
        
        total_preguntas_texto = []
        if total_multiple > 0:
            total_preguntas_texto.append(f"{total_multiple} opción múltiple")
        if total_vf > 0:
            total_preguntas_texto.append(f"{total_vf} verdadero/falso")
        if total_corta > 0:
            total_preguntas_texto.append(f"{total_corta} respuesta corta")
        if total_desarrollo > 0:
            total_preguntas_texto.append(f"{total_desarrollo} desarrollo")
        
        total_texto = ", ".join(total_preguntas_texto)
        total_numero = sum([total_multiple, total_vf, total_corta, total_desarrollo])
        
        # Si sin_prompt_sistema=True, el usuario controla TODO el prompt
        if sin_prompt_sistema:
            # Usar el contenido directamente, ya incluye el prompt del usuario
            user_msg = contenido_limitado
            print(f"🎯 MODO PROMPT PERSONALIZADO: Usando prompt del usuario directamente")
        else:
            user_msg = f"""Crea {total_numero} preguntas de examen ({total_texto}) sobre este contenido:

{contenido_limitado}

GENERA EXACTAMENTE {total_numero} PREGUNTAS EN TOTAL.

FORMATO (usa números 1, 2, 3, etc para cada pregunta):
"""
        
        # Solo agregar formato si NO es prompt personalizado
        if not sin_prompt_sistema and total_multiple > 0:
            user_msg += f"""
OPCIÓN MÚLTIPLE (primeras {total_multiple} preguntas):
1. [Pregunta sobre el tema]
   A) Primera opción
   B) Segunda opción
   C) Tercera opción
   D) Cuarta opción
   Respuesta correcta: [A/B/C/D]

"""
        
        if not sin_prompt_sistema and total_vf > 0:
            user_msg += f"""
VERDADERO/FALSO (siguientes {total_vf} preguntas):
{total_multiple + 1}. [Afirmación sobre el tema]
   Respuesta: [Verdadero/Falso]

"""
        
        if not sin_prompt_sistema and total_corta > 0:
            inicio = total_multiple + total_vf + 1
            user_msg += f"""
RESPUESTA CORTA (siguientes {total_corta} preguntas):
{inicio}. [Pregunta que requiere respuesta breve]
   Respuesta esperada: [1-3 oraciones]

"""
        
        if not sin_prompt_sistema and total_desarrollo > 0:
            inicio = total_multiple + total_vf + total_corta + 1
            user_msg += f"""
DESARROLLO (últimas {total_desarrollo} preguntas):
{inicio}. [Pregunta que requiere análisis]
   Puntos clave: [Lo que debe incluir la respuesta]

"""
        
        if not sin_prompt_sistema:
            user_msg += f"""
IMPORTANTE:
- Genera TODAS las {total_numero} preguntas
- Numera cada pregunta consecutivamente (1, 2, 3...)
- Basa TODO en el contenido proporcionado
- NO inventes información"""
        
        prompt = self._formatear_prompt_llama(system_msg, user_msg)
        
        # Logging inicial
        if log_file:
            self._escribir_log(log_file, "="*80)
            self._escribir_log(log_file, f"📝 PASO 1: GENERACIÓN DE PREGUNTAS NATURALES")
            self._escribir_log(log_file, f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self._escribir_log(log_file, "="*80)
            
            if archivos:
                self._escribir_log(log_file, f"\n📚 ARCHIVOS CARGADOS ({len(archivos)}):")
                for i, archivo in enumerate(archivos, 1):
                    self._escribir_log(log_file, f"   {i}. {archivo}")
            
            self._escribir_log(log_file, f"\n⚙️ CONFIGURACIÓN DEL MODELO:")
            self._escribir_log(log_file, f"   • Temperatura: {temperature}")
            self._escribir_log(log_file, f"   • Max tokens: {max_tokens}")
            self._escribir_log(log_file, f"   • Top P: {top_p}")
            self._escribir_log(log_file, f"   • Repeat Penalty: {repeat_penalty}")
            
            self._escribir_log(log_file, f"\n📊 PREGUNTAS SOLICITADAS:")
            for tipo, cantidad in num_preguntas.items():
                if cantidad > 0:
                    self._escribir_log(log_file, f"   • {tipo}: {cantidad}")
            
            self._escribir_log(log_file, f"\n📄 CONTENIDO ({len(contenido)} caracteres):")
            self._escribir_log(log_file, f"{contenido[:500]}...")
            self._escribir_log(log_file, "\n" + "-"*80 + "\n")
        
        print(f"📝 PASO 1: Generando preguntas en lenguaje natural...")
        print(f"   Temperatura: {temperature}, Max tokens: {max_tokens}")
        
        respuesta = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            repeat_penalty=repeat_penalty,
            stop=["<|eot_id|>", "<|end_of_text|>"]
        )
        
        texto_preguntas = respuesta['choices'][0]['text'].strip()
        
        print(f"✅ PASO 1 completado: {len(texto_preguntas)} caracteres generados")
        print(f"\n{'='*60}")
        print("📋 PREGUNTAS GENERADAS (primeros 500 caracteres):")
        print(f"{'='*60}")
        print(texto_preguntas[:500])
        print(f"{'='*60}\n")
        
        # Guardar resultado del paso 1 en log
        if log_file:
            self._escribir_log(log_file, f"✅ PASO 1 COMPLETADO")
            self._escribir_log(log_file, f"Caracteres generados: {len(texto_preguntas)}")
            self._escribir_log(log_file, f"\n{'='*80}")
            self._escribir_log(log_file, f"📋 PREGUNTAS GENERADAS COMPLETAS:")
            self._escribir_log(log_file, f"{'='*80}")
            self._escribir_log(log_file, texto_preguntas)
            self._escribir_log(log_file, f"{'='*80}\n")
        
        return texto_preguntas
    
    def paso2_formatear_a_json(self, texto_preguntas: str, num_preguntas: Dict[str, int],
                               ajustes_modelo: dict = None, log_file: Path = None) -> str:
        """
        PASO 2: Toma las preguntas en lenguaje natural y las formatea al JSON requerido.
        """
        if not self.llm:
            print("❌ No hay modelo cargado")
            if log_file:
                self._escribir_log(log_file, "❌ ERROR PASO 2: No hay modelo cargado")
            return ""
        
        # Preparar ajustes
        if ajustes_modelo is None:
            ajustes_modelo = {}
        
        temperature = 0.1  # Temperatura BAJA para formato preciso
        max_tokens = ajustes_modelo.get('max_tokens', 2000)
        
        system_msg = """Eres un conversor de texto a JSON. Responde únicamente con el objeto JSON, sin marcadores de código ni explicaciones."""
        
        user_msg = f"""Convierte estas preguntas a JSON válido:

{texto_preguntas}

Formato esperado:
{{
  "preguntas": [
    {{"tipo": "multiple", "pregunta": "...", "opciones": ["A) ...", "B) ...", "C) ...", "D) ..."], "respuesta_correcta": "A", "puntos": 3}},
    {{"tipo": "verdadero_falso", "pregunta": "...", "respuesta_correcta": "verdadero", "puntos": 2}},
    {{"tipo": "corta", "pregunta": "...", "respuesta_correcta": "...", "puntos": 4}},
    {{"tipo": "desarrollo", "pregunta": "...", "respuesta_correcta": "...", "puntos": 5}}
  ]
}}

Reglas:
- Convierte TODAS las preguntas
- respuesta_correcta en múltiple: solo letra (A, B, C, D)
- verdadero/falso: usa "verdadero" o "falso"
- NO uses marcadores ```json o ```
- Responde SOLO el JSON puro, comenzando con {{"""
        
        prompt = self._formatear_prompt_llama(system_msg, user_msg)
        
        if log_file:
            self._escribir_log(log_file, "\n" + "="*80)
            self._escribir_log(log_file, "📝 PASO 2: FORMATEO A JSON")
            self._escribir_log(log_file, "="*80)
            self._escribir_log(log_file, f"Temperatura: {temperature} (baja para precisión)")
            self._escribir_log(log_file, f"Max tokens: {max_tokens}\n")
        
        print(f"📝 PASO 2: Formateando preguntas a JSON...")
        
        respuesta = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            repeat_penalty=1.0,
            stop=["<|eot_id|>", "<|end_of_text|>"]
        )
        
        json_texto = respuesta['choices'][0]['text'].strip()
        
        print(f"✅ PASO 2 completado")
        print(f"\n{'='*60}")
        print("📋 JSON GENERADO (primeros 500 caracteres):")
        print(f"{'='*60}")
        print(json_texto[:500])
        print(f"{'='*60}\n")
        
        if log_file:
            self._escribir_log(log_file, f"✅ PASO 2 COMPLETADO")
            self._escribir_log(log_file, f"\n{'='*80}")
            self._escribir_log(log_file, f"📋 JSON COMPLETO GENERADO:")
            self._escribir_log(log_file, f"{'='*80}")
            self._escribir_log(log_file, json_texto)
            self._escribir_log(log_file, f"{'='*80}\n")
        
        return json_texto
    
    def _extraer_preguntas_del_json(self, json_texto: str, num_preguntas: Dict[str, int],
                                     log_file: Path = None) -> List[PreguntaExamen]:
        """Extrae las preguntas del JSON generado"""
        preguntas = []
        
        if log_file:
            self._escribir_log(log_file, "\n" + "="*80)
            self._escribir_log(log_file, "🔍 EXTRACCIÓN Y VALIDACIÓN DE PREGUNTAS")
            self._escribir_log(log_file, "="*80)
        
        try:
            # Limpiar marcadores de código markdown
            json_limpio = json_texto.replace('```json', '').replace('```', '').strip()
            
            # Buscar el JSON entre llaves
            json_inicio = json_limpio.find('{')
            json_fin = json_limpio.rfind('}') + 1
            
            if json_inicio >= 0 and json_fin > json_inicio:
                json_limpio = json_limpio[json_inicio:json_fin]
                datos = json.loads(json_limpio)
                
                for p in datos.get('preguntas', []):
                    tipo = p.get('tipo', '')
                    pregunta_texto = p.get('pregunta', '')
                    
                    if not pregunta_texto:
                        continue
                    
                    pregunta_obj = PreguntaExamen(
                        tipo=tipo,
                        pregunta=pregunta_texto,
                        puntos=p.get('puntos', 3)
                    )
                    
                    if tipo == 'multiple':
                        opciones = p.get('opciones', [])
                        if opciones and len(opciones) >= 4:
                            pregunta_obj.opciones = opciones[:4]
                            pregunta_obj.respuesta_correcta = p.get('respuesta_correcta', 'A')
                            preguntas.append(pregunta_obj)
                    
                    elif tipo == 'verdadero_falso':
                        respuesta = p.get('respuesta_correcta', '').lower()
                        if respuesta in ['verdadero', 'falso']:
                            pregunta_obj.respuesta_correcta = respuesta
                            preguntas.append(pregunta_obj)
                    
                    elif tipo in ['corta', 'desarrollo']:
                        pregunta_obj.respuesta_correcta = p.get('respuesta_correcta', '')
                        preguntas.append(pregunta_obj)
                
                print(f"✅ Extraídas {len(preguntas)} preguntas válidas del JSON")
                
                if log_file:
                    self._escribir_log(log_file, f"\n✅ PREGUNTAS EXTRAÍDAS: {len(preguntas)}")
                    self._escribir_log(log_file, "\n📝 DETALLE DE PREGUNTAS:\n")
                    for i, p in enumerate(preguntas, 1):
                        self._escribir_log(log_file, f"\n--- Pregunta {i} ---")
                        self._escribir_log(log_file, f"Tipo: {p.tipo}")
                        self._escribir_log(log_file, f"Pregunta: {p.pregunta}")
                        if p.opciones:
                            self._escribir_log(log_file, f"Opciones: {', '.join(p.opciones)}")
                        self._escribir_log(log_file, f"Respuesta: {p.respuesta_correcta}")
                        self._escribir_log(log_file, f"Puntos: {p.puntos}")
        
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando JSON: {e}")
            print(f"Texto recibido: {json_texto[:200]}")
            if log_file:
                self._escribir_log(log_file, f"\n❌ ERROR parseando JSON: {e}")
                self._escribir_log(log_file, f"Texto problemático: {json_texto[:500]}")
                self._escribir_log(log_file, "\n⚠️ Intentando parsear manualmente...")
            
            # FALLBACK: Intentar extraer preguntas del texto original si JSON falla
            preguntas = self._parsear_manual(json_texto, num_preguntas, log_file)
            
        except Exception as e:
            print(f"❌ Error extrayendo preguntas: {e}")
            if log_file:
                self._escribir_log(log_file, f"\n❌ ERROR extrayendo preguntas: {e}")
        
        # FILTRAR PREGUNTAS POR TIPO Y CANTIDAD SOLICITADA
        preguntas_filtradas = []
        contador_por_tipo = {}
        
        # Mapeo de tipos nuevos a tipos del sistema
        mapeo_tipos = {
            'flashcard': 'flashcard',
            'mcq': 'mcq', 
            'true_false': 'true_false',
            'verdadero_falso': 'true_false',  # Compatibilidad
            'cloze': 'cloze',
            'short_answer': 'short_answer',
            'respuesta_corta': 'short_answer',  # Compatibilidad
            'open_question': 'open_question',
            'desarrollo': 'open_question',  # Compatibilidad
            'case_study': 'case_study',
            'caso_estudio': 'case_study',  # Compatibilidad
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
            # Tipos antiguos
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
        
        if log_file:
            self._escribir_log(log_file, f"\n🔍 FILTRADO DE PREGUNTAS:")
            self._escribir_log(log_file, f"   Solicitadas: {num_preguntas}")
            self._escribir_log(log_file, f"   Generadas: {len(preguntas)}")
            self._escribir_log(log_file, f"   Filtradas: {len(preguntas_filtradas)}")
            self._escribir_log(log_file, f"   Por tipo: {contador_por_tipo}")
        
        print(f"🔍 Filtrado: {len(preguntas)} generadas → {len(preguntas_filtradas)} solicitadas")
        print(f"   Por tipo: {contador_por_tipo}")
        
        return preguntas_filtradas
    
    def _parsear_manual(self, texto: str, num_preguntas: Dict[str, int], log_file: Path = None) -> List[PreguntaExamen]:
        """Fallback: parsea el texto manualmente si el JSON falla"""
        preguntas = []
        
        if log_file:
            self._escribir_log(log_file, "🔧 Parseando texto manualmente...")
        
        print("🔧 Parseando texto manualmente...")
        
        # Limpiar marcadores de código
        texto = texto.replace('```json', '').replace('```', '').strip()
        
        # Intentar encontrar array de preguntas
        try:
            # Buscar patrón "preguntas": [
            inicio_array = texto.find('"preguntas"')
            if inicio_array > 0:
                # Buscar el inicio del array
                inicio_corchete = texto.find('[', inicio_array)
                if inicio_corchete > 0:
                    # Encontrar todas las preguntas individuales
                    texto_preguntas = texto[inicio_corchete:]
                    
                    # Buscar objetos de pregunta usando regex
                    patron_pregunta = r'\{[^{}]*?"tipo"[^{}]*?"pregunta"[^{}]*?\}'
                    matches = re.finditer(patron_pregunta, texto_preguntas, re.DOTALL)
                    
                    for match in matches:
                        try:
                            # Intentar parsear cada pregunta individual
                            pregunta_json = match.group(0)
                            # Arreglar JSON incompleto agregando llaves faltantes
                            if pregunta_json.count('{') > pregunta_json.count('}'):
                                pregunta_json += '}'
                            
                            pregunta_data = json.loads(pregunta_json)
                            
                            tipo = pregunta_data.get('tipo', '')
                            pregunta_texto = pregunta_data.get('pregunta', '')
                            
                            if not pregunta_texto:
                                continue
                            
                            pregunta_obj = PreguntaExamen(
                                tipo=tipo,
                                pregunta=pregunta_texto,
                                puntos=pregunta_data.get('puntos', 3)
                            )
                            
                            if tipo == 'multiple':
                                opciones = pregunta_data.get('opciones', [])
                                if opciones and len(opciones) >= 4:
                                    pregunta_obj.opciones = opciones[:4]
                                    pregunta_obj.respuesta_correcta = pregunta_data.get('respuesta_correcta', 'A')
                                    preguntas.append(pregunta_obj)
                            
                            elif tipo == 'verdadero_falso':
                                respuesta = pregunta_data.get('respuesta_correcta', '').lower()
                                if respuesta in ['verdadero', 'falso']:
                                    pregunta_obj.respuesta_correcta = respuesta
                                    preguntas.append(pregunta_obj)
                            
                            elif tipo in ['corta', 'desarrollo']:
                                pregunta_obj.respuesta_correcta = pregunta_data.get('respuesta_correcta', '')
                                preguntas.append(pregunta_obj)
                        
                        except json.JSONDecodeError:
                            continue  # Saltar preguntas mal formadas
        
        except Exception as e:
            print(f"⚠️ Error en parseo por regex: {e}")
        
        # Si no encontramos preguntas con regex, usar el método anterior línea por línea
        if len(preguntas) == 0:
            print("🔧 Intentando parseo línea por línea...")
            preguntas = self._parsear_linea_por_linea(texto, num_preguntas, log_file)
        
        if log_file:
            self._escribir_log(log_file, f"✅ Parseadas manualmente: {len(preguntas)} preguntas")
        
        print(f"✅ Parseadas manualmente: {len(preguntas)} preguntas")
        return preguntas
    
    def _parsear_linea_por_linea(self, texto: str, num_preguntas: Dict[str, int], log_file: Path = None) -> List[PreguntaExamen]:
        """Parsea el texto línea por línea buscando patrones"""
        preguntas = []
        
        if log_file:
            self._escribir_log(log_file, "🔧 Parseando texto manualmente...")
        
        # Buscar patrones de preguntas
        lineas = texto.split('\n')
        pregunta_actual = None
        opciones_actuales = []
        respuesta_actual = None
        tipo_actual = None
        
        for linea in lineas:
            linea = linea.strip()
            if not linea:
                continue
            
            # Detectar nueva pregunta (número seguido de punto o paréntesis)
            if re.match(r'^\d+[\.\)]\s+', linea):
                # Guardar pregunta anterior si existe
                if pregunta_actual:
                    if tipo_actual == 'multiple' and len(opciones_actuales) >= 4:
                        preguntas.append(PreguntaExamen(
                            tipo='multiple',
                            pregunta=pregunta_actual,
                            opciones=opciones_actuales[:4],
                            respuesta_correcta=respuesta_actual or 'A',
                            puntos=3
                        ))
                    elif tipo_actual == 'verdadero_falso':
                        preguntas.append(PreguntaExamen(
                            tipo='verdadero_falso',
                            pregunta=pregunta_actual,
                            respuesta_correcta=respuesta_actual or 'verdadero',
                            puntos=2
                        ))
                    elif tipo_actual in ['corta', 'desarrollo']:
                        preguntas.append(PreguntaExamen(
                            tipo=tipo_actual,
                            pregunta=pregunta_actual,
                            respuesta_correcta=respuesta_actual or '',
                            puntos=4 if tipo_actual == 'corta' else 5
                        ))
                
                # Nueva pregunta
                pregunta_actual = re.sub(r'^\d+[\.\)]\s+', '', linea)
                opciones_actuales = []
                respuesta_actual = None
                
                # Determinar tipo basándose en la cantidad solicitada
                num_actual = len(preguntas)
                if num_actual < num_preguntas.get('multiple', 0):
                    tipo_actual = 'multiple'
                elif num_actual < num_preguntas.get('multiple', 0) + num_preguntas.get('verdadero_falso', 0):
                    tipo_actual = 'verdadero_falso'
                elif num_actual < num_preguntas.get('multiple', 0) + num_preguntas.get('verdadero_falso', 0) + num_preguntas.get('corta', 0):
                    tipo_actual = 'corta'
                else:
                    tipo_actual = 'desarrollo'
            
            # Detectar opciones (A), B), C), D) o A., B., C., D.)
            elif re.match(r'^[A-D][\)\.]', linea) and tipo_actual == 'multiple':
                opciones_actuales.append(linea)
            
            # Detectar respuesta correcta
            elif re.search(r'respuesta\s*(correcta)?[:=]\s*([A-D]|verdadero|falso)', linea, re.IGNORECASE):
                match = re.search(r'([A-D]|verdadero|falso)', linea, re.IGNORECASE)
                if match:
                    respuesta_actual = match.group(1).lower() if 'verdadero' in match.group(1).lower() or 'falso' in match.group(1).lower() else match.group(1).upper()
            
            # Si es respuesta esperada o puntos clave, agregar al texto
            elif re.search(r'(respuesta\s*esperada|puntos\s*clave)[:=]', linea, re.IGNORECASE) and tipo_actual in ['corta', 'desarrollo']:
                respuesta_actual = re.sub(r'.*[:=]\s*', '', linea)
        
        # Agregar última pregunta
        if pregunta_actual:
            if tipo_actual == 'multiple' and len(opciones_actuales) >= 4:
                preguntas.append(PreguntaExamen(
                    tipo='multiple',
                    pregunta=pregunta_actual,
                    opciones=opciones_actuales[:4],
                    respuesta_correcta=respuesta_actual or 'A',
                    puntos=3
                ))
            elif tipo_actual == 'verdadero_falso':
                preguntas.append(PreguntaExamen(
                    tipo='verdadero_falso',
                    pregunta=pregunta_actual,
                    respuesta_correcta=respuesta_actual or 'verdadero',
                    puntos=2
                ))
            elif tipo_actual in ['corta', 'desarrollo']:
                preguntas.append(PreguntaExamen(
                    tipo=tipo_actual,
                    pregunta=pregunta_actual,
                    respuesta_correcta=respuesta_actual or '',
                    puntos=4 if tipo_actual == 'corta' else 5
                ))
        
        if log_file:
            self._escribir_log(log_file, f"✅ Parseadas manualmente: {len(preguntas)} preguntas")
        
        print(f"✅ Parseadas manualmente: {len(preguntas)} preguntas")
        return preguntas
    
    def generar_examen(self, contenido: str, num_preguntas: Dict[str, int], 
                      ajustes_modelo: dict = None, callback_progreso=None,
                      archivos: list = None, session_id: str = None,
                      sin_prompt_sistema: bool = False) -> List[PreguntaExamen]:
        """
        Método principal: Genera examen usando el proceso de DOS PASOS
        sin_prompt_sistema: Si es True, usa el contenido directamente sin agregar instrucciones
        """
        # Crear archivo de log para esta sesión
        log_file = self._crear_log_archivo(session_id)
        print(f"\n📝 Log guardándose en: {log_file}")
        
        self._escribir_log(log_file, "="*80)
        self._escribir_log(log_file, "🎓 GENERACIÓN DE EXAMEN - PROCESO DE DOS PASOS")
        self._escribir_log(log_file, "="*80)
        self._escribir_log(log_file, f"Session ID: {session_id or 'N/A'}")
        self._escribir_log(log_file, f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._escribir_log(log_file, f"Prompt personalizado: {sin_prompt_sistema}")
        self._escribir_log(log_file, "="*80 + "\n")
        
        if callback_progreso:
            callback_progreso(10, "Iniciando generación en dos pasos...")
        
        # PASO 1: Generar preguntas naturales
        if callback_progreso:
            callback_progreso(20, "PASO 1: Generando preguntas...")
        
        texto_preguntas = self.paso1_generar_preguntas_naturales(
            contenido, num_preguntas, ajustes_modelo, archivos, log_file, sin_prompt_sistema
        )
        
        if not texto_preguntas:
            print("❌ No se generaron preguntas en el Paso 1")
            self._escribir_log(log_file, "\n❌ ERROR: No se generaron preguntas en el Paso 1")
            return []
        
        # PASO 2: Formatear a JSON
        if callback_progreso:
            callback_progreso(60, "PASO 2: Formateando a JSON...")
        
        json_texto = self.paso2_formatear_a_json(
            texto_preguntas, num_preguntas, ajustes_modelo, log_file
        )
        
        if not json_texto:
            print("❌ No se generó JSON en el Paso 2")
            self._escribir_log(log_file, "\n❌ ERROR: No se generó JSON en el Paso 2")
            return []
        
        # Extraer preguntas del JSON
        if callback_progreso:
            callback_progreso(80, "Extrayendo preguntas...")
        
        preguntas = self._extraer_preguntas_del_json(json_texto, num_preguntas, log_file)
        
        # Finalizar log
        self._escribir_log(log_file, "\n" + "="*80)
        self._escribir_log(log_file, "✅ GENERACIÓN COMPLETADA")
        self._escribir_log(log_file, f"Total preguntas generadas: {len(preguntas)}")
        self._escribir_log(log_file, f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._escribir_log(log_file, "="*80)
        
        print(f"✅ Log guardado en: {log_file}")
        
        if callback_progreso:
            callback_progreso(100, f"✅ {len(preguntas)} preguntas generadas")
        
        return preguntas
    
    def evaluar_respuesta(self, pregunta: PreguntaExamen, respuesta_usuario: str) -> tuple[int, str]:
        """Evalúa una respuesta del usuario usando el modelo de IA para análisis semántico"""
        # Preguntas de opción múltiple: evaluación directa
        if pregunta.tipo == 'multiple':
            r = respuesta_usuario.strip().upper()
            c = pregunta.respuesta_correcta.strip().upper()
            if r == c or r == c[0]:
                return pregunta.puntos, "¡Correcto!"
            return 0, f"Incorrecto. La respuesta correcta es: {pregunta.respuesta_correcta}"
        
        # Validar respuesta mínima
        if not respuesta_usuario or len(respuesta_usuario.strip()) < 10:
            return 0, "❌ Respuesta insuficiente. Se requiere al menos 10 caracteres."
        
        # Para preguntas abiertas: usar el modelo de IA para evaluar comparando con la respuesta esperada
        try:
            # Obtener respuesta esperada
            respuesta_esperada = pregunta.respuesta_correcta or "No especificada"
            
            if pregunta.tipo == 'verdadero_falso':
                prompt = f"""Evalúa esta respuesta comparándola con la correcta:

PREGUNTA: {pregunta.pregunta}
RESPUESTA CORRECTA: {respuesta_esperada}
RESPUESTA DEL ESTUDIANTE: {respuesta_usuario}

Da puntos del 0 al {pregunta.puntos} según qué tan bien respondió comparado con la respuesta correcta.
Explica brevemente qué hizo bien o mal.

PUNTOS: 
FEEDBACK:"""

            elif pregunta.tipo == 'corta':
                prompt = f"""Evalúa esta respuesta comparándola con la esperada:

PREGUNTA: {pregunta.pregunta}
RESPUESTA ESPERADA: {respuesta_esperada}
RESPUESTA DEL ESTUDIANTE: {respuesta_usuario}

Da puntos del 0 al {pregunta.puntos} según:
- ¿Menciona los conceptos clave de la respuesta esperada?
- ¿Es correcta y clara?

PUNTOS:
FEEDBACK:"""

            elif pregunta.tipo == 'desarrollo':
                prompt = f"""Evalúa esta respuesta de desarrollo:

PREGUNTA: {pregunta.pregunta}
PUNTOS CLAVE QUE DEBÍA INCLUIR: {respuesta_esperada}
RESPUESTA DEL ESTUDIANTE: {respuesta_usuario}

Da puntos del 0 al {pregunta.puntos} según:
- ¿Cuántos puntos clave incluyó?
- ¿Qué tan bien desarrolló su respuesta?

PUNTOS:
FEEDBACK:"""

            else:
                return 0, "❌ Tipo de pregunta no soportado"
            
            # Generar evaluación con el modelo
            print(f"🤖 Evaluando respuesta con IA...")
            print(f"📝 Prompt: {prompt[:150]}...")
            
            respuesta_modelo = self.llm(
                prompt,
                max_tokens=250,
                temperature=0.3,
                top_p=0.9,
                repeat_penalty=1.05,
                stop=["PREGUNTA:", "\n\n\n"]
            )
            
            evaluacion = respuesta_modelo['choices'][0]['text'].strip()
            print(f"📊 Evaluación del modelo: {evaluacion[:200]}...")
            
            # Extraer puntos y feedback
            puntos = 0
            feedback = ""
            
            # Buscar patrón PUNTOS:
            import re
            match_puntos = re.search(r'PUNTOS:\s*(\d+(?:\.\d+)?)', evaluacion, re.IGNORECASE)
            if match_puntos:
                puntos_str = match_puntos.group(1)
                puntos = float(puntos_str)
                # Asegurar que no exceda el máximo
                puntos = min(int(puntos), pregunta.puntos)
                puntos = max(0, puntos)  # No negativo
                print(f"✅ Puntos asignados: {puntos}/{pregunta.puntos}")
            else:
                # Si no encuentra el formato, intentar extraer número del inicio
                match_numero = re.search(r'^(\d+(?:\.\d+)?)', evaluacion.strip())
                if match_numero:
                    puntos = min(int(float(match_numero.group(1))), pregunta.puntos)
                    print(f"⚠️ Puntos extraídos sin formato: {puntos}/{pregunta.puntos}")
            
            # Buscar patrón FEEDBACK:
            match_feedback = re.search(r'FEEDBACK:\s*(.+)', evaluacion, re.IGNORECASE | re.DOTALL)
            if match_feedback:
                feedback = match_feedback.group(1).strip()
                # Limpiar el feedback
                lineas = [l.strip() for l in feedback.split('\n') if l.strip()][:4]
                feedback = '\n'.join(lineas)
                print(f"✅ Feedback extraído: {len(feedback)} caracteres")
            else:
                # Si no encuentra FEEDBACK:, usar toda la evaluación después de PUNTOS:
                if match_puntos:
                    texto_despues = evaluacion[match_puntos.end():].strip()
                    if texto_despues:
                        feedback = texto_despues
                        print(f"⚠️ Usando texto completo como feedback")
                else:
                    # Usar toda la evaluación como feedback
                    feedback = evaluacion
                    print(f"⚠️ Usando evaluación completa como feedback")
            
            # Si aún no hay puntos, usar estimación inteligente
            if puntos == 0:
                palabras = len(respuesta_usuario.split())
                print(f"⚠️ No se detectaron puntos, usando fallback...")
                
                if pregunta.tipo in ['corta', 'verdadero_falso']:
                    if palabras < 20:
                        puntos = max(1, pregunta.puntos // 3)
                    elif palabras < 50:
                        puntos = int(pregunta.puntos * 0.7)
                    else:
                        puntos = pregunta.puntos
                elif pregunta.tipo == 'desarrollo':
                    if palabras < 80:
                        puntos = int(pregunta.puntos * 0.4)
                    elif palabras < 150:
                        puntos = int(pregunta.puntos * 0.7)
                    else:
                        puntos = pregunta.puntos
            
            # Si no hay feedback útil, agregar nota
            if not feedback or len(feedback.strip()) < 10:
                feedback = f"Evaluación: {evaluacion}" if evaluacion else "Sin feedback detallado disponible"
            
            return puntos, feedback
            
        except Exception as e:
            print(f"❌ Error en evaluación con IA: {e}")
            # Fallback a evaluación por longitud
            palabras = len(respuesta_usuario.split())
            
            if pregunta.tipo in ['corta', 'verdadero_falso']:
                if palabras < 20:
                    return pregunta.puntos // 3, "⚠️ Respuesta muy breve"
                elif palabras < 50:
                    return int(pregunta.puntos * 0.7), "✓ Respuesta aceptable"
                return pregunta.puntos, "✅ Respuesta completa"
            
            elif pregunta.tipo == 'desarrollo':
                if palabras < 80:
                    return int(pregunta.puntos * 0.4), "⚠️ Desarrollo insuficiente"
                elif palabras < 150:
                    return int(pregunta.puntos * 0.7), "✓ Desarrollo aceptable"
                return pregunta.puntos, "✅ Desarrollo completo"
            
            return 0, "❌ Error en evaluación"
