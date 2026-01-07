# Instrucciones para Implementar Buscador IA

## Paso 1: Instalar Dependencias de Python

```powershell
cd C:\Users\Fela\Documents\Proyectos\Examinator
pip install sentence-transformers torch faiss-gpu PyPDF2 rank-bm25 flask flask-cors
```

## Paso 2: Crear Índice Inicial

```python
# Ejecutar una sola vez para crear el índice
from buscador_ia import ConfigBuscador, IndexadorLocal

config = ConfigBuscador()
indexador = IndexadorLocal(config)

# Indexar todo
archivos, chunks = indexador.indexar(incremental=False)
print(f"✅ Indexados {archivos} archivos, {chunks} chunks")
```

Guarda esto como `crear_indice_inicial.py` y ejecútalo:
```powershell
python crear_indice_inicial.py
```

## Paso 3: Iniciar Servidor de Búsqueda

```powershell
python api_buscador.py
```

El servidor estará en `http://localhost:5001`

## Paso 4: Agregar Funciones en App.jsx

**Ubicación**: Después de `navegarRutaFlashcards` (línea ~7530)

Copiar el contenido de `funciones_buscador.jsx` completo.

## Paso 5: Agregar Sección UI en App.jsx

**Ubicación**: Después de la sección de Calendario (donde dice `{selectedMenu === 'historial' && ...}`)

Agregar esta sección completa:

```jsx
        {selectedMenu === 'buscar' && (
          <div className="content-section">
            <h1>🔍 Buscador IA</h1>
            
            {/* Estado del Índice */}
            {estadoIndice && (
              <div className="info-indice">
                <div className="info-indice-stats">
                  <span>📊 {estadoIndice.total_chunks} chunks indexados</span>
                  <span>📁 {estadoIndice.total_archivos} archivos</span>
                  <span>🎮 GPU: {estadoIndice.gpu_disponible ? estadoIndice.gpu_nombre : 'CPU'}</span>
                </div>
              </div>
            )}
            
            {/* Barra de Búsqueda */}
            <div className="buscador-container">
              <div className="buscador-input-grupo">
                <input
                  type="text"
                  className="buscador-input"
                  placeholder="Busca en todos tus documentos, notas, flashcards, exámenes..."
                  value={queryBusqueda}
                  onChange={(e) => setQueryBusqueda(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') buscarConIA();
                  }}
                />
                <button 
                  className="btn-buscar"
                  onClick={buscarConIA}
                  disabled={buscando}
                >
                  {buscando ? '🔄 Buscando...' : '🔍 Buscar'}
                </button>
              </div>
              
              {/* Filtros */}
              <div className="buscador-filtros">
                <span>Tipo:</span>
                <select 
                  value={filtroBusquedaTipo}
                  onChange={(e) => setFiltroBusquedaTipo(e.target.value)}
                >
                  <option value="todos">Todos</option>
                  <option value="nota">Notas</option>
                  <option value="flashcard">Flashcards</option>
                  <option value="examen">Exámenes</option>
                  <option value="practica">Prácticas</option>
                  <option value="curso">Cursos</option>
                  <option value="documento">Documentos</option>
                </select>
                
                <button 
                  className="btn-actualizar-indice"
                  onClick={() => actualizarIndice(false)}
                  disabled={actualizandoIndice}
                  title="Actualizar índice (solo nuevos archivos)"
                >
                  {actualizandoIndice ? '🔄 Actualizando...' : '🔄 Actualizar Índice'}
                </button>
                
                <button 
                  className="btn-reindexar"
                  onClick={() => {
                    if (confirm('¿Reindexar todo? Esto puede tardar varios minutos.')) {
                      actualizarIndice(true);
                    }
                  }}
                  disabled={actualizandoIndice}
                  title="Reindexar todo desde cero"
                >
                  🔥 Reindexar Todo
                </button>
              </div>
            </div>
            
            {/* Resultados */}
            {resultadosBusqueda.length > 0 && (
              <div className="resultados-busqueda">
                <h2>📋 Resultados ({resultadosBusqueda.length})</h2>
                
                <div className="lista-resultados">
                  {resultadosBusqueda.map((resultado, idx) => (
                    <div key={idx} className="resultado-item">
                      <div className="resultado-header">
                        <span className={`resultado-tipo tipo-${resultado.tipo}`}>
                          {resultado.tipo === 'nota' && '📝'}
                          {resultado.tipo === 'flashcard' && '🎴'}
                          {resultado.tipo === 'examen' && '📝'}
                          {resultado.tipo === 'practica' && '🎯'}
                          {resultado.tipo === 'curso' && '📚'}
                          {resultado.tipo === 'documento' && '📄'}
                          {' '}
                          {resultado.tipo}
                        </span>
                        <span className="resultado-score">
                          Score: {resultado.score}
                        </span>
                      </div>
                      
                      <h3 className="resultado-nombre">{resultado.nombre}</h3>
                      
                      <div className="resultado-snippet">
                        {resultado.snippet}
                      </div>
                      
                      <div className="resultado-footer">
                        <span className="resultado-ruta">
                          📁 {resultado.ruta}
                        </span>
                        <span className="resultado-chunk">
                          Fragmento {resultado.chunk_id + 1}/{resultado.total_chunks}
                        </span>
                        <button 
                          className="btn-abrir-archivo"
                          onClick={() => abrirArchivoBusqueda(resultado.ruta)}
                        >
                          📂 Abrir
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Mensaje cuando no hay resultados */}
            {resultadosBusqueda.length === 0 && queryBusqueda && !buscando && (
              <div className="sin-resultados">
                <p>🔍 No se encontraron resultados para "{queryBusqueda}"</p>
                <p>Intenta con otros términos o actualiza el índice si agregaste archivos nuevos.</p>
              </div>
            )}
            
            {/* Información inicial */}
            {!queryBusqueda && (
              <div className="buscador-info-inicial">
                <h2>💡 Cómo usar el buscador</h2>
                <ul>
                  <li>🔍 <strong>Búsqueda semántica:</strong> Escribe en lenguaje natural (ej: "fotosíntesis en plantas")</li>
                  <li>🎯 <strong>Keywords:</strong> Usa palabras clave específicas (ej: "mitocondria ATP energía")</li>
                  <li>🏷️ <strong>Filtra por tipo:</strong> Notas, flashcards, exámenes, etc.</li>
                  <li>🔄 <strong>Actualizar índice:</strong> Ejecuta después de agregar nuevos archivos</li>
                  <li>📂 <strong>Abrir archivo:</strong> Click en "Abrir" para ir directamente al archivo</li>
                </ul>
                
                <div className="buscador-ejemplos">
                  <h3>Ejemplos de búsqueda:</h3>
                  <div className="ejemplo-chips">
                    <button onClick={() => setQueryBusqueda('qué es la fotosíntesis')}>
                      qué es la fotosíntesis
                    </button>
                    <button onClick={() => setQueryBusqueda('fórmulas de física cinemática')}>
                      fórmulas de física cinemática
                    </button>
                    <button onClick={() => setQueryBusqueda('definición de función matemática')}>
                      definición de función matemática
                    </button>
                    <button onClick={() => setQueryBusqueda('verbos irregulares inglés')}>
                      verbos irregulares inglés
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
```

## Paso 6: Agregar CSS

Agregar al final de `App.css`:

```css
/* ================================================
   BUSCADOR IA
   ================================================ */

.info-indice {
  background: linear-gradient(135deg, rgba(100, 108, 255, 0.1) 0%, rgba(100, 108, 255, 0.05) 100%);
  border: 2px solid rgba(100, 108, 255, 0.3);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 2rem;
}

.info-indice-stats {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
  font-size: 0.95rem;
  color: #94a3b8;
}

.info-indice-stats span {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.buscador-container {
  background: rgba(30, 35, 50, 0.5);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.buscador-input-grupo {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.buscador-input {
  flex: 1;
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: white;
  font-size: 1rem;
  transition: all 0.3s;
}

.buscador-input:focus {
  outline: none;
  border-color: #646cff;
  background: rgba(255, 255, 255, 0.08);
}

.btn-buscar {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #646cff 0%, #535bf2 100%);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.btn-buscar:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(100, 108, 255, 0.4);
}

.btn-buscar:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.buscador-filtros {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.buscador-filtros select {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: white;
  cursor: pointer;
}

.btn-actualizar-indice,
.btn-reindexar {
  padding: 0.5rem 1rem;
  background: rgba(16, 185, 129, 0.2);
  border: 1px solid rgba(16, 185, 129, 0.4);
  border-radius: 8px;
  color: #10b981;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.9rem;
}

.btn-reindexar {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.4);
  color: #ef4444;
}

.btn-actualizar-indice:hover:not(:disabled),
.btn-reindexar:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.btn-actualizar-indice:disabled,
.btn-reindexar:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Resultados */
.resultados-busqueda {
  margin-top: 2rem;
}

.lista-resultados {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.resultado-item {
  background: rgba(30, 35, 50, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 1.5rem;
  transition: all 0.3s;
}

.resultado-item:hover {
  border-color: #646cff;
  box-shadow: 0 4px 12px rgba(100, 108, 255, 0.2);
}

.resultado-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.resultado-tipo {
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
}

.tipo-nota {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(251, 191, 36, 0.4);
}

.tipo-flashcard {
  background: rgba(139, 92, 246, 0.2);
  color: #8b5cf6;
  border: 1px solid rgba(139, 92, 246, 0.4);
}

.tipo-examen {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.4);
}

.tipo-practica {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.4);
}

.tipo-curso {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.4);
}

.tipo-documento {
  background: rgba(148, 163, 184, 0.2);
  color: #94a3b8;
  border: 1px solid rgba(148, 163, 184, 0.4);
}

.resultado-score {
  font-size: 0.85rem;
  color: #94a3b8;
}

.resultado-nombre {
  color: white;
  font-size: 1.1rem;
  margin-bottom: 0.75rem;
}

.resultado-snippet {
  color: #cbd5e1;
  line-height: 1.6;
  margin-bottom: 1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
  font-size: 0.95rem;
}

.resultado-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  font-size: 0.85rem;
  color: #94a3b8;
}

.resultado-ruta {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-abrir-archivo {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #646cff 0%, #535bf2 100%);
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.85rem;
  font-weight: 600;
}

.btn-abrir-archivo:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(100, 108, 255, 0.4);
}

/* Sin resultados */
.sin-resultados {
  text-align: center;
  padding: 3rem;
  color: #94a3b8;
}

/* Info inicial */
.buscador-info-inicial {
  background: rgba(30, 35, 50, 0.4);
  border-radius: 12px;
  padding: 2rem;
  margin-top: 2rem;
}

.buscador-info-inicial h2 {
  color: #646cff;
  margin-bottom: 1rem;
}

.buscador-info-inicial ul {
  list-style: none;
  padding: 0;
}

.buscador-info-inicial li {
  padding: 0.75rem 0;
  color: #cbd5e1;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.buscador-ejemplos {
  margin-top: 2rem;
}

.buscador-ejemplos h3 {
  color: white;
  margin-bottom: 1rem;
}

.ejemplo-chips {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.ejemplo-chips button {
  padding: 0.5rem 1rem;
  background: rgba(100, 108, 255, 0.1);
  border: 1px solid rgba(100, 108, 255, 0.3);
  border-radius: 20px;
  color: #646cff;
  cursor: pointer;
  transition: all 0.3s;
}

.ejemplo-chips button:hover {
  background: rgba(100, 108, 255, 0.2);
  border-color: #646cff;
  transform: translateY(-2px);
}

/* Responsive */
@media (max-width: 768px) {
  .buscador-input-grupo {
    flex-direction: column;
  }
  
  .buscador-filtros {
    flex-direction: column;
    align-items: stretch;
  }
  
  .resultado-footer {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .ejemplo-chips {
    flex-direction: column;
  }
}
```

## Paso 7: Configurar Rutas

Editar `buscador_ia.py` líneas 43-47 con tus rutas reales:

```python
CARPETAS_RAIZ = [
    r"C:\Users\Fela\Documents\Proyectos\Examinator\cursos",
    r"C:\Users\Fela\Documents\Proyectos\Examinator\notas",
    # ... tus carpetas
]
```

## Paso 8: Probar

1. Iniciar API: `python api_buscador.py`
2. Iniciar frontend: `npm run dev`
3. Ir a pestaña "🔍 Buscar"
4. Buscar algo!

## Notas Importantes

- Primera indexación puede tardar 5-30 min dependiendo de archivos
- GPU se usa automáticamente si está disponible
- El índice se guarda en `C:\Users\Fela\Documents\Proyectos\Examinator\indice_busqueda`
- Actualizar índice solo procesa archivos nuevos/modificados
- Reindexar todo solo si cambias el modelo de embeddings

## Solución de Problemas

**Error: ModuleNotFoundError**
```powershell
pip install sentence-transformers torch faiss-gpu PyPDF2 rank-bm25 flask flask-cors
```

**Error: CUDA no disponible**
- Verifica drivers NVIDIA
- O cambia `USAR_GPU = False` en ConfigBuscador

**Error: Servidor no responde**
- Verifica que `python api_buscador.py` esté corriendo
- Comprueba puerto 5001 no esté en uso

**Sin resultados**
- Ejecuta "🔄 Actualizar Índice" primero
- Verifica que las rutas en CARPETAS_RAIZ existan
