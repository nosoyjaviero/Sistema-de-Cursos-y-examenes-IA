import { useState } from 'react';

/**
 * 🎨 SELECTOR DE MODOS VISUALES
 * Sistema de "Contextual Toolbars" estilo Figma/Notion
 * Hace que la app NO parezca de programadores
 */
export default function VisualModeSelector({ onModeChange, currentMode }) {
  const modes = [
    {
      id: 'texto',
      icon: '📝',
      name: 'Texto Simple',
      color: '#94a3b8',
      description: 'Flashcards clásicas con texto',
      tipos: ['clasica', 'cloze', 'mcq', 'error', 'escenario']
    },
    {
      id: 'matematicas',
      icon: '📐',
      name: 'Matemáticas',
      color: '#3b82f6',
      description: 'Fórmulas, ecuaciones, fracciones',
      tipos: ['matematica']
    },
    {
      id: 'quimica',
      icon: '🧪',
      name: 'Química',
      color: '#10b981',
      description: 'Moléculas, estructuras, reacciones',
      tipos: ['quimica', 'quimica-avanzada']
    },
    {
      id: 'fisica',
      icon: '⚡',
      name: 'Física',
      color: '#f59e0b',
      description: 'Diagramas, fuerzas, vectores',
      tipos: ['fisica']
    },
    {
      id: 'geometria',
      icon: '📐',
      name: 'Geometría',
      color: '#22c55e',
      description: 'Puntos, rectas, triángulos, círculos',
      tipos: ['geometria']
    },
    {
      id: 'ingenieria',
      icon: '🔧',
      name: 'Ingeniería',
      color: '#ef4444',
      description: 'DCL, vigas, mecanismos',
      tipos: ['ingenieria']
    },
    {
      id: 'logica',
      icon: '🔮',
      name: 'Lógica',
      color: '#7c3aed',
      description: 'Tablas verdad, conjuntos, grafos',
      tipos: ['logica-discreta']
    },
    {
      id: 'fonetica',
      icon: '🗣️',
      name: 'Fonética',
      color: '#ec4899',
      description: 'IPA, acento, entonación',
      tipos: ['linguistica']
    },
    {
      id: 'musica',
      icon: '🎼',
      name: 'Música',
      color: '#a855f7',
      description: 'Pentagramas, notas, acordes',
      tipos: ['musica']
    },
    {
      id: 'programacion',
      icon: '💻',
      name: 'Programación',
      color: '#14b8a6',
      description: 'UML, algoritmos, código',
      tipos: ['programacion', 'programacion-avanzada']
    },
    {
      id: 'probabilidad',
      icon: '🎲',
      name: 'Probabilidad',
      color: '#8b5cf6',
      description: 'Árboles, Venn, distribuciones',
      tipos: ['probabilidad']
    },
    {
      id: 'datos',
      icon: '📊',
      name: 'Datos',
      color: '#06b6d4',
      description: 'Tablas, gráficos, estadística',
      tipos: ['datos']
    },
    {
      id: 'arte',
      icon: '🎨',
      name: 'Arte',
      color: '#f472b6',
      description: 'Figuras, paletas, composiciones',
      tipos: ['arte']
    }
  ];

  return (
    <div style={{
      background: 'rgba(15, 23, 42, 0.95)',
      borderRadius: '16px',
      padding: '1.5rem',
      marginBottom: '1.5rem',
      border: '2px solid rgba(148, 163, 184, 0.2)'
    }}>
      <h3 style={{
        color: '#cbd5e1',
        fontSize: '0.95rem',
        fontWeight: '600',
        marginBottom: '1rem',
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem'
      }}>
        <span style={{fontSize: '1.2rem'}}>✨</span>
        ¿Qué tipo de contenido quieres crear?
      </h3>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
        gap: '0.75rem'
      }}>
        {modes.map(mode => (
          <button
            type="button"
            key={mode.id}
            onClick={() => onModeChange(mode)}
            style={{
              background: currentMode === mode.id 
                ? `linear-gradient(135deg, ${mode.color}40 0%, ${mode.color}20 100%)`
                : 'rgba(30, 41, 59, 0.5)',
              border: currentMode === mode.id
                ? `2px solid ${mode.color}`
                : '2px solid rgba(71, 85, 105, 0.3)',
              borderRadius: '12px',
              padding: '1rem 0.75rem',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '0.5rem',
              position: 'relative',
              overflow: 'hidden'
            }}
            onMouseEnter={(e) => {
              if (currentMode !== mode.id) {
                e.currentTarget.style.background = `rgba(${parseInt(mode.color.slice(1,3), 16)}, ${parseInt(mode.color.slice(3,5), 16)}, ${parseInt(mode.color.slice(5,7), 16)}, 0.15)`;
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = `0 8px 20px ${mode.color}30`;
              }
            }}
            onMouseLeave={(e) => {
              if (currentMode !== mode.id) {
                e.currentTarget.style.background = 'rgba(30, 41, 59, 0.5)';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }
            }}
            title={mode.description}
          >
            <span style={{fontSize: '2rem', filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3)'}}>
              {mode.icon}
            </span>
            <span style={{
              color: currentMode === mode.id ? mode.color : '#cbd5e1',
              fontSize: '0.8rem',
              fontWeight: currentMode === mode.id ? '700' : '600',
              textAlign: 'center',
              lineHeight: '1.2'
            }}>
              {mode.name}
            </span>
            <span style={{
              color: '#94a3b8',
              fontSize: '0.65rem',
              textAlign: 'center',
              lineHeight: '1.2',
              opacity: 0.8
            }}>
              {mode.description}
            </span>

            {currentMode === mode.id && (
              <div style={{
                position: 'absolute',
                top: '0.5rem',
                right: '0.5rem',
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: mode.color,
                boxShadow: `0 0 8px ${mode.color}`
              }} />
            )}
          </button>
        ))}
      </div>

      {currentMode && (
        <div style={{
          marginTop: '1rem',
          padding: '0.75rem 1rem',
          background: 'rgba(59, 130, 246, 0.1)',
          border: '1px solid rgba(59, 130, 246, 0.3)',
          borderRadius: '8px',
          fontSize: '0.85rem',
          color: '#93c5fd',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <span>💡</span>
          <span>
            Modo activo: <strong>{modes.find(m => m.id === currentMode)?.name}</strong>
            {' '}- Solo verás las herramientas necesarias para este tipo de contenido
          </span>
        </div>
      )}
    </div>
  );
}
