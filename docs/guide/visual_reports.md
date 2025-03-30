# Visual Reports Guide

Summit SEO now includes a powerful visual reporting feature that enhances your SEO analysis results with interactive charts and visualizations. This guide explains how to use and customize visual reports in your projects.

## Overview

Visual reports transform raw SEO analysis data into clear, actionable insights through charts and data visualizations. They help you:

- Quickly understand overall site performance
- Identify critical issues and prioritize fixes
- Compare performance across different aspects of your site
- Share results with stakeholders in an accessible format

## Getting Started

### Command Line Usage

To generate a visual report from the command line:

```bash
summit-seo analyze https://example.com --visual
```

This will run a full SEO analysis and generate an HTML report with visualizations in the current directory.

### Additional Options

You can customize the output with the following options:

```bash
summit-seo analyze https://example.com --visual -o ./reports -s animated -v
```

Where:
- `-o ./reports`: Specifies the output directory
- `-s animated`: Sets the progress display style during analysis
- `-v`: Enables verbose output for debugging

### Programmatic Usage

You can also generate visual reports programmatically:

```python
import asyncio
from summit_seo.reporter import ReporterFactory

async def generate_visual_report(analysis_results):
    # Create a visual HTML reporter
    reporter = ReporterFactory.create("VisualHTMLReporter", {
        "visualizer_name": "matplotlib",  # Visualization backend
        "visualizer_config": {
            "figure_size": (10, 6),       # Chart dimensions in inches
            "dpi": 100,                   # Resolution
            "style": "seaborn-v0_8-whitegrid"  # Style theme
        }
    })
    
    # Prepare the data
    data = {
        "url": "https://example.com",
        "results": analysis_results,
        "output_file": "my_visual_report.html"
    }
    
    # Generate the report
    result = await reporter.generate_report(data)
    
    print(f"Report generated at: {result.path}")

# Run with your analysis results
asyncio.run(generate_visual_report(analysis_results))
```

## Report Components

### Overview Dashboard

The visual report begins with an overview dashboard containing four key visualizations:

1. **Score Distribution Chart** - Shows scores across all analyzers
2. **Issues by Severity Chart** - Displays the distribution of issues by severity level
3. **Recommendations by Priority Chart** - Groups recommendations by priority level
4. **Quick Win Opportunities Chart** - Highlights issues that can be fixed quickly for immediate impact

### Analyzer Sections

Following the dashboard, each analyzer has its own section containing:

- Score indicator with color coding
- List of issues with severity indicators
- Warnings with suggested fixes
- Recommendations for improvements

## Customization Options

### Visualization Styles

The visual reports support different visualization styles through matplotlib style sheets:

- **default** - Clean, professional style with a light background
- **dark** - Dark background for presentations and low-light viewing
- **minimal** - Simplified charts with minimal styling
- **presentation** - Bold style optimized for presentations

You can set the style when creating the reporter:

```python
reporter = ReporterFactory.create("VisualHTMLReporter", {
    "visualizer_config": {
        "style": "dark_background"  # Use dark style
    }
})
```

### Custom Templates

You can provide your own HTML template to customize the report appearance:

```python
reporter = ReporterFactory.create("VisualHTMLReporter", {
    "template_path": "/path/to/my_template.html"
})
```

Your template should include the Jinja2 template variables used in the default template, such as `{{ data.url }}`, `{{ data.timestamp }}`, and `{{ charts.score_distribution.data_uri }}`.

## Advanced Configuration

### Chart Customization

To customize the appearance of charts, you can adjust the visualizer configuration:

```python
reporter = ReporterFactory.create("VisualHTMLReporter", {
    "visualizer_config": {
        "figure_size": (12, 8),     # Width and height in inches
        "dpi": 150,                 # Resolution (dots per inch)
        "font_size": 12,            # Base font size
        "colormap": "viridis",      # Color palette
        "output_format": "svg"      # Output format (png, svg, pdf)
    }
})
```

### Selective Visualization

You can control which parts of the report are shown:

```python
reporter = ReporterFactory.create("VisualHTMLReporter", {
    "include_dashboard": True,             # Show/hide the dashboard
    "include_analyzer_details": True       # Show/hide individual analyzer sections
})
```

## Generating Multiple Reports

To generate reports with different styles for comparison:

```python
async def generate_multiple_styles():
    styles = ["seaborn-v0_8-whitegrid", "dark_background", "bmh", "fivethirtyeight"]
    
    for style in styles:
        reporter = ReporterFactory.create("VisualHTMLReporter", {
            "visualizer_config": {"style": style},
        })
        
        data = {
            "url": "https://example.com",
            "results": analysis_results,
            "output_file": f"report_{style}.html"
        }
        
        await reporter.generate_report(data)
```

## Examples

Check out the example script at `examples/visual_report_example.py` for a complete demonstration of how to generate visual reports with different styles and configurations.

## Troubleshooting

### Missing Dependencies

If you see errors related to missing libraries, make sure you have installed the visualization dependencies:

```bash
pip install matplotlib pandas numpy
```

### Chart Generation Issues

If charts aren't appearing correctly:

1. Check that matplotlib is properly installed
2. Verify that the data contains valid scores and metrics
3. Try a different matplotlib style sheet
4. Check the log for specific error messages

### Memory Errors

For large reports with many visualizations, you might encounter memory issues. Solutions include:

- Reduce the DPI setting
- Decrease the figure size
- Generate fewer charts per report
- Use PNG format instead of SVG for larger datasets 