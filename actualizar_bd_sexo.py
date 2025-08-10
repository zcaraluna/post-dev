#!/usr/bin/env python3
"""
Script para actualizar la base de datos y agregar la columna sexo
"""

from database import connect_db, init_database
import psycopg2

def actualizar_bd_sexo():
    """Actualizar la base de datos para agregar la columna sexo"""
    try:
        print("🔄 Inicializando base de datos...")
        if init_database():
            print("✅ Base de datos actualizada correctamente")
            print("✅ Columna 'sexo' agregada a la tabla postulantes")
        else:
            print("❌ Error al actualizar la base de datos")
            return False
            
        # Verificar que la columna se creó correctamente
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'postulantes' 
                AND column_name = 'sexo'
            """)
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if resultado:
                print("✅ Verificación exitosa: La columna 'sexo' existe en la tabla postulantes")
                return True
            else:
                print("❌ Error: La columna 'sexo' no se creó correctamente")
                return False
        else:
            print("❌ Error: No se pudo conectar a la base de datos")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la actualización: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando actualización de base de datos...")
    if actualizar_bd_sexo():
        print("\n🎉 ¡Actualización completada exitosamente!")
        print("📝 Ahora puedes usar el campo 'Sexo' en el formulario de agregar postulante")
    else:
        print("\n💥 Error en la actualización")
        print("🔧 Verifica la conexión a la base de datos y vuelve a intentar")
