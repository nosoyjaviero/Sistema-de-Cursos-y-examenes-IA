#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para actualizar índice
"""

import requests
import json

print("=" * 60)
print("🔄 TEST: Actualización de Índice")
print("=" * 60)

url = "http://localhost:5001/api/actualizar_indice"

print("\n1️⃣ Probando actualización incremental...")
try:
    response = requests.post(url, json={"completo": False}, timeout=60)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ Test completado")
print("=" * 60)
