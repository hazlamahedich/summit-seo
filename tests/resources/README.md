# Test Resources

This directory contains files and resources used for testing the Summit SEO framework components.

## Contents

- `sample.html` - A sample HTML file with various elements for testing the HTML processor, Content Analyzer, and integration tests.
- `logo.png` - A sample logo image for testing the PDF Reporter with logo integration.

## Usage

These files are referenced by test cases in various test modules:

- Unit tests: Test individual components with controlled inputs
- Integration tests: Test the interaction between multiple components
- End-to-end tests: Test the complete workflow from processing to analysis to reporting

## Adding New Resources

When adding new test resources:

1. Place the file in this directory with a descriptive name
2. Update this README.md to document the new resource
3. Make sure the file is appropriately sized for testing (avoid large files)
4. If the file contains test data, document the key elements or scenarios it's designed to test 