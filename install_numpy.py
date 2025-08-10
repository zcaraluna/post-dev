#!/usr/bin/env python3
"""
Script para instalar numpy si no está disponible
"""

import subprocess
import sys

def install_numpy():
    """Instalar numpy si no está disponible"""
    try:
        import numpy
        print("✅ numpy ya está instalado")
        return True
    except ImportError:
        print("📦 Instalando numpy...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy>=1.24.0"])
            print("✅ numpy instalado correctamente")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error al instalar numpy: {e}")
            return False

if __name__ == "__main__":
    install_numpy()
