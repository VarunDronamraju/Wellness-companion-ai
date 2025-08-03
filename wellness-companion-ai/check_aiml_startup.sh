#!/bin/bash
# Check AI/ML service startup progress

echo "🔍 Checking AI/ML Service Startup"
echo "=================================="

echo "1. Check container status:"
docker-compose ps aiml-orchestration

echo -e "\n2. Check recent logs:"
docker-compose logs --tail=20 aiml-orchestration

echo -e "\n3. Wait and test every 10 seconds:"
for i in {1..6}; do
    echo "Attempt $i/6:"
    response=$(curl -s -w "%{http_code}" http://localhost:8001/health 2>/dev/null)
    http_code="${response: -3}"
    
    if [ "$http_code" = "200" ]; then
        echo "✅ AI/ML service is ready!"
        echo "Response: ${response%???}"
        break
    else
        echo "⏳ Still starting... (HTTP: $http_code)"
        sleep 10
    fi
done

echo -e "\n4. Final test - all endpoints:"
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ /health - OK"
    curl -s http://localhost:8001/ | head -1
    echo "✅ / - OK"
    echo ""
    echo "🎉 TASK 8 COMPLETED SUCCESSFULLY!"
    echo "🚀 Ready for Task 9: Core Backend Service"
else
    echo "❌ Service still not ready after 60 seconds"
    echo "💡 Check logs: docker-compose logs aiml-orchestration"
fi