"""Tests for the Schema Analyzer."""

import pytest
from bs4 import BeautifulSoup
from summit_seo.analyzer.schema_analyzer import SchemaAnalyzer

# Sample HTML with valid JSON-LD schema
VALID_JSONLD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Schema.org Test Page</title>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Test Article",
        "author": {
            "@type": "Person",
            "name": "John Doe"
        },
        "datePublished": "2023-01-01T08:00:00+08:00",
        "dateModified": "2023-01-02T09:00:00+08:00",
        "publisher": {
            "@type": "Organization",
            "name": "Test Publisher",
            "logo": {
                "@type": "ImageObject",
                "url": "https://example.com/logo.png"
            }
        },
        "image": "https://example.com/article-image.jpg",
        "description": "This is a test article with schema.org markup."
    }
    </script>
</head>
<body>
    <h1>Schema.org Test Page</h1>
    <p>This page contains valid schema.org markup.</p>
</body>
</html>
"""

# Sample HTML with invalid JSON-LD schema (missing required properties)
INVALID_JSONLD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Schema.org Test Page</title>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Test Article"
    }
    </script>
</head>
<body>
    <h1>Schema.org Test Page</h1>
    <p>This page contains schema.org markup with missing required properties.</p>
</body>
</html>
"""

# Sample HTML with multiple JSON-LD schemas
MULTIPLE_JSONLD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Schema.org Test Page</title>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Test Article",
        "author": {
            "@type": "Person",
            "name": "John Doe"
        },
        "datePublished": "2023-01-01T08:00:00+08:00"
    }
    </script>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "Test Product",
        "offers": {
            "@type": "Offer",
            "price": "19.99",
            "priceCurrency": "USD"
        }
    }
    </script>
</head>
<body>
    <h1>Schema.org Test Page</h1>
    <p>This page contains multiple schema.org markup blocks.</p>
</body>
</html>
"""

# Sample HTML with no schema markup
NO_SCHEMA_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Schema.org Test Page</title>
</head>
<body>
    <h1>Schema.org Test Page</h1>
    <p>This page contains no schema.org markup.</p>
</body>
</html>
"""

# Sample HTML with invalid JSON (syntax error)
SYNTAX_ERROR_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Schema.org Test Page</title>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Test Article",
        "author": {
            "@type": "Person",
            "name": "John Doe"
        },
        "datePublished": "2023-01-01T08:00:00+08:00",
        missing_quotes: "This will cause a syntax error"
    }
    </script>
</head>
<body>
    <h1>Schema.org Test Page</h1>
    <p>This page contains schema.org markup with a JSON syntax error.</p>
</body>
</html>
"""

@pytest.fixture
def schema_analyzer():
    """Create a schema analyzer instance."""
    return SchemaAnalyzer()

def test_analyze_valid_jsonld(schema_analyzer):
    """Test analyzing a page with valid JSON-LD schema."""
    result = schema_analyzer.analyze(VALID_JSONLD_HTML)
    
    # Check basic results
    assert result.score > 0.7
    assert result.data['has_schema_markup'] is True
    assert result.data['schema_score'] >= 70
    
    # Check format detection
    assert 'JSON-LD' in result.data['detected_formats']
    assert result.data['jsonld_count'] == 1
    
    # Check type detection
    assert 'Article' in result.data['detected_types']
    assert 'Person' in result.data['detected_types']
    assert 'Organization' in result.data['detected_types']
    
    # Check issue counts
    assert result.data['critical_severity_issues'] == 0
    assert result.data['high_severity_issues'] == 0
    
    # Verify schema issues array exists
    assert 'schema_issues' in result.data
    assert isinstance(result.data['schema_issues'], list)

def test_analyze_invalid_jsonld(schema_analyzer):
    """Test analyzing a page with invalid JSON-LD schema (missing required properties)."""
    result = schema_analyzer.analyze(INVALID_JSONLD_HTML)
    
    # Check basic results
    assert result.score < 0.7
    assert result.data['has_schema_markup'] is True
    assert result.data['schema_score'] < 70
    
    # Check format detection
    assert 'JSON-LD' in result.data['detected_formats']
    assert result.data['jsonld_count'] == 1
    
    # Check type detection
    assert 'Article' in result.data['detected_types']
    
    # Check issue counts - should have high severity issues for missing required props
    assert result.data['high_severity_issues'] > 0
    
    # Check specific issues
    has_missing_props_issue = any(
        issue['name'] == 'Missing Required Properties' 
        for issue in result.data['schema_issues']
    )
    assert has_missing_props_issue
    
    # Check recommendations
    assert len(result.recommendations) > 0
    has_props_recommendation = any(
        'required properties' in rec.lower() 
        for rec in result.recommendations
    )
    assert has_props_recommendation

def test_analyze_multiple_jsonld(schema_analyzer):
    """Test analyzing a page with multiple JSON-LD schemas."""
    result = schema_analyzer.analyze(MULTIPLE_JSONLD_HTML)
    
    # Check basic results
    assert result.data['has_schema_markup'] is True
    
    # Check format detection
    assert 'JSON-LD' in result.data['detected_formats']
    assert result.data['jsonld_count'] == 2
    
    # Check type detection
    assert 'Article' in result.data['detected_types']
    assert 'Product' in result.data['detected_types']
    assert 'Person' in result.data['detected_types']
    assert 'Offer' in result.data['detected_types']
    
    # Check total schema items
    assert result.data['total_schema_items'] == 2

def test_analyze_no_schema(schema_analyzer):
    """Test analyzing a page with no schema markup."""
    result = schema_analyzer.analyze(NO_SCHEMA_HTML)
    
    # Check basic results
    assert result.data['has_schema_markup'] is False
    assert result.data['jsonld_count'] == 0
    assert result.data['microdata_count'] == 0
    assert result.data['rdfa_count'] == 0
    
    # Check empty detection
    assert len(result.data['detected_formats']) == 0
    assert len(result.data['detected_types']) == 0
    
    # Should have warnings about missing schema
    assert len(result.warnings) > 0
    has_no_schema_warning = any(
        'no schema.org structured data found' in warning.lower() 
        for warning in result.warnings
    )
    assert has_no_schema_warning
    
    # Should have recommendations for adding schema
    assert len(result.recommendations) > 0
    has_implementation_recommendation = any(
        'add schema.org structured data' in rec.lower() 
        for rec in result.recommendations
    )
    assert has_implementation_recommendation

def test_analyze_syntax_error(schema_analyzer):
    """Test analyzing a page with a JSON syntax error in schema markup."""
    result = schema_analyzer.analyze(SYNTAX_ERROR_HTML)
    
    # Check basic results
    assert result.data['has_schema_markup'] is False
    
    # Should have critical issues for invalid JSON
    assert result.data['critical_severity_issues'] > 0
    
    # Check specific issues
    has_invalid_json_issue = any(
        issue['name'] == 'Invalid JSON Format' 
        for issue in result.data['schema_issues']
    )
    assert has_invalid_json_issue
    
    # Check recommendations for fixing
    assert len(result.recommendations) > 0
    has_fix_json_recommendation = any(
        'fix invalid json-ld schema' in rec.lower() 
        for rec in result.recommendations
    )
    assert has_fix_json_recommendation

def test_disable_jsonld_checking(schema_analyzer):
    """Test disabling JSON-LD checking."""
    # Configure analyzer to disable JSON-LD checking
    schema_analyzer = SchemaAnalyzer({'check_jsonld': False})
    
    # Analyze a page with valid JSON-LD
    result = schema_analyzer.analyze(VALID_JSONLD_HTML)
    
    # JSON-LD should not be detected since checking is disabled
    assert result.data['has_schema_markup'] is False
    assert result.data['jsonld_count'] == 0
    assert 'JSON-LD' not in result.data['detected_formats']

def test_custom_property_requirements(schema_analyzer):
    """Test analyzer with custom property requirements."""
    # Configure analyzer with custom property requirements
    schema_analyzer = SchemaAnalyzer({
        'custom_property_requirements': {
            'Article': {
                'required': ['headline', 'author', 'datePublished', 'customRequiredProp'],
                'recommended': ['image', 'description']
            }
        }
    })
    
    # Analyze valid JSON-LD that's missing the custom required property
    result = schema_analyzer.analyze(VALID_JSONLD_HTML)
    
    # Should have high severity issue for missing custom required property
    assert result.data['high_severity_issues'] > 0
    
    # Check specific issues
    has_missing_custom_prop = any(
        'customRequiredProp' in issue['description']
        for issue in result.data['schema_issues']
    )
    assert has_missing_custom_prop 