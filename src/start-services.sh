#!/bin/bash
# Bash script to start PostgreSQL and Redis services
# Usage: ./start-services.sh

echo "🚀 Starting Docker services (PostgreSQL and Redis)..."

# Navigate to script directory
cd "$(dirname "$0")"

# Start only postgres and redis services
docker-compose up -d postgres redis

echo "⏳ Waiting for services to be ready..."
sleep 5

# Check service status
echo ""
echo "📊 Service Status:"
docker ps --filter "name=context_handling" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "✅ Services started! You can now run:"
echo "   uvicorn app.main_app:app --reload --host 0.0.0.0 --port 30020"

echo ""
echo "🧪 Test health check:"
echo "   curl http://localhost:30020/v1/health"



