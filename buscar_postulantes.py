#!/usr/bin/env python3
"""
Módulo para buscar postulantes en el sistema
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import buscar_postulante, eliminar_postulante, get_postulantes, obtener_postulante_por_id, obtener_nombre_registrador, obtener_nombre_aparato
from editar_postulante import EditarPostulante

class BuscarPostulantes(tk.Toplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.parent = parent
        self.user_data = user_data
        
        # Variables de paginación
        self.current_page = 1
        self.items_per_page = 20
        self.total_items = 0
        self.all_postulantes = []
        
        self.title("Buscar Postulantes")
        self.geometry('')
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        # Configurar estilos modernos
        self.setup_styles()
        self.setup_ui()
        self.center_window()
        
    def setup_styles(self):
        """Configurar estilos modernos"""
        style = ttk.Style()
        
        # Colores modernos
        primary_color = '#2c3e50'
        secondary_color = '#34495e'
        accent_color = '#3498db'
        light_gray = '#ecf0f1'
        dark_gray = '#7f8c8d'
        
        # Estilos personalizados
        style.configure('Modern.TFrame', background=light_gray)
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 16, 'bold'), 
                       foreground=primary_color,
                       background=light_gray)
        style.configure('Subtitle.TLabel', 
                       font=('Segoe UI', 11), 
                       foreground=secondary_color,
                       background=light_gray)
        style.configure('Info.TLabel', 
                       font=('Segoe UI', 9), 
                       foreground=dark_gray,
                       background=light_gray)
        style.configure('Modern.TButton', 
                       font=('Segoe UI', 9, 'bold'),
                       padding=(15, 8))
        style.configure('Search.TLabelframe', 
                       background=light_gray,
                       relief='flat')
        style.configure('Search.TLabelframe.Label', 
                       font=('Segoe UI', 11, 'bold'),
                       foreground=primary_color,
                       background=light_gray)
        
    def setup_ui(self):
        """Configurar la interfaz"""
        # Frame principal con color de fondo
        main_frame = ttk.Frame(self, style='Modern.TFrame', padding=25)
        main_frame.pack(expand=True, fill='both')
        
        # Título principal
        title_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        title_frame.pack(fill='x', pady=(0, 25))
        
        title_label = ttk.Label(title_frame, text="Buscar Postulantes", style='Title.TLabel')
        title_label.pack(side='left')
        
        # Frame de búsqueda
        search_frame = ttk.LabelFrame(main_frame, text="Criterios de Búsqueda", 
                                     style='Search.TLabelframe', padding=20)
        search_frame.pack(fill='x', pady=(0, 25))
        
        # Variables de búsqueda
        self.search_type = tk.StringVar(value="cedula")
        self.search_term = tk.StringVar()
        
        # Crear controles de búsqueda
        self.create_search_controls(search_frame)
        
        # Frame de resultados
        results_frame = ttk.LabelFrame(main_frame, text="Resultados", 
                                      style='Search.TLabelframe', padding=20)
        results_frame.pack(fill='both', expand=True)
        
        # Crear tabla de resultados
        self.create_results_table(results_frame)
        
        # Crear controles de paginación
        self.create_pagination_controls(results_frame)
        
    def create_search_controls(self, parent):
        """Crear controles de búsqueda con diseño mejorado"""
        # Grid principal
        grid_frame = ttk.Frame(parent, style='Modern.TFrame')
        grid_frame.pack(fill='x')
        
        # Tipo de búsqueda
        ttk.Label(grid_frame, text="Buscar por:", style='Subtitle.TLabel').grid(
            row=0, column=0, sticky='w', pady=(0, 10))
        
        search_type_frame = ttk.Frame(grid_frame, style='Modern.TFrame')
        search_type_frame.grid(row=0, column=1, padx=(15, 0), pady=(0, 10), sticky='w')
        
        ttk.Radiobutton(search_type_frame, text="Cédula", variable=self.search_type, 
                       value="cedula", command=self.on_search_type_change).pack(side='left', padx=(0, 15))
        ttk.Radiobutton(search_type_frame, text="Nombre", variable=self.search_type, 
                       value="nombre", command=self.on_search_type_change).pack(side='left')
        
        # Campo de búsqueda
        ttk.Label(grid_frame, text="Término de búsqueda:", style='Subtitle.TLabel').grid(
            row=1, column=0, sticky='w', pady=(0, 10))
        
        self.search_entry = ttk.Entry(grid_frame, textvariable=self.search_term, 
                                     font=('Segoe UI', 10), width=45)
        self.search_entry.grid(row=1, column=1, padx=(15, 0), pady=(0, 10), sticky='ew')
        
        # Botones con mejor espaciado (sin "Ver Todos")
        button_frame = ttk.Frame(grid_frame, style='Modern.TFrame')
        button_frame.grid(row=2, column=0, columnspan=2, pady=(15, 0))
        
        ttk.Button(button_frame, text="Buscar", style='Modern.TButton',
                  command=self.search_postulantes).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Limpiar", style='Modern.TButton',
                  command=self.clear_search).pack(side='left')
        
        # Configurar grid
        grid_frame.columnconfigure(1, weight=1)
        
        # Configurar eventos
        self.search_entry.bind('<Return>', lambda e: self.search_postulantes())
        
    def create_results_table(self, parent):
        """Crear tabla de resultados con diseño mejorado"""
        # Frame para tabla y scrollbar
        table_frame = ttk.Frame(parent, style='Modern.TFrame')
        table_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Crear Treeview con estilos modernos (cambiar ID por Aparato)
        columns = ('Aparato', 'Nombre', 'Apellido', 'Cédula', 'Teléfono', 'Fecha Registro')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas con mejor formato
        self.tree.heading('Aparato', text='Aparato Biométrico - Dedo')
        self.tree.heading('Nombre', text='Nombre')
        self.tree.heading('Apellido', text='Apellido')
        self.tree.heading('Cédula', text='Cédula')
        self.tree.heading('Teléfono', text='Teléfono')
        self.tree.heading('Fecha Registro', text='Fecha Registro')
        
        # Configurar anchos de columna optimizados
        self.tree.column('Aparato', width=180, minwidth=150)
        self.tree.column('Nombre', width=150, minwidth=120)
        self.tree.column('Apellido', width=150, minwidth=120)
        self.tree.column('Cédula', width=120, minwidth=100, anchor='center')
        self.tree.column('Teléfono', width=120, minwidth=100, anchor='center')
        self.tree.column('Fecha Registro', width=140, minwidth=120, anchor='center')
        
        # Scrollbar moderno
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar con mejor distribución
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Configurar eventos
        self.tree.bind('<Double-1>', self.on_item_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        # Frame de información con mejor diseño
        info_frame = ttk.Frame(parent, style='Modern.TFrame')
        info_frame.pack(fill='x')
        
        self.info_label = ttk.Label(info_frame, text="Ingrese criterios de búsqueda para comenzar", 
                                   style='Info.TLabel')
        self.info_label.pack(side='left')
        
    def create_pagination_controls(self, parent):
        """Crear controles de paginación"""
        pagination_frame = ttk.Frame(parent, style='Modern.TFrame')
        pagination_frame.pack(fill='x', pady=(10, 0))
        
        # Botones de navegación
        self.prev_button = ttk.Button(pagination_frame, text="Anterior", 
                                     command=self.previous_page, state='disabled')
        self.prev_button.pack(side='left', padx=(0, 10))
        
        # Información de página
        self.page_info = ttk.Label(pagination_frame, text="", style='Info.TLabel')
        self.page_info.pack(side='left', padx=10)
        
        self.next_button = ttk.Button(pagination_frame, text="Siguiente", 
                                     command=self.next_page, state='disabled')
        self.next_button.pack(side='left', padx=(10, 0))
        
        # Selector de elementos por página
        ttk.Label(pagination_frame, text="Elementos por página:", 
                 style='Info.TLabel').pack(side='right', padx=(0, 10))
        
        self.items_per_page_var = tk.StringVar(value="20")
        items_combo = ttk.Combobox(pagination_frame, textvariable=self.items_per_page_var, 
                                  values=["10", "20", "50", "100"], width=8, state='readonly')
        items_combo.pack(side='right')
        items_combo.bind('<<ComboboxSelected>>', self.on_items_per_page_change)
        
    def center_window(self):
        """Centrar la ventana"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def on_search_type_change(self):
        """Manejar cambio de tipo de búsqueda"""
        self.search_entry.delete(0, tk.END)
        self.search_entry.focus()
            
    def search_postulantes(self):
        """Buscar postulantes con paginación"""
        search_term = self.search_term.get().strip()
        search_type = self.search_type.get()
        
        if not search_term:
            messagebox.showwarning("Advertencia", "Por favor ingrese un término de búsqueda")
            return
            
        # Realizar búsqueda
        if search_type == "cedula":
            self.all_postulantes = buscar_postulante(cedula=search_term)
        else:
            self.all_postulantes = buscar_postulante(nombre=search_term)
            
        self.total_items = len(self.all_postulantes)
        self.current_page = 1
        self.update_pagination()
        self.display_current_page()
        
        # Mostrar mensaje si no hay resultados
        if self.total_items == 0:
            messagebox.showinfo("Sin resultados", 
                              f"No se encontraron postulantes con {search_type} '{search_term}'.\n\n"
                              "Sugerencias:\n"
                              "• Verifique que el término esté escrito correctamente\n"
                              "• Intente con términos más cortos\n"
                              "• Use solo números para cédula\n"
                              "• Use solo letras para nombre")
            
    def clear_search(self):
        """Limpiar búsqueda"""
        self.search_term.set("")
        self.all_postulantes = []
        self.total_items = 0
        self.current_page = 1
        self.update_pagination()
        self.display_current_page()
        self.info_label.config(text="Ingrese criterios de búsqueda para comenzar")
        
    def display_current_page(self):
        """Mostrar la página actual"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not self.all_postulantes:
            self.info_label.config(text="No se encontraron postulantes")
            return
            
        # Calcular índices de la página actual
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_items = self.all_postulantes[start_idx:end_idx]
        
        # Mostrar elementos de la página actual
        for postulante in page_items:
            fecha_registro = postulante[6].strftime('%d/%m/%Y') if postulante[6] else 'N/A'
            
            # Obtener nombre del aparato biométrico y dedo
            # Los índices están basados en la consulta de buscar_postulante:
            # id, nombre, apellido, cedula, fecha_nacimiento, telefono, fecha_registro, 
            # usuario_registrador, registrado_por, aparato_id, dedo_registrado, usuario_ultima_edicion, fecha_ultima_edicion
            
            aparato_id = postulante[9]  # aparato_id está en la posición 9
            nombre_aparato = obtener_nombre_aparato(aparato_id)
            dedo_registrado = postulante[10] or 'N/A'  # dedo_registrado está en la posición 10
            aparato_dedo = f"{nombre_aparato} - {dedo_registrado}"
            
            self.tree.insert('', 'end', values=(
                aparato_dedo,  # Aparato biométrico - Dedo
                postulante[1],  # Nombre
                postulante[2],  # Apellido
                postulante[3],  # Cédula
                postulante[5] or 'N/A',  # Teléfono
                fecha_registro
            ))
            
        # Actualizar información
        total_pages = (self.total_items + self.items_per_page - 1) // self.items_per_page
        self.info_label.config(text=f"Mostrando {len(page_items)} de {self.total_items} postulante(s) - Página {self.current_page} de {total_pages}")
        
    def update_pagination(self):
        """Actualizar controles de paginación"""
        total_pages = (self.total_items + self.items_per_page - 1) // self.items_per_page
        
        # Actualizar botones
        self.prev_button.config(state='normal' if self.current_page > 1 else 'disabled')
        self.next_button.config(state='normal' if self.current_page < total_pages else 'disabled')
        
        # Actualizar información de página
        if total_pages > 0:
            self.page_info.config(text=f"Página {self.current_page} de {total_pages}")
        else:
            self.page_info.config(text="Sin resultados")
            
    def previous_page(self):
        """Ir a la página anterior"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_pagination()
            self.display_current_page()
            
    def next_page(self):
        """Ir a la página siguiente"""
        total_pages = (self.total_items + self.items_per_page - 1) // self.items_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_pagination()
            self.display_current_page()
            
    def on_items_per_page_change(self, event=None):
        """Manejar cambio en elementos por página"""
        try:
            self.items_per_page = int(self.items_per_page_var.get())
            self.current_page = 1
            self.update_pagination()
            self.display_current_page()
        except ValueError:
            pass
        
    def on_item_double_click(self, event):
        """Manejar doble clic en un elemento"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.show_postulante_details(item['values'])
            
    def show_context_menu(self, event):
        """Mostrar menú contextual"""
        selection = self.tree.selection()
        if selection:
            # Crear menú contextual
            context_menu = tk.Menu(self, tearoff=0)
            context_menu.add_command(label="Ver Detalles", 
                                   command=lambda: self.show_postulante_details(
                                       self.tree.item(selection[0])['values']))
            context_menu.add_command(label="Editar", 
                                   command=lambda: self.edit_postulante(
                                       self.tree.item(selection[0])['values']))
            context_menu.add_separator()
            context_menu.add_command(label="Eliminar", 
                                   command=lambda: self.delete_postulante(
                                       self.tree.item(selection[0])['values']))
            
            # Mostrar menú
            context_menu.tk_popup(event.x_root, event.y_root)
            
    def show_postulante_details(self, values):
        """Mostrar detalles del postulante con interfaz moderna y estética"""
        if not values:
            return
            
        # Obtener información completa del postulante
        postulante_id = None
        for postulante in self.all_postulantes:
            if (postulante[1] == values[1] and  # nombre
                postulante[2] == values[2] and  # apellido
                postulante[3] == values[3]):    # cédula
                postulante_id = postulante[0]
                break
        
        if not postulante_id:
            # Intentar buscar por cédula directamente en la base de datos
            from database import buscar_postulante
            # Convertir cédula a string para evitar errores de tipo
            cedula_str = str(values[3]) if values[3] is not None else ""
            resultados = buscar_postulante(cedula=cedula_str)
            if resultados:
                postulante_id = resultados[0][0]  # Tomar el primer resultado
            else:
                messagebox.showerror("Error", "No se pudo obtener la información completa del postulante")
                return
            
        # Obtener datos completos del postulante
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
        
        # UID K40 (si existe)
        if postulante_completo[13]:  # uid_k40
            ttk.Label(registro_content, text="UID K40:", style='Info.TLabel').grid(row=2, column=0, sticky='w', padx=(0, 10), pady=5)
            ttk.Label(registro_content, text=str(postulante_completo[13]), style='Value.TLabel').grid(row=2, column=1, sticky='w', pady=5)
        
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
        
        # SECCIÓN 3 - Información de Última Edición (solo si existe)
        if postulante_completo[16] and postulante_completo[16].strip():
            edicion_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
            edicion_frame.pack(fill='x', pady=(0, 15), padx=10)
            
            # Título de sección
            ttk.Label(edicion_frame, text="INFORMACIÓN DE ÚLTIMA EDICIÓN", style='Section.TLabel').pack(anchor='w', padx=20, pady=(15, 10))
            
            # Contenido de edición
            edicion_content = ttk.Frame(edicion_frame, style='Card.TFrame')
            edicion_content.pack(fill='x', padx=25, pady=(0, 15))
            
            edicion_content.columnconfigure(1, weight=1, minsize=200)
            edicion_content.columnconfigure(3, weight=1, minsize=200)
            
            # Usuario que editó
            ttk.Label(edicion_content, text="Editado por:", style='Info.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
            ttk.Label(edicion_content, text=postulante_completo[16], style='Value.TLabel').grid(row=0, column=1, sticky='w', pady=5)
            
            # Fecha de edición
            ttk.Label(edicion_content, text="Fecha de Edición:", style='Info.TLabel').grid(row=0, column=2, sticky='w', padx=(20, 10), pady=5)
            ttk.Label(edicion_content, text=fecha_ultima_edicion, style='Value.TLabel').grid(row=0, column=3, sticky='w', pady=5)
        
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
        
        observaciones_text = tk.Text(adicional_content, height=4, wrap='word', 
                                   font=('Segoe UI', 10), relief='flat', 
                                   bg='#f8f9fa', fg='#2c3e50', padx=10, pady=10)
        observaciones_text.pack(fill='x', pady=(0, 10))
        observaciones_text.insert('1.0', str(postulante_completo[15] or 'Sin observaciones'))
        observaciones_text.config(state='disabled')
        
        # Botón de cerrar
        button_frame = ttk.Frame(scrollable_frame, style='Details.TFrame')
        button_frame.pack(fill='x', pady=(20, 0), padx=10)
        
        close_button = ttk.Button(button_frame, text="Cerrar", 
                                 command=details_window.destroy,
                                 style='Accent.TButton')
        close_button.pack(pady=10)
        
        # Configurar scroll con mouse
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Limpiar binding cuando se cierre la ventana
        def on_closing():
            main_canvas.unbind_all("<MouseWheel>")
            details_window.destroy()
        
        details_window.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Configurar tamaño con ancho ajustable y altura fija
        details_window.update_idletasks()
        
        # Calcular el ancho necesario basado en el contenido
        content_width = scrollable_frame.winfo_reqwidth() + 120  # Agregar más espacio para scrollbar y padding
        max_width = min(content_width, 1440)  # Aumentar máximo a 1100px de ancho
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
            if event.keysym == "Up":
                main_canvas.yview_scroll(-1, "units")
            elif event.keysym == "Down":
                main_canvas.yview_scroll(1, "units")
            elif event.keysym == "Page_Up":
                main_canvas.yview_scroll(-1, "pages")
            elif event.keysym == "Page_Down":
                main_canvas.yview_scroll(1, "pages")
        
        main_canvas.bind_all("<Key>", _on_key_press)
        
    def edit_postulante(self, values):
        """Editar postulante"""
        if not values:
            return
        
        # Verificar privilegios para editar
        from privilegios_utils import puede_editar_postulante
        from database import obtener_postulante_por_id
        
        # Obtener datos del postulante para verificar permisos
        postulante_id = None
        for postulante in self.all_postulantes:
            if (postulante[1] == values[1] and  # nombre
                postulante[2] == values[2] and  # apellido
                postulante[3] == values[3]):    # cédula
                postulante_id = postulante[0]
                break
        
        if not postulante_id:
            # Intentar buscar por cédula directamente en la base de datos
            from database import buscar_postulante
            # Convertir cédula a string para evitar errores de tipo
            cedula_str = str(values[3]) if values[3] is not None else ""
            resultados = buscar_postulante(cedula=cedula_str)
            if resultados:
                postulante_id = resultados[0][0]  # Tomar el primer resultado
            else:
                messagebox.showerror("Error", "No se pudo identificar el postulante")
                return
        
        # Obtener datos completos del postulante
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
            
        # Encontrar el ID del postulante
        postulante_id = None
        for postulante in self.all_postulantes:
            if (postulante[1] == values[1] and  # nombre
                postulante[2] == values[2] and  # apellido
                postulante[3] == values[3]):    # cédula
                postulante_id = postulante[0]
                break
        
        if not postulante_id:
            # Intentar buscar por cédula directamente en la base de datos
            from database import buscar_postulante
            # Convertir cédula a string para evitar errores de tipo
            cedula_str = str(values[3]) if values[3] is not None else ""
            resultados = buscar_postulante(cedula=cedula_str)
            if resultados:
                postulante_id = resultados[0][0]  # Tomar el primer resultado
            else:
                messagebox.showerror("Error", "No se pudo identificar el postulante")
                return
        
        # Abrir ventana de edición
        edit_window = EditarPostulante(self, self.user_data, postulante_id)
        
        # Esperar a que se cierre la ventana de edición
        self.wait_window(edit_window)
        
        # Actualizar la lista después de editar
        self.refresh_results()
        
    def delete_postulante(self, values):
        """Eliminar postulante"""
        if not values:
            return
        
        # Verificar privilegios para eliminar
        from privilegios_utils import puede_eliminar_postulante
        from database import obtener_postulante_por_id
        
        # Obtener datos del postulante para verificar permisos
        postulante_id = None
        for postulante in self.all_postulantes:
            if (postulante[1] == values[1] and  # nombre
                postulante[2] == values[2] and  # apellido
                postulante[3] == values[3]):    # cédula
                postulante_id = postulante[0]
                break
        
        if not postulante_id:
            # Intentar buscar por cédula directamente en la base de datos
            from database import buscar_postulante
            # Convertir cédula a string para evitar errores de tipo
            cedula_str = str(values[3]) if values[3] is not None else ""
            resultados = buscar_postulante(cedula=cedula_str)
            if resultados:
                postulante_id = resultados[0][0]  # Tomar el primer resultado
            else:
                messagebox.showerror("Error", "No se pudo identificar el postulante")
                return
        
        # Obtener datos completos del postulante
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
            
        # Encontrar el ID del postulante
        postulante_id = None
        for postulante in self.all_postulantes:
            if (postulante[1] == values[1] and  # nombre
                postulante[2] == values[2] and  # apellido
                postulante[3] == values[3]):    # cédula
                postulante_id = postulante[0]
                break
        
        if not postulante_id:
            # Intentar buscar por cédula directamente en la base de datos
            from database import buscar_postulante
            # Convertir cédula a string para evitar errores de tipo
            cedula_str = str(values[3]) if values[3] is not None else ""
            resultados = buscar_postulante(cedula=cedula_str)
            if resultados:
                postulante_id = resultados[0][0]  # Tomar el primer resultado
            else:
                messagebox.showerror("Error", "No se pudo identificar el postulante")
                return
            
        nombre = values[1]
        apellido = values[2]
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar Eliminación", 
                              f"¿Está seguro de eliminar al postulante {nombre} {apellido}?\n\n"
                              "Esta acción no se puede deshacer."):
            
            # Intentar eliminar
            if eliminar_postulante(postulante_id):
                messagebox.showinfo("Éxito", f"Postulante {nombre} {apellido} eliminado correctamente.")
                # Actualizar la lista
                self.refresh_results()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el postulante.")
                
    def refresh_results(self):
        """Actualizar los resultados de la tabla"""
        # Obtener el término de búsqueda actual
        search_term = self.search_term.get().strip()
        search_type = self.search_type.get()
        
        # Realizar búsqueda nuevamente
        if search_term:
            if search_type == "cedula":
                self.all_postulantes = buscar_postulante(cedula=search_term)
            else:
                self.all_postulantes = buscar_postulante(nombre=search_term)
        else:
            # Si no hay término de búsqueda, mostrar todos
            self.all_postulantes = get_postulantes()
            
        self.total_items = len(self.all_postulantes)
        self.current_page = 1
        self.update_pagination()
        self.display_current_page()

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
    
    app = BuscarPostulantes(root, user_data)
    root.mainloop()

if __name__ == "__main__":
    main() 