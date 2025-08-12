@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo    ACTUALIZAR REQUIREMENTS.TXT
echo ========================================
echo.
echo Este script actualizará el archivo requirements.txt
echo con las versiones actuales de las dependencias
echo.

:: Verificar si existe el entorno virtual
if not exist "zkteco_env" (
    echo ❌ ERROR: No se encontró el entorno virtual 'zkteco_env'
    echo.
    echo Por favor:
    echo 1. Asegúrese de estar en el directorio correcto
    echo 2. Active el entorno virtual: zkteco_env\Scripts\activate
    echo.
    pause
    exit /b 1
)

echo ✅ Entorno virtual encontrado
echo.

:: Activar entorno virtual
echo 🔧 Activando entorno virtual...
call zkteco_env\Scripts\activate.bat
if !errorlevel! neq 0 (
    echo ❌ Error al activar el entorno virtual
    pause
    exit /b 1
)

echo ✅ Entorno virtual activado
echo.

:: Generar requirements.txt actualizado
echo 📦 Generando requirements.txt actualizado...
pip freeze > requirements_actualizado.txt
if !errorlevel! neq 0 (
    echo ❌ Error al generar requirements.txt
    pause
    exit /b 1
)

echo ✅ Archivo requirements_actualizado.txt generado
echo.

:: Mostrar diferencias
echo 🔍 Mostrando diferencias con el archivo actual...
echo.

echo Archivo actual (requirements.txt):
type requirements.txt
echo.

echo Archivo actualizado (requirements_actualizado.txt):
type requirements_actualizado.txt
echo.

:: Preguntar si actualizar
echo.
set /p "actualizar=¿Desea actualizar requirements.txt? (s/n): "
if /i "!actualizar!"=="s" (
    echo.
    echo 🔄 Actualizando requirements.txt...
    copy requirements_actualizado.txt requirements.txt >nul
    if !errorlevel! equ 0 (
        echo ✅ requirements.txt actualizado correctamente
    ) else (
        echo ❌ Error al actualizar requirements.txt
    )
) else (
    echo.
    echo ℹ️ No se actualizó requirements.txt
    echo El archivo requirements_actualizado.txt está disponible para revisión
)

echo.

:: Limpiar archivo temporal
del requirements_actualizado.txt >nul 2>&1

echo 🎯 Proceso completado
echo.

pause
