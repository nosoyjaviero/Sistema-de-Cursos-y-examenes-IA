# 📋 Sistema de Logs Detallados

## ¿Qué es?

Sistema de logging completo que registra **TODO** el proceso de generación de prácticas en archivos individuales por consulta.

## 📁 Ubicación de los Logs

Los logs se guardan automáticamente en:
```
logs_practicas_detallado/
├── practica_20251119_143052.log    (archivo legible)
├── practica_20251119_143052.json   (formato JSON)
├── practica_20251119_143210.log
├── practica_20251119_143210.json
└── ...
```

Cada generación de práctica crea **2 archivos**:
- `.log` → Formato legible para humanos
- `.json` → Formato estructurado para análisis

## 📊 Contenido del Log

Cada archivo `.log` contiene **7 secciones completas**:

### 1. REQUEST RECIBIDO DEL FRONTEND
```
num_preguntas: {'true_false': 2}
ajustes_modelo: {'temperature': 0.7, 'max_tokens': 4000}
sin_prompt_sistema: True
usar_ollama: True
modelo: qwen-local:latest
contenido_length: 2163
```

### 2. PROMPT ENVIADO AL MODELO
```
Longitud: 2163 caracteres

Genera una práctica educativa basada en el contenido proporcionado.

TIPOS DE PREGUNTAS A GENERAR:

**2 Verdadero/Falso** - Formato JSON:
{
  "type": "true_false",
  ...
}
```

### 3. RESPUESTA COMPLETA DEL MODELO
```
Longitud: 4316 caracteres

[Respuesta completa sin modificar del modelo de IA]
```

### 4. JSON EXTRAÍDO Y PARSEADO
```json
{
  "questions": [
    {
      "type": "true_false",
      "difficulty": "medium",
      "statement": "Un diseño visualmente atractivo...",
      "correct_answer": true,
      "explanation": "..."
    }
  ]
}
```

### 5. PREGUNTAS PARSEADAS (Objetos Python)
```json
Pregunta 1:
{
  "tipo": "true_false",
  "pregunta": "Un diseño visualmente atractivo...",
  "respuesta_correcta": true,
  "puntos": 1,
  "dificultad": "medium"
}
```

### 6. PROCESO DE FILTRADO
```
total_generadas: 2
total_filtradas: 2
solicitadas: {'true_false': 2}
contador_por_tipo: {'true_false': 2}
```

### 7. RESULTADO FINAL DEVUELTO AL FRONTEND
```json
Total preguntas: 2

Pregunta 1:
{
  "tipo": "true_false",
  "pregunta": "...",
  ...
}

Pregunta 2:
{
  "tipo": "true_false",
  "pregunta": "...",
  ...
}
```

### 8. ERRORES ENCONTRADOS (si los hay)
```
• El modelo no generó suficientes preguntas: true_false: 1/2
• Error parseando JSON: Unexpected character at position 123
```

## 🔍 Cómo Usar los Logs

### Verificar en la Terminal
Cuando generas una práctica, verás en la terminal:
```
📋 Log detallado: logs_practicas_detallado\practica_20251119_143052.log
```

### Leer el Archivo
1. Abre el archivo `.log` con cualquier editor de texto
2. Busca la sección que te interesa (están numeradas)
3. Compara lo que enviaste vs lo que recibiste vs lo que se pintó

### Identificar Problemas

**Problema: No se generaron preguntas**
1. Ve a **Sección 3** (Respuesta del modelo)
   - ¿El modelo respondió algo?
   - ¿Está en formato JSON?

2. Ve a **Sección 4** (JSON extraído)
   - ¿Se pudo extraer el JSON?
   - ¿Tiene el campo `questions`?

3. Ve a **Sección 8** (Errores)
   - ¿Qué error específico ocurrió?

**Problema: Se generaron menos preguntas de las solicitadas**
1. Ve a **Sección 6** (Filtrado)
   - `solicitadas`: ¿Qué pediste?
   - `contador_por_tipo`: ¿Qué generó el modelo?
   - Si no coinciden → el modelo generó tipos diferentes

2. Ve a **Sección 5** (Preguntas parseadas)
   - Verifica el `tipo` de cada pregunta
   - Compara con lo que solicitaste en Sección 1

**Problema: Preguntas incorrectas o raras**
1. Ve a **Sección 2** (Prompt enviado)
   - ¿Las instrucciones son claras?
   - ¿El contenido es suficiente?

2. Ve a **Sección 3** (Respuesta del modelo)
   - ¿El modelo entendió las instrucciones?
   - ¿Agregó texto extra fuera del JSON?

## 📈 Análisis de Patrones

Si tienes múltiples logs, puedes:

1. **Buscar patrones de error**:
   ```powershell
   Get-ChildItem logs_practicas_detallado\*.log | Select-String "Error"
   ```

2. **Ver cuántas preguntas se generaron por log**:
   ```powershell
   Get-ChildItem logs_practicas_detallado\*.log | Select-String "Total preguntas:"
   ```

3. **Encontrar casos donde el filtrado redujo preguntas**:
   ```powershell
   Get-ChildItem logs_practicas_detallado\*.log | Select-String "generadas →"
   ```

## 🎯 Casos de Uso

### 1. Reportar un Bug
Cuando encuentres un problema:
1. Genera la práctica problemática
2. Copia el nombre del archivo log que aparece en terminal
3. Comparte ese archivo con el desarrollador
4. El desarrollador verá **exactamente** qué pasó en cada paso

### 2. Entender por qué el modelo falla
Si el modelo constantemente genera tipos incorrectos:
1. Revisa **Sección 2** de varios logs
2. Compara los prompts
3. Verifica si hay patrones en **Sección 3** (respuestas)

### 3. Optimizar el contenido
Si las preguntas son malas:
1. Ve a **Sección 2** → largo del contenido
2. Si es muy corto (< 500 chars) → el modelo no tiene suficiente info
3. Si es muy largo (> 8000 chars) → se trunca

## ⚙️ Configuración

El sistema de logging está **siempre activo** y se ejecuta automáticamente cada vez que:
- Generas una nueva práctica desde el frontend
- El backend llama a `generador_actual.generar_examen()`

**No necesitas hacer nada**, los logs se crean solos.

## 🗑️ Limpieza

Para limpiar logs antiguos:
```powershell
# Eliminar logs de más de 7 días
Get-ChildItem logs_practicas_detallado\* -File | 
  Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | 
  Remove-Item
```

## 🆘 Soporte

Si encuentras problemas:
1. Localiza el archivo `.log` de la consulta problemática
2. Revisa las 7 secciones en orden
3. Identifica en qué sección ocurre el problema
4. Comparte esa información específica

Los logs te darán **visibilidad completa** de todo el proceso de generación. 🔍
