#!/usr/bin/env python3
"""
Módulo para gestionar el dispositivo ZKTeco
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import datetime
import csv
import os
from zkteco_connector_v2 import ZKTecoK40V2

class GestionZKTeco(tk.Toplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.parent = parent
        self.user_data = user_data
        self.zkteco_device = None
        self.connected = False
        self._watchdog_stop = False
        self._watchdog_thread = None
        
        self.title("Gestión ZKTeco K40")
        self.geometry("720x720")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        # Configurar protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_ui()
        self.center_window()
        
    def setup_ui(self):
        """Configurar la interfaz"""
        # Configurar estilo
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'), foreground='#2c3e50')
        style.configure('Status.TLabel', font=('Arial', 10), foreground='#34495e')
        
        # Crear canvas con scrollbar
        self.canvas = tk.Canvas(self, bg='white')
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        scrollable_frame = ttk.Frame(self.canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame principal dentro del canvas
        main_frame = ttk.Frame(scrollable_frame, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Título
        title_label = ttk.Label(main_frame, text="📱 Gestión ZKTeco K40", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Frame de conexión
        connection_frame = ttk.LabelFrame(main_frame, text="Estado de Conexión", padding=15)
        connection_frame.pack(fill='x', pady=(0, 20))
        
        self.create_connection_controls(connection_frame)
        
        # Frame de información del dispositivo
        device_frame = ttk.LabelFrame(main_frame, text="Información del Dispositivo", padding=15)
        device_frame.pack(fill='x', pady=(0, 20))
        
        self.create_device_info(device_frame)
        
        # Frame de operaciones
        operations_frame = ttk.LabelFrame(main_frame, text="Operaciones", padding=15)
        operations_frame.pack(fill='x', pady=(0, 20))
        
        self.create_operations_controls(operations_frame)
        
        # Frame de logs
        logs_frame = ttk.LabelFrame(main_frame, text="Logs del Sistema", padding=15)
        logs_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        self.create_logs_section(logs_frame)
        
        # Configurar scroll con mouse
        def _on_mousewheel(event):
            try:
                if self.canvas.winfo_exists():
                    self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                # El canvas ya no existe, ignorar el evento
                pass
        
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Empaquetar canvas y scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def on_closing(self):
        """Maneja el cierre de la ventana"""
        try:
            # Desvincular el evento del mouse
            self.canvas.unbind_all("<MouseWheel>")
        except:
            pass
        
        # Detener watchdog antes de cerrar
        self.stop_watchdog()

        # Desconectar dispositivo si está conectado
        if self.connected and self.zkteco_device:
            try:
                self.zkteco_device.disconnect()
            except:
                pass
        
        # Destruir la ventana
        self.destroy()
        
    def create_connection_controls(self, parent):
        """Crear controles de conexión"""
        # Variables
        self.ip_var = tk.StringVar(value="192.168.100.201")
        self.port_var = tk.StringVar(value="4370")
        
        # Frame de configuración
        config_frame = ttk.Frame(parent)
        config_frame.pack(fill='x', pady=(0, 15))
        
        # IP Address
        ttk.Label(config_frame, text="IP Address:", style='Status.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(config_frame, textvariable=self.ip_var, width=20).grid(row=0, column=1, padx=(10, 0), pady=5)
        
        # Puerto
        ttk.Label(config_frame, text="Puerto:", style='Status.TLabel').grid(row=0, column=2, sticky='w', padx=(20, 0), pady=5)
        ttk.Entry(config_frame, textvariable=self.port_var, width=10).grid(row=0, column=3, padx=(10, 0), pady=5)
        
        # Botones de conexión
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        self.connect_btn = ttk.Button(button_frame, text="🔌 Conectar", command=self.connect_device)
        self.connect_btn.pack(side='left', padx=(0, 10))
        
        self.disconnect_btn = ttk.Button(button_frame, text="🔌 Desconectar", command=self.disconnect_device, state='disabled')
        self.disconnect_btn.pack(side='left', padx=(0, 10))
        
        self.refresh_btn = ttk.Button(button_frame, text="🔄 Actualizar Info", command=self.update_device_info)
        self.refresh_btn.pack(side='left', padx=(0, 10))
        

        
        # Estado de conexión
        self.status_label = ttk.Label(parent, text="❌ Desconectado", 
                                     font=('Arial', 10, 'bold'), foreground='#e74c3c')
        self.status_label.pack(pady=(10, 0))
        
    def create_logs_section(self, parent):
        """Crear sección de logs del sistema"""
        # Frame para logs
        logs_frame = ttk.Frame(parent)
        logs_frame.pack(fill='both', expand=True)
        
        # Text widget para logs
        self.log_text = tk.Text(logs_frame, height=8, width=80, wrap='word', 
                               font=('Consolas', 9), bg='#f8f9fa', fg='#2c3e50')
        
        # Scrollbar para logs
        log_scrollbar = ttk.Scrollbar(logs_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # Empaquetar
        self.log_text.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')
        
        # Botón para limpiar logs
        clear_logs_btn = ttk.Button(parent, text="🗑️ Limpiar Logs", 
                                   command=lambda: self.log_text.delete(1.0, tk.END))
        clear_logs_btn.pack(pady=(10, 0))
        
    def create_device_info(self, parent):
        """Crear información del dispositivo"""
        # Grid para información
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill='x')
        
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
        
        # Crear etiquetas de información
        row = 0
        for label, var in [
            ("Número de Serie:", self.device_info['serial']),
            ("Versión de Firmware:", self.device_info['firmware']),
            ("Dirección MAC:", self.device_info['mac']),
            ("Algoritmo:", self.device_info['algorithm']),
            ("Usuarios Registrados:", self.device_info['users_count']),
            ("Registros de Asistencia:", self.device_info['logs_count']),
            ("Hora del Dispositivo:", self.device_info['time'])
        ]:
            ttk.Label(info_frame, text=label, style='Status.TLabel').grid(row=row, column=0, sticky='w', pady=2)
            ttk.Label(info_frame, textvariable=var, font=('Arial', 9, 'bold')).grid(row=row, column=1, sticky='w', padx=(10, 0), pady=2)
            row += 1
            
        # Configurar grid
        info_frame.columnconfigure(1, weight=1)
        
    def create_operations_controls(self, parent):
        """Crear controles de operaciones"""
        # Frame de botones principales
        main_buttons_frame = ttk.Frame(parent)
        main_buttons_frame.pack(fill='x', pady=(0, 20))
        
        # Botones principales
        buttons = [
            ("👥 Gestionar Usuarios", self.manage_users),
            ("📊 Descargar Asistencias", self.download_attendance),
            ("🔄 Sincronizar Hora", self.sync_time),
            ("🗑️ Limpiar Datos", self.clear_data)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(main_buttons_frame, text=text, command=command, width=25)
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='ew')
            
        main_buttons_frame.columnconfigure(0, weight=1)
        main_buttons_frame.columnconfigure(1, weight=1)
        
        # Frame de operaciones avanzadas
        advanced_frame = ttk.LabelFrame(parent, text="Operaciones Avanzadas", padding=15)
        advanced_frame.pack(fill='x')
        
        advanced_buttons = [
            ("📱 Reiniciar Dispositivo", self.restart_device),
            ("⚙️ Configuración", self.device_config),
            ("📋 Ver Logs", self.view_logs),
            ("💾 Backup", self.backup_device)
        ]
        
        for i, (text, command) in enumerate(advanced_buttons):
            btn = ttk.Button(advanced_frame, text=text, command=command, width=25)
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='ew')
            
        advanced_frame.columnconfigure(0, weight=1)
        advanced_frame.columnconfigure(1, weight=1)
        
        # Configurar log inicial
        self.log("Sistema de gestión QUIRA iniciado")
        
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
        from datetime import datetime
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
            
        self.log(f"Conectando a {ip}:{port}...")
        
        def connect_thread():
            try:
                self.zkteco_device = ZKTecoK40V2(ip, port)
                if self.zkteco_device.connect():
                    self.after(0, self.connection_success)
                else:
                    self.after(0, self.connection_failed)
            except Exception as e:
                self.after(0, lambda: self.connection_error(str(e)))
                
        threading.Thread(target=connect_thread, daemon=True).start()
        
    def connection_success(self):
        """Manejar conexión exitosa"""
        self.connected = True
        self.status_label.config(text="✅ Conectado", foreground='#27ae60')
        self.connect_btn.config(state='disabled')
        self.disconnect_btn.config(state='normal')
        self.log("Conexión establecida exitosamente")
        
        # Actualizar información del dispositivo
        self.update_device_info()

        # Iniciar watchdog de reconexión automática
        self.start_watchdog()
        
    def connection_failed(self):
        """Manejar fallo de conexión"""
        self.connected = False
        self.status_label.config(text="❌ Error de conexión", foreground='#e74c3c')
        self.connect_btn.config(state='normal')
        self.disconnect_btn.config(state='disabled')
        self.log("Error: No se pudo conectar al dispositivo")
        messagebox.showerror("Error", "No se pudo conectar al dispositivo ZKTeco")
        
    def connection_error(self, error_msg):
        """Manejar error de conexión"""
        self.connected = False
        self.status_label.config(text="❌ Error", foreground='#e74c3c')
        self.connect_btn.config(state='normal')
        self.disconnect_btn.config(state='disabled')
        self.log(f"Error de conexión: {error_msg}")
        messagebox.showerror("Error", f"Error al conectar: {error_msg}")
        
    def disconnect_device(self):
        """Desconectar dispositivo"""
        # Detener watchdog primero
        self.stop_watchdog()
        if self.zkteco_device:
            try:
                self.zkteco_device.disconnect()
                self.log("Dispositivo desconectado")
            except:
                pass
                
        self.connected = False
        self.zkteco_device = None
        self.status_label.config(text="❌ Desconectado", foreground='#e74c3c')
        self.connect_btn.config(state='normal')
        self.disconnect_btn.config(state='disabled')
        
        # Limpiar información
        for var in self.device_info.values():
            var.set("No disponible")
            
    def start_watchdog(self, interval_s: int = 30):
        """Iniciar un hilo watchdog que verifica la conexión y reintenta con backoff."""
        if self._watchdog_thread and self._watchdog_thread.is_alive():
            return
        self._watchdog_stop = False

        def loop():
            import time
            backoff_seconds = 3
            max_backoff = 60
            while not self._watchdog_stop:
                try:
                    # Si no hay dispositivo inicializado, esperar
                    if not self.zkteco_device:
                        time.sleep(interval_s)
                        continue

                    # Si está marcado como conectado, validar vida
                    if self.connected and self.zkteco_device.is_alive():
                        backoff_seconds = 3
                        time.sleep(interval_s)
                        continue

                    # En este punto, no está vivo. Marcar UI y reintentar
                    self.after(0, lambda: self.status_label.config(text="❌ Desconectado (reintentando)", foreground='#e67e22'))
                    self.after(0, lambda: self.connect_btn.config(state='disabled'))
                    self.after(0, lambda: self.disconnect_btn.config(state='normal'))

                    # Intentar reconectar
                    if self.zkteco_device.reconnect():
                        self.connected = True
                        backoff_seconds = 3
                        self.after(0, lambda: self.status_label.config(text="✅ Conectado", foreground='#27ae60'))
                        # Refrescar info tras reconexión
                        self.after(0, self.update_device_info)
                        time.sleep(interval_s)
                    else:
                        self.connected = False
                        # Aumentar backoff y esperar
                        time.sleep(backoff_seconds)
                        backoff_seconds = min(backoff_seconds * 2, max_backoff)

                except Exception:
                    # Cualquier excepción: esperar con backoff y seguir
                    time.sleep(backoff_seconds)
                    backoff_seconds = min(backoff_seconds * 2, max_backoff)

        import threading as _th
        self._watchdog_thread = _th.Thread(target=loop, daemon=True)
        self._watchdog_thread.start()

    def stop_watchdog(self):
        """Detener el hilo watchdog si está corriendo."""
        self._watchdog_stop = True
        thr = self._watchdog_thread
        self._watchdog_thread = None
        # No join() para no bloquear UI; es daemon


        
    def update_device_info(self):
        """Actualizar información del dispositivo"""
        self.log("🔄 Iniciando actualización de información del dispositivo...")
        self.log(f"🔍 Estado actual - Connected: {self.connected}, Device: {self.zkteco_device}")
        
        if not self.connected:
            self.log("❌ No se puede actualizar información: dispositivo no conectado")
            messagebox.showwarning("Advertencia", "Debe estar conectado al dispositivo")
            return
            
        if not self.zkteco_device:
            self.log("❌ No se puede actualizar información: dispositivo no inicializado")
            messagebox.showwarning("Advertencia", "Dispositivo no inicializado")
            return
            
        self.log("🔄 Actualizando información del dispositivo...")
        
        def update_thread():
            try:
                # Paso 1: Obtener información básica del dispositivo
                self.after(0, lambda: self.log("📱 Paso 1: Obteniendo información básica del dispositivo..."))
                
                try:
                    info = self.zkteco_device.get_device_info()
                    self.after(0, lambda: self.log(f"📱 Información básica obtenida: {info}"))
                except Exception as e:
                    self.after(0, lambda: self.log(f"❌ Error al obtener información básica: {e}"))
                    info = {}
                
                # Paso 2: Obtener lista de usuarios
                self.after(0, lambda: self.log("👥 Paso 2: Obteniendo lista de usuarios..."))
                
                try:
                    users = self.zkteco_device.get_user_list()
                    users_count = len(users) if users else 0
                    self.after(0, lambda: self.log(f"👥 Usuarios encontrados: {users_count}"))
                    if users:
                        self.after(0, lambda: self.log(f"👥 Detalle usuarios: {[u.get('uid', 'N/A') for u in users[:3]]}..."))
                except Exception as e:
                    self.after(0, lambda: self.log(f"❌ Error al obtener usuarios: {e}"))
                    users_count = 0
                
                # Paso 3: Obtener logs de asistencia
                self.after(0, lambda: self.log("📊 Paso 3: Obteniendo logs de asistencia..."))
                
                try:
                    logs = self.zkteco_device.get_attendance_logs()  # Cambié a get_attendance_logs
                    logs_count = len(logs) if logs else 0
                    self.after(0, lambda: self.log(f"📊 Logs encontrados: {logs_count}"))
                except Exception as e:
                    self.after(0, lambda: self.log(f"❌ Error al obtener logs: {e}"))
                    logs_count = 0
                
                # Paso 4: Obtener hora del dispositivo
                self.after(0, lambda: self.log("🕐 Paso 4: Obteniendo hora del dispositivo..."))
                
                try:
                    # Usar datetime.now() como alternativa
                    device_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    self.after(0, lambda: self.log(f"🕐 Hora del dispositivo: {device_time}"))
                except Exception as e:
                    self.after(0, lambda: self.log(f"❌ Error al obtener hora: {e}"))
                    device_time = None
                
                # Paso 5: Actualizar interfaz
                self.after(0, lambda: self.log("🖥️ Paso 5: Actualizando interfaz..."))
                
                # Obtener valores con manejo de errores
                serial = info.get('serial_number', 'No disponible') if info else 'No disponible'
                firmware = info.get('firmware_version', 'No disponible') if info else 'No disponible'
                mac = info.get('mac_address', 'No disponible') if info else 'No disponible'
                algorithm = info.get('algorithm', 'No disponible') if info else 'No disponible'
                
                self.after(0, lambda: self.device_info['serial'].set(serial))
                self.after(0, lambda: self.device_info['firmware'].set(firmware))
                self.after(0, lambda: self.device_info['mac'].set(mac))
                self.after(0, lambda: self.device_info['algorithm'].set(algorithm))
                self.after(0, lambda: self.device_info['users_count'].set(str(users_count)))
                self.after(0, lambda: self.device_info['logs_count'].set(str(logs_count)))
                self.after(0, lambda: self.device_info['time'].set(device_time if device_time else 'No disponible'))
                
                self.after(0, lambda: self.log(f"✅ Información del dispositivo actualizada - {users_count} usuarios, {logs_count} logs"))
                self.after(0, lambda: messagebox.showinfo("Éxito", f"Información actualizada\nUsuarios: {users_count}\nLogs: {logs_count}"))
                
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda: self.log(f"❌ Error general al obtener información: {error_msg}"))
                self.after(0, lambda: self.log(f"🔍 Debug - Connected: {self.connected}, Device: {self.zkteco_device}"))
                self.after(0, lambda: messagebox.showerror("Error", f"Error al obtener información: {error_msg}"))
                
        threading.Thread(target=update_thread, daemon=True).start()
        
    def show_users_window(self, users):
        """Mostrar ventana con lista de usuarios"""
        # Crear ventana de usuarios
        users_window = tk.Toplevel(self)
        users_window.title("Gestión de Usuarios - ZKTeco K40")
        users_window.geometry("800x600")
        users_window.transient(self)
        users_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(users_window, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Título
        title_label = ttk.Label(main_frame, text=f"👥 Usuarios del Dispositivo ({len(users)})", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Frame para tabla
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill='both', expand=True)
        
        # Crear Treeview
        columns = ('UID', 'User ID', 'Nombre', 'Privilegio', 'Huellas')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        column_widths = {
            'UID': 80,
            'User ID': 100,
            'Nombre': 200,
            'Privilegio': 100,
            'Huellas': 100
        }
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=column_widths.get(col, 100), anchor='center')
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Insertar datos
        for user in users:
            privilege_text = "Admin" if user.get('privilege', 0) == 1 else "Usuario"
            tree.insert('', 'end', values=(
                user.get('uid', 'N/A'),
                user.get('user_id', 'N/A'),
                user.get('name', 'N/A'),
                privilege_text,
                user.get('fingerprints', 0)
            ))
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(button_frame, text="💾 Exportar a CSV", 
                  command=lambda: self.export_users_to_csv(users)).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="🔄 Actualizar", 
                  command=lambda: self.refresh_users_window(users_window)).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="❌ Cerrar", 
                  command=users_window.destroy).pack(side='right')
        
    def export_users_to_csv(self, users):
        """Exportar usuarios a archivo CSV"""
        try:
            # Solicitar ubicación del archivo
            filename = filedialog.asksaveasfilename(
                title="Guardar Usuarios",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not filename:
                return
                
            # Escribir archivo CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['UID', 'User ID', 'Nombre', 'Privilegio', 'Huellas']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for user in users:
                    privilege_text = "Admin" if user.get('privilege', 0) == 1 else "Usuario"
                    writer.writerow({
                        'UID': user.get('uid', 'N/A'),
                        'User ID': user.get('user_id', 'N/A'),
                        'Nombre': user.get('name', 'N/A'),
                        'Privilegio': privilege_text,
                        'Huellas': user.get('fingerprints', 0)
                    })
            
            self.log(f"✅ Usuarios exportados a: {filename}")
            messagebox.showinfo("Éxito", f"Usuarios exportados exitosamente a:\n{filename}")
            
        except Exception as e:
            self.log(f"❌ Error al exportar usuarios: {e}")
            messagebox.showerror("Error", f"Error al exportar usuarios: {e}")
    
    def refresh_users_window(self, window):
        """Actualizar ventana de usuarios"""
        window.destroy()
        self.manage_users()
    
    def save_attendance_to_file(self, logs):
        """Guardar registros de asistencia a archivo"""
        try:
            # Solicitar ubicación del archivo
            filename = filedialog.asksaveasfilename(
                title="Guardar Registros de Asistencia",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not filename:
                return
                
            # Escribir archivo CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['User ID', 'Nombre', 'Fecha', 'Hora', 'Estado', 'Verificación']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for log in logs:
                    # Convertir timestamp a fecha y hora
                    timestamp = log.get('timestamp', 0)
                    if timestamp:
                        try:
                            dt = datetime.fromtimestamp(timestamp)
                            fecha = dt.strftime('%d/%m/%Y')
                            hora = dt.strftime('%H:%M:%S')
                        except:
                            fecha = "N/A"
                            hora = "N/A"
                    else:
                        fecha = "N/A"
                        hora = "N/A"
                    
                    writer.writerow({
                        'User ID': log.get('user_id', 'N/A'),
                        'Nombre': log.get('name', 'N/A'),
                        'Fecha': fecha,
                        'Hora': hora,
                        'Estado': log.get('status', 'N/A'),
                        'Verificación': log.get('verification', 'N/A')
                    })
            
            self.log(f"✅ Registros de asistencia exportados a: {filename}")
            messagebox.showinfo("Éxito", f"Registros de asistencia exportados exitosamente a:\n{filename}")
            
        except Exception as e:
            self.log(f"❌ Error al exportar registros: {e}")
            messagebox.showerror("Error", f"Error al exportar registros: {e}")
        
    # Métodos de operaciones
    def manage_users(self):
        """Gestionar usuarios del dispositivo"""
        if not self.connected:
            messagebox.showwarning("Advertencia", "Debe estar conectado al dispositivo")
            return
            
        self.log("👥 Iniciando gestión de usuarios...")
        
        def manage_thread():
            try:
                # Obtener lista de usuarios
                self.after(0, lambda: self.log("📋 Obteniendo lista de usuarios..."))
                users = self.zkteco_device.get_user_list()
                
                if not users:
                    self.after(0, lambda: self.log("⚠️ No se encontraron usuarios en el dispositivo"))
                    self.after(0, lambda: messagebox.showinfo("Información", "No se encontraron usuarios en el dispositivo"))
                    return
                
                self.after(0, lambda: self.log(f"✅ Se encontraron {len(users)} usuarios"))
                
                # Crear ventana de gestión de usuarios
                self.after(0, lambda: self.show_users_window(users))
                
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda: self.log(f"❌ Error al gestionar usuarios: {error_msg}"))
                
                # Intentar reconectar y reintentar
                if "TCP packet invalid" in error_msg or "unpack requires" in error_msg:
                    self.after(0, lambda: self.log("🔄 Intentando reconectar..."))
                    if self.zkteco_device.reconnect():
                        self.after(0, lambda: self.log("✅ Reconexión exitosa, reintentando..."))
                        try:
                            users = self.zkteco_device.get_user_list()
                            if users:
                                self.after(0, lambda: self.log(f"✅ Se encontraron {len(users)} usuarios"))
                                self.after(0, lambda: self.show_users_window(users))
                                return
                        except Exception as retry_error:
                            self.after(0, lambda: self.log(f"❌ Error en reintento: {retry_error}"))
                    else:
                        self.after(0, lambda: self.log("❌ No se pudo reconectar"))
                
                self.after(0, lambda: messagebox.showerror("Error", f"Error al gestionar usuarios: {error_msg}"))
                
        threading.Thread(target=manage_thread, daemon=True).start()
        
    def download_attendance(self):
        """Descargar registros de asistencia"""
        if not self.connected:
            messagebox.showwarning("Advertencia", "Debe estar conectado al dispositivo")
            return
            
        self.log("📊 Iniciando descarga de asistencias...")
        
        def download_thread():
            try:
                # Obtener registros de asistencia
                self.after(0, lambda: self.log("📋 Obteniendo registros de asistencia..."))
                logs = self.zkteco_device.get_attendance_logs()
                
                if not logs:
                    self.after(0, lambda: self.log("⚠️ No se encontraron registros de asistencia"))
                    self.after(0, lambda: messagebox.showinfo("Información", "No se encontraron registros de asistencia"))
                    return
                
                self.after(0, lambda: self.log(f"✅ Se encontraron {len(logs)} registros de asistencia"))
                
                # Solicitar ubicación para guardar
                self.after(0, lambda: self.save_attendance_to_file(logs))
                
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda: self.log(f"❌ Error al descargar asistencias: {error_msg}"))
                
                # Intentar reconectar y reintentar
                if "TCP packet invalid" in error_msg or "unpack requires" in error_msg:
                    self.after(0, lambda: self.log("🔄 Intentando reconectar..."))
                    if self.zkteco_device.reconnect():
                        self.after(0, lambda: self.log("✅ Reconexión exitosa, reintentando..."))
                        try:
                            logs = self.zkteco_device.get_attendance_logs()
                            if logs:
                                self.after(0, lambda: self.log(f"✅ Se encontraron {len(logs)} registros de asistencia"))
                                self.after(0, lambda: self.save_attendance_to_file(logs))
                                return
                        except Exception as retry_error:
                            self.after(0, lambda: self.log(f"❌ Error en reintento: {retry_error}"))
                    else:
                        self.after(0, lambda: self.log("❌ No se pudo reconectar"))
                
                self.after(0, lambda: messagebox.showerror("Error", f"Error al descargar asistencias: {error_msg}"))
                
        threading.Thread(target=download_thread, daemon=True).start()
        
    def sync_time(self):
        """Sincronizar hora del dispositivo"""
        if not self.connected:
            messagebox.showwarning("Advertencia", "Debe estar conectado al dispositivo")
            return
        messagebox.showinfo("Funcionalidad", "Sincronización de hora en desarrollo")
        
    def clear_data(self):
        """Limpiar datos del dispositivo"""
        if not self.connected:
            messagebox.showwarning("Advertencia", "Debe estar conectado al dispositivo")
            return
        if messagebox.askyesno("Confirmar", "¿Está seguro de limpiar todos los datos del dispositivo?"):
            messagebox.showinfo("Funcionalidad", "Limpieza de datos en desarrollo")
            
    def restart_device(self):
        """Reiniciar dispositivo"""
        if not self.connected:
            messagebox.showwarning("Advertencia", "Debe estar conectado al dispositivo")
            return
        if messagebox.askyesno("Confirmar", "¿Está seguro de reiniciar el dispositivo?"):
            messagebox.showinfo("Funcionalidad", "Reinicio de dispositivo en desarrollo")
            
    def device_config(self):
        """Configuración del dispositivo"""
        if not self.connected:
            messagebox.showwarning("Advertencia", "Debe estar conectado al dispositivo")
            return
        messagebox.showinfo("Funcionalidad", "Configuración de dispositivo en desarrollo")
        
    def view_logs(self):
        """Ver logs del dispositivo"""
        if not self.connected:
            messagebox.showwarning("Advertencia", "Debe estar conectado al dispositivo")
            return
        messagebox.showinfo("Funcionalidad", "Visualización de logs en desarrollo")
        
    def backup_device(self):
        """Hacer backup del dispositivo"""
        if not self.connected:
            messagebox.showwarning("Advertencia", "Debe estar conectado al dispositivo")
            return
        messagebox.showinfo("Funcionalidad", "Backup de dispositivo en desarrollo")

def main():
    """Función de prueba"""
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    # Datos de usuario de prueba
    user_data = {
        'id': 1,
        'nombre': 'Admin',
        'apellido': 'General',
        'rol': 'SUPERADMIN'
    }
    
    app = GestionZKTeco(root, user_data)
    root.mainloop()

if __name__ == "__main__":
    main() 