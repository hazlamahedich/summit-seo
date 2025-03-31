# Common Use Cases Tutorial

This tutorial provides step-by-step instructions for common Summit SEO use cases, helping you get started quickly with the most frequent scenarios.

## Table of Contents

1. [Basic Website Analysis](#basic-website-analysis)
2. [Batch Analysis of Multiple Pages](#batch-analysis-of-multiple-pages)
3. [Focused Security Audit](#focused-security-audit)
4. [Performance Optimization](#performance-optimization)
5. [Schema.org Validation](#schemaorg-validation)
6. [Accessibility Compliance Check](#accessibility-compliance-check)
7. [Mobile-Friendly Analysis](#mobile-friendly-analysis)
8. [Continuous Monitoring Setup](#continuous-monitoring-setup)
9. [Integration with CI/CD Pipeline](#integration-with-cicd-pipeline)
10. [Custom Report Generation](#custom-report-generation)

## Basic Website Analysis

This use case covers a basic analysis of a single website, which is the most common starting point.

### Steps:

1. **Install Summit SEO:**

```bash
pip install summit-seo
```

2. **Create a simple analysis script:**

```python
from summit_seo import SummitSEO

# Initialize the analyzer
seo = SummitSEO()

# Analyze a website
result = seo.analyze("https://example.com")

# Generate a report
seo.report(result, format="html", output_path="report.html")
```

3. **Run the script:**

```bash
python analyze_website.py
```

4. **Review the results:**
   - Open `report.html` in your browser
   - Review the overall score and recommendations
   - Prioritize issues based on severity

### Example Output:

```
Overall Score: 78/100

Issues Found:
- Missing meta description (Severity: Medium)
- Images without alt text (Severity: Medium)
- Non-HTTPS content (Severity: High)

Top Recommendations:
1. Add a descriptive meta description
2. Ensure all images have meaningful alt text
3. Secure all content with HTTPS
```

## Batch Analysis of Multiple Pages

This use case covers analyzing multiple pages of a website in parallel.

### Steps:

1. **Create a file with URLs to analyze:**

Create `urls.txt` with the following content:
```
https://example.com
https://example.com/about
https://example.com/products
https://example.com/contact
```

2. **Create a batch analysis script:**

```python
from summit_seo import SummitSEO
import asyncio

async def analyze_batch():
    # Initialize with parallel processing
    seo = SummitSEO(config={"system": {"parallel_processing": True, "max_workers": 4}})
    
    # Load URLs from file
    with open("urls.txt") as f:
        urls = [line.strip() for line in f.readlines()]
    
    # Analyze all URLs in parallel
    results = await seo.analyze_batch(urls)
    
    # Generate consolidated report
    seo.report_batch(results, format="html", output_path="batch_report.html")
    
    # Generate individual reports
    for url, result in results.items():
        filename = url.replace("https://", "").replace("/", "_") + ".html"
        seo.report(result, format="html", output_path=f"reports/{filename}")

# Run the batch analysis
asyncio.run(analyze_batch())
```

3. **Run the script:**

```bash
python analyze_batch.py
```

4. **Review the results:**
   - Open `batch_report.html` for a consolidated view
   - Check individual reports in the `reports` directory

## Focused Security Audit

This use case focuses specifically on security analysis.

### Steps:

1. **Create a security audit script:**

```python
from summit_seo import SummitSEO
from summit_seo.analyzers import AnalyzerFactory

# Initialize with only security analyzer
config = {
    "analyzer": {
        "security": {
            "check_https": True,
            "check_mixed_content": True,
            "check_cookies": True,
            "check_csp": True,
            "check_xss": True,
            "check_dependencies": True,
            "check_sensitive_data": True
        }
    }
}

seo = SummitSEO(config=config)

# Create security analyzer directly for more detailed configuration
security_analyzer = AnalyzerFactory.create("security", config=config["analyzer"]["security"])

# Analyze website
result = seo.analyze("https://example.com", analyzers=["security"])

# Generate security report
seo.report(result, format="html", output_path="security_report.html")

# Print critical security issues
security_findings = result.analyzer_results["security"]["findings"]
critical_issues = [f for f in security_findings if f["severity"] == "critical"]

print(f"Found {len(critical_issues)} critical security issues:")
for issue in critical_issues:
    print(f"- {issue['message']}")
    print(f"  Remediation: {issue['remediation']}")
    print()
```

2. **Run the script:**

```bash
python security_audit.py
```

3. **Review the security findings:**
   - Address critical issues immediately
   - Plan remediation for high and medium severity issues

## Performance Optimization

This use case focuses on analyzing and improving website performance.

### Steps:

1. **Create a performance analysis script:**

```python
from summit_seo import SummitSEO
from summit_seo.visualization import VisualizationFactory

# Initialize with performance focus
config = {
    "analyzer": {
        "performance": {
            "analyze_load_time": True,
            "analyze_resources": True,
            "analyze_render_blocking": True,
            "analyze_compression": True,
            "analyze_caching": True,
            "analyze_images": True
        }
    }
}

seo = SummitSEO(config=config)

# Analyze performance
result = seo.analyze("https://example.com", analyzers=["performance"])

# Generate performance report
seo.report(result, format="html", output_path="performance_report.html")

# Create performance visualization
visualizer = VisualizationFactory.create("performance_waterfall")
chart = visualizer.generate(result.analyzer_results["performance"])
chart.save("performance_waterfall.png")

# Print performance suggestions
performance_findings = result.analyzer_results["performance"]["findings"]
print("Top performance optimizations:")
for i, finding in enumerate(performance_findings[:5], 1):
    print(f"{i}. {finding['message']}")
    print(f"   Impact: {finding.get('impact', 'Medium')}")
    print(f"   Remediation: {finding['remediation']}")
    print()
```

2. **Run the script:**

```bash
python performance_analysis.py
```

3. **Implement the suggested optimizations:**
   - Focus on high-impact optimizations first
   - Retest after implementing changes to measure improvement

## Schema.org Validation

This use case validates and improves schema.org markup.

### Steps:

1. **Create a schema validation script:**

```python
from summit_seo import SummitSEO
from summit_seo.analyzers import AnalyzerFactory
import json

# Initialize with schema focus
config = {
    "analyzer": {
        "schema": {
            "validate_json_ld": True,
            "validate_microdata": True,
            "validate_rdfa": True,
            "check_required_properties": True,
            "suggest_recommended_properties": True
        }
    }
}

seo = SummitSEO(config=config)

# Analyze schema
result = seo.analyze("https://example.com", analyzers=["schema"])

# Generate schema report
seo.report(result, format="html", output_path="schema_report.html")

# Extract and save found schemas
schemas = result.analyzer_results["schema"]["details"]["found_schemas"]
with open("found_schemas.json", "w") as f:
    json.dump(schemas, f, indent=2)

# Print schema improvement suggestions
schema_findings = result.analyzer_results["schema"]["findings"]
print("Schema.org Improvement Suggestions:")
for finding in schema_findings:
    print(f"- {finding['message']}")
    print(f"  Remediation: {finding['remediation']}")
    print()

# Print missing recommended properties
recommended = result.analyzer_results["schema"]["details"].get("recommended_properties", {})
for schema_type, props in recommended.items():
    print(f"Recommended properties for {schema_type}:")
    for prop in props:
        print(f"- {prop}")
    print()
```

2. **Run the script:**

```bash
python schema_validation.py
```

3. **Improve schema markup:**
   - Add missing required properties
   - Add recommended properties for better rich snippets
   - Fix any validation errors

## Accessibility Compliance Check

This use case checks for accessibility compliance with WCAG guidelines.

### Steps:

1. **Create an accessibility analysis script:**

```python
from summit_seo import SummitSEO
from summit_seo.analyzers import AnalyzerFactory

# Initialize with accessibility focus
config = {
    "analyzer": {
        "accessibility": {
            "wcag_level": "AA",  # AA is the commonly required compliance level
            "check_color_contrast": True,
            "check_alt_text": True,
            "check_form_labels": True,
            "check_aria": True,
            "check_keyboard_navigation": True
        }
    }
}

seo = SummitSEO(config=config)

# Analyze accessibility
result = seo.analyze("https://example.com", analyzers=["accessibility"])

# Generate accessibility report
seo.report(result, format="html", output_path="accessibility_report.html")

# Group findings by WCAG criteria
accessibility_findings = result.analyzer_results["accessibility"]["findings"]
wcag_criteria = {}

for finding in accessibility_findings:
    criterion = finding.get("wcag_criterion", "general")
    if criterion not in wcag_criteria:
        wcag_criteria[criterion] = []
    wcag_criteria[criterion].append(finding)

# Print WCAG compliance issues
print("WCAG Compliance Issues:")
for criterion, findings in wcag_criteria.items():
    print(f"\n== {criterion} ==")
    for finding in findings:
        print(f"- {finding['message']}")
        print(f"  Location: {finding.get('location', 'N/A')}")
        print(f"  Remediation: {finding['remediation']}")
```

2. **Run the script:**

```bash
python accessibility_check.py
```

3. **Address accessibility issues:**
   - Prioritize issues by severity and impact
   - Retest after implementing changes

## Mobile-Friendly Analysis

This use case analyzes mobile-friendliness of a website.

### Steps:

1. **Create a mobile-friendly analysis script:**

```python
from summit_seo import SummitSEO
from summit_seo.analyzers import AnalyzerFactory

# Initialize with mobile focus
config = {
    "analyzer": {
        "mobile_friendly": {
            "check_viewport": True,
            "check_responsive_design": True,
            "check_touch_targets": True,
            "check_font_sizes": True,
            "check_content_width": True,
            "check_mobile_speed": True
        }
    }
}

seo = SummitSEO(config=config)

# Analyze mobile-friendliness
result = seo.analyze("https://example.com", analyzers=["mobile_friendly"])

# Generate mobile-friendly report
seo.report(result, format="html", output_path="mobile_friendly_report.html")

# Print mobile optimization suggestions
mobile_findings = result.analyzer_results["mobile_friendly"]["findings"]
print("Mobile Optimization Suggestions:")
for finding in mobile_findings:
    print(f"- {finding['message']}")
    print(f"  Impact: {finding.get('impact', 'Medium')}")
    print(f"  Remediation: {finding['remediation']}")
    print()

# Check if the site is mobile-friendly overall
overall_score = result.analyzer_results["mobile_friendly"]["score"]
if overall_score >= 80:
    print("This site is generally mobile-friendly.")
elif overall_score >= 60:
    print("This site needs some mobile optimizations.")
else:
    print("This site is not mobile-friendly and needs significant improvements.")
```

2. **Run the script:**

```bash
python mobile_analysis.py
```

3. **Implement mobile optimizations:**
   - Ensure proper viewport configuration
   - Implement responsive design
   - Fix touch target sizing issues

## Continuous Monitoring Setup

This use case sets up continuous monitoring of a website's SEO health.

### Steps:

1. **Create a monitoring configuration file** (`monitor_config.json`):

```json
{
  "urls": [
    "https://example.com",
    "https://example.com/about",
    "https://example.com/products"
  ],
  "schedule": "daily",
  "analyzers": ["content", "meta", "performance", "security"],
  "alert_threshold": 70,
  "notification_email": "webmaster@example.com",
  "store_history": true,
  "history_path": "./history"
}
```

2. **Create a monitoring script:**

```python
from summit_seo import SummitSEO
from summit_seo.monitoring import Monitor
import json
import os
from datetime import datetime

# Load configuration
with open("monitor_config.json", "r") as f:
    config = json.load(f)

# Initialize Summit SEO
seo = SummitSEO()

# Initialize Monitor
monitor = Monitor(seo, config)

# Run a monitoring cycle
async def run_monitoring():
    results = await monitor.run_cycle()
    
    # Process results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("reports", exist_ok=True)
    
    # Generate consolidated report
    seo.report_batch(results, format="html", output_path=f"reports/monitor_report_{timestamp}.html")
    
    # Check for alerts
    alerts = monitor.get_alerts(results)
    if alerts:
        print(f"Found {len(alerts)} issues requiring attention:")
        for alert in alerts:
            print(f"- URL: {alert['url']}")
            print(f"  Issue: {alert['message']}")
            print(f"  Score: {alert['score']}")
            print()
    
    # Store history
    if config.get("store_history", False):
        monitor.store_history(results)
    
    # Generate trend report if history exists
    if config.get("store_history", False) and os.path.exists(config.get("history_path", "./history")):
        trend_report = monitor.generate_trend_report()
        with open(f"reports/trend_report_{timestamp}.html", "w") as f:
            f.write(trend_report)

# Run the monitoring
import asyncio
asyncio.run(run_monitoring())
```

3. **Set up a scheduled task:**

For Linux/Mac (crontab):
```
0 1 * * * /usr/bin/python3 /path/to/monitoring_script.py >> /path/to/monitoring.log 2>&1
```

For Windows (Task Scheduler):
```
schtasks /create /sc daily /tn "SEO Monitoring" /tr "python C:\path\to\monitoring_script.py" /st 01:00
```

4. **Review periodic reports:**
   - Check for trend patterns
   - Address persistent issues
   - Monitor overall SEO health over time

## Integration with CI/CD Pipeline

This use case integrates Summit SEO into a CI/CD pipeline to ensure SEO compliance with each deployment.

### Steps:

1. **Create a CI/CD integration script** (`ci_seo_check.py`):

```python
from summit_seo import SummitSEO
import sys
import json
import os

# Define minimum acceptable scores
MIN_SCORES = {
    "overall": 75,
    "performance": 70,
    "accessibility": 80,
    "seo": 75,
    "security": 85
}

# Website to test
# In CI/CD, this could be a staging environment URL
website_url = os.environ.get("TEST_WEBSITE_URL", "https://staging.example.com")

# Initialize analyzer
seo = SummitSEO()

# Run analysis
result = seo.analyze(website_url)

# Generate report for artifacts
seo.report(result, format="html", output_path="seo_report.html")

# Save JSON results for processing
with open("seo_results.json", "w") as f:
    json.dump(result.to_dict(), f, indent=2)

# Check if scores meet minimum requirements
scores = result.scores
failures = []

for category, min_score in MIN_SCORES.items():
    actual_score = scores.get(category, 0)
    if actual_score < min_score:
        failures.append(f"{category}: {actual_score} (minimum: {min_score})")

# Report results
if failures:
    print("SEO check failed. The following scores are below minimum requirements:")
    for failure in failures:
        print(f"- {failure}")
    sys.exit(1)
else:
    print("SEO check passed. All scores meet minimum requirements.")
    for category, score in scores.items():
        if category in MIN_SCORES:
            print(f"- {category}: {score} (minimum: {MIN_SCORES[category]})")
    sys.exit(0)
```

2. **Create a GitHub Actions workflow** (`.github/workflows/seo-check.yml`):

```yaml
name: SEO Check

on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]

jobs:
  seo-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install summit-seo
          
      - name: Start test server
        run: |
          # Start your application in the background
          # This is application-specific
          npm install
          npm run build
          npm run serve &
          sleep 10  # Wait for server to start
          
      - name: Run SEO check
        run: |
          export TEST_WEBSITE_URL=http://localhost:3000
          python ci_seo_check.py
          
      - name: Upload SEO report as artifact
        uses: actions/upload-artifact@v2
        with:
          name: seo-report
          path: |
            seo_report.html
            seo_results.json
```

3. **Configure failure thresholds:**
   - Adjust the minimum scores in `MIN_SCORES` based on your requirements
   - Consider starting with lower thresholds and gradually increasing them
   - Make critical SEO factors non-negotiable (e.g., proper meta tags)

4. **Deploy only when checks pass:**
   - Configure CI/CD to deploy only when SEO checks pass
   - Review artifacts from failed checks to understand issues

## Custom Report Generation

This use case creates custom SEO reports tailored to specific stakeholders.

### Steps:

1. **Create a custom report generator script:**

```python
from summit_seo import SummitSEO
from summit_seo.reporters import BaseReporter, ReporterFactory
from jinja2 import Environment, FileSystemLoader
import os
import json

# Define a custom reporter
class ExecutiveReporter(BaseReporter):
    def __init__(self, config=None):
        super().__init__(config or {})
        self.template_dir = self.config.get("template_dir", "./templates")
        self.template_name = self.config.get("template_name", "executive_summary.html")
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        self.template = self.env.get_template(self.template_name)
    
    async def _generate_report(self, data):
        # Extract key metrics for executive summary
        summary = {
            "url": data.get("url", ""),
            "overall_score": data.get("overall_score", 0),
            "scores": data.get("scores", {}),
            "critical_issues_count": sum(1 for issue in data.get("issues", []) 
                                     if issue.get("severity") == "critical"),
            "high_issues_count": sum(1 for issue in data.get("issues", []) 
                                 if issue.get("severity") == "high"),
            "top_issues": [issue for issue in data.get("issues", [])[:5] 
                         if issue.get("severity") in ["critical", "high"]],
            "performance_metrics": {
                "page_load_time": data.get("analyzer_results", {})
                .get("performance", {}).get("details", {}).get("page_load_time", 0),
                "page_size": data.get("analyzer_results", {})
                .get("performance", {}).get("details", {}).get("page_size", 0),
            },
            "seo_metrics": {
                "meta_score": data.get("analyzer_results", {})
                .get("meta", {}).get("score", 0),
                "content_score": data.get("analyzer_results", {})
                .get("content", {}).get("score", 0),
            },
            "recommendations": data.get("recommendations", [])[:3]
        }
        
        # Render template with data
        return self.template.render(summary=summary)

# Register custom reporter
ReporterFactory.register("executive", ExecutiveReporter)

# Create a directory for templates
os.makedirs("templates", exist_ok=True)

# Create a template file
with open("templates/executive_summary.html", "w") as f:
    f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Executive SEO Summary: {{ summary.url }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }
        .header { background-color: #2c3e50; color: white; padding: 20px; margin-bottom: 20px; }
        .score { font-size: 48px; font-weight: bold; }
        .metric { display: inline-block; width: 45%; margin: 10px; padding: 15px; border-radius: 5px; background-color: #f8f9fa; }
        .issues { margin: 20px 0; }
        .issue { padding: 10px; margin: 5px 0; border-left: 4px solid #e74c3c; background-color: #f8f9fa; }
        .recommendations { margin: 20px 0; }
        .recommendation { padding: 10px; margin: 5px 0; border-left: 4px solid #2ecc71; background-color: #f8f9fa; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Executive SEO Summary</h1>
        <p>{{ summary.url }}</p>
        <p>Generated on {{ now().strftime('%Y-%m-%d') }}</p>
    </div>
    
    <div class="overview">
        <h2>Overview</h2>
        <div class="score">{{ summary.overall_score }}/100</div>
        <p>This website has {{ summary.critical_issues_count }} critical and {{ summary.high_issues_count }} high-priority issues.</p>
    </div>
    
    <div class="metrics">
        <h2>Key Metrics</h2>
        <div class="metric">
            <h3>Performance</h3>
            <p>Score: {{ summary.scores.get('performance', 'N/A') }}/100</p>
            <p>Page Load Time: {{ '%.2f'|format(summary.performance_metrics.page_load_time) }}s</p>
            <p>Page Size: {{ '%.2f'|format(summary.performance_metrics.page_size / 1024 / 1024) }} MB</p>
        </div>
        <div class="metric">
            <h3>SEO</h3>
            <p>Meta Tags Score: {{ summary.seo_metrics.meta_score }}/100</p>
            <p>Content Score: {{ summary.seo_metrics.content_score }}/100</p>
        </div>
    </div>
    
    <div class="issues">
        <h2>Top Priority Issues</h2>
        {% for issue in summary.top_issues %}
        <div class="issue">
            <h3>{{ issue.message }}</h3>
            <p><strong>Severity:</strong> {{ issue.severity }}</p>
            <p><strong>Impact:</strong> {{ issue.get('impact', 'Medium') }}</p>
            <p><strong>Remediation:</strong> {{ issue.remediation }}</p>
        </div>
        {% endfor %}
        {% if not summary.top_issues %}
        <p>No critical or high-priority issues found.</p>
        {% endif %}
    </div>
    
    <div class="recommendations">
        <h2>Key Recommendations</h2>
        {% for recommendation in summary.recommendations %}
        <div class="recommendation">
            <h3>{{ recommendation.title }}</h3>
            <p>{{ recommendation.description }}</p>
            <p><strong>Priority:</strong> {{ recommendation.priority }}</p>
            <p><strong>Steps:</strong></p>
            <ul>
                {% for step in recommendation.steps %}
                <li>{{ step }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endfor %}
    </div>
</body>
</html>
    """)

# Create analysis and report script
with open("generate_executive_report.py", "w") as f:
    f.write("""
from summit_seo import SummitSEO

# Initialize analyzer
seo = SummitSEO()

# Analyze website
result = seo.analyze("https://example.com")

# Generate executive report
seo.report(result, reporter="executive", output_path="executive_summary.html",
           config={"template_dir": "./templates", "template_name": "executive_summary.html"})

print("Executive summary generated: executive_summary.html")
    """)
```

2. **Run the script to set up the custom reporter:**

```bash
python custom_report.py
```

3. **Generate the executive report:**

```bash
python generate_executive_report.py
```

4. **Create other specialized reports as needed:**
   - Technical SEO report for developers
   - Content SEO report for content teams
   - Competitive analysis report for marketing

These tutorials cover the most common use cases for Summit SEO, providing practical examples that you can adapt to your specific needs. Each tutorial includes complete code examples that you can use as starting points for your own implementations. 