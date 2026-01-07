# 🎯 Guía de Uso: Sistema de Gestión de Errores en la UI

## 📋 Paso 1: Integrar el Componente en tu App React

### 1.1 Agregar la ruta en `App.jsx`

```jsx
// examinator-web/src/App.jsx
import SesionEstudio from './components/SesionEstudio';

function App() {
  return (
    <Routes>
      {/* Tus rutas existentes... */}
      
      {/* NUEVA RUTA: Sesión de Estudio */}
      <Route path="/sesion-estudio" element={<SesionEstudio />} />
    </Routes>
  );
}
```

### 1.2 Agregar botón en el menú de navegación

```jsx
// En tu componente de navegación o sidebar
<nav>
  <Link to="/">Inicio</Link>
  <Link to="/generar">Generar Examen</Link>
  <Link to="/sesion-estudio">🎯 Sesión de Estudio</Link>  {/* NUEVO */}
</nav>
```

---

## 🚀 Paso 2: Iniciar el Sistema

### 2.1 Iniciar el servidor API (Backend)

```bash
# En la terminal, dentro de la carpeta Examinator
python api_server.py
```

Verás:
```
🚀 Iniciando servidor API de Examinator...
📍 URL: http://localhost:8000
📚 Docs: http://localhost:8000/docs
🎯 Sistema de Gestión de Errores: ACTIVO
```

### 2.2 Iniciar la aplicación React (Frontend)

```bash
# En otra terminal, dentro de examinator-web
npm start
```

La app se abrirá en `http://localhost:3000`

---

## 🎓 Paso 3: Usar el Sistema

### Flujo Completo:

#### 1️⃣ **Completar un Examen**

- Ve a tu UI normal y completa un examen
- El sistema guardará el examen como `examen_YYYYMMDD_HHMMSS.json`

#### 2️⃣ **Procesar Errores Automáticamente** (OPCIÓN A: Backend)

Si quieres que se procese automáticamente al completar el examen, modifica el endpoint de completar examen:

```python
# En api_server.py, en el endpoint que guarda exámenes completados
@app.post("/api/examenes/completar")
async def completar_examen(...):
    # ... código existente de guardar examen ...
    
    # AGREGAR ESTO AL FINAL:
    try:
        resumen_errores = await procesar_examen_errores(examen_id)
        print(f"✅ Errores procesados automáticamente")
    except:
        print("⚠️ No se pudieron procesar errores")
    
    return resultado
```

#### 2️⃣ **Procesar Errores Manualmente** (OPCIÓN B: Script)

```bash
# Ejecuta después de completar un examen
python procesar_mi_examen.py
```

Esto:
- ✅ Encuentra tu último examen
- ✅ Detecta errores
- ✅ Actualiza el banco
- ✅ Genera sesión de estudio

#### 3️⃣ **Ver Sesión de Estudio en la UI**

1. Abre tu navegador en `http://localhost:3000`
2. Haz clic en **"🎯 Sesión de Estudio"** en el menú
3. Verás:
   - 📊 Estadísticas del banco de errores
   - 🎯 Errores priorizados para hoy
   - 💡 Recomendaciones personalizadas
   - ✅ Botón para marcar como resuelto

---

## 📊 Endpoints Disponibles

### 1. Procesar Examen

```bash
POST http://localhost:8000/api/errores/procesar-examen?examen_id=20251122_111844
```

**Respuesta:**
```json
{
  "examen_id": "20251122_111844",
  "resumen_estados": {
    "aciertos": 2,
    "fallos": 3,
    "respuestas_debiles": 1
  },
  "errores_detectados": [...],
  "banco_actualizado": {
    "nuevos": 2,
    "actualizados": 2,
    "total_banco": 10
  }
}
```

### 2. Ver Estadísticas

```bash
GET http://localhost:8000/api/errores/estadisticas
```

**Respuesta:**
```json
{
  "total_errores": 10,
  "errores_activos": 7,
  "por_estado": {
    "nuevos": 2,
    "en_refuerzo": 5,
    "resueltos": 3
  },
  "tasa_resolucion": 30.0
}
```

### 3. Obtener Sesión de Estudio

```bash
GET http://localhost:8000/api/errores/sesion-estudio?max_errores=10
```

**Respuesta:**
```json
{
  "fecha_sesion": "2025-11-22T12:00:00",
  "total_errores_seleccionados": 8,
  "errores": [
    {
      "id_error": "err_abc123",
      "pregunta": { ... },
      "razon_seleccion": "🔴 Fallada 3 veces | 📅 7 días sin practicar",
      "recomendacion_estudio": "💡 Dedica tiempo extra..."
    }
  ],
  "estadisticas_sesion": { ... },
  "mensaje_motivacional": "🎯 Sesión intensiva: 3 conceptos difíciles..."
}
```

### 4. Marcar Error como Resuelto

```bash
POST http://localhost:8000/api/errores/marcar-resuelto/err_abc123
```

**Respuesta:**
```json
{
  "mensaje": "✅ Error err_abc123 marcado como resuelto",
  "error": { ... }
}
```

---

## 🎯 Cómo Funciona el Repaso

### Sistema de Priorización Inteligente

El sistema prioriza errores según:

1. **Estado** (máxima prioridad):
   - ⚠️ **Nuevos errores** (nunca practicados después del fallo)
   - 🔄 **En refuerzo** (practicados pero no dominados)
   - ✅ **Resueltos** (ya dominados, solo repaso)

2. **Frecuencia de Fallos**:
   - 🔴 **≥3 fallos**: Conceptos muy difíciles
   - 🟡 **2 fallos**: Necesita refuerzo
   - 🟢 **1 fallo**: Error ocasional

3. **Spacing Effect** (días sin práctica):
   - Más días sin practicar = más urgente
   - Aplica el principio pedagógico de repetición espaciada
   - Evita que olvides conceptos antiguos

4. **Prioridad Calculada**:
   - Alta: Errores críticos
   - Media: Errores importantes
   - Baja: Errores menores

### Ejemplo de Orden de Prioridad:

```
1. ⚠️ Error nuevo con 3 fallos (URGENTE)
2. 🔄 Error con 4 fallos, sin practicar 15 días
3. 🔄 Error con 3 fallos, sin practicar 10 días
4. 🔄 Error con 2 fallos, sin practicar 8 días
5. 🔄 Error con 1 fallo, sin practicar 5 días
...
```

---

## 🔄 Flujo de Repaso Completo

### Sesión de Estudio Típica:

1. **Abrir Sesión de Estudio**
   - Ir a `/sesion-estudio` en tu app
   - El sistema muestra los N errores más prioritarios

2. **Revisar Cada Error**
   - Lee la pregunta
   - Intenta responderla mentalmente
   - Ve la respuesta correcta
   - Lee la recomendación de estudio

3. **Marcar como Resuelto**
   - Si ya dominas el concepto, haz clic en "✅ Marcar como Resuelto"
   - El error pasará a estado "resuelto" y tendrá menor prioridad

4. **Repetir Regularmente**
   - Haz sesiones de estudio diarias/semanales
   - El sistema ajustará prioridades automáticamente
   - Conceptos antiguos volverán a aparecer (spacing effect)

---

## 📱 Capturas de Pantalla (Simulación)

### Vista de Sesión de Estudio:

```
╔══════════════════════════════════════════════════════════╗
║           🎯 Sesión de Estudio Personalizada             ║
╚══════════════════════════════════════════════════════════╝

💬 🎯 Sesión intensiva: 3 conceptos difíciles. ¡Puedes con esto! 💡

┌─────────────────── Tu Banco de Errores ───────────────────┐
│  Total: 10  │  Activos: 7  │  Resueltos: 3  │  Tasa: 30%  │
└────────────────────────────────────────────────────────────┘

📋 Composición de la Sesión:
   ⚠️ 2 Nuevos  🔴 3 Alta Frecuencia  📅 5 Antiguos  ⏱️ 8.5 días promedio

─────────────────────────────────────────────────────────────

🎓 Errores a Practicar Hoy (8)

┌─────────────────────────────────────────────────────────┐
│ #1  MCQ  ⚠️ Nuevo  🔴 Alta                              │
│                                                          │
│ ¿Cuál es la derivada de x²?                              │
│                                                          │
│ A. x                                                     │
│ B. 2x  ✓                                                 │
│ C. x³                                                    │
│ D. 2                                                     │
│                                                          │
│ 📊 Veces fallada: 3 | 📅 Días sin práctica: 0           │
│                                                          │
│ 📍 🔴 Fallada 3 veces - concepto difícil | 🎯 Alta      │
│ 💡 Dedica tiempo extra a entender el concepto...        │
│                                                          │
│ [✅ Marcar como Resuelto]                               │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Personalización

### Cambiar Cantidad de Errores:

En la UI, usa el selector:
```
Errores a mostrar: [5] [10] [15] [20]
```

O en la API:
```bash
GET /api/errores/sesion-estudio?max_errores=15
```

### Filtrar por Carpeta:

```bash
GET /api/errores/buscar?carpeta=Matematicas
```

### Filtrar por Tipo:

```bash
GET /api/errores/buscar?tipo_pregunta=multiple
```

### Filtrar por Estado:

```bash
GET /api/errores/buscar?estado=nuevo_error
```

---

## 💾 Persistencia de Datos

Todos los errores se guardan en:
```
examenes/error_bank/banco_errores_global.json
```

Este archivo persiste entre sesiones, así que:
- ✅ Puedes cerrar el servidor y los datos se mantienen
- ✅ El historial de cada error se guarda
- ✅ Las estadísticas se actualizan en tiempo real

---

## 🎓 Uso Recomendado para Repasar

### Rutina Diaria:

1. **Mañana** (10 min):
   - Abrir sesión de estudio
   - Revisar 5 errores prioritarios
   - Marcar los que ya domines

2. **Tarde** (después de nuevo examen):
   - Completar examen nuevo
   - Ejecutar `python procesar_mi_examen.py`
   - Ver nuevos errores agregados

3. **Noche** (15 min):
   - Repasar errores de alta frecuencia
   - Estudiar conceptos difíciles
   - Marcar resueltos si corresponde

### Rutina Semanal:

- **Lunes**: Sesión completa (10 errores)
- **Miércoles**: Repaso rápido (5 errores)
- **Viernes**: Sesión completa + marcar resueltos
- **Domingo**: Revisar estadísticas generales

---

## 🆘 Solución de Problemas

### Error: "No se pudieron cargar los errores"

**Causa**: El servidor API no está ejecutándose.

**Solución**:
```bash
python api_server.py
```

### Error: "Banco vacío"

**Causa**: No has completado exámenes aún.

**Solución**:
1. Completa al menos un examen
2. Ejecuta `python procesar_mi_examen.py`
3. Recarga la sesión de estudio

### Los errores no se actualizan

**Solución**:
1. Haz clic en el botón "🔄 Actualizar"
2. O recarga la página (F5)

---

## 📚 Scripts Auxiliares Creados

| Script | Función |
|--------|---------|
| `procesar_mi_examen.py` | Procesa el último examen automáticamente |
| `ver_estadisticas.py` | Muestra estadísticas del banco |
| `ver_sesion_hoy.py` | Muestra sesión de estudio en terminal |
| `ejemplo_sistema_errores.py` | Demo completa con examen ficticio |

---

## 🎯 Resumen

✅ **El sistema está listo para:**
- Detectar automáticamente tus errores
- Priorizarlos inteligentemente
- Mostrarte qué repasar cada día
- Trackear tu progreso a largo plazo

✅ **Para usarlo:**
1. Inicia el servidor: `python api_server.py`
2. Inicia React: `npm start`
3. Navega a `/sesion-estudio`
4. ¡Empieza a repasar!

✅ **Para repasar:**
- El sistema usa spacing effect (repetición espaciada)
- Errores antiguos reaparecen automáticamente
- Puedes marcar como resueltos cuando domines
- Las estadísticas te muestran tu progreso

**¡Listo para mejorar tu aprendizaje! 🚀**
