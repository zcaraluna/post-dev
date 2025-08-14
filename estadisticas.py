#!/usr/bin/env python3
"""
Módulo de estadísticas del sistema - Versión simplificada y funcional
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db
from datetime import datetime, timedelta
import ctypes
import locale

# Configurar locale para formato de números latinoamericano
try:
    locale.setlocale(locale.LC_ALL, 'es_PY.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Spanish_Spain.1252')
    except:
        pass

def formatear_numero(numero, decimales=0):
    """
    Formatea un número con separadores de miles (puntos) y decimales (comas)
    Ejemplo: 1000000 -> 1.000.000, 10.5 -> 10,5
    """
    if numero is None:
        return "0"
    
    # Convertir a float para manejar decimales
    numero_float = float(numero)
    
    if decimales == 0:
        # Número entero
        return f"{int(numero_float):,}".replace(",", ".")
    else:
        # Número con decimales
        numero_str = f"{numero_float:.{decimales}f}"
        parte_entera, parte_decimal = numero_str.split('.')
        
        # Formatear parte entera con separadores de miles
        parte_entera_formateada = f"{int(parte_entera):,}".replace(",", ".")
        
        # Combinar con coma decimal
        return f"{parte_entera_formateada},{parte_decimal}"

def formatear_porcentaje(porcentaje, decimales=1):
    """
    Formatea un porcentaje con separadores decimales (comas)
    Ejemplo: 10.5 -> 10,5%
    """
    if porcentaje is None:
        return "0,0%"
    
    # Convertir a float para manejar decimales
    porcentaje_float = float(porcentaje)
    
    # Formatear con coma decimal
    porcentaje_str = f"{porcentaje_float:.{decimales}f}"
    parte_entera, parte_decimal = porcentaje_str.split('.')
    
    # Combinar con coma decimal y símbolo %
    return f"{parte_entera},{parte_decimal}%"

# Configurar DPI para Windows (HD/4K)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

class Estadisticas(tk.Toplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.parent = parent
        self.user_data = user_data
        
        # Variable para controlar el estado del interruptor de edades individuales
        self.show_individual_ages = tk.BooleanVar(value=False)
        
        self.title("Estadísticas del Sistema")
        self.geometry('')
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        # Configurar estilo consistente con el resto del sistema
        self.configure(bg='white')
        
        self.setup_ui()
        self.center_window()
        
        # Cargar estadísticas después de que la interfaz esté completamente creada
        self.after(200, self.load_statistics)
        
    def setup_ui(self):
        """Configurar la interfaz principal"""
        # Configurar el fondo de la ventana principal
        self.configure(bg='white')
        
        # Título principal directamente en la ventana
        title_label = tk.Label(self, text="ESTADÍSTICAS DEL SISTEMA", 
                               font=('Segoe UI', 16, 'bold'), 
                               fg='#2c3e50', bg='white')
        title_label.pack(pady=(20, 5))
        
        subtitle_label = tk.Label(self, text="Resumen de actividad y métricas", 
                                 font=('Segoe UI', 10), 
                                 fg='#7f8c8d', bg='white')
        subtitle_label.pack(pady=(0, 20))
        
        # Notebook directamente en la ventana principal
        self.create_detailed_stats(self)
        
    def create_detailed_stats(self, parent):
        """Crear estadísticas detalladas"""
        # Notebook para pestañas
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Pestaña 1: Resumen general
        summary_frame = tk.Frame(notebook, bg='white')
        notebook.add(summary_frame, text="Resumen General")
        self.create_summary_tab(summary_frame)
        
        # Pestaña 2: Estadísticas generales
        general_frame = tk.Frame(notebook, bg='white')
        notebook.add(general_frame, text="Estadísticas Específicas")
        self.create_general_tab(general_frame)
        
        # Pestaña 3: Registros por hora
        hourly_frame = tk.Frame(notebook, bg='white')
        notebook.add(hourly_frame, text="Registros por Hora")
        self.create_hourly_tab(hourly_frame)
        
    def create_summary_tab(self, parent):
        """Crear pestaña de resumen general"""
        # Contenido del resumen directamente en el parent
        self.create_summary_content(parent)
        
    def create_summary_content(self, parent):
        """Crear contenido del resumen"""
        # Métricas principales
        metrics_frame = tk.Frame(parent, bg='white')
        metrics_frame.pack(fill='x', padx=20, pady=20)
        
        # Título de métricas
        metrics_title = tk.Label(metrics_frame, text="Métricas Principales", 
                                font=('Segoe UI', 12, 'bold'), 
                                fg='#2c3e50', bg='white')
        metrics_title.pack(anchor='w', pady=(0, 10))
        
        # Variables para métricas
        self.total_postulantes_var = tk.StringVar(value="0")
        self.total_usuarios_var = tk.StringVar(value="0")
        self.postulantes_hoy_var = tk.StringVar(value="0")
        self.postulantes_semana_var = tk.StringVar(value="0")
        self.postulantes_mes_var = tk.StringVar(value="0")
        
        # Frame para las métricas
        metrics_container = tk.Frame(metrics_frame, bg='white')
        metrics_container.pack(fill='x')
        
        # Crear métricas en una cuadrícula
        metrics = [
            ("Total de Postulantes", self.total_postulantes_var, "#4a90e2"),
            ("Total de Usuarios", self.total_usuarios_var, "#4a90e2"),
            ("Postulantes Hoy", self.postulantes_hoy_var, "#4a90e2"),
            ("Postulantes Esta Semana", self.postulantes_semana_var, "#4a90e2"),
            ("Postulantes Este Mes", self.postulantes_mes_var, "#4a90e2")
        ]
        
        for i, (label, var, color) in enumerate(metrics):
            metric_frame = tk.Frame(metrics_container, bg='white')
            metric_frame.grid(row=0, column=i, padx=10, pady=10, sticky='ew')
            
            # Label del título
            title_label = tk.Label(metric_frame, text=label, 
                                  font=('Segoe UI', 9), 
                                  fg='#7f8c8d', bg='white')
            title_label.pack()
            
            # Valor de la métrica
            value_label = tk.Label(metric_frame, textvariable=var, 
                                  font=('Segoe UI', 18, 'bold'), 
                                  fg=color, bg='white')
            value_label.pack()
            
            # Configurar peso de columna
            metrics_container.columnconfigure(i, weight=1)
        
        # Estadísticas generales
        general_frame = tk.Frame(parent, bg='white')
        general_frame.pack(fill='x', pady=(0, 20))
        
        # Título
        general_title = tk.Label(general_frame, text="Estadísticas Generales", 
                                font=('Segoe UI', 12, 'bold'), 
                                fg='#2c3e50', bg='white')
        general_title.pack(anchor='w', pady=(0, 10))
        
        # Variables para estadísticas
        self.stats_vars = {
            'promedio_edad': tk.StringVar(value="N/A"),
            'edad_minima': tk.StringVar(value="N/A"),
            'edad_maxima': tk.StringVar(value="N/A"),
            'ultimo_registro': tk.StringVar(value="N/A"),
            'primer_registro': tk.StringVar(value="N/A"),
            'total_unidades': tk.StringVar(value="0")
        }
        
        # Crear estadísticas en una cuadrícula
        stats_grid = tk.Frame(general_frame, bg='white')
        stats_grid.pack(fill='x')
        
        stats_data = [
            ("Promedio de Edad:", self.stats_vars['promedio_edad']),
            ("Edad Mínima:", self.stats_vars['edad_minima']),
            ("Edad Máxima:", self.stats_vars['edad_maxima']),
            ("Último Registro:", self.stats_vars['ultimo_registro']),
            ("Primer Registro:", self.stats_vars['primer_registro']),
            ("Total de Unidades:", self.stats_vars['total_unidades'])
        ]
        
        for i, (label, var) in enumerate(stats_data):
            row = i // 2
            col = i % 2
            
            stat_frame = tk.Frame(stats_grid, bg='white')
            stat_frame.grid(row=row, column=col, sticky='ew', padx=(0, 20), pady=5)
            
            tk.Label(stat_frame, text=label, 
                    font=('Segoe UI', 9), 
                    fg='#7f8c8d', bg='white').pack(anchor='w')
            tk.Label(stat_frame, textvariable=var, 
                    font=('Segoe UI', 11, 'bold'), 
                    fg='#2c3e50', bg='white').pack(anchor='w')
            
            stats_grid.columnconfigure(col, weight=1)
        
    def create_general_tab(self, parent):
        """Crear pestaña de estadísticas generales"""
        # Título principal
        title = tk.Label(parent, 
                        text="Estadísticas Generales", 
                        font=('Segoe UI', 16, 'bold'), 
                        fg='#2c3e50', 
                        bg='white')
        title.pack(pady=20)
        
        # Solo una sección: Distribución por Unidad de Inscripción
        self.create_simple_unidad_section(parent)
        
    def create_toggle_switch(self, parent, text, variable, command=None):
        """Crear un interruptor moderno (toggle switch)"""
        # Frame principal del interruptor
        switch_frame = tk.Frame(parent, bg=parent.cget('bg'))
        
        # Label del texto
        label = tk.Label(switch_frame, text=text, 
                        font=('Segoe UI', 10, 'bold'),
                        fg='#2c3e50', bg=parent.cget('bg'))
        label.pack(side='left', padx=(0, 8))
        
        # Frame del interruptor
        toggle_frame = tk.Frame(switch_frame, bg='#e0e0e0', width=45, height=22, relief='flat', bd=0)
        toggle_frame.pack(side='left')
        toggle_frame.pack_propagate(False)
        
        # Círculo del interruptor
        toggle_circle = tk.Frame(toggle_frame, bg='white', width=18, height=18, relief='flat', bd=0)
        toggle_circle.place(x=2, y=2)
        
        # Agregar sombra sutil al círculo
        toggle_circle.configure(relief='raised', bd=1)
        
        # Función para actualizar el interruptor
        def update_switch():
            if variable.get():
                toggle_frame.config(bg='#4CAF50')  # Verde cuando está activado
                toggle_circle.place(x=25, y=2)  # Mover a la derecha
            else:
                toggle_frame.config(bg='#e0e0e0')  # Gris cuando está desactivado
                toggle_circle.place(x=2, y=2)  # Mover a la izquierda
        
        # Función para manejar el clic
        def toggle_switch():
            variable.set(not variable.get())
            update_switch()
            if command:
                command()
        
        # Configurar eventos
        toggle_frame.bind('<Button-1>', lambda e: toggle_switch())
        toggle_circle.bind('<Button-1>', lambda e: toggle_switch())
        
        # Configurar el estado inicial
        update_switch()
        
        return switch_frame
        
    def on_age_display_changed(self):
        """Manejar el cambio en el interruptor de edades individuales"""
        # Recargar la estadística actual si estamos en la pestaña de edades
        if self.current_stat == 2:  # Índice de la pestaña de edades
            self.load_edad_data_simple()
        
    def create_simple_unidad_section(self, parent):
        """Crear sección simple para distribución por unidad"""
        # Frame para la sección
        section_frame = tk.Frame(parent, bg='white')
        section_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Header de la sección
        header_frame = tk.Frame(section_frame, bg='#2E5090', height=50)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Título de la sección (variable)
        self.section_title_label = tk.Label(header_frame, 
                                           text="📍 Distribución por Unidad de Inscripción", 
                                           font=('Segoe UI', 14, 'bold'), 
                                           fg='white', 
                                           bg='#2E5090')
        self.section_title_label.pack(expand=True)
        
        # Área de contenido
        content_frame = tk.Frame(section_frame, bg='white', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Frame para contener la tabla y scrollbar
        table_frame = tk.Frame(content_frame, bg='white')
        table_frame.pack(fill='both', expand=False)
        
        # Configurar estilo moderno para la tabla
        style = ttk.Style()
        style.theme_use("clam")
        
        # Estilo moderno para las filas
        style.configure("Modern.Treeview", 
                       background="#ffffff",
                       foreground="#2d3748", 
                       rowheight=32,
                       fieldbackground="#ffffff",
                       font=('Segoe UI', 11),
                       borderwidth=0,
                       relief="flat")
        
        # Estilo moderno para los headers
        style.configure("Modern.Treeview.Heading", 
                       background="#2E5090",
                       foreground="white", 
                       font=('Segoe UI', 12, 'bold'),
                       borderwidth=0,
                       relief="flat",
                       anchor="center")
        
        # Colores para filas seleccionadas y hover
        style.map("Modern.Treeview",
                 background=[('selected', '#e3f2fd'),
                            ('active', '#f5f5f5')],
                 foreground=[('selected', '#1565c0'),
                            ('active', '#2d3748')])
        
        # Crear tabla (Treeview) con columnas (sin columna ordinal)
        columns = ("unidad", "registros", "porcentaje")
        self.stats_table = ttk.Treeview(table_frame, 
                                      columns=columns, 
                                      show='headings',
                                      style="Modern.Treeview",
                                      height=12)
        
        # Configurar headers de columnas
        self.stats_table.heading("unidad", text="UNIDAD DE INSCRIPCIÓN")
        self.stats_table.heading("registros", text="REGISTROS")
        self.stats_table.heading("porcentaje", text="PORCENTAJE")
        
        # Configurar ancho de columnas (redistribuir el espacio)
        self.stats_table.column("unidad", width=350, anchor="w")
        self.stats_table.column("registros", width=120, anchor="center")
        self.stats_table.column("porcentaje", width=120, anchor="center")
        
        # Scrollbar vertical para la tabla
        table_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.stats_table.yview)
        self.stats_table.configure(yscrollcommand=table_scrollbar.set)
        
        # Empaquetar tabla y scrollbar
        self.stats_table.pack(side="left", fill="both", expand=True)
        table_scrollbar.pack(side="right", fill="y")
        
        # Paginación para navegar entre estadísticas
        pagination_frame = tk.Frame(content_frame, bg='white', height=60)
        pagination_frame.pack(fill='x', pady=(15, 10))
        pagination_frame.pack_propagate(False)
        
        # Variables para la paginación
        self.current_stat = 0
        self.stat_names = [
            "Distribución por Unidad de Inscripción",
            "Distribución por Dedo Registrado", 
            "Distribución por Edades",
            "Distribución por Sexo",
            "Distribución por Día de la Semana",
            "Registros por Años",
            "Horarios de Pico de Registro",
            "Distribución por Rango de Edad y Sexo",
            "Edad Promedio por Unidad",
            "Top 5 Usuarios Más Activos"
        ]
        self.stat_titles = [
            "Distribución por Unidad de Inscripción",
            "Distribución por Dedo Registrado",
            "Distribución por Grupos Etarios",
            "Distribución por Sexo",
            "Distribución por Día de la Semana",
            "Registros por Años",
            "Horarios de Pico de Registro",
            "Distribución por Rango de Edad y Sexo",
            "Edad Promedio por Unidad",
            "Usuarios con más registros realizados"
        ]
        
        # Contenedor centrado para los botones
        centered_frame = tk.Frame(pagination_frame, bg='white')
        centered_frame.pack(expand=True)
        
        # Botón anterior
        self.prev_btn = tk.Button(centered_frame, 
                                 text="◀ Anterior", 
                                 font=('Segoe UI', 10, 'bold'), 
                                 fg='#2E5090', 
                                 bg='white',
                                 relief='flat',
                                 bd=1,
                                 padx=15,
                                 pady=6,
                                 cursor='hand2',
                                 command=self.prev_stat)
        self.prev_btn.pack(side='left')
        
        # Indicador de página actual
        self.page_label = tk.Label(centered_frame, 
                                  text="1 / 4", 
                                  font=('Segoe UI', 10, 'bold'), 
                                  fg='#2E5090', 
                                  bg='white')
        self.page_label.pack(side='left', padx=(20, 20))
        
        # Botón siguiente (mismo color que anterior)
        self.next_btn = tk.Button(centered_frame, 
                                 text="Siguiente ▶", 
                                 font=('Segoe UI', 10, 'bold'), 
                                 fg='#2E5090', 
                                 bg='white',
                                 relief='flat',
                                 bd=1,
                                 padx=15,
                                 pady=6,
                                 cursor='hand2',
                                 command=self.next_stat)
        self.next_btn.pack(side='left')
        
        # Actualizar estado inicial de botones
        self.update_pagination_buttons()
        
    def prev_stat(self):
        """Ir a la estadística anterior"""
        if self.current_stat > 0:
            self.current_stat -= 1
            self.load_current_stat()
            self.update_pagination_buttons()
            
    def next_stat(self):
        """Ir a la siguiente estadística"""
        if self.current_stat < len(self.stat_names) - 1:
            self.current_stat += 1
            self.load_current_stat()
            self.update_pagination_buttons()
            
    def update_pagination_buttons(self):
        """Actualizar el estado de los botones de paginación"""
        # Actualizar texto del indicador
        current_page = self.current_stat + 1
        total_pages = len(self.stat_names)
        current_name = self.stat_names[self.current_stat]
        self.page_label.config(text=f"{current_page} / {total_pages}")
        
        # Actualizar título del header
        if hasattr(self, 'section_title_label'):
            current_title = self.stat_titles[self.current_stat]
            self.section_title_label.config(text=current_title)
        
        # Habilitar/deshabilitar botones (mismo color para ambos)
        if self.current_stat == 0:
            self.prev_btn.config(state='disabled', fg='#cccccc', bg='#f0f0f0')
        else:
            self.prev_btn.config(state='normal', fg='#2E5090', bg='white')
            
        if self.current_stat == len(self.stat_names) - 1:
            self.next_btn.config(state='disabled', fg='#cccccc', bg='#f0f0f0')
        else:
            self.next_btn.config(state='normal', fg='#2E5090', bg='white')
            
    def load_current_stat(self):
        """Cargar la estadística actual"""
        # Limpiar controles de edad si existen y no estamos en la página de edades
        if hasattr(self, 'age_switch_added') and self.current_stat != 2:
            # Buscar y eliminar el interruptor del content_frame
            try:
                # Buscar el content_frame
                content_frame = self.stats_table.master.master
                
                # Buscar y eliminar el frame del interruptor
                for child in content_frame.winfo_children():
                    if isinstance(child, tk.Frame) and hasattr(child, '_age_switch'):
                        child.destroy()
                        print("[OK] Interruptor eliminado")
                delattr(self, 'age_switch_added')
            except Exception as e:
                print(f"[ERROR] Error al eliminar interruptor: {e}")
        
        if self.current_stat == 0:
            self.load_unidad_data_simple()
        elif self.current_stat == 1:
            self.load_dedo_data_simple()
        elif self.current_stat == 2:
            self.load_edad_data_simple()
        elif self.current_stat == 3:
            self.load_sexo_data_simple()
        elif self.current_stat == 4:
            self.load_dia_semana_data_simple()
        elif self.current_stat == 5:
            self.load_anios_data_simple()
        elif self.current_stat == 6:
            self.load_horarios_pico_data_simple()
        elif self.current_stat == 7:
            self.load_edad_sexo_data_simple()
        elif self.current_stat == 8:
            self.load_edad_promedio_unidad_data_simple()
        elif self.current_stat == 9:
            self.load_usuario_data_simple()
        
    def load_unidad_data_simple(self):
        """Cargar datos de distribución por unidad en tabla real"""
        try:
            print("[REFRESH] Cargando datos de unidades...")
            
            # Verificar que la tabla existe
            if not hasattr(self, 'stats_table'):
                print("[ERROR] Widget stats_table no existe")
                return
                
            # Limpiar tabla actual
            for item in self.stats_table.get_children():
                self.stats_table.delete(item)
                
            # Actualizar header de tabla para unidades
            self.stats_table.heading("unidad", text="UNIDAD DE INSCRIPCIÓN")
            self.update_idletasks()
            
            # Conectar a la base de datos
            conn = connect_db()
            if not conn:
                self.show_error_in_table("Error: No se pudo conectar a la base de datos")
                return
                
            cursor = conn.cursor()
            
            # Obtener datos de postulantes con sus unidades
            cursor.execute("""
                SELECT unidad 
                FROM postulantes 
                WHERE unidad IS NOT NULL AND unidad != ''
                ORDER BY unidad
            """)
            
            unidades_data = cursor.fetchall()
            conn.close()
            
            if not unidades_data:
                self.show_error_in_table("No se encontraron datos de unidades")
                return
                
            # Contar unidades
            unidad_count = {}
            for row in unidades_data:
                unidad = row[0]
                unidad_count[unidad] = unidad_count.get(unidad, 0) + 1
                
            # Insertar datos en la tabla ordenados por cantidad (mayor a menor)
            total = sum(unidad_count.values())
            sorted_unidades = sorted(unidad_count.items(), key=lambda x: x[1], reverse=True)
            
            for unidad, count in sorted_unidades:
                porcentaje = (count / total) * 100
                self.stats_table.insert("", "end", values=(
                    unidad,
                    formatear_numero(count),
                    formatear_porcentaje(porcentaje)
                ))
            
            print(f"[OK] Datos cargados: {total} registros procesados")
            
        except Exception as e:
            print(f"[ERROR] Error al cargar datos: {e}")
            self.show_error_in_table(f"Error al cargar datos: {str(e)}")
            
    def show_error_in_text(self, mensaje):
        """Mostrar mensaje de error en el widget de texto (deprecated)"""
        if hasattr(self, 'unidad_text'):
            self.unidad_text.config(state='normal')
            self.unidad_text.delete(1.0, tk.END)
            self.unidad_text.insert(tk.END, f"[ERROR] {mensaje}")
            self.unidad_text.config(state='disabled')
            
    def show_error_in_table(self, mensaje):
        """Mostrar mensaje de error en la tabla"""
        if hasattr(self, 'stats_table'):
            # Limpiar tabla
            for item in self.stats_table.get_children():
                self.stats_table.delete(item)
            # Insertar mensaje de error
            self.stats_table.insert("", "end", values=(f"[ERROR] {mensaje}", "", ""))
            
    def load_dedo_data_simple(self):
        """Cargar datos de distribución por dedo registrado en tabla real"""
        try:
            print("[REFRESH] Cargando datos de dedos...")
            
            if not hasattr(self, 'stats_table'):
                return
                
            # Limpiar tabla actual
            for item in self.stats_table.get_children():
                self.stats_table.delete(item)
                
            # Actualizar header de tabla para dedos
            self.stats_table.heading("unidad", text="DEDO REGISTRADO")
            self.update_idletasks()
            
            conn = connect_db()
            if not conn:
                self.show_error_in_table("Error: No se pudo conectar a la base de datos")
                return
                
            cursor = conn.cursor()
            cursor.execute("""
                SELECT dedo_registrado 
                FROM postulantes 
                WHERE dedo_registrado IS NOT NULL AND dedo_registrado != ''
                ORDER BY dedo_registrado
            """)
            
            dedos_data = cursor.fetchall()
            conn.close()
            
            if not dedos_data:
                self.show_error_in_table("No se encontraron datos de dedos registrados")
                return
                
            # Contar dedos
            dedo_count = {}
            for row in dedos_data:
                dedo = row[0]
                dedo_count[dedo] = dedo_count.get(dedo, 0) + 1
                
            # Insertar datos en la tabla ordenados por cantidad (mayor a menor)
            total = sum(dedo_count.values())
            sorted_dedos = sorted(dedo_count.items(), key=lambda x: x[1], reverse=True)
            
            for dedo, count in sorted_dedos:
                porcentaje = (count / total) * 100
                self.stats_table.insert("", "end", values=(
                    dedo,
                    formatear_numero(count),
                    formatear_porcentaje(porcentaje)
                ))
            
            print(f"[OK] Datos de dedos cargados: {total} registros")
            
        except Exception as e:
            print(f"[ERROR] Error al cargar datos de dedos: {e}")
            self.show_error_in_table(f"Error al cargar datos: {str(e)}")
            
    def load_edad_data_simple(self):
        """Cargar datos de distribución por edades en tabla real"""
        try:
            print("[REFRESH] Cargando datos de edades...")
            
            if not hasattr(self, 'stats_table'):
                return
                
            # Limpiar tabla actual
            for item in self.stats_table.get_children():
                self.stats_table.delete(item)
                
            # Actualizar header de tabla para edades
            self.stats_table.heading("unidad", text="GRUPO ETARIO")
            self.update_idletasks()
            
            # Agregar interruptor para edades individuales en la posición marcada (solo en esta página)
            if not hasattr(self, 'age_switch_added'):
                try:
                    # Buscar el content_frame para agregar el interruptor
                    content_frame = self.stats_table.master.master
                    
                    # Crear frame para el interruptor - insertarlo ANTES de la tabla
                    switch_frame = tk.Frame(content_frame, bg='white')
                    switch_frame._age_switch = True  # Marcar para identificación
                    
                    # Insertar el frame del interruptor ANTES del frame de la tabla
                    table_frame = self.stats_table.master
                    switch_frame.pack(fill='x', padx=20, pady=(5, 10), before=table_frame)
                    
                    # Crear y agregar el interruptor
                    age_switch = self.create_toggle_switch(
                        switch_frame, 
                        "Mostrar edades individuales", 
                        self.show_individual_ages, 
                        self.on_age_display_changed
                    )
                    age_switch.pack(anchor='w')  # Alinear a la izquierda
                    
                    # Marcar que ya se agregó el interruptor
                    self.age_switch_added = True
                    print("[OK] Interruptor agregado en la posición marcada")
                except Exception as e:
                    print(f"[ERROR] Error al agregar interruptor: {e}")
            
            conn = connect_db()
            if not conn:
                self.show_error_in_table("Error: No se pudo conectar a la base de datos")
                return
                
            cursor = conn.cursor()
            cursor.execute("""
                SELECT edad, fecha_nacimiento 
                FROM postulantes 
                WHERE edad IS NOT NULL OR fecha_nacimiento IS NOT NULL
            """)
            
            edad_data = cursor.fetchall()
            conn.close()
            
            if not edad_data:
                self.show_error_in_table("No se encontraron datos de edades")
                return
                
            # Procesar edades
            edades = []
            for row in edad_data:
                edad = row[0]
                fecha_nac = row[1]
                
                if edad:
                    edades.append(edad)
                elif fecha_nac:
                    from datetime import datetime
                    try:
                        edad_calc = datetime.now().year - fecha_nac.year
                        if datetime.now().date() < fecha_nac.replace(year=datetime.now().year):
                            edad_calc -= 1
                        edades.append(edad_calc)
                    except:
                        continue
                        
            if not edades:
                self.show_error_in_table("No se pudieron procesar las edades")
                return
                
            # Verificar si mostrar edades individuales o rangos
            show_individual = getattr(self, 'show_individual_ages', tk.BooleanVar(value=False)).get()
            
            if show_individual:
                # Actualizar header de tabla para edades individuales
                self.stats_table.heading("unidad", text="EDAD")
                self.update_idletasks()
                # Mostrar edades individuales
                edad_counts = {}
                for edad in edades:
                    edad_counts[edad] = edad_counts.get(edad, 0) + 1
                
                # Ordenar por edad
                sorted_ages = sorted(edad_counts.items())
                
                # Insertar datos en la tabla
                total = len(edades)
                for edad, count in sorted_ages:
                    porcentaje = (count / total) * 100
                    self.stats_table.insert("", "end", values=(
                        f"{edad} años",
                        formatear_numero(count),
                        formatear_porcentaje(porcentaje)
                    ))
                
                print(f"[OK] Datos de edades individuales cargados: {total} registros")
                return
                
            # Crear rangos dinámicos basados en la distribución real de datos
            # Actualizar header de tabla para rangos
            self.stats_table.heading("unidad", text="GRUPO ETARIO")
            self.update_idletasks()
            
            if len(edades) > 0:
                edades_sorted = sorted(edades)
                min_edad = min(edades)
                max_edad = max(edades)
                
                # Si hay pocos datos, usar rangos estándar
                if len(edades) < 10:
                    rangos = {
                        "18-25 años": 0,
                        "26-35 años": 0, 
                        "36-45 años": 0,
                        "46-55 años": 0,
                        "56+ años": 0
                    }
                    
                    for edad in edades:
                        if 18 <= edad <= 25:
                            rangos["18-25 años"] += 1
                        elif 26 <= edad <= 35:
                            rangos["26-35 años"] += 1
                        elif 36 <= edad <= 45:
                            rangos["36-45 años"] += 1
                        elif 46 <= edad <= 55:
                            rangos["46-55 años"] += 1
                        elif edad > 55:
                            rangos["56+ años"] += 1
                else:
                    # Crear rangos dinámicos usando percentiles
                    try:
                        import numpy as np
                        
                        # Calcular percentiles para crear rangos equilibrados
                        percentiles = [0, 20, 40, 60, 80, 100]
                        limites = np.percentile(edades, percentiles)
                        
                        # Crear rangos dinámicos
                        rangos = {}
                        for i in range(len(limites) - 1):
                            inicio = int(limites[i])
                            fin = int(limites[i + 1])
                            
                            if inicio == fin:
                                fin += 1
                                
                            if i == len(limites) - 2:  # Último rango
                                rango_nombre = f"{inicio}+ años"
                            else:
                                rango_nombre = f"{inicio}-{fin} años"
                            
                            rangos[rango_nombre] = 0
                        
                        # Asignar edades a rangos dinámicos
                        for edad in edades:
                            for i in range(len(limites) - 1):
                                inicio = int(limites[i])
                                fin = int(limites[i + 1])
                                
                                if inicio == fin:
                                    fin += 1
                                    
                                if i == len(limites) - 2:  # Último rango
                                    if edad >= inicio:
                                        rango_nombre = f"{inicio}+ años"
                                        rangos[rango_nombre] += 1
                                        break
                                else:
                                    if inicio <= edad <= fin:
                                        rango_nombre = f"{inicio}-{fin} años"
                                        rangos[rango_nombre] += 1
                                        break
                    except ImportError:
                        # Fallback si numpy no está disponible
                        print("[WARN] numpy no disponible, usando rangos estándar")
                        rangos = {
                            "18-25 años": 0,
                            "26-35 años": 0, 
                            "36-45 años": 0,
                            "46-55 años": 0,
                            "56+ años": 0
                        }
                        
                        for edad in edades:
                            if 18 <= edad <= 25:
                                rangos["18-25 años"] += 1
                            elif 26 <= edad <= 35:
                                rangos["26-35 años"] += 1
                            elif 36 <= edad <= 45:
                                rangos["36-45 años"] += 1
                            elif 46 <= edad <= 55:
                                rangos["46-55 años"] += 1
                            elif edad > 55:
                                rangos["56+ años"] += 1
            else:
                rangos = {"Sin datos": 0}
                    
            # Insertar datos en la tabla ordenados por cantidad (mayor a menor)
            total = sum(rangos.values())
            sorted_rangos = sorted([(rango, count) for rango, count in rangos.items() if count > 0], 
                                 key=lambda x: x[1], reverse=True)
            
            for rango, count in sorted_rangos:
                porcentaje = (count / total) * 100
                self.stats_table.insert("", "end", values=(
                    rango,
                    formatear_numero(count),
                    formatear_porcentaje(porcentaje)
                ))
            
            print(f"[OK] Datos de edades cargados: {total} registros")
            
        except Exception as e:
            print(f"[ERROR] Error al cargar datos de edades: {e}")
            self.show_error_in_table(f"Error al cargar datos: {str(e)}")
            
    def load_sexo_data_simple(self):
        """Cargar datos de distribución por sexo en tabla real"""
        try:
            print("[REFRESH] Cargando datos de sexo...")
            
            if not hasattr(self, 'stats_table'):
                return
                
            # Limpiar tabla actual
            for item in self.stats_table.get_children():
                self.stats_table.delete(item)
                
            # Actualizar header de tabla para sexo
            self.stats_table.heading("unidad", text="SEXO")
            self.update_idletasks()
            
            conn = connect_db()
            if not conn:
                self.show_error_in_table("Error: No se pudo conectar a la base de datos")
                return
                
            cursor = conn.cursor()
            
            # Consulta para obtener distribución por sexo
            cursor.execute("""
                SELECT 
                    COALESCE(sexo, 'No especificado') as sexo,
                    COUNT(*) as cantidad,
                    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM postulantes), 2) as porcentaje
                FROM postulantes 
                GROUP BY sexo 
                ORDER BY cantidad DESC
            """)
            
            sexo_data = cursor.fetchall()
            conn.close()
            
            if not sexo_data:
                self.show_error_in_table("No se encontraron datos de sexo")
                return
                
            # Insertar datos en la tabla
            for sexo, cantidad, porcentaje in sexo_data:
                self.stats_table.insert("", "end", values=(
                    sexo,
                    formatear_numero(cantidad),
                    formatear_porcentaje(porcentaje)
                ))
            
            print(f"[OK] Datos de sexo cargados: {len(sexo_data)} categorías")
            
        except Exception as e:
            print(f"[ERROR] Error al cargar datos de sexo: {e}")
            self.show_error_in_table(f"Error al cargar datos: {str(e)}")
            
    def load_dia_semana_data_simple(self):
        """Cargar datos de distribución por día de la semana"""
        try:
            print("[REFRESH] Cargando datos por día de la semana...")
            
            if not hasattr(self, 'stats_table'):
                return
                
            # Limpiar tabla actual
            for item in self.stats_table.get_children():
                self.stats_table.delete(item)
                
            # Actualizar header de tabla para días de la semana
            self.stats_table.heading("unidad", text="DÍA DE LA SEMANA")
            self.update_idletasks()
            
            conn = connect_db()
            if not conn:
                self.show_error_in_table("Error: No se pudo conectar a la base de datos")
                return
                
            cursor = conn.cursor()
            
            # Consulta para obtener distribución por día de la semana
            cursor.execute("""
                SELECT 
                    CASE EXTRACT(DOW FROM fecha_registro)
                        WHEN 0 THEN 'Domingo'
                        WHEN 1 THEN 'Lunes'
                        WHEN 2 THEN 'Martes'
                        WHEN 3 THEN 'Miércoles'
                        WHEN 4 THEN 'Jueves'
                        WHEN 5 THEN 'Viernes'
                        WHEN 6 THEN 'Sábado'
                    END as dia_semana,
                    COUNT(*) as cantidad,
                    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM postulantes), 2) as porcentaje
                FROM postulantes 
                GROUP BY EXTRACT(DOW FROM fecha_registro)
                ORDER BY EXTRACT(DOW FROM fecha_registro)
            """)
            
            dia_data = cursor.fetchall()
            conn.close()
            
            if not dia_data:
                self.show_error_in_table("No se encontraron datos por día de la semana")
                return
                
            # Insertar datos en la tabla
            for dia, cantidad, porcentaje in dia_data:
                self.stats_table.insert("", "end", values=(
                    dia,
                    formatear_numero(cantidad),
                    formatear_porcentaje(porcentaje)
                ))
            
            print(f"[OK] Datos por día de la semana cargados: {len(dia_data)} días")
            
        except Exception as e:
            print(f"[ERROR] Error al cargar datos por día de la semana: {e}")
            self.show_error_in_table(f"Error al cargar datos: {str(e)}")
            
    def load_anios_data_simple(self):
        """Cargar datos de registros por años"""
        try:
            print("[REFRESH] Cargando datos por años...")
            
            if not hasattr(self, 'stats_table'):
                return
                
            # Limpiar tabla actual
            for item in self.stats_table.get_children():
                self.stats_table.delete(item)
                
            # Actualizar header de tabla para años
            self.stats_table.heading("unidad", text="AÑO")
            self.update_idletasks()
            
            conn = connect_db()
            if not conn:
                self.show_error_in_table("Error: No se pudo conectar a la base de datos")
                return
                
            cursor = conn.cursor()
            
            # Consulta para obtener registros por años
            cursor.execute("""
                SELECT 
                    EXTRACT(YEAR FROM fecha_registro) as anio,
                    COUNT(*) as cantidad,
                    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM postulantes), 2) as porcentaje
                FROM postulantes 
                GROUP BY EXTRACT(YEAR FROM fecha_registro)
                ORDER BY anio DESC
            """)
            
            anio_data = cursor.fetchall()
            conn.close()
            
            if not anio_data:
                self.show_error_in_table("No se encontraron datos por años")
                return
                
            # Insertar datos en la tabla
            for anio, cantidad, porcentaje in anio_data:
                self.stats_table.insert("", "end", values=(
                    str(int(anio)),
                    formatear_numero(cantidad),
                    formatear_porcentaje(porcentaje)
                ))
            
            print(f"[OK] Datos por años cargados: {len(anio_data)} años")
            
        except Exception as e:
            print(f"[ERROR] Error al cargar datos por años: {e}")
            self.show_error_in_table(f"Error al cargar datos: {str(e)}")
            
    def load_horarios_pico_data_simple(self):
        """Cargar datos de horarios de pico de registro (por hora)"""
        try:
            print("[REFRESH] Cargando datos de horarios de pico...")
            
            if not hasattr(self, 'stats_table'):
                return
                
            # Limpiar tabla actual
            for item in self.stats_table.get_children():
                self.stats_table.delete(item)
                
            # Actualizar header de tabla para horarios
            self.stats_table.heading("unidad", text="HORARIO")
            self.update_idletasks()
            
            conn = connect_db()
            if not conn:
                self.show_error_in_table("Error: No se pudo conectar a la base de datos")
                return
                
            cursor = conn.cursor()
            
            # Consulta para obtener registros por hora
            cursor.execute("""
                SELECT 
                    EXTRACT(HOUR FROM fecha_registro) as hora,
                    COUNT(*) as cantidad,
                    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM postulantes), 2) as porcentaje
                FROM postulantes 
                GROUP BY EXTRACT(HOUR FROM fecha_registro)
                ORDER BY EXTRACT(HOUR FROM fecha_registro) ASC
            """)
            
            hora_data = cursor.fetchall()
            conn.close()
            
            if not hora_data:
                self.show_error_in_table("No se encontraron datos de horarios")
                return
                
            # Ordenar los datos por hora antes de insertar
            hora_data_ordenada = sorted(hora_data, key=lambda x: x[0])
            
            # Insertar datos en la tabla con formato de hora
            for hora, cantidad, porcentaje in hora_data_ordenada:
                hora_formato = f"{int(hora):02d}:00 - {int(hora):02d}:59"
                self.stats_table.insert("", "end", values=(
                    hora_formato,
                    formatear_numero(cantidad),
                    formatear_porcentaje(porcentaje)
                ))
            
            print(f"[OK] Datos de horarios de pico cargados: {len(hora_data)} horas")
            
        except Exception as e:
            print(f"[ERROR] Error al cargar datos de horarios de pico: {e}")
            self.show_error_in_table(f"Error al cargar datos: {str(e)}")
            
    def load_edad_sexo_data_simple(self):
        """Cargar datos de distribución por rango de edad y sexo"""
        try:
            print("[REFRESH] Cargando datos por rango de edad y sexo...")
            
            if not hasattr(self, 'stats_table'):
                return
                
            # Limpiar tabla actual
            for item in self.stats_table.get_children():
                self.stats_table.delete(item)
                
            # Actualizar header de tabla para edad y sexo
            self.stats_table.heading("unidad", text="RANGO ETARIO Y SEXO")
            self.update_idletasks()
            
            conn = connect_db()
            if not conn:
                self.show_error_in_table("Error: No se pudo conectar a la base de datos")
                return
                
            cursor = conn.cursor()
            
            # Consulta para obtener distribución por rango de edad y sexo
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN edad < 25 THEN '18-24 años'
                        WHEN edad < 35 THEN '25-34 años'
                        WHEN edad < 45 THEN '35-44 años'
                        WHEN edad < 55 THEN '45-54 años'
                        ELSE '55+ años'
                    END as rango_edad,
                    COALESCE(sexo, 'No especificado') as sexo,
                    COUNT(*) as cantidad,
                    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM postulantes), 2) as porcentaje
                FROM postulantes 
                GROUP BY 
                    CASE 
                        WHEN edad < 25 THEN '18-24 años'
                        WHEN edad < 35 THEN '25-34 años'
                        WHEN edad < 45 THEN '35-44 años'
                        WHEN edad < 55 THEN '45-54 años'
                        ELSE '55+ años'
                    END,
                    sexo
                ORDER BY rango_edad, sexo
            """)
            
            edad_sexo_data = cursor.fetchall()
            conn.close()
            
            if not edad_sexo_data:
                self.show_error_in_table("No se encontraron datos por rango de edad y sexo")
                return
                
            # Insertar datos en la tabla
            for rango_edad, sexo, cantidad, porcentaje in edad_sexo_data:
                self.stats_table.insert("", "end", values=(
                    f"{rango_edad} - {sexo}",
                    formatear_numero(cantidad),
                    formatear_porcentaje(porcentaje)
                ))
            
            print(f"[OK] Datos por rango de edad y sexo cargados: {len(edad_sexo_data)} combinaciones")
            
        except Exception as e:
            print(f"[ERROR] Error al cargar datos por rango de edad y sexo: {e}")
            self.show_error_in_table(f"Error al cargar datos: {str(e)}")
            
    def load_edad_promedio_unidad_data_simple(self):
        """Cargar datos de edad promedio por unidad"""
        try:
            print("[REFRESH] Cargando datos de edad promedio por unidad...")
            
            if not hasattr(self, 'stats_table'):
                return
                
            # Limpiar tabla actual
            for item in self.stats_table.get_children():
                self.stats_table.delete(item)
                
            # Actualizar headers de tabla para edad promedio
            self.stats_table.heading("unidad", text="UNIDAD")
            self.stats_table.heading("registros", text="EDAD PROMEDIO")
            self.stats_table.heading("porcentaje", text="TOTAL PERSONAS")
            self.update_idletasks()
            
            conn = connect_db()
            if not conn:
                self.show_error_in_table("Error: No se pudo conectar a la base de datos")
                return
                
            cursor = conn.cursor()
            
            # Consulta para obtener edad promedio por unidad
            cursor.execute("""
                SELECT 
                    unidad,
                    ROUND(AVG(edad), 1) as edad_promedio,
                    COUNT(*) as total_personas
                FROM postulantes 
                WHERE unidad IS NOT NULL AND unidad != ''
                GROUP BY unidad
                ORDER BY edad_promedio DESC
            """)
            
            edad_promedio_data = cursor.fetchall()
            conn.close()
            
            if not edad_promedio_data:
                self.show_error_in_table("No se encontraron datos de edad promedio por unidad")
                return
                
            # Insertar datos en la tabla
            for unidad, edad_promedio, total_personas in edad_promedio_data:
                self.stats_table.insert("", "end", values=(
                    unidad,
                    f"{formatear_numero(edad_promedio, 1)} años",
                    f"{formatear_numero(total_personas)} personas"
                ))
            
            print(f"[OK] Datos de edad promedio por unidad cargados: {len(edad_promedio_data)} unidades")
            
        except Exception as e:
            print(f"[ERROR] Error al cargar datos de edad promedio por unidad: {e}")
            self.show_error_in_table(f"Error al cargar datos: {str(e)}")
            
    def load_usuario_data_simple(self):
        """Cargar datos de top 5 usuarios más activos en tabla real"""
        try:
            print("[REFRESH] Cargando datos de usuarios...")
            
            if not hasattr(self, 'stats_table'):
                return
                
            # Limpiar tabla actual
            for item in self.stats_table.get_children():
                self.stats_table.delete(item)
                
            # Actualizar header de tabla para usuarios
            self.stats_table.heading("unidad", text="NOMBRE COMPLETO")
            self.update_idletasks()
            
            conn = connect_db()
            if not conn:
                self.show_error_in_table("Error: No se pudo conectar a la base de datos")
                return
                
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.registrado_por, COUNT(p.id) as total_registros
                FROM postulantes p
                WHERE p.registrado_por IS NOT NULL AND p.registrado_por != ''
                GROUP BY p.registrado_por
                ORDER BY total_registros DESC
            """)
            
            usuarios_data = cursor.fetchall()
            conn.close()
            
            if not usuarios_data:
                self.show_error_in_table("No se encontraron datos de usuarios")
                return
                
            # Ranking con medallas
            medallas = ["🥇", "🥈", "🥉", "🏅", "[MEDAL]"]
            total_general = sum(total for _, total in usuarios_data)
            
            # Insertar datos en la tabla sin ranking
            for registrado_por, total_registros in usuarios_data:
                porcentaje = (total_registros / total_general) * 100
                
                self.stats_table.insert("", "end", values=(
                    registrado_por,
                    formatear_numero(total_registros),
                    formatear_porcentaje(porcentaje)
                ))
            
            print(f"[OK] Datos de usuarios cargados: {len(usuarios_data)} usuarios")
            
        except Exception as e:
            print(f"[ERROR] Error al cargar datos de usuarios: {e}")
            self.show_error_in_table(f"Error al cargar datos: {str(e)}")
        
    def create_premium_card_vertical(self, parent, title, subtitle, content_creator, section_id, expanded=False):
        """Crear una card premium moderna en layout vertical"""
        # Card principal con márgenes apropiados
        card_frame = tk.Frame(parent, bg='#ffffff', relief='flat', bd=0)
        card_frame.pack(fill='x', padx=0, pady=10)
        
        # Borde elegante
        border_frame = tk.Frame(card_frame, bg='#e2e8f0', height=1)
        border_frame.pack(fill='x', side='bottom')
        
        # Header de la card
        header_frame = tk.Frame(card_frame, bg='#ffffff')
        header_frame.pack(fill='x', padx=25, pady=(20, 15))
        
        # Container para título y botón
        title_container = tk.Frame(header_frame, bg='#ffffff')
        title_container.pack(fill='x')
        
        # Título principal de la card (lado izquierdo)
        title_label = tk.Label(title_container, 
                              text=title, 
                              font=('Segoe UI', 16, 'bold'), 
                              fg='#1a365d', 
                              bg='#ffffff')
        title_label.pack(side='left', anchor='w')
        
        # Botón toggle moderno (lado derecho)
        toggle_btn = tk.Button(title_container, 
                              text="▼ Ver detalles", 
                              font=('Segoe UI', 10, 'bold'), 
                              fg='#4299e1', 
                              bg='#ffffff', 
                              bd=0, 
                              relief='flat',
                              cursor='hand2',
                              activeforeground='#2b6cb0',
                              activebackground='#f7fafc')
        toggle_btn.pack(side='right', anchor='e')
        
        # Subtítulo descriptivo
        subtitle_label = tk.Label(header_frame, 
                                 text=subtitle, 
                                 font=('Segoe UI', 11), 
                                 fg='#718096', 
                                 bg='#ffffff')
        subtitle_label.pack(anchor='w', pady=(5, 0))
        
        # Contenedor para el contenido (inicialmente oculto)
        content_container = tk.Frame(card_frame, bg='#ffffff')
        
        # Crear el contenido usando el content_creator
        content_frame = content_creator(content_container)
        
        # Configurar el toggle - usar el parámetro expanded
        
        def toggle_content():
            nonlocal expanded
            if expanded:
                # Contraer
                content_container.pack_forget()
                toggle_btn.config(text="▼ Ver detalles", fg='#4299e1')
                expanded = False
            else:
                # Expandir
                content_container.pack(fill='both', expand=True, padx=25, pady=(0, 20))
                toggle_btn.config(text="▲ Ocultar detalles", fg='#e53e3e')
                expanded = True
                
        toggle_btn.config(command=toggle_content)
        
        # Si debe estar expandido inicialmente, expandir ahora
        if expanded:
            content_container.pack(fill='both', expand=True, padx=25, pady=(0, 20))
            toggle_btn.config(text="▲ Ocultar detalles", fg='#e53e3e')
        
        # Hover effects para toda la card
        def on_enter(e):
            card_frame.config(bg='#f7fafc')
            header_frame.config(bg='#f7fafc')
            title_container.config(bg='#f7fafc')
            content_container.config(bg='#f7fafc')
            
        def on_leave(e):
            card_frame.config(bg='#ffffff')
            header_frame.config(bg='#ffffff')
            title_container.config(bg='#f7fafc')
            content_container.config(bg='#ffffff')
            
        # Aplicar hover a toda la card
        for widget in [card_frame, header_frame, title_container, title_label, subtitle_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
        
        # Almacenar referencias para actualizaciones
        if not hasattr(self, 'premium_cards'):
            self.premium_cards = {}
        self.premium_cards[section_id] = {
            'content_frame': content_frame,
            'toggle_btn': toggle_btn,
            'expanded': expanded
        }
        
        return card_frame
        
    def create_premium_card(self, parent, title, subtitle, content_creator, section_id, row, col):
        """Crear una card premium moderna"""
        # Card principal con sombra
        card_frame = tk.Frame(parent, bg='#ffffff', relief='flat', bd=0)
        card_frame.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')
        
        # Efecto de sombra (simulado con frames)
        shadow_frame = tk.Frame(card_frame, bg='#e2e8f0', height=2)
        shadow_frame.pack(side='bottom', fill='x')
        
        # Header de la card
        header_frame = tk.Frame(card_frame, bg='#ffffff', height=80)
        header_frame.pack(fill='x', padx=20, pady=(20, 0))
        header_frame.pack_propagate(False)
        
        # Título principal de la card
        title_label = tk.Label(header_frame, 
                              text=title, 
                              font=('Segoe UI', 16, 'bold'), 
                              fg='#2d3748', 
                              bg='#ffffff')
        title_label.pack(anchor='w', pady=(15, 2))
        
        # Subtítulo descriptivo
        subtitle_label = tk.Label(header_frame, 
                                 text=subtitle, 
                                 font=('Segoe UI', 10), 
                                 fg='#718096', 
                                 bg='#ffffff')
        subtitle_label.pack(anchor='w')
        
        # Línea separadora elegante
        separator = tk.Frame(card_frame, bg='#e2e8f0', height=1)
        separator.pack(fill='x', padx=20, pady=(10, 0))
        
        # Botón toggle moderno
        toggle_frame = tk.Frame(card_frame, bg='#ffffff')
        toggle_frame.pack(fill='x', padx=20, pady=10)
        
        toggle_btn = tk.Button(toggle_frame, 
                              text="▼ Ver detalles", 
                              font=('Segoe UI', 10, 'bold'), 
                              fg='#4299e1', 
                              bg='#ffffff', 
                              bd=0, 
                              relief='flat',
                              cursor='hand2',
                              activeforeground='#2b6cb0',
                              activebackground='#f7fafc')
        toggle_btn.pack(anchor='w')
        
        # Contenedor para el contenido (inicialmente oculto)
        content_container = tk.Frame(card_frame, bg='#ffffff')
        
        # Crear el contenido usando el content_creator
        content_frame = content_creator(content_container)
        
        # Configurar el toggle
        expanded = False
        
        def toggle_content():
            nonlocal expanded
            if expanded:
                # Contraer
                content_container.pack_forget()
                toggle_btn.config(text="▼ Ver detalles", fg='#4299e1')
                expanded = False
            else:
                # Expandir
                content_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
                toggle_btn.config(text="▲ Ocultar detalles", fg='#e53e3e')
                expanded = True
                
        toggle_btn.config(command=toggle_content)
        
        # Hover effects
        def on_enter(e):
            card_frame.config(bg='#f7fafc')
            header_frame.config(bg='#f7fafc')
            toggle_frame.config(bg='#f7fafc')
            content_container.config(bg='#f7fafc')
            
        def on_leave(e):
            card_frame.config(bg='#ffffff')
            header_frame.config(bg='#ffffff')
            toggle_frame.config(bg='#ffffff')
            content_container.config(bg='#ffffff')
            
        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
        
        # Almacenar referencias para actualizaciones
        if not hasattr(self, 'premium_cards'):
            self.premium_cards = {}
        self.premium_cards[section_id] = {
            'content_frame': content_frame,
            'toggle_btn': toggle_btn,
            'expanded': expanded
        }
        
        return card_frame
        
    def create_modern_section(self, parent, title, content_creator, section_id, expanded=False, color="#4a90e2"):
        """Crear una sección moderna con diseño atractivo"""
        # Frame principal
        section_frame = tk.Frame(parent, bg='white', relief='flat', bd=0)
        section_frame.pack(fill='x', pady=(0, 15))
        
        # Frame interno con borde
        inner_frame = tk.Frame(section_frame, bg='white', relief='solid', bd=1)
        inner_frame.pack(fill='x', padx=2, pady=2)
        
        # Frame del header clickeable
        header_frame = tk.Frame(inner_frame, bg=color, cursor='hand2')
        header_frame.pack(fill='x')
        
        # Título de la sección
        title_label = tk.Label(header_frame, text=title, 
                              font=('Segoe UI', 12, 'bold'), 
                              fg='white', bg=color, cursor='hand2')
        title_label.pack(side='left', padx=15, pady=12)
        
        # Botón expandir/contraer
        expand_btn = tk.Label(header_frame, text="▼", 
                             font=('Segoe UI', 12, 'bold'),
                             fg='white', bg=color, cursor='hand2')
        expand_btn.pack(side='right', padx=15, pady=12)
        
        # Frame para el contenido
        content_frame = tk.Frame(inner_frame, bg='white')
        
        # Crear el contenido específico
        content_creator(content_frame)
        
        # Configurar estado inicial
        if expanded:
            content_frame.pack(fill='x', padx=15, pady=15)
            expand_btn.config(text="▲")
        
        # Hacer que toda la barra sea clickeable
        def toggle_section_click(event):
            self.toggle_modern_section(section_id, content_frame, expand_btn)
        
        header_frame.bind("<Button-1>", toggle_section_click)
        title_label.bind("<Button-1>", toggle_section_click)
        expand_btn.bind("<Button-1>", toggle_section_click)
        
        # Guardar referencias para el toggle
        if not hasattr(self, 'expandable_sections'):
            self.expandable_sections = {}
        self.expandable_sections[section_id] = {
            'content_frame': content_frame,
            'expand_btn': expand_btn,
            'expanded': expanded
        }
        
    def toggle_modern_section(self, section_id, content_frame, expand_btn):
        """Expandir o contraer una sección moderna"""
        section = self.expandable_sections[section_id]
        
        if section['expanded']:
            # Contraer
            content_frame.pack_forget()
            expand_btn.config(text="▼")
            section['expanded'] = False
        else:
            # Expandir
            content_frame.pack(fill='x', padx=15, pady=15)
            expand_btn.config(text="▲")
            section['expanded'] = True
            
        # Forzar actualización visual simple
        self.update_idletasks()
            
    def create_unidad_content(self, parent):
        """Crear contenido para distribución por unidad"""
        content_frame = tk.Frame(parent, bg='#ffffff')
        
        # Texto estilizado para cards
        self.unidad_text = tk.Text(content_frame, 
                                  height=6, 
                                  font=('Segoe UI', 10), 
                                  bg='#f8fafc', 
                                  fg='#2d3748',
                                  wrap=tk.WORD, 
                                  state='disabled',
                                  relief='flat',
                                  bd=0,
                                  padx=15,
                                  pady=10)
        self.unidad_text.pack(fill='both', expand=True)
        
        return content_frame
        
    def create_dedo_content(self, parent):
        """Crear contenido para distribución por dedo"""
        content_frame = tk.Frame(parent, bg='#ffffff')
        
        # Texto estilizado para cards
        self.dedos_text = tk.Text(content_frame, 
                                 height=6, 
                                 font=('Segoe UI', 10), 
                                 bg='#f8fafc', 
                                 fg='#2d3748',
                                 wrap=tk.WORD, 
                                 state='disabled',
                                 relief='flat',
                                 bd=0,
                                 padx=15,
                                 pady=10)
        self.dedos_text.pack(fill='both', expand=True)
        
        return content_frame
        
    def create_edad_content(self, parent):
        """Crear contenido para distribución por edad"""
        content_frame = tk.Frame(parent, bg='#ffffff')
        
        # Texto estilizado para cards
        self.age_distribution_text = tk.Text(content_frame, 
                                            height=6, 
                                            font=('Segoe UI', 10), 
                                            bg='#f8fafc', 
                                            fg='#2d3748',
                                            wrap=tk.WORD, 
                                            state='disabled',
                                            relief='flat',
                                            bd=0,
                                            padx=15,
                                            pady=10)
        self.age_distribution_text.pack(fill='both', expand=True)
        
        return content_frame
        
    def create_usuario_content(self, parent):
        """Crear contenido para registros por usuario"""
        content_frame = tk.Frame(parent, bg='#ffffff')
        
        # Texto estilizado para cards
        self.usuario_text = tk.Text(content_frame, 
                                   height=6, 
                                   font=('Segoe UI', 10), 
                                   bg='#f8fafc', 
                                   fg='#2d3748',
                                   wrap=tk.WORD, 
                                   state='disabled',
                                   relief='flat',
                                   bd=0,
                                   padx=15,
                                   pady=10)
        self.usuario_text.pack(fill='both', expand=True)
        
        return content_frame
        
    def create_hourly_tab(self, parent):
        """Crear pestaña de registros por hora"""
        # Frame principal
        main_frame = tk.Frame(parent, bg='white', padx=15, pady=15)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title = tk.Label(main_frame, text="Registros por Turnos de Trabajo", 
                        font=('Segoe UI', 12, 'bold'), 
                        fg='#2c3e50', bg='white')
        title.pack(anchor='w', pady=(0, 12))
        
        # Frame de controles
        controls_frame = tk.Frame(main_frame, bg='white')
        controls_frame.pack(fill='x', pady=(0, 12))
        
        # Selector de fecha
        tk.Label(controls_frame, text="Fecha:", 
                font=('Segoe UI', 9), 
                fg='#2c3e50', bg='white').pack(side='left')
        
        self.hourly_date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        date_entry = tk.Entry(controls_frame, textvariable=self.hourly_date_var, 
                             font=('Segoe UI', 9), width=12,
                             relief='solid', bd=1)
        date_entry.pack(side='left', padx=(10, 20))
        
        # Configuración de rango horario
        tk.Label(controls_frame, text="Rango horario:", 
                font=('Segoe UI', 9), 
                fg='#2c3e50', bg='white').pack(side='left')
        
        # Hora inicio
        self.rango_inicio_var = tk.StringVar(value="07:00")
        rango_inicio = tk.Entry(controls_frame, textvariable=self.rango_inicio_var, 
                               font=('Segoe UI', 9), width=6,
                               relief='solid', bd=1)
        rango_inicio.pack(side='left', padx=(5, 0))
        
        tk.Label(controls_frame, text="a", 
                font=('Segoe UI', 9), 
                fg='#2c3e50', bg='white').pack(side='left', padx=2)
        
        # Hora fin
        self.rango_fin_var = tk.StringVar(value="12:00")
        rango_fin = tk.Entry(controls_frame, textvariable=self.rango_fin_var, 
                            font=('Segoe UI', 9), width=6,
                            relief='solid', bd=1)
        rango_fin.pack(side='left', padx=(0, 20))
        
        # Botón actualizar
        update_btn = tk.Button(controls_frame, text="Actualizar", 
                              command=self.update_hourly_stats,
                              font=('Segoe UI', 9),
                              fg='white', bg='#3498db',
                              relief='flat', bd=0,
                              padx=15, pady=5,
                              cursor='hand2')
        update_btn.pack(side='left', padx=(0, 10))
        
        # Botón restaurar rango por defecto
        default_btn = tk.Button(controls_frame, text="Rango por Defecto", 
                               command=self.restore_default_hours,
                               font=('Segoe UI', 9),
                               fg='white', bg='#95a5a6',
                               relief='flat', bd=0,
                               padx=10, pady=5,
                               cursor='hand2')
        default_btn.pack(side='left')
        
        # Variables para el rango (ocultas, solo para cálculos internos)
        self.rango_count_var = tk.StringVar(value="0")
        self.total_dia_var = tk.StringVar(value="0")
        
        # Frame para resumen principal (tarjeta)
        summary_card_frame = tk.Frame(main_frame, bg='#e8f5e8', relief='solid', bd=2)
        summary_card_frame.pack(fill='x', pady=(0, 15))
        
        # Título de la tarjeta
        card_title = tk.Label(summary_card_frame, text="RESUMEN", 
                             font=('Segoe UI', 14, 'bold'), 
                             fg='#27ae60', bg='#e8f5e8')
        card_title.pack(pady=(15, 10))
        
        # Variable para el resumen
        self.summary_text_var = tk.StringVar(value="Seleccione fecha y rango horario y haga clic en 'Actualizar'")
        
        # Texto del resumen
        summary_text = tk.Label(summary_card_frame, textvariable=self.summary_text_var,
                               font=('Segoe UI', 12), 
                               fg='#2c3e50', bg='#e8f5e8',
                               wraplength=600, justify='center')
        summary_text.pack(pady=(0, 15))
        
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.update_idletasks()
        
        # Asegurar un tamaño mínimo para mostrar todo el contenido
        min_width = 1000
        min_height = 700
        
        width = max(self.winfo_width(), min_width)
        height = max(self.winfo_height(), min_height)
        
        # Centrar en la pantalla
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        
        # Asegurar que la ventana no se salga de la pantalla
        x = max(0, x)
        y = max(0, y)
        
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def update_hourly_stats(self):
        """Actualizar estadísticas por hora"""
        try:
            # Obtener fecha seleccionada
            fecha_texto = self.hourly_date_var.get().strip()
            
            if not fecha_texto:
                # Si no hay fecha, usar hoy
                fecha = datetime.now().date()
            else:
                # Validar formato de fecha
                try:
                    fecha = datetime.strptime(fecha_texto, "%d/%m/%Y").date()
                except ValueError:
                    messagebox.showerror("Error", "Formato de fecha incorrecto. Use DD/MM/AAAA")
                    return
                
            # Obtener horario configurado
            try:
                # Parsear horarios del rango
                rango_inicio = datetime.strptime(self.rango_inicio_var.get(), "%H:%M").time()
                rango_fin = datetime.strptime(self.rango_fin_var.get(), "%H:%M").time()
                
            except ValueError:
                messagebox.showerror("Error", "Formato de hora incorrecto. Use HH:MM (ej: 07:00)")
                return
            
            # Obtener datos de la base de datos
            conn = connect_db()
            if not conn:
                return
                
            cursor = conn.cursor()
            
            # Consulta para obtener registros por hora del día seleccionado
            cursor.execute("""
                SELECT 
                    EXTRACT(HOUR FROM fecha_registro) as hora,
                    EXTRACT(MINUTE FROM fecha_registro) as minuto,
                    COUNT(*) as cantidad
                FROM postulantes 
                WHERE DATE(fecha_registro) = %s
                GROUP BY EXTRACT(HOUR FROM fecha_registro), EXTRACT(MINUTE FROM fecha_registro)
                ORDER BY hora, minuto
            """, (fecha,))
            
            registros_por_hora = cursor.fetchall()
            
            # Calcular totales por rango
            rango_count = 0
            
            # Crear diccionario para facilitar el conteo
            hora_counts = {}
            for hora, minuto, cantidad in registros_por_hora:
                hora_int = int(hora)
                minuto_int = int(minuto)
                
                # Crear tiempo para comparación
                tiempo_registro = datetime.strptime(f"{hora_int:02d}:{minuto_int:02d}", "%H:%M").time()
                
                # Acumular por hora para el diccionario
                if hora_int not in hora_counts:
                    hora_counts[hora_int] = 0
                hora_counts[hora_int] += cantidad
                
                # Asignar al rango según horario configurado
                if rango_inicio <= tiempo_registro <= rango_fin:
                    rango_count += cantidad
            
            # Actualizar variables
            self.rango_count_var.set(str(rango_count))
            self.total_dia_var.set(str(rango_count))
            
            # Actualizar tarjeta de resumen
            fecha_str = fecha.strftime('%d/%m/%Y')
            summary_message = f"Usuarios registrados en fecha {fecha_str}\nentre las {rango_inicio.strftime('%H:%M')} y las {rango_fin.strftime('%H:%M')}\n\nTotal: {rango_count} registros"
            self.summary_text_var.set(summary_message)
            
            conn.close()
            
        except Exception as e:
            print(f"Error al actualizar estadísticas por hora: {e}")
            messagebox.showerror("Error", f"Error al actualizar estadísticas por hora: {e}")
            
    def restore_default_hours(self):
        """Restaurar rango horario por defecto"""
        self.rango_inicio_var.set("07:00")
        self.rango_fin_var.set("12:00")
        
        # Actualizar automáticamente las estadísticas
        self.update_hourly_stats()
        

        
    def load_statistics(self):
        """Cargar todas las estadísticas"""
        try:
            print("[REFRESH] Cargando estadísticas...")
            
            # Verificar privilegios para estadísticas
            from privilegios_utils import puede_ver_estadisticas_completas, verificar_permiso
            
            # Cargar métricas principales
            self.load_main_metrics()
            
            # Cargar estadísticas detalladas solo si tiene permisos
            if puede_ver_estadisticas_completas(self.user_data) or verificar_permiso(self.user_data, 'estadisticas_basicas', mostrar_error=False):
                self.load_detailed_stats()
                print("[OK] Estadísticas cargadas correctamente")
            else:
                # Mostrar mensaje de acceso restringido
                messagebox.showwarning("Acceso Restringido", 
                                     "No tiene permisos para ver estadísticas detalladas.\n"
                                     "Contacte al administrador del sistema.")
                self.destroy()
            
        except Exception as e:
            print(f"[ERROR] Error al cargar estadísticas: {e}")
            messagebox.showerror("Error", f"Error al cargar estadísticas: {e}")
            
    def load_main_metrics(self):
        """Cargar métricas principales"""
        try:
            conn = connect_db()
            if not conn:
                print("[ERROR] No se pudo conectar a la base de datos")
                return
                
            cursor = conn.cursor()
            
            # Total de postulantes
            cursor.execute("SELECT COUNT(*) FROM postulantes")
            total_postulantes = cursor.fetchone()[0]
            
            # Total de usuarios
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            total_usuarios = cursor.fetchone()[0]
            
            # Postulantes de hoy
            hoy = datetime.now().date()
            cursor.execute("SELECT COUNT(*) FROM postulantes WHERE DATE(fecha_registro) = %s", (hoy,))
            postulantes_hoy = cursor.fetchone()[0]
            
            # Postulantes de esta semana
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            cursor.execute("SELECT COUNT(*) FROM postulantes WHERE DATE(fecha_registro) >= %s", (inicio_semana,))
            postulantes_semana = cursor.fetchone()[0]
            
            # Postulantes de este mes
            inicio_mes = hoy.replace(day=1)
            cursor.execute("SELECT COUNT(*) FROM postulantes WHERE DATE(fecha_registro) >= %s", (inicio_mes,))
            postulantes_mes = cursor.fetchone()[0]
            
            # Actualizar variables INMEDIATAMENTE
            self.total_postulantes_var.set(str(total_postulantes))
            self.total_usuarios_var.set(str(total_usuarios))
            self.postulantes_hoy_var.set(str(postulantes_hoy))
            self.postulantes_semana_var.set(str(postulantes_semana))
            self.postulantes_mes_var.set(str(postulantes_mes))
            
            # Forzar actualización visual
            self.update_idletasks()
            
            conn.close()
            print(f"[OK] Métricas cargadas: {total_postulantes} postulantes, {total_usuarios} usuarios")
            
        except Exception as e:
            print(f"[ERROR] Error al cargar métricas principales: {e}")
            
    def load_detailed_stats(self):
        """Cargar estadísticas detalladas"""
        try:
            conn = connect_db()
            if not conn:
                return
                
            cursor = conn.cursor()
            
            # Obtener todos los postulantes
            cursor.execute("""
                SELECT fecha_nacimiento, fecha_registro, edad, dedo_registrado, unidad 
                FROM postulantes 
                ORDER BY fecha_registro DESC
            """)
            postulantes = cursor.fetchall()
            
            if not postulantes:
                print("[INFO] No hay postulantes en la base de datos")
                return
                
            # Calcular estadísticas de edad
            edades = []
            for p in postulantes:
                if p[2]:  # edad
                    edades.append(p[2])
                elif p[0]:  # fecha_nacimiento
                    try:
                        edad = datetime.now().year - p[0].year
                        if datetime.now().date() < p[0].replace(year=datetime.now().year):
                            edad -= 1
                        edades.append(edad)
                    except:
                        continue
                    
            if edades:
                promedio_edad = sum(edades) / len(edades)
                edad_minima = min(edades)
                edad_maxima = max(edades)
                
                self.stats_vars['promedio_edad'].set(f"{promedio_edad:.1f} años")
                self.stats_vars['edad_minima'].set(f"{edad_minima} años")
                self.stats_vars['edad_maxima'].set(f"{edad_maxima} años")
                
            # Fechas de registro
            fechas_registro = [p[1] for p in postulantes if p[1]]
            if fechas_registro:
                ultimo = max(fechas_registro)
                primer = min(fechas_registro)
                
                self.stats_vars['ultimo_registro'].set(ultimo.strftime('%d/%m/%Y %H:%M'))
                self.stats_vars['primer_registro'].set(primer.strftime('%d/%m/%Y %H:%M'))
                
            # Total de unidades únicas
            unidades = set(p[4] for p in postulantes if p[4])
            self.stats_vars['total_unidades'].set(str(len(unidades)))
            
            # Cargar la estadística inicial (primera página)
            self.after(100, lambda: self.load_current_stat())
            
            # Forzar actualización visual
            self.update_idletasks()
            
            conn.close()
            print(f"[OK] Estadísticas detalladas cargadas: {len(postulantes)} registros procesados")
            
        except Exception as e:
            print(f"[ERROR] Error al cargar estadísticas detalladas: {e}")
            
    def update_unidad_distribution(self, postulantes):
        """Actualizar distribución por unidad de inscripción"""
        try:
            print(f"[SEARCH] Intentando actualizar unidad_text...")
            if not hasattr(self, 'unidad_text'):
                print("[ERROR] Widget unidad_text no existe aún")
                return
            print(f"[OK] Widget unidad_text encontrado")
                
            # Contar unidades
            unidad_count = {}
            for p in postulantes:
                unidad = p[4]  # unidad
                if unidad:
                    unidad_count[unidad] = unidad_count.get(unidad, 0) + 1
                    
            # Mostrar distribución
            self.unidad_text.config(state='normal')
            self.unidad_text.delete(1.0, tk.END)
            if unidad_count:
                self.unidad_text.insert(tk.END, "DISTRIBUCIÓN POR UNIDAD DE INSCRIPCIÓN\n")
                self.unidad_text.insert(tk.END, "=" * 45 + "\n\n")
                
                total = sum(unidad_count.values())
                for unidad, count in sorted(unidad_count.items()):
                    porcentaje = (count / total) * 100
                    self.unidad_text.insert(tk.END, f"{unidad:<20} {formatear_numero(count):>8} ({formatear_porcentaje(porcentaje):>6})\n")
                    
                self.unidad_text.insert(tk.END, f"\nTotal: {total} registros\n")
            else:
                self.unidad_text.insert(tk.END, "No hay datos de unidades disponibles")
            self.unidad_text.config(state='disabled')
            
            # Forzar actualización visual
            self.unidad_text.update_idletasks()
            print("[OK] Distribución por unidad cargada")
                
        except Exception as e:
            print(f"[ERROR] Error al actualizar distribución de unidades: {e}")
            
    def update_dedos_distribution(self, postulantes):
        """Actualizar distribución por dedos registrados"""
        try:
            if not hasattr(self, 'dedos_text'):
                print("Widget dedos_text no existe aún")
                return
                
            # Contar dedos
            dedos_count = {}
            for p in postulantes:
                dedo = p[3]  # dedo_registrado
                if dedo:
                    dedos_count[dedo] = dedos_count.get(dedo, 0) + 1
                    
            # Mostrar distribución
            self.dedos_text.config(state='normal')
            self.dedos_text.delete(1.0, tk.END)
            if dedos_count:
                self.dedos_text.insert(tk.END, "DISTRIBUCIÓN POR DEDO REGISTRADO\n")
                self.dedos_text.insert(tk.END, "=" * 40 + "\n\n")
                
                total = sum(dedos_count.values())
                for dedo, count in sorted(dedos_count.items()):
                    porcentaje = (count / total) * 100
                    self.dedos_text.insert(tk.END, f"{dedo:<10} {formatear_numero(count):>8} ({formatear_porcentaje(porcentaje):>6})\n")
                    
                self.dedos_text.insert(tk.END, f"\nTotal: {total} registros\n")
            else:
                self.dedos_text.insert(tk.END, "No hay datos de dedos registrados")
            self.dedos_text.config(state='disabled')
            
            # Forzar actualización visual
            self.dedos_text.update_idletasks()
            print("[OK] Distribución por dedo cargada")
                
        except Exception as e:
            print(f"[ERROR] Error al actualizar distribución de dedos: {e}")
            
    def update_age_distribution(self, edades):
        """Actualizar distribución por edad"""
        try:
            if not hasattr(self, 'age_distribution_text'):
                print("Widget age_distribution_text no existe aún")
                return
                
            if not edades:
                self.age_distribution_text.config(state='normal')
                self.age_distribution_text.delete(1.0, tk.END)
                self.age_distribution_text.insert(tk.END, "No hay datos de edad disponibles")
                self.age_distribution_text.config(state='disabled')
                return
                
            # Crear rangos dinámicos basados en la distribución real de datos
            if len(edades) > 0:
                edades_sorted = sorted(edades)
                min_edad = min(edades)
                max_edad = max(edades)
                
                # Si hay pocos datos, usar rangos estándar
                if len(edades) < 10:
                    rangos = {
                        "18-25": 0,
                        "26-35": 0,
                        "36-45": 0,
                        "46-55": 0,
                        "56-65": 0,
                        "65+": 0
                    }
                    
                    for edad in edades:
                        if 18 <= edad <= 25:
                            rangos["18-25"] += 1
                        elif 26 <= edad <= 35:
                            rangos["26-35"] += 1
                        elif 36 <= edad <= 45:
                            rangos["36-45"] += 1
                        elif 46 <= edad <= 55:
                            rangos["46-55"] += 1
                        elif 56 <= edad <= 65:
                            rangos["56-65"] += 1
                        else:
                            rangos["65+"] += 1
                else:
                    # Crear rangos dinámicos usando percentiles
                    try:
                        import numpy as np
                        
                        # Calcular percentiles para crear rangos equilibrados
                        percentiles = [0, 20, 40, 60, 80, 100]
                        limites = np.percentile(edades, percentiles)
                        
                    except ImportError:
                        # Fallback si numpy no está disponible
                        print("[WARN] numpy no disponible, usando rangos estándar")
                        rangos = {
                            "18-25": 0,
                            "26-35": 0,
                            "36-45": 0,
                            "46-55": 0,
                            "56-65": 0,
                            "65+": 0
                        }
                        
                        for edad in edades:
                            if 18 <= edad <= 25:
                                rangos["18-25"] += 1
                            elif 26 <= edad <= 35:
                                rangos["26-35"] += 1
                            elif 36 <= edad <= 45:
                                rangos["36-45"] += 1
                            elif 46 <= edad <= 55:
                                rangos["46-55"] += 1
                            elif 56 <= edad <= 65:
                                rangos["56-65"] += 1
                            else:
                                rangos["65+"] += 1
                    
                    # Crear rangos dinámicos
                    rangos = {}
                    for i in range(len(limites) - 1):
                        inicio = int(limites[i])
                        fin = int(limites[i + 1])
                        
                        if inicio == fin:
                            fin += 1
                            
                        if i == len(limites) - 2:  # Último rango
                            rango_nombre = f"{inicio}+"
                        else:
                            rango_nombre = f"{inicio}-{fin}"
                        
                        rangos[rango_nombre] = 0
                    
                    # Asignar edades a rangos dinámicos
                    for edad in edades:
                        for i in range(len(limites) - 1):
                            inicio = int(limites[i])
                            fin = int(limites[i + 1])
                            
                            if inicio == fin:
                                fin += 1
                                
                            if i == len(limites) - 2:  # Último rango
                                if edad >= inicio:
                                    rango_nombre = f"{inicio}+"
                                    rangos[rango_nombre] += 1
                                    break
                            else:
                                if inicio <= edad <= fin:
                                    rango_nombre = f"{inicio}-{fin}"
                                    rangos[rango_nombre] += 1
                                    break
            else:
                rangos = {"Sin datos": 0}
                    
            # Mostrar distribución
            self.age_distribution_text.config(state='normal')
            self.age_distribution_text.delete(1.0, tk.END)
            self.age_distribution_text.insert(tk.END, "DISTRIBUCIÓN DE EDADES\n")
            self.age_distribution_text.insert(tk.END, "=" * 30 + "\n\n")
            
            total = len(edades)
            for rango, count in rangos.items():
                if count > 0:
                    porcentaje = (count / total) * 100
                    self.age_distribution_text.insert(tk.END, f"{rango:<8} {formatear_numero(count):>8} ({formatear_porcentaje(porcentaje):>6})\n")
                    
            self.age_distribution_text.insert(tk.END, f"\nTotal: {total} registros\n")
            self.age_distribution_text.insert(tk.END, f"Promedio: {sum(edades)/len(edades):.1f} años\n")
            self.age_distribution_text.config(state='disabled')
            
            # Forzar actualización visual
            self.age_distribution_text.update_idletasks()
            print("[OK] Distribución por edad cargada")
            
        except Exception as e:
            print(f"[ERROR] Error al actualizar distribución de edad: {e}")
            
    def update_usuario_distribution(self):
        """Actualizar distribución por registros de usuario"""
        try:
            if not hasattr(self, 'usuario_text'):
                print("Widget usuario_text no existe aún")
                return
                
            # Obtener datos de la base de datos
            conn = connect_db()
            if not conn:
                return
                
            cursor = conn.cursor()
            
            # Consulta para obtener todos los usuarios que han registrado postulantes
            cursor.execute("""
                SELECT 
                    p.registrado_por,
                    COUNT(p.id) as total_registros
                FROM postulantes p
                WHERE p.registrado_por IS NOT NULL AND p.registrado_por != ''
                GROUP BY p.registrado_por
                ORDER BY total_registros DESC
            """)
            
            usuarios_data = cursor.fetchall()
            
            # Mostrar distribución
            self.usuario_text.config(state='normal')
            self.usuario_text.delete(1.0, tk.END)
            if usuarios_data:
                self.usuario_text.insert(tk.END, "TODOS LOS USUARIOS CON REGISTROS\n")
                self.usuario_text.insert(tk.END, "=" * 45 + "\n\n")
                
                # Calcular el total de registros para porcentajes
                total_registros = sum(row[1] for row in usuarios_data)
                
                for i, (registrado_por, registros) in enumerate(usuarios_data, 1):
                    if registros > 0 and total_registros > 0:
                        porcentaje = (registros / total_registros) * 100
                        self.usuario_text.insert(tk.END, f"{i:2d}. {registrado_por:<25} {formatear_numero(registros):>8} ({formatear_porcentaje(porcentaje):>6})\n")
                    else:
                        self.usuario_text.insert(tk.END, f"{i:2d}. {registrado_por:<25} {formatear_numero(registros):>8} (0,0%)\n")
                
                self.usuario_text.insert(tk.END, f"\nTotal de registros: {total_registros}\n")
            else:
                self.usuario_text.insert(tk.END, "No hay datos de usuarios disponibles")
            self.usuario_text.config(state='disabled')
            
            # Forzar actualización visual
            self.usuario_text.update_idletasks()
            print("[OK] Distribución por usuario cargada")
                
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Error al actualizar distribución de usuarios: {e}")
            if hasattr(self, 'usuario_text'):
                self.usuario_text.config(state='normal')
                self.usuario_text.delete(1.0, tk.END)
                self.usuario_text.insert(tk.END, f"Error al cargar datos: {e}")
                self.usuario_text.config(state='disabled')
    


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
    
    app = Estadisticas(root, user_data)
    root.mainloop()

if __name__ == "__main__":
    main() 
