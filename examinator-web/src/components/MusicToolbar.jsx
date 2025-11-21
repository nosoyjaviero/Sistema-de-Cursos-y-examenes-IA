import { useState } from 'react';

function MusicToolbar({ onInsertSymbol }) {
  const [activeTab, setActiveTab] = useState('pentagramas');

  const tabs = [
    { id: 'pentagramas', label: '🎼 Pentagramas', icon: '🎼' },
    { id: 'notas', label: '🎵 Notas', icon: '🎵' },
    { id: 'acordes', label: '🎸 Acordes', icon: '🎸' },
    { id: 'intervalos', label: '📏 Intervalos', icon: '📏' },
    { id: 'escalas', label: '🎹 Escalas', icon: '🎹' },
    { id: 'progresiones', label: '🔄 Progresiones', icon: '🔄' },
    { id: 'ritmo', label: '🥁 Ritmo', icon: '🥁' },
    { id: 'simbolos', label: '♯♭ Símbolos', icon: '♯' }
  ];

  // 🎼 CATEGORÍA 1: Pentagramas y Compases
  const pentagramas = [
    { nombre: 'Pentagrama Vacío', simbolo: '═══\n═══\n═══\n═══\n═══' },
    { nombre: 'Clave Sol', simbolo: '𝄞' },
    { nombre: 'Clave Fa', simbolo: '𝄢' },
    { nombre: 'Clave Do', simbolo: '𝄡' },
    { nombre: 'Compás 4/4', simbolo: '4/4' },
    { nombre: 'Compás 3/4', simbolo: '3/4' },
    { nombre: 'Compás 6/8', simbolo: '6/8' },
    { nombre: 'Compás 2/4', simbolo: '2/4' },
    { nombre: 'Barra Simple', simbolo: '|' },
    { nombre: 'Barra Doble', simbolo: '||' },
    { nombre: 'Barra Final', simbolo: '||:' }
  ];

  // 🎵 CATEGORÍA 2: Notas Musicales
  const notas = [
    { nombre: 'Redonda', simbolo: '𝅝' },
    { nombre: 'Blanca', simbolo: '𝅗𝅥' },
    { nombre: 'Negra', simbolo: '♩' },
    { nombre: 'Corchea', simbolo: '♪' },
    { nombre: 'Doble Corchea', simbolo: '♬' },
    { nombre: 'Semicorchea', simbolo: '𝅘𝅥𝅯' },
    { nombre: 'Puntillo', simbolo: '·' },
    { nombre: 'Ligadura', simbolo: '⌢' },
    { nombre: 'Nota Do', simbolo: 'C' },
    { nombre: 'Nota Re', simbolo: 'D' },
    { nombre: 'Nota Mi', simbolo: 'E' },
    { nombre: 'Nota Fa', simbolo: 'F' },
    { nombre: 'Nota Sol', simbolo: 'G' },
    { nombre: 'Nota La', simbolo: 'A' },
    { nombre: 'Nota Si', simbolo: 'B' }
  ];

  // 🎸 CATEGORÍA 3: Acordes
  const acordes = [
    { nombre: 'C Mayor', simbolo: 'C' },
    { nombre: 'Cmaj7', simbolo: 'Cmaj7' },
    { nombre: 'Cm (menor)', simbolo: 'Cm' },
    { nombre: 'Cm7', simbolo: 'Cm7' },
    { nombre: 'C7 (dominante)', simbolo: 'C7' },
    { nombre: 'Cdim (disminuido)', simbolo: 'Cdim' },
    { nombre: 'Caug (aumentado)', simbolo: 'Caug' },
    { nombre: 'Csus2', simbolo: 'Csus2' },
    { nombre: 'Csus4', simbolo: 'Csus4' },
    { nombre: 'C/E (slash)', simbolo: 'C/E' },
    { nombre: 'G Mayor', simbolo: 'G' },
    { nombre: 'D Mayor', simbolo: 'D' },
    { nombre: 'Am (la menor)', simbolo: 'Am' },
    { nombre: 'Em (mi menor)', simbolo: 'Em' },
    { nombre: 'F Mayor', simbolo: 'F' }
  ];

  // 📏 CATEGORÍA 4: Intervalos
  const intervalos = [
    { nombre: 'Unísono (P1)', simbolo: 'P1' },
    { nombre: '2ª menor (m2)', simbolo: 'm2' },
    { nombre: '2ª Mayor (M2)', simbolo: 'M2' },
    { nombre: '3ª menor (m3)', simbolo: 'm3' },
    { nombre: '3ª Mayor (M3)', simbolo: 'M3' },
    { nombre: '4ª Justa (P4)', simbolo: 'P4' },
    { nombre: '4ª Aumentada (A4)', simbolo: 'A4' },
    { nombre: '5ª Justa (P5)', simbolo: 'P5' },
    { nombre: '6ª menor (m6)', simbolo: 'm6' },
    { nombre: '6ª Mayor (M6)', simbolo: 'M6' },
    { nombre: '7ª menor (m7)', simbolo: 'm7' },
    { nombre: '7ª Mayor (M7)', simbolo: 'M7' },
    { nombre: 'Octava (P8)', simbolo: 'P8' }
  ];

  // 🎹 CATEGORÍA 5: Escalas
  const escalas = [
    { nombre: 'Escala Mayor', simbolo: '[Mayor] C-D-E-F-G-A-B-C' },
    { nombre: 'Menor Natural', simbolo: '[Menor Natural] A-B-C-D-E-F-G-A' },
    { nombre: 'Menor Armónica', simbolo: '[Menor Armónica] A-B-C-D-E-F-G♯-A' },
    { nombre: 'Menor Melódica', simbolo: '[Menor Melódica] A-B-C-D-E-F♯-G♯-A' },
    { nombre: 'Pentatónica Mayor', simbolo: '[Penta Mayor] C-D-E-G-A' },
    { nombre: 'Pentatónica Menor', simbolo: '[Penta Menor] A-C-D-E-G' },
    { nombre: 'Blues Mayor', simbolo: '[Blues Mayor] C-D-E♭-E-G-A' },
    { nombre: 'Blues Menor', simbolo: '[Blues Menor] A-C-D-E♭-E-G' },
    { nombre: 'Jónico (I)', simbolo: '[Jónico] C-D-E-F-G-A-B' },
    { nombre: 'Dórico (II)', simbolo: '[Dórico] D-E-F-G-A-B-C' },
    { nombre: 'Frigio (III)', simbolo: '[Frigio] E-F-G-A-B-C-D' },
    { nombre: 'Lidio (IV)', simbolo: '[Lidio] F-G-A-B-C-D-E' },
    { nombre: 'Mixolidio (V)', simbolo: '[Mixolidio] G-A-B-C-D-E-F' },
    { nombre: 'Eólico (VI)', simbolo: '[Eólico] A-B-C-D-E-F-G' },
    { nombre: 'Locrio (VII)', simbolo: '[Locrio] B-C-D-E-F-G-A' }
  ];

  // 🔄 CATEGORÍA 6: Progresiones Armónicas
  const progresiones = [
    { nombre: 'Flecha →', simbolo: '→' },
    { nombre: 'Flecha Circular ↻', simbolo: '↻' },
    { nombre: 'I-IV-V', simbolo: '| I | IV | V |' },
    { nombre: 'ii-V-I (Jazz)', simbolo: '| iim7 | V7 | Imaj7 |' },
    { nombre: 'vi-IV-I-V (Pop)', simbolo: '| vi | IV | I | V |' },
    { nombre: 'I-V-vi-IV', simbolo: '| I | V | vi | IV |' },
    { nombre: 'I-vi-ii-V', simbolo: '| I | vi | ii | V |' },
    { nombre: 'Blues (I-IV-V)', simbolo: '| I7 | IV7 | I7 | I7 | IV7 | IV7 | I7 | I7 | V7 | IV7 | I7 | V7 |' },
    { nombre: 'Círculo Quintas', simbolo: '↻ C→F→B♭→E♭→A♭→D♭→G♭→B→E→A→D→G→C' }
  ];

  // 🥁 CATEGORÍA 7: Ritmo y Estructura
  const ritmo = [
    { nombre: 'Silencio Redonda', simbolo: '𝄻' },
    { nombre: 'Silencio Blanca', simbolo: '𝄼' },
    { nombre: 'Silencio Negra', simbolo: '𝄽' },
    { nombre: 'Silencio Corchea', simbolo: '𝄾' },
    { nombre: 'Silencio Semicorchea', simbolo: '𝄿' },
    { nombre: 'Repetición ||:', simbolo: '||:' },
    { nombre: 'Repetición :||', simbolo: ':||' },
    { nombre: 'Anacruza', simbolo: '(anacruza)' },
    { nombre: 'Tresillo', simbolo: '[3]' },
    { nombre: 'Cinquillo', simbolo: '[5]' },
    { nombre: 'Compás Simple', simbolo: '| |' },
    { nombre: 'Compás Compuesto', simbolo: '|| ||' }
  ];

  // ♯♭ CATEGORÍA 8: Símbolos Musicales
  const simbolos = [
    { nombre: 'Sostenido ♯', simbolo: '♯' },
    { nombre: 'Bemol ♭', simbolo: '♭' },
    { nombre: 'Becuadro ♮', simbolo: '♮' },
    { nombre: 'Doble Sostenido 𝄪', simbolo: '𝄪' },
    { nombre: 'Doble Bemol 𝄫', simbolo: '𝄫' },
    { nombre: 'Calderón 𝄐', simbolo: '𝄐' },
    { nombre: 'Crescendo <', simbolo: '<' },
    { nombre: 'Decrescendo >', simbolo: '>' },
    { nombre: 'Forte f', simbolo: 'f' },
    { nombre: 'Piano p', simbolo: 'p' },
    { nombre: 'Fortissimo ff', simbolo: 'ff' },
    { nombre: 'Pianissimo pp', simbolo: 'pp' },
    { nombre: 'Mezzo-forte mf', simbolo: 'mf' },
    { nombre: 'Mezzo-piano mp', simbolo: 'mp' },
    { nombre: 'Staccato ·', simbolo: '·' },
    { nombre: 'Acento >', simbolo: '>' },
    { nombre: 'Trino tr', simbolo: 'tr~~~' },
    { nombre: 'Mordente ∼', simbolo: '∼' }
  ];

  const getActiveComponents = () => {
    switch(activeTab) {
      case 'pentagramas': return pentagramas;
      case 'notas': return notas;
      case 'acordes': return acordes;
      case 'intervalos': return intervalos;
      case 'escalas': return escalas;
      case 'progresiones': return progresiones;
      case 'ritmo': return ritmo;
      case 'simbolos': return simbolos;
      default: return [];
    }
  };

  return (
    <div style={{
      background: 'linear-gradient(135deg, rgba(236, 72, 153, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)',
      borderRadius: '12px',
      padding: '1rem',
      border: '1px solid rgba(236, 72, 153, 0.2)'
    }}>
      {/* Tabs de categorías */}
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        marginBottom: '1rem',
        flexWrap: 'wrap',
        borderBottom: '2px solid rgba(236, 72, 153, 0.2)',
        paddingBottom: '0.75rem'
      }}>
        {tabs.map(tab => (
          <button
            type="button"
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '0.5rem 1rem',
              background: activeTab === tab.id 
                ? 'linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%)'
                : 'rgba(236, 72, 153, 0.1)',
              color: activeTab === tab.id ? '#fff' : '#fce7f3',
              border: activeTab === tab.id 
                ? '2px solid #ec4899'
                : '1px solid rgba(236, 72, 153, 0.3)',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '0.85rem',
              fontWeight: activeTab === tab.id ? '600' : '500',
              transition: 'all 0.2s ease',
              boxShadow: activeTab === tab.id 
                ? '0 4px 12px rgba(236, 72, 153, 0.3)'
                : 'none'
            }}
            onMouseOver={(e) => {
              if (activeTab !== tab.id) {
                e.target.style.background = 'rgba(236, 72, 153, 0.2)';
                e.target.style.borderColor = 'rgba(236, 72, 153, 0.5)';
              }
            }}
            onMouseOut={(e) => {
              if (activeTab !== tab.id) {
                e.target.style.background = 'rgba(236, 72, 153, 0.1)';
                e.target.style.borderColor = 'rgba(236, 72, 153, 0.3)';
              }
            }}
          >
            <span style={{marginRight: '0.35rem'}}>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Grid de componentes */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))',
        gap: '0.75rem',
        maxHeight: '280px',
        overflowY: 'auto',
        padding: '0.5rem'
      }}>
        {getActiveComponents().map((comp, idx) => (
          <button
            type="button"
            key={idx}
            onClick={() => onInsertSymbol(comp.simbolo)}
            style={{
              padding: '0.75rem',
              background: 'rgba(236, 72, 153, 0.08)',
              border: '1px solid rgba(236, 72, 153, 0.25)',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '0.5rem'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.background = 'rgba(236, 72, 153, 0.15)';
              e.currentTarget.style.borderColor = '#ec4899';
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(236, 72, 153, 0.2)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = 'rgba(236, 72, 153, 0.08)';
              e.currentTarget.style.borderColor = 'rgba(236, 72, 153, 0.25)';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <div style={{
              fontSize: '1.8rem',
              color: '#ec4899',
              fontWeight: '700',
              lineHeight: '1'
            }}>
              {comp.simbolo.split('\n')[0].substring(0, 5)}
            </div>
            <div style={{
              fontSize: '0.7rem',
              color: '#fce7f3',
              fontWeight: '500',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              width: '100%'
            }}>
              {comp.nombre}
            </div>
          </button>
        ))}
      </div>

      {/* Leyenda informativa */}
      <div style={{
        marginTop: '1rem',
        padding: '0.75rem',
        background: 'rgba(236, 72, 153, 0.05)',
        borderRadius: '8px',
        fontSize: '0.75rem',
        color: '#fbcfe8',
        borderLeft: '3px solid #ec4899'
      }}>
        <strong style={{color: '#ec4899'}}>💡 Herramientas Musicales:</strong><br/>
        {activeTab === 'pentagramas' && '🎼 Pentagramas con claves (sol/fa/do), compases (4/4, 3/4, 6/8), barras'}
        {activeTab === 'notas' && '🎵 Figuras musicales: redonda, blanca, negra, corchea, semicorchea + puntillos y ligaduras'}
        {activeTab === 'acordes' && '🎸 Acordes: mayores, menores, maj7, m7, dim, aug, sus2/4, slash chords'}
        {activeTab === 'intervalos' && '📏 Intervalos: m2, M2, m3, M3, P4, A4, P5, m6, M6, m7, M7, P8'}
        {activeTab === 'escalas' && '🎹 Escalas: mayor, menor (natural/armónica/melódica), pentatónicas, blues, modos griegos'}
        {activeTab === 'progresiones' && '🔄 Progresiones: I-IV-V, ii-V-I, vi-IV-I-V, círculo de quintas, blues'}
        {activeTab === 'ritmo' && '🥁 Silencios, repeticiones, anacrusas, tresillos, compases simples/compuestos'}
        {activeTab === 'simbolos' && '♯♭ Alteraciones (♯♭♮), dinámicas (f, p, mf, mp), articulaciones (staccato, trino)'}
      </div>
    </div>
  );
}

export default MusicToolbar;
