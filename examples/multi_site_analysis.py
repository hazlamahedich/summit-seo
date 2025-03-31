#!/usr/bin/env python3
"""
Multi-Site Analysis Example for Summit SEO

This example demonstrates how to analyze multiple websites in batch mode,
efficiently processing multiple sites while optimizing resource usage.

The example includes:
1. Simple multi-site analysis with sequential processing
2. Parallel multi-site analysis using ProcessPoolExecutor
3. Advanced configuration with site-specific analyzer settings
4. Aggregating results across multiple sites
5. Comparative reporting between sites
"""

import os
import sys
import json
import time
import argparse
import csv
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed

from summit_seo import SummitSEO
from summit_seo.analyzer import (
    SecurityAnalyzer,
    PerformanceAnalyzer,
    AccessibilityAnalyzer,
    MobileFriendlyAnalyzer,
    SchemaAnalyzer
)
from summit_seo.reporter import JSONReporter, HTMLReporter
from summit_seo.parallel import ParallelManager


class MultiSiteAnalyzer:
    """
    Utility class for analyzing multiple websites and comparing results.
    """
    
    def __init__(
        self,
        sites: List[str],
        output_dir: str = "reports/multi_site",
        analyzers: Optional[List[str]] = None,
        parallel: bool = True,
        max_workers: int = None,
        verbose: bool = False
    ):
        """
        Initialize the multi-site analyzer.
        
        Args:
            sites: List of URLs to analyze
            output_dir: Directory to store output reports
            analyzers: List of analyzers to run (runs selected set if None)
            parallel: Whether to run analysis in parallel
            max_workers: Maximum number of worker processes (None = auto)
            verbose: Whether to print verbose output
        """
        self.sites = sites
        self.output_dir = output_dir
        self.analyzers = analyzers or ["security", "performance", "accessibility"]
        self.parallel = parallel
        self.max_workers = max_workers
        self.verbose = verbose
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize Summit SEO
        self.summit = SummitSEO()
        
        # Store results
        self.results = {}
    
    def get_analyzer_instances(self) -> List[Any]:
        """
        Get the analyzer instances to use for all sites.
        
        Returns:
            List of analyzer instances
        """
        analyzer_instances = []
        
        if "security" in self.analyzers:
            analyzer_instances.append(SecurityAnalyzer())
        if "performance" in self.analyzers:
            analyzer_instances.append(PerformanceAnalyzer())
        if "accessibility" in self.analyzers:
            analyzer_instances.append(AccessibilityAnalyzer())
        if "mobile_friendly" in self.analyzers:
            analyzer_instances.append(MobileFriendlyAnalyzer())
        if "schema" in self.analyzers:
            analyzer_instances.append(SchemaAnalyzer())
            
        return analyzer_instances
    
    def analyze_site(self, site_url: str) -> Dict[str, Any]:
        """
        Analyze a single site with all configured analyzers.
        
        Args:
            site_url: URL of the site to analyze
            
        Returns:
            Analysis results for the site
        """
        if self.verbose:
            print(f"Starting analysis of {site_url}")
            start_time = time.time()
        
        analyzer_instances = self.get_analyzer_instances()
        
        try:
            # Use parallel processing for analyzers if enabled
            if self.parallel:
                parallel_manager = ParallelManager(max_workers=len(analyzer_instances))
                results = self.summit.analyze_url(
                    site_url, 
                    analyzers=analyzer_instances,
                    parallel_manager=parallel_manager
                )
            else:
                results = self.summit.analyze_url(site_url, analyzers=analyzer_instances)
                
            # Save individual site report
            self._save_site_report(site_url, results)
            
            if self.verbose:
                duration = time.time() - start_time
                print(f"Completed analysis of {site_url} in {duration:.2f} seconds")
            
            return results
        
        except Exception as e:
            if self.verbose:
                print(f"Error analyzing {site_url}: {str(e)}")
            return {"error": str(e)}
    
    def analyze_all_sites_sequential(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze all sites sequentially.
        
        Returns:
            Dictionary mapping site URLs to their analysis results
        """
        results = {}
        
        if self.verbose:
            print(f"Starting sequential analysis of {len(self.sites)} sites")
            start_time = time.time()
        
        for site_url in self.sites:
            results[site_url] = self.analyze_site(site_url)
        
        if self.verbose:
            duration = time.time() - start_time
            print(f"Completed analysis of {len(self.sites)} sites in {duration:.2f} seconds")
        
        self.results = results
        return results
    
    def analyze_all_sites_parallel(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze all sites in parallel using ProcessPoolExecutor.
        
        Returns:
            Dictionary mapping site URLs to their analysis results
        """
        results = {}
        
        if self.verbose:
            print(f"Starting parallel analysis of {len(self.sites)} sites")
            start_time = time.time()
        
        # Determine number of workers (default to min(len(sites), cpu_count))
        workers = self.max_workers or min(len(self.sites), os.cpu_count() or 1)
        
        with ProcessPoolExecutor(max_workers=workers) as executor:
            # Submit all tasks
            future_to_site = {
                executor.submit(self.analyze_site, site_url): site_url
                for site_url in self.sites
            }
            
            # Process results as they complete
            for future in as_completed(future_to_site):
                site_url = future_to_site[future]
                try:
                    results[site_url] = future.result()
                except Exception as e:
                    if self.verbose:
                        print(f"Error analyzing {site_url}: {str(e)}")
                    results[site_url] = {"error": str(e)}
        
        if self.verbose:
            duration = time.time() - start_time
            print(f"Completed parallel analysis of {len(self.sites)} sites in {duration:.2f} seconds")
        
        self.results = results
        return results
    
    def run_analysis(self) -> Dict[str, Dict[str, Any]]:
        """
        Run analysis on all sites using the configured method.
        
        Returns:
            Dictionary mapping site URLs to their analysis results
        """
        if self.parallel and len(self.sites) > 1:
            return self.analyze_all_sites_parallel()
        else:
            return self.analyze_all_sites_sequential()
    
    def _save_site_report(self, site_url: str, results: Dict[str, Any]) -> None:
        """
        Save individual site report.
        
        Args:
            site_url: URL of the site
            results: Analysis results for the site
        """
        # Create a safe filename from the URL
        safe_name = "".join(c if c.isalnum() else "_" for c in site_url)
        
        # Save JSON report
        json_file = os.path.join(self.output_dir, f"{safe_name}.json")
        json_reporter = JSONReporter(output_file=json_file)
        json_reporter.generate_report(results)
        
        # Save HTML report
        html_file = os.path.join(self.output_dir, f"{safe_name}.html")
        html_reporter = HTMLReporter(output_file=html_file)
        html_reporter.generate_report(results)
    
    def generate_comparative_report(self) -> str:
        """
        Generate a comparative report for all analyzed sites.
        
        Returns:
            Path to the generated report
        """
        if not self.results:
            raise ValueError("No analysis results available. Run analysis first.")
        
        # Prepare data for the report
        report_data = self._prepare_comparative_data()
        
        # Generate HTML report
        report_file = os.path.join(self.output_dir, "comparative_report.html")
        self._generate_html_comparative_report(report_data, report_file)
        
        # Generate CSV report
        csv_file = os.path.join(self.output_dir, "comparative_report.csv")
        self._generate_csv_comparative_report(report_data, csv_file)
        
        return report_file
    
    def _prepare_comparative_data(self) -> Dict[str, Any]:
        """
        Prepare data for comparative reporting.
        
        Returns:
            Dictionary with comparative data
        """
        comparative_data = {
            "sites": list(self.results.keys()),
            "timestamp": datetime.now().isoformat(),
            "analyzer_scores": {},
            "overall_scores": {},
            "rankings": {},
            "summary": {}
        }
        
        # Extract scores for each analyzer and site
        for site_url, site_results in self.results.items():
            if "error" in site_results:
                # Skip sites with errors
                continue
                
            for analyzer_name, analyzer_result in site_results.items():
                if hasattr(analyzer_result, "score"):
                    # Add analyzer to comparative data if not already present
                    if analyzer_name not in comparative_data["analyzer_scores"]:
                        comparative_data["analyzer_scores"][analyzer_name] = {}
                    
                    # Add score to comparative data
                    comparative_data["analyzer_scores"][analyzer_name][site_url] = analyzer_result.score
        
        # Calculate overall scores
        for site_url, site_results in self.results.items():
            if "error" in site_results:
                comparative_data["overall_scores"][site_url] = 0
                continue
                
            total_score = 0
            count = 0
            
            for analyzer_name, analyzer_result in site_results.items():
                if hasattr(analyzer_result, "score"):
                    total_score += analyzer_result.score
                    count += 1
            
            if count > 0:
                comparative_data["overall_scores"][site_url] = total_score / count
            else:
                comparative_data["overall_scores"][site_url] = 0
        
        # Create rankings for each analyzer
        for analyzer_name, scores in comparative_data["analyzer_scores"].items():
            # Sort sites by score (descending)
            sorted_sites = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            
            # Add rankings
            if analyzer_name not in comparative_data["rankings"]:
                comparative_data["rankings"][analyzer_name] = {}
                
            for rank, (site_url, score) in enumerate(sorted_sites, 1):
                comparative_data["rankings"][analyzer_name][site_url] = rank
        
        # Create overall rankings
        sorted_overall = sorted(
            comparative_data["overall_scores"].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        comparative_data["rankings"]["overall"] = {}
        for rank, (site_url, score) in enumerate(sorted_overall, 1):
            comparative_data["rankings"]["overall"][site_url] = rank
        
        # Create summary statistics
        comparative_data["summary"] = {
            "best_overall": sorted_overall[0][0] if sorted_overall else None,
            "worst_overall": sorted_overall[-1][0] if sorted_overall else None,
            "average_scores": {},
            "score_ranges": {}
        }
        
        # Calculate average scores and ranges for each analyzer
        for analyzer_name, scores in comparative_data["analyzer_scores"].items():
            score_values = list(scores.values())
            if score_values:
                comparative_data["summary"]["average_scores"][analyzer_name] = sum(score_values) / len(score_values)
                comparative_data["summary"]["score_ranges"][analyzer_name] = {
                    "min": min(score_values),
                    "max": max(score_values)
                }
        
        return comparative_data
    
    def _generate_html_comparative_report(self, data: Dict[str, Any], output_file: str) -> None:
        """
        Generate HTML comparative report.
        
        Args:
            data: Comparative data
            output_file: Path to output file
        """
        # Basic HTML template
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Multi-Site SEO Analysis Comparison</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .good {{ background-color: #dff0d8; }}
                .medium {{ background-color: #fcf8e3; }}
                .poor {{ background-color: #f2dede; }}
                .rank-1 {{ font-weight: bold; color: green; }}
                .error {{ background-color: #f2dede; color: #a94442; }}
                .summary {{ margin: 20px 0; padding: 15px; background-color: #f9f9f9; border: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <h1>Multi-Site SEO Analysis Comparison</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Best Overall Site:</strong> {data['summary']['best_overall'] if data['summary']['best_overall'] else 'N/A'}</p>
                <p><strong>Worst Overall Site:</strong> {data['summary']['worst_overall'] if data['summary']['worst_overall'] else 'N/A'}</p>
            </div>
            
            <h2>Overall Scores</h2>
            <table>
                <tr>
                    <th>Site</th>
                    <th>Overall Score</th>
                    <th>Ranking</th>
                </tr>
        """
        
        # Add overall scores
        for site_url, score in sorted(data["overall_scores"].items(), key=lambda x: x[1], reverse=True):
            rank = data["rankings"]["overall"].get(site_url, "N/A")
            score_class = "good" if score >= 80 else "medium" if score >= 60 else "poor"
            rank_class = f"rank-{rank}" if rank == 1 else ""
            
            html += f"""
                <tr>
                    <td>{site_url}</td>
                    <td class="{score_class}">{score:.1f}</td>
                    <td class="{rank_class}">{rank}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <h2>Analyzer Scores</h2>
        """
        
        # Add analyzer scores
        for analyzer_name, scores in data["analyzer_scores"].items():
            html += f"""
            <h3>{analyzer_name}</h3>
            <table>
                <tr>
                    <th>Site</th>
                    <th>Score</th>
                    <th>Ranking</th>
                </tr>
            """
            
            for site_url, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
                rank = data["rankings"][analyzer_name].get(site_url, "N/A")
                score_class = "good" if score >= 80 else "medium" if score >= 60 else "poor"
                rank_class = f"rank-{rank}" if rank == 1 else ""
                
                html += f"""
                <tr>
                    <td>{site_url}</td>
                    <td class="{score_class}">{score:.1f}</td>
                    <td class="{rank_class}">{rank}</td>
                </tr>
                """
            
            html += """
            </table>
            """
        
        html += """
        </body>
        </html>
        """
        
        # Write HTML file
        with open(output_file, "w") as f:
            f.write(html)
    
    def _generate_csv_comparative_report(self, data: Dict[str, Any], output_file: str) -> None:
        """
        Generate CSV comparative report.
        
        Args:
            data: Comparative data
            output_file: Path to output file
        """
        # Prepare CSV rows
        rows = []
        
        # Create header row
        header = ["Site", "Overall Score", "Overall Ranking"]
        for analyzer_name in data["analyzer_scores"].keys():
            header.extend([f"{analyzer_name} Score", f"{analyzer_name} Ranking"])
        
        rows.append(header)
        
        # Add data rows
        for site_url in data["sites"]:
            row = [
                site_url,
                f"{data['overall_scores'].get(site_url, 0):.1f}",
                str(data["rankings"]["overall"].get(site_url, "N/A"))
            ]
            
            for analyzer_name in data["analyzer_scores"].keys():
                score = data["analyzer_scores"][analyzer_name].get(site_url, 0)
                rank = data["rankings"][analyzer_name].get(site_url, "N/A")
                row.extend([f"{score:.1f}", str(rank)])
            
            rows.append(row)
        
        # Write CSV file
        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
    
    def export_results_json(self, output_file: str = None) -> str:
        """
        Export all results to a JSON file.
        
        Args:
            output_file: Path to output file (default: results.json in output_dir)
            
        Returns:
            Path to the generated file
        """
        if not output_file:
            output_file = os.path.join(self.output_dir, "results.json")
        
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        return output_file


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Multi-site SEO analysis example")
    parser.add_argument(
        "--sites", 
        nargs="+", 
        help="List of sites to analyze",
        default=["https://example.com", "https://example.org", "https://example.net"]
    )
    parser.add_argument(
        "--output-dir", 
        help="Output directory for reports",
        default="examples/output/multi_site"
    )
    parser.add_argument(
        "--analyzers",
        nargs="+",
        choices=["security", "performance", "accessibility", "mobile_friendly", "schema"],
        help="Analyzers to run",
        default=["security", "performance", "accessibility"]
    )
    parser.add_argument(
        "--no-parallel", 
        action="store_true",
        help="Disable parallel processing"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        help="Maximum number of worker processes",
        default=None
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )
    return parser.parse_args()


def main():
    """Run the multi-site analysis example."""
    args = parse_args()
    
    # Create the multi-site analyzer
    analyzer = MultiSiteAnalyzer(
        sites=args.sites,
        output_dir=args.output_dir,
        analyzers=args.analyzers,
        parallel=not args.no_parallel,
        max_workers=args.max_workers,
        verbose=args.verbose
    )
    
    # Run the analysis
    analyzer.run_analysis()
    
    # Generate comparative report
    report_file = analyzer.generate_comparative_report()
    
    # Export results to JSON
    json_file = analyzer.export_results_json()
    
    if args.verbose:
        print(f"Comparative report generated: {report_file}")
        print(f"JSON results exported: {json_file}")


if __name__ == "__main__":
    main() 