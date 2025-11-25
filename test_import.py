#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
os.chdir("C:\\Users\\Fela\\Documents\\Proyectos\\Examinator")

print("Cargando módulo api_server...")
import api_server

print("✅ Módulo cargado correctamente")
print(f"App: {api_server.app}")
print(f"Generador actual: {api_server.generador_actual}")
