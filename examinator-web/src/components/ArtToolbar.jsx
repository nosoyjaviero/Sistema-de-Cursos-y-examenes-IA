import { useState } from 'react';

const ArtToolbar = ({ onInsertElement }) => {
  const [activeTab, setActiveTab] = useState('figuras');

  const tabs = [
    { id: 'figuras', nombre: '🔷 Figuras', color: '#3b82f6' },
    { id: 'paletas', nombre: '🎨 Paletas', color: '#ec4899' },
    { id: 'composiciones', nombre: '📐 Layouts', color: '#8b5cf6' },
    { id: 'estilos', nombre: '🖼️ Estilos', color: '#f59e0b' },
    { id: 'iconos', nombre: '✨ Iconos', color: '#10b981' }
  ];

  const elementos = {
    figuras: [
      { nombre: 'Círculo', simbolo: '●', template: '⬤ (tamaño: □)' },
      { nombre: 'Cuadrado', simbolo: '■', template: '◼ (tamaño: □)' },
      { nombre: 'Triángulo', simbolo: '▲', template: '▲ (tamaño: □)' },
      { nombre: 'Rectángulo', simbolo: '▭', template: '▬ (ancho: □, alto: □)' },
      { nombre: 'Rectángulo redondeado', simbolo: '▢', template: '▢ (ancho: □, alto: □, radio: □)' },
      { nombre: 'Línea recta', simbolo: '─', template: '━━━━━ (longitud: □)' },
      { nombre: 'Línea curva', simbolo: '〰', template: '〰️〰️〰️ (amplitud: □)' },
      { nombre: 'Flecha derecha', simbolo: '→', template: '➡️ (tamaño: □)' },
      { nombre: 'Flecha izquierda', simbolo: '←', template: '⬅️ (tamaño: □)' },
      { nombre: 'Flecha arriba', simbolo: '↑', template: '⬆️ (tamaño: □)' },
      { nombre: 'Flecha abajo', simbolo: '↓', template: '⬇️ (tamaño: □)' },
      { nombre: 'Estrella', simbolo: '★', template: '⭐ (tamaño: □, puntas: □)' }
    ],
    paletas: [
      { 
        nombre: 'Pastel', 
        colores: ['#ffd1dc', '#ffb3ba', '#bae1ff', '#baffc9', '#ffffba'],
        preview: '🧁',
        descripcion: 'Suaves y delicados'
      },
      { 
        nombre: 'Neón', 
        colores: ['#ff00ff', '#00ffff', '#ffff00', '#ff1493', '#00ff00'],
        preview: '⚡',
        descripcion: 'Vibrantes y brillantes'
      },
      { 
        nombre: 'Tierra', 
        colores: ['#8b4513', '#d2691e', '#daa520', '#cd853f', '#f4a460'],
        preview: '🌍',
        descripcion: 'Cálidos y naturales'
      },
      { 
        nombre: 'Retro', 
        colores: ['#ff6b6b', '#4ecdc4', '#ffe66d', '#a8e6cf', '#ff8b94'],
        preview: '📻',
        descripcion: 'Vintage años 70-80'
      },
      { 
        nombre: 'Minimalista', 
        colores: ['#000000', '#ffffff', '#808080', '#c0c0c0', '#404040'],
        preview: '⬛',
        descripcion: 'Blanco y negro elegante'
      },
      { 
        nombre: 'Acuarela', 
        colores: ['#a8dadc', '#f1faee', '#e63946', '#f4a261', '#2a9d8f'],
        preview: '🎨',
        descripcion: 'Suaves y artísticos'
      },
      { 
        nombre: 'Alto contraste', 
        colores: ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff'],
        preview: '🌈',
        descripcion: 'Máxima visibilidad'
      },
      { 
        nombre: 'Océano', 
        colores: ['#006994', '#1a8cba', '#5eb3d6', '#a2d5e8', '#d0ecf5'],
        preview: '🌊',
        descripcion: 'Azules profundos'
      }
    ],
    composiciones: [
      { 
        nombre: '2 Columnas equilibradas',
        simbolo: '▮▮',
        template: `
┌────────┬────────┐
│        │        │
│   □    │   □    │
│        │        │
└────────┴────────┘`,
        descripcion: 'División vertical 50/50'
      },
      { 
        nombre: 'Caja + Texto',
        simbolo: '▯T',
        template: `
┌─────────┐
│    □    │
├─────────┤
│ Texto:  │
│ □       │
└─────────┘`,
        descripcion: 'Elemento visual arriba'
      },
      { 
        nombre: 'Dos bloques + Icono',
        simbolo: '⊞⊞',
        template: `
      ★
┌──────┐┌──────┐
│  □   ││  □   │
└──────┘└──────┘`,
        descripcion: 'Icono central superior'
      },
      { 
        nombre: 'Figura + Descripción',
        simbolo: '●→',
        template: `
    ●  →  □ Título
          □ Texto
          □ Detalle`,
        descripcion: 'Concepto lateral izquierdo'
      },
      { 
        nombre: 'División diagonal',
        simbolo: '◢◣',
        template: `
┌──────────┐
│  □   ╱   │
│    ╱  □  │
│  ╱       │
└──────────┘`,
        descripcion: 'Elegante y dinámica'
      },
      { 
        nombre: 'Grid 3×3',
        simbolo: '⊞',
        template: `
┌───┬───┬───┐
│ □ │ □ │ □ │
├───┼───┼───┤
│ □ │ □ │ □ │
├───┼───┼───┤
│ □ │ □ │ □ │
└───┴───┴───┘`,
        descripcion: 'Cuadrícula organizada'
      },
      { 
        nombre: 'Timeline horizontal',
        simbolo: '━●━',
        template: `
□──●──□──●──□──●──□
1     2     3     4`,
        descripcion: 'Línea de tiempo'
      },
      { 
        nombre: 'Pirámide',
        simbolo: '△',
        template: `
        ▲
       ▲ ▲
      ▲ ▲ ▲
     □ □ □ □`,
        descripcion: 'Jerarquía visual'
      }
    ],
    estilos: [
      { 
        nombre: 'Impresionismo',
        simbolo: '🌅',
        filtro: 'blur(0.5px) brightness(1.1) saturate(1.3)',
        descripcion: 'Monet - Luz y pinceladas sueltas'
      },
      { 
        nombre: 'Cubismo',
        simbolo: '📐',
        filtro: 'contrast(1.3) saturate(0.8)',
        descripcion: 'Picasso - Geometría fragmentada'
      },
      { 
        nombre: 'Surrealismo',
        simbolo: '🌙',
        filtro: 'hue-rotate(30deg) saturate(1.5)',
        descripcion: 'Dalí - Onírico e ilógico'
      },
      { 
        nombre: 'Barroco',
        simbolo: '👑',
        filtro: 'brightness(0.9) contrast(1.4) sepia(0.2)',
        descripcion: 'Caravaggio - Drama y luz'
      },
      { 
        nombre: 'Modernismo',
        simbolo: '🏛️',
        filtro: 'saturate(0.7) brightness(1.05)',
        descripcion: 'Klimt - Elegancia decorativa'
      },
      { 
        nombre: 'Bauhaus',
        simbolo: '▲■●',
        filtro: 'contrast(1.5) saturate(1.2)',
        descripcion: 'Minimalista - Formas puras'
      },
      { 
        nombre: 'Ukiyo-e',
        simbolo: '🌸',
        filtro: 'saturate(1.4) contrast(1.1)',
        descripcion: 'Hokusai - Grabados japoneses'
      },
      { 
        nombre: 'Pop Art',
        simbolo: '💥',
        filtro: 'contrast(1.6) saturate(2) brightness(1.1)',
        descripcion: 'Warhol - Colores vibrantes'
      }
    ],
    iconos: [
      { nombre: 'Pincel', simbolo: '🖌️', descripcion: 'Herramienta artística' },
      { nombre: 'Paleta', simbolo: '🎨', descripcion: 'Mezcla de colores' },
      { nombre: 'Busto clásico', simbolo: '🗿', descripcion: 'Escultura antigua' },
      { nombre: 'Marco', simbolo: '🖼️', descripcion: 'Obra enmarcada' },
      { nombre: 'Museo', simbolo: '🏛️', descripcion: 'Institución cultural' },
      { nombre: 'Estatua', simbolo: '🗽', descripcion: 'Escultura monumental' },
      { nombre: 'Cámara', simbolo: '📷', descripcion: 'Fotografía artística' },
      { nombre: 'Ojo', simbolo: '👁️', descripcion: 'Percepción visual' },
      { nombre: 'Corona', simbolo: '👑', descripcion: 'Arte clásico' },
      { nombre: 'Estrella', simbolo: '⭐', descripcion: 'Obra destacada' },
      { nombre: 'Luz', simbolo: '💡', descripcion: 'Iluminación' },
      { nombre: 'Corazón', simbolo: '❤️', descripcion: 'Emoción artística' }
    ]
  };

  const tabActual = tabs.find(t => t.id === activeTab);

  return (
    <div style={{ width: '100%' }}>
      {/* Tabs superiores */}
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        marginBottom: '1rem',
        borderBottom: '2px solid rgba(255, 255, 255, 0.1)',
        paddingBottom: '0.5rem'
      }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '0.6rem 1.2rem',
              background: activeTab === tab.id 
                ? `linear-gradient(135deg, ${tab.color}30, ${tab.color}15)`
                : 'transparent',
              border: activeTab === tab.id 
                ? `2px solid ${tab.color}`
                : '2px solid transparent',
              borderRadius: '8px',
              color: activeTab === tab.id ? tab.color : '#94a3b8',
              cursor: 'pointer',
              fontSize: '0.9rem',
              fontWeight: activeTab === tab.id ? '600' : '500',
              transition: 'all 0.2s',
              whiteSpace: 'nowrap'
            }}
          >
            {tab.nombre}
          </button>
        ))}
      </div>

      {/* Contenido del tab activo */}
      {activeTab === 'figuras' && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))',
          gap: '0.75rem'
        }}>
          {elementos.figuras.map((fig, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => onInsertElement(fig.template)}
              style={{
                padding: '1rem',
                background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(59, 130, 246, 0.03))',
                border: '2px solid rgba(59, 130, 246, 0.2)',
                borderRadius: '10px',
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '0.5rem'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(59, 130, 246, 0.08))';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(59, 130, 246, 0.03))';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div style={{ fontSize: '2rem', color: '#60a5fa' }}>{fig.simbolo}</div>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8', textAlign: 'center' }}>{fig.nombre}</div>
            </button>
          ))}
        </div>
      )}

      {activeTab === 'paletas' && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
          gap: '1rem'
        }}>
          {elementos.paletas.map((pal, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                const paletaTexto = `🎨 Paleta ${pal.nombre} (${pal.descripcion}):\n${pal.colores.map((c, i) => `█ ${c}`).join(' ')}`;
                onInsertElement(paletaTexto);
              }}
              style={{
                padding: '1rem',
                background: 'linear-gradient(135deg, rgba(236, 72, 153, 0.08), rgba(236, 72, 153, 0.03))',
                border: '2px solid rgba(236, 72, 153, 0.2)',
                borderRadius: '10px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'linear-gradient(135deg, rgba(236, 72, 153, 0.15), rgba(236, 72, 153, 0.08))';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'linear-gradient(135deg, rgba(236, 72, 153, 0.08), rgba(236, 72, 153, 0.03))';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{pal.preview}</div>
              <div style={{ fontSize: '0.85rem', color: '#f9a8d4', fontWeight: '600', marginBottom: '0.5rem' }}>
                {pal.nombre}
              </div>
              <div style={{ fontSize: '0.7rem', color: '#94a3b8', marginBottom: '0.75rem' }}>
                {pal.descripcion}
              </div>
              <div style={{ display: 'flex', gap: '4px', justifyContent: 'center' }}>
                {pal.colores.map((color, i) => (
                  <div
                    key={i}
                    style={{
                      width: '24px',
                      height: '24px',
                      background: color,
                      borderRadius: '4px',
                      border: '1px solid rgba(255, 255, 255, 0.2)'
                    }}
                  />
                ))}
              </div>
            </button>
          ))}
        </div>
      )}

      {activeTab === 'composiciones' && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
          gap: '1rem'
        }}>
          {elementos.composiciones.map((comp, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => onInsertElement(comp.template)}
              style={{
                padding: '1rem',
                background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(139, 92, 246, 0.03))',
                border: '2px solid rgba(139, 92, 246, 0.2)',
                borderRadius: '10px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(139, 92, 246, 0.08))';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(139, 92, 246, 0.03))';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div style={{ fontSize: '2rem', color: '#a78bfa', marginBottom: '0.5rem' }}>{comp.simbolo}</div>
              <div style={{ fontSize: '0.85rem', color: '#c4b5fd', fontWeight: '600', marginBottom: '0.25rem' }}>
                {comp.nombre}
              </div>
              <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>
                {comp.descripcion}
              </div>
            </button>
          ))}
        </div>
      )}

      {activeTab === 'estilos' && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
          gap: '1rem'
        }}>
          {elementos.estilos.map((est, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                const estiloTexto = `🖼️ Estilo: ${est.nombre}\n📝 ${est.descripcion}\n✨ Características: ${est.filtro}`;
                onInsertElement(estiloTexto);
              }}
              style={{
                padding: '1rem',
                background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(245, 158, 11, 0.03))',
                border: '2px solid rgba(245, 158, 11, 0.2)',
                borderRadius: '10px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.08))';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(245, 158, 11, 0.03))';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>{est.simbolo}</div>
              <div style={{ fontSize: '0.85rem', color: '#fbbf24', fontWeight: '600', marginBottom: '0.25rem' }}>
                {est.nombre}
              </div>
              <div style={{ fontSize: '0.7rem', color: '#94a3b8', lineHeight: '1.4' }}>
                {est.descripcion}
              </div>
            </button>
          ))}
        </div>
      )}

      {activeTab === 'iconos' && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))',
          gap: '0.75rem'
        }}>
          {elementos.iconos.map((ico, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => onInsertElement(ico.simbolo)}
              style={{
                padding: '1rem',
                background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(16, 185, 129, 0.03))',
                border: '2px solid rgba(16, 185, 129, 0.2)',
                borderRadius: '10px',
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '0.5rem'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.08))';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(16, 185, 129, 0.03))';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div style={{ fontSize: '2.5rem' }}>{ico.simbolo}</div>
              <div style={{ fontSize: '0.75rem', color: '#6ee7b7', fontWeight: '600', textAlign: 'center' }}>
                {ico.nombre}
              </div>
              <div style={{ fontSize: '0.65rem', color: '#94a3b8', textAlign: 'center' }}>
                {ico.descripcion}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default ArtToolbar;
