# Examinator

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
