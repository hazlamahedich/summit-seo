"""Title analyzer implementation."""

from typing import Dict, Any, Optional, List, Set, Tuple
from bs4 import BeautifulSoup
import re
from collections import Counter

from .base import BaseAnalyzer, AnalysisResult, InputType, OutputType

class TitleAnalyzer(BaseAnalyzer[str, Dict[str, Any]]):
    """Analyzer for webpage titles.
    
    This analyzer examines the title tag content and provides analysis based on
    SEO best practices, including length, keyword presence, and formatting.
    """

    # Common stop words that add little SEO value
    STOP_WORDS = {
        'a', 'an', 'the', 'and', 'or', 'but', 'if', 'then', 'else', 'when',
        'at', 'from', 'by', 'for', 'with', 'about', 'to', 'in', 'on', 'of',
        'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'this', 'that', 'these', 'those', 'it', 'its',
    }
    
    # Power words that can increase CTR
    POWER_WORDS = {
        'best', 'free', 'new', 'now', 'how', 'why', 'top', 'guide',
        'review', 'ultimate', 'essential', 'complete', 'proven', 'easy',
        'quick', 'fast', 'simple', 'effective', 'powerful', 'amazing',
        'incredible', 'guaranteed', 'exclusive', 'secret', 'awesome',
        'stunning', 'remarkable', 'extraordinary', 'sensational'
    }
    
    # Common title separators
    SEPARATORS = {'-', '|', '—', ':', '•', '»', '·'}

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the title analyzer.
        
        Args:
            config: Optional configuration dictionary that may include:
                - min_length: Minimum title length (default: 30)
                - max_length: Maximum title length (default: 60)
                - keyword_weight: Weight for keyword presence (default: 0.3)
                - format_weight: Weight for format issues (default: 0.2)
                - brand_name: Brand name to check for (default: None)
                - target_keywords: List of target keywords to check for (default: [])
                - max_stop_words: Maximum recommended stop words (default: 4)
                - stop_words: Additional stop words to check
                - power_words: Additional power words to check
                - ideal_keyword_position: Ideal position for primary keyword (default: 'beginning')
                - check_competitors: Whether to include competitor suggestions (default: False)
        """
        super().__init__(config)
        self.min_length = self.config.get('min_length', 30)
        self.max_length = self.config.get('max_length', 60)
        self.keyword_weight = self.config.get('keyword_weight', 0.3)
        self.format_weight = self.config.get('format_weight', 0.2)
        self.brand_name = self.config.get('brand_name', None)
        self.target_keywords = self.config.get('target_keywords', [])
        self.max_stop_words = self.config.get('max_stop_words', 4)
        self.ideal_keyword_position = self.config.get('ideal_keyword_position', 'beginning')
        self.check_competitors = self.config.get('check_competitors', False)
        
        # Extend default stop words and power words with custom ones
        if 'stop_words' in self.config:
            self.STOP_WORDS.update(self.config['stop_words'])
        if 'power_words' in self.config:
            self.POWER_WORDS.update(self.config['power_words'])

    def analyze(self, html_content: str) -> AnalysisResult[Dict[str, Any]]:
        """Analyze the webpage title from HTML content.
        
        Args:
            html_content: HTML content containing the title tag
            
        Returns:
            AnalysisResult containing title analysis data
            
        Raises:
            AnalyzerError: If analysis fails
        """
        self.validate_input(html_content)
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            title_tag = soup.title
            title_text = title_tag.string.strip() if title_tag else ""
            
            # Analyze the title
            issues = []
            warnings = []
            suggestions = []
            
            # Check title presence
            if not title_text:
                issues.append("Page title is missing")
                return AnalysisResult(
                    data={
                        'title': None,
                        'length': 0,
                        'has_title': False
                    },
                    metadata=self.create_metadata('title'),
                    score=0.0,
                    issues=issues,
                    warnings=warnings,
                    suggestions=["Add a descriptive page title"]
                )
            
            # Initialize analysis components
            analysis_data = {
                'title': title_text,
                'length': len(title_text),
                'has_title': True,
            }
            
            # Perform basic length analysis
            length_analysis = self._analyze_length(title_text)
            issues.extend(length_analysis['issues'])
            warnings.extend(length_analysis['warnings'])
            suggestions.extend(length_analysis['suggestions'])
            analysis_data.update(length_analysis['data'])
            
            # Perform format analysis
            format_analysis = self._analyze_format(title_text)
            issues.extend(format_analysis['issues'])
            warnings.extend(format_analysis['warnings'])
            suggestions.extend(format_analysis['suggestions'])
            analysis_data.update(format_analysis['data'])
            
            # Perform keyword analysis if target keywords are provided
            if self.target_keywords:
                keyword_analysis = self._analyze_keywords(title_text)
                issues.extend(keyword_analysis['issues'])
                warnings.extend(keyword_analysis['warnings'])
                suggestions.extend(keyword_analysis['suggestions'])
                analysis_data.update(keyword_analysis['data'])
            
            # Perform brand analysis if brand name is provided
            if self.brand_name:
                brand_analysis = self._analyze_brand(title_text)
                issues.extend(brand_analysis['issues'])
                warnings.extend(brand_analysis['warnings'])
                suggestions.extend(brand_analysis['suggestions'])
                analysis_data.update(brand_analysis['data'])
            
            # Analyze stop words
            stop_word_analysis = self._analyze_stop_words(title_text)
            issues.extend(stop_word_analysis['issues'])
            warnings.extend(stop_word_analysis['warnings'])
            suggestions.extend(stop_word_analysis['suggestions'])
            analysis_data.update(stop_word_analysis['data'])
            
            # Analyze power words
            power_word_analysis = self._analyze_power_words(title_text)
            issues.extend(power_word_analysis['issues'])
            warnings.extend(power_word_analysis['warnings'])
            suggestions.extend(power_word_analysis['suggestions'])
            analysis_data.update(power_word_analysis['data'])
            
            # Add SERP preview
            analysis_data['serp_preview'] = self._generate_serp_preview(title_text)
            
            # Calculate score
            score = self.calculate_score(issues, warnings, analysis_data)
            
            return AnalysisResult(
                data=analysis_data,
                metadata=self.create_metadata('title'),
                score=score,
                issues=issues,
                warnings=warnings,
                suggestions=suggestions
            )
            
        except Exception as e:
            raise self.error_type(f"Failed to analyze title: {str(e)}")
    
    def _analyze_length(self, title_text: str) -> Dict[str, Any]:
        """Analyze the length of the title.
        
        Args:
            title_text: The title text to analyze
            
        Returns:
            Dictionary with analysis results
        """
        length = len(title_text)
        issues = []
        warnings = []
        suggestions = []
        
        # Check title length
        if length < self.min_length:
            warnings.append(
                f"Title length ({length} chars) is below recommended minimum "
                f"of {self.min_length} characters"
            )
            suggestions.append(
                "Make the title more descriptive to reach at least "
                f"{self.min_length} characters"
            )
        elif length > self.max_length:
            warnings.append(
                f"Title length ({length} chars) exceeds recommended maximum "
                f"of {self.max_length} characters"
            )
            suggestions.append(
                "Shorten the title to be under "
                f"{self.max_length} characters"
            )
            
        # Google typically displays 50-60 characters of a title
        truncated = length > 60
        if truncated:
            warnings.append(
                "Title may be truncated in search results"
            )
        
        return {
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'length': length,
                'is_optimal_length': self.min_length <= length <= self.max_length,
                'is_likely_truncated': truncated,
                'visible_character_count': min(length, 60)
            }
        }
    
    def _analyze_format(self, title_text: str) -> Dict[str, Any]:
        """Analyze the formatting of the title.
        
        Args:
            title_text: The title text to analyze
            
        Returns:
            Dictionary with analysis results
        """
        issues = []
        warnings = []
        suggestions = []
        format_issues = []
        
        # Check title casing
        if title_text.isupper():
            warnings.append("Title is in all uppercase")
            suggestions.append(
                "Use title case or sentence case instead of all uppercase"
            )
            format_issues.append("all_uppercase")
        
        # Check for separators and segments
        separators = [sep for sep in self.SEPARATORS if sep in title_text]
        has_separators = bool(separators)
        
        segments = []
        if has_separators:
            # Replace all separators with a standard one for analysis
            temp_text = title_text
            for sep in separators:
                temp_text = temp_text.replace(sep, '|')
            segments = [s.strip() for s in temp_text.split('|')]
            
            # Check for very short segments
            if any(len(segment) < 3 for segment in segments):
                warnings.append("Title contains very short segments")
                suggestions.append(
                    "Ensure all title segments are meaningful"
                )
                format_issues.append("short_segments")
        else:
            segments = [title_text]
        
        # Check for common formatting issues
        if any(title_text.endswith(f" {sep}") for sep in self.SEPARATORS):
            warnings.append("Title ends with a separator")
            suggestions.append("Remove trailing separator from title")
            format_issues.append("trailing_separator")
        
        if any(title_text.startswith(f"{sep} ") for sep in self.SEPARATORS):
            warnings.append("Title starts with a separator")
            suggestions.append("Remove leading separator from title")
            format_issues.append("leading_separator")
        
        # Check for duplicate words
        words = [word.lower() for word in re.findall(r'\b\w+\b', title_text)]
        word_counts = Counter(words)
        duplicates = [word for word, count in word_counts.items() 
                     if count > 1 and word not in self.STOP_WORDS]
        
        if duplicates:
            warnings.append(f"Title contains duplicate words: {', '.join(duplicates)}")
            suggestions.append("Remove unnecessary word repetition")
            format_issues.append("duplicate_words")
        
        return {
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'format_issues': format_issues,
                'segments': segments,
                'separators_used': separators,
                'has_separators': has_separators,
                'duplicate_words': duplicates
            }
        }
    
    def _analyze_keywords(self, title_text: str) -> Dict[str, Any]:
        """Analyze keyword usage in the title.
        
        Args:
            title_text: The title text to analyze
            
        Returns:
            Dictionary with analysis results
        """
        issues = []
        warnings = []
        suggestions = []
        
        title_lower = title_text.lower()
        words = [word.lower() for word in re.findall(r'\b\w+\b', title_lower)]
        
        # Track which keywords are present and their positions
        found_keywords = []
        keyword_positions = {}
        first_keyword = None
        
        for keyword in self.target_keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in title_lower:
                found_keywords.append(keyword)
                
                # Find position of keyword (beginning, middle, end)
                position_index = title_lower.find(keyword_lower)
                title_third = len(title_text) / 3
                
                if position_index < title_third:
                    position = "beginning"
                elif position_index < title_third * 2:
                    position = "middle"
                else:
                    position = "end"
                
                keyword_positions[keyword] = {
                    "position": position,
                    "index": position_index
                }
                
                if first_keyword is None:
                    first_keyword = keyword
        
        # Analyze keyword findings
        if not found_keywords:
            warnings.append("No target keywords found in title")
            suggestions.append(
                f"Include target keywords in title: {', '.join(self.target_keywords[:3])}"
            )
        else:
            # Check if primary keyword is in the ideal position
            if first_keyword and self.ideal_keyword_position != "any":
                actual_position = keyword_positions[first_keyword]["position"]
                if actual_position != self.ideal_keyword_position:
                    warnings.append(
                        f"Primary keyword '{first_keyword}' is not in the "
                        f"ideal position (found at {actual_position}, "
                        f"ideal is {self.ideal_keyword_position})"
                    )
                    suggestions.append(
                        f"Move primary keyword '{first_keyword}' to the "
                        f"{self.ideal_keyword_position} of the title"
                    )
        
        # Calculate keyword density
        keyword_density = len(found_keywords) / len(words) if words else 0
        
        # Check for keyword stuffing
        if keyword_density > 0.3:  # More than 30% of words are keywords
            warnings.append("Possible keyword stuffing detected")
            suggestions.append(
                "Reduce keyword density for more natural phrasing"
            )
        
        return {
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'target_keywords': self.target_keywords,
                'found_keywords': found_keywords,
                'keyword_positions': keyword_positions,
                'keyword_density': keyword_density,
                'first_keyword': first_keyword
            }
        }
    
    def _analyze_brand(self, title_text: str) -> Dict[str, Any]:
        """Analyze brand presence in the title.
        
        Args:
            title_text: The title text to analyze
            
        Returns:
            Dictionary with analysis results
        """
        issues = []
        warnings = []
        suggestions = []
        
        title_lower = title_text.lower()
        brand_lower = self.brand_name.lower()
        
        # Check if brand is present
        brand_present = brand_lower in title_lower
        
        # Check brand position
        brand_position = None
        if brand_present:
            position_index = title_lower.find(brand_lower)
            title_third = len(title_text) / 3
            
            if position_index < title_third:
                brand_position = "beginning"
            elif position_index < title_third * 2:
                brand_position = "middle"
            else:
                brand_position = "end"
        
        # Best practice often suggests brand at the end
        if not brand_present:
            suggestions.append(f"Consider adding your brand name '{self.brand_name}' to the title")
        elif brand_position != "end":
            suggestions.append(
                f"Consider moving your brand name to the end of the title "
                f"for better keyword prominence"
            )
        
        return {
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'brand_name': self.brand_name,
                'brand_present': brand_present,
                'brand_position': brand_position
            }
        }
    
    def _analyze_stop_words(self, title_text: str) -> Dict[str, Any]:
        """Analyze stop word usage in the title.
        
        Args:
            title_text: The title text to analyze
            
        Returns:
            Dictionary with analysis results
        """
        issues = []
        warnings = []
        suggestions = []
        
        # Find stop words in title
        words = [word.lower() for word in re.findall(r'\b\w+\b', title_text.lower())]
        stop_words_found = [word for word in words if word in self.STOP_WORDS]
        stop_word_count = len(stop_words_found)
        
        # Check if too many stop words
        if stop_word_count > self.max_stop_words:
            warnings.append(
                f"Title contains {stop_word_count} stop words, "
                f"which is more than the recommended maximum of {self.max_stop_words}"
            )
            suggestions.append(
                f"Reduce the number of stop words (e.g., {', '.join(stop_words_found[:3])})"
            )
        
        return {
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'stop_words_found': stop_words_found,
                'stop_word_count': stop_word_count,
                'stop_word_ratio': stop_word_count / len(words) if words else 0
            }
        }
    
    def _analyze_power_words(self, title_text: str) -> Dict[str, Any]:
        """Analyze power word usage in the title.
        
        Args:
            title_text: The title text to analyze
            
        Returns:
            Dictionary with analysis results
        """
        issues = []
        warnings = []
        suggestions = []
        
        # Find power words in title
        words = [word.lower() for word in re.findall(r'\b\w+\b', title_text.lower())]
        power_words_found = [word for word in words if word in self.POWER_WORDS]
        
        # Suggest power words if none found
        if not power_words_found:
            suggestions.append(
                f"Consider adding power words to increase CTR "
                f"(e.g., {', '.join(list(self.POWER_WORDS)[:5])})"
            )
        
        return {
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'power_words_found': power_words_found,
                'power_word_count': len(power_words_found),
                'power_word_ratio': len(power_words_found) / len(words) if words else 0
            }
        }
    
    def _generate_serp_preview(self, title_text: str) -> Dict[str, Any]:
        """Generate a SERP preview for the title.
        
        Args:
            title_text: The title text to analyze
            
        Returns:
            Dictionary with preview information
        """
        display_title = title_text
        is_truncated = False
        
        # Google typically shows about 60 characters
        if len(title_text) > 60:
            display_title = title_text[:57] + "..."
            is_truncated = True
        
        return {
            'display_title': display_title,
            'is_truncated': is_truncated,
            'pixel_width_estimate': len(title_text) * 8  # Rough pixel estimate
        }
    
    def calculate_score(self, issues: List[str], warnings: List[str], 
                      analysis_data: Dict[str, Any] = None) -> float:
        """Calculate the overall score for the title.
        
        Args:
            issues: List of critical issues
            warnings: List of warnings
            analysis_data: Additional analysis data for score calculation
            
        Returns:
            Score from 0.0 to 1.0
        """
        # Start with base score
        score = 1.0
        
        # Deduct for issues and warnings
        score -= len(issues) * 0.2  # Deduct 20% per critical issue
        score -= len(warnings) * 0.05  # Deduct 5% per warning
        
        # If we have analysis data, use it for more nuanced scoring
        if analysis_data:
            # Length optimality
            if not analysis_data.get('is_optimal_length', True):
                score -= 0.1
            
            # Keyword presence
            if 'found_keywords' in analysis_data:
                if not analysis_data['found_keywords']:
                    score -= 0.15  # Major penalty for no keywords
                else:
                    # Bonus for good keyword position
                    if (analysis_data.get('first_keyword') and 
                        'keyword_positions' in analysis_data and
                        analysis_data['keyword_positions'].get(analysis_data['first_keyword'], {}).get('position') == 
                        self.ideal_keyword_position):
                        score += 0.05
            
            # Brand presence
            if 'brand_present' in analysis_data and not analysis_data['brand_present']:
                score -= 0.05
            
            # Power words bonus
            power_word_count = analysis_data.get('power_word_count', 0)
            if power_word_count > 0:
                score += min(0.05, power_word_count * 0.01)  # Up to 5% bonus
        
        # Ensure score is within bounds
        return max(0.0, min(1.0, score))

    def format_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Format an analysis message with title-specific context.
        
        Args:
            message: Base message to format
            context: Optional context dictionary for message formatting
            
        Returns:
            Formatted message string
        """
        title_context = {
            'min_length': self.min_length,
            'max_length': self.max_length,
            **(context or {})
        }
        return super().format_message(message, title_context) 