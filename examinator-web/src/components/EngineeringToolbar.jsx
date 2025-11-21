import { useState } from 'react';

const EngineeringToolbar = ({ onInsertComponent }) => {
  const [activeTab, setActiveTab] = useState('circuitos');

  const COMPONENTES_INGENIERIA = {
    circuitos: [
      { nombre: 'Resistencia', svg: '<circle cx="20" cy="20" r="3" fill="none" stroke="currentColor"/><path d="M 5 20 L 17 20 M 23 20 L 35 20 M 17 14 L 23 14 L 23 26 L 17 26 Z" stroke="currentColor" fill="none"/>', latex: 'R = \\square \\, \\Omega', descripcion: 'Resistor' },
      { nombre: 'Capacitor', svg: '<path d="M 5 20 L 17 20 M 17 12 L 17 28 M 23 12 L 23 28 M 23 20 L 35 20" stroke="currentColor" fill="none"/>', latex: 'C = \\square \\, \\mu F', descripcion: 'Condensador' },
      { nombre: 'Inductor', svg: '<path d="M 5 20 L 10 20 Q 12 15 15 20 Q 18 25 20 20 Q 22 15 25 20 Q 28 25 30 20 L 35 20" stroke="currentColor" fill="none"/>', latex: 'L = \\square \\, mH', descripcion: 'Bobina' },
      { nombre: 'Fuente DC', svg: '<circle cx="20" cy="20" r="12" fill="none" stroke="currentColor"/><path d="M 15 20 L 25 20 M 20 15 L 20 25" stroke="currentColor"/>', latex: 'V = \\square \\, V', descripcion: 'Voltaje continuo' },
      { nombre: 'Fuente AC', svg: '<circle cx="20" cy="20" r="12" fill="none" stroke="currentColor"/><path d="M 12 20 Q 16 14 20 20 Q 24 26 28 20" stroke="currentColor" fill="none"/>', latex: 'V = \\square \\sin(\\omega t)', descripcion: 'Voltaje alterno' },
      { nombre: 'Batería', svg: '<path d="M 5 20 L 15 20 M 15 12 L 15 28 M 18 15 L 18 25 M 18 20 L 35 20" stroke="currentColor" fill="none"/>', latex: 'V = \\square \\, V', descripcion: 'Pila/Batería' },
      { nombre: 'Diodo', svg: '<path d="M 5 20 L 17 20 M 23 20 L 35 20 M 17 12 L 17 28 L 23 20 Z" stroke="currentColor" fill="currentColor"/>', latex: 'D', descripcion: 'Diodo rectificador' },
      { nombre: 'LED', svg: '<path d="M 5 20 L 17 20 M 23 20 L 35 20 M 17 12 L 17 28 L 23 20 Z M 24 14 L 28 10 M 24 18 L 28 14" stroke="currentColor" fill="currentColor"/>', latex: 'LED', descripcion: 'Diodo emisor de luz' },
      { nombre: 'Tierra', svg: '<path d="M 20 5 L 20 20 M 12 20 L 28 20 M 14 24 L 26 24 M 16 28 L 24 28" stroke="currentColor" fill="none"/>', latex: 'GND', descripcion: 'Conexión a tierra' },
      { nombre: 'Interruptor', svg: '<path d="M 5 20 L 15 20 M 25 20 L 35 20 M 15 20 L 24 12" stroke="currentColor" fill="none"/><circle cx="15" cy="20" r="2" fill="currentColor"/><circle cx="25" cy="20" r="2" fill="currentColor"/>', latex: 'S', descripcion: 'Switch' },
      { nombre: 'Amperímetro', svg: '<circle cx="20" cy="20" r="12" fill="none" stroke="currentColor"/><text x="20" y="25" text-anchor="middle" font-size="12" fill="currentColor">A</text>', latex: 'I = \\square \\, A', descripcion: 'Medidor de corriente' },
      { nombre: 'Voltímetro', svg: '<circle cx="20" cy="20" r="12" fill="none" stroke="currentColor"/><text x="20" y="25" text-anchor="middle" font-size="12" fill="currentColor">V</text>', latex: 'V = \\square \\, V', descripcion: 'Medidor de voltaje' },
      { nombre: 'Transistor NPN', svg: '<circle cx="20" cy="20" r="12" fill="none" stroke="currentColor"/><path d="M 12 20 L 17 20 M 17 14 L 17 26 M 17 17 L 25 12 M 17 23 L 25 28 M 23 26 L 25 28 L 23 28" stroke="currentColor" fill="currentColor"/>', latex: 'NPN', descripcion: 'Transistor bipolar' },
      { nombre: 'Nodo', svg: '<circle cx="20" cy="20" r="4" fill="currentColor"/>', latex: '\\bullet', descripcion: 'Punto de conexión' }
    ],
    mecanica: [
      { nombre: 'Fuerza →', svg: '<path d="M 5 20 L 30 20 L 25 15 M 30 20 L 25 25" stroke="currentColor" fill="none" stroke-width="2"/>', latex: '\\vec{F} = \\square \\, N', descripcion: 'Vector de fuerza' },
      { nombre: 'Peso mg', svg: '<path d="M 20 5 L 20 30 L 15 25 M 20 30 L 25 25" stroke="currentColor" fill="none" stroke-width="2"/><text x="25" y="20" font-size="10" fill="currentColor">mg</text>', latex: '\\vec{W} = mg', descripcion: 'Fuerza gravitacional' },
      { nombre: 'Normal N', svg: '<path d="M 20 30 L 20 5 L 15 10 M 20 5 L 25 10" stroke="currentColor" fill="none" stroke-width="2"/><text x="25" y="15" font-size="10" fill="currentColor">N</text>', latex: '\\vec{N} = \\square \\, N', descripcion: 'Fuerza normal' },
      { nombre: 'Fricción f', svg: '<path d="M 5 20 L 30 20 L 25 15 M 30 20 L 25 25" stroke="currentColor" fill="none" stroke-width="2"/><text x="18" y="15" font-size="10" fill="currentColor">f</text>', latex: '\\vec{f} = \\mu N', descripcion: 'Fuerza de fricción' },
      { nombre: 'Tensión T', svg: '<path d="M 5 20 L 30 20 L 25 15 M 30 20 L 25 25 M 5 18 L 5 22 M 30 18 L 30 22" stroke="currentColor" fill="none" stroke-width="2"/><text x="18" y="15" font-size="10" fill="currentColor">T</text>', latex: '\\vec{T} = \\square \\, N', descripcion: 'Tensión en cuerda' },
      { nombre: 'Torque τ', svg: '<path d="M 20 20 m -10 0 a 10 10 0 1 1 20 0" stroke="currentColor" fill="none" stroke-width="2"/><path d="M 28 15 L 30 20 L 28 18" stroke="currentColor" fill="currentColor"/>', latex: '\\vec{\\tau} = \\vec{r} \\times \\vec{F}', descripcion: 'Momento de fuerza' },
      { nombre: 'Bloque', svg: '<rect x="10" y="15" width="20" height="10" fill="none" stroke="currentColor" stroke-width="2"/><text x="20" y="22" text-anchor="middle" font-size="8" fill="currentColor">m</text>', latex: 'm = \\square \\, kg', descripcion: 'Masa/Cuerpo rígido' },
      { nombre: 'Plano Inclinado', svg: '<path d="M 5 30 L 30 30 L 30 10 Z" fill="none" stroke="currentColor" stroke-width="2"/><path d="M 28 30 a 2 2 0 0 0 0 -4" stroke="currentColor" fill="none"/><text x="25" y="28" font-size="8" fill="currentColor">θ</text>', latex: '\\theta = \\square°', descripcion: 'Superficie inclinada' },
      { nombre: 'Polea', svg: '<circle cx="20" cy="20" r="8" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="20" cy="20" r="2" fill="currentColor"/><path d="M 20 12 L 20 5 M 12 20 L 5 20 M 28 20 L 35 20" stroke="currentColor" stroke-width="1"/>', latex: 'r = \\square \\, m', descripcion: 'Polea simple' },
      { nombre: 'Velocidad', svg: '<path d="M 5 20 L 30 20 L 25 15 M 30 20 L 25 25" stroke="#3b82f6" fill="none" stroke-width="2"/><text x="18" y="15" font-size="10" fill="#3b82f6">v</text>', latex: '\\vec{v} = \\square \\, m/s', descripcion: 'Vector velocidad' },
      { nombre: 'Aceleración', svg: '<path d="M 5 20 L 30 20 L 25 15 M 30 20 L 25 25" stroke="#ef4444" fill="none" stroke-width="2"/><text x="18" y="15" font-size="10" fill="#ef4444">a</text>', latex: '\\vec{a} = \\square \\, m/s^2', descripcion: 'Vector aceleración' },
      { nombre: 'Bisagra', svg: '<circle cx="20" cy="20" r="6" fill="none" stroke="currentColor" stroke-width="2"/><path d="M 14 20 L 26 20 M 20 14 L 20 26" stroke="currentColor"/>', latex: '\\text{Bisagra}', descripcion: 'Articulación de rotación' },
      { nombre: 'Rótula', svg: '<circle cx="20" cy="20" r="8" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="20" cy="20" r="4" fill="currentColor"/>', latex: '\\text{Rótula}', descripcion: 'Junta esférica' },
      { nombre: 'Resorte', svg: '<path d="M 5 20 L 10 20 L 12 15 L 16 25 L 20 15 L 24 25 L 28 15 L 30 20 L 35 20" stroke="currentColor" fill="none" stroke-width="1.5"/>', latex: 'k = \\square \\, N/m', descripcion: 'Muelle elástico' }
    ],
    materiales: [
      { nombre: 'Diagrama Fe-C', svg: '<rect x="5" y="5" width="30" height="30" fill="none" stroke="currentColor"/><path d="M 5 35 L 5 5 L 35 5" stroke="currentColor" stroke-width="2"/><text x="20" y="38" font-size="6" fill="currentColor">%C</text><text x="2" y="20" font-size="6" fill="currentColor">T°C</text>', latex: '\\text{Fe-C}', descripcion: 'Diagrama hierro-carbono' },
      { nombre: 'Celda FCC', svg: '<path d="M 10 10 L 30 10 L 35 15 L 35 35 L 15 35 L 10 30 Z M 10 10 L 15 15 L 15 35 M 30 10 L 35 15 M 15 15 L 35 15" stroke="currentColor" fill="none"/><circle cx="10" cy="10" r="2" fill="currentColor"/><circle cx="30" cy="10" r="2" fill="currentColor"/><circle cx="35" cy="35" r="2" fill="currentColor"/><circle cx="15" cy="35" r="2" fill="currentColor"/><circle cx="22.5" cy="12.5" r="2" fill="currentColor"/>', latex: '\\text{FCC}', descripcion: 'Cúbica centrada en caras' },
      { nombre: 'Celda BCC', svg: '<path d="M 10 10 L 30 10 L 35 15 L 35 35 L 15 35 L 10 30 Z M 10 10 L 15 15 L 15 35 M 30 10 L 35 15 M 15 15 L 35 15" stroke="currentColor" fill="none"/><circle cx="10" cy="10" r="2" fill="currentColor"/><circle cx="30" cy="10" r="2" fill="currentColor"/><circle cx="35" cy="35" r="2" fill="currentColor"/><circle cx="15" cy="35" r="2" fill="currentColor"/><circle cx="22.5" cy="22.5" r="2" fill="currentColor"/>', latex: '\\text{BCC}', descripcion: 'Cúbica centrada en el cuerpo' },
      { nombre: 'Celda HCP', svg: '<path d="M 15 8 L 25 8 L 30 15 L 25 22 L 15 22 L 10 15 Z M 15 18 L 25 18 L 30 25 L 25 32 L 15 32 L 10 25 Z M 15 18 L 15 22 M 25 18 L 25 22" stroke="currentColor" fill="none"/><circle cx="20" cy="8" r="2" fill="currentColor"/><circle cx="20" cy="20" r="2" fill="currentColor"/><circle cx="20" cy="32" r="2" fill="currentColor"/>', latex: '\\text{HCP}', descripcion: 'Hexagonal compacta' },
      { nombre: 'Ferrita', svg: '<rect x="8" y="8" width="24" height="24" fill="none" stroke="currentColor"/><circle cx="12" cy="12" r="3" fill="#cbd5e1"/><circle cx="28" cy="12" r="3" fill="#cbd5e1"/><circle cx="12" cy="28" r="3" fill="#cbd5e1"/><circle cx="28" cy="28" r="3" fill="#cbd5e1"/>', latex: '\\alpha\\text{-Fe}', descripcion: 'Fase ferrita' },
      { nombre: 'Perlita', svg: '<rect x="8" y="8" width="24" height="24" fill="none" stroke="currentColor"/><path d="M 10 10 L 30 10 M 10 14 L 30 14 M 10 18 L 30 18 M 10 22 L 30 22 M 10 26 L 30 26 M 10 30 L 30 30" stroke="currentColor" opacity="0.5"/>', latex: '\\text{Perlita}', descripcion: 'Ferrita + Cementita laminada' },
      { nombre: 'Martensita', svg: '<rect x="8" y="8" width="24" height="24" fill="none" stroke="currentColor"/><path d="M 10 20 L 30 10 M 10 24 L 30 14 M 10 28 L 30 18 M 10 32 L 30 22" stroke="currentColor" stroke-width="2"/>', latex: '\\text{Martensita}', descripcion: 'Estructura tetragonal dura' },
      { nombre: 'Diagrama TTT', svg: '<path d="M 5 35 L 5 5 L 35 5" stroke="currentColor" stroke-width="2"/><path d="M 10 30 Q 15 20 20 15 Q 25 10 30 12" stroke="currentColor" fill="none"/><text x="18" y="38" font-size="6" fill="currentColor">t (s)</text><text x="2" y="20" font-size="6" fill="currentColor">T°C</text>', latex: '\\text{TTT}', descripcion: 'Tiempo-Temperatura-Transformación' },
      { nombre: 'Grano', svg: '<path d="M 15 10 L 25 8 L 32 15 L 30 25 L 22 30 L 12 28 L 8 20 Z" fill="none" stroke="currentColor" stroke-width="2"/>', latex: '\\text{Grano}', descripcion: 'Estructura granular' },
      { nombre: 'Esfuerzo σ', svg: '<rect x="10" y="15" width="20" height="10" fill="none" stroke="currentColor" stroke-width="2"/><path d="M 5 20 L 10 20 L 5 17 M 5 20 L 5 23 M 30 20 L 35 20 L 30 17 M 30 20 L 30 23" stroke="#ef4444" stroke-width="2" fill="none"/>', latex: '\\sigma = \\frac{F}{A}', descripcion: 'Esfuerzo normal' },
      { nombre: 'Deformación ε', svg: '<rect x="10" y="15" width="15" height="10" fill="none" stroke="currentColor"/><rect x="15" y="15" width="20" height="10" fill="none" stroke="#3b82f6" stroke-dasharray="2,2"/><path d="M 25 20 L 30 20" stroke="#3b82f6" stroke-width="2"/>', latex: '\\epsilon = \\frac{\\Delta L}{L_0}', descripcion: 'Deformación unitaria' }
    ],
    civil: [
      { nombre: 'Viga Simple', svg: '<path d="M 5 20 L 35 20" stroke="currentColor" stroke-width="3"/>', latex: 'L = \\square \\, m', descripcion: 'Viga horizontal' },
      { nombre: 'Apoyo Simple', svg: '<circle cx="20" cy="25" r="3" fill="currentColor"/><path d="M 15 28 L 20 25 L 25 28" stroke="currentColor" fill="none" stroke-width="2"/><path d="M 12 28 L 28 28" stroke="currentColor" stroke-width="2"/>', latex: '\\Delta', descripcion: 'Apoyo de rodillo' },
      { nombre: 'Empotramiento', svg: '<rect x="18" y="15" width="4" height="15" fill="currentColor"/><path d="M 18 15 L 18 30 M 18 17 L 15 19 M 18 21 L 15 23 M 18 25 L 15 27 M 18 29 L 15 31" stroke="currentColor" stroke-width="1"/>', latex: '\\text{Emp}', descripcion: 'Apoyo empotrado' },
      { nombre: 'Rodillo', svg: '<circle cx="20" cy="25" r="3" fill="none" stroke="currentColor" stroke-width="2"/><path d="M 15 28 L 25 28" stroke="currentColor" stroke-width="2"/>', latex: '\\circ', descripcion: 'Apoyo móvil' },
      { nombre: 'Carga Puntual', svg: '<path d="M 20 5 L 20 20 L 15 15 M 20 20 L 25 15" stroke="#ef4444" fill="none" stroke-width="2"/><text x="22" y="12" font-size="8" fill="#ef4444">P</text>', latex: 'P = \\square \\, kN', descripcion: 'Fuerza concentrada' },
      { nombre: 'Carga Distribuida', svg: '<path d="M 10 5 L 10 15 L 5 12 M 10 15 L 7 12 M 15 5 L 15 15 L 10 12 M 15 15 L 12 12 M 20 5 L 20 15 L 15 12 M 20 15 L 17 12 M 25 5 L 25 15 L 20 12 M 25 15 L 22 12 M 30 5 L 30 15 L 25 12 M 30 15 L 27 12" stroke="#f59e0b" stroke-width="1.5"/>', latex: 'w = \\square \\, kN/m', descripcion: 'Carga uniformemente distribuida' },
      { nombre: 'Momento', svg: '<path d="M 20 20 m -8 0 a 8 8 0 1 1 16 0" stroke="#8b5cf6" fill="none" stroke-width="2"/><path d="M 26 15 L 28 20 L 26 18" stroke="#8b5cf6" fill="#8b5cf6"/><text x="22" y="12" font-size="8" fill="#8b5cf6">M</text>', latex: 'M = \\square \\, kN \\cdot m', descripcion: 'Momento aplicado' },
      { nombre: 'Cortante V', svg: '<path d="M 5 25 L 35 25" stroke="currentColor" stroke-width="2"/><path d="M 5 20 L 15 20 L 15 30 L 35 30" stroke="#10b981" stroke-width="2" fill="none"/><path d="M 15 20 L 15 30" stroke="#10b981" stroke-width="3"/>', latex: 'V(x)', descripcion: 'Diagrama de cortante' },
      { nombre: 'Momento Flector', svg: '<path d="M 5 25 L 35 25" stroke="currentColor" stroke-width="2"/><path d="M 5 25 Q 20 10 35 25" stroke="#ef4444" stroke-width="2" fill="none"/>', latex: 'M(x)', descripcion: 'Diagrama de momento' },
      { nombre: 'Deflexión', svg: '<path d="M 5 20 L 35 20" stroke="currentColor" stroke-width="1" stroke-dasharray="2,2"/><path d="M 5 20 Q 20 28 35 20" stroke="#3b82f6" stroke-width="2" fill="none"/><path d="M 20 20 L 20 28 L 18 26 M 20 28 L 22 26" stroke="#3b82f6" stroke-width="1.5"/>', latex: '\\delta_{max}', descripcion: 'Deformación máxima' },
      { nombre: 'Columna', svg: '<rect x="17" y="5" width="6" height="30" fill="none" stroke="currentColor" stroke-width="2"/><path d="M 15 8 L 25 8 M 15 32 L 25 32" stroke="currentColor" stroke-width="3"/>', latex: 'L = \\square \\, m', descripcion: 'Elemento vertical' },
      { nombre: 'Viga en I', svg: '<path d="M 15 10 L 25 10 M 20 10 L 20 30 M 15 30 L 25 30" stroke="currentColor" stroke-width="2"/>', latex: 'I\\text{-beam}', descripcion: 'Perfil doble T' }
    ]
  };

  const tabsConfig = [
    { id: 'circuitos', nombre: 'Circuitos', icon: '⚡', color: '#3b82f6' },
    { id: 'mecanica', nombre: 'Mecánica', icon: '⚙️', color: '#f59e0b' },
    { id: 'materiales', nombre: 'Materiales', icon: '🔬', color: '#8b5cf6' },
    { id: 'civil', nombre: 'Civil/Estructuras', icon: '🏗️', color: '#10b981' }
  ];

  return (
    <div style={{
      background: 'rgba(239, 68, 68, 0.08)',
      border: '2px solid rgba(239, 68, 68, 0.3)',
      borderRadius: '12px',
      padding: '1rem',
      marginBottom: '1rem'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        marginBottom: '1rem',
        paddingBottom: '0.75rem',
        borderBottom: '1px solid rgba(239, 68, 68, 0.2)'
      }}>
        <span style={{ fontSize: '1.5rem' }}>🔧</span>
        <h3 style={{
          margin: 0,
          color: '#fca5a5',
          fontSize: '1rem',
          fontWeight: '600',
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }}>
          Herramientas de Ingeniería
        </h3>
      </div>

      {/* Tabs */}
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        marginBottom: '1rem',
        flexWrap: 'wrap'
      }}>
        {tabsConfig.map(tab => (
          <button
            type="button"
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '0.5rem 1rem',
              background: activeTab === tab.id 
                ? `linear-gradient(135deg, ${tab.color} 0%, ${tab.color}dd 100%)`
                : 'rgba(100, 116, 139, 0.2)',
              border: activeTab === tab.id 
                ? `2px solid ${tab.color}`
                : '2px solid rgba(148, 163, 184, 0.3)',
              borderRadius: '8px',
              color: activeTab === tab.id ? 'white' : '#cbd5e1',
              cursor: 'pointer',
              fontWeight: activeTab === tab.id ? '600' : '400',
              fontSize: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              transition: 'all 0.2s',
              boxShadow: activeTab === tab.id ? `0 0 15px ${tab.color}40` : 'none'
            }}
          >
            <span>{tab.icon}</span>
            <span>{tab.nombre}</span>
          </button>
        ))}
      </div>

      {/* Componentes */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))',
        gap: '0.75rem',
        maxHeight: '400px',
        overflowY: 'auto',
        padding: '0.5rem'
      }}>
        {COMPONENTES_INGENIERIA[activeTab]?.map((comp, idx) => (
          <button
            type="button"
            key={idx}
            onClick={() => onInsertComponent(comp)}
            style={{
              padding: '0.75rem',
              background: 'rgba(30, 41, 59, 0.6)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '8px',
              color: '#e2e8f0',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.2s',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.5rem'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(239, 68, 68, 0.15)';
              e.currentTarget.style.borderColor = '#ef4444';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(30, 41, 59, 0.6)';
              e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.3)';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <div style={{
              fontWeight: '600',
              fontSize: '0.9rem',
              color: '#fca5a5'
            }}>
              {comp.nombre}
            </div>
            {comp.svg && (
              <div style={{
                width: '40px',
                height: '40px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <svg 
                  width="40" 
                  height="40" 
                  viewBox="0 0 40 40"
                  style={{ color: '#cbd5e1' }}
                  dangerouslySetInnerHTML={{ __html: comp.svg }}
                />
              </div>
            )}
            <div style={{
              fontSize: '0.75rem',
              color: '#94a3b8',
              fontStyle: 'italic'
            }}>
              {comp.descripcion}
            </div>
          </button>
        ))}
      </div>

      {/* Guía */}
      <div style={{
        marginTop: '1rem',
        padding: '0.75rem',
        background: 'rgba(239, 68, 68, 0.1)',
        borderRadius: '8px',
        fontSize: '0.85rem',
        color: '#fca5a5'
      }}>
        <strong>💡 Tip:</strong> Los componentes se insertan como bloques editables. Usa el canvas para conectar elementos y construir diagramas.
      </div>
    </div>
  );
};

export default EngineeringToolbar;
