"""Specialized context extractor for conversation history."""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


@dataclass
class ConversationChunk:
    """Represents a conversation chunk with enhanced metadata."""
    content: str
    role: str  # 'user' or 'assistant'
    timestamp: datetime
    message_id: str
    conversation_id: str
    score: float
    topic: Optional[str]
    intent: Optional[str]
    metadata: Dict[str, Any]


class ConversationContextExtractor:
    """Specialized extractor for processing conversation history context."""
    
    def __init__(self, 
                 max_conversation_chunks: int = 5,
                 time_decay_hours: float = 24.0,
                 prefer_assistant_responses: bool = True,
                 topic_continuity_boost: float = 0.3):
        """
        Initialize conversation context extractor.
        
        Args:
            max_conversation_chunks: Maximum conversation chunks to include
            time_decay_hours: Hours after which conversation relevance decays
            prefer_assistant_responses: Give higher scores to assistant responses
            topic_continuity_boost: Boost for messages related to current topic
        """
        self.max_conversation_chunks = max_conversation_chunks
        self.time_decay_hours = time_decay_hours
        self.prefer_assistant_responses = prefer_assistant_responses
        self.topic_continuity_boost = topic_continuity_boost
        
        # Common question patterns for intent detection
        self.question_patterns = [
            r'\bwhat\s+is\b',
            r'\bhow\s+(?:do|does|can|to)\b',
            r'\bwhy\s+(?:is|does|do|would)\b',
            r'\bwhen\s+(?:is|does|do|will)\b',
            r'\bwhere\s+(?:is|does|can)\b',
            r'\bwho\s+(?:is|are|was)\b',
            r'\bwhich\s+(?:is|are|one)\b',
            r'\bcan\s+you\b',
            r'\?'
        ]
        
        logger.info("ConversationContextExtractor initialized")
    
    def extract_conversation_context(self, 
                                   conversation_history: List[Dict[str, Any]], 
                                   current_query: str,
                                   conversation_id: Optional[str] = None) -> List[ConversationChunk]:
        """
        Extract and process conversation context.
        
        Args:
            conversation_history: List of conversation messages
            current_query: Current user query for relevance scoring
            conversation_id: ID of the current conversation
            
        Returns:
            List of processed conversation chunks
        """
        try:
            if not conversation_history:
                return []
            
            # Convert raw messages to conversation chunks
            chunks = self._create_conversation_chunks(conversation_history, conversation_id or "current")
            
            # Filter and enhance chunks
            enhanced_chunks = self._enhance_conversation_chunks(chunks, current_query)
            
            # Select most relevant chunks
            selected_chunks = self._select_relevant_chunks(enhanced_chunks, current_query)
            
            logger.info(f"Extracted {len(selected_chunks)} conversation chunks from {len(conversation_history)} messages")
            return selected_chunks
            
        except Exception as e:
            logger.error(f"Error extracting conversation context: {e}")
            return []
    
    def _create_conversation_chunks(self, 
                                  messages: List[Dict[str, Any]], 
                                  conversation_id: str) -> List[ConversationChunk]:
        """Convert raw messages to conversation chunks."""
        chunks = []
        
        for i, message in enumerate(messages):
            try:
                content = message.get('content', message.get('message', ''))
                role = message.get('role', 'user')
                
                # Parse timestamp
                timestamp_str = message.get('timestamp', message.get('created_at', ''))
                timestamp = self._parse_timestamp(timestamp_str)
                
                message_id = message.get('id', message.get('message_id', f"msg_{i}"))
                
                if content and len(content.strip()) > 5:
                    # Extract topic and intent
                    topic = self._extract_topic(content)
                    intent = self._extract_intent(content, role)
                    
                    chunk = ConversationChunk(
                        content=content,
                        role=role,
                        timestamp=timestamp,
                        message_id=message_id,
                        conversation_id=conversation_id,
                        score=0.0,  # Will be calculated later
                        topic=topic,
                        intent=intent,
                        metadata=message.get('metadata', {})
                    )
                    chunks.append(chunk)
                    
            except Exception as e:
                logger.warning(f"Error creating conversation chunk: {e}")
                continue
        
        return chunks
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime object."""
        if not timestamp_str:
            return datetime.now()
        
        # Try common timestamp formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        # If all else fails, return current time
        logger.warning(f"Could not parse timestamp: {timestamp_str}")
        return datetime.now()
    
    def _extract_topic(self, content: str) -> Optional[str]:
        """Extract main topic from message content."""
        # Simple topic extraction based on keywords
        content_lower = content.lower()
        
        # Common topic indicators
        topic_patterns = {
            'document': ['document', 'file', 'pdf', 'upload', 'text'],
            'search': ['search', 'find', 'look', 'query'],
            'help': ['help', 'how', 'explain', 'what'],
            'error': ['error', 'problem', 'issue', 'bug', 'fail'],
            'configuration': ['config', 'setting', 'setup', 'configure'],
            'analysis': ['analyze', 'analysis', 'summary', 'report']
        }
        
        for topic, keywords in topic_patterns.items():
            if any(keyword in content_lower for keyword in keywords):
                return topic
        
        # Extract potential topic from first few words if they seem like a topic
        words = content.split()[:5]
        topic_candidates = [word for word in words if len(word) > 3 and word.isalpha()]
        
        if topic_candidates:
            return topic_candidates[0].lower()
        
        return None
    
    def _extract_intent(self, content: str, role: str) -> Optional[str]:
        """Extract intent from message content."""
        if role == 'assistant':
            # Assistant intents
            if any(phrase in content.lower() for phrase in ['here is', 'here are', 'i found']):
                return 'provide_info'
            elif any(phrase in content.lower() for phrase in ['i can help', 'let me', 'i will']):
                return 'offer_help'
            elif any(phrase in content.lower() for phrase in ['error', 'sorry', 'apologize']):
                return 'error_response'
            else:
                return 'respond'
        else:
            # User intents
            content_lower = content.lower()
            
            # Check for question patterns
            if any(re.search(pattern, content_lower) for pattern in self.question_patterns):
                return 'question'
            
            # Check for commands
            if any(word in content_lower for word in ['upload', 'delete', 'create', 'update']):
                return 'command'
            
            # Check for requests
            if any(phrase in content_lower for phrase in ['can you', 'please', 'could you']):
                return 'request'
            
            return 'statement'
    
    def _enhance_conversation_chunks(self, 
                                   chunks: List[ConversationChunk], 
                                   current_query: str) -> List[ConversationChunk]:
        """Enhance conversation chunks with relevance scores."""
        if not chunks:
            return chunks
        
        current_time = datetime.now()
        current_topic = self._extract_topic(current_query)
        current_intent = self._extract_intent(current_query, 'user')
        
        for chunk in chunks:
            score = 0.0
            
            # Base score based on role
            if chunk.role == 'assistant' and self.prefer_assistant_responses:
                score += 0.6
            else:
                score += 0.4
            
            # Time decay score
            time_diff = current_time - chunk.timestamp
            hours_diff = time_diff.total_seconds() / 3600
            time_score = max(0.1, 1.0 - (hours_diff / self.time_decay_hours))
            score *= time_score
            
            # Topic continuity boost
            if current_topic and chunk.topic == current_topic:
                score += self.topic_continuity_boost
            
            # Intent matching boost
            if chunk.role == 'assistant' and current_intent == 'question':
                if chunk.intent == 'provide_info':
                    score += 0.2
            
            # Content relevance (simple keyword matching)
            content_relevance = self._calculate_content_relevance(chunk.content, current_query)
            score += content_relevance * 0.3
            
            # Recency boost for very recent messages
            if hours_diff < 1.0:
                score += 0.2
            
            # Length penalty for very short or very long messages
            word_count = len(chunk.content.split())
            if word_count < 5:
                score *= 0.7
            elif word_count > 200:
                score *= 0.8
            
            chunk.score = min(1.0, score)  # Cap at 1.0
        
        return chunks
    
    def _calculate_content_relevance(self, content: str, query: str) -> float:
        """Calculate content relevance using simple keyword matching."""
        if not content or not query:
            return 0.0
        
        content_words = set(content.lower().split())
        query_words = set(query.lower().split())
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
        
        content_words -= stop_words
        query_words -= stop_words
        
        if not content_words or not query_words:
            return 0.0
        
        intersection = content_words.intersection(query_words)
        union = content_words.union(query_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _select_relevant_chunks(self, 
                              chunks: List[ConversationChunk], 
                              current_query: str) -> List[ConversationChunk]:
        """Select the most relevant conversation chunks."""
        if not chunks:
            return []
        
        # Sort by score descending
        sorted_chunks = sorted(chunks, key=lambda x: x.score, reverse=True)
        
        # Take top chunks up to the limit
        selected = sorted_chunks[:self.max_conversation_chunks]
        
        # Ensure we have a good mix of user and assistant messages
        selected = self._ensure_conversation_balance(selected, chunks)
        
        # Sort selected chunks chronologically for better context flow
        selected.sort(key=lambda x: x.timestamp)
        
        return selected
    
    def _ensure_conversation_balance(self, 
                                   selected: List[ConversationChunk], 
                                   all_chunks: List[ConversationChunk]) -> List[ConversationChunk]:
        """Ensure selected chunks have a good balance of user and assistant messages."""
        if len(selected) < 2:
            return selected
        
        user_count = sum(1 for chunk in selected if chunk.role == 'user')
        assistant_count = len(selected) - user_count
        
        # If heavily skewed towards one role, try to balance
        if user_count == 0 and assistant_count > 1:
            # Find a good user message to include
            user_chunks = [c for c in all_chunks if c.role == 'user']
            if user_chunks:
                best_user = max(user_chunks, key=lambda x: x.score)
                if best_user.score > 0.3:  # Only if reasonably relevant
                    selected[-1] = best_user  # Replace lowest scoring chunk
        
        elif assistant_count == 0 and user_count > 1:
            # Find a good assistant response to include
            assistant_chunks = [c for c in all_chunks if c.role == 'assistant']
            if assistant_chunks:
                best_assistant = max(assistant_chunks, key=lambda x: x.score)
                if best_assistant.score > 0.3:
                    selected[-1] = best_assistant
        
        return selected
    
    def format_conversation_chunks(self, chunks: List[ConversationChunk]) -> str:
        """Format conversation chunks for LLM consumption."""
        if not chunks:
            return "No conversation context available."
        
        formatted_chunks = []
        
        for chunk in chunks:
            # Format timestamp
            time_str = chunk.timestamp.strftime('%H:%M')
            
            # Create role indicator
            role_indicator = "🤖" if chunk.role == 'assistant' else "👤"
            
            # Format chunk with metadata
            chunk_header = f"[{time_str} {role_indicator} {chunk.role.title()}"
            if chunk.topic:
                chunk_header += f" | Topic: {chunk.topic}"
            if chunk.intent:
                chunk_header += f" | Intent: {chunk.intent}"
            chunk_header += f" | Score: {chunk.score:.2f}]"
            
            formatted_chunk = f"{chunk_header}\n{chunk.content}\n"
            formatted_chunks.append(formatted_chunk)
        
        return "\n".join(formatted_chunks)
    
    def get_conversation_summary(self, chunks: List[ConversationChunk]) -> Dict[str, Any]:
        """Get summary statistics about the extracted conversation context."""
        if not chunks:
            return {
                "total_chunks": 0,
                "user_messages": 0,
                "assistant_messages": 0,
                "avg_score": 0.0,
                "time_span_hours": 0.0,
                "topics": [],
                "intents": []
            }
        
        user_count = sum(1 for chunk in chunks if chunk.role == 'user')
        assistant_count = len(chunks) - user_count
        avg_score = sum(chunk.score for chunk in chunks) / len(chunks)
        
        # Calculate time span
        timestamps = [chunk.timestamp for chunk in chunks]
        time_span = max(timestamps) - min(timestamps)
        time_span_hours = time_span.total_seconds() / 3600
        
        # Collect topics and intents
        topics = list(set(chunk.topic for chunk in chunks if chunk.topic))
        intents = list(set(chunk.intent for chunk in chunks if chunk.intent))
        
        return {
            "total_chunks": len(chunks),
            "user_messages": user_count,
            "assistant_messages": assistant_count,
            "avg_score": avg_score,
            "time_span_hours": time_span_hours,
            "topics": topics,
            "intents": intents
        }
    
    def detect_conversation_patterns(self, chunks: List[ConversationChunk]) -> Dict[str, Any]:
        """Detect patterns in the conversation for better context understanding."""
        if not chunks:
            return {}
        
        patterns = {
            "question_answer_pairs": 0,
            "follow_up_questions": 0,
            "topic_changes": 0,
            "error_recovery": 0,
            "dominant_topic": None,
            "conversation_flow": []
        }
        
        # Analyze conversation flow
        prev_chunk = None
        current_topic = None
        
        for chunk in chunks:
            flow_item = {
                "role": chunk.role,
                "intent": chunk.intent,
                "topic": chunk.topic,
                "timestamp": chunk.timestamp.isoformat()
            }
            patterns["conversation_flow"].append(flow_item)
            
            if prev_chunk:
                # Detect question-answer pairs
                if (prev_chunk.role == 'user' and prev_chunk.intent == 'question' and
                    chunk.role == 'assistant' and chunk.intent == 'provide_info'):
                    patterns["question_answer_pairs"] += 1
                
                # Detect follow-up questions
                if (prev_chunk.role == 'assistant' and 
                    chunk.role == 'user' and chunk.intent == 'question'):
                    patterns["follow_up_questions"] += 1
                
                # Detect topic changes
                if (prev_chunk.topic and chunk.topic and 
                    prev_chunk.topic != chunk.topic):
                    patterns["topic_changes"] += 1
                
                # Detect error recovery
                if (prev_chunk.intent == 'error_response' and 
                    chunk.role == 'user'):
                    patterns["error_recovery"] += 1
            
            prev_chunk = chunk
        
        # Find dominant topic
        topic_counts = {}
        for chunk in chunks:
            if chunk.topic:
                topic_counts[chunk.topic] = topic_counts.get(chunk.topic, 0) + 1
        
        if topic_counts:
            patterns["dominant_topic"] = max(topic_counts, key=topic_counts.get)
        
        return patterns