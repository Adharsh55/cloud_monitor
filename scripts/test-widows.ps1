Write-Host "Testing Cloud Monitoring System..." -ForegroundColor Cyan
Write-Host ""

# Function to test service
function Test-Service {
    param(
        [string]$Name,
        [string]$Url
    )
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 10
        Write-Host "[PASS] $Name ($Url)" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "[FAIL] $Name ($Url)" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Yellow
        return $false
    }
}

# Test services
$services = @(
    @{Name = "Grafana"; Url = "http://localhost:3000"},
    @{Name = "Prometheus"; Url = "http://localhost:9090"},
    @{Name = "Elasticsearch"; Url = "http://localhost:9200"},
    @{Name = "Node.js App"; Url = "http://localhost:3001"},
    @{Name = "Python App"; Url = "http://localhost:5001"}
)

$allPassed = $true
foreach ($service in $services) {
    if (-not (Test-Service -Name $service.Name -Url $service.Url)) {
        $allPassed = $false
    }
}

Write-Host ""
Write-Host "Container Status:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "Recent Logs:" -ForegroundColor Cyan
docker-compose logs --tail=10

Write-Host ""
if ($allPassed) {
    Write-Host "✅ All tests passed! System is running correctly." -ForegroundColor Green
    
    Write-Host @"
    
    Next Steps:
    1. Open Grafana: http://localhost:3000 (admin/admin123)
    2. Add Prometheus as data source
    3. Import dashboard from /grafana/dashboards/
    4. Generate logs by accessing:
       - Node.js App: http://localhost:3001/api/error
       - Python App: http://localhost:5001/api/error
    5. Check alerts in Prometheus: http://localhost:9090/alerts
    "@ -ForegroundColor Cyan
}
else {
    Write-Host "❌ Some tests failed. Check Docker logs:" -ForegroundColor Red
    Write-Host "docker-compose logs -f" -ForegroundColor Yellow
}