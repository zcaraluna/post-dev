#!/usr/bin/env python3
"""
Script de prueba para verificar la conectividad con dispositivos ZKTeco K40
"""

import sys
import socket
from zkteco_connector import ZKTecoK40, test_connection

def test_basic_connectivity(ip_address="192.168.1.100", port=4370):
    """Prueba básica de conectividad de red"""
    print(f"🔍 Probando conectividad básica a {ip_address}:{port}")
    
    try:
        # Crear socket UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3)
        
        # Intentar conectar
        sock.connect((ip_address, port))
        print("✅ Socket UDP creado correctamente")
        
        # Cerrar socket
        sock.close()
        return True
        
    except socket.timeout:
        print("❌ Timeout: El dispositivo no responde")
        return False
    except ConnectionRefusedError:
        print("❌ Conexión rechazada: Puerto cerrado o dispositivo no disponible")
        return False
    except Exception as e:
        print(f"❌ Error de conectividad: {e}")
        return False

def test_device_connection(ip_address="192.168.1.100", port=4370):
    """Prueba de conexión con el dispositivo ZKTeco"""
    print(f"\n🔌 Probando conexión con dispositivo ZKTeco en {ip_address}:{port}")
    
    # Crear instancia del dispositivo
    device = ZKTecoK40(ip_address, port, timeout=5)
    
    try:
        # Intentar conectar
        if device.connect():
            print("✅ Conexión establecida con el dispositivo")
            
            # Obtener información básica
            try:
                info = device.get_device_info()
                print(f"📱 Dispositivo: {info.get('device_name', 'Desconocido')}")
                print(f"🔧 Firmware: {info.get('firmware_version', 'Desconocido')}")
                print(f"📋 Serial: {info.get('serial_number', 'Desconocido')}")
            except Exception as e:
                print(f"⚠️  No se pudo obtener información del dispositivo: {e}")
            
            # Obtener cantidad de usuarios
            try:
                user_count = device.get_user_count()
                print(f"👥 Usuarios registrados: {user_count}")
            except Exception as e:
                print(f"⚠️  No se pudo obtener cantidad de usuarios: {e}")
            
            return True
        else:
            print("❌ No se pudo establecer conexión con el dispositivo")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la conexión: {e}")
        return False
    finally:
        device.disconnect()

def test_local_network():
    """Prueba de red local"""
    print("\n🌐 Probando red local...")
    
    # IPs comunes para probar
    test_ips = [
        "192.168.1.100",
        "192.168.1.101", 
        "192.168.1.102",
        "192.168.0.100",
        "192.168.0.101"
    ]
    
    for ip in test_ips:
        print(f"\n📍 Probando {ip}...")
        if test_basic_connectivity(ip):
            print(f"✅ {ip} responde - Probando conexión ZKTeco...")
            if test_device_connection(ip):
                print(f"🎉 ¡Dispositivo ZKTeco encontrado en {ip}!")
                return ip
        else:
            print(f"❌ {ip} no responde")
    
    return None

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de conectividad ZKTeco K40")
    print("=" * 50)
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        ip_address = sys.argv[1]
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 4370
        
        print(f"🎯 Probando IP específica: {ip_address}:{port}")
        
        if test_basic_connectivity(ip_address, port):
            test_device_connection(ip_address, port)
    else:
        print("🔍 Escaneando red local en busca de dispositivos ZKTeco...")
        found_device = test_local_network()
        
        if found_device:
            print(f"\n✅ Dispositivo encontrado en: {found_device}")
            print("💡 Puedes usar esta IP en la aplicación:")
            print(f"   python gui_app.py")
            print(f"   python simple_connector.py {found_device}")
        else:
            print("\n❌ No se encontraron dispositivos ZKTeco en la red")
            print("💡 Verifica que:")
            print("   - El dispositivo esté encendido")
            print("   - Esté conectado por Ethernet")
            print("   - La IP esté configurada correctamente")
            print("   - No haya firewall bloqueando el puerto 4370")

if __name__ == "__main__":
    main() 