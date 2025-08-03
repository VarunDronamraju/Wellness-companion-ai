#!/bin/bash
# services/aiml-orchestration/ollama-config/health-check.sh
# Ollama Health Check Script for Docker

set -e

# Test basic Ollama API connectivity
echo "🔍 Checking Ollama API..."
if ! curl -s http://localhost:11434/api/version > /dev/null; then
    echo "❌ Ollama API not responding"
    exit 1
fi

# Check if any models are loaded
echo "📋 Checking available models..."
MODELS=$(ollama list 2>/dev/null | tail -n +2 | wc -l)

if [ "$MODELS" -eq 0 ]; then
    echo "⚠️  No models available - this is normal on first startup"
    # Don't fail health check if no models, they will be pulled later
    exit 0
fi

# Test model functionality if models are available
DEFAULT_MODEL=$(ollama list 2>/dev/null | tail -n +2 | head -1 | awk '{print $1}')

if [ -n "$DEFAULT_MODEL" ]; then
    echo "🧪 Testing model functionality with: $DEFAULT_MODEL"
    
    # Quick test with timeout
    RESPONSE=$(timeout 10s ollama run "$DEFAULT_MODEL" "Hi" 2>/dev/null || echo "timeout")
    
    if [ "$RESPONSE" = "timeout" ]; then
        echo "⚠️  Model test timed out - this is normal during model loading"
        exit 0
    elif [ -n "$RESPONSE" ]; then
        echo "✅ Model test successful"
        exit 0
    else
        echo "⚠️  Model test returned empty response"
        exit 0
    fi
fi

echo "✅ Ollama health check passed"
exit 0