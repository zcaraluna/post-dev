#!/usr/bin/env python3
"""
Módulo para editar postulantes existentes en el sistema
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import actualizar_postulante, obtener_postulante_por_id
import ctypes

# Configurar DPI para Windows (HD/4K)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Per Monitor DPI Aware
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()  # Fallback para versiones anteriores
    except:
        pass

class EditarPostulante(tk.Toplevel):
    def __init__(self, parent, user_data, postulante_id, callback=None):
        super().__init__(parent)
        self.title("Editar Postulante - Sistema QUIRA")
        self.geometry("")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Configurar estilo moderno
        self.configure(bg='#f0f0f0')
        
        self.user_data = user_data
        self.postulante_id = postulante_id
        self.postulante_data = None
        self.callback = callback  # Callback para notificar cuando se complete la edición
        
        # Cargar datos del postulante
        self.cargar_datos_postulante()
        
        # Frame principal con padding y estilo
        frame_main = tk.Frame(self, bg='#f0f0f0', padx=30, pady=20)
        frame_main.pack(expand=True, fill='both')

        # Título principal
        title_frame = tk.Frame(frame_main, bg='#f0f0f0')
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(title_frame, text="EDITAR POSTULANTE", 
                               font=('Segoe UI', 16, 'bold'), 
                               fg='#2c3e50', bg='#f0f0f0')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Sistema de Registro Biométrico", 
                                 font=('Segoe UI', 10), 
                                 fg='#7f8c8d', bg='#f0f0f0')
        subtitle_label.pack()

        # Frame para el formulario
        form_frame = tk.Frame(frame_main, bg='white', relief='solid', bd=2)
        form_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Configurar grid del formulario
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        # Variables para los campos
        self.entry_nombre = tk.StringVar()
        self.entry_apellido = tk.StringVar()
        self.entry_cedula = tk.StringVar()
        self.entry_telefono = tk.StringVar()
        self.entry_fecha_nacimiento = tk.StringVar()
        self.entry_edad = tk.StringVar()

        self.entry_unidad = tk.StringVar()
        self.entry_dedo = tk.StringVar()
        self.entry_observaciones = tk.StringVar()
        
        # Valores para comboboxes
        self.unidades = ["Unidad 1", "Unidad 2", "Unidad 3", "Unidad 4"]
        self.dedos = ["PD", "ID", "MD", "AD", "MeD", "PI", "II", "MI", "AI", "MeI"]

        # Sección 1: Información Personal
        self.crear_seccion_titulo(form_frame, "INFORMACIÓN PERSONAL", 0)
        
        # Nombre y Apellido en la misma fila
        self.crear_campo_horizontal(form_frame, "Nombre:", self.entry_nombre, 1, "Apellido:", self.entry_apellido)
        
        # Cédula y Teléfono en la misma fila
        self.crear_campo_horizontal(form_frame, "Cédula:", self.entry_cedula, 2, "Teléfono:", self.entry_telefono)
        
        # Fecha de Nacimiento y Edad en la misma fila
        self.crear_campo_fecha_inteligente(form_frame, "Fecha Nacimiento:", self.entry_fecha_nacimiento, 3, "Edad:", self.entry_edad, readonly2=True)
        

        
        # Sección 2: Información del Registro
        self.crear_seccion_titulo(form_frame, "INFORMACIÓN DEL REGISTRO", 5)
        
        # Unidad y Dedo Registrado en la misma fila
        self.crear_campo_horizontal_combobox(form_frame, "Unidad:", self.entry_unidad, 6, "Dedo Registrado:", self.entry_dedo, self.unidades, self.dedos)
        
        # Observaciones
        self.crear_campo_texto(form_frame, "Observaciones:", self.entry_observaciones, 7)

        # Frame para botones centrados
        button_frame = tk.Frame(frame_main, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=20)

        # Frame interno para centrar los botones
        button_center_frame = tk.Frame(button_frame, bg='#f0f0f0')
        button_center_frame.pack(expand=True)

        # Botón Guardar con estilo moderno
        save_button = tk.Button(button_center_frame, text="GUARDAR CAMBIOS", 
                               command=self.guardar_cambios,
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', bg='#27ae60',
                               activebackground='#229954',
                               relief='flat', bd=0,
                               padx=30, pady=12,
                               cursor='hand2')

        # Botón Cancelar
        cancel_button = tk.Button(button_center_frame, text="CANCELAR", 
                                 command=self.destroy,
                                 font=('Segoe UI', 12),
                                 fg='white', bg='#e74c3c',
                                 activebackground='#c0392b',
                                 relief='flat', bd=0,
                                 padx=30, pady=12,
                                 cursor='hand2')
        
        # Centrar los botones
        save_button.pack(side='left', padx=(0, 10))
        cancel_button.pack(side='left')

        # Configurar eventos
        self.entry_fecha_nacimiento.trace('w', self.calcular_edad)
        
        # Cargar datos en el formulario después de crear la interfaz
        self.after(100, self.cargar_datos_en_formulario)

    def cargar_datos_postulante(self):
        """Cargar los datos del postulante desde la base de datos"""
        self.postulante_data = obtener_postulante_por_id(self.postulante_id)
        
        if not self.postulante_data:
            messagebox.showerror("Error", "No se pudo cargar los datos del postulante")
            self.destroy()
            return

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
        entry.grid(row=row, column=1, columnspan=3, sticky='ew', pady=8, padx=(0, 10))

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

    def crear_campo_fecha_inteligente(self, parent, label1, var1, row, label2, var2, readonly1=False, readonly2=False):
        """Crear campo de fecha inteligente con calendario y validación"""
        # Primer campo (Fecha de Nacimiento)
        label1_widget = tk.Label(parent, text=label1, 
                                 font=('Segoe UI', 10, 'bold'), 
                                 fg='#2c3e50', bg='white', anchor='w')
        label1_widget.grid(row=row, column=0, sticky='w', pady=8, padx=10)
        
        # Frame para el campo de fecha y botón de calendario
        fecha_frame = tk.Frame(parent, bg='white')
        fecha_frame.grid(row=row, column=1, sticky='ew', pady=8, padx=(0, 5))
        
        # Entry para fecha con placeholder
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
            
            entry1.bind('<FocusIn>', on_focus_in)
            entry1.bind('<FocusOut>', on_focus_out)
        
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

    def crear_campo_texto(self, parent, label_text, variable, row):
        """Crear campo de texto multilínea"""
        # Label con información adicional para observaciones
        if "observaciones" in label_text.lower():
            label_text_with_info = f"{label_text} (Se agregarán a las existentes)"
            label = tk.Label(parent, text=label_text_with_info, 
                             font=('Segoe UI', 10, 'bold'), 
                             fg='#2c3e50', bg='white', anchor='w')
        else:
            label = tk.Label(parent, text=label_text, 
                             font=('Segoe UI', 10, 'bold'), 
                             fg='#2c3e50', bg='white', anchor='w')
        label.grid(row=row, column=0, sticky='w', pady=8, padx=10)
        
        # Text widget
        text_widget = tk.Text(parent, height=4, font=('Segoe UI', 10),
                             relief='solid', bd=2,
                             highlightthickness=1, highlightcolor='#3498db',
                             bg='white')
        text_widget.grid(row=row, column=1, columnspan=3, sticky='ew', pady=8, padx=(0, 10))
        
        # Scrollbar para el texto
        scrollbar = tk.Scrollbar(parent, orient='vertical', command=text_widget.yview)
        scrollbar.grid(row=row, column=4, sticky='ns', pady=8)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Botón para ver observaciones existentes (solo para observaciones)
        if "observaciones" in label_text.lower():
            def mostrar_observaciones_existentes():
                observaciones_existentes = getattr(self, 'postulante_data', None)
                if observaciones_existentes and observaciones_existentes[15]:
                    # Crear ventana para mostrar observaciones existentes
                    ventana_obs = tk.Toplevel(self)
                    ventana_obs.title("Observaciones Existentes")
                    ventana_obs.geometry("500x400")
                    ventana_obs.transient(self)
                    ventana_obs.grab_set()
                    ventana_obs.configure(bg='#f0f0f0')
                    
                    # Frame principal
                    main_frame = tk.Frame(ventana_obs, bg='#f0f0f0', padx=20, pady=20)
                    main_frame.pack(expand=True, fill='both')
                    
                    # Título
                    titulo = tk.Label(main_frame, text="Observaciones Existentes", 
                                      font=('Segoe UI', 14, 'bold'), 
                                      fg='#2c3e50', bg='#f0f0f0')
                    titulo.pack(pady=(0, 15))
                    
                    # Área de texto para mostrar observaciones
                    text_area = tk.Text(main_frame, wrap='word', font=('Segoe UI', 10),
                                       relief='solid', bd=1, bg='white', fg='#2c3e50')
                    text_area.pack(expand=True, fill='both', pady=(0, 15))
                    
                    # Insertar observaciones existentes
                    text_area.insert('1.0', observaciones_existentes[15])
                    text_area.config(state='disabled')  # Solo lectura
                    
                    # Botón cerrar
                    tk.Button(main_frame, text="Cerrar", command=ventana_obs.destroy,
                              font=('Segoe UI', 10, 'bold'), fg='white', bg='#3498db',
                              relief='flat', padx=20, pady=5).pack()
                else:
                    messagebox.showinfo("Observaciones", "No hay observaciones existentes para este postulante.")
            
            # Botón para ver observaciones existentes
            btn_ver_obs = tk.Button(parent, text="📋 Ver existentes", 
                                   command=mostrar_observaciones_existentes,
                                   font=('Segoe UI', 8), fg='white', bg='#95a5a6',
                                   relief='flat', padx=10, pady=2)
            btn_ver_obs.grid(row=row+1, column=1, sticky='w', pady=(0, 8), padx=(0, 10))
        
        # Placeholder para observaciones
        if "observaciones" in label_text.lower():
            placeholder_text = "Escriba aquí las nuevas observaciones...\n(Se agregarán automáticamente a las observaciones existentes)"
            text_widget.insert('1.0', placeholder_text)
            text_widget.config(fg='gray')
            
            def on_focus_in(event):
                if text_widget.get('1.0', tk.END).strip() == placeholder_text:
                    text_widget.delete('1.0', tk.END)
                    text_widget.config(fg='black')
            
            def on_focus_out(event):
                if not text_widget.get('1.0', tk.END).strip():
                    text_widget.insert('1.0', placeholder_text)
                    text_widget.config(fg='gray')
            
            text_widget.bind('<FocusIn>', on_focus_in)
            text_widget.bind('<FocusOut>', on_focus_out)
        
        # Vincular con la variable
        def update_variable(*args):
            current_text = text_widget.get('1.0', tk.END).strip()
            # No incluir el placeholder en la variable
            if "observaciones" in label_text.lower() and current_text == placeholder_text:
                variable.set('')
            else:
                variable.set(current_text)
        
        text_widget.bind('<KeyRelease>', update_variable)
        
        return text_widget

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
        ventana_calendario.geometry("300x350")
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

    def calcular_edad(self, *args):
        """Calcula la edad en base a la fecha de nacimiento con formato inteligente."""
        fecha_nac = self.entry_fecha_nacimiento.get().strip()
        
        # Ignorar si es el placeholder
        if fecha_nac == "DD/MM/AAAA" or not fecha_nac:
            return
            
        # Procesar la fecha con formato inteligente
        fecha_procesada = self.procesar_fecha_inteligente(fecha_nac)
        if fecha_procesada:
            try:
                fecha_nac = datetime.strptime(fecha_procesada, "%d/%m/%Y")
                hoy = datetime.today()
                edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
                
                # Validar que la edad sea razonable
                if 0 <= edad <= 120:
                    self.entry_edad.set(str(edad))
                    # Actualizar el campo con la fecha formateada correctamente
                    if fecha_procesada != fecha_nac:
                        self.entry_fecha_nacimiento.set(fecha_procesada)
                else:
                    self.entry_edad.set("")
                    messagebox.showwarning("Advertencia", f"La edad calculada ({edad} años) parece incorrecta. Verifica la fecha de nacimiento.")
            except ValueError:
                self.entry_edad.set("")
        else:
            self.entry_edad.set("")

    def procesar_fecha_inteligente(self, fecha_texto):
        """
        Procesa una fecha en diferentes formatos y la convierte a DD/MM/YYYY
        """
        fecha_texto = fecha_texto.strip()
        
        # Si ya está en formato correcto DD/MM/YYYY, retornar tal como está
        if len(fecha_texto) == 10 and fecha_texto[2] == '/' and fecha_texto[5] == '/':
            try:
                datetime.strptime(fecha_texto, "%d/%m/%Y")
                return fecha_texto
            except ValueError:
                pass
        
        # Remover todos los separadores no numéricos
        numeros = ''.join(filter(str.isdigit, fecha_texto))
        
        if not numeros:
            return None
            
        # Procesar según la longitud de los números
        if len(numeros) == 8:  # DDMMYYYY
            dia = numeros[0:2]
            mes = numeros[2:4]
            anio = numeros[4:8]
            
        elif len(numeros) == 6:  # DDMMYY
            dia = numeros[0:2]
            mes = numeros[2:4]
            anio = numeros[4:6]
            # Asumir que años 00-29 son 2000-2029, años 30-99 son 1930-1999
            if int(anio) <= 29:
                anio = "20" + anio
            else:
                anio = "19" + anio
                
        elif len(numeros) == 4:  # DDMM (asumir año actual)
            dia = numeros[0:2]
            mes = numeros[2:4]
            anio = str(datetime.now().year)
            
        else:
            return None
        
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

    def cargar_datos_en_formulario(self):
        """Cargar los datos del postulante en el formulario"""
        if not self.postulante_data:
            return
            
        # Cargar datos básicos
        # Los índices están basados en la consulta de obtener_postulante_por_id:
        # id, nombre, apellido, cedula, fecha_nacimiento, telefono, fecha_registro, usuario_registrador, edad, unidad, 
        # dedo_registrado, registrado_por, aparato_id, uid_k40, huella_dactilar, observaciones
        
        self.entry_nombre.set(self.postulante_data[1] or '')
        self.entry_apellido.set(self.postulante_data[2] or '')
        self.entry_cedula.set(self.postulante_data[3] or '')
        self.entry_telefono.set(self.postulante_data[5] or '')

        self.entry_edad.set(str(self.postulante_data[8]) if self.postulante_data[8] else '')  # edad (índice 8)
        self.entry_unidad.set(self.postulante_data[9] or '')  # unidad (índice 9)
        self.entry_dedo.set(self.postulante_data[10] or '')  # dedo_registrado (índice 10)
        # Para observaciones, no cargar en el campo de texto (se mostrarán en el placeholder)
        # Las observaciones existentes se mantienen en self.postulante_data[15]
        self.entry_observaciones.set('')  # Campo vacío para nuevas observaciones
        
        # Cargar fecha de nacimiento
        if self.postulante_data[4]:  # fecha_nacimiento
            fecha_nac = self.postulante_data[4]
            if isinstance(fecha_nac, str):
                # Si es string, intentar parsear
                try:
                    fecha_obj = datetime.strptime(fecha_nac, "%Y-%m-%d")
                    fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
                    self.entry_fecha_nacimiento.set(fecha_formateada)
                except:
                    self.entry_fecha_nacimiento.set("")
            else:
                # Si es objeto date
                fecha_formateada = fecha_nac.strftime("%d/%m/%Y")
                self.entry_fecha_nacimiento.set(fecha_formateada)

    def guardar_cambios(self):
        """Guardar los cambios del postulante"""
        # Obtener datos del formulario
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        cedula = self.entry_cedula.get().strip()
        telefono = self.entry_telefono.get().strip()

        fecha_nacimiento = self.entry_fecha_nacimiento.get().strip()
        edad = self.entry_edad.get().strip()
        unidad = self.entry_unidad.get().strip()
        dedo_registrado = self.entry_dedo.get().strip()
        observaciones = self.entry_observaciones.get().strip()

        # Validar campos obligatorios
        if not nombre or not apellido or not cedula:
            messagebox.showerror("Error", "Los campos Nombre, Apellido y Cédula son obligatorios.")
            return

        # Procesar fecha de nacimiento
        try:
            if fecha_nacimiento and fecha_nacimiento != "DD/MM/AAAA":
                fecha_procesada = self.procesar_fecha_inteligente(fecha_nacimiento)
                if fecha_procesada:
                    fecha_nacimiento = datetime.strptime(fecha_procesada, "%d/%m/%Y").strftime("%Y-%m-%d")
                else:
                    messagebox.showerror("Error", "Formato de fecha de nacimiento incorrecto.")
                    return
            else:
                fecha_nacimiento = None
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha de nacimiento incorrecto.")
            return

        # Manejar observaciones de manera inteligente
        observaciones_actuales = self.postulante_data[15] or ''  # Observaciones existentes
        nuevas_observaciones = observaciones.strip()
        
        # Obtener información del usuario actual
        nombre_usuario = f"{self.user_data.get('nombre', '')} {self.user_data.get('apellido', '')}".strip()
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        # Si hay observaciones existentes y nuevas observaciones
        if observaciones_actuales and nuevas_observaciones:
            # Verificar si las nuevas observaciones ya están incluidas
            if nuevas_observaciones not in observaciones_actuales:
                # Agregar las nuevas observaciones con formato mejorado
                nueva_obs_formateada = f"[{timestamp}] {nombre_usuario}:\n{nuevas_observaciones}"
                observaciones_finales = f"{observaciones_actuales}\n\n{nueva_obs_formateada}"
            else:
                # Si ya están incluidas, mantener las existentes
                observaciones_finales = observaciones_actuales
        elif observaciones_actuales:
            # Solo hay observaciones existentes
            observaciones_finales = observaciones_actuales
        elif nuevas_observaciones:
            # Solo hay nuevas observaciones (primera observación)
            observaciones_finales = f"[{timestamp}] {nombre_usuario}:\n{nuevas_observaciones}"
        else:
            # No hay observaciones
            observaciones_finales = ''
        
        # Preparar datos para actualización
        postulante_data = {
            'nombre': nombre,
            'apellido': apellido,
            'cedula': cedula,
            'fecha_nacimiento': fecha_nacimiento,
            'telefono': telefono,
            'edad': int(edad) if edad and edad.isdigit() else None,
            'unidad': unidad,
            'dedo_registrado': dedo_registrado,
            'observaciones': observaciones_finales
        }

        # Actualizar en la base de datos
        if actualizar_postulante(self.postulante_id, postulante_data, self.user_data):
            # Mensaje informativo sobre las observaciones
            if observaciones_actuales and nuevas_observaciones:
                messagebox.showinfo("Éxito", 
                    "Postulante actualizado correctamente.\n\n"
                    "✅ Las nuevas observaciones se han agregado a las existentes.\n"
                    "📝 Total de observaciones actualizadas.")
            else:
                messagebox.showinfo("Éxito", "Postulante actualizado correctamente.")
            
            # Llamar callback si existe, pasando los datos actualizados
            if self.callback:
                self.callback(postulante_data)
            
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el postulante.")

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
    
    # ID de postulante de prueba
    postulante_id = 1
    
    app = EditarPostulante(root, user_data, postulante_id)
    root.mainloop()

if __name__ == "__main__":
    main() 