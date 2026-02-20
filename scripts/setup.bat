@echo off
echo Setting up Cloud Log Monitoring System on Windows...
echo.

REM Create directories
mkdir prometheus 2>nul
mkdir grafana\provisioning\datasources 2>nul
mkdir grafana\provisioning\dashboards 2>nul
mkdir elasticsearch 2>nul
mkdir logstash\pipeline 2>nul
mkdir alertmanager 2>nul
mkdir node-app\logs 2>nul
mkdir python-app\logs 2>nul
mkdir jenkins 2>nul
mkdir scripts 2>nul

echo Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not installed. Please install Docker Desktop from:
    echo https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

echo Checking Docker Compose installation...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker Compose is not installed. Please install it.
    pause
    exit /b 1
)

echo Starting Docker services...
docker-compose up -d

echo Waiting for services to start...
timeout /t 30 /nobreak >nul

echo.
echo Checking service status...
echo.

setlocal enabledelayedexpansion

set services[0]=elasticsearch:9200
set services[1]=prometheus:9090
set services[2]=grafana:3000
set services[3]=node-app:3001
set services[4]=python-app:5001

set index=0
:loop
if defined services[!index!] (
    set service=!services[%index%]!
    
    powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://!service!' -Method Head -TimeoutSec 5; exit 0 } catch { exit 1 }" >nul 2>&1
    
    if !errorlevel! equ 0 (
        echo [OK] !service! is up
    ) else (
        echo [ERROR] !service! is down
    )
    
    set /a index+=1
    goto loop
)

echo.
echo ==========================================
echo Cloud Log Monitoring System Setup Complete
echo ==========================================
echo.
echo Access URLs:
echo Grafana Dashboard: http://localhost:3000
echo   Username: admin
echo   Password: admin123
echo.
echo Prometheus: http://localhost:9090
echo Elasticsearch: http://localhost:9200
echo Kibana: http://localhost:5601
echo Node.js App: http://localhost:3001
echo Python App: http://localhost:5001
echo Jenkins: http://localhost:8080
echo.
echo To view logs: docker-compose logs -f
echo To stop services: docker-compose down
echo ==========================================
echo.
pause