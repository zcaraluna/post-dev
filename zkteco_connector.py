#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conector para dispositivo biométrico ZKTeco K40
Permite obtener información de usuarios registrados
"""

import socket
import struct
import time
from typing import List, Dict, Optional, Tuple
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ZKTecoK40:
    """Clase para manejar la comunicación con dispositivos ZKTeco K40"""
    
    def __init__(self, ip_address: str, port: int = 4370, timeout: int = 5):
        """
        Inicializar conexión con dispositivo ZKTeco
        
        Args:
            ip_address: Dirección IP del dispositivo
            port: Puerto de comunicación (por defecto 4370)
            timeout: Tiempo de espera en segundos
        """
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.session_id = 0
        self.reply_id = 0
        
    def connect(self) -> bool:
        """
        Establecer conexión con el dispositivo
        
        Returns:
            bool: True si la conexión fue exitosa
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.ip_address, self.port))
            
            # Enviar comando de conexión
            cmd = self._create_command(0x1000, b'')
            response = self._send_command(cmd)
            
            if response and len(response) >= 8:
                self.session_id = struct.unpack('<I', response[4:8])[0]
                logger.info(f"Conexión exitosa con {self.ip_address}:{self.port}")
                return True
            else:
                logger.error("No se pudo establecer la conexión")
                return False
                
        except Exception as e:
            logger.error(f"Error al conectar: {e}")
            return False
    
    def disconnect(self):
        """Cerrar conexión con el dispositivo"""
        if self.socket:
            self.socket.close()
            self.socket = None
            logger.info("Conexión cerrada")
    
    def get_device_info(self) -> Dict[str, str]:
        """
        Obtener información del dispositivo
        
        Returns:
            Dict con información del dispositivo
        """
        try:
            cmd = self._create_command(0x0001, b'')
            response = self._send_command(cmd)
            
            if response and len(response) >= 72:
                info = {
                    'firmware_version': response[8:16].decode('utf-8', errors='ignore').strip('\x00'),
                    'serial_number': response[16:32].decode('utf-8', errors='ignore').strip('\x00'),
                    'platform': response[32:48].decode('utf-8', errors='ignore').strip('\x00'),
                    'fingerprint_algorithm': response[48:56].decode('utf-8', errors='ignore').strip('\x00'),
                    'face_algorithm': response[56:64].decode('utf-8', errors='ignore').strip('\x00'),
                    'device_name': response[64:72].decode('utf-8', errors='ignore').strip('\x00')
                }
                return info
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error al obtener información del dispositivo: {e}")
            return {}
    
    def get_user_count(self) -> int:
        """
        Obtener cantidad total de usuarios registrados
        
        Returns:
            int: Número de usuarios
        """
        try:
            cmd = self._create_command(0x0002, b'')
            response = self._send_command(cmd)
            
            if response and len(response) >= 8:
                count = struct.unpack('<I', response[4:8])[0]
                return count
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Error al obtener cantidad de usuarios: {e}")
            return 0
    
    def get_user_list(self, start_index: int = 0, count: int = 100) -> List[Dict]:
        """
        Obtener lista de usuarios registrados
        
        Args:
            start_index: Índice de inicio
            count: Cantidad de usuarios a obtener
            
        Returns:
            Lista de diccionarios con información de usuarios
        """
        try:
            data = struct.pack('<II', start_index, count)
            cmd = self._create_command(0x0003, data)
            response = self._send_command(cmd)
            
            users = []
            if response and len(response) >= 8:
                user_count = struct.unpack('<I', response[4:8])[0]
                offset = 8
                
                for i in range(user_count):
                    if offset + 72 <= len(response):
                        user_data = response[offset:offset+72]
                        user = {
                            'user_id': struct.unpack('<I', user_data[0:4])[0],
                            'name': user_data[4:36].decode('utf-8', errors='ignore').strip('\x00'),
                            'password': user_data[36:44].decode('utf-8', errors='ignore').strip('\x00'),
                            'role': struct.unpack('<I', user_data[44:48])[0],
                            'group': struct.unpack('<I', user_data[48:52])[0],
                            'card_number': struct.unpack('<I', user_data[52:56])[0],
                            'fingerprint_count': struct.unpack('<I', user_data[56:60])[0],
                            'face_count': struct.unpack('<I', user_data[60:64])[0],
                            'password_count': struct.unpack('<I', user_data[64:68])[0],
                            'status': struct.unpack('<I', user_data[68:72])[0]
                        }
                        users.append(user)
                        offset += 72
            
            return users
            
        except Exception as e:
            logger.error(f"Error al obtener lista de usuarios: {e}")
            return []
    
    def get_attendance_logs(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        Obtener registros de asistencia
        
        Args:
            start_date: Fecha de inicio (YYYY-MM-DD)
            end_date: Fecha de fin (YYYY-MM-DD)
            
        Returns:
            Lista de registros de asistencia
        """
        try:
            # Convertir fechas a timestamp si se proporcionan
            start_timestamp = 0
            end_timestamp = int(time.time())
            
            if start_date:
                start_timestamp = int(time.mktime(time.strptime(start_date, '%Y-%m-%d')))
            if end_date:
                end_timestamp = int(time.mktime(time.strptime(end_date, '%Y-%m-%d')))
            
            data = struct.pack('<II', start_timestamp, end_timestamp)
            cmd = self._create_command(0x0004, data)
            response = self._send_command(cmd)
            
            logs = []
            if response and len(response) >= 8:
                log_count = struct.unpack('<I', response[4:8])[0]
                offset = 8
                
                for i in range(log_count):
                    if offset + 16 <= len(response):
                        log_data = response[offset:offset+16]
                        log = {
                            'user_id': struct.unpack('<I', log_data[0:4])[0],
                            'timestamp': struct.unpack('<I', log_data[4:8])[0],
                            'status': struct.unpack('<I', log_data[8:12])[0],
                            'verification_type': struct.unpack('<I', log_data[12:16])[0]
                        }
                        logs.append(log)
                        offset += 16
            
            return logs
            
        except Exception as e:
            logger.error(f"Error al obtener registros de asistencia: {e}")
            return []
    
    def _create_command(self, command: int, data: bytes) -> bytes:
        """
        Crear comando para enviar al dispositivo
        
        Args:
            command: Código del comando
            data: Datos del comando
            
        Returns:
            bytes: Comando formateado
        """
        self.reply_id += 1
        session_id = self.session_id if self.session_id else 0
        
        # Estructura del comando: [command][checksum][session_id][reply_id][data]
        cmd = struct.pack('<IIII', command, 0, session_id, self.reply_id) + data
        
        # Calcular checksum
        checksum = sum(cmd) & 0xFFFFFFFF
        cmd = struct.pack('<IIII', command, checksum, session_id, self.reply_id) + data
        
        return cmd
    
    def _send_command(self, command: bytes) -> Optional[bytes]:
        """
        Enviar comando al dispositivo
        
        Args:
            command: Comando a enviar
            
        Returns:
            bytes: Respuesta del dispositivo o None si hay error
        """
        try:
            if not self.socket:
                return None
            
            self.socket.send(command)
            response = self.socket.recv(1024)
            
            if len(response) >= 8:
                # Verificar checksum
                received_checksum = struct.unpack('<I', response[4:8])[0]
                calculated_checksum = sum(response[:4] + response[8:]) & 0xFFFFFFFF
                
                if received_checksum == calculated_checksum:
                    return response
                else:
                    logger.warning("Checksum incorrecto en la respuesta")
                    return None
            else:
                logger.warning("Respuesta demasiado corta")
                return None
                
        except socket.timeout:
            logger.error("Timeout al enviar comando")
            return None
        except Exception as e:
            logger.error(f"Error al enviar comando: {e}")
            return None

def test_connection(ip_address: str, port: int = 4370) -> bool:
    """
    Probar conexión con el dispositivo
    
    Args:
        ip_address: Dirección IP del dispositivo
        port: Puerto de comunicación
        
    Returns:
        bool: True si la conexión es exitosa
    """
    device = ZKTecoK40(ip_address, port)
    try:
        return device.connect()
    finally:
        device.disconnect()

if __name__ == "__main__":
    # Ejemplo de uso
    device_ip = "192.168.1.100"  # Cambiar por la IP real del dispositivo
    
    print("Probando conexión con dispositivo ZKTeco K40...")
    if test_connection(device_ip):
        print("✓ Conexión exitosa")
        
        device = ZKTecoK40(device_ip)
        if device.connect():
            try:
                # Obtener información del dispositivo
                info = device.get_device_info()
                print(f"\nInformación del dispositivo:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
                
                # Obtener cantidad de usuarios
                user_count = device.get_user_count()
                print(f"\nCantidad de usuarios registrados: {user_count}")
                
                # Obtener lista de usuarios (primeros 10)
                users = device.get_user_list(0, 10)
                print(f"\nPrimeros {len(users)} usuarios:")
                for user in users:
                    print(f"  ID: {user['user_id']}, Nombre: {user['name']}")
                
            finally:
                device.disconnect()
    else:
        print("✗ No se pudo conectar al dispositivo")
        print("Verifica:")
        print("  1. La dirección IP es correcta")
        print("  2. El dispositivo está encendido y conectado")
        print("  3. No hay firewall bloqueando la conexión")
        print("  4. El puerto 4370 está abierto") 