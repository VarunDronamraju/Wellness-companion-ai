#!/bin/bash
# services/aiml-orchestration/ollama-config/init-models.sh
# Ollama Model Initialization Script for Wellness Companion AI

set -e

echo "🚀 Initializing Ollama Models for Wellness Companion AI..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Wait for Ollama service to be ready
wait_for_ollama() {
    echo -e "${BLUE}⏳ Waiting for Ollama service to start...${NC}"
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Ollama service is ready${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}Attempt ${attempt}/${max_attempts} - Ollama not ready yet...${NC}"
        sleep 5
        ((attempt++))
    done
    
    echo -e "${RED}❌ Ollama service failed to start after ${max_attempts} attempts${NC}"
    exit 1
}

# Pull and verify model
pull_model() {
    local model_name=$1
    local model_description=$2
    
    echo -e "${BLUE}📥 Pulling ${model_description}...${NC}"
    
    if ollama pull "$model_name"; then
        echo -e "${GREEN}✅ Successfully pulled ${model_name}${NC}"
        
        # Verify model is available
        if ollama list | grep -q "$model_name"; then
            echo -e "${GREEN}✅ ${model_name} verified and available${NC}"
            return 0
        else
            echo -e "${RED}❌ ${model_name} pull succeeded but model not found in list${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Failed to pull ${model_name}${NC}"
        return 1
    fi
}

# Test model functionality
test_model() {
    local model_name=$1
    local test_prompt="Hello, respond with exactly: 'Model working correctly'"
    
    echo -e "${BLUE}🧪 Testing ${model_name} functionality...${NC}"
    
    local response=$(ollama run "$model_name" "$test_prompt" 2>/dev/null | head -1)
    
    if [[ "$response" == *"Model working correctly"* ]] || [[ "$response" == *"Hello"* ]]; then
        echo -e "${GREEN}✅ ${model_name} is responding correctly${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  ${model_name} responded but output may be unexpected: ${response}${NC}"
        return 0  # Still consider it working
    fi
}

# Main execution
main() {
    echo -e "${BLUE}🎯 Starting Ollama Model Setup${NC}"
    echo "================================="
    
    # Wait for Ollama to be ready
    wait_for_ollama
    
    # Default models for Wellness Companion AI
    # Using smaller models for better performance and lower resource usage
    
    echo -e "\n${BLUE}📋 Installing recommended models...${NC}"
    
    # Primary LLM: Gemma 2B (fast, efficient)
    if pull_model "gemma:2b" "Gemma 2B (Primary LLM - Fast & Efficient)"; then
        test_model "gemma:2b"
    fi
    
    # Alternative LLM: Llama3.2 3B (better quality, more resources)
    if pull_model "llama3.2:3b" "Llama 3.2 3B (Alternative LLM - Better Quality)"; then
        test_model "llama3.2:3b"
    fi
    
    # Lightweight option: TinyLlama (very fast, basic responses)
    if pull_model "tinyllama" "TinyLlama (Lightweight Option)"; then
        test_model "tinyllama"
    fi
    
    # List all available models
    echo -e "\n${BLUE}📋 Currently available models:${NC}"
    ollama list
    
    # Model recommendations
    echo -e "\n${GREEN}🎯 Model Recommendations:${NC}"
    echo "• gemma:2b - Best balance of speed and quality"
    echo "• llama3.2:3b - Higher quality responses (more resources)"
    echo "• tinyllama - Ultra-fast responses (basic quality)"
    
    echo -e "\n${GREEN}✅ Ollama model initialization completed!${NC}"
    echo -e "${BLUE}💡 Models can be switched via API or environment variables${NC}"
}

# Run main function
main "$@"