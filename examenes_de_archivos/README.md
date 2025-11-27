# 📚 Sistema de Generación de Exámenes por Archivos

## 🎯 Descripción General

Este sistema permite generar exámenes automáticos a partir de múltiples archivos de contenido educativo utilizando inteligencia artificial (Ollama). El proceso se realiza a través de un **modal de selección de archivos** que permite configurar y personalizar completamente el examen.

---

## 🖥️ Componentes del Sistema

### 1. **Modal de Selección de Archivos** (`modal-seleccion-archivos`)

Este modal aparece cuando seleccionas una carpeta y eliges generar un examen por:
- 🎓 **CURSO**: Examen completo de un curso
- 📚 **CAPÍTULO**: Examen de un capítulo específico
- 📖 **CLASE**: Examen de una clase individual
- 📝 **LECCIÓN**: Examen de una lección particular

#### Características del Modal:

**📊 Información de la Carpeta:**
- Muestra el nombre de la carpeta seleccionada
- Cantidad total de archivos encontrados
- Cantidad de archivos seleccionados para el examen

**⚙️ Configuración del Examen:**
Permite configurar cuántas preguntas de cada tipo quieres:
- **Opción Múltiple** (0-50 preguntas)
- **Respuesta Corta** (0-30 preguntas)
- **Verdadero/Falso** (0-20 preguntas)
- **Desarrollo** (0-10 preguntas)

**📂 Selección de Archivos:**
- Lista de todos los archivos disponibles en la carpeta
- Checkbox para incluir/excluir cada archivo
- Botones para seleccionar/deseleccionar todos
- Información de cada archivo (nombre, ruta, tamaño en KB)

---

## 🔄 Proceso de Generación

### Flujo Completo:

1. **Selección de Carpeta** → Usuario marca carpeta como curso/capítulo/clase/lección
2. **Apertura del Modal** → Se muestra el modal con archivos encontrados
3. **Configuración** → Usuario ajusta tipos y cantidad de preguntas
4. **Selección de Archivos** → Usuario elige qué archivos incluir
5. **Generación** → Sistema procesa archivos y genera preguntas
6. **Visualización** → Examen listo para responder

---

## 🚀 Estrategia de Generación (Backend)

### Endpoint: `/api/generar_examen_bloque`

El sistema utiliza una estrategia inteligente para generar preguntas de calidad:

#### **📝 Proceso por Archivo:**

1. **Lectura de Contenido:**
   - Lee el contenido de cada archivo seleccionado
   - Extrae texto y metadatos
   - Calcula caracteres totales

2. **Distribución Proporcional:**
   - Cada archivo recibe preguntas según su tamaño
   - Fórmula: `proporción = caracteres_archivo / total_caracteres`
   - Se generan más preguntas de las necesarias (200%) para mejor selección

3. **Generación con IA (Ollama):**
   - Modelo: `Meta-Llama-3.1-8B-Instruct-Q4-K-L:latest`
   - Temperature: 0.7 (creatividad moderada)
   - Max tokens: 3000
   - Timeout: 600 segundos (10 minutos)

4. **Tipos de Preguntas Generadas:**
   - 50% Opción Múltiple (`mcq`)
   - 20% Respuesta Corta (`short_answer`)
   - 20% Verdadero/Falso (`true_false`)
   - 10% Desarrollo (`open_question`)

---

## 📋 Normalización de Tipos

El sistema normaliza automáticamente los tipos de preguntas:

```javascript
Mapeo Backend → Frontend:
- 'mcq' / 'multiple' → 'multiple'
- 'short_answer' / 'corta' / 'respuesta_corta' → 'corta'
- 'true_false' / 'verdadero_falso' / 'verdadero-falso' → 'verdadero-falso'
- 'open_question' / 'desarrollo' → 'desarrollo'
```

---

## 🎲 Selección Final de Preguntas

Una vez generadas todas las preguntas, el sistema:

1. **Mezcla aleatoriamente** todas las preguntas generadas
2. **Separa por tipo** usando normalización
3. **Toma la cantidad solicitada** de cada tipo
4. **Completa faltantes** si es necesario con preguntas sobrantes
5. **Mezcla resultado final** para variedad
6. **Limita al total solicitado**

---

## 📂 Almacenamiento de Logs

Cada generación crea logs detallados en:

```
logs_practicas_detallado/
└── practica_YYYYMMDD_HHMMSS/
    └── practica_YYYYMMDD_HHMMSS.log
```

### Información en Logs:

- ✅ Archivos leídos (nombre y tamaño)
- 📊 Proporción de preguntas por archivo
- 🎯 Estrategia de generación
- 📝 Preguntas obtenidas por tipo
- ⚠️ Advertencias y errores
- ✅ Total final generado

---

## 🔍 Ejemplo de Uso

### Configuración:
```
📚 Archivos: 7 archivos seleccionados
📊 Config: M=3, C=2, VF=2, D=1
Total deseado: 8 preguntas
```

### Proceso:
```
Archivo 1: contexto_2025-11-23 (1949 chars)
  → Proporción: 10.5%
  → Genera: 4 preguntas (2 MCQ, 1 corta, 1 V/F)

Archivo 2: nota_2025_11_23 (1978 chars)
  → Proporción: 10.7%
  → Genera: 4 preguntas (2 MCQ, 1 corta, 1 V/F)

... (continúa con todos los archivos)

Total obtenido: 28 preguntas
Distribución: MCQ=14, Corta=7, V/F=7, Desarrollo=0
```

### Selección Final:
```
MCQ: tomadas 3/3 (disponibles: 14) ✅
Corta: tomadas 2/2 (disponibles: 7) ✅
V/F: tomadas 2/2 (disponibles: 7) ✅
Desarrollo: tomadas 0/1 (disponibles: 0) ⚠️
  → Completa 1 faltante con MCQ sobrante

✅ Total final: 8 preguntas generadas
```

---

## 🎨 Clases CSS Destacadas

### Modal Principal:
```css
.modal-seleccion-archivos {
  /* Contenedor principal del modal */
}
```

### Elementos Interactivos:
```css
.dropdown-item-highlight {
  /* Botones destacados para generar examen */
}

.archivo-item {
  /* Items de archivos seleccionables */
}

.archivo-item.incluido {
  /* Archivo seleccionado (con checkbox ☑) */
}

.archivo-item.excluido {
  /* Archivo excluido (con checkbox ☐) */
}
```

---

## 🛠️ Configuración Técnica

### Modelos de IA Soportados:
- Meta-Llama-3.1-8B-Instruct (Recomendado)
- Otros modelos compatibles con Ollama

### Requisitos:
- Ollama instalado y ejecutándose
- GPU activada (opcional, mejora rendimiento)
- Archivos en formato compatible (txt, md, pdf, etc.)

### Limitaciones:
- Máximo 50 preguntas de opción múltiple
- Máximo 30 preguntas de respuesta corta
- Máximo 20 preguntas de verdadero/falso
- Máximo 10 preguntas de desarrollo

---

## 📊 Estadísticas de Generación

El sistema proporciona:
- ✅ Total de preguntas obtenidas
- 📊 Distribución por tipo
- ⚠️ Advertencias de tipos faltantes
- 🔄 Completado automático de faltantes
- 🎯 Precisión de selección

---

## 🚦 Estados de Generación

Durante la generación verás:
- **Bloque X/Y**: Progreso de bloques
- **Porcentaje**: Barra de progreso visual
- **Mensaje**: Estado actual del proceso
- **Tiempo estimado**: Basado en archivos y configuración

---

## 💡 Consejos de Uso

1. **Selecciona archivos relevantes**: Solo incluye contenido relacionado con el tema
2. **Configura balanceadamente**: Distribuye tipos de preguntas según dificultad
3. **Revisa logs**: Si algo falla, consulta los logs detallados
4. **Prueba diferentes configs**: Experimenta con cantidades para mejores resultados
5. **Usa carpetas organizadas**: Estructura tu contenido por cursos/capítulos/clases

---

## 🔗 Archivos Relacionados

- **Frontend**: `examinator-web/src/App.jsx` (líneas 23534+)
- **Backend**: `api_server.py` (líneas 2143-2350)
- **Generador**: `generador_unificado.py`
- **Logs**: `logs_practicas_detallado/`

---

## 📝 Notas Adicionales

Este sistema está optimizado para:
- ✅ Generar exámenes de alta calidad
- ✅ Procesar múltiples archivos eficientemente
- ✅ Diversificar tipos de preguntas
- ✅ Mantener relevancia del contenido
- ✅ Proporcionar feedback detallado

**¡Ahora puedes crear exámenes automáticos de cualquier carpeta de contenido educativo!** 🎓✨
