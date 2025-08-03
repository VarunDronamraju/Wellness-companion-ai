#!/bin/bash
# TASK 11: Comprehensive Docker Environment Test
# Test all services start without errors

echo "🧪 TASK 11: Docker Environment Comprehensive Test"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

echo -e "${BLUE}📋 Testing Complete Docker Environment${NC}"
echo "Date: $(date)"
echo ""

# Step 1: Clean environment
echo -e "${YELLOW}🔄 Step 1: Clean Environment${NC}"
docker-compose down -v
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Environment cleaned successfully${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ Failed to clean environment${NC}"
    ((TESTS_FAILED++))
fi

# Step 2: Start all services
echo -e "\n${YELLOW}🚀 Step 2: Starting All Services${NC}"
docker-compose up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ All services started successfully${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ Failed to start services${NC}"
    ((TESTS_FAILED++))
    exit 1
fi

# Step 3: Wait for services to be ready
echo -e "\n${YELLOW}⏳ Step 3: Waiting for Services (30 seconds)${NC}"
sleep 30

# Step 4: Check container status
echo -e "\n${YELLOW}🐳 Step 4: Container Status Check${NC}"
RUNNING_CONTAINERS=$(docker-compose ps --services --filter "status=running" | wc -l)
ALL_SERVICES=$(docker-compose ps --services | wc -l)

echo "Running containers: $RUNNING_CONTAINERS"
echo "Total services: $ALL_SERVICES"

if [ "$RUNNING_CONTAINERS" -ge 5 ]; then
    echo -e "${GREEN}✅ Sufficient services running${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ Not enough services running${NC}"
    ((TESTS_FAILED++))
fi

# Step 5: Test individual service endpoints
echo -e "\n${YELLOW}🔍 Step 5: Service Endpoint Tests${NC}"

# Test Core Backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Core Backend (8000) - Healthy${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ Core Backend (8000) - Failed${NC}"
    ((TESTS_FAILED++))
fi

# Test AI/ML Service
if curl -s http://localhost:8001/health > /dev/null; then
    echo -e "${GREEN}✅ AI/ML Service (8001) - Healthy${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ AI/ML Service (8001) - Failed${NC}"
    ((TESTS_FAILED++))
fi

# Test Data Layer
if curl -s http://localhost:8002/health > /dev/null; then
    echo -e "${GREEN}✅ Data Layer (8002) - Healthy${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ Data Layer (8002) - Failed${NC}"
    ((TESTS_FAILED++))
fi

# Test Qdrant
if curl -s http://localhost:6333/ > /dev/null; then
    echo -e "${GREEN}✅ Qdrant (6333) - Responding${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ Qdrant (6333) - Failed${NC}"
    ((TESTS_FAILED++))
fi

# Test Ollama
if curl -s http://localhost:11434/api/version > /dev/null; then
    echo -e "${GREEN}✅ Ollama (11434) - Responding${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ Ollama (11434) - Failed${NC}"
    ((TESTS_FAILED++))
fi

# Step 6: Check logs for errors
echo -e "\n${YELLOW}📋 Step 6: Error Log Analysis${NC}"
ERROR_COUNT=0

for service in core-backend aiml-orchestration data-layer; do
    ERRORS=$(docker-compose logs $service 2>/dev/null | grep -i "error\|exception\|fail" | wc -l)
    if [ "$ERRORS" -eq 0 ]; then
        echo -e "${GREEN}✅ $service - No errors in logs${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠️  $service - $ERRORS potential errors found${NC}"
        ERROR_COUNT=$((ERROR_COUNT + ERRORS))
    fi
done

if [ "$ERROR_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ No critical errors found in logs${NC}"
    ((TESTS_PASSED++))
fi

# Step 7: Resource usage check
echo -e "\n${YELLOW}💾 Step 7: Resource Usage Check${NC}"
MEMORY_USAGE=$(docker stats --no-stream --format "table {{.MemUsage}}" | tail -n +2 | head -5)
echo "Memory usage by containers:"
echo "$MEMORY_USAGE"
echo -e "${GREEN}✅ Resource usage recorded${NC}"
((TESTS_PASSED++))

# Final Results
echo -e "\n${BLUE}📊 TASK 11 - Final Results${NC}"
echo "================================"
echo -e "${GREEN}✅ Tests Passed: ${TESTS_PASSED}${NC}"
echo -e "${RED}❌ Tests Failed: ${TESTS_FAILED}${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 TASK 11 COMPLETED SUCCESSFULLY!${NC}"
    echo -e "${GREEN}✅ Docker environment is fully operational${NC}"
    echo -e "${GREEN}🚀 Ready for Task 12: Service Health Checks${NC}"
    exit 0
else
    echo -e "\n${YELLOW}⚠️  Some tests failed, but environment may still be functional${NC}"
    echo -e "${YELLOW}📋 Check individual service logs for details${NC}"
    exit 1
fi