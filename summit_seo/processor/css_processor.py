"""CSS processor module for analyzing CSS content."""

import re
import math
from typing import Dict, Any, List, Optional, Set, Tuple
from .base import BaseProcessor, TransformationError

class CSSProcessor(BaseProcessor):
    """Processor for analyzing CSS content."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the CSS processor.
        
        Args:
            config: Optional configuration dictionary with settings:
                - minify: Whether to minify the CSS (default: False)
                - analyze_selectors: Whether to analyze selectors (default: True)
                - count_media_queries: Whether to count media queries (default: True)
                - detect_browser_hacks: Whether to detect browser hacks (default: True)
                - find_unused_selectors: Whether to find unused selectors (default: False)
                - analyze_colors: Whether to analyze color usage (default: True)
                - detect_duplicates: Whether to detect duplicate rules (default: True)
        """
        super().__init__(config)
        self.minify = self.config.get('minify', False)
        self.analyze_selectors = self.config.get('analyze_selectors', True)
        self.count_media_queries = self.config.get('count_media_queries', True)
        self.detect_browser_hacks = self.config.get('detect_browser_hacks', True)
        self.find_unused_selectors = self.config.get('find_unused_selectors', False)
        self.analyze_colors = self.config.get('analyze_colors', True)
        self.detect_duplicates = self.config.get('detect_duplicates', True)
    
    def _validate_config(self) -> None:
        """Validate processor configuration."""
        bool_keys = [
            'minify', 'analyze_selectors', 'count_media_queries', 
            'detect_browser_hacks', 'find_unused_selectors', 'analyze_colors',
            'detect_duplicates'
        ]
        
        for key in bool_keys:
            if key in self.config and not isinstance(self.config[key], bool):
                raise ValueError(f"{key} must be a boolean")
    
    def _get_required_fields(self) -> List[str]:
        """Get list of required input fields."""
        return ['css_content']
    
    async def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process CSS content.
        
        Args:
            data: Dictionary containing CSS content.
            
        Returns:
            Dictionary with processed CSS and analysis results.
            
        Raises:
            TransformationError: If CSS processing fails.
        """
        try:
            css_content = data['css_content']
            html_content = data.get('html_content', '')  # Optional for selector matching
            
            processed_data = {
                'original_size': len(css_content),
                'line_count': css_content.count('\n') + 1
            }
            
            # Minify CSS if configured
            if self.minify:
                minified_css = self._minify_css(css_content)
                processed_data['minified_content'] = minified_css
                processed_data['minified_size'] = len(minified_css)
                processed_data['size_reduction'] = round(
                    (1 - len(minified_css) / len(css_content)) * 100, 2
                )
            else:
                processed_data['processed_content'] = css_content
            
            # Analyze selectors if configured
            if self.analyze_selectors:
                selector_analysis = self._analyze_selectors(css_content)
                processed_data['selector_analysis'] = selector_analysis
            
            # Count media queries if configured
            if self.count_media_queries:
                media_queries = self._analyze_media_queries(css_content)
                processed_data['media_queries'] = media_queries
            
            # Detect browser hacks if configured
            if self.detect_browser_hacks:
                browser_hacks = self._detect_browser_hacks(css_content)
                processed_data['browser_hacks'] = browser_hacks
            
            # Find unused selectors if configured
            if self.find_unused_selectors and html_content:
                unused_selectors = self._find_unused_selectors(css_content, html_content)
                processed_data['unused_selectors'] = unused_selectors
            
            # Analyze colors if configured
            if self.analyze_colors:
                color_analysis = self._analyze_colors(css_content)
                processed_data['color_analysis'] = color_analysis
            
            # Detect duplicate rules if configured
            if self.detect_duplicates:
                duplicates = self._detect_duplicates(css_content)
                processed_data['duplicates'] = duplicates
            
            return processed_data
            
        except Exception as e:
            raise TransformationError(f"CSS processing failed: {str(e)}")
    
    def _minify_css(self, css_content: str) -> str:
        """Minify CSS content.
        
        Args:
            css_content: CSS content to minify.
            
        Returns:
            Minified CSS content.
        """
        # Remove comments
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        
        # Remove whitespace
        css_content = re.sub(r'\s+', ' ', css_content)
        css_content = re.sub(r';\s*}', '}', css_content)
        css_content = re.sub(r':\s+', ':', css_content)
        css_content = re.sub(r',\s+', ',', css_content)
        css_content = re.sub(r'{\s+', '{', css_content)
        css_content = re.sub(r'}\s+', '}', css_content)
        css_content = re.sub(r';\s+', ';', css_content)
        
        # Remove last semicolon in each rule
        css_content = re.sub(r';}', '}', css_content)
        
        return css_content.strip()
    
    def _analyze_selectors(self, css_content: str) -> Dict[str, Any]:
        """Analyze CSS selectors.
        
        Args:
            css_content: CSS content to analyze.
            
        Returns:
            Dictionary with selector analysis.
        """
        # Remove comments and string content first
        clean_css = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        
        # Extract all selectors
        selector_blocks = re.findall(r'([^{]+){[^}]*}', clean_css)
        selectors = []
        
        for block in selector_blocks:
            # Skip @media queries and other @ rules for selector counting
            if block.strip().startswith('@'):
                continue
                
            # Split and clean selectors
            block_selectors = [s.strip() for s in block.split(',')]
            selectors.extend(block_selectors)
        
        # Calculate selector specificity
        specificities = {
            'id': 0,
            'class': 0,
            'tag': 0,
            'attribute': 0,
            'pseudo': 0
        }
        
        for selector in selectors:
            # Count ID selectors (#id)
            specificities['id'] += len(re.findall(r'#[\w-]+', selector))
            
            # Count class selectors (.class)
            specificities['class'] += len(re.findall(r'\.[\w-]+', selector))
            
            # Count attribute selectors ([attr])
            specificities['attribute'] += len(re.findall(r'\[\w+(?:[~^$*|]?=[\'"]\w+[\'"]+)?\]', selector))
            
            # Count pseudo-classes and pseudo-elements (:hover, ::before)
            specificities['pseudo'] += len(re.findall(r':{1,2}[\w-]+(?:\([^)]*\))?', selector))
            
            # Count tag selectors (div, span)
            tag_selectors = re.findall(r'(?<![#\.\w-])[a-zA-Z][\w-]*', selector)
            specificities['tag'] += len(tag_selectors)
        
        # Find complex selectors
        complex_selectors = [s for s in selectors if len(re.split(r'\s+|[>+~]', s)) > 1]
        
        # Calculate selector complexity score
        complexity_scores = []
        for selector in selectors:
            # Complexity factors
            id_count = len(re.findall(r'#[\w-]+', selector))
            class_count = len(re.findall(r'\.[\w-]+', selector))
            attr_count = len(re.findall(r'\[\w+(?:[~^$*|]?=[\'"]\w+[\'"]+)?\]', selector))
            pseudo_count = len(re.findall(r':{1,2}[\w-]+(?:\([^)]*\))?', selector))
            combinators = len(re.findall(r'[>+~]', selector))
            nesting_level = len(re.split(r'\s+|[>+~]', selector))
            
            # Calculate a weighted complexity score
            score = (
                id_count * 100 +
                class_count * 10 +
                attr_count * 10 +
                pseudo_count * 5 +
                combinators * 5 +
                nesting_level
            )
            complexity_scores.append(score)
        
        return {
            'total_selectors': len(selectors),
            'unique_selectors': len(set(selectors)),
            'average_specificity': {
                'id': specificities['id'] / len(selectors) if selectors else 0,
                'class': specificities['class'] / len(selectors) if selectors else 0,
                'tag': specificities['tag'] / len(selectors) if selectors else 0,
                'attribute': specificities['attribute'] / len(selectors) if selectors else 0,
                'pseudo': specificities['pseudo'] / len(selectors) if selectors else 0
            },
            'complex_selectors': len(complex_selectors),
            'complex_selector_examples': complex_selectors[:5] if complex_selectors else [],
            'average_complexity': sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0,
            'max_complexity': max(complexity_scores) if complexity_scores else 0,
            'complexity_histogram': self._create_histogram(complexity_scores, 5) if complexity_scores else {}
        }
    
    def _analyze_media_queries(self, css_content: str) -> Dict[str, Any]:
        """Analyze media queries in CSS content.
        
        Args:
            css_content: CSS content to analyze.
            
        Returns:
            Dictionary with media query analysis.
        """
        # Extract all media queries
        media_query_blocks = re.findall(r'@media\s+([^{]+){', css_content)
        
        if not media_query_blocks:
            return {
                'total_queries': 0,
                'responsive_design': False,
                'queries': []
            }
        
        # Analyze media query types
        media_types = {
            'screen': 0,
            'print': 0,
            'all': 0,
            'speech': 0,
            'other': 0
        }
        
        # Categorize media features
        media_features = {
            'width': 0,
            'height': 0,
            'orientation': 0,
            'resolution': 0,
            'aspect-ratio': 0,
            'color': 0,
            'other': 0
        }
        
        # Extract breakpoints for width-based media queries
        breakpoints = []
        
        unique_queries = set(media_query_blocks)
        queries_data = []
        
        for query in unique_queries:
            query_data = {'query': query.strip(), 'features': []}
            
            # Check media types
            for media_type in media_types.keys():
                if media_type in query and re.search(r'\b' + media_type + r'\b', query):
                    media_types[media_type] += 1
                    query_data['type'] = media_type
                    break
            else:
                # If no specific type found, it's likely 'all'
                media_types['all'] += 1
                query_data['type'] = 'all'
            
            # Check media features
            for feature in ['width', 'height', 'orientation', 'resolution', 'aspect-ratio', 'color']:
                if feature in query:
                    media_features[feature] += 1
                    query_data['features'].append(feature)
                    
                    # Extract breakpoints for width/height
                    if feature in ['width', 'height']:
                        # Look for min-/max- width/height values
                        value_match = re.search(r'(?:min|max)-' + feature + r'[\s:]+(\d+)(?:px|em|rem)', query)
                        if value_match:
                            value = int(value_match.group(1))
                            unit = re.search(r'(?:min|max)-' + feature + r'[\s:]+\d+(px|em|rem)', query).group(1)
                            breakpoint_type = 'min' if 'min-' + feature in query else 'max'
                            
                            breakpoints.append({
                                'value': value,
                                'unit': unit,
                                'type': breakpoint_type,
                                'feature': feature
                            })
            
            queries_data.append(query_data)
        
        # Check for responsive design (at least 2 different width breakpoints)
        width_breakpoints = [b for b in breakpoints if b['feature'] == 'width']
        is_responsive = len(width_breakpoints) >= 2
        
        return {
            'total_queries': len(media_query_blocks),
            'unique_queries': len(unique_queries),
            'responsive_design': is_responsive,
            'media_types': media_types,
            'media_features': media_features,
            'breakpoints': sorted(
                width_breakpoints, 
                key=lambda x: x['value']
            ) if width_breakpoints else [],
            'queries': queries_data
        }
    
    def _detect_browser_hacks(self, css_content: str) -> List[Dict[str, Any]]:
        """Detect browser hacks in CSS content.
        
        Args:
            css_content: CSS content to analyze.
            
        Returns:
            List of detected browser hacks.
        """
        browser_hacks = []
        
        # Common browser hacks patterns
        hack_patterns = [
            {
                'pattern': r'_[\w-]+\s*:',
                'browser': 'IE6',
                'description': 'Underscore hack for IE6'
            },
            {
                'pattern': r'\*[\w-]+\s*:',
                'browser': 'IE6-7',
                'description': 'Star hack for IE6-7'
            },
            {
                'pattern': r'#[\w-]+\s*>\s*\*\s*[\w-]+\s*:',
                'browser': 'IE6-7',
                'description': 'Child selector combined with star hack for IE6-7'
            },
            {
                'pattern': r'/\*\\*/[\w\s:;]+/\*/[\w\s:;]+',
                'browser': 'IE8',
                'description': 'Comment backslash hack for IE8'
            },
            {
                'pattern': r'\bhtml\[lang[~|^]=[^\]]+\]\s+',
                'browser': 'all',
                'description': 'Attribute selectors for language targeting'
            },
            {
                'pattern': r'-webkit-',
                'browser': 'Webkit',
                'description': 'Webkit vendor prefix'
            },
            {
                'pattern': r'-moz-',
                'browser': 'Firefox',
                'description': 'Mozilla vendor prefix'
            },
            {
                'pattern': r'-ms-',
                'browser': 'IE',
                'description': 'Microsoft vendor prefix'
            },
            {
                'pattern': r'-o-',
                'browser': 'Opera',
                'description': 'Opera vendor prefix'
            }
        ]
        
        for hack in hack_patterns:
            matches = re.findall(hack['pattern'], css_content)
            if matches:
                browser_hacks.append({
                    'browser': hack['browser'],
                    'description': hack['description'],
                    'count': len(matches),
                    'examples': matches[:3]  # Show at most 3 examples
                })
        
        return browser_hacks
    
    def _find_unused_selectors(self, css_content: str, html_content: str) -> List[str]:
        """Find potentially unused CSS selectors in the context of given HTML content.
        
        Args:
            css_content: CSS content to analyze.
            html_content: HTML content to check against.
            
        Returns:
            List of potentially unused selectors.
        """
        # Extract all selectors
        clean_css = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        selector_blocks = re.findall(r'([^{]+){[^}]*}', clean_css)
        
        all_selectors = []
        for block in selector_blocks:
            # Skip @media queries and other @ rules for selector checking
            if block.strip().startswith('@'):
                continue
                
            # Split and clean selectors
            block_selectors = [s.strip() for s in block.split(',')]
            all_selectors.extend(block_selectors)
        
        # Clean up selectors
        cleaned_selectors = []
        for selector in all_selectors:
            # Skip complex selectors that are hard to check
            if ':' in selector or '[' in selector:
                continue
                
            # Simple cleaning
            cleaned_selector = selector.replace('>', ' > ').replace('+', ' + ').replace('~', ' ~ ')
            cleaned_selectors.append(cleaned_selector.strip())
        
        # Check simple selectors (this is a very basic check and not foolproof)
        unused_selectors = []
        for selector in cleaned_selectors:
            # Extract class, ID, and tag selectors
            classes = re.findall(r'\.([\w-]+)', selector)
            ids = re.findall(r'#([\w-]+)', selector)
            
            # Check classes
            if classes:
                if not any(f'class="[^"]*{c}[^"]*"' in html_content or f"class='[^']*{c}[^']*'" in html_content for c in classes):
                    unused_selectors.append(selector)
                continue
                
            # Check IDs
            if ids:
                if not any(f'id="{i}"' in html_content or f"id='{i}'" in html_content for i in ids):
                    unused_selectors.append(selector)
                continue
        
        return unused_selectors
    
    def _analyze_colors(self, css_content: str) -> Dict[str, Any]:
        """Analyze color usage in CSS content.
        
        Args:
            css_content: CSS content to analyze.
            
        Returns:
            Dictionary with color analysis.
        """
        # Extract all color values
        color_patterns = [
            r'#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?',  # Hex colors
            r'rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)',  # RGB colors
            r'rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[0-9.]+\s*\)',  # RGBA colors
            r'hsl\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*\)',  # HSL colors
            r'hsla\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*,\s*[0-9.]+\s*\)'  # HSLA colors
        ]
        
        # Also include named colors
        common_colors = [
            'black', 'white', 'red', 'green', 'blue', 'yellow', 'orange', 'purple',
            'gray', 'grey', 'cyan', 'magenta', 'silver', 'gold', 'transparent'
        ]
        
        named_color_pattern = r'\b(?:' + '|'.join(common_colors) + r')\b'
        color_patterns.append(named_color_pattern)
        
        # Find all colors
        all_colors = []
        for pattern in color_patterns:
            colors = re.findall(pattern, css_content)
            all_colors.extend(colors)
        
        # Count unique colors
        unique_colors = set(all_colors)
        
        return {
            'total_colors': len(all_colors),
            'unique_colors': len(unique_colors),
            'color_formats': {
                'hex': len(re.findall(r'#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?', css_content)),
                'rgb': len(re.findall(r'rgb\(', css_content)),
                'rgba': len(re.findall(r'rgba\(', css_content)),
                'hsl': len(re.findall(r'hsl\(', css_content)),
                'hsla': len(re.findall(r'hsla\(', css_content)),
                'named': len(re.findall(named_color_pattern, css_content))
            },
            'most_common': self._get_most_common(all_colors, 5)
        }
    
    def _detect_duplicates(self, css_content: str) -> Dict[str, Any]:
        """Detect duplicate rules in CSS content.
        
        Args:
            css_content: CSS content to analyze.
            
        Returns:
            Dictionary with duplicate rule analysis.
        """
        # Extract all CSS rules
        clean_css = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        rule_blocks = re.findall(r'([^{]+){([^}]*)}', clean_css)
        
        # Process rule blocks
        rules = {}
        properties = {}
        
        for selector, declaration in rule_blocks:
            selector = selector.strip()
            
            # Skip @media queries and other @ rules
            if selector.startswith('@'):
                continue
            
            # Extract properties from declaration
            declaration_props = declaration.strip().split(';')
            declaration_props = [p.strip() for p in declaration_props if p.strip()]
            
            # Check for duplicate selectors
            if selector in rules:
                rules[selector].append(declaration_props)
            else:
                rules[selector] = [declaration_props]
            
            # Check for duplicate properties
            for prop in declaration_props:
                if ':' not in prop:
                    continue
                
                prop_name, prop_value = prop.split(':', 1)
                prop_name = prop_name.strip()
                prop_value = prop_value.strip()
                
                if prop_name in properties:
                    properties[prop_name].append(prop_value)
                else:
                    properties[prop_name] = [prop_value]
        
        # Find duplicate selectors
        duplicate_selectors = {selector: rule_list for selector, rule_list in rules.items() if len(rule_list) > 1}
        
        # Find properties with multiple values
        property_variations = {
            prop: list(set(values)) 
            for prop, values in properties.items() 
            if len(set(values)) > 1
        }
        
        return {
            'duplicate_selectors': len(duplicate_selectors),
            'duplicate_selector_examples': list(duplicate_selectors.keys())[:5],
            'property_variations': len(property_variations),
            'property_variation_examples': {
                k: v for k, v in list(property_variations.items())[:5]
            }
        }
    
    def _create_histogram(self, values: List[float], buckets: int) -> Dict[str, int]:
        """Create a histogram from a list of values.
        
        Args:
            values: List of numerical values.
            buckets: Number of buckets to divide the range into.
            
        Returns:
            Dictionary with bucket ranges and counts.
        """
        if not values:
            return {}
        
        min_val = min(values)
        max_val = max(values)
        
        if min_val == max_val:
            return {f"{min_val}": len(values)}
        
        # Create buckets
        bucket_size = (max_val - min_val) / buckets
        histogram = {}
        
        for i in range(buckets):
            lower = min_val + i * bucket_size
            upper = min_val + (i + 1) * bucket_size
            
            # Create bucket label
            if i == buckets - 1:
                label = f"{lower:.1f}-{upper:.1f}"
            else:
                label = f"{lower:.1f}-{upper:.1f}"
            
            # Count values in this bucket
            count = sum(1 for v in values if lower <= v < upper or (i == buckets - 1 and v == upper))
            histogram[label] = count
        
        return histogram
    
    def _get_most_common(self, items: List[str], limit: int) -> List[Dict[str, Any]]:
        """Get the most common items in a list.
        
        Args:
            items: List of items.
            limit: Maximum number of common items to return.
            
        Returns:
            List of dictionaries with item and count.
        """
        if not items:
            return []
        
        # Count occurrences
        counts = {}
        for item in items:
            counts[item] = counts.get(item, 0) + 1
        
        # Sort by count and get top items
        top_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [{'value': item, 'count': count} for item, count in top_items] 