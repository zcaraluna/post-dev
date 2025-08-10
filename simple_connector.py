#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para conectar con dispositivos ZKTeco K40
Uso: python simple_connector.py [IP] [PUERTO]
"""

import sys
import argparse
from zkteco_connector_v2 import ZKTecoK40V2 as ZKTecoK40, test_connection

def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(description='Conectar con dispositivo ZKTeco K40')
    parser.add_argument('ip', nargs='?', default='192.168.1.100', 
                       help='Dirección IP del dispositivo (default: 192.168.1.100)')
    parser.add_argument('port', nargs='?', type=int, default=4370,
                       help='Puerto del dispositivo (default: 4370)')
    parser.add_argument('--users', action='store_true',
                       help='Mostrar lista de usuarios')
    parser.add_argument('--logs', action='store_true',
                       help='Mostrar registros de asistencia')
    parser.add_argument('--info', action='store_true',
                       help='Mostrar información del dispositivo')
    
    args = parser.parse_args()
    
    print(f"Conectando a {args.ip}:{args.port}...")
    
    # Probar conexión
    if not test_connection(args.ip, args.port):
        print("❌ No se pudo conectar al dispositivo")
        print("Verifica:")
        print("  1. La dirección IP es correcta")
        print("  2. El dispositivo está encendido y conectado")
        print("  3. No hay firewall bloqueando la conexión")
        sys.exit(1)
    
    print("✅ Conexión exitosa")
    
    # Crear dispositivo
    device = ZKTecoK40(args.ip, args.port)
    
    if not device.connect():
        print("❌ Error al establecer sesión")
        sys.exit(1)
    
    try:
        # Mostrar información del dispositivo
        if args.info or not (args.users or args.logs):
            print("\n📋 INFORMACIÓN DEL DISPOSITIVO:")
            print("=" * 40)
            info = device.get_device_info()
            if info:
                for key, value in info.items():
                    print(f"{key.replace('_', ' ').title()}: {value}")
            else:
                print("No se pudo obtener información del dispositivo")
        
        # Mostrar cantidad de usuarios
        user_count = device.get_user_count()
        print(f"\n👥 USUARIOS REGISTRADOS: {user_count}")
        
        # Mostrar lista de usuarios si se solicita
        if args.users and user_count > 0:
            print("\n📝 LISTA DE USUARIOS:")
            print("=" * 80)
            print(f"{'ID':<6} {'Nombre':<30} {'Rol':<8} {'Grupo':<8} {'Huellas':<8} {'Estado':<8}")
            print("-" * 80)
            
            users = device.get_user_list(0, min(user_count, 3000), include_fingerprints=False)  # Máximo 3000 usuarios sin huellas
            for user in users:
                status = "Activo" if user['status'] == 1 else "Inactivo"
                print(f"{user['user_id']:<6} {user['name']:<30} {user['role']:<8} "
                      f"{user['group']:<8} {user['fingerprint_count']:<8} {status:<8}")
        
        # Mostrar registros de asistencia si se solicita
        if args.logs:
            print("\n📊 REGISTROS DE ASISTENCIA (Últimos 50):")
            print("=" * 80)
            print(f"{'Usuario':<8} {'Fecha/Hora':<20} {'Tipo':<12} {'Estado':<8}")
            print("-" * 80)
            
            logs = device.get_attendance_logs()
            # Mostrar solo los últimos 50 registros
            recent_logs = logs[-50:] if len(logs) > 50 else logs
            
            for log in recent_logs:
                from datetime import datetime
                timestamp = datetime.fromtimestamp(log['timestamp'])
                date_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                
                verification_types = {
                    0: "Contraseña",
                    1: "Huella",
                    2: "Tarjeta",
                    3: "Rostro"
                }
                verification_type = verification_types.get(log['verification_type'], "Desconocido")
                status = "Entrada" if log['status'] == 1 else "Salida"
                
                print(f"{log['user_id']:<8} {date_str:<20} {verification_type:<12} {status:<8}")
        
        # Si no se especificaron opciones, mostrar resumen
        if not (args.users or args.logs or args.info):
            print("\n💡 USO:")
            print("  python simple_connector.py [IP] [PUERTO] --users    # Ver usuarios")
            print("  python simple_connector.py [IP] [PUERTO] --logs     # Ver registros")
            print("  python simple_connector.py [IP] [PUERTO] --info     # Ver información")
            print("  python simple_connector.py [IP] [PUERTO] --users --logs  # Ver todo")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    finally:
        device.disconnect()
        print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    main() 