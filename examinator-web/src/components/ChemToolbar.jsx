import { useState } from 'react'

/**
 * Panel de Herramientas Químicas
 * 
 * Categorías:
 * - Anillos (hexágonos aromáticos y alifáticos)
 * - Enlaces (simples, dobles, triples)
 * - Átomos comunes
 * - Grupos funcionales
 * - Reacciones básicas
 * - Geometrías moleculares
 */

const CATEGORIAS_QUIMICA = {
  anillos: {
    nombre: 'Anillos',
    icono: '⬡',
    estructuras: [
      { nombre: 'Benceno', smiles: 'c1ccccc1', descripcion: 'Anillo aromático básico' },
      { nombre: 'Ciclohexano', smiles: 'C1CCCCC1', descripcion: 'Anillo saturado de 6 carbonos' },
      { nombre: 'Ciclopentano', smiles: 'C1CCCC1', descripcion: 'Anillo saturado de 5 carbonos' },
      { nombre: 'Naftaleno', smiles: 'c1ccc2ccccc2c1', descripcion: 'Dos anillos fusionados' },
      { nombre: 'Piridina', smiles: 'c1ccncc1', descripcion: 'Anillo aromático con N' },
      { nombre: 'Furano', smiles: 'c1ccoc1', descripcion: 'Anillo aromático con O' },
    ]
  },
  funcionales: {
    nombre: 'Grupos Funcionales',
    icono: '-OH',
    estructuras: [
      { nombre: 'Alcohol (-OH)', smiles: 'CCO', descripcion: 'Etanol como ejemplo' },
      { nombre: 'Aldehído (-CHO)', smiles: 'CC=O', descripcion: 'Acetaldehído' },
      { nombre: 'Cetona (C=O)', smiles: 'CC(=O)C', descripcion: 'Acetona' },
      { nombre: 'Ácido (-COOH)', smiles: 'CC(=O)O', descripcion: 'Ácido acético' },
      { nombre: 'Amina (-NH₂)', smiles: 'CCN', descripcion: 'Etilamina' },
      { nombre: 'Éter (-O-)', smiles: 'CCOC', descripcion: 'Éter dietílico' },
      { nombre: 'Éster (-COO-)', smiles: 'CC(=O)OC', descripcion: 'Acetato de metilo' },
      { nombre: 'Amida (-CONH₂)', smiles: 'CC(=O)N', descripcion: 'Acetamida' },
      { nombre: 'Nitrilo (-CN)', smiles: 'CC#N', descripcion: 'Acetonitrilo' },
      { nombre: 'Haluro (-Cl)', smiles: 'CCCl', descripcion: 'Cloruro de etilo' },
    ]
  },
  cadenas: {
    nombre: 'Cadenas',
    icono: '─',
    estructuras: [
      { nombre: 'Metano', smiles: 'C', descripcion: 'CH₄' },
      { nombre: 'Etano', smiles: 'CC', descripcion: 'CH₃-CH₃' },
      { nombre: 'Propano', smiles: 'CCC', descripcion: 'CH₃-CH₂-CH₃' },
      { nombre: 'Butano', smiles: 'CCCC', descripcion: 'Cadena de 4 carbonos' },
      { nombre: 'Pentano', smiles: 'CCCCC', descripcion: 'Cadena de 5 carbonos' },
      { nombre: 'Hexano', smiles: 'CCCCCC', descripcion: 'Cadena de 6 carbonos' },
    ]
  },
  insaturados: {
    nombre: 'Insaturados',
    icono: '═',
    estructuras: [
      { nombre: 'Eteno', smiles: 'C=C', descripcion: 'Doble enlace' },
      { nombre: 'Propeno', smiles: 'CC=C', descripcion: 'CH₃-CH=CH₂' },
      { nombre: 'Etino', smiles: 'C#C', descripcion: 'Triple enlace (acetileno)' },
      { nombre: 'Propino', smiles: 'CC#C', descripcion: 'CH₃-C≡CH' },
      { nombre: '1,3-Butadieno', smiles: 'C=CC=C', descripcion: 'Dieno conjugado' },
    ]
  },
  biomoleculas: {
    nombre: 'Biomoléculas',
    icono: '🧬',
    estructuras: [
      { nombre: 'Glucosa', smiles: 'C(C1C(C(C(C(O1)O)O)O)O)O', descripcion: 'Azúcar simple' },
      { nombre: 'Glicina', smiles: 'C(C(=O)O)N', descripcion: 'Aminoácido más simple' },
      { nombre: 'Alanina', smiles: 'CC(C(=O)O)N', descripcion: 'Aminoácido' },
      { nombre: 'Adenina', smiles: 'c1nc(c2c(n1)ncn2)N', descripcion: 'Base nitrogenada' },
    ]
  },
  aromaticos: {
    nombre: 'Aromáticos',
    icono: '⬡⬡',
    estructuras: [
      { nombre: 'Tolueno', smiles: 'Cc1ccccc1', descripcion: 'Benceno con CH₃' },
      { nombre: 'Fenol', smiles: 'Oc1ccccc1', descripcion: 'Benceno con -OH' },
      { nombre: 'Anilina', smiles: 'Nc1ccccc1', descripcion: 'Benceno con -NH₂' },
      { nombre: 'Ácido benzoico', smiles: 'O=C(O)c1ccccc1', descripcion: 'Benceno con -COOH' },
      { nombre: 'Estireno', smiles: 'C=Cc1ccccc1', descripcion: 'Benceno con vinil' },
    ]
  }
}

const ChemToolbar = ({ onInsertStructure }) => {
  const [categoriaActiva, setCategoriaActiva] = useState('anillos')

  return (
    <div style={{
      background: 'rgba(17, 24, 39, 0.95)',
      border: '1px solid rgba(16, 185, 129, 0.3)',
      borderRadius: '12px',
      overflow: 'hidden'
    }}>
      {/* Tabs de categorías */}
      <div style={{
        display: 'flex',
        gap: '4px',
        padding: '12px',
        borderBottom: '1px solid rgba(16, 185, 129, 0.2)',
        overflowX: 'auto',
        flexWrap: 'wrap'
      }}>
        {Object.entries(CATEGORIAS_QUIMICA).map(([key, cat]) => (
          <button
            type="button"
            key={key}
            onClick={() => setCategoriaActiva(key)}
            style={{
              padding: '8px 16px',
              background: categoriaActiva === key 
                ? 'linear-gradient(135deg, #10b981, #059669)' 
                : 'rgba(16, 185, 129, 0.1)',
              color: categoriaActiva === key ? '#fff' : '#a7f3d0',
              border: categoriaActiva === key 
                ? '1px solid #34d399' 
                : '1px solid rgba(16, 185, 129, 0.2)',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: categoriaActiva === key ? '600' : '500',
              transition: 'all 0.2s',
              whiteSpace: 'nowrap'
            }}
            onMouseEnter={(e) => {
              if (categoriaActiva !== key) {
                e.target.style.background = 'rgba(16, 185, 129, 0.2)'
              }
            }}
            onMouseLeave={(e) => {
              if (categoriaActiva !== key) {
                e.target.style.background = 'rgba(16, 185, 129, 0.1)'
              }
            }}
          >
            <span style={{ marginRight: '6px' }}>{cat.icono}</span>
            {cat.nombre}
          </button>
        ))}
      </div>

      {/* Grid de estructuras */}
      <div style={{
        padding: '16px',
        maxHeight: '280px',
        overflowY: 'auto'
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
          gap: '12px'
        }}>
          {CATEGORIAS_QUIMICA[categoriaActiva]?.estructuras.map((est, idx) => (
            <button
              type="button"
              key={idx}
              onClick={() => onInsertStructure(est.smiles)}
              style={{
                background: 'rgba(16, 185, 129, 0.08)',
                border: '1px solid rgba(16, 185, 129, 0.2)',
                borderRadius: '8px',
                padding: '12px 8px',
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                gap: '6px',
                textAlign: 'left'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(16, 185, 129, 0.15)'
                e.currentTarget.style.borderColor = '#34d399'
                e.currentTarget.style.transform = 'translateY(-2px)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(16, 185, 129, 0.08)'
                e.currentTarget.style.borderColor = 'rgba(16, 185, 129, 0.2)'
                e.currentTarget.style.transform = 'translateY(0)'
              }}
            >
              {/* Nombre */}
              <div style={{
                fontSize: '13px',
                fontWeight: '600',
                color: '#d1fae5'
              }}>
                {est.nombre}
              </div>
              
              {/* SMILES (código) */}
              <div style={{
                fontSize: '10px',
                color: '#6ee7b7',
                fontFamily: 'monospace',
                background: 'rgba(16, 185, 129, 0.1)',
                padding: '2px 6px',
                borderRadius: '4px',
                width: '100%',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}>
                {est.smiles}
              </div>

              {/* Descripción */}
              <div style={{
                fontSize: '11px',
                color: '#a7f3d0',
                lineHeight: '1.3'
              }}>
                {est.descripcion}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ChemToolbar
