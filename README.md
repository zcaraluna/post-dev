# ZKTeco K40 - Gestor de Dispositivos Biométricos

Esta aplicación te permite conectar y gestionar dispositivos biométricos ZKTeco modelo K40 a través de conexión Ethernet.

## Características

- ✅ Conexión directa con dispositivos ZKTeco K40
- 📊 Visualización de información del dispositivo
- 👥 Gestión de usuarios registrados
- 📝 Registros de asistencia
- 🖥️ Interfaz gráfica moderna y minimalista
- 💻 Script de línea de comandos para uso rápido

## Requisitos

- Python 3.7 o superior
- Conexión Ethernet con el dispositivo
- Dispositivo ZKTeco K40 encendido y configurado

## Instalación

### Opción 1: Entorno Virtual (Recomendado)

1. **Crear y activar entorno virtual**
   ```bash
   # Crear entorno virtual
   python -m venv zkteco_env
   
   # Activar en Windows (PowerShell)
   .\zkteco_env\Scripts\Activate.ps1
   
   # O usar el script de activación
   .\activar_entorno.ps1
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

### Opción 2: Instalación Directa

1. **Clonar o descargar el proyecto**
   ```bash
   git clone <url-del-repositorio>
   cd POSTULANTES
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

### Scripts de Activación

Para facilitar el uso, se incluyen scripts de activación:

- **Windows (PowerShell)**: `activar_entorno.ps1`
- **Windows (CMD)**: `activar_entorno.bat`

Simplemente ejecuta uno de estos scripts para activar el entorno virtual automáticamente.

## Configuración del Dispositivo

Antes de usar la aplicación, asegúrate de que tu dispositivo ZKTeco K40 esté configurado correctamente:

1. **Configuración de red:**
   - Conecta el dispositivo por cable Ethernet
   - Configura una dirección IP estática (ej: 192.168.1.100)
   - Puerto por defecto: 4370

2. **Verificar conectividad:**
   ```bash
   ping 192.168.1.100
   ```

## Uso

### Interfaz Gráfica

Para usar la interfaz gráfica completa:

```bash
python gui_app.py
```

**Características de la interfaz:**
- Configuración de conexión (IP y puerto)
- Información del dispositivo en tiempo real
- Lista de usuarios con detalles
- Registros de asistencia filtrables por fecha
- Estado de conexión visual

### Script de Línea de Comandos

Para uso rápido desde terminal:

```bash
# Ver información básica
python simple_connector.py 192.168.1.100

# Ver lista de usuarios
python simple_connector.py 192.168.1.100 --users

# Ver registros de asistencia
python simple_connector.py 192.168.1.100 --logs

# Ver información del dispositivo
python simple_connector.py 192.168.1.100 --info

# Ver todo
python simple_connector.py 192.168.1.100 --users --logs --info
```

### Uso Programático

Para usar en tus propios scripts:

```python
from zkteco_connector import ZKTecoK40

# Conectar al dispositivo
device = ZKTecoK40("192.168.1.100", 4370)

if device.connect():
    try:
        # Obtener información del dispositivo
        info = device.get_device_info()
        print(f"Dispositivo: {info['device_name']}")
        
        # Obtener cantidad de usuarios
        user_count = device.get_user_count()
        print(f"Usuarios registrados: {user_count}")
        
        # Obtener lista de usuarios
        users = device.get_user_list(0, 10)
        for user in users:
            print(f"ID: {user['user_id']}, Nombre: {user['name']}")
        
        # Obtener registros de asistencia
        logs = device.get_attendance_logs()
        print(f"Registros de asistencia: {len(logs)}")
        
    finally:
        device.disconnect()
```

## Estructura del Proyecto

```
POSTULANTES/
├── zkteco_connector.py    # Módulo principal de conexión
├── gui_app.py            # Interfaz gráfica
├── simple_connector.py   # Script de línea de comandos
├── requirements.txt      # Dependencias
└── README.md            # Este archivo
```

## Funciones Disponibles

### ZKTecoK40 Class

- `connect()` - Establecer conexión con el dispositivo
- `disconnect()` - Cerrar conexión
- `get_device_info()` - Obtener información del dispositivo
- `get_user_count()` - Obtener cantidad de usuarios
- `get_user_list(start_index, count)` - Obtener lista de usuarios
- `get_attendance_logs(start_date, end_date)` - Obtener registros de asistencia

### Información de Usuarios

Cada usuario contiene:
- `user_id` - ID único del usuario
- `name` - Nombre del usuario
- `password` - Contraseña (si existe)
- `role` - Rol del usuario
- `group` - Grupo del usuario
- `card_number` - Número de tarjeta
- `fingerprint_count` - Cantidad de huellas registradas
- `face_count` - Cantidad de rostros registrados
- `status` - Estado del usuario (1=Activo, 0=Inactivo)

### Registros de Asistencia

Cada registro contiene:
- `user_id` - ID del usuario
- `timestamp` - Fecha y hora del registro
- `status` - Tipo de registro (1=Entrada, 0=Salida)
- `verification_type` - Método de verificación (0=Contraseña, 1=Huella, 2=Tarjeta, 3=Rostro)

## Solución de Problemas

### Error de Conexión

Si no puedes conectar al dispositivo:

1. **Verificar conectividad de red:**
   ```bash
   ping [IP_DEL_DISPOSITIVO]
   ```

2. **Verificar puerto:**
   ```bash
   telnet [IP_DEL_DISPOSITIVO] 4370
   ```

3. **Verificar configuración del dispositivo:**
   - Asegúrate de que el dispositivo esté encendido
   - Verifica que la IP configurada sea correcta
   - Confirma que el puerto 4370 esté abierto

### Errores Comunes

- **"No se pudo conectar"**: Verifica la IP y que el dispositivo esté encendido
- **"Timeout"**: El dispositivo no responde, verifica la conectividad de red
- **"Checksum incorrecto"**: Error en la comunicación, intenta reconectar

## Notas Técnicas

- **Protocolo**: La aplicación usa el protocolo UDP nativo de ZKTeco
- **Puerto por defecto**: 4370
- **Timeout**: 5 segundos por defecto
- **Codificación**: UTF-8 para nombres y texto

## Contribuir

Si encuentras algún problema o quieres agregar funcionalidades:

1. Reporta el problema en los issues
2. Propón mejoras con pull requests
3. Documenta cualquier cambio importante

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## Soporte

Para soporte técnico o preguntas:
- Revisa la documentación
- Consulta los issues existentes
- Crea un nuevo issue si es necesario

---

**Nota**: Esta aplicación está diseñada específicamente para dispositivos ZKTeco modelo K40. Para otros modelos, puede requerir modificaciones en el protocolo de comunicación. 