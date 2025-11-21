import { useState } from 'react';

const PhysicsToolbar = ({ onInsertTemplate }) => {
  const [activeTab, setActiveTab] = useState('vectores');

  const CATEGORIAS_FISICA = {
    vectores: [
      { nombre: 'Vector', latex: '\\vec{F}', descripcion: 'Vector con flecha' },
      { nombre: 'Magnitud', latex: '|\\vec{F}|', descripcion: 'Magnitud de vector' },
      { nombre: 'Vector Unitario', latex: '\\hat{n}', descripcion: 'Vector unitario' },
      { nombre: 'Componentes', latex: '(F_x, F_y, F_z)', descripcion: 'Componentes cartesianas' },
      { nombre: 'Vector Columna', latex: '\\begin{pmatrix} F_x \\\\ F_y \\\\ F_z \\end{pmatrix}', descripcion: 'Notación matricial' },
      { nombre: 'Producto Escalar', latex: '\\vec{A} \\cdot \\vec{B}', descripcion: 'Producto punto' },
      { nombre: 'Producto Vectorial', latex: '\\vec{A} \\times \\vec{B}', descripcion: 'Producto cruz' },
      { nombre: 'Vector Posición', latex: '\\vec{r} = x\\hat{i} + y\\hat{j} + z\\hat{k}', descripcion: 'Vector en base canónica' }
    ],
    operadores: [
      { nombre: 'Gradiente', latex: '\\nabla f', descripcion: 'Gradiente de campo escalar' },
      { nombre: 'Divergencia', latex: '\\nabla \\cdot \\vec{F}', descripcion: 'Divergencia de campo vectorial' },
      { nombre: 'Rotacional', latex: '\\nabla \\times \\vec{F}', descripcion: 'Rotacional de campo vectorial' },
      { nombre: 'Laplaciano', latex: '\\nabla^2 f', descripcion: 'Operador de Laplace' },
      { nombre: 'Derivada Parcial', latex: '\\frac{\\partial f}{\\partial x}', descripcion: 'Derivada parcial' },
      { nombre: 'Derivada Total', latex: '\\frac{d}{dt}', descripcion: 'Derivada total temporal' },
      { nombre: 'Integral de Línea', latex: '\\int_C \\vec{F} \\cdot d\\vec{r}', descripcion: 'Integral de línea' },
      { nombre: 'Integral de Superficie', latex: '\\iint_S \\vec{F} \\cdot d\\vec{S}', descripcion: 'Integral de superficie' }
    ],
    fuerzas: [
      { nombre: 'Flecha →', latex: '\\xrightarrow{F}', descripcion: 'Flecha con etiqueta' },
      { nombre: 'Peso', latex: '\\vec{F}_g = m\\vec{g}', descripcion: 'Fuerza gravitacional' },
      { nombre: 'Normal', latex: '\\vec{N}', descripcion: 'Fuerza normal' },
      { nombre: 'Fricción', latex: '\\vec{f} = \\mu \\vec{N}', descripcion: 'Fuerza de fricción' },
      { nombre: 'Tensión', latex: '\\vec{T}', descripcion: 'Tensión en cuerda' },
      { nombre: 'Elástica', latex: '\\vec{F} = -k\\vec{x}', descripcion: 'Fuerza elástica (Hooke)' },
      { nombre: 'Centrípeta', latex: '\\vec{F}_c = \\frac{mv^2}{r}\\hat{r}', descripcion: 'Fuerza centrípeta' },
      { nombre: 'Diagrama FBD', latex: '\\sum \\vec{F} = \\vec{0}', descripcion: 'Diagrama de cuerpo libre' }
    ],
    mecanica: [
      { nombre: '2ª Ley Newton', latex: '\\sum \\vec{F} = m\\vec{a}', descripcion: 'Segunda ley de Newton' },
      { nombre: 'Trabajo', latex: 'W = \\vec{F} \\cdot \\vec{d}', descripcion: 'Trabajo mecánico' },
      { nombre: 'Energía Cinética', latex: 'K = \\frac{1}{2}mv^2', descripcion: 'Energía cinética' },
      { nombre: 'Energía Potencial', latex: 'U = mgh', descripción: 'Energía potencial gravitacional' },
      { nombre: 'Momento Lineal', latex: '\\vec{p} = m\\vec{v}', descripcion: 'Momento lineal' },
      { nombre: 'Impulso', latex: '\\vec{J} = \\int \\vec{F}dt', descripcion: 'Impulso mecánico' },
      { nombre: 'Torque', latex: '\\vec{\\tau} = \\vec{r} \\times \\vec{F}', descripcion: 'Momento de fuerza' },
      { nombre: 'Momento Angular', latex: '\\vec{L} = \\vec{r} \\times \\vec{p}', descripcion: 'Momento angular' },
      { nombre: 'Conservación Energía', latex: 'E_i = E_f', descripcion: 'Conservación de energía' },
      { nombre: 'MAS', latex: 'x(t) = A\\cos(\\omega t + \\phi)', descripcion: 'Movimiento armónico simple' }
    ],
    electromagnetismo: [
      { nombre: 'Campo E', latex: '\\vec{E} = \\frac{\\vec{F}}{q}', descripcion: 'Campo eléctrico' },
      { nombre: 'Campo B', latex: '\\vec{B}', descripcion: 'Campo magnético' },
      { nombre: 'Ley de Coulomb', latex: 'F = k\\frac{q_1 q_2}{r^2}', descripcion: 'Fuerza electrostática' },
      { nombre: 'Ley de Gauss (E)', latex: '\\nabla \\cdot \\vec{E} = \\frac{\\rho}{\\epsilon_0}', descripcion: 'Ley de Gauss eléctrica' },
      { nombre: 'Ley de Gauss (B)', latex: '\\nabla \\cdot \\vec{B} = 0', descripcion: 'Ley de Gauss magnética' },
      { nombre: 'Ley de Faraday', latex: '\\nabla \\times \\vec{E} = -\\frac{\\partial \\vec{B}}{\\partial t}', descripcion: 'Ley de Faraday' },
      { nombre: 'Ley de Ampère-Maxwell', latex: '\\nabla \\times \\vec{B} = \\mu_0 \\vec{J} + \\mu_0\\epsilon_0 \\frac{\\partial \\vec{E}}{\\partial t}', descripcion: 'Ley de Ampère-Maxwell' },
      { nombre: 'Fuerza de Lorentz', latex: '\\vec{F} = q(\\vec{E} + \\vec{v} \\times \\vec{B})', descripcion: 'Fuerza electromagnética' },
      { nombre: 'Potencial E', latex: 'V = \\frac{kq}{r}', descripcion: 'Potencial eléctrico' },
      { nombre: 'Capacitor', latex: 'C = \\frac{Q}{V}', descripcion: 'Capacitancia' },
      { nombre: 'Ley de Ohm', latex: 'V = IR', descripcion: 'Ley de Ohm' },
      { nombre: 'Potencia', latex: 'P = IV', descripcion: 'Potencia eléctrica' }
    ],
    optica: [
      { nombre: 'Ley de Snell', latex: 'n_1\\sin\\theta_1 = n_2\\sin\\theta_2', descripcion: 'Refracción' },
      { nombre: 'Lente Delgada', latex: '\\frac{1}{f} = \\frac{1}{d_o} + \\frac{1}{d_i}', descripcion: 'Ecuación del lente' },
      { nombre: 'Aumento', latex: 'm = -\\frac{d_i}{d_o}', descripcion: 'Aumento lateral' },
      { nombre: 'Espejo', latex: '\\frac{1}{f} = \\frac{1}{d_o} + \\frac{1}{d_i}', descripcion: 'Ecuación del espejo' },
      { nombre: 'Interferencia', latex: '\\delta = d\\sin\\theta = m\\lambda', descripcion: 'Interferencia constructiva' },
      { nombre: 'Difracción', latex: 'a\\sin\\theta = m\\lambda', descripcion: 'Mínimos de difracción' },
      { nombre: 'Rayo Incidente', latex: '\\xrightarrow{\\text{rayo}}', descripcion: 'Rayo de luz' },
      { nombre: 'Índice Refracción', latex: 'n = \\frac{c}{v}', descripcion: 'Índice de refracción' }
    ],
    termodinamica: [
      { nombre: '1ª Ley', latex: '\\Delta U = Q - W', descripcion: 'Primera ley de termodinámica' },
      { nombre: 'Trabajo', latex: 'W = \\int P dV', descripcion: 'Trabajo termodinámico' },
      { nombre: 'Gas Ideal', latex: 'PV = nRT', descripcion: 'Ecuación de estado ideal' },
      { nombre: 'Proceso Isotérmico', latex: 'PV = \\text{const}', descripcion: 'Temperatura constante' },
      { nombre: 'Proceso Adiabático', latex: 'PV^\\gamma = \\text{const}', descripcion: 'Sin transferencia de calor' },
      { nombre: 'Proceso Isobárico', latex: 'V \\propto T', descripcion: 'Presión constante' },
      { nombre: 'Proceso Isocórico', latex: 'P \\propto T', descripcion: 'Volumen constante' },
      { nombre: 'Entropía', latex: 'dS = \\frac{dQ}{T}', descripcion: 'Cambio de entropía' },
      { nombre: '2ª Ley', latex: '\\Delta S_{\\text{universo}} \\geq 0', descripcion: 'Segunda ley' },
      { nombre: 'Eficiencia Carnot', latex: '\\eta = 1 - \\frac{T_c}{T_h}', descripcion: 'Máxima eficiencia' }
    ],
    cuantica: [
      { nombre: 'Función de Onda', latex: '\\Psi(x,t)', descripcion: 'Estado cuántico' },
      { nombre: 'Schrödinger', latex: 'i\\hbar\\frac{\\partial}{\\partial t}\\Psi = \\hat{H}\\Psi', descripcion: 'Ecuación de Schrödinger' },
      { nombre: 'Operador Hamiltoniano', latex: '\\hat{H} = -\\frac{\\hbar^2}{2m}\\nabla^2 + V', descripcion: 'Operador energía' },
      { nombre: 'Bra-Ket', latex: '|\\psi\\rangle', descripcion: 'Notación de Dirac' },
      { nombre: 'Producto Interno', latex: '\\langle\\phi|\\psi\\rangle', descripcion: 'Producto interno' },
      { nombre: 'Operador', latex: '\\hat{A}', descripcion: 'Operador hermitiano' },
      { nombre: 'Conmutador', latex: '[\\hat{A}, \\hat{B}]', descripcion: 'Conmutador de operadores' },
      { nombre: 'Incertidumbre', latex: '\\Delta x \\Delta p \\geq \\frac{\\hbar}{2}', descripcion: 'Principio de incertidumbre' },
      { nombre: 'Energía Fotón', latex: 'E = h\\nu', descripcion: 'Cuantización de luz' },
      { nombre: 'De Broglie', latex: '\\lambda = \\frac{h}{p}', descripcion: 'Longitud de onda de materia' },
      { nombre: 'Partícula en Caja', latex: 'E_n = \\frac{n^2\\pi^2\\hbar^2}{2mL^2}', descripcion: 'Niveles de energía' },
      { nombre: 'Probabilidad', latex: 'P = |\\Psi|^2', descripcion: 'Densidad de probabilidad' }
    ]
  };

  const tabsConfig = [
    { id: 'vectores', nombre: 'Vectores', icon: '➜', color: '#f59e0b' },
    { id: 'operadores', nombre: 'Operadores', icon: '∇', color: '#f97316' },
    { id: 'fuerzas', nombre: 'Fuerzas', icon: '⇉', color: '#dc2626' },
    { id: 'mecanica', nombre: 'Mecánica', icon: '⚙️', color: '#eab308' },
    { id: 'electromagnetismo', nombre: 'Electromag.', icon: '⚡', color: '#3b82f6' },
    { id: 'optica', nombre: 'Óptica', icon: '🔦', color: '#06b6d4' },
    { id: 'termodinamica', nombre: 'Termodinámica', icon: '🌡️', color: '#ef4444' },
    { id: 'cuantica', nombre: 'Cuántica', icon: 'ℏ', color: '#8b5cf6' }
  ];

  return (
    <div style={{
      background: 'rgba(245, 158, 11, 0.08)',
      border: '2px solid rgba(245, 158, 11, 0.3)',
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
        borderBottom: '1px solid rgba(245, 158, 11, 0.2)'
      }}>
        <span style={{ fontSize: '1.5rem' }}>⚛️</span>
        <h3 style={{
          margin: 0,
          color: '#fbbf24',
          fontSize: '1rem',
          fontWeight: '600',
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }}>
          Herramientas de Física
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

      {/* Botones de plantillas */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
        gap: '0.75rem',
        maxHeight: '400px',
        overflowY: 'auto',
        padding: '0.5rem'
      }}>
        {CATEGORIAS_FISICA[activeTab]?.map((plantilla, idx) => (
          <button
            type="button"
            key={idx}
            onClick={() => onInsertTemplate(plantilla.latex)}
            style={{
              padding: '0.75rem',
              background: 'rgba(30, 41, 59, 0.6)',
              border: '1px solid rgba(245, 158, 11, 0.3)',
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
              e.currentTarget.style.background = 'rgba(245, 158, 11, 0.15)';
              e.currentTarget.style.borderColor = '#f59e0b';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(30, 41, 59, 0.6)';
              e.currentTarget.style.borderColor = 'rgba(245, 158, 11, 0.3)';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <div style={{
              fontWeight: '600',
              fontSize: '0.9rem',
              color: '#fbbf24'
            }}>
              {plantilla.nombre}
            </div>
            <div style={{
              fontSize: '0.75rem',
              color: '#94a3b8',
              fontStyle: 'italic'
            }}>
              {plantilla.descripcion}
            </div>
            <div style={{
              fontSize: '0.8rem',
              fontFamily: 'monospace',
              color: '#cbd5e1',
              background: 'rgba(0, 0, 0, 0.3)',
              padding: '0.25rem 0.5rem',
              borderRadius: '4px',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}>
              {plantilla.latex}
            </div>
          </button>
        ))}
      </div>

      {/* Guía rápida */}
      <div style={{
        marginTop: '1rem',
        padding: '0.75rem',
        background: 'rgba(245, 158, 11, 0.1)',
        borderRadius: '8px',
        fontSize: '0.85rem',
        color: '#fcd34d'
      }}>
        <strong>💡 Tip:</strong> Las plantillas se insertan en el editor. Usa <code style={{
          background: 'rgba(0, 0, 0, 0.3)',
          padding: '0.15rem 0.4rem',
          borderRadius: '3px',
          color: '#fbbf24'
        }}>\square</code> para espacios editables
      </div>
    </div>
  );
};

export default PhysicsToolbar;
