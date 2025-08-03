# services/data-layer/src/embedding_pipeline/document_processor.py
"""
Main document processor for PDF, DOCX, and TXT files.
Coordinates text extraction across different file types.
"""

from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path
import mimetypes

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Main document processing orchestrator"""
    
    def __init__(self):
        # Use relative imports that work in Docker
        from .pdf_handler import PDFHandler
        from .docx_handler import DOCXHandler  
        from .txt_handler import TXTHandler
        
        self.pdf_handler = PDFHandler()
        self.docx_handler = DOCXHandler()
        self.txt_handler = TXTHandler()
        
        self.handlers = {
            'application/pdf': self.pdf_handler,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': self.docx_handler,
            'text/plain': self.txt_handler
        }
    
    def process_document(self, file_path: str, file_type: Optional[str] = None) -> Dict:
        """
        Process document and extract text with metadata
        
        Args:
            file_path: Path to the document file
            file_type: MIME type (auto-detected if None)
            
        Returns:
            Dict with extracted text, metadata, and processing info
        """
        try:
            # Auto-detect file type if not provided
            if not file_type:
                file_type, _ = mimetypes.guess_type(file_path)
            
            if file_type not in self.handlers:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            handler = self.handlers[file_type]
            result = handler.extract_text(file_path)
            
            # Add processing metadata
            result.update({
                'file_path': file_path,
                'file_type': file_type,
                'processor': handler.__class__.__name__,
                'status': 'success'
            })
            
            logger.info(f"Successfully processed {file_path} ({file_type})")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {str(e)}")
            return {
                'file_path': file_path,
                'file_type': file_type,
                'text': '',
                'metadata': {},
                'status': 'error',
                'error': str(e)
            }