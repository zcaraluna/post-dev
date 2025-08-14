#!/usr/bin/env python3
"""
Script ultra silencioso para compilar sin ventanas CMD
"""

import os
import sys
import subprocess
import platform

def compilar_ultra_silencioso():
    """
    Compilar el ejecutable con configuración ultra silenciosa
    """
    print("🔨 Compilando ejecutable ultra silencioso...")
    
    # Configurar variables de entorno para PyInstaller
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    os.environ['PYINSTALLER_NO_CONSOLE'] = '1'
    os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '1'
    
    # Comando ultra silencioso de PyInstaller
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--noconsole',
        '--disable-windowed-traceback',
        '--name=Sistema_Postulantes',
        '--icon=quira.ico',
        '--add-data=capture_cmd.py;.',
        '--add-data=cmd_blocker.py;.',
        '--add-data=silent_wrapper.py;.',
        '--add-data=quiraXXXL.png;.',
        '--add-data=quira.png;.',
        '--add-data=instituto.png;.',
        '--add-data=quiraXXL.png;.',
        '--add-data=quira_bigger.png;.',
        '--hidden-import=capture_cmd',
        '--hidden-import=cmd_blocker',
        '--hidden-import=silent_wrapper',
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
    
    try:
        print("[DEPS] Ejecutando PyInstaller...")
        print(f"Comando: {' '.join(cmd)}")
        
        # Ejecutar PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Ejecutable ultra silencioso compilado exitosamente")
            print("[PATH] El ejecutable se encuentra en: dist/Sistema_Postulantes.exe")
            print("🚫 Las ventanas CMD están completamente bloqueadas")
        else:
            print("[ERROR] Error al compilar el ejecutable")
            print(f"Error: {result.stderr}")
            
    except Exception as e:
        print(f"[ERROR] Error ejecutando PyInstaller: {e}")

if __name__ == "__main__":
    compilar_ultra_silencioso()
