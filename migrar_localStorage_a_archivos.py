"""
Script para migrar datos de localStorage a archivos JSON
Ejecuta este script DESDE EL NAVEGADOR (consola de desarrollador)
o usa el exportador HTML que ya tienes
"""

# Este script debe ejecutarse en la consola del navegador
# Copia y pega en la consola de Chrome/Edge (F12 → Console)

migrar_a_archivos = """
(async function() {
    const SERVER_IP = window.location.hostname;
    const SERVER_PORT = 8000;
    
    const tipos = ['notas', 'flashcards', 'practicas'];
    
    console.log('🔄 Iniciando migración de localStorage a archivos...');
    
    for (const tipo of tipos) {
        try {
            const data = localStorage.getItem(tipo);
            if (data) {
                const parsed = JSON.parse(data);
                console.log(`📦 Migrando ${tipo}: ${parsed.length} elementos`);
                
                const response = await fetch(`http://${SERVER_IP}:${SERVER_PORT}/datos/${tipo}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: data
                });
                
                if (response.ok) {
                    console.log(`✅ ${tipo} migrado correctamente`);
                } else {
                    console.error(`❌ Error migrando ${tipo}`);
                }
            } else {
                console.log(`ℹ️  No hay datos de ${tipo} en localStorage`);
            }
        } catch (e) {
            console.error(`❌ Error con ${tipo}:`, e);
        }
    }
    
    // Migrar sesiones completadas
    try {
        const sesiones = localStorage.getItem('sesiones_completadas');
        if (sesiones) {
            const response = await fetch(`http://${SERVER_IP}:${SERVER_PORT}/datos/sesiones/completadas`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: sesiones
            });
            if (response.ok) {
                console.log('✅ Sesiones completadas migradas');
            }
        }
    } catch (e) {
        console.error('❌ Error migrando sesiones:', e);
    }
    
    // Migrar sesión activa
    try {
        const sesionActiva = localStorage.getItem('examinator_sesion_activa');
        if (sesionActiva) {
            const response = await fetch(`http://${SERVER_IP}:${SERVER_PORT}/datos/sesion/activa`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: sesionActiva
            });
            if (response.ok) {
                console.log('✅ Sesión activa migrada');
            }
        }
    } catch (e) {
        console.error('❌ Error migrando sesión activa:', e);
    }
    
    console.log('🎉 Migración completada!');
    console.log('💡 Los datos ahora están en: C:\\\\Users\\\\Fela\\\\Documents\\\\Proyectos\\\\Examinator\\\\extracciones\\\\');
})();
"""

print("="*70)
print("MIGRACIÓN DE DATOS DE LOCALSTORAGE A ARCHIVOS JSON")
print("="*70)
print()
print("INSTRUCCIONES:")
print()
print("1. Abre tu app en el navegador (http://localhost:5173)")
print("2. Presiona F12 para abrir las herramientas de desarrollador")
print("3. Ve a la pestaña 'Console'")
print("4. Copia y pega el siguiente código:")
print()
print("-"*70)
print(migrar_a_archivos)
print("-"*70)
print()
print("5. Presiona Enter")
print("6. Verás mensajes de migración en la consola")
print("7. Los archivos se guardarán en:")
print("   C:\\Users\\Fela\\Documents\\Proyectos\\Examinator\\extracciones\\")
print()
print("="*70)
