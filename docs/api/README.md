# Summit SEO API Documentation

This directory contains comprehensive documentation for all public APIs in the Summit SEO project. The documentation is organized by component type and includes usage examples, parameter descriptions, return value specifications, and exception details.

## Documentation Structure

- **Core Components**
  - [Analyzers](analyzers.md): Documentation for all analyzer components and the analyzer factory
  - [Collectors](collectors.md): Documentation for all collector components and the collector factory
  - [Processors](processors.md): Documentation for all processor components and the processor factory
  - [Reporters](reporters.md): Documentation for all reporter components and the reporter factory

- **Support Components**
  - [Visualization](visualization.md): Documentation for visualization components
  - [Progress Tracking](progress.md): Documentation for progress tracking components
  - [Caching](caching.md): Documentation for caching mechanisms
  - [Parallel Processing](parallel.md): Documentation for parallel processing capabilities
  - [Error Handling](error_handling.md): Documentation for error handling utilities

## Documentation Format

Each API documentation file follows a consistent format:

1. **Overview**: Brief description of the component and its purpose
2. **Class Hierarchy**: Inheritance structure when applicable
3. **Public Classes**: Detailed documentation for each public class
   - Constructor parameters
   - Public methods with parameters and return values
   - Properties and attributes
   - Exceptions that may be raised
4. **Usage Examples**: Code examples demonstrating typical usage patterns
5. **Extension Points**: Information on how to extend or customize the component

## Versioning

API documentation is versioned to match the Summit SEO package version. The current documentation applies to version `0.3.0` and later. 