# HTI Experiment Platform - Startup Script
# Run this to start the experiment server

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "🧠 HTI EXPERIMENT PLATFORM" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if Python is available
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "❌ Python not found. Please install Python 3.8+`n" -ForegroundColor Red
    exit 1
}

$pythonVersion = python --version 2>&1
Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green

# Check if required packages are installed
Write-Host "`nChecking dependencies..." -ForegroundColor Yellow
$flaskInstalled = python -c "import flask" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Flask not installed. Installing dependencies...`n" -ForegroundColor Red
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n❌ Failed to install dependencies. Please check requirements.txt`n" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ All dependencies installed" -ForegroundColor Green

# Ensure data directory exists
if (-not (Test-Path "data")) {
    New-Item -ItemType Directory -Path "data" | Out-Null
    Write-Host "✅ Created data directory" -ForegroundColor Green
}

# Display information
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "📋 EXPERIMENT INFO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Server will start at: http://localhost:5000" -ForegroundColor White
Write-Host "Data will be saved to: data/results.csv" -ForegroundColor White
Write-Host "`nTo stop the server: Press Ctrl+C`n" -ForegroundColor Yellow

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 STARTING SERVER..." -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Start the Flask app
python app.py
