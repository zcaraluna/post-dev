#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para instalar las dependencias necesarias para el generador de documentos Word
"""

import subprocess
import sys

def instalar_dependencias():
    """Instala las dependencias necesarias"""
    print("🔄 Instalando dependencias para el generador de documentos Word...")
    
    try:
        # Instalar python-docx
        print("📦 Instalando python-docx...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx==0.8.11"])
        print("✅ python-docx instalado correctamente")
        
        print("\n🎉 ¡Todas las dependencias han sido instaladas exitosamente!")
        print("📝 Ahora puedes ejecutar: python generar_documento_word.py")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar las dependencias: {e}")
        print("💡 Intenta ejecutar manualmente: pip install python-docx==0.8.11")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    instalar_dependencias() 