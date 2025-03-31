# Summit SEO Developer Contribution Guide

This guide provides information for developers who want to contribute to the Summit SEO project. Whether you're fixing bugs, adding features, improving documentation, or suggesting enhancements, this guide will help you understand the contribution process.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Setting up the Development Environment](#setting-up-the-development-environment)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Documentation Guidelines](#documentation-guidelines)
7. [Pull Request Process](#pull-request-process)
8. [Review Process](#review-process)
9. [Issue Tracking](#issue-tracking)
10. [Release Process](#release-process)
11. [Community](#community)

## Code of Conduct

Summit SEO adheres to a Code of Conduct that all contributors are expected to follow. The full code is available in the repository's [CODE_OF_CONDUCT.md](https://github.com/summit-seo/summit-seo/blob/main/CODE_OF_CONDUCT.md) file. In summary:

- Be respectful and inclusive
- Focus on constructive feedback
- Be patient, especially with new contributors
- Maintain a harassment-free environment
- Prioritize the community's wellbeing

Violations of the code of conduct can be reported to the project maintainers.

## Setting up the Development Environment

### Prerequisites

- Python 3.8 or higher
- Git
- A GitHub account
- pip and virtualenv

### Fork and Clone the Repository

1. Fork the Summit SEO repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/summit-seo.git
   cd summit-seo
   ```

3. Add the upstream repository as a remote:
   ```bash
   git remote add upstream https://github.com/summit-seo/summit-seo.git
   ```

### Set Up Development Environment

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev,test,docs]"
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Verify Setup

1. Run the test suite:
   ```bash
   pytest
   ```

2. Build the documentation:
   ```bash
   cd docs
   make html
   ```

## Development Workflow

Summit SEO follows a GitHub flow development process:

1. **Sync with upstream**: Always ensure your local main branch is up-to-date
   ```bash
   git checkout main
   git pull upstream main
   ```

2. **Create a feature branch**: Create a new branch for your feature or bugfix
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

3. **Implement changes**: Make your changes in the feature branch

4. **Write tests**: Add or modify tests to cover your changes

5. **Local validation**: Run tests and linting locally
   ```bash
   pytest
   flake8
   pylint summit_seo
   ```

6. **Document your changes**: Update documentation as needed

7. **Commit changes**: Use meaningful commit messages
   ```bash
   git add .
   git commit -m "Add feature: detailed description of changes"
   ```

8. **Push to GitHub**:
   ```bash
   git push origin feature/your-feature-name
   ```

9. **Create a Pull Request**: Open a PR from your feature branch to the main repository

## Coding Standards

Summit SEO follows strict coding standards to ensure code quality and consistency.

### Python Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Follow [PEP 257](https://www.python.org/dev/peps/pep-0257/) for docstrings
- Use [Google style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Maximum line length is 100 characters
- Use 4 spaces for indentation (no tabs)
- Use snake_case for variables and function names
- Use CamelCase for class names
- Use UPPER_CASE for constants
- Add type hints for function parameters and return values

### Examples

#### Function Example

```python
def calculate_score(findings: List[Dict[str, Any]], weights: Dict[str, float] = None) -> float:
    """
    Calculate a weighted score based on analysis findings.
    
    Args:
        findings: List of finding dictionaries with 'status' and 'type' keys
        weights: Optional dictionary mapping finding types to weight values
        
    Returns:
        A score from 0.0 to 100.0 representing the weighted result
        
    Raises:
        ValueError: If findings contain invalid status values
    """
    if not findings:
        return 100.0
        
    weights = weights or {}
    default_weight = 1.0
    
    # Implementation here
    
    return max(0.0, min(100.0, final_score))
```

#### Class Example

```python
class SecurityAnalyzer(BaseAnalyzer):
    """
    Analyzer for security-related aspects of a website.
    
    This analyzer checks for security best practices including HTTPS
    implementation, secure cookies, content security policy, and more.
    
    Attributes:
        name: The analyzer name identifier
        description: Human-readable description of the analyzer
        version: Version string for the analyzer
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the SecurityAnalyzer.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self.name = "security"
        self.description = "Analyzes website security aspects"
        self.version = "1.0.0"
        
        # Initialize other properties
```

### Code Quality Tools

Summit SEO uses several automated tools to ensure code quality:

- **flake8**: For style guide enforcement
- **pylint**: For code quality analysis
- **mypy**: For static type checking
- **black**: For code formatting (optional but recommended)
- **isort**: For import sorting
- **pre-commit**: To run checks before committing

These tools are configured in the repository and run as part of the CI pipeline.

## Testing Guidelines

Summit SEO has a comprehensive test suite. New code should maintain or improve test coverage.

### Test Structure

Tests are organized by component type and reside in the `tests/` directory:

```
tests/
├── analyzers/
│   ├── test_security_analyzer.py
│   ├── test_performance_analyzer.py
│   └── ...
├── collectors/
├── processors/
├── reporters/
├── utils/
└── integration/
```

### Test Requirements

- All code should be covered by tests
- Use pytest for writing tests
- Each test should focus on a single functionality
- Use descriptive test names in the format `test_<function_name>_<scenario>`
- Isolate tests using appropriate fixtures and mocks
- Add tests for edge cases and error conditions

### Example Test

```python
import pytest
from summit_seo.analyzers import SecurityAnalyzer
from summit_seo.models import ProcessedData

@pytest.fixture
def security_analyzer():
    """Create a SecurityAnalyzer instance for testing."""
    return SecurityAnalyzer()

@pytest.fixture
def processed_data_https():
    """Create a processed data instance with HTTPS content."""
    return ProcessedData(
        data={
            "url": "https://example.com",
            "status_code": 200,
            "headers": {
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
            }
        },
        metadata={
            "protocol": "https",
            "domain": "example.com"
        }
    )

def test_analyze_https_valid(security_analyzer, processed_data_https):
    """Test HTTPS validation with a valid HTTPS site."""
    results = security_analyzer.analyze(processed_data_https)
    
    # Check findings structure
    assert "findings" in results
    
    # Find the HTTPS finding
    https_finding = next(
        (f for f in results["findings"] if f["type"] == "https"), None
    )
    
    # Assert finding details
    assert https_finding is not None
    assert https_finding["status"] == "pass"
    assert "HTTPS properly configured" in https_finding["message"]
    
    # Test score impact
    score = security_analyzer.compute_score(results)
    assert score == 100  # Perfect score for this case
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/analyzers/test_security_analyzer.py

# Run specific test
pytest tests/analyzers/test_security_analyzer.py::test_analyze_https_valid

# Run with coverage report
pytest --cov=summit_seo

# Export coverage report
pytest --cov=summit_seo --cov-report=xml
```

## Documentation Guidelines

Good documentation is crucial for the Summit SEO project. All code should be documented following these guidelines:

### Code Documentation

- Every module, class, method, and function should have a docstring
- Follow Google style docstrings format
- Document parameters, return values, exceptions, and examples
- Include type information in docstrings (in addition to type hints)
- Explain complex algorithms or design decisions in comments

### Project Documentation

Project documentation is built using Sphinx and is stored in the `docs/` directory:

- API reference documentation is generated from docstrings
- Tutorials and guides are written as standalone Markdown or reStructuredText files
- Examples should be tested to ensure they work correctly

### Writing Documentation

To contribute to documentation:

1. Edit the appropriate files in the `docs/` directory
2. Build the documentation locally to verify changes:
   ```bash
   cd docs
   make html
   ```
3. View the documentation by opening `docs/_build/html/index.html` in a browser
4. Submit a pull request with your changes

## Pull Request Process

### Creating a Pull Request

1. Push your feature branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Go to the [Summit SEO repository](https://github.com/summit-seo/summit-seo) and click "New Pull Request"

3. Choose "compare across forks" and select your fork and branch

4. Fill in the PR template with:
   - A clear title
   - A description of the changes
   - Reference to related issues
   - Any breaking changes
   - Any additional information for reviewers

### PR Requirements

Pull requests must meet these requirements before merging:

- All tests passing
- Code meets style guidelines
- New code has test coverage
- Documentation updated
- PR description complete
- Appropriate labels added
- Signed-off by at least one maintainer

### PR Labels

Use labels to categorize your PR:

- `bug`: Bug fix
- `feature`: New feature
- `enhancement`: Improvement to existing functionality
- `documentation`: Documentation-only changes
- `breaking-change`: Introduces breaking changes
- `good-first-issue`: Suitable for first-time contributors
- `help-wanted`: Extra attention needed

## Review Process

All submissions go through a review process:

### Code Review Guidelines

As a contributor:
- Be responsive to feedback
- Explain your design decisions
- Be willing to make requested changes
- Ask questions if feedback is unclear

As a reviewer:
- Be respectful and constructive
- Explain the reasoning behind suggestions
- Focus on code quality, not style preferences
- Consider the overall architecture and maintainability

### Addressing Feedback

1. Make requested changes in your feature branch
2. Commit and push the changes
3. Respond to review comments in GitHub
4. Request a re-review when changes are complete

### Approval and Merging

PRs require approval from at least one maintainer before merging. Once approved:

1. Maintainer will merge the PR or request you to merge
2. The branch will be deleted after merging
3. The PR will be linked to any related issues
4. The changes will be included in the next release

## Issue Tracking

Summit SEO uses GitHub Issues for tracking bugs, features, and other tasks.

### Creating Issues

Before creating an issue:

1. Search existing issues to prevent duplicates
2. Use the appropriate issue template
3. Provide detailed information:
   - For bugs: Steps to reproduce, expected vs. actual behavior, environment details
   - For features: Detailed description, use cases, acceptance criteria

### Issue Labels

Issues are categorized with labels:

- `bug`: Something isn't working
- `feature`: New feature request
- `enhancement`: Improvement to existing functionality
- `documentation`: Documentation-related issues
- `question`: Request for information
- `good-first-issue`: Good for newcomers
- `help-wanted`: Extra attention needed
- `wontfix`: This won't be addressed
- `duplicate`: This issue already exists

### Working on Issues

1. Comment on an issue to express interest
2. Wait for assignment or confirmation from a maintainer
3. Reference the issue number in your PR using `#issue-number`

## Release Process

Summit SEO follows semantic versioning (MAJOR.MINOR.PATCH):

- MAJOR: Incompatible API changes
- MINOR: Backward-compatible new features
- PATCH: Backward-compatible bug fixes

### Release Schedule

- Patch releases: As needed for critical bug fixes
- Minor releases: Every 1-2 months with new features
- Major releases: When significant API changes are required, announced in advance

### Release Process

1. A release branch is created
2. Version numbers are updated
3. Final testing is performed
4. Release notes are generated
5. GitHub release is created
6. Package is published to PyPI

### Release Notes

Release notes include:

- New features
- Bug fixes
- Breaking changes
- Deprecations
- Migration guides
- Contributors

## Community

### Communication Channels

- **GitHub Discussions**: For feature discussions and community help
- **Issue Tracker**: For bugs and specific tasks
- **Discord**: For real-time communication
- **Monthly Community Call**: For project updates and discussion

### Getting Help

- Check the [documentation](https://docs.summit-seo.org)
- Ask in GitHub Discussions
- Join Discord for real-time help
- Email the maintainers for private inquiries

### Recognition

All contributors are recognized in:

- Release notes
- CONTRIBUTORS.md file
- Annual recognition posts

### Becoming a Maintainer

Active contributors may be invited to become maintainers. Criteria include:

- Consistent quality contributions
- Helping other contributors
- Participating in discussions
- Understanding project architecture and goals
- Demonstrating good judgment in reviews

---

Thank you for contributing to Summit SEO! Your efforts help make the project better for everyone. 