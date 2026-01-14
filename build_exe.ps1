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
    
    # Create ZIP package
    $version = "v1.3.0"
    $zipName = "PrivacyDashboard_$version.zip"
    $source = "dist\PrivacyDashboard.exe"
    $destination = "dist\$zipName"
    
    Write-Host "Creating release package: $zipName..." -ForegroundColor Cyan
    Compress-Archive -Path $source -DestinationPath $destination -Force
    
    Write-Host "Release package created at: $(Resolve-Path $destination)" -ForegroundColor Green

    # Open explorer to the file
    ii dist
}
else {
    Write-Error "Build Failed!"
    exit 1
}
