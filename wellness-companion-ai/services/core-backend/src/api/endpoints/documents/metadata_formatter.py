
# ========================================
# services/core-backend/src/api/endpoints/documents/metadata_formatter.py
# ========================================

"""
Metadata formatting utilities for document management
"""

import os
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MetadataFormatter:
    """Utilities for formatting document metadata"""
    
    def format_document_metadata(
        self, 
        document_id: str,
        file_path: str,
        original_filename: str,
        file_stat: os.stat_result
    ) -> Dict[str, Any]:
        """Format comprehensive document metadata"""
        
        try:
            # Basic file information
            file_size = file_stat.st_size
            created_at = datetime.fromtimestamp(file_stat.st_ctime)
            modified_at = datetime.fromtimestamp(file_stat.st_mtime)
            
            # File type analysis
            file_extension = os.path.splitext(original_filename)[1].lower()
            file_type_info = self._analyze_file_type(file_extension)
            
            # Size formatting
            size_info = self._format_file_size(file_size)
            
            # File hash for integrity
            file_hash = self._calculate_file_hash(file_path)
            
            # Permissions and accessibility
            permissions = self._get_file_permissions(file_path)
            
            metadata = {
                # Basic information
                "document_id": document_id,
                "filename": original_filename,
                "file_path": file_path,
                
                # Size information
                "size": {
                    "bytes": file_size,
                    "human_readable": size_info["human_readable"],
                    "size_category": size_info["category"]
                },
                
                # Date information
                "dates": {
                    "created_at": created_at.isoformat(),
                    "modified_at": modified_at.isoformat(),
                    "age_days": (datetime.now() - created_at).days,
                    "last_modified_days_ago": (datetime.now() - modified_at).days
                },
                
                # File type information
                "file_type": {
                    "extension": file_extension,
                    "mime_type": file_type_info["mime_type"],
                    "category": file_type_info["category"],
                    "description": file_type_info["description"]
                },
                
                # Security and integrity
                "security": {
                    "file_hash": file_hash,
                    "permissions": permissions,
                    "is_readable": os.access(file_path, os.R_OK),
                    "is_writable": os.access(file_path, os.W_OK)
                },
                
                # Processing status
                "processing": {
                    "status": "uploaded",
                    "indexed": False,
                    "embedded": False,
                    "last_processed": None
                },
                
                # Generated metadata
                "generated_at": datetime.utcnow().isoformat(),
                "metadata_version": "1.0"
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to format metadata for {document_id}: {e}")
            return {
                "document_id": document_id,
                "error": f"Failed to generate metadata: {str(e)}",
                "generated_at": datetime.utcnow().isoformat()
            }
    
    def get_content_preview(
        self, 
        file_path: str, 
        filename: str, 
        max_length: int = 500
    ) -> Dict[str, Any]:
        """Generate content preview for supported file types"""
        
        try:
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext in ['.txt', '.md']:
                return self._get_text_preview(file_path, max_length)
            elif file_ext == '.pdf':
                return self._get_pdf_preview(file_path, max_length)
            elif file_ext in ['.docx', '.doc']:
                return self._get_document_preview(file_path, max_length)
            else:
                return {
                    "type": "unsupported",
                    "message": f"Content preview not available for {file_ext} files",
                    "file_type": file_ext
                }
                
        except Exception as e:
            logger.error(f"Failed to generate content preview: {e}")
            return {
                "type": "error",
                "message": f"Failed to generate preview: {str(e)}"
            }
    
    def _analyze_file_type(self, extension: str) -> Dict[str, str]:
        """Analyze file type based on extension"""
        
        type_mapping = {
            '.pdf': {
                'mime_type': 'application/pdf',
                'category': 'document',
                'description': 'Portable Document Format'
            },
            '.docx': {
                'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'category': 'document',
                'description': 'Microsoft Word Document'
            },
            '.doc': {
                'mime_type': 'application/msword',
                'category': 'document',
                'description': 'Microsoft Word Document (Legacy)'
            },
            '.txt': {
                'mime_type': 'text/plain',
                'category': 'text',
                'description': 'Plain Text File'
            },
            '.md': {
                'mime_type': 'text/markdown',
                'category': 'text',
                'description': 'Markdown Document'
            }
        }
        
        return type_mapping.get(extension, {
            'mime_type': 'application/octet-stream',
            'category': 'unknown',
            'description': 'Unknown File Type'
        })
    
    def _format_file_size(self, size_bytes: int) -> Dict[str, Any]:
        """Format file size in human-readable format"""
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(size_bytes)
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        # Determine size category
        if size_bytes < 1024 * 1024:  # < 1MB
            category = "small"
        elif size_bytes < 10 * 1024 * 1024:  # < 10MB
            category = "medium"
        else:  # >= 10MB
            category = "large"
        
        return {
            "human_readable": f"{size:.1f} {units[unit_index]}",
            "category": category,
            "unit": units[unit_index],
            "value": round(size, 1)
        }
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to calculate file hash: {e}")
            return "unavailable"
    
    def _get_file_permissions(self, file_path: str) -> Dict[str, bool]:
        """Get file permissions information"""
        
        try:
            return {
                "readable": os.access(file_path, os.R_OK),
                "writable": os.access(file_path, os.W_OK),
                "executable": os.access(file_path, os.X_OK)
            }
        except Exception:
            return {"readable": False, "writable": False, "executable": False}
    
    def _get_text_preview(self, file_path: str, max_length: int) -> Dict[str, Any]:
        """Get preview for text files"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(max_length + 100)  # Read a bit extra to check if truncated
            
            is_truncated = len(content) > max_length
            preview_content = content[:max_length]
            
            # Count lines and words
            lines = preview_content.count('\n') + 1
            words = len(preview_content.split())
            
            return {
                "type": "text",
                "content": preview_content,
                "is_truncated": is_truncated,
                "preview_length": len(preview_content),
                "stats": {
                    "lines": lines,
                    "words": words,
                    "characters": len(preview_content)
                },
                "encoding": "utf-8"
            }
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read(max_length)
                return {
                    "type": "text",
                    "content": content,
                    "encoding": "latin-1",
                    "preview_length": len(content)
                }
            except Exception as e:
                return {
                    "type": "error",
                    "message": f"Failed to read text file: {str(e)}"
                }
        except Exception as e:
            return {
                "type": "error",
                "message": f"Failed to preview text: {str(e)}"
            }
    
    def _get_pdf_preview(self, file_path: str, max_length: int) -> Dict[str, Any]:
        """Get preview for PDF files (basic implementation)"""
        
        # For now, return basic PDF info
        # In a full implementation, you'd use PyPDF2 or similar
        return {
            "type": "pdf",
            "message": "PDF content preview requires additional libraries",
            "content": "[PDF Document - Content preview not available in basic implementation]",
            "preview_available": False
        }
    
    def _get_document_preview(self, file_path: str, max_length: int) -> Dict[str, Any]:
        """Get preview for Word documents (basic implementation)"""
        
        # For now, return basic document info
        # In a full implementation, you'd use python-docx or similar
        return {
            "type": "document",
            "message": "Document content preview requires additional libraries",
            "content": "[Word Document - Content preview not available in basic implementation]",
            "preview_available": False
        }