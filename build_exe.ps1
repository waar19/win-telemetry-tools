Write-Host "Building Windows Privacy Dashboard..." -ForegroundColor Cyan

# Check if PyInstaller is installed
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Clean previous builds
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }

# Build
Write-Host "Running PyInstaller..." -ForegroundColor Cyan
pyinstaller privacy_dashboard.spec

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nBuild Successful!" -ForegroundColor Green
    Write-Host "Executable is located at: $(Resolve-Path dist\PrivacyDashboard.exe)" -ForegroundColor Green
    
    # Open explorer to the file
    ii dist
} else {
    Write-Error "Build Failed!"
    exit 1
}
