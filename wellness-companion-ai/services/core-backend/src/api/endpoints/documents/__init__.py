# ========================================
# services/core-backend/src/api/endpoints/documents/__init__.py
# ========================================

"""
Document endpoints package
"""

from .upload import router as upload_router

__all__ = ["upload_router"]
