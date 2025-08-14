# Solución para Ventanas CMD y Errores de Codificación

## Problemas Identificados

### 1. Ventanas CMD
Después de compilar el programa con PyInstaller, se abrían ventanas CMD brevemente al ejecutar ciertas funciones como "Agregar Postulante".

### 2. Error de Codificación Unicode
Error `UnicodeEncodeError: 'charmap' codec can't encode character '\u2705'` causado por el uso de emojis en los mensajes de print().

## Causas

### Ventanas CMD
Las ventanas CMD aparecían debido a llamadas a subprocesos (`subprocess.run`, `subprocess.Popen`, `os.system`, etc.) que no estaban configuradas para ejecutarse de forma silenciosa.

### Error de Codificación
Los emojis Unicode (✅, ⚠️, etc.) no pueden ser codificados por el codec `cp1252` (charmap) de Windows cuando se ejecuta desde PyInstaller.

## Solución Implementada

### 1. Silent Wrapper (`silent_wrapper.py`)
Se creó un wrapper que intercepta todas las llamadas a subprocesos y las ejecuta de forma silenciosa:

- **subprocess.run**: Reemplazado con versión silenciosa
- **subprocess.Popen**: Reemplazado con versión silenciosa  
- **subprocess.call**: Reemplazado con versión silenciosa
- **os.system**: Reemplazado con versión silenciosa
- **os.popen**: Reemplazado con versión silenciosa

### 2. Integración en Main (`main_integrado.py`)
Se modificó el punto de entrada principal para importar `silent_wrapper` al inicio:

```python
# Importar silent_wrapper PRIMERO para evitar ventanas CMD
try:
    import silent_wrapper
    print("✅ Silent wrapper cargado correctamente")
except ImportError:
    print("⚠️ No se pudo cargar silent_wrapper")
```

### 3. Eliminación de Emojis
Se reemplazaron todos los emojis Unicode con texto simple:
- ✅ → `[OK]`
- ⚠️ → `[WARN]`
- ❌ → `[ERROR]`
- 🚀 → `[INIT]`
- 📦 → `[DEPS]`
- etc.

### 4. Scripts de Compilación Actualizados
Se crearon scripts que incluyen `silent_wrapper` como import oculto:

```bash
# Script básico
python compilar_silencioso_final.py

# Script con UTF-8 (recomendado)
python compilar_silencioso_utf8.py
```

## Características del Silent Wrapper

### Configuración Automática
- `CREATE_NO_WINDOW`: Evita que se creen ventanas CMD
- `STARTUPINFO`: Configura las ventanas para que no se muestren
- `stdout/stderr`: Redirige la salida a `DEVNULL`

### Compatibilidad
- Funciona en Windows 10/11 y versiones anteriores
- Compatible con PyInstaller
- No afecta la funcionalidad del programa

## Uso

### Compilación
```bash
# Script básico (recomendado para la mayoría de casos)
python compilar_silencioso_final.py

# Script con UTF-8 (recomendado si hay problemas de codificación)
python compilar_silencioso_utf8.py
```

### Verificación
Después de compilar, ejecutar el programa y verificar que:
- No aparezcan ventanas CMD al usar funciones
- El programa funcione normalmente
- Los logs muestren "[OK] Silent wrapper cargado correctamente"

## Archivos Modificados

1. **main_integrado.py**: 
   - Agregada importación de silent_wrapper
   - Reemplazados todos los emojis con texto simple
2. **silent_wrapper.py**: Creado wrapper completo para subprocesos
3. **compilar_silencioso_final.py**: Script de compilación básico
4. **compilar_silencioso_utf8.py**: Script de compilación con UTF-8

## Notas Técnicas

- El wrapper se carga al inicio del programa
- Intercepta todas las llamadas a subprocesos automáticamente
- Mantiene la funcionalidad original pero sin ventanas visibles
- Compatible con todas las funciones del sistema QUIRA
