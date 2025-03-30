"""Meta analyzer implementation."""

from typing import Dict, Any, Optional, List, Set, Tuple
from bs4 import BeautifulSoup
import re
from collections import Counter

from .base import BaseAnalyzer, AnalysisResult, InputType, OutputType

class MetaAnalyzer(BaseAnalyzer[str, Dict[str, Any]]):
    """Analyzer for webpage meta tags.
    
    This analyzer examines meta tags in HTML content and provides analysis based on
    SEO best practices, including description length, keyword usage, and other
    important meta directives.
    """
    
    # Common meta tags to analyze
    META_TAGS = {
        'description': {
            'min_length': 120,
            'max_length': 160,
            'required': True,
        },
        'keywords': {
            'max_count': 10,
            'required': False,
        },
        'robots': {
            'required': False,
            'valid_values': [
                'index', 'noindex', 'follow', 'nofollow', 'none', 'noarchive',
                'nosnippet', 'noimageindex', 'nocache'
            ],
        },
        'viewport': {
            'required': True,
            'recommended': 'width=device-width, initial-scale=1',
        },
        'charset': {
            'required': True,
            'recommended': 'UTF-8',
        }
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the meta analyzer.
        
        Args:
            config: Optional configuration dictionary that may include:
                - required_tags: List of meta tags that are required
                - max_description_length: Maximum description length (default: 160)
                - min_description_length: Minimum description length (default: 120)
                - keyword_limit: Maximum number of keywords (default: 10)
                - check_opengraph: Whether to check Open Graph tags (default: True)
                - check_twitter: Whether to check Twitter Card tags (default: True)
        """
        super().__init__(config)
        
        # Set configuration values with defaults
        self.required_tags = self.config.get('required_tags', ['description', 'viewport'])
        self.max_description_length = self.config.get('max_description_length', 160)
        self.min_description_length = self.config.get('min_description_length', 120)
        self.keyword_limit = self.config.get('keyword_limit', 10)
        self.check_opengraph = self.config.get('check_opengraph', True)
        self.check_twitter = self.config.get('check_twitter', True)
        
        # Update META_TAGS with custom configuration
        if 'meta_tags' in self.config:
            for tag, settings in self.config['meta_tags'].items():
                if tag in self.META_TAGS:
                    self.META_TAGS[tag].update(settings)
                else:
                    self.META_TAGS[tag] = settings

    def analyze(self, html_content: str) -> AnalysisResult[Dict[str, Any]]:
        """Analyze the meta tags from HTML content.
        
        Args:
            html_content: HTML content containing meta tags
            
        Returns:
            AnalysisResult containing meta tag analysis data
            
        Raises:
            AnalyzerError: If analysis fails
        """
        self.validate_input(html_content)
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Initialize results
            issues = []
            warnings = []
            suggestions = []
            meta_data = {}
            
            # Extract all meta tags
            meta_tags = self._extract_meta_tags(soup)
            meta_data['meta_tags'] = meta_tags
            
            # Analyze basic meta tags
            basic_analysis = self._analyze_basic_meta_tags(meta_tags)
            issues.extend(basic_analysis['issues'])
            warnings.extend(basic_analysis['warnings'])
            suggestions.extend(basic_analysis['suggestions'])
            meta_data.update(basic_analysis['data'])
            
            # Analyze description meta tag
            if 'description' in meta_tags:
                description_analysis = self._analyze_description(meta_tags['description'])
                issues.extend(description_analysis['issues'])
                warnings.extend(description_analysis['warnings'])
                suggestions.extend(description_analysis['suggestions'])
                meta_data.update(description_analysis['data'])
            
            # Analyze keywords meta tag
            if 'keywords' in meta_tags:
                keywords_analysis = self._analyze_keywords(meta_tags['keywords'])
                issues.extend(keywords_analysis['issues'])
                warnings.extend(keywords_analysis['warnings'])
                suggestions.extend(keywords_analysis['suggestions'])
                meta_data.update(keywords_analysis['data'])
            
            # Analyze robots meta tag
            if 'robots' in meta_tags:
                robots_analysis = self._analyze_robots(meta_tags['robots'])
                issues.extend(robots_analysis['issues'])
                warnings.extend(robots_analysis['warnings'])
                suggestions.extend(robots_analysis['suggestions'])
                meta_data.update(robots_analysis['data'])
            
            # Analyze viewport meta tag
            if 'viewport' in meta_tags:
                viewport_analysis = self._analyze_viewport(meta_tags['viewport'])
                issues.extend(viewport_analysis['issues'])
                warnings.extend(viewport_analysis['warnings'])
                suggestions.extend(viewport_analysis['suggestions'])
                meta_data.update(viewport_analysis['data'])
            
            # Analyze charset meta tag or equivalent
            charset_analysis = self._analyze_charset(soup, meta_tags)
            issues.extend(charset_analysis['issues'])
            warnings.extend(charset_analysis['warnings'])
            suggestions.extend(charset_analysis['suggestions'])
            meta_data.update(charset_analysis['data'])
            
            # Check Open Graph tags if configured
            if self.check_opengraph:
                og_analysis = self._analyze_opengraph(meta_tags)
                issues.extend(og_analysis['issues'])
                warnings.extend(og_analysis['warnings'])
                suggestions.extend(og_analysis['suggestions'])
                meta_data.update(og_analysis['data'])
            
            # Check Twitter Card tags if configured
            if self.check_twitter:
                twitter_analysis = self._analyze_twitter(meta_tags)
                issues.extend(twitter_analysis['issues'])
                warnings.extend(twitter_analysis['warnings'])
                suggestions.extend(twitter_analysis['suggestions'])
                meta_data.update(twitter_analysis['data'])
            
            # Calculate score
            score = self.calculate_score(issues, warnings, meta_data)
            
            return AnalysisResult(
                data=meta_data,
                metadata=self.create_metadata('meta'),
                score=score,
                issues=issues,
                warnings=warnings,
                suggestions=suggestions
            )
        
        except Exception as e:
            raise self.error_type(f"Failed to analyze meta tags: {str(e)}")
    
    def _extract_meta_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract meta tags from HTML content.
        
        Args:
            soup: BeautifulSoup object of HTML content
            
        Returns:
            Dictionary of meta tag names and their content
        """
        meta_tags = {}
        
        # Extract meta tags with name attribute
        for tag in soup.find_all('meta', attrs={'name': True}):
            name = tag.get('name', '').lower()
            content = tag.get('content', '')
            if name and content:
                meta_tags[name] = content
        
        # Extract meta tags with property attribute (for Open Graph, etc.)
        for tag in soup.find_all('meta', attrs={'property': True}):
            prop = tag.get('property', '').lower()
            content = tag.get('content', '')
            if prop and content:
                meta_tags[prop] = content
        
        # Extract meta charset
        meta_charset = soup.find('meta', attrs={'charset': True})
        if meta_charset:
            meta_tags['charset'] = meta_charset.get('charset', '')
        
        # Extract http-equiv tags
        for tag in soup.find_all('meta', attrs={'http-equiv': True}):
            http_equiv = tag.get('http-equiv', '').lower()
            content = tag.get('content', '')
            if http_equiv and content:
                meta_tags[f'http-equiv:{http_equiv}'] = content
        
        return meta_tags
    
    def _analyze_basic_meta_tags(self, meta_tags: Dict[str, str]) -> Dict[str, Any]:
        """Analyze the presence and completeness of basic meta tags.
        
        Args:
            meta_tags: Dictionary of meta tag names and their content
            
        Returns:
            Dictionary with analysis results
        """
        issues = []
        warnings = []
        suggestions = []
        missing_required = []
        
        # Check for required meta tags
        for tag in self.required_tags:
            if tag not in meta_tags:
                missing_required.append(tag)
                issues.append(f"Missing required meta tag: {tag}")
                suggestions.append(f"Add a {tag} meta tag")
        
        return {
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'missing_required_tags': missing_required,
                'has_all_required': len(missing_required) == 0,
                'total_meta_tags': len(meta_tags)
            }
        }
    
    def _analyze_description(self, description: str) -> Dict[str, Any]:
        """Analyze the meta description.
        
        Args:
            description: Content of the description meta tag
            
        Returns:
            Dictionary with analysis results
        """
        issues = []
        warnings = []
        suggestions = []
        
        # Check description length
        length = len(description)
        is_optimal_length = self.min_description_length <= length <= self.max_description_length
        
        if length < self.min_description_length:
            warnings.append(
                f"Meta description length ({length} chars) is below "
                f"recommended minimum of {self.min_description_length} characters"
            )
            suggestions.append(
                f"Expand meta description to at least {self.min_description_length} characters"
            )
        elif length > self.max_description_length:
            warnings.append(
                f"Meta description length ({length} chars) exceeds "
                f"recommended maximum of {self.max_description_length} characters"
            )
            suggestions.append(
                f"Shorten meta description to {self.max_description_length} characters or less"
            )
        
        # Check for empty description
        if not description.strip():
            issues.append("Meta description is empty")
            suggestions.append("Add a meaningful meta description")
        
        # Check for duplicate words
        words = [word.lower() for word in re.findall(r'\b\w+\b', description)]
        word_counts = Counter(words)
        duplicates = [word for word, count in word_counts.items() 
                     if count > 2 and len(word) > 3]  # Ignore small words and low counts
        
        if duplicates:
            warnings.append(f"Meta description contains repeated words: {', '.join(duplicates)}")
            suggestions.append("Reduce word repetition in meta description")
        
        # Check for excessive punctuation
        if len(re.findall(r'[!?]', description)) > 2:
            warnings.append("Meta description contains excessive exclamation or question marks")
            suggestions.append("Use punctuation more sparingly in meta description")
        
        # Google typically displays about 155-160 characters
        is_truncated = length > 160
        if is_truncated:
            warnings.append("Meta description may be truncated in search results")
        
        return {
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'description_length': length,
                'is_optimal_length': is_optimal_length,
                'is_likely_truncated': is_truncated,
                'duplicate_words': duplicates,
                'serp_preview': self._generate_description_preview(description),
                'has_call_to_action': bool(re.search(r'\b(discover|learn|get|find|read|explore|download|try|start|view)\b', 
                                                  description, re.IGNORECASE))
            }
        }
    
    def _analyze_keywords(self, keywords: str) -> Dict[str, Any]:
        """Analyze the meta keywords.
        
        Args:
            keywords: Content of the keywords meta tag
            
        Returns:
            Dictionary with analysis results
        """
        issues = []
        warnings = []
        suggestions = []
        
        # Split keywords by common separators
        keyword_list = [k.strip() for k in re.split(r',|;|\|', keywords)]
        keyword_list = [k for k in keyword_list if k]  # Remove empty entries
        
        # Check number of keywords
        if len(keyword_list) > self.keyword_limit:
            warnings.append(
                f"Meta keywords contain {len(keyword_list)} keywords, "
                f"which exceeds the recommended limit of {self.keyword_limit}"
            )
            suggestions.append(
                f"Reduce the number of keywords to {self.keyword_limit} or fewer"
            )
        
        # Check for very long keywords
        long_keywords = [k for k in keyword_list if len(k) > 30]
        if long_keywords:
            warnings.append(f"Some keywords are excessively long: {', '.join(long_keywords)}")
            suggestions.append("Use shorter, more focused keywords")
        
        # Check for single word vs. phrases
        single_words = [k for k in keyword_list if len(k.split()) == 1]
        single_word_ratio = len(single_words) / len(keyword_list) if keyword_list else 0
        
        if single_word_ratio > 0.7 and len(keyword_list) > 3:
            warnings.append("Most keywords are single words rather than phrases")
            suggestions.append("Consider using more keyword phrases (2-3 words)")
        
        # Modern SEO note
        warnings.append(
            "Meta keywords tag has minimal impact on most modern search engines"
        )
        suggestions.append(
            "Focus on quality content and meta description rather than keywords tag"
        )
        
        return {
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'keyword_count': len(keyword_list),
                'keywords': keyword_list,
                'long_keywords': long_keywords,
                'single_word_ratio': single_word_ratio,
                'average_keyword_length': sum(len(k) for k in keyword_list) / len(keyword_list) if keyword_list else 0
            }
        }
    
    def _analyze_robots(self, robots: str) -> Dict[str, Any]:
        """Analyze the robots meta tag.
        
        Args:
            robots: Content of the robots meta tag
            
        Returns:
            Dictionary with analysis results
        """
        issues = []
        warnings = []
        suggestions = []
        
        # Split directives
        directives = [d.strip().lower() for d in robots.split(',')]
        directives = [d for d in directives if d]  # Remove empty entries
        
        # Check for valid directives
        valid_directives = set(self.META_TAGS['robots']['valid_values'])
        invalid_directives = [d for d in directives if d not in valid_directives]
        
        if invalid_directives:
            warnings.append(f"Invalid robots directives: {', '.join(invalid_directives)}")
            suggestions.append(
                f"Use standard robots directives: {', '.join(valid_directives)}"
            )
        
        # Check for noindex and warn about search visibility
        if 'noindex' in directives:
            warnings.append("Page is set to not be indexed by search engines (noindex)")
            suggestions.append(
                "Ensure this is intentional as it prevents the page from appearing in search results"
            )
        
        # Check for nofollow and warn about link authority
        if 'nofollow' in directives:
            warnings.append("Page is set to not be followed by search engines (nofollow)")
            suggestions.append(
                "Ensure this is intentional as it prevents link authority from being passed"
            )
        
        # Check for both index and noindex (conflicting)
        if 'index' in directives and 'noindex' in directives:
            issues.append("Conflicting robots directives: both index and noindex specified")
            suggestions.append("Remove either 'index' or 'noindex' directive")
        
        # Check for both follow and nofollow (conflicting)
        if 'follow' in directives and 'nofollow' in directives:
            issues.append("Conflicting robots directives: both follow and nofollow specified")
            suggestions.append("Remove either 'follow' or 'nofollow' directive")
        
        return {
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'directives': directives,
                'invalid_directives': invalid_directives,
                'is_indexable': 'noindex' not in directives,
                'is_followable': 'nofollow' not in directives,
                'has_conflicts': ('index' in directives and 'noindex' in directives) or 
                                ('follow' in directives and 'nofollow' in directives)
            }
        }
    
    def _analyze_viewport(self, viewport: str) -> Dict[str, Any]:
        """Analyze the viewport meta tag.
        
        Args:
            viewport: Content of the viewport meta tag
            
        Returns:
            Dictionary with analysis results
        """
        issues = []
        warnings = []
        suggestions = []
        
        # Check for recommended viewport setting
        recommended = self.META_TAGS['viewport']['recommended']
        is_recommended = viewport.lower() == recommended.lower()
        
        if not is_recommended:
            # Check for specific issues
            if 'width=device-width' not in viewport:
                warnings.append("Viewport meta tag is missing 'width=device-width'")
                suggestions.append("Add 'width=device-width' to viewport meta tag")
            
            if 'initial-scale=1' not in viewport:
                warnings.append("Viewport meta tag is missing 'initial-scale=1'")
                suggestions.append("Add 'initial-scale=1' to viewport meta tag")
            
            if 'user-scalable=no' in viewport or 'maximum-scale=1' in viewport:
                issues.append("Viewport prevents zooming, which harms accessibility")
                suggestions.append("Remove 'user-scalable=no' and allow maximum-scale > 1")
        
        return {
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'viewport_content': viewport,
                'is_recommended': is_recommended,
                'is_responsive': 'width=device-width' in viewport,
                'prevents_zooming': 'user-scalable=no' in viewport or 'maximum-scale=1' in viewport
            }
        }
    
    def _analyze_charset(self, soup: BeautifulSoup, meta_tags: Dict[str, str]) -> Dict[str, Any]:
        """Analyze the charset meta tag or equivalent.
        
        Args:
            soup: BeautifulSoup object of HTML content
            meta_tags: Dictionary of meta tag names and their content
            
        Returns:
            Dictionary with analysis results
        """
        issues = []
        warnings = []
        suggestions = []
        
        # Check for charset meta tag or http-equiv
        charset = None
        if 'charset' in meta_tags:
            charset = meta_tags['charset']
        elif 'http-equiv:content-type' in meta_tags:
            content_type = meta_tags['http-equiv:content-type']
            charset_match = re.search(r'charset=([^\s;]+)', content_type)
            if charset_match:
                charset = charset_match.group(1)
        
        # Check HTML5 charset on the document
        html_tag = soup.find('html')
        if html_tag and html_tag.has_attr('charset'):
            html_charset = html_tag['charset']
            if charset and html_charset != charset:
                warnings.append(f"Mismatched charset: meta says {charset}, html tag says {html_charset}")
                suggestions.append("Ensure consistent charset declaration")
            elif not charset:
                charset = html_charset
        
        # Check if charset is specified
        if not charset:
            issues.append("No character set (charset) is specified")
            suggestions.append("Add a meta charset tag, preferably UTF-8")
            is_recommended = False
        else:
            # Check if it's the recommended charset
            recommended = self.META_TAGS['charset']['recommended']
            is_recommended = charset.upper() == recommended.upper()
            
            if not is_recommended:
                warnings.append(f"Character set is {charset}, not the recommended {recommended}")
                suggestions.append(f"Consider using {recommended} for better international support")
        
        return {
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'charset': charset,
                'is_recommended_charset': bool(charset) and is_recommended,
                'has_charset': bool(charset)
            }
        }
    
    def _analyze_opengraph(self, meta_tags: Dict[str, str]) -> Dict[str, Any]:
        """Analyze Open Graph meta tags.
        
        Args:
            meta_tags: Dictionary of meta tag names and their content
            
        Returns:
            Dictionary with analysis results
        """
        issues = []
        warnings = []
        suggestions = []
        
        # Basic Open Graph tags that should be present
        essential_og_tags = ['og:title', 'og:description', 'og:image', 'og:url', 'og:type']
        
        # Extract Open Graph tags
        og_tags = {k: v for k, v in meta_tags.items() if k.startswith('og:')}
        
        # Check for missing essential tags
        missing_og = [tag for tag in essential_og_tags if tag not in og_tags]
        
        if not og_tags:
            warnings.append("No Open Graph meta tags found")
            suggestions.append(
                "Add Open Graph tags for better social media sharing"
            )
        elif missing_og:
            warnings.append(f"Missing essential Open Graph tags: {', '.join(missing_og)}")
            suggestions.append(
                f"Add missing Open Graph tags: {', '.join(missing_og)}"
            )
        
        # Check og:image for proper dimensions if present
        if 'og:image' in og_tags:
            if 'og:image:width' not in og_tags or 'og:image:height' not in og_tags:
                warnings.append("Open Graph image dimensions not specified")
                suggestions.append(
                    "Add og:image:width and og:image:height tags "
                    "(Facebook recommends 1200x630 pixels)"
                )
        
        # Check og:url for consistency with canonical if both present
        if 'og:url' in og_tags and 'canonical' in meta_tags:
            if og_tags['og:url'] != meta_tags['canonical']:
                warnings.append("Open Graph URL does not match canonical URL")
                suggestions.append(
                    "Ensure og:url matches the canonical URL for consistency"
                )
        
        return {
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'og_tags_present': list(og_tags.keys()),
                'missing_og_tags': missing_og,
                'has_essential_og': not missing_og,
                'total_og_tags': len(og_tags)
            }
        }
    
    def _analyze_twitter(self, meta_tags: Dict[str, str]) -> Dict[str, Any]:
        """Analyze Twitter Card meta tags.
        
        Args:
            meta_tags: Dictionary of meta tag names and their content
            
        Returns:
            Dictionary with analysis results
        """
        issues = []
        warnings = []
        suggestions = []
        
        # Basic Twitter Card tags that should be present
        essential_twitter_tags = ['twitter:card', 'twitter:title', 'twitter:description']
        
        # Extract Twitter Card tags
        twitter_tags = {k: v for k, v in meta_tags.items() if k.startswith('twitter:')}
        
        # Check for missing essential tags
        missing_twitter = [tag for tag in essential_twitter_tags if tag not in twitter_tags]
        
        if not twitter_tags:
            warnings.append("No Twitter Card meta tags found")
            suggestions.append(
                "Add Twitter Card tags for better Twitter sharing"
            )
        elif missing_twitter:
            warnings.append(f"Missing essential Twitter Card tags: {', '.join(missing_twitter)}")
            suggestions.append(
                f"Add missing Twitter Card tags: {', '.join(missing_twitter)}"
            )
        
        # Check twitter:card type
        if 'twitter:card' in twitter_tags:
            card_type = twitter_tags['twitter:card']
            valid_card_types = ['summary', 'summary_large_image', 'app', 'player']
            
            if card_type not in valid_card_types:
                warnings.append(f"Invalid Twitter Card type: {card_type}")
                suggestions.append(
                    f"Use a valid Twitter Card type: {', '.join(valid_card_types)}"
                )
            
            # If using summary_large_image, check for twitter:image
            if card_type == 'summary_large_image' and 'twitter:image' not in twitter_tags:
                warnings.append("Twitter Card type 'summary_large_image' requires twitter:image")
                suggestions.append("Add twitter:image tag for summary_large_image card type")
        
        return {
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'twitter_tags_present': list(twitter_tags.keys()),
                'missing_twitter_tags': missing_twitter,
                'has_essential_twitter': not missing_twitter,
                'total_twitter_tags': len(twitter_tags),
                'card_type': twitter_tags.get('twitter:card')
            }
        }
    
    def _generate_description_preview(self, description: str) -> Dict[str, Any]:
        """Generate a search preview for the meta description.
        
        Args:
            description: The meta description text
            
        Returns:
            Dictionary with preview information
        """
        display_description = description
        is_truncated = False
        
        # Google typically shows about 155-160 characters for descriptions
        if len(description) > 160:
            display_description = description[:157] + "..."
            is_truncated = True
        
        return {
            'display_description': display_description,
            'is_truncated': is_truncated,
            'character_count': len(description)
        }
    
    def calculate_score(self, issues: List[str], warnings: List[str], 
                       meta_data: Dict[str, Any]) -> float:
        """Calculate the overall score for meta tags.
        
        Args:
            issues: List of critical issues
            warnings: List of warnings
            meta_data: Additional analysis data for score calculation
            
        Returns:
            Score from 0.0 to 1.0
        """
        # Start with base score
        score = 1.0
        
        # Deduct for issues and warnings
        score -= len(issues) * 0.2  # Deduct 20% per critical issue
        score -= len(warnings) * 0.05  # Deduct 5% per warning
        
        # Specific penalties based on analysis data
        if meta_data.get('missing_required_tags'):
            score -= len(meta_data['missing_required_tags']) * 0.1
        
        # Description penalties/bonuses
        if 'description_length' in meta_data:
            if not meta_data.get('is_optimal_length', False):
                score -= 0.1
            
            if meta_data.get('duplicate_words'):
                score -= min(0.1, len(meta_data['duplicate_words']) * 0.02)
            
            if meta_data.get('has_call_to_action', False):
                score += 0.05  # Bonus for call-to-action
        
        # Robots penalties
        if 'directives' in meta_data:
            if not meta_data.get('is_indexable', True):
                score -= 0.15  # Major penalty for noindex (unless intentional)
            
            if meta_data.get('has_conflicts', False):
                score -= 0.1  # Penalty for conflicting directives
        
        # Charset penalties
        if not meta_data.get('has_charset', False):
            score -= 0.15
        
        # Open Graph and Twitter Card bonuses
        if meta_data.get('has_essential_og', False):
            score += 0.05
        
        if meta_data.get('has_essential_twitter', False):
            score += 0.05
        
        # Ensure score is within bounds
        return max(0.0, min(1.0, score)) 