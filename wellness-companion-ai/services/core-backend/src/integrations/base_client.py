"""
Base HTTP Client - Wellness Companion AI
Base client with retry logic, timeout handling, and error management
"""

import httpx
import asyncio
from typing import Dict, Any, Optional, Union
from datetime import datetime
import logging
from contextlib import asynccontextmanager

from .exceptions import handle_httpx_exception, IntegrationException
from .client_config import ServiceEndpoint

logger = logging.getLogger(__name__)


class BaseHTTPClient:
    """Base HTTP client with retry logic and error handling"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.client: Optional[httpx.AsyncClient] = None
        self._session_stats = {
            "requests_made": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "total_retry_attempts": 0,
            "session_started": datetime.utcnow()
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_session()
    
    async def start_session(self):
        """Start HTTP client session"""
        if self.client is None:
            self.client = httpx.AsyncClient(
                headers={
                    "User-Agent": f"WellnessCompanionAI-CoreBackend/1.0",
                    "X-Service-Name": "core-backend",
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                follow_redirects=True,
                verify=True  # SSL verification
            )
            logger.debug(f"Started HTTP session for {self.service_name}")
    
    async def close_session(self):
        """Close HTTP client session"""
        if self.client:
            await self.client.aclose()
            self.client = None
            
            # Log session statistics
            stats = self._session_stats
            success_rate = (
                (stats["requests_successful"] / stats["requests_made"] * 100)
                if stats["requests_made"] > 0 else 0
            )
            
            logger.info(
                f"Closed HTTP session for {self.service_name} - "
                f"Requests: {stats['requests_made']}, "
                f"Success rate: {success_rate:.1f}%, "
                f"Retries: {stats['total_retry_attempts']}"
            )
    
    async def _make_request_with_retry(
        self,
        method: str,
        endpoint: ServiceEndpoint,
        path_params: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        """Make HTTP request with retry logic"""
        
        if not self.client:
            await self.start_session()
        
        # Prepare URL
        url = endpoint.url
        if path_params:
            for key, value in path_params.items():
                url = url.replace(f"{{{key}}}", str(value))
        
        # Track request attempt
        self._session_stats["requests_made"] += 1
        last_exception = None
        
        for attempt in range(endpoint.retries + 1):
            try:
                logger.debug(
                    f"Request attempt {attempt + 1}/{endpoint.retries + 1} "
                    f"to {self.service_name}: {method} {url}"
                )
                
                # Make the request
                response = await self.client.request(
                    method=method,
                    url=url,
                    params=query_params,
                    json=json_data,
                    files=files,
                    timeout=endpoint.timeout
                )
                
                # Check for HTTP errors
                response.raise_for_status()
                
                # Success
                self._session_stats["requests_successful"] += 1
                logger.debug(
                    f"Successful request to {self.service_name}: "
                    f"{response.status_code} {method} {url}"
                )
                
                return response
                
            except httpx.HTTPError as e:
                last_exception = e
                self._session_stats["total_retry_attempts"] += 1
                
                # Log the error
                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{endpoint.retries + 1}) "
                    f"to {self.service_name}: {str(e)}"
                )
                
                # Don't retry on client errors (4xx) except timeout
                if (isinstance(e, httpx.HTTPStatusError) and 
                    400 <= e.response.status_code < 500 and
                    e.response.status_code != 408):
                    break
                
                # Wait before retry (except on last attempt)
                if attempt < endpoint.retries:
                    await asyncio.sleep(endpoint.retry_delay * (attempt + 1))
        
        # All retries failed
        self._session_stats["requests_failed"] += 1
        integration_exception = handle_httpx_exception(last_exception, self.service_name)
        
        logger.error(
            f"All retry attempts failed for {self.service_name}: {str(integration_exception)}"
        )
        
        raise integration_exception
    
    async def get(
        self,
        endpoint: ServiceEndpoint,
        path_params: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make GET request"""
        response = await self._make_request_with_retry(
            method="GET",
            endpoint=endpoint,
            path_params=path_params,
            query_params=query_params
        )
        return response.json()
    
    async def post(
        self,
        endpoint: ServiceEndpoint,
        json_data: Optional[Dict[str, Any]] = None,
        path_params: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make POST request"""
        response = await self._make_request_with_retry(
            method="POST",
            endpoint=endpoint,
            path_params=path_params,
            query_params=query_params,
            json_data=json_data,
            files=files
        )
        return response.json()
    
    async def put(
        self,
        endpoint: ServiceEndpoint,
        json_data: Optional[Dict[str, Any]] = None,
        path_params: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make PUT request"""
        response = await self._make_request_with_retry(
            method="PUT",
            endpoint=endpoint,
            path_params=path_params,
            query_params=query_params,
            json_data=json_data
        )
        return response.json()
    
    async def delete(
        self,
        endpoint: ServiceEndpoint,
        path_params: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make DELETE request"""
        response = await self._make_request_with_retry(
            method="DELETE",
            endpoint=endpoint,
            path_params=path_params,
            query_params=query_params
        )
        return response.json() if response.content else {}
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        stats = self._session_stats.copy()
        stats["session_duration"] = (
            datetime.utcnow() - stats["session_started"]
        ).total_seconds()
        return stats