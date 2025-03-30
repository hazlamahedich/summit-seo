#!/usr/bin/env python
"""Example script demonstrating enhanced recommendations for security analysis."""

import asyncio
import sys
import os
import json
from typing import Dict, Any, List
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from summit_seo.analyzer import factory, RecommendationSeverity, RecommendationPriority
from summit_seo.analyzer.recommendation import Recommendation


async def analyze_security(html_content: str, page_url: str = 'https://example.com') -> Dict[str, Any]:
    """Analyze security aspects of a webpage.
    
    Args:
        html_content: HTML content to analyze
        page_url: URL of the page being analyzed
        
    Returns:
        Analysis results
    """
    # Get security analyzer from factory
    security_analyzer = factory.create('security', {
        'page_url': page_url
    })
    
    # Analyze the HTML content
    result = await security_analyzer.analyze(html_content)
    
    return result


def print_recommendation(rec: Recommendation, index: int = 0) -> None:
    """Print a formatted recommendation.
    
    Args:
        rec: Recommendation to print
        index: Index number for the recommendation
    """
    priority_symbols = {
        RecommendationPriority.P0: "🔴",  # Critical priority
        RecommendationPriority.P1: "🟠",  # High priority
        RecommendationPriority.P2: "🟡",  # Medium priority
        RecommendationPriority.P3: "🟢",  # Low priority
        RecommendationPriority.P4: "⚪",   # Info priority
    }
    
    severity_symbols = {
        RecommendationSeverity.CRITICAL: "💀",  # Critical severity
        RecommendationSeverity.HIGH: "🚨",      # High severity
        RecommendationSeverity.MEDIUM: "⚠️",     # Medium severity
        RecommendationSeverity.LOW: "ℹ️",        # Low severity
        RecommendationSeverity.INFO: "📝",      # Info severity
    }
    
    quick_win_symbol = "⚡" if rec.quick_win else ""
    
    # Print header
    print(f"\n{'-' * 80}")
    print(f"#{index+1}: {priority_symbols.get(rec.priority, '?')} {severity_symbols.get(rec.severity, '?')} {quick_win_symbol} {rec.title}")
    print(f"{'-' * 80}")
    
    # Print description
    print(f"\n📋 Description: {rec.description}")
    
    # Print impact if available
    if rec.impact:
        print(f"\n💥 Impact: {rec.impact}")
    
    # Print implementation details
    print(f"\n🔧 Implementation Difficulty: {rec.difficulty.capitalize()}")
    
    # Print implementation steps
    if rec.steps:
        print("\n📋 Implementation Steps:")
        for i, step in enumerate(rec.steps, 1):
            print(f"  {i}. {step}")
    
    # Print code example if available
    if rec.code_example:
        print("\n💻 Code Example:")
        print(f"```\n{rec.code_example}\n```")
    
    # Print resource links
    if rec.resource_links:
        print("\n📚 Resources:")
        for link in rec.resource_links:
            print(f"  • {link['title']}: {link['url']}")


def print_results(results: Dict[str, Any]) -> None:
    """Print formatted security analysis results.
    
    Args:
        results: Security analysis results
    """
    print("\n====== SECURITY ANALYSIS RESULTS ======\n")
    
    # Print basic info
    print(f"Security Score: {results.data['security_score']}/100")
    print(f"High Severity Issues: {results.data['high_severity_issues']}")
    print(f"Medium Severity Issues: {results.data['medium_severity_issues']}")
    print(f"Low Severity Issues: {results.data['low_severity_issues']}")
    
    # Print enhanced recommendations by priority
    priority_recommendations = results.get_priority_recommendations()
    
    if priority_recommendations:
        print("\n\n====== RECOMMENDATIONS BY PRIORITY ======\n")
        for i, rec in enumerate(priority_recommendations):
            print_recommendation(rec, i)
    
    # Print quick wins
    quick_wins = results.get_quick_wins()
    
    if quick_wins:
        print("\n\n====== QUICK WINS ======\n")
        print("These issues can be fixed quickly for immediate security improvement:")
        for i, rec in enumerate(quick_wins):
            print(f"  {i+1}. {rec.title}")


async def main() -> None:
    """Run the example."""
    # Sample HTML with security issues
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Example Page with Security Issues</title>
        <meta charset="UTF-8">
        <script src="http://example.com/insecure-script.js"></script>
        <link rel="stylesheet" href="http://example.com/styles.css">
        <!-- API Key: api_key="1234567890abcdef" -->
        <!-- TODO: Remove password before production: dbpassword="password123" -->
    </head>
    <body>
        <h1>Welcome to our site</h1>
        <img src="http://example.com/image.jpg" alt="Example Image">
        <form action="/submit" method="POST">
            <input type="text" name="username" value="">
            <input type="password" name="password" value="">
            <input type="submit" value="Login">
        </form>
        <script>
            // Insecure way to handle user input
            function displayMessage() {
                var username = getUrlParameter('username');
                document.getElementById('message').innerHTML = 'Welcome, ' + username;
            }
        </script>
    </body>
    </html>
    """
    
    # Analyze the sample HTML
    results = await analyze_security(sample_html)
    
    # Print the results
    print_results(results)


if __name__ == "__main__":
    asyncio.run(main()) 