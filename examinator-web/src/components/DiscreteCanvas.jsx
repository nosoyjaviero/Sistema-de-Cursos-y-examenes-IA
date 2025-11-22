import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({ 
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    primaryColor: '#7c3aed',
    primaryTextColor: '#e9d5ff',
    primaryBorderColor: '#5b21b6',
    lineColor: '#a78bfa',
    secondaryColor: '#c4b5fd',
    background: '#1e1b4b',
    mainBkg: '#312e81',
    textColor: '#e9d5ff'
  }
});

const DiscreteCanvas = ({ value, onChange, placeholder }) => {
  const [renderMode, setRenderMode] = useState('visual');
  const mermaidRef = useRef(null);

  const convertToMermaid = (text) => {
    if (!text.trim()) return '';
    
    // Si ya tiene sintaxis Mermaid, devolverlo
    if (text.includes('graph ') || text.includes('flowchart')) {
      return text;
    }

    // Convertir sintaxis natural a Mermaid para grafos
    if (text.includes('[Nodo]') || text.includes('[Arista]')) {
      return convertToGraph(text);
    }

    // Para tablas de verdad y otras estructuras lógicas, mostrar como texto formateado
    return null;
  };

  const convertToGraph = (text) => {
    let mermaid = 'graph TD\n';
    const lines = text.split('\n');
    const nodes = new Set();
    
    lines.forEach(line => {
      if (line.includes('[Nodo]')) {
        const match = line.match(/\[Nodo\]\s*(\w+)/);
        if (match) {
          nodes.add(match[1]);
          mermaid += `  ${match[1]}\n`;
        }
      } else if (line.includes('[Arista]') || line.includes('-->')) {
        const match = line.match(/(\w+)\s*-->\s*(\w+)/);
        if (match) {
          mermaid += `  ${match[1]} --> ${match[2]}\n`;
        }
      }
    });
    
    return mermaid;
  };

  useEffect(() => {
    if (renderMode === 'visual' && value && mermaidRef.current) {
      const code = convertToMermaid(value);
      
      if (code) {
        mermaid.render('discrete-diagram', code)
          .then(({ svg }) => {
            mermaidRef.current.innerHTML = svg;
          })
          .catch((err) => {
            mermaidRef.current.innerHTML = `<pre style="color: #94a3b8; font-size: 0.85rem;">Modo visual para grafos/árboles. Para lógica/conjuntos usa modo texto.</pre>`;
          });
      } else {
        mermaidRef.current.innerHTML = `<pre style="color: #94a3b8; font-size: 0.85rem;">Vista texto recomendada para lógica y conjuntos.</pre>`;
      }
    }
  }, [value, renderMode]);

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
      {/* Controles */}
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <label style={{fontSize: '0.9rem', fontWeight: '600', color: '#c4b5fd'}}>
          🔍 Editor de Lógica/Discreta
        </label>
        <div style={{display: 'flex', gap: '0.5rem'}}>
          <button
            type="button"
            onClick={() => setRenderMode('visual')}
            style={{
              padding: '0.4rem 0.8rem',
              background: renderMode === 'visual' ? 'linear-gradient(135deg, #7c3aed, #5b21b6)' : 'rgba(124, 58, 237, 0.2)',
              border: '1px solid rgba(124, 58, 237, 0.4)',
              borderRadius: '6px',
              color: '#e9d5ff',
              fontSize: '0.75rem',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            🎨 Grafos
          </button>
          <button
            type="button"
            onClick={() => setRenderMode('text')}
            style={{
              padding: '0.4rem 0.8rem',
              background: renderMode === 'text' ? 'linear-gradient(135deg, #7c3aed, #5b21b6)' : 'rgba(124, 58, 237, 0.2)',
              border: '1px solid rgba(124, 58, 237, 0.4)',
              borderRadius: '6px',
              color: '#e9d5ff',
              fontSize: '0.75rem',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            📝 Lógica/Sets
          </button>
        </div>
      </div>

      {/* Editor de texto */}
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder || "Escribe lógica, conjuntos, grafos o tablas de verdad...\n\n🔷 Grafos/Árboles:\n[Nodo] A\n[Nodo] B\n[Arista] A --> B\n\n🔷 Lógica:\n¬p ∨ q\np → q ≡ ¬p ∨ q\n∀x (P(x) → Q(x))\n\n🔷 Conjuntos:\nA = {1, 2, 3}\nB = {2, 3, 4}\nA ∪ B = {1, 2, 3, 4}\nA ∩ B = {2, 3}\n\n🔷 Tabla Verdad:\np | q | p∧q | p∨q\nV | V | V   | V\nV | F | F   | V"}
        style={{
          minHeight: '200px',
          padding: '1rem',
          background: 'rgba(17, 24, 39, 0.5)',
          border: '1px solid rgba(124, 58, 237, 0.3)',
          borderRadius: '8px',
          color: '#e9d5ff',
          fontFamily: 'monospace',
          fontSize: '0.9rem',
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
          {renderMode === 'visual' ? '🎨 Diagrama' : '📝 Formato'}
        </div>
        
        {renderMode === 'visual' ? (
          <div ref={mermaidRef} style={{
            background: '#1e1b4b',
            borderRadius: '6px',
            padding: '1rem',
            minHeight: '150px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            {!value && <span style={{color: '#94a3b8'}}>Escribe un grafo arriba...</span>}
          </div>
        ) : (
          <pre style={{
            margin: 0,
            color: '#e9d5ff',
            fontFamily: 'monospace',
            fontSize: '0.95rem',
            lineHeight: '1.9',
            whiteSpace: 'pre-wrap',
            wordWrap: 'break-word',
            letterSpacing: '0.3px'
          }}>
            {value ? renderMixedContent(value) : '(Vacío - Comienza a escribir arriba)'}
          </pre>
        )}
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
