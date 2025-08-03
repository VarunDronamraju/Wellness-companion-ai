# services/data-layer/src/embedding_pipeline/text_splitter.py
"""
Text chunking with 512 tokens and 50 token overlap using LangChain.
"""

import logging
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken

logger = logging.getLogger(__name__)

class TextSplitter:
    """Text chunking with configurable parameters"""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize tokenizer for accurate token counting
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Initialize LangChain text splitter
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size * 4,  # Approximate character count (4 chars per token)
            chunk_overlap=chunk_overlap * 4,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def split_text(self, text: str, document_id: str = None) -> List[Dict]:
        """
        Split text into chunks with metadata
        
        Args:
            text: Input text to split
            document_id: Optional document identifier
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        try:
            # Split text using LangChain
            chunks = self.splitter.split_text(text)
            
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                # Count actual tokens
                token_count = len(self.tokenizer.encode(chunk))
                
                # Trim if exceeds token limit
                if token_count > self.chunk_size:
                    tokens = self.tokenizer.encode(chunk)[:self.chunk_size]
                    chunk = self.tokenizer.decode(tokens)
                    token_count = self.chunk_size
                
                chunk_data = {
                    'chunk_id': f"{document_id}_{i}" if document_id else f"chunk_{i}",
                    'text': chunk,
                    'chunk_index': i,
                    'token_count': token_count,
                    'character_count': len(chunk),
                    'document_id': document_id
                }
                
                processed_chunks.append(chunk_data)
            
            logger.info(f"Split text into {len(processed_chunks)} chunks")
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Text splitting failed: {str(e)}")
            raise