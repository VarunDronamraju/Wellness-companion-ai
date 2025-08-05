# ========================================
# services/core-backend/src/api/endpoints/documents/pagination.py
# ========================================

"""
Pagination utilities for document endpoints
"""

from typing import Dict, Any, List
import math

class PaginationHelper:
    """Helper class for pagination logic"""
    
    @staticmethod
    def paginate_results(
        items: List[Any], 
        limit: int, 
        offset: int
    ) -> Dict[str, Any]:
        """Apply pagination to a list of items"""
        
        total = len(items)
        paginated_items = items[offset:offset + limit]
        
        return {
            "items": paginated_items,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total,
            "page": (offset // limit) + 1,
            "total_pages": math.ceil(total / limit) if limit > 0 else 1
        }
    
    @staticmethod
    def validate_pagination_params(limit: int, offset: int) -> Dict[str, Any]:
        """Validate pagination parameters"""
        
        errors = []
        
        if limit < 1:
            errors.append("Limit must be at least 1")
        if limit > 100:
            errors.append("Limit cannot exceed 100")
        if offset < 0:
            errors.append("Offset cannot be negative")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "normalized_limit": max(1, min(100, limit)),
            "normalized_offset": max(0, offset)
        }

