#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
# Forzar codificación UTF-8 en Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""
API del Buscador IA Local
=========================

Servicio Flask que expone endpoints para:
- Búsqueda híbrida (semántica + keywords)
- Actualización incremental del índice
- Estado del sistema
- Detección y configuración de GPU
- Instalación automática de dependencias GPU
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pickle
import json
import subprocess
import numpy as np
from typing import List, Dict, Tuple, Optional
from threading import Lock, Semaphore
import time

# Importaciones condicionales para manejar GPU/CPU
FAISS_DISPONIBLE = False
FAISS_GPU = False
TORCH_DISPONIBLE = False
CUDA_DISPONIBLE = False
SENTENCE_TRANSFORMERS_DISPONIBLE = False

try:
    import torch
    TORCH_DISPONIBLE = True
    CUDA_DISPONIBLE = torch.cuda.is_available()
except ImportError:
    torch = None

try:
    import faiss
    FAISS_DISPONIBLE = True
    # Verificar si faiss tiene soporte GPU
    try:
        if hasattr(faiss, 'get_num_gpus') and faiss.get_num_gpus() > 0:
            FAISS_GPU = True
    except:
        pass
except ImportError:
    faiss = None

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_DISPONIBLE = True
except ImportError:
    SentenceTransformer = None

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None

from buscador_ia import ConfigBuscador, IndexadorLocal

# Archivo de configuración de modo GPU/CPU
CONFIG_GPU_FILE = os.path.join(os.path.dirname(__file__), "config_gpu.json")

def cargar_config_gpu():
    """Carga la configuración de GPU desde archivo"""
    if os.path.exists(CONFIG_GPU_FILE):
        try:
            with open(CONFIG_GPU_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"modo": "cpu", "gpu_instalada": False}

def guardar_config_gpu(config):
    """Guarda la configuración de GPU"""
    with open(CONFIG_GPU_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def detectar_gpu_nvidia():
    """Detecta si hay GPU NVIDIA disponible en el sistema"""
    info = {
        "gpu_detectada": False,
        "nombre_gpu": None,
        "vram_mb": None,
        "cuda_version": None,
        "driver_version": None
    }
    
    try:
        # Intentar nvidia-smi para detectar GPU
        resultado = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if resultado.returncode == 0 and resultado.stdout.strip():
            partes = resultado.stdout.strip().split(", ")
            info["gpu_detectada"] = True
            info["nombre_gpu"] = partes[0] if len(partes) > 0 else "GPU NVIDIA"
            info["vram_mb"] = int(partes[1]) if len(partes) > 1 else None
            info["driver_version"] = partes[2] if len(partes) > 2 else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Detectar versión de CUDA si torch está instalado con CUDA
    if TORCH_DISPONIBLE and CUDA_DISPONIBLE:
        info["cuda_version"] = torch.version.cuda
        if not info["gpu_detectada"]:
            info["gpu_detectada"] = True
            info["nombre_gpu"] = torch.cuda.get_device_name(0)
            try:
                info["vram_mb"] = torch.cuda.get_device_properties(0).total_memory // (1024 * 1024)
            except:
                pass
    
    return info

def verificar_dependencias_gpu():
    """Verifica si las dependencias para GPU están instaladas (chequeo dinámico)"""
    # Hacer chequeo dinámico en lugar de usar las variables cacheadas al inicio
    refrescar_estado_gpu()
    return {
        "torch_cuda": TORCH_DISPONIBLE and CUDA_DISPONIBLE,
        "faiss_gpu": FAISS_GPU,
        "sentence_transformers": SENTENCE_TRANSFORMERS_DISPONIBLE,
        "completo": TORCH_DISPONIBLE and CUDA_DISPONIBLE and SENTENCE_TRANSFORMERS_DISPONIBLE
    }

def refrescar_estado_gpu():
    """Re-chequea las dependencias GPU actualizando las variables globales"""
    global TORCH_DISPONIBLE, CUDA_DISPONIBLE, FAISS_GPU, SENTENCE_TRANSFORMERS_DISPONIBLE, torch, faiss, SentenceTransformer
    
    try:
        import torch as _torch
        torch = _torch
        TORCH_DISPONIBLE = True
        CUDA_DISPONIBLE = torch.cuda.is_available()
    except ImportError:
        torch = None
        TORCH_DISPONIBLE = False
        CUDA_DISPONIBLE = False
    
    try:
        import faiss as _faiss
        faiss = _faiss
        try:
            if hasattr(faiss, 'get_num_gpus') and faiss.get_num_gpus() > 0:
                FAISS_GPU = True
        except:
            pass
    except ImportError:
        pass
    
    try:
        from sentence_transformers import SentenceTransformer as _ST
        SentenceTransformer = _ST
        SENTENCE_TRANSFORMERS_DISPONIBLE = True
    except ImportError:
        pass


# ===================================
# BUSCADOR
# ===================================

class BuscadorHibrido:
    """Buscador que combina búsqueda semántica (FAISS) + keywords (BM25)"""
    
    def __init__(self, config: ConfigBuscador, modo_gpu: str = None):
        self.config = config
        self.modelo = None
        self.index_faiss = None
        self.metadata = []
        self.bm25 = None
        self.device = None
        
        # Cargar modo de GPU desde config si no se especifica
        if modo_gpu is None:
            config_guardada = cargar_config_gpu()
            self.modo_gpu = config_guardada.get("modo", "cpu")
        else:
            self.modo_gpu = modo_gpu
        
        # Control de concurrencia
        self.lock = Lock()
        self.semaforo = Semaphore(config.MAX_CONSULTAS_CONCURRENTES)
        
        self.cargar_indices()
    
    def cambiar_modo(self, nuevo_modo: str):
        """Cambia entre modo CPU y GPU"""
        if nuevo_modo not in ["cpu", "gpu"]:
            raise ValueError("Modo debe ser 'cpu' o 'gpu'")
        
        if nuevo_modo == "gpu" and not CUDA_DISPONIBLE:
            raise ValueError("GPU no disponible. Instala las dependencias primero.")
        
        self.modo_gpu = nuevo_modo
        
        # Recargar modelo con nuevo dispositivo
        self.modelo = None
        self._cargar_modelo()
        
        # Guardar preferencia
        config_gpu = cargar_config_gpu()
        config_gpu["modo"] = nuevo_modo
        guardar_config_gpu(config_gpu)
        
        return {"modo": nuevo_modo, "device": self.device}
    
    def cargar_indices(self):
        """Carga índices FAISS, metadata y BM25"""
        print("📂 Cargando índices...")
        
        ruta_faiss = os.path.join(self.config.RUTA_INDICE, self.config.ARCHIVO_FAISS)
        ruta_metadata = os.path.join(self.config.RUTA_INDICE, self.config.ARCHIVO_METADATA)
        ruta_bm25 = os.path.join(self.config.RUTA_INDICE, self.config.ARCHIVO_BM25)
        
        # FAISS
        if os.path.exists(ruta_faiss) and faiss is not None:
            self.index_faiss = faiss.read_index(ruta_faiss)
            print(f"✅ Índice FAISS cargado: {self.index_faiss.ntotal} vectores")
        else:
            print("⚠️ No existe índice FAISS o faiss no instalado")
        
        # Metadata
        if os.path.exists(ruta_metadata):
            with open(ruta_metadata, 'rb') as f:
                self.metadata = pickle.load(f)
            print(f"✅ Metadata cargada: {len(self.metadata)} chunks")
        else:
            print("⚠️ No existe metadata")
        
        # BM25
        if os.path.exists(ruta_bm25):
            with open(ruta_bm25, 'rb') as f:
                self.bm25 = pickle.load(f)
            print(f"✅ Índice BM25 cargado")
        else:
            print("⚠️ No existe índice BM25")
        
        # Modelo
        self._cargar_modelo()
    
    def _cargar_modelo(self):
        """Carga modelo de embeddings"""
        if self.modelo is not None:
            return
        
        if not SENTENCE_TRANSFORMERS_DISPONIBLE:
            print("❌ sentence-transformers no instalado")
            return
        
        print(f"🔧 Cargando modelo {self.config.MODELO_EMBEDDINGS}...")
        
        # Determinar dispositivo según el modo configurado
        if self.modo_gpu == "gpu" and CUDA_DISPONIBLE:
            self.device = 'cuda'
            print(f"🎮 GPU detectada: {torch.cuda.get_device_name(0)}")
        else:
            self.device = 'cpu'
            print("💻 Usando CPU")
        
        self.modelo = SentenceTransformer(self.config.MODELO_EMBEDDINGS, device=self.device)
        print(f"✅ Modelo listo en {self.device}")
    
    def extraer_contexto_relevante(self, texto: str, query: str, max_chars: int = 300) -> str:
        """
        Extrae el fragmento del texto donde aparece el término buscado.
        
        Args:
            texto: Texto completo del chunk
            query: Término buscado
            max_chars: Máximo de caracteres a extraer
        
        Returns:
            Fragmento de texto con el contexto relevante
        """
        texto_lower = texto.lower()
        query_lower = query.lower()
        
        # Buscar términos de la query en el texto
        palabras_query = query_lower.split()
        mejor_pos = -1
        mejor_score = 0
        
        # Buscar la posición donde aparecen más palabras de la query
        for i in range(len(texto)):
            ventana = texto_lower[i:i+max_chars]
            score = sum(1 for palabra in palabras_query if palabra in ventana)
            if score > mejor_score:
                mejor_score = score
                mejor_pos = i
        
        # Si no encontró nada, devolver el inicio
        if mejor_pos == -1:
            return texto[:max_chars] + ('...' if len(texto) > max_chars else '')
        
        # Ajustar para no cortar palabras
        inicio = mejor_pos
        # Retroceder hasta encontrar inicio de frase o espacio
        while inicio > 0 and texto[inicio-1] not in '.!?\n':
            inicio -= 1
            if mejor_pos - inicio > 100:  # No retroceder demasiado
                break
        
        # Limpiar espacios iniciales
        while inicio < len(texto) and texto[inicio] in ' \n\t':
            inicio += 1
        
        # Extraer fragmento
        fin = min(inicio + max_chars, len(texto))
        fragmento = texto[inicio:fin]
        
        # Agregar puntos suspensivos
        if inicio > 0:
            fragmento = '...' + fragmento
        if fin < len(texto):
            fragmento = fragmento + '...'
        
        return fragmento
    
    def buscar_semantica(self, query: str, k: int = 20) -> List[Tuple[int, float]]:
        """Búsqueda semántica con FAISS"""
        if self.index_faiss is None or self.modelo is None:
            return []
        
        # Generar embedding de la query
        query_embedding = self.modelo.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        # Buscar
        distancias, indices = self.index_faiss.search(query_embedding.astype('float32'), k)
        
        # Retornar (índice, score)
        resultados = []
        for idx, dist in zip(indices[0], distancias[0]):
            if idx >= 0:  # FAISS retorna -1 si no hay suficientes
                resultados.append((int(idx), float(dist)))
        
        return resultados
    
    def buscar_keywords(self, query: str, k: int = 20) -> List[Tuple[int, float]]:
        """Búsqueda por keywords con BM25"""
        if self.bm25 is None:
            return []
        
        query_tokens = query.lower().split()
        scores = self.bm25.get_scores(query_tokens)
        
        # Top K
        top_indices = np.argsort(scores)[::-1][:k]
        
        resultados = []
        for idx in top_indices:
            score = scores[idx]
            if score > 0:  # Solo resultados relevantes
                resultados.append((int(idx), float(score)))
        
        return resultados
    
    def fusionar_resultados(
        self,
        semanticos: List[Tuple[int, float]],
        keywords: List[Tuple[int, float]],
        peso_semantico: float = 0.7
    ) -> List[Tuple[int, float]]:
        """Fusiona resultados de búsqueda semántica y keywords"""
        # Normalizar scores
        if semanticos:
            max_sem = max(s for _, s in semanticos)
            semanticos = [(idx, s/max_sem if max_sem > 0 else s) for idx, s in semanticos]
        
        if keywords:
            max_key = max(s for _, s in keywords)
            keywords = [(idx, s/max_key if max_key > 0 else s) for idx, s in keywords]
        
        # Combinar
        scores_combinados = {}
        
        for idx, score in semanticos:
            scores_combinados[idx] = score * peso_semantico
        
        for idx, score in keywords:
            if idx in scores_combinados:
                scores_combinados[idx] += score * (1 - peso_semantico)
            else:
                scores_combinados[idx] = score * (1 - peso_semantico)
        
        # Ordenar
        resultados = sorted(scores_combinados.items(), key=lambda x: x[1], reverse=True)
        
        return resultados
    
    def buscar(
        self,
        query: str,
        tipo_filtro: Optional[str] = None,
        max_resultados: int = None
    ) -> List[Dict]:
        """
        Búsqueda híbrida principal.
        
        Args:
            query: Texto de búsqueda
            tipo_filtro: Filtrar por tipo (nota, examen, practica, flashcard)
            max_resultados: Máximo de resultados a devolver
        
        Returns:
            Lista de resultados con metadata
        """
        if max_resultados is None:
            max_resultados = self.config.MAX_RESULTADOS
        
        # Control de concurrencia
        if not self.semaforo.acquire(blocking=False):
            return {"error": "Demasiadas consultas concurrentes"}
        
        try:
            start_time = time.time()
            
            # Búsqueda semántica
            resultados_sem = self.buscar_semantica(query, k=50)
            
            # Búsqueda keywords
            resultados_key = self.buscar_keywords(query, k=50)
            
            # Fusionar
            resultados_fusionados = self.fusionar_resultados(resultados_sem, resultados_key)
            
            # Construir respuesta
            respuesta = []
            for idx, score in resultados_fusionados:
                # Salir si ya tenemos suficientes resultados
                if len(respuesta) >= max_resultados:
                    break
                    
                if idx >= len(self.metadata):
                    continue
                
                meta = self.metadata[idx]
                
                # Filtrar por tipo si se especifica
                if tipo_filtro and meta['tipo'] != tipo_filtro:
                    continue
                
                # Extraer contexto relevante donde aparece el término buscado
                contexto_relevante = self.extraer_contexto_relevante(meta['texto'], query, max_chars=300)
                
                respuesta.append({
                    'contenido': contexto_relevante,
                    'texto_completo': meta['texto'],
                    'score': round(score, 4),
                    'ruta': meta['ruta'],
                    'nombre_archivo': meta['nombre'],
                    'tipo': meta['tipo'],
                    'chunk_id': meta['chunk_id'],
                    'total_chunks': meta['total_chunks'],
                    'timestamp': meta['timestamp']
                })
            
            tiempo_busqueda = time.time() - start_time
            
            return {
                'resultados': respuesta,
                'total': len(respuesta),
                'tiempo': round(tiempo_busqueda, 3),
                'query': query
            }
        
        finally:
            self.semaforo.release()


# ===================================
# API FLASK
# ===================================

app = Flask(__name__)
CORS(app)

# Instancias globales (se inicializarán al inicio)
config = None
buscador = None
indexador = None

# Lock para actualización de índice
lock_actualizacion = Lock()

def inicializar_sistema():
    """Inicializa el sistema de búsqueda"""
    global config, buscador, indexador
    
    print("🔧 Inicializando sistema...")
    config = ConfigBuscador()
    buscador = BuscadorHibrido(config)
    indexador = IndexadorLocal(config)
    print("✅ Sistema inicializado\n")


@app.route('/api/buscar', methods=['POST'])
def api_buscar():
    """
    Endpoint de búsqueda.
    
    POST /api/buscar
    {
        "query": "texto a buscar",
        "tipo": "nota|examen|practica|flashcard",  // opcional
        "max_resultados": 20  // opcional
    }
    """
    try:
        datos = request.json
        query = datos.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query vacía'}), 400
        
        tipo_filtro = datos.get('tipo')
        max_resultados = datos.get('max_resultados', config.MAX_RESULTADOS)
        
        print(f"\n🔍 Búsqueda: '{query}' | Tipo: {tipo_filtro or 'todos'} | Max: {max_resultados}")
        
        resultados = buscador.buscar(
            query=query,
            tipo_filtro=tipo_filtro,
            max_resultados=max_resultados
        )
        
        print(f"✅ {resultados['total']} resultados encontrados\n")
        
        return jsonify(resultados)
    
    except Exception as e:
        print(f"\n❌ Error en búsqueda: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/actualizar_indice', methods=['POST'])
def api_actualizar_indice():
    """
    Actualiza el índice de forma incremental.
    
    POST /api/actualizar_indice
    {
        "completo": false  // true para reindexar todo
    }
    """
    # Evitar múltiples actualizaciones simultáneas
    if not lock_actualizacion.acquire(blocking=False):
        return jsonify({'error': 'Ya hay una actualización en curso'}), 409
    
    try:
        datos = request.json or {}
        completo = datos.get('completo', False)
        
        print(f"\n{'='*60}")
        print(f"🔄 Iniciando {'reindexación completa' if completo else 'actualización incremental'}...")
        print(f"{'='*60}\n")
        
        # Indexar
        archivos_procesados, chunks_indexados = indexador.indexar(incremental=not completo)
        
        print(f"\n✅ Indexación completada: {archivos_procesados} archivos, {chunks_indexados} chunks\n")
        
        # Recargar índices
        print("🔄 Recargando índices en memoria...")
        buscador.cargar_indices()
        print("✅ Índices recargados\n")
        
        return jsonify({
            'success': True,
            'archivos_procesados': archivos_procesados,
            'chunks_indexados': chunks_indexados,
            'total_chunks': len(buscador.metadata) if buscador.metadata else 0
        })
    
    except Exception as e:
        print(f"\n❌ Error en actualización: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
    finally:
        lock_actualizacion.release()


@app.route('/api/estado', methods=['GET'])
def api_estado():
    """Retorna estado del sistema con información detallada de GPU"""
    # Detectar GPU
    info_gpu = detectar_gpu_nvidia()
    deps_gpu = verificar_dependencias_gpu()
    config_gpu = cargar_config_gpu()
    
    # Determinar si GPU está activa
    gpu_activa = (config_gpu.get("modo") == "gpu" and 
                  CUDA_DISPONIBLE and 
                  buscador.device == 'cuda' if buscador else False)
    
    return jsonify({
        'total_chunks': len(buscador.metadata) if buscador and buscador.metadata else 0,
        'total_archivos': len(set(m['ruta'] for m in buscador.metadata)) if buscador and buscador.metadata else 0,
        'modelo': config.MODELO_EMBEDDINGS if config else "No iniciado",
        'carpetas_indexadas': config.CARPETAS_RAIZ if config else [],
        'indexado': len(buscador.metadata) > 0 if buscador and buscador.metadata else False,
        
        # Información de GPU
        'gpu_detectada': info_gpu['gpu_detectada'],
        'gpu_nombre': info_gpu['nombre_gpu'],
        'gpu_vram_mb': info_gpu['vram_mb'],
        'gpu_driver': info_gpu['driver_version'],
        'cuda_version': info_gpu['cuda_version'],
        
        # Estado de dependencias GPU
        'deps_gpu': deps_gpu,
        'gpu_lista_para_usar': deps_gpu['completo'] and info_gpu['gpu_detectada'],
        
        # Modo actual
        'modo_actual': config_gpu.get("modo", "cpu"),
        'gpu_activa': gpu_activa,
        'device_actual': buscador.device if buscador else None,
        
        # Compatibilidad con código anterior
        'gpu_disponible': CUDA_DISPONIBLE
    })


@app.route('/api/gpu/detectar', methods=['GET'])
def api_detectar_gpu():
    """Detecta si hay GPU disponible y sus características"""
    info = detectar_gpu_nvidia()
    deps = verificar_dependencias_gpu()
    config_gpu = cargar_config_gpu()
    
    return jsonify({
        **info,
        'dependencias': deps,
        'modo_guardado': config_gpu.get("modo", "cpu"),
        'puede_usar_gpu': info['gpu_detectada'] and deps['completo']
    })


@app.route('/api/gpu/instalar', methods=['POST'])
def api_instalar_gpu():
    """
    Instala las dependencias necesarias para usar GPU (torch con CUDA).
    Este proceso puede tardar varios minutos.
    """
    info_gpu = detectar_gpu_nvidia()
    
    if not info_gpu['gpu_detectada']:
        return jsonify({
            'error': 'No se detectó ninguna GPU NVIDIA en el sistema',
            'sugerencia': 'Asegúrate de tener una GPU NVIDIA y los drivers instalados'
        }), 400
    
    try:
        resultados = []
        errores = []
        
        # 1. Instalar PyTorch con CUDA
        print("📦 Instalando PyTorch con CUDA...")
        resultados.append("Instalando PyTorch con CUDA 12.4...")
        
        # Usar pip para instalar torch con CUDA
        # IMPORTANTE: usar --force-reinstall en vez de --upgrade para evitar
        # que pip instale una versión CPU-only más reciente del índice por defecto
        comando_torch = [
            sys.executable, "-m", "pip", "install", "--force-reinstall",
            "torch", "torchvision", "torchaudio",
            "--index-url", "https://download.pytorch.org/whl/cu124"
        ]
        
        proceso = subprocess.run(
            comando_torch,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutos máximo
        )
        
        if proceso.returncode == 0:
            resultados.append("✅ PyTorch con CUDA instalado correctamente")
        else:
            errores.append(f"Error instalando PyTorch: {proceso.stderr}")
            
        # 2. Instalar sentence-transformers si no está
        if not SENTENCE_TRANSFORMERS_DISPONIBLE:
            print("📦 Instalando sentence-transformers...")
            proceso = subprocess.run(
                [sys.executable, "-m", "pip", "install", "sentence-transformers"],
                capture_output=True,
                text=True,
                timeout=300
            )
            if proceso.returncode == 0:
                resultados.append("✅ sentence-transformers instalado")
            else:
                errores.append(f"Error instalando sentence-transformers: {proceso.stderr}")
        
        # 3. Refrescar estado de las dependencias GPU tras instalar
        refrescar_estado_gpu()
        
        # 4. Guardar configuración
        config_gpu = cargar_config_gpu()
        config_gpu["gpu_instalada"] = len(errores) == 0
        guardar_config_gpu(config_gpu)
        
        # Mensaje final
        gpu_activa_ahora = TORCH_DISPONIBLE and CUDA_DISPONIBLE
        if errores:
            return jsonify({
                'success': False,
                'resultados': resultados,
                'errores': errores,
                'mensaje': '⚠️ Instalación parcial. Algunos componentes fallaron.'
            }), 500
        else:
            return jsonify({
                'success': True,
                'resultados': resultados,
                'gpu_activa': gpu_activa_ahora,
                'mensaje': '✅ GPU instalada y lista.' if gpu_activa_ahora else '✅ Instalación completada. Reinicia el servidor para activar GPU.',
                'siguiente_paso': 'Activa el modo GPU' if gpu_activa_ahora else 'Reinicia el servidor y activa el modo GPU'
            })
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'error': 'La instalación tardó demasiado tiempo',
            'sugerencia': 'Intenta instalar manualmente: pip install torch --index-url https://download.pytorch.org/whl/cu124'
        }), 500
    except Exception as e:
        return jsonify({
            'error': str(e),
            'sugerencia': 'Revisa la consola del servidor para más detalles'
        }), 500


@app.route('/api/gpu/activar', methods=['POST'])
def api_activar_gpu():
    """Activa el modo GPU para las búsquedas"""
    datos = request.json or {}
    modo = datos.get('modo', 'gpu')  # 'gpu' o 'cpu'
    
    if modo not in ['cpu', 'gpu']:
        return jsonify({'error': 'Modo debe ser "cpu" o "gpu"'}), 400
    
    if modo == 'gpu':
        # Verificar que GPU esté disponible
        if not CUDA_DISPONIBLE:
            return jsonify({
                'error': 'CUDA no está disponible. Instala las dependencias primero.',
                'deps': verificar_dependencias_gpu()
            }), 400
        
        info_gpu = detectar_gpu_nvidia()
        if not info_gpu['gpu_detectada']:
            return jsonify({
                'error': 'No se detectó GPU NVIDIA',
                'info': info_gpu
            }), 400
    
    try:
        resultado = buscador.cambiar_modo(modo)
        return jsonify({
            'success': True,
            'modo': resultado['modo'],
            'device': resultado['device'],
            'mensaje': f"✅ Ahora usando {'GPU' if modo == 'gpu' else 'CPU'}"
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/gpu/config', methods=['GET'])
def api_obtener_config_gpu():
    """Obtiene la configuración actual de GPU"""
    return jsonify(cargar_config_gpu())


@app.route('/api/limpiar_indice', methods=['POST'])
def api_limpiar_indice():
    """Elimina todos los índices para empezar desde cero"""
    try:
        import shutil
        
        ruta_indice = config.RUTA_INDICE
        
        if os.path.exists(ruta_indice):
            # Limpiar archivos del índice
            archivos_eliminados = []
            for archivo in os.listdir(ruta_indice):
                ruta_archivo = os.path.join(ruta_indice, archivo)
                os.remove(ruta_archivo)
                archivos_eliminados.append(archivo)
            
            # Recargar buscador (vacío)
            buscador.metadata = []
            buscador.index_faiss = None
            buscador.bm25 = None
            
            return jsonify({
                'success': True,
                'archivos_eliminados': archivos_eliminados,
                'mensaje': '✅ Índice limpiado correctamente'
            })
        else:
            return jsonify({
                'success': True,
                'mensaje': '⚠️ No había índice que limpiar'
            })
            
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/tipos', methods=['GET'])
def api_tipos():
    """Retorna estadísticas por tipo de documento"""
    if not buscador.metadata:
        return jsonify({})
    
    from collections import Counter
    tipos = Counter(m['tipo'] for m in buscador.metadata)
    
    return jsonify(dict(tipos))


if __name__ == '__main__':
    # Inicializar sistema antes de arrancar
    inicializar_sistema()
    
    print("🚀 Iniciando servidor de búsqueda IA...")
    print(f"📂 Carpetas indexadas: {len(config.CARPETAS_RAIZ) if config else 0}")
    
    # Mostrar info de GPU
    info_gpu = detectar_gpu_nvidia()
    deps_gpu = verificar_dependencias_gpu()
    config_gpu = cargar_config_gpu()
    
    if info_gpu['gpu_detectada']:
        print(f"🎮 GPU detectada: {info_gpu['nombre_gpu']}")
        if info_gpu['vram_mb']:
            print(f"   VRAM: {info_gpu['vram_mb']} MB")
        if info_gpu['driver_version']:
            print(f"   Driver: {info_gpu['driver_version']}")
        
        if deps_gpu['completo']:
            print(f"   ✅ Dependencias GPU: Instaladas")
            if config_gpu.get('modo') == 'gpu':
                print(f"   ⚡ Modo actual: GPU activa")
            else:
                print(f"   💻 Modo actual: CPU (puedes activar GPU desde la interfaz)")
        else:
            print(f"   ⚠️ Dependencias GPU: No instaladas")
            print(f"      - torch CUDA: {'✅' if deps_gpu['torch_cuda'] else '❌'}")
            print(f"      - sentence-transformers: {'✅' if deps_gpu['sentence_transformers'] else '❌'}")
            print(f"   💡 Usa el botón 'Instalar GPU' en la interfaz")
    else:
        print("🎮 GPU: No detectada (usando CPU)")
    
    print("\n" + "="*60)
    print("✅ SERVIDOR LISTO")
    print("="*60 + "\n")
    
    print("🌐 Servidor corriendo en http://localhost:5001")
    print("\nEndpoints disponibles:")
    print("  POST /api/buscar           - Búsqueda híbrida")
    print("  POST /api/actualizar_indice - Actualizar índice")
    print("  GET  /api/estado           - Estado del sistema")
    print("  GET  /api/gpu/detectar     - Detectar GPU")
    print("  POST /api/gpu/instalar     - Instalar deps GPU")
    print("  POST /api/gpu/activar      - Cambiar modo CPU/GPU")
    print("  POST /api/limpiar_indice   - Limpiar índice")
    print("\nPresiona CTRL+C para detener\n")
    
    # Usar waitress en lugar de Flask dev server (más estable con CUDA)
    try:
        from waitress import serve
        serve(app, host='127.0.0.1', port=5001, threads=4)
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error al iniciar servidor: {e}\n")
        import traceback
        traceback.print_exc()
