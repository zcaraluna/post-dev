# Sistema de Respaldo Local - Sistema QUIRA

## 🛡️ Método de Respaldo Recomendado para Entornos Sin Internet

Este sistema de respaldo está diseñado específicamente para funcionar en entornos sin conexión a internet, garantizando la seguridad y disponibilidad de los datos críticos del sistema.

## 📋 Características Principales

### ✅ **Respaldo Local Automático**
- **Respaldo diario incremental**: Solo los cambios del día
- **Respaldo semanal completo**: Base de datos completa
- **Respaldo mensual integral**: Todo el sistema + ZKTeco + logs

### ✅ **Múltiples Dispositivos de Almacenamiento**
- **Disco duro local**: Respaldos automáticos
- **Dispositivos USB**: Copia manual/automática
- **Discos externos**: Respaldo adicional

### ✅ **Verificación de Integridad**
- Checksums MD5 para verificar archivos
- Validación de archivos ZIP
- Logs detallados de todas las operaciones

### ✅ **Compresión Inteligente**
- Compresión automática de archivos grandes
- Ahorro de hasta 70% en espacio de almacenamiento
- Formato estándar (.gz, .zip)

## 🗂️ Estructura de Respaldos

```
/backups/
├── diario/                    # Respaldos incrementales diarios
│   ├── 2025-01-15_14-30-00_bd_incremental_2025-01-15_14-30-00.sql.gz
│   └── 2025-01-16_14-30-00_bd_incremental_2025-01-16_14-30-00.sql.gz
├── semanal/                   # Respaldos completos semanales
│   ├── 2025-01-12_bd_completo_2025-01-12_14-30-00.sql.gz
│   └── 2025-01-19_bd_completo_2025-01-19_14-30-00.sql.gz
├── mensual/                   # Respaldos integrales mensuales
│   └── respaldo_completo_2025-01-01_14-30-00.zip
├── logs/                      # Respaldos de logs del sistema
│   └── logs_2025-01-15_14-30-00.zip
└── zkteco/                    # Respaldos del dispositivo ZKTeco
    └── zkteco_2025-01-15_14-30-00.json
```

## 🚀 Cómo Usar el Sistema

### 1. **Acceso desde el Menú Principal**
1. Iniciar sesión como SUPERADMIN
2. Ir a **Sistema → Configuración del Sistema**
3. Se abrirá la interfaz de respaldo

### 2. **Respaldo Rápido (Recomendado para uso diario)**
- **Propósito**: Respaldo rápido de solo la base de datos
- **Tiempo**: 30 segundos - 2 minutos
- **Tamaño**: 1-10 MB (comprimido)
- **Frecuencia**: Diaria

### 3. **Respaldo Completo (Recomendado semanal)**
- **Propósito**: Respaldo completo del sistema
- **Incluye**: BD + ZKTeco + Logs + Configuración
- **Tiempo**: 5-15 minutos
- **Tamaño**: 50-200 MB (comprimido)
- **Frecuencia**: Semanal

### 4. **Copia a USB (Recomendado para portabilidad)**
- **Propósito**: Llevar respaldo a otro lugar
- **Requisito**: Dispositivo USB conectado
- **Tiempo**: 1-5 minutos (depende del tamaño)
- **Frecuencia**: Según necesidad

## ⚙️ Configuración Automática

El sistema se configura automáticamente con valores óptimos:

```json
{
    "directorio_respaldo": "./backups",
    "respaldo_diario": true,
    "respaldo_semanal": true,
    "respaldo_mensual": true,
    "retener_diarios": 7,        // Mantener 7 días
    "retener_semanales": 4,      // Mantener 4 semanas
    "retener_mensuales": 12,     // Mantener 12 meses
    "comprimir_respaldos": true,
    "verificar_integridad": true,
    "incluir_zkteco": true,
    "incluir_logs": true,
    "hora_respaldo_automatico": "14:30"
}
```

## 🔄 Respaldo Automático

El sistema incluye un respaldo automático que se ejecuta en segundo plano:

- **Diario**: A las 14:30 (respaldo incremental)
- **Semanal**: Domingos a las 14:30 (respaldo completo)
- **Mensual**: Primer día del mes a las 14:30 (respaldo integral)

## 📱 Dispositivos USB Recomendados

### **Opciones por Capacidad:**

| Capacidad | Uso Recomendado | Precio Aproximado |
|-----------|-----------------|-------------------|
| 8 GB      | Respaldo diario | $5-10 USD        |
| 16 GB     | Respaldo semanal | $8-15 USD        |
| 32 GB     | Respaldo mensual | $12-20 USD       |
| 64 GB     | Múltiples respaldos | $20-30 USD    |
| 128 GB    | Respaldo completo + histórico | $35-50 USD |

### **Recomendaciones Específicas:**

1. **USB 3.0/3.1** para mayor velocidad
2. **Marcas confiables**: SanDisk, Kingston, Samsung
3. **Dedicar exclusivamente** para respaldos
4. **Rotar múltiples dispositivos** para mayor seguridad

## 🛠️ Recuperación de Datos

### **Recuperar Base de Datos:**
```bash
# Descomprimir si es necesario
gunzip backup_file.sql.gz

# Restaurar en PostgreSQL
psql -h localhost -U postgres -d sistema_postulantes -f backup_file.sql
```

### **Recuperar desde USB:**
1. Conectar dispositivo USB
2. Copiar archivo de respaldo al directorio local
3. Usar herramienta de restauración del sistema

## 📊 Monitoreo y Mantenimiento

### **Verificar Estado del Sistema:**
- Revisar logs en la interfaz de respaldo
- Verificar espacio disponible en disco
- Comprobar integridad de respaldos recientes

### **Limpieza Automática:**
- Respaldos diarios: Se eliminan después de 7 días
- Respaldos semanales: Se eliminan después de 4 semanas
- Respaldos mensuales: Se eliminan después de 12 meses

### **Alertas Recomendadas:**
- Espacio en disco < 1 GB
- Error en respaldo automático
- Dispositivo USB no detectado
- Verificación de integridad fallida

## 🔒 Seguridad

### **Protección de Datos:**
- Respaldos en formato comprimido
- Verificación de integridad con checksums
- Logs detallados de todas las operaciones
- Acceso restringido a SUPERADMIN

### **Buenas Prácticas:**
1. **Mantener múltiples copias** en diferentes ubicaciones
2. **Probar restauraciones** periódicamente
3. **Documentar procedimientos** de recuperación
4. **Rotar dispositivos USB** regularmente
5. **Verificar integridad** después de cada respaldo

## 🚨 Procedimientos de Emergencia

### **Si el sistema principal falla:**
1. Usar respaldo más reciente del USB
2. Restaurar base de datos
3. Sincronizar con dispositivo ZKTeco
4. Verificar integridad de datos

### **Si se pierde un dispositivo USB:**
1. Usar respaldo local más reciente
2. Crear nuevo respaldo inmediatamente
3. Usar dispositivo USB de respaldo
4. Documentar el incidente

## 📞 Soporte Técnico

### **Problemas Comunes:**

**Error: "No se pudo conectar a la base de datos"**
- Verificar que PostgreSQL esté ejecutándose
- Comprobar credenciales en database.py
- Verificar permisos de usuario

**Error: "No se detectaron dispositivos USB"**
- Verificar que el USB esté conectado correctamente
- Comprobar que el sistema reconozca el dispositivo
- Intentar con otro puerto USB

**Error: "Espacio insuficiente en disco"**
- Limpiar respaldos antiguos manualmente
- Liberar espacio en disco
- Cambiar directorio de respaldo

### **Contacto:**
- **Desarrollador**: Sistema QUIRA
- **Institución**: Policía Nacional del Paraguay
- **Departamento**: Instituto de Criminalística

---

## 📝 Notas Importantes

1. **Este sistema está diseñado para entornos sin internet**
2. **Los respaldos son locales y no requieren conexión externa**
3. **Se recomienda mantener al menos 3 copias en diferentes ubicaciones**
4. **Probar el sistema de respaldo antes de usarlo en producción**
5. **Documentar cualquier problema o mejora para futuras versiones**

---

*Sistema de Respaldo Local v1.0 - Optimizado para Sistema QUIRA*

