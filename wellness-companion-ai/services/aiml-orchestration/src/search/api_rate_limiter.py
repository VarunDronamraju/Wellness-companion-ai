
# ==== FILE 4: services/aiml-orchestration/src/search/api_rate_limiter.py ====

"""
API rate limiting for external search services.
Implements sliding window rate limiting.
"""

import asyncio
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    calls_per_minute: int
    calls_per_hour: int
    burst_allowance: int = 5  # Allow small bursts

class APIRateLimiter:
    """
    Sliding window rate limiter for API calls.
    """
    
    def __init__(self, calls_per_minute: int = 50, calls_per_hour: int = 1000):
        self.calls_per_minute = calls_per_minute
        self.calls_per_hour = calls_per_hour
        
        # Track API calls with timestamps
        self.call_history: List[float] = []
        self.minute_calls: List[float] = []
        self.hour_calls: List[float] = []
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'allowed_requests': 0,
            'denied_requests': 0,
            'current_minute_calls': 0,
            'current_hour_calls': 0
        }
        
        # Lock for thread safety
        self._lock = asyncio.Lock()

    async def can_make_request(self) -> bool:
        """
        Check if a request can be made within rate limits.
        
        Returns:
            True if request is allowed, False if rate limited
        """
        async with self._lock:
            current_time = time.time()
            
            # Clean old entries
            self._cleanup_old_entries(current_time)
            
            # Check minute limit
            minute_calls = len(self.minute_calls)
            if minute_calls >= self.calls_per_minute:
                self.stats['denied_requests'] += 1
                logger.warning(f"Rate limit exceeded: {minute_calls}/{self.calls_per_minute} calls per minute")
                return False
            
            # Check hour limit
            hour_calls = len(self.hour_calls)
            if hour_calls >= self.calls_per_hour:
                self.stats['denied_requests'] += 1
                logger.warning(f"Rate limit exceeded: {hour_calls}/{self.calls_per_hour} calls per hour")
                return False
            
            # Request is allowed - record it
            self.minute_calls.append(current_time)
            self.hour_calls.append(current_time)
            self.call_history.append(current_time)
            
            self.stats['total_requests'] += 1
            self.stats['allowed_requests'] += 1
            self.stats['current_minute_calls'] = len(self.minute_calls)
            self.stats['current_hour_calls'] = len(self.hour_calls)
            
            return True

    async def wait_if_needed(self) -> float:
        """
        Wait if necessary to comply with rate limits.
        
        Returns:
            Time waited in seconds
        """
        if await self.can_make_request():
            return 0.0
        
        # Calculate wait time
        wait_time = self._calculate_wait_time()
        
        if wait_time > 0:
            logger.info(f"Rate limited - waiting {wait_time:.2f} seconds")
            await asyncio.sleep(wait_time)
        
        return wait_time

    def _cleanup_old_entries(self, current_time: float):
        """Remove entries outside the time windows."""
        minute_cutoff = current_time - 60  # 1 minute ago
        hour_cutoff = current_time - 3600   # 1 hour ago
        
        # Clean minute calls
        self.minute_calls = [
            call_time for call_time in self.minute_calls
            if call_time > minute_cutoff
        ]
        
        # Clean hour calls
        self.hour_calls = [
            call_time for call_time in self.hour_calls
            if call_time > hour_cutoff
        ]
        
        # Clean general call history (keep last 24 hours)
        day_cutoff = current_time - 86400  # 24 hours ago
        self.call_history = [
            call_time for call_time in self.call_history
            if call_time > day_cutoff
        ]

    def _calculate_wait_time(self) -> float:
        """Calculate how long to wait before next request is allowed."""
        current_time = time.time()
        
        # Check minute limit
        if len(self.minute_calls) >= self.calls_per_minute:
            oldest_in_minute = min(self.minute_calls)
            wait_for_minute = (oldest_in_minute + 60) - current_time
        else:
            wait_for_minute = 0
        
        # Check hour limit  
        if len(self.hour_calls) >= self.calls_per_hour:
            oldest_in_hour = min(self.hour_calls)
            wait_for_hour = (oldest_in_hour + 3600) - current_time
        else:
            wait_for_hour = 0
        
        # Return the maximum wait time needed
        return max(0, wait_for_minute, wait_for_hour)

    def get_status(self) -> Dict[str, any]:
        """Get current rate limit status."""
        current_time = time.time()
        self._cleanup_old_entries(current_time)
        
        return {
            'calls_per_minute_limit': self.calls_per_minute,
            'calls_per_hour_limit': self.calls_per_hour,
            'current_minute_calls': len(self.minute_calls),
            'current_hour_calls': len(self.hour_calls),
            'minute_limit_remaining': self.calls_per_minute - len(self.minute_calls),
            'hour_limit_remaining': self.calls_per_hour - len(self.hour_calls),
            'next_minute_reset': self._get_next_reset_time(60),
            'next_hour_reset': self._get_next_reset_time(3600),
            'is_rate_limited': not (
                len(self.minute_calls) < self.calls_per_minute and 
                len(self.hour_calls) < self.calls_per_hour
            ),
            'stats': self.stats.copy()
        }

    def _get_next_reset_time(self, window_seconds: int) -> Optional[str]:
        """Get next reset time for a time window."""
        if window_seconds == 60:
            calls = self.minute_calls
        elif window_seconds == 3600:
            calls = self.hour_calls
        else:
            return None
        
        if not calls:
            return None
        
        oldest_call = min(calls)
        reset_time = oldest_call + window_seconds
        reset_datetime = datetime.fromtimestamp(reset_time)
        
        return reset_datetime.isoformat()

    def reset_stats(self):
        """Reset rate limiter statistics."""
        self.stats = {
            'total_requests': 0,
            'allowed_requests': 0,
            'denied_requests': 0,
            'current_minute_calls': len(self.minute_calls),
            'current_hour_calls': len(self.hour_calls)
        }

    def get_statistics(self) -> Dict[str, any]:
        """Get comprehensive rate limiter statistics."""
        current_time = time.time()
        self._cleanup_old_entries(current_time)
        
        total_requests = self.stats['total_requests']
        success_rate = (self.stats['allowed_requests'] / max(1, total_requests)) * 100
        
        return {
            **self.stats,
            'success_rate': f"{success_rate:.2f}%",
            'current_status': self.get_status(),
            'average_calls_per_minute': len(self.call_history) / max(1, len(self.call_history) / 60) if self.call_history else 0,
            'call_history_length': len(self.call_history)
        }
