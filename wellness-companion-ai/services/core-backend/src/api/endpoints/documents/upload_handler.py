
# ========================================
# services/core-backend/src/api/endpoints/documents/upload_handler.py
# ========================================

"""
Upload handling utilities for document management
"""

from fastapi import UploadFile, HTTPException
import os
import uuid
import aiofiles
import logging
from datetime import datetime
from typing import Dict, Any
import hashlib

logger = logging.getLogger(__name__)

class UploadHandler:
    """Handles file upload operations"""
    
    def __init__(self):
        self.upload_dir = os.getenv("UPLOAD_DIR", "/tmp/uploads")
        self.ensure_upload_directory()
    
    def ensure_upload_directory(self):
        """Ensure upload directory exists"""
        os.makedirs(self.upload_dir, exist_ok=True)
        logger.info(f"Upload directory ready: {self.upload_dir}")
    
    async def handle_upload(self, file: UploadFile, user_id: str) -> Dict[str, Any]:
        """Handle file upload with secure storage"""
        
        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            original_extension = os.path.splitext(file.filename)[1].lower()
            secure_filename = f"{file_id}{original_extension}"
            
            # Create user-specific directory
            user_dir = os.path.join(self.upload_dir, user_id)
            os.makedirs(user_dir, exist_ok=True)
            
            # Full file path
            file_path = os.path.join(user_dir, secure_filename)
            
            # Read and save file
            content = await file.read()
            await file.seek(0)  # Reset for potential reuse
            
            # Calculate file hash for integrity
            file_hash = hashlib.sha256(content).hexdigest()
            
            # Save file asynchronously
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            logger.info(f"File uploaded successfully: {file_path}")
            
            return {
                "file_id": file_id,
                "file_path": file_path,
                "secure_filename": secure_filename,
                "original_filename": file.filename,
                "file_size": len(content),
                "file_hash": file_hash,
                "upload_time": datetime.utcnow().isoformat(),
                "user_directory": user_dir
            }
            
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"File upload processing failed: {str(e)}"
            )
    
    async def cleanup_file(self, file_path: str) -> bool:
        """Clean up uploaded file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to cleanup file {file_path}: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information"""
        try:
            if not os.path.exists(file_path):
                return {"exists": False}
            
            stat = os.stat(file_path)
            return {
                "exists": True,
                "size": stat.st_size,
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "path": file_path
            }
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            return {"exists": False, "error": str(e)}