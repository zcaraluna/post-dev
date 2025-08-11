#!/usr/bin/env python3
"""
Utilidades para verificación de privilegios en el sistema
"""

from database import verificar_privilegio
from tkinter import messagebox

def verificar_permiso(user_data, permiso, mostrar_error=True):
    """
    Verificar si un usuario tiene un permiso específico
    
    Args:
        user_data (dict): Datos del usuario
        permiso (str): Permiso a verificar
        mostrar_error (bool): Si mostrar mensaje de error
        
    Returns:
        bool: True si tiene el permiso, False en caso contrario
    """
    if not user_data:
        if mostrar_error:
            messagebox.showerror("Error", "No se pudo verificar los permisos del usuario")
        return False
    
    rol = user_data.get('rol', 'USUARIO')
    
    # SUPERADMIN siempre tiene todos los permisos
    if rol == 'SUPERADMIN':
        return True
    
    # Verificar privilegio específico
    tiene_permiso = verificar_privilegio(rol, permiso)
    
    if not tiene_permiso and mostrar_error:
        messagebox.showerror(
            "Acceso Denegado", 
            f"No tiene permisos para realizar esta acción.\n\n"
            f"Permiso requerido: {permiso}\n"
            f"Su rol: {rol}\n\n"
            "Contacte al administrador del sistema."
        )
    
    return tiene_permiso

def verificar_permiso_silencioso(user_data, permiso):
    """
    Verificar permiso sin mostrar mensajes de error
    
    Args:
        user_data (dict): Datos del usuario
        permiso (str): Permiso a verificar
        
    Returns:
        bool: True si tiene el permiso, False en caso contrario
    """
    return verificar_permiso(user_data, permiso, mostrar_error=False)

def puede_editar_postulante(user_data, postulante_data):
    """
    Verificar si un usuario puede editar un postulante específico
    
    Args:
        user_data (dict): Datos del usuario
        postulante_data (dict): Datos del postulante
        
    Returns:
        bool: True si puede editar, False en caso contrario
    """
    if not user_data or not postulante_data:
        return False
    
    rol = user_data.get('rol', 'USUARIO')
    
    # SUPERADMIN puede editar cualquier postulante
    if rol == 'SUPERADMIN':
        return True
    
    # Verificar si puede editar postulantes de otros usuarios
    if verificar_privilegio(rol, 'editar_postulantes_otros'):
        return True
    
    # Verificar si puede editar sus propios postulantes
    if verificar_privilegio(rol, 'editar_postulantes_propios'):
        # Verificar si el postulante fue registrado por este usuario
        usuario_registrador = postulante_data.get('usuario_registrador')
        if usuario_registrador == user_data.get('id'):
            return True
    
    return False

def puede_eliminar_postulante(user_data, postulante_data):
    """
    Verificar si un usuario puede eliminar un postulante específico
    
    Args:
        user_data (dict): Datos del usuario
        postulante_data (dict): Datos del postulante
        
    Returns:
        bool: True si puede eliminar, False en caso contrario
    """
    if not user_data or not postulante_data:
        return False
    
    rol = user_data.get('rol', 'USUARIO')
    
    # SUPERADMIN puede eliminar cualquier postulante
    if rol == 'SUPERADMIN':
        return True
    
    # Verificar si puede eliminar postulantes de otros usuarios
    if verificar_privilegio(rol, 'eliminar_postulantes_otros'):
        return True
    
    # Verificar si puede eliminar sus propios postulantes
    if verificar_privilegio(rol, 'eliminar_postulantes_propios'):
        # Verificar si el postulante fue registrado por este usuario
        usuario_registrador = postulante_data.get('usuario_registrador')
        if usuario_registrador == user_data.get('id'):
            return True
    
    return False

def puede_ver_estadisticas_completas(user_data):
    """
    Verificar si un usuario puede ver estadísticas completas
    
    Args:
        user_data (dict): Datos del usuario
        
    Returns:
        bool: True si puede ver estadísticas completas, False en caso contrario
    """
    if not user_data:
        return False
    
    rol = user_data.get('rol', 'USUARIO')
    
    # SUPERADMIN siempre puede ver estadísticas completas
    if rol == 'SUPERADMIN':
        return True
    
    return verificar_privilegio(rol, 'estadisticas_completas')

def puede_gestionar_zkteco(user_data):
    """
    Verificar si un usuario puede gestionar dispositivos ZKTeco
    
    Args:
        user_data (dict): Datos del usuario
        
    Returns:
        bool: True si puede gestionar ZKTeco, False en caso contrario
    """
    if not user_data:
        return False
    
    rol = user_data.get('rol', 'USUARIO')
    
    # SUPERADMIN siempre puede gestionar ZKTeco
    if rol == 'SUPERADMIN':
        return True
    
    return verificar_privilegio(rol, 'gestion_zkteco_completa')

def puede_usar_zkteco_basico(user_data):
    """
    Verificar si un usuario puede usar dispositivos ZKTeco básicamente
    
    Args:
        user_data (dict): Datos del usuario
        
    Returns:
        bool: True si puede usar ZKTeco básicamente, False en caso contrario
    """
    if not user_data:
        return False
    
    rol = user_data.get('rol', 'USUARIO')
    
    # SUPERADMIN siempre puede usar ZKTeco
    if rol == 'SUPERADMIN':
        return True
    
    # Verificar privilegios básicos o completos
    return (verificar_privilegio(rol, 'gestion_zkteco_basica') or 
            verificar_privilegio(rol, 'gestion_zkteco_completa'))

def obtener_privilegios_usuario(user_data):
    """
    Obtener lista de privilegios activos de un usuario
    
    Args:
        user_data (dict): Datos del usuario
        
    Returns:
        list: Lista de privilegios activos
    """
    if not user_data:
        return []
    
    rol = user_data.get('rol', 'USUARIO')
    
    # SUPERADMIN tiene todos los privilegios
    if rol == 'SUPERADMIN':
        return [
            'buscar_postulantes',
            'agregar_postulante',
            'lista_postulantes',
            'estadisticas_completas',
            'gestion_zkteco_completa',
            'editar_postulantes_propios',
            'editar_postulantes_otros',
            'eliminar_postulantes_propios',
            'eliminar_postulantes_otros',
            'gestion_usuarios',
            'gestion_privilegios'
        ]
    
    # Para otros roles, verificar privilegios específicos
    privilegios = []
    todos_privilegios = [
        'buscar_postulantes',
        'agregar_postulante',
        'lista_postulantes',
        'estadisticas_basicas',
        'estadisticas_completas',
        'gestion_zkteco_basica',
        'gestion_zkteco_completa',
        'editar_postulantes_propios',
        'editar_postulantes_otros',
        'eliminar_postulantes_propios',
        'eliminar_postulantes_otros',
        'gestion_usuarios',
        'gestion_privilegios'
    ]
    
    for privilegio in todos_privilegios:
        if verificar_privilegio(rol, privilegio):
            privilegios.append(privilegio)
    
    return privilegios
