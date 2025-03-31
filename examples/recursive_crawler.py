#!/usr/bin/env python3
"""
Recursive Crawler Example for Summit SEO

This example demonstrates how to recursively crawl a website,
analyzing multiple pages and aggregating the results.
"""

import os
import sys
import json
import time
import argparse
from urllib.parse import urlparse, urljoin
from collections import defaultdict

from bs4 import BeautifulSoup
import requests

from summit_seo import SummitSEO
from summit_seo.analyzer import SecurityAnalyzer, PerformanceAnalyzer
from summit_seo.reporter import JSONReporter, HTMLReporter


class RecursiveCrawler:
    """A recursive web crawler that analyzes multiple pages on a website."""
    
    def __init__(
        self,
        start_url,
        output_dir="reports/recursive_crawl",
        max_pages=10,
        max_depth=3,
        verbose=False
    ):
        self.start_url = start_url
        self.output_dir = output_dir
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.verbose = verbose
        
        # Extract domain from start URL
        parsed_url = urlparse(start_url)
        self.base_domain = parsed_url.netloc
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize Summit SEO
        self.summit = SummitSEO()
        
        # Set up tracking variables
        self.visited_urls = set()
        self.queued_urls = set()
        self.url_to_depth = {start_url: 0}
        self.results = {}
        self.all_issues = defaultdict(list)
    
    def _is_same_domain(self, url):
        """Check if a URL belongs to the same domain."""
        parsed_url = urlparse(url)
        return parsed_url.netloc == self.base_domain
    
    def _extract_links(self, html_content, base_url):
        """Extract links from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Skip anchors and javascript links
            if href.startswith('#') or href.startswith('javascript:'):
                continue
                
            # Convert to absolute URL
            absolute_url = urljoin(base_url, href)
            
            # Parse URL and remove fragments
            parsed = urlparse(absolute_url)
            clean_url = parsed._replace(fragment='').geturl()
            
            links.append(clean_url)
        
        return links
    
    def analyze_page(self, url):
        """Analyze a single page with security and performance analyzers."""
        if self.verbose:
            print(f"Analyzing page: {url}")
        
        try:
            # Analyze the page
            results = self.summit.analyze_url(
                url, 
                analyzers=[SecurityAnalyzer(), PerformanceAnalyzer()]
            )
            
            # Extract issues for site-wide aggregation
            for analyzer_name, analyzer_result in results.items():
                if hasattr(analyzer_result, "issues"):
                    for issue in analyzer_result.issues:
                        self.all_issues[analyzer_name].append({
                            "url": url,
                            "issue": issue
                        })
            
            return results
        
        except Exception as e:
            if self.verbose:
                print(f"Error analyzing {url}: {str(e)}")
            return {"error": str(e)}
    
    def crawl(self):
        """Start the recursive crawl from the start URL."""
        # Initialize queue with start URL
        queue = [self.start_url]
        self.queued_urls.add(self.start_url)
        
        while queue and len(self.visited_urls) < self.max_pages:
            # Get next URL from queue
            current_url = queue.pop(0)
            current_depth = self.url_to_depth[current_url]
            
            # Skip if already visited
            if current_url in self.visited_urls:
                continue
                
            if self.verbose:
                print(f"Crawling: {current_url} (depth: {current_depth})")
            
            # Mark as visited
            self.visited_urls.add(current_url)
            
            # Analyze the page
            results = self.analyze_page(current_url)
            self.results[current_url] = results
            
            # Stop crawling if reached max depth
            if current_depth >= self.max_depth:
                continue
                
            # Fetch the page to extract links
            try:
                response = requests.get(current_url, timeout=10)
                if response.status_code == 200:
                    links = self._extract_links(response.text, current_url)
                    
                    # Process each link
                    for link in links:
                        # Skip if already visited or queued
                        if link in self.visited_urls or link in self.queued_urls:
                            continue
                            
                        # Check if link is in the same domain
                        if not self._is_same_domain(link):
                            continue
                            
                        # Add to queue
                        queue.append(link)
                        self.queued_urls.add(link)
                        self.url_to_depth[link] = current_depth + 1
            
            except Exception as e:
                if self.verbose:
                    print(f"Error fetching {current_url}: {str(e)}")
        
        return self.results
    
    def generate_site_report(self):
        """Generate a site-wide report summarizing all pages."""
        if not self.results:
            raise ValueError("No analysis results available. Run crawler first.")
        
        # Generate site summary
        summary = {
            "start_url": self.start_url,
            "base_domain": self.base_domain,
            "pages_analyzed": len(self.results),
            "urls": list(self.results.keys()),
            "common_issues": {}
        }
        
        # Identify common issues
        for analyzer_name, issues in self.all_issues.items():
            # Group issues by type
            issue_count = defaultdict(int)
            for issue_data in issues:
                issue_key = str(issue_data["issue"])
                issue_count[issue_key] += 1
            
            # Sort issues by frequency
            sorted_issues = sorted(
                issue_count.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Add to summary
            summary["common_issues"][analyzer_name] = [
                {
                    "issue": issue,
                    "count": count
                }
                for issue, count in sorted_issues
            ]
        
        # Save JSON report
        json_file = os.path.join(self.output_dir, "site_summary.json")
        with open(json_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        return json_file


def main():
    """Run the recursive crawler example."""
    parser = argparse.ArgumentParser(description="Recursive crawler example")
    parser.add_argument("--url", required=True, help="Starting URL to crawl")
    parser.add_argument("--output-dir", default="examples/output/recursive_crawl")
    parser.add_argument("--max-pages", type=int, default=10)
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    
    # Create the crawler
    crawler = RecursiveCrawler(
        start_url=args.url,
        output_dir=args.output_dir,
        max_pages=args.max_pages,
        max_depth=args.max_depth,
        verbose=args.verbose
    )
    
    # Start crawling
    crawler.crawl()
    
    # Generate site report
    report_file = crawler.generate_site_report()
    
    if args.verbose:
        print(f"Site report generated: {report_file}")


if __name__ == "__main__":
    main() 