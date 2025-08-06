#!/usr/bin/env python3
"""
Prueba con la biblioteca pyzk original
"""

from zk import ZK
import sys

def test_pyzk_connection(ip_address="192.168.100.201", port=4370):
    """Prueba conexión usando la biblioteca pyzk"""
    print(f"🔌 Probando conexión con pyzk a {ip_address}:{port}")
    
    try:
        # Crear instancia ZK
        zk = ZK(ip_address, port, timeout=10)
        
        # Intentar conectar
        print("📡 Intentando conectar...")
        conn = zk.connect()
        
        if conn:
            print("✅ Conexión exitosa con pyzk!")
            
            # Obtener información del dispositivo
            try:
                info = conn.get_device_info()
                print(f"📱 Dispositivo: {info}")
            except Exception as e:
                print(f"⚠️  No se pudo obtener info: {e}")
            
            # Obtener usuarios
            try:
                users = conn.get_users()
                print(f"👥 Usuarios encontrados: {len(users)}")
            except Exception as e:
                print(f"⚠️  No se pudo obtener usuarios: {e}")
            
            # Cerrar conexión
            conn.disconnect()
            return True
        else:
            print("❌ No se pudo conectar con pyzk")
            return False
            
    except Exception as e:
        print(f"❌ Error con pyzk: {e}")
        return False

if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.100.201"
    test_pyzk_connection(ip) 