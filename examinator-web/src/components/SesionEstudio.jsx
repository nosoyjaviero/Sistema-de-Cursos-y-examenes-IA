import React, { useState, useEffect } from 'react';
import './SesionEstudio.css';

function SesionEstudio() {
  const [sesion, setSesion] = useState(null);
  const [estadisticas, setEstadisticas] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [maxErrores, setMaxErrores] = useState(10);

  useEffect(() => {
    cargarDatos();
  }, [maxErrores]);

  const cargarDatos = async () => {
    setLoading(true);
    try {
      // Cargar sesión de estudio
      const resSesion = await fetch(`http://localhost:8000/api/errores/sesion-estudio?max_errores=${maxErrores}`);
      const dataSesion = await resSesion.json();
      setSesion(dataSesion);

      // Cargar estadísticas
      const resStats = await fetch('http://localhost:8000/api/errores/estadisticas');
      const dataStats = await resStats.json();
      setEstadisticas(dataStats);

      setError(null);
    } catch (err) {
      console.error('Error cargando datos:', err);
      setError('No se pudieron cargar los errores. Asegúrate de que el servidor esté ejecutándose.');
    } finally {
      setLoading(false);
    }
  };

  const marcarResuelto = async (errorId) => {
    try {
      await fetch(`http://localhost:8000/api/errores/marcar-resuelto/${errorId}`, {
        method: 'POST'
      });
      
      // Recargar datos
      cargarDatos();
      
      alert('✅ Error marcado como resuelto');
    } catch (err) {
      console.error('Error marcando como resuelto:', err);
      alert('❌ Error al marcar como resuelto');
    }
  };

  if (loading) {
    return (
      <div className="sesion-estudio">
        <div className="loading">
          <div className="spinner"></div>
          <p>Cargando sesión de estudio...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="sesion-estudio">
        <div className="error-message">
          <h3>⚠️ Error</h3>
          <p>{error}</p>
          <button onClick={cargarDatos}>🔄 Reintentar</button>
        </div>
      </div>
    );
  }

  if (!sesion || sesion.total_errores_seleccionados === 0) {
    return (
      <div className="sesion-estudio">
        <div className="sin-errores">
          <h2>🎉 ¡No tienes errores pendientes!</h2>
          <p>Sigue practicando para mantener tu nivel.</p>
          {estadisticas && (
            <div className="stats-resueltos">
              <p>✅ Errores resueltos: {estadisticas.por_estado.resueltos}</p>
              <p>📊 Tasa de resolución: {estadisticas.tasa_resolucion}%</p>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="sesion-estudio">
      <div className="header">
        <h1>🎯 Sesión de Estudio Personalizada</h1>
        <p className="fecha">📅 {new Date(sesion.fecha_sesion).toLocaleDateString('es-ES')}</p>
      </div>

      {/* Mensaje motivacional */}
      <div className="mensaje-motivacional">
        <p>{sesion.mensaje_motivacional}</p>
      </div>

      {/* Estadísticas del banco */}
      {estadisticas && (
        <div className="estadisticas-banco">
          <h3>📊 Tu Banco de Errores</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{estadisticas.total_errores}</div>
              <div className="stat-label">Total Errores</div>
            </div>
            <div className="stat-card active">
              <div className="stat-value">{estadisticas.errores_activos}</div>
              <div className="stat-label">Activos</div>
            </div>
            <div className="stat-card resolved">
              <div className="stat-value">{estadisticas.por_estado.resueltos}</div>
              <div className="stat-label">Resueltos</div>
            </div>
            <div className="stat-card rate">
              <div className="stat-value">{estadisticas.tasa_resolucion}%</div>
              <div className="stat-label">Tasa Resolución</div>
            </div>
          </div>
        </div>
      )}

      {/* Composición de la sesión */}
      <div className="composicion-sesion">
        <h3>📋 Composición de la Sesión</h3>
        <div className="composition-chips">
          <span className="chip nuevos">
            ⚠️ {sesion.estadisticas_sesion.errores_nuevos_incluidos} Nuevos
          </span>
          <span className="chip alta-frecuencia">
            🔴 {sesion.estadisticas_sesion.errores_alta_frecuencia} Alta Frecuencia
          </span>
          <span className="chip antiguos">
            📅 {sesion.estadisticas_sesion.errores_antiguos} Antiguos (&gt;7 días)
          </span>
          <span className="chip promedio">
            ⏱️ {sesion.estadisticas_sesion.promedio_dias_sin_practica} días promedio
          </span>
        </div>
      </div>

      {/* Control de cantidad */}
      <div className="controles">
        <label>
          Errores a mostrar:
          <select value={maxErrores} onChange={(e) => setMaxErrores(Number(e.target.value))}>
            <option value={5}>5 errores</option>
            <option value={10}>10 errores</option>
            <option value={15}>15 errores</option>
            <option value={20}>20 errores</option>
          </select>
        </label>
        <button onClick={cargarDatos} className="btn-refresh">🔄 Actualizar</button>
      </div>

      {/* Lista de errores */}
      <div className="lista-errores">
        <h3>🎓 Errores a Practicar Hoy ({sesion.total_errores_seleccionados})</h3>
        
        {sesion.errores.map((error, index) => (
          <div key={error.id_error} className={`error-card prioridad-${error.prioridad}`}>
            <div className="error-header">
              <span className="error-numero">#{index + 1}</span>
              <span className="error-tipo">{error.pregunta.tipo.toUpperCase()}</span>
              <span className={`estado-badge ${error.estado_refuerzo}`}>
                {error.estado_refuerzo === 'nuevo_error' && '⚠️ Nuevo'}
                {error.estado_refuerzo === 'en_refuerzo' && '🔄 En Refuerzo'}
                {error.estado_refuerzo === 'resuelto' && '✅ Resuelto'}
              </span>
              <span className={`prioridad-badge ${error.prioridad}`}>
                {error.prioridad === 'alta' && '🔴 Alta'}
                {error.prioridad === 'media' && '🟡 Media'}
                {error.prioridad === 'baja' && '🟢 Baja'}
              </span>
            </div>

            <div className="error-contenido">
              <h4>{error.pregunta.texto}</h4>
              
              {/* Opciones si es multiple choice */}
              {error.pregunta.opciones && error.pregunta.opciones.length > 0 && (
                <div className="opciones">
                  {error.pregunta.opciones.map((opcion, idx) => (
                    <div 
                      key={idx} 
                      className={`opcion ${opcion === error.pregunta.respuesta_correcta ? 'correcta' : ''}`}
                    >
                      {String.fromCharCode(65 + idx)}. {opcion}
                      {opcion === error.pregunta.respuesta_correcta && ' ✓'}
                    </div>
                  ))}
                </div>
              )}

              {/* Respuesta correcta para otras */}
              {(!error.pregunta.opciones || error.pregunta.opciones.length === 0) && error.pregunta.respuesta_correcta && (
                <div className="respuesta-correcta">
                  <strong>Respuesta correcta:</strong>
                  <p>{error.pregunta.respuesta_correcta}</p>
                </div>
              )}
            </div>

            <div className="error-metadata">
              <div className="metadata-item">
                <span className="label">📊 Veces fallada:</span>
                <span className="value">{error.veces_fallada}</span>
              </div>
              <div className="metadata-item">
                <span className="label">📅 Días sin práctica:</span>
                <span className="value">{error.dias_sin_practica}</span>
              </div>
              <div className="metadata-item">
                <span className="label">📚 Origen:</span>
                <span className="value">{error.examen_origen.carpeta_ruta}</span>
              </div>
            </div>

            <div className="error-razon">
              <strong>📍 ¿Por qué practicar esto?</strong>
              <p>{error.razon_seleccion}</p>
            </div>

            <div className="error-recomendacion">
              <strong>💡 Recomendación:</strong>
              <p>{error.recomendacion_estudio}</p>
            </div>

            <div className="error-acciones">
              <button 
                onClick={() => marcarResuelto(error.id_error)}
                className="btn-resolver"
              >
                ✅ Marcar como Resuelto
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SesionEstudio;
