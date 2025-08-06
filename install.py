#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de instalación para ZKTeco K40 - Gestor de Dispositivos
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Verificar versión de Python"""
    if sys.version_info < (3, 7):
        print("❌ Error: Se requiere Python 3.7 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def install_requirements():
    """Instalar dependencias"""
    print("\n📦 Instalando dependencias...")
    
    try:
        # Verificar si pip está disponible
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ Error: pip no está disponible")
        return False
    
    try:
        # Instalar dependencias
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencias instaladas correctamente")
            return True
        else:
            print("❌ Error al instalar dependencias:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_imports():
    """Probar importaciones de módulos"""
    print("\n🔍 Probando importaciones...")
    
    try:
        import tkinter
        print("✅ tkinter - OK")
    except ImportError:
        print("❌ tkinter no está disponible")
        return False
    
    try:
        import socket
        print("✅ socket - OK")
    except ImportError:
        print("❌ socket no está disponible")
        return False
    
    try:
        import struct
        print("✅ struct - OK")
    except ImportError:
        print("❌ struct no está disponible")
        return False
    
    try:
        import threading
        print("✅ threading - OK")
    except ImportError:
        print("❌ threading no está disponible")
        return False
    
    return True

def create_launcher_scripts():
    """Crear scripts de lanzamiento"""
    print("\n🚀 Creando scripts de lanzamiento...")
    
    # Script para Windows
    if os.name == 'nt':
        with open("ejecutar_gui.bat", "w", encoding="utf-8") as f:
            f.write("@echo off\n")
            f.write("echo Iniciando ZKTeco K40 - Gestor de Dispositivos...\n")
            f.write("python gui_app.py\n")
            f.write("pause\n")
        
        with open("ejecutar_cli.bat", "w", encoding="utf-8") as f:
            f.write("@echo off\n")
            f.write("echo ZKTeco K40 - Script de Línea de Comandos\n")
            f.write("echo Uso: ejecutar_cli.bat [IP] [PUERTO] [OPCIONES]\n")
            f.write("python simple_connector.py %*\n")
            f.write("pause\n")
        
        print("✅ Scripts de Windows creados:")
        print("   - ejecutar_gui.bat (Interfaz gráfica)")
        print("   - ejecutar_cli.bat (Línea de comandos)")
    
    # Script para Linux/Mac
    else:
        with open("ejecutar_gui.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write("echo 'Iniciando ZKTeco K40 - Gestor de Dispositivos...'\n")
            f.write("python3 gui_app.py\n")
        
        with open("ejecutar_cli.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write("echo 'ZKTeco K40 - Script de Línea de Comandos'\n")
            f.write("echo 'Uso: ./ejecutar_cli.sh [IP] [PUERTO] [OPCIONES]'\n")
            f.write("python3 simple_connector.py \"$@\"\n")
        
        # Hacer ejecutables
        os.chmod("ejecutar_gui.sh", 0o755)
        os.chmod("ejecutar_cli.sh", 0o755)
        
        print("✅ Scripts de Linux/Mac creados:")
        print("   - ejecutar_gui.sh (Interfaz gráfica)")
        print("   - ejecutar_cli.sh (Línea de comandos)")

def show_usage_instructions():
    """Mostrar instrucciones de uso"""
    print("\n" + "="*60)
    print("🎉 INSTALACIÓN COMPLETADA")
    print("="*60)
    
    print("\n📋 CÓMO USAR LA APLICACIÓN:")
    
    if os.name == 'nt':
        print("\n🖥️  Interfaz Gráfica:")
        print("   Doble clic en 'ejecutar_gui.bat'")
        print("   O ejecuta: python gui_app.py")
        
        print("\n💻 Línea de Comandos:")
        print("   Doble clic en 'ejecutar_cli.bat'")
        print("   O ejecuta: python simple_connector.py [IP] [PUERTO]")
    else:
        print("\n🖥️  Interfaz Gráfica:")
        print("   ./ejecutar_gui.sh")
        print("   O ejecuta: python3 gui_app.py")
        
        print("\n💻 Línea de Comandos:")
        print("   ./ejecutar_cli.sh [IP] [PUERTO]")
        print("   O ejecuta: python3 simple_connector.py [IP] [PUERTO]")
    
    print("\n🔧 CONFIGURACIÓN DEL DISPOSITIVO:")
    print("   1. Conecta el dispositivo ZKTeco K40 por Ethernet")
    print("   2. Configura una IP estática (ej: 192.168.1.100)")
    print("   3. Puerto por defecto: 4370")
    print("   4. Verifica conectividad: ping [IP_DEL_DISPOSITIVO]")
    
    print("\n📖 DOCUMENTACIÓN:")
    print("   Lee el archivo README.md para más detalles")
    
    print("\n" + "="*60)

def main():
    """Función principal de instalación"""
    print("🔧 ZKTeco K40 - Instalador")
    print("="*40)
    
    # Verificar versión de Python
    if not check_python_version():
        sys.exit(1)
    
    # Verificar que estamos en el directorio correcto
    if not Path("requirements.txt").exists():
        print("❌ Error: No se encontró requirements.txt")
        print("   Asegúrate de ejecutar este script desde el directorio del proyecto")
        sys.exit(1)
    
    # Instalar dependencias
    if not install_requirements():
        print("\n❌ La instalación falló. Revisa los errores anteriores.")
        sys.exit(1)
    
    # Probar importaciones
    if not test_imports():
        print("\n❌ Error en las importaciones. Revisa la instalación.")
        sys.exit(1)
    
    # Crear scripts de lanzamiento
    create_launcher_scripts()
    
    # Mostrar instrucciones
    show_usage_instructions()

if __name__ == "__main__":
    main() 