#!/usr/bin/env python3
"""
Sistema de login integrado para Sistema QUIRA
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from database import validate_user, update_password, USUARIO_ACTUAL
import ctypes

# Configurar DPI para Windows (HD/4K)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Per Monitor DPI Aware
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()  # Fallback para versiones anteriores
    except:
        pass

class LoginWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar la interfaz de login"""
        # Configurar el fondo principal
        self.configure(bg='#f8f9fa')
        
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
                
                print("✅ Imagen del instituto cargada correctamente en login")
            else:
                print(f"⚠️ No se encontró la imagen en: {img_path}")
                
        except ImportError:
            print("⚠️ Pillow no está instalado. Ejecute: pip install Pillow")
        except Exception as e:
            print(f"⚠️ No se pudo cargar la imagen del instituto: {e}")
            # Si no se puede cargar la imagen, continuar sin ella
        
        # Título principal
        title_label = tk.Label(center_frame, text="Sistema QUIRA", 
                              font=('Segoe UI', 18, 'bold'), 
                              fg='#2c3e50', bg='#f8f9fa')
        title_label.pack(pady=(0, 40))
        
        # Frame con gradiente sutil (simulado con color intermedio)
        login_frame = tk.Frame(center_frame, bg='#f5f6f7', relief='solid', bd=1)
        login_frame.pack(pady=10, padx=30)
        
        # Título del formulario
        login_title = tk.Label(login_frame, text="Iniciar Sesión", 
                              font=('Segoe UI', 14, 'bold'), 
                              fg='#2c3e50', bg='#f5f6f7')
        login_title.pack(pady=(25, 30))
        
        # Frame para campos de entrada con gradiente sutil
        fields_frame = tk.Frame(login_frame, bg='#f7f8f9')
        fields_frame.pack(pady=(0, 25), padx=40)
        
        # Usuario
        user_label = tk.Label(fields_frame, text="Usuario", 
                             font=('Segoe UI', 10), 
                             fg='#495057', bg='#f7f8f9', anchor='w')
        user_label.pack(anchor='w', pady=(0, 8))
        
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(fields_frame, textvariable=self.username_var,
                                      font=('Segoe UI', 10),
                                      relief='solid', bd=1,
                                      highlightthickness=1, highlightcolor='#2E5090',
                                      bg='white', width=20)
        self.username_entry.pack(pady=(0, 20))
        
        # Contraseña
        pass_label = tk.Label(fields_frame, text="Contraseña", 
                             font=('Segoe UI', 10), 
                             fg='#495057', bg='#f7f8f9', anchor='w')
        pass_label.pack(anchor='w', pady=(0, 8))
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(fields_frame, textvariable=self.password_var, show='*',
                                      font=('Segoe UI', 10),
                                      relief='solid', bd=1,
                                      highlightthickness=1, highlightcolor='#2E5090',
                                      bg='white', width=20)
        self.password_entry.pack(pady=(0, 30))
        
        # Botón de login con estilo moderno y elegante
        self.login_btn = tk.Button(fields_frame, text="Iniciar Sesión", command=self.login,
                                  font=('Segoe UI', 11, 'bold'),
                                  fg='white', bg='#2E5090',
                                  activebackground='#2E5090',
                                  relief='flat', bd=0,
                                  padx=40, pady=14,
                                  cursor='hand2')
        self.login_btn.pack()
        
        # Configurar eventos
        self.password_entry.bind('<Return>', lambda e: self.login())
        self.username_entry.focus()
        
    def login(self):
        """Procesar el login"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return
        
        # Deshabilitar botón durante el login
        self.login_btn.config(state='disabled', text="Conectando...")
        
        # Procesar login en hilo separado
        def login_thread():
            try:
                user_data = validate_user(username, password)
                
                if user_data:
                    # Login exitoso
                    try:
                        if self.parent.winfo_exists():
                            self.parent.after(0, self.login_success, user_data)
                    except (tk.TclError, RuntimeError):
                        # La ventana se cerró durante el proceso
                        pass
                else:
                    # Login fallido
                    try:
                        if self.parent.winfo_exists():
                            self.parent.after(0, self.login_failed)
                    except (tk.TclError, RuntimeError):
                        # La ventana se cerró durante el proceso
                        pass
                    
            except Exception as e:
                try:
                    if self.parent.winfo_exists():
                        self.parent.after(0, lambda: self.login_error(str(e)))
                except (tk.TclError, RuntimeError):
                    # La ventana se cerró durante el proceso
                    pass
        
        threading.Thread(target=login_thread, daemon=True).start()
    
    def login_success(self, user_data):
        """Manejar login exitoso"""
        self.login_btn.config(state='normal', text="Iniciar Sesión")
        
        # Verificar si es primer inicio
        if user_data.get('primer_inicio', False):
            self.show_change_password_dialog(user_data)
        else:
            self.open_main_menu(user_data)
    
    def login_failed(self):
        """Manejar login fallido"""
        self.login_btn.config(state='normal', text="Iniciar Sesión")
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")
        self.password_var.set("")
        self.password_entry.focus()
    
    def login_error(self, error_msg):
        """Manejar error de login"""
        self.login_btn.config(state='normal', text="Iniciar Sesión")
        messagebox.showerror("Error", f"Error de conexión: {error_msg}")
    
    def show_change_password_dialog(self, user_data):
        """Mostrar diálogo para cambiar contraseña"""
        dialog = ChangePasswordDialog(self, user_data)
        self.wait_window(dialog)
        
        # Si se cambió la contraseña exitosamente, abrir menú principal
        if dialog.password_changed:
            self.open_main_menu(user_data)
    
    def open_main_menu(self, user_data):
        """Abrir menú principal"""
        from menu_principal import MenuPrincipal
        self.pack_forget()  # Ocultar login
        menu = MenuPrincipal(self.parent, user_data)
        menu.pack(expand=True, fill='both')  # Empaquetar el menú

class ChangePasswordDialog(tk.Toplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.user_data = user_data
        self.password_changed = False
        
        self.title("Cambiar Contraseña")
        self.geometry("")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Configurar icono de la ventana
        try:
            from icon_utils import set_window_icon
            set_window_icon(self)
        except ImportError:
            pass
        
        # Configurar estilo moderno
        self.configure(bg='#f8f9fa')
        
        self.setup_ui()
        self.center_window()
        
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        # Frame principal
        main_frame = tk.Frame(self, bg='#f8f9fa', padx=30, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        # Cargar y mostrar imagen institucional
        self.load_institutional_image(main_frame)
        
        # Título principal
        title_frame = tk.Frame(main_frame, bg='#f8f9fa')
        title_frame.pack(fill='x', pady=(20, 30))
        
        title_label = tk.Label(title_frame, text="PRIMER INICIO - CAMBIAR CONTRASEÑA", 
                               font=('Segoe UI', 16, 'bold'), 
                               fg='#2c3e50', bg='#f8f9fa')
        title_label.pack()
        
        # Mensaje de bienvenida
        welcome_text = f"BIENVENIDO {self.user_data['nombre']} {self.user_data['apellido']}"
        welcome_label = tk.Label(title_frame, text=welcome_text, 
                                font=('Segoe UI', 12, 'bold'), 
                                fg='#2E5090', bg='#f8f9fa')
        welcome_label.pack(pady=(10, 5))
        
        subtitle_label = tk.Label(title_frame, text="Por favor cambie su contraseña por defecto", 
                                  font=('Segoe UI', 10), 
                                  fg='#6c757d', bg='#f8f9fa')
        subtitle_label.pack()
        
        # Frame para el formulario
        form_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        form_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Frame interno para los campos
        fields_frame = tk.Frame(form_frame, bg='white')
        fields_frame.pack(pady=30, padx=40)
        
        # Nueva contraseña
        new_pass_label = tk.Label(fields_frame, text="Nueva Contraseña:", 
                                  font=('Segoe UI', 10, 'bold'), 
                                  fg='#2c3e50', bg='white', anchor='w')
        new_pass_label.pack(anchor='w', pady=(0, 8))
        
        self.new_password_var = tk.StringVar()
        self.new_password_entry = tk.Entry(fields_frame, textvariable=self.new_password_var, 
                                          show='*', font=('Segoe UI', 10),
                                          relief='solid', bd=1,
                                          highlightthickness=1, highlightcolor='#2E5090',
                                          bg='white', width=25)
        self.new_password_entry.pack(fill='x', pady=(0, 20))
        
        # Confirmar contraseña
        confirm_pass_label = tk.Label(fields_frame, text="Confirmar Contraseña:", 
                                      font=('Segoe UI', 10, 'bold'), 
                                      fg='#2c3e50', bg='white', anchor='w')
        confirm_pass_label.pack(anchor='w', pady=(0, 8))
        
        self.confirm_password_var = tk.StringVar()
        self.confirm_password_entry = tk.Entry(fields_frame, textvariable=self.confirm_password_var, 
                                              show='*', font=('Segoe UI', 10),
                                              relief='solid', bd=1,
                                              highlightthickness=1, highlightcolor='#2E5090',
                                              bg='white', width=25)
        self.confirm_password_entry.pack(fill='x', pady=(0, 30))
        
        # Frame para botones centrados
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(fill='x', pady=20)
        
        # Frame interno para centrar los botones
        button_center_frame = tk.Frame(button_frame, bg='#f8f9fa')
        button_center_frame.pack(expand=True)
        
        # Botón Guardar
        self.save_btn = tk.Button(button_center_frame, text="GUARDAR", 
                                 command=self.save_password,
                                 font=('Segoe UI', 12, 'bold'),
                                 fg='white', bg='#2E902E',
                                 activebackground='#2E902E',
                                 relief='flat', bd=0,
                                 padx=30, pady=12,
                                 cursor='hand2')
        
        # Botón Cancelar
        self.cancel_btn = tk.Button(button_center_frame, text="CANCELAR", 
                                   command=self.cancel,
                                   font=('Segoe UI', 12),
                                   fg='white', bg='#902E2E',
                                   activebackground='#902E2E',
                                   relief='flat', bd=0,
                                   padx=30, pady=12,
                                   cursor='hand2')
        
        # Centrar los botones
        self.save_btn.pack(side='left', padx=(0, 10))
        self.cancel_btn.pack(side='left')
        
        # Configurar eventos
        self.new_password_entry.bind('<Return>', lambda e: self.confirm_password_entry.focus())
        self.confirm_password_entry.bind('<Return>', lambda e: self.save_password())
        self.new_password_entry.focus()
        
    def load_institutional_image(self, parent):
        """Cargar y mostrar imagen institucional"""
        try:
            from PIL import Image, ImageTk
            import os
            
            # Ruta de la imagen
            image_path = os.path.join(os.path.dirname(__file__), 'instituto.png')
            
            if os.path.exists(image_path):
                # Cargar imagen
                image = Image.open(image_path)
                
                # Redimensionar manteniendo proporción (máximo 100px de alto)
                max_height = 100
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
            pass
        
    def center_window(self):
        """Centrar la ventana"""
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def save_password(self):
        """Guardar nueva contraseña"""
        new_password = self.new_password_var.get().strip()
        confirm_password = self.confirm_password_var.get().strip()
        
        # Validaciones
        if not new_password or not confirm_password:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return
        
        if new_password != confirm_password:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            self.confirm_password_var.set("")
            self.confirm_password_entry.focus()
            return
        
        if len(new_password) < 6:
            messagebox.showerror("Error", "La contraseña debe tener al menos 6 caracteres")
            return
        
        # Deshabilitar botón durante el proceso
        self.save_btn.config(state='disabled', text="Guardando...")
        
        # Procesar en hilo separado
        def save_thread():
            try:
                success = update_password(self.user_data['id'], new_password)
                
                if success:
                    self.password_changed = True
                    try:
                        if self.winfo_exists():
                            self.after(0, self.save_success)
                    except (tk.TclError, RuntimeError):
                        # La ventana se cerró durante el proceso
                        pass
                else:
                    try:
                        if self.winfo_exists():
                            self.after(0, self.save_failed)
                    except (tk.TclError, RuntimeError):
                        # La ventana se cerró durante el proceso
                        pass
                    
            except Exception as e:
                try:
                    if self.winfo_exists():
                        self.after(0, lambda: self.save_error(str(e)))
                except (tk.TclError, RuntimeError):
                    # La ventana se cerró durante el proceso
                    pass
        
        threading.Thread(target=save_thread, daemon=True).start()
    
    def save_success(self):
        """Manejar guardado exitoso"""
        self.save_btn.config(state='normal', text="Guardar")
        messagebox.showinfo("Éxito", "Contraseña actualizada correctamente")
        self.destroy()
    
    def save_failed(self):
        """Manejar guardado fallido"""
        self.save_btn.config(state='normal', text="Guardar")
        messagebox.showerror("Error", "No se pudo actualizar la contraseña")
    
    def save_error(self, error_msg):
        """Manejar error de guardado"""
        self.save_btn.config(state='normal', text="Guardar")
        messagebox.showerror("Error", f"Error al actualizar contraseña: {error_msg}")
    
    def cancel(self):
        """Cancelar cambio de contraseña"""
        if messagebox.askyesno("Confirmar", "¿Está seguro de cancelar? Deberá cambiar la contraseña en el próximo inicio."):
            self.destroy()

def main():
    """Función principal para probar el login"""
    root = tk.Tk()
    root.title("Sistema QUIRA - Login")
    
    # Inicializar base de datos
    from database import init_database
    if not init_database():
        messagebox.showerror("Error", "No se pudo inicializar la base de datos")
        root.destroy()
        return
    
    # Crear ventana de login
    login_window = LoginWindow(root)
    login_window.pack(expand=True, fill='both')
    
    # Centrar la ventana en la pantalla
    root.update_idletasks()  # Actualizar para obtener dimensiones reales
    width = root.winfo_reqwidth()
    height = root.winfo_reqheight()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Hacer la ventana no redimensionable para mantener el tamaño del contenido
    root.resizable(False, False)
    
    root.mainloop()

if __name__ == "__main__":
    main() 