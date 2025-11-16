# Examinator - Sistema de Extracción y Exámenes con IA

Sistema completo para extraer texto de PDFs y generar exámenes inteligentes con evaluación automática usando IA local.

## Características

### 1. Extracción de Texto (examinator.py)
- Extrae texto de PDFs y archivos de texto
- Limpieza y normalización de texto configurable
- División automática en secciones
- Guardado organizado por fecha
- Soporte para PDFs largos con feedback de progreso

### 2. Generación de Exámenes (examinator_interactivo.py)
- Genera exámenes usando IA local (llama-cpp-python)
- Tipos de preguntas:
  - **Opción múltiple**: 4 opciones (A, B, C, D)
  - **Respuesta corta**: 2-4 líneas
  - **Desarrollo**: Análisis profundo
- Evaluación automática con feedback
- Guarda resultados con calificación

## Instalación

```powershell
# Clonar o descargar el proyecto
cd Examinator

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

### Paso 1: Extraer texto del PDF

```powershell
# Extracción con guardado automático organizado
python examinator.py "ruta/al/documento.pdf" --auto-save -v

# Extracción sin limpieza (preserva formato original)
python examinator.py "documento.pdf" --auto-save --sin-limpiar

# Extracción manual a ruta específica
python examinator.py "documento.pdf" -o "salida.txt"
```

**El archivo se guardará en**: `extracciones/YYYY-MM-DD/nombre_documento.txt`

### Paso 2: Generar y tomar examen

#### Sin modelo IA (modo ejemplo):
```powershell
python examinator_interactivo.py "extracciones/2025-11-16/mi_documento.txt"
```

#### Con modelo IA local:
Primero descarga un modelo GGUF (por ejemplo, de Hugging Face):
- [Llama 3.2 3B](https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF)
- [Mistral 7B](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF)

```powershell
# Con modelo IA (mejores preguntas y evaluación)
python examinator_interactivo.py "extracciones/2025-11-16/mi_documento.txt" --modelo "ruta/al/modelo.gguf"

# Personalizar número de preguntas
python examinator_interactivo.py "documento.txt" --modelo "modelo.gguf" --num-multiple 10 --num-corta 5 --num-desarrollo 3

# Guardar examen generado para reutilizar
python examinator_interactivo.py "documento.txt" --modelo "modelo.gguf" --guardar-examen "mi_examen.json"

# Cargar examen previamente generado
python examinator_interactivo.py "documento.txt" --cargar-examen "mi_examen.json"
```

### Flujo completo de ejemplo:

```powershell
# 1. Extraer PDF
python examinator.py "C:\Mis Documentos\paper_cientifico.pdf" --auto-save -v

# 2. Generar y tomar examen
python examinator_interactivo.py "extracciones/2025-11-16/paper_cientifico.txt" --modelo "llama-3.2-3B.gguf" --num-multiple 8 --num-corta 4 --num-desarrollo 2
```

## Estructura del Proyecto

```
Examinator/
├── examinator.py              # Extractor de texto de PDFs
├── examinator_interactivo.py  # Sistema interactivo de exámenes
├── generador_examenes.py      # Motor de generación y evaluación
├── test_pdf.py               # Utilidad de prueba
├── requirements.txt          # Dependencias
├── extracciones/             # PDFs extraídos (organizado por fecha)
│   └── 2025-11-16/
│       ├── documento1.txt
│       └── resultados/       # Resultados de exámenes
│           └── resultado_20251116_143022.txt
└── README.md
```

## Opciones Avanzadas

### Examinator.py

```powershell
# Ver ayuda completa
python examinator.py --help

# Opciones principales:
--auto-save              # Guardar automáticamente en carpeta organizada
-o, --output            # Ruta específica de salida
-v, --verbose           # Mostrar progreso detallado
--sin-limpiar          # No aplicar limpieza de texto
--limpieza-agresiva    # Unir líneas de párrafos
-s, --secciones        # Dividir en secciones por títulos
```

### Examinator_interactivo.py

```powershell
# Ver ayuda completa
python examinator_interactivo.py --help

# Opciones principales:
--modelo                # Ruta al modelo GGUF (opcional)
--num-multiple N        # Preguntas de opción múltiple (default: 5)
--num-corta N          # Preguntas de respuesta corta (default: 3)
--num-desarrollo N     # Preguntas de desarrollo (default: 2)
--guardar-examen       # Guardar examen en JSON
--cargar-examen        # Cargar examen desde JSON
```

## Dependencias

- `pypdf` - Extracción de texto de PDFs
- `llama-cpp-python` - Ejecución de modelos LLM locales
- Python 3.8+

## Notas

- Los modelos GGUF más pequeños (3B-7B parámetros) funcionan bien para generar preguntas
- Se recomienda al menos 8GB RAM para modelos de 7B
- Sin modelo IA, el sistema genera preguntas de ejemplo básicas
- Los resultados se guardan automáticamente en la carpeta `resultados/`

## Troubleshooting

**"No module named pypdf"**: Activa el entorno virtual y ejecuta `pip install pypdf`

**"Modelo no cargado"**: Verifica la ruta al archivo .gguf y que tengas suficiente RAM

**"PDF vacío"**: Algunos PDFs son imágenes escaneadas sin texto extraíble (requieren OCR)

## Autor

Sistema desarrollado con GitHub Copilot

## Licencia

MIT

Pequeña utilidad para extraer texto de archivos PDF o TXT.

## Requisitos
- Python 3.9+
- Dependencias Python: `pypdf`

Instala dependencias (PowerShell):

```pwsh
# Opcional: crear y activar un entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
python -m pip install -r requirements.txt
# Si tu sistema usa el lanzador de Windows, puedes usar:
# py -m pip install -r requirements.txt
```

## Uso
Desde la carpeta del proyecto:

```pwsh
# Abrir selector de archivos (sin argumentos)
python examinator.py

# Mostrar el texto por pantalla (vía argumentos)
python examinator.py ruta\al\archivo.pdf
python examinator.py ruta\al\archivo.txt

# Guardar el texto en un archivo de salida
python examinator.py ruta\al\archivo.pdf -o salida.txt

# Alternativa con el lanzador de Windows
py examinator.py ruta\al\archivo.pdf -o salida.txt
```

## Notas
- Para PDF se usa `pypdf`. La extracción depende de cómo esté creado el PDF.
- Para TXT se asume codificación UTF-8.
- Extensiones soportadas: `.pdf`, `.txt` (también `.log`, `.md`).
