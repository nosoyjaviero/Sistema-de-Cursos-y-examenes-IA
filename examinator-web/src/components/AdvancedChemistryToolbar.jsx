import { useState } from 'react';

function AdvancedChemistryToolbar({ onInsertComponent }) {
  const [activeTab, setActiveTab] = useState('orbitales');

  const tabs = [
    { id: 'orbitales', label: '⚛️ Orbitales', icon: '⚛️' },
    { id: 'hibridacion', label: '🔺 Hibridación', icon: '🔺' },
    { id: 'vsepr', label: '🔷 VSEPR', icon: '🔷' },
    { id: 'electrones', label: '↻ Movimiento e⁻', icon: '↻' },
    { id: 'cargas', label: 'δ Cargas', icon: 'δ' },
    { id: 'mo', label: '📊 Diagramas MO', icon: '📊' },
    { id: 'pares', label: '•• Pares e⁻', icon: '••' },
    { id: 'resonancia', label: '⇌ Resonancia', icon: '⇌' },
    { id: 'enlaces', label: '⚡ Enlaces', icon: '⚡' }
  ];

  // ⚛️ CATEGORÍA 1: Orbitales Atómicos
  const orbitales = [
    { nombre: 'Orbital 1s', simbolo: '[1s] ○ (esfera)', descripcion: 'Orbital s (esférico)' },
    { nombre: 'Orbital 2s', simbolo: '[2s] ⊚ (esfera mayor)', descripcion: 'Orbital 2s con nodo' },
    { nombre: 'Orbital 2px', simbolo: '[2px] ∞ (horizontal)', descripcion: 'Orbital p en eje x' },
    { nombre: 'Orbital 2py', simbolo: '[2py] ⧖ (vertical)', descripcion: 'Orbital p en eje y' },
    { nombre: 'Orbital 2pz', simbolo: '[2pz] ⧗ (profundidad)', descripcion: 'Orbital p en eje z' },
    { nombre: 'Orbital 3dxy', simbolo: '[3dxy] ✥ (trébol xy)', descripcion: 'Orbital d en plano xy' },
    { nombre: 'Orbital 3dxz', simbolo: '[3dxz] ✥ (trébol xz)', descripcion: 'Orbital d en plano xz' },
    { nombre: 'Orbital 3dyz', simbolo: '[3dyz] ✥ (trébol yz)', descripcion: 'Orbital d en plano yz' },
    { nombre: 'Orbital 3dx²-y²', simbolo: '[3dx²-y²] ✦ (4 lóbulos)', descripcion: 'Orbital d x²-y²' },
    { nombre: 'Orbital 3dz²', simbolo: '[3dz²] ⟐ (donut + lóbulos)', descripcion: 'Orbital d z²' },
    { nombre: 'Orbital f', simbolo: '[4f] ✺ (complejo)', descripcion: 'Orbital f (forma compleja)' },
    { nombre: 'Superposición', simbolo: '[Overlap] ⧉', descripcion: 'Solapamiento de orbitales' }
  ];

  // 🔺 CATEGORÍA 2: Hibridación
  const hibridacion = [
    { nombre: 'sp Lineal', simbolo: '[sp] ←A→ (180°)', descripcion: 'Hibridación sp, geometría lineal' },
    { nombre: 'sp² Trigonal', simbolo: '[sp²] ⟁ A (120°)', descripcion: 'Hibridación sp², trigonal planar' },
    { nombre: 'sp³ Tetraédrica', simbolo: '[sp³] ⧓ A (109.5°)', descripcion: 'Hibridación sp³, tetraédrica' },
    { nombre: 'sp³d Bipiramidal', simbolo: '[sp³d] ⧮ A', descripcion: 'Hibridación sp³d, trigonal bipiramidal' },
    { nombre: 'sp³d² Octaédrica', simbolo: '[sp³d²] ⧈ A', descripcion: 'Hibridación sp³d², octaédrica' },
    { nombre: 'Diagrama Orbital sp', simbolo: '[Diagrama sp] 2 orbitales híbridos', descripcion: 'Diagrama de formación sp' },
    { nombre: 'Diagrama Orbital sp²', simbolo: '[Diagrama sp²] 3 orbitales híbridos', descripcion: 'Diagrama de formación sp²' },
    { nombre: 'Diagrama Orbital sp³', simbolo: '[Diagrama sp³] 4 orbitales híbridos', descripcion: 'Diagrama de formación sp³' },
    { nombre: 'Ángulo 180°', simbolo: '∠ = 180°', descripcion: 'Ángulo lineal' },
    { nombre: 'Ángulo 120°', simbolo: '∠ = 120°', descripcion: 'Ángulo trigonal' },
    { nombre: 'Ángulo 109.5°', simbolo: '∠ = 109.5°', descripcion: 'Ángulo tetraédrico' },
    { nombre: 'Ángulo 90°', simbolo: '∠ = 90°', descripcion: 'Ángulo octaédrico' }
  ];

  // 🔷 CATEGORÍA 3: Geometrías VSEPR
  const vsepr = [
    { nombre: 'AX₂ Lineal', simbolo: '[AX₂] X—A—X (180°)', descripcion: 'Geometría lineal' },
    { nombre: 'AX₃ Trigonal Planar', simbolo: '[AX₃] ⟁ (120°)', descripcion: 'Trigonal planar' },
    { nombre: 'AX₂E Angular', simbolo: '[AX₂E] ⌒ A (<120°)', descripcion: 'Angular con 1 par solitario' },
    { nombre: 'AX₄ Tetraédrica', simbolo: '[AX₄] ⧓ (109.5°)', descripcion: 'Tetraédrica' },
    { nombre: 'AX₃E Piramidal', simbolo: '[AX₃E] ⧩ (<109.5°)', descripcion: 'Trigonal piramidal' },
    { nombre: 'AX₂E₂ Angular', simbolo: '[AX₂E₂] ⌒ (<109.5°)', descripcion: 'Angular con 2 pares' },
    { nombre: 'AX₅ Trigoal Bipiramidal', simbolo: '[AX₅] ⧮', descripcion: 'Trigonal bipiramidal' },
    { nombre: 'AX₄E Balancín', simbolo: '[AX₄E] ⧰', descripcion: 'Balancín (seesaw)' },
    { nombre: 'AX₃E₂ Forma T', simbolo: '[AX₃E₂] ⊤', descripcion: 'Forma de T' },
    { nombre: 'AX₂E₃ Lineal', simbolo: '[AX₂E₃] X—A—X', descripcion: 'Lineal con 3 pares' },
    { nombre: 'AX₆ Octaédrica', simbolo: '[AX₆] ⧈', descripcion: 'Octaédrica' },
    { nombre: 'AX₅E Piramidal Cuadrada', simbolo: '[AX₅E] ⧉', descripcion: 'Piramidal cuadrada' },
    { nombre: 'AX₄E₂ Plana Cuadrada', simbolo: '[AX₄E₂] ▢', descripcion: 'Plana cuadrada' }
  ];

  // ↻ CATEGORÍA 4: Movimiento de Electrones
  const electrones = [
    { nombre: 'Flecha Curva →', simbolo: '↷ (movimiento par e⁻)', descripcion: 'Movimiento de par electrónico' },
    { nombre: 'Flecha Curva Doble ⇉', simbolo: '↷↷ (dos pares)', descripcion: 'Movimiento de dos pares' },
    { nombre: 'Flecha Media →', simbolo: '⤼ (electrón individual)', descripcion: 'Movimiento de 1 electrón' },
    { nombre: 'Nucleófilo → Electrófilo', simbolo: 'Nu:⁻ → E⁺', descripcion: 'Ataque nucleofílico' },
    { nombre: 'Flecha Retrocurva ↶', simbolo: '↶ (retroceso)', descripcion: 'Movimiento reverso' },
    { nombre: 'Flecha Doble Cabeza ⇄', simbolo: '⇄ (resonancia)', descripcion: 'Movimiento bidireccional' },
    { nombre: 'Flecha Pescado ⥅', simbolo: '⥅ (rompimiento)', descripcion: 'Rompimiento homolítico' },
    { nombre: 'Flecha Larga ⟿', simbolo: '⟿ (transferencia)', descripcion: 'Transferencia electrónica' },
    { nombre: 'Donación e⁻', simbolo: '→ (donación)', descripcion: 'Donación de electrones' },
    { nombre: 'Retiro e⁻', simbolo: '← (retiro)', descripcion: 'Retiro de electrones' }
  ];

  // δ CATEGORÍA 5: Cargas Parciales y Polaridad
  const cargas = [
    { nombre: 'δ+ (parcial positiva)', simbolo: 'δ⁺', descripcion: 'Carga parcial positiva' },
    { nombre: 'δ− (parcial negativa)', simbolo: 'δ⁻', descripcion: 'Carga parcial negativa' },
    { nombre: 'Dipolo →', simbolo: '→ (dipolo)', descripcion: 'Momento dipolar' },
    { nombre: 'Dipolo Neto ⇒', simbolo: '⇒ (dipolo neto)', descripcion: 'Dipolo molecular neto' },
    { nombre: 'Polarización ⟶', simbolo: '⟶ (polarización)', descripcion: 'Polarización de enlace' },
    { nombre: 'Carga +1', simbolo: '+', descripcion: 'Carga formal +1' },
    { nombre: 'Carga −1', simbolo: '−', descripcion: 'Carga formal −1' },
    { nombre: 'Carga +2', simbolo: '²⁺', descripcion: 'Carga +2' },
    { nombre: 'Carga −2', simbolo: '²⁻', descripcion: 'Carga −2' },
    { nombre: 'No Polar', simbolo: '⊝ (no polar)', descripcion: 'Enlace no polar' },
    { nombre: 'Polar', simbolo: '⊕→⊖ (polar)', descripcion: 'Enlace polar' }
  ];

  // 📊 CATEGORÍA 6: Diagramas de Orbitales Moleculares
  const mo = [
    { nombre: 'MO Homonuclear H₂', simbolo: '[MO H₂] σ₁s, σ*₁s', descripcion: 'Diagrama MO para H₂' },
    { nombre: 'MO Homonuclear O₂', simbolo: '[MO O₂] σ₂s, σ*₂s, σ₂p, π₂p, π*₂p, σ*₂p', descripcion: 'Diagrama MO para O₂' },
    { nombre: 'MO Heteronuclear CO', simbolo: '[MO CO] energías diferentes', descripcion: 'Diagrama MO para CO' },
    { nombre: 'MO General', simbolo: '[MO] ⎢ Átomo A ⎢ OM ⎢ Átomo B ⎢', descripcion: 'Plantilla MO genérica' },
    { nombre: 'Orbital σ Enlazante', simbolo: 'σ (enlazante)', descripcion: 'Orbital σ enlazante' },
    { nombre: 'Orbital σ* Antienlazante', simbolo: 'σ* (antienlazante)', descripcion: 'Orbital σ* antienlazante' },
    { nombre: 'Orbital π Enlazante', simbolo: 'π (enlazante)', descripcion: 'Orbital π enlazante' },
    { nombre: 'Orbital π* Antienlazante', simbolo: 'π* (antienlazante)', descripcion: 'Orbital π* antienlazante' },
    { nombre: 'Electrones ↑↓', simbolo: '↑↓', descripcion: 'Par de electrones apareados' },
    { nombre: 'Electrón ↑', simbolo: '↑', descripcion: 'Electrón desapareado' },
    { nombre: 'Nivel Energía —', simbolo: '———', descripcion: 'Nivel de energía' },
    { nombre: 'Eje Energía ↑', simbolo: 'E ↑', descripcion: 'Eje de energía' }
  ];

  // •• CATEGORÍA 7: Representación Electrónica
  const pares = [
    { nombre: 'Par Electrónico ••', simbolo: '••', descripcion: 'Par de electrones no enlazantes' },
    { nombre: 'Electrón Individual •', simbolo: '•', descripcion: 'Electrón individual' },
    { nombre: 'Par Enlazante —', simbolo: '—', descripcion: 'Par enlazante (enlace simple)' },
    { nombre: 'Dos Pares ==', simbolo: '═', descripcion: 'Enlace doble (2 pares)' },
    { nombre: 'Tres Pares ≡', simbolo: '≡', descripcion: 'Enlace triple (3 pares)' },
    { nombre: 'Nube e⁻ ⊙', simbolo: '⊙', descripcion: 'Nube electrónica' },
    { nombre: 'Densidad e⁻ Alta', simbolo: '⊚ (alta densidad)', descripcion: 'Alta densidad electrónica' },
    { nombre: 'Densidad e⁻ Baja', simbolo: '○ (baja densidad)', descripcion: 'Baja densidad electrónica' },
    { nombre: 'Radical •', simbolo: '• (radical)', descripcion: 'Radical libre' },
    { nombre: 'Carbocatión ⁺', simbolo: '⁺ (carbocatión)', descripcion: 'Carbocatión' },
    { nombre: 'Carbanión ⁻', simbolo: '⁻ (carbanión)', descripcion: 'Carbanión' }
  ];

  // ⇌ CATEGORÍA 8: Resonancia
  const resonancia = [
    { nombre: 'Flecha Resonancia ⇌', simbolo: '⇌', descripcion: 'Flecha de resonancia doble' },
    { nombre: 'Estructura A | B', simbolo: '[Estructura A] ⇌ [Estructura B]', descripcion: 'Dos estructuras resonantes' },
    { nombre: 'Híbrido de Resonancia', simbolo: '[Híbrido] ⟷', descripcion: 'Estructura híbrida' },
    { nombre: 'Contribución Mayor →', simbolo: '→ (mayor)', descripcion: 'Contribución principal' },
    { nombre: 'Contribución Menor ⇀', simbolo: '⇀ (menor)', descripcion: 'Contribución secundaria' },
    { nombre: 'Carga Deslocalizada', simbolo: '⊖…⊖ (deslocalizada)', descripcion: 'Carga deslocalizada' },
    { nombre: 'Enlace Parcial ⋯', simbolo: '⋯ (parcial)', descripcion: 'Enlace parcial' }
  ];

  // ⚡ CATEGORÍA 9: Enlaces Especiales
  const enlaces = [
    { nombre: 'Enlace σ', simbolo: 'σ (sigma)', descripcion: 'Enlace sigma' },
    { nombre: 'Enlace π', simbolo: 'π (pi)', descripcion: 'Enlace pi' },
    { nombre: 'Enlace Simple —', simbolo: '—', descripcion: 'Enlace simple' },
    { nombre: 'Enlace Doble =', simbolo: '═', descripcion: 'Enlace doble' },
    { nombre: 'Enlace Triple ≡', simbolo: '≡', descripcion: 'Enlace triple' },
    { nombre: 'Enlace Coordinado →', simbolo: '→ (coordinado)', descripcion: 'Enlace coordinado/dativo' },
    { nombre: 'Enlace Parcial ⋯', simbolo: '⋯', descripcion: 'Enlace parcial' },
    { nombre: 'Enlace Iónico ⊕—⊖', simbolo: '⊕—⊖', descripcion: 'Enlace iónico' },
    { nombre: 'Enlace Puente Hidrógeno', simbolo: '⋯H⋯', descripcion: 'Puente de hidrógeno' },
    { nombre: 'Enlace Metálico', simbolo: '⊕e⁻⊕', descripcion: 'Enlace metálico' },
    { nombre: 'Enlace van der Waals', simbolo: '… (débil)', descripcion: 'Fuerzas de van der Waals' },
    { nombre: 'Rompimiento →←', simbolo: '→←', descripcion: 'Rompimiento de enlace' }
  ];

  const getActiveComponents = () => {
    switch(activeTab) {
      case 'orbitales': return orbitales;
      case 'hibridacion': return hibridacion;
      case 'vsepr': return vsepr;
      case 'electrones': return electrones;
      case 'cargas': return cargas;
      case 'mo': return mo;
      case 'pares': return pares;
      case 'resonancia': return resonancia;
      case 'enlaces': return enlaces;
      default: return [];
    }
  };

  return (
    <div style={{
      background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%)',
      borderRadius: '12px',
      padding: '1rem',
      border: '1px solid rgba(168, 85, 247, 0.2)'
    }}>
      {/* Tabs de categorías */}
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        marginBottom: '1rem',
        flexWrap: 'wrap',
        borderBottom: '2px solid rgba(168, 85, 247, 0.2)',
        paddingBottom: '0.75rem'
      }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '0.5rem 1rem',
              background: activeTab === tab.id 
                ? 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)'
                : 'rgba(168, 85, 247, 0.1)',
              color: activeTab === tab.id ? '#fff' : '#e9d5ff',
              border: activeTab === tab.id 
                ? '2px solid #a855f7'
                : '1px solid rgba(168, 85, 247, 0.3)',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '0.8rem',
              fontWeight: activeTab === tab.id ? '600' : '500',
              transition: 'all 0.2s ease',
              boxShadow: activeTab === tab.id 
                ? '0 4px 12px rgba(168, 85, 247, 0.3)'
                : 'none'
            }}
            onMouseOver={(e) => {
              if (activeTab !== tab.id) {
                e.target.style.background = 'rgba(168, 85, 247, 0.2)';
                e.target.style.borderColor = 'rgba(168, 85, 247, 0.5)';
              }
            }}
            onMouseOut={(e) => {
              if (activeTab !== tab.id) {
                e.target.style.background = 'rgba(168, 85, 247, 0.1)';
                e.target.style.borderColor = 'rgba(168, 85, 247, 0.3)';
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
        gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
        gap: '0.75rem',
        maxHeight: '300px',
        overflowY: 'auto',
        padding: '0.5rem'
      }}>
        {getActiveComponents().map((comp, idx) => (
          <button
            type="button"
            key={idx}
            onClick={() => onInsertComponent(comp.simbolo)}
            title={comp.descripcion}
            style={{
              padding: '0.75rem',
              background: 'rgba(168, 85, 247, 0.08)',
              border: '1px solid rgba(168, 85, 247, 0.25)',
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
              e.currentTarget.style.background = 'rgba(168, 85, 247, 0.15)';
              e.currentTarget.style.borderColor = '#a855f7';
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(168, 85, 247, 0.2)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = 'rgba(168, 85, 247, 0.08)';
              e.currentTarget.style.borderColor = 'rgba(168, 85, 247, 0.25)';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <div style={{
              fontSize: '1.4rem',
              color: '#a855f7',
              fontWeight: '700',
              lineHeight: '1.2',
              fontFamily: 'monospace',
              minHeight: '2.5rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              {comp.simbolo.substring(0, 12)}
            </div>
            <div style={{
              fontSize: '0.7rem',
              color: '#e9d5ff',
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
        background: 'rgba(168, 85, 247, 0.05)',
        borderRadius: '8px',
        fontSize: '0.75rem',
        color: '#ddd6fe',
        borderLeft: '3px solid #a855f7'
      }}>
        <strong style={{color: '#a855f7'}}>💡 Química Avanzada:</strong><br/>
        {activeTab === 'orbitales' && '⚛️ Orbitales atómicos s, p, d, f con orientaciones y formas específicas'}
        {activeTab === 'hibridacion' && '🔺 Hibridación sp/sp²/sp³ con ángulos característicos (180°, 120°, 109.5°)'}
        {activeTab === 'vsepr' && '🔷 Geometrías moleculares VSEPR (lineal, trigonal, tetraédrica, octaédrica)'}
        {activeTab === 'electrones' && '↻ Flechas curvas para movimientos electrónicos en mecanismos de reacción'}
        {activeTab === 'cargas' && 'δ Cargas parciales (δ⁺/δ⁻), momentos dipolares, polarización de enlaces'}
        {activeTab === 'mo' && '📊 Diagramas de orbitales moleculares (σ, σ*, π, π*) para moléculas diatómicas'}
        {activeTab === 'pares' && '•• Pares electrónicos, electrones individuales, radicales, densidad electrónica'}
        {activeTab === 'resonancia' && '⇌ Estructuras de resonancia con flechas dobles y cargas deslocalizadas'}
        {activeTab === 'enlaces' && '⚡ Enlaces σ, π, coordinados, puentes de hidrógeno, fuerzas intermoleculares'}
      </div>
    </div>
  );
}

export default AdvancedChemistryToolbar;
