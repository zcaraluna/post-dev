#!/usr/bin/env python3
"""
Utilidades para configurar iconos en ventanas tkinter
"""

def set_window_icon(window, icon_filename="quira.png", large_icon=True):
    """
    Configurar icono para una ventana tkinter
    
    Args:
        window: Ventana tkinter (Tk o Toplevel)
        icon_filename: Nombre del archivo de icono (por defecto "quira.png")
        large_icon: Si True, usa tamaños más grandes para mejor visibilidad
    """
    try:
        from PIL import Image, ImageTk
        import os
        
        # Ruta del icono
        icon_path = os.path.join(os.path.dirname(__file__), icon_filename)
        
        if os.path.exists(icon_path):
            # Cargar imagen original
            original_image = Image.open(icon_path)
            
            # Crear múltiples tamaños de icono para mejor compatibilidad
            if large_icon:
                # Tamaños más grandes para mejor visibilidad en pantallas HD/4K
                icon_sizes = [24, 32, 48, 64, 96, 128, 256]
            else:
                # Tamaños estándar
                icon_sizes = [16, 24, 32, 48, 64]
            
            icon_photos = []
            
            for size in icon_sizes:
                # Redimensionar imagen manteniendo la calidad
                icon_image = original_image.resize((size, size), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon_image)
                icon_photos.append(icon_photo)
            
            # Configurar icono de la ventana con múltiples tamaños
            # El primer argumento True hace que se aplique a todas las ventanas secundarias también
            window.iconphoto(True, *icon_photos)
            
            # Mantener referencia a los iconos para evitar que sean recolectados por el garbage collector
            if not hasattr(window, '_icon_photos'):
                window._icon_photos = icon_photos
            
            return True
        else:
            print(f"⚠️ No se encontró el icono en: {icon_path}")
            return False
            
    except ImportError:
        print("⚠️ Pillow no está instalado para cargar el icono")
        return False
    except Exception as e:
        print(f"⚠️ No se pudo cargar el icono: {e}")
        return False

def set_extra_large_icon(window, icon_filename="quira.png"):
    """
    Configurar icono extra grande para ventanas principales
    
    Args:
        window: Ventana tkinter (Tk o Toplevel)
        icon_filename: Nombre del archivo de icono (por defecto "quira.png")
    """
    try:
        from PIL import Image, ImageTk
        import os
        
        # Ruta del icono
        icon_path = os.path.join(os.path.dirname(__file__), icon_filename)
        
        if os.path.exists(icon_path):
            # Cargar imagen original
            original_image = Image.open(icon_path)
            
            # Tamaños extra grandes para máxima visibilidad
            icon_sizes = [32, 48, 64, 96, 128, 256, 512]
            icon_photos = []
            
            for size in icon_sizes:
                # Redimensionar imagen manteniendo la calidad
                icon_image = original_image.resize((size, size), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon_image)
                icon_photos.append(icon_photo)
            
            # Configurar icono de la ventana con múltiples tamaños
            window.iconphoto(True, *icon_photos)
            
            # Mantener referencia a los iconos
            if not hasattr(window, '_icon_photos'):
                window._icon_photos = icon_photos
            
            return True
        else:
            print(f"⚠️ No se encontró el icono en: {icon_path}")
            return False
            
    except ImportError:
        print("⚠️ Pillow no está instalado para cargar el icono")
        return False
    except Exception as e:
        print(f"⚠️ No se pudo cargar el icono extra grande: {e}")
        return False

def set_large_256_icon(window, icon_filename="quira.png"):
    """
    Configurar icono de 256 píxeles como tamaño principal
    
    Args:
        window: Ventana tkinter (Tk o Toplevel)
        icon_filename: Nombre del archivo de icono (por defecto "quira.png")
    """
    try:
        from PIL import Image, ImageTk
        import os
        
        # Ruta del icono
        icon_path = os.path.join(os.path.dirname(__file__), icon_filename)
        
        if os.path.exists(icon_path):
            # Cargar imagen original
            original_image = Image.open(icon_path)
            
            # Crear icono de 256 píxeles como principal, con algunos tamaños de respaldo
            icon_sizes = [256, 128, 64, 48, 32]  # 256 como principal
            icon_photos = []
            
            for size in icon_sizes:
                # Redimensionar imagen manteniendo la calidad
                icon_image = original_image.resize((size, size), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon_image)
                icon_photos.append(icon_photo)
            
            # Configurar icono de la ventana (256px será el principal)
            window.iconphoto(True, *icon_photos)
            
            # Mantener referencia a los iconos
            if not hasattr(window, '_icon_photos'):
                window._icon_photos = icon_photos
            
            return True
        else:
            print(f"⚠️ No se encontró el icono en: {icon_path}")
            return False
            
    except ImportError:
        print("⚠️ Pillow no está instalado para cargar el icono")
        return False
    except Exception as e:
        print(f"⚠️ No se pudo cargar el icono de 256px: {e}")
        return False
