#!/usr/bin/env python3
"""
Bloqueador específico para ventanas CMD
"""

import os
import sys
import subprocess
import threading
import time
import ctypes
from ctypes import wintypes

# Configuración agresiva para evitar ventanas CMD
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['PYINSTALLER_NO_CONSOLE'] = '1'
os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '1'

# Detectar ejecutable PyInstaller
if getattr(sys, 'frozen', False):
    os.environ['PYINSTALLER_RUNNING'] = '1'

class CMDBlocker:
    """
    Clase para bloquear ventanas CMD
    """
    
    def __init__(self):
        self.original_subprocess_run = subprocess.run
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.blocking = True
        
    def start_blocking(self):
        """Iniciar bloqueo de ventanas CMD"""
        if os.name == 'nt':  # Windows
            # Redirigir stdout y stderr
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')
            
            # Reemplazar subprocess.run
            subprocess.run = self.silent_run
            
            # Iniciar thread para monitorear y cerrar ventanas CMD
            self.monitor_thread = threading.Thread(target=self.monitor_cmd_windows, daemon=True)
            self.monitor_thread.start()
    
    def silent_run(self, *args, **kwargs):
        """Versión silenciosa de subprocess.run"""
        try:
            # Configurar para evitar ventanas CMD
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            
            if 'startupinfo' not in kwargs:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                kwargs['startupinfo'] = startupinfo
            
            # Redirigir salida
            kwargs['stdout'] = subprocess.DEVNULL
            kwargs['stderr'] = subprocess.DEVNULL
            
            return self.original_subprocess_run(*args, **kwargs)
        except Exception as e:
            return None
    
    def monitor_cmd_windows(self):
        """Monitorear y cerrar ventanas CMD que aparezcan"""
        try:
            import win32gui
            import win32con
            import win32process
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if any(keyword in window_text.lower() for keyword in ['cmd', 'command', 'console']):
                        try:
                            # Cerrar la ventana CMD
                            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                        except:
                            pass
                return True
            
            while self.blocking:
                try:
                    win32gui.EnumWindows(enum_windows_callback, [])
                except:
                    pass
                time.sleep(0.1)  # Verificar cada 100ms
                
        except ImportError:
            # Si no hay win32gui, usar método alternativo
            while self.blocking:
                time.sleep(0.1)
    
    def stop_blocking(self):
        """Detener bloqueo"""
        self.blocking = False
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        subprocess.run = self.original_subprocess_run

# Crear instancia global
cmd_blocker = CMDBlocker()

# Iniciar bloqueo automáticamente
cmd_blocker.start_blocking()
