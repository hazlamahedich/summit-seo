"""Link analyzer implementation."""

from typing import Dict, Any, Optional, List, Tuple, Set
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

from .base import BaseAnalyzer, AnalysisResult

class LinkAnalyzer(BaseAnalyzer[str, Dict[str, Any]]):
    """Analyzer for webpage link structure and quality.
    
    This analyzer examines internal and external links, analyzing their distribution,
    anchor text quality, accessibility, and adherence to SEO best practices.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the link analyzer.
        
        Args:
            config: Optional configuration dictionary that may include:
                - base_url: Base URL for resolving relative links (default: None)
                - min_anchor_length: Minimum anchor text length (default: 3)
                - max_anchor_length: Maximum anchor text length (default: 60)
                - max_links_per_page: Maximum recommended links per page (default: 100)
                - nofollow_external: Whether external links should have nofollow (default: True)
                - check_fragments: Whether to check for fragment identifiers (default: True)
                - allowed_schemes: List of allowed URL schemes (default: ['http', 'https'])
        """
        super().__init__(config)
        self.base_url = self.config.get('base_url')
        self.min_anchor_length = self.config.get('min_anchor_length', 3)
        self.max_anchor_length = self.config.get('max_anchor_length', 60)
        self.max_links_per_page = self.config.get('max_links_per_page', 100)
        self.nofollow_external = self.config.get('nofollow_external', True)
        self.check_fragments = self.config.get('check_fragments', True)
        self.allowed_schemes = self.config.get('allowed_schemes', ['http', 'https'])

    def analyze(self, html_content: str) -> AnalysisResult[Dict[str, Any]]:
        """Analyze the webpage link structure from HTML content.
        
        Args:
            html_content: HTML content to analyze
            
        Returns:
            AnalysisResult containing link analysis data
            
        Raises:
            AnalyzerError: If analysis fails
        """
        self.validate_input(html_content)
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Initialize analysis components
            issues: List[str] = []
            warnings: List[str] = []
            recommendations: List[str] = []
            
            # Get all links
            links = self._get_links(soup)
            if not links:
                issues.append("No links found in content")
                return AnalysisResult(
                    data={
                        'has_links': False,
                        'link_count': 0
                    },
                    metadata=self.create_metadata('link_structure'),
                    score=0.0,
                    issues=issues,
                    warnings=warnings,
                    recommendations=["Add relevant internal and external links to improve content connectivity"]
                )
            
            # Analyze link types and distribution
            internal_links, external_links = self._categorize_links(links)
            distribution_issues = self._analyze_link_distribution(len(internal_links), len(external_links))
            issues.extend(distribution_issues)
            
            # Analyze anchor text
            anchor_issues, anchor_warnings = self._analyze_anchor_text(links)
            issues.extend(anchor_issues)
            warnings.extend(anchor_warnings)
            
            # Analyze link attributes
            attribute_issues = self._analyze_link_attributes(links)
            issues.extend(attribute_issues)
            
            # Analyze link accessibility
            accessibility_issues = self._analyze_link_accessibility(links)
            issues.extend(accessibility_issues)
            
            # Generate recommendations
            recommendations.extend(self._generate_recommendations(issues, warnings))
            
            # Calculate overall score
            score = self.calculate_score(issues, warnings)
            
            # Prepare analysis data
            analysis_data = {
                'has_links': True,
                'link_count': len(links),
                'internal_links': self._format_link_data(internal_links),
                'external_links': self._format_link_data(external_links),
                'link_distribution': {
                    'internal': len(internal_links),
                    'external': len(external_links)
                },
                'unique_domains': self._count_unique_domains(external_links),
                'anchor_text_analysis': self._analyze_anchor_text_distribution(links)
            }
            
            return AnalysisResult(
                data=analysis_data,
                metadata=self.create_metadata('link_structure'),
                score=score,
                issues=issues,
                warnings=warnings,
                recommendations=recommendations
            )
            
        except Exception as e:
            raise self.error_type(f"Failed to analyze link structure: {str(e)}")

    def _get_links(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all links from the HTML content."""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            if href and not href.startswith(('javascript:', 'mailto:', 'tel:')):
                links.append({
                    'url': self._normalize_url(href),
                    'anchor_text': link.get_text().strip(),
                    'html': str(link),
                    'attributes': dict(link.attrs)
                })
        return links

    def _normalize_url(self, url: str) -> str:
        """Normalize URL by resolving relative paths and removing fragments."""
        if self.base_url:
            url = urljoin(self.base_url, url)
        if not self.check_fragments:
            url = url.split('#')[0]
        return url

    def _categorize_links(self, links: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Categorize links as internal or external."""
        internal_links = []
        external_links = []
        
        for link in links:
            if self._is_internal_link(link['url']):
                internal_links.append(link)
            else:
                external_links.append(link)
                
        return internal_links, external_links

    def _is_internal_link(self, url: str) -> bool:
        """Check if a URL is internal."""
        if not self.base_url:
            return False
        return urlparse(url).netloc == urlparse(self.base_url).netloc

    def _analyze_link_distribution(self, internal_count: int, external_count: int) -> List[str]:
        """Analyze the distribution of internal vs external links."""
        issues = []
        total_links = internal_count + external_count
        
        if total_links > self.max_links_per_page:
            issues.append(
                f"Too many links on page ({total_links} > {self.max_links_per_page})"
            )
        
        if total_links > 0 and internal_count == 0:
            issues.append("No internal links found")
            
        if external_count > internal_count * 2:
            issues.append(
                "Disproportionate number of external links compared to internal links"
            )
            
        return issues

    def _analyze_anchor_text(
        self, links: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[str]]:
        """Analyze anchor text quality."""
        issues = []
        warnings = []
        
        generic_anchors = {'click here', 'read more', 'learn more', 'more info', 'link'}
        
        for link in links:
            anchor_text = link['anchor_text'].lower()
            length = len(anchor_text)
            
            if not anchor_text:
                issues.append(f"Empty anchor text found: {link['url']}")
            elif length < self.min_anchor_length:
                warnings.append(
                    f"Anchor text too short ({length} chars): '{anchor_text}'"
                )
            elif length > self.max_anchor_length:
                warnings.append(
                    f"Anchor text too long ({length} chars): '{anchor_text}'"
                )
            
            if anchor_text in generic_anchors:
                warnings.append(
                    f"Generic anchor text found: '{anchor_text}'"
                )
                
        return issues, warnings

    def _analyze_link_attributes(self, links: List[Dict[str, Any]]) -> List[str]:
        """Analyze link attributes for SEO best practices."""
        issues = []
        
        for link in links:
            attrs = link['attributes']
            
            # Check for title attribute
            if 'title' not in attrs:
                issues.append(f"Missing title attribute: {link['url']}")
            
            # Check for rel attributes on external links
            if not self._is_internal_link(link['url']):
                if self.nofollow_external and 'rel' not in attrs:
                    issues.append(f"External link missing rel attribute: {link['url']}")
                elif self.nofollow_external and 'nofollow' not in attrs.get('rel', ''):
                    issues.append(f"External link missing nofollow: {link['url']}")
            
            # Check for target attribute
            if attrs.get('target') == '_blank' and 'rel' not in attrs:
                issues.append(
                    f"Link with target='_blank' missing rel='noopener': {link['url']}"
                )
                
        return issues

    def _analyze_link_accessibility(self, links: List[Dict[str, Any]]) -> List[str]:
        """Analyze link accessibility."""
        issues = []
        
        for link in links:
            url = link['url']
            
            # Check URL scheme
            scheme = urlparse(url).scheme
            if scheme and scheme not in self.allowed_schemes:
                issues.append(f"Invalid URL scheme '{scheme}': {url}")
            
            # Check for fragment identifiers without base URL
            if '#' in url and not self.base_url:
                issues.append(f"Fragment identifier without base URL: {url}")
            
            # Check for potentially broken relative links
            if not urlparse(url).netloc and not self.base_url:
                issues.append(f"Relative link without base URL: {url}")
                
        return issues

    def _format_link_data(self, links: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format link data for output."""
        return [
            {
                'url': link['url'],
                'anchor_text': link['anchor_text'],
                'attributes': link['attributes']
            }
            for link in links
        ]

    def _count_unique_domains(self, external_links: List[Dict[str, Any]]) -> int:
        """Count unique domains in external links."""
        domains = {urlparse(link['url']).netloc for link in external_links}
        return len(domains)

    def _analyze_anchor_text_distribution(self, links: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the distribution of anchor text types."""
        distribution = {
            'empty': 0,
            'short': 0,
            'optimal': 0,
            'long': 0,
            'generic': 0
        }
        
        generic_anchors = {'click here', 'read more', 'learn more', 'more info', 'link'}
        
        for link in links:
            anchor_text = link['anchor_text'].lower()
            length = len(anchor_text)
            
            if not anchor_text:
                distribution['empty'] += 1
            elif length < self.min_anchor_length:
                distribution['short'] += 1
            elif length > self.max_anchor_length:
                distribution['long'] += 1
            else:
                distribution['optimal'] += 1
                
            if anchor_text in generic_anchors:
                distribution['generic'] += 1
                
        return distribution

    def _generate_recommendations(self, issues: List[str], warnings: List[str]) -> List[str]:
        """Generate recommendations based on issues and warnings."""
        recommendations = []
        
        if "No links found in content" in issues:
            recommendations.append(
                "Add relevant internal and external links to improve content connectivity"
            )
        
        if "No internal links found" in issues:
            recommendations.append(
                "Add internal links to improve site navigation and content discovery"
            )
        
        if any("Empty anchor text" in i for i in issues):
            recommendations.append(
                "Provide descriptive anchor text for all links"
            )
        
        if any("Generic anchor text" in w for w in warnings):
            recommendations.append(
                "Replace generic anchor text (e.g., 'click here') with descriptive text"
            )
        
        if any("too many links" in i.lower() for i in issues):
            recommendations.append(
                f"Reduce the number of links to less than {self.max_links_per_page} "
                "for better user experience and SEO"
            )
        
        if any("missing rel attribute" in i.lower() for i in issues):
            recommendations.append(
                "Add appropriate rel attributes (nofollow, noopener) to external links"
            )
        
        if any("missing title attribute" in i.lower() for i in issues):
            recommendations.append(
                "Add descriptive title attributes to links for better accessibility"
            )
            
        return recommendations 