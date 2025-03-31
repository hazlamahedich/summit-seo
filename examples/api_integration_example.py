#!/usr/bin/env python3
"""
API Integration Example for Summit SEO

This example demonstrates how to integrate Summit SEO with third-party tools and services
via their APIs. It shows how to combine SEO analysis with other data sources to
create comprehensive reports and automated workflows.

The examples cover:
1. Google Search Console integration
2. Google Analytics integration
3. Ahrefs API integration
4. Moz API integration
5. Custom API wrapper creation
"""

import os
import json
import csv
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from unittest.mock import MagicMock  # For simulating API responses in the example

from summit_seo import SummitSEO
from summit_seo.analyzer import SecurityAnalyzer, PerformanceAnalyzer
from summit_seo.reporter import JSONReporter, HTMLReporter


class GoogleSearchConsoleIntegration:
    """
    Integration with Google Search Console API to combine SEO analysis
    with actual search performance data.
    
    Note: This example uses a mock for the Google API client,
    but in a real implementation, you would use the googleapiclient package.
    """
    
    def __init__(self, site_url: str, credentials_file: Optional[str] = None):
        """
        Initialize the Google Search Console integration.
        
        Args:
            site_url: URL of the site in Google Search Console
            credentials_file: Path to Google API credentials file
        """
        self.site_url = site_url
        self.credentials_file = credentials_file
        
        # In a real implementation, we would initialize the Google API client
        # self.service = self._build_search_console_service()
        
        # Using a mock for example purposes
        self.service = MagicMock()
        self._setup_mock_responses()
        
        # Initialize Summit SEO
        self.summit = SummitSEO()
    
    def _setup_mock_responses(self):
        """Set up mock responses for the example."""
        # Mock response for search analytics query
        self.service.searchanalytics().query().execute.return_value = {
            "rows": [
                {"keys": ["homepage"], "clicks": 1200, "impressions": 5000, "ctr": 0.24, "position": 3.5},
                {"keys": ["products"], "clicks": 800, "impressions": 3500, "ctr": 0.23, "position": 4.2},
                {"keys": ["blog"], "clicks": 600, "impressions": 2800, "ctr": 0.21, "position": 5.0},
            ]
        }
        
        # Mock response for sitemaps list
        self.service.sitemaps().list().execute.return_value = {
            "sitemap": [
                {"path": "https://example.com/sitemap.xml", "lastSubmitted": "2023-03-15T10:00:00Z", "isPending": False},
                {"path": "https://example.com/blog-sitemap.xml", "lastSubmitted": "2023-03-15T10:05:00Z", "isPending": False},
            ]
        }
    
    def _build_search_console_service(self):
        """
        Build and return a Google Search Console service object.
        
        Note: This would be implemented in a real application.
        """
        # This is pseudocode for what would be implemented in a real app
        """
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_file,
            scopes=['https://www.googleapis.com/auth/webmasters']
        )
        
        return build('searchconsole', 'v1', credentials=credentials)
        """
        pass
    
    def get_search_performance(self, days: int = 30, dimensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get search performance data from Google Search Console.
        
        Args:
            days: Number of days to include in report
            dimensions: Dimensions to group by (default: ["page"])
            
        Returns:
            Dictionary with search performance data
        """
        if dimensions is None:
            dimensions = ["page"]
            
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Format dates for API request
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Prepare request
        request = {
            "startDate": start_date_str,
            "endDate": end_date_str,
            "dimensions": dimensions,
            "rowLimit": 500
        }
        
        # Execute request (this would call the real API in production)
        response = self.service.searchanalytics().query(siteUrl=self.site_url, body=request).execute()
        
        return response
    
    def combine_with_seo_analysis(self, pages_to_analyze: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Combine search performance data with SEO analysis.
        
        Args:
            pages_to_analyze: List of pages to analyze (default: top 3 pages by clicks)
            
        Returns:
            Dictionary with combined data
        """
        # Get search performance data
        performance_data = self.get_search_performance(days=30)
        
        # Determine which pages to analyze
        if pages_to_analyze is None:
            # Use top pages by clicks
            pages_to_analyze = [
                f"{self.site_url}/{row['keys'][0]}" if row['keys'][0] != "homepage" else self.site_url
                for row in performance_data.get("rows", [])[:3]
            ]
        
        # Run SEO analysis on each page
        analysis_results = {}
        for page_url in pages_to_analyze:
            analyzers = [SecurityAnalyzer(), PerformanceAnalyzer()]
            page_results = self.summit.analyze_url(page_url, analyzers=analyzers)
            analysis_results[page_url] = page_results
        
        # Combine the data
        combined_data = {
            "search_performance": performance_data,
            "seo_analysis": analysis_results,
            "combined_metrics": self._create_combined_metrics(performance_data, analysis_results)
        }
        
        return combined_data
    
    def _create_combined_metrics(
        self, 
        performance_data: Dict[str, Any], 
        analysis_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Create combined metrics from search performance and SEO analysis.
        
        Args:
            performance_data: Search performance data
            analysis_results: SEO analysis results
            
        Returns:
            Dictionary with combined metrics
        """
        combined_metrics = {}
        
        # Create a lookup for performance data by page
        performance_by_page = {}
        for row in performance_data.get("rows", []):
            page_key = row["keys"][0]
            page_url = f"{self.site_url}/{page_key}" if page_key != "homepage" else self.site_url
            performance_by_page[page_url] = {
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": row.get("ctr", 0),
                "position": row.get("position", 0)
            }
        
        # Combine metrics for each analyzed page
        for page_url, page_analysis in analysis_results.items():
            page_performance = performance_by_page.get(page_url, {})
            
            # Calculate average SEO score
            total_score = 0
            analyzer_count = 0
            
            for analyzer_name, analyzer_result in page_analysis.items():
                if hasattr(analyzer_result, "score"):
                    total_score += analyzer_result.score
                    analyzer_count += 1
            
            avg_score = total_score / analyzer_count if analyzer_count > 0 else 0
            
            # Create combined metrics
            combined_metrics[page_url] = {
                "avg_seo_score": avg_score,
                "search_position": page_performance.get("position", 0),
                "clicks": page_performance.get("clicks", 0),
                "impressions": page_performance.get("impressions", 0),
                "ctr": page_performance.get("ctr", 0),
                "score_to_position_ratio": avg_score / page_performance.get("position", 1) if page_performance.get("position", 0) > 0 else 0,
                "potential_improvement": max(0, 100 - avg_score)
            }
        
        return combined_metrics
    
    def generate_report(self, output_file: str = "gsc_seo_report.html") -> str:
        """
        Generate a combined report with search performance and SEO analysis.
        
        Args:
            output_file: Path to output HTML file
            
        Returns:
            Path to the generated report
        """
        # Get combined data
        data = self.combine_with_seo_analysis()
        
        # In a real implementation, we would use a template engine or the HTMLReporter
        # to generate a nice HTML report. For this example, we'll just create a simple one.
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Combined GSC and SEO Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #4285f4; color: white; padding: 10px; }
                .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .good { color: green; }
                .medium { color: orange; }
                .poor { color: red; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Combined Google Search Console and SEO Analysis Report</h1>
                <p>Generated on {date}</p>
            </div>
            
            <div class="section">
                <h2>Combined Metrics</h2>
                <table>
                    <tr>
                        <th>Page</th>
                        <th>Avg SEO Score</th>
                        <th>Search Position</th>
                        <th>Clicks</th>
                        <th>Impressions</th>
                        <th>CTR</th>
                        <th>Potential Improvement</th>
                    </tr>
        """.format(date=datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        # Add combined metrics
        for page_url, metrics in data["combined_metrics"].items():
            score_class = "good" if metrics["avg_seo_score"] >= 80 else "medium" if metrics["avg_seo_score"] >= 60 else "poor"
            position_class = "good" if metrics["search_position"] <= 3 else "medium" if metrics["search_position"] <= 10 else "poor"
            
            html_content += """
                    <tr>
                        <td>{page_url}</td>
                        <td class="{score_class}">{score:.1f}</td>
                        <td class="{position_class}">{position:.1f}</td>
                        <td>{clicks}</td>
                        <td>{impressions}</td>
                        <td>{ctr:.1%}</td>
                        <td>{improvement:.1f}</td>
                    </tr>
            """.format(
                page_url=page_url,
                score_class=score_class,
                score=metrics["avg_seo_score"],
                position_class=position_class,
                position=metrics["search_position"],
                clicks=metrics["clicks"],
                impressions=metrics["impressions"],
                ctr=metrics["ctr"],
                improvement=metrics["potential_improvement"]
            )
        
        # Close the table and add more sections
        html_content += """
                </table>
            </div>
            
            <!-- More sections would be added here in a real implementation -->
            
        </body>
        </html>
        """
        
        # Write the HTML report
        with open(output_file, "w") as f:
            f.write(html_content)
        
        return output_file


class GoogleAnalyticsIntegration:
    """
    Integration with Google Analytics API to combine SEO analysis
    with user behavior data.
    
    Note: This example uses a mock for the Google Analytics API client,
    but in a real implementation, you would use the google-analytics-data package.
    """
    
    def __init__(self, property_id: str, credentials_file: Optional[str] = None):
        """
        Initialize the Google Analytics integration.
        
        Args:
            property_id: Google Analytics 4 property ID
            credentials_file: Path to Google API credentials file
        """
        self.property_id = property_id
        self.credentials_file = credentials_file
        
        # In a real implementation, we would initialize the Google Analytics API client
        # self.client = self._build_analytics_client()
        
        # Using a mock for example purposes
        self.client = MagicMock()
        self._setup_mock_responses()
        
        # Initialize Summit SEO
        self.summit = SummitSEO()
    
    def _setup_mock_responses(self):
        """Set up mock responses for the example."""
        # Mock response for page view data
        self.client.run_report.return_value = MagicMock(
            rows=[
                MagicMock(
                    dimension_values=[MagicMock(value="/")],
                    metric_values=[
                        MagicMock(value="5000"),  # pageviews
                        MagicMock(value="3.5"),   # avg session duration
                        MagicMock(value="45.2")   # bounce rate
                    ]
                ),
                MagicMock(
                    dimension_values=[MagicMock(value="/products")],
                    metric_values=[
                        MagicMock(value="3500"),  # pageviews
                        MagicMock(value="4.2"),   # avg session duration
                        MagicMock(value="32.1")   # bounce rate
                    ]
                ),
                MagicMock(
                    dimension_values=[MagicMock(value="/blog")],
                    metric_values=[
                        MagicMock(value="2800"),  # pageviews
                        MagicMock(value="5.0"),   # avg session duration
                        MagicMock(value="28.7")   # bounce rate
                    ]
                ),
            ]
        )
    
    def _build_analytics_client(self):
        """
        Build and return a Google Analytics API client.
        
        Note: This would be implemented in a real application.
        """
        # This is pseudocode for what would be implemented in a real app
        """
        from google.oauth2 import service_account
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_file,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        
        return BetaAnalyticsDataClient(credentials=credentials)
        """
        pass
    
    def get_page_metrics(self, days: int = 30, base_url: str = "https://example.com") -> Dict[str, Dict[str, Any]]:
        """
        Get page metrics from Google Analytics.
        
        Args:
            days: Number of days to include in report
            base_url: Base URL to prepend to page paths
            
        Returns:
            Dictionary with page metrics
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Format dates for API request
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # In a real implementation, we would make a proper API request
        # Here we're using the mock response set up earlier
        """
        from google.analytics.data_v1beta.types import (
            DateRange, Dimension, Metric, RunReportRequest
        )
        
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            date_ranges=[DateRange(start_date=start_date_str, end_date=end_date_str)],
            dimensions=[Dimension(name="pagePath")],
            metrics=[
                Metric(name="screenPageViews"),
                Metric(name="averageSessionDuration"),
                Metric(name="bounceRate")
            ],
            limit=500
        )
        
        response = self.client.run_report(request)
        """
        
        # Use mock response instead
        response = self.client.run_report()
        
        # Process response
        page_metrics = {}
        
        for row in response.rows:
            # Get page path
            page_path = row.dimension_values[0].value
            page_url = f"{base_url}{page_path}"
            
            # Get metrics
            pageviews = int(row.metric_values[0].value)
            avg_session_duration = float(row.metric_values[1].value)
            bounce_rate = float(row.metric_values[2].value)
            
            # Store metrics
            page_metrics[page_url] = {
                "pageviews": pageviews,
                "avg_session_duration": avg_session_duration,
                "bounce_rate": bounce_rate
            }
        
        return page_metrics
    
    def combine_with_seo_analysis(self, pages_to_analyze: Optional[List[str]] = None, base_url: str = "https://example.com") -> Dict[str, Any]:
        """
        Combine Google Analytics metrics with SEO analysis.
        
        Args:
            pages_to_analyze: List of pages to analyze (default: top 3 pages by pageviews)
            base_url: Base URL for the site
            
        Returns:
            Dictionary with combined data
        """
        # Get page metrics
        page_metrics = self.get_page_metrics(base_url=base_url)
        
        # Determine which pages to analyze
        if pages_to_analyze is None:
            # Use top pages by pageviews
            pages_to_analyze = sorted(
                page_metrics.keys(),
                key=lambda x: page_metrics[x]["pageviews"],
                reverse=True
            )[:3]
        
        # Run SEO analysis on each page
        analysis_results = {}
        for page_url in pages_to_analyze:
            analyzers = [SecurityAnalyzer(), PerformanceAnalyzer()]
            page_results = self.summit.analyze_url(page_url, analyzers=analyzers)
            analysis_results[page_url] = page_results
        
        # Combine the data
        combined_data = {
            "analytics_metrics": page_metrics,
            "seo_analysis": analysis_results,
            "combined_metrics": self._create_combined_metrics(page_metrics, analysis_results)
        }
        
        return combined_data
    
    def _create_combined_metrics(
        self, 
        page_metrics: Dict[str, Dict[str, Any]], 
        analysis_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Create combined metrics from analytics data and SEO analysis.
        
        Args:
            page_metrics: Google Analytics metrics by page
            analysis_results: SEO analysis results
            
        Returns:
            Dictionary with combined metrics
        """
        combined_metrics = {}
        
        # Combine metrics for each analyzed page
        for page_url, page_analysis in analysis_results.items():
            page_ga_metrics = page_metrics.get(page_url, {})
            
            # Calculate average SEO score
            total_score = 0
            analyzer_count = 0
            
            for analyzer_name, analyzer_result in page_analysis.items():
                if hasattr(analyzer_result, "score"):
                    total_score += analyzer_result.score
                    analyzer_count += 1
            
            avg_score = total_score / analyzer_count if analyzer_count > 0 else 0
            
            # Get performance score if available
            performance_score = 0
            if "PerformanceAnalyzer" in page_analysis and hasattr(page_analysis["PerformanceAnalyzer"], "score"):
                performance_score = page_analysis["PerformanceAnalyzer"].score
            
            # Create combined metrics
            combined_metrics[page_url] = {
                "avg_seo_score": avg_score,
                "performance_score": performance_score,
                "pageviews": page_ga_metrics.get("pageviews", 0),
                "avg_session_duration": page_ga_metrics.get("avg_session_duration", 0),
                "bounce_rate": page_ga_metrics.get("bounce_rate", 0),
                "engagement_index": (
                    page_ga_metrics.get("avg_session_duration", 0) * 
                    (100 - page_ga_metrics.get("bounce_rate", 0)) / 100
                ),
                "performance_engagement_ratio": (
                    performance_score / 
                    page_ga_metrics.get("bounce_rate", 1) 
                    if page_ga_metrics.get("bounce_rate", 0) > 0 else performance_score
                )
            }
        
        return combined_metrics
    
    def export_combined_data_csv(self, output_file: str = "ga_seo_data.csv") -> str:
        """
        Export combined Google Analytics and SEO data to CSV.
        
        Args:
            output_file: Path to output CSV file
            
        Returns:
            Path to the generated CSV file
        """
        # Get combined data
        data = self.combine_with_seo_analysis()
        combined_metrics = data["combined_metrics"]
        
        # Define CSV columns
        columns = [
            "page_url", "avg_seo_score", "performance_score", "pageviews",
            "avg_session_duration", "bounce_rate", "engagement_index",
            "performance_engagement_ratio"
        ]
        
        # Write CSV file
        with open(output_file, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            
            for page_url, metrics in combined_metrics.items():
                row = {
                    "page_url": page_url,
                    "avg_seo_score": metrics["avg_seo_score"],
                    "performance_score": metrics["performance_score"],
                    "pageviews": metrics["pageviews"],
                    "avg_session_duration": metrics["avg_session_duration"],
                    "bounce_rate": metrics["bounce_rate"],
                    "engagement_index": metrics["engagement_index"],
                    "performance_engagement_ratio": metrics["performance_engagement_ratio"]
                }
                writer.writerow(row)
        
        return output_file


class AhrefsApiWrapper:
    """
    Example wrapper for the Ahrefs API to combine with Summit SEO analysis.
    
    Note: This is a simulated wrapper since actual API access requires a paid Ahrefs account.
    In a real implementation, you would use the Ahrefs API documentation to make proper requests.
    """
    
    def __init__(self, api_token: str):
        """
        Initialize the Ahrefs API wrapper.
        
        Args:
            api_token: Ahrefs API token
        """
        self.api_token = api_token
        self.base_url = "https://apiv2.ahrefs.com"
        
        # Using mock data for the example
        self._mock_data = self._get_mock_data()
        
        # Initialize Summit SEO
        self.summit = SummitSEO()
    
    def _get_mock_data(self) -> Dict[str, Any]:
        """Get mock data for the example."""
        return {
            "backlinks": {
                "pages": {
                    "count": 1500,
                    "items": [
                        {"url": "https://example.com/", "backlinks": 800, "referring_domains": 150},
                        {"url": "https://example.com/products", "backlinks": 450, "referring_domains": 85},
                        {"url": "https://example.com/blog", "backlinks": 250, "referring_domains": 60},
                    ]
                }
            },
            "keywords": {
                "organic": {
                    "count": 1200,
                    "items": [
                        {"keyword": "example product", "position": 3, "search_volume": 5000, "traffic": 800},
                        {"keyword": "example guide", "position": 5, "search_volume": 3000, "traffic": 350},
                        {"keyword": "example tutorial", "position": 7, "search_volume": 2000, "traffic": 180},
                    ]
                }
            }
        }
    
    def get_backlinks(self, target: str) -> Dict[str, Any]:
        """
        Get backlink data for a target URL.
        
        Args:
            target: Target URL to analyze
            
        Returns:
            Dictionary with backlink data
        """
        # In a real implementation, this would make an API request to Ahrefs
        # For the example, we return mock data
        return self._mock_data["backlinks"]
    
    def get_organic_keywords(self, target: str) -> Dict[str, Any]:
        """
        Get organic keyword data for a target URL.
        
        Args:
            target: Target URL to analyze
            
        Returns:
            Dictionary with organic keyword data
        """
        # In a real implementation, this would make an API request to Ahrefs
        # For the example, we return mock data
        return self._mock_data["keywords"]
    
    def combine_with_seo_analysis(self, target: str) -> Dict[str, Any]:
        """
        Combine Ahrefs data with SEO analysis.
        
        Args:
            target: Target URL to analyze
            
        Returns:
            Dictionary with combined data
        """
        # Get backlink and keyword data
        backlinks_data = self.get_backlinks(target)
        keywords_data = self.get_organic_keywords(target)
        
        # Run SEO analysis
        analyzers = [SecurityAnalyzer(), PerformanceAnalyzer()]
        seo_results = self.summit.analyze_url(target, analyzers=analyzers)
        
        # Get average SEO score
        total_score = 0
        analyzer_count = 0
        
        for analyzer_name, analyzer_result in seo_results.items():
            if hasattr(analyzer_result, "score"):
                total_score += analyzer_result.score
                analyzer_count += 1
        
        avg_score = total_score / analyzer_count if analyzer_count > 0 else 0
        
        # Combine the data
        combined_data = {
            "target_url": target,
            "avg_seo_score": avg_score,
            "backlinks_count": sum(item["backlinks"] for item in backlinks_data["pages"]["items"]),
            "referring_domains_count": sum(item["referring_domains"] for item in backlinks_data["pages"]["items"]),
            "organic_keywords_count": keywords_data["organic"]["count"],
            "top_keywords": keywords_data["organic"]["items"],
            "estimated_organic_traffic": sum(item["traffic"] for item in keywords_data["organic"]["items"]),
            "seo_analysis": seo_results,
            "backlinks_data": backlinks_data,
            "keywords_data": keywords_data
        }
        
        return combined_data
    
    def generate_report(self, target: str, output_file: str = "ahrefs_seo_report.json") -> str:
        """
        Generate a combined report with Ahrefs data and SEO analysis.
        
        Args:
            target: Target URL to analyze
            output_file: Path to output JSON file
            
        Returns:
            Path to the generated report
        """
        # Get combined data
        data = self.combine_with_seo_analysis(target)
        
        # Write JSON report
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        
        return output_file


def create_api_integration_example():
    """Example of various API integrations with Summit SEO."""
    # Create output directory
    os.makedirs("examples/output/api_integration", exist_ok=True)
    
    # Example 1: Google Search Console integration
    print("1. Running Google Search Console integration example...")
    gsc_integration = GoogleSearchConsoleIntegration("https://example.com")
    gsc_report_path = gsc_integration.generate_report("examples/output/api_integration/gsc_seo_report.html")
    print(f"  - GSC integration report generated: {gsc_report_path}")
    
    # Example 2: Google Analytics integration
    print("2. Running Google Analytics integration example...")
    ga_integration = GoogleAnalyticsIntegration("GA4-12345678")
    ga_csv_path = ga_integration.export_combined_data_csv("examples/output/api_integration/ga_seo_data.csv")
    print(f"  - GA integration data exported: {ga_csv_path}")
    
    # Example 3: Ahrefs API integration
    print("3. Running Ahrefs API integration example...")
    ahrefs_wrapper = AhrefsApiWrapper("example_token")
    ahrefs_report_path = ahrefs_wrapper.generate_report(
        "https://example.com",
        "examples/output/api_integration/ahrefs_seo_report.json"
    )
    print(f"  - Ahrefs integration report generated: {ahrefs_report_path}")
    
    print("\nAll API integration examples completed.")


if __name__ == "__main__":
    create_api_integration_example() 