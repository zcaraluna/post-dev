@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo    SOLUCIONAR "HOST INACCESIBLE"
echo ========================================
echo.
echo Este script solucionará el problema de
echo "host de destino inaccesible" al hacer ping
echo al dispositivo ZKTeco 192.168.100.201
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
echo Configuración IP actual:
ipconfig | findstr /i "IPv4"
echo.

:: Verificar si estamos en el rango correcto
set "in_correct_range=false"
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set "current_ip=%%a"
    set "current_ip=!current_ip: =!"
    
    if "!current_ip!" neq "" (
        echo !current_ip! | findstr /r "^192\.168\.100\." >nul
        if !errorlevel! equ 0 (
            set "in_correct_range=true"
            echo ✅ IP en rango correcto: !current_ip!
        ) else (
            echo ❌ IP NO en rango correcto: !current_ip!
        )
    )
)

echo.

:: Si no está en el rango correcto, configurar automáticamente
if "!in_correct_range!"=="false" (
    echo 🔧 CONFIGURANDO RED AUTOMÁTICAMENTE...
    echo.
    
    :: Detectar interfaz activa
    for /f "tokens=1,2,3,4 delims= " %%a in ('netsh interface show interface ^| findstr /i "conectado"') do (
        set "interface_name=%%d"
        set "interface_admin=%%a"
        set "interface_type=%%b"
        
        if "!interface_type!"=="Ethernet" (
            set "target_interface=!interface_name!"
            goto :configure_network
        )
        if "!interface_type!"=="Wi-Fi" (
            set "target_interface=!interface_name!"
            goto :configure_network
        )
    )
    
    :configure_network
    if defined target_interface (
        echo 🎯 Configurando interfaz: !target_interface!
        
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
        
        echo 📡 Configurando IP: !new_ip!
        
        :: Configurar IP estática
        netsh interface ip set address "!target_interface!" static !new_ip! 255.255.255.0 192.168.100.1
        netsh interface ip set dns "!target_interface!" static 8.8.8.8
        netsh interface ip add dns "!target_interface!" 8.8.4.4 index=2
        
        echo ✅ Red configurada automáticamente
    ) else (
        echo ❌ No se pudo detectar interfaz de red
        goto :manual_solutions
    )
) else (
    echo ✅ La IP ya está en el rango correcto
)

echo.

:: Limpiar tabla ARP y caché DNS
echo 🧹 LIMPIANDO CACHÉ DE RED...
echo.

echo Limpiando tabla ARP...
arp -d *
if !errorlevel! equ 0 (
    echo ✅ Tabla ARP limpiada
) else (
    echo ⚠️ No se pudo limpiar tabla ARP
)

echo Limpiando caché DNS...
ipconfig /flushdns
if !errorlevel! equ 0 (
    echo ✅ Caché DNS limpiado
) else (
    echo ⚠️ No se pudo limpiar caché DNS
)

echo.

:: Reiniciar tarjeta de red
echo 🔄 REINICIANDO TARJETA DE RED...
echo.

:: Detectar interfaz activa
for /f "tokens=1,2,3,4 delims= " %%a in ('netsh interface show interface ^| findstr /i "conectado"') do (
    set "interface_name=%%d"
    set "interface_admin=%%a"
    set "interface_type=%%b"
    
    if "!interface_type!"=="Ethernet" (
        set "target_interface=!interface_name!"
        goto :restart_interface
    )
    if "!interface_type!"=="Wi-Fi" (
        set "target_interface=!interface_name!"
        goto :restart_interface
    )
)

:restart_interface
if defined target_interface (
    echo Reiniciando interfaz: !target_interface!
    
    :: Deshabilitar interfaz
    netsh interface set interface "!target_interface!" admin=disable
    timeout /t 3 /nobreak >nul
    
    :: Habilitar interfaz
    netsh interface set interface "!target_interface!" admin=enable
    timeout /t 5 /nobreak >nul
    
    echo ✅ Interfaz reiniciada
) else (
    echo ❌ No se pudo detectar interfaz para reiniciar
)

echo.

:: Verificar conectividad
echo 🔍 VERIFICANDO CONECTIVIDAD...
echo.

echo Probando ping al dispositivo ZKTeco...
ping -n 3 192.168.100.201
if !errorlevel! equ 0 (
    echo.
    echo ✅ ¡PROBLEMA SOLUCIONADO!
    echo    El dispositivo ZKTeco ahora responde correctamente
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

echo 🎉 ¡Proceso completado!
echo    Si el problema persiste, revise las soluciones manuales
echo.

goto :end

:manual_solutions
echo.
echo 📝 SOLUCIONES MANUALES SI EL PROBLEMA PERSISTE:
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
echo 3. VERIFICAR CONFIGURACIÓN DE RED:
echo    - Ejecute: ipconfig /all (para ver configuración completa)
echo    - Verifique que la máscara sea 255.255.255.0
echo    - Verifique que el gateway sea 192.168.100.1
echo    - Verifique que no haya conflictos de IP
echo.
echo 4. PRUEBAS ADICIONALES:
echo    - Ejecute: arp -a (para ver tabla ARP)
echo    - Ejecute: route print (para ver tabla de rutas)
echo    - Ejecute: tracert 192.168.100.201 (para ver ruta)
echo.
echo 5. SOLUCIONES AVANZADAS:
echo    - Reinicie el dispositivo ZKTeco
echo    - Reinicie el switch/router
echo    - Cambie el cable de red
echo    - Configure una IP diferente en el dispositivo
echo.
echo 6. COMANDOS ÚTILES:
echo    - ipconfig /release && ipconfig /renew
echo    - netsh winsock reset
echo    - netsh int ip reset
echo.

:end
pause
