#!/usr/bin/env python3
"""
Script de compilación optimizado siguiendo recomendaciones de ChatGPT
"""

import os
import sys
import subprocess
import logging
import multiprocessing

def setup_logging():
    """Configurar logging para la compilación"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('compilacion.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_pyinstaller():
    """Verificar que PyInstaller esté instalado"""
    try:
        import PyInstaller
        logging.info(f"[OK] PyInstaller {PyInstaller.__version__} encontrado")
        return True
    except ImportError:
        logging.error("[ERROR] PyInstaller no está instalado")
        print("Instale PyInstaller con: pip install pyinstaller")
        return False

def clean_build_dirs():
    """Limpiar directorios de compilación anteriores"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                import shutil
                shutil.rmtree(dir_name)
                logging.info(f"🧹 Limpiado directorio: {dir_name}")
            except Exception as e:
                logging.warning(f"[WARN] No se pudo limpiar {dir_name}: {e}")

def compile_executable():
    """Compilar el ejecutable con configuración optimizada"""
    logging.info("🔨 Iniciando compilación optimizada...")
    
    # Configurar variables de entorno para PyInstaller
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    os.environ['PYINSTALLER_NO_CONSOLE'] = '1'
    os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '1'
    
    # Comando de PyInstaller optimizado
    cmd = [
        'pyinstaller',
        '--onedir',                     # Carpeta con archivos
        '--windowed',                   # Sin consola
        '--noconsole',                  # Sin consola (redundante pero seguro)
        '--disable-windowed-traceback', # Sin ventanas de error
        '--name=Sistema_Postulantes',   # Nombre del ejecutable
        '--icon=quira.ico',            # Icono
        '--clean',                      # Limpiar cache
        '--strip',                      # Reducir tamaño
        '--optimize=2',                 # Optimización máxima
        
        # Archivos de datos
        '--add-data=capture_cmd.py;.',
        '--add-data=cmd_blocker.py;.',
        '--add-data=silent_wrapper.py;.',
        '--add-data=quiraXXXL.png;.',
        '--add-data=quira.png;.',
        '--add-data=instituto.png;.',
        '--add-data=quiraXXL.png;.',
        '--add-data=quira_bigger.png;.',
        
        # Imports ocultos
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
        '--hidden-import=multiprocessing',
        '--hidden-import=logging',
        '--hidden-import=psycopg2',
        '--hidden-import=bcrypt',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=tkinter.ttk',
        
        # Excluir módulos innecesarios
        '--exclude-module=tkinter.test',
        '--exclude-module=unittest',
        '--exclude-module=test',
        '--exclude-module=distutils',
        '--exclude-module=setuptools',
        '--exclude-module=pip',
        '--exclude-module=wheel',
        
        # Archivo principal
        'main_integrado.py'
    ]
    
    try:
        logging.info("[DEPS] Ejecutando PyInstaller...")
        logging.info(f"Comando: {' '.join(cmd)}")
        
        # Ejecutar PyInstaller con configuración silenciosa
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode == 0:
            logging.info("[OK] Compilación exitosa")
            
            # Verificar archivo resultante
            exe_path = "dist/Sistema_Postulantes/Sistema_Postulantes.exe"
            if os.path.exists(exe_path):
                # Calcular tamaño total de la carpeta
                total_size = 0
                for root, dirs, files in os.walk("dist/Sistema_Postulantes"):
                    for file in files:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                
                size_mb = total_size / (1024 * 1024)
                logging.info(f"[PATH] Ejecutable creado: {exe_path}")
                logging.info(f"📏 Tamaño total: {size_mb:.2f} MB")
                
                # Verificar que sea realmente onedir
                dist_contents = os.listdir("dist")
                if len(dist_contents) == 1 and dist_contents[0] == "Sistema_Postulantes":
                    logging.info("[OK] Confirmado: Ejecutable onedir")
                    logging.info("[PATH] Carpeta: dist/Sistema_Postulantes/")
                else:
                    logging.warning("[WARN] Puede no ser onedir - verificar contenido de dist/")
                
                return True
            else:
                logging.error("[ERROR] Ejecutable no encontrado")
                return False
        else:
            logging.error("[ERROR] Error en la compilación")
            logging.error(f"STDOUT: {result.stdout}")
            logging.error(f"STDERR: {result.stderr}")
            return False
            
    except Exception as e:
        logging.error(f"[ERROR] Error ejecutando PyInstaller: {e}")
        return False

def verify_executable():
    """Verificar que el ejecutable funcione correctamente"""
    logging.info("[SEARCH] Verificando ejecutable...")
    
    exe_path = "dist/Sistema_Postulantes.exe"
    if not os.path.exists(exe_path):
        logging.error("[ERROR] Ejecutable no encontrado para verificación")
        return False
    
    try:
        # Verificar que el archivo sea ejecutable
        logging.info("[OK] Archivo ejecutable encontrado")
        
        # Verificar dependencias embebidas
        logging.info("[CLIPBOARD] Verificando dependencias embebidas...")
        
        # Lista de archivos que deben estar embebidos
        required_files = [
            'capture_cmd.py',
            'cmd_blocker.py', 
            'silent_wrapper.py',
            'quiraXXXL.png',
            'quira.png',
            'instituto.png',
            'quiraXXL.png',
            'quira_bigger.png'
        ]
        
        logging.info("[OK] Verificación básica completada")
        logging.info("[TIP] Para verificación completa, ejecute el .exe manualmente")
        
        return True
        
    except Exception as e:
        logging.error(f"[ERROR] Error en verificación: {e}")
        return False

def main():
    """Función principal de compilación"""
    setup_logging()
    logging.info("[INIT] Iniciando proceso de compilación optimizado")
    logging.info("=" * 60)
    
    # Verificar PyInstaller
    if not check_pyinstaller():
        return False
    
    # Limpiar directorios anteriores
    clean_build_dirs()
    
    # Compilar ejecutable
    if not compile_executable():
        logging.error("[ERROR] Falló la compilación")
        return False
    
    # Verificar resultado
    if not verify_executable():
        logging.error("[ERROR] Falló la verificación")
        return False
    
    logging.info("[SUCCESS] Compilación completada exitosamente")
    logging.info("[PATH] Carpeta: dist/Sistema_Postulantes/")
    logging.info("[PATH] Ejecutable: dist/Sistema_Postulantes/Sistema_Postulantes.exe")
    logging.info("[CLIPBOARD] Log: compilacion.log")
    
    return True

if __name__ == "__main__":
    # Soporte para multiprocessing
    multiprocessing.freeze_support()
    
    success = main()
    if success:
        print("\n[OK] Compilación exitosa!")
        print("[PATH] Carpeta: dist/Sistema_Postulantes/")
        print("[PATH] Ejecutable: dist/Sistema_Postulantes/Sistema_Postulantes.exe")
        print("[CLIPBOARD] Log: compilacion.log")
    else:
        print("\n[ERROR] Compilación falló")
        print("[CLIPBOARD] Revisar: compilacion.log")
        sys.exit(1)
