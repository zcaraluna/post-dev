#!/usr/bin/env python3
"""
Módulo para mostrar lista completa de postulantes con paginación y filtros avanzados
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import math
from database import get_postulantes, eliminar_postulante, connect_db
from editar_postulante import EditarPostulante
from PIL import Image, ImageTk
import os

class ListaPostulantes(tk.Toplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.parent = parent
        self.user_data = user_data
        
        # Configuración de la ventana
        self.title("Lista de Postulantes")
        self.geometry('')  # Tamaño más controlado
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        # Variables de paginación optimizada
        self.current_page = 1
        self.items_per_page = 10
        self.total_items = 0
        self.total_pages = 0
        
        # Variables de filtro
        self.filter_nombre = tk.StringVar()
        self.filter_apellido = tk.StringVar()
        self.filter_cedula = tk.StringVar()
        self.filter_fecha_desde = tk.StringVar()
        self.filter_fecha_hasta = tk.StringVar()
        self.filter_unidad = tk.StringVar()
        self.filter_dedo = tk.StringVar()
        self.filter_aparato = tk.StringVar()
        
        # Cargar imagen institucional
        self.load_institutional_image()
        
        # Configurar UI
        self.setup_ui()
        self.center_window()
        self.load_postulantes()
        
    def load_institutional_image(self):
        """Cargar imagen institucional"""
        try:
            import sys
            
            # Función para obtener la ruta base correcta
            def get_base_path():
                if getattr(sys, 'frozen', False):
                    # Ejecutando desde PyInstaller
                    return os.path.dirname(sys.executable)
                else:
                    # Ejecutando desde script
                    return os.path.dirname(os.path.abspath(__file__))
            
            base_path = get_base_path()
            
            # Lista de posibles rutas para la imagen
            posibles_rutas = [
                os.path.join(base_path, "quira.png"),
                os.path.join(base_path, "_internal", "quira.png"),  # En _internal (PyInstaller)
                "quira.png",  # Ruta relativa
            ]
            
            image_path = None
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    image_path = ruta
                    break
            
            if image_path:
                self.institutional_image = Image.open(image_path)
                # Redimensionar manteniendo proporción, máximo 160px de altura
                max_height = 160
                ratio = max_height / self.institutional_image.height
                new_width = int(self.institutional_image.width * ratio)
                self.institutional_image = self.institutional_image.resize((new_width, max_height), Image.Resampling.LANCZOS)
                self.institutional_image_tk = ImageTk.PhotoImage(self.institutional_image)
                print(f"✅ Imagen institucional cargada desde: {image_path}")
            else:
                self.institutional_image_tk = None
                print("⚠️ No se encontró la imagen institucional")
        except Exception as e:
            print(f"❌ Error al cargar imagen institucional: {e}")
            self.institutional_image_tk = None
        
    def setup_ui(self):
        """Configurar la interfaz con diseño moderno minimalista"""
        # Configurar el fondo principal
        self.configure(bg='#f8f9fa')
        
        # Frame principal con padding mínimo
        main_frame = tk.Frame(self, bg='#f8f9fa')
        main_frame.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Header con imagen institucional
        header_frame = tk.Frame(main_frame, bg='#f8f9fa')
        header_frame.pack(fill='x', pady=0)
        
        # Título y controles superiores
        title_frame = tk.Frame(header_frame, bg='#f8f9fa')
        title_frame.pack(fill='x')
        
        # Título con estilo moderno más compacto
        title_label = tk.Label(title_frame, text="Lista de Postulantes", 
                              font=('Segoe UI', 14, 'bold'), 
                              fg='#2c3e50', bg='#f8f9fa')
        title_label.pack(side='left')
        
        # Imagen institucional (si existe)
        if self.institutional_image_tk:
            image_label = tk.Label(title_frame, image=self.institutional_image_tk, bg='#f8f9fa')
            image_label.pack(side='right', padx=(10, 0))
        
        # Controles de acción eliminados para maximizar espacio de tabla
        
        # Frame de filtros con estilo moderno
        filter_frame = tk.LabelFrame(main_frame, text="Filtros de Búsqueda", 
                                   font=('Segoe UI', 11, 'bold'), 
                                   fg='#2c3e50', bg='#f8f9fa', 
                                   relief='flat', bd=1)
        filter_frame.pack(fill='x', pady=(2, 4))
        
        # Frame interno para filtros con padding reducido
        filter_inner_frame = tk.Frame(filter_frame, bg='#f8f9fa')
        filter_inner_frame.pack(fill='x', padx=8, pady=3)
        
        self.create_filters(filter_inner_frame)
        
        # Frame de tabla con estilo moderno
        table_frame = tk.LabelFrame(main_frame, text="Postulantes Registrados", 
                                  font=('Segoe UI', 11, 'bold'), 
                                  fg='#2c3e50', bg='#f8f9fa', 
                                  relief='flat', bd=1)
        table_frame.pack(fill='both', expand=True, pady=(2, 4))
        
        # Frame interno para tabla con padding reducido
        table_inner_frame = tk.Frame(table_frame, bg='#f8f9fa')
        table_inner_frame.pack(fill='both', expand=True, padx=8, pady=3)
        
        self.create_table(table_inner_frame)
        
        # Frame de paginación
        pagination_frame = tk.Frame(main_frame, bg='#f8f9fa')
        pagination_frame.pack(fill='x', pady=(0, 10))
        
        self.create_pagination_controls(pagination_frame)
        
        # Frame de información
        info_frame = tk.Frame(main_frame, bg='#f8f9fa')
        info_frame.pack(fill='x')
        
        self.info_label = tk.Label(info_frame, text="Cargando postulantes...", 
                                  font=('Segoe UI', 10), 
                                  fg='#6c757d', bg='#f8f9fa')
        self.info_label.pack(side='left')
        
        # Barra de estado
        self.status_label = tk.Label(info_frame, text="", 
                                    font=('Segoe UI', 10), 
                                    fg='#6c757d', bg='#f8f9fa')
        self.status_label.pack(side='right')
        
    def create_filters(self, parent):
        """Crear controles de filtro avanzados"""
        # Frame principal de filtros
        filters_frame = ttk.Frame(parent)
        filters_frame.pack(fill='x')
        
        # Primera fila de filtros
        row1_frame = tk.Frame(filters_frame, bg='#f8f9fa')
        row1_frame.pack(fill='x', pady=(0, 5))
        
        # Filtro por nombre
        tk.Label(row1_frame, text="Nombre:", 
                font=('Segoe UI', 10), 
                fg='#6c757d', bg='#f8f9fa').grid(row=0, column=0, sticky='w', pady=4)
        ttk.Entry(row1_frame, textvariable=self.filter_nombre, width=20).grid(row=0, column=1, padx=(10, 20), pady=4)
        
        # Filtro por apellido
        tk.Label(row1_frame, text="Apellido:", 
                font=('Segoe UI', 10), 
                fg='#6c757d', bg='#f8f9fa').grid(row=0, column=2, sticky='w', pady=4)
        ttk.Entry(row1_frame, textvariable=self.filter_apellido, width=20).grid(row=0, column=3, padx=(10, 20), pady=4)
        
        # Filtro por cédula
        tk.Label(row1_frame, text="Cédula:", 
                font=('Segoe UI', 10), 
                fg='#6c757d', bg='#f8f9fa').grid(row=0, column=4, sticky='w', pady=4)
        ttk.Entry(row1_frame, textvariable=self.filter_cedula, width=15).grid(row=0, column=5, padx=(10, 0), pady=4)
        
        # Segunda fila de filtros
        row2_frame = tk.Frame(filters_frame, bg='#f8f9fa')
        row2_frame.pack(fill='x', pady=(0, 5))
        
        # Filtro por fecha desde
        tk.Label(row2_frame, text="Fecha desde (DD/MM/AAAA):", 
                font=('Segoe UI', 10), 
                fg='#6c757d', bg='#f8f9fa').grid(row=0, column=0, sticky='w', pady=4)
        ttk.Entry(row2_frame, textvariable=self.filter_fecha_desde, width=15).grid(row=0, column=1, padx=(10, 20), pady=4)
        
        # Filtro por fecha hasta
        tk.Label(row2_frame, text="Fecha hasta (DD/MM/AAAA):", 
                font=('Segoe UI', 10), 
                fg='#6c757d', bg='#f8f9fa').grid(row=0, column=2, sticky='w', pady=4)
        ttk.Entry(row2_frame, textvariable=self.filter_fecha_hasta, width=15).grid(row=0, column=3, padx=(10, 20), pady=4)
        
        # Tercera fila de filtros
        row3_frame = tk.Frame(filters_frame, bg='#f8f9fa')
        row3_frame.pack(fill='x', pady=(0, 5))
        
        # Filtro por unidad
        tk.Label(row3_frame, text="Unidad:", 
                font=('Segoe UI', 10), 
                fg='#6c757d', bg='#f8f9fa').grid(row=0, column=0, sticky='w', pady=4)
        self.unidad_combobox = ttk.Combobox(row3_frame, textvariable=self.filter_unidad, width=20, state='readonly')
        self.unidad_combobox.grid(row=0, column=1, padx=(10, 20), pady=4)
        
        # Filtro por dedo
        tk.Label(row3_frame, text="Dedo:", 
                font=('Segoe UI', 10), 
                fg='#6c757d', bg='#f8f9fa').grid(row=0, column=2, sticky='w', pady=4)
        self.dedo_combobox = ttk.Combobox(row3_frame, textvariable=self.filter_dedo, width=15, state='readonly')
        self.dedo_combobox.grid(row=0, column=3, padx=(10, 20), pady=4)
        
        # Filtro por aparato
        tk.Label(row3_frame, text="Aparato:", 
                font=('Segoe UI', 10), 
                fg='#6c757d', bg='#f8f9fa').grid(row=0, column=4, sticky='w', pady=4)
        self.aparato_combobox = ttk.Combobox(row3_frame, textvariable=self.filter_aparato, width=20, state='readonly')
        self.aparato_combobox.grid(row=0, column=5, padx=(10, 0), pady=4)
        
        # Botones de filtro
        filter_buttons_frame = tk.Frame(parent, bg='#f8f9fa')
        filter_buttons_frame.pack(fill='x', pady=(10, 0))
        
        self.create_modern_button(filter_buttons_frame, "Aplicar Filtros", self.apply_filters).pack(side='left', padx=(0, 10))
        self.create_modern_button(filter_buttons_frame, "Limpiar Filtros", self.clear_filters).pack(side='left')
        
        # Configurar grid para responsive design
        for frame in [row1_frame, row2_frame, row3_frame]:
            frame.columnconfigure(1, weight=1)
            frame.columnconfigure(3, weight=1)
            frame.columnconfigure(5, weight=1)
        
    def create_modern_button(self, parent, text, command):
        """Crear un botón con estilo moderno y minimalista"""
        # Frame contenedor para el botón
        button_frame = tk.Frame(parent, bg='#f8f9fa')
        
        # Botón principal
        btn = tk.Button(button_frame, text=text, command=command,
                       font=('Segoe UI', 11),
                       fg='#495057', bg='#ffffff',
                       activebackground='#2E5090',
                       activeforeground='#ffffff',
                       relief='flat', bd=0,
                       padx=15, pady=6,
                       cursor='hand2')
        btn.pack(fill='x')
        
        # Efectos hover
        def on_enter(e):
            btn.config(bg='#2E5090', fg='#ffffff')
        
        def on_leave(e):
            btn.config(bg='#ffffff', fg='#495057')
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return button_frame
        
    def create_table(self, parent):
        """Crear tabla de postulantes con columnas expandidas"""
        # Crear Treeview con columnas principales
        columns = ('ID', 'Nombre', 'Apellido', 'Cédula', 'Unidad', 'Dedo', 'Aparato', 'Fecha Registro')
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', height=12)
        
        # Configurar columnas
        self.tree.heading('Nombre', text='Nombre')
        self.tree.heading('Apellido', text='Apellido')
        self.tree.heading('Cédula', text='Cédula')
        self.tree.heading('Unidad', text='Unidad')
        self.tree.heading('Dedo', text='Dedo')
        self.tree.heading('Aparato', text='Aparato')
        self.tree.heading('Fecha Registro', text='Fecha Registro')
        
        # Configurar anchos de columna
        self.tree.column('ID', width=0, minwidth=0, stretch=False)  # Oculto
        self.tree.column('Nombre', width=200, minwidth=150)
        self.tree.column('Apellido', width=200, minwidth=150)
        self.tree.column('Cédula', width=120, minwidth=100)
        self.tree.column('Unidad', width=150, minwidth=120)
        self.tree.column('Dedo', width=100, minwidth=80)
        self.tree.column('Aparato', width=150, minwidth=120)
        self.tree.column('Fecha Registro', width=150, minwidth=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Empaquetar
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configurar grid
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Configurar eventos
        self.tree.bind('<Double-1>', self.on_item_double_click)
        
    def create_pagination_controls(self, parent):
        """Crear controles de paginación"""
        # Frame para controles de paginación
        pagination_controls = tk.Frame(parent, bg='#f8f9fa')
        pagination_controls.pack(fill='x')
        
        # Información de paginación
        self.pagination_info = tk.Label(pagination_controls, text="Cargando...", 
                                       font=('Segoe UI', 10), 
                                       fg='#6c757d', bg='#f8f9fa')
        self.pagination_info.pack(side='left')
        
        # Frame para controles
        controls_frame = tk.Frame(pagination_controls, bg='#f8f9fa')
        controls_frame.pack(side='right')
        
        # Selector de elementos por página
        tk.Label(controls_frame, text="Mostrar:", 
                font=('Segoe UI', 10), 
                fg='#6c757d', bg='#f8f9fa').pack(side='left', padx=(0, 5))
        self.items_per_page_var = tk.StringVar(value="10")
        items_combobox = ttk.Combobox(controls_frame, textvariable=self.items_per_page_var, 
                                     values=["5", "10", "20", "40"], width=5, state='readonly')
        items_combobox.pack(side='left', padx=(0, 20))
        items_combobox.bind('<<ComboboxSelected>>', self.on_items_per_page_change)
        
        # Establecer valor por defecto
        items_combobox.set("10")
        
        # Forzar actualización inicial después de un breve delay
        self.after(100, self.force_update_pagination)
        
        # Botones de navegación
        self.create_modern_button(controls_frame, "Primera", self.go_to_first_page).pack(side='left', padx=(0, 5))
        self.create_modern_button(controls_frame, "Anterior", self.go_to_previous_page).pack(side='left', padx=(0, 5))
        
        # Número de página actual
        self.page_label = tk.Label(controls_frame, text="1 de 1", 
                                  font=('Segoe UI', 10), 
                                  fg='#6c757d', bg='#f8f9fa')
        self.page_label.pack(side='left', padx=10)
        
        self.create_modern_button(controls_frame, "Siguiente", self.go_to_next_page).pack(side='left', padx=5)
        self.create_modern_button(controls_frame, "Última", self.go_to_last_page).pack(side='left', padx=5)
        
    def center_window(self):
        """Centrar la ventana"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def load_postulantes(self):
        """Cargar postulantes desde la base de datos con optimización"""
        try:
            print("DEBUG: Iniciando carga optimizada de postulantes...")
            
            # Obtener solo el total de postulantes (sin cargar todos los datos)
            from database import get_total_postulantes
            self.total_items = get_total_postulantes()
            
            print(f"DEBUG: Total de postulantes: {self.total_items}")
            
            # Cargar opciones de filtro
            self.load_filter_options()
            
            # Cargar solo la primera página
            self.current_page = 1
            self.display_current_page()
            
            # Actualizar paginación
            print("DEBUG: Actualizando paginación...")
            self.update_pagination()
            
            print("DEBUG: Carga optimizada completada")
                
        except Exception as e:
            print(f"ERROR en load_postulantes: {e}")
            self.info_label.config(text=f"Error al cargar postulantes: {e}")
            messagebox.showerror("Error", f"Error al cargar postulantes: {e}")
            
    def load_filter_options(self):
        """Cargar opciones para los combobox de filtro"""
        try:
            conn = connect_db()
            if not conn:
                return
                
            cursor = conn.cursor()
            
            # Obtener unidades únicas
            cursor.execute("SELECT DISTINCT unidad FROM postulantes WHERE unidad IS NOT NULL AND unidad != '' ORDER BY unidad")
            unidades = [row[0] for row in cursor.fetchall()]
            self.unidad_combobox['values'] = [''] + unidades
            
            # Obtener dedos únicos
            cursor.execute("SELECT DISTINCT dedo_registrado FROM postulantes WHERE dedo_registrado IS NOT NULL AND dedo_registrado != '' ORDER BY dedo_registrado")
            dedos = [row[0] for row in cursor.fetchall()]
            self.dedo_combobox['values'] = [''] + dedos
            
            # Obtener aparatos únicos y crear mapeo aparato_id -> nombre
            cursor.execute("""
                SELECT DISTINCT a.id, a.nombre 
                FROM aparatos_biometricos a 
                INNER JOIN postulantes p ON a.id = p.aparato_id 
                WHERE a.nombre IS NOT NULL AND a.nombre != ''
                ORDER BY a.nombre
            """)
            aparatos_data = cursor.fetchall()
            
            # Crear lista de nombres para el combobox
            aparatos = [row[1] for row in aparatos_data]
            self.aparato_combobox['values'] = [''] + aparatos
            
            # Crear diccionario de mapeo aparato_id -> nombre
            self.aparato_id_to_name = {row[0]: row[1] for row in aparatos_data}
            
            conn.close()
            
        except Exception as e:
            print(f"Error al cargar opciones de filtro: {e}")
            self.aparato_id_to_name = {}
        
    def apply_filters(self):
        """Aplicar filtros a los postulantes"""
        try:
            # Filtrar postulantes
            filtered = []
            
            for postulante in self.all_postulantes:
                # Filtro por nombre
                if self.filter_nombre.get() and self.filter_nombre.get().lower() not in postulante[1].lower():
                    continue
                    
                # Filtro por apellido
                if self.filter_apellido.get() and self.filter_apellido.get().lower() not in postulante[2].lower():
                    continue
                    
                # Filtro por cédula
                if self.filter_cedula.get() and self.filter_cedula.get() not in str(postulante[3]):
                    continue
                    
                # Filtro por fecha desde
                if self.filter_fecha_desde.get():
                    try:
                        fecha_desde = datetime.strptime(self.filter_fecha_desde.get(), '%d/%m/%Y')
                        if postulante[6] and postulante[6].date() < fecha_desde.date():
                            continue
                    except ValueError:
                        pass
                        
                # Filtro por fecha hasta
                if self.filter_fecha_hasta.get():
                    try:
                        fecha_hasta = datetime.strptime(self.filter_fecha_hasta.get(), '%d/%m/%Y')
                        if postulante[6] and postulante[6].date() > fecha_hasta.date():
                            continue
                    except ValueError:
                        pass
                        
                # Filtro por unidad
                if self.filter_unidad.get() and self.filter_unidad.get() != postulante[12]:
                    continue
                    
                # Filtro por dedo
                if self.filter_dedo.get() and self.filter_dedo.get() != postulante[13]:
                    continue
                    
                # Filtro por aparato (optimizado)
                if self.filter_aparato.get():
                    aparato_id = postulante[15]  # aparato_id está en la posición 15
                    aparato_nombre = self.aparato_id_to_name.get(aparato_id)
                    
                    if not aparato_nombre or aparato_nombre != self.filter_aparato.get():
                        continue
                
                filtered.append(postulante)
            
            self.filtered_postulantes = filtered
            self.current_page = 1
            self.update_pagination()
            self.display_current_page()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar filtros: {e}")
        
    def clear_filters(self):
        """Limpiar todos los filtros"""
        self.filter_nombre.set("")
        self.filter_apellido.set("")
        self.filter_cedula.set("")
        self.filter_fecha_desde.set("")
        self.filter_fecha_hasta.set("")
        self.filter_unidad.set("")
        self.filter_dedo.set("")
        self.filter_aparato.set("")
        
        self.filtered_postulantes = self.all_postulantes.copy()
        self.current_page = 1
        self.update_pagination()
        self.display_current_page()
        
    def update_pagination(self):
        """Actualizar información de paginación optimizada"""
        # Usar self.total_items que ya está calculado
        self.total_pages = math.ceil(self.total_items / self.items_per_page)
        
        if self.total_pages == 0:
            self.total_pages = 1
            
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
            
        # Actualizar información
        start_item = (self.current_page - 1) * self.items_per_page + 1
        end_item = min(self.current_page * self.items_per_page, self.total_items)
        
        # Texto de paginación
        if self.total_items == 0:
            pagination_text = "No hay postulantes que mostrar"
        else:
            pagination_text = f"Mostrando {start_item}-{end_item} de {self.total_items} postulantes"
        
        # Texto de página
        page_text = f"{self.current_page} de {self.total_pages}"
        
        # Actualizar etiquetas con verificación
        try:
            if hasattr(self, 'pagination_info') and self.pagination_info:
                self.pagination_info.config(text=pagination_text)
                print(f"DEBUG: Pagination info actualizado: {pagination_text}")
            
            if hasattr(self, 'page_label') and self.page_label:
                self.page_label.config(text=page_text)
                print(f"DEBUG: Page label actualizado: {page_text}")
            
            if hasattr(self, 'info_label') and self.info_label:
                self.info_label.config(text=f"Total: {self.total_items} postulante(s)")
            
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.config(text=f"Última actualización: {self.get_current_time()}")
                
        except Exception as e:
            print(f"ERROR al actualizar paginación: {e}")
    
    def force_update_pagination(self):
        """Forzar actualización de paginación"""
        try:
            print("DEBUG: Forzando actualización de paginación...")
            print(f"DEBUG: pagination_info existe: {hasattr(self, 'pagination_info')}")
            print(f"DEBUG: page_label existe: {hasattr(self, 'page_label')}")
            
            if hasattr(self, 'pagination_info') and self.pagination_info:
                print(f"DEBUG: pagination_info actual: {self.pagination_info.cget('text')}")
            
            if hasattr(self, 'page_label') and self.page_label:
                print(f"DEBUG: page_label actual: {self.page_label.cget('text')}")
            
            self.update_pagination()
            
        except Exception as e:
            print(f"ERROR en force_update_pagination: {e}")
        
    def display_current_page(self):
        """Mostrar la página actual de postulantes con optimización"""
        try:
            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Calcular índices de la página actual
            start_idx = (self.current_page - 1) * self.items_per_page
            
            # Obtener solo los postulantes de la página actual
            from database import get_postulantes
            page_postulantes = get_postulantes(limit=self.items_per_page, offset=start_idx)
            
            # Mostrar postulantes de la página actual
            for postulante in page_postulantes:
                # Formatear fecha
                fecha_registro = postulante[6].strftime('%d/%m/%Y %H:%M') if postulante[6] else 'N/A'
                
                # Obtener nombre del aparato
                aparato_nombre = 'N/A'
                if postulante[15]:  # aparato_id
                    try:
                        conn = connect_db()
                        if conn:
                            cursor = conn.cursor()
                            cursor.execute("SELECT nombre FROM aparatos_biometricos WHERE id = %s", (postulante[15],))
                            aparato_result = cursor.fetchone()
                            if aparato_result:
                                aparato_nombre = aparato_result[0]
                            conn.close()
                    except:
                        pass
                
                self.tree.insert('', 'end', values=(
                    postulante[0],  # ID
                    postulante[1],  # Nombre
                    postulante[2],  # Apellido
                    postulante[3],  # Cédula
                    postulante[12] or 'N/A',  # Unidad
                    postulante[13] or 'N/A',  # Dedo
                    aparato_nombre,  # Aparato
                    fecha_registro   # Fecha Registro
                ))
                
        except Exception as e:
            print(f"Error al mostrar página actual: {e}")
            # Fallback: mostrar mensaje de error
            self.tree.insert('', 'end', values=('Error', 'Error', 'Error', 'Error', 'Error', 'Error', 'Error', 'Error'))
            
    def on_items_per_page_change(self, event=None):
        """Manejar cambio en elementos por página"""
        try:
            self.items_per_page = int(self.items_per_page_var.get())
            self.current_page = 1
            self.update_pagination()
            self.display_current_page()
        except ValueError:
            pass
            
    def go_to_first_page(self):
        """Ir a la primera página"""
        if self.current_page > 1:
            self.current_page = 1
            self.update_pagination()
            self.display_current_page()
            
    def go_to_previous_page(self):
        """Ir a la página anterior"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_pagination()
            self.display_current_page()
            
    def go_to_next_page(self):
        """Ir a la página siguiente"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_pagination()
            self.display_current_page()
            
    def go_to_last_page(self):
        """Ir a la última página"""
        if self.current_page < self.total_pages:
            self.current_page = self.total_pages
            self.update_pagination()
            self.display_current_page()
            
    def get_current_time(self):
        """Obtener hora actual formateada"""
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        

        
    def on_item_double_click(self, event):
        """Manejar doble clic en un elemento"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            self.show_postulante_details(values)
            

            
    def show_postulante_details(self, values):
        """Mostrar detalles del postulante con interfaz moderna y estética"""
        if not values:
            return
            
        # Obtener información completa del postulante
        postulante_id = values[0]
        
        # Obtener datos completos del postulante
        from database import obtener_postulante_por_id, obtener_nombre_aparato
        postulante_completo = obtener_postulante_por_id(postulante_id)
        if not postulante_completo:
            messagebox.showerror("Error", "No se pudo obtener la información del postulante")
            return
            
        # Crear ventana de detalles con diseño moderno
        details_window = tk.Toplevel(self)
        details_window.title(f"Detalles del Postulante - {values[1]} {values[2]}")
        details_window.transient(self)
        details_window.grab_set()
        details_window.configure(bg='#f0f2f5')
        
        # Configurar para que se ajuste al contenido
        details_window.resizable(True, True)
        details_window.minsize(600, 400)
        
        # Configurar estilos para la ventana de detalles
        style = ttk.Style()
        style.configure('Details.TFrame', background='#f0f2f5')
        style.configure('Card.TFrame', background='white', relief='flat', borderwidth=1)
        style.configure('Header.TLabel', background='#2c3e50', foreground='white', font=('Segoe UI', 14, 'bold'))
        style.configure('Section.TLabel', background='white', foreground='#2c3e50', font=('Segoe UI', 12, 'bold'))
        style.configure('Info.TLabel', background='white', foreground='#34495e', font=('Segoe UI', 10))
        style.configure('Value.TLabel', background='white', foreground='#2c3e50', font=('Segoe UI', 10, 'bold'))
        
        # Frame principal con scroll
        main_canvas = tk.Canvas(details_window, bg='#f0f2f5', highlightthickness=0, height=560)
        scrollbar = ttk.Scrollbar(details_window, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas, style='Details.TFrame')
        
        # Configurar el canvas
        main_canvas.configure(yscrollcommand=scrollbar.set)
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Configurar el frame para que se expanda horizontalmente
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.pack(side="left", fill="both", expand=True, padx=30, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Obtener información adicional
        nombre_registrador = postulante_completo[11] or "Desconocido"
        nombre_aparato = obtener_nombre_aparato(postulante_completo[12])
        
        # Formatear fechas y calcular edad
        fecha_nacimiento = 'No registrada'
        edad_detallada = 'No registrada'
        
        if postulante_completo[4]:
            try:
                from datetime import datetime, date
                
                if isinstance(postulante_completo[4], str):
                    fecha_nac_obj = datetime.strptime(postulante_completo[4], "%Y-%m-%d").date()
                else:
                    fecha_nac_obj = postulante_completo[4]
                
                fecha_nacimiento = fecha_nac_obj.strftime('%d/%m/%Y')
                
                # Calcular edad detallada
                fecha_actual = date.today()
                diferencia = fecha_actual - fecha_nac_obj
                
                años = diferencia.days // 365
                meses_restantes = (diferencia.days % 365) // 30
                dias_restantes = (diferencia.days % 365) % 30
                
                if años > 0:
                    edad_detallada = f"{años} años"
                    if meses_restantes > 0:
                        edad_detallada += f", {meses_restantes} meses"
                    if dias_restantes > 0:
                        edad_detallada += f", {dias_restantes} días"
                elif meses_restantes > 0:
                    edad_detallada = f"{meses_restantes} meses"
                    if dias_restantes > 0:
                        edad_detallada += f", {dias_restantes} días"
                else:
                    edad_detallada = f"{dias_restantes} días"
                    
            except Exception as e:
                fecha_nacimiento = 'No registrada'
                edad_detallada = 'No registrada'
        
        fecha_ultima_edicion = 'No registrada'
        if postulante_completo[17]:
            try:
                if isinstance(postulante_completo[17], str):
                    from datetime import datetime
                    fecha_obj = datetime.strptime(postulante_completo[17], "%Y-%m-%d %H:%M:%S")
                    fecha_ultima_edicion = fecha_obj.strftime('%d/%m/%Y %H:%M')
                else:
                    fecha_ultima_edicion = postulante_completo[17].strftime('%d/%m/%Y %H:%M')
            except:
                fecha_ultima_edicion = 'No registrada'
        
        # SECCIÓN 1 - INFORMACIÓN DEL POSTULANTE
        personal_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        personal_frame.pack(fill='x', pady=(0, 15), padx=10)
        
        # Título de sección
        ttk.Label(personal_frame, text="INFORMACIÓN DEL POSTULANTE", style='Section.TLabel').pack(anchor='w', padx=20, pady=(15, 10))
        
        # Contenido de información personal
        personal_content = ttk.Frame(personal_frame, style='Card.TFrame')
        personal_content.pack(fill='x', padx=25, pady=(0, 15))
        
        personal_content.columnconfigure(1, weight=1, minsize=200)
        personal_content.columnconfigure(3, weight=1, minsize=200)
        
        # Nombre
        ttk.Label(personal_content, text="Nombre:", style='Info.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(personal_content, text=postulante_completo[1], style='Value.TLabel').grid(row=0, column=1, sticky='w', pady=5)
        
        # Apellido
        ttk.Label(personal_content, text="Apellido:", style='Info.TLabel').grid(row=0, column=2, sticky='w', padx=(20, 10), pady=5)
        ttk.Label(personal_content, text=postulante_completo[2], style='Value.TLabel').grid(row=0, column=3, sticky='w', pady=5)
        
        # Cédula
        ttk.Label(personal_content, text="Cédula:", style='Info.TLabel').grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(personal_content, text=str(postulante_completo[3]), style='Value.TLabel').grid(row=1, column=1, sticky='w', pady=5)
        
        # Fecha de nacimiento
        ttk.Label(personal_content, text="Fecha de Nacimiento:", style='Info.TLabel').grid(row=1, column=2, sticky='w', padx=(20, 10), pady=5)
        ttk.Label(personal_content, text=fecha_nacimiento, style='Value.TLabel').grid(row=1, column=3, sticky='w', pady=5)
        
        # Edad
        ttk.Label(personal_content, text="Edad:", style='Info.TLabel').grid(row=2, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(personal_content, text=edad_detallada, style='Value.TLabel').grid(row=2, column=1, sticky='w', pady=5)
        
        # Teléfono
        ttk.Label(personal_content, text="Teléfono:", style='Info.TLabel').grid(row=2, column=2, sticky='w', padx=(20, 10), pady=5)
        ttk.Label(personal_content, text=str(postulante_completo[5] or 'No registrado'), style='Value.TLabel').grid(row=2, column=3, sticky='w', pady=5)
        
        # SECCIÓN 2 - INFORMACIÓN DE REGISTRO
        registro_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        registro_frame.pack(fill='x', pady=(0, 15), padx=10)
        
        # Título de sección
        ttk.Label(registro_frame, text="INFORMACIÓN DE REGISTRO", style='Section.TLabel').pack(anchor='w', padx=20, pady=(15, 10))
        
        # Contenido de registro
        registro_content = ttk.Frame(registro_frame, style='Card.TFrame')
        registro_content.pack(fill='x', padx=25, pady=(0, 15))
        
        registro_content.columnconfigure(1, weight=1, minsize=200)
        registro_content.columnconfigure(3, weight=1, minsize=200)
        
        # Fecha de registro
        ttk.Label(registro_content, text="Fecha de Registro:", style='Info.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        fecha_registro = postulante_completo[6].strftime('%d/%m/%Y') if postulante_completo[6] else 'No registrada'
        ttk.Label(registro_content, text=fecha_registro, style='Value.TLabel').grid(row=0, column=1, sticky='w', pady=5)
        
        # Registrado por
        ttk.Label(registro_content, text="Registrado por:", style='Info.TLabel').grid(row=0, column=2, sticky='w', padx=(20, 10), pady=5)
        ttk.Label(registro_content, text=nombre_registrador, style='Value.TLabel').grid(row=0, column=3, sticky='w', pady=5)
        
        # Aparato biométrico
        ttk.Label(registro_content, text="Aparato Biométrico:", style='Info.TLabel').grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(registro_content, text=nombre_aparato, style='Value.TLabel').grid(row=1, column=1, sticky='w', pady=5)
        
        # Dedo registrado
        ttk.Label(registro_content, text="Dedo Registrado:", style='Info.TLabel').grid(row=1, column=2, sticky='w', padx=(20, 10), pady=5)
        ttk.Label(registro_content, text=str(postulante_completo[10] or 'No especificado'), style='Value.TLabel').grid(row=1, column=3, sticky='w', pady=5)
        
        # Unidad de inscripción
        ttk.Label(registro_content, text="Unidad de Inscripción:", style='Info.TLabel').grid(row=2, column=0, sticky='w', padx=(0, 10), pady=5)
        ttk.Label(registro_content, text=str(postulante_completo[9] or 'No especificada'), style='Value.TLabel').grid(row=2, column=1, sticky='w', pady=5)
        
        # UID K40 (si existe)
        if postulante_completo[13]:  # uid_k40
            ttk.Label(registro_content, text="UID K40:", style='Info.TLabel').grid(row=3, column=0, sticky='w', padx=(0, 10), pady=5)
            ttk.Label(registro_content, text=str(postulante_completo[13]), style='Value.TLabel').grid(row=3, column=1, sticky='w', pady=5)
        
        # Huella dactilar (si existe)
        if postulante_completo[14]:  # huella_dactilar
            ttk.Label(registro_content, text="Huella Dactilar:", style='Info.TLabel').grid(row=3, column=2, sticky='w', padx=(20, 10), pady=5)
            ttk.Label(registro_content, text="Registrada", style='Value.TLabel').grid(row=3, column=3, sticky='w', pady=5)
        
        # SECCIÓN 3 - Historial de Ediciones
        from database import obtener_historial_ediciones
        historial_ediciones = obtener_historial_ediciones(postulante_id)
        
        if historial_ediciones or (postulante_completo[16] and postulante_completo[16].strip()):
            edicion_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
            edicion_frame.pack(fill='x', pady=(0, 15), padx=10)
            
            # Título de sección
            ttk.Label(edicion_frame, text="HISTORIAL DE EDICIONES", style='Section.TLabel').pack(anchor='w', padx=20, pady=(15, 10))
            
            # Contenido de edición con diseño mejorado
            edicion_content = ttk.Frame(edicion_frame, style='Card.TFrame')
            edicion_content.pack(fill='x', padx=25, pady=(0, 15))
            
            # Frame para información destacada
            info_destacada_frame = tk.Frame(edicion_content, bg='#f8f9fa', relief='solid', bd=1)
            info_destacada_frame.pack(fill='x', padx=10, pady=10)
            
            # Información del último editor
            ultimo_editor_frame = tk.Frame(info_destacada_frame, bg='#f8f9fa')
            ultimo_editor_frame.pack(fill='x', padx=15, pady=10)
            
            # Usuario que editó
            ttk.Label(ultimo_editor_frame, text="Último editor:", style='Info.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
            ttk.Label(ultimo_editor_frame, text=postulante_completo[16], style='Value.TLabel').grid(row=0, column=1, sticky='w', pady=5)
            
            # Botón para ver historial completo (solo si hay historial)
            if historial_ediciones:
                def mostrar_historial_completo():
                    ventana_historial = tk.Toplevel(self)
                    ventana_historial.title(f"Historial Completo de Ediciones - {postulante_completo[1]} {postulante_completo[2]}")
                    ventana_historial.geometry("800x600")
                    ventana_historial.transient(self)
                    ventana_historial.grab_set()
                    ventana_historial.configure(bg='#f0f2f5')
                    
                    # Frame principal
                    main_frame = tk.Frame(ventana_historial, bg='#f0f2f5', padx=20, pady=20)
                    main_frame.pack(expand=True, fill='both')
                    
                    # Título
                    titulo = tk.Label(main_frame, text="HISTORIAL COMPLETO DE EDICIONES", 
                                      font=('Segoe UI', 16, 'bold'), 
                                      fg='#2c3e50', bg='#f0f2f5')
                    titulo.pack(pady=(0, 20))
                    
                    # Área de texto con scroll
                    text_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
                    text_frame.pack(expand=True, fill='both', pady=(0, 20))
                    
                    historial_text = tk.Text(text_frame, wrap='word', font=('Segoe UI', 10),
                                           relief='flat', bg='white', fg='#2c3e50')
                    historial_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
                    
                    # Scrollbar
                    scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=historial_text.yview)
                    scrollbar.pack(side='right', fill='y')
                    historial_text.configure(yscrollcommand=scrollbar.set)
                    
                    # Insertar historial (ordenado cronológicamente, más reciente primero)
                    for i, (usuario, fecha, cambios) in enumerate(historial_ediciones, 1):
                        # Formatear fecha correctamente (DD/MM/YYYY HH:MM)
                        if hasattr(fecha, 'strftime'):
                            fecha_formateada = fecha.strftime('%d/%m/%Y %H:%M')
                        elif isinstance(fecha, str):
                            try:
                                from datetime import datetime
                                fecha_obj = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
                                fecha_formateada = fecha_obj.strftime('%d/%m/%Y %H:%M')
                            except:
                                fecha_formateada = fecha
                        else:
                            fecha_formateada = str(fecha)
                        
                        historial_text.insert('end', f"📝 EDICIÓN #{len(historial_ediciones) - i + 1}\n", 'titulo')
                        historial_text.insert('end', f"👤 Usuario: {usuario}\n", 'usuario')
                        historial_text.insert('end', f"🕒 Fecha: {fecha_formateada}\n", 'fecha')
                        historial_text.insert('end', f"🔧 Cambios realizados:\n", 'subtitulo')
                        
                        # Mostrar cada cambio en una línea separada
                        cambios_lista = cambios.split('; ')
                        for cambio in cambios_lista:
                            if cambio.strip():
                                historial_text.insert('end', f"   • {cambio.strip()}\n", 'cambios')
                        
                        historial_text.insert('end', "\n", 'espacio')
                    
                    # Configurar tags para colores
                    historial_text.tag_configure('titulo', font=('Segoe UI', 12, 'bold'), foreground='#2E5090')
                    historial_text.tag_configure('usuario', font=('Segoe UI', 10, 'bold'), foreground='#27ae60')
                    historial_text.tag_configure('fecha', font=('Segoe UI', 10), foreground='#7f8c8d')
                    historial_text.tag_configure('subtitulo', font=('Segoe UI', 10, 'bold'), foreground='#e67e22')
                    historial_text.tag_configure('cambios', font=('Segoe UI', 10), foreground='#2c3e50')
                    historial_text.tag_configure('espacio', font=('Segoe UI', 10), foreground='#f0f2f5')
                    
                    historial_text.config(state='disabled')
                    
                    # Botón cerrar
                    tk.Button(main_frame, text="Cerrar", command=ventana_historial.destroy,
                              font=('Segoe UI', 10, 'bold'), fg='white', bg='#3498db',
                              relief='flat', padx=20, pady=5).pack()
                
                # Botón para ver historial completo
                btn_historial = tk.Button(ultimo_editor_frame, text="Ver historial completo", 
                                        command=mostrar_historial_completo,
                                        font=('Segoe UI', 9), fg='white', bg='#2E5090',
                                        relief='flat', padx=15, pady=3, cursor='hand2')
                btn_historial.grid(row=1, column=0, columnspan=2, sticky='w', pady=(10, 0))
        
        # SECCIÓN 4 - Información Adicional
        adicional_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        adicional_frame.pack(fill='x', pady=(0, 15), padx=10)
        
        # Título de sección
        ttk.Label(adicional_frame, text="INFORMACIÓN ADICIONAL", style='Section.TLabel').pack(anchor='w', padx=20, pady=(15, 10))
        
        # Contenido adicional
        adicional_content = ttk.Frame(adicional_frame, style='Card.TFrame')
        adicional_content.pack(fill='x', padx=25, pady=(0, 15))
        
        # Observaciones (puede ser largo, usar frame separado)
        ttk.Label(adicional_content, text="Observaciones:", style='Info.TLabel').pack(anchor='w', pady=(0, 5))
        
        # Frame para el área de observaciones con scrollbar visible
        observaciones_frame = tk.Frame(adicional_content, bg='white')
        observaciones_frame.pack(fill='x', pady=(0, 10))
        
        # Área de texto con altura optimizada para mostrar más contenido
        observaciones_text = tk.Text(observaciones_frame, height=10, wrap='word', 
                                   font=('Segoe UI', 10), relief='solid', bd=2,
                                   bg='#f8f9fa', fg='#2c3e50', padx=15, pady=15)
        observaciones_text.pack(side='left', fill='both', expand=True)
        
        # Scrollbar siempre visible y prominente
        observaciones_scrollbar = tk.Scrollbar(observaciones_frame, orient='vertical', 
                                             command=observaciones_text.yview,
                                             width=20, bg='#2E5090', troughcolor='#e8e8e8',
                                             activebackground='#1a3a6b', relief='raised', bd=2)
        observaciones_scrollbar.pack(side='right', fill='y', padx=(8, 0))
        
        # Configurar el scroll
        observaciones_text.configure(yscrollcommand=observaciones_scrollbar.set)
        
        # Insertar contenido
        observaciones_text.insert('1.0', str(postulante_completo[15] or 'Sin observaciones'))
        observaciones_text.config(state='disabled')
        
        # Forzar actualización del scroll después de insertar contenido
        observaciones_text.update_idletasks()
        observaciones_text.see('1.0')  # Ir al inicio
        
        # Botones de acción
        button_frame = ttk.Frame(scrollable_frame, style='Details.TFrame')
        button_frame.pack(fill='x', pady=(20, 0), padx=10)
        
        # Botones con estilo moderno
        edit_button = ttk.Button(button_frame, text="✏️ Editar", 
                                command=lambda: self.edit_postulante(values),
                                style='Accent.TButton')
        edit_button.pack(side='left', padx=(0, 10), pady=10)
        
        delete_button = ttk.Button(button_frame, text="🗑️ Eliminar", 
                                  command=lambda: self.delete_postulante(values),
                                  style='Accent.TButton')
        delete_button.pack(side='left', padx=(0, 10), pady=10)
        
        close_button = ttk.Button(button_frame, text="✖️ Cerrar", 
                                 command=details_window.destroy,
                                 style='Accent.TButton')
        close_button.pack(side='left', pady=10)
        
        # Configurar scroll con mouse
        def _on_mousewheel(event):
            try:
                main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                # Si el canvas ya no existe, limpiar el binding
                details_window.unbind_all("<MouseWheel>")
        
        details_window.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Limpiar binding cuando se cierre la ventana
        def on_closing():
            try:
                details_window.unbind_all("<MouseWheel>")
                details_window.unbind_all("<Key>")
            except:
                pass
            details_window.destroy()
        
        details_window.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Configurar tamaño con ancho ajustable y altura fija
        details_window.update_idletasks()
        
        # Calcular el ancho necesario basado en el contenido
        content_width = scrollable_frame.winfo_reqwidth() + 120  # Agregar más espacio para scrollbar y padding
        max_width = min(content_width, 1440)  # Aumentar máximo a 1440px de ancho
        min_width = 700  # Aumentar mínimo a 700px de ancho
        final_width = max(min_width, max_width)
        
        # Altura fija
        max_height = 600
        
        # Aplicar el tamaño
        details_window.geometry(f"{final_width}x{max_height}")
        
        # Centrar la ventana
        x = (details_window.winfo_screenwidth() // 2) - (final_width // 2)
        y = (details_window.winfo_screenheight() // 2) - (max_height // 2)
        details_window.geometry(f"{final_width}x{max_height}+{x}+{y}")
        
        # Configurar scroll para que funcione correctamente
        def configure_scroll(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", configure_scroll)
        
        # Configurar el canvas para que se expanda correctamente
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        # Asegurar que el scroll funcione con el mouse
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Vincular el scroll del mouse al canvas
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Configurar el scroll para que funcione con las teclas
        def _on_key_press(event):
            try:
                if event.keysym == "Up":
                    main_canvas.yview_scroll(-1, "units")
                elif event.keysym == "Down":
                    main_canvas.yview_scroll(1, "units")
                elif event.keysym == "Page_Up":
                    main_canvas.yview_scroll(-1, "pages")
                elif event.keysym == "Page_Down":
                    main_canvas.yview_scroll(1, "pages")
            except tk.TclError:
                # Si el canvas ya no existe, limpiar el binding
                details_window.unbind_all("<Key>")
        
        details_window.bind_all("<Key>", _on_key_press)
        
    def edit_postulante(self, values):
        """Editar postulante con optimización"""
        try:
            postulante_id = values[0]
            
            # Verificar privilegios para editar
            from privilegios_utils import puede_editar_postulante
            from database import obtener_postulante_por_id
            
            # Obtener datos completos del postulante para verificar permisos
            postulante_data = obtener_postulante_por_id(postulante_id)
            if not postulante_data:
                messagebox.showerror("Error", "No se pudo obtener la información del postulante")
                return
            
            # Crear diccionario con datos del postulante para verificación
            postulante_dict = {
                'id': postulante_data[0],
                'usuario_registrador': postulante_data[7]  # usuario_registrador
            }
            
            # Verificar si puede editar este postulante
            if not puede_editar_postulante(self.user_data, postulante_dict):
                return
            
            # Obtener la ventana raíz correcta
            root_window = self.winfo_toplevel()
            
            # Crear callback para actualizar solo la fila específica
            def on_edit_complete(updated_data=None):
                if updated_data:
                    # Actualizar solo la fila específica en la tabla
                    self.update_single_row(postulante_id, updated_data)
                else:
                    # Si no hay datos actualizados, recargar solo la página actual
                    self.refresh_current_page()
            
            EditarPostulante(root_window, self.user_data, postulante_id, callback=on_edit_complete)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al editar postulante: {e}")
        
    def delete_postulante(self, values):
        """Eliminar postulante con optimización"""
        try:
            postulante_id = values[0]
            nombre = values[1]
            apellido = values[2]
            
            # Verificar privilegios para eliminar
            from privilegios_utils import puede_eliminar_postulante
            from database import obtener_postulante_por_id
            
            # Obtener datos completos del postulante para verificar permisos
            postulante_data = obtener_postulante_por_id(postulante_id)
            if not postulante_data:
                messagebox.showerror("Error", "No se pudo obtener la información del postulante")
                return
            
            # Crear diccionario con datos del postulante para verificación
            postulante_dict = {
                'id': postulante_data[0],
                'usuario_registrador': postulante_data[7]  # usuario_registrador
            }
            
            # Verificar si puede eliminar este postulante
            if not puede_eliminar_postulante(self.user_data, postulante_dict):
                return
            
            # Confirmar eliminación
            result = messagebox.askyesno(
                "Confirmar Eliminación",
                f"¿Está seguro de que desea eliminar al postulante:\n\n{nombre} {apellido}\n\nEsta acción no se puede deshacer."
            )
            
            if result:
                if eliminar_postulante(postulante_id):
                    messagebox.showinfo("Éxito", "Postulante eliminado correctamente")
                    # Remover solo la fila específica y actualizar contadores
                    self.remove_single_row(postulante_id)
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el postulante")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar postulante: {e}")
    
    def update_single_row(self, postulante_id, updated_data):
        """Actualizar solo una fila específica en la tabla"""
        try:
            # Buscar la fila en la tabla actual
            for item in self.tree.get_children():
                if self.tree.item(item)['values'][0] == postulante_id:
                    # Actualizar los valores de la fila
                    current_values = list(self.tree.item(item)['values'])
                    
                    # Actualizar con los nuevos datos
                    if 'nombre' in updated_data:
                        current_values[1] = updated_data['nombre']
                    if 'apellido' in updated_data:
                        current_values[2] = updated_data['apellido']
                    if 'cedula' in updated_data:
                        current_values[3] = updated_data['cedula']
                    if 'unidad' in updated_data:
                        current_values[4] = updated_data['unidad']
                    if 'dedo_registrado' in updated_data:
                        current_values[5] = updated_data['dedo_registrado']
                    
                    # Actualizar la fila en la tabla
                    self.tree.item(item, values=current_values)
                    break
                    
        except Exception as e:
            print(f"Error al actualizar fila: {e}")
            # Fallback: recargar solo la página actual
            self.refresh_current_page()
    
    def remove_single_row(self, postulante_id):
        """Remover solo una fila específica de la tabla"""
        try:
            # Buscar y remover la fila de la tabla
            for item in self.tree.get_children():
                if self.tree.item(item)['values'][0] == postulante_id:
                    self.tree.delete(item)
                    break
            
            # Actualizar contadores
            self.total_items -= 1
            
            # Recalcular paginación
            total_pages = (self.total_items + self.items_per_page - 1) // self.items_per_page
            
            # Si la página actual está vacía y no es la primera, ir a la página anterior
            if self.current_page > total_pages and self.current_page > 1:
                self.current_page = total_pages
            
            # Actualizar información de paginación
            self.update_pagination()
            
        except Exception as e:
            print(f"Error al remover fila: {e}")
            # Fallback: recargar solo la página actual
            self.refresh_current_page()
    
    def refresh_current_page(self):
        """Recargar solo la página actual sin cargar todos los datos"""
        try:
            # Calcular el rango de la página actual
            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = start_idx + self.items_per_page
            
            # Obtener solo los datos de la página actual
            from database import get_postulantes
            page_data = get_postulantes(limit=self.items_per_page, offset=start_idx)
            
            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Cargar solo los datos de la página actual
            for postulante in page_data:
                self.tree.insert('', 'end', values=postulante)
            
            # Actualizar información de paginación
            self.update_pagination()
            
        except Exception as e:
            print(f"Error al refrescar página: {e}")
            # Fallback: recargar todo
            self.load_postulantes()

def main():
    """Función principal para pruebas"""
    root = tk.Tk()
    root.withdraw()
    
    # Datos de usuario de prueba
    user_data = {
        'id': 1,
        'usuario': 'admin',
        'rol': 'admin',
        'nombre': 'Administrador',
        'apellido': 'Sistema'
    }
    
    app = ListaPostulantes(root, user_data)
    root.mainloop()

if __name__ == "__main__":
    main() 