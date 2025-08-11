# Script para crear instalador del Sistema de Postulantes
# Desarrollado por Guillermo Recalde a.k.a. 's1mple'
# Versión 1.0

param(
    [string]$InnoSetupPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    [string]$Version = "1.0"
)

Write-Host "🔧 CREANDO INSTALADOR DEL SISTEMA QUIRA" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que Inno Setup esté instalado
if (-not (Test-Path $InnoSetupPath)) {
    Write-Host "❌ ERROR: No se encontró Inno Setup en la ruta especificada" -ForegroundColor Red
    Write-Host "   Ruta buscada: $InnoSetupPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📥 Para instalar Inno Setup:" -ForegroundColor Cyan
    Write-Host "   1. Descarga desde: https://jrsoftware.org/isdl.php" -ForegroundColor White
    Write-Host "   2. Instala en la ruta por defecto" -ForegroundColor White
    Write-Host "   3. O especifica la ruta correcta con: -InnoSetupPath 'tu\ruta\ISCC.exe'" -ForegroundColor White
    exit 1
}

Write-Host "✅ Inno Setup encontrado en: $InnoSetupPath" -ForegroundColor Green

# Verificar que existe la distribución
$DistPath = "dist\Sistema_Postulantes"
if (-not (Test-Path $DistPath)) {
    Write-Host "❌ ERROR: No se encontró la distribución en: $DistPath" -ForegroundColor Red
    Write-Host "   Ejecuta primero: python -m PyInstaller --onedir --name=Sistema_Postulantes --noconsole --icon=quira.ico --add-data='quira.png;.' --add-data='instituto.png;.' --add-data='zkteco_connector_v2.py;.' --add-data='gestion_zkteco.py;.' --hidden-import=zkteco_connector_v2 --hidden-import=gestion_zkteco menu_principal.py" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Distribución encontrada en: $DistPath" -ForegroundColor Green

# Verificar que existe el script de Inno Setup
$ScriptPath = "Sistema_Postulantes_Setup.iss"
if (-not (Test-Path $ScriptPath)) {
    Write-Host "❌ ERROR: No se encontró el script de Inno Setup: $ScriptPath" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Script de Inno Setup encontrado: $ScriptPath" -ForegroundColor Green

# Verificar que existe el icono
$IconPath = "quira.ico"
if (-not (Test-Path $IconPath)) {
    Write-Host "⚠️  ADVERTENCIA: No se encontró el icono: $IconPath" -ForegroundColor Yellow
    Write-Host "   El instalador usará el icono por defecto" -ForegroundColor Yellow
} else {
    Write-Host "✅ Icono encontrado: $IconPath" -ForegroundColor Green
}

Write-Host ""
Write-Host "🚀 Iniciando compilación del instalador..." -ForegroundColor Cyan

# Crear carpeta Output si no existe
$OutputPath = "Output"
if (-not (Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath | Out-Null
    Write-Host "📁 Carpeta Output creada" -ForegroundColor Green
}

# Compilar el instalador
try {
    $Arguments = @(
        $ScriptPath,
        "/DMyAppVersion=$Version"
    )
    
    Write-Host "📦 Ejecutando: $InnoSetupPath $($Arguments -join ' ')" -ForegroundColor Gray
    
    $Process = Start-Process -FilePath $InnoSetupPath -ArgumentList $Arguments -Wait -PassThru -NoNewWindow
    
    if ($Process.ExitCode -eq 0) {
        Write-Host ""
        Write-Host "✅ ¡INSTALADOR CREADO EXITOSAMENTE!" -ForegroundColor Green
        Write-Host "=================================" -ForegroundColor Green
        
        # Buscar el archivo creado
        $InstallerFile = Get-ChildItem -Path $OutputPath -Filter "Sistema_Postulantes_Setup_v$Version.exe" -ErrorAction SilentlyContinue
        
        if ($InstallerFile) {
            $FileSize = [math]::Round($InstallerFile.Length / 1MB, 2)
            Write-Host "📁 Archivo: $($InstallerFile.FullName)" -ForegroundColor White
            Write-Host "📏 Tamaño: $FileSize MB" -ForegroundColor White
            Write-Host "📅 Creado: $($InstallerFile.CreationTime)" -ForegroundColor White
        }
        
        Write-Host ""
        Write-Host "🎯 PRÓXIMOS PASOS:" -ForegroundColor Cyan
        Write-Host "   1. Prueba el instalador en una máquina limpia" -ForegroundColor White
        Write-Host "   2. Verifica que todos los accesos directos funcionen" -ForegroundColor White
        Write-Host "   3. Confirma que la desinstalación sea limpia" -ForegroundColor White
        Write-Host "   4. Distribuye el archivo a tus usuarios" -ForegroundColor White
        
        Write-Host ""
        Write-Host "📋 INFORMACIÓN DEL INSTALADOR:" -ForegroundColor Cyan
        Write-Host "   • Requiere Windows 10 o superior" -ForegroundColor White
        Write-Host "   • Requiere Windows de 64 bits" -ForegroundColor White
        Write-Host "   • Instala en: C:\Program Files\Sistema QUIRA" -ForegroundColor White
        Write-Host "   • Crea accesos directos en Escritorio y Menú Inicio" -ForegroundColor White
        Write-Host "   • Se integra con Panel de Control" -ForegroundColor White
        
    } else {
        Write-Host ""
        Write-Host "❌ ERROR: La compilación falló con código de salida: $($Process.ExitCode)" -ForegroundColor Red
        Write-Host "   Revisa los logs de Inno Setup para más detalles" -ForegroundColor Yellow
        exit 1
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ ERROR: No se pudo ejecutar Inno Setup" -ForegroundColor Red
    Write-Host "   Detalles: $($_.Exception.Message)" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "🎉 ¡PROCESO COMPLETADO!" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Green
