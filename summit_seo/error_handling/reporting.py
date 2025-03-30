"""Module for error reporting with actionable suggestions.

This module provides utilities for reporting errors in various formats,
including rich console output, file-based logging, and structured formats
with actionable suggestions for resolution.
"""

import abc
import datetime
import json
import logging
import os
import sys
import traceback
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union, TextIO, Any, Set

from .suggestions import (
    ActionableSuggestion,
    SuggestionSeverity,
    get_suggestion_for_error
)

logger = logging.getLogger(__name__)


@dataclass
class ErrorContext:
    """Context information about an error occurrence."""
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    operation: Optional[str] = None
    component: Optional[str] = None
    user_action: Optional[str] = None
    environment: Dict[str, str] = field(default_factory=dict)
    inputs: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize environment information if not provided."""
        if not self.environment:
            # Add basic environment information
            self.environment = {
                "python_version": ".".join(map(str, sys.version_info[:3])),
                "platform": sys.platform,
                "timestamp": self.timestamp.isoformat()
            }


@dataclass
class ReportedError:
    """An error report with context and suggestions."""
    error: Exception
    error_type: str
    error_message: str
    traceback: Optional[str] = None
    context: ErrorContext = field(default_factory=ErrorContext)
    suggestions: List[ActionableSuggestion] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize derived fields if not provided."""
        if not self.error_type:
            self.error_type = type(self.error).__name__
        
        if not self.error_message:
            self.error_message = str(self.error)
        
        # Format traceback if available and not already set
        if not self.traceback and hasattr(self.error, '__traceback__'):
            self.traceback = ''.join(traceback.format_exception(
                type(self.error), self.error, self.error.__traceback__
            ))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error report to a dictionary.
        
        Returns:
            Dictionary representation of the error report
        """
        result = {
            "error_type": self.error_type,
            "error_message": self.error_message,
            "context": {
                "timestamp": self.context.timestamp.isoformat(),
                "operation": self.context.operation,
                "component": self.context.component,
                "user_action": self.context.user_action,
                "environment": self.context.environment,
            },
            "suggestions": [
                {
                    "message": s.message,
                    "steps": s.steps,
                    "severity": s.severity.value,
                    "category": s.category.value,
                    "documentation_url": s.documentation_url,
                    "requires_restart": s.requires_restart,
                    "requires_reinstall": s.requires_reinstall,
                    "estimated_fix_time": s.estimated_fix_time,
                    "code_example": s.code_example
                }
                for s in self.suggestions
            ]
        }
        
        if self.traceback:
            result["traceback"] = self.traceback
            
        return result
    
    def to_json(self, indent: int = 2) -> str:
        """Convert the error report to a JSON string.
        
        Args:
            indent: Number of spaces for indentation (default: 2)
            
        Returns:
            JSON string representation of the error report
        """
        return json.dumps(self.to_dict(), indent=indent)


class ErrorReporter(abc.ABC):
    """Base class for error reporters."""
    
    @abc.abstractmethod
    def report_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None,
        include_suggestions: bool = True
    ) -> ReportedError:
        """Report an error with context and suggestions.
        
        Args:
            error: The exception to report
            context: Optional context information about the error
            include_suggestions: Whether to include actionable suggestions
            
        Returns:
            A ReportedError object with the report information
        """
        pass


class ConsoleErrorReporter(ErrorReporter):
    """Reporter that displays errors in the console with colored output."""
    
    def __init__(
        self,
        show_traceback: bool = False,
        colored_output: bool = True,
        output_stream: TextIO = sys.stderr,
        verbose: bool = False
    ):
        """Initialize the console error reporter.
        
        Args:
            show_traceback: Whether to show the traceback (default: False)
            colored_output: Whether to use ANSI colors (default: True)
            output_stream: Where to write output (default: sys.stderr)
            verbose: Whether to show verbose output (default: False)
        """
        self.show_traceback = show_traceback
        self.colored_output = colored_output
        self.output_stream = output_stream
        self.verbose = verbose
        
        # ANSI color codes
        self.colors = {
            "reset": "\033[0m",
            "red": "\033[31m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "magenta": "\033[35m",
            "cyan": "\033[36m",
            "white": "\033[37m",
            "bold": "\033[1m",
            "underline": "\033[4m"
        } if colored_output else {
            # No colors if colored_output is False
            k: "" for k in [
                "reset", "red", "green", "yellow", "blue", 
                "magenta", "cyan", "white", "bold", "underline"
            ]
        }
    
    def color_text(self, text: str, color: str) -> str:
        """Add color to text if colored output is enabled.
        
        Args:
            text: The text to color
            color: The color name from self.colors
            
        Returns:
            Colored text if enabled, otherwise original text
        """
        if not self.colored_output:
            return text
            
        if color not in self.colors:
            return text
            
        return f"{self.colors[color]}{text}{self.colors['reset']}"
    
    def report_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None,
        include_suggestions: bool = True
    ) -> ReportedError:
        """Report an error to the console with color formatting.
        
        Args:
            error: The exception to report
            context: Optional context information about the error
            include_suggestions: Whether to include actionable suggestions
            
        Returns:
            A ReportedError object with the report information
        """
        # Create context if not provided
        if context is None:
            context = ErrorContext()
        
        # Get suggestions if requested
        suggestions = []
        if include_suggestions:
            suggestions = get_suggestion_for_error(error)
        
        # Create the error report
        report = ReportedError(
            error=error,
            error_type=type(error).__name__,
            error_message=str(error),
            traceback=None if not self.show_traceback else traceback.format_exc(),
            context=context,
            suggestions=suggestions
        )
        
        # Print the error header
        header = f"ERROR: {report.error_type}"
        if context.component:
            header += f" in {context.component}"
        
        print(self.color_text(header, "red"), file=self.output_stream)
        print(self.color_text("=" * len(header), "red"), file=self.output_stream)
        print(self.color_text(report.error_message, "yellow"), file=self.output_stream)
        print(file=self.output_stream)
        
        # Print context information if verbose
        if self.verbose and context:
            print(self.color_text("Context:", "cyan"), file=self.output_stream)
            if context.operation:
                print(f"  Operation: {context.operation}", file=self.output_stream)
            if context.user_action:
                print(f"  User Action: {context.user_action}", file=self.output_stream)
            if context.inputs:
                print(f"  Inputs: {context.inputs}", file=self.output_stream)
            print(file=self.output_stream)
        
        # Print traceback if enabled
        if self.show_traceback and report.traceback:
            print(self.color_text("Traceback:", "magenta"), file=self.output_stream)
            print(report.traceback, file=self.output_stream)
            print(file=self.output_stream)
        
        # Print suggestions
        if suggestions:
            print(self.color_text("Suggested actions:", "green"), file=self.output_stream)
            for i, suggestion in enumerate(suggestions, 1):
                # Format suggestion message with severity and steps
                severity_color = {
                    SuggestionSeverity.CRITICAL: "red",
                    SuggestionSeverity.HIGH: "red",
                    SuggestionSeverity.MEDIUM: "yellow",
                    SuggestionSeverity.LOW: "cyan",
                    SuggestionSeverity.INFO: "blue"
                }.get(suggestion.severity, "white")
                
                print(
                    f"{i}. {self.color_text(suggestion.message, severity_color)}",
                    file=self.output_stream
                )
                
                # Print the steps
                for j, step in enumerate(suggestion.steps, 1):
                    print(f"   {j}. {step}", file=self.output_stream)
                
                # Print documentation URL if available
                if suggestion.documentation_url:
                    print(
                        f"   {self.color_text('For more information:', 'blue')} "
                        f"{suggestion.documentation_url}",
                        file=self.output_stream
                    )
                
                # Print code example if available and verbose
                if self.verbose and suggestion.code_example:
                    print(
                        f"\n   {self.color_text('Example:', 'cyan')}\n",
                        file=self.output_stream
                    )
                    for line in suggestion.code_example.split('\n'):
                        print(f"     {line}", file=self.output_stream)
                
                print(file=self.output_stream)
        
        return report


class FileErrorReporter(ErrorReporter):
    """Reporter that writes detailed error reports to files."""
    
    def __init__(
        self,
        output_dir: Union[str, Path] = "error_reports",
        format: str = "json",
        include_traceback: bool = True,
        log_to_stderr: bool = True
    ):
        """Initialize the file error reporter.
        
        Args:
            output_dir: Directory to write error reports (default: "error_reports")
            format: Output format, "json" or "text" (default: "json")
            include_traceback: Whether to include traceback in reports (default: True)
            log_to_stderr: Whether to also log basic info to stderr (default: True)
        """
        self.output_dir = Path(output_dir)
        self.format = format.lower()
        self.include_traceback = include_traceback
        self.log_to_stderr = log_to_stderr
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _generate_filename(self, error_type: str, timestamp: datetime.datetime) -> str:
        """Generate a filename for the error report.
        
        Args:
            error_type: Type of error
            timestamp: When the error occurred
            
        Returns:
            Filename for the error report
        """
        # Format timestamp as YYYYMMDD_HHMMSS
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        # Sanitize error type for filename
        error_type_clean = "".join(c if c.isalnum() else "_" for c in error_type)
        # Combine with timestamp and format
        return f"error_{error_type_clean}_{timestamp_str}.{self.format}"
    
    def report_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None,
        include_suggestions: bool = True
    ) -> ReportedError:
        """Generate a detailed error report and write it to a file.
        
        Args:
            error: The exception to report
            context: Optional context information about the error
            include_suggestions: Whether to include actionable suggestions
            
        Returns:
            A ReportedError object with the report information
        """
        # Create context if not provided
        if context is None:
            context = ErrorContext()
        
        # Get suggestions if requested
        suggestions = []
        if include_suggestions:
            suggestions = get_suggestion_for_error(error)
        
        # Create the error report
        report = ReportedError(
            error=error,
            error_type=type(error).__name__,
            error_message=str(error),
            traceback=None if not self.include_traceback else traceback.format_exc(),
            context=context,
            suggestions=suggestions
        )
        
        # Generate the filename
        filename = self._generate_filename(report.error_type, context.timestamp)
        filepath = self.output_dir / filename
        
        # Write the report to the file
        with open(filepath, "w", encoding="utf-8") as f:
            if self.format == "json":
                f.write(report.to_json())
            else:
                # Plain text format
                f.write(f"ERROR: {report.error_type}\n")
                f.write(f"Message: {report.error_message}\n")
                f.write(f"Timestamp: {context.timestamp.isoformat()}\n")
                
                if context.component:
                    f.write(f"Component: {context.component}\n")
                if context.operation:
                    f.write(f"Operation: {context.operation}\n")
                if context.user_action:
                    f.write(f"User Action: {context.user_action}\n")
                
                f.write("\n")
                
                if report.traceback:
                    f.write("Traceback:\n")
                    f.write(report.traceback)
                    f.write("\n")
                
                if suggestions:
                    f.write("Suggested actions:\n")
                    for i, suggestion in enumerate(suggestions, 1):
                        f.write(f"{i}. {suggestion.message}\n")
                        f.write(f"   Severity: {suggestion.severity.value}\n")
                        f.write(f"   Category: {suggestion.category.value}\n")
                        
                        f.write("   Steps:\n")
                        for j, step in enumerate(suggestion.steps, 1):
                            f.write(f"    {j}. {step}\n")
                        
                        if suggestion.documentation_url:
                            f.write(f"   Documentation: {suggestion.documentation_url}\n")
                            
                        if suggestion.code_example:
                            f.write("   Example:\n")
                            for line in suggestion.code_example.split('\n'):
                                f.write(f"     {line}\n")
                        
                        f.write("\n")
        
        # Log basic information to stderr if requested
        if self.log_to_stderr:
            print(f"Error report written to: {filepath}", file=sys.stderr)
        
        return report 