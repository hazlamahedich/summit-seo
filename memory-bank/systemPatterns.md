# System Architecture and Patterns

## Core Architecture

The Summit SEO system consists of four primary modules that form a pipeline for SEO analysis:

1. **Collector Module**: Gathers raw data from websites or files
2. **Processor Module**: Processes and structures raw data for analysis
3. **Analyzer Module**: Analyzes processed data to generate SEO insights
4. **Reporter Module**: Transforms analysis results into structured reports

### Collector Module
The collector module is responsible for gathering raw data:

1. Abstract Base Class Pattern
   - `BaseCollector` defines the interface for all collectors
   - Abstract methods enforce implementation of key functionality
   - Asynchronous API for efficient data collection

2. Factory Pattern
   - `CollectorFactory` manages collector creation
   - Dynamic registration of collector implementations
   - Type-safe instantiation with configuration support

3. Data Class Pattern
   - `CollectionResult` for structured collected data
   - Clear separation of content and metadata

### Processor Module
The processor module transforms raw data into structured formats:

1. Abstract Base Class Pattern
   - `BaseProcessor` defines the interface for all processors
   - Abstract methods enforce implementation of key functionality
   - Consistent validation approach across implementations

2. Factory Pattern
   - `ProcessorFactory` manages processor creation
   - Dynamic registration of processor implementations
   - Type-safe instantiation with configuration support

3. Specialized Implementations
   - `HTMLProcessor`: Processes HTML content
   - `JavaScriptProcessor`: Analyzes JavaScript code
   - `CSSProcessor`: Analyzes CSS styles
   - `RobotsTxtProcessor`: Processes robots.txt files
   - `SitemapProcessor`: Processes XML sitemaps

### Analyzer Module
The analyzer module generates SEO insights from processed data:

1. Abstract Base Class Pattern
   - `BaseAnalyzer` defines the interface for all analyzers
   - Abstract methods enforce implementation of key functionality
   - Generic type support for type-safe input/output handling

2. Factory Pattern
   - `AnalyzerFactory` manages analyzer creation
   - Dynamic registration of analyzer implementations
   - Type-safe instantiation with configuration support

3. Data Class Pattern
   - `AnalysisResult` and `AnalysisMetadata` for structured data
   - Immutable data structures
   - Clear separation of analysis data and metadata

4. Specialized Implementations
   - `ContentAnalyzer`: Analyzes webpage content
   - `MetaAnalyzer`: Analyzes meta information
   - `LinkAnalyzer`: Analyzes link structures
   - `SecurityAnalyzer`: Analyzes security aspects
   - `PerformanceAnalyzer`: Analyzes performance aspects
   - `SchemaAnalyzer`: Analyzes schema markup
   - `AccessibilityAnalyzer`: Analyzes accessibility aspects
   - `MobileFriendlyAnalyzer`: Analyzes mobile-friendliness
   - `SocialMediaAnalyzer`: Analyzes social media optimization

5. Recommendation (recommendation.py)
   - `Recommendation`: Dataclass for recommendation objects
   - `RecommendationBuilder`: Builder for creating recommendations
   - `RecommendationManager`: Manager for organizing recommendations
   - `RecommendationSeverity`: Enum for recommendation severity
   - `RecommendationPriority`: Enum for recommendation priority

### Reporter Module
The reporter module transforms analysis results into reports:

1. Abstract Base Class Pattern
   - `BaseReporter` defines the interface for all reporters
   - Abstract methods enforce implementation of key functionality
   - Generic type support for type-safe input handling

2. Factory Pattern
   - `ReporterFactory` manages reporter creation
   - Dynamic registration of reporter implementations
   - Type-safe instantiation with configuration support

3. Data Class Pattern
   - `ReportResult` and `ReportMetadata` for structured data
   - Immutable data structures
   - Clear separation of data and metadata

4. Strategy Pattern
   - Different reporter implementations for different formats
   - Common interface through BaseReporter
   - Configurable behavior through initialization options

5. Specialized Implementations
   - `JSONReporter`: Generates JSON reports
   - `HTMLReporter`: Generates HTML reports
   - `XMLReporter`: Generates XML reports
   - `PDFReporter`: Generates PDF reports
   - `CSVReporter`: Generates CSV reports

## Complete System Architecture
```
Summit SEO
├── Collector Module
│   ├── Base (base.py)
│   │   ├── BaseCollector [abstract]
│   │   ├── CollectionResult [dataclass]
│   │   └── CollectorError [exception]
│   ├── Factory (factory.py)
│   │   └── CollectorFactory [static]
│   └── Implementations
│       └── WebPageCollector (webpage_collector.py)
│
├── Processor Module
│   ├── Base (base.py)
│   │   ├── BaseProcessor [abstract]
│   │   └── ProcessorError [exception]
│   ├── Factory (factory.py)
│   │   └── ProcessorFactory [static]
│   └── Implementations
│       ├── HTMLProcessor (html_processor.py)
│       ├── JavaScriptProcessor (javascript_processor.py)
│       ├── CSSProcessor (css_processor.py)
│       ├── RobotsTxtProcessor (robotstxt_processor.py)
│       └── SitemapProcessor (sitemap_processor.py)
│
├── Analyzer Module
│   ├── Base (base.py)
│   │   ├── BaseAnalyzer [abstract]
│   │   ├── AnalysisResult [dataclass]
│   │   ├── AnalysisMetadata [dataclass]
│   │   └── AnalyzerError [exception]
│   ├── Factory (factory.py)
│   │   └── AnalyzerFactory [static]
│   ├── Recommendation (recommendation.py)
│   │   ├── Recommendation [dataclass]
│   │   ├── RecommendationBuilder [builder]
│   │   ├── RecommendationManager [manager]
│   │   ├── RecommendationSeverity [enum]
│   │   └── RecommendationPriority [enum]
│   └── Implementations
│       ├── ContentAnalyzer (content_analyzer.py)
│       ├── MetaAnalyzer (meta_analyzer.py)
│       ├── LinkAnalyzer (link_analyzer.py)
│       ├── SecurityAnalyzer (security_analyzer.py)
│       ├── PerformanceAnalyzer (performance_analyzer.py)
│       ├── SchemaAnalyzer (schema_analyzer.py)
│       ├── AccessibilityAnalyzer (accessibility_analyzer.py)
│       ├── MobileFriendlyAnalyzer (mobile_friendly_analyzer.py)
│       └── SocialMediaAnalyzer (social_media_analyzer.py)
│
└── Reporter Module
    ├── Base (base.py)
    │   ├── BaseReporter [abstract]
    │   ├── ReportResult [dataclass]
    │   ├── ReportMetadata [dataclass]
    │   └── ReportGenerationError [exception]
    ├── Factory (factory.py)
    │   └── ReporterFactory [static]
    └── Implementations
        ├── JSONReporter (json_reporter.py)
        ├── HTMLReporter (html_reporter.py)
        ├── XMLReporter (xml_reporter.py)
        ├── PDFReporter (pdf_reporter.py)
        └── CSVReporter (csv_reporter.py)
```

## Data Flow
```
1. Collector → Raw Data (HTML, JavaScript, CSS, etc.)
   │
2. Processor → Structured Data (Parsed DOM, Analysis, etc.)
   │
3. Analyzer → SEO Insights (Issues, Recommendations, Metrics)
   │
4. Reporter → Formatted Reports (JSON, HTML, PDF, etc.)
```

## Key Design Patterns

### Factory Pattern
Used throughout the system for component creation:
```python
# Example: Creating a reporter
reporter = ReporterFactory.create("pdf", config={"output_path": "report.pdf"})

# Example: Creating an analyzer
analyzer = AnalyzerFactory.create("content")
```

### Builder Pattern
Used for complex object construction with fluent API:
```python
# Creating a recommendation using the builder pattern
recommendation = (RecommendationBuilder("Use HTTPS")
                 .with_severity(RecommendationSeverity.HIGH)
                 .with_priority(RecommendationPriority.P1)
                 .with_code_example("RewriteEngine On\nRewriteCond %{HTTPS} off\nRewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]")
                 .with_steps(["Enable HTTPS on your server", "Update internal links to use HTTPS"])
                 .mark_as_quick_win()
                 .with_impact("Improves security and SEO ranking")
                 .with_difficulty("medium")
                 .with_resource_link("Let's Encrypt", "https://letsencrypt.org/")
                 .build())
```

### Strategy Pattern
Used to encapsulate different implementations with the same interface:
```python
# All reporters share the same interface
json_reporter = ReporterFactory.create("json")
html_reporter = ReporterFactory.create("html")

# Both can be used with the same method call
json_result = await json_reporter.generate_report(analysis_data)
```

### Manager Pattern
Used to organize and filter collections of objects:
```python
# Example: Managing and filtering recommendations
manager = RecommendationManager()
manager.add(recommendation1)
manager.add(recommendation2)
manager.add(recommendation3)

# Get recommendations by different criteria
priority_ordered = manager.get_priority_ordered()
severity_ordered = manager.get_severity_ordered()
quick_wins = manager.get_quick_wins()
easy_fixes = manager.get_by_difficulty("easy")
```

### Enum Pattern
Used for type-safe categorical values:
```python
# Using enums for recommendation classification
class RecommendationSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class RecommendationPriority(Enum):
    P0 = 0  # Must fix immediately
    P1 = 1  # High priority
    P2 = 2  # Medium priority
    P3 = 3  # Low priority
    P4 = 4  # Nice to have
```

### Observer Pattern
Used for monitoring progress and collecting metrics (planned for Phase 3).

### Lazy Import Pattern
Used to prevent circular imports and improve module loading performance:

```python
# In __init__.py, use properties for lazy loading
__all__ = [
    'cli', 
    'AnalyzerFactory', 
    'CollectorFactory', 
    'ProcessorFactory', 
    'ReporterFactory',
    'CacheFactory',
    'cache_manager',
    'ParallelManager',
    'parallel_manager'
]

# Define getter functions to lazily import modules when needed
def get_analyzer_factory():
    from .analyzer import AnalyzerFactory
    return AnalyzerFactory

def get_collector_factory():
    from .collector import CollectorFactory
    return CollectorFactory

# Setup properties for lazy loading
AnalyzerFactory = property(lambda _: get_analyzer_factory())
CollectorFactory = property(lambda _: get_collector_factory())
```

### Memory Management Patterns

#### Monitoring Pattern
Centralized memory monitoring with callbacks:

```python
# Memory monitor provides a single source of truth for memory usage
memory_monitor = MemoryMonitor(poll_interval=1.0)
memory_monitor.start_monitoring()

# Components can register for memory usage notifications
def memory_callback(usage_stats):
    if usage_stats.percent > 80:
        # Take action to reduce memory usage
        pass

memory_monitor.register_callback(memory_callback)
```

#### Threshold Action Pattern
Configurable actions based on memory thresholds:

```python
# Memory limiter enforces memory limits with different actions
memory_limiter = MemoryLimiter(monitor=memory_monitor)

# Add thresholds with different actions
memory_limiter.add_threshold(
    limit=500, 
    action=LimitAction.WARN,
    limit_unit=MemoryUnit.MB
)
memory_limiter.add_threshold(
    limit=700, 
    action=LimitAction.THROTTLE,
    limit_unit=MemoryUnit.MB
)
memory_limiter.add_threshold(
    limit=900, 
    action=LimitAction.GC,
    limit_unit=MemoryUnit.MB
)
memory_limiter.add_threshold(
    limit=950, 
    action=LimitAction.ERROR,
    limit_unit=MemoryUnit.MB
)
```

### Parallel Processing Patterns

#### Task Abstraction Pattern
Encapsulating units of work with metadata:

```python
# Create a task with metadata
task = Task(
    coro=async_function(),
    id="unique-task-id",
    name="Task Name",
    priority=TaskPriority.HIGH,
    dependencies=["other-task-id"],
    timeout=30.0
)

# Tasks can be grouped for collective management
task_group = TaskGroup(
    name="Task Group",
    tasks=[task1, task2, task3]
)
```

#### Execution Strategy Pattern
Pluggable strategies for task execution:

```python
# Create an executor with a specific execution strategy
executor = ParallelExecutor(
    max_workers=10,
    execution_strategy=ExecutionStrategy.PRIORITY
)

# Change strategy at runtime
executor.execution_strategy = ExecutionStrategy.DEPENDENCY
```

#### Worker Pool Pattern
Managing a pool of worker threads/processes:

```python
# Worker pool with automatic scaling
manager = ParallelManager(
    num_workers=8,
    min_workers=2,
    max_workers=16,
    idle_timeout=60.0,
    executor_type='thread'
)

# Submit tasks to the pool
task = await manager.submit(
    func=process_url,
    args=("https://example.com",),
    priority=TaskPriority.NORMAL
)
```

## Design Decisions

### Asynchronous API
- All major operations are asynchronous for better performance
- Allows for concurrent processing of multiple tasks
- Uses Python's asyncio framework

### Type Safety
- Using TypeVar and Generic for type-safe implementations
- Static type checking support with mypy
- Clear type hints for all public interfaces

### Configuration
- Dictionary-based configuration for flexibility
- Default values for common options
- Module-specific configuration support

### Error Handling
- Custom exception hierarchy
- Validation at multiple levels
- Clear error messages for debugging

### Extensibility
- Easy addition of new implementations
- Consistent interfaces across modules
- Modular design for independent components

## Technical Constraints
- Python 3.8+ required for asyncio and typing features
- Dependencies carefully managed for maintainability
- Memory and performance considerations for large websites

## Phase 3 Architecture Extensions
1. Additional Analyzers
   - Security Analyzer
   - Performance Analyzer
   - Schema.org Analyzer
   - Accessibility Analyzer
   - Mobile Friendly Analyzer
   - Social Media Analyzer

2. Performance Optimization
   - Caching mechanisms
   - Parallel processing
   - Memory optimization

3. Advanced Features
   - Template system for reports
   - Advanced visualization components
   - Machine learning integration for recommendations

This document will be updated as the system architecture evolves.

## Security Analyzer Architecture

The Security Analyzer follows the established analyzer pattern but incorporates specialized security analysis capabilities:

### Design Principles
1. **Modular Security Checks**: Each security aspect is implemented as a separate internal method
2. **Severity Classification**: Issues are classified as high, medium, or low severity
3. **Actionable Remediation**: Each issue includes specific remediation instructions
4. **Comprehensive Scoring**: Security score calculated based on weighted severity counts

### Security Analyzer Components

#### Core Analysis Engine
- Integrates multiple security check modules
- Aggregates results into a unified security analysis
- Calculates overall security score based on issue severity

#### Security Check Modules
1. **HTTPS Analysis**: Validates secure protocol usage
   - Detects non-HTTPS connections
   - Validates HSTS implementation
   - Checks for insecure form submissions
   - Validates canonical link protocols

2. **Mixed Content Detection**: Identifies insecure resources
   - Scans for HTTP resources on HTTPS pages
   - Checks elements like images, scripts, stylesheets
   - Validates inline content security

3. **Cookie Security Analysis**: Examines cookie implementation
   - Validates Secure flag usage
   - Checks HttpOnly flag implementation
   - Verifies SameSite attribute
   - Analyzes secure cookie transmission

4. **Content Security Policy Analysis**: Validates CSP implementation
   - Checks for CSP header presence
   - Identifies unsafe directives
   - Validates required directive presence
   - Verifies reporting directive implementation

5. **XSS Vulnerability Detection**: Identifies potential XSS vectors
   - Detects unsafe event handlers
   - Identifies dangerous JavaScript functions
   - Checks for JavaScript URL usage
   - Evaluates input sanitization
   - Validates CSRF protection

6. **Sensitive Data Exposure Detection**: Identifies exposed sensitive information
   - Detects PII exposure
   - Identifies password exposure
   - Checks for API key exposure
   - Scans for credit card information
   - Validates sensitive form handling

7. **Outdated Library Detection**: Identifies vulnerable dependencies
   - Checks JavaScript library versions
   - Correlates with known CVE vulnerabilities
   - Compares against safe versions
   - Provides update recommendations

#### Output Format
- Structured security issues list with severity classification
- Actionable remediation steps for each issue
- Overall security score (0-100)
- Categorized warnings for potential issues
- Comprehensive recommendations for security improvements

## Component Interaction Patterns

### Data Flow
1. A Collector gathers raw input data
2. A Processor transforms the data into a structured format
3. Multiple Analyzers examine different aspects of the structured data
4. Reporters transform the analysis results into various output formats

### Configuration Flow
1. Base configuration is defined at the top level
2. Configuration is passed to the factory when creating a component
3. Factory merges the provided configuration with defaults
4. Component receives the merged configuration and validates it

### Error Handling
1. Each component implements appropriate error handling
2. Errors are propagated up the chain with appropriate context
3. User-friendly error messages are provided
4. Recoverable errors are handled gracefully when possible

## Extension Points

The system is designed for extensibility at multiple levels:

1. **New Component Types**: New component categories can be added
2. **New Implementations**: New implementations of existing component types can be registered
3. **Configuration Extensions**: Component behavior can be modified through configuration
4. **Analysis Extensions**: Existing analyzers can be extended with new analysis types
5. **Output Formats**: New reporter implementations can be added for different output formats

## Performance Considerations

### Caching
- Result caching for repeated operations
- File-based caching for persistent storage
- Memory caching for performance-critical operations

### Parallel Processing
- Async I/O for network operations
- Multiprocessing for CPU-bound operations
- Configurable parallelism levels

### Resource Management
- Automatic resource cleanup
- Memory usage monitoring
- Configurable resource limits

## Security Analyzer Usage Examples

### Basic Security Analysis
```python
from summit_seo.analyzer import AnalyzerFactory

# Create a security analyzer
security_analyzer = AnalyzerFactory.create('security')

# Analyze HTML content
result = security_analyzer.analyze(html_content)

# Access security score
security_score = result.score

# Access security issues
security_issues = result.issues

# Access recommendations
recommendations = result.recommendations
```

### Advanced Configuration
```python
from summit_seo.analyzer import AnalyzerFactory

# Create a security analyzer with custom configuration
config = {
    'check_https': True,
    'check_mixed_content': True,
    'check_cookies': True,
    'check_csp': True,
    'check_xss': True,
    'check_sensitive_data': True,
    'check_outdated_libraries': True,
    'page_url': 'https://example.com',
    'additional_sensitive_patterns': {
        'custom_api_key': r'api_key_custom[_\-]?[kK]ey["\']?\s*[=:]\s*["\']?[\w\-]{16,}'
    }
}

security_analyzer = AnalyzerFactory.create('security', config)
result = security_analyzer.analyze(html_content)
```

# Summit SEO Project Architecture

## System Overview

The Summit SEO toolkit is designed as a modular, component-based system for analyzing websites for SEO optimization. The system follows a pipeline architecture where data flows through multiple components:

1. **Collectors** gather raw data from various sources (URLs, files)
2. **Processors** transform raw data into structured formats
3. **Analyzers** evaluate the processed data to provide insights
4. **Reporters** format and present the analysis results

## Design Patterns

### Factory Pattern

All major components utilize the Factory pattern for instantiation:

- `AnalyzerFactory` manages all analyzer instances
- `CollectorFactory` manages all collector instances 
- `ProcessorFactory` manages all processor instances
- `ReporterFactory` manages all reporter instances

This provides:
- Centralized component registration
- Runtime component discovery
- Configuration inheritance
- Component lifecycle management

Example:
```python
# Registering an analyzer
AnalyzerFactory.register("content", ContentAnalyzer)

# Creating an analyzer instance
analyzer = AnalyzerFactory.create("content", config)
```

### Base Classes and Inheritance

Each component type has a base class that defines the interface and common functionality:

- `BaseAnalyzer` - Common analyzer interface and functionality
- `BaseCollector` - Common collector interface and functionality
- `BaseProcessor` - Common processor interface and functionality
- `BaseReporter` - Common reporter interface and functionality

This provides:
- Consistent interfaces across components
- Shared utility methods
- Configuration validation
- Error handling

### Strategy Pattern

Different analysis strategies are implemented as separate analyzer classes:

- `ContentAnalyzer` for analyzing page content
- `MetaAnalyzer` for analyzing meta tags
- `LinkAnalyzer` for analyzing links
- `SecurityAnalyzer` for analyzing security aspects
- `PerformanceAnalyzer` for analyzing page performance
- `SchemaAnalyzer` for analyzing schema markup
- `AccessibilityAnalyzer` for analyzing accessibility
- `MobileFriendlyAnalyzer` for analyzing mobile-friendliness
- `SocialMediaAnalyzer` for analyzing social media optimization

This allows:
- Swapping analysis strategies
- Focused, single-responsibility components
- Easier testing and maintenance
- Configuration of specific strategies

### Pipeline Pattern

Data flows through a pipeline of components:

`Collector -> Processor -> Analyzer -> Reporter`

This provides:
- Clear separation of concerns
- Processing stages that can be reconfigured
- Ability to insert custom components
- Parallel processing capabilities

### Observer Pattern

Components can register observers to track their progress and receive notifications:

- Progress tracking during long-running operations
- Status updates during processing
- Error notifications
- Result broadcasting

### Configuration System

A hierarchical configuration system allows:

- Global default configuration
- Component-type configuration
- Instance-specific configuration
- Configuration inheritance
- Runtime configuration changes

Example:
```python
config = {
    "global": {
        "timeout": 30,
        "user_agent": "Summit SEO Bot"
    },
    "analyzers": {
        "content": {
            "min_content_length": 300,
            "check_grammar": True
        }
    }
}
```

## Component Architecture

### Analyzers

All analyzers follow a common pattern:

1. Inherit from `BaseAnalyzer`
2. Implement the `_analyze` method
3. Return results as `AnalysisResult` objects
4. Register with the `AnalyzerFactory`

```python
class ExampleAnalyzer(BaseAnalyzer):
    def _analyze(self, data):
        # Analysis logic here
        result = AnalysisResult()
        
        # Add findings, scores, etc.
        result.add_finding("example", "Example finding")
        result.set_score(85)
        
        return result
```

#### Content Analyzer

- Analyzes page content for SEO optimization
- Checks keyword usage, density, and placement
- Evaluates readability and structure
- Analyzes heading hierarchy and distribution

#### Meta Analyzer

- Analyzes meta tags for SEO optimization
- Checks title, description, and keywords
- Evaluates robots directives
- Analyzes canonical tags and other SEO-related meta tags

#### Security Analyzer

- Analyzes website security aspects related to SEO
- Checks for HTTPS implementation
- Detects mixed content issues
- Analyzes cookie security
- Evaluates content security policy
- Detects common vulnerabilities
- Identifies sensitive data exposure
- Detects outdated libraries with known vulnerabilities

#### Performance Analyzer

- Analyzes page performance aspects related to SEO
- Evaluates page size and resource counts
- Detects render-blocking resources
- Analyzes image optimization
- Checks for minification, compression, and caching
- Evaluates font loading strategies

#### Schema Analyzer

- Analyzes schema.org markup for SEO
- Supports JSON-LD, Microdata, and RDFa formats
- Validates required and recommended properties
- Ensures proper context and types
- Recommends schema enhancements

#### Accessibility Analyzer

- Analyzes accessibility aspects related to SEO
- Checks WCAG 2.1 compliance factors
- Evaluates screen reader compatibility
- Analyzes keyboard navigation
- Checks color contrast and form accessibility
- Validates alternative text and ARIA roles
- Evaluates focus indicators and skip navigation

#### Mobile Friendly Analyzer

- Analyzes mobile-friendliness aspects related to SEO
- Checks viewport configuration
- Evaluates responsive design implementation
- Validates touch target sizes
- Analyzes font sizes for readability
- Checks content width and horizontal scrolling
- Detects mobile-first approach
- Evaluates PWA features and mobile meta tags

#### Social Media Analyzer

- Analyzes social media optimization aspects related to SEO
- Validates Open Graph meta tags (og:title, og:type, og:image, og:url)
- Checks Twitter Card implementation
- Evaluates Facebook Insights integration
- Analyzes LinkedIn, Pinterest, and other platform optimizations
- Detects social sharing buttons and functionality
- Evaluates social signal indicators
- Checks social media profile links and embeds
- Provides comprehensive social media optimization recommendations

### Social Media Analyzer Implementation Pattern

The Social Media Analyzer follows a structured pattern for evaluating social media optimization:

1. **Tag Detection and Validation**
   - Uses BeautifulSoup to locate and extract social media tags
   - Implements specialized methods for each platform (Open Graph, Twitter, Facebook, etc.)
   - Validates required and recommended tags for each platform
   - Checks for proper formatting and content of tag values

2. **Element Detection**
   - Identifies social sharing buttons through class and ID patterns
   - Detects embedded social media content (iframe patterns)
   - Analyzes social profile links through URL pattern matching
   - Uses regular expressions for detecting social media pixels and tracking codes

3. **Scoring Algorithm**
   - Implements a weighted scoring system for social media optimization
   - Assigns different weights to critical tags (e.g., og:title, og:image)
   - Considers platform coverage across major social networks
   - Evaluates sharing functionality and social proof elements

4. **Recommendation Generation**
   - Creates platform-specific recommendations for missing tags
   - Provides guidance on image dimensions and content types
   - Suggests social sharing implementation improvements
   - Offers detailed remediation steps with examples

5. **Result Structure**
   - Organizes findings by social media platform
   - Categorizes issues by severity (critical, high, medium, low)
   - Includes detailed scoring breakdown by category
   - Provides a comprehensive social media optimization score

Implementation Example:
```python
def _analyze_open_graph(self, soup):
    """Analyze Open Graph meta tags for social sharing optimization."""
    findings = []
    
    # Check for required Open Graph tags
    og_title = soup.find('meta', property='og:title')
    if not og_title:
        findings.append(Finding(
            'missing_og_title', 
            'Missing Open Graph title tag',
            severity=Severity.HIGH,
            remediation='Add <meta property="og:title" content="Your Title Here"> to the head section.'
        ))
    
    # Check for additional Open Graph tags
    # ... more validation logic
    
    return findings, score
```

The Social Media Analyzer module orchestrates these components to provide comprehensive analysis of a webpage's social media optimization.

### Collectors

Data collectors handle:

- Retrieving data from various sources
- Managing request policies (rate limiting, politeness)
- Handling errors and retries
- Processing collection results

#### URL Collector

- Collects data from URLs
- Handles single and multiple URLs
- Supports sitemap parsing
- Implements recursive crawling with depth limits
- Manages politeness with rate limiting and delays

#### File Collector

- Collects data from local files
- Supports directory traversal
- Implements file type filtering
- Handles different file encodings

### Processors

Data processors handle:

- Transforming raw data into structured formats
- Cleaning and normalizing data
- Extracting relevant portions
- Preliminary analysis for efficiency

#### HTML Processor

- Processes HTML content
- Cleans and normalizes HTML
- Extracts relevant elements
- Handles encoding issues
- Provides DOM structure for analyzers

#### JavaScript Processor

- Processes JavaScript content
- Analyzes script tags and external scripts
- Detects libraries and frameworks
- Identifies performance and security issues
- Supports optional minification

#### CSS Processor

- Processes CSS content
- Analyzes style tags and external stylesheets
- Evaluates selector efficiency and complexity
- Detects unused styles and duplicates
- Supports optional minification

#### Robots.txt Processor

- Processes robots.txt files
- Parses and validates directives
- Extracts sitemap URLs
- Evaluates SEO impact of directives
- Checks common path access rules

#### Sitemap Processor

- Processes XML sitemaps
- Supports sitemap index files
- Extracts URLs and metadata
- Validates sitemap structure
- Evaluates lastmod, changefreq, and priority attributes

### Reporters

Reporters handle:

- Formatting analysis results
- Generating output in various formats
- Customizing output presentation
- Filtering and prioritizing results

#### Console Reporter

- Outputs results to the console
- Supports colored output for different severities
- Displays summary statistics
- Shows detailed issue information
- Provides progress indicators

#### HTML Reporter

- Generates HTML reports
- Includes interactive UI elements
- Features collapsible sections
- Implements issue filtering
- Supports custom styling
- Incorporates data visualizations

#### JSON Reporter

- Produces structured JSON output
- Includes comprehensive data
- Follows consistent schema
- Supports API integration

#### CSV Reporter

- Creates CSV output files
- Supports custom column configuration
- Compatible with spreadsheet software
- Formats issue lists efficiently

#### XML Reporter

- Generates XML output
- Follows defined schema
- Represents hierarchical data
- Compatible with XML processing tools

#### PDF Reporter

- Creates PDF documents
- Implements styled formatting
- Includes charts and graphics
- Supports bookmarks and table of contents
- Adds page numbering and headers

## Data Models

### AnalysisResult

Stores the results of analysis:

- Overall score
- Findings (issues, warnings, suggestions)
- Metadata about the analysis
- Resource references

### Finding

Represents a specific finding from analysis:

- Type (issue, warning, suggestion)
- Severity (critical, high, medium, low)
- Message description
- Code location or element reference
- Remediation steps

### Resource

Represents a resource used or referenced:

- URL or file path
- Resource type
- Size and other metadata
- Status (OK, error, warning)

### Configuration

Manages component configuration:

- Default values
- Validation rules
- Inheritance hierarchy
- Schema definition

## Error Handling

The system implements a comprehensive error handling strategy:

- Custom exception hierarchy
- Graceful degradation
- Detailed error messages
- Error categorization
- Recovery mechanisms

Custom exceptions include:

- `AnalyzerError` for analyzer-specific errors
- `CollectorError` for collector-specific errors
- `ProcessorError` for processor-specific errors
- `ReporterError` for reporter-specific errors
- `ConfigurationError` for configuration issues

## Performance Considerations

The system addresses performance through:

- Lazy loading of components
- Caching of intermediate results
- Parallel processing where applicable
- Resource cleanup and management
- Memory usage optimization

## Extension Points

The system provides well-defined extension points:

- Custom analyzers through inheritance from `BaseAnalyzer`
- Custom collectors through inheritance from `BaseCollector`
- Custom processors through inheritance from `BaseProcessor`
- Custom reporters through inheritance from `BaseReporter`
- Custom findings through extending the Finding class
- Configuration extension through schema updates

## Validation System

A validation system ensures:

- Configuration schema validation
- Input data validation
- Output format validation
- Component compatibility validation

## Concurrency Model

The system handles concurrency through:

- Thread-safe factories
- Immutable shared data
- Lock-free algorithms where possible
- Explicit synchronization where needed
- Resource pools for expensive operations

## Testing Architecture

The testing system includes:

- Unit tests for all components
- Integration tests for component interactions
- End-to-end tests for complete workflows
- Performance benchmarks
- Resource usage monitoring

## Security Model

Security considerations include:

- Safe handling of external content
- Input validation and sanitization
- Resource usage limits
- Timeouts for external operations
- Content security policy compliance

## Caching Architecture

The Summit SEO system implements a comprehensive caching system to improve performance by eliminating redundant operations. The caching architecture follows these key design principles:

### Caching Module Structure
1. **Core Components**
   - `BaseCache`: Abstract base class defining the cache interface
   - `CacheConfig`: Configuration class for cache behavior
   - `CacheResult`: Result container with metadata
   - `CacheFactory`: Factory for creating and managing cache instances
   - `CacheManager`: High-level interface for coordinating cache operations

2. **Cache Implementations**
   - `MemoryCache`: In-memory cache with LRU eviction policy
   - `FileCache`: File-based persistent cache

3. **Integration Points**
   - Collector-level caching to avoid redundant network requests
   - Processor-level caching to avoid redundant data processing
   - Analyzer-level caching to avoid redundant analysis

### Caching Patterns

#### Factory Pattern
The `CacheFactory` manages cache creation and reuse:
```python
# Register cache implementations
CacheFactory.register('memory', MemoryCache)
CacheFactory.register('file', FileCache)

# Create or retrieve cache instances
memory_cache = CacheFactory.create('memory', config)
```

#### Strategy Pattern
Different cache backends can be selected based on requirements:
```python
# Choose memory cache for speed
config = CacheConfig(ttl=3600, cache_type='memory')

# Choose file cache for persistence
config = CacheConfig(ttl=86400, cache_type='file')
```

#### Singleton Pattern
The `CacheManager` provides a singleton interface for coordinating caches:
```python
from summit_seo import cache_manager

# Initialize cache system
cache_manager.initialize()

# Use high-level interface
await cache_manager.get(key)
await cache_manager.set(key, value)
```

#### Decorator Pattern (Planned)
Future versions will support method caching via decorators:
```python
@cache_manager.cached(ttl=3600)
async def expensive_operation(data):
    # Expensive operation here
    return result
```

### Cache Key Generation
Cache keys are generated based on:
1. Component type (Analyzer, Collector, Processor)
2. Input data (hashed for consistency)
3. Configuration parameters that affect results

This ensures cache hits only occur for truly identical operations.

### Cache Invalidation Strategies
1. **TTL-based expiration**: All cache entries have a configurable Time-To-Live
2. **LRU eviction**: When cache size limits are reached, least recently used items are removed
3. **Manual invalidation**: API for explicitly invalidating specific cache entries
4. **Namespace invalidation**: API for clearing entire categories of cache entries

### Cache Tiering
The system implements a tiered caching approach with different TTL values:
1. **Short-term cache**: 5 minutes TTL for frequently changing data
2. **Medium-term cache**: 1 hour TTL for semi-stable data
3. **Long-term cache**: 24 hours TTL for stable data

### Performance Considerations
- Memory caches prioritize speed with higher memory usage
- File caches prioritize persistence with some speed trade-offs
- Cache statistics track hit/miss rates for optimization
- Automatic cleanup of expired entries prevents memory leaks 

## Parallel Processing Architecture

The Summit SEO system implements a flexible parallel processing architecture to improve performance through concurrent execution of tasks. This architecture follows these key design principles:

### Core Components

1. **Task Abstraction**
   - `Task`: Represents a unit of work with execution metadata
   - `TaskResult`: Contains execution results and performance metrics
   - `TaskStatus`: Tracks progress through task lifecycle states

2. **Worker Implementation**
   - `Worker`: Executes individual tasks using thread or process executors
   - `WorkerPool`: Manages a collection of workers for optimal resource utilization

3. **Manager Coordination**
   - `ParallelManager`: Coordinates task submission and execution
   - `ProcessingStrategy`: Defines task execution patterns and prioritization

### Processing Strategies

#### Parallel Strategy
Executes all tasks concurrently (limited by worker count):
```python
# Execute tasks in parallel
tasks = [task1, task2, task3, task4]
results = await manager.process_tasks()  # All tasks execute concurrently
```

#### Batched Strategy
Processes tasks in configurable batch sizes:
```python
# Execute tasks in batches of 2
manager.strategy = ProcessingStrategy.BATCHED
manager.batch_size = 2
results = await manager.process_tasks()  # Processes 2 tasks at a time
```

#### Priority Strategy
Executes tasks strictly by priority order:
```python
# Submit tasks with priorities
await manager.submit(func1, priority=10)  # Higher priority
await manager.submit(func2, priority=5)   # Lower priority
results = await manager.process_tasks()  # Highest priority first
```

#### Dependency Graph Strategy
Executes tasks respecting dependencies:
```python
# Create task dependencies
task1 = await manager.submit(func1)
task2 = await manager.submit(func2)
task3 = await manager.submit(func3, dependencies=[task1, task2])
```

### Execution Patterns

#### Executor Selection
Supports both thread and process-based execution:
```python
# Thread-based execution (default)
thread_manager = ParallelManager(executor_type='thread')

# Process-based execution
process_manager = ParallelManager(executor_type='process')
```

#### Concurrency Control
Configurable limits at multiple levels:
```python
# Control total workers
manager = ParallelManager(num_workers=4)

# Control tasks per worker
manager = ParallelManager(max_tasks_per_worker=2)
```

#### Error Handling
Comprehensive error isolation and retry mechanisms:
```python
# Set retry attempts for a task
task = await manager.submit(func, max_retries=3)

# Error tracking
if task.result.failed:
    error = task.result.error  # Access the specific exception
```

#### Resource Management
Automatic startup and cleanup of execution resources:
```python
# Resources managed automatically
async with ParallelManager() as manager:
    await manager.submit(task)
    await manager.process_tasks()
# Resources cleaned up when exiting context
```

### Performance Considerations
- Thread executors provide lower overhead for I/O-bound tasks
- Process executors provide true parallelism for CPU-bound tasks
- Statistics tracking allows optimization of worker count
- Task prioritization ensures critical tasks complete first
- Dependency resolution maximizes parallelism when possible

This document will be updated as the system architecture evolves.

## Error Handling Architecture

The Summit SEO system implements a comprehensive error handling and reporting architecture designed to provide actionable suggestions for resolving errors. This architecture follows these key design principles:

### Core Components

1. **Error Context Capturing**
   - `ErrorContext`: Captures comprehensive contextual information about errors
     - Timestamp, operation name, component name, user action
     - Environment information and input data
     - Custom context values for specialized error scenarios

2. **Error Reporting**
   - `ErrorReporter`: Abstract base class defining the error reporting interface
   - `ConsoleErrorReporter`: Rich console output with color coding by severity
   - `FileErrorReporter`: Persistent error logs in JSON or text format

3. **Actionable Suggestions**
   - `ActionableSuggestion`: Core data structure for remediation steps
     - Severity-based categorization (Critical, High, Medium, Low, Info)
     - Step-by-step instructions for resolution
     - Code examples and documentation links
   - `SuggestionProvider`: Base class for domain-specific suggestion providers

### Design Patterns

#### Decorator Pattern
Used to enhance standard exceptions with suggestions:
```python
enhanced_error = ErrorWithSuggestions(
    message="Enhanced error message",
    original_error=original_exception,
    suggestions=suggestions_list
)
```

#### Factory Method Pattern
Used to create appropriate suggestion providers based on error types:
```python
suggestions = get_suggestion_for_error(error)
```

#### Registry Pattern
Used to register and discover suggestion providers:
```python
@register_suggestion_provider
def custom_provider(error, error_text):
    # Return appropriate suggestions
```

#### Strategy Pattern
Used to implement different error reporting strategies:
```python
# Console-based reporting
reporter = ConsoleErrorReporter(colored_output=True)

# File-based reporting
reporter = FileErrorReporter(output_dir="error_logs", format="json")
```

### Suggestion Provider Hierarchy

1. **Network Suggestion Providers**
   - Connection errors
   - DNS resolution errors
   - SSL/TLS errors
   - Proxy configuration errors
   - Timeout handling

2. **Parsing Suggestion Providers**
   - HTML parsing errors
   - JSON parsing errors
   - XML parsing errors
   - CSS selector errors
   - Encoding errors

3. **Authentication Suggestion Providers**
   - Authentication failures
   - Token expiration
   - Permission issues
   - Login problems

4. **Additional Specialized Providers**
   - Rate limiting errors
   - Configuration errors
   - Resource not found errors
   - Analyzer-specific errors
   - Data extraction errors

### Implementation Patterns

#### Automatic Registration
SuggestionProvider subclasses are automatically registered via metaclass:
```python
class CustomSuggestionProvider(SuggestionProvider):
    @classmethod
    def provide_suggestions(cls, error, error_text):
        # Analyze error and provide suggestions
        return suggestions
```

#### Error Matching
Suggestions can be matched to errors through type or pattern matching:
```python
suggestion = ActionableSuggestion(
    message="Fix this specific error",
    steps=["Step 1", "Step 2"],
    applies_to_exceptions=[ValueError, TypeError],  # Match by type
    error_patterns=["timeout", "connection refused"]  # Match by pattern
)
```

#### Severity Prioritization
Suggestions are automatically sorted by severity for presentation:
```python
# Order: CRITICAL, HIGH, MEDIUM, LOW, INFO
suggestions.sort(key=lambda s: severity_order.get(s.severity, 999))
```

### Error Reporting Flow

1. **Error Detection**: System detects an exception during operation
2. **Context Capture**: ErrorContext collects relevant execution information
3. **Suggestion Generation**: SuggestionProviders analyze the error and generate suggestions
4. **Report Creation**: ReportedError combines error, context, and suggestions
5. **Report Presentation**: ErrorReporter formats and presents the report to the user

This comprehensive error handling architecture significantly improves the user experience by transforming cryptic error messages into actionable remediation steps, enhancing the self-service capability of the Summit SEO system.

## Phase 4 Architecture (Planned)

### Web Application Architecture
The web interface will follow a modern front-end architecture:
- **Framework**: React for component-based UI
- **State Management**: Redux for application state
- **Styling**: Tailwind CSS for utility-first styling
- **Build System**: Vite for fast development and production builds
- **Component Design**: Atomic design methodology (atoms, molecules, organisms, templates, pages)
- **Routing**: React Router for client-side navigation
- **API Integration**: Axios for API communication
- **Authentication**: JWT-based authentication with refresh tokens

### REST API Architecture
The REST API will follow a structured design:
- **Framework**: FastAPI for performance and automatic documentation
- **Authentication**: OAuth2 with JWT tokens
- **Versioning**: URL-based versioning (e.g., /api/v1/)
- **Documentation**: OpenAPI 3.0 specification
- **Serialization**: Pydantic models for validation and serialization
- **Error Handling**: Standard error responses with problem details
- **Rate Limiting**: Token bucket algorithm for request throttling
- **CORS**: Configurable cross-origin resource sharing

### Database Architecture
Database integration will use a layered approach:
- **ORM**: SQLAlchemy for database abstraction
- **Migration**: Alembic for schema versioning
- **Schema Design**: Normalized design with performance considerations
- **Repository Pattern**: Abstraction over ORM for business logic
- **Connection Pooling**: Efficient connection reuse
- **Caching**: Redis for query caching

### Cloud Deployment Architecture
Cloud deployment will follow modern practices:
- **Containerization**: Docker for consistent environments
- **Orchestration**: Kubernetes for container management
- **Infrastructure as Code**: Terraform for infrastructure provisioning
- **CI/CD**: GitHub Actions for automated deployment
- **Monitoring**: Prometheus and Grafana for metrics
- **Logging**: ELK stack for centralized logging
- **Scaling**: Horizontal pod autoscaling based on load

### Multi-User Architecture
Support for multiple users will include:
- **Authentication**: Role-based access control (RBAC)
- **User Management**: User, group, and role management
- **Workspace Isolation**: Multi-tenancy with data separation
- **Audit Trail**: Logging of user actions for accountability
- **Team Collaboration**: Shared projects and reports

### Enterprise Features
Enterprise capabilities will include:
- **Scheduled Analysis**: Cron-like scheduling of analyses
- **Notifications**: Email and webhook notifications
- **Reporting**: Customizable report templates
- **White Labeling**: Custom branding options
- **Integration**: APIs for third-party integration
- **Data Export**: Multiple export formats (PDF, Excel, CSV)
- **Historical Data**: Trend analysis and comparison

## Integration Patterns

### External System Integration
Integration with external systems follows:
- **Webhook Pattern**: For event-driven integration
- **API Gateway Pattern**: For centralized API access
- **Message Queue Pattern**: For asynchronous processing
- **Adapter Pattern**: For legacy system integration

### Plugin Architecture
The plugin system allows for extension:
- **Plugin Registry**: Central registry for discovery
- **Interface-based Design**: Clearly defined extension points
- **Configuration-driven**: Plugin configuration through settings
- **Lifecycle Management**: Controlled plugin loading/unloading

## Data Flow Architecture

### Analysis Pipeline
Data flows through the system in a pipeline:
1. **Collection**: Raw data gathered from sources
2. **Processing**: Data transformed into analyzable format
3. **Analysis**: Multiple analyzers examine processed data
4. **Aggregation**: Results combined across analyzers
5. **Reporting**: Aggregated results presented to user

### Parallel Analysis
Parallel execution follows a directed acyclic graph (DAG):
- Independent analyzers run concurrently
- Dependent analyzers wait for prerequisites
- Results are merged asynchronously
- Progress is tracked across all parallel operations

## Error Handling Architecture

### Error Propagation
Errors are handled through:
- Exception hierarchies for categorization
- Context enrichment for debugging
- Graceful degradation for partial failures
- Comprehensive logging for troubleshooting

### Error Reporting
Error reporting follows a structured approach:
- Severity-based categorization
- Actionable recommendations
- Contextual information
- Root cause identification

## Testing Architecture

### Test Hierarchy
Tests are organized in a hierarchy:
- Unit tests for individual components
- Integration tests for component interactions
- System tests for end-to-end functionality
- Performance tests for resource utilization

### Test Fixtures
Test data is managed through:
- Fixture factories for test data generation
- Mock objects for external dependencies
- Parameterized tests for comprehensive coverage
- Snapshot testing for report output validation

## Database Architecture

### Core Models
1. Base Models:
   - `BaseModel`: Abstract base class with common fields
     - UUID primary key
     - Creation and update timestamps
     - Soft delete support
   - `TenantModel`: Multi-tenant base class
     - Tenant identifier field
     - Tenant-specific relationships

2. User Management:
   - `User`: Core user entity
     - Authentication fields
     - Profile information
     - Role relationships
   - `Role`: Authorization roles
     - Role name and description
     - User relationships
   - `TenantUser`: Tenant-specific user settings
     - Tenant-specific permissions
     - Role in tenant context

3. Project Management:
   - `Project`: Website analysis project
     - Basic project information
     - Configuration settings
     - Analysis relationships
   - `Analysis`: SEO analysis results
     - Analysis status tracking
     - Results storage
     - Finding relationships
   - `Finding`: Individual analysis findings
     - Severity levels
     - Location tracking
     - Recommendation relationships
   - `Recommendation`: Improvement suggestions
     - Priority levels
     - Implementation details
     - Resource references

### Database Design Patterns
1. Multi-tenancy:
   - Tenant isolation through tenant_id field
   - Tenant-specific relationships
   - Tenant user management
   - Tenant-specific settings

2. Soft Delete:
   - is_deleted flag on all models
   - Filtering of deleted records
   - Recovery capability

3. Audit Trail:
   - created_at timestamp
   - updated_at timestamp
   - Version tracking capability

4. Relationships:
   - One-to-many relationships
   - Many-to-many relationships
   - Cascade delete rules
   - Back references

### Migration Strategy
1. Version Control:
   - Alembic for migration management
   - Versioned schema changes
   - Upgrade and downgrade paths

2. Data Seeding:
   - Initial role creation
   - Admin user setup
   - Default configurations

3. Environment Support:
   - Development (SQLite)
   - Production (PostgreSQL)
   - Environment-specific settings

### Security Patterns
1. Authentication:
   - Password hashing with bcrypt
   - JWT token-based authentication
   - Role-based access control

2. Authorization:
   - Role-based permissions
   - Tenant-specific permissions
   - Resource-level access control

3. Data Isolation:
   - Tenant data separation
   - User data protection
   - Secure credential storage

### Performance Patterns
1. Indexing Strategy:
   - Primary key indexes
   - Foreign key indexes
   - Tenant-specific indexes
   - Search optimization indexes

2. Query Optimization:
   - Eager loading relationships
   - Lazy loading where appropriate
   - Query caching support

3. Connection Management:
   - Connection pooling
   - Session management
   - Transaction handling

## API Architecture

### RESTful Design
1. Resource Naming:
   - Plural nouns for collections
   - Singular nouns for individual resources
   - Nested resources for relationships

2. HTTP Methods:
   - GET for retrieval
   - POST for creation
   - PUT/PATCH for updates
   - DELETE for removal

3. Status Codes:
   - 200 for success
   - 201 for creation
   - 400 for bad requests
   - 401 for unauthorized
   - 403 for forbidden
   - 404 for not found
   - 500 for server errors

### Authentication
1. JWT Implementation:
   - Token-based authentication
   - Refresh token support
   - Token expiration handling

2. Authorization:
   - Role-based access control
   - Permission checking
   - Resource ownership validation

### Rate Limiting
1. Implementation:
   - Request counting
   - Time window tracking
   - Rate limit headers

2. Configuration:
   - Per-endpoint limits
   - Per-user limits
   - Per-tenant limits

### Error Handling
1. Standard Format:
   - Error code
   - Error message
   - Error details
   - Stack trace (development only)

2. Validation:
   - Input validation
   - Business rule validation
   - Constraint checking

## Frontend Architecture

### Component Structure
1. Layout Components:
   - Header
   - Navigation
   - Footer
   - Sidebar

2. Feature Components:
   - Dashboard
   - Analysis views
   - Project management
   - User management

3. Common Components:
   - Forms
   - Tables
   - Charts
   - Modals

### State Management
1. Global State:
   - User information
   - Tenant context
   - Application settings

2. Local State:
   - Form data
   - UI state
   - Component data

### Routing
1. Route Structure:
   - Nested routes
   - Protected routes
   - Dynamic routes

2. Navigation:
   - Breadcrumb navigation
   - Menu structure
   - Route guards

## Testing Strategy

### Unit Testing
1. Model Tests:
   - CRUD operations
   - Relationship handling
   - Validation rules

2. Service Tests:
   - Business logic
   - Data processing
   - Error handling

### Integration Testing
1. API Tests:
   - Endpoint functionality
   - Authentication
   - Authorization
   - Error handling

2. Database Tests:
   - Migration testing
   - Data integrity
   - Transaction handling

### Performance Testing
1. Load Testing:
   - Concurrent users
   - Request throughput
   - Response times

2. Stress Testing:
   - System limits
   - Error conditions
   - Recovery testing

## Testing Patterns

### Test Structure
- Each analyzer has a dedicated test file in tests/analyzer/
- Tests use pytest fixtures for setup and teardown
- Mock HTML content is used for testing parsing logic
- Expected results are explicitly defined for validation
- Edge cases are tested separately from normal cases
- Integration with factory is tested in factory tests

### Security Testing
- Each security check has dedicated test cases
- Tests validate both positive (secure) and negative (insecure) scenarios
- Mock HTTP responses are used to simulate headers
- Severity levels are validated in tests
- Remediation recommendations are verified

### Service Testing
- Services with external dependencies use comprehensive mocking
- Supabase client operations are mocked using AsyncMock for async operations
- Database queries use fixture data with standardized patterns
- Complete test isolation eliminates reliance on external systems
- CRUD operations are tested with various scenarios (found/not found, create/update)
- Test coverage is maintained at 95%+ for service layer code
- All tests are async-compatible with proper pytest-asyncio markers
- Mock data patterns follow the same structure as real data

### AsyncMock Implementation Pattern
- AsyncMock is used for all async methods that will be awaited
- Complete isolation from external dependencies
- Each mock is configured to return appropriate data for the test scenario
- Chainable methods (like `from_`, `select`, `eq`, `order`) return self or new mocks
- Terminal methods like `execute()` return AsyncMock objects with predefined results
- Different test scenarios use different return values to test all code paths
- Tests validate that mocks are called with expected parameters

### Database Service Testing
- Mock Supabase client provides consistent responses
- Test fixtures define standard database responses
- Service logic is tested independently of database implementation
- Row Level Security testing uses mock permission checks 
- Transaction handling is verified with mock commits/rollbacks
- Error cases test proper exception handling
- Edge cases like empty results, duplicates, and invalid IDs are covered

# System Patterns

## API Architecture
- FastAPI for high-performance async API
- Error response standardization
- Middleware architecture for cross-cutting concerns
- Service layer pattern for business logic
- Repository pattern for data access

## Error Handling
- Standardized error response format
- Error code enumeration
- Centralized exception handlers
- Middleware-based error processing
- Actionable suggestions for resolution
- Detailed logging with client information

## Testing Patterns
- Primary testing with pytest
- Standalone unittest-based testing for components with settings dependencies
- AsyncTestCase for properly testing async functions
- Mock objects for external dependencies
- Consolidated test runners for manual test execution
- Isolation from application configuration

## Authentication
- JWT token-based authentication
- User role-based permissions
- Token refresh mechanism
- Secure password hashing

## Data Access
- SQLAlchemy ORM for database operations
- Repository pattern for data access abstraction
- Unit of Work pattern for transaction management
- Data Transfer Objects (DTOs) for external interfaces
- Mapper functions for entity transformations

## SEO Analysis
- Analyzer factory pattern
- Base analyzer with specialized implementations
- Analysis result standardization
- Scoring algorithm with weighted components
- Remediation suggestions framework

## Frontend Patterns

### Component Architecture
- All UI components follow shadcn/ui patterns with consistent styling
- Modular component approach with clear separation of concerns
- Custom theming with Tailwind CSS using CSS variables
- Responsive design patterns using custom breakpoint utilities
- Dark/light theme support with OS preference detection
- Reusable layout components:
  - Container: For consistent content width and padding
  - Section: For semantic grouping of content with proper spacing
  - Grid: Flexible grid system with responsive column support
  - Flex: Layout utility for flexbox-based designs
- Specialized layout components:
  - PageLayout: Page-level structure with header, content, footer
  - SidebarLayout: Two-column layout with responsive sidebar
  - DashboardLayout: Comprehensive layout for dashboard pages

### Admin Dashboard Architecture
- Role-based layout with admin permission check
- Restricted access using ProtectedRoute component and useAuth context
- Tabbed interface for organizing different admin functions:
  - System monitoring with real-time metrics
  - User management with CRUD operations
  - System configuration with categorized settings
  - Analytics for system performance (placeholder)
- Consistent data fetching pattern using:
  - Custom API client for admin operations
  - Loading states with skeleton loaders
  - Error handling with toast notifications
  - Refresh capability for all data sections
- Data display patterns:
  - Card-based grouping of related information
  - Table layout for data with consistent styling
  - Form components for data editing with validation
  - Modal dialogs for confirmation and complex editing
- Shared components across tabs:
  - Alert component for error states
  - Loading indicators for asynchronous operations
  - Action buttons with consistent positioning
  - Responsive layout adapting to different screen sizes

### State Management
- React Context for global state
- React Query for server state
- Local state with useState where appropriate
- localStorage for persistent user preferences

### UI/UX Patterns
- Consistent card-based layouts
- Responsive grid and flex layouts
- Dark/light theme support
- Loading states and skeletons
- Error boundaries and fallbacks
- Animation and transition system
- Toast notifications for feedback

### Keyboard Shortcuts System
- Custom `useKeyboardShortcuts` hook for managing shortcuts
- Context provider for global shortcuts access
- Keyboard shortcuts dialog accessible via Shift+?
- Keymap button in navigation for discoverability
- Support for different shortcut categories
- Format utility for displaying key combinations
- Shortcut conflict prevention
- Focus-aware shortcuts (respects input fields)

### Sound Effects System
- Web Audio API for cross-browser compatibility
- Context provider for global sound access
- Multiple sound types for different interactions
- Volume control and mute functionality
- User preference persistence in localStorage
- Subtle audio feedback on key interactions
- Integration with keyboard shortcuts and UI elements

### Product Tour / Onboarding
- Step-by-step guided tour system
- Element targeting and highlighting
- Tooltip positioning with responsive adjustments
- Tour persistence and progress tracking
- Notification prompt for new users
- Manual trigger via tour button
- Animation effects for engagement
- Sound feedback integration

## Data Patterns

### Form Management
- Form validation with shadcn-ui and form libraries
- Consistent error handling and feedback

### API Integration
- Services layer for API calls
- React Query for data fetching and caching
- Optimistic updates for improved UX
- Error handling with retry logic

## Animation Patterns

### Transition Animations
- Page transitions with Framer Motion
- Content reveal animations
- List item animations
- Modal and dialog transitions

### Interaction Feedback
- Button and control state animations
- Hover and focus effects
- Loading and progress animations
- Success/error state animations

### Motion Design System
- Consistent animation timing
- Shared animation variants
- Performance-optimized animations
- Respect for reduced motion preferences

## Mobile Patterns

### Responsive Design
- Mobile-first approach
- Breakpoint system for different devices
- Conditional rendering for mobile/desktop
- Touch-optimized interactions

### Mobile Navigation
- Bottom navigation for mobile
- Collapsible sidebar for tablet/desktop
- Hamburger menu with slide-in navigation

## Architectural Integrations

### Supabase Integration
- Authentication flow with Supabase Auth
- Real-time subscriptions for live updates
- Row Level Security for data access control
- Storage integration for file uploads

### LLM Integration
- LiteLLM service abstraction
- Model routing for different providers
- Cost optimization strategies
- Fallback mechanisms for reliability

## Frontend Architecture Patterns

### A/B Testing System

The A/B testing system enables data-driven UI/UX decisions through controlled experiments. The architecture follows these key patterns:

1. **Context Provider Pattern**
   - `ABTestingProvider`: Central context provider for experiment state
   - Manages experiment data, user assignments, and tracking
   - Provides hooks and utilities for components to access experiment state

2. **Database Schema**
   - `ab_experiments`: Stores experiment definitions with metadata
   - `ab_variants`: Stores variant configurations for each experiment
   - `ab_user_experiments`: Tracks user assignments and conversions

3. **Component Patterns**
   - **Variant Selection**: Conditionally renders components based on assigned variant
   - **Interaction Tracking**: Monitors user interactions with variants
   - **Conversion Tracking**: Records conversion events for analysis

4. **Admin Interface**
   - Experiment management dashboard for creating and monitoring tests
   - Statistical analysis of variant performance
   - Conversion tracking and visualization

5. **Implementation Example**
   ```tsx
   // Using an A/B test component
   <ABTest experimentId="dashboard-layout">
     <ABVariant id="control">Original Design</ABVariant>
     <ABVariant id="variant-a">New Design A</ABVariant>
     <ABVariant id="variant-b">New Design B</ABVariant>
   </ABTest>
   ```

6. **Hook-Based API**
   - `useABTestVariant`: Hook for accessing variant assignment and tracking
   - Provides utilities for interaction and conversion tracking
   - Supports automatic view tracking

7. **Statistical Analysis**
   - Calculates conversion rates and confidence intervals
   - Supports multi-variant testing with weighted distribution
   - Provides actionable insights for UX improvements

8. **Implementation Components**
   - Dashboard Widget A/B Test: Tests different data visualization layouts
   - CTA Button A/B Test: Tests button designs for conversion optimization
   - Admin Dashboard: Manages and monitors experiments