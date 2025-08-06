#!/usr/bin/env python3
"""
Interfaz gráfica para dispositivos ZKTeco K40 usando pyzk
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from datetime import datetime
from zkteco_connector_v2 import ZKTecoK40V2, test_connection

class ZKTecoGUIV2:
    def __init__(self, root):
        self.root = root
        self.root.title("ZKTeco K40 - Gestor de Dispositivos Biométricos")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.device = None
        self.connected = False
        
        # Configurar estilo
        self.setup_styles()
        
        # Crear widgets
        self.create_widgets()
        
        # Centrar ventana
        self.center_window()
        
    def setup_styles(self):
        """Configurar estilos de la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Status.TLabel', font=('Arial', 10), foreground='#34495e')
        style.configure('Connected.TLabel', font=('Arial', 10, 'bold'), foreground='#27ae60')
        style.configure('Disconnected.TLabel', font=('Arial', 10, 'bold'), foreground='#e74c3c')
        
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="ZKTeco K40 - Gestor de Dispositivos", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame de conexión
        connection_frame = ttk.LabelFrame(main_frame, text="Configuración de Conexión", padding="10")
        connection_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        connection_frame.columnconfigure(1, weight=1)
        
        # IP Address
        ttk.Label(connection_frame, text="IP Address:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.ip_var = tk.StringVar(value="192.168.100.201")
        self.ip_entry = ttk.Entry(connection_frame, textvariable=self.ip_var, width=20)
        self.ip_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Puerto
        ttk.Label(connection_frame, text="Puerto:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.port_var = tk.StringVar(value="4370")
        self.port_entry = ttk.Entry(connection_frame, textvariable=self.port_var, width=10)
        self.port_entry.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        
        # Botones de conexión
        self.connect_btn = ttk.Button(connection_frame, text="Conectar", command=self.connect_device)
        self.connect_btn.grid(row=0, column=4, padx=(0, 5))
        
        self.disconnect_btn = ttk.Button(connection_frame, text="Desconectar", command=self.disconnect_device, state='disabled')
        self.disconnect_btn.grid(row=0, column=5, padx=(0, 5))
        
        self.refresh_btn = ttk.Button(connection_frame, text="Actualizar", command=self.refresh_data, state='disabled')
        self.refresh_btn.grid(row=0, column=6)
        
        # Estado de conexión
        self.status_label = ttk.Label(connection_frame, text="Desconectado", style='Disconnected.TLabel')
        self.status_label.grid(row=1, column=0, columnspan=7, pady=(10, 0))
        
        # Frame de información del dispositivo
        info_frame = ttk.LabelFrame(main_frame, text="Información del Dispositivo", padding="10")
        info_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(0, weight=1)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=6, width=80)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Frame de usuarios
        users_frame = ttk.LabelFrame(main_frame, text="Usuarios Registrados", padding="10")
        users_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        users_frame.columnconfigure(0, weight=1)
        users_frame.rowconfigure(0, weight=1)
        
        # Treeview para usuarios
        columns = ('ID', 'Nombre', 'Privilegio', 'Tarjeta', 'Huellas', 'Estado')
        self.users_tree = ttk.Treeview(users_frame, columns=columns, show='headings', height=8)
        
        # Configurar columnas
        self.users_tree.heading('ID', text='ID')
        self.users_tree.heading('Nombre', text='Nombre')
        self.users_tree.heading('Privilegio', text='Privilegio')
        self.users_tree.heading('Tarjeta', text='Tarjeta')
        self.users_tree.heading('Huellas', text='Huellas')
        self.users_tree.heading('Estado', text='Estado')
        
        self.users_tree.column('ID', width=50)
        self.users_tree.column('Nombre', width=150)
        self.users_tree.column('Privilegio', width=100)
        self.users_tree.column('Tarjeta', width=100)
        self.users_tree.column('Huellas', width=80)
        self.users_tree.column('Estado', width=80)
        
        # Scrollbar para usuarios
        users_scrollbar = ttk.Scrollbar(users_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=users_scrollbar.set)
        
        self.users_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        users_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Frame de registros de asistencia
        logs_frame = ttk.LabelFrame(main_frame, text="Registros de Asistencia", padding="10")
        logs_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)
        
        # Treeview para registros
        log_columns = ('Usuario', 'Fecha/Hora', 'Tipo', 'Estado')
        self.logs_tree = ttk.Treeview(logs_frame, columns=log_columns, show='headings', height=6)
        
        # Configurar columnas de registros
        self.logs_tree.heading('Usuario', text='Usuario')
        self.logs_tree.heading('Fecha/Hora', text='Fecha/Hora')
        self.logs_tree.heading('Tipo', text='Tipo')
        self.logs_tree.heading('Estado', text='Estado')
        
        self.logs_tree.column('Usuario', width=100)
        self.logs_tree.column('Fecha/Hora', width=150)
        self.logs_tree.column('Tipo', width=80)
        self.logs_tree.column('Estado', width=80)
        
        # Scrollbar para registros
        logs_scrollbar = ttk.Scrollbar(logs_frame, orient=tk.VERTICAL, command=self.logs_tree.yview)
        self.logs_tree.configure(yscrollcommand=logs_scrollbar.set)
        
        self.logs_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        logs_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configurar pesos del grid principal
        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def connect_device(self):
        """Conectar al dispositivo en un hilo separado"""
        def connect_thread():
            try:
                ip = self.ip_var.get()
                port = int(self.port_var.get())
                
                self.device = ZKTecoK40V2(ip, port)
                
                if self.device.connect():
                    self.connected = True
                    self.root.after(0, self.update_connection_status, True)
                    self.root.after(0, self.get_device_info)
                    self.root.after(0, self.get_user_count)
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error", "No se pudo conectar al dispositivo"))
                    
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error de conexión: {error_msg}"))
        
        threading.Thread(target=connect_thread, daemon=True).start()
        
    def disconnect_device(self):
        """Desconectar del dispositivo"""
        if self.device:
            self.device.disconnect()
            self.device = None
            self.connected = False
            self.update_connection_status(False)
            self.clear_data()
            
    def update_connection_status(self, connected):
        """Actualizar el estado de conexión"""
        if connected:
            self.status_label.config(text="Conectado", style='Connected.TLabel')
            self.connect_btn.config(state='disabled')
            self.disconnect_btn.config(state='normal')
            self.refresh_btn.config(state='normal')
        else:
            self.status_label.config(text="Desconectado", style='Disconnected.TLabel')
            self.connect_btn.config(state='normal')
            self.disconnect_btn.config(state='disabled')
            self.refresh_btn.config(state='disabled')
            
    def get_device_info(self):
        """Obtener información del dispositivo"""
        if not self.device or not self.connected:
            return
            
        try:
            info = self.device.get_device_info()
            
            info_text = "Información del Dispositivo:\n"
            info_text += "=" * 40 + "\n"
            
            for key, value in info.items():
                if key == 'network_params':
                    info_text += f"Configuración de Red: {value}\n"
                else:
                    info_text += f"{key.replace('_', ' ').title()}: {value}\n"
            
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info_text)
            
        except Exception as e:
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, f"Error al obtener información: {e}")
            
    def get_user_count(self):
        """Obtener cantidad de usuarios"""
        if not self.device or not self.connected:
            return
            
        try:
            user_count = self.device.get_user_count()
            self.refresh_users()
            self.refresh_logs()
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener usuarios: {e}")
            
    def refresh_data(self):
        """Actualizar todos los datos"""
        if not self.device or not self.connected:
            return
            
        def refresh_thread():
            try:
                self.root.after(0, self.get_device_info)
                self.root.after(0, self.refresh_users)
                self.root.after(0, self.refresh_logs)
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error al actualizar: {error_msg}"))
        
        threading.Thread(target=refresh_thread, daemon=True).start()
        
    def refresh_users(self):
        """Actualizar lista de usuarios"""
        if not self.device or not self.connected:
            return
            
        try:
            # Limpiar lista actual
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)
            
            # Obtener usuarios
            users = self.device.get_user_list()
            
            # Agregar usuarios a la lista
            for user in users:
                privilege = "Admin" if user['privilege'] == 1 else "Usuario"
                status = "Activo" if user['status'] == 0 else "Inactivo"
                
                self.users_tree.insert('', 'end', values=(
                    user['user_id'],
                    user['name'],
                    privilege,
                    user['card'] if user['card'] else "N/A",
                    user['fingerprints'],
                    status
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener usuarios: {e}")
            
    def refresh_logs(self):
        """Actualizar registros de asistencia"""
        if not self.device or not self.connected:
            return
            
        try:
            # Limpiar lista actual
            for item in self.logs_tree.get_children():
                self.logs_tree.delete(item)
            
            # Obtener registros
            logs = self.device.get_attendance_logs()
            
            # Agregar registros a la lista
            for log in logs:
                timestamp = log['timestamp'].strftime("%Y-%m-%d %H:%M:%S") if log['timestamp'] else "N/A"
                punch_type = "Entrada" if log['punch'] == 0 else "Salida"
                status = "OK" if log['status'] == 1 else "Error"
                
                self.logs_tree.insert('', 'end', values=(
                    log['user_id'],
                    timestamp,
                    punch_type,
                    status
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener registros: {e}")
            
    def clear_data(self):
        """Limpiar todos los datos"""
        self.info_text.delete(1.0, tk.END)
        
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
            
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)
            
    def on_closing(self):
        """Manejar cierre de la aplicación"""
        if self.device:
            self.device.disconnect()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ZKTecoGUIV2(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 