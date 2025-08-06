
# ========================================
# services/core-backend/docs/tags_metadata.py
# ========================================

"""
API Tags Metadata - OpenAPI tags and descriptions for endpoint grouping
Organizes API endpoints into logical groups with rich descriptions
"""

from typing import List, Dict, Any


def get_tags_metadata() -> List[Dict[str, Any]]:
    """Get OpenAPI tags metadata for endpoint organization"""
    
    return [
        {
            "name": "system",
            "description": """
## System & Health Monitoring

System-level endpoints for monitoring service health, checking dependencies, 
and retrieving system status information. These endpoints are essential for 
DevOps, monitoring, and troubleshooting.

### Key Features:
- Real-time health checks
- Dependency status monitoring  
- System metrics and performance data
- Service capability discovery
            """,
            "externalDocs": {
                "description": "System monitoring guide",
                "url": "https://docs.wellness-companion.ai/monitoring"
            }
        },
        {
            "name": "documents", 
            "description": """
## Document Management

Complete document lifecycle management including upload, processing, metadata extraction,
and CRUD operations. Supports multiple file formats with automatic content analysis.

### Supported Formats:
- **PDF**: Portable Document Format files
- **DOCX**: Microsoft Word documents  
- **TXT**: Plain text files
- **MD**: Markdown documents
- **HTML**: HyperText Markup Language
- **RTF**: Rich Text Format

### Features:
- Automatic text extraction and processing
- Metadata extraction and indexing
- Document versioning and history
- User-based access control
- Bulk operations support
            """,
            "externalDocs": {
                "description": "Document management guide", 
                "url": "https://docs.wellness-companion.ai/documents"
            }
        },
        {
            "name": "search",
            "description": """
## Advanced Search & Retrieval

Sophisticated search capabilities combining semantic vector search, web search integration,
and hybrid approaches for comprehensive information retrieval.

### Search Types:

#### 🔍 Semantic Search
- Vector-based similarity search using advanced embeddings
- Sub-second response times
- Configurable relevance thresholds
- User document scope filtering

#### 🌐 Web Search  
- External web search integration via Tavily API
- Real-time web content retrieval
- Domain filtering and result ranking
- Rate-limited and cached results

#### 🎯 Hybrid Search
- Intelligent combination of local and web results
- Confidence-based fallback mechanisms
- Result deduplication and ranking
- Enhanced context and coverage

### Performance:
- Average response time: <200ms for semantic search
- Average response time: <500ms for web search
- Concurrent request handling with async processing
            """,
            "externalDocs": {
                "description": "Search implementation guide",
                "url": "https://docs.wellness-companion.ai/search"
            }
        },
        {
            "name": "authentication",
            "description": """
## Authentication & Authorization

Secure authentication system supporting multiple OAuth providers and JWT-based
session management with role-based access control.

### Supported Providers:
- **Google OAuth 2.0**: Social authentication via Google
- **AWS Cognito**: Enterprise identity management
- **Local Authentication**: Email/password with secure hashing

### Security Features:
- JWT tokens with configurable expiration
- Refresh token rotation
- Rate limiting on authentication endpoints
- Secure password policies
- Session management and logout

### Access Control:
- Role-based permissions (Admin, User, Moderator, ReadOnly)
- Resource-level access control
- User document isolation
- API endpoint protection
            """,
            "externalDocs": {
                "description": "Authentication guide",
                "url": "https://docs.wellness-companion.ai/auth"
            }
        },
        {
            "name": "admin",
            "description": """
## Administration & Management

Administrative endpoints for system configuration, user management, 
maintenance operations, and advanced system control.

### Capabilities:
- User account management
- System configuration updates
- Maintenance mode control
- Bulk operations and data management
- Service orchestration and control

### Security:
- Admin-only access restrictions
- Audit logging for all operations
- Safe configuration validation
- Rollback capabilities for critical changes

**⚠️ Warning**: These endpoints require administrative privileges and can affect
system-wide operations. Use with caution in production environments.
            """,
            "externalDocs": {
                "description": "Administration guide",
                "url": "https://docs.wellness-companion.ai/admin"
            }
        },
        {
            "name": "analytics",
            "description": """
## Analytics & Metrics

Comprehensive analytics endpoints providing insights into system usage,
performance metrics, and user behavior analysis.

### Available Metrics:
- API usage statistics and trends
- Search analytics and popular queries
- Document management metrics
- User engagement and activity patterns
- Performance and response time analysis

### Data Export:
- CSV, JSON, and XML export formats
- Configurable time ranges and filters
- Scheduled report generation
- Real-time dashboard data feeds
            """,
            "externalDocs": {
                "description": "Analytics guide", 
                "url": "https://docs.wellness-companion.ai/analytics"
            }
        }
    ]

