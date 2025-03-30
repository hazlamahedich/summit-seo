"""Robots.txt processor module for analyzing robots.txt content."""

import re
import urllib.parse
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime
from .base import BaseProcessor, TransformationError

class RobotsTxtProcessor(BaseProcessor):
    """Processor for analyzing robots.txt content."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the robots.txt processor.
        
        Args:
            config: Optional configuration dictionary with settings:
                - validate_directives: Whether to validate directive syntax (default: True)
                - check_seo_issues: Whether to check for SEO issues (default: True)
                - evaluate_crawler_access: Whether to evaluate access for specific crawlers (default: True)
                - detect_sitemap: Whether to detect sitemap declarations (default: True)
                - extract_crawl_delays: Whether to extract crawl delay information (default: True)
                - check_common_paths: Whether to check access to common paths (default: True)
        """
        super().__init__(config)
        self.validate_directives = self.config.get('validate_directives', True)
        self.check_seo_issues = self.config.get('check_seo_issues', True)
        self.evaluate_crawler_access = self.config.get('evaluate_crawler_access', True)
        self.detect_sitemap = self.config.get('detect_sitemap', True)
        self.extract_crawl_delays = self.config.get('extract_crawl_delays', True)
        self.check_common_paths = self.config.get('check_common_paths', True)
        
        # Common web crawlers
        self.common_crawlers = {
            'googlebot': 'Google Search',
            'bingbot': 'Bing Search',
            'googlebot-image': 'Google Images',
            'googlebot-news': 'Google News',
            'googlebot-video': 'Google Video',
            'adsbot-google': 'Google AdsBot',
            'apis-google': 'Google APIs',
            'mediapartners-google': 'Google AdSense',
            'duckduckbot': 'DuckDuckGo',
            'baiduspider': 'Baidu',
            'yandexbot': 'Yandex',
            'slurp': 'Yahoo',
            'facebookexternalhit': 'Facebook',
            'linkedinbot': 'LinkedIn',
            'twitterbot': 'Twitter',
            'applebot': 'Apple',
            'msnbot': 'Bing/MSN',
            'rogerbot': 'Moz',
            'dotbot': 'OpenSiteExplorer',
            'semrushbot': 'SEMrush',
            'ahrefsbot': 'Ahrefs',
            'majestic12': 'Majestic',
            'screaming frog': 'Screaming Frog SEO Spider'
        }
        
        # Common paths to check
        self.common_paths = [
            '/', '/index.html', '/about', '/contact', '/products', '/services',
            '/blog', '/news', '/search', '/sitemap.xml', '/images', '/css', 
            '/js', '/assets', '/login', '/register', '/cart', '/checkout',
            '/wp-admin', '/wp-content', '/wp-includes', '/admin', '/cms'
        ]
    
    def _validate_config(self) -> None:
        """Validate processor configuration."""
        bool_keys = [
            'validate_directives', 'check_seo_issues', 'evaluate_crawler_access',
            'detect_sitemap', 'extract_crawl_delays', 'check_common_paths'
        ]
        
        for key in bool_keys:
            if key in self.config and not isinstance(self.config[key], bool):
                raise ValueError(f"{key} must be a boolean")
    
    def _get_required_fields(self) -> List[str]:
        """Get list of required input fields."""
        return ['robotstxt_content']
    
    async def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process robots.txt content.
        
        Args:
            data: Dictionary containing robots.txt content.
            
        Returns:
            Dictionary with processed robots.txt analysis.
            
        Raises:
            TransformationError: If robots.txt processing fails.
        """
        try:
            robotstxt_content = data['robotstxt_content']
            domain = data.get('domain', '')
            
            processed_data = {
                'original_size': len(robotstxt_content),
                'line_count': robotstxt_content.count('\n') + 1
            }
            
            # Parse the robots.txt content
            directives = self._parse_robotstxt(robotstxt_content)
            processed_data['directives'] = directives
            
            # Validate directives if configured
            if self.validate_directives:
                validation_issues = self._validate_directives(directives)
                processed_data['validation_issues'] = validation_issues
            
            # Check for SEO issues if configured
            if self.check_seo_issues:
                seo_issues = self._check_seo_issues(directives)
                processed_data['seo_issues'] = seo_issues
            
            # Evaluate crawler access if configured
            if self.evaluate_crawler_access:
                crawler_access = self._evaluate_crawler_access(directives)
                processed_data['crawler_access'] = crawler_access
            
            # Detect sitemaps if configured
            if self.detect_sitemap:
                sitemaps = self._extract_sitemaps(directives)
                processed_data['sitemaps'] = sitemaps
            
            # Extract crawl delays if configured
            if self.extract_crawl_delays:
                crawl_delays = self._extract_crawl_delays(directives)
                processed_data['crawl_delays'] = crawl_delays
            
            # Check common paths if configured
            if self.check_common_paths and domain:
                path_access = self._check_common_paths(directives, domain)
                processed_data['path_access'] = path_access
            
            # Calculate overall metrics
            processed_data['metrics'] = self._calculate_metrics(directives)
            
            return processed_data
            
        except Exception as e:
            raise TransformationError(f"Robots.txt processing failed: {str(e)}")
    
    def _parse_robotstxt(self, content: str) -> Dict[str, Any]:
        """Parse robots.txt content into structured data.
        
        Args:
            content: robots.txt file content.
            
        Returns:
            Dictionary with parsed directives.
        """
        # Initialize directives dictionary
        directives = {
            'user_agents': {},
            'sitemaps': [],
            'host': None,
            'unknown': []
        }
        
        # Split by lines and remove comments
        lines = []
        for line in content.split('\n'):
            # Remove comments (anything after #)
            comment_pos = line.find('#')
            if comment_pos != -1:
                line = line[:comment_pos]
            
            # Skip empty lines
            if line.strip():
                lines.append(line.strip())
        
        # Process directives
        current_user_agent = None
        
        for line in lines:
            # Split by first colon or space
            parts = re.split(r':\s*|\s+', line, 1)
            
            if len(parts) == 2:
                directive = parts[0].lower()
                value = parts[1].strip()
                
                if directive == 'user-agent':
                    current_user_agent = value.lower()
                    if current_user_agent not in directives['user_agents']:
                        directives['user_agents'][current_user_agent] = {
                            'allow': [],
                            'disallow': [],
                            'crawl_delay': None,
                            'request_rate': None
                        }
                elif directive == 'disallow' and current_user_agent:
                    directives['user_agents'][current_user_agent]['disallow'].append(value)
                elif directive == 'allow' and current_user_agent:
                    directives['user_agents'][current_user_agent]['allow'].append(value)
                elif directive == 'crawl-delay' and current_user_agent:
                    try:
                        directives['user_agents'][current_user_agent]['crawl_delay'] = float(value)
                    except ValueError:
                        directives['user_agents'][current_user_agent]['crawl_delay'] = value
                elif directive == 'request-rate' and current_user_agent:
                    directives['user_agents'][current_user_agent]['request_rate'] = value
                elif directive == 'sitemap':
                    directives['sitemaps'].append(value)
                elif directive == 'host':
                    directives['host'] = value
                else:
                    directives['unknown'].append(line)
        
        return directives
    
    def _validate_directives(self, directives: Dict[str, Any]) -> List[Dict[str, str]]:
        """Validate robots.txt directives for syntax issues.
        
        Args:
            directives: Parsed robots.txt directives.
            
        Returns:
            List of validation issues found.
        """
        validation_issues = []
        
        # Check for missing wildcard user-agent
        if '*' not in directives['user_agents']:
            validation_issues.append({
                'type': 'missing_wildcard',
                'message': 'No wildcard (*) user-agent defined, which may cause unexpected behavior for unlisted crawlers.'
            })
        
        # Check for URL encoding in paths
        for user_agent, rules in directives['user_agents'].items():
            for rule_type in ['allow', 'disallow']:
                for path in rules[rule_type]:
                    # Check for spaces in paths (should be encoded)
                    if ' ' in path:
                        validation_issues.append({
                            'type': 'unencoded_space',
                            'user_agent': user_agent,
                            'rule_type': rule_type,
                            'path': path,
                            'message': f'Path contains unencoded spaces: {path}'
                        })
                    
                    # Check for unescaped special characters
                    special_chars = [';', ',', '&', '=', '+', '$', '!', '\'', '(', ')', '[', ']']
                    for char in special_chars:
                        if char in path:
                            validation_issues.append({
                                'type': 'special_character',
                                'user_agent': user_agent,
                                'rule_type': rule_type,
                                'path': path,
                                'message': f'Path contains potentially unencoded special character ({char}): {path}'
                            })
        
        # Check for sitemap URL validity
        for sitemap in directives['sitemaps']:
            if not sitemap.startswith(('http://', 'https://')):
                validation_issues.append({
                    'type': 'invalid_sitemap_url',
                    'sitemap': sitemap,
                    'message': f'Sitemap URL does not start with http:// or https://: {sitemap}'
                })
        
        return validation_issues
    
    def _check_seo_issues(self, directives: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check for SEO issues in robots.txt directives.
        
        Args:
            directives: Parsed robots.txt directives.
            
        Returns:
            List of SEO issues found.
        """
        seo_issues = []
        
        # Check for complete site blocking
        for user_agent, rules in directives['user_agents'].items():
            if '/' in rules['disallow']:
                seo_issues.append({
                    'type': 'complete_site_block',
                    'user_agent': user_agent,
                    'message': f'User-agent {user_agent} is blocked from crawling the entire site with "Disallow: /"'
                })
        
        # Check for googlebot being blocked
        for user_agent in ['googlebot', 'googlebot-image', 'googlebot-news', 'googlebot-video']:
            if user_agent in directives['user_agents'] and '/' in directives['user_agents'][user_agent]['disallow']:
                seo_issues.append({
                    'type': 'google_blocked',
                    'user_agent': user_agent,
                    'message': f'{user_agent} is completely blocked, which may prevent content from appearing in Google search results'
                })
        
        # Check for important content being blocked
        important_paths = ['/about', '/product', '/service', '/blog', '/news', '/contact']
        for user_agent, rules in directives['user_agents'].items():
            for path in rules['disallow']:
                for important_path in important_paths:
                    if path == important_path or path.startswith(important_path + '/'):
                        seo_issues.append({
                            'type': 'important_content_blocked',
                            'user_agent': user_agent,
                            'path': path,
                            'message': f'Potentially important content path "{path}" is blocked for {user_agent}'
                        })
        
        # Check for missing sitemap
        if not directives['sitemaps']:
            seo_issues.append({
                'type': 'missing_sitemap',
                'message': 'No Sitemap directive found. Adding a sitemap helps search engines discover pages on your site.'
            })
        
        # Check for duplicate rules
        for user_agent, rules in directives['user_agents'].items():
            allow_set = set(rules['allow'])
            disallow_set = set(rules['disallow'])
            
            # Check for identical rules in both allow and disallow
            overlap = allow_set.intersection(disallow_set)
            if overlap:
                for path in overlap:
                    seo_issues.append({
                        'type': 'conflicting_rules',
                        'user_agent': user_agent,
                        'path': path,
                        'message': f'Path "{path}" has both Allow and Disallow directives for {user_agent}'
                    })
            
            # Check for redundant rules
            for rule_type in ['allow', 'disallow']:
                rule_list = rules[rule_type]
                if len(rule_list) != len(set(rule_list)):
                    seo_issues.append({
                        'type': 'redundant_rules',
                        'user_agent': user_agent,
                        'rule_type': rule_type,
                        'message': f'Redundant {rule_type} rules found for {user_agent}'
                    })
        
        return seo_issues
    
    def _evaluate_crawler_access(self, directives: Dict[str, Any]) -> Dict[str, Dict[str, bool]]:
        """Evaluate which crawlers have access to which types of content.
        
        Args:
            directives: Parsed robots.txt directives.
            
        Returns:
            Dictionary with crawler access information.
        """
        crawler_access = {}
        
        # Define content categories to evaluate
        content_types = {
            'general': '/',
            'images': ['/images', '/img', '/pics', '/photos'],
            'css': ['/css', '/styles', '/stylesheet'],
            'js': ['/js', '/javascript', '/scripts'],
            'pdf': ['/pdf', '.pdf'],
            'documents': ['.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx'],
            'media': ['/media', '/video', '/audio', '.mp4', '.mp3', '.wav'],
            'admin': ['/admin', '/administrator', '/wp-admin', '/dashboard'],
            'login': ['/login', '/signin', '/register', '/account'],
            'api': ['/api', '/rest', '/graphql', '/endpoint'],
            'feeds': ['/feed', '/rss', '/atom', '/xml']
        }
        
        # Get all user agents mentioned in the robots.txt
        all_agents = list(directives['user_agents'].keys())
        
        # Add common crawlers that might not be explicitly mentioned
        for crawler in self.common_crawlers.keys():
            if crawler not in all_agents and '*' not in all_agents:
                all_agents.append(crawler)
        
        # Evaluate access for each crawler and content type
        for agent in all_agents:
            crawler_access[agent] = {}
            
            # Get rules for this agent, or fall back to wildcard rules
            if agent in directives['user_agents']:
                rules = directives['user_agents'][agent]
            elif '*' in directives['user_agents'] and agent not in directives['user_agents']:
                rules = directives['user_agents']['*']
            else:
                # If no rules for this agent and no wildcard, everything is allowed
                for content_type in content_types:
                    crawler_access[agent][content_type] = True
                continue
            
            # Check each content type
            for content_type, paths in content_types.items():
                if isinstance(paths, str):
                    paths = [paths]
                
                # Assume allowed by default (robots.txt is permissive by default)
                is_allowed = True
                
                for path in paths:
                    # Check if path is explicitly disallowed
                    for disallow_rule in rules['disallow']:
                        # Empty disallow rule means everything is allowed
                        if not disallow_rule:
                            continue
                            
                        # Check if the disallow rule applies to this path
                        if self._rule_applies_to_path(disallow_rule, path):
                            # Check if there's a more specific allow rule
                            override_by_allow = False
                            for allow_rule in rules['allow']:
                                if self._rule_applies_to_path(allow_rule, path) and len(allow_rule) > len(disallow_rule):
                                    override_by_allow = True
                                    break
                            
                            if not override_by_allow:
                                is_allowed = False
                                break
                
                crawler_access[agent][content_type] = is_allowed
        
        return crawler_access
    
    def _extract_sitemaps(self, directives: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and validate sitemap declarations.
        
        Args:
            directives: Parsed robots.txt directives.
            
        Returns:
            Dictionary with sitemap information.
        """
        result = {
            'count': len(directives['sitemaps']),
            'urls': directives['sitemaps'],
            'validation': []
        }
        
        # Validate each sitemap URL
        for sitemap in directives['sitemaps']:
            validation_item = {
                'url': sitemap,
                'issues': []
            }
            
            # Check for HTTP/HTTPS
            if not sitemap.startswith(('http://', 'https://')):
                validation_item['issues'].append('URL does not use HTTP or HTTPS protocol')
            
            # Check for .xml extension or valid sitemap format
            if not sitemap.endswith('.xml') and not sitemap.endswith('.txt') and 'sitemap' not in sitemap.lower():
                validation_item['issues'].append('URL does not end with .xml or .txt extension, may not be recognized as a sitemap')
            
            # Add validation only if issues were found
            if validation_item['issues']:
                result['validation'].append(validation_item)
        
        return result
    
    def _extract_crawl_delays(self, directives: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and analyze crawl delay directives.
        
        Args:
            directives: Parsed robots.txt directives.
            
        Returns:
            Dictionary with crawl delay information.
        """
        crawl_delays = {
            'user_agents': {},
            'analysis': {
                'has_delays': False,
                'max_delay': 0,
                'avg_delay': 0,
                'recommendations': []
            }
        }
        
        delay_values = []
        
        # Extract crawl delays for each user agent
        for user_agent, rules in directives['user_agents'].items():
            if rules['crawl_delay'] is not None:
                crawl_delays['user_agents'][user_agent] = rules['crawl_delay']
                
                # Try to convert to float for analysis
                try:
                    delay_value = float(rules['crawl_delay'])
                    delay_values.append(delay_value)
                    
                    # Check for excessive delays
                    if delay_value > 5:
                        crawl_delays['analysis']['recommendations'].append({
                            'user_agent': user_agent,
                            'delay': delay_value,
                            'message': f'Crawl delay of {delay_value} seconds for {user_agent} is quite high and may slow down indexing'
                        })
                except (ValueError, TypeError):
                    pass
        
        # Update analysis
        if delay_values:
            crawl_delays['analysis']['has_delays'] = True
            crawl_delays['analysis']['max_delay'] = max(delay_values)
            crawl_delays['analysis']['avg_delay'] = sum(delay_values) / len(delay_values)
            
            # General recommendations based on average delay
            avg_delay = crawl_delays['analysis']['avg_delay']
            if avg_delay > 10:
                crawl_delays['analysis']['recommendations'].append({
                    'message': 'Average crawl delay is very high (>10s). Consider lowering to improve indexing efficiency.'
                })
            elif avg_delay > 5:
                crawl_delays['analysis']['recommendations'].append({
                    'message': 'Average crawl delay is high (>5s). May be appropriate for large sites with limited server resources.'
                })
            elif avg_delay > 1:
                crawl_delays['analysis']['recommendations'].append({
                    'message': 'Average crawl delay is moderate (>1s). Acceptable for most sites, but consider lowering if faster indexing is desired.'
                })
        
        return crawl_delays
    
    def _check_common_paths(self, directives: Dict[str, Any], domain: str) -> Dict[str, List[Dict[str, Any]]]:
        """Check how common website paths are handled in robots.txt.
        
        Args:
            directives: Parsed robots.txt directives.
            domain: Website domain for context.
            
        Returns:
            Dictionary with path access information.
        """
        result = {
            'allowed': [],
            'disallowed': [],
            'partially_allowed': []  # Allowed for some crawlers, disallowed for others
        }
        
        # Check each common path
        for path in self.common_paths:
            path_info = {
                'path': path,
                'access_by_crawler': {}
            }
            
            # Check access for each crawler
            allowed_count = 0
            disallowed_count = 0
            
            for user_agent, rules in directives['user_agents'].items():
                # Assume allowed by default
                is_allowed = True
                
                # Check disallow rules
                for disallow_rule in rules['disallow']:
                    if self._rule_applies_to_path(disallow_rule, path):
                        # Check if there's a more specific allow rule
                        override_by_allow = False
                        for allow_rule in rules['allow']:
                            if self._rule_applies_to_path(allow_rule, path) and len(allow_rule) > len(disallow_rule):
                                override_by_allow = True
                                break
                        
                        if not override_by_allow:
                            is_allowed = False
                            break
                
                path_info['access_by_crawler'][user_agent] = is_allowed
                
                if is_allowed:
                    allowed_count += 1
                else:
                    disallowed_count += 1
            
            # Determine overall status
            if disallowed_count == 0:
                result['allowed'].append(path_info)
            elif allowed_count == 0:
                result['disallowed'].append(path_info)
            else:
                result['partially_allowed'].append(path_info)
        
        return result
    
    def _calculate_metrics(self, directives: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall metrics about the robots.txt file.
        
        Args:
            directives: Parsed robots.txt directives.
            
        Returns:
            Dictionary with metrics.
        """
        metrics = {
            'user_agent_count': len(directives['user_agents']),
            'sitemap_count': len(directives['sitemaps']),
            'total_rules': 0,
            'allow_rules': 0,
            'disallow_rules': 0,
            'has_wildcard_agent': '*' in directives['user_agents'],
            'has_googlebot': any(ua.startswith('googlebot') for ua in directives['user_agents']),
            'has_crawl_delays': any(rules['crawl_delay'] is not None for rules in directives['user_agents'].values()),
            'unknown_directive_count': len(directives['unknown']),
            'is_empty': len(directives['user_agents']) == 0 and len(directives['sitemaps']) == 0,
            'blocks_everything': False,
            'allows_everything': False
        }
        
        # Count rules
        for user_agent, rules in directives['user_agents'].items():
            metrics['allow_rules'] += len(rules['allow'])
            metrics['disallow_rules'] += len(rules['disallow'])
        
        metrics['total_rules'] = metrics['allow_rules'] + metrics['disallow_rules']
        
        # Check if it blocks or allows everything
        if '*' in directives['user_agents']:
            wildcard_rules = directives['user_agents']['*']
            if '/' in wildcard_rules['disallow'] and not wildcard_rules['allow']:
                metrics['blocks_everything'] = True
            elif not wildcard_rules['disallow']:
                metrics['allows_everything'] = True
        
        return metrics
    
    def _rule_applies_to_path(self, rule: str, path: str) -> bool:
        """Check if a robots.txt rule applies to a specific path.
        
        Args:
            rule: The robots.txt rule (Allow or Disallow directive value).
            path: The path to check against.
            
        Returns:
            True if the rule applies to the path, False otherwise.
        """
        # Empty rule doesn't match anything
        if not rule:
            return False
        
        # Exact match
        if rule == path:
            return True
        
        # Rule ending with $ requires exact match
        if rule.endswith('$') and rule[:-1] == path:
            return True
        
        # Handle wildcards (*) by converting to regex
        if '*' in rule:
            # Convert robots.txt pattern to regex
            regex_pattern = rule.replace('*', '.*')
            # Escape special regex characters, except the .* we just created
            for char in ['.', '+', '?', '^', '$', '[', ']', '(', ')', '{', '}', '|', '\\']:
                if char != '.' or not regex_pattern.endswith('.*'):
                    regex_pattern = regex_pattern.replace(char, '\\' + char)
            
            return bool(re.match(f'^{regex_pattern}', path))
        
        # Path prefix match (most common case)
        return path.startswith(rule) 