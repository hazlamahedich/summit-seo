# Configuration Management

This document describes the configuration management system in Summit SEO, detailing how components can be configured and how configuration options are processed.

## Overview

The Summit SEO configuration system provides a flexible way to customize the behavior of all components. It follows a hierarchical approach with configuration options cascading from system-wide defaults to component-specific settings.

## Configuration Structure

Configuration in Summit SEO is managed through nested dictionaries:

```python
config = {
    "system": {
        "cache_enabled": True,
        "parallel_processing": True,
        "max_workers": 4,
        "timeout": 30,
        "log_level": "INFO"
    },
    "collector": {
        "rate_limit": 1.0,  # requests per second
        "user_agent": "Summit SEO Analyzer/1.0",
        "timeout": 10,
        "verify_ssl": True,
        "max_retries": 3,
        "retry_delay": 2,
        "follow_redirects": True,
        "max_redirects": 5
    },
    "processor": {
        "extract_metadata": True,
        "analyze_images": True,
        "process_javascript": True,
        "process_css": True,
        "detect_schema": True,
        "include_raw_html": False
    },
    "analyzer": {
        "content": {
            "min_word_count": 300,
            "keyword_density_threshold": 0.02,
            "readability_algorithm": "flesch_kincaid",
            "analyze_headings": True,
            "analyze_images": True,
            "analyze_links": True
        },
        "meta": {
            "required_meta_tags": ["title", "description"],
            "title_length_range": [30, 60],
            "description_length_range": [120, 160],
            "detect_keywords": True
        },
        "security": {
            "check_https": True,
            "check_mixed_content": True,
            "check_cookies": True,
            "check_csp": True,
            "check_xss": True,
            "check_dependencies": True,
            "check_sensitive_data": True
        }
    },
    "reporter": {
        "include_summary": True,
        "include_details": True,
        "include_recommendations": True,
        "include_visualizations": True,
        "sort_by_severity": True,
        "output_format": "json",
        "output_path": "./reports/"
    }
}
```

## Configuration Inheritance

Configuration follows an inheritance model where more specific settings override general ones:

1. **System defaults**: Hardcoded defaults in the system
2. **Global configuration**: User-provided system-wide configuration
3. **Component-type configuration**: Configuration for a specific component type (e.g., all analyzers)
4. **Component-specific configuration**: Configuration for a specific component (e.g., SecurityAnalyzer)
5. **Method-level overrides**: Configuration passed to specific method calls

## Loading Configuration

Configuration can be loaded from various sources:

```python
# Load from file
config = Config.from_file("config.json")

# Load from dictionary
config = Config.from_dict({
    "system": {"cache_enabled": True},
    "analyzer": {"security": {"check_https": True}}
})

# Load from environment variables
config = Config.from_env("SUMMIT_SEO_")
# Environment variables like SUMMIT_SEO_SYSTEM_CACHE_ENABLED=1
```

## Configuration Validation

Each component validates its configuration during initialization:

```python
class BaseComponent:
    def __init__(self, config=None):
        self.config = config or {}
        self._validate_config()
        self._apply_defaults()
        
    def _validate_config(self):
        # Implementation depends on the specific component
        pass
        
    def _apply_defaults(self):
        # Apply default values for missing configuration options
        pass
```

## Configuration Schema

Each component defines a configuration schema:

```python
class SecurityAnalyzer(BaseAnalyzer):
    CONFIG_SCHEMA = {
        "check_https": {"type": "bool", "default": True},
        "check_mixed_content": {"type": "bool", "default": True},
        "check_cookies": {"type": "bool", "default": True},
        "check_csp": {"type": "bool", "default": True},
        "check_xss": {"type": "bool", "default": True},
        "check_dependencies": {"type": "bool", "default": True},
        "check_sensitive_data": {"type": "bool", "default": True},
        "severity_weights": {
            "type": "dict",
            "default": {
                "critical": 30,
                "high": 15,
                "medium": 7,
                "low": 3,
                "info": 0
            }
        }
    }
```

## Dynamic Configuration

Summit SEO supports dynamic configuration updates:

```python
# Update configuration at runtime
analyzer.update_config({
    "check_xss": False,
    "severity_weights": {"critical": 40}
})
```

## Configuration Profiles

Predefined configuration profiles are available for common use cases:

```python
# Load a predefined profile
config = Config.load_profile("performance")

# Available profiles
profiles = {
    "basic": {
        "system": {"parallel_processing": False},
        "collector": {"rate_limit": 0.5},
        "analyzer": {"content": {"analyze_images": False}}
    },
    "comprehensive": {
        "system": {"parallel_processing": True, "max_workers": 8},
        "collector": {"rate_limit": 2.0},
        "analyzer": {"content": {"analyze_images": True}}
    },
    "performance": {
        "system": {"cache_enabled": True},
        "analyzer": {"security": {"check_dependencies": False}}
    }
}
```

## Environment-Specific Configuration

Different configurations can be applied based on the environment:

```python
# Load environment-specific configuration
env = os.getenv("SUMMIT_SEO_ENV", "development")
config = Config.from_file(f"config.{env}.json")
```

## Configuration Serialization

Configurations can be serialized for persistence:

```python
# Save configuration to file
config.to_file("config.json")

# Convert configuration to dictionary
config_dict = config.to_dict()

# Create environment variables from configuration
env_vars = config.to_env_vars("SUMMIT_SEO_")
```

## Configuration Command-Line Interface

Summit SEO provides a CLI for configuration management:

```bash
# Generate a default configuration file
summit-seo config generate --output config.json

# Validate a configuration file
summit-seo config validate --file config.json

# Show the effective configuration for a component
summit-seo config show --component analyzer.security
```

## Configuration Best Practices

1. **Use the configuration system instead of hardcoded values**
2. **Provide sensible defaults for all options**
3. **Validate configuration during component initialization**
4. **Document all configuration options with descriptions and valid values**
5. **Use the hierarchical nature of configuration for organization**
6. **Allow for easy overrides at various levels**
7. **Provide predefined profiles for common use cases**

## Example: Configuring a Security Analysis

```python
from summit_seo.config import Config
from summit_seo.analyzers import AnalyzerFactory

# Create configuration
config = {
    "system": {
        "cache_enabled": True,
        "parallel_processing": True
    },
    "analyzer": {
        "security": {
            "check_https": True,
            "check_mixed_content": True,
            "check_cookies": True,
            "check_csp": True,
            "check_xss": False,  # Disable XSS checking
            "check_dependencies": False,  # Disable dependency checking
            "check_sensitive_data": True,
            "severity_weights": {
                "critical": 40,  # Increase weight of critical findings
                "high": 20,
                "medium": 10,
                "low": 3,
                "info": 0
            }
        }
    }
}

# Create analyzer with configuration
analyzer = AnalyzerFactory.create("security", config=config["analyzer"]["security"])

# Run analysis
result = analyzer.analyze(data)
```

## Example: Environment-Specific Configuration

```python
import os
from summit_seo.config import Config

# Determine environment
env = os.getenv("SUMMIT_SEO_ENV", "development")

# Load base configuration
base_config = Config.from_file("config.base.json")

# Load environment-specific configuration
env_config = Config.from_file(f"config.{env}.json")

# Merge configurations
config = base_config.merge(env_config)

# Use configuration
analyzer = AnalyzerFactory.create("security", config=config["analyzer"]["security"])
```

This document provides a comprehensive overview of the configuration management system in Summit SEO, detailing how components can be configured and how configuration options are processed. 