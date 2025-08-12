@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo    CONFIGURADOR DE RED PARA ZKTECO
echo ========================================
echo.
echo Este script configurará la red de su computadora
echo para conectarse al dispositivo ZKTeco K40
echo.
echo IP del dispositivo: 192.168.100.201
echo Puerto: 4370
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

:: Mostrar interfaces de red disponibles
echo 📋 Interfaces de red disponibles:
echo.
netsh interface show interface
echo.

:: Detectar interfaces activas
echo 🔍 Detectando interfaces de red activas...
echo.

:: Buscar interfaces Ethernet y WiFi activas
for /f "tokens=1,2,3,4 delims= " %%a in ('netsh interface show interface ^| findstr /i "conectado"') do (
    set "interface_name=%%d"
    set "interface_admin=%%a"
    set "interface_type=%%b"
    
    if "!interface_type!"=="Ethernet" (
        echo ✅ Encontrada interfaz Ethernet: !interface_name!
        set "ethernet_interface=!interface_name!"
    )
    if "!interface_type!"=="Wi-Fi" (
        echo ✅ Encontrada interfaz Wi-Fi: !interface_name!
        set "wifi_interface=!interface_name!"
    )
)

echo.

:: Priorizar Ethernet sobre WiFi
if defined ethernet_interface (
    set "target_interface=!ethernet_interface!"
    echo 🎯 Usando interfaz Ethernet: !target_interface!
) else if defined wifi_interface (
    set "target_interface=!wifi_interface!"
    echo 🎯 Usando interfaz Wi-Fi: !target_interface!
) else (
    echo ❌ ERROR: No se encontraron interfaces de red activas
    pause
    exit /b 1
)

echo.

:: Verificar configuración actual IPv4 e IPv6
echo 📊 Verificando configuración actual de la interfaz...
echo.

:: Mostrar configuración IPv4 actual
for /f "tokens=2 delims=:" %%a in ('netsh interface ip show config "!target_interface!" ^| findstr /i "IP Address"') do (
    set "current_ipv4=%%a"
    set "current_ipv4=!current_ipv4: =!"
)

if defined current_ipv4 (
    echo IPv4 actual: !current_ipv4!
) else (
    echo IPv4 actual: No configurada (DHCP)
)

:: Mostrar configuración IPv6 actual
for /f "tokens=2 delims=:" %%a in ('netsh interface ipv6 show config "!target_interface!" ^| findstr /i "IP Address"') do (
    set "current_ipv6=%%a"
    set "current_ipv6=!current_ipv6: =!"
)

if defined current_ipv6 (
    echo IPv6 actual: !current_ipv6!
) else (
    echo IPv6 actual: No configurada (Auto)
)

echo.

:: Preguntar al usuario si desea continuar
echo ¿Desea configurar la interfaz "!target_interface!" para conectarse al ZKTeco?
echo.
echo Esta acción:
echo - Configurará una IP estática IPv4 en el rango 192.168.100.x
echo - Configurará la puerta de enlace IPv4 192.168.100.1
echo - Configurará DNS IPv4 8.8.8.8 y 8.8.4.4
echo - Configurará IPv6 automático (recomendado)
echo.
set /p "confirm=¿Continuar? (S/N): "

if /i not "!confirm!"=="S" (
    echo.
    echo ❌ Configuración cancelada por el usuario
    pause
    exit /b 0
)

echo.

:: Generar IP única para esta computadora
set "ip_suffix=100"
for /l %%i in (2,1,254) do (
    ping -n 1 192.168.100.%%i >nul 2>&1
    if !errorlevel! neq 0 (
        set "ip_suffix=%%i"
        goto :ip_found
    )
)

:ip_found
set "new_ipv4=192.168.100.!ip_suffix!"

echo 🎯 Configurando IPv4: !new_ipv4!
echo.

:: Configurar IPv4 estática
echo 📡 Configurando interfaz de red IPv4...
netsh interface ip set address "!target_interface!" static !new_ipv4! 255.255.255.0 192.168.100.1

if !errorlevel! equ 0 (
    echo ✅ IPv4 configurada exitosamente
) else (
    echo ❌ Error al configurar IPv4
    pause
    exit /b 1
)

:: Configurar DNS IPv4
echo 📡 Configurando DNS IPv4...
netsh interface ip set dns "!target_interface!" static 8.8.8.8
netsh interface ip add dns "!target_interface!" 8.8.4.4 index=2

if !errorlevel! equ 0 (
    echo ✅ DNS IPv4 configurado exitosamente
) else (
    echo ⚠️ Advertencia: Error al configurar DNS IPv4
)

echo.

:: Configurar IPv6 automático
echo 📡 Configurando IPv6 automático...
netsh interface ipv6 set address "!target_interface!" auto

if !errorlevel! equ 0 (
    echo ✅ IPv6 automático configurado exitosamente
) else (
    echo ⚠️ Advertencia: Error al configurar IPv6 automático
)

:: Configurar DNS IPv6 automático
netsh interface ipv6 set dns "!target_interface!" auto

if !errorlevel! equ 0 (
    echo ✅ DNS IPv6 automático configurado exitosamente
) else (
    echo ⚠️ Advertencia: Error al configurar DNS IPv6 automático
)

echo.

:: Verificar conectividad con el dispositivo
echo 🔍 Verificando conectividad con el dispositivo ZKTeco...
echo.

ping -n 3 192.168.100.201 >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ ¡CONECTIVIDAD EXITOSA!
    echo    El dispositivo ZKTeco responde correctamente
) else (
    echo ⚠️ ADVERTENCIA: No se pudo conectar al dispositivo ZKTeco
    echo    Verifique que el dispositivo esté encendido y conectado
    echo    IP del dispositivo: 192.168.100.201
)

echo.

:: Mostrar configuración final
echo 📋 CONFIGURACIÓN FINAL:
echo.
echo Interfaz: !target_interface!
echo.
echo IPv4:
echo   IP: !new_ipv4!
echo   Máscara: 255.255.255.0
echo   Longitud de prefijo: /24
echo   Gateway: 192.168.100.1
echo   DNS 1: 8.8.8.8
echo   DNS 2: 8.8.4.4
echo.
echo IPv6:
echo   Configuración: Automática
echo   Longitud de prefijo: /64 (automático)
echo   DNS: Automático
echo.
echo Dispositivo ZKTeco: 192.168.100.201:4370
echo.

:: Crear archivo de configuración para el sistema
echo Creando archivo de configuración...
(
echo # Configuración de red para ZKTeco
echo # Generado automáticamente el %date% %time%
echo.
echo INTERFACE=!target_interface!
echo.
echo IPv4_CONFIG:
echo COMPUTER_IP=!new_ipv4!
echo SUBNET_MASK=255.255.255.0
echo PREFIX_LENGTH=24
echo GATEWAY=192.168.100.1
echo DNS1=8.8.8.8
echo DNS2=8.8.4.4
echo.
echo IPv6_CONFIG:
echo CONFIGURATION=AUTO
echo PREFIX_LENGTH=64
echo DNS=AUTO
echo.
echo ZKTECO_IP=192.168.100.201
echo ZKTECO_PORT=4370
) > "configuracion_red_zkteco.txt"

echo ✅ Archivo de configuración guardado: configuracion_red_zkteco.txt
echo.

:: Mostrar información técnica adicional
echo 📚 INFORMACIÓN TÉCNICA:
echo.
echo Longitud de prefijo IPv4 (/24):
echo - Rango de red: 192.168.100.0 - 192.168.100.255
echo - Direcciones utilizables: 192.168.100.1 - 192.168.100.254
echo - Broadcast: 192.168.100.255
echo.
echo Longitud de prefijo IPv6 (/64):
echo - Configuración automática por SLAAC
echo - Soporte para direcciones link-local y global
echo - Compatibilidad con dispositivos modernos
echo.

:: Instrucciones adicionales
echo 📝 INSTRUCCIONES ADICIONALES:
echo.
echo 1. Si el dispositivo ZKTeco no responde:
echo    - Verifique que esté encendido
echo    - Verifique la conexión de red
echo    - Reinicie el dispositivo si es necesario
echo.
echo 2. Para restaurar configuración DHCP:
echo    - Ejecute: netsh interface ip set address "!target_interface!" dhcp
echo    - Ejecute: netsh interface ip set dns "!target_interface!" dhcp
echo    - Ejecute: netsh interface ipv6 set address "!target_interface!" auto
echo.
echo 3. Para verificar conectividad manualmente:
echo    - ping 192.168.100.201
echo    - telnet 192.168.100.201 4370
echo    - ping -6 [IPv6-address] (si el dispositivo soporta IPv6)
echo.

echo 🎉 ¡Configuración completada!
echo    El sistema QUIRA debería poder conectarse al dispositivo ZKTeco
echo.

pause
