import { useState, useRef, useEffect } from 'react'

/**
 * Editor de Figuras Geométricas para Arte y Diseño
 * 
 * Permite crear y editar figuras geométricas:
 * - Círculos, cuadrados, rectángulos
 * - Triángulos, hexágonos, estrellas
 * - Líneas, flechas, puntos
 * - Ajuste de tamaño, color, posición
 */

const FIGURAS_DISPONIBLES = {
  circulo: {
    nombre: 'Círculo',
    icono: '⬤',
    svg: (props) => <circle cx={props.x} cy={props.y} r={props.size} fill={props.color} stroke={props.stroke} strokeWidth={props.strokeWidth} />,
    defaultProps: { size: 40 }
  },
  cuadrado: {
    nombre: 'Cuadrado',
    icono: '◼',
    svg: (props) => <rect x={props.x - props.size/2} y={props.y - props.size/2} width={props.size} height={props.size} fill={props.color} stroke={props.stroke} strokeWidth={props.strokeWidth} />,
    defaultProps: { size: 60 }
  },
  rectangulo: {
    nombre: 'Rectángulo',
    icono: '▬',
    svg: (props) => <rect x={props.x - props.width/2} y={props.y - props.height/2} width={props.width} height={props.height} fill={props.color} stroke={props.stroke} strokeWidth={props.strokeWidth} rx={props.radius || 0} />,
    defaultProps: { width: 80, height: 50, radius: 0 }
  },
  triangulo: {
    nombre: 'Triángulo',
    icono: '▲',
    svg: (props) => {
      const h = props.size * 0.866; // altura de triángulo equilátero
      const points = `${props.x},${props.y - h/2} ${props.x - props.size/2},${props.y + h/2} ${props.x + props.size/2},${props.y + h/2}`;
      return <polygon points={points} fill={props.color} stroke={props.stroke} strokeWidth={props.strokeWidth} />;
    },
    defaultProps: { size: 60 }
  },
  hexagono: {
    nombre: 'Hexágono',
    icono: '⬡',
    svg: (props) => {
      const r = props.size / 2;
      const points = Array.from({length: 6}, (_, i) => {
        const angle = (i * 60 - 30) * Math.PI / 180;
        return `${props.x + r * Math.cos(angle)},${props.y + r * Math.sin(angle)}`;
      }).join(' ');
      return <polygon points={points} fill={props.color} stroke={props.stroke} strokeWidth={props.strokeWidth} />;
    },
    defaultProps: { size: 60 }
  },
  pentagono: {
    nombre: 'Pentágono',
    icono: '⬠',
    svg: (props) => {
      const r = props.size / 2;
      const points = Array.from({length: 5}, (_, i) => {
        const angle = (i * 72 - 90) * Math.PI / 180;
        return `${props.x + r * Math.cos(angle)},${props.y + r * Math.sin(angle)}`;
      }).join(' ');
      return <polygon points={points} fill={props.color} stroke={props.stroke} strokeWidth={props.strokeWidth} />;
    },
    defaultProps: { size: 60 }
  },
  estrella: {
    nombre: 'Estrella',
    icono: '★',
    svg: (props) => {
      const outer = props.size / 2;
      const inner = outer * 0.4;
      const points = Array.from({length: 10}, (_, i) => {
        const r = i % 2 === 0 ? outer : inner;
        const angle = (i * 36 - 90) * Math.PI / 180;
        return `${props.x + r * Math.cos(angle)},${props.y + r * Math.sin(angle)}`;
      }).join(' ');
      return <polygon points={points} fill={props.color} stroke={props.stroke} strokeWidth={props.strokeWidth} />;
    },
    defaultProps: { size: 60 }
  },
  rombo: {
    nombre: 'Rombo',
    icono: '◆',
    svg: (props) => {
      const w = props.size / 2;
      const h = props.size * 0.7;
      const points = `${props.x},${props.y - h} ${props.x + w},${props.y} ${props.x},${props.y + h} ${props.x - w},${props.y}`;
      return <polygon points={points} fill={props.color} stroke={props.stroke} strokeWidth={props.strokeWidth} />;
    },
    defaultProps: { size: 50 }
  },
  linea: {
    nombre: 'Línea',
    icono: '━',
    svg: (props) => <line x1={props.x - props.length/2} y1={props.y} x2={props.x + props.length/2} y2={props.y} stroke={props.color} strokeWidth={props.strokeWidth} transform={`rotate(${props.rotation || 0} ${props.x} ${props.y})`} />,
    defaultProps: { length: 80, strokeWidth: 3, rotation: 0 }
  },
  flecha: {
    nombre: 'Flecha',
    icono: '➤',
    svg: (props) => {
      const halfLen = props.length / 2;
      const arrowSize = 10;
      return (
        <g transform={`rotate(${props.rotation || 0} ${props.x} ${props.y})`}>
          <line x1={props.x - halfLen} y1={props.y} x2={props.x + halfLen - arrowSize} y2={props.y} stroke={props.color} strokeWidth={props.strokeWidth} />
          <polygon points={`${props.x + halfLen},${props.y} ${props.x + halfLen - arrowSize},${props.y - arrowSize/2} ${props.x + halfLen - arrowSize},${props.y + arrowSize/2}`} fill={props.color} />
        </g>
      );
    },
    defaultProps: { length: 80, strokeWidth: 3, rotation: 0 }
  },
  punto: {
    nombre: 'Punto',
    icono: '●',
    svg: (props) => <circle cx={props.x} cy={props.y} r={props.size} fill={props.color} />,
    defaultProps: { size: 8 }
  },
  elipse: {
    nombre: 'Elipse',
    icono: '⬭',
    svg: (props) => <ellipse cx={props.x} cy={props.y} rx={props.width/2} ry={props.height/2} fill={props.color} stroke={props.stroke} strokeWidth={props.strokeWidth} />,
    defaultProps: { width: 80, height: 50 }
  }
};

const COLORES_RAPIDOS = [
  '#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4', 
  '#3b82f6', '#8b5cf6', '#ec4899', '#000000', '#ffffff',
  '#6b7280', '#a855f7', '#14b8a6', '#f43f5e', '#84cc16'
];

const ShapeEditor = ({ value, onChange, onInsert }) => {
  const canvasRef = useRef(null);
  const [figuras, setFiguras] = useState([]);
  const [figuraSeleccionada, setFiguraSeleccionada] = useState(null);
  const [herramientaActiva, setHerramientaActiva] = useState('circulo');
  const [colorActivo, setColorActivo] = useState('#3b82f6');
  const [strokeActivo, setStrokeActivo] = useState('#1e40af');
  const [strokeWidth, setStrokeWidth] = useState(2);
  const [isDragging, setIsDragging] = useState(false);
  const [canvasSize] = useState({ width: 400, height: 300 });

  // Parsear valor inicial si existe
  useEffect(() => {
    if (value && typeof value === 'string') {
      try {
        const parsed = JSON.parse(value);
        if (Array.isArray(parsed)) {
          setFiguras(parsed);
        }
      } catch (e) {
        // valor no es JSON válido, ignorar
      }
    }
  }, []);

  // Actualizar valor cuando cambian las figuras
  useEffect(() => {
    if (figuras.length > 0) {
      onChange?.(JSON.stringify(figuras));
    }
  }, [figuras, onChange]);

  const handleCanvasClick = (e) => {
    if (isDragging) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const nuevaFigura = {
      id: Date.now(),
      tipo: herramientaActiva,
      x,
      y,
      color: colorActivo,
      stroke: strokeActivo,
      strokeWidth,
      ...FIGURAS_DISPONIBLES[herramientaActiva].defaultProps
    };

    setFiguras([...figuras, nuevaFigura]);
    setFiguraSeleccionada(nuevaFigura.id);
  };

  const handleFiguraClick = (e, id) => {
    e.stopPropagation();
    setFiguraSeleccionada(id);
  };

  const actualizarFigura = (id, cambios) => {
    setFiguras(figuras.map(f => f.id === id ? { ...f, ...cambios } : f));
  };

  const eliminarFigura = (id) => {
    setFiguras(figuras.filter(f => f.id !== id));
    if (figuraSeleccionada === id) {
      setFiguraSeleccionada(null);
    }
  };

  const figuraActual = figuras.find(f => f.id === figuraSeleccionada);

  // Generar descripción textual para guardar
  const generarDescripcion = () => {
    if (figuras.length === 0) return '';
    
    const desc = figuras.map(f => {
      const nombre = FIGURAS_DISPONIBLES[f.tipo]?.nombre || f.tipo;
      const icono = FIGURAS_DISPONIBLES[f.tipo]?.icono || '?';
      return `${icono} ${nombre} (${f.color}, pos: ${Math.round(f.x)},${Math.round(f.y)})`;
    }).join('\n');
    
    return `📐 Composición Geométrica:\n${desc}`;
  };

  const exportarComoTexto = () => {
    const desc = generarDescripcion();
    onInsert?.(desc);
  };

  return (
    <div style={{
      background: 'rgba(17, 24, 39, 0.95)',
      borderRadius: '12px',
      padding: '1rem',
      border: '1px solid rgba(139, 92, 246, 0.3)'
    }}>
      {/* Barra de herramientas de figuras */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '0.5rem',
        marginBottom: '1rem',
        padding: '0.75rem',
        background: 'rgba(139, 92, 246, 0.1)',
        borderRadius: '8px'
      }}>
        {Object.entries(FIGURAS_DISPONIBLES).map(([key, fig]) => (
          <button
            key={key}
            type="button"
            onClick={() => setHerramientaActiva(key)}
            style={{
              padding: '0.5rem 0.75rem',
              background: herramientaActiva === key 
                ? 'linear-gradient(135deg, #8b5cf6, #7c3aed)'
                : 'rgba(139, 92, 246, 0.2)',
              color: herramientaActiva === key ? '#fff' : '#c4b5fd',
              border: herramientaActiva === key 
                ? '1px solid #a855f7'
                : '1px solid rgba(139, 92, 246, 0.3)',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              transition: 'all 0.2s'
            }}
            title={fig.nombre}
          >
            <span style={{ fontSize: '1.1rem' }}>{fig.icono}</span>
            <span>{fig.nombre}</span>
          </button>
        ))}
      </div>

      {/* Selector de colores */}
      <div style={{
        display: 'flex',
        gap: '1rem',
        marginBottom: '1rem',
        alignItems: 'center',
        flexWrap: 'wrap'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ color: '#c4b5fd', fontSize: '0.85rem' }}>Relleno:</span>
          <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
            {COLORES_RAPIDOS.map(c => (
              <button
                key={c}
                type="button"
                onClick={() => setColorActivo(c)}
                style={{
                  width: '24px',
                  height: '24px',
                  background: c,
                  border: colorActivo === c ? '3px solid #fff' : '2px solid rgba(255,255,255,0.3)',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  boxShadow: colorActivo === c ? `0 0 8px ${c}` : 'none'
                }}
              />
            ))}
            <input
              type="color"
              value={colorActivo}
              onChange={(e) => setColorActivo(e.target.value)}
              style={{ width: '24px', height: '24px', cursor: 'pointer', border: 'none' }}
            />
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ color: '#c4b5fd', fontSize: '0.85rem' }}>Borde:</span>
          <div style={{ display: 'flex', gap: '4px' }}>
            {['#000000', '#ffffff', '#1e40af', '#dc2626', '#059669'].map(c => (
              <button
                key={c}
                type="button"
                onClick={() => setStrokeActivo(c)}
                style={{
                  width: '20px',
                  height: '20px',
                  background: c,
                  border: strokeActivo === c ? '2px solid #a855f7' : '1px solid rgba(255,255,255,0.3)',
                  borderRadius: '3px',
                  cursor: 'pointer'
                }}
              />
            ))}
          </div>
          <input
            type="range"
            min="0"
            max="8"
            value={strokeWidth}
            onChange={(e) => setStrokeWidth(Number(e.target.value))}
            style={{ width: '60px' }}
          />
          <span style={{ color: '#94a3b8', fontSize: '0.75rem' }}>{strokeWidth}px</span>
        </div>
      </div>

      {/* Canvas SVG */}
      <div style={{
        display: 'flex',
        gap: '1rem',
        flexWrap: 'wrap'
      }}>
        <div style={{
          background: '#fff',
          borderRadius: '8px',
          overflow: 'hidden',
          border: '2px solid rgba(139, 92, 246, 0.3)',
          cursor: 'crosshair'
        }}>
          <svg
            ref={canvasRef}
            width={canvasSize.width}
            height={canvasSize.height}
            onClick={handleCanvasClick}
            style={{ display: 'block' }}
          >
            {/* Cuadrícula de fondo */}
            <defs>
              <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e5e7eb" strokeWidth="0.5"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
            
            {/* Figuras */}
            {figuras.map(fig => {
              const FigSvg = FIGURAS_DISPONIBLES[fig.tipo]?.svg;
              if (!FigSvg) return null;
              
              return (
                <g
                  key={fig.id}
                  onClick={(e) => handleFiguraClick(e, fig.id)}
                  style={{ cursor: 'pointer' }}
                >
                  <FigSvg {...fig} />
                  {figuraSeleccionada === fig.id && (
                    <rect
                      x={fig.x - 35}
                      y={fig.y - 35}
                      width={70}
                      height={70}
                      fill="none"
                      stroke="#8b5cf6"
                      strokeWidth="2"
                      strokeDasharray="4,2"
                    />
                  )}
                </g>
              );
            })}
          </svg>
        </div>

        {/* Panel de propiedades */}
        {figuraActual && (
          <div style={{
            background: 'rgba(139, 92, 246, 0.1)',
            borderRadius: '8px',
            padding: '1rem',
            minWidth: '200px',
            border: '1px solid rgba(139, 92, 246, 0.3)'
          }}>
            <div style={{
              color: '#e9d5ff',
              fontWeight: '600',
              marginBottom: '1rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span>{FIGURAS_DISPONIBLES[figuraActual.tipo]?.icono} {FIGURAS_DISPONIBLES[figuraActual.tipo]?.nombre}</span>
              <button
                type="button"
                onClick={() => eliminarFigura(figuraActual.id)}
                style={{
                  background: 'rgba(239, 68, 68, 0.2)',
                  color: '#fca5a5',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  borderRadius: '4px',
                  padding: '2px 8px',
                  fontSize: '0.75rem',
                  cursor: 'pointer'
                }}
              >
                🗑️ Eliminar
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {/* Tamaño */}
              {figuraActual.size !== undefined && (
                <div>
                  <label style={{ color: '#c4b5fd', fontSize: '0.8rem', display: 'block', marginBottom: '4px' }}>
                    Tamaño: {figuraActual.size}px
                  </label>
                  <input
                    type="range"
                    min="10"
                    max="100"
                    value={figuraActual.size}
                    onChange={(e) => actualizarFigura(figuraActual.id, { size: Number(e.target.value) })}
                    style={{ width: '100%' }}
                  />
                </div>
              )}

              {/* Ancho/Alto para rectángulos */}
              {figuraActual.width !== undefined && (
                <>
                  <div>
                    <label style={{ color: '#c4b5fd', fontSize: '0.8rem', display: 'block', marginBottom: '4px' }}>
                      Ancho: {figuraActual.width}px
                    </label>
                    <input
                      type="range"
                      min="20"
                      max="150"
                      value={figuraActual.width}
                      onChange={(e) => actualizarFigura(figuraActual.id, { width: Number(e.target.value) })}
                      style={{ width: '100%' }}
                    />
                  </div>
                  <div>
                    <label style={{ color: '#c4b5fd', fontSize: '0.8rem', display: 'block', marginBottom: '4px' }}>
                      Alto: {figuraActual.height}px
                    </label>
                    <input
                      type="range"
                      min="20"
                      max="150"
                      value={figuraActual.height}
                      onChange={(e) => actualizarFigura(figuraActual.id, { height: Number(e.target.value) })}
                      style={{ width: '100%' }}
                    />
                  </div>
                </>
              )}

              {/* Longitud para líneas */}
              {figuraActual.length !== undefined && (
                <div>
                  <label style={{ color: '#c4b5fd', fontSize: '0.8rem', display: 'block', marginBottom: '4px' }}>
                    Longitud: {figuraActual.length}px
                  </label>
                  <input
                    type="range"
                    min="20"
                    max="200"
                    value={figuraActual.length}
                    onChange={(e) => actualizarFigura(figuraActual.id, { length: Number(e.target.value) })}
                    style={{ width: '100%' }}
                  />
                </div>
              )}

              {/* Rotación para líneas/flechas */}
              {figuraActual.rotation !== undefined && (
                <div>
                  <label style={{ color: '#c4b5fd', fontSize: '0.8rem', display: 'block', marginBottom: '4px' }}>
                    Rotación: {figuraActual.rotation}°
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="360"
                    value={figuraActual.rotation}
                    onChange={(e) => actualizarFigura(figuraActual.id, { rotation: Number(e.target.value) })}
                    style={{ width: '100%' }}
                  />
                </div>
              )}

              {/* Color de relleno */}
              <div>
                <label style={{ color: '#c4b5fd', fontSize: '0.8rem', display: 'block', marginBottom: '4px' }}>
                  Color
                </label>
                <input
                  type="color"
                  value={figuraActual.color}
                  onChange={(e) => actualizarFigura(figuraActual.id, { color: e.target.value })}
                  style={{ width: '100%', height: '30px', cursor: 'pointer', border: 'none', borderRadius: '4px' }}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Botones de acción */}
      <div style={{
        display: 'flex',
        gap: '0.75rem',
        marginTop: '1rem',
        flexWrap: 'wrap'
      }}>
        <button
          type="button"
          onClick={() => setFiguras([])}
          style={{
            padding: '0.5rem 1rem',
            background: 'rgba(239, 68, 68, 0.2)',
            color: '#fca5a5',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '0.85rem'
          }}
        >
          🗑️ Limpiar todo
        </button>
        
        <button
          type="button"
          onClick={exportarComoTexto}
          disabled={figuras.length === 0}
          style={{
            padding: '0.5rem 1rem',
            background: figuras.length > 0 
              ? 'linear-gradient(135deg, #8b5cf6, #7c3aed)'
              : 'rgba(139, 92, 246, 0.2)',
            color: figuras.length > 0 ? '#fff' : '#9ca3af',
            border: 'none',
            borderRadius: '6px',
            cursor: figuras.length > 0 ? 'pointer' : 'not-allowed',
            fontSize: '0.85rem',
            fontWeight: '600'
          }}
        >
          ✅ Insertar ({figuras.length} figuras)
        </button>

        <div style={{
          marginLeft: 'auto',
          color: '#94a3b8',
          fontSize: '0.8rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <span>💡 Click en el canvas para agregar figuras</span>
        </div>
      </div>
    </div>
  );
};

export default ShapeEditor;
