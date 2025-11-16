# Funcionalidad de Reintentar Exámenes y Ver Respuestas Correctas

## 📋 Resumen

Esta actualización implementa dos características principales solicitadas:

1. **Opción de reintentar exámenes completados**: Los usuarios pueden volver a tomar cualquier examen previamente completado con las mismas preguntas.
2. **Visualización de respuestas correctas**: Se muestran las respuestas correctas/modelo para preguntas de "respuesta breve" y "desarrollo".

## 🎯 Características Implementadas

### 1. Generar Examen
- Selecciona cualquier documento de "Mis Cursos" haciendo clic en el icono 📝
- Configura la cantidad de preguntas:
  - **Opción Múltiple**: 4 opciones (A, B, C, D)
  - **Respuesta Corta**: 2-4 líneas
  - **Desarrollo**: Análisis profundo
- Genera examen con inteligencia artificial

### 2. Tomar Examen
- Interfaz intuitiva para responder cada pregunta
- Soporte para todos los tipos de preguntas:
  - Radio buttons para opción múltiple
  - Textarea para respuestas cortas
  - Textarea extendida para preguntas de desarrollo
- Botón "Evaluar Examen" al completar

### 3. Ver Resultados
- **Calificación general**: Porcentaje, puntos obtenidos/totales
- **Desglose por pregunta**:
  - Puntos obtenidos vs máximos
  - Retroalimentación de la IA
  - **Respuestas correctas visibles** para todos los tipos de pregunta
  - Para preguntas de respuesta corta y desarrollo:
    - Se muestra la "respuesta modelo" o criterios de evaluación
    - Se compara con la respuesta del estudiante
    - Feedback detallado sobre qué mejorar

### 4. Historial de Exámenes
- Lista completa de todos los exámenes completados
- Información mostrada:
  - Documento del examen
  - Fecha y hora
  - Calificación (% y puntos)
  - Número de preguntas
- Acciones disponibles:
  - 👁️ **Ver**: Muestra los resultados con respuestas correctas
  - 🔄 **Reintentar**: Carga el mismo examen para intentarlo de nuevo
  - 🗑️ **Eliminar**: Borra el resultado del historial

## 🔄 Flujo de Uso: Reintentar Examen

1. Ve a la sección "📋 Historial"
2. Encuentra el examen que quieres reintentar
3. Haz clic en el botón "🔄 Reintentar"
4. El sistema carga las mismas preguntas del examen original
5. Responde nuevamente las preguntas
6. Evalúa el examen
7. Compara tu nuevo resultado con el anterior

## 📝 Visualización de Respuestas Correctas

### Para Preguntas de Opción Múltiple
- ✓ marca verde en la opción correcta
- ✗ marca roja en la opción seleccionada si es incorrecta

### Para Preguntas de Respuesta Corta
- Se muestra la "Respuesta modelo" con el texto esperado
- Feedback de la IA sobre qué incluir o mejorar
- Comparación lado a lado con tu respuesta

### Para Preguntas de Desarrollo
- Se muestran los "Criterios de evaluación"
- Qué puntos debía mencionar la respuesta
- Análisis detallado de la calidad de tu respuesta
- Sugerencias de mejora

## 🛠️ Implementación Técnica

### Backend (api_server.py)

#### Nuevos Endpoints

1. **GET `/api/examenes/resultados`**
   - Lista todos los exámenes completados
   - Puede filtrar por documento específico
   - Retorna: id, fecha, documento, puntos, porcentaje, num_preguntas

2. **GET `/api/examenes/resultado/{resultado_id}`**
   - Obtiene los detalles completos de un resultado
   - Incluye todas las preguntas originales para retry
   - Incluye respuestas correctas para todas las preguntas

3. **DELETE `/api/examenes/resultado/{resultado_id}`**
   - Elimina un resultado del historial

#### Modificación al Endpoint de Evaluación

**POST `/api/evaluar-examen`** - Actualizado para:
- Guardar las preguntas completas del examen (`preguntas` array)
- Incluir `respuesta_correcta` en cada resultado
- Retornar `resultado_id` para referencia futura

### Frontend (App.jsx)

#### Nuevo Estado
```javascript
const [examenGenerado, setExamenGenerado] = useState(null)
const [respuestasExamen, setRespuestasExamen] = useState({})
const [resultadoExamen, setResultadoExamen] = useState(null)
const [historialExamenes, setHistorialExamenes] = useState([])
const [mostrandoRespuestas, setMostrandoRespuestas] = useState(false)
```

#### Funciones Principales

1. **`generarExamen()`**: Genera un nuevo examen desde un documento
2. **`evaluarExamen()`**: Evalúa las respuestas y guarda resultado
3. **`verResultadoExamen(id, path)`**: Muestra resultados con respuestas correctas
4. **`reintentarExamen(id, path)`**: Carga preguntas para reintentar
5. **`eliminarResultadoExamen(id, path)`**: Elimina resultado del historial

### Estructura de Datos del Resultado

```json
{
  "id": "20250116_120000",
  "fecha": "2025-01-16T12:00:00",
  "documento": "extracciones/curso/documento.txt",
  "puntos_obtenidos": 7,
  "puntos_totales": 10,
  "porcentaje": 70.0,
  "preguntas": [
    {
      "tipo": "corta",
      "pregunta": "Explica el concepto...",
      "respuesta_correcta": "Respuesta modelo esperada",
      "puntos": 3
    }
  ],
  "resultados": [
    {
      "pregunta": "Explica el concepto...",
      "tipo": "corta",
      "respuesta_correcta": "Respuesta modelo esperada",
      "respuesta_usuario": "Mi respuesta...",
      "puntos": 2,
      "puntos_maximos": 3,
      "feedback": "Buena respuesta pero falta mencionar..."
    }
  ]
}
```

## 🎨 Interfaz de Usuario

### Sección "Generar Examen"
- Configuración visual con sliders numéricos
- Vista previa del tiempo estimado
- Interfaz de toma de examen limpia y organizada
- Resultados con código de colores (verde=correcto, rojo=incorrecto)

### Sección "Historial"
- Tarjetas de examen con información clave
- Indicador visual de aprobado/reprobado
- Botones de acción claramente identificados
- Layout responsive para móviles

## 📱 Responsive Design

Todas las nuevas interfaces son completamente responsivas:
- Desktop: Layout de 2-3 columnas
- Tablet: Layout de 2 columnas adaptativo
- Mobile: Layout de 1 columna con elementos apilados

## ✅ Verificación

Ejecuta el test de verificación:

```bash
python3 -c "
import json
from pathlib import Path

# Verificar endpoints
with open('api_server.py', 'r') as f:
    assert '/api/examenes/resultados' in f.read()
    
# Verificar funciones de retry
with open('examinator-web/src/App.jsx', 'r') as f:
    assert 'reintentarExamen' in f.read()
    
print('✅ Verificación exitosa')
"
```

## 🚀 Cómo Usar

1. **Generar un examen**:
   ```
   Mis Cursos → Selecciona documento → 📝 → Configura preguntas → Generar
   ```

2. **Completar el examen**:
   ```
   Responde cada pregunta → Evaluar Examen
   ```

3. **Ver respuestas correctas**:
   ```
   Después de evaluar, las respuestas correctas aparecen automáticamente
   ```

4. **Reintentar examen**:
   ```
   Historial → Encuentra tu examen → 🔄 Reintentar
   ```

## 📊 Ejemplo de Uso

```
Usuario: "Quiero estudiar para mi examen de biología"

1. Sube PDF de biología a "Mis Cursos"
2. Selecciona el documento → 📝
3. Configura: 10 opción múltiple, 5 corta, 2 desarrollo
4. Genera examen
5. Completa el examen
6. Evalúa → Obtiene 75%
7. Revisa respuestas correctas para aprender
8. En "Historial" → 🔄 Reintentar
9. Completa el examen nuevamente
10. Evalúa → Obtiene 90% ¡Mejoró!
```

## 🎓 Valor Educativo

Esta funcionalidad permite:
- **Aprendizaje iterativo**: Reintentar hasta dominar el material
- **Feedback inmediato**: Ver qué se hizo mal y cómo mejorar
- **Auto-evaluación**: Comparar respuestas con modelos correctos
- **Seguimiento de progreso**: Historial completo de intentos
- **Estudio efectivo**: Enfocarse en áreas débiles

## 🔒 Almacenamiento

Los resultados se guardan en:
```
extracciones/
  └── [carpeta]/
      ├── documento.txt
      └── resultados/
          ├── resultado_20250116_120000.json
          ├── resultado_20250116_140000.json
          └── ...
```

Cada archivo contiene toda la información necesaria para:
- Ver resultados históricos
- Reintentar con las mismas preguntas
- Comparar múltiples intentos
