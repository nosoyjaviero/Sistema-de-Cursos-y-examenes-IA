#!/usr/bin/env python3
"""
Script de prueba para verificar el toggle GPU/CPU y la funcionalidad del chatbot
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_motor_cambio(config_name, usar_ollama, modelo_ollama=None, modelo_gguf=None, n_gpu_layers=0):
    """Prueba cambiar el motor de IA"""
    print(f"\n{'='*70}")
    print(f"🧪 TEST: {config_name}")
    print(f"{'='*70}")
    
    # 1. Cambiar motor
    print(f"\n1️⃣  Cambiando motor...")
    payload = {
        "usar_ollama": usar_ollama,
        "n_gpu_layers": n_gpu_layers
    }
    if usar_ollama and modelo_ollama:
        payload["modelo_ollama"] = modelo_ollama
    if not usar_ollama and modelo_gguf:
        payload["modelo_gguf"] = modelo_gguf
    
    try:
        response = requests.post(f"{BASE_URL}/api/motor/cambiar", json=payload, timeout=5)
        result = response.json()
        if result.get("success"):
            print(f"✅ Motor cambiado: {result.get('mensaje')}")
            print(f"   GPU activa: {result['config'].get('gpu_activa')}")
            print(f"   Usar Ollama: {result['config'].get('usar_ollama')}")
        else:
            print(f"❌ Error: {result.get('detail')}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # 2. Esperar un poco para que se reinicialice el generador
    time.sleep(1)
    
    # 3. Obtener configuración
    print(f"\n2️⃣  Verificando configuración...")
    try:
        response = requests.get(f"{BASE_URL}/api/config", timeout=5)
        config = response.json()
        print(f"✅ Configuración actual:")
        print(f"   Usar Ollama: {config.get('usar_ollama')}")
        print(f"   GPU activa: {config.get('gpu_activa')}")
        print(f"   Modelo cargado: {config.get('modelo_cargado')}")
        print(f"   GPU layers: {config.get('n_gpu_layers')}")
    except Exception as e:
        print(f"❌ Error obteniendo configuración: {e}")
        return False
    
    # 4. Enviar un mensaje de chat
    print(f"\n3️⃣  Probando chat...")
    chat_message = "Hola, ¿eres un modelo de IA? Responde brevemente en una sola línea."
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "mensaje": chat_message,
                "historial": [],
                "contexto": None,
                "buscar_web": False,
                "ajustes": {
                    "temperature": 0.7,
                    "max_tokens": 100
                }
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            respuesta = result.get("respuesta", "").strip()
            if respuesta and not respuesta.startswith("❌"):
                print(f"✅ Chat funcionando")
                print(f"   Respuesta: {respuesta[:100]}...")
            else:
                print(f"❌ Error en chat: {respuesta}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión en chat: {e}")
        return False
    
    print(f"\n{'='*70}")
    print(f"✅ TEST COMPLETADO: {config_name}")
    print(f"{'='*70}")
    return True

def main():
    """Ejecuta todos los tests"""
    print("\n\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "🧪 PRUEBAS GPU/CPU TOGGLE" + " "*27 + "║")
    print("╚" + "="*68 + "╝")
    
    tests = [
        ("Ollama GPU", True, "qwen-local:latest", None, 35),
        ("Ollama CPU", True, "qwen-local:latest", None, 0),
    ]
    
    results = []
    for test_config in tests:
        result = test_motor_cambio(*test_config)
        results.append((test_config[0], result))
        time.sleep(2)  # Esperar entre tests
    
    # Resumen
    print("\n\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "📊 RESUMEN DE PRUEBAS" + " "*27 + "║")
    print("╠" + "="*68 + "╣")
    for test_name, result in results:
        status = "✅ EXITOSO" if result else "❌ FALLIDO"
        print(f"║ {test_name:.<30} {status:>33} ║")
    print("╚" + "="*68 + "╝\n")
    
    # Verificar si todos pasaron
    all_passed = all(r for _, r in results)
    if all_passed:
        print("🎉 ¡Todos los tests pasaron correctamente!")
    else:
        print("⚠️ Algunos tests fallaron. Revisa los logs arriba.")
    
    return all_passed

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
