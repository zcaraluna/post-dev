@echo off
cd /d "%~dp0"
call zkteco_env\Scripts\activate.bat
python main_integrado.py
pause
