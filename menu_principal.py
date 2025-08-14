#!/usr/bin/env python3
"""
Menú principal integrado para Sistema QUIRA
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import get_postulantes, get_usuarios, crear_usuario
from zkteco_connector_v2 import ZKTecoK40V2
import ctypes

# Configurar DPI para Windows (HD/4K)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Per Monitor DPI Aware
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()  # Fallback para versiones anteriores
    except:
        pass

class MenuPrincipal(tk.Frame):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.parent = parent
        self.user_data = user_data
        self.zkteco_device = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar la interfaz del menú principal"""
        # Configurar el fondo principal
        self.configure(bg='#f8f9fa')
        
        # Crear barra de menú
        self.create_menu_bar()
        
        # Frame principal con padding generoso
        main_frame = tk.Frame(self, bg='#f8f9fa')
        main_frame.pack(expand=True, fill='both', padx=40, pady=40)
        
        # Contenedor central para centrar todo el contenido
        center_frame = tk.Frame(main_frame, bg='#f8f9fa')
        center_frame.pack(expand=True)
        
        # Agregar imagen del instituto
        try:
            # Cargar y mostrar la imagen del instituto
            from PIL import Image, ImageTk
            import os
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
                # Cargar la imagen
                img = Image.open(img_path)
                
                # Redimensionar la imagen manteniendo proporción (máximo 120px de alto)
                img_width, img_height = img.size
                max_height = 120
                if img_height > max_height:
                    ratio = max_height / img_height
                    new_width = int(img_width * ratio)
                    new_height = max_height
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convertir a PhotoImage
                photo = ImageTk.PhotoImage(img)
                
                # Crear label para la imagen
                img_label = tk.Label(center_frame, image=photo, bg='#f8f9fa')
                img_label.image = photo  # Mantener referencia
                img_label.pack(pady=(0, 20))
                
                print(f"[OK] Imagen del instituto cargada correctamente desde: {img_path}")
            else:
                print(f"[WARN] No se encontró la imagen del instituto en ninguna ruta")
                
        except ImportError:
            print("[WARN] Pillow no está instalado. Ejecute: pip install Pillow")
        except Exception as e:
            print(f"[WARN] No se pudo cargar la imagen del instituto: {e}")
            # Si no se puede cargar la imagen, continuar sin ella
        
        # Mensaje de bienvenida con estilo moderno
        welcome_text = f"Bienvenido {self.user_data['nombre']} {self.user_data['apellido']}"
        welcome_label = tk.Label(center_frame, text=welcome_text, 
                               font=('Segoe UI', 18, 'bold'), 
                               fg='#2c3e50', bg='#f8f9fa')
        welcome_label.pack(pady=(0, 5))
        
        # Subtítulo con el grado
        grado_text = self.user_data['grado']
        grado_label = tk.Label(center_frame, text=grado_text, 
                             font=('Segoe UI', 12), 
                             fg='#6c757d', bg='#f8f9fa')
        grado_label.pack(pady=(0, 40))
        
        # Frame de botones con espaciado moderno
        button_frame = tk.Frame(center_frame, bg='#f8f9fa')
        button_frame.pack()
        
        # Crear botones principales simplificados
        self.create_main_buttons(button_frame)
    
    def create_menu_bar(self):
        """Crear barra de menú en cascada"""
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        
        # Menú Gestión
        gestion_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Gestión", menu=gestion_menu)
        gestion_menu.add_command(label="Lista de Postulantes", command=self.ver_lista_postulantes)
        gestion_menu.add_command(label="Estadísticas", command=self.ver_estadisticas)
        gestion_menu.add_separator()
        gestion_menu.add_command(label="Control de Asistencia", command=self.control_asistencia)
        
        # Menú Sistema
        sistema_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Sistema", menu=sistema_menu)
        sistema_menu.add_command(label="Gestión ZKTeco", command=self.gestion_zkteco)
        
        # Solo mostrar gestión de usuarios y privilegios para superadmin
        if self.user_data["rol"] == "SUPERADMIN":
            sistema_menu.add_separator()
            sistema_menu.add_command(label="Gestión de Usuarios", command=self.gestion_usuarios)
            sistema_menu.add_command(label="Gestión de Privilegios", command=self.gestion_privilegios)
            sistema_menu.add_separator()
            sistema_menu.add_command(label="Cargar Cédulas Problema Judicial", command=self.cargar_cedulas_problema_judicial)
        
        # Menú Ayuda
        ayuda_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=ayuda_menu)
        ayuda_menu.add_command(label="Acerca de", command=self.acerca_de)
    
    def create_main_buttons(self, frame):
        """Crear botones principales simplificados"""
        # Solo botones esenciales para todos los usuarios
        buttons = [
            ("Buscar Postulantes", self.buscar_postulantes),
            ("Agregar Postulante", self.agregar_postulante),
        ]
        
        # Crear frame para organizar botones en 2 columnas
        buttons_grid_frame = tk.Frame(frame, bg='#f8f9fa')
        buttons_grid_frame.pack()
        
        # Crear botones organizados en 2 columnas
        for i, (text, command) in enumerate(buttons):
            btn = self.create_modern_button(buttons_grid_frame, text, command)
            row = i // 2  # Fila
            col = i % 2   # Columna
            btn.grid(row=row, column=col, padx=10, pady=8, sticky='ew')
        
        # Configurar peso de columnas para que se expandan igual
        buttons_grid_frame.grid_columnconfigure(0, weight=1)
        buttons_grid_frame.grid_columnconfigure(1, weight=1)
        
        # Separador antes del botón de cerrar sesión
        separator = tk.Frame(frame, height=2, bg='#e9ecef')
        separator.pack(fill='x', pady=20)
        
        # Botón de cerrar sesión con estilo diferente (centrado)
        logout_frame = tk.Frame(frame, bg='#f8f9fa')
        logout_frame.pack(fill='x')
        logout_btn = self.create_logout_button(logout_frame)
        logout_btn.pack(pady=8)
    
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
                       padx=30, pady=12,
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
    
    def create_logout_button(self, parent):
        """Crear el botón de cerrar sesión con estilo especial"""
        # Frame contenedor para el botón
        button_frame = tk.Frame(parent, bg='#f8f9fa')
        
        # Botón de cerrar sesión
        btn = tk.Button(button_frame, text="Cerrar Sesión", command=self.logout,
                       font=('Segoe UI', 11),
                       fg='#6c757d', bg='#f8f9fa',
                       activebackground='#902E2E',
                       activeforeground='#ffffff',
                       relief='flat', bd=0,
                       padx=30, pady=12,
                       cursor='hand2')
        btn.pack(fill='x')
        
        # Efectos hover para el botón de logout
        def on_enter(e):
            btn.config(bg='#902E2E', fg='#ffffff')
        
        def on_leave(e):
            btn.config(bg='#f8f9fa', fg='#6c757d')
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return button_frame
    
    def buscar_postulantes(self):
        """Abrir ventana de búsqueda de postulantes"""
        from privilegios_utils import verificar_permiso_silencioso
        
        if verificar_permiso_silencioso(self.user_data, 'buscar_postulantes'):
            from buscar_postulantes import BuscarPostulantes
            BuscarPostulantes(self, self.user_data)
        else:
            # Mostrar aviso específico para buscar postulantes
            from tkinter import messagebox
            messagebox.showerror(
                "Acceso Denegado", 
                "No tiene permisos para buscar postulantes.\n\n"
                "Permiso requerido: buscar_postulantes\n\n"
                "Contacte al administrador del sistema."
            )
    
    def agregar_postulante(self):
        """Abrir ventana de agregar postulante"""
        from privilegios_utils import verificar_permiso_silencioso
        
        if verificar_permiso_silencioso(self.user_data, 'agregar_postulante'):
            from agregar_postulante import AgregarPostulante
            # Crear la ventana de agregar postulante
            ventana_agregar = AgregarPostulante(self, self.user_data)
            
            # Registrar como listener del modo prueba si existe la ventana de gestión ZKTeco
            if hasattr(self, 'gestion_zkteco_window') and self.gestion_zkteco_window.winfo_exists():
                self.gestion_zkteco_window.registrar_listener_modo_prueba(ventana_agregar)
        else:
            # Mostrar aviso específico para agregar postulante
            from tkinter import messagebox
            messagebox.showerror(
                "Acceso Denegado", 
                "No tiene permisos para agregar postulantes.\n\n"
                "Permiso requerido: agregar_postulante\n\n"
                "Contacte al administrador del sistema."
            )
    
    def gestion_zkteco(self):
        """Abrir gestión del dispositivo ZKTeco"""
        from privilegios_utils import puede_gestionar_zkteco
        
        if puede_gestionar_zkteco(self.user_data):
            from gestion_zkteco import GestionZKTeco
            # Mantener referencia a la ventana de gestión ZKTeco
            self.gestion_zkteco_window = GestionZKTeco(self, self.user_data)
        else:
            # Mostrar aviso específico para ZKTeco
            from tkinter import messagebox
            messagebox.showerror(
                "Acceso Denegado", 
                "No tiene permisos para gestionar dispositivos ZKTeco.\n\n"
                "Permiso requerido: gestion_zkteco_completa\n\n"
                "Contacte al administrador del sistema."
            )
    
    def ver_lista_postulantes(self):
        """Abrir lista completa de postulantes"""
        from privilegios_utils import verificar_permiso_silencioso
        
        if verificar_permiso_silencioso(self.user_data, 'lista_postulantes'):
            from lista_postulantes import ListaPostulantes
            ListaPostulantes(self, self.user_data)
        else:
            # Mostrar aviso específico para lista de postulantes
            from tkinter import messagebox
            messagebox.showerror(
                "Acceso Denegado", 
                "No tiene permisos para ver la lista de postulantes.\n\n"
                "Permiso requerido: lista_postulantes\n\n"
                "Contacte al administrador del sistema."
            )
    
    def ver_estadisticas(self):
        """Abrir estadísticas del sistema"""
        from privilegios_utils import puede_ver_estadisticas_completas, verificar_permiso
        
        # Verificar si puede ver estadísticas completas o básicas
        if puede_ver_estadisticas_completas(self.user_data) or verificar_permiso(self.user_data, 'estadisticas_basicas', mostrar_error=False):
            from estadisticas import Estadisticas
            Estadisticas(self, self.user_data)
        else:
            # Mostrar aviso específico para estadísticas
            from tkinter import messagebox
            messagebox.showerror(
                "Acceso Denegado", 
                "No tiene permisos para ver estadísticas.\n\n"
                "Permisos requeridos:\n"
                "• estadisticas_basicas\n"
                "• estadisticas_completas\n\n"
                "Contacte al administrador del sistema."
            )
    
    def gestion_usuarios(self):
        """Abrir gestión de usuarios"""
        from privilegios_utils import verificar_permiso_silencioso
        
        if verificar_permiso_silencioso(self.user_data, 'gestion_usuarios'):
            from gestion_usuarios import GestionUsuarios
            GestionUsuarios(self, self.user_data)
        else:
            # Mostrar aviso específico para gestión de usuarios
            from tkinter import messagebox
            messagebox.showerror(
                "Acceso Denegado", 
                "No tiene permisos para gestionar usuarios.\n\n"
                "Permiso requerido: gestion_usuarios\n\n"
                "Contacte al administrador del sistema."
            )
    
    def gestion_privilegios(self):
        """Abrir gestión de privilegios"""
        from privilegios_utils import verificar_permiso_silencioso
        
        if verificar_permiso_silencioso(self.user_data, 'gestion_privilegios'):
            from gestion_privilegios import GestionPrivilegios
            GestionPrivilegios(self, self.user_data)
        else:
            # Mostrar aviso específico para gestión de privilegios
            from tkinter import messagebox
            messagebox.showerror(
                "Acceso Denegado", 
                "No tiene permisos para gestionar privilegios.\n\n"
                "Permiso requerido: gestion_privilegios\n\n"
                "Contacte al administrador del sistema."
            )
    
    def cargar_cedulas_problema_judicial(self):
        """Abrir carga de cédulas con problemas judiciales"""
        from cargar_cedulas_problema_judicial import CargarCedulasProblemaJudicial
        CargarCedulasProblemaJudicial(self)
    
    def control_asistencia(self):
        """Abrir control de asistencia"""
        from privilegios_utils import verificar_permiso_silencioso
        
        if verificar_permiso_silencioso(self.user_data, 'control_asistencia'):
            from control_asistencia import ControlAsistencia
            ControlAsistencia(self, self.user_data)
        else:
            # Mostrar aviso específico para control de asistencia
            from tkinter import messagebox
            messagebox.showerror(
                "Acceso Denegado", 
                "No tiene permisos para acceder al control de asistencia.\n\n"
                "Permiso requerido: control_asistencia\n\n"
                "Contacte al administrador del sistema."
            )
    

    def acerca_de(self):
        """Mostrar información sobre el sistema"""
        # Crear ventana personalizada
        about_window = tk.Toplevel(self.parent)
        about_window.title("Acerca de QUIRA")
        about_window.geometry('')
        about_window.resizable(False, False)
        about_window.configure(bg='#f0f0f0')
        
        # Centrar la ventana
        about_window.transient(self.parent)
        about_window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(about_window, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Frame para logo y título (para controlar espaciado)
        logo_title_frame = tk.Frame(main_frame, bg='#f0f0f0')
        logo_title_frame.pack(pady=(0, 10))
        
        # Logo
        def cargar_logo():
            """Cargar logo con manejo robusto para PyInstaller"""
            import os
            import sys
            
            # Función para obtener la ruta base correcta
            def get_base_path():
                if getattr(sys, 'frozen', False):
                    # Ejecutando en PyInstaller
                    return os.path.dirname(sys.executable)
                else:
                    # Ejecutando en desarrollo
                    return os.path.dirname(os.path.abspath(__file__))
            
            base_path = get_base_path()
            
            # Lista de posibles rutas para la imagen
            posibles_rutas = [
                os.path.join(base_path, "quiraXXXL.png"),
                os.path.join(base_path, "quira.png"),
                os.path.join(base_path, "_internal", "quiraXXXL.png"),  # En _internal (PyInstaller)
                os.path.join(base_path, "_internal", "quira.png"),      # En _internal (PyInstaller)
                "quiraXXXL.png",  # Ruta relativa
                "quira.png",      # Ruta relativa
            ]
            
            for ruta in posibles_rutas:
                try:
                    if os.path.exists(ruta):
                        from PIL import Image, ImageTk
                        logo_img = Image.open(ruta)
                        # Redimensionar logo a 180x180 manteniendo proporción
                        logo_img = logo_img.resize((180, 180), Image.Resampling.LANCZOS)
                        logo_photo = ImageTk.PhotoImage(logo_img)
                        print(f"[OK] Logo cargado desde: {ruta}")
                        return logo_photo
                    else:
                        print(f"[WARN] Ruta no existe: {ruta}")
                except Exception as e:
                    print(f"[ERROR] Error cargando imagen {ruta}: {e}")
                    continue
            
            return None
        
        # Intentar cargar el logo
        logo_photo = cargar_logo()
        if logo_photo:
            logo_label = tk.Label(logo_title_frame, image=logo_photo, bg='#f0f0f0')
            logo_label.image = logo_photo  # Mantener referencia
            logo_label.pack(pady=(0, 0))
        else:
            # Si no se puede cargar la imagen, mostrar texto estilizado
            logo_label = tk.Label(logo_title_frame, text="QUIRA", font=('Arial', 36, 'bold'), 
                                fg='#2c3e50', bg='#f0f0f0')
            logo_label.pack(pady=(0, 0))
        
        # Título del sistema
        title_label = tk.Label(logo_title_frame, text="Sistema QUIRA", 
                              font=('Arial', 18, 'bold'), fg='#2c3e50', bg='#f0f0f0')
        title_label.pack(pady=(0, 0))
        
        # Versión
        version_label = tk.Label(main_frame, text="Versión 1.0", 
                                font=('Arial', 12), fg='#7f8c8d', bg='#f0f0f0')
        version_label.pack(pady=(0, 20))
        
        # Información del desarrollador
        dev_frame = tk.Frame(main_frame, bg='#f0f0f0')
        dev_frame.pack(pady=(0, 20))
        
        dev_title = tk.Label(dev_frame, text="Desarrollador:", 
                            font=('Arial', 12, 'bold'), fg='#2c3e50', bg='#f0f0f0')
        dev_title.pack()
        
        dev_name = tk.Label(dev_frame, text="Guillermo Recalde", 
                           font=('Arial', 12), fg='#34495e', bg='#f0f0f0')
        dev_name.pack()
        
        dev_alias = tk.Label(dev_frame, text="a.k.a. \"s1mple\"", 
                            font=('Arial', 10, 'italic'), fg='#7f8c8d', bg='#f0f0f0')
        dev_alias.pack()
        
        # Información institucional
        inst_frame = tk.Frame(main_frame, bg='#f0f0f0')
        inst_frame.pack(pady=(0, 20))
        
        inst_title = tk.Label(inst_frame, text="Desarrollado para:", 
                             font=('Arial', 12, 'bold'), fg='#2c3e50', bg='#f0f0f0')
        inst_title.pack()
        
        inst_name = tk.Label(inst_frame, text="Instituto de Criminalística", 
                            font=('Arial', 12), fg='#34495e', bg='#f0f0f0')
        inst_name.pack()
        
        inst_org = tk.Label(inst_frame, text="Policía Nacional del Paraguay", 
                           font=('Arial', 12), fg='#34495e', bg='#f0f0f0')
        inst_org.pack()
        
        # Copyright
        copyright_label = tk.Label(main_frame, text="© 2025 - Todos los derechos reservados", 
                                  font=('Arial', 10), fg='#95a5a6', bg='#f0f0f0')
        copyright_label.pack(pady=(20, 0))
        
        # Botón cerrar
        close_button = tk.Button(main_frame, text="Cerrar", 
                                command=about_window.destroy,
                                font=('Arial', 10, 'bold'),
                                bg='#3498db', fg='white',
                                relief='flat', padx=20, pady=5)
        close_button.pack(pady=(20, 0))
        
        # Centrar la ventana en la pantalla
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (about_window.winfo_reqwidth() // 2)
        y = (about_window.winfo_screenheight() // 2) - (about_window.winfo_reqheight() // 2)
        about_window.geometry(f"+{x}+{y}")
    
    def logout(self):
        """Cerrar sesión y volver al login"""
        if messagebox.askyesno("Cerrar Sesión", "¿Está seguro de cerrar sesión?"):
            # Limpiar la ventana actual sin destruirla
            for widget in self.parent.winfo_children():
                widget.destroy()
            
            # Crear nueva ventana de login en la misma ventana principal
            from login_system import LoginWindow
            login_window = LoginWindow(self.parent)
            login_window.pack(expand=True, fill='both')

def main():
    """Función principal para probar el menú"""
    root = tk.Tk()
    root.title("Sistema QUIRA")
    
    # Configurar icono de la ventana (256 píxeles)
    try:
        from icon_utils import set_large_256_icon
        if set_large_256_icon(root):
            print("[OK] Icono de 256px configurado correctamente en menú principal")
    except ImportError:
        print("[WARN] No se pudo importar icon_utils")
    
    # Usuario de prueba (ID real de la base de datos)
    user_data = {
        'id': 5,
        'nombre': 'GUILLERMO ANDRES',
        'apellido': 'RECALDE VALDEZ',
        'grado': 'Oficial Segundo',
        'rol': 'SUPERADMIN'
    }
    
    menu = MenuPrincipal(root, user_data)
    menu.pack(expand=True, fill='both')
    
    # Centrar la ventana en la pantalla
    root.update_idletasks()  # Actualizar para obtener dimensiones reales
    width = root.winfo_reqwidth()
    height = root.winfo_reqheight()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry('')
    
    # Hacer la ventana no redimensionable para mantener el tamaño del contenido
    root.resizable(True, True)
    
    root.mainloop()

if __name__ == "__main__":
    main() 