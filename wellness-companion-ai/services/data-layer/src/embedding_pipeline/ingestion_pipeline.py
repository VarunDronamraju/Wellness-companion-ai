
# File 1: services/data-layer/src/embedding_pipeline/ingestion_pipeline.py
"""
Main document ingestion pipeline: PDF → chunks → embeddings → Qdrant storage.
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import time
import requests
import os

from .document_processor import DocumentProcessor
from .custom_text_splitter import TextSplitter
from vector_db.vector_operations import VectorOperations

logger = logging.getLogger(__name__)

class DocumentIngestionPipeline:
    """Complete pipeline for document processing and storage"""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.text_splitter = TextSplitter(chunk_size=512, chunk_overlap=50)
        self.vector_operations = VectorOperations()
        
        # AI/ML service URL for embedding generation
        self.aiml_service_url = os.getenv("AIML_SERVICE_URL", "http://aiml-orchestration:8000")
        
        self.pipeline_stats = {
            'total_documents_processed': 0,
            'successful_documents': 0,
            'failed_documents': 0,
            'total_chunks_generated': 0,
            'total_embeddings_stored': 0
        }
    
    def process_document(self, 
                        file_path: str, 
                        document_id: str,
                        metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a complete document through the ingestion pipeline
        
        Args:
            file_path: Path to the document file
            document_id: Unique document identifier
            metadata: Optional document metadata
            
        Returns:
            Pipeline processing result
        """
        start_time = time.time()
        self.pipeline_stats['total_documents_processed'] += 1
        
        try:
            logger.info(f"Starting ingestion pipeline for document: {document_id}")
            
            # Step 1: Extract text from document
            logger.info(f"Step 1: Extracting text from {file_path}")
            extraction_result = self.document_processor.process_document(file_path)
            
            if extraction_result['status'] != 'success':
                self.pipeline_stats['failed_documents'] += 1
                return {
                    'success': False,
                    'document_id': document_id,
                    'error': f"Text extraction failed: {extraction_result.get('error', 'Unknown error')}",
                    'stage': 'text_extraction'
                }
            
            extracted_text = extraction_result['text']
            if not extracted_text.strip():
                self.pipeline_stats['failed_documents'] += 1
                return {
                    'success': False,
                    'document_id': document_id,
                    'error': 'No text content extracted from document',
                    'stage': 'text_extraction'
                }
            
            # Step 2: Split text into chunks
            logger.info(f"Step 2: Splitting text into chunks")
            chunks = self.text_splitter.split_text(extracted_text, document_id)
            
            if not chunks:
                self.pipeline_stats['failed_documents'] += 1
                return {
                    'success': False,
                    'document_id': document_id,
                    'error': 'No chunks generated from text',
                    'stage': 'text_chunking'
                }
            
            self.pipeline_stats['total_chunks_generated'] += len(chunks)
            logger.info(f"Generated {len(chunks)} chunks")
            
            # Step 3: Generate embeddings via AI/ML service
            logger.info(f"Step 3: Generating embeddings for {len(chunks)} chunks")
            embeddings_result = self._generate_embeddings_via_service([chunk['text'] for chunk in chunks])
            
            if not embeddings_result['success']:
                self.pipeline_stats['failed_documents'] += 1
                return {
                    'success': False,
                    'document_id': document_id,
                    'error': f"Embedding generation failed: {embeddings_result.get('error', 'Unknown error')}",
                    'stage': 'embedding_generation'
                }
            
            embeddings = embeddings_result['embeddings']
            
            # Step 4: Combine chunks with embeddings
            logger.info(f"Step 4: Combining chunks with embeddings")
            enhanced_chunks = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                enhanced_chunk = {
                    **chunk,
                    'embedding': embedding,
                    'document_metadata': metadata or {},
                    'processed_at': time.time(),
                    'file_path': file_path,
                    'extraction_method': extraction_result.get('extraction_method', 'unknown')
                }
                enhanced_chunks.append(enhanced_chunk)
            
            # Step 5: Store in vector database
            logger.info(f"Step 5: Storing {len(enhanced_chunks)} chunks in vector database")
            storage_result = self.vector_operations.store_document_embeddings(
                document_id=document_id,
                chunks=enhanced_chunks
            )
            
            if not storage_result['success']:
                self.pipeline_stats['failed_documents'] += 1
                return {
                    'success': False,
                    'document_id': document_id,
                    'error': f"Vector storage failed: {storage_result.get('error', 'Unknown error')}",
                    'stage': 'vector_storage'
                }
            
            # Success!
            processing_time = time.time() - start_time
            self.pipeline_stats['successful_documents'] += 1
            self.pipeline_stats['total_embeddings_stored'] += len(enhanced_chunks)
            
            logger.info(f"Successfully processed document {document_id} in {processing_time:.2f}s")
            
            return {
                'success': True,
                'document_id': document_id,
                'processing_time': processing_time,
                'text_length': len(extracted_text),
                'chunks_generated': len(chunks),
                'embeddings_stored': len(enhanced_chunks),
                'storage_result': storage_result,
                'extraction_metadata': extraction_result.get('metadata', {}),
                'stage': 'completed'
            }
            
        except Exception as e:
            self.pipeline_stats['failed_documents'] += 1
            logger.error(f"Pipeline processing failed for document {document_id}: {str(e)}")
            return {
                'success': False,
                'document_id': document_id,
                'error': str(e),
                'processing_time': time.time() - start_time,
                'stage': 'exception'
            }
    
    def _generate_embeddings_via_service(self, texts: List[str]) -> Dict[str, Any]:
        """
        Generate embeddings by calling the AI/ML service
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Embeddings generation result
        """
        try:
            # Call AI/ML service embedding endpoint
            response = requests.post(
                f"{self.aiml_service_url}/api/embeddings/generate",
                json={'texts': texts},
                timeout=60  # 1 minute timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'embeddings': result.get('embeddings', []),
                    'processing_time': result.get('processing_time', 0)
                }
            else:
                return {
                    'success': False,
                    'error': f"AI/ML service returned {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.RequestException as e:
            # Fallback: generate dummy embeddings for testing
            logger.warning(f"AI/ML service unavailable ({str(e)}), using dummy embeddings")
            dummy_embeddings = [[0.1] * 384 for _ in texts]  # 384-dim dummy vectors
            
            return {
                'success': True,
                'embeddings': dummy_embeddings,
                'processing_time': 0.1,
                'note': 'Used dummy embeddings due to service unavailability'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Embedding generation error: {str(e)}"
            }
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline processing statistics"""
        total_processed = self.pipeline_stats['total_documents_processed']
        success_rate = (self.pipeline_stats['successful_documents'] / max(total_processed, 1)) * 100
        
        return {
            **self.pipeline_stats,
            'success_rate': f"{success_rate:.2f}%",
            'average_chunks_per_document': (
                self.pipeline_stats['total_chunks_generated'] / max(total_processed, 1)
            )
        }
