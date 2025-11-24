# 🚀 Guía Rápida: Iniciar Sistema de Búsqueda IA

## ✅ YA ESTÁ TODO INTEGRADO EN LA INTERFAZ

La interfaz de búsqueda ya está completamente agregada a tu aplicación React. Solo necesitas iniciar el backend.

## 📋 Pasos para empezar:

### 1. Instalar dependencias de Python (solo la primera vez)

```powershell
cd C:\Users\Fela\Documents\Proyectos\Examinator
pip install -r requirements_buscador.txt
```

⏱️ Esto puede tomar 5-10 minutos la primera vez (descarga modelos y bibliotecas).

### 2. Crear el índice inicial (solo la primera vez)

```powershell
python crear_indice_inicial.py
```

⏱️ Esto puede tomar 1-5 minutos dependiendo de cuántos archivos tengas.

Verás algo como:
```
📁 Escaneando: cursos...
📁 Escaneando: notas...
📁 Escaneando: flashcards...
🤖 Generando embeddings...
✅ Indexados 150 archivos, 3420 chunks
```

### 3. Iniciar el servidor de búsqueda

```powershell
python api_buscador.py
```

Debe mostrar:
```
🚀 Servidor de búsqueda iniciado en http://localhost:5001
🤖 Modelo: BAAI/bge-small-en-v1.5
⚡ GPU: ✅ Disponible (CUDA)
📊 Índice cargado: 3420 chunks de 150 archivos
```

**DEJA ESTE TERMINAL ABIERTO** mientras uses la búsqueda.

### 4. Usar la búsqueda en la interfaz

1. **Abre tu aplicación React** (si no está corriendo):
   ```powershell
   cd examinator-web
   npm start
   ```

2. **En la interfaz web**:
   - Haz clic en **🔍 Buscar** en el menú lateral
   - Escribe lo que quieras buscar
   - ¡Listo! 🎉

## 🔍 Ejemplos de búsqueda:

- "¿Qué es una función recursiva?"
- "Conceptos de machine learning"
- "Ejercicios de cálculo"
- "Notas sobre React"
- "Flashcards de historia"

## 🔄 Actualizar índice cuando agregues archivos nuevos

Desde la interfaz:
- Botón **🔄 Actualizar Índice** (solo archivos nuevos/modificados)
- Botón **♻️ Reindexar Todo** (todo desde cero)

## 🐛 Solución de problemas:

### "Error al buscar. Servidor no disponible"
→ Inicia el servidor: `python api_buscador.py`

### "Sin indexar"
→ Crea el índice: `python crear_indice_inicial.py`

### "GPU no disponible"
→ Se usará CPU (más lento pero funciona igual)

### El servidor se cierra solo
→ Revisa que no haya otro proceso en el puerto 5001
→ Revisa errores en la consola

## 📊 Verificar estado del sistema:

El panel superior en la interfaz muestra:
- ✅/⚠️ Estado del índice
- 📁 Número de archivos indexados
- 📄 Número de fragmentos (chunks)
- 🤖 Modelo usado
- ⚡ GPU activa o no

## 💡 Características:

- ✅ **Búsqueda semántica**: Entiende el significado, no solo palabras exactas
- ✅ **Búsqueda híbrida**: Combina semántica + palabras clave
- ✅ **GPU acelerada**: Usa tu RTX 4050
- ✅ **100% local**: Sin APIs de pago, sin internet
- ✅ **Multiusuario**: Máximo 3 búsquedas simultáneas
- ✅ **Actualización incremental**: Solo reindexar archivos modificados

## 🎯 ¡Empieza ahora!

```powershell
# Si es la primera vez:
pip install -r requirements_buscador.txt
python crear_indice_inicial.py

# Siempre que quieras usar la búsqueda:
python api_buscador.py
```

Luego abre la interfaz web y haz clic en **🔍 Buscar**.

---

**¿Problemas?** Revisa que:
1. ✅ El servidor de búsqueda esté corriendo (`python api_buscador.py`)
2. ✅ La aplicación React esté corriendo (`npm start` en examinator-web)
3. ✅ Ambos en terminales separadas
