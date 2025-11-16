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
from busqueda_web import buscar_y_resumir

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
    """Lista todos los modelos disponibles con información detallada"""
    modelos_dir = Path("modelos")
    modelos_dir.mkdir(exist_ok=True)
    
    # Información sobre diferentes tipos de modelos
    info_modelos = {
        "3B": {
            "parametros": "3 mil millones",
            "velocidad": "Muy rápida",
            "calidad": "Buena para tareas básicas",
            "ram_necesaria": "4-6 GB",
            "descripcion": "Ideal para respuestas rápidas y preguntas simples. Perfecto para equipos con recursos limitados."
        },
        "7B": {
            "parametros": "7 mil millones",
            "velocidad": "Rápida",
            "calidad": "Excelente balance calidad/velocidad",
            "ram_necesaria": "8-12 GB",
            "descripcion": "Mejor opción para uso general. Genera preguntas más elaboradas manteniendo buena velocidad."
        },
        "13B": {
            "parametros": "13 mil millones",
            "velocidad": "Media",
            "calidad": "Muy buena calidad",
            "ram_necesaria": "16-20 GB",
            "descripcion": "Para exámenes complejos que requieren razonamiento profundo y preguntas más sofisticadas."
        },
        "70B": {
            "parametros": "70 mil millones",
            "velocidad": "Lenta",
            "calidad": "Máxima calidad",
            "ram_necesaria": "32+ GB",
            "descripcion": "Calidad profesional para evaluaciones críticas. Requiere hardware potente."
        }
    }
    
    modelos = []
    for archivo in modelos_dir.glob("*.gguf"):
        tamaño = archivo.stat().st_size / (1024 * 1024 * 1024)  # GB
        nombre = archivo.stem
        
        # Detectar tamaño del modelo
        tamaño_modelo = "3B"
        for key in ["70B", "13B", "7B", "3B"]:
            if key in nombre.upper():
                tamaño_modelo = key
                break
        
        info = info_modelos.get(tamaño_modelo, {
            "parametros": "Desconocido",
            "velocidad": "Variable",
            "calidad": "A evaluar",
            "ram_necesaria": "Variable",
            "descripcion": "Modelo personalizado"
        })
        
        modelos.append({
            "nombre": nombre,
            "ruta": str(archivo),
            "tamaño_gb": round(tamaño, 2),
            "tamaño_modelo": tamaño_modelo,
            **info
        })
    
    return {"modelos": modelos}


@app.get("/api/modelos/disponibles")
async def listar_modelos_disponibles():
    """Lista modelos disponibles para descargar"""
    modelos_disponibles = [
        {
            "id": "llama-3.2-3b",
            "nombre": "Llama 3.2 3B Instruct",
            "archivo": "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
            "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
            "tamaño_gb": 1.88,
            "tamaño_modelo": "3B",
            "parametros": "3 mil millones",
            "velocidad": "Muy rápida",
            "calidad": "Buena para tareas básicas",
            "ram_necesaria": "4-6 GB",
            "descripcion": "Modelo pequeño y rápido, ideal para generar preguntas y evaluar respuestas. Perfecto para equipos con recursos limitados.",
            "recomendado": True,
            "requiere_auth": False
        },
        {
            "id": "llama-3.3-70b",
            "nombre": "Llama 3.3 70B Instruct",
            "archivo": "Llama-3.3-70B-Instruct-Q4_K_M.gguf",
            "url": "https://huggingface.co/bartowski/Llama-3.3-70B-Instruct-GGUF/resolve/main/Llama-3.3-70B-Instruct-Q4_K_M.gguf",
            "tamaño_gb": 40.2,
            "tamaño_modelo": "70B",
            "parametros": "70 mil millones",
            "velocidad": "Lenta",
            "calidad": "Calidad excepcional",
            "ram_necesaria": "48-64 GB",
            "descripcion": "El modelo más avanzado de Meta, liberado en diciembre 2024. Excelente razonamiento y generación de contenido educativo de la más alta calidad.",
            "recomendado": False,
            "requiere_auth": False
        },
        {
            "id": "qwen-2.5-7b",
            "nombre": "Qwen 2.5 7B Instruct",
            "archivo": "qwen2.5-7b-instruct-q4_k_m.gguf",
            "url": "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q4_k_m.gguf",
            "tamaño_gb": 4.4,
            "tamaño_modelo": "7B",
            "parametros": "7 mil millones",
            "velocidad": "Rápida",
            "calidad": "Excelente, especialmente multilingüe",
            "ram_necesaria": "8-12 GB",
            "descripcion": "De Alibaba Cloud, septiembre 2024. Excelente en español y múltiples idiomas. Muy bueno para contenido educativo y razonamiento.",
            "recomendado": True,
            "requiere_auth": False
        },
        {
            "id": "mistral-7b-v0.3",
            "nombre": "Mistral 7B Instruct v0.3",
            "archivo": "Mistral-7B-Instruct-v0.3-Q4_K_M.gguf",
            "url": "https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3-Q4_K_M.gguf",
            "tamaño_gb": 4.4,
            "tamaño_modelo": "7B",
            "parametros": "7 mil millones",
            "velocidad": "Rápida",
            "calidad": "Excelente balance",
            "ram_necesaria": "8-12 GB",
            "descripcion": "De Mistral AI, 2024. Modelo europeo con excelente rendimiento general y seguimiento de instrucciones precisas.",
            "recomendado": False,
            "requiere_auth": False
        },
        {
            "id": "phi-3-mini",
            "nombre": "Phi-3 Mini 3.8B Instruct",
            "archivo": "Phi-3-mini-4k-instruct-q4.gguf",
            "url": "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf",
            "tamaño_gb": 2.2,
            "tamaño_modelo": "3.8B",
            "parametros": "3.8 mil millones",
            "velocidad": "Muy rápida",
            "calidad": "Sorprendentemente buena para su tamaño",
            "ram_necesaria": "4-6 GB",
            "descripcion": "De Microsoft, mayo 2024. Modelo pequeño pero muy capaz, entrenado con datos de alta calidad. Ideal para equipos limitados.",
            "recomendado": False,
            "requiere_auth": False
        },
        {
            "id": "gemma-2-9b",
            "nombre": "Gemma 2 9B Instruct",
            "archivo": "gemma-2-9b-it-Q4_K_M.gguf",
            "url": "https://huggingface.co/bartowski/gemma-2-9b-it-GGUF/resolve/main/gemma-2-9b-it-Q4_K_M.gguf",
            "tamaño_gb": 5.4,
            "tamaño_modelo": "9B",
            "parametros": "9 mil millones",
            "velocidad": "Rápida",
            "calidad": "Excelente calidad",
            "ram_necesaria": "10-14 GB",
            "descripcion": "De Google DeepMind, junio 2024. Rendimiento excepcional y seguro. Excelente para tareas educativas complejas.",
            "recomendado": False,
            "requiere_auth": False
        },
        {
            "id": "llama-3.1-8b",
            "nombre": "Llama 3.1 8B Instruct",
            "archivo": "Llama-3.1-8B-Instruct-Q4_K_M.gguf",
            "url": "https://huggingface.co/bartowski/Llama-3.1-8B-Instruct-GGUF/resolve/main/Llama-3.1-8B-Instruct-Q4_K_M.gguf",
            "tamaño_gb": 4.92,
            "tamaño_modelo": "8B",
            "parametros": "8 mil millones",
            "velocidad": "Rápida",
            "calidad": "Excelente balance calidad/velocidad",
            "ram_necesaria": "8-12 GB",
            "descripcion": "De Meta, julio 2024. Modelo equilibrado con buen rendimiento general y capacidad de razonamiento.",
            "recomendado": False,
            "requiere_auth": False
        },
        {
            "id": "qwen-2.5-14b",
            "nombre": "Qwen 2.5 14B Instruct",
            "archivo": "qwen2.5-14b-instruct-q4_k_m.gguf",
            "url": "https://huggingface.co/Qwen/Qwen2.5-14B-Instruct-GGUF/resolve/main/qwen2.5-14b-instruct-q4_k_m.gguf",
            "tamaño_gb": 8.7,
            "tamaño_modelo": "14B",
            "parametros": "14 mil millones",
            "velocidad": "Media",
            "calidad": "Muy alta, excelente en español",
            "ram_necesaria": "16-20 GB",
            "descripcion": "De Alibaba Cloud, septiembre 2024. Versión más potente de Qwen 2.5, sobresaliente en múltiples idiomas y razonamiento complejo.",
            "recomendado": False,
            "requiere_auth": False
        }
    ]
    
    # Verificar cuáles ya están descargados
    modelos_dir = Path("modelos")
    modelos_dir.mkdir(exist_ok=True)
    
    archivos_descargados = {f.name for f in modelos_dir.glob("*.gguf")}
    
    for modelo in modelos_disponibles:
        modelo["descargado"] = modelo["archivo"] in archivos_descargados
    
    return {"modelos": modelos_disponibles}


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


@app.post("/api/chat")
async def chat_con_modelo(data: dict):
    """Endpoint para chatear con el modelo"""
    global generador_actual
    
    mensaje = data.get("mensaje", "").strip()
    if not mensaje:
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")
    
    # Verificar si hay modelo cargado
    config = cargar_config()
    if not config.get("modelo_path"):
        return {"respuesta": "❌ No hay modelo configurado. Ve a Configuración para seleccionar uno."}
    
    # Inicializar generador si no existe
    if generador_actual is None:
        try:
            generador_actual = GeneradorExamenes(modelo_path=config["modelo_path"])
        except Exception as e:
            return {"respuesta": f"❌ Error al cargar el modelo: {str(e)}"}
    
    try:
        # Usar el modelo para generar respuesta
        from llama_cpp import Llama
        
        # Crear instancia del modelo si no existe
        if not hasattr(generador_actual, 'llm') or generador_actual.llm is None:
            generador_actual.llm = Llama(
                model_path=config["modelo_path"],
                n_ctx=4096,  # Aumentado para mejor memoria (2x contexto)
                n_threads=6,  # Optimizado para mejor rendimiento
                verbose=False
            )
        
        # Preparar el contexto si existe
        contexto = data.get("contexto", None)
        buscar_web = data.get("buscar_web", False)
        mensaje_completo = mensaje
        system_prompt = "Eres un asistente educativo útil y amigable. Responde de manera clara y concisa en español."
        
        # Si se solicita búsqueda web
        if buscar_web:
            try:
                print(f"🌐 Realizando búsqueda web para: {mensaje}")
                resultado_busqueda = buscar_y_resumir(mensaje, max_resultados=3)
                print(f"✓ Búsqueda completada: {resultado_busqueda.get('exito', False)}")
                print(f"📊 Número de resultados: {resultado_busqueda.get('num_resultados', 0)}")
                print(f"📝 Resultados: {len(resultado_busqueda.get('resultados', []))} encontrados")
                
                if resultado_busqueda.get('exito', False) and resultado_busqueda.get('resultados'):
                    contexto_web = resultado_busqueda['resumen']
                    print(f"📄 Longitud del contexto web: {len(contexto_web)} caracteres")
                    print(f"📄 Primeros 200 caracteres del contexto: {contexto_web[:200]}...")
                    
                    system_prompt = "Eres un asistente que tiene acceso a información de internet. DEBES usar ÚNICAMENTE la información proporcionada de las búsquedas web para responder. NO inventes información ni uses conocimiento previo. Cita las fuentes cuando sea relevante."
                    mensaje_completo = f"""INFORMACIÓN DE BÚSQUEDA WEB:

{contexto_web}

---

PREGUNTA DEL USUARIO: {mensaje}

INSTRUCCIONES: Responde la pregunta usando SOLO la información de búsqueda web proporcionada arriba. Sé específico y menciona los datos encontrados."""
                    print(f"✅ Mensaje completo preparado, enviando al modelo...")
                else:
                    print(f"⚠️ No se encontraron resultados de búsqueda")
                    print(f"⚠️ Detalle del resultado: {resultado_busqueda}")
                    return {"respuesta": "🌐 No pude encontrar información actualizada en internet sobre ese tema. Por favor, intenta reformular tu pregunta o busca directamente en un navegador."}
            except Exception as e:
                print(f"❌ Error en búsqueda web: {e}")
                import traceback
                traceback.print_exc()
                return {"respuesta": f"🌐 Error al buscar en internet: {str(e)}. Por favor, intenta nuevamente."}
        
        # Si hay contexto de archivo
        elif contexto:
            # Limitar el contexto a un tamaño manejable (primeros 4000 caracteres)
            contexto_limitado = contexto[:4000] if len(contexto) > 4000 else contexto
            system_prompt = "Eres un asistente que analiza documentos. Responde basándote ÚNICAMENTE en el contenido del documento proporcionado."
            mensaje_completo = f"""DOCUMENTO:

---
{contexto_limitado}
---

PREGUNTA: {mensaje}

INSTRUCCIONES: Responde usando SOLO la información del documento."""
        
        # Construir historial de mensajes para el modelo
        historial = data.get("historial", [])
        messages = [{"role": "system", "content": system_prompt}]
        
        # Agregar historial previo (también en búsquedas web para mantener contexto)
        if historial:
            # Aumentar a últimos 20 mensajes (~10 intercambios) con contexto de 4096 tokens
            historial_reciente = historial[-20:]
            
            # En búsquedas web, solo incluir últimos 6 mensajes para dejar espacio al contenido web
            if buscar_web:
                historial_reciente = historial[-6:]
            # Con documentos, reducir a 4 mensajes para priorizar el documento
            elif contexto:
                historial_reciente = historial[-4:]
            
            for msg in historial_reciente:
                if msg.get('tipo') == 'usuario':
                    messages.append({"role": "user", "content": msg.get('texto', '')})
                elif msg.get('tipo') == 'asistente':
                    messages.append({"role": "assistant", "content": msg.get('texto', '')})
        
        # Agregar mensaje actual
        messages.append({"role": "user", "content": mensaje_completo})
        
        # Generar respuesta
        respuesta = generador_actual.llm.create_chat_completion(
            messages=messages,
            max_tokens=768,  # Aumentado para respuestas más completas
            temperature=0.7,
            top_p=0.9
        )
        
        texto_respuesta = respuesta['choices'][0]['message']['content']
        return {"respuesta": texto_respuesta}
        
    except Exception as e:
        return {"respuesta": f"❌ Error al generar respuesta: {str(e)}"}


@app.post("/api/buscar-web")
async def buscar_web_endpoint(data: dict):
    """Endpoint para realizar búsquedas en internet"""
    query = data.get("query", "").strip()
    max_resultados = data.get("max_resultados", 3)
    
    if not query:
        raise HTTPException(status_code=400, detail="Se requiere un término de búsqueda")
    
    try:
        resultado = buscar_y_resumir(query, max_resultados)
        return resultado
    except Exception as e:
        return {
            "exito": False,
            "mensaje": f"Error al buscar: {str(e)}",
            "resultados": []
        }


@app.post("/api/extraer-texto-simple")
async def extraer_texto_simple(file: UploadFile = File(...)):
    """Extrae texto de un PDF para usar como contexto en el chat"""
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
        
        # Limpiar archivo temporal
        temp_path.unlink()
        
        return {
            "texto": texto,
            "caracteres": len(texto),
            "nombre_archivo": file.filename
        }
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error al extraer texto: {str(e)}")


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


@app.put("/api/carpetas/renombrar")
async def renombrar_carpeta(data: dict):
    """Renombra una carpeta de cursos"""
    ruta_actual = data.get("ruta_actual", "").strip()
    nuevo_nombre = data.get("nuevo_nombre", "").strip()
    
    if not ruta_actual:
        raise HTTPException(status_code=400, detail="La ruta actual no puede estar vacía")
    
    if not nuevo_nombre:
        raise HTTPException(status_code=400, detail="El nuevo nombre no puede estar vacío")
    
    try:
        # Usar el método de base de datos para renombrar
        resultado = cursos_db.renombrar_carpeta(ruta_actual, nuevo_nombre)
        return {"success": True, **resultado}
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


# ========================================
# ENDPOINTS DE HISTORIAL DE CHATS
# ========================================

@app.get("/api/chats/historial")
async def listar_historial_chats():
    """Lista todos los chats guardados"""
    chats_dir = Path("chats_historial")
    chats_dir.mkdir(exist_ok=True)
    
    chats = []
    
    # Función auxiliar para procesar archivos de chat
    def procesar_chat(archivo, carpeta=""):
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
                chats.append({
                    "id": archivo.stem,
                    "nombre": data.get("nombre", "Sin nombre"),
                    "fecha": data.get("fecha", ""),
                    "num_mensajes": len(data.get("mensajes", [])),
                    "carpeta": carpeta
                })
        except Exception as e:
            print(f"Error al leer {archivo}: {e}")
    
    # Leer chats en la raíz
    for archivo in chats_dir.glob("*.json"):
        procesar_chat(archivo)
    
    # Leer chats en subcarpetas
    for carpeta in chats_dir.iterdir():
        if carpeta.is_dir():
            for archivo in carpeta.glob("*.json"):
                procesar_chat(archivo, carpeta.name)
    
    # Ordenar por fecha (más reciente primero)
    chats.sort(key=lambda x: x.get("fecha", ""), reverse=True)
    
    return {"chats": chats}


@app.post("/api/chats/guardar")
async def guardar_chat(data: dict):
    """Guarda un chat en el historial, opcionalmente en una carpeta"""
    chats_dir = Path("chats_historial")
    chats_dir.mkdir(exist_ok=True)
    
    # Obtener carpeta si existe
    carpeta = data.get("carpeta", "").strip()
    if carpeta:
        # Crear subcarpeta si no existe
        carpeta_path = chats_dir / carpeta
        carpeta_path.mkdir(exist_ok=True)
        chat_dir = carpeta_path
    else:
        chat_dir = chats_dir
    
    chat_id = data.get("id")
    if not chat_id:
        # Generar nuevo ID basado en timestamp
        import time
        chat_id = f"chat_{int(time.time())}"
    
    chat_data = {
        "id": chat_id,
        "nombre": data.get("nombre", "Chat sin nombre"),
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mensajes": data.get("mensajes", []),
        "carpeta": carpeta
    }
    
    archivo = chat_dir / f"{chat_id}.json"
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=2)
    
    return {
        "success": True,
        "id": chat_id,
        "message": "Chat guardado exitosamente"
    }


@app.get("/api/chats/carpetas")
async def listar_carpetas_chats():
    """Lista todas las carpetas de chats con información detallada"""
    chats_dir = Path("chats_historial")
    if not chats_dir.exists():
        return {"carpetas": []}
    
    carpetas = []
    for item in chats_dir.iterdir():
        if item.is_dir():
            # Contar chats en la carpeta
            num_chats = len(list(item.glob("*.json")))
            
            # Obtener fecha del chat más reciente
            archivos = list(item.glob("*.json"))
            fecha_reciente = ""
            if archivos:
                archivos_ordenados = sorted(
                    archivos, 
                    key=lambda x: x.stat().st_mtime, 
                    reverse=True
                )
                try:
                    with open(archivos_ordenados[0], 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        fecha_reciente = data.get("fecha", "")
                except:
                    pass
            
            carpetas.append({
                "nombre": item.name,
                "num_chats": num_chats,
                "fecha_reciente": fecha_reciente
            })
    
    # Ordenar por fecha reciente
    carpetas.sort(key=lambda x: x.get("fecha_reciente", ""), reverse=True)
    
    return {"carpetas": carpetas}


@app.get("/api/chats/contenido")
async def listar_contenido_carpeta(ruta: str = ""):
    """Lista carpetas y chats en una ruta específica"""
    chats_dir = Path("chats_historial")
    if not chats_dir.exists():
        chats_dir.mkdir()
    
    # Construir ruta completa
    if ruta:
        ruta_completa = chats_dir / ruta
    else:
        ruta_completa = chats_dir
    
    if not ruta_completa.exists():
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    
    carpetas = []
    chats = []
    
    for item in ruta_completa.iterdir():
        if item.is_dir():
            # Contar chats en la carpeta
            num_chats = len(list(item.glob("*.json")))
            carpetas.append({
                "nombre": item.name,
                "num_chats": num_chats,
                "ruta": str(item.relative_to(chats_dir))
            })
        elif item.suffix == ".json":
            try:
                with open(item, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    chats.append({
                        "id": data.get("id"),
                        "nombre": data.get("nombre"),
                        "fecha": data.get("fecha"),
                        "num_mensajes": len(data.get("mensajes", [])),
                        "ruta": str(item.relative_to(chats_dir))
                    })
            except:
                pass
    
    # Ordenar
    carpetas.sort(key=lambda x: x["nombre"])
    chats.sort(key=lambda x: x.get("fecha", ""), reverse=True)
    
    return {
        "carpetas": carpetas,
        "chats": chats
    }


@app.post("/api/chats/carpetas")
async def crear_carpeta_chat(data: dict):
    """Crea una nueva carpeta para organizar chats"""
    nombre = data.get("nombre", "").strip()
    ruta_padre = data.get("ruta_padre", "").strip()
    
    if not nombre:
        raise HTTPException(status_code=400, detail="El nombre de la carpeta no puede estar vacío")
    
    chats_dir = Path("chats_historial")
    chats_dir.mkdir(exist_ok=True)
    
    # Construir ruta completa
    if ruta_padre:
        carpeta_path = chats_dir / ruta_padre / nombre
    else:
        carpeta_path = chats_dir / nombre
    
    if carpeta_path.exists():
        raise HTTPException(status_code=400, detail="La carpeta ya existe")
    
    carpeta_path.mkdir(parents=True)
    
    return {
        "success": True,
        "message": f"Carpeta '{nombre}' creada exitosamente",
        "ruta": str(carpeta_path.relative_to(chats_dir))
    }


@app.delete("/api/chats/carpetas/{ruta:path}")
async def eliminar_carpeta_chat(ruta: str):
    """Elimina una carpeta de chats y todo su contenido"""
    chats_dir = Path("chats_historial")
    carpeta_path = chats_dir / ruta
    
    if not carpeta_path.exists():
        raise HTTPException(status_code=404, detail="La carpeta no existe")
    
    if not carpeta_path.is_dir():
        raise HTTPException(status_code=400, detail="La ruta no es una carpeta")
    
    # Verificar que la ruta esté dentro de chats_historial (seguridad)
    try:
        carpeta_path.relative_to(chats_dir)
    except ValueError:
        raise HTTPException(status_code=400, detail="Ruta inválida")
    
    # Eliminar carpeta y todo su contenido
    import shutil
    shutil.rmtree(carpeta_path)
    
    return {
        "success": True,
        "message": f"Carpeta eliminada exitosamente"
    }


@app.put("/api/chats/carpetas/{ruta:path}/renombrar")
async def renombrar_carpeta_chat(ruta: str, data: dict):
    """Renombra una carpeta de chats"""
    nuevo_nombre = data.get("nuevo_nombre", "").strip()
    
    if not nuevo_nombre:
        raise HTTPException(status_code=400, detail="El nuevo nombre no puede estar vacío")
    
    chats_dir = Path("chats_historial")
    carpeta_path = chats_dir / ruta
    
    if not carpeta_path.exists():
        raise HTTPException(status_code=404, detail="La carpeta no existe")
    
    if not carpeta_path.is_dir():
        raise HTTPException(status_code=400, detail="La ruta no es una carpeta")
    
    # Verificar que la ruta esté dentro de chats_historial (seguridad)
    try:
        carpeta_path.relative_to(chats_dir)
    except ValueError:
        raise HTTPException(status_code=400, detail="Ruta inválida")
    
    # Construir nueva ruta (mantener el padre, cambiar solo el nombre)
    carpeta_padre = carpeta_path.parent
    nueva_ruta = carpeta_padre / nuevo_nombre
    
    if nueva_ruta.exists():
        raise HTTPException(status_code=400, detail="Ya existe una carpeta con ese nombre")
    
    # Renombrar carpeta
    carpeta_path.rename(nueva_ruta)
    
    # Actualizar campo "carpeta" en todos los chats dentro de la carpeta renombrada
    import json
    for chat_file in nueva_ruta.rglob("*.json"):
        try:
            with open(chat_file, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
            
            # Actualizar ruta de carpeta si existe
            if 'carpeta' in chat_data:
                ruta_relativa = str(chat_file.parent.relative_to(chats_dir))
                chat_data['carpeta'] = ruta_relativa if ruta_relativa != '.' else ''
                
                with open(chat_file, 'w', encoding='utf-8') as f:
                    json.dump(chat_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error actualizando chat {chat_file}: {e}")
    
    return {
        "success": True,
        "message": f"Carpeta renombrada exitosamente",
        "nueva_ruta": str(nueva_ruta.relative_to(chats_dir))
    }


@app.get("/api/chats/{chat_id}")
async def obtener_chat(chat_id: str):
    """Obtiene un chat específico del historial"""
    chats_dir = Path("chats_historial")
    
    # Buscar en raíz
    archivo = chats_dir / f"{chat_id}.json"
    if archivo.exists():
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Buscar en subcarpetas
    for carpeta in chats_dir.iterdir():
        if carpeta.is_dir():
            archivo = carpeta / f"{chat_id}.json"
            if archivo.exists():
                with open(archivo, 'r', encoding='utf-8') as f:
                    return json.load(f)
    
    raise HTTPException(status_code=404, detail="Chat no encontrado")


@app.put("/api/chats/{chat_id}/renombrar")
async def renombrar_chat(chat_id: str, data: dict):
    """Renombra un chat del historial"""
    nuevo_nombre = data.get("nuevo_nombre", "").strip()
    
    if not nuevo_nombre:
        raise HTTPException(status_code=400, detail="El nuevo nombre no puede estar vacío")
    
    chats_dir = Path("chats_historial")
    archivo = None
    
    # Buscar en raíz
    archivo_raiz = chats_dir / f"{chat_id}.json"
    if archivo_raiz.exists():
        archivo = archivo_raiz
    else:
        # Buscar en subcarpetas
        for carpeta in chats_dir.iterdir():
            if carpeta.is_dir():
                archivo_carpeta = carpeta / f"{chat_id}.json"
                if archivo_carpeta.exists():
                    archivo = archivo_carpeta
                    break
    
    if not archivo:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    
    # Leer, modificar y guardar
    with open(archivo, 'r', encoding='utf-8') as f:
        chat_data = json.load(f)
    
    chat_data['nombre'] = nuevo_nombre
    
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=2)
    
    return {
        "success": True,
        "message": f"Chat renombrado a '{nuevo_nombre}'"
    }


@app.delete("/api/chats/{chat_id}")
async def eliminar_chat(chat_id: str):
    """Elimina un chat del historial"""
    chats_dir = Path("chats_historial")
    
    # Buscar en raíz
    archivo = chats_dir / f"{chat_id}.json"
    if archivo.exists():
        archivo.unlink()
        return {
            "success": True,
            "message": "Chat eliminado exitosamente"
        }
    
    # Buscar en subcarpetas
    for carpeta in chats_dir.iterdir():
        if carpeta.is_dir():
            archivo = carpeta / f"{chat_id}.json"
            if archivo.exists():
                archivo.unlink()
                return {
                    "success": True,
                    "message": "Chat eliminado exitosamente"
                }
    
    raise HTTPException(status_code=404, detail="Chat no encontrado")


if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor API de Examinator...")
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
