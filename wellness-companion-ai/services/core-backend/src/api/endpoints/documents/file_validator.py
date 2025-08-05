# ========================================
# services/core-backend/src/api/endpoints/documents/file_validator.py - UPDATED
# ========================================

"""
File validation utilities for document uploads
"""

from fastapi import UploadFile
import logging
from typing import Dict, List, Any
import os

logger = logging.getLogger(__name__)

class FileValidator:
    """Validates uploaded files"""
    
    # Allowed file types and extensions
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.md'}
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword', 
        'text/plain',
        'text/markdown'
    }
    
    # File size limits (in bytes)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    MIN_FILE_SIZE = 10  # 10 bytes
    
    def __init__(self):
        self.errors = []
        # Check if python-magic is available
        self.magic_available = self._check_magic_availability()
    
    def _check_magic_availability(self) -> bool:
        """Check if python-magic is available"""
        try:
            import magic
            return True
        except ImportError:
            logger.warning("python-magic not available, using fallback validation")
            return False
    
    async def validate_file(self, file: UploadFile) -> Dict[str, Any]:
        """Comprehensive file validation"""
        
        self.errors = []
        
        # Check filename
        if not self._validate_filename(file.filename):
            return {"valid": False, "error": "Invalid filename"}
        
        # Check file extension
        if not self._validate_extension(file.filename):
            return {"valid": False, "error": f"Unsupported file type. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"}
        
        # Read file content for validation
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        # Check file size
        if not self._validate_size(len(content)):
            return {"valid": False, "error": f"File size must be between {self.MIN_FILE_SIZE} bytes and {self.MAX_FILE_SIZE // (1024*1024)}MB"}
        
        # Check MIME type (with fallback)
        if not self._validate_mime_type(content, file.content_type):
            return {"valid": False, "error": "File content doesn't match expected format"}
        
        # Check if file is not empty/corrupted
        if not self._validate_content(content, file.filename):
            return {"valid": False, "error": "File appears to be empty or corrupted"}
        
        logger.info(f"File validation passed: {file.filename}")
        
        return {
            "valid": True,
            "file_size": len(content),
            "detected_type": self._detect_file_type(content, file.content_type),
            "extension": os.path.splitext(file.filename)[1].lower()
        }
    
    def _validate_filename(self, filename: str) -> bool:
        """Validate filename"""
        if not filename or len(filename.strip()) == 0:
            return False
        
        # Check for dangerous characters
        dangerous_chars = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
        if any(char in filename for char in dangerous_chars):
            return False
        
        return True
    
    def _validate_extension(self, filename: str) -> bool:
        """Validate file extension"""
        extension = os.path.splitext(filename)[1].lower()
        return extension in self.ALLOWED_EXTENSIONS
    
    def _validate_size(self, size: int) -> bool:
        """Validate file size"""
        return self.MIN_FILE_SIZE <= size <= self.MAX_FILE_SIZE
    
    def _validate_mime_type(self, content: bytes, declared_mime: str) -> bool:
        """Validate MIME type using file content"""
        
        if self.magic_available:
            try:
                import magic
                # Use python-magic to detect actual file type
                detected_type = magic.from_buffer(content, mime=True)
                return detected_type in self.ALLOWED_MIME_TYPES
            except Exception as e:
                logger.warning(f"MIME type detection failed: {e}")
        
        # Fallback validation using declared MIME type and content signatures
        if declared_mime and declared_mime in self.ALLOWED_MIME_TYPES:
            return self._validate_content_signature(content, declared_mime)
        
        # If no declared MIME type, use basic content validation
        return True
    
    def _validate_content_signature(self, content: bytes, mime_type: str) -> bool:
        """Validate content using file signatures (magic numbers)"""
        
        if not content:
            return False
        
        # PDF signature
        if mime_type == 'application/pdf':
            return content.startswith(b'%PDF-')
        
        # DOCX signature (ZIP format)
        if mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            return content.startswith(b'PK')
        
        # DOC signature (OLE format)
        if mime_type == 'application/msword':
            return content.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1')
        
        # Text files - basic UTF-8 validation
        if mime_type in ['text/plain', 'text/markdown']:
            try:
                content.decode('utf-8')
                return True
            except UnicodeDecodeError:
                # Try other common encodings
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        content.decode(encoding)
                        return True
                    except UnicodeDecodeError:
                        continue
                return False
        
        return True
    
    def _validate_content(self, content: bytes, filename: str) -> bool:
        """Basic content validation"""
        if len(content) == 0:
            return False
        
        # PDF specific validation
        if filename.lower().endswith('.pdf'):
            return content.startswith(b'%PDF-')
        
        # DOCX specific validation  
        if filename.lower().endswith('.docx'):
            return content.startswith(b'PK')  # ZIP signature
        
        # DOC specific validation
        if filename.lower().endswith('.doc'):
            return content.startswith(b'\xd0\xcf\x11\xe0')  # OLE signature
        
        # Text files - check if content is readable
        if filename.lower().endswith(('.txt', '.md')):
            try:
                content.decode('utf-8')
                return True
            except UnicodeDecodeError:
                try:
                    content.decode('latin-1')
                    return True
                except UnicodeDecodeError:
                    return False
        
        return True
    
    def _detect_file_type(self, content: bytes, declared_mime: str = None) -> str:
        """Detect actual file type"""
        
        if self.magic_available:
            try:
                import magic
                return magic.from_buffer(content, mime=True)
            except Exception:
                pass
        
        # Fallback detection using file signatures
        if content.startswith(b'%PDF-'):
            return "application/pdf"
        elif content.startswith(b'PK'):
            return "application/zip"  # Could be DOCX
        elif content.startswith(b'\xd0\xcf\x11\xe0'):
            return "application/msword"
        else:
            # Try to detect text
            try:
                content.decode('utf-8')
                return "text/plain"
            except UnicodeDecodeError:
                pass
        
        return declared_mime or "application/octet-stream"