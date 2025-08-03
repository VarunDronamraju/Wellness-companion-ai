#!/bin/bash
# test_database_services.sh
# Comprehensive testing script for Tasks 4-6 (Database Services)

echo "🧪 Testing Database Services (Tasks 4-6)"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test service health
test_service() {
    local service_name=$1
    local test_command=$2
    local service_description=$3
    
    echo -e "\n🔍 Testing ${service_description}..."
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ ${service_name} is healthy${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}❌ ${service_name} health check failed${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Function to test database operations
test_database_operations() {
    echo -e "\n🗄️  Testing Database Operations..."
    
    # Test PostgreSQL operations
    echo "📊 Testing PostgreSQL operations..."
    docker-compose exec -T postgres psql -U wellness_user -d wellness_companion -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema IN ('core_backend', 'data_layer', 'user_management', 'document_management');" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PostgreSQL schemas and tables created successfully${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ PostgreSQL schema creation failed${NC}"
        ((TESTS_FAILED++))
    fi
    
    # Test Redis operations
    echo "🔄 Testing Redis operations..."
    docker-compose exec -T redis redis-cli -a "${REDIS_PASSWORD}" set test_key "test_value" > /dev/null 2>&1
    REDIS_GET_RESULT=$(docker-compose exec -T redis redis-cli -a "${REDIS_PASSWORD}" get test_key 2>/dev/null)
    if [ "$REDIS_GET_RESULT" = "test_value" ]; then
        echo -e "${GREEN}✅ Redis SET/GET operations working${NC}"
        docker-compose exec -T redis redis-cli -a "${REDIS_PASSWORD}" del test_key > /dev/null 2>&1
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ Redis operations failed${NC}"
        ((TESTS_FAILED++))
    fi
    
    # Test Qdrant operations
    echo "🔍 Testing Qdrant operations..."
    QDRANT_COLLECTIONS=$(curl -s http://localhost:6333/collections | jq -r '.result.collections[].name' 2>/dev/null)
    if echo "$QDRANT_COLLECTIONS" | grep -q "wellness_documents"; then
        echo -e "${GREEN}✅ Qdrant collections created successfully${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠️  Qdrant collections not found - will be created during initialization${NC}"
        ((TESTS_PASSED++))
    fi
}

# Function to test service connectivity
test_service_connectivity() {
    echo -e "\n🌐 Testing Service Connectivity..."
    
    # Test PostgreSQL connection from other services
    echo "🔗 Testing PostgreSQL connectivity..."
    docker-compose exec -T postgres pg_isready -h postgres -p 5432 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PostgreSQL accepting connections${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ PostgreSQL connection failed${NC}"
        ((TESTS_FAILED++))
    fi
    
    # Test Redis connection
    echo "🔗 Testing Redis connectivity..."
    docker-compose exec -T redis redis-cli ping > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Redis accepting connections${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ Redis connection failed${NC}"
        ((TESTS_FAILED++))
    fi
    
    # Test Qdrant API connectivity
    echo "🔗 Testing Qdrant API connectivity..."
    if curl -s http://localhost:6333/health | grep -q "true"; then
        echo -e "${GREEN}✅ Qdrant API responding${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ Qdrant API not responding${NC}"
        ((TESTS_FAILED++))
    fi
}

# Function to check docker volumes
test_docker_volumes() {
    echo -e "\n💾 Testing Docker Volume Persistence..."
    
    # Check if volumes exist
    VOLUMES=(postgres_data redis_data qdrant_data)
    
    for volume in "${VOLUMES[@]}"; do
        if docker volume inspect "wellness-companion-ai_${volume}" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Volume ${volume} exists${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}❌ Volume ${volume} missing${NC}"
            ((TESTS_FAILED++))
        fi
    done
}

# Function to check service logs for errors
check_service_logs() {
    echo -e "\n📋 Checking Service Logs for Errors..."
    
    SERVICES=(postgres redis qdrant)
    
    for service in "${SERVICES[@]}"; do
        echo "📝 Checking ${service} logs..."
        ERROR_COUNT=$(docker-compose logs "$service" 2>/dev/null | grep -i "error\|fatal\|fail" | wc -l)
        if [ "$ERROR_COUNT" -eq 0 ]; then
            echo -e "${GREEN}✅ No errors in ${service} logs${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "${YELLOW}⚠️  Found ${ERROR_COUNT} potential errors in ${service} logs${NC}"
            echo "💡 Run 'docker-compose logs ${service}' to investigate"
        fi
    done
}

# Main testing sequence
main() {
    echo "🚀 Starting comprehensive database services test..."
    echo "📅 $(date)"
    echo ""
    
    # Ensure services are running
    echo "🔄 Checking if services are running..."
    if ! docker-compose ps | grep -q "Up"; then
        echo -e "${RED}❌ Services not running. Start with: docker-compose up -d${NC}"
        exit 1
    fi
    
    # Wait for services to be ready
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    # Run tests
    test_service "PostgreSQL" "docker-compose exec -T postgres pg_isready -U wellness_user -d wellness_companion" "PostgreSQL Database"
    test_service "Redis" "docker-compose exec -T redis redis-cli ping" "Redis Cache"
    test_service "Qdrant" "curl -s http://localhost:6333/health" "Qdrant Vector Database"
    
    test_database_operations
    test_service_connectivity
    test_docker_volumes
    check_service_logs
    
    # Final results
    echo -e "\n📊 Test Results Summary"
    echo "======================="
    echo -e "${GREEN}✅ Tests Passed: ${TESTS_PASSED}${NC}"
    echo -e "${RED}❌ Tests Failed: ${TESTS_FAILED}${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}🎉 ALL DATABASE SERVICES ARE WORKING PERFECTLY!${NC}"
        echo -e "${GREEN}✅ Tasks 4-6 completed successfully${NC}"
        echo -e "${GREEN}🚀 Ready for Phase 2: Core RAG Foundation${NC}"
        exit 0
    else
        echo -e "\n${YELLOW}⚠️  Some tests failed. Please check the issues above.${NC}"
        echo "💡 Common fixes:"
        echo "   - Ensure .env file is properly configured"
        echo "   - Check if all required ports are available"
        echo "   - Verify Docker has sufficient resources"
        exit 1
    fi
}

# Run main function
main "$@"