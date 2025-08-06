Write-Host "Activando entorno virtual ZKTeco..." -ForegroundColor Green
& ".\zkteco_env\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Entorno virtual activado! Ahora puedes ejecutar:" -ForegroundColor Yellow
Write-Host "  python gui_app.py          - Para la interfaz grafica" -ForegroundColor Cyan
Write-Host "  python simple_connector.py - Para la linea de comandos" -ForegroundColor Cyan
Write-Host "" 