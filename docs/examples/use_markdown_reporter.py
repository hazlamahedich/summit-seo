#!/usr/bin/env python3
"""
Example script demonstrating how to use a custom MarkdownReporter 
with the Summit SEO framework in a complete workflow.
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Any, List

from summit_seo import SummitSEO
from summit_seo.reporter import ReporterFactory
from summit_seo.analyzer import AnalyzerFactory
from markdown_reporter import MarkdownReporter

# Register the custom reporter with the factory
ReporterFactory.register('markdown', MarkdownReporter)


async def analyze_and_generate_report(url: str, output_dir: str = 'reports'):
    """Analyze a website and generate a Markdown report.
    
    Args:
        url: The URL to analyze
        output_dir: Directory to save the report in
    """
    print(f"Analyzing {url}...")
    
    # Initialize Summit SEO with default analyzers
    summit = SummitSEO()
    
    # Configure which analyzers to use
    analyzers = ['title', 'meta', 'headings', 'links', 'images', 'performance', 'security']
    
    # Set up configuration for the analysis
    config = {
        'max_depth': 2,  # Limit crawl depth
        'max_pages': 10,  # Limit number of pages to analyze
        'user_agent': 'SummitSEO/1.0 Custom Reporter Example',
        'timeout': 30,
        'analyzers': {
            'security': {
                'check_https': True,
                'check_xss': True,
                'check_cookies': True
            },
            'performance': {
                'threshold_good': 90,
                'threshold_acceptable': 70
            }
        }
    }
    
    try:
        # Run the analysis
        results = await summit.analyze(url, analyzers, config)
        
        # Prepare the results for reporting
        timestamp = datetime.now().isoformat()
        report_data = {
            'url': url,
            'timestamp': timestamp,
            'results': results
        }
        
        # Create the reporter with custom configuration
        reporter_config = {
            'include_toc': True,
            'max_issues': 5,
            'include_recommendations': True,
            'include_metadata': True,
            'heading_style': 'hash'
        }
        reporter = ReporterFactory.create('markdown', reporter_config)
        
        # Generate the report
        report_result = await reporter.generate_report(report_data)
        
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a filename based on the domain
        domain = url.replace('https://', '').replace('http://', '').split('/')[0]
        filename = f"{domain.replace('.', '_')}_{timestamp.split('T')[0]}.md"
        filepath = os.path.join(output_dir, filename)
        
        # Save the report
        with open(filepath, 'w') as f:
            f.write(report_result.content)
        
        print(f"Report saved to {filepath}")
        
        return filepath
        
    except Exception as e:
        print(f"Error analyzing {url}: {str(e)}")
        return None


async def batch_analyze_and_report(urls: List[str], output_dir: str = 'reports'):
    """Analyze multiple websites and generate a batch report.
    
    Args:
        urls: List of URLs to analyze
        output_dir: Directory to save the report in
    """
    print(f"Analyzing {len(urls)} websites...")
    
    # Initialize Summit SEO
    summit = SummitSEO()
    
    # Configure which analyzers to use
    analyzers = ['title', 'meta', 'headings', 'security']
    
    # Set up configuration for the analysis
    config = {
        'max_depth': 1,  # Only analyze the homepage for batch processing
        'max_pages': 1,
        'timeout': 20,
    }
    
    all_results = []
    
    try:
        for url in urls:
            print(f"Processing {url}...")
            
            # Run the analysis for this URL
            results = await summit.analyze(url, analyzers, config)
            
            # Add to our collection
            all_results.append({
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'results': results
            })
        
        # Create the reporter
        reporter = ReporterFactory.create('markdown', {
            'include_toc': True,
            'max_issues': 3  # Limit issues in batch report for brevity
        })
        
        # Generate the batch report
        report_result = await reporter.generate_batch_report(all_results)
        
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the batch report
        timestamp = datetime.now().strftime('%Y%m%d')
        filepath = os.path.join(output_dir, f"batch_report_{timestamp}.md")
        
        with open(filepath, 'w') as f:
            f.write(report_result.content)
        
        print(f"Batch report saved to {filepath}")
        return filepath
        
    except Exception as e:
        print(f"Error in batch analysis: {str(e)}")
        return None


async def main():
    """Main function to demonstrate the MarkdownReporter."""
    # Example 1: Single site analysis and report
    await analyze_and_generate_report('https://example.com')
    
    # Example 2: Batch analysis of multiple sites
    urls = [
        'https://example.com',
        'https://example.org',
        'https://example.net'
    ]
    await batch_analyze_and_report(urls)
    
    # Example 3: Custom analysis with specific configuration
    reporter_config = {
        'include_toc': False,
        'heading_style': 'underline',
        'max_issues': 10
    }
    
    # Create the reporter directly (not through factory)
    reporter = MarkdownReporter(reporter_config)
    
    # Create a simple results structure
    simple_results = {
        'url': 'https://mywebsite.com',
        'timestamp': datetime.now().isoformat(),
        'results': {
            'accessibility': {
                'score': 92.5,
                'issues': ['Missing alt text on 2 images'],
                'recommendations': ['Add alt text to all images']
            }
        }
    }
    
    # Generate the report
    result = await reporter.generate_report(simple_results)
    
    # Save to a file
    with open('custom_report.md', 'w') as f:
        f.write(result.content)
    
    print("Custom report generated: custom_report.md")


if __name__ == "__main__":
    asyncio.run(main()) 