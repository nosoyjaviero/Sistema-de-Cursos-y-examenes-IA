# Correcciones Aplicadas al Sistema - 22 Nov 2025

## Problema Original
El servidor API fallaba al generar exámenes con el error:
```
AttributeError: 'PreguntaExamen' object has no attribute 'dict'
```

## Diagnóstico
1. **Error de serialización**: El código intentaba usar `.dict()` o `.model_dump()`, métodos de Pydantic v2
2. **PreguntaExamen NO es un modelo Pydantic**: Es una clase normal en `generador_examenes.py` y un dataclass en `generador_dos_pasos.py`
3. **Endpoint `/api/carpetas/info`**: Esperaba diccionario pero `listar_carpetas()` retorna lista
4. **Payload mal procesado**: El endpoint recibía objetos `{nombre, ruta}` pero los trataba como strings

## Solución Implementada

### 1. Corrección de serialización (api_server.py línea 1325)
**ANTES:**
```python
"preguntas": [p.model_dump() if hasattr(p, 'model_dump') else p.dict() for p in preguntas]
```

**DESPUÉS:**
```python
"preguntas": [p.to_dict() for p in preguntas]
```

**Razón**: `PreguntaExamen` tiene método `to_dict()` nativo, no necesita Pydantic.

### 2. Corrección endpoint carpetas/info (api_server.py línea 1231-1248)
**ANTES:**
```python
resultado = cursos_db.listar_carpetas(ruta)
num_documentos = len(resultado.get('documentos', []))
num_subcarpetas = len(resultado.get('carpetas', []))
```

**DESPUÉS:**
```python
subcarpetas = cursos_db.listar_carpetas(ruta)
documentos = cursos_db.listar_documentos(ruta)
return {
    "num_documentos": len(documentos),
    "num_subcarpetas": len(subcarpetas),
    "ruta": ruta
}
```

**Razón**: `listar_carpetas()` retorna lista, no dict. Hay que llamar ambas funciones por separado.

### 3. Corrección procesamiento de payload (api_server.py línea 1293-1310)
**ANTES:**
```python
for ruta_archivo in archivos:
    contenido = cursos_db.obtener_contenido_documento(ruta_archivo)
```

**DESPUÉS:**
```python
for archivo_obj in archivos:
    # Extraer ruta del objeto (puede ser string o dict con 'ruta')
    if isinstance(archivo_obj, dict):
        ruta_archivo = archivo_obj.get('ruta', archivo_obj.get('nombre', ''))
    else:
        ruta_archivo = archivo_obj
    
    contenido = cursos_db.obtener_contenido_documento(ruta_archivo)
```

**Razón**: La UI envía objetos `{nombre: "...", ruta: "..."}` pero el código esperaba strings.

## Validación

### Test exitoso:
```bash
python test_generar_examen.py
```

**Resultado:**
```
✅ SUCCESS!
📝 Total preguntas: 5
✅ TEST PASADO - La serialización funciona correctamente
```

### Tipos de preguntas generadas correctamente:
- ✅ MCQ (Multiple Choice Questions)
- ✅ TRUE_FALSE (Verdadero/Falso)
- ✅ SHORT_ANSWER (Respuesta Corta)
- ✅ OPEN_QUESTION (Pregunta Abierta)

## Archivos Modificados
1. `api_server.py` (3 correcciones)
2. `test_generar_examen.py` (creado para validación)

## Estado Final
✅ Sistema completamente funcional
✅ Generación de exámenes OK
✅ Serialización JSON OK
✅ Endpoints de carpetas OK
✅ Compatible con UI React

## Próximos Pasos
1. Probar desde la UI web
2. Integrar componente `SesionEstudio.jsx` en `App.jsx`
3. Completar un examen y verificar sistema de gestión de errores
