Write-Host "Setting up Cloud Log Monitoring System on Windows..." -ForegroundColor Green
Write-Host ""

# Create directories
$directories = @(
    "prometheus",
    "grafana\provisioning\datasources",
    "grafana\provisioning\dashboards",
    "elasticsearch",
    "logstash\pipeline",
    "alertmanager",
    "node-app\logs",
    "python-app\logs",
    "jenkins",
    "scripts"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created directory: $dir"
    }
}

# Check Docker installation
try {
    $dockerVersion = docker --version
    Write-Host "Docker installed: $dockerVersion" -ForegroundColor Green
}
catch {
    Write-Host "Docker is not installed!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Docker Compose
try {
    $composeVersion = docker-compose --version
    Write-Host "Docker Compose installed: $composeVersion" -ForegroundColor Green
}
catch {
    Write-Host "Docker Compose is not installed!" -ForegroundColor Red
    Write-Host "Docker Compose usually comes with Docker Desktop. Please ensure it's installed." -ForegroundColor Yellow
}

# Start Docker services
Write-Host "`nStarting Docker services..." -ForegroundColor Cyan
docker-compose up -d

Write-Host "Waiting for services to start (30 seconds)..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

# Check service status
Write-Host "`nChecking service status..." -ForegroundColor Cyan

$services = @(
    @{Name = "Elasticsearch"; Url = "http://localhost:9200"},
    @{Name = "Prometheus"; Url = "http://localhost:9090"},
    @{Name = "Grafana"; Url = "http://localhost:3000"},
    @{Name = "Node.js App"; Url = "http://localhost:3001"},
    @{Name = "Python App"; Url = "http://localhost:5001"},
    @{Name = "Jenkins"; Url = "http://localhost:8080"}
)

foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri $service.Url -Method Head -TimeoutSec 5 -ErrorAction Stop
        Write-Host "[✓] $($service.Name) ($($service.Url))" -ForegroundColor Green
    }
    catch {
        Write-Host "[✗] $($service.Name) ($($service.Url))" -ForegroundColor Red
    }
}

# Display access information
Write-Host @"

==========================================
Cloud Log Monitoring System Setup Complete
==========================================

Access URLs:
1. Grafana Dashboard: http://localhost:3000
   - Username: admin
   - Password: admin123

2. Prometheus Metrics: http://localhost:9090

3. Elasticsearch: http://localhost:9200

4. Kibana UI: http://localhost:5601

5. Node.js App: http://localhost:3001

6. Python App: http://localhost:5001

7. Jenkins CI/CD: http://localhost:8080

Useful Commands:
- View all logs: docker-compose logs -f
- View specific service logs: docker-compose logs -f [service_name]
- Stop all services: docker-compose down
- Restart services: docker-compose restart
- Rebuild and restart: docker-compose up -d --build

To test the system:
1. Access Grafana at http://localhost:3000
2. Login with admin/admin123
3. Import the dashboard from /grafana/dashboards/
4. Access the Node.js and Python apps to generate logs
5. Check alerts in Prometheus: http://localhost:9090/alerts

==========================================
"@ -ForegroundColor Cyan

Read-Host "`nPress Enter to continue..."