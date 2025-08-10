#!/usr/bin/env python3
"""
Script de diagnóstico completo para revisar el contenido actual de las tablas
"""

from database import connect_db
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def mostrar_estructura_tabla(cursor, nombre_tabla):
    """Mostrar estructura detallada de una tabla"""
    try:
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_name = %s 
            ORDER BY ordinal_position
        """, (nombre_tabla,))
        
        columnas = cursor.fetchall()
        
        print(f"\n{'='*80}")
        print(f"📋 ESTRUCTURA DE LA TABLA: {nombre_tabla.upper()}")
        print(f"{'='*80}")
        
        for columna in columnas:
            nombre, tipo, longitud, nullable, default = columna
            print(f"📝 {nombre:25} | {tipo:15} | Longitud: {longitud or 'N/A':8} | Nullable: {nullable}")
        
        return columnas
        
    except Exception as e:
        logger.error(f"Error al obtener estructura de {nombre_tabla}: {e}")
        return []

def mostrar_contenido_tabla(cursor, nombre_tabla, limite=10):
    """Mostrar contenido de una tabla con límite de registros"""
    try:
        # Obtener total de registros
        cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
        total = cursor.fetchone()[0]
        
        print(f"\n📊 CONTENIDO DE {nombre_tabla.upper()}:")
        print(f"   Total de registros: {total:,}")
        
        if total == 0:
            print("   ⚠️  Tabla vacía")
            return
        
        # Obtener columnas
        cursor.execute(f"SELECT * FROM {nombre_tabla} LIMIT {limite}")
        registros = cursor.fetchall()
        
        # Obtener nombres de columnas
        cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{nombre_tabla}' ORDER BY ordinal_position")
        nombres_columnas = [col[0] for col in cursor.fetchall()]
        
        print(f"   Mostrando primeros {len(registros)} registros:")
        print("-" * 100)
        
        # Mostrar encabezados
        headers = " | ".join([f"{col:15}" for col in nombres_columnas])
        print(f"   {headers}")
        print("-" * 100)
        
        # Mostrar datos
        for registro in registros:
            # Truncar valores largos para mejor visualización
            valores = []
            for valor in registro:
                if valor is None:
                    valores.append("NULL")
                elif isinstance(valor, bytes):
                    valores.append(f"BYTES({len(valor)})")
                elif isinstance(valor, str) and len(str(valor)) > 12:
                    valores.append(f"{str(valor)[:10]}...")
                else:
                    valores.append(str(valor)[:15])
            
            fila = " | ".join([f"{val:15}" for val in valores])
            print(f"   {fila}")
        
        if total > limite:
            print(f"   ... y {total - limite} registros más")
            
    except Exception as e:
        logger.error(f"Error al mostrar contenido de {nombre_tabla}: {e}")

def mostrar_restricciones_tabla(cursor, nombre_tabla):
    """Mostrar restricciones de una tabla"""
    try:
        cursor.execute("""
            SELECT 
                constraint_name,
                constraint_type
            FROM information_schema.table_constraints 
            WHERE table_name = %s
        """, (nombre_tabla,))
        
        restricciones = cursor.fetchall()
        if restricciones:
            print(f"\n🔒 RESTRICCIONES DE {nombre_tabla.upper()}:")
            for nombre, tipo in restricciones:
                print(f"   • {nombre}: {tipo}")
        else:
            print(f"\n🔒 {nombre_tabla.upper()}: Sin restricciones")
            
    except Exception as e:
        logger.error(f"Error al obtener restricciones de {nombre_tabla}: {e}")

def diagnosticar_tabla_completa(cursor, nombre_tabla):
    """Diagnóstico completo de una tabla"""
    print(f"\n{'='*100}")
    print(f"🔍 DIAGNÓSTICO COMPLETO: {nombre_tabla.upper()}")
    print(f"{'='*100}")
    
    # Estructura
    columnas = mostrar_estructura_tabla(cursor, nombre_tabla)
    
    # Restricciones
    mostrar_restricciones_tabla(cursor, nombre_tabla)
    
    # Contenido
    mostrar_contenido_tabla(cursor, nombre_tabla, limite=5)

def main():
    """Función principal"""
    print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA QUIRA")
    print("=" * 60)
    
    try:
        conn = connect_db()
        if not conn:
            logger.error("❌ No se pudo conectar a la base de datos")
            return
        
        cursor = conn.cursor()
        
        # Lista de tablas a diagnosticar
        tablas = ['usuarios', 'aparatos_biometricos', 'postulantes']
        
        for tabla in tablas:
            try:
                diagnosticar_tabla_completa(cursor, tabla)
            except Exception as e:
                logger.error(f"Error al diagnosticar tabla {tabla}: {e}")
        
        # Resumen final
        print(f"\n{'='*100}")
        print("📋 RESUMEN GENERAL")
        print(f"{'='*100}")
        
        for tabla in tablas:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"   📊 {tabla}: {count:,} registros")
            except Exception as e:
                print(f"   ❌ {tabla}: Error al contar - {e}")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Error en diagnóstico: {e}")

if __name__ == "__main__":
    main()
