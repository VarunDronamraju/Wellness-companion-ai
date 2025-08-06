
# ========================================
# services/core-backend/docs/api_description.py
# ========================================

"""
API Description - Main OpenAPI description and metadata
Provides comprehensive API overview and documentation
"""

from typing import Dict, Any


def get_api_description() -> str:
    """Get the main API description for OpenAPI documentation"""
    
    return """
# Wellness Companion AI - Core Backend API

## Overview

The **Wellness Companion AI Core Backend** is a sophisticated API service that provides document management, 
semantic search, web search integration, and AI-powered content analysis capabilities. This service acts as 
the central hub for all client applications and orchestrates communication between various microservices.

## Key Features

### 🗄️ Document Management
- **Upload & Processing**: Support for PDF, DOCX, TXT, MD, HTML, and RTF files
- **Metadata Extraction**: Automatic extraction of document metadata and content analysis
- **Version Control**: Document versioning and history tracking
- **Security**: User-based access control and document isolation

### 🔍 Advanced Search Capabilities
- **Semantic Search**: Vector-based similarity search using state-of-the-art embeddings
- **Web Search Integration**: Fallback to web search when local results have low confidence
- **Hybrid Search**: Intelligent combination of local and web search results
- **Real-time Results**: Fast, sub-second search responses

### 🤖 AI/ML Integration
- **Local LLM Processing**: Privacy-first AI processing using local language models
- **Embedding Generation**: High-quality document embeddings for semantic search
- **Content Analysis**: Automatic categorization, keyword extraction, and sentiment analysis

### 🔒 Security & Authentication
- **JWT Authentication**: Secure token-based authentication
- **OAuth Integration**: Support for Google OAuth and AWS Cognito
- **Rate Limiting**: Protection against abuse with configurable rate limits
- **Input Validation**: Comprehensive request validation and sanitization

### 📊 Monitoring & Analytics
- **Health Monitoring**: Real-time service health checks and dependency monitoring
- **Request Tracking**: Unique request IDs for debugging and analytics
- **Error Handling**: Comprehensive error handling with structured responses
- **Performance Metrics**: Detailed performance monitoring and logging

## Architecture

This API follows a microservices architecture with clear separation of concerns:

- **Core Backend**: Main API gateway and orchestration (this service)
- **AI/ML Orchestration**: Document processing and AI model inference
- **Data Layer**: Database operations and file storage management
- **Infrastructure**: Containerized deployment with Docker and AWS

## Getting Started

1. **Authentication**: Obtain an access token using the `/api/auth/login` endpoint
2. **Document Upload**: Upload documents using the `/api/documents/upload` endpoint
3. **Search**: Perform searches using `/api/search/semantic`, `/api/search/web`, or `/api/search/hybrid`
4. **Document Management**: List, view, and manage documents using the document endpoints

## Rate Limits

- **Authentication**: 10 requests/minute per IP
- **Document Upload**: 5 requests/minute per user
- **Search**: 60 requests/minute per user
- **General API**: 100 requests/minute per user

## Error Handling

All API responses follow a consistent error format with:
- HTTP status codes following REST conventions
- Structured error messages with error codes
- Request IDs for tracking and debugging
- Detailed validation errors for bad requests

## Support

For technical support and API questions, please refer to the documentation or contact the development team.
"""


def get_openapi_metadata() -> Dict[str, Any]:
    """Get OpenAPI metadata configuration"""
    
    return {
        "title": "Wellness Companion AI - Core Backend API",
        "description": get_api_description(),
        "version": "1.0.0",
        "contact": {
            "name": "Wellness Companion AI Team",
            "email": "api-support@wellness-companion.ai",
            "url": "https://wellness-companion.ai/support"
        },
        "license": {
            "name": "Proprietary",
            "url": "https://wellness-companion.ai/license"
        },
        "servers": [
            {
                "url": "http://localhost:8001",
                "description": "Development server"
            },
            {
                "url": "https://api-dev.wellness-companion.ai",
                "description": "Development environment"
            },
            {
                "url": "https://api-staging.wellness-companion.ai", 
                "description": "Staging environment"
            },
            {
                "url": "https://api.wellness-companion.ai",
                "description": "Production environment"
            }
        ],
        "externalDocs": {
            "description": "Find more info here",
            "url": "https://docs.wellness-companion.ai"
        }
    }
