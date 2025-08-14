#!/usr/bin/env python3
"""
Wrapper para evitar ventanas CMD optimizado para ZKTeco
"""

import os
import sys
import subprocess
import threading
import time
import ctypes
from ctypes import wintypes

# Guardar las funciones originales
original_os_system = os.system
original_os_popen = os.popen
original_subprocess_run = subprocess.run
original_subprocess_popen = subprocess.Popen
original_subprocess_call = subprocess.call

# Configurar para evitar ventanas CMD desde el inicio
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['PYINSTALLER_NO_CONSOLE'] = '1'

# Detectar si estamos en un ejecutable PyInstaller
if getattr(sys, 'frozen', False):
    os.environ['PYINSTALLER_RUNNING'] = '1'

def disable_console_windows():
    """
    Deshabilitar completamente las ventanas de consola en Windows
    """
    try:
        if os.name == 'nt':  # Windows
            # Ocultar la ventana de consola actual
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            
            # Obtener handle de la consola
            SW_HIDE = 0
            SW_SHOW = 5
            
            # Ocultar ventana de consola
            hwnd = kernel32.GetConsoleWindow()
            if hwnd:
                user32.ShowWindow(hwnd, SW_HIDE)
                
            # Redirigir stdout y stderr a null
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')
            
    except Exception as e:
        pass

def silent_subprocess_run(*args, **kwargs):
    """
    Ejecutar subprocess de forma inteligente para ZKTeco
    """
    try:
        # Verificar si es una llamada relacionada con ZKTeco
        is_zkteco_call = False
        
        if args and len(args) > 0:
            cmd = args[0]
            if isinstance(cmd, list) and len(cmd) > 0:
                cmd_str = str(cmd[0]).lower()
                # Comandos que ZKTeco necesita para funcionar
                zkteco_commands = ['ping', 'ipconfig', 'netstat', 'arp', 'route', 'nslookup']
                is_zkteco_call = any(cmd in cmd_str for cmd in zkteco_commands)
        
        # Configurar para evitar ventanas CMD
        if 'creationflags' not in kwargs:
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        
        if 'startupinfo' not in kwargs:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            kwargs['startupinfo'] = startupinfo
        
        # Para comandos de ZKTeco, permitir salida pero ocultar ventana
        if is_zkteco_call:
            # No redirigir stdout/stderr para comandos de red
            return original_subprocess_run(*args, **kwargs)
        else:
            # Para otros comandos, redirigir salida
            kwargs['stdout'] = subprocess.DEVNULL
            kwargs['stderr'] = subprocess.DEVNULL
            return original_subprocess_run(*args, **kwargs)
            
    except Exception as e:
        return None

def silent_subprocess_popen(*args, **kwargs):
    """
    Ejecutar subprocess.Popen de forma inteligente para ZKTeco
    """
    try:
        # Verificar si es una llamada relacionada con ZKTeco
        is_zkteco_call = False
        
        if args and len(args) > 0:
            cmd = args[0]
            if isinstance(cmd, list) and len(cmd) > 0:
                cmd_str = str(cmd[0]).lower()
                # Comandos que ZKTeco necesita para funcionar
                zkteco_commands = ['ping', 'ipconfig', 'netstat', 'arp', 'route', 'nslookup']
                is_zkteco_call = any(cmd in cmd_str for cmd in zkteco_commands)
        
        # Configurar para evitar ventanas CMD
        if 'creationflags' not in kwargs:
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        
        if 'startupinfo' not in kwargs:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            kwargs['startupinfo'] = startupinfo
        
        # Para comandos de ZKTeco, permitir salida pero ocultar ventana
        if is_zkteco_call:
            # No redirigir stdout/stderr para comandos de red
            return original_subprocess_popen(*args, **kwargs)
        else:
            # Para otros comandos, redirigir salida
            kwargs['stdout'] = subprocess.DEVNULL
            kwargs['stderr'] = subprocess.DEVNULL
            return original_subprocess_popen(*args, **kwargs)
            
    except Exception as e:
        return None

def silent_subprocess_call(*args, **kwargs):
    """
    Ejecutar subprocess.call de forma inteligente para ZKTeco
    """
    try:
        # Verificar si es una llamada relacionada con ZKTeco
        is_zkteco_call = False
        
        if args and len(args) > 0:
            cmd = args[0]
            if isinstance(cmd, list) and len(cmd) > 0:
                cmd_str = str(cmd[0]).lower()
                # Comandos que ZKTeco necesita para funcionar
                zkteco_commands = ['ping', 'ipconfig', 'netstat', 'arp', 'route', 'nslookup']
                is_zkteco_call = any(cmd in cmd_str for cmd in zkteco_commands)
        
        # Configurar para evitar ventanas CMD
        if 'creationflags' not in kwargs:
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        
        if 'startupinfo' not in kwargs:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            kwargs['startupinfo'] = startupinfo
        
        # Para comandos de ZKTeco, permitir salida pero ocultar ventana
        if is_zkteco_call:
            # No redirigir stdout/stderr para comandos de red
            return original_subprocess_call(*args, **kwargs)
        else:
            # Para otros comandos, redirigir salida
            kwargs['stdout'] = subprocess.DEVNULL
            kwargs['stderr'] = subprocess.DEVNULL
            return original_subprocess_call(*args, **kwargs)
            
    except Exception as e:
        return None

def silent_os_system(command):
    """
    Ejecutar os.system de forma completamente silenciosa
    """
    try:
        # Usar subprocess silencioso en lugar de os.system
        return silent_subprocess_call(command, shell=True)
    except Exception as e:
        return None

def silent_os_popen(command, mode='r', bufsize=-1):
    """
    Ejecutar os.popen de forma completamente silenciosa
    """
    try:
        # Usar subprocess silencioso en lugar de os.popen
        result = silent_subprocess_run(command, shell=True, capture_output=True, text=True)
        if result and result.returncode == 0:
            return result.stdout
        return ""
    except Exception as e:
        return ""

# Aplicar configuración al importar
disable_console_windows()

# Reemplazar subprocess.run con nuestra versión silenciosa
subprocess.run = silent_subprocess_run

# Reemplazar subprocess.Popen con nuestra versión silenciosa
subprocess.Popen = silent_subprocess_popen

# Reemplazar subprocess.call con nuestra versión silenciosa
subprocess.call = silent_subprocess_call

# Reemplazar os.system con nuestra versión silenciosa
os.system = silent_os_system

# Reemplazar os.popen con nuestra versión silenciosa
os.popen = silent_os_popen
