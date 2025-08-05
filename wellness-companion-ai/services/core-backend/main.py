
# ========================================
# services/core-backend/main.py - NO CHANGES NEEDED
# ========================================

"""
Core Backend Service Entry Point - Wellness Companion AI
Production entry point for the Core Backend service
"""

import uvicorn
import logging
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the Core Backend service"""
    
    logger.info("🚀 Starting Wellness Companion AI - Core Backend Service")
    
    # Get configuration from environment
    host = os.getenv("CORE_BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("CORE_BACKEND_PORT", "8001"))
    environment = os.getenv("ENVIRONMENT", "development")
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    logger.info(f"Environment: {environment}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Service will run on {host}:{port}")
    
    try:
        # Run the application
        uvicorn.run(
            "src.api.main:app",  # FIXED: Correct module path
            host=host,
            port=port,
            reload=debug and environment == "development",
            log_level="info",
            access_log=True,
            server_header=False,  # Security: Hide server header
            date_header=False     # Security: Hide date header
        )
    except Exception as e:
        logger.error(f"Failed to start Core Backend service: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()