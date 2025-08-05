
"""
Document endpoints package
"""

from .upload import router as upload_router
from .list import router as list_router
from .details import router as details_router

__all__ = ["upload_router", "list_router", "details_router"]