# Summit SEO Examples

This directory contains example scripts demonstrating the usage of various Summit SEO components.

## Error Handling Examples

The `error_handling_example.py` script demonstrates how to use the enhanced error handling system with actionable suggestions.

To run the example:
```bash
python examples/error_handling_example.py
```

### Features Demonstrated

1. **Custom Error Handling**
   - Creating enhanced errors with actionable suggestions
   - Providing detailed context for troubleshooting
   - Categorizing errors by severity and type

2. **Console Error Reporting**
   - Color-coded error output by severity
   - Formatted suggestion display
   - Step-by-step instructions for resolution
   - Including/excluding traceback based on verbosity needs

3. **File Error Reporting**
   - JSON-formatted error reports for machine processing
   - Text-formatted reports for human readability
   - Automatic report filename generation
   - Timestamped error reporting

4. **Simulated Error Scenarios**
   - Network errors (DNS resolution, connection failures)
   - Parsing errors (HTML parsing issues)
   - Authentication errors
   - Analyzer execution errors

### Key Components Used

- `ConsoleErrorReporter`: For displaying error information in the terminal
- `FileErrorReporter`: For writing detailed error reports to files
- `ErrorWithSuggestions`: For enhancing errors with actionable suggestions
- `ActionableSuggestion`: For structured recommendation steps
- `ErrorContext`: For capturing detailed execution context
- `get_suggestion_for_error`: For automatically generating suggestions based on error types

### Creating Your Own Suggestion Providers

To create a custom suggestion provider:

```python
from summit_seo.error_handling import SuggestionProvider, ActionableSuggestion, SuggestionSeverity

class CustomSuggestionProvider(SuggestionProvider):
    @classmethod
    def provide_suggestions(cls, error, error_text):
        # Check if this is an error we can provide suggestions for
        if "specific error pattern" in error_text:
            return [
                ActionableSuggestion(
                    message="How to fix this specific error",
                    steps=["Step 1: Check X", "Step 2: Verify Y", "Step 3: Update Z"],
                    severity=SuggestionSeverity.HIGH,
                    code_example="# Example code to fix the issue\nfixed_code = correct_implementation()",
                    documentation_url="https://docs.summit-seo.com/errors/specific-error"
                )
            ]
        return []  # Return empty list if we can't provide suggestions
```

This provider will be automatically registered with the suggestion system.

### Adding Error Context

To provide rich context with errors:

```python
from summit_seo.error_handling import ErrorContext, ConsoleErrorReporter

try:
    # Operation that might fail
    result = analyze_webpage("https://example.com")
except Exception as e:
    # Create context with details about what was happening
    context = ErrorContext(
        operation="Webpage Analysis",
        component="ContentAnalyzer",
        user_action="User requested content analysis of example.com",
        inputs={"url": "https://example.com", "depth": 2}
    )
    
    # Report the error with context
    reporter = ConsoleErrorReporter(show_traceback=True)
    reporter.report_error(e, context)
```

## Other Examples

- `basic_analysis.py`: Demonstrates basic website analysis
- `visual_report_example.py`: Shows how to generate visual reports
- `parallel_processing_example.py`: Demonstrates parallel execution
- More examples coming soon... 