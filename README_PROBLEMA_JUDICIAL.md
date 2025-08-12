# Sistema de Verificación de Cédulas con Problemas Judiciales

## Descripción

Esta funcionalidad permite verificar automáticamente si un postulante tiene problemas judiciales antes de registrarlo en el sistema. El sistema compara la cédula del postulante contra una base de datos previamente cargada con cédulas que tienen órdenes de captura judicial u otros problemas.

## Características

- ✅ **Verificación automática**: Al agregar un postulante, se verifica automáticamente si su cédula está en la lista de problemas judiciales
- ✅ **Carga masiva**: Permite cargar miles de cédulas desde un archivo CSV
- ✅ **Advertencia visual**: Muestra una advertencia clara cuando se detecta un problema judicial
- ✅ **Gestión de duplicados**: Evita cédulas duplicadas en la base de datos
- ✅ **Interfaz intuitiva**: Fácil de usar con vista previa de datos

## Cómo usar

### 1. Cargar Cédulas con Problemas Judiciales

1. **Acceder al menú**: Como SUPERADMIN, ve a `Sistema → Cargar Cédulas Problema Judicial`

2. **Preparar archivo CSV**: 
   - Formato: Una cédula por línea
   - Puede tener encabezado "cedula" o solo números
   - Solo cédulas numéricas válidas

3. **Cargar archivo**:
   - Hacer clic en "Seleccionar Archivo CSV"
   - Revisar la vista previa
   - Hacer clic en "Cargar Cédulas"

### 2. Verificación Automática

Cuando agregues un postulante:

- **Sin problemas**: Mensaje normal de éxito
- **Con problemas**: Mensaje de advertencia con alerta visual

## Estructura de la Base de Datos

```sql
CREATE TABLE cedulas_problema_judicial (
    id SERIAL PRIMARY KEY,
    cedula VARCHAR(20) UNIQUE NOT NULL
);
```

## Archivos Modificados

### Base de Datos
- `database.py`: 
  - Nueva función `verificar_cedula_problema_judicial()`
  - Modificada función `agregar_postulante()` para incluir verificación
  - Nueva tabla `cedulas_problema_judicial`

### Interfaz
- `agregar_postulante.py`: Modificado para mostrar advertencias
- `menu_principal.py`: Agregada opción en menú Sistema
- `cargar_cedulas_problema_judicial.py`: Nueva interfaz para cargar cédulas

## Ejemplo de Uso

### Archivo CSV de ejemplo:
```csv
cedula
12345678
87654321
11111111
```

### Flujo de trabajo:
1. Cargar cédulas con problemas judiciales
2. Al agregar postulante con cédula 12345678
3. Sistema muestra: "⚠️ ADVERTENCIA: Este postulante tiene problemas judiciales"

## Ventajas

- **Seguridad**: Previene registro de personas con problemas judiciales
- **Eficiencia**: Verificación automática sin intervención manual
- **Escalabilidad**: Maneja miles de cédulas sin problemas
- **Flexibilidad**: Fácil actualización de la lista de cédulas

## Notas Importantes

- Solo usuarios SUPERADMIN pueden cargar cédulas con problemas judiciales
- La verificación es automática al agregar postulantes
- Las cédulas duplicadas se ignoran automáticamente
- Se puede limpiar toda la base de datos de cédulas si es necesario

## Soporte

Para problemas o preguntas sobre esta funcionalidad, contactar al administrador del sistema.
