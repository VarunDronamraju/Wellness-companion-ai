# services/data-layer/src/embedding_pipeline/pdf_handler.py
"""
PDF text extraction using PyPDF2 and pymupdf fallback.
"""

import logging
from typing import Dict, List
import PyPDF2
from io import BytesIO

logger = logging.getLogger(__name__)

class PDFHandler:
    """PDF text extraction handler"""
    
    def extract_text(self, file_path: str) -> Dict:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dict with text content and metadata
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                metadata = {
                    'page_count': len(pdf_reader.pages),
                    'title': pdf_reader.metadata.get('/Title', '') if pdf_reader.metadata else '',
                    'author': pdf_reader.metadata.get('/Author', '') if pdf_reader.metadata else '',
                    'creator': pdf_reader.metadata.get('/Creator', '') if pdf_reader.metadata else ''
                }
                
                # Extract text from all pages
                text_content = []
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            text_content.append({
                                'page_number': page_num + 1,
                                'text': page_text.strip()
                            })
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1}: {str(e)}")
                
                # Combine all text
                full_text = '\n\n'.join([page['text'] for page in text_content])
                
                return {
                    'text': full_text,
                    'metadata': metadata,
                    'pages': text_content,
                    'extraction_method': 'PyPDF2'
                }
                
        except Exception as e:
            logger.error(f"PDF extraction failed for {file_path}: {str(e)}")
            raise