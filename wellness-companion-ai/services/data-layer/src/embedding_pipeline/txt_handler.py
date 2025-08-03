# services/data-layer/src/embedding_pipeline/txt_handler.py
"""
Plain text file handler.
"""

import logging
from typing import Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class TXTHandler:
    """Plain text file handler"""
    
    def extract_text(self, file_path: str) -> Dict:
        """
        Extract text from plain text file
        
        Args:
            file_path: Path to text file
            
        Returns:
            Dict with text content and metadata
        """
        try:
            file_obj = Path(file_path)
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            text_content = None
            encoding_used = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        text_content = file.read()
                        encoding_used = encoding
                        break
                except UnicodeDecodeError:
                    continue
            
            if text_content is None:
                raise ValueError("Unable to decode text file with common encodings")
            
            metadata = {
                'file_size': file_obj.stat().st_size,
                'encoding': encoding_used,
                'line_count': len(text_content.splitlines()),
                'character_count': len(text_content)
            }
            
            return {
                'text': text_content,
                'metadata': metadata,
                'extraction_method': 'direct_read'
            }
            
        except Exception as e:
            logger.error(f"TXT extraction failed for {file_path}: {str(e)}")
            raise