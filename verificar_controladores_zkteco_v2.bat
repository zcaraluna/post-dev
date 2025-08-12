@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo    VERIFICAR CONTROLADORES ZKTECO V2
echo ========================================
echo.
echo Este script verificará los controladores necesarios
echo para el dispositivo ZKTeco K40 (Windows 11 compatible)
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

:: Verificar controladores de red (método moderno)
echo 🔍 VERIFICANDO CONTROLADORES DE RED...
echo.

echo Controladores de tarjeta de red instalados:
Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Format-Table Name, InterfaceDescription, Status -AutoSize
echo.

:: Verificar servicios de red
echo 🔍 VERIFICANDO SERVICIOS DE RED...
echo.

echo Estado de servicios críticos:
Get-Service -Name "Tcpip", "Dhcp", "Dnscache" | Format-Table Name, Status, StartType -AutoSize
echo.

:: Verificar configuración de red
echo 🔍 VERIFICANDO CONFIGURACIÓN DE RED...
echo.

echo Configuración IP actual:
Get-NetIPAddress | Where-Object {$_.AddressFamily -eq "IPv4"} | Format-Table IPAddress, InterfaceAlias, PrefixLength -AutoSize
echo.

:: Verificar interfaces de red
echo 🔍 VERIFICANDO INTERFACES DE RED...
echo.

echo Interfaces de red activas:
Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Format-Table Name, InterfaceDescription, Status, LinkSpeed -AutoSize
echo.

:: Verificar dispositivos de red
echo 🔍 BUSCANDO DISPOSITIVOS DE RED...
echo.

echo Dispositivos en la red 192.168.100.x:
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
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*ZKTeco*" -or $_.DisplayName -like "*4370*"} | Format-Table DisplayName, Enabled, Direction, Action -AutoSize
echo.

:: Crear regla de firewall si no existe
echo 🧠 CONFIGURANDO FIREWALL PARA ZKTECO...
echo.

echo Creando regla de firewall para ZKTeco...
New-NetFirewallRule -DisplayName "ZKTeco K40 UDP In" -Direction Inbound -Protocol UDP -LocalPort 4370 -Action Allow -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "ZKTeco K40 UDP Out" -Direction Outbound -Protocol UDP -RemotePort 4370 -Action Allow -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "ZKTeco K40 TCP In" -Direction Inbound -Protocol TCP -LocalPort 4370 -Action Allow -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "ZKTeco K40 TCP Out" -Direction Outbound -Protocol TCP -RemotePort 4370 -Action Allow -ErrorAction SilentlyContinue
echo ✅ Reglas de firewall creadas
echo.

:: Verificar controladores específicos
echo 🔍 VERIFICANDO CONTROLADORES ESPECÍFICOS...
echo.

echo Controladores de dispositivos biométricos:
Get-PnpDevice | Where-Object {$_.FriendlyName -like "*biometric*" -or $_.FriendlyName -like "*fingerprint*" -or $_.FriendlyName -like "*zk*"} | Format-Table FriendlyName, Status, Class -AutoSize
echo.

:: Verificar dispositivos USB
echo 🔍 VERIFICANDO DISPOSITIVOS USB...
echo.

echo Dispositivos USB conectados:
Get-PnpDevice | Where-Object {$_.Class -eq "USB"} | Format-Table FriendlyName, Status, InstanceId -AutoSize
echo.

:: Verificar conectividad
echo 🔍 VERIFICANDO CONECTIVIDAD...
echo.

echo Probando conectividad al dispositivo ZKTeco...
ping -n 3 192.168.100.201
if !errorlevel! equ 0 (
    echo ✅ Dispositivo responde correctamente
) else (
    echo ❌ Dispositivo no responde
)
echo.

:: Verificar configuración de red específica
echo 🔍 VERIFICANDO CONFIGURACIÓN ESPECÍFICA...
echo.

echo Configuración de red para ZKTeco:
Get-NetIPAddress | Where-Object {$_.IPAddress -like "192.168.100.*"} | Format-Table IPAddress, InterfaceAlias, PrefixLength -AutoSize
echo.

echo Gateway configurado:
Get-NetRoute | Where-Object {$_.DestinationPrefix -eq "0.0.0.0/0"} | Format-Table DestinationPrefix, NextHop, InterfaceAlias -AutoSize
echo.

:: Mostrar información de controladores
echo 📋 INFORMACIÓN DE CONTROLADORES:
echo.

echo Controladores de red principales:
Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | ForEach-Object {
    $adapter = $_
    $driver = Get-PnpDevice | Where-Object {$_.InstanceId -eq $adapter.PnPDeviceID}
    [PSCustomObject]@{
        Name = $adapter.Name
        Description = $adapter.InterfaceDescription
        Status = $adapter.Status
        Driver = $driver.FriendlyName
    }
} | Format-Table -AutoSize
echo.

:: Crear reporte de controladores
echo 📄 Generando reporte de controladores...
(
echo ========================================
echo    REPORTE DE CONTROLADORES ZKTECO V2
echo ========================================
echo Fecha: %date% %time%
echo.
echo CONTROLADORES DE RED:
Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Format-Table Name, InterfaceDescription, Status -AutoSize
echo.
echo SERVICIOS DE RED:
Get-Service -Name "Tcpip", "Dhcp", "Dnscache" | Format-Table Name, Status, StartType -AutoSize
echo.
echo CONFIGURACIÓN IP:
Get-NetIPAddress | Where-Object {$_.AddressFamily -eq "IPv4"} | Format-Table IPAddress, InterfaceAlias, PrefixLength -AutoSize
echo.
echo REGLAS DE FIREWALL:
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*ZKTeco*" -or $_.DisplayName -like "*4370*"} | Format-Table DisplayName, Enabled, Direction, Action -AutoSize
echo.
echo PUERTOS ACTIVOS:
netstat -an | findstr ":4370"
echo.
echo CONECTIVIDAD:
ping -n 1 192.168.100.201
echo.
echo ========================================
) > "reporte_controladores_zkteco_v2_%date:~-4,4%%date:~-10,2%%date:~-7,2%.txt"

echo ✅ Reporte guardado: reporte_controladores_zkteco_v2_%date:~-4,4%%date:~-10,2%%date:~-7,2%.txt
echo.

:: Instrucciones adicionales
echo 📝 INSTRUCCIONES ADICIONALES:
echo.
echo 1. CONTROLADORES ZKTECO:
echo    - El dispositivo ZKTeco K40 NO requiere controladores especiales
echo    - Se comunica por protocolos de red estándar (UDP/TCP)
echo    - Solo necesita conectividad de red básica
echo.
echo 2. SI EL PROBLEMA PERSISTE:
echo    - Verifique que el dispositivo esté encendido
echo    - Verifique la conexión de cable de red
echo    - Reinicie el dispositivo ZKTeco
echo    - Verifique la IP del dispositivo (192.168.100.201)
echo.
echo 3. VERIFICACIÓN MANUAL:
echo    - Abra "Administrador de dispositivos"
echo    - Verifique que no hay dispositivos con signo de exclamación
echo    - Verifique que la tarjeta de red funciona correctamente
echo    - Verifique que los servicios de red están activos
echo.
echo 4. COMANDOS ÚTILES:
echo    - Get-NetAdapter (ver interfaces de red)
echo    - Get-NetIPAddress (ver configuración IP)
echo    - Get-NetFirewallRule (ver reglas de firewall)
echo    - Get-PnpDevice (ver dispositivos)
echo.

echo 🎯 VERIFICACIÓN DE CONTROLADORES COMPLETADA
echo    Revise el reporte generado para más detalles
echo.

pause
