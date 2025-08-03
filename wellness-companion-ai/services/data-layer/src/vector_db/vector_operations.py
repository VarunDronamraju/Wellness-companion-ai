
# File 1: services/data-layer/src/vector_db/vector_operations.py
"""
CRUD operations for vector data in Qdrant.
"""

import logging
from typing import List, Dict, Optional, Any, Tuple
from .qdrant_client import DataLayerQdrantClient
import uuid
import time

logger = logging.getLogger(__name__)

class VectorOperations:
    """High-level vector operations for document storage and retrieval"""
    
    def __init__(self):
        self.client = DataLayerQdrantClient()
        self.default_collection = "documents"
        
        # Ensure connection
        if not self.client.connected:
            self.client.connect()
    
    def store_document_embeddings(self, 
                                document_id: str,
                                chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Store embeddings for a document with chunks
        
        Args:
            document_id: Unique document identifier
            chunks: List of chunks with text, embeddings, and metadata
            
        Returns:
            Storage result with statistics
        """
        start_time = time.time()
        
        try:
            if not chunks:
                return {
                    'success': False,
                    'error': 'No chunks provided',
                    'document_id': document_id
                }
            
            # Prepare vectors and payloads
            vectors = []
            payloads = []
            point_ids = []
            
            for i, chunk in enumerate(chunks):
                if 'embedding' not in chunk:
                    logger.warning(f"Chunk {i} missing embedding, skipping")
                    continue
                
                # Generate unique point ID
                point_id = f"{document_id}_chunk_{i}_{str(uuid.uuid4())[:8]}"
                point_ids.append(point_id)
                
                # Extract embedding vector
                vectors.append(chunk['embedding'])
                
                # Prepare payload with metadata
                payload = {
                    'document_id': document_id,
                    'chunk_id': chunk.get('chunk_id', f"chunk_{i}"),
                    'text': chunk.get('text', ''),
                    'chunk_index': i,
                    'token_count': chunk.get('token_count', 0),
                    'character_count': chunk.get('character_count', 0),
                    'stored_at': time.time(),
                    'embedding_model': chunk.get('embedding_model', 'unknown')
                }
                
                # Add any additional metadata
                for key, value in chunk.items():
                    if key not in ['embedding', 'text'] and not key.startswith('_'):
                        payload[f"meta_{key}"] = value
                
                payloads.append(payload)
            
            if not vectors:
                return {
                    'success': False,
                    'error': 'No valid embeddings found in chunks',
                    'document_id': document_id
                }
            
            # Store in Qdrant
            success = self.client.upsert_vectors(
                collection_name=self.default_collection,
                vectors=vectors,
                payloads=payloads,
                ids=point_ids
            )
            
            processing_time = time.time() - start_time
            
            if success:
                logger.info(f"Stored {len(vectors)} embeddings for document {document_id}")
                return {
                    'success': True,
                    'document_id': document_id,
                    'stored_chunks': len(vectors),
                    'point_ids': point_ids,
                    'processing_time': processing_time,
                    'collection': self.default_collection
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to store vectors in Qdrant',
                    'document_id': document_id
                }
                
        except Exception as e:
            logger.error(f"Vector storage failed for document {document_id}: {str(e)}")
            return {
                'success': False,
                'document_id': document_id,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def search_similar_chunks(self, 
                            query_vector: List[float],
                            limit: int = 10,
                            score_threshold: float = 0.7,
                            document_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for similar document chunks
        
        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            document_filter: Optional document ID to filter by
            
        Returns:
            Search results with chunks and scores
        """
        try:
            # TODO: Add document filtering when needed
            results = self.client.client.search(
                collection_name=self.default_collection,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_result = {
                    'score': result.score,
                    'document_id': result.payload.get('document_id'),
                    'chunk_id': result.payload.get('chunk_id'),
                    'text': result.payload.get('text', ''),
                    'chunk_index': result.payload.get('chunk_index', 0),
                    'metadata': {
                        'token_count': result.payload.get('token_count', 0),
                        'character_count': result.payload.get('character_count', 0),
                        'embedding_model': result.payload.get('embedding_model'),
                        'stored_at': result.payload.get('stored_at')
                    }
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"Found {len(formatted_results)} similar chunks")
            return {
                'success': True,
                'results': formatted_results,
                'query_info': {
                    'limit': limit,
                    'score_threshold': score_threshold,
                    'results_count': len(formatted_results)
                }
            }
            
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'results': []
            }
    
    def delete_document_vectors(self, document_id: str) -> Dict[str, Any]:
        """
        Delete all vectors for a document
        
        Args:
            document_id: Document identifier
            
        Returns:
            Deletion result
        """
        try:
            # Use filter-based deletion
            filter_condition = {
                "must": [
                    {
                        "key": "document_id",
                        "match": {"value": document_id}
                    }
                ]
            }
            
            success = self.client.delete_vectors(
                collection_name=self.default_collection,
                filter_condition=filter_condition
            )
            
            if success:
                logger.info(f"Deleted vectors for document {document_id}")
                return {
                    'success': True,
                    'document_id': document_id,
                    'message': 'Document vectors deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'document_id': document_id,
                    'error': 'Failed to delete document vectors'
                }
                
        except Exception as e:
            logger.error(f"Vector deletion failed for document {document_id}: {str(e)}")
            return {
                'success': False,
                'document_id': document_id,
                'error': str(e)
            }
    
    def get_document_chunks(self, document_id: str) -> Dict[str, Any]:
        """
        Get all chunks for a specific document
        
        Args:
            document_id: Document identifier
            
        Returns:
            List of document chunks
        """
        try:
            # Search with very low threshold to get all chunks
            dummy_vector = [0.0] * 384  # Dummy vector for search
            
            results = self.client.client.search(
                collection_name=self.default_collection,
                query_vector=dummy_vector,
                limit=1000,  # High limit to get all chunks
                score_threshold=0.0  # Get all results
            )
            
            # Filter by document_id
            document_chunks = []
            for result in results:
                if result.payload.get('document_id') == document_id:
                    chunk_info = {
                        'chunk_id': result.payload.get('chunk_id'),
                        'text': result.payload.get('text', ''),
                        'chunk_index': result.payload.get('chunk_index', 0),
                        'token_count': result.payload.get('token_count', 0),
                        'character_count': result.payload.get('character_count', 0),
                        'stored_at': result.payload.get('stored_at')
                    }
                    document_chunks.append(chunk_info)
            
            # Sort by chunk_index
            document_chunks.sort(key=lambda x: x['chunk_index'])
            
            return {
                'success': True,
                'document_id': document_id,
                'chunks': document_chunks,
                'total_chunks': len(document_chunks)
            }
            
        except Exception as e:
            logger.error(f"Failed to get chunks for document {document_id}: {str(e)}")
            return {
                'success': False,
                'document_id': document_id,
                'error': str(e),
                'chunks': []
            }
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection"""
        try:
            info = self.client.get_collection_info(self.default_collection)
            return {
                'success': True,
                'collection_name': self.default_collection,
                'stats': info
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }