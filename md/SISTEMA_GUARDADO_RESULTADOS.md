# Sistema de Guardado de Resultados en Extracciones

## 📋 Resumen

Se implementó exitosamente el sistema de guardado de resultados de exámenes y prácticas calificadas directamente en las carpetas de `extracciones/` donde se generaron originalmente.

## 🎯 Objetivo

Cuando un usuario genera un examen o práctica desde una carpeta en `extracciones/`, los resultados calificados ahora se guardan automáticamente en la misma carpeta, manteniendo todo organizado en un solo lugar.

## 🔧 Cambios Realizados

### Archivo Modificado: `api_server.py`

#### 1. Endpoint `/api/evaluar-examen` (líneas ~2525-2550)

**Antes:**
- Los resultados se guardaban en `examenes/[carpeta]/` o `practicas/[carpeta]/`
- Separado de los archivos originales en `extracciones/`

**Ahora:**
- Los resultados se guardan en `extracciones/[carpeta]/resultados_examenes/` para exámenes
- Los resultados se guardan en `extracciones/[carpeta]/resultados_practicas/` para prácticas
- Todo queda en la misma carpeta donde se generó el contenido

#### 2. Endpoint `/api/examenes/pausar` (líneas ~2620-2640)

**Cambio:**
- Los exámenes pausados también se guardan en la carpeta correcta de `extracciones/`
- Se mantiene la compatibilidad con carpetas por defecto ("Examenes_Generales", "Practicas_Generales")

## 📁 Estructura de Carpetas

### Antes
```
extracciones/
├── Platzi/
│   ├── flashcards.json
│   └── notas.json
examenes/
└── Platzi/
    └── examen_20251125.json
```

### Ahora
```
extracciones/
└── Platzi/
    ├── flashcards.json
    ├── notas.json
    ├── resultados_examenes/
    │   └── examen_20251125_195843.json
    └── resultados_practicas/
        └── examen_20251125_195859.json
```

## ✅ Pruebas Realizadas

### Prueba 1: Examen en Carpeta Principal
- **Carpeta:** `Platzi`
- **Tipo:** Examen
- **Resultado:** ✅ Guardado en `extracciones/Platzi/resultados_examenes/`
- **Archivo:** `examen_20251125_195843.json`

### Prueba 2: Práctica en Carpeta Principal
- **Carpeta:** `Platzi`
- **Tipo:** Práctica
- **Resultado:** ✅ Guardado en `extracciones/Platzi/resultados_practicas/`
- **Archivo:** `examen_20251125_195859.json`

### Prueba 3: Práctica en Otra Carpeta
- **Carpeta:** `cursos`
- **Tipo:** Práctica
- **Resultado:** ✅ Guardado en `extracciones/cursos/resultados_practicas/`
- **Archivo:** `examen_20251125_195958.json`

### Prueba 4: Examen en Subcarpeta
- **Carpeta:** `Platzi/Diseño de Producto y UX`
- **Tipo:** Examen
- **Resultado:** ✅ Guardado en `extracciones/Platzi/Diseño de Producto y UX/resultados_examenes/`
- **Archivo:** `examen_20251125_200047.json`

## 📊 Formato de Archivo Guardado

```json
{
  "id": "20251125_195843",
  "archivo": "examen_20251125_195843.json",
  "fecha_completado": "2025-11-25T19:58:43.947236",
  "carpeta_ruta": "Platzi",
  "carpeta_nombre": "Platzi",
  "puntos_obtenidos": 25.0,
  "puntos_totales": 30,
  "porcentaje": 83.3333333333333,
  "resultados": [...],
  "tipo": "completado",
  "es_practica": false,
  "proximaRevision": "2025-11-26T19:58:43.947236",
  "ultimaRevision": "2025-11-25T19:58:43.947236",
  "intervalo": 1,
  "repeticiones": 0,
  "facilidad": 2.5,
  "estadoRevision": "nueva",
  "titulo": "Platzi"
}
```

## 🔄 Compatibilidad

El sistema mantiene compatibilidad con:
- ✅ Carpetas por defecto (`Examenes_Generales`, `Practicas_Generales`)
- ✅ Carpetas de `extracciones/` (nueva funcionalidad)
- ✅ Subcarpetas anidadas (ej: `Platzi/Diseño de Producto y UX`)
- ✅ Limpieza automática de exámenes en progreso al completar

## 🚀 Beneficios

1. **Organización:** Todo el contenido relacionado a una carpeta en un solo lugar
2. **Fácil Búsqueda:** Los resultados están junto a los archivos fuente
3. **Claridad:** Separación clara entre exámenes y prácticas
4. **Escalabilidad:** Funciona con cualquier nivel de anidación de carpetas

## 📝 Scripts de Prueba Creados

1. `test_guardar_resultados.py` - Prueba completa del sistema
2. `test_otra_carpeta.py` - Prueba con diferentes carpetas
3. `test_subcarpeta.py` - Prueba con subcarpetas anidadas

## ✨ Estado Final

**✅ IMPLEMENTACIÓN COMPLETADA Y VERIFICADA**

Todos los tests pasaron exitosamente. El sistema ahora guarda automáticamente los resultados de exámenes y prácticas en la carpeta `extracciones/` correspondiente.
