# Creating a Custom Analyzer

This guide demonstrates how to create a custom analyzer by extending the `BaseAnalyzer` class. We'll implement a simple keyword density analyzer that evaluates how well a webpage targets specific keywords.

## Overview

Custom analyzers allow you to extend Summit SEO with specialized analysis capabilities. By inheriting from `BaseAnalyzer`, you get access to the caching, scoring, and recommendation systems built into the framework.

## Step 1: Import Required Components

```python
from typing import Dict, List, Any, Optional
import re
from bs4 import BeautifulSoup

from summit_seo import (
    BaseAnalyzer,
    AnalysisResult,
    AnalysisMetadata,
    Recommendation,
    RecommendationSeverity,
    RecommendationPriority,
    RecommendationBuilder
)
```

## Step 2: Define Your Analyzer Class

```python
class KeywordDensityAnalyzer(BaseAnalyzer[Dict[str, Any], Dict[str, Any]]):
    """Analyzer for evaluating keyword density and usage on a webpage.
    
    This analyzer checks how well a webpage targets specific keywords by
    analyzing keyword density in different page elements (title, headings,
    content) and providing recommendations for optimization.
    
    Attributes:
        config (Dict[str, Any]): Configuration for the analyzer
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the keyword density analyzer.
        
        Args:
            config: Configuration dictionary for customizing analyzer behavior
        """
        default_config = {
            'target_keywords': [],
            'min_keyword_density': 1.0,  # Percentage
            'max_keyword_density': 3.0,  # Percentage
            'ideal_keyword_density': 2.0,  # Percentage
            'keyword_in_title_weight': 3.0,
            'keyword_in_headings_weight': 2.0,
            'keyword_in_first_paragraph_weight': 2.0,
            'keyword_in_content_weight': 1.0,
            'enable_caching': True
        }
        
        # Merge default config with provided config
        merged_config = {**default_config, **(config or {})}
        super().__init__(merged_config)
```

## Step 3: Implement the Analysis Logic

```python
    async def _analyze(self, data: Dict[str, Any]) -> AnalysisResult[Dict[str, Any]]:
        """Perform keyword density analysis.
        
        Args:
            data: Dictionary containing HTML content and URL
            
        Returns:
            AnalysisResult containing keyword density analysis
            
        Raises:
            AnalyzerError: If analysis fails
        """
        html = data.get('html', '')
        url = data.get('url', '')
        target_keywords = self.config.get('target_keywords', [])
        
        if not html:
            raise self.error_type("No HTML content provided for analysis")
            
        if not target_keywords:
            # Use default behavior for empty keyword list
            # Extract potential keywords from the URL
            url_keywords = self._extract_keywords_from_url(url)
            target_keywords = url_keywords
            
        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract text content
        title_text = self._get_title(soup)
        heading_texts = self._get_headings(soup)
        first_paragraph = self._get_first_paragraph(soup)
        content_text = self._get_content(soup)
        
        # Calculate keyword occurrences and density
        keyword_stats = {}
        total_words = len(content_text.split())
        
        for keyword in target_keywords:
            # Count occurrences
            title_count = self._count_keyword(keyword, title_text)
            heading_count = sum(self._count_keyword(keyword, heading) for heading in heading_texts)
            first_para_count = self._count_keyword(keyword, first_paragraph)
            content_count = self._count_keyword(keyword, content_text)
            
            # Calculate density (percentage)
            density = (content_count / total_words * 100) if total_words > 0 else 0
            
            # Store stats
            keyword_stats[keyword] = {
                'title_count': title_count,
                'heading_count': heading_count,
                'first_paragraph_count': first_para_count,
                'content_count': content_count,
                'total_count': content_count,
                'density': round(density, 2)
            }
        
        # Evaluate results
        issues = []
        warnings = []
        recommendations = []
        enhanced_recommendations = []
        
        min_density = self.config.get('min_keyword_density')
        max_density = self.config.get('max_keyword_density')
        ideal_density = self.config.get('ideal_keyword_density')
        
        # Create analysis output data
        result_data = {
            'target_keywords': target_keywords,
            'total_words': total_words,
            'keyword_stats': keyword_stats,
        }
        
        # Generate issues, warnings, and recommendations
        for keyword, stats in keyword_stats.items():
            # Check title
            if stats['title_count'] == 0:
                issues.append(f"Keyword '{keyword}' not found in page title")
                recommendations.append(f"Include keyword '{keyword}' in the page title")
                
                # Create enhanced recommendation
                rec_builder = RecommendationBuilder()
                rec = rec_builder.set_message(f"Include keyword '{keyword}' in the page title")
                    .set_severity(RecommendationSeverity.HIGH)
                    .set_priority(RecommendationPriority.HIGH)
                    .set_implementation_guide(f"Update the title tag to include '{keyword}'. Example: '<title>Your Page Title with {keyword}</title>'")
                    .set_impact_description("Keywords in title have high SEO value and improve click-through rates from search results")
                    .set_quick_win(True)
                    .build()
                enhanced_recommendations.append(rec)
            
            # Check density
            density = stats['density']
            if density < min_density:
                issues.append(f"Keyword '{keyword}' density is too low ({density}%)")
                recommendations.append(f"Increase the usage of keyword '{keyword}' to achieve {ideal_density}% density")
                
                # Create enhanced recommendation
                rec_builder = RecommendationBuilder()
                rec = rec_builder.set_message(f"Increase keyword '{keyword}' density to {ideal_density}%")
                    .set_severity(RecommendationSeverity.MEDIUM)
                    .set_priority(RecommendationPriority.MEDIUM)
                    .set_implementation_guide(f"Add more instances of '{keyword}' naturally throughout your content, especially in headings and important paragraphs")
                    .set_impact_description("Proper keyword density helps search engines understand your page topic")
                    .set_quick_win(False)
                    .build()
                enhanced_recommendations.append(rec)
                
            elif density > max_density:
                warnings.append(f"Keyword '{keyword}' density is too high ({density}%)")
                recommendations.append(f"Reduce the usage of keyword '{keyword}' to achieve {ideal_density}% density")
                
                # Create enhanced recommendation
                rec_builder = RecommendationBuilder()
                rec = rec_builder.set_message(f"Reduce keyword '{keyword}' density to {ideal_density}%")
                    .set_severity(RecommendationSeverity.MEDIUM)
                    .set_priority(RecommendationPriority.MEDIUM)
                    .set_implementation_guide(f"Reduce instances of '{keyword}' and use synonyms or related terms instead")
                    .set_impact_description("Excessive keyword density can trigger spam filters in search engines")
                    .set_quick_win(False)
                    .build()
                enhanced_recommendations.append(rec)
            
            # Check headings
            if stats['heading_count'] == 0:
                warnings.append(f"Keyword '{keyword}' not found in any headings")
                recommendations.append(f"Include keyword '{keyword}' in at least one heading (H1-H3)")
                
                # Create enhanced recommendation
                rec_builder = RecommendationBuilder()
                rec = rec_builder.set_message(f"Include keyword '{keyword}' in headings")
                    .set_severity(RecommendationSeverity.MEDIUM)
                    .set_priority(RecommendationPriority.MEDIUM)
                    .set_implementation_guide(f"Add '{keyword}' to at least one H1, H2, or H3 heading")
                    .set_impact_description("Keywords in headings help search engines understand your content structure")
                    .set_quick_win(True)
                    .build()
                enhanced_recommendations.append(rec)
        
        # Create metadata
        metadata = self.create_metadata('keyword_density')
        
        # Calculate score
        score = self.calculate_score(issues, warnings)
        
        # Create and return the analysis result
        return AnalysisResult(
            data=result_data,
            metadata=metadata,
            score=score,
            issues=issues,
            warnings=warnings,
            recommendations=recommendations,
            enhanced_recommendations=enhanced_recommendations
        )
```

## Step 4: Implement Helper Methods

```python
    def _get_title(self, soup: BeautifulSoup) -> str:
        """Extract the title text from HTML.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Title text or empty string if not found
        """
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ''
    
    def _get_headings(self, soup: BeautifulSoup) -> List[str]:
        """Extract all heading texts from HTML.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of heading texts
        """
        headings = []
        for heading_level in range(1, 7):
            for heading in soup.find_all(f'h{heading_level}'):
                headings.append(heading.get_text().strip())
        return headings
    
    def _get_first_paragraph(self, soup: BeautifulSoup) -> str:
        """Extract the first paragraph text from HTML.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            First paragraph text or empty string if not found
        """
        first_p = soup.find('p')
        return first_p.get_text().strip() if first_p else ''
    
    def _get_content(self, soup: BeautifulSoup) -> str:
        """Extract the main content text from HTML.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Combined text content
        """
        # Try to find content in main content areas
        content_areas = soup.select('main, article, #content, .content')
        
        if content_areas:
            # Use the first content area found
            content = content_areas[0].get_text().strip()
        else:
            # Fallback to body content
            body = soup.find('body')
            content = body.get_text().strip() if body else ''
        
        return content
    
    def _count_keyword(self, keyword: str, text: str) -> int:
        """Count occurrences of a keyword in text.
        
        Performs case-insensitive matching and handles word boundaries.
        
        Args:
            keyword: Keyword to search for
            text: Text to search in
            
        Returns:
            Number of occurrences
        """
        # Prepare regex pattern with word boundaries
        pattern = r'\b' + re.escape(keyword) + r'\b'
        return len(re.findall(pattern, text, re.IGNORECASE))
    
    def _extract_keywords_from_url(self, url: str) -> List[str]:
        """Extract potential keywords from URL.
        
        Args:
            url: URL to analyze
            
        Returns:
            List of potential keywords
        """
        # Extract path from URL
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        # Remove file extensions and split by slashes and hyphens
        path = re.sub(r'\.[a-zA-Z0-9]+$', '', path)  # Remove file extension
        segments = re.split(r'[/-]', path)
        
        # Filter out empty segments and common words
        common_words = {'the', 'and', 'or', 'of', 'to', 'in', 'for', 'with', 'on', 'at', 'by', 'an', 'a'}
        keywords = [s.lower() for s in segments if s and s.lower() not in common_words and len(s) > 3]
        
        return keywords
```

## Step 5: Register Your Analyzer with the Factory

```python
from summit_seo import AnalyzerFactory

# Create an instance of the analyzer factory
factory = AnalyzerFactory()

# Register your custom analyzer
factory.register('keyword_density', KeywordDensityAnalyzer)
```

## Step 6: Use Your Custom Analyzer

```python
import asyncio
from summit_seo import AnalyzerFactory

async def analyze_keyword_density():
    # Create the analyzer factory
    factory = AnalyzerFactory()
    
    # Register your custom analyzer (if not registered globally)
    factory.register('keyword_density', KeywordDensityAnalyzer)
    
    # Create your analyzer with custom configuration
    analyzer = factory.create('keyword_density', {
        'target_keywords': ['seo', 'optimization', 'keywords'],
        'min_keyword_density': 1.5,
        'max_keyword_density': 3.5
    })
    
    # Prepare input data
    data = {
        'html': open('my_webpage.html', 'r').read(),
        'url': 'https://example.com/seo-optimization-guide'
    }
    
    # Run the analysis
    result = await analyzer.analyze(data)
    
    # Print results
    print(f"Keyword Density Analysis Score: {result.score:.2f}/100")
    
    # Print keyword stats
    print("\nKeyword Statistics:")
    for keyword, stats in result.data['keyword_stats'].items():
        print(f"\n{keyword.upper()}:")
        print(f"  Density: {stats['density']}%")
        print(f"  In Title: {stats['title_count'] > 0}")
        print(f"  In Headings: {stats['heading_count']}")
        print(f"  In First Paragraph: {stats['first_paragraph_count']}")
        print(f"  Total Count: {stats['total_count']}")
    
    # Print issues and recommendations
    if result.issues:
        print("\nIssues:")
        for issue in result.issues:
            print(f"- {issue}")
    
    if result.enhanced_recommendations:
        print("\nRecommendations:")
        for rec in result.enhanced_recommendations:
            print(f"- [{rec.severity.name}] {rec.message}")
            print(f"  How to implement: {rec.implementation_guide}")
    
    return result

# Run the analysis
asyncio.run(analyze_keyword_density())
```

## Complete Code Example

The complete custom analyzer implementation is available as a gist:

https://gist.github.com/summit-seo/keyword-density-analyzer

## Next Steps

After creating your custom analyzer, you can:

1. Add more sophisticated analysis logic
2. Implement additional helper methods for specific analysis tasks
3. Create unit tests to verify your analyzer's behavior
4. Contribute your analyzer to the Summit SEO project

## Related Documentation

- [API Reference for BaseAnalyzer](../api/analyzers.md)
- [Recommendation System Guide](../guide/recommendations.md)
- [Scoring Algorithm Documentation](../guide/scoring.md)
- [Custom Processor Creation](custom_processor.md) 