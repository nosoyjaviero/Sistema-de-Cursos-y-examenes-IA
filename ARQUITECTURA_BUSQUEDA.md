# 🏗️ Arquitectura del Sistema de Búsqueda IA

> Documentación técnica del sistema de búsqueda híbrida con GPU

---

## 📊 Visión General

El sistema combina **búsqueda semántica** (basada en significado) con **búsqueda por palabras clave** (BM25) para obtener resultados más relevantes.

```
┌─────────────────────────────────────────────────────────────┐
│                    USUARIO                                   │
│              (Interfaz React - Puerto 5174)                  │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP POST /api/buscar
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              API REST (Flask + Waitress)                     │
│                   Puerto 5001                                │
│  • /api/buscar - Búsqueda híbrida                           │
│  • /api/actualizar_indice - Reindexar                       │
│  • /api/estado - Estado del sistema                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              BUSCADOR HÍBRIDO                                │
│  ┌─────────────────┐         ┌──────────────────┐          │
│  │ Búsqueda        │   70%   │ Búsqueda         │   30%   │
│  │ Semántica       │ ─────►  │ Palabras Clave   │ ─────►  │
│  │ (FAISS)         │         │ (BM25)           │         │
│  └────────┬────────┘         └────────┬─────────┘         │
│           │                           │                    │
│           │    Combinación de scores  │                    │
│           └────────────┬──────────────┘                    │
│                        ▼                                    │
│              Resultados ordenados                           │
└─────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  EMBEDDINGS (GPU)                            │
│              sentence-transformers                           │
│           BAAI/bge-small-en-v1.5                            │
│         NVIDIA RTX 4050 (CUDA 11.8)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧩 Componentes Principales

### 1. Frontend (React + Vite)

**Archivo:** `examinator-web/src/App.jsx`

**Funciones clave:**
- `buscarConIA(query)` - Envía consulta a backend
- `actualizarIndice(forzar)` - Actualiza/recrea índices
- `extraerInfoRelevante(resultado)` - Extrae metadata de resultados
- `cargarEstadoIndice()` - Obtiene estado del sistema

**Puerto:** 5174

**Tecnologías:**
- React 18
- Vite (dev server con HMR)
- Fetch API para comunicación con backend

### 2. Backend API (Flask + Waitress)

**Archivo:** `api_buscador.py`

**Endpoints:**

```python
POST /api/buscar
{
  "query": "texto a buscar",
  "max_resultados": 10,
  "tipo_archivo": "todos"  # o "nota", "flashcard", etc.
}

Response:
{
  "resultados": [
    {
      "nombre_archivo": "archivo.txt",
      "ruta": "/path/to/archivo.txt",
      "score": 0.85,
      "contenido": "snippet del contenido...",
      "tipo": "nota"
    }
  ],
  "total": 5,
  "tiempo": 0.577
}
```

```python
POST /api/actualizar_indice
{
  "forzar": false  # true = reindexar todo
}
```

```python
GET /api/estado
Response:
{
  "gpu_disponible": true,
  "total_chunks": 27,
  "archivos_indexados": 3
}
```

**Servidor:** Waitress (WSGI)
- Más estable que Flask dev server en Windows
- No se cierra inesperadamente con CUDA
- Puerto: 5001

### 3. Motor de Búsqueda (buscador_ia.py)

**Clase principal:** `BuscadorHibrido`

**Componentes:**

#### a) Indexador (IndexadorLocal)

```python
class IndexadorLocal:
    def indexar_archivos(rutas_archivos):
        # 1. Lee archivos (TXT, PDF, DOCX, JSON)
        # 2. Divide en chunks (800 chars, 200 overlap)
        # 3. Genera embeddings (GPU)
        # 4. Crea índices FAISS y BM25
```

**Chunking:**
- Tamaño: 800 caracteres
- Overlap: 200 caracteres
- Motivo: Balance entre contexto y precisión

#### b) Búsqueda Semántica (FAISS)

```python
def buscar_semantico(query, k=10):
    # 1. Genera embedding de la query (GPU)
    embedding = model.encode([query], device='cuda')
    
    # 2. Búsqueda en FAISS (Inner Product)
    scores, indices = faiss_index.search(embedding, k)
    
    # 3. Retorna chunks más similares
    return resultados
```

**Índice:** FAISS IndexFlatIP (Inner Product)
- Ventaja: Rápido para <100k vectores
- Dimensión: 384 (modelo bge-small)
- Métrica: Similitud coseno (normalizado)

#### c) Búsqueda por Palabras Clave (BM25)

```python
def buscar_keywords(query, k=10):
    # 1. Tokeniza query
    tokens = query.lower().split()
    
    # 2. BM25 scoring
    scores = bm25.get_scores(tokens)
    
    # 3. Retorna top-k
    return resultados
```

**Algoritmo:** BM25 Okapi
- Mejora de TF-IDF
- Considera frecuencia de términos y longitud del documento

#### d) Combinación Híbrida

```python
def buscar(query, max_resultados=10):
    # 1. Búsqueda semántica
    sem_results = buscar_semantico(query, k=20)
    
    # 2. Búsqueda keywords
    kw_results = buscar_keywords(query, k=20)
    
    # 3. Combinar scores (70% semántica + 30% keywords)
    final_scores = 0.7 * sem_scores + 0.3 * kw_scores
    
    # 4. Ordenar y retornar top-k
    return sorted(final_scores)[:max_resultados]
```

**Pesos configurables:**
- `peso_semantico = 0.7` - Prioriza significado
- `peso_keywords = 0.3` - Asegura matches exactos

---

## 🚀 Flujo de Ejecución

### Indexación (crear_indice_inicial.py)

```
1. Escanear carpetas (cursos/, notas/, flashcards/, examenes/)
   ↓
2. Leer archivos (.txt, .json, .pdf, .docx)
   ↓
3. Dividir en chunks (800 chars con 200 overlap)
   ↓
4. Generar embeddings en GPU
   sentence-transformers (BAAI/bge-small-en-v1.5)
   ↓
5. Crear índice FAISS
   IndexFlatIP (Inner Product)
   ↓
6. Crear índice BM25
   rank-bm25
   ↓
7. Guardar en disco
   indices_busqueda/
   ├── faiss_index.bin
   ├── bm25_index.pkl
   └── chunks.json
```

**Tiempo:** ~30 segundos para 100 archivos

### Búsqueda (Runtime)

```
Usuario escribe query en frontend
   ↓
POST /api/buscar {"query": "...", "max_resultados": 10}
   ↓
Backend recibe query
   ↓
┌─────────────────────┬────────────────────┐
│                     │                    │
│ Búsqueda Semántica  │  Búsqueda BM25     │
│ 1. Encode query     │  1. Tokenizar      │
│ 2. FAISS search     │  2. BM25 scoring   │
│ 3. Scores 0-1       │  3. Scores 0-1     │
│                     │                    │
└──────────┬──────────┴──────────┬─────────┘
           │                     │
           │   Combinar scores   │
           │   (0.7 * sem + 0.3 * kw)
           └──────────┬──────────┘
                      ↓
              Ordenar por score
                      ↓
          Retornar top-k resultados
                      ↓
      Frontend muestra resultados
      con metadata extraída
```

**Tiempo:** 0.5-1 segundo con GPU

---

## 🎯 Modelo de Embeddings

**Nombre:** BAAI/bge-small-en-v1.5

**Características:**
- Dimensión: 384
- Tamaño: ~130MB
- Velocidad: ~1000 textos/segundo (GPU)
- Idioma: Inglés (funciona bien con español)

**Descarga automática:**
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('BAAI/bge-small-en-v1.5', device='cuda')
# Se descarga en: ~/.cache/huggingface/
```

**Alternativas:**
- `all-MiniLM-L6-v2` - Más pequeño (~80MB)
- `paraphrase-multilingual-MiniLM-L12-v2` - Multilingüe
- `bge-large-en-v1.5` - Más preciso pero más lento

---

## 💾 Almacenamiento

### Estructura de Índices

```
indices_busqueda/
├── faiss_index.bin        # Vectores FAISS (binario)
├── bm25_index.pkl         # Modelo BM25 (pickle)
└── chunks.json            # Metadata de chunks
```

**chunks.json:**
```json
[
  {
    "chunk_id": 0,
    "texto": "Contenido del chunk...",
    "archivo": "/ruta/al/archivo.txt",
    "nombre_archivo": "archivo.txt",
    "tipo": "nota",
    "inicio": 0,
    "fin": 800
  }
]
```

**Tamaño estimado:**
- 100 archivos → ~50 chunks → ~20KB (JSON) + ~200KB (FAISS)
- 1000 archivos → ~500 chunks → ~200KB (JSON) + ~2MB (FAISS)

---

## ⚡ Optimizaciones

### GPU Acceleration

```python
# Verificar GPU
import torch
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Cargar modelo en GPU
model = SentenceTransformer(modelo_name, device=device)

# Generar embeddings en GPU
embeddings = model.encode(textos, device=device, show_progress_bar=True)
```

**Speedup:** 5-10x vs CPU

### Caché de Embeddings

Los embeddings se generan una vez durante indexación y se reutilizan en búsquedas.

### Batch Processing

```python
# En vez de:
for texto in textos:
    embedding = model.encode([texto])

# Hacer:
embeddings = model.encode(textos, batch_size=32)
```

---

## 🔧 Configuración

**Archivo:** `buscador_ia.py`

```python
class ConfigBuscador:
    modelo_embeddings = 'BAAI/bge-small-en-v1.5'
    chunk_size = 800
    chunk_overlap = 200
    max_resultados = 10
    carpetas = ['cursos', 'notas', 'flashcards', 'examenes']
    extensiones = ['.txt', '.json', '.pdf', '.docx']
```

**Ajustes recomendados:**

| Parámetro | Valor por defecto | Para más precisión | Para más velocidad |
|-----------|-------------------|--------------------|--------------------|
| chunk_size | 800 | 500 | 1200 |
| chunk_overlap | 200 | 300 | 100 |
| peso_semantico | 0.7 | 0.8 | 0.5 |
| peso_keywords | 0.3 | 0.2 | 0.5 |

---

## 🐛 Debugging

### Ver logs del servidor

```powershell
# Ventana donde corre INICIAR_BUSCADOR_GPU.bat
# Muestra:
Cargando modelo BAAI/bge-small-en-v1.5...
Modelo cargado en: cuda
GPU disponible: NVIDIA GeForce RTX 4050 Laptop GPU
Indices cargados: 27 chunks
Running on http://0.0.0.0:5001
```

### Probar API directamente

```powershell
Invoke-WebRequest -Method POST `
  -Uri "http://localhost:5001/api/buscar" `
  -ContentType "application/json" `
  -Body '{"query":"test","max_resultados":5}' | 
  Select-Object -ExpandProperty Content
```

### Verificar índices

```python
import faiss
import pickle

# FAISS
index = faiss.read_index('indices_busqueda/faiss_index.bin')
print(f"Total vectores: {index.ntotal}")

# BM25
with open('indices_busqueda/bm25_index.pkl', 'rb') as f:
    bm25 = pickle.load(f)
    print(f"Documentos: {len(bm25.corpus_size)}")
```

---

## 📈 Métricas de Rendimiento

**Hardware de referencia:** RTX 4050, 16GB RAM, SSD

| Operación | Tiempo | Notas |
|-----------|--------|-------|
| Indexar 100 archivos | ~30s | GPU |
| Primera búsqueda | ~5s | Carga modelo |
| Búsquedas siguientes | ~0.5s | GPU |
| Modo CPU | ~3-5s | Sin GPU |

---

## 🔒 Seguridad

- ✅ CORS limitado a localhost:5174
- ✅ No guarda queries del usuario
- ✅ Solo lee archivos locales
- ✅ No conexión a internet (excepto descarga modelo)

---

## 📚 Referencias

- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Sentence Transformers](https://www.sbert.net/)
- [BM25 Algorithm](https://en.wikipedia.org/wiki/Okapi_BM25)
- [PyTorch CUDA](https://pytorch.org/get-started/locally/)
