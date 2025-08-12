# Script para actualizar requirements.txt
# Ejecutar como: PowerShell -ExecutionPolicy Bypass -File actualizar_requirements.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    ACTUALIZAR REQUIREMENTS.TXT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Este script actualizará el archivo requirements.txt" -ForegroundColor White
Write-Host "con las versiones actuales de las dependencias" -ForegroundColor White
Write-Host ""

# Verificar si existe el entorno virtual
if (-not (Test-Path "zkteco_env")) {
    Write-Host "❌ ERROR: No se encontró el entorno virtual 'zkteco_env'" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor:" -ForegroundColor Yellow
    Write-Host "1. Asegúrese de estar en el directorio correcto" -ForegroundColor Yellow
    Write-Host "2. Active el entorno virtual: zkteco_env\Scripts\activate" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Presione Enter para continuar"
    exit 1
}

Write-Host "✅ Entorno virtual encontrado" -ForegroundColor Green
Write-Host ""

# Activar entorno virtual
Write-Host "🔧 Activando entorno virtual..." -ForegroundColor Yellow
& "zkteco_env\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al activar el entorno virtual" -ForegroundColor Red
    Read-Host "Presione Enter para continuar"
    exit 1
}

Write-Host "✅ Entorno virtual activado" -ForegroundColor Green
Write-Host ""

# Leer requirements.txt actual
Write-Host "📖 Leyendo requirements.txt actual..." -ForegroundColor Yellow
$currentRequirements = @()
if (Test-Path "requirements.txt") {
    $currentRequirements = Get-Content "requirements.txt" | Where-Object { $_.Trim() -ne "" }
}

Write-Host "✅ Requirements actual leído" -ForegroundColor Green
Write-Host ""

# Generar requirements.txt actualizado
Write-Host "📦 Generando requirements.txt actualizado..." -ForegroundColor Yellow
$updatedRequirements = & pip freeze
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al generar requirements.txt" -ForegroundColor Red
    Read-Host "Presione Enter para continuar"
    exit 1
}

Write-Host "✅ Archivo requirements_actualizado.txt generado" -ForegroundColor Green
Write-Host ""

# Filtrar solo las dependencias principales del proyecto
Write-Host "🔍 Filtrando dependencias principales..." -ForegroundColor Yellow

# Dependencias principales del proyecto QUIRA
$mainDependencies = @(
    "pyzk",
    "tkinter-tooltip", 
    "Pillow",
    "psycopg2-binary",
    "bcrypt",
    "numpy"
)

$filteredRequirements = @()
foreach ($req in $updatedRequirements) {
    $packageName = ($req -split "==")[0]
    if ($mainDependencies -contains $packageName) {
        $filteredRequirements += $req
    }
}

# Agregar dependencias que puedan faltar
foreach ($dep in $mainDependencies) {
    $found = $false
    foreach ($req in $filteredRequirements) {
        if ($req.StartsWith($dep)) {
            $found = $true
            break
        }
    }
    if (-not $found) {
        Write-Host "⚠️ Dependencia '$dep' no encontrada en pip freeze" -ForegroundColor Yellow
    }
}

Write-Host "✅ Dependencias filtradas" -ForegroundColor Green
Write-Host ""

# Mostrar diferencias
Write-Host "🔍 Mostrando diferencias..." -ForegroundColor Yellow
Write-Host ""

Write-Host "Archivo actual (requirements.txt):" -ForegroundColor Cyan
foreach ($req in $currentRequirements) {
    Write-Host "  $req" -ForegroundColor White
}
Write-Host ""

Write-Host "Archivo actualizado (requirements_actualizado.txt):" -ForegroundColor Cyan
foreach ($req in $filteredRequirements) {
    Write-Host "  $req" -ForegroundColor White
}
Write-Host ""

# Preguntar si actualizar
$actualizar = Read-Host "¿Desea actualizar requirements.txt? (s/n)"
if ($actualizar -eq "s" -or $actualizar -eq "S") {
    Write-Host ""
    Write-Host "🔄 Actualizando requirements.txt..." -ForegroundColor Yellow
    
    # Crear backup del archivo actual
    if (Test-Path "requirements.txt") {
        Copy-Item "requirements.txt" "requirements.txt.backup"
        Write-Host "✅ Backup creado: requirements.txt.backup" -ForegroundColor Green
    }
    
    # Escribir nuevo requirements.txt
    $filteredRequirements | Out-File -FilePath "requirements.txt" -Encoding UTF8
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ requirements.txt actualizado correctamente" -ForegroundColor Green
    } else {
        Write-Host "❌ Error al actualizar requirements.txt" -ForegroundColor Red
    }
} else {
    Write-Host ""
    Write-Host "ℹ️ No se actualizó requirements.txt" -ForegroundColor Yellow
    Write-Host "El archivo requirements_actualizado.txt está disponible para revisión" -ForegroundColor Yellow
}

Write-Host ""

# Mostrar información adicional
Write-Host "📋 Información adicional:" -ForegroundColor Cyan
Write-Host ""

# Verificar versiones específicas
Write-Host "Versiones de dependencias principales:" -ForegroundColor Yellow
foreach ($dep in $mainDependencies) {
    $version = & pip show $dep 2>$null | Select-String "Version:"
    if ($version) {
        $ver = ($version -split ": ")[1]
        Write-Host "  $dep : $ver" -ForegroundColor White
    } else {
        Write-Host "  $dep : No instalado" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎯 Proceso completado" -ForegroundColor Green
Write-Host ""

Read-Host "Presione Enter para continuar"
