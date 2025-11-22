"""
🎯 MÓDULO 3: Priorizador de Errores para Sesiones de Estudio
=============================================================

Motor de recomendaciones inteligente que selecciona qué errores debe
practicar el usuario basándose en criterios pedagógicos optimizados.

Funcionalidades:
- Priorización multi-criterio (estado, frecuencia, antigüedad)
- Aplicación del "Spacing Effect" pedagógico
- Recomendaciones personalizadas de estudio
- Razones transparentes de selección
- Integración con sesiones de práctica

Compatible con Módulo 2 (Banco de Errores) del sistema Examinator.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json

from banco_errores import BancoErrores


class Priorizador:
    """
    Motor de priorización inteligente de errores para sesiones de estudio.
    
    Aplica un algoritmo multi-criterio basado en:
    1. Estado de refuerzo (nuevos primero)
    2. Frecuencia de fallos (≥2 fallos)
    3. Días sin práctica (spacing effect)
    4. Prioridad calculada del banco
    """
    
    def __init__(self):
        """Inicializa el priorizador con acceso al banco de errores."""
        self.banco = BancoErrores()
    
    def obtener_errores_para_hoy(
        self,
        max_errores: int = 10,
        fecha_hoy: Optional[datetime] = None,
        incluir_resueltos: bool = False,
        solo_tipo: Optional[str] = None,
        solo_carpeta: Optional[str] = None
    ) -> Dict:
        """
        Selecciona y prioriza errores para la sesión de estudio de hoy.
        
        Este es el punto de entrada principal del módulo. Se debe llamar
        cuando el usuario inicia una sesión de estudio o práctica.
        
        Args:
            max_errores: Número máximo de errores a retornar (default: 10)
            fecha_hoy: Fecha de referencia (default: datetime.now())
            incluir_resueltos: Si True, incluye errores resueltos para repaso
            solo_tipo: Filtrar por tipo de pregunta ("multiple", "corta", etc.)
            solo_carpeta: Filtrar por carpeta específica (ej: "Matematicas")
        
        Returns:
            Diccionario con:
            {
                "fecha_sesion": str,
                "total_errores_seleccionados": int,
                "errores": List[Dict],
                "estadisticas_sesion": Dict,
                "mensaje_motivacional": str
            }
        
        Raises:
            ValueError: Si max_errores <= 0
        """
        
        if max_errores <= 0:
            raise ValueError("max_errores debe ser mayor que 0")
        
        if fecha_hoy is None:
            fecha_hoy = datetime.now()
        
        print(f"🎯 Priorizando errores para sesión de estudio...")
        print(f"   Fecha: {fecha_hoy.strftime('%Y-%m-%d')}")
        print(f"   Max errores: {max_errores}\n")
        
        # PASO 1: Cargar banco de errores
        banco_data = self.banco._cargar_banco()
        errores_disponibles = banco_data["errores"]
        
        if not errores_disponibles:
            return self._respuesta_banco_vacio()
        
        # PASO 2: Filtrar errores según criterios
        errores_filtrados = self._filtrar_errores(
            errores_disponibles,
            incluir_resueltos,
            solo_tipo,
            solo_carpeta
        )
        
        if not errores_filtrados:
            return self._respuesta_sin_errores_disponibles(incluir_resueltos)
        
        # PASO 3: Calcular métricas para cada error
        errores_con_metricas = self._calcular_metricas(
            errores_filtrados,
            fecha_hoy
        )
        
        # PASO 4: Aplicar algoritmo de priorización
        errores_priorizados = self._priorizar_errores(errores_con_metricas)
        
        # PASO 5: Limitar a N errores
        errores_seleccionados = errores_priorizados[:max_errores]
        
        # PASO 6: Enriquecer con metadatos pedagógicos
        errores_enriquecidos = self._enriquecer_errores(errores_seleccionados)
        
        # PASO 7: Generar estadísticas de la sesión
        estadisticas = self._calcular_estadisticas_sesion(errores_enriquecidos)
        
        # PASO 8: Generar mensaje motivacional
        mensaje = self._generar_mensaje_motivacional(
            len(errores_enriquecidos),
            estadisticas
        )
        
        print(f"✅ {len(errores_enriquecidos)} errores priorizados para hoy\n")
        
        return {
            "fecha_sesion": fecha_hoy.isoformat(),
            "total_errores_seleccionados": len(errores_enriquecidos),
            "errores": errores_enriquecidos,
            "estadisticas_sesion": estadisticas,
            "mensaje_motivacional": mensaje
        }
    
    def _filtrar_errores(
        self,
        errores: List[Dict],
        incluir_resueltos: bool,
        solo_tipo: Optional[str],
        solo_carpeta: Optional[str]
    ) -> List[Dict]:
        """
        Filtra errores según criterios especificados.
        
        Args:
            errores: Lista de errores del banco
            incluir_resueltos: Si incluir errores resueltos
            solo_tipo: Tipo de pregunta específico
            solo_carpeta: Carpeta específica
        
        Returns:
            Lista filtrada de errores
        """
        errores_filtrados = errores.copy()
        
        # Filtro 1: Estado de refuerzo
        if not incluir_resueltos:
            errores_filtrados = [
                e for e in errores_filtrados
                if e["estado_refuerzo"] in ["nuevo_error", "en_refuerzo"]
            ]
        
        # Filtro 2: Tipo de pregunta
        if solo_tipo:
            errores_filtrados = [
                e for e in errores_filtrados
                if e["pregunta"]["tipo"] == solo_tipo
            ]
        
        # Filtro 3: Carpeta
        if solo_carpeta:
            errores_filtrados = [
                e for e in errores_filtrados
                if solo_carpeta in e["examen_origen"]["carpeta_ruta"]
            ]
        
        return errores_filtrados
    
    def _calcular_metricas(
        self,
        errores: List[Dict],
        fecha_hoy: datetime
    ) -> List[Dict]:
        """
        Calcula métricas adicionales para cada error.
        
        Args:
            errores: Lista de errores
            fecha_hoy: Fecha de referencia
        
        Returns:
            Lista de errores con métricas añadidas
        """
        for error in errores:
            # Calcular días sin práctica
            ultima_practica = datetime.fromisoformat(
                error["ultima_vez_practicada"]
            )
            dias_sin_practica = (fecha_hoy - ultima_practica).days
            error["dias_sin_practica"] = max(0, dias_sin_practica)
            
            # Calcular puntuación compuesta de prioridad
            error["puntuacion_prioridad"] = self._calcular_puntuacion(error)
            
            # Extraer último intento del historial
            if error["historial_respuestas"]:
                error["ultimo_intento"] = error["historial_respuestas"][-1]
            else:
                error["ultimo_intento"] = None
        
        return errores
    
    def _calcular_puntuacion(self, error: Dict) -> int:
        """
        Calcula puntuación compuesta de prioridad pedagógica.
        
        Factores considerados:
        - Estado de refuerzo (nuevo = más urgente)
        - Frecuencia de fallos (más fallos = más importante)
        - Días sin práctica (spacing effect)
        - Prioridad del banco
        
        Args:
            error: Diccionario del error
        
        Returns:
            Puntuación numérica (mayor = más prioritario)
        """
        puntuacion = 0
        
        # Factor 1: Estado de refuerzo (peso más alto)
        if error["estado_refuerzo"] == "nuevo_error":
            puntuacion += 100  # Máxima prioridad
        elif error["estado_refuerzo"] == "en_refuerzo":
            puntuacion += 50
        else:  # resuelto
            puntuacion += 10
        
        # Factor 2: Frecuencia de fallos
        puntuacion += error["veces_fallada"] * 10
        
        # Factor 3: Días sin práctica (spacing effect)
        # Más días = más urgente practicar
        puntuacion += min(error["dias_sin_practica"] * 2, 60)  # Cap en 60
        
        # Factor 4: Prioridad del banco
        if error["prioridad"] == "alta":
            puntuacion += 30
        elif error["prioridad"] == "media":
            puntuacion += 15
        else:  # baja
            puntuacion += 5
        
        return puntuacion
    
    def _priorizar_errores(self, errores: List[Dict]) -> List[Dict]:
        """
        Aplica algoritmo de priorización multi-criterio.
        
        Criterios en orden de importancia:
        1. Estado == "nuevo_error" (primero)
        2. Veces fallada >= 2 (luego)
        3. Días sin práctica (descendente)
        4. Prioridad del banco (alta → media → baja)
        
        Args:
            errores: Lista de errores con métricas calculadas
        
        Returns:
            Lista ordenada de errores
        """
        
        # Mapeo de valores para ordenamiento
        estado_orden = {
            "nuevo_error": 0,    # Primero
            "en_refuerzo": 1,    # Segundo
            "resuelto": 2        # Último
        }
        
        prioridad_orden = {
            "alta": 0,
            "media": 1,
            "baja": 2
        }
        
        # Ordenamiento multi-criterio
        errores_ordenados = sorted(
            errores,
            key=lambda e: (
                estado_orden[e["estado_refuerzo"]],        # Criterio 1
                0 if e["veces_fallada"] >= 2 else 1,       # Criterio 2 (inverso)
                -e["dias_sin_practica"],                    # Criterio 3 (descendente)
                prioridad_orden[e["prioridad"]]             # Criterio 4
            )
        )
        
        return errores_ordenados
    
    def _enriquecer_errores(self, errores: List[Dict]) -> List[Dict]:
        """
        Enriquece errores con metadatos pedagógicos.
        
        Agrega:
        - razon_seleccion: Por qué se seleccionó este error
        - recomendacion_estudio: Estrategia de estudio sugerida
        
        Args:
            errores: Lista de errores priorizados
        
        Returns:
            Lista de errores enriquecidos
        """
        for error in errores:
            error["razon_seleccion"] = self._generar_razon_seleccion(error)
            error["recomendacion_estudio"] = self._generar_recomendacion(error)
        
        return errores
    
    def _generar_razon_seleccion(self, error: Dict) -> str:
        """
        Genera explicación de por qué se seleccionó este error.
        
        Args:
            error: Diccionario del error
        
        Returns:
            String con razones separadas por " | "
        """
        razones = []
        
        # Razón 1: Estado de refuerzo
        if error["estado_refuerzo"] == "nuevo_error":
            razones.append("⚠️ Error nuevo - atención inmediata")
        elif error["estado_refuerzo"] == "en_refuerzo":
            razones.append("🔄 En proceso de refuerzo")
        
        # Razón 2: Frecuencia de fallos
        if error["veces_fallada"] >= 3:
            razones.append(f"🔴 Fallada {error['veces_fallada']} veces - concepto difícil")
        elif error["veces_fallada"] >= 2:
            razones.append(f"🟡 Fallada {error['veces_fallada']} veces - necesita refuerzo")
        
        # Razón 3: Antigüedad sin práctica
        dias = error["dias_sin_practica"]
        if dias > 14:
            razones.append(f"📅 {dias} días sin practicar - riesgo alto de olvido")
        elif dias > 7:
            razones.append(f"📅 {dias} días sin practicar - refrescar concepto")
        elif dias > 3:
            razones.append(f"📅 {dias} días sin practicar - momento óptimo")
        
        # Razón 4: Prioridad
        if error["prioridad"] == "alta":
            razones.append("🎯 Alta prioridad")
        
        return " | ".join(razones) if razones else "📚 Práctica de refuerzo"
    
    def _generar_recomendacion(self, error: Dict) -> str:
        """
        Genera recomendación de estrategia de estudio.
        
        Args:
            error: Diccionario del error
        
        Returns:
            String con recomendación personalizada
        """
        # Casos especiales primero
        if error["veces_fallada"] >= 3:
            return "💡 Dedica tiempo extra a entender el concepto fundamental. Busca recursos adicionales."
        
        if error["estado_refuerzo"] == "nuevo_error":
            return "📖 Estudia la teoría relacionada antes de intentar resolver de nuevo."
        
        if error["dias_sin_practica"] > 14:
            return "📝 Revisa tus apuntes o la documentación antes de responder."
        
        if error["dias_sin_practica"] > 7:
            return "🔍 Lee la pregunta con atención y recuerda los conceptos clave."
        
        # Recomendación por defecto
        return "✍️ Practica con atención a los detalles. ¡Tú puedes!"
    
    def _calcular_estadisticas_sesion(self, errores: List[Dict]) -> Dict:
        """
        Calcula estadísticas agregadas de la sesión.
        
        Args:
            errores: Lista de errores seleccionados
        
        Returns:
            Diccionario con estadísticas
        """
        if not errores:
            return {
                "errores_nuevos_incluidos": 0,
                "errores_alta_frecuencia": 0,
                "errores_antiguos": 0,
                "promedio_dias_sin_practica": 0,
                "tipos_pregunta": {}
            }
        
        # Contar por categorías
        nuevos = sum(1 for e in errores if e["estado_refuerzo"] == "nuevo_error")
        alta_frecuencia = sum(1 for e in errores if e["veces_fallada"] >= 3)
        antiguos = sum(1 for e in errores if e["dias_sin_practica"] > 7)
        
        # Promedio de días sin práctica
        total_dias = sum(e["dias_sin_practica"] for e in errores)
        promedio_dias = round(total_dias / len(errores), 1)
        
        # Contar tipos de pregunta
        tipos = {}
        for error in errores:
            tipo = error["pregunta"]["tipo"]
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        return {
            "errores_nuevos_incluidos": nuevos,
            "errores_alta_frecuencia": alta_frecuencia,
            "errores_antiguos": antiguos,
            "promedio_dias_sin_practica": promedio_dias,
            "tipos_pregunta": tipos
        }
    
    def _generar_mensaje_motivacional(
        self,
        total_errores: int,
        estadisticas: Dict
    ) -> str:
        """
        Genera mensaje motivacional contextual.
        
        Args:
            total_errores: Número de errores seleccionados
            estadisticas: Estadísticas de la sesión
        
        Returns:
            String con mensaje motivacional
        """
        if total_errores == 0:
            return "🎉 ¡No tienes errores pendientes! Sigue así."
        
        # Mensajes según características de la sesión
        if estadisticas["errores_nuevos_incluidos"] >= 3:
            return f"🚀 Hoy dominarás {total_errores} conceptos nuevos. ¡Vamos a ello! 💪"
        
        if estadisticas["errores_alta_frecuencia"] >= 2:
            return f"🎯 Sesión intensiva: {estadisticas['errores_alta_frecuencia']} conceptos difíciles. ¡Puedes con esto! 💡"
        
        if estadisticas["promedio_dias_sin_practica"] > 10:
            return f"📚 Tiempo de refrescar conceptos. {total_errores} preguntas te esperan. ¡A por ellas! ✨"
        
        # Mensaje por defecto
        return f"💪 Hoy practicarás {total_errores} conceptos. ¡Cada práctica te acerca a la maestría! 🎓"
    
    def _respuesta_banco_vacio(self) -> Dict:
        """Respuesta cuando el banco está vacío."""
        return {
            "fecha_sesion": datetime.now().isoformat(),
            "total_errores_seleccionados": 0,
            "errores": [],
            "estadisticas_sesion": {},
            "mensaje_motivacional": "🎉 ¡No tienes errores pendientes! Continúa con nuevos temas."
        }
    
    def _respuesta_sin_errores_disponibles(self, incluir_resueltos: bool) -> Dict:
        """Respuesta cuando no hay errores que cumplan los filtros."""
        if incluir_resueltos:
            mensaje = "🎊 ¡Has resuelto todos tus errores! Sigue practicando para mantener el nivel."
        else:
            mensaje = "✅ No tienes errores activos. ¡Todos están resueltos o en pausa!"
        
        return {
            "fecha_sesion": datetime.now().isoformat(),
            "total_errores_seleccionados": 0,
            "errores": [],
            "estadisticas_sesion": {},
            "mensaje_motivacional": mensaje
        }
    
    def generar_reporte_priorizacion(
        self,
        resultado_priorizacion: Dict
    ) -> str:
        """
        Genera reporte en texto plano de la priorización.
        
        Args:
            resultado_priorizacion: Resultado de obtener_errores_para_hoy()
        
        Returns:
            String con reporte formateado
        """
        errores = resultado_priorizacion["errores"]
        stats = resultado_priorizacion["estadisticas_sesion"]
        
        reporte = f"""
╔══════════════════════════════════════════════════════════════╗
║           SESIÓN DE ESTUDIO PRIORIZADA - HOY                ║
╚══════════════════════════════════════════════════════════════╝

📅 Fecha: {datetime.fromisoformat(resultado_priorizacion['fecha_sesion']).strftime('%Y-%m-%d')}
🎯 Errores seleccionados: {resultado_priorizacion['total_errores_seleccionados']}

💬 {resultado_priorizacion['mensaje_motivacional']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 COMPOSICIÓN DE LA SESIÓN
  • ⚠️  Errores nuevos: {stats.get('errores_nuevos_incluidos', 0)}
  • 🔴 Alta frecuencia (≥3 fallos): {stats.get('errores_alta_frecuencia', 0)}
  • 📅 Antiguos (>7 días): {stats.get('errores_antiguos', 0)}
  • ⏱️  Promedio días sin práctica: {stats.get('promedio_dias_sin_practica', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎓 ERRORES A PRACTICAR HOY:
"""
        
        for i, error in enumerate(errores, 1):
            reporte += f"""
{i}. [{error['pregunta']['tipo'].upper()}] {error['pregunta']['texto'][:60]}...
   
   📍 {error['razon_seleccion']}
   💡 {error['recomendacion_estudio']}
   
   📊 Métricas:
      • Veces fallada: {error['veces_fallada']}
      • Días sin práctica: {error['dias_sin_practica']}
      • Estado: {error['estado_refuerzo']}
      • Prioridad: {error['prioridad']}
   
   📚 Origen: {error['examen_origen']['carpeta_ruta']}
"""
        
        return reporte


# ═══════════════════════════════════════════════════════════════
# EJEMPLO DE USO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    Ejemplo de uso del priorizador de errores.
    """
    
    print("=" * 70)
    print("🎯 EJEMPLO: Priorizador de Errores para Sesión de Estudio")
    print("=" * 70 + "\n")
    
    priorizador = Priorizador()
    
    try:
        # Obtener errores priorizados para hoy
        resultado = priorizador.obtener_errores_para_hoy(
            max_errores=10
        )
        
        # Generar y mostrar reporte
        reporte = priorizador.generar_reporte_priorizacion(resultado)
        print(reporte)
        
        # Guardar resultado (opcional)
        output_file = "sesion_estudio_hoy.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Sesión guardada en: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
