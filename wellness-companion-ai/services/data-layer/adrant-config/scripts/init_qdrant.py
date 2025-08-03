# services/data-layer/scripts/init_qdrant.py
"""
Qdrant Vector Database Initialization Script
Creates collections for Wellness Companion AI
"""

import requests
import json
import time
import os
from typing import Dict, Any

class QdrantInitializer:
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.base_url = f"http://{host}:{port}"
        self.headers = {"Content-Type": "application/json"}
        
    def wait_for_health(self, max_retries: int = 30, delay: int = 2):
        """Wait for Qdrant to be healthy"""
        for attempt in range(max_retries):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Qdrant is healthy and ready")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            print(f"⏳ Waiting for Qdrant... (attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)
        
        raise Exception("❌ Qdrant health check failed")
    
    def create_collection(self, collection_name: str, config: Dict[str, Any]):
        """Create a collection with specified configuration"""
        try:
            # Check if collection exists
            response = requests.get(f"{self.base_url}/collections/{collection_name}")
            if response.status_code == 200:
                print(f"✅ Collection '{collection_name}' already exists")
                return True
            
            # Create collection
            response = requests.put(
                f"{self.base_url}/collections/{collection_name}",
                headers=self.headers,
                json=config,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Created collection '{collection_name}'")
                return True
            else:
                print(f"❌ Failed to create collection '{collection_name}': {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating collection '{collection_name}': {e}")
            return False
    
    def initialize_collections(self):
        """Initialize all required collections"""
        
        # Document Embeddings Collection
        documents_config = {
            "vectors": {
                "size": 384,  # all-MiniLM-L6-v2 embedding size
                "distance": "Cosine"
            },
            "optimizers_config": {
                "deleted_threshold": 0.2,
                "vacuum_min_vector_number": 1000,
                "default_segment_number": 0,
                "max_segment_size": 20000,
                "memmap_threshold": 50000,
                "indexing_threshold": 20000,
                "flush_interval_sec": 5,
                "max_optimization_threads": 1
            },
            "replication_factor": 1,
            "write_consistency_factor": 1
        }
        
        # User Conversations Collection (for conversation context)
        conversations_config = {
            "vectors": {
                "size": 384,
                "distance": "Cosine"
            },
            "optimizers_config": {
                "deleted_threshold": 0.2,
                "vacuum_min_vector_number": 100,
                "default_segment_number": 0,
                "max_segment_size": 10000,
                "memmap_threshold": 20000,
                "indexing_threshold": 10000,
                "flush_interval_sec": 5,
                "max_optimization_threads": 1
            },
            "replication_factor": 1,
            "write_consistency_factor": 1
        }
        
        # Web Search Cache Collection (for cached web results)
        web_cache_config = {
            "vectors": {
                "size": 384,
                "distance": "Cosine"
            },
            "optimizers_config": {
                "deleted_threshold": 0.3,
                "vacuum_min_vector_number": 500,
                "default_segment_number": 0,
                "max_segment_size": 5000,
                "memmap_threshold": 10000,
                "indexing_threshold": 5000,
                "flush_interval_sec": 10,
                "max_optimization_threads": 1
            },
            "replication_factor": 1,
            "write_consistency_factor": 1
        }
        
        collections = {
            "wellness_documents": documents_config,
            "wellness_conversations": conversations_config,
            "wellness_web_cache": web_cache_config
        }
        
        success_count = 0
        for collection_name, config in collections.items():
            if self.create_collection(collection_name, config):
                success_count += 1
        
        print(f"\n🎯 Qdrant Initialization Complete!")
        print(f"✅ Successfully created {success_count}/{len(collections)} collections")
        
        if success_count == len(collections):
            print("🚀 Qdrant is ready for Wellness Companion AI!")
            return True
        else:
            print("⚠️  Some collections failed to create")
            return False

def main():
    """Main initialization function"""
    print("🚀 Initializing Qdrant for Wellness Companion AI...")
    
    # Get Qdrant connection details from environment
    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", "6333"))
    
    initializer = QdrantInitializer(host, port)
    
    try:
        # Wait for Qdrant to be ready
        initializer.wait_for_health()
        
        # Initialize collections
        success = initializer.initialize_collections()
        
        if success:
            print("\n✅ Qdrant initialization completed successfully!")
            exit(0)
        else:
            print("\n❌ Qdrant initialization failed!")
            exit(1)
            
    except Exception as e:
        print(f"\n❌ Fatal error during Qdrant initialization: {e}")
        exit(1)

if __name__ == "__main__":
    main()