#!/usr/bin/env python3
"""
Script para instalar Pillow si no está disponible
"""

import subprocess
import sys

def install_pillow():
    """Instalar Pillow si no está disponible"""
    try:
        import PIL
        print("✅ Pillow ya está instalado")
        return True
    except ImportError:
        print("📦 Instalando Pillow...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow>=10.1.0"])
            print("✅ Pillow instalado correctamente")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error al instalar Pillow: {e}")
            return False

if __name__ == "__main__":
    install_pillow() 