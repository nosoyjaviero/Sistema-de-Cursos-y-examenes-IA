#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de arranque del servidor
"""
import sys

print("="*60)
print("TEST: Iniciando servidor...")
print("="*60)

try:
    print("\n1. Importando módulos...")
    from api_buscador import app, inicializar_sistema
    print("✅ Módulos importados")
    
    print("\n2. Inicializando sistema...")
    inicializar_sistema()
    print("✅ Sistema inicializado")
    
    print("\n3. Iniciando Flask...")
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)
