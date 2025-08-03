# services/data-layer/src/embedding_pipeline/langchain_integration.py
"""
LangChain text splitter wrapper and integration.
"""

import logging
from typing import List, Dict, Optional
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
    CharacterTextSplitter
)

logger = logging.getLogger(__name__)

class LangChainIntegration:
    """Wrapper for various LangChain text splitters"""
    
    def __init__(self):
        self.splitters = {
            'recursive': RecursiveCharacterTextSplitter,
            'token': TokenTextSplitter,
            'character': CharacterTextSplitter
        }
    
    def get_splitter(self, splitter_type: str = 'recursive', **kwargs) -> object:
        """
        Get configured LangChain text splitter
        
        Args:
            splitter_type: Type of splitter to use
            **kwargs: Splitter configuration parameters
            
        Returns:
            Configured LangChain splitter instance
        """
        if splitter_type not in self.splitters:
            raise ValueError(f"Unknown splitter type: {splitter_type}")
        
        default_config = {
            'chunk_size': 2048,  # Characters (approximate)
            'chunk_overlap': 200,
            'length_function': len
        }
        
        config = {**default_config, **kwargs}
        
        splitter_class = self.splitters[splitter_type]
        return splitter_class(**config)
    
    def split_documents(self, text: str, splitter_type: str = 'recursive', **kwargs) -> List[str]:
        """
        Split text using specified LangChain splitter
        
        Args:
            text: Text to split
            splitter_type: Splitter to use
            **kwargs: Splitter parameters
            
        Returns:
            List of text chunks
        """
        try:
            splitter = self.get_splitter(splitter_type, **kwargs)
            chunks = splitter.split_text(text)
            
            logger.info(f"LangChain {splitter_type} splitter created {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"LangChain splitting failed: {str(e)}")
            raise