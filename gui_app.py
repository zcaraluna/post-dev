#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interfaz gráfica para conectar con dispositivos ZKTeco K40
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from datetime import datetime
from zkteco_connector import ZKTecoK40, test_connection

class ZKTecoGUI:
    """Interfaz gráfica para dispositivos ZKTeco"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ZKTeco K40 - Gestor de Dispositivos")
        self.root.geometry("900x700")
        self.root.configure(bg='#f5f5f5')
        
        # Variables
        self.device = None
        self.is_connected = False
        
        # Configurar estilo
        self.setup_styles()
        
        # Crear interfaz
        self.create_widgets()
        
        # Centrar ventana
        self.center_window()
    
    def setup_styles(self):
        """Configurar estilos de la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 16, 'bold'), 
                       foreground='#2c3e50',
                       background='#f5f5f5')
        
        style.configure('Subtitle.TLabel', 
                       font=('Segoe UI', 10), 
                       foreground='#7f8c8d',
                       background='#f5f5f5')
        
        style.configure('Status.TLabel', 
                       font=('Segoe UI', 9, 'bold'),
                       background='#f5f5f5')
        
        style.configure('Connect.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       padding=10)
        
        style.configure('Action.TButton',
                       font=('Segoe UI', 9),
                       padding=8)
    
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, 
                               text="ZKTeco K40 - Gestor de Dispositivos", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Frame de conexión
        connection_frame = ttk.LabelFrame(main_frame, text="Configuración de Conexión", padding="15")
        connection_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Campos de conexión
        conn_grid = ttk.Frame(connection_frame)
        conn_grid.pack(fill=tk.X)
        
        ttk.Label(conn_grid, text="Dirección IP:").grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        self.ip_var = tk.StringVar(value="192.168.1.100")
        self.ip_entry = ttk.Entry(conn_grid, textvariable=self.ip_var, width=20)
        self.ip_entry.grid(row=0, column=1, sticky='w', padx=(0, 20), pady=5)
        
        ttk.Label(conn_grid, text="Puerto:").grid(row=0, column=2, sticky='w', padx=(0, 10), pady=5)
        self.port_var = tk.StringVar(value="4370")
        self.port_entry = ttk.Entry(conn_grid, textvariable=self.port_var, width=10)
        self.port_entry.grid(row=0, column=3, sticky='w', pady=5)
        
        # Botones de conexión
        button_frame = ttk.Frame(connection_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.connect_btn = ttk.Button(button_frame, 
                                     text="Conectar", 
                                     command=self.connect_device,
                                     style='Connect.TButton')
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.disconnect_btn = ttk.Button(button_frame, 
                                        text="Desconectar", 
                                        command=self.disconnect_device,
                                        style='Connect.TButton',
                                        state='disabled')
        self.disconnect_btn.pack(side=tk.LEFT)
        
        # Estado de conexión
        self.status_label = ttk.Label(connection_frame, 
                                     text="Estado: Desconectado", 
                                     style='Status.TLabel',
                                     foreground='#e74c3c')
        self.status_label.pack(anchor='w', pady=(10, 0))
        
        # Frame de información del dispositivo
        device_frame = ttk.LabelFrame(main_frame, text="Información del Dispositivo", padding="15")
        device_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.device_info_text = scrolledtext.ScrolledText(device_frame, 
                                                         height=6, 
                                                         font=('Consolas', 9),
                                                         state='disabled')
        self.device_info_text.pack(fill=tk.X)
        
        # Frame de usuarios
        users_frame = ttk.LabelFrame(main_frame, text="Gestión de Usuarios", padding="15")
        users_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Controles de usuarios
        users_controls = ttk.Frame(users_frame)
        users_controls.pack(fill=tk.X, pady=(0, 10))
        
        self.user_count_label = ttk.Label(users_controls, 
                                         text="Usuarios registrados: 0",
                                         style='Subtitle.TLabel')
        self.user_count_label.pack(side=tk.LEFT)
        
        ttk.Button(users_controls, 
                  text="Actualizar Lista", 
                  command=self.refresh_users,
                  style='Action.TButton').pack(side=tk.RIGHT)
        
        # Lista de usuarios
        users_list_frame = ttk.Frame(users_frame)
        users_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear Treeview para usuarios
        columns = ('ID', 'Nombre', 'Rol', 'Grupo', 'Huellas', 'Estado')
        self.users_tree = ttk.Treeview(users_list_frame, columns=columns, show='headings', height=10)
        
        # Configurar columnas
        self.users_tree.heading('ID', text='ID')
        self.users_tree.heading('Nombre', text='Nombre')
        self.users_tree.heading('Rol', text='Rol')
        self.users_tree.heading('Grupo', text='Grupo')
        self.users_tree.heading('Huellas', text='Huellas')
        self.users_tree.heading('Estado', text='Estado')
        
        self.users_tree.column('ID', width=60)
        self.users_tree.column('Nombre', width=200)
        self.users_tree.column('Rol', width=80)
        self.users_tree.column('Grupo', width=80)
        self.users_tree.column('Huellas', width=80)
        self.users_tree.column('Estado', width=80)
        
        # Scrollbar para la lista
        users_scrollbar = ttk.Scrollbar(users_list_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=users_scrollbar.set)
        
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        users_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de registros de asistencia
        logs_frame = ttk.LabelFrame(main_frame, text="Registros de Asistencia", padding="15")
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        # Controles de registros
        logs_controls = ttk.Frame(logs_frame)
        logs_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(logs_controls, text="Desde:").pack(side=tk.LEFT)
        self.start_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(logs_controls, textvariable=self.start_date_var, width=12).pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(logs_controls, text="Hasta:").pack(side=tk.LEFT)
        self.end_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(logs_controls, textvariable=self.end_date_var, width=12).pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Button(logs_controls, 
                  text="Obtener Registros", 
                  command=self.get_attendance_logs,
                  style='Action.TButton').pack(side=tk.RIGHT)
        
        # Lista de registros
        logs_list_frame = ttk.Frame(logs_frame)
        logs_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear Treeview para registros
        log_columns = ('Usuario', 'Fecha/Hora', 'Tipo', 'Estado')
        self.logs_tree = ttk.Treeview(logs_list_frame, columns=log_columns, show='headings', height=8)
        
        # Configurar columnas
        self.logs_tree.heading('Usuario', text='Usuario')
        self.logs_tree.heading('Fecha/Hora', text='Fecha/Hora')
        self.logs_tree.heading('Tipo', text='Tipo')
        self.logs_tree.heading('Estado', text='Estado')
        
        self.logs_tree.column('Usuario', width=150)
        self.logs_tree.column('Fecha/Hora', width=150)
        self.logs_tree.column('Tipo', width=100)
        self.logs_tree.column('Estado', width=100)
        
        # Scrollbar para registros
        logs_scrollbar = ttk.Scrollbar(logs_list_frame, orient=tk.VERTICAL, command=self.logs_tree.yview)
        self.logs_tree.configure(yscrollcommand=logs_scrollbar.set)
        
        self.logs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        logs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def connect_device(self):
        """Conectar al dispositivo"""
        def connect_thread():
            try:
                ip = self.ip_var.get().strip()
                port = int(self.port_var.get().strip())
                
                if not ip:
                    messagebox.showerror("Error", "Por favor ingresa una dirección IP válida")
                    return
                
                # Probar conexión
                self.update_status("Probando conexión...", "#f39c12")
                
                if test_connection(ip, port):
                    # Crear dispositivo
                    self.device = ZKTecoK40(ip, port)
                    
                    if self.device.connect():
                        self.is_connected = True
                        self.update_status("Conectado", "#27ae60")
                        self.update_connection_buttons()
                        
                        # Obtener información del dispositivo
                        self.get_device_info()
                        
                        # Obtener cantidad de usuarios
                        self.get_user_count()
                        
                        messagebox.showinfo("Éxito", "Conexión establecida correctamente")
                    else:
                        self.update_status("Error de conexión", "#e74c3c")
                        messagebox.showerror("Error", "No se pudo establecer la conexión")
                else:
                    self.update_status("No se puede conectar", "#e74c3c")
                    messagebox.showerror("Error", 
                                       "No se puede conectar al dispositivo.\n"
                                       "Verifica la dirección IP y que el dispositivo esté encendido.")
                    
            except ValueError:
                messagebox.showerror("Error", "El puerto debe ser un número válido")
                self.update_status("Error de configuración", "#e74c3c")
            except Exception as e:
                messagebox.showerror("Error", f"Error inesperado: {str(e)}")
                self.update_status("Error", "#e74c3c")
        
        # Ejecutar en hilo separado para no bloquear la interfaz
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def disconnect_device(self):
        """Desconectar del dispositivo"""
        if self.device:
            self.device.disconnect()
            self.device = None
        
        self.is_connected = False
        self.update_status("Desconectado", "#e74c3c")
        self.update_connection_buttons()
        
        # Limpiar datos
        self.clear_device_info()
        self.clear_users_list()
        self.clear_logs_list()
    
    def update_status(self, status, color):
        """Actualizar estado de conexión"""
        self.status_label.config(text=f"Estado: {status}", foreground=color)
    
    def update_connection_buttons(self):
        """Actualizar estado de botones de conexión"""
        if self.is_connected:
            self.connect_btn.config(state='disabled')
            self.disconnect_btn.config(state='normal')
        else:
            self.connect_btn.config(state='normal')
            self.disconnect_btn.config(state='disabled')
    
    def get_device_info(self):
        """Obtener información del dispositivo"""
        if not self.device:
            return
        
        try:
            info = self.device.get_device_info()
            self.display_device_info(info)
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener información del dispositivo: {str(e)}")
    
    def display_device_info(self, info):
        """Mostrar información del dispositivo"""
        self.device_info_text.config(state='normal')
        self.device_info_text.delete(1.0, tk.END)
        
        if info:
            for key, value in info.items():
                self.device_info_text.insert(tk.END, f"{key.replace('_', ' ').title()}: {value}\n")
        else:
            self.device_info_text.insert(tk.END, "No se pudo obtener información del dispositivo")
        
        self.device_info_text.config(state='disabled')
    
    def clear_device_info(self):
        """Limpiar información del dispositivo"""
        self.device_info_text.config(state='normal')
        self.device_info_text.delete(1.0, tk.END)
        self.device_info_text.config(state='disabled')
    
    def get_user_count(self):
        """Obtener cantidad de usuarios"""
        if not self.device:
            return
        
        try:
            count = self.device.get_user_count()
            self.user_count_label.config(text=f"Usuarios registrados: {count}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener cantidad de usuarios: {str(e)}")
    
    def refresh_users(self):
        """Actualizar lista de usuarios"""
        if not self.device:
            messagebox.showwarning("Advertencia", "No hay dispositivo conectado")
            return
        
        def refresh_thread():
            try:
                users = self.device.get_user_list(0, 1000)  # Obtener hasta 1000 usuarios
                self.display_users(users)
            except Exception as e:
                messagebox.showerror("Error", f"Error al obtener usuarios: {str(e)}")
        
        threading.Thread(target=refresh_thread, daemon=True).start()
    
    def display_users(self, users):
        """Mostrar lista de usuarios"""
        # Limpiar lista actual
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        # Agregar usuarios
        for user in users:
            status = "Activo" if user['status'] == 1 else "Inactivo"
            self.users_tree.insert('', tk.END, values=(
                user['user_id'],
                user['name'],
                user['role'],
                user['group'],
                user['fingerprint_count'],
                status
            ))
    
    def clear_users_list(self):
        """Limpiar lista de usuarios"""
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        self.user_count_label.config(text="Usuarios registrados: 0")
    
    def get_attendance_logs(self):
        """Obtener registros de asistencia"""
        if not self.device:
            messagebox.showwarning("Advertencia", "No hay dispositivo conectado")
            return
        
        def logs_thread():
            try:
                start_date = self.start_date_var.get()
                end_date = self.end_date_var.get()
                
                logs = self.device.get_attendance_logs(start_date, end_date)
                self.display_logs(logs)
            except Exception as e:
                messagebox.showerror("Error", f"Error al obtener registros: {str(e)}")
        
        threading.Thread(target=logs_thread, daemon=True).start()
    
    def display_logs(self, logs):
        """Mostrar registros de asistencia"""
        # Limpiar lista actual
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)
        
        # Agregar registros
        for log in logs:
            # Convertir timestamp a fecha legible
            timestamp = datetime.fromtimestamp(log['timestamp'])
            date_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            
            # Determinar tipo de verificación
            verification_types = {
                0: "Contraseña",
                1: "Huella",
                2: "Tarjeta",
                3: "Rostro"
            }
            verification_type = verification_types.get(log['verification_type'], "Desconocido")
            
            # Determinar estado
            status = "Entrada" if log['status'] == 1 else "Salida"
            
            self.logs_tree.insert('', tk.END, values=(
                log['user_id'],
                date_str,
                verification_type,
                status
            ))
    
    def clear_logs_list(self):
        """Limpiar lista de registros"""
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)

def main():
    """Función principal"""
    root = tk.Tk()
    app = ZKTecoGUI(root)
    
    # Manejar cierre de ventana
    def on_closing():
        if app.device:
            app.disconnect_device()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 