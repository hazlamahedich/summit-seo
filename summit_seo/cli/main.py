"""Command-line interface for Summit SEO."""

import argparse
import asyncio
import sys
from typing import List, Dict, Any, Optional
import logging

from summit_seo.cli.analysis_runner import AnalysisRunner
from summit_seo.cli.progress_display import DisplayStyle
from summit_seo.cli.interactive_mode import run_interactive_analysis
from summit_seo.cli.logging_system import configure_logging, get_logger
from summit_seo.cli.output_formatter import OutputFormat, set_output_format

# Get logger for this module
logger = get_logger(__name__)


async def run_analysis(args):
    """Run SEO analysis with specified arguments."""
    # Convert analyzers string to list if provided
    analyzers = None
    if args.analyzers:
        analyzers = [a.strip() for a in args.analyzers.split(",")]
    
    # Convert style string to DisplayStyle enum
    style_map = {
        "minimal": DisplayStyle.MINIMAL,
        "detailed": DisplayStyle.DETAILED,
        "animated": DisplayStyle.ANIMATED,
        "compact": DisplayStyle.COMPACT
    }
    display_style = style_map.get(args.style, DisplayStyle.ANIMATED)
    
    # Check if visual report is requested but format is not HTML
    if args.visual and args.format.lower() != "html":
        logger.warning("Visual reports are only available for HTML format. Ignoring --visual flag.")
        args.visual = False
    
    # Configure output format if specified
    if args.output_format:
        try:
            output_format = OutputFormat(args.output_format)
            set_output_format(output_format, width=args.output_width)
        except ValueError:
            logger.warning("Invalid output format: %s. Using default.", args.output_format)
    
    # Configure batch mode settings
    batch_mode = args.batch
    if batch_mode:
        # Force minimal display style in batch mode
        display_style = DisplayStyle.MINIMAL
        
        # Use batch output format if not explicitly specified
        if not args.output_format:
            set_output_format(OutputFormat.BATCH, show_details=args.detailed)
    
    # Create and run the analysis
    runner = AnalysisRunner(
        url=args.url,
        analyzers=analyzers,
        display_style=display_style,
        output_format=args.format,
        output_path=args.output,
        visual_report=args.visual,
        verbose=args.verbose,
        batch_mode=batch_mode
    )
    
    # Run in interactive mode if requested
    if args.interactive:
        run_interactive_analysis(runner)
    else:
        return await runner.run()


def setup_logging(args):
    """Configure logging based on command-line arguments."""
    # Determine log level
    log_level = "INFO"
    if args.verbose:
        log_level = "DEBUG"
    if args.trace:
        log_level = "TRACE"
        
    # Configure logging system
    config = {
        "log_level": log_level,
        "console_output": True,
        "file_output": args.log_file,
        "log_directory": args.log_dir,
        "use_colors": not args.no_color,
        "log_file_prefix": "summit_seo"
    }
    
    # Add syslog configuration if specified
    if args.syslog:
        config["syslog_output"] = True
        config["syslog_address"] = args.syslog_address
        
    configure_logging(config)
    
    logger.info("Logging configured with level %s", log_level)
    if args.log_file:
        logger.info("Log files will be saved to %s", args.log_dir or "logs/")


def cli():
    """Execute the command-line interface."""
    parser = argparse.ArgumentParser(description="Summit SEO - Comprehensive SEO Analysis Tool")
    
    # Add global options
    parser.add_argument(
        "-v", "--verbose",
        help="Enable verbose output",
        action="store_true"
    )
    parser.add_argument(
        "--trace",
        help="Enable trace-level logging (even more verbose than debug)",
        action="store_true"
    )
    parser.add_argument(
        "--log-file",
        help="Log to file",
        action="store_true"
    )
    parser.add_argument(
        "--log-dir",
        help="Directory for log files",
        type=str
    )
    parser.add_argument(
        "--no-color",
        help="Disable colored output",
        action="store_true"
    )
    parser.add_argument(
        "--syslog",
        help="Send logs to syslog",
        action="store_true"
    )
    parser.add_argument(
        "--syslog-address",
        help="Syslog server address (host:port)",
        type=str
    )
    parser.add_argument(
        "--output-format",
        help="Output format for CLI results",
        choices=[f.value for f in OutputFormat],
        type=str
    )
    parser.add_argument(
        "--output-width",
        help="Width for formatted output",
        type=int,
        default=80
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Analysis command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a website")
    analyze_parser.add_argument("url", help="URL to analyze")
    analyze_parser.add_argument(
        "-a", "--analyzers",
        help="Comma-separated list of analyzers to run (default: all)",
        type=str
    )
    analyze_parser.add_argument(
        "-s", "--style",
        help="Progress display style (default: animated)",
        choices=["minimal", "detailed", "animated", "compact"],
        default="animated"
    )
    analyze_parser.add_argument(
        "-i", "--interactive",
        help="Run in interactive mode with keyboard controls",
        action="store_true"
    )
    analyze_parser.add_argument(
        "-f", "--format",
        help="Output format (default: html)",
        choices=["html", "json", "csv", "xml", "pdf"],
        default="html"
    )
    analyze_parser.add_argument(
        "-o", "--output",
        help="Output directory (default: current directory)",
        default="."
    )
    analyze_parser.add_argument(
        "--visual",
        help="Generate a visual report with charts (HTML format only)",
        action="store_true"
    )
    analyze_parser.add_argument(
        "-b", "--batch",
        help="Run in batch mode with minimal output",
        action="store_true"
    )
    analyze_parser.add_argument(
        "-d", "--detailed",
        help="Show detailed information in batch mode",
        action="store_true"
    )
    analyze_parser.add_argument(
        "--machine-readable",
        help="Output machine-readable format (implies --batch)",
        action="store_true"
    )
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available components")
    list_parser.add_argument(
        "component_type",
        choices=["analyzers", "collectors", "processors", "reporters"],
        help="Type of components to list"
    )
    
    # Version command
    subparsers.add_parser("version", help="Show version information")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up logging based on arguments
    setup_logging(args)
    
    # Process commands
    if args.command == "analyze":
        # Check for incompatible options
        if args.interactive and args.batch:
            logger.error("Cannot use both interactive and batch mode at the same time.")
            sys.exit(1)
        
        # Enable batch mode if machine-readable output is specified    
        if args.machine_readable:
            args.batch = True
            
        # Setup batch mode if requested
        if args.batch:
            args.style = "minimal"
            if not args.verbose:
                # Configure minimal logging in batch mode
                logger.info("Configuring minimal logging for batch mode")
                for handler in logging.root.handlers:
                    if isinstance(handler, logging.StreamHandler):
                        handler.setLevel(logging.WARNING)
        
        # Run analysis asynchronously
        try:
            report_path = asyncio.run(run_analysis(args))
            # Exit with status code 0 for successful analysis
            sys.exit(0)
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            # Exit with status code 1 for failed analysis
            sys.exit(1)
    elif args.command == "list":
        # List available components
        if args.component_type == "analyzers":
            from summit_seo.analyzer import AnalyzerFactory
            components = AnalyzerFactory.get_registered_analyzers()
            component_type = "Analyzers"
        elif args.component_type == "collectors":
            from summit_seo.collector import CollectorFactory
            components = CollectorFactory.get_registered_collectors()
            component_type = "Collectors"
        elif args.component_type == "processors":
            from summit_seo.processor import ProcessorFactory
            components = ProcessorFactory.get_registered_processors()
            component_type = "Processors"
        elif args.component_type == "reporters":
            from summit_seo.reporter import ReporterFactory
            components = ReporterFactory.get_registered_reporters()
            component_type = "Reporters"
        
        # Use the output formatter to format the list
        from summit_seo.cli.output_formatter import format_list
        formatted_output = format_list(sorted(components), f"Available {component_type}")
        print(formatted_output)
    elif args.command == "version":
        # Show version information
        from summit_seo import __version__
        print(f"Summit SEO v{__version__}")
    else:
        # No command specified, show help
        parser.print_help()


if __name__ == "__main__":
    cli() 