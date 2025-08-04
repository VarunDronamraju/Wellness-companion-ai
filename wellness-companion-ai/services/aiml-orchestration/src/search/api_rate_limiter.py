# services/aiml-orchestration/src/search/api_rate_limiter.py

import asyncio
import time
from typing import Dict, Optional
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

class APIRateLimiter:
    """Rate limiter for API calls with sliding window approach"""
    
    def __init__(self, calls_per_minute: int = 60, calls_per_hour: int = 1000):
        self.calls_per_minute = calls_per_minute
        self.calls_per_hour = calls_per_hour
        
        # Track calls with timestamps
        self.minute_calls: deque = deque()
        self.hour_calls: deque = deque()
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
    
    async def can_make_call(self) -> bool:
        """Check if we can make a call without exceeding limits"""
        async with self._lock:
            current_time = time.time()
            
            # Clean old calls (older than 1 minute)
            self._clean_old_calls(self.minute_calls, current_time, 60)
            
            # Clean old calls (older than 1 hour)
            self._clean_old_calls(self.hour_calls, current_time, 3600)
            
            # Check limits
            if len(self.minute_calls) >= self.calls_per_minute:
                logger.warning(f"Rate limit exceeded: {len(self.minute_calls)} calls in last minute")
                return False
            
            if len(self.hour_calls) >= self.calls_per_hour:
                logger.warning(f"Rate limit exceeded: {len(self.hour_calls)} calls in last hour")
                return False
            
            return True
    
    async def record_call(self):
        """Record a successful API call"""
        async with self._lock:
            current_time = time.time()
            self.minute_calls.append(current_time)
            self.hour_calls.append(current_time)
            
            logger.debug(f"API call recorded. Minute: {len(self.minute_calls)}, Hour: {len(self.hour_calls)}")
    
    def _clean_old_calls(self, calls_deque: deque, current_time: float, window_seconds: int):
        """Remove calls older than the specified window"""
        cutoff_time = current_time - window_seconds
        
        while calls_deque and calls_deque[0] < cutoff_time:
            calls_deque.popleft()
    
    async def wait_if_needed(self) -> Optional[float]:
        """Wait if rate limit is exceeded, return wait time"""
        if await self.can_make_call():
            return None
        
        # Calculate wait time based on oldest call in minute window
        async with self._lock:
            if self.minute_calls:
                oldest_call = self.minute_calls[0]
                wait_time = 60 - (time.time() - oldest_call)
                if wait_time > 0:
                    logger.info(f"Rate limit hit, waiting {wait_time:.2f} seconds")
                    await asyncio.sleep(wait_time)
                    return wait_time
        
        return None
    
    def get_current_usage(self) -> Dict[str, int]:
        """Get current API usage statistics"""
        current_time = time.time()
        
        # Clean old calls before reporting
        self._clean_old_calls(self.minute_calls, current_time, 60)
        self._clean_old_calls(self.hour_calls, current_time, 3600)
        
        return {
            "calls_last_minute": len(self.minute_calls),
            "calls_last_hour": len(self.hour_calls),
            "minute_limit": self.calls_per_minute,
            "hour_limit": self.calls_per_hour
        }

# Global rate limiter instance
rate_limiter = APIRateLimiter()