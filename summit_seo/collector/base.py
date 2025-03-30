"""Base collector module for data collection."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio
import time
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urlparse

@dataclass
class CollectionResult:
    """Data class for collection results."""
    url: str
    content: str
    status_code: int
    headers: Dict[str, str]
    collection_time: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    cached: bool = False
    cache_key: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary.
        
        Returns:
            Dictionary representation of the result
        """
        return {
            'url': self.url,
            'status_code': self.status_code,
            'collection_time': self.collection_time,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'headers': {k: v for k, v in self.headers.items() if isinstance(v, str)},
            'cached': self.cached,
            'cache_key': self.cache_key
            # Note: content is excluded to avoid large dictionaries
        }

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
                - enable_caching: Whether to enable caching (bool)
                - cache_ttl: Cache time to live in seconds (int)
                - cache_type: Type of cache to use ('memory' or 'file') (str)
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
        
        # Caching configuration
        self.enable_caching = self.config.get('enable_caching', True)
        self.cache_ttl = self.config.get('cache_ttl', 3600)  # 1 hour default
        self.cache_type = self.config.get('cache_type', 'memory')

    async def collect(self, url: str) -> CollectionResult:
        """Collect data from the specified URL.
        
        This implementation checks the cache first, and only performs collection
        if the result is not found in cache or if caching is disabled.
        
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
        
        # Check cache if enabled
        if self.enable_caching:
            try:
                from ..cache import cache_manager
                
                # Generate cache key
                cache_key = self.generate_cache_key(url)
                
                # Try to get result from cache
                cache_result = await cache_manager.get(
                    cache_key, 
                    cache_type=self.cache_type,
                    name=self.get_cache_name()
                )
                
                if cache_result.hit and not cache_result.expired:
                    # Cache hit, return cached result
                    cached_result = cache_result.value
                    
                    # Update metadata to indicate cached result
                    cached_result.cached = True
                    cached_result.cache_key = cache_key
                    
                    return cached_result
                    
            except ImportError:
                # Cache module not available, continue with collection
                pass
            except Exception as e:
                # Log cache error but continue with collection
                import logging
                logging.warning(f"Cache error in {self.__class__.__name__}: {str(e)}")

        # Apply rate limiting
        await self._apply_rate_limit()

        # Attempt collection with retries
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                result = await self._collect_data(url)
                collection_time = time.time() - start_time
                
                # Create collection result
                collection_result = CollectionResult(
                    url=url,
                    content=result['content'],
                    status_code=result['status_code'],
                    headers=result['headers'],
                    collection_time=collection_time,
                    metadata=result.get('metadata', {}),
                    timestamp=datetime.now()
                )
                
                # Cache result if caching is enabled
                if self.enable_caching:
                    try:
                        from ..cache import cache_manager
                        
                        cache_key = self.generate_cache_key(url)
                        
                        # Store result in cache
                        await cache_manager.set(
                            cache_key,
                            collection_result,
                            ttl=self.cache_ttl,
                            cache_type=self.cache_type,
                            name=self.get_cache_name()
                        )
                        
                        # Update cache key in result
                        collection_result.cache_key = cache_key
                        
                    except ImportError:
                        # Cache module not available, skip caching
                        pass
                    except Exception as e:
                        # Log cache error
                        import logging
                        logging.warning(f"Cache error in {self.__class__.__name__}: {str(e)}")
                
                return collection_result
                
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
                - content: The HTML content as string
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
            
    def generate_cache_key(self, url: str) -> str:
        """Generate a cache key for the URL.
        
        Args:
            url: The URL to generate a cache key for
            
        Returns:
            Cache key string
        """
        # Use collector class name as prefix
        prefix = self.__class__.__name__
        
        # Hash the URL and any relevant configuration
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        
        # Include relevant configuration in cache key
        config_hash = ""
        if self.config:
            # Only include config keys that affect collection results
            collection_config = {
                'headers': self.headers,
                'verify_ssl': self.verify_ssl,
                'timeout': self.timeout
            }
            
            if collection_config:
                config_hash = hashlib.md5(json.dumps(collection_config, sort_keys=True).encode('utf-8')).hexdigest()[:8]
                return f"{prefix}:{url_hash}:{config_hash}"
        
        return f"{prefix}:{url_hash}"
    
    def get_cache_name(self) -> Optional[str]:
        """Get the cache name based on TTL.
        
        Returns:
            Cache name (short, medium, long) or None for default
        """
        if self.cache_ttl <= 300:  # 5 minutes or less
            return 'short'
        elif self.cache_ttl <= 3600:  # 1 hour or less
            return 'medium'
        elif self.cache_ttl <= 86400:  # 24 hours or less
            return 'long'
        
        return None 