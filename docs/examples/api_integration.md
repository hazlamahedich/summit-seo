# API Integration with Third-Party Tools

This guide explains how to integrate Summit SEO with third-party tools and services via their APIs, enabling you to combine SEO analysis with other data sources for comprehensive reporting and automated workflows.

## Overview

Integrating Summit SEO with other tools allows you to:

1. **Combine SEO analysis with real-world performance data** from tools like Google Search Console and Google Analytics
2. **Correlate SEO scores with actual search rankings and traffic**
3. **Augment SEO analysis with backlink and keyword data** from specialized SEO tools
4. **Create comprehensive marketing dashboards** that include SEO health alongside other metrics
5. **Automate reporting workflows** across multiple platforms

## API Integration Example

Summit SEO includes examples for integrating with popular SEO and analytics platforms in `examples/api_integration_example.py`, which demonstrates how to:

- Combine Summit SEO analysis with Google Search Console data
- Integrate with Google Analytics for user behavior insights
- Use data from Ahrefs API for backlink and keyword analysis
- Create custom API wrappers for other SEO tools
- Generate combined reports and export data

## Google Search Console Integration

Google Search Console provides valuable data about how your site performs in Google search results. Combining this data with Summit SEO analysis helps correlate SEO best practices with actual search performance.

### Example Implementation

```python
from summit_seo import SummitSEO
from summit_seo.analyzer import SecurityAnalyzer, PerformanceAnalyzer

class GoogleSearchConsoleIntegration:
    def __init__(self, site_url, credentials_file=None):
        self.site_url = site_url
        self.credentials_file = credentials_file
        self.summit = SummitSEO()
        
        # Initialize Google API client (requires googleapiclient package)
        # from google.oauth2 import service_account
        # from googleapiclient.discovery import build
        # credentials = service_account.Credentials.from_service_account_file(
        #     credentials_file, scopes=['https://www.googleapis.com/auth/webmasters']
        # )
        # self.service = build('searchconsole', 'v1', credentials=credentials)
    
    def get_search_performance(self, days=30, dimensions=None):
        # Get performance data from Google Search Console
        # This would normally make an API call to Google
        # ...
        
    def combine_with_seo_analysis(self, pages_to_analyze=None):
        # Get search performance data
        performance_data = self.get_search_performance(days=30)
        
        # Determine which pages to analyze (top pages by clicks)
        # ...
        
        # Run SEO analysis on each page
        analysis_results = {}
        for page_url in pages_to_analyze:
            analyzers = [SecurityAnalyzer(), PerformanceAnalyzer()]
            page_results = self.summit.analyze_url(page_url, analyzers=analyzers)
            analysis_results[page_url] = page_results
        
        # Combine the data
        return {
            "search_performance": performance_data,
            "seo_analysis": analysis_results,
            "combined_metrics": self._create_combined_metrics(performance_data, analysis_results)
        }
```

### Usage Example

```python
# Initialize the integration with your site URL
gsc_integration = GoogleSearchConsoleIntegration(
    "https://example.com",
    credentials_file="path/to/credentials.json"
)

# Get combined data
combined_data = gsc_integration.combine_with_seo_analysis()

# Generate a report
report_path = gsc_integration.generate_report("gsc_seo_report.html")
```

## Google Analytics Integration

Google Analytics provides insights into user behavior on your website. Combining this with SEO analysis helps understand how SEO quality affects user engagement metrics.

### Example Implementation

```python
class GoogleAnalyticsIntegration:
    def __init__(self, property_id, credentials_file=None):
        self.property_id = property_id
        self.credentials_file = credentials_file
        self.summit = SummitSEO()
        
        # Initialize GA client (requires google-analytics-data package)
        # ...
    
    def get_page_metrics(self, days=30, base_url="https://example.com"):
        # Get metrics from Google Analytics
        # ...
        
    def combine_with_seo_analysis(self, pages_to_analyze=None):
        # Get page metrics
        page_metrics = self.get_page_metrics()
        
        # Run SEO analysis on each page
        analysis_results = {}
        for page_url in pages_to_analyze:
            analyzers = [SecurityAnalyzer(), PerformanceAnalyzer()]
            page_results = self.summit.analyze_url(page_url, analyzers=analyzers)
            analysis_results[page_url] = page_results
        
        # Combine the data
        return {
            "analytics_metrics": page_metrics,
            "seo_analysis": analysis_results,
            "combined_metrics": self._create_combined_metrics(page_metrics, analysis_results)
        }
```

### CSV Export Example

```python
ga_integration = GoogleAnalyticsIntegration("GA4-12345678")

# Export combined data to CSV
csv_path = ga_integration.export_combined_data_csv("ga_seo_data.csv")
```

## Ahrefs API Integration

Ahrefs is a popular SEO tool that provides backlink and keyword data. Combining this with Summit SEO analysis helps understand how technical SEO relates to backlink profile and keyword rankings.

### Example Implementation

```python
class AhrefsApiWrapper:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://apiv2.ahrefs.com"
        self.summit = SummitSEO()
    
    def get_backlinks(self, target):
        # Make API request to Ahrefs to get backlink data
        # ...
        
    def get_organic_keywords(self, target):
        # Make API request to Ahrefs to get organic keyword data
        # ...
        
    def combine_with_seo_analysis(self, target):
        # Get backlink and keyword data
        backlinks_data = self.get_backlinks(target)
        keywords_data = self.get_organic_keywords(target)
        
        # Run SEO analysis
        analyzers = [SecurityAnalyzer(), PerformanceAnalyzer()]
        seo_results = self.summit.analyze_url(target, analyzers=analyzers)
        
        # Combine the data
        return {
            "target_url": target,
            "avg_seo_score": calculate_avg_score(seo_results),
            "backlinks_count": calculate_backlinks_count(backlinks_data),
            "referring_domains_count": calculate_domains_count(backlinks_data),
            "organic_keywords_count": keywords_data["organic"]["count"],
            "top_keywords": keywords_data["organic"]["items"],
            "estimated_organic_traffic": calculate_traffic(keywords_data),
            "seo_analysis": seo_results,
            "backlinks_data": backlinks_data,
            "keywords_data": keywords_data
        }
```

## Creating Custom API Wrappers

You can create custom wrappers for other SEO tools and services by following these guidelines:

1. **Initialize Summit SEO** within your wrapper class
2. **Create methods to fetch data** from the third-party API
3. **Implement a method to run SEO analysis** on relevant URLs
4. **Combine the data** into a unified format
5. **Create export or reporting methods** for the combined data

A basic template for a custom API wrapper:

```python
class CustomSEOToolIntegration:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.summit = SummitSEO()
    
    def fetch_custom_data(self, target_url):
        # Make API requests to the custom SEO tool
        # Process and return the data
        
    def run_seo_analysis(self, target_url):
        # Configure and run Summit SEO analysis
        analyzers = [SecurityAnalyzer(), PerformanceAnalyzer()]
        return self.summit.analyze_url(target_url, analyzers=analyzers)
    
    def combine_data(self, target_url):
        # Fetch data from custom tool
        custom_data = self.fetch_custom_data(target_url)
        
        # Run SEO analysis
        seo_results = self.run_seo_analysis(target_url)
        
        # Combine and return the data
        return {
            "custom_data": custom_data,
            "seo_results": seo_results,
            "combined_metrics": self._calculate_combined_metrics(custom_data, seo_results)
        }
```

## Best Practices for API Integration

1. **Handle API rate limits** carefully to avoid being throttled or blocked
2. **Cache API responses** when appropriate to reduce the number of requests
3. **Implement proper error handling** for API failures and timeouts
4. **Use asynchronous requests** when fetching data from multiple sources
5. **Normalize data formats** to ensure consistency across different APIs
6. **Respect API terms of service** and usage limitations
7. **Keep API credentials secure** and never hardcode them in your application
8. **Add documentation** to explain what each integration does and how to use it

## Authentication Best Practices

Most APIs require authentication. Here are best practices for handling API credentials:

1. **Use environment variables** to store API keys and tokens
2. **Support credential files** for service account-based authentication
3. **Implement OAuth flows** where appropriate
4. **Create a credentials manager** for applications that use multiple APIs

Example of using environment variables for credentials:

```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
google_api_key = os.getenv("GOOGLE_API_KEY")
ahrefs_api_token = os.getenv("AHREFS_API_TOKEN")

# Initialize integrations
gsc_integration = GoogleSearchConsoleIntegration("https://example.com")
ahrefs_wrapper = AhrefsApiWrapper(ahrefs_api_token)
```

## Common Integration Patterns

### 1. Find SEO Issues on Top Landing Pages

Analyze pages that get the most traffic from Google:

```python
# Get top landing pages from Google Analytics
ga_integration = GoogleAnalyticsIntegration("GA4-12345678")
top_pages = ga_integration.get_top_landing_pages(limit=10)

# Run SEO analysis on these pages
summit = SummitSEO()
seo_issues = {}

for page in top_pages:
    results = summit.analyze_url(page["url"])
    seo_issues[page["url"]] = extract_issues(results)
```

### 2. Correlate SEO Fixes with Ranking Improvements

Track how SEO improvements affect rankings:

```python
# Store initial SEO scores and rankings
initial_scores = get_seo_scores(pages)
initial_rankings = get_rankings_from_gsc(pages)

# Implement SEO fixes
implement_seo_fixes(pages)

# Wait for changes to take effect (e.g., 2 weeks)
time.sleep(14 * 24 * 60 * 60)

# Get new scores and rankings
new_scores = get_seo_scores(pages)
new_rankings = get_rankings_from_gsc(pages)

# Calculate improvements
improvements = calculate_improvements(initial_scores, new_scores, initial_rankings, new_rankings)
```

### 3. Prioritize SEO Fixes by Traffic Impact

Focus on issues that affect high-traffic pages:

```python
# Get traffic data from Google Analytics
traffic_data = ga_integration.get_page_traffic()

# Run SEO analysis on all pages
seo_results = run_seo_analysis_on_all_pages()

# Calculate potential impact of fixing issues
prioritized_issues = []
for page, issues in seo_results.items():
    traffic = traffic_data.get(page, 0)
    for issue in issues:
        impact_score = calculate_impact(issue, traffic)
        prioritized_issues.append({
            "page": page,
            "issue": issue,
            "traffic": traffic,
            "impact_score": impact_score
        })

# Sort issues by impact score
prioritized_issues.sort(key=lambda x: x["impact_score"], reverse=True)
``` 