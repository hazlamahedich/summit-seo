# Analyzers API Documentation

## Overview

The `analyzer` package provides components for analyzing different aspects of SEO on web pages. Each analyzer focuses on a specific area such as titles, meta tags, content, security, performance, etc. All analyzers inherit from a common base class to ensure consistent behavior and output formats.

## Class Hierarchy

```
BaseAnalyzer (Generic[InputType, OutputType])
├── TitleAnalyzer
├── MetaAnalyzer
├── HeadingStructureAnalyzer
├── ContentAnalyzer
├── LinkAnalyzer
├── ImageAnalyzer
├── SecurityAnalyzer
├── PerformanceAnalyzer
├── SchemaAnalyzer
├── AccessibilityAnalyzer
├── MobileFriendlyAnalyzer
└── SocialMediaAnalyzer
```

## Public Classes

### BaseAnalyzer

`BaseAnalyzer` is the abstract base class that all analyzers inherit from. It defines the interface and common functionality that all analyzers must implement.

#### Constructor

```python
def __init__(self, config: Optional[Dict[str, Any]] = None) -> None
```

**Parameters:**
- `config` (Optional[Dict[str, Any]]): Configuration dictionary for customizing analyzer behavior

**Configuration options:**
- `enable_caching` (bool): Whether to enable result caching (default: True)
- `cache_ttl` (int): Time-to-live for cached results in seconds (default: 3600)
- `cache_type` (str): Type of cache to use (default: 'memory')
- `cache_namespace` (str): Namespace for cache entries (default: 'analyzer')

#### Public Methods

```python
async def analyze(self, data: InputType) -> AnalysisResult[OutputType]
```

**Description:** Analyze the input data and return results. The implementation checks the cache first, and only performs analysis if the result is not found in cache or if caching is disabled.

**Parameters:**
- `data` (InputType): Input data to analyze

**Returns:**
- `AnalysisResult[OutputType]`: Container for analysis results

**Raises:**
- `AnalyzerError`: If analysis fails

```python
def validate_input(self, data: InputType) -> None
```

**Description:** Validate the input data before analysis.

**Parameters:**
- `data` (InputType): Input data to validate

**Raises:**
- `AnalyzerError`: If input validation fails

```python
def create_metadata(self, analyzer_type: str) -> AnalysisMetadata
```

**Description:** Create metadata for analysis results.

**Parameters:**
- `analyzer_type` (str): Type of analyzer

**Returns:**
- `AnalysisMetadata`: Metadata for analysis results

```python
def calculate_score(self, issues: List[str], warnings: List[str]) -> float
```

**Description:** Calculate a score based on issues and warnings.

**Parameters:**
- `issues` (List[str]): List of issues found during analysis
- `warnings` (List[str]): List of warnings found during analysis

**Returns:**
- `float`: Calculated score between 0 and 100

### AnalysisResult

`AnalysisResult` is a container for analysis results.

#### Fields

- `data` (OutputType): The output data from the analysis
- `metadata` (AnalysisMetadata): Metadata about the analysis
- `score` (float): Numeric score representing the quality (0-100)
- `issues` (List[str]): List of issues found during analysis
- `warnings` (List[str]): List of warnings found during analysis
- `recommendations` (List[str]): List of recommendations to address issues
- `enhanced_recommendations` (List[Recommendation]): Enhanced recommendations with severity, priority, and implementation guidance

#### Methods

```python
def to_dict(self) -> Dict[str, Any]
```

**Description:** Convert the result to a dictionary.

**Returns:**
- `Dict[str, Any]`: Dictionary representation of the result

```python
def get_priority_recommendations(self) -> List[Recommendation]
```

**Description:** Get recommendations sorted by priority.

**Returns:**
- `List[Recommendation]`: List of recommendations ordered by priority (highest first)

```python
def get_severity_recommendations(self) -> List[Recommendation]
```

**Description:** Get recommendations sorted by severity.

**Returns:**
- `List[Recommendation]`: List of recommendations ordered by severity (most severe first)

```python
def get_quick_wins(self) -> List[Recommendation]
```

**Description:** Get all quick win recommendations.

**Returns:**
- `List[Recommendation]`: List of quick win recommendations

### AnalysisMetadata

`AnalysisMetadata` contains metadata for analysis results.

#### Fields

- `timestamp` (datetime): When the analysis was performed
- `analyzer_type` (str): Type of analyzer used
- `version` (str): Version of the analyzer (default: '1.0.0')
- `additional_info` (Optional[Dict[str, Any]]): Additional information specific to the analyzer
- `cached` (bool): Whether the result was retrieved from cache (default: False)
- `cache_key` (Optional[str]): Cache key used to store/retrieve the result (default: None)

### AnalyzerFactory

The `AnalyzerFactory` is responsible for creating analyzer instances.

#### Methods

```python
def register(self, name: str, analyzer_class: Type[BaseAnalyzer]) -> None
```

**Description:** Register an analyzer class with a name.

**Parameters:**
- `name` (str): Name to associate with the analyzer class
- `analyzer_class` (Type[BaseAnalyzer]): Analyzer class to register

```python
def create(self, name: str, config: Optional[Dict[str, Any]] = None) -> BaseAnalyzer
```

**Description:** Create an analyzer instance by name.

**Parameters:**
- `name` (str): Name of the analyzer to create
- `config` (Optional[Dict[str, Any]]): Configuration for the analyzer

**Returns:**
- `BaseAnalyzer`: Instance of the specified analyzer

**Raises:**
- `ValueError`: If analyzer name is not registered

```python
def get_registered_analyzers(self) -> Dict[str, Type[BaseAnalyzer]]
```

**Description:** Get all registered analyzers.

**Returns:**
- `Dict[str, Type[BaseAnalyzer]]`: Dictionary mapping names to analyzer classes

## Usage Examples

### Basic Usage

```python
from summit_seo import AnalyzerFactory

# Create an analyzer using the factory
factory = AnalyzerFactory()
title_analyzer = factory.create('title')

# Run the analysis
import asyncio
result = asyncio.run(title_analyzer.analyze({
    'html': '<html><head><title>My Page Title</title></head><body></body></html>',
    'url': 'https://example.com'
}))

# Access results
print(f"Score: {result.score}")
print(f"Issues: {result.issues}")
print(f"Recommendations: {result.recommendations}")
```

### Custom Configuration

```python
from summit_seo import AnalyzerFactory

# Create an analyzer with custom configuration
config = {
    'enable_caching': False,
    'min_title_length': 20,
    'max_title_length': 60
}
factory = AnalyzerFactory()
title_analyzer = factory.create('title', config)

# Run the analysis
import asyncio
result = asyncio.run(title_analyzer.analyze({
    'html': '<html><head><title>Short Title</title></head><body></body></html>',
    'url': 'https://example.com'
}))

# Access prioritized recommendations
for rec in result.get_priority_recommendations():
    print(f"{rec.priority}: {rec.message}")
```

### Using Multiple Analyzers

```python
from summit_seo import AnalyzerFactory
import asyncio

async def run_multiple_analyzers(html, url):
    factory = AnalyzerFactory()
    analyzers = {
        'title': factory.create('title'),
        'meta': factory.create('meta'),
        'content': factory.create('content')
    }
    
    data = {
        'html': html,
        'url': url
    }
    
    results = {}
    for name, analyzer in analyzers.items():
        results[name] = await analyzer.analyze(data)
        
    return results

# Run multiple analyzers
html_content = '<html><head><title>My Page</title></head><body>Content here</body></html>'
results = asyncio.run(run_multiple_analyzers(html_content, 'https://example.com'))

# Calculate average score
avg_score = sum(r.score for r in results.values()) / len(results)
print(f"Average score: {avg_score}")
```

## Extension Points

To create a custom analyzer, extend the `BaseAnalyzer` class and implement the required abstract methods:

```python
from summit_seo import BaseAnalyzer, AnalysisResult, AnalysisMetadata
from typing import Dict, Any
import datetime

class CustomAnalyzer(BaseAnalyzer[Dict[str, str], Dict[str, Any]]):
    """A custom analyzer implementation."""
    
    async def _analyze(self, data: Dict[str, str]) -> AnalysisResult[Dict[str, Any]]:
        """Implement the core analysis logic."""
        # Analyze the data
        html = data.get('html', '')
        url = data.get('url', '')
        
        # Example logic
        issues = []
        warnings = []
        recommendations = []
        
        # Perform analysis
        custom_result = {'key_finding': 'value'}
        
        # Add recommendations
        if some_condition:
            issues.append("Issue found")
            recommendations.append("Fix the issue")
        
        # Create metadata
        metadata = self.create_metadata('custom')
        
        # Calculate score
        score = self.calculate_score(issues, warnings)
        
        # Return result
        return AnalysisResult(
            data=custom_result,
            metadata=metadata,
            score=score,
            issues=issues,
            warnings=warnings,
            recommendations=recommendations
        )

# Register with factory
from summit_seo import AnalyzerFactory
factory = AnalyzerFactory()
factory.register('custom', CustomAnalyzer) 