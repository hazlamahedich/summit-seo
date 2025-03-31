#!/usr/bin/env python3
"""
Monitoring Integration Example for Summit SEO

This example demonstrates how to integrate Summit SEO with monitoring systems
to track SEO metrics over time and set up alerts for critical issues.

The examples cover:
1. Prometheus metrics export
2. Grafana dashboard integration
3. Nagios/Icinga2 monitoring checks
4. Simple alerting system
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from summit_seo import SummitSEO
from summit_seo.analyzer import SecurityAnalyzer, PerformanceAnalyzer
from summit_seo.reporter import JSONReporter


class SEOMonitoringBase:
    """Base class for SEO monitoring integrations."""
    
    def __init__(
        self,
        url: str,
        output_dir: str = "monitoring",
        check_interval: int = 86400,  # 24 hours
        analyzers: Optional[List[str]] = None
    ):
        """
        Initialize the monitoring integration.
        
        Args:
            url: URL to monitor
            output_dir: Directory to store monitoring data
            check_interval: Interval between checks in seconds
            analyzers: List of analyzers to run (runs a subset if None)
        """
        self.url = url
        self.output_dir = output_dir
        self.check_interval = check_interval
        self.analyzers = analyzers or ["security", "performance"]
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize Summit SEO
        self.summit = SummitSEO()
    
    def get_analyzer_instances(self) -> List[Any]:
        """Get the analyzer instances to run."""
        analyzer_instances = []
        
        if "security" in self.analyzers:
            analyzer_instances.append(SecurityAnalyzer())
        if "performance" in self.analyzers:
            analyzer_instances.append(PerformanceAnalyzer())
            
        return analyzer_instances
    
    def run_check(self) -> Dict[str, Any]:
        """Run a single monitoring check."""
        analyzer_instances = self.get_analyzer_instances()
        results = self.summit.analyze_url(self.url, analyzers=analyzer_instances)
        
        # Save the results
        self._save_results(results)
        
        return results
    
    def _save_results(self, results: Dict[str, Any]) -> None:
        """Save the results to the output directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"check_{timestamp}.json")
        
        reporter = JSONReporter(output_file=filename)
        reporter.generate_report(results)
    
    def check_thresholds(self, results: Dict[str, Any], thresholds: Dict[str, float]) -> List[Tuple[str, float, float]]:
        """
        Check if the results meet the defined thresholds.
        
        Args:
            results: Analysis results
            thresholds: Dictionary mapping analyzer names to minimum scores
            
        Returns:
            List of tuples (analyzer_name, score, threshold) for failing checks
        """
        failures = []
        
        for analyzer_name, analyzer_result in results.items():
            if hasattr(analyzer_result, "score"):
                score = analyzer_result.score
                if analyzer_name.lower() in thresholds:
                    threshold = thresholds[analyzer_name.lower()]
                    if score < threshold:
                        failures.append((analyzer_name, score, threshold))
        
        return failures


class PrometheusExporter(SEOMonitoringBase):
    """Export Summit SEO metrics in Prometheus format."""
    
    def generate_prometheus_metrics(self, results: Dict[str, Any]) -> str:
        """
        Generate Prometheus metrics from the analysis results.
        
        Args:
            results: Analysis results
            
        Returns:
            Prometheus-formatted metrics text
        """
        metrics = []
        
        # Add header with timestamp
        metrics.append(f"# HELP summit_seo_score SEO score from 0-100")
        metrics.append(f"# TYPE summit_seo_score gauge")
        
        # Add overall score if available
        total_score = 0
        count = 0
        
        # Add analyzer-specific scores
        for analyzer_name, analyzer_result in results.items():
            if hasattr(analyzer_result, "score"):
                score = analyzer_result.score
                metrics.append(f'summit_seo_score{{analyzer="{analyzer_name}"}} {score}')
                total_score += score
                count += 1
                
                # Add issue counts if available
                if hasattr(analyzer_result, "issues"):
                    metrics.append(f"# HELP summit_seo_issues Number of SEO issues detected")
                    metrics.append(f"# TYPE summit_seo_issues gauge")
                    
                    # Count issues by severity
                    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
                    for issue in analyzer_result.issues:
                        severity = getattr(issue, "severity", "info").lower()
                        if severity in severity_counts:
                            severity_counts[severity] += 1
                    
                    # Add metrics for each severity
                    for severity, count in severity_counts.items():
                        if count > 0:
                            metrics.append(
                                f'summit_seo_issues{{analyzer="{analyzer_name}", severity="{severity}"}} {count}'
                            )
        
        # Add overall score
        if count > 0:
            overall_score = total_score / count
            metrics.append(f'summit_seo_score{{analyzer="overall"}} {overall_score}')
        
        return "\n".join(metrics)
    
    def write_metrics_file(self, results: Dict[str, Any]) -> str:
        """
        Write metrics to a file for Prometheus to scrape.
        
        Args:
            results: Analysis results
            
        Returns:
            Path to the metrics file
        """
        metrics = self.generate_prometheus_metrics(results)
        metrics_file = os.path.join(self.output_dir, "summit_seo_metrics.prom")
        
        with open(metrics_file, "w") as f:
            f.write(metrics)
        
        return metrics_file


class NagiosCheck(SEOMonitoringBase):
    """Nagios/Icinga2 compatible check for Summit SEO."""
    
    def get_nagios_status(self, results: Dict[str, Any], thresholds: Dict[str, Tuple[float, float]]) -> Tuple[int, str]:
        """
        Get Nagios/Icinga2 compatible status and output.
        
        Args:
            results: Analysis results
            thresholds: Dictionary mapping analyzer names to (warning, critical) thresholds
            
        Returns:
            Tuple of (status_code, status_message)
            
            Status codes:
            0 - OK
            1 - WARNING
            2 - CRITICAL
            3 - UNKNOWN
        """
        # Define Nagios status codes
        OK = 0
        WARNING = 1
        CRITICAL = 2
        UNKNOWN = 3
        
        # Check results against thresholds
        status = OK
        messages = []
        performance_data = []
        
        for analyzer_name, analyzer_result in results.items():
            if not hasattr(analyzer_result, "score"):
                continue
                
            score = analyzer_result.score
            analyzer_key = analyzer_name.lower()
            
            # Add performance data
            performance_data.append(f"{analyzer_name}={score:.1f}")
            
            # Check thresholds if defined
            if analyzer_key in thresholds:
                warning_threshold, critical_threshold = thresholds[analyzer_key]
                
                if score < critical_threshold:
                    status = max(status, CRITICAL)
                    messages.append(f"{analyzer_name} score is {score:.1f} (below critical threshold {critical_threshold})")
                elif score < warning_threshold:
                    status = max(status, WARNING)
                    messages.append(f"{analyzer_name} score is {score:.1f} (below warning threshold {warning_threshold})")
        
        # Generate overall message
        if status == OK:
            message = "SEO checks OK"
        elif status == WARNING:
            message = "SEO WARNING: " + "; ".join(messages)
        elif status == CRITICAL:
            message = "SEO CRITICAL: " + "; ".join(messages)
        else:
            message = "SEO status UNKNOWN"
        
        # Add performance data
        message += " | " + " ".join(performance_data)
        
        return status, message


class AlertingSystem(SEOMonitoringBase):
    """Simple alerting system for SEO monitoring."""
    
    def check_and_alert(
        self,
        results: Dict[str, Any],
        thresholds: Dict[str, float],
        alert_handlers: List[callable]
    ) -> List[str]:
        """
        Check results against thresholds and trigger alerts if needed.
        
        Args:
            results: Analysis results
            thresholds: Dictionary mapping analyzer names to minimum scores
            alert_handlers: List of callables to handle alerts
            
        Returns:
            List of alert messages sent
        """
        # Check thresholds
        failures = self.check_thresholds(results, thresholds)
        
        if not failures:
            return []
        
        # Generate alerts
        alerts = []
        for analyzer_name, score, threshold in failures:
            alert_message = (
                f"SEO Alert: {analyzer_name} score is {score:.1f}, "
                f"which is below the threshold of {threshold}"
            )
            alerts.append(alert_message)
        
        # Send alerts through handlers
        for alert in alerts:
            for handler in alert_handlers:
                handler(alert)
        
        return alerts


# Example alert handlers
def email_alert(message):
    """Example email alert handler."""
    print(f"[EMAIL ALERT] {message}")
    # In a real implementation, this would send an email
    # using smtplib or similar


def slack_alert(message):
    """Example Slack alert handler."""
    print(f"[SLACK ALERT] {message}")
    # In a real implementation, this would post to a Slack webhook


def prometheus_alert_manager(message):
    """Example Prometheus Alert Manager integration."""
    print(f"[PROMETHEUS ALERT] {message}")
    # In a real implementation, this would send an alert to Prometheus Alert Manager


def example_prometheus_export():
    """Example of exporting metrics for Prometheus."""
    url = "https://example.com"
    exporter = PrometheusExporter(url, output_dir="examples/output/monitoring")
    
    # Run the check
    results = exporter.run_check()
    
    # Generate metrics
    metrics_file = exporter.write_metrics_file(results)
    
    print(f"Prometheus metrics written to {metrics_file}")
    
    # Display example metrics
    with open(metrics_file, "r") as f:
        metrics = f.read()
        print("\nExample Prometheus Metrics:")
        print(metrics)


def example_nagios_check():
    """Example of a Nagios/Icinga2 check."""
    url = "https://example.com"
    nagios = NagiosCheck(url, output_dir="examples/output/monitoring")
    
    # Define thresholds as (warning, critical)
    thresholds = {
        "security": (80.0, 70.0),
        "performance": (70.0, 60.0)
    }
    
    # Run the check
    results = nagios.run_check()
    
    # Get Nagios status
    status_code, status_message = nagios.get_nagios_status(results, thresholds)
    
    print("\nNagios/Icinga2 Check Example:")
    print(f"Status Code: {status_code}")
    print(f"Status Message: {status_message}")


def example_alerting():
    """Example of a simple alerting system."""
    url = "https://example.com"
    alerting = AlertingSystem(url, output_dir="examples/output/monitoring")
    
    # Define thresholds
    thresholds = {
        "security": 80.0,
        "performance": 75.0
    }
    
    # Define alert handlers
    alert_handlers = [email_alert, slack_alert, prometheus_alert_manager]
    
    # Run the check
    results = alerting.run_check()
    
    # Check and alert
    alerts = alerting.check_and_alert(results, thresholds, alert_handlers)
    
    print("\nAlerting System Example:")
    if alerts:
        print(f"Sent {len(alerts)} alerts:")
        for alert in alerts:
            print(f"- {alert}")
    else:
        print("No alerts triggered")


def main():
    """Run all monitoring integration examples."""
    # Create output directory
    os.makedirs("examples/output/monitoring", exist_ok=True)
    
    # Run the examples
    print("Running Monitoring Integration Examples...")
    example_prometheus_export()
    example_nagios_check()
    example_alerting()
    print("\nAll examples completed. Results saved to examples/output/monitoring/")


if __name__ == "__main__":
    main() 