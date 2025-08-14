#!/usr/bin/env python3
"""
Configuración para PyInstaller que evita ventanas CMD
"""

import os
import sys

def configure_pyinstaller_environment():
    """
    Configurar variables de entorno para PyInstaller que eviten ventanas CMD
    """
    # Variables de entorno para evitar ventanas CMD
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    
    # Variables específicas para PyInstaller
    os.environ['PYINSTALLER_NO_CONSOLE'] = '1'
    
    # Configurar para evitar subprocess que abran ventanas
    if hasattr(sys, '_MEIPASS'):
        # Estamos en un ejecutable PyInstaller
        os.environ['PYINSTALLER_RUNNING'] = '1'

# Configurar al importar
configure_pyinstaller_environment()

# Hook personalizado para PyInstaller
def get_pyinstaller_hooks():
    """
    Retorna hooks personalizados para PyInstaller
    """
    return {
        'zk': {
            'hiddenimports': ['zk'],
            'excludes': ['tkinter.test'],
        },
        'subprocess': {
            'hiddenimports': ['subprocess'],
            'excludes': ['tkinter.test'],
        },
        'socket': {
            'hiddenimports': ['socket'],
            'excludes': ['tkinter.test'],
        }
    }
