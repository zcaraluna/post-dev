@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo    RESTAURAR CONFIGURACIÓN DHCP
echo ========================================
echo.
echo Este script restaurará la configuración DHCP
echo de la interfaz de red configurada para ZKTeco
echo.

:: Verificar si se ejecuta como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ ERROR: Este script debe ejecutarse como ADMINISTRADOR
    echo.
    echo Por favor:
    echo 1. Haga clic derecho en este archivo
    echo 2. Seleccione "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo ✅ Ejecutando como administrador...
echo.

:: Verificar si existe archivo de configuración
if exist "configuracion_red_zkteco.txt" (
    echo 📋 Archivo de configuración encontrado
    echo.
    
    :: Leer interfaz del archivo de configuración
    for /f "tokens=2 delims==" %%a in ('findstr "INTERFACE=" configuracion_red_zkteco.txt') do (
        set "target_interface=%%a"
    )
    
    if defined target_interface (
        echo 🎯 Interfaz detectada: !target_interface!
    ) else (
        echo ⚠️ No se pudo detectar la interfaz del archivo
        goto :manual_interface
    )
) else (
    echo ⚠️ No se encontró archivo de configuración
    goto :manual_interface
)

goto :restore_config

:manual_interface
echo.
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

:restore_config
echo.

:: Preguntar al usuario si desea continuar
echo ¿Desea restaurar la configuración DHCP en la interfaz "!target_interface!"?
echo.
echo Esta acción:
echo - Restaurará la configuración DHCP automática
echo - Eliminará la IP estática configurada
echo - Restaurará DNS automático
echo.
set /p "confirm=¿Continuar? (S/N): "

if /i not "!confirm!"=="S" (
    echo.
    echo ❌ Restauración cancelada por el usuario
    pause
    exit /b 0
)

echo.

:: Restaurar configuración DHCP
echo 📡 Restaurando configuración DHCP...
echo.

:: Restaurar IP DHCP
netsh interface ip set address "!target_interface!" dhcp
if !errorlevel! equ 0 (
    echo ✅ IP DHCP restaurada exitosamente
) else (
    echo ❌ Error al restaurar IP DHCP
)

:: Restaurar DNS DHCP
netsh interface ip set dns "!target_interface!" dhcp
if !errorlevel! equ 0 (
    echo ✅ DNS DHCP restaurado exitosamente
) else (
    echo ❌ Error al restaurar DNS DHCP
)

echo.

:: Verificar nueva configuración
echo 📊 Verificando nueva configuración...
echo.

for /f "tokens=2 delims=:" %%a in ('netsh interface ip show config "!target_interface!" ^| findstr /i "IP Address"') do (
    set "new_ip=%%a"
    set "new_ip=!new_ip: =!"
)

if defined new_ip (
    echo Nueva IP: !new_ip! (DHCP)
) else (
    echo Nueva IP: Configurando... (DHCP)
)

echo.

:: Verificar conectividad a internet
echo 🔍 Verificando conectividad a internet...
echo.

ping -n 3 8.8.8.8 >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ ¡CONECTIVIDAD A INTERNET EXITOSA!
    echo    La configuración DHCP funciona correctamente
) else (
    echo ⚠️ ADVERTENCIA: No se pudo conectar a internet
    echo    Verifique la configuración de red
)

echo.

:: Mostrar configuración final
echo 📋 CONFIGURACIÓN FINAL:
echo.
echo Interfaz: !target_interface!
echo Configuración: DHCP (Automática)
echo.
echo ✅ La interfaz de red ha sido restaurada a DHCP
echo.

:: Crear archivo de respaldo de la restauración
echo Creando archivo de respaldo...
(
echo # Restauración DHCP para ZKTeco
echo # Generado automáticamente el %date% %time%
echo.
echo INTERFACE=!target_interface!
echo CONFIGURATION=DHCP
echo RESTORED=YES
echo TIMESTAMP=%date% %time%
) > "restauracion_dhcp_%date:~-4,4%%date:~-10,2%%date:~-7,2%.txt"

echo ✅ Archivo de respaldo guardado
echo.

echo 🎉 ¡Restauración completada!
echo    La interfaz de red ha sido restaurada a DHCP
echo.

pause
