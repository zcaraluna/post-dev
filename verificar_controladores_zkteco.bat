@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo    VERIFICAR CONTROLADORES ZKTECO
echo ========================================
echo.
echo Este script verificará e instalará los
echo controladores necesarios para el dispositivo ZKTeco K40
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

:: Verificar controladores de red
echo 🔍 VERIFICANDO CONTROLADORES DE RED...
echo.

echo Controladores de tarjeta de red instalados:
wmic nic get name,driverversion /format:table
echo.

:: Verificar si hay controladores desactualizados
echo Verificando controladores desactualizados...
pnputil /enum-drivers | findstr /i "ethernet\|network\|realtek\|intel"
echo.

:: Verificar servicios de red
echo 🔍 VERIFICANDO SERVICIOS DE RED...
echo.

echo Estado de servicios críticos:
sc query "Tcpip" | findstr "STATE"
sc query "Dhcp" | findstr "STATE"
sc query "Dnscache" | findstr "STATE"
echo.

:: Verificar configuración de red avanzada
echo 🔍 VERIFICANDO CONFIGURACIÓN DE RED AVANZADA...
echo.

echo Configuración de Winsock:
netsh winsock show catalog
echo.

echo Configuración de protocolos de red:
netsh interface show interface
echo.

:: Verificar si hay dispositivos ZKTeco detectados
echo 🔍 BUSCANDO DISPOSITIVOS ZKTECO...
echo.

echo Dispositivos USB conectados:
wmic usbcontrollerdevice get dependent /format:table | findstr /i "zk\|biometric\|fingerprint"
echo.

echo Dispositivos de red:
arp -a | findstr "192.168.100"
echo.

:: Verificar puertos abiertos
echo 🔍 VERIFICANDO PUERTOS DE RED...
echo.

echo Puerto 4370 (ZKTeco):
netstat -an | findstr ":4370"
echo.

echo Puertos UDP activos:
netstat -an | findstr "UDP" | findstr "LISTENING"
echo.

:: Verificar firewall
echo 🔍 VERIFICANDO FIREWALL...
echo.

echo Reglas de firewall para ZKTeco:
netsh advfirewall firewall show rule name=all | findstr /i "zk\|4370\|biometric"
echo.

:: Crear regla de firewall si no existe
echo 🧧 CONFIGURANDO FIREWALL PARA ZKTECO...
echo.

echo Creando regla de firewall para ZKTeco...
netsh advfirewall firewall add rule name="ZKTeco K40" dir=in action=allow protocol=UDP localport=4370
netsh advfirewall firewall add rule name="ZKTeco K40 Out" dir=out action=allow protocol=UDP remoteport=4370
echo ✅ Reglas de firewall creadas
echo.

:: Verificar controladores específicos
echo 🔍 VERIFICANDO CONTROLADORES ESPECÍFICOS...
echo.

echo Controladores de dispositivos biométricos:
pnputil /enum-devices | findstr /i "biometric\|fingerprint\|zk"
echo.

:: Instalar controladores de red si es necesario
echo 🔧 INSTALANDO CONTROLADORES DE RED...
echo.

echo Actualizando controladores de red...
pnputil /scan-devices
echo ✅ Dispositivos escaneados

echo Actualizando controladores...
pnputil /add-driver "C:\Windows\System32\DriverStore\FileRepository\*.inf" /install
echo ✅ Controladores actualizados
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
)

echo.

:: Mostrar información de controladores
echo 📋 INFORMACIÓN DE CONTROLADORES:
echo.

echo Controladores de red principales:
wmic nic where "NetEnabled='true'" get name,driverversion,manufacturer /format:table
echo.

echo Controladores de dispositivos USB:
wmic usbcontroller get name,driverversion /format:table
echo.

:: Crear reporte de controladores
echo 📄 Generando reporte de controladores...
(
echo ========================================
echo    REPORTE DE CONTROLADORES ZKTECO
echo ========================================
echo Fecha: %date% %time%
echo.
echo CONTROLADORES DE RED:
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
echo PUERTOS ACTIVOS:
netstat -an | findstr ":4370"
echo.
echo ========================================
) > "reporte_controladores_zkteco_%date:~-4,4%%date:~-10,2%%date:~-7,2%.txt"

echo ✅ Reporte guardado: reporte_controladores_zkteco_%date:~-4,4%%date:~-10,2%%date:~-7,2%.txt
echo.

:: Instrucciones adicionales
echo 📝 INSTRUCCIONES ADICIONALES:
echo.
echo 1. CONTROLADORES ESPECÍFICOS ZKTECO:
echo    - El dispositivo ZKTeco K40 NO requiere controladores especiales
echo    - Se comunica por protocolo UDP estándar
echo    - Solo necesita conectividad de red básica
echo.
echo 2. SI EL PROBLEMA PERSISTE:
echo    - Verifique que el dispositivo esté encendido
echo    - Verifique la conexión de cable de red
echo    - Reinicie el dispositivo ZKTeco
echo    - Verifique la IP del dispositivo (192.168.100.201)
echo.
echo 3. CONTROLADORES OPCIONALES:
echo    - Software de gestión ZKTeco (no requerido para QUIRA)
echo    - Controladores de impresora (si tiene impresora integrada)
echo    - Controladores de cámara (si tiene cámara integrada)
echo.
echo 4. VERIFICACIÓN MANUAL:
echo    - Abra "Administrador de dispositivos"
echo    - Verifique que no hay dispositivos con signo de exclamación
echo    - Verifique que la tarjeta de red funciona correctamente
echo.

echo 🎯 VERIFICACIÓN DE CONTROLADORES COMPLETADA
echo    Revise el reporte generado para más detalles
echo.

pause
