#!/usr/bin/env python3
"""
Script para cargar cédulas con problemas judiciales en la base de datos
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import connect_db
import csv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CargarCedulasProblemaJudicial(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        self.title("Cargar Cédulas con Problema Judicial")
        self.geometry("600x400")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        # Configurar estilo
        self.configure(bg='#f0f0f0')
        
        self.setup_ui()
        self.center_window()
        
    def setup_ui(self):
        """Configurar la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Título
        title_label = ttk.Label(main_frame, text="Cargar Cédulas con Problema Judicial", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Frame de instrucciones
        instructions_frame = ttk.LabelFrame(main_frame, text="Instrucciones", padding=15)
        instructions_frame.pack(fill='x', pady=(0, 20))
        
        instructions_text = """
1. Prepare un archivo CSV con las cédulas (una por línea)
2. El archivo debe tener una columna llamada 'cedula' o solo contener los números
3. Haga clic en 'Seleccionar Archivo' para cargar el CSV
4. Revise la vista previa y haga clic en 'Cargar Cédulas'
        """
        
        instructions_label = ttk.Label(instructions_frame, text=instructions_text, 
                                      font=('Segoe UI', 10), justify='left')
        instructions_label.pack()
        
        # Frame de carga
        load_frame = ttk.LabelFrame(main_frame, text="Cargar Archivo", padding=15)
        load_frame.pack(fill='x', pady=(0, 20))
        
        # Botón para seleccionar archivo
        self.select_button = ttk.Button(load_frame, text="Seleccionar Archivo CSV", 
                                       command=self.select_file)
        self.select_button.pack(pady=(0, 10))
        
        # Label para mostrar archivo seleccionado
        self.file_label = ttk.Label(load_frame, text="Ningún archivo seleccionado", 
                                   font=('Segoe UI', 9), foreground='gray')
        self.file_label.pack()
        
        # Frame de vista previa
        preview_frame = ttk.LabelFrame(main_frame, text="Vista Previa", padding=15)
        preview_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Treeview para mostrar vista previa
        self.preview_tree = ttk.Treeview(preview_frame, columns=('cedula',), show='headings', height=8)
        self.preview_tree.heading('cedula', text='Cédula')
        self.preview_tree.column('cedula', width=200, anchor='center')
        
        # Scrollbar para el treeview
        scrollbar = ttk.Scrollbar(preview_frame, orient='vertical', command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=scrollbar.set)
        
        self.preview_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Frame de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(0, 10))
        
        # Botón cargar
        self.load_button = ttk.Button(button_frame, text="Cargar Cédulas", 
                                     command=self.load_cedulas, state='disabled')
        self.load_button.pack(side='right', padx=(10, 0))
        
        # Botón limpiar base de datos
        self.clear_button = ttk.Button(button_frame, text="Limpiar Base de Datos", 
                                      command=self.clear_database)
        self.clear_button.pack(side='right')
        
        # Variables
        self.selected_file = None
        self.cedulas_data = []
        
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_reqwidth() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_reqheight() // 2)
        self.geometry(f"+{x}+{y}")
        
    def select_file(self):
        """Seleccionar archivo CSV"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_label.config(text=f"Archivo: {file_path.split('/')[-1]}")
            self.load_preview()
            
    def load_preview(self):
        """Cargar vista previa del archivo"""
        try:
            self.cedulas_data = []
            
            with open(self.selected_file, 'r', encoding='utf-8') as file:
                # Detectar si tiene encabezados
                first_line = file.readline().strip()
                file.seek(0)  # Volver al inicio
                
                reader = csv.reader(file)
                
                # Si la primera línea parece ser un encabezado
                if 'cedula' in first_line.lower():
                    next(reader)  # Saltar encabezado
                
                # Leer todas las cédulas
                for row in reader:
                    if row:  # Si la fila no está vacía
                        cedula = row[0].strip() if row[0] else ""
                        if cedula and cedula.isdigit():  # Validar que sea numérico
                            self.cedulas_data.append(cedula)
            
            # Limpiar vista previa
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
            
            # Mostrar primeras 50 cédulas en vista previa
            for i, cedula in enumerate(self.cedulas_data[:50]):
                self.preview_tree.insert('', 'end', values=(cedula,))
            
            if len(self.cedulas_data) > 50:
                self.preview_tree.insert('', 'end', values=(f"... y {len(self.cedulas_data) - 50} más",))
            
            # Habilitar botón de carga
            self.load_button.config(state='normal')
            
            messagebox.showinfo("Vista Previa", f"Se cargaron {len(self.cedulas_data)} cédulas válidas")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al leer el archivo: {e}")
            
    def load_cedulas(self):
        """Cargar cédulas en la base de datos"""
        if not self.cedulas_data:
            messagebox.showwarning("Advertencia", "No hay cédulas para cargar")
            return
            
        try:
            conn = connect_db()
            if not conn:
                messagebox.showerror("Error", "No se pudo conectar a la base de datos")
                return
                
            cursor = conn.cursor()
            
            # Contador de cédulas cargadas
            cargadas = 0
            duplicadas = 0
            
            for cedula in self.cedulas_data:
                try:
                    cursor.execute("""
                        INSERT INTO cedulas_problema_judicial (cedula) 
                        VALUES (%s)
                        ON CONFLICT (cedula) DO NOTHING
                    """, (cedula,))
                    
                    if cursor.rowcount > 0:
                        cargadas += 1
                    else:
                        duplicadas += 1
                        
                except Exception as e:
                    logger.error(f"Error al insertar cédula {cedula}: {e}")
                    continue
            
            conn.commit()
            cursor.close()
            conn.close()
            
            messagebox.showinfo("Carga Completada", 
                              f"Cédulas cargadas: {cargadas}\n"
                              f"Cédulas duplicadas (ignoradas): {duplicadas}\n"
                              f"Total procesadas: {len(self.cedulas_data)}")
            
            # Limpiar vista previa
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
            
            self.cedulas_data = []
            self.selected_file = None
            self.file_label.config(text="Ningún archivo seleccionado")
            self.load_button.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar cédulas: {e}")
            
    def clear_database(self):
        """Limpiar todas las cédulas de la base de datos"""
        if messagebox.askyesno("Confirmar", 
                              "¿Está seguro de que desea eliminar TODAS las cédulas con problemas judiciales?\n\n"
                              "Esta acción no se puede deshacer."):
            try:
                conn = connect_db()
                if not conn:
                    messagebox.showerror("Error", "No se pudo conectar a la base de datos")
                    return
                    
                cursor = conn.cursor()
                
                # Contar registros antes de eliminar
                cursor.execute("SELECT COUNT(*) FROM cedulas_problema_judicial")
                count = cursor.fetchone()[0]
                
                # Eliminar todos los registros
                cursor.execute("DELETE FROM cedulas_problema_judicial")
                
                conn.commit()
                cursor.close()
                conn.close()
                
                messagebox.showinfo("Base de Datos Limpiada", 
                                  f"Se eliminaron {count} cédulas de la base de datos")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al limpiar base de datos: {e}")

def main():
    """Función principal para probar"""
    root = tk.Tk()
    root.withdraw()
    
    app = CargarCedulasProblemaJudicial(root)
    root.mainloop()

if __name__ == "__main__":
    main()


