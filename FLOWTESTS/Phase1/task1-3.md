# Wellness Companion AI

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 8GB+ RAM available
- Git

### Setup Instructions

1. **Clone and Setup**
```bash
git clone <repository-url>
cd wellness-companion-ai
cp .env.example .env
# Edit .env with your configuration
```

2. **Start All Services**
```bash
# Basic services
docker-compose up -d

# With monitoring
docker-compose --profile monitoring up -d

# Development mode (includes desktop app)
docker-compose --profile development up -d
```

3. **Verify Health**
```bash
# Check all services are running
docker-compose ps

# Test health endpoints
curl http://localhost:8000/health  # Core Backend
curl http://localhost:8001/health  # AI/ML Service
curl http://localhost:8002/health  # Data Layer
curl http://localhost:6333/health  # Qdrant
```

## 📋 Development Status

### ✅ Completed Tasks
- [x] **Task 1**: Complete 6-layer project structure
- [x] **Task 2**: Docker Compose configuration with all services
- [x] **Task 3**: Environment configuration and .gitignore

### 🔄 Next Steps
- [ ] **Task 4**: PostgreSQL Docker service setup
- [ ] **Task 5**: Redis Docker service setup
- [ ] **Task 6**: Qdrant Docker service integration

## 🏗️ Architecture

### 6-Layer Structure
1. **Desktop Layer** - PyQt6 application (`services/desktop-app/`)
2. **Core Backend** - FastAPI services (`services/core-backend/`)
3. **AI/ML Orchestration** - RAG pipeline (`services/aiml-orchestration/`)
4. **Data Layer** - Database operations (`services/data-layer/`)
5. **Infrastructure** - Docker & AWS configs (`services/infrastructure/`)
6. **CI/CD & Logging** - Automation & monitoring (`services/cicd-logging/`)

### Service Communication
```
Desktop App ↔ NGINX ↔ Core Backend ↔ AI/ML Service ↔ Data Layer
                           ↓              ↓              ↓
                        Redis         Ollama      Qdrant/PostgreSQL
```

## 🛠️ Services Overview

| Service | Port | Purpose | Health Check |
|---------|------|---------|--------------|
| NGINX | 80/443 | API Gateway | `curl localhost/health` |
| Core Backend | 8000 | REST APIs | `curl localhost:8000/health` |
| AI/ML Service | 8001 | RAG Pipeline | `curl localhost:8001/health` |
| Data Layer | 8002 | Database Ops | `curl localhost:8002/health` |
| PostgreSQL | 5432 | Metadata DB | Internal |
| Redis | 6379 | Cache/Sessions | Internal |
| Qdrant | 6333 | Vector DB | `curl localhost:6333/health` |
| Ollama | 11434 | Local LLM | `curl localhost:11434/api/version` |

## 📊 Docker Volumes

- `postgres_data` - PostgreSQL database
- `redis_data` - Redis persistence
- `qdrant_data` - Vector database
- `ollama_models` - LLM models
- `nginx_logs` - Access logs

## 🔧 Configuration

### Required Environment Variables
See `.env.example` for complete configuration template.

Key variables to set:
- Database passwords
- API keys (Tavily, Google OAuth)
- JWT secrets
- AWS credentials

### Optional Profiles
- `monitoring` - Prometheus + Grafana
- `development` - Desktop app container

## 📝 Development Notes

### Phase 1 Progress (Tasks 1-15)
- ✅ Foundation structure complete
- ✅ Docker orchestration ready
- ✅ Environment configuration done
- 🔄 Individual service setup in progress

### Next Phase: Core RAG Foundation (Tasks 16-30)
Focus on AI/ML service implementation and RAG pipeline.

---

**Last Updated**: Tasks 1-3 completed
**Next**: Database service setup (Tasks 4-6)