"""Content analyzer implementation."""

from typing import Dict, Any, Optional, List, Tuple, Set
from bs4 import BeautifulSoup
import re
from collections import Counter
import math
import json

from .base import BaseAnalyzer, AnalysisResult

class ContentAnalyzer(BaseAnalyzer[str, Dict[str, Any]]):
    """Analyzer for webpage content.
    
    This analyzer examines the main content of a webpage and provides analysis based on
    SEO best practices, including content length, readability, keyword density,
    structure, and overall quality metrics.
    """

    # Common stop words to exclude from analysis
    STOP_WORDS = {
        'a', 'an', 'the', 'and', 'or', 'but', 'if', 'then', 'else', 'when',
        'at', 'from', 'by', 'for', 'with', 'about', 'to', 'in', 'on', 'of',
        'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall',
        'should', 'can', 'could', 'may', 'might', 'must', 'this', 'that',
        'these', 'those', 'there', 'here', 'where', 'when', 'why', 'how',
        'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
        'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
        'very', 'just', 'it', 'its'
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the content analyzer.
        
        Args:
            config: Optional configuration dictionary that may include:
                - min_word_count: Minimum word count (default: 300)
                - optimal_word_count: Optimal word count (default: 1000)
                - max_keyword_density: Maximum keyword density % (default: 2.5)
                - min_keyword_density: Minimum keyword density % (default: 0.5)
                - readability_weight: Weight for readability score (default: 0.3)
                - structure_weight: Weight for content structure (default: 0.3)
                - keyword_weight: Weight for keyword optimization (default: 0.4)
                - target_keywords: List of target keywords to check for
                - competitor_keywords: List of competitor keywords to compare against
                - stop_words: Additional stop words to exclude
        """
        super().__init__(config)
        self.min_word_count = self.config.get('min_word_count', 300)
        self.optimal_word_count = self.config.get('optimal_word_count', 1000)
        self.max_keyword_density = self.config.get('max_keyword_density', 2.5)
        self.min_keyword_density = self.config.get('min_keyword_density', 0.5)
        self.readability_weight = self.config.get('readability_weight', 0.3)
        self.structure_weight = self.config.get('structure_weight', 0.3)
        self.keyword_weight = self.config.get('keyword_weight', 0.4)
        self.target_keywords = self.config.get('target_keywords', [])
        self.competitor_keywords = self.config.get('competitor_keywords', [])
        
        # Extend default stop words with custom ones
        self.stop_words = self.STOP_WORDS.copy()
        if 'stop_words' in self.config:
            self.stop_words.update(self.config['stop_words'])

    def analyze(self, html_content: str) -> AnalysisResult[Dict[str, Any]]:
        """Analyze the webpage content from HTML content.
        
        Args:
            html_content: HTML content to analyze
            
        Returns:
            AnalysisResult containing content analysis data
            
        Raises:
            AnalyzerError: If analysis fails
        """
        self.validate_input(html_content)
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            original_soup = BeautifulSoup(html_content, 'html.parser')  # Keep an unmodified copy
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()
            
            # Get main content
            content = soup.get_text()
            
            # Initialize analysis components
            issues: List[str] = []
            warnings: List[str] = []
            suggestions: List[str] = []
            
            # Basic content analysis
            paragraphs = self._extract_paragraphs(soup)
            words = self._extract_words(content)
            sentences = self._extract_sentences(content)
            
            if not words:
                issues.append("No meaningful content found")
                return AnalysisResult(
                    data={
                        'word_count': 0,
                        'has_content': False
                    },
                    metadata=self.create_metadata('content'),
                    score=0.0,
                    issues=issues,
                    warnings=warnings,
                    suggestions=["Add meaningful content to the page"]
                )
            
            # Analyze content length
            word_count = len(words)
            if word_count < self.min_word_count:
                warnings.append(
                    f"Content length ({word_count} words) is below recommended minimum "
                    f"of {self.min_word_count} words"
                )
                suggestions.append(
                    "Add more detailed content to reach at least "
                    f"{self.min_word_count} words"
                )
            
            # Analyze readability
            readability_score = self._calculate_readability(sentences, words)
            readability_analysis = self._analyze_readability(readability_score)
            warnings.extend(readability_analysis['warnings'])
            suggestions.extend(readability_analysis['suggestions'])
            
            # Analyze keyword usage
            keyword_analysis = self._analyze_keywords(words, content)
            issues.extend(keyword_analysis['issues'])
            warnings.extend(keyword_analysis['warnings'])
            suggestions.extend(keyword_analysis['suggestions'])
            
            # Analyze content structure
            structure_issues = self._analyze_structure(soup)
            issues.extend(structure_issues)
            
            # Analyze images
            image_analysis = self._gather_image_data(soup)
            
            # Analyze internal links
            link_analysis = self._gather_link_data(soup)
            
            # Analyze content-to-code ratio
            code_ratio_analysis = self._analyze_content_to_code_ratio(html_content, content)
            warnings.extend(code_ratio_analysis['warnings'])
            suggestions.extend(code_ratio_analysis['suggestions'])
            
            # Analyze schema.org structured data
            schema_analysis = self._analyze_structured_data(original_soup)
            warnings.extend(schema_analysis['warnings'])
            suggestions.extend(schema_analysis['suggestions'])
            
            # Analyze content freshness
            freshness_analysis = self._analyze_content_freshness(original_soup, content)
            warnings.extend(freshness_analysis['warnings'])
            suggestions.extend(freshness_analysis['suggestions'])
            
            # Analyze accessibility compliance
            accessibility_analysis = self._analyze_accessibility(original_soup)
            issues.extend(accessibility_analysis['issues'])
            warnings.extend(accessibility_analysis['warnings'])
            suggestions.extend(accessibility_analysis['suggestions'])
            
            # Analyze content quality
            quality_analysis = self._analyze_content_quality(soup, words, sentences)
            warnings.extend(quality_analysis['warnings'])
            suggestions.extend(quality_analysis['suggestions'])
            
            # Analyze mobile-friendliness
            mobile_analysis = self._analyze_mobile_friendliness(soup)
            warnings.extend(mobile_analysis['warnings'])
            suggestions.extend(mobile_analysis['suggestions'])
            
            # Analyze paragraph length
            long_paragraphs = [p for p in paragraphs if len(p.split()) > 150]
            if long_paragraphs:
                warnings.append(
                    f"Found {len(long_paragraphs)} paragraphs that are too long"
                )
                suggestions.append(
                    "Break up long paragraphs to improve readability"
                )
            
            # Calculate overall score
            score = self.calculate_score(issues, warnings, {
                'readability_score': readability_score,
                'keyword_analysis': keyword_analysis['data'],
                'word_count': word_count,
                'image_analysis': image_analysis,
                'link_analysis': link_analysis,
                'quality_analysis': quality_analysis['data'],
                'mobile_analysis': mobile_analysis['data'],
                'code_ratio': code_ratio_analysis['data'],
                'schema_analysis': schema_analysis['data'],
                'accessibility_analysis': accessibility_analysis['data'],
                'freshness_analysis': freshness_analysis['data']
            })
            
            # Prepare analysis data
            analysis_data = {
                'word_count': word_count,
                'has_content': True,
                'sentence_count': len(sentences),
                'paragraph_count': len(paragraphs),
                'avg_words_per_sentence': word_count / len(sentences) if sentences else 0,
                'avg_words_per_paragraph': word_count / len(paragraphs) if paragraphs else 0,
                'readability': {
                    'score': readability_score,
                    'grade_level': readability_analysis['data']['grade_level'],
                    'complexity': readability_analysis['data']['complexity']
                },
                'keyword_analysis': keyword_analysis['data'],
                'structure_analysis': {
                    'headings': self._count_headings(soup),
                    'lists': len(soup.find_all(['ul', 'ol'])),
                    'images': image_analysis,
                    'links': link_analysis
                },
                'content_quality': quality_analysis['data'],
                'mobile_friendliness': mobile_analysis['data'],
                'content_to_code_ratio': code_ratio_analysis['data'],
                'structured_data': schema_analysis['data'],
                'accessibility': accessibility_analysis['data'],
                'content_freshness': freshness_analysis['data']
            }
            
            return AnalysisResult(
                data=analysis_data,
                metadata=self.create_metadata('content'),
                score=score,
                issues=issues,
                warnings=warnings,
                suggestions=suggestions
            )
            
        except Exception as e:
            raise self.error_type(f"Failed to analyze content: {str(e)}")

    def _extract_paragraphs(self, soup: BeautifulSoup) -> List[str]:
        """Extract paragraphs from the HTML content."""
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if text:  # Only include non-empty paragraphs
                paragraphs.append(text)
        return paragraphs

    def _extract_words(self, text: str) -> List[str]:
        """Extract words from text, filtering out common stop words."""
        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if w not in self.stop_words and len(w) > 1]

    def _extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text."""
        # More sophisticated sentence splitting
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
        return [s.strip() for s in sentences if s.strip()]

    def _calculate_readability(self, sentences: List[str], words: List[str]) -> float:
        """Calculate readability score using Flesch-Kincaid formula."""
        if not sentences or not words:
            return 0.0
        
        total_words = len(words)
        total_sentences = len(sentences)
        total_syllables = sum(self._count_syllables(word) for word in words)
        
        # Flesch-Kincaid Grade Level formula
        score = (0.39 * (total_words / total_sentences)) + \
                (11.8 * (total_syllables / total_words)) - 15.59
        
        return round(score, 2)

    def _analyze_readability(self, score: float) -> Dict[str, Any]:
        """Analyze readability score and provide recommendations."""
        warnings = []
        suggestions = []
        
        # Determine grade level and complexity
        if score <= 6:
            grade_level = "Elementary"
            complexity = "Very Easy"
        elif score <= 8:
            grade_level = "Middle School"
            complexity = "Easy"
        elif score <= 12:
            grade_level = "High School"
            complexity = "Moderate"
        elif score <= 16:
            grade_level = "College"
            complexity = "Difficult"
        else:
            grade_level = "Graduate"
            complexity = "Very Difficult"
            
        # Provide warnings and suggestions based on complexity
        if score > 12:
            warnings.append(
                f"Content readability score ({score:.1f}) indicates {complexity} reading level"
            )
            suggestions.append(
                "Simplify language and use shorter sentences to improve readability"
            )
        elif score < 6:
            warnings.append(
                f"Content may be too simplistic (readability score: {score:.1f})"
            )
            suggestions.append(
                "Consider adding more sophisticated content while maintaining clarity"
            )
            
        return {
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'grade_level': grade_level,
                'complexity': complexity
            }
        }

    def _count_syllables(self, word: str) -> int:
        """Count the number of syllables in a word."""
        word = word.lower()
        count = 0
        vowels = 'aeiouy'
        on_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not on_vowel:
                count += 1
            on_vowel = is_vowel
        
        if word.endswith('e'):
            count -= 1
        if word.endswith('le') and len(word) > 2:
            count += 1
        if count == 0:
            count = 1
            
        return count

    def _analyze_keywords(self, words: List[str], content: str) -> Dict[str, Any]:
        """Analyze keyword usage in content."""
        issues = []
        warnings = []
        suggestions = []
        
        # Calculate keyword density for all words
        word_freq = Counter(words)
        total_words = len(words)
        
        # Get all keywords that appear more than once and are longer than 3 characters
        all_keywords = {
            word: {
                'count': count,
                'density': round((count / total_words) * 100, 2)
            }
            for word, count in word_freq.items()
            if count > 1 and len(word) > 3
        }
        
        # Check for keyword stuffing (excessive density)
        stuffed_keywords = {
            word: data['density']
            for word, data in all_keywords.items()
            if data['density'] > self.max_keyword_density
        }
        
        for keyword, density in stuffed_keywords.items():
            warnings.append(
                f"Keyword '{keyword}' appears too frequently "
                f"(density: {density:.1f}%)"
            )
            suggestions.append(
                f"Reduce the frequency of '{keyword}' to avoid keyword stuffing"
            )
            
        # Identify phrases (2-3 word combinations)
        text = ' '.join(words)
        phrases = self._extract_phrases(text)
        
        # Target keyword analysis
        if self.target_keywords:
            target_keyword_analysis = self._analyze_target_keywords(
                content, words, phrases
            )
            warnings.extend(target_keyword_analysis['warnings'])
            suggestions.extend(target_keyword_analysis['suggestions'])
            
            # Add target keyword data to the analysis
            target_keywords_data = target_keyword_analysis['data']
        else:
            target_keywords_data = None
            
        # Content gap analysis
        if self.competitor_keywords and self.target_keywords:
            gap_analysis = self._analyze_content_gaps(words, phrases)
            warnings.extend(gap_analysis['warnings'])
            suggestions.extend(gap_analysis['suggestions'])
            
            # Add gap analysis data
            gap_data = gap_analysis['data']
        else:
            gap_data = None
            
        # Extract top keywords and phrases for recommendations
        top_keywords = sorted(
            all_keywords.items(), 
            key=lambda x: x[1]['count'], 
            reverse=True
        )[:10]
        
        top_phrases = sorted(
            phrases.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        return {
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'keyword_density': {k: v['density'] for k, v in all_keywords.items()},
                'stuffed_keywords': stuffed_keywords,
                'top_keywords': [k for k, _ in top_keywords],
                'top_phrases': [p for p, _ in top_phrases],
                'target_keywords': target_keywords_data,
                'content_gaps': gap_data
            }
        }
        
    def _extract_phrases(self, text: str) -> Dict[str, int]:
        """Extract common phrases (2-3 word combinations) from text."""
        words = text.lower().split()
        if len(words) < 2:
            return {}
            
        # Extract 2-word phrases
        bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
        
        # Extract 3-word phrases
        trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
        
        # Count occurrences
        phrases = Counter(bigrams + trigrams)
        
        # Filter out phrases containing only stop words
        filtered_phrases = {}
        for phrase, count in phrases.items():
            if count < 2:
                continue
                
            phrase_words = phrase.split()
            if all(word in self.stop_words for word in phrase_words):
                continue
                
            filtered_phrases[phrase] = count
            
        return filtered_phrases
        
    def _analyze_target_keywords(
        self, content: str, words: List[str], phrases: Dict[str, int]
    ) -> Dict[str, Any]:
        """Analyze target keywords in content."""
        warnings = []
        suggestions = []
        
        content_lower = content.lower()
        total_words = len(words)
        
        # Check each target keyword
        keyword_data = {}
        missing_keywords = []
        low_density_keywords = []
        
        for keyword in self.target_keywords:
            keyword_lower = keyword.lower()
            
            # Check if keyword is present
            is_present = keyword_lower in content_lower
            count = content_lower.count(keyword_lower)
            
            # Calculate density
            density = round((count / total_words) * 100, 2) if count > 0 else 0
            
            # Check placement in content
            in_first_paragraph = False
            in_headings = False
            in_title = False
            
            # Store data for this keyword
            keyword_data[keyword] = {
                'present': is_present,
                'count': count,
                'density': density,
                'in_first_paragraph': in_first_paragraph,
                'in_headings': in_headings,
                'in_title': in_title
            }
            
            # Add to missing keywords if not present
            if not is_present:
                missing_keywords.append(keyword)
            # Check if density is too low
            elif density < self.min_keyword_density and keyword not in phrases:
                low_density_keywords.append(keyword)
                
        # Generate warnings and suggestions
        if missing_keywords:
            warnings.append(
                f"Missing target keywords: {', '.join(missing_keywords)}"
            )
            suggestions.append(
                "Add missing target keywords to improve content relevance"
            )
            
        if low_density_keywords:
            warnings.append(
                f"Low density for keywords: {', '.join(low_density_keywords)}"
            )
            suggestions.append(
                "Increase the usage of these keywords to improve content relevance"
            )
            
        return {
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'keyword_data': keyword_data,
                'missing_keywords': missing_keywords,
                'low_density_keywords': low_density_keywords
            }
        }
        
    def _analyze_content_gaps(
        self, words: List[str], phrases: Dict[str, int]
    ) -> Dict[str, Any]:
        """Analyze content gaps compared to competitor keywords."""
        warnings = []
        suggestions = []
        
        # Identify keywords present in competitor keywords but missing in content
        content_terms = set(words).union(phrases.keys())
        missing_competitor_terms = [
            term for term in self.competitor_keywords
            if term.lower() not in content_terms
        ]
        
        if missing_competitor_terms:
            warnings.append(
                f"Content gap identified: missing {len(missing_competitor_terms)} "
                "competitor keywords"
            )
            suggestions.append(
                "Consider adding these competitor keywords to cover content gaps: "
                f"{', '.join(missing_competitor_terms[:5])}"
                + ("..." if len(missing_competitor_terms) > 5 else "")
            )
            
        return {
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'missing_competitor_terms': missing_competitor_terms
            }
        }

    def _analyze_structure(self, soup: BeautifulSoup) -> List[str]:
        """Analyze content structure for SEO issues."""
        issues = []
        
        # Check heading hierarchy
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if not headings:
            issues.append("No headings found in content")
        else:
            # Check if H1 is present and unique
            h1_count = len(soup.find_all('h1'))
            if h1_count == 0:
                issues.append("No H1 heading found")
            elif h1_count > 1:
                issues.append("Multiple H1 headings found")
            
            # Check heading hierarchy
            current_level = 1
            for heading in headings:
                level = int(heading.name[1])
                if level - current_level > 1:
                    issues.append(f"Skipped heading level (H{current_level} to H{level})")
                current_level = level
        
        # Check for proper paragraph usage
        paragraphs = soup.find_all('p')
        if not paragraphs:
            issues.append("No paragraph tags found in content")
        
        # Check image optimization
        image_issues = self._analyze_images(soup)
        issues.extend(image_issues)
        
        # Check internal linking structure
        link_issues = self._analyze_internal_links(soup)
        issues.extend(link_issues)
        
        # Check content formatting
        formatting_issues = self._analyze_formatting(soup)
        issues.extend(formatting_issues)
        
        return issues
    
    def _analyze_images(self, soup: BeautifulSoup) -> List[str]:
        """Analyze images for SEO best practices."""
        issues = []
        
        images = soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]
        images_without_loading = [img for img in images if not img.get('loading')]
        
        if images_without_alt:
            issues.append(f"Found {len(images_without_alt)} images without alt text")
        
        if images_without_loading:
            issues.append(f"Found {len(images_without_loading)} images without lazy loading")
        
        return issues
    
    def _analyze_internal_links(self, soup: BeautifulSoup) -> List[str]:
        """Analyze internal links for SEO best practices."""
        issues = []
        
        links = soup.find_all('a')
        
        # Check for empty links
        empty_links = [link for link in links if not link.get('href')]
        if empty_links:
            issues.append(f"Found {len(empty_links)} links with empty href")
        
        # Check for links without text content
        links_without_text = [link for link in links if not link.get_text().strip()]
        if links_without_text:
            issues.append(f"Found {len(links_without_text)} links without text content")
        
        # Check for generic link text
        generic_link_texts = ['click here', 'read more', 'learn more', 'more info', 'more information']
        generic_links = [
            link for link in links 
            if link.get_text().strip().lower() in generic_link_texts
        ]
        if generic_links:
            issues.append(f"Found {len(generic_links)} links with generic text (e.g., 'click here')")
        
        return issues
    
    def _analyze_formatting(self, soup: BeautifulSoup) -> List[str]:
        """Analyze content formatting for SEO and readability best practices."""
        issues = []
        
        # Check for lists
        lists = soup.find_all(['ul', 'ol'])
        if not lists:
            issues.append("No list elements found - consider using lists to break up content")
        
        # Check for emphasized text
        emphasized = soup.find_all(['strong', 'em', 'b', 'i'])
        if not emphasized:
            issues.append("No emphasized text found - consider using text emphasis for important concepts")
        
        # Check for large blocks of text without breaks
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text()
            if len(text.split()) > 100:
                issues.append("Found paragraph with more than 100 words - consider breaking into smaller chunks")
                break
        
        return issues

    def _count_headings(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Count the number of each heading level."""
        return {
            f'h{i}': len(soup.find_all(f'h{i}'))
            for i in range(1, 7)
        }
    
    def calculate_score(
        self, issues: List[str], warnings: List[str], data: Dict[str, Any] = None
    ) -> float:
        """Calculate the overall score for content analysis.
        
        Args:
            issues: List of critical issues
            warnings: List of warnings
            data: Additional analysis data for score calculation
            
        Returns:
            Score from 0.0 to 1.0
        """
        # Start with base score
        score = 1.0
        
        # Deduct for issues and warnings
        score -= len(issues) * 0.2  # Deduct 20% per critical issue
        score -= len(warnings) * 0.05  # Deduct 5% per warning
        
        # Use data for more nuanced scoring if available
        if data:
            # Readability score adjustment
            if 'readability_score' in data:
                readability_score = data['readability_score']
                
                # Penalize very high (complex) or very low (simplistic) readability scores
                if readability_score > 16:
                    score -= 0.1
                elif readability_score < 5:
                    score -= 0.05
                    
            # Word count adjustment
            if 'word_count' in data:
                word_count = data['word_count']
                
                # Penalize very low word count
                if word_count < self.min_word_count:
                    score -= 0.15
                # Reward optimal word count
                elif word_count >= self.optimal_word_count:
                    score += 0.05
                    
            # Keyword analysis adjustment
            if 'keyword_analysis' in data and data['keyword_analysis'].get('target_keywords'):
                target_data = data['keyword_analysis']['target_keywords']
                
                # Penalize missing target keywords
                if 'missing_keywords' in target_data:
                    score -= min(0.2, len(target_data['missing_keywords']) * 0.05)
                    
                # Penalize low density keywords
                if 'low_density_keywords' in target_data:
                    score -= min(0.1, len(target_data['low_density_keywords']) * 0.03)
                    
            # Image optimization adjustment
            if 'image_analysis' in data:
                image_data = data['image_analysis']
                
                # Penalize missing alt text
                if image_data['count'] > 0:
                    missing_alt_ratio = image_data['without_alt_text'] / image_data['count']
                    score -= min(0.1, missing_alt_ratio * 0.2)
                    
                    # Penalize missing lazy loading
                    missing_lazy_ratio = image_data['without_lazy_loading'] / image_data['count']
                    score -= min(0.05, missing_lazy_ratio * 0.1)
                    
            # Link quality adjustment
            if 'link_analysis' in data:
                link_data = data['link_analysis']
                
                if link_data['count'] > 0:
                    # Penalize generic link text
                    generic_ratio = link_data['with_generic_text'] / link_data['count']
                    score -= min(0.1, generic_ratio * 0.2)
                    
                    # Penalize links without text
                    no_text_ratio = link_data['without_text'] / link_data['count']
                    score -= min(0.1, no_text_ratio * 0.2)
            
            # Content quality adjustment
            if 'quality_analysis' in data:
                quality_data = data['quality_analysis']
                
                # Penalize low vocabulary diversity
                if quality_data['vocabulary_diversity'] < 0.4:
                    score -= 0.1
                
                # Penalize low semantic depth
                if quality_data['semantic_depth'] < 0.3:
                    score -= 0.1
                
                # Penalize duplicate content
                if quality_data['duplicate_content_ratio'] > 0.2:
                    score -= min(0.15, quality_data['duplicate_content_ratio'] * 0.5)
                
                # Penalize thin content
                if quality_data['has_thin_content']:
                    score -= 0.1
            
            # Mobile-friendliness adjustment
            if 'mobile_analysis' in data:
                mobile_data = data['mobile_analysis']
                
                # Penalize mobile usability issues
                mobile_issues = sum([
                    mobile_data['tables_count'],
                    mobile_data['fixed_width_elements'],
                    mobile_data['small_font_elements'],
                    mobile_data['small_touch_targets']
                ])
                
                if mobile_issues > 0:
                    score -= min(0.15, mobile_issues * 0.02)
                    
            # Content-to-code ratio adjustment
            if 'code_ratio' in data:
                code_data = data['code_ratio']
                
                # Penalize very low content-to-code ratio
                if code_data['ratio'] < 0.1:
                    score -= 0.15
                elif code_data['ratio'] < 0.25:
                    score -= 0.1
                
                # Penalize excessive comments
                if code_data['comment_percentage'] > 10:
                    score -= 0.05
                
                # Penalize excessive inline scripts/styles
                if code_data['inline_scripts'] > 5 or code_data['inline_styles'] > 5:
                    score -= 0.05
                    
            # Structured data adjustment
            if 'schema_analysis' in data:
                schema_data = data['schema_analysis']
                
                # Penalize missing structured data
                if not schema_data['has_structured_data']:
                    score -= 0.1
                # Reward having structured data
                elif len(schema_data['schema_types']) > 0:
                    score += 0.05
                    
            # Accessibility adjustment
            if 'accessibility_analysis' in data:
                accessibility_data = data['accessibility_analysis']
                
                # Penalize missing language attribute
                if not accessibility_data['has_lang_attribute']:
                    score -= 0.05
                
                # Penalize missing alt text
                if accessibility_data['images_without_alt'] > 0:
                    score -= min(0.1, accessibility_data['images_without_alt'] * 0.02)
                
                # Penalize missing form labels
                if accessibility_data['inputs_without_labels']:
                    score -= 0.1
                
                # Penalize empty interactive elements
                if accessibility_data['has_empty_interactive']:
                    score -= 0.1
                    
            # Content freshness adjustment
            if 'freshness_analysis' in data:
                freshness_data = data['freshness_analysis']
                
                # Penalize missing dates
                if not freshness_data['has_publication_date'] and not freshness_data['has_date_indicators']:
                    score -= 0.1
                
                # Penalize outdated content
                if freshness_data['has_outdated_content']:
                    score -= 0.15
                
                # Penalize old content
                if freshness_data['content_age_days']:
                    if freshness_data['content_age_days'] > 730:  # 2+ years
                        score -= 0.15
                    elif freshness_data['content_age_days'] > 365:  # 1+ year
                        score -= 0.05
                
                # Extra penalty for outdated seasonal content
                if freshness_data['is_seasonal_content'] and freshness_data['has_outdated_content']:
                    score -= 0.1
        
        # Ensure score is within bounds
        return max(0.0, min(1.0, score))

    def _gather_image_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Gather image data for analysis results."""
        images = soup.find_all('img')
        
        # Count images with and without alt text
        with_alt = sum(1 for img in images if img.get('alt'))
        without_alt = len(images) - with_alt
        
        # Count images with and without lazy loading
        with_lazy = sum(1 for img in images if img.get('loading') == 'lazy')
        
        return {
            'count': len(images),
            'with_alt_text': with_alt,
            'without_alt_text': without_alt,
            'with_lazy_loading': with_lazy,
            'without_lazy_loading': len(images) - with_lazy
        }
        
    def _gather_link_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Gather link data for analysis results."""
        links = soup.find_all('a')
        
        # Count internal vs external links
        internal_links = [link for link in links if not link.get('href') or 
                         not link.get('href').startswith(('http', 'https', '//'))]
        external_links = [link for link in links if link.get('href') and 
                         link.get('href').startswith(('http', 'https', '//'))]
        
        # Count links with generic text
        generic_link_texts = ['click here', 'read more', 'learn more', 'more info', 'more information']
        generic_links = [
            link for link in links 
            if link.get_text().strip().lower() in generic_link_texts
        ]
        
        # Count links without text
        without_text = [link for link in links if not link.get_text().strip()]
        
        return {
            'count': len(links),
            'internal': len(internal_links),
            'external': len(external_links),
            'with_generic_text': len(generic_links),
            'without_text': len(without_text)
        }

    def _analyze_content_quality(
        self, soup: BeautifulSoup, words: List[str], sentences: List[str]
    ) -> Dict[str, Any]:
        """Analyze content quality factors.
        
        This examines semantic richness, content depth, and potential content duplication.
        """
        warnings = []
        suggestions = []
        
        # Analyze semantic richness (vocabulary diversity)
        unique_words = set(words)
        vocabulary_diversity = len(unique_words) / len(words) if words else 0
        
        if vocabulary_diversity < 0.4:
            warnings.append("Content has low vocabulary diversity")
            suggestions.append(
                "Use a more diverse vocabulary to improve content quality"
            )
        
        # Analyze content depth by examining semantic fields
        semantic_depth = self._analyze_semantic_depth(words)
        if semantic_depth < 0.3:
            warnings.append("Content lacks semantic depth")
            suggestions.append(
                "Explore related topics and concepts to add depth to your content"
            )
        
        # Check for potential content duplication (repeated sentences or paragraphs)
        duplicate_ratio = self._check_content_duplication(sentences)
        if duplicate_ratio > 0.2:
            warnings.append("Content contains potential duplicated sections")
            suggestions.append(
                "Review and rewrite duplicated content sections"
            )
        
        # Check for thin content sections
        thin_content = self._check_thin_content(soup)
        if thin_content:
            warnings.append("Content contains sections with minimal valuable information")
            suggestions.append(
                "Enhance thin content sections with more substantive information"
            )
        
        return {
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'vocabulary_diversity': round(vocabulary_diversity, 2),
                'semantic_depth': round(semantic_depth, 2),
                'duplicate_content_ratio': round(duplicate_ratio, 2),
                'has_thin_content': thin_content
            }
        }
    
    def _analyze_semantic_depth(self, words: List[str]) -> float:
        """Analyze the semantic depth of content.
        
        This is a simplified measure of topic coverage and content depth.
        """
        # Group words into potential semantic fields (simplified)
        word_freq = Counter(words)
        
        # Get top words and their immediate collocations
        top_words = [word for word, count in word_freq.most_common(10)]
        
        # Count related terms for each top word (simplified semantic field detection)
        semantic_fields = 0
        for word in top_words:
            # Consider words starting with the same 4 chars as potentially related
            # This is a very simplified approach - in a real implementation, 
            # you'd use proper semantic analysis or NLP
            if len(word) >= 4:
                prefix = word[:4]
                related_terms = sum(1 for w in words if w.startswith(prefix) and w != word)
                if related_terms >= 3:
                    semantic_fields += 1
        
        # Calculate semantic depth score (0-1)
        return min(1.0, semantic_fields / 5)
    
    def _check_content_duplication(self, sentences: List[str]) -> float:
        """Check for duplicated content within the page."""
        if not sentences:
            return 0.0
            
        # Count duplicate sentences
        sentence_counts = Counter(sentences)
        duplicate_count = sum(count - 1 for count in sentence_counts.values() if count > 1)
        
        # Calculate duplicate ratio
        return duplicate_count / len(sentences) if sentences else 0
    
    def _check_thin_content(self, soup: BeautifulSoup) -> bool:
        """Check for thin content sections."""
        # Look for short paragraphs with little valuable content
        paragraphs = soup.find_all('p')
        
        # Count very short paragraphs (less than 20 words)
        short_paragraphs = 0
        for p in paragraphs:
            text = p.get_text().strip()
            if text and len(text.split()) < 20:
                short_paragraphs += 1
        
        # If more than 50% of paragraphs are very short, consider it thin content
        return short_paragraphs > len(paragraphs) * 0.5 if paragraphs else False
    
    def _analyze_mobile_friendliness(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze content for mobile-friendliness issues."""
        warnings = []
        suggestions = []
        
        # Check for potential mobile usability issues
        
        # Check for tables (often problematic on mobile)
        tables = soup.find_all('table')
        if tables:
            warnings.append(f"Found {len(tables)} tables which may cause mobile display issues")
            suggestions.append(
                "Consider responsive alternatives to tables for mobile users"
            )
        
        # Check for fixed-width elements
        fixed_width_elements = []
        for elem in soup.find_all(style=True):
            style = elem.get('style', '')
            if 'width' in style and 'px' in style:
                fixed_width_elements.append(elem)
        
        if fixed_width_elements:
            warnings.append(f"Found {len(fixed_width_elements)} elements with fixed width")
            suggestions.append(
                "Use relative units (%, em, rem) instead of fixed pixel widths"
            )
        
        # Check for small font sizes
        small_font_elements = []
        for elem in soup.find_all(style=True):
            style = elem.get('style', '')
            if 'font-size' in style and 'px' in style:
                size_match = re.search(r'font-size:\s*(\d+)px', style)
                if size_match and int(size_match.group(1)) < 16:
                    small_font_elements.append(elem)
        
        if small_font_elements:
            warnings.append(f"Found {len(small_font_elements)} elements with small font size")
            suggestions.append(
                "Use font sizes of at least 16px for mobile readability"
            )
        
        # Check for touch-unfriendly elements
        small_clickable_elements = 0
        for elem in soup.find_all(['a', 'button']):
            # Check if element has dimensions specified
            style = elem.get('style', '')
            if ('width' in style and 'px' in style) or ('height' in style and 'px' in style):
                width_match = re.search(r'width:\s*(\d+)px', style)
                height_match = re.search(r'height:\s*(\d+)px', style)
                
                # Consider elements smaller than 44x44px as too small for touch
                if (width_match and int(width_match.group(1)) < 44) or \
                   (height_match and int(height_match.group(1)) < 44):
                    small_clickable_elements += 1
        
        if small_clickable_elements:
            warnings.append(f"Found {small_clickable_elements} clickable elements too small for touch")
            suggestions.append(
                "Make touch targets at least 44x44px for better mobile usability"
            )
        
        return {
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'tables_count': len(tables),
                'fixed_width_elements': len(fixed_width_elements),
                'small_font_elements': len(small_font_elements),
                'small_touch_targets': small_clickable_elements
            }
        }

    def _analyze_content_to_code_ratio(self, html_content: str, text_content: str) -> Dict[str, Any]:
        """Analyze the ratio of actual content to HTML code.
        
        Args:
            html_content: The raw HTML content
            text_content: The extracted text content
            
        Returns:
            Dict with analysis results, warnings, and suggestions
        """
        warnings = []
        suggestions = []
        
        # Calculate sizes
        html_size = len(html_content)
        text_size = len(text_content)
        
        # Handle edge case
        if html_size == 0:
            return {
                'warnings': ['Empty HTML content'],
                'suggestions': ['Add meaningful content to the page'],
                'data': {
                    'html_size': 0,
                    'text_size': 0,
                    'ratio': 0,
                    'percentage': 0
                }
            }
        
        # Calculate ratio and percentage
        ratio = text_size / html_size
        percentage = ratio * 100
        
        # Analyze results
        if ratio < 0.1:  # Less than 10% content
            warnings.append(f"Very low content-to-code ratio ({percentage:.1f}%)")
            suggestions.append(
                "Reduce excessive HTML, JavaScript, or inline CSS to improve page load speed"
            )
        elif ratio < 0.25:  # Less than 25% content
            warnings.append(f"Low content-to-code ratio ({percentage:.1f}%)")
            suggestions.append(
                "Consider simplifying page structure or moving scripts to external files"
            )
            
        # Check for excessive HTML comments
        comment_size = sum(len(comment.string) for comment in re.finditer(r'<!--.*?-->', html_content, re.DOTALL))
        comment_percentage = (comment_size / html_size) * 100
        
        if comment_percentage > 5:  # More than 5% of the page is comments
            warnings.append(f"Excessive HTML comments ({comment_percentage:.1f}% of page size)")
            suggestions.append("Remove unnecessary HTML comments to reduce page size")
            
        # Check for inline scripts and styles
        inline_scripts = len(re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL))
        inline_styles = len(re.findall(r'<style[^>]*>(.*?)</style>', html_content, re.DOTALL))
        
        if inline_scripts > 3:
            suggestions.append(f"Consider moving {inline_scripts} inline scripts to external files")
            
        if inline_styles > 3:
            suggestions.append(f"Consider moving {inline_styles} inline styles to external CSS files")
            
        return {
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'html_size': html_size,
                'text_size': text_size,
                'ratio': round(ratio, 3),
                'percentage': round(percentage, 1),
                'comment_size': comment_size,
                'comment_percentage': round(comment_percentage, 1),
                'inline_scripts': inline_scripts,
                'inline_styles': inline_styles
            }
        }

    def _analyze_structured_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze schema.org structured data markup in the HTML.
        
        Args:
            soup: BeautifulSoup object of the original HTML
            
        Returns:
            Dict with analysis results, warnings, and suggestions
        """
        warnings = []
        suggestions = []
        schema_types = []
        
        # Check for JSON-LD structured data
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        json_ld_data = []
        
        for script in json_ld_scripts:
            try:
                # Parse the JSON content
                data = json.loads(script.string)
                
                # Check if it's schema.org data
                if isinstance(data, dict) and ('@context' in data and 'schema.org' in data['@context']):
                    json_ld_data.append(data)
                    if '@type' in data:
                        schema_types.append(data['@type'])
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and ('@context' in item and 'schema.org' in item['@context']):
                            json_ld_data.append(item)
                            if '@type' in item:
                                schema_types.append(item['@type'])
            except (json.JSONDecodeError, TypeError):
                warnings.append("Invalid JSON-LD structured data found")
                suggestions.append("Fix malformed JSON-LD schema markup")
                
        # Check for microdata structured data
        microdata_elements = soup.find_all(itemscope=True)
        microdata_types = []
        
        for element in microdata_elements:
            itemtype = element.get('itemtype', '')
            if 'schema.org' in itemtype:
                # Extract the schema type from the URL
                schema_type = itemtype.split('/')[-1]
                microdata_types.append(schema_type)
                schema_types.append(schema_type)
                
        # Check for RDFa structured data
        rdfa_elements = soup.find_all(attrs={"vocab": True})
        rdfa_types = []
        
        for element in rdfa_elements:
            vocab = element.get('vocab', '')
            if 'schema.org' in vocab:
                # Find all elements with typeof attribute
                type_elements = element.find_all(attrs={"typeof": True})
                for type_elem in type_elements:
                    rdfa_types.append(type_elem.get('typeof', ''))
                    schema_types.append(type_elem.get('typeof', ''))
                    
        # Analyze findings
        has_structured_data = bool(json_ld_data or microdata_types or rdfa_types)
        schema_types = [t for t in schema_types if t]  # Remove empty strings
        
        if not has_structured_data:
            warnings.append("No schema.org structured data found on the page")
            
            # Suggest appropriate schema based on content
            page_title = soup.title.string if soup.title else ""
            page_type = self._suggest_schema_type(soup, page_title)
            
            suggestions.append(
                f"Consider adding schema.org structured data ({page_type}) "
                "to improve search engine understanding of your content"
            )
        else:
            # Check for common schema issues
            if len(schema_types) == 0:
                warnings.append("Schema.org markup found but without type specification")
                suggestions.append("Add @type property to your schema.org markup")
                
            # Check for organization, local business without contact info
            if any(t in ['Organization', 'LocalBusiness'] for t in schema_types):
                if not self._check_contact_info_in_schema(json_ld_data):
                    suggestions.append(
                        "Add contact information to your Organization/LocalBusiness schema"
                    )
                    
            # Check for product schema without price or availability
            if 'Product' in schema_types:
                if not self._check_product_info_in_schema(json_ld_data):
                    suggestions.append(
                        "Enhance your Product schema with price and availability information"
                    )
                    
            # Check for article schema without dates
            if any(t in ['Article', 'BlogPosting', 'NewsArticle'] for t in schema_types):
                if not self._check_article_dates_in_schema(json_ld_data):
                    suggestions.append(
                        "Add datePublished and dateModified to your Article schema"
                    )
                    
        # Prepare analysis data
        return {
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'has_structured_data': has_structured_data,
                'schema_types': schema_types,
                'json_ld_count': len(json_ld_data),
                'microdata_count': len(microdata_types),
                'rdfa_count': len(rdfa_types)
            }
        }
        
    def _suggest_schema_type(self, soup: BeautifulSoup, title: str) -> str:
        """Suggest appropriate schema.org type based on page content."""
        # Check for common page patterns
        
        # Check if it's a product page
        product_indicators = ['price', 'buy now', 'add to cart', 'product', 'item']
        has_product_terms = any(term in title.lower() for term in product_indicators)
        
        # Check for forms - might be a contact page
        contact_forms = soup.find_all('form')
        has_contact_form = bool(contact_forms)
        
        # Check for blog patterns
        blog_indicators = ['blog', 'article', 'post', 'news']
        has_blog_terms = any(term in title.lower() for term in blog_indicators)
        
        # Check for article structure (complex content with headings)
        has_article_structure = bool(soup.find_all(['h1', 'h2', 'h3'])) and len(soup.find_all('p')) > 5
        
        # Make suggestions based on patterns
        if has_product_terms:
            return "Product"
        elif has_contact_form:
            return "ContactPage"
        elif has_blog_terms or has_article_structure:
            return "Article or BlogPosting"
        else:
            return "WebPage"  # Default fallback
            
    def _check_contact_info_in_schema(self, schema_data: List[Dict[str, Any]]) -> bool:
        """Check if contact information exists in organization schema."""
        for data in schema_data:
            if not isinstance(data, dict):
                continue
                
            # Check for common contact properties
            contact_props = ['telephone', 'email', 'contactPoint', 'address']
            if any(prop in data for prop in contact_props):
                return True
                
        return False
        
    def _check_product_info_in_schema(self, schema_data: List[Dict[str, Any]]) -> bool:
        """Check if product schema has essential information."""
        for data in schema_data:
            if not isinstance(data, dict) or data.get('@type') != 'Product':
                continue
                
            # Check for essential product properties
            has_offers = 'offers' in data
            has_price = False
            
            if has_offers:
                offers = data['offers']
                if isinstance(offers, dict):
                    has_price = 'price' in offers or 'priceCurrency' in offers
                elif isinstance(offers, list) and offers:
                    has_price = 'price' in offers[0] or 'priceCurrency' in offers[0]
                    
            return has_price
            
        return False
        
    def _check_article_dates_in_schema(self, schema_data: List[Dict[str, Any]]) -> bool:
        """Check if article schema has publication and modification dates."""
        article_types = ['Article', 'BlogPosting', 'NewsArticle']
        
        for data in schema_data:
            if not isinstance(data, dict) or data.get('@type') not in article_types:
                continue
                
            # Check for date properties
            has_pub_date = 'datePublished' in data
            has_mod_date = 'dateModified' in data
            
            return has_pub_date and has_mod_date
            
        return False

    def _analyze_accessibility(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze accessibility compliance of the content.
        
        Args:
            soup: BeautifulSoup object of the HTML
            
        Returns:
            Dict with analysis results, issues, warnings, and suggestions
        """
        issues = []
        warnings = []
        suggestions = []
        
        # Check for language attribute
        html_tag = soup.find('html')
        has_lang = html_tag and html_tag.get('lang')
        
        if not has_lang:
            issues.append("Missing language attribute on HTML element")
            suggestions.append(
                "Add a lang attribute to the HTML element (e.g., <html lang=\"en\">)"
            )
        
        # Check for proper heading hierarchy
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        heading_levels = [int(h.name[1]) for h in headings]
        
        if heading_levels:
            if 1 not in heading_levels:
                issues.append("No H1 heading found - important for screen readers")
                suggestions.append("Add an H1 heading as the main title of your content")
            
            prev_level = 0
            skipped_levels = []
            
            for i, level in enumerate(heading_levels):
                if level > prev_level + 1 and prev_level > 0:
                    skipped_levels.append(f"H{prev_level} to H{level}")
                prev_level = level
            
            if skipped_levels:
                issues.append(f"Skipped heading levels: {', '.join(skipped_levels)}")
                suggestions.append(
                    "Maintain a proper heading hierarchy without skipping levels"
                )
        
        # Check for image accessibility
        images = soup.find_all('img')
        missing_alt = [img for img in images if not img.get('alt')]
        
        if missing_alt:
            issues.append(f"Found {len(missing_alt)} images without alt text")
            suggestions.append(
                "Add descriptive alt text to all images for screen reader users"
            )
        
        # Check for form accessibility
        forms = soup.find_all('form')
        
        for form in forms:
            # Check for labels on form elements
            inputs = form.find_all(['input', 'textarea', 'select'])
            inputs_without_labels = []
            
            for input_element in inputs:
                # Skip hidden and submit inputs
                input_type = input_element.get('type', '').lower()
                if input_type in ['hidden', 'submit', 'button']:
                    continue
                
                # Check for label
                input_id = input_element.get('id')
                has_label = False
                
                if input_id:
                    label = soup.find('label', attrs={'for': input_id})
                    has_label = bool(label)
                
                # Check for aria-label or aria-labelledby
                has_aria = bool(input_element.get('aria-label') or input_element.get('aria-labelledby'))
                
                if not has_label and not has_aria:
                    inputs_without_labels.append(input_element)
            
            if inputs_without_labels:
                issues.append(f"Found {len(inputs_without_labels)} form inputs without labels")
                suggestions.append(
                    "Add proper labels to all form inputs for screen reader accessibility"
                )
        
        # Check for sufficient color contrast (simplified approach)
        elements_with_color = []
        
        for element in soup.find_all(style=True):
            style = element.get('style', '')
            if 'color' in style and 'background' in style:
                elements_with_color.append(element)
        
        if elements_with_color:
            warnings.append(
                f"Found {len(elements_with_color)} elements with custom colors - "
                "verify contrast ratios"
            )
            suggestions.append(
                "Ensure text has sufficient contrast with background colors (4.5:1 ratio)"
            )
        
        # Check for tabindex values
        high_tabindex = []
        for element in soup.find_all(tabindex=True):
            tabindex = element.get('tabindex')
            try:
                if int(tabindex) > 0:
                    high_tabindex.append(element)
            except ValueError:
                pass
        
        if high_tabindex:
            warnings.append(f"Found {len(high_tabindex)} elements with positive tabindex values")
            suggestions.append(
                "Avoid using positive tabindex values which can disrupt natural tab order"
            )
        
        # Check for ARIA usage
        aria_elements = []
        for tag in soup.find_all():
            for attr in tag.attrs:
                if attr.startswith('aria-'):
                    aria_elements.append(tag)
                    break
        
        # Check for empty links and buttons
        empty_interactive = []
        for element in soup.find_all(['a', 'button']):
            if not element.get_text().strip() and not element.find('img'):
                empty_interactive.append(element)
        
        if empty_interactive:
            issues.append(f"Found {len(empty_interactive)} empty links or buttons")
            suggestions.append(
                "Add text content to all interactive elements for screen reader users"
            )
        
        # Return analysis results
        return {
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'has_lang_attribute': has_lang,
                'has_proper_headings': 1 in heading_levels if heading_levels else False,
                'images_without_alt': len(missing_alt),
                'inputs_without_labels': len(forms) > 0 and any('form inputs without labels' in issue for issue in issues),
                'has_color_contrast_issues': len(elements_with_color) > 0,
                'has_positive_tabindex': len(high_tabindex) > 0,
                'uses_aria': len(aria_elements) > 0,
                'has_empty_interactive': len(empty_interactive) > 0
            }
        }

    def _analyze_content_freshness(self, soup: BeautifulSoup, content: str) -> Dict[str, Any]:
        """Analyze the freshness and timeliness of content.
        
        Args:
            soup: BeautifulSoup object of the HTML
            content: Extracted text content
            
        Returns:
            Dict with analysis results, warnings, and suggestions
        """
        from datetime import datetime, timedelta
        import re
        
        warnings = []
        suggestions = []
        
        # Initialize data
        dates_found = []
        publication_date = None
        last_modified_date = None
        has_date_indicators = False
        has_outdated_content = False
        
        # Look for date metadata
        meta_dates = []
        
        # Check standard publication metadata
        for meta in soup.find_all('meta'):
            if meta.get('property') in ['article:published_time', 'og:published_time']:
                try:
                    date_str = meta.get('content')
                    if date_str:
                        pub_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        meta_dates.append(pub_date)
                        publication_date = pub_date
                except (ValueError, TypeError):
                    pass
            
            # Check for modified time
            if meta.get('property') in ['article:modified_time', 'og:updated_time']:
                try:
                    date_str = meta.get('content')
                    if date_str:
                        mod_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        meta_dates.append(mod_date)
                        last_modified_date = mod_date
                except (ValueError, TypeError):
                    pass
        
        # Look for date in schema.org structured data
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                
                # Handle both direct objects and arrays of objects
                items = [data] if isinstance(data, dict) else data if isinstance(data, list) else []
                
                for item in items:
                    if not isinstance(item, dict):
                        continue
                        
                    # Check for datePublished and dateModified
                    if 'datePublished' in item:
                        try:
                            date_str = item['datePublished']
                            pub_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            meta_dates.append(pub_date)
                            if not publication_date:
                                publication_date = pub_date
                        except (ValueError, TypeError):
                            pass
                            
                    if 'dateModified' in item:
                        try:
                            date_str = item['dateModified']
                            mod_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            meta_dates.append(mod_date)
                            if not last_modified_date:
                                last_modified_date = mod_date
                        except (ValueError, TypeError):
                            pass
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Extract dates from content with regex
        # Format: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY, Month DD, YYYY
        date_patterns = [
            r'\b\d{4}-\d{1,2}-\d{1,2}\b',  # YYYY-MM-DD
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY or DD/MM/YYYY
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b',  # Month DD, YYYY
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}\b',  # Mon DD, YYYY
        ]
        
        content_dates = []
        for pattern in date_patterns:
            for date_match in re.finditer(pattern, content):
                date_str = date_match.group(0)
                dates_found.append(date_str)
                has_date_indicators = True
        
        # Look for time indicators
        time_indicators = [
            'recent', 'recently', 'latest', 'new', 'update', 'updated',
            'current', 'today', 'yesterday', 'last week', 'this month',
            'this year', 'now', '2023', '2024'  # Add current years
        ]
        
        for indicator in time_indicators:
            if indicator in content.lower():
                has_date_indicators = True
                break
        
        # Look for outdated content indicators
        current_year = datetime.now().year
        outdated_years = [str(year) for year in range(current_year - 10, current_year - 2)]
        
        for year in outdated_years:
            if re.search(r'\b' + year + r'\b', content):
                has_outdated_content = True
                break
        
        # Analyze freshness
        today = datetime.now()
        
        # Determine content age if publication date is available
        content_age_days = None
        if publication_date:
            content_age_days = (today - publication_date).days
            
            if content_age_days > 730:  # Older than 2 years
                warnings.append(
                    f"Content is over 2 years old (published {publication_date.strftime('%Y-%m-%d')})"
                )
                suggestions.append(
                    "Consider updating content or adding a recent update date"
                )
            elif content_age_days > 365:  # Older than 1 year
                warnings.append(
                    f"Content is over 1 year old (published {publication_date.strftime('%Y-%m-%d')})"
                )
                suggestions.append(
                    "Review content for currency and update if necessary"
                )
        else:
            # No explicit publication date
            if has_outdated_content:
                warnings.append("Content contains outdated year references")
                suggestions.append(
                    "Update outdated references and add publication/modification dates"
                )
            elif not has_date_indicators:
                warnings.append("No date indicators or publication date found")
                suggestions.append(
                    "Add publication date metadata to help search engines understand content freshness"
                )
        
        # Check if modified date is significantly more recent than publication date
        if publication_date and last_modified_date:
            days_since_update = (last_modified_date - publication_date).days
            if days_since_update > 180:  # More than 6 months between publication and last update
                # This is actually good!
                pass
            elif content_age_days and content_age_days > 365 and days_since_update < 180:
                # Old content with no recent updates
                suggestions.append(
                    "Content is over a year old with no recent updates - consider refreshing"
                )
        
        # Check for seasonal content that may need updates
        seasonal_terms = ['holiday', 'christmas', 'halloween', 'summer', 'winter', 
                         'spring', 'fall', 'black friday', 'new year']
        is_seasonal = any(term in content.lower() for term in seasonal_terms)
        
        if is_seasonal and ((publication_date and content_age_days and content_age_days > 300) or 
                          has_outdated_content):
            warnings.append("Seasonal content appears to be outdated")
            suggestions.append("Update seasonal content for the current or upcoming season")
        
        # Prepare analysis data
        return {
            'warnings': warnings,
            'suggestions': suggestions,
            'data': {
                'has_publication_date': publication_date is not None,
                'has_modified_date': last_modified_date is not None,
                'publication_date': publication_date.isoformat() if publication_date else None,
                'last_modified_date': last_modified_date.isoformat() if last_modified_date else None,
                'content_age_days': content_age_days,
                'has_date_indicators': has_date_indicators,
                'has_outdated_content': has_outdated_content,
                'is_seasonal_content': is_seasonal,
                'dates_found': dates_found[:10]  # Limit to first 10 for brevity
            }
        } 