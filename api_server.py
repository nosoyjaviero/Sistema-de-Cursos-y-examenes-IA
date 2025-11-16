"""
API Backend para Examinator Web
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import List, Optional
import json
import shutil
from datetime import datetime

from examinator import obtener_texto
from generador_examenes import GeneradorExamenes, PreguntaExamen, guardar_examen
from cursos_db import CursosDatabase

app = FastAPI(title="Examinator API")

# Inicializar gestor de carpetas
cursos_db = CursosDatabase("extracciones")

# Configurar CORS para permitir peticiones desde React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estado global
config_path = Path("config.json")
generador_actual = None


def cargar_config():
    """Carga la configuración guardada"""
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"modelo_path": None}


def guardar_config(config: dict):
    """Guarda la configuración"""
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


@app.get("/")
async def root():
    return {"message": "Examinator API", "version": "1.0"}


@app.get("/api/modelos")
async def listar_modelos():
    """Lista todos los modelos disponibles"""
    modelos_dir = Path("modelos")
    modelos_dir.mkdir(exist_ok=True)
    
    modelos = []
    for archivo in modelos_dir.glob("*.gguf"):
        tamaño = archivo.stat().st_size / (1024 * 1024 * 1024)  # GB
        modelos.append({
            "nombre": archivo.stem,
            "ruta": str(archivo),
            "tamaño_gb": round(tamaño, 2)
        })
    
    return {"modelos": modelos}


@app.get("/api/config")
async def obtener_config():
    """Obtiene la configuración actual"""
    return cargar_config()


@app.post("/api/config")
async def actualizar_config(config: dict):
    """Actualiza la configuración"""
    guardar_config(config)
    
    # Recargar generador con nuevo modelo
    global generador_actual
    if config.get("modelo_path"):
        try:
            generador_actual = GeneradorExamenes(modelo_path=config["modelo_path"])
            return {"message": "Configuración actualizada y modelo cargado", "success": True}
        except Exception as e:
            return {"message": f"Error al cargar modelo: {str(e)}", "success": False}
    
    return {"message": "Configuración actualizada", "success": True}


@app.post("/api/extraer-pdf")
async def extraer_pdf(file: UploadFile = File(...), carpeta: str = Form("")):
    """Extrae texto de un PDF subido y lo guarda en la carpeta especificada"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
    
    # Guardar archivo temporalmente
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    temp_path = temp_dir / file.filename
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Extraer texto
        texto = obtener_texto(str(temp_path), sin_limpiar=False, agresivo=False, verbose=False)
        
        # Determinar carpeta de destino
        if carpeta:
            carpeta_destino = Path("extracciones") / carpeta
        else:
            # Si no se especifica carpeta, usar la raíz de extracciones
            carpeta_destino = Path("extracciones")
        
        carpeta_destino.mkdir(parents=True, exist_ok=True)
        
        nombre_limpio = temp_path.stem.replace(' ', '_')
        archivo_salida = carpeta_destino / f"{nombre_limpio}.txt"
        
        # Si ya existe, agregar número
        contador = 1
        while archivo_salida.exists():
            archivo_salida = carpeta_destino / f"{nombre_limpio}_{contador}.txt"
            contador += 1
        
        archivo_salida.write_text(texto, encoding='utf-8')
        
        return {
            "success": True,
            "mensaje": "PDF extraído exitosamente",
            "archivo": str(archivo_salida.relative_to(Path("extracciones"))),
            "ruta_completa": str(archivo_salida),
            "caracteres": len(texto),
            "palabras": len(texto.split()),
            "carpeta": carpeta or "raíz"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al extraer PDF: {str(e)}")
    
    finally:
        # Limpiar archivo temporal
        if temp_path.exists():
            temp_path.unlink()


@app.get("/api/documentos")
async def listar_documentos():
    """Lista todos los documentos extraídos"""
    extracciones_dir = Path("extracciones")
    if not extracciones_dir.exists():
        return {"documentos": []}
    
    documentos = []
    for carpeta_fecha in sorted(extracciones_dir.iterdir(), reverse=True):
        if carpeta_fecha.is_dir():
            for archivo in carpeta_fecha.glob("*.txt"):
                if archivo.parent.name == "resultados":
                    continue
                
                documentos.append({
                    "nombre": archivo.stem,
                    "ruta": str(archivo),
                    "fecha": carpeta_fecha.name,
                    "tamaño_kb": round(archivo.stat().st_size / 1024, 2)
                })
    
    return {"documentos": documentos}


# ========== ENDPOINTS DE NAVEGACIÓN DE CARPETAS ==========

@app.get("/api/carpetas")
async def listar_carpetas(ruta: str = ""):
    """Lista todas las carpetas en una ruta específica"""
    try:
        carpetas = cursos_db.listar_carpetas(ruta)
        documentos = cursos_db.listar_documentos(ruta)
        return {
            "ruta_actual": ruta,
            "carpetas": carpetas,
            "documentos": documentos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/carpetas")
async def crear_carpeta(datos: dict):
    """Crea una nueva carpeta"""
    ruta_padre = datos.get("ruta_padre", "")
    nombre = datos.get("nombre")
    
    if not nombre:
        raise HTTPException(status_code=400, detail="El nombre de la carpeta es requerido")
    
    try:
        resultado = cursos_db.crear_carpeta(ruta_padre, nombre)
        return {"success": True, **resultado}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/carpetas")
async def eliminar_carpeta(ruta: str, forzar: bool = False):
    """Elimina una carpeta (forzar=true elimina con contenido)"""
    try:
        if cursos_db.eliminar_carpeta(ruta, forzar=forzar):
            return {"success": True, "mensaje": "Carpeta eliminada"}
        raise HTTPException(status_code=404, detail="Carpeta no encontrada")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/carpetas/mover")
async def mover_carpeta(datos: dict):
    """Mueve una carpeta a otra ubicación"""
    ruta_origen = datos.get("ruta_origen")
    ruta_destino = datos.get("ruta_destino", "")
    
    if not ruta_origen:
        raise HTTPException(status_code=400, detail="La ruta de origen es requerida")
    
    try:
        resultado = cursos_db.mover_carpeta(ruta_origen, ruta_destino)
        return {"success": True, **resultado}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/documentos")
async def eliminar_documento(ruta: str):
    """Elimina un documento"""
    try:
        if cursos_db.eliminar_documento(ruta):
            return {"success": True, "mensaje": "Documento eliminado"}
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/arbol")
async def obtener_arbol(ruta: str = "", profundidad: int = 3):
    """Obtiene el árbol completo de carpetas y documentos"""
    try:
        arbol = cursos_db.obtener_arbol(ruta, max_depth=profundidad)
        return arbol
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/buscar")
async def buscar_documentos(q: str):
    """Busca documentos por nombre"""
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="La búsqueda debe tener al menos 2 caracteres")
    
    try:
        resultados = cursos_db.buscar_documentos(q)
        return {"query": q, "resultados": resultados, "total": len(resultados)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documentos/contenido")
async def obtener_contenido_documento(ruta: str):
    """Obtiene el contenido de un documento"""
    try:
        contenido = cursos_db.obtener_contenido_documento(ruta)
        return contenido
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generar-examen")
async def generar_examen(datos: dict):
    """Genera un examen basado en un documento"""
    global generador_actual
    
    documento_path = datos.get("documento_path")
    num_multiple = datos.get("num_multiple", 5)
    num_corta = datos.get("num_corta", 3)
    num_desarrollo = datos.get("num_desarrollo", 2)
    
    if not documento_path:
        raise HTTPException(status_code=400, detail="Falta la ruta del documento")
    
    # Leer documento
    doc_path = Path(documento_path)
    if not doc_path.exists():
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    with open(doc_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Cargar o crear generador
    if generador_actual is None:
        config = cargar_config()
        modelo_path = config.get("modelo_path")
        generador_actual = GeneradorExamenes(modelo_path=modelo_path)
    
    # Generar preguntas
    num_preguntas = {
        'multiple': num_multiple,
        'corta': num_corta,
        'desarrollo': num_desarrollo
    }
    
    preguntas = generador_actual.generar_examen(contenido, num_preguntas)
    
    # Convertir a formato JSON
    preguntas_json = [p.to_dict() for p in preguntas]
    
    return {
        "success": True,
        "preguntas": preguntas_json,
        "total_preguntas": len(preguntas),
        "puntos_totales": sum(p['puntos'] for p in preguntas_json)
    }


@app.post("/api/evaluar-examen")
async def evaluar_examen(datos: dict):
    """Evalúa las respuestas de un examen"""
    global generador_actual
    
    if generador_actual is None:
        config = cargar_config()
        modelo_path = config.get("modelo_path")
        generador_actual = GeneradorExamenes(modelo_path=modelo_path)
    
    preguntas_data = datos.get("preguntas", [])
    respuestas = datos.get("respuestas", {})
    
    resultados = []
    puntos_obtenidos = 0
    puntos_totales = 0
    
    for i, pregunta_dict in enumerate(preguntas_data):
        pregunta = PreguntaExamen.from_dict(pregunta_dict)
        respuesta_usuario = respuestas.get(str(i), "")
        
        puntos, feedback = generador_actual.evaluar_respuesta(pregunta, respuesta_usuario)
        
        puntos_obtenidos += puntos
        puntos_totales += pregunta.puntos
        
        resultados.append({
            "pregunta": pregunta.pregunta,
            "tipo": pregunta.tipo,
            "respuesta_usuario": respuesta_usuario,
            "puntos": puntos,
            "puntos_maximos": pregunta.puntos,
            "feedback": feedback
        })
    
    # Guardar resultados
    documento_path = datos.get("documento_path")
    if documento_path:
        doc_path = Path(documento_path)
        carpeta_resultados = doc_path.parent / "resultados"
        carpeta_resultados.mkdir(exist_ok=True)
        
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_resultado = carpeta_resultados / f"resultado_{fecha}.json"
        
        resultado_completo = {
            "fecha": datetime.now().isoformat(),
            "documento": str(doc_path),
            "puntos_obtenidos": puntos_obtenidos,
            "puntos_totales": puntos_totales,
            "porcentaje": (puntos_obtenidos / puntos_totales * 100) if puntos_totales > 0 else 0,
            "resultados": resultados
        }
        
        with open(archivo_resultado, 'w', encoding='utf-8') as f:
            json.dump(resultado_completo, f, ensure_ascii=False, indent=2)
    
    return {
        "success": True,
        "puntos_obtenidos": puntos_obtenidos,
        "puntos_totales": puntos_totales,
        "porcentaje": (puntos_obtenidos / puntos_totales * 100) if puntos_totales > 0 else 0,
        "resultados": resultados
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor API de Examinator...")
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
