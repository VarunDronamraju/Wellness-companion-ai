"""
Core Backend Service Entry Point - Wellness Companion AI
C:\Users\varun\Desktop\JObSearch\Application\WellnessAtWorkAI\wellness-companion-ai\services\core-backend\main.py
Production entry point for the Core Backend service
"""

import uvicorn
import logging
from src.core.settings import settings
from src.core.config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the Core Backend service"""
    
    logger.info("🚀 Starting Wellness Companion AI - Core Backend Service")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Service will run on {settings.host}:{settings.port}")
    
    # Run the application
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug and settings.environment == "development",
        log_level=settings.log_level.lower(),
        access_log=True,
        server_header=False,  # Security: Hide server header
        date_header=False     # Security: Hide date header
    )


if __name__ == "__main__":
    main()