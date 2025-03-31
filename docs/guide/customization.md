# Summit SEO Customization Guide

This guide explains how to customize and configure Summit SEO to suit your specific needs without having to develop full plugins.

## Table of Contents

1. [Configuration Options](#configuration-options)
2. [Custom Reporting Templates](#custom-reporting-templates)
3. [Scoring Algorithms](#scoring-algorithms)
4. [Integration with External Systems](#integration-with-external-systems)
5. [Custom Rules and Thresholds](#custom-rules-and-thresholds)
6. [Custom CSS for Reports](#custom-css-for-reports)
7. [White Labeling](#white-labeling)
8. [Internationalization](#internationalization)
9. [Custom Data Sources](#custom-data-sources)
10. [Advanced Customization](#advanced-customization)

## Configuration Options

Summit SEO provides extensive configuration options that allow you to customize its behavior without coding. Configuration can be specified in several ways:

### Configuration File

Create a JSON or YAML configuration file:

```json
{
  "general": {
    "user_agent": "MySEOTool/1.0",
    "timeout": 60,
    "parallel": true,
    "max_workers": 8
  },
  "collection": {
    "max_pages": 500,
    "max_depth": 5,
    "follow_external_links": false,
    "respect_robots_txt": true
  },
  "analysis": {
    "analyzers": ["security", "performance", "schema", "accessibility", "mobile", "social"],
    "performance": {
      "page_speed_threshold": 3000,
      "resource_size_threshold": 1000000
    },
    "security": {
      "check_xss": true,
      "check_csrf": true,
      "check_https": true,
      "check_headers": true
    }
  },
  "reporting": {
    "format": "html",
    "template": "custom",
    "logo_path": "/path/to/logo.png",
    "include_timestamp": true,
    "include_charts": true
  }
}
```

Use this configuration with:

```bash
summit-seo analyze --url https://example.com --config my-config.json
```

### Environment Variables

Configuration can also be specified using environment variables:

```bash
# Basic configuration
export SUMMIT_SEO_USER_AGENT="MySEOTool/1.0"
export SUMMIT_SEO_TIMEOUT=60
export SUMMIT_SEO_MAX_PAGES=500

# Analyzer-specific configuration
export SUMMIT_SEO_ANALYZERS="security,performance,schema"
export SUMMIT_SEO_PERFORMANCE_PAGE_SPEED_THRESHOLD=3000
export SUMMIT_SEO_SECURITY_CHECK_XSS=true

# Run the tool
summit-seo analyze --url https://example.com
```

### Command Line Arguments

Most configuration options can be specified directly on the command line:

```bash
summit-seo analyze --url https://example.com \
  --user-agent "MySEOTool/1.0" \
  --timeout 60 \
  --max-pages 500 \
  --analyzers security,performance,schema \
  --performance-page-speed-threshold 3000 \
  --security-check-xss true
```

### Configuration Precedence

Configuration options are applied in the following order (later overrides earlier):

1. Default built-in configuration
2. Configuration file
3. Environment variables
4. Command line arguments

## Custom Reporting Templates

You can create custom report templates to change the look and feel of generated reports.

### HTML Templates

Create a custom HTML template using Jinja2 syntax:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ analysis_result.url }} - SEO Analysis</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    {% if custom_css %}
    <style>{{ custom_css }}</style>
    {% else %}
    <link rel="stylesheet" href="default.css">
    {% endif %}
</head>
<body>
    <header>
        {% if logo_path %}
        <img src="{{ logo_path }}" alt="Logo" class="logo">
        {% endif %}
        <h1>SEO Analysis Report</h1>
        <p class="url">{{ analysis_result.url }}</p>
        <p class="timestamp">Generated on {{ timestamp }}</p>
    </header>
    
    <section class="summary">
        <h2>Overall Score: {{ analysis_result.overall_score }}</h2>
        <div class="score-chart">
            <!-- Custom chart rendering code -->
            <div class="score-gauge" style="--score: {{ analysis_result.overall_score }}%"></div>
        </div>
    </section>
    
    {% for analyzer_name, analyzer_result in analysis_result.analyzers.items() %}
    <section class="analyzer-results">
        <h2>{{ analyzer_name|title }} Analysis</h2>
        <p class="score">Score: {{ analyzer_result.score }}</p>
        
        <h3>Findings</h3>
        <table>
            <thead>
                <tr>
                    <th>Check</th>
                    <th>Status</th>
                    <th>Message</th>
                    <th>Recommendation</th>
                </tr>
            </thead>
            <tbody>
                {% for finding in analyzer_result.findings %}
                <tr class="{{ finding.status }}">
                    <td>{{ finding.type }}</td>
                    <td>{{ finding.status|upper }}</td>
                    <td>{{ finding.message }}</td>
                    <td>{{ finding.recommendation }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </section>
    {% endfor %}
    
    <footer>
        <p>Powered by Summit SEO</p>
        {% if custom_footer %}
        <div class="custom-footer">{{ custom_footer }}</div>
        {% endif %}
    </footer>
</body>
</html>
```

Save this template to `~/.summit-seo/templates/my-template.html` and use it with:

```bash
summit-seo analyze --url https://example.com --format html --template my-template
```

### Markdown Templates

You can also create custom Markdown templates:

```markdown
# SEO Analysis Report for {{ analysis_result.url }}

Generated on {{ timestamp }}

## Overall Score: {{ analysis_result.overall_score }}

{% for analyzer_name, analyzer_result in analysis_result.analyzers.items() %}
## {{ analyzer_name|title }} Analysis (Score: {{ analyzer_result.score }})

### Findings

| Check | Status | Message | Recommendation |
|-------|--------|---------|---------------|
{% for finding in analyzer_result.findings %}
| {{ finding.type }} | {{ finding.status|upper }} | {{ finding.message }} | {{ finding.recommendation }} |
{% endfor %}

{% endfor %}

Powered by Summit SEO
```

### Template Locations

Summit SEO looks for templates in these locations (in order):

1. Path specified in configuration
2. `~/.summit-seo/templates/`
3. Built-in templates directory

## Scoring Algorithms

You can customize how scores are calculated for different analyzers.

### Customizing Weights

Define custom weights for different checks to prioritize certain aspects:

```json
{
  "analysis": {
    "security": {
      "weights": {
        "https": 30,
        "cookies": 20,
        "xss": 25,
        "headers": 15,
        "sensitive_data": 10
      }
    },
    "performance": {
      "weights": {
        "page_speed": 40,
        "resource_size": 20,
        "caching": 15,
        "compression": 15,
        "render_blocking": 10
      }
    }
  }
}
```

### Custom Severity Levels

Define how much each severity level affects the score:

```json
{
  "analysis": {
    "score_impact": {
      "critical": -40,
      "high": -20,
      "medium": -10,
      "low": -5,
      "info": 0
    }
  }
}
```

### Score Normalization

Control how scores are normalized:

```json
{
  "analysis": {
    "score_normalization": {
      "min_score": 0,
      "max_score": 100,
      "pass_threshold": 70
    }
  }
}
```

## Integration with External Systems

Summit SEO can be integrated with various external systems for enhanced functionality.

### Webhooks

Configure webhooks to send results to external systems:

```json
{
  "webhooks": {
    "enabled": true,
    "endpoints": [
      {
        "url": "https://myapp.example.com/webhooks/seo-results",
        "method": "POST",
        "format": "json",
        "headers": {
          "Authorization": "Bearer my-api-key",
          "Content-Type": "application/json"
        }
      }
    ],
    "events": ["analysis_complete", "error"]
  }
}
```

### Database Integration

Configure database storage for analysis results:

```json
{
  "storage": {
    "type": "database",
    "driver": "sqlite",
    "path": "~/.summit-seo/results.db"
  }
}
```

Or for a remote database:

```json
{
  "storage": {
    "type": "database",
    "driver": "postgresql",
    "host": "db.example.com",
    "port": 5432,
    "database": "seo_results",
    "username": "seo_user",
    "password": "seo_password",
    "ssl": true
  }
}
```

### API Integration

Configure API integration for external data:

```json
{
  "api_integrations": {
    "google_pagespeed": {
      "enabled": true,
      "api_key": "your-api-key"
    },
    "lighthouse": {
      "enabled": true
    },
    "google_search_console": {
      "enabled": true,
      "credentials_file": "~/.summit-seo/google-credentials.json"
    }
  }
}
```

## Custom Rules and Thresholds

Define custom rules and thresholds for various analyzers.

### Performance Rules

```json
{
  "analysis": {
    "performance": {
      "rules": {
        "page_load_time": {
          "fast": 1500,
          "average": 3000,
          "slow": 5000
        },
        "resource_size": {
          "images": 200000,
          "scripts": 100000,
          "styles": 50000,
          "fonts": 150000
        },
        "requests": {
          "max_total": 50,
          "max_per_domain": 20
        }
      }
    }
  }
}
```

### Accessibility Rules

```json
{
  "analysis": {
    "accessibility": {
      "rules": {
        "contrast_ratio": 4.5,
        "font_size_minimum": 12,
        "require_alt_text": true,
        "require_aria_labels": true,
        "check_keyboard_navigation": true
      },
      "wcag_level": "AA"
    }
  }
}
```

### Security Rules

```json
{
  "analysis": {
    "security": {
      "rules": {
        "required_headers": [
          "Strict-Transport-Security",
          "X-Content-Type-Options",
          "X-Frame-Options",
          "Content-Security-Policy"
        ],
        "cookie_flags": {
          "require_secure": true,
          "require_http_only": true,
          "require_same_site": "Lax"
        },
        "sensitive_patterns": [
          "\\b(?:\\d[ -]*?){13,16}\\b",
          "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}\\b"
        ]
      }
    }
  }
}
```

## Custom CSS for Reports

Create custom CSS to style your HTML reports:

```json
{
  "reporting": {
    "html": {
      "custom_css_path": "~/my-seo-styles.css",
      "inline_css": true
    }
  }
}
```

Alternatively, include CSS directly in the configuration:

```json
{
  "reporting": {
    "html": {
      "custom_css": "
        body { font-family: 'Roboto', sans-serif; }
        .score-gauge { background-color: #3498db; }
        .pass { background-color: #2ecc71; }
        .fail { background-color: #e74c3c; }
        .warning { background-color: #f39c12; }
      "
    }
  }
}
```

## White Labeling

Customize reports to use your own branding:

```json
{
  "white_label": {
    "enabled": true,
    "company_name": "Your Company",
    "logo_path": "~/company-logo.png",
    "primary_color": "#3498db",
    "secondary_color": "#2c3e50",
    "contact_info": "For more information, contact support@yourcompany.com",
    "report_title": "{company} SEO Analysis for {url}",
    "copyright_text": "© {year} {company}. All rights reserved."
  }
}
```

## Internationalization

Configure internationalization options:

```json
{
  "i18n": {
    "language": "fr",
    "fallback_language": "en",
    "custom_translations_path": "~/my-translations.json"
  }
}
```

Custom translations file example:

```json
{
  "fr": {
    "overall_score": "Score Global",
    "security": "Sécurité",
    "performance": "Performance",
    "accessibility": "Accessibilité",
    "pass": "Réussite",
    "fail": "Échec",
    "warning": "Avertissement",
    "high": "Élevé",
    "medium": "Moyen",
    "low": "Faible"
  }
}
```

## Custom Data Sources

Define custom data sources for analysis:

```json
{
  "data_sources": {
    "custom_headers": {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "Accept-Language": "en-US,en;q=0.9"
    },
    "proxy": {
      "enabled": true,
      "url": "http://proxy.example.com:8080",
      "username": "proxy_user",
      "password": "proxy_password"
    },
    "authentication": {
      "type": "basic",
      "username": "site_user",
      "password": "site_password"
    },
    "cookies": {
      "session_id": "abc123",
      "user_preferences": "theme=dark"
    }
  }
}
```

## Advanced Customization

For advanced customization beyond configuration options, you can use Python functions.

### Custom Function Modules

Create a Python module with custom functions:

```python
# my_custom_functions.py

def custom_score_calculator(results, analyzer_name):
    """Custom scoring algorithm implementation"""
    # Custom logic here
    base_score = 100
    
    for finding in results.get('findings', []):
        if finding['status'] == 'fail':
            if finding.get('severity') == 'critical':
                base_score -= 25
            elif finding.get('severity') == 'high':
                base_score -= 15
            else:
                base_score -= 10
                
    return max(0, min(100, base_score))

def custom_html_preprocessor(html_content):
    """Preprocess HTML before analysis"""
    # Custom preprocessing logic
    import re
    
    # Remove comments
    html_content = re.sub('<!--.*?-->', '', html_content, flags=re.DOTALL)
    
    # Other preprocessing
    return html_content

def custom_report_postprocessor(report_content, format):
    """Postprocess report content"""
    # Custom postprocessing logic
    if format == 'html':
        report_content = report_content.replace(
            '<footer>Powered by Summit SEO</footer>',
            '<footer>Customized SEO Report</footer>'
        )
    
    return report_content
```

Reference these in your configuration:

```json
{
  "extensions": {
    "module_paths": ["~/my_custom_functions.py"],
    "scoring": {
      "security": "my_custom_functions.custom_score_calculator"
    },
    "preprocessing": {
      "html": "my_custom_functions.custom_html_preprocessor"
    },
    "postprocessing": {
      "report": "my_custom_functions.custom_report_postprocessor"
    }
  }
}
```

### Using Configuration Files with Environment-Specific Values

Create configuration files for different environments:

```
~/.summit-seo/
├── config/
│   ├── default.json
│   ├── development.json
│   ├── staging.json
│   └── production.json
```

Then specify which environment to use:

```bash
summit-seo analyze --url https://example.com --environment production
```

Or with an environment variable:

```bash
export SUMMIT_SEO_ENVIRONMENT=production
summit-seo analyze --url https://example.com
```

### Creating Custom Profiles

Define profiles for common use cases:

```json
{
  "profiles": {
    "quick_scan": {
      "max_pages": 5,
      "max_depth": 1,
      "analyzers": ["security", "performance"]
    },
    "security_audit": {
      "analyzers": ["security"],
      "security": {
        "check_xss": true,
        "check_csrf": true,
        "check_headers": true,
        "check_outdated_libraries": true
      }
    },
    "full_analysis": {
      "max_pages": 100,
      "max_depth": 3,
      "analyzers": ["all"]
    }
  }
}
```

Use these profiles from the command line:

```bash
summit-seo analyze --url https://example.com --profile security_audit
```

### Customizing the Analysis Pipeline

Customize the order and execution of the analysis pipeline:

```json
{
  "pipeline": {
    "stages": [
      {
        "name": "collection",
        "parallel": true,
        "max_workers": 4
      },
      {
        "name": "preprocessing",
        "handlers": ["html_preprocessor", "link_extractor"]
      },
      {
        "name": "analysis",
        "parallel": true,
        "max_workers": 8,
        "order": ["security", "performance", "accessibility", "schema", "mobile", "social"]
      },
      {
        "name": "reporting",
        "handlers": ["summary_generator", "chart_generator", "report_builder"]
      }
    ]
  }
}
```

This allows you to customize the execution flow without writing code. 