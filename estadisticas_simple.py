#!/usr/bin/env python3
"""
Módulo de estadísticas del sistema - Versión simplificada y funcional
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import connect_db
from datetime import datetime, timedelta
import ctypes

# Configurar DPI para Windows (HD/4K)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

class Estadisticas(tk.Toplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.parent = parent
        self.user_data = user_data
        
        self.title("Estadísticas del Sistema")
        self.geometry('')
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        # Configurar estilo consistente con el resto del sistema
        self.configure(bg='#f8f9fa')
        
        self.setup_ui()
        self.center_window()
        
        # Cargar estadísticas después de que la interfaz esté completamente creada
        self.after(100, self.load_statistics)
        
    def setup_ui(self):
        """Configurar la interfaz principal"""
        # Frame principal con padding optimizado para pantalla completa
        main_frame = tk.Frame(self, bg='#f8f9fa', padx=20, pady=15)
        main_frame.pack(expand=True, fill='both')
        
        # Título principal
        title_frame = tk.Frame(main_frame, bg='#f8f9fa')
        title_frame.pack(fill='x', pady=(0, 15))
        
        title_label = tk.Label(title_frame, text="ESTADÍSTICAS DEL SISTEMA", 
                               font=('Segoe UI', 16, 'bold'), 
                               fg='#2c3e50', bg='#f8f9fa')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Resumen de actividad y métricas", 
                                 font=('Segoe UI', 10), 
                                 fg='#7f8c8d', bg='#f8f9fa')
        subtitle_label.pack()
        
        # Frame de estadísticas detalladas
        details_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        details_frame.pack(fill='both', expand=True)
        
        # Título de estadísticas detalladas
        details_title = tk.Label(details_frame, text="ESTADÍSTICAS DETALLADAS", 
                                font=('Segoe UI', 12, 'bold'), 
                                fg='#2c3e50', bg='white')
        details_title.pack(pady=(12, 8))
        
        self.create_detailed_stats(details_frame)
        
    def create_detailed_stats(self, parent):
        """Crear estadísticas detalladas"""
        # Notebook para pestañas
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Pestaña 1: Resumen general
        summary_frame = tk.Frame(notebook, bg='white')
        notebook.add(summary_frame, text="Resumen General")
        self.create_summary_tab(summary_frame)
        
        # Pestaña 2: Estadísticas generales
        general_frame = tk.Frame(notebook, bg='white')
        notebook.add(general_frame, text="Estadísticas Generales")
        self.create_general_tab(general_frame)
        
        # Pestaña 3: Registros por hora
        hourly_frame = tk.Frame(notebook, bg='white')
        notebook.add(hourly_frame, text="Registros por Hora")
        self.create_hourly_tab(hourly_frame)
        
    def create_summary_tab(self, parent):
        """Crear pestaña de resumen general"""
        # Crear contenido directamente sin scroll complicado
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Contenido del resumen
        self.create_summary_content(main_frame)
        
    def create_summary_content(self, parent):
        """Crear contenido del resumen"""
        # Métricas principales
        metrics_frame = tk.Frame(parent, bg='white')
        metrics_frame.pack(fill='x', pady=(0, 20))
        
        # Título de métricas
        metrics_title = tk.Label(metrics_frame, text="Métricas Principales", 
                                font=('Segoe UI', 12, 'bold'), 
                                fg='#2c3e50', bg='white')
        metrics_title.pack(anchor='w', pady=(0, 10))
        
        # Variables para métricas
        self.total_postulantes_var = tk.StringVar(value="0")
        self.total_usuarios_var = tk.StringVar(value="0")
        self.postulantes_hoy_var = tk.StringVar(value="0")
        self.postulantes_semana_var = tk.StringVar(value="0")
        self.postulantes_mes_var = tk.StringVar(value="0")
        
        # Frame para las métricas
        metrics_container = tk.Frame(metrics_frame, bg='white')
        metrics_container.pack(fill='x')
        
        # Crear métricas en una cuadrícula
        metrics = [
            ("Total de Postulantes", self.total_postulantes_var, "#4a90e2"),
            ("Total de Usuarios", self.total_usuarios_var, "#4a90e2"),
            ("Postulantes Hoy", self.postulantes_hoy_var, "#4a90e2"),
            ("Postulantes Esta Semana", self.postulantes_semana_var, "#4a90e2"),
            ("Postulantes Este Mes", self.postulantes_mes_var, "#4a90e2")
        ]
        
        for i, (label, var, color) in enumerate(metrics):
            metric_frame = tk.Frame(metrics_container, bg='white')
            metric_frame.grid(row=0, column=i, padx=10, pady=10, sticky='ew')
            
            # Label del título
            title_label = tk.Label(metric_frame, text=label, 
                                  font=('Segoe UI', 9), 
                                  fg='#7f8c8d', bg='white')
            title_label.pack()
            
            # Valor de la métrica
            value_label = tk.Label(metric_frame, textvariable=var, 
                                  font=('Segoe UI', 18, 'bold'), 
                                  fg=color, bg='white')
            value_label.pack()
            
            # Configurar peso de columna
            metrics_container.columnconfigure(i, weight=1)
        
        # Estadísticas generales
        general_frame = tk.Frame(parent, bg='white')
        general_frame.pack(fill='x', pady=(0, 20))
        
        # Título
        general_title = tk.Label(general_frame, text="Estadísticas Generales", 
                                font=('Segoe UI', 12, 'bold'), 
                                fg='#2c3e50', bg='white')
        general_title.pack(anchor='w', pady=(0, 10))
        
        # Variables para estadísticas
        self.stats_vars = {
            'promedio_edad': tk.StringVar(value="N/A"),
            'edad_minima': tk.StringVar(value="N/A"),
            'edad_maxima': tk.StringVar(value="N/A"),
            'ultimo_registro': tk.StringVar(value="N/A"),
            'primer_registro': tk.StringVar(value="N/A"),
            'total_unidades': tk.StringVar(value="0")
        }
        
        # Crear estadísticas en una cuadrícula
        stats_grid = tk.Frame(general_frame, bg='white')
        stats_grid.pack(fill='x')
        
        stats_data = [
            ("Promedio de Edad:", self.stats_vars['promedio_edad']),
            ("Edad Mínima:", self.stats_vars['edad_minima']),
            ("Edad Máxima:", self.stats_vars['edad_maxima']),
            ("Último Registro:", self.stats_vars['ultimo_registro']),
            ("Primer Registro:", self.stats_vars['primer_registro']),
            ("Total de Unidades:", self.stats_vars['total_unidades'])
        ]
        
        for i, (label, var) in enumerate(stats_data):
            row = i // 2
            col = i % 2
            
            stat_frame = tk.Frame(stats_grid, bg='white')
            stat_frame.grid(row=row, column=col, sticky='ew', padx=(0, 20), pady=5)
            
            tk.Label(stat_frame, text=label, 
                    font=('Segoe UI', 9), 
                    fg='#7f8c8d', bg='white').pack(anchor='w')
            tk.Label(stat_frame, textvariable=var, 
                    font=('Segoe UI', 11, 'bold'), 
                    fg='#2c3e50', bg='white').pack(anchor='w')
            
            stats_grid.columnconfigure(col, weight=1)
        
    def create_general_tab(self, parent):
        """Crear pestaña de estadísticas generales"""
        # Mensaje simple por ahora
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        title = tk.Label(main_frame, text="Estadísticas Generales", 
                        font=('Segoe UI', 18, 'bold'), 
                        fg='#2c3e50', bg='white')
        title.pack(pady=50)
        
        message = tk.Label(main_frame, text="Secciones detalladas se cargarán aquí\nuna vez corregidos los problemas", 
                          font=('Segoe UI', 12), 
                          fg='#7f8c8d', bg='white')
        message.pack()
        
    def create_hourly_tab(self, parent):
        """Crear pestaña de registros por hora"""
        # Mensaje simple por ahora
        main_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        title = tk.Label(main_frame, text="Registros por Hora", 
                        font=('Segoe UI', 18, 'bold'), 
                        fg='#2c3e50', bg='white')
        title.pack(pady=50)
        
        message = tk.Label(main_frame, text="Funcionalidad de registros por hora\nse implementará una vez solucionados los problemas", 
                          font=('Segoe UI', 12), 
                          fg='#7f8c8d', bg='white')
        message.pack()
        
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def load_statistics(self):
        """Cargar todas las estadísticas"""
        try:
            print("🔄 Cargando estadísticas...")
            
            # Cargar métricas principales
            self.load_main_metrics()
            
            # Cargar estadísticas detalladas
            self.load_detailed_stats()
            
            print("✅ Estadísticas cargadas correctamente")
            
        except Exception as e:
            print(f"❌ Error al cargar estadísticas: {e}")
            messagebox.showerror("Error", f"Error al cargar estadísticas: {e}")
            
    def load_main_metrics(self):
        """Cargar métricas principales"""
        try:
            conn = connect_db()
            if not conn:
                print("❌ No se pudo conectar a la base de datos")
                return
                
            cursor = conn.cursor()
            
            # Total de postulantes
            cursor.execute("SELECT COUNT(*) FROM postulantes")
            total_postulantes = cursor.fetchone()[0]
            
            # Total de usuarios
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            total_usuarios = cursor.fetchone()[0]
            
            # Postulantes de hoy
            hoy = datetime.now().date()
            cursor.execute("SELECT COUNT(*) FROM postulantes WHERE DATE(fecha_registro) = %s", (hoy,))
            postulantes_hoy = cursor.fetchone()[0]
            
            # Postulantes de esta semana
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            cursor.execute("SELECT COUNT(*) FROM postulantes WHERE DATE(fecha_registro) >= %s", (inicio_semana,))
            postulantes_semana = cursor.fetchone()[0]
            
            # Postulantes de este mes
            inicio_mes = hoy.replace(day=1)
            cursor.execute("SELECT COUNT(*) FROM postulantes WHERE DATE(fecha_registro) >= %s", (inicio_mes,))
            postulantes_mes = cursor.fetchone()[0]
            
            # Actualizar variables INMEDIATAMENTE
            self.total_postulantes_var.set(str(total_postulantes))
            self.total_usuarios_var.set(str(total_usuarios))
            self.postulantes_hoy_var.set(str(postulantes_hoy))
            self.postulantes_semana_var.set(str(postulantes_semana))
            self.postulantes_mes_var.set(str(postulantes_mes))
            
            # Forzar actualización visual
            self.update_idletasks()
            
            conn.close()
            print(f"✅ Métricas cargadas: {total_postulantes} postulantes, {total_usuarios} usuarios")
            
        except Exception as e:
            print(f"❌ Error al cargar métricas principales: {e}")
            
    def load_detailed_stats(self):
        """Cargar estadísticas detalladas"""
        try:
            conn = connect_db()
            if not conn:
                return
                
            cursor = conn.cursor()
            
            # Obtener todos los postulantes
            cursor.execute("""
                SELECT fecha_nacimiento, fecha_registro, edad, dedo_registrado, unidad 
                FROM postulantes 
                ORDER BY fecha_registro DESC
            """)
            postulantes = cursor.fetchall()
            
            if not postulantes:
                print("ℹ️ No hay postulantes en la base de datos")
                return
                
            # Calcular estadísticas de edad
            edades = []
            for p in postulantes:
                if p[2]:  # edad
                    edades.append(p[2])
                elif p[0]:  # fecha_nacimiento
                    try:
                        edad = datetime.now().year - p[0].year
                        if datetime.now().date() < p[0].replace(year=datetime.now().year):
                            edad -= 1
                        edades.append(edad)
                    except:
                        continue
                    
            if edades:
                promedio_edad = sum(edades) / len(edades)
                edad_minima = min(edades)
                edad_maxima = max(edades)
                
                self.stats_vars['promedio_edad'].set(f"{promedio_edad:.1f} años")
                self.stats_vars['edad_minima'].set(f"{edad_minima} años")
                self.stats_vars['edad_maxima'].set(f"{edad_maxima} años")
                
            # Fechas de registro
            fechas_registro = [p[1] for p in postulantes if p[1]]
            if fechas_registro:
                ultimo = max(fechas_registro)
                primer = min(fechas_registro)
                
                self.stats_vars['ultimo_registro'].set(ultimo.strftime('%d/%m/%Y %H:%M'))
                self.stats_vars['primer_registro'].set(primer.strftime('%d/%m/%Y %H:%M'))
                
            # Total de unidades únicas
            unidades = set(p[4] for p in postulantes if p[4])
            self.stats_vars['total_unidades'].set(str(len(unidades)))
            
            # Forzar actualización visual
            self.update_idletasks()
            
            conn.close()
            print(f"✅ Estadísticas detalladas cargadas: {len(postulantes)} registros procesados")
            
        except Exception as e:
            print(f"❌ Error al cargar estadísticas detalladas: {e}")

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
    
    app = Estadisticas(root, user_data)
    root.mainloop()

if __name__ == "__main__":
    main()
