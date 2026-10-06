$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$AppName = "BatchAIDocumentGenerator"

Set-Location $ProjectRoot

Write-Host ""
Write-Host "========================================"
Write-Host " Batch AI Document Generator"
Write-Host "========================================"
Write-Host ""

Write-Host "Cleaning previous build..."

Remove-Item `
    "$ProjectRoot\build" `
    -Recurse `
    -Force `
    -ErrorAction SilentlyContinue

Remove-Item `
    "$ProjectRoot\dist" `
    -Recurse `
    -Force `
    -ErrorAction SilentlyContinue

Remove-Item `
    "$ProjectRoot\$AppName.spec" `
    -Force `
    -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Running tests..."

python -m pytest -q

if ($LASTEXITCODE -ne 0) {
    throw "Tests failed. Build cancelled."
}

Write-Host ""
Write-Host "Tests passed."
Write-Host ""
Write-Host "Building application..."

python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name $AppName `
    --icon "$ProjectRoot\assets\app.ico" `
    --add-data "$ProjectRoot\templates;templates" `
    --add-data "$ProjectRoot\assets;assets" `
    "$ProjectRoot\launcher.py"

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed."
}

$ExePath = Join-Path `
    $ProjectRoot `
    "dist\$AppName\$AppName.exe"

if (-not (Test-Path $ExePath)) {
    throw (
        "Build finished, but executable " +
        "was not found at: $ExePath"
    )
}

Write-Host ""
Write-Host "========================================"
Write-Host " Build completed successfully"
Write-Host "========================================"
Write-Host ""
Write-Host "Executable:"
Write-Host $ExePath
Write-Host ""