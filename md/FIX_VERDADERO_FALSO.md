# Fix: Soporte completo para tipo 'verdadero-falso'

## Problema
Las preguntas de verdadero-falso generadas con tipo `'verdadero-falso'` (con guion) se mostraban incorrectamente en la UI como "📖 Desarrollo" en lugar de "✓✗ Verdadero/Falso".

## Causa
El sistema usaba tres variantes del tipo:
- `'verdadero_falso'` (con guion bajo) - usado internamente
- `'true_false'` - formato normalizado interno
- `'verdadero-falso'` (con guion) - generado por el mapeo al formato UI

El frontend y backend no manejaban consistentemente la variante con guion.

## Solución Implementada

### 1. Frontend (App.jsx)
**Línea ~10673**: Agregado reconocimiento de `'verdadero-falso'` en etiqueta de tipo
```javascript
pregunta.tipo === 'verdadero-falso' ? '✓✗ Verdadero/Falso' :
```

**Línea ~11350**: Agregado a condición de renderizado de opciones
```javascript
{(pregunta.tipo === 'verdadero_falso' || pregunta.tipo === 'verdadero-falso' || pregunta.tipo === 'true_false') && (
```

### 2. Backend (generador_unificado.py)

**Línea ~740**: Agregado mapeo en filtrado de preguntas
```python
'verdadero-falso': 'true_false',
```

**Línea ~1221**: Agregado mapeo en generación con dos pasos
```python
'verdadero-falso': 'true_false',
```

**Línea ~1454**: Agregado soporte en evaluación de respuestas
```python
elif pregunta.tipo == "verdadero_falso" or pregunta.tipo == "verdadero-falso" or pregunta.tipo == "true_false":
```

## Validación
Ahora todas las variantes funcionan correctamente:
- ✅ `'verdadero_falso'` (guion bajo)
- ✅ `'verdadero-falso'` (guion)
- ✅ `'true_false'` (inglés)

## Archivos Modificados
1. `examinator-web/src/App.jsx` - 2 cambios
2. `generador_unificado.py` - 3 cambios
