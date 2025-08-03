# services/infrastructure/docker/postgres/init-scripts/01-init-database.sh
#!/bin/bash
set -e

echo "🚀 Initializing Wellness Companion AI Database..."

# Create additional databases for different services
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create vector extension for PostgreSQL
    CREATE EXTENSION IF NOT EXISTS vector;
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS pg_trgm;
    
    -- Create schemas for different services
    CREATE SCHEMA IF NOT EXISTS core_backend;
    CREATE SCHEMA IF NOT EXISTS data_layer;
    CREATE SCHEMA IF NOT EXISTS user_management;
    CREATE SCHEMA IF NOT EXISTS document_management;
    
    -- Grant permissions
    GRANT ALL PRIVILEGES ON SCHEMA core_backend TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON SCHEMA data_layer TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON SCHEMA user_management TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON SCHEMA document_management TO $POSTGRES_USER;
    
    -- Create initial tables
    
    -- Users table
    CREATE TABLE IF NOT EXISTS user_management.users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        email VARCHAR(255) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        provider VARCHAR(50) NOT NULL, -- 'google', 'cognito'
        provider_id VARCHAR(255) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        is_active BOOLEAN DEFAULT TRUE,
        preferences JSONB DEFAULT '{}'
    );
    
    -- Documents table
    CREATE TABLE IF NOT EXISTS document_management.documents (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID REFERENCES user_management.users(id) ON DELETE CASCADE,
        filename VARCHAR(255) NOT NULL,
        original_filename VARCHAR(255) NOT NULL,
        file_type VARCHAR(50) NOT NULL,
        file_size BIGINT NOT NULL,
        s3_key VARCHAR(500),
        processing_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
        chunk_count INTEGER DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        metadata JSONB DEFAULT '{}'
    );
    
    -- Document chunks table (for vector storage reference)
    CREATE TABLE IF NOT EXISTS document_management.document_chunks (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        document_id UUID REFERENCES document_management.documents(id) ON DELETE CASCADE,
        chunk_index INTEGER NOT NULL,
        chunk_text TEXT NOT NULL,
        chunk_tokens INTEGER,
        qdrant_point_id UUID,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Chat conversations table
    CREATE TABLE IF NOT EXISTS core_backend.conversations (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID REFERENCES user_management.users(id) ON DELETE CASCADE,
        title VARCHAR(255),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        is_archived BOOLEAN DEFAULT FALSE
    );
    
    -- Chat messages table
    CREATE TABLE IF NOT EXISTS core_backend.messages (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        conversation_id UUID REFERENCES core_backend.conversations(id) ON DELETE CASCADE,
        role VARCHAR(20) NOT NULL, -- 'user', 'assistant'
        content TEXT NOT NULL,
        sources JSONB DEFAULT '[]',
        confidence_score DECIMAL(3,2),
        processing_time_ms INTEGER,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Create indexes for performance
    CREATE INDEX IF NOT EXISTS idx_users_email ON user_management.users(email);
    CREATE INDEX IF NOT EXISTS idx_users_provider ON user_management.users(provider, provider_id);
    CREATE INDEX IF NOT EXISTS idx_documents_user_id ON document_management.documents(user_id);
    CREATE INDEX IF NOT EXISTS idx_documents_status ON document_management.documents(processing_status);
    CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON document_management.document_chunks(document_id);
    CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON core_backend.conversations(user_id);
    CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON core_backend.messages(conversation_id);
    CREATE INDEX IF NOT EXISTS idx_messages_created_at ON core_backend.messages(created_at);
    
    -- Full text search indexes
    CREATE INDEX IF NOT EXISTS idx_documents_filename_search 
        ON document_management.documents USING gin(to_tsvector('english', filename));
    CREATE INDEX IF NOT EXISTS idx_chunks_text_search 
        ON document_management.document_chunks USING gin(to_tsvector('english', chunk_text));
EOSQL

echo "✅ Database initialization completed successfully!"
echo "📊 Created schemas: core_backend, data_layer, user_management, document_management"
echo "📋 Created tables: users, documents, document_chunks, conversations, messages"
echo "🔍 Created performance indexes and full-text search support"