"""
API Router - Wellness Companion AI
Main router registration for all API endpoints
"""

from fastapi import APIRouter
from ..core.config import config

# Create main API router
api_router = APIRouter(prefix=config.settings.api_v1_prefix)

# Import routers from different modules (will be implemented in subsequent tasks)
# from .endpoints.auth.router import router as auth_router          # Task 70 (Phase 6)
# from .endpoints.documents.router import router as documents_router # Tasks 40-43
# from .endpoints.search.router import router as search_router       # Tasks 39, 44-45
# from .endpoints.system.router import router as system_router       # Task 38

def setup_routers() -> APIRouter:
    """Setup and register all API routers"""
    
    # Register routers (will be uncommented as tasks are completed)
    # api_router.include_router(system_router, tags=["system"])           # Task 38
    # api_router.include_router(auth_router, tags=["auth"])               # Phase 6
    # api_router.include_router(documents_router, tags=["documents"])     # Tasks 40-43
    # api_router.include_router(search_router, tags=["search"])           # Tasks 39, 44-45
    
    return api_router


# Export configured router
router = setup_routers()