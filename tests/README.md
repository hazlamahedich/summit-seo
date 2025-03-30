# Summit SEO Testing Framework

This directory contains the automated testing framework for the Summit SEO project.

## Structure

- `analyzer/` - Tests for analyzer components
- `collector/` - Tests for collector components  
- `processor/` - Tests for processor components
- `reporter/` - Tests for reporter components
- `integration/` - Integration tests between components
- `resources/` - Test resources and sample files
- `conftest.py` - Pytest fixtures and configuration
- `run_all_tests.py` - Test runner script

## Running Tests

The easiest way to run all tests is to use the test runner:

```bash
python tests/run_all_tests.py
```

### Options

- `-m/--module MODULE` - Run tests for a specific module (e.g., analyzer, processor)
- `-t/--test TEST` - Run a specific test file or test case
- `-k/--keyword KEYWORD` - Only run tests matching the keyword
- `-v/--verbose` - Increase output verbosity
- `--no-coverage` - Run tests without coverage
- `--html-report` - Generate HTML coverage report
- `--xml-report` - Generate XML coverage report
- `--fail-under PERCENTAGE` - Fail if coverage is under threshold (default: 80%)

### Examples

Run all tests with default options:
```bash
python tests/run_all_tests.py
```

Run only processor tests:
```bash
python tests/run_all_tests.py -m processor
```

Run a specific test file:
```bash
python tests/run_all_tests.py -t test_content_analyzer
```

Run tests matching a keyword with verbose output:
```bash
python tests/run_all_tests.py -k "sitemap" -v
```

Generate HTML coverage report:
```bash
python tests/run_all_tests.py --html-report
```

## Writing Tests

### Test Naming Conventions

- Test files should be named `test_*.py`
- Test classes should be named `Test*`
- Test methods should be named `test_*`

### Using Fixtures

Common fixtures are defined in `conftest.py`:

```python
def test_example(sample_html_soup):
    # Use the sample_html_soup fixture
    assert sample_html_soup.title.string == "Test Page"
```

### Marking Tests

Use pytest markers to categorize tests:

```python
@pytest.mark.slow
def test_slow_operation():
    # This test is marked as slow
    pass

@pytest.mark.integration
def test_integration():
    # This test is marked as an integration test
    pass
```

### Testing Async Functions

For testing async functions, use the `pytest.mark.asyncio` decorator:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected_value
```

## Adding Test Resources

Test resources should be placed in the appropriate subdirectory under the `resources/` directory:

- Analyzer test resources: `resources/analyzer/`
- Processor test resources: `resources/processor/`
- Reporter test resources: `resources/reporter/`

## Continuous Integration

Tests are automatically run on GitHub Actions when:
- Pushing to main or development branches
- Creating a pull request to main or development branches

The CI pipeline:
1. Runs all tests with coverage reporting
2. Uploads coverage reports as artifacts
3. Reports coverage to Codecov 