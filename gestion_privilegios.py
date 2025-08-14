#!/usr/bin/env python3
"""
Módulo para gestión de privilegios del sistema
"""

import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
import os
from database import obtener_todos_privilegios, actualizar_privilegio, verificar_privilegio

# Configurar DPI para Windows (HD/4K)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Per Monitor DPI Aware
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()  # Fallback para versiones anteriores
    except:
        pass

class GestionPrivilegios(tk.Toplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.title("Gestión de Privilegios - Sistema QUIRA")
        self.geometry('')
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        # Configurar estilo moderno
        self.configure(bg='#f8f9fa')
        
        self.user_data = user_data
        self.privilegios_data = {}
        self.setup_ui()
        self.load_privileges()
        
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
        
        title_label = tk.Label(title_frame, text="GESTIÓN DE PRIVILEGIOS", 
                               font=('Segoe UI', 18, 'bold'), 
                               fg='#2c3e50', bg='#f8f9fa')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Configuración de Permisos por Rol", 
                                  font=('Segoe UI', 11), 
                                  fg='#6c757d', bg='#f8f9fa')
        subtitle_label.pack()
        
        # Frame de información
        info_frame = tk.Frame(main_frame, bg='#f8f9fa')
        info_frame.pack(fill='x', pady=(0, 20))
        
        info_label = tk.Label(info_frame, 
                              text="Marque o desmarque los privilegios para cada rol. Los cambios se aplican inmediatamente.",
                              font=('Segoe UI', 10), 
                              fg='#495057', bg='#f8f9fa',
                              wraplength=600)
        info_label.pack()
        
        # Frame para el contenido de privilegios
        content_frame = tk.Frame(main_frame, bg='#f8f9fa')
        content_frame.pack(expand=True, fill='both')
        
        # Crear notebook para organizar por roles
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Crear pestañas para cada rol
        self.create_role_tabs()
        
    def load_institutional_image(self, parent):
        """Cargar imagen institucional"""
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
                os.path.join(os.path.dirname(__file__), "instituto.png"),  # Ruta original
                "instituto.png",  # Ruta relativa
            ]
            
            img_path = None
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    img_path = ruta
                    break
            
            if img_path:
                img = Image.open(img_path)
                
                # Redimensionar la imagen
                img_width, img_height = img.size
                max_height = 80
                if img_height > max_height:
                    ratio = max_height / img_height
                    new_width = int(img_width * ratio)
                    new_height = max_height
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(img)
                
                img_label = tk.Label(parent, image=photo, bg='#f8f9fa')
                img_label.image = photo
                img_label.pack(pady=(0, 10))
                
        except Exception as e:
            print(f"[WARN] No se pudo cargar la imagen del instituto: {e}")
    
    def create_role_tabs(self):
        """Crear pestañas para cada rol"""
        roles = ['USUARIO', 'ADMIN', 'SUPERADMIN']
        
        for rol in roles:
            # Crear frame para la pestaña
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=rol)
            
            # Crear contenido para el rol
            self.create_role_content(tab_frame, rol)
    
    def create_role_content(self, parent, rol):
        """Crear contenido para un rol específico"""
        # Frame principal del rol
        role_frame = tk.Frame(parent, bg='#f8f9fa')
        role_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Título del rol
        role_title = tk.Label(role_frame, text=f"Privilegios para Rol: {rol}", 
                              font=('Segoe UI', 14, 'bold'), 
                              fg='#2c3e50', bg='#f8f9fa')
        role_title.pack(pady=(0, 20))
        
        # Frame para la lista de privilegios
        privileges_frame = tk.Frame(role_frame, bg='#f8f9fa')
        privileges_frame.pack(expand=True, fill='both')
        
        # Crear Treeview para privilegios
        self.create_privileges_treeview(privileges_frame, rol)
        
        # Frame para botones
        buttons_frame = tk.Frame(role_frame, bg='#f8f9fa')
        buttons_frame.pack(fill='x', pady=(20, 0))
        
        # Botón para activar todos
        activate_all_btn = tk.Button(buttons_frame, text="Activar Todos", 
                                     command=lambda: self.toggle_all_privileges(rol, True),
                                     font=('Segoe UI', 10, 'bold'),
                                     fg='white', bg='#2E902E',
                                     activebackground='#2E902E',
                                     relief='flat', bd=0,
                                     padx=20, pady=8,
                                     cursor='hand2')
        activate_all_btn.pack(side='left', padx=(0, 10))
        
        # Botón para desactivar todos
        deactivate_all_btn = tk.Button(buttons_frame, text="Desactivar Todos", 
                                       command=lambda: self.toggle_all_privileges(rol, False),
                                       font=('Segoe UI', 10, 'bold'),
                                       fg='white', bg='#902E2E',
                                       activebackground='#902E2E',
                                       relief='flat', bd=0,
                                       padx=20, pady=8,
                                       cursor='hand2')
        deactivate_all_btn.pack(side='left', padx=(0, 10))
        
        # Botón para restaurar valores por defecto
        restore_btn = tk.Button(buttons_frame, text="Restaurar Valores por Defecto", 
                                command=lambda: self.restore_default_privileges(rol),
                                font=('Segoe UI', 10, 'bold'),
                                fg='white', bg='#2E5090',
                                activebackground='#2E5090',
                                relief='flat', bd=0,
                                padx=20, pady=8,
                                cursor='hand2')
        restore_btn.pack(side='left', padx=(0, 10))
    
    def create_privileges_treeview(self, parent, rol):
        """Crear Treeview para mostrar privilegios"""
        # Frame para contener el Treeview y scrollbar
        tree_frame = tk.Frame(parent, bg='#f8f9fa')
        tree_frame.pack(expand=True, fill='both')
        
        # Crear Treeview
        columns = ('Privilegio', 'Descripción', 'Estado')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.tree.heading('Privilegio', text='Privilegio')
        self.tree.heading('Descripción', text='Descripción')
        self.tree.heading('Estado', text='Estado')
        
        self.tree.column('Privilegio', width=200, minwidth=150)
        self.tree.column('Descripción', width=300, minwidth=200)
        self.tree.column('Estado', width=100, minwidth=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind para doble clic
        self.tree.bind('<Double-1>', lambda e: self.toggle_privilege(rol))
        
        # Guardar referencia al treeview por rol
        if not hasattr(self, 'trees'):
            self.trees = {}
        self.trees[rol] = self.tree
    
    def load_privileges(self):
        """Cargar privilegios desde la base de datos"""
        try:
            self.privilegios_data = obtener_todos_privilegios()
            self.populate_privileges()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar privilegios: {e}")
    
    def populate_privileges(self):
        """Poblar los Treeviews con los privilegios"""
        for rol, privilegios in self.privilegios_data.items():
            if rol in self.trees:
                tree = self.trees[rol]
                
                # Limpiar treeview
                for item in tree.get_children():
                    tree.delete(item)
                
                # Agregar privilegios
                for privilegio in privilegios:
                    estado = "[OK] Activo" if privilegio['activo'] else "[ERROR] Inactivo"
                    tree.insert('', 'end', values=(
                        privilegio['permiso'],
                        privilegio['descripcion'],
                        estado
                    ))
    
    def toggle_privilege(self, rol):
        """Cambiar el estado de un privilegio"""
        try:
            tree = self.trees[rol]
            selection = tree.selection()
            
            if not selection:
                return
            
            item = selection[0]
            values = tree.item(item, 'values')
            permiso = values[0]
            
            # Obtener estado actual
            privilegios_rol = self.privilegios_data.get(rol, [])
            privilegio_actual = next((p for p in privilegios_rol if p['permiso'] == permiso), None)
            
            if privilegio_actual:
                nuevo_estado = not privilegio_actual['activo']
                
                # Actualizar en base de datos
                if actualizar_privilegio(rol, permiso, nuevo_estado):
                    # Actualizar datos locales
                    privilegio_actual['activo'] = nuevo_estado
                    
                    # Actualizar vista
                    estado_texto = "[OK] Activo" if nuevo_estado else "[ERROR] Inactivo"
                    tree.item(item, values=(permiso, values[1], estado_texto))
                    
                    messagebox.showinfo("Éxito", f"Privilegio '{permiso}' para rol '{rol}' actualizado correctamente")
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el privilegio")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar privilegio: {e}")
    
    def toggle_all_privileges(self, rol, activo):
        """Activar o desactivar todos los privilegios de un rol"""
        try:
            confirmacion = messagebox.askyesno(
                "Confirmar", 
                f"¿Está seguro de {'activar' if activo else 'desactivar'} todos los privilegios para el rol '{rol}'?"
            )
            
            if not confirmacion:
                return
            
            privilegios_rol = self.privilegios_data.get(rol, [])
            actualizados = 0
            
            for privilegio in privilegios_rol:
                if actualizar_privilegio(rol, privilegio['permiso'], activo):
                    privilegio['activo'] = activo
                    actualizados += 1
            
            # Actualizar vista
            self.populate_privileges()
            
            messagebox.showinfo("Éxito", f"Se actualizaron {actualizados} privilegios para el rol '{rol}'")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar privilegios: {e}")
    
    def restore_default_privileges(self, rol):
        """Restaurar privilegios por defecto para un rol"""
        try:
            confirmacion = messagebox.askyesno(
                "Confirmar", 
                f"¿Está seguro de restaurar los valores por defecto para el rol '{rol}'?\n\nEsto desactivará todos los privilegios y luego activará solo los predeterminados."
            )
            
            if not confirmacion:
                return
            
            # Primero desactivar todos
            privilegios_rol = self.privilegios_data.get(rol, [])
            for privilegio in privilegios_rol:
                actualizar_privilegio(rol, privilegio['permiso'], False)
                privilegio['activo'] = False
            
            # Luego activar solo los por defecto según el rol
            default_privileges = self.get_default_privileges_for_role(rol)
            for permiso in default_privileges:
                actualizar_privilegio(rol, permiso, True)
                # Actualizar datos locales
                for privilegio in privilegios_rol:
                    if privilegio['permiso'] == permiso:
                        privilegio['activo'] = True
                        break
            
            # Actualizar vista
            self.populate_privileges()
            
            messagebox.showinfo("Éxito", f"Privilegios por defecto restaurados para el rol '{rol}'")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al restaurar privilegios: {e}")
    
    def get_default_privileges_for_role(self, rol):
        """Obtener privilegios por defecto para un rol específico"""
        # Ahora todos los roles tienen acceso a todos los privilegios
        # Los valores por defecto son solo sugerencias, pero puedes activar/desactivar cualquier permiso
        default_privileges = {
            'USUARIO': [
                'buscar_postulantes',
                'agregar_postulante',
                'lista_postulantes',
                'estadisticas_basicas',
                'gestion_zkteco_basica',
                'eliminar_postulantes',
                'eliminar_postulantes_propios'
            ],
            'ADMIN': [
                'buscar_postulantes',
                'agregar_postulante',
                'lista_postulantes',
                'estadisticas_completas',
                'gestion_zkteco_completa',
                'editar_postulantes_propios',
                'editar_postulantes_otros',
                'eliminar_postulantes_propios',
                'eliminar_postulantes'
            ],
            'SUPERADMIN': [
                'buscar_postulantes',
                'agregar_postulante',
                'lista_postulantes',
                'estadisticas_completas',
                'gestion_zkteco_completa',
                'editar_postulantes_propios',
                'editar_postulantes_otros',
                'eliminar_postulantes_propios',
                'eliminar_postulantes_otros',
                'eliminar_postulantes',
                'gestion_usuarios',
                'gestion_privilegios'
            ]
        }
        
        return default_privileges.get(rol, [])

def main():
    """Función principal para pruebas"""
    root = tk.Tk()
    root.withdraw()
    
    # Datos de usuario de prueba
    user_data = {
        'id': 1,
        'usuario': 'admin',
        'rol': 'SUPERADMIN',
        'nombre': 'Admin',
        'apellido': 'General'
    }
    
    app = GestionPrivilegios(root, user_data)
    root.mainloop()

if __name__ == "__main__":
    main()
