import { useState } from 'react';

/**
 * 🎲 TOOLBAR DE PROBABILIDAD Y ESTADÍSTICA
 * Panel súper amigable con plantillas visuales
 * Árboles, Venn, distribuciones, fórmulas de Bayes
 */
export default function ProbabilityToolbar({ onInsertElement }) {
  const [activeTab, setActiveTab] = useState('arboles');

  const tabs = [
    { id: 'arboles', name: '🌳 Árboles', color: '#8b5cf6' },
    { id: 'venn', name: '⭕ Venn', color: '#06b6d4' },
    { id: 'tablas', name: '📋 Tablas', color: '#10b981' },
    { id: 'distribuciones', name: '📊 Distribuciones', color: '#f59e0b' },
    { id: 'graficos', name: '📈 Gráficos', color: '#ec4899' },
    { id: 'formulas', name: '🔣 Fórmulas', color: '#a855f7' },
    { id: 'datos', name: '🧪 Datos', color: '#14b8a6' }
  ];

  const elements = {
    arboles: [
      { symbol: '    ●\n   / \\\n  □   □\n / \\ / \\\n□  □□  □', name: 'Árbol 2 niveles', tooltip: 'Úsalo para decisiones y caminos posibles' },
      { symbol: '      ●\n     /|\\\n    □ □ □\n   /|\\', name: 'Árbol 3 ramas', tooltip: 'Para más opciones simultáneas' },
      { symbol: '[P=□] ●──→ □ [□]', name: 'Rama simple', tooltip: 'Una rama con probabilidad' },
      { symbol: '●──→[Sí:□]──→ □\n └──→[No:□]──→ □', name: 'Bifurcación', tooltip: 'Decisión binaria' },
      { symbol: 'Ω = {□, □, □}', name: 'Espacio muestral', tooltip: 'Todos los resultados posibles' }
    ],
    venn: [
      { symbol: '   A     B\n  ( ) ∩ ( )', name: 'A ∩ B', tooltip: 'Intersección de dos conjuntos' },
      { symbol: '  A ∪ B\n ( ( ) )', name: 'A ∪ B', tooltip: 'Unión de dos conjuntos' },
      { symbol: '    A\n  (   )\n B(   )\n  C(   )', name: 'A, B, C', tooltip: 'Tres conjuntos' },
      { symbol: '[A] = □%\n[B] = □%\n[A∩B] = □%', name: 'Probabilidades', tooltip: 'Con porcentajes editables' },
      { symbol: 'Aᶜ (complemento)', name: 'Complemento', tooltip: 'Todo excepto A' },
      { symbol: 'A - B (diferencia)', name: 'Diferencia', tooltip: 'A sin B' }
    ],
    tablas: [
      { symbol: '     | Sí | No |\n-----|-----|-----|\nH    | □  | □  |\nM    | □  | □  |', name: 'Tabla 2×2', tooltip: 'Para probabilidades conjuntas' },
      { symbol: '     | A  | B  | C  |\n-----|----|----|----|\n1    | □ | □ | □ |\n2    | □ | □ | □ |', name: 'Tabla 3×3', tooltip: 'Contingencia 3×3' },
      { symbol: 'P(A|B) = P(A∩B) / P(B)', name: 'Prob. condicional', tooltip: 'Probabilidad dado un evento' },
      { symbol: '       | Total\n-------|------\nTotal  | □', name: 'Con totales', tooltip: 'Suma automática' }
    ],
    distribuciones: [
      { symbol: 'N(μ=□, σ=□)', name: 'Normal', tooltip: 'Distribución normal (campana de Gauss)' },
      { symbol: 'Binomial(n=□, p=□)', name: 'Binomial', tooltip: 'Éxitos en n ensayos' },
      { symbol: 'Poisson(λ=□)', name: 'Poisson', tooltip: 'Eventos raros en intervalo' },
      { symbol: 'Exponencial(λ=□)', name: 'Exponencial', tooltip: 'Tiempo entre eventos' },
      { symbol: 'Uniforme[a=□, b=□]', name: 'Uniforme', tooltip: 'Todos los valores igualmente probables' },
      { symbol: 't-Student(gl=□)', name: 't-Student', tooltip: 'Para muestras pequeñas' },
      { symbol: 'χ²(gl=□)', name: 'Chi-cuadrado', tooltip: 'Pruebas de bondad de ajuste' },
      { symbol: '    /\\\n   /  \\\n  /    \\\n ▔▔▔▔▔▔', name: 'Campana Gauss', tooltip: 'Visualización de normal' }
    ],
    graficos: [
      { symbol: '┃ ▉\n┃ ▉ ▉\n┃▉▉▉▉\n└─────', name: 'Histograma', tooltip: 'Para ver distribución de datos' },
      { symbol: '┃   •\n┃  • \n┃ •  \n└─────', name: 'Dispersión', tooltip: 'Relación entre dos variables' },
      { symbol: '┃ ▉\n┃   ▉\n┃     ▉\n└─────', name: 'Barras', tooltip: 'Comparar categorías' },
      { symbol: '┃   /\n┃  / \n┃ /  \n└─────', name: 'Línea', tooltip: 'Tendencia en el tiempo' },
      { symbol: '┃ ●───●\n┃ │   │\n┃ ●───●\n└─────', name: 'Box plot', tooltip: 'Cuartiles y outliers' }
    ],
    formulas: [
      { symbol: 'P(A|B) = P(B|A)·P(A) / P(B)', name: 'Teorema de Bayes', tooltip: 'Probabilidad inversa' },
      { symbol: 'E[X] = Σ xᵢ·pᵢ', name: 'Esperanza', tooltip: 'Valor esperado promedio' },
      { symbol: 'Var(X) = E[X²] - (E[X])²', name: 'Varianza', tooltip: 'Dispersión de datos' },
      { symbol: 'σ = √Var(X)', name: 'Desv. estándar', tooltip: 'Raíz de la varianza' },
      { symbol: 'Cov(X,Y) = E[XY] - E[X]E[Y]', name: 'Covarianza', tooltip: 'Relación lineal entre variables' },
      { symbol: 'P(A∪B) = P(A) + P(B) - P(A∩B)', name: 'Prob. de unión', tooltip: 'Al menos uno ocurre' },
      { symbol: 'P(Total) = Σ P(Aᵢ)·P(B|Aᵢ)', name: 'Prob. total', tooltip: 'Partición del espacio muestral' },
      { symbol: 'C(n,k) = n! / (k!(n-k)!)', name: 'Combinaciones', tooltip: 'Elegir k de n sin orden' },
      { symbol: 'P(n,k) = n! / (n-k)!', name: 'Permutaciones', tooltip: 'Elegir k de n con orden' }
    ],
    datos: [
      { symbol: 'x  | y\n---|---\n□ | □\n□ | □\n□ | □', name: 'Dataset 2 col', tooltip: 'Pequeña tabla de datos' },
      { symbol: 'x̄ = Σxᵢ / n', name: 'Media', tooltip: 'Promedio aritmético' },
      { symbol: 'Me = valor central', name: 'Mediana', tooltip: 'Valor del medio' },
      { symbol: 'Mo = valor más frecuente', name: 'Moda', tooltip: 'Valor que más se repite' },
      { symbol: 'Q₁ | Me | Q₃', name: 'Cuartiles', tooltip: 'División en 4 partes iguales' },
      { symbol: 'IQR = Q₃ - Q₁', name: 'Rango intercuartil', tooltip: 'Dispersión central' }
    ]
  };

  return (
    <div style={{
      background: 'rgba(139, 92, 246, 0.03)',
      borderRadius: '12px',
      padding: '1rem',
      border: '1px solid rgba(139, 92, 246, 0.2)'
    }}>
      {/* TABS */}
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        marginBottom: '1rem',
        flexWrap: 'wrap',
        borderBottom: '2px solid rgba(139, 92, 246, 0.2)',
        paddingBottom: '0.75rem'
      }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            style={{
              background: activeTab === tab.id 
                ? `linear-gradient(135deg, ${tab.color}30 0%, ${tab.color}15 100%)`
                : 'rgba(30, 41, 59, 0.4)',
              color: activeTab === tab.id ? tab.color : '#94a3b8',
              border: activeTab === tab.id ? `2px solid ${tab.color}` : '2px solid transparent',
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '0.85rem',
              fontWeight: activeTab === tab.id ? '700' : '600',
              transition: 'all 0.2s',
              whiteSpace: 'nowrap'
            }}
            onMouseEnter={(e) => {
              if (activeTab !== tab.id) {
                e.currentTarget.style.background = `rgba(${parseInt(tab.color.slice(1,3), 16)}, ${parseInt(tab.color.slice(3,5), 16)}, ${parseInt(tab.color.slice(5,7), 16)}, 0.15)`;
              }
            }}
            onMouseLeave={(e) => {
              if (activeTab !== tab.id) {
                e.currentTarget.style.background = 'rgba(30, 41, 59, 0.4)';
              }
            }}
          >
            {tab.name}
          </button>
        ))}
      </div>

      {/* ELEMENTOS */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))',
        gap: '0.75rem',
        maxHeight: '280px',
        overflowY: 'auto',
        padding: '0.5rem'
      }}>
        {elements[activeTab]?.map((elem, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => onInsertElement(elem.symbol)}
            style={{
              background: 'rgba(30, 41, 59, 0.6)',
              border: '2px solid rgba(139, 92, 246, 0.3)',
              borderRadius: '10px',
              padding: '0.75rem 0.5rem',
              cursor: 'pointer',
              transition: 'all 0.2s',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '0.5rem',
              minHeight: '90px'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(139, 92, 246, 0.15)';
              e.currentTarget.style.borderColor = '#8b5cf6';
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 8px 20px rgba(139, 92, 246, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(30, 41, 59, 0.6)';
              e.currentTarget.style.borderColor = 'rgba(139, 92, 246, 0.3)';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
            title={elem.tooltip}
          >
            <pre style={{
              color: '#c4b5fd',
              fontSize: '0.7rem',
              fontFamily: 'monospace',
              lineHeight: '1.2',
              margin: 0,
              whiteSpace: 'pre',
              textAlign: 'center',
              maxWidth: '100%',
              overflow: 'hidden'
            }}>
              {elem.symbol.substring(0, 60)}
            </pre>
            <span style={{
              color: '#a78bfa',
              fontSize: '0.7rem',
              fontWeight: '600',
              textAlign: 'center',
              lineHeight: '1.2'
            }}>
              {elem.name}
            </span>
          </button>
        ))}
      </div>

      {/* GUÍA */}
      <div style={{
        marginTop: '1rem',
        padding: '0.75rem',
        background: 'rgba(139, 92, 246, 0.08)',
        borderRadius: '8px',
        fontSize: '0.8rem',
        color: '#c4b5fd',
        lineHeight: '1.5'
      }}>
        <strong style={{color: '#a78bfa'}}>💡 Cómo usar:</strong><br/>
        {activeTab === 'arboles' && '• Haz clic en un árbol para insertarlo. Los □ son editables para poner probabilidades.'}
        {activeTab === 'venn' && '• Inserta diagramas de Venn. Útil para A∩B, A∪B, complementos.'}
        {activeTab === 'tablas' && '• Tablas de contingencia para probabilidades conjuntas y condicionales.'}
        {activeTab === 'distribuciones' && '• Elige una distribución y completa sus parámetros (μ, σ, λ, n, p...).'}
        {activeTab === 'graficos' && '• Visualiza datos con histogramas, dispersión, barras o box plots.'}
        {activeTab === 'formulas' && '• Fórmulas esenciales: Bayes, esperanza, varianza, covarianza... Completa los valores.'}
        {activeTab === 'datos' && '• Crea mini datasets y calcula media, mediana, moda, cuartiles...'}
      </div>
    </div>
  );
}
