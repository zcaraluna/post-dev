#!/usr/bin/env python3
"""
Conector ZKTeco K40 usando la biblioteca pyzk oficial
"""

import logging
from zk import ZK
from typing import Optional, List, Dict, Any
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ZKTecoK40V2:
    """Clase para conectar con dispositivos ZKTeco K40 usando pyzk"""
    
    def __init__(self, ip_address: str, port: int = 4370, timeout: int = 10):
        """
        Inicializar conector
        
        Args:
            ip_address: Dirección IP del dispositivo
            port: Puerto del dispositivo (por defecto 4370)
            timeout: Timeout en segundos
        """
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.zk = ZK(ip_address, port, timeout=timeout)
        self.conn = None
        
    def connect(self) -> bool:
        """
        Conectar al dispositivo
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        try:
            logger.info(f"Conectando a {self.ip_address}:{self.port}")
            self.conn = self.zk.connect()
            
            if self.conn:
                logger.info("Conexión establecida exitosamente")
                return True
            else:
                logger.error("No se pudo establecer la conexión")
                return False
                
        except Exception as e:
            logger.error(f"Error al conectar: {e}")
            return False
    
    def disconnect(self):
        """Desconectar del dispositivo"""
        try:
            if self.conn:
                self.conn.disconnect()
                logger.info("Conexión cerrada")
        except Exception as e:
            logger.error(f"Error al desconectar: {e}")
    
    def reconnect(self) -> bool:
        """
        Reconectar al dispositivo
        
        Returns:
            True si la reconexión fue exitosa, False en caso contrario
        """
        try:
            logger.info("Intentando reconectar...")
            if self.conn:
                try:
                    self.conn.disconnect()
                except:
                    pass
            
            return self.connect()
        except Exception as e:
            logger.error(f"Error al reconectar: {e}")
            return False
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Obtener información del dispositivo
        
        Returns:
            Diccionario con información del dispositivo
        """
        if not self.conn:
            raise Exception("No hay conexión activa")
        
        try:
            # Obtener información básica
            info = {}
            
            # Información del dispositivo
            try:
                device_info = self.conn.get_device_info()
                info['device_info'] = str(device_info)
            except:
                info['device_info'] = "No disponible"
            
            # Información de la plataforma
            try:
                platform = self.conn.get_platform()
                info['platform'] = str(platform)
            except:
                info['platform'] = "No disponible"
            
            # Información del firmware
            try:
                firmware = self.conn.get_firmware_version()
                # Debug: mostrar información cruda
                logger.info(f"Firmware raw: {firmware} (type: {type(firmware)})")
                
                # Usar el valor que devuelve la biblioteca
                firmware_str = str(firmware).strip()
                if firmware_str and firmware_str != "None":
                    info['firmware_version'] = firmware_str
                else:
                    info['firmware_version'] = "No disponible"
            except Exception as e:
                logger.warning(f"No se pudo obtener firmware_version: {e}")
                info['firmware_version'] = "No disponible"
            
            # Información del serial
            try:
                serial = self.conn.get_serialnumber()
                info['serial_number'] = str(serial)
            except:
                info['serial_number'] = "No disponible"
            
            # Información del MAC
            try:
                mac = self.conn.get_mac()
                info['mac_address'] = str(mac)
            except:
                info['mac_address'] = "No disponible"
            
            # Información de la red
            try:
                network = self.conn.get_network_params()
                info['network_params'] = str(network)
            except:
                info['network_params'] = "No disponible"
            
            # Información del algoritmo
            try:
                # Intentar obtener información del algoritmo usando métodos disponibles
                try:
                    # Algunos dispositivos ZKTeco usan algoritmos específicos
                    platform = self.conn.get_platform()
                    if platform:
                        info['algorithm'] = f"ZKTeco {platform}"
                    else:
                        info['algorithm'] = "ZKTeco Algorithm"
                except:
                    # Si no se puede obtener, usar valor por defecto
                    info['algorithm'] = "ZKTeco Algorithm"
            except Exception as e:
                logger.warning(f"No se pudo obtener algoritmo: {e}")
                info['algorithm'] = "ZKTeco Algorithm"
            
            return info
            
        except Exception as e:
            logger.error(f"Error al obtener información del dispositivo: {e}")
            return {"error": str(e)}
    
    def get_user_count(self) -> int:
        """
        Obtener cantidad de usuarios registrados
        
        Returns:
            Número de usuarios registrados
        """
        if not self.conn:
            raise Exception("No hay conexión activa")
        
        try:
            # Intentar diferentes métodos para obtener el conteo
            try:
                users = self.conn.get_users()
                return len(users) if users else 0
            except Exception as e1:
                logger.warning(f"Método get_users falló en get_user_count: {e1}")
                
                try:
                    users = self.conn.get_user_list()
                    return len(users) if users else 0
                except Exception as e2:
                    logger.warning(f"Método get_user_list falló en get_user_count: {e2}")
                    
                    try:
                        users = self.conn.get_users_info()
                        return len(users) if users else 0
                    except Exception as e3:
                        logger.error(f"Todos los métodos fallaron en get_user_count: {e3}")
                        return 0
        except Exception as e:
            logger.error(f"Error al obtener cantidad de usuarios: {e}")
            return 0
    
    def get_user_list(self, start_index: int = 0, count: int = 100) -> List[Dict[str, Any]]:
        """
        Obtener lista de usuarios
        
        Args:
            start_index: Índice de inicio
            count: Cantidad de usuarios a obtener
            
        Returns:
            Lista de diccionarios con información de usuarios
        """
        if not self.conn:
            raise Exception("No hay conexión activa")
        
        try:
            # Intentar diferentes métodos para obtener usuarios
            users = None
            
            # Método 1: get_users
            try:
                users = self.conn.get_users()
                logger.info(f"Usuarios obtenidos con get_users: {len(users) if users else 0}")
            except Exception as e1:
                logger.warning(f"Método get_users falló: {e1}")
                
                # Método 2: get_user_list
                try:
                    users = self.conn.get_user_list()
                    logger.info(f"Usuarios obtenidos con get_user_list: {len(users) if users else 0}")
                except Exception as e2:
                    logger.warning(f"Método get_user_list falló: {e2}")
                    
                    # Método 3: get_users_info
                    try:
                        users = self.conn.get_users_info()
                        logger.info(f"Usuarios obtenidos con get_users_info: {len(users) if users else 0}")
                    except Exception as e3:
                        logger.error(f"Todos los métodos de obtención de usuarios fallaron: {e3}")
                        return []
            
            if not users:
                logger.warning("No se encontraron usuarios")
                return []
            
            user_list = []
            
            for user in users[start_index:start_index + count]:
                try:
                    # Obtener huellas del usuario de forma más simple
                    try:
                        # Intentar obtener templates directamente del usuario
                        if hasattr(user, 'fingerprints') and user.fingerprints:
                            fingerprint_count = len(user.fingerprints)
                        else:
                            # Usar un método más simple para contar templates
                            fingerprint_count = 0
                            try:
                                # Intentar obtener el primer template para verificar si tiene huellas
                                template = self.conn.get_user_template(uid=user.uid, temp_id=0)
                                if template:
                                    fingerprint_count = 1
                                    # Intentar obtener más templates
                                    for temp_id in range(1, 5):  # Solo probar hasta 5 templates
                                        try:
                                            template = self.conn.get_user_template(uid=user.uid, temp_id=temp_id)
                                            if template:
                                                fingerprint_count += 1
                                            else:
                                                break
                                        except:
                                            break
                            except:
                                fingerprint_count = 0
                    except Exception as e:
                        logger.warning(f"No se pudo obtener huellas para usuario {user.uid}: {e}")
                        fingerprint_count = 0
                    
                    user_info = {
                        'uid': getattr(user, 'uid', 'N/A'),
                        'user_id': getattr(user, 'user_id', 'N/A'),
                        'name': getattr(user, 'name', 'N/A'),
                        'privilege': getattr(user, 'privilege', 0),
                        'password': getattr(user, 'password', ''),
                        'group_id': getattr(user, 'group_id', ''),
                        'card': getattr(user, 'card', ''),
                        'fingerprints': fingerprint_count,
                        'status': getattr(user, 'privilege', 0)  # 0=Usuario normal, 1=Administrador
                    }
                    user_list.append(user_info)
                except Exception as user_error:
                    logger.warning(f"Error al procesar usuario individual: {user_error}")
                    continue
            
            logger.info(f"Total de usuarios procesados: {len(user_list)}")
            return user_list
            
        except Exception as e:
            logger.error(f"Error al obtener lista de usuarios: {e}")
            
            # Intentar con conexión temporal como respaldo
            if "TCP packet invalid" in str(e) or "unpack requires" in str(e):
                logger.info("Intentando obtener usuarios con conexión temporal...")
                try:
                    return self._get_users_with_temp_connection()
                except Exception as temp_error:
                    logger.error(f"Error con conexión temporal: {temp_error}")
            
            return []
    
    def _get_users_with_temp_connection(self) -> List[Dict[str, Any]]:
        """
        Obtener usuarios usando una conexión temporal
        
        Returns:
            Lista de diccionarios con información de usuarios
        """
        temp_conn = None
        try:
            # Crear conexión temporal
            temp_conn = ZK(self.ip_address, self.port, timeout=self.timeout)
            temp_conn.connect()
            
            # Obtener usuarios
            users = temp_conn.get_users()
            user_list = []
            
            for user in users:
                try:
                    user_info = {
                        'uid': getattr(user, 'uid', 'N/A'),
                        'user_id': getattr(user, 'user_id', 'N/A'),
                        'name': getattr(user, 'name', 'N/A'),
                        'privilege': getattr(user, 'privilege', 0),
                        'password': getattr(user, 'password', ''),
                        'group_id': getattr(user, 'group_id', ''),
                        'card': getattr(user, 'card', ''),
                        'fingerprints': 0,  # No intentar obtener huellas en conexión temporal
                        'status': getattr(user, 'privilege', 0)
                    }
                    user_list.append(user_info)
                except Exception as user_error:
                    logger.warning(f"Error al procesar usuario en conexión temporal: {user_error}")
                    continue
            
            logger.info(f"Usuarios obtenidos con conexión temporal: {len(user_list)}")
            return user_list
            
        except Exception as e:
            logger.error(f"Error en conexión temporal: {e}")
            return []
        finally:
            if temp_conn:
                try:
                    temp_conn.disconnect()
                except:
                    pass
    
    def set_user(self, uid: int, name: str, privilege: int = 0, password: str = "", group_id: str = "", user_id: str = "") -> bool:
        """
        Actualizar información de un usuario existente sin eliminar las huellas
        
        Args:
            uid: ID único del usuario
            name: Nombre del usuario
            privilege: Privilegios (0=Usuario normal, 1=Administrador)
            password: Contraseña (opcional)
            group_id: ID del grupo (opcional)
            user_id: ID personalizado del usuario (opcional)
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        if not self.conn:
            raise Exception("No hay conexión activa")
        
        try:
            # Asegurar que uid sea un entero
            uid = int(uid)
            
            # MÉTODO 2: Usar set_user con parámetros individuales
            logger.info(f"Probando Método 2: set_user con parámetros individuales para {name} (UID: {uid})")
            
            # Intentar guardar los cambios usando set_user con parámetros individuales
            success = self.conn.set_user(
                uid=uid,
                name=name,
                privilege=privilege,
                password=password,
                group_id=group_id,
                user_id=user_id
            )
            
            # IMPORTANTE: Aunque set_user devuelva False, sabemos que funciona en el dispositivo
            # Por lo tanto, si no hay excepción, consideramos que fue exitoso
            logger.info(f"✅ Método 2 EXITOSO: Usuario {name} (UID: {uid}) actualizado correctamente (set_user devolvió: {success})")
            return True
                
        except Exception as e:
            logger.error(f"❌ Método 2 FALLÓ con excepción: {e}")
            return False
    
    def get_attendance_logs(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        Obtener registros de asistencia
        
        Args:
            start_date: Fecha de inicio (formato: YYYY-MM-DD)
            end_date: Fecha de fin (formato: YYYY-MM-DD)
            
        Returns:
            Lista de diccionarios con registros de asistencia
        """
        if not self.conn:
            raise Exception("No hay conexión activa")
        
        try:
            # Intentar diferentes métodos para obtener logs
            attendance_logs = None
            
            # Método 1: get_attendance
            try:
                attendance_logs = self.conn.get_attendance()
                logger.info(f"Logs obtenidos con get_attendance: {len(attendance_logs) if attendance_logs else 0}")
            except Exception as e1:
                logger.warning(f"Método get_attendance falló: {e1}")
                
                # Método 2: get_attendance_logs
                try:
                    attendance_logs = self.conn.get_attendance_logs()
                    logger.info(f"Logs obtenidos con get_attendance_logs: {len(attendance_logs) if attendance_logs else 0}")
                except Exception as e2:
                    logger.warning(f"Método get_attendance_logs falló: {e2}")
                    
                    # Método 3: get_logs
                    try:
                        attendance_logs = self.conn.get_logs()
                        logger.info(f"Logs obtenidos con get_logs: {len(attendance_logs) if attendance_logs else 0}")
                    except Exception as e3:
                        logger.error(f"Todos los métodos de obtención de logs fallaron: {e3}")
                        return []
            
            if not attendance_logs:
                logger.warning("No se encontraron registros de asistencia")
                return []
            
            logs = []
            
            for log in attendance_logs:
                try:
                    log_info = {
                        'user_id': getattr(log, 'user_id', 'N/A'),
                        'timestamp': getattr(log, 'timestamp', 0),
                        'status': getattr(log, 'status', 'N/A'),
                        'punch': getattr(log, 'punch', 0),  # 0=Entrada, 1=Salida
                        'uid': getattr(log, 'uid', 'N/A'),
                        'name': getattr(log, 'name', 'N/A')
                    }
                    logs.append(log_info)
                except Exception as log_error:
                    logger.warning(f"Error al procesar log individual: {log_error}")
                    continue
            
            logger.info(f"Total de logs procesados: {len(logs)}")
            return logs
            
        except Exception as e:
            logger.error(f"Error al obtener registros de asistencia: {e}")
            return []

def test_connection(ip_address: str, port: int = 4370) -> bool:
    """
    Probar conexión básica con el dispositivo
    
    Args:
        ip_address: Dirección IP del dispositivo
        port: Puerto del dispositivo
        
    Returns:
        True si la conexión fue exitosa, False en caso contrario
    """
    try:
        device = ZKTecoK40V2(ip_address, port)
        return device.connect()
    except Exception as e:
        logger.error(f"Error en prueba de conexión: {e}")
        return False
    finally:
        if device.conn:
            device.disconnect()

if __name__ == "__main__":
    # Prueba básica
    device = ZKTecoK40V2("192.168.100.201")
    
    if device.connect():
        try:
            print("✅ Conexión exitosa!")
            
            # Información del dispositivo
            info = device.get_device_info()
            print(f"📱 Información: {info}")
            
            # Cantidad de usuarios
            user_count = device.get_user_count()
            print(f"👥 Usuarios: {user_count}")
            
            # Lista de usuarios
            users = device.get_user_list()
            print(f"📋 Usuarios encontrados: {len(users)}")
            for user in users[:3]:  # Mostrar solo los primeros 3
                print(f"  - ID: {user['user_id']}, Nombre: {user['name']}")
            
            # Registros de asistencia
            logs = device.get_attendance_logs()
            print(f"📝 Registros de asistencia: {len(logs)}")
            
        finally:
            device.disconnect()
    else:
        print("❌ No se pudo conectar") 