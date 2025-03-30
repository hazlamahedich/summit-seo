"""Base collector module for data collection."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio
import time
from dataclasses import dataclass
from urllib.parse import urlparse

@dataclass
class CollectionResult:
    """Data class for collection results."""
    url: str
    html_content: str
    status_code: int
    headers: Dict[str, str]
    collection_time: float
    metadata: Dict[str, Any]

class CollectorError(Exception):
    """Base exception for collector errors."""
    pass

class RateLimitError(CollectorError):
    """Exception raised when rate limit is exceeded."""
    pass

class CollectionError(CollectorError):
    """Exception raised when collection fails."""
    pass

class BaseCollector(ABC):
    """Base class for all collectors."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the collector with configuration.
        
        Args:
            config: Optional configuration dictionary with settings like:
                - requests_per_second: Maximum requests per second (float)
                - timeout: Request timeout in seconds (float)
                - max_retries: Maximum number of retries for failed requests (int)
                - retry_delay: Delay between retries in seconds (float)
                - headers: Custom headers for requests (Dict[str, str])
                - verify_ssl: Whether to verify SSL certificates (bool)
        """
        self.config = config or {}
        self._last_request_time = 0.0
        self._request_times: List[float] = []
        
        # Set default configuration values
        self.requests_per_second = float(self.config.get('requests_per_second', 2.0))
        self.timeout = float(self.config.get('timeout', 30.0))
        self.max_retries = int(self.config.get('max_retries', 3))
        self.retry_delay = float(self.config.get('retry_delay', 1.0))
        self.headers = self.config.get('headers', {})
        self.verify_ssl = bool(self.config.get('verify_ssl', True))

    async def collect(self, url: str) -> CollectionResult:
        """Collect data from the specified URL.
        
        Args:
            url: The URL to collect data from.
            
        Returns:
            CollectionResult containing the collected data.
            
        Raises:
            CollectorError: If collection fails.
            RateLimitError: If rate limit is exceeded.
        """
        # Validate URL
        try:
            parsed_url = urlparse(url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                raise CollectorError(f"Invalid URL format: {url}")
        except Exception as e:
            raise CollectorError(f"URL parsing error: {str(e)}")

        # Apply rate limiting
        await self._apply_rate_limit()

        # Attempt collection with retries
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                result = await self._collect_data(url)
                collection_time = time.time() - start_time
                
                return CollectionResult(
                    url=url,
                    html_content=result['html_content'],
                    status_code=result['status_code'],
                    headers=result['headers'],
                    collection_time=collection_time,
                    metadata=result.get('metadata', {})
                )
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise CollectionError(f"Collection failed after {self.max_retries} attempts: {str(e)}")
                await asyncio.sleep(self.retry_delay)

    async def _apply_rate_limit(self) -> None:
        """Apply rate limiting to requests."""
        current_time = time.time()
        
        # Remove old request times
        self._request_times = [t for t in self._request_times 
                             if current_time - t < 1.0]
        
        # Check if we're within rate limit
        if len(self._request_times) >= self.requests_per_second:
            sleep_time = 1.0 - (current_time - self._request_times[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        # Record this request
        self._request_times.append(current_time)
        self._last_request_time = current_time

    @abstractmethod
    async def _collect_data(self, url: str) -> Dict[str, Any]:
        """Collect data from the specified URL.
        
        This method should be implemented by concrete collectors.
        
        Args:
            url: The URL to collect data from.
            
        Returns:
            Dictionary containing:
                - html_content: The HTML content as string
                - status_code: HTTP status code
                - headers: Response headers
                - metadata: Optional additional metadata
        """
        raise NotImplementedError("Collectors must implement _collect_data method")

    @property
    def name(self) -> str:
        """Get the name of the collector."""
        return self.__class__.__name__

    def validate_config(self) -> None:
        """Validate the collector configuration.
        
        Raises:
            ValueError: If configuration is invalid.
        """
        if self.requests_per_second <= 0:
            raise ValueError("requests_per_second must be positive")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        if self.retry_delay < 0:
            raise ValueError("retry_delay cannot be negative") 