#!/usr/bin/env python3
"""
Módulo de estadísticas del sistema - Versión mejorada
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db
from datetime import datetime, timedelta
import ctypes

# Configurar DPI para Windows (HD/4K)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Per Monitor DPI Aware
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()  # Fallback para versiones anteriores
    except:
        pass

class Estadisticas(tk.Toplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.parent = parent
        self.user_data = user_data
        
        self.title("Estadísticas del Sistema")
        self.geometry('')
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        # Configurar estilo consistente con el resto del sistema
        self.configure(bg='#f8f9fa')
        
        self.setup_ui()
        self.center_window()
        
        # Cargar estadísticas después de que la interfaz esté completamente creada
        self.after(500, self.load_statistics)
        
    def setup_ui(self):
        """Configurar la interfaz principal"""
        # Frame principal con padding optimizado para pantalla completa
        main_frame = tk.Frame(self, bg='#f8f9fa', padx=20, pady=15)
        main_frame.pack(expand=True, fill='both')
        
        # Título principal
        title_frame = tk.Frame(main_frame, bg='#f8f9fa')
        title_frame.pack(fill='x', pady=(0, 15))
        
        title_label = tk.Label(title_frame, text="ESTADÍSTICAS DEL SISTEMA", 
                               font=('Segoe UI', 16, 'bold'), 
                               fg='#2c3e50', bg='#f8f9fa')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Resumen de actividad y métricas", 
                                 font=('Segoe UI', 10), 
                                 fg='#7f8c8d', bg='#f8f9fa')
        subtitle_label.pack()
        
        # Frame de estadísticas detalladas
        details_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        details_frame.pack(fill='both', expand=True)
        
        # Título de estadísticas detalladas
        details_title = tk.Label(details_frame, text="ESTADÍSTICAS DETALLADAS", 
                                font=('Segoe UI', 12, 'bold'), 
                                fg='#2c3e50', bg='white')
        details_title.pack(pady=(12, 8))
        
        self.create_detailed_stats(details_frame)
        

        
    def create_detailed_stats(self, parent):
        """Crear estadísticas detalladas"""
        # Notebook para pestañas
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Pestaña 1: Resumen general
        summary_frame = tk.Frame(notebook, bg='white')
        notebook.add(summary_frame, text="Resumen General")
        self.create_summary_tab(summary_frame)
        
        # Pestaña 2: Estadísticas generales
        general_frame = tk.Frame(notebook, bg='white')
        notebook.add(general_frame, text="Estadísticas Generales")
        self.create_general_tab(general_frame)
        
        # Pestaña 3: Registros por hora
        hourly_frame = tk.Frame(notebook, bg='white')
        notebook.add(hourly_frame, text="Registros por Hora")
        self.create_hourly_tab(hourly_frame)
        
    def create_summary_tab(self, parent):
        """Crear pestaña de resumen general"""
        # Frame con scrollbar
        canvas = tk.Canvas(parent, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white', padx=15, pady=15)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Contenido del resumen
        self.create_summary_content(scrollable_frame)
        
        # Configurar el scroll después de crear todo el contenido
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Asegurar que el ancho del canvas coincida con el contenido
            if canvas.find_withtag("all"):
                canvas.itemconfig(canvas.find_withtag("all")[0], width=canvas.winfo_width())
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        
        # Configurar scroll con mouse wheel
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Configurar scroll para toda la pestaña
        canvas.bind("<MouseWheel>", on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", on_mousewheel)
        
        # También configurar scroll para widgets hijos
        def bind_mousewheel_to_children(widget):
            try:
                widget.bind("<MouseWheel>", on_mousewheel)
                for child in widget.winfo_children():
                    bind_mousewheel_to_children(child)
            except:
                pass
        
        # Aplicar scroll a todos los widgets hijos después de crear el contenido
        canvas.after(200, lambda: bind_mousewheel_to_children(scrollable_frame))
        
        # Configurar scroll con teclas
        def on_key_press(event):
            if event.keysym == 'Up':
                canvas.yview_scroll(-1, "units")
            elif event.keysym == 'Down':
                canvas.yview_scroll(1, "units")
            elif event.keysym == 'Page_Up':
                canvas.yview_scroll(-1, "pages")
            elif event.keysym == 'Page_Down':
                canvas.yview_scroll(1, "pages")
        
        canvas.bind("<KeyPress>", on_key_press)
        scrollable_frame.bind("<KeyPress>", on_key_press)
        
        # Configurar el scroll inicial después de que todo esté creado
        canvas.after(100, lambda: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Configurar focus para que funcione el scroll con teclado
        canvas.focus_set()
        
        # Empaquetar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_summary_content(self, parent):
        """Crear contenido del resumen"""
        # Métricas principales
        metrics_frame = tk.Frame(parent, bg='white')
        metrics_frame.pack(fill='x', pady=(0, 20))
        
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
        """Crear pestaña de estadísticas generales con diseño moderno"""
        # Frame principal con scroll
        canvas = tk.Canvas(parent, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f8f9fa', padx=20, pady=20)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Título principal con diseño moderno
        title_frame = tk.Frame(scrollable_frame, bg='#f8f9fa')
        title_frame.pack(fill='x', pady=(0, 25))
        
        title = tk.Label(title_frame, text="📊 ESTADÍSTICAS GENERALES", 
                        font=('Segoe UI', 18, 'bold'), 
                        fg='#2c3e50', bg='#f8f9fa')
        title.pack()
        
        subtitle = tk.Label(title_frame, text="Análisis detallado de la información del sistema", 
                           font=('Segoe UI', 11), 
                           fg='#7f8c8d', bg='#f8f9fa')
        subtitle.pack(pady=(5, 0))
        
        # Crear secciones con nuevo diseño
        self.create_modern_section(scrollable_frame, "Distribución por Unidad de Inscripción", 
                                 self.create_unidad_content, "unidad", expanded=True, color="#4a90e2")
        self.create_modern_section(scrollable_frame, "Distribución por Dedo Registrado", 
                                 self.create_dedo_content, "dedo", color="#4a90e2")
        self.create_modern_section(scrollable_frame, "Distribución por Edades", 
                                 self.create_edad_content, "edad", color="#4a90e2")
        self.create_modern_section(scrollable_frame, "Registros por Usuario", 
                                 self.create_usuario_content, "usuario", color="#4a90e2")
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar el scroll después de crear todo el contenido
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Asegurar que el ancho del canvas coincida con el contenido
            canvas.itemconfig(canvas.find_withtag("all")[0], width=canvas.winfo_width())
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        
        # Configurar scroll con mouse wheel
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Configurar scroll para toda la pestaña
        canvas.bind("<MouseWheel>", on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", on_mousewheel)
        
        # Configurar scroll con teclas
        def on_key_press(event):
            if event.keysym == 'Up':
                canvas.yview_scroll(-1, "units")
            elif event.keysym == 'Down':
                canvas.yview_scroll(1, "units")
            elif event.keysym == 'Page_Up':
                canvas.yview_scroll(-1, "pages")
            elif event.keysym == 'Page_Down':
                canvas.yview_scroll(1, "pages")
        
        canvas.bind("<KeyPress>", on_key_press)
        scrollable_frame.bind("<KeyPress>", on_key_press)
        
        # Configurar el scroll inicial después de que todo esté creado
        canvas.after(100, lambda: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Configurar focus para que funcione el scroll con teclado
        canvas.focus_set()
        
    def create_modern_section(self, parent, title, content_creator, section_id, expanded=False, color="#4a90e2"):
        """Crear una sección moderna con diseño atractivo"""
        # Frame principal con sombra y bordes redondeados
        section_frame = tk.Frame(parent, bg='white', relief='flat', bd=0)
        section_frame.pack(fill='x', pady=(0, 15))
        
        # Frame interno con borde y sombra
        inner_frame = tk.Frame(section_frame, bg='white', relief='solid', bd=1)
        inner_frame.pack(fill='x', padx=2, pady=2)
        
        # Frame del header con color de acento - HACER CLICKEABLE
        header_frame = tk.Frame(inner_frame, bg=color, cursor='hand2')
        header_frame.pack(fill='x')
        
        # Título de la sección con color blanco
        title_label = tk.Label(header_frame, text=title, 
                              font=('Segoe UI', 12, 'bold'), 
                              fg='white', bg=color, cursor='hand2')
        title_label.pack(side='left', padx=15, pady=12)
        
        # Botón expandir/contraer moderno
        expand_btn = tk.Label(header_frame, text="▼", 
                             font=('Segoe UI', 12, 'bold'),
                             fg='white', bg=color, cursor='hand2')
        expand_btn.pack(side='right', padx=15, pady=12)
        
        # Frame para el contenido con padding
        content_frame = tk.Frame(inner_frame, bg='white')
        
        # Crear el contenido específico
        content_creator(content_frame)
        
        # Configurar estado inicial (expandido o contraído)
        if expanded:
            content_frame.pack(fill='x', padx=15, pady=15)
            expand_btn.config(text="▲")
        # Si no está expandido, el content_frame no se empaqueta (queda oculto)
        
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
        
    def create_expandable_section(self, parent, title, content_creator, section_id, expanded=False):
        """Crear una sección expandible (mantener para compatibilidad)"""
        # Frame principal de la sección
        section_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        section_frame.pack(fill='x', pady=(0, 10))
        
        # Frame del header (título + botón)
        header_frame = tk.Frame(section_frame, bg='#f8f9fa')
        header_frame.pack(fill='x')
        
        # Título de la sección
        title_label = tk.Label(header_frame, text=title, 
                              font=('Segoe UI', 11, 'bold'), 
                              fg='#2c3e50', bg='#f8f9fa')
        title_label.pack(side='left', padx=10, pady=8)
        
        # Botón expandir/contraer
        expand_btn = tk.Button(header_frame, text="▼", 
                              font=('Segoe UI', 10, 'bold'),
                              fg='#3498db', bg='#f8f9fa',
                              relief='flat', bd=0,
                              cursor='hand2',
                              command=lambda: self.toggle_section(section_id, content_frame, expand_btn))
        expand_btn.pack(side='right', padx=10, pady=8)
        
        # Frame para el contenido
        content_frame = tk.Frame(section_frame, bg='white')
        
        # Crear el contenido específico
        content_creator(content_frame)
        
        # Configurar estado inicial (expandido o contraído)
        if expanded:
            content_frame.pack(fill='x')
            expand_btn.config(text="▲")
        # Si no está expandido, el content_frame no se empaqueta (queda oculto)
        
        # Guardar referencias para el toggle
        if not hasattr(self, 'expandable_sections'):
            self.expandable_sections = {}
        self.expandable_sections[section_id] = {
            'content_frame': content_frame,
            'expand_btn': expand_btn,
            'expanded': expanded
        }
        
    def create_unidad_content(self, parent):
        """Crear contenido para distribución por unidad"""
        # Frame para el contenido con diseño moderno
        content_frame = tk.Frame(parent, bg='white')
        content_frame.pack(fill='x')
        
        # Título del contenido
        title_label = tk.Label(content_frame, text="Detalles por Unidad", 
                              font=('Segoe UI', 11, 'bold'), 
                              fg='#2c3e50', bg='white')
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Texto de distribución por unidad (solo lectura) con diseño mejorado
        self.unidad_text = tk.Text(content_frame, height=8, width=70, 
                                  font=('Segoe UI', 10), 
                                  bg='#f8f9fa', fg='#2c3e50',
                                  relief='flat', bd=1, state='disabled',
                                  padx=15, pady=15)
        self.unidad_text.pack(fill='x')
        
    def create_dedo_content(self, parent):
        """Crear contenido para distribución por dedo"""
        # Frame para el contenido con diseño moderno
        content_frame = tk.Frame(parent, bg='white')
        content_frame.pack(fill='x')
        
        # Título del contenido
        title_label = tk.Label(content_frame, text="Detalles por Dedo", 
                              font=('Segoe UI', 12, 'bold'), 
                              fg='#2c3e50', bg='white')
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Texto de distribución por dedo (solo lectura) con diseño mejorado
        self.dedos_text = tk.Text(content_frame, height=8, width=70, 
                                 font=('Segoe UI', 10), 
                                 bg='#f8f9fa', fg='#2c3e50',
                                 relief='flat', bd=1, state='disabled',
                                 padx=15, pady=15)
        self.dedos_text.pack(fill='x')
        
    def create_edad_content(self, parent):
        """Crear contenido para distribución por edad"""
        # Frame para el contenido con diseño moderno
        content_frame = tk.Frame(parent, bg='white')
        content_frame.pack(fill='x')
        
        # Título del contenido
        title_label = tk.Label(content_frame, text="Detalles por Edad", 
                              font=('Segoe UI', 11, 'bold'), 
                              fg='#2c3e50', bg='white')
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Texto de distribución por edad (solo lectura) con diseño mejorado
        self.age_distribution_text = tk.Text(content_frame, height=8, width=70, 
                                            font=('Segoe UI', 10), 
                                            bg='#f8f9fa', fg='#2c3e50',
                                            relief='flat', bd=1, state='disabled',
                                            padx=15, pady=15)
        self.age_distribution_text.pack(fill='x')
        
    def create_usuario_content(self, parent):
        """Crear contenido para registros por usuario"""
        # Frame para el contenido con diseño moderno
        content_frame = tk.Frame(parent, bg='white')
        content_frame.pack(fill='x')
        
        # Título del contenido
        title_label = tk.Label(content_frame, text="Detalles por Usuario", 
                              font=('Segoe UI', 11, 'bold'), 
                              fg='#2c3e50', bg='white')
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Texto de registros por usuario (solo lectura) con diseño mejorado
        self.usuario_text = tk.Text(content_frame, height=8, width=70, 
                                   font=('Segoe UI', 10), 
                                   bg='#f8f9fa', fg='#2c3e50',
                                   relief='flat', bd=1, state='disabled',
                                   padx=15, pady=15)
        self.usuario_text.pack(fill='x')
        
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
            
        # Actualizar el scroll después de expandir/contraer
        # Buscar el canvas padre y actualizar su scrollregion
        parent = content_frame.master
        while parent and not isinstance(parent, tk.Canvas):
            parent = parent.master
        
        if parent and isinstance(parent, tk.Canvas):
            # Usar after para asegurar que el layout se actualice antes de configurar el scroll
            parent.after(10, lambda: self.update_canvas_scroll(parent))
    
    def toggle_section(self, section_id, content_frame, expand_btn):
        """Expandir o contraer una sección"""
        section = self.expandable_sections[section_id]
        
        if section['expanded']:
            # Contraer
            content_frame.pack_forget()
            expand_btn.config(text="▼")
            section['expanded'] = False
        else:
            # Expandir
            content_frame.pack(fill='x')
            expand_btn.config(text="▲")
            section['expanded'] = True
            
        # Actualizar el scroll después de expandir/contraer
        # Buscar el canvas padre y actualizar su scrollregion
        parent = content_frame.master
        while parent and not isinstance(parent, tk.Canvas):
            parent = parent.master
        
        if parent and isinstance(parent, tk.Canvas):
            # Usar after para asegurar que el layout se actualice antes de configurar el scroll
            parent.after(10, lambda: self.update_canvas_scroll(parent))
    
    def update_canvas_scroll(self, canvas):
        """Actualizar el scroll del canvas"""
        try:
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
        except Exception as e:
            print(f"Error al actualizar scroll: {e}")
        

        
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
        self.summary_text_var = tk.StringVar(value="Seleccione fecha y rango horario")
        
        # Texto del resumen
        summary_text = tk.Label(summary_card_frame, textvariable=self.summary_text_var,
                               font=('Segoe UI', 12), 
                               fg='#2c3e50', bg='#e8f5e8',
                               wraplength=600, justify='center')
        summary_text.pack(pady=(0, 15))
        

        
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def load_statistics(self):
        """Cargar todas las estadísticas"""
        try:
            # Cargar métricas principales
            self.load_main_metrics()
            
            # Cargar estadísticas detalladas
            self.load_detailed_stats()
            
            # Cargar estadísticas por hora
            self.update_hourly_stats()
            
            # Actualizar el scroll y forzar redibujado después de cargar todo el contenido
            self.after(200, self.refresh_all_scrollbars)
            self.after(300, self.force_content_update)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar estadísticas: {e}")
            
    def refresh_all_scrollbars(self):
        """Actualizar todas las barras de scroll después de cargar contenido"""
        try:
            def update_canvas_scroll(widget):
                if isinstance(widget, tk.Canvas):
                    try:
                        widget.configure(scrollregion=widget.bbox("all"))
                        widget.update_idletasks()
                    except:
                        pass
                
                for child in widget.winfo_children():
                    update_canvas_scroll(child)
            
            # Actualizar todos los canvas en la ventana
            update_canvas_scroll(self)
            
        except Exception as e:
            print(f"Error al actualizar scrollbars: {e}")
            
    def force_content_update(self):
        """Forzar la actualización visual de todo el contenido"""
        try:
            # Forzar actualización de todos los widgets Text
            for widget_name in ['unidad_text', 'dedos_text', 'age_distribution_text', 'usuario_text']:
                if hasattr(self, widget_name):
                    widget = getattr(self, widget_name)
                    try:
                        widget.update_idletasks()
                        widget.update()
                    except:
                        pass
            
            # Forzar actualización de la ventana completa
            self.update_idletasks()
            self.update()
            
        except Exception as e:
            print(f"Error al forzar actualización de contenido: {e}")
            
    def load_main_metrics(self):
        """Cargar métricas principales"""
        try:
            conn = connect_db()
            if not conn:
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
            
            # Actualizar variables
            self.total_postulantes_var.set(str(total_postulantes))
            self.total_usuarios_var.set(str(total_usuarios))
            self.postulantes_hoy_var.set(str(postulantes_hoy))
            self.postulantes_semana_var.set(str(postulantes_semana))
            self.postulantes_mes_var.set(str(postulantes_mes))
            
            conn.close()
            
        except Exception as e:
            print(f"Error al cargar métricas principales: {e}")
            
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
            
            # Distribución por unidad
            self.update_unidad_distribution(postulantes)
            
            # Distribución por dedos
            self.update_dedos_distribution(postulantes)
                    
            # Distribución por edad
            self.update_age_distribution(edades)
            
            # Registros por usuario
            self.update_usuario_distribution()
            
            conn.close()
            
        except Exception as e:
            print(f"Error al cargar estadísticas detalladas: {e}")
            
    def update_unidad_distribution(self, postulantes):
        """Actualizar distribución por unidad de inscripción"""
        try:
            # Verificar que el widget existe
            if not hasattr(self, 'unidad_text'):
                print("Widget unidad_text no existe aún")
                return
                
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
                    self.unidad_text.insert(tk.END, f"{unidad:<20} {count:>4} ({porcentaje:>5.1f}%)\n")
                    
                self.unidad_text.insert(tk.END, f"\nTotal: {total} registros\n")
            else:
                self.unidad_text.insert(tk.END, "No hay datos de unidades disponibles")
            self.unidad_text.config(state='disabled')
            
            # Forzar actualización visual
            self.unidad_text.update_idletasks()
            self.unidad_text.update()
                
        except Exception as e:
            print(f"Error al actualizar distribución de unidades: {e}")
            
    def update_dedos_distribution(self, postulantes):
        """Actualizar distribución por dedos registrados"""
        try:
            # Verificar que el widget existe
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
                    self.dedos_text.insert(tk.END, f"{dedo:<10} {count:>4} ({porcentaje:>5.1f}%)\n")
                    
                self.dedos_text.insert(tk.END, f"\nTotal: {total} registros\n")
            else:
                self.dedos_text.insert(tk.END, "No hay datos de dedos registrados")
            self.dedos_text.config(state='disabled')
            
            # Forzar actualización visual
            self.dedos_text.update_idletasks()
            self.dedos_text.update()
                
        except Exception as e:
            print(f"Error al actualizar distribución de dedos: {e}")
            
    def update_age_distribution(self, edades):
        """Actualizar distribución por edad"""
        try:
            # Verificar que el widget existe
            if not hasattr(self, 'age_distribution_text'):
                print("Widget age_distribution_text no existe aún")
                return
                
            if not edades:
                self.age_distribution_text.config(state='normal')
                self.age_distribution_text.delete(1.0, tk.END)
                self.age_distribution_text.insert(tk.END, "No hay datos de edad disponibles")
                self.age_distribution_text.config(state='disabled')
                return
                
            # Crear rangos de edad
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
                    
            # Mostrar distribución
            self.age_distribution_text.config(state='normal')
            self.age_distribution_text.delete(1.0, tk.END)
            self.age_distribution_text.insert(tk.END, "DISTRIBUCIÓN DE EDADES\n")
            self.age_distribution_text.insert(tk.END, "=" * 30 + "\n\n")
            
            total = len(edades)
            for rango, count in rangos.items():
                if count > 0:
                    porcentaje = (count / total) * 100
                    self.age_distribution_text.insert(tk.END, f"{rango:<8} {count:>4} ({porcentaje:>5.1f}%)\n")
                    
            self.age_distribution_text.insert(tk.END, f"\nTotal: {total} registros\n")
            self.age_distribution_text.insert(tk.END, f"Promedio: {sum(edades)/len(edades):.1f} años\n")
            self.age_distribution_text.config(state='disabled')
            
            # Forzar actualización visual
            self.age_distribution_text.update_idletasks()
            self.age_distribution_text.update()
                
        except Exception as e:
            print(f"Error al actualizar distribución de edad: {e}")
            
    def update_usuario_distribution(self):
        """Actualizar distribución por registros de usuario"""
        try:
            # Verificar que el widget existe
            if not hasattr(self, 'usuario_text'):
                print("Widget usuario_text no existe aún")
                return
                
            # Obtener datos de la base de datos
            conn = connect_db()
            if not conn:
                return
                
            cursor = conn.cursor()
            
            # Consulta para obtener los 5 usuarios que más han registrado postulantes
            cursor.execute("""
                SELECT 
                    u.nombre,
                    u.apellido,
                    COUNT(p.id) as total_registros
                FROM usuarios u
                LEFT JOIN postulantes p ON u.id = p.usuario_registrador
                GROUP BY u.id, u.nombre, u.apellido
                ORDER BY total_registros DESC
                LIMIT 5
            """)
            
            usuarios_data = cursor.fetchall()
            
            # Mostrar distribución
            self.usuario_text.config(state='normal')
            self.usuario_text.delete(1.0, tk.END)
            if usuarios_data:
                self.usuario_text.insert(tk.END, "TOP 5 USUARIOS CON MÁS REGISTROS\n")
                self.usuario_text.insert(tk.END, "=" * 45 + "\n\n")
                
                # Calcular el total de registros para porcentajes
                total_registros = sum(row[2] for row in usuarios_data)
                
                for i, (nombre, apellido, registros) in enumerate(usuarios_data, 1):
                    nombre_completo = f"{nombre} {apellido}".strip()
                    if registros > 0:
                        porcentaje = (registros / total_registros) * 100
                        self.usuario_text.insert(tk.END, f"{i:2d}. {nombre_completo:<25} {registros:>4} ({porcentaje:>5.1f}%)\n")
            else:
                        self.usuario_text.insert(tk.END, f"{i:2d}. {nombre_completo:<25} {registros:>4} (0.0%)\n")
                
                self.usuario_text.insert(tk.END, f"\nTotal de registros: {total_registros}\n")
            else:
                self.usuario_text.insert(tk.END, "No hay datos de usuarios disponibles")
            self.usuario_text.config(state='disabled')
            
            # Forzar actualización visual
            self.usuario_text.update_idletasks()
            self.usuario_text.update()
                
            conn.close()
            
        except Exception as e:
            print(f"Error al actualizar distribución de usuarios: {e}")
            if hasattr(self, 'usuario_text'):
                self.usuario_text.config(state='normal')
                self.usuario_text.delete(1.0, tk.END)
                self.usuario_text.insert(tk.END, f"Error al cargar datos: {e}")
                self.usuario_text.config(state='disabled')
            

            
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
            
            # Los títulos se mostrarán directamente en el texto de detalles
            
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