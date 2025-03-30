"""Heading structure analyzer implementation."""

from typing import Dict, Any, Optional, List, Tuple
from bs4 import BeautifulSoup
import re

from .base import BaseAnalyzer, AnalysisResult

class HeadingStructureAnalyzer(BaseAnalyzer[str, Dict[str, Any]]):
    """Analyzer for webpage heading structure.
    
    This analyzer examines the heading hierarchy (h1-h6) of a webpage and provides
    analysis based on SEO best practices, including proper nesting, uniqueness of H1,
    heading distribution, and semantic structure.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the heading structure analyzer.
        
        Args:
            config: Optional configuration dictionary that may include:
                - max_heading_length: Maximum length for headings (default: 60)
                - min_heading_length: Minimum length for headings (default: 10)
                - max_heading_depth: Maximum heading depth (h1-h6) to analyze (default: 6)
                - require_h1: Whether to require H1 heading (default: True)
                - allow_multiple_h1: Whether to allow multiple H1 headings (default: False)
        """
        super().__init__(config)
        self.max_heading_length = self.config.get('max_heading_length', 60)
        self.min_heading_length = self.config.get('min_heading_length', 10)
        self.max_heading_depth = min(self.config.get('max_heading_depth', 6), 6)
        self.require_h1 = self.config.get('require_h1', True)
        self.allow_multiple_h1 = self.config.get('allow_multiple_h1', False)

    def analyze(self, html_content: str) -> AnalysisResult[Dict[str, Any]]:
        """Analyze the webpage heading structure from HTML content.
        
        Args:
            html_content: HTML content to analyze
            
        Returns:
            AnalysisResult containing heading structure analysis data
            
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
            
            # Get all headings
            headings = self._get_headings(soup)
            if not headings:
                issues.append("No headings found in content")
                return AnalysisResult(
                    data={
                        'has_headings': False,
                        'heading_count': 0
                    },
                    metadata=self.create_metadata('heading_structure'),
                    score=0.0,
                    issues=issues,
                    warnings=warnings,
                    recommendations=["Add proper heading structure to improve content organization"]
                )
            
            # Analyze H1 headings
            h1_issues = self._analyze_h1_headings(headings)
            issues.extend(h1_issues)
            
            # Analyze heading hierarchy
            hierarchy_issues = self._analyze_hierarchy(headings)
            issues.extend(hierarchy_issues)
            
            # Analyze heading lengths
            length_issues, length_warnings = self._analyze_heading_lengths(headings)
            issues.extend(length_issues)
            warnings.extend(length_warnings)
            
            # Analyze heading distribution
            distribution_warnings = self._analyze_distribution(headings)
            warnings.extend(distribution_warnings)
            
            # Generate recommendations
            recommendations.extend(self._generate_recommendations(issues, warnings))
            
            # Calculate overall score
            score = self.calculate_score(issues, warnings)
            
            # Prepare analysis data
            analysis_data = {
                'has_headings': True,
                'heading_count': len(headings),
                'heading_distribution': self._count_headings_by_level(headings),
                'heading_structure': self._get_heading_structure(headings),
                'average_heading_length': self._calculate_average_length(headings),
                'h1_content': self._get_h1_content(headings)
            }
            
            return AnalysisResult(
                data=analysis_data,
                metadata=self.create_metadata('heading_structure'),
                score=score,
                issues=issues,
                warnings=warnings,
                recommendations=recommendations
            )
            
        except Exception as e:
            raise self.error_type(f"Failed to analyze heading structure: {str(e)}")

    def _get_headings(self, soup: BeautifulSoup) -> List[Tuple[int, str, str]]:
        """Get all headings with their levels and content.
        
        Returns list of tuples: (level, text, full_html)
        """
        headings = []
        for i in range(1, self.max_heading_depth + 1):
            for heading in soup.find_all(f'h{i}'):
                headings.append((
                    i,
                    heading.get_text().strip(),
                    str(heading)
                ))
        return headings

    def _analyze_h1_headings(self, headings: List[Tuple[int, str, str]]) -> List[str]:
        """Analyze H1 headings for issues."""
        issues = []
        h1_headings = [h for h in headings if h[0] == 1]
        
        if not h1_headings and self.require_h1:
            issues.append("No H1 heading found")
        elif len(h1_headings) > 1 and not self.allow_multiple_h1:
            issues.append(f"Multiple H1 headings found ({len(h1_headings)})")
        
        return issues

    def _analyze_hierarchy(self, headings: List[Tuple[int, str, str]]) -> List[str]:
        """Analyze heading hierarchy for proper nesting."""
        issues = []
        current_level = 1
        
        for i, (level, text, _) in enumerate(headings):
            if i == 0 and level != 1 and self.require_h1:
                issues.append("First heading is not H1")
            elif level - current_level > 1:
                issues.append(
                    f"Improper heading structure: H{current_level} followed by H{level}"
                )
            current_level = level
            
        return issues

    def _analyze_heading_lengths(
        self, headings: List[Tuple[int, str, str]]
    ) -> Tuple[List[str], List[str]]:
        """Analyze heading lengths for SEO optimization."""
        issues = []
        warnings = []
        
        for level, text, _ in headings:
            length = len(text)
            if length < self.min_heading_length:
                warnings.append(
                    f"H{level} heading too short ({length} chars): '{text}'"
                )
            elif length > self.max_heading_length:
                warnings.append(
                    f"H{level} heading too long ({length} chars): '{text}'"
                )
            
            # Check for empty headings
            if not text.strip():
                issues.append(f"Empty H{level} heading found")
                
        return issues, warnings

    def _analyze_distribution(self, headings: List[Tuple[int, str, str]]) -> List[str]:
        """Analyze heading distribution for content structure."""
        warnings = []
        distribution = self._count_headings_by_level(headings)
        
        # Check for too many headings
        total_headings = len(headings)
        if total_headings > 20:  # Arbitrary threshold, can be configurable
            warnings.append(
                f"Large number of headings found ({total_headings}). "
                "Consider simplifying the structure."
            )
        
        # Check for balanced distribution
        for level in range(2, self.max_heading_depth + 1):
            if distribution.get(f'h{level}', 0) > distribution.get(f'h{level-1}', 0) * 3:
                warnings.append(
                    f"Disproportionate number of H{level} headings compared to H{level-1}"
                )
                
        return warnings

    def _count_headings_by_level(self, headings: List[Tuple[int, str, str]]) -> Dict[str, int]:
        """Count the number of headings at each level."""
        distribution = {}
        for level, _, _ in headings:
            key = f'h{level}'
            distribution[key] = distribution.get(key, 0) + 1
        return distribution

    def _get_heading_structure(self, headings: List[Tuple[int, str, str]]) -> List[Dict[str, Any]]:
        """Get the hierarchical structure of headings."""
        return [
            {
                'level': level,
                'text': text,
                'html': html
            }
            for level, text, html in headings
        ]

    def _calculate_average_length(self, headings: List[Tuple[int, str, str]]) -> float:
        """Calculate the average length of headings."""
        if not headings:
            return 0.0
        total_length = sum(len(text) for _, text, _ in headings)
        return round(total_length / len(headings), 2)

    def _get_h1_content(self, headings: List[Tuple[int, str, str]]) -> List[str]:
        """Get the content of all H1 headings."""
        return [text for level, text, _ in headings if level == 1]

    def _generate_recommendations(self, issues: List[str], warnings: List[str]) -> List[str]:
        """Generate recommendations based on issues and warnings."""
        recommendations = []
        
        if "No H1 heading found" in issues:
            recommendations.append(
                "Add a single, descriptive H1 heading that clearly indicates the main topic"
            )
        
        if "Multiple H1 headings found" in issues:
            recommendations.append(
                "Keep only one H1 heading per page and use H2-H6 for subsections"
            )
        
        if any("heading too long" in w for w in warnings):
            recommendations.append(
                f"Keep heading lengths between {self.min_heading_length} and "
                f"{self.max_heading_length} characters for better readability"
            )
        
        if any("Improper heading structure" in i for i in issues):
            recommendations.append(
                "Maintain proper heading hierarchy (H1 → H2 → H3) without skipping levels"
            )
        
        if any("Disproportionate number" in w for w in warnings):
            recommendations.append(
                "Balance the number of subheadings under each section"
            )
            
        return recommendations 