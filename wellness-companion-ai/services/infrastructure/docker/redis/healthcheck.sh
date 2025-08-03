#!/bin/bash
# services/infrastructure/docker/redis/healthcheck.sh
# Redis Health Check Script for Wellness Companion AI

set -e

# Test basic Redis connectivity
if [ -n "$REDIS_PASSWORD" ]; then
    # With password
    redis-cli -a "$REDIS_PASSWORD" ping > /dev/null 2>&1
else
    # Without password
    redis-cli ping > /dev/null 2>&1
fi

# Test basic operations
if [ -n "$REDIS_PASSWORD" ]; then
    # Test SET/GET operations with auth
    redis-cli -a "$REDIS_PASSWORD" set health_check_key "$(date)" > /dev/null 2>&1
    redis-cli -a "$REDIS_PASSWORD" get health_check_key > /dev/null 2>&1
    redis-cli -a "$REDIS_PASSWORD" del health_check_key > /dev/null 2>&1
else
    # Test SET/GET operations without auth
    redis-cli set health_check_key "$(date)" > /dev/null 2>&1
    redis-cli get health_check_key > /dev/null 2>&1
    redis-cli del health_check_key > /dev/null 2>&1
fi

echo "Redis health check passed"
exit 0