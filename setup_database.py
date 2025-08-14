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
            print(f"[OK] Base de datos '{db_name}' creada exitosamente")
        else:
            print(f"[OK] Base de datos '{db_name}' ya existe")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Error al crear base de datos: {e}")
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
        
        ttk.Button(button_frame, text="[SEARCH] Probar Conexión", 
                  command=self.test_connection).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="[DB] Crear Base de Datos", 
                  command=self.create_database).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="[OK] Inicializar Sistema", 
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
        self.log("[SEARCH] Verificando PostgreSQL...")
        installed, version = check_postgresql_installed()
        
        if installed:
            self.log(f"[OK] PostgreSQL instalado: {version}")
        else:
            self.log(f"[ERROR] PostgreSQL no encontrado: {version}")
            self.log("[TIP] Instale PostgreSQL desde: https://www.postgresql.org/download/")
    
    def test_connection(self):
        """Probar conexión a PostgreSQL"""
        self.log("[SEARCH] Probando conexión...")
        
        try:
            conn = psycopg2.connect(
                host=self.host_var.get(),
                port=self.port_var.get(),
                user=self.user_var.get(),
                password=self.password_var.get(),
                dbname="postgres"  # Conectar a postgres por defecto
            )
            conn.close()
            self.log("[OK] Conexión exitosa a PostgreSQL")
            return True
        except Exception as e:
            self.log(f"[ERROR] Error de conexión: {e}")
            return False
    
    def create_database(self):
        """Crear base de datos"""
        if not self.test_connection():
            return
        
        self.log(f"[DB] Creando base de datos '{self.db_name_var.get()}'...")
        
        if create_database(
            self.db_name_var.get(),
            self.user_var.get(),
            self.password_var.get(),
            self.host_var.get(),
            self.port_var.get()
        ):
            self.log("[OK] Base de datos creada exitosamente")
        else:
            self.log("[ERROR] Error al crear base de datos")
    
    def initialize_system(self):
        """Inicializar el sistema completo"""
        self.log("[INIT] Inicializando sistema...")
        
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
                self.log("[OK] Sistema inicializado correctamente")
                self.log("[SUCCESS] ¡El sistema está listo para usar!")
                messagebox.showinfo("Éxito", "Sistema inicializado correctamente.\n\n"
                                           "Credenciales por defecto:\n"
                                           "Usuario: admin\n"
                                           "Contraseña: admin123")
            else:
                self.log("[ERROR] Error al inicializar sistema")
                
        except Exception as e:
            self.log(f"[ERROR] Error: {e}")
    
    def log(self, message):
        """Agregar mensaje al log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def run(self):
        """Ejecutar la ventana"""
        self.root.mainloop()

def crear_tabla_comunicados():
    """Crear tabla para comunicados del sistema"""
    try:
        conn = psycopg2.connect(
            dbname=self.db_name_var.get(), # Usar la base de datos configurada
            user=self.user_var.get(),
            password=self.password_var.get(),
            host=self.host_var.get(),
            port=self.port_var.get()
        )
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Verificar si la tabla ya existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'comunicados'
            );
        """)
        
        if cursor.fetchone()[0]:
            print("[OK] Tabla 'comunicados' ya existe")
            conn.close()
            return True
        
        # Crear tabla comunicados
        cursor.execute("""
            CREATE TABLE comunicados (
                id SERIAL PRIMARY KEY,
                titulo VARCHAR(200) NOT NULL,
                mensaje TEXT NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_expiracion TIMESTAMP,
                creado_por INTEGER REFERENCES usuarios(id),
                activo BOOLEAN DEFAULT TRUE,
                prioridad VARCHAR(20) DEFAULT 'normal' CHECK (prioridad IN ('baja', 'normal', 'alta', 'urgente'))
            );
        """)
        
        # Crear tabla para seguimiento de lectura de comunicados
        cursor.execute("""
            CREATE TABLE comunicados_leidos (
                id SERIAL PRIMARY KEY,
                comunicado_id INTEGER REFERENCES comunicados(id) ON DELETE CASCADE,
                usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                fecha_lectura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(comunicado_id, usuario_id)
            );
        """)
        
        conn.commit()
        conn.close()
        print("[OK] Tabla 'comunicados' creada exitosamente")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error al crear tabla comunicados: {e}")
        if conn:
            conn.close()
        return False

def crear_tabla_comentarios():
    """Crear tabla para comentarios de usuarios"""
    try:
        conn = psycopg2.connect(
            dbname=self.db_name_var.get(), # Usar la base de datos configurada
            user=self.user_var.get(),
            password=self.password_var.get(),
            host=self.host_var.get(),
            port=self.port_var.get()
        )
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Verificar si la tabla ya existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'comentarios'
            );
        """)
        
        if cursor.fetchone()[0]:
            print("[OK] Tabla 'comentarios' ya existe")
            conn.close()
            return True
        
        # Crear tabla comentarios
        cursor.execute("""
            CREATE TABLE comentarios (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER REFERENCES usuarios(id),
                nombre_usuario VARCHAR(100),
                email VARCHAR(100),
                asunto VARCHAR(200) NOT NULL,
                mensaje TEXT NOT NULL,
                fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'en_revision', 'respondido', 'cerrado')),
                respuesta TEXT,
                fecha_respuesta TIMESTAMP,
                respondido_por INTEGER REFERENCES usuarios(id)
            );
        """)
        
        conn.commit()
        conn.close()
        print("[OK] Tabla 'comentarios' creada exitosamente")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error al crear tabla comentarios: {e}")
        if conn:
            conn.close()
        return False

def main():
    """Función principal para configurar la base de datos"""
    print("[INIT] Configurando base de datos del sistema...")
    
    # Crear tablas principales
    if crear_tabla_usuarios():
        print("[OK] Tabla usuarios configurada")
    else:
        print("[ERROR] Error al configurar tabla usuarios")
        return
    
    if crear_tabla_postulantes():
        print("[OK] Tabla postulantes configurada")
    else:
        print("[ERROR] Error al configurar tabla postulantes")
        return
    
    if crear_tabla_aparatos():
        print("[OK] Tabla aparatos configurada")
    else:
        print("[ERROR] Error al configurar tabla aparatos")
        return
    
    # Crear tablas nuevas
    if crear_tabla_comunicados():
        print("[OK] Tabla comunicados configurada")
    else:
        print("[ERROR] Error al configurar tabla comunicados")
        return
    
    if crear_tabla_comentarios():
        print("[OK] Tabla comentarios configurada")
    else:
        print("[ERROR] Error al configurar tabla comentarios")
        return
    
    # Crear usuario admin por defecto
    if crear_usuario_admin():
        print("[OK] Usuario admin creado")
    else:
        print("[ERROR] Error al crear usuario admin")
        return
    
    print("\n[SUCCESS] ¡Base de datos configurada exitosamente!")
    print("[CLIPBOARD] Tablas creadas:")
    print("   - usuarios")
    print("   - postulantes") 
    print("   - aparatos_biometricos")
    print("   - comunicados")
    print("   - comentarios")
    print("\n[USER] Usuario admin creado:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")

if __name__ == "__main__":
    main() 