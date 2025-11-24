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
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pickle
import numpy as np
from typing import List, Dict, Tuple, Optional
import faiss
from sentence_transformers import SentenceTransformer
import torch
from rank_bm25 import BM25Okapi
from threading import Lock, Semaphore
import time

from buscador_ia import ConfigBuscador, IndexadorLocal


# ===================================
# BUSCADOR
# ===================================

class BuscadorHibrido:
    """Buscador que combina búsqueda semántica (FAISS) + keywords (BM25)"""
    
    def __init__(self, config: ConfigBuscador):
        self.config = config
        self.modelo = None
        self.index_faiss = None
        self.metadata = []
        self.bm25 = None
        self.device = None
        
        # Control de concurrencia
        self.lock = Lock()
        self.semaforo = Semaphore(config.MAX_CONSULTAS_CONCURRENTES)
        
        self.cargar_indices()
    
    def cargar_indices(self):
        """Carga índices FAISS, metadata y BM25"""
        print("📂 Cargando índices...")
        
        ruta_faiss = os.path.join(self.config.RUTA_INDICE, self.config.ARCHIVO_FAISS)
        ruta_metadata = os.path.join(self.config.RUTA_INDICE, self.config.ARCHIVO_METADATA)
        ruta_bm25 = os.path.join(self.config.RUTA_INDICE, self.config.ARCHIVO_BM25)
        
        # FAISS
        if os.path.exists(ruta_faiss):
            self.index_faiss = faiss.read_index(ruta_faiss)
            print(f"✅ Índice FAISS cargado: {self.index_faiss.ntotal} vectores")
        else:
            print("⚠️ No existe índice FAISS")
        
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
        
        print(f"🔧 Cargando modelo {self.config.MODELO_EMBEDDINGS}...")
        
        # Intentar usar GPU con PyTorch/CUDA
        if self.config.USAR_GPU and torch.cuda.is_available():
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
    """Retorna estado del sistema"""
    gpu_disponible = torch.cuda.is_available() if torch else False
    gpu_nombre = torch.cuda.get_device_name(0) if gpu_disponible else None
    
    return jsonify({
        'total_chunks': len(buscador.metadata) if buscador.metadata else 0,
        'total_archivos': len(set(m['ruta'] for m in buscador.metadata)) if buscador.metadata else 0,
        'modelo': config.MODELO_EMBEDDINGS,
        'gpu_disponible': gpu_disponible,
        'gpu_nombre': gpu_nombre,
        'carpetas_indexadas': config.CARPETAS_RAIZ
    })


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
    print(f"📂 Carpetas indexadas: {len(config.CARPETAS_RAIZ)}")
    
    if torch.cuda.is_available():
        print(f"🎮 GPU: Sí - {torch.cuda.get_device_name(0)}")
    else:
        print("🎮 GPU: No disponible (usando CPU)")
    
    print("\n" + "="*60)
    print("✅ SERVIDOR LISTO")
    print("="*60 + "\n")
    
    print("🌐 Servidor corriendo en http://localhost:5001")
    print("Presiona CTRL+C para detener\n")
    
    # Usar waitress en lugar de Flask dev server (más estable con CUDA)
    try:
        from waitress import serve
        serve(app, host='0.0.0.0', port=5001, threads=4)
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error al iniciar servidor: {e}\n")
        import traceback
        traceback.print_exc()
