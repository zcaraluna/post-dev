#!/usr/bin/env python3
"""
Módulo para gestión de usuarios del sistema
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import get_usuarios, crear_usuario, actualizar_usuario, eliminar_usuario, obtener_usuario_por_id
import ctypes
import os

# Configurar DPI para Windows (HD/4K)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Per Monitor DPI Aware
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()  # Fallback para versiones anteriores
    except:
        pass

class GestionUsuarios(tk.Toplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.title("Gestión de Usuarios - Sistema QUIRA")
        self.geometry('')
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        # Configurar estilo moderno
        self.configure(bg='#f8f9fa')
        
        self.user_data = user_data
        self.setup_ui()
        self.load_users()
        
    def setup_ui(self):
        """Configurar la interfaz principal"""
        # Frame principal
        main_frame = tk.Frame(self, bg='#f8f9fa', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        # Cargar y mostrar imagen institucional
        self.load_institutional_image(main_frame)
        
        # Título principal
        title_frame = tk.Frame(main_frame, bg='#f8f9fa')
        title_frame.pack(fill='x', pady=(20, 30))
        
        title_label = tk.Label(title_frame, text="GESTIÓN DE USUARIOS", 
                               font=('Segoe UI', 18, 'bold'), 
                               fg='#2c3e50', bg='#f8f9fa')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Administración del Personal del Sistema", 
                                  font=('Segoe UI', 11), 
                                  fg='#6c757d', bg='#f8f9fa')
        subtitle_label.pack()
        
        # Frame de controles
        controls_frame = tk.Frame(main_frame, bg='#f8f9fa')
        controls_frame.pack(fill='x', pady=(0, 20))
        
        # Botones de acción
        button_frame = tk.Frame(controls_frame, bg='#f8f9fa')
        button_frame.pack(side='left')
        
        # Botón Nuevo Usuario
        nuevo_btn = tk.Button(button_frame, text="NUEVO USUARIO", 
                             command=self.nuevo_usuario,
                             font=('Segoe UI', 10, 'bold'),
                             fg='white', bg='#2E902E',
                             activebackground='#2E902E',
                             relief='flat', bd=0,
                             padx=20, pady=10,
                             cursor='hand2')
        nuevo_btn.pack(side='left', padx=(0, 10))
        
        # Botón Modificar
        modificar_btn = tk.Button(button_frame, text="MODIFICAR", 
                                 command=self.modificar_usuario,
                                 font=('Segoe UI', 10, 'bold'),
                                 fg='white', bg='#2E5090',
                                 activebackground='#2E5090',
                                 relief='flat', bd=0,
                                 padx=20, pady=10,
                                 cursor='hand2')
        modificar_btn.pack(side='left', padx=(0, 10))
        
        # Botón Eliminar
        eliminar_btn = tk.Button(button_frame, text="ELIMINAR", 
                                command=self.eliminar_usuario,
                                font=('Segoe UI', 10, 'bold'),
                                fg='white', bg='#902E2E',
                                activebackground='#902E2E',
                                relief='flat', bd=0,
                                padx=20, pady=10,
                                cursor='hand2')
        eliminar_btn.pack(side='left', padx=(0, 10))
        
        # Botón Actualizar
        actualizar_btn = tk.Button(button_frame, text="ACTUALIZAR", 
                                  command=self.load_users,
                                  font=('Segoe UI', 10, 'bold'),
                                  fg='white', bg='#2E5090',
                                  activebackground='#2E5090',
                                  relief='flat', bd=0,
                                  padx=20, pady=10,
                                  cursor='hand2')
        actualizar_btn.pack(side='left')
        
        # Frame de información
        info_frame = tk.Frame(controls_frame, bg='#f8f9fa')
        info_frame.pack(side='right')
        
        self.info_label = tk.Label(info_frame, text="Cargando usuarios...", 
                                   font=('Segoe UI', 10), 
                                   fg='#6c757d', bg='#f8f9fa')
        self.info_label.pack(side='right')
        
        # Frame para la tabla
        table_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        table_frame.pack(fill='both', expand=True)
        
        # Crear tabla
        self.create_table(table_frame)
        
    def load_institutional_image(self, parent):
        """Cargar y mostrar imagen institucional"""
        try:
            from PIL import Image, ImageTk
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
                os.path.join(base_path, "instituto.png"),
                os.path.join(base_path, "_internal", "instituto.png"),  # En _internal (PyInstaller)
                os.path.join(os.path.dirname(__file__), 'instituto.png'),  # Ruta original
                "instituto.png",  # Ruta relativa
            ]
            
            image_path = None
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    image_path = ruta
                    break
            
            if image_path:
                # Cargar imagen
                image = Image.open(image_path)
                
                # Redimensionar manteniendo proporción (máximo 120px de alto)
                max_height = 120
                ratio = min(max_height / image.height, 1.0)
                new_width = int(image.width * ratio)
                new_height = int(image.height * ratio)
                
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convertir para Tkinter
                photo = ImageTk.PhotoImage(image)
                
                # Crear label para la imagen
                image_label = tk.Label(parent, image=photo, bg='#f8f9fa')
                image_label.image = photo  # Mantener referencia
                image_label.pack(pady=(0, 10))
                
        except Exception as e:
            # Si hay error, simplemente continuar sin imagen
            print(f"⚠️ Error cargando imagen institucional: {e}")
            pass
        
    def create_table(self, parent):
        """Crear tabla de usuarios"""
        # Crear Treeview
        columns = ('Usuario', 'Rol', 'Nombre', 'Apellido', 'Grado', 'Cédula', 'Teléfono')
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', height=20)
        
        # Configurar encabezados
        self.tree.heading('Usuario', text='Usuario')
        self.tree.heading('Rol', text='Rol')
        self.tree.heading('Nombre', text='Nombre')
        self.tree.heading('Apellido', text='Apellido')
        self.tree.heading('Grado', text='Grado', command=self.sort_by_grado)
        self.tree.heading('Cédula', text='Cédula')
        self.tree.heading('Teléfono', text='Teléfono')
        
        # Configurar anchos de columna
        self.tree.column('Usuario', width=120, minwidth=100)
        self.tree.column('Rol', width=100, minwidth=80)
        self.tree.column('Nombre', width=150, minwidth=120)
        self.tree.column('Apellido', width=150, minwidth=120)
        self.tree.column('Grado', width=180, minwidth=150)
        self.tree.column('Cédula', width=120, minwidth=100)
        self.tree.column('Teléfono', width=130, minwidth=110)
        
        # Variable para controlar el orden de clasificación
        self.sort_reverse = False
        
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
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)
        
    def sort_by_grado(self):
        """Ordenar por grado según la jerarquía específica"""
        # Definir el orden jerárquico de grados
        grado_order = {
            "Comisario Principal": 1,
            "Comisario": 2,
            "Subcomisario": 3,
            "Oficial Inspector": 4,
            "Oficial Primero": 5,
            "Oficial Segundo": 6,
            "Oficial Ayudante": 7,
            "Suboficial Superior": 8,
            "Suboficial Principal": 9,
            "Suboficial Mayor": 10,
            "Suboficial Inspector": 11,
            "Suboficial Primero": 12,
            "Suboficial Segundo": 13,
            "Suboficial Ayudante": 14,
            "Funcionario/a": 15
        }
        
        # Obtener todos los elementos de la tabla
        items = [(self.tree.set(item, 'Grado'), item) for item in self.tree.get_children('')]
        
        # Ordenar por el valor numérico del grado
        def sort_key(item):
            grado, tree_item = item
            return grado_order.get(grado, 999)  # 999 para grados no definidos
        
        items.sort(key=sort_key, reverse=self.sort_reverse)
        
        # Reorganizar los elementos en la tabla
        for index, (grado, item) in enumerate(items):
            self.tree.move(item, '', index)
        
        # Cambiar el orden para el próximo clic
        self.sort_reverse = not self.sort_reverse
        
        # Actualizar el encabezado para mostrar la dirección del orden
        if self.sort_reverse:
            self.tree.heading('Grado', text='Grado ▼')
        else:
            self.tree.heading('Grado', text='Grado ▲')
        
    def load_users(self):
        """Cargar usuarios en la tabla"""
        try:
            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Obtener usuarios
            users = get_usuarios()
            
            if users:
                for user in users:
                    self.tree.insert('', 'end', values=(
                        user[1],  # Usuario
                        user[2],  # Rol
                        user[3],  # Nombre
                        user[4],  # Apellido
                        user[5] or 'N/A',  # Grado
                        user[6] or 'N/A',  # Cédula
                        user[8] or 'N/A',  # Teléfono
                    ))
                
                self.info_label.config(text=f"Total: {len(users)} usuario(s)")
            else:
                self.info_label.config(text="No hay usuarios registrados")
                
        except Exception as e:
            self.info_label.config(text=f"Error al cargar usuarios: {e}")
            messagebox.showerror("Error", f"Error al cargar usuarios: {e}")
    
    def nuevo_usuario(self):
        """Abrir formulario para nuevo usuario"""
        FormularioUsuario(self, None)
    
    def modificar_usuario(self):
        """Modificar usuario seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un usuario para modificar")
            return
        
        # Obtener el usuario seleccionado
        user_values = self.tree.item(selected[0])['values']
        username = user_values[0]  # Usuario está en la primera columna ahora
        
        # Buscar el ID del usuario por su nombre de usuario
        users = get_usuarios()
        user_id = None
        for user in users:
            if user[1] == username:  # user[1] es el nombre de usuario
                user_id = user[0]  # user[0] es el ID
                break
        
        if user_id:
            FormularioUsuario(self, user_id)
        else:
            messagebox.showerror("Error", "No se pudo encontrar el usuario seleccionado")
    
    def eliminar_usuario(self):
        """Eliminar usuario seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un usuario para eliminar")
            return
        
        # Obtener el usuario seleccionado
        user_values = self.tree.item(selected[0])['values']
        username = user_values[0]  # Usuario está en la primera columna ahora
        nombre = user_values[2]    # Nombre está en la tercera columna ahora
        apellido = user_values[3]  # Apellido está en la cuarta columna ahora
        
        # Buscar el ID del usuario por su nombre de usuario
        users = get_usuarios()
        user_id = None
        for user in users:
            if user[1] == username:  # user[1] es el nombre de usuario
                user_id = user[0]  # user[0] es el ID
                break
        
        if not user_id:
            messagebox.showerror("Error", "No se pudo encontrar el usuario seleccionado")
            return
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar Eliminación", 
                              f"¿Está seguro de eliminar al usuario {nombre} {apellido} ({username})?\n\n"
                              "Esta acción no se puede deshacer."):
            
            # Verificar que no sea el usuario actual
            if user_id == self.user_data['id']:
                messagebox.showerror("Error", "No puede eliminar su propio usuario")
                return
            
            # Intentar eliminar
            if eliminar_usuario(user_id):
                messagebox.showinfo("Éxito", f"Usuario {nombre} {apellido} eliminado correctamente")
                self.load_users()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el usuario")
    
    def on_double_click(self, event):
        """Manejar doble clic en un usuario"""
        self.modificar_usuario()
    
    def show_context_menu(self, event):
        """Mostrar menú contextual"""
        selection = self.tree.selection()
        if selection:
            context_menu = tk.Menu(self, tearoff=0)
            context_menu.add_command(label="Ver Detalles", 
                                   command=lambda: self.ver_detalles_usuario(
                                       self.tree.item(selection[0])['values']))
            context_menu.add_command(label="Modificar", 
                                   command=lambda: self.modificar_usuario())
            context_menu.add_separator()
            context_menu.add_command(label="Eliminar", 
                                   command=lambda: self.eliminar_usuario())
            
            context_menu.tk_popup(event.x_root, event.y_root)
    
    def ver_detalles_usuario(self, values):
        """Ver detalles del usuario"""
        if not values:
            return
        
        # Crear ventana de detalles
        details_window = tk.Toplevel(self)
        details_window.title(f"Detalles del Usuario - {values[2]} {values[3]}")
        details_window.geometry("500x400")
        details_window.transient(self)
        details_window.grab_set()
        details_window.configure(bg='#f8f9fa')
        
        # Buscar información completa del usuario
        users = get_usuarios()
        user_info = None
        for user in users:
            if user[1] == values[0]:  # Buscar por nombre de usuario
                user_info = user
                break
        
        if not user_info:
            messagebox.showerror("Error", "No se pudo obtener la información completa del usuario")
            return
        
        # Mostrar información detallada
        info_text = f"""
        INFORMACIÓN DEL USUARIO
        
        ID: {user_info[0]}
        Usuario: {user_info[1]}
        Rol: {user_info[2]}
        Nombre: {user_info[3]}
        Apellido: {user_info[4]}
        Grado: {user_info[5] or 'N/A'}
        Cédula: {user_info[6] or 'N/A'}
        N° Credencial: {user_info[7] or 'N/A'}
        Teléfono: {user_info[8] or 'N/A'}
        Estado: {'Primer Inicio' if user_info[9] else 'Activo'}
        
        INFORMACIÓN ADICIONAL
        - Fecha de creación: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        - Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """
        
        text_widget = tk.Text(details_window, wrap='word', padx=20, pady=20, 
                             font=('Segoe UI', 10), bg='white')
        text_widget.pack(expand=True, fill='both')
        text_widget.insert('1.0', info_text)
        text_widget.config(state='disabled')

class FormularioUsuario(tk.Toplevel):
    def __init__(self, parent, user_id=None):
        super().__init__(parent)
        self.title("Nuevo Usuario" if user_id is None else "Modificar Usuario")
        self.geometry("")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Configurar estilo moderno
        self.configure(bg='#f8f9fa')
        
        self.parent = parent
        self.user_id = user_id
        self.user_data = None
        
        # Cargar datos del usuario si es modificación
        if user_id:
            self.cargar_datos_usuario()
        
        self.setup_ui()
        
        # Cargar datos en el formulario después de crear la interfaz
        if user_id:
            self.after(100, self.cargar_datos_en_formulario)
    
    def cargar_datos_usuario(self):
        """Cargar los datos del usuario desde la base de datos"""
        self.user_data = obtener_usuario_por_id(self.user_id)
        
        if not self.user_data:
            messagebox.showerror("Error", "No se pudo cargar los datos del usuario")
            self.destroy()
            return
    
    def setup_ui(self):
        """Configurar la interfaz del formulario"""
        # Frame principal
        frame_main = tk.Frame(self, bg='#f8f9fa', padx=30, pady=20)
        frame_main.pack(expand=True, fill='both')
        
        # Título principal
        title_frame = tk.Frame(frame_main, bg='#f8f9fa')
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_text = "NUEVO USUARIO" if self.user_id is None else "MODIFICAR USUARIO"
        title_label = tk.Label(title_frame, text=title_text, 
                               font=('Segoe UI', 16, 'bold'), 
                               fg='#2c3e50', bg='#f8f9fa')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Sistema de Administración de Usuarios", 
                                  font=('Segoe UI', 10), 
                                  fg='#6c757d', bg='#f8f9fa')
        subtitle_label.pack()
        
        # Frame para el formulario
        form_frame = tk.Frame(frame_main, bg='white', relief='solid', bd=1)
        form_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Configurar grid del formulario
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)
        
        # Variables para los campos
        self.entry_usuario = tk.StringVar()
        self.entry_contrasena = tk.StringVar()
        self.entry_rol = tk.StringVar(value="USUARIO")
        self.entry_nombre = tk.StringVar()
        self.entry_apellido = tk.StringVar()
        self.entry_grado = tk.StringVar()
        self.entry_cedula = tk.StringVar()
        self.entry_credencial = tk.StringVar()
        self.entry_telefono = tk.StringVar()
        self.entry_primer_inicio = tk.BooleanVar()
        
        # Valores para combobox
        self.roles = ["USUARIO", "ADMIN", "SUPERADMIN"]
        self.grados = [
            "Oficial Ayudante", "Oficial Segundo", "Oficial Primero", "Oficial Inspector",
            "Subcomisario", "Comisario", "Comisario Principal", "Comisario General",
            "Suboficial Ayudante", "Suboficial Segundo", "Suboficial Primero", "Suboficial Inspector",
            "Suboficial Mayor", "Suboficial Principal", "Suboficial Superior",
            "Funcionario/a"
        ]
        
        # Sección 1: Información de Acceso
        self.crear_seccion_titulo(form_frame, "INFORMACIÓN DE ACCESO", 0)
        
        # Usuario y Contraseña
        self.crear_campo_horizontal(form_frame, "Usuario:", self.entry_usuario, 1, "Contraseña:", self.entry_contrasena, readonly2=False, password2=True)
        
        # Rol
        self.crear_campo_combobox(form_frame, "Rol:", self.entry_rol, 2, self.roles)
        
        # Sección 2: Información Personal
        self.crear_seccion_titulo(form_frame, "INFORMACIÓN PERSONAL", 3)
        
        # Nombre y Apellido
        self.crear_campo_horizontal(form_frame, "Nombre:", self.entry_nombre, 4, "Apellido:", self.entry_apellido)
        
        # Grado y Cédula
        self.crear_campo_horizontal_combobox(form_frame, "Grado:", self.entry_grado, 5, "Cédula:", self.entry_cedula, self.grados, [])
        
        # Credencial y Teléfono
        self.crear_campo_horizontal(form_frame, "N° Credencial:", self.entry_credencial, 6, "Teléfono:", self.entry_telefono)
        
        # Sección 3: Configuración de Acceso
        self.crear_seccion_titulo(form_frame, "CONFIGURACIÓN DE ACCESO", 7)
        
        # Opción de Primer Inicio
        self.crear_campo_toggle(form_frame, "Forzar cambio de contraseña en próximo inicio:", self.entry_primer_inicio, 8)
        
        # Frame para botones centrados
        button_frame = tk.Frame(frame_main, bg='#f8f9fa')
        button_frame.pack(fill='x', pady=20)
        
        # Frame interno para centrar los botones
        button_center_frame = tk.Frame(button_frame, bg='#f8f9fa')
        button_center_frame.pack(expand=True)
        
        # Botón Guardar
        save_text = "GUARDAR USUARIO" if self.user_id is None else "GUARDAR CAMBIOS"
        save_button = tk.Button(button_center_frame, text=save_text, 
                               command=self.guardar_usuario,
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', bg='#2E902E',
                               activebackground='#2E902E',
                               relief='flat', bd=0,
                               padx=30, pady=12,
                               cursor='hand2')
        
        # Botón Cancelar
        cancel_button = tk.Button(button_center_frame, text="CANCELAR", 
                                 command=self.destroy,
                                 font=('Segoe UI', 12),
                                 fg='white', bg='#902E2E',
                                 activebackground='#902E2E',
                                 relief='flat', bd=0,
                                 padx=30, pady=12,
                                 cursor='hand2')
        
        # Centrar los botones
        save_button.pack(side='left', padx=(0, 10))
        cancel_button.pack(side='left')
    
    def crear_seccion_titulo(self, parent, texto, row):
        """Crear título de sección"""
        title_label = tk.Label(parent, text=texto, 
                               font=('Segoe UI', 12, 'bold'), 
                               fg='#2c3e50', bg='white')
        title_label.grid(row=row, column=0, columnspan=4, sticky='w', pady=(20, 15), padx=10)
    
    def crear_campo_horizontal(self, parent, label1, var1, row, label2, var2, readonly1=False, readonly2=False, password1=False, password2=False):
        """Crear dos campos en la misma fila"""
        # Primer campo
        label1_widget = tk.Label(parent, text=label1, 
                                 font=('Segoe UI', 10, 'bold'), 
                                 fg='#2c3e50', bg='white', anchor='w')
        label1_widget.grid(row=row, column=0, sticky='w', pady=8, padx=10)
        
        if readonly1:
            entry1 = tk.Entry(parent, textvariable=var1, 
                             font=('Segoe UI', 10),
                             state='readonly', readonlybackground='#f8f9fa',
                             relief='solid', bd=1,
                             highlightthickness=1, highlightcolor='#2E5090')
        else:
            show_char = '*' if password1 else None
            entry1 = tk.Entry(parent, textvariable=var1, 
                             font=('Segoe UI', 10),
                             relief='solid', bd=1,
                             highlightthickness=1, highlightcolor='#2E5090',
                             bg='white', show=show_char)
        entry1.grid(row=row, column=1, sticky='ew', pady=8, padx=(0, 5))
        
        # Segundo campo
        label2_widget = tk.Label(parent, text=label2, 
                                 font=('Segoe UI', 10, 'bold'), 
                                 fg='#2c3e50', bg='white', anchor='w')
        label2_widget.grid(row=row, column=2, sticky='w', pady=8, padx=10)
        
        if readonly2:
            entry2 = tk.Entry(parent, textvariable=var2, 
                             font=('Segoe UI', 10),
                             state='readonly', readonlybackground='#f8f9fa',
                             relief='solid', bd=1,
                             highlightthickness=1, highlightcolor='#2E5090')
        else:
            show_char = '*' if password2 else None
            entry2 = tk.Entry(parent, textvariable=var2, 
                             font=('Segoe UI', 10),
                             relief='solid', bd=1,
                             highlightthickness=1, highlightcolor='#2E5090',
                             bg='white', show=show_char)
        entry2.grid(row=row, column=3, sticky='ew', pady=8, padx=(0, 10))
    
    def crear_campo_combobox(self, parent, label_text, variable, row, valores):
        """Crear campo con combobox"""
        # Label
        label = tk.Label(parent, text=label_text, 
                         font=('Segoe UI', 10, 'bold'), 
                         fg='#2c3e50', bg='white', anchor='w')
        label.grid(row=row, column=0, sticky='w', pady=8, padx=10)
        
        # Combobox
        combo = ttk.Combobox(parent, textvariable=variable, values=valores, 
                             state="readonly", font=('Segoe UI', 10))
        combo.grid(row=row, column=1, columnspan=3, sticky='ew', pady=8, padx=(0, 10))
    
    def crear_campo_horizontal_combobox(self, parent, label1, var1, row, label2, var2, valores1, valores2):
        """Crear dos campos con combobox en la misma fila"""
        # Primer campo
        label1_widget = tk.Label(parent, text=label1, 
                                 font=('Segoe UI', 10, 'bold'), 
                                 fg='#2c3e50', bg='white', anchor='w')
        label1_widget.grid(row=row, column=0, sticky='w', pady=8, padx=10)
        
        combo1 = ttk.Combobox(parent, textvariable=var1, values=valores1, 
                              state="readonly", font=('Segoe UI', 10))
        combo1.grid(row=row, column=1, sticky='ew', pady=8, padx=(0, 5))
        
        # Segundo campo
        label2_widget = tk.Label(parent, text=label2, 
                                 font=('Segoe UI', 10, 'bold'), 
                                 fg='#2c3e50', bg='white', anchor='w')
        label2_widget.grid(row=row, column=2, sticky='w', pady=8, padx=10)
        
        if valores2:  # Si hay valores para el segundo campo, usar combobox
            combo2 = ttk.Combobox(parent, textvariable=var2, values=valores2, 
                                  state="readonly", font=('Segoe UI', 10))
            combo2.grid(row=row, column=3, sticky='ew', pady=8, padx=(0, 10))
        else:  # Si no hay valores, usar entry normal
            entry2 = tk.Entry(parent, textvariable=var2, 
                             font=('Segoe UI', 10),
                             relief='solid', bd=1,
                             highlightthickness=1, highlightcolor='#2E5090',
                             bg='white')
            entry2.grid(row=row, column=3, sticky='ew', pady=8, padx=(0, 10))
    
    def crear_campo_toggle(self, parent, label_text, variable, row):
        """Crear campo con toggle switch moderno"""
        # Frame para contener label y toggle
        toggle_frame = tk.Frame(parent, bg='white')
        toggle_frame.grid(row=row, column=0, columnspan=4, sticky='ew', pady=8, padx=10)
        
        # Label
        label = tk.Label(toggle_frame, text=label_text, 
                         font=('Segoe UI', 10, 'bold'), 
                         fg='#2c3e50', bg='white', anchor='w')
        label.pack(side='left')
        
        # Frame para el toggle switch
        toggle_container = tk.Frame(toggle_frame, bg='white')
        toggle_container.pack(side='right', padx=(10, 0))
        
        # Crear el toggle switch
        self.crear_toggle_switch(toggle_container, variable)
    
    def crear_toggle_switch(self, parent, variable):
        """Crear un toggle switch moderno"""
        # Frame principal del toggle (fondo)
        toggle_bg = tk.Frame(parent, bg='#e9ecef', width=50, height=24, 
                            relief='flat', bd=0)
        toggle_bg.pack()
        toggle_bg.pack_propagate(False)
        
        # Círculo del toggle (indicador)
        toggle_circle = tk.Frame(toggle_bg, bg='white', width=20, height=20,
                                relief='flat', bd=0)
        toggle_circle.place(x=2, y=2)
        
        # Función para actualizar el toggle
        def update_toggle():
            if variable.get():
                # Estado ON
                toggle_bg.configure(bg='#2E5090')
                toggle_circle.place(x=28, y=2)  # Mover a la derecha
            else:
                # Estado OFF
                toggle_bg.configure(bg='#e9ecef')
                toggle_circle.place(x=2, y=2)   # Mover a la izquierda
        
        # Función para manejar clics
        def toggle_click(event):
            variable.set(not variable.get())
            update_toggle()
        
        # Configurar eventos de clic
        toggle_bg.bind('<Button-1>', toggle_click)
        toggle_circle.bind('<Button-1>', toggle_click)
        
        # Configurar el comando de la variable
        def on_variable_change(*args):
            update_toggle()
        
        variable.trace('w', on_variable_change)
        
        # Aplicar estado inicial
        update_toggle()
    
    def cargar_datos_en_formulario(self):
        """Cargar los datos del usuario en el formulario"""
        if not self.user_data:
            return
        
        # Cargar datos básicos
        self.entry_usuario.set(self.user_data[1] or '')
        self.entry_nombre.set(self.user_data[3] or '')
        self.entry_apellido.set(self.user_data[4] or '')
        self.entry_grado.set(self.user_data[5] or '')
        self.entry_cedula.set(self.user_data[6] or '')
        self.entry_credencial.set(self.user_data[7] or '')
        self.entry_telefono.set(self.user_data[8] or '')
        self.entry_rol.set(self.user_data[2] or 'USUARIO')
        
        # Cargar estado de primer_inicio
        self.entry_primer_inicio.set(self.user_data[9] if len(self.user_data) > 9 else False)
        
        # No cargar contraseña por seguridad
        self.entry_contrasena.set("")
    
    def guardar_usuario(self):
        """Guardar o actualizar usuario"""
        # Obtener datos del formulario
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_contrasena.get().strip()
        rol = self.entry_rol.get()
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        grado = self.entry_grado.get().strip()
        cedula = self.entry_cedula.get().strip()
        credencial = self.entry_credencial.get().strip()
        telefono = self.entry_telefono.get().strip()
        
        # Validar campos obligatorios
        if not usuario:
            messagebox.showerror("Error", "El campo Usuario es obligatorio")
            return
        
        if not nombre:
            messagebox.showerror("Error", "El campo Nombre es obligatorio")
            return
        
        if not apellido:
            messagebox.showerror("Error", "El campo Apellido es obligatorio")
            return
        
        # Para nuevos usuarios, la contraseña es obligatoria
        if self.user_id is None and not contrasena:
            messagebox.showerror("Error", "La contraseña es obligatoria para nuevos usuarios")
            return
        
        # Preparar datos
        user_data = {
            'usuario': usuario,
            'rol': rol,
            'nombre': nombre,
            'apellido': apellido,
            'grado': grado,
            'cedula': cedula,
            'numero_credencial': credencial,
            'telefono': telefono,
            'primer_inicio': self.entry_primer_inicio.get()
        }
        
        # Agregar contraseña solo si se proporcionó
        if contrasena:
            user_data['contrasena'] = contrasena
        
        # Guardar o actualizar
        if self.user_id is None:
            # Crear nuevo usuario
            if crear_usuario(user_data):
                messagebox.showinfo("Éxito", "Usuario creado correctamente")
                self.destroy()
                # Actualizar lista en la ventana padre
                if hasattr(self.parent, 'load_users'):
                    self.parent.load_users()
            else:
                messagebox.showerror("Error", "No se pudo crear el usuario")
        else:
            # Actualizar usuario existente
            if actualizar_usuario(self.user_id, user_data):
                messagebox.showinfo("Éxito", "Usuario actualizado correctamente")
                self.destroy()
                # Actualizar lista en la ventana padre
                if hasattr(self.parent, 'load_users'):
                    self.parent.load_users()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el usuario")

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
    
    app = GestionUsuarios(root, user_data)
    root.mainloop()

if __name__ == "__main__":
    main() 