#!/usr/bin/env python3
"""
Script de prueba simple para chatbot
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_chat_simple():
    """Prueba simple de chat"""
    print(f"\n{'='*70}")
    print(f"🧪 PRUEBA SIMPLE DE CHAT")
    print(f"{'='*70}\n")
    
    # 1. Obtener configuración actual
    print("1️⃣  Obteniendo configuración...")
    try:
        response = requests.get(f"{BASE_URL}/api/config", timeout=5)
        config = response.json()
        print(f"✅ Configuración actual:")
        print(f"   Usar Ollama: {config.get('usar_ollama')}")
        print(f"   GPU activa: {config.get('gpu_activa')}")
        print(f"   Modelo cargado: {config.get('modelo_cargado')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 2. Enviar chat
    print(f"\n2️⃣  Enviando mensaje...")
    message = "¿Hola? ¿Quién eres?"
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "mensaje": message,
                "historial": [],
                "contexto": None,
                "buscar_web": False,
                "ajustes": {
                    "temperature": 0.7,
                    "max_tokens": 100
                }
            },
            timeout=60
        )
        if response.status_code == 200:
            result = response.json()
            respuesta = result.get("respuesta", "").strip()
            print(f"✅ Respuesta recibida:")
            print(f"   '{respuesta[:150]}...'")
            return True
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(response.text[:200])
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_chat_simple()
    print(f"\n{'='*70}")
    if success:
        print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
    else:
        print("❌ PRUEBA FALLIDA")
    print(f"{'='*70}\n")
