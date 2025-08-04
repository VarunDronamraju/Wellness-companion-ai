# ==== FILE 1: services/aiml-orchestration/src/orchestrators/response_synthesizer.py ====

"""
Response generation coordination for RAG pipeline.
Orchestrates LLM calls and response formatting.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
import sys
import os

sys.path.append('/app/src')

from .prompt_formatter import PromptFormatter
from llm.ollama_client import OllamaClient
from llm.response_handler import ResponseHandler
from llm.streaming_handler import StreamingHandler

logger = logging.getLogger(__name__)

@dataclass
class SynthesizedResponse:
    """Complete synthesized response with metadata."""
    response_text: str
    sources: List[str]
    confidence: float
    processing_time: float
    token_count: int
    is_streaming: bool
    metadata: Dict[str, Any]

class ResponseSynthesizer:
    """
    Coordinates response generation from context and query.
    """
    
    def __init__(self):
        self.prompt_formatter = PromptFormatter()
        self.ollama_client = OllamaClient()
        self.response_handler = ResponseHandler()
        self.streaming_handler = StreamingHandler()
        
        self.synthesis_stats = {
            'total_syntheses': 0,
            'successful_syntheses': 0,
            'failed_syntheses': 0,
            'streaming_syntheses': 0,
            'average_synthesis_time': 0.0,
            'total_synthesis_time': 0.0,
            'average_token_count': 0.0,
            'total_tokens_generated': 0
        }

    async def synthesize_response(
        self, 
        context: Any, 
        query: str,
        model_name: str = "gemma:3b",
        max_tokens: int = 500
    ) -> SynthesizedResponse:
        """
        Synthesize response from context and query.
        """
        start_time = datetime.now()
        
        try:
            # Format prompt based on context availability
            if hasattr(context, 'context_text') and context.context_text.strip():
                formatted_prompt = self.prompt_formatter.format_rag_prompt(context, query)
                sources = context.sources if hasattr(context, 'sources') else []
            else:
                formatted_prompt = self.prompt_formatter.format_fallback_prompt(query)
                sources = []
            
            logger.debug(f"Generated prompt length: {len(formatted_prompt)} chars")
            
            # Generate response using Ollama
           
            llm_response = await asyncio.to_thread(
                self.ollama_client.generate_response,
                prompt=formatted_prompt,
                model=model_name,
                max_tokens=max_tokens
)
            
            if not llm_response.get('success', False):
                raise Exception(f"LLM generation failed: {llm_response.get('error', 'Unknown error')}")
            
            # Process the raw response
            processed_response = self.response_handler.process_llm_response(
                llm_response['response']
            )
            
            # Format final response with citations
            final_response = self._format_final_response(processed_response, sources)
            
            # Calculate metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            token_count = len(final_response.split())
            confidence = self._calculate_response_confidence(final_response, context)
            
            synthesized = SynthesizedResponse(
                response_text=final_response,
                sources=sources,
                confidence=confidence,
                processing_time=processing_time,
                token_count=token_count,
                is_streaming=False,
                metadata={
                    'timestamp': datetime.now().isoformat(),
                    'model_used': model_name,
                    'prompt_length': len(formatted_prompt),
                    'has_context': bool(sources),
                    'llm_tokens': llm_response.get('tokens_used', 0)
                }
            )
            
            self._update_stats(True, processing_time, token_count, False)
            logger.info(f"Response synthesized: {token_count} tokens, confidence: {confidence:.2f}")
            
            return synthesized
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(False, processing_time, 0, False)
            logger.error(f"Error synthesizing response: {str(e)}")
            
            return self._create_error_response(query, str(e), processing_time)

    async def stream_response(
        self, 
        context: Any, 
        query: str,
        model_name: str = "gemma:3b"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream response generation in real-time.
        """
        start_time = datetime.now()
        
        try:
            # Format prompt
            if hasattr(context, 'context_text') and context.context_text.strip():
                formatted_prompt = self.prompt_formatter.format_streaming_prompt(context, query)
                sources = context.sources if hasattr(context, 'sources') else []
            else:
                formatted_prompt = self.prompt_formatter.format_fallback_prompt(query)
                sources = []
            
            # Start streaming from Ollama

            async for chunk in asyncio.to_thread(
                self.ollama_client.stream_response,
                prompt=formatted_prompt,
                model=model_name
                ):
                if chunk.get('success', False):
                    processed_chunk = self.streaming_handler.process_chunk(chunk)
                    
                    yield {
                        'type': 'chunk',
                        'content': processed_chunk['content'],
                        'sources': sources,
                        'metadata': {
                            'timestamp': datetime.now().isoformat(),
                            'chunk_index': processed_chunk['index']
                        }
                    }
                else:
                    yield {
                        'type': 'error',
                        'content': chunk.get('error', 'Streaming error'),
                        'metadata': {'timestamp': datetime.now().isoformat()}
                    }
            
            # Send completion signal
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(True, processing_time, 0, True)
            
            yield {
                'type': 'complete',
                'content': '',
                'sources': sources,
                'metadata': {
                    'processing_time': processing_time,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(False, processing_time, 0, True)
            
            yield {
                'type': 'error',
                'content': f"Streaming failed: {str(e)}",
                'metadata': {
                    'processing_time': processing_time,
                    'timestamp': datetime.now().isoformat()
                }
            }

    def _format_final_response(self, response: str, sources: List[str]) -> str:
        """Format final response with citations."""
        if not sources:
            return response
        
        # Add source citations
        citations = "\n\n**Sources:**\n"
        for i, source in enumerate(sources, 1):
            citations += f"{i}. {source}\n"
        
        return response + citations

    def _calculate_response_confidence(self, response: str, context: Any) -> float:
        """Calculate confidence in the generated response."""
        confidence = 0.5  # Base confidence
        
        # Length bonus
        if 50 <= len(response) <= 500:
            confidence += 0.2
        
        # Context availability bonus
        if hasattr(context, 'context_text') and context.context_text.strip():
            confidence += 0.2
            
            # Context relevance bonus
            if hasattr(context, 'relevance_score'):
                confidence += context.relevance_score * 0.1
        
        # Response quality indicators
        if any(phrase in response.lower() for phrase in ['based on', 'according to', 'the document states']):
            confidence += 0.1
        
        return min(1.0, confidence)

    def _create_error_response(self, query: str, error: str, processing_time: float) -> SynthesizedResponse:
        """Create error response when synthesis fails."""
        return SynthesizedResponse(
            response_text=f"I apologize, but I encountered an error while generating a response: {error}",
            sources=[],
            confidence=0.0,
            processing_time=processing_time,
            token_count=20,
            is_streaming=False,
            metadata={
                'timestamp': datetime.now().isoformat(),
                'error': error,
                'query': query
            }
        )

    def _update_stats(self, success: bool, processing_time: float, token_count: int, is_streaming: bool):
        """Update synthesis statistics."""
        self.synthesis_stats['total_syntheses'] += 1
        
        if success:
            self.synthesis_stats['successful_syntheses'] += 1
            if is_streaming:
                self.synthesis_stats['streaming_syntheses'] += 1
        else:
            self.synthesis_stats['failed_syntheses'] += 1
        
        self.synthesis_stats['total_synthesis_time'] += processing_time
        self.synthesis_stats['average_synthesis_time'] = (
            self.synthesis_stats['total_synthesis_time'] / 
            self.synthesis_stats['total_syntheses']
        )
        
        if token_count > 0:
            self.synthesis_stats['total_tokens_generated'] += token_count
            self.synthesis_stats['average_token_count'] = (
                self.synthesis_stats['total_tokens_generated'] / 
                max(1, self.synthesis_stats['successful_syntheses'])
            )

    def get_synthesis_statistics(self) -> Dict[str, Any]:
        """Get synthesis performance statistics."""
        return {
            **self.synthesis_stats,
            'success_rate': f"{(self.synthesis_stats['successful_syntheses'] / max(1, self.synthesis_stats['total_syntheses'])) * 100:.2f}%",
            'streaming_rate': f"{(self.synthesis_stats['streaming_syntheses'] / max(1, self.synthesis_stats['total_syntheses'])) * 100:.2f}%"
        }

