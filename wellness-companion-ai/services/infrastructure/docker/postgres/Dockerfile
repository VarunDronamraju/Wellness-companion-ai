# services/infrastructure/docker/postgres/Dockerfile
FROM postgres:15-alpine

# Install additional extensions
RUN apk add --no-cache \
    postgresql-contrib \
    curl

# Copy initialization scripts
COPY init-scripts/ /docker-entrypoint-initdb.d/

# Copy custom configuration
COPY postgresql.conf /etc/postgresql/postgresql.conf

# Set permissions
RUN chmod +x /docker-entrypoint-initdb.d/*.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD pg_isready -U $POSTGRES_USER -d $POSTGRES_DB || exit 1

EXPOSE 5432