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
            
            # Ruta de la imagen (usar ruta absoluta)
            img_path = os.path.join(os.path.dirname(__file__), "instituto.png")
            
            if os.path.exists(img_path):
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
                
                print("✅ Imagen del instituto cargada correctamente")
            else:
                print(f"⚠️ No se encontró la imagen en: {img_path}")
                
        except ImportError:
            print("⚠️ Pillow no está instalado. Ejecute: pip install Pillow")
        except Exception as e:
            print(f"⚠️ No se pudo cargar la imagen del instituto: {e}")
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
        
        # Menú Sistema
        sistema_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Sistema", menu=sistema_menu)
        sistema_menu.add_command(label="Gestión ZKTeco", command=self.gestion_zkteco)
        
        # Solo mostrar gestión de usuarios y configuración para superadmin
        if self.user_data["rol"] == "SUPERADMIN":
            sistema_menu.add_separator()
            sistema_menu.add_command(label="Gestión de Usuarios", command=self.gestion_usuarios)
            sistema_menu.add_command(label="Configuración del Sistema", command=self.configuracion_sistema)
        
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
        from buscar_postulantes import BuscarPostulantes
        BuscarPostulantes(self, self.user_data)
    
    def agregar_postulante(self):
        """Abrir ventana de agregar postulante"""
        from agregar_postulante import AgregarPostulante
        AgregarPostulante(self, self.user_data)
    
    def gestion_zkteco(self):
        """Abrir gestión del dispositivo ZKTeco"""
        from gestion_zkteco import GestionZKTeco
        GestionZKTeco(self, self.user_data)
    
    def ver_lista_postulantes(self):
        """Abrir lista completa de postulantes"""
        from lista_postulantes import ListaPostulantes
        ListaPostulantes(self, self.user_data)
    
    def ver_estadisticas(self):
        """Abrir estadísticas del sistema"""
        from estadisticas import Estadisticas
        Estadisticas(self, self.user_data)
    
    def gestion_usuarios(self):
        """Abrir gestión de usuarios"""
        from gestion_usuarios import GestionUsuarios
        GestionUsuarios(self, self.user_data)
    
    def configuracion_sistema(self):
        """Abrir configuración del sistema"""
        from sistema_respaldo import InterfazRespaldo
        InterfazRespaldo(self.parent)
    
    def acerca_de(self):
        """Mostrar información sobre el sistema"""
        messagebox.showinfo(
            "Acerca de",
            "Sistema: QUIRA\n\n"
            "Versión: 1.0\n"
            "Desarrollado para el Instituto de Criminalística\n"
            "Policía Nacional del Paraguay\n\n"
            "© 2025 - Todos los derechos reservados"
        )
    
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
            print("✅ Icono de 256px configurado correctamente en menú principal")
    except ImportError:
        print("⚠️ No se pudo importar icon_utils")
    
    # Usuario de prueba
    user_data = {
        'id': 1,
        'nombre': 'Guillermo Andres',
        'apellido': 'Recalde Valdez',
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