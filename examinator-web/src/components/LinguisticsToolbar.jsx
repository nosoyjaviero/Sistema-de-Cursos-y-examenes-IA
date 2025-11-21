import { useState } from 'react';

const LinguisticsToolbar = ({ onInsertSymbol }) => {
  const [tabActiva, setTabActiva] = useState('ipa-vowels');

  // 🔤 IPA - Vocales
  const componentesVocales = [
    { nombre: 'iː (beat)', svg: 'M18 10 L18 30 M22 10 L22 30', latex: '/iː/', desc: 'Vocal larga /iː/' },
    { nombre: 'ɪ (bit)', svg: 'M18 10 L18 30 M22 10 L22 22', latex: '/ɪ/', desc: 'Vocal corta /ɪ/' },
    { nombre: 'e (bed)', svg: 'M25 10 L12 10 L12 30 L25 30 M12 20 L22 20', latex: '/e/', desc: 'Vocal /e/' },
    { nombre: 'æ (cat)', svg: 'M15 25 C15 15, 25 15, 25 25 M18 20 L28 20 M28 15 L28 25 L32 30', latex: '/æ/', desc: 'Vocal /æ/' },
    { nombre: 'ɑː (father)', svg: 'M15 25 C15 15, 25 15, 25 25 M18 20 L28 20 M32 10 L32 30', latex: '/ɑː/', desc: 'Vocal larga /ɑː/' },
    { nombre: 'ʌ (cup)', svg: 'M12 10 L18 25 L24 10', latex: '/ʌ/', desc: 'Vocal /ʌ/' },
    { nombre: 'ɔː (law)', svg: 'M20 20 m -8 0 a 8 8 0 1 0 16 0 a 8 8 0 1 0 -16 0 M28 10 L28 30', latex: '/ɔː/', desc: 'Vocal larga /ɔː/' },
    { nombre: 'ɒ (hot)', svg: 'M20 20 m -8 0 a 8 8 0 1 0 16 0 a 8 8 0 1 0 -16 0', latex: '/ɒ/', desc: 'Vocal /ɒ/' },
    { nombre: 'uː (boot)', svg: 'M12 10 L12 22 C12 28, 28 28, 28 22 L28 10 M32 10 L32 30', latex: '/uː/', desc: 'Vocal larga /uː/' },
    { nombre: 'ʊ (foot)', svg: 'M12 10 L12 22 C12 28, 28 28, 28 22 L28 10', latex: '/ʊ/', desc: 'Vocal /ʊ/' },
    { nombre: 'ə (about)', svg: 'M28 15 C28 12, 20 12, 15 15 C12 18, 12 22, 15 25 C20 28, 28 28, 28 25 M15 20 L25 20', latex: '/ə/', desc: 'Schwa /ə/' },
    { nombre: 'ɜː (bird)', svg: 'M28 15 C28 12, 20 12, 15 15 C12 18, 12 22, 15 25 C20 28, 28 28, 28 25 M15 20 L25 20 M32 10 L32 30', latex: '/ɜː/', desc: 'Vocal larga /ɜː/' }
  ];

  // 🔤 IPA - Consonantes
  const componentesConsonantes = [
    { nombre: 'θ (thin)', svg: 'M20 20 m -8 0 a 8 8 0 1 0 16 0 a 8 8 0 1 0 -16 0 M12 20 L28 20', latex: '/θ/', desc: 'Fricativa /θ/' },
    { nombre: 'ð (this)', svg: 'M20 20 m -8 0 a 8 8 0 1 0 16 0 a 8 8 0 1 0 -16 0 M12 20 L28 20 M18 8 L22 12', latex: '/ð/', desc: 'Fricativa /ð/' },
    { nombre: 'ʃ (ship)', svg: 'M15 10 C12 15, 12 15, 15 20 C12 25, 12 25, 15 30 M25 10 L25 30', latex: '/ʃ/', desc: 'Fricativa /ʃ/' },
    { nombre: 'ʒ (vision)', svg: 'M15 10 C12 15, 12 15, 15 20 C12 25, 12 25, 15 30 M25 10 L25 30 M22 5 L28 10', latex: '/ʒ/', desc: 'Fricativa /ʒ/' },
    { nombre: 'tʃ (chip)', svg: 'M12 12 L25 12 M18 12 L18 28 M28 10 C25 15, 25 15, 28 20 C25 25, 25 25, 28 30', latex: '/tʃ/', desc: 'Africada /tʃ/' },
    { nombre: 'dʒ (judge)', svg: 'M12 10 L12 25 C12 28, 18 28, 18 25 M25 10 C22 15, 22 15, 25 20 C22 25, 22 25, 25 30', latex: '/dʒ/', desc: 'Africada /dʒ/' },
    { nombre: 'ŋ (sing)', svg: 'M12 20 L12 30 M12 20 L18 10 L24 20 L24 30 M24 25 C24 28, 28 30, 30 28', latex: '/ŋ/', desc: 'Nasal /ŋ/' },
    { nombre: 'j (yes)', svg: 'M15 10 L22 20 M18 16 L15 10 M22 20 C22 28, 18 28, 18 28', latex: '/j/', desc: 'Aproximante /j/' },
    { nombre: 'w (wet)', svg: 'M10 10 L13 25 L18 15 L23 25 L26 10', latex: '/w/', desc: 'Aproximante /w/' },
    { nombre: 'r (red)', svg: 'M12 10 L12 30 M12 10 C12 10, 18 10, 22 15 M22 15 L26 30', latex: '/r/', desc: 'Aproximante /r/' },
    { nombre: 'ː (largo)', svg: 'M18 14 L18 18 M18 22 L18 26', latex: 'ː', desc: 'Marca de longitud' },
    { nombre: 'ˈ (stress 1)', svg: 'M20 8 L20 18', latex: 'ˈ', desc: 'Stress primario' }
  ];

  // 🔤 IPA - Diptongos
  const componentesDiptongos = [
    { nombre: 'eɪ (day)', svg: 'M8 10 L8 30 L18 30 M8 20 L15 20 M22 10 L22 30 M26 10 L26 30', latex: '/eɪ/', desc: 'Diptongo /eɪ/' },
    { nombre: 'aɪ (my)', svg: 'M10 25 C10 15, 18 15, 18 25 M12 20 L20 20 M24 10 L24 30 M28 10 L28 30', latex: '/aɪ/', desc: 'Diptongo /aɪ/' },
    { nombre: 'ɔɪ (boy)', svg: 'M12 20 m -6 0 a 6 6 0 1 0 12 0 a 6 6 0 1 0 -12 0 M24 10 L24 30 M28 10 L28 30', latex: '/ɔɪ/', desc: 'Diptongo /ɔɪ/' },
    { nombre: 'əʊ (go)', svg: 'M12 20 m -6 0 a 6 6 0 1 0 12 0 a 6 6 0 1 0 -12 0 M22 10 L22 22 C22 28, 32 28, 32 22 L32 10', latex: '/əʊ/', desc: 'Diptongo /əʊ/' },
    { nombre: 'aʊ (now)', svg: 'M10 25 C10 15, 18 15, 18 25 M12 20 L20 20 M24 10 L24 22 C24 28, 32 28, 32 22 L32 10', latex: '/aʊ/', desc: 'Diptongo /aʊ/' },
    { nombre: 'ɪə (ear)', svg: 'M10 10 L10 30 M14 10 L14 22 M20 20 m -5 0 a 5 5 0 1 0 10 0 a 5 5 0 1 0 -10 0', latex: '/ɪə/', desc: 'Diptongo /ɪə/' },
    { nombre: 'eə (air)', svg: 'M8 10 L8 30 L16 30 M8 20 L14 20 M20 20 m -5 0 a 5 5 0 1 0 10 0 a 5 5 0 1 0 -10 0', latex: '/eə/', desc: 'Diptongo /eə/' },
    { nombre: 'ʊə (tour)', svg: 'M8 10 L8 22 C8 28, 16 28, 16 22 L16 10 M22 20 m -5 0 a 5 5 0 1 0 10 0 a 5 5 0 1 0 -10 0', latex: '/ʊə/', desc: 'Diptongo /ʊə/' }
  ];

  // 🎵 Stress y Entonación
  const componentesStress = [
    { nombre: 'ˈ (primario)', svg: 'M20 10 L20 25', latex: 'ˈ', desc: 'Stress primario' },
    { nombre: 'ˌ (secund)', svg: 'M20 15 L20 25', latex: 'ˌ', desc: 'Stress secundario' },
    { nombre: '↗ (subida)', svg: 'M8 28 L20 12 L32 8 L28 12', latex: '↗', desc: 'Entonación ascendente' },
    { nombre: '↘ (bajada)', svg: 'M8 8 L20 24 L32 28 L28 24', latex: '↘', desc: 'Entonación descendente' },
    { nombre: '→ (plana)', svg: 'M8 20 L32 20 L28 16 M32 20 L28 24', latex: '→', desc: 'Entonación plana' },
    { nombre: '‿ (linking)', svg: 'M10 25 C10 15, 30 15, 30 25', latex: '‿', desc: 'Enlace entre palabras' },
    { nombre: '| (pausa)', svg: 'M20 10 L20 30', latex: '|', desc: 'Pausa breve' },
    { nombre: '‖ (pausa lar)', svg: 'M18 10 L18 30 M22 10 L22 30', latex: '‖', desc: 'Pausa larga' }
  ];

  // 📐 Diagramas Articulación
  const componentesDiagramas = [
    { nombre: 'Mapa Voc', svg: 'M10 10 L30 10 L35 30 L5 30 Z M10 10 L5 30 M30 10 L35 30 M17 18 L23 18 L27 24 L13 24 Z', latex: 'Vowel Chart', desc: 'Mapa de vocales (trapezoide)' },
    { nombre: 'Lengua Alta', svg: 'M8 25 C8 20, 12 15, 20 15 C28 15, 32 20, 32 25 L20 25', latex: 'High', desc: 'Lengua posición alta' },
    { nombre: 'Lengua Med', svg: 'M8 22 C8 18, 12 15, 20 15 C28 15, 32 18, 32 22', latex: 'Mid', desc: 'Lengua posición media' },
    { nombre: 'Lengua Baj', svg: 'M8 18 C12 22, 16 25, 20 25 C24 25, 28 22, 32 18', latex: 'Low', desc: 'Lengua posición baja' },
    { nombre: 'Bilabial', svg: 'M10 15 L30 15 M10 25 L30 25', latex: 'Bilabial', desc: 'Articulación bilabial' },
    { nombre: 'Alveolar', svg: 'M20 10 C15 12, 15 18, 20 20 M10 25 L30 25', latex: 'Alveolar', desc: 'Articulación alveolar' },
    { nombre: 'Velar', svg: 'M10 15 C15 12, 25 12, 30 15 M20 20 C18 24, 18 28, 20 30 M10 25 L30 25', latex: 'Velar', desc: 'Articulación velar' },
    { nombre: 'Oclusiva', svg: 'M10 18 L30 18 M10 22 L30 22 M20 10 L20 30', latex: 'Plosive', desc: 'Modo oclusivo' }
  ];

  // 🔄 Flechas Fonéticas
  const componentesFlechas = [
    { nombre: '→ (cambio)', svg: 'M8 20 L30 20 L25 15 M30 20 L25 25', latex: '→', desc: 'Cambio fonético' },
    { nombre: '↷ (reducción)', svg: 'M15 15 L25 15 C28 15, 28 25, 25 25 L20 25 L22 22', latex: '↷', desc: 'Reducción vocal' },
    { nombre: '⇄ (alternancia)', svg: 'M8 18 L28 18 L24 14 M28 18 L24 22 M28 22 L8 22 L12 18 M8 22 L12 26', latex: '⇄', desc: 'Alternancia fonética' },
    { nombre: '≈ (aproximado)', svg: 'M10 16 C15 14, 20 18, 25 16 M10 24 C15 22, 20 26, 25 24', latex: '≈', desc: 'Pronunciación aproximada' },
    { nombre: '* (incorrecto)', svg: 'M20 12 L20 22 M16 16 L24 16 M18 18 L22 18 M18 20 L22 20 M20 26 m -2 0 a 2 2 0 1 0 4 0 a 2 2 0 1 0 -4 0', latex: '*', desc: 'Forma incorrecta' },
    { nombre: '√ (correcto)', svg: 'M10 20 L15 28 L30 10', latex: '√', desc: 'Forma correcta' }
  ];

  const componentes = {
    'ipa-vowels': componentesVocales,
    'ipa-consonants': componentesConsonantes,
    'ipa-diphthongs': componentesDiptongos,
    'stress': componentesStress,
    'diagrams': componentesDiagramas,
    'arrows': componentesFlechas
  };

  const tabs = [
    { id: 'ipa-vowels', nombre: 'Vocales IPA', icon: '🔤', color: '#ec4899' },
    { id: 'ipa-consonants', nombre: 'Consonantes', icon: '🔠', color: '#db2777' },
    { id: 'ipa-diphthongs', nombre: 'Diptongos', icon: '📢', color: '#be185d' },
    { id: 'stress', nombre: 'Stress', icon: '🎵', color: '#9f1239' },
    { id: 'diagrams', nombre: 'Diagramas', icon: '📐', color: '#881337' },
    { id: 'arrows', nombre: 'Flechas', icon: '🔄', color: '#be123c' }
  ];

  return (
    <div style={{
      background: 'rgba(236, 72, 153, 0.05)',
      borderRadius: '12px',
      padding: '1rem',
      border: '1px solid rgba(236, 72, 153, 0.2)'
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
            key={tab.id}
            type="button"
            onClick={() => setTabActiva(tab.id)}
            style={{
              padding: '0.5rem 1rem',
              background: tabActiva === tab.id ? tab.color : 'rgba(236, 72, 153, 0.1)',
              color: tabActiva === tab.id ? 'white' : '#fce7f3',
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
        gridTemplateColumns: 'repeat(auto-fill, minmax(95px, 1fr))',
        gap: '0.75rem',
        maxHeight: '350px',
        overflowY: 'auto',
        padding: '0.5rem'
      }}>
        {componentes[tabActiva].map((comp, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => onInsertSymbol(comp.latex)}
            style={{
              padding: '0.75rem',
              background: 'rgba(236, 72, 153, 0.1)',
              border: '1px solid rgba(236, 72, 153, 0.3)',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.2s',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '0.5rem'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(236, 72, 153, 0.2)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(236, 72, 153, 0.1)';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            {/* Preview SVG */}
            <svg width="40" height="40" viewBox="0 0 40 40" style={{ flexShrink: 0 }}>
              <path
                d={comp.svg}
                stroke="#fce7f3"
                strokeWidth="2"
                fill="none"
              />
            </svg>
            
            {/* Nombre */}
            <span style={{
              fontSize: '0.7rem',
              color: '#fbcfe8',
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
        background: 'rgba(236, 72, 153, 0.08)',
        borderRadius: '6px',
        fontSize: '0.8rem',
        color: '#fce7f3',
        lineHeight: '1.5'
      }}>
        <strong style={{color: '#fbcfe8'}}>💡 Categoría {tabs.find(t => t.id === tabActiva)?.nombre}:</strong> {
          tabActiva === 'ipa-vowels' ? 'Vocales IPA (largas/cortas, schwa)' :
          tabActiva === 'ipa-consonants' ? 'Consonantes difíciles (θ ð ʃ ʒ tʃ dʒ ŋ)' :
          tabActiva === 'ipa-diphthongs' ? 'Diptongos comunes en inglés' :
          tabActiva === 'stress' ? 'Marcas de stress, entonación, pausas' :
          tabActiva === 'diagrams' ? 'Diagramas de articulación (lengua, modo, lugar)' :
          'Flechas y símbolos para cambios fonéticos'
        }
      </div>
    </div>
  );
};

export default LinguisticsToolbar;
