# Creating a Custom Processor

This guide demonstrates how to create a custom processor by extending the `BaseProcessor` class. Processors in Summit SEO are responsible for transforming raw data (like HTML, CSS, or JavaScript) into structured formats suitable for analysis.

## Overview

Processors sit between collectors and analyzers in the Summit SEO pipeline:
1. **Collectors** retrieve raw data from web pages
2. **Processors** transform that data into structured formats
3. **Analyzers** analyze the processed data to provide SEO insights

By creating custom processors, you can handle special data formats or implement custom transformation logic for specific types of content.

## When to Create a Custom Processor

Consider creating a custom processor when:
- You need to process a specialized file format (e.g., PDFs, SVGs, or JSON-LD)
- You want to extract specific data structures from standard formats
- You need custom transformation logic for specific types of websites

## Step 1: Import Required Components

Start by importing the base processor classes and any required libraries:

```python
from typing import Dict, Any, List, Optional
import json
from summit_seo.processor.base import (
    BaseProcessor,
    ProcessingResult,
    ValidationError,
    TransformationError
)
```

## Step 2: Define Your Processor Class

Create a class that inherits from `BaseProcessor`:

```python
class JSONLDProcessor(BaseProcessor):
    """Processor for extracting and validating JSON-LD structured data."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the JSON-LD processor.
        
        Args:
            config: Optional configuration dictionary with settings:
                - validate_schema: Whether to validate against schema.org (default: True)
                - extract_types: List of schema types to extract (default: all)
                - normalize_urls: Whether to normalize URLs (default: True)
                - enable_caching: Whether to enable caching (default: True)
        """
        default_config = {
            'validate_schema': True,
            'extract_types': [],  # Empty list means extract all types
            'normalize_urls': True,
            'enable_caching': True,
            'cache_ttl': 3600,  # 1 hour default
        }
        
        # Merge provided config with defaults
        merged_config = {**default_config, **(config or {})}
        super().__init__(merged_config)
```

## Step 3: Implement Configuration Validation

Override the `_validate_config` method to validate your processor's specific configuration options:

```python
    def _validate_config(self) -> None:
        """Validate processor configuration."""
        # Validate boolean options
        bool_options = ['validate_schema', 'normalize_urls', 'enable_caching']
        for option in bool_options:
            if option in self.config and not isinstance(self.config[option], bool):
                raise ValidationError(f"{option} must be a boolean")
        
        # Validate extract_types
        if 'extract_types' in self.config:
            if not isinstance(self.config['extract_types'], list):
                raise ValidationError("extract_types must be a list")
            
            # Validate each type is a string
            for schema_type in self.config['extract_types']:
                if not isinstance(schema_type, str):
                    raise ValidationError("Each schema type in extract_types must be a string")
```

## Step 4: Define Required Input Fields

Implement the `_get_required_fields` method to specify what input fields your processor requires:

```python
    def _get_required_fields(self) -> List[str]:
        """Get list of required input fields.
        
        Returns:
            List of field names required in the input data
        """
        return ['html_content', 'url']
```

## Step 5: Implement the Core Processing Logic

Implement the `_process_data` method with your processor's transformation logic:

```python
    async def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and process JSON-LD structured data from HTML.
        
        Args:
            data: Dictionary containing HTML content and URL
            
        Returns:
            Dictionary with extracted and processed JSON-LD data
            
        Raises:
            TransformationError: If extraction or processing fails
        """
        try:
            # Extract HTML and URL from input data
            html_content = data['html_content']
            url = data['url']
            
            # Extract JSON-LD scripts from HTML
            json_ld_data = self._extract_json_ld(html_content)
            
            # Filter by schema type if configured
            if self.config['extract_types']:
                json_ld_data = self._filter_by_type(json_ld_data)
            
            # Normalize URLs if configured
            if self.config['normalize_urls']:
                json_ld_data = self._normalize_urls(json_ld_data, url)
            
            # Validate against schema.org if configured
            validation_results = {}
            if self.config['validate_schema']:
                validation_results = self._validate_schema(json_ld_data)
            
            # Prepare result
            result = {
                'structured_data': json_ld_data,
                'validation_results': validation_results,
                'structured_data_count': len(json_ld_data),
                'has_structured_data': len(json_ld_data) > 0
            }
            
            return result
            
        except json.JSONDecodeError as e:
            raise TransformationError(f"Invalid JSON-LD format: {str(e)}")
        except Exception as e:
            raise TransformationError(f"JSON-LD processing failed: {str(e)}")
```

## Step 6: Implement Helper Methods

Add helper methods to support your processor's functionality:

```python
    def _extract_json_ld(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract JSON-LD data from HTML content.
        
        Args:
            html_content: HTML content to extract JSON-LD from
            
        Returns:
            List of parsed JSON-LD objects
            
        Raises:
            TransformationError: If extraction fails
        """
        from bs4 import BeautifulSoup
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            
            result = []
            for script in json_ld_scripts:
                try:
                    # Parse JSON content
                    json_content = json.loads(script.string)
                    
                    # Handle both single objects and arrays of objects
                    if isinstance(json_content, list):
                        result.extend(json_content)
                    else:
                        result.append(json_content)
                except json.JSONDecodeError:
                    # Skip invalid JSON
                    continue
                    
            return result
            
        except Exception as e:
            raise TransformationError(f"Failed to extract JSON-LD: {str(e)}")
    
    def _filter_by_type(self, json_ld_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter JSON-LD data by schema type.
        
        Args:
            json_ld_data: List of JSON-LD objects
            
        Returns:
            Filtered list of JSON-LD objects
        """
        extract_types = self.config['extract_types']
        return [
            item for item in json_ld_data
            if '@type' in item and item['@type'] in extract_types
        ]
    
    def _normalize_urls(self, json_ld_data: List[Dict[str, Any]], base_url: str) -> List[Dict[str, Any]]:
        """Normalize URLs in JSON-LD data.
        
        Args:
            json_ld_data: List of JSON-LD objects
            base_url: Base URL for resolving relative URLs
            
        Returns:
            JSON-LD data with normalized URLs
        """
        from urllib.parse import urljoin, urlparse
        
        # Create a deep copy to avoid modifying the original
        import copy
        normalized_data = copy.deepcopy(json_ld_data)
        
        # URL property names that we want to normalize
        url_properties = ['url', 'image', 'contentUrl', 'thumbnailUrl', 'sameAs']
        
        for item in normalized_data:
            for prop in url_properties:
                # Handle string URLs
                if prop in item and isinstance(item[prop], str):
                    if not urlparse(item[prop]).netloc:  # If it's a relative URL
                        item[prop] = urljoin(base_url, item[prop])
                
                # Handle URL objects with @value
                elif prop in item and isinstance(item[prop], dict) and '@value' in item[prop]:
                    if not urlparse(item[prop]['@value']).netloc:
                        item[prop]['@value'] = urljoin(base_url, item[prop]['@value'])
                        
                # Handle arrays of URLs
                elif prop in item and isinstance(item[prop], list):
                    for i, url in enumerate(item[prop]):
                        if isinstance(url, str) and not urlparse(url).netloc:
                            item[prop][i] = urljoin(base_url, url)
        
        return normalized_data
    
    def _validate_schema(self, json_ld_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate JSON-LD data against schema.org vocabulary.
        
        Args:
            json_ld_data: List of JSON-LD objects
            
        Returns:
            Dictionary with validation results
        """
        # In a real implementation, you'd integrate with a JSON-LD validation library
        # This is a simplified version that checks for required properties
        validation_results = {
            'valid_count': 0,
            'invalid_count': 0,
            'errors': []
        }
        
        # Required properties for common schema types
        required_properties = {
            'Product': ['name', 'image'],
            'Article': ['headline', 'author'],
            'Organization': ['name'],
            'LocalBusiness': ['name', 'address'],
            'Person': ['name'],
            'Event': ['name', 'startDate'],
            'Recipe': ['name', 'recipeIngredient', 'recipeInstructions']
        }
        
        for item in json_ld_data:
            if '@type' not in item:
                validation_results['invalid_count'] += 1
                validation_results['errors'].append({
                    'type': 'unknown',
                    'message': 'Missing @type property'
                })
                continue
                
            schema_type = item['@type']
            
            # Skip validation for unknown types
            if schema_type not in required_properties:
                validation_results['valid_count'] += 1
                continue
                
            # Check required properties
            missing_props = [
                prop for prop in required_properties[schema_type]
                if prop not in item
            ]
            
            if missing_props:
                validation_results['invalid_count'] += 1
                validation_results['errors'].append({
                    'type': schema_type,
                    'message': f"Missing required properties: {', '.join(missing_props)}"
                })
            else:
                validation_results['valid_count'] += 1
                
        return validation_results
```

## Step 7: Register Your Processor with the Factory

Register your custom processor with the processor factory to make it available through the standard interface:

```python
from summit_seo import ProcessorFactory

# Register your custom processor
ProcessorFactory.register('jsonld', JSONLDProcessor)
```

## Step 8: Use Your Custom Processor

Now you can use your custom processor in your SEO analysis workflow:

```python
import asyncio
from summit_seo import ProcessorFactory

async def extract_structured_data():
    # Create the processor factory
    factory = ProcessorFactory()
    
    # Create your processor with custom configuration
    processor = factory.create('jsonld', {
        'extract_types': ['Product', 'Organization'],
        'validate_schema': True
    })
    
    # Prepare input data
    data = {
        'html_content': open('example_page.html', 'r').read(),
        'url': 'https://example.com/product-page'
    }
    
    # Process the data
    result = await processor.process(data, data['url'])
    
    # Access the processed data
    structured_data = result.processed_data.get('structured_data', [])
    validation_results = result.processed_data.get('validation_results', {})
    
    # Print results
    print(f"Found {len(structured_data)} structured data items")
    print(f"Valid: {validation_results.get('valid_count', 0)}")
    print(f"Invalid: {validation_results.get('invalid_count', 0)}")
    
    if validation_results.get('errors', []):
        print("\nValidation Errors:")
        for error in validation_results['errors']:
            print(f"- [{error['type']}] {error['message']}")
    
    # Print extracted structured data
    for i, item in enumerate(structured_data, 1):
        print(f"\nItem {i} (@type: {item.get('@type', 'Unknown')}):")
        if 'name' in item:
            print(f"Name: {item['name']}")
        if 'description' in item:
            print(f"Description: {item['description'][:100]}...")

    return result

# Run the processing
asyncio.run(extract_structured_data())
```

## Step 9: Process Multiple Items in Batch

For efficiency, you can process multiple items in batch:

```python
import asyncio
from summit_seo import ProcessorFactory

async def batch_process_structured_data():
    # Create the processor
    factory = ProcessorFactory()
    processor = factory.create('jsonld')
    
    # Prepare batch data
    batch_items = [
        {
            'data': {
                'html_content': open(f'page{i}.html', 'r').read(),
                'url': f'https://example.com/page{i}'
            },
            'url': f'https://example.com/page{i}'
        }
        for i in range(1, 4)  # Process 3 pages
    ]
    
    # Process batch
    results = await processor.process_batch(batch_items)
    
    # Print summary
    print(f"Processed {len(results)} pages")
    for i, result in enumerate(results, 1):
        print(f"\nPage {i} ({result.url}):")
        structured_data = result.processed_data.get('structured_data', [])
        print(f"Found {len(structured_data)} structured data items")
        
        # Print types of structured data found
        types = [item.get('@type', 'Unknown') for item in structured_data]
        if types:
            print(f"Types: {', '.join(types)}")
        
        # Print any errors
        if result.errors:
            print("Errors:")
            for error in result.errors:
                print(f"- {error}")
    
    return results

# Run batch processing
asyncio.run(batch_process_structured_data())
```

## Complete Example

The complete processor implementation is available as a gist:

https://gist.github.com/summit-seo/jsonld-processor-example

## Testing Your Custom Processor

Create a test file to verify your processor works correctly:

```python
import pytest
from summit_seo.processor import ProcessorFactory
from summit_seo.processor.base import ProcessingResult, TransformationError

# Register your custom processor for testing
from custom_processors import JSONLDProcessor
ProcessorFactory.register('jsonld', JSONLDProcessor)

@pytest.fixture
def processor():
    factory = ProcessorFactory()
    return factory.create('jsonld')

@pytest.fixture
def html_with_jsonld():
    return """
    <html>
    <head>
        <title>Test Page</title>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Example Product",
            "description": "This is an example product",
            "image": "/images/product.jpg",
            "offers": {
                "@type": "Offer",
                "price": "49.99",
                "priceCurrency": "USD"
            }
        }
        </script>
    </head>
    <body>
        <h1>Product Page</h1>
    </body>
    </html>
    """

@pytest.mark.asyncio
async def test_jsonld_processor(processor, html_with_jsonld):
    # Prepare test data
    data = {
        'html_content': html_with_jsonld,
        'url': 'https://example.com/product'
    }
    
    # Process the data
    result = await processor.process(data, data['url'])
    
    # Assertions
    assert isinstance(result, ProcessingResult)
    assert len(result.errors) == 0
    assert 'structured_data' in result.processed_data
    
    structured_data = result.processed_data['structured_data']
    assert len(structured_data) == 1
    
    product = structured_data[0]
    assert product['@type'] == 'Product'
    assert product['name'] == 'Example Product'
    
    # Check URL normalization
    assert product['image'] == 'https://example.com/images/product.jpg'

@pytest.mark.asyncio
async def test_invalid_html(processor):
    # Test with invalid HTML
    data = {
        'html_content': '<html><script type="application/ld+json">{invalid json}</script></html>',
        'url': 'https://example.com'
    }
    
    # Process should not raise an exception but return an empty result
    result = await processor.process(data, data['url'])
    
    assert len(result.processed_data.get('structured_data', [])) == 0
    assert len(result.errors) > 0
```

## Best Practices for Custom Processors

1. **Validate Input**: Always validate input data before processing
2. **Handle Errors Gracefully**: Catch exceptions and provide meaningful error messages
3. **Optimize for Performance**: Use efficient algorithms and data structures
4. **Support Batching**: Implement efficient batch processing when appropriate
5. **Make Configuration Flexible**: Allow users to customize behavior through configuration
6. **Return Structured Results**: Ensure your results are structured consistently

## Related Documentation

- [API Reference for BaseProcessor](../api/processors.md)
- [Processor Factory Documentation](../guide/factories.md)
- [Caching Mechanism](../guide/caching.md)
- [Custom Analyzer Creation](custom_analyzer.md)
- [Custom Reporter Creation](custom_reporter.md) 