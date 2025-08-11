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
        
        # Variables de paginación
        self.current_page = 1
        self.items_per_page = 10
        self.total_items = 0
        self.total_pages = 0
        self.all_postulantes = []
        self.filtered_postulantes = []
        
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
        self.tree.bind('<Button-3>', self.show_context_menu)
        
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
        """Cargar postulantes desde la base de datos"""
        try:
            print("DEBUG: Iniciando carga de postulantes...")
            
            # Obtener postulantes
            self.all_postulantes = get_postulantes()
            self.filtered_postulantes = self.all_postulantes.copy()
            
            print(f"DEBUG: Cargados {len(self.all_postulantes)} postulantes")
            
            # Cargar opciones de filtro
            self.load_filter_options()
            
            # Aplicar filtros y paginación
            self.apply_filters()
            
            # Asegurar que la paginación se actualice
            print("DEBUG: Actualizando paginación...")
            self.update_pagination()
            
            print("DEBUG: Carga de postulantes completada")
                
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
        """Actualizar información de paginación"""
        self.total_items = len(self.filtered_postulantes)
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
        """Mostrar la página actual de postulantes"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not self.filtered_postulantes:
            return
            
        # Calcular índices de la página actual
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.filtered_postulantes))
        
        # Mostrar postulantes de la página actual
        for i in range(start_idx, end_idx):
            postulante = self.filtered_postulantes[i]
            
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
            
    def show_context_menu(self, event):
        """Mostrar menú contextual"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            
            # Crear menú contextual
            context_menu = tk.Menu(self, tearoff=0)
            context_menu.add_command(label="Ver Detalles", command=lambda: self.show_postulante_details(values))
            context_menu.add_command(label="Editar", command=lambda: self.edit_postulante(values))
            context_menu.add_separator()
            context_menu.add_command(label="Eliminar", command=lambda: self.delete_postulante(values))
            
            # Mostrar menú en posición del mouse
            context_menu.tk_popup(event.x_root, event.y_root)
            
    def show_postulante_details(self, values):
        """Mostrar detalles del postulante"""
        try:
            postulante_id = values[0]
            
            # Obtener datos completos del postulante
            conn = connect_db()
            if not conn:
                return
                
                cursor = conn.cursor()
                cursor.execute("""
                SELECT id, nombre, apellido, cedula, fecha_nacimiento, 
                       telefono, fecha_registro, usuario_registrador, id_k40, 
                       huella_dactilar, observaciones, edad, unidad, dedo_registrado, 
                       registrado_por, aparato_id, uid_k40, usuario_ultima_edicion, 
                       fecha_ultima_edicion
                FROM postulantes 
                WHERE id = %s
                """, (postulante_id,))
            
                postulante = cursor.fetchone()
                conn.close()
                
                if postulante:
                    # Crear ventana de detalles
                    details_window = tk.Toplevel(self)
                    details_window.title(f"Detalles del Postulante - {postulante[1]} {postulante[2]}")
                    details_window.geometry("600x500")
                    details_window.resizable(True, True)
                    details_window.transient(self)
                    details_window.grab_set()
                    
                # Crear contenido
                main_frame = ttk.Frame(details_window, padding=20)
                main_frame.pack(expand=True, fill='both')
                
                # Título
                title_label = ttk.Label(main_frame, text=f"Detalles del Postulante", style='Title.TLabel')
                title_label.pack(pady=(0, 20))
                
                # Frame para detalles
                details_frame = ttk.LabelFrame(main_frame, text="Información Personal", padding=15)
                details_frame.pack(fill='x', pady=(0, 15))
                
                # Mostrar detalles
                details = [
                    ("ID:", postulante[0]),
                    ("Nombre:", postulante[1]),
                    ("Apellido:", postulante[2]),
                    ("Cédula:", postulante[3]),
                    ("Fecha de Nacimiento:", postulante[4].strftime('%d/%m/%Y') if postulante[4] else 'N/A'),
                    ("Teléfono:", postulante[5] or 'N/A'),
                    ("Edad:", str(postulante[11]) if postulante[11] else 'N/A'),
                    ("Unidad:", postulante[12] or 'N/A'),
                    ("Dedo Registrado:", postulante[13] or 'N/A'),
                    ("Fecha de Registro:", postulante[6].strftime('%d/%m/%Y %H:%M') if postulante[6] else 'N/A'),
                    ("Registrado por:", postulante[14] or 'N/A'),
                    ("Observaciones:", postulante[10] or 'N/A')
                ]
                
                for i, (label, value) in enumerate(details):
                    row = i // 2
                    col = (i % 2) * 2
                    
                    ttk.Label(details_frame, text=label, style='Info.TLabel').grid(row=row, column=col, sticky='w', pady=5, padx=(0, 10))
                    ttk.Label(details_frame, text=value, style='Info.TLabel').grid(row=row, column=col+1, sticky='w', pady=5)
                
                # Botones
                buttons_frame = ttk.Frame(main_frame)
                buttons_frame.pack(fill='x', pady=(20, 0))
                
                ttk.Button(buttons_frame, text="Editar", command=lambda: self.edit_postulante(values)).pack(side='left', padx=(0, 10))
                ttk.Button(buttons_frame, text="Cerrar", command=details_window.destroy).pack(side='left')
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar detalles: {e}")
        
    def edit_postulante(self, values):
        """Editar postulante"""
        try:
            postulante_id = values[0]
            EditarPostulante(self, postulante_id, self.user_data)
            # Recargar datos después de editar
            self.load_postulantes()
        except Exception as e:
            messagebox.showerror("Error", f"Error al editar postulante: {e}")
        
    def delete_postulante(self, values):
        """Eliminar postulante"""
        try:
            postulante_id = values[0]
            nombre = values[1]
            apellido = values[2]
                    
                    # Confirmar eliminación
            result = messagebox.askyesno(
                "Confirmar Eliminación",
                f"¿Está seguro de que desea eliminar al postulante:\n\n{nombre} {apellido}\n\nEsta acción no se puede deshacer."
            )
            
            if result:
                if eliminar_postulante(postulante_id):
                    messagebox.showinfo("Éxito", "Postulante eliminado correctamente")
                    self.load_postulantes()  # Recargar lista
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el postulante")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar postulante: {e}")

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