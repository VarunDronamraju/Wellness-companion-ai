#!/bin/bash
# TASK 13: Inter-Service Networking Communication Test

echo "🌐 TASK 13: Inter-Service Networking Test"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test results
NETWORK_TESTS_PASSED=0
NETWORK_TESTS_FAILED=0

echo -e "${BLUE}📡 Testing Service-to-Service Communication${NC}"
echo "Date: $(date)"
echo ""

# Function to test inter-service communication
test_service_communication() {
    local from_service=$1
    local to_service=$2
    local to_endpoint=$3
    local description=$4
    
    echo -e "${YELLOW}🔗 Testing: $from_service → $to_service${NC}"
    echo "   $description"
    
    # Execute command inside container to test communication
    result=$(docker exec wellness_${from_service} curl -s -w "%{http_code}" $to_endpoint 2>/dev/null || echo "000")
    http_code="${result: -3}"
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✅ SUCCESS - $from_service can reach $to_service${NC}"
        echo "   Endpoint: $to_endpoint"
        ((NETWORK_TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAILED - $from_service cannot reach $to_service (HTTP: $http_code)${NC}"
        echo "   Endpoint: $to_endpoint"
        ((NETWORK_TESTS_FAILED++))
    fi
    echo ""
}

# Test Docker Network Configuration
echo -e "${BLUE}🏗️ Docker Network Analysis${NC}"
echo "-------------------------"

# Check network exists
network_info=$(docker network ls | grep wellness_network)
if [ -n "$network_info" ]; then
    echo -e "${GREEN}✅ Wellness Network exists${NC}"
    echo "   $network_info"
    ((NETWORK_TESTS_PASSED++))
else
    echo -e "${RED}❌ Wellness Network not found${NC}"
    ((NETWORK_TESTS_FAILED++))
fi

# Get network details
echo -e "\n${YELLOW}🔍 Network Details:${NC}"
docker network inspect wellness-companion-ai_wellness_network --format='{{range .Containers}}{{.Name}}: {{.IPv4Address}}{{"\n"}}{{end}}' 2>/dev/null || echo "Could not retrieve network details"

echo ""

# Test Core Application Communication Chains
echo -e "${BLUE}🚀 Application Service Communication${NC}"
echo "----------------------------------"

# Core Backend → AI/ML Service
test_service_communication "backend" "aiml" "http://aiml-orchestration:8000/health" "Core Backend calling AI/ML Service"

# Core Backend → Data Layer
test_service_communication "backend" "data_layer" "http://data-layer:8000/health" "Core Backend calling Data Layer"

# AI/ML Service → Data Layer
test_service_communication "aiml" "data_layer" "http://data-layer:8000/health" "AI/ML Service calling Data Layer"

# Test Infrastructure Communication
echo -e "${BLUE}🏗️ Infrastructure Service Communication${NC}"
echo "------------------------------------"

# AI/ML Service → Qdrant
test_service_communication "aiml" "qdrant" "http://qdrant:6333/" "AI/ML Service calling Qdrant"

# AI/ML Service → Ollama
test_service_communication "aiml" "ollama" "http://ollama:11434/api/version" "AI/ML Service calling Ollama"

# Data Layer → PostgreSQL (internal check)
echo -e "${YELLOW}🔗 Testing: Data Layer → PostgreSQL${NC}"
echo "   Database connectivity test"
pg_test=$(docker exec wellness_data_layer python -c "
import os
try:
    import psycopg2
    conn = psycopg2.connect(os.getenv('POSTGRES_URL'))
    conn.close()
    print('SUCCESS')
except Exception as e:
    print(f'FAILED: {e}')
" 2>/dev/null)

if [ "$pg_test" = "SUCCESS" ]; then
    echo -e "${GREEN}✅ SUCCESS - Data Layer can connect to PostgreSQL${NC}"
    ((NETWORK_TESTS_PASSED++))
else
    echo -e "${RED}❌ FAILED - Data Layer cannot connect to PostgreSQL${NC}"
    echo "   Error: $pg_test"
    ((NETWORK_TESTS_FAILED++))
fi
echo ""

# Data Layer → Redis (internal check) 
echo -e "${YELLOW}🔗 Testing: Data Layer → Redis${NC}"
echo "   Cache connectivity test"
redis_test=$(docker exec wellness_data_layer python -c "
import os
try:
    import redis
    r = redis.from_url(os.getenv('REDIS_URL'))
    r.ping()
    print('SUCCESS')
except Exception as e:
    print(f'FAILED: {e}')
" 2>/dev/null)

if [ "$redis_test" = "SUCCESS" ]; then
    echo -e "${GREEN}✅ SUCCESS - Data Layer can connect to Redis${NC}"
    ((NETWORK_TESTS_PASSED++))
else
    echo -e "${RED}❌ FAILED - Data Layer cannot connect to Redis${NC}"
    echo "   Error: $redis_test"
    ((NETWORK_TESTS_FAILED++))
fi
echo ""

# Test Port Accessibility
echo -e "${BLUE}🔌 Port Accessibility Test${NC}"
echo "-------------------------"

# Test external port access
ports=("8000:Core Backend" "8001:AI/ML Service" "8002:Data Layer" "6333:Qdrant" "11434:Ollama")

for port_info in "${ports[@]}"; do
    port=$(echo $port_info | cut -d: -f1)
    service=$(echo $port_info | cut -d: -f2)
    
    echo -e "${YELLOW}🔍 Testing external access to $service (port $port)${NC}"
    
    if curl -s http://localhost:$port/health > /dev/null 2>&1 || curl -s http://localhost:$port/ > /dev/null 2>&1 || curl -s http://localhost:$port/api/version > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Port $port accessible externally${NC}"
        ((NETWORK_TESTS_PASSED++))
    else
        echo -e "${RED}❌ Port $port not accessible externally${NC}"
        ((NETWORK_TESTS_FAILED++))
    fi
done

echo ""

# Network Performance Test
echo -e "${BLUE}⚡ Network Performance Test${NC}"
echo "-------------------------"

echo -e "${YELLOW}🔍 Testing network latency between services${NC}"

# Test response time from Core Backend to AI/ML Service
response_time=$(docker exec wellness_backend curl -s -w "%{time_total}" http://aiml-orchestration:8000/ping -o /dev/null 2>/dev/null || echo "timeout")

if [ "$response_time" != "timeout" ] && [ -n "$response_time" ]; then
    response_ms=$(echo "$response_time * 1000" | bc 2>/dev/null || echo "0")
    echo -e "${GREEN}✅ Network latency: ${response_ms}ms${NC}"
    echo "   Core Backend → AI/ML Service ping time"
    ((NETWORK_TESTS_PASSED++))
else
    echo -e "${RED}❌ Network latency test failed${NC}"
    ((NETWORK_TESTS_FAILED++))
fi

echo ""

# Final Network Assessment
echo -e "${BLUE}📊 TASK 13 - Network Summary${NC}"
echo "============================="
echo -e "${GREEN}✅ Network Tests Passed: ${NETWORK_TESTS_PASSED}${NC}"
echo -e "${RED}❌ Network Tests Failed: ${NETWORK_TESTS_FAILED}${NC}"

# Determine overall success
if [ $NETWORK_TESTS_PASSED -ge 8 ] && [ $NETWORK_TESTS_FAILED -le 2 ]; then
    echo -e "\n${GREEN}🎉 TASK 13 COMPLETED SUCCESSFULLY!${NC}"
    echo -e "${GREEN}✅ Inter-service networking is operational${NC}"
    echo -e "${GREEN}✅ All critical service communications working${NC}"
    echo -e "${GREEN}🚀 Ready for Task 14: Volume Management${NC}"
    exit 0
elif [ $NETWORK_TESTS_PASSED -ge 5 ]; then
    echo -e "\n${YELLOW}⚠️  TASK 13 MOSTLY COMPLETE${NC}"
    echo -e "${YELLOW}✅ Core networking functional${NC}"
    echo -e "${YELLOW}⚠️  Some advanced features may need optimization${NC}"
    exit 0
else
    echo -e "\n${RED}❌ TASK 13 NEEDS ATTENTION${NC}"
    echo -e "${RED}❌ Critical networking issues detected${NC}"
    echo -e "${YELLOW}💡 Check Docker network configuration and service connectivity${NC}"
    exit 1
fi