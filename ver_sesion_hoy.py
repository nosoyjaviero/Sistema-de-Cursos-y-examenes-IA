"""
🎯 Ver Sesión de Estudio Recomendada Para Hoy
==============================================

Muestra qué errores deberías practicar hoy según prioridad.
"""

from priorizador_errores import Priorizador

priorizador = Priorizador()

# Obtener sesión
sesion = priorizador.obtener_errores_para_hoy(max_errores=10)

# Mostrar reporte
reporte = priorizador.generar_reporte_priorizacion(sesion)
print(reporte)
