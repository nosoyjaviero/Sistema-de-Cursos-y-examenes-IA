"""
🏦 MÓDULO 2: Banco de Errores (Error Bank)
==========================================

Sistema de almacenamiento y seguimiento de preguntas falladas o respondidas
débilmente para refuerzo personalizado.

Funcionalidades:
- Almacenar errores de todos los exámenes
- Detectar preguntas duplicadas (mismo error en múltiples exámenes)
- Rastrear progreso de mejora con historial
- Calcular prioridad y estado de refuerzo automáticamente
- Generar estadísticas agregadas

Compatible con Módulo 1 (Detector de Errores) del sistema Examinator.
"""

from typing import Dict, List, Literal, Optional
from pathlib import Path
from datetime import datetime
import json
import hashlib
import uuid

from detector_errores import DetectorErrores

# Tipos de estado de refuerzo
EstadoRefuerzo = Literal["nuevo_error", "en_refuerzo", "resuelto"]
Prioridad = Literal["alta", "media", "baja"]


class BancoErrores:
    """
    Gestor del banco centralizado de errores para refuerzo personalizado.
    
    El banco almacena todas las preguntas falladas o respondidas débilmente,
    con seguimiento completo de intentos, progreso y priorización automática.
    """
    
    RUTA_BANCO = Path("examenes/error_bank/banco_errores_global.json")
    RUTA_ESTADISTICAS = Path("examenes/error_bank/estadisticas_resumen.json")
    VERSION_BANCO = "2.0"
    
    def __init__(self):
        """Inicializa el gestor del banco de errores."""
        self.detector = DetectorErrores()
        self._asegurar_directorios()
    
    def _asegurar_directorios(self):
        """Crea los directorios necesarios si no existen."""
        self.RUTA_BANCO.parent.mkdir(parents=True, exist_ok=True)
    
    def actualizar_banco_desde_examen(self, ruta_examen: str) -> Dict:
        """
        Actualiza el banco de errores después de completar un examen.
        
        Este es el punto de entrada principal del módulo. Se debe llamar
        automáticamente después de que un usuario complete un examen.
        
        Args:
            ruta_examen: Ruta al JSON del examen completado
        
        Returns:
            Diccionario con resumen de la actualización:
            {
                "mensaje": str,
                "nuevos": int,
                "actualizados": int,
                "total_banco": int,
                "errores_activos": int,
                "errores_resueltos": int
            }
        
        Raises:
            FileNotFoundError: Si no existe el archivo del examen
            ValueError: Si el examen no está completado
        """
        
        # PASO 1: Analizar examen con Detector de Errores (Módulo 1)
        print(f"📊 Analizando examen: {Path(ruta_examen).name}")
        analisis = self.detector.analizar_examen(ruta_examen)
        
        # PASO 2: Filtrar solo errores y respuestas débiles
        errores_a_procesar = [
            pregunta for pregunta in analisis["resultados_clasificados"]
            if pregunta["estado_respuesta"] in ["fallo", "respuesta_debil"]
        ]
        
        if not errores_a_procesar:
            return {
                "mensaje": "✅ No hay errores que agregar al banco",
                "nuevos": 0,
                "actualizados": 0,
                "total_banco": self._contar_errores_en_banco(),
                "errores_activos": 0,
                "errores_resueltos": 0
            }
        
        print(f"🔍 Encontrados {len(errores_a_procesar)} errores para procesar")
        
        # PASO 3: Cargar banco existente
        banco = self._cargar_banco()
        
        # PASO 4: Procesar cada error
        contador_nuevos = 0
        contador_actualizados = 0
        
        for error in errores_a_procesar:
            hash_pregunta = self._calcular_hash_pregunta(error["pregunta"])
            error_existente = self._buscar_por_hash(banco["errores"], hash_pregunta)
            
            if error_existente:
                # Actualizar error existente
                self._actualizar_error_existente(
                    error_existente,
                    error,
                    analisis["metadata"]
                )
                contador_actualizados += 1
                print(f"  🔄 Actualizado: {error['pregunta'][:50]}...")
            else:
                # Crear nuevo error
                nuevo_error = self._crear_nuevo_error(
                    error,
                    analisis["metadata"],
                    hash_pregunta
                )
                banco["errores"].append(nuevo_error)
                contador_nuevos += 1
                print(f"  ➕ Nuevo: {error['pregunta'][:50]}...")
        
        # PASO 5: Actualizar metadatos del banco
        banco["fecha_ultima_actualizacion"] = datetime.now().isoformat()
        banco["total_errores_registrados"] = len(banco["errores"])
        
        # PASO 6: Guardar banco actualizado
        self._guardar_banco(banco)
        
        # PASO 7: Actualizar estadísticas
        self._actualizar_estadisticas_resumen(banco)
        
        # PASO 8: Retornar resumen
        errores_activos = self._contar_errores_activos(banco)
        errores_resueltos = self._contar_errores_resueltos(banco)
        
        print(f"\n✅ Banco actualizado: {contador_nuevos} nuevos, {contador_actualizados} actualizados")
        
        return {
            "mensaje": "✅ Banco de errores actualizado exitosamente",
            "nuevos": contador_nuevos,
            "actualizados": contador_actualizados,
            "total_banco": len(banco["errores"]),
            "errores_activos": errores_activos,
            "errores_resueltos": errores_resueltos
        }
    
    def _calcular_hash_pregunta(self, texto_pregunta: str) -> str:
        """
        Calcula SHA-256 hash de la pregunta para detectar duplicados.
        
        Args:
            texto_pregunta: Texto de la pregunta
        
        Returns:
            Hash hexadecimal de 64 caracteres
        """
        texto_normalizado = texto_pregunta.strip().lower()
        return hashlib.sha256(texto_normalizado.encode('utf-8')).hexdigest()
    
    def _cargar_banco(self) -> Dict:
        """
        Carga el banco de errores desde disco.
        
        Returns:
            Diccionario con la estructura del banco
        """
        if self.RUTA_BANCO.exists():
            with open(self.RUTA_BANCO, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Crear banco vacío
            return self._crear_banco_vacio()
    
    def _crear_banco_vacio(self) -> Dict:
        """Crea estructura inicial del banco."""
        return {
            "version": self.VERSION_BANCO,
            "fecha_creacion": datetime.now().isoformat(),
            "fecha_ultima_actualizacion": datetime.now().isoformat(),
            "total_errores_registrados": 0,
            "errores": []
        }
    
    def _guardar_banco(self, banco: Dict):
        """
        Guarda el banco de errores en disco.
        
        Args:
            banco: Diccionario con la estructura del banco
        """
        with open(self.RUTA_BANCO, 'w', encoding='utf-8') as f:
            json.dump(banco, f, indent=2, ensure_ascii=False)
    
    def _buscar_por_hash(self, errores: List[Dict], hash_pregunta: str) -> Optional[Dict]:
        """
        Busca un error en el banco por su hash.
        
        Args:
            errores: Lista de errores del banco
            hash_pregunta: Hash SHA-256 de la pregunta
        
        Returns:
            Diccionario del error si existe, None si no
        """
        for error in errores:
            if error["hash_pregunta"] == hash_pregunta:
                return error
        return None
    
    def _crear_nuevo_error(
        self, 
        pregunta: Dict, 
        metadata_examen: Dict, 
        hash_pregunta: str
    ) -> Dict:
        """
        Crea una nueva entrada de error en el banco.
        
        Args:
            pregunta: Datos de la pregunta del análisis
            metadata_examen: Metadata del examen
            hash_pregunta: Hash SHA-256 de la pregunta
        
        Returns:
            Diccionario con la estructura completa del error
        """
        nuevo_error = {
            "id_error": str(uuid.uuid4()),
            "hash_pregunta": hash_pregunta,
            
            "examen_origen": {
                "id": metadata_examen["id"],
                "archivo": f"examen_{metadata_examen['id']}.json",
                "fecha_completado": metadata_examen["fecha_completado"],
                "carpeta_ruta": metadata_examen.get("carpeta_ruta", ""),
                "carpeta_nombre": metadata_examen.get("carpeta", "")
            },
            
            "pregunta": {
                "texto": pregunta["pregunta"],
                "tipo": pregunta["tipo"],
                "opciones": pregunta.get("opciones", []),
                "respuesta_correcta": pregunta.get("respuesta_correcta", None)
            },
            
            "historial_respuestas": [
                {
                    "fecha": metadata_examen["fecha_completado"],
                    "respuesta_usuario": pregunta["respuesta_usuario"],
                    "puntos": pregunta["puntos"],
                    "puntos_maximos": pregunta["puntos_maximos"],
                    "estado": pregunta["estado_respuesta"],
                    "examen_id": metadata_examen["id"]
                }
            ],
            
            "veces_fallada": 1 if pregunta["estado_respuesta"] == "fallo" else 0,
            "veces_practicada": 1,
            "ultima_vez_practicada": metadata_examen["fecha_completado"],
            "fecha_primer_error": metadata_examen["fecha_completado"],
            "estado_refuerzo": "nuevo_error",
            "prioridad": "media",  # Inicial, se recalcula después
            
            "tema_detectado": None,  # Para Módulo 3 (futuro)
            "etiquetas": [],  # Para Módulo 3 (futuro)
            "nota_usuario": ""
        }
        
        # Recalcular prioridad inicial
        nuevo_error["prioridad"] = self._calcular_prioridad(nuevo_error)
        
        return nuevo_error
    
    def _actualizar_error_existente(
        self, 
        error_existente: Dict, 
        nuevo_intento: Dict, 
        metadata_examen: Dict
    ):
        """
        Actualiza un error que ya existe en el banco con nuevo intento.
        
        Args:
            error_existente: Error existente en el banco (se modifica in-place)
            nuevo_intento: Datos del nuevo intento
            metadata_examen: Metadata del examen actual
        """
        # Agregar nuevo intento al historial
        error_existente["historial_respuestas"].append({
            "fecha": metadata_examen["fecha_completado"],
            "respuesta_usuario": nuevo_intento["respuesta_usuario"],
            "puntos": nuevo_intento["puntos"],
            "puntos_maximos": nuevo_intento["puntos_maximos"],
            "estado": nuevo_intento["estado_respuesta"],
            "examen_id": metadata_examen["id"]
        })
        
        # Actualizar contadores
        if nuevo_intento["estado_respuesta"] == "fallo":
            error_existente["veces_fallada"] += 1
        
        error_existente["veces_practicada"] += 1
        error_existente["ultima_vez_practicada"] = metadata_examen["fecha_completado"]
        
        # Recalcular estado de refuerzo
        error_existente["estado_refuerzo"] = self._calcular_estado_refuerzo(error_existente)
        
        # Recalcular prioridad
        error_existente["prioridad"] = self._calcular_prioridad(error_existente)
    
    def _calcular_estado_refuerzo(self, error: Dict) -> EstadoRefuerzo:
        """
        Calcula el estado de refuerzo basándose en el historial.
        
        Args:
            error: Diccionario del error
        
        Returns:
            "nuevo_error" | "en_refuerzo" | "resuelto"
        """
        historial = error["historial_respuestas"]
        
        if len(historial) == 1:
            return "nuevo_error"
        
        # Verificar criterio de resolución
        if self._criterio_resolucion_cumplido(error):
            return "resuelto"
        
        return "en_refuerzo"
    
    def _criterio_resolucion_cumplido(self, error: Dict) -> bool:
        """
        Determina si un error se considera resuelto.
        
        Criterio: Últimos 2 intentos fueron aciertos consecutivos
        
        Args:
            error: Diccionario del error
        
        Returns:
            True si el error está resuelto, False si no
        """
        historial = error["historial_respuestas"]
        
        if len(historial) < 2:
            return False
        
        # Verificar últimos 2 intentos
        ultimos_dos = historial[-2:]
        
        return all(intento["estado"] == "acierto" for intento in ultimos_dos)
    
    def _calcular_prioridad(self, error: Dict) -> Prioridad:
        """
        Calcula la prioridad del error basándose en historial.
        
        Args:
            error: Diccionario del error
        
        Returns:
            "alta" | "media" | "baja"
        """
        veces_fallada = error["veces_fallada"]
        
        # Calcular días sin práctica
        ultima_practica = datetime.fromisoformat(error["ultima_vez_practicada"])
        dias_sin_practica = (datetime.now() - ultima_practica).days
        
        # Criterios de prioridad
        if veces_fallada >= 3:
            return "alta"
        elif veces_fallada >= 2 or dias_sin_practica > 7:
            return "media"
        else:
            return "baja"
    
    def _contar_errores_en_banco(self) -> int:
        """Cuenta el total de errores en el banco."""
        if not self.RUTA_BANCO.exists():
            return 0
        banco = self._cargar_banco()
        return len(banco["errores"])
    
    def _contar_errores_activos(self, banco: Dict) -> int:
        """Cuenta errores con estado 'nuevo_error' o 'en_refuerzo'."""
        return sum(
            1 for error in banco["errores"]
            if error["estado_refuerzo"] in ["nuevo_error", "en_refuerzo"]
        )
    
    def _contar_errores_resueltos(self, banco: Dict) -> int:
        """Cuenta errores con estado 'resuelto'."""
        return sum(
            1 for error in banco["errores"]
            if error["estado_refuerzo"] == "resuelto"
        )
    
    def _actualizar_estadisticas_resumen(self, banco: Dict):
        """
        Genera y guarda estadísticas agregadas del banco (cache).
        
        Args:
            banco: Diccionario del banco completo
        """
        total_errores = len(banco["errores"])
        
        # Contar por estado
        errores_nuevos = sum(
            1 for e in banco["errores"] if e["estado_refuerzo"] == "nuevo_error"
        )
        errores_en_refuerzo = sum(
            1 for e in banco["errores"] if e["estado_refuerzo"] == "en_refuerzo"
        )
        errores_resueltos = sum(
            1 for e in banco["errores"] if e["estado_refuerzo"] == "resuelto"
        )
        
        # Contar por prioridad
        errores_alta = sum(1 for e in banco["errores"] if e["prioridad"] == "alta")
        errores_media = sum(1 for e in banco["errores"] if e["prioridad"] == "media")
        errores_baja = sum(1 for e in banco["errores"] if e["prioridad"] == "baja")
        
        # Calcular tasa de resolución
        tasa_resolucion = (
            (errores_resueltos / total_errores * 100) 
            if total_errores > 0 
            else 0
        )
        
        estadisticas = {
            "fecha_actualizacion": datetime.now().isoformat(),
            "total_errores": total_errores,
            "por_estado": {
                "nuevos": errores_nuevos,
                "en_refuerzo": errores_en_refuerzo,
                "resueltos": errores_resueltos
            },
            "por_prioridad": {
                "alta": errores_alta,
                "media": errores_media,
                "baja": errores_baja
            },
            "errores_activos": errores_nuevos + errores_en_refuerzo,
            "tasa_resolucion": round(tasa_resolucion, 2)
        }
        
        with open(self.RUTA_ESTADISTICAS, 'w', encoding='utf-8') as f:
            json.dump(estadisticas, f, indent=2, ensure_ascii=False)
    
    # ===== MÉTODOS DE CONSULTA =====
    
    def obtener_estadisticas(self) -> Dict:
        """
        Obtiene las estadísticas agregadas del banco.
        
        Returns:
            Diccionario con estadísticas del cache o calculadas en vivo
        """
        if self.RUTA_ESTADISTICAS.exists():
            with open(self.RUTA_ESTADISTICAS, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Calcular en vivo si no hay cache
            banco = self._cargar_banco()
            self._actualizar_estadisticas_resumen(banco)
            with open(self.RUTA_ESTADISTICAS, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    def obtener_errores_para_practica(
        self, 
        max_errores: int = 10,
        solo_estado: Optional[EstadoRefuerzo] = None,
        solo_prioridad: Optional[Prioridad] = None
    ) -> List[Dict]:
        """
        Obtiene errores del banco para generar práctica personalizada.
        
        Args:
            max_errores: Máximo número de errores a retornar
            solo_estado: Filtrar por estado ("nuevo_error", "en_refuerzo", "resuelto")
            solo_prioridad: Filtrar por prioridad ("alta", "media", "baja")
        
        Returns:
            Lista de errores ordenados por prioridad
        """
        banco = self._cargar_banco()
        errores = banco["errores"]
        
        # Filtrar por estado si se especifica
        if solo_estado:
            errores = [e for e in errores if e["estado_refuerzo"] == solo_estado]
        
        # Filtrar por prioridad si se especifica
        if solo_prioridad:
            errores = [e for e in errores if e["prioridad"] == solo_prioridad]
        
        # Ordenar por prioridad (alta primero) y fecha (más antiguos primero)
        prioridad_orden = {"alta": 0, "media": 1, "baja": 2}
        errores_ordenados = sorted(
            errores,
            key=lambda e: (
                prioridad_orden[e["prioridad"]],
                e["fecha_primer_error"]
            )
        )
        
        return errores_ordenados[:max_errores]
    
    def generar_reporte_banco(self) -> str:
        """
        Genera un reporte en texto plano del banco de errores.
        
        Returns:
            String con reporte formateado
        """
        estadisticas = self.obtener_estadisticas()
        
        reporte = f"""
╔══════════════════════════════════════════════════════════════╗
║             REPORTE DEL BANCO DE ERRORES                     ║
╚══════════════════════════════════════════════════════════════╝

📊 ESTADÍSTICAS GENERALES
  • Total errores registrados: {estadisticas['total_errores']}
  • Errores activos: {estadisticas['errores_activos']}
  • Errores resueltos: {estadisticas['por_estado']['resueltos']}
  • Tasa de resolución: {estadisticas['tasa_resolucion']}%

📋 POR ESTADO DE REFUERZO
  • 🆕 Nuevos: {estadisticas['por_estado']['nuevos']}
  • 🔄 En refuerzo: {estadisticas['por_estado']['en_refuerzo']}
  • ✅ Resueltos: {estadisticas['por_estado']['resueltos']}

⚠️ POR PRIORIDAD
  • 🔴 Alta: {estadisticas['por_prioridad']['alta']}
  • 🟡 Media: {estadisticas['por_prioridad']['media']}
  • 🟢 Baja: {estadisticas['por_prioridad']['baja']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 RECOMENDACIÓN:
"""
        
        if estadisticas['por_prioridad']['alta'] > 0:
            reporte += f"   Tienes {estadisticas['por_prioridad']['alta']} errores de alta prioridad.\n"
            reporte += "   ¡Practica estos primero!\n"
        elif estadisticas['errores_activos'] > 0:
            reporte += f"   Tienes {estadisticas['errores_activos']} errores activos.\n"
            reporte += "   Dedica tiempo a reforzarlos.\n"
        else:
            reporte += "   ¡Excelente! No tienes errores activos.\n"
            reporte += "   Sigue practicando para mantener el nivel.\n"
        
        return reporte


# ═══════════════════════════════════════════════════════════════
# EJEMPLO DE USO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    Ejemplo de uso del banco de errores.
    """
    
    banco = BancoErrores()
    
    # Ejemplo 1: Actualizar banco después de un examen
    print("=" * 70)
    print("📝 EJEMPLO 1: Actualizar banco desde examen")
    print("=" * 70)
    
    try:
        resultado = banco.actualizar_banco_desde_examen(
            "examenes/Platzi/examen_20251120_134728.json"
        )
        
        print(f"\n{resultado['mensaje']}")
        print(f"  Nuevos errores: {resultado['nuevos']}")
        print(f"  Actualizados: {resultado['actualizados']}")
        print(f"  Total en banco: {resultado['total_banco']}")
        print(f"  Errores activos: {resultado['errores_activos']}")
        
    except FileNotFoundError:
        print("⚠️  Archivo de examen no encontrado")
    
    # Ejemplo 2: Ver estadísticas
    print("\n" + "=" * 70)
    print("📊 EJEMPLO 2: Estadísticas del banco")
    print("=" * 70)
    
    estadisticas = banco.obtener_estadisticas()
    print(f"\nTotal errores: {estadisticas['total_errores']}")
    print(f"Errores activos: {estadisticas['errores_activos']}")
    print(f"Tasa de resolución: {estadisticas['tasa_resolucion']}%")
    
    # Ejemplo 3: Obtener errores para práctica
    print("\n" + "=" * 70)
    print("🎯 EJEMPLO 3: Errores para práctica")
    print("=" * 70)
    
    errores_practica = banco.obtener_errores_para_practica(
        max_errores=5,
        solo_prioridad="alta"
    )
    
    print(f"\nErrores de alta prioridad para practicar: {len(errores_practica)}")
    for i, error in enumerate(errores_practica, 1):
        print(f"\n{i}. {error['pregunta']['texto'][:60]}...")
        print(f"   Veces fallada: {error['veces_fallada']}")
        print(f"   Estado: {error['estado_refuerzo']}")
    
    # Ejemplo 4: Generar reporte
    print("\n" + "=" * 70)
    print("📄 EJEMPLO 4: Reporte del banco")
    print("=" * 70)
    
    print(banco.generar_reporte_banco())
