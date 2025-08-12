@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo    SOLUCIONAR IP DUPLICADA Y HOST INACCESIBLE
echo ========================================
echo.
echo Este script solucionará el problema de IP duplicada
echo y "host de destino inaccesible"
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

:: Mostrar estado actual
echo 📊 ESTADO ACTUAL:
echo.
ipconfig | findstr /i "IPv4"
echo.

:: Detectar interfaz con IP duplicada
echo 🔍 DETECTANDO INTERFACES CON IP DUPLICADA...
echo.

:: Buscar todas las interfaces
for /f "tokens=1,2,3,4 delims= " %%a in ('netsh interface show interface ^| findstr /i "conectado"') do (
    set "interface_name=%%d"
    set "interface_admin=%%a"
    set "interface_type=%%b"
    
    if "!interface_type!"=="Ethernet" (
        echo Encontrada interfaz Ethernet: !interface_name!
        set "ethernet_interface=!interface_name!"
    )
    if "!interface_type!"=="Wi-Fi" (
        echo Encontrada interfaz Wi-Fi: !interface_name!
        set "wifi_interface=!interface_name!"
    )
)

echo.

:: Priorizar Ethernet
if defined ethernet_interface (
    set "target_interface=!ethernet_interface!"
) else if defined wifi_interface (
    set "target_interface=!wifi_interface!"
) else (
    echo ❌ No se encontraron interfaces de red
    pause
    exit /b 1
)

echo 🎯 Interfaz seleccionada: !target_interface!
echo.

:: SOLUCIÓN 1: Limpiar configuración de red
echo 🔧 SOLUCIÓN 1: LIMPIANDO CONFIGURACIÓN DE RED...
echo.

echo Liberando IP actual...
netsh interface ip set address "!target_interface!" dhcp
timeout /t 2 /nobreak >nul

echo Liberando DNS actual...
netsh interface ip set dns "!target_interface!" dhcp
timeout /t 2 /nobreak >nul

echo ✅ Configuración DHCP restaurada
echo.

:: SOLUCIÓN 2: Limpiar caché de red
echo 🧹 SOLUCIÓN 2: LIMPIANDO CACHÉ DE RED...
echo.

echo Limpiando tabla ARP...
arp -d *
echo ✅ Tabla ARP limpiada

echo Limpiando caché DNS...
ipconfig /flushdns
echo ✅ Caché DNS limpiado

echo Limpiando caché de rutas...
route /f
echo ✅ Tabla de rutas limpiada

echo.

:: SOLUCIÓN 3: Reiniciar servicios de red
echo 🔄 SOLUCIÓN 3: REINICIANDO SERVICIOS DE RED...
echo.

echo Reiniciando servicio DHCP...
net stop dhcp 2>nul
net start dhcp 2>nul
echo ✅ Servicio DHCP reiniciado

echo Reiniciando servicio DNS...
net stop dnscache 2>nul
net start dnscache 2>nul
echo ✅ Servicio DNS reiniciado

echo.

:: SOLUCIÓN 4: Configurar IP estática correcta
echo 📡 SOLUCIÓN 4: CONFIGURANDO IP ESTÁTICA CORRECTA...
echo.

:: Generar IP única
set "ip_suffix=70"
for /l %%i in (2,1,254) do (
    ping -n 1 192.168.100.%%i >nul 2>&1
    if !errorlevel! neq 0 (
        set "ip_suffix=%%i"
        goto :ip_found
    )
)

:ip_found
set "new_ip=192.168.100.!ip_suffix!"

echo Configurando IP: !new_ip!
echo.

:: Configurar IP estática
netsh interface ip set address "!target_interface!" static !new_ip! 255.255.255.0 192.168.100.1
if !errorlevel! equ 0 (
    echo ✅ IP estática configurada
) else (
    echo ❌ Error al configurar IP estática
)

:: Configurar DNS
netsh interface ip set dns "!target_interface!" static 8.8.8.8
netsh interface ip add dns "!target_interface!" 8.8.4.4 index=2
if !errorlevel! equ 0 (
    echo ✅ DNS configurado
) else (
    echo ❌ Error al configurar DNS
)

echo.

:: SOLUCIÓN 5: Verificar configuración
echo 📋 SOLUCIÓN 5: VERIFICANDO CONFIGURACIÓN...
echo.

echo Configuración actual:
ipconfig | findstr /i "IPv4"
echo.

:: Verificar que solo hay una IP en el rango correcto
set "correct_ip_count=0"
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set "current_ip=%%a"
    set "current_ip=!current_ip: =!"
    
    if "!current_ip!" neq "" (
        echo !current_ip! | findstr /r "^192\.168\.100\." >nul
        if !errorlevel! equ 0 (
            set /a correct_ip_count+=1
            echo ✅ IP correcta encontrada: !current_ip!
        ) else (
            echo ⚠️ IP incorrecta: !current_ip!
        )
    )
)

if !correct_ip_count! equ 1 (
    echo ✅ Solo hay una IP en el rango correcto
) else (
    echo ❌ Hay múltiples IPs o ninguna IP correcta
)

echo.

:: SOLUCIÓN 6: Probar conectividad
echo 🔍 SOLUCIÓN 6: PROBANDO CONECTIVIDAD...
echo.

echo Probando ping al gateway...
ping -n 2 192.168.100.1
if !errorlevel! equ 0 (
    echo ✅ Gateway responde
) else (
    echo ❌ Gateway no responde
)

echo.
echo Probando ping al dispositivo ZKTeco...
ping -n 3 192.168.100.201
if !errorlevel! equ 0 (
    echo.
    echo ✅ ¡PROBLEMA SOLUCIONADO!
    echo    El dispositivo ZKTeco responde correctamente
) else (
    echo.
    echo ❌ El problema persiste
    goto :manual_solutions
)

echo.

:: Mostrar configuración final
echo 📋 CONFIGURACIÓN FINAL:
echo.
ipconfig | findstr /i "IPv4"
echo.

echo 🎉 ¡Proceso completado exitosamente!
echo.

goto :end

:manual_solutions
echo.
echo 📝 SOLUCIONES MANUALES AVANZADAS:
echo.
echo 1. VERIFICAR DISPOSITIVO ZKTECO:
echo    - ¿Está encendido el dispositivo?
echo    - ¿Está conectado el cable de red?
echo    - ¿La IP del dispositivo es realmente 192.168.100.201?
echo    - ¿Hay luces en el puerto de red del dispositivo?
echo.
echo 2. VERIFICAR INFRAESTRUCTURA DE RED:
echo    - ¿Está conectado el cable de red a la computadora?
echo    - ¿Hay un switch/router entre la PC y el dispositivo?
echo    - ¿El switch/router está encendido y funcionando?
echo    - ¿El cable de red está en buen estado?
echo.
echo 3. COMANDOS AVANZADOS PARA EJECUTAR:
echo    - netsh winsock reset
echo    - netsh int ip reset
echo    - ipconfig /release && ipconfig /renew
echo    - arp -a (para ver tabla ARP)
echo    - route print (para ver tabla de rutas)
echo    - tracert 192.168.100.201 (para ver ruta)
echo.
echo 4. SOLUCIONES DE ÚLTIMO RECURSO:
echo    - Reinicie el dispositivo ZKTeco
echo    - Reinicie el switch/router
echo    - Cambie el cable de red
echo    - Configure una IP diferente en el dispositivo
echo    - Desactive temporalmente el firewall
echo.

:end
pause
