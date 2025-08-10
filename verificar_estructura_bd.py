#!/usr/bin/env python3
"""
Script para verificar la estructura de la base de datos
"""

from database import connect_db
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verificar_estructura_tabla():
    """Verificar la estructura exacta de la tabla postulantes"""
    try:
        conn = connect_db()
        if not conn:
            logger.error("❌ No se pudo conectar a la base de datos")
            return False
        
        cursor = conn.cursor()
        
        # Obtener información detallada de las columnas
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_name = 'postulantes' 
            ORDER BY ordinal_position
        """)
        
        columnas = cursor.fetchall()
        
        print("=" * 80)
        print("📋 ESTRUCTURA DE LA TABLA POSTULANTES")
        print("=" * 80)
        
        for columna in columnas:
            nombre, tipo, longitud, nullable, default = columna
            print(f"📝 {nombre:25} | {tipo:15} | Longitud: {longitud or 'N/A':8} | Nullable: {nullable}")
        
        print("=" * 80)
        
        # Verificar si hay datos existentes
        cursor.execute("SELECT COUNT(*) FROM postulantes")
        count = cursor.fetchone()[0]
        print(f"📊 Total de registros existentes: {count:,}")
        
        # Verificar restricciones
        cursor.execute("""
            SELECT 
                constraint_name,
                constraint_type
            FROM information_schema.table_constraints 
            WHERE table_name = 'postulantes'
        """)
        
        restricciones = cursor.fetchall()
        if restricciones:
            print("\n🔒 RESTRICCIONES:")
            for nombre, tipo in restricciones:
                print(f"   • {nombre}: {tipo}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error al verificar estructura: {e}")
        return False

def probar_insercion_simple():
    """Probar una inserción simple para identificar el problema"""
    try:
        conn = connect_db()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Datos de prueba mínimos
        datos_prueba = {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'cedula': '12345678',
            'fecha_nacimiento': '1990-01-01',
            'telefono': '0981-123456',
            'fecha_registro': '2024-01-01 10:00:00',
            'usuario_registrador': 1,
            'edad': 34,
            'unidad': 'Escuela de Formación Básica',
            'dedo_registrado': 'Pulgar Derecho',
            'registrado_por': 'Téc. Juan Pérez',
            'aparato_id': 1,
            'uid_k40': 1000,
            'huella_dactilar': b'test',
            'observaciones': 'Prueba',
            'sexo': 'M',
            'usuario_ultima_edicion': 'Téc. Juan Pérez',
            'fecha_ultima_edicion': '2024-01-01 10:00:00'
        }
        
        print("\n🧪 PROBANDO INSERCIÓN SIMPLE...")
        
        try:
            cursor.execute("""
                INSERT INTO postulantes (
                    nombre, apellido, cedula, fecha_nacimiento, telefono, 
                    fecha_registro, usuario_registrador, edad, unidad, 
                    dedo_registrado, registrado_por, aparato_id, uid_k40, 
                    huella_dactilar, observaciones, sexo, usuario_ultima_edicion, 
                    fecha_ultima_edicion
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                datos_prueba['nombre'], datos_prueba['apellido'], datos_prueba['cedula'],
                datos_prueba['fecha_nacimiento'], datos_prueba['telefono'], datos_prueba['fecha_registro'],
                datos_prueba['usuario_registrador'], datos_prueba['edad'], datos_prueba['unidad'],
                datos_prueba['dedo_registrado'], datos_prueba['registrado_por'], datos_prueba['aparato_id'],
                datos_prueba['uid_k40'], datos_prueba['huella_dactilar'], datos_prueba['observaciones'],
                datos_prueba['sexo'], datos_prueba['usuario_ultima_edicion'], datos_prueba['fecha_ultima_edicion']
            ))
            
            conn.commit()
            print("✅ Inserción de prueba exitosa")
            
            # Limpiar el registro de prueba
            cursor.execute("DELETE FROM postulantes WHERE cedula = '12345678'")
            conn.commit()
            print("🧹 Registro de prueba eliminado")
            
        except Exception as e:
            print(f"❌ Error en inserción de prueba: {e}")
            conn.rollback()
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en prueba de inserción: {e}")
        return False

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN DE ESTRUCTURA DE BASE DE DATOS")
    print("=" * 60)
    
    if verificar_estructura_tabla():
        probar_insercion_simple()
    else:
        print("❌ No se pudo verificar la estructura")

if __name__ == "__main__":
    main()
