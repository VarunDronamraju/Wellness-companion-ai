
# ==== FILE 3: services/aiml-orchestration/src/llm/prompt_templates.py ====

"""
Engineered prompt templates for various scenarios.
"""

# System prompts for different contexts
RAG_SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on provided context. 
You are knowledgeable, accurate, and always cite your sources when referencing specific information."""

FALLBACK_SYSTEM_PROMPT = """You are a helpful AI assistant. When you don't have specific context, 
you provide useful general information while being clear about any limitations in your knowledge."""

STREAMING_SYSTEM_PROMPT = """You are a helpful AI assistant providing detailed streaming responses. 
Structure your answers clearly and provide comprehensive information."""

# RAG-specific templates
RAG_TEMPLATE = """Based on the following context, please answer the question accurately.

Context:
{context}

Question: {query}

Please provide a comprehensive answer using the information from the context. If the context doesn't contain sufficient information to fully answer the question, please state this clearly.

Answer:"""

# Fallback templates
FALLBACK_TEMPLATE = """Please answer the following question using your general knowledge:

Question: {query}

Provide a helpful and accurate response. If you're uncertain about specific details, please acknowledge this.

Answer:"""

# Specialized templates
SUMMARIZATION_TEMPLATE = """Please provide a concise summary of the following content:

Content:
{content}

Summary:"""

COMPARISON_TEMPLATE = """Based on the provided information, please compare and contrast the following:

Information:
{context}

Question: {query}

Provide a balanced comparison highlighting key similarities and differences.

Comparison:"""

ANALYSIS_TEMPLATE = """Please analyze the following information and answer the question:

Information:
{context}

Question: {query}

Provide a thorough analysis considering multiple perspectives where relevant.

Analysis:"""

# Confidence indicators for responses
HIGH_CONFIDENCE_PHRASES = [
    "Based on the provided information",
    "According to the context",
    "The document clearly states",
    "As mentioned in the source"
]

LOW_CONFIDENCE_PHRASES = [
    "Based on general knowledge",
    "Generally speaking",
    "It's commonly understood that",
    "In most cases"
]

UNCERTAINTY_PHRASES = [
    "I don't have enough information",
    "The context doesn't provide details about",
    "This information isn't available in the provided sources",
    "I cannot find specific information about"
]

