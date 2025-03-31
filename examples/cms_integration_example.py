#!/usr/bin/env python3
"""
CMS Integration Example for Summit SEO

This example demonstrates how to integrate Summit SEO with different Content Management Systems (CMS)
to enable SEO analysis directly within your CMS workflow. 

The examples cover:
1. WordPress integration via a plugin
2. Drupal integration via a module
3. Django CMS integration
4. Headless CMS integration (Contentful)

This file provides the core code that would be used in such integrations,
along with explanations of how to implement them in practice.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from summit_seo import SummitSEO
from summit_seo.analyzer import (
    SecurityAnalyzer,
    PerformanceAnalyzer,
    MobileFriendlyAnalyzer,
    AccessibilityAnalyzer,
    SchemaAnalyzer,
    SocialMediaAnalyzer,
)
from summit_seo.reporter import JSONReporter, HTMLReporter


class CMSIntegrationBase:
    """
    Base class for CMS integrations with Summit SEO.
    
    This class provides common functionality that would be needed
    across different CMS integrations, such as analysis runners,
    report generators, and data transformers.
    """
    
    def __init__(
        self,
        output_dir: str = "reports",
        save_reports: bool = True,
        analyzers: Optional[List[str]] = None
    ):
        """
        Initialize the CMS integration.
        
        Args:
            output_dir: Directory to store output reports
            save_reports: Whether to save reports to disk
            analyzers: List of analyzers to run (runs all if None)
        """
        self.output_dir = output_dir
        self.save_reports = save_reports
        self.analyzers = analyzers or [
            "security",
            "performance",
            "mobile_friendly",
            "accessibility",
            "schema",
            "social_media"
        ]
        
        # Create output directory if needed
        if save_reports:
            os.makedirs(output_dir, exist_ok=True)
        
        # Initialize Summit SEO
        self.summit = SummitSEO()
    
    def get_analyzer_instances(self) -> List[Any]:
        """
        Get the analyzer instances based on configured analyzers.
        
        Returns:
            List of analyzer instances
        """
        analyzer_instances = []
        
        if "security" in self.analyzers:
            analyzer_instances.append(SecurityAnalyzer())
        if "performance" in self.analyzers:
            analyzer_instances.append(PerformanceAnalyzer())
        if "mobile_friendly" in self.analyzers:
            analyzer_instances.append(MobileFriendlyAnalyzer())
        if "accessibility" in self.analyzers:
            analyzer_instances.append(AccessibilityAnalyzer())
        if "schema" in self.analyzers:
            analyzer_instances.append(SchemaAnalyzer())
        if "social_media" in self.analyzers:
            analyzer_instances.append(SocialMediaAnalyzer())
            
        return analyzer_instances
    
    def analyze_url(self, url: str) -> Dict[str, Any]:
        """
        Run analysis on a given URL.
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary with analysis results
        """
        analyzer_instances = self.get_analyzer_instances()
        results = self.summit.analyze_url(url, analyzers=analyzer_instances)
        
        if self.save_reports:
            self._save_reports(url, results)
        
        return results
    
    def analyze_content(self, content: str, base_url: str = "https://example.com") -> Dict[str, Any]:
        """
        Analyze raw HTML content.
        
        This is useful for CMS integrations that want to analyze content
        before it's published, or for headless CMS systems.
        
        Args:
            content: HTML content to analyze
            base_url: Base URL to use for relative links
            
        Returns:
            Dictionary with analysis results
        """
        analyzer_instances = self.get_analyzer_instances()
        results = self.summit.analyze_html(content, base_url=base_url, analyzers=analyzer_instances)
        
        if self.save_reports:
            timestamp = int(time.time())
            report_name = f"content_analysis_{timestamp}"
            self._save_reports(report_name, results)
        
        return results
    
    def _save_reports(self, identifier: str, results: Dict[str, Any]) -> None:
        """
        Save analysis results as reports.
        
        Args:
            identifier: URL or identifier for the report
            results: Analysis results to save
        """
        # Create a safe filename
        safe_id = "".join(c if c.isalnum() else "_" for c in str(identifier))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_base = f"{safe_id}_{timestamp}"
        
        # Generate JSON report
        json_reporter = JSONReporter(
            output_file=os.path.join(self.output_dir, f"{filename_base}.json")
        )
        json_reporter.generate_report(results)
        
        # Generate HTML report
        html_reporter = HTMLReporter(
            output_file=os.path.join(self.output_dir, f"{filename_base}.html")
        )
        html_reporter.generate_report(results)
    
    def format_results_for_cms(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform analysis results into a format suitable for CMS display.
        
        Args:
            results: Raw analysis results
            
        Returns:
            CMS-friendly result format with summary and recommendations
        """
        cms_results = {
            "summary": {
                "scores": {},
                "overall_score": 0,
                "timestamp": datetime.now().isoformat(),
                "total_issues": 0,
                "critical_issues": 0,
                "warning_issues": 0,
                "info_issues": 0,
            },
            "recommendations": [],
            "detailed_results": {}
        }
        
        # Process each analyzer's results
        total_score = 0
        analyzer_count = 0
        
        for analyzer_name, analyzer_result in results.items():
            if hasattr(analyzer_result, "score"):
                # Add score to summary
                score = analyzer_result.score
                cms_results["summary"]["scores"][analyzer_name] = score
                total_score += score
                analyzer_count += 1
                
                # Add detailed results
                cms_results["detailed_results"][analyzer_name] = {
                    "score": score,
                    "issues": []
                }
                
                # Process issues and recommendations
                if hasattr(analyzer_result, "issues"):
                    for issue in analyzer_result.issues:
                        issue_data = {
                            "severity": getattr(issue, "severity", "info"),
                            "message": getattr(issue, "message", ""),
                            "remediation": getattr(issue, "remediation", ""),
                            "impact": getattr(issue, "impact", ""),
                            "location": getattr(issue, "location", ""),
                        }
                        
                        # Add to overall issue counts
                        cms_results["summary"]["total_issues"] += 1
                        severity = issue_data["severity"].lower()
                        if severity == "critical":
                            cms_results["summary"]["critical_issues"] += 1
                        elif severity in ["high", "warning"]:
                            cms_results["summary"]["warning_issues"] += 1
                        else:
                            cms_results["summary"]["info_issues"] += 1
                        
                        # Add to detailed results
                        cms_results["detailed_results"][analyzer_name]["issues"].append(issue_data)
                        
                        # Add as recommendation if it has remediation steps
                        if issue_data["remediation"]:
                            cms_results["recommendations"].append({
                                "analyzer": analyzer_name,
                                "severity": issue_data["severity"],
                                "message": issue_data["message"],
                                "remediation": issue_data["remediation"],
                            })
        
        # Calculate overall score
        if analyzer_count > 0:
            cms_results["summary"]["overall_score"] = total_score / analyzer_count
            
        # Sort recommendations by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        cms_results["recommendations"].sort(
            key=lambda x: severity_order.get(x["severity"].lower(), 999)
        )
            
        return cms_results


class WordPressIntegration(CMSIntegrationBase):
    """
    WordPress-specific integration for Summit SEO.
    
    This class provides methods that would be used in a WordPress plugin
    to analyze content and present results within the WordPress admin interface.
    """
    
    def analyze_post_preview(self, post_id: int, post_content: str, post_url: str) -> Dict[str, Any]:
        """
        Analyze a WordPress post before it's published.
        
        Args:
            post_id: WordPress post ID
            post_content: HTML content of the post
            post_url: URL where the post will be published
            
        Returns:
            Analysis results formatted for WordPress
        """
        # In a real WordPress plugin, we'd get content from the database
        # or via WordPress hooks, but for this example we use parameters
        
        # Run analysis on the content
        results = self.analyze_content(post_content, base_url=post_url)
        
        # Format results for WordPress admin display
        wp_results = self.format_results_for_cms(results)
        
        # Add WordPress-specific metadata
        wp_results["wordpress"] = {
            "post_id": post_id,
            "report_url": f"{self.output_dir}/post_{post_id}_latest.html",
        }
        
        return wp_results
    
    def get_wordpress_dashboard_widget_data(self, site_url: str) -> Dict[str, Any]:
        """
        Get data for a WordPress dashboard widget showing SEO status.
        
        Args:
            site_url: URL of the WordPress site
            
        Returns:
            Data formatted for a WordPress dashboard widget
        """
        # Analyze the homepage
        results = self.analyze_url(site_url)
        cms_results = self.format_results_for_cms(results)
        
        # Create widget-specific format
        widget_data = {
            "overall_score": cms_results["summary"]["overall_score"],
            "scores": cms_results["summary"]["scores"],
            "critical_issues": cms_results["summary"]["critical_issues"],
            "top_recommendations": cms_results["recommendations"][:5],
            "last_updated": datetime.now().isoformat(),
        }
        
        return widget_data


class DrupalIntegration(CMSIntegrationBase):
    """
    Drupal-specific integration for Summit SEO.
    
    This class provides methods that would be used in a Drupal module
    to analyze content and present results within the Drupal admin interface.
    """
    
    def analyze_node(self, node_id: int, node_content: str, node_url: str) -> Dict[str, Any]:
        """
        Analyze a Drupal node before it's published.
        
        Args:
            node_id: Drupal node ID
            node_content: HTML content of the node
            node_url: URL where the node will be published
            
        Returns:
            Analysis results formatted for Drupal
        """
        # Run analysis on the content
        results = self.analyze_content(node_content, base_url=node_url)
        
        # Format results for Drupal admin display
        drupal_results = self.format_results_for_cms(results)
        
        # Add Drupal-specific metadata
        drupal_results["drupal"] = {
            "node_id": node_id,
            "report_url": f"{self.output_dir}/node_{node_id}_latest.html",
        }
        
        return drupal_results
    
    def get_drupal_block_data(self, site_url: str) -> Dict[str, Any]:
        """
        Get data for a Drupal block showing SEO status.
        
        Args:
            site_url: URL of the Drupal site
            
        Returns:
            Data formatted for a Drupal block
        """
        # Analyze the homepage
        results = self.analyze_url(site_url)
        cms_results = self.format_results_for_cms(results)
        
        # Create block-specific format
        block_data = {
            "overall_score": cms_results["summary"]["overall_score"],
            "scores": cms_results["summary"]["scores"],
            "critical_issues": cms_results["summary"]["critical_issues"],
            "top_recommendations": cms_results["recommendations"][:5],
            "last_updated": datetime.now().isoformat(),
        }
        
        return block_data


class DjangoCMSIntegration(CMSIntegrationBase):
    """
    Django CMS-specific integration for Summit SEO.
    
    This class demonstrates how Summit SEO could be integrated with Django CMS.
    """
    
    def analyze_page(self, page_id: int, page_content: str, page_url: str) -> Dict[str, Any]:
        """
        Analyze a Django CMS page.
        
        Args:
            page_id: Django CMS page ID
            page_content: HTML content of the page
            page_url: URL of the page
            
        Returns:
            Analysis results formatted for Django CMS
        """
        # Run analysis on the content
        results = self.analyze_content(page_content, base_url=page_url)
        
        # Format results for Django CMS admin display
        django_results = self.format_results_for_cms(results)
        
        # Add Django CMS-specific metadata
        django_results["django_cms"] = {
            "page_id": page_id,
            "report_url": f"{self.output_dir}/page_{page_id}_latest.html",
        }
        
        return django_results
    
    def get_admin_extension_data(self, site_url: str) -> Dict[str, Any]:
        """
        Get data for a Django CMS admin extension showing SEO status.
        
        Args:
            site_url: URL of the Django CMS site
            
        Returns:
            Data formatted for a Django CMS admin extension
        """
        # Analyze the homepage
        results = self.analyze_url(site_url)
        django_results = self.format_results_for_cms(results)
        
        return django_results


class HeadlessCMSIntegration(CMSIntegrationBase):
    """
    Integration example for headless CMS platforms like Contentful.
    
    This class demonstrates how Summit SEO could be integrated with
    headless CMS systems through their APIs.
    """
    
    def analyze_entry_preview(self, entry_id: str, rendered_html: str, preview_url: str) -> Dict[str, Any]:
        """
        Analyze a headless CMS entry preview.
        
        Args:
            entry_id: Entry ID in the headless CMS
            rendered_html: HTML content rendered from the entry data
            preview_url: URL of the preview
            
        Returns:
            Analysis results
        """
        # Run analysis on the rendered content
        results = self.analyze_content(rendered_html, base_url=preview_url)
        
        # Format results for display in the headless CMS interface
        cms_results = self.format_results_for_cms(results)
        
        # Add headless CMS-specific metadata
        cms_results["headless_cms"] = {
            "entry_id": entry_id,
            "report_url": f"{self.output_dir}/entry_{entry_id}_latest.html",
        }
        
        return cms_results


def wordpress_plugin_example():
    """Example usage of WordPress integration."""
    # This simulates functionality that would be in a WordPress plugin
    wp_integration = WordPressIntegration(output_dir="reports/wordpress")
    
    # Simulate a WordPress post being previewed
    post_id = 123
    post_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Example WordPress Post</title>
        <meta name="description" content="This is an example post for SEO analysis">
    </head>
    <body>
        <h1>Example WordPress Post</h1>
        <p>This is a sample post that would be analyzed for SEO.</p>
        <img src="example.jpg">
    </body>
    </html>
    """
    post_url = "https://example.com/sample-post"
    
    # Analyze the post
    results = wp_integration.analyze_post_preview(post_id, post_content, post_url)
    
    # In a real plugin, we'd display these results in the WordPress editor
    print("WordPress Plugin Example Results:")
    print(f"Overall Score: {results['summary']['overall_score']:.1f}/100")
    print(f"Critical Issues: {results['summary']['critical_issues']}")
    
    if results['recommendations']:
        print("\nTop Recommendation:")
        top_rec = results['recommendations'][0]
        print(f"- {top_rec['message']}")
        print(f"  Remediation: {top_rec['remediation']}")
    
    # Also get dashboard widget data
    widget_data = wp_integration.get_wordpress_dashboard_widget_data("https://example.com")
    
    # Save results for demonstration
    with open("examples/output/wordpress_results.json", "w") as f:
        json.dump(results, f, indent=2)


def drupal_module_example():
    """Example usage of Drupal integration."""
    # This simulates functionality that would be in a Drupal module
    drupal_integration = DrupalIntegration(output_dir="reports/drupal")
    
    # Simulate a Drupal node being edited
    node_id = 456
    node_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Example Drupal Node</title>
        <meta name="description" content="This is an example node for SEO analysis">
    </head>
    <body>
        <h1>Example Drupal Node</h1>
        <p>This is a sample node that would be analyzed for SEO.</p>
        <img src="example.jpg" alt="">
    </body>
    </html>
    """
    node_url = "https://example.org/content/sample-node"
    
    # Analyze the node
    results = drupal_integration.analyze_node(node_id, node_content, node_url)
    
    # In a real module, we'd display these results in the Drupal editor
    print("\nDrupal Module Example Results:")
    print(f"Overall Score: {results['summary']['overall_score']:.1f}/100")
    print(f"Total Issues: {results['summary']['total_issues']}")
    
    # Save results for demonstration
    with open("examples/output/drupal_results.json", "w") as f:
        json.dump(results, f, indent=2)


def django_cms_example():
    """Example usage of Django CMS integration."""
    # This simulates functionality that would be in a Django CMS extension
    django_integration = DjangoCMSIntegration(output_dir="reports/django")
    
    # Simulate a Django CMS page being edited
    page_id = 789
    page_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Example Django CMS Page</title>
        <meta name="description" content="This is an example page for SEO analysis">
    </head>
    <body>
        <h1>Example Django CMS Page</h1>
        <p>This is a sample page that would be analyzed for SEO.</p>
        <div class="plugin">This is a plugin content</div>
    </body>
    </html>
    """
    page_url = "https://example.net/pages/sample-page"
    
    # Analyze the page
    results = django_integration.analyze_page(page_id, page_content, page_url)
    
    # In a real extension, we'd display these results in the Django admin
    print("\nDjango CMS Example Results:")
    print(f"Overall Score: {results['summary']['overall_score']:.1f}/100")
    
    # Save results for demonstration
    with open("examples/output/django_cms_results.json", "w") as f:
        json.dump(results, f, indent=2)


def headless_cms_example():
    """Example usage of headless CMS integration."""
    # This simulates functionality that would be in a headless CMS integration
    headless_integration = HeadlessCMSIntegration(output_dir="reports/headless")
    
    # Simulate a headless CMS entry being previewed
    entry_id = "abc123"
    rendered_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Example Headless CMS Entry</title>
        <meta name="description" content="This is an example entry for SEO analysis">
    </head>
    <body>
        <h1>Example Headless CMS Entry</h1>
        <p>This is a sample entry that would be analyzed for SEO.</p>
        <div data-contentful-field-id="content">
            <p>This is the main content from the headless CMS.</p>
        </div>
    </body>
    </html>
    """
    preview_url = "https://preview.example.io/entries/sample-entry"
    
    # Analyze the entry
    results = headless_integration.analyze_entry_preview(entry_id, rendered_html, preview_url)
    
    # In a real integration, we'd send these results back to the headless CMS
    print("\nHeadless CMS Example Results:")
    print(f"Overall Score: {results['summary']['overall_score']:.1f}/100")
    
    # Save results for demonstration
    with open("examples/output/headless_cms_results.json", "w") as f:
        json.dump(results, f, indent=2)


def main():
    """Run all CMS integration examples."""
    # Create output directory
    os.makedirs("examples/output", exist_ok=True)
    
    # Run all examples
    print("Running CMS Integration Examples...")
    wordpress_plugin_example()
    drupal_module_example()
    django_cms_example()
    headless_cms_example()
    print("\nAll examples completed. Results saved to examples/output/")


if __name__ == "__main__":
    main() 