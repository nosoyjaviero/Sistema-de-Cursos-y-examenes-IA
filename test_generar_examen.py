"""
Test de generación de examen para verificar que to_dict() funciona
"""
import requests
import json

# Configuración
API_URL = "http://localhost:8000/api/generar_examen_bloque"

# Payload de prueba - usando archivo real que existe
payload = {
    "archivos": [
        {
            "nombre": "Resumen_251116_083114",
            "ruta": "Platzi/Diseño de Producto y UX/Resumen_251116_083114.txt"
        }
    ],
    "num_mcq": 3,
    "num_short_answer": 1,
    "num_true_false": 2,
    "num_open_question": 1
}

print("=" * 70)
print("🧪 TEST: Generación de Examen")
print("=" * 70)
print(f"📡 Endpoint: {API_URL}")
print(f"📊 Config: {payload['num_mcq']} MCQ, {payload['num_short_answer']} SA, {payload['num_true_false']} TF, {payload['num_open_question']} OQ")
print(f"📁 Archivo: {payload['archivos'][0]['ruta']}")
print()

try:
    print("🚀 Enviando request...")
    response = requests.post(API_URL, json=payload, timeout=600)
    
    print(f"📬 Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS!")
        print(f"📝 Total preguntas: {data.get('total', 0)}")
        print()
        
        # Mostrar primeras 3 preguntas
        preguntas = data.get('preguntas', [])
        for i, p in enumerate(preguntas[:3], 1):
            print(f"  {i}. [{p.get('tipo', 'N/A').upper()}] {p.get('pregunta', 'N/A')[:60]}...")
        
        if len(preguntas) > 3:
            print(f"  ... (+{len(preguntas) - 3} más)")
        
        print()
        print("=" * 70)
        print("✅ TEST PASADO - La serialización funciona correctamente")
        print("=" * 70)
        
    else:
        print(f"❌ ERROR {response.status_code}")
        print(f"📄 Response: {response.text[:500]}")
        
except requests.Timeout:
    print("⏱️ TIMEOUT - El servidor tardó más de 10 minutos")
except requests.ConnectionError:
    print("❌ ERROR DE CONEXIÓN - ¿Está corriendo el servidor?")
except Exception as e:
    print(f"❌ ERROR: {e}")
