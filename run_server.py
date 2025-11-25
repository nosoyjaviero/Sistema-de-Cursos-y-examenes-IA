#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para iniciar el servidor Examinator en modo producción
Permite que el servidor siga corriendo sin interrupciones
"""

import os
import sys
import subprocess
import signal

# Configurar UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

def signal_handler(sig, frame):
    print('\n✅ Servidor detenido correctamente')
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    print("="*60)
    print("🚀 Iniciando Examinator API Server...")
    print("="*60)
    print()
    
    cmd = [
        sys.executable,
        "-m", "uvicorn",
        "api_server:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--log-level", "info",
        "--timeout-keep-alive", "30",
        "--loop", "asyncio"
    ]
    
    try:
        proc = subprocess.run(cmd, cwd=os.getcwd())
        sys.exit(proc.returncode)
    except KeyboardInterrupt:
        print('\n✅ Servidor detenido')
        sys.exit(0)
