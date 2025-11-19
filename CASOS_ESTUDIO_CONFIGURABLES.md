# 🎯 Casos de Estudio Configurables

## 📋 Descripción

Sistema completo para generar **12 tipos diferentes de casos de estudio** con estructuras personalizadas según el tipo seleccionado. Cada tipo tiene campos específicos que el modelo IA genera automáticamente.

## ✨ Características Implementadas

### 🔧 Backend (Python)

#### 1. **generador_unificado.py**
- ✅ Método `_obtener_prompt_caso_estudio()` con 12 plantillas JSON
- ✅ Parámetro `tipo_caso` en `generar_examen()`
- ✅ Parámetro `tipo_caso` en `_crear_prompt()`
- ✅ Prompts especializados para cada tipo con campos únicos

#### 2. **api_server.py**
- ✅ Recibe parámetro `tipo_caso` en endpoint `/api/generar_practica`
- ✅ Pasa `tipo_caso` al generador cuando hay casos de estudio
- ✅ Logging mejorado mostrando tipo de caso seleccionado

### 🎨 Frontend (React)

#### 1. **Estado**
- ✅ Variable `tipoCasoEstudio` con valor por defecto "descriptivo"

#### 2. **UI - Selector**
- ✅ Dropdown con 12 opciones de tipos de caso
- ✅ Selector visible solo cuando casos de estudio > 0
- ✅ Estilo consistente con el diseño actual

#### 3. **Visualización Dinámica**
- ✅ Renderizado condicional según subtipo del caso
- ✅ Tarjetas visuales con gradientes por sección
- ✅ Iconos específicos para cada campo
- ✅ Compatibilidad con formato antiguo (legacy)

## 📚 Los 12 Tipos de Casos de Estudio

### 1. 📖 **Descriptivo**
Describe qué pasó, quién hizo qué y por qué.

**Campos:**
- `titulo`: Título del caso
- `contexto`: Situación del caso
- `descripcion`: Eventos detallados
- `pregunta`: Qué elementos clave caracterizaron la situación
- `puntos_clave`: Array de puntos a observar
- `respuesta_esperada`: Análisis descriptivo

**Uso:** Principiantes, análisis de mercado, diagnósticos

---

### 2. 🔬 **Analítico-Diagnóstico**
Explica causas, relaciones y consecuencias. Autopsia empresarial.

**Campos:**
- `titulo`, `contexto`, `descripcion`, `pregunta`
- `areas_analisis`: ["Causas", "Relaciones", "Consecuencias", "Impacto"]
- `respuesta_esperada`: Análisis profundo de causas-efectos

**Uso:** Consultoría, ingeniería, trading, producto

---

### 3. 🔥 **Resolución de Problemas**
Plantea un problema abierto y exige una solución.

**Campos:**
- `titulo`, `contexto`, `descripcion`, `pregunta`
- `restricciones`: Array de limitaciones
- `criterios_evaluacion`: ["Viabilidad", "Costo-beneficio", "Implementación"]
- `respuesta_esperada`: Solución detallada con pasos

**Uso:** Estrategia, operaciones, trading algorítmico, optimización

---

### 4. 🎯 **Toma de Decisiones**
Escenario donde debes decidir entre varias rutas y justificar.

**Campos:**
- `titulo`, `contexto`, `descripcion`, `pregunta`
- `opciones_disponibles`: Array de opciones con descripción
- `criterios_decision`: Criterios para evaluar
- `respuesta_esperada`: Decisión con pros/contras

**Uso:** Management, inversiones, liderazgo

---

### 5. 🔄 **Comparativo**
Compara dos soluciones, caminos, empresas o metodologías.

**Campos:**
- `titulo`, `contexto`, `descripcion`, `pregunta`
- `elementos_comparar`: Objeto con alternativas y características
- `criterios_comparacion`: Criterios de comparación
- `respuesta_esperada`: Comparación detallada con recomendación

**Uso:** Análisis competitivo, producto, ingeniería

---

### 6. 📈 **Predictivo**
Proyectar el futuro basado en datos actuales.

**Campos:**
- `titulo`, `contexto`, `descripcion`, `pregunta`
- `datos_actuales`: Métricas e indicadores
- `factores_considerar`: Variables externas
- `respuesta_esperada`: Predicción fundamentada

**Uso:** Trading, marketing, ciencia de datos

---

### 7. 🎮 **Simulación**
Mundo con variables dinámicas donde decides en tiempo real.

**Campos:**
- `titulo`, `contexto`, `descripcion`, `pregunta`
- `variables_dinamicas`: Objeto con variables y rangos
- `decisiones_tomar`: Array de decisiones
- `respuesta_esperada`: Secuencia de decisiones justificadas

**Uso:** Negocios, trading, logística, sistemas complejos

---

### 8. 🔙 **Inverso (Reverse)**
Resultado final conocido, reconstruye el proceso.

**Campos:**
- `titulo`, `contexto`, `descripcion`, `pregunta`
- `resultado_final`: Outcome conocido
- `pistas`: Array de evidencias
- `pasos_reconstruir`: Número de pasos esperados
- `respuesta_esperada`: Reconstrucción lógica paso a paso

**Uso:** Ingeniería, investigación, auditoría, metodología

---

### 9. 💥 **Fallo/Desastre**
Estudio de algo que salió mal. Lecciones aprendidas.

**Campos:**
- `titulo`, `contexto`, `descripcion`, `pregunta`
- `señales_alerta`: Warnings ignorados
- `consecuencias`: Array de impactos
- `respuesta_esperada`: Análisis de causas con prevención

**Uso:** Liderazgo, startups, control de calidad

---

### 10. ✨ **Creativo/Innovación**
No hay respuesta correcta única. Ideación e innovación.

**Campos:**
- `titulo`, `contexto`, `descripcion`, `pregunta`
- `restricciones`: Limitaciones
- `criterios_creatividad`: ["Originalidad", "Viabilidad", "Impacto"]
- `respuesta_esperada`: Idea innovadora justificada

**Uso:** Diseño, innovación, estrategia empresarial

---

### 11. ⚖️ **Ético**
Decisión correcta cuando negocio choca con moral.

**Campos:**
- `titulo`, `contexto`, `descripcion`, `pregunta`
- `stakeholders`: Partes afectadas
- `dilema`: Conflicto ético específico
- `consideraciones_eticas`: Principios y valores
- `respuesta_esperada`: Decisión balanceando ética y negocio

**Uso:** Compliance, liderazgo, cultura organizacional

---

### 12. 🔧 **Técnico-Operativo**
Sistema o proceso a optimizar.

**Campos:**
- `titulo`, `contexto`, `descripcion`, `pregunta`
- `metricas_actuales`: Objeto con valores actuales
- `limitaciones_tecnicas`: Array de constraints
- `objetivos_optimizacion`: Mejoras esperadas
- `respuesta_esperada`: Propuesta de optimización técnica

**Uso:** Ingenierías, programación, sistemas, manufactura

---

## 🎨 Visualización en la UI

Cada tipo de caso se muestra con:

1. **Tarjeta de Título** (gradiente morado)
   - Título del caso
   - Badge con subtipo

2. **Tarjeta de Contexto** (gradiente oscuro)
   - Situación del caso

3. **Descripción** (fondo transparente)
   - Detalles específicos

4. **Campos Específicos** (según tipo)
   - Colores diferenciados
   - Iconos temáticos
   - Listas o objetos estructurados

5. **Pregunta Principal** (gradiente morado)
   - Destacada al final

## 🚀 Cómo Usar

### 1. En la Interfaz Web

```
1. Ir a "Prácticas"
2. Seleccionar carpeta/archivo
3. En "Casos de Estudio":
   - Cantidad: 1-5
   - Tipo de Caso: Seleccionar del dropdown
4. Generar Práctica
```

### 2. Tipos Recomendados por Área

**Negocios/Management:**
- Decisión, Comparativo, Predictivo, Ético

**Ingeniería/Técnico:**
- Técnico-Operativo, Resolución, Analítico, Simulación

**Consultoría:**
- Analítico, Fallo, Comparativo, Resolución

**Educación/Training:**
- Descriptivo, Inverso, Creativo

**Trading/Finanzas:**
- Predictivo, Simulación, Decisión

## 📝 Ejemplo de JSON Generado

### Caso Analítico
```json
{
  "tipo": "case_study",
  "subtipo": "analitico",
  "titulo": "Caída de Ventas Post-Lanzamiento",
  "contexto": "Startup tech lanzó app móvil con gran marketing",
  "descripcion": "Primeras 2 semanas: 50k descargas. Mes 2: 80% de usuarios inactivos",
  "pregunta": "Analiza las causas, relaciones y consecuencias de esta caída",
  "areas_analisis": [
    "Causas principales de la inactividad",
    "Relación entre UX y retención",
    "Consecuencias en el modelo de negocio",
    "Impacto en funding siguiente ronda"
  ],
  "respuesta_esperada": "Análisis profundo de causas-efectos...",
  "puntos": 10
}
```

### Caso de Decisión
```json
{
  "tipo": "case_study",
  "subtipo": "decision",
  "titulo": "Elegir Stack Tecnológico",
  "contexto": "Equipo de 5 devs debe elegir tech stack para MVP",
  "descripcion": "6 meses de desarrollo, presupuesto limitado, necesidad de escalar",
  "pregunta": "¿Qué stack tecnológico elegirías y por qué?",
  "opciones_disponibles": [
    "Opción A: MERN (Mongo, Express, React, Node)",
    "Opción B: Django + PostgreSQL + React",
    "Opción C: Laravel + Vue + MySQL"
  ],
  "criterios_decision": [
    "Velocidad de desarrollo",
    "Escalabilidad",
    "Curva de aprendizaje",
    "Costo de hosting"
  ],
  "respuesta_esperada": "Decisión justificada con pros/contras...",
  "puntos": 10
}
```

## 🔍 Testing

Para probar cada tipo:

```bash
# 1. Reiniciar servidor
python api_server.py

# 2. En la web:
- Seleccionar tipo de caso
- Generar 1 caso
- Verificar que se muestran todos los campos específicos
- Responder el caso
- Evaluar con IA
```

## 📊 Estructura de Archivos Modificados

```
Backend:
├── generador_unificado.py
│   ├── _obtener_prompt_caso_estudio() [NUEVO]
│   ├── _crear_prompt() [MODIFICADO - parámetro tipo_caso]
│   └── generar_examen() [MODIFICADO - parámetro tipo_caso]
│
└── api_server.py
    └── generar_practica() [MODIFICADO - recibe tipo_caso]

Frontend:
└── examinator-web/src/App.jsx
    ├── Estado: tipoCasoEstudio [NUEVO]
    ├── Selector dropdown [NUEVO]
    ├── Renderizado dinámico [MODIFICADO - 400+ líneas]
    └── Llamada API [MODIFICADO - incluye tipo_caso]
```

## 🎯 Beneficios

1. ✅ **Flexibilidad Total**: 12 tipos diferentes adaptables a cualquier tema
2. ✅ **Generación Automática**: El modelo crea todos los campos específicos
3. ✅ **Visualización Rica**: UI muestra cada campo con estilo propio
4. ✅ **Educativo**: Casos realistas y estructurados profesionalmente
5. ✅ **Escalable**: Fácil agregar más tipos en el futuro

## 🔮 Próximos Pasos (Opcional)

- [ ] Agregar ejemplos de casos reales por tipo
- [ ] Permitir mezclar tipos en una misma práctica
- [ ] Guardar tipo de caso en historial
- [ ] Estadísticas de performance por tipo
- [ ] Templates predefinidos por industria

## 📞 Soporte

Si un tipo de caso no se genera correctamente:

1. Verificar logs del servidor
2. Revisar que el modelo tenga suficiente contexto
3. Aumentar `max_tokens` si la respuesta se corta
4. Probar con otro tipo más simple primero

---

**Implementado:** 19 de noviembre de 2025
**Versión:** 1.0.0
