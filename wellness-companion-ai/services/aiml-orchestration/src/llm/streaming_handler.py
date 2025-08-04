
# ==== FILE 5: services/aiml-orchestration/src/llm/streaming_handler.py ====

"""
Streaming response management for real-time LLM interactions.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)

@dataclass
class StreamChunk:
    """Individual streaming chunk with metadata."""
    content: str
    index: int
    timestamp: datetime
    is_complete: bool
    metadata: Dict[str, Any]

class StreamingHandler:
    """
    Handles streaming responses from LLM models.
    """
    
    def __init__(self, buffer_size: int = 1024):
        self.buffer_size = buffer_size
        self.streaming_stats = {
            'total_streams': 0,
            'successful_streams': 0,
            'failed_streams': 0,
            'total_chunks_processed': 0,
            'average_chunks_per_stream': 0.0,
            'average_stream_duration': 0.0,
            'total_stream_time': 0.0
        }
        
        # Buffer for chunk management
        self.chunk_buffer = []
        self.current_stream_id = None

    async def handle_stream(
        self, 
        ollama_stream: AsyncGenerator[Dict[str, Any], None],
        stream_id: str = None
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Handle streaming response from Ollama.
        """
        start_time = datetime.now()
        chunk_index = 0
        
        if not stream_id:
            stream_id = f"stream_{datetime.now().timestamp()}"
        
        self.current_stream_id = stream_id
        
        try:
            self.streaming_stats['total_streams'] += 1
            
            async for raw_chunk in ollama_stream:
                try:
                    processed_chunk = self.process_chunk(raw_chunk, chunk_index)
                    
                    if processed_chunk:
                        chunk_index += 1
                        yield processed_chunk
                        
                        # Buffer management
                        self._buffer_chunks(processed_chunk)
                        
                except Exception as e:
                    logger.error(f"Error processing stream chunk: {str(e)}")
                    continue
            
            # Stream completion
            duration = (datetime.now() - start_time).total_seconds()
            self._update_stats(True, duration, chunk_index)
            
            # Send completion chunk
            yield StreamChunk(
                content="",
                index=chunk_index,
                timestamp=datetime.now(),
                is_complete=True,
                metadata={
                    'stream_id': stream_id,
                    'total_chunks': chunk_index,
                    'duration': duration
                }
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self._update_stats(False, duration, chunk_index)
            logger.error(f"Error in stream handling: {str(e)}")
            
            # Send error chunk
            yield StreamChunk(
                content="",
                index=chunk_index,
                timestamp=datetime.now(),
                is_complete=True,
                metadata={
                    'stream_id': stream_id,
                    'error': str(e),
                    'duration': duration
                }
            )

    def process_chunk(self, raw_chunk: Dict[str, Any], index: int = 0) -> Optional[StreamChunk]:
        """
        Process individual streaming chunk.
        """
        try:
            # Extract content from different possible formats
            content = ""
            
            if 'response' in raw_chunk:
                content = raw_chunk['response']
            elif 'message' in raw_chunk:
                if isinstance(raw_chunk['message'], dict):
                    content = raw_chunk['message'].get('content', '')
                else:
                    content = str(raw_chunk['message'])
            elif 'content' in raw_chunk:
                content = raw_chunk['content']
            elif 'text' in raw_chunk:
                content = raw_chunk['text']
            else:
                # Fallback: convert entire chunk to string if no recognized format
                content = str(raw_chunk)
            
            # Basic content validation
            if not isinstance(content, str):
                content = str(content)
            
            # Create processed chunk
            return StreamChunk(
                content=content,
                index=index,
                timestamp=datetime.now(),
                is_complete=raw_chunk.get('done', False),
                metadata={
                    'stream_id': self.current_stream_id,
                    'raw_chunk_keys': list(raw_chunk.keys()),
                    'content_length': len(content)
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing chunk at index {index}: {str(e)}")
            return None

    def _buffer_chunks(self, chunk: StreamChunk):
        """Buffer management for streaming chunks."""
        self.chunk_buffer.append(chunk)
        
        # Keep buffer size manageable
        if len(self.chunk_buffer) > self.buffer_size:
            self.chunk_buffer = self.chunk_buffer[-self.buffer_size:]

    def get_buffered_content(self) -> str:
        """Get complete content from buffered chunks."""
        return ''.join(chunk.content for chunk in self.chunk_buffer)

    def clear_buffer(self):
        """Clear the chunk buffer."""
        self.chunk_buffer.clear()

    def _update_stats(self, success: bool, duration: float, chunk_count: int):
        """Update streaming statistics."""
        if success:
            self.streaming_stats['successful_streams'] += 1
        else:
            self.streaming_stats['failed_streams'] += 1
        
        self.streaming_stats['total_chunks_processed'] += chunk_count
        self.streaming_stats['total_stream_time'] += duration
        
        # Calculate averages
        total_streams = self.streaming_stats['total_streams']
        if total_streams > 0:
            self.streaming_stats['average_chunks_per_stream'] = (
                self.streaming_stats['total_chunks_processed'] / total_streams
            )
            self.streaming_stats['average_stream_duration'] = (
                self.streaming_stats['total_stream_time'] / total_streams
            )

    def get_streaming_statistics(self) -> Dict[str, Any]:
        """Get streaming performance statistics."""
        return {
            **self.streaming_stats,
            'success_rate': f"{(self.streaming_stats['successful_streams'] / max(1, self.streaming_stats['total_streams'])) * 100:.2f}%",
            'buffer_size': len(self.chunk_buffer),
            'current_stream_id': self.current_stream_id
        }

    async def stream_with_buffering(
        self, 
        ollama_stream: AsyncGenerator[Dict[str, Any], None],
        buffer_threshold: int = 50
    ) -> AsyncGenerator[str, None]:
        """
        Stream with intelligent buffering for smoother output.
        """
        buffer = ""
        
        async for chunk in self.handle_stream(ollama_stream):
            if not chunk.is_complete:
                buffer += chunk.content
                
                # Yield buffer content when threshold is reached or at sentence boundaries
                if (len(buffer) >= buffer_threshold or 
                    buffer.endswith(('.', '!', '?', '\n'))):
                    yield buffer
                    buffer = ""
            else:
                # Yield any remaining buffer content
                if buffer:
                    yield buffer
                break

    def estimate_completion_time(self, current_chunks: int, target_length: int = 200) -> float:
        """
        Estimate time to completion based on current streaming rate.
        """
        if current_chunks == 0 or self.streaming_stats['average_chunks_per_stream'] == 0:
            return 5.0  # Default estimate
        
        avg_content_per_chunk = target_length / max(1, self.streaming_stats['average_chunks_per_stream'])
        estimated_remaining_chunks = max(0, (target_length - current_chunks * avg_content_per_chunk) / avg_content_per_chunk)
        
        chunk_rate = self.streaming_stats['average_chunks_per_stream'] / max(0.1, self.streaming_stats['average_stream_duration'])
        
        return estimated_remaining_chunks / max(0.1, chunk_rate)

    def get_stream_health(self) -> Dict[str, Any]:
        """Get streaming system health metrics."""
        total_streams = self.streaming_stats['total_streams']
        success_rate = (self.streaming_stats['successful_streams'] / max(1, total_streams)) * 100
        
        health_status = "healthy"
        if success_rate < 90:
            health_status = "degraded"
        if success_rate < 70:
            health_status = "unhealthy"
        
        return {
            'status': health_status,
            'success_rate': f"{success_rate:.1f}%",
            'average_duration': f"{self.streaming_stats['average_stream_duration']:.2f}s",
            'buffer_utilization': f"{len(self.chunk_buffer)}/{self.buffer_size}",
            'recommendations': self._get_health_recommendations(success_rate)
        }

    def _get_health_recommendations(self, success_rate: float) -> List[str]:
        """Get recommendations based on streaming health."""
        recommendations = []
        
        if success_rate < 90:
            recommendations.append("Monitor stream error rates")
        
        if self.streaming_stats['average_stream_duration'] > 10:
            recommendations.append("Consider optimizing chunk processing")
        
        if len(self.chunk_buffer) > self.buffer_size * 0.8:
            recommendations.append("Increase buffer size or improve chunk consumption")
        
        return recommendations