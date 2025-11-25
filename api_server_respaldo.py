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
    """Carga la configuraci├│n guardada"""
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
    """Guarda la configuraci├│n"""
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def inicializar_modelo():
    """Carga autom├íticamente el modelo configurado al iniciar el servidor"""
    global generador_actual
    try:
        config = cargar_config()
        modelo_path = config.get("modelo_path")
        modelo_ollama = config.get("modelo_ollama_activo", "llama31-local")
        usar_ollama = config.get("usar_ollama", True)
        
        print(f"\n{'='*60}")
        print(f"­ƒÜÇ Iniciando Examinator API con Ollama + GPU...")
        print(f"{'='*60}\n")
        
        # Intentar usar Ollama primero (GPU autom├ítica)
        if usar_ollama:
            try:
                generador_actual = GeneradorUnificado(
                    usar_ollama=True,
                    modelo_ollama=modelo_ollama,
                    modelo_path_gguf=modelo_path,
                    n_gpu_layers=35
                )
                print(f"Ô£à Ollama cargado - Usando GPU autom├íticamente")
                print(f"­ƒÄ« Modelo activo: {modelo_ollama}")
                print(f"{'='*60}\n")
            except Exception as e:
                print(f"ÔÜá´©Å  Ollama no disponible: {e}")
                print(f"­ƒÆí Intentando con modelo GGUF...\n")
                
                # Fallback a GeneradorDosPasos si Ollama falla
                if modelo_path and Path(modelo_path).exists():
                    ajustes = config.get("ajustes_avanzados", {})
                    gpu_layers = ajustes.get('n_gpu_layers', 35)
                    generador_actual = GeneradorDosPasos(modelo_path=modelo_path, n_gpu_layers=gpu_layers)
                    print(f"Ô£à Modelo GGUF cargado: {modelo_path}")
                    print(f"{'='*60}\n")
                else:
                    print("\nÔÜá´©Å No hay modelo configurado o no existe el archivo")
                    print("­ƒÆí Ve a Configuraci├│n para seleccionar un modelo\n")
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
                print(f"Ô£à Modelo GGUF cargado: {modelo_path}")
                print(f"{'='*60}\n")
            else:
                print("\nÔÜá´©Å No hay modelo configurado o no existe el archivo")
                print("­ƒÆí Ve a Configuraci├│n para seleccionar un modelo\n")
    except Exception as e:
        print(f"\nÔØî Error al cargar modelo inicial: {e}")
        print("­ƒÆí Puedes configurar el modelo desde la interfaz web\n")


# Funci├│n para verificar y arrancar Ollama
def verificar_y_arrancar_ollama():
    """Verifica si Ollama est├í corriendo y lo arranca si no lo est├í"""
    import subprocess
    import platform
    
    try:
        # Verificar si Ollama responde
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("Ô£à Ollama ya est├í corriendo")
            return True
    except:
        print("ÔÜá´©Å Ollama no est├í corriendo, iniciando...")
        
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
                    print("Ô£à Ollama iniciado correctamente")
                    return True
            except:
                continue
        
        print("ÔÜá´©Å Ollama no pudo iniciarse autom├íticamente")
        return False
    except Exception as e:
        print(f"ÔØî Error al iniciar Ollama: {e}")
        return False


# Inicializar modelo al arrancar
@app.on_event("startup")
async def startup_event():
    """Se ejecuta cuando arranca el servidor"""
    print("\n" + "="*60)
    print("­ƒÜÇ INICIANDO EXAMINATOR API SERVER")
    print("="*60)
    
    # Verificar y arrancar Ollama autom├íticamente
    verificar_y_arrancar_ollama()
    
    # Inicializar modelo
    inicializar_modelo()
    
    print("="*60)
    print("Ô£à Servidor listo en http://localhost:8000")
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
    """Lista todos los modelos disponibles con informaci├│n detallada"""
    modelos_dir = Path("modelos")
    modelos_dir.mkdir(exist_ok=True)
    
    # Informaci├│n sobre diferentes tipos de modelos
    info_modelos = {
        "3B": {
            "parametros": "3 mil millones",
            "velocidad": "Muy r├ípida",
            "calidad": "Buena para tareas b├ísicas",
            "ram_necesaria": "4-6 GB",
            "descripcion": "Ideal para respuestas r├ípidas y preguntas simples. Perfecto para equipos con recursos limitados."
        },
        "7B": {
            "parametros": "7 mil millones",
            "velocidad": "R├ípida",
            "calidad": "Excelente balance calidad/velocidad",
            "ram_necesaria": "8-12 GB",
            "descripcion": "Mejor opci├│n para uso general. Genera preguntas m├ís elaboradas manteniendo buena velocidad."
        },
        "13B": {
            "parametros": "13 mil millones",
            "velocidad": "Media",
            "calidad": "Muy buena calidad",
            "ram_necesaria": "16-20 GB",
            "descripcion": "Para ex├ímenes complejos que requieren razonamiento profundo y preguntas m├ís sofisticadas."
        },
        "70B": {
            "parametros": "70 mil millones",
            "velocidad": "Lenta",
            "calidad": "M├íxima calidad",
            "ram_necesaria": "32+ GB",
            "descripcion": "Calidad profesional para evaluaciones cr├¡ticas. Requiere hardware potente."
        }
    }
    
    modelos = []
    for archivo in modelos_dir.glob("*.gguf"):
        tama├▒o = archivo.stat().st_size / (1024 * 1024 * 1024)  # GB
        nombre = archivo.stem
        
        # Detectar tama├▒o del modelo
        tama├▒o_modelo = "3B"
        for key in ["70B", "13B", "7B", "3B"]:
            if key in nombre.upper():
                tama├▒o_modelo = key
                break
        
        info = info_modelos.get(tama├▒o_modelo, {
            "parametros": "Desconocido",
            "velocidad": "Variable",
            "calidad": "A evaluar",
            "ram_necesaria": "Variable",
            "descripcion": "Modelo personalizado"
        })
        
        modelos.append({
            "nombre": nombre,
            "ruta": str(archivo),
            "tama├▒o_gb": round(tama├▒o, 2),
            "tama├▒o_modelo": tama├▒o_modelo,
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
            "tama├▒o_gb": 1.88,
            "tama├▒o_modelo": "3B",
            "parametros": "3 mil millones",
            "velocidad": "Muy r├ípida",
            "calidad": "Buena para tareas b├ísicas",
            "ram_necesaria": "4-6 GB",
            "descripcion": "Modelo peque├▒o y r├ípido, ideal para generar preguntas y evaluar respuestas. Perfecto para equipos con recursos limitados.",
            "recomendado": True,
            "requiere_auth": False
        },
        {
            "id": "llama-3.3-70b",
            "nombre": "Llama 3.3 70B Instruct",
            "archivo": "Llama-3.3-70B-Instruct-Q4_K_M.gguf",
            "url": "https://huggingface.co/bartowski/Llama-3.3-70B-Instruct-GGUF/resolve/main/Llama-3.3-70B-Instruct-Q4_K_M.gguf",
            "tama├▒o_gb": 40.2,
            "tama├▒o_modelo": "70B",
            "parametros": "70 mil millones",
            "velocidad": "Lenta",
            "calidad": "Calidad excepcional",
            "ram_necesaria": "48-64 GB",
            "descripcion": "El modelo m├ís avanzado de Meta, liberado en diciembre 2024. Excelente razonamiento y generaci├│n de contenido educativo de la m├ís alta calidad.",
            "recomendado": False,
            "requiere_auth": False
        },
        {
            "id": "qwen-2.5-7b",
            "nombre": "Qwen 2.5 7B Instruct",
            "archivo": "qwen2.5-7b-instruct-q4_k_m.gguf",
            "url": "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q4_k_m.gguf",
            "tama├▒o_gb": 4.4,
            "tama├▒o_modelo": "7B",
            "parametros": "7 mil millones",
            "velocidad": "R├ípida",
            "calidad": "Excelente, especialmente multiling├╝e",
            "ram_necesaria": "8-12 GB",
            "descripcion": "De Alibaba Cloud, septiembre 2024. Excelente en espa├▒ol y m├║ltiples idiomas. Muy bueno para contenido educativo y razonamiento.",
            "recomendado": True,
            "requiere_auth": False
        },
        {
            "id": "mistral-7b-v0.3",
            "nombre": "Mistral 7B Instruct v0.3",
            "archivo": "Mistral-7B-Instruct-v0.3-Q4_K_M.gguf",
            "url": "https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3-Q4_K_M.gguf",
            "tama├▒o_gb": 4.4,
            "tama├▒o_modelo": "7B",
            "parametros": "7 mil millones",
            "velocidad": "R├ípida",
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
            "tama├▒o_gb": 2.2,
            "tama├▒o_modelo": "3.8B",
            "parametros": "3.8 mil millones",
            "velocidad": "Muy r├ípida",
            "calidad": "Sorprendentemente buena para su tama├▒o",
            "ram_necesaria": "4-6 GB",
            "descripcion": "De Microsoft, mayo 2024. Modelo peque├▒o pero muy capaz, entrenado con datos de alta calidad. Ideal para equipos limitados.",
            "recomendado": False,
            "requiere_auth": False
        },
        {
            "id": "gemma-2-9b",
            "nombre": "Gemma 2 9B Instruct",
            "archivo": "gemma-2-9b-it-Q4_K_M.gguf",
            "url": "https://huggingface.co/bartowski/gemma-2-9b-it-GGUF/resolve/main/gemma-2-9b-it-Q4_K_M.gguf",
            "tama├▒o_gb": 5.4,
            "tama├▒o_modelo": "9B",
            "parametros": "9 mil millones",
            "velocidad": "R├ípida",
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
            "tama├▒o_gb": 4.92,
            "tama├▒o_modelo": "8B",
            "parametros": "8 mil millones",
            "velocidad": "R├ípida",
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
            "tama├▒o_gb": 8.7,
            "tama├▒o_modelo": "14B",
            "parametros": "14 mil millones",
            "velocidad": "Media",
            "calidad": "Muy alta, excelente en espa├▒ol",
            "ram_necesaria": "16-20 GB",
            "descripcion": "De Alibaba Cloud, septiembre 2024. Versi├│n m├ís potente de Qwen 2.5, sobresaliente en m├║ltiples idiomas y razonamiento complejo.",
            "recomendado": False,
            "requiere_auth": False
        }
    ]
    
    # Verificar cu├íles ya est├ín descargados
    modelos_dir = Path("modelos")
    modelos_dir.mkdir(exist_ok=True)
    
    archivos_descargados = {f.name for f in modelos_dir.glob("*.gguf")}
    
    for modelo in modelos_disponibles:
        modelo["descargado"] = modelo["archivo"] in archivos_descargados
    
    return {"modelos": modelos_disponibles}


@app.get("/api/config")
async def obtener_config():
    """Obtiene la configuraci├│n actual"""
    config = cargar_config()
    
    # A├▒adir informaci├│n del modelo cargado en memoria
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
            print(f"­ƒôè GET /api/config - Ollama detectado:")
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
    """Actualiza la configuraci├│n"""
    guardar_config(config)
    
    # Recargar generador con nuevo modelo
    global generador_actual
    if config.get("modelo_path"):
        try:
            # Liberar modelo anterior si existe
            if generador_actual and generador_actual.llm:
                print("­ƒöä Liberando modelo anterior...")
                del generador_actual.llm
                generador_actual.llm = None
                del generador_actual
                generador_actual = None
                
                # Forzar garbage collection
                import gc
                gc.collect()
                print("Ô£à Modelo anterior liberado")
            
            # Cargar nuevo modelo
            print(f"­ƒöä Cargando nuevo modelo: {config['modelo_path']}")
            generador_actual = GeneradorDosPasos(modelo_path=config["modelo_path"])
            print("Ô£à Nuevo modelo cargado exitosamente")
            return {"message": "Configuraci├│n actualizada y modelo cargado", "success": True}
        except Exception as e:
            print(f"ÔØî Error al cargar modelo: {e}")
            return {"message": f"Error al cargar modelo: {str(e)}", "success": False}
    
    return {"message": "Configuraci├│n actualizada", "success": True}


@app.get("/api/diagnostico/ollama")
async def diagnostico_ollama():
    """Verifica el estado de Ollama y devuelve informaci├│n de diagn├│stico"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            modelos = response.json()
            return {
                "estado": "ok",
                "corriendo": True,
                "mensaje": "Ollama est├í funcionando correctamente",
                "modelos_disponibles": len(modelos.get("models", [])),
                "puerto": 11434
            }
        else:
            return {
                "estado": "error",
                "corriendo": False,
                "mensaje": f"Ollama responde pero con error (c├│digo {response.status_code})",
                "puerto": 11434
            }
    except requests.exceptions.ConnectionError:
        return {
            "estado": "error",
            "corriendo": False,
            "mensaje": "Ollama no est├í corriendo. Usa el bot├│n 'Reparar' para iniciarlo.",
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
    """Intenta reparar Ollama arranc├índolo autom├íticamente"""
    import subprocess
    import platform
    import time
    
    # Primero verificar si ya est├í corriendo
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            return {
                "success": True,
                "mensaje": "Ô£à Ollama ya est├í funcionando correctamente",
                "accion": "ninguna"
            }
    except:
        pass
    
    # Intentar arrancar Ollama
    try:
        print("\n­ƒöº Intentando reparar Ollama...")
        
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
        
        # Esperar a que Ollama arranque (m├íximo 15 segundos)
        for i in range(15):
            time.sleep(1)
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=1)
                if response.status_code == 200:
                    print("Ô£à Ollama reparado exitosamente")
                    return {
                        "success": True,
                        "mensaje": "Ô£à Ollama iniciado correctamente. El chatbot ya est├í disponible.",
                        "accion": "iniciado",
                        "tiempo_arranque": f"{i+1} segundos"
                    }
            except:
                continue
        
        # Si llegamos aqu├¡, no arranc├│
        return {
            "success": False,
            "mensaje": "ÔÜá´©Å Ollama no pudo iniciarse autom├íticamente. Intenta manualmente: ollama serve",
            "accion": "fallido"
        }
        
    except FileNotFoundError:
        return {
            "success": False,
            "mensaje": "ÔØî Ollama no est├í instalado en el sistema. Desc├írgalo de https://ollama.ai",
            "accion": "no_instalado"
        }
    except Exception as e:
        print(f"ÔØî Error al reparar Ollama: {e}")
        return {
            "success": False,
            "mensaje": f"ÔØî Error al iniciar Ollama: {str(e)}",
            "accion": "error"
        }


@app.post("/api/chat")
async def chat_con_modelo(data: dict):
    """Endpoint para chatear con el modelo (soporta Ollama y GGUF con fallback autom├ítico)"""
    global generador_actual
    
    mensaje = data.get("mensaje", "").strip()
    if not mensaje:
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vac├¡o")
    
    print(f"\n{'='*70}")
    print(f"­ƒÆ¼ CHAT REQUEST RECIBIDA")
    print(f"{'='*70}")
    print(f"­ƒôØ Mensaje: {mensaje[:100]}...")
    
    # Verificar si hay modelo cargado
    if generador_actual is None:
        print("ÔØî generador_actual es None")
        return {"respuesta": "ÔØî No hay modelo inicializado. Ve a Configuraci├│n para seleccionar uno."}
    
    print(f"Ô£à Generador actual existe")
    print(f"­ƒöº Tipo configurado: {'Ollama' if generador_actual.usar_ollama else 'GGUF'}")
    
    # Si est├í configurado para Ollama, intentar usarlo con fallback a GGUF
    usar_ollama_exitoso = False
    if generador_actual.usar_ollama:
        try:
            # Verificar si Ollama est├í disponible
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                usar_ollama_exitoso = True
                print("Ô£à Ollama disponible - usando Ollama")
            else:
                print(f"ÔÜá´©Å Ollama no responde (status {response.status_code}) - fallback a GGUF")
        except Exception as e:
            print(f"ÔÜá´©Å Ollama no disponible ({str(e)}) - fallback a GGUF")
    
    # Si no usa Ollama o fall├│, verificar GGUF
    if not usar_ollama_exitoso:
        if generador_actual.llm is None:
            return {"respuesta": "ÔØî Ollama no est├í disponible y no hay modelo GGUF cargado. Por favor:\n\n1. Inicia Ollama con: ollama serve\n2. O carga un modelo GGUF desde Configuraci├│n"}
        print(f"Ô£à LLM GGUF cargado correctamente - usando fallback")
    
    try:
        # Obtener ajustes avanzados del frontend
        ajustes = data.get("ajustes", {})
        temperature = ajustes.get("temperature", 0.7)
        max_tokens = ajustes.get("max_tokens", 768)
        
        print(f"\n{'='*60}")
        print(f"­ƒÆ¼ Solicitud de chat")
        print(f"ÔÜÖ´©Å Temperatura: {temperature} | Max tokens: {max_tokens}")
        print(f"{'='*60}\n")
        
        # Preparar el contexto si existe
        contexto = data.get("contexto", None)
        buscar_web = data.get("buscar_web", False)
        mensaje_completo = mensaje
        system_prompt = "Eres un asistente educativo ├║til y respondes de manera clara y concisa en espa├▒ol."
        
        # Si se solicita b├║squeda web
        if buscar_web:
            try:
                print(f"­ƒîÉ Realizando b├║squeda web para: {mensaje}")
                resultado_busqueda = buscar_y_resumir(mensaje, max_resultados=3)
                
                if resultado_busqueda.get('exito', False) and resultado_busqueda.get('resultados'):
                    contexto_web = resultado_busqueda['resumen']
                    system_prompt = "Eres un asistente que tiene acceso a informaci├│n de internet. DEBES usar ├ÜNICAMENTE la informaci├│n proporcionada de las b├║squedas web para responder."
                    mensaje_completo = f"""INFORMACI├ôN DE B├ÜSQUEDA WEB:\n\n{contexto_web}\n\n---\n\nPREGUNTA DEL USUARIO: {mensaje}\n\nResponde usando SOLO la informaci├│n de b├║squeda web proporcionada."""
                else:
                    return {"respuesta": "­ƒîÉ No pude encontrar informaci├│n actualizada en internet sobre ese tema."}
            except Exception as e:
                print(f"ÔØî Error en b├║squeda web: {e}")
                return {"respuesta": f"­ƒîÉ Error al buscar en internet: {str(e)}"}
        
        # Si hay contexto de archivo
        elif contexto:
            contexto_limitado = contexto[:4000] if len(contexto) > 4000 else contexto
            system_prompt = "Eres un asistente que analiza documentos. Responde bas├índote ├ÜNICAMENTE en el contenido del documento proporcionado."
            mensaje_completo = f"""DOCUMENTO:\n\n---\n{contexto_limitado}\n---\n\nPREGUNTA: {mensaje}\n\nResponde usando SOLO la informaci├│n del documento."""
        
        # Construir historial de mensajes
        historial = data.get("historial", [])
        messages = [{"role": "system", "content": system_prompt}]
        
        print(f"\n{'='*70}")
        print(f"­ƒôÑ HISTORIAL RECIBIDO DEL FRONTEND")
        print(f"{'='*70}")
        print(f"­ƒôè Total mensajes recibidos: {len(historial)}")
        
        # Agregar historial previo (IMPORTANTE: no incluir el ├║ltimo mensaje porque ya viene en 'mensaje')
        if historial:
            # Tomar m├ís mensajes del historial para mejor contexto
            historial_reciente = historial[-20:]  # ├Ültimos 20 mensajes (10 intercambios)
            if buscar_web:
                historial_reciente = historial[-12:]  # 6 intercambios para b├║squeda web
            elif contexto:
                historial_reciente = historial[-8:]  # 4 intercambios con contexto
            
            print(f"­ƒôî Mensajes a procesar: {len(historial_reciente)} (filtrados de {len(historial)} totales)")
            print(f"\n­ƒöì CONSTRUYENDO CONTEXTO PARA EL MODELO:")
            print(f"1. [SYSTEM] {system_prompt[:80]}...")
            
            # Filtrar solo hasta el pen├║ltimo mensaje (el ├║ltimo es el actual)
            for i, msg in enumerate(historial_reciente[:-1]):
                tipo = msg.get('tipo', 'unknown')
                texto = msg.get('texto', '')
                preview = texto[:100] if len(texto) > 100 else texto
                
                if tipo == 'usuario':
                    messages.append({"role": "user", "content": texto})
                    print(f"{len(messages)}. [USER] {preview}...")
                elif tipo == 'asistente':
                    messages.append({"role": "assistant", "content": texto})
                    print(f"{len(messages)}. [ASSISTANT] {preview}...")
        
        # Agregar mensaje actual
        messages.append({"role": "user", "content": mensaje_completo})
        print(f"{len(messages)}. [USER - ACTUAL] {mensaje_completo[:100]}...")
        
        print(f"\n­ƒô¿ TOTAL MENSAJES ENVIADOS AL MODELO: {len(messages)}")
        print(f"   ÔööÔöÇ 1 system + {len(messages)-2} historial + 1 actual")
        print(f"{'='*70}\n")
        
        # Generar respuesta usando GeneradorUnificado con fallback
        print(f"­ƒñû Generando respuesta con temperatura={temperature}, max_tokens={max_tokens}")
        print(f"­ƒöº Usando {'Ollama' if usar_ollama_exitoso else 'GGUF/GPU (fallback)'}")
        
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
        
        print(f"Ô£à Respuesta generada: {len(respuesta_texto)} caracteres")
        print(f"­ƒôØ Preview: {respuesta_texto[:100]}...\n")
        
        return {"respuesta": respuesta_texto}
        
    except Exception as e:
        print(f"ÔØî Error en chat: {e}")
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
        print(f"ÔØî Error guardando nota: {e}")
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
        
        print(f"Ô£à Contexto guardado: {ruta_completa}")
        
        return {
            "success": True,
            "message": f"Contexto guardado exitosamente",
            "ruta": str(ruta_completa.relative_to(cursos_db.base_path)),
            "archivo": nombre_archivo
        }
    except Exception as e:
        print(f"ÔØî Error guardando contexto: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat_anterior")
async def chat_con_modelo(data: dict):
    """Endpoint para chatear con el modelo (soporta Ollama y GGUF)"""
    global generador_actual
    
    mensaje = data.get("mensaje", "").strip()
    if not mensaje:
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vac├¡o")
    
    print(f"\n{'='*70}")
    print(f"­ƒÆ¼ CHAT REQUEST RECIBIDA")
    print(f"{'='*70}")
    print(f"­ƒôØ Mensaje: {mensaje[:100]}...")
    
    # Verificar si hay modelo cargado
    if generador_actual is None:
        print("ÔØî generador_actual es None")
        return {"respuesta": "ÔØî No hay modelo inicializado. Ve a Configuraci├│n para seleccionar uno."}
    
    print(f"Ô£à Generador actual existe")
    print(f"­ƒöº Tipo: {'Ollama' if generador_actual.usar_ollama else 'GGUF'}")
    
    if not generador_actual.usar_ollama:
        if generador_actual.llm is None:
            print("ÔØî generador_actual.llm es None (GGUF no cargado)")
            return {"respuesta": "ÔØî Modelo GGUF no est├í cargado. Ve a Configuraci├│n y carga un modelo."}
        print(f"Ô£à LLM cargado correctamente")
    
    try:
        # Obtener ajustes avanzados del frontend
        ajustes = data.get("ajustes", {})
        temperature = ajustes.get("temperature", 0.7)
        max_tokens = ajustes.get("max_tokens", 768)
        
        print(f"\n{'='*60}")
        print(f"­ƒÆ¼ Solicitud de chat")
        print(f"ÔÜÖ´©Å Temperatura: {temperature} | Max tokens: {max_tokens}")
        print(f"{'='*60}\n")
        
        # Preparar el contexto si existe
        contexto = data.get("contexto", None)
        buscar_web = data.get("buscar_web", False)
        mensaje_completo = mensaje
        system_prompt = "Eres un asistente educativo ├║til y respondes de manera clara y concisa en espa├▒ol."
        
        # Si se solicita b├║squeda web
        if buscar_web:
            try:
                print(f"­ƒîÉ Realizando b├║squeda web para: {mensaje}")
                resultado_busqueda = buscar_y_resumir(mensaje, max_resultados=3)
                
                if resultado_busqueda.get('exito', False) and resultado_busqueda.get('resultados'):
                    contexto_web = resultado_busqueda['resumen']
                    system_prompt = "Eres un asistente que tiene acceso a informaci├│n de internet. DEBES usar ├ÜNICAMENTE la informaci├│n proporcionada de las b├║squedas web para responder."
                    mensaje_completo = f"""INFORMACI├ôN DE B├ÜSQUEDA WEB:\n\n{contexto_web}\n\n---\n\nPREGUNTA DEL USUARIO: {mensaje}\n\nResponde usando SOLO la informaci├│n de b├║squeda web proporcionada."""
                else:
                    return {"respuesta": "­ƒîÉ No pude encontrar informaci├│n actualizada en internet sobre ese tema."}
            except Exception as e:
                print(f"ÔØî Error en b├║squeda web: {e}")
                return {"respuesta": f"­ƒîÉ Error al buscar en internet: {str(e)}"}
        
        # Si hay contexto de archivo
        elif contexto:
            contexto_limitado = contexto[:4000] if len(contexto) > 4000 else contexto
            system_prompt = "Eres un asistente que analiza documentos. Responde bas├índote ├ÜNICAMENTE en el contenido del documento proporcionado."
            mensaje_completo = f"""DOCUMENTO:\n\n---\n{contexto_limitado}\n---\n\nPREGUNTA: {mensaje}\n\nResponde usando SOLO la informaci├│n del documento."""
        
        # Construir historial de mensajes
        historial = data.get("historial", [])
        messages = [{"role": "system", "content": system_prompt}]
        
        # Agregar historial previo
        if historial:
            historial_reciente = historial[-10:]  # ├Ültimos 10 mensajes
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
        print(f"­ƒñû Generando respuesta con temperatura={temperature}, max_tokens={max_tokens}")
        print(f"­ƒöº Usando {'Ollama' if generador_actual.usar_ollama else 'GGUF/GPU'}")
        
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
                return {"respuesta": "ÔØî Modelo GGUF no est├í cargado. Ve a Configuraci├│n y carga un modelo."}
            
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
        
        print(f"Ô£à Respuesta generada: {len(respuesta_texto)} caracteres")
        print(f"­ƒôØ Preview: {respuesta_texto[:100]}...\n")
        return {"respuesta": respuesta_texto}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"respuesta": f"ÔØî Error al generar respuesta: {str(e)}"}


@app.post("/api/buscar-web")
async def buscar_web_endpoint(data: dict):
    """Endpoint para realizar b├║squedas en internet"""
    query = data.get("query", "").strip()
    max_resultados = data.get("max_resultados", 3)
    
    if not query:
        raise HTTPException(status_code=400, detail="Se requiere un t├®rmino de b├║squeda")
    
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
    print(f"­ƒôä Procesando archivo: {file.filename}")
    print(f"   Tipo de contenido: {file.content_type}")
    print(f"   Carpeta destino: {carpeta or 'ra├¡z'}")
    
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
        
        print(f"   Ô£à Texto extra├¡do: {len(texto)} caracteres")
        
        # Determinar carpeta de destino
        if carpeta:
            carpeta_destino = Path("extracciones") / carpeta
        else:
            # Si no se especifica carpeta, usar la ra├¡z de extracciones
            carpeta_destino = Path("extracciones")
        
        carpeta_destino.mkdir(parents=True, exist_ok=True)
        
        nombre_limpio = temp_path.stem.replace(' ', '_')
        archivo_salida = carpeta_destino / f"{nombre_limpio}.txt"
        
        # Si ya existe, agregar n├║mero
        contador = 1
        while archivo_salida.exists():
            archivo_salida = carpeta_destino / f"{nombre_limpio}_{contador}.txt"
            contador += 1
        
        archivo_salida.write_text(texto, encoding='utf-8')
        
        print(f"   ­ƒÆ¥ Guardado en: {archivo_salida}")
        
        return {
            "success": True,
            "mensaje": "Archivo procesado exitosamente",
            "archivo": str(archivo_salida.relative_to(Path("extracciones"))),
            "ruta_completa": str(archivo_salida),
            "caracteres": len(texto),
            "palabras": len(texto.split()),
            "carpeta": carpeta or "ra├¡z"
        }
    
    except Exception as e:
        print(f"   ÔØî Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar archivo: {str(e)}")
    
    finally:
        # Limpiar archivo temporal
        if temp_path.exists():
            temp_path.unlink()
            print(f"   ­ƒùæ´©Å Archivo temporal eliminado")


@app.get("/api/documentos")
async def listar_documentos():
    """Lista todos los documentos extra├¡dos"""
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
                    "tama├▒o_kb": round(archivo.stat().st_size / 1024, 2)
                })
    
    return {"documentos": documentos}


# ========== ENDPOINTS DE NAVEGACI├ôN DE CARPETAS ==========

@app.get("/api/carpetas")
async def listar_carpetas(ruta: str = ""):
    """Lista todas las carpetas en una ruta espec├¡fica"""
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
        raise HTTPException(status_code=400, detail="La ruta actual no puede estar vac├¡a")
    
    if not nuevo_nombre:
        raise HTTPException(status_code=400, detail="El nuevo nombre no puede estar vac├¡o")
    
    try:
        # Usar el m├®todo de base de datos para renombrar
        resultado = cursos_db.renombrar_carpeta(ruta_actual, nuevo_nombre)
        return {"success": True, **resultado}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/carpetas/mover")
async def mover_carpeta(datos: dict):
    """Mueve una carpeta a otra ubicaci├│n"""
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
    
    print(f"­ƒöä Renombrar documento:")
    print(f"   Ruta actual: {ruta_actual}")
    print(f"   Nuevo nombre: {nuevo_nombre}")
    
    if not ruta_actual:
        raise HTTPException(status_code=400, detail="La ruta actual no puede estar vac├¡a")
    
    if not nuevo_nombre:
        raise HTTPException(status_code=400, detail="El nuevo nombre no puede estar vac├¡o")
    
    try:
        resultado = cursos_db.renombrar_documento(ruta_actual, nuevo_nombre)
        print(f"   Ô£à Resultado: {resultado}")
        return {"success": True, **resultado}
    except ValueError as e:
        print(f"   ÔØî Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/arbol")
async def obtener_arbol():
    """Obtiene el ├írbol completo de carpetas"""
    try:
        return cursos_db.obtener_arbol()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/carpetas/info")
async def obtener_info_carpeta(ruta: str = ""):
    """Obtiene informaci├│n detallada de una carpeta espec├¡fica"""
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
        print(f"ÔØî Error obteniendo info de carpeta: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/carpetas/archivos-recursivos")
async def obtener_archivos_recursivos(ruta: str = ""):
    """Obtiene todos los archivos .txt recursivamente de una carpeta y sus subcarpetas"""
    try:
        print(f"\n{'='*70}")
        print(f"­ƒôé OBTENER ARCHIVOS RECURSIVOS")
        print(f"{'='*70}")
        print(f"­ƒôü Ruta: {ruta}")
        
        archivos = cursos_db.listar_documentos_recursivo(ruta)
        print(f"­ƒôÜ Archivos encontrados: {len(archivos)}")
        
        return {
            "archivos": archivos,
            "total": len(archivos)
        }
    except Exception as e:
        print(f"ÔØî Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generar_examen_bloque")
async def generar_examen_bloque(datos: dict):
    """Genera preguntas para un bloque de archivos"""
    print(f"\n{'='*70}")
    print(f"­ƒôØ GENERAR EXAMEN POR BLOQUE")
    print(f"{'='*70}")
    
    archivos = datos.get("archivos", [])
    config = datos.get("config", {})
    
    num_multiple = config.get("num_multiple", 2)
    num_corta = config.get("num_corta", 1)
    num_vf = config.get("num_vf", 1)
    num_desarrollo = config.get("num_desarrollo", 1)
    
    print(f"­ƒôÜ Archivos en bloque: {len(archivos)}")
    print(f"­ƒôè Config: M={num_multiple}, C={num_corta}, VF={num_vf}, D={num_desarrollo}")
    
    if not archivos:
        raise HTTPException(status_code=400, detail="No se especificaron archivos")
    
    if generador_actual is None:
        raise HTTPException(status_code=500, detail="Modelo no inicializado")
    
    try:
        # ESTRATEGIA: Generar preguntas por archivo individualmente
        # Esto evita que el modelo se quede sin tokens con ex├ímenes grandes
        
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
                    print(f"  Ô£à Le├¡do: {nombre_archivo} ({len(contenido_texto)} chars)")
            except Exception as e:
                print(f"  ÔÜá´©Å  Error leyendo {archivo_obj}: {e}")
        
        if not archivos_contenido:
            raise HTTPException(status_code=404, detail="No se pudo leer el contenido de los archivos")
        
        # Calcular total de caracteres
        total_chars = sum(a['chars'] for a in archivos_contenido)
        print(f"­ƒôä Contenido total: {total_chars} caracteres en {len(archivos_contenido)} archivos")
        
        # Calcular distribuci├│n proporcional de preguntas por archivo
        total_preguntas = num_multiple + num_corta + num_vf + num_desarrollo
        
        print(f"\n­ƒÄ» Estrategia: Generar {total_preguntas} preguntas desde {len(archivos_contenido)} archivos")
        
        todas_preguntas = []
        
        for idx, archivo_info in enumerate(archivos_contenido, 1):
            # Calcular proporci├│n de preguntas para este archivo
            proporcion = archivo_info['chars'] / total_chars
            preguntas_este_archivo = max(3, round(total_preguntas * proporcion * 2.0))  # Generar 100% m├ís (x2)
            
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
            
            print(f"\n  ­ƒôØ Archivo {idx}/{len(archivos_contenido)}: {archivo_info['nombre']}")
            print(f"     Proporci├│n: {proporcion*100:.1f}% ({archivo_info['chars']} chars)")
            print(f"     Generando ~{sum(num_preguntas_archivo.values())} preguntas (variedad de tipos)")
            
            # Generar preguntas para este archivo
            contenido_formateado = f"=== {archivo_info['nombre']} ===\n{archivo_info['contenido']}"
            preguntas_archivo = generador_actual.generar_examen(contenido_formateado, num_preguntas_archivo)
            
            print(f"     Ô£à Obtenidas: {len(preguntas_archivo)} preguntas")
            todas_preguntas.extend(preguntas_archivo)
        
        # Mezclar todas las preguntas para variedad
        import random
        random.shuffle(todas_preguntas)
        
        print(f"\n­ƒôè Resumen de generaci├│n:")
        print(f"   Total obtenido: {len(todas_preguntas)} preguntas")
        print(f"   Total solicitado: {total_preguntas}")
        
        # Contar por tipo lo que tenemos
        contador_tipos = {}
        for p in todas_preguntas:
            tipo = p.tipo
            contador_tipos[tipo] = contador_tipos.get(tipo, 0) + 1
        
        print(f"   Distribuci├│n obtenida: {contador_tipos}")
        
        # Seleccionar las necesarias respetando proporci├│n solicitada
        preguntas_finales = []
        tipos_necesarios = {
            'mcq': num_multiple,
            'short_answer': num_corta,
            'true_false': num_vf,
            'open_question': num_desarrollo
        }
        
        # Separar por tipo con normalizaci├│n
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
                print(f"   ÔÜá´©Å  Tipo desconocido ignorado: '{p.tipo}' (no est├í en el mapeo)")
        
        print(f"\n­ƒôï Preguntas por tipo (normalizadas):")
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
                print(f"      ÔÜá´©Å  Faltan {cantidad - len(tomadas)} preguntas de tipo '{tipo}'")
        
        # Si a├║n faltan, completar con las que sobran
        if len(preguntas_finales) < total_preguntas:
            faltantes = total_preguntas - len(preguntas_finales)
            print(f"\n  ­ƒöä Completando {faltantes} preguntas faltantes...")
            
            # Tomar de las que sobraron
            usadas = set(id(p) for p in preguntas_finales)
            sobrantes = [p for p in todas_preguntas if id(p) not in usadas]
            random.shuffle(sobrantes)
            preguntas_finales.extend(sobrantes[:faltantes])
        
        # Mezclar resultado final
        random.shuffle(preguntas_finales)
        
        # Limitar al total solicitado
        preguntas = preguntas_finales[:total_preguntas]
        
        print(f"\nÔ£à Total final: {len(preguntas)} preguntas generadas")
        
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
    """Obtiene el ├írbol completo de carpetas y documentos"""
    try:
        arbol = cursos_db.obtener_arbol(ruta, max_depth=profundidad)
        return arbol
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/buscar")
async def buscar_documentos(q: str):
    """Busca documentos por nombre"""
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="La b├║squeda debe tener al menos 2 caracteres")
    
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
        print(f"­ƒôä Cargando: {nombre_archivo}")
        
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
        raise HTTPException(status_code=400, detail="La ruta no puede estar vac├¡a")
    
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
    print(f"­ƒöì DEBUG - Datos recibidos en /api/generar-examen:")
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
    print(f"­ƒôØ Solicitud de generaci├│n de examen (Session: {session_id})")
    print(f"­ƒôè Configuraci├│n de preguntas:")
    if num_multiple > 0:
        print(f"   ÔÇó Opci├│n m├║ltiple: {num_multiple}")
    if num_verdadero_falso > 0:
        print(f"   ÔÇó Verdadero/Falso: {num_verdadero_falso}")
    if num_corta > 0:
        print(f"   ÔÇó Corta: {num_corta}")
    if num_desarrollo > 0:
        print(f"   ÔÇó Desarrollo: {num_desarrollo}")
    print(f"\n­ƒÄ« Motor de IA:")
    if generador_actual and hasattr(generador_actual, 'usar_ollama') and generador_actual.usar_ollama:
        print(f"   Ô£à USANDO GPU - Ollama")
        print(f"   ­ƒÄ» Modelo: {generador_actual.modelo_ollama}")
        print(f"   ­ƒÆí GPU activada autom├íticamente")
    else:
        print(f"   ÔÜá´©Å  Usando llama-cpp-python")
    print(f"\nÔÜÖ´©Å Configuraci├│n del modelo:")
    print(f"   ÔÇó Temperatura: {ajustes.get('temperature', 0.7)}")
    print(f"   ÔÇó Tokens m├íximos: {ajustes.get('max_tokens', 512)}")
    print(f"   ÔÇó Contexto (n_ctx): {ajustes.get('n_ctx', 4096)} tokens")
    print(f"   ÔÇó Top P: 0.9")
    print(f"   ÔÇó Repetici├│n: 1.15")
    print(f"\n­ƒôä Longitud del contenido: {len(contenido) if contenido else 0} caracteres")
    if archivos:
        print(f"­ƒôÜ Archivos cargados en contexto ({len(archivos)}):")
        for i, archivo in enumerate(archivos, 1):
            print(f"   {i}. ­ƒôä {archivo}")
    if prompt_personalizado:
        print(f"­ƒÆ¼ Prompt personalizado: {prompt_personalizado[:100]}...")
    if prompt_sistema:
        print(f"­ƒÄ¿ Prompt sistema personalizado recibido: {len(prompt_sistema)} caracteres")
        print(f"   Primeros 100 caracteres: {prompt_sistema[:100]}...")
    else:
        print(f"­ƒôï Usando prompt del sistema predeterminado")
    print(f"{'='*60}\n")
    
    if not contenido:
        raise HTTPException(status_code=400, detail="Falta el contenido para generar el examen")
    
    # Inicializar progreso
    progreso_generacion[session_id] = {
        'progreso': 0,
        'mensaje': 'Iniciando generaci├│n...',
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
        print(f"­ƒôè Progreso {progreso}%: {mensaje}")
    
    try:
        # Recargar generador con la configuraci├│n actual
        callback_progreso(5, "Cargando modelo de IA...")
        config = cargar_config()
        modelo_ollama = config.get("modelo_ollama_activo", "llama31-local")
        usar_ollama = config.get("usar_ollama", True)
        modelo_path = config.get("modelo_path")
        gpu_layers = ajustes.get('n_gpu_layers', 35)
        
        print(f"­ƒôª Configuraci├│n actual:")
        print(f"   ÔÇó Usar Ollama: {usar_ollama}")
        if usar_ollama:
            print(f"   ÔÇó Modelo Ollama: {modelo_ollama}")
        else:
            print(f"   ÔÇó Modelo GGUF: {modelo_path}")
            print(f"   ÔÇó GPU Layers: {gpu_layers}")
        
        # Crear generador con la configuraci├│n actual
        if usar_ollama:
            print(f"­ƒöä Cargando modelo Ollama: {modelo_ollama}")
            generador_actual = GeneradorUnificado(
                usar_ollama=True,
                modelo_ollama=modelo_ollama,
                n_gpu_layers=gpu_layers
            )
        else:
            print(f"­ƒöä Cargando modelo GGUF: {modelo_path}")
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
        
        callback_progreso(10, "Preparando generaci├│n de preguntas...")
        print("­ƒñû Generando preguntas con IA en DOS PASOS...")
        preguntas = generador_actual.generar_examen(
            contenido, 
            num_preguntas,
            ajustes_modelo=ajustes,
            callback_progreso=callback_progreso,
            archivos=archivos,  # Pasar lista de archivos
            session_id=session_id  # Pasar session_id para el log
        )
        print(f"Ô£à Generadas {len(preguntas)} preguntas exitosamente")
        
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
        
        print(f"Ô£à Examen generado: {resultado['total_preguntas']} preguntas, {resultado['puntos_totales']} puntos totales\n")
        return resultado
        
    except Exception as e:
        import traceback
        print(f"\nÔØî ERROR generando examen:")
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
    """Endpoint SSE para streaming de progreso de generaci├│n de examen"""
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
                    
                    # Si est├í completado (exitoso o error), terminar stream
                    if progreso['completado']:
                        # Limpiar progreso despu├®s de 5 segundos
                        await asyncio.sleep(5)
                        if session_id in progreso_generacion:
                            del progreso_generacion[session_id]
                        break
                else:
                    # Si no existe la sesi├│n, enviar progreso inicial
                    data = json.dumps({
                        'progreso': 0,
                        'mensaje': 'Esperando inicio...',
                        'completado': False,
                        'error': None
                    })
                    yield f"data: {data}\n\n"
                
                # Esperar un poco antes de la siguiente actualizaci├│n
                await asyncio.sleep(0.5)
                
        except asyncio.CancelledError:
            # Cliente desconect├│
            print(f"­ƒöî Cliente desconectado del stream de progreso: {session_id}")
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
    """Eval├║a las respuestas de un examen"""
    global generador_unificado
    
    try:
        # Usar GeneradorUnificado (con GPU/CPU seg├║n configuraci├│n)
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
            # Validar que los datos requeridos est├®n presentes
            if not isinstance(datos, dict):
                raise HTTPException(status_code=400, detail="El cuerpo de la solicitud debe ser un diccionario JSON v├ílido.")

            preguntas_data = datos.get("preguntas")
            respuestas = datos.get("respuestas")
            carpeta_path = datos.get("carpeta_path", "")

            if not preguntas_data:
                raise HTTPException(status_code=400, detail="El campo 'preguntas' es obligatorio y no puede estar vac├¡o.")

            if not isinstance(respuestas, dict):
                raise HTTPException(status_code=400, detail="El campo 'respuestas' debe ser un diccionario.")

            # Validar que cada respuesta sea una cadena v├ílida
            for key, value in respuestas.items():
                if value is None:
                    respuestas[key] = ""
                elif not isinstance(value, str):
                    raise HTTPException(status_code=400, detail=f"La respuesta para la pregunta {key} debe ser una cadena de texto.")

            # Continuar con la l├│gica existente
            resultados = []
            puntos_obtenidos = 0
            puntos_totales = 0

            for i, pregunta_dict in enumerate(preguntas_data):
                pregunta = PreguntaExamen.from_dict(pregunta_dict)
                respuesta_usuario = respuestas.get(str(i), "")
                if respuesta_usuario is None:
                    respuesta_usuario = ""
                elif not isinstance(respuesta_usuario, str):
                    respuesta_usuario = str(respuesta_usuario)

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
                    "respuesta_correcta": pregunta.respuesta_correcta,
                    "puntos": puntos,
                    "puntos_maximos": pregunta.puntos,
                    "feedback": feedback
                })
            
            porcentaje = (puntos_obtenidos / puntos_totales * 100) if puntos_totales > 0 else 0
            
            # Guardar resultados SIEMPRE (con o sin carpeta)
            try:
                # Si no hay carpeta, usar carpeta por defecto
                if not carpeta_path:
                    carpeta_path = "Examenes_Generales"
                    carpeta_nombre = "Ex├ímenes Generales"
                    print(f"­ƒÆ¥ Guardando en carpeta por defecto: {carpeta_path}")
                else:
                    print(f"­ƒÆ¥ Guardando resultados para carpeta: {carpeta_path}")
                    carpeta = Path(carpeta_path)
                    if not carpeta.exists():
                        carpeta = Path("extracciones") / carpeta_path
                    carpeta_nombre = carpeta.name

                # Crear estructura en examenes/
                carpeta_examenes = Path("examenes") / carpeta_path
                carpeta_examenes.mkdir(parents=True, exist_ok=True)

                fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
                archivo_resultado = carpeta_examenes / f"examen_{fecha}.json"

                resultado_completo = {
                    "id": fecha,
                    "archivo": f"examen_{fecha}.json",
                    "fecha_completado": datetime.now().isoformat(),
                    "carpeta_ruta": carpeta_path,
                    "carpeta_nombre": carpeta_nombre,
                    "puntos_obtenidos": puntos_obtenidos,
                    "puntos_totales": puntos_totales,
                    "porcentaje": porcentaje,
                    "resultados": resultados,
                    "tipo": "completado"
                }

                with open(archivo_resultado, 'w', encoding='utf-8') as f:
                    json.dump(resultado_completo, f, ensure_ascii=False, indent=2)

                print(f"Ô£à Resultados guardados en: {archivo_resultado}")

                # Limpiar ex├ímenes en progreso de esta carpeta
                carpeta_progreso = carpeta_examenes / "examenes_progreso"
                if carpeta_progreso.exists():
                    for archivo in carpeta_progreso.glob("examen_progreso_*.json"):
                        archivo.unlink()
                        print(f"­ƒùæ´©Å Examen en progreso eliminado: {archivo.name}")
            except Exception as e:
                print(f"ÔØî Error guardando resultados: {e}")
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


@app.post("/api/examenes/pausar")
async def pausar_examen(datos: dict):
    """Guarda el progreso de un examen para continuarlo despu├®s"""
    try:
        carpeta_ruta = datos.get("carpeta_ruta") or "Examenes_Generales"
        carpeta_nombre = datos.get("carpeta_nombre") or "Ex├ímenes Generales"
        preguntas = datos.get("preguntas", [])
        respuestas = datos.get("respuestas", {})
        fecha_inicio = datos.get("fecha_inicio")
        
        print(f"ÔÅ©´©Å Pausando examen para carpeta: {carpeta_ruta}")
        
        # Crear estructura en examenes/
        carpeta_examenes_base = Path("examenes") / carpeta_ruta
        carpeta_examenes_base.mkdir(parents=True, exist_ok=True)
        
        carpeta_examenes = carpeta_examenes_base / "examenes_progreso"
        carpeta_examenes.mkdir(parents=True, exist_ok=True)
        
        print(f"   ­ƒôü Guardando en: {carpeta_examenes}")
        
        # IMPORTANTE: Eliminar ex├ímenes anteriores de esta misma carpeta
        # para evitar duplicados
        for archivo_anterior in carpeta_examenes.glob("examen_progreso_*.json"):
            try:
                archivo_anterior.unlink()
                print(f"­ƒùæ´©Å Examen anterior eliminado: {archivo_anterior.name}")
            except Exception as e:
                print(f"ÔÜá´©Å No se pudo eliminar {archivo_anterior.name}: {e}")
        
        # Crear archivo ├║nico para este examen en progreso
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_progreso = carpeta_examenes / f"examen_progreso_{fecha}.json"
        
        datos_progreso = {
            "id": fecha,
            "archivo": f"examen_progreso_{fecha}.json",
            "carpeta_ruta": carpeta_ruta,
            "carpeta_nombre": carpeta_nombre,
            "preguntas": preguntas,
            "respuestas": respuestas,
            "fecha_inicio": fecha_inicio,
            "fecha_pausa": datetime.now().isoformat(),
            "tipo": "en_progreso"
        }
        
        with open(archivo_progreso, 'w', encoding='utf-8') as f:
            json.dump(datos_progreso, f, ensure_ascii=False, indent=2)
        
        print(f"Ô£à Examen pausado guardado en: {archivo_progreso}")
        
        return {"success": True, "message": "Examen pausado correctamente"}
    except Exception as e:
        print(f"ÔØî Error pausando examen: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al pausar examen: {str(e)}")


@app.post("/api/examenes/guardar-temporal")
async def guardar_examen_temporal(datos: dict):
    """Guarda el examen en curso localmente para recuperarlo despu├®s"""
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
        
        print(f"­ƒÆ¥ Examen temporal guardado en: {archivo_temp}")
        
        return {"success": True, "message": "Guardado autom├ítico completado"}
    except Exception as e:
        print(f"ÔØî Error guardando examen temporal: {e}")
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
        
        print(f"­ƒôé Examen temporal cargado desde: {archivo_temp}")
        
        return {
            "success": True,
            "examen": datos
        }
    except Exception as e:
        print(f"ÔØî Error cargando examen temporal: {e}")
        return {"success": False, "message": str(e)}


@app.delete("/api/examenes/limpiar-temporal")
async def limpiar_examen_temporal():
    """Elimina el examen temporal"""
    try:
        archivo_temp = Path("temp_examenes/examen_en_curso.json")
        
        if archivo_temp.exists():
            archivo_temp.unlink()
            print(f"­ƒùæ´©Å Examen temporal eliminado")
        
        return {"success": True, "message": "Examen temporal eliminado"}
    except Exception as e:
        print(f"ÔØî Error eliminando examen temporal: {e}")
        return {"success": False, "message": str(e)}


@app.delete("/api/examenes/carpeta")
async def eliminar_carpeta_examenes(ruta: str, forzar: bool = False):
    """Elimina una carpeta de ex├ímenes (forzar=true elimina con contenido)"""
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
        print(f"­ƒùæ´©Å Carpeta de ex├ímenes eliminada: {ruta}")
        
        return {"success": True, "mensaje": "Carpeta eliminada"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"ÔØî Error eliminando carpeta de ex├ímenes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/examenes/examen")
async def eliminar_examen(ruta: str, archivo: str):
    """Elimina un examen espec├¡fico (completado o en progreso)"""
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
        print(f"­ƒùæ´©Å Examen eliminado: {archivo}")
        
        return {"success": True, "mensaje": "Examen eliminado"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"ÔØî Error eliminando examen: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/examenes/carpetas")
async def listar_carpetas_examenes(ruta: str = ""):
    """Lista carpetas y ex├ímenes en una ruta de examenes/ (estructura paralela)"""
    try:
        base_examenes = Path("examenes")
        
        # Construir ruta completa
        if ruta:
            ruta_completa = base_examenes / ruta
        else:
            ruta_completa = base_examenes
        
        if not ruta_completa.exists():
            raise HTTPException(status_code=404, detail="Ruta no encontrada")
        
        carpetas = []
        examenes_completados = []
        examenes_progreso = []
        examenes_progreso_global = []
        
        # Si estamos en la ra├¡z, buscar TODOS los ex├ímenes en progreso recursivamente
        if not ruta:
            print("­ƒôè Buscando todos los ex├ímenes en progreso...")
            for carpeta in base_examenes.rglob("*"):
                if carpeta.is_dir() and carpeta.name == "examenes_progreso":
                    for archivo in sorted(carpeta.glob("examen_progreso_*.json"), reverse=True):
                        try:
                            with open(archivo, 'r', encoding='utf-8') as f:
                                examen = json.load(f)
                                examenes_progreso_global.append(examen)
                        except Exception as e:
                            print(f"Error leyendo {archivo}: {e}")
            print(f"   Ô£à Encontrados {len(examenes_progreso_global)} ex├ímenes en progreso")
        
        # Listar carpetas
        for item in sorted(ruta_completa.iterdir()):
            if item.is_dir() and item.name != "examenes_progreso":
                # Contar ex├ímenes en la carpeta
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
        
        # Listar ex├ímenes completados en esta carpeta
        for archivo in sorted(ruta_completa.glob("examen_*.json"), reverse=True):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    examen = json.load(f)
                    if examen.get("tipo") == "completado":
                        examenes_completados.append(examen)
            except Exception as e:
                print(f"Error leyendo {archivo}: {e}")
        
        # Listar ex├ímenes en progreso en esta carpeta espec├¡fica (solo si no es ra├¡z)
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
            "examenes_progreso_global": examenes_progreso_global  # Solo lleno en ra├¡z
        }
    except Exception as e:
        print(f"Error listando carpetas de ex├ímenes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/examenes/listar")
async def listar_examenes():
    """Lista todos los ex├ímenes guardados (completados y en progreso) - DEPRECATED"""
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
                
                # Buscar ex├ímenes completados directamente en la carpeta
                for archivo in sorted(carpeta.glob("examen_*.json"), reverse=True):
                    try:
                        with open(archivo, 'r', encoding='utf-8') as f:
                            examen = json.load(f)
                            if examen.get("tipo") == "completado":
                                completados.append(examen)
                    except Exception as e:
                        print(f"Error leyendo examen completado {archivo}: {e}")
                
                # Buscar ex├ímenes en progreso
                carpeta_progreso = carpeta / "examenes_progreso"
                if carpeta_progreso.exists():
                    for archivo in sorted(carpeta_progreso.glob("examen_progreso_*.json"), reverse=True):
                        try:
                            with open(archivo, 'r', encoding='utf-8') as f:
                                examen = json.load(f)
                                en_progreso.append(examen)
                        except Exception as e:
                            print(f"Error leyendo examen en progreso {archivo}: {e}")
        
        print(f"­ƒôè Ex├ímenes encontrados: {len(completados)} completados, {len(en_progreso)} en progreso")
        
        return {
            "success": True,
            "completados": completados,
            "enProgreso": en_progreso
        }
    except Exception as e:
        print(f"Error listando ex├ímenes: {e}")
        raise HTTPException(status_code=500, detail=f"Error al listar ex├ímenes: {str(e)}")


# =============================
# TIMER SYNC ENDPOINTS
# =============================
from fastapi import Request
from fastapi.responses import JSONResponse
TIMER_SYNC_PATH = Path("timer_sync_state.json")

@app.get("/timer_sync")
def get_timer_sync():
    if TIMER_SYNC_PATH.exists():
        with open(TIMER_SYNC_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return JSONResponse(content=data)
    return JSONResponse(content={"timer": 0, "enPausa": False, "pausaRestante": 0, "ultimoUpdate": None})

@app.post("/timer_sync")
def set_timer_sync(request: Request):
    data = None
    try:
        data = asyncio.run(request.json())
    except Exception:
        return JSONResponse(content={"error": "JSON inv├ílido"}, status_code=400)
    if not isinstance(data, dict):
        return JSONResponse(content={"error": "Formato incorrecto"}, status_code=400)
    with open(TIMER_SYNC_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return JSONResponse(content={"ok": True, "data": data})





