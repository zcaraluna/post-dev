#!/usr/bin/env python3
"""
Módulo para agregar postulantes al sistema con funcionalidad completa
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from database import connect_db, agregar_postulante, USUARIO_ACTUAL
from zkteco_connector_v2 import ZKTecoK40V2
import psycopg2
import bcrypt
import ctypes

# Configurar DPI para Windows (HD/4K)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Per Monitor DPI Aware
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()  # Fallback para versiones anteriores
    except:
        pass

def obtener_serial_desde_hardware(ip="192.168.100.201", puerto=4370, intentos=3):
    """
    Conecta al dispositivo biométrico vía TCP/IP y obtiene el número de serie.
    Si fallan todos los intentos, retorna None para indicar que no hay conexión.
    """
    try:
        zkteco = ZKTecoK40V2(ip, puerto)
        
        for intento in range(intentos):
            try:
                print(f"🔍 Intentando conectar con {ip}:{puerto} (Intento {intento + 1}/{intentos})")
                if zkteco.connect():
                    # Obtener el número de serie del aparato conectado
                    serial = zkteco.get_device_info().get('serial_number', 'No disponible')
                    zkteco.disconnect()
                    
                    if serial:
                        print(f"✅ Número de serie detectado: {serial}")
                        return serial
                    else:
                        print("⚠️ No se obtuvo el número de serie.")
                        
            except Exception as e:
                print(f"⛔ Error en la conexión: {e}")
                
    except Exception as e:
        print(f"⛔ Error al crear conexión ZKTeco: {e}")
    
    # Si llegamos aquí, todos los intentos fallaron
    print("⚠️ Todos los intentos de conexión fallaron. No se puede conectar al dispositivo.")
    return None  # No hay conexión disponible

def obtener_aparato_por_serial(serial_number):
    """Consulta la base de datos para obtener un aparato biométrico basado en su número de serie."""
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Buscar el aparato biométrico en la base de datos por su número de serie
        cursor.execute("""
            SELECT id, nombre FROM aparatos_biometricos
            WHERE serial = %s
            LIMIT 1;
        """, (serial_number,))

        aparato = cursor.fetchone()
        cursor.close()
        conn.close()

        if aparato:
            return aparato[0], aparato[1]  # Retorna ID y Nombre
        else:
            return None, "No disponible"
            
    except Exception as e:
        print(f"⛔ Error al obtener aparato biométrico desde la BD: {e}")
        return None, "No disponible"

class AgregarPostulante(tk.Toplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.title("Añadir Postulante - Sistema QUIRA")
        self.geometry("")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Configurar estilo moderno
        self.configure(bg='#f0f0f0')
        
        self.user_data = user_data
        self.usuario_registrador = self.user_data["id"]
        
        # Conexión ZKTeco que se mantendrá abierta
        self.zkteco = None
        self.zkteco_connected = False
        
        # Crear el string del registrador con grado+nombre+apellido
        grado = self.user_data.get("grado", "")
        nombre = self.user_data.get("nombre", "")
        apellido = self.user_data.get("apellido", "")
        self.registrador_string = f"{grado} {nombre} {apellido}".strip()
        
        # Log para debug
        print(f"🔍 Debug - Registrador string: '{self.registrador_string}'")
        print(f"🔍 Debug - User data: {self.user_data}")

        # Frame principal con padding y estilo
        frame_main = tk.Frame(self, bg='#f0f0f0', padx=30, pady=20)
        frame_main.pack(expand=True, fill='both')

        # Título principal
        title_frame = tk.Frame(frame_main, bg='#f0f0f0')
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(title_frame, text="AÑADIR NUEVO POSTULANTE", 
                               font=('Segoe UI', 16, 'bold'), 
                               fg='#2c3e50', bg='#f0f0f0')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Sistema de Registro Biométrico", 
                                 font=('Segoe UI', 10), 
                                 fg='#7f8c8d', bg='#f0f0f0')
        subtitle_label.pack()

        # Indicador de estado (movido aquí para mayor visibilidad)
        self.status_frame = tk.Frame(title_frame, bg='#f0f0f0')
        self.status_frame.pack(fill='x', pady=(10, 0))
        
        # Label de estado
        self.status_label = tk.Label(self.status_frame, text="", 
                                    font=('Segoe UI', 9), 
                                    fg='#7f8c8d', bg='#f0f0f0')
        self.status_label.pack()
        
        # Barra de progreso sutil
        self.progress_frame = tk.Frame(self.status_frame, bg='#f0f0f0', height=2)
        self.progress_frame.pack(fill='x', pady=(2, 0))
        self.progress_frame.pack_propagate(False)
        
        self.progress_bar = tk.Frame(self.progress_frame, bg='#3498db', width=0)
        self.progress_bar.pack(side='left', fill='y')
        
        # Mostrar inicialmente con un mensaje de carga
        self.status_label.config(text="Inicializando sistema...")
        self.status_frame.pack(fill='x', pady=(10, 0))
        self.animar_progreso()

        # Frame para el formulario
        form_frame = tk.Frame(frame_main, bg='white', relief='solid', bd=2)
        form_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Configurar grid del formulario
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        # Variables para los campos
        self.entry_id_k40 = tk.StringVar()
        self.entry_nombre = tk.StringVar()
        self.entry_apellido = tk.StringVar()
        self.entry_cedula = tk.StringVar()
        self.entry_telefono = tk.StringVar()
        self.entry_fecha_nacimiento = tk.StringVar()
        self.entry_edad = tk.StringVar()
        self.entry_sexo = tk.StringVar(value="Seleccionar")
        self.entry_fecha_registro = tk.StringVar()
        self.entry_aparato = tk.StringVar()
        self.entry_unidad = tk.StringVar()
        self.entry_dedo = tk.StringVar()
        
        # Valores para comboboxes
        self.unidades = ["Unidad 1", "Unidad 2", "Unidad 3", "Unidad 4"]
        self.dedos = ["PD", "ID", "MD", "AD", "MeD", "PI", "II", "MI", "AI", "MeI"]
        self.sexos = ["Hombre", "Mujer"]

        # Sección 1: Información Personal
        self.crear_seccion_titulo(form_frame, "INFORMACIÓN PERSONAL", 0)
        
        # ID en K40 (Opcional)
        self.crear_campo(form_frame, "ID en K40 (Opcional):", self.entry_id_k40, 1, readonly=False)
        
        # Nombre y Apellido en la misma fila
        self.crear_campo_horizontal(form_frame, "Nombre:", self.entry_nombre, 2, "Apellido:", self.entry_apellido)
        
        # Cédula y Teléfono en la misma fila
        self.crear_campo_horizontal(form_frame, "Cédula:", self.entry_cedula, 3, "Teléfono:", self.entry_telefono)
        
        # Fecha de Nacimiento y Edad en la misma fila (con campo inteligente)
        self.crear_campo_fecha_inteligente(form_frame, "Fecha Nacimiento:", self.entry_fecha_nacimiento, 4, "Edad:", self.entry_edad, readonly2=True)
        
        # Sexo (campo individual)
        self.crear_campo_combobox(form_frame, "Sexo:", self.entry_sexo, 5, self.sexos)
        
        # Sección 2: Información del Registro
        self.crear_seccion_titulo(form_frame, "INFORMACIÓN DEL REGISTRO", 6)
        
        # Unidad y Dedo Registrado en la misma fila
        self.crear_campo_horizontal_combobox(form_frame, "Unidad:", self.entry_unidad, 7, "Dedo Registrado:", self.entry_dedo, self.unidades, self.dedos)
        
        # Fecha de Registro y Aparato Biométrico en la misma fila
        self.crear_campo_horizontal(form_frame, "Fecha Registro:", self.entry_fecha_registro, 8, "Aparato Biométrico:", self.entry_aparato, readonly1=True, readonly2=True)

        # Frame para botones centrados
        button_frame = tk.Frame(frame_main, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=20)

        # Frame interno para centrar los botones
        button_center_frame = tk.Frame(button_frame, bg='#f0f0f0')
        button_center_frame.pack(expand=True)

        # Botón Guardar con estilo moderno
        save_button = tk.Button(button_center_frame, text="GUARDAR POSTULANTE", 
                               command=self.guardar_postulante,
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', bg='#2E902E',
                               activebackground='#2E902E',
                               relief='flat', bd=0,
                               padx=30, pady=12,
                               cursor='hand2')

        # Botón Cancelar
        cancel_button = tk.Button(button_center_frame, text="CANCELAR", 
                                  command=self.on_closing,
                                  font=('Segoe UI', 12),
                                  fg='white', bg='#902E2E',
                                  activebackground='#902E2E',
                                  relief='flat', bd=0,
                                  padx=30, pady=12,
                                  cursor='hand2')
        
        # Centrar los botones
        save_button.pack(side='left', padx=(0, 10))
        cancel_button.pack(side='left')

        # Configurar eventos
        self.entry_fecha_nacimiento.trace('w', self.calcular_edad)
        self.entry_nombre.trace('w', self.convertir_a_mayusculas)
        self.entry_apellido.trace('w', self.convertir_a_mayusculas)
        
        # Inicializar datos después de crear la ventana
        self.after(100, self.inicializar_datos)
        
        # Configurar evento para cerrar conexión al cerrar la ventana
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def crear_seccion_titulo(self, parent, texto, row):
        """Crear título de sección"""
        title_label = tk.Label(parent, text=texto, 
                              font=('Segoe UI', 12, 'bold'), 
                              fg='#2c3e50', bg='white')
        title_label.grid(row=row, column=0, columnspan=4, sticky='w', pady=(20, 15), padx=10)

    def crear_campo(self, parent, label_text, variable, row, readonly=False):
        """Crear campo de entrada individual"""
        # Label
        label = tk.Label(parent, text=label_text, 
                        font=('Segoe UI', 10, 'bold'), 
                        fg='#2c3e50', bg='white', anchor='w')
        label.grid(row=row, column=0, sticky='w', pady=8, padx=10)
        
        # Entry con bordes más visibles
        if readonly:
            entry = tk.Entry(parent, textvariable=variable, 
                           font=('Segoe UI', 10),
                           state='readonly', readonlybackground='#f8f9fa',
                           relief='solid', bd=2, 
                           highlightthickness=1, highlightcolor='#3498db')
        else:
            entry = tk.Entry(parent, textvariable=variable, 
                           font=('Segoe UI', 10),
                           relief='solid', bd=2,
                           highlightthickness=1, highlightcolor='#3498db',
                           bg='white')
        entry.grid(row=row, column=1, sticky='ew', pady=8, padx=(0, 10))

    def crear_campo_horizontal(self, parent, label1, var1, row, label2, var2, readonly1=False, readonly2=False):
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
                            relief='solid', bd=2,
                            highlightthickness=1, highlightcolor='#3498db')
        else:
            entry1 = tk.Entry(parent, textvariable=var1, 
                            font=('Segoe UI', 10),
                            relief='solid', bd=2,
                            highlightthickness=1, highlightcolor='#3498db',
                            bg='white')
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
                            relief='solid', bd=2,
                            highlightthickness=1, highlightcolor='#3498db')
        else:
            entry2 = tk.Entry(parent, textvariable=var2, 
                            font=('Segoe UI', 10),
                            relief='solid', bd=2,
                            highlightthickness=1, highlightcolor='#3498db',
                            bg='white')
        entry2.grid(row=row, column=3, sticky='ew', pady=8, padx=(0, 10))

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
        
        combo2 = ttk.Combobox(parent, textvariable=var2, values=valores2, 
                             state="readonly", font=('Segoe UI', 10))
        combo2.grid(row=row, column=3, sticky='ew', pady=8, padx=(0, 10))

    def crear_campo_combobox(self, parent, label_text, variable, row, valores):
        """Crear campo individual con combobox"""
        # Label
        label = tk.Label(parent, text=label_text, 
                        font=('Segoe UI', 10, 'bold'), 
                        fg='#2c3e50', bg='white', anchor='w')
        label.grid(row=row, column=0, sticky='w', pady=8, padx=10)
        
        # Combobox
        combo = ttk.Combobox(parent, textvariable=variable, values=valores, 
                            state="readonly", font=('Segoe UI', 10))
        combo.grid(row=row, column=1, sticky='ew', pady=8, padx=(0, 10))

    def crear_campo_fecha_inteligente(self, parent, label1, var1, row, label2, var2, readonly1=False, readonly2=False):
        """Crear campo de fecha inteligente con formato automático y validación"""
        # Primer campo (Fecha de Nacimiento)
        label1_widget = tk.Label(parent, text=label1, 
                                font=('Segoe UI', 10, 'bold'), 
                                fg='#2c3e50', bg='white', anchor='w')
        label1_widget.grid(row=row, column=0, sticky='w', pady=8, padx=10)
        
        # Frame para el campo de fecha y botón de calendario
        fecha_frame = tk.Frame(parent, bg='white')
        fecha_frame.grid(row=row, column=1, sticky='ew', pady=8, padx=(0, 5))
        
        # Entry para fecha con formato automático
        if readonly1:
            entry1 = tk.Entry(fecha_frame, textvariable=var1, 
                            font=('Segoe UI', 10),
                            state='readonly', readonlybackground='#f8f9fa',
                            relief='solid', bd=2,
                            highlightthickness=1, highlightcolor='#3498db')
        else:
            entry1 = tk.Entry(fecha_frame, textvariable=var1, 
                            font=('Segoe UI', 10),
                            relief='solid', bd=2,
                            highlightthickness=1, highlightcolor='#3498db',
                            bg='white')
            # Agregar placeholder
            entry1.insert(0, "DD/MM/AAAA")
            entry1.config(fg='gray')
            
            def on_focus_in(event):
                if entry1.get() == "DD/MM/AAAA":
                    entry1.delete(0, tk.END)
                    entry1.config(fg='black')
            
            def on_focus_out(event):
                if not entry1.get():
                    entry1.insert(0, "DD/MM/AAAA")
                    entry1.config(fg='gray')
                else:
                    # Calcular edad solo cuando se complete la fecha
                    self.calcular_edad()
            
            def on_key_release(event):
                # Obtener el texto actual
                texto = entry1.get()
                if texto == "DD/MM/AAAA":
                    return
                
                # Remover caracteres no numéricos para el procesamiento
                numeros = ''.join(filter(str.isdigit, texto))
                
                # Aplicar solo separadores automáticos
                if len(numeros) >= 2:
                    # Si tenemos exactamente 2 dígitos, agregar primer separador
                    if len(numeros) == 2 and not texto.endswith('/'):
                        nuevo_texto = numeros[:2] + '/'
                        entry1.delete(0, tk.END)
                        entry1.insert(0, nuevo_texto)
                        entry1.icursor(tk.END)
                    elif len(numeros) >= 4:
                        # Si tenemos exactamente 4 dígitos, agregar segundo separador
                        if len(numeros) == 4 and texto.count('/') == 1:
                            nuevo_texto = numeros[:2] + '/' + numeros[2:4] + '/'
                            entry1.delete(0, tk.END)
                            entry1.insert(0, nuevo_texto)
                            entry1.icursor(tk.END)
            
            entry1.bind('<FocusIn>', on_focus_in)
            entry1.bind('<FocusOut>', on_focus_out)
            entry1.bind('<KeyRelease>', on_key_release)
        
        entry1.pack(side='left', fill='x', expand=True)
        
        # Botón de calendario
        if not readonly1:
            calendar_button = tk.Button(fecha_frame, text="📅", 
                                      command=lambda: self.abrir_calendario(var1),
                                      font=('Segoe UI', 10),
                                      bg='#3498db', fg='white',
                                      relief='flat', bd=0,
                                      padx=8, pady=2,
                                      cursor='hand2')
            calendar_button.pack(side='right', padx=(5, 0))
        
        # Segundo campo (Edad)
        label2_widget = tk.Label(parent, text=label2, 
                                font=('Segoe UI', 10, 'bold'), 
                                fg='#2c3e50', bg='white', anchor='w')
        label2_widget.grid(row=row, column=2, sticky='w', pady=8, padx=10)
        
        if readonly2:
            entry2 = tk.Entry(parent, textvariable=var2, 
                            font=('Segoe UI', 10),
                            state='readonly', readonlybackground='#f8f9fa',
                            relief='solid', bd=2,
                            highlightthickness=1, highlightcolor='#3498db')
        else:
            entry2 = tk.Entry(parent, textvariable=var2, 
                            font=('Segoe UI', 10),
                            relief='solid', bd=2,
                            highlightthickness=1, highlightcolor='#3498db',
                            bg='white')
        entry2.grid(row=row, column=3, sticky='ew', pady=8, padx=(0, 10))

    def abrir_calendario(self, variable_fecha):
        """Abrir ventana de calendario para seleccionar fecha"""
        def seleccionar_fecha():
            fecha_seleccionada = f"{dia_var.get():02d}/{mes_var.get():02d}/{anio_var.get()}"
            variable_fecha.set(fecha_seleccionada)
            ventana_calendario.destroy()
            # Calcular edad automáticamente
            self.calcular_edad()
        
        # Crear ventana de calendario
        ventana_calendario = tk.Toplevel(self)
        ventana_calendario.title("Seleccionar Fecha de Nacimiento")
        ventana_calendario.geometry("")
        ventana_calendario.resizable(False, False)
        ventana_calendario.transient(self)
        ventana_calendario.grab_set()
        ventana_calendario.configure(bg='#f0f0f0')
        
        # Variables para fecha
        dia_var = tk.IntVar(value=1)
        mes_var = tk.IntVar(value=1)
        anio_var = tk.IntVar(value=1990)
        
        # Frame principal
        main_frame = tk.Frame(ventana_calendario, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        # Título
        titulo = tk.Label(main_frame, text="Selecciona la fecha de nacimiento", 
                         font=('Segoe UI', 12, 'bold'), 
                         fg='#2c3e50', bg='#f0f0f0')
        titulo.pack(pady=(0, 20))
        
        # Frame para controles
        controles_frame = tk.Frame(main_frame, bg='#f0f0f0')
        controles_frame.pack(fill='x', pady=10)
        
        # Día
        tk.Label(controles_frame, text="Día:", font=('Segoe UI', 10, 'bold'), 
                fg='#2c3e50', bg='#f0f0f0').pack(anchor='w')
        dia_spinbox = tk.Spinbox(controles_frame, from_=1, to=31, textvariable=dia_var,
                                font=('Segoe UI', 10), width=10)
        dia_spinbox.pack(fill='x', pady=(5, 10))
        
        # Mes
        tk.Label(controles_frame, text="Mes:", font=('Segoe UI', 10, 'bold'), 
                fg='#2c3e50', bg='#f0f0f0').pack(anchor='w')
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        mes_combobox = ttk.Combobox(controles_frame, values=meses,
                                   state="readonly", font=('Segoe UI', 10))
        mes_combobox.pack(fill='x', pady=(5, 10))
        mes_combobox.set("Enero")
        
        def on_mes_change(event):
            mes_seleccionado = mes_combobox.get()
            mes_numero = meses.index(mes_seleccionado) + 1
            mes_var.set(mes_numero)
        
        mes_combobox.bind('<<ComboboxSelected>>', on_mes_change)
        
        # Año
        tk.Label(controles_frame, text="Año:", font=('Segoe UI', 10, 'bold'), 
                fg='#2c3e50', bg='#f0f0f0').pack(anchor='w')
        anio_spinbox = tk.Spinbox(controles_frame, from_=1900, to=datetime.now().year, 
                                 textvariable=anio_var, font=('Segoe UI', 10), width=10)
        anio_spinbox.pack(fill='x', pady=(5, 20))
        
        # Botones
        botones_frame = tk.Frame(main_frame, bg='#f0f0f0')
        botones_frame.pack(fill='x', pady=10)
        
        tk.Button(botones_frame, text="Seleccionar", command=seleccionar_fecha,
                 font=('Segoe UI', 10, 'bold'), fg='white', bg='#27ae60',
                 relief='flat', bd=0, padx=20, pady=8, cursor='hand2').pack(side='left', padx=(0, 10))
        
        tk.Button(botones_frame, text="Cancelar", command=ventana_calendario.destroy,
                 font=('Segoe UI', 10), fg='white', bg='#e74c3c',
                 relief='flat', bd=0, padx=20, pady=8, cursor='hand2').pack(side='left')

        # Inicializar datos después de crear la ventana
        self.after(100, self.inicializar_datos)

    def inicializar_datos(self):
        """Inicializa los datos de fecha y aparato biométrico después de crear la ventana"""
        # Usar after para permitir que la interfaz se actualice
        self.after(100, self.paso_1_inicializacion)
    
    def paso_1_inicializacion(self):
        """Paso 1: Obtener fecha y hora"""
        self.mostrar_estado("Obteniendo fecha y hora del sistema...")
        self.obtener_fecha_hora_servidor()
        self.after(150, self.paso_2_conexion)
    
    def paso_2_conexion(self):
        """Paso 2: Establecer conexión ZKTeco"""
        self.mostrar_estado("Conectando al dispositivo biométrico...")
        self.establecer_conexion_zkteco()
        self.after(150, self.paso_3_deteccion)
    
    def paso_3_deteccion(self):
        """Paso 3: Detectar dispositivo"""
        self.mostrar_estado("Detectando dispositivo biométrico...")
        self.asignar_aparato_biometrico()
        self.after(150, self.paso_4_usuarios)
    
    def paso_4_usuarios(self):
        """Paso 4: Obtener información de usuarios"""
        self.mostrar_estado("Obteniendo último UID del dispositivo...")
        self.obtener_id_mas_alto_k40()
        self.after(150, self.finalizar_inicializacion)
    
    def finalizar_inicializacion(self):
        """Finalizar la inicialización"""
        # Completar la barra de progreso primero
        self.completar_progreso()
        # Esperar un momento para que se vea la barra completa
        self.after(200, self.mostrar_estado_final)
    
    def mostrar_estado_final(self):
        """Muestra el estado final del sistema basado en las conexiones establecidas"""
        # Verificar el estado de las conexiones
        if self.zkteco_connected and self.zkteco:
            # Sistema completamente funcional
            self.status_label.config(text="✅ Sistema listo - QUIRA conectado", fg='#2E902E', font=('Segoe UI', 10, 'bold'))
            self.progress_bar.config(width=0)
        elif self.verificar_modo_prueba_activo():
            # Modo prueba activo en la base de datos
            self.status_label.config(text="🔧 Modo prueba activado", fg='#f39c12', font=('Segoe UI', 10, 'bold'))
            self.progress_bar.config(width=0)
            
            # Completar inicialización en modo prueba
            self.obtener_fecha_hora_servidor()
            self.obtener_id_mas_alto_k40()
        else:
            # Sistema con problemas de conexión - mostrar aviso
            self.mostrar_aviso_conexion()
    
    def mostrar_aviso_conexion(self):
        """Muestra aviso de conexión fallida con opciones para el operador"""
        # Ocultar barra de progreso
        self.progress_bar.config(width=0)
        
        # Mostrar messagebox con opciones
        mensaje = """⚠️ No se pudo conectar al dispositivo biométrico

Por favor verifique:
• El dispositivo biométrico esté encendido
• El cable de red esté conectado correctamente
• La IP del dispositivo sea 192.168.100.201
• No haya problemas de red

¿Desea reintentar la conexión?"""
        
        respuesta = messagebox.askyesno(
            "Error de Conexión - Dispositivo Biométrico",
            mensaje,
            icon='warning'
        )
        
        if respuesta:
            # Usuario eligió reintentar
            self.reintentar_conexion()
        else:
            # Usuario canceló - mostrar estado de error
            self.status_label.config(text="❌ Conexión cancelada por el usuario", fg='#e74c3c', font=('Segoe UI', 10, 'bold'))
            self.progress_bar.config(width=0)
    
    def reintentar_conexion(self):
        """Reintenta la conexión al dispositivo biométrico"""
        # Mostrar estado de reconexión
        self.mostrar_estado("🔄 Reintentando conexión al dispositivo...")
        self.animar_progreso()
        
        # Ejecutar reconexión después de un breve delay
        self.after(500, self.ejecutar_reconexion)
    
    def ejecutar_reconexion(self):
        """Ejecuta el proceso de reconexión"""
        try:
            # Cerrar conexión anterior si existe
            if self.zkteco:
                try:
                    self.zkteco.disconnect()
                except:
                    pass
            
            # Intentar nueva conexión
            self.establecer_conexion_zkteco()
            
            if self.zkteco_connected and self.zkteco:
                # Conexión exitosa
                self.mostrar_estado("✅ Conexión restablecida exitosamente")
                self.completar_progreso()
                self.after(1000, self.finalizar_reconexion_exitosa)
            else:
                # Conexión fallida
                self.after(500, self.finalizar_reconexion_fallida)
                
        except Exception as e:
            print(f"Error en reconexión: {e}")
            self.after(500, self.finalizar_reconexion_fallida)
    
    def finalizar_reconexion_exitosa(self):
        """Finaliza el proceso de reconexión exitosa"""
        # Continuar con la inicialización normal
        self.paso_3_deteccion()
    
    def finalizar_reconexion_fallida(self):
        """Finaliza el proceso de reconexión fallida"""
        self.ocultar_estado()
        # Mostrar messagebox de error
        messagebox.showerror(
            "Error de Conexión",
            "No se pudo restablecer la conexión al dispositivo biométrico.\n\n"
            "Por favor verifique la conectividad y vuelva a intentar."
        )
        # Mostrar estado de error
        self.status_label.config(text="❌ Conexión fallida", fg='#e74c3c', font=('Segoe UI', 10, 'bold'))
        self.progress_bar.config(width=0)
    


    def asignar_aparato_biometrico(self):
        """Detecta automáticamente el aparato biométrico en uso y lo asigna en la interfaz."""
        # Usar la conexión existente para obtener el serial
        numero_de_serie = None
        
        if self.zkteco_connected and self.zkteco:
            try:
                device_info = self.zkteco.get_device_info()
                numero_de_serie = device_info.get('serial_number', None)
                print(f"✅ Número de serie obtenido desde conexión existente: {numero_de_serie}")
            except Exception as e:
                print(f"⚠️ Error al obtener serial desde conexión existente: {e}")
                # Fallback a la función original
                numero_de_serie = obtener_serial_desde_hardware()
        else:
            # Fallback a la función original si no hay conexión
            numero_de_serie = obtener_serial_desde_hardware()

        # Primero verificar si el modo prueba está activo
        modo_prueba_activo = self.verificar_modo_prueba_activo()
        
        if modo_prueba_activo:
            # Modo prueba activo - asignar dispositivo de prueba
            aparato_id, aparato_nombre = obtener_aparato_por_serial("0X0AB0")
            self.aparato_id = aparato_id
            
            if aparato_nombre and aparato_nombre != "No disponible":
                texto_aparato = f"{aparato_nombre} (0X0AB0) - MODO PRUEBA"
            else:
                texto_aparato = "APARATO DE PRUEBA (0X0AB0) - MODO PRUEBA"
        elif numero_de_serie:
            # Conexión normal al dispositivo físico
            aparato_id, aparato_nombre = obtener_aparato_por_serial(numero_de_serie)
            self.aparato_id = aparato_id  # Guardamos el ID del aparato detectado
            
            # Mostrar el nombre del dispositivo y el serial entre paréntesis
            if aparato_nombre and aparato_nombre != "No disponible":
                texto_aparato = f"{aparato_nombre} ({numero_de_serie})"
            else:
                texto_aparato = f"Dispositivo {numero_de_serie}"
        else:
            # No hay conexión al dispositivo y modo prueba no está activo
            texto_aparato = "No disponible - Sin conexión"
            self.aparato_id = None

        # Mostrar el nombre del aparato en la interfaz
        self.entry_aparato.set(texto_aparato)
    
    def refrescar_asignacion_aparato(self):
        """Refrescar la asignación del aparato biométrico (útil cuando cambia el modo prueba)"""
        self.asignar_aparato_biometrico()
    
    def verificar_modo_prueba_activo(self):
        """Verifica si el modo prueba está activo en la base de datos"""
        try:
            conn = connect_db()
            if not conn:
                return False
                
            cursor = conn.cursor()
            
            # Verificar si el aparato de prueba está activo
            cursor.execute("""
                SELECT activo FROM aparatos_biometricos 
                WHERE serial = '0X0AB0' 
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                return result[0]  # Retorna True si está activo, False si no
            else:
                return False  # No existe el aparato de prueba
                
        except Exception as e:
            print(f"Error al verificar modo prueba: {e}")
            return False
    
    def obtener_id_mas_alto_k40(self):
        """Obtiene el ID más alto del dispositivo K40 y lo muestra en el campo ID usando la conexión existente"""
        # Verificar si estamos en modo prueba
        es_modo_prueba = self.verificar_modo_prueba_activo()
        
        if es_modo_prueba:
            # En modo prueba, generar un ID simulado
            import random
            uid_simulado = random.randint(1000, 9999)
            self.entry_id_k40.set(str(uid_simulado))
            print(f"🔧 Modo prueba: ID simulado generado: {uid_simulado}")
            return
        
        if not self.zkteco_connected or not self.zkteco:
            print("⚠️ No hay conexión activa para obtener el ID más alto")
            self.entry_id_k40.set("")
            return
            
        try:
            # Obtener solo los últimos 5 usuarios para optimizar rendimiento
            usuarios = self.zkteco.get_user_list(count=5, include_fingerprints=False)
            
            if usuarios:
                # Encontrar el UID más alto entre los últimos 5 usuarios
                uid_mas_alto = max(usuarios, key=lambda u: int(u['uid']))['uid']
                self.entry_id_k40.set(str(uid_mas_alto))
                print(f"✅ ID más alto detectado en K40 (últimos 5 usuarios): {uid_mas_alto}")
            else:
                print("⚠️ No hay usuarios registrados en el K40")
                self.entry_id_k40.set("")
        except Exception as e:
            print(f"⛔ Error al obtener ID más alto del K40: {e}")
            self.entry_id_k40.set("")
    
    def establecer_conexion_zkteco(self):
        """Establece una conexión única al ZKTeco que se mantendrá abierta"""
        try:
            self.zkteco = ZKTecoK40V2('192.168.100.201', 4370)
            if self.zkteco.connect():
                self.zkteco_connected = True
                print("✅ Conexión ZKTeco establecida y mantenida")
            else:
                self.zkteco_connected = False
                print("⚠️ No se pudo establecer conexión ZKTeco")
        except Exception as e:
            self.zkteco_connected = False
            print(f"⛔ Error al establecer conexión ZKTeco: {e}")
    
    def cerrar_conexion_zkteco(self):
        """Cierra la conexión ZKTeco si está abierta"""
        if self.zkteco and self.zkteco_connected:
            try:
                self.zkteco.disconnect()
                self.zkteco_connected = False
                print("✅ Conexión ZKTeco cerrada")
            except Exception as e:
                print(f"⚠️ Error al cerrar conexión ZKTeco: {e}")
    
    def on_closing(self):
        """Maneja el cierre de la ventana y cierra la conexión ZKTeco"""
        self.cerrar_conexion_zkteco()
        self.destroy()
    
    def mostrar_estado(self, mensaje, mostrar_progreso=True):
        """Muestra un mensaje de estado y opcionalmente una barra de progreso animada"""
        self.status_label.config(text=mensaje)
        self.status_frame.pack(fill='x', pady=(0, 10))
        
        if mostrar_progreso:
            self.animar_progreso()
        else:
            self.progress_bar.config(width=0)
    
    def ocultar_estado(self):
        """Oculta el indicador de estado"""
        # Solo ocultar la barra de progreso, mantener el estado del sistema
        self.progress_bar.config(width=0)
    
    def animar_progreso(self):
        """Anima la barra de progreso de forma indefinida"""
        def animar():
            if hasattr(self, 'status_frame') and self.status_frame.winfo_exists():
                # Obtener el ancho del frame de progreso
                frame_width = self.progress_frame.winfo_width()
                if frame_width > 0:
                    # Calcular posición de la barra (mover de izquierda a derecha)
                    current_width = self.progress_bar.winfo_width()
                    if current_width >= frame_width:
                        # Reiniciar desde el inicio
                        self.progress_bar.config(width=0)
                    else:
                        # Expandir la barra más rápido para mejor sincronización
                        self.progress_bar.config(width=current_width + 30)
                
                # Programar la siguiente animación
                self.after(80, animar)
        
        # Iniciar la animación
        animar()
    
    def completar_progreso(self):
        """Completa la barra de progreso al 100%"""
        if hasattr(self, 'progress_frame') and self.progress_frame.winfo_exists():
            frame_width = self.progress_frame.winfo_width()
            if frame_width > 0:
                self.progress_bar.config(width=frame_width)



    def convertir_a_mayusculas(self, *args):
        """Convierte automáticamente el texto a mayúsculas"""
        # Obtener el texto actual del campo que disparó el evento
        texto_actual = self.focus_get().get()
        if texto_actual:
            # Convertir a mayúsculas
            texto_mayusculas = texto_actual.upper()
            # Actualizar el campo solo si es diferente
            if texto_actual != texto_mayusculas:
                self.focus_get().delete(0, tk.END)
                self.focus_get().insert(0, texto_mayusculas)

    def calcular_edad(self, *args):
        """Calcula la edad en base a la fecha de nacimiento sin validaciones."""
        fecha_nac = self.entry_fecha_nacimiento.get().strip()
        
        # Ignorar si es el placeholder o está incompleta
        if fecha_nac == "DD/MM/AAAA" or not fecha_nac or fecha_nac.count('/') < 2:
            self.entry_edad.set("")
            return
            
        # Procesar la fecha con formato inteligente
        fecha_procesada = self.procesar_fecha_inteligente(fecha_nac)
        if fecha_procesada:
            try:
                fecha_nac = datetime.strptime(fecha_procesada, "%d/%m/%Y")
                hoy = datetime.today()
                edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
                
                # Simplemente mostrar la edad calculada sin validaciones
                self.entry_edad.set(str(edad))
                
                # Actualizar el campo con la fecha formateada correctamente si es necesario
                if fecha_procesada != fecha_nac:
                    self.entry_fecha_nacimiento.set(fecha_procesada)
                    
            except ValueError:
                self.entry_edad.set("")
        else:
            self.entry_edad.set("")

    def procesar_fecha_inteligente(self, fecha_texto):
        """
        Procesa una fecha en diferentes formatos y la convierte a DD/MM/YYYY
        Solo procesa fechas completas para evitar autocompletado no deseado
        """
        fecha_texto = fecha_texto.strip()
        
        # Si ya está en formato correcto DD/MM/YYYY, retornar tal como está
        if len(fecha_texto) == 10 and fecha_texto[2] == '/' and fecha_texto[5] == '/':
            try:
                datetime.strptime(fecha_texto, "%d/%m/%Y")
                return fecha_texto
            except ValueError:
                pass
        
        # Solo procesar si la fecha está completa (tiene 8 dígitos o formato DD/MM/YYYY)
        numeros = ''.join(filter(str.isdigit, fecha_texto))
        
        if len(numeros) != 8:  # Solo procesar fechas completas de 8 dígitos
            return None
            
        # Procesar DDMMYYYY
        dia = numeros[0:2]
        mes = numeros[2:4]
        anio = numeros[4:8]
        
        # Validar día y mes
        try:
            dia_int = int(dia)
            mes_int = int(mes)
            anio_int = int(anio)
            
            if dia_int < 1 or dia_int > 31 or mes_int < 1 or mes_int > 12:
                return None
                
            # Crear fecha para validar que existe
            fecha_test = datetime(anio_int, mes_int, dia_int)
            
            # Formatear con ceros a la izquierda
            fecha_formateada = f"{dia_int:02d}/{mes_int:02d}/{anio_int}"
            return fecha_formateada
            
        except ValueError:
            return None

    def obtener_fecha_hora_servidor(self):
        """Obtiene la fecha y hora actual del sistema local."""
        try:
            # Usar la hora local del sistema en lugar de la base de datos
            # para evitar problemas de zona horaria
            # Paraguay está en UTC-3 (America/Asuncion)
            fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.entry_fecha_registro.set(fecha_hora)
        except Exception as e:
            # Fallback en caso de error
            fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.entry_fecha_registro.set(fecha_hora)

    def guardar_postulante(self):
        """Guarda los datos del postulante en la base de datos y actualiza el K40 sin perder la huella."""
        # Mostrar estado inicial
        self.mostrar_estado("Validando datos...")
        
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        cedula = self.entry_cedula.get().strip()
        telefono = self.entry_telefono.get().strip()
        edad_str = self.entry_edad.get().strip()
        edad = int(edad_str) if edad_str.isdigit() else None
        sexo = self.entry_sexo.get().strip()
        fecha_nacimiento = self.entry_fecha_nacimiento.get().strip()
        unidad = self.entry_unidad.get().strip()
        fecha_registro = self.entry_fecha_registro.get().strip()
        dedo_registrado = self.entry_dedo.get().strip()
        registrado_por = self.registrador_string  # Usar el nombre completo del registrador
        id_manual = self.entry_id_k40.get().strip()
        
        # Log para debug
        print(f"🔍 Debug - Guardando registrado_por: '{registrado_por}'")

        # Verificar si hay un aparato biométrico detectado
        if self.aparato_id is None:
            self.ocultar_estado()
            messagebox.showerror("Error", "No se detectó ningún aparato biométrico.")
            return
        aparato_id = self.aparato_id

        # Validar campos obligatorios
        if not nombre or not apellido or not cedula or not dedo_registrado or sexo == "Seleccionar":
            self.ocultar_estado()
            messagebox.showerror("Error", "Todos los campos, incluido 'Dedo Registrado' y 'Sexo', son obligatorios.")
            return

        try:
            fecha_nacimiento = datetime.strptime(fecha_nacimiento, "%d/%m/%Y").strftime("%Y-%m-%d")
            fecha_registro = datetime.strptime(fecha_registro, "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            self.ocultar_estado()
            messagebox.showerror("Error", "Formato de fecha incorrecto. Usa DD/MM/AAAA para la Fecha de Nacimiento.")
            return

        # PASO 1: ACTUALIZAR EN EL K40 PRIMERO (solo si no es modo prueba)
        usuario_uid = None  # Inicializar variable para UID
        k40_actualizado = False  # Flag para verificar si se actualizó correctamente
        
        # Verificar si estamos en modo prueba
        es_modo_prueba = self.verificar_modo_prueba_activo()
        if es_modo_prueba:
            print("🔧 Modo prueba detectado - Saltando conexión K40")

        if not es_modo_prueba:
            self.mostrar_estado("Conectando al dispositivo K40...")
            
            if not self.zkteco_connected or not self.zkteco:
                self.ocultar_estado()
                messagebox.showerror("Error", "No hay conexión activa con el dispositivo K40.")
                return

            try:
                self.mostrar_estado("Obteniendo lista de usuarios...")
                # Obtener solo los últimos 5 usuarios para optimizar rendimiento
                usuarios = self.zkteco.get_user_list(count=5, include_fingerprints=False)

                if not usuarios:
                    self.ocultar_estado()
                    messagebox.showerror("Error", "No hay usuarios registrados en el K40.")
                    return

                # Si el operador ingresó un ID manualmente, buscarlo
                if id_manual.isdigit():
                    self.mostrar_estado("Buscando usuario específico...")
                    usuario_manual = next((u for u in usuarios if str(u['uid']) == id_manual), None)
                    if usuario_manual:
                        ultimo_usuario = usuario_manual
                    else:
                        self.ocultar_estado()
                        messagebox.showerror("Error", f"No se encontró un usuario con ID {id_manual} en los últimos 5 usuarios del K40. Intente ingresar un ID más reciente.")
                        return
                else:
                    # Buscar el usuario más reciente sin `user_id` entre los últimos 5
                    self.mostrar_estado("Buscando usuario disponible...")
                    usuarios_sin_id = [u for u in usuarios if not u.get('user_id') or u.get('user_id', '').startswith("NN-")]
                    if usuarios_sin_id:
                        ultimo_usuario = usuarios_sin_id[-1]
                    else:
                        ultimo_usuario = max(usuarios, key=lambda u: int(u['uid']))

                if ultimo_usuario:
                    usuario_uid = ultimo_usuario['uid']  # Mantener el mismo UID
                    usuario_id_actual = ultimo_usuario.get('user_id', '')  # Mantener el mismo ID

                    # Si el usuario ya tiene un nombre real asignado, dirigir al usuario a la función de edición
                    if ultimo_usuario.get('name') and not ultimo_usuario.get('name', '').startswith("NN-"):
                        self.ocultar_estado()
                        
                        # Obtener el nombre del aparato para el mensaje
                        nombre_aparato = "Desconocido"
                        try:
                            conn = connect_db()
                            cursor = conn.cursor()
                            cursor.execute("SELECT nombre FROM aparatos_biometricos WHERE id = %s", (self.aparato_id,))
                            resultado = cursor.fetchone()
                            if resultado:
                                nombre_aparato = resultado[0]
                            cursor.close()
                            conn.close()
                        except:
                            pass
                        
                        messagebox.showwarning(
                            "Usuario ya registrado",
                            f"El usuario con ID {usuario_uid} en el aparato {nombre_aparato} ya tiene un nombre asignado: '{ultimo_usuario['name']}'.\n\n"
                            "Si es que lo necesita siga esta guía:\n\n"
                            "Para modificar los datos de un usuario existente, utiliza la función:\n"
                            "BUSCAR POSTULANTES → Editar Postulante\n\n"
                            "IMPORTANTE: Después de editar y actualizar la información en la base de datos, asegúrate de sincronizar manualmente en el aparato biométrico para que los cambios también se reflejen en el ahí los cambios para evitar inconsistencias entre ambos sistemas.\n\n"
                            "Esta función es solo para agregar nuevos postulantes."
                        )
                        return  # Salir sin hacer cambios

                    # ACTUALIZAR EL USUARIO EN EL K40 (solo si no tiene nombre asignado)
                    self.mostrar_estado("Actualizando usuario en dispositivo...")
                    resultado_k40 = self.zkteco.set_user(
                        uid=usuario_uid,
                        name=f"{nombre} {apellido}",
                        privilege=ultimo_usuario.get('privilege', 0),
                        password="",
                        group_id=ultimo_usuario.get('group_id', ''),
                        user_id=usuario_id_actual
                    )

                    # Verificar si la actualización en K40 fue exitosa
                    if resultado_k40:
                        k40_actualizado = True
                        print(f"✅ Usuario {usuario_id_actual} actualizado en K40 sin perder la huella.")
                    else:
                        self.ocultar_estado()
                        messagebox.showerror("Error", "No se pudo actualizar el usuario en el dispositivo K40. No se guardará en la base de datos.")
                        return

                else:
                    self.ocultar_estado()
                    messagebox.showerror("Error", "No se encontró un usuario registrado recientemente en el K40.")
                    return

            except Exception as e:
                self.ocultar_estado()
                messagebox.showerror("Error", f"No se pudo actualizar el K40: {e}. No se guardará en la base de datos.")
                return
        else:
            # Modo prueba - generar UID simulado (solo detección automática)
            if es_modo_prueba:
                import random
                usuario_uid = random.randint(1000, 9999)  # UID simulado
                k40_actualizado = True
                print(f"🔧 Modo prueba: UID simulado generado: {usuario_uid}")

        # PASO 2: SOLO SI EL K40 SE ACTUALIZÓ CORRECTAMENTE, GUARDAR EN LA BASE DE DATOS
        if not k40_actualizado:
            self.ocultar_estado()
            messagebox.showerror("Error", "No se pudo actualizar el K40. No se guardará en la base de datos.")
            return

        # VERIFICAR PROBLEMAS JUDICIALES ANTES DE GUARDAR
        from database import verificar_cedula_problema_judicial
        
        # Verificar si hay problemas judiciales
        problema_judicial = verificar_cedula_problema_judicial(cedula)
        
        if problema_judicial:
            # Mostrar diálogo de confirmación para problemas judiciales
            respuesta = messagebox.askyesno(
                "⚠️ ADVERTENCIA - Problema Judicial",
                f"ADVERTENCIA: Este postulante con CI {cedula} podría tener problemas judiciales.\n\n"
                f"Es recomendable verificar la situación real del mismo antes de continuar.\n\n"
                f"¿Quiere proceder con el registro de todos modos?",
                icon='warning'
            )
            
            if not respuesta:
                # Usuario canceló el registro
                self.ocultar_estado()
                messagebox.showinfo(
                    "Registro Cancelado",
                    "El registro del postulante ha sido cancelado debido al problema judicial detectado."
                )
                return
        
        self.mostrar_estado("Guardando datos en base de datos...")
        
        # Usar la función de database.py que copia automáticamente el nombre del registrador
        from database import agregar_postulante
        
        postulante_data = {
            'nombre': nombre,
            'apellido': apellido,
            'cedula': cedula,
            'fecha_nacimiento': fecha_nacimiento,
            'telefono': telefono,
            'fecha_registro': fecha_registro,
            'usuario_registrador': self.usuario_registrador,
            'nombre_registrador': self.registrador_string,  # Enviar el nombre completo directamente
            'edad': edad,
            'sexo': sexo,
            'unidad': unidad,
            'dedo_registrado': dedo_registrado,
            'aparato_id': aparato_id,
            'uid_k40': usuario_uid
        }
        
        try:
            resultado = agregar_postulante(postulante_data)
            
            if resultado['success']:
                # Obtener el nombre del aparato biométrico
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("SELECT nombre FROM aparatos_biometricos WHERE id = %s", (aparato_id,))
                aparato_nombre = cursor.fetchone()
                aparato_nombre = aparato_nombre[0] if aparato_nombre else "Aparato Desconocido"
                cursor.close()
                conn.close()
                
                # MENSAJE DE ÉXITO Y CERRAR VENTANA
                self.ocultar_estado()
                
                # Mostrar mensaje de éxito
                if problema_judicial:
                    messagebox.showinfo(
                        "Registro Confirmado",
                        f"Postulante registrado correctamente en el aparato {aparato_nombre}, con UID {usuario_uid}.\n\n"
                        "⚠️ Nota: Se registró a pesar del problema judicial detectado."
                    )
                else:
                    messagebox.showinfo(
                        "Éxito",
                        f"Postulante registrado correctamente en el aparato {aparato_nombre}, con UID {usuario_uid}."
                    )
                self.on_closing()
            else:
                self.ocultar_estado()
                messagebox.showerror("Error", resultado['message'])
                return

        except Exception as e:
            self.ocultar_estado()
            messagebox.showerror("Error", f"No se pudo guardar en la base de datos: {e}")
            return

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
    
    app = AgregarPostulante(root, user_data)
    root.mainloop()

if __name__ == "__main__":
    main() 