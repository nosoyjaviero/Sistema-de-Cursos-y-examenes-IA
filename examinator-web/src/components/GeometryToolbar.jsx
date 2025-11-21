import { useState } from 'react';

function GeometryToolbar({ onInsertComponent }) {
  const [activeTab, setActiveTab] = useState('puntos');

  const tabs = [
    { id: 'puntos', label: '⚫ Puntos', icon: '⚫' },
    { id: 'rectas', label: '📏 Rectas', icon: '📏' },
    { id: 'angulos', label: '📐 Ángulos', icon: '📐' },
    { id: 'poligonos', label: '🔷 Polígonos', icon: '🔷' },
    { id: 'circulos', label: '⭕ Círculos', icon: '⭕' },
    { id: 'construcciones', label: '🔨 Construcciones', icon: '🔨' },
    { id: 'flechas', label: '➡️ Flechas', icon: '➡️' },
    { id: 'medidas', label: '📊 Medidas', icon: '📊' }
  ];

  // ⚫ CATEGORÍA 1: Puntos
  const puntos = [
    { nombre: 'Punto A', simbolo: '• A' },
    { nombre: 'Punto B', simbolo: '• B' },
    { nombre: 'Punto C', simbolo: '• C' },
    { nombre: 'Punto P', simbolo: '• P' },
    { nombre: 'Punto Q', simbolo: '• Q' },
    { nombre: 'Punto con Etiqueta', simbolo: '● [Label]' },
    { nombre: 'Punto Fijo', simbolo: '✱' },
    { nombre: 'Punto Móvil', simbolo: '○' },
    { nombre: 'Punto Medio M', simbolo: 'M (punto medio)' },
    { nombre: 'Origen (0,0)', simbolo: 'O (0,0)' },
    { nombre: 'Coordenadas (x,y)', simbolo: 'P(x, y)' }
  ];

  // 📏 CATEGORÍA 2: Rectas y Segmentos
  const rectas = [
    { nombre: 'Segmento AB', simbolo: 'AB̅' },
    { nombre: 'Recta ↔', simbolo: '←→' },
    { nombre: 'Semirrecta →', simbolo: 'AB→' },
    { nombre: 'Vector AB⃗', simbolo: 'AB⃗' },
    { nombre: 'Recta Horizontal —', simbolo: '—' },
    { nombre: 'Recta Vertical |', simbolo: '|' },
    { nombre: 'Recta Diagonal /', simbolo: '/' },
    { nombre: 'Perpendicular ⟂', simbolo: 'AB ⟂ CD' },
    { nombre: 'Paralela ∥', simbolo: 'AB ∥ CD' },
    { nombre: 'Bisectriz', simbolo: '[Bisectriz] ∠ABC' },
    { nombre: 'Eje X', simbolo: 'x─────→' },
    { nombre: 'Eje Y', simbolo: 'y↑' },
    { nombre: 'Plano Cartesiano', simbolo: '[Plano] x-y' }
  ];

  // 📐 CATEGORÍA 3: Ángulos
  const angulos = [
    { nombre: 'Ángulo ∠ABC', simbolo: '∠ABC' },
    { nombre: 'Ángulo Recto ⟂', simbolo: '∠ABC = 90°' },
    { nombre: 'Ángulo Agudo', simbolo: '∠ < 90°' },
    { nombre: 'Ángulo Obtuso', simbolo: '∠ > 90°' },
    { nombre: 'Ángulo Llano 180°', simbolo: '∠ = 180°' },
    { nombre: 'Ángulo 30°', simbolo: '30°' },
    { nombre: 'Ángulo 45°', simbolo: '45°' },
    { nombre: 'Ángulo 60°', simbolo: '60°' },
    { nombre: 'Ángulo 90°', simbolo: '90°' },
    { nombre: 'π/6 (30°)', simbolo: 'π/6' },
    { nombre: 'π/4 (45°)', simbolo: 'π/4' },
    { nombre: 'π/3 (60°)', simbolo: 'π/3' },
    { nombre: 'π/2 (90°)', simbolo: 'π/2' },
    { nombre: 'Marca Ángulo ⌒', simbolo: '⌒' },
    { nombre: 'Arco Medida ⌢', simbolo: '⌢ θ' }
  ];

  // 🔷 CATEGORÍA 4: Triángulos y Polígonos
  const poligonos = [
    { nombre: 'Triángulo △', simbolo: '△ABC' },
    { nombre: 'Triángulo Rectángulo', simbolo: '△ (90°)' },
    { nombre: 'Triángulo Equilátero', simbolo: '△ (60°-60°-60°)' },
    { nombre: 'Triángulo Isósceles', simbolo: '△ (2 lados =)' },
    { nombre: 'Cuadrado □', simbolo: '□ABCD' },
    { nombre: 'Rectángulo ▭', simbolo: '▭ABCD' },
    { nombre: 'Rombo ◊', simbolo: '◊ABCD' },
    { nombre: 'Paralelogramo ▱', simbolo: '▱ABCD' },
    { nombre: 'Trapecio', simbolo: '[Trapecio] ABCD' },
    { nombre: 'Pentágono', simbolo: '[Pentágono] 5 lados' },
    { nombre: 'Hexágono', simbolo: '[Hexágono] 6 lados' },
    { nombre: 'Octágono', simbolo: '[Octágono] 8 lados' },
    { nombre: 'Polígono Regular', simbolo: '[Polígono] n lados' }
  ];

  // ⭕ CATEGORÍA 5: Circunferencias y Arcos
  const circulos = [
    { nombre: 'Circunferencia ○', simbolo: '○ (centro, radio)' },
    { nombre: 'Círculo ●', simbolo: '● (relleno)' },
    { nombre: 'Radio r', simbolo: 'r = □' },
    { nombre: 'Diámetro d', simbolo: 'd = 2r' },
    { nombre: 'Arco ⌒', simbolo: '⌒AB' },
    { nombre: 'Sector Circular', simbolo: '[Sector] θ' },
    { nombre: 'Segmento Circular', simbolo: '[Segmento]' },
    { nombre: 'Cuerda AB̅', simbolo: 'AB̅ (cuerda)' },
    { nombre: 'Tangente →|', simbolo: '→| (tangente)' },
    { nombre: 'Secante ↔', simbolo: '↔ (secante)' },
    { nombre: 'Circunferencia por 3 pts', simbolo: '○(A,B,C)' }
  ];

  // 🔨 CATEGORÍA 6: Construcciones Especiales
  const construcciones = [
    { nombre: 'Mediatriz ⟂', simbolo: '[Mediatriz] AB̅' },
    { nombre: 'Bisectriz ∠', simbolo: '[Bisectriz] ∠ABC' },
    { nombre: 'Altura h', simbolo: '[Altura] △ABC' },
    { nombre: 'Mediana m', simbolo: '[Mediana] △ABC' },
    { nombre: 'Circuncentro O', simbolo: 'O (circuncentro)' },
    { nombre: 'Baricentro G', simbolo: 'G (baricentro)' },
    { nombre: 'Ortocentro H', simbolo: 'H (ortocentro)' },
    { nombre: 'Incentro I', simbolo: 'I (incentro)' },
    { nombre: 'Perpendicular desde P', simbolo: '[⟂] desde P a r' },
    { nombre: 'Paralela desde P', simbolo: '[∥] desde P a r' },
    { nombre: 'División Áurea φ', simbolo: 'φ = (1+√5)/2' }
  ];

  // ➡️ CATEGORÍA 7: Flechas y Notación
  const flechas = [
    { nombre: 'Flecha →', simbolo: '→' },
    { nombre: 'Flecha ←', simbolo: '←' },
    { nombre: 'Flecha ↔', simbolo: '↔' },
    { nombre: 'Flecha ↑', simbolo: '↑' },
    { nombre: 'Flecha ↓', simbolo: '↓' },
    { nombre: 'Flecha Curva ↻', simbolo: '↻' },
    { nombre: 'Flecha Curva ↺', simbolo: '↺' },
    { nombre: 'Doble Flecha ⇄', simbolo: '⇄' },
    { nombre: 'Vector ⃗', simbolo: 'v⃗' },
    { nombre: 'Marca × (cruz)', simbolo: '×' },
    { nombre: 'Marca • (punto)', simbolo: '•' },
    { nombre: 'Marca ⟂', simbolo: '⟂' },
    { nombre: 'Marca ∥', simbolo: '∥' },
    { nombre: 'Etiqueta [ ]', simbolo: '[Label]' }
  ];

  // 📊 CATEGORÍA 8: Medidas y Trigonometría
  const medidas = [
    { nombre: 'Longitud |AB|', simbolo: '|AB| = □' },
    { nombre: 'Distancia d(A,B)', simbolo: 'd(A,B) = □' },
    { nombre: 'Perímetro P', simbolo: 'P = □' },
    { nombre: 'Área A', simbolo: 'A = □' },
    { nombre: 'Pendiente m', simbolo: 'm = Δy/Δx' },
    { nombre: 'Pendiente Positiva /', simbolo: 'm > 0' },
    { nombre: 'Pendiente Negativa \\', simbolo: 'm < 0' },
    { nombre: 'sen θ', simbolo: 'sen θ = cateto opuesto / hipotenusa' },
    { nombre: 'cos θ', simbolo: 'cos θ = cateto adyacente / hipotenusa' },
    { nombre: 'tan θ', simbolo: 'tan θ = cateto opuesto / cateto adyacente' },
    { nombre: 'Teorema Pitágoras', simbolo: 'a² + b² = c²' },
    { nombre: 'Cateto a', simbolo: 'a = □' },
    { nombre: 'Cateto b', simbolo: 'b = □' },
    { nombre: 'Hipotenusa c', simbolo: 'c = □' },
    { nombre: 'Radio r', simbolo: 'r = □' },
    { nombre: 'π (pi)', simbolo: 'π ≈ 3.14159' },
    { nombre: '√2', simbolo: '√2 ≈ 1.414' },
    { nombre: '√3', simbolo: '√3 ≈ 1.732' }
  ];

  const getActiveComponents = () => {
    switch(activeTab) {
      case 'puntos': return puntos;
      case 'rectas': return rectas;
      case 'angulos': return angulos;
      case 'poligonos': return poligonos;
      case 'circulos': return circulos;
      case 'construcciones': return construcciones;
      case 'flechas': return flechas;
      case 'medidas': return medidas;
      default: return [];
    }
  };

  return (
    <div style={{
      background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%)',
      borderRadius: '12px',
      padding: '1rem',
      border: '1px solid rgba(34, 197, 94, 0.2)'
    }}>
      {/* Tabs de categorías */}
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        marginBottom: '1rem',
        flexWrap: 'wrap',
        borderBottom: '2px solid rgba(34, 197, 94, 0.2)',
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
                ? 'linear-gradient(135deg, #22c55e 0%, #3b82f6 100%)'
                : 'rgba(34, 197, 94, 0.1)',
              color: activeTab === tab.id ? '#fff' : '#d1fae5',
              border: activeTab === tab.id 
                ? '2px solid #22c55e'
                : '1px solid rgba(34, 197, 94, 0.3)',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '0.85rem',
              fontWeight: activeTab === tab.id ? '600' : '500',
              transition: 'all 0.2s ease',
              boxShadow: activeTab === tab.id 
                ? '0 4px 12px rgba(34, 197, 94, 0.3)'
                : 'none'
            }}
            onMouseOver={(e) => {
              if (activeTab !== tab.id) {
                e.target.style.background = 'rgba(34, 197, 94, 0.2)';
                e.target.style.borderColor = 'rgba(34, 197, 94, 0.5)';
              }
            }}
            onMouseOut={(e) => {
              if (activeTab !== tab.id) {
                e.target.style.background = 'rgba(34, 197, 94, 0.1)';
                e.target.style.borderColor = 'rgba(34, 197, 94, 0.3)';
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
        gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))',
        gap: '0.75rem',
        maxHeight: '280px',
        overflowY: 'auto',
        padding: '0.5rem'
      }}>
        {getActiveComponents().map((comp, idx) => (
          <button
            type="button"
            key={idx}
            onClick={() => onInsertComponent(comp.simbolo)}
            style={{
              padding: '0.75rem',
              background: 'rgba(34, 197, 94, 0.08)',
              border: '1px solid rgba(34, 197, 94, 0.25)',
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
              e.currentTarget.style.background = 'rgba(34, 197, 94, 0.15)';
              e.currentTarget.style.borderColor = '#22c55e';
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(34, 197, 94, 0.2)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = 'rgba(34, 197, 94, 0.08)';
              e.currentTarget.style.borderColor = 'rgba(34, 197, 94, 0.25)';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <div style={{
              fontSize: '1.5rem',
              color: '#22c55e',
              fontWeight: '700',
              lineHeight: '1.2',
              fontFamily: 'serif'
            }}>
              {comp.simbolo.substring(0, 8)}
            </div>
            <div style={{
              fontSize: '0.7rem',
              color: '#d1fae5',
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
        background: 'rgba(34, 197, 94, 0.05)',
        borderRadius: '8px',
        fontSize: '0.75rem',
        color: '#bbf7d0',
        borderLeft: '3px solid #22c55e'
      }}>
        <strong style={{color: '#22c55e'}}>💡 Herramientas Geométricas:</strong><br/>
        {activeTab === 'puntos' && '⚫ Puntos etiquetados, fijos, móviles, coordenadas (x,y), origen'}
        {activeTab === 'rectas' && '📏 Segmentos, rectas, semirrectas, vectores, perpendiculares (⟂), paralelas (∥), ejes'}
        {activeTab === 'angulos' && '📐 Ángulos rectos, agudos, obtusos, medidas en grados (30°, 45°, 60°, 90°) y radianes (π/6, π/4, π/3)'}
        {activeTab === 'poligonos' && '🔷 Triángulos (rectángulo, equilátero, isósceles), cuadrados, rectángulos, rombos, polígonos regulares'}
        {activeTab === 'circulos' && '⭕ Circunferencias, círculos, radios, diámetros, arcos, sectores, cuerdas, tangentes, secantes'}
        {activeTab === 'construcciones' && '🔨 Mediatriz, bisectriz, alturas, medianas, puntos notables (circuncentro, baricentro, ortocentro)'}
        {activeTab === 'flechas' && '➡️ Flechas direccionales, vectores, marcas de perpendicularidad (⟂), paralelismo (∥), etiquetas'}
        {activeTab === 'medidas' && '📊 Longitudes, distancias, áreas, perímetros, pendientes, trigonometría (sen, cos, tan), Pitágoras'}
      </div>
    </div>
  );
}

export default GeometryToolbar;
