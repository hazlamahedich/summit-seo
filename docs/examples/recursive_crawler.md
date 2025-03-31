# Recursive Website Crawler

## Overview

The Summit SEO tool includes a powerful recursive crawler that allows you to:

- Analyze multiple pages on a website automatically
- Discover and follow links within a domain
- Limit crawling by depth and maximum number of pages
- Aggregate SEO issues across an entire site
- Identify the most common issues affecting a website
- Generate site-wide reports and statistics

This is particularly useful for comprehensive site audits, identifying systemic issues, and understanding the overall SEO health of a website.

## Recursive Crawler Example

The `examples/recursive_crawler.py` example demonstrates how to:

1. Start from a single URL and recursively discover linked pages
2. Analyze each page for security and performance issues
3. Keep track of visited pages to avoid duplicates
4. Stay within the same domain during crawling
5. Respect crawl depth and page limits
6. Generate a site-wide summary report

## Basic Usage

To run a recursive crawl, use the following command:

```bash
python examples/recursive_crawler.py --url https://example.com --max-pages 20 --max-depth 3 --verbose
```

This will:
1. Start crawling from example.com
2. Follow links up to 3 levels deep
3. Analyze up to 20 pages
4. Print verbose output during the crawl
5. Generate a site summary report in JSON format

## Implementation Example

```python
from summit_seo import SummitSEO
from examples.recursive_crawler import RecursiveCrawler

# Create the crawler
crawler = RecursiveCrawler(
    start_url="https://example.com",
    output_dir="reports/my_site_audit",
    max_pages=50,
    max_depth=3,
    verbose=True
)

# Start crawling
crawler.crawl()

# Generate site report
report_file = crawler.generate_site_report()

print(f"Site report generated: {report_file}")
```

## How It Works

The recursive crawler works as follows:

1. Begins with a starting URL (seed)
2. Analyzes the page using Summit SEO analyzers
3. Extracts all links from the page
4. Filters links to stay within the same domain
5. Adds new links to a crawl queue
6. Processes the queue while respecting depth and page limits
7. Aggregates results and issues across all pages
8. Generates a comprehensive site report

## Controlling the Crawl

You can control the crawler's behavior with these parameters:

- `start_url`: The URL to begin crawling from
- `max_pages`: Maximum number of pages to analyze (default: 10)
- `max_depth`: Maximum link depth to follow (default: 3)
- `output_dir`: Directory to store reports (default: "reports/recursive_crawl")
- `verbose`: Whether to print progress information

## Site Report

The site report includes:

- Basic information about the crawl (start URL, domain, pages analyzed)
- List of all URLs analyzed
- Common issues across the site, grouped by analyzer
- Issue frequency (how many pages each issue affects)

The report is saved in JSON format for easy processing and integration with other tools.

## Advanced Implementation

You can extend the `RecursiveCrawler` class to add custom functionality:

```python
class CustomCrawler(RecursiveCrawler):
    def should_analyze_url(self, url):
        # Custom logic to determine if a URL should be analyzed
        # For example, skip login pages or certain file types
        if "login" in url or url.endswith(".pdf"):
            return False
        return True
        
    def generate_html_report(self):
        # Custom HTML report generator
        # Use self.results and self.all_issues to create a report
        pass
```

## Best Practices

When using the recursive crawler:

1. **Start with small limits** - Begin with low page and depth limits before doing a full crawl
2. **Be considerate** - Use reasonable crawl rates to avoid overwhelming the server
3. **Focus on specific sections** - Target specific sections of a site rather than the entire domain
4. **Check robot exclusions** - Honor robots.txt and meta robots directives
5. **Review and filter** - Be prepared to filter out non-relevant pages from the results
6. **Monitor performance** - Larger sites may require optimizing resource usage
7. **Consider legal implications** - Ensure you have permission to crawl the site

## Use Cases

### Complete Site Audit

Use the recursive crawler to analyze an entire website:
- Identify systemic issues affecting multiple pages
- Discover hidden pages with serious SEO problems
- Prioritize fixes based on issue frequency

### Section Analysis

Focus on a specific section of a website:
- Start from a category page
- Keep the depth shallow to stay within that section
- Compare different sections of a website

### Finding Orphaned Pages

Discover pages that aren't well-linked within your site:
- Analyze your sitemap
- Compare with pages discovered through crawling
- Identify important pages that need better internal linking

### Regular Monitoring

Schedule regular crawls to monitor site health:
- Compare results over time
- Detect new issues as they arise
- Verify that fixes have been properly implemented 