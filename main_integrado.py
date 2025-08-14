#!/usr/bin/env python3
"""
Sistema QUIRA
Punto de entrada principal del sistema
"""

# Importar silent_wrapper optimizado para ZKTeco PRIMERO para evitar ventanas CMD
try:
    import silent_wrapper_zkteco
    print("[OK] Silent wrapper ZKTeco cargado correctamente")
except ImportError:
    try:
        import silent_wrapper
        print("[OK] Silent wrapper básico cargado correctamente")
    except ImportError:
        print("[WARN] No se pudo cargar ningún silent wrapper")

import tkinter as tk
from tkinter import messagebox
import sys
import os
import ctypes

# Configurar DPI para Windows (HD/4K)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Per Monitor DPI Aware
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()  # Fallback para versiones anteriores
    except:
        pass

# Agregar el directorio actual al path para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Verificar que todas las dependencias estén instaladas"""
    try:
        import psycopg2
        import bcrypt
        from zk import ZK
        import tkinter
        return True
    except ImportError as e:
        messagebox.showerror("Error de Dependencias", 
                           f"Falta instalar dependencias: {e}\n\n"
                           "Ejecute: pip install -r requirements.txt")
        return False

def check_database():
    """Verificar conexión a la base de datos"""
    try:
        from database import connect_db, init_database
        
        # Intentar conectar
        conn = connect_db()
        if not conn:
            messagebox.showerror("Error de Base de Datos", 
                               "No se pudo conectar a PostgreSQL.\n\n"
                               "Verifique que:\n"
                               "1. PostgreSQL esté instalado y ejecutándose\n"
                               "2. Exista la base de datos 'sistema_postulantes'\n"
                               "3. Las credenciales sean correctas")
            return False
        
        # Inicializar base de datos
        if not init_database():
            messagebox.showerror("Error de Base de Datos", 
                               "No se pudo inicializar la base de datos")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        messagebox.showerror("Error de Base de Datos", 
                           f"Error al verificar base de datos: {e}")
        return False

def check_zkteco_connection():
    """Verificar conexión al dispositivo ZKTeco"""
    try:
        from zkteco_connector_v2 import test_connection
        
        # Intentar conectar al dispositivo
        if test_connection("192.168.100.201", 4370):
            print("[OK] Conexión ZKTeco verificada")
            return True
        else:
            print("[WARN] No se pudo conectar al dispositivo ZKTeco")
            print("   El sistema funcionará sin el dispositivo biométrico")
            return False
            
    except Exception as e:
        print(f"[WARN] Error al verificar ZKTeco: {e}")
        return False

def main():
    """Función principal del sistema"""
    print("[INIT] Iniciando Sistema QUIRA")
    print("=" * 50)
    
    # Verificar dependencias
    print("[DEPS] Verificando dependencias...")
    if not check_dependencies():
        return
    
    # Verificar base de datos
    print("[DB] Verificando base de datos...")
    if not check_database():
        return
    
    # Verificar ZKTeco (opcional)
    print("[ZKT] Verificando dispositivo ZKTeco...")
    zkteco_available = check_zkteco_connection()
    
    # Crear ventana principal
    root = tk.Tk()
    root.title("Sistema QUIRA")
    
    # Configurar icono de la ventana (256 píxeles)
    try:
        from icon_utils import set_large_256_icon
        if set_large_256_icon(root):
            print("[OK] Icono de 256px configurado correctamente")
    except ImportError:
        print("[WARN] No se pudo importar icon_utils")
    
    # Mostrar estado del sistema
    if zkteco_available:
        status_msg = "[OK] Sistema listo\n[OK] Base de datos conectada\n[OK] ZKTeco disponible"
    else:
        status_msg = "[OK] Sistema listo\n[OK] Base de datos conectada\n[WARN] ZKTeco no disponible"
    
    # Crear ventana de login
    try:
        from login_system import LoginWindow
        login_window = LoginWindow(root)
        login_window.pack(expand=True, fill='both')
        
        # Centrar la ventana en la pantalla
        root.update_idletasks()  # Actualizar para obtener dimensiones reales
        width = root.winfo_reqwidth()
        height = root.winfo_reqheight()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry('')
        
        # Hacer la ventana no redimensionable para mantener el tamaño del contenido
        root.resizable(False, False)
        
        print("[OK] Sistema iniciado correctamente")
        print(f"[STATUS] Estado: {status_msg}")
        
        # Iniciar loop principal
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al iniciar el sistema: {e}")
        print(f"[ERROR] Error al iniciar: {e}")

if __name__ == "__main__":
    main() 