# Creating a Custom Reporter

This guide demonstrates how to create a custom reporter by extending the `BaseReporter` class. Reporters in Summit SEO are responsible for transforming analysis results into various output formats, such as JSON, HTML, CSV, or PDF.

## Overview

Reporters are responsible for:
1. Taking the raw analysis results from various analyzers
2. Processing and formatting the data according to specific requirements
3. Generating output in the desired format (e.g., JSON, XML, HTML, PDF, custom formats)

By creating a custom reporter, you can generate reports in specialized formats or with specific customizations to meet your project's needs.

## When to Create a Custom Reporter

Consider creating a custom reporter when:
- You need output in a format not supported by the built-in reporters
- You want to integrate with a specific reporting tool or platform
- You need custom formatting or styling for your reports
- You want to add specific metrics or visualizations to your reports

## Step 1: Import Required Components

Start by importing the base reporter classes and any required libraries:

```python
from typing import Dict, Any, List, Optional
from datetime import datetime
from summit_seo.reporter.base import BaseReporter, ReportResult, ReportGenerationError, ReportMetadata
```

## Step 2: Define Your Reporter Class

Create a class that inherits from `BaseReporter`:

```python
class MarkdownReporter(BaseReporter):
    """Reporter for generating Markdown format reports."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Markdown reporter.
        
        Args:
            config: Optional configuration dictionary.
                   Supported keys:
                   - include_toc: Whether to include table of contents (default: True)
                   - max_issues: Maximum number of issues to include (default: 10)
                   - include_recommendations: Whether to include recommendations (default: True)
                   - include_metadata: Whether to include report metadata (default: True)
                   - heading_style: Style for headings ("hash" or "underline") (default: "hash")
        """
        default_config = {
            'include_toc': True,
            'max_issues': 10,
            'include_recommendations': True,
            'include_metadata': True,
            'heading_style': 'hash'  # "hash" (#) or "underline" (===)
        }
        
        # Merge provided config with defaults
        merged_config = {**default_config, **(config or {})}
        super().__init__(merged_config)
```

## Step 3: Implement Configuration Validation

Implement the required `validate_config` method to validate your reporter's configuration:

```python
    def validate_config(self) -> None:
        """Validate the reporter configuration.
        
        Raises:
            ValueError: If configuration is invalid.
        """
        # Validate boolean options
        bool_options = ['include_toc', 'include_recommendations', 'include_metadata']
        for option in bool_options:
            if option in self.config and not isinstance(self.config[option], bool):
                raise ValueError(f"{option} must be a boolean")
        
        # Validate max_issues
        if 'max_issues' in self.config:
            if not isinstance(self.config['max_issues'], int) or self.config['max_issues'] < 0:
                raise ValueError("max_issues must be a non-negative integer")
        
        # Validate heading_style
        if 'heading_style' in self.config:
            if self.config['heading_style'] not in ['hash', 'underline']:
                raise ValueError("heading_style must be either 'hash' or 'underline'")
```

## Step 4: Implement Report Generation

Implement the required `generate_report` method to create reports from analysis results:

```python
    async def generate_report(self, data: Dict[str, Any]) -> ReportResult:
        """Generate a Markdown report from the analysis results.
        
        Args:
            data: Dictionary containing analysis results.
        
        Returns:
            ReportResult containing the generated Markdown and metadata.
        
        Raises:
            ReportGenerationError: If report generation fails.
        """
        try:
            # Validate input data
            self._validate_data(data)
            
            # Create metadata
            metadata = self._create_metadata('markdown')
            
            # Generate markdown content
            markdown_content = self._generate_markdown(data, metadata)
            
            return ReportResult(
                content=markdown_content,
                metadata=metadata,
                format='markdown'
            )
            
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate Markdown report: {str(e)}")
```

## Step 5: Implement Batch Report Generation

Implement the required `generate_batch_report` method to handle multiple results:

```python
    async def generate_batch_report(self, data: List[Dict[str, Any]]) -> ReportResult:
        """Generate a Markdown report for multiple analysis results.
        
        Args:
            data: List of dictionaries containing analysis results.
        
        Returns:
            ReportResult containing the generated Markdown and metadata.
        
        Raises:
            ReportGenerationError: If report generation fails.
        """
        try:
            # Validate batch data
            self._validate_batch_data(data)
            
            # Create metadata
            metadata = self._create_metadata('markdown')
            
            # Generate batch markdown content
            markdown_content = self._generate_batch_markdown(data, metadata)
            
            return ReportResult(
                content=markdown_content,
                metadata=metadata,
                format='markdown'
            )
            
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate batch Markdown report: {str(e)}")
```

## Step 6: Implement Helper Methods

Add helper methods to support your report generation:

```python
    def _generate_markdown(self, data: Dict[str, Any], metadata: ReportMetadata) -> str:
        """Generate markdown report content.
        
        Args:
            data: Analysis results data.
            metadata: Report metadata.
        
        Returns:
            Markdown formatted string.
        """
        url = data['url']
        timestamp = data['timestamp']
        results = data['results']
        
        # Initialize the report content
        content = []
        
        # Add title
        content.append(f"# SEO Analysis Report: {url}")
        content.append(f"\nAnalysis performed on: {timestamp}\n")
        
        # Add table of contents if configured
        if self.config['include_toc']:
            content.append("## Table of Contents\n")
            content.append("1. [Summary](#summary)")
            analyzer_num = 2
            for analyzer_name in results.keys():
                content.append(f"{analyzer_num}. [{analyzer_name.capitalize()} Analysis](#{analyzer_name.lower().replace(' ', '-')})")
                analyzer_num += 1
            if self.config['include_metadata']:
                content.append(f"{analyzer_num}. [Report Metadata](#report-metadata)")
            content.append("\n")
        
        # Add summary section
        content.append(self._generate_summary_section(results))
        
        # Add results for each analyzer
        for analyzer_name, result in results.items():
            content.append(self._generate_analyzer_section(analyzer_name, result))
        
        # Add metadata if configured
        if self.config['include_metadata']:
            content.append(self._generate_metadata_section(metadata))
        
        return "\n".join(content)
    
    def _generate_summary_section(self, results: Dict[str, Any]) -> str:
        """Generate summary section of the report.
        
        Args:
            results: Dictionary of analyzer results.
        
        Returns:
            Markdown formatted string for summary section.
        """
        section = []
        
        if self.config['heading_style'] == 'hash':
            section.append("## Summary")
        else:
            section.append("Summary\n=======")
        
        # Calculate overall score
        scores = [result['score'] for result in results.values() if 'score' in result]
        if scores:
            avg_score = sum(scores) / len(scores)
            section.append(f"\nOverall Score: **{avg_score:.1f}** / 100\n")
        
        # Add analysis overview
        section.append("### Analysis Overview\n")
        section.append("| Analyzer | Score | Issues | Warnings |")
        section.append("|----------|-------|--------|----------|")
        
        for analyzer_name, result in results.items():
            score = result.get('score', 'N/A')
            issues = len(result.get('issues', []))
            warnings = len(result.get('warnings', []))
            section.append(f"| {analyzer_name.capitalize()} | {score:.1f} | {issues} | {warnings} |")
        
        section.append("\n")
        return "\n".join(section)
    
    def _generate_analyzer_section(self, analyzer_name: str, result: Dict[str, Any]) -> str:
        """Generate section for an individual analyzer.
        
        Args:
            analyzer_name: Name of the analyzer.
            result: Analysis result for this analyzer.
        
        Returns:
            Markdown formatted string for analyzer section.
        """
        section = []
        title = f"{analyzer_name.capitalize()} Analysis"
        
        if self.config['heading_style'] == 'hash':
            section.append(f"## {title}")
        else:
            section.append(f"{title}\n" + "=" * len(title))
        
        # Add score
        if 'score' in result:
            section.append(f"\nScore: **{result['score']:.1f}** / 100\n")
        
        # Add issues
        issues = result.get('issues', [])
        if issues:
            section.append("### Issues\n")
            max_issues = self.config['max_issues']
            for i, issue in enumerate(issues[:max_issues]):
                section.append(f"- {issue}")
            
            if len(issues) > max_issues:
                section.append(f"- *...and {len(issues) - max_issues} more issues*")
            
            section.append("")
        
        # Add warnings
        warnings = result.get('warnings', [])
        if warnings:
            section.append("### Warnings\n")
            for warning in warnings[:max_issues]:
                section.append(f"- {warning}")
            
            if len(warnings) > max_issues:
                section.append(f"- *...and {len(warnings) - max_issues} more warnings*")
            
            section.append("")
        
        # Add recommendations if configured
        if self.config['include_recommendations']:
            recommendations = result.get('recommendations', [])
            enhanced_recs = result.get('enhanced_recommendations', [])
            
            if recommendations or enhanced_recs:
                section.append("### Recommendations\n")
                
                # Handle enhanced recommendations first
                if enhanced_recs:
                    for rec in enhanced_recs[:max_issues]:
                        section.append(f"- **{rec.get('message')}**")
                        if 'implementation_guide' in rec:
                            section.append(f"  - Implementation: {rec.get('implementation_guide')}")
                    
                    if len(enhanced_recs) > max_issues:
                        section.append(f"- *...and {len(enhanced_recs) - max_issues} more recommendations*")
                
                # Fall back to simple recommendations if no enhanced ones
                elif recommendations:
                    for rec in recommendations[:max_issues]:
                        section.append(f"- {rec}")
                    
                    if len(recommendations) > max_issues:
                        section.append(f"- *...and {len(recommendations) - max_issues} more recommendations*")
                
                section.append("")
        
        return "\n".join(section)
    
    def _generate_metadata_section(self, metadata: ReportMetadata) -> str:
        """Generate metadata section of the report.
        
        Args:
            metadata: Report metadata.
        
        Returns:
            Markdown formatted string for metadata section.
        """
        section = []
        
        if self.config['heading_style'] == 'hash':
            section.append("## Report Metadata")
        else:
            section.append("Report Metadata\n===============")
        
        section.append("\n| Property | Value |")
        section.append("|----------|-------|")
        section.append(f"| Generated | {metadata.timestamp} |")
        section.append(f"| Format | {metadata.format} |")
        section.append(f"| Version | {metadata.version} |")
        section.append(f"| Generator | {metadata.generator} |")
        
        return "\n".join(section)
    
    def _generate_batch_markdown(self, data: List[Dict[str, Any]], metadata: ReportMetadata) -> str:
        """Generate markdown for batch report.
        
        Args:
            data: List of analysis results data.
            metadata: Report metadata.
        
        Returns:
            Markdown formatted string for batch report.
        """
        batch_content = []
        
        # Add title
        batch_content.append("# SEO Batch Analysis Report")
        batch_content.append(f"\nAnalysis performed on: {metadata.timestamp}")
        batch_content.append(f"Total sites analyzed: {len(data)}\n")
        
        # Add table of contents if configured
        if self.config['include_toc']:
            batch_content.append("## Table of Contents\n")
            batch_content.append("1. [Summary](#summary)")
            for i, item in enumerate(data, 2):
                url = item['url']
                site_name = url.replace('https://', '').replace('http://', '').split('/')[0]
                batch_content.append(f"{i}. [{site_name}](#{site_name.lower().replace('.', '-')})")
            
            if self.config['include_metadata']:
                batch_content.append(f"{len(data) + 2}. [Report Metadata](#report-metadata)")
            
            batch_content.append("\n")
        
        # Add batch summary
        batch_content.append(self._generate_batch_summary(data))
        
        # Add individual site reports
        for site_data in data:
            url = site_data['url']
            site_name = url.replace('https://', '').replace('http://', '').split('/')[0]
            
            if self.config['heading_style'] == 'hash':
                batch_content.append(f"## {site_name}")
            else:
                batch_content.append(f"{site_name}\n" + "=" * len(site_name))
            
            batch_content.append(f"\nURL: {url}")
            batch_content.append(f"Analysis Time: {site_data['timestamp']}\n")
            
            # Add summary for this site
            results = site_data['results']
            scores = [result['score'] for result in results.values() if 'score' in result]
            if scores:
                avg_score = sum(scores) / len(scores)
                batch_content.append(f"Overall Score: **{avg_score:.1f}** / 100\n")
            
            # Add quick overview table
            batch_content.append("| Analyzer | Score | Issues |")
            batch_content.append("|----------|-------|--------|")
            
            for analyzer_name, result in results.items():
                score = result.get('score', 'N/A')
                issues = len(result.get('issues', []))
                batch_content.append(f"| {analyzer_name.capitalize()} | {score:.1f} | {issues} |")
            
            batch_content.append("\n")
            
            # Add top issues
            all_issues = []
            for analyzer, result in results.items():
                for issue in result.get('issues', [])[:3]:  # Top 3 issues per analyzer
                    all_issues.append(f"- **{analyzer.capitalize()}**: {issue}")
            
            if all_issues:
                batch_content.append("### Top Issues\n")
                batch_content.extend(all_issues[:self.config['max_issues']])
                batch_content.append("\n")
        
        # Add metadata if configured
        if self.config['include_metadata']:
            batch_content.append(self._generate_metadata_section(metadata))
        
        return "\n".join(batch_content)
    
    def _generate_batch_summary(self, data: List[Dict[str, Any]]) -> str:
        """Generate summary for batch report.
        
        Args:
            data: List of analysis results data.
        
        Returns:
            Markdown formatted string for batch summary.
        """
        if self.config['heading_style'] == 'hash':
            summary = ["## Summary\n"]
        else:
            summary = ["Summary\n=======\n"]
        
        # Calculate average scores across all sites
        site_scores = []
        analyzer_scores = {}
        
        for site_data in data:
            results = site_data['results']
            
            # Calculate average score for this site
            site_avg = sum(r['score'] for r in results.values() if 'score' in r) / len(results) if results else 0
            site_scores.append(site_avg)
            
            # Track scores by analyzer
            for analyzer, result in results.items():
                if 'score' in result:
                    if analyzer not in analyzer_scores:
                        analyzer_scores[analyzer] = []
                    analyzer_scores[analyzer].append(result['score'])
        
        # Overall average
        if site_scores:
            summary.append(f"Overall Average Score: **{sum(site_scores) / len(site_scores):.1f}** / 100\n")
        
        # Summary table
        summary.append("| Metric | Value |")
        summary.append("|--------|-------|")
        summary.append(f"| Sites Analyzed | {len(data)} |")
        
        if site_scores:
            summary.append(f"| Highest Score | {max(site_scores):.1f} |")
            summary.append(f"| Lowest Score | {min(site_scores):.1f} |")
        
        summary.append("\n### Analyzer Performance\n")
        
        summary.append("| Analyzer | Average Score |")
        summary.append("|----------|---------------|")
        
        for analyzer, scores in analyzer_scores.items():
            avg = sum(scores) / len(scores) if scores else 0
            summary.append(f"| {analyzer.capitalize()} | {avg:.1f} |")
        
        return "\n".join(summary)
```

## Step 7: Register Your Reporter with the Factory

Register your custom reporter with the reporter factory to make it available through the standard interface:

```python
from summit_seo.reporter import ReporterFactory

# Register your custom reporter
ReporterFactory.register('markdown', MarkdownReporter)
```

## Step 8: Use Your Custom Reporter

Now you can use your custom reporter in your SEO analysis workflow:

```python
import asyncio
from summit_seo.reporter import ReporterFactory

async def generate_markdown_report():
    # Sample analysis results
    analysis_results = {
        'url': 'https://example.com',
        'timestamp': '2023-04-15T14:30:00',
        'results': {
            'title': {
                'score': 85.5,
                'issues': [
                    'Title length (55 characters) is less than recommended (60-70 characters)',
                    'Title does not include main keyword'
                ],
                'warnings': [
                    'Title does not include brand name'
                ],
                'recommendations': [
                    'Increase title length to 60-70 characters',
                    'Include main keyword at the beginning of the title',
                    'Add brand name at the end of the title'
                ]
            },
            'meta': {
                'score': 72.0,
                'issues': [
                    'Meta description missing',
                    'Canonical URL not set'
                ],
                'warnings': [],
                'recommendations': [
                    'Add a meta description between 150-160 characters',
                    'Set canonical URL to avoid duplicate content issues'
                ]
            }
        }
    }
    
    # Create the reporter factory
    factory = ReporterFactory()
    
    # Create your reporter with custom configuration
    reporter = factory.create('markdown', {
        'include_toc': True,
        'max_issues': 5,
        'heading_style': 'hash'
    })
    
    # Generate the report
    result = await reporter.generate_report(analysis_results)
    
    # Save the report to a file
    with open('seo_report.md', 'w') as f:
        f.write(result.content)
    
    print(f"Report generated: seo_report.md")
    return result

# Run the report generation
asyncio.run(generate_markdown_report())
```

## Step 9: Generate Batch Reports

For multiple sites or pages, you can generate batch reports:

```python
import asyncio
from summit_seo.reporter import ReporterFactory

async def generate_batch_markdown_report():
    # Sample batch analysis results
    batch_results = [
        {
            'url': 'https://example.com/home',
            'timestamp': '2023-04-15T14:30:00',
            'results': {
                'title': {'score': 85.5, 'issues': ['Title too short']},
                'meta': {'score': 72.0, 'issues': ['Meta description missing']}
            }
        },
        {
            'url': 'https://example.com/about',
            'timestamp': '2023-04-15T14:35:00',
            'results': {
                'title': {'score': 92.0, 'issues': []},
                'meta': {'score': 65.0, 'issues': ['Meta description too long']}
            }
        },
        {
            'url': 'https://example.com/contact',
            'timestamp': '2023-04-15T14:40:00',
            'results': {
                'title': {'score': 78.5, 'issues': ['Title missing brand name']},
                'meta': {'score': 88.0, 'issues': []}
            }
        }
    ]
    
    # Create the reporter factory
    factory = ReporterFactory()
    
    # Create your reporter
    reporter = factory.create('markdown')
    
    # Generate the batch report
    result = await reporter.generate_batch_report(batch_results)
    
    # Save the report to a file
    with open('seo_batch_report.md', 'w') as f:
        f.write(result.content)
    
    print(f"Batch report generated: seo_batch_report.md")
    return result

# Run the batch report generation
asyncio.run(generate_batch_markdown_report())
```

## Complete Example

The complete Markdown reporter implementation is available as a gist:

https://gist.github.com/summit-seo/markdown-reporter-example

## Best Practices for Custom Reporters

1. **Validate Configuration**: Always validate all configuration parameters
2. **Handle Errors Gracefully**: Catch and report all potential errors
3. **Support Batch Reports**: Implement efficient batch reporting for multiple results
4. **Make Configuration Flexible**: Allow customization through configuration options
5. **Maintain Consistent Structure**: Follow the same structure across different reports
6. **Include Metadata**: Add report metadata to help with tracking and versioning
7. **Test Different Input Data**: Ensure your reporter works with various data structures

## Related Documentation

- [API Reference for BaseReporter](../api/reporters.md)
- [Reporter Factory Documentation](../guide/factories.md)
- [Custom Analyzer Creation](custom_analyzer.md)
- [Custom Processor Creation](custom_processor.md)
- [Report Output Formats](../guide/report_formats.md) 