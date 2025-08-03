
# File 2: services/data-layer/src/vector_db/collection_manager.py
"""
Collection management for different types of vector data.
"""

import logging
from typing import Dict, List, Optional, Any
from .qdrant_client import DataLayerQdrantClient

logger = logging.getLogger(__name__)

class CollectionManager:
    """Manages multiple vector collections for different data types"""
    
    COLLECTION_CONFIGS = {
        'documents': {
            'vector_size': 384,
            'distance': 'Cosine',
            'description': 'Document chunks and embeddings'
        },
        'conversations': {
            'vector_size': 384,
            'distance': 'Cosine',
            'description': 'Chat conversations and context'
        },
        'web_cache': {
            'vector_size': 384,
            'distance': 'Cosine',
            'description': 'Web search results cache'
        }
    }
    
    def __init__(self):
        self.client = DataLayerQdrantClient()
        
        # Ensure connection
        if not self.client.connected:
            self.client.connect()
    
    def initialize_collections(self) -> Dict[str, Any]:
        """
        Initialize all required collections
        
        Returns:
            Initialization results for each collection
        """
        results = {}
        
        for collection_name, config in self.COLLECTION_CONFIGS.items():
            try:
                # Check if collection exists
                existing_collections = self.client.client.get_collections()
                collection_names = [col.name for col in existing_collections.collections]
                
                if collection_name in collection_names:
                    logger.info(f"Collection {collection_name} already exists")
                    results[collection_name] = {
                        'status': 'exists',
                        'action': 'skipped'
                    }
                else:
                    # Create collection
                    success = self.client.create_collection(
                        collection_name=collection_name,
                        vector_size=config['vector_size'],
                        distance=config['distance']
                    )
                    
                    if success:
                        logger.info(f"Created collection: {collection_name}")
                        results[collection_name] = {
                            'status': 'created',
                            'action': 'success',
                            'config': config
                        }
                    else:
                        logger.error(f"Failed to create collection: {collection_name}")
                        results[collection_name] = {
                            'status': 'failed',
                            'action': 'error',
                            'error': 'Creation failed'
                        }
                        
            except Exception as e:
                logger.error(f"Error initializing collection {collection_name}: {str(e)}")
                results[collection_name] = {
                    'status': 'error',
                    'action': 'exception',
                    'error': str(e)
                }
        
        return {
            'success': all(r['status'] in ['exists', 'created'] for r in results.values()),
            'collections': results,
            'total_collections': len(self.COLLECTION_CONFIGS),
            'initialized_count': len([r for r in results.values() if r['status'] in ['exists', 'created']])
        }
    
    def get_collection_status(self) -> Dict[str, Any]:
        """Get status of all collections"""
        try:
            existing_collections = self.client.client.get_collections()
            collection_names = [col.name for col in existing_collections.collections]
            
            status = {}
            for collection_name, config in self.COLLECTION_CONFIGS.items():
                if collection_name in collection_names:
                    try:
                        info = self.client.get_collection_info(collection_name)
                        status[collection_name] = {
                            'exists': True,
                            'info': info,
                            'config': config
                        }
                    except Exception as e:
                        status[collection_name] = {
                            'exists': True,
                            'error': str(e),
                            'config': config
                        }
                else:
                    status[collection_name] = {
                        'exists': False,
                        'config': config
                    }
            
            return {
                'success': True,
                'collections': status,
                'total_existing': len([s for s in status.values() if s['exists']])
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """
        Delete a specific collection
        
        Args:
            collection_name: Name of collection to delete
            
        Returns:
            Deletion result
        """
        try:
            if collection_name not in self.COLLECTION_CONFIGS:
                return {
                    'success': False,
                    'error': f'Unknown collection: {collection_name}'
                }
            
            self.client.client.delete_collection(collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            
            return {
                'success': True,
                'collection_name': collection_name,
                'action': 'deleted'
            }
            
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {str(e)}")
            return {
                'success': False,
                'collection_name': collection_name,
                'error': str(e)
            }
    
    def recreate_collection(self, collection_name: str) -> Dict[str, Any]:
        """
        Delete and recreate a collection (useful for schema changes)
        
        Args:
            collection_name: Name of collection to recreate
            
        Returns:
            Recreation result
        """
        try:
            # Delete first
            delete_result = self.delete_collection(collection_name)
            if not delete_result['success']:
                return delete_result
            
            # Wait a moment
            import time
            time.sleep(1)
            
            # Recreate
            config = self.COLLECTION_CONFIGS[collection_name]
            success = self.client.create_collection(
                collection_name=collection_name,
                vector_size=config['vector_size'],
                distance=config['distance']
            )
            
            if success:
                return {
                    'success': True,
                    'collection_name': collection_name,
                    'action': 'recreated'
                }
            else:
                return {
                    'success': False,
                    'collection_name': collection_name,
                    'error': 'Failed to recreate after deletion'
                }
                
        except Exception as e:
            logger.error(f"Failed to recreate collection {collection_name}: {str(e)}")
            return {
                'success': False,
                'collection_name': collection_name,
                'error': str(e)
            }