@echo off
echo Activando entorno virtual ZKTeco...
call zkteco_env\Scripts\activate.bat
echo.
echo Entorno virtual activado! Ahora puedes ejecutar:
echo   python gui_app.py          - Para la interfaz grafica
echo   python simple_connector.py - Para la linea de comandos
echo.
cmd /k 