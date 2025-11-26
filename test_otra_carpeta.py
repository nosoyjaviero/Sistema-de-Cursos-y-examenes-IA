"""
Prueba adicional: verificar que funciona con diferentes carpetas
"""
import requests
import json

API_URL = "http://localhost:8000"

# Prueba con carpeta "cursos"
carpeta_test = "cursos"

preguntas = [
    {
        "id": 1,
        "tipo": "multiple",
        "pregunta": "¿Qué es una función?",
        "opciones": ["Un procedimiento", "Una variable", "Un bucle", "Un comentario"],
        "respuesta_correcta": "Un procedimiento",
        "puntos": 10,
        "metadata": {}
    }
]

respuestas = {
    "0": "Un procedimiento"
}

print(f"🧪 Probando con carpeta: {carpeta_test}")

response = requests.post(
    f"{API_URL}/api/evaluar-examen",
    json={
        "preguntas": preguntas,
        "respuestas": respuestas,
        "carpeta_path": carpeta_test,
        "es_practica": True
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Calificado exitosamente: {data['puntos_obtenidos']}/{data['puntos_totales']}")
    
    # Verificar archivo
    from pathlib import Path
    ruta = Path("extracciones") / carpeta_test / "resultados_practicas"
    if ruta.exists():
        archivos = list(ruta.glob("*.json"))
        print(f"✅ Archivos en {ruta}:")
        for archivo in archivos:
            print(f"   - {archivo.name}")
    else:
        print(f"❌ No existe: {ruta}")
else:
    print(f"❌ Error: {response.status_code}")
