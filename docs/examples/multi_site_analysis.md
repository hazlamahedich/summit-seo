# Multi-Site SEO Analysis

## Overview

The Summit SEO tool provides powerful multi-site analysis capabilities that allow you to:

- Analyze multiple websites in batch mode
- Compare SEO performance across different sites
- Identify patterns and trends across a portfolio of websites
- Generate comparative reports highlighting strengths and weaknesses
- Process sites efficiently using parallel execution

This is particularly useful for agencies managing multiple client websites, enterprises with multiple domains, or comparing your site against competitors.

## Multi-Site Analysis Example

The `examples/multi_site_analysis.py` example demonstrates how to:

1. Analyze multiple websites sequentially or in parallel
2. Generate individual reports for each site
3. Create comparative reports showing how sites rank against each other
4. Export aggregated data for further processing

## Basic Usage

The simplest way to run a multi-site analysis is:

```bash
python examples/multi_site_analysis.py --sites https://site1.com https://site2.com https://site3.com
```

This will:
1. Analyze all three sites using the default analyzers (security, performance, accessibility)
2. Generate individual HTML and JSON reports for each site
3. Create a comparative report showing how the sites compare
4. Export all results to a JSON file

## Implementation Example

```python
from summit_seo import SummitSEO
from summit_seo.analyzer import SecurityAnalyzer, PerformanceAnalyzer, AccessibilityAnalyzer
from examples.multi_site_analysis import MultiSiteAnalyzer

# List of sites to analyze
sites = [
    "https://example.com",
    "https://example.org",
    "https://example.net"
]

# Create the multi-site analyzer
analyzer = MultiSiteAnalyzer(
    sites=sites,
    output_dir="reports/my_comparison",
    analyzers=["security", "performance", "accessibility"],
    parallel=True,
    verbose=True
)

# Run the analysis
analyzer.run_analysis()

# Generate comparative report
report_file = analyzer.generate_comparative_report()

# Export results to JSON
json_file = analyzer.export_results_json()

print(f"Comparative report: {report_file}")
print(f"JSON results: {json_file}")
```

## Parallel Processing

By default, the multi-site analyzer uses parallel processing to analyze multiple sites simultaneously, which can significantly improve performance when analyzing many sites. You can control parallelism with:

```python
# Disable parallel processing
analyzer = MultiSiteAnalyzer(sites=sites, parallel=False)

# Control the number of worker processes
analyzer = MultiSiteAnalyzer(sites=sites, max_workers=4)
```

## Comparative Reporting

The multi-site analyzer generates comparative reports in both HTML and CSV formats:

### HTML Report

The HTML report provides a visual comparison of all sites, including:
- Overall scores and rankings
- Individual analyzer scores and rankings
- Color-coded performance indicators
- Summary statistics

### CSV Report

The CSV report contains the same data in a tabular format suitable for importing into spreadsheets or data analysis tools.

## Command Line Options

The example script provides several command line options:

```
--sites               List of sites to analyze
--output-dir          Output directory for reports
--analyzers           Analyzers to run (security, performance, accessibility, etc.)
--no-parallel         Disable parallel processing
--max-workers         Maximum number of worker processes
--verbose             Enable verbose output
```

Example:

```bash
python examples/multi_site_analysis.py \
    --sites https://site1.com https://site2.com \
    --output-dir reports/competitor_analysis \
    --analyzers security performance \
    --max-workers 2 \
    --verbose
```

## Extending the Multi-Site Analyzer

You can extend the `MultiSiteAnalyzer` class to add custom functionality:

```python
class EnhancedAnalyzer(MultiSiteAnalyzer):
    def export_to_spreadsheet(self):
        # Custom code to export to Excel or Google Sheets
        pass
        
    def send_report_email(self, recipients):
        # Custom code to email the comparative report
        pass
```

## Best Practices

When performing multi-site analysis:

1. **Select representative pages** - Choose similar pages across sites for fair comparison
2. **Use consistent analyzers** - Ensure you use the same set of analyzers for all sites
3. **Consider timing** - Run analyses at similar times to avoid temporal biases
4. **Group similar sites** - Compare sites with similar purposes for meaningful insights
5. **Look for patterns** - Identify common issues across multiple sites
6. **Focus on significant differences** - Pay attention to areas with large performance gaps
7. **Analyze competitors regularly** - Track changes in competitor sites over time

## Use Cases

### Competitive Analysis

Compare your site against competitors to:
- Identify areas where competitors outperform you
- Discover common industry weaknesses you can exploit
- Track how your site improves relative to competitors over time

### Portfolio Management

For agencies or enterprises managing multiple sites:
- Identify systemic issues across your portfolio
- Prioritize improvements based on comparative performance
- Track progress across sites over time
- Generate client-ready reports showing relative performance

### Pre/Post Analysis

Compare before and after states when making significant changes:
- Test different implementations against each other
- Verify improvements after major redesigns
- Compare staging and production environments 