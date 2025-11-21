import { useState } from 'react';

const DiscreteToolbar = ({ onInsertComponent }) => {
  const [tabActiva, setTabActiva] = useState('logica');

  // 🟪 Tablas de Verdad y Lógica Proposicional
  const componentesLogica = [
    { nombre: 'Tabla Verdad', svg: 'M2 2 L38 2 L38 38 L2 38 Z M20 2 L20 38 M2 10 L38 10 M2 18 L38 18 M2 26 L38 26 M2 34 L38 34', latex: 'p | q | p∧q', desc: 'Tabla de verdad' },
    { nombre: '¬ (NOT)', svg: 'M15 12 L25 12 M20 12 L20 8', latex: '\\neg', desc: 'Negación' },
    { nombre: '∧ (AND)', svg: 'M10 25 L20 10 L30 25', latex: '\\land', desc: 'Conjunción' },
    { nombre: '∨ (OR)', svg: 'M10 10 L20 25 L30 10', latex: '\\lor', desc: 'Disyunción' },
    { nombre: '→ (IMPL)', svg: 'M5 20 L30 20 L25 15 M30 20 L25 25', latex: '\\rightarrow', desc: 'Implicación' },
    { nombre: '↔ (BIIM)', svg: 'M5 20 L30 20 L25 15 M30 20 L25 25 M30 20 L35 20 L30 15 M35 20 L30 25', latex: '\\leftrightarrow', desc: 'Bicondicional' },
    { nombre: '⊕ (XOR)', svg: 'M20 20 m -12 0 a 12 12 0 1 0 24 0 a 12 12 0 1 0 -24 0 M14 14 L26 26 M26 14 L14 26', latex: '\\oplus', desc: 'XOR' },
    { nombre: '⊤ (TRUE)', svg: 'M10 15 L30 15 M20 15 L20 25', latex: '\\top', desc: 'Tautología' },
    { nombre: '⊥ (FALSE)', svg: 'M10 25 L30 25 M20 15 L20 25', latex: '\\bot', desc: 'Contradicción' },
    { nombre: '⊢ (Prueba)', svg: 'M15 10 L15 30 M15 20 L30 20 L25 15 M30 20 L25 25', latex: '\\vdash', desc: 'Deducción' },
    { nombre: '⊨ (Modelo)', svg: 'M12 10 L12 30 M18 10 L18 30 M18 20 L30 20 L25 15 M30 20 L25 25', latex: '\\models', desc: 'Modelo/Satisface' },
    { nombre: '∀ (Todo)', svg: 'M10 30 L20 10 L30 30 M15 22 L25 22', latex: '\\forall', desc: 'Cuantificador universal' },
    { nombre: '∃ (Existe)', svg: 'M30 10 L15 10 M15 10 L15 30 M15 20 L25 20 M15 30 L30 30', latex: '\\exists', desc: 'Cuantificador existencial' },
    { nombre: '∴ (Por tanto)', svg: 'M15 22 m -2 0 a 2 2 0 1 0 4 0 a 2 2 0 1 0 -4 0 M25 22 m -2 0 a 2 2 0 1 0 4 0 a 2 2 0 1 0 -4 0 M20 30 m -2 0 a 2 2 0 1 0 4 0 a 2 2 0 1 0 -4 0', latex: '\\therefore', desc: 'Conclusión' }
  ];

  // 🟫 Teoría de Conjuntos
  const componentesConjuntos = [
    { nombre: '∪ (Unión)', svg: 'M10 10 C10 25, 30 25, 30 10', latex: '\\cup', desc: 'Unión de conjuntos' },
    { nombre: '∩ (Inter)', svg: 'M10 25 C10 10, 30 10, 30 25', latex: '\\cap', desc: 'Intersección' },
    { nombre: '⊂ (Subconj)', svg: 'M30 10 C20 10, 10 15, 10 20 C10 25, 20 30, 30 30', latex: '\\subset', desc: 'Subconjunto propio' },
    { nombre: '⊆ (Sub≤)', svg: 'M30 10 C20 10, 10 15, 10 20 C10 25, 20 30, 30 30 M10 35 L30 35', latex: '\\subseteq', desc: 'Subconjunto o igual' },
    { nombre: '∈ (Perten)', svg: 'M30 10 L15 10 M15 10 C15 10, 10 15, 10 20 C10 25, 15 30, 15 30 M15 20 L25 20 M15 30 L30 30', latex: '\\in', desc: 'Pertenece' },
    { nombre: '∉ (No Pert)', svg: 'M30 10 L15 10 M15 10 C15 10, 10 15, 10 20 C10 25, 15 30, 15 30 M15 20 L25 20 M15 30 L30 30 M12 8 L28 32', latex: '\\notin', desc: 'No pertenece' },
    { nombre: '× (Product)', svg: 'M12 12 L28 28 M28 12 L12 28', latex: '\\times', desc: 'Producto cartesiano' },
    { nombre: '∅ (Vacío)', svg: 'M20 20 m -12 0 a 12 12 0 1 0 24 0 a 12 12 0 1 0 -24 0 M12 12 L28 28', latex: '\\emptyset', desc: 'Conjunto vacío' },
    { nombre: '{ } (Conj)', svg: 'M15 8 C12 12, 12 18, 12 20 C12 22, 12 28, 15 32 M8 20 L10 20 M25 8 C28 12, 28 18, 28 20 C28 22, 28 28, 25 32 M30 20 L32 20', latex: '\\{ \\}', desc: 'Llaves de conjunto' },
    { nombre: 'ℕ (Natur)', svg: 'M10 10 L10 30 M10 30 L15 25 L20 30 L25 15 L25 30', latex: '\\mathbb{N}', desc: 'Números naturales' },
    { nombre: 'ℤ (Enter)', svg: 'M12 12 L28 12 M12 12 L22 28 M12 28 L28 28', latex: '\\mathbb{Z}', desc: 'Números enteros' },
    { nombre: 'ℚ (Racion)', svg: 'M20 20 m -8 0 a 8 8 0 1 0 16 0 a 8 8 0 1 0 -16 0 M25 25 L30 32', latex: '\\mathbb{Q}', desc: 'Números racionales' },
    { nombre: 'ℝ (Real)', svg: 'M12 10 L12 30 M12 10 C12 10, 18 10, 22 15 C26 20, 26 25, 22 30 L18 30', latex: '\\mathbb{R}', desc: 'Números reales' },
    { nombre: '\\  (Difer)', svg: 'M5 15 L35 15 M5 25 L35 25 M30 8 L38 35', latex: '\\setminus', desc: 'Diferencia de conjuntos' }
  ];

  // 🟩 Diagramas de Venn
  const componentesVenn = [
    { nombre: 'Venn 2', svg: 'M15 20 m -10 0 a 10 10 0 1 0 20 0 a 10 10 0 1 0 -20 0 M25 20 m -10 0 a 10 10 0 1 0 20 0 a 10 10 0 1 0 -20 0', latex: 'A \\cap B', desc: 'Diagrama de Venn 2 conjuntos' },
    { nombre: 'Venn 3', svg: 'M15 18 m -8 0 a 8 8 0 1 0 16 0 a 8 8 0 1 0 -16 0 M25 18 m -8 0 a 8 8 0 1 0 16 0 a 8 8 0 1 0 -16 0 M20 28 m -8 0 a 8 8 0 1 0 16 0 a 8 8 0 1 0 -16 0', latex: 'A \\cap B \\cap C', desc: 'Diagrama de Venn 3 conjuntos' },
    { nombre: 'Región A', svg: 'M20 20 m -12 0 a 12 12 0 1 0 24 0 a 12 12 0 1 0 -24 0', latex: 'A', desc: 'Región de conjunto A', fill: true },
    { nombre: 'A ∩ B', svg: 'M18 20 Q20 16, 22 20 Q20 24, 18 20', latex: 'A \\cap B', desc: 'Intersección', fill: true },
    { nombre: 'A ∪ B', svg: 'M10 20 C8 15, 8 25, 10 20 M30 20 C32 15, 32 25, 30 20', latex: 'A \\cup B', desc: 'Unión visual', fill: true },
    { nombre: 'Universo', svg: 'M2 2 L38 2 L38 38 L2 38 Z', latex: 'U', desc: 'Conjunto universo' }
  ];

  // 🟦 Relaciones
  const componentesRelaciones = [
    { nombre: 'Par (a,b)', svg: 'M10 15 C8 20, 8 20, 10 25 M12 15 L12 25 M30 15 C32 20, 32 20, 30 25 M28 15 L28 25', latex: '(a,b)', desc: 'Par ordenado' },
    { nombre: 'R = { }', svg: 'M8 10 L8 30 M8 20 L15 20 M25 8 C22 12, 22 18, 22 20 C22 22, 22 28, 25 32 M32 8 C35 12, 35 18, 35 20 C35 22, 35 28, 32 32', latex: 'R = \\{\\}', desc: 'Relación como conjunto' },
    { nombre: 'Matriz R', svg: 'M8 8 L10 8 L10 32 L8 32 M30 8 L32 8 L32 32 L30 32 M14 14 L14 28 M20 14 L20 28 M26 14 L26 28 M12 18 L28 18 M12 24 L28 24', latex: 'M_R', desc: 'Matriz de relación' },
    { nombre: 'Reflexiva', svg: 'M20 15 m -5 0 a 5 5 0 1 0 10 0 a 5 5 0 1 0 -10 0 M20 10 C15 8, 25 8, 20 10', latex: 'xRx', desc: 'Relación reflexiva' },
    { nombre: 'Simétrica', svg: 'M10 15 m -3 0 a 3 3 0 1 0 6 0 a 3 3 0 1 0 -6 0 M30 15 m -3 0 a 3 3 0 1 0 6 0 a 3 3 0 1 0 -6 0 M13 15 L27 15 L25 12 M27 15 L25 18 M27 15 L13 15 L15 12 M13 15 L15 18', latex: 'xRy \\Leftrightarrow yRx', desc: 'Relación simétrica' },
    { nombre: 'Transitiva', svg: 'M8 10 m -2 0 a 2 2 0 1 0 4 0 a 2 2 0 1 0 -4 0 M20 10 m -2 0 a 2 2 0 1 0 4 0 a 2 2 0 1 0 -4 0 M32 10 m -2 0 a 2 2 0 1 0 4 0 a 2 2 0 1 0 -4 0 M10 10 L18 10 L16 8 M18 10 L16 12 M22 10 L30 10 L28 8 M30 10 L28 12 M12 12 L28 28 L26 26', latex: 'xRy \\land yRz \\Rightarrow xRz', desc: 'Relación transitiva' },
    { nombre: 'Grafo Bipar', svg: 'M8 12 m -2 0 a 2 2 0 1 0 4 0 a 2 2 0 1 0 -4 0 M8 20 m -2 0 a 2 2 0 1 0 4 0 a 2 2 0 1 0 -4 0 M8 28 m -2 0 a 2 2 0 1 0 4 0 a 2 2 0 1 0 -4 0 M32 12 m -2 0 a 2 2 0 1 0 4 0 a 2 2 0 1 0 -4 0 M32 28 m -2 0 a 2 2 0 1 0 4 0 a 2 2 0 1 0 -4 0 M10 12 L30 12 M10 12 L30 28 M10 20 L30 12 M10 28 L30 12', latex: 'G(X,Y)', desc: 'Grafo bipartito' }
  ];

  // 🔵 Grafos (dirigidos/no dirigidos)
  const componentesGrafos = [
    { nombre: 'Nodo', svg: 'M20 20 m -10 0 a 10 10 0 1 0 20 0 a 10 10 0 1 0 -20 0', latex: 'v', desc: 'Vértice de grafo' },
    { nombre: 'Arista →', svg: 'M5 20 L30 20 L25 15 M30 20 L25 25', latex: '\\rightarrow', desc: 'Arista dirigida' },
    { nombre: 'Arista —', svg: 'M5 20 L35 20', latex: '-', desc: 'Arista no dirigida' },
    { nombre: 'Arista ↔', svg: 'M5 20 L30 20 L25 15 M30 20 L25 25 M10 20 L5 20 L7 15 M5 20 L7 25', latex: '\\leftrightarrow', desc: 'Arista bidireccional' },
    { nombre: 'Loop', svg: 'M25 8 C30 5, 35 10, 30 15 L28 13', latex: 'loop', desc: 'Bucle (arista reflexiva)' },
    { nombre: 'Peso', svg: 'M15 18 L25 18 M20 13 L20 23 M22 15 Q28 12, 28 18 Q28 24, 22 21', latex: 'w', desc: 'Peso de arista' },
    { nombre: 'Grafo K₃', svg: 'M20 8 m -3 0 a 3 3 0 1 0 6 0 a 3 3 0 1 0 -6 0 M10 28 m -3 0 a 3 3 0 1 0 6 0 a 3 3 0 1 0 -6 0 M30 28 m -3 0 a 3 3 0 1 0 6 0 a 3 3 0 1 0 -6 0 M20 11 L12 25 M20 11 L28 25 M13 28 L27 28', latex: 'K_3', desc: 'Grafo completo de 3 vértices' },
    { nombre: 'Grafo K₄', svg: 'M12 10 m -2 0 a 2 2 0 1 0 4 0 a 2 2 0 1 0 -4 0 M28 10 m -2 0 a 2 2 0 1 0 4 0 a 2 2 0 1 0 -4 0 M12 30 m -2 0 a 2 2 0 1 0 4 0 a 2 2 0 1 0 -4 0 M28 30 m -2 0 a 2 2 0 1 0 4 0 a 2 2 0 1 0 -4 0 M14 10 L26 10 M14 10 L12 28 M14 10 L26 28 M26 10 L28 28 M26 10 L14 28 M12 28 L26 28 M12 28 L28 30 M26 28 L14 30', latex: 'K_4', desc: 'Grafo completo de 4 vértices' },
    { nombre: 'Camino', svg: 'M8 20 m -2 0 a 2 2 0 1 0 4 0 a 2 2 0 1 0 -4 0 M18 20 m -2 0 a 2 2 0 1 0 4 0 a 2 2 0 1 0 -4 0 M28 20 m -2 0 a 2 2 0 1 0 4 0 a 2 2 0 1 0 -4 0 M10 20 L16 20 M20 20 L26 20', latex: 'P_3', desc: 'Camino' },
    { nombre: 'Ciclo', svg: 'M15 12 m -3 0 a 3 3 0 1 0 6 0 a 3 3 0 1 0 -6 0 M25 12 m -3 0 a 3 3 0 1 0 6 0 a 3 3 0 1 0 -6 0 M15 28 m -3 0 a 3 3 0 1 0 6 0 a 3 3 0 1 0 -6 0 M25 28 m -3 0 a 3 3 0 1 0 6 0 a 3 3 0 1 0 -6 0 M18 12 L22 12 M25 15 L25 25 M22 28 L18 28 M15 25 L15 15', latex: 'C_4', desc: 'Ciclo' }
  ];

  // 🟠 Lógica de Predicados
  const componentesPredicados = [
    { nombre: 'P(x)', svg: 'M15 10 L15 30 M15 10 C15 10, 20 10, 23 15 C26 20, 26 15, 23 20 L20 20 M25 15 C27 15, 30 17, 30 20 C30 23, 27 25, 25 25 L25 30', latex: 'P(x)', desc: 'Predicado' },
    { nombre: '∀x P(x)', svg: 'M8 28 L15 10 L22 28 M12 22 L18 22 M24 20 L24 30 M24 20 C24 20, 28 20, 30 22 C32 24, 32 22, 30 24 L28 24', latex: '\\forall x P(x)', desc: 'Cuantificador universal' },
    { nombre: '∃x P(x)', svg: 'M8 10 L18 10 M8 10 L8 30 M8 20 L15 20 M8 30 L18 30 M20 20 L20 30 M20 20 C20 20, 24 20, 26 22 C28 24, 28 22, 26 24 L24 24', latex: '\\exists x P(x)', desc: 'Cuantificador existencial' },
    { nombre: '∃! (Único)', svg: 'M8 10 L18 10 M8 10 L8 30 M8 20 L15 20 M8 30 L18 30 M22 10 L22 30 M19 35 L25 35', latex: '\\exists !', desc: 'Existe único' }
  ];

  const componentes = {
    logica: componentesLogica,
    conjuntos: componentesConjuntos,
    venn: componentesVenn,
    relaciones: componentesRelaciones,
    grafos: componentesGrafos,
    predicados: componentesPredicados
  };

  const tabs = [
    { id: 'logica', nombre: 'Lógica', icon: '🟪', color: '#7c3aed' },
    { id: 'conjuntos', nombre: 'Conjuntos', icon: '🟫', color: '#92400e' },
    { id: 'venn', nombre: 'Venn', icon: '🟩', color: '#16a34a' },
    { id: 'relaciones', nombre: 'Relaciones', icon: '🟦', color: '#2563eb' },
    { id: 'grafos', nombre: 'Grafos', icon: '🔵', color: '#0891b2' },
    { id: 'predicados', nombre: 'Predicados', icon: '🟠', color: '#ea580c' }
  ];

  return (
    <div style={{
      background: 'rgba(124, 58, 237, 0.05)',
      borderRadius: '12px',
      padding: '1rem',
      border: '1px solid rgba(124, 58, 237, 0.2)'
    }}>
      {/* Tabs */}
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        marginBottom: '1rem',
        flexWrap: 'wrap'
      }}>
        {tabs.map(tab => (
          <button
            type="button"
            key={tab.id}
            onClick={() => setTabActiva(tab.id)}
            style={{
              padding: '0.5rem 1rem',
              background: tabActiva === tab.id ? tab.color : 'rgba(124, 58, 237, 0.1)',
              color: tabActiva === tab.id ? 'white' : '#c4b5fd',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: tabActiva === tab.id ? '600' : '400',
              fontSize: '0.9rem',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem'
            }}
          >
            <span>{tab.icon}</span>
            {tab.nombre}
          </button>
        ))}
      </div>

      {/* Grid de componentes */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))',
        gap: '0.75rem',
        maxHeight: '350px',
        overflowY: 'auto',
        padding: '0.5rem'
      }}>
        {componentes[tabActiva].map((comp, idx) => (
          <button
            type="button"
            key={idx}
            onClick={() => onInsertComponent(comp)}
            style={{
              padding: '0.75rem',
              background: 'rgba(124, 58, 237, 0.1)',
              border: '1px solid rgba(124, 58, 237, 0.3)',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.2s',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '0.5rem'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(124, 58, 237, 0.2)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(124, 58, 237, 0.1)';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            {/* Preview SVG */}
            <svg width="40" height="40" viewBox="0 0 40 40" style={{ flexShrink: 0 }}>
              <path
                d={comp.svg}
                stroke="#c4b5fd"
                strokeWidth="2"
                fill={comp.fill ? '#7c3aed' : 'none'}
              />
            </svg>
            
            {/* Nombre */}
            <span style={{
              fontSize: '0.7rem',
              color: '#e9d5ff',
              textAlign: 'center',
              fontWeight: '500',
              lineHeight: '1.2'
            }}>
              {comp.nombre}
            </span>
          </button>
        ))}
      </div>

      {/* Footer con info */}
      <div style={{
        marginTop: '1rem',
        padding: '0.75rem',
        background: 'rgba(124, 58, 237, 0.08)',
        borderRadius: '6px',
        fontSize: '0.8rem',
        color: '#ddd6fe',
        lineHeight: '1.5'
      }}>
        <strong style={{color: '#e9d5ff'}}>💡 Categoría {tabs.find(t => t.id === tabActiva)?.nombre}:</strong> {
          tabActiva === 'logica' ? 'Tablas de verdad, conectivos lógicos, cuantificadores' :
          tabActiva === 'conjuntos' ? 'Operaciones de conjuntos, pertenencia, subconjuntos' :
          tabActiva === 'venn' ? 'Diagramas de Venn de 2 y 3 conjuntos' :
          tabActiva === 'relaciones' ? 'Pares ordenados, matrices, propiedades de relaciones' :
          tabActiva === 'grafos' ? 'Grafos dirigidos/no dirigidos, caminos, ciclos' :
          'Lógica de predicados, cuantificadores'
        }
      </div>
    </div>
  );
};

export default DiscreteToolbar;
