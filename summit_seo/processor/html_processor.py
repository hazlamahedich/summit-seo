"""HTML processor module for preparing HTML content for analysis."""

import re
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from .base import BaseProcessor, TransformationError

class HTMLProcessor(BaseProcessor):
    """Processor for preparing HTML content for analysis."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the HTML processor.
        
        Args:
            config: Optional configuration dictionary with settings:
                - parser: BeautifulSoup parser to use (default: 'html.parser')
                - clean_whitespace: Whether to clean whitespace (default: True)
                - normalize_urls: Whether to normalize URLs (default: True)
                - remove_comments: Whether to remove HTML comments (default: True)
                - extract_metadata: Whether to extract metadata (default: True)
        """
        super().__init__(config)
        self.parser = self.config.get('parser', 'html.parser')
        self.clean_whitespace = self.config.get('clean_whitespace', True)
        self.normalize_urls = self.config.get('normalize_urls', True)
        self.remove_comments = self.config.get('remove_comments', True)
        self.extract_metadata = self.config.get('extract_metadata', True)
    
    def _validate_config(self) -> None:
        """Validate processor configuration."""
        if 'parser' in self.config:
            valid_parsers = ['html.parser', 'lxml', 'html5lib']
            if self.config['parser'] not in valid_parsers:
                raise ValueError(
                    f"Invalid parser. Must be one of: {', '.join(valid_parsers)}"
                )
        
        for bool_key in ['clean_whitespace', 'normalize_urls', 
                        'remove_comments', 'extract_metadata']:
            if bool_key in self.config:
                if not isinstance(self.config[bool_key], bool):
                    raise ValueError(f"{bool_key} must be a boolean")
    
    def _get_required_fields(self) -> List[str]:
        """Get list of required input fields."""
        return ['html_content']
    
    async def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process HTML content.
        
        Args:
            data: Dictionary containing HTML content.
            
        Returns:
            Dictionary with processed HTML and extracted data.
            
        Raises:
            TransformationError: If HTML processing fails.
        """
        try:
            html_content = data['html_content']
            soup = BeautifulSoup(html_content, self.parser)
            
            # Remove comments if configured
            if self.remove_comments:
                for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
                    comment.extract()
            
            # Clean whitespace if configured
            if self.clean_whitespace:
                for element in soup.find_all(text=True):
                    if element.parent.name not in ['script', 'style']:
                        text = re.sub(r'\s+', ' ', element.strip())
                        element.replace_with(text)
            
            # Normalize URLs if configured
            if self.normalize_urls:
                base_url = data.get('url', '')
                for tag in soup.find_all(['a', 'img', 'link', 'script']):
                    for attr in ['href', 'src']:
                        if tag.get(attr):
                            tag[attr] = self._normalize_url(tag[attr], base_url)
            
            processed_data = {
                'processed_html': str(soup),
                'text_content': soup.get_text(separator=' ', strip=True)
            }
            
            # Extract metadata if configured
            if self.extract_metadata:
                metadata = self._extract_metadata(soup)
                processed_data.update(metadata)
            
            return processed_data
            
        except Exception as e:
            raise TransformationError(f"HTML processing failed: {str(e)}")
    
    def _normalize_url(self, url: str, base_url: str) -> str:
        """Normalize a URL relative to a base URL.
        
        Args:
            url: URL to normalize.
            base_url: Base URL for relative URLs.
            
        Returns:
            Normalized URL.
        """
        from urllib.parse import urljoin, urlparse
        
        # Skip URLs that are already absolute
        if urlparse(url).netloc:
            return url
            
        # Skip special URLs
        if url.startswith(('mailto:', 'tel:', 'javascript:', '#')):
            return url
            
        # Join with base URL
        return urljoin(base_url, url)
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from HTML content.
        
        Args:
            soup: BeautifulSoup object.
            
        Returns:
            Dictionary containing extracted metadata.
        """
        metadata = {}
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.string.strip()
        
        # Extract meta tags
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', ''))
            content = meta.get('content', '')
            if name and content:
                meta_tags[name] = content
        metadata['meta_tags'] = meta_tags
        
        # Extract headings
        headings = {}
        for level in range(1, 7):
            tags = soup.find_all(f'h{level}')
            if tags:
                headings[f'h{level}'] = [tag.get_text(strip=True) for tag in tags]
        metadata['headings'] = headings
        
        # Extract links
        links = []
        for link in soup.find_all('a'):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            if href:
                links.append({'href': href, 'text': text})
        metadata['links'] = links
        
        # Extract images
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            if src:
                images.append({'src': src, 'alt': alt})
        metadata['images'] = images
        
        return metadata 