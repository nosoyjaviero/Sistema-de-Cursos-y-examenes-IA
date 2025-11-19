# 📋 Guía Rápida de Logs de Prácticas

## 🎯 ¿Qué hace el sistema de logs?

Cada vez que generas una práctica, se crean automáticamente **2 archivos** con toda la información:
- `practica_YYYYMMDD_HHMMSS.log` → Archivo de texto legible
- `practica_YYYYMMDD_HHMMSS.json` → Datos estructurados en JSON

## 🚀 Comandos Rápidos

### Ver si la última práctica funcionó o falló
```powershell
.\check_ultimo.ps1
```
**Muestra:**
- ✅ EXITOSO o ❌ FALLÓ
- Número de preguntas solicitadas vs generadas
- Errores si los hay
- Info de filtrado

---

### Ver resumen de la última práctica
```powershell
.\ver_ultimo_log.ps1
```
**Muestra solo el resumen ejecutivo con:**
- Estado (exitoso/falló)
- Preguntas solicitadas vs generadas
- Errores encontrados
- Detalles del filtrado

---

### Ver log completo de la última práctica
```powershell
.\ver_ultimo_log.ps1 -Completo
```
**Muestra las 7 secciones completas:**
1. Request recibido
2. Prompt enviado al modelo
3. Respuesta del modelo
4. JSON extraído
5. Preguntas parseadas
6. Proceso de filtrado
7. Resultado final

---

### Listar todas las prácticas generadas
```powershell
.\listar_logs.ps1
```
**Muestra:**
- Últimos 10 logs (por defecto)
- ✅/❌ indicador de éxito/fallo
- Fecha, tamaño, número de preguntas
- Primeros errores si existen

Para ver más logs:
```powershell
.\listar_logs.ps1 -Ultimos 20
```

---

## 📊 Estructura del Log

### Resumen Ejecutivo (Inicio del archivo)
```
🎯 RESUMEN EJECUTIVO
--------------------------------------------------------------------------------
Estado: ✅ EXITOSO  o  ❌ FALLÓ
Fecha/Hora: 2025-11-19T14:30:52.123456
Preguntas solicitadas: 2
Preguntas generadas: 2

✅ Sin errores  o  ⚠️ ERRORES ENCONTRADOS:
  1. Descripción del error...
  2. Otro error...

Filtrado:
  • Total generadas: 2
  • Total filtradas: 2
  • Por tipo: {'true_false': 2}
```

### Secciones Detalladas (Resto del archivo)
1. **REQUEST RECIBIDO** - Qué pidió el frontend
2. **PROMPT ENVIADO** - Instrucciones exactas al modelo
3. **RESPUESTA DEL MODELO** - Output completo de Qwen/Ollama
4. **JSON EXTRAÍDO** - JSON parseado
5. **PREGUNTAS PARSEADAS** - Objetos Python creados
6. **PROCESO DE FILTRADO** - Cómo se filtraron las preguntas
7. **RESULTADO FINAL** - Qué se devolvió al frontend

---

## 🔍 Casos de Uso

### Caso 1: La práctica falló, quiero saber por qué
```powershell
.\check_ultimo.ps1
```
Te mostrará inmediatamente el error.

### Caso 2: Se generaron menos preguntas de las que pedí
```powershell
.\ver_ultimo_log.ps1
```
El resumen te mostrará cuántas se solicitaron vs cuántas se generaron y por qué.

### Caso 3: Quiero ver exactamente qué respondió el modelo
```powershell
.\ver_ultimo_log.ps1 -Completo
```
Ve a la sección "3. RESPUESTA COMPLETA DEL MODELO" para ver el output sin procesar.

### Caso 4: Quiero comparar varias ejecuciones
```powershell
.\listar_logs.ps1 -Ultimos 20
```
Te mostrará un listado con indicadores de éxito/fallo.

---

## 📂 Ubicación de los Logs

Todos los logs se guardan en:
```
logs_practicas_detallado/
  ├── practica_20251119_143052.log
  ├── practica_20251119_143052.json
  ├── practica_20251119_144521.log
  ├── practica_20251119_144521.json
  └── ...
```

**Nota:** Los logs NO se suben a Git (están en `.gitignore`)

---

## 💡 Tips

- Ejecuta `.\check_ultimo.ps1` después de cada generación para verificación rápida
- Usa `.\ver_ultimo_log.ps1` para diagnóstico rápido
- Solo usa `-Completo` cuando necesites investigar a fondo
- Los archivos `.json` son útiles para procesamiento automatizado
