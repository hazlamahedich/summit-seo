# Docstring Conventions

Summit SEO uses Google-style docstrings for documenting code. This guide explains the conventions to be followed when writing docstrings in the project.

## Google Style Docstrings

Google-style docstrings consist of a summary line, followed by an optional extended description, followed by sections. Each section has a header line followed by a list of parameters, return values, raised exceptions, etc.

## Basic Format

```python
"""Summary line.

Extended description of function.

Args:
    param1 (type): Description of param1.
    param2 (type): Description of param2.

Returns:
    type: Description of return value.

Raises:
    ExceptionType: When and why this exception is raised.

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting.

    >>> function_name(param1, param2)
    result
"""
```

## Class Docstrings

Class docstrings should contain information about the class and its attributes.

```python
class ExampleClass:
    """Summary of class here.

    Longer class information...
    Longer class information...

    Attributes:
        attr1 (type): Description of attr1.
        attr2 (type): Description of attr2.
    """

    def __init__(self, param1, param2):
        """Example of docstring on the __init__ method.

        Args:
            param1 (type): Description of param1.
            param2 (type): Description of param2.
        """
        self.attr1 = param1
        self.attr2 = param2
```

## Method Docstrings

Method docstrings should describe what the method does, its parameters, return values, and any exceptions it may raise.

```python
def function_with_types_in_docstring(param1, param2):
    """Example function with types documented in the docstring.
    
    PEP 484 type annotations are supported. If used, the parameter types
    should be omitted from the docstring.
    
    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.
    
    Returns:
        bool: The return value. True for success, False otherwise.
    
    Raises:
        ValueError: If param1 is equal to param2.
    """
    if param1 == param2:
        raise ValueError('param1 may not be equal to param2')
    return True
```

## Type Annotations

When using type annotations (PEP 484), the types should be omitted from the docstring:

```python
def function_with_pep484_type_annotations(param1: int, param2: str) -> bool:
    """Example function with PEP 484 type annotations.
    
    Args:
        param1: The first parameter.
        param2: The second parameter.
    
    Returns:
        The return value. True for success, False otherwise.
    
    Raises:
        ValueError: If param1 is equal to param2.
    """
    if param1 == param2:
        raise ValueError('param1 may not be equal to param2')
    return True
```

## Property Docstrings

For properties, document them as attributes in the class docstring and add a short docstring to the property.

```python
class ExampleClass:
    """Class with properties.
    
    Attributes:
        property_name (type): Description of the property.
    """
    
    @property
    def property_name(self) -> type:
        """Short description of the property.
        
        Longer description if necessary.
        
        Returns:
            type: Description of the return value.
        """
        return self._property_name
```

## Module Docstrings

Module docstrings appear at the top of the file and explain the purpose of the module.

```python
"""Module for handling all analyzer components.

This module provides functionality for analyzing SEO aspects of web pages,
including title tags, meta descriptions, content quality, etc.

Typical usage example:
  analyzer = TitleAnalyzer()
  result = await analyzer.analyze(data)
  print(f"Score: {result.score}")
"""
```

## Sections In Docstrings

Commonly used sections in docstrings:

- **Args**: List of parameters and their descriptions
- **Returns**: Description of the return value and its type
- **Raises**: List of exceptions that can be raised and when
- **Example/Examples**: Code examples showing how to use the function/class
- **Note**: Additional notes or caveats about implementation
- **Attributes**: For class docstrings, list of attributes
- **Warnings**: Warnings about using the function/class

## Examples from Summit SEO

### BaseAnalyzer

```python
class BaseAnalyzer(ABC, Generic[InputType, OutputType]):
    """Abstract base class for SEO analyzers.
    
    This class defines the interface that all SEO analyzers must implement.
    It provides a common structure for analyzing different aspects of SEO
    and generating standardized results.
    
    Attributes:
        config (Dict[str, Any]): Configuration dictionary for customizing analyzer behavior.
        error_type (Type[Exception]): Exception type raised by this analyzer.
        enable_caching (bool): Whether caching is enabled.
        cache_ttl (int): Time-to-live for cached results in seconds.
        cache_type (str): Type of cache to use.
        cache_namespace (str): Namespace for cache entries.
        recommendation_manager (RecommendationManager): Manager for recommendations.
    """
```

### Analysis Method

```python
async def analyze(self, data: InputType) -> AnalysisResult[OutputType]:
    """Analyze the input data and return results.
    
    This implementation checks the cache first, and only performs analysis
    if the result is not found in cache or if caching is disabled.
    
    Args:
        data: Input data to analyze
        
    Returns:
        AnalysisResult containing the analysis output
        
    Raises:
        AnalyzerError: If analysis fails
    """
```

## Best Practices

1. **Be Concise**: Keep summary lines short and to the point.
2. **Be Descriptive**: Give enough information to understand what the function does.
3. **Be Consistent**: Follow the same style throughout the codebase.
4. **Include Types**: Always include parameter and return types.
5. **Document Exceptions**: Document all exceptions that might be raised.
6. **Include Examples**: Provide examples for complex functions.
7. **Document Side Effects**: Document any side effects or state changes.
8. **Update When Code Changes**: Keep docstrings up to date with code changes.

## Tools for Documentation

Summit SEO uses the following tools for documentation:

- **pydocstyle**: For checking docstring style
- **sphinx**: For generating HTML documentation from docstrings
- **sphinx-rtd-theme**: For a nice looking theme
- **napoleon**: Sphinx extension for Google style docstrings

## Linting and Validation

In our CI/CD pipeline, docstrings are validated using:

```bash
pydocstyle --convention=google summit_seo
```

This ensures all docstrings follow the Google style guide. 