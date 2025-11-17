"""
API Backend para Examinator Web
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pathlib import Path
from typing import List, Optional
import json
import shutil
from datetime import datetime
import asyncio
import uuid
import requests

from examinator import obtener_texto
from generador_dos_pasos import GeneradorDosPasos, PreguntaExamen
from generador_unificado import GeneradorUnificado
from generador_examenes import guardar_examen
from cursos_db import CursosDatabase
from busqueda_web import buscar_y_resumir

app = FastAPI(title="Examinator API")

# Inicializar gestor de carpetas
cursos_db = CursosDatabase("extracciones")

# Configurar CORS para permitir peticiones desde React y red local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las IPs de la red local
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estado global
config_path = Path("config.json")
generador_actual = None
generador_unificado = None  # GeneradorUnificado para GPU/CPU
progreso_generacion = {}  # {session_id: {progreso, mensaje, completado}}


def cargar_config():
    """Carga la configuración guardada"""
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "modelo_path": None,
        "ajustes_avanzados": {
            "n_ctx": 4096,
            "temperature": 0.7,
            "max_tokens": 512,
            "top_p": 0.9,
            "repeat_penalty": 1.15,
            "n_gpu_layers": 35
        }
    }


def guardar_config(config: dict):
    """Guarda la configuración"""
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def inicializar_modelo():
    """Carga automáticamente el modelo configurado al iniciar el servidor"""
    global generador_actual
    try:
        config = cargar_config()
        modelo_path = config.get("modelo_path")
        modelo_ollama = config.get("modelo_ollama_activo", "llama31-local")
        usar_ollama = config.get("usar_ollama", True)
        
        print(f"\n{'='*60}")
        print(f"🚀 Iniciando Examinator API con Ollama + GPU...")
        print(f"{'='*60}\n")
        
        # Intentar usar Ollama primero (GPU automática)
        if usar_ollama:
            try:
                generador_actual = GeneradorUnificado(
                    usar_ollama=True,
                    modelo_ollama=modelo_ollama,
                    modelo_path_gguf=modelo_path,
                    n_gpu_layers=35
                )
                print(f"✅ Ollama cargado - Usando GPU automáticamente")
                print(f"🎮 Modelo activo: {modelo_ollama}")
                print(f"{'='*60}\n")
            except Exception as e:
                print(f"⚠️  Ollama no disponible: {e}")
                print(f"💡 Intentando con modelo GGUF...\n")
                
                # Fallback a GeneradorDosPasos si Ollama falla
                if modelo_path and Path(modelo_path).exists():
                    ajustes = config.get("ajustes_avanzados", {})
                    gpu_layers = ajustes.get('n_gpu_layers', 35)
                    generador_actual = GeneradorDosPasos(modelo_path=modelo_path, n_gpu_layers=gpu_layers)
                    print(f"✅ Modelo GGUF cargado: {modelo_path}")
                    print(f"{'='*60}\n")
                else:
                    print("\n⚠️ No hay modelo configurado o no existe el archivo")
                    print("💡 Ve a Configuración para seleccionar un modelo\n")
        else:
            # Usar modelo GGUF
            if modelo_path and Path(modelo_path).exists():
                ajustes = config.get("ajustes_avanzados", {})
                gpu_layers = ajustes.get('n_gpu_layers', 0)
                generador_actual = GeneradorUnificado(
                    usar_ollama=False,
                    modelo_path_gguf=modelo_path,
                    n_gpu_layers=gpu_layers
                )
                print(f"✅ Modelo GGUF cargado: {modelo_path}")
                print(f"{'='*60}\n")
            else:
                print("\n⚠️ No hay modelo configurado o no existe el archivo")
                print("💡 Ve a Configuración para seleccionar un modelo\n")
    except Exception as e:
        print(f"\n❌ Error al cargar modelo inicial: {e}")
        print("💡 Puedes configurar el modelo desde la interfaz web\n")


# Inicializar modelo al arrancar
@app.on_event("startup")
async def startup_event():
    """Se ejecuta cuando arranca el servidor"""
    inicializar_modelo()


@app.get("/api/prompt-template")
async def obtener_prompt_template():
    """Obtiene el template del prompt predeterminado"""
    from generador_examenes import GeneradorExamenes
    return {
        "template": GeneradorExamenes.obtener_prompt_template()
    }


@app.get("/api/prompt-personalizado")
async def obtener_prompt_personalizado():
    """Obtiene el prompt personalizado guardado"""
    config = cargar_config()
    return {
        "prompt": config.get("prompt_personalizado", "")
    }


@app.post("/api/prompt-personalizado")
async def guardar_prompt_personalizado(datos: dict):
    """Guarda el prompt personalizado"""
    prompt = datos.get("prompt", "")
    config = cargar_config()
    config["prompt_personalizado"] = prompt
    guardar_config(config)
    return {
        "success": True,
        "message": "Prompt guardado exitosamente"
    }


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
    config = cargar_config()
    
    # Añadir información del modelo cargado en memoria
    global generador_actual
    if generador_actual:
        if hasattr(generador_actual, 'modelo_ollama') and generador_actual.usar_ollama:
            config["modelo_cargado"] = generador_actual.modelo_ollama
            config["modelo_activo"] = True
            config["tipo_motor"] = "ollama"
            config["gpu_activa"] = True
        elif hasattr(generador_actual, 'modelo_path_gguf') and generador_actual.modelo_path_gguf:
            config["modelo_cargado"] = generador_actual.modelo_path_gguf
            config["modelo_activo"] = True
            config["tipo_motor"] = "gguf"
            gpu_layers = generador_actual.n_gpu_layers if hasattr(generador_actual, 'n_gpu_layers') else 0
            config["gpu_activa"] = gpu_layers > 0
        else:
            config["modelo_cargado"] = None
            config["modelo_activo"] = False
            config["tipo_motor"] = None
            config["gpu_activa"] = False
    else:
        config["modelo_cargado"] = None
        config["modelo_activo"] = False
        config["tipo_motor"] = None
        config["gpu_activa"] = False
    
    return config


@app.post("/api/config")
async def actualizar_config(config: dict):
    """Actualiza la configuración"""
    guardar_config(config)
    
    # Recargar generador con nuevo modelo
    global generador_actual
    if config.get("modelo_path"):
        try:
            # Liberar modelo anterior si existe
            if generador_actual and generador_actual.llm:
                print("🔄 Liberando modelo anterior...")
                del generador_actual.llm
                generador_actual.llm = None
                del generador_actual
                generador_actual = None
                
                # Forzar garbage collection
                import gc
                gc.collect()
                print("✅ Modelo anterior liberado")
            
            # Cargar nuevo modelo
            print(f"🔄 Cargando nuevo modelo: {config['modelo_path']}")
            generador_actual = GeneradorDosPasos(modelo_path=config["modelo_path"])
            print("✅ Nuevo modelo cargado exitosamente")
            return {"message": "Configuración actualizada y modelo cargado", "success": True}
        except Exception as e:
            print(f"❌ Error al cargar modelo: {e}")
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
            generador_actual = GeneradorDosPasos(modelo_path=config["modelo_path"])
        except Exception as e:
            return {"respuesta": f"❌ Error al cargar el modelo: {str(e)}"}
    
    try:
        # Obtener ajustes avanzados del frontend
        ajustes = data.get("ajustes", {})
        n_ctx = ajustes.get("n_ctx", 4096)
        temperature = ajustes.get("temperature", 0.7)
        max_tokens = ajustes.get("max_tokens", 768)
        
        # Mostrar configuración en consola
        print(f"\n{'='*60}")
        print(f"💬 Solicitud de chat")
        print(f"⚙️ Configuración avanzada:")
        print(f"   • Contexto (n_ctx): {n_ctx} tokens")
        print(f"   • Temperatura: {temperature}")
        print(f"   • Tokens máximos: {max_tokens}")
        print(f"{'='*60}\n")
        
        # Usar el modelo para generar respuesta
        from llama_cpp import Llama
        
        # Obtener n_gpu_layers de config
        ajustes = config.get("ajustes_avanzados", {})
        gpu_layers = ajustes.get('n_gpu_layers', 35)
        
        # Crear instancia del modelo si no existe o si cambió n_ctx
        if not hasattr(generador_actual, 'llm') or generador_actual.llm is None or \
           (hasattr(generador_actual, '_n_ctx') and generador_actual._n_ctx != n_ctx):
            print(f"🔄 Recargando modelo con n_ctx={n_ctx}...")
            generador_actual.llm = Llama(
                model_path=config["modelo_path"],
                n_ctx=n_ctx,
                n_threads=6,
                n_gpu_layers=gpu_layers,
                verbose=False
            )
            generador_actual._n_ctx = n_ctx
            print("✅ Modelo cargado con nueva configuración")
        
        # Preparar el contexto si existe
        contexto = data.get("contexto", None)
        buscar_web = data.get("buscar_web", False)
        mensaje_completo = mensaje
        system_prompt = "Eres un asistente educativo útil y respondes de manera clara y concisa en español."
        
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
        
        # Generar respuesta con configuración personalizada
        top_p = ajustes.get('top_p', 0.9)
        repeat_penalty = ajustes.get('repeat_penalty', 1.15)
        
        print(f"🤖 Generando respuesta con temperatura={temperature}, max_tokens={max_tokens}, top_p={top_p}, repeat_penalty={repeat_penalty}")
        respuesta = generador_actual.llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            repeat_penalty=repeat_penalty
        )
        
        texto_respuesta = respuesta['choices'][0]['message']['content']
        print(f"✅ Respuesta generada: {len(texto_respuesta)} caracteres\n")
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
    print(f"📄 Procesando archivo: {file.filename}")
    print(f"   Tipo de contenido: {file.content_type}")
    print(f"   Carpeta destino: {carpeta or 'raíz'}")
    
    if not file.filename.endswith('.pdf') and not file.filename.endswith('.txt'):
        raise HTTPException(
            status_code=400, 
            detail=f"Solo se permiten archivos PDF o TXT. Archivo recibido: {file.filename}"
        )
    
    # Guardar archivo temporalmente
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    temp_path = temp_dir / file.filename
    
    print(f"   Guardando temporalmente en: {temp_path}")
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Extraer texto
        if file.filename.endswith('.pdf'):
            print(f"   Extrayendo texto del PDF...")
            texto = obtener_texto(str(temp_path), sin_limpiar=False, agresivo=False, verbose=False)
        else:  # .txt
            print(f"   Leyendo archivo TXT...")
            texto = temp_path.read_text(encoding='utf-8')
        
        print(f"   ✅ Texto extraído: {len(texto)} caracteres")
        
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
        
        print(f"   💾 Guardado en: {archivo_salida}")
        
        return {
            "success": True,
            "mensaje": "Archivo procesado exitosamente",
            "archivo": str(archivo_salida.relative_to(Path("extracciones"))),
            "ruta_completa": str(archivo_salida),
            "caracteres": len(texto),
            "palabras": len(texto.split()),
            "carpeta": carpeta or "raíz"
        }
    
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar archivo: {str(e)}")
    
    finally:
        # Limpiar archivo temporal
        if temp_path.exists():
            temp_path.unlink()
            print(f"   🗑️ Archivo temporal eliminado")


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


@app.put("/api/documentos/renombrar")
async def renombrar_documento(data: dict):
    """Renombra un documento"""
    ruta_actual = data.get("ruta_actual", "").strip()
    nuevo_nombre = data.get("nuevo_nombre", "").strip()
    
    print(f"🔄 Renombrar documento:")
    print(f"   Ruta actual: {ruta_actual}")
    print(f"   Nuevo nombre: {nuevo_nombre}")
    
    if not ruta_actual:
        raise HTTPException(status_code=400, detail="La ruta actual no puede estar vacía")
    
    if not nuevo_nombre:
        raise HTTPException(status_code=400, detail="El nuevo nombre no puede estar vacío")
    
    try:
        resultado = cursos_db.renombrar_documento(ruta_actual, nuevo_nombre)
        print(f"   ✅ Resultado: {resultado}")
        return {"success": True, **resultado}
    except ValueError as e:
        print(f"   ❌ Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
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
        # Obtener solo el nombre del archivo
        nombre_archivo = Path(ruta).name
        print(f"📄 Cargando: {nombre_archivo}")
        
        contenido = cursos_db.obtener_contenido_documento(ruta)
        return contenido
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/documentos/contenido")
async def actualizar_contenido_documento(data: dict):
    """Actualiza el contenido de un documento"""
    ruta = data.get("ruta", "").strip()
    contenido = data.get("contenido", "")
    
    if not ruta:
        raise HTTPException(status_code=400, detail="La ruta no puede estar vacía")
    
    try:
        resultado = cursos_db.actualizar_contenido_documento(ruta, contenido)
        return {"success": True, **resultado}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generar-examen")
async def generar_examen(datos: dict):
    """Genera un examen basado en contenido de documentos"""
    global generador_actual, progreso_generacion
    
    contenido = datos.get("contenido")
    prompt_personalizado = datos.get("prompt_personalizado", "")
    prompt_sistema = datos.get("prompt_sistema", None)  # Prompt completo del sistema si se proporciona
    num_multiple = datos.get("num_multiple", 5)
    num_corta = datos.get("num_corta", 3)
    num_desarrollo = datos.get("num_desarrollo", 2)
    num_verdadero_falso = datos.get("num_verdadero_falso", 0)
    session_id = datos.get("session_id", str(uuid.uuid4()))
    
    # Cargar ajustes avanzados desde config
    config = cargar_config()
    ajustes = config.get("ajustes_avanzados", {
        "n_ctx": 4096,
        "temperature": 0.7,
        "max_tokens": 512
    })
    
    # Extraer nombres de archivos del contenido
    import re
    archivos = re.findall(r'=== (.+?) ===', contenido)
    
    print(f"\n{'='*60}")
    print(f"📝 Solicitud de generación de examen (Session: {session_id})")
    print(f"📊 Configuración de preguntas:")
    if num_multiple > 0:
        print(f"   • Opción múltiple: {num_multiple}")
    if num_verdadero_falso > 0:
        print(f"   • Verdadero/Falso: {num_verdadero_falso}")
    if num_corta > 0:
        print(f"   • Corta: {num_corta}")
    if num_desarrollo > 0:
        print(f"   • Desarrollo: {num_desarrollo}")
    print(f"\n🎮 Motor de IA:")
    if generador_actual and hasattr(generador_actual, 'usar_ollama') and generador_actual.usar_ollama:
        print(f"   ✅ USANDO GPU - Ollama")
        print(f"   🎯 Modelo: {generador_actual.modelo_ollama}")
        print(f"   💡 GPU activada automáticamente")
    else:
        print(f"   ⚠️  Usando llama-cpp-python")
    print(f"\n⚙️ Configuración del modelo:")
    print(f"   • Temperatura: {ajustes.get('temperature', 0.7)}")
    print(f"   • Tokens máximos: {ajustes.get('max_tokens', 512)}")
    print(f"   • Contexto (n_ctx): {ajustes.get('n_ctx', 4096)} tokens")
    print(f"   • Top P: 0.9")
    print(f"   • Repetición: 1.15")
    print(f"\n📄 Longitud del contenido: {len(contenido) if contenido else 0} caracteres")
    if archivos:
        print(f"📚 Archivos cargados en contexto ({len(archivos)}):")
        for i, archivo in enumerate(archivos, 1):
            print(f"   {i}. 📄 {archivo}")
    if prompt_personalizado:
        print(f"💬 Prompt personalizado: {prompt_personalizado[:100]}...")
    if prompt_sistema:
        print(f"🎨 Prompt sistema personalizado recibido: {len(prompt_sistema)} caracteres")
        print(f"   Primeros 100 caracteres: {prompt_sistema[:100]}...")
    else:
        print(f"📋 Usando prompt del sistema predeterminado")
    print(f"{'='*60}\n")
    
    if not contenido:
        raise HTTPException(status_code=400, detail="Falta el contenido para generar el examen")
    
    # Inicializar progreso
    progreso_generacion[session_id] = {
        'progreso': 0,
        'mensaje': 'Iniciando generación...',
        'completado': False,
        'error': None
    }
    
    def callback_progreso(progreso: int, mensaje: str):
        """Callback para actualizar el progreso"""
        progreso_generacion[session_id] = {
            'progreso': progreso,
            'mensaje': mensaje,
            'completado': False,
            'error': None
        }
        print(f"📊 Progreso {progreso}%: {mensaje}")
    
    try:
        # Recargar generador con la configuración actual
        callback_progreso(5, "Cargando modelo de IA...")
        config = cargar_config()
        modelo_ollama = config.get("modelo_ollama_activo", "llama31-local")
        usar_ollama = config.get("usar_ollama", True)
        modelo_path = config.get("modelo_path")
        gpu_layers = ajustes.get('n_gpu_layers', 35)
        
        print(f"📦 Configuración actual:")
        print(f"   • Usar Ollama: {usar_ollama}")
        if usar_ollama:
            print(f"   • Modelo Ollama: {modelo_ollama}")
        else:
            print(f"   • Modelo GGUF: {modelo_path}")
            print(f"   • GPU Layers: {gpu_layers}")
        
        # Crear generador con la configuración actual
        if usar_ollama:
            print(f"🔄 Cargando modelo Ollama: {modelo_ollama}")
            generador_actual = GeneradorUnificado(
                usar_ollama=True,
                modelo_ollama=modelo_ollama,
                n_gpu_layers=gpu_layers
            )
        else:
            print(f"🔄 Cargando modelo GGUF: {modelo_path}")
            generador_actual = GeneradorUnificado(
                usar_ollama=False,
                modelo_path_gguf=modelo_path,
                n_gpu_layers=gpu_layers
            )
        
        # Generar preguntas
        num_preguntas = {
            'multiple': num_multiple,
            'verdadero_falso': num_verdadero_falso,
            'corta': num_corta,
            'desarrollo': num_desarrollo
        }
        
        callback_progreso(10, "Preparando generación de preguntas...")
        print("🤖 Generando preguntas con IA en DOS PASOS...")
        preguntas = generador_actual.generar_examen(
            contenido, 
            num_preguntas,
            ajustes_modelo=ajustes,
            callback_progreso=callback_progreso,
            archivos=archivos,  # Pasar lista de archivos
            session_id=session_id  # Pasar session_id para el log
        )
        print(f"✅ Generadas {len(preguntas)} preguntas exitosamente")
        
        # Convertir a formato JSON
        callback_progreso(95, "Finalizando...")
        preguntas_json = [p.to_dict() for p in preguntas]
        
        # Marcar como completado
        progreso_generacion[session_id] = {
            'progreso': 100,
            'mensaje': 'Examen generado exitosamente',
            'completado': True,
            'error': None
        }
        
        resultado = {
            "success": True,
            "session_id": session_id,
            "preguntas": preguntas_json,
            "total_preguntas": len(preguntas),
            "puntos_totales": sum(p['puntos'] for p in preguntas_json)
        }
        
        print(f"✅ Examen generado: {resultado['total_preguntas']} preguntas, {resultado['puntos_totales']} puntos totales\n")
        return resultado
        
    except Exception as e:
        import traceback
        print(f"\n❌ ERROR generando examen:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        print(f"   Traceback:")
        traceback.print_exc()
        print(f"{'='*60}\n")
        
        # Marcar progreso como error
        if session_id in progreso_generacion:
            progreso_generacion[session_id] = {
                'progreso': 0,
                'mensaje': f'Error: {str(e)}',
                'completado': True,
                'error': str(e)
            }
        
        raise HTTPException(status_code=500, detail=f"Error al generar examen: {str(e)}")


@app.get("/api/progreso-examen/{session_id}")
async def obtener_progreso_examen(session_id: str):
    """Endpoint SSE para streaming de progreso de generación de examen"""
    async def event_generator():
        try:
            while True:
                # Obtener progreso actual
                if session_id in progreso_generacion:
                    progreso = progreso_generacion[session_id]
                    
                    # Enviar evento SSE
                    data = json.dumps({
                        'progreso': progreso['progreso'],
                        'mensaje': progreso['mensaje'],
                        'completado': progreso['completado'],
                        'error': progreso['error']
                    })
                    yield f"data: {data}\n\n"
                    
                    # Si está completado (exitoso o error), terminar stream
                    if progreso['completado']:
                        # Limpiar progreso después de 5 segundos
                        await asyncio.sleep(5)
                        if session_id in progreso_generacion:
                            del progreso_generacion[session_id]
                        break
                else:
                    # Si no existe la sesión, enviar progreso inicial
                    data = json.dumps({
                        'progreso': 0,
                        'mensaje': 'Esperando inicio...',
                        'completado': False,
                        'error': None
                    })
                    yield f"data: {data}\n\n"
                
                # Esperar un poco antes de la siguiente actualización
                await asyncio.sleep(0.5)
                
        except asyncio.CancelledError:
            # Cliente desconectó
            print(f"🔌 Cliente desconectado del stream de progreso: {session_id}")
            if session_id in progreso_generacion:
                del progreso_generacion[session_id]
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/evaluar-examen")
async def evaluar_examen(datos: dict):
    """Evalúa las respuestas de un examen"""
    global generador_unificado
    
    try:
        # Usar GeneradorUnificado (con GPU/CPU según configuración)
        if generador_unificado is None:
            config = cargar_config()
            usar_ollama = config.get("usar_ollama", True)
            modelo_ollama = config.get("modelo_ollama_activo", "llama31-local")
            modelo_path_gguf = config.get("modelo_path")
            ajustes = config.get("ajustes_avanzados", {})
            n_gpu_layers = ajustes.get("n_gpu_layers", 35)
            
            generador_unificado = GeneradorUnificado(
                usar_ollama=usar_ollama,
                modelo_ollama=modelo_ollama,
                modelo_path_gguf=modelo_path_gguf,
                n_gpu_layers=n_gpu_layers
            )
        
        try:
            # Validar que los datos requeridos estén presentes
            if not isinstance(datos, dict):
                raise HTTPException(status_code=400, detail="El cuerpo de la solicitud debe ser un diccionario JSON válido.")

            preguntas_data = datos.get("preguntas")
            respuestas = datos.get("respuestas")
            carpeta_path = datos.get("carpeta_path", "")

            if not preguntas_data:
                raise HTTPException(status_code=400, detail="El campo 'preguntas' es obligatorio y no puede estar vacío.")

            if not isinstance(respuestas, dict):
                raise HTTPException(status_code=400, detail="El campo 'respuestas' debe ser un diccionario.")

            # Validar que cada respuesta sea una cadena válida
            for key, value in respuestas.items():
                if not isinstance(value, str):
                    raise HTTPException(status_code=400, detail=f"La respuesta para la pregunta {key} debe ser una cadena de texto.")

            # Continuar con la lógica existente
            resultados = []
            puntos_obtenidos = 0
            puntos_totales = 0

            for i, pregunta_dict in enumerate(preguntas_data):
                pregunta = PreguntaExamen.from_dict(pregunta_dict)
                respuesta_usuario = respuestas.get(str(i), "")

                # Evaluar respuesta
                resultado_eval = generador_unificado.evaluar_respuesta(pregunta, respuesta_usuario)
                puntos = resultado_eval["puntos_obtenidos"]
                feedback = resultado_eval["feedback"]

                puntos_obtenidos += puntos
                puntos_totales += pregunta.puntos

                resultados.append({
                    "pregunta": pregunta.pregunta,
                    "tipo": pregunta.tipo,
                    "opciones": pregunta.opciones if pregunta.tipo == 'multiple' else [],
                    "respuesta_usuario": respuesta_usuario,
                    "respuesta_correcta": pregunta.respuesta_correcta if pregunta.tipo == 'multiple' else None,
                    "puntos": puntos,
                    "puntos_maximos": pregunta.puntos,
                    "feedback": feedback
                })
            
            porcentaje = (puntos_obtenidos / puntos_totales * 100) if puntos_totales > 0 else 0
            
            # Guardar resultados si hay carpeta especificada
            if carpeta_path:
                try:
                    print(f"💾 Guardando resultados para carpeta: {carpeta_path}")
                    carpeta = Path(carpeta_path)
                    if not carpeta.exists():
                        carpeta = Path("extracciones") / carpeta_path

                    carpeta_examenes = Path("examenes") / carpeta.relative_to(Path("extracciones"))
                    carpeta_examenes.mkdir(parents=True, exist_ok=True)

                    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
                    archivo_resultado = carpeta_examenes / f"examen_{fecha}.json"

                    resultado_completo = {
                        "id": fecha,
                        "archivo": f"examen_{fecha}.json",
                        "fecha_completado": datetime.now().isoformat(),
                        "carpeta_ruta": str(carpeta.relative_to(Path("extracciones"))),
                        "carpeta_nombre": carpeta.name,
                        "puntos_obtenidos": puntos_obtenidos,
                        "puntos_totales": puntos_totales,
                        "porcentaje": porcentaje,
                        "resultados": resultados,
                        "tipo": "completado"
                    }

                    with open(archivo_resultado, 'w', encoding='utf-8') as f:
                        json.dump(resultado_completo, f, ensure_ascii=False, indent=2)

                    print(f"✅ Resultados guardados en: {archivo_resultado}")

                    carpeta_progreso = carpeta_examenes / "examenes_progreso"
                    if carpeta_progreso.exists():
                        for archivo in carpeta_progreso.glob("examen_progreso_*.json"):
                            archivo.unlink()
                except Exception as e:
                    print(f"❌ Error guardando resultados: {e}")

            return {
                "success": True,
                "puntos_obtenidos": puntos_obtenidos,
                "puntos_totales": puntos_totales,
                "porcentaje": porcentaje,
                "resultados": resultados
            }
        except Exception as e:
            print(f"Error evaluando examen: {e}")
            raise HTTPException(status_code=500, detail=f"Error al evaluar examen: {str(e)}")
    except Exception as e:
        print(f"Error evaluando examen: {e}")
        raise HTTPException(status_code=500, detail=f"Error al evaluar examen: {str(e)}")


@app.post("/api/examenes/pausar")
async def pausar_examen(datos: dict):
    """Guarda el progreso de un examen para continuarlo después"""
    try:
        carpeta_ruta = datos.get("carpeta_ruta")
        carpeta_nombre = datos.get("carpeta_nombre")
        preguntas = datos.get("preguntas", [])
        respuestas = datos.get("respuestas", {})
        fecha_inicio = datos.get("fecha_inicio")
        
        if not carpeta_ruta:
            raise HTTPException(status_code=400, detail="Falta la ruta de la carpeta")
        
        print(f"📝 Pausando examen para carpeta: {carpeta_ruta}")
        
        # Determinar ruta relativa desde extracciones/
        carpeta = Path(carpeta_ruta)
        if not carpeta.exists():
            carpeta = Path("extracciones") / carpeta_ruta
        
        # Obtener ruta relativa respecto a extracciones
        try:
            ruta_relativa = carpeta.relative_to(Path("extracciones"))
        except ValueError:
            # Si no está en extracciones, usar la ruta tal cual
            ruta_relativa = Path(carpeta_ruta)
        
        # Crear estructura paralela en examenes/
        carpeta_examenes_base = Path("examenes") / ruta_relativa
        carpeta_examenes_base.mkdir(parents=True, exist_ok=True)
        
        carpeta_examenes = carpeta_examenes_base / "examenes_progreso"
        carpeta_examenes.mkdir(parents=True, exist_ok=True)
        
        print(f"   Guardando en estructura paralela: {carpeta_examenes}")
        
        # IMPORTANTE: Eliminar exámenes anteriores de esta misma carpeta
        # para evitar duplicados
        for archivo_anterior in carpeta_examenes.glob("examen_progreso_*.json"):
            try:
                archivo_anterior.unlink()
                print(f"🗑️ Examen anterior eliminado: {archivo_anterior.name}")
            except Exception as e:
                print(f"⚠️ No se pudo eliminar {archivo_anterior.name}: {e}")
        
        # Crear archivo único para este examen en progreso
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_progreso = carpeta_examenes / f"examen_progreso_{fecha}.json"
        
        datos_progreso = {
            "id": fecha,
            "archivo": f"examen_progreso_{fecha}.json",
            "carpeta_ruta": str(ruta_relativa),
            "carpeta_nombre": carpeta_nombre,
            "preguntas": preguntas,
            "respuestas": respuestas,
            "fecha_inicio": fecha_inicio,
            "fecha_pausa": datetime.now().isoformat(),
            "tipo": "en_progreso"
        }
        
        with open(archivo_progreso, 'w', encoding='utf-8') as f:
            json.dump(datos_progreso, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Examen pausado guardado en: {archivo_progreso}")
        
        return {"success": True, "message": "Examen pausado correctamente"}
    except Exception as e:
        print(f"❌ Error pausando examen: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al pausar examen: {str(e)}")


@app.post("/api/examenes/guardar-temporal")
async def guardar_examen_temporal(datos: dict):
    """Guarda el examen en curso localmente para recuperarlo después"""
    try:
        # Crear carpeta temporal si no existe
        carpeta_temp = Path("temp_examenes")
        carpeta_temp.mkdir(exist_ok=True)
        
        # Siempre usar el mismo archivo para el examen temporal
        archivo_temp = carpeta_temp / "examen_en_curso.json"
        
        datos_examen = {
            "preguntas": datos.get("preguntas", []),
            "respuestas": datos.get("respuestas", {}),
            "carpeta": datos.get("carpeta"),
            "fecha_guardado": datetime.now().isoformat()
        }
        
        with open(archivo_temp, 'w', encoding='utf-8') as f:
            json.dump(datos_examen, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Examen temporal guardado en: {archivo_temp}")
        
        return {"success": True, "message": "Guardado automático completado"}
    except Exception as e:
        print(f"❌ Error guardando examen temporal: {e}")
        # No lanzar error para que no interrumpa al usuario
        return {"success": False, "message": str(e)}


@app.get("/api/examenes/cargar-temporal")
async def cargar_examen_temporal():
    """Carga el examen temporal si existe"""
    try:
        archivo_temp = Path("temp_examenes/examen_en_curso.json")
        
        if not archivo_temp.exists():
            return {"success": False, "message": "No hay examen temporal guardado"}
        
        with open(archivo_temp, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        print(f"📂 Examen temporal cargado desde: {archivo_temp}")
        
        return {
            "success": True,
            "examen": datos
        }
    except Exception as e:
        print(f"❌ Error cargando examen temporal: {e}")
        return {"success": False, "message": str(e)}


@app.delete("/api/examenes/limpiar-temporal")
async def limpiar_examen_temporal():
    """Elimina el examen temporal"""
    try:
        archivo_temp = Path("temp_examenes/examen_en_curso.json")
        
        if archivo_temp.exists():
            archivo_temp.unlink()
            print(f"🗑️ Examen temporal eliminado")
        
        return {"success": True, "message": "Examen temporal eliminado"}
    except Exception as e:
        print(f"❌ Error eliminando examen temporal: {e}")
        return {"success": False, "message": str(e)}


@app.delete("/api/examenes/carpeta")
async def eliminar_carpeta_examenes(ruta: str, forzar: bool = False):
    """Elimina una carpeta de exámenes (forzar=true elimina con contenido)"""
    try:
        base_examenes = Path("examenes")
        ruta_completa = base_examenes / ruta if ruta else None
        
        if not ruta_completa or not ruta_completa.exists():
            raise HTTPException(status_code=404, detail="Carpeta no encontrada")
        
        # Verificar si tiene contenido
        tiene_contenido = any(ruta_completa.iterdir())
        
        if tiene_contenido and not forzar:
            raise HTTPException(
                status_code=400, 
                detail="La carpeta contiene archivos. Use forzar=true para eliminar con contenido"
            )
        
        # Eliminar carpeta
        import shutil
        shutil.rmtree(ruta_completa)
        print(f"🗑️ Carpeta de exámenes eliminada: {ruta}")
        
        return {"success": True, "mensaje": "Carpeta eliminada"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error eliminando carpeta de exámenes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/examenes/examen")
async def eliminar_examen(ruta: str, archivo: str):
    """Elimina un examen específico (completado o en progreso)"""
    try:
        base_examenes = Path("examenes")
        
        # Puede ser un examen completado o en progreso
        archivo_completo = base_examenes / ruta / archivo
        
        if not archivo_completo.exists():
            # Intentar en la carpeta de progreso
            archivo_completo = base_examenes / ruta / "examenes_progreso" / archivo
        
        if not archivo_completo.exists():
            raise HTTPException(status_code=404, detail="Examen no encontrado")
        
        # Eliminar archivo
        archivo_completo.unlink()
        print(f"🗑️ Examen eliminado: {archivo}")
        
        return {"success": True, "mensaje": "Examen eliminado"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error eliminando examen: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/examenes/carpetas")
async def listar_carpetas_examenes(ruta: str = ""):
    """Lista carpetas y exámenes en una ruta de examenes/ (estructura paralela)"""
    try:
        base_examenes = Path("examenes")
        
        # Construir ruta completa
        if ruta:
            ruta_completa = base_examenes / ruta
        else:
            ruta_completa = base_examenes
        
        if not ruta_completa.exists():
            return {
                "ruta_actual": ruta,
                "carpetas": [],
                "examenes_completados": [],
                "examenes_progreso": [],
                "examenes_progreso_global": []
            }
        
        carpetas = []
        examenes_completados = []
        examenes_progreso = []
        examenes_progreso_global = []
        
        # Si estamos en la raíz, buscar TODOS los exámenes en progreso recursivamente
        if not ruta:
            print("📊 Buscando todos los exámenes en progreso...")
            for carpeta in base_examenes.rglob("*"):
                if carpeta.is_dir() and carpeta.name == "examenes_progreso":
                    for archivo in sorted(carpeta.glob("examen_progreso_*.json"), reverse=True):
                        try:
                            with open(archivo, 'r', encoding='utf-8') as f:
                                examen = json.load(f)
                                examenes_progreso_global.append(examen)
                        except Exception as e:
                            print(f"Error leyendo {archivo}: {e}")
            print(f"   ✅ Encontrados {len(examenes_progreso_global)} exámenes en progreso")
        
        # Listar carpetas
        for item in sorted(ruta_completa.iterdir()):
            if item.is_dir() and item.name != "examenes_progreso":
                # Contar exámenes en la carpeta
                num_completados = len(list(item.glob("examen_*.json")))
                num_progreso = 0
                carpeta_progreso = item / "examenes_progreso"
                if carpeta_progreso.exists():
                    num_progreso = len(list(carpeta_progreso.glob("examen_progreso_*.json")))
                
                carpetas.append({
                    "nombre": item.name,
                    "ruta": str(item.relative_to(base_examenes)) if ruta else item.name,
                    "num_completados": num_completados,
                    "num_progreso": num_progreso,
                    "total_examenes": num_completados + num_progreso
                })
        
        # Listar exámenes completados en esta carpeta
        for archivo in sorted(ruta_completa.glob("examen_*.json"), reverse=True):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    examen = json.load(f)
                    if examen.get("tipo") == "completado":
                        examenes_completados.append(examen)
            except Exception as e:
                print(f"Error leyendo {archivo}: {e}")
        
        # Listar exámenes en progreso en esta carpeta específica (solo si no es raíz)
        if ruta:
            carpeta_progreso = ruta_completa / "examenes_progreso"
            if carpeta_progreso.exists():
                for archivo in sorted(carpeta_progreso.glob("examen_progreso_*.json"), reverse=True):
                    try:
                        with open(archivo, 'r', encoding='utf-8') as f:
                            examen = json.load(f)
                            examenes_progreso.append(examen)
                    except Exception as e:
                        print(f"Error leyendo {archivo}: {e}")
        
        return {
            "ruta_actual": ruta,
            "carpetas": carpetas,
            "examenes_completados": examenes_completados,
            "examenes_progreso": examenes_progreso,
            "examenes_progreso_global": examenes_progreso_global  # Solo lleno en raíz
        }
    except Exception as e:
        print(f"Error listando carpetas de exámenes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/examenes/listar")
async def listar_examenes():
    """Lista todos los exámenes guardados (completados y en progreso) - DEPRECATED"""
    try:
        # Buscar en la carpeta examenes/ con estructura paralela
        carpeta_examenes = Path("examenes")
        completados = []
        en_progreso = []
        
        if carpeta_examenes.exists():
            # Buscar recursivamente en todas las carpetas de examenes/
            for carpeta in carpeta_examenes.rglob("*"):
                if not carpeta.is_dir():
                    continue
                
                # Buscar exámenes completados directamente en la carpeta
                for archivo in sorted(carpeta.glob("examen_*.json"), reverse=True):
                    try:
                        with open(archivo, 'r', encoding='utf-8') as f:
                            examen = json.load(f)
                            if examen.get("tipo") == "completado":
                                completados.append(examen)
                    except Exception as e:
                        print(f"Error leyendo examen completado {archivo}: {e}")
                
                # Buscar exámenes en progreso
                carpeta_progreso = carpeta / "examenes_progreso"
                if carpeta_progreso.exists():
                    for archivo in sorted(carpeta_progreso.glob("examen_progreso_*.json"), reverse=True):
                        try:
                            with open(archivo, 'r', encoding='utf-8') as f:
                                examen = json.load(f)
                                en_progreso.append(examen)
                        except Exception as e:
                            print(f"Error leyendo examen en progreso {archivo}: {e}")
        
        print(f"📊 Exámenes encontrados: {len(completados)} completados, {len(en_progreso)} en progreso")
        
        return {
            "success": True,
            "completados": completados,
            "enProgreso": en_progreso
        }
    except Exception as e:
        print(f"Error listando exámenes: {e}")
        raise HTTPException(status_code=500, detail=f"Error al listar exámenes: {str(e)}")


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


# ========================================
# ENDPOINTS DE OLLAMA Y GPU
# ========================================

@app.get("/api/ollama/modelos")
async def listar_modelos_ollama():
    """Lista todos los modelos disponibles en Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            modelos = data.get('models', [])
            
            # Formatear modelos con información adicional
            modelos_formateados = []
            for modelo in modelos:
                nombre = modelo.get('name', '')
                tamaño_bytes = modelo.get('size', 0)
                tamaño_gb = round(tamaño_bytes / (1024**3), 2)
                
                # Detectar tipo de modelo por nombre
                tipo = "Desconocido"
                velocidad = "Media"
                if "3b" in nombre.lower():
                    tipo = "Pequeño (3B)"
                    velocidad = "Muy rápida"
                elif "7b" in nombre.lower() or "8b" in nombre.lower():
                    tipo = "Mediano (7-8B)"
                    velocidad = "Rápida"
                elif "13b" in nombre.lower() or "14b" in nombre.lower():
                    tipo = "Grande (13-14B)"
                    velocidad = "Media"
                elif "70b" in nombre.lower():
                    tipo = "Muy Grande (70B)"
                    velocidad = "Lenta"
                
                modelos_formateados.append({
                    'nombre': nombre,
                    'tamaño_gb': tamaño_gb,
                    'tipo': tipo,
                    'velocidad': velocidad,
                    'modified_at': modelo.get('modified_at', ''),
                    'digest': modelo.get('digest', '')[:12]  # Primeros 12 caracteres del digest
                })
            
            return {
                "success": True,
                "modelos": modelos_formateados,
                "total": len(modelos_formateados),
                "ollama_activo": True
            }
        else:
            return {
                "success": False,
                "modelos": [],
                "total": 0,
                "ollama_activo": False,
                "mensaje": "Ollama no responde correctamente"
            }
    except Exception as e:
        return {
            "success": False,
            "modelos": [],
            "total": 0,
            "ollama_activo": False,
            "mensaje": f"Ollama no disponible: {str(e)}"
        }


@app.post("/api/ollama/cambiar-modelo")
async def cambiar_modelo_ollama(datos: dict):
    """Cambia el modelo activo de Ollama"""
    global generador_actual
    
    modelo = datos.get("modelo", "").strip()
    if not modelo:
        raise HTTPException(status_code=400, detail="Falta el nombre del modelo")
    
    try:
        print(f"\n🔄 Cambiando a modelo Ollama: {modelo}")
        
        # Liberar generador anterior
        if generador_actual:
            del generador_actual
            generador_actual = None
            import gc
            gc.collect()
        
        # Crear nuevo generador con Ollama
        from generador_unificado import GeneradorUnificado
        generador_actual = GeneradorUnificado(
            usar_ollama=True,
            modelo_ollama=modelo,
            n_gpu_layers=35
        )
        
        # Guardar en config
        config = cargar_config()
        config["modelo_ollama_activo"] = modelo
        config["usar_ollama"] = True
        guardar_config(config)
        
        print(f"✅ Modelo cambiado a: {modelo}")
        
        return {
            "success": True,
            "mensaje": f"Modelo cambiado a {modelo}",
            "modelo": modelo
        }
    except Exception as e:
        print(f"❌ Error cambiando modelo: {e}")
        raise HTTPException(status_code=500, detail=f"Error al cambiar modelo: {str(e)}")


@app.delete("/api/ollama/modelo/{nombre_modelo:path}")
async def eliminar_modelo_ollama(nombre_modelo: str):
    """Elimina un modelo de Ollama"""
    try:
        print(f"\n🗑️ Eliminando modelo de Ollama: {nombre_modelo}")
        
        # Verificar que no sea el modelo activo
        config = cargar_config()
        modelo_activo = config.get("modelo_ollama_activo", "")
        
        if nombre_modelo == modelo_activo:
            return {
                "success": False,
                "mensaje": "No puedes eliminar el modelo activo. Cambia a otro modelo primero."
            }
        
        # Llamar a Ollama para eliminar el modelo
        response = requests.delete(
            f"http://localhost:11434/api/delete",
            json={"name": nombre_modelo},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Modelo eliminado: {nombre_modelo}")
            return {
                "success": True,
                "mensaje": f"Modelo '{nombre_modelo}' eliminado correctamente"
            }
        else:
            error_msg = response.text if response.text else "Error desconocido"
            print(f"❌ Error eliminando modelo: {error_msg}")
            return {
                "success": False,
                "mensaje": f"Error al eliminar modelo: {error_msg}"
            }
            
    except Exception as e:
        print(f"❌ Error eliminando modelo: {e}")
        return {
            "success": False,
            "mensaje": f"Error al eliminar modelo: {str(e)}"
        }


@app.post("/api/motor/cambiar")
async def cambiar_motor_ia(datos: dict):
    """Cambia entre Ollama (GPU) y llama-cpp-python (CPU/GPU)"""
    global generador_actual
    
    usar_ollama = datos.get("usar_ollama", True)
    modelo_ollama = datos.get("modelo_ollama", "llama31-local")
    modelo_gguf = datos.get("modelo_gguf", None)
    n_gpu_layers = datos.get("n_gpu_layers", 35)
    
    try:
        motor = "Ollama (GPU automática)" if usar_ollama else "llama-cpp-python"
        print(f"\n🔄 Cambiando motor de IA a: {motor}")
        
        # Liberar generador anterior
        if generador_actual:
            del generador_actual
            generador_actual = None
            import gc
            gc.collect()
        
        # Crear nuevo generador
        from generador_unificado import GeneradorUnificado
        
        if usar_ollama:
            generador_actual = GeneradorUnificado(
                usar_ollama=True,
                modelo_ollama=modelo_ollama,
                n_gpu_layers=n_gpu_layers
            )
            print(f"✅ Motor Ollama activo - GPU automática")
            print(f"🎯 Modelo: {modelo_ollama}")
        else:
            if not modelo_gguf:
                config = cargar_config()
                modelo_gguf = config.get("modelo_path")
            
            if not modelo_gguf or not Path(modelo_gguf).exists():
                raise ValueError("No hay modelo GGUF configurado o no existe")
            
            generador_actual = GeneradorUnificado(
                usar_ollama=False,
                modelo_path_gguf=modelo_gguf,
                n_gpu_layers=n_gpu_layers
            )
            
            gpu_info = f"GPU activada ({n_gpu_layers} capas)" if n_gpu_layers > 0 else "Solo CPU (0 capas)"
            print(f"✅ Motor llama-cpp-python activo - {gpu_info}")
            print(f"📁 Modelo: {Path(modelo_gguf).name}")
        
        # Guardar configuración
        config = cargar_config()
        config["usar_ollama"] = usar_ollama
        config["modelo_ollama_activo"] = modelo_ollama if usar_ollama else None
        config["ajustes_avanzados"]["n_gpu_layers"] = n_gpu_layers
        guardar_config(config)
        
        return {
            "success": True,
            "mensaje": f"Motor cambiado a {motor}",
            "usar_ollama": usar_ollama,
            "gpu_activa": n_gpu_layers > 0 or usar_ollama
        }
    except Exception as e:
        print(f"❌ Error cambiando motor: {e}")
        raise HTTPException(status_code=500, detail=f"Error al cambiar motor: {str(e)}")


@app.get("/api/motor/estado")
async def obtener_estado_motor():
    """Obtiene el estado actual del motor de IA"""
    global generador_actual
    
    if not generador_actual:
        return {
            "activo": False,
            "tipo": None,
            "modelo": None,
            "gpu_activa": False
        }
    
    if hasattr(generador_actual, 'usar_ollama') and generador_actual.usar_ollama:
        return {
            "activo": True,
            "tipo": "ollama",
            "modelo": generador_actual.modelo_ollama,
            "gpu_activa": True,
            "gpu_automatica": True,
            "descripcion": "Ollama activa la GPU automáticamente"
        }
    else:
        gpu_layers = generador_actual.n_gpu_layers if hasattr(generador_actual, 'n_gpu_layers') else 0
        return {
            "activo": True,
            "tipo": "llama-cpp-python",
            "modelo": Path(generador_actual.modelo_path_gguf).name if hasattr(generador_actual, 'modelo_path_gguf') else None,
            "gpu_activa": gpu_layers > 0,
            "gpu_layers": gpu_layers,
            "descripcion": f"GPU con {gpu_layers} capas" if gpu_layers > 0 else "Solo CPU"
        }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor API de Examinator...")
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)


