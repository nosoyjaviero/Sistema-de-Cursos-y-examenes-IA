"""
API Backend para Examinator Web
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pathlib import Path
from typing import List, Optional
import json
import shutil
from datetime import datetime, timedelta
import asyncio
import uuid
import requests

from examinator import obtener_texto
from generador_dos_pasos import GeneradorDosPasos, PreguntaExamen
from generador_unificado import GeneradorUnificado
from generador_examenes import guardar_examen
from cursos_db import CursosDatabase
from busqueda_web import buscar_y_resumir

app = FastAPI(title="Examinator API", docs_url="/api/docs", openapi_url="/api/openapi.json")

# Inicializar gestor de carpetas
try:
    cursos_db = CursosDatabase("extracciones")
except Exception as e:
    print(f"⚠️  Error inicializando base de datos: {e}")
    cursos_db = None

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


def normalizar_examen_completo(examen: dict) -> dict:
    """
    Normaliza un examen completo después de generarlo y antes de guardarlo.
    
    Correcciones aplicadas:
    1. Tipos de pregunta: "verdadero-falso" → "verdadero_falso"
    2. Intervalos SM-2: decimales → enteros (0.5 → 1)
    3. Rutas: backslash → forward slash (Platzi\\Prueba → Platzi/Prueba)
    4. Campos requeridos para Spaced Repetition
    """
    # Normalizar carpeta_ruta (Windows → Unix)
    if "carpeta_ruta" in examen and examen["carpeta_ruta"]:
        examen["carpeta_ruta"] = examen["carpeta_ruta"].replace("\\", "/")
    if "carpeta" in examen and examen["carpeta"]:
        examen["carpeta"] = examen["carpeta"].replace("\\", "/")
    
    # Normalizar preguntas
    if "preguntas" in examen and isinstance(examen["preguntas"], list):
        for pregunta in examen["preguntas"]:
            pregunta = normalizar_pregunta_spaced_repetition(pregunta)
    
    # Normalizar resultados (si existen)
    if "resultados" in examen and isinstance(examen["resultados"], list):
        for resultado in examen["resultados"]:
            resultado = normalizar_pregunta_spaced_repetition(resultado)
    
    # Asegurar intervalos enteros en el examen mismo
    if "intervalo" in examen and isinstance(examen["intervalo"], (int, float)):
        examen["intervalo"] = max(1, int(round(examen["intervalo"])))
    
    return examen

def normalizar_pregunta_spaced_repetition(pregunta_dict: dict) -> dict:
    """
    Normaliza una pregunta para incluir todos los campos necesarios para Spaced Repetition.
    
    Correcciones aplicadas:
    1. Tipos de pregunta: "verdadero-falso" → "verdadero_falso", "multiple" → "mcq"
    2. Intervalos: decimales → enteros, mínimo 1 día
    3. Campos SM-2: asegura todos los campos requeridos
    """
    # 🔥 CORRECCIÓN 1: Normalizar tipo de pregunta
    tipo_mapa = {
        "verdadero-falso": "verdadero_falso",
        "true_false": "verdadero_falso",
        "true-false": "verdadero_falso",
        "vf": "verdadero_falso",
        "multiple": "mcq",
        "opcion_multiple": "mcq",
        "multiple_choice": "mcq",
        "corta": "short_answer",
        "short-answer": "short_answer",
        "desarrollo": "open_question",
        "abierta": "open_question"
    }
    
    if 'tipo' in pregunta_dict:
        tipo_original = pregunta_dict['tipo']
        pregunta_dict['tipo'] = tipo_mapa.get(tipo_original, tipo_original)
    
    # 🔥 CORRECCIÓN 2: Intervalos enteros (no decimales)
    if 'intervalo' in pregunta_dict and isinstance(pregunta_dict['intervalo'], (int, float)):
        pregunta_dict['intervalo'] = max(1, int(round(pregunta_dict['intervalo'])))
    
    if 'interval' in pregunta_dict and isinstance(pregunta_dict['interval'], (int, float)):
        pregunta_dict['interval'] = max(1, int(round(pregunta_dict['interval'])))
    
    # Generar ID único si no existe
    if 'id' not in pregunta_dict or not pregunta_dict['id']:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        tipo = pregunta_dict.get('tipo', pregunta_dict.get('type', 'question'))
        pregunta_dict['id'] = f"{tipo}_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    # Campos de Spaced Repetition (nomenclatura española)
    if 'facilidad' not in pregunta_dict:
        pregunta_dict['facilidad'] = 2.5
    
    if 'intervalo' not in pregunta_dict:
        pregunta_dict['intervalo'] = 1  # Mínimo 1 día
    
    if 'repeticiones' not in pregunta_dict:
        pregunta_dict['repeticiones'] = 0
    
    if 'ultimaRevision' not in pregunta_dict:
        pregunta_dict['ultimaRevision'] = None
    
    if 'proximaRevision' not in pregunta_dict:
        pregunta_dict['proximaRevision'] = None
    
    if 'estadoRevision' not in pregunta_dict:
        pregunta_dict['estadoRevision'] = 'nueva'
    
    return pregunta_dict


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
        modelo_ollama = config.get("modelo_ollama_activo", "Meta-Llama-3.1-8B-Instruct-Q4-K-L")
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


# Función para verificar y arrancar Ollama
def verificar_y_arrancar_ollama():
    """Verifica si Ollama está corriendo y lo arranca si no lo está"""
    import subprocess
    import platform
    
    try:
        # Verificar si Ollama responde
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("✅ Ollama ya está corriendo")
            return True
    except:
        print("⚠️ Ollama no está corriendo, iniciando...")
        
    try:
        # Arrancar Ollama en segundo plano
        if platform.system() == "Windows":
            subprocess.Popen(
                ["ollama", "serve"],
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        # Esperar a que Ollama arranque
        import time
        for i in range(10):
            time.sleep(1)
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=1)
                if response.status_code == 200:
                    print("✅ Ollama iniciado correctamente")
                    return True
            except:
                continue
        
        print("⚠️ Ollama no pudo iniciarse automáticamente")
        return False
    except Exception as e:
        print(f"❌ Error al iniciar Ollama: {e}")
        return False


# Inicializar modelo al arrancar
@app.on_event("startup")
async def startup_event():
    """Se ejecuta cuando arranca el servidor"""
    print("\n" + "="*60)
    print("🚀 INICIANDO EXAMINATOR API SERVER")
    print("="*60)
    
    # Verificar y arrancar Ollama automáticamente
    verificar_y_arrancar_ollama()
    
    # Inicializar modelo
    inicializar_modelo()
    
    print("="*60)
    print("✅ Servidor listo en http://localhost:8000")
    print("="*60 + "\n")


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
            config["usar_ollama"] = True
            # Para Ollama, gpu_activa depende de n_gpu_layers
            gpu_layers = generador_actual.n_gpu_layers if hasattr(generador_actual, 'n_gpu_layers') else 35
            config["gpu_activa"] = gpu_layers > 0
            print(f"📊 GET /api/config - Ollama detectado:")
            print(f"   usar_ollama={config['usar_ollama']}, gpu_activa={config['gpu_activa']}, n_gpu_layers={gpu_layers}")
        elif hasattr(generador_actual, 'modelo_path_gguf') and generador_actual.modelo_path_gguf:
            config["modelo_cargado"] = generador_actual.modelo_path_gguf
            config["modelo_activo"] = True
            config["tipo_motor"] = "gguf"
            config["usar_ollama"] = False
            gpu_layers = generador_actual.n_gpu_layers if hasattr(generador_actual, 'n_gpu_layers') else 0
            config["gpu_activa"] = gpu_layers > 0
        else:
            config["modelo_cargado"] = None
            config["modelo_activo"] = False
            config["tipo_motor"] = None
            config["usar_ollama"] = False
            config["gpu_activa"] = False
    else:
        config["modelo_cargado"] = None
        config["modelo_activo"] = False
        config["tipo_motor"] = None
        config["usar_ollama"] = False
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


@app.get("/api/diagnostico/ollama")
async def diagnostico_ollama():
    """Verifica el estado de Ollama y devuelve información de diagnóstico"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            modelos = response.json()
            return {
                "estado": "ok",
                "corriendo": True,
                "mensaje": "Ollama está funcionando correctamente",
                "modelos_disponibles": len(modelos.get("models", [])),
                "puerto": 11434
            }
        else:
            return {
                "estado": "error",
                "corriendo": False,
                "mensaje": f"Ollama responde pero con error (código {response.status_code})",
                "puerto": 11434
            }
    except requests.exceptions.ConnectionError:
        return {
            "estado": "error",
            "corriendo": False,
            "mensaje": "Ollama no está corriendo. Usa el botón 'Reparar' para iniciarlo.",
            "puerto": 11434
        }
    except Exception as e:
        return {
            "estado": "error",
            "corriendo": False,
            "mensaje": f"Error al verificar Ollama: {str(e)}",
            "puerto": 11434
        }


@app.post("/api/diagnostico/reparar-ollama")
async def reparar_ollama():
    """Intenta reparar Ollama arrancándolo automáticamente"""
    import subprocess
    import platform
    import time
    
    # Primero verificar si ya está corriendo
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            return {
                "success": True,
                "mensaje": "✅ Ollama ya está funcionando correctamente",
                "accion": "ninguna"
            }
    except:
        pass
    
    # Intentar arrancar Ollama
    try:
        print("\n🔧 Intentando reparar Ollama...")
        
        if platform.system() == "Windows":
            subprocess.Popen(
                ["ollama", "serve"],
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        # Esperar a que Ollama arranque (máximo 15 segundos)
        for i in range(15):
            time.sleep(1)
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=1)
                if response.status_code == 200:
                    print("✅ Ollama reparado exitosamente")
                    return {
                        "success": True,
                        "mensaje": "✅ Ollama iniciado correctamente. El chatbot ya está disponible.",
                        "accion": "iniciado",
                        "tiempo_arranque": f"{i+1} segundos"
                    }
            except:
                continue
        
        # Si llegamos aquí, no arrancó
        return {
            "success": False,
            "mensaje": "⚠️ Ollama no pudo iniciarse automáticamente. Intenta manualmente: ollama serve",
            "accion": "fallido"
        }
        
    except FileNotFoundError:
        return {
            "success": False,
            "mensaje": "❌ Ollama no está instalado en el sistema. Descárgalo de https://ollama.ai",
            "accion": "no_instalado"
        }
    except Exception as e:
        print(f"❌ Error al reparar Ollama: {e}")
        return {
            "success": False,
            "mensaje": f"❌ Error al iniciar Ollama: {str(e)}",
            "accion": "error"
        }


@app.post("/api/chat")
async def chat_con_modelo(data: dict):
    """Endpoint para chatear con el modelo (soporta Ollama y GGUF con fallback automático)"""
    global generador_actual
    
    mensaje = data.get("mensaje", "").strip()
    if not mensaje:
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")
    
    print(f"\n{'='*70}")
    print(f"💬 CHAT REQUEST RECIBIDA")
    print(f"{'='*70}")
    print(f"📝 Mensaje: {mensaje[:100]}...")
    print(f"🔍 DEBUG - Datos recibidos: {list(data.keys())}")
    print(f"🔍 DEBUG - buscar_web en data: {'buscar_web' in data}")
    if 'buscar_web' in data:
        print(f"🔍 DEBUG - Valor buscar_web: {data['buscar_web']} (tipo: {type(data['buscar_web'])})")
    
    # Verificar si hay modelo cargado
    if generador_actual is None:
        print("❌ generador_actual es None")
        return {"respuesta": "❌ No hay modelo inicializado. Ve a Configuración para seleccionar uno."}
    
    print(f"✅ Generador actual existe")
    print(f"🔧 Tipo configurado: {'Ollama' if generador_actual.usar_ollama else 'GGUF'}")
    
    # Si está configurado para Ollama, intentar usarlo con fallback a GGUF
    usar_ollama_exitoso = False
    if generador_actual.usar_ollama:
        try:
            # Verificar si Ollama está disponible
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                usar_ollama_exitoso = True
                print("✅ Ollama disponible - usando Ollama")
            else:
                print(f"⚠️ Ollama no responde (status {response.status_code}) - fallback a GGUF")
        except Exception as e:
            print(f"⚠️ Ollama no disponible ({str(e)}) - fallback a GGUF")
    
    # Si no usa Ollama o falló, verificar GGUF
    if not usar_ollama_exitoso:
        if generador_actual.llm is None:
            return {"respuesta": "❌ Ollama no está disponible y no hay modelo GGUF cargado. Por favor:\n\n1. Inicia Ollama con: ollama serve\n2. O carga un modelo GGUF desde Configuración"}
        print(f"✅ LLM GGUF cargado correctamente - usando fallback")
    
    try:
        # Obtener ajustes avanzados del frontend
        ajustes = data.get("ajustes", {})
        temperature = ajustes.get("temperature", 0.7)
        max_tokens = ajustes.get("max_tokens", 768)
        
        print(f"\n{'='*60}")
        print(f"💬 Solicitud de chat")
        print(f"⚙️ Temperatura: {temperature} | Max tokens: {max_tokens}")
        print(f"{'='*60}\n")
        
        # Preparar el contexto si existe
        contexto = data.get("contexto", None)
        
        # Obtener buscar_web del data principal o del último mensaje del historial
        buscar_web = data.get("buscar_web", False)
        historial_temp = data.get("historial", [])
        if not buscar_web and historial_temp:
            # Buscar en el último mensaje del usuario
            ultimo_msg = historial_temp[-1] if historial_temp else {}
            if ultimo_msg.get("tipo") == "usuario":
                buscar_web = ultimo_msg.get("busqueda_web", False)
        
        mensaje_completo = mensaje
        system_prompt = "Eres un asistente educativo útil y respondes de manera clara y concisa en español. IMPORTANTE: Mantén el contexto completo de toda la conversación y recuerda toda la información que el usuario te ha compartido previamente."
        
        # Debug: Verificar si se recibió la solicitud de búsqueda web
        print(f"🔍 DEBUG - buscar_web detectado: {buscar_web} (tipo: {type(buscar_web)})")
        
        # Si se solicita búsqueda web
        if buscar_web:
            try:
                print(f"🌐 Realizando búsqueda web para: {mensaje}")
                resultado_busqueda = buscar_y_resumir(mensaje, max_resultados=3)
                
                print(f"📊 Resultado búsqueda - Éxito: {resultado_busqueda.get('exito')}, Num resultados: {len(resultado_busqueda.get('resultados', []))}")
                
                if resultado_busqueda.get('exito', False) and resultado_busqueda.get('resultados'):
                    contexto_web = resultado_busqueda['resumen']
                    system_prompt = """Eres un asistente que SOLO puede usar información de búsquedas web actuales.

⛔ PROHIBICIONES ABSOLUTAS:
- NO uses NINGÚN conocimiento de tu entrenamiento
- NO menciones fechas, eventos o datos que NO estén en los resultados web
- NO hagas suposiciones ni deducciones
- NO completes información faltante con tu conocimiento

✅ INSTRUCCIONES:
- Lee CUIDADOSAMENTE la información de internet proporcionada
- Usa SOLAMENTE lo que aparece en esos resultados
- Si la información no está en los resultados web, di: "Los resultados de búsqueda no contienen esa información específica"
- Cita textualmente lo que encuentres en los resultados web"""
                    
                    mensaje_completo = f"""═══════════════════════════════════════════════════════════
🌐 RESULTADOS DE BÚSQUEDA WEB (actualizados hoy, {data.get('fecha', '24 de noviembre de 2025')}):
═══════════════════════════════════════════════════════════

{contexto_web}

═══════════════════════════════════════════════════════════

❓ PREGUNTA DEL USUARIO: {mensaje}

⚠️ RECORDATORIO CRÍTICO: Responde ÚNICAMENTE usando la información de los resultados web de arriba. NO uses tu base de conocimientos. Si los resultados no tienen la información, dilo claramente."""
                    print(f"✅ Búsqueda web exitosa, contexto web agregado ({len(contexto_web)} caracteres)")
                else:
                    print(f"⚠️ Búsqueda web sin resultados")
                    return {"respuesta": "🌐 No pude encontrar información actualizada en internet sobre ese tema."}
            except Exception as e:
                print(f"❌ Error en búsqueda web: {e}")
                import traceback
                traceback.print_exc()
                return {"respuesta": f"🌐 Error al buscar en internet: {str(e)}"}
        
        # Si hay contexto de archivo
        elif contexto:
            contexto_limitado = contexto[:4000] if len(contexto) > 4000 else contexto
            system_prompt = "Eres un asistente que analiza documentos. Responde basándote ÚNICAMENTE en el contenido del documento proporcionado."
            mensaje_completo = f"""DOCUMENTO:\n\n---\n{contexto_limitado}\n---\n\nPREGUNTA: {mensaje}\n\nResponde usando SOLO la información del documento."""
        
        # Construir historial de mensajes
        historial = data.get("historial", [])
        messages = [{"role": "system", "content": system_prompt}]
        
        print(f"\n{'='*70}")
        print(f"📥 HISTORIAL RECIBIDO DEL FRONTEND")
        print(f"{'='*70}")
        print(f"📊 Total mensajes recibidos: {len(historial)}")
        
        # Agregar historial previo
        if historial:
            # Tomar más mensajes del historial para mejor contexto
            historial_reciente = historial[-30:]  # Últimos 30 mensajes (15 intercambios)
            if buscar_web:
                # NO incluir historial para búsqueda web - solo la pregunta actual
                # Esto evita que el modelo se confunda con conocimiento de conversaciones previas
                historial_reciente = []
                # Bajar temperatura para búsqueda web (más precisa)
                temperature = min(temperature, 0.2)
            elif contexto:
                historial_reciente = historial[-12:]  # 6 intercambios con contexto
            
            print(f"📌 Mensajes a procesar: {len(historial_reciente)} (filtrados de {len(historial)} totales)")
            print(f"\n🔍 CONSTRUYENDO CONTEXTO PARA EL MODELO:")
            print(f"1. [SYSTEM] {system_prompt[:80]}...")
            
            # Procesar TODOS los mensajes del historial
            for i, msg in enumerate(historial_reciente):
                tipo = msg.get('tipo', 'unknown')
                texto = msg.get('texto', '')
                preview = texto[:100] if len(texto) > 100 else texto
                
                if tipo == 'usuario':
                    messages.append({"role": "user", "content": texto})
                    print(f"{len(messages)}. [USER] {preview}...")
                elif tipo == 'asistente':
                    messages.append({"role": "assistant", "content": texto})
                    print(f"{len(messages)}. [ASSISTANT] {preview}...")
            
            # SIEMPRE agregar el mensaje actual (con búsqueda web o contexto si aplica)
            messages.append({"role": "user", "content": mensaje_completo})
            print(f"{len(messages)}. [USER - ACTUAL] {mensaje_completo[:100]}...")
        else:
            # Si no hay historial, agregar mensaje actual
            messages.append({"role": "user", "content": mensaje_completo})
            print(f"{len(messages)}. [USER - ACTUAL] {mensaje_completo[:100]}...")
        
        print(f"\n📨 TOTAL MENSAJES ENVIADOS AL MODELO: {len(messages)}")
        if historial:
            print(f"   └─ 1 system + {len(messages)-1} historial (incluyendo mensaje actual)")
        else:
            print(f"   └─ 1 system + 1 mensaje actual")
        
        if buscar_web:
            print(f"   └─ ⚠️ MODO BÚSQUEDA WEB ACTIVO: Sin historial, solo información fresca de internet")
        
        print(f"{'='*70}\n")
        
        # Generar respuesta usando GeneradorUnificado con fallback
        print(f"🤖 Generando respuesta con temperatura={temperature}, max_tokens={max_tokens}")
        print(f"🔧 Usando {'Ollama' if usar_ollama_exitoso else 'GGUF/GPU (fallback)'}")
        
        if usar_ollama_exitoso:
            # Usar Ollama API de chat con historial completo
            respuesta_texto = generador_actual._generar_ollama_chat(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
        else:
            # Usar GGUF/llama-cpp (GPU o CPU)
            respuesta = generador_actual.llm.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=ajustes.get('top_p', 0.9),
                repeat_penalty=ajustes.get('repeat_penalty', 1.15),
                stop=["\n\nHuman:", "\n\nUser:", "</s>"]
            )
            respuesta_texto = respuesta['choices'][0]['message']['content'].strip()
        
        if not respuesta_texto:
            respuesta_texto = "Lo siento, no pude generar una respuesta. Intenta de nuevo."
        
        # Agregar prefijo si se usó búsqueda web
        if buscar_web:
            respuesta_texto = f"🌐 *Información actualizada de Internet:*\n\n{respuesta_texto}"
        
        print(f"✅ Respuesta generada: {len(respuesta_texto)} caracteres")
        print(f"📝 Preview: {respuesta_texto[:100]}...\n")
        
        return {"respuesta": respuesta_texto}
        
    except Exception as e:
        print(f"❌ Error en chat: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generando respuesta: {str(e)}")


@app.post("/api/guardar-nota-txt")
async def guardar_nota_txt(datos: dict):
    """Guarda una nota como archivo TXT en la carpeta especificada"""
    try:
        carpeta = datos.get("carpeta", "")
        nombre_archivo = datos.get("nombreArchivo", "nota.txt")
        contenido = datos.get("contenido", "")
        
        # Construir ruta completa
        if carpeta:
            ruta_completa = cursos_db.base_path / carpeta / nombre_archivo
        else:
            ruta_completa = cursos_db.base_path / nombre_archivo
        
        # Crear carpeta si no existe
        ruta_completa.parent.mkdir(parents=True, exist_ok=True)
        
        # Guardar archivo
        with open(ruta_completa, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        return {"success": True, "message": f"Nota guardada en {ruta_completa}"}
    except Exception as e:
        print(f"❌ Error guardando nota: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/subir-imagen-nota")
async def subir_imagen_nota(file: UploadFile = File(...), carpeta: str = Form("")):
    """Sube una imagen y la guarda en la carpeta de la nota"""
    try:
        import base64
        
        # Crear carpeta de imágenes dentro de la carpeta de la nota
        if carpeta:
            carpeta_imagenes = cursos_db.base_path / carpeta / "imagenes"
        else:
            carpeta_imagenes = cursos_db.base_path / "imagenes"
        
        carpeta_imagenes.mkdir(parents=True, exist_ok=True)
        
        # Generar nombre único para la imagen
        extension = Path(file.filename).suffix or ".png"
        nombre_imagen = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{extension}"
        ruta_imagen = carpeta_imagenes / nombre_imagen
        
        # Guardar imagen
        contenido = await file.read()
        with open(ruta_imagen, 'wb') as f:
            f.write(contenido)
        
        # Retornar ruta relativa para usar en el frontend
        ruta_relativa = str(ruta_imagen.relative_to(cursos_db.base_path))
        
        print(f"✅ Imagen guardada: {ruta_imagen}")
        
        return {
            "success": True,
            "ruta": ruta_relativa,
            "url": f"/api/imagen/{ruta_relativa.replace(chr(92), '/')}",
            "nombre": nombre_imagen
        }
    except Exception as e:
        print(f"❌ Error subiendo imagen: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/imagen/{ruta:path}")
async def obtener_imagen(ruta: str):
    """Sirve una imagen guardada"""
    try:
        from fastapi.responses import FileResponse
        
        ruta_imagen = cursos_db.base_path / ruta
        
        if not ruta_imagen.exists():
            raise HTTPException(status_code=404, detail="Imagen no encontrada")
        
        # Determinar tipo MIME
        extension = ruta_imagen.suffix.lower()
        mimes = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml'
        }
        mime = mimes.get(extension, 'application/octet-stream')
        
        return FileResponse(ruta_imagen, media_type=mime)
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error sirviendo imagen: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/imagen/{ruta:path}")
async def eliminar_imagen(ruta: str):
    """Elimina una imagen del servidor"""
    try:
        ruta_imagen = cursos_db.base_path / ruta
        
        if not ruta_imagen.exists():
            # Si no existe, igual retornamos éxito (ya fue eliminada)
            return {"success": True, "mensaje": "Imagen ya eliminada o no encontrada"}
        
        # Eliminar el archivo
        ruta_imagen.unlink()
        print(f"🗑️ Imagen eliminada: {ruta_imagen}")
        
        return {"success": True, "mensaje": "Imagen eliminada correctamente"}
    except Exception as e:
        print(f"❌ Error eliminando imagen: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/guardar_contexto_ejercicio")
async def guardar_contexto_ejercicio(datos: dict):
    """Guarda el contenido de una nota como contexto TXT para generar ejercicios"""
    try:
        carpeta = datos.get("carpeta", "contexto_ejercicios")
        titulo = datos.get("titulo", f"contexto_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        contenido = datos.get("contenido", "")
        tags = datos.get("tags", "")
        
        # Limpiar nombre de archivo
        nombre_archivo = f"{titulo}.txt"
        nombre_archivo = nombre_archivo.replace('/', '_').replace('\\', '_')
        
        # Construir ruta completa
        ruta_completa = cursos_db.base_path / carpeta / nombre_archivo
        
        # Crear carpeta si no existe
        ruta_completa.parent.mkdir(parents=True, exist_ok=True)
        
        # Preparar contenido con metadatos
        contenido_completo = f"""# {titulo}
# Tags: {tags}
# Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{contenido}
"""
        
        # Guardar archivo
        with open(ruta_completa, 'w', encoding='utf-8') as f:
            f.write(contenido_completo)
        
        print(f"✅ Contexto guardado: {ruta_completa}")
        
        return {
            "success": True,
            "message": f"Contexto guardado exitosamente",
            "ruta": str(ruta_completa.relative_to(cursos_db.base_path)),
            "archivo": nombre_archivo
        }
    except Exception as e:
        print(f"❌ Error guardando contexto: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat_anterior")
async def chat_con_modelo(data: dict):
    """Endpoint para chatear con el modelo (soporta Ollama y GGUF)"""
    global generador_actual
    
    mensaje = data.get("mensaje", "").strip()
    if not mensaje:
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")
    
    print(f"\n{'='*70}")
    print(f"💬 CHAT REQUEST RECIBIDA")
    print(f"{'='*70}")
    print(f"📝 Mensaje: {mensaje[:100]}...")
    
    # Verificar si hay modelo cargado
    if generador_actual is None:
        print("❌ generador_actual es None")
        return {"respuesta": "❌ No hay modelo inicializado. Ve a Configuración para seleccionar uno."}
    
    print(f"✅ Generador actual existe")
    print(f"🔧 Tipo: {'Ollama' if generador_actual.usar_ollama else 'GGUF'}")
    
    if not generador_actual.usar_ollama:
        if generador_actual.llm is None:
            print("❌ generador_actual.llm es None (GGUF no cargado)")
            return {"respuesta": "❌ Modelo GGUF no está cargado. Ve a Configuración y carga un modelo."}
        print(f"✅ LLM cargado correctamente")
    
    try:
        # Obtener ajustes avanzados del frontend
        ajustes = data.get("ajustes", {})
        temperature = ajustes.get("temperature", 0.7)
        max_tokens = ajustes.get("max_tokens", 768)
        
        print(f"\n{'='*60}")
        print(f"💬 Solicitud de chat")
        print(f"⚙️ Temperatura: {temperature} | Max tokens: {max_tokens}")
        print(f"{'='*60}\n")
        
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
                
                if resultado_busqueda.get('exito', False) and resultado_busqueda.get('resultados'):
                    contexto_web = resultado_busqueda['resumen']
                    system_prompt = "Eres un asistente que tiene acceso a información de internet. DEBES usar ÚNICAMENTE la información proporcionada de las búsquedas web para responder."
                    mensaje_completo = f"""INFORMACIÓN DE BÚSQUEDA WEB:\n\n{contexto_web}\n\n---\n\nPREGUNTA DEL USUARIO: {mensaje}\n\nResponde usando SOLO la información de búsqueda web proporcionada."""
                else:
                    return {"respuesta": "🌐 No pude encontrar información actualizada en internet sobre ese tema."}
            except Exception as e:
                print(f"❌ Error en búsqueda web: {e}")
                return {"respuesta": f"🌐 Error al buscar en internet: {str(e)}"}
        
        # Si hay contexto de archivo
        elif contexto:
            contexto_limitado = contexto[:4000] if len(contexto) > 4000 else contexto
            system_prompt = "Eres un asistente que analiza documentos. Responde basándote ÚNICAMENTE en el contenido del documento proporcionado."
            mensaje_completo = f"""DOCUMENTO:\n\n---\n{contexto_limitado}\n---\n\nPREGUNTA: {mensaje}\n\nResponde usando SOLO la información del documento."""
        
        # Construir historial de mensajes
        historial = data.get("historial", [])
        messages = [{"role": "system", "content": system_prompt}]
        
        # Agregar historial previo
        if historial:
            historial_reciente = historial[-10:]  # Últimos 10 mensajes
            if buscar_web:
                historial_reciente = historial[-6:]
            elif contexto:
                historial_reciente = historial[-4:]
            
            for msg in historial_reciente:
                if msg.get('tipo') == 'usuario':
                    messages.append({"role": "user", "content": msg.get('texto', '')})
                elif msg.get('tipo') == 'asistente':
                    messages.append({"role": "assistant", "content": msg.get('texto', '')})
        
        # Agregar mensaje actual
        messages.append({"role": "user", "content": mensaje_completo})
        
        # Generar respuesta usando GeneradorUnificado (soporta Ollama y GGUF)
        print(f"🤖 Generando respuesta con temperatura={temperature}, max_tokens={max_tokens}")
        print(f"🔧 Usando {'Ollama' if generador_actual.usar_ollama else 'GGUF/GPU'}")
        
        if generador_actual.usar_ollama:
            # Usar Ollama para chat
            respuesta_texto = generador_actual._generar_ollama(
                prompt=mensaje_completo,
                max_tokens=max_tokens,
                temperature=temperature
            )
        else:
            # Usar GGUF/llama-cpp (GPU o CPU)
            if generador_actual.llm is None:
                return {"respuesta": "❌ Modelo GGUF no está cargado. Ve a Configuración y carga un modelo."}
            
            respuesta = generador_actual.llm.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=ajustes.get('top_p', 0.9),
                repeat_penalty=ajustes.get('repeat_penalty', 1.15),
                stop=["\n\nHuman:", "\n\nUser:", "</s>"]
            )
            respuesta_texto = respuesta['choices'][0]['message']['content'].strip()
        
        if not respuesta_texto:
            respuesta_texto = "Lo siento, no pude generar una respuesta. Intenta de nuevo."
        
        print(f"✅ Respuesta generada: {len(respuesta_texto)} caracteres")
        print(f"📝 Preview: {respuesta_texto[:100]}...\n")
        return {"respuesta": respuesta_texto}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
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


@app.get("/api/archivos/recientes")
async def obtener_archivos_recientes(limite: int = 30):
    """Obtiene los archivos más recientes de todas las carpetas del sistema (cursos, notas, exámenes, prácticas)"""
    try:
        archivos = []
        
        # 1. Obtener archivos de cursos recursivamente
        def obtener_archivos_recursivo(ruta_relativa: str = ""):
            datos = cursos_db.listar_documentos(ruta_relativa)
            
            for doc in datos:
                ruta_completa = cursos_db.base_path / doc['ruta']
                if ruta_completa.exists() and ruta_completa.is_file():
                    stat = ruta_completa.stat()
                    archivos.append({
                        'nombre': doc['nombre'],
                        'ruta_completa': doc['ruta'],
                        'tipo': doc.get('tipo', 'Documento'),
                        'extension': ruta_completa.suffix,
                        'tamaño': stat.st_size,
                        'modificado': stat.st_mtime,
                        'carpeta': ruta_relativa or 'Cursos'
                    })
            
            # Buscar en subcarpetas
            carpetas = cursos_db.listar_carpetas(ruta_relativa)
            for carpeta in carpetas:
                obtener_archivos_recursivo(carpeta['ruta'])
        
        # Iniciar búsqueda recursiva desde la raíz de cursos
        obtener_archivos_recursivo()
        
        # 2. Obtener notas desde extracciones/*/notas.json
        extracciones_base = EXTRACCIONES_PATH
        if extracciones_base.exists():
            for carpeta in extracciones_base.iterdir():
                if carpeta.is_dir():
                    notas_json = carpeta / 'notas.json'
                    if notas_json.exists():
                        try:
                            with open(notas_json, 'r', encoding='utf-8') as f:
                                notas = json.load(f)
                            for idx, nota in enumerate(notas):
                                titulo = nota.get('titulo', f'Nota {idx+1}')
                                contenido = nota.get('contenido', '')
                                fecha_modificacion = nota.get('fechaModificacion', nota.get('fecha', ''))
                                try:
                                    if isinstance(fecha_modificacion, str) and fecha_modificacion:
                                        from datetime import datetime
                                        dt = datetime.fromisoformat(fecha_modificacion.replace('Z', '+00:00'))
                                        timestamp = dt.timestamp()
                                    else:
                                        timestamp = notas_json.stat().st_mtime
                                except:
                                    timestamp = notas_json.stat().st_mtime
                                
                                archivos.append({
                                    'nombre': f"{titulo}.json",
                                    'ruta_completa': f"extracciones/{carpeta.name}/notas/{idx}",
                                    'tipo': 'Nota',
                                    'extension': '.json',
                                    'tamaño': len(contenido.encode('utf-8')),
                                    'modificado': timestamp,
                                    'carpeta': carpeta.name
                                })
                        except Exception as e:
                            print(f"⚠️ Error leyendo notas de {carpeta.name}: {e}")
        
        # 3. Obtener exámenes desde examenes/*.json
        examenes_path = Path("examenes")
        if examenes_path.exists():
            for archivo_examen in examenes_path.glob("*.json"):
                stat = archivo_examen.stat()
                archivos.append({
                    'nombre': archivo_examen.name,
                    'ruta_completa': str(archivo_examen),
                    'tipo': 'Examen',
                    'extension': '.json',
                    'tamaño': stat.st_size,
                    'modificado': stat.st_mtime,
                    'carpeta': 'Exámenes'
                })
        
        # 4. Obtener prácticas desde extracciones/*/resultados_practicas/*.json
        extracciones_base = EXTRACCIONES_PATH
        if extracciones_base.exists():
            practicas_encontradas = 0
            for carpeta in extracciones_base.iterdir():
                if carpeta.is_dir():
                    practicas_path = carpeta / 'resultados_practicas'
                    if practicas_path.exists():
                        for archivo_practica in practicas_path.glob("*.json"):
                            try:
                                stat = archivo_practica.stat()
                                # Leer el archivo para obtener el título y verificar que es una práctica
                                with open(archivo_practica, 'r', encoding='utf-8') as f:
                                    practica_data = json.load(f)
                                
                                # Verificar que tiene es_practica=true
                                if practica_data.get('es_practica', False):
                                    practicas_encontradas += 1
                                    titulo = practica_data.get('titulo', practica_data.get('carpeta_nombre', archivo_practica.stem))
                                    archivos.append({
                                        'nombre': f"{titulo}.json",
                                        'ruta_completa': str(archivo_practica.relative_to(Path.cwd())),
                                        'tipo': 'Práctica',
                                        'extension': '.json',
                                        'tamaño': stat.st_size,
                                        'modificado': stat.st_mtime,
                                        'carpeta': carpeta.name
                                    })
                            except Exception as e:
                                print(f"⚠️ Error leyendo práctica {archivo_practica}: {e}")
            print(f"✅ Prácticas encontradas en recientes: {practicas_encontradas}")
        
        # Ordenar por fecha de modificación (más recientes primero)
        archivos.sort(key=lambda x: x['modificado'], reverse=True)
        
        # Limitar cantidad
        archivos = archivos[:limite]
        
        return {'archivos': archivos}
    except Exception as e:
        print(f"❌ Error obteniendo archivos recientes: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/archivos/listar_documentos")
async def listar_documentos_carpeta(carpeta: str = "", recursivo: bool = False):
    """
    Lista documentos de una carpeta específica
    Si recursivo=True, incluye subcarpetas
    """
    try:
        print(f"📂 LISTAR DOCUMENTOS: carpeta='{carpeta}', recursivo={recursivo}")
        documentos = []
        
        # Base path
        if carpeta:
            carpeta_base = EXTRACCIONES_PATH / carpeta
        else:
            carpeta_base = EXTRACCIONES_PATH
        
        if not carpeta_base.exists():
            return {"documentos": []}
        
        def procesar_carpeta(ruta_carpeta: Path, ruta_relativa: str = ""):
            """Procesa una carpeta y retorna sus documentos"""
            docs_encontrados = []
            
            # Buscar archivos .txt (documentos extraídos)
            for archivo in ruta_carpeta.glob("*.txt"):
                # Ignorar carpetas de resultados
                if 'resultados' in archivo.parts or 'resultado' in archivo.parts:
                    continue
                
                try:
                    stat = archivo.stat()
                    nombre_relativo = str(archivo.relative_to(EXTRACCIONES_PATH))
                    
                    docs_encontrados.append({
                        'nombre': archivo.name,
                        'ruta': nombre_relativo,
                        'ruta_completa': str(archivo),
                        'tamaño_kb': round(stat.st_size / 1024, 2),
                        'carpeta': ruta_relativa or carpeta
                    })
                except Exception as e:
                    print(f"⚠️ Error procesando {archivo}: {e}")
            
            # Si es recursivo, procesar subcarpetas
            if recursivo:
                for subcarpeta in ruta_carpeta.iterdir():
                    if subcarpeta.is_dir():
                        # Ignorar carpetas de resultados
                        if 'resultados' in subcarpeta.name or 'resultado' in subcarpeta.name:
                            continue
                        
                        subruta_relativa = str(subcarpeta.relative_to(carpeta_base))
                        docs_subcarpeta = procesar_carpeta(subcarpeta, subruta_relativa)
                        docs_encontrados.extend(docs_subcarpeta)
            
            return docs_encontrados
        
        # Procesar carpeta
        documentos = procesar_carpeta(carpeta_base, "")
        
        print(f"✅ Documentos encontrados: {len(documentos)}")
        return {"documentos": documentos}
    
    except Exception as e:
        print(f"❌ Error listando documentos: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/archivos/explorar")
async def explorar_archivos_por_tipo(tipo: str, ruta: str = ""):
    """Explora archivos filtrados por tipo (notas, examenes, practicas, cursos)"""
    try:
        print(f"🔍 EXPLORAR: tipo='{tipo}', ruta='{ruta}', len={len(ruta)}, bool={bool(ruta)}")
        carpetas = []
        archivos = []
        
        # Para notas y flashcards, leer desde extracciones/*/
        if tipo in ['notas', 'flashcards']:
            extracciones_base = EXTRACCIONES_PATH
            
            if not extracciones_base.exists():
                return {
                    'carpetas': [],
                    'archivos': [],
                    'ruta_actual': ruta,
                    'tipo': tipo
                }
            
            # Si ruta está vacía o es None, mostrar carpetas disponibles
            if not ruta:
                carpetas_disponibles = []
                for carpeta in extracciones_base.iterdir():
                    if carpeta.is_dir():
                        archivo_json = carpeta / f"{tipo}.json"
                        if archivo_json.exists():
                            try:
                                with open(archivo_json, 'r', encoding='utf-8') as f:
                                    datos = json.load(f)
                                num_items = len(datos) if isinstance(datos, list) else 0
                                if num_items > 0:
                                    carpetas_disponibles.append({
                                        'nombre': carpeta.name,
                                        'ruta': carpeta.name,
                                        'num_archivos': num_items
                                    })
                            except Exception as e:
                                print(f"⚠️ Error leyendo {archivo_json}: {e}")
                
                return {
                    'carpetas': carpetas_disponibles,
                    'archivos': [],
                    'ruta_actual': '',
                    'tipo': tipo
                }
            
            # Si hay ruta específica, listar items de esa carpeta
            else:
                archivos = []
                carpeta_seleccionada = extracciones_base / ruta
                archivo_json = carpeta_seleccionada / f"{tipo}.json"
                if archivo_json.exists():
                    try:
                        with open(archivo_json, "r", encoding="utf-8") as f:
                            datos = json.load(f)
                        
                        # Crear un "archivo virtual" por cada nota/flashcard
                        for idx, item in enumerate(datos):
                            if tipo == 'notas':
                                titulo = item.get('titulo', f'Nota {idx+1}')
                                contenido = item.get('contenido', '')
                                # Obtener fecha de modificación de la nota
                                fecha_modificacion = item.get('fechaModificacion', item.get('fecha', ''))
                            else:  # flashcards
                                # Manejar diferentes formatos de flashcards
                                pregunta = item.get('pregunta', item.get('titulo', f'Flashcard {idx+1}'))
                                respuesta = item.get('respuesta', item.get('respuestaCorrecta', item.get('contenido', '')))
                                titulo = pregunta[:50] if pregunta else f'Flashcard {idx+1}'
                                contenido = f"Pregunta: {pregunta}\nRespuesta: {respuesta}"
                                # Obtener fecha de modificación de la flashcard
                                fecha_modificacion = item.get('fechaRevision', item.get('fechaModificacion', item.get('fecha', '')))
                            
                            # Convertir fecha a timestamp si es string
                            try:
                                if isinstance(fecha_modificacion, str) and fecha_modificacion:
                                    from datetime import datetime
                                    dt = datetime.fromisoformat(fecha_modificacion.replace('Z', '+00:00'))
                                    timestamp = dt.timestamp()
                                else:
                                    timestamp = archivo_json.stat().st_mtime
                            except:
                                timestamp = archivo_json.stat().st_mtime
                            
                            archivos.append({
                                'nombre': f"{titulo}.json",
                                'ruta_completa': f"extracciones/{ruta}/{tipo}/{idx}",  # Ruta virtual
                                'tipo': 'Nota' if tipo == 'notas' else 'Flashcard',
                                'extension': '.json',
                                'tamaño': len(contenido.encode('utf-8')),
                                'modificado': timestamp,
                                'contenido': contenido,  # Incluir contenido directamente
                                'item_original': item  # Para leer después
                            })
                    except Exception as e:
                        print(f"⚠️ Error leyendo {archivo_json}: {e}")
                
                # Ordenar por fecha de modificación descendente (más recientes primero)
                archivos.sort(key=lambda x: x.get('modificado', 0), reverse=True)
                
                return {
                    'carpetas': [],
                    'archivos': archivos,
                    'ruta_actual': ruta,
                    'tipo': tipo
                }
        
        # Para examenes, buscar en carpeta examenes/
        if tipo == 'examenes':
            examenes_base = EXAMENES_PATH  # Path("examenes")
            
            if not examenes_base.exists():
                return {
                    'carpetas': [],
                    'archivos': [],
                    'ruta_actual': ruta,
                    'tipo': tipo
                }
            
            # Si ruta está vacía, mostrar carpetas disponibles
            if not ruta:
                carpetas_examenes = []
                for carpeta in examenes_base.iterdir():
                    if carpeta.is_dir():
                        # Contar exámenes en esta carpeta (archivos examen_*.json)
                        num_examenes = len(list(carpeta.glob("examen_*.json")))
                        if num_examenes > 0:
                            carpetas_examenes.append({
                                'nombre': carpeta.name,
                                'ruta': carpeta.name,
                                'num_archivos': num_examenes
                            })
                
                return {
                    'carpetas': carpetas_examenes,
                    'archivos': [],
                    'ruta_actual': '',
                    'tipo': tipo
                }
            
            # Si hay ruta específica, listar exámenes de esa carpeta
            else:
                carpeta_seleccionada = examenes_base / ruta
                print(f"📂 Buscando exámenes en: {carpeta_seleccionada}")
                print(f"📂 ¿Existe?: {carpeta_seleccionada.exists()}")
                
                if carpeta_seleccionada.exists() and carpeta_seleccionada.is_dir():
                    for archivo_examen in carpeta_seleccionada.glob("examen_*.json"):
                        try:
                            stat = archivo_examen.stat()
                            
                            # Leer examen para obtener metadatos
                            with open(archivo_examen, 'r', encoding='utf-8') as f:
                                examen_data = json.load(f)
                            
                            # Generar título descriptivo
                            titulo = examen_data.get('titulo', archivo_examen.stem)
                            porcentaje = examen_data.get('resultado', {}).get('porcentaje', 
                                                        examen_data.get('porcentaje', 0))
                            
                            # Obtener fecha de completado
                            fecha_completado = examen_data.get('fecha_completado', '')
                            try:
                                if fecha_completado:
                                    from datetime import datetime
                                    dt = datetime.fromisoformat(fecha_completado.replace('Z', '+00:00'))
                                    timestamp = dt.timestamp()
                                else:
                                    timestamp = stat.st_mtime
                            except:
                                timestamp = stat.st_mtime
                            
                            archivos.append({
                                'nombre': f"{titulo}.json",
                                'ruta_completa': str(archivo_examen),
                                'tipo': 'Examen',
                                'extension': '.json',
                                'tamaño': stat.st_size,
                                'modificado': timestamp,
                                'carpeta': ruta,
                                'item_original': examen_data
                            })
                            print(f"✅ Examen encontrado: {titulo}")
                        except Exception as e:
                            print(f"⚠️ Error leyendo {archivo_examen}: {e}")
                
                # Ordenar por fecha de modificación descendente (más recientes primero)
                archivos.sort(key=lambda x: x.get('modificado', 0), reverse=True)
                
                print(f"📊 Total exámenes encontrados: {len(archivos)}")
                
                return {
                    'carpetas': [],
                    'archivos': archivos,
                    'ruta_actual': ruta,
                    'tipo': tipo
                }

        
        # Para prácticas, buscar en extracciones/*/practicas.json
        if tipo == 'practicas':
            extracciones_base = EXTRACCIONES_PATH
            carpetas_practicas = []
            
            if extracciones_base.exists():
                # Si no hay ruta específica, mostrar carpetas disponibles
                if not ruta:
                    for carpeta in extracciones_base.iterdir():
                        if carpeta.is_dir():
                            practicas_json = carpeta / 'practicas.json'
                            if practicas_json.exists():
                                try:
                                    with open(practicas_json, 'r', encoding='utf-8') as f:
                                        practicas_list = json.load(f)
                                    num_practicas = len(practicas_list) if isinstance(practicas_list, list) else 0
                                    if num_practicas > 0:
                                        carpetas_practicas.append({
                                            'nombre': carpeta.name,
                                            'ruta': carpeta.name,
                                            'num_archivos': num_practicas
                                        })
                                except Exception as e:
                                    print(f"⚠️ Error leyendo {practicas_json}: {e}")
                else:
                    # Listar prácticas de la carpeta específica desde practicas.json
                    carpeta_seleccionada = extracciones_base / ruta
                    practicas_json = carpeta_seleccionada / 'practicas.json'
                    print(f"📂 Buscando prácticas en: {practicas_json}")
                    print(f"📂 ¿Existe?: {practicas_json.exists()}")
                    
                    if practicas_json.exists():
                        try:
                            with open(practicas_json, 'r', encoding='utf-8') as f:
                                practicas_list = json.load(f)
                            
                            print(f"📄 Prácticas encontradas: {len(practicas_list)}")
                            stat = practicas_json.stat()
                            
                            # Crear un archivo virtual por cada práctica
                            for idx, practica_data in enumerate(practicas_list):
                                # Generar título descriptivo
                                if 'titulo' in practica_data and practica_data['titulo']:
                                    titulo = practica_data['titulo']
                                elif 'ruta' in practica_data:
                                    # Extraer nombre del archivo de la ruta
                                    ruta_archivo = practica_data['ruta']
                                    nombre_archivo = Path(ruta_archivo).stem  # Sin extensión
                                    titulo = f"Práctica: {nombre_archivo}"
                                else:
                                    titulo = f'Práctica {idx+1}'
                                
                                print(f"🔍 Práctica {idx+1}: {titulo}")
                                
                                # Obtener fecha de modificación
                                fecha_completado = practica_data.get('fecha_completado', '')
                                try:
                                    if fecha_completado:
                                        from datetime import datetime
                                        # Intentar parsear diferentes formatos de fecha
                                        if 'T' in fecha_completado:
                                            dt = datetime.fromisoformat(fecha_completado.replace('Z', '+00:00'))
                                        else:
                                            dt = datetime.strptime(fecha_completado, '%d/%m/%Y %H:%M:%S')
                                        timestamp = dt.timestamp()
                                    else:
                                        timestamp = stat.st_mtime
                                except:
                                    timestamp = stat.st_mtime
                                
                                # Formatear el contenido de la práctica
                                porcentaje = practica_data.get('porcentaje', 0)
                                
                                archivos.append({
                                    'nombre': f"{titulo}.json",
                                    'ruta_completa': f"extracciones/{ruta}/practicas/{idx}",  # Ruta virtual
                                    'tipo': 'Práctica',
                                    'extension': '.json',
                                    'tamaño': len(json.dumps(practica_data).encode('utf-8')),
                                    'modificado': timestamp,
                                    'item_original': practica_data,  # Para leer después
                                    'carpeta': ruta
                                })
                        except Exception as e:
                            print(f"⚠️ Error leyendo practicas.json: {e}")
                            import traceback
                            traceback.print_exc()
            
            # Ordenar archivos por fecha de modificación descendente (más recientes primero)
            archivos.sort(key=lambda x: x.get('modificado', 0), reverse=True)
            
            return {
                'carpetas': carpetas_practicas,
                'archivos': archivos,
                'ruta_actual': ruta,
                'tipo': tipo
            }
        
        # Para cursos, usar el sistema normal de cursos_db
        if tipo == 'cursos':
            extensiones_permitidas = ['.pdf', '.html', '.txt', '.md']
            
            # Obtener contenido de la carpeta
            datos_carpetas = cursos_db.listar_carpetas(ruta)
            datos_docs = cursos_db.listar_documentos(ruta)
            
            # Filtrar archivos por extensión
            for doc in datos_docs:
                ruta_completa = cursos_db.base_path / doc['ruta']
                if ruta_completa.suffix in extensiones_permitidas:
                    stat = ruta_completa.stat()
                    archivos.append({
                        'nombre': doc['nombre'],
                        'ruta_completa': doc['ruta'],
                        'tipo': doc.get('tipo', 'Documento'),
                        'extension': ruta_completa.suffix,
                        'tamaño': stat.st_size,
                        'modificado': stat.st_mtime
                    })
            
            # Agregar información de carpetas (para navegar)
            for carpeta in datos_carpetas:
                carpetas.append({
                    'nombre': carpeta['nombre'],
                    'ruta': carpeta['ruta'],
                    'num_archivos': carpeta.get('archivos', 0)
                })
            
            # Ordenar archivos por fecha de modificación descendente (más recientes primero)
            archivos.sort(key=lambda x: x.get('modificado', 0), reverse=True)
            
            return {
                'carpetas': carpetas,
                'archivos': archivos,
                'ruta_actual': ruta,
                'tipo': tipo
            }
        
        raise HTTPException(status_code=400, detail=f"Tipo '{tipo}' no válido. Usa: notas, examenes, practicas, cursos")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error explorando archivos por tipo: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/archivos/leer-contenido")
async def leer_contenido_archivo(data: dict):
    """Lee el contenido de un archivo"""
    try:
        ruta = data.get('ruta', '')
        if not ruta:
            raise HTTPException(status_code=400, detail="Ruta no proporcionada")
        
        print(f"📖 Leyendo contenido de: {ruta}")
        
        # Normalizar separadores de ruta (convertir \ a /)
        ruta_normalizada = ruta.replace('\\', '/')
        
        # Verificar si es una ruta virtual (notas/flashcards/practicas)
        if 'extracciones/' in ruta_normalizada and ('/notas/' in ruta_normalizada or '/flashcards/' in ruta_normalizada or '/practicas/' in ruta_normalizada):
            partes = ruta_normalizada.split('/')
            carpeta_nombre = partes[1]  # nombre de la carpeta (ej: 'Platzi', 'Sin carpeta')
            tipo = partes[2]  # 'notas', 'flashcards' o 'practicas'
            idx = int(partes[3])  # índice del item
            
            archivo_json = EXTRACCIONES_PATH / carpeta_nombre / f"{tipo}.json"
            if archivo_json.exists():
                with open(archivo_json, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                
                if idx < len(datos):
                    item = datos[idx]
                    
                    if tipo == 'notas':
                        contenido = f"# {item.get('titulo', 'Sin título')}\n\n{item.get('contenido', '')}"
                    elif tipo == 'flashcards':
                        # Manejar diferentes formatos
                        pregunta = item.get('pregunta', item.get('titulo', 'Sin pregunta'))
                        respuesta = item.get('respuesta', item.get('respuestaCorrecta', item.get('contenido', 'Sin respuesta')))
                        contenido = f"**Pregunta:**\n{pregunta}\n\n**Respuesta:**\n{respuesta}"
                        if item.get('categoria') or item.get('carpeta'):
                            cat = item.get('categoria', item.get('carpeta', ''))
                            if cat:
                                contenido = f"**Categoría:** {cat}\n\n" + contenido
                    elif tipo == 'practicas':
                        # Verificar si es práctica completada o en progreso
                        if 'resultados' in item and item['resultados']:
                            # Práctica completada
                            titulo = item.get('titulo', item.get('carpeta_nombre', 'Sin título'))
                            porcentaje = item.get('porcentaje', 0)
                            fecha = item.get('fecha_completado', item.get('fecha', 'Sin fecha'))
                            
                            contenido = f"# Práctica: {titulo}\n\n"
                            contenido += f"**Estado:** ✅ Completada\n"
                            contenido += f"**Fecha:** {fecha}\n"
                            contenido += f"**Puntuación:** {porcentaje:.1f}%\n\n"
                            contenido += f"## Preguntas\n\n"
                            
                            # Agregar preguntas y respuestas
                            resultados = item.get('resultados', [])
                            preguntas_correctas = []
                            preguntas_incorrectas = []
                            
                            for idx_res, resultado in enumerate(resultados, 1):
                                pregunta = resultado.get('pregunta', 'Sin pregunta')
                                respuesta_usuario = resultado.get('respuesta_usuario', 'Sin respuesta')
                                respuesta_correcta = resultado.get('respuesta_correcta', 'Sin respuesta correcta')
                                puntos = resultado.get('puntos', 0)
                                puntos_maximos = resultado.get('puntos_maximos', 0)
                                
                                # Determinar si fue correcta o incorrecta
                                es_correcta = puntos == puntos_maximos and puntos > 0
                                estado = "✅ CORRECTA" if es_correcta else "❌ INCORRECTA"
                                
                                # Clasificar
                                if es_correcta:
                                    preguntas_correctas.append(f"{idx_res}. {pregunta}")
                                else:
                                    preguntas_incorrectas.append(f"{idx_res}. {pregunta}")
                                
                                contenido += f"### {idx_res}. {pregunta} [{estado}]\n\n"
                                contenido += f"**Tu respuesta:** {respuesta_usuario}\n\n"
                                contenido += f"**Respuesta correcta:** {respuesta_correcta}\n\n"
                                contenido += f"**Puntos obtenidos:** {puntos}/{puntos_maximos}\n\n"
                                
                                if resultado.get('feedback'):
                                    contenido += f"**Feedback:**\n{resultado['feedback']}\n\n"
                                
                                contenido += "---\n\n"
                            
                            # Agregar resumen al final
                            contenido += "## 📊 Resumen\n\n"
                            contenido += f"**Preguntas correctas ({len(preguntas_correctas)}):**\n"
                            if preguntas_correctas:
                                for preg in preguntas_correctas:
                                    contenido += f"- {preg}\n"
                            else:
                                contenido += "- Ninguna\n"
                            
                            contenido += f"\n**Preguntas incorrectas ({len(preguntas_incorrectas)}):**\n"
                            if preguntas_incorrectas:
                                for preg in preguntas_incorrectas:
                                    contenido += f"- {preg}\n"
                            else:
                                contenido += "- Ninguna\n"
                        else:
                            # Práctica en progreso (sin completar)
                            ruta_origen = item.get('ruta', '')
                            nombre_archivo = Path(ruta_origen).stem if ruta_origen else 'Sin título'
                            titulo = item.get('titulo', f'Práctica: {nombre_archivo}')
                            fecha = item.get('fecha', 'Sin fecha')
                            
                            contenido = f"# {titulo}\n\n"
                            contenido += f"**Estado:** ⏳ En progreso (no completada)\n"
                            contenido += f"**Fecha creación:** {fecha}\n"
                            contenido += f"**Archivo origen:** {ruta_origen}\n\n"
                            
                            # Mostrar preguntas disponibles
                            preguntas = item.get('preguntas', [])
                            if preguntas:
                                contenido += f"## Preguntas ({len(preguntas)})\n\n"
                                for idx_preg, pregunta in enumerate(preguntas, 1):
                                    tipo_preg = pregunta.get('tipo', 'desconocido')
                                    texto_preg = pregunta.get('pregunta', 'Sin texto')
                                    puntos = pregunta.get('puntos', 0)
                                    respuesta_correcta = pregunta.get('respuesta_correcta', '')
                                    opciones = pregunta.get('opciones', [])
                                    metadata = pregunta.get('metadata', {})
                                    
                                    contenido += f"### {idx_preg}. [{tipo_preg.upper()}] - {puntos} puntos\n\n"
                                    contenido += f"**Pregunta:** {texto_preg}\n\n"
                                    
                                    # Mostrar opciones si existen (MCQ, True/False)
                                    if opciones:
                                        contenido += f"**Opciones:**\n"
                                        for opt in opciones:
                                            contenido += f"- {opt}\n"
                                        contenido += "\n"
                                    
                                    # Mostrar respuesta correcta
                                    if respuesta_correcta:
                                        contenido += f"**Respuesta correcta:** {respuesta_correcta}\n\n"
                                    
                                    # Información adicional del metadata
                                    if metadata:
                                        if metadata.get('answers'):
                                            contenido += f"**Respuestas esperadas:** {', '.join(metadata['answers'])}\n\n"
                                        if metadata.get('hint'):
                                            contenido += f"**Pista:** {metadata['hint']}\n\n"
                                        if metadata.get('key_points'):
                                            contenido += f"**Puntos clave a incluir:**\n"
                                            for kp in metadata['key_points']:
                                                contenido += f"- {kp}\n"
                                            contenido += "\n"
                                    
                                    contenido += "---\n\n"
                            else:
                                contenido += "No hay preguntas generadas.\n\n"
                            
                            contenido += f"\n💡 **Nota:** Esta práctica aún no ha sido completada. Ve a la sección de Prácticas para responderla.\n"
                    
                    return {
                        'success': True,
                        'contenido': contenido,
                        'ruta': ruta,
                        'tamaño': len(contenido)
                    }
            
            raise HTTPException(status_code=404, detail="Nota/Flashcard no encontrada")
        
        # Verificar si es un examen
        if ruta_normalizada.startswith('examenes/'):
            examen_path = Path(ruta)
            if examen_path.exists():
                with open(examen_path, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                return {
                    'success': True,
                    'contenido': contenido,
                    'ruta': ruta,
                    'tamaño': len(contenido)
                }
            raise HTTPException(status_code=404, detail="Examen no encontrado")
        
        # Verificar si es una práctica
        if ruta_normalizada.startswith('extracciones/') and 'resultados_practicas' in ruta_normalizada:
            practica_path = Path(ruta)
            print(f"📂 Buscando práctica en: {practica_path}")
            print(f"📂 Existe: {practica_path.exists()}")
            
            if practica_path.exists():
                with open(practica_path, 'r', encoding='utf-8') as f:
                    practica_data = json.load(f)
                
                # Formatear el contenido de la práctica de forma legible
                titulo = practica_data.get('titulo', practica_data.get('carpeta_nombre', 'Sin título'))
                porcentaje = practica_data.get('porcentaje', 0)
                fecha = practica_data.get('fecha_completado', 'Sin fecha')
                
                contenido = f"# Práctica: {titulo}\n\n"
                contenido += f"**Fecha:** {fecha}\n"
                contenido += f"**Puntuación:** {porcentaje:.1f}%\n\n"
                contenido += f"## Preguntas\n\n"
                
                # Agregar preguntas y respuestas
                resultados = practica_data.get('resultados', [])
                preguntas_correctas = []
                preguntas_incorrectas = []
                
                for idx, resultado in enumerate(resultados, 1):
                    pregunta = resultado.get('pregunta', 'Sin pregunta')
                    respuesta_usuario = resultado.get('respuesta_usuario', 'Sin respuesta')
                    respuesta_correcta = resultado.get('respuesta_correcta', 'Sin respuesta correcta')
                    puntos = resultado.get('puntos', 0)
                    puntos_maximos = resultado.get('puntos_maximos', 0)
                    
                    # Determinar si fue correcta o incorrecta
                    es_correcta = puntos == puntos_maximos and puntos > 0
                    estado = "✅ CORRECTA" if es_correcta else "❌ INCORRECTA"
                    
                    # Clasificar
                    if es_correcta:
                        preguntas_correctas.append(f"{idx}. {pregunta}")
                    else:
                        preguntas_incorrectas.append(f"{idx}. {pregunta}")
                    
                    contenido += f"### {idx}. {pregunta} [{estado}]\n\n"
                    contenido += f"**Tu respuesta:** {respuesta_usuario}\n\n"
                    contenido += f"**Respuesta correcta:** {respuesta_correcta}\n\n"
                    contenido += f"**Puntos obtenidos:** {puntos}/{puntos_maximos}\n\n"
                    
                    if resultado.get('feedback'):
                        contenido += f"**Feedback:**\n{resultado['feedback']}\n\n"
                    
                    contenido += "---\n\n"
                
                # Agregar resumen al final
                contenido += "## 📊 Resumen\n\n"
                contenido += f"**Preguntas correctas ({len(preguntas_correctas)}):**\n"
                if preguntas_correctas:
                    for preg in preguntas_correctas:
                        contenido += f"- {preg}\n"
                else:
                    contenido += "- Ninguna\n"
                
                contenido += f"\n**Preguntas incorrectas ({len(preguntas_incorrectas)}):**\n"
                if preguntas_incorrectas:
                    for preg in preguntas_incorrectas:
                        contenido += f"- {preg}\n"
                else:
                    contenido += "- Ninguna\n"
                
                return {
                    'success': True,
                    'contenido': contenido,
                    'ruta': ruta,
                    'tamaño': len(contenido)
                }
            raise HTTPException(status_code=404, detail="Práctica no encontrada")
        
        # Ruta normal del sistema de archivos
        ruta_completa = cursos_db.base_path / ruta
        
        if not ruta_completa.exists():
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
        if not ruta_completa.is_file():
            raise HTTPException(status_code=400, detail="La ruta no es un archivo")
        
        # Leer contenido según extensión
        try:
            if ruta_completa.suffix == '.pdf':
                contenido = obtener_texto(str(ruta_completa))
            elif ruta_completa.suffix in ['.txt', '.md', '.html', '.json']:
                with open(ruta_completa, 'r', encoding='utf-8') as f:
                    contenido = f.read()
            else:
                with open(ruta_completa, 'r', encoding='utf-8', errors='ignore') as f:
                    contenido = f.read()
            
            return {
                'success': True,
                'contenido': contenido,
                'ruta': ruta,
                'tamaño': len(contenido)
            }
        except Exception as e:
            print(f"❌ Error leyendo archivo {ruta}: {e}")
            raise HTTPException(status_code=500, detail=f"Error al leer archivo: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en leer-contenido: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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


@app.get("/api/cursos/carpetas")
async def listar_carpetas_cursos(ruta: str = ""):
    """Lista carpetas de cursos (alias de /api/carpetas)"""
    result = await listar_carpetas(ruta)
    # Agregar num_archivos como alias de num_documentos para compatibilidad
    for carpeta in result.get('carpetas', []):
        if 'num_documentos' in carpeta and 'num_archivos' not in carpeta:
            carpeta['num_archivos'] = carpeta['num_documentos']
    return result


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
async def obtener_arbol():
    """Obtiene el árbol completo de carpetas"""
    try:
        return cursos_db.obtener_arbol()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/carpetas/info")
async def obtener_info_carpeta(ruta: str = ""):
    """Obtiene información detallada de una carpeta específica"""
    try:
        # listar_carpetas retorna una lista de dicts, listar_documentos otra lista
        subcarpetas = cursos_db.listar_carpetas(ruta)
        documentos = cursos_db.listar_documentos(ruta)
        
        return {
            "num_documentos": len(documentos),
            "num_subcarpetas": len(subcarpetas),
            "ruta": ruta
        }
    except Exception as e:
        print(f"❌ Error obteniendo info de carpeta: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/carpetas/archivos-recursivos")
async def obtener_archivos_recursivos(ruta: str = ""):
    """Obtiene todos los archivos .txt recursivamente de una carpeta y sus subcarpetas"""
    try:
        print(f"\n{'='*70}")
        print(f"📂 OBTENER ARCHIVOS RECURSIVOS")
        print(f"{'='*70}")
        print(f"📁 Ruta: {ruta}")
        
        archivos = cursos_db.listar_documentos_recursivo(ruta)
        print(f"📚 Archivos encontrados: {len(archivos)}")
        
        return {
            "archivos": archivos,
            "total": len(archivos)
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generar_examen_bloque")
async def generar_examen_bloque(datos: dict):
    """Genera preguntas para un bloque de archivos"""
    print(f"\n{'='*70}")
    print(f"📝 GENERAR EXAMEN POR BLOQUE")
    print(f"{'='*70}")
    
    archivos = datos.get("archivos", [])
    config = datos.get("config", {})
    
    num_multiple = config.get("num_multiple", 2)
    num_corta = config.get("num_corta", 1)
    num_vf = config.get("num_vf", 1)
    num_desarrollo = config.get("num_desarrollo", 1)
    
    print(f"📚 Archivos en bloque: {len(archivos)}")
    print(f"📊 Config: M={num_multiple}, C={num_corta}, VF={num_vf}, D={num_desarrollo}")
    
    if not archivos:
        raise HTTPException(status_code=400, detail="No se especificaron archivos")
    
    if generador_actual is None:
        raise HTTPException(status_code=500, detail="Modelo no inicializado")
    
    try:
        # ESTRATEGIA: Generar preguntas por archivo individualmente
        # Esto evita que el modelo se quede sin tokens con exámenes grandes
        
        # Leer contenido de cada archivo
        archivos_contenido = []
        for archivo_obj in archivos:
            try:
                if isinstance(archivo_obj, dict):
                    ruta_archivo = archivo_obj.get('ruta', archivo_obj.get('nombre', ''))
                else:
                    ruta_archivo = archivo_obj
                
                resultado = cursos_db.obtener_contenido_documento(ruta_archivo)
                if resultado and 'contenido' in resultado:
                    contenido_texto = resultado['contenido']
                    nombre_archivo = Path(ruta_archivo).stem
                    archivos_contenido.append({
                        'nombre': nombre_archivo,
                        'ruta': ruta_archivo,
                        'contenido': contenido_texto,
                        'chars': len(contenido_texto)
                    })
                    print(f"  ✅ Leído: {nombre_archivo} ({len(contenido_texto)} chars)")
            except Exception as e:
                print(f"  ⚠️  Error leyendo {archivo_obj}: {e}")
        
        if not archivos_contenido:
            raise HTTPException(status_code=404, detail="No se pudo leer el contenido de los archivos")
        
        # Calcular total de caracteres
        total_chars = sum(a['chars'] for a in archivos_contenido)
        print(f"📄 Contenido total: {total_chars} caracteres en {len(archivos_contenido)} archivos")
        
        # Calcular distribución proporcional de preguntas por archivo
        total_preguntas = num_multiple + num_corta + num_vf + num_desarrollo
        
        print(f"\n🎯 Estrategia: Generar {total_preguntas} preguntas desde {len(archivos_contenido)} archivos")
        
        todas_preguntas = []
        
        for idx, archivo_info in enumerate(archivos_contenido, 1):
            # Calcular proporción de preguntas para este archivo
            proporcion = archivo_info['chars'] / total_chars
            preguntas_este_archivo = max(3, round(total_preguntas * proporcion * 2.0))  # Generar 100% más (x2)
            
            # Distribuir tipos de preguntas proporcionalmente
            num_preguntas_archivo = {
                'mcq': max(0, round(preguntas_este_archivo * 0.5)),  # 50% MCQ
                'short_answer': max(0, round(preguntas_este_archivo * 0.2)),  # 20% cortas
                'true_false': max(0, round(preguntas_este_archivo * 0.2)),  # 20% V/F
                'open_question': max(0, round(preguntas_este_archivo * 0.1))  # 10% desarrollo
            }
            
            total_calculado = sum(num_preguntas_archivo.values())
            if total_calculado < preguntas_este_archivo:
                num_preguntas_archivo['mcq'] += (preguntas_este_archivo - total_calculado)
            
            print(f"\n  📝 Archivo {idx}/{len(archivos_contenido)}: {archivo_info['nombre']}")
            print(f"     Proporción: {proporcion*100:.1f}% ({archivo_info['chars']} chars)")
            print(f"     Generando ~{sum(num_preguntas_archivo.values())} preguntas (variedad de tipos)")
            
            # Generar preguntas para este archivo
            contenido_formateado = f"=== {archivo_info['nombre']} ===\n{archivo_info['contenido']}"
            preguntas_archivo = generador_actual.generar_examen(contenido_formateado, num_preguntas_archivo)
            
            print(f"     ✅ Obtenidas: {len(preguntas_archivo)} preguntas")
            todas_preguntas.extend(preguntas_archivo)
        
        # Mezclar todas las preguntas para variedad
        import random
        random.shuffle(todas_preguntas)
        
        print(f"\n📊 Resumen de generación:")
        print(f"   Total obtenido: {len(todas_preguntas)} preguntas")
        print(f"   Total solicitado: {total_preguntas}")
        
        # Contar por tipo lo que tenemos
        contador_tipos = {}
        for p in todas_preguntas:
            tipo = p.tipo
            contador_tipos[tipo] = contador_tipos.get(tipo, 0) + 1
        
        print(f"   Distribución obtenida: {contador_tipos}")
        
        # Seleccionar las necesarias respetando proporción solicitada
        preguntas_finales = []
        tipos_necesarios = {
            'mcq': num_multiple,
            'short_answer': num_corta,
            'true_false': num_vf,
            'open_question': num_desarrollo
        }
        
        # Separar por tipo con normalización
        preguntas_por_tipo = {
            'mcq': [],
            'short_answer': [],
            'true_false': [],
            'open_question': []
        }
        
        # Mapeo de tipos para normalizar
        mapeo_tipos = {
            'mcq': 'mcq',
            'multiple': 'mcq',
            'true_false': 'true_false',
            'verdadero_falso': 'true_false',
            'verdadero-falso': 'true_false',
            'short_answer': 'short_answer',
            'corta': 'short_answer',
            'respuesta_corta': 'short_answer',
            'open_question': 'open_question',
            'desarrollo': 'open_question'
        }
        
        for p in todas_preguntas:
            tipo_normalizado = mapeo_tipos.get(p.tipo, p.tipo)
            if tipo_normalizado in preguntas_por_tipo:
                preguntas_por_tipo[tipo_normalizado].append(p)
            else:
                print(f"   ⚠️  Tipo desconocido ignorado: '{p.tipo}' (no está en el mapeo)")
        
        print(f"\n📋 Preguntas por tipo (normalizadas):")
        for tipo, lista in preguntas_por_tipo.items():
            if lista:
                print(f"   {tipo}: {len(lista)} disponibles")
        
        # Tomar las necesarias de cada tipo
        for tipo, cantidad in tipos_necesarios.items():
            disponibles = preguntas_por_tipo.get(tipo, [])
            random.shuffle(disponibles)  # Aleatorizar dentro del tipo
            tomadas = disponibles[:cantidad]
            preguntas_finales.extend(tomadas)
            print(f"   {tipo}: tomadas {len(tomadas)}/{cantidad} (disponibles: {len(disponibles)})")
            if len(tomadas) < cantidad:
                print(f"      ⚠️  Faltan {cantidad - len(tomadas)} preguntas de tipo '{tipo}'")
        
        # Si aún faltan, completar con las que sobran
        if len(preguntas_finales) < total_preguntas:
            faltantes = total_preguntas - len(preguntas_finales)
            print(f"\n  🔄 Completando {faltantes} preguntas faltantes...")
            
            # Tomar de las que sobraron
            usadas = set(id(p) for p in preguntas_finales)
            sobrantes = [p for p in todas_preguntas if id(p) not in usadas]
            random.shuffle(sobrantes)
            preguntas_finales.extend(sobrantes[:faltantes])
        
        # Mezclar resultado final
        random.shuffle(preguntas_finales)
        
        # Limitar al total solicitado
        preguntas = preguntas_finales[:total_preguntas]
        
        print(f"\n✅ Total final: {len(preguntas)} preguntas generadas")
        
        # Mapear tipos de pregunta al formato esperado por la UI
        tipo_map = {
            'mcq': 'multiple',
            'short_answer': 'corta',
            'true_false': 'verdadero-falso',
            'open_question': 'desarrollo'
        }
        
        preguntas_dict = []
        for p in preguntas:
            pregunta_dict = p.to_dict()
            # Mapear el tipo al formato de la UI
            if pregunta_dict['tipo'] in tipo_map:
                pregunta_dict['tipo'] = tipo_map[pregunta_dict['tipo']]
            preguntas_dict.append(pregunta_dict)
        
        return {
            "preguntas": preguntas_dict,
            "total": len(preguntas_dict)
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generando examen: {str(e)}")


@app.get("/api/arbol_antiguo")
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
    
    # DEBUG: Imprimir datos recibidos
    print(f"\n{'='*60}")
    print(f"🔍 DEBUG - Datos recibidos en /api/generar-examen:")
    print(f"   Keys: {list(datos.keys())}")
    print(f"   num_multiple: {datos.get('num_multiple')} (tipo: {type(datos.get('num_multiple'))})")
    print(f"   num_corta: {datos.get('num_corta')} (tipo: {type(datos.get('num_corta'))})")
    print(f"   num_desarrollo: {datos.get('num_desarrollo')} (tipo: {type(datos.get('num_desarrollo'))})")
    print(f"   num_verdadero_falso: {datos.get('num_verdadero_falso')} (tipo: {type(datos.get('num_verdadero_falso'))})")
    print(f"{'='*60}\n")
    
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
        modelo_ollama = config.get("modelo_ollama_activo", "Meta-Llama-3.1-8B-Instruct-Q4-K-L")
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
        
        # Generar preguntas (claves normalizadas para coincidir con el generador)
        num_preguntas = {
            'mcq': num_multiple,
            'true_false': num_verdadero_falso,
            'short_answer': num_corta,
            'open_question': num_desarrollo
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
        
        # Mapear tipos de pregunta al formato esperado por la UI
        tipo_map = {
            'mcq': 'multiple',
            'short_answer': 'corta',
            'true_false': 'verdadero-falso',
            'open_question': 'desarrollo'
        }
        
        # Convertir a formato JSON y mapear tipos
        callback_progreso(95, "Finalizando...")
        preguntas_json = []
        for p in preguntas:
            p_dict = p.to_dict()
            # Mapear el tipo al formato de la UI
            if p_dict['tipo'] in tipo_map:
                p_dict['tipo'] = tipo_map[p_dict['tipo']]
            preguntas_json.append(p_dict)
        
        # 🔥 NORMALIZAR TODAS LAS PREGUNTAS PARA SPACED REPETITION
        print(f"🔄 Normalizando {len(preguntas_json)} preguntas para Spaced Repetition...")
        preguntas_json = [normalizar_pregunta_spaced_repetition(p) for p in preguntas_json]
        print(f"✅ Preguntas normalizadas con campos de repetición espaciada")
        
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


@app.post("/api/generar_practica")
async def generar_practica(datos: dict):
    """Genera flashcards/prácticas basadas en contenido de documentos"""
    global generador_actual, progreso_generacion
    
    print(f"\n{'='*60}")
    print(f"🎯 DEBUG - Datos recibidos en /api/generar_practica:")
    print(f"   Keys: {list(datos.keys())}")
    print(f"{'='*60}\n")
    
    # Extraer parámetros
    ruta = datos.get("ruta")
    prompt = datos.get("prompt", "")
    tipo_flashcard = datos.get("tipo_flashcard", "respuesta_corta")
    tipo_caso = datos.get("tipo_caso", "decision")
    session_id = datos.get("session_id", str(uuid.uuid4()))
    
    # 🔥 NUEVOS PARÁMETROS PARA MÚLTIPLES DOCUMENTOS
    documentos = datos.get("documentos", [])  # Array de rutas de documentos
    tipo_fuente = datos.get("tipo_fuente", "carpeta")  # 'carpeta' o 'documento'
    
    print(f"📚 Tipo de fuente: {tipo_fuente}")
    print(f"📄 Documentos recibidos: {documentos}")
    print(f"📄 Cantidad de documentos: {len(documentos)}")
    print(f"🔍 Tipo de documentos: {type(documentos)}")
    if documentos:
        print(f"   Primer documento: {documentos[0] if len(documentos) > 0 else 'N/A'}")
    
    # Contadores de tipos de preguntas
    num_flashcards = datos.get("num_flashcards", 0)
    num_mcq = datos.get("num_mcq", 0)
    num_verdadero_falso = datos.get("num_verdadero_falso", 0)
    num_cloze = datos.get("num_cloze", 0)
    num_respuesta_corta = datos.get("num_respuesta_corta", 0)
    num_open_question = datos.get("num_open_question", 0)
    num_caso_estudio = datos.get("num_caso_estudio", 0)
    
    # Reading types
    num_reading_comprehension = datos.get("num_reading_comprehension", 0)
    num_reading_true_false = datos.get("num_reading_true_false", 0)
    num_reading_cloze = datos.get("num_reading_cloze", 0)
    num_reading_skill = datos.get("num_reading_skill", 0)
    num_reading_matching = datos.get("num_reading_matching", 0)
    num_reading_sequence = datos.get("num_reading_sequence", 0)
    
    # Writing types
    num_writing_short = datos.get("num_writing_short", 0)
    num_writing_paraphrase = datos.get("num_writing_paraphrase", 0)
    num_writing_correction = datos.get("num_writing_correction", 0)
    num_writing_transformation = datos.get("num_writing_transformation", 0)
    num_writing_essay = datos.get("num_writing_essay", 0)
    num_writing_sentence_builder = datos.get("num_writing_sentence_builder", 0)
    num_writing_picture_description = datos.get("num_writing_picture_description", 0)
    num_writing_email = datos.get("num_writing_email", 0)
    
    # Cargar contenido desde la ruta o múltiples documentos
    contenido = ""
    
    # 🔥 PRIORIDAD: Si hay lista de documentos, cargar todos
    if documentos and len(documentos) > 0:
        print(f"📚 Cargando {len(documentos)} documentos...")
        contenidos_documentos = []
        
        for idx, ruta_doc in enumerate(documentos, 1):
            try:
                ruta_path = Path(ruta_doc)
                print(f"   📄 {idx}/{len(documentos)}: {ruta_path.name}")
                
                # Si la ruta no es absoluta, intentar desde extracciones/
                if not ruta_path.exists():
                    ruta_alternativa = EXTRACCIONES_PATH / ruta_doc
                    if ruta_alternativa.exists():
                        ruta_path = ruta_alternativa
                
                if ruta_path.exists():
                    texto_doc = obtener_texto(str(ruta_path))
                    if texto_doc:
                        # Agregar separador con nombre del documento
                        contenidos_documentos.append(f"\n\n{'='*60}\n")
                        contenidos_documentos.append(f"DOCUMENTO: {ruta_path.name}\n")
                        contenidos_documentos.append(f"{'='*60}\n\n")
                        contenidos_documentos.append(texto_doc)
                        print(f"      ✅ Cargado: {len(texto_doc)} caracteres")
                else:
                    print(f"      ⚠️ No encontrado: {ruta_doc}")
            except Exception as e:
                print(f"      ❌ Error cargando {ruta_doc}: {e}")
        
        if contenidos_documentos:
            contenido = "".join(contenidos_documentos)
            print(f"✅ Total contenido cargado: {len(contenido)} caracteres de {len(documentos)} documentos")
    
    # 🔥 FALLBACK: Si es tipo carpeta pero no hay documentos cargados, buscar archivos en la carpeta
    elif tipo_fuente == "carpeta" and ruta:
        print(f"⚠️ No se recibieron documentos pero es tipo carpeta. Buscando archivos en: {ruta}")
        try:
            carpeta_path = EXTRACCIONES_PATH / ruta
            print(f"   📂 Carpeta completa: {carpeta_path}")
            
            if carpeta_path.exists() and carpeta_path.is_dir():
                # Buscar todos los .txt recursivamente
                archivos_txt = list(carpeta_path.glob('**/*.txt'))
                print(f"   📄 Encontrados {len(archivos_txt)} archivos .txt")
                
                contenidos_documentos = []
                for idx, archivo in enumerate(archivos_txt, 1):
                    try:
                        texto_doc = obtener_texto(str(archivo))
                        if texto_doc:
                            contenidos_documentos.append(f"\n\n{'='*60}\n")
                            contenidos_documentos.append(f"DOCUMENTO: {archivo.name}\n")
                            contenidos_documentos.append(f"{'='*60}\n\n")
                            contenidos_documentos.append(texto_doc)
                            print(f"      ✅ {idx}/{len(archivos_txt)}: {archivo.name} ({len(texto_doc)} chars)")
                    except Exception as e:
                        print(f"      ❌ Error con {archivo.name}: {e}")
                
                if contenidos_documentos:
                    contenido = "".join(contenidos_documentos)
                    print(f"✅ FALLBACK exitoso: {len(contenido)} caracteres de {len(archivos_txt)} archivos")
                else:
                    print(f"⚠️ No se pudo cargar ningún archivo de la carpeta")
            else:
                print(f"❌ La carpeta no existe: {carpeta_path}")
        except Exception as e:
            print(f"❌ Error en fallback de carpeta: {e}")
            import traceback
            traceback.print_exc()
    
    # Fallback: Cargar desde ruta única (comportamiento original)
    elif ruta:
        try:
            ruta_path = Path(ruta)
            print(f"🔍 DEBUG - Ruta recibida: {ruta}")
            print(f"   Path object: {ruta_path}")
            print(f"   Existe? {ruta_path.exists()}")
            print(f"   Es absoluta? {ruta_path.is_absolute()}")
            
            # Si la ruta no existe, intentar desde extracciones/
            if not ruta_path.exists():
                ruta_alternativa = Path("extracciones") / ruta
                print(f"   Intentando ruta alternativa: {ruta_alternativa}")
                print(f"   Existe alternativa? {ruta_alternativa.exists()}")
                if ruta_alternativa.exists():
                    ruta_path = ruta_alternativa
            
            if ruta_path.exists():
                contenido = obtener_texto(str(ruta_path))
                print(f"✅ Contenido cargado: {len(contenido)} caracteres")
                print(f"   Primeros 150 chars: {contenido[:150]}...")
            else:
                print(f"❌ ERROR: La ruta no existe ni en absoluto ni en extracciones/")
        except Exception as e:
            print(f"⚠️ No se pudo cargar contenido de ruta: {e}")
            import traceback
            traceback.print_exc()
    
    # Si no hay contenido, usar el prompt directamente
    if not contenido and not prompt:
        raise HTTPException(status_code=400, detail="Se requiere contenido o prompt para generar la práctica")
    
    # Cargar configuración
    config = cargar_config()
    ajustes = config.get("ajustes_avanzados", {
        "n_ctx": 4096,
        "temperature": 0.7,
        "max_tokens": 512
    })
    
    print(f"\n{'='*60}")
    print(f"📝 Solicitud de generación de práctica (Session: {session_id})")
    print(f"📊 Tipos de preguntas solicitadas:")
    if num_flashcards > 0:
        print(f"   • Flashcards: {num_flashcards}")
    if num_mcq > 0:
        print(f"   • Opción múltiple: {num_mcq}")
    if num_verdadero_falso > 0:
        print(f"   • Verdadero/Falso: {num_verdadero_falso}")
    if num_cloze > 0:
        print(f"   • Cloze (completar): {num_cloze}")
    if num_respuesta_corta > 0:
        print(f"   • Respuesta corta: {num_respuesta_corta}")
    if num_open_question > 0:
        print(f"   • Pregunta abierta: {num_open_question}")
    if num_caso_estudio > 0:
        print(f"   • Caso de estudio: {num_caso_estudio}")
    
    # Reading types logging
    if num_reading_comprehension > 0:
        print(f"   • Reading comprehension: {num_reading_comprehension}")
    if num_reading_true_false > 0:
        print(f"   • Reading true/false: {num_reading_true_false}")
    if num_reading_cloze > 0:
        print(f"   • Reading cloze: {num_reading_cloze}")
    if num_reading_skill > 0:
        print(f"   • Reading skill: {num_reading_skill}")
    if num_reading_matching > 0:
        print(f"   • Reading matching: {num_reading_matching}")
    if num_reading_sequence > 0:
        print(f"   • Reading sequence: {num_reading_sequence}")
    
    # Writing types logging
    if num_writing_short > 0:
        print(f"   • Writing short: {num_writing_short}")
    if num_writing_paraphrase > 0:
        print(f"   • Writing paraphrase: {num_writing_paraphrase}")
    if num_writing_correction > 0:
        print(f"   • Writing correction: {num_writing_correction}")
    if num_writing_transformation > 0:
        print(f"   • Writing transformation: {num_writing_transformation}")
    if num_writing_essay > 0:
        print(f"   • Writing essay: {num_writing_essay}")
    if num_writing_sentence_builder > 0:
        print(f"   • Writing sentence builder: {num_writing_sentence_builder}")
    if num_writing_picture_description > 0:
        print(f"   • Writing picture description: {num_writing_picture_description}")
    if num_writing_email > 0:
        print(f"   • Writing email: {num_writing_email}")
    
    print(f"\n🎮 Motor de IA:")
    if generador_actual and hasattr(generador_actual, 'usar_ollama') and generador_actual.usar_ollama:
        print(f"   ✅ USANDO GPU - Ollama")
        print(f"   🎯 Modelo: {generador_actual.modelo_ollama}")
    else:
        print(f"   ⚠️  Usando llama-cpp-python")
    print(f"{'='*60}\n")
    
    # Inicializar progreso
    progreso_generacion[session_id] = {
        'progreso': 0,
        'mensaje': 'Iniciando generación de práctica...',
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
        modelo_ollama = config.get("modelo_ollama_activo", "Meta-Llama-3.1-8B-Instruct-Q4-K-L")
        usar_ollama = config.get("usar_ollama", True)
        modelo_path = config.get("modelo_path")
        gpu_layers = ajustes.get('n_gpu_layers', 35)
        
        # Crear generador con la configuración actual
        if usar_ollama:
            generador_actual = GeneradorUnificado(
                usar_ollama=True,
                modelo_ollama=modelo_ollama,
                n_gpu_layers=gpu_layers
            )
        else:
            generador_actual = GeneradorUnificado(
                usar_ollama=False,
                modelo_path_gguf=modelo_path,
                n_gpu_layers=gpu_layers
            )
        
        # Mapear tipos de pregunta (usar los mismos tipos que generar-examen)
        num_preguntas = {}
        
        # Mapeo de tipos de práctica a tipos de examen
        if num_flashcards > 0 or num_respuesta_corta > 0:
            num_preguntas['short_answer'] = num_flashcards + num_respuesta_corta
        if num_mcq > 0:
            num_preguntas['mcq'] = num_mcq
        if num_verdadero_falso > 0:
            num_preguntas['true_false'] = num_verdadero_falso
        if num_cloze > 0:
            num_preguntas['cloze'] = num_cloze
        if num_open_question > 0:
            num_preguntas['open_question'] = num_open_question
        if num_caso_estudio > 0:
            num_preguntas['case_study'] = num_caso_estudio
        
        # Por ahora, los demás tipos se tratan como short_answer
        tipos_adicionales = (num_reading_comprehension + num_reading_true_false + num_reading_cloze +
                           num_reading_skill + num_reading_matching + num_reading_sequence +
                           num_writing_short + num_writing_paraphrase + num_writing_correction +
                           num_writing_transformation + num_writing_essay + num_writing_sentence_builder +
                           num_writing_picture_description + num_writing_email)
        
        if tipos_adicionales > 0:
            num_preguntas['short_answer'] = num_preguntas.get('short_answer', 0) + tipos_adicionales
        
        # Si no se especificó ningún tipo, generar 5 flashcards por defecto
        if not num_preguntas:
            num_preguntas['short_answer'] = 5
        
        callback_progreso(10, "Preparando generación de flashcards...")
        print("🤖 Generando flashcards con IA...")
        
        # Usar el contenido del documento (cargado desde la ruta)
        # El generador_actual.generar_examen() se encarga de crear el prompt internamente
        contexto = contenido if contenido else prompt
        
        preguntas = generador_actual.generar_examen(
            contexto, 
            num_preguntas,
            ajustes_modelo=ajustes,
            callback_progreso=callback_progreso,
            session_id=session_id,
            tipo_caso=tipo_caso  # Pasar el tipo de caso de estudio seleccionado
        )
        print(f"✅ Generadas {len(preguntas)} preguntas exitosamente")
        
        # Convertir a formato JSON
        callback_progreso(95, "Finalizando...")
        preguntas_json = [p.to_dict() for p in preguntas]
        
        # Post-procesar preguntas tipo cloze para aplanar metadata
        for pregunta_json in preguntas_json:
            try:
                # CLOZE: Aplanar metadata anidada
                if pregunta_json.get('tipo') == 'cloze' and 'metadata' in pregunta_json:
                    # Si metadata tiene metadata anidada, aplanar
                    if isinstance(pregunta_json['metadata'], dict) and 'metadata' in pregunta_json['metadata']:
                        metadata_interna = pregunta_json['metadata']['metadata']
                        if isinstance(metadata_interna, dict):
                            # Mover los campos importantes al nivel superior de metadata
                            if 'text_with_gaps' in metadata_interna:
                                pregunta_json['metadata']['text_with_gaps'] = metadata_interna['text_with_gaps']
                            if 'answers' in metadata_interna:
                                pregunta_json['metadata']['answers'] = metadata_interna['answers']
                            if 'hint' in metadata_interna:
                                pregunta_json['metadata']['hint'] = metadata_interna['hint']
                            # Eliminar la metadata duplicada
                            del pregunta_json['metadata']['metadata']
                
                # OPEN_QUESTION: Aplanar metadata anidada
                elif pregunta_json.get('tipo') == 'open_question' and 'metadata' in pregunta_json:
                    if isinstance(pregunta_json['metadata'], dict) and 'metadata' in pregunta_json['metadata']:
                        metadata_interna = pregunta_json['metadata']['metadata']
                        if isinstance(metadata_interna, dict):
                            # Mover campos importantes
                            if 'key_points' in metadata_interna:
                                pregunta_json['metadata']['key_points'] = metadata_interna['key_points']
                            if 'expected_length' in metadata_interna:
                                pregunta_json['metadata']['expected_length'] = metadata_interna['expected_length']
                            if 'evaluation_criteria' in metadata_interna:
                                pregunta_json['metadata']['evaluation_criteria'] = metadata_interna['evaluation_criteria']
                            # Eliminar metadata duplicada
                            del pregunta_json['metadata']['metadata']
            except Exception as e:
                print(f"⚠️ Error al aplanar metadata de pregunta {pregunta_json.get('tipo')}: {e}")
                continue
        
        # 🔥 NORMALIZAR TODAS LAS PREGUNTAS PARA SPACED REPETITION
        print(f"🔄 Normalizando {len(preguntas_json)} preguntas para Spaced Repetition...")
        preguntas_json = [normalizar_pregunta_spaced_repetition(p) for p in preguntas_json]
        print(f"✅ Preguntas normalizadas con campos de repetición espaciada")
        
        # Marcar como completado
        progreso_generacion[session_id] = {
            'progreso': 100,
            'mensaje': 'Práctica generada exitosamente',
            'completado': True,
            'error': None
        }
        
        resultado = {
            "success": True,
            "session_id": session_id,
            "preguntas": preguntas_json,
            "total_preguntas": len(preguntas),
        }
        
        print(f"✅ Práctica generada: {resultado['total_preguntas']} preguntas\n")
        return resultado
        
    except Exception as e:
        import traceback
        print(f"\n❌ ERROR generando práctica:")
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
        
        raise HTTPException(status_code=500, detail=f"Error al generar práctica: {str(e)}")


@app.post("/api/evaluar-examen")
async def evaluar_examen(datos: dict):
    """Evalúa las respuestas de un examen"""
    global generador_unificado
    
    try:
        # Usar GeneradorUnificado (con GPU/CPU según configuración)
        if generador_unificado is None:
            config = cargar_config()
            usar_ollama = config.get("usar_ollama", True)
            modelo_ollama = config.get("modelo_ollama_activo", "Meta-Llama-3.1-8B-Instruct-Q4-K-L")
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
            es_practica = datos.get("es_practica", False)  # Nuevo parámetro

            # 🔥 LIMPIAR CARPETA_PATH: Eliminar prefijos no deseados
            if carpeta_path:
                print(f"\n🔍 DEBUG - carpeta_path original: '{carpeta_path}'")
                # Normalizar separadores a /
                carpeta_path_limpia = carpeta_path.replace("\\", "/")
                
                # Eliminar prefijos problemáticos
                prefijos_eliminar = ["extracciones/", "Practicas/", "practicas/"]
                for prefijo in prefijos_eliminar:
                    if carpeta_path_limpia.startswith(prefijo):
                        carpeta_path_limpia = carpeta_path_limpia[len(prefijo):]
                        print(f"   🧹 Eliminado prefijo '{prefijo}'")
                
                # Convertir de vuelta a backslashes para Windows
                carpeta_path = carpeta_path_limpia.replace("/", "\\")
                print(f"   ✅ carpeta_path limpia: '{carpeta_path}'\n")

            if not preguntas_data:
                raise HTTPException(status_code=400, detail="El campo 'preguntas' es obligatorio y no puede estar vacío.")

            if not isinstance(respuestas, dict):
                raise HTTPException(status_code=400, detail="El campo 'respuestas' debe ser un diccionario.")

            # Validar que cada respuesta sea una cadena válida o array (para cloze)
            for key, value in respuestas.items():
                if value is None:
                    respuestas[key] = ""
                elif isinstance(value, list):
                    # Para tipo cloze, puede ser array de respuestas
                    # Convertir a string separado por comas para procesamiento
                    respuestas[key] = ", ".join(str(v) for v in value)
                elif isinstance(value, str) and '|||' in value:
                    # Frontend envía respuestas cloze separadas por |||, convertir a comas
                    respuestas[key] = value.replace('|||', ', ')
                elif not isinstance(value, str):
                    respuestas[key] = str(value)

            # Continuar con la lógica existente
            resultados = []
            puntos_obtenidos = 0
            puntos_totales = 0

            for i, pregunta_dict in enumerate(preguntas_data):
                pregunta = PreguntaExamen.from_dict(pregunta_dict)
                respuesta_usuario = respuestas.get(str(i), "")
                if respuesta_usuario is None:
                    respuesta_usuario = ""
                elif isinstance(respuesta_usuario, list):
                    # Para tipo cloze, convertir array a string
                    respuesta_usuario = ", ".join(str(v) for v in respuesta_usuario)
                elif isinstance(respuesta_usuario, str) and '|||' in respuesta_usuario:
                    # Frontend envía respuestas cloze separadas por |||, convertir a comas
                    respuesta_usuario = respuesta_usuario.replace('|||', ', ')
                elif not isinstance(respuesta_usuario, str):
                    respuesta_usuario = str(respuesta_usuario)

                # Evaluar respuesta
                resultado_eval = generador_unificado.evaluar_respuesta(pregunta, respuesta_usuario)
                puntos = resultado_eval["puntos_obtenidos"]
                feedback = resultado_eval["feedback"]

                puntos_obtenidos += puntos
                puntos_totales += pregunta.puntos
                
                # Calcular porcentaje individual de esta pregunta
                porcentaje_pregunta = (puntos / pregunta.puntos * 100) if pregunta.puntos > 0 else 0
                
                # Calcular repetición espaciada individual según rendimiento
                ahora = datetime.now()
                if porcentaje_pregunta >= 90:
                    # Excelente: revisar en 7 días
                    intervalo_dias = 7
                    facilidad = 2.8
                elif porcentaje_pregunta >= 70:
                    # Bien: revisar en 3 días
                    intervalo_dias = 3
                    facilidad = 2.5
                elif porcentaje_pregunta >= 50:
                    # Regular: revisar mañana
                    intervalo_dias = 1
                    facilidad = 2.2
                else:
                    # Mal: revisar hoy (en 12 horas)
                    intervalo_dias = 0.5
                    facilidad = 2.0
                
                proxima_revision_pregunta = (ahora + timedelta(days=intervalo_dias)).isoformat()

                resultados.append({
                    "pregunta": pregunta.pregunta,
                    "tipo": pregunta.tipo,
                    "opciones": pregunta.opciones if pregunta.tipo == 'multiple' else [],
                    "respuesta_usuario": respuesta_usuario,
                    "respuesta_correcta": pregunta.respuesta_correcta,
                    "puntos": puntos,
                    "puntos_maximos": pregunta.puntos,
                    "feedback": feedback,
                    # Repetición espaciada individual
                    "porcentaje": porcentaje_pregunta,
                    "proximaRevision": proxima_revision_pregunta,
                    "ultimaRevision": ahora.isoformat(),
                    "intervalo": intervalo_dias,
                    "repeticiones": 0,
                    "facilidad": facilidad,
                    "estadoRevision": "nueva"
                })
            
            porcentaje = (puntos_obtenidos / puntos_totales * 100) if puntos_totales > 0 else 0
            
            # 🔥 NO GUARDAR ARCHIVO NUEVO SI ES UNA PRÁCTICA EXISTENTE
            # Buscar archivo existente (original o pausado) para reutilizarlo
            guardar_archivo_nuevo = True
            archivo_existente = None
            if es_practica and carpeta_path:
                carpeta_limpia = carpeta_path.replace('/', '\\')
                carpeta_destino = EXTRACCIONES_PATH / carpeta_limpia
                # Buscar archivos de práctica (pausados o normales)
                archivos_practica = list(carpeta_destino.glob("practica_*.json"))
                if archivos_practica:
                    # Usar el más reciente
                    archivo_existente = max(archivos_practica, key=lambda p: p.stat().st_mtime)
                    guardar_archivo_nuevo = False
                    print(f"♻️ Práctica existente encontrada - Reutilizando: {archivo_existente.name}")
            
            # Guardar resultados SIEMPRE (con o sin carpeta)
            if guardar_archivo_nuevo:
                try:
                    # 🔥 GUARDAR EN extracciones/{carpeta}/examen.json
                    if not carpeta_path:
                        # Sin carpeta: usar carpeta por defecto en extracciones
                        carpeta_path = "Examenes_Generales"
                        carpeta_nombre = "Exámenes Generales"
                        carpeta_destino = EXTRACCIONES_PATH / carpeta_path
                        print(f"💾 Guardando en carpeta por defecto: {carpeta_destino}")
                    else:
                        # 🔥 GUARDAR EN LA MISMA CARPETA DE EXTRACCIONES (NUNCA en Practicas/)
                        print(f"💾 Guardando resultados para carpeta: {carpeta_path}")
                        print(f"🔥 es_practica = {es_practica}")
                        
                        # Extraer el nombre de la carpeta
                        carpeta_nombre = carpeta_path.split('/')[-1] if '/' in carpeta_path else carpeta_path.split('\\')[-1]
                        
                        # 🔥 GUARDAR DIRECTAMENTE EN extracciones/{carpeta}/ (NO en Practicas/)
                        carpeta_destino = EXTRACCIONES_PATH / carpeta_path
                        print(f"🔥 CARPETA DESTINO FINAL = {carpeta_destino}")
                    
                    # Crear estructura de carpetas
                    carpeta_destino.mkdir(parents=True, exist_ok=True)

                    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # 🔥 NOMBRE DE ARCHIVO: Reutilizar existente o crear nuevo
                    if archivo_existente:
                        # Reutilizar archivo existente de práctica
                        archivo_resultado = archivo_existente
                        # Extraer ID del nombre del archivo existente
                        fecha = archivo_existente.stem.replace("practica_", "").replace("practica_progreso_", "")
                    elif es_practica:
                        archivo_resultado = carpeta_destino / f"practica_{fecha}.json"
                    else:
                        archivo_resultado = carpeta_destino / f"examen_{fecha}.json"

                    # Calcular próxima revisión (SM-2 algorithm inicial)
                    ahora = datetime.now()
                    proxima_revision = (ahora + timedelta(days=1)).isoformat()  # Primer repaso mañana
                    
                    resultado_completo = {
                        "id": fecha,
                        "archivo": archivo_resultado.name,  # 🔥 Usar nombre real del archivo
                        "fecha_completado": datetime.now().isoformat(),
                        "carpeta_ruta": carpeta_path.replace("\\", "/"),  # 🔥 Normalizar rutas
                        "carpeta_nombre": carpeta_nombre,
                        "puntos_obtenidos": puntos_obtenidos,
                        "puntos_totales": puntos_totales,
                        "porcentaje": porcentaje,
                        "preguntas": preguntas_data,  # 🔥 Guardar preguntas originales para el frontend
                        "resultados": resultados,
                        "tipo": "completado",
                        "es_practica": es_practica,
                        # Campos para repetición espaciada (SM-2)
                        "proximaRevision": proxima_revision,
                        "ultimaRevision": ahora.isoformat(),
                        "intervalo": 1,  # 🔥 Entero, no decimal
                        "repeticiones": 0,
                        "facilidad": 2.5,
                        "estadoRevision": "nueva",
                        "titulo": carpeta_nombre
                    }
                    
                    # 🔥 NORMALIZAR ANTES DE GUARDAR
                    resultado_completo = normalizar_examen_completo(resultado_completo)

                    with open(archivo_resultado, 'w', encoding='utf-8') as f:
                        json.dump(resultado_completo, f, ensure_ascii=False, indent=2)

                    print(f"✅ Resultados guardados en: {archivo_resultado}")

                    # Limpiar exámenes/prácticas en progreso de esta carpeta
                    # La carpeta de progreso está en el mismo nivel que resultados
                    carpeta_progreso_base = carpeta_destino.parent / "examenes_progreso"
                    if carpeta_progreso_base.exists():
                        for archivo in carpeta_progreso_base.glob("examen_progreso_*.json"):
                            archivo.unlink()
                            print(f"🗑️ Examen en progreso eliminado: {archivo.name}")
                except Exception as e:
                    print(f"❌ Error guardando resultados: {e}")
                    import traceback
                    traceback.print_exc()

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


@app.post("/api/evaluar-respuesta-textual")
async def evaluar_respuesta_textual(datos: dict):
    """Evalúa una respuesta de texto usando el modelo seleccionado por el usuario"""
    try:
        # Extraer parámetros
        pregunta = datos.get("pregunta", "")
        respuesta_usuario = datos.get("respuesta_usuario", "")
        respuesta_correcta = datos.get("respuesta_correcta", "")
        intentos_previos = datos.get("intentos_previos", [])
        modelo = datos.get("modelo")  # Modelo seleccionado por el usuario
        
        if not modelo:
            raise HTTPException(status_code=400, detail="Debe especificar un modelo")
        
        if not pregunta or not respuesta_usuario:
            raise HTTPException(status_code=400, detail="Faltan datos requeridos: pregunta y respuesta_usuario")
        
        print(f"🤖 Evaluando respuesta con modelo: {modelo}")
        print(f"   📝 Pregunta: {pregunta[:100]}...")
        print(f"   💭 Respuesta usuario: {respuesta_usuario[:100]}...")
        
        # Construir prompt de evaluación
        historial_intentos = "\n".join([
            f"Intento {i+1} (puntuación {int.get('puntuacion', 0)}/10): {int.get('respuesta', '')}\nFeedback: {int.get('feedback', '')}"
            for i, int in enumerate(intentos_previos)
        ]) if intentos_previos else "Primer intento"
        
        prompt = f"""Eres un evaluador de respuestas académicas. Evalúa la siguiente respuesta de manera objetiva y constructiva.

PREGUNTA:
{pregunta}

RESPUESTA ESPERADA:
{respuesta_correcta}

RESPUESTA DEL ESTUDIANTE:
{respuesta_usuario}

HISTORIAL DE INTENTOS PREVIOS:
{historial_intentos}

Evalúa la respuesta con los siguientes criterios:
1. Precisión conceptual (¿es correcta?)
2. Completitud (¿incluye todos los puntos clave?)
3. Claridad (¿está bien explicada?)
4. Mejora respecto a intentos anteriores (si aplica)

IMPORTANTE: Responde ÚNICAMENTE con un JSON válido en este formato exacto:
{{
  "puntuacion": <número del 0 al 10>,
  "feedback": "<explicación constructiva de 2-3 líneas>",
  "aprobada": <true o false>,
  "sugerencias": "<sugerencias específicas para mejorar (si aplica)>"
}}

NO incluyas texto adicional fuera del JSON. NO uses markdown. Solo el JSON puro."""

        # Llamar a Ollama con el modelo especificado
        try:
            import httpx
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    'http://localhost:11434/api/generate',
                    json={
                        'model': modelo,
                        'prompt': prompt,
                        'stream': False,
                        'options': {
                            'temperature': 0.3,
                            'top_p': 0.9,
                            'num_predict': 500
                        }
                    }
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error de Ollama: {response.status_code} - {response.text}"
                    )
                
                resultado = response.json()
                respuesta_ia = resultado.get('response', '').strip()
                
                print(f"   🤖 Respuesta IA: {respuesta_ia[:200]}...")
                
                # Extraer JSON de la respuesta
                import re
                json_match = re.search(r'\{[\s\S]*\}', respuesta_ia)
                if json_match:
                    evaluacion = json.loads(json_match.group())
                else:
                    # Si no hay JSON, crear evaluación por defecto
                    evaluacion = {
                        "puntuacion": 5,
                        "feedback": respuesta_ia[:200] if respuesta_ia else "No se pudo evaluar la respuesta",
                        "aprobada": False,
                        "sugerencias": "Por favor, revisa tu respuesta y vuelve a intentarlo"
                    }
                
                print(f"   ✅ Evaluación: {evaluacion.get('puntuacion')}/10 - Aprobada: {evaluacion.get('aprobada')}")
                
                return {
                    "success": True,
                    "evaluacion": evaluacion
                }
                
        except httpx.RequestError as e:
            print(f"❌ Error conectando con Ollama: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"No se pudo conectar con Ollama. Asegúrate de que esté ejecutándose: {str(e)}"
            )
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando JSON de la respuesta IA: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"La respuesta del modelo no tiene el formato esperado: {str(e)}"
            )
            
    except Exception as e:
        print(f"❌ Error en evaluar_respuesta_textual: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al evaluar respuesta: {str(e)}")


@app.post("/api/examenes/pausar")
async def pausar_examen(datos: dict):
    """Guarda el progreso de un examen o práctica para continuarlo después"""
    try:
        carpeta_ruta = datos.get("carpeta_ruta") or "Examenes_Generales"
        carpeta_nombre = datos.get("carpeta_nombre") or "Exámenes Generales"
        preguntas = datos.get("preguntas", [])
        respuestas = datos.get("respuestas", {})
        fecha_inicio = datos.get("fecha_inicio")
        es_practica = datos.get("es_practica", False)  # Nuevo parámetro
        archivo_original = datos.get("archivo_original")  # 🔥 NOMBRE DEL ARCHIVO ORIGINAL
        
        # 🔥 LIMPIAR CARPETA_RUTA: Eliminar prefijos no deseados
        if carpeta_ruta and carpeta_ruta not in ["Examenes_Generales", "Practicas_Generales"]:
            print(f"\n🔍 DEBUG pausar - carpeta_ruta original: '{carpeta_ruta}'")
            carpeta_ruta_limpia = carpeta_ruta.replace("\\", "/")
            prefijos_eliminar = ["extracciones/", "Practicas/", "practicas/"]
            for prefijo in prefijos_eliminar:
                if carpeta_ruta_limpia.startswith(prefijo):
                    carpeta_ruta_limpia = carpeta_ruta_limpia[len(prefijo):]
                    print(f"   🧹 Eliminado prefijo '{prefijo}'")
            carpeta_ruta = carpeta_ruta_limpia.replace("/", "\\")
            print(f"   ✅ carpeta_ruta limpia: '{carpeta_ruta}'\n")
        
        print(f"⏸️ Pausando {'práctica' if es_practica else 'examen'} para carpeta: {carpeta_ruta}")
        
        # Determinar carpeta de destino
        if carpeta_ruta in ["Examenes_Generales", "Practicas_Generales"]:
            # Carpetas por defecto: usar estructura antigua con subcarpetas
            tipo_carpeta = "practicas" if es_practica else "examenes"
            carpeta_examenes_base = Path(tipo_carpeta) / carpeta_ruta
            # Para carpetas generales, usar subcarpeta
            nombre_subcarpeta = "practicas_progreso" if es_practica else "examenes_progreso"
            carpeta_destino = carpeta_examenes_base / nombre_subcarpeta
        else:
            # 🔥 Carpetas de extracciones: guardar DIRECTAMENTE en la carpeta del documento
            carpeta_destino = Path("extracciones") / carpeta_ruta
        
        carpeta_destino.mkdir(parents=True, exist_ok=True)
        
        print(f"   📁 Guardando en: {carpeta_destino}")
        
        # 🔥 ELIMINAR ARCHIVO ORIGINAL SI EXISTE
        if archivo_original:
            archivo_original_path = carpeta_destino / archivo_original
            if archivo_original_path.exists():
                archivo_original_path.unlink()
                print(f"🗑️ Archivo original eliminado temporalmente: {archivo_original}")
        
        # Crear nuevo archivo de progreso con timestamp nuevo
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefijo_archivo = "practica_progreso" if es_practica else "examen_progreso"
        archivo_progreso = carpeta_destino / f"{prefijo_archivo}_{fecha}.json"
        timestamp = fecha
        
        datos_progreso = {
            "id": timestamp,
            "archivo": archivo_progreso.name,
            "archivo_original": archivo_original,  # 🔥 GUARDAR NOMBRE ORIGINAL
            "carpeta_ruta": carpeta_ruta,
            "carpeta_nombre": carpeta_nombre,
            "carpeta": carpeta_ruta,  # 🔥 Campo que espera el frontend
            "ruta": carpeta_ruta,  # 🔥 Campo que espera el frontend
            "preguntas": preguntas,
            "respuestas": respuestas,
            "fecha_inicio": fecha_inicio,
            "fecha": fecha_inicio or datetime.now().isoformat(),  # 🔥 Campo que espera el frontend
            "fecha_pausa": datetime.now().isoformat(),
            "tipo": "en_progreso",
            "completada": False,  # 🔥 Para que aparezca en "sin completar"
            "es_practica": es_practica  # 🔥 CAMPO CRÍTICO para distinguir tipo
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
    """Elimina un examen específico (completado o en progreso) - busca en TODAS las ubicaciones posibles"""
    try:
        print(f"\n🗑️ DELETE /api/examenes/examen")
        print(f"   Ruta recibida: '{ruta}'")
        print(f"   Archivo recibido: '{archivo}'")
        
        archivos_eliminados = 0
        ubicaciones_busqueda = []
        
        # 🔥 BUSCAR EN TODAS LAS UBICACIONES POSIBLES (eliminar duplicados)
        base_examenes = EXTRACCIONES_PATH
        
        # 1. extracciones/{ruta}/archivo
        ubicaciones_busqueda.append(base_examenes / ruta / archivo)
        
        # 2. extracciones/{ruta}/examenes_progreso/archivo
        ubicaciones_busqueda.append(base_examenes / ruta / "examenes_progreso" / archivo)
        
        # 3. extracciones/{ruta}/resultados_examenes/archivo (legacy)
        ubicaciones_busqueda.append(base_examenes / ruta / "resultados_examenes" / archivo)
        
        # 4. examenes/{ruta}/archivo (vieja estructura)
        old_base = Path("examenes")
        ubicaciones_busqueda.append(old_base / ruta / archivo)
        ubicaciones_busqueda.append(old_base / ruta / "examenes_progreso" / archivo)
        
        # 5. extracciones/Practicas/{ruta}/archivo (por si hay copias mal ubicadas)
        ubicaciones_busqueda.append(base_examenes / "Practicas" / ruta / archivo)
        
        print(f"   Buscando en {len(ubicaciones_busqueda)} ubicaciones posibles...")
        
        # Eliminar de TODAS las ubicaciones donde exista
        for ubicacion in ubicaciones_busqueda:
            if ubicacion.exists():
                print(f"   🗑️ Eliminando: {ubicacion}")
                ubicacion.unlink()
                archivos_eliminados += 1
        
        if archivos_eliminados == 0:
            print(f"   ❌ Archivo no encontrado en ninguna ubicación")
            raise HTTPException(status_code=404, detail="Examen no encontrado")
        
        print(f"   ✅ {archivos_eliminados} archivo(s) eliminado(s)")
        
        return {"success": True, "mensaje": f"Examen eliminado ({archivos_eliminados} copias)", "archivos_eliminados": archivos_eliminados}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error eliminando examen: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/examenes/carpetas")
async def listar_carpetas_examenes(ruta: str = ""):
    """Lista carpetas y exámenes en una ruta de extracciones/ (donde se guardan los ExamenGeneral.json)"""
    try:
        print(f"\n{'='*60}")
        print(f"🔍 GET /api/examenes/carpetas - ruta: '{ruta}'")
        print(f"{'='*60}")
        
        base_examenes = EXTRACCIONES_PATH  # 🔥 Cambio: buscar en extracciones/
        
        # Construir ruta completa
        if ruta:
            ruta_completa = base_examenes / ruta
        else:
            ruta_completa = base_examenes
        
        print(f"📁 Ruta completa: {ruta_completa}")
        print(f"   Existe: {ruta_completa.exists()}")
        
        if not ruta_completa.exists():
            raise HTTPException(status_code=404, detail="Ruta no encontrada")
        
        carpetas = []
        examenes_completados = []
        examenes_progreso = []
        examenes_progreso_global = []
        
        # Si estamos en la raíz, buscar TODOS los exámenes en progreso recursivamente
        if not ruta:
            print("📊 Buscando todos los exámenes en progreso en extracciones/...")
            # Buscar ExamenGeneral.json sin completar
            for archivo in base_examenes.rglob("ExamenGeneral.json"):
                try:
                    with open(archivo, 'r', encoding='utf-8') as f:
                        examen = json.load(f)
                        # Tratar null como False (no completado)
                        if examen.get("completado") is not True:
                            # 🔥 AGREGAR información de ruta y archivo para poder eliminar
                            carpeta_relativa = archivo.parent.relative_to(base_examenes)
                            examen["carpeta_ruta"] = str(carpeta_relativa).replace("\\", "/")
                            examen["archivo"] = "ExamenGeneral.json"
                            examenes_progreso_global.append(examen)
                except Exception as e:
                    print(f"Error leyendo {archivo}: {e}")
            print(f"   ✅ Encontrados {len(examenes_progreso_global)} exámenes en progreso")
        
        # Listar carpetas
        for item in sorted(ruta_completa.iterdir()):
            if item.is_dir():
                # Contar exámenes en la carpeta
                num_completados = 0
                num_progreso = 0
                
                # 🔥 Verificar ExamenGeneral.json (nuevo formato)
                examen_general = item / "ExamenGeneral.json"
                if examen_general.exists():
                    try:
                        with open(examen_general, 'r', encoding='utf-8') as f:
                            examen = json.load(f)
                            if examen.get("completado", False):
                                num_completados += 1
                            else:
                                num_progreso += 1
                    except Exception as e:
                        print(f"Error leyendo {examen_general}: {e}")
                
                # 🔥 También contar archivos legacy (examen_*.json) para no ignorarlos
                for archivo_legacy in item.glob("examen_*.json"):
                    try:
                        with open(archivo_legacy, 'r', encoding='utf-8') as f:
                            examen = json.load(f)
                            # Verificar que NO sea práctica
                            if not examen.get("es_practica", False):
                                # 🔥 Verificar completado: usar campo "completado" O campo "tipo"
                                esta_completado = (
                                    examen.get("completado") is True or 
                                    examen.get("tipo") == "completado"
                                )
                                if esta_completado:
                                    num_completados += 1
                                else:
                                    num_progreso += 1
                    except Exception as e:
                        print(f"Error leyendo {archivo_legacy}: {e}")
                
                carpetas.append({
                    "nombre": item.name,
                    "ruta": str(item.relative_to(base_examenes)) if ruta else item.name,
                    "num_completados": num_completados,
                    "num_progreso": num_progreso,
                    "total_examenes": num_completados + num_progreso
                })
        
        # Listar exámenes completados en esta carpeta
        # 🔥 Buscar ExamenGeneral.json
        examen_general = ruta_completa / "ExamenGeneral.json"
        if examen_general.exists():
            try:
                with open(examen_general, 'r', encoding='utf-8') as f:
                    examen = json.load(f)
                    # Tratar null como False
                    if examen.get("completado") is True:
                        # 🔥 AGREGAR metadatos de ruta y archivo
                        carpeta_relativa = ruta_completa.relative_to(base_examenes) if ruta else Path(".")
                        examen["carpeta_ruta"] = str(carpeta_relativa).replace("\\", "/")
                        examen["archivo"] = "ExamenGeneral.json"
                        examenes_completados.append(examen)
            except Exception as e:
                print(f"Error leyendo {examen_general}: {e}")
        
        # 🔥 También buscar archivos legacy (examen_*.json)
        for archivo_legacy in sorted(ruta_completa.glob("examen_*.json"), reverse=True):
            try:
                with open(archivo_legacy, 'r', encoding='utf-8') as f:
                    examen = json.load(f)
                    # Verificar que NO sea práctica y esté completado
                    # 🔥 Usar campo "completado" O campo "tipo"
                    esta_completado = (
                        examen.get("completado") is True or 
                        examen.get("tipo") == "completado"
                    )
                    if not examen.get("es_practica", False) and esta_completado:
                        # 🔥 AGREGAR metadatos de ruta y archivo (solo si no existen)
                        if ruta:
                            carpeta_relativa = ruta_completa.relative_to(base_examenes)
                            if not examen.get("carpeta_ruta"):
                                examen["carpeta_ruta"] = str(carpeta_relativa).replace("\\", "/")
                        if not examen.get("archivo"):
                            examen["archivo"] = archivo_legacy.name
                        examenes_completados.append(examen)
            except Exception as e:
                print(f"Error leyendo {archivo_legacy}: {e}")
        
        # Listar exámenes en progreso en esta carpeta específica (solo si no es raíz)
        if ruta:
            # 🔥 Buscar ExamenGeneral.json sin completar
            examen_general = ruta_completa / "ExamenGeneral.json"
            if examen_general.exists():
                try:
                    with open(examen_general, 'r', encoding='utf-8') as f:
                        examen = json.load(f)
                        # Tratar null como False (no completado)
                        if examen.get("completado") is not True:
                            # 🔥 AGREGAR metadatos de ruta y archivo
                            carpeta_relativa = ruta_completa.relative_to(base_examenes)
                            examen["carpeta_ruta"] = str(carpeta_relativa).replace("\\", "/")
                            examen["archivo"] = "ExamenGeneral.json"
                            examenes_progreso.append(examen)
                except Exception as e:
                    print(f"Error leyendo {examen_general}: {e}")
            
            # 🔥 También buscar archivos legacy sin completar
            for archivo_legacy in sorted(ruta_completa.glob("examen_*.json"), reverse=True):
                try:
                    with open(archivo_legacy, 'r', encoding='utf-8') as f:
                        examen = json.load(f)
                        # Verificar que NO sea práctica y NO esté completado
                        # 🔥 Usar campo "completado" O campo "tipo"
                        esta_completado = (
                            examen.get("completado") is True or 
                            examen.get("tipo") == "completado"
                        )
                        if not examen.get("es_practica", False) and not esta_completado:
                            # 🔥 AGREGAR metadatos de ruta y archivo
                            carpeta_relativa = ruta_completa.relative_to(base_examenes)
                            examen["carpeta_ruta"] = str(carpeta_relativa).replace("\\", "/")
                            examen["archivo"] = archivo_legacy.name
                            examenes_progreso.append(examen)
                except Exception as e:
                    print(f"Error leyendo {archivo_legacy}: {e}")
        
        print(f"\n📊 RESULTADOS:")
        print(f"   Carpetas: {len(carpetas)}")
        print(f"   Exámenes completados: {len(examenes_completados)}")
        print(f"   Exámenes en progreso: {len(examenes_progreso)}")
        print(f"   Exámenes progreso global: {len(examenes_progreso_global)}")
        print(f"{'='*60}\n")
        
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


@app.post("/api/examenes/actualizar")
async def actualizar_examen(datos: dict):
    """Actualiza un examen existente (por ejemplo, marcar preguntas como corregidas)"""
    try:
        carpeta_ruta = datos.get("carpeta_ruta")
        tipo_carpeta = datos.get("tipo_carpeta", "examenes")  # "examenes" o "practicas"
        archivo_nombre = datos.get("archivo")
        datos_examen = datos.get("datos")
        
        if not carpeta_ruta or not archivo_nombre or not datos_examen:
            raise HTTPException(status_code=400, detail="Faltan parámetros requeridos")
        
        # Construir ruta al archivo
        carpeta_destino = Path(tipo_carpeta) / carpeta_ruta
        archivo_path = carpeta_destino / archivo_nombre
        
        if not archivo_path.exists():
            raise HTTPException(status_code=404, detail=f"Examen no encontrado: {archivo_path}")
        
        # Guardar examen actualizado
        with open(archivo_path, 'w', encoding='utf-8') as f:
            json.dump(datos_examen, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Examen actualizado: {archivo_path}")
        
        return {
            "success": True,
            "message": "Examen actualizado correctamente"
        }
    except Exception as e:
        print(f"❌ Error actualizando examen: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al actualizar examen: {str(e)}")


# =============================
# TIMER SYNC ENDPOINTS
# =============================
# Timer sync removido - Los contadores se ejecutan localmente en el navegador
# y los datos se envían al servidor solo cuando es necesario




# =============================
# GESTIÓN DE DATOS PERSISTENTES (NOTAS, FLASHCARDS, PRÁCTICAS)
# =============================
EXTRACCIONES_PATH = Path("extracciones")
EXAMENES_PATH = Path("examenes")  # 🔥 NUEVA RUTA PARA EXÁMENES (paralela a extracciones/)
PRACTICAS_PATH = Path("practicas")  # 🔥 NUEVA RUTA PARA PRÁCTICAS (paralela a extracciones/)

@app.get("/datos/{tipo}")
def get_datos(tipo: str):
    """Lee notas, flashcards o prácticas desde archivos JSON"""
    try:
        # Si es flashcards, agregar todas las flashcards de todas las carpetas
        if tipo == "flashcards":
            todas_flashcards = []
            
            # Leer flashcards.json central (legacy)
            archivo_central = EXTRACCIONES_PATH / tipo / f"{tipo}.json"
            if archivo_central.exists():
                with open(archivo_central, "r", encoding="utf-8") as f:
                    flashcards_central = json.load(f)
                    todas_flashcards.extend(flashcards_central)
            
            # Leer flashcards.json de cada carpeta recursivamente
            for archivo_flashcard in EXTRACCIONES_PATH.rglob("flashcards.json"):
                # Saltar el archivo central
                if archivo_flashcard == archivo_central:
                    continue
                try:
                    with open(archivo_flashcard, "r", encoding="utf-8") as f:
                        flashcards_carpeta = json.load(f)
                        todas_flashcards.extend(flashcards_carpeta)
                except Exception as e:
                    print(f"⚠️ Error leyendo {archivo_flashcard}: {e}")
            
            print(f"📚 Flashcards cargadas: {len(todas_flashcards)} total")
            return JSONResponse(content=todas_flashcards)
        
        # Si es practicas, agregar todas las prácticas de todas las carpetas
        elif tipo == "practicas":
            todas_practicas = []
            
            # 🔥 BUSCAR EN MÚLTIPLES UBICACIONES
            carpetas_busqueda = [
                EXTRACCIONES_PATH,  # extracciones/
                Path("practicas"),   # practicas/
                Path("examenes")     # examenes/ (por si hay prácticas allí)
            ]
            
            # Leer practicas.json central (legacy)
            archivo_central = EXTRACCIONES_PATH / tipo / f"{tipo}.json"
            if archivo_central.exists():
                with open(archivo_central, "r", encoding="utf-8") as f:
                    practicas_central = json.load(f)
                    todas_practicas.extend(practicas_central)
            
            # Leer practicas.json de cada carpeta recursivamente EN TODAS LAS UBICACIONES
            for carpeta_raiz in carpetas_busqueda:
                if not carpeta_raiz.exists():
                    continue
                    
                for archivo_practica in carpeta_raiz.rglob("practica*.json"):
                    # Saltar el archivo central
                    if archivo_practica == archivo_central:
                        continue
                    try:
                        with open(archivo_practica, "r", encoding="utf-8") as f:
                            contenido = json.load(f)
                            # Puede ser una sola práctica o una lista
                            if isinstance(contenido, list):
                                todas_practicas.extend(contenido)
                            elif isinstance(contenido, dict):
                                todas_practicas.append(contenido)
                    except Exception as e:
                        print(f"⚠️ Error leyendo {archivo_practica}: {e}")
            
            print(f"🎯 Prácticas cargadas: {len(todas_practicas)} total")
            return JSONResponse(content=todas_practicas)
        
        # Si es examenes, agregar todos los exámenes de todas las carpetas
        elif tipo == "examenes":
            todos_examenes = []
            
            # 🔥 BUSCAR EN MÚLTIPLES UBICACIONES
            carpetas_busqueda = [
                EXTRACCIONES_PATH,  # extracciones/
                Path("examenes"),    # examenes/
                Path("practicas")    # practicas/ (por si hay exámenes allí)
            ]
            
            # Leer examenes.json central (legacy)
            archivo_central = EXTRACCIONES_PATH / tipo / f"{tipo}.json"
            if archivo_central.exists():
                with open(archivo_central, "r", encoding="utf-8") as f:
                    examenes_central = json.load(f)
                    todos_examenes.extend(examenes_central)
            
            # Leer examenes.json de cada carpeta recursivamente EN TODAS LAS UBICACIONES
            for carpeta_raiz in carpetas_busqueda:
                if not carpeta_raiz.exists():
                    continue
                    
                for archivo_examen in carpeta_raiz.rglob("examen*.json"):
                    # Saltar el archivo central
                    if archivo_examen == archivo_central:
                        continue
                    try:
                        with open(archivo_examen, "r", encoding="utf-8") as f:
                            contenido = json.load(f)
                            # Puede ser un solo examen o una lista
                            if isinstance(contenido, list):
                                todos_examenes.extend(contenido)
                            elif isinstance(contenido, dict):
                                todos_examenes.append(contenido)
                    except Exception as e:
                        print(f"⚠️ Error leyendo {archivo_examen}: {e}")
            
            print(f"📋 Exámenes cargados: {len(todos_examenes)} total")
            return JSONResponse(content=todos_examenes)
        
        # Si es notas, agregar todas las notas de todas las carpetas
        elif tipo == "notas":
            todas_notas = []
            
            # Leer notas.json central (legacy)
            archivo_central = EXTRACCIONES_PATH / tipo / f"{tipo}.json"
            if archivo_central.exists():
                with open(archivo_central, "r", encoding="utf-8") as f:
                    notas_central = json.load(f)
                    todas_notas.extend(notas_central)
            
            # Leer notas.json de cada carpeta recursivamente
            for archivo_nota in EXTRACCIONES_PATH.rglob("notas.json"):
                # Saltar el archivo central
                if archivo_nota == archivo_central:
                    continue
                try:
                    with open(archivo_nota, "r", encoding="utf-8") as f:
                        notas_carpeta = json.load(f)
                        todas_notas.extend(notas_carpeta)
                except Exception as e:
                    print(f"⚠️ Error leyendo {archivo_nota}: {e}")
            
            print(f"📝 Notas cargadas: {len(todas_notas)} total")
            return JSONResponse(content=todas_notas)
        
        else:
            # Para otros tipos, usar el archivo central
            archivo = EXTRACCIONES_PATH / tipo / f"{tipo}.json"
            if archivo.exists():
                with open(archivo, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return JSONResponse(content=data)
            return JSONResponse(content=[])
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/datos/{tipo}")
async def set_datos(tipo: str, request: Request):
    """Guarda notas, flashcards o prácticas en archivos JSON"""
    try:
        data = await request.json()
        carpeta = EXTRACCIONES_PATH / tipo
        carpeta.mkdir(parents=True, exist_ok=True)
        archivo = carpeta / f"{tipo}.json"
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return JSONResponse(content={"ok": True, "count": len(data) if isinstance(data, list) else 1})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/datos/flashcards/carpeta")
async def guardar_flashcard_carpeta(request: Request):
    """Guarda una flashcard en el archivo flashcards.json de su carpeta específica"""
    try:
        data = await request.json()
        flashcard = data.get("flashcard")
        carpeta_ruta = data.get("carpeta", "")
        
        if not flashcard:
            raise HTTPException(status_code=400, detail="Falta flashcard en los datos")
        
        # Determinar ruta del archivo
        if carpeta_ruta:
            carpeta_destino = EXTRACCIONES_PATH / carpeta_ruta
        else:
            # Si no hay carpeta, usar carpeta central de flashcards
            carpeta_destino = EXTRACCIONES_PATH / "flashcards"
        
        carpeta_destino.mkdir(parents=True, exist_ok=True)
        archivo_flashcards = carpeta_destino / "flashcards.json"
        
        # Leer flashcards existentes de esta carpeta
        flashcards_existentes = []
        if archivo_flashcards.exists():
            with open(archivo_flashcards, "r", encoding="utf-8") as f:
                flashcards_existentes = json.load(f)
        
        # Buscar si ya existe (por ID)
        flashcard_id = flashcard.get("id")
        if flashcard_id:
            # Actualizar existente
            encontrada = False
            for i, f in enumerate(flashcards_existentes):
                if f.get("id") == flashcard_id:
                    flashcards_existentes[i] = flashcard
                    encontrada = True
                    break
            if not encontrada:
                flashcards_existentes.append(flashcard)
        else:
            # Nueva flashcard
            flashcards_existentes.append(flashcard)
        
        # Guardar
        with open(archivo_flashcards, "w", encoding="utf-8") as f:
            json.dump(flashcards_existentes, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Flashcard guardada en: {archivo_flashcards}")
        print(f"   Total flashcards en carpeta: {len(flashcards_existentes)}")
        
        return JSONResponse(content={
            "ok": True,
            "count": len(flashcards_existentes),
            "archivo": str(archivo_flashcards)
        })
    except Exception as e:
        print(f"❌ Error guardando flashcard: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/datos/flashcards/carpeta/{carpeta_ruta:path}")
def get_flashcards_carpeta(carpeta_ruta: str):
    """Obtiene flashcards de una carpeta específica"""
    try:
        if carpeta_ruta:
            archivo = EXTRACCIONES_PATH / carpeta_ruta / "flashcards.json"
        else:
            archivo = EXTRACCIONES_PATH / "flashcards" / "flashcards.json"
        
        if archivo.exists():
            with open(archivo, "r", encoding="utf-8") as f:
                flashcards = json.load(f)
            return JSONResponse(content=flashcards)
        return JSONResponse(content=[])
    except Exception as e:
        print(f"❌ Error leyendo flashcards de {carpeta_ruta}: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.delete("/datos/flashcards/{flashcard_id}")
def delete_flashcard(flashcard_id: str, carpeta: str = ""):
    """Elimina una flashcard de su carpeta"""
    try:
        print(f"🗑️ Intentando eliminar flashcard ID: {flashcard_id} (tipo: {type(flashcard_id)})")
        print(f"   Carpeta especificada: '{carpeta}'")
        
        if carpeta:
            archivo = EXTRACCIONES_PATH / carpeta / "flashcards.json"
            print(f"   Buscando en: {archivo}")
        else:
            # Buscar en todas las carpetas
            print(f"   Buscando en todas las carpetas...")
            archivo = None
            for carpeta_path in EXTRACCIONES_PATH.rglob("flashcards.json"):
                with open(carpeta_path, "r", encoding="utf-8") as f:
                    flashcards = json.load(f)
                
                # Comparar tanto string como int
                flashcard_encontrada = any(
                    str(f.get("id")) == str(flashcard_id) for f in flashcards
                )
                if flashcard_encontrada:
                    archivo = carpeta_path
                    print(f"   ✅ Flashcard encontrada en: {archivo}")
                    break
            
            if not archivo:
                print(f"   ❌ Flashcard {flashcard_id} no encontrada en ninguna carpeta")
                return JSONResponse(content={"error": "Flashcard no encontrada"}, status_code=404)
        
        if not archivo.exists():
            print(f"   ❌ Archivo no existe: {archivo}")
            return JSONResponse(content={"error": "Archivo no encontrado"}, status_code=404)
        
        # Leer, eliminar y guardar
        with open(archivo, "r", encoding="utf-8") as f:
            flashcards = json.load(f)
        
        print(f"   📋 Total flashcards antes: {len(flashcards)}")
        
        # Comparar como string para evitar problemas de tipo
        flashcards_filtradas = [f for f in flashcards if str(f.get("id")) != str(flashcard_id)]
        
        print(f"   📋 Total flashcards después: {len(flashcards_filtradas)}")
        
        if len(flashcards_filtradas) == len(flashcards):
            print(f"   ⚠️ Flashcard {flashcard_id} no encontrada en esta carpeta")
            return JSONResponse(content={"error": "Flashcard no encontrada en esta carpeta"}, status_code=404)
        
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(flashcards_filtradas, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Flashcard {flashcard_id} eliminada de {archivo.parent.name}")
        return JSONResponse(content={
            "success": True,
            "count": len(flashcards_filtradas),
            "carpeta": str(archivo.parent.name)
        })
    except Exception as e:
        print(f"❌ Error eliminando flashcard {flashcard_id}: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

# ============================================
# ENDPOINTS PARA EXÁMENES Y PRÁCTICAS POR CARPETA
# ============================================

@app.post("/datos/examenes/carpeta")
async def guardar_examen_carpeta(request: Request):
    """
    🚫 ENDPOINT DESHABILITADO - YA NO GUARDA DUPLICADOS
    
    Los exámenes ya se guardan en /api/evaluar_examen como examen_TIMESTAMP.json
    Este endpoint causaba duplicados al guardar el mismo examen como ExamenGeneral.json
    
    Ahora solo retorna éxito sin guardar nada (el examen ya fue guardado en evaluar_examen)
    """
    try:
        data = await request.json()
        examen = data.get("examen")
        carpeta = data.get("carpeta", "")
        
        print(f"\n{'='*70}")
        print(f"⚠️ ENDPOINT /datos/examenes/carpeta LLAMADO (DESHABILITADO)")
        print(f"{'='*70}")
        print(f"📦 Examen ID: {examen.get('id') if examen else 'N/A'}")
        print(f"📁 Carpeta: {carpeta}")
        print(f"✅ El examen YA fue guardado en /api/evaluar_examen")
        print(f"   No se creará archivo duplicado ExamenGeneral.json")
        print(f"{'='*70}\n")
        
        # Retornar éxito sin guardar (el examen ya existe como examen_TIMESTAMP.json)
        return JSONResponse(content={
            "success": True,
            "archivo": examen.get('archivo', 'examen_existente.json'),
            "carpeta": carpeta,
            "message": "Examen ya guardado previamente (sin duplicado)"
        })
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/datos/examenes")
def get_examenes():
    """Obtiene todos los exámenes de todas las carpetas (examenes.json y archivos individuales)"""
    try:
        todos_examenes = []
        
        # 🔥 BUSCAR EN extracciones/{carpeta}/examen_*.json
        if EXTRACCIONES_PATH.exists():
            # 🚫 YA NO BUSCAR ExamenGeneral.json (causaba duplicados)
            # El endpoint /datos/examenes/carpeta fue deshabilitado
            # Solo se guardan archivos examen_TIMESTAMP.json en /api/evaluar_examen
            
            # Buscar examen_*.json Y practica_*.json
            for patron in ["examen_*.json", "practica_*.json"]:
                for archivo in EXTRACCIONES_PATH.rglob(patron):
                    try:
                        # 🔥 FILTRO: Excluir carpeta Practicas (legacy)
                        ruta_str = str(archivo).replace("\\", "/")
                        
                        if "/Practicas/" in ruta_str or ruta_str.startswith("Practicas/"):
                            print(f"⏭️  Saltando (carpeta Practicas legacy): {archivo}")
                            continue
                        
                        with open(archivo, "r", encoding="utf-8") as f:
                            examen = json.load(f)
                            
                            # 🔥 INCLUIR TANTO EXÁMENES COMO PRÁCTICAS
                            # (Las prácticas tienen es_practica=True, los exámenes no)
                            todos_examenes.append(examen)
                    except Exception as e:
                        print(f"Error leyendo {archivo}: {e}")
        
        # 1. LEGACY: Buscar recursivamente todos los examenes.json en extracciones/
        for archivo in EXTRACCIONES_PATH.rglob("examenes.json"):
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    examenes = json.load(f)
                    # Filtrar prácticas
                    examenes_filtrados = [e for e in examenes if not e.get("es_practica")]
                    todos_examenes.extend(examenes_filtrados)
            except Exception as e:
                print(f"Error leyendo {archivo}: {e}")
        
        # 2. LEGACY: Buscar en resultados_examenes/*.json (archivos individuales en extracciones/)
        for carpeta in EXTRACCIONES_PATH.iterdir():
            if carpeta.is_dir():
                resultados_path = carpeta / "resultados_examenes"
                if resultados_path.exists() and resultados_path.is_dir():
                    for archivo in resultados_path.glob("*.json"):
                        try:
                            with open(archivo, "r", encoding="utf-8") as f:
                                examen = json.load(f)
                                # Verificar que NO sea práctica
                                if not examen.get("es_practica"):
                                    todos_examenes.append(examen)
                        except Exception as e:
                            print(f"Error leyendo {archivo}: {e}")
        
        print(f"📊 Total archivos de exámenes encontrados: {len(todos_examenes)}")
        
        # 🔥 NORMALIZAR TODOS LOS EXÁMENES AL CARGAR
        print(f"🔄 Normalizando {len(todos_examenes)} exámenes completos...")
        for examen in todos_examenes:
            # Normalizar el examen completo (rutas, intervalos, tipos)
            examen = normalizar_examen_completo(examen)
        print(f"✅ Todos los exámenes normalizados")
        
        # 🔥 DEDUPLICAR EXÁMENES POR ID (más confiable)
        print(f"\n🔍 DEDUPLICACIÓN DE EXÁMENES:")
        examenes_unicos = {}
        for idx, examen in enumerate(todos_examenes):
            # Usar ID del examen como clave principal (más confiable)
            carpeta = examen.get('carpeta_ruta', 'sin-carpeta')
            fecha = examen.get('fecha_completado', 'sin-fecha')
            examen_id = examen.get('id', 'sin-id')
            archivo = examen.get('archivo', 'sin-archivo')
            
            print(f"   Examen #{idx + 1}: carpeta={carpeta}, fecha={fecha}, id={examen_id}, archivo={archivo}")
            
            # 🔥 CLAVE ÚNICA: ID del examen (único garantizado)
            # Si no tiene ID, usar carpeta + fecha + archivo como fallback
            if examen_id and examen_id != 'sin-id':
                clave_unica = str(examen_id)
            else:
                clave_unica = f"{carpeta}|{fecha}|{archivo}"
            
            print(f"      → Clave única: {clave_unica}")
            
            if clave_unica not in examenes_unicos:
                examenes_unicos[clave_unica] = examen
                print(f"      ✅ AGREGADO (nuevo)")
            else:
                print(f"      ⏭️  DUPLICADO (ya existe)")
                # Si ya existe, mantener el que tenga más datos completos
                examen_existente = examenes_unicos[clave_unica]
                
                # Preferencias de reemplazo:
                # 1. Preferir el que tenga preguntas
                # 2. Preferir el que tenga más resultados
                # 3. Preferir el que sea más reciente (por nombre de archivo)
                
                debe_reemplazar = False
                
                if not examen_existente.get('preguntas') and examen.get('preguntas'):
                    debe_reemplazar = True
                    print(f"      🔄 REEMPLAZAR: tiene preguntas")
                elif len(examen_existente.get('resultados', [])) < len(examen.get('resultados', [])):
                    debe_reemplazar = True
                    print(f"      🔄 REEMPLAZAR: más resultados ({len(examen.get('resultados', []))} vs {len(examen_existente.get('resultados', []))})")
                elif examen.get('archivo', '') > examen_existente.get('archivo', ''):
                    # Archivo más reciente (orden alfabético de timestamps)
                    debe_reemplazar = True
                    print(f"      🔄 REEMPLAZAR: archivo más reciente")
                
                if debe_reemplazar:
                    examenes_unicos[clave_unica] = examen
        
        todos_examenes = list(examenes_unicos.values())
        print(f"📋 Exámenes cargados: {len(todos_examenes)} total (únicos después de deduplicar)\n")
        
        return JSONResponse(content=todos_examenes)
    except Exception as e:
        print(f"❌ Error obteniendo exámenes: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/datos/examenes/normalizar")
async def normalizar_todos_examenes():
    """
    Normaliza TODOS los exámenes en examenes.json y archivos individuales
    Aplica:
    1. Tipos: "verdadero-falso" → "verdadero_falso"
    2. Intervalos: 0.5 → 1 (enteros >= 1)
    3. Rutas: "Platzi\\Prueba" → "Platzi/Prueba"
    """
    try:
        print(f"\n{'='*70}")
        print(f"🔧 NORMALIZACIÓN MASIVA DE EXÁMENES")
        print(f"{'='*70}")
        
        archivos_normalizados = 0
        examenes_normalizados = 0
        
        # 1️⃣ Normalizar archivos individuales en extracciones/
        if EXTRACCIONES_PATH.exists():
            # Normalizar ExamenGeneral.json
            for archivo in EXTRACCIONES_PATH.rglob("ExamenGeneral.json"):
                try:
                    with open(archivo, "r", encoding="utf-8") as f:
                        examen = json.load(f)
                    
                    # Normalizar
                    examen_normalizado = normalizar_examen_completo(examen)
                    
                    # Guardar
                    with open(archivo, "w", encoding="utf-8") as f:
                        json.dump(examen_normalizado, f, ensure_ascii=False, indent=2)
                    
                    archivos_normalizados += 1
                    examenes_normalizados += 1
                    print(f"   ✅ {archivo.relative_to(EXTRACCIONES_PATH)}")
                except Exception as e:
                    print(f"   ❌ Error en {archivo}: {e}")
            
            # Normalizar examen_*.json (legacy)
            for archivo in EXTRACCIONES_PATH.rglob("examen_*.json"):
                try:
                    with open(archivo, "r", encoding="utf-8") as f:
                        examen = json.load(f)
                    
                    # Normalizar
                    examen_normalizado = normalizar_examen_completo(examen)
                    
                    # Guardar
                    with open(archivo, "w", encoding="utf-8") as f:
                        json.dump(examen_normalizado, f, ensure_ascii=False, indent=2)
                    
                    archivos_normalizados += 1
                    examenes_normalizados += 1
                    print(f"   ✅ {archivo.relative_to(EXTRACCIONES_PATH)}")
                except Exception as e:
                    print(f"   ❌ Error en {archivo}: {e}")
        
        # 2️⃣ Normalizar examenes.json (legacy)
        for archivo in EXTRACCIONES_PATH.rglob("examenes.json"):
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    examenes = json.load(f)
                
                # Normalizar cada examen
                examenes_normalizados_en_archivo = [
                    normalizar_examen_completo(e) for e in examenes
                ]
                
                # Guardar
                with open(archivo, "w", encoding="utf-8") as f:
                    json.dump(examenes_normalizados_en_archivo, f, ensure_ascii=False, indent=2)
                
                archivos_normalizados += 1
                examenes_normalizados += len(examenes_normalizados_en_archivo)
                print(f"   ✅ {archivo.relative_to(EXTRACCIONES_PATH)} ({len(examenes)} exámenes)")
            except Exception as e:
                print(f"   ❌ Error en {archivo}: {e}")
        
        print(f"\n{'='*70}")
        print(f"📊 RESUMEN DE NORMALIZACIÓN")
        print(f"{'='*70}")
        print(f"✅ Archivos procesados: {archivos_normalizados}")
        print(f"✅ Exámenes normalizados: {examenes_normalizados}")
        print(f"{'='*70}\n")
        
        return JSONResponse(content={
            "success": True,
            "archivos_normalizados": archivos_normalizados,
            "examenes_normalizados": examenes_normalizados
        })
    except Exception as e:
        print(f"❌ Error en normalización masiva: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/datos/practicas/guardar_individual")
async def guardar_practica_individual(request: Request):
    """Guarda una práctica como archivo individual practica_TIMESTAMP.json en la carpeta de origen"""
    try:
        data = await request.json()
        practica = data.get("practica")
        carpeta_ruta = data.get("carpeta_ruta", "")
        
        print(f"\n{'='*60}")
        print(f"📥 GUARDAR PRÁCTICA INDIVIDUAL - DEBUG")
        print(f"{'='*60}")
        print(f"📁 carpeta_ruta recibida: '{carpeta_ruta}'")
        print(f"🆔 practica.id: {practica.get('id') if practica else 'N/A'}")
        print(f"📂 practica.carpeta: {practica.get('carpeta') if practica else 'N/A'}")
        print(f"📂 practica.carpeta_ruta: {practica.get('carpeta_ruta') if practica else 'N/A'}")
        print(f"{'='*60}\n")
        
        if not practica:
            return JSONResponse(content={"error": "No se proporcionó práctica"}, status_code=400)
        
        if not carpeta_ruta:
            return JSONResponse(content={"error": "No se especificó carpeta_ruta"}, status_code=400)
        
        # 🔥 LIMPIAR CARPETA_RUTA: Eliminar prefijos no deseados
        # Normalizar separadores a /
        carpeta_ruta_limpia = carpeta_ruta.replace("\\", "/")
        
        # Eliminar prefijos problemáticos
        prefijos_eliminar = ["extracciones/", "Practicas/", "practicas/"]
        for prefijo in prefijos_eliminar:
            if carpeta_ruta_limpia.startswith(prefijo):
                carpeta_ruta_limpia = carpeta_ruta_limpia[len(prefijo):]
        
        # Convertir de vuelta a backslashes para Windows
        carpeta_ruta_limpia = carpeta_ruta_limpia.replace("/", "\\")
        
        print(f"🔧 Carpeta limpia: '{carpeta_ruta_limpia}' (original: '{carpeta_ruta}')")
        
        # Usar la carpeta limpia
        carpeta_ruta = carpeta_ruta_limpia
        
        # 🔥 NORMALIZAR PREGUNTAS ANTES DE GUARDAR
        if 'preguntas' in practica and isinstance(practica['preguntas'], list):
            print(f"🔄 Normalizando {len(practica['preguntas'])} preguntas de la práctica...")
            practica['preguntas'] = [
                normalizar_pregunta_spaced_repetition(p) 
                for p in practica['preguntas']
            ]
            print(f"✅ Preguntas normalizadas para Spaced Repetition")
        
        # Construir ruta de carpeta destino (la misma donde está el documento de origen)
        carpeta_destino = EXTRACCIONES_PATH / carpeta_ruta
        carpeta_destino.mkdir(parents=True, exist_ok=True)
        
        # Generar nombre de archivo con timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_nombre = f"practica_{timestamp}.json"
        archivo_path = carpeta_destino / archivo_nombre
        
        # Marcar como práctica
        practica["es_practica"] = True
        practica["carpeta_ruta"] = carpeta_ruta
        practica["archivo"] = archivo_nombre
        
        # Guardar archivo
        with open(archivo_path, "w", encoding="utf-8") as f:
            json.dump(practica, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Práctica guardada en: {archivo_path}")
        print(f"   📁 Carpeta: {carpeta_ruta}")
        print(f"   📄 Archivo: {archivo_nombre}")
        print(f"   ✅ es_practica: {practica.get('es_practica')}")
        
        return JSONResponse(content={
            "success": True,
            "archivo": archivo_nombre,
            "carpeta": carpeta_ruta,
            "ruta_completa": str(archivo_path)
        })
    except Exception as e:
        print(f"❌ Error guardando práctica individual: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/datos/practicas/carpeta")
async def guardar_practica_carpeta(request: Request):
    """Guarda una práctica en su carpeta correspondiente"""
    try:
        data = await request.json()
        practica = data.get("practica")
        carpeta = data.get("carpeta", "")
        
        if not practica:
            return JSONResponse(content={"error": "No se proporcionó práctica"}, status_code=400)
        
        # 🔥 NORMALIZAR PREGUNTAS DE LA PRÁCTICA ANTES DE GUARDAR
        if 'preguntas' in practica and isinstance(practica['preguntas'], list):
            print(f"🔄 Normalizando {len(practica['preguntas'])} preguntas de la práctica...")
            practica['preguntas'] = [
                normalizar_pregunta_spaced_repetition(p) 
                for p in practica['preguntas']
            ]
            print(f"✅ Preguntas normalizadas para Spaced Repetition")
        
        # Determinar carpeta destino en extracciones/
        if carpeta:
            carpeta_destino = EXTRACCIONES_PATH / carpeta
        else:
            carpeta_destino = EXTRACCIONES_PATH / "practicas"
        
        carpeta_destino.mkdir(parents=True, exist_ok=True)
        archivo = carpeta_destino / "practicasArchivos.json"
        
        # Leer prácticas existentes
        practicas = []
        if archivo.exists():
            with open(archivo, "r", encoding="utf-8") as f:
                practicas = json.load(f)
        
        # 🔥 NORMALIZAR PREGUNTAS DE TODAS LAS PRÁCTICAS EXISTENTES
        print(f"🔄 Normalizando preguntas de {len(practicas)} prácticas existentes...")
        for practica_existente in practicas:
            if 'preguntas' in practica_existente and isinstance(practica_existente['preguntas'], list):
                practica_existente['preguntas'] = [
                    normalizar_pregunta_spaced_repetition(p)
                    for p in practica_existente['preguntas']
                ]
        print(f"✅ Todas las prácticas normalizadas")
        
        # Buscar si ya existe por ID y actualizar, o agregar nuevo
        practica_id = practica.get("id")
        encontrado = False
        for i, p in enumerate(practicas):
            if p.get("id") == practica_id:
                practicas[i] = practica
                encontrado = True
                break
        
        if not encontrado:
            practicas.append(practica)
        
        # Guardar
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(practicas, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Práctica guardada en: {archivo}")
        return JSONResponse(content={
            "success": True,
            "count": len(practicas),
            "carpeta": str(carpeta_destino.name)
        })
    except Exception as e:
        print(f"❌ Error guardando práctica: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/datos/practicas")
def get_practicas():
    """Obtiene todas las prácticas de todas las carpetas (practicas.json y resultados_practicas/*.json)"""
    print("\n" + "="*60)
    print("🔍 GET /datos/practicas - INICIANDO")
    print("="*60)
    try:
        todas_practicas = []
        
        # 1. Buscar recursivamente todos los practicas.json y practicasArchivos.json
        practicas_json_count = 0
        print(f"📁 Buscando practicas.json y practicasArchivos.json en: {EXTRACCIONES_PATH.absolute()}")
        for patron in ["practicas.json", "practicasArchivos.json"]:
            for archivo in EXTRACCIONES_PATH.rglob(patron):
                try:
                    print(f"   Encontrado: {archivo}")
                    with open(archivo, "r", encoding="utf-8") as f:
                        practicas = json.load(f)
                        if not isinstance(practicas, list):
                            print(f"   ⚠️ ADVERTENCIA: {archivo} no contiene un array, saltando...")
                            continue
                        todas_practicas.extend(practicas)
                        practicas_json_count += len(practicas)
                except json.JSONDecodeError as je:
                    print(f"   ❌ JSON CORRUPTO en {archivo}: {je}")
                    print(f"      Este archivo tiene formato JSON inválido, saltando...")
                except Exception as e:
                    print(f"   ❌ Error leyendo {archivo}: {e}")
        
        print(f"📁 Prácticas desde practicas.json: {practicas_json_count}")
        
        # 2. 🔥 BUSCAR practica_*.json EN TODAS LAS CARPETAS (nuevo formato)
        practicas_individuales_nuevas = 0
        print(f"🔍 Buscando archivos practica_*.json...")
        for archivo in EXTRACCIONES_PATH.rglob("practica_*.json"):
            try:
                # Excluir carpeta Practicas legacy
                ruta_str = str(archivo).replace("\\", "/")
                if "/Practicas/" in ruta_str or ruta_str.startswith("Practicas/"):
                    print(f"   ⏭️ Saltando (carpeta Practicas legacy): {archivo}")
                    continue
                
                with open(archivo, "r", encoding="utf-8") as f:
                    practica = json.load(f)
                    
                    # Verificar que sea un diccionario válido
                    if not isinstance(practica, dict):
                        print(f"   ⚠️ {archivo} no es un objeto JSON válido, saltando...")
                        continue
                    
                    # Verificar que tenga es_practica=true
                    if practica.get("es_practica"):
                        todas_practicas.append(practica)
                        practicas_individuales_nuevas += 1
                        print(f"   ✅ Cargada: {archivo} (id: {practica.get('id')})")
                    else:
                        print(f"   ⏭️ Archivo practica_*.json sin flag es_practica: {archivo}")
            except json.JSONDecodeError as je:
                print(f"   ❌ JSON CORRUPTO: {archivo}")
                print(f"      Error: {je}")
            except Exception as e:
                print(f"   ❌ Error leyendo {archivo}: {e}")
        
        print(f"📁 Archivos practica_*.json encontrados: {practicas_individuales_nuevas}")
        
        # 4. 🔥 BUSCAR PRÁCTICAS EN PROGRESO (pausadas) - DIRECTAMENTE EN CARPETAS
        practicas_progreso_count = 0
        print(f"🔍 Buscando prácticas en progreso (practica_progreso_*.json)...")
        for archivo in EXTRACCIONES_PATH.rglob("practica_progreso_*.json"):
            try:
                # Excluir si está en subcarpeta legacy practicas_progreso/
                ruta_str = str(archivo).replace("\\", "/")
                if "/practicas_progreso/" in ruta_str:
                    print(f"   ⏭️ Saltando (subcarpeta legacy): {archivo}")
                    continue
                    
                with open(archivo, "r", encoding="utf-8") as f:
                    practica = json.load(f)
                    
                    # Verificar que sea un diccionario válido
                    if not isinstance(practica, dict):
                        print(f"   ⚠️ {archivo} no es un objeto JSON válido, saltando...")
                        continue
                    
                    # Agregar marcador de que está en progreso
                    practica["completada"] = False
                    practica["es_practica"] = True
                    practica["en_progreso"] = True
                    todas_practicas.append(practica)
                    practicas_progreso_count += 1
                    print(f"   ✅ Práctica en progreso: {archivo.name}")
            except json.JSONDecodeError as je:
                print(f"   ❌ JSON CORRUPTO: {archivo}")
                print(f"      Error: {je}")
            except Exception as e:
                print(f"   ❌ Error leyendo {archivo}: {e}")
        
        print(f"📁 Prácticas en progreso: {practicas_progreso_count}")
        
        # 3. 🔥 BUSCAR TAMBIÉN EN resultados_practicas/*.json (archivos individuales legacy)
        practicas_individuales_count = 0
        print(f"🔍 Buscando en resultados_practicas/...")
        
        for carpeta in EXTRACCIONES_PATH.iterdir():
            if carpeta.is_dir():
                resultados_path = carpeta / "resultados_practicas"
                if resultados_path.exists() and resultados_path.is_dir():
                    archivos = list(resultados_path.glob("*.json"))
                    for archivo in archivos:
                        try:
                            with open(archivo, "r", encoding="utf-8") as f:
                                practica = json.load(f)
                                
                                # Verificar que sea un diccionario válido
                                if not isinstance(practica, dict):
                                    print(f"   ⚠️ {archivo.name} no es un objeto JSON válido, saltando...")
                                    continue
                                
                                # Verificar que tenga es_practica=true
                                if practica.get("es_practica"):
                                    todas_practicas.append(practica)
                                    practicas_individuales_count += 1
                                    print(f"   ✅ Cargada (legacy): {archivo.name} (id: {practica.get('id')})")
                        except json.JSONDecodeError as je:
                            print(f"   ❌ JSON CORRUPTO: {archivo.name}")
                            print(f"      Error: {je}")
                        except Exception as e:
                            print(f"   ❌ Error leyendo {archivo}: {e}")
        print(f"🔍 Buscando en resultados_practicas/...")
        
        for carpeta in EXTRACCIONES_PATH.iterdir():
            if carpeta.is_dir():
                resultados_path = carpeta / "resultados_practicas"
                if resultados_path.exists() and resultados_path.is_dir():
                    archivos = list(resultados_path.glob("*.json"))
                    for archivo in archivos:
                        try:
                            with open(archivo, "r", encoding="utf-8") as f:
                                practica = json.load(f)
                                # Verificar que tenga es_practica=true
                                if practica.get("es_practica"):
                                    todas_practicas.append(practica)
                                    practicas_individuales_count += 1
                                    print(f"   ✅ Cargada (legacy): {archivo.name} (id: {practica.get('id')})")
                        except Exception as e:
                            print(f"   ❌ Error leyendo {archivo}: {e}")
        
        print(f"\n📊 RESUMEN:")
        print(f"   📁 practicas.json: {practicas_json_count}")
        print(f"   📄 practica_*.json (nuevo): {practicas_individuales_nuevas}")
        print(f"   ⏸️ practicas_progreso/ (pausadas): {practicas_progreso_count}")
        print(f"   📂 resultados_practicas/ (legacy): {practicas_individuales_count}")
        print(f"   🎯 Total: {len(todas_practicas)}")
        
        # 🔥 NORMALIZAR PREGUNTAS DE TODAS LAS PRÁCTICAS AL CARGAR
        print(f"🔄 Normalizando preguntas en {len(todas_practicas)} prácticas...")
        for practica in todas_practicas:
            if 'preguntas' in practica and isinstance(practica['preguntas'], list):
                practica['preguntas'] = [
                    normalizar_pregunta_spaced_repetition(p)
                    for p in practica['preguntas']
                ]
        print(f"✅ Todas las prácticas normalizadas para Spaced Repetition")
        
        # 🔥 DEDUPLICAR PRÁCTICAS POR ID (evitar duplicados)
        practicas_unicas = {}
        for practica in todas_practicas:
            practica_id = practica.get('id')
            if practica_id and practica_id not in practicas_unicas:
                practicas_unicas[practica_id] = practica
        
        todas_practicas = list(practicas_unicas.values())
        print(f"🎯 Prácticas cargadas: {len(todas_practicas)} total (únicas después de deduplicar)")
        
        return JSONResponse(content=todas_practicas)
    except Exception as e:
        print(f"❌ Error obteniendo prácticas: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.delete("/datos/practicas/{practica_id}")
def delete_practica(practica_id: str, carpeta: str = ""):
    """Elimina una práctica de su carpeta"""
    try:
        print(f"\n🔍 DELETE práctica: ID={practica_id}, carpeta={carpeta}")
        archivo = None
        
        # 1. Si se especifica carpeta, buscar primero ahí (en ambos archivos)
        if carpeta:
            for nombre_archivo in ["practicas.json", "practicasArchivos.json"]:
                archivo_carpeta = EXTRACCIONES_PATH / carpeta / nombre_archivo
                print(f"   Buscando en: {archivo_carpeta}")
                if archivo_carpeta.exists():
                    with open(archivo_carpeta, "r", encoding="utf-8") as f:
                        practicas = json.load(f)
                    print(f"   Prácticas en {carpeta}/{nombre_archivo}: {len(practicas)}")
                    # Verificar si está en esta carpeta
                    if any(str(p.get("id")) == str(practica_id) for p in practicas):
                        archivo = archivo_carpeta
                        print(f"   ✓ Encontrada en carpeta especificada: {nombre_archivo}")
                        break
            if archivo:
                pass  # Ya encontrada, salir del if
        
        # 2. Si no se encontró, buscar en TODAS las carpetas (incluyendo legacy)
        if archivo is None:
            print(f"   No encontrada en carpeta especificada, buscando en todas...")
            for patron in ["practicas.json", "practicasArchivos.json"]:
                for carpeta_path in EXTRACCIONES_PATH.rglob(patron):
                    try:
                        with open(carpeta_path, "r", encoding="utf-8") as f:
                            practicas = json.load(f)
                        
                        print(f"   Revisando {carpeta_path}: {len(practicas)} prácticas")
                        if practicas:
                            print(f"      IDs: {[str(p.get('id')) for p in practicas[:3]]}")
                        
                        # Comparar tanto string como int
                        practica_encontrada = any(
                            str(p.get("id")) == str(practica_id) for p in practicas
                        )
                        if practica_encontrada:
                            archivo = carpeta_path
                            print(f"   ✓✓ Práctica encontrada en: {archivo}")
                            break
                    except Exception as e:
                        print(f"   Error leyendo {carpeta_path}: {e}")
                if archivo:  # Si ya encontró, salir del loop de patrones
                    break
        
        if archivo is None:
            print(f"   ❌ No encontrada en ninguna carpeta")
            return JSONResponse(content={"error": "Práctica no encontrada en ninguna carpeta"}, status_code=404)
        
        # Leer, eliminar y guardar
        with open(archivo, "r", encoding="utf-8") as f:
            practicas = json.load(f)
        
        print(f"   Total antes de eliminar: {len(practicas)}")
        
        # Comparar como string para evitar problemas de tipo
        practicas_filtradas = [p for p in practicas if str(p.get("id")) != str(practica_id)]
        
        print(f"   Total después de filtrar: {len(practicas_filtradas)}")
        
        if len(practicas_filtradas) == len(practicas):
            print(f"   ❌ No se eliminó nada (ID no coincide)")
            return JSONResponse(content={"error": "Práctica no encontrada en esta carpeta"}, status_code=404)
        
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(practicas_filtradas, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Práctica {practica_id} eliminada de {archivo.parent.name}")
        return JSONResponse(content={
            "success": True,
            "count": len(practicas_filtradas),
            "carpeta": str(archivo.parent.name)
        })
    except Exception as e:
        print(f"❌ Error eliminando práctica {practica_id}: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/datos/practicas/actualizar_archivo")
async def actualizar_archivo_practica(request: Request):
    """Actualiza un archivo individual de práctica (practica_*.json en carpeta raíz o legacy en resultados_practicas/)"""
    try:
        data = await request.json()
        practica = data.get("practica")
        
        if not practica:
            return JSONResponse(content={"error": "No se proporcionó práctica"}, status_code=400)
        
        practica_id = practica.get("id")
        carpeta_ruta = practica.get("carpeta_ruta") or practica.get("carpeta") or practica.get("ruta")
        archivo_nombre = practica.get("archivo")
        archivo_original = practica.get("archivo_original")  # 🔥 NOMBRE ORIGINAL
        
        print(f"\n{'='*60}")
        print(f"📝 POST /datos/practicas/actualizar_archivo")
        print(f"{'='*60}")
        print(f"   ID: {practica_id}")
        print(f"   carpeta_ruta: {carpeta_ruta}")
        print(f"   archivo: {archivo_nombre}")
        print(f"   archivo_original: {archivo_original}")
        print(f"   Campos disponibles: {list(practica.keys())}")
        
        if not carpeta_ruta:
            print(f"❌ ERROR: No se especificó carpeta_ruta")
            return JSONResponse(content={"error": "No se especificó carpeta_ruta"}, status_code=400)
        
        archivo_path = None
        
        # 🔥 PRIORIDAD 1: Si el archivo es practica_*.json, buscarlo en la carpeta raíz (nueva estructura)
        if archivo_nombre and (archivo_nombre.startswith("practica_") or archivo_nombre.startswith("practica_progreso_")):
            carpeta_principal = EXTRACCIONES_PATH / carpeta_ruta
            archivo_candidato = carpeta_principal / archivo_nombre
            
            # 🔥 Si se completa una práctica pausada Y tenemos el nombre original guardado
            if archivo_original and archivo_nombre.startswith("practica_progreso_"):
                archivo_path = carpeta_principal / archivo_original
                print(f"🔄 Recreando archivo con nombre original: {archivo_path}")
                practica["archivo"] = archivo_original  # Restaurar nombre original
                practica.pop("archivo_original", None)  # Remover campo temporal
                # Marcar el archivo pausado para eliminación
                if archivo_candidato.exists():
                    print(f"🗑️ Se eliminará archivo pausado: {archivo_candidato}")
            elif archivo_candidato.exists():
                archivo_path = archivo_candidato
                print(f"✅ Encontrado en carpeta raíz (nueva estructura): {archivo_path}")
            else:
                # 🔥 Si es practica_progreso_*.json que ya se completó, buscar versión sin "progreso"
                if archivo_nombre.startswith("practica_progreso_"):
                    archivo_completado = archivo_nombre.replace("practica_progreso_", "practica_")
                    archivo_candidato_completado = carpeta_principal / archivo_completado
                    if archivo_candidato_completado.exists():
                        archivo_path = archivo_candidato_completado
                        print(f"✅ Encontrado archivo completado: {archivo_path}")
                    else:
                        # Crear archivo completado (renombrado)
                        archivo_path = archivo_candidato_completado
                        print(f"📝 Se creará archivo completado (renombrado): {archivo_path}")
                        # Si existe el archivo _progreso, eliminarlo después de guardar
                        if archivo_candidato.exists():
                            print(f"🗑️ Se eliminará archivo pausado: {archivo_candidato}")
                else:
                    # Si no existe, lo creará en la carpeta raíz (nueva estructura)
                    archivo_path = archivo_candidato
                    print(f"📝 Se creará en carpeta raíz (nueva estructura): {archivo_path}")
        
        # 🔥 FALLBACK: Buscar en resultados_practicas/ (legacy) solo si no se encontró arriba
        if not archivo_path:
            carpeta_legacy = EXTRACCIONES_PATH / carpeta_ruta / "resultados_practicas"
            
            if archivo_nombre:
                archivo_candidato = carpeta_legacy / archivo_nombre
                if archivo_candidato.exists():
                    archivo_path = archivo_candidato
                    print(f"⚠️ Encontrado en resultados_practicas/ (legacy): {archivo_path}")
            
            # Buscar por ID en resultados_practicas/
            if not archivo_path and carpeta_legacy.exists():
                for archivo in carpeta_legacy.glob("*.json"):
                    try:
                        with open(archivo, "r", encoding="utf-8") as f:
                            data_existente = json.load(f)
                            if data_existente.get("id") == practica_id:
                                archivo_path = archivo
                                print(f"⚠️ Encontrado por ID en resultados_practicas/ (legacy): {archivo_path}")
                                break
                    except:
                        continue
        
        if not archivo_path:
            return JSONResponse(content={"error": f"No se encontró archivo de práctica con ID {practica_id}"}, status_code=404)
        
        # 🔥 Ya no necesitamos renombrar aquí si usamos archivo_original
        # La lógica de renombrado ya se manejó arriba al asignar archivo_path
        archivo_final = archivo_path
        
        # Guardar archivo actualizado (en la ruta final)
        archivo_final.parent.mkdir(parents=True, exist_ok=True)
        with open(archivo_final, "w", encoding="utf-8") as f:
            json.dump(practica, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Práctica actualizada en: {archivo_final}")
        
        # 🔥 Si completamos una práctica pausada, eliminar el archivo pausado
        if archivo_nombre and archivo_nombre.startswith("practica_progreso_"):
            carpeta_principal = EXTRACCIONES_PATH / carpeta_ruta
            archivo_pausado = carpeta_principal / archivo_nombre
            if archivo_pausado.exists() and archivo_pausado != archivo_final:
                try:
                    archivo_pausado.unlink()
                    print(f"🗑️ Archivo pausado eliminado: {archivo_pausado.name}")
                except Exception as e:
                    print(f"⚠️ No se pudo eliminar archivo pausado: {e}")
        
        return JSONResponse(content={
            "success": True,
            "archivo": str(archivo_final.name),
            "carpeta": carpeta_ruta
        })
    except Exception as e:
        print(f"❌ Error actualizando archivo de práctica: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/datos/practicas/eliminar")
async def eliminar_practica(request: Request):
    """Elimina un archivo de práctica"""
    try:
        data = await request.json()
        archivo = data.get("archivo")
        carpeta_ruta = data.get("carpeta_ruta")
        
        if not archivo or not carpeta_ruta:
            return JSONResponse(content={"error": "Faltan parámetros: archivo y carpeta_ruta"}, status_code=400)
        
        print(f"\n{'='*60}")
        print(f"🗑️ DELETE /datos/practicas/eliminar")
        print(f"{'='*60}")
        print(f"   archivo: {archivo}")
        print(f"   carpeta_ruta: {carpeta_ruta}")
        
        # Normalizar ruta
        carpeta_limpia = carpeta_ruta.replace('/', '\\')
        carpeta_destino = EXTRACCIONES_PATH / carpeta_limpia
        archivo_path = carpeta_destino / archivo
        
        if not archivo_path.exists():
            print(f"⚠️ Archivo no encontrado: {archivo_path}")
            return JSONResponse(content={"error": "Archivo no encontrado"}, status_code=404)
        
        # Eliminar archivo
        archivo_path.unlink()
        print(f"✅ Archivo eliminado: {archivo}")
        
        return JSONResponse(content={
            "success": True,
            "archivo": archivo
        })
    except Exception as e:
        print(f"❌ Error eliminando práctica: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/datos/examenes/actualizar_archivo")
async def actualizar_archivo_examen(request: Request):
    """Actualiza un archivo individual de examen"""
    try:
        data = await request.json()
        examen = data.get("examen")
        
        if not examen:
            return JSONResponse(content={"error": "No se proporcionó examen"}, status_code=400)
        
        examen_id = examen.get("id")
        carpeta_ruta = examen.get("carpeta_ruta") or examen.get("carpeta")
        archivo_nombre = examen.get("archivo")
        
        if not carpeta_ruta:
            return JSONResponse(content={"error": "No se especificó carpeta_ruta"}, status_code=400)
        
        # 🔥 BUSCAR EN NUEVA ESTRUCTURA: examenes/{carpeta}/examen_*.json
        carpeta_destino_nueva = EXAMENES_PATH / carpeta_ruta
        
        # LEGACY: También buscar en extracciones/{carpeta}/resultados_examenes/
        carpeta_destino_legacy = EXTRACCIONES_PATH / carpeta_ruta / "resultados_examenes"
        
        archivo_path = None
        
        # 1. Buscar primero en nueva estructura (examenes/)
        if archivo_nombre and carpeta_destino_nueva.exists():
            archivo_candidato = carpeta_destino_nueva / archivo_nombre
            if archivo_candidato.exists():
                archivo_path = archivo_candidato
        
        # 2. Si no se encontró y no hay nombre específico, buscar por ID en nueva estructura
        if not archivo_path and carpeta_destino_nueva.exists():
            for archivo in carpeta_destino_nueva.glob("examen_*.json"):
                try:
                    with open(archivo, "r", encoding="utf-8") as f:
                        data_existente = json.load(f)
                        if data_existente.get("id") == examen_id:
                            archivo_path = archivo
                            break
                except:
                    continue
        
        # 3. LEGACY: Buscar en resultados_examenes/ (estructura antigua)
        if not archivo_path:
            if archivo_nombre and carpeta_destino_legacy.exists():
                archivo_candidato = carpeta_destino_legacy / archivo_nombre
                if archivo_candidato.exists():
                    archivo_path = archivo_candidato
            
            # Buscar por ID en legacy
            if not archivo_path and carpeta_destino_legacy.exists():
                for archivo in carpeta_destino_legacy.glob("*.json"):
                    try:
                        with open(archivo, "r", encoding="utf-8") as f:
                            data_existente = json.load(f)
                            if data_existente.get("id") == examen_id:
                                archivo_path = archivo
                                break
                    except:
                        continue
        
        if not archivo_path:
            return JSONResponse(content={"error": f"No se encontró archivo de examen con ID {examen_id}"}, status_code=404)
        
        # Guardar archivo actualizado
        archivo_path.parent.mkdir(parents=True, exist_ok=True)
        with open(archivo_path, "w", encoding="utf-8") as f:
            json.dump(examen, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Examen actualizado en: {archivo_path}")
        return JSONResponse(content={
            "success": True,
            "archivo": str(archivo_path.name),
            "carpeta": carpeta_ruta
        })
    except Exception as e:
        print(f"❌ Error actualizando archivo de examen: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/datos/notas/carpeta")
async def guardar_nota_carpeta(request: Request):
    """Guarda una nota en su carpeta correspondiente"""
    try:
        data = await request.json()
        nota = data.get("nota")
        carpeta = data.get("carpeta", "")
        
        if not nota:
            return JSONResponse(content={"error": "No se proporcionó nota"}, status_code=400)
        
        # Determinar carpeta destino en extracciones/
        if carpeta:
            carpeta_destino = EXTRACCIONES_PATH / carpeta
        else:
            carpeta_destino = EXTRACCIONES_PATH / "notas"
        
        carpeta_destino.mkdir(parents=True, exist_ok=True)
        archivo = carpeta_destino / "notas.json"
        
        # Leer notas existentes
        notas = []
        if archivo.exists():
            with open(archivo, "r", encoding="utf-8") as f:
                notas = json.load(f)
        
        # Buscar si ya existe por ID y actualizar, o agregar nuevo
        nota_id = nota.get("id")
        encontrado = False
        for i, n in enumerate(notas):
            if n.get("id") == nota_id:
                notas[i] = nota
                encontrado = True
                break
        
        if not encontrado:
            notas.append(nota)
        
        # Guardar
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(notas, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Nota guardada en: {archivo}")
        return JSONResponse(content={
            "success": True,
            "count": len(notas),
            "carpeta": str(carpeta_destino.name)
        })
    except Exception as e:
        print(f"❌ Error guardando nota: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/datos/notas")
def get_notas():
    """Obtiene todas las notas de todas las carpetas"""
    try:
        todas_notas = []
        
        # Buscar recursivamente todos los notas.json
        for archivo in EXTRACCIONES_PATH.rglob("notas.json"):
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    notas = json.load(f)
                    todas_notas.extend(notas)
            except Exception as e:
                print(f"Error leyendo {archivo}: {e}")
        
        return JSONResponse(content=todas_notas)
    except Exception as e:
        print(f"❌ Error obteniendo notas: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.delete("/datos/notas/{nota_id}")
def delete_nota(nota_id: str, carpeta: str = ""):
    """Elimina una nota de su carpeta"""
    try:
        archivo = None
        
        if carpeta:
            archivo = EXTRACCIONES_PATH / carpeta / "notas.json"
            if not archivo.exists():
                # Intentar buscar en subcarpetas
                for carpeta_path in EXTRACCIONES_PATH.rglob("notas.json"):
                    if carpeta in str(carpeta_path):
                        with open(carpeta_path, "r", encoding="utf-8") as f:
                            notas = json.load(f)
                        if any(str(n.get("id")) == str(nota_id) for n in notas):
                            archivo = carpeta_path
                            break
        
        if not archivo or not archivo.exists():
            # Buscar en todas las carpetas
            for carpeta_path in EXTRACCIONES_PATH.rglob("notas.json"):
                with open(carpeta_path, "r", encoding="utf-8") as f:
                    notas = json.load(f)
                
                # Comparar tanto string como int
                nota_encontrada = any(
                    str(n.get("id")) == str(nota_id) for n in notas
                )
                if nota_encontrada:
                    archivo = carpeta_path
                    break
            else:
                return JSONResponse(content={"error": "Nota no encontrada"}, status_code=404)
        
        if not archivo.exists():
            return JSONResponse(content={"error": "Archivo no encontrado"}, status_code=404)
        
        # Leer, eliminar y guardar
        with open(archivo, "r", encoding="utf-8") as f:
            notas = json.load(f)
        
        # Comparar como string para evitar problemas de tipo
        notas_filtradas = [n for n in notas if str(n.get("id")) != str(nota_id)]
        
        if len(notas_filtradas) == len(notas):
            return JSONResponse(content={"error": "Nota no encontrada en esta carpeta"}, status_code=404)
        
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(notas_filtradas, f, indent=2, ensure_ascii=False)
        
        print(f"🗑️ Nota {nota_id} eliminada de {archivo.parent.name}")
        return JSONResponse(content={
            "success": True,
            "count": len(notas_filtradas),
            "carpeta": str(archivo.parent.name)
        })
    except Exception as e:
        print(f"❌ Error eliminando nota {nota_id}: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/datos/sesiones/completadas")
def get_sesiones_completadas():
    """Lee sesiones completadas"""
    try:
        archivo = EXTRACCIONES_PATH / "sesiones" / "completadas.json"
        if archivo.exists():
            with open(archivo, "r", encoding="utf-8") as f:
                data = json.load(f)
            return JSONResponse(content=data)
        return JSONResponse(content=[])
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/datos/sesiones/completadas")
async def set_sesiones_completadas(request: Request):
    """Guarda sesiones completadas"""
    try:
        data = await request.json()
        carpeta = EXTRACCIONES_PATH / "sesiones"
        carpeta.mkdir(parents=True, exist_ok=True)
        archivo = carpeta / "completadas.json"
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return JSONResponse(content={"ok": True})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/datos/sesion/activa")
def get_sesion_activa():
    """Lee la sesión activa"""
    try:
        archivo = EXTRACCIONES_PATH / "sesiones" / "activa.json"
        if archivo.exists():
            with open(archivo, "r", encoding="utf-8") as f:
                data = json.load(f)
            return JSONResponse(content=data)
        return JSONResponse(content={})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/datos/sesion/activa")
async def set_sesion_activa(request: Request):
    """Guarda la sesión activa"""
    try:
        data = await request.json()
        carpeta = EXTRACCIONES_PATH / "sesiones"
        carpeta.mkdir(parents=True, exist_ok=True)
        archivo = carpeta / "activa.json"
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return JSONResponse(content={"ok": True})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# ===== ENDPOINTS PARA GESTIÓN DE MODELOS OLLAMA =====

@app.get("/api/ollama/modelos")
async def listar_modelos_ollama():
    """Lista todos los modelos disponibles en Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            modelos = []
            for modelo in data.get('models', []):
                nombre = modelo.get('name', '')
                size_bytes = modelo.get('size', 0)
                size_gb = round(size_bytes / (1024**3), 2)
                
                modelos.append({
                    'nombre': nombre,
                    'tamaño_gb': size_gb,
                    'tipo': 'Ollama',
                    'digest': modelo.get('digest', '')[:12],
                    'velocidad': 'GPU/CPU'
                })
            
            return {
                'success': True,
                'modelos': modelos,
                'total': len(modelos)
            }
        else:
            return {
                'success': False,
                'mensaje': 'Ollama no está respondiendo. Asegúrate de que esté ejecutándose.',
                'modelos': [],
                'total': 0
            }
    except Exception as e:
        print(f"❌ Error al listar modelos de Ollama: {e}")
        return {
            'success': False,
            'mensaje': f'Error al conectar con Ollama: {str(e)}',
            'modelos': [],
            'total': 0
        }


@app.delete("/api/ollama/modelo/{nombre_modelo}")
async def eliminar_modelo_ollama(nombre_modelo: str):
    """Elimina un modelo de Ollama"""
    try:
        response = requests.delete(
            "http://localhost:11434/api/delete",
            json={"name": nombre_modelo},
            timeout=10
        )
        if response.status_code == 200:
            return {
                'success': True,
                'mensaje': f'✅ Modelo "{nombre_modelo}" eliminado correctamente'
            }
        else:
            return {
                'success': False,
                'mensaje': f'❌ Error al eliminar modelo: {response.text}'
            }
    except Exception as e:
        print(f"❌ Error eliminando modelo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/motor/cambiar")
async def cambiar_motor(data: dict):
    """Cambia la configuración del motor de IA"""
    global generador_actual
    
    try:
        usar_ollama = data.get('usar_ollama', False)
        modelo_ollama = data.get('modelo_ollama', None)
        modelo_gguf = data.get('modelo_gguf', None)
        n_gpu_layers = data.get('n_gpu_layers', 0)
        
        # Actualizar configuración
        config = cargar_config()
        config['usar_ollama'] = usar_ollama
        config['gpu_activa'] = n_gpu_layers > 0
        
        if usar_ollama and modelo_ollama:
            config['modelo_ollama_activo'] = modelo_ollama
        
        if modelo_gguf:
            config['modelo_path'] = modelo_gguf
        
        if n_gpu_layers >= 0:
            config['n_gpu_layers'] = n_gpu_layers
        
        guardar_config(config)
        
        # Reinicializar generador con los parámetros correctos
        try:
            if usar_ollama:
                generador_actual = GeneradorUnificado(
                    usar_ollama=True,
                    modelo_ollama=modelo_ollama or config.get('modelo_ollama_activo', 'qwen-local:latest'),
                    modelo_path_gguf=config.get('modelo_path'),
                    n_gpu_layers=n_gpu_layers
                )
                print(f"✅ GeneradorUnificado configurado para Ollama (GPU layers: {n_gpu_layers})")
            else:
                generador_actual = GeneradorUnificado(
                    usar_ollama=False,
                    modelo_path_gguf=modelo_gguf or config.get('modelo_path'),
                    n_gpu_layers=n_gpu_layers
                )
                print(f"✅ GeneradorUnificado configurado para GGUF (GPU layers: {n_gpu_layers})")
        except Exception as e:
            print(f"⚠️ Error inicializando GeneradorUnificado: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: reintentar sin GPU
            generador_actual = GeneradorUnificado()
            print(f"⚠️ Fallback a GeneradorUnificado default")
        
        return {
            'success': True,
            'mensaje': f'✅ Motor configurado correctamente',
            'config': config
        }
    except Exception as e:
        print(f"❌ Error cambiando motor: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/motor/reparar")
async def reparar_motor():
    """Repara/reinicia el motor de IA sin cambiar configuración"""
    global generador_actual
    
    try:
        print("\n🔧 Reparando motor de IA...")
        
        # Reinicializar generador con configuración actual
        config = cargar_config()
        generador_actual = GeneradorUnificado()
        
        # Verificar estado
        if generador_actual.usar_ollama:
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    mensaje = f"✅ Motor reparado - Ollama OK (modelo: {config.get('modelo_ollama_activo', 'default')})"
                else:
                    mensaje = "⚠️ Motor reiniciado pero Ollama no responde"
            except:
                mensaje = "⚠️ Motor reiniciado pero Ollama no está disponible"
        else:
            if generador_actual.llm:
                mensaje = f"✅ Motor reparado - GGUF cargado ({config.get('n_gpu_layers', 0)} capas GPU)"
            else:
                mensaje = "⚠️ Motor reiniciado pero no hay modelo GGUF cargado"
        
        return {
            'success': True,
            'mensaje': mensaje
        }
    except Exception as e:
        print(f"❌ Error reparando motor: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ===== ENDPOINTS PARA GESTIÓN DE HISTORIAL DE CHATS =====

# Directorio para chats
CHATS_DIR = Path("chats_historial")
CHATS_DIR.mkdir(exist_ok=True)


@app.get("/api/chats/historial")
async def obtener_historial_chats():
    """Obtiene la lista de chats guardados (deprecated - usar /api/chats/contenido)"""
    try:
        chats = []
        for archivo in CHATS_DIR.glob("*.json"):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    chats.append({
                        'id': archivo.stem,
                        'nombre': data.get('nombre', archivo.stem),
                        'fecha': data.get('fecha', ''),
                        'mensajes_count': len(data.get('mensajes', []))
                    })
            except Exception as e:
                print(f"Error leyendo {archivo}: {e}")
        
        return {'chats': sorted(chats, key=lambda x: x.get('fecha', ''), reverse=True)}
    except Exception as e:
        print(f"❌ Error al obtener historial: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chats/contenido")
async def obtener_contenido_chats(ruta: str = ''):
    """Obtiene carpetas y chats en una ruta específica"""
    try:
        ruta_completa = CHATS_DIR / ruta if ruta else CHATS_DIR
        ruta_completa.mkdir(parents=True, exist_ok=True)
        
        carpetas = []
        chats = []
        
        # Listar contenido
        for item in ruta_completa.iterdir():
            if item.is_dir():
                # Contar chats en la carpeta
                num_chats = len(list(item.glob("*.json")))
                carpetas.append({
                    'nombre': item.name,
                    'ruta': str(Path(ruta) / item.name) if ruta else item.name,
                    'num_chats': num_chats
                })
            elif item.suffix == '.json':
                try:
                    with open(item, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        chats.append({
                            'id': item.stem,
                            'nombre': data.get('nombre', item.stem),
                            'fecha': data.get('fecha', ''),
                            'mensajes_count': len(data.get('mensajes', [])),
                            'ruta': str(Path(ruta) / item.name) if ruta else item.name
                        })
                except Exception as e:
                    print(f"Error leyendo {item}: {e}")
        
        return {
            'carpetas': sorted(carpetas, key=lambda x: x['nombre']),
            'chats': sorted(chats, key=lambda x: x.get('fecha', ''), reverse=True),
            'ruta_actual': ruta
        }
    except Exception as e:
        print(f"❌ Error al obtener contenido: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chats/carpetas")
async def crear_carpeta_chat(data: dict):
    """Crea una nueva carpeta para organizar chats"""
    try:
        nombre = data.get('nombre', '')
        ruta_padre = data.get('ruta_padre', '')
        
        if not nombre:
            raise HTTPException(status_code=400, detail="Nombre de carpeta requerido")
        
        ruta_completa = CHATS_DIR / ruta_padre / nombre if ruta_padre else CHATS_DIR / nombre
        ruta_completa.mkdir(parents=True, exist_ok=True)
        
        return {
            'success': True,
            'mensaje': f'Carpeta "{nombre}" creada',
            'ruta': str(ruta_completa.relative_to(CHATS_DIR))
        }
    except Exception as e:
        print(f"❌ Error creando carpeta: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chats/carpetas")
async def listar_carpetas_chats(ruta: str = ""):
    """Lista todas las carpetas de chats disponibles"""
    try:
        ruta_base = CHATS_DIR / ruta if ruta else CHATS_DIR
        
        if not ruta_base.exists():
            return {'carpetas': []}
        
        carpetas = []
        for item in ruta_base.iterdir():
            if item.is_dir():
                # Contar chats en esta carpeta
                num_chats = len(list(item.glob("*.json")))
                
                carpetas.append({
                    'nombre': item.name,
                    'ruta': str(item.relative_to(CHATS_DIR)),
                    'num_chats': num_chats
                })
        
        return {'carpetas': sorted(carpetas, key=lambda x: x['nombre'])}
    except Exception as e:
        print(f"❌ Error listando carpetas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chats/guardar")
async def guardar_chat(data: dict):
    """Guarda un chat en el historial"""
    try:
        chat_id = data.get('id') or str(uuid.uuid4())
        nombre = data.get('nombre', f'Chat {datetime.now().strftime("%Y-%m-%d %H:%M")}')
        mensajes = data.get('mensajes', [])
        ruta = data.get('ruta', '')  # Ruta de carpeta opcional
        
        # Determinar ruta de guardado
        if ruta:
            archivo = CHATS_DIR / ruta / f"{chat_id}.json"
            archivo.parent.mkdir(parents=True, exist_ok=True)
        else:
            archivo = CHATS_DIR / f"{chat_id}.json"
        
        # Guardar chat
        chat_data = {
            'id': chat_id,
            'nombre': nombre,
            'fecha': datetime.now().isoformat(),
            'mensajes': mensajes
        }
        
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
        
        return {
            'success': True,
            'id': chat_id,
            'mensaje': 'Chat guardado exitosamente'
        }
    except Exception as e:
        print(f"❌ Error guardando chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chats/cargar/{chat_id}")
async def cargar_chat(chat_id: str):
    """Carga un chat específico"""
    try:
        # Buscar el archivo en todas las subcarpetas
        archivo_encontrado = None
        for archivo in CHATS_DIR.rglob(f"{chat_id}.json"):
            archivo_encontrado = archivo
            break
        
        if not archivo_encontrado:
            raise HTTPException(status_code=404, detail="Chat no encontrado")
        
        with open(archivo_encontrado, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            'success': True,
            'nombre': data.get('nombre', ''),
            'mensajes': data.get('mensajes', []),
            'fecha': data.get('fecha', '')
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error cargando chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chats/{chat_id}")
async def obtener_chat(chat_id: str):
    """Obtiene un chat específico (alias de cargar)"""
    return await cargar_chat(chat_id)


@app.delete("/api/chats/{chat_id}")
async def eliminar_chat(chat_id: str):
    """Elimina un chat del historial"""
    try:
        # Buscar el archivo en todas las subcarpetas
        archivo_encontrado = None
        for archivo in CHATS_DIR.rglob(f"{chat_id}.json"):
            archivo_encontrado = archivo
            break
        
        if archivo_encontrado and archivo_encontrado.exists():
            archivo_encontrado.unlink()
            return {
                'success': True,
                'mensaje': 'Chat eliminado'
            }
        else:
            raise HTTPException(status_code=404, detail="Chat no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error eliminando chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/chats/{chat_id}/renombrar")
async def renombrar_chat(chat_id: str, data: dict):
    """Renombra un chat del historial"""
    try:
        nuevo_nombre = data.get('nuevo_nombre', '').strip()
        if not nuevo_nombre:
            raise HTTPException(status_code=400, detail="Nombre vacío")
        
        # Buscar el archivo en todas las subcarpetas
        archivo_encontrado = None
        for archivo in CHATS_DIR.rglob(f"{chat_id}.json"):
            archivo_encontrado = archivo
            break
        
        if not archivo_encontrado or not archivo_encontrado.exists():
            raise HTTPException(status_code=404, detail="Chat no encontrado")
        
        # Leer el chat, actualizar el nombre y guardarlo
        with open(archivo_encontrado, 'r', encoding='utf-8') as f:
            chat_data = json.load(f)
        
        chat_data['nombre'] = nuevo_nombre
        
        with open(archivo_encontrado, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
        
        return {
            'success': True,
            'mensaje': f'Chat renombrado a "{nuevo_nombre}"'
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error renombrando chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/chats/carpetas/{ruta:path}")
async def eliminar_carpeta_chats(ruta: str):
    """Elimina una carpeta de chats y todo su contenido"""
    try:
        carpeta_path = CHATS_DIR / ruta
        
        if not carpeta_path.exists():
            raise HTTPException(status_code=404, detail="Carpeta no encontrada")
        
        if not carpeta_path.is_dir():
            raise HTTPException(status_code=400, detail="La ruta no es una carpeta")
        
        # Eliminar carpeta y todo su contenido
        import shutil
        shutil.rmtree(carpeta_path)
        
        return {
            'success': True,
            'mensaje': 'Carpeta eliminada'
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error eliminando carpeta: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/chats/carpetas/{ruta:path}/renombrar")
async def renombrar_carpeta_chats(ruta: str, data: dict):
    """Renombra una carpeta de chats"""
    try:
        nuevo_nombre = data.get('nuevo_nombre', '').strip()
        if not nuevo_nombre:
            raise HTTPException(status_code=400, detail="Nombre vacío")
        
        # Validar que no contenga caracteres inválidos
        caracteres_invalidos = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        if any(c in nuevo_nombre for c in caracteres_invalidos):
            raise HTTPException(status_code=400, detail="Nombre contiene caracteres inválidos")
        
        carpeta_actual = CHATS_DIR / ruta
        
        if not carpeta_actual.exists():
            raise HTTPException(status_code=404, detail="Carpeta no encontrada")
        
        # Obtener carpeta padre y nueva ruta
        carpeta_padre = carpeta_actual.parent
        nueva_ruta = carpeta_padre / nuevo_nombre
        
        if nueva_ruta.exists():
            raise HTTPException(status_code=400, detail="Ya existe una carpeta con ese nombre")
        
        # Renombrar
        carpeta_actual.rename(nueva_ruta)
        
        return {
            'success': True,
            'mensaje': f'Carpeta renombrada a "{nuevo_nombre}"',
            'nueva_ruta': str(nueva_ruta.relative_to(CHATS_DIR))
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error renombrando carpeta: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/chats/{chat_id}/mover")
async def mover_chat(chat_id: str, data: dict):
    """Mueve un chat a otra carpeta"""
    try:
        nueva_ruta = data.get('nueva_ruta', '').strip()
        
        # Buscar el archivo actual
        archivo_actual = None
        for archivo in CHATS_DIR.rglob(f"{chat_id}.json"):
            archivo_actual = archivo
            break
        
        if not archivo_actual:
            raise HTTPException(status_code=404, detail="Chat no encontrado")
        
        # Determinar carpeta destino
        if nueva_ruta:
            carpeta_destino = CHATS_DIR / nueva_ruta
        else:
            carpeta_destino = CHATS_DIR
        
        # Crear carpeta destino si no existe
        carpeta_destino.mkdir(parents=True, exist_ok=True)
        
        # Nueva ubicación del archivo
        archivo_nuevo = carpeta_destino / f"{chat_id}.json"
        
        if archivo_nuevo.exists():
            raise HTTPException(status_code=400, detail="Ya existe un chat con ese ID en el destino")
        
        # Mover archivo
        archivo_actual.rename(archivo_nuevo)
        
        return {
            'success': True,
            'mensaje': f'Chat movido a {nueva_ruta or "Raíz"}',
            'nueva_ubicacion': str(archivo_nuevo.relative_to(CHATS_DIR))
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error moviendo chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/chats/carpetas/{ruta:path}/mover")
async def mover_carpeta_chats(ruta: str, data: dict):
    """Mueve una carpeta de chats a otra ubicación"""
    try:
        nueva_ruta = data.get('nueva_ruta', '').strip()
        
        carpeta_actual = CHATS_DIR / ruta
        
        if not carpeta_actual.exists():
            raise HTTPException(status_code=404, detail="Carpeta no encontrada")
        
        # Obtener nombre de la carpeta
        nombre_carpeta = carpeta_actual.name
        
        # Determinar carpeta destino
        if nueva_ruta:
            carpeta_padre_destino = CHATS_DIR / nueva_ruta
        else:
            carpeta_padre_destino = CHATS_DIR
        
        # Validar que no se intente mover dentro de sí misma
        try:
            carpeta_actual.relative_to(carpeta_padre_destino)
            raise HTTPException(status_code=400, detail="No se puede mover una carpeta dentro de sí misma")
        except ValueError:
            pass  # Está bien, no es subcarpeta
        
        # Nueva ubicación
        carpeta_nueva = carpeta_padre_destino / nombre_carpeta
        
        if carpeta_nueva.exists():
            raise HTTPException(status_code=400, detail="Ya existe una carpeta con ese nombre en el destino")
        
        # Crear carpeta padre si no existe
        carpeta_padre_destino.mkdir(parents=True, exist_ok=True)
        
        # Mover carpeta
        import shutil
        shutil.move(str(carpeta_actual), str(carpeta_nueva))
        
        return {
            'success': True,
            'mensaje': f'Carpeta movida a {nueva_ruta or "Raíz"}',
            'nueva_ubicacion': str(carpeta_nueva.relative_to(CHATS_DIR))
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error moviendo carpeta: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
