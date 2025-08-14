#!/usr/bin/env python3
"""
Script de compilación final con silent_wrapper integrado
"""

import subprocess
import sys
import os

def compilar_silencioso():
    """Compilar el sistema con silent_wrapper integrado"""
    
    # Comando de compilación con silent_wrapper
    cmd = [
        'zkteco_env', 'Scripts', 'activate',
        'python', '-m', 'PyInstaller',
        '--onedir',
        '--noconsole',
        '--icon=quira.ico',
        '--add-data=quiraXXXL.png;.',
        '--add-data=quira.png;.',
        '--add-data=instituto.png;.',
        '--add-data=quiraXXL.png;.',
        '--add-data=quira_bigger.png;.',
        '--hidden-import=silent_wrapper',
        '--hidden-import=zkteco_connector_v2',
        '--hidden-import=gestion_zkteco',
        '--hidden-import=privilegios_utils',
        '--hidden-import=gestion_privilegios',
        '--hidden-import=login_system',
        '--hidden-import=icon_utils',
        '--hidden-import=subprocess',
        '--hidden-import=os',
        '--name=Sistema_Postulantes',
        '--noconfirm',
        'main_integrado.py'
    ]
    
    print("[BUILD] Compilando Sistema QUIRA con silent_wrapper...")
    print("=" * 60)
    
    try:
        # Ejecutar compilación
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Compilación exitosa!")
            print("[PATH] El ejecutable se encuentra en: dist/Sistema_Postulantes/")
            print("[INFO] El silent_wrapper está integrado para evitar ventanas CMD")
        else:
            print("[ERROR] Error en la compilación:")
            print(result.stderr)
            
    except Exception as e:
        print(f"[ERROR] Error ejecutando PyInstaller: {e}")

if __name__ == "__main__":
    compilar_silencioso()
