const DiscreteCanvas = ({ value, onChange, placeholder }) => {
  return (
    <div style={{
      background: 'rgba(124, 58, 237, 0.05)',
      border: '2px solid rgba(124, 58, 237, 0.3)',
      borderRadius: '10px',
      padding: '1rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem'
    }}>
      {/* Editor de texto */}
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder || "Describe tu problema de lógica/discreta usando símbolos...\n\nEjemplo Lógica:\n¬p ∨ q\np → q ≡ ¬p ∨ q\n∀x (P(x) → Q(x))\n\nEjemplo Conjuntos:\nA = {1, 2, 3}\nB = {2, 3, 4}\nA ∪ B = {1, 2, 3, 4}\nA ∩ B = {2, 3}\n\nEjemplo Relación:\nR = {(1,2), (2,3), (1,3)}\nReflexiva: No\nTransitiva: Sí\n\nEjemplo Tabla Verdad:\np | q | p∧q | p∨q\nV | V | V   | V\nV | F | F   | V\nF | V | F   | V\nF | F | F   | F"}
        style={{
          minHeight: '250px',
          padding: '1rem',
          background: 'rgba(17, 24, 39, 0.5)',
          border: '1px solid rgba(124, 58, 237, 0.3)',
          borderRadius: '8px',
          color: '#e9d5ff',
          fontFamily: 'monospace',
          fontSize: '0.95rem',
          lineHeight: '1.6',
          resize: 'vertical',
          width: '100%'
        }}
      />

      {/* Vista previa */}
      <div style={{
        background: 'rgba(17, 24, 39, 0.5)',
        border: '1px solid rgba(124, 58, 237, 0.3)',
        borderRadius: '8px',
        padding: '1rem',
        minHeight: '150px'
      }}>
        <div style={{
          fontSize: '0.85rem',
          fontWeight: '600',
          color: '#c4b5fd',
          marginBottom: '0.75rem',
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }}>
          🔍 Vista Previa
        </div>
        <pre style={{
          margin: 0,
          color: '#e9d5ff',
          fontFamily: 'monospace',
          fontSize: '0.9rem',
          lineHeight: '1.8',
          whiteSpace: 'pre-wrap',
          wordWrap: 'break-word'
        }}>
          {value || '(Vacío - Comienza a escribir arriba)'}
        </pre>
      </div>

      {/* Guía rápida */}
      <div style={{
        padding: '1rem',
        background: 'rgba(124, 58, 237, 0.08)',
        borderLeft: '4px solid #7c3aed',
        borderRadius: '8px',
        fontSize: '0.85rem',
        color: '#ddd6fe',
        lineHeight: '1.6'
      }}>
        <strong style={{color: '#e9d5ff'}}>💡 Símbolos disponibles:</strong><br/>
        
        <div style={{marginTop: '0.5rem', display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.4rem'}}>
          <div>
            <strong style={{color: '#c4b5fd'}}>Lógica:</strong> ¬ ∧ ∨ → ↔ ⊕ ⊤ ⊥
          </div>
          <div>
            <strong style={{color: '#c4b5fd'}}>Cuantif.:</strong> ∀ ∃ ⊢ ⊨ ∴
          </div>
          <div>
            <strong style={{color: '#c4b5fd'}}>Conjuntos:</strong> ∪ ∩ ⊂ ⊆ ∈ ∉ ∅
          </div>
          <div>
            <strong style={{color: '#c4b5fd'}}>Números:</strong> ℕ ℤ ℚ ℝ
          </div>
        </div>

        <div style={{marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(124, 58, 237, 0.2)'}}>
          <strong style={{color: '#e9d5ff'}}>📋 Ejemplos rápidos:</strong><br/>
          <code style={{background: 'rgba(124, 58, 237, 0.2)', padding: '2px 6px', borderRadius: '4px', color: '#c4b5fd'}}>
            p → q ≡ ¬p ∨ q
          </code> - Equivalencia lógica<br/>
          <code style={{background: 'rgba(124, 58, 237, 0.2)', padding: '2px 6px', borderRadius: '4px', color: '#c4b5fd'}}>
            A ∩ B ⊆ A ∪ B
          </code> - Conjuntos<br/>
          <code style={{background: 'rgba(124, 58, 237, 0.2)', padding: '2px 6px', borderRadius: '4px', color: '#c4b5fd'}}>
            ∀x (x ∈ A → x ∈ B)
          </code> - Predicados
        </div>

        <div style={{marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(124, 58, 237, 0.2)'}}>
          <strong style={{color: '#e9d5ff'}}>🎯 Categorías:</strong> 🟪 Lógica • 🟫 Conjuntos • 🟩 Venn • 🟦 Relaciones • 🔵 Grafos • 🟠 Predicados
        </div>
      </div>
    </div>
  );
};

export default DiscreteCanvas;
