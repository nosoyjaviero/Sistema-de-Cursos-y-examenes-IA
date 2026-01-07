# ✅ CHECKLIST DE INSTALACIÓN

> Usa este checklist para asegurar que todo está configurado correctamente

---

## 📋 Pre-Instalación

- [ ] **Python 3.8+ instalado**
  ```powershell
  python --version
  # Esperado: Python 3.8 o superior
  ```

- [ ] **Node.js 16+ instalado**
  ```powershell
  node --version
  # Esperado: v16.x o superior
  ```

- [ ] **GPU NVIDIA con drivers actualizados** (opcional pero recomendado)
  ```powershell
  nvidia-smi
  # Debe mostrar información de tu GPU
  ```

- [ ] **Al menos 15GB de espacio en disco libre**
  ```powershell
  Get-PSDrive C | Select-Object Used,Free
  ```

---

## 🔧 Instalación

- [ ] **Ejecutar script de instalación**
  ```powershell
  .\INSTALACION_COMPLETA.ps1
  ```
  - Esperar ~10-15 minutos
  - Ver que no hay errores en rojo
  - Confirmar "✓ INSTALACIÓN COMPLETADA"

- [ ] **Verificar entorno**
  ```powershell
  .\VERIFICAR_ENTORNO.ps1
  ```
  Debe mostrar:
  - [x] Python ✓
  - [x] Node.js ✓
  - [x] PyTorch con CUDA ✓
  - [x] GPU detectada ✓
  - [x] Dependencias Python ✓
  - [x] Dependencias Node.js ✓

---

## 🧪 Pruebas Post-Instalación

- [ ] **Verificar GPU/CUDA**
  ```powershell
  python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
  ```
  Esperado:
  ```
  CUDA: True
  GPU: NVIDIA GeForce RTX 4050 Laptop GPU
  ```

- [ ] **Verificar sentence-transformers**
  ```powershell
  python -c "from sentence_transformers import SentenceTransformer; print('OK')"
  ```
  Esperado: `OK`

- [ ] **Verificar FAISS**
  ```powershell
  python -c "import faiss; print('FAISS version:', faiss.__version__)"
  ```
  Esperado: `FAISS version: 1.9.0`

- [ ] **Verificar Flask**
  ```powershell
  python -c "import flask; print('Flask version:', flask.__version__)"
  ```
  Esperado: `Flask version: 3.1.0`

---

## 🚀 Primera Ejecución

- [ ] **Crear índice inicial**
  ```powershell
  python crear_indice_inicial.py
  ```
  - Debe crear carpeta `indices_busqueda/`
  - Archivos: `faiss_index.bin`, `bm25_index.pkl`, `chunks.json`
  - Sin errores

- [ ] **Iniciar sistema completo**
  ```powershell
  .\INICIAR_BUSCADOR_TODO.ps1
  ```
  - Se abren 2 ventanas nuevas (servidor + frontend)
  - Navegador abre automáticamente en http://localhost:5174
  - Sin errores en las ventanas

- [ ] **Verificar servidor de búsqueda**
  ```powershell
  Invoke-WebRequest -Uri "http://localhost:5001/api/estado"
  ```
  Esperado:
  ```json
  {
    "gpu_disponible": true,
    "total_chunks": X,
    "archivos_indexados": Y
  }
  ```

- [ ] **Probar búsqueda desde API**
  ```powershell
  Invoke-WebRequest -Method POST -Uri "http://localhost:5001/api/buscar" -ContentType "application/json" -Body '{"query":"test","max_resultados":5}' | Select-Object -ExpandProperty Content
  ```
  - Debe retornar JSON con resultados
  - Campo "tiempo" debe ser < 2 segundos

- [ ] **Probar interfaz web**
  - Abrir http://localhost:5174
  - Ir a pestaña "Buscar"
  - Escribir "test" y presionar Enter
  - Deben aparecer resultados
  - Sin errores en consola del navegador (F12)

---

## 🎯 Funcionalidades Básicas

- [ ] **Búsqueda funciona**
  - Resultados aparecen en < 2 segundos
  - Muestra títulos/metadata en vez de rutas
  - Snippets de contenido visibles
  - Score de relevancia mostrado

- [ ] **Actualización de índice funciona**
  - Botón "🔄 Actualizar Índice" funciona
  - Botón "♻️ Reindexar Todo" funciona
  - Muestra estado: "Indexados: X archivos, Y chunks"

- [ ] **Navegación entre pestañas**
  - Cursos ✓
  - Notas ✓
  - Flashcards ✓
  - Buscar ✓

---

## 🔄 Reinicio del Sistema

- [ ] **Detener servicios**
  ```powershell
  .\DETENER_BUSCADOR.ps1
  ```
  - Confirma "✓ SERVICIOS DETENIDOS"
  - Puertos liberados

- [ ] **Reiniciar servicios**
  ```powershell
  .\INICIAR_BUSCADOR_TODO.ps1
  ```
  - Sistema inicia sin errores
  - Interfaz accesible nuevamente

---

## 📊 Verificación de Rendimiento

- [ ] **GPU en uso**
  En ventana del servidor debe decir:
  ```
  Modelo cargado en: cuda
  GPU disponible: NVIDIA GeForce RTX 4050 Laptop GPU
  ```

- [ ] **Tiempos de respuesta aceptables**
  - Primera búsqueda: < 5 segundos (carga modelo)
  - Búsquedas siguientes: < 1 segundo
  - Si es más lento, verificar que GPU esté activa

- [ ] **Uso de memoria**
  ```powershell
  Get-Process python | Where-Object {$_.Path -like "*Examinator*"} | Select-Object WorkingSet
  ```
  - Esperado: ~1-2GB con GPU
  - Si es >4GB, revisar configuración

---

## 🆘 Si Algo Falla

### GPU no detectada

```powershell
# Reinstalar PyTorch con CUDA
.\venv\Scripts\Activate.ps1
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Puerto ocupado

```powershell
# Ver qué proceso usa el puerto
netstat -ano | Select-String ":5001"
# Matar proceso
Stop-Process -Id <PID> -Force
```

### Servidor se cierra

```powershell
# Usar .bat en vez de PowerShell
.\INICIAR_BUSCADOR_GPU.bat
```

### Módulos no encontrados

```powershell
# Reinstalar dependencias
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Frontend no carga

```powershell
# Reinstalar node_modules
cd examinator-web
rm -r node_modules
rm package-lock.json
npm install
npm run dev
```

---

## 📚 Documentación de Referencia

- [ ] He leído: `GUIA_INSTALACION.md`
- [ ] He leído: `SOLUCIONES_PROBLEMAS.md`
- [ ] Conozco dónde está: `ARQUITECTURA_BUSQUEDA.md`
- [ ] Sé cómo ejecutar: `.\VERIFICAR_ENTORNO.ps1`
- [ ] Sé cómo iniciar: `.\INICIAR_BUSCADOR_TODO.ps1`
- [ ] Sé cómo detener: `.\DETENER_BUSCADOR.ps1`

---

## ✨ Sistema Listo

Si todos los checks están ✅, tu sistema está completamente configurado.

### Para uso diario:

1. Abrir PowerShell en carpeta del proyecto
2. Ejecutar: `.\INICIAR_BUSCADOR_TODO.ps1`
3. Esperar ~5 segundos
4. Usar interfaz en http://localhost:5174
5. Al terminar, cerrar ventanas o ejecutar `.\DETENER_BUSCADOR.ps1`

### Para agregar contenido nuevo:

1. Agregar archivos en `cursos/`, `notas/`, `flashcards/`
2. En interfaz → Pestaña "Buscar" → "🔄 Actualizar Índice"
3. Esperar ~10-30 segundos
4. ¡Listo para buscar!

---

**Fecha de instalación:** _________________  
**Versión Python:** _________________  
**GPU detectada:** _________________  
**Sistema funcional:** ☐ Sí  ☐ No  

---

*Guarda este checklist para futuras reinstalaciones*
