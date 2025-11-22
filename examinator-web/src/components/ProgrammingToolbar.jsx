import { useState } from 'react';

const ProgrammingToolbar = ({ onInsertComponent }) => {
  const [tabActiva, setTabActiva] = useState('uml');

  // 🟣 UML - Clases, interfaces, relaciones, paquetes
  const componentesUML = [
    { nombre: 'Clase', svg: 'M2 2 L38 2 L38 38 L2 38 Z M2 12 L38 12 M2 22 L38 22', latex: 'ClassName', desc: 'Clase con atributos y métodos' },
    { nombre: 'Interfaz', svg: 'M2 2 L38 2 L38 38 L2 38 Z M10 6 L30 6 M2 12 L38 12 M2 22 L38 22', latex: '<<interface>>', desc: 'Interface con métodos abstractos' },
    { nombre: 'Clase Abstracta', svg: 'M2 2 L38 2 L38 38 L2 38 Z M10 8 L30 8 M2 12 L38 12 M2 22 L38 22', latex: '<<abstract>>', desc: 'Clase abstracta' },
    { nombre: 'Asociación', svg: 'M2 20 L38 20', latex: '---', desc: 'Relación de asociación' },
    { nombre: 'Herencia', svg: 'M2 30 L20 10 L38 30 M20 10 L20 35', latex: '--|>', desc: 'Relación de herencia' },
    { nombre: 'Implementación', svg: 'M2 30 L20 10 L38 30 M20 10 L20 35 M5 28 L15 18 M25 18 L35 28', latex: '..|>', desc: 'Implementación de interfaz' },
    { nombre: 'Agregación', svg: 'M2 20 L15 10 L28 20 L15 30 Z M28 20 L38 20', latex: 'o--', desc: 'Agregación (rombo vacío)' },
    { nombre: 'Composición', svg: 'M2 20 L15 10 L28 20 L15 30 Z M28 20 L38 20', latex: '*--', desc: 'Composición (rombo lleno)', fill: true },
    { nombre: 'Dependencia', svg: 'M2 20 L38 20 M10 18 L8 20 L10 22 M20 18 L18 20 L20 22 M30 18 L28 20 L30 22', latex: '..>', desc: 'Relación de dependencia' },
    { nombre: 'Paquete', svg: 'M2 8 L18 8 L18 2 L38 2 L38 38 L2 38 Z', latex: 'package', desc: 'Paquete o módulo' },
    { nombre: 'Nota', svg: 'M2 2 L32 2 L38 8 L38 38 L2 38 Z M32 2 L32 8 L38 8', latex: 'note', desc: 'Nota o comentario' },
    { nombre: 'Atributo +', svg: 'M15 12 L25 12 M20 7 L20 17', latex: '+attribute', desc: 'Atributo público' },
    { nombre: 'Atributo -', svg: 'M15 12 L25 12', latex: '-attribute', desc: 'Atributo privado' },
    { nombre: 'Método', svg: 'M8 15 C8 10, 32 10, 32 15 C32 20, 8 20, 8 15', latex: 'method()', desc: 'Método de clase' }
  ];

  // 🟡 Diagramas de Flujo - Formas estándar de flujo
  const componentesFlujo = [
    { nombre: 'Inicio/Fin', svg: 'M2 20 C2 10, 38 10, 38 20 C38 30, 2 30, 2 20', latex: 'START/END', desc: 'Inicio o fin del flujo' },
    { nombre: 'Proceso', svg: 'M5 8 L35 8 L35 32 L5 32 Z', latex: 'Proceso', desc: 'Proceso o acción' },
    { nombre: 'Decisión', svg: 'M20 2 L38 20 L20 38 L2 20 Z', latex: '¿Condición?', desc: 'Decisión o condición' },
    { nombre: 'Entrada/Salida', svg: 'M8 8 L38 8 L32 32 L2 32 Z', latex: 'Input/Output', desc: 'Entrada o salida de datos' },
    { nombre: 'Subproceso', svg: 'M5 8 L35 8 L35 32 L5 32 Z M8 8 L8 32 M32 8 L32 32', latex: 'Subproceso', desc: 'Subproceso o módulo' },
    { nombre: 'Conector', svg: 'M20 20 m -15 0 a 15 15 0 1 0 30 0 a 15 15 0 1 0 -30 0', latex: 'A', desc: 'Conector de flujo' },
    { nombre: 'Documento', svg: 'M5 8 L35 8 L35 32 C30 28, 25 36, 20 32 C15 28, 10 36, 5 32 Z', latex: 'Doc', desc: 'Documento' },
    { nombre: 'Base Datos', svg: 'M5 12 C5 8, 35 8, 35 12 L35 28 C35 32, 5 32, 5 28 Z M5 12 C5 16, 35 16, 35 12', latex: 'DB', desc: 'Base de datos' },
    { nombre: 'Flecha →', svg: 'M5 20 L30 20 L25 15 M30 20 L25 25', latex: '-->', desc: 'Flecha derecha' },
    { nombre: 'Flecha ↓', svg: 'M20 5 L20 30 L15 25 M20 30 L25 25', latex: 'down', desc: 'Flecha abajo' },
    { nombre: 'Flecha ↑', svg: 'M20 35 L20 10 L15 15 M20 10 L25 15', latex: 'up', desc: 'Flecha arriba' },
    { nombre: 'Flecha ←', svg: 'M35 20 L10 20 L15 15 M10 20 L15 25', latex: '<--', desc: 'Flecha izquierda' },
    { nombre: 'Bucle', svg: 'M10 10 L30 10 L30 30 L10 30 Z M12 15 L28 15 M12 20 L28 20', latex: 'Loop', desc: 'Estructura de bucle' }
  ];

  // 🟩 Tablas de Algoritmos - Estructuras tabulares
  const componentesTablas = [
    { nombre: 'Paso | Acción', svg: 'M2 2 L38 2 L38 38 L2 38 Z M20 2 L20 38 M2 15 L38 15', latex: 'Step | Action', desc: 'Tabla paso a paso' },
    { nombre: 'Línea | Código', svg: 'M2 2 L38 2 L38 38 L2 38 Z M10 2 L10 38 M2 12 L38 12 M2 22 L38 22 M2 32 L38 32', latex: 'Line | Code', desc: 'Tabla de código' },
    { nombre: 'Caso | Complejidad', svg: 'M2 2 L38 2 L38 38 L2 38 Z M15 2 L15 38 M25 2 L25 38 M2 15 L38 15', latex: 'Case | O()', desc: 'Análisis de complejidad' },
    { nombre: 'Variable | Valor', svg: 'M2 2 L38 2 L38 38 L2 38 Z M18 2 L18 38 M2 12 L38 12 M2 22 L38 22', latex: 'Var | Val', desc: 'Tabla de variables' },
    { nombre: 'Entrada | Salida', svg: 'M2 2 L38 2 L38 38 L2 38 Z M20 2 L20 38 M2 20 L38 20', latex: 'Input | Output', desc: 'Tabla I/O' },
    { nombre: 'Traza', svg: 'M2 2 L38 2 L38 38 L2 38 Z M12 2 L12 38 M22 2 L22 38 M32 2 L32 38 M2 10 L38 10 M2 18 L38 18 M2 26 L38 26 M2 34 L38 34', latex: 'Trace', desc: 'Tabla de traza de ejecución' },
    { nombre: 'Pre/Post', svg: 'M2 2 L38 2 L38 38 L2 38 Z M20 2 L20 38 M2 10 L38 10 M2 20 L38 20 M2 30 L38 30', latex: 'Pre | Post', desc: 'Precondiciones y postcondiciones' },
    { nombre: 'Invariante', svg: 'M5 10 L35 10 L35 30 L5 30 Z M5 20 L35 20', latex: 'Invariant', desc: 'Invariante de bucle' }
  ];

  // 🔵 Árboles y Grafos - Nodos, aristas, estructuras
  const componentesGrafos = [
    { nombre: 'Nodo', svg: 'M20 20 m -15 0 a 15 15 0 1 0 30 0 a 15 15 0 1 0 -30 0', latex: 'n', desc: 'Nodo básico' },
    { nombre: 'Nodo Raíz', svg: 'M20 20 m -15 0 a 15 15 0 1 0 30 0 a 15 15 0 1 0 -30 0 M20 5 L20 10', latex: 'root', desc: 'Nodo raíz de árbol' },
    { nombre: 'Nodo Hoja', svg: 'M20 20 m -15 0 a 15 15 0 1 0 30 0 a 15 15 0 1 0 -30 0 M20 30 L20 35', latex: 'leaf', desc: 'Nodo hoja' },
    { nombre: 'Arista', svg: 'M5 20 L35 20', latex: '--', desc: 'Arista no dirigida' },
    { nombre: 'Arista Dirigida', svg: 'M5 20 L30 20 L25 15 M30 20 L25 25', latex: '->', desc: 'Arista dirigida' },
    { nombre: 'Arista Peso', svg: 'M5 20 L35 20 M20 12 L20 18', latex: '-5-', desc: 'Arista con peso' },
    { nombre: 'Árbol Binario', svg: 'M20 5 m -4 0 a 4 4 0 1 0 8 0 a 4 4 0 1 0 -8 0 M20 9 L15 18 M20 9 L25 18 M12 20 m -4 0 a 4 4 0 1 0 8 0 a 4 4 0 1 0 -8 0 M28 20 m -4 0 a 4 4 0 1 0 8 0 a 4 4 0 1 0 -8 0', latex: 'BST', desc: 'Árbol binario' },
    { nombre: 'Nivel', svg: 'M5 15 L35 15 M5 25 L35 25 M10 10 m -3 0 a 3 3 0 1 0 6 0 a 3 3 0 1 0 -6 0 M30 10 m -3 0 a 3 3 0 1 0 6 0 a 3 3 0 1 0 -6 0', latex: 'level', desc: 'Nivel de árbol' },
    { nombre: 'Grafo', svg: 'M10 10 m -5 0 a 5 5 0 1 0 10 0 a 5 5 0 1 0 -10 0 M30 10 m -5 0 a 5 5 0 1 0 10 0 a 5 5 0 1 0 -10 0 M10 30 m -5 0 a 5 5 0 1 0 10 0 a 5 5 0 1 0 -10 0 M30 30 m -5 0 a 5 5 0 1 0 10 0 a 5 5 0 1 0 -10 0 M15 10 L25 10 M10 15 L10 25 M30 15 L30 25 M15 30 L25 30', latex: 'G', desc: 'Grafo completo' },
    { nombre: 'Recorrido BFS', svg: 'M20 10 m -5 0 a 5 5 0 1 0 10 0 a 5 5 0 1 0 -10 0 M10 25 m -4 0 a 4 4 0 1 0 8 0 a 4 4 0 1 0 -8 0 M30 25 m -4 0 a 4 4 0 1 0 8 0 a 4 4 0 1 0 -8 0 M20 15 L15 21 M20 15 L25 21', latex: 'BFS', desc: 'Recorrido BFS' },
    { nombre: 'Recorrido DFS', svg: 'M20 8 m -4 0 a 4 4 0 1 0 8 0 a 4 4 0 1 0 -8 0 M20 12 L20 18 M20 22 m -4 0 a 4 4 0 1 0 8 0 a 4 4 0 1 0 -8 0 M20 26 L20 32 M20 36 m -3 0 a 3 3 0 1 0 6 0 a 3 3 0 1 0 -6 0', latex: 'DFS', desc: 'Recorrido DFS' },
    { nombre: 'Camino', svg: 'M8 20 m -3 0 a 3 3 0 1 0 6 0 a 3 3 0 1 0 -6 0 M32 20 m -3 0 a 3 3 0 1 0 6 0 a 3 3 0 1 0 -6 0 M11 20 L26 20 L22 16 M26 20 L22 24', latex: 'path', desc: 'Camino entre nodos' }
  ];

  // 🟠 Autómatas Finitos - Estados, transiciones
  const componentesAutomatas = [
    { nombre: 'Estado', svg: 'M20 20 m -15 0 a 15 15 0 1 0 30 0 a 15 15 0 1 0 -30 0', latex: 'q0', desc: 'Estado básico' },
    { nombre: 'Estado Inicial', svg: 'M20 20 m -15 0 a 15 15 0 1 0 30 0 a 15 15 0 1 0 -30 0 M2 20 L5 20 L5 18 M5 20 L5 22', latex: '→q0', desc: 'Estado inicial' },
    { nombre: 'Estado Aceptación', svg: 'M20 20 m -15 0 a 15 15 0 1 0 30 0 a 15 15 0 1 0 -30 0 M20 20 m -12 0 a 12 12 0 1 0 24 0 a 12 12 0 1 0 -24 0', latex: '((q))', desc: 'Estado de aceptación' },
    { nombre: 'Transición', svg: 'M5 20 L30 20 L25 15 M30 20 L25 25', latex: '--a-->', desc: 'Transición con símbolo' },
    { nombre: 'Transición Epsilon', svg: 'M5 20 L30 20 L25 15 M30 20 L25 25 M18 12 L22 12', latex: '--ε-->', desc: 'Transición epsilon' },
    { nombre: 'Transición Loop', svg: 'M20 5 C15 0, 25 0, 20 5 L18 8 M20 5 L22 8', latex: 'a', desc: 'Transición de bucle' },
    { nombre: 'Autómata AFD', svg: 'M10 20 m -6 0 a 6 6 0 1 0 12 0 a 6 6 0 1 0 -12 0 M30 20 m -6 0 a 6 6 0 1 0 12 0 a 6 6 0 1 0 -12 0 M30 20 m -4 0 a 4 4 0 1 0 8 0 a 4 4 0 1 0 -8 0 M16 20 L24 20 L22 18 M24 20 L22 22 M2 20 L4 20', latex: 'DFA', desc: 'Autómata finito determinista' },
    { nombre: 'Autómata AFN', svg: 'M8 15 m -4 0 a 4 4 0 1 0 8 0 a 4 4 0 1 0 -8 0 M8 25 m -4 0 a 4 4 0 1 0 8 0 a 4 4 0 1 0 -8 0 M32 20 m -6 0 a 6 6 0 1 0 12 0 a 6 6 0 1 0 -12 0 M32 20 m -4 0 a 4 4 0 1 0 8 0 a 4 4 0 1 0 -8 0 M12 15 L26 20 M12 25 L26 20', latex: 'NFA', desc: 'Autómata finito no determinista' },
    { nombre: 'Pila', svg: 'M15 8 L25 8 L25 12 L15 12 Z M15 14 L25 14 L25 18 L15 18 Z M15 20 L25 20 L25 24 L15 24 Z M15 26 L25 26 L25 30 L15 30 Z M15 32 L25 32 L25 36 L15 36 Z', latex: 'Stack', desc: 'Pila de autómata pushdown' },
    { nombre: 'Cinta', svg: 'M2 15 L38 15 L38 25 L2 25 Z M10 15 L10 25 M18 15 L18 25 M26 15 L26 25 M34 15 L34 25', latex: 'Tape', desc: 'Cinta de máquina de Turing' }
  ];

  const componentes = {
    uml: componentesUML,
    flujo: componentesFlujo,
    tablas: componentesTablas,
    grafos: componentesGrafos,
    automatas: componentesAutomatas
  };

  const tabs = [
    { id: 'uml', nombre: 'UML', icon: '🟣', color: '#a855f7' },
    { id: 'flujo', nombre: 'Flujo', icon: '🟡', color: '#eab308' },
    { id: 'tablas', nombre: 'Tablas', icon: '🟩', color: '#22c55e' },
    { id: 'grafos', nombre: 'Grafos', icon: '🔵', color: '#3b82f6' },
    { id: 'automatas', nombre: 'Autómatas', icon: '🟠', color: '#f97316' }
  ];

  return (
    <div style={{
      background: 'rgba(139, 92, 246, 0.05)',
      borderRadius: '12px',
      padding: '1rem',
      border: '1px solid rgba(139, 92, 246, 0.2)'
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
              background: tabActiva === tab.id ? tab.color : 'rgba(139, 92, 246, 0.1)',
              color: tabActiva === tab.id ? 'white' : '#c4b5fd',
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
        gridTemplateColumns: 'repeat(auto-fill, minmax(110px, 1fr))',
        gap: '0.75rem',
        maxHeight: '350px',
        overflowY: 'auto',
        padding: '0.5rem'
      }}>
        {componentes[tabActiva].map((comp, idx) => (
          <button
            type="button"
            key={idx}
            onClick={() => onInsertComponent(comp)}
            style={{
              padding: '0.75rem',
              background: 'rgba(139, 92, 246, 0.1)',
              border: '1px solid rgba(139, 92, 246, 0.3)',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.2s',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '0.5rem'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(139, 92, 246, 0.2)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(139, 92, 246, 0.1)';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            {/* Preview SVG */}
            <svg width="40" height="40" viewBox="0 0 40 40" style={{ flexShrink: 0 }}>
              <path
                d={comp.svg}
                stroke="#c4b5fd"
                strokeWidth="2"
                fill={comp.fill ? '#8b5cf6' : 'none'}
              />
            </svg>
            
            {/* Nombre */}
            <span style={{
              fontSize: '0.75rem',
              color: '#e9d5ff',
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
        background: 'rgba(139, 92, 246, 0.08)',
        borderRadius: '6px',
        fontSize: '0.8rem',
        color: '#ddd6fe',
        lineHeight: '1.5'
      }}>
        <strong style={{color: '#e9d5ff'}}>💡 Categoría {tabs.find(t => t.id === tabActiva)?.nombre}:</strong> {
          tabActiva === 'uml' ? 'Clases, interfaces, relaciones UML' :
          tabActiva === 'flujo' ? 'Formas estándar de diagramas de flujo' :
          tabActiva === 'tablas' ? 'Estructuras tabulares para algoritmos' :
          tabActiva === 'grafos' ? 'Nodos, aristas, árboles binarios, grafos' :
          'Estados, transiciones, autómatas finitos'
        }
      </div>
    </div>
  );
};

export default ProgrammingToolbar;
