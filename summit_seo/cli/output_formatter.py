"""Output formatters for CLI results.

This module provides customizable output formats for CLI results,
allowing users to control how analysis results are displayed.
"""

import json
import os
import sys
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List, Optional, Union

from summit_seo.cli.logging_system import get_logger

logger = get_logger(__name__)


class OutputFormat(str, Enum):
    """Available output formats for CLI results."""
    
    PLAIN = "plain"     # Simple text output
    JSON = "json"       # JSON formatted output
    YAML = "yaml"       # YAML formatted output
    CSV = "csv"         # CSV formatted output
    TABLE = "table"     # Tabular output
    BATCH = "batch"     # Minimal output for batch processing


class OutputFormatter(ABC):
    """Base class for output formatters."""
    
    @abstractmethod
    def format_result(self, result: Dict[str, Any]) -> str:
        """Format a result dictionary into a string.
        
        Args:
            result: Analysis result dictionary.
            
        Returns:
            Formatted result string.
        """
        pass
    
    @abstractmethod
    def format_error(self, error: str) -> str:
        """Format an error message.
        
        Args:
            error: Error message.
            
        Returns:
            Formatted error string.
        """
        pass
    
    @abstractmethod
    def format_summary(self, summary: Dict[str, Any]) -> str:
        """Format a summary dictionary.
        
        Args:
            summary: Summary dictionary.
            
        Returns:
            Formatted summary string.
        """
        pass
    
    @abstractmethod
    def format_list(self, items: List[Any], title: Optional[str] = None) -> str:
        """Format a list of items.
        
        Args:
            items: List of items to format.
            title: Optional title for the list.
            
        Returns:
            Formatted list string.
        """
        pass


class PlainFormatter(OutputFormatter):
    """Plain text output formatter."""
    
    def __init__(self, indent: int = 2, width: int = 80):
        """Initialize the formatter.
        
        Args:
            indent: Number of spaces to use for indentation.
            width: Maximum line width.
        """
        self.indent = indent
        self.width = width
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """Format a result dictionary into plain text."""
        lines = []
        
        # Add title if present
        if "title" in result:
            lines.append(result["title"])
            lines.append("=" * len(result["title"]))
            lines.append("")
        
        # Add score if present
        if "score" in result:
            lines.append(f"Score: {result['score']:.1f}/100")
            lines.append("")
        
        # Add issues if present
        if "issues" in result and result["issues"]:
            lines.append("Issues:")
            for issue in result["issues"]:
                lines.append(f"{' ' * self.indent}- {issue['description']}")
                if "severity" in issue:
                    lines.append(f"{' ' * (self.indent * 2)}Severity: {issue['severity']}")
                if "location" in issue:
                    lines.append(f"{' ' * (self.indent * 2)}Location: {issue['location']}")
            lines.append("")
        
        # Add recommendations if present
        if "recommendations" in result and result["recommendations"]:
            lines.append("Recommendations:")
            for rec in result["recommendations"]:
                lines.append(f"{' ' * self.indent}- {rec['description']}")
                if "priority" in rec:
                    lines.append(f"{' ' * (self.indent * 2)}Priority: {rec['priority']}")
                if "impact" in rec:
                    lines.append(f"{' ' * (self.indent * 2)}Impact: {rec['impact']}")
            lines.append("")
        
        # Add additional information if present
        if "details" in result and result["details"]:
            lines.append("Details:")
            self._append_dict(lines, result["details"], self.indent)
            lines.append("")
            
        return "\n".join(lines)
    
    def format_error(self, error: str) -> str:
        """Format an error message as plain text."""
        return f"Error: {error}"
    
    def format_summary(self, summary: Dict[str, Any]) -> str:
        """Format a summary dictionary as plain text."""
        lines = []
        
        # Add title
        if "title" in summary:
            lines.append(summary["title"])
            lines.append("=" * len(summary["title"]))
            lines.append("")
        
        # Add summary information
        for key, value in summary.items():
            if key != "title":
                if isinstance(value, dict):
                    lines.append(f"{key}:")
                    self._append_dict(lines, value, self.indent)
                    lines.append("")
                elif isinstance(value, list):
                    lines.append(f"{key}:")
                    for item in value:
                        lines.append(f"{' ' * self.indent}- {item}")
                    lines.append("")
                else:
                    lines.append(f"{key}: {value}")
        
        return "\n".join(lines)
    
    def format_list(self, items: List[Any], title: Optional[str] = None) -> str:
        """Format a list of items as plain text."""
        lines = []
        
        # Add title if provided
        if title:
            lines.append(title)
            lines.append("=" * len(title))
            lines.append("")
        
        # Add items
        for item in items:
            if isinstance(item, dict):
                # Use the first value as the item text
                text = next(iter(item.values())) if item else "N/A"
                lines.append(f"- {text}")
                
                # Add remaining key-value pairs with indentation
                for key, value in item.items():
                    if value != text:  # Skip the first value which we already added
                        lines.append(f"{' ' * self.indent}{key}: {value}")
            else:
                lines.append(f"- {item}")
        
        return "\n".join(lines)
    
    def _append_dict(self, lines: List[str], data: Dict[str, Any], indent: int):
        """Helper method to append a dictionary to the output lines."""
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{' ' * indent}{key}:")
                self._append_dict(lines, value, indent + self.indent)
            elif isinstance(value, list):
                lines.append(f"{' ' * indent}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"{' ' * (indent + self.indent)}-")
                        self._append_dict(lines, item, indent + self.indent * 2)
                    else:
                        lines.append(f"{' ' * (indent + self.indent)}- {item}")
            else:
                lines.append(f"{' ' * indent}{key}: {value}")


class JsonFormatter(OutputFormatter):
    """JSON output formatter."""
    
    def __init__(self, indent: int = 2, sort_keys: bool = True):
        """Initialize the formatter.
        
        Args:
            indent: Number of spaces to use for indentation.
            sort_keys: Whether to sort dictionary keys.
        """
        self.indent = indent
        self.sort_keys = sort_keys
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """Format a result dictionary as JSON."""
        return json.dumps(result, indent=self.indent, sort_keys=self.sort_keys)
    
    def format_error(self, error: str) -> str:
        """Format an error message as JSON."""
        return json.dumps({"error": error}, indent=self.indent, sort_keys=self.sort_keys)
    
    def format_summary(self, summary: Dict[str, Any]) -> str:
        """Format a summary dictionary as JSON."""
        return json.dumps(summary, indent=self.indent, sort_keys=self.sort_keys)
    
    def format_list(self, items: List[Any], title: Optional[str] = None) -> str:
        """Format a list of items as JSON."""
        data = {"items": items}
        if title:
            data["title"] = title
        return json.dumps(data, indent=self.indent, sort_keys=self.sort_keys)


class CsvFormatter(OutputFormatter):
    """CSV output formatter."""
    
    def __init__(self, delimiter: str = ",", quote_char: str = '"'):
        """Initialize the formatter.
        
        Args:
            delimiter: Field delimiter.
            quote_char: Character to use for quoting.
        """
        self.delimiter = delimiter
        self.quote_char = quote_char
        
        # Try to import the csv module
        try:
            import csv
            self.csv = csv
        except ImportError:
            logger.error("CSV module not available. Using simple implementation.")
            self.csv = None
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """Format a result dictionary as CSV."""
        lines = []
        
        # Format issues
        if "issues" in result and result["issues"]:
            lines.append("Issues")
            headers = ["Description", "Severity", "Location"]
            lines.append(self.delimiter.join(headers))
            
            for issue in result["issues"]:
                row = [
                    self._quote(issue.get("description", "")),
                    self._quote(issue.get("severity", "")),
                    self._quote(issue.get("location", ""))
                ]
                lines.append(self.delimiter.join(row))
            
            lines.append("")  # Add blank line between sections
        
        # Format recommendations
        if "recommendations" in result and result["recommendations"]:
            lines.append("Recommendations")
            headers = ["Description", "Priority", "Impact"]
            lines.append(self.delimiter.join(headers))
            
            for rec in result["recommendations"]:
                row = [
                    self._quote(rec.get("description", "")),
                    self._quote(rec.get("priority", "")),
                    self._quote(rec.get("impact", ""))
                ]
                lines.append(self.delimiter.join(row))
        
        return "\n".join(lines)
    
    def format_error(self, error: str) -> str:
        """Format an error message as CSV."""
        return f"Error{self.delimiter}{self._quote(error)}"
    
    def format_summary(self, summary: Dict[str, Any]) -> str:
        """Format a summary dictionary as CSV."""
        lines = []
        
        # Add headers
        headers = list(summary.keys())
        lines.append(self.delimiter.join(self._quote(h) for h in headers))
        
        # Add values
        values = []
        for key in headers:
            value = summary[key]
            if isinstance(value, (dict, list)):
                # Convert complex values to JSON
                values.append(self._quote(json.dumps(value)))
            else:
                values.append(self._quote(str(value)))
        
        lines.append(self.delimiter.join(values))
        
        return "\n".join(lines)
    
    def format_list(self, items: List[Any], title: Optional[str] = None) -> str:
        """Format a list of items as CSV."""
        lines = []
        
        # Add title if provided
        if title:
            lines.append(title)
        
        # Determine headers
        if items and isinstance(items[0], dict):
            headers = list(items[0].keys())
            lines.append(self.delimiter.join(self._quote(h) for h in headers))
            
            for item in items:
                row = []
                for header in headers:
                    value = item.get(header, "")
                    if isinstance(value, (dict, list)):
                        # Convert complex values to JSON
                        row.append(self._quote(json.dumps(value)))
                    else:
                        row.append(self._quote(str(value)))
                lines.append(self.delimiter.join(row))
        else:
            # Simple list
            lines.append("Item")
            for item in items:
                lines.append(self._quote(str(item)))
        
        return "\n".join(lines)
    
    def _quote(self, value: str) -> str:
        """Quote a string value if it contains the delimiter or quote character."""
        if self.delimiter in value or self.quote_char in value or "\n" in value:
            # Escape quote characters and surround with quotes
            escaped = value.replace(self.quote_char, self.quote_char + self.quote_char)
            return f"{self.quote_char}{escaped}{self.quote_char}"
        return value


class TableFormatter(OutputFormatter):
    """Tabular output formatter."""
    
    def __init__(self, max_width: Optional[int] = None):
        """Initialize the formatter.
        
        Args:
            max_width: Maximum width of the table in characters.
        """
        # Use terminal width if not specified
        if max_width is None:
            try:
                max_width = os.get_terminal_size().columns
            except (AttributeError, OSError):
                max_width = 80  # Fallback width
        
        self.max_width = max_width
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """Format a result dictionary as a table."""
        lines = []
        
        # Add title and score
        if "title" in result:
            lines.append(self._create_header(result["title"]))
        
        if "score" in result:
            lines.append(self._create_row(["Score", f"{result['score']:.1f}/100"]))
            lines.append("")
        
        # Format issues
        if "issues" in result and result["issues"]:
            lines.append(self._create_header("Issues"))
            
            # Create table header
            headers = ["Description", "Severity", "Location"]
            lines.append(self._create_row(headers, is_header=True))
            lines.append(self._create_separator(len(headers)))
            
            # Add issues
            for issue in result["issues"]:
                row = [
                    issue.get("description", ""),
                    issue.get("severity", ""),
                    issue.get("location", "")
                ]
                lines.append(self._create_row(row))
            
            lines.append("")
        
        # Format recommendations
        if "recommendations" in result and result["recommendations"]:
            lines.append(self._create_header("Recommendations"))
            
            # Create table header
            headers = ["Description", "Priority", "Impact"]
            lines.append(self._create_row(headers, is_header=True))
            lines.append(self._create_separator(len(headers)))
            
            # Add recommendations
            for rec in result["recommendations"]:
                row = [
                    rec.get("description", ""),
                    rec.get("priority", ""),
                    rec.get("impact", "")
                ]
                lines.append(self._create_row(row))
            
            lines.append("")
        
        return "\n".join(lines)
    
    def format_error(self, error: str) -> str:
        """Format an error message as a table."""
        lines = [
            self._create_header("Error"),
            error
        ]
        return "\n".join(lines)
    
    def format_summary(self, summary: Dict[str, Any]) -> str:
        """Format a summary dictionary as a table."""
        lines = []
        
        # Add title
        if "title" in summary:
            lines.append(self._create_header(summary["title"]))
        
        # Create key-value table
        lines.append(self._create_row(["Key", "Value"], is_header=True))
        lines.append(self._create_separator(2))
        
        for key, value in summary.items():
            if key != "title":
                if isinstance(value, (dict, list)):
                    # Convert complex values to JSON
                    value_str = json.dumps(value, sort_keys=True)
                    if len(value_str) > self.max_width // 2:
                        value_str = value_str[:self.max_width // 2 - 3] + "..."
                else:
                    value_str = str(value)
                
                lines.append(self._create_row([key, value_str]))
        
        return "\n".join(lines)
    
    def format_list(self, items: List[Any], title: Optional[str] = None) -> str:
        """Format a list of items as a table."""
        lines = []
        
        # Add title if provided
        if title:
            lines.append(self._create_header(title))
        
        # Determine table structure
        if items and isinstance(items[0], dict):
            # Create table from dictionaries
            headers = list(items[0].keys())
            lines.append(self._create_row(headers, is_header=True))
            lines.append(self._create_separator(len(headers)))
            
            for item in items:
                row = [str(item.get(header, "")) for header in headers]
                lines.append(self._create_row(row))
        else:
            # Create simple list table
            lines.append(self._create_row(["Items"], is_header=True))
            lines.append(self._create_separator(1))
            
            for item in items:
                lines.append(self._create_row([str(item)]))
        
        return "\n".join(lines)
    
    def _create_header(self, text: str) -> str:
        """Create a header line."""
        return f"\n{text}\n{'-' * min(len(text), self.max_width)}"
    
    def _create_separator(self, columns: int) -> str:
        """Create a separator line for a table."""
        col_width = max(1, (self.max_width - 3 * (columns - 1) - 2) // columns)
        parts = ["-" * col_width for _ in range(columns)]
        return f"|{'+'.join(parts)}|"
    
    def _create_row(self, values: List[str], is_header: bool = False) -> str:
        """Create a table row."""
        columns = len(values)
        col_width = max(1, (self.max_width - 3 * (columns - 1) - 2) // columns)
        
        # Truncate or pad each value
        formatted_values = []
        for value in values:
            if len(value) > col_width:
                formatted = value[:col_width - 3] + "..."
            else:
                formatted = value.ljust(col_width)
            
            if is_header:
                formatted = formatted.upper()
                
            formatted_values.append(formatted)
        
        return f"| {' | '.join(formatted_values)} |"


class YamlFormatter(OutputFormatter):
    """YAML output formatter."""
    
    def __init__(self, indent: int = 2):
        """Initialize the formatter.
        
        Args:
            indent: Number of spaces to use for indentation.
        """
        self.indent = indent
        
        # Try to import yaml
        try:
            import yaml
            self.yaml = yaml
        except ImportError:
            logger.error("YAML module not available. Using JSON fallback.")
            self.yaml = None
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """Format a result dictionary as YAML."""
        if self.yaml:
            return self.yaml.dump(result, indent=self.indent, sort_keys=True)
        else:
            # Fallback to JSON if yaml not available
            return json.dumps(result, indent=self.indent, sort_keys=True)
    
    def format_error(self, error: str) -> str:
        """Format an error message as YAML."""
        if self.yaml:
            return self.yaml.dump({"error": error}, indent=self.indent)
        else:
            return json.dumps({"error": error}, indent=self.indent)
    
    def format_summary(self, summary: Dict[str, Any]) -> str:
        """Format a summary dictionary as YAML."""
        if self.yaml:
            return self.yaml.dump(summary, indent=self.indent, sort_keys=True)
        else:
            return json.dumps(summary, indent=self.indent, sort_keys=True)
    
    def format_list(self, items: List[Any], title: Optional[str] = None) -> str:
        """Format a list of items as YAML."""
        data = {"items": items}
        if title:
            data["title"] = title
            
        if self.yaml:
            return self.yaml.dump(data, indent=self.indent, sort_keys=True)
        else:
            return json.dumps(data, indent=self.indent, sort_keys=True)


class BatchFormatter(OutputFormatter):
    """Minimal output formatter optimized for batch processing and scripting."""
    
    def __init__(self, show_details: bool = False):
        """Initialize the formatter.
        
        Args:
            show_details: Whether to show detailed information.
        """
        self.show_details = show_details
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """Format a result dictionary into minimal output for batch processing."""
        lines = []
        
        # Add score information in a machine-readable format
        if "score" in result:
            score = result.get("score", 0)
            analyzer = result.get("analyzer", "Unknown")
            lines.append(f"{analyzer}:{score:.1f}")
        
        # Add critical issues in compact format if show_details is enabled
        if self.show_details and "issues" in result and result["issues"]:
            # Only include high and critical severity issues
            critical_issues = [
                issue for issue in result["issues"] 
                if issue.get("severity", "").lower() in ("high", "critical")
            ]
            
            if critical_issues:
                lines.append("CRITICAL_ISSUES:")
                for issue in critical_issues[:5]:  # Limit to 5 issues max
                    lines.append(f"- {issue.get('description', 'Unknown issue')}")
        
        return "\n".join(lines)
    
    def format_error(self, error: str) -> str:
        """Format an error message for batch processing."""
        return f"ERROR:{error}"
    
    def format_summary(self, summary: Dict[str, Any]) -> str:
        """Format a summary dictionary for batch processing."""
        lines = []
        
        # Include only key metrics in a machine-readable format
        if "overall_score" in summary:
            lines.append(f"OVERALL_SCORE:{summary['overall_score']:.1f}")
        
        if "duration" in summary:
            lines.append(f"DURATION:{summary['duration']:.2f}")
        
        if "url" in summary:
            lines.append(f"URL:{summary['url']}")
        
        # Add analyzer scores if present
        if "analyzer_scores" in summary and isinstance(summary["analyzer_scores"], dict):
            lines.append("ANALYZER_SCORES:")
            for analyzer, score in summary["analyzer_scores"].items():
                lines.append(f"{analyzer}:{score:.1f}")
        
        return "\n".join(lines)
    
    def format_list(self, items: List[Any], title: Optional[str] = None) -> str:
        """Format a list of items for batch processing."""
        if not items:
            return "EMPTY_LIST"
        
        lines = []
        
        # Add items in a compact, machine-readable format
        for item in items:
            if isinstance(item, dict):
                # Get the primary identifier for the item
                identifier = next(iter(item.values())) if item else "unknown"
                lines.append(f"{identifier}")
            else:
                lines.append(f"{item}")
        
        return "\n".join(lines)


class OutputManager:
    """Manager for handling different output formatters."""
    
    def __init__(self, format_name: str = OutputFormat.PLAIN, **format_options):
        """Initialize the output manager.
        
        Args:
            format_name: Name of the output format to use.
            **format_options: Additional options for the formatter.
        """
        self.format_name = format_name
        self.format_options = format_options
        self.formatter = self._create_formatter()
    
    def _create_formatter(self) -> OutputFormatter:
        """Create a formatter instance based on format name."""
        if self.format_name == OutputFormat.JSON:
            return JsonFormatter(**self.format_options)
        elif self.format_name == OutputFormat.YAML:
            return YamlFormatter(**self.format_options)
        elif self.format_name == OutputFormat.CSV:
            return CsvFormatter(**self.format_options)
        elif self.format_name == OutputFormat.TABLE:
            return TableFormatter(**self.format_options)
        elif self.format_name == OutputFormat.BATCH:
            return BatchFormatter(**self.format_options)
        else:
            return PlainFormatter(**self.format_options)
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """Format a result dictionary."""
        return self.formatter.format_result(result)
    
    def format_error(self, error: str) -> str:
        """Format an error message."""
        return self.formatter.format_error(error)
    
    def format_summary(self, summary: Dict[str, Any]) -> str:
        """Format a summary dictionary."""
        return self.formatter.format_summary(summary)
    
    def format_list(self, items: List[Any], title: Optional[str] = None) -> str:
        """Format a list of items."""
        return self.formatter.format_list(items, title)
    
    def set_format(self, format_name: str, **format_options):
        """Change the output format.
        
        Args:
            format_name: Name of the output format to use.
            **format_options: Additional options for the formatter.
        """
        self.format_name = format_name
        self.format_options.update(format_options)
        self.formatter = self._create_formatter()


# Create default output manager
output_manager = OutputManager()


def format_result(result: Dict[str, Any]) -> str:
    """Format a result dictionary.
    
    Args:
        result: Result dictionary to format.
        
    Returns:
        Formatted result string.
    """
    return output_manager.format_result(result)


def format_error(error: str) -> str:
    """Format an error message.
    
    Args:
        error: Error message to format.
        
    Returns:
        Formatted error string.
    """
    return output_manager.format_error(error)


def format_summary(summary: Dict[str, Any]) -> str:
    """Format a summary dictionary.
    
    Args:
        summary: Summary dictionary to format.
        
    Returns:
        Formatted summary string.
    """
    return output_manager.format_summary(summary)


def format_list(items: List[Any], title: Optional[str] = None) -> str:
    """Format a list of items.
    
    Args:
        items: List of items to format.
        title: Optional title for the list.
        
    Returns:
        Formatted list string.
    """
    return output_manager.format_list(items, title)


def set_output_format(format_name: str, **format_options):
    """Set the global output format.
    
    Args:
        format_name: Name of the output format to use.
        **format_options: Additional options for the formatter.
    """
    output_manager.set_format(format_name, **format_options) 