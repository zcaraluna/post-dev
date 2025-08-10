#!/usr/bin/env python3
"""
Script para agregar un nuevo aparato biométrico a la base de datos
"""

import sys
from database import connect_db
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def agregar_aparato_biometrico(nombre, serial, ip_address=None, puerto=4370, ubicacion=None):
    """
    Agregar un nuevo aparato biométrico a la base de datos
    
    Args:
        nombre (str): Nombre del aparato
        serial (str): Número de serie del aparato
        ip_address (str): Dirección IP del aparato (opcional)
        puerto (int): Puerto del aparato (por defecto 4370)
        ubicacion (str): Ubicación del aparato (opcional)
        
    Returns:
        bool: True si se agregó correctamente, False en caso contrario
    """
    try:
        conn = connect_db()
        if not conn:
            logger.error("No se pudo conectar a la base de datos")
            return False
            
        cursor = conn.cursor()
        
        # Verificar si el aparato ya existe
        cursor.execute("SELECT id, nombre FROM aparatos_biometricos WHERE serial = %s", (serial,))
        existing = cursor.fetchone()
        
        if existing:
            logger.warning(f"El aparato con serial {serial} ya existe en la base de datos")
            logger.info(f"Aparato existente: ID={existing[0]}, Nombre={existing[1]}")
            return False
        
        # Insertar nuevo aparato
        query = """
            INSERT INTO aparatos_biometricos 
            (nombre, serial, ip_address, puerto, ubicacion, estado) 
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        cursor.execute(query, (nombre, serial, ip_address, puerto, ubicacion, 'ACTIVO'))
        aparato_id = cursor.fetchone()[0]
        
        conn.commit()
        
        logger.info(f"✅ Aparato biométrico agregado exitosamente:")
        logger.info(f"   ID: {aparato_id}")
        logger.info(f"   Nombre: {nombre}")
        logger.info(f"   Serial: {serial}")
        if ip_address:
            logger.info(f"   IP: {ip_address}:{puerto}")
        if ubicacion:
            logger.info(f"   Ubicación: {ubicacion}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error al agregar aparato biométrico: {e}")
        return False
    finally:
        if conn:
            conn.close()

def listar_aparatos_biometricos():
    """
    Listar todos los aparatos biométricos en la base de datos
    
    Returns:
        bool: True si se listaron correctamente
    """
    try:
        conn = connect_db()
        if not conn:
            logger.error("No se pudo conectar a la base de datos")
            return False
            
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nombre, serial, ip_address, puerto, ubicacion, estado, fecha_registro 
            FROM aparatos_biometricos 
            ORDER BY id
        """)
        
        aparatos = cursor.fetchall()
        
        if not aparatos:
            print("📋 No hay aparatos biométricos registrados en la base de datos")
            return True
        
        print("📋 APARATOS BIOMÉTRICOS REGISTRADOS:")
        print("=" * 80)
        print(f"{'ID':<4} {'Nombre':<20} {'Serial':<15} {'IP':<15} {'Puerto':<6} {'Estado':<8}")
        print("-" * 80)
        
        for aparato in aparatos:
            id_aparato, nombre, serial, ip, puerto, ubicacion, estado, fecha = aparato
            ip_display = ip if ip else "N/A"
            print(f"{id_aparato:<4} {nombre:<20} {serial:<15} {ip_display:<15} {puerto:<6} {estado:<8}")
        
        print(f"\nTotal de aparatos: {len(aparatos)}")
        return True
        
    except Exception as e:
        logger.error(f"Error al listar aparatos biométricos: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    """Función principal"""
    print("🔧 GESTOR DE APARATOS BIOMÉTRICOS")
    print("=" * 50)
    
    if len(sys.argv) < 3:
        print("❌ Uso incorrecto")
        print("\n💡 USO:")
        print("  python agregar_aparato_biometrico.py <NOMBRE> <SERIAL> [IP] [PUERTO] [UBICACION]")
        print("\n📝 EJEMPLOS:")
        print("  python agregar_aparato_biometrico.py 'ANAPOL 2' 'PAS4241300509'")
        print("  python agregar_aparato_biometrico.py 'ANAPOL 2' 'PAS4241300509' '192.168.100.202'")
        print("  python agregar_aparato_biometrico.py 'ANAPOL 2' 'PAS4241300509' '192.168.100.202' 4370 'Oficina Principal'")
        print("\n📋 COMANDOS ESPECIALES:")
        print("  python agregar_aparato_biometrico.py --list")
        print("  python agregar_aparato_biometrico.py --help")
        sys.exit(1)
    
    # Comando especial para listar
    if sys.argv[1] == "--list":
        if listar_aparatos_biometricos():
            sys.exit(0)
        else:
            sys.exit(1)
    
    # Comando especial para ayuda
    if sys.argv[1] == "--help":
        print("🔧 GESTOR DE APARATOS BIOMÉTRICOS - AYUDA")
        print("=" * 50)
        print("\n📝 FUNCIONES:")
        print("  • Agregar nuevo aparato biométrico")
        print("  • Listar aparatos existentes")
        print("  • Verificar duplicados")
        print("\n📋 PARÁMETROS:")
        print("  NOMBRE    : Nombre descriptivo del aparato")
        print("  SERIAL    : Número de serie único del dispositivo")
        print("  IP        : Dirección IP del aparato (opcional)")
        print("  PUERTO    : Puerto de comunicación (opcional, default: 4370)")
        print("  UBICACION : Ubicación física del aparato (opcional)")
        sys.exit(0)
    
    # Obtener parámetros
    nombre = sys.argv[1]
    serial = sys.argv[2]
    ip_address = sys.argv[3] if len(sys.argv) > 3 else None
    puerto = int(sys.argv[4]) if len(sys.argv) > 4 else 4370
    ubicacion = sys.argv[5] if len(sys.argv) > 5 else None
    
    print(f"🎯 Agregando aparato biométrico:")
    print(f"   Nombre: {nombre}")
    print(f"   Serial: {serial}")
    if ip_address:
        print(f"   IP: {ip_address}:{puerto}")
    if ubicacion:
        print(f"   Ubicación: {ubicacion}")
    print()
    
    # Agregar aparato
    if agregar_aparato_biometrico(nombre, serial, ip_address, puerto, ubicacion):
        print("✅ APARATO AGREGADO EXITOSAMENTE")
        print("\n📋 Lista actualizada de aparatos:")
        listar_aparatos_biometricos()
        sys.exit(0)
    else:
        print("❌ ERROR AL AGREGAR APARATO")
        sys.exit(1)

if __name__ == "__main__":
    main()
