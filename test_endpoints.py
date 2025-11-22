"""
🧪 Test de Endpoints del Sistema de Errores
============================================

Prueba rápida de los nuevos endpoints de la API.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("\n" + "=" * 70)
print("🧪 PROBANDO ENDPOINTS DEL SISTEMA DE ERRORES")
print("=" * 70 + "\n")

# Test 1: Estadísticas
print("1️⃣ Probando: GET /api/errores/estadisticas")
try:
    response = requests.get(f"{BASE_URL}/api/errores/estadisticas")
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✅ Funciona correctamente")
        print(f"   📊 Total errores: {stats.get('total_errores', 0)}")
        print(f"   📊 Activos: {stats.get('errores_activos', 0)}")
    else:
        print(f"   ❌ Error {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ❌ Servidor no está corriendo en puerto 8000")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 2: Sesión de estudio
print("2️⃣ Probando: GET /api/errores/sesion-estudio")
try:
    response = requests.get(f"{BASE_URL}/api/errores/sesion-estudio?max_errores=5")
    if response.status_code == 200:
        sesion = response.json()
        print(f"   ✅ Funciona correctamente")
        print(f"   🎯 Errores seleccionados: {sesion.get('total_errores_seleccionados', 0)}")
        print(f"   💬 {sesion.get('mensaje_motivacional', '')}")
    else:
        print(f"   ❌ Error {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ❌ Servidor no está corriendo")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 3: Buscar errores
print("3️⃣ Probando: GET /api/errores/buscar")
try:
    response = requests.get(f"{BASE_URL}/api/errores/buscar?tipo_pregunta=multiple")
    if response.status_code == 200:
        resultado = response.json()
        print(f"   ✅ Funciona correctamente")
        print(f"   🔍 Errores encontrados: {resultado.get('total', 0)}")
    else:
        print(f"   ❌ Error {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ❌ Servidor no está corriendo")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 4: Todos los errores
print("4️⃣ Probando: GET /api/errores/todos")
try:
    response = requests.get(f"{BASE_URL}/api/errores/todos")
    if response.status_code == 200:
        resultado = response.json()
        print(f"   ✅ Funciona correctamente")
        print(f"   📚 Total en banco: {resultado.get('total', 0)}")
    else:
        print(f"   ❌ Error {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ❌ Servidor no está corriendo")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("✅ PRUEBAS COMPLETADAS")
print("=" * 70)
print("\n💡 Si todos funcionan, el sistema está listo para usar en la UI.\n")
