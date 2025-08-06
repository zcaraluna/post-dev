#!/usr/bin/env python3
"""
Script de configuración de base de datos PostgreSQL
"""

import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
import subprocess
import sys

def check_postgresql_installed():
    """Verificar si PostgreSQL está instalado"""
    try:
        # Intentar ejecutar psql
        result = subprocess.run(['psql', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, "No se pudo ejecutar psql"
    except FileNotFoundError:
        return False, "PostgreSQL no está instalado o no está en el PATH"
    except Exception as e:
        return False, str(e)

def create_database(db_name, user, password, host="localhost", port="5432"):
    """Crear base de datos si no existe"""
    try:
        # Conectar a postgres (base de datos por defecto)
        conn = psycopg2.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Verificar si la base de datos existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            # Crear la base de datos
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"✅ Base de datos '{db_name}' creada exitosamente")
        else:
            print(f"✅ Base de datos '{db_name}' ya existe")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error al crear base de datos: {e}")
        return False

class DatabaseSetupWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Configuración de Base de Datos PostgreSQL")
        self.root.geometry("500x400")
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz"""
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Título
        title_label = ttk.Label(main_frame, text="Configuración de Base de Datos", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Verificar PostgreSQL
        self.check_postgresql()
        
        # Frame de configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración de Conexión", padding=15)
        config_frame.pack(fill='x', pady=(0, 20))
        
        # Variables
        self.host_var = tk.StringVar(value="localhost")
        self.port_var = tk.StringVar(value="5432")
        self.user_var = tk.StringVar(value="postgres")
        self.password_var = tk.StringVar()
        self.db_name_var = tk.StringVar(value="sistema_postulantes")
        
        # Campos
        ttk.Label(config_frame, text="Host:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(config_frame, textvariable=self.host_var, width=20).grid(row=0, column=1, padx=(10, 0), pady=5)
        
        ttk.Label(config_frame, text="Puerto:").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(config_frame, textvariable=self.port_var, width=20).grid(row=1, column=1, padx=(10, 0), pady=5)
        
        ttk.Label(config_frame, text="Usuario:").grid(row=2, column=0, sticky='w', pady=5)
        ttk.Entry(config_frame, textvariable=self.user_var, width=20).grid(row=2, column=1, padx=(10, 0), pady=5)
        
        ttk.Label(config_frame, text="Contraseña:").grid(row=3, column=0, sticky='w', pady=5)
        ttk.Entry(config_frame, textvariable=self.password_var, show='*', width=20).grid(row=3, column=1, padx=(10, 0), pady=5)
        
        ttk.Label(config_frame, text="Base de Datos:").grid(row=4, column=0, sticky='w', pady=5)
        ttk.Entry(config_frame, textvariable=self.db_name_var, width=20).grid(row=4, column=1, padx=(10, 0), pady=5)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="🔍 Probar Conexión", 
                  command=self.test_connection).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="🗄️ Crear Base de Datos", 
                  command=self.create_database).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="✅ Inicializar Sistema", 
                  command=self.initialize_system).pack(side='left')
        
        # Área de log
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding=10)
        log_frame.pack(fill='both', expand=True)
        
        self.log_text = tk.Text(log_frame, height=8, width=60)
        scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def check_postgresql(self):
        """Verificar instalación de PostgreSQL"""
        self.log("🔍 Verificando PostgreSQL...")
        installed, version = check_postgresql_installed()
        
        if installed:
            self.log(f"✅ PostgreSQL instalado: {version}")
        else:
            self.log(f"❌ PostgreSQL no encontrado: {version}")
            self.log("💡 Instale PostgreSQL desde: https://www.postgresql.org/download/")
    
    def test_connection(self):
        """Probar conexión a PostgreSQL"""
        self.log("🔍 Probando conexión...")
        
        try:
            conn = psycopg2.connect(
                host=self.host_var.get(),
                port=self.port_var.get(),
                user=self.user_var.get(),
                password=self.password_var.get(),
                dbname="postgres"  # Conectar a postgres por defecto
            )
            conn.close()
            self.log("✅ Conexión exitosa a PostgreSQL")
            return True
        except Exception as e:
            self.log(f"❌ Error de conexión: {e}")
            return False
    
    def create_database(self):
        """Crear base de datos"""
        if not self.test_connection():
            return
        
        self.log(f"🗄️ Creando base de datos '{self.db_name_var.get()}'...")
        
        if create_database(
            self.db_name_var.get(),
            self.user_var.get(),
            self.password_var.get(),
            self.host_var.get(),
            self.port_var.get()
        ):
            self.log("✅ Base de datos creada exitosamente")
        else:
            self.log("❌ Error al crear base de datos")
    
    def initialize_system(self):
        """Inicializar el sistema completo"""
        self.log("🚀 Inicializando sistema...")
        
        # Probar conexión
        if not self.test_connection():
            return
        
        # Crear base de datos si no existe
        self.create_database()
        
        # Inicializar tablas
        try:
            from database import init_database
            
            # Actualizar configuración temporalmente
            import database
            database.DB_CONFIG = {
                'host': self.host_var.get(),
                'port': self.port_var.get(),
                'user': self.user_var.get(),
                'password': self.password_var.get(),
                'dbname': self.db_name_var.get()
            }
            
            if init_database():
                self.log("✅ Sistema inicializado correctamente")
                self.log("🎉 ¡El sistema está listo para usar!")
                messagebox.showinfo("Éxito", "Sistema inicializado correctamente.\n\n"
                                           "Credenciales por defecto:\n"
                                           "Usuario: admin\n"
                                           "Contraseña: admin123")
            else:
                self.log("❌ Error al inicializar sistema")
                
        except Exception as e:
            self.log(f"❌ Error: {e}")
    
    def log(self, message):
        """Agregar mensaje al log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def run(self):
        """Ejecutar la ventana"""
        self.root.mainloop()

def main():
    """Función principal"""
    print("🔧 Configuración de Base de Datos PostgreSQL")
    print("=" * 50)
    
    # Verificar si PostgreSQL está instalado
    installed, version = check_postgresql_installed()
    
    if not installed:
        print(f"❌ PostgreSQL no está instalado: {version}")
        print("💡 Instale PostgreSQL desde: https://www.postgresql.org/download/")
        print("   Luego ejecute este script nuevamente")
        return
    
    print(f"✅ PostgreSQL encontrado: {version}")
    
    # Abrir ventana de configuración
    app = DatabaseSetupWindow()
    app.run()

if __name__ == "__main__":
    main() 