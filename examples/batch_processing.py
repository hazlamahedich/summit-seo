#!/usr/bin/env python3
"""Example script demonstrating batch processing mode for multiple URLs.

This script analyzes multiple URLs in batch mode, which is useful for
automated processing and integration with other systems.

Usage:
    python batch_processing.py urls.txt

Where urls.txt contains one URL per line.
"""

import argparse
import asyncio
import os
import sys
import time
from typing import List

from summit_seo.cli.analysis_runner import AnalysisRunner
from summit_seo.cli.progress_display import DisplayStyle
from summit_seo.cli.output_formatter import OutputFormat, set_output_format


async def analyze_url(url: str, output_dir: str, analyzers: List[str] = None) -> dict:
    """Analyze a single URL in batch mode.
    
    Args:
        url: URL to analyze
        output_dir: Directory for output reports
        analyzers: List of specific analyzers to run (None for all)
        
    Returns:
        Dictionary with analysis results and metadata
    """
    # Configure batch output format
    set_output_format(OutputFormat.BATCH, show_details=True)
    
    # Create the runner with batch mode enabled
    runner = AnalysisRunner(
        url=url,
        analyzers=analyzers,
        display_style=DisplayStyle.MINIMAL,
        output_format="html",
        output_path=output_dir,
        batch_mode=True
    )
    
    # Record start time
    start_time = time.time()
    
    try:
        # Run the analysis
        report_path = await runner.run()
        end_time = time.time()
        
        return {
            "url": url,
            "success": True,
            "report_path": report_path,
            "duration": end_time - start_time
        }
    except Exception as e:
        end_time = time.time()
        return {
            "url": url,
            "success": False,
            "error": str(e),
            "duration": end_time - start_time
        }


async def batch_process(urls: List[str], output_dir: str, analyzers: List[str] = None) -> List[dict]:
    """Process multiple URLs in batch mode.
    
    Args:
        urls: List of URLs to analyze
        output_dir: Directory for output reports
        analyzers: List of specific analyzers to run (None for all)
        
    Returns:
        List of result dictionaries
    """
    results = []
    
    # Process each URL sequentially
    for i, url in enumerate(urls, 1):
        print(f"\nProcessing URL {i}/{len(urls)}: {url}")
        result = await analyze_url(url, output_dir, analyzers)
        results.append(result)
        
        # Print a short summary
        if result["success"]:
            print(f"✓ Success ({result['duration']:.2f}s): {os.path.basename(result['report_path'])}")
        else:
            print(f"✗ Failed ({result['duration']:.2f}s): {result['error']}")
    
    return results


def load_urls(filename: str) -> List[str]:
    """Load URLs from a file with one URL per line.
    
    Args:
        filename: Path to file containing URLs
        
    Returns:
        List of URLs
    """
    with open(filename, "r") as f:
        # Strip whitespace and filter out empty lines and comments
        return [
            line.strip() for line in f 
            if line.strip() and not line.strip().startswith("#")
        ]


def main():
    """Main entry point for the batch processing example."""
    parser = argparse.ArgumentParser(description="Batch process multiple URLs for SEO analysis")
    
    parser.add_argument(
        "urls_file",
        help="File containing URLs to analyze (one per line)"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output directory for reports (default: ./reports)",
        default="./reports"
    )
    
    parser.add_argument(
        "-a", "--analyzers",
        help="Comma-separated list of analyzers to run (default: all)",
        type=str
    )
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)
    
    # Load URLs from file
    try:
        urls = load_urls(args.urls_file)
    except FileNotFoundError:
        print(f"Error: File not found: {args.urls_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading URLs: {str(e)}")
        sys.exit(1)
    
    if not urls:
        print("No valid URLs found in the input file")
        sys.exit(1)
    
    # Parse analyzers if specified
    analyzers = None
    if args.analyzers:
        analyzers = [a.strip() for a in args.analyzers.split(",")]
    
    # Process all URLs
    start_time = time.time()
    results = asyncio.run(batch_process(urls, args.output, analyzers))
    end_time = time.time()
    
    # Print overall summary
    successful = sum(1 for r in results if r["success"])
    print("\n" + "="*50)
    print(f"BATCH PROCESSING SUMMARY")
    print("="*50)
    print(f"Total URLs: {len(urls)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(urls) - successful}")
    print(f"Total time: {end_time - start_time:.2f}s")
    print(f"Reports directory: {os.path.abspath(args.output)}")
    print("="*50)
    
    # Exit with appropriate status code
    sys.exit(0 if successful == len(urls) else 1)


if __name__ == "__main__":
    main() 