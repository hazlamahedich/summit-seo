# Summit SEO - Basic Usage Examples

This guide provides basic examples of how to use Summit SEO for common SEO analysis tasks.

## Installation

Install Summit SEO using pip:

```bash
pip install summit-seo
```

## Simple Analysis Example

The simplest way to analyze a website is to use the built-in analyzers:

```python
import asyncio
from summit_seo import AnalyzerFactory

async def analyze_webpage():
    # Create an analyzer factory
    factory = AnalyzerFactory()
    
    # Create a title analyzer
    title_analyzer = factory.create('title')
    
    # Prepare input data
    data = {
        'html': '<html><head><title>My Sample Page Title</title></head><body>Content here</body></html>',
        'url': 'https://example.com'
    }
    
    # Run the analysis
    result = await title_analyzer.analyze(data)
    
    # Print results
    print(f"Score: {result.score}")
    print(f"Issues: {result.issues}")
    print(f"Recommendations: {result.recommendations}")
    
    return result

# Run the analysis
asyncio.run(analyze_webpage())
```

## Analyzing Multiple Aspects

You can use multiple analyzers to get a comprehensive analysis:

```python
import asyncio
from summit_seo import AnalyzerFactory

async def comprehensive_analysis():
    # Create an analyzer factory
    factory = AnalyzerFactory()
    
    # Create analyzers for different aspects
    analyzers = {
        'title': factory.create('title'),
        'meta': factory.create('meta'),
        'heading': factory.create('heading'),
        'content': factory.create('content'),
        'link': factory.create('link'),
        'image': factory.create('image')
    }
    
    # Prepare input data
    data = {
        'html': open('my_webpage.html', 'r').read(),
        'url': 'https://example.com/my-page'
    }
    
    # Run all analyzers
    results = {}
    for name, analyzer in analyzers.items():
        print(f"Running {name} analysis...")
        results[name] = await analyzer.analyze(data)
    
    # Calculate overall score
    overall_score = sum(r.score for r in results.values()) / len(results)
    print(f"Overall score: {overall_score:.2f}/100")
    
    # Print key issues from each analyzer
    for name, result in results.items():
        print(f"\n=== {name.upper()} ANALYSIS ===")
        print(f"Score: {result.score:.2f}/100")
        if result.issues:
            print("Issues:")
            for issue in result.issues[:3]:  # Show top 3 issues
                print(f"- {issue}")
        
        if result.enhanced_recommendations:
            print("Key Recommendations:")
            for rec in result.get_priority_recommendations()[:3]:  # Show top 3 recommendations
                print(f"- [{rec.severity.name}] {rec.message}")
    
    return results

# Run the analysis
asyncio.run(comprehensive_analysis())
```

## Security Analysis Example

Analyze the security aspects of a website:

```python
import asyncio
from summit_seo import AnalyzerFactory

async def security_analysis():
    # Create a security analyzer
    factory = AnalyzerFactory()
    security_analyzer = factory.create('security')
    
    # Prepare input data with HTTP headers
    data = {
        'html': open('my_webpage.html', 'r').read(),
        'url': 'https://example.com',
        'headers': {
            'Content-Security-Policy': "default-src 'self'",
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY'
        }
    }
    
    # Run the analysis
    result = await security_analyzer.analyze(data)
    
    # Print security score
    print(f"Security Score: {result.score:.2f}/100")
    
    # Print findings by severity
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        findings = [r for r in result.enhanced_recommendations 
                   if r.severity.name == severity]
        
        if findings:
            print(f"\n{severity} FINDINGS ({len(findings)}):")
            for i, finding in enumerate(findings, 1):
                print(f"{i}. {finding.message}")
                print(f"   Remediation: {finding.implementation_guide}")
    
    return result

# Run the security analysis
asyncio.run(security_analysis())
```

## Performance Analysis Example

Analyze the performance of a website:

```python
import asyncio
from summit_seo import AnalyzerFactory

async def performance_analysis():
    # Create a performance analyzer
    factory = AnalyzerFactory()
    perf_analyzer = factory.create('performance')
    
    # Prepare input data with resource information
    data = {
        'html': open('my_webpage.html', 'r').read(),
        'url': 'https://example.com',
        'resources': [
            {'url': 'https://example.com/styles.css', 'size': 45000, 'type': 'stylesheet'},
            {'url': 'https://example.com/script.js', 'size': 120000, 'type': 'script'},
            {'url': 'https://example.com/image.jpg', 'size': 350000, 'type': 'image'},
            {'url': 'https://example.com/font.woff2', 'size': 80000, 'type': 'font'}
        ],
        'load_time': 2.5,  # seconds
        'time_to_interactive': 3.2  # seconds
    }
    
    # Run the analysis
    result = await perf_analyzer.analyze(data)
    
    # Print performance score
    print(f"Performance Score: {result.score:.2f}/100")
    
    # Print detailed results
    perf_data = result.data
    print(f"\nPage Load Time: {perf_data.get('load_time', 'N/A')}s")
    print(f"Time to Interactive: {perf_data.get('time_to_interactive', 'N/A')}s")
    print(f"Total Resources: {perf_data.get('resource_count', 0)}")
    print(f"Total Page Size: {perf_data.get('total_size', 0)/1024:.1f} KB")
    
    # Print quick wins - easy performance improvements
    quick_wins = result.get_quick_wins()
    if quick_wins:
        print("\nQuick Performance Wins:")
        for i, win in enumerate(quick_wins, 1):
            print(f"{i}. {win.message}")
            if win.implementation_guide:
                print(f"   How to implement: {win.implementation_guide}")
    
    return result

# Run the performance analysis
asyncio.run(performance_analysis())
```

## Using Custom Configuration

Customize analyzer behavior by providing configuration options:

```python
import asyncio
from summit_seo import AnalyzerFactory

async def custom_analysis():
    # Create an analyzer factory
    factory = AnalyzerFactory()
    
    # Create a title analyzer with custom configuration
    title_config = {
        'min_title_length': 30,  # Require longer titles
        'max_title_length': 60,  # Standard maximum
        'title_must_contain': ['Product', 'Buy'],  # Required keywords
        'enable_caching': False  # Disable caching
    }
    
    title_analyzer = factory.create('title', title_config)
    
    # Prepare input data
    data = {
        'html': '<html><head><title>Buy Premium Product - Best Deals</title></head><body>Content</body></html>',
        'url': 'https://example.com/product'
    }
    
    # Run the analysis
    result = await title_analyzer.analyze(data)
    
    # Print results
    print(f"Title Score: {result.score:.2f}/100")
    print(f"Title: {result.data.get('title', 'N/A')}")
    print(f"Length: {result.data.get('length', 0)} characters")
    print(f"Contains keywords: {result.data.get('contains_required_keywords', False)}")
    
    if result.issues:
        print("\nIssues:")
        for issue in result.issues:
            print(f"- {issue}")
    
    if result.recommendations:
        print("\nRecommendations:")
        for rec in result.recommendations:
            print(f"- {rec}")
    
    return result

# Run the analysis
asyncio.run(custom_analysis())
```

## Batch Processing Multiple URLs

Process multiple URLs in a batch:

```python
import asyncio
from summit_seo import AnalyzerFactory
import aiohttp
from bs4 import BeautifulSoup

async def fetch_url(session, url):
    async with session.get(url) as response:
        return {
            'url': url,
            'html': await response.text(),
            'status': response.status
        }

async def batch_analysis():
    # List of URLs to analyze
    urls = [
        'https://example.com',
        'https://example.com/about',
        'https://example.com/products',
        'https://example.com/contact'
    ]
    
    # Create analyzers
    factory = AnalyzerFactory()
    analyzers = {
        'title': factory.create('title'),
        'meta': factory.create('meta'),
        'content': factory.create('content')
    }
    
    # Fetch all URLs
    async with aiohttp.ClientSession() as session:
        fetch_tasks = [fetch_url(session, url) for url in urls]
        pages = await asyncio.gather(*fetch_tasks)
    
    # Analyze each page
    results = {}
    for page in pages:
        if page['status'] != 200:
            print(f"Skipping {page['url']} - status code: {page['status']}")
            continue
            
        url_results = {}
        for name, analyzer in analyzers.items():
            url_results[name] = await analyzer.analyze({
                'html': page['html'],
                'url': page['url']
            })
        
        # Store results for this URL
        results[page['url']] = {
            'individual': url_results,
            'average_score': sum(r.score for r in url_results.values()) / len(url_results)
        }
    
    # Print summary
    print("ANALYSIS SUMMARY")
    print("=" * 50)
    for url, url_result in results.items():
        print(f"\n{url}")
        print(f"Average Score: {url_result['average_score']:.2f}/100")
        
        # Get top issues across all analyzers
        all_issues = []
        for analyzer_name, analysis in url_result['individual'].items():
            for issue in analysis.issues:
                all_issues.append(f"[{analyzer_name.upper()}] {issue}")
        
        if all_issues:
            print("Top Issues:")
            for issue in all_issues[:3]:  # Show top 3 issues
                print(f"- {issue}")
    
    return results

# Run batch analysis
asyncio.run(batch_analysis())
```

## Next Steps

For more advanced usage, refer to:

- [Advanced Configuration](advanced_configuration.md)
- [Custom Analyzer Creation](custom_analyzer.md)
- [Reporting Options](reporting_options.md)
- [Performance Optimization](performance_tuning.md) 