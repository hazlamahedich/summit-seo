# Summit SEO API Reference

This documentation provides a comprehensive reference for the Summit SEO API, including core classes, methods, and usage examples.

## Table of Contents

1. [Core Components](#core-components)
   - [SummitSEO](#summitseo)
   - [Analyzers](#analyzers)
   - [Collectors](#collectors)
   - [Processors](#processors)
   - [Reporters](#reporters)
2. [Configuration](#configuration)
3. [Analysis Results](#analysis-results)
4. [Error Handling](#error-handling)
5. [Extension Points](#extension-points)
6. [CLI Interface](#cli-interface)

## Core Components

### SummitSEO

The `SummitSEO` class is the main entry point for analysis functionality.

```python
from summit_seo import SummitSEO

# Create instance with default configuration
seo = SummitSEO()

# Create instance with custom configuration
seo = SummitSEO(config={
    'max_pages': 100,
    'max_depth': 3,
    'user_agent': 'SummitSEO/1.0',
    'analyzers': ['content', 'security', 'performance']
})

# Analyze a URL
results = seo.analyze_url('https://example.com')

# Analyze local HTML file
results = seo.analyze_file('path/to/file.html')

# Analyze HTML content directly
results = seo.analyze_html('<html>...</html>', base_url='https://example.com')
```

#### Methods

| Method | Description | Parameters | Return Value |
| ------ | ----------- | ---------- | ------------ |
| `__init__(config=None)` | Constructor | `config`: Dictionary with configuration options | `SummitSEO` instance |
| `analyze_url(url, options=None)` | Analyze a URL | `url`: Target URL<br>`options`: Analysis options | `AnalysisResult` object |
| `analyze_file(file_path, options=None)` | Analyze a local HTML file | `file_path`: Path to HTML file<br>`options`: Analysis options | `AnalysisResult` object |
| `analyze_html(html, base_url=None, options=None)` | Analyze HTML content | `html`: HTML content string<br>`base_url`: Base URL for relative links<br>`options`: Analysis options | `AnalysisResult` object |
| `get_collectors()` | Get available collectors | None | List of collector names |
| `get_processors()` | Get available processors | None | List of processor names |
| `get_analyzers()` | Get available analyzers | None | List of analyzer names |
| `get_reporters()` | Get available reporters | None | List of reporter names |

### Analyzers

Analyzers are responsible for evaluating specific aspects of a webpage or website.

#### BaseAnalyzer

All analyzers inherit from the `BaseAnalyzer` class:

```python
from summit_seo.analyzers import BaseAnalyzer

class MyCustomAnalyzer(BaseAnalyzer):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "custom"
        self.description = "My custom analyzer"
        
    def _analyze(self, processed_data):
        # Implement analysis logic here
        results = {}
        # Add analysis results
        return results
        
    def compute_score(self, results):
        # Implement scoring logic
        return 85  # Example score
```

#### Built-in Analyzers

| Analyzer | Class | Description |
| -------- | ----- | ----------- |
| Content Analyzer | `ContentAnalyzer` | Analyzes page content, keywords, and structure |
| Security Analyzer | `SecurityAnalyzer` | Evaluates security aspects like HTTPS, cookies, XSS |
| Performance Analyzer | `PerformanceAnalyzer` | Checks performance metrics and optimizations |
| Schema Analyzer | `SchemaAnalyzer` | Validates schema.org markup implementation |
| Accessibility Analyzer | `AccessibilityAnalyzer` | Checks for accessibility compliance |
| Mobile Friendly Analyzer | `MobileFriendlyAnalyzer` | Assesses mobile optimization |
| Social Media Analyzer | `SocialMediaAnalyzer` | Evaluates social media integration |

#### Example: Using SecurityAnalyzer

```python
from summit_seo.analyzers import SecurityAnalyzer

# Create and configure the analyzer
security = SecurityAnalyzer(config={
    'check_https': True,
    'check_cookies': True,
    'check_xss': True,
    'check_libraries': True,
    'severity_threshold': 'medium'
})

# Process data should come from a processor
security_results = security.analyze(processed_data)

# Get just the score
score = security.compute_score(security_results)
```

### Collectors

Collectors are responsible for retrieving web content for analysis.

#### BaseCollector

All collectors inherit from the `BaseCollector` class:

```python
from summit_seo.collectors import BaseCollector

class MyCustomCollector(BaseCollector):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "custom"
        
    def collect(self, target):
        # Implement collection logic
        result = {}
        # Add collected data
        return result
```

#### Built-in Collectors

| Collector | Class | Description |
| --------- | ----- | ----------- |
| Web Page Collector | `WebPageCollector` | Collects HTML from web URLs |
| File Collector | `FileCollector` | Reads HTML from local files |
| Headless Browser Collector | `BrowserCollector` | Uses headless browser for JavaScript-heavy sites |
| Site Crawler | `SiteCrawler` | Crawls multiple pages from a site |

#### Example: Using WebPageCollector

```python
from summit_seo.collectors import WebPageCollector

collector = WebPageCollector(config={
    'timeout': 30,
    'user_agent': 'SummitSEO/1.0',
    'headers': {'Accept-Language': 'en-US'},
    'verify_ssl': True
})

# Collect data from a URL
collection_result = collector.collect('https://example.com')

# Access the HTML content
html_content = collection_result.content

# Access metadata
status_code = collection_result.metadata.get('status_code')
content_type = collection_result.metadata.get('content_type')
```

### Processors

Processors transform collected data into a format suitable for analysis.

#### BaseProcessor

All processors inherit from the `BaseProcessor` class:

```python
from summit_seo.processors import BaseProcessor

class MyCustomProcessor(BaseProcessor):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "custom"
        
    def process(self, collection_result):
        # Implement processing logic
        processed_data = {}
        # Transform collected data
        return processed_data
```

#### Built-in Processors

| Processor | Class | Description |
| --------- | ----- | ----------- |
| HTML Processor | `HTMLProcessor` | Processes HTML content |
| Sitemap Processor | `SitemapProcessor` | Processes XML sitemaps |
| Robots Processor | `RobotsProcessor` | Processes robots.txt files |
| Resource Processor | `ResourceProcessor` | Processes page resources (JS, CSS, images) |

#### Example: Using HTMLProcessor

```python
from summit_seo.processors import HTMLProcessor

processor = HTMLProcessor(config={
    'parse_javascript': True,
    'extract_metadata': True,
    'extract_links': True
})

# Process the collection result
processed_data = processor.process(collection_result)

# Access the parsed document
document = processed_data.document

# Access extracted metadata
title = processed_data.metadata.get('title')
description = processed_data.metadata.get('description')

# Access links
links = processed_data.links
```

### Reporters

Reporters generate output formats from analysis results.

#### BaseReporter

All reporters inherit from the `BaseReporter` class:

```python
from summit_seo.reporters import BaseReporter

class MyCustomReporter(BaseReporter):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "custom"
        self.format = "custom"
        
    def generate(self, analysis_result):
        # Implement report generation logic
        report = ""
        # Generate report from analysis result
        return report
```

#### Built-in Reporters

| Reporter | Class | Description |
| -------- | ----- | ----------- |
| Console Reporter | `ConsoleReporter` | Outputs to terminal |
| JSON Reporter | `JSONReporter` | Generates JSON reports |
| HTML Reporter | `HTMLReporter` | Creates HTML reports |
| CSV Reporter | `CSVReporter` | Produces CSV reports |
| PDF Reporter | `PDFReporter` | Generates PDF reports |
| Markdown Reporter | `MarkdownReporter` | Creates Markdown reports |

#### Example: Using HTMLReporter

```python
from summit_seo.reporters import HTMLReporter

reporter = HTMLReporter(config={
    'template': 'default',
    'include_charts': True,
    'detailed': True
})

# Generate a report from the analysis result
report = reporter.generate(analysis_result)

# Save the report to a file
with open('seo_report.html', 'w') as f:
    f.write(report)
```

## Configuration

Summit SEO uses a configuration system for customizing behavior.

### Configuration Options

```python
default_config = {
    # General settings
    'user_agent': 'SummitSEO/1.0',
    'timeout': 30,
    'verify_ssl': True,
    'max_retries': 3,
    'retry_delay': 1,
    
    # Collection settings
    'max_pages': 100,
    'max_depth': 3,
    'follow_external_links': False,
    'respect_robots_txt': True,
    'headers': {},
    
    # Processing settings
    'parse_javascript': False,
    'extract_metadata': True,
    'extract_links': True,
    'normalize_urls': True,
    
    # Analysis settings
    'analyzers': ['all'],
    'analyze_performance': True,
    'analyze_security': True,
    'analyze_schema': True,
    'analyze_accessibility': True,
    'analyze_mobile': True,
    'analyze_social': True,
    
    # Reporting settings
    'report_format': 'html',
    'report_detail_level': 'detailed',
    'include_charts': True,
    'include_recommendations': True,
    
    # Performance settings
    'parallel': True,
    'max_workers': 4,
    'use_cache': True,
    'cache_ttl': 3600,
    'memory_limit': 0
}
```

### Configuration Methods

```python
# Using the constructor
seo = SummitSEO(config={'max_pages': 50, 'analyzers': ['security', 'performance']})

# Loading from a file
seo = SummitSEO.from_config_file('config.json')

# Loading from environment variables
seo = SummitSEO.from_environment()

# Using configuration context
with seo.config_context({'max_depth': 1}):
    results = seo.analyze_url('https://example.com')
```

## Analysis Results

The `AnalysisResult` class is used to represent the output of the analysis.

### Structure

```python
# Example analysis result structure
analysis_result = {
    'url': 'https://example.com',
    'timestamp': '2023-10-15T14:30:00Z',
    'overall_score': 87,
    'analyzers': {
        'security': {
            'score': 92,
            'findings': [
                {'type': 'https', 'status': 'pass', 'message': 'HTTPS properly configured'},
                {'type': 'cookies', 'status': 'warning', 'message': 'Missing Secure flag in cookie'},
                # More findings...
            ],
            'recommendations': [
                {'priority': 'high', 'message': 'Add Secure flag to all cookies'},
                # More recommendations...
            ]
        },
        'performance': {
            'score': 78,
            # Performance analysis results...
        },
        # Other analyzer results...
    },
    'metadata': {
        'title': 'Example Website',
        'description': 'This is an example website',
        # Other metadata...
    }
}
```

### API

```python
# Accessing analysis results
overall_score = analysis_result.overall_score
security_score = analysis_result.get_analyzer_score('security')
security_findings = analysis_result.get_analyzer_findings('security')

# Filtering findings
critical_issues = analysis_result.filter_findings(status='fail', priority='critical')
security_warnings = analysis_result.filter_findings(analyzer='security', status='warning')

# Accessing recommendations
all_recommendations = analysis_result.get_recommendations()
security_recommendations = analysis_result.get_recommendations(analyzer='security')
high_priority_recommendations = analysis_result.get_recommendations(priority='high')

# Exporting results
json_data = analysis_result.to_json()
dict_data = analysis_result.to_dict()
```

## Error Handling

Summit SEO provides a set of exception classes for error handling.

```python
from summit_seo.exceptions import *

try:
    results = seo.analyze_url('https://example.com')
except CollectionError as e:
    print(f"Failed to collect data: {e}")
except ProcessingError as e:
    print(f"Failed to process data: {e}")
except AnalysisError as e:
    print(f"Analysis failed: {e}")
except ReportingError as e:
    print(f"Failed to generate report: {e}")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except SummitSEOError as e:
    print(f"General error: {e}")
```

### Exception Hierarchy

- `SummitSEOError` - Base exception class
  - `ConfigurationError` - Configuration-related errors
  - `CollectionError` - Data collection errors
    - `ConnectionError` - Network connection issues
    - `TimeoutError` - Request timeout
    - `HTTPError` - HTTP error responses
  - `ProcessingError` - Data processing errors
    - `ParsingError` - HTML/XML parsing errors
  - `AnalysisError` - Analysis-related errors
    - `AnalyzerError` - Specific analyzer errors
  - `ReportingError` - Report generation errors
  - `ExtensionError` - Plugin/extension errors

## Extension Points

Summit SEO can be extended through various extension points.

### Creating Custom Analyzers

```python
from summit_seo.analyzers import BaseAnalyzer, register_analyzer

@register_analyzer
class CustomAnalyzer(BaseAnalyzer):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "custom"
        self.description = "My custom analyzer"
        
    def _analyze(self, processed_data):
        # Custom analysis logic
        results = {}
        # Populate results
        return results
        
    def compute_score(self, results):
        # Custom scoring logic
        return 85
```

### Creating Custom Collectors

```python
from summit_seo.collectors import BaseCollector, register_collector

@register_collector
class CustomCollector(BaseCollector):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "custom"
        
    def collect(self, target):
        # Custom collection logic
        result = {"content": "...", "metadata": {...}}
        return result
```

### Creating Custom Processors

```python
from summit_seo.processors import BaseProcessor, register_processor

@register_processor
class CustomProcessor(BaseProcessor):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "custom"
        
    def process(self, collection_result):
        # Custom processing logic
        processed_data = {...}
        return processed_data
```

### Creating Custom Reporters

```python
from summit_seo.reporters import BaseReporter, register_reporter

@register_reporter
class CustomReporter(BaseReporter):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "custom"
        self.format = "custom"
        
    def generate(self, analysis_result):
        # Custom report generation logic
        report = "..."
        return report
```

## CLI Interface

Summit SEO provides a command-line interface for executing analyses.

### Basic Commands

```bash
# Analyze a URL
summit-seo analyze --url https://example.com

# Analyze a file
summit-seo analyze --file path/to/file.html

# Analyze multiple URLs
summit-seo analyze --url-list urls.txt

# Analyze with specific analyzers
summit-seo analyze --url https://example.com --analyzers security,performance

# Generate a specific report format
summit-seo analyze --url https://example.com --format json --output report.json

# Use a configuration file
summit-seo analyze --url https://example.com --config my-config.json
```

### Advanced Commands

```bash
# Crawl a site with depth limit
summit-seo crawl --url https://example.com --max-depth 3 --max-pages 100

# Run a focused security audit
summit-seo security-audit --url https://example.com

# Run a performance analysis
summit-seo performance-analysis --url https://example.com

# Generate a comparison report
summit-seo compare --before before.json --after after.json --output comparison.html

# Validate schema.org markup
summit-seo validate-schema --url https://example.com

# Check accessibility compliance
summit-seo accessibility-check --url https://example.com --standard wcag2.1
```

### CLI Options

```
Usage: summit-seo [command] [options]

Commands:
  analyze              Run a full analysis
  crawl                Crawl a website
  security-audit       Run a security audit
  performance-analysis Run a performance analysis
  validate-schema      Validate schema.org markup
  accessibility-check  Check accessibility compliance
  compare              Compare analysis results
  list-analyzers       List available analyzers
  version              Show version information

Common Options:
  --url URL            Target URL to analyze
  --file FILE          Local HTML file to analyze
  --url-list FILE      File containing URLs to analyze
  --format FORMAT      Output format (html, json, csv, md, pdf)
  --output FILE        Output file for the report
  --config FILE        Configuration file
  --analyzers LIST     Comma-separated list of analyzers to use
  --log-level LEVEL    Logging level (debug, info, warning, error)
  --quiet              Suppress output
  --verbose            Increase output verbosity
  --version            Show version information and exit
  --help               Show this help message and exit

For more information, use --help with a specific command:
  summit-seo analyze --help
``` 