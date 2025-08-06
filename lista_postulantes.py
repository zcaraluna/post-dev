#!/usr/bin/env python3
"""
Módulo para mostrar lista completa de postulantes
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import get_postulantes, eliminar_postulante
from editar_postulante import EditarPostulante

class ListaPostulantes(tk.Toplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.parent = parent
        self.user_data = user_data
        
        self.title("Lista de Postulantes")
        self.geometry("1200x800")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.center_window()
        self.load_postulantes()
        
    def setup_ui(self):
        """Configurar la interfaz"""
        # Configurar estilo
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Info.TLabel', font=('Arial', 10), foreground='#34495e')
        style.configure('Header.TFrame', background='#ecf0f1')
        
        # Frame principal sin canvas (más simple y eficiente)
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Título y controles superiores
        header_frame = ttk.Frame(main_frame, style='Header.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Título
        title_label = ttk.Label(header_frame, text="Lista de Postulantes", style='Title.TLabel')
        title_label.pack(side='left', padx=20, pady=15)
        
        # Controles
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side='right', padx=20, pady=15)
        
        # Botones de acción (sin iconos)
        ttk.Button(controls_frame, text="Actualizar", command=self.load_postulantes).pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Exportar", command=self.export_data).pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Imprimir", command=self.print_data).pack(side='left')
        
        # Frame de filtros
        filter_frame = ttk.LabelFrame(main_frame, text="Filtros de Búsqueda", padding=15)
        filter_frame.pack(fill='x', pady=(0, 20))
        
        self.create_filters(filter_frame)
        
        # Frame de tabla con scroll propio
        table_frame = ttk.LabelFrame(main_frame, text="Postulantes Registrados", padding=15)
        table_frame.pack(fill='both', expand=True)
        
        self.create_table(table_frame)
        
        # Frame de información
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill='x', pady=(15, 0))
        
        self.info_label = ttk.Label(info_frame, text="Cargando postulantes...", style='Info.TLabel')
        self.info_label.pack(side='left')
        
        # Barra de estado
        self.status_label = ttk.Label(info_frame, text="", style='Info.TLabel')
        self.status_label.pack(side='right')
        
    def create_filters(self, parent):
        """Crear controles de filtro"""
        # Variables de filtro
        self.filter_nombre = tk.StringVar()
        self.filter_cedula = tk.StringVar()
        self.filter_fecha_desde = tk.StringVar()
        self.filter_fecha_hasta = tk.StringVar()
        
        # Frame de filtros
        filters_frame = ttk.Frame(parent)
        filters_frame.pack(fill='x')
        
        # Filtro por nombre
        ttk.Label(filters_frame, text="Nombre:", style='Info.TLabel').grid(row=0, column=0, sticky='w', pady=8)
        ttk.Entry(filters_frame, textvariable=self.filter_nombre, width=20).grid(row=0, column=1, padx=(10, 20), pady=8)
        
        # Filtro por cédula
        ttk.Label(filters_frame, text="Cédula:", style='Info.TLabel').grid(row=0, column=2, sticky='w', pady=8)
        ttk.Entry(filters_frame, textvariable=self.filter_cedula, width=15).grid(row=0, column=3, padx=(10, 20), pady=8)
        
        # Filtro por fecha desde
        ttk.Label(filters_frame, text="Desde:", style='Info.TLabel').grid(row=0, column=4, sticky='w', pady=8)
        ttk.Entry(filters_frame, textvariable=self.filter_fecha_desde, width=12).grid(row=0, column=5, padx=(10, 20), pady=8)
        
        # Filtro por fecha hasta
        ttk.Label(filters_frame, text="Hasta:", style='Info.TLabel').grid(row=0, column=6, sticky='w', pady=8)
        ttk.Entry(filters_frame, textvariable=self.filter_fecha_hasta, width=12).grid(row=0, column=7, padx=(10, 0), pady=8)
        
        # Botones de filtro
        filter_buttons_frame = ttk.Frame(parent)
        filter_buttons_frame.pack(fill='x', pady=(15, 0))
        
        ttk.Button(filter_buttons_frame, text="Aplicar Filtros", command=self.apply_filters).pack(side='left', padx=(0, 10))
        ttk.Button(filter_buttons_frame, text="Limpiar Filtros", command=self.clear_filters).pack(side='left')
        
        # Configurar grid
        filters_frame.columnconfigure(1, weight=1)
        filters_frame.columnconfigure(3, weight=1)
        filters_frame.columnconfigure(5, weight=1)
        filters_frame.columnconfigure(7, weight=1)
        
    def create_table(self, parent):
        """Crear tabla de postulantes"""
        # Crear Treeview con solo las columnas principales (sin ID visible)
        columns = ('ID', 'Nombre', 'Apellido', 'Cédula')
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', height=25)
        
        # Configurar columnas (ID oculto pero disponible para funciones internas)
        self.tree.heading('Nombre', text='Nombre')
        self.tree.heading('Apellido', text='Apellido')
        self.tree.heading('Cédula', text='Cédula')
        
        # Configurar anchos de columna (ID oculto, columnas principales más anchas)
        self.tree.column('ID', width=0, minwidth=0, stretch=False)  # Ocultar columna ID
        self.tree.column('Nombre', width=250, minwidth=200)
        self.tree.column('Apellido', width=250, minwidth=200)
        self.tree.column('Cédula', width=200, minwidth=150)
        
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
            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Obtener postulantes
            postulantes = get_postulantes()
            
            if postulantes:
                for postulante in postulantes:
                    # Formatear fechas
                    fecha_nac = postulante[4].strftime('%d/%m/%Y') if postulante[4] else 'N/A'
                    fecha_registro = postulante[6].strftime('%d/%m/%Y %H:%M') if postulante[6] else 'N/A'
                    
                    # Usar el nombre del registrador almacenado directamente
                    # registrado_por está en la posición 14 según la consulta SQL
                    registrador = postulante[14] if postulante[14] else 'N/A'
                    
                    self.tree.insert('', 'end', values=(
                        postulante[0],  # ID
                        postulante[1],  # Nombre
                        postulante[2],  # Apellido
                        postulante[3]   # Cédula
                    ))
                    
                self.info_label.config(text=f"Total: {len(postulantes)} postulante(s)")
                self.status_label.config(text=f"Última actualización: {self.get_current_time()}")
            else:
                self.info_label.config(text="No hay postulantes registrados")
                self.status_label.config(text="")
                
        except Exception as e:
            self.info_label.config(text=f"Error al cargar postulantes: {e}")
            messagebox.showerror("Error", f"Error al cargar postulantes: {e}")
            
    def get_registrador_name(self, user_id):
        """Obtener nombre del usuario registrador"""
        try:
            from database import connect_db
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre, apellido FROM usuarios WHERE id = %s", (user_id,))
                result = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if result:
                    return f"{result[0]} {result[1]}"
        except:
            pass
        return "N/A"
        
    def get_current_time(self):
        """Obtener hora actual formateada"""
        from datetime import datetime
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
    def apply_filters(self):
        """Aplicar filtros a la tabla"""
        # Por ahora, recargar todos los datos
        # En una implementación completa, aquí se aplicarían los filtros
        self.load_postulantes()
        messagebox.showinfo("Filtros", "Función de filtros en desarrollo")
        
    def clear_filters(self):
        """Limpiar filtros"""
        self.filter_nombre.set("")
        self.filter_cedula.set("")
        self.filter_fecha_desde.set("")
        self.filter_fecha_hasta.set("")
        self.load_postulantes()
        
    def export_data(self):
        """Exportar datos a archivo"""
        try:
            from tkinter import filedialog
            import csv
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Guardar lista de postulantes"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Escribir encabezados (sin ID)
                    headers = ['Nombre', 'Apellido', 'Cédula']
                    writer.writerow(headers)
                    
                    # Escribir datos (sin ID)
                    for item in self.tree.get_children():
                        values = self.tree.item(item)['values']
                        # Omitir el ID (primer elemento) y escribir solo Nombre, Apellido, Cédula
                        writer.writerow(values[1:4])
                        
                messagebox.showinfo("Éxito", f"Datos exportados a {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {e}")
            
    def print_data(self):
        """Imprimir datos"""
        messagebox.showinfo("Imprimir", "Función de impresión en desarrollo")
        
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
        """Mostrar detalles del postulante"""
        if not values:
            return
            
        # Obtener datos completos del postulante desde la base de datos
        postulante_id = values[0]
        try:
            from database import connect_db
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT p.id, p.nombre, p.apellido, p.cedula, p.fecha_nacimiento, p.telefono, 
                           p.fecha_registro, p.registrado_por, p.uid_k40, p.aparato_id,
                           ab.serial as aparato_serial, ab.nombre as aparato_nombre
                    FROM postulantes p
                    LEFT JOIN aparatos_biometricos ab ON p.aparato_id = ab.id
                    WHERE p.id = %s
                """, (postulante_id,))
                postulante = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if postulante:
                    # Formatear fechas
                    fecha_nac = postulante[4].strftime('%d/%m/%Y') if postulante[4] else 'N/A'
                    fecha_registro = postulante[6].strftime('%d/%m/%Y %H:%M') if postulante[6] else 'N/A'
                    
                    # Información del dispositivo biométrico
                    uid_k40 = postulante[8] if postulante[8] else 'N/A'
                    aparato_serial = postulante[10] if postulante[10] else 'N/A'
                    aparato_nombre = postulante[11] if postulante[11] else 'N/A'
                    
                    # Crear ventana de detalles
                    details_window = tk.Toplevel(self)
                    details_window.title(f"Detalles del Postulante - {postulante[1]} {postulante[2]}")
                    details_window.geometry("700x600")
                    details_window.transient(self)
                    details_window.grab_set()
                    
                    # Mostrar información detallada
                    info_text = f"""
                    INFORMACIÓN DEL POSTULANTE
                    
                    ID: {postulante[0]}
                    Nombre: {postulante[1]}
                    Apellido: {postulante[2]}
                    Cédula: {postulante[3]}
                    Fecha de Nacimiento: {fecha_nac}
                    Teléfono: {postulante[5] or 'N/A'}
                    
                    Fecha de Registro: {fecha_registro}
                    Registrado por: {postulante[7] or 'N/A'}
                    
                    INFORMACIÓN BIOMÉTRICA
                    UID en K40: {uid_k40}
                    Dispositivo: {aparato_nombre}
                    Serial del Dispositivo: {aparato_serial}
                    
                    INFORMACIÓN ADICIONAL
                    - Estado: Activo
                    - Última actualización: {self.get_current_time()}
                    """
                    
                    text_widget = tk.Text(details_window, wrap='word', padx=20, pady=20, font=('Arial', 10))
                    text_widget.pack(expand=True, fill='both')
                    text_widget.insert('1.0', info_text)
                    text_widget.config(state='disabled')
                else:
                    messagebox.showerror("Error", "No se encontró el postulante en la base de datos.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener detalles: {e}")
        
    def edit_postulante(self, values):
        """Editar postulante"""
        if not values:
            return
            
        postulante_id = values[0]  # ID del postulante
        
        # Abrir ventana de edición
        edit_window = EditarPostulante(self, self.user_data, postulante_id)
        
        # Esperar a que se cierre la ventana de edición
        self.wait_window(edit_window)
        
        # Actualizar la lista después de editar
        self.load_postulantes()
        
    def delete_postulante(self, values):
        """Eliminar postulante"""
        if not values:
            return
            
        postulante_id = values[0]  # ID del postulante
        
        # Obtener nombre y apellido desde la base de datos
        try:
            from database import connect_db
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre, apellido FROM postulantes WHERE id = %s", (postulante_id,))
                result = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if result:
                    nombre = result[0]
                    apellido = result[1]
                    
                    # Confirmar eliminación
                    if messagebox.askyesno("Confirmar Eliminación", 
                                          f"¿Está seguro de eliminar al postulante {nombre} {apellido}?\n\n"
                                          "Esta acción no se puede deshacer."):
                        
                        # Intentar eliminar
                        if eliminar_postulante(postulante_id):
                            messagebox.showinfo("Éxito", f"Postulante {nombre} {apellido} eliminado correctamente.")
                            # Actualizar la lista
                            self.load_postulantes()
                        else:
                            messagebox.showerror("Error", "No se pudo eliminar el postulante.")
                else:
                    messagebox.showerror("Error", "No se encontró el postulante en la base de datos.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener datos del postulante: {e}")

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
    
    app = ListaPostulantes(root, user_data)
    root.mainloop()

if __name__ == "__main__":
    main() 