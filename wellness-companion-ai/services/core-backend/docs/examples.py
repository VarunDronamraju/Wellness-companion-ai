
# ========================================
# services/core-backend/docs/examples.py
# ========================================

"""
API Examples - Request and response examples for documentation
Provides realistic examples for all API endpoints to improve developer experience
"""

from typing import Dict, Any


def get_request_examples() -> Dict[str, Dict[str, Any]]:
    """Get request examples for API documentation"""
    
    return {
        "document_upload": {
            "summary": "Upload a PDF document",
            "description": "Upload a PDF document with metadata",
            "value": {
                "title": "Machine Learning Research Paper",
                "description": "Comprehensive research on transformer architectures",
                "tags": ["machine-learning", "research", "transformers"],
                "category": "research",
                "is_public": False,
                "metadata": {
                    "author": "Dr. Jane Smith",
                    "institution": "AI Research Institute",
                    "publish_date": "2024-01-15"
                }
            }
        },
        "semantic_search": {
            "summary": "Semantic search query", 
            "description": "Search for documents about artificial intelligence",
            "value": {
                "query": "artificial intelligence machine learning algorithms",
                "max_results": 10,
                "threshold": 0.75,
                "user_id": "user_12345",
                "include_metadata": True,
                "boost_recent": True,
                "boost_tags": ["ai", "research"]
            }
        },
        "web_search": {
            "summary": "Web search query",
            "description": "Search the web for latest AI news",
            "value": {
                "query": "latest artificial intelligence breakthroughs 2024",
                "max_results": 5,
                "search_depth": "basic",
                "user_id": "user_12345",
                "language": "en",
                "region": "US"
            }
        },
        "hybrid_search": {
            "summary": "Hybrid search query",
            "description": "Combined local and web search for comprehensive results",
            "value": {
                "query": "transformer neural networks applications",
                "max_results": 15,
                "confidence_threshold": 0.7,
                "semantic_weight": 0.8,
                "web_fallback": True,
                "web_max_results": 5,
                "mix_results": True,
                "user_id": "user_12345"
            }
        },
        "document_list": {
            "summary": "List documents with filters",
            "description": "Get paginated list of user documents with filtering",
            "value": {
                "user_id": "user_12345",
                "file_type": "pdf",
                "search": "machine learning",
                "limit": 20,
                "offset": 0,
                "sort_by": "created_at",
                "sort_order": "desc",
                "tags": ["research", "ai"],
                "date_range": {
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2024-12-31T23:59:59Z"
                }
            }
        },
        "login_request": {
            "summary": "OAuth login initiation",
            "description": "Initiate Google OAuth login flow",
            "value": {
                "provider": "google",
                "redirect_uri": "http://localhost:3000/auth/callback",
                "user_id": "temp_user_12345",
                "remember_me": True
            }
        }
    }


def get_response_examples() -> Dict[str, Dict[str, Any]]:
    """Get response examples for API documentation"""
    
    return {
        "document_upload_success": {
            "summary": "Successful document upload",
            "description": "Document uploaded and processing initiated",
            "value": {
                "success": True,
                "document_id": "doc_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "filename": "research_paper.pdf",
                "title": "Machine Learning Research Paper", 
                "size": 2048576,
                "file_type": "pdf",
                "status": "uploaded",
                "processing_id": "proc_x1y2z3a4-b5c6-7890-def1-234567890abc",
                "timestamp": "2024-08-06T10:30:00Z"
            }
        },
        "semantic_search_success": {
            "summary": "Successful semantic search",
            "description": "Local document search with high-relevance results",
            "value": {
                "success": True,
                "query": "artificial intelligence machine learning algorithms",
                "results": [
                    {
                        "title": "Introduction to Machine Learning Algorithms",
                        "snippet": "This comprehensive guide covers the fundamentals of machine learning algorithms including supervised, unsupervised, and reinforcement learning approaches...",
                        "score": 0.94,
                        "source_type": "document",
                        "document_id": "doc_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "filename": "ml_algorithms_guide.pdf",
                        "file_type": "pdf",
                        "metadata": {
                            "author": "Dr. Jane Smith",
                            "category": "research",
                            "tags": ["machine-learning", "algorithms", "ai"]
                        }
                    },
                    {
                        "title": "Deep Learning and Neural Networks",
                        "snippet": "Exploring the depths of artificial neural networks and their applications in modern AI systems...",
                        "score": 0.89,
                        "source_type": "document", 
                        "document_id": "doc_b2c3d4e5-f6g7-8901-bcde-f23456789012",
                        "filename": "deep_learning_basics.docx",
                        "file_type": "docx"
                    }
                ],
                "total_results": 2,
                "search_time_ms": 145.3,
                "threshold_used": 0.75,
                "search_type": "semantic_only",
                "timestamp": "2024-08-06T10:30:00Z"
            }
        },
        "web_search_success": {
            "summary": "Successful web search",
            "description": "Web search results from external sources",
            "value": {
                "success": True,
                "query": "latest artificial intelligence breakthroughs 2024",
                "results": [
                    {
                        "title": "Major AI Breakthroughs in 2024: A Comprehensive Review",
                        "url": "https://airesearch.com/2024-breakthroughs",
                        "snippet": "2024 has been a landmark year for artificial intelligence with significant breakthroughs in large language models, computer vision, and robotics...",
                        "domain": "airesearch.com",
                        "score": 0.96,
                        "published_date": "2024-08-01T09:00:00Z"
                    },
                    {
                        "title": "OpenAI's Latest Model Achieves Human-Level Performance",
                        "url": "https://techcrunch.com/openai-latest-model",
                        "snippet": "OpenAI has announced their latest language model that demonstrates human-level performance across multiple benchmarks...",
                        "domain": "techcrunch.com", 
                        "score": 0.91,
                        "published_date": "2024-07-28T14:30:00Z"
                    }
                ],
                "total_results": 2,
                "search_time_ms": 487.2,
                "search_depth": "basic",
                "search_type": "web_only",
                "source": "tavily_api",
                "timestamp": "2024-08-06T10:30:00Z"
            }
        },
        "document_list_success": {
            "summary": "Successful document list",
            "description": "Paginated list of user documents with metadata",
            "value": {
                "success": True,
                "documents": [
                    {
                        "document_id": "doc_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "filename": "research_paper.pdf",
                        "file_path": "/app/uploads/user_12345/doc_a1b2c3d4_research_paper.pdf",
                        "title": "Machine Learning Research Paper",
                        "size": 2048576,
                        "created_at": "2024-08-05T15:30:00Z",
                        "modified_at": "2024-08-05T15:30:00Z",
                        "status": "ready",
                        "file_type": "pdf",
                        "tags": ["machine-learning", "research"],
                        "category": "research"
                    }
                ],
                "total": 42,
                "limit": 20,
                "offset": 0,
                "has_more": True,
                "page": 1,
                "total_pages": 3,
                "user_id": "user_12345",
                "filters_applied": {
                    "file_type": "pdf",
                    "status": None,
                    "search": "machine learning",
                    "sort_by": "created_at",
                    "sort_order": "desc"
                },
                "timestamp": "2024-08-06T10:30:00Z"
            }
        },
        "error_validation": {
            "summary": "Validation error response",
            "description": "Request validation failed with field-specific errors",
            "value": {
                "success": False,
                "error": "Validation failed",
                "error_code": "VALIDATION_ERROR",
                "details": {
                    "validation_errors": [
                        {
                            "field": "body -> query",
                            "message": "String should have at least 2 characters",
                            "type": "string_too_short",
                            "input": ""
                        },
                        {
                            "field": "body -> max_results", 
                            "message": "Input should be less than or equal to 20",
                            "type": "less_than_equal",
                            "input": 150
                        }
                    ],
                    "total_errors": 2
                },
                "request_id": "req_12345678-90ab-cdef-1234-567890abcdef",
                "timestamp": "2024-08-06T10:30:00Z"
            }
        },
        "error_not_found": {
            "summary": "Resource not found error",
            "description": "Requested document was not found",
            "value": {
                "success": False,
                "error": "Document 'doc_invalid123' not found",
                "error_code": "DOCUMENT_NOT_FOUND",
                "details": {
                    "document_id": "doc_invalid123"
                },
                "request_id": "req_87654321-09ba-fedc-8765-432109876543",
                "timestamp": "2024-08-06T10:30:00Z"
            }
        },
        "health_check_success": {
            "summary": "Healthy service response",
            "description": "All systems operational",
            "value": {
                "success": True,
                "status": "healthy",
                "timestamp": "2024-08-06T10:30:00Z",
                "service": "core-backend",
                "version": "1.0.0",
                "uptime_started": "2024-08-06T09:00:00Z",
                "error_handling": "active",
                "dependencies": {
                    "aiml_service": {
                        "status": "healthy",
                        "response_time_ms": 45
                    },
                    "data_layer": {
                        "status": "healthy", 
                        "response_time_ms": 23
                    },
                    "postgres": {
                        "status": "healthy",
                        "response_time_ms": 12
                    },
                    "redis": {
                        "status": "healthy",
                        "response_time_ms": 8
                    }
                }
            }
        }
    }