"""Schema.org analyzer implementation."""

from typing import Dict, Any, Optional, List, Set, Tuple
from bs4 import BeautifulSoup
import json
import re
import urllib.parse
from dataclasses import dataclass

from .base import BaseAnalyzer, AnalysisResult, InputType, OutputType

@dataclass
class SchemaIssue:
    """Schema.org issue found during analysis."""
    name: str
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    schema_type: str  # The schema.org type affected
    location: str  # Where in the document the issue was found
    remediation: str

class SchemaAnalyzer(BaseAnalyzer[str, Dict[str, Any]]):
    """Analyzer for Schema.org structured data.
    
    This analyzer examines JSON-LD, Microdata, and RDFa formats of Schema.org
    structured data, validating their implementation and providing recommendations
    for improvement.
    """
    
    # Severity levels for schema issues
    SEVERITY_CRITICAL = "critical"
    SEVERITY_HIGH = "high"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_LOW = "low"
    
    # Common schema.org types with required properties
    COMMON_SCHEMA_TYPES = {
        "Article": ["headline", "author", "datePublished"],
        "BlogPosting": ["headline", "author", "datePublished"],
        "NewsArticle": ["headline", "author", "datePublished"],
        "Product": ["name", "offers"],
        "LocalBusiness": ["name", "address"],
        "Organization": ["name"],
        "Person": ["name"],
        "WebPage": ["name"],
        "Event": ["name", "startDate"],
        "Recipe": ["name", "recipeIngredient", "recipeInstructions"],
        "Review": ["reviewRating", "itemReviewed"],
        "FAQPage": ["mainEntity"],
        "HowTo": ["name", "step"],
        "BreadcrumbList": ["itemListElement"]
    }
    
    # Property requirements for specific schema types
    PROPERTY_REQUIREMENTS = {
        "Product": {
            "required": ["name", "offers"],
            "recommended": ["image", "description", "brand", "aggregateRating", "review"]
        },
        "Article": {
            "required": ["headline", "author", "datePublished"],
            "recommended": ["image", "dateModified", "publisher"]
        },
        "LocalBusiness": {
            "required": ["name", "address"],
            "recommended": ["telephone", "openingHours", "geo", "image", "priceRange"]
        }
        # More can be added as needed
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the schema analyzer.
        
        Args:
            config: Optional configuration dictionary that may include:
                - check_jsonld: Whether to check JSON-LD format (default: True)
                - check_microdata: Whether to check Microdata format (default: True)
                - check_rdfa: Whether to check RDFa format (default: True)
                - check_required_props: Whether to check required properties (default: True)
                - check_recommended_props: Whether to check recommended properties (default: True)
                - check_context: Whether to check schema.org context (default: True)
                - issue_weight_critical: Weight for critical severity issues (default: 0.4)
                - issue_weight_high: Weight for high severity issues (default: 0.3)
                - issue_weight_medium: Weight for medium severity issues (default: 0.2)
                - issue_weight_low: Weight for low severity issues (default: 0.1)
                - custom_schema_types: Additional schema types to check
                - custom_property_requirements: Additional property requirements for schema types
        """
        super().__init__(config)
        
        # Configure which checks to run
        self.check_jsonld = self.config.get('check_jsonld', True)
        self.check_microdata = self.config.get('check_microdata', True)
        self.check_rdfa = self.config.get('check_rdfa', True)
        self.check_required_props = self.config.get('check_required_props', True)
        self.check_recommended_props = self.config.get('check_recommended_props', True)
        self.check_context = self.config.get('check_context', True)
        
        # Configure issue weights for scoring
        self.issue_weight_critical = self.config.get('issue_weight_critical', 0.4)
        self.issue_weight_high = self.config.get('issue_weight_high', 0.3)
        self.issue_weight_medium = self.config.get('issue_weight_medium', 0.2)
        self.issue_weight_low = self.config.get('issue_weight_low', 0.1)
        
        # Extend schema types if provided
        if 'custom_schema_types' in self.config:
            self.COMMON_SCHEMA_TYPES.update(self.config['custom_schema_types'])
            
        # Extend property requirements if provided
        if 'custom_property_requirements' in self.config:
            self.PROPERTY_REQUIREMENTS.update(self.config['custom_property_requirements'])
            
    def analyze(self, html_content: str) -> AnalysisResult[Dict[str, Any]]:
        """Analyze the webpage for Schema.org structured data.
        
        Args:
            html_content: HTML content to analyze
            
        Returns:
            AnalysisResult containing schema analysis data
            
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
            schema_issues = []
            
            # Initialize analysis data
            analysis_data = {
                'has_schema_markup': False,
                'schema_score': 100,
                'critical_severity_issues': 0,
                'high_severity_issues': 0,
                'medium_severity_issues': 0,
                'low_severity_issues': 0,
                'schema_issues': [],
                'detected_formats': [],
                'detected_types': [],
                'jsonld_count': 0,
                'microdata_count': 0,
                'rdfa_count': 0,
                'total_schema_items': 0,
                'valid_schema_items': 0,
                'invalid_schema_items': 0,
            }
            
            # Run enabled schema checks
            if self.check_jsonld:
                jsonld_results = self._analyze_jsonld(soup)
                self._merge_results(jsonld_results, issues, warnings, recommendations, schema_issues)
                analysis_data['jsonld_count'] = jsonld_results.get('jsonld_count', 0)
                if jsonld_results.get('has_jsonld', False):
                    analysis_data['detected_formats'].append('JSON-LD')
                analysis_data['detected_types'].extend(jsonld_results.get('detected_types', []))
                analysis_data['valid_schema_items'] += jsonld_results.get('valid_jsonld', 0)
                analysis_data['invalid_schema_items'] += jsonld_results.get('invalid_jsonld', 0)
            
            if self.check_microdata:
                microdata_results = self._analyze_microdata(soup)
                self._merge_results(microdata_results, issues, warnings, recommendations, schema_issues)
                analysis_data['microdata_count'] = microdata_results.get('microdata_count', 0)
                if microdata_results.get('has_microdata', False):
                    analysis_data['detected_formats'].append('Microdata')
                analysis_data['detected_types'].extend(microdata_results.get('detected_types', []))
                analysis_data['valid_schema_items'] += microdata_results.get('valid_microdata', 0)
                analysis_data['invalid_schema_items'] += microdata_results.get('invalid_microdata', 0)
            
            if self.check_rdfa:
                rdfa_results = self._analyze_rdfa(soup)
                self._merge_results(rdfa_results, issues, warnings, recommendations, schema_issues)
                analysis_data['rdfa_count'] = rdfa_results.get('rdfa_count', 0)
                if rdfa_results.get('has_rdfa', False):
                    analysis_data['detected_formats'].append('RDFa')
                analysis_data['detected_types'].extend(rdfa_results.get('detected_types', []))
                analysis_data['valid_schema_items'] += rdfa_results.get('valid_rdfa', 0)
                analysis_data['invalid_schema_items'] += rdfa_results.get('invalid_rdfa', 0)
            
            # Update analysis data
            has_valid_schema = analysis_data['valid_schema_items'] > 0
            has_invalid_schema = analysis_data['invalid_schema_items'] > 0 or analysis_data['critical_severity_issues'] > 0
            
            # Set has_schema_markup based on valid schema presence
            analysis_data['has_schema_markup'] = any([
                analysis_data['jsonld_count'] > 0,
                analysis_data['microdata_count'] > 0,
                analysis_data['rdfa_count'] > 0
            ]) and not (has_invalid_schema and not has_valid_schema)
            
            analysis_data['total_schema_items'] = (
                analysis_data['jsonld_count'] + 
                analysis_data['microdata_count'] + 
                analysis_data['rdfa_count']
            )
            
            # Remove duplicates from detected types
            analysis_data['detected_types'] = list(set(analysis_data['detected_types']))
            
            # Update severity counts
            analysis_data['critical_severity_issues'] = sum(1 for issue in schema_issues if issue.severity == self.SEVERITY_CRITICAL)
            analysis_data['high_severity_issues'] = sum(1 for issue in schema_issues if issue.severity == self.SEVERITY_HIGH)
            analysis_data['medium_severity_issues'] = sum(1 for issue in schema_issues if issue.severity == self.SEVERITY_MEDIUM)
            analysis_data['low_severity_issues'] = sum(1 for issue in schema_issues if issue.severity == self.SEVERITY_LOW)
            
            # Add general recommendations if no schema markup found
            if analysis_data['total_schema_items'] == 0:
                warnings.append("No Schema.org structured data found on this page")
                recommendations.append(
                    "Add Schema.org structured data to improve search engine understanding of your content"
                )
                recommendations.append(
                    "Consider using JSON-LD format for easier implementation and maintenance"
                )
                recommendations.append(
                    "Implement schema types relevant to your content (e.g., Article, Product, LocalBusiness, etc.)"
                )
            
            # Add recommendations for invalid schema
            if has_invalid_schema:
                if analysis_data.get('critical_severity_issues', 0) > 0:
                    recommendations.append(
                        "Fix critical schema issues to ensure proper interpretation by search engines"
                    )
                if analysis_data.get('high_severity_issues', 0) > 0:
                    recommendations.append(
                        "Address high-severity schema issues by adding required properties to your structured data"
                    )
            
            # Calculate schema score
            score = self._calculate_schema_score(schema_issues)
            analysis_data['schema_score'] = round(score * 100)
            
            # Convert schema issues to serializable format
            analysis_data['schema_issues'] = [
                {
                    'name': issue.name,
                    'description': issue.description,
                    'severity': issue.severity,
                    'schema_type': issue.schema_type,
                    'location': issue.location,
                    'remediation': issue.remediation
                } for issue in schema_issues
            ]
            
            return AnalysisResult(
                data=analysis_data,
                metadata=self.create_metadata('schema'),
                score=score,
                issues=issues,
                warnings=warnings,
                recommendations=recommendations
            )
        
        except Exception as e:
            raise self.error_type(f"Failed to analyze Schema.org structured data: {str(e)}")
    
    def _merge_results(self, 
                      results: Dict[str, Any], 
                      issues: List[str], 
                      warnings: List[str], 
                      recommendations: List[str],
                      schema_issues: List[SchemaIssue]) -> None:
        """Merge results from individual schema checks.
        
        Args:
            results: Results from a schema check
            issues: List of issues to append to
            warnings: List of warnings to append to
            recommendations: List of recommendations to append to
            schema_issues: List of schema issues to append to
        """
        if results.get('issues'):
            issues.extend(results['issues'])
        if results.get('warnings'):
            warnings.extend(results['warnings'])
        if results.get('recommendations'):
            recommendations.extend(results['recommendations'])
        if results.get('schema_issues'):
            schema_issues.extend(results['schema_issues'])
    
    def _calculate_schema_score(self, schema_issues: List[SchemaIssue]) -> float:
        """Calculate a schema score based on the issues found.
        
        Args:
            schema_issues: List of schema issues found
            
        Returns:
            Float score between 0 and 1, with 1 being perfect schema implementation
        """
        # Start with a perfect score
        score = 1.0
        
        # Count issues by severity
        critical_severity = sum(1 for issue in schema_issues if issue.severity == self.SEVERITY_CRITICAL)
        high_severity = sum(1 for issue in schema_issues if issue.severity == self.SEVERITY_HIGH)
        medium_severity = sum(1 for issue in schema_issues if issue.severity == self.SEVERITY_MEDIUM)
        low_severity = sum(1 for issue in schema_issues if issue.severity == self.SEVERITY_LOW)
        
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
        
        # For sites with only minor schema issues, ensure score is above 0.7
        if critical_severity == 0 and high_severity == 0 and medium_severity <= 2:
            score = max(0.7, score)
        
        # Ensure score stays between 0 and 1
        return max(0.0, min(1.0, score))
    
    def _analyze_jsonld(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze JSON-LD schema markup.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Dictionary with analysis results
        """
        issues = []
        warnings = []
        recommendations = []
        schema_issues = []
        
        # Find all JSON-LD script tags
        jsonld_scripts = soup.find_all('script', type='application/ld+json')
        jsonld_count = len(jsonld_scripts)
        
        # Initialize result dictionary
        result = {
            'has_jsonld': jsonld_count > 0,
            'jsonld_count': jsonld_count,
            'valid_jsonld': 0,
            'invalid_jsonld': 0,
            'detected_types': []
        }
        
        if jsonld_count == 0:
            warnings.append("No JSON-LD schema markup found")
            recommendations.append(
                "Implement JSON-LD schema markup to enhance search engine understanding of your content"
            )
            return result
        
        # Analyze each JSON-LD script
        for i, script in enumerate(jsonld_scripts):
            script_location = f"JSON-LD script #{i+1}"
            
            try:
                # Check for empty script
                if not script.string or script.string.strip() == "":
                    warnings.append(f"Empty JSON-LD script found")
                    schema_issues.append(SchemaIssue(
                        name="Empty Schema Markup",
                        description=f"JSON-LD script contains no data",
                        severity=self.SEVERITY_HIGH,
                        schema_type="Unknown",
                        location=script_location,
                        remediation="Remove empty JSON-LD scripts or add valid schema.org data"
                    ))
                    result['invalid_jsonld'] += 1
                    continue
                
                # Parse JSON content
                schema_data = json.loads(script.string)
                
                # Check if it's an array of schemas
                if isinstance(schema_data, list):
                    for j, item in enumerate(schema_data):
                        self._validate_jsonld_item(
                            item, 
                            issues, 
                            warnings, 
                            recommendations, 
                            schema_issues, 
                            f"{script_location}, item #{j+1}",
                            result
                        )
                else:
                    # Single schema object
                    self._validate_jsonld_item(
                        schema_data, 
                        issues, 
                        warnings, 
                        recommendations, 
                        schema_issues, 
                        script_location,
                        result
                    )
                
            except json.JSONDecodeError:
                issues.append(f"Invalid JSON in schema markup at {script_location}")
                schema_issues.append(SchemaIssue(
                    name="Invalid JSON Format",
                    description=f"JSON-LD schema markup contains invalid JSON",
                    severity=self.SEVERITY_CRITICAL,
                    schema_type="Unknown",
                    location=script_location,
                    remediation="Fix the JSON syntax in your schema markup"
                ))
                result['invalid_jsonld'] += 1
                
            except Exception as e:
                warnings.append(f"Error analyzing JSON-LD schema at {script_location}: {str(e)}")
                result['invalid_jsonld'] += 1
        
        # Add general recommendations
        if result['invalid_jsonld'] > 0:
            recommendations.append(
                "Fix invalid JSON-LD schema markups to ensure proper interpretation by search engines"
            )
        
        if result['valid_jsonld'] == 0 and jsonld_count > 0:
            issues.append("No valid JSON-LD schema markup found despite having script tags")
            
        # Add recommendations based on missing required properties
        missing_required_props = any(
            issue.name == "Missing Required Properties" 
            for issue in schema_issues
        )
        
        if missing_required_props:
            recommendations.append(
                "Add all required properties to your schema markup for better search engine understanding"
            )
        
        # Add analysis components to result
        result['issues'] = issues
        result['warnings'] = warnings
        result['recommendations'] = recommendations
        result['schema_issues'] = schema_issues
        
        return result
    
    def _validate_jsonld_item(
        self, 
        item: Dict[str, Any], 
        issues: List[str], 
        warnings: List[str], 
        recommendations: List[str], 
        schema_issues: List[SchemaIssue],
        location: str,
        result: Dict[str, Any]
    ) -> None:
        """Validate a single JSON-LD schema item.
        
        Args:
            item: Schema.org data item
            issues: List of issues to append to
            warnings: List of warnings to append to
            recommendations: List of recommendations to append to
            schema_issues: List of schema issues to append to
            location: Location identifier for the schema item
            result: Result dictionary to update
        """
        # Check if it's a dictionary
        if not isinstance(item, dict):
            warnings.append(f"Non-object schema found at {location}")
            schema_issues.append(SchemaIssue(
                name="Invalid Schema Structure",
                description="Schema markup should be a JSON object",
                severity=self.SEVERITY_HIGH,
                schema_type="Unknown",
                location=location,
                remediation="Ensure your schema markup is a proper JSON object with key-value pairs"
            ))
            result['invalid_jsonld'] += 1
            return
        
        # Check for @context
        if self.check_context:
            if '@context' not in item:
                issues.append(f"Missing @context in schema at {location}")
                schema_issues.append(SchemaIssue(
                    name="Missing Schema Context",
                    description="Schema.org markup is missing the @context property",
                    severity=self.SEVERITY_HIGH,
                    schema_type=item.get('@type', 'Unknown'),
                    location=location,
                    remediation='Add "@context": "https://schema.org" to your JSON-LD'
                ))
                result['invalid_jsonld'] += 1
                return
            elif 'schema.org' not in str(item['@context']):
                warnings.append(f"Non-schema.org context in schema at {location}")
                schema_issues.append(SchemaIssue(
                    name="Non-Schema.org Context",
                    description=f"Context \"{item['@context']}\" is not from schema.org",
                    severity=self.SEVERITY_MEDIUM,
                    schema_type=item.get('@type', 'Unknown'),
                    location=location,
                    remediation='Use "https://schema.org" as the @context value'
                ))
                recommendations.append(f"Use 'https://schema.org' as the @context value in your schema markup")
        
        # Check for @type
        if '@type' not in item:
            issues.append(f"Missing @type in schema at {location}")
            schema_issues.append(SchemaIssue(
                name="Missing Schema Type",
                description="Schema.org markup is missing the @type property",
                severity=self.SEVERITY_HIGH,
                schema_type="Unknown",
                location=location,
                remediation='Add "@type": "[SchemaType]" to your JSON-LD where [SchemaType] is the appropriate type for your content'
            ))
            recommendations.append(f"Add '@type' property to specify the schema type in your markup")
            result['invalid_jsonld'] += 1
            return
        
        # Get schema type
        schema_type = item['@type']
        
        # Add to detected types
        if schema_type not in result['detected_types']:
            result['detected_types'].append(schema_type)
        
        # Check required properties if it's a known type
        if self.check_required_props and schema_type in self.PROPERTY_REQUIREMENTS:
            required_props = self.PROPERTY_REQUIREMENTS[schema_type]['required']
            missing_props = [prop for prop in required_props if prop not in item]
            
            if missing_props:
                issues.append(f"Missing required properties ({', '.join(missing_props)}) for {schema_type} schema at {location}")
                schema_issues.append(SchemaIssue(
                    name="Missing Required Properties",
                    description=f"Schema.org {schema_type} is missing required properties: {', '.join(missing_props)}",
                    severity=self.SEVERITY_HIGH,
                    schema_type=schema_type,
                    location=location,
                    remediation=f"Add the following required properties to your {schema_type} schema: {', '.join(missing_props)}"
                ))
                recommendations.append(f"Add required properties ({', '.join(missing_props)}) to your {schema_type} schema")
        
        # Check recommended properties if it's a known type
        if self.check_recommended_props and schema_type in self.PROPERTY_REQUIREMENTS:
            recommended_props = self.PROPERTY_REQUIREMENTS[schema_type]['recommended']
            missing_props = [prop for prop in recommended_props if prop not in item]
            
            if missing_props:
                warnings.append(f"Missing recommended properties ({', '.join(missing_props)}) for {schema_type} schema at {location}")
                schema_issues.append(SchemaIssue(
                    name="Missing Recommended Properties",
                    description=f"Schema.org {schema_type} is missing recommended properties: {', '.join(missing_props)}",
                    severity=self.SEVERITY_MEDIUM,
                    schema_type=schema_type,
                    location=location,
                    remediation=f"Consider adding these recommended properties to your {schema_type} schema: {', '.join(missing_props)}"
                ))
        
        # Check for nested schema types
        for key, value in item.items():
            if key not in ['@context', '@type'] and isinstance(value, dict) and '@type' in value:
                nested_type = value['@type']
                
                # Add to detected types
                if nested_type not in result['detected_types']:
                    result['detected_types'].append(nested_type)
                
                # Add note about nested schema
                recommendations.append(f"Found nested {nested_type} schema within {schema_type} at {location}")
                
                # Check required properties for nested schema
                if self.check_required_props and nested_type in self.PROPERTY_REQUIREMENTS:
                    required_props = self.PROPERTY_REQUIREMENTS[nested_type]['required']
                    missing_props = [prop for prop in required_props if prop not in value]
                    
                    if missing_props:
                        warnings.append(f"Missing required properties ({', '.join(missing_props)}) for nested {nested_type} schema at {location}")
                        schema_issues.append(SchemaIssue(
                            name="Missing Required Properties in Nested Schema",
                            description=f"Nested {nested_type} schema is missing required properties: {', '.join(missing_props)}",
                            severity=self.SEVERITY_MEDIUM,
                            schema_type=nested_type,
                            location=f"{location} (nested in {schema_type})",
                            remediation=f"Add the following required properties to your nested {nested_type} schema: {', '.join(missing_props)}"
                        ))
        
        # If we got this far, it's at least partially valid
        result['valid_jsonld'] += 1

    def _analyze_microdata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze Microdata schema markup.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Dictionary with analysis results
        """
        issues = []
        warnings = []
        recommendations = []
        schema_issues = []
        
        # Find all elements with itemscope
        microdata_elements = soup.find_all(itemscope=True)
        microdata_count = len(microdata_elements)
        
        # Initialize result dictionary
        result = {
            'has_microdata': microdata_count > 0,
            'microdata_count': microdata_count,
            'valid_microdata': 0,
            'invalid_microdata': 0,
            'detected_types': []
        }
        
        if microdata_count == 0:
            warnings.append("No Microdata schema markup found")
            recommendations.append(
                "Consider implementing Microdata or JSON-LD schema markup to enhance search engine understanding"
            )
        
        # Add analysis components to result
        result['issues'] = issues
        result['warnings'] = warnings
        result['recommendations'] = recommendations
        result['schema_issues'] = schema_issues
        
        return result

    def _analyze_rdfa(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze RDFa schema markup.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Dictionary with analysis results
        """
        issues = []
        warnings = []
        recommendations = []
        schema_issues = []
        
        # Initialize result dictionary
        result = {
            'has_rdfa': False,
            'rdfa_count': 0,
            'valid_rdfa': 0,
            'invalid_rdfa': 0,
            'detected_types': []
        }
        
        # Find all elements with vocab attribute
        rdfa_elements = soup.find_all(attrs={"vocab": True})
        rdfa_count = len(rdfa_elements)
        
        # Update result
        result['has_rdfa'] = rdfa_count > 0
        result['rdfa_count'] = rdfa_count
        
        if rdfa_count == 0:
            warnings.append("No RDFa schema markup found")
            recommendations.append(
                "Consider implementing RDFa or JSON-LD schema markup to enhance search engine understanding"
            )
        
        # Add analysis components to result
        result['issues'] = issues
        result['warnings'] = warnings
        result['recommendations'] = recommendations
        result['schema_issues'] = schema_issues
        
        return result 