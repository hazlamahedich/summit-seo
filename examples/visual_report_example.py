#!/usr/bin/env python3
"""Example script demonstrating the Visual HTML Report component.

This script shows how to generate a visual HTML report with charts and visualizations
from SEO analysis results.
"""

import asyncio
import logging
import time
import random
from pathlib import Path
from typing import Dict, Any, List

from summit_seo.reporter import VisualHTMLReporter, ReporterFactory
from summit_seo.analyzer import BaseAnalyzer
from summit_seo.processor import BaseProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Sample analysis results for demonstration
SAMPLE_RESULTS = {
    "url": "https://example.com",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "results": {
        "content_analyzer": {
            "score": 87,
            "issues": [
                "Missing alt text on 3 images",
                "Content-to-code ratio is low (20%)"
            ],
            "warnings": [
                "Content is slightly short (400 words)",
                "Keyword density could be improved"
            ],
            "suggestions": [
                "Add more detailed content",
                "Include more relevant keywords"
            ],
            "metrics": {
                "word_count": 400,
                "keyword_density": 1.5,
                "content_code_ratio": 0.2
            },
            "enhanced_recommendations": [
                {
                    "severity": "medium",
                    "priority": "P2",
                    "message": "Missing alt text on 3 images",
                    "impact": "Reduced accessibility and SEO value",
                    "quick_win": True
                },
                {
                    "severity": "low",
                    "priority": "P3",
                    "message": "Content-to-code ratio is low (20%)",
                    "impact": "May affect crawling and indexing",
                    "quick_win": False
                }
            ]
        },
        "meta_analyzer": {
            "score": 72,
            "issues": [
                "Meta description is too short (50 characters)"
            ],
            "warnings": [
                "Title tag is close to the 60 character limit",
                "Open Graph tags are incomplete"
            ],
            "suggestions": [
                "Improve meta description length and quality",
                "Add missing Open Graph tags"
            ],
            "metrics": {
                "title_length": 58,
                "meta_desc_length": 50,
                "keyword_in_meta": 1
            },
            "enhanced_recommendations": [
                {
                    "severity": "medium",
                    "priority": "P1",
                    "message": "Meta description is too short (50 characters)",
                    "impact": "Lower CTR in search results",
                    "quick_win": True
                }
            ]
        },
        "performance_analyzer": {
            "score": 65,
            "issues": [
                "Large image files (2.5MB total)",
                "Render-blocking JavaScript detected"
            ],
            "warnings": [
                "CSS files are not minified",
                "Cache headers not properly set"
            ],
            "suggestions": [
                "Optimize and compress images",
                "Minify CSS and JavaScript files",
                "Implement proper cache headers"
            ],
            "metrics": {
                "page_size": 3.2,
                "load_time": 2.8,
                "request_count": 42
            },
            "enhanced_recommendations": [
                {
                    "severity": "high",
                    "priority": "P1",
                    "message": "Large image files (2.5MB total)",
                    "impact": "Slower page load times and higher bounce rates",
                    "quick_win": True
                },
                {
                    "severity": "high",
                    "priority": "P2",
                    "message": "Render-blocking JavaScript detected",
                    "impact": "Delayed page rendering and interactivity",
                    "quick_win": False
                }
            ]
        },
        "security_analyzer": {
            "score": 53,
            "issues": [
                "Missing HTTPS implementation",
                "Cookie security attributes not set",
                "Cross-site scripting vulnerability detected"
            ],
            "warnings": [
                "Outdated libraries detected",
                "Missing Content-Security-Policy header"
            ],
            "suggestions": [
                "Implement HTTPS sitewide",
                "Add secure and httpOnly flags to cookies",
                "Update JavaScript libraries to latest versions"
            ],
            "metrics": {
                "secure_cookies_pct": 0,
                "xss_vulnerabilities": 2,
                "outdated_libs": 3
            },
            "enhanced_recommendations": [
                {
                    "severity": "critical",
                    "priority": "P0",
                    "message": "Missing HTTPS implementation",
                    "impact": "User data can be intercepted by attackers",
                    "quick_win": True
                },
                {
                    "severity": "high",
                    "priority": "P1",
                    "message": "Cookie security attributes not set",
                    "impact": "Cookies can be stolen or modified",
                    "quick_win": True
                },
                {
                    "severity": "critical",
                    "priority": "P0",
                    "message": "Cross-site scripting vulnerability detected",
                    "impact": "Attackers can execute malicious code",
                    "quick_win": False
                }
            ]
        },
        "accessibility_analyzer": {
            "score": 78,
            "issues": [
                "Insufficient color contrast in navigation"
            ],
            "warnings": [
                "Missing ARIA labels on interactive elements",
                "Skip navigation link not provided"
            ],
            "suggestions": [
                "Improve color contrast ratio to at least 4.5:1",
                "Add ARIA labels to all interactive elements"
            ],
            "metrics": {
                "a11y_score": 78,
                "contrast_issues": 2,
                "missing_labels": 5
            },
            "enhanced_recommendations": [
                {
                    "severity": "medium",
                    "priority": "P2",
                    "message": "Insufficient color contrast in navigation",
                    "impact": "Content may be difficult to read for visually impaired users",
                    "quick_win": True
                }
            ]
        }
    }
}


async def generate_visual_report():
    """Generate a visual HTML report from sample analysis results."""
    try:
        logger.info("Generating visual HTML report...")
        
        # Create output directory if it doesn't exist
        output_dir = Path("examples/output")
        output_dir.mkdir(exist_ok=True, parents=True)
        output_file = output_dir / "visual_seo_report.html"
        
        # Add output file to the data
        data = SAMPLE_RESULTS.copy()
        data["output_file"] = str(output_file)
        
        # Create the reporter using the factory
        reporter = ReporterFactory.create("VisualHTMLReporter", {
            "visualizer_name": "matplotlib",
            "visualizer_config": {
                "figure_size": (10, 6),
                "dpi": 100,
                "style": "seaborn-v0_8-whitegrid",
                "include_base64": True
            }
        })
        
        # Generate the report
        result = await reporter.generate_report(data)
        
        logger.info(f"Visual report generated successfully at: {result.content['output_path']}")
        logger.info(f"Report metadata: {result.metadata}")
        
        return result
        
    except Exception as e:
        logger.exception(f"Error generating visual report: {e}")
        raise


async def generate_different_styles():
    """Generate visual reports with different visualization styles."""
    try:
        logger.info("Generating reports with different visualization styles...")
        
        # Create output directory if it doesn't exist
        output_dir = Path("examples/output")
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Different visualization styles to demonstrate
        styles = [
            {"name": "default", "style": "seaborn-v0_8-whitegrid"},
            {"name": "dark", "style": "dark_background"},
            {"name": "minimal", "style": "bmh"},
            {"name": "presentation", "style": "fivethirtyeight"}
        ]
        
        results = []
        
        for style_config in styles:
            # Create the reporter with the specific style
            reporter = ReporterFactory.create("VisualHTMLReporter", {
                "visualizer_name": "matplotlib",
                "visualizer_config": {
                    "figure_size": (10, 6),
                    "dpi": 100,
                    "style": style_config["style"],
                    "include_base64": True
                }
            })
            
            # Add output file to the data
            data = SAMPLE_RESULTS.copy()
            output_file = output_dir / f"visual_report_{style_config['name']}.html"
            data["output_file"] = str(output_file)
            
            # Generate the report
            result = await reporter.generate_report(data)
            results.append(result)
            
            logger.info(f"Generated {style_config['name']} style report at: {result.content['output_path']}")
        
        return results
        
    except Exception as e:
        logger.exception(f"Error generating different style reports: {e}")
        raise


async def main():
    """Run the visual report examples."""
    logger.info("Starting visual report examples...")
    
    # Generate a basic visual report
    await generate_visual_report()
    
    # Generate reports with different styles
    await generate_different_styles()
    
    logger.info("Visual report examples completed!")


if __name__ == "__main__":
    asyncio.run(main()) 