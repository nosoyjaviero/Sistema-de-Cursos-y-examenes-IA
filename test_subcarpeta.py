"""
Prueba con subcarpeta: extracciones/Platzi/Diseño de Producto y UX
"""
import requests
import json
from pathlib import Path

API_URL = "http://localhost:8000"

# Prueba con subcarpeta
carpeta_test = "Platzi/Diseño de Producto y UX"

preguntas = [
    {
        "id": 1,
        "tipo": "corta",
        "pregunta": "¿Qué es UX?",
        "respuesta_correcta": "User Experience",
        "puntos": 20,
        "metadata": {}
    }
]

respuestas = {
    "0": "User Experience"
}

print(f"🧪 Probando con subcarpeta: {carpeta_test}")

response = requests.post(
    f"{API_URL}/api/evaluar-examen",
    json={
        "preguntas": preguntas,
        "respuestas": respuestas,
        "carpeta_path": carpeta_test,
        "es_practica": False
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Calificado exitosamente: {data['puntos_obtenidos']}/{data['puntos_totales']}")
    
    # Verificar archivo
    ruta = Path("extracciones") / carpeta_test / "resultados_examenes"
    print(f"📁 Verificando: {ruta}")
    if ruta.exists():
        archivos = list(ruta.glob("*.json"))
        print(f"✅ Se creó la carpeta y archivos:")
        for archivo in archivos:
            print(f"   - {archivo}")
            # Leer contenido
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = json.load(f)
                print(f"     Carpeta: {contenido.get('carpeta_nombre')}")
                print(f"     Ruta: {contenido.get('carpeta_ruta')}")
    else:
        print(f"❌ No existe: {ruta}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
