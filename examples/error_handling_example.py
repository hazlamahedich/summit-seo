#!/usr/bin/env python3
"""
Example script demonstrating the enhanced error handling system with actionable suggestions.

This script shows how to use the error handling system to provide helpful,
actionable suggestions when errors occur during SEO analysis.
"""

import asyncio
import logging
import sys
from pathlib import Path
from urllib.error import URLError

from summit_seo.analyzer import AnalyzerFactory
from summit_seo.collector import CollectorFactory, CollectionError
from summit_seo.processor import ProcessorFactory
from summit_seo.error_handling import (
    ConsoleErrorReporter,
    FileErrorReporter,
    ErrorWithSuggestions,
    ActionableSuggestion,
    SuggestionSeverity,
    SuggestionCategory,
    ErrorContext,
    get_suggestion_for_error
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def demo_console_reporter(error, show_traceback=False):
    """Demonstrate the ConsoleErrorReporter with various errors."""
    print("\n" + "="*80)
    print(f"DEMONSTRATING CONSOLE ERROR REPORTER FOR: {type(error).__name__}")
    print("="*80)
    
    reporter = ConsoleErrorReporter(
        show_traceback=show_traceback,
        colored_output=True,
        verbose=True
    )
    
    # Create context with details about what was happening
    context = ErrorContext(
        operation="Collect and analyze webpage",
        component="CollectorExample",
        user_action="User requested analysis of a website",
        inputs={"url": "https://example.com"}
    )
    
    # Report the error with context
    reporter.report_error(error, context)


def demo_file_reporter(error):
    """Demonstrate the FileErrorReporter with various errors."""
    # Create output directory
    output_dir = Path("examples/error_reports")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    reporter = FileErrorReporter(
        output_dir=output_dir,
        format="json",
        include_traceback=True
    )
    
    # Create context with details about what was happening
    context = ErrorContext(
        operation="Collect and analyze webpage",
        component="CollectorExample",
        user_action="User requested analysis of a website",
        inputs={"url": "https://example.com"}
    )
    
    # Report the error with context
    result = reporter.report_error(error, context)
    print(f"\nError report written to: {output_dir}")


def demo_custom_error_handling():
    """Demonstrate custom error handling with ErrorWithSuggestions."""
    print("\n" + "="*80)
    print("DEMONSTRATING CUSTOM ERROR HANDLING")
    print("="*80)
    
    try:
        # Simulate a complex operation that fails
        raise ValueError("Invalid configuration: missing required field 'api_key'")
    except Exception as e:
        # Get suggestions for this error
        suggestions = get_suggestion_for_error(e)
        
        # If no suggestions found, create a custom suggestion
        if not suggestions:
            suggestions = [
                ActionableSuggestion(
                    message="API key missing from configuration",
                    steps=[
                        "Add your API key to the configuration file",
                        "Request an API key if you don't have one",
                        "Check environment variables for API_KEY"
                    ],
                    severity=SuggestionSeverity.HIGH,
                    category=SuggestionCategory.CONFIGURATION,
                    code_example="""
# Add API key to configuration
config = {
    "api_key": "your-api-key-here",
    "timeout": 30,
    "max_requests": 100
}
                    """,
                    documentation_url="https://docs.summit-seo.com/api/authentication",
                    estimated_fix_time="2-5 minutes"
                )
            ]
        
        # Create enhanced error with suggestions
        enhanced_error = ErrorWithSuggestions(
            message="Configuration error occurred",
            original_error=e,
            suggestions=suggestions
        )
        
        # Report the enhanced error
        reporter = ConsoleErrorReporter(colored_output=True)
        reporter.report_error(enhanced_error)


async def simulate_network_error():
    """Simulate a network error during collection."""
    print("\n" + "="*80)
    print("SIMULATING NETWORK ERROR")
    print("="*80)
    
    try:
        # Use a non-existent domain to trigger DNS resolution error
        collector = CollectorFactory.create(
            "WebpageCollector", 
            url="https://this-domain-does-not-exist-123456789.com"
        )
        result = await collector.collect()
    except Exception as e:
        demo_console_reporter(e)
        demo_file_reporter(e)


async def simulate_parsing_error():
    """Simulate an HTML parsing error."""
    print("\n" + "="*80)
    print("SIMULATING PARSING ERROR")
    print("="*80)
    
    try:
        # Create an invalid HTML string
        invalid_html = "<html><body><div>Unclosed div tag</body></html>"
        
        # Simulate collection
        collector = CollectorFactory.create("BaseCollector")
        collector.set_result({"html": invalid_html, "url": "https://example.com"})
        
        # Process with HTML processor
        processor = ProcessorFactory.create("HTMLProcessor")
        result = await processor.process(await collector.collect())
    except Exception as e:
        demo_console_reporter(e)


async def simulate_authentication_error():
    """Simulate an authentication error."""
    print("\n" + "="*80)
    print("SIMULATING AUTHENTICATION ERROR")
    print("="*80)
    
    # Create a custom authentication error
    auth_error = PermissionError("401 Unauthorized: Invalid API key provided")
    demo_console_reporter(auth_error)


async def simulate_analyzer_error():
    """Simulate an analyzer execution error."""
    print("\n" + "="*80)
    print("SIMULATING ANALYZER ERROR")
    print("="*80)
    
    try:
        # Try to create an analyzer that doesn't exist
        analyzer = AnalyzerFactory.create("NonExistentAnalyzer")
    except Exception as e:
        demo_console_reporter(e, show_traceback=True)


async def main():
    """Run the error handling examples."""
    print("Starting error handling examples...")
    
    # Demonstrate custom error handling
    demo_custom_error_handling()
    
    # Simulate various errors
    await simulate_network_error()
    await simulate_parsing_error()
    await simulate_authentication_error()
    await simulate_analyzer_error()
    
    print("\nError handling examples completed!")


if __name__ == "__main__":
    asyncio.run(main()) 