# services/data-layer/src/embedding_pipeline/chunk_manager.py
"""
Chunk metadata management and validation.
"""

import logging
from typing import List, Dict, Optional
import hashlib

logger = logging.getLogger(__name__)

class ChunkManager:
    """Manages chunk metadata and validation"""
    
    def __init__(self):
        self.processed_chunks = {}
    
    def add_metadata(self, chunks: List[Dict], document_metadata: Dict) -> List[Dict]:
        """
        Add document metadata to chunks
        
        Args:
            chunks: List of chunk dictionaries
            document_metadata: Document-level metadata
            
        Returns:
            Enhanced chunks with additional metadata
        """
        enhanced_chunks = []
        
        for chunk in chunks:
            # Generate content hash for deduplication
            content_hash = hashlib.md5(chunk['text'].encode()).hexdigest()
            
            enhanced_chunk = {
                **chunk,
                'content_hash': content_hash,
                'document_metadata': document_metadata,
                'created_at': document_metadata.get('processed_at'),
                'source_file': document_metadata.get('file_path', ''),
                'file_type': document_metadata.get('file_type', '')
            }
            
            enhanced_chunks.append(enhanced_chunk)
        
        return enhanced_chunks
    
    def validate_chunks(self, chunks: List[Dict]) -> Dict:
        """
        Validate chunk quality and statistics
        
        Args:
            chunks: List of chunks to validate
            
        Returns:
            Validation report
        """
        stats = {
            'total_chunks': len(chunks),
            'empty_chunks': 0,
            'oversized_chunks': 0,
            'average_tokens': 0,
            'average_characters': 0
        }
        
        total_tokens = 0
        total_chars = 0
        
        for chunk in chunks:
            if not chunk.get('text', '').strip():
                stats['empty_chunks'] += 1
            
            token_count = chunk.get('token_count', 0)
            if token_count > 512:
                stats['oversized_chunks'] += 1
            
            total_tokens += token_count
            total_chars += chunk.get('character_count', 0)
        
        if len(chunks) > 0:
            stats['average_tokens'] = total_tokens / len(chunks)
            stats['average_characters'] = total_chars / len(chunks)
        
        logger.info(f"Chunk validation: {stats}")
        return stats