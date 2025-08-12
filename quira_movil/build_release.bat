@echo off
echo ========================================
echo    SILCO Móvil - Build de Release
echo ========================================
echo.

echo [1/4] Limpiando build anterior...
C:\flutter\bin\flutter.bat clean

echo.
echo [2/4] Obteniendo dependencias...
C:\flutter\bin\flutter.bat pub get

echo.
echo [3/4] Generando iconos...
C:\flutter\bin\flutter.bat pub run flutter_launcher_icons:main

echo.
echo [4/4] Compilando APK de release...
C:\flutter\bin\flutter.bat build apk --release

echo.
echo ========================================
echo    ¡Compilación completada!
echo ========================================
echo.
echo APK generado en: build\app\outputs\flutter-apk\app-release.apk
echo Tamaño: 
dir build\app\outputs\flutter-apk\app-release.apk | find "app-release.apk"
echo.
echo Presiona cualquier tecla para salir...
pause > nul
