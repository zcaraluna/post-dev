#!/usr/bin/env python3
"""
Módulo para visualizar logs de asistencia del sistema QUIRA
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime, timedelta
from zkteco_connector_v2 import ZKTecoK40V2
from database import connect_db

class ControlAsistencia(tk.Toplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.parent = parent
        self.user_data = user_data
        self.zkteco_device = None
        self.connected = False
        self.logs_data = []
        self.device_info = None
        self.nombres_usuarios = {}
        
        # Variables de paginación
        self.current_page = 1
        self.items_per_page = 15
        self.total_pages = 1
        self.all_logs = []  # Todos los logs sin filtrar
        self.sort_recent_first = True  # Ordenamiento: True = más recientes primero
        
        self.title("Control de Asistencia - Sistema QUIRA")
        self.geometry('')
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
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#2c3e50')
        style.configure('Status.TLabel', font=('Segoe UI', 10), foreground='#34495e')
        
        # Frame principal
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Título
        title_label = ttk.Label(main_frame, text="Control de Asistencia", style='Title.TLabel')
        title_label.pack(pady=(0, 5))
        
        # Información del dispositivo
        self.device_info_label = ttk.Label(main_frame, text="Desconectado", font=('Segoe UI', 10), foreground='#e74c3c')
        self.device_info_label.pack(pady=(0, 20))
        
        # Conexión automática al dispositivo
        self.connect_automatically()
        
        # Frame de filtros
        filters_frame = ttk.LabelFrame(main_frame, text="Filtros de Búsqueda", padding=15)
        filters_frame.pack(fill='x', pady=(0, 20))
        
        self.create_filters_controls(filters_frame)
        
        # Frame de resultados
        results_frame = ttk.LabelFrame(main_frame, text="Registros de Asistencia", padding=15)
        results_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        self.create_results_section(results_frame)
        
        # Frame de estadísticas
        stats_frame = ttk.LabelFrame(main_frame, text="Estadísticas", padding=15)
        stats_frame.pack(fill='x', pady=(0, 20))
        
        self.create_stats_section(stats_frame)
        
    def connect_automatically(self):
        """Conectar automáticamente al dispositivo al abrir la ventana"""
        # Configuración por defecto del dispositivo
        self.ip_var = tk.StringVar(value="192.168.100.201")
        self.port_var = tk.StringVar(value="4370")
        
        # Iniciar conexión automática
        self.connect_device()
        
    def create_filters_controls(self, parent):
        """Crear controles de filtros"""
        # Frame para filtros
        filters_frame = ttk.Frame(parent)
        filters_frame.pack(fill='x')
        
        # Fecha desde
        ttk.Label(filters_frame, text="Desde:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.date_from_var = tk.StringVar(value="")
        date_from_entry = ttk.Entry(filters_frame, textvariable=self.date_from_var, width=12)
        date_from_entry.grid(row=0, column=1, padx=(0, 20))
        ttk.Label(filters_frame, text="(DD/MM/AAAA)", font=('Segoe UI', 8), foreground='#7f8c8d').grid(row=1, column=1, sticky='w', padx=(0, 20))
        
        # Fecha hasta
        ttk.Label(filters_frame, text="Hasta:").grid(row=0, column=2, sticky='w', padx=(0, 10))
        self.date_to_var = tk.StringVar(value="")
        date_to_entry = ttk.Entry(filters_frame, textvariable=self.date_to_var, width=12)
        date_to_entry.grid(row=0, column=3, padx=(0, 20))
        ttk.Label(filters_frame, text="(DD/MM/AAAA)", font=('Segoe UI', 8), foreground='#7f8c8d').grid(row=1, column=3, sticky='w', padx=(0, 20))
        
        # Usuario específico
        ttk.Label(filters_frame, text="Postulante:").grid(row=0, column=4, sticky='w', padx=(0, 10))
        self.user_filter_var = tk.StringVar()
        user_filter_entry = ttk.Entry(filters_frame, textvariable=self.user_filter_var, width=15)
        user_filter_entry.grid(row=0, column=5, padx=(0, 20))
        
        # Botón buscar (debajo del campo Postulante)
        self.search_btn = ttk.Button(filters_frame, text="Buscar", command=self.search_logs)
        self.search_btn.grid(row=1, column=5, sticky='w', pady=(5, 0))
        
        # Botón limpiar (en su posición original)
        self.clear_btn = ttk.Button(filters_frame, text="Limpiar filtros", command=self.clear_filters)
        self.clear_btn.grid(row=0, column=6, padx=(0, 10))
        
        # Frame para ordenamiento
        sort_frame = ttk.Frame(filters_frame)
        sort_frame.grid(row=0, column=7, padx=(0, 10))
        
        ttk.Label(sort_frame, text="Ordenar:").pack(side='left', padx=(0, 5))
        self.sort_var = tk.StringVar(value="Más recientes primero")
        sort_combo = ttk.Combobox(sort_frame, textvariable=self.sort_var, values=["Más recientes primero", "Más antiguos primero"], 
                                 state="readonly", width=20)
        sort_combo.pack(side='left')
        sort_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_sort())
        
        # Configurar grid
        filters_frame.columnconfigure(8, weight=1)
        
    def create_results_section(self, parent):
        """Crear sección de resultados"""
        # Frame para tabla
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill='both', expand=True)
        
        # Crear Treeview con scrollbars
        columns = ('user_id', 'name', 'date', 'time')
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        # Configurar columnas
        self.tree.heading('user_id', text='UID en K40')
        self.tree.heading('name', text='Nombre')
        self.tree.heading('date', text='Fecha')
        self.tree.heading('time', text='Hora')
        
        # Configurar anchos de columna
        self.tree.column('user_id', width=100, minwidth=80)
        self.tree.column('name', width=300, minwidth=200)
        self.tree.column('date', width=120, minwidth=100)
        self.tree.column('time', width=120, minwidth=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Empaquetar
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configurar grid
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Frame para paginación
        pagination_frame = ttk.Frame(parent)
        pagination_frame.pack(fill='x', pady=(10, 0))
        
        # Frame interno para centrar los controles
        center_frame = ttk.Frame(pagination_frame)
        center_frame.pack(expand=True)
        
        # Primera línea: Controles de paginación (Anterior, Página X de X, Siguiente)
        pagination_line1 = ttk.Frame(center_frame)
        pagination_line1.pack()
        
        self.prev_btn = ttk.Button(pagination_line1, text="◀ Anterior", command=self.prev_page, state='disabled')
        self.prev_btn.pack(side='left', padx=(0, 10))
        
        # Información de página
        self.page_info = tk.StringVar(value="Página 1 de 1")
        page_label = ttk.Label(pagination_line1, textvariable=self.page_info, font=('Segoe UI', 10, 'bold'))
        page_label.pack(side='left', padx=(0, 10))
        
        self.next_btn = ttk.Button(pagination_line1, text="Siguiente ▶", command=self.next_page, state='disabled')
        self.next_btn.pack(side='left')
        
        # Segunda línea: Navegación directa a página
        pagination_line2 = ttk.Frame(center_frame)
        pagination_line2.pack(pady=(5, 0))
        
        ttk.Label(pagination_line2, text="Ir a página:").pack(side='left', padx=(0, 5))
        self.page_entry_var = tk.StringVar()
        page_entry = ttk.Entry(pagination_line2, textvariable=self.page_entry_var, width=5)
        page_entry.pack(side='left', padx=(0, 5))
        page_entry.bind('<Return>', lambda e: self.go_to_page())
        
        ttk.Button(pagination_line2, text="Ir", command=self.go_to_page).pack(side='left')
        
        # Información de resultados
        self.results_info = tk.StringVar(value="No hay registros para mostrar")
        info_label = ttk.Label(parent, textvariable=self.results_info, font=('Segoe UI', 10))
        info_label.pack(pady=(5, 0))
        
    def create_stats_section(self, parent):
        """Crear sección de estadísticas"""
        # Frame para estadísticas
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill='x')
        
        # Variables para estadísticas
        self.total_records = tk.StringVar(value="0")
        self.today_records = tk.StringVar(value="0")
        self.unique_users = tk.StringVar(value="0")
        
        # Crear etiquetas de estadísticas
        stats_data = [
            ("Total de Registros en el dispositivo:", self.total_records),
            ("Registros totales de hoy:", self.today_records),
            ("Registros únicos:", self.unique_users)
        ]
        
        for i, (label, var) in enumerate(stats_data):
            ttk.Label(stats_frame, text=label, font=('Segoe UI', 10, 'bold')).grid(row=0, column=i*2, sticky='w', padx=(0, 5))
            ttk.Label(stats_frame, textvariable=var, font=('Segoe UI', 10)).grid(row=0, column=i*2+1, sticky='w', padx=(0, 20))
        
        # Configurar grid
        stats_frame.columnconfigure(7, weight=1)
        
    def center_window(self):
        """Centrar la ventana"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def obtener_info_dispositivo(self, serial_number):
        """Obtener información del dispositivo desde la base de datos"""
        try:
            conn = connect_db()
            if not conn:
                return None, "No disponible"
                
            cursor = conn.cursor()
            
            # Buscar el aparato biométrico en la base de datos por su número de serie
            cursor.execute("""
                SELECT id, nombre FROM aparatos_biometricos
                WHERE serial = %s
                LIMIT 1;
            """, (serial_number,))
            
            aparato = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if aparato:
                return aparato[0], aparato[1]  # Retorna ID y Nombre
            else:
                return None, "No disponible"
                
        except Exception as e:
            print(f"Error al obtener información del dispositivo: {e}")
            return None, "No disponible"
            
    def cargar_nombres_usuarios_dispositivo(self):
        """Cargar nombres de usuarios directamente del dispositivo ZKTeco"""
        try:
            if not self.zkteco_device or not self.connected:
                print("DEBUG: No hay dispositivo conectado para obtener usuarios")
                return {}
            
            # Obtener usuarios directamente del dispositivo
            users = self.zkteco_device.get_user_list()
            print(f"DEBUG: Usuarios obtenidos del dispositivo: {users}")
            
            # Crear diccionario {user_id: name}
            nombres_usuarios = {}
            for user in users:
                user_id = user.get('user_id', '')
                name = user.get('name', '')
                if user_id and name:
                    nombres_usuarios[str(user_id)] = name
                    print(f"DEBUG: Usuario cargado - ID: {user_id}, Nombre: {name}")
            
            print(f"DEBUG: Cargados {len(nombres_usuarios)} usuarios del dispositivo")
            return nombres_usuarios
                
        except Exception as e:
            print(f"Error al cargar usuarios del dispositivo: {e}")
            return {}
        
    def connect_device(self):
        """Conectar al dispositivo"""
        ip = self.ip_var.get().strip()
        port = self.port_var.get().strip()
        
        if not ip or not port:
            self.device_info_label.config(text="Error: IP o puerto no configurado", foreground='#e74c3c')
            return
            
        try:
            port = int(port)
        except ValueError:
            self.device_info_label.config(text="Error: Puerto inválido", foreground='#e74c3c')
            return
        
        # Actualizar estado de conexión
        self.device_info_label.config(text="Conectando al dispositivo...", foreground='#f39c12')
        
        def connect_thread():
            try:
                # Crear dispositivo
                self.zkteco_device = ZKTecoK40V2(ip, port)
                
                # Intentar conectar
                if self.zkteco_device.connect():
                    # Obtener información del dispositivo
                    try:
                        device_info = self.zkteco_device.get_device_info()
                        serial_number = device_info.get('serial_number', 'No disponible')
                        
                        # Obtener información desde la base de datos
                        device_id, device_name = self.obtener_info_dispositivo(serial_number)
                        self.device_info = {
                            'id': device_id,
                            'name': device_name,
                            'serial': serial_number
                        }
                        
                        # Actualizar título de la ventana con información del dispositivo
                        if device_name and device_name != "No disponible":
                            self.after(0, lambda: self.title(f"Control de Asistencia - {device_name} ({serial_number}) - Sistema QUIRA"))
                            self.after(0, lambda: self.device_info_label.config(text=f"Conectado a: {device_name} ({serial_number})", foreground='#27ae60'))
                        else:
                            self.after(0, lambda: self.title(f"Control de Asistencia - Dispositivo {serial_number} - Sistema QUIRA"))
                            self.after(0, lambda: self.device_info_label.config(text=f"Conectado a: Dispositivo {serial_number}", foreground='#27ae60'))
                            
                    except Exception as e:
                        print(f"Error obteniendo información del dispositivo: {e}")
                        self.device_info = None
                        self.after(0, lambda: self.device_info_label.config(text=f"Conectado a: Dispositivo {serial_number}", foreground='#27ae60'))
                    
                    self.after(0, lambda: setattr(self, 'connected', True))
                    
                    # Cargar logs automáticamente
                    self.after(0, self.search_logs)
                else:
                    self.after(0, lambda: self.device_info_label.config(text="❌ Error: No se pudo conectar al dispositivo", foreground='#e74c3c'))
                    
            except Exception as e:
                self.after(0, lambda: self.device_info_label.config(text=f"❌ Error de conexión: {str(e)}", foreground='#e74c3c'))
        
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
        self.device_info_label.config(text="❌ Desconectado", foreground='#e74c3c')
        
        # Limpiar datos
        self.clear_results()
        self.nombres_usuarios = {}
        self.all_logs = []
        self.current_page = 1
        self.total_pages = 1
        
    def search_logs(self):
        """Buscar logs de asistencia"""
        if not self.connected:
            self.results_info.set("❌ No hay conexión al dispositivo")
            return
        
        # Limpiar resultados anteriores
        self.clear_results()
        
        # Mostrar indicador de carga
        self.results_info.set("🔄 Cargando registros...")
        
        def search_thread():
            try:
                # Cargar nombres de usuarios solo si no están cargados
                if not self.nombres_usuarios:
                    print("DEBUG: Cargando usuarios del dispositivo...")
                    self.nombres_usuarios = self.cargar_nombres_usuarios_dispositivo()
                else:
                    print("DEBUG: Usuarios ya cargados, reutilizando...")
                
                # Obtener logs del dispositivo
                logs = self.zkteco_device.get_attendance_logs()
                
                if not logs:
                    self.after(0, lambda: self.results_info.set("No se encontraron registros de asistencia"))
                    return
                
                # Debug: imprimir información de los logs
                print(f"DEBUG: Se obtuvieron {len(logs)} logs del dispositivo")
                if logs:
                    print(f"DEBUG: Primer log: {logs[0]}")
                    print(f"DEBUG: Tipos de datos del primer log:")
                    for key, value in logs[0].items():
                        print(f"  {key}: {value} (tipo: {type(value)})")
                
                # Filtrar logs según criterios
                filtered_logs = self.filter_logs(logs)
                print(f"DEBUG: Después del filtro: {len(filtered_logs)} logs")
                
                # Aplicar ordenamiento y guardar logs filtrados
                self.all_logs = self.sort_logs(filtered_logs)
                self.current_page = 1
                self.total_pages = max(1, (len(filtered_logs) + self.items_per_page - 1) // self.items_per_page)
                
                # Mostrar primera página
                self.after(0, self.display_current_page)
                
            except Exception as e:
                print(f"DEBUG: Error en search_logs: {e}")
                self.after(0, lambda: self.results_info.set(f"Error al cargar registros: {str(e)}"))
                self.after(0, lambda: messagebox.showerror("Error", f"Error al cargar registros: {str(e)}"))
        
        threading.Thread(target=search_thread, daemon=True).start()
        
    def filter_logs(self, logs):
        """Filtrar logs según criterios"""
        filtered = []
        
        # Obtener filtros
        date_from = self.date_from_var.get()
        date_to = self.date_to_var.get()
        user_filter = self.user_filter_var.get().strip().lower()
        
        # Si no hay filtros de fecha, mostrar todos los logs
        if not date_from and not date_to and not user_filter:
            return logs
            
        print(f"DEBUG: Aplicando filtros - Desde: '{date_from}', Hasta: '{date_to}', Usuario: '{user_filter}'")
        print(f"DEBUG: Nombres de usuarios disponibles: {self.nombres_usuarios}")
        
        for log in logs:
            # Filtrar por usuario
            if user_filter:
                user_id = str(log.get('user_id', '')).lower()
                # Obtener nombre del usuario desde el diccionario cargado
                user_name = self.nombres_usuarios.get(log.get('user_id', ''), '').lower()
                
                # Buscar en ID de usuario o en nombre
                if user_filter not in user_id and user_filter not in user_name:
                    print(f"DEBUG: Filtrado usuario - ID: {user_id}, Nombre: '{user_name}', Filtro: '{user_filter}'")
                    continue
                else:
                    print(f"DEBUG: Usuario incluido - ID: {user_id}, Nombre: '{user_name}', Filtro: '{user_filter}'")
            
            # Filtrar por fecha
            timestamp = log.get('timestamp', None)
            if timestamp:
                try:
                    # Si timestamp es ya un objeto datetime
                    if isinstance(timestamp, datetime):
                        dt = timestamp
                    else:
                        # Si es un número, convertir a datetime
                        dt = datetime.fromtimestamp(timestamp)
                    
                    # Convertir fecha del log a formato DD/MM/AAAA para comparación
                    log_date = dt.strftime('%d/%m/%Y')
                    
                    # Comparar fechas en formato DD/MM/AAAA
                    if date_from and log_date < date_from:
                        print(f"DEBUG: Filtrado por fecha - Log: {log_date}, Desde: {date_from}")
                        continue
                    if date_to and log_date > date_to:
                        print(f"DEBUG: Filtrado por fecha - Log: {log_date}, Hasta: {date_to}")
                        continue
                        
                    print(f"DEBUG: Fecha incluida - Log: {log_date}, Desde: {date_from}, Hasta: {date_to}")
                except Exception as e:
                    print(f"DEBUG: Error filtrando por fecha: {e}")
                    continue
            
            filtered.append(log)
        
        return filtered
        
    def sort_logs(self, logs):
        """Ordenar logs según el criterio seleccionado"""
        if not logs:
            return logs
            
        # Determinar el orden según la selección
        sort_recent_first = self.sort_var.get() == "Más recientes primero"
        
        # Ordenar por timestamp
        sorted_logs = sorted(logs, key=lambda log: log.get('timestamp', 0), reverse=sort_recent_first)
        
        return sorted_logs
        
    def apply_sort(self):
        """Aplicar ordenamiento a los logs actuales"""
        if self.all_logs:
            self.all_logs = self.sort_logs(self.all_logs)
            self.current_page = 1
            self.display_current_page()
        
    def go_to_page(self):
        """Ir a una página específica"""
        try:
            page_num = int(self.page_entry_var.get())
            if 1 <= page_num <= self.total_pages:
                self.current_page = page_num
                self.display_current_page()
                self.page_entry_var.set("")  # Limpiar entrada
            else:
                messagebox.showwarning("Página inválida", f"La página debe estar entre 1 y {self.total_pages}")
        except ValueError:
            messagebox.showwarning("Entrada inválida", "Por favor ingrese un número válido")
        
    def update_results(self, logs):
        """Actualizar resultados en la tabla"""
        print(f"DEBUG: update_results llamado con {len(logs)} logs")
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Agregar registros
        for i, log in enumerate(logs):
            print(f"DEBUG: Procesando log {i+1}: {log}")
            
            # Convertir timestamp a fecha y hora
            timestamp = log.get('timestamp', None)
            if timestamp:
                try:
                    # Si timestamp es ya un objeto datetime
                    if isinstance(timestamp, datetime):
                        dt = timestamp
                    else:
                        # Si es un número, convertir a datetime
                        dt = datetime.fromtimestamp(timestamp)
                    
                    date = dt.strftime('%d/%m/%Y')
                    time = dt.strftime('%H:%M:%S')
                except Exception as e:
                    print(f"DEBUG: Error convirtiendo timestamp {timestamp}: {e}")
                    date = "N/A"
                    time = "N/A"
            else:
                date = "N/A"
                time = "N/A"
            
            # Obtener nombre del usuario desde el diccionario cargado
            user_id = log.get('user_id', 'N/A')
            if user_id != 'N/A':
                nombre_usuario = self.nombres_usuarios.get(str(user_id), "")
            else:
                nombre_usuario = ""
            
            # Preparar valores para la tabla
            values = (
                user_id,
                nombre_usuario,
                date,
                time
            )
            
            print(f"DEBUG: Insertando en tabla: {values}")
            
            # Insertar en tabla
            self.tree.insert('', 'end', values=values)
        
        # Actualizar información
        self.logs_data = logs
        self.results_info.set(f"Mostrando {len(logs)} de {len(self.all_logs)} registros")
        
        # Actualizar estadísticas con todos los logs
        self.update_statistics(self.all_logs)
        
        print(f"DEBUG: update_results completado. Registros en tabla: {len(self.tree.get_children())}")
        
    def update_statistics(self, logs):
        """Actualizar estadísticas"""
        if not logs:
            self.total_records.set("0")
            self.today_records.set("0")
            self.unique_users.set("0")
            return
        
        # Total de registros
        self.total_records.set(str(len(logs)))
        
        # Registros de hoy
        today = datetime.now().date()
        today_count = 0
        unique_users = set()
        
        for log in logs:
            timestamp = log.get('timestamp', None)
            if timestamp:
                try:
                    # Si timestamp es ya un objeto datetime
                    if isinstance(timestamp, datetime):
                        dt = timestamp
                    else:
                        # Si es un número, convertir a datetime
                        dt = datetime.fromtimestamp(timestamp)
                    
                    log_date = dt.date()
                    if log_date == today:
                        today_count += 1
                except Exception as e:
                    print(f"DEBUG: Error en estadísticas de fecha: {e}")
                    pass
            
            # Usuarios únicos
            user_id = log.get('user_id', '')
            if user_id and user_id != 'N/A':
                unique_users.add(user_id)
        
        self.today_records.set(str(today_count))
        self.unique_users.set(str(len(unique_users)))
        
    def prev_page(self):
        """Ir a la página anterior"""
        if self.current_page > 1:
            self.current_page -= 1
            self.display_current_page()
    
    def next_page(self):
        """Ir a la página siguiente"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_current_page()
    
    def display_current_page(self):
        """Mostrar la página actual"""
        if not self.all_logs:
            return
        
        # Calcular índices de inicio y fin
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        
        # Obtener logs de la página actual
        page_logs = self.all_logs[start_idx:end_idx]
        
        # Actualizar tabla
        self.update_results(page_logs)
        
        # Actualizar controles de paginación
        self.update_pagination_controls()
    
    def update_pagination_controls(self):
        """Actualizar estado de los controles de paginación"""
        # Actualizar información de página
        self.page_info.set(f"Página {self.current_page} de {self.total_pages}")
        
        # Habilitar/deshabilitar botones
        self.prev_btn.config(state='normal' if self.current_page > 1 else 'disabled')
        self.next_btn.config(state='normal' if self.current_page < self.total_pages else 'disabled')
    
    def clear_filters(self):
        """Limpiar filtros"""
        self.date_from_var.set("")
        self.date_to_var.set("")
        self.user_filter_var.set("")
        self.page_entry_var.set("")  # Limpiar entrada de página
        
        # Ejecutar búsqueda automáticamente después de limpiar filtros
        self.search_logs()
        
    def clear_results(self):
        """Limpiar resultados"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.logs_data = []
        self.all_logs = []
        self.current_page = 1
        self.total_pages = 1
        self.results_info.set("No hay registros para mostrar")
        self.page_info.set("Página 1 de 1")
        self.page_entry_var.set("")  # Limpiar entrada de página
        self.total_records.set("0")
        self.today_records.set("0")
        self.unique_users.set("0")
        
        # Deshabilitar controles de paginación
        self.prev_btn.config(state='disabled')
        self.next_btn.config(state='disabled')
        
    def on_closing(self):
        """Manejar cierre de ventana"""
        if self.connected:
            self.disconnect_device()
        self.destroy()

def main():
    """Función de prueba"""
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    # Datos de usuario de prueba
    user_data = {
        'id': 1,
        'nombre': 'Usuario',
        'apellido': 'Prueba',
        'grado': 'Oficial',
        'rol': 'ADMIN'
    }
    
    # Crear ventana de control de asistencia
    control_window = ControlAsistencia(root, user_data)
    
    root.mainloop()

if __name__ == "__main__":
    main()
