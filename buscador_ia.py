#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
# Forzar codificación UTF-8 en Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""
Sistema de Búsqueda con IA Local
=================================

Búsqueda híbrida (semántica + keywords) sobre archivos locales
usando modelos open source y GPU RTX 4050.

Características:
- Indexación incremental de txt, md, pdf, flashcards, notas, exámenes
- Embeddings con modelo BGE local (HuggingFace)
- Índice vectorial FAISS (GPU acelerado)
- Búsqueda híbrida: semántica + BM25
- Multiusuario con límites de concurrencia
- Botón "Actualizar índice" incremental
"""

import os
import json
import hashlib
import pickle
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np
from collections import defaultdict

# Para embeddings
try:
    from sentence_transformers import SentenceTransformer
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    print("[!] Instalando dependencias necesarias...")
    print("pip install sentence-transformers torch faiss-cpu PyPDF2 rank-bm25")
    TORCH_AVAILABLE = False
    SentenceTransformer = None
    
    # Importar torch como fallback
    try:
        import torch
    except:
        torch = None

# Para índice vectorial
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    print("[!] Necesitas instalar: pip install faiss-cpu")
    FAISS_AVAILABLE = False
    faiss = None

# Para PDFs
try:
    import PyPDF2
except ImportError:
    print("⚠️ Para PDFs: pip install PyPDF2")

# Para BM25
try:
    from rank_bm25 import BM25Okapi
except ImportError:
    print("⚠️ Para BM25: pip install rank-bm25")


# ===================================
# CONFIGURACIÓN
# ===================================

class ConfigBuscador:
    """Configuración centralizada del buscador"""
    
    # Rutas a indexar (incluye todas las carpetas con contenido relevante)
    CARPETAS_RAIZ = [
        r"C:\Users\Fela\Documents\Proyectos\Examinator\extracciones",
        r"C:\Users\Fela\Documents\Proyectos\Examinator\md",
        r"C:\Users\Fela\Documents\Proyectos\Examinator\datos_persistentes",
        r"C:\Users\Fela\Documents\Proyectos\Examinator\chats",
    ]
    
    # Modelo de embeddings (MODIFICA SI QUIERES OTRO MODELO)
    # Opciones: "BAAI/bge-small-en-v1.5" (ligero), "BAAI/bge-base-en-v1.5" (mejor)
    MODELO_EMBEDDINGS = "BAAI/bge-small-en-v1.5"
    
    # Chunking
    CHUNK_SIZE = 800  # caracteres por chunk
    CHUNK_OVERLAP = 200  # solapamiento entre chunks
    
    # Índice
    RUTA_INDICE = r"C:\Users\Fela\Documents\Proyectos\Examinator\indice_busqueda"
    ARCHIVO_FAISS = "vectores.index"
    ARCHIVO_METADATA = "metadata.pkl"
    ARCHIVO_BM25 = "bm25.pkl"
    ARCHIVO_HASHES = "hashes.json"
    
    # GPU - PyTorch puede usar CUDA incluso con faiss-cpu
    USAR_GPU = True  # RTX 4050 (para embeddings con PyTorch)
    BATCH_SIZE = 32  # para embeddings
    
    # Búsqueda
    MAX_RESULTADOS = 20
    MAX_CONSULTAS_CONCURRENTES = 3
    
    # Tipos de archivo
    EXTENSIONES_TEXTO = {'.txt', '.md', '.json'}
    EXTENSIONES_PDF = {'.pdf'}


# ===================================
# UTILIDADES
# ===================================

def calcular_hash_archivo(ruta: str) -> str:
    """Calcula hash MD5 de un archivo para detectar cambios"""
    try:
        with open(ruta, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"❌ Error calculando hash de {ruta}: {e}")
        return ""


def detectar_tipo_documento(ruta: str) -> str:
    """Detecta el tipo de documento por ruta y contenido"""
    ruta_lower = ruta.lower()
    
    if 'flashcard' in ruta_lower:
        return 'flashcard'
    elif 'examen' in ruta_lower or 'exam' in ruta_lower:
        return 'examen'
    elif 'practica' in ruta_lower or 'practice' in ruta_lower:
        return 'practica'
    elif 'nota' in ruta_lower or 'note' in ruta_lower:
        return 'nota'
    elif 'curso' in ruta_lower or 'course' in ruta_lower:
        return 'curso'
    else:
        return 'documento'


def extraer_texto_practica_json(data: dict) -> str:
    """
    Extrae texto relevante de un JSON de práctica/examen para indexación.
    
    Campos importantes que extrae:
    - pregunta: El enunciado de la pregunta
    - respuesta_correcta: La respuesta esperada
    - explicacion: Explicación del ejercicio
    - opciones: Opciones de respuesta (para MCQ)
    - metadata.texto_lectura: Texto de lectura (idiomas)
    - metadata.oraciones_originales: Para parafraseo
    - metadata.items: Items con palabras clave y oraciones
    - feedback: Retroalimentación
    """
    textos = []
    
    # Nombre de la práctica
    if data.get('nombre'):
        textos.append(f"📝 Práctica: {data['nombre']}")
    
    # Procesar preguntas
    preguntas = data.get('preguntas', [])
    if not isinstance(preguntas, list):
        preguntas = []
    
    for idx, pregunta in enumerate(preguntas):
        if not isinstance(pregunta, dict):
            continue
        
        tipo = pregunta.get('tipo', 'desconocido')
        textos.append(f"\n--- Ejercicio {idx+1} ({tipo}) ---")
        
        # Pregunta principal
        if pregunta.get('pregunta'):
            textos.append(f"Pregunta: {pregunta['pregunta']}")
        
        # Respuesta correcta
        if pregunta.get('respuesta_correcta'):
            textos.append(f"Respuesta: {pregunta['respuesta_correcta']}")
        
        # Explicación
        if pregunta.get('explicacion'):
            textos.append(f"Explicación: {pregunta['explicacion']}")
        
        # Opciones (MCQ)
        opciones = pregunta.get('opciones', [])
        if opciones and isinstance(opciones, list):
            textos.append("Opciones: " + " | ".join(str(o) for o in opciones))
        
        # Metadata específica de cada tipo
        metadata = pregunta.get('metadata', {})
        if isinstance(metadata, dict):
            # Texto de lectura (reading comprehension)
            if metadata.get('texto_lectura'):
                textos.append(f"Texto: {metadata['texto_lectura']}")
            
            # Oraciones originales (parafraseo)
            oraciones_orig = metadata.get('oraciones_originales', [])
            if oraciones_orig:
                for orac in oraciones_orig:
                    if isinstance(orac, dict):
                        if orac.get('original'):
                            textos.append(f"Original: {orac['original']}")
                        if orac.get('parafraseo_esperado'):
                            textos.append(f"Parafraseo: {orac['parafraseo_esperado']}")
            
            # Items (sentence builder, etc.)
            items = metadata.get('items', [])
            if items:
                for item in items:
                    if isinstance(item, dict):
                        if item.get('palabras_clave'):
                            palabras = item['palabras_clave']
                            if isinstance(palabras, list):
                                textos.append(f"Palabras clave: {', '.join(palabras)}")
                        if item.get('oracion_esperada'):
                            textos.append(f"Oración esperada: {item['oracion_esperada']}")
                        if item.get('contexto_pista'):
                            textos.append(f"Contexto: {item['contexto_pista']}")
            
            # Preguntas MCQ internas (reading comprehension)
            preguntas_mcq = metadata.get('preguntas', metadata.get('preguntas_mcq', []))
            if preguntas_mcq:
                for pmcq in preguntas_mcq:
                    if isinstance(pmcq, dict):
                        if pmcq.get('pregunta'):
                            textos.append(f"Sub-pregunta: {pmcq['pregunta']}")
            
            # Afirmaciones (V/F)
            afirmaciones = metadata.get('afirmaciones', [])
            if afirmaciones:
                for afirm in afirmaciones:
                    if isinstance(afirm, dict):
                        if afirm.get('texto'):
                            textos.append(f"Afirmación: {afirm['texto']}")
                        if afirm.get('justificacion'):
                            textos.append(f"Justificación: {afirm['justificacion']}")
            
            # Frases con errores (corrección)
            frases_errores = metadata.get('frases_con_errores', [])
            if frases_errores:
                for frase in frases_errores:
                    if isinstance(frase, dict):
                        if frase.get('frase_con_error'):
                            textos.append(f"Frase con error: {frase['frase_con_error']}")
                        if frase.get('correccion'):
                            textos.append(f"Corrección: {frase['correccion']}")
            
            # Transformaciones
            transformaciones = metadata.get('transformaciones', [])
            if transformaciones:
                for transf in transformaciones:
                    if isinstance(transf, dict):
                        if transf.get('original'):
                            textos.append(f"Original: {transf['original']}")
                        if transf.get('transformacion_esperada'):
                            textos.append(f"Transformación: {transf['transformacion_esperada']}")
            
            # Código (programación)
            if metadata.get('codigo'):
                textos.append(f"Código: {metadata['codigo']}")
            if metadata.get('codigo_corregido'):
                textos.append(f"Código corregido: {metadata['codigo_corregido']}")
        
        # Items a nivel de pregunta (alternativa)
        items_pregunta = pregunta.get('items', [])
        if items_pregunta and isinstance(items_pregunta, list):
            for item in items_pregunta:
                if isinstance(item, dict):
                    if item.get('palabras_clave'):
                        palabras = item['palabras_clave']
                        if isinstance(palabras, list):
                            textos.append(f"Palabras: {', '.join(palabras)}")
                    if item.get('oracion_esperada'):
                        textos.append(f"Oración: {item['oracion_esperada']}")
    
    # Resultados (si hay)
    resultado = data.get('resultado', {})
    if isinstance(resultado, dict):
        resultados_items = resultado.get('resultados', [])
        if resultados_items:
            for res_item in resultados_items:
                if isinstance(res_item, dict):
                    if res_item.get('feedback'):
                        textos.append(f"Feedback: {res_item['feedback']}")
    
    return '\n'.join(textos)


def leer_archivo_texto(ruta: str) -> str:
    """Lee archivo de texto (txt, md, json)"""
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(ruta, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error leyendo {ruta}: {e}")
            return ""
    except Exception as e:
        print(f"❌ Error leyendo {ruta}: {e}")
        return ""


def leer_pdf(ruta: str) -> str:
    """Lee archivo PDF"""
    try:
        with open(ruta, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            texto = ""
            for pagina in reader.pages:
                texto += pagina.extract_text() + "\n"
            return texto
    except Exception as e:
        print(f"❌ Error leyendo PDF {ruta}: {e}")
        return ""


def trocear_texto(texto: str, chunk_size: int = 800, overlap: int = 200) -> List[str]:
    """
    Trocea texto en chunks inteligentes.
    Intenta cortar por párrafos/líneas cuando sea posible.
    """
    if len(texto) <= chunk_size:
        return [texto]
    
    chunks = []
    
    # Dividir por párrafos primero
    parrafos = texto.split('\n\n')
    
    chunk_actual = ""
    for parrafo in parrafos:
        if len(chunk_actual) + len(parrafo) + 2 <= chunk_size:
            chunk_actual += parrafo + "\n\n"
        else:
            if chunk_actual:
                chunks.append(chunk_actual.strip())
            
            # Si el párrafo es muy largo, trocearlo
            if len(parrafo) > chunk_size:
                for i in range(0, len(parrafo), chunk_size - overlap):
                    chunks.append(parrafo[i:i + chunk_size].strip())
                chunk_actual = ""
            else:
                chunk_actual = parrafo + "\n\n"
    
    if chunk_actual:
        chunks.append(chunk_actual.strip())
    
    return [c for c in chunks if c.strip()]


# ===================================
# INDEXADOR
# ===================================

class IndexadorLocal:
    """Indexa archivos locales generando embeddings y metadata"""
    
    def __init__(self, config: ConfigBuscador):
        self.config = config
        self.modelo = None
        self.device = None
        self.hashes_previos = {}
        
        # Crear directorio de índice
        os.makedirs(config.RUTA_INDICE, exist_ok=True)
        
        # Cargar hashes previos
        self._cargar_hashes()
    
    def _cargar_hashes(self):
        """Carga hashes de indexación previa"""
        ruta_hashes = os.path.join(self.config.RUTA_INDICE, self.config.ARCHIVO_HASHES)
        if os.path.exists(ruta_hashes):
            with open(ruta_hashes, 'r') as f:
                self.hashes_previos = json.load(f)
            print(f"📁 Cargados {len(self.hashes_previos)} hashes previos")
    
    def _guardar_hashes(self, hashes: Dict[str, str]):
        """Guarda hashes de archivos indexados"""
        ruta_hashes = os.path.join(self.config.RUTA_INDICE, self.config.ARCHIVO_HASHES)
        with open(ruta_hashes, 'w') as f:
            json.dump(hashes, f, indent=2)
    
    def inicializar_modelo(self):
        """Inicializa modelo de embeddings"""
        if self.modelo is not None:
            return
        
        print(f"🔧 Cargando modelo {self.config.MODELO_EMBEDDINGS}...")
        
        # Intentar usar GPU con PyTorch/CUDA
        if self.config.USAR_GPU and torch and torch.cuda.is_available():
            self.device = 'cuda'
            print(f"🎮 GPU detectada: {torch.cuda.get_device_name(0)}")
        else:
            self.device = 'cpu'
            print("💻 Usando CPU")
        
        # Cargar modelo
        self.modelo = SentenceTransformer(self.config.MODELO_EMBEDDINGS, device=self.device)
        print(f"✅ Modelo cargado en {self.device}")
    
    def escanear_archivos(self, incremental: bool = False) -> List[Dict]:
        """
        Escanea carpetas y retorna lista de archivos a indexar.
        Si incremental=True, solo retorna nuevos/modificados.
        """
        archivos_a_indexar = []
        hashes_actuales = {}
        
        for carpeta_raiz in self.config.CARPETAS_RAIZ:
            if not os.path.exists(carpeta_raiz):
                print(f"⚠️ Carpeta no existe: {carpeta_raiz}")
                continue
            
            print(f"📂 Escaneando {carpeta_raiz}...")
            
            for root, dirs, files in os.walk(carpeta_raiz):
                # Excluir carpetas del sistema
                dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '.git', '__pycache__', 'indice_busqueda', 'indices_busqueda', 'examinator-web', 'temp', 'logs_generacion']]
                
                for archivo in files:
                    ruta_completa = os.path.join(root, archivo)
                    ext = Path(archivo).suffix.lower()
                    
                    # Filtrar por extensión
                    if ext not in self.config.EXTENSIONES_TEXTO and ext not in self.config.EXTENSIONES_PDF:
                        continue
                    
                    # Excluir archivos del sistema, node_modules, venv, etc.
                    if any(excluir in ruta_completa.lower() for excluir in ['node_modules', 'venv', '.git', '__pycache__', 'indices_busqueda']):
                        continue
                    
                    # Calcular hash
                    hash_actual = calcular_hash_archivo(ruta_completa)
                    if not hash_actual:
                        continue
                    
                    hashes_actuales[ruta_completa] = hash_actual
                    
                    # Si es incremental, solo agregar si es nuevo o modificado
                    if incremental:
                        hash_previo = self.hashes_previos.get(ruta_completa)
                        if hash_previo == hash_actual:
                            continue  # No ha cambiado
                    
                    # Agregar a lista
                    archivos_a_indexar.append({
                        'ruta': ruta_completa,
                        'nombre': archivo,
                        'extension': ext,
                        'tipo': detectar_tipo_documento(ruta_completa),
                        'timestamp': datetime.fromtimestamp(os.path.getmtime(ruta_completa)),
                        'hash': hash_actual
                    })
        
        print(f"📊 Encontrados {len(archivos_a_indexar)} archivos a indexar")
        
        # Guardar hashes actuales
        self._guardar_hashes(hashes_actuales)
        
        return archivos_a_indexar
    
    def procesar_archivo(self, info_archivo: Dict) -> List[Dict]:
        """Procesa un archivo y retorna lista de chunks con metadata"""
        ruta = info_archivo['ruta']
        ext = info_archivo['extension']
        tipo_doc = info_archivo['tipo']
        
        # Leer contenido
        if ext in self.config.EXTENSIONES_PDF:
            contenido = leer_pdf(ruta)
        elif ext == '.json':
            # Para archivos JSON de prácticas/exámenes, extraer texto relevante
            contenido_raw = leer_archivo_texto(ruta)
            if contenido_raw.strip():
                try:
                    data = json.loads(contenido_raw)
                    # Si es un JSON de práctica o examen, extraer texto relevante
                    if isinstance(data, dict) and ('preguntas' in data or tipo_doc in ['practica', 'examen']):
                        contenido = extraer_texto_practica_json(data)
                        if not contenido.strip():
                            contenido = contenido_raw  # Fallback al JSON raw
                    else:
                        contenido = contenido_raw
                except json.JSONDecodeError:
                    contenido = contenido_raw  # Si no es JSON válido, usar raw
            else:
                contenido = ""
        else:
            contenido = leer_archivo_texto(ruta)
        
        if not contenido.strip():
            return []
        
        # Trocear
        chunks = trocear_texto(
            contenido,
            self.config.CHUNK_SIZE,
            self.config.CHUNK_OVERLAP
        )
        
        # Crear metadata para cada chunk
        chunks_con_metadata = []
        for idx, chunk in enumerate(chunks):
            chunks_con_metadata.append({
                'texto': chunk,
                'ruta': ruta,
                'nombre': info_archivo['nombre'],
                'tipo': info_archivo['tipo'],
                'chunk_id': idx,
                'total_chunks': len(chunks),
                'timestamp': info_archivo['timestamp'].isoformat(),
            })
        
        return chunks_con_metadata
    
    def generar_embeddings(self, textos: List[str]) -> np.ndarray:
        """Genera embeddings para lista de textos (con batching)"""
        if self.modelo is None:
            self.inicializar_modelo()
        
        embeddings = self.modelo.encode(
            textos,
            batch_size=self.config.BATCH_SIZE,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True  # Importante para búsqueda coseno
        )
        
        return embeddings
    
    def indexar(self, incremental: bool = False) -> Tuple[int, int]:
        """
        Indexa archivos completos.
        Retorna (archivos_procesados, chunks_indexados)
        """
        print("🚀 Iniciando indexación...")
        
        # Escanear archivos
        archivos = self.escanear_archivos(incremental=incremental)
        
        if not archivos:
            print("✅ No hay archivos nuevos para indexar")
            return 0, 0
        
        # Procesar archivos
        print("📝 Procesando archivos...")
        todos_chunks = []
        for info_archivo in archivos:
            chunks = self.procesar_archivo(info_archivo)
            todos_chunks.extend(chunks)
        
        print(f"📦 Total de chunks: {len(todos_chunks)}")
        
        if not todos_chunks:
            return len(archivos), 0
        
        # Generar embeddings
        print("🧠 Generando embeddings...")
        textos = [c['texto'] for c in todos_chunks]
        embeddings = self.generar_embeddings(textos)
        
        # Guardar índice FAISS
        print("💾 Guardando índice FAISS...")
        self._guardar_indice_faiss(embeddings, todos_chunks, incremental)
        
        # Guardar metadata
        print("💾 Guardando metadata...")
        self._guardar_metadata(todos_chunks, incremental)
        
        # Generar índice BM25
        print("📊 Generando índice BM25...")
        self._generar_indice_bm25(textos, incremental)
        
        print(f"✅ Indexación completa: {len(archivos)} archivos, {len(todos_chunks)} chunks")
        
        return len(archivos), len(todos_chunks)
    
    def _guardar_indice_faiss(self, embeddings: np.ndarray, chunks: List[Dict], incremental: bool):
        """Guarda índice FAISS (incremental si ya existe)"""
        ruta_indice = os.path.join(self.config.RUTA_INDICE, self.config.ARCHIVO_FAISS)
        
        dimension = embeddings.shape[1]
        
        if incremental and os.path.exists(ruta_indice):
            # Cargar índice existente
            index = faiss.read_index(ruta_indice)
            # Agregar nuevos vectores
            index.add(embeddings.astype('float32'))
        else:
            # Crear nuevo índice
            # Usar IndexFlatIP (inner product) para coseno con vectores normalizados
            index = faiss.IndexFlatIP(dimension)
            
            # GPU desactivado - usando CPU
            # (Si quieres GPU, instala faiss-gpu y cambia USAR_GPU=True en config)
            
            index.add(embeddings.astype('float32'))
        
        # Guardar (siempre desde CPU)
        faiss.write_index(index, ruta_indice)
    
    def _guardar_metadata(self, chunks: List[Dict], incremental: bool):
        """Guarda metadata de chunks"""
        ruta_metadata = os.path.join(self.config.RUTA_INDICE, self.config.ARCHIVO_METADATA)
        
        if incremental and os.path.exists(ruta_metadata):
            # Cargar metadata existente
            with open(ruta_metadata, 'rb') as f:
                metadata_existente = pickle.load(f)
            metadata_existente.extend(chunks)
            chunks = metadata_existente
        
        with open(ruta_metadata, 'wb') as f:
            pickle.dump(chunks, f)
    
    def _generar_indice_bm25(self, textos: List[str], incremental: bool):
        """Genera índice BM25 para búsqueda por keywords"""
        ruta_bm25 = os.path.join(self.config.RUTA_INDICE, self.config.ARCHIVO_BM25)
        ruta_metadata = os.path.join(self.config.RUTA_INDICE, self.config.ARCHIVO_METADATA)
        
        # Tokenizar (simple)
        corpus_tokenizado = [texto.lower().split() for texto in textos]
        
        if incremental and os.path.exists(ruta_metadata):
            # Para incremental, recargar TODOS los textos desde metadata
            try:
                with open(ruta_metadata, 'rb') as f:
                    metadata_completa = pickle.load(f)
                corpus_tokenizado = [m['texto'].lower().split() for m in metadata_completa]
            except Exception as e:
                print(f"⚠️ Error recargando metadata para BM25: {e}")
        
        bm25 = BM25Okapi(corpus_tokenizado)
        
        with open(ruta_bm25, 'wb') as f:
            pickle.dump(bm25, f)


# Continúa en el siguiente mensaje...
