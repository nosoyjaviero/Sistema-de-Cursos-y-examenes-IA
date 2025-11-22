"""
📊 Ver Estadísticas del Banco de Errores
==========================================

Script rápido para ver el estado actual de tus errores.
"""

from banco_errores import BancoErrores

banco = BancoErrores()

# Mostrar reporte completo
print(banco.generar_reporte())

# O solo estadísticas
stats = banco.obtener_estadisticas()
print(f"\n📈 RESUMEN RÁPIDO:")
print(f"   Total errores: {stats['total_errores']}")
print(f"   Activos: {stats['errores_activos']}")
print(f"   Resueltos: {stats['por_estado']['resueltos']}")
print(f"   Tasa de resolución: {stats['tasa_resolucion']}%")
