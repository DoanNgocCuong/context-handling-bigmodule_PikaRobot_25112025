# PowerShell script to start PostgreSQL and Redis services
# Usage: .\start-services.ps1

Write-Host "🚀 Starting Docker services (PostgreSQL and Redis)..." -ForegroundColor Cyan

# Navigate to src directory
Set-Location $PSScriptRoot

# Start only postgres and redis services
docker-compose up -d postgres redis

Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check service status
Write-Host "`n📊 Service Status:" -ForegroundColor Green
docker ps --filter "name=context_handling" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`n✅ Services started! You can now run:" -ForegroundColor Green
Write-Host "   uvicorn app.main_app:app --reload --host 0.0.0.0 --port 30020" -ForegroundColor Yellow

Write-Host "`n🧪 Test health check:" -ForegroundColor Cyan
Write-Host "   curl http://localhost:30020/v1/health" -ForegroundColor Yellow




