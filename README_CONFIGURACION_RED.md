# Configuración de Red para Sistema QUIRA - ZKTeco K40

Este conjunto de scripts automatiza la configuración de red necesaria para que el sistema QUIRA pueda conectarse al dispositivo biométrico ZKTeco K40.

## 📋 Requisitos

- **Sistema Operativo:** Windows 10/11
- **Permisos:** Administrador (requerido para configurar red)
- **Dispositivo ZKTeco:** Configurado con IP `192.168.100.201`

## 🚀 Scripts Disponibles

### 1. `configurar_red_zkteco.bat`
**Propósito:** Configura automáticamente la red de la computadora para conectarse al ZKTeco.

**Funciones:**
- Detecta interfaces de red activas (Ethernet/WiFi)
- Configura IP estática en rango `192.168.100.x`
- Configura gateway `192.168.100.1`
- Configura DNS (8.8.8.8 y 8.8.4.4)
- Verifica conectividad con el dispositivo
- Genera archivo de configuración

**Uso:**
```bash
# Ejecutar como administrador
configurar_red_zkteco.bat
```

### 2. `restaurar_dhcp.bat`
**Propósito:** Restaura la configuración DHCP original de la red.

**Funciones:**
- Lee configuración anterior del archivo generado
- Restaura IP automática (DHCP)
- Restaura DNS automático
- Verifica conectividad a internet
- Genera archivo de respaldo

**Uso:**
```bash
# Ejecutar como administrador
restaurar_dhcp.bat
```

### 3. `diagnostico_zkteco.bat`
**Propósito:** Diagnostica problemas de conectividad con el ZKTeco.

**Funciones:**
- Verifica configuración de red actual (IPv4 e IPv6)
- Prueba conectividad con ping
- Prueba conectividad de puerto
- Analiza ruta de red
- Verifica firewall
- Verifica tabla de enrutamiento
- Genera reporte de diagnóstico detallado

**Uso:**
```bash
# No requiere permisos de administrador
diagnostico_zkteco.bat
```

### 4. `solucionar_host_inaccesible.bat`
**Propósito:** Soluciona específicamente el problema "host de destino inaccesible".

**Funciones:**
- Detecta y corrige problemas de configuración de red
- Limpia caché ARP y DNS
- Reinicia tarjeta de red automáticamente
- Proporciona soluciones manuales detalladas
- Verifica conectividad después de las correcciones

**Uso:**
```bash
# Ejecutar como administrador
solucionar_host_inaccesible.bat
```

## 📖 Guía de Uso

### Paso 1: Diagnóstico Inicial
```bash
# Ejecutar diagnóstico para verificar estado actual
diagnostico_zkteco.bat
```

### Paso 2: Configurar Red (si es necesario)
```bash
# Si el diagnóstico muestra problemas de conectividad:
# 1. Hacer clic derecho en configurar_red_zkteco.bat
# 2. Seleccionar "Ejecutar como administrador"
# 3. Seguir las instrucciones en pantalla
```

### Paso 3: Verificar Configuración
```bash
# Ejecutar diagnóstico nuevamente para confirmar
diagnostico_zkteco.bat
```

### Paso 4: Restaurar DHCP (cuando sea necesario)
```bash
# Para restaurar configuración original:
# 1. Hacer clic derecho en restaurar_dhcp.bat
# 2. Seleccionar "Ejecutar como administrador"
# 3. Seguir las instrucciones en pantalla
```

## 🔧 Configuración Manual (Alternativa)

Si prefiere configurar manualmente:

### Configurar IP Estática IPv4
1. Abrir "Configuración de red e Internet"
2. Seleccionar "Cambiar opciones del adaptador"
3. Hacer clic derecho en la interfaz activa
4. Seleccionar "Propiedades"
5. Seleccionar "Protocolo de Internet versión 4 (TCP/IPv4)"
6. Hacer clic en "Propiedades"
7. Seleccionar "Usar la siguiente dirección IP"
8. Configurar:
   - **IP:** `192.168.100.x` (donde x es 2-254)
   - **Máscara:** `255.255.255.0`
   - **Longitud de prefijo:** `/24`
   - **Gateway:** `192.168.100.1`
   - **DNS:** `8.8.8.8` y `8.8.4.4`

### Configurar IPv6 (Automático - Recomendado)
1. En la misma ventana de propiedades
2. Seleccionar "Protocolo de Internet versión 6 (TCP/IPv6)"
3. Hacer clic en "Propiedades"
4. Seleccionar "Obtener una dirección IPv6 automáticamente"
5. Seleccionar "Obtener la dirección del servidor DNS automáticamente"
6. **Longitud de prefijo:** `/64` (automático)

## 📊 Archivos Generados

Los scripts generan los siguientes archivos:

- `configuracion_red_zkteco.txt` - Configuración aplicada
- `restauracion_dhcp_YYYYMMDD.txt` - Respaldo de restauración
- `diagnostico_zkteco_YYYYMMDD.txt` - Reporte de diagnóstico

## ⚠️ Consideraciones Importantes

### Antes de Configurar
- **Hacer respaldo** de la configuración actual
- **Verificar** que el dispositivo ZKTeco esté encendido
- **Confirmar** que la IP del dispositivo sea `192.168.100.201`

### Durante la Configuración
- **No interrumpir** el proceso de configuración
- **Esperar** a que se complete cada paso
- **Leer** los mensajes de confirmación

### Después de Configurar
- **Verificar** conectividad con el diagnóstico
- **Probar** el sistema QUIRA
- **Guardar** los archivos de configuración

## 🚨 Solución de Problemas

### Error: "Debe ejecutarse como administrador"
**Solución:** Hacer clic derecho en el script y seleccionar "Ejecutar como administrador"

### Error: "No se encontraron interfaces de red activas"
**Solución:** Verificar que la tarjeta de red esté habilitada y conectada

### Error: "No se pudo conectar al dispositivo ZKTeco"
**Soluciones:**
1. Verificar que el dispositivo esté encendido
2. Verificar la conexión de cable de red
3. Verificar que la IP del dispositivo sea correcta
4. Reiniciar el dispositivo ZKTeco

### Error: "Host de destino inaccesible"
**Soluciones:**
1. **Ejecutar:** `solucionar_host_inaccesible.bat` como administrador
2. Verificar configuración de red (máscara, gateway)
3. Limpiar caché ARP: `arp -d *`
4. Reiniciar tarjeta de red
5. Verificar infraestructura de red (switch/router)

### Error: "IP ya está en uso"
**Solución:** El script automáticamente encuentra una IP disponible

## 📞 Soporte

Si tiene problemas con la configuración:

1. **Ejecutar diagnóstico** para identificar el problema
2. **Revisar** el archivo de reporte generado
3. **Verificar** la configuración del dispositivo ZKTeco
4. **Contactar** al administrador del sistema

## 🔒 Seguridad

- Los scripts solo modifican la configuración de red local
- No se envían datos a servidores externos
- Se generan archivos de respaldo automáticamente
- Se puede restaurar la configuración original en cualquier momento

---

**🎯 Objetivo:** Permitir que cualquier computadora pueda conectarse al dispositivo ZKTeco K40 para usar el sistema QUIRA sin problemas de configuración de red.
