# CLI Output Formatter Guide

## Overview

The Summit SEO Output Formatter provides customizable output formats for displaying analysis results in the command-line interface. This component allows users to choose their preferred output format for better integration with other tools and workflows.

## Supported Formats

The output formatter supports the following formats:

| Format | Description | Best For |
| ------ | ----------- | -------- |
| Plain  | Simple text output with indentation | Human readability |
| JSON   | Standard JSON format | Integration with other tools, parsing |
| YAML   | YAML format (with fallback to JSON) | Configuration files, readability |
| CSV    | Comma-separated values | Spreadsheet import, data analysis |
| Table  | Tabular format with borders | Terminal display, structured view |

## Integration

The output formatter is integrated with the CLI through the following command-line arguments:

```bash
# Specify output format
summit-seo analyze example.com --output-format=json

# Specify output width for formatted display
summit-seo analyze example.com --output-format=table --output-width=120
```

It's also used internally for various commands, such as:

```bash
# List available components
summit-seo list analyzers
```

## Configuration

### Format Selection

You can select the output format using:

1. Command-line arguments:
   ```bash
   --output-format=FORMAT  # FORMAT can be plain, json, yaml, csv, or table
   ```

2. Programmatically:
   ```python
   from summit_seo.cli.output_formatter import set_output_format, OutputFormat
   
   # Set the format
   set_output_format(OutputFormat.JSON, indent=4)
   ```

### Width Customization

For formats that support width customization (Plain and Table):

```bash
--output-width=WIDTH  # WIDTH is the number of characters
```

### Global Functions

The following global functions are available for formatting:

- `format_result(result)`: Format analysis results
- `format_error(error)`: Format error messages
- `format_summary(summary)`: Format summary information
- `format_list(items, title)`: Format a list of items

## Format Details

### Plain Format

Simple text output with indentation:

```
Test Analysis
Score: 85.5/100

Issues:
  - Issue 1
    Severity: high
    Location: header
  - Issue 2
    Severity: medium
    Location: body
```

### JSON Format

Standard JSON format:

```json
{
  "title": "Test Analysis",
  "score": 85.5,
  "issues": [
    {
      "description": "Issue 1",
      "severity": "high",
      "location": "header"
    },
    {
      "description": "Issue 2",
      "severity": "medium",
      "location": "body"
    }
  ]
}
```

### YAML Format

YAML format (requires PyYAML package, falls back to JSON if not available):

```yaml
title: Test Analysis
score: 85.5
issues:
- description: Issue 1
  severity: high
  location: header
- description: Issue 2
  severity: medium
  location: body
```

### CSV Format

Comma-separated values for tables:

```csv
Title: Test Analysis
Score: 85.5/100

Issues:
Description,Severity,Location
Issue 1,high,header
Issue 2,medium,body
```

### Table Format

Tabular format with borders:

```
+--------------------+
| Test Analysis      |
+--------------------+
| Score: 85.5/100    |
+--------------------+

Issues:
+-------------+---------+----------+
| DESCRIPTION | SEVERITY| LOCATION |
+-------------+---------+----------+
| Issue 1     | high    | header   |
| Issue 2     | medium  | body     |
+-------------+---------+----------+
```

## Architecture

The output formatter uses a clean, object-oriented architecture:

1. `OutputFormat` enum defines available formats
2. `OutputFormatter` abstract base class defines the interface
3. Format-specific implementations (e.g., `JsonFormatter`, `CsvFormatter`)
4. `OutputManager` singleton for centralized format management
5. Global functions for easy access

## Extension

To add a new output format:

1. Add a new value to the `OutputFormat` enum
2. Create a new formatter class that inherits from `OutputFormatter`
3. Implement all required methods
4. Register the new formatter in the `OutputManager._create_formatter` method

## Examples

### Basic CLI Example

```bash
# Generate JSON output
summit-seo analyze example.com --output-format=json > results.json

# Generate table output with custom width
summit-seo analyze example.com --output-format=table --output-width=100
```

### Programmatic Example

```python
from summit_seo.cli.output_formatter import (
    format_result, 
    format_error, 
    set_output_format, 
    OutputFormat
)

# Set the output format to JSON
set_output_format(OutputFormat.JSON, indent=2)

# Format analysis results
result = {
    "title": "SEO Analysis",
    "score": 92.5,
    "issues": [{"description": "Missing meta description", "severity": "medium"}]
}
formatted_output = format_result(result)
print(formatted_output)

# Handle errors
try:
    # Some operation
    pass
except Exception as e:
    error_output = format_error(str(e))
    print(error_output)
```

## Best Practices

1. Use JSON or YAML for machine parsing and automation
2. Use Table format for interactive terminal display
3. Use CSV for data import into analysis tools
4. Use Plain for simple, readable output
5. Consider output width for terminal display (usually 80-120 characters) 