#!/usr/bin/env python3
"""
Capturador simple de ventanas CMD
"""

import os
import sys
import subprocess
import threading
import time

# Configuración básica
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

def capture_cmd_windows():
    """
    Capturar y cerrar ventanas CMD que aparezcan
    """
    try:
        # Redirigir stdout y stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        
        # Reemplazar subprocess.run
        original_run = subprocess.run
        
        def silent_run(*args, **kwargs):
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
                
                return original_run(*args, **kwargs)
            except Exception as e:
                return None
        
        subprocess.run = silent_run
        
        # Thread para cerrar ventanas CMD
        def close_cmd_windows():
            while True:
                try:
                    # Buscar y cerrar ventanas CMD
                    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq cmd.exe'], 
                                          capture_output=True, text=True, 
                                          creationflags=subprocess.CREATE_NO_WINDOW)
                    
                    if 'cmd.exe' in result.stdout:
                        # Cerrar procesos cmd.exe
                        subprocess.run(['taskkill', '/F', '/IM', 'cmd.exe'], 
                                     capture_output=True,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
                        
                except:
                    pass
                
                time.sleep(0.5)  # Verificar cada 500ms
        
        # Iniciar thread
        cmd_thread = threading.Thread(target=close_cmd_windows, daemon=True)
        cmd_thread.start()
        
    except Exception as e:
        pass

# Ejecutar capturador
capture_cmd_windows()
