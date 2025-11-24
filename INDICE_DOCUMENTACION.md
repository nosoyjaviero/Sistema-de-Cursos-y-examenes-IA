# 📖 ÍNDICE DE DOCUMENTACIÓN

> Guía rápida para encontrar la información que necesitas

---

## 🚀 Inicio Rápido (3 Pasos)

```powershell
# 1. Instalar
.\INSTALACION_COMPLETA.ps1

# 2. Verificar
.\VERIFICAR_ENTORNO.ps1

# 3. Iniciar
.\INICIAR_BUSCADOR_TODO.ps1
```

**¿Problemas?** → Ver sección "🆘 Solución de Problemas" abajo

---

## 📚 Documentación por Categoría

### 🎯 Para Usuarios Nuevos

| Documento | Propósito | Leer si... |
|-----------|-----------|------------|
| **[README_INSTALACION.md](README_INSTALACION.md)** | Punto de entrada principal | Es tu primera vez con el proyecto |
| **[CHECKLIST_INSTALACION.md](CHECKLIST_INSTALACION.md)** | Lista de verificación paso a paso | Quieres asegurar que todo está bien |
| **[GUIA_INSTALACION.md](GUIA_INSTALACION.md)** | Instalación detallada | Prefieres instrucciones paso a paso |

### 🔧 Para Solucionar Problemas

| Documento | Propósito | Leer si... |
|-----------|-----------|------------|
| **[SOLUCIONES_PROBLEMAS.md](SOLUCIONES_PROBLEMAS.md)** | Errores comunes y fixes | Algo no funciona |
| **Script: VERIFICAR_ENTORNO.ps1** | Diagnóstico automático | Quieres saber qué está mal |
| **[RESUMEN_CONFIGURACION.md](RESUMEN_CONFIGURACION.md)** | Resumen de todos los cambios | Necesitas contexto general |

### 💻 Para Desarrolladores

| Documento | Propósito | Leer si... |
|-----------|-----------|------------|
| **[ARQUITECTURA_BUSQUEDA.md](ARQUITECTURA_BUSQUEDA.md)** | Cómo funciona el sistema | Quieres entender el código |
| **[requirements.txt](requirements.txt)** | Dependencias Python | Necesitas saber qué se usa |
| **[RESUMEN_CONFIGURACION.md](RESUMEN_CONFIGURACION.md)** | Problemas resueltos | Quieres saber qué se arregló |

---

## 🆘 Solución de Problemas

### Por Síntoma

| Problema | Ver | Solución Rápida |
|----------|-----|-----------------|
| **GPU no detectada** | [SOLUCIONES_PROBLEMAS.md](SOLUCIONES_PROBLEMAS.md) → GPU/CUDA | `pip uninstall torch; pip install torch --index-url https://download.pytorch.org/whl/cu118` |
| **Servidor se cierra** | [SOLUCIONES_PROBLEMAS.md](SOLUCIONES_PROBLEMAS.md) → Servidor | Usar `INICIAR_BUSCADOR_GPU.bat` |
| **Puerto ocupado** | [SOLUCIONES_PROBLEMAS.md](SOLUCIONES_PROBLEMAS.md) → Servidor | `.\INICIAR_BUSCADOR_TODO.ps1` (auto-libera) |
| **Dependencias faltantes** | [GUIA_INSTALACION.md](GUIA_INSTALACION.md) → Instalación | `.\INSTALACION_COMPLETA.ps1` |
| **Frontend no conecta** | [SOLUCIONES_PROBLEMAS.md](SOLUCIONES_PROBLEMAS.md) → Frontend | Verificar `http://localhost:5001/api/estado` |
| **Búsqueda lenta** | [SOLUCIONES_PROBLEMAS.md](SOLUCIONES_PROBLEMAS.md) → Rendimiento | Verificar que GPU esté activa |

### Por Etapa

| Etapa | Problema | Documento |
|-------|----------|-----------|
| **Instalación** | Error al instalar | [GUIA_INSTALACION.md](GUIA_INSTALACION.md) |
| **Verificación** | Checks fallan | [CHECKLIST_INSTALACION.md](CHECKLIST_INSTALACION.md) |
| **Inicio** | No arranca | [SOLUCIONES_PROBLEMAS.md](SOLUCIONES_PROBLEMAS.md) |
| **Uso** | No funciona bien | [SOLUCIONES_PROBLEMAS.md](SOLUCIONES_PROBLEMAS.md) |

---

## 🎯 Por Tarea

### "Quiero instalar el proyecto"

1. Lee: [README_INSTALACION.md](README_INSTALACION.md) (5 min)
2. Ejecuta: `.\INSTALACION_COMPLETA.ps1` (15 min)
3. Verifica: `.\VERIFICAR_ENTORNO.ps1` (1 min)
4. Inicia: `.\INICIAR_BUSCADOR_TODO.ps1` (30 seg)

### "Algo no funciona"

1. Ejecuta: `.\VERIFICAR_ENTORNO.ps1`
2. Lee: [SOLUCIONES_PROBLEMAS.md](SOLUCIONES_PROBLEMAS.md)
3. Busca tu error específico
4. Aplica solución
5. Si falla, reinstala: `.\INSTALACION_COMPLETA.ps1`

### "Quiero entender cómo funciona"

1. Lee: [ARQUITECTURA_BUSQUEDA.md](ARQUITECTURA_BUSQUEDA.md) (15 min)
2. Revisa: [requirements.txt](requirements.txt) (2 min)
3. Explora código: `buscador_ia.py`, `api_buscador.py`

### "Voy a reinstalar en otra máquina"

1. Lee: [CHECKLIST_INSTALACION.md](CHECKLIST_INSTALACION.md)
2. Ejecuta: `.\INSTALACION_COMPLETA.ps1`
3. Sigue checklist paso a paso
4. Marca cada ✓

---

## 📂 Archivos por Tipo

### Scripts Ejecutables (.ps1, .bat)

```powershell
INSTALACION_COMPLETA.ps1      # Instalar todo
VERIFICAR_ENTORNO.ps1         # Verificar instalación
INICIAR_BUSCADOR_TODO.ps1     # Iniciar sistema completo
INICIAR_BUSCADOR_GPU.bat      # Solo backend
DETENER_BUSCADOR.ps1          # Detener todo
```

### Documentación (.md)

```
README_INSTALACION.md         # Punto de entrada
GUIA_INSTALACION.md          # Instalación detallada
SOLUCIONES_PROBLEMAS.md      # Debugging
ARQUITECTURA_BUSQUEDA.md     # Documentación técnica
CHECKLIST_INSTALACION.md     # Lista de verificación
RESUMEN_CONFIGURACION.md     # Resumen de cambios
INDICE_DOCUMENTACION.md      # Este archivo
```

### Configuración

```
requirements.txt              # Dependencias Python
.gitignore                   # Git ignore rules
```

---

## 🔍 Búsqueda Rápida

### Por Palabra Clave

| Busco... | Ver Documento |
|----------|---------------|
| **GPU** | [SOLUCIONES_PROBLEMAS.md](SOLUCIONES_PROBLEMAS.md) → GPU/CUDA |
| **CUDA** | [GUIA_INSTALACION.md](GUIA_INSTALACION.md) → PyTorch |
| **Puerto** | [SOLUCIONES_PROBLEMAS.md](SOLUCIONES_PROBLEMAS.md) → Servidor |
| **PyTorch** | [requirements.txt](requirements.txt) + [GUIA_INSTALACION.md](GUIA_INSTALACION.md) |
| **FAISS** | [ARQUITECTURA_BUSQUEDA.md](ARQUITECTURA_BUSQUEDA.md) |
| **Embeddings** | [ARQUITECTURA_BUSQUEDA.md](ARQUITECTURA_BUSQUEDA.md) |
| **BM25** | [ARQUITECTURA_BUSQUEDA.md](ARQUITECTURA_BUSQUEDA.md) |
| **Waitress** | [SOLUCIONES_PROBLEMAS.md](SOLUCIONES_PROBLEMAS.md) → Servidor |
| **Flask** | [ARQUITECTURA_BUSQUEDA.md](ARQUITECTURA_BUSQUEDA.md) |
| **React** | [ARQUITECTURA_BUSQUEDA.md](ARQUITECTURA_BUSQUEDA.md) |

### Por Comando

| Comando | Para Qué | Documentado En |
|---------|----------|----------------|
| `.\INSTALACION_COMPLETA.ps1` | Instalar todo | [GUIA_INSTALACION.md](GUIA_INSTALACION.md) |
| `.\VERIFICAR_ENTORNO.ps1` | Verificar instalación | [CHECKLIST_INSTALACION.md](CHECKLIST_INSTALACION.md) |
| `.\INICIAR_BUSCADOR_TODO.ps1` | Iniciar sistema | [README_INSTALACION.md](README_INSTALACION.md) |
| `.\DETENER_BUSCADOR.ps1` | Detener sistema | [README_INSTALACION.md](README_INSTALACION.md) |
| `pip install torch --index-url ...` | Instalar PyTorch CUDA | [SOLUCIONES_PROBLEMAS.md](SOLUCIONES_PROBLEMAS.md) |
| `python crear_indice_inicial.py` | Crear índice | [GUIA_INSTALACION.md](GUIA_INSTALACION.md) |

---

## 📊 Matriz de Decisión

### "¿Qué documento necesito?"

```
¿Es tu primera vez?
├─ Sí → README_INSTALACION.md
└─ No
   │
   ¿Tienes un problema?
   ├─ Sí
   │  ├─ Error específico → SOLUCIONES_PROBLEMAS.md
   │  ├─ No sé qué está mal → VERIFICAR_ENTORNO.ps1
   │  └─ Quiero reinstalar → INSTALACION_COMPLETA.ps1
   │
   └─ No
      │
      ¿Qué quieres hacer?
      ├─ Entender cómo funciona → ARQUITECTURA_BUSQUEDA.md
      ├─ Verificar instalación → CHECKLIST_INSTALACION.md
      ├─ Ver qué cambió → RESUMEN_CONFIGURACION.md
      └─ Instalar en nueva máquina → GUIA_INSTALACION.md
```

---

## 🎓 Orden de Lectura Recomendado

### Para Usuarios Nuevos

1. **[README_INSTALACION.md](README_INSTALACION.md)** (5 min) - Visión general
2. **[GUIA_INSTALACION.md](GUIA_INSTALACION.md)** (10 min) - Instalación paso a paso
3. **[CHECKLIST_INSTALACION.md](CHECKLIST_INSTALACION.md)** (5 min) - Verificación
4. **[SOLUCIONES_PROBLEMAS.md](SOLUCIONES_PROBLEMAS.md)** (referencia) - Para cuando falle algo

### Para Desarrolladores

1. **[README_INSTALACION.md](README_INSTALACION.md)** (5 min) - Contexto
2. **[ARQUITECTURA_BUSQUEDA.md](ARQUITECTURA_BUSQUEDA.md)** (20 min) - Cómo funciona
3. **[RESUMEN_CONFIGURACION.md](RESUMEN_CONFIGURACION.md)** (10 min) - Qué se arregló
4. **Código fuente** - `buscador_ia.py`, `api_buscador.py`, `App.jsx`

### Para Reinstalación

1. **[CHECKLIST_INSTALACION.md](CHECKLIST_INSTALACION.md)** - Guía principal
2. Ejecutar `.\INSTALACION_COMPLETA.ps1`
3. Ejecutar `.\VERIFICAR_ENTORNO.ps1`
4. Marcar cada ✓ en checklist

---

## 💡 Consejos de Navegación

### Atajos Rápidos

| Necesito... | Ir a... |
|-------------|---------|
| **Instalar ya** | `.\INSTALACION_COMPLETA.ps1` |
| **Ver si funciona** | `.\VERIFICAR_ENTORNO.ps1` |
| **Arreglar error** | [SOLUCIONES_PROBLEMAS.md](SOLUCIONES_PROBLEMAS.md) |
| **Entender código** | [ARQUITECTURA_BUSQUEDA.md](ARQUITECTURA_BUSQUEDA.md) |

### Documentos Más Útiles

🥇 **[SOLUCIONES_PROBLEMAS.md](SOLUCIONES_PROBLEMAS.md)** - El más consultado  
🥈 **[README_INSTALACION.md](README_INSTALACION.md)** - Punto de entrada  
🥉 **[ARQUITECTURA_BUSQUEDA.md](ARQUITECTURA_BUSQUEDA.md)** - Para entender  

---

## 📞 Flujo de Soporte

```
Tengo un problema
       ↓
¿Ya leíste SOLUCIONES_PROBLEMAS.md?
       ↓ No
   Léelo primero
       ↓
¿Encontraste tu error?
   ↓ Sí                    ↓ No
Aplicar solución     Ejecutar VERIFICAR_ENTORNO.ps1
       ↓                          ↓
¿Funciona?              Ver qué falla
   ↓ No                          ↓
Reinstalar         Buscar error específico en docs
```

---

## ✅ Verificación Final

### Antes de Usar el Sistema

- [ ] He leído [README_INSTALACION.md](README_INSTALACION.md)
- [ ] He ejecutado `.\INSTALACION_COMPLETA.ps1`
- [ ] He ejecutado `.\VERIFICAR_ENTORNO.ps1` → Todo ✓
- [ ] Sé dónde está [SOLUCIONES_PROBLEMAS.md](SOLUCIONES_PROBLEMAS.md)
- [ ] Sistema funciona: `.\INICIAR_BUSCADOR_TODO.ps1`

---

**Última actualización:** 23 de noviembre de 2025  
**Versión:** 2.0 (con búsqueda IA + GPU)

---

*Este índice te ayuda a encontrar rápidamente la información que necesitas*
