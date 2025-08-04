#!/bin/bash

# Task 32 Web Search Processing - Test Execution Script
# Location: services/aiml-orchestration/run_task32_tests.sh
# Purpose: Execute comprehensive tests for all Task 32 components

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SERVICE_DIR="$PROJECT_ROOT/services/aiml-orchestration"
TEST_DIR="$SERVICE_DIR/tests"
SRC_DIR="$SERVICE_DIR/src"

print_status "🧪 TASK 32 WEB SEARCH PROCESSING TEST SUITE"
print_status "=============================================="
echo ""

# Check if running in Docker environment
if [ -f /.dockerenv ]; then
    print_status "✅ Running inside Docker container"
    DOCKER_MODE=true
else
    print_warning "⚠️  Running outside Docker - some tests may not work as expected"
    DOCKER_MODE=false
fi

# Navigate to service directory
print_status "📁 Navigating to AI/ML orchestration service directory..."
cd "$SERVICE_DIR" || {
    print_error "Failed to navigate to service directory: $SERVICE_DIR"
    exit 1
}

print_success "Current directory: $(pwd)"

# Check directory structure
print_status "🔍 Verifying Task 32 file structure..."

REQUIRED_FILES=(
    "src/search/web_result_processor.py"
    "src/search/result_parser.py"
    "src/search/content_extractor.py"
    "src/search/result_validator.py"
    "src/search/metadata_enricher.py"
)

MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "✅ Found: $file"
    else
        print_error "❌ Missing: $file"
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    print_error "❌ Missing required files. Please ensure all Task 32 files are created."
    exit 1
fi

# Check Python environment
print_status "🐍 Checking Python environment..."

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    print_error "❌ Python not found. Please install Python 3.7+"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
print_success "✅ Found: $PYTHON_VERSION"

# Check required Python packages
print_status "📦 Checking required Python packages..."

REQUIRED_PACKAGES=("asyncio" "json" "datetime" "typing" "re" "urllib.parse" "hashlib")

for package in "${REQUIRED_PACKAGES[@]}"; do
    if $PYTHON_CMD -c "import $package" 2>/dev/null; then
        print_success "✅ Package available: $package"
    else
        print_warning "⚠️  Package may not be available: $package"
    fi
done

# Create test directory if it doesn't exist
print_status "📁 Setting up test directory..."
mkdir -p "$TEST_DIR"

# Create __init__.py files for proper imports
touch "$SRC_DIR/__init__.py"
touch "$SRC_DIR/search/__init__.py"
touch "$TEST_DIR/__init__.py"

print_success "✅ Test directory structure ready"

# Create and run the test script
print_status "📝 Creating test script..."

cat > "$TEST_DIR/test_task32_web_processing.py" << 'EOF'
#!/usr/bin/env python3
"""
Test Script for Task 32: Web Search Processing
Location: services/aiml-orchestration/tests/test_task32_web_processing.py
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    # Import Task 32 components
    from search.web_result_processor import WebResultProcessor, ProcessedWebResult
    from search.result_parser import ResultParser
    from search.content_extractor import ContentExtractor
    from search.result_validator import ResultValidator
    from search.metadata_enricher import MetadataEnricher
    print("✅ All Task 32 modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all Task 32 files are in the correct location")
    sys.exit(1)

class SimpleTest:
    """Simple test class for Task 32 components"""
    
    def __init__(self):
        self.mock_response = {
            "results": [
                {
                    "title": "Machine Learning Algorithms Guide",
                    "url": "https://example.com/ml-guide",
                    "content": "Machine learning algorithms are computational methods that enable computers to learn and make decisions from data without being explicitly programmed for every scenario. There are three main types: supervised learning, unsupervised learning, and reinforcement learning. Supervised learning algorithms like linear regression and decision trees learn from labeled training data. Unsupervised learning methods such as clustering and dimensionality reduction find patterns in unlabeled data. Reinforcement learning involves agents learning optimal actions through trial and error in an environment.",
                    "snippet": "Machine learning algorithms are computational methods...",
                    "score": 0.85
                }
            ]
        }
        self.test_query = "machine learning algorithms"
    
    async def test_basic_functionality(self):
        """Test basic functionality of each component"""
        print("\n🧪 Testing basic functionality...")
        
        try:
            # Test ResultParser
            print("  📋 Testing ResultParser...")
            parser = ResultParser()
            parsed = await parser.parse_tavily_response(self.mock_response)
            assert len(parsed) > 0, "Parser failed"
            print("    ✅ ResultParser working")
            
            # Test ContentExtractor
            print("  🔧 Testing ContentExtractor...")
            extractor = ContentExtractor()
            extracted = await extractor.extract_relevant_content(parsed[0], self.test_query)
            assert extracted is not None, "Extractor failed"
            print("    ✅ ContentExtractor working")
            
            # Test ResultValidator
            print("  ✅ Testing ResultValidator...")
            validator = ResultValidator()
            validated = await validator.validate_results([extracted], self.test_query)
            assert len(validated) > 0, "Validator failed"
            print("    ✅ ResultValidator working")
            
            # Test MetadataEnricher
            print("  🏷️ Testing MetadataEnricher...")
            enricher = MetadataEnricher()
            enriched = await enricher.enrich_with_metadata(validated[0], self.test_query)
            assert 'confidence_score' in enriched, "Enricher failed"
            print("    ✅ MetadataEnricher working")
            
            # Test WebResultProcessor (integration)
            print("  🔄 Testing WebResultProcessor...")
            processor = WebResultProcessor()
            processed = await processor.process_web_results(self.mock_response, self.test_query)
            assert len(processed) > 0, "Processor failed"
            print("    ✅ WebResultProcessor working")
            
            print("\n🎉 ALL TESTS PASSED!")
            return True
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            return False

async def main():
    """Run simple tests"""
    print("🚀 Starting Task 32 Basic Tests...")
    
    test = SimpleTest()
    success = await test.test_basic_functionality()
    
    if success:
        print("\n✅ TASK 32 COMPONENTS ARE WORKING CORRECTLY!")
        print("🎯 Ready to proceed to Task 33")
    else:
        print("\n❌ TASK 32 TESTS FAILED")
        print("Please check the implementation")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
EOF

print_success "✅ Test script created"

# Make test script executable
chmod +x "$TEST_DIR/test_task32_web_processing.py"

# Run the tests
print_status "🚀 Running Task 32 tests..."
echo ""

if cd "$SERVICE_DIR" && $PYTHON_CMD tests/test_task32_web_processing.py; then
    TEST_RESULT="PASSED"
    print_success "🎉 ALL TASK 32 TESTS PASSED!"
else
    TEST_RESULT="FAILED"
    print_error "❌ SOME TASK 32 TESTS FAILED"
fi

echo ""
print_status "📊 TEST SUMMARY"
print_status "==============="
echo "Service Directory: $SERVICE_DIR"
echo "Test Script: $TEST_DIR/test_task32_web_processing.py"
echo "Python Command: $PYTHON_CMD"
echo "Docker Mode: $DOCKER_MODE"
echo "Test Result: $TEST_RESULT"

if [ "$TEST_RESULT" = "PASSED" ]; then
    echo ""
    print_success "✅ TASK 32: WEB SEARCH PROCESSING - COMPLETE"
    print_success "🎯 Ready to proceed to Task 33: Hybrid Search Logic"
    echo ""
    print_status "Next steps:"
    print_status "1. ✅ Task 31: Tavily API Client (Complete)"
    print_status "2. ✅ Task 32: Web Search Processing (Complete)"
    print_status "3. ⏳ Task 33: Hybrid Search Logic (Next)"
    print_status "4. ⏳ Task 34: Result Synthesis (Pending)"
    print_status "5. ⏳ Task 35: Test Hybrid Search (Pending)"
    exit 0
else
    echo ""
    print_error "❌ TASK 32 TESTS FAILED"
    print_error "Please review the implementation and fix any issues"
    exit 1
fi