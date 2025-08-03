# services/infrastructure/docker/redis/Dockerfile
FROM redis:7-alpine

# Install additional tools
RUN apk add --no-cache \
    curl \
    ca-certificates

# Copy custom Redis configuration
COPY redis.conf /usr/local/etc/redis/redis.conf

# Copy health check script
COPY healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

# Create data directory with proper permissions
RUN mkdir -p /data && chown redis:redis /data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

# Expose Redis port
EXPOSE 6379

# Use custom configuration
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]