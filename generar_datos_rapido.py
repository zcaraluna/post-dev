#!/usr/bin/env python3
"""
Script rápido para generar datos ficticios en el Sistema QUIRA
Ejecuta automáticamente sin interacción del usuario
"""

from insercion_masiva_datos import insercion_masiva
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Función principal - ejecuta inserción automática"""
    print("🚀 GENERANDO DATOS FICTICIOS PARA SISTEMA QUIRA")
    print("=" * 50)
    
    # Cantidad de registros a generar
    CANTIDAD = 10000
    
    print(f"📊 Generando {CANTIDAD:,} registros de postulantes...")
    print("⏳ Esto puede tomar varios minutos...")
    
    # Ejecutar inserción masiva
    if insercion_masiva(CANTIDAD):
        print("\n✅ ¡Datos generados exitosamente!")
        print(f"📈 Se han creado {CANTIDAD:,} registros de postulantes")
        print("🎯 El sistema QUIRA ahora tiene datos para pruebas y demostraciones")
    else:
        print("\n❌ Error al generar datos")
        print("🔧 Verifique que PostgreSQL esté ejecutándose y la base de datos exista")

if __name__ == "__main__":
    main()
