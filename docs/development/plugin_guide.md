# Summit SEO Plugin Development Guide

This guide provides detailed instructions for extending Summit SEO functionality through custom plugins.

## Table of Contents

1. [Plugin Architecture Overview](#plugin-architecture-overview)
2. [Plugin Types](#plugin-types)
3. [Creating Custom Analyzers](#creating-custom-analyzers)
4. [Creating Custom Collectors](#creating-custom-collectors)
5. [Creating Custom Processors](#creating-custom-processors)
6. [Creating Custom Reporters](#creating-custom-reporters)
7. [Plugin Configuration](#plugin-configuration)
8. [Plugin Discovery and Registration](#plugin-discovery-and-registration)
9. [Packaging and Distribution](#packaging-and-distribution)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

## Plugin Architecture Overview

Summit SEO is designed to be extensible through a plugin system. Plugins can extend or replace core functionality in several areas:

- **Analyzers**: Add new analysis capabilities
- **Collectors**: Add new data collection methods
- **Processors**: Add new data processing capabilities
- **Reporters**: Add new report formats or visualization methods

The plugin architecture uses Python's class inheritance and dynamic loading mechanisms to discover and integrate plugins into the main application.

```
┌───────────────────────────────────────────────┐
│                 Summit SEO Core               │
├───────────┬───────────┬───────────┬───────────┤
│ Analyzer  │ Collector │ Processor │ Reporter  │
│  Registry │  Registry │  Registry │  Registry │
└─────┬─────┴─────┬─────┴─────┬─────┴─────┬─────┘
      │           │           │           │
┌─────▼─────┐┌────▼──────┐┌───▼───────┐┌──▼──────┐
│  Built-in ││  Built-in ││  Built-in ││ Built-in│
│ Analyzers ││Collectors ││Processors ││Reporters│
└─────┬─────┘└─────┬─────┘└─────┬─────┘└────┬────┘
      │            │            │            │
┌─────▼─────┐┌─────▼─────┐┌─────▼─────┐┌─────▼────┐
│   Plugin  ││   Plugin  ││   Plugin  ││  Plugin  │
│ Analyzers ││Collectors ││Processors ││Reporters │
└───────────┘└───────────┘└───────────┘└──────────┘
```

## Plugin Types

### Analyzer Plugins

Analyzer plugins evaluate specific aspects of a webpage or website and generate analysis results and recommendations.

### Collector Plugins

Collector plugins gather data from various sources, such as websites, files, or APIs.

### Processor Plugins

Processor plugins transform raw collected data into a structured format suitable for analysis.

### Reporter Plugins

Reporter plugins generate output in various formats, such as HTML, JSON, CSV, PDF, etc.

## Creating Custom Analyzers

Custom analyzers allow you to implement specialized analysis logic for particular aspects of a website.

### Step 1: Inherit from BaseAnalyzer

```python
from summit_seo.analyzers import BaseAnalyzer

class MyCustomAnalyzer(BaseAnalyzer):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "my_custom_analyzer"
        self.description = "My custom analyzer for specialized analysis"
        self.version = "1.0.0"
```

### Step 2: Implement Required Methods

```python
def _analyze(self, processed_data):
    """
    Implement your analysis logic here.
    
    Args:
        processed_data: The processed data from a Processor
        
    Returns:
        Dict containing analysis results
    """
    results = {
        'findings': [],
        'metadata': {}
    }
    
    # Example: Check if a specific element exists
    if processed_data.document.select('div.important-element'):
        results['findings'].append({
            'type': 'important_element',
            'status': 'pass',
            'message': 'Important element found on page'
        })
    else:
        results['findings'].append({
            'type': 'important_element',
            'status': 'fail',
            'message': 'Important element missing from page',
            'recommendation': 'Add div with class "important-element"'
        })
    
    return results

def compute_score(self, results):
    """
    Calculate a score from 0-100 based on analysis results.
    
    Args:
        results: The analysis results from _analyze method
        
    Returns:
        Integer score from 0-100
    """
    # Example scoring logic
    score = 100
    
    # Deduct points for each failed check
    for finding in results.get('findings', []):
        if finding['status'] == 'fail':
            score -= 10
        elif finding['status'] == 'warning':
            score -= 5
    
    # Ensure score is between 0-100
    return max(0, min(100, score))
```

### Step 3: Register Your Analyzer

Method 1: Use the decorator:

```python
from summit_seo.analyzers import register_analyzer

@register_analyzer
class MyCustomAnalyzer(BaseAnalyzer):
    # Your implementation
    pass
```

Method 2: Register manually:

```python
from summit_seo.analyzers import register_analyzer

class MyCustomAnalyzer(BaseAnalyzer):
    # Your implementation
    pass

register_analyzer(MyCustomAnalyzer)
```

### Complete Example

```python
from summit_seo.analyzers import BaseAnalyzer, register_analyzer

@register_analyzer
class SEOTitleAnalyzer(BaseAnalyzer):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "seo_title"
        self.description = "Analyzes SEO best practices for page titles"
        self.version = "1.0.0"
        
        # Default configuration
        self.default_config = {
            'min_title_length': 30,
            'max_title_length': 60,
            'check_keyword_in_title': True
        }
        
        # Merge default config with user config
        if config:
            self.config = {**self.default_config, **config}
        else:
            self.config = self.default_config
    
    def _analyze(self, processed_data):
        results = {
            'findings': [],
            'metadata': {}
        }
        
        # Extract the title
        title = processed_data.metadata.get('title', '')
        results['metadata']['title'] = title
        
        # Check title existence
        if not title:
            results['findings'].append({
                'type': 'title_missing',
                'status': 'fail',
                'message': 'Page title is missing',
                'recommendation': 'Add a title tag to the page'
            })
            return results
        
        # Check title length
        title_length = len(title)
        results['metadata']['title_length'] = title_length
        
        if title_length < self.config['min_title_length']:
            results['findings'].append({
                'type': 'title_too_short',
                'status': 'warning',
                'message': f'Title is too short ({title_length} chars)',
                'recommendation': f'Increase title length to at least {self.config["min_title_length"]} characters'
            })
        elif title_length > self.config['max_title_length']:
            results['findings'].append({
                'type': 'title_too_long',
                'status': 'warning',
                'message': f'Title is too long ({title_length} chars)',
                'recommendation': f'Reduce title length to at most {self.config["max_title_length"]} characters'
            })
        else:
            results['findings'].append({
                'type': 'title_length',
                'status': 'pass',
                'message': f'Title length is optimal ({title_length} chars)'
            })
        
        # Check if primary keyword is in title
        if self.config['check_keyword_in_title']:
            keyword = processed_data.metadata.get('primary_keyword', '')
            if keyword and keyword.lower() in title.lower():
                results['findings'].append({
                    'type': 'keyword_in_title',
                    'status': 'pass',
                    'message': 'Primary keyword found in title'
                })
            elif keyword:
                results['findings'].append({
                    'type': 'keyword_in_title',
                    'status': 'fail',
                    'message': 'Primary keyword not found in title',
                    'recommendation': f'Include the primary keyword "{keyword}" in the title'
                })
        
        return results
    
    def compute_score(self, results):
        score = 100
        
        # No title is a major issue
        if any(f['type'] == 'title_missing' for f in results['findings']):
            return 0
        
        # Deduct points for issues
        for finding in results['findings']:
            if finding['status'] == 'fail':
                score -= 20
            elif finding['status'] == 'warning':
                score -= 10
        
        return max(0, min(100, score))
```

## Creating Custom Collectors

Custom collectors allow you to gather data from different sources or using different methods.

### Step 1: Inherit from BaseCollector

```python
from summit_seo.collectors import BaseCollector

class MyCustomCollector(BaseCollector):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "my_custom_collector"
        self.description = "My custom collector for specialized data gathering"
        self.version = "1.0.0"
```

### Step 2: Implement Required Methods

```python
def collect(self, target):
    """
    Implement your collection logic here.
    
    Args:
        target: The target to collect data from (URL, file path, etc.)
        
    Returns:
        CollectionResult object containing collected data
    """
    from summit_seo.models import CollectionResult
    
    # Implement your collection logic
    content = "..."  # Replace with actual collection
    
    # Create metadata
    metadata = {
        'source': target,
        'timestamp': datetime.now().isoformat(),
        'collector': self.name,
        # Add additional metadata
    }
    
    # Return the collection result
    return CollectionResult(content=content, metadata=metadata)
```

### Step 3: Register Your Collector

```python
from summit_seo.collectors import register_collector

@register_collector
class MyCustomCollector(BaseCollector):
    # Your implementation
    pass
```

### Complete Example

```python
import requests
from datetime import datetime
from summit_seo.collectors import BaseCollector, register_collector
from summit_seo.models import CollectionResult
from summit_seo.exceptions import CollectionError

@register_collector
class APICollector(BaseCollector):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "api_collector"
        self.description = "Collects data from API endpoints"
        self.version = "1.0.0"
        
        # Default configuration
        self.default_config = {
            'timeout': 30,
            'headers': {},
            'auth': None,
            'format': 'json'
        }
        
        # Merge default config with user config
        if config:
            self.config = {**self.default_config, **config}
        else:
            self.config = self.default_config
    
    def collect(self, target):
        """
        Collect data from an API endpoint.
        
        Args:
            target: API URL
            
        Returns:
            CollectionResult object containing API response
        """
        try:
            # Make the API request
            response = requests.get(
                target,
                headers=self.config['headers'],
                auth=self.config['auth'],
                timeout=self.config['timeout']
            )
            
            # Check for successful response
            response.raise_for_status()
            
            # Parse the response based on format
            if self.config['format'] == 'json':
                content = response.json()
            else:
                content = response.text
            
            # Create metadata
            metadata = {
                'source': target,
                'timestamp': datetime.now().isoformat(),
                'collector': self.name,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'response_time': response.elapsed.total_seconds()
            }
            
            return CollectionResult(content=content, metadata=metadata)
            
        except requests.RequestException as e:
            raise CollectionError(f"Failed to collect data from API: {str(e)}")
```

## Creating Custom Processors

Custom processors allow you to transform collected data into formats suitable for your analyzers.

### Step 1: Inherit from BaseProcessor

```python
from summit_seo.processors import BaseProcessor

class MyCustomProcessor(BaseProcessor):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "my_custom_processor"
        self.description = "My custom processor for specialized data transformation"
        self.version = "1.0.0"
```

### Step 2: Implement Required Methods

```python
def process(self, collection_result):
    """
    Implement your processing logic here.
    
    Args:
        collection_result: The result from a Collector
        
    Returns:
        ProcessedData object containing the processed data
    """
    from summit_seo.models import ProcessedData
    
    # Implement your processing logic
    processed_content = {}  # Replace with actual processing
    
    # Create metadata
    metadata = {
        'processor': self.name,
        'timestamp': datetime.now().isoformat(),
        # Add additional metadata
    }
    
    # Return the processed data
    return ProcessedData(data=processed_content, metadata=metadata)
```

### Step 3: Register Your Processor

```python
from summit_seo.processors import register_processor

@register_processor
class MyCustomProcessor(BaseProcessor):
    # Your implementation
    pass
```

### Complete Example

```python
import json
from datetime import datetime
from bs4 import BeautifulSoup
from summit_seo.processors import BaseProcessor, register_processor
from summit_seo.models import ProcessedData
from summit_seo.exceptions import ProcessingError

@register_processor
class JSONAPIProcessor(BaseProcessor):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "json_api_processor"
        self.description = "Processes JSON API responses"
        self.version = "1.0.0"
        
        # Default configuration
        self.default_config = {
            'extract_fields': [],
            'normalize_keys': True
        }
        
        # Merge default config with user config
        if config:
            self.config = {**self.default_config, **config}
        else:
            self.config = self.default_config
    
    def process(self, collection_result):
        """
        Process a JSON API response.
        
        Args:
            collection_result: The result from a Collector
            
        Returns:
            ProcessedData object containing the processed data
        """
        try:
            # Get content from collection result
            content = collection_result.content
            
            # Ensure content is a dictionary (JSON)
            if isinstance(content, str):
                content = json.loads(content)
            
            # Extract specific fields if requested
            if self.config['extract_fields']:
                extracted_data = {}
                for field in self.config['extract_fields']:
                    value = self._get_nested_value(content, field)
                    if value is not None:
                        extracted_data[field] = value
                processed_content = extracted_data
            else:
                processed_content = content
            
            # Normalize keys if requested
            if self.config['normalize_keys']:
                processed_content = self._normalize_keys(processed_content)
            
            # Create metadata
            metadata = {
                'processor': self.name,
                'timestamp': datetime.now().isoformat(),
                'source': collection_result.metadata.get('source'),
                'field_count': len(processed_content) if isinstance(processed_content, dict) else 0
            }
            
            return ProcessedData(data=processed_content, metadata=metadata)
            
        except Exception as e:
            raise ProcessingError(f"Failed to process JSON API data: {str(e)}")
    
    def _get_nested_value(self, data, key_path):
        """Get a value from a nested dictionary using dot notation."""
        keys = key_path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
                
        return value
    
    def _normalize_keys(self, data):
        """Normalize dictionary keys (convert to snake_case)."""
        if not isinstance(data, dict):
            return data
            
        result = {}
        for key, value in data.items():
            # Convert camelCase or PascalCase to snake_case
            normalized_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
            
            # Recursively normalize nested dictionaries
            if isinstance(value, dict):
                result[normalized_key] = self._normalize_keys(value)
            elif isinstance(value, list):
                result[normalized_key] = [
                    self._normalize_keys(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[normalized_key] = value
                
        return result
```

## Creating Custom Reporters

Custom reporters allow you to generate output in specialized formats or with custom visualizations.

### Step 1: Inherit from BaseReporter

```python
from summit_seo.reporters import BaseReporter

class MyCustomReporter(BaseReporter):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "my_custom_reporter"
        self.description = "My custom reporter for specialized output"
        self.format = "custom"  # Output format identifier
        self.version = "1.0.0"
```

### Step 2: Implement Required Methods

```python
def generate(self, analysis_result):
    """
    Implement your report generation logic here.
    
    Args:
        analysis_result: The AnalysisResult to generate a report for
        
    Returns:
        The generated report (string, bytes, etc.)
    """
    # Implement your report generation logic
    report = ""  # Replace with actual report generation
    
    return report
```

### Step 3: Register Your Reporter

```python
from summit_seo.reporters import register_reporter

@register_reporter
class MyCustomReporter(BaseReporter):
    # Your implementation
    pass
```

### Complete Example

```python
import csv
import io
from summit_seo.reporters import BaseReporter, register_reporter
from summit_seo.exceptions import ReportingError

@register_reporter
class CSVReporter(BaseReporter):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "csv_reporter"
        self.description = "Generates CSV reports from analysis results"
        self.format = "csv"
        self.version = "1.0.0"
        
        # Default configuration
        self.default_config = {
            'dialect': 'excel',
            'include_header': True,
            'detailed': False
        }
        
        # Merge default config with user config
        if config:
            self.config = {**self.default_config, **config}
        else:
            self.config = self.default_config
    
    def generate(self, analysis_result):
        """
        Generate a CSV report from analysis results.
        
        Args:
            analysis_result: The AnalysisResult to generate a report for
            
        Returns:
            CSV string
        """
        try:
            output = io.StringIO()
            writer = csv.writer(output, dialect=self.config['dialect'])
            
            # Write header if requested
            if self.config['include_header']:
                if self.config['detailed']:
                    writer.writerow([
                        'URL', 'Analyzer', 'Check', 'Status', 'Message', 'Recommendation'
                    ])
                else:
                    writer.writerow([
                        'URL', 'Analyzer', 'Score'
                    ])
            
            # Write data
            url = analysis_result.url
            
            if self.config['detailed']:
                # Write detailed findings
                for analyzer_name, analyzer_result in analysis_result.analyzers.items():
                    for finding in analyzer_result.get('findings', []):
                        writer.writerow([
                            url,
                            analyzer_name,
                            finding.get('type', ''),
                            finding.get('status', ''),
                            finding.get('message', ''),
                            finding.get('recommendation', '')
                        ])
            else:
                # Write summary scores
                for analyzer_name, analyzer_result in analysis_result.analyzers.items():
                    writer.writerow([
                        url,
                        analyzer_name,
                        analyzer_result.get('score', 0)
                    ])
            
            return output.getvalue()
            
        except Exception as e:
            raise ReportingError(f"Failed to generate CSV report: {str(e)}")
```

## Plugin Configuration

Plugins can define their own configuration options, which are merged with the core application configuration.

### Defining Default Configuration

```python
def __init__(self, config=None):
    super().__init__(config)
    
    # Define default configuration
    self.default_config = {
        'option1': 'default_value',
        'option2': 100,
        'option3': True
    }
    
    # Merge default config with user config
    if config:
        self.config = {**self.default_config, **config}
    else:
        self.config = self.default_config
```

### Accessing Configuration Values

```python
def some_method(self):
    option1 = self.config['option1']
    option2 = self.config.get('option2', 100)  # With default fallback
```

### Configuration Validation

To validate configuration values, override the `validate_config` method:

```python
def validate_config(self, config):
    """
    Validate the configuration.
    
    Args:
        config: The configuration to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    from summit_seo.exceptions import ConfigurationError
    
    if 'option1' in config and not isinstance(config['option1'], str):
        raise ConfigurationError("option1 must be a string")
        
    if 'option2' in config and not isinstance(config['option2'], int):
        raise ConfigurationError("option2 must be an integer")
        
    if 'option2' in config and config['option2'] <= 0:
        raise ConfigurationError("option2 must be greater than 0")
        
    return True
```

## Plugin Discovery and Registration

Summit SEO discovers plugins through several mechanisms:

### 1. Decorator Registration

The simplest way to register a plugin is using the provided decorators:

```python
from summit_seo.analyzers import register_analyzer

@register_analyzer
class MyAnalyzer(BaseAnalyzer):
    # Implementation
    pass
```

### 2. Manual Registration

Plugins can be registered manually using the registration functions:

```python
from summit_seo.analyzers import register_analyzer
from summit_seo.collectors import register_collector
from summit_seo.processors import register_processor
from summit_seo.reporters import register_reporter

# Create your plugin classes
class MyAnalyzer(BaseAnalyzer):
    # Implementation
    pass

# Register the plugins
register_analyzer(MyAnalyzer)
```

### 3. Entry Points

For packaged plugins, use Python entry points in your `setup.py`:

```python
from setuptools import setup

setup(
    name="summit-seo-myplugin",
    version="1.0.0",
    packages=["summit_seo_myplugin"],
    entry_points={
        "summit_seo.analyzers": [
            "my_analyzer = summit_seo_myplugin.analyzers:MyAnalyzer"
        ],
        "summit_seo.collectors": [
            "my_collector = summit_seo_myplugin.collectors:MyCollector"
        ],
        "summit_seo.processors": [
            "my_processor = summit_seo_myplugin.processors:MyProcessor"
        ],
        "summit_seo.reporters": [
            "my_reporter = summit_seo_myplugin.reporters:MyReporter"
        ]
    }
)
```

### 4. Plugin Directories

Summit SEO searches for plugins in specific directories. You can place your plugin modules in:

- `~/.summit-seo/plugins/`
- The directory specified by the `SUMMIT_SEO_PLUGINS` environment variable
- Custom directories specified in the configuration

## Packaging and Distribution

To distribute your plugins, you can create a Python package:

### Directory Structure

```
summit-seo-myplugin/
├── LICENSE
├── README.md
├── setup.py
└── summit_seo_myplugin/
    ├── __init__.py
    ├── analyzers.py
    ├── collectors.py
    ├── processors.py
    └── reporters.py
```

### setup.py Example

```python
from setuptools import setup, find_packages

setup(
    name="summit-seo-myplugin",
    version="1.0.0",
    description="Custom plugins for Summit SEO",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/summit-seo-myplugin",
    packages=find_packages(),
    install_requires=[
        "summit-seo>=1.0.0",
        "requests>=2.25.0"
    ],
    entry_points={
        "summit_seo.analyzers": [
            "my_analyzer = summit_seo_myplugin.analyzers:MyAnalyzer"
        ],
        "summit_seo.collectors": [
            "my_collector = summit_seo_myplugin.collectors:MyCollector"
        ],
        "summit_seo.processors": [
            "my_processor = summit_seo_myplugin.processors:MyProcessor"
        ],
        "summit_seo.reporters": [
            "my_reporter = summit_seo_myplugin.reporters:MyReporter"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10"
    ],
)
```

### Publishing to PyPI

```bash
# Build your package
python setup.py sdist bdist_wheel

# Upload to PyPI
twine upload dist/*
```

## Best Practices

### 1. Documentation

Ensure your plugin is well-documented:

- Clear docstrings for classes and methods
- Example usage in the README
- Description of configuration options
- Explanation of output formats or reports

### 2. Error Handling

Use the appropriate exception classes:

```python
from summit_seo.exceptions import (
    SummitSEOError,
    ConfigurationError,
    CollectionError,
    ProcessingError,
    AnalysisError,
    ReportingError
)

# Example usage
def some_method(self):
    try:
        # Some operation
        result = perform_operation()
        return result
    except Exception as e:
        raise AnalysisError(f"Operation failed: {str(e)}")
```

### 3. Testing

Create thorough tests for your plugins:

```python
import pytest
from summit_seo.analyzers import BaseAnalyzer
from summit_seo_myplugin.analyzers import MyAnalyzer

def test_my_analyzer_init():
    analyzer = MyAnalyzer()
    assert analyzer.name == "my_analyzer"
    assert isinstance(analyzer, BaseAnalyzer)

def test_my_analyzer_analyze():
    # Create test data
    analyzer = MyAnalyzer()
    processed_data = create_test_processed_data()
    
    # Run the analyzer
    results = analyzer.analyze(processed_data)
    
    # Check results
    assert 'findings' in results
    assert len(results['findings']) > 0
```

### 4. Versioning

Use semantic versioning for your plugins:

- Major version: Breaking changes
- Minor version: New features, non-breaking
- Patch version: Bug fixes

### 5. Performance

Consider performance implications:

- Optimize expensive operations
- Use caching where appropriate
- Process data in chunks if large
- Implement timeouts for external calls

## Troubleshooting

### Common Issues

#### Plugin Not Found

**Symptom**: Your plugin doesn't appear in the available plugins list.

**Solutions**:
- Verify that your plugin is properly registered
- Check entry points in setup.py
- Ensure your plugin module is in the Python path
- Check for import errors in your plugin

#### Configuration Errors

**Symptom**: You get a `ConfigurationError` when using your plugin.

**Solutions**:
- Implement `validate_config` to provide clear error messages
- Check that required configuration values are provided
- Ensure configuration values have the correct types

#### Integration Issues

**Symptom**: Your plugin doesn't integrate properly with the core application.

**Solutions**:
- Ensure your plugin follows the contract of the base class
- Check that you're returning the expected data structures
- Verify that your plugin handles all edge cases

### Debugging Plugins

To debug your plugins:

```python
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MyDebugAnalyzer(BaseAnalyzer):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "debug_analyzer"
        
    def _analyze(self, processed_data):
        logger.debug("Starting analysis")
        logger.debug(f"Processed data: {processed_data}")
        
        # Your analysis logic
        
        logger.debug("Analysis complete")
        return results
```

### Getting Help

If you encounter issues developing plugins:

- Check the [Summit SEO documentation](https://docs.summit-seo.org)
- Review the [API reference](https://docs.summit-seo.org/api)
- Join the [community forum](https://forum.summit-seo.org)
- File an issue on [GitHub](https://github.com/summit-seo/summit-seo) 