# Instrucciones para Compilar Ejecutable Silencioso

## Problema
El ejecutable compilado con PyInstaller abre ventanas CMD cuando se presionan los botones "Agregar postulante" y "Control de Asistencias".

## Solución

### 1. Usar el Script de Compilación Simple (Recomendado)
```bash
python compilar_simple.py
```

### 2. Usar el Script de Compilación Automática
```bash
python build_silent_exe.py
```

### 2. Compilación Manual con PyInstaller
```bash
pyinstaller --onefile --windowed --noconsole --disable-windowed-traceback --name=Sistema_Postulantes --icon=quira.ico --add-data="quiraXXXL.png;." --add-data="quira.png;." --add-data="instituto.png;." --add-data="quiraXXL.png;." --add-data="quira_bigger.png;." --hidden-import=zkteco_connector_v2 --hidden-import=gestion_zkteco --hidden-import=privilegios_utils --hidden-import=gestion_privilegios --hidden-import=login_system --hidden-import=icon_utils --hidden-import=zk --hidden-import=subprocess --hidden-import=socket --exclude-module=tkinter.test --exclude-module=unittest --exclude-module=test --exclude-module=distutils main_integrado.py
```

### 3. Usar el Archivo .spec Modificado
```bash
pyinstaller Sistema_Postulantes.spec
```

## Archivos de Configuración Creados

### 1. `pyinstaller_config.py`
- Configuración de entorno para PyInstaller
- Variables de entorno para evitar ventanas CMD

### 2. `hook-zk.py`
- Hook personalizado para la biblioteca zk
- Maneja correctamente las dependencias de pyzk

### 3. `hook-subprocess.py`
- Hook personalizado para subprocess
- Evita problemas con subprocess en PyInstaller

### 4. `compilar_simple.py`
- Script simple para compilar sin conflictos
- Configuración básica pero efectiva

### 5. `build_silent_exe.py`
- Script automatizado para compilar
- Incluye todas las configuraciones necesarias

## Modificaciones Realizadas

### 1. `main_integrado.py`
- Detección de ejecutable PyInstaller
- Configuración de entorno silencioso
- Redirección de stdout/stderr

### 2. `zkteco_connector_v2.py`
- Configuración específica para ejecutables
- Redirección temporal de salida
- Variables de entorno para PyInstaller

### 3. `Sistema_Postulantes.spec`
- `disable_windowed_traceback=True`
- Hooks personalizados incluidos
- Módulos problemáticos excluidos

## Verificación

Después de compilar, el ejecutable debe:
- ✅ No abrir ventanas CMD al presionar "Agregar postulante"
- ✅ No abrir ventanas CMD al presionar "Control de Asistencias"
- ✅ Funcionar correctamente sin mostrar consolas
- ✅ Mantener todas las funcionalidades del sistema

## Notas Importantes

1. **Siempre usar `--windowed` o `--noconsole`** en PyInstaller
2. **Incluir `--disable-windowed-traceback`** para evitar ventanas de error
3. **Usar los hooks personalizados** para manejar bibliotecas problemáticas
4. **Excluir módulos de prueba** que pueden causar problemas
5. **Configurar variables de entorno** para PyInstaller
