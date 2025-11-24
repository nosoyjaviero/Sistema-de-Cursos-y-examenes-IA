# Endpoints adicionales para gestión de datos persistentes
# Agregar al final de api_server.py antes del arranque del servidor

from fastapi import Request
from fastapi.responses import JSONResponse

# =============================
# GESTIÓN DE DATOS PERSISTENTES (NOTAS, FLASHCARDS, PRÁCTICAS)
# =============================
EXTRACCIONES_PATH = Path("extracciones")

@app.get("/datos/{tipo}")
def get_datos(tipo: str):
    """Lee notas, flashcards o prácticas desde archivos JSON"""
    try:
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
