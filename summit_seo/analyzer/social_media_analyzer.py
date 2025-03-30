"""Social Media analyzer implementation."""

from typing import Dict, Any, Optional, List, Set, Tuple
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

from .base import BaseAnalyzer, AnalysisResult, InputType, OutputType

class SocialMediaAnalyzer(BaseAnalyzer[Dict[str, Any], Dict[str, Any]]):
    """Analyzer for social media optimization.
    
    This analyzer examines social media tags and elements in HTML content and provides
    analysis based on best practices for social media optimization, including Open Graph tags,
    Twitter Cards, and social sharing buttons.
    """
    
    # Required Open Graph tags
    REQUIRED_OG_TAGS = ['og:title', 'og:type', 'og:image', 'og:url']
    
    # Required Twitter Card tags
    REQUIRED_TWITTER_TAGS = ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image']
    
    # Social media platforms to check for
    SOCIAL_PLATFORMS = [
        'facebook',
        'twitter',
        'linkedin',
        'pinterest',
        'instagram',
        'youtube',
        'tiktok'
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the social media analyzer.
        
        Args:
            config: Optional configuration dictionary that may include:
                - required_og_tags: List of required Open Graph tags
                - required_twitter_tags: List of required Twitter Card tags
                - social_platforms: List of social media platforms to check for
                - check_share_buttons: Whether to check for social sharing buttons (default: True)
                - check_facebook_pixel: Whether to check for Facebook Pixel (default: True)
                - check_twitter_pixel: Whether to check for Twitter Pixel (default: True)
                - image_min_width: Minimum width for social media images (default: 1200)
                - image_min_height: Minimum height for social media images (default: 630)
        """
        super().__init__(config)
        
        # Set configuration values with defaults
        self.required_og_tags = self.config.get('required_og_tags', self.REQUIRED_OG_TAGS)
        self.required_twitter_tags = self.config.get('required_twitter_tags', self.REQUIRED_TWITTER_TAGS)
        self.social_platforms = self.config.get('social_platforms', self.SOCIAL_PLATFORMS)
        self.check_share_buttons = self.config.get('check_share_buttons', True)
        self.check_facebook_pixel = self.config.get('check_facebook_pixel', True)
        self.check_twitter_pixel = self.config.get('check_twitter_pixel', True)
        self.image_min_width = self.config.get('image_min_width', 1200)
        self.image_min_height = self.config.get('image_min_height', 630)

    def analyze(self, data: Dict[str, Any]) -> AnalysisResult[Dict[str, Any]]:
        """Analyze the social media optimization from HTML content.
        
        Args:
            data: Dictionary containing HTML content and URL
            
        Returns:
            AnalysisResult containing social media optimization analysis data
            
        Raises:
            AnalyzerError: If analysis fails
        """
        self.validate_input(data)
        
        html_content = data.get('html')
        url = data.get('url')
        
        if not html_content:
            raise self.error_type("No HTML content provided for analysis")
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Initialize results
            issues = []
            warnings = []
            recommendations = []
            social_data = {
                'open_graph': {},
                'twitter_cards': {},
                'share_buttons': {},
                'social_links': {},
                'social_pixels': {}
            }
            
            # Analyze Open Graph tags
            og_analysis = self._analyze_open_graph(soup, url)
            issues.extend(og_analysis['issues'])
            warnings.extend(og_analysis['warnings'])
            recommendations.extend(og_analysis['recommendations'])
            social_data['open_graph'] = og_analysis['data']
            
            # Analyze Twitter Card tags
            twitter_analysis = self._analyze_twitter_cards(soup, url)
            issues.extend(twitter_analysis['issues'])
            warnings.extend(twitter_analysis['warnings'])
            recommendations.extend(twitter_analysis['recommendations'])
            social_data['twitter_cards'] = twitter_analysis['data']
            
            # Analyze social sharing buttons if configured
            if self.check_share_buttons:
                share_button_analysis = self._analyze_share_buttons(soup)
                issues.extend(share_button_analysis['issues'])
                warnings.extend(share_button_analysis['warnings'])
                recommendations.extend(share_button_analysis['recommendations'])
                social_data['share_buttons'] = share_button_analysis['data']
            
            # Analyze social media profile links
            social_links_analysis = self._analyze_social_links(soup)
            issues.extend(social_links_analysis['issues'])
            warnings.extend(social_links_analysis['warnings'])
            recommendations.extend(social_links_analysis['recommendations'])
            social_data['social_links'] = social_links_analysis['data']
            
            # Analyze social media pixels if configured
            pixel_analysis = self._analyze_social_pixels(soup)
            issues.extend(pixel_analysis['issues'])
            warnings.extend(pixel_analysis['warnings'])
            recommendations.extend(pixel_analysis['recommendations'])
            social_data['social_pixels'] = pixel_analysis['data']
            
            # Calculate score
            score = self._calculate_social_score(social_data, issues, warnings)
            
            return AnalysisResult(
                data=social_data,
                metadata=self.create_metadata('social_media'),
                score=score,
                issues=issues,
                warnings=warnings,
                recommendations=recommendations
            )
        
        except Exception as e:
            raise self.error_type(f"Failed to analyze social media optimization: {str(e)}")

    def _analyze_open_graph(self, soup: BeautifulSoup, url: Optional[str]) -> Dict[str, Any]:
        """Analyze Open Graph tags in HTML content.
        
        Args:
            soup: BeautifulSoup object of HTML content
            url: URL of the page being analyzed
            
        Returns:
            Dictionary containing Open Graph analysis data
        """
        result = {
            'issues': [],
            'warnings': [],
            'recommendations': [],
            'data': {}
        }
        
        # Extract all Open Graph tags
        og_tags = {}
        for tag in soup.find_all('meta', attrs={'property': True}):
            prop = tag.get('property', '').lower()
            if prop.startswith('og:'):
                content = tag.get('content', '')
                if content:
                    og_tags[prop] = content
        
        result['data']['tags'] = og_tags
        
        # Check for required tags
        missing_tags = [tag for tag in self.required_og_tags if tag not in og_tags]
        if missing_tags:
            result['issues'].append(f"Missing required Open Graph tags: {', '.join(missing_tags)}")
            result['recommendations'].append(
                f"Add the following Open Graph tags: {', '.join(missing_tags)}"
            )
        
        # Check if og:image is properly formatted
        if 'og:image' in og_tags:
            image_url = og_tags['og:image']
            # Check if image URL is absolute
            if url and not bool(urlparse(image_url).netloc):
                result['warnings'].append("Open Graph image URL should be absolute")
                absolute_url = urljoin(url, image_url)
                result['recommendations'].append(
                    f"Change og:image URL to absolute path: {absolute_url}"
                )
            
            # Check if image dimensions are specified
            if 'og:image:width' not in og_tags or 'og:image:height' not in og_tags:
                result['warnings'].append("Open Graph image dimensions not specified")
                result['recommendations'].append(
                    "Add og:image:width and og:image:height tags to improve sharing appearance"
                )
            else:
                # Check if image dimensions meet minimum requirements
                try:
                    width = int(og_tags.get('og:image:width', 0))
                    height = int(og_tags.get('og:image:height', 0))
                    
                    if width < self.image_min_width or height < self.image_min_height:
                        result['warnings'].append(
                            f"Open Graph image dimensions ({width}x{height}) are smaller than recommended "
                            f"({self.image_min_width}x{self.image_min_height})"
                        )
                        result['recommendations'].append(
                            f"Use a larger image for og:image, at least {self.image_min_width}x{self.image_min_height} pixels"
                        )
                except ValueError:
                    result['warnings'].append("Open Graph image dimensions are not valid integers")
        
        # Check for og:type
        if 'og:type' in og_tags:
            valid_types = ['website', 'article', 'blog', 'book', 'profile', 'music', 'video']
            if og_tags['og:type'] not in valid_types:
                result['warnings'].append(f"Unusual Open Graph type: {og_tags['og:type']}")
                result['recommendations'].append(
                    f"Consider using one of the common og:type values: {', '.join(valid_types)}"
                )
        
        # Check for og:description
        if 'og:description' in og_tags:
            description = og_tags['og:description']
            if len(description) < 60:
                result['warnings'].append("Open Graph description is too short")
                result['recommendations'].append(
                    "Make og:description at least 60 characters long for better social sharing"
                )
            elif len(description) > 300:
                result['warnings'].append("Open Graph description is too long")
                result['recommendations'].append(
                    "Keep og:description under 300 characters to ensure it displays properly"
                )
        
        return result

    def _analyze_twitter_cards(self, soup: BeautifulSoup, url: Optional[str]) -> Dict[str, Any]:
        """Analyze Twitter Card tags in HTML content.
        
        Args:
            soup: BeautifulSoup object of HTML content
            url: URL of the page being analyzed
            
        Returns:
            Dictionary containing Twitter Card analysis data
        """
        result = {
            'issues': [],
            'warnings': [],
            'recommendations': [],
            'data': {}
        }
        
        # Extract all Twitter Card tags
        twitter_tags = {}
        for tag in soup.find_all('meta', attrs={'name': True}):
            name = tag.get('name', '').lower()
            if name.startswith('twitter:'):
                content = tag.get('content', '')
                if content:
                    twitter_tags[name] = content
        
        result['data']['tags'] = twitter_tags
        
        # Check for required tags
        missing_tags = [tag for tag in self.required_twitter_tags if tag not in twitter_tags]
        if missing_tags:
            result['issues'].append(f"Missing required Twitter Card tags: {', '.join(missing_tags)}")
            result['recommendations'].append(
                f"Add the following Twitter Card tags: {', '.join(missing_tags)}"
            )
        
        # Check Twitter Card type
        if 'twitter:card' in twitter_tags:
            valid_card_types = ['summary', 'summary_large_image', 'app', 'player']
            if twitter_tags['twitter:card'] not in valid_card_types:
                result['warnings'].append(f"Invalid Twitter Card type: {twitter_tags['twitter:card']}")
                result['recommendations'].append(
                    f"Use one of the valid Twitter Card types: {', '.join(valid_card_types)}"
                )
        
        # Check for twitter:image
        if 'twitter:image' in twitter_tags:
            image_url = twitter_tags['twitter:image']
            # Check if image URL is absolute
            if url and not bool(urlparse(image_url).netloc):
                result['warnings'].append("Twitter image URL should be absolute")
                absolute_url = urljoin(url, image_url)
                result['recommendations'].append(
                    f"Change twitter:image URL to absolute path: {absolute_url}"
                )
        
        # Check for twitter:site (Twitter handle)
        if 'twitter:site' not in twitter_tags:
            result['warnings'].append("Twitter site handle not specified")
            result['recommendations'].append(
                "Add twitter:site meta tag with your Twitter handle"
            )
        elif not twitter_tags['twitter:site'].startswith('@'):
            result['warnings'].append("Twitter site handle should start with @")
            result['recommendations'].append(
                f"Change twitter:site to @{twitter_tags['twitter:site'].lstrip('@')}"
            )
        
        return result

    def _analyze_share_buttons(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze social media sharing buttons in HTML content.
        
        Args:
            soup: BeautifulSoup object of HTML content
            
        Returns:
            Dictionary containing social sharing button analysis data
        """
        result = {
            'issues': [],
            'warnings': [],
            'recommendations': [],
            'data': {
                'platforms': [],
                'count': 0
            }
        }
        
        # Common class patterns for share buttons
        share_patterns = [
            re.compile(r'(?i)share'),
            re.compile(r'(?i)social'),
            re.compile(r'(?i)facebook'),
            re.compile(r'(?i)twitter'),
            re.compile(r'(?i)linkedin'),
            re.compile(r'(?i)pinterest'),
            re.compile(r'(?i)instagram'),
        ]
        
        # Find elements that might be share buttons
        potential_share_elements = []
        for pattern in share_patterns:
            # Check class attributes
            for element in soup.find_all(class_=pattern):
                potential_share_elements.append(element)
            
            # Check id attributes
            for element in soup.find_all(id=pattern):
                potential_share_elements.append(element)
        
        # Find links to social platforms
        share_platforms = set()
        for platform in self.social_platforms:
            pattern = re.compile(f'(?i){platform}.*share')
            for element in soup.find_all(class_=pattern):
                share_platforms.add(platform)
            
            # Check for share URLs in hrefs
            for a in soup.find_all('a', href=re.compile(f'(?i){platform}.*share')):
                share_platforms.add(platform)
        
        result['data']['platforms'] = list(share_platforms)
        result['data']['count'] = len(share_platforms)
        
        # Provide recommendations based on findings
        if not share_platforms:
            result['issues'].append("No social sharing buttons detected")
            result['recommendations'].append(
                "Add social sharing buttons to increase content distribution"
            )
        elif len(share_platforms) < 3:
            platforms_to_add = [p for p in ['facebook', 'twitter', 'linkedin'] if p not in share_platforms]
            if platforms_to_add:
                result['warnings'].append("Limited social sharing options detected")
                result['recommendations'].append(
                    f"Consider adding more social sharing buttons: {', '.join(platforms_to_add)}"
                )
        
        return result

    def _analyze_social_links(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze social media profile links in HTML content.
        
        Args:
            soup: BeautifulSoup object of HTML content
            
        Returns:
            Dictionary containing social profile links analysis data
        """
        result = {
            'issues': [],
            'warnings': [],
            'recommendations': [],
            'data': {
                'platforms': [],
                'count': 0
            }
        }
        
        # Find links to social media profiles
        social_links = {}
        for platform in self.social_platforms:
            platform_links = []
            
            # Common patterns for social media profile links
            patterns = [
                re.compile(f'(?i){platform}\\.com'),
                re.compile(f'(?i){platform}')
            ]
            
            for pattern in patterns:
                for a in soup.find_all('a', href=pattern):
                    href = a.get('href', '')
                    if href and platform not in social_links:
                        platform_links.append(href)
            
            if platform_links:
                social_links[platform] = platform_links
        
        result['data']['platforms'] = list(social_links.keys())
        result['data']['links'] = social_links
        result['data']['count'] = len(social_links)
        
        # Provide recommendations based on findings
        if not social_links:
            result['warnings'].append("No social media profile links detected")
            result['recommendations'].append(
                "Add links to your social media profiles to increase follower growth"
            )
        elif len(social_links) < 3:
            platforms_to_add = [p for p in ['facebook', 'twitter', 'linkedin'] if p not in social_links]
            if platforms_to_add:
                result['warnings'].append("Limited social media profile links detected")
                result['recommendations'].append(
                    f"Consider adding links to more social profiles: {', '.join(platforms_to_add)}"
                )
        
        return result

    def _analyze_social_pixels(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze social media tracking pixels in HTML content.
        
        Args:
            soup: BeautifulSoup object of HTML content
            
        Returns:
            Dictionary containing social media pixel analysis data
        """
        result = {
            'issues': [],
            'warnings': [],
            'recommendations': [],
            'data': {
                'facebook_pixel': False,
                'twitter_pixel': False,
                'linkedin_pixel': False,
                'pinterest_pixel': False
            }
        }
        
        # Check for Facebook Pixel
        facebook_pixel = False
        for script in soup.find_all('script'):
            script_text = script.string if script.string else ''
            if 'fbq(' in script_text or 'facebook-pixel' in script.get('src', ''):
                facebook_pixel = True
                break
        
        result['data']['facebook_pixel'] = facebook_pixel
        
        # Check for Twitter Pixel
        twitter_pixel = False
        for script in soup.find_all('script'):
            script_text = script.string if script.string else ''
            if 'twq(' in script_text or 'twitter' in script.get('src', '') and 'pixel' in script.get('src', ''):
                twitter_pixel = True
                break
        
        result['data']['twitter_pixel'] = twitter_pixel
        
        # Check for LinkedIn Insight Tag
        linkedin_pixel = False
        for script in soup.find_all('script'):
            script_text = script.string if script.string else ''
            if '_linkedin_data_partner_id' in script_text:
                linkedin_pixel = True
                break
        
        result['data']['linkedin_pixel'] = linkedin_pixel
        
        # Check for Pinterest Tag
        pinterest_pixel = False
        for script in soup.find_all('script'):
            script_text = script.string if script.string else ''
            if 'pintrk(' in script_text:
                pinterest_pixel = True
                break
        
        result['data']['pinterest_pixel'] = pinterest_pixel
        
        # Provide recommendations based on findings
        if self.check_facebook_pixel and not facebook_pixel:
            result['warnings'].append("Facebook Pixel not detected")
            result['recommendations'].append(
                "Consider adding Facebook Pixel for conversion tracking and retargeting"
            )
        
        if self.check_twitter_pixel and not twitter_pixel:
            result['warnings'].append("Twitter Pixel not detected")
            result['recommendations'].append(
                "Consider adding Twitter Pixel for conversion tracking and audience building"
            )
        
        return result

    def _calculate_social_score(self, social_data: Dict[str, Any], issues: List[str], warnings: List[str]) -> float:
        """Calculate a score for social media optimization.
        
        Args:
            social_data: Dictionary containing social media analysis data
            issues: List of issues found
            warnings: List of warnings found
            
        Returns:
            Float score between 0 and 1
        """
        # Start with perfect score
        score = 100.0
        
        # Deduct for missing Open Graph tags
        og_tags = social_data.get('open_graph', {}).get('tags', {})
        missing_og_tags = len([tag for tag in self.required_og_tags if tag not in og_tags])
        score -= missing_og_tags * 5
        
        # Deduct for missing Twitter Card tags
        twitter_tags = social_data.get('twitter_cards', {}).get('tags', {})
        missing_twitter_tags = len([tag for tag in self.required_twitter_tags if tag not in twitter_tags])
        score -= missing_twitter_tags * 5
        
        # Deduct for missing share buttons
        if self.check_share_buttons:
            share_count = social_data.get('share_buttons', {}).get('count', 0)
            if share_count == 0:
                score -= 15
            elif share_count < 3:
                score -= 10
        
        # Deduct for missing social profile links
        social_link_count = social_data.get('social_links', {}).get('count', 0)
        if social_link_count == 0:
            score -= 10
        elif social_link_count < 3:
            score -= 5
        
        # Deduct for missing pixels
        if self.check_facebook_pixel and not social_data.get('social_pixels', {}).get('facebook_pixel', False):
            score -= 5
        
        if self.check_twitter_pixel and not social_data.get('social_pixels', {}).get('twitter_pixel', False):
            score -= 5
        
        # Deduct for issues and warnings
        score -= len(issues) * 5
        score -= len(warnings) * 2
        
        # Normalize score between 0 and 1
        return self.normalize_score(score / 100.0) 