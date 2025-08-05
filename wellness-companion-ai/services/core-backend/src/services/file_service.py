
# ========================================
# services/core-backend/src/services/file_service.py
# ========================================

"""
File Service - File system operations and management
"""

import os
import logging
import aiofiles
from typing import Dict, Any, List, Optional
from datetime import datetime
import shutil

logger = logging.getLogger(__name__)

class FileService:
    """Service for file system operations"""
    
    def __init__(self):
        self.upload_dir = os.getenv("UPLOAD_DIR", "/tmp/uploads")
        self.max_storage_per_user = int(os.getenv("MAX_USER_STORAGE", str(100 * 1024 * 1024)))  # 100MB default
        logger.info(f"File service initialized - Upload dir: {self.upload_dir}")
    
    async def get_file_content(self, file_path: str) -> Optional[bytes]:
        """Read file content"""
        
        try:
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                return None
            
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
            
            logger.debug(f"Read file content: {file_path} ({len(content)} bytes)")
            return content
            
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return None
    
    async def write_file_content(self, file_path: str, content: bytes) -> bool:
        """Write content to file"""
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            logger.info(f"File written: {file_path} ({len(content)} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            return False
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from filesystem"""
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    
    async def get_user_storage_usage(self, user_id: str) -> Dict[str, Any]:
        """Get storage usage for user"""
        
        try:
            user_dir = os.path.join(self.upload_dir, user_id)
            
            if not os.path.exists(user_dir):
                return {
                    "user_id": user_id,
                    "total_size": 0,
                    "file_count": 0,
                    "quota": self.max_storage_per_user,
                    "usage_percentage": 0
                }
            
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(user_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                    except OSError:
                        continue
            
            usage_percentage = (total_size / self.max_storage_per_user) * 100
            
            logger.debug(f"User {user_id} storage: {total_size} bytes, {file_count} files")
            
            return {
                "user_id": user_id,
                "total_size": total_size,
                "file_count": file_count,
                "quota": self.max_storage_per_user,
                "usage_percentage": usage_percentage,
                "quota_exceeded": total_size > self.max_storage_per_user
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage usage for user {user_id}: {e}")
            return {"error": str(e)}
    
    async def cleanup_user_files(self, user_id: str) -> Dict[str, Any]:
        """Cleanup all files for a user"""
        
        try:
            user_dir = os.path.join(self.upload_dir, user_id)
            
            if not os.path.exists(user_dir):
                return {"cleaned": 0, "message": "No files found"}
            
            # Count files before cleanup
            file_count = sum(len(files) for _, _, files in os.walk(user_dir))
            
            # Remove directory and all contents
            shutil.rmtree(user_dir)
            
            logger.info(f"Cleaned up {file_count} files for user {user_id}")
            
            return {
                "cleaned": file_count,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup files for user {user_id}: {e}")
            return {"error": str(e)}
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get detailed file information"""
        
        try:
            if not os.path.exists(file_path):
                return {"exists": False}
            
            stat = os.stat(file_path)
            
            return {
                "exists": True,
                "path": file_path,
                "size": stat.st_size,
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_file": os.path.isfile(file_path),
                "is_readable": os.access(file_path, os.R_OK),
                "is_writable": os.access(file_path, os.W_OK)
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            return {"exists": False, "error": str(e)}