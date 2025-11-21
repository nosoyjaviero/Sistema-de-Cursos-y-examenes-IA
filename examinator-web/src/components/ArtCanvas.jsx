import { useState } from 'react';

const ArtCanvas = ({ value, onChange }) => {
  const [showPreview, setShowPreview] = useState(true);
  const [showTimeline, setShowTimeline] = useState(false);
  const [showPrompts, setShowPrompts] = useState(false);

  const timelinePeriodos = [
    { periodo: 'Renacimiento', años: '1400-1600', artistas: 'Leonardo, Miguel Ángel, Rafael', color: '#f59e0b' },
    { periodo: 'Barroco', años: '1600-1750', artistas: 'Caravaggio, Rembrandt, Velázquez', color: '#ef4444' },
    { periodo: 'Romanticismo', años: '1780-1850', artistas: 'Delacroix, Turner, Goya', color: '#ec4899' },
    { periodo: 'Impresionismo', años: '1860-1890', artistas: 'Monet, Renoir, Degas', color: '#8b5cf6' },
    { periodo: 'Vanguardias', años: '1900-1950', artistas: 'Picasso, Kandinsky, Dalí', color: '#06b6d4' }
  ];

  const promptsVisuales = [
    '🔷 Describe esta idea usando solo geometría básica',
    '🎨 Transforma este concepto en un collage visual',
    '❤️ Crea un mapa emocional de este tema',
    '🌊 Piensa en este problema como un flujo de agua',
    '🏗️ Construye una arquitectura visual de la información',
    '🌳 Dibuja este sistema como un árbol ramificado',
    '⚡ Representa este proceso como una cadena de energía',
    '🎭 Diseña una metáfora visual teatral'
  ];

  const analogiasVisuales = [
    { concepto: 'Blockchain', analogia: '🔗 Cadena de cajas transparentes conectadas', uso: 'Para explicar tecnología' },
    { concepto: 'Modelo atómico', analogia: '🪐 Sistema solar en miniatura', uso: 'Para ciencias' },
    { concepto: 'Neurona', analogia: '🌳 Árbol eléctrico con ramas', uso: 'Para biología' },
    { concepto: 'Internet', analogia: '🕸️ Telaraña global conectada', uso: 'Para tecnología' },
    { concepto: 'Memoria', analogia: '📚 Biblioteca con archivos', uso: 'Para psicología' },
    { concepto: 'Economía', analogia: '💧 Flujo circular de agua/dinero', uso: 'Para finanzas' }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* Controles superiores */}
      <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
        <button
          onClick={() => setShowPreview(!showPreview)}
          style={{
            padding: '0.6rem 1.2rem',
            background: showPreview ? 'rgba(59, 130, 246, 0.15)' : 'rgba(100, 116, 139, 0.1)',
            border: showPreview ? '2px solid #3b82f6' : '2px solid rgba(148, 163, 184, 0.2)',
            borderRadius: '8px',
            color: showPreview ? '#60a5fa' : '#94a3b8',
            cursor: 'pointer',
            fontSize: '0.85rem',
            fontWeight: '600'
          }}
        >
          {showPreview ? '👁️ Vista previa' : '✏️ Solo editor'}
        </button>

        <button
          onClick={() => setShowTimeline(!showTimeline)}
          style={{
            padding: '0.6rem 1.2rem',
            background: 'rgba(245, 158, 11, 0.1)',
            border: '2px solid rgba(245, 158, 11, 0.3)',
            borderRadius: '8px',
            color: '#fbbf24',
            cursor: 'pointer',
            fontSize: '0.85rem',
            fontWeight: '600'
          }}
        >
          📅 Timeline Historia del Arte
        </button>

        <button
          onClick={() => setShowPrompts(!showPrompts)}
          style={{
            padding: '0.6rem 1.2rem',
            background: 'rgba(139, 92, 246, 0.1)',
            border: '2px solid rgba(139, 92, 246, 0.3)',
            borderRadius: '8px',
            color: '#a78bfa',
            cursor: 'pointer',
            fontSize: '0.85rem',
            fontWeight: '600'
          }}
        >
          💡 Prompts & Analogías
        </button>
      </div>

      {/* Timeline de Historia del Arte */}
      {showTimeline && (
        <div style={{
          background: 'rgba(245, 158, 11, 0.05)',
          padding: '1.5rem',
          borderRadius: '10px',
          border: '2px solid rgba(245, 158, 11, 0.2)'
        }}>
          <h4 style={{ color: '#fbbf24', marginBottom: '1rem', fontSize: '1rem' }}>
            📅 Línea de Tiempo del Arte
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {timelinePeriodos.map((per, idx) => (
              <button
                key={idx}
                onClick={() => {
                  const timeline = `📅 ${per.periodo} (${per.años})\n   Artistas: ${per.artistas}\n   Obras: □\n   Conceptos: □`;
                  onChange(value + '\n\n' + timeline);
                }}
                style={{
                  padding: '1rem',
                  background: `linear-gradient(90deg, ${per.color}20, ${per.color}05)`,
                  border: `2px solid ${per.color}40`,
                  borderRadius: '8px',
                  textAlign: 'left',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateX(5px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateX(0)';
                }}
              >
                <div style={{ color: per.color, fontWeight: '600', fontSize: '0.95rem', marginBottom: '0.25rem' }}>
                  {per.periodo} ({per.años})
                </div>
                <div style={{ color: '#94a3b8', fontSize: '0.8rem' }}>
                  {per.artistas}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Prompts visuales y Analogías */}
      {showPrompts && (
        <div style={{
          background: 'rgba(139, 92, 246, 0.05)',
          padding: '1.5rem',
          borderRadius: '10px',
          border: '2px solid rgba(139, 92, 246, 0.2)'
        }}>
          <h4 style={{ color: '#a78bfa', marginBottom: '1rem', fontSize: '1rem' }}>
            💡 Prompts para Pensamiento Visual
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '0.75rem', marginBottom: '1.5rem' }}>
            {promptsVisuales.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => onChange(value + '\n\n' + prompt + '\n□')}
                style={{
                  padding: '0.75rem',
                  background: 'rgba(139, 92, 246, 0.08)',
                  border: '2px solid rgba(139, 92, 246, 0.2)',
                  borderRadius: '8px',
                  color: '#c4b5fd',
                  cursor: 'pointer',
                  fontSize: '0.85rem',
                  textAlign: 'left',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(139, 92, 246, 0.15)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(139, 92, 246, 0.08)';
                }}
              >
                {prompt}
              </button>
            ))}
          </div>

          <h4 style={{ color: '#a78bfa', marginBottom: '1rem', fontSize: '1rem', marginTop: '1.5rem' }}>
            🎯 Analogías Visuales Pre-armadas
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {analogiasVisuales.map((ana, idx) => (
              <button
                key={idx}
                onClick={() => {
                  const texto = `${ana.analogia}\n  Concepto: ${ana.concepto}\n  Uso: ${ana.uso}`;
                  onChange(value + '\n\n' + texto);
                }}
                style={{
                  padding: '0.75rem 1rem',
                  background: 'rgba(139, 92, 246, 0.08)',
                  border: '2px solid rgba(139, 92, 246, 0.2)',
                  borderRadius: '8px',
                  textAlign: 'left',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(139, 92, 246, 0.15)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(139, 92, 246, 0.08)';
                }}
              >
                <div style={{ color: '#c4b5fd', fontWeight: '600', marginBottom: '0.25rem' }}>
                  {ana.analogia}
                </div>
                <div style={{ color: '#94a3b8', fontSize: '0.8rem' }}>
                  Explica: <span style={{ color: '#a78bfa' }}>{ana.concepto}</span> • {ana.uso}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Editor */}
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Crea tu composición artística aquí...&#10;&#10;Usa las herramientas de arriba para insertar:&#10;  • Figuras y formas&#10;  • Paletas de color&#10;  • Layouts prearmados&#10;  • Estilos artísticos&#10;  • Iconos temáticos&#10;&#10;Todo editable con □ placeholders"
        style={{
          width: '100%',
          minHeight: showPreview ? '200px' : '400px',
          padding: '1rem',
          background: 'rgba(30, 41, 59, 0.5)',
          border: '2px solid rgba(148, 163, 184, 0.2)',
          borderRadius: '8px',
          color: '#e2e8f0',
          fontSize: '0.95rem',
          fontFamily: 'monospace',
          lineHeight: '1.8',
          resize: 'vertical'
        }}
      />

      {/* Preview */}
      {showPreview && (
        <div style={{
          padding: '1.5rem',
          background: 'rgba(100, 116, 139, 0.08)',
          borderRadius: '10px',
          border: '2px solid rgba(148, 163, 184, 0.15)',
          minHeight: '150px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            marginBottom: '1rem',
            paddingBottom: '0.75rem',
            borderBottom: '1px solid rgba(148, 163, 184, 0.2)'
          }}>
            <span style={{ fontSize: '1.2rem' }}>👁️</span>
            <span style={{ color: '#94a3b8', fontSize: '0.9rem', fontWeight: '600' }}>
              Vista Previa
            </span>
          </div>
          <div style={{
            color: '#cbd5e1',
            fontSize: '1.1rem',
            lineHeight: '2',
            whiteSpace: 'pre-wrap',
            fontFamily: 'monospace'
          }}>
            {value || (
              <span style={{ color: '#64748b', fontStyle: 'italic' }}>
                La composición aparecerá aquí...
              </span>
            )}
          </div>
        </div>
      )}

      {/* Guía de uso */}
      <div style={{
        background: 'rgba(16, 185, 129, 0.08)',
        padding: '1rem',
        borderRadius: '8px',
        fontSize: '0.85rem',
        color: '#6ee7b7',
        lineHeight: '1.6'
      }}>
        <strong style={{ color: '#10b981' }}>🎨 Guía rápida:</strong><br />
        • <strong>Figuras:</strong> Insertar formas SVG editables (círculo, cuadrado, flechas)<br />
        • <strong>Paletas:</strong> Aplicar esquemas de color profesionales<br />
        • <strong>Layouts:</strong> Composiciones prearmadas (2 columnas, caja+texto, diagonal)<br />
        • <strong>Estilos:</strong> Filtros artísticos (Impresionismo, Cubismo, Pop Art)<br />
        • <strong>Timeline:</strong> Historia del arte con periodos editables<br />
        • <strong>Prompts:</strong> Generador de ideas visuales y analogías
      </div>
    </div>
  );
};

export default ArtCanvas;
