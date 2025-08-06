#!/usr/bin/env python3
"""
Script de línea de comandos para dispositivos ZKTeco K40 usando pyzk
"""

import sys
import argparse
from zkteco_connector_v2 import ZKTecoK40V2, test_connection

def main():
    parser = argparse.ArgumentParser(description='Conectar con dispositivo ZKTeco K40')
    parser.add_argument('ip', nargs='?', default='192.168.100.201', help='Dirección IP del dispositivo')
    parser.add_argument('port', nargs='?', type=int, default=4370, help='Puerto del dispositivo')
    parser.add_argument('--users', action='store_true', help='Mostrar lista de usuarios')
    parser.add_argument('--logs', action='store_true', help='Mostrar registros de asistencia')
    parser.add_argument('--info', action='store_true', help='Mostrar información del dispositivo')
    args = parser.parse_args()

    print(f"Conectando a {args.ip}:{args.port}...")
    
    # Probar conexión básica
    if not test_connection(args.ip, args.port):
        print("❌ No se pudo conectar al dispositivo")
        print("Verifica:")
        print("  1. La dirección IP es correcta")
        print("  2. El dispositivo está encendido y conectado")
        print("  3. No hay firewall bloqueando la conexión")
        return

    # Conectar al dispositivo
    device = ZKTecoK40V2(args.ip, args.port)
    
    try:
        if device.connect():
            print("✅ Conexión establecida exitosamente")
            
            # Mostrar información del dispositivo
            if args.info or not (args.users or args.logs):
                print("\n📱 INFORMACIÓN DEL DISPOSITIVO:")
                print("=" * 40)
                info = device.get_device_info()
                for key, value in info.items():
                    if key == 'network_params':
                        print(f"Configuración de Red: {value}")
                    else:
                        print(f"{key.replace('_', ' ').title()}: {value}")
            
            # Obtener cantidad de usuarios
            user_count = device.get_user_count()
            print(f"\n👥 USUARIOS REGISTRADOS: {user_count}")
            
            # Mostrar lista de usuarios
            if args.users and user_count > 0:
                print("\n📋 LISTA DE USUARIOS:")
                print("=" * 40)
                print(f"{'ID':<5} {'Nombre':<20} {'Privilegio':<10} {'Tarjeta':<10} {'Huellas':<8} {'Estado':<8}")
                print("-" * 70)
                
                users = device.get_user_list()
                for user in users:
                    privilege = "Admin" if user['privilege'] == 1 else "Usuario"
                    status = "Activo" if user['status'] == 0 else "Inactivo"
                    card = user['card'] if user['card'] else "N/A"
                    
                    print(f"{user['user_id']:<5} {user['name']:<20} {privilege:<10} {card:<10} {user['fingerprints']:<8} {status:<8}")
            
            # Mostrar registros de asistencia
            if args.logs:
                print("\n📝 REGISTROS DE ASISTENCIA:")
                print("=" * 50)
                print(f"{'Usuario':<8} {'Fecha/Hora':<20} {'Tipo':<8} {'Estado':<6}")
                print("-" * 50)
                
                logs = device.get_attendance_logs()
                for log in logs:
                    timestamp = log['timestamp'].strftime("%Y-%m-%d %H:%M:%S") if log['timestamp'] else "N/A"
                    punch_type = "Entrada" if log['punch'] == 0 else "Salida"
                    status = "OK" if log['status'] == 1 else "Error"
                    
                    print(f"{log['user_id']:<8} {timestamp:<20} {punch_type:<8} {status:<6}")
                
                print(f"\nTotal de registros: {len(logs)}")
            
            # Si no se especificaron opciones, mostrar resumen
            if not (args.users or args.logs or args.info):
                print("\n💡 USO:")
                print("  python simple_connector_v2.py [IP] [PUERTO] [OPCIONES]")
                print("\nOPCIONES:")
                print("  --info     Mostrar información del dispositivo")
                print("  --users    Mostrar lista de usuarios")
                print("  --logs     Mostrar registros de asistencia")
                print("\nEJEMPLOS:")
                print("  python simple_connector_v2.py 192.168.100.201 --info")
                print("  python simple_connector_v2.py 192.168.100.201 --users --logs")
                print("  python simple_connector_v2.py 192.168.100.201 --users --logs --info")
        
        else:
            print("❌ No se pudo establecer la conexión")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        device.disconnect()

if __name__ == "__main__":
    main() 