import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({ 
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    primaryColor: '#8b5cf6',
    primaryTextColor: '#e9d5ff',
    primaryBorderColor: '#6d28d9',
    lineColor: '#a78bfa',
    secondaryColor: '#c4b5fd',
    tertiaryColor: '#ddd6fe',
    background: '#1e1b4b',
    mainBkg: '#312e81',
    textColor: '#e9d5ff',
    fontSize: '14px'
  }
});

const ProgrammingCanvas = ({ value, onChange, placeholder }) => {
  const [renderMode, setRenderMode] = useState('visual'); // 'visual' o 'text'
  const mermaidRef = useRef(null);
  const [mermaidCode, setMermaidCode] = useState('');
  const [parseError, setParseError] = useState(null);

  // Convertir sintaxis natural a Mermaid
  const convertToMermaid = (text) => {
    if (!text.trim()) return '';
    
    // Si ya parece código Mermaid válido, devolverlo tal cual
    if (text.match(/^(classDiagram|flowchart|graph|stateDiagram|sequenceDiagram|erDiagram|gantt|pie)/m)) {
      return text;
    }
    
    // Detectar tipo de diagrama por palabras clave
    if (text.includes('[Clase]') || text.includes('[Método]') || text.includes('[Atributo]')) {
      return convertToClassDiagram(text);
    } else if (text.includes('[Inicio]') || text.includes('[Proceso]') || text.includes('[Decisión]') || text.includes('[Fin]')) {
      return convertToFlowchart(text);
    } else if (text.includes('[Nodo]') || text.includes('[Arista]')) {
      return convertToGraph(text);
    } else if (text.includes('[Estado')) {
      return convertToStateDiagram(text);
    }
    
    // Si no se detecta nada, crear un diagrama de clase simple con el texto
    return `classDiagram\n  note "Texto sin formato detectado:\n${text.split('\n').slice(0, 5).join('\\n')}"`;
  };

  const convertToClassDiagram = (text) => {
    let mermaid = 'classDiagram\n';
    const lines = text.split('\n');
    let currentClass = null;
    
    lines.forEach(line => {
      const trimmed = line.trim();
      if (!trimmed) return;
      
      if (trimmed.includes('[Clase]')) {
        const match = trimmed.match(/\[Clase\]\s*(\w+)/);
        if (match) {
          currentClass = match[1];
          mermaid += `  class ${currentClass}\n`;
        }
      } else if (trimmed.includes('[Método]') && currentClass) {
        const match = trimmed.match(/\[Método\]\s*(.+)/);
        if (match) {
          mermaid += `  ${currentClass} : ${match[1]}\n`;
        }
      } else if (trimmed.includes('[Atributo]') && currentClass) {
        const match = trimmed.match(/\[Atributo\]\s*(.+)/);
        if (match) {
          mermaid += `  ${currentClass} : ${match[1]}\n`;
        }
      } else if (trimmed.includes('[Herencia]')) {
        const match = trimmed.match(/(\w+)\s*--|>\s*(\w+)/);
        if (match) mermaid += `  ${match[2]} <|-- ${match[1]}\n`;
      }
    });
    
    return mermaid;
  };

  const convertToFlowchart = (text) => {
    let mermaid = 'flowchart TD\n';
    const lines = text.split('\n');
    let nodeId = 0;
    
    lines.forEach(line => {
      if (line.includes('[Inicio]')) {
        const content = line.replace('[Inicio]', '').trim();
        mermaid += `  A${nodeId}([${content}])\n`;
        nodeId++;
      } else if (line.includes('[Proceso]')) {
        const content = line.replace('[Proceso]', '').trim();
        mermaid += `  A${nodeId}[${content}]\n`;
        nodeId++;
      } else if (line.includes('[Decisión]')) {
        const content = line.replace('[Decisión]', '').trim();
        mermaid += `  A${nodeId}{${content}}\n`;
        nodeId++;
      } else if (line.includes('[Fin]')) {
        const content = line.replace('[Fin]', '').trim();
        mermaid += `  A${nodeId}([${content}])\n`;
        nodeId++;
      }
    });
    
    return mermaid;
  };

  const convertToGraph = (text) => {
    let mermaid = 'graph TD\n';
    const lines = text.split('\n');
    
    lines.forEach(line => {
      if (line.includes('[Nodo]')) {
        const match = line.match(/\[Nodo\]\s*(\w+)/);
        if (match) mermaid += `  ${match[1]}\n`;
      } else if (line.includes('[Arista]') || line.includes('-->')) {
        const match = line.match(/(\w+)\s*-->\s*(\w+)/);
        if (match) mermaid += `  ${match[1]} --> ${match[2]}\n`;
      }
    });
    
    return mermaid;
  };

  const convertToStateDiagram = (text) => {
    let mermaid = 'stateDiagram-v2\n';
    const lines = text.split('\n');
    
    lines.forEach(line => {
      if (line.includes('[Estado Inicial]')) {
        const match = line.match(/\[Estado Inicial\]\s*(\w+)/);
        if (match) mermaid += `  [*] --> ${match[1]}\n`;
      } else if (line.includes('[Transición]')) {
        const match = line.match(/(\w+)\s*--(\w+)-->\s*(\w+)/);
        if (match) mermaid += `  ${match[1]} --> ${match[3]} : ${match[2]}\n`;
      } else if (line.includes('[Estado Aceptación]')) {
        const match = line.match(/\[Estado Aceptación\]\s*(\w+)/);
        if (match) mermaid += `  ${match[1]} --> [*]\n`;
      }
    });
    
    return mermaid;
  };

  useEffect(() => {
    if (renderMode === 'visual' && value && mermaidRef.current) {
      const code = convertToMermaid(value);
      setMermaidCode(code);
      
      mermaid.render('mermaid-diagram', code)
        .then(({ svg }) => {
          mermaidRef.current.innerHTML = svg;
          setParseError(null);
        })
        .catch((err) => {
          setParseError(err.message);
          mermaidRef.current.innerHTML = `<pre style="color: #ef4444;">${err.message}</pre>`;
        });
    }
  }, [value, renderMode]);

  return (
    <div style={{
      background: 'rgba(139, 92, 246, 0.05)',
      border: '2px solid rgba(139, 92, 246, 0.3)',
      borderRadius: '10px',
      padding: '1rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem'
    }}>
      {/* Controles */}
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <label style={{fontSize: '0.9rem', fontWeight: '600', color: '#c4b5fd'}}>
          💻 Editor de Diagramas
        </label>
        <div style={{display: 'flex', gap: '0.5rem'}}>
          <button
            type="button"
            onClick={() => setRenderMode('visual')}
            style={{
              padding: '0.4rem 0.8rem',
              background: renderMode === 'visual' ? 'linear-gradient(135deg, #8b5cf6, #6d28d9)' : 'rgba(139, 92, 246, 0.2)',
              border: '1px solid rgba(139, 92, 246, 0.4)',
              borderRadius: '6px',
              color: '#e9d5ff',
              fontSize: '0.75rem',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            🎨 Visual
          </button>
          <button
            type="button"
            onClick={() => setRenderMode('text')}
            style={{
              padding: '0.4rem 0.8rem',
              background: renderMode === 'text' ? 'linear-gradient(135deg, #8b5cf6, #6d28d9)' : 'rgba(139, 92, 246, 0.2)',
              border: '1px solid rgba(139, 92, 246, 0.4)',
              borderRadius: '6px',
              color: '#e9d5ff',
              fontSize: '0.75rem',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            📝 Texto
          </button>
        </div>
      </div>

      {/* Editor de texto descriptivo */}
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder || "Escribe en lenguaje natural o código Mermaid directo...\n\n🔷 Lenguaje natural:\n[Clase] Usuario\n[Clase] Producto\n[Herencia] Usuario --|> Persona\n\n[Inicio] Login\n[Proceso] Validar\n[Decisión] ¿Válido?\n[Fin] Acceso\n\n🔷 O usa Mermaid directo:\nclassDiagram\n  class Usuario\n  class Producto\n  Usuario <|-- Persona\n\nflowchart TD\n  A[Login] --> B[Validar]\n  B --> C{¿Válido?}\n  C -->|Sí| D[Acceso]\n  C -->|No| E[Error]"}
        style={{
          minHeight: '200px',
          padding: '1rem',
          background: 'rgba(17, 24, 39, 0.5)',
          border: '1px solid rgba(139, 92, 246, 0.3)',
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
        border: '1px solid rgba(139, 92, 246, 0.3)',
        borderRadius: '8px',
        padding: '1rem',
        minHeight: '200px'
      }}>
        <div style={{
          fontSize: '0.85rem',
          fontWeight: '600',
          color: '#c4b5fd',
          marginBottom: '0.75rem',
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }}>
          {renderMode === 'visual' ? '🎨 Diagrama Renderizado' : '📝 Vista Texto'}
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
            {!value && <span style={{color: '#94a3b8'}}>Escribe arriba para ver el diagrama...</span>}
          </div>
        ) : (
          <pre style={{
            margin: 0,
            color: '#e9d5ff',
            fontFamily: 'monospace',
            fontSize: '0.9rem',
            lineHeight: '1.8',
            whiteSpace: 'pre-wrap',
            wordWrap: 'break-word'
          }}>
            {value ? renderMixedContent(value) : '(Vacío - Comienza a escribir arriba)'}
          </pre>
        )}
      </div>

      {/* Guía rápida */}
      <div style={{
        padding: '1rem',
        background: 'rgba(139, 92, 246, 0.08)',
        borderLeft: '4px solid #8b5cf6',
        borderRadius: '8px',
        fontSize: '0.85rem',
        color: '#ddd6fe',
        lineHeight: '1.6'
      }}>
        <strong style={{color: '#e9d5ff'}}>💡 Sintaxis soportada:</strong><br/>
        
        <div style={{marginTop: '0.5rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem'}}>
          <div>
            <strong style={{color: '#c4b5fd'}}>Lenguaje Natural:</strong><br/>
            <code style={{background: 'rgba(139, 92, 246, 0.2)', padding: '2px 6px', borderRadius: '4px'}}>
              [Clase] Usuario
            </code><br/>
            <code style={{background: 'rgba(139, 92, 246, 0.2)', padding: '2px 6px', borderRadius: '4px'}}>
              [Proceso] Validar
            </code><br/>
            <code style={{background: 'rgba(139, 92, 246, 0.2)', padding: '2px 6px', borderRadius: '4px'}}>
              [Nodo] A
            </code>
          </div>
          <div>
            <strong style={{color: '#c4b5fd'}}>Mermaid Directo:</strong><br/>
            <code style={{background: 'rgba(139, 92, 246, 0.2)', padding: '2px 6px', borderRadius: '4px'}}>
              classDiagram
            </code><br/>
            <code style={{background: 'rgba(139, 92, 246, 0.2)', padding: '2px 6px', borderRadius: '4px'}}>
              flowchart TD
            </code><br/>
            <code style={{background: 'rgba(139, 92, 246, 0.2)', padding: '2px 6px', borderRadius: '4px'}}>
              stateDiagram-v2
            </code>
          </div>
        </div>

        <div style={{marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(139, 92, 246, 0.2)'}}>
          <strong style={{color: '#e9d5ff'}}>🎯 Tipos de diagrama:</strong><br/>
          🟣 Clases UML • 🟡 Flujos • 🟩 Grafos • 🔵 Autómatas • 🟠 Secuencia
        </div>
      </div>
    </div>
  );
};

export default ProgrammingCanvas;
