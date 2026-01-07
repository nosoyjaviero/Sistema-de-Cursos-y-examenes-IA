# Examinator - Sistema de Gestión de Carpetas y Documentos

## 🚀 Inicio Rápido

### Servidores activos

- **Backend API**: http://localhost:8000
- **Frontend React**: http://localhost:5173

## 📁 Sistema de Carpetas

### Concepto Principal

**Tú creas la estructura de carpetas manualmente**, y el sistema simplemente navega y usa esa estructura. No hay base de datos - el sistema lee directamente del sistema de archivos.

### Cómo Funciona

1. **Página "Mis Carpetas"**: Navegador de archivos dentro de `extracciones/`
2. **Creas carpetas manualmente**: Con nombres que tú decides (ej: "Matemáticas", "Historia", "Semestre_1")
3. **Carpetas anidadas**: Puedes crear subcarpetas dentro de otras carpetas
4. **Sube PDFs**: Se guardan en la carpeta donde estás actualmente

### Ejemplo de Estructura

```
extracciones/
├── Matematicas/
│   ├── Algebra/
│   │   ├── ecuaciones.txt
│   │   └── funciones.txt
│   └── Calculo/
│       ├── limites.txt
│       └── derivadas.txt
├── Historia/
│   ├── Antigua/
│   └── Moderna/
└── Programacion/
    ├── Python/
    ├── JavaScript/
    └── proyecto_final.txt
```

## 🎯 Uso de la Aplicación

### 1. Página de Inicio

- **Subir PDF rápido**: Los documentos se guardan en la raíz de `extracciones/`
- **Botón "Organizar Carpetas"**: Te lleva al navegador de carpetas

### 2. Mis Carpetas (Navegador de Archivos)

#### Crear Carpeta
1. Click en "➕ Nueva Carpeta"
2. Ingresa el nombre (ej: "Matemáticas_2025")
3. La carpeta se crea en la ubicación actual

#### Subir PDF
1. Navega a la carpeta donde quieres guardar el documento
2. Click en "📤 Subir PDF aquí"
3. Selecciona tu PDF
4. El sistema automáticamente:
   - Extrae el texto usando `examinator.py`
   - Guarda el `.txt` en la carpeta actual
   - Muestra el documento en la lista

#### Navegar
- **Doble click en carpeta**: Entra a la carpeta
- **Breadcrumb (arriba)**: Click para volver a carpetas anteriores
- **Botón "🏠 Inicio"**: Vuelve a la raíz

#### Eliminar
- **Carpetas**: Solo se pueden eliminar si están vacías
- **Documentos**: Se eliminan directamente

### 3. Ventajas del Sistema

✅ **Simple**: No hay base de datos, solo archivos
✅ **Flexible**: Crea la estructura que necesites
✅ **Transparente**: Puedes ver los archivos en el explorador de Windows
✅ **Sin límites**: Crea todas las carpetas y subcarpetas que necesites
✅ **Manual**: Tú tienes control total de la organización

## 📊 Ejemplos de Uso

### Caso 1: Estudiante Universitario

```
extracciones/
├── Semestre_1/
│   ├── Calculo_I/
│   ├── Programacion_I/
│   └── Fisica_I/
├── Semestre_2/
│   ├── Calculo_II/
│   └── Programacion_II/
└── Proyectos/
    └── Tesis/
```

### Caso 2: Profesor con Múltiples Cursos

```
extracciones/
├── 2025_A/
│   ├── MAT101/
│   ├── MAT102/
│   └── MAT201/
├── 2025_B/
│   ├── MAT101/
│   └── MAT103/
└── Material_Extra/
```

### Caso 3: Preparación de Exámenes Profesionales

```
extracciones/
├── Medicina/
│   ├── Anatomia/
│   ├── Fisiologia/
│   └── Farmacologia/
├── Derecho/
│   ├── Civil/
│   └── Penal/
└── Repasos_Generales/
```

## 🛠️ Características Técnicas

### Backend (FastAPI)

**Nuevos Endpoints**:

```python
GET  /api/carpetas?ruta={ruta}          # Lista carpetas y documentos
POST /api/carpetas                      # Crea nueva carpeta
DELETE /api/carpetas?ruta={ruta}        # Elimina carpeta vacía
DELETE /api/documentos?ruta={ruta}      # Elimina documento
POST /api/extraer-pdf?carpeta={ruta}    # Sube PDF a carpeta específica
GET  /api/arbol?profundidad={n}         # Obtiene árbol de carpetas
GET  /api/buscar?q={query}              # Busca documentos
```

### Frontend (React)

**Componentes**:
- Navegador de carpetas con breadcrumb
- Vista de carpetas y documentos
- Upload contextual (sube a la carpeta actual)
- Acciones inline (eliminar, abrir)

## 🔧 API de Carpetas

### Listar Contenido

```bash
curl "http://localhost:8000/api/carpetas?ruta=Matematicas/Algebra"
```

Respuesta:
```json
{
  "ruta_actual": "Matematicas/Algebra",
  "carpetas": [
    {
      "nombre": "Ejercicios",
      "num_documentos": 5,
      "num_subcarpetas": 0
    }
  ],
  "documentos": [
    {
      "nombre": "ecuaciones_lineales",
      "tamaño_kb": 45.3,
      "fecha_modificacion": "2025-11-16T..."
    }
  ]
}
```

### Crear Carpeta

```bash
curl -X POST "http://localhost:8000/api/carpetas" \
  -H "Content-Type: application/json" \
  -d '{"ruta_padre": "Matematicas", "nombre": "Geometria"}'
```

### Subir PDF

```bash
curl -X POST "http://localhost:8000/api/extraer-pdf" \
  -F "file=@documento.pdf" \
  -F "carpeta=Matematicas/Algebra"
```

## 💡 Tips y Trucos

### 1. Organización Recomendada

**Por materia/curso**:
```
extracciones/
├── NombreCurso/
│   ├── Unidad_1/
│   ├── Unidad_2/
│   └── Examenes_Anteriores/
```

### 2. Nombres de Carpetas

✅ **Recomendado**:
- `Matematicas_Avanzadas`
- `Historia_Universal_2025`
- `Proyecto_Final`

❌ **Evitar**:
- Espacios múltiples
- Caracteres especiales: `<>:"/\|?*`
- Nombres muy largos

### 3. Workflow Típico

1. Crear carpeta principal para el curso
2. Crear subcarpetas por temas/unidades
3. Subir PDFs a cada carpeta según corresponda
4. Generar exámenes desde documentos específicos

## 🐛 Solución de Problemas

### "La carpeta no se puede eliminar"
- La carpeta no está vacía
- Elimina primero los documentos y subcarpetas

### "No veo mis carpetas"
- Verifica que estén en `extracciones/`
- Actualiza la página (F5)

### "Error al subir PDF"
- Verifica que sea un PDF válido
- Revisa permisos de escritura

## 📝 Notas Importantes

- Los archivos `.txt` extraídos tienen el mismo nombre que el PDF original
- Las carpetas `resultados/` se ignoran automáticamente
- Puedes organizar manualmente desde el explorador de Windows
- Los cambios manuales en el sistema de archivos se reflejan inmediatamente
