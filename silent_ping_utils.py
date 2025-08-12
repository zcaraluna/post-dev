#!/usr/bin/env python3
"""
Utilidades para ping silencioso sin mostrar ventanas de CMD
"""

import subprocess
import platform
import socket
import logging
from typing import Optional

# Configurar logging
logger = logging.getLogger(__name__)

def silent_ping(host: str, timeout: int = 3) -> bool:
    """
    Realizar ping silencioso sin mostrar ventanas de CMD
    
    Args:
        host: Dirección IP o hostname a hacer ping
        timeout: Timeout en segundos
        
    Returns:
        True si el host responde, False en caso contrario
    """
    try:
        # Detectar el sistema operativo
        system = platform.system().lower()
        
        if system == "windows":
            # En Windows, usar subprocess con CREATE_NO_WINDOW para ocultar la ventana
            if hasattr(subprocess, 'CREATE_NO_WINDOW'):
                # Windows 10/11
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', str(timeout * 1000), host],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                # Windows anterior - crear STARTUPINFO para ocultar ventana
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', str(timeout * 1000), host],
                    capture_output=True,
                    text=True,
                    startupinfo=startupinfo
                )
        else:
            # En Linux/Mac
            result = subprocess.run(
                ['ping', '-c', '1', '-W', str(timeout), host],
                capture_output=True,
                text=True
            )
        
        # Verificar si el ping fue exitoso
        return result.returncode == 0
        
    except Exception as e:
        logger.warning(f"Error en ping silencioso a {host}: {e}")
        return False

def test_port_connectivity(host: str, port: int, timeout: int = 3) -> bool:
    """
    Probar conectividad a un puerto específico
    
    Args:
        host: Dirección IP o hostname
        port: Puerto a probar
        timeout: Timeout en segundos
        
    Returns:
        True si el puerto está abierto, False en caso contrario
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        return result == 0
        
    except Exception as e:
        logger.warning(f"Error al probar puerto {port} en {host}: {e}")
        return False

def test_network_connectivity(ip_address: str, port: int = 4370) -> bool:
    """
    Probar conectividad de red de forma silenciosa
    
    Args:
        ip_address: Dirección IP del dispositivo
        port: Puerto del dispositivo
        
    Returns:
        True si hay conectividad, False en caso contrario
    """
    try:
        # Primero hacer ping silencioso
        if not silent_ping(ip_address):
            logger.warning(f"No hay conectividad de red con {ip_address}")
            return False
        
        # Si el ping es exitoso, intentar conectar al puerto
        if not test_port_connectivity(ip_address, port):
            logger.warning(f"Puerto {port} no está abierto en {ip_address}")
            return False
        
        logger.info(f"Conectividad de red exitosa con {ip_address}:{port}")
        return True
            
    except Exception as e:
        logger.error(f"Error al probar conectividad de red: {e}")
        return False

def check_device_connectivity(ip_address: str = "192.168.100.201", port: int = 4370) -> bool:
    """
    Verificar conectividad con el dispositivo de forma completamente silenciosa
    
    Args:
        ip_address: Dirección IP del dispositivo (por defecto 192.168.100.201)
        port: Puerto del dispositivo (por defecto 4370)
        
    Returns:
        True si hay conectividad, False en caso contrario
    """
    return test_network_connectivity(ip_address, port)

def get_network_info(ip_address: str) -> dict:
    """
    Obtener información de red de forma silenciosa
    
    Args:
        ip_address: Dirección IP a analizar
        
    Returns:
        Diccionario con información de red
    """
    info = {
        'ping_successful': False,
        'port_open': False,
        'response_time': None,
        'error': None
    }
    
    try:
        # Probar ping
        info['ping_successful'] = silent_ping(ip_address)
        
        # Si el ping es exitoso, probar puerto
        if info['ping_successful']:
            info['port_open'] = test_port_connectivity(ip_address, 4370)
            
    except Exception as e:
        info['error'] = str(e)
    
    return info

if __name__ == "__main__":
    # Prueba de las funciones
    test_ip = "192.168.100.201"
    
    print(f"Probando conectividad con {test_ip}...")
    
    # Ping silencioso
    ping_result = silent_ping(test_ip)
    print(f"Ping silencioso: {'✅ Exitoso' if ping_result else '❌ Falló'}")
    
    # Conectividad de red
    network_result = test_network_connectivity(test_ip, 4370)
    print(f"Conectividad de red: {'✅ Exitoso' if network_result else '❌ Falló'}")
    
    # Información detallada
    info = get_network_info(test_ip)
    print(f"Información de red: {info}")


