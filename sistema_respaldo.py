#!/usr/bin/env python3
"""
Sistema de Respaldo Local para Sistema QUIRA
Optimizado para entornos sin internet
"""

import os
import shutil
import zipfile
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import psycopg2
from psycopg2 import sql
import threading
import time
from tkinter import messagebox, filedialog
import tkinter as tk
from tkinter import ttk

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SistemaRespaldo:
    def __init__(self, config_path="config_respaldo.json"):
        """
        Inicializar sistema de respaldo
        
        Args:
            config_path (str): Ruta al archivo de configuración
        """
        self.config_path = config_path
        self.config = self.cargar_configuracion()
        self.crear_directorios_respaldo()
        
    def cargar_configuracion(self):
        """Cargar configuración de respaldo"""
        config_default = {
            "directorio_respaldo": "./backups",
            "respaldo_diario": True,
            "respaldo_semanal": True,
            "respaldo_mensual": True,
            "retener_diarios": 7,  # días
            "retener_semanales": 4,  # semanas
            "retener_mensuales": 12,  # meses
            "comprimir_respaldos": True,
            "verificar_integridad": True,
            "dispositivos_usb": [],
            "incluir_zkteco": True,
            "incluir_logs": True,
            "hora_respaldo_automatico": "14:30"
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Combinar con configuración por defecto
                    config_default.update(config)
                    return config_default
            else:
                # Crear archivo de configuración por defecto
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(config_default, f, indent=4, ensure_ascii=False)
                return config_default
        except Exception as e:
            logger.error(f"Error al cargar configuración: {e}")
            return config_default
    
    def crear_directorios_respaldo(self):
        """Crear estructura de directorios para respaldos"""
        directorios = [
            self.config["directorio_respaldo"],
            f"{self.config['directorio_respaldo']}/diario",
            f"{self.config['directorio_respaldo']}/semanal",
            f"{self.config['directorio_respaldo']}/mensual",
            f"{self.config['directorio_respaldo']}/logs",
            f"{self.config['directorio_respaldo']}/zkteco"
        ]
        
        for directorio in directorios:
            Path(directorio).mkdir(parents=True, exist_ok=True)
    
    def respaldo_base_datos(self, tipo="completo"):
        """
        Crear respaldo de la base de datos PostgreSQL
        
        Args:
            tipo (str): "completo" o "incremental"
            
        Returns:
            str: Ruta del archivo de respaldo creado
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nombre_archivo = f"bd_{tipo}_{timestamp}.sql"
        ruta_respaldo = os.path.join(self.config["directorio_respaldo"], 
                                    "diario" if tipo == "incremental" else "semanal",
                                    nombre_archivo)
        
        try:
            # Comando pg_dump para PostgreSQL
            comando = [
                "pg_dump",
                "-h", "localhost",
                "-U", "postgres",
                "-d", "sistema_postulantes",
                "-f", ruta_respaldo,
                "--no-password"
            ]
            
            # Configurar variable de entorno para la contraseña
            env = os.environ.copy()
            env["PGPASSWORD"] = "admin123"
            
            import subprocess
            resultado = subprocess.run(comando, env=env, capture_output=True, text=True)
            
            if resultado.returncode == 0:
                logger.info(f"✅ Respaldo de BD creado: {ruta_respaldo}")
                
                # Comprimir si está habilitado
                if self.config["comprimir_respaldos"]:
                    ruta_comprimida = self.comprimir_archivo(ruta_respaldo)
                    os.remove(ruta_respaldo)  # Eliminar archivo original
                    return ruta_comprimida
                
                return ruta_respaldo
            else:
                logger.error(f"❌ Error en respaldo de BD: {resultado.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error al crear respaldo de BD: {e}")
            return None
    
    def respaldo_zkteco(self):
        """
        Crear respaldo del dispositivo ZKTeco
        
        Returns:
            str: Ruta del archivo de respaldo creado
        """
        if not self.config["incluir_zkteco"]:
            return None
            
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nombre_archivo = f"zkteco_{timestamp}.json"
        ruta_respaldo = os.path.join(self.config["directorio_respaldo"], "zkteco", nombre_archivo)
        
        try:
            from zkteco_connector_v2 import ZKTecoK40V2
            
            zkteco = ZKTecoK40V2()
            if zkteco.connect():
                # Obtener datos del dispositivo
                datos_zkteco = {
                    "timestamp": timestamp,
                    "usuarios": zkteco.get_users(),
                    "registros_asistencia": zkteco.get_attendance(),
                    "configuracion": zkteco.get_device_info(),
                    "logs": zkteco.get_logs() if hasattr(zkteco, 'get_logs') else []
                }
                
                # Guardar datos en JSON
                with open(ruta_respaldo, 'w', encoding='utf-8') as f:
                    json.dump(datos_zkteco, f, indent=4, ensure_ascii=False)
                
                zkteco.disconnect()
                logger.info(f"✅ Respaldo de ZKTeco creado: {ruta_respaldo}")
                return ruta_respaldo
            else:
                logger.warning("⚠️ No se pudo conectar al dispositivo ZKTeco")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error al crear respaldo de ZKTeco: {e}")
            return None
    
    def respaldo_logs_sistema(self):
        """
        Crear respaldo de logs del sistema
        
        Returns:
            str: Ruta del archivo de respaldo creado
        """
        if not self.config["incluir_logs"]:
            return None
            
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nombre_archivo = f"logs_{timestamp}.zip"
        ruta_respaldo = os.path.join(self.config["directorio_respaldo"], "logs", nombre_archivo)
        
        try:
            with zipfile.ZipFile(ruta_respaldo, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Buscar archivos de log en el directorio actual
                for archivo in Path(".").glob("*.log"):
                    zipf.write(archivo, archivo.name)
                
                # Incluir logs del sistema si existen
                log_dirs = ["logs", "log", "__pycache__"]
                for log_dir in log_dirs:
                    if os.path.exists(log_dir):
                        for archivo in Path(log_dir).rglob("*"):
                            if archivo.is_file():
                                zipf.write(archivo, archivo.relative_to("."))
            
            logger.info(f"✅ Respaldo de logs creado: {ruta_respaldo}")
            return ruta_respaldo
            
        except Exception as e:
            logger.error(f"❌ Error al crear respaldo de logs: {e}")
            return None
    
    def comprimir_archivo(self, ruta_archivo):
        """
        Comprimir un archivo individual
        
        Args:
            ruta_archivo (str): Ruta del archivo a comprimir
            
        Returns:
            str: Ruta del archivo comprimido
        """
        ruta_comprimida = f"{ruta_archivo}.gz"
        
        try:
            import gzip
            with open(ruta_archivo, 'rb') as f_in:
                with gzip.open(ruta_comprimida, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            return ruta_comprimida
        except Exception as e:
            logger.error(f"❌ Error al comprimir archivo: {e}")
            return ruta_archivo
    
    def crear_respaldo_completo(self):
        """
        Crear un respaldo completo del sistema
        
        Returns:
            dict: Información del respaldo creado
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nombre_paquete = f"respaldo_completo_{timestamp}.zip"
        ruta_paquete = os.path.join(self.config["directorio_respaldo"], "mensual", nombre_paquete)
        
        archivos_respaldo = []
        
        try:
            # 1. Respaldo de base de datos
            bd_respaldo = self.respaldo_base_datos("completo")
            if bd_respaldo:
                archivos_respaldo.append(bd_respaldo)
            
            # 2. Respaldo de ZKTeco
            zkteco_respaldo = self.respaldo_zkteco()
            if zkteco_respaldo:
                archivos_respaldo.append(zkteco_respaldo)
            
            # 3. Respaldo de logs
            logs_respaldo = self.respaldo_logs_sistema()
            if logs_respaldo:
                archivos_respaldo.append(logs_respaldo)
            
            # 4. Crear paquete completo
            with zipfile.ZipFile(ruta_paquete, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for archivo in archivos_respaldo:
                    if os.path.exists(archivo):
                        zipf.write(archivo, os.path.basename(archivo))
                
                # Agregar archivos de configuración importantes
                archivos_config = [
                    "config_respaldo.json",
                    "database.py",
                    "requirements.txt"
                ]
                
                for archivo_config in archivos_config:
                    if os.path.exists(archivo_config):
                        zipf.write(archivo_config, archivo_config)
                
                # Agregar metadata del respaldo
                metadata = {
                    "timestamp": timestamp,
                    "tipo": "completo",
                    "archivos_incluidos": [os.path.basename(f) for f in archivos_respaldo],
                    "version_sistema": "1.0",
                    "checksum": self.calcular_checksum(ruta_paquete)
                }
                
                zipf.writestr("metadata.json", json.dumps(metadata, indent=4, ensure_ascii=False))
            
            # Limpiar archivos temporales
            for archivo in archivos_respaldo:
                if os.path.exists(archivo):
                    os.remove(archivo)
            
            logger.info(f"✅ Respaldo completo creado: {ruta_paquete}")
            
            return {
                "ruta": ruta_paquete,
                "tamaño": os.path.getsize(ruta_paquete),
                "timestamp": timestamp,
                "archivos": len(archivos_respaldo)
            }
            
        except Exception as e:
            logger.error(f"❌ Error al crear respaldo completo: {e}")
            return None
    
    def calcular_checksum(self, ruta_archivo):
        """Calcular checksum MD5 de un archivo"""
        import hashlib
        
        try:
            with open(ruta_archivo, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Error al calcular checksum: {e}")
            return None
    
    def verificar_integridad(self, ruta_archivo):
        """
        Verificar integridad de un archivo de respaldo
        
        Args:
            ruta_archivo (str): Ruta del archivo a verificar
            
        Returns:
            bool: True si el archivo está íntegro
        """
        if not self.config["verificar_integridad"]:
            return True
            
        try:
            if ruta_archivo.endswith('.zip'):
                with zipfile.ZipFile(ruta_archivo, 'r') as zipf:
                    # Verificar que el archivo ZIP no esté corrupto
                    zipf.testzip()
                    
                    # Verificar metadata si existe
                    if 'metadata.json' in zipf.namelist():
                        metadata = json.loads(zipf.read('metadata.json'))
                        checksum_guardado = metadata.get('checksum')
                        checksum_actual = self.calcular_checksum(ruta_archivo)
                        
                        if checksum_guardado and checksum_actual:
                            return checksum_guardado == checksum_actual
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al verificar integridad: {e}")
            return False
    
    def limpiar_respaldos_antiguos(self):
        """Limpiar respaldos antiguos según la configuración"""
        try:
            # Limpiar respaldos diarios
            if self.config["retener_diarios"] > 0:
                self.limpiar_por_tipo("diario", self.config["retener_diarios"])
            
            # Limpiar respaldos semanales
            if self.config["retener_semanales"] > 0:
                self.limpiar_por_tipo("semanal", self.config["retener_semanales"])
            
            # Limpiar respaldos mensuales
            if self.config["retener_mensuales"] > 0:
                self.limpiar_por_tipo("mensual", self.config["retener_mensuales"])
                
        except Exception as e:
            logger.error(f"❌ Error al limpiar respaldos antiguos: {e}")
    
    def limpiar_por_tipo(self, tipo, dias_retener):
        """Limpiar respaldos de un tipo específico"""
        directorio = os.path.join(self.config["directorio_respaldo"], tipo)
        if not os.path.exists(directorio):
            return
            
        fecha_limite = datetime.now() - timedelta(days=dias_retener)
        
        for archivo in os.listdir(directorio):
            ruta_archivo = os.path.join(directorio, archivo)
            if os.path.isfile(ruta_archivo):
                fecha_archivo = datetime.fromtimestamp(os.path.getctime(ruta_archivo))
                if fecha_archivo < fecha_limite:
                    os.remove(ruta_archivo)
                    logger.info(f"🗑️ Eliminado respaldo antiguo: {archivo}")
    
    def copiar_a_dispositivo_usb(self, ruta_respaldo):
        """
        Copiar respaldo a dispositivo USB
        
        Args:
            ruta_respaldo (str): Ruta del archivo de respaldo
            
        Returns:
            bool: True si se copió exitosamente
        """
        try:
            # Buscar dispositivos USB disponibles
            dispositivos_usb = self.detectar_dispositivos_usb()
            
            if not dispositivos_usb:
                logger.warning("⚠️ No se detectaron dispositivos USB")
                return False
            
            # Usar el primer dispositivo USB disponible
            dispositivo_destino = dispositivos_usb[0]
            nombre_archivo = os.path.basename(ruta_respaldo)
            ruta_destino = os.path.join(dispositivo_destino, "RESPALDOS_ZKTECO", nombre_archivo)
            
            # Crear directorio de respaldos en USB si no existe
            os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
            
            # Copiar archivo
            shutil.copy2(ruta_respaldo, ruta_destino)
            
            logger.info(f"✅ Respaldo copiado a USB: {ruta_destino}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al copiar a USB: {e}")
            return False
    
    def detectar_dispositivos_usb(self):
        """
        Detectar dispositivos USB disponibles
        
        Returns:
            list: Lista de rutas de dispositivos USB
        """
        dispositivos = []
        
        try:
            # En Windows, buscar unidades de disco removibles
            import string
            for letra in string.ascii_uppercase:
                ruta_unidad = f"{letra}:\\"
                if os.path.exists(ruta_unidad):
                    try:
                        # Verificar si es un dispositivo removible
                        if os.path.ismount(ruta_unidad):
                            dispositivos.append(ruta_unidad)
                    except:
                        pass
        except Exception as e:
            logger.error(f"Error al detectar dispositivos USB: {e}")
        
        return dispositivos
    
    def iniciar_respaldo_automatico(self):
        """Iniciar respaldo automático en segundo plano"""
        def respaldo_automatico():
            while True:
                try:
                    hora_actual = datetime.now().strftime("%H:%M")
                    if hora_actual == self.config["hora_respaldo_automatico"]:
                        logger.info("🔄 Iniciando respaldo automático...")
                        
                        # Crear respaldo diario
                        if self.config["respaldo_diario"]:
                            self.respaldo_base_datos("incremental")
                        
                        # Crear respaldo semanal (domingos)
                        if self.config["respaldo_semanal"] and datetime.now().weekday() == 6:
                            self.respaldo_base_datos("completo")
                        
                        # Crear respaldo mensual (primer día del mes)
                        if self.config["respaldo_mensual"] and datetime.now().day == 1:
                            self.crear_respaldo_completo()
                        
                        # Limpiar respaldos antiguos
                        self.limpiar_respaldos_antiguos()
                        
                        logger.info("✅ Respaldo automático completado")
                        
                        # Esperar 24 horas antes del siguiente ciclo
                        time.sleep(86400)  # 24 horas
                    else:
                        # Verificar cada minuto
                        time.sleep(60)
                        
                except Exception as e:
                    logger.error(f"❌ Error en respaldo automático: {e}")
                    time.sleep(300)  # Esperar 5 minutos antes de reintentar
        
        # Iniciar en hilo separado
        thread = threading.Thread(target=respaldo_automatico, daemon=True)
        thread.start()
        logger.info("🔄 Respaldo automático iniciado")

class InterfazRespaldo(tk.Toplevel):
    """Interfaz gráfica para gestión de respaldos"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.sistema_respaldo = SistemaRespaldo()
        
        self.title("Sistema de Respaldo - Sistema QUIRA")
        self.geometry("600x500")
        self.configure(bg='#f8f9fa')
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        # Frame principal
        main_frame = tk.Frame(self, bg='#f8f9fa')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Título
        titulo = tk.Label(main_frame, text="Sistema de Respaldo Local", 
                         font=('Segoe UI', 16, 'bold'), 
                         fg='#2c3e50', bg='#f8f9fa')
        titulo.pack(pady=(0, 20))
        
        # Frame de botones
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(fill='x', pady=10)
        
        # Botones principales
        tk.Button(button_frame, text="🔄 Respaldo Rápido (BD)", 
                 command=self.respaldo_rapido,
                 font=('Segoe UI', 11), bg='#28a745', fg='white',
                 relief='flat', padx=20, pady=10).pack(fill='x', pady=5)
        
        tk.Button(button_frame, text="💾 Respaldo Completo", 
                 command=self.respaldo_completo,
                 font=('Segoe UI', 11), bg='#007bff', fg='white',
                 relief='flat', padx=20, pady=10).pack(fill='x', pady=5)
        
        tk.Button(button_frame, text="📱 Copiar a USB", 
                 command=self.copiar_usb,
                 font=('Segoe UI', 11), bg='#ffc107', fg='black',
                 relief='flat', padx=20, pady=10).pack(fill='x', pady=5)
        
        tk.Button(button_frame, text="⚙️ Configuración", 
                 command=self.configuracion,
                 font=('Segoe UI', 11), bg='#6c757d', fg='white',
                 relief='flat', padx=20, pady=10).pack(fill='x', pady=5)
        
        # Área de logs
        log_frame = tk.Frame(main_frame, bg='#f8f9fa')
        log_frame.pack(fill='both', expand=True, pady=10)
        
        tk.Label(log_frame, text="Logs del Sistema:", 
                font=('Segoe UI', 12, 'bold'), 
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w')
        
        self.log_text = tk.Text(log_frame, height=10, font=('Consolas', 9),
                               bg='#ffffff', fg='#2c3e50')
        self.log_text.pack(fill='both', expand=True)
        
        # Scrollbar para logs
        scrollbar = tk.Scrollbar(log_frame, orient='vertical', command=self.log_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.log_text.configure(yscrollcommand=scrollbar.set)
    
    def respaldo_rapido(self):
        """Crear respaldo rápido de la base de datos"""
        self.log("🔄 Iniciando respaldo rápido...")
        
        def ejecutar_respaldo():
            resultado = self.sistema_respaldo.respaldo_base_datos("incremental")
            if resultado:
                self.log(f"✅ Respaldo rápido completado: {os.path.basename(resultado)}")
                messagebox.showinfo("Éxito", "Respaldo rápido completado exitosamente")
            else:
                self.log("❌ Error en respaldo rápido")
                messagebox.showerror("Error", "No se pudo crear el respaldo rápido")
        
        threading.Thread(target=ejecutar_respaldo, daemon=True).start()
    
    def respaldo_completo(self):
        """Crear respaldo completo del sistema"""
        self.log("🔄 Iniciando respaldo completo...")
        
        def ejecutar_respaldo():
            resultado = self.sistema_respaldo.crear_respaldo_completo()
            if resultado:
                self.log(f"✅ Respaldo completo completado: {os.path.basename(resultado['ruta'])}")
                self.log(f"   Tamaño: {resultado['tamaño'] / 1024 / 1024:.2f} MB")
                messagebox.showinfo("Éxito", "Respaldo completo completado exitosamente")
            else:
                self.log("❌ Error en respaldo completo")
                messagebox.showerror("Error", "No se pudo crear el respaldo completo")
        
        threading.Thread(target=ejecutar_respaldo, daemon=True).start()
    
    def copiar_usb(self):
        """Copiar respaldo a dispositivo USB"""
        self.log("📱 Buscando dispositivos USB...")
        
        dispositivos = self.sistema_respaldo.detectar_dispositivos_usb()
        if not dispositivos:
            messagebox.showwarning("Advertencia", "No se detectaron dispositivos USB")
            return
        
        # Buscar el respaldo más reciente
        directorio_respaldo = self.sistema_respaldo.config["directorio_respaldo"]
        respaldos = []
        
        for root, dirs, files in os.walk(directorio_respaldo):
            for file in files:
                if file.endswith(('.sql', '.zip', '.gz')):
                    ruta_completa = os.path.join(root, file)
                    respaldos.append((ruta_completa, os.path.getctime(ruta_completa)))
        
        if not respaldos:
            messagebox.showwarning("Advertencia", "No se encontraron respaldos para copiar")
            return
        
        # Ordenar por fecha de creación (más reciente primero)
        respaldos.sort(key=lambda x: x[1], reverse=True)
        respaldo_mas_reciente = respaldos[0][0]
        
        self.log(f"📱 Copiando a USB: {os.path.basename(respaldo_mas_reciente)}")
        
        def ejecutar_copia():
            if self.sistema_respaldo.copiar_a_dispositivo_usb(respaldo_mas_reciente):
                self.log("✅ Respaldo copiado a USB exitosamente")
                messagebox.showinfo("Éxito", "Respaldo copiado a USB exitosamente")
            else:
                self.log("❌ Error al copiar a USB")
                messagebox.showerror("Error", "No se pudo copiar el respaldo a USB")
        
        threading.Thread(target=ejecutar_copia, daemon=True).start()
    
    def configuracion(self):
        """Abrir configuración del sistema de respaldo"""
        messagebox.showinfo("Configuración", 
                           "La configuración se encuentra en el archivo 'config_respaldo.json'\n\n"
                           "Puedes editar manualmente este archivo para personalizar:\n"
                           "- Frecuencia de respaldos\n"
                           "- Retención de archivos\n"
                           "- Compresión de archivos\n"
                           "- Verificación de integridad")
    
    def log(self, mensaje):
        """Agregar mensaje al log de la interfaz"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert('end', f"[{timestamp}] {mensaje}\n")
        self.log_text.see('end')
        self.update_idletasks()

def main():
    """Función principal para probar el sistema de respaldo"""
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    app = InterfazRespaldo(root)
    app.mainloop()

if __name__ == "__main__":
    main()

