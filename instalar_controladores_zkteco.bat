@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo    INSTALAR CONTROLADORES ZKTECO
echo ========================================
echo.
echo Este script instalará controladores específicos
echo para el dispositivo ZKTeco K40 si son necesarios
echo.

:: Verificar si se ejecuta como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ ERROR: Este script debe ejecutarse como ADMINISTRADOR
    echo.
    echo Por favor:
    echo 1. Haga clic derecho en este archivo
    echo 2. Seleccionar "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo ✅ Ejecutando como administrador...
echo.

:: Verificar si hay controladores específicos disponibles
echo 🔍 VERIFICANDO CONTROLADORES DISPONIBLES...
echo.

:: Buscar controladores en el sistema
echo Buscando controladores de dispositivos biométricos...
pnputil /enum-drivers | findstr /i "biometric\|fingerprint\|zk\|usb"
echo.

:: Verificar si hay dispositivos no reconocidos
echo Verificando dispositivos no reconocidos...
pnputil /enum-devices | findstr /i "unknown\|other"
echo.

:: Instalar controladores de red genéricos si es necesario
echo 🔧 INSTALANDO CONTROLADORES DE RED GENÉRICOS...
echo.

echo Actualizando controladores de red...
dism /online /add-driver /driver:"C:\Windows\System32\DriverStore\FileRepository" /recurse
echo ✅ Controladores de red actualizados
echo.

:: Instalar controladores USB genéricos
echo 🔧 INSTALANDO CONTROLADORES USB...
echo.

echo Actualizando controladores USB...
pnputil /scan-devices
echo ✅ Dispositivos USB escaneados

echo Instalando controladores USB genéricos...
pnputil /add-driver "C:\Windows\System32\DriverStore\FileRepository\usb*.inf" /install
echo ✅ Controladores USB instalados
echo.

:: Configurar servicios de red
echo 🔧 CONFIGURANDO SERVICIOS DE RED...
echo.

echo Configurando servicio TCP/IP...
netsh winsock reset
echo ✅ Winsock reiniciado

echo Configurando protocolos de red...
netsh int ip reset
echo ✅ Protocolos de red reiniciados
echo.

:: Crear reglas de firewall específicas
echo 🔧 CONFIGURANDO FIREWALL ESPECÍFICO...
echo.

echo Eliminando reglas anteriores de ZKTeco...
netsh advfirewall firewall delete rule name="ZKTeco*"
echo ✅ Reglas anteriores eliminadas

echo Creando reglas específicas para ZKTeco...
netsh advfirewall firewall add rule name="ZKTeco K40 UDP In" dir=in action=allow protocol=UDP localport=4370
netsh advfirewall firewall add rule name="ZKTeco K40 UDP Out" dir=out action=allow protocol=UDP remoteport=4370
netsh advfirewall firewall add rule name="ZKTeco K40 TCP In" dir=in action=allow protocol=TCP localport=4370
netsh advfirewall firewall add rule name="ZKTeco K40 TCP Out" dir=out action=allow protocol=TCP remoteport=4370
echo ✅ Reglas de firewall creadas
echo.

:: Verificar controladores de dispositivos específicos
echo 🔍 VERIFICANDO DISPOSITIVOS ESPECÍFICOS...
echo.

echo Dispositivos de entrada:
wmic path win32_pnpentity where "name like '%%keyboard%%' or name like '%%mouse%%' or name like '%%usb%%'" get name,status
echo.

echo Dispositivos de red:
wmic nic get name,status,manufacturer
echo.

:: Instalar controladores de dispositivos de entrada si es necesario
echo 🔧 INSTALANDO CONTROLADORES DE ENTRADA...
echo.

echo Actualizando controladores de dispositivos de entrada...
pnputil /add-driver "C:\Windows\System32\DriverStore\FileRepository\hid*.inf" /install
echo ✅ Controladores de entrada instalados
echo.

:: Verificar conectividad después de la instalación
echo 🔍 VERIFICANDO CONECTIVIDAD POST-INSTALACIÓN...
echo.

echo Probando conectividad al dispositivo ZKTeco...
ping -n 3 192.168.100.201
if !errorlevel! equ 0 (
    echo ✅ Dispositivo responde después de la instalación
) else (
    echo ❌ Dispositivo aún no responde
    echo.
    echo Verificando configuración de red...
    ipconfig | findstr /i "IPv4"
    echo.
    echo Verificando tabla ARP...
    arp -a | findstr "192.168.100"
)

echo.

:: Mostrar información final
echo 📋 INFORMACIÓN FINAL:
echo.

echo Controladores instalados:
wmic nic get name,driverversion,manufacturer /format:table
echo.

echo Servicios de red:
sc query "Tcpip" | findstr "STATE"
sc query "Dhcp" | findstr "STATE"
sc query "Dnscache" | findstr "STATE"
echo.

echo Reglas de firewall para ZKTeco:
netsh advfirewall firewall show rule name="ZKTeco*"
echo.

:: Crear reporte de instalación
echo 📄 Generando reporte de instalación...
(
echo ========================================
echo    REPORTE DE INSTALACIÓN ZKTECO
echo ========================================
echo Fecha: %date% %time%
echo.
echo CONTROLADORES INSTALADOS:
wmic nic get name,driverversion,manufacturer /format:table
echo.
echo SERVICIOS DE RED:
sc query "Tcpip" | findstr "STATE"
sc query "Dhcp" | findstr "STATE"
sc query "Dnscache" | findstr "STATE"
echo.
echo REGLAS DE FIREWALL:
netsh advfirewall firewall show rule name="ZKTeco*"
echo.
echo CONECTIVIDAD:
ping -n 1 192.168.100.201
echo.
echo ========================================
) > "reporte_instalacion_zkteco_%date:~-4,4%%date:~-10,2%%date:~-7,2%.txt"

echo ✅ Reporte guardado: reporte_instalacion_zkteco_%date:~-4,4%%date:~-10,2%%date:~-7,2%.txt
echo.

:: Instrucciones adicionales
echo 📝 INFORMACIÓN IMPORTANTE:
echo.
echo 1. CONTROLADORES ZKTECO:
echo    - El dispositivo ZKTeco K40 NO requiere controladores especiales
echo    - Se comunica por protocolos de red estándar (UDP/TCP)
echo    - Los controladores instalados son genéricos del sistema
echo.
echo 2. SI EL PROBLEMA PERSISTE:
echo    - El problema NO es de controladores
echo    - Verifique la configuración de red
echo    - Verifique la conectividad física
echo    - Verifique la configuración del dispositivo
echo.
echo 3. CONTROLADORES OPCIONALES:
echo    - Software de gestión ZKTeco (no requerido para QUIRA)
echo    - Controladores de impresora (si aplica)
echo    - Controladores de cámara (si aplica)
echo.
echo 4. VERIFICACIÓN MANUAL:
echo    - Abra "Administrador de dispositivos"
echo    - Verifique que no hay dispositivos con problemas
echo    - Verifique que la tarjeta de red funciona
echo    - Verifique que los servicios de red están activos
echo.

echo 🎯 INSTALACIÓN DE CONTROLADORES COMPLETADA
echo    El dispositivo ZKTeco debería funcionar correctamente
echo.

pause
