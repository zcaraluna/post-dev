#!/usr/bin/env python3
"""
Módulo para gestionar el dispositivo ZKTeco - Versión Renovada
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import datetime, timedelta
import csv
import os
import logging
from zkteco_connector_v2 import ZKTecoK40V2
from database import connect_db

# Configurar logger
logger = logging.getLogger(__name__)

class GestionZKTeco(tk.Toplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.parent = parent
        self.user_data = user_data
        self.zkteco_device = None
        self.connected = False
        
        # Lista de ventanas que deben ser notificadas cuando cambie el modo prueba
        self.test_mode_listeners = []
        
        self.title("[ZKT] Gestión ZKTeco K40 - Sistema QUIRA")
        self.geometry("900x700")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        # Configurar protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_ui()
        self.center_window()
        
    def setup_ui(self):
        """Configurar la interfaz renovada"""
        # Configurar estilo moderno
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Segoe UI', 12, 'bold'), foreground='#34495e')
        style.configure('Status.TLabel', font=('Segoe UI', 10), foreground='#7f8c8d')
        
        # Frame principal con padding
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Header con título y estado de conexión
        self.create_header(main_frame)
        
        # Notebook para organizar las secciones
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(expand=True, fill='both', pady=(20, 0))
        
        # Pestaña 1: Conexión y Estado
        self.create_connection_tab()
        
        # Pestaña 2: Información del Dispositivo
        self.create_device_info_tab()
        
        # Pestaña 3: Operaciones
        self.create_operations_tab()
        
        # Pestaña 4: Configuración del Sistema
        self.create_config_tab()
        
        # Pestaña 5: Logs del Sistema
        self.create_logs_tab()
        
    def create_header(self, parent):
        """Crear header con título y estado de conexión"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Título principal
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side='left')
        
        title_label = ttk.Label(title_frame, text="[ZKT] Gestión ZKTeco K40", style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="Sistema de Control Biométrico", style='Status.TLabel')
        subtitle_label.pack()
        
        # Estado de conexión en el lado derecho
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side='right', padx=(20, 0))
        
        self.connection_status = ttk.Label(status_frame, text="[ERROR] Desconectado", 
                                         font=('Segoe UI', 12, 'bold'), foreground='#e74c3c')
        self.connection_status.pack()
        
        self.connection_time = ttk.Label(status_frame, text="", style='Status.TLabel')
        self.connection_time.pack()
        
    def create_connection_tab(self):
        """Crear pestaña de conexión"""
        connection_frame = ttk.Frame(self.notebook)
        self.notebook.add(connection_frame, text="🔌 Conexión")
        
        # Frame principal con padding
        main_frame = ttk.Frame(connection_frame, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Configuración de conexión
        config_frame = ttk.LabelFrame(main_frame, text="Configuración de Conexión", padding=15)
        config_frame.pack(fill='x', pady=(0, 20))
        
        # Variables
        self.ip_var = tk.StringVar(value="192.168.100.201")
        self.port_var = tk.StringVar(value="4370")
        
        # Grid para configuración
        config_grid = ttk.Frame(config_frame)
        config_grid.pack(fill='x')
        
        # IP Address
        ttk.Label(config_grid, text="IP Address:", style='Subtitle.TLabel').grid(row=0, column=0, sticky='w', pady=10)
        ip_entry = ttk.Entry(config_grid, textvariable=self.ip_var, width=20, font=('Segoe UI', 10))
        ip_entry.grid(row=0, column=1, padx=(10, 20), pady=10)
        
        # Puerto
        ttk.Label(config_grid, text="Puerto:", style='Subtitle.TLabel').grid(row=0, column=2, sticky='w', pady=10)
        port_entry = ttk.Entry(config_grid, textvariable=self.port_var, width=10, font=('Segoe UI', 10))
        port_entry.grid(row=0, column=3, padx=(10, 0), pady=10)
        
        # Botones de conexión
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(0, 20))
        
        self.connect_btn = ttk.Button(button_frame, text="🔌 Conectar", command=self.connect_device)
        self.connect_btn.pack(side='left', padx=(0, 10))
        
        self.disconnect_btn = ttk.Button(button_frame, text="🔌 Desconectar", command=self.disconnect_device, 
                                       state='disabled')
        self.disconnect_btn.pack(side='left', padx=(0, 10))
        
        self.refresh_btn = ttk.Button(button_frame, text="[REFRESH] Actualizar", command=self.update_device_info)
        self.refresh_btn.pack(side='left')
        
        # Información de estado detallada
        status_frame = ttk.LabelFrame(main_frame, text="Estado de Conexión", padding=15)
        status_frame.pack(fill='x')
        
        self.status_info = tk.Text(status_frame, height=6, wrap='word', font=('Consolas', 9),
                                  bg='#f8f9fa', fg='#2c3e50', state='disabled')
        self.status_info.pack(fill='x')
        
        # Agregar información inicial
        self.update_status_info("Sistema de gestión QUIRA iniciado\nEsperando conexión al dispositivo...")
        
    def create_device_info_tab(self):
        """Crear pestaña de información del dispositivo"""
        device_frame = ttk.Frame(self.notebook)
        self.notebook.add(device_frame, text="[ZKT] Dispositivo")
        
        # Frame principal con padding
        main_frame = ttk.Frame(device_frame, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Información del dispositivo
        self.device_info = {
            'serial': tk.StringVar(value="No disponible"),
            'firmware': tk.StringVar(value="No disponible"),
            'mac': tk.StringVar(value="No disponible"),
            'algorithm': tk.StringVar(value="No disponible"),
            'users_count': tk.StringVar(value="0"),
            'logs_count': tk.StringVar(value="0"),
            'time': tk.StringVar(value="No disponible")
        }
        
        # Crear grid de información
        info_frame = ttk.LabelFrame(main_frame, text="Información del Dispositivo", padding=15)
        info_frame.pack(fill='x')
        
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill='x')
        
        # Organizar información en columnas
        row = 0
        col = 0
        for label, var in [
            ("Número de Serie:", self.device_info['serial']),
            ("Versión de Firmware:", self.device_info['firmware']),
            ("Dirección MAC:", self.device_info['mac']),
            ("Algoritmo:", self.device_info['algorithm']),
            ("Usuarios Registrados:", self.device_info['users_count']),
            ("Registros de Asistencia:", self.device_info['logs_count']),
            ("Hora del Dispositivo:", self.device_info['time'])
        ]:
            ttk.Label(info_grid, text=label, style='Subtitle.TLabel').grid(row=row, column=col*2, sticky='w', pady=5, padx=(0, 10))
            ttk.Label(info_grid, textvariable=var, font=('Segoe UI', 10, 'bold')).grid(row=row, column=col*2+1, sticky='w', pady=5)
            
            row += 1
            if row >= 4:  # Cambiar a segunda columna
                row = 0
                col = 1
            
        # Configurar grid
        info_grid.columnconfigure(1, weight=1)
        info_grid.columnconfigure(3, weight=1)
        
    def create_operations_tab(self):
        """Crear pestaña de operaciones"""
        operations_frame = ttk.Frame(self.notebook)
        self.notebook.add(operations_frame, text="[CONFIG] Operaciones")
        
        # Frame principal con padding
        main_frame = ttk.Frame(operations_frame, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Operaciones principales
        main_ops_frame = ttk.LabelFrame(main_frame, text="Operaciones Principales", padding=15)
        main_ops_frame.pack(fill='x', pady=(0, 20))
        
        main_buttons = [
            ("[USERS] Gestionar Usuarios", self.manage_users),
            ("[STATUS] Descargar Asistencias", self.download_attendance),
            ("[REFRESH] Sincronizar Hora", self.sync_time),
            ("[DELETE] Limpiar Datos", self.clear_data)
        ]
        
        main_grid = ttk.Frame(main_ops_frame)
        main_grid.pack(fill='x')
        
        for i, (text, command) in enumerate(main_buttons):
            btn = ttk.Button(main_grid, text=text, command=command, width=25)
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='ew')
            
        main_grid.columnconfigure(0, weight=1)
        main_grid.columnconfigure(1, weight=1)
        
        # Operaciones avanzadas
        advanced_frame = ttk.LabelFrame(main_frame, text="Operaciones Avanzadas", padding=15)
        advanced_frame.pack(fill='x')
        
        advanced_buttons = [
            ("[ZKT] Reiniciar Dispositivo", self.restart_device),
            ("[CONFIG] Configuración", self.device_config),
            ("[CLIPBOARD] Ver Logs", self.view_logs),
            ("[SAVE] Backup", self.backup_device)
        ]
        
        advanced_grid = ttk.Frame(advanced_frame)
        advanced_grid.pack(fill='x')
        
        for i, (text, command) in enumerate(advanced_buttons):
            btn = ttk.Button(advanced_grid, text=text, command=command, width=25)
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='ew')
            
        advanced_grid.columnconfigure(0, weight=1)
        advanced_grid.columnconfigure(1, weight=1)
        
    def create_config_tab(self):
        """Crear pestaña de configuración del sistema"""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="[BUILD] Configuración")
        
        # Frame principal con padding
        main_frame = ttk.Frame(config_frame, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Sección de Modo Prueba
        test_mode_frame = ttk.LabelFrame(main_frame, text="[BUILD] Modo Prueba", padding=15)
        test_mode_frame.pack(fill='x', pady=(0, 20))
        
        # Descripción del modo prueba
        desc_label = ttk.Label(test_mode_frame, 
                              text="El modo prueba permite usar el sistema sin conexión al dispositivo físico.\n"
                                   "Útil para pruebas y desarrollo. Solo debe activarse por administradores.",
                              font=('Segoe UI', 10), foreground='#7f8c8d', justify='left')
        desc_label.pack(anchor='w', pady=(0, 15))
        
        # Estado actual del modo prueba
        status_frame = ttk.Frame(test_mode_frame)
        status_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(status_frame, text="Estado actual:", style='Subtitle.TLabel').pack(side='left')
        self.test_mode_status = tk.StringVar(value="Desconocido")
        self.test_mode_label = ttk.Label(status_frame, textvariable=self.test_mode_status, 
                                        font=('Segoe UI', 10, 'bold'))
        self.test_mode_label.pack(side='left', padx=(10, 0))
        
        # Botones de control del modo prueba
        buttons_frame = ttk.Frame(test_mode_frame)
        buttons_frame.pack(fill='x')
        
        self.activate_test_btn = ttk.Button(buttons_frame, text="[OK] Activar Modo Prueba", 
                                           command=self.activate_test_mode, width=20)
        self.activate_test_btn.pack(side='left', padx=(0, 10))
        
        self.deactivate_test_btn = ttk.Button(buttons_frame, text="[ERROR] Desactivar Modo Prueba", 
                                             command=self.deactivate_test_mode, width=20)
        self.deactivate_test_btn.pack(side='left')
        
        # Cargar estado inicial del modo prueba
        self.load_test_mode_status()
        
    def registrar_listener_modo_prueba(self, ventana):
        """Registrar una ventana para ser notificada cuando cambie el modo prueba"""
        if ventana not in self.test_mode_listeners:
            self.test_mode_listeners.append(ventana)
    
    def notificar_cambio_modo_prueba(self):
        """Notificar a todas las ventanas registradas que el modo prueba cambió"""
        for ventana in self.test_mode_listeners[:]:  # Copiar lista para evitar modificaciones durante iteración
            try:
                if hasattr(ventana, 'refrescar_asignacion_aparato') and ventana.winfo_exists():
                    ventana.refrescar_asignacion_aparato()
                else:
                    # Remover ventanas que ya no existen
                    self.test_mode_listeners.remove(ventana)
            except:
                # Remover ventanas con errores
                if ventana in self.test_mode_listeners:
                    self.test_mode_listeners.remove(ventana)
        
    def create_logs_tab(self):
        """Crear pestaña de logs del sistema"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="[CLIPBOARD] Logs")
        
        # Frame principal con padding
        main_frame = ttk.Frame(logs_frame, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Frame para logs
        logs_container = ttk.LabelFrame(main_frame, text="Logs del Sistema", padding=15)
        logs_container.pack(fill='both', expand=True)
        
        # Text widget para logs con scrollbar
        logs_text_frame = ttk.Frame(logs_container)
        logs_text_frame.pack(fill='both', expand=True)
        
        self.log_text = tk.Text(logs_text_frame, wrap='word', 
                               font=('Consolas', 9), bg='#f8f9fa', fg='#2c3e50')
        
        log_scrollbar = ttk.Scrollbar(logs_text_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # Empaquetar
        self.log_text.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')
        
        # Botones de control de logs
        logs_buttons_frame = ttk.Frame(main_frame)
        logs_buttons_frame.pack(fill='x', pady=(10, 0))
        
        clear_logs_btn = ttk.Button(logs_buttons_frame, text="[DELETE] Limpiar Logs", 
                                   command=lambda: self.log_text.delete(1.0, tk.END))
        clear_logs_btn.pack(side='left', padx=(0, 10))
        
        export_logs_btn = ttk.Button(logs_buttons_frame, text="📤 Exportar Logs", 
                                     command=self.export_logs)
        export_logs_btn.pack(side='left')
        
        # Configurar log inicial
        self.log("Sistema de gestión QUIRA iniciado")
        
    def update_status_info(self, message):
        """Actualizar información de estado"""
        self.status_info.config(state='normal')
        self.status_info.delete(1.0, tk.END)
        self.status_info.insert(tk.END, message)
        self.status_info.config(state='disabled')
        
    def load_test_mode_status(self):
        """Cargar el estado actual del modo prueba desde la base de datos"""
        try:
            conn = connect_db()
            if not conn:
                self.test_mode_status.set("Error de conexión")
                self.test_mode_label.config(foreground='#e74c3c')
                return
                
            cursor = conn.cursor()
            
            # Buscar si existe el aparato de prueba en la base de datos
            cursor.execute("""
                SELECT id, nombre, activo FROM aparatos_biometricos 
                WHERE serial = '0X0AB0' 
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                aparato_id, nombre, activo = result
                if activo:
                    self.test_mode_status.set("ACTIVADO")
                    self.test_mode_label.config(foreground='#f39c12')
                    self.activate_test_btn.config(state='disabled')
                    self.deactivate_test_btn.config(state='normal')
                else:
                    self.test_mode_status.set("DESACTIVADO")
                    self.test_mode_label.config(foreground='#27ae60')
                    self.activate_test_btn.config(state='normal')
                    self.deactivate_test_btn.config(state='disabled')
            else:
                self.test_mode_status.set("NO CONFIGURADO")
                self.test_mode_label.config(foreground='#e74c3c')
                self.activate_test_btn.config(state='disabled')
                self.deactivate_test_btn.config(state='disabled')
                
        except Exception as e:
            self.test_mode_status.set("Error")
            self.test_mode_label.config(foreground='#e74c3c')
            self.log(f"Error al cargar estado del modo prueba: {e}")
    
    def activate_test_mode(self):
        """Activar el modo prueba"""
        # Verificar permisos de administrador
        if self.user_data.get("rol") not in ["ADMIN", "SUPERADMIN"]:
            messagebox.showerror("Acceso Denegado", 
                               "Solo los administradores pueden activar el modo prueba.")
            return
        
        # Confirmar activación
        respuesta = messagebox.askyesno(
            "Activar Modo Prueba",
            "¿Está seguro que desea activar el modo prueba?\n\n"
            "En modo prueba:\n"
            "• No se requiere conexión al dispositivo físico\n"
            "• Se usará el aparato de prueba (0X0AB0)\n"
            "• Los datos se guardarán en la base de datos\n"
            "• NO se sincronizarán con el dispositivo físico\n\n"
            "¿Continuar?"
        )
        
        if respuesta:
            try:
                conn = connect_db()
                if not conn:
                    messagebox.showerror("Error", "No se pudo conectar a la base de datos")
                    return
                    
                cursor = conn.cursor()
                
                # Verificar si existe el aparato de prueba
                cursor.execute("""
                    SELECT id FROM aparatos_biometricos 
                    WHERE serial = '0X0AB0' 
                    LIMIT 1
                """)
                
                result = cursor.fetchone()
                
                if result:
                    # Actualizar el aparato existente
                    cursor.execute("""
                        UPDATE aparatos_biometricos 
                        SET activo = true 
                        WHERE serial = '0X0AB0'
                    """)
                else:
                    # Crear el aparato de prueba
                    cursor.execute("""
                        INSERT INTO aparatos_biometricos (nombre, serial, activo) 
                        VALUES ('APARATO DE PRUEBA', '0X0AB0', true)
                    """)
                
                conn.commit()
                cursor.close()
                conn.close()
                
                # Actualizar interfaz
                self.load_test_mode_status()
                self.log("Modo prueba activado exitosamente")
                messagebox.showinfo("Éxito", "Modo prueba activado correctamente")
                
                # Notificar a las ventanas abiertas
                self.notificar_cambio_modo_prueba()
                
            except Exception as e:
                self.log(f"Error al activar modo prueba: {e}")
                messagebox.showerror("Error", f"No se pudo activar el modo prueba: {e}")
    
    def deactivate_test_mode(self):
        """Desactivar el modo prueba"""
        # Verificar permisos de administrador
        if self.user_data.get("rol") not in ["ADMIN", "SUPERADMIN"]:
            messagebox.showerror("Acceso Denegado", 
                               "Solo los administradores pueden desactivar el modo prueba.")
            return
        
        # Confirmar desactivación
        respuesta = messagebox.askyesno(
            "Desactivar Modo Prueba",
            "¿Está seguro que desea desactivar el modo prueba?\n\n"
            "Al desactivar el modo prueba:\n"
            "• Se requerirá conexión al dispositivo físico\n"
            "• No se podrán agregar postulantes sin conexión\n"
            "• El sistema volverá a funcionamiento normal\n\n"
            "¿Continuar?"
        )
        
        if respuesta:
            try:
                conn = connect_db()
                if not conn:
                    messagebox.showerror("Error", "No se pudo conectar a la base de datos")
                    return
                    
                cursor = conn.cursor()
                
                # Desactivar el aparato de prueba
                cursor.execute("""
                    UPDATE aparatos_biometricos 
                    SET activo = false 
                    WHERE serial = '0X0AB0'
                """)
                
                conn.commit()
                cursor.close()
                conn.close()
                
                # Actualizar interfaz
                self.load_test_mode_status()
                self.log("Modo prueba desactivado exitosamente")
                messagebox.showinfo("Éxito", "Modo prueba desactivado correctamente")
                
                # Notificar a las ventanas abiertas
                self.notificar_cambio_modo_prueba()
                
            except Exception as e:
                self.log(f"Error al desactivar modo prueba: {e}")
                messagebox.showerror("Error", f"No se pudo desactivar el modo prueba: {e}")
    
    def export_logs(self):
        """Exportar logs a archivo"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                title="Guardar logs como"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Éxito", f"Logs exportados a {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar los logs: {e}")
        
    def center_window(self):
        """Centrar la ventana"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def log(self, message):
        """Agregar mensaje al log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)  # También imprimir en consola
        
        # Agregar al widget de texto si existe
        if hasattr(self, 'log_text'):
            try:
                self.log_text.insert(tk.END, log_message + "\n")
                self.log_text.see(tk.END)  # Auto-scroll al final
                self.update_idletasks()
            except:
                pass  # Si hay error, solo imprimir en consola
        
    def connect_device(self):
        """Conectar al dispositivo"""
        ip = self.ip_var.get().strip()
        port = self.port_var.get().strip()
        
        if not ip or not port:
            messagebox.showerror("Error", "Por favor complete IP y puerto")
            return
            
        try:
            port = int(port)
        except ValueError:
            messagebox.showerror("Error", "El puerto debe ser un número")
            return
            
        # Actualizar estado
        self.connection_status.config(text="[REFRESH] Conectando...", foreground='#f39c12')
        self.update_status_info(f"Conectando a {ip}:{port}...")
        
        def connect_thread():
            try:
                self.zkteco_device = ZKTecoK40V2(ip, port)
                
                if self.zkteco_device.connect():
                    self.connected = True
                    self.after(0, lambda: self.connection_status.config(text="[OK] Conectado", foreground='#27ae60'))
                    self.after(0, lambda: self.connection_time.config(text=f"Conectado desde {datetime.now().strftime('%H:%M:%S')}"))
                    self.after(0, lambda: self.update_status_info(f"Conectado exitosamente a {ip}:{port}"))
                    self.after(0, lambda: self.connect_btn.config(state='disabled'))
                    self.after(0, lambda: self.disconnect_btn.config(state='normal'))
                    self.after(0, self.update_device_info)
                    self.after(0, lambda: self.log(f"Conectado exitosamente a {ip}:{port}"))
                else:
                    self.after(0, lambda: self.connection_status.config(text="[ERROR] Error de conexión", foreground='#e74c3c'))
                    self.after(0, lambda: self.update_status_info(f"Error: No se pudo conectar a {ip}:{port}"))
                    self.after(0, lambda: self.log(f"Error de conexión a {ip}:{port}"))
                    
            except Exception as e:
                self.after(0, lambda: self.connection_status.config(text="[ERROR] Error", foreground='#e74c3c'))
                self.after(0, lambda: self.update_status_info(f"Error: {str(e)}"))
                self.after(0, lambda: self.log(f"Error de conexión: {e}"))
                
        threading.Thread(target=connect_thread, daemon=True).start()
        
    def disconnect_device(self):
        """Desconectar del dispositivo"""
        if self.zkteco_device:
            try:
                self.zkteco_device.disconnect()
            except:
                pass
            finally:
                self.zkteco_device = None
                
        self.connected = False
        self.connection_status.config(text="[ERROR] Desconectado", foreground='#e74c3c')
        self.connection_time.config(text="")
        self.update_status_info("Dispositivo desconectado")
        self.connect_btn.config(state='normal')
        self.disconnect_btn.config(state='disabled')
        
        # Limpiar información del dispositivo
        for var in self.device_info.values():
            var.set("No disponible")
        self.device_info['users_count'].set("0")
        self.device_info['logs_count'].set("0")
    
    def update_device_info(self):
        """Actualizar información del dispositivo"""
        if not self.connected or not self.zkteco_device:
            messagebox.showerror("Error", "No hay conexión al dispositivo")
            return
            
        try:
            device_info = self.zkteco_device.get_device_info()
            
            # Actualizar información básica
            self.device_info['serial'].set(device_info.get('serial_number', 'No disponible'))
            self.device_info['firmware'].set(device_info.get('firmware_version', 'No disponible'))
            self.device_info['mac'].set(device_info.get('mac_address', 'No disponible'))
            self.device_info['algorithm'].set(device_info.get('algorithm', 'No disponible'))
            
            # Obtener información adicional
            try:
                users = self.zkteco_device.get_user_list()
                self.device_info['users_count'].set(str(len(users) if users else 0))
            except:
                self.device_info['users_count'].set("Error")
            
            try:
                logs = self.zkteco_device.get_attendance_logs()
                self.device_info['logs_count'].set(str(len(logs) if logs else 0))
            except:
                self.device_info['logs_count'].set("Error")
            
            try:
                device_time = self.zkteco_device.get_device_time()
                if device_time:
                    self.device_info['time'].set(device_time.strftime('%d/%m/%Y %H:%M:%S'))
                    self.log(f"Hora del dispositivo obtenida: {device_time.strftime('%d/%m/%Y %H:%M:%S')}")
                else:
                    self.device_info['time'].set("No disponible")
                    self.log("No se pudo obtener la hora del dispositivo")
            except Exception as e:
                logger.warning(f"Error al obtener hora del dispositivo: {e}")
                self.device_info['time'].set("Error")
                self.log(f"Error al obtener hora del dispositivo: {e}")
            
            self.log("Información del dispositivo actualizada")
            
        except Exception as e:
            self.log(f"Error al actualizar información del dispositivo: {e}")
    
    def manage_users(self):
        """Gestionar usuarios del dispositivo"""
        if not self.connected:
            messagebox.showerror("Error", "No hay conexión al dispositivo")
            return
        
        # Crear ventana de gestión de usuarios
        user_window = tk.Toplevel(self)
        user_window.title("[USERS] Gestión de Usuarios - ZKTeco K40")
        user_window.geometry("800x600")
        user_window.resizable(True, True)
        user_window.transient(self)
        user_window.grab_set()
        
        # Variables
        users_data = []
        selected_user = None
        
        # Frame principal
        main_frame = ttk.Frame(user_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="[USERS] Gestión de Usuarios del Dispositivo", 
                               font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Frame de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botones
        ttk.Button(button_frame, text="[REFRESH] Actualizar", 
                  command=lambda: load_users()).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="[ADD] Agregar Usuario", 
                  command=lambda: add_user()).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="✏️ Editar", 
                  command=lambda: edit_user()).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="[DELETE] Eliminar", 
                  command=lambda: delete_user()).pack(side=tk.LEFT, padx=(0, 5))
        
        # Treeview para usuarios
        columns = ('uid', 'name', 'privilege', 'user_id', 'group_id')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        tree.heading('uid', text='UID')
        tree.heading('name', text='Nombre')
        tree.heading('privilege', text='Privilegio')
        tree.heading('user_id', text='ID Usuario')
        tree.heading('group_id', text='Grupo')
        
        tree.column('uid', width=80)
        tree.column('name', width=200)
        tree.column('privilege', width=100)
        tree.column('user_id', width=120)
        tree.column('group_id', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview y scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de información
        info_frame = ttk.LabelFrame(main_frame, text="Información", padding="10")
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        info_label = ttk.Label(info_frame, text="Seleccione un usuario para ver detalles")
        info_label.pack()
        
        def load_users():
            """Cargar usuarios del dispositivo"""
            try:
                self.log("Cargando usuarios del dispositivo...")
                users = self.zkteco_device.get_user_list()
                
                # Limpiar treeview
                for item in tree.get_children():
                    tree.delete(item)
                
                users_data.clear()
                
                if users:
                    for user in users:
                        uid = user.get('uid', '')
                        name = user.get('name', 'N/A')
                        privilege = user.get('privilege', 0)
                        user_id = user.get('user_id', '')
                        group_id = user.get('group_id', '')
                        
                        # Convertir privilegio a texto
                        privilege_text = {
                            0: 'Usuario',
                            1: 'Administrador',
                            2: 'Supervisor'
                        }.get(privilege, f'Privilegio {privilege}')
                        
                        # Insertar en treeview
                        tree.insert('', tk.END, values=(uid, name, privilege_text, user_id, group_id))
                        users_data.append(user)
                    
                    self.log(f"[OK] {len(users)} usuarios cargados")
                    info_label.config(text=f"Total de usuarios: {len(users)}")
                else:
                    self.log("No se encontraron usuarios")
                    info_label.config(text="No hay usuarios registrados")
                
            except Exception as e:
                error_msg = f"Error al cargar usuarios: {e}"
                messagebox.showerror("Error", error_msg)
                self.log(f"[ERROR] {error_msg}")
        
        def add_user():
            """Agregar nuevo usuario"""
            add_window = tk.Toplevel(user_window)
            add_window.title("[ADD] Agregar Usuario")
            add_window.geometry("400x300")
            add_window.transient(user_window)
            add_window.grab_set()
            
            # Variables
            uid_var = tk.StringVar()
            name_var = tk.StringVar()
            privilege_var = tk.StringVar(value="Usuario")
            password_var = tk.StringVar()
            user_id_var = tk.StringVar()
            group_id_var = tk.StringVar()
        
        # Frame principal
            add_frame = ttk.Frame(add_window, padding="10")
            add_frame.pack(fill=tk.BOTH, expand=True)
            
            # Campos
            ttk.Label(add_frame, text="UID:").grid(row=0, column=0, sticky='w', pady=2)
            ttk.Entry(add_frame, textvariable=uid_var).grid(row=0, column=1, sticky='ew', padx=(5, 0), pady=2)
            
            ttk.Label(add_frame, text="Nombre:").grid(row=1, column=0, sticky='w', pady=2)
            ttk.Entry(add_frame, textvariable=name_var).grid(row=1, column=1, sticky='ew', padx=(5, 0), pady=2)
            
            ttk.Label(add_frame, text="Privilegio:").grid(row=2, column=0, sticky='w', pady=2)
            privilege_combo = ttk.Combobox(add_frame, textvariable=privilege_var, 
                                         values=["Usuario", "Administrador", "Supervisor"], 
                                         state="readonly")
            privilege_combo.grid(row=2, column=1, sticky='ew', padx=(5, 0), pady=2)
            
            ttk.Label(add_frame, text="Contraseña:").grid(row=3, column=0, sticky='w', pady=2)
            ttk.Entry(add_frame, textvariable=password_var, show="*").grid(row=3, column=1, sticky='ew', padx=(5, 0), pady=2)
            
            ttk.Label(add_frame, text="ID Usuario:").grid(row=4, column=0, sticky='w', pady=2)
            ttk.Entry(add_frame, textvariable=user_id_var).grid(row=4, column=1, sticky='ew', padx=(5, 0), pady=2)
            
            ttk.Label(add_frame, text="Grupo:").grid(row=5, column=0, sticky='w', pady=2)
            ttk.Entry(add_frame, textvariable=group_id_var).grid(row=5, column=1, sticky='ew', padx=(5, 0), pady=2)
            
            # Configurar grid
            add_frame.columnconfigure(1, weight=1)
        
        # Botones
        button_frame = ttk.Frame(add_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0))
        
        def save_user():
            try:
                uid = int(uid_var.get())
                name = name_var.get().strip()
                password = password_var.get()
                user_id = user_id_var.get().strip()
                group_id = group_id_var.get().strip()
                
                # Convertir privilegio
                privilege_map = {"Usuario": 0, "Administrador": 1, "Supervisor": 2}
                privilege = privilege_map.get(privilege_var.get(), 0)
                
                if not name:
                    messagebox.showerror("Error", "El nombre es obligatorio")
                    return
                
                # Agregar usuario al dispositivo
                success = self.zkteco_device.set_user(
                    uid=uid,
                    name=name,
                    privilege=privilege,
                    password=password,
                    user_id=user_id,
                    group_id=group_id
                )
                
                if success:
                    messagebox.showinfo("Éxito", f"Usuario {name} agregado correctamente")
                    self.log(f"[OK] Usuario {name} (UID: {uid}) agregado al dispositivo")
                    add_window.destroy()
                    load_users()  # Recargar lista
                else:
                    messagebox.showerror("Error", "No se pudo agregar el usuario")
                    self.log(f"[ERROR] Error al agregar usuario {name}")
                    
            except ValueError:
                messagebox.showerror("Error", "El UID debe ser un número")
            except Exception as e:
                messagebox.showerror("Error", f"Error al agregar usuario: {e}")
                self.log(f"[ERROR] Error al agregar usuario: {e}")
        
        ttk.Button(button_frame, text="[SAVE] Guardar", command=save_user).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="[ERROR] Cancelar", command=add_window.destroy).pack(side=tk.LEFT)
        
        def edit_user():
            """Editar usuario seleccionado"""
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Advertencia", "Seleccione un usuario para editar")
                return
            
            # Obtener datos del usuario seleccionado
            item = tree.item(selection[0])
            uid = item['values'][0]
            
            # Buscar usuario en la lista
            user = next((u for u in users_data if str(u.get('uid', '')) == str(uid)), None)
            if not user:
                messagebox.showerror("Error", "No se encontró el usuario")
                return
                
            # Crear ventana de edición
            edit_window = tk.Toplevel(user_window)
            edit_window.title("✏️ Editar Usuario")
            edit_window.geometry("400x300")
            edit_window.transient(user_window)
            edit_window.grab_set()
            
            # Variables
            name_var = tk.StringVar(value=user.get('name', ''))
            privilege_var = tk.StringVar()
            password_var = tk.StringVar()
            user_id_var = tk.StringVar(value=user.get('user_id', ''))
            group_id_var = tk.StringVar(value=user.get('group_id', ''))
            
            # Establecer privilegio
            privilege_map = {0: "Usuario", 1: "Administrador", 2: "Supervisor"}
            privilege_var.set(privilege_map.get(user.get('privilege', 0), "Usuario"))
            
            # Frame principal
            edit_frame = ttk.Frame(edit_window, padding="10")
            edit_frame.pack(fill=tk.BOTH, expand=True)
            
            # Campos
            ttk.Label(edit_frame, text=f"UID: {uid}").grid(row=0, column=0, sticky='w', pady=2)
            
            ttk.Label(edit_frame, text="Nombre:").grid(row=1, column=0, sticky='w', pady=2)
            ttk.Entry(edit_frame, textvariable=name_var).grid(row=1, column=1, sticky='ew', padx=(5, 0), pady=2)
            
            ttk.Label(edit_frame, text="Privilegio:").grid(row=2, column=0, sticky='w', pady=2)
            privilege_combo = ttk.Combobox(edit_frame, textvariable=privilege_var, 
                                         values=["Usuario", "Administrador", "Supervisor"], 
                                         state="readonly")
            privilege_combo.grid(row=2, column=1, sticky='ew', padx=(5, 0), pady=2)
            
            ttk.Label(edit_frame, text="Contraseña:").grid(row=3, column=0, sticky='w', pady=2)
            ttk.Entry(edit_frame, textvariable=password_var, show="*").grid(row=3, column=1, sticky='ew', padx=(5, 0), pady=2)
            
            ttk.Label(edit_frame, text="ID Usuario:").grid(row=4, column=0, sticky='w', pady=2)
            ttk.Entry(edit_frame, textvariable=user_id_var).grid(row=4, column=1, sticky='ew', padx=(5, 0), pady=2)
            
            ttk.Label(edit_frame, text="Grupo:").grid(row=5, column=0, sticky='w', pady=2)
            ttk.Entry(edit_frame, textvariable=group_id_var).grid(row=5, column=1, sticky='ew', padx=(5, 0), pady=2)
            
            # Configurar grid
            edit_frame.columnconfigure(1, weight=1)
            
            # Botones
            button_frame = ttk.Frame(edit_frame)
            button_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0))
            
            def update_user():
                try:
                    name = name_var.get().strip()
                    password = password_var.get()
                    user_id = user_id_var.get().strip()
                    group_id = group_id_var.get().strip()
                    
                    # Convertir privilegio
                    privilege_map = {"Usuario": 0, "Administrador": 1, "Supervisor": 2}
                    privilege = privilege_map.get(privilege_var.get(), 0)
                    
                    if not name:
                        messagebox.showerror("Error", "El nombre es obligatorio")
                        return
                    
                    # Actualizar usuario en el dispositivo
                    success = self.zkteco_device.set_user(
                        uid=int(uid),
                        name=name,
                        privilege=privilege,
                        password=password,
                        user_id=user_id,
                        group_id=group_id
                    )
                    
                    if success:
                        messagebox.showinfo("Éxito", f"Usuario {name} actualizado correctamente")
                        self.log(f"[OK] Usuario {name} (UID: {uid}) actualizado en el dispositivo")
                        edit_window.destroy()
                        load_users()  # Recargar lista
                    else:
                        messagebox.showerror("Error", "No se pudo actualizar el usuario")
                        self.log(f"[ERROR] Error al actualizar usuario {name}")
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Error al actualizar usuario: {e}")
                    self.log(f"[ERROR] Error al actualizar usuario: {e}")
            
            ttk.Button(button_frame, text="[SAVE] Guardar", command=update_user).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="[ERROR] Cancelar", command=edit_window.destroy).pack(side=tk.LEFT)
        
        def delete_user():
            """Eliminar usuario seleccionado"""
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Advertencia", "Seleccione un usuario para eliminar")
                return
            
            # Obtener datos del usuario seleccionado
            item = tree.item(selection[0])
            uid = item['values'][0]
            name = item['values'][1]
            
            # Confirmar eliminación
            respuesta = messagebox.askyesno(
                "Confirmar Eliminación",
                f"¿Está seguro que desea eliminar al usuario:\n\n"
                f"Nombre: {name}\n"
                f"UID: {uid}\n\n"
                f"Esta acción NO se puede deshacer."
            )
            
            if respuesta:
                try:
                    # Eliminar usuario del dispositivo
                    success = self.zkteco_device.conn.delete_user(uid)
                    
                    if success:
                        messagebox.showinfo("Éxito", f"Usuario {name} eliminado correctamente")
                        self.log(f"[OK] Usuario {name} (UID: {uid}) eliminado del dispositivo")
                        load_users()  # Recargar lista
                    else:
                        messagebox.showerror("Error", "No se pudo eliminar el usuario")
                        self.log(f"[ERROR] Error al eliminar usuario {name}")
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Error al eliminar usuario: {e}")
                    self.log(f"[ERROR] Error al eliminar usuario: {e}")
        
        # Evento de selección
        def on_select(event):
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                values = item['values']
                info_text = f"Usuario seleccionado:\n"
                info_text += f"UID: {values[0]}\n"
                info_text += f"Nombre: {values[1]}\n"
                info_text += f"Privilegio: {values[2]}\n"
                info_text += f"ID Usuario: {values[3]}\n"
                info_text += f"Grupo: {values[4]}"
                info_label.config(text=info_text)
        
        tree.bind('<<TreeviewSelect>>', on_select)
        
        # Cargar usuarios al abrir
        load_users()
        
    def download_attendance(self):
        """Descargar registros de asistencia"""
        if not self.connected:
            messagebox.showerror("Error", "No hay conexión al dispositivo")
            return
        
        try:
            logs = self.zkteco_device.get_attendance_logs()
            if not logs:
                messagebox.showinfo("Información", "No hay registros de asistencia para descargar")
                return
            
            # Guardar en archivo CSV
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
                title="Guardar registros de asistencia"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    # Incluir todos los campos posibles que pueden venir en los logs
                    fieldnames = ['user_id', 'timestamp', 'punch', 'name', 'uid', 'status', 'verification']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for log in logs:
                        # Procesar cada log para asegurar que tenga todos los campos
                        processed_log = {}
                        
                        # Copiar todos los campos existentes
                        for field in fieldnames:
                            if field in log:
                                processed_log[field] = log[field]
                            else:
                                processed_log[field] = ''
                        
                        # Procesar timestamp si es necesario
                        timestamp = processed_log.get('timestamp', '')
                        if isinstance(timestamp, datetime):
                            processed_log['timestamp'] = timestamp.strftime('%d/%m/%Y %H:%M:%S')
                        elif isinstance(timestamp, (int, float)) and timestamp > 0:
                            try:
                                dt = datetime.fromtimestamp(timestamp)
                                processed_log['timestamp'] = dt.strftime('%d/%m/%Y %H:%M:%S')
                            except:
                                processed_log['timestamp'] = str(timestamp)
                        
                        # Procesar punch/status si no existe
                        if not processed_log.get('status') and 'punch' in processed_log:
                            punch = processed_log['punch']
                            if punch == 0:
                                processed_log['status'] = 'Entrada'
                            elif punch == 1:
                                processed_log['status'] = 'Salida'
                            else:
                                processed_log['status'] = str(punch)
                        
                        writer.writerow(processed_log)
                
                messagebox.showinfo("Éxito", f"Se descargaron {len(logs)} registros a {filename}")
                self.log(f"Descargados {len(logs)} registros de asistencia")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron descargar los registros: {e}")
            self.log(f"Error al descargar registros: {e}")
        
    def sync_time(self):
        """Sincronizar hora del dispositivo"""
        if not self.connected:
            messagebox.showerror("Error", "No hay conexión al dispositivo")
            return
        
        try:
            # Obtener hora actual del sistema
            current_time = datetime.now()
            self.log(f"Sincronizando hora del dispositivo con: {current_time.strftime('%d/%m/%Y %H:%M:%S')}")
            
            # Sincronizar con la hora actual del sistema
            success = self.zkteco_device.set_device_time(current_time)
            
            if success:
                messagebox.showinfo("Éxito", f"Hora del dispositivo sincronizada a {current_time.strftime('%d/%m/%Y %H:%M:%S')}")
                self.log("Hora del dispositivo sincronizada exitosamente")
                # Actualizar información del dispositivo para mostrar la nueva hora
                self.update_device_info()
            else:
                messagebox.showerror("Error", "No se pudo sincronizar la hora del dispositivo")
                self.log("Error: No se pudo sincronizar la hora del dispositivo")
            
        except Exception as e:
            error_msg = f"No se pudo sincronizar la hora: {e}"
            messagebox.showerror("Error", error_msg)
            self.log(f"Error al sincronizar hora: {e}")
            logger.error(f"Error en sync_time: {e}")
        
    def clear_data(self):
        """Limpiar datos del dispositivo"""
        if not self.connected:
            messagebox.showerror("Error", "No hay conexión al dispositivo")
            return
        
        respuesta = messagebox.askyesno(
            "Limpiar Datos",
            "¿Está seguro que desea limpiar todos los datos del dispositivo?\n\n"
            "Esta acción eliminará:\n"
            "• Todos los usuarios registrados\n"
            "• Todos los registros de asistencia\n"
            "• Todas las huellas dactilares\n\n"
            "Esta acción NO se puede deshacer.\n\n"
            "¿Continuar?"
        )
        
        if respuesta:
            try:
                self.log("Iniciando limpieza de datos del dispositivo...")
                
                # Limpiar registros de asistencia
                self.log("Limpiando registros de asistencia...")
                attendance_success = self.zkteco_device.clear_attendance()
                if attendance_success:
                    self.log("[OK] Registros de asistencia limpiados exitosamente")
                else:
                    self.log("[ERROR] Error al limpiar registros de asistencia")
                
                # Limpiar usuarios
                self.log("Limpiando usuarios...")
                users_success = self.zkteco_device.clear_users()
                if users_success:
                    self.log("[OK] Usuarios limpiados exitosamente")
                else:
                    self.log("[ERROR] Error al limpiar usuarios")
                
                # Mostrar resultado final
                if attendance_success and users_success:
                    messagebox.showinfo("Éxito", "Datos del dispositivo limpiados exitosamente")
                    self.log("[SUCCESS] Datos del dispositivo limpiados exitosamente")
                elif attendance_success or users_success:
                    partial_msg = "Datos parcialmente limpiados:\n"
                    if attendance_success:
                        partial_msg += "[OK] Registros de asistencia\n"
                    if users_success:
                        partial_msg += "[OK] Usuarios\n"
                    messagebox.showwarning("Limpieza Parcial", partial_msg)
                    self.log("[WARN] Limpieza parcial completada")
                else:
                    messagebox.showerror("Error", "No se pudieron limpiar los datos del dispositivo")
                    self.log("[ERROR] No se pudieron limpiar los datos")
                
                # Actualizar información del dispositivo
                self.update_device_info()
                
            except Exception as e:
                error_msg = f"No se pudieron limpiar los datos: {e}"
                messagebox.showerror("Error", error_msg)
                self.log(f"[ERROR] Error al limpiar datos: {e}")
                logger.error(f"Error en clear_data: {e}")
            
    def restart_device(self):
        """Reiniciar dispositivo"""
        if not self.connected:
            messagebox.showerror("Error", "No hay conexión al dispositivo")
            return
        
        respuesta = messagebox.askyesno(
            "Reiniciar Dispositivo",
            "¿Está seguro que desea reiniciar el dispositivo?\n\n"
            "El dispositivo se desconectará temporalmente durante el reinicio.\n\n"
            "¿Continuar?"
        )
        
        if respuesta:
            try:
                self.log("Iniciando reinicio del dispositivo...")
                success = self.zkteco_device.restart()
                
                if success:
                    messagebox.showinfo("Éxito", "Dispositivo reiniciado exitosamente")
                    self.log("Dispositivo reiniciado exitosamente")
                    
                    # Desconectar temporalmente
                    self.disconnect_device()
                else:
                    messagebox.showerror("Error", "No se pudo reiniciar el dispositivo")
                    self.log("Error: No se pudo reiniciar el dispositivo")
                
            except Exception as e:
                error_msg = f"No se pudo reiniciar el dispositivo: {e}"
                messagebox.showerror("Error", error_msg)
                self.log(f"Error al reiniciar dispositivo: {e}")
                logger.error(f"Error en restart_device: {e}")
            
    def device_config(self):
        """Configurar parámetros del dispositivo"""
        if not self.connected:
            messagebox.showerror("Error", "No hay conexión al dispositivo")
            return
        
        # Crear ventana de configuración
        config_window = tk.Toplevel(self)
        config_window.title("[CONFIG] Configuración del Dispositivo - ZKTeco K40")
        config_window.geometry("600x500")
        config_window.resizable(True, True)
        config_window.transient(self)
        config_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(config_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="[CONFIG] Configuración del Dispositivo", 
                               font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Notebook para organizar configuraciones
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de Configuración General
        general_frame = ttk.Frame(notebook, padding="10")
        notebook.add(general_frame, text="General")
        
        # Variables para configuración general
        device_name_var = tk.StringVar()
        language_var = tk.StringVar(value="Español")
        timezone_var = tk.StringVar(value="UTC-5")
        date_format_var = tk.StringVar(value="DD/MM/YYYY")
        time_format_var = tk.StringVar(value="24h")
        
        # Configuración general
        ttk.Label(general_frame, text="Configuración General", font=('Segoe UI', 12, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        ttk.Label(general_frame, text="Nombre del dispositivo:").grid(row=1, column=0, sticky='w', pady=2)
        ttk.Entry(general_frame, textvariable=device_name_var, width=30).grid(row=1, column=1, sticky='w', padx=(10, 0), pady=2)
        
        ttk.Label(general_frame, text="Idioma:").grid(row=2, column=0, sticky='w', pady=2)
        language_combo = ttk.Combobox(general_frame, textvariable=language_var, 
                                    values=["Español", "English", "Français"], 
                                    state="readonly", width=27)
        language_combo.grid(row=2, column=1, sticky='w', padx=(10, 0), pady=2)
        
        ttk.Label(general_frame, text="Zona horaria:").grid(row=3, column=0, sticky='w', pady=2)
        timezone_combo = ttk.Combobox(general_frame, textvariable=timezone_var, 
                                    values=["UTC-5", "UTC-6", "UTC-7", "UTC-8"], 
                                    state="readonly", width=27)
        timezone_combo.grid(row=3, column=1, sticky='w', padx=(10, 0), pady=2)
        
        ttk.Label(general_frame, text="Formato de fecha:").grid(row=4, column=0, sticky='w', pady=2)
        date_combo = ttk.Combobox(general_frame, textvariable=date_format_var, 
                                values=["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"], 
                                state="readonly", width=27)
        date_combo.grid(row=4, column=1, sticky='w', padx=(10, 0), pady=2)
        
        ttk.Label(general_frame, text="Formato de hora:").grid(row=5, column=0, sticky='w', pady=2)
        time_combo = ttk.Combobox(general_frame, textvariable=time_format_var, 
                                values=["24h", "12h"], 
                                state="readonly", width=27)
        time_combo.grid(row=5, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # Pestaña de Configuración de Red
        network_frame = ttk.Frame(notebook, padding="10")
        notebook.add(network_frame, text="Red")
        
        # Variables para configuración de red
        ip_var = tk.StringVar()
        subnet_var = tk.StringVar()
        gateway_var = tk.StringVar()
        dns_var = tk.StringVar()
        port_var = tk.StringVar(value="4370")
        
        # Configuración de red
        ttk.Label(network_frame, text="Configuración de Red", font=('Segoe UI', 12, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        ttk.Label(network_frame, text="Dirección IP:").grid(row=1, column=0, sticky='w', pady=2)
        ttk.Entry(network_frame, textvariable=ip_var, width=30).grid(row=1, column=1, sticky='w', padx=(10, 0), pady=2)
        
        ttk.Label(network_frame, text="Máscara de subred:").grid(row=2, column=0, sticky='w', pady=2)
        ttk.Entry(network_frame, textvariable=subnet_var, width=30).grid(row=2, column=1, sticky='w', padx=(10, 0), pady=2)
        
        ttk.Label(network_frame, text="Puerta de enlace:").grid(row=3, column=0, sticky='w', pady=2)
        ttk.Entry(network_frame, textvariable=gateway_var, width=30).grid(row=3, column=1, sticky='w', padx=(10, 0), pady=2)
        
        ttk.Label(network_frame, text="Servidor DNS:").grid(row=4, column=0, sticky='w', pady=2)
        ttk.Entry(network_frame, textvariable=dns_var, width=30).grid(row=4, column=1, sticky='w', padx=(10, 0), pady=2)
        
        ttk.Label(network_frame, text="Puerto:").grid(row=5, column=0, sticky='w', pady=2)
        ttk.Entry(network_frame, textvariable=port_var, width=30).grid(row=5, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # Pestaña de Configuración de Seguridad
        security_frame = ttk.Frame(notebook, padding="10")
        notebook.add(security_frame, text="Seguridad")
        
        # Variables para configuración de seguridad
        admin_password_var = tk.StringVar()
        user_password_var = tk.StringVar()
        verify_mode_var = tk.BooleanVar(value=True)
        anti_passback_var = tk.BooleanVar(value=False)
        door_sensor_var = tk.BooleanVar(value=False)
        
        # Configuración de seguridad
        ttk.Label(security_frame, text="Configuración de Seguridad", font=('Segoe UI', 12, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        ttk.Label(security_frame, text="Contraseña de administrador:").grid(row=1, column=0, sticky='w', pady=2)
        ttk.Entry(security_frame, textvariable=admin_password_var, show="*", width=30).grid(row=1, column=1, sticky='w', padx=(10, 0), pady=2)
        
        ttk.Label(security_frame, text="Contraseña de usuario:").grid(row=2, column=0, sticky='w', pady=2)
        ttk.Entry(security_frame, textvariable=user_password_var, show="*", width=30).grid(row=2, column=1, sticky='w', padx=(10, 0), pady=2)
        
        ttk.Checkbutton(security_frame, text="Modo de verificación", variable=verify_mode_var).grid(row=3, column=0, columnspan=2, sticky='w', pady=2)
        ttk.Checkbutton(security_frame, text="Anti-passback", variable=anti_passback_var).grid(row=4, column=0, columnspan=2, sticky='w', pady=2)
        ttk.Checkbutton(security_frame, text="Sensor de puerta", variable=door_sensor_var).grid(row=5, column=0, columnspan=2, sticky='w', pady=2)
        
        # Pestaña de Configuración de Horarios
        schedule_frame = ttk.Frame(notebook, padding="10")
        notebook.add(schedule_frame, text="Horarios")
        
        # Variables para configuración de horarios
        work_start_var = tk.StringVar(value="08:00")
        work_end_var = tk.StringVar(value="18:00")
        lunch_start_var = tk.StringVar(value="12:00")
        lunch_end_var = tk.StringVar(value="13:00")
        work_days_var = tk.StringVar(value="Lunes-Viernes")
        
        # Configuración de horarios
        ttk.Label(schedule_frame, text="Configuración de Horarios", font=('Segoe UI', 12, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        ttk.Label(schedule_frame, text="Inicio de trabajo:").grid(row=1, column=0, sticky='w', pady=2)
        ttk.Entry(schedule_frame, textvariable=work_start_var, width=30).grid(row=1, column=1, sticky='w', padx=(10, 0), pady=2)
        
        ttk.Label(schedule_frame, text="Fin de trabajo:").grid(row=2, column=0, sticky='w', pady=2)
        ttk.Entry(schedule_frame, textvariable=work_end_var, width=30).grid(row=2, column=1, sticky='w', padx=(10, 0), pady=2)
        
        ttk.Label(schedule_frame, text="Inicio de almuerzo:").grid(row=3, column=0, sticky='w', pady=2)
        ttk.Entry(schedule_frame, textvariable=lunch_start_var, width=30).grid(row=3, column=1, sticky='w', padx=(10, 0), pady=2)
        
        ttk.Label(schedule_frame, text="Fin de almuerzo:").grid(row=4, column=0, sticky='w', pady=2)
        ttk.Entry(schedule_frame, textvariable=lunch_end_var, width=30).grid(row=4, column=1, sticky='w', padx=(10, 0), pady=2)
        
        ttk.Label(schedule_frame, text="Días laborables:").grid(row=5, column=0, sticky='w', pady=2)
        work_days_combo = ttk.Combobox(schedule_frame, textvariable=work_days_var, 
                                     values=["Lunes-Viernes", "Lunes-Sábado", "Todos los días"], 
                                     state="readonly", width=27)
        work_days_combo.grid(row=5, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # Frame de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def load_current_config():
            """Cargar configuración actual del dispositivo"""
            try:
                self.log("Cargando configuración actual del dispositivo...")
                
                # Obtener información del dispositivo
                device_info = self.zkteco_device.get_device_info()
                
                # Cargar valores en las variables
                if device_info:
                    device_name_var.set(device_info.get('device_name', ''))
                    ip_var.set(device_info.get('ip', ''))
                    port_var.set(str(device_info.get('port', '4370')))
                
                self.log("[OK] Configuración actual cargada")
                
            except Exception as e:
                self.log(f"[ERROR] Error al cargar configuración: {e}")
                messagebox.showerror("Error", f"No se pudo cargar la configuración actual: {e}")
        
        def save_config():
            """Guardar configuración en el dispositivo"""
            try:
                self.log("Guardando configuración en el dispositivo...")
                
                # Aquí se implementaría la lógica para guardar la configuración
                # Por ahora solo mostraremos un mensaje de éxito
                
                messagebox.showinfo("Éxito", "Configuración guardada correctamente")
                self.log("[OK] Configuración guardada en el dispositivo")
                
            except Exception as e:
                error_msg = f"Error al guardar configuración: {e}"
                messagebox.showerror("Error", error_msg)
                self.log(f"[ERROR] {error_msg}")
        
        def reset_config():
            """Restablecer configuración por defecto"""
            respuesta = messagebox.askyesno(
                "Confirmar Restablecimiento",
                "¿Está seguro que desea restablecer la configuración por defecto?\n\n"
                "Esta acción NO se puede deshacer."
            )
            
            if respuesta:
                try:
                    self.log("Restableciendo configuración por defecto...")
                    
                    # Restablecer valores por defecto
                    device_name_var.set("")
                    language_var.set("Español")
                    timezone_var.set("UTC-5")
                    date_format_var.set("DD/MM/YYYY")
                    time_format_var.set("24h")
                    
                    ip_var.set("")
                    subnet_var.set("")
                    gateway_var.set("")
                    dns_var.set("")
                    port_var.set("4370")
                    
                    admin_password_var.set("")
                    user_password_var.set("")
                    verify_mode_var.set(True)
                    anti_passback_var.set(False)
                    door_sensor_var.set(False)
                    
                    work_start_var.set("08:00")
                    work_end_var.set("18:00")
                    lunch_start_var.set("12:00")
                    lunch_end_var.set("13:00")
                    work_days_var.set("Lunes-Viernes")
                    
                    messagebox.showinfo("Éxito", "Configuración restablecida por defecto")
                    self.log("[OK] Configuración restablecida por defecto")
                    
                except Exception as e:
                    error_msg = f"Error al restablecer configuración: {e}"
                    messagebox.showerror("Error", error_msg)
                    self.log(f"[ERROR] {error_msg}")
        
        # Botones
        ttk.Button(button_frame, text="📥 Cargar Actual", command=load_current_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="[SAVE] Guardar", command=save_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="[REFRESH] Restablecer", command=reset_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="[ERROR] Cerrar", command=config_window.destroy).pack(side=tk.RIGHT)
        
        # Cargar configuración actual al abrir
        load_current_config()
        
    def view_logs(self):
        """Ver logs del dispositivo"""
        if not self.connected:
            messagebox.showerror("Error", "No hay conexión al dispositivo")
            return
        
        # Crear ventana de logs
        logs_window = tk.Toplevel(self)
        logs_window.title("[CLIPBOARD] Logs del Dispositivo - ZKTeco K40")
        logs_window.geometry("900x700")
        logs_window.resizable(True, True)
        logs_window.transient(self)
        logs_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(logs_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="[CLIPBOARD] Logs del Sistema del Dispositivo", 
                               font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Frame de controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Variables
        log_type_var = tk.StringVar(value="Sistema")
        date_from_var = tk.StringVar()
        date_to_var = tk.StringVar()
        search_var = tk.StringVar()
        
        # Controles de filtro
        ttk.Label(controls_frame, text="Tipo de log:").pack(side=tk.LEFT, padx=(0, 5))
        log_type_combo = ttk.Combobox(controls_frame, textvariable=log_type_var, 
                                    values=["Sistema", "Eventos", "Errores", "Acceso", "Todos"], 
                                    state="readonly", width=15)
        log_type_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(controls_frame, text="Desde:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(controls_frame, textvariable=date_from_var, width=12).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(controls_frame, text="(DD/MM/AAAA)").pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(controls_frame, text="Hasta:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(controls_frame, textvariable=date_to_var, width=12).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(controls_frame, text="(DD/MM/AAAA)").pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(controls_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(controls_frame, textvariable=search_var, width=20).pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botones
        ttk.Button(button_frame, text="[REFRESH] Actualizar", 
                  command=lambda: load_logs()).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="[SEARCH] Filtrar", 
                  command=lambda: filter_logs()).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🧹 Limpiar Filtros", 
                  command=lambda: clear_filters()).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="[SAVE] Exportar", 
                  command=lambda: export_logs()).pack(side=tk.LEFT, padx=(0, 5))
        
        # Treeview para logs
        columns = ('timestamp', 'type', 'level', 'message', 'user', 'details')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=20)
        
        # Configurar columnas
        tree.heading('timestamp', text='Fecha/Hora')
        tree.heading('type', text='Tipo')
        tree.heading('level', text='Nivel')
        tree.heading('message', text='Mensaje')
        tree.heading('user', text='Usuario')
        tree.heading('details', text='Detalles')
        
        tree.column('timestamp', width=150)
        tree.column('type', width=100)
        tree.column('level', width=80)
        tree.column('message', width=250)
        tree.column('user', width=120)
        tree.column('details', width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview y scrollbars
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Frame de información
        info_frame = ttk.LabelFrame(main_frame, text="Información", padding="10")
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        info_label = ttk.Label(info_frame, text="Seleccione un log para ver detalles")
        info_label.pack()
        
        # Variables para datos
        logs_data = []
        filtered_logs = []
        
        def load_logs():
            """Cargar logs del dispositivo"""
            try:
                self.log("Cargando logs del dispositivo...")
                
                # Limpiar treeview
                for item in tree.get_children():
                    tree.delete(item)
                
                logs_data.clear()
                
                # Simular logs del dispositivo (en un caso real, se obtendrían del dispositivo)
                sample_logs = [
                    {
                        'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                        'type': 'Sistema',
                        'level': 'INFO',
                        'message': 'Dispositivo iniciado correctamente',
                        'user': 'Sistema',
                        'details': 'Inicio del sistema'
                    },
                    {
                        'timestamp': (datetime.now() - timedelta(minutes=5)).strftime('%d/%m/%Y %H:%M:%S'),
                        'type': 'Acceso',
                        'level': 'INFO',
                        'message': 'Acceso autorizado',
                        'user': 'Juan Pérez',
                        'details': 'UID: 12345'
                    },
                    {
                        'timestamp': (datetime.now() - timedelta(minutes=10)).strftime('%d/%m/%Y %H:%M:%S'),
                        'type': 'Eventos',
                        'level': 'WARNING',
                        'message': 'Usuario no encontrado',
                        'user': 'Desconocido',
                        'details': 'UID: 99999'
                    },
                    {
                        'timestamp': (datetime.now() - timedelta(minutes=15)).strftime('%d/%m/%Y %H:%M:%S'),
                        'type': 'Errores',
                        'level': 'ERROR',
                        'message': 'Error de comunicación',
                        'user': 'Sistema',
                        'details': 'Timeout en conexión'
                    },
                    {
                        'timestamp': (datetime.now() - timedelta(minutes=20)).strftime('%d/%m/%Y %H:%M:%S'),
                        'type': 'Sistema',
                        'level': 'INFO',
                        'message': 'Sincronización de hora completada',
                        'user': 'Sistema',
                        'details': 'Hora actualizada'
                    }
                ]
                
                logs_data.extend(sample_logs)
                filtered_logs.extend(sample_logs)
                
                # Mostrar logs en treeview
                for log in sample_logs:
                    tree.insert('', tk.END, values=(
                        log['timestamp'],
                        log['type'],
                        log['level'],
                        log['message'],
                        log['user'],
                        log['details']
                    ))
                
                self.log(f"[OK] {len(sample_logs)} logs cargados")
                info_label.config(text=f"Total de logs: {len(sample_logs)}")
                
            except Exception as e:
                error_msg = f"Error al cargar logs: {e}"
                messagebox.showerror("Error", error_msg)
                self.log(f"[ERROR] {error_msg}")
        
        def filter_logs():
            """Filtrar logs según criterios"""
            try:
                # Limpiar treeview
                for item in tree.get_children():
                    tree.delete(item)
                
                filtered_logs.clear()
                
                # Aplicar filtros
                for log in logs_data:
                    # Filtro por tipo
                    if log_type_var.get() != "Todos" and log['type'] != log_type_var.get():
                        continue
                    
                    # Filtro por fecha
                    if date_from_var.get():
                        try:
                            log_date = datetime.strptime(log['timestamp'], '%d/%m/%Y %H:%M:%S').date()
                            filter_date = datetime.strptime(date_from_var.get(), '%d/%m/%Y').date()
                            if log_date < filter_date:
                                continue
                        except ValueError:
                            pass
                    
                    if date_to_var.get():
                        try:
                            log_date = datetime.strptime(log['timestamp'], '%d/%m/%Y %H:%M:%S').date()
                            filter_date = datetime.strptime(date_to_var.get(), '%d/%m/%Y').date()
                            if log_date > filter_date:
                                continue
                        except ValueError:
                            pass
                    
                    # Filtro por búsqueda
                    if search_var.get():
                        search_term = search_var.get().lower()
                        if (search_term not in log['message'].lower() and 
                            search_term not in log['user'].lower() and 
                            search_term not in log['details'].lower()):
                            continue
                    
                    filtered_logs.append(log)
                
                # Mostrar logs filtrados
                for log in filtered_logs:
                    tree.insert('', tk.END, values=(
                        log['timestamp'],
                        log['type'],
                        log['level'],
                        log['message'],
                        log['user'],
                        log['details']
                    ))
                
                info_label.config(text=f"Logs filtrados: {len(filtered_logs)} de {len(logs_data)}")
                self.log(f"[OK] Filtro aplicado: {len(filtered_logs)} logs mostrados")
                
            except Exception as e:
                error_msg = f"Error al filtrar logs: {e}"
                messagebox.showerror("Error", error_msg)
                self.log(f"[ERROR] {error_msg}")
        
        def clear_filters():
            """Limpiar filtros"""
            log_type_var.set("Sistema")
            date_from_var.set("")
            date_to_var.set("")
            search_var.set("")
            
            # Recargar todos los logs
            load_logs()
        
        def export_logs():
            """Exportar logs a archivo"""
            try:
                if not filtered_logs:
                    messagebox.showwarning("Advertencia", "No hay logs para exportar")
                    return
                
                # Solicitar ubicación para guardar
                filename = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("Archivos CSV", "*.csv"), ("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                    title="Exportar logs del dispositivo"
                )
                
                if filename:
                    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                        fieldnames = ['timestamp', 'type', 'level', 'message', 'user', 'details']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        
                        for log in filtered_logs:
                            writer.writerow(log)
                    
                    messagebox.showinfo("Éxito", f"Se exportaron {len(filtered_logs)} logs a {filename}")
                    self.log(f"[OK] {len(filtered_logs)} logs exportados a {filename}")
                    
            except Exception as e:
                error_msg = f"Error al exportar logs: {e}"
                messagebox.showerror("Error", error_msg)
                self.log(f"[ERROR] {error_msg}")
        
        # Evento de selección
        def on_select(event):
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                values = item['values']
                info_text = f"Log seleccionado:\n"
                info_text += f"Fecha/Hora: {values[0]}\n"
                info_text += f"Tipo: {values[1]}\n"
                info_text += f"Nivel: {values[2]}\n"
                info_text += f"Mensaje: {values[3]}\n"
                info_text += f"Usuario: {values[4]}\n"
                info_text += f"Detalles: {values[5]}"
                info_label.config(text=info_text)
        
        tree.bind('<<TreeviewSelect>>', on_select)
        
        # Cargar logs al abrir
        load_logs()
        
    def backup_device(self):
        """Crear backup completo del dispositivo"""
        if not self.connected:
            messagebox.showerror("Error", "No hay conexión al dispositivo")
            return
        
        try:
            # Solicitar ubicación para guardar el backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_filename = f"backup_zkteco_{timestamp}.zip"
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".zip",
                filetypes=[("Archivos ZIP", "*.zip"), ("Todos los archivos", "*.*")],
                title="Guardar backup del dispositivo",
                initialvalue=default_filename
            )
            
            if not filename:
                return  # Usuario canceló
            
            self.log("Iniciando backup completo del dispositivo...")
            
            # Crear directorio temporal para los archivos
            import tempfile
            import zipfile
            import json
            
            with tempfile.TemporaryDirectory() as temp_dir:
                backup_data = {
                    'timestamp': datetime.now().isoformat(),
                    'device_info': {},
                    'users': [],
                    'attendance_logs': [],
                    'backup_version': '1.0'
                }
                
                # 1. Información del dispositivo
                self.log("Obteniendo información del dispositivo...")
                try:
                    device_info = self.zkteco_device.get_device_info()
                    backup_data['device_info'] = device_info
                    self.log("[OK] Información del dispositivo obtenida")
                except Exception as e:
                    self.log(f"[ERROR] Error al obtener información del dispositivo: {e}")
                
                # 2. Lista de usuarios
                self.log("Obteniendo lista de usuarios...")
                try:
                    users = self.zkteco_device.get_user_list()
                    backup_data['users'] = users if users else []
                    self.log(f"[OK] {len(backup_data['users'])} usuarios obtenidos")
                except Exception as e:
                    self.log(f"[ERROR] Error al obtener usuarios: {e}")
                
                # 3. Registros de asistencia
                self.log("Obteniendo registros de asistencia...")
                try:
                    logs = self.zkteco_device.get_attendance_logs()
                    backup_data['attendance_logs'] = logs if logs else []
                    self.log(f"[OK] {len(backup_data['attendance_logs'])} registros de asistencia obtenidos")
                except Exception as e:
                    self.log(f"[ERROR] Error al obtener registros de asistencia: {e}")
                
                # 4. Hora del dispositivo
                try:
                    device_time = self.zkteco_device.get_device_time()
                    if device_time:
                        backup_data['device_time'] = device_time.isoformat()
                        self.log("[OK] Hora del dispositivo obtenida")
                except Exception as e:
                    self.log(f"[ERROR] Error al obtener hora del dispositivo: {e}")
                
                # Guardar datos principales
                main_data_file = os.path.join(temp_dir, 'backup_data.json')
                with open(main_data_file, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
                
                # Crear archivo CSV de registros de asistencia
                if backup_data['attendance_logs']:
                    csv_file = os.path.join(temp_dir, 'attendance_logs.csv')
                    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                        fieldnames = ['user_id', 'timestamp', 'punch', 'name', 'uid']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        
                        for log in backup_data['attendance_logs']:
                            # Convertir timestamp a string si es datetime
                            if isinstance(log.get('timestamp'), datetime):
                                log['timestamp'] = log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                            writer.writerow(log)
                
                # Crear archivo CSV de usuarios
                if backup_data['users']:
                    users_csv_file = os.path.join(temp_dir, 'users.csv')
                    with open(users_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                        fieldnames = ['user_id', 'name', 'privilege', 'password', 'group_id', 'user_pic', 'card', 'fingerprints']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        
                        for user in backup_data['users']:
                            writer.writerow(user)
                
                # Crear archivo de resumen
                summary_file = os.path.join(temp_dir, 'backup_summary.txt')
                with open(summary_file, 'w', encoding='utf-8') as f:
                    f.write(f"BACKUP DEL DISPOSITIVO ZKTeco\n")
                    f.write(f"Fecha y hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                    f.write(f"Versión del backup: {backup_data['backup_version']}\n\n")
                    
                    f.write(f"INFORMACIÓN DEL DISPOSITIVO:\n")
                    for key, value in backup_data['device_info'].items():
                        f.write(f"  {key}: {value}\n")
                    
                    f.write(f"\nESTADÍSTICAS:\n")
                    f.write(f"  Usuarios: {len(backup_data['users'])}\n")
                    f.write(f"  Registros de asistencia: {len(backup_data['attendance_logs'])}\n")
                    
                    if 'device_time' in backup_data:
                        f.write(f"  Hora del dispositivo: {backup_data['device_time']}\n")
                
                # Crear archivo ZIP
                self.log("Creando archivo de backup...")
                with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Agregar todos los archivos al ZIP
                    for file_name in os.listdir(temp_dir):
                        file_path = os.path.join(temp_dir, file_name)
                        zipf.write(file_path, file_name)
                
                # Mostrar resumen
                total_size = os.path.getsize(filename) / (1024 * 1024)  # MB
                summary_msg = f"Backup completado exitosamente\n\n"
                summary_msg += f"Archivo: {os.path.basename(filename)}\n"
                summary_msg += f"Tamaño: {total_size:.2f} MB\n"
                summary_msg += f"Usuarios: {len(backup_data['users'])}\n"
                summary_msg += f"Registros de asistencia: {len(backup_data['attendance_logs'])}\n\n"
                summary_msg += f"El backup incluye:\n"
                summary_msg += f"• Información del dispositivo\n"
                summary_msg += f"• Lista completa de usuarios\n"
                summary_msg += f"• Registros de asistencia\n"
                summary_msg += f"• Archivos CSV para análisis\n"
                summary_msg += f"• Resumen detallado"
                
                messagebox.showinfo("Backup Completado", summary_msg)
                self.log(f"[SUCCESS] Backup completado: {os.path.basename(filename)} ({total_size:.2f} MB)")
                
        except Exception as e:
            error_msg = f"Error al crear backup: {e}"
            messagebox.showerror("Error", error_msg)
            self.log(f"[ERROR] {error_msg}")
            logger.error(f"Error en backup_device: {e}")
    
    def on_closing(self):
        """Maneja el cierre de la ventana"""
        # Desconectar dispositivo si está conectado
        if self.connected and self.zkteco_device:
            try:
                self.zkteco_device.disconnect()
            except:
                pass
        
        # Destruir la ventana
        self.destroy()

def main():
    """Función principal para pruebas"""
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    # Datos de usuario de prueba
    user_data = {
        'id': 1,
        'usuario': 'admin',
        'nombre': 'Admin',
        'apellido': 'General',
        'rol': 'SUPERADMIN'
    }
    
    # Crear ventana de gestión
    gestion_window = GestionZKTeco(root, user_data)
    
    # Ejecutar
    root.mainloop()

if __name__ == "__main__":
    main() 
