"""
🔍 MÓDULO 1: Detector de Errores por Pregunta
==============================================

Este módulo analiza los resultados de exámenes completados y clasifica
cada pregunta según el desempeño del usuario en:
- acierto
- fallo  
- respuesta_debil

Compatible con el sistema Examinator sin romper funcionalidad existente.
"""

from typing import Dict, List, Literal
from pathlib import Path
import json

# Tipos de estado posibles para una respuesta
EstadoRespuesta = Literal["acierto", "fallo", "respuesta_debil"]

# Tipos de pregunta soportados por el sistema
TiposPreguntaObjetivos = ["multiple", "verdadero_falso", "flashcard"]
TiposPreguntaSubjetivos = ["corta", "desarrollo"]


class ResultadoPreguntaExtendido:
    """
    Estructura extendida de una pregunta evaluada con clasificación de estado.
    
    Esta clase NO modifica los JSON existentes, sino que agrega información
    adicional para análisis de patrones de error.
    """
    
    def __init__(self, pregunta_data: Dict):
        """
        Inicializa desde un resultado de pregunta del JSON de examen.
        
        Args:
            pregunta_data: Diccionario con los datos de una pregunta evaluada
        """
        # Campos originales del sistema
        self.id_pregunta = pregunta_data.get("id_pregunta", None)  # Puede no existir en versiones antiguas
        self.pregunta = pregunta_data["pregunta"]
        self.tipo = pregunta_data["tipo"]
        self.opciones = pregunta_data.get("opciones", [])
        self.respuesta_usuario = pregunta_data["respuesta_usuario"]
        self.respuesta_correcta = pregunta_data.get("respuesta_correcta", None)
        self.puntos = pregunta_data["puntos"]
        self.puntos_maximos = pregunta_data["puntos_maximos"]
        self.feedback = pregunta_data.get("feedback", "")
        
        # Campo NUEVO: clasificación del estado de la respuesta
        self.estado_respuesta: EstadoRespuesta = self._clasificar_respuesta()
    
    def _clasificar_respuesta(self) -> EstadoRespuesta:
        """
        Clasifica el estado de la respuesta según el tipo de pregunta y puntuación.
        
        Reglas de clasificación:
        
        PREGUNTAS OBJETIVAS (multiple, verdadero_falso, flashcard):
        - Compara respuesta_usuario == respuesta_correcta (cuando disponible)
        - Si no hay respuesta_correcta: usa ratio de puntos
        
        PREGUNTAS SUBJETIVAS (corta, desarrollo):
        - Usa ratio: puntos / puntos_maximos
        - < 0.7 → fallo
        - 0.7 - 0.89 → respuesta_debil  
        - >= 0.9 → acierto
        
        Returns:
            "acierto" | "fallo" | "respuesta_debil"
        """
        # Calcular ratio de puntuación
        if self.puntos_maximos == 0:
            ratio = 0.0
        else:
            ratio = self.puntos / self.puntos_maximos
        
        # CASO 1: Preguntas objetivas (comparación directa)
        if self.tipo in TiposPreguntaObjetivos:
            # Intentar comparación directa si existe respuesta_correcta
            if self.respuesta_correcta is not None:
                # Normalizar respuestas para comparación
                resp_usuario = str(self.respuesta_usuario).strip().lower()
                resp_correcta = str(self.respuesta_correcta).strip().lower()
                
                if resp_usuario == resp_correcta:
                    return "acierto"
                else:
                    return "fallo"
            
            # Fallback: usar ratio si no hay respuesta_correcta
            # (puede ocurrir en verdadero_falso o flashcards evaluadas por IA)
            if ratio >= 0.9:
                return "acierto"
            elif ratio >= 0.7:
                return "respuesta_debil"
            else:
                return "fallo"
        
        # CASO 2: Preguntas subjetivas (basado en ratio)
        elif self.tipo in TiposPreguntaSubjetivos:
            if ratio >= 0.9:
                return "acierto"
            elif ratio >= 0.7:
                return "respuesta_debil"
            else:
                return "fallo"
        
        # CASO 3: Tipo desconocido (usar ratio conservador)
        else:
            if ratio >= 0.9:
                return "acierto"
            elif ratio >= 0.7:
                return "respuesta_debil"
            else:
                return "fallo"
    
    def to_dict(self) -> Dict:
        """
        Convierte a diccionario con todos los campos (originales + nuevo).
        
        Returns:
            Diccionario con estructura extendida para análisis
        """
        return {
            "id_pregunta": self.id_pregunta,
            "pregunta": self.pregunta,
            "tipo": self.tipo,
            "opciones": self.opciones,
            "respuesta_usuario": self.respuesta_usuario,
            "respuesta_correcta": self.respuesta_correcta,
            "puntos": self.puntos,
            "puntos_maximos": self.puntos_maximos,
            "feedback": self.feedback,
            "estado_respuesta": self.estado_respuesta  # ← CAMPO NUEVO
        }


class DetectorErrores:
    """
    Analizador de exámenes completados para detección de patrones de error.
    
    Funcionalidades:
    - Leer JSONs de exámenes completados
    - Clasificar cada pregunta por estado de respuesta
    - Generar reportes de análisis
    - Mantener compatibilidad con el sistema existente
    """
    
    def analizar_examen(self, ruta_json_examen: str) -> Dict:
        """
        Analiza un examen completado y clasifica cada pregunta.
        
        Args:
            ruta_json_examen: Ruta al archivo JSON del examen completado
                             (ej: "examenes/Platzi/examen_20251120_134728.json")
        
        Returns:
            Diccionario con:
            {
                "metadata": {
                    "id": "20251120_134728",
                    "carpeta": "Platzi",
                    "fecha_completado": "2025-11-20T13:47:28",
                    "puntos_obtenidos": 1.0,
                    "puntos_totales": 2,
                    "porcentaje": 50.0
                },
                "resultados_clasificados": [
                    {
                        "pregunta": "...",
                        "tipo": "flashcard",
                        "puntos": 0.5,
                        "puntos_maximos": 1,
                        "estado_respuesta": "fallo",  # ← NUEVO
                        ... (todos los campos originales)
                    },
                    ...
                ],
                "resumen_estados": {
                    "total_preguntas": 2,
                    "aciertos": 0,
                    "fallos": 2,
                    "respuestas_debiles": 0,
                    "porcentaje_aciertos": 0.0,
                    "porcentaje_fallos": 100.0,
                    "porcentaje_debiles": 0.0
                }
            }
        
        Raises:
            FileNotFoundError: Si no existe el archivo JSON
            json.JSONDecodeError: Si el JSON está malformado
            KeyError: Si faltan campos requeridos en el JSON
        """
        # Leer archivo JSON
        ruta = Path(ruta_json_examen)
        if not ruta.exists():
            raise FileNotFoundError(f"No se encontró el examen: {ruta_json_examen}")
        
        with open(ruta, 'r', encoding='utf-8') as f:
            datos_examen = json.load(f)
        
        # Validar que sea un examen completado
        if datos_examen.get("tipo") != "completado":
            raise ValueError(f"El examen no está completado (tipo: {datos_examen.get('tipo')})")
        
        # Extraer metadata
        metadata = {
            "id": datos_examen["id"],
            "carpeta": datos_examen.get("carpeta_nombre", ""),
            "carpeta_ruta": datos_examen.get("carpeta_ruta", ""),
            "fecha_completado": datos_examen["fecha_completado"],
            "puntos_obtenidos": datos_examen["puntos_obtenidos"],
            "puntos_totales": datos_examen["puntos_totales"],
            "porcentaje": datos_examen["porcentaje"]
        }
        
        # Procesar cada pregunta
        resultados_clasificados = []
        for pregunta_data in datos_examen["resultados"]:
            pregunta_extendida = ResultadoPreguntaExtendido(pregunta_data)
            resultados_clasificados.append(pregunta_extendida.to_dict())
        
        # Calcular resumen de estados
        total = len(resultados_clasificados)
        aciertos = sum(1 for r in resultados_clasificados if r["estado_respuesta"] == "acierto")
        fallos = sum(1 for r in resultados_clasificados if r["estado_respuesta"] == "fallo")
        debiles = sum(1 for r in resultados_clasificados if r["estado_respuesta"] == "respuesta_debil")
        
        resumen_estados = {
            "total_preguntas": total,
            "aciertos": aciertos,
            "fallos": fallos,
            "respuestas_debiles": debiles,
            "porcentaje_aciertos": round((aciertos / total * 100) if total > 0 else 0, 2),
            "porcentaje_fallos": round((fallos / total * 100) if total > 0 else 0, 2),
            "porcentaje_debiles": round((debiles / total * 100) if total > 0 else 0, 2)
        }
        
        return {
            "metadata": metadata,
            "resultados_clasificados": resultados_clasificados,
            "resumen_estados": resumen_estados
        }
    
    def analizar_multiples_examenes(self, rutas_json: List[str]) -> List[Dict]:
        """
        Analiza múltiples exámenes y retorna lista de resultados clasificados.
        
        Args:
            rutas_json: Lista de rutas a archivos JSON de exámenes
        
        Returns:
            Lista de diccionarios con análisis de cada examen
        """
        resultados = []
        for ruta in rutas_json:
            try:
                analisis = self.analizar_examen(ruta)
                resultados.append(analisis)
            except Exception as e:
                print(f"❌ Error analizando {ruta}: {e}")
                continue
        
        return resultados
    
    def filtrar_por_estado(
        self, 
        resultados_clasificados: List[Dict], 
        estado: EstadoRespuesta
    ) -> List[Dict]:
        """
        Filtra preguntas por estado de respuesta.
        
        Args:
            resultados_clasificados: Lista de preguntas clasificadas
            estado: "acierto" | "fallo" | "respuesta_debil"
        
        Returns:
            Lista filtrada de preguntas con el estado especificado
        """
        return [
            r for r in resultados_clasificados 
            if r["estado_respuesta"] == estado
        ]
    
    def generar_reporte_texto(self, analisis: Dict) -> str:
        """
        Genera un reporte en texto plano del análisis.
        
        Args:
            analisis: Resultado de analizar_examen()
        
        Returns:
            String con reporte formateado
        """
        metadata = analisis["metadata"]
        resumen = analisis["resumen_estados"]
        
        reporte = f"""
╔══════════════════════════════════════════════════════════════╗
║          REPORTE DE ANÁLISIS DE ERRORES - EXAMINATOR        ║
╚══════════════════════════════════════════════════════════════╝

📋 INFORMACIÓN DEL EXAMEN
  • ID: {metadata['id']}
  • Carpeta: {metadata['carpeta']}
  • Fecha: {metadata['fecha_completado']}
  • Puntuación: {metadata['puntos_obtenidos']}/{metadata['puntos_totales']} ({metadata['porcentaje']:.1f}%)

📊 RESUMEN DE ESTADOS
  • Total preguntas: {resumen['total_preguntas']}
  • ✅ Aciertos: {resumen['aciertos']} ({resumen['porcentaje_aciertos']}%)
  • ⚠️  Respuestas débiles: {resumen['respuestas_debiles']} ({resumen['porcentaje_debiles']}%)
  • ❌ Fallos: {resumen['fallos']} ({resumen['porcentaje_fallos']}%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 DETALLE POR PREGUNTA:
"""
        
        for i, resultado in enumerate(analisis["resultados_clasificados"], 1):
            emoji_estado = {
                "acierto": "✅",
                "respuesta_debil": "⚠️",
                "fallo": "❌"
            }[resultado["estado_respuesta"]]
            
            reporte += f"""
{i}. {emoji_estado} [{resultado['tipo'].upper()}] {resultado['estado_respuesta'].upper()}
   Pregunta: {resultado['pregunta'][:80]}{'...' if len(resultado['pregunta']) > 80 else ''}
   Puntuación: {resultado['puntos']}/{resultado['puntos_maximos']}
   Tu respuesta: {str(resultado['respuesta_usuario'])[:60]}{'...' if len(str(resultado['respuesta_usuario'])) > 60 else ''}
"""
        
        return reporte


# ═══════════════════════════════════════════════════════════════
# EJEMPLO DE USO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    Ejemplo de uso del detector de errores.
    
    Este código NO se ejecuta automáticamente en el sistema,
    solo sirve como demostración de cómo usar el módulo.
    """
    
    # Inicializar detector
    detector = DetectorErrores()
    
    # Analizar un examen
    try:
        analisis = detector.analizar_examen(
            "examenes/Platzi/examen_20251120_134728.json"
        )
        
        # Mostrar reporte
        print(detector.generar_reporte_texto(analisis))
        
        # Filtrar solo fallos
        fallos = detector.filtrar_por_estado(
            analisis["resultados_clasificados"], 
            "fallo"
        )
        
        print(f"\n🔴 Se detectaron {len(fallos)} fallos en este examen")
        
        # Guardar análisis extendido (opcional)
        import json
        with open("analisis_examen.json", "w", encoding="utf-8") as f:
            json.dump(analisis, f, indent=2, ensure_ascii=False)
        
        print("✅ Análisis guardado en: analisis_examen.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")
