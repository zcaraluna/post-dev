# Sistema QUIRA

Sistema QUIRA - Solución completa que integra la gestión de dispositivos biométricos ZKTeco K40 con un sistema de gestión de postulantes para criminalística.

## 🚀 Características

### ✅ **Gestión de Dispositivos ZKTeco K40**
- Conexión directa con dispositivos ZKTeco K40
- Visualización de información del dispositivo
- Gestión de usuarios registrados en el dispositivo
- Registros de asistencia en tiempo real
- Sincronización con base de datos

### ✅ **Sistema de Gestión de Postulantes**
- Sistema de login con roles y permisos
- Gestión de usuarios del sistema
- Registro de postulantes
- Búsqueda y listado de postulantes
- Estadísticas del sistema

### ✅ **Base de Datos PostgreSQL**
- Almacenamiento seguro de datos
- Encriptación de contraseñas con bcrypt
- Gestión de roles y permisos
- Integración con dispositivos biométricos

## 📋 Requisitos

### **Software Requerido:**
- Python 3.7 o superior
- PostgreSQL 12 o superior
- Dispositivo ZKTeco K40 (opcional)

### **Dependencias Python:**
```
pyzk==0.9.0
tkinter-tooltip==2.0.0
Pillow>=10.1.0
psycopg2-binary==2.9.10
bcrypt==4.3.0
```

## 🛠️ Instalación

### **1. Clonar o Descargar el Proyecto**
```bash
git clone <url-del-repositorio>
cd POSTULANTES
```

### **2. Crear Entorno Virtual**
```bash
# Crear entorno virtual
python -m venv zkteco_env

# Activar en Windows (PowerShell)
.\zkteco_env\Scripts\Activate.ps1

# O usar el script de activación
.\activar_entorno.ps1
```

### **3. Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### **4. Configurar Base de Datos PostgreSQL**

#### **Opción A: Configuración Automática**
```bash
python setup_database.py
```
Este script te guiará para:
- Verificar instalación de PostgreSQL
- Configurar conexión a la base de datos
- Crear la base de datos `sistema_postulantes`
- Inicializar las tablas del sistema

#### **Opción B: Configuración Manual**
1. **Instalar PostgreSQL** desde https://www.postgresql.org/download/
2. **Crear base de datos:**
   ```sql
   CREATE DATABASE sistema_postulantes;
   ```
3. **Configurar usuario** (si es necesario):
   ```sql
   ALTER USER postgres PASSWORD 'tu_contraseña';
   ```

### **5. Configurar Dispositivo ZKTeco K40**
1. Conectar el dispositivo por cable Ethernet
2. Configurar IP estática (ej: 192.168.100.201)
3. Puerto UDP: 4370
4. Verificar conectividad con `ping 192.168.100.201`

## 🚀 Uso del Sistema

### **Iniciar el Sistema**
```bash
# Activar entorno virtual
.\activar_entorno.ps1

# Ejecutar sistema principal
python main_integrado.py
```

### **Credenciales por Defecto**
- **Usuario:** `admin`
- **Contraseña:** `admin123`

**⚠️ Importante:** Cambie la contraseña en el primer inicio.

## 📱 Funcionalidades del Sistema

### **🔐 Sistema de Autenticación**
- Login seguro con encriptación bcrypt
- Gestión de roles (SUPERADMIN, ADMIN, USUARIO)
- Cambio de contraseña obligatorio en primer inicio
- Sesiones seguras

### **👥 Gestión de Usuarios**
- Crear, modificar y eliminar usuarios
- Asignación de roles y permisos
- Información personal completa
- Credenciales y contactos

### **📋 Gestión de Postulantes**
- Registro de postulantes con datos completos
- Búsqueda por cédula o nombre
- Listado con filtros y paginación
- Integración con dispositivo biométrico

### **📱 Gestión ZKTeco K40**
- Conexión directa al dispositivo
- Visualización de información del dispositivo
- Lista de usuarios registrados
- Registros de asistencia en tiempo real
- Sincronización con base de datos

### **📊 Estadísticas y Reportes**
- Estadísticas de postulantes
- Reportes de asistencia
- Informes del dispositivo
- Métricas del sistema

## 🗂️ Estructura del Proyecto

```
POSTULANTES/
├── main_integrado.py          # Punto de entrada principal
├── database.py               # Módulo de base de datos
├── login_system.py           # Sistema de autenticación
├── menu_principal.py         # Menú principal
├── zkteco_connector_v2.py    # Conector ZKTeco mejorado
├── gui_app_v2.py            # Interfaz ZKTeco
├── simple_connector_v2.py    # CLI ZKTeco
├── setup_database.py         # Configuración de BD
├── requirements.txt          # Dependencias
├── activar_entorno.ps1       # Script de activación
├── activar_entorno.bat       # Script de activación (CMD)
└── README_INTEGRADO.md       # Esta documentación
```

## 🔧 Configuración Avanzada

### **Configurar IP del Dispositivo ZKTeco**
Editar `main_integrado.py` línea 45:
```python
if test_connection("TU_IP_AQUI", 4370):
```

### **Configurar Base de Datos**
Editar `database.py` función `connect_db()`:
```python
conn = psycopg2.connect(
    dbname="sistema_postulantes",
    user="tu_usuario",
    password="tu_contraseña",
    host="localhost",
    port="5432"
)
```

## 🚨 Solución de Problemas

### **Error de Conexión a PostgreSQL**
1. Verificar que PostgreSQL esté ejecutándose
2. Verificar credenciales de conexión
3. Ejecutar `python setup_database.py`

### **Error de Conexión ZKTeco**
1. Verificar IP del dispositivo
2. Verificar conectividad de red
3. Verificar configuración del dispositivo

### **Error de Dependencias**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 📞 Soporte

Para soporte técnico:
1. Revisar la documentación
2. Verificar logs del sistema
3. Ejecutar scripts de diagnóstico
4. Contactar al administrador del sistema

## 🔒 Seguridad

- Contraseñas encriptadas con bcrypt
- Validación de entrada de datos
- Gestión de sesiones seguras
- Roles y permisos granulares
- Logs de auditoría

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

**🎉 ¡El sistema está listo para usar!**

Para comenzar, ejecute:
```bash
.\activar_entorno.ps1
python main_integrado.py
``` 