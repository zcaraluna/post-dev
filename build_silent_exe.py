#!/usr/bin/env python3
"""
Script para compilar el ejecutable con configuración que evite ventanas CMD
"""

import os
import sys
import subprocess
import platform

def build_silent_executable():
    """
    Compilar el ejecutable con configuración que evite ventanas CMD
    """
    print("🔨 Compilando ejecutable silencioso...")
    
    # Configurar variables de entorno para PyInstaller
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    os.environ['PYINSTALLER_NO_CONSOLE'] = '1'
    
    # Comando de PyInstaller con configuración específica
    cmd = [
        'pyinstaller',
        '--onefile',  # Crear un solo archivo ejecutable
        '--windowed',  # No mostrar consola
        '--noconsole',  # No mostrar consola (redundante pero seguro)
        '--disable-windowed-traceback',  # Deshabilitar traceback en ventanas
        '--name=Sistema_Postulantes',
        '--icon=quira.ico',
        '--add-data=quiraXXXL.png;.',
        '--add-data=quira.png;.',
        '--add-data=instituto.png;.',
        '--add-data=quiraXXL.png;.',
        '--add-data=quira_bigger.png;.',
        '--hidden-import=zkteco_connector_v2',
        '--hidden-import=gestion_zkteco',
        '--hidden-import=privilegios_utils',
        '--hidden-import=gestion_privilegios',
        '--hidden-import=login_system',
        '--hidden-import=icon_utils',
        '--hidden-import=zk',
        '--hidden-import=subprocess',
        '--hidden-import=socket',
        '--exclude-module=tkinter.test',
        '--exclude-module=unittest',
        '--exclude-module=test',
        'main_integrado.py'
    ]
    
    # En Windows, usar punto y coma como separador
    if platform.system().lower() == "windows":
        cmd = [arg.replace(';', ';') for arg in cmd]
    else:
        # En Linux/Mac, usar dos puntos como separador
        cmd = [arg.replace(';', ':') for arg in cmd]
    
    try:
        print("[DEPS] Ejecutando PyInstaller...")
        print(f"Comando: {' '.join(cmd)}")
        
        # Ejecutar PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Ejecutable compilado exitosamente")
            print("[PATH] El ejecutable se encuentra en: dist/Sistema_Postulantes.exe")
        else:
            print("[ERROR] Error al compilar el ejecutable")
            print(f"Error: {result.stderr}")
            
    except Exception as e:
        print(f"[ERROR] Error ejecutando PyInstaller: {e}")

if __name__ == "__main__":
    build_silent_executable()
