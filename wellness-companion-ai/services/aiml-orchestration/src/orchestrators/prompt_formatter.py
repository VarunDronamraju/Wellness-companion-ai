
# ==== FILE 2: services/aiml-orchestration/src/orchestrators/prompt_formatter.py ====

"""
LLM prompt formatting for different scenarios.
Creates optimized prompts from context and query.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class PromptFormatter:
    """
    Formats prompts for different LLM scenarios.
    """
    
    def __init__(self):
        self.format_stats = {
            'total_prompts_formatted': 0,
            'rag_prompts': 0,
            'fallback_prompts': 0,
            'streaming_prompts': 0,
            'average_prompt_length': 0.0,
            'total_prompt_length': 0
        }

    def format_rag_prompt(self, context: Any, query: str) -> str:
        """Format RAG prompt with context and query."""
        try:
            # Extract context text
            context_text = ""
            if hasattr(context, 'context_text'):
                context_text = context.context_text
            elif isinstance(context, str):
                context_text = context
            
            # Build the RAG prompt
            prompt = f"""You are a helpful AI assistant. Based on the provided context, answer the user's question accurately and comprehensively.

Context:
{context_text}

Question: {query}

Instructions:
- Use only the information provided in the context
- If the context doesn't contain enough information, say so clearly
- Provide specific details when available
- Be concise but thorough
- If you reference specific information, indicate it came from the provided context

Answer:"""

            self._update_stats('rag', len(prompt))
            return prompt
            
        except Exception as e:
            logger.error(f"Error formatting RAG prompt: {str(e)}")
            return self.format_fallback_prompt(query)

    def format_fallback_prompt(self, query: str) -> str:
        """Format fallback prompt when no context is available."""
        prompt = f"""You are a helpful AI assistant. Please answer the following question to the best of your knowledge.

Question: {query}

Instructions:
- Provide a helpful and accurate response
- If you're unsure about specific details, acknowledge the limitation
- Be clear and concise
- Use your general knowledge to provide useful information

Answer:"""

        self._update_stats('fallback', len(prompt))
        return prompt

    def format_streaming_prompt(self, context: Any, query: str) -> str:
        """Format prompt optimized for streaming responses."""
        try:
            context_text = ""
            if hasattr(context, 'context_text'):
                context_text = context.context_text
            elif isinstance(context, str):
                context_text = context
            
            prompt = f"""You are a helpful AI assistant providing a streaming response. Answer comprehensively based on the context provided.

Context:
{context_text}

Question: {query}

Instructions:
- Provide a detailed, well-structured response
- Start with the most important information
- Use the context information to support your answer
- Be thorough but maintain good flow for streaming
- Structure your response with clear points

Response:"""

            self._update_stats('streaming', len(prompt))
            return prompt
            
        except Exception as e:
            logger.error(f"Error formatting streaming prompt: {str(e)}")
            return self.format_fallback_prompt(query)

    def format_custom_prompt(
        self, 
        system_message: str, 
        context: str, 
        query: str,
        instructions: List[str] = None
    ) -> str:
        """Format custom prompt with specific parameters."""
        instruction_text = ""
        if instructions:
            instruction_text = "\n".join(f"- {instruction}" for instruction in instructions)
        
        prompt = f"""{system_message}

Context:
{context}

Question: {query}

Instructions:
{instruction_text}

Response:"""

        self._update_stats('custom', len(prompt))
        return prompt

    def _build_context_section(self, context: Any) -> str:
        """Build formatted context section for prompts."""
        if not context:
            return "No specific context available."
        
        if hasattr(context, 'chunks') and context.chunks:
            # Format multiple chunks with sources
            formatted_chunks = []
            for i, chunk in enumerate(context.chunks, 1):
                source = getattr(chunk, 'source', f'Source {i}')
                content = getattr(chunk, 'content', str(chunk))
                formatted_chunks.append(f"[{source}]\n{content}")
            
            return "\n\n".join(formatted_chunks)
        
        elif hasattr(context, 'context_text'):
            return context.context_text
        
        elif isinstance(context, str):
            return context
        
        else:
            return str(context)

    def _update_stats(self, prompt_type: str, prompt_length: int):
        """Update formatting statistics."""
        self.format_stats['total_prompts_formatted'] += 1
        self.format_stats['total_prompt_length'] += prompt_length
        
        if prompt_type == 'rag':
            self.format_stats['rag_prompts'] += 1
        elif prompt_type == 'fallback':
            self.format_stats['fallback_prompts'] += 1
        elif prompt_type == 'streaming':
            self.format_stats['streaming_prompts'] += 1
        
        self.format_stats['average_prompt_length'] = (
            self.format_stats['total_prompt_length'] / 
            self.format_stats['total_prompts_formatted']
        )

    def get_formatting_statistics(self) -> Dict[str, Any]:
        """Get prompt formatting statistics."""
        return self.format_stats

    def optimize_prompt_for_model(self, prompt: str, model_name: str) -> str:
        """Optimize prompt for specific model characteristics."""
        if 'gemma' in model_name.lower():
            # Gemma prefers concise, structured prompts
            return self._optimize_for_gemma(prompt)
        elif 'llama' in model_name.lower():
            # LLaMA handles longer, more detailed prompts
            return self._optimize_for_llama(prompt)
        else:
            return prompt

    def _optimize_for_gemma(self, prompt: str) -> str:
        """Optimize prompt for Gemma model."""
        # Keep prompt concise and well-structured
        return prompt

    def _optimize_for_llama(self, prompt: str) -> str:
        """Optimize prompt for LLaMA model."""
        # LLaMA can handle more detailed instructions
        return prompt

