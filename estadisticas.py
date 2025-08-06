#!/usr/bin/env python3
"""
Módulo de estadísticas del sistema
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import get_postulantes, get_usuarios
from datetime import datetime, timedelta
import ctypes
import os

# Configurar DPI awareness para Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

class Estadisticas(tk.Toplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.parent = parent
        self.user_data = user_data
        
        self.title("Estadísticas del Sistema")
        self.geometry("")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.center_window()
        self.load_statistics()
        
    def setup_ui(self):
        """Configurar la interfaz"""
        # Configurar estilo
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'), foreground='#2c3e50')
        style.configure('Metric.TLabel', font=('Arial', 12, 'bold'), foreground='#27ae60')
        style.configure('Info.TLabel', font=('Arial', 10), foreground='#34495e')
        
        # Frame principal
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill='both')
        
        # Título
        title_label = ttk.Label(main_frame, text="Estadísticas del Sistema", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Frame de métricas principales
        metrics_frame = ttk.LabelFrame(main_frame, text="Métricas Principales", padding=15)
        metrics_frame.pack(fill='x', pady=(0, 20))
        
        self.create_main_metrics(metrics_frame)
        
        # Frame de estadísticas detalladas
        details_frame = ttk.LabelFrame(main_frame, text="Estadísticas Detalladas", padding=15)
        details_frame.pack(fill='both', expand=True)
        
        self.create_detailed_stats(details_frame)
        
    def create_main_metrics(self, parent):
        """Crear métricas principales"""
        # Variables para métricas
        self.total_postulantes_var = tk.StringVar(value="0")
        self.total_usuarios_var = tk.StringVar(value="0")
        self.postulantes_hoy_var = tk.StringVar(value="0")
        self.postulantes_semana_var = tk.StringVar(value="0")
        
        # Grid de métricas
        metrics_grid = ttk.Frame(parent)
        metrics_grid.pack(fill='x')
        
        # Métrica 1: Total de postulantes
        metric1_frame = ttk.Frame(metrics_grid)
        metric1_frame.grid(row=0, column=0, padx=10, pady=5, sticky='ew')
        
        ttk.Label(metric1_frame, text="Total de Postulantes", style='Info.TLabel').pack()
        ttk.Label(metric1_frame, textvariable=self.total_postulantes_var, style='Metric.TLabel').pack()
        
        # Métrica 2: Total de usuarios
        metric2_frame = ttk.Frame(metrics_grid)
        metric2_frame.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        
        ttk.Label(metric2_frame, text="Total de Usuarios", style='Info.TLabel').pack()
        ttk.Label(metric2_frame, textvariable=self.total_usuarios_var, style='Metric.TLabel').pack()
        
        # Métrica 3: Postulantes hoy
        metric3_frame = ttk.Frame(metrics_grid)
        metric3_frame.grid(row=0, column=2, padx=10, pady=5, sticky='ew')
        
        ttk.Label(metric3_frame, text="Postulantes Hoy", style='Info.TLabel').pack()
        ttk.Label(metric3_frame, textvariable=self.postulantes_hoy_var, style='Metric.TLabel').pack()
        
        # Métrica 4: Postulantes esta semana
        metric4_frame = ttk.Frame(metrics_grid)
        metric4_frame.grid(row=0, column=3, padx=10, pady=5, sticky='ew')
        
        ttk.Label(metric4_frame, text="Postulantes Esta Semana", style='Info.TLabel').pack()
        ttk.Label(metric4_frame, textvariable=self.postulantes_semana_var, style='Metric.TLabel').pack()
        
        # Configurar grid
        metrics_grid.columnconfigure(0, weight=1)
        metrics_grid.columnconfigure(1, weight=1)
        metrics_grid.columnconfigure(2, weight=1)
        metrics_grid.columnconfigure(3, weight=1)
        
    def create_detailed_stats(self, parent):
        """Crear estadísticas detalladas"""
        # Notebook para pestañas
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True)
        
        # Pestaña 1: Resumen general
        summary_frame = ttk.Frame(notebook)
        notebook.add(summary_frame, text="Resumen General")
        self.create_summary_tab(summary_frame)
        
        # Pestaña 2: Registros por fecha
        timeline_frame = ttk.Frame(notebook)
        notebook.add(timeline_frame, text="Registros por Fecha")
        self.create_timeline_tab(timeline_frame)
        
        # Pestaña 3: Reporte por día
        report_frame = ttk.Frame(notebook)
        notebook.add(report_frame, text="Reporte por Día")
        self.create_daily_report_tab(report_frame)
        
    def create_summary_tab(self, parent):
        """Crear pestaña de resumen general"""
        # Frame con scrollbar
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Contenido del resumen
        self.create_summary_content(scrollable_frame)
        
        # Empaquetar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_summary_content(self, parent):
        """Crear contenido del resumen"""
        # Estadísticas generales
        general_frame = ttk.LabelFrame(parent, text="Estadísticas Generales", padding=15)
        general_frame.pack(fill='x', pady=(0, 20))
        
        # Variables para estadísticas
        self.stats_vars = {
            'promedio_edad': tk.StringVar(value="N/A"),
            'postulantes_mes': tk.StringVar(value="0"),
            'usuarios_activos': tk.StringVar(value="0"),
            'ultimo_registro': tk.StringVar(value="N/A")
        }
        
        # Crear estadísticas
        stats_grid = ttk.Frame(general_frame)
        stats_grid.pack(fill='x')
        
        row = 0
        for label, var in [
            ("Promedio de Edad:", self.stats_vars['promedio_edad']),
            ("Postulantes este Mes:", self.stats_vars['postulantes_mes']),
            ("Usuarios Activos:", self.stats_vars['usuarios_activos']),
            ("Último Registro:", self.stats_vars['ultimo_registro'])
        ]:
            ttk.Label(stats_grid, text=label, style='Info.TLabel').grid(row=row, column=0, sticky='w', pady=2)
            ttk.Label(stats_grid, textvariable=var, font=('Arial', 10, 'bold')).grid(row=row, column=1, sticky='w', padx=(10, 0), pady=2)
            row += 1
            
        # Distribución por edad
        age_frame = ttk.LabelFrame(parent, text="Distribución por Edad", padding=15)
        age_frame.pack(fill='x', pady=(0, 20))
        
        self.age_distribution_text = tk.Text(age_frame, height=6, width=60)
        self.age_distribution_text.pack(fill='x')
        
    def create_timeline_tab(self, parent):
        """Crear pestaña de registros por fecha"""
        # Frame de controles
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill='x', pady=(0, 20))
        
        # Período de tiempo
        ttk.Label(controls_frame, text="Período:", style='Info.TLabel').pack(side='left')
        
        self.period_var = tk.StringVar(value="7d")
        period_combo = ttk.Combobox(controls_frame, textvariable=self.period_var, 
                                   values=["7d", "30d", "90d", "1a"], width=10, state='readonly')
        period_combo.pack(side='left', padx=(10, 20))
        
        ttk.Button(controls_frame, text="Actualizar", command=self.update_timeline).pack(side='left')
        
        # Área de timeline
        timeline_frame = ttk.LabelFrame(parent, text="Registros por Fecha", padding=15)
        timeline_frame.pack(fill='both', expand=True)
        
        self.timeline_text = tk.Text(timeline_frame, wrap='word')
        scrollbar = ttk.Scrollbar(timeline_frame, orient='vertical', command=self.timeline_text.yview)
        self.timeline_text.configure(yscrollcommand=scrollbar.set)
        
        self.timeline_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def create_daily_report_tab(self, parent):
        """Crear pestaña de reporte por día"""
        # Frame de controles
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill='x', pady=(0, 20))
        
        # Entrada de fecha
        ttk.Label(controls_frame, text="Fecha (DD/MM/AAAA):", style='Info.TLabel').pack(side='left')
        
        self.fecha_var = tk.StringVar()
        fecha_entry = ttk.Entry(controls_frame, textvariable=self.fecha_var, width=15)
        fecha_entry.pack(side='left', padx=(10, 20))
        
        ttk.Button(controls_frame, text="Generar Reporte", command=self.generate_daily_report).pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Exportar Reporte", command=self.export_daily_report).pack(side='left')
        
        # Área de reporte
        report_frame = ttk.LabelFrame(parent, text="Reporte del Día", padding=15)
        report_frame.pack(fill='both', expand=True)
        
        self.daily_report_text = tk.Text(report_frame, wrap='word')
        report_scrollbar = ttk.Scrollbar(report_frame, orient='vertical', command=self.daily_report_text.yview)
        self.daily_report_text.configure(yscrollcommand=report_scrollbar.set)
        
        self.daily_report_text.pack(side='left', fill='both', expand=True)
        report_scrollbar.pack(side='right', fill='y')
        
    def center_window(self):
        """Centrar la ventana"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def load_statistics(self):
        """Cargar todas las estadísticas"""
        try:
            # Cargar métricas principales
            self.load_main_metrics()
            
            # Cargar estadísticas detalladas
            self.load_detailed_stats()
            
            # Cargar timeline
            self.update_timeline()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar estadísticas: {e}")
            
    def load_main_metrics(self):
        """Cargar métricas principales"""
        try:
            # Obtener datos
            postulantes = get_postulantes()
            usuarios = get_usuarios()
            
            # Calcular métricas
            total_postulantes = len(postulantes)
            total_usuarios = len(usuarios)
            
            # Postulantes de hoy
            hoy = datetime.now().date()
            postulantes_hoy = sum(1 for p in postulantes if p[6] and p[6].date() == hoy)  # fecha_registro
            
            # Postulantes de esta semana
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            postulantes_semana = sum(1 for p in postulantes if p[6] and p[6].date() >= inicio_semana)  # fecha_registro
            
            # Actualizar variables
            self.total_postulantes_var.set(str(total_postulantes))
            self.total_usuarios_var.set(str(total_usuarios))
            self.postulantes_hoy_var.set(str(postulantes_hoy))
            self.postulantes_semana_var.set(str(postulantes_semana))
            
        except Exception as e:
            print(f"Error al cargar métricas principales: {e}")
            
    def load_detailed_stats(self):
        """Cargar estadísticas detalladas"""
        try:
            postulantes = get_postulantes()
            
            if not postulantes:
                return
                
            # Calcular promedio de edad
            edades = []
            for p in postulantes:
                if p[4]:  # fecha_nacimiento
                    try:
                        edad = datetime.now().year - p[4].year
                        if datetime.now().date() < p[4].replace(year=datetime.now().year):
                            edad -= 1
                        edades.append(edad)
                    except:
                        continue
                    
            if edades:
                promedio_edad = sum(edades) / len(edades)
                self.stats_vars['promedio_edad'].set(f"{promedio_edad:.1f} años")
                
            # Postulantes este mes
            inicio_mes = datetime.now().replace(day=1).date()
            postulantes_mes = sum(1 for p in postulantes if p[6] and p[6].date() >= inicio_mes)  # fecha_registro
            self.stats_vars['postulantes_mes'].set(str(postulantes_mes))
            
            # Usuarios activos
            usuarios = get_usuarios()
            self.stats_vars['usuarios_activos'].set(str(len(usuarios)))
            
            # Último registro
            if postulantes:
                fechas_registro = [p[6] for p in postulantes if p[6]]  # fecha_registro
                if fechas_registro:
                    try:
                        ultimo = max(fechas_registro)
                        self.stats_vars['ultimo_registro'].set(ultimo.strftime('%d/%m/%Y %H:%M'))
                    except:
                        self.stats_vars['ultimo_registro'].set("N/A")
                    
            # Distribución por edad
            self.update_age_distribution(postulantes)
            
        except Exception as e:
            print(f"Error al cargar estadísticas detalladas: {e}")
            
    def update_age_distribution(self, postulantes):
        """Actualizar distribución por edad"""
        try:
            # Calcular distribución
            distribucion = {}
            for p in postulantes:
                if p[4]:  # fecha_nacimiento
                    try:
                        edad = datetime.now().year - p[4].year
                        if datetime.now().date() < p[4].replace(year=datetime.now().year):
                            edad -= 1
                        
                        rango = f"{(edad // 10) * 10}-{((edad // 10) * 10) + 9}"
                        distribucion[rango] = distribucion.get(rango, 0) + 1
                    except:
                        continue
                    
            # Mostrar distribución
            self.age_distribution_text.delete('1.0', tk.END)
            if distribucion:
                for rango, cantidad in sorted(distribucion.items()):
                    self.age_distribution_text.insert(tk.END, f"{rango} años: {cantidad} postulantes\n")
            else:
                self.age_distribution_text.insert(tk.END, "No hay datos de edad disponibles")
                
        except Exception as e:
            print(f"Error al actualizar distribución por edad: {e}")
            
    def update_timeline(self):
        """Actualizar timeline de registros"""
        try:
            postulantes = get_postulantes()
            period = self.period_var.get()
            
            # Calcular fecha de inicio según período
            if period == "7d":
                start_date = datetime.now().date() - timedelta(days=7)
            elif period == "30d":
                start_date = datetime.now().date() - timedelta(days=30)
            elif period == "90d":
                start_date = datetime.now().date() - timedelta(days=90)
            else:  # 1a
                start_date = datetime.now().date() - timedelta(days=365)
                
            # Filtrar postulantes por fecha
            filtered_postulantes = [p for p in postulantes if p[6] and p[6].date() >= start_date]  # fecha_registro
            
            # Agrupar por fecha
            registros_por_fecha = {}
            for p in filtered_postulantes:
                fecha = p[6].date()  # fecha_registro
                registros_por_fecha[fecha] = registros_por_fecha.get(fecha, 0) + 1
                
            # Mostrar timeline
            self.timeline_text.delete('1.0', tk.END)
            if registros_por_fecha:
                for fecha in sorted(registros_por_fecha.keys()):
                    cantidad = registros_por_fecha[fecha]
                    self.timeline_text.insert(tk.END, f"{fecha.strftime('%d/%m/%Y')}: {cantidad} postulantes\n")
            else:
                self.timeline_text.insert(tk.END, "No hay registros en el período seleccionado")
                
        except Exception as e:
            print(f"Error al actualizar timeline: {e}")
            
    def generate_daily_report(self):
        """Generar reporte por día"""
        try:
            fecha_texto = self.fecha_var.get().strip()
            
            if not fecha_texto:
                messagebox.showerror("Error", "Por favor ingrese una fecha en formato DD/MM/AAAA")
                return
                
            # Validar formato de fecha
            try:
                fecha = datetime.strptime(fecha_texto, "%d/%m/%Y").date()
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha incorrecto. Use DD/MM/AAAA")
                return
                
            # Obtener postulantes del día
            postulantes = get_postulantes()
            postulantes_del_dia = []
            
            for p in postulantes:
                if p[6] and p[6].date() == fecha:  # fecha_registro
                    postulantes_del_dia.append(p)
                    
            # Generar reporte completo para exportación
            report_completo = f"""
REPORTE DEL DÍA: {fecha.strftime('%d/%m/%Y')}
Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

RESUMEN:
- Total de postulantes registrados: {len(postulantes_del_dia)}
- Fecha consultada: {fecha.strftime('%d/%m/%Y')}

DETALLE DE POSTULANTES:
"""
            
            # Generar reporte resumido para pantalla
            report_resumen = f"""
REPORTE DEL DÍA: {fecha.strftime('%d/%m/%Y')}
Total de postulantes: {len(postulantes_del_dia)}

LISTA DE POSTULANTES:
"""
            
            if postulantes_del_dia:
                for i, p in enumerate(postulantes_del_dia, 1):
                    # Calcular edad
                    edad = "N/A"
                    if p[4]:  # fecha_nacimiento
                        try:
                            edad_calc = datetime.now().year - p[4].year
                            if datetime.now().date() < p[4].replace(year=datetime.now().year):
                                edad_calc -= 1
                            edad = str(edad_calc)
                        except:
                            pass
                    
                    # Agregar al reporte completo
                    report_completo += f"""
{i}. {p[1]} {p[2]}
   Cédula: {p[3]}
   Teléfono: {p[5] or 'N/A'}
   Edad: {edad}
   Unidad: {p[12] or 'N/A'}
   Dedo Registrado: {p[13] or 'N/A'}
   Registrado por: {p[14] or 'N/A'}
   Hora de registro: {p[6].strftime('%H:%M:%S') if p[6] else 'N/A'}
   Aparato ID: {p[15] or 'N/A'}
"""
                    
                    # Agregar al reporte resumido
                    report_resumen += f"{i}. {p[1]} {p[2]} - Cédula: {p[3]} - Edad: {edad} - Hora: {p[6].strftime('%H:%M') if p[6] else 'N/A'}\n"
            else:
                report_completo += "\nNo se encontraron postulantes registrados en esta fecha."
                report_resumen += "\nNo se encontraron postulantes registrados en esta fecha."
                
            # Guardar reporte completo para exportación
            self.last_generated_report = report_completo
                
            # Mostrar reporte resumido en pantalla
            self.daily_report_text.delete('1.0', tk.END)
            self.daily_report_text.insert('1.0', report_resumen)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {e}")
            
    def export_daily_report(self):
        """Exportar reporte por día a archivo"""
        try:
            # Verificar si hay un reporte generado
            if not hasattr(self, 'last_generated_report') or not self.last_generated_report:
                messagebox.showwarning("Advertencia", "Primero debe generar un reporte antes de exportarlo.")
                return
                
            # Solicitar ubicación del archivo
            fecha_actual = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_filename = f"reporte_diario_{fecha_actual}.txt"
            
            file_path = filedialog.asksaveasfilename(
                title="Guardar Reporte",
                defaultextension=".txt",
                filetypes=[
                    ("Archivos de texto", "*.txt"),
                    ("Todos los archivos", "*.*")
                ],
                initialfile=default_filename
            )
            
            if not file_path:
                return  # Usuario canceló
                
            # Escribir reporte al archivo
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.last_generated_report)
                
            messagebox.showinfo(
                "Éxito", 
                f"Reporte exportado exitosamente a:\n{file_path}"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar reporte: {e}")

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