#!/bin/bash
# test_aiml_service.sh
# Test script for TASK 8: AI/ML Service Container

echo "🧪 Testing AI/ML Service (Task 8)"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test endpoint
test_endpoint() {
    local endpoint=$1
    local description=$2
    local expected_status=${3:-200}
    
    echo -e "\n🔍 Testing ${description}..."
    
    response=$(curl -s -w "%{http_code}" http://localhost:8001${endpoint})
    http_code="${response: -3}"
    body="${response%???}"
    
    if [ "$http_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}✅ ${description} - HTTP ${http_code}${NC}"
        ((TESTS_PASSED++))
        
        # Show response preview
        if command -v jq &> /dev/null; then
            echo "$body" | jq -r '.message // .status // .service // "Response received"' 2>/dev/null || echo "Response received"
        else
            echo "Response received"
        fi
        
        return 0
    else
        echo -e "${RED}❌ ${description} - Expected HTTP ${expected_status}, got ${http_code}${NC}"
        echo "Response: $body"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Function to check docker container
check_container() {
    echo -e "\n🐳 Checking Docker container..."
    
    if docker-compose ps aiml-orchestration | grep -q "Up"; then
        echo -e "${GREEN}✅ AI/ML service container is running${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ AI/ML service container is not running${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
    
    # Check container health
    health_status=$(docker inspect wellness_aiml --format='{{.State.Health.Status}}' 2>/dev/null || echo "no-health")
    
    if [ "$health_status" = "healthy" ]; then
        echo -e "${GREEN}✅ Container health check: healthy${NC}"
        ((TESTS_PASSED++))
    elif [ "$health_status" = "starting" ]; then
        echo -e "${YELLOW}⏳ Container health check: starting${NC}"
        echo "Waiting for health check to complete..."
        sleep 10
    else
        echo -e "${YELLOW}⚠️  Container health check: ${health_status}${NC}"
    fi
}

# Function to check logs
check_logs() {
    echo -e "\n📋 Checking service logs..."
    
    # Get recent logs
    LOGS=$(docker-compose logs --tail=20 aiml-orchestration 2>/dev/null)
    
    if echo "$LOGS" | grep -q "started successfully"; then
        echo -e "${GREEN}✅ Service started successfully according to logs${NC}"
        ((TESTS_PASSED++))
    elif echo "$LOGS" | grep -q "Starting"; then
        echo -e "${YELLOW}⏳ Service is starting...${NC}"
    else
        echo -e "${YELLOW}⚠️  No startup confirmation in logs${NC}"
    fi
    
    # Check for errors
    ERROR_COUNT=$(echo "$LOGS" | grep -i "error\|exception\|traceback" | wc -l)
    if [ "$ERROR_COUNT" -eq 0 ]; then
        echo -e "${GREEN}✅ No errors found in logs${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ Found ${ERROR_COUNT} potential errors in logs${NC}"
        echo "Recent errors:"
        echo "$LOGS" | grep -i "error\|exception" | tail -3
        ((TESTS_FAILED++))
    fi
}

# Main testing sequence
main() {
    echo "🚀 Starting AI/ML Service test..."
    echo "📅 $(date)"
    echo ""
    
    # Check if service is running
    check_container
    
    # Wait for service to be ready
    echo "⏳ Waiting for service to be ready..."
    sleep 5
    
    # Test API endpoints
    test_endpoint "/" "Root endpoint"
    test_endpoint "/health" "Health check endpoint"
    test_endpoint "/status" "Status endpoint"
    test_endpoint "/ping" "Ping endpoint"
    test_endpoint "/models" "Models endpoint"
    test_endpoint "/collections" "Collections endpoint"
    test_endpoint "/docs" "API documentation" 200
    
    # Check logs
    check_logs
    
    # Final results
    echo -e "\n📊 Test Results Summary"
    echo "======================="
    echo -e "${GREEN}✅ Tests Passed: ${TESTS_PASSED}${NC}"
    echo -e "${RED}❌ Tests Failed: ${TESTS_FAILED}${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}🎉 AI/ML SERVICE IS WORKING PERFECTLY!${NC}"
        echo -e "${GREEN}✅ Task 8 completed successfully${NC}"
        echo -e "${GREEN}🚀 Ready for Task 9: Core Backend Service${NC}"
        exit 0
    else
        echo -e "\n${YELLOW}⚠️  Some tests failed. Please check the issues above.${NC}"
        echo "💡 Common fixes:"
        echo "   - Ensure container has sufficient time to start"
        echo "   - Check Docker logs: docker-compose logs aiml-orchestration"
        echo "   - Verify all dependencies are properly installed"
        exit 1
    fi
}

# Run main function
main "$@"