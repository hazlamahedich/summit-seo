"""Sitemap processor module for analyzing sitemap.xml content."""

import re
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from .base import BaseProcessor, TransformationError

class SitemapProcessor(BaseProcessor):
    """Processor for analyzing sitemap.xml content."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the sitemap processor.
        
        Args:
            config: Optional configuration dictionary with settings:
                - validate_format: Whether to validate XML format (default: True)
                - extract_metadata: Whether to extract URL metadata (default: True)
                - analyze_seo: Whether to analyze SEO metrics (default: True)
                - check_lastmod: Whether to check last modification dates (default: True)
                - follow_sitemapindex: Whether to process sitemap index references (default: True)
                - max_urls: Maximum number of URLs to process (default: 5000)
        """
        super().__init__(config)
        self.validate_format = self.config.get('validate_format', True)
        self.extract_metadata = self.config.get('extract_metadata', True)
        self.analyze_seo = self.config.get('analyze_seo', True)
        self.check_lastmod = self.config.get('check_lastmod', True)
        self.follow_sitemapindex = self.config.get('follow_sitemapindex', True)
        self.max_urls = self.config.get('max_urls', 5000)
    
    def _validate_config(self) -> None:
        """Validate processor configuration."""
        bool_keys = [
            'validate_format', 'extract_metadata', 'analyze_seo', 
            'check_lastmod', 'follow_sitemapindex'
        ]
        
        for key in bool_keys:
            if key in self.config and not isinstance(self.config[key], bool):
                raise ValueError(f"{key} must be a boolean")
        
        if 'max_urls' in self.config and not (isinstance(self.config['max_urls'], int) and self.config['max_urls'] > 0):
            raise ValueError("max_urls must be a positive integer")
    
    def _get_required_fields(self) -> List[str]:
        """Get list of required input fields."""
        return ['sitemap_content']
    
    async def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process sitemap.xml content.
        
        Args:
            data: Dictionary containing sitemap.xml content.
            
        Returns:
            Dictionary with processed sitemap data.
            
        Raises:
            TransformationError: If sitemap processing fails.
        """
        try:
            sitemap_content = data.get('sitemap_content', '')
            sitemap_url = data.get('url', '')
            
            processed_data = {
                'original_size': len(sitemap_content),
                'is_valid': True,
                'validation_errors': []
            }
            
            # Parse the sitemap content
            try:
                # Remove XML namespace to simplify parsing
                sitemap_content = re.sub(r'\sxmlns="[^"]+"', '', sitemap_content)
                sitemap_content = re.sub(r'\sxmlns:xsi="[^"]+"', '', sitemap_content)
                sitemap_content = re.sub(r'\sxsi:schemaLocation="[^"]+"', '', sitemap_content)
                
                root = ET.fromstring(sitemap_content)
                
                # Determine sitemap type
                if root.tag == 'sitemapindex':
                    sitemap_type = 'sitemapindex'
                    sitemaps = self._process_sitemap_index(root)
                    processed_data['sitemap_type'] = 'index'
                    processed_data['sitemaps'] = sitemaps
                    processed_data['sitemap_count'] = len(sitemaps)
                else:
                    sitemap_type = 'urlset'
                    urls = self._process_urlset(root)
                    processed_data['sitemap_type'] = 'urlset'
                    processed_data['urls'] = urls
                    processed_data['url_count'] = len(urls)
                
                # Extract metadata if configured
                if self.extract_metadata and sitemap_type == 'urlset':
                    metadata = self._extract_metadata(urls)
                    processed_data['metadata'] = metadata
                
                # Analyze SEO metrics if configured
                if self.analyze_seo and sitemap_type == 'urlset':
                    seo_metrics = self._analyze_seo_metrics(urls)
                    processed_data['seo_metrics'] = seo_metrics
                
                # Check lastmod dates if configured
                if self.check_lastmod:
                    if sitemap_type == 'urlset':
                        lastmod_analysis = self._analyze_lastmod_dates(urls)
                        processed_data['lastmod_analysis'] = lastmod_analysis
                    elif sitemap_type == 'sitemapindex':
                        lastmod_analysis = self._analyze_sitemap_index_dates(sitemaps)
                        processed_data['lastmod_analysis'] = lastmod_analysis
                
            except ET.ParseError as e:
                processed_data['is_valid'] = False
                processed_data['validation_errors'].append(f"XML parsing error: {str(e)}")
            
            # Validate format if configured
            if self.validate_format and processed_data['is_valid']:
                validation_errors = self._validate_sitemap_format(sitemap_content, processed_data.get('sitemap_type', ''))
                processed_data['validation_errors'].extend(validation_errors)
                processed_data['is_valid'] = len(validation_errors) == 0
            
            return processed_data
            
        except Exception as e:
            raise TransformationError(f"Sitemap processing failed: {str(e)}")
    
    def _process_sitemap_index(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Process a sitemap index.
        
        Args:
            root: XML root element.
            
        Returns:
            List of sitemap information.
        """
        sitemaps = []
        
        for sitemap in root.findall('sitemap'):
            sitemap_data = {'url': '', 'lastmod': None}
            
            # Get loc (required)
            loc_elem = sitemap.find('loc')
            if loc_elem is not None and loc_elem.text:
                sitemap_data['url'] = loc_elem.text.strip()
            
            # Get lastmod (optional)
            lastmod_elem = sitemap.find('lastmod')
            if lastmod_elem is not None and lastmod_elem.text:
                sitemap_data['lastmod'] = lastmod_elem.text.strip()
            
            sitemaps.append(sitemap_data)
        
        return sitemaps
    
    def _process_urlset(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Process a URL set.
        
        Args:
            root: XML root element.
            
        Returns:
            List of URL information.
        """
        urls = []
        count = 0
        
        for url in root.findall('url'):
            url_data = {
                'loc': '',
                'lastmod': None,
                'changefreq': None,
                'priority': None,
                'images': [],
                'videos': [],
                'news': None,
                'mobile': False,
                'hreflang': []
            }
            
            # Get loc (required)
            loc_elem = url.find('loc')
            if loc_elem is not None and loc_elem.text:
                url_data['loc'] = loc_elem.text.strip()
            else:
                # Skip URLs without a location
                continue
            
            # Get lastmod (optional)
            lastmod_elem = url.find('lastmod')
            if lastmod_elem is not None and lastmod_elem.text:
                url_data['lastmod'] = lastmod_elem.text.strip()
            
            # Get changefreq (optional)
            changefreq_elem = url.find('changefreq')
            if changefreq_elem is not None and changefreq_elem.text:
                url_data['changefreq'] = changefreq_elem.text.strip()
            
            # Get priority (optional)
            priority_elem = url.find('priority')
            if priority_elem is not None and priority_elem.text:
                try:
                    url_data['priority'] = float(priority_elem.text.strip())
                except ValueError:
                    pass
            
            # Check for images (Google extension)
            for image in url.findall(".//image:image") or url.findall(".//image"):
                image_data = {}
                
                loc_elem = image.find('loc') or image.find('image:loc')
                if loc_elem is not None and loc_elem.text:
                    image_data['loc'] = loc_elem.text.strip()
                
                caption_elem = image.find('caption') or image.find('image:caption')
                if caption_elem is not None and caption_elem.text:
                    image_data['caption'] = caption_elem.text.strip()
                
                title_elem = image.find('title') or image.find('image:title')
                if title_elem is not None and title_elem.text:
                    image_data['title'] = title_elem.text.strip()
                
                if image_data:
                    url_data['images'].append(image_data)
            
            # Check for mobile (Google extension)
            if url.find(".//mobile:mobile") is not None or url.find(".//mobile") is not None:
                url_data['mobile'] = True
            
            # Check for hreflang entries (Google extension)
            for link in url.findall(".//xhtml:link") or url.findall(".//link"):
                if link.get('rel') == 'alternate' and link.get('hreflang') and link.get('href'):
                    url_data['hreflang'].append({
                        'hreflang': link.get('hreflang'),
                        'href': link.get('href')
                    })
            
            urls.append(url_data)
            count += 1
            
            # Respect max_urls limit
            if count >= self.max_urls:
                break
        
        return urls
    
    def _extract_metadata(self, urls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract metadata from URL information.
        
        Args:
            urls: List of URL information.
            
        Returns:
            Dictionary with metadata.
        """
        metadata = {
            'url_count': len(urls),
            'urls_with_lastmod': 0,
            'urls_with_changefreq': 0,
            'urls_with_priority': 0,
            'urls_with_images': 0,
            'urls_with_videos': 0,
            'urls_with_news': 0,
            'urls_with_mobile': 0,
            'urls_with_hreflang': 0,
            'total_images': 0,
            'total_videos': 0,
            'total_hreflang': 0,
            'changefreq_distribution': {},
            'priority_distribution': {},
            'url_patterns': {},
            'file_types': {}
        }
        
        for url in urls:
            # Count attributes
            if url.get('lastmod'):
                metadata['urls_with_lastmod'] += 1
            
            if url.get('changefreq'):
                metadata['urls_with_changefreq'] += 1
                changefreq = url['changefreq']
                metadata['changefreq_distribution'][changefreq] = metadata['changefreq_distribution'].get(changefreq, 0) + 1
            
            if url.get('priority') is not None:
                metadata['urls_with_priority'] += 1
                # Round to nearest 0.1 for distribution
                priority_bucket = round(url['priority'] * 10) / 10
                metadata['priority_distribution'][priority_bucket] = metadata['priority_distribution'].get(priority_bucket, 0) + 1
            
            # Count extensions
            if images := url.get('images', []):
                metadata['urls_with_images'] += 1
                metadata['total_images'] += len(images)
            
            if videos := url.get('videos', []):
                metadata['urls_with_videos'] += 1
                metadata['total_videos'] += len(videos)
            
            if url.get('news'):
                metadata['urls_with_news'] += 1
            
            if url.get('mobile'):
                metadata['urls_with_mobile'] += 1
            
            if hreflang := url.get('hreflang', []):
                metadata['urls_with_hreflang'] += 1
                metadata['total_hreflang'] += len(hreflang)
            
            # Analyze URL patterns (e.g., /blog/, /product/, etc.)
            url_loc = url.get('loc', '')
            path = url_loc.split('://')[-1].split('/', 1)[-1] if '://' in url_loc else url_loc
            
            pattern = None
            if not path or path == '':
                pattern = 'homepage'
            else:
                path_parts = path.strip('/').split('/')
                if path_parts:
                    pattern = path_parts[0]
            
            if pattern:
                metadata['url_patterns'][pattern] = metadata['url_patterns'].get(pattern, 0) + 1
            
            # Analyze file types
            if '.' in path.split('/')[-1]:
                file_extension = path.split('/')[-1].split('.')[-1].lower()
                if file_extension not in ('html', 'htm', 'php', 'asp', 'aspx', 'jsp'):
                    metadata['file_types'][file_extension] = metadata['file_types'].get(file_extension, 0) + 1
        
        return metadata
    
    def _analyze_seo_metrics(self, urls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze SEO metrics from URL information.
        
        Args:
            urls: List of URL information.
            
        Returns:
            Dictionary with SEO metrics.
        """
        metrics = {
            'recommendations': [],
            'priority_usage': {},
            'changefreq_consistency': {},
            'mobile_percentage': 0,
            'multilingual_percentage': 0,
            'image_seo': {},
            'lastmod_usage': {}
        }
        
        # Calculate percentages
        url_count = len(urls)
        if url_count > 0:
            metrics['mobile_percentage'] = sum(1 for url in urls if url.get('mobile')) / url_count * 100
            metrics['multilingual_percentage'] = sum(1 for url in urls if url.get('hreflang')) / url_count * 100
        
        # Analyze priority usage
        has_priority = sum(1 for url in urls if url.get('priority') is not None)
        metrics['priority_usage'] = {
            'usage_percentage': (has_priority / url_count * 100) if url_count > 0 else 0,
            'uses_default_only': all(url.get('priority') == 0.5 for url in urls if url.get('priority') is not None)
        }
        
        # Check for SEO issues and generate recommendations
        if url_count > 0:
            # Check if sitemap is too large
            if url_count > 50000:
                metrics['recommendations'].append({
                    'type': 'large_sitemap',
                    'message': f'Sitemap contains {url_count} URLs, which exceeds the recommended limit of 50,000. Consider splitting into multiple sitemaps.'
                })
            
            # Check if no URLs have lastmod
            lastmod_count = sum(1 for url in urls if url.get('lastmod'))
            metrics['lastmod_usage']['usage_percentage'] = (lastmod_count / url_count * 100)
            if lastmod_count == 0:
                metrics['recommendations'].append({
                    'type': 'missing_lastmod',
                    'message': 'None of the URLs have lastmod dates. Adding last modification dates helps search engines determine when content was updated.'
                })
            
            # Check if no URLs have changefreq
            changefreq_count = sum(1 for url in urls if url.get('changefreq'))
            if changefreq_count == 0:
                metrics['recommendations'].append({
                    'type': 'missing_changefreq',
                    'message': 'None of the URLs have changefreq values. Adding change frequency hints helps search engines determine crawl schedules.'
                })
            
            # Check if no URLs have priority
            if has_priority == 0:
                metrics['recommendations'].append({
                    'type': 'missing_priority',
                    'message': 'None of the URLs have priority values. Adding priority helps search engines understand the relative importance of pages.'
                })
            elif metrics['priority_usage']['uses_default_only']:
                metrics['recommendations'].append({
                    'type': 'default_priority_only',
                    'message': 'All URLs use the default priority (0.5). Consider adjusting priorities to indicate relative importance of different pages.'
                })
            
            # Check for duplicate URLs
            url_set = set()
            duplicate_urls = []
            for url in urls:
                loc = url.get('loc', '').lower()
                if loc in url_set:
                    duplicate_urls.append(loc)
                else:
                    url_set.add(loc)
            
            if duplicate_urls:
                metrics['recommendations'].append({
                    'type': 'duplicate_urls',
                    'message': f'Found {len(duplicate_urls)} duplicate URLs in the sitemap. Each URL should appear only once.'
                })
        
        return metrics
    
    def _analyze_lastmod_dates(self, urls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze last modification dates.
        
        Args:
            urls: List of URL information.
            
        Returns:
            Dictionary with lastmod analysis.
        """
        lastmod_analysis = {
            'has_lastmod': False,
            'lastmod_count': 0,
            'lastmod_percent': 0,
            'oldest_lastmod': None,
            'newest_lastmod': None,
            'lastmod_distribution': {},
            'issues': []
        }
        
        # Count URLs with lastmod
        urls_with_lastmod = [url for url in urls if url.get('lastmod')]
        lastmod_count = len(urls_with_lastmod)
        url_count = len(urls)
        
        lastmod_analysis['has_lastmod'] = lastmod_count > 0
        lastmod_analysis['lastmod_count'] = lastmod_count
        lastmod_analysis['lastmod_percent'] = (lastmod_count / url_count * 100) if url_count > 0 else 0
        
        if not urls_with_lastmod:
            return lastmod_analysis
        
        # Parse dates for analysis
        dates = []
        now = datetime.now()
        
        for url in urls_with_lastmod:
            lastmod = url.get('lastmod', '')
            try:
                # Try different date formats
                for fmt in ('%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d'):
                    try:
                        # Remove Z and replace with +00:00 for timezone
                        if lastmod.endswith('Z'):
                            lastmod = lastmod[:-1] + '+00:00'
                        date = datetime.strptime(lastmod, fmt)
                        dates.append((url.get('loc', ''), date))
                        break
                    except ValueError:
                        continue
            except (ValueError, TypeError):
                lastmod_analysis['issues'].append({
                    'type': 'invalid_date',
                    'url': url.get('loc', ''),
                    'lastmod': lastmod,
                    'message': f'Invalid lastmod date format: {lastmod}'
                })
        
        if not dates:
            return lastmod_analysis
        
        # Find oldest and newest dates
        dates.sort(key=lambda x: x[1])
        oldest = dates[0]
        newest = dates[-1]
        
        lastmod_analysis['oldest_lastmod'] = {
            'url': oldest[0],
            'date': oldest[1].isoformat()
        }
        
        lastmod_analysis['newest_lastmod'] = {
            'url': newest[0],
            'date': newest[1].isoformat()
        }
        
        # Check for future dates
        future_dates = [(url, date) for url, date in dates if date > now]
        if future_dates:
            lastmod_analysis['issues'].append({
                'type': 'future_dates',
                'count': len(future_dates),
                'examples': [{'url': url, 'date': date.isoformat()} for url, date in future_dates[:3]],
                'message': f'Found {len(future_dates)} URLs with lastmod dates in the future'
            })
        
        # Check for very old dates
        one_year_ago = now.replace(year=now.year - 1)
        old_dates = [(url, date) for url, date in dates if date < one_year_ago]
        if old_dates:
            lastmod_analysis['issues'].append({
                'type': 'old_dates',
                'count': len(old_dates),
                'examples': [{'url': url, 'date': date.isoformat()} for url, date in old_dates[:3]],
                'message': f'Found {len(old_dates)} URLs with lastmod dates older than one year'
            })
        
        # Create date distribution by month/year
        date_dist = {}
        for _, date in dates:
            key = f"{date.year}-{date.month:02d}"
            date_dist[key] = date_dist.get(key, 0) + 1
        
        lastmod_analysis['lastmod_distribution'] = dict(sorted(date_dist.items()))
        
        return lastmod_analysis
    
    def _analyze_sitemap_index_dates(self, sitemaps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze last modification dates in a sitemap index.
        
        Args:
            sitemaps: List of sitemap information.
            
        Returns:
            Dictionary with lastmod analysis.
        """
        lastmod_analysis = {
            'has_lastmod': False,
            'lastmod_count': 0,
            'lastmod_percent': 0,
            'oldest_lastmod': None,
            'newest_lastmod': None,
            'issues': []
        }
        
        # Count sitemaps with lastmod
        sitemaps_with_lastmod = [sm for sm in sitemaps if sm.get('lastmod')]
        lastmod_count = len(sitemaps_with_lastmod)
        sitemap_count = len(sitemaps)
        
        lastmod_analysis['has_lastmod'] = lastmod_count > 0
        lastmod_analysis['lastmod_count'] = lastmod_count
        lastmod_analysis['lastmod_percent'] = (lastmod_count / sitemap_count * 100) if sitemap_count > 0 else 0
        
        if not sitemaps_with_lastmod:
            return lastmod_analysis
        
        # Parse dates for analysis
        dates = []
        now = datetime.now()
        
        for sitemap in sitemaps_with_lastmod:
            lastmod = sitemap.get('lastmod', '')
            try:
                # Try different date formats
                for fmt in ('%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d'):
                    try:
                        # Remove Z and replace with +00:00 for timezone
                        if lastmod.endswith('Z'):
                            lastmod = lastmod[:-1] + '+00:00'
                        date = datetime.strptime(lastmod, fmt)
                        dates.append((sitemap.get('url', ''), date))
                        break
                    except ValueError:
                        continue
            except (ValueError, TypeError):
                lastmod_analysis['issues'].append({
                    'type': 'invalid_date',
                    'url': sitemap.get('url', ''),
                    'lastmod': lastmod,
                    'message': f'Invalid lastmod date format: {lastmod}'
                })
        
        if not dates:
            return lastmod_analysis
        
        # Find oldest and newest dates
        dates.sort(key=lambda x: x[1])
        oldest = dates[0]
        newest = dates[-1]
        
        lastmod_analysis['oldest_lastmod'] = {
            'url': oldest[0],
            'date': oldest[1].isoformat()
        }
        
        lastmod_analysis['newest_lastmod'] = {
            'url': newest[0],
            'date': newest[1].isoformat()
        }
        
        # Check for future dates
        future_dates = [(url, date) for url, date in dates if date > now]
        if future_dates:
            lastmod_analysis['issues'].append({
                'type': 'future_dates',
                'count': len(future_dates),
                'examples': [{'url': url, 'date': date.isoformat()} for url, date in future_dates[:3]],
                'message': f'Found {len(future_dates)} sitemaps with lastmod dates in the future'
            })
        
        return lastmod_analysis
    
    def _validate_sitemap_format(self, content: str, sitemap_type: str) -> List[Dict[str, str]]:
        """Validate sitemap format against the sitemap protocol.
        
        Args:
            content: Sitemap XML content.
            sitemap_type: Type of sitemap ('urlset' or 'sitemapindex').
            
        Returns:
            List of validation errors.
        """
        validation_errors = []
        
        # Check XML declaration
        if not content.strip().startswith('<?xml'):
            validation_errors.append({
                'type': 'missing_xml_declaration',
                'message': 'Sitemap should start with XML declaration (<?xml version="1.0" encoding="UTF-8"?>)'
            })
        
        # Check for required namespace
        if 'xmlns=' not in content:
            validation_errors.append({
                'type': 'missing_namespace',
                'message': 'Missing required namespace declaration (xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")'
            })
        
        if sitemap_type == 'urlset':
            # Check for required elements in urlset
            if '<urlset' not in content:
                validation_errors.append({
                    'type': 'missing_urlset',
                    'message': 'Missing required root element <urlset>'
                })
            
            if '<url>' not in content and '<url ' not in content:
                validation_errors.append({
                    'type': 'missing_url',
                    'message': 'No <url> elements found in sitemap'
                })
            
            if '<loc>' not in content:
                validation_errors.append({
                    'type': 'missing_loc',
                    'message': 'No <loc> elements found in sitemap'
                })
        
        elif sitemap_type == 'index':
            # Check for required elements in sitemapindex
            if '<sitemapindex' not in content:
                validation_errors.append({
                    'type': 'missing_sitemapindex',
                    'message': 'Missing required root element <sitemapindex>'
                })
            
            if '<sitemap>' not in content and '<sitemap ' not in content:
                validation_errors.append({
                    'type': 'missing_sitemap',
                    'message': 'No <sitemap> elements found in sitemap index'
                })
        
        # Check file size (should be under 50MB and ideally under 10MB)
        size_mb = len(content) / (1024 * 1024)
        if size_mb > 50:
            validation_errors.append({
                'type': 'file_too_large',
                'message': f'Sitemap is {size_mb:.2f}MB, exceeding the 50MB limit'
            })
        elif size_mb > 10:
            validation_errors.append({
                'type': 'file_large',
                'message': f'Sitemap is {size_mb:.2f}MB, which is over the recommended 10MB size'
            })
        
        return validation_errors 