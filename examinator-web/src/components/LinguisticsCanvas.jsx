const LinguisticsCanvas = ({ value, onChange, placeholder }) => {
  return (
    <div style={{
      background: 'rgba(236, 72, 153, 0.05)',
      border: '2px solid rgba(236, 72, 153, 0.3)',
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
        placeholder={placeholder || "Escribe pronunciación usando símbolos IPA...\n\nEjemplo:\nwater /ˈwɔːtə/\nthink /θɪŋk/\nthis /ðɪs/\nship /ʃɪp/\nvision /ˈvɪʒən/\n\nCon stress:\nˈwater (stress en primera sílaba)\ndeˌmocracy (stress primario + secundario)\n\nCon entonación:\n¿Are you coming? ↗\nI'm going home. ↘\n\nCon linking:\nAn ‿ apple\nGo ‿ out"}
        style={{
          minHeight: '250px',
          padding: '1rem',
          background: 'rgba(17, 24, 39, 0.5)',
          border: '1px solid rgba(236, 72, 153, 0.3)',
          borderRadius: '8px',
          color: '#fbcfe8',
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
        border: '1px solid rgba(236, 72, 153, 0.3)',
        borderRadius: '8px',
        padding: '1rem',
        minHeight: '150px'
      }}>
        <div style={{
          fontSize: '0.85rem',
          fontWeight: '600',
          color: '#fce7f3',
          marginBottom: '0.75rem',
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }}>
          🔊 Vista Previa
        </div>
        <pre style={{
          margin: 0,
          color: '#fbcfe8',
          fontFamily: 'monospace',
          fontSize: '1rem',
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
        background: 'rgba(236, 72, 153, 0.08)',
        borderLeft: '4px solid #ec4899',
        borderRadius: '8px',
        fontSize: '0.85rem',
        color: '#fce7f3',
        lineHeight: '1.6'
      }}>
        <strong style={{color: '#fbcfe8'}}>💡 Símbolos IPA disponibles:</strong><br/>
        
        <div style={{marginTop: '0.5rem', display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.4rem'}}>
          <div>
            <strong style={{color: '#fce7f3'}}>Vocales:</strong> iː ɪ e æ ɑː ʌ ɔː ɒ uː ʊ ə ɜː
          </div>
          <div>
            <strong style={{color: '#fce7f3'}}>Diptongos:</strong> eɪ aɪ ɔɪ əʊ aʊ ɪə eə ʊə
          </div>
          <div>
            <strong style={{color: '#fce7f3'}}>Consonantes:</strong> θ ð ʃ ʒ tʃ dʒ ŋ j w r
          </div>
          <div>
            <strong style={{color: '#fce7f3'}}>Marcas:</strong> ˈ (stress1) ˌ (stress2) ː (largo)
          </div>
        </div>

        <div style={{marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(236, 72, 153, 0.2)'}}>
          <strong style={{color: '#fbcfe8'}}>📋 Ejemplos comunes:</strong><br/>
          <code style={{background: 'rgba(236, 72, 153, 0.2)', padding: '2px 6px', borderRadius: '4px', color: '#fce7f3'}}>
            /ˈwɔːtə/
          </code> - water<br/>
          <code style={{background: 'rgba(236, 72, 153, 0.2)', padding: '2px 6px', borderRadius: '4px', color: '#fce7f3'}}>
            /θɪŋk/
          </code> - think<br/>
          <code style={{background: 'rgba(236, 72, 153, 0.2)', padding: '2px 6px', borderRadius: '4px', color: '#fce7f3'}}>
            ˈhello ↗
          </code> - entonación pregunta
        </div>

        <div style={{marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(236, 72, 153, 0.2)'}}>
          <strong style={{color: '#fbcfe8'}}>🎯 Categorías:</strong> 🔤 Vocales • 🔠 Consonantes • 📢 Diptongos • 🎵 Stress • 📐 Diagramas • 🔄 Flechas
        </div>
      </div>
    </div>
  );
};

export default LinguisticsCanvas;
