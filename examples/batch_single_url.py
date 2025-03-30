#!/usr/bin/env python3
"""Simple example script to run batch analysis on a single URL."""

import asyncio
import sys
from summit_seo.cli.analysis_runner import AnalysisRunner
from summit_seo.cli.progress_display import DisplayStyle
from summit_seo.cli.output_formatter import OutputFormat, set_output_format

async def main():
    """Run a batch analysis on a URL."""
    if len(sys.argv) != 2:
        print("Usage: python batch_single_url.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Configure output format for batch mode
    set_output_format(OutputFormat.BATCH, show_details=True)
    
    # Create runner with batch mode enabled
    runner = AnalysisRunner(
        url=url,
        display_style=DisplayStyle.MINIMAL,
        batch_mode=True
    )
    
    # Run the analysis
    report_path = await runner.run()
    
    # Print the final report path
    print(f"\nReport saved to: {report_path}")

if __name__ == "__main__":
    asyncio.run(main()) 