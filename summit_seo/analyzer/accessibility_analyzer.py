"""Accessibility analyzer implementation."""

from typing import Dict, Any, Optional, List, Tuple
from bs4 import BeautifulSoup
import re
from dataclasses import dataclass

from .base import BaseAnalyzer, AnalysisResult, InputType, OutputType

@dataclass
class AccessibilityIssue:
    """Accessibility issue found during analysis."""
    name: str
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    wcag_criterion: str  # The WCAG criterion affected
    element_type: str   # The type of element affected
    remediation: str

class AccessibilityAnalyzer(BaseAnalyzer[str, Dict[str, Any]]):
    """Analyzer for webpage accessibility.
    
    This analyzer examines various accessibility aspects of a webpage according to
    WCAG standards, including proper alt text, form labeling, heading structure, 
    color contrast, keyboard navigation, ARIA roles, and more.
    """
    
    # Severity levels for accessibility issues
    SEVERITY_CRITICAL = "critical"
    SEVERITY_HIGH = "high"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_LOW = "low"
    
    # WCAG criteria mapping
    WCAG_CRITERIA = {
        "1.1.1": "Non-text Content",
        "1.3.1": "Info and Relationships", 
        "1.3.2": "Meaningful Sequence",
        "1.4.3": "Contrast (Minimum)",
        "2.1.1": "Keyboard",
        "2.4.1": "Bypass Blocks",
        "2.4.2": "Page Titled",
        "2.4.3": "Focus Order",
        "2.4.4": "Link Purpose (In Context)",
        "2.4.6": "Headings and Labels",
        "3.1.1": "Language of Page",
        "3.3.2": "Labels or Instructions",
        "4.1.1": "Parsing",
        "4.1.2": "Name, Role, Value"
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the accessibility analyzer.
        
        Args:
            config: Optional configuration dictionary that may include:
                - check_alt_text: Whether to check for alt text on images (default: True)
                - check_form_labels: Whether to check form field labeling (default: True)
                - check_heading_structure: Whether to check heading structure (default: True)
                - check_color_contrast: Whether to check color contrast (default: True)
                - check_keyboard_navigation: Whether to check keyboard navigation (default: True)
                - check_aria_roles: Whether to check ARIA roles (default: True)
                - check_language: Whether to check page language (default: True)
                - check_document_structure: Whether to check document structure (default: True)
                - issue_weight_critical: Weight for critical severity issues (default: 0.4)
                - issue_weight_high: Weight for high severity issues (default: 0.3)
                - issue_weight_medium: Weight for medium severity issues (default: 0.2)
                - issue_weight_low: Weight for low severity issues (default: 0.1)
                - min_contrast_ratio: Minimum color contrast ratio (default: 4.5)
        """
        super().__init__(config)
        
        # Configure which checks to run
        self.check_alt_text = self.config.get('check_alt_text', True)
        self.check_form_labels = self.config.get('check_form_labels', True)
        self.check_heading_structure = self.config.get('check_heading_structure', True)
        self.check_color_contrast = self.config.get('check_color_contrast', True)
        self.check_keyboard_navigation = self.config.get('check_keyboard_navigation', True)
        self.check_aria_roles = self.config.get('check_aria_roles', True)
        self.check_language = self.config.get('check_language', True)
        self.check_document_structure = self.config.get('check_document_structure', True)
        
        # Configure issue weights for scoring
        self.issue_weight_critical = self.config.get('issue_weight_critical', 0.4)
        self.issue_weight_high = self.config.get('issue_weight_high', 0.3)
        self.issue_weight_medium = self.config.get('issue_weight_medium', 0.2)
        self.issue_weight_low = self.config.get('issue_weight_low', 0.1)
        
        # Configure other parameters
        self.min_contrast_ratio = self.config.get('min_contrast_ratio', 4.5)
        
    def analyze(self, html_content: str) -> AnalysisResult[Dict[str, Any]]:
        """Analyze the webpage for accessibility issues.
        
        Args:
            html_content: HTML content to analyze
            
        Returns:
            AnalysisResult containing accessibility analysis data
            
        Raises:
            AnalyzerError: If analysis fails
        """
        self.validate_input(html_content)
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Initialize analysis components
            issues = []
            warnings = []
            recommendations = []
            accessibility_issues = []
            
            # Initialize analysis data
            analysis_data = {
                'has_accessibility_issues': False,
                'accessibility_score': 100,
                'critical_severity_issues': 0,
                'high_severity_issues': 0,
                'medium_severity_issues': 0,
                'low_severity_issues': 0,
                'accessibility_issues': [],
                'wcag_criteria_violations': [],
                'elements_with_issues': 0,
                'total_elements_analyzed': 0,
                'compliant_elements': 0,
                'non_compliant_elements': 0,
            }
            
            # Run enabled accessibility checks
            if self.check_language:
                language_results = self._analyze_language(soup)
                self._merge_results(language_results, issues, warnings, recommendations, accessibility_issues)
                analysis_data['wcag_criteria_violations'].extend(language_results.get('wcag_violations', []))
                analysis_data['elements_with_issues'] += language_results.get('elements_with_issues', 0)
                analysis_data['total_elements_analyzed'] += language_results.get('total_elements_analyzed', 0)
                analysis_data['compliant_elements'] += language_results.get('compliant_elements', 0)
                analysis_data['non_compliant_elements'] += language_results.get('non_compliant_elements', 0)
            
            if self.check_alt_text:
                alt_text_results = self._analyze_alt_text(soup)
                self._merge_results(alt_text_results, issues, warnings, recommendations, accessibility_issues)
                analysis_data['wcag_criteria_violations'].extend(alt_text_results.get('wcag_violations', []))
                analysis_data['elements_with_issues'] += alt_text_results.get('elements_with_issues', 0)
                analysis_data['total_elements_analyzed'] += alt_text_results.get('total_elements_analyzed', 0)
                analysis_data['compliant_elements'] += alt_text_results.get('compliant_elements', 0)
                analysis_data['non_compliant_elements'] += alt_text_results.get('non_compliant_elements', 0)
            
            if self.check_heading_structure:
                heading_results = self._analyze_heading_structure(soup)
                self._merge_results(heading_results, issues, warnings, recommendations, accessibility_issues)
                analysis_data['wcag_criteria_violations'].extend(heading_results.get('wcag_violations', []))
                analysis_data['elements_with_issues'] += heading_results.get('elements_with_issues', 0)
                analysis_data['total_elements_analyzed'] += heading_results.get('total_elements_analyzed', 0)
                analysis_data['compliant_elements'] += heading_results.get('compliant_elements', 0)
                analysis_data['non_compliant_elements'] += heading_results.get('non_compliant_elements', 0)
            
            if self.check_form_labels:
                form_results = self._analyze_form_labels(soup)
                self._merge_results(form_results, issues, warnings, recommendations, accessibility_issues)
                analysis_data['wcag_criteria_violations'].extend(form_results.get('wcag_violations', []))
                analysis_data['elements_with_issues'] += form_results.get('elements_with_issues', 0)
                analysis_data['total_elements_analyzed'] += form_results.get('total_elements_analyzed', 0)
                analysis_data['compliant_elements'] += form_results.get('compliant_elements', 0)
                analysis_data['non_compliant_elements'] += form_results.get('non_compliant_elements', 0)
            
            if self.check_document_structure:
                structure_results = self._analyze_document_structure(soup)
                self._merge_results(structure_results, issues, warnings, recommendations, accessibility_issues)
                analysis_data['wcag_criteria_violations'].extend(structure_results.get('wcag_violations', []))
                analysis_data['elements_with_issues'] += structure_results.get('elements_with_issues', 0)
                analysis_data['total_elements_analyzed'] += structure_results.get('total_elements_analyzed', 0)
                analysis_data['compliant_elements'] += structure_results.get('compliant_elements', 0)
                analysis_data['non_compliant_elements'] += structure_results.get('non_compliant_elements', 0)
            
            if self.check_aria_roles:
                aria_results = self._analyze_aria_roles(soup)
                self._merge_results(aria_results, issues, warnings, recommendations, accessibility_issues)
                analysis_data['wcag_criteria_violations'].extend(aria_results.get('wcag_violations', []))
                analysis_data['elements_with_issues'] += aria_results.get('elements_with_issues', 0)
                analysis_data['total_elements_analyzed'] += aria_results.get('total_elements_analyzed', 0)
                analysis_data['compliant_elements'] += aria_results.get('compliant_elements', 0)
                analysis_data['non_compliant_elements'] += aria_results.get('non_compliant_elements', 0)
            
            if self.check_keyboard_navigation:
                keyboard_results = self._analyze_keyboard_navigation(soup)
                self._merge_results(keyboard_results, issues, warnings, recommendations, accessibility_issues)
                analysis_data['wcag_criteria_violations'].extend(keyboard_results.get('wcag_violations', []))
                analysis_data['elements_with_issues'] += keyboard_results.get('elements_with_issues', 0)
                analysis_data['total_elements_analyzed'] += keyboard_results.get('total_elements_analyzed', 0)
                analysis_data['compliant_elements'] += keyboard_results.get('compliant_elements', 0)
                analysis_data['non_compliant_elements'] += keyboard_results.get('non_compliant_elements', 0)
            
            if self.check_color_contrast:
                contrast_results = self._analyze_color_contrast(soup)
                self._merge_results(contrast_results, issues, warnings, recommendations, accessibility_issues)
                analysis_data['wcag_criteria_violations'].extend(contrast_results.get('wcag_violations', []))
                analysis_data['elements_with_issues'] += contrast_results.get('elements_with_issues', 0)
                analysis_data['total_elements_analyzed'] += contrast_results.get('total_elements_analyzed', 0)
                analysis_data['compliant_elements'] += contrast_results.get('compliant_elements', 0)
                analysis_data['non_compliant_elements'] += contrast_results.get('non_compliant_elements', 0)
            
            # Remove duplicate WCAG criteria violations
            analysis_data['wcag_criteria_violations'] = list(set(analysis_data['wcag_criteria_violations']))
            
            # Calculate accessibility score
            score = self._calculate_accessibility_score(accessibility_issues)
            analysis_data['accessibility_score'] = round(score * 100)
            
            # Update analysis data
            analysis_data['has_accessibility_issues'] = len(accessibility_issues) > 0
            analysis_data['critical_severity_issues'] = sum(1 for issue in accessibility_issues if issue.severity == self.SEVERITY_CRITICAL)
            analysis_data['high_severity_issues'] = sum(1 for issue in accessibility_issues if issue.severity == self.SEVERITY_HIGH)
            analysis_data['medium_severity_issues'] = sum(1 for issue in accessibility_issues if issue.severity == self.SEVERITY_MEDIUM)
            analysis_data['low_severity_issues'] = sum(1 for issue in accessibility_issues if issue.severity == self.SEVERITY_LOW)
            
            # Convert accessibility issues to serializable format
            analysis_data['accessibility_issues'] = [
                {
                    'name': issue.name,
                    'description': issue.description,
                    'severity': issue.severity,
                    'wcag_criterion': issue.wcag_criterion,
                    'element_type': issue.element_type,
                    'remediation': issue.remediation
                } for issue in accessibility_issues
            ]
            
            return AnalysisResult(
                data=analysis_data,
                metadata=self.create_metadata('accessibility'),
                score=score,
                issues=issues,
                warnings=warnings,
                recommendations=recommendations
            )
        
        except Exception as e:
            raise self.error_type(f"Failed to analyze accessibility: {str(e)}")
    
    def _merge_results(self, 
                      results: Dict[str, Any], 
                      issues: List[str], 
                      warnings: List[str], 
                      recommendations: List[str],
                      accessibility_issues: List[AccessibilityIssue]) -> None:
        """Merge results from individual accessibility checks.
        
        Args:
            results: Results from an accessibility check
            issues: List of issues to append to
            warnings: List of warnings to append to
            recommendations: List of recommendations to append to
            accessibility_issues: List of accessibility issues to append to
        """
        if results.get('issues'):
            issues.extend(results['issues'])
        if results.get('warnings'):
            warnings.extend(results['warnings'])
        if results.get('recommendations'):
            recommendations.extend(results['recommendations'])
        if results.get('accessibility_issues'):
            accessibility_issues.extend(results['accessibility_issues'])
    
    def _calculate_accessibility_score(self, accessibility_issues: List[AccessibilityIssue]) -> float:
        """Calculate an accessibility score based on the issues found.
        
        Args:
            accessibility_issues: List of accessibility issues found
            
        Returns:
            Float score between 0 and 1, with 1 being perfectly accessible
        """
        # Start with a perfect score
        score = 1.0
        
        # Count issues by severity
        critical_severity = sum(1 for issue in accessibility_issues if issue.severity == self.SEVERITY_CRITICAL)
        high_severity = sum(1 for issue in accessibility_issues if issue.severity == self.SEVERITY_HIGH)
        medium_severity = sum(1 for issue in accessibility_issues if issue.severity == self.SEVERITY_MEDIUM)
        low_severity = sum(1 for issue in accessibility_issues if issue.severity == self.SEVERITY_LOW)
        
        # Calculate score based on weighted severity counts
        critical_impact = min(1.0, critical_severity * self.issue_weight_critical * 1.5)
        high_impact = min(0.8, high_severity * self.issue_weight_high)
        medium_impact = min(0.5, medium_severity * self.issue_weight_medium)
        low_impact = min(0.3, low_severity * self.issue_weight_low)
        
        # Apply a more nuanced scoring
        score -= critical_impact
        score -= high_impact
        score -= medium_impact
        score -= low_impact
        
        # Ensure score stays between 0 and 1
        return max(0.0, min(1.0, score))
    
    def _analyze_language(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze language attributes of the document.
        
        Args:
            soup: BeautifulSoup object of the HTML
            
        Returns:
            Dict with analysis results
        """
        issues = []
        warnings = []
        recommendations = []
        accessibility_issues = []
        wcag_violations = []
        
        # Check for language attribute on html element
        html_tag = soup.find('html')
        has_lang = html_tag and html_tag.get('lang')
        
        # Track elements analyzed
        total_elements_analyzed = 1  # html tag
        compliant_elements = 1 if has_lang else 0
        non_compliant_elements = 0 if has_lang else 1
        elements_with_issues = 0 if has_lang else 1
        
        if not has_lang:
            issue_description = "Missing language attribute on HTML element"
            issues.append(issue_description)
            recommendations.append("Add a lang attribute to the HTML element (e.g., <html lang=\"en\">)")
            wcag_violations.append("3.1.1")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Missing Page Language",
                    description=issue_description,
                    severity=self.SEVERITY_HIGH,
                    wcag_criterion="3.1.1 Language of Page",
                    element_type="html",
                    remediation="Add a lang attribute to the HTML element (e.g., <html lang=\"en\">)"
                )
            )
        
        # Check for non-empty lang attributes
        if has_lang and not html_tag.get('lang').strip():
            issue_description = "Empty language attribute on HTML element"
            issues.append(issue_description)
            recommendations.append("Specify a valid language code in the lang attribute (e.g., <html lang=\"en\">)")
            wcag_violations.append("3.1.1")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Empty Page Language",
                    description=issue_description,
                    severity=self.SEVERITY_HIGH,
                    wcag_criterion="3.1.1 Language of Page",
                    element_type="html",
                    remediation="Specify a valid language code in the lang attribute (e.g., <html lang=\"en\">)"
                )
            )
            compliant_elements -= 1
            non_compliant_elements += 1
            elements_with_issues += 1
        
        # Check for language changes within content
        elements_with_lang = soup.find_all(attrs={"lang": True})
        total_elements_analyzed += len(elements_with_lang)
        
        for element in elements_with_lang:
            if element.name != 'html':  # Skip the html tag we already checked
                if not element.get('lang').strip():
                    issue_description = f"Empty language attribute on {element.name} element"
                    warnings.append(issue_description)
                    recommendations.append("Specify a valid language code for content in different languages")
                    
                    accessibility_issues.append(
                        AccessibilityIssue(
                            name="Empty Language Change",
                            description=issue_description,
                            severity=self.SEVERITY_MEDIUM,
                            wcag_criterion="3.1.2 Language of Parts",
                            element_type=element.name,
                            remediation="Specify a valid language code for content in different languages"
                        )
                    )
                    non_compliant_elements += 1
                    elements_with_issues += 1
                else:
                    compliant_elements += 1
        
        return {
            'issues': issues,
            'warnings': warnings,
            'recommendations': recommendations,
            'accessibility_issues': accessibility_issues,
            'wcag_violations': wcag_violations,
            'elements_with_issues': elements_with_issues,
            'total_elements_analyzed': total_elements_analyzed,
            'compliant_elements': compliant_elements,
            'non_compliant_elements': non_compliant_elements,
            'data': {
                'has_lang_attribute': bool(has_lang),
                'lang_value': html_tag.get('lang') if has_lang else None,
                'elements_with_lang_changes': len(elements_with_lang) - 1  # Exclude html tag
            }
        }
    
    def _analyze_alt_text(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze alt text for images.
        
        Args:
            soup: BeautifulSoup object of the HTML
            
        Returns:
            Dict with analysis results
        """
        issues = []
        warnings = []
        recommendations = []
        accessibility_issues = []
        wcag_violations = []
        
        # Find all images
        images = soup.find_all('img')
        total_elements_analyzed = len(images)
        compliant_elements = 0
        non_compliant_elements = 0
        elements_with_issues = 0
        
        # Images without alt attributes
        images_without_alt = [img for img in images if 'alt' not in img.attrs]
        
        # Images with empty alt attributes (might be intentional for decorative images)
        images_with_empty_alt = [img for img in images if 'alt' in img.attrs and not img['alt'].strip()]
        
        # Images with alt text that is too long
        images_with_long_alt = [img for img in images if 'alt' in img.attrs and len(img['alt'].strip()) > 125]
        
        # Evaluate and categorize each image
        for img in images:
            if 'alt' not in img.attrs:
                non_compliant_elements += 1
                elements_with_issues += 1
            elif len(img['alt'].strip()) > 125:
                non_compliant_elements += 1
                elements_with_issues += 1
            else:
                compliant_elements += 1
        
        # Report issues for missing alt text
        if images_without_alt:
            issue_description = f"Found {len(images_without_alt)} images without alt attributes"
            issues.append(issue_description)
            recommendations.append("Add alt attributes to all images to provide text alternatives")
            wcag_violations.append("1.1.1")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Missing Alt Text",
                    description=issue_description,
                    severity=self.SEVERITY_HIGH,
                    wcag_criterion="1.1.1 Non-text Content",
                    element_type="img",
                    remediation="Add descriptive alt attributes to all images to provide text alternatives"
                )
            )
        
        # Report warnings for long alt text
        if images_with_long_alt:
            warning_description = f"Found {len(images_with_long_alt)} images with alt text longer than 125 characters"
            warnings.append(warning_description)
            recommendations.append("Keep alt text concise and descriptive, under 125 characters")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Long Alt Text",
                    description=warning_description,
                    severity=self.SEVERITY_LOW,
                    wcag_criterion="1.1.1 Non-text Content",
                    element_type="img",
                    remediation="Keep alt text concise and descriptive, under 125 characters"
                )
            )
        
        # Check for images that might be informational but have empty alt text
        potentially_informational_with_empty_alt = []
        for img in images_with_empty_alt:
            # Check if image is likely informational based on context or attributes
            parent_is_link = img.parent.name == 'a'
            has_dimensions = img.get('width') and int(img.get('width', 0)) > 50 and int(img.get('height', 0)) > 50
            
            if parent_is_link or has_dimensions:
                potentially_informational_with_empty_alt.append(img)
        
        if potentially_informational_with_empty_alt:
            warning_description = f"Found {len(potentially_informational_with_empty_alt)} potentially informational images with empty alt text"
            warnings.append(warning_description)
            recommendations.append("Provide descriptive alt text for informational images, especially those used as links")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Empty Alt on Informational Images",
                    description=warning_description,
                    severity=self.SEVERITY_MEDIUM,
                    wcag_criterion="1.1.1 Non-text Content",
                    element_type="img",
                    remediation="Provide descriptive alt text for informational images, especially those used as links"
                )
            )
        
        return {
            'issues': issues,
            'warnings': warnings,
            'recommendations': recommendations,
            'accessibility_issues': accessibility_issues,
            'wcag_violations': wcag_violations,
            'elements_with_issues': elements_with_issues,
            'total_elements_analyzed': total_elements_analyzed,
            'compliant_elements': compliant_elements,
            'non_compliant_elements': non_compliant_elements,
            'data': {
                'total_images': len(images),
                'images_without_alt': len(images_without_alt),
                'images_with_empty_alt': len(images_with_empty_alt),
                'images_with_long_alt': len(images_with_long_alt),
                'potentially_informational_with_empty_alt': len(potentially_informational_with_empty_alt)
            }
        }
    
    def _analyze_heading_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze heading structure for proper hierarchy.
        
        Args:
            soup: BeautifulSoup object of the HTML
            
        Returns:
            Dict with analysis results
        """
        issues = []
        warnings = []
        recommendations = []
        accessibility_issues = []
        wcag_violations = []
        
        # Find all headings
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        heading_levels = [int(h.name[1]) for h in headings]
        
        # Track elements analyzed
        total_elements_analyzed = len(headings)
        compliant_elements = 0
        non_compliant_elements = 0
        elements_with_issues = 0
        
        # No headings found
        if not headings:
            issue_description = "No heading elements (h1-h6) found"
            issues.append(issue_description)
            recommendations.append("Add proper heading elements to structure your content")
            wcag_violations.append("1.3.1")
            wcag_violations.append("2.4.6")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="No Headings",
                    description=issue_description,
                    severity=self.SEVERITY_HIGH,
                    wcag_criterion="1.3.1 Info and Relationships",
                    element_type="document",
                    remediation="Add proper heading elements to structure your content"
                )
            )
            
            # Since we have no headings, set elements_with_issues to 1 (the document as a whole)
            elements_with_issues = 1
            non_compliant_elements = 1
            
            return {
                'issues': issues,
                'warnings': warnings,
                'recommendations': recommendations,
                'accessibility_issues': accessibility_issues,
                'wcag_violations': wcag_violations,
                'elements_with_issues': elements_with_issues,
                'total_elements_analyzed': total_elements_analyzed + 1,  # +1 for document
                'compliant_elements': compliant_elements,
                'non_compliant_elements': non_compliant_elements,
                'data': {
                    'has_headings': False,
                    'has_h1': False,
                    'heading_counts': {},
                    'heading_hierarchy_issues': []
                }
            }
        
        # Check for h1 heading
        has_h1 = 1 in heading_levels
        if not has_h1:
            issue_description = "No H1 heading found"
            issues.append(issue_description)
            recommendations.append("Add an H1 heading as the main title of your content")
            wcag_violations.append("1.3.1")
            wcag_violations.append("2.4.6")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Missing H1",
                    description=issue_description,
                    severity=self.SEVERITY_HIGH,
                    wcag_criterion="1.3.1 Info and Relationships",
                    element_type="document",
                    remediation="Add an H1 heading as the main title of your content"
                )
            )
            
            elements_with_issues += 1
            non_compliant_elements += 1
        
        # Check for multiple h1 headings
        h1_count = heading_levels.count(1)
        if h1_count > 1:
            issue_description = f"Multiple H1 headings found ({h1_count})"
            issues.append(issue_description)
            recommendations.append("Use only one H1 heading per page as the main title")
            wcag_violations.append("1.3.1")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Multiple H1 Headings",
                    description=issue_description,
                    severity=self.SEVERITY_MEDIUM,
                    wcag_criterion="1.3.1 Info and Relationships",
                    element_type="h1",
                    remediation="Use only one H1 heading per page as the main title"
                )
            )
            
            elements_with_issues += h1_count - 1  # Count all but one h1 as issues
            non_compliant_elements += h1_count - 1
        
        # Check for skipped heading levels
        prev_level = 0
        skipped_levels = []
        heading_hierarchy_issues = []
        
        for i, level in enumerate(heading_levels):
            # Only flag as an issue if we skip levels going deeper
            if level > prev_level + 1 and prev_level > 0:
                issue_text = f"Skipped heading level from H{prev_level} to H{level}"
                skipped_levels.append(issue_text)
                heading_hierarchy_issues.append({
                    'issue': issue_text,
                    'position': i,
                    'level_from': prev_level,
                    'level_to': level
                })
                non_compliant_elements += 1
                elements_with_issues += 1
            else:
                compliant_elements += 1
            
            prev_level = level
        
        if skipped_levels:
            issue_description = f"Found {len(skipped_levels)} instances of skipped heading levels"
            issues.append(issue_description)
            recommendations.append("Maintain a proper heading hierarchy without skipping levels")
            wcag_violations.append("1.3.1")
            wcag_violations.append("2.4.6")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Skipped Heading Levels",
                    description=issue_description,
                    severity=self.SEVERITY_MEDIUM,
                    wcag_criterion="1.3.1 Info and Relationships",
                    element_type="headings",
                    remediation="Maintain a proper heading hierarchy without skipping levels"
                )
            )
        
        # Check for empty headings
        empty_headings = [h for h in headings if not h.get_text().strip()]
        if empty_headings:
            issue_description = f"Found {len(empty_headings)} empty heading elements"
            issues.append(issue_description)
            recommendations.append("Ensure all heading elements contain descriptive text")
            wcag_violations.append("2.4.6")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Empty Headings",
                    description=issue_description,
                    severity=self.SEVERITY_MEDIUM,
                    wcag_criterion="2.4.6 Headings and Labels",
                    element_type="headings",
                    remediation="Ensure all heading elements contain descriptive text"
                )
            )
            
            elements_with_issues += len(empty_headings)
            non_compliant_elements += len(empty_headings)
            compliant_elements -= len(empty_headings)  # Adjust count of compliant headings
        
        # Count headings by level
        heading_counts = {}
        for level in range(1, 7):
            heading_counts[f'h{level}'] = heading_levels.count(level)
        
        return {
            'issues': issues,
            'warnings': warnings,
            'recommendations': recommendations,
            'accessibility_issues': accessibility_issues,
            'wcag_violations': wcag_violations,
            'elements_with_issues': elements_with_issues,
            'total_elements_analyzed': total_elements_analyzed,
            'compliant_elements': compliant_elements,
            'non_compliant_elements': non_compliant_elements,
            'data': {
                'has_headings': True,
                'has_h1': has_h1,
                'heading_counts': heading_counts,
                'heading_hierarchy_issues': heading_hierarchy_issues,
                'empty_headings': len(empty_headings) if 'empty_headings' in locals() else 0
            }
        }
    
    def _analyze_form_labels(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze form fields for proper labeling.
        
        Args:
            soup: BeautifulSoup object of the HTML
            
        Returns:
            Dict with analysis results
        """
        issues = []
        warnings = []
        recommendations = []
        accessibility_issues = []
        wcag_violations = []
        
        # Find all forms
        forms = soup.find_all('form')
        
        # Find all input elements, including those outside of forms
        all_inputs = soup.find_all(['input', 'textarea', 'select'])
        
        # Filter out inputs that don't need labels
        form_controls = []
        for control in all_inputs:
            input_type = control.get('type', '').lower()
            # Skip hidden, button, submit, reset, and image inputs
            if input_type not in ['hidden', 'button', 'submit', 'reset', 'image']:
                form_controls.append(control)
        
        # Track elements analyzed
        total_elements_analyzed = len(form_controls)
        compliant_elements = 0
        non_compliant_elements = 0
        elements_with_issues = 0
        
        # No form controls found
        if not form_controls:
            return {
                'issues': issues,
                'warnings': warnings,
                'recommendations': recommendations,
                'accessibility_issues': accessibility_issues,
                'wcag_violations': wcag_violations,
                'elements_with_issues': 0,
                'total_elements_analyzed': 0,
                'compliant_elements': 0,
                'non_compliant_elements': 0,
                'data': {
                    'has_forms': len(forms) > 0,
                    'form_count': len(forms),
                    'unlabeled_controls': 0,
                    'labeled_controls': 0,
                    'controls_with_placeholder_only': 0
                }
            }
        
        # Check each form control for proper labeling
        unlabeled_controls = []
        controls_with_placeholder_only = []
        
        for control in form_controls:
            # Check for explicit label
            control_id = control.get('id')
            has_explicit_label = False
            
            if control_id:
                label = soup.find('label', attrs={'for': control_id})
                has_explicit_label = bool(label) and bool(label.get_text().strip())
            
            # Check for implicit label (control inside label)
            has_implicit_label = False
            parent_label = control.find_parent('label')
            has_implicit_label = bool(parent_label) and bool(parent_label.get_text().strip())
            
            # Check for ARIA labeling
            has_aria_label = bool(control.get('aria-label'))
            has_aria_labelledby = bool(control.get('aria-labelledby'))
            
            # Check for title attribute
            has_title = bool(control.get('title'))
            
            # Check for placeholder only
            has_placeholder = bool(control.get('placeholder'))
            
            # Determine if properly labeled
            is_properly_labeled = (
                has_explicit_label or 
                has_implicit_label or 
                has_aria_label or 
                has_aria_labelledby
            )
            
            # Fall back to title attribute if no other labeling
            if not is_properly_labeled and has_title:
                is_properly_labeled = True
                recommendations.append(
                    "Use explicit labels instead of title attributes for form controls"
                )
            
            # Check for placeholder-only labeling
            if not is_properly_labeled and has_placeholder:
                controls_with_placeholder_only.append(control)
            
            if is_properly_labeled:
                compliant_elements += 1
            else:
                non_compliant_elements += 1
                elements_with_issues += 1
                unlabeled_controls.append(control)
        
        # Report issues for unlabeled controls
        if unlabeled_controls:
            issue_description = f"Found {len(unlabeled_controls)} form controls without labels"
            issues.append(issue_description)
            recommendations.append("Add labels to all form controls for screen reader accessibility")
            wcag_violations.append("1.3.1")
            wcag_violations.append("3.3.2")
            wcag_violations.append("4.1.2")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Missing Form Labels",
                    description=issue_description,
                    severity=self.SEVERITY_HIGH,
                    wcag_criterion="1.3.1 Info and Relationships",
                    element_type="form controls",
                    remediation="Add proper labels to all form controls using the label element with a for attribute or ARIA attributes"
                )
            )
        
        # Report issues for controls with only placeholder text
        if controls_with_placeholder_only:
            issue_description = f"Found {len(controls_with_placeholder_only)} form controls with placeholder text but no label"
            warnings.append(issue_description)
            recommendations.append("Don't rely only on placeholder text to label form controls")
            wcag_violations.append("3.3.2")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Placeholder as Label",
                    description=issue_description,
                    severity=self.SEVERITY_MEDIUM,
                    wcag_criterion="3.3.2 Labels or Instructions",
                    element_type="form controls",
                    remediation="Use proper labels in addition to placeholder text for form controls"
                )
            )
        
        # Check for required inputs without indication
        required_inputs_without_indication = []
        for control in form_controls:
            is_required = control.get('required') is not None or control.get('aria-required') == 'true'
            has_required_indicator = False
            
            # Check for label with * or "required" text
            control_id = control.get('id')
            if control_id:
                label = soup.find('label', attrs={'for': control_id})
                if label:
                    label_text = label.get_text().strip().lower()
                    has_required_indicator = '*' in label_text or 'required' in label_text
            
            if is_required and not has_required_indicator:
                required_inputs_without_indication.append(control)
        
        if required_inputs_without_indication:
            warning_description = f"Found {len(required_inputs_without_indication)} required form controls without visual indication"
            warnings.append(warning_description)
            recommendations.append("Clearly indicate required form fields (e.g., with an asterisk *)")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Required Field Indication",
                    description=warning_description,
                    severity=self.SEVERITY_LOW,
                    wcag_criterion="3.3.2 Labels or Instructions",
                    element_type="form controls",
                    remediation="Clearly indicate required form fields (e.g., with an asterisk *)"
                )
            )
        
        return {
            'issues': issues,
            'warnings': warnings,
            'recommendations': recommendations,
            'accessibility_issues': accessibility_issues,
            'wcag_violations': wcag_violations,
            'elements_with_issues': elements_with_issues,
            'total_elements_analyzed': total_elements_analyzed,
            'compliant_elements': compliant_elements,
            'non_compliant_elements': non_compliant_elements,
            'data': {
                'has_forms': len(forms) > 0,
                'form_count': len(forms),
                'unlabeled_controls': len(unlabeled_controls),
                'labeled_controls': compliant_elements,
                'controls_with_placeholder_only': len(controls_with_placeholder_only),
                'required_controls_without_indication': len(required_inputs_without_indication) if 'required_inputs_without_indication' in locals() else 0
            }
        }
    
    def _analyze_document_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze document structure for proper semantic elements.
        
        Args:
            soup: BeautifulSoup object of the HTML
            
        Returns:
            Dict with analysis results
        """
        issues = []
        warnings = []
        recommendations = []
        accessibility_issues = []
        wcag_violations = []
        
        # Check for semantic elements
        semantic_elements = [
            'header', 'nav', 'main', 'article', 'section', 'aside', 'footer',
            'figure', 'figcaption', 'time', 'mark', 'details', 'summary'
        ]
        
        found_semantic_elements = {}
        for element in semantic_elements:
            found_elements = soup.find_all(element)
            found_semantic_elements[element] = len(found_elements)
        
        # Check for main element
        has_main = found_semantic_elements.get('main', 0) > 0
        
        # Check for nav element
        has_nav = found_semantic_elements.get('nav', 0) > 0
        
        # Check for header/footer elements
        has_header = found_semantic_elements.get('header', 0) > 0
        has_footer = found_semantic_elements.get('footer', 0) > 0
        
        # Track elements analyzed
        total_elements_analyzed = 1  # document as a whole
        compliant_elements = 0
        non_compliant_elements = 0
        elements_with_issues = 0
        
        # Missing main element
        if not has_main:
            issue_description = "No main element found to identify the primary content"
            warnings.append(issue_description)
            recommendations.append("Add a main element to identify the primary content of the page")
            wcag_violations.append("1.3.1")
            wcag_violations.append("2.4.1")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Missing Main Element",
                    description=issue_description,
                    severity=self.SEVERITY_MEDIUM,
                    wcag_criterion="1.3.1 Info and Relationships",
                    element_type="document",
                    remediation="Add a main element to identify the primary content of the page"
                )
            )
            
            elements_with_issues += 1
            non_compliant_elements += 1
        else:
            compliant_elements += 1
        
        # Check for too many main elements
        main_count = found_semantic_elements.get('main', 0)
        if main_count > 1:
            issue_description = f"Multiple main elements found ({main_count})"
            issues.append(issue_description)
            recommendations.append("Use only one main element per page")
            wcag_violations.append("1.3.1")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Multiple Main Elements",
                    description=issue_description,
                    severity=self.SEVERITY_HIGH,
                    wcag_criterion="1.3.1 Info and Relationships",
                    element_type="main",
                    remediation="Use only one main element per page"
                )
            )
            
            elements_with_issues += main_count - 1
            non_compliant_elements += main_count - 1
            compliant_elements -= main_count - 1
        
        # Check for landmark elements
        found_landmarks = {
            'banner': has_header,
            'navigation': has_nav,
            'main': has_main,
            'contentinfo': has_footer
        }
        
        # Check elements with ARIA landmark roles
        for role in ['banner', 'navigation', 'main', 'contentinfo', 'search', 'complementary']:
            elements_with_role = soup.find_all(attrs={"role": role})
            if elements_with_role:
                found_landmarks[role] = True
        
        # Missing navigation landmarks
        if not found_landmarks.get('navigation', False):
            warning_description = "No navigation landmark found (nav element or role='navigation')"
            warnings.append(warning_description)
            recommendations.append("Add a nav element or role='navigation' to identify navigation links")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Missing Navigation Landmark",
                    description=warning_description,
                    severity=self.SEVERITY_LOW,
                    wcag_criterion="1.3.1 Info and Relationships",
                    element_type="document",
                    remediation="Add a nav element or role='navigation' to identify navigation links"
                )
            )
            
            total_elements_analyzed += 1
            non_compliant_elements += 1
            elements_with_issues += 1
        
        # Check for skip links
        skip_links = soup.find_all('a', href=lambda href: href and href.startswith('#') and (
            'skip' in href.lower() or 'jump' in href.lower() or 'content' in href.lower()
        ))
        
        has_skip_link = len(skip_links) > 0
        
        if not has_skip_link:
            warning_description = "No skip navigation link found"
            warnings.append(warning_description)
            recommendations.append("Add a skip navigation link at the beginning of the page")
            wcag_violations.append("2.4.1")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Missing Skip Link",
                    description=warning_description,
                    severity=self.SEVERITY_MEDIUM,
                    wcag_criterion="2.4.1 Bypass Blocks",
                    element_type="document",
                    remediation="Add a skip navigation link at the beginning of the page"
                )
            )
            
            total_elements_analyzed += 1
            non_compliant_elements += 1
            elements_with_issues += 1
        
        # Check for excessive div usage where semantic elements would be appropriate
        divs = soup.find_all('div')
        div_with_id_class = [div for div in divs if div.get('id') or div.get('class')]
        semantic_div_candidates = []
        
        for div in div_with_id_class:
            id_value = div.get('id', '').lower()
            class_value = ' '.join(div.get('class', [])).lower()
            
            # Look for divs that should likely be semantic elements
            if any(term in id_value or term in class_value for term in ['header', 'head', 'banner', 'top']):
                semantic_div_candidates.append({'div': div, 'suggested': 'header'})
            elif any(term in id_value or term in class_value for term in ['footer', 'foot', 'bottom']):
                semantic_div_candidates.append({'div': div, 'suggested': 'footer'})
            elif any(term in id_value or term in class_value for term in ['nav', 'menu', 'navigation']):
                semantic_div_candidates.append({'div': div, 'suggested': 'nav'})
            elif any(term in id_value or term in class_value for term in ['main', 'content']):
                semantic_div_candidates.append({'div': div, 'suggested': 'main'})
            elif any(term in id_value or term in class_value for term in ['article', 'post']):
                semantic_div_candidates.append({'div': div, 'suggested': 'article'})
            elif any(term in id_value or term in class_value for term in ['section']):
                semantic_div_candidates.append({'div': div, 'suggested': 'section'})
            elif any(term in id_value or term in class_value for term in ['sidebar', 'complementary', 'aside']):
                semantic_div_candidates.append({'div': div, 'suggested': 'aside'})
        
        if semantic_div_candidates:
            warning_description = f"Found {len(semantic_div_candidates)} divs that could be replaced with semantic HTML5 elements"
            warnings.append(warning_description)
            recommendations.append("Replace divs with appropriate semantic elements (header, nav, main, article, section, aside, footer)")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Non-semantic Structure",
                    description=warning_description,
                    severity=self.SEVERITY_LOW,
                    wcag_criterion="1.3.1 Info and Relationships",
                    element_type="div",
                    remediation="Replace divs with appropriate semantic elements (header, nav, main, article, section, aside, footer)"
                )
            )
            
            # Don't count these in the elements_with_issues as they're advisory
        
        # Check for proper page title
        title_tag = soup.find('title')
        has_title = title_tag and title_tag.string and title_tag.string.strip()
        
        if not has_title:
            issue_description = "Missing page title"
            issues.append(issue_description)
            recommendations.append("Add a descriptive title element to the page")
            wcag_violations.append("2.4.2")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Missing Page Title",
                    description=issue_description,
                    severity=self.SEVERITY_HIGH,
                    wcag_criterion="2.4.2 Page Titled",
                    element_type="title",
                    remediation="Add a descriptive title element to the page"
                )
            )
            
            total_elements_analyzed += 1
            non_compliant_elements += 1
            elements_with_issues += 1
        else:
            total_elements_analyzed += 1
            compliant_elements += 1
        
        return {
            'issues': issues,
            'warnings': warnings,
            'recommendations': recommendations,
            'accessibility_issues': accessibility_issues,
            'wcag_violations': wcag_violations,
            'elements_with_issues': elements_with_issues,
            'total_elements_analyzed': total_elements_analyzed,
            'compliant_elements': compliant_elements,
            'non_compliant_elements': non_compliant_elements,
            'data': {
                'has_main': has_main,
                'has_nav': has_nav,
                'has_header': has_header,
                'has_footer': has_footer,
                'has_skip_link': has_skip_link,
                'has_title': has_title,
                'semantic_elements': found_semantic_elements,
                'potential_semantic_elements': len(semantic_div_candidates)
            }
        }
    
    def _analyze_aria_roles(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze ARIA roles and attributes for proper usage.
        
        Args:
            soup: BeautifulSoup object of the HTML
            
        Returns:
            Dict with analysis results
        """
        issues = []
        warnings = []
        recommendations = []
        accessibility_issues = []
        wcag_violations = []
        
        # Find all elements with ARIA attributes
        elements_with_aria = []
        for element in soup.find_all():
            has_aria = False
            for attr in element.attrs:
                if attr == 'role' or attr.startswith('aria-'):
                    has_aria = True
                    elements_with_aria.append({
                        'element': element,
                        'name': element.name,
                        'attribute': attr,
                        'value': element[attr]
                    })
        
        # Valid ARIA roles
        valid_roles = {
            'alert', 'alertdialog', 'application', 'article', 'banner', 'button',
            'cell', 'checkbox', 'columnheader', 'combobox', 'complementary',
            'contentinfo', 'definition', 'dialog', 'directory', 'document',
            'feed', 'figure', 'form', 'grid', 'gridcell', 'group', 'heading',
            'img', 'link', 'list', 'listbox', 'listitem', 'log', 'main',
            'marquee', 'math', 'menu', 'menubar', 'menuitem', 'menuitemcheckbox',
            'menuitemradio', 'navigation', 'none', 'note', 'option', 'presentation',
            'progressbar', 'radio', 'radiogroup', 'region', 'row', 'rowgroup',
            'rowheader', 'scrollbar', 'search', 'searchbox', 'separator',
            'slider', 'spinbutton', 'status', 'switch', 'tab', 'table',
            'tablist', 'tabpanel', 'term', 'textbox', 'timer', 'toolbar',
            'tooltip', 'tree', 'treegrid', 'treeitem'
        }
        
        # Track elements analyzed
        total_elements_analyzed = len(elements_with_aria)
        compliant_elements = 0
        non_compliant_elements = 0
        elements_with_issues = 0
        
        # No ARIA elements found
        if not elements_with_aria:
            # Not necessarily an issue, just return empty data
            return {
                'issues': issues,
                'warnings': warnings,
                'recommendations': recommendations,
                'accessibility_issues': accessibility_issues,
                'wcag_violations': wcag_violations,
                'elements_with_issues': 0,
                'total_elements_analyzed': 0,
                'compliant_elements': 0,
                'non_compliant_elements': 0,
                'data': {
                    'has_aria': False,
                    'aria_count': 0,
                    'invalid_roles': 0,
                    'missing_required_attributes': 0
                }
            }
        
        # Check for invalid roles
        elements_with_invalid_roles = []
        
        for item in elements_with_aria:
            if item['attribute'] == 'role' and item['value'] not in valid_roles:
                elements_with_invalid_roles.append(item)
        
        if elements_with_invalid_roles:
            issue_description = f"Found {len(elements_with_invalid_roles)} elements with invalid ARIA roles"
            issues.append(issue_description)
            recommendations.append("Use only valid ARIA roles as defined in the ARIA specification")
            wcag_violations.append("4.1.2")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Invalid ARIA Roles",
                    description=issue_description,
                    severity=self.SEVERITY_HIGH,
                    wcag_criterion="4.1.2 Name, Role, Value",
                    element_type="elements with ARIA",
                    remediation="Use only valid ARIA roles as defined in the ARIA specification"
                )
            )
            
            elements_with_issues += len(elements_with_invalid_roles)
            non_compliant_elements += len(elements_with_invalid_roles)
        
        # Check for required ARIA attributes
        elements_missing_required_attributes = []
        
        # Required attributes for common roles
        role_required_attributes = {
            'checkbox': ['aria-checked'],
            'combobox': ['aria-expanded'],
            'slider': ['aria-valuenow'],
            'scrollbar': ['aria-valuenow', 'aria-valuemin', 'aria-valuemax'],
            'textbox': []  # No required attributes, but commonly needs aria-label or aria-labelledby
        }
        
        for item in elements_with_aria:
            if item['attribute'] == 'role' and item['value'] in role_required_attributes:
                required_attrs = role_required_attributes[item['value']]
                missing_attrs = []
                
                for attr in required_attrs:
                    if not item['element'].has_attr(attr):
                        missing_attrs.append(attr)
                
                if missing_attrs:
                    elements_missing_required_attributes.append({
                        'element': item['element'],
                        'role': item['value'],
                        'missing_attrs': missing_attrs
                    })
        
        if elements_missing_required_attributes:
            issue_description = f"Found {len(elements_missing_required_attributes)} elements with ARIA roles missing required attributes"
            issues.append(issue_description)
            recommendations.append("Include all required ARIA attributes for each ARIA role")
            wcag_violations.append("4.1.2")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Missing Required ARIA Attributes",
                    description=issue_description,
                    severity=self.SEVERITY_HIGH,
                    wcag_criterion="4.1.2 Name, Role, Value",
                    element_type="elements with ARIA",
                    remediation="Include all required ARIA attributes for each ARIA role"
                )
            )
            
            elements_with_issues += len(elements_missing_required_attributes)
            non_compliant_elements += len(elements_missing_required_attributes)
        
        # Check for redundant roles (elements with default implicit roles)
        redundant_roles = {
            'button': 'button',
            'a': 'link',
            'h1': 'heading',
            'h2': 'heading',
            'h3': 'heading',
            'h4': 'heading',
            'h5': 'heading',
            'h6': 'heading',
            'input[type="checkbox"]': 'checkbox',
            'input[type="radio"]': 'radio',
            'input[type="text"]': 'textbox',
            'textarea': 'textbox',
            'select': 'listbox',
            'nav': 'navigation',
            'main': 'main',
            'header': 'banner',
            'footer': 'contentinfo',
            'aside': 'complementary',
            'form': 'form',
            'img': 'img',
            'ul': 'list',
            'ol': 'list',
            'li': 'listitem',
            'table': 'table',
            'tr': 'row',
            'td': 'cell',
            'th': 'columnheader'
        }
        
        elements_with_redundant_roles = []
        
        for item in elements_with_aria:
            if item['attribute'] == 'role':
                element_key = item['name']
                
                # Handle input elements with type
                if element_key == 'input' and item['element'].has_attr('type'):
                    element_key = f'input[type="{item["element"]["type"]}"]'
                
                if element_key in redundant_roles and item['value'] == redundant_roles[element_key]:
                    elements_with_redundant_roles.append(item)
        
        if elements_with_redundant_roles:
            warning_description = f"Found {len(elements_with_redundant_roles)} elements with redundant ARIA roles"
            warnings.append(warning_description)
            recommendations.append("Avoid using redundant ARIA roles that match the element's implicit role")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Redundant ARIA Roles",
                    description=warning_description,
                    severity=self.SEVERITY_LOW,
                    wcag_criterion="4.1.2 Name, Role, Value",
                    element_type="elements with ARIA",
                    remediation="Avoid using redundant ARIA roles that match the element's implicit role"
                )
            )
        
        # Calculate compliant elements
        compliant_elements = total_elements_analyzed - non_compliant_elements
        
        return {
            'issues': issues,
            'warnings': warnings,
            'recommendations': recommendations,
            'accessibility_issues': accessibility_issues,
            'wcag_violations': wcag_violations,
            'elements_with_issues': elements_with_issues,
            'total_elements_analyzed': total_elements_analyzed,
            'compliant_elements': compliant_elements,
            'non_compliant_elements': non_compliant_elements,
            'data': {
                'has_aria': True,
                'aria_count': len(elements_with_aria),
                'invalid_roles': len(elements_with_invalid_roles),
                'missing_required_attributes': len(elements_missing_required_attributes),
                'redundant_roles': len(elements_with_redundant_roles) if 'elements_with_redundant_roles' in locals() else 0
            }
        }
    
    def _analyze_keyboard_navigation(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze keyboard navigation accessibility.
        
        Args:
            soup: BeautifulSoup object of the HTML
            
        Returns:
            Dict with analysis results
        """
        issues = []
        warnings = []
        recommendations = []
        accessibility_issues = []
        wcag_violations = []
        
        # Find elements that might interfere with keyboard navigation
        positive_tabindex_elements = soup.find_all(lambda tag: tag.has_attr('tabindex') and tag['tabindex'].isdigit() and int(tag['tabindex']) > 0)
        
        # Find elements with tabindex=-1 that should be focusable
        negative_tabindex_elements = soup.find_all(lambda tag: tag.has_attr('tabindex') and tag['tabindex'] == '-1' and 
                                                 tag.name in ['a', 'button', 'input', 'select', 'textarea'])
        
        # Find potentially interactive elements with event handlers that might not be keyboard accessible
        elements_with_click_handlers = []
        for element in soup.find_all():
            has_click_handler = any(attr.startswith('on') and attr.lower() != 'onfocus' and attr.lower() != 'onblur' for attr in element.attrs)
            is_not_natively_interactive = element.name not in ['a', 'button', 'input', 'select', 'textarea']
            has_no_tabindex = not element.has_attr('tabindex')
            
            if has_click_handler and is_not_natively_interactive and has_no_tabindex:
                elements_with_click_handlers.append(element)
        
        # Track elements analyzed
        total_elements_analyzed = len(positive_tabindex_elements) + len(negative_tabindex_elements) + len(elements_with_click_handlers)
        compliant_elements = 0
        non_compliant_elements = 0
        elements_with_issues = 0
        
        # No issues found
        if total_elements_analyzed == 0:
            return {
                'issues': issues,
                'warnings': warnings,
                'recommendations': recommendations,
                'accessibility_issues': accessibility_issues,
                'wcag_violations': wcag_violations,
                'elements_with_issues': 0,
                'total_elements_analyzed': 0,
                'compliant_elements': 0,
                'non_compliant_elements': 0,
                'data': {
                    'has_positive_tabindex': False,
                    'has_negative_tabindex_on_interactive': False,
                    'has_inaccessible_click_handlers': False
                }
            }
        
        # Check for positive tabindex values
        if positive_tabindex_elements:
            issue_description = f"Found {len(positive_tabindex_elements)} elements with positive tabindex values"
            issues.append(issue_description)
            recommendations.append("Avoid using positive tabindex values which disrupt natural tab order")
            wcag_violations.append("2.4.3")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Positive Tabindex",
                    description=issue_description,
                    severity=self.SEVERITY_HIGH,
                    wcag_criterion="2.4.3 Focus Order",
                    element_type="element with tabindex",
                    remediation="Remove positive tabindex values or replace with tabindex='0'"
                )
            )
            
            elements_with_issues += len(positive_tabindex_elements)
            non_compliant_elements += len(positive_tabindex_elements)
        
        # Check for negative tabindex on interactive elements
        if negative_tabindex_elements:
            issue_description = f"Found {len(negative_tabindex_elements)} interactive elements with tabindex=-1 (removed from tab order)"
            issues.append(issue_description)
            recommendations.append("Avoid removing naturally focusable elements from the tab order with tabindex=-1")
            wcag_violations.append("2.1.1")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Interactive Elements Removed from Tab Order",
                    description=issue_description,
                    severity=self.SEVERITY_HIGH,
                    wcag_criterion="2.1.1 Keyboard",
                    element_type="interactive element",
                    remediation="Remove tabindex=-1 from interactive elements or ensure they're accessible by other means"
                )
            )
            
            elements_with_issues += len(negative_tabindex_elements)
            non_compliant_elements += len(negative_tabindex_elements)
        
        # Check for inaccessible click handlers
        if elements_with_click_handlers:
            issue_description = f"Found {len(elements_with_click_handlers)} non-interactive elements with click handlers but no keyboard access"
            issues.append(issue_description)
            recommendations.append("Add tabindex='0' and keyboard event handlers to non-interactive elements with click handlers")
            wcag_violations.append("2.1.1")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Inaccessible Click Handlers",
                    description=issue_description,
                    severity=self.SEVERITY_HIGH,
                    wcag_criterion="2.1.1 Keyboard",
                    element_type="element with click handler",
                    remediation="Add tabindex='0' and keyboard event handlers to elements with click handlers"
                )
            )
            
            elements_with_issues += len(elements_with_click_handlers)
            non_compliant_elements += len(elements_with_click_handlers)
        
        # Detect potential keyboard traps
        potential_keyboard_traps = []
        
        # Look for elements that might create keyboard traps
        for element in soup.find_all():
            # Check for a combination of tabindex and event handlers that might create traps
            has_tabindex = element.has_attr('tabindex')
            has_keyboard_handlers = any(attr in element.attrs for attr in ['onkeydown', 'onkeypress', 'onkeyup'])
            
            if has_tabindex and has_keyboard_handlers:
                potential_keyboard_traps.append(element)
        
        if potential_keyboard_traps:
            warning_description = f"Found {len(potential_keyboard_traps)} elements that might create keyboard traps"
            warnings.append(warning_description)
            recommendations.append("Ensure elements with keyboard event handlers don't trap keyboard focus")
            wcag_violations.append("2.1.2")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Potential Keyboard Traps",
                    description=warning_description,
                    severity=self.SEVERITY_MEDIUM,
                    wcag_criterion="2.1.2 No Keyboard Trap",
                    element_type="element with keyboard handlers",
                    remediation="Ensure users can navigate away from elements using standard keyboard controls"
                )
            )
        
        # Calculate compliant elements
        compliant_elements = total_elements_analyzed - non_compliant_elements
        
        return {
            'issues': issues,
            'warnings': warnings,
            'recommendations': recommendations,
            'accessibility_issues': accessibility_issues,
            'wcag_violations': wcag_violations,
            'elements_with_issues': elements_with_issues,
            'total_elements_analyzed': total_elements_analyzed,
            'compliant_elements': compliant_elements,
            'non_compliant_elements': non_compliant_elements,
            'data': {
                'has_positive_tabindex': len(positive_tabindex_elements) > 0,
                'has_negative_tabindex_on_interactive': len(negative_tabindex_elements) > 0,
                'has_inaccessible_click_handlers': len(elements_with_click_handlers) > 0,
                'potential_keyboard_traps': len(potential_keyboard_traps) if 'potential_keyboard_traps' in locals() else 0
            }
        }
    
    def _analyze_color_contrast(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze color contrast for text elements.
        
        Args:
            soup: BeautifulSoup object of the HTML
            
        Returns:
            Dict with analysis results
        """
        issues = []
        warnings = []
        recommendations = []
        accessibility_issues = []
        wcag_violations = []
        
        # Find elements with inline color styles
        elements_with_color_style = soup.find_all(lambda tag: tag.has_attr('style') and 
                                               ('color:' in tag['style'].lower() or 
                                                'background-color:' in tag['style'].lower()))
        
        # Count elements that might have contrast issues (simplified approach)
        potential_contrast_issues = []
        
        for element in elements_with_color_style:
            style = element.get('style', '').lower()
            has_text_color = 'color:' in style
            has_background_color = 'background-color:' in style
            
            # Elements with text color but no background might have contrast issues
            if has_text_color and not has_background_color:
                potential_contrast_issues.append(element)
            
            # Elements with background color but no text color might have contrast issues
            if has_background_color and not has_text_color:
                potential_contrast_issues.append(element)
        
        # Find elements with classes that might relate to color
        color_related_classes = []
        for element in soup.find_all(class_=True):
            classes = element.get('class', [])
            for cls in classes:
                if any(term in cls.lower() for term in ['color', 'bg', 'background', 'dark', 'light', 'text', 'theme']):
                    color_related_classes.append(element)
                    break
        
        # Track elements analyzed
        total_elements_analyzed = len(elements_with_color_style) + len(color_related_classes)
        compliant_elements = 0
        non_compliant_elements = 0
        elements_with_issues = 0
        
        # No color styling found
        if total_elements_analyzed == 0:
            return {
                'issues': issues,
                'warnings': warnings,
                'recommendations': recommendations,
                'accessibility_issues': accessibility_issues,
                'wcag_violations': wcag_violations,
                'elements_with_issues': 0,
                'total_elements_analyzed': 0,
                'compliant_elements': 0,
                'non_compliant_elements': 0,
                'data': {
                    'elements_with_color_style': 0,
                    'potential_contrast_issues': 0,
                    'color_related_classes': 0
                }
            }
        
        # Count how many elements might have color contrast issues
        if potential_contrast_issues:
            warning_description = f"Found {len(potential_contrast_issues)} elements with potential color contrast issues"
            warnings.append(warning_description)
            recommendations.append("Ensure text color has sufficient contrast with background color (at least 4.5:1 ratio)")
            wcag_violations.append("1.4.3")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Potential Color Contrast Issues",
                    description=warning_description,
                    severity=self.SEVERITY_MEDIUM,
                    wcag_criterion="1.4.3 Contrast (Minimum)",
                    element_type="text elements",
                    remediation="Ensure text color has sufficient contrast with background color (at least 4.5:1 ratio)"
                )
            )
            
            elements_with_issues += len(potential_contrast_issues)
            non_compliant_elements += len(potential_contrast_issues)
        
        # Warning about color-related classes
        if color_related_classes:
            classes_count = len(color_related_classes)
            warning_description = f"Found {classes_count} elements with classes that might affect color styling"
            warnings.append(warning_description)
            recommendations.append("Verify contrast of text elements styled via CSS classes")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="CSS Color Classes",
                    description=warning_description,
                    severity=self.SEVERITY_LOW,
                    wcag_criterion="1.4.3 Contrast (Minimum)",
                    element_type="elements with color classes",
                    remediation="Verify contrast of text elements styled via CSS classes meets WCAG requirements"
                )
            )
        
        # Check for color used as the only means of conveying information
        color_only_elements = []
        
        # Look for common patterns where color might be the only indicator
        for element in soup.find_all():
            classes = ' '.join(element.get('class', []))
            id_value = element.get('id', '')
            
            # Check for common color-only indicators in classes or IDs
            if any(term in classes.lower() or term in id_value.lower() 
                  for term in ['success', 'error', 'warning', 'info', 'alert']):
                
                # If the element has text content, it's likely not using color alone
                if not element.get_text().strip():
                    color_only_elements.append(element)
        
        if color_only_elements:
            warning_description = f"Found {len(color_only_elements)} elements that might use color as the only means of conveying information"
            warnings.append(warning_description)
            recommendations.append("Don't rely on color alone to convey information; add text, patterns, or icons")
            wcag_violations.append("1.4.1")
            
            accessibility_issues.append(
                AccessibilityIssue(
                    name="Color Only Information",
                    description=warning_description,
                    severity=self.SEVERITY_MEDIUM,
                    wcag_criterion="1.4.1 Use of Color",
                    element_type="elements with color-only indicators",
                    remediation="Don't rely on color alone to convey information; add text, patterns, or icons"
                )
            )
            
            elements_with_issues += len(color_only_elements)
            non_compliant_elements += len(color_only_elements)
        
        # Calculate compliant elements
        compliant_elements = total_elements_analyzed - non_compliant_elements
        
        return {
            'issues': issues,
            'warnings': warnings,
            'recommendations': recommendations,
            'accessibility_issues': accessibility_issues,
            'wcag_violations': wcag_violations,
            'elements_with_issues': elements_with_issues,
            'total_elements_analyzed': total_elements_analyzed,
            'compliant_elements': compliant_elements,
            'non_compliant_elements': non_compliant_elements,
            'data': {
                'elements_with_color_style': len(elements_with_color_style),
                'potential_contrast_issues': len(potential_contrast_issues),
                'color_related_classes': len(color_related_classes),
                'color_only_elements': len(color_only_elements) if 'color_only_elements' in locals() else 0
            }
        } 