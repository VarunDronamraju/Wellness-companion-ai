
# ========================================
# services/core-backend/src/api/endpoints/documents/filtering.py
# ========================================

"""
Document filtering logic
"""

from typing import List, Dict, Any, Optional
import os
from datetime import datetime, timedelta

class DocumentFilter:
    """Document filtering utilities"""
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.md'}
    
    @staticmethod
    def filter_by_file_type(documents: List[Dict[str, Any]], file_type: str) -> List[Dict[str, Any]]:
        """Filter documents by file extension"""
        
        if not file_type:
            return documents
        
        # Normalize file type (ensure it starts with dot)
        if not file_type.startswith('.'):
            file_type = f'.{file_type}'
        
        file_type = file_type.lower()
        
        return [
            doc for doc in documents 
            if doc.get('file_type', '').lower() == file_type
        ]
    
    @staticmethod
    def filter_by_date_range(
        documents: List[Dict[str, Any]], 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Filter documents by creation date range"""
        
        if not start_date and not end_date:
            return documents
        
        filtered_docs = []
        
        for doc in documents:
            created_at_str = doc.get('created_at')
            if not created_at_str:
                continue
            
            try:
                created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                
                # Check start date
                if start_date:
                    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    if created_at < start_dt:
                        continue
                
                # Check end date
                if end_date:
                    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    if created_at > end_dt:
                        continue
                
                filtered_docs.append(doc)
                
            except (ValueError, TypeError):
                # Skip documents with invalid dates
                continue
        
        return filtered_docs
    
    @staticmethod
    def filter_by_size_range(
        documents: List[Dict[str, Any]], 
        min_size: Optional[int] = None,
        max_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Filter documents by file size range (in bytes)"""
        
        if min_size is None and max_size is None:
            return documents
        
        filtered_docs = []
        
        for doc in documents:
            size = doc.get('size', 0)
            
            # Check minimum size
            if min_size is not None and size < min_size:
                continue
            
            # Check maximum size
            if max_size is not None and size > max_size:
                continue
            
            filtered_docs.append(doc)
        
        return filtered_docs
    
    @staticmethod
    def filter_by_status(
        documents: List[Dict[str, Any]], 
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Filter documents by processing status"""
        
        if not status:
            return documents
        
        return [
            doc for doc in documents 
            if doc.get('status', '').lower() == status.lower()
        ]
    
    @staticmethod
    def search_by_filename(
        documents: List[Dict[str, Any]], 
        search_term: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search documents by filename"""
        
        if not search_term:
            return documents
        
        search_term = search_term.lower()
        
        return [
            doc for doc in documents 
            if search_term in doc.get('filename', '').lower()
        ]
    
    @staticmethod
    def sort_documents(
        documents: List[Dict[str, Any]], 
        sort_by: str = 'created_at',
        sort_order: str = 'desc'
    ) -> List[Dict[str, Any]]:
        """Sort documents by specified field"""
        
        valid_sort_fields = ['created_at', 'modified_at', 'filename', 'size']
        
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        
        reverse = sort_order.lower() == 'desc'
        
        try:
            if sort_by in ['created_at', 'modified_at']:
                # Sort by datetime
                return sorted(
                    documents,
                    key=lambda x: datetime.fromisoformat(x.get(sort_by, '1970-01-01T00:00:00').replace('Z', '+00:00')),
                    reverse=reverse
                )
            elif sort_by == 'size':
                # Sort by numeric size
                return sorted(
                    documents,
                    key=lambda x: x.get(sort_by, 0),
                    reverse=reverse
                )
            else:
                # Sort by string (filename)
                return sorted(
                    documents,
                    key=lambda x: x.get(sort_by, '').lower(),
                    reverse=reverse
                )
        except (ValueError, TypeError):
            # Fallback to original order if sorting fails
            return documents
