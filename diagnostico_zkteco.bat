@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo    DIAGNÓSTICO DE CONECTIVIDAD ZKTECO
echo ========================================
echo.
echo Este script diagnosticará la conectividad
echo con el dispositivo ZKTeco K40
echo.

:: Configuración del dispositivo
set "ZKTECO_IP=192.168.100.201"
set "ZKTECO_PORT=4370"

echo 📋 INFORMACIÓN DEL DISPOSITIVO:
echo    IP: %ZKTECO_IP%
echo    Puerto: %ZKTECO_PORT%
echo.

:: Verificar configuración de red actual
echo 🔍 VERIFICANDO CONFIGURACIÓN DE RED...
echo.

:: Mostrar interfaces activas
echo 📡 Interfaces de red activas:
netsh interface show interface | findstr /i "conectado"
echo.

:: Mostrar configuración IP actual
echo 📊 Configuración IP actual:
ipconfig | findstr /i "IPv4"
echo.

:: Mostrar configuración IPv6 actual
echo 📊 Configuración IPv6 actual:
ipconfig | findstr /i "IPv6"
echo.

:: Verificar si estamos en el rango correcto
echo 🔍 Verificando rango de red...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set "current_ip=%%a"
    set "current_ip=!current_ip: =!"
    
    if "!current_ip!" neq "" (
        echo IP actual: !current_ip!
        
        :: Verificar si está en el rango 192.168.100.x
        echo !current_ip! | findstr /r "^192\.168\.100\." >nul
        if !errorlevel! equ 0 (
            echo ✅ IP en rango correcto (192.168.100.x)
        ) else (
            echo ⚠️ IP NO está en el rango correcto
            echo    Se requiere IP en rango 192.168.100.x
        )
    )
)

echo.

:: Prueba de conectividad básica
echo 🔍 PRUEBA DE CONECTIVIDAD BÁSICA...
echo.

echo 1. Ping al dispositivo ZKTeco:
ping -n 3 %ZKTECO_IP%
if !errorlevel! equ 0 (
    echo ✅ PING EXITOSO - El dispositivo responde
) else (
    echo ❌ PING FALLIDO - El dispositivo no responde
    echo    Posibles causas:
    echo    - Dispositivo apagado
    echo    - Cable de red desconectado
    echo    - IP incorrecta del dispositivo
    echo    - Configuración de red incorrecta
    echo    - Problema de enrutamiento
)

echo.

:: Prueba de conectividad de puerto
echo 2. Prueba de puerto %ZKTECO_PORT%:
echo    Intentando conectar al puerto %ZKTECO_PORT%...

:: Usar telnet para probar el puerto (si está disponible)
telnet %ZKTECO_IP% %ZKTECO_PORT% <nul >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ PUERTO ACCESIBLE - Conexión exitosa al puerto %ZKTECO_PORT%
) else (
    echo ⚠️ PUERTO NO ACCESIBLE - No se pudo conectar al puerto %ZKTECO_PORT%
    echo    Esto puede ser normal si el dispositivo no está configurado
)

echo.

:: Prueba de ruta de red
echo 3. Prueba de ruta de red:
tracert -h 5 %ZKTECO_IP%
echo.

:: Verificar firewall
echo 4. Verificando firewall de Windows:
netsh advfirewall show allprofiles state | findstr /i "estado"
echo.

:: Verificar tabla de enrutamiento
echo 5. Verificando tabla de enrutamiento:
route print | findstr "192.168.100"
echo.

:: Verificar configuración de gateway
echo 6. Verificando configuración de gateway:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "Default Gateway"') do (
    set "gateway=%%a"
    set "gateway=!gateway: =!"
    if "!gateway!" neq "" (
        echo Gateway detectado: !gateway!
        echo Probando conectividad al gateway...
        ping -n 2 !gateway! >nul 2>&1
        if !errorlevel! equ 0 (
            echo ✅ Gateway responde correctamente
        ) else (
            echo ❌ Gateway no responde
        )
    )
)

echo.

:: Información adicional
echo 📋 INFORMACIÓN ADICIONAL:
echo.

:: Verificar si hay otros dispositivos en la red
echo 7. Escaneando red local (192.168.100.x):
echo    Buscando otros dispositivos...
for /l %%i in (1,1,10) do (
    ping -n 1 192.168.100.%%i >nul 2>&1
    if !errorlevel! equ 0 (
        echo    ✅ 192.168.100.%%i responde
    )
)

echo.

:: Verificar configuración de interfaz específica
echo 8. Verificando configuración detallada de interfaz:
for /f "tokens=1,2,3,4 delims= " %%a in ('netsh interface show interface ^| findstr /i "conectado"') do (
    set "interface_name=%%d"
    set "interface_admin=%%a"
    set "interface_type=%%b"
    
    if "!interface_type!"=="Ethernet" (
        echo Interfaz Ethernet: !interface_name!
        echo Configuración IPv4:
        netsh interface ip show config "!interface_name!" | findstr /i "IP\|Gateway\|DNS"
        echo.
        echo Configuración IPv6:
        netsh interface ipv6 show config "!interface_name!" | findstr /i "IP\|Gateway\|DNS"
        echo.
    )
)

echo.

:: Recomendaciones específicas para "host inaccesible"
echo 📝 DIAGNÓSTICO ESPECÍFICO PARA "HOST INACCESIBLE":
echo.

:: Verificar configuración actual
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set "current_ip=%%a"
    set "current_ip=!current_ip: =!"
    
    if "!current_ip!" neq "" (
        echo !current_ip! | findstr /r "^192\.168\.100\." >nul
        if !errorlevel! neq 0 (
            echo ❌ PROBLEMA DETECTADO:
            echo    Su IP actual (!current_ip!) no está en el rango correcto
            echo    Para solucionarlo:
            echo    1. Ejecute "configurar_red_zkteco.bat" como administrador
            echo    2. O configure manualmente una IP en rango 192.168.100.x
        ) else (
            echo ✅ CONFIGURACIÓN CORRECTA:
            echo    Su IP está en el rango correcto
        )
    )
)

echo.

:: Verificar si el ping fue exitoso
ping -n 1 %ZKTECO_IP% >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ PROBLEMA DE CONECTIVIDAD:
    echo    No se puede conectar al dispositivo ZKTeco
    echo.
    echo SOLUCIONES PARA "HOST INACCESIBLE":
    echo.
    echo 1. VERIFICAR DISPOSITIVO:
    echo    - ¿Está el dispositivo ZKTeco encendido?
    echo    - ¿Está conectado el cable de red?
    echo    - ¿La IP del dispositivo es realmente %ZKTECO_IP%?
    echo.
    echo 2. VERIFICAR RED:
    echo    - ¿Está conectado el cable de red a la computadora?
    echo    - ¿Hay un switch/router entre la PC y el dispositivo?
    echo    - ¿El switch/router está encendido?
    echo.
    echo 3. VERIFICAR CONFIGURACIÓN:
    echo    - ¿La máscara de subred es 255.255.255.0?
    echo    - ¿El gateway está configurado correctamente?
    echo    - ¿No hay conflictos de IP?
    echo.
    echo 4. PRUEBAS ADICIONALES:
    echo    - Ejecute: arp -a (para ver tabla ARP)
    echo    - Ejecute: route print (para ver tabla de rutas)
    echo    - Ejecute: ipconfig /all (para configuración completa)
    echo.
    echo 5. SOLUCIÓN RÁPIDA:
    echo    - Reinicie el dispositivo ZKTeco
    echo    - Reinicie la tarjeta de red
    echo    - Ejecute: ipconfig /release && ipconfig /renew
) else (
    echo ✅ CONECTIVIDAD EXITOSA:
    echo    El dispositivo ZKTeco responde correctamente
    echo    El sistema QUIRA debería poder conectarse
)

echo.

:: Crear reporte de diagnóstico
echo 📄 Generando reporte de diagnóstico...
(
echo ========================================
echo    REPORTE DE DIAGNÓSTICO ZKTECO
echo ========================================
echo Fecha: %date% %time%
echo.
echo DISPOSITIVO:
echo IP: %ZKTECO_IP%
echo Puerto: %ZKTECO_PORT%
echo.
echo CONFIGURACIÓN ACTUAL:
ipconfig | findstr /i "IPv4"
echo.
echo CONFIGURACIÓN IPv6:
ipconfig | findstr /i "IPv6"
echo.
echo PRUEBA DE PING:
ping -n 1 %ZKTECO_IP%
echo.
echo TABLA DE ENRUTAMIENTO:
route print | findstr "192.168.100"
echo.
echo ESTADO DE FIREWALL:
netsh advfirewall show allprofiles state
echo.
echo ========================================
) > "diagnostico_zkteco_%date:~-4,4%%date:~-10,2%%date:~-7,2%.txt"

echo ✅ Reporte guardado: diagnostico_zkteco_%date:~-4,4%%date:~-10,2%%date:~-7,2%.txt
echo.

echo 🎯 DIAGNÓSTICO COMPLETADO
echo    Revise el reporte generado para más detalles
echo.

pause
