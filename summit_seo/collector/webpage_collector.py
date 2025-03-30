"""Web page collector implementation."""

import aiohttp
import asyncio
from typing import Dict, Any, Optional
from .base import BaseCollector, CollectionError
from bs4 import BeautifulSoup
import chardet

class WebPageCollector(BaseCollector):
    """Collector for fetching web pages using aiohttp."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the web page collector.
        
        Args:
            config: Optional configuration dictionary with settings like:
                - requests_per_second: Maximum requests per second (float)
                - timeout: Request timeout in seconds (float)
                - max_retries: Maximum number of retries for failed requests (int)
                - retry_delay: Delay between retries in seconds (float)
                - headers: Custom headers for requests (Dict[str, str])
                - verify_ssl: Whether to verify SSL certificates (bool)
                - follow_redirects: Whether to follow redirects (bool)
                - max_redirects: Maximum number of redirects to follow (int)
                - proxy: Proxy URL to use (str)
                - cookies: Cookies to send with requests (Dict[str, str])
        """
        super().__init__(config)
        
        # Additional configuration
        self.follow_redirects = bool(self.config.get('follow_redirects', True))
        self.max_redirects = int(self.config.get('max_redirects', 5))
        self.proxy = self.config.get('proxy')
        self.cookies = self.config.get('cookies', {})
        
        # Default headers for web requests
        self.headers.update({
            'User-Agent': self.config.get('user_agent', 
                'Mozilla/5.0 (compatible; SummitSEO/1.0; +https://summit-seo.com/bot)'),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

    async def _collect_data(self, url: str) -> Dict[str, Any]:
        """Collect data from the specified URL using aiohttp.
        
        Args:
            url: The URL to collect data from.
            
        Returns:
            Dictionary containing:
                - html_content: The HTML content as string
                - status_code: HTTP status code
                - headers: Response headers
                - metadata: Additional metadata about the request
                
        Raises:
            CollectionError: If collection fails.
        """
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(
            headers=self.headers,
            cookies=self.cookies,
            timeout=timeout
        ) as session:
            try:
                async with session.get(
                    url,
                    proxy=self.proxy,
                    ssl=self.verify_ssl,
                    allow_redirects=self.follow_redirects,
                    max_redirects=self.max_redirects
                ) as response:
                    # Read response content
                    content = await response.read()
                    
                    # Detect encoding
                    encoding = response.charset or chardet.detect(content)['encoding'] or 'utf-8'
                    
                    try:
                        html_content = content.decode(encoding)
                    except UnicodeDecodeError:
                        # Fallback to utf-8 if specified encoding fails
                        html_content = content.decode('utf-8', errors='replace')
                    
                    # Parse with BeautifulSoup to get metadata
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Extract metadata
                    metadata = {
                        'title': soup.title.string if soup.title else None,
                        'encoding': encoding,
                        'content_type': response.headers.get('Content-Type'),
                        'content_length': len(content),
                        'is_redirect': response.history is not None and len(response.history) > 0,
                        'redirect_count': len(response.history) if response.history else 0,
                        'final_url': str(response.url)
                    }
                    
                    return {
                        'html_content': html_content,
                        'status_code': response.status,
                        'headers': dict(response.headers),
                        'metadata': metadata
                    }
                    
            except asyncio.TimeoutError:
                raise CollectionError(f"Request timed out after {self.timeout} seconds")
            except aiohttp.ClientError as e:
                raise CollectionError(f"HTTP request failed: {str(e)}")
            except Exception as e:
                raise CollectionError(f"Collection failed: {str(e)}")

    def validate_config(self) -> None:
        """Validate the collector configuration.
        
        Raises:
            ValueError: If configuration is invalid.
        """
        super().validate_config()
        
        if self.max_redirects < 0:
            raise ValueError("max_redirects cannot be negative")
        
        if self.proxy and not isinstance(self.proxy, str):
            raise ValueError("proxy must be a string URL")
        
        if not isinstance(self.cookies, dict):
            raise ValueError("cookies must be a dictionary")
        
        if not isinstance(self.headers, dict):
            raise ValueError("headers must be a dictionary") 