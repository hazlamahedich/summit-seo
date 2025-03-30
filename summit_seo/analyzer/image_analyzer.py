"""Image SEO analyzer implementation."""

from typing import Dict, Any, Optional, List, Tuple, Set
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import os
import mimetypes

from .base import BaseAnalyzer, AnalysisResult

class ImageSEOAnalyzer(BaseAnalyzer[str, Dict[str, Any]]):
    """Analyzer for webpage image SEO optimization.
    
    This analyzer examines image elements for SEO best practices, including
    alt text quality, file naming, dimensions, loading optimization, and accessibility.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the image SEO analyzer.
        
        Args:
            config: Optional configuration dictionary that may include:
                - base_url: Base URL for resolving relative image paths (default: None)
                - min_alt_length: Minimum alt text length (default: 5)
                - max_alt_length: Maximum alt text length (default: 125)
                - max_file_size_kb: Maximum recommended file size in KB (default: 200)
                - allowed_formats: List of allowed image formats (default: ['jpg', 'jpeg', 'png', 'webp', 'svg'])
                - require_lazy_loading: Whether to require lazy loading (default: True)
                - require_width_height: Whether to require width/height attrs (default: True)
                - max_images_per_page: Maximum recommended images per page (default: 50)
        """
        super().__init__(config)
        self.base_url = self.config.get('base_url')
        self.min_alt_length = self.config.get('min_alt_length', 5)
        self.max_alt_length = self.config.get('max_alt_length', 125)
        self.max_file_size_kb = self.config.get('max_file_size_kb', 200)
        self.allowed_formats = self.config.get('allowed_formats', ['jpg', 'jpeg', 'png', 'webp', 'svg'])
        self.require_lazy_loading = self.config.get('require_lazy_loading', True)
        self.require_width_height = self.config.get('require_width_height', True)
        self.max_images_per_page = self.config.get('max_images_per_page', 50)

    def analyze(self, html_content: str) -> AnalysisResult[Dict[str, Any]]:
        """Analyze the webpage images from HTML content.
        
        Args:
            html_content: HTML content to analyze
            
        Returns:
            AnalysisResult containing image analysis data
            
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
            
            # Get all images
            images = self._get_images(soup)
            if not images:
                issues.append("No images found in content")
                return AnalysisResult(
                    data={
                        'has_images': False,
                        'image_count': 0
                    },
                    metadata=self.create_metadata('image_seo'),
                    score=0.0,
                    issues=issues,
                    warnings=warnings,
                    recommendations=["Add relevant images with proper SEO optimization"]
                )
            
            # Check total number of images
            if len(images) > self.max_images_per_page:
                issues.append(
                    f"Too many images on page ({len(images)} > {self.max_images_per_page})"
                )
            
            # Analyze alt text
            alt_issues, alt_warnings = self._analyze_alt_text(images)
            issues.extend(alt_issues)
            warnings.extend(alt_warnings)
            
            # Analyze file names
            filename_issues = self._analyze_filenames(images)
            issues.extend(filename_issues)
            
            # Analyze file formats and sizes
            format_issues = self._analyze_formats(images)
            issues.extend(format_issues)
            
            # Analyze loading optimization
            loading_issues = self._analyze_loading_optimization(images)
            issues.extend(loading_issues)
            
            # Analyze dimensions
            dimension_issues = self._analyze_dimensions(images)
            issues.extend(dimension_issues)
            
            # Generate recommendations
            recommendations.extend(self._generate_recommendations(issues, warnings))
            
            # Calculate overall score
            score = self.calculate_score(issues, warnings)
            
            # Prepare analysis data
            analysis_data = {
                'has_images': True,
                'image_count': len(images),
                'images': self._format_image_data(images),
                'format_distribution': self._analyze_format_distribution(images),
                'alt_text_analysis': self._analyze_alt_text_distribution(images),
                'loading_optimization': self._analyze_loading_stats(images),
                'dimension_stats': self._analyze_dimension_stats(images)
            }
            
            return AnalysisResult(
                data=analysis_data,
                metadata=self.create_metadata('image_seo'),
                score=score,
                issues=issues,
                warnings=warnings,
                recommendations=recommendations
            )
            
        except Exception as e:
            raise self.error_type(f"Failed to analyze images: {str(e)}")

    def _get_images(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all images from the HTML content."""
        images = []
        for img in soup.find_all('img'):
            if 'src' in img.attrs:
                src = img['src'].strip()
                if src and not src.startswith('data:'):
                    images.append({
                        'src': self._normalize_url(src),
                        'alt': img.get('alt', ''),
                        'title': img.get('title', ''),
                        'width': img.get('width', ''),
                        'height': img.get('height', ''),
                        'loading': img.get('loading', ''),
                        'html': str(img),
                        'attributes': dict(img.attrs)
                    })
        return images

    def _normalize_url(self, url: str) -> str:
        """Normalize URL by resolving relative paths."""
        if self.base_url:
            return urljoin(self.base_url, url)
        return url

    def _analyze_alt_text(
        self, images: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[str]]:
        """Analyze alt text quality."""
        issues = []
        warnings = []
        
        generic_alt = {'image', 'picture', 'photo', 'graphic', ''}
        
        for img in images:
            alt_text = img.get('alt', '').strip().lower()
            length = len(alt_text)
            
            if not alt_text:
                issues.append(f"Missing alt text: {img['src']}")
            elif length < self.min_alt_length:
                warnings.append(
                    f"Alt text too short ({length} chars): '{alt_text}'"
                )
            elif length > self.max_alt_length:
                warnings.append(
                    f"Alt text too long ({length} chars): '{alt_text}'"
                )
            
            if alt_text in generic_alt:
                warnings.append(
                    f"Generic alt text found: '{alt_text}'"
                )
                
        return issues, warnings

    def _analyze_filenames(self, images: List[Dict[str, Any]]) -> List[str]:
        """Analyze image filenames for SEO best practices."""
        issues = []
        
        for img in images:
            filename = os.path.basename(urlparse(img['src']).path)
            
            # Check for descriptive filenames
            if len(filename) < 5:
                issues.append(f"Non-descriptive filename: {filename}")
            
            # Check for proper formatting
            if not re.match(r'^[a-z0-9-]+\.[a-z]+$', filename.lower()):
                issues.append(
                    f"Filename should use lowercase letters, numbers, and hyphens: {filename}"
                )
                
        return issues

    def _analyze_formats(self, images: List[Dict[str, Any]]) -> List[str]:
        """Analyze image formats and sizes."""
        issues = []
        
        for img in images:
            src = img['src']
            ext = os.path.splitext(src)[1].lower().lstrip('.')
            
            if ext not in self.allowed_formats:
                issues.append(
                    f"Non-optimal image format '{ext}': {src}. "
                    f"Consider using: {', '.join(self.allowed_formats)}"
                )
            
            # Note: Actual file size check would require downloading the image
            # Here we could add integration with the collector module to get file sizes
                
        return issues

    def _analyze_loading_optimization(self, images: List[Dict[str, Any]]) -> List[str]:
        """Analyze image loading optimization."""
        issues = []
        
        for img in images:
            # Check for lazy loading
            if self.require_lazy_loading and img.get('loading') != 'lazy':
                issues.append(f"Image missing lazy loading: {img['src']}")
            
            # Check for srcset/sizes for responsive images
            if 'srcset' not in img['attributes']:
                issues.append(f"Image missing srcset attribute: {img['src']}")
                
        return issues

    def _analyze_dimensions(self, images: List[Dict[str, Any]]) -> List[str]:
        """Analyze image dimensions."""
        issues = []
        
        for img in images:
            # Check for explicit dimensions
            if self.require_width_height:
                if not img.get('width') or not img.get('height'):
                    issues.append(
                        f"Image missing explicit dimensions: {img['src']}"
                    )
                
        return issues

    def _format_image_data(self, images: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format image data for output."""
        return [
            {
                'src': img['src'],
                'alt': img.get('alt', ''),
                'dimensions': {
                    'width': img.get('width', ''),
                    'height': img.get('height', '')
                },
                'loading': img.get('loading', ''),
                'format': os.path.splitext(img['src'])[1].lower().lstrip('.'),
                'attributes': img['attributes']
            }
            for img in images
        ]

    def _analyze_format_distribution(self, images: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze the distribution of image formats."""
        distribution = {}
        for img in images:
            ext = os.path.splitext(img['src'])[1].lower().lstrip('.')
            distribution[ext] = distribution.get(ext, 0) + 1
        return distribution

    def _analyze_alt_text_distribution(self, images: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze the distribution of alt text types."""
        distribution = {
            'missing': 0,
            'short': 0,
            'optimal': 0,
            'long': 0,
            'generic': 0
        }
        
        generic_alt = {'image', 'picture', 'photo', 'graphic', ''}
        
        for img in images:
            alt_text = img.get('alt', '').strip().lower()
            length = len(alt_text)
            
            if not alt_text:
                distribution['missing'] += 1
            elif length < self.min_alt_length:
                distribution['short'] += 1
            elif length > self.max_alt_length:
                distribution['long'] += 1
            else:
                distribution['optimal'] += 1
                
            if alt_text in generic_alt:
                distribution['generic'] += 1
                
        return distribution

    def _analyze_loading_stats(self, images: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze image loading optimization statistics."""
        stats = {
            'lazy_loading': 0,
            'eager_loading': 0,
            'no_loading': 0,
            'has_srcset': 0,
            'no_srcset': 0
        }
        
        for img in images:
            loading = img.get('loading', '').lower()
            if loading == 'lazy':
                stats['lazy_loading'] += 1
            elif loading == 'eager':
                stats['eager_loading'] += 1
            else:
                stats['no_loading'] += 1
                
            if 'srcset' in img['attributes']:
                stats['has_srcset'] += 1
            else:
                stats['no_srcset'] += 1
                
        return stats

    def _analyze_dimension_stats(self, images: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze image dimension statistics."""
        stats = {
            'has_dimensions': 0,
            'missing_dimensions': 0,
            'missing_width': 0,
            'missing_height': 0
        }
        
        for img in images:
            has_width = bool(img.get('width'))
            has_height = bool(img.get('height'))
            
            if has_width and has_height:
                stats['has_dimensions'] += 1
            else:
                stats['missing_dimensions'] += 1
                if not has_width:
                    stats['missing_width'] += 1
                if not has_height:
                    stats['missing_height'] += 1
                    
        return stats

    def _generate_recommendations(self, issues: List[str], warnings: List[str]) -> List[str]:
        """Generate recommendations based on issues and warnings."""
        recommendations = []
        
        if "No images found in content" in issues:
            recommendations.append(
                "Add relevant images with proper alt text and optimization"
            )
        
        if any("Missing alt text" in i for i in issues):
            recommendations.append(
                "Add descriptive alt text to all images for better accessibility and SEO"
            )
        
        if any("Generic alt text" in w for w in warnings):
            recommendations.append(
                "Replace generic alt text with descriptive text that explains the image"
            )
        
        if any("Non-optimal image format" in i for i in issues):
            recommendations.append(
                f"Use optimized image formats: {', '.join(self.allowed_formats)}"
            )
        
        if any("missing lazy loading" in i.lower() for i in issues):
            recommendations.append(
                "Implement lazy loading for images to improve page load performance"
            )
        
        if any("missing srcset" in i.lower() for i in issues):
            recommendations.append(
                "Add srcset attribute for responsive images"
            )
        
        if any("missing explicit dimensions" in i.lower() for i in issues):
            recommendations.append(
                "Specify width and height attributes to prevent layout shifts"
            )
        
        if any("Non-descriptive filename" in i for i in issues):
            recommendations.append(
                "Use descriptive, SEO-friendly filenames with hyphens between words"
            )
            
        return recommendations 