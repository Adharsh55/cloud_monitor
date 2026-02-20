#!/bin/bash

echo "Setting up Cloud Log Monitoring System..."

# Create directories
mkdir -p prometheus grafana/provisioning/datasources grafana/provisioning/dashboards
mkdir -p elasticsearch logstash/pipeline alertmanager
mkdir -p node-app/logs python-app/logs jenkins scripts

# Create necessary files
touch prometheus/prometheus.yml prometheus/alert_rules.yml
touch grafana/provisioning/datasources/datasource.yml
touch logstash/pipeline/logstash.conf
touch alertmanager/alertmanager.yml

# Install dependencies
echo "Installing required tools..."
sudo apt-get update
sudo apt-get install -y docker.io docker-compose curl wget

# Start Docker services
sudo systemctl start docker
sudo systemctl enable docker

# Build and start services
echo "Building and starting services..."
docker-compose up -d

echo "Waiting for services to start..."
sleep 30

# Check service status
echo "Checking service status..."
services=("elasticsearch:9200" "prometheus:9090" "grafana:3000" "node-app:3001" "python-app:5001")

for service in "${services[@]}"; do
    if curl -f http://$service > /dev/null 2>&1; then
        echo "✅ $service is up"
    else
        echo "❌ $service is down"
    fi
done

echo ""
echo "=========================================="
echo "Cloud Log Monitoring System Setup Complete"
echo "=========================================="
echo ""
echo "Access URLs:"
echo "Grafana Dashboard: http://localhost:3000"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "Prometheus: http://localhost:9090"
echo "Elasticsearch: http://localhost:9200"
echo "Kibana: http://localhost:5601"
echo "Node.js App: http://localhost:3001"
echo "Python App: http://localhost:5001"
echo "Jenkins: http://localhost:8080"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop services: docker-compose down"
echo "=========================================="