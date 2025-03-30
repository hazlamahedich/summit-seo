#!/usr/bin/env python3
"""Example demonstrating visualization capabilities in Summit SEO."""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to import summit_seo package
sys.path.append(str(Path(__file__).resolve().parent.parent))

from summit_seo.visualization import VisualizationFactory, ChartType
from summit_seo.visualization.analyzer_visualization import AnalyzerVisualization

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Sample analysis results
SAMPLE_RESULTS = {
    "content_analyzer": {
        "score": 85,
        "issues": [
            "Content is too short (300 words)",
            "Keyword density is too low (0.5%)"
        ],
        "warnings": [
            "No internal links found",
            "Reading level is too advanced"
        ],
        "suggestions": [
            "Add more relevant keywords",
            "Break content into smaller paragraphs"
        ],
        "enhanced_recommendations": [
            {
                "title": "Increase content length",
                "severity": "medium",
                "priority": "P2",
                "code_example": "<article>Add more relevant content here</article>",
                "quick_win": True,
                "difficulty": "easy"
            },
            {
                "title": "Improve keyword density",
                "severity": "medium",
                "priority": "P1",
                "code_example": "<!-- Add target keywords naturally throughout content -->",
                "quick_win": False,
                "difficulty": "medium"
            }
        ]
    },
    "meta_analyzer": {
        "score": 72,
        "issues": [
            "Meta description is missing",
            "Meta title is too short"
        ],
        "warnings": [
            "Canonical URL is not set"
        ],
        "suggestions": [
            "Add Open Graph tags",
            "Add Twitter Card tags"
        ],
        "enhanced_recommendations": [
            {
                "title": "Add meta description",
                "severity": "high",
                "priority": "P1",
                "code_example": "<meta name=\"description\" content=\"Your compelling description here\" />",
                "quick_win": True,
                "difficulty": "easy"
            },
            {
                "title": "Optimize meta title",
                "severity": "medium",
                "priority": "P2",
                "code_example": "<title>Primary Keyword | Secondary Keyword | Brand Name</title>",
                "quick_win": True,
                "difficulty": "easy"
            }
        ]
    },
    "security_analyzer": {
        "score": 45,
        "issues": [
            "Missing HTTPS implementation",
            "Insecure cookies detected"
        ],
        "warnings": [
            "No Content-Security-Policy header",
            "Outdated jQuery version (1.8.3)"
        ],
        "suggestions": [
            "Enable HSTS header",
            "Update dependencies"
        ],
        "enhanced_recommendations": [
            {
                "title": "Implement HTTPS",
                "severity": "critical",
                "priority": "P0",
                "code_example": "# .htaccess redirect\nRewriteEngine On\nRewriteCond %{HTTPS} off\nRewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]",
                "quick_win": False,
                "difficulty": "medium"
            },
            {
                "title": "Secure cookies",
                "severity": "high",
                "priority": "P1",
                "code_example": "# Set secure cookies\nSet-Cookie: session=123; Secure; HttpOnly; SameSite=Strict",
                "quick_win": True,
                "difficulty": "easy"
            },
            {
                "title": "Implement Content-Security-Policy",
                "severity": "high",
                "priority": "P2",
                "code_example": "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'self'; script-src 'self' trusted-scripts.com\">",
                "quick_win": False,
                "difficulty": "hard"
            }
        ]
    },
    "performance_analyzer": {
        "score": 65,
        "issues": [
            "Large image files not optimized",
            "Render-blocking CSS detected"
        ],
        "warnings": [
            "No browser caching implemented",
            "No image lazy loading"
        ],
        "suggestions": [
            "Minify JavaScript and CSS",
            "Defer non-critical JavaScript"
        ],
        "enhanced_recommendations": [
            {
                "title": "Optimize images",
                "severity": "medium",
                "priority": "P1",
                "code_example": "<!-- Use WebP format and appropriate dimensions -->\n<img src=\"image.webp\" alt=\"Description\" width=\"800\" height=\"600\">",
                "quick_win": True,
                "difficulty": "easy"
            },
            {
                "title": "Eliminate render-blocking resources",
                "severity": "high",
                "priority": "P1",
                "code_example": "<!-- Add defer to non-critical scripts -->\n<script src=\"script.js\" defer></script>",
                "quick_win": False,
                "difficulty": "medium"
            }
        ],
        "metrics": {
            "page_size": 2.5,  # MB
            "load_time": 3.2,  # seconds
            "resource_count": 45,
            "js_size": 1.2,  # MB
            "css_size": 0.3,  # MB
            "image_size": 0.9  # MB
        }
    }
}


async def demonstrate_basic_charts():
    """Demonstrate basic chart generation."""
    logger.info("=== Basic Chart Generation ===")
    
    # Create a visualizer
    visualizer = VisualizationFactory.create('matplotlib', {
        'figure_size': (10, 6),
        'dpi': 100,
        'output_format': 'png'
    })
    
    # Create bar chart
    bar_data = {
        'x': ['Category A', 'Category B', 'Category C', 'Category D'],
        'y': [35, 45, 55, 25],
        'title': 'Sample Bar Chart',
        'x_label': 'Categories',
        'y_label': 'Values'
    }
    
    bar_chart = await visualizer.generate_chart(bar_data, ChartType.BAR)
    logger.info(f"Generated bar chart: {bar_chart['format']}, {len(bar_chart.get('image_base64', ''))//1024}KB")
    
    # Create pie chart
    pie_data = {
        'values': [35, 25, 20, 20],
        'labels': ['A', 'B', 'C', 'D'],
        'title': 'Sample Pie Chart'
    }
    
    pie_chart = await visualizer.generate_chart(pie_data, ChartType.PIE)
    logger.info(f"Generated pie chart: {pie_chart['format']}, {len(pie_chart.get('image_base64', ''))//1024}KB")
    
    # Save chart to file
    if bar_chart.get('image_base64'):
        import base64
        
        output_dir = Path(__file__).parent / 'output'
        output_dir.mkdir(exist_ok=True)
        
        # Save bar chart
        with open(output_dir / 'bar_chart.png', 'wb') as f:
            f.write(base64.b64decode(bar_chart['image_base64']))
        logger.info(f"Saved bar chart to {output_dir / 'bar_chart.png'}")
        
        # Save pie chart
        with open(output_dir / 'pie_chart.png', 'wb') as f:
            f.write(base64.b64decode(pie_chart['image_base64']))
        logger.info(f"Saved pie chart to {output_dir / 'pie_chart.png'}")


async def demonstrate_analyzer_visualizations():
    """Demonstrate analyzer visualization integration."""
    logger.info("=== Analyzer Visualization Integration ===")
    
    # Create the analyzer visualization utility
    visualizer = AnalyzerVisualization()
    
    # Create output directory
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)
    
    # Generate score distribution visualization
    score_viz = await visualizer.visualize_score_distribution(SAMPLE_RESULTS)
    if score_viz.get('image_base64'):
        import base64
        with open(output_dir / 'score_distribution.png', 'wb') as f:
            f.write(base64.b64decode(score_viz['image_base64']))
        logger.info(f"Saved score distribution chart to {output_dir / 'score_distribution.png'}")
    
    # Generate issue severity visualization
    severity_viz = await visualizer.visualize_issue_severity(SAMPLE_RESULTS)
    if severity_viz.get('image_base64'):
        import base64
        with open(output_dir / 'issue_severity.png', 'wb') as f:
            f.write(base64.b64decode(severity_viz['image_base64']))
        logger.info(f"Saved issue severity chart to {output_dir / 'issue_severity.png'}")
    
    # Generate recommendation priority visualization
    priority_viz = await visualizer.visualize_recommendation_priority(SAMPLE_RESULTS)
    if priority_viz.get('image_base64'):
        import base64
        with open(output_dir / 'recommendation_priority.png', 'wb') as f:
            f.write(base64.b64decode(priority_viz['image_base64']))
        logger.info(f"Saved recommendation priority chart to {output_dir / 'recommendation_priority.png'}")
    
    # Generate quick win visualization
    quickwin_viz = await visualizer.visualize_quick_wins(SAMPLE_RESULTS)
    if quickwin_viz.get('image_base64'):
        import base64
        with open(output_dir / 'quick_wins.png', 'wb') as f:
            f.write(base64.b64decode(quickwin_viz['image_base64']))
        logger.info(f"Saved quick win chart to {output_dir / 'quick_wins.png'}")


async def demonstrate_dashboard():
    """Demonstrate dashboard generation."""
    logger.info("=== Dashboard Generation ===")
    
    # Create the analyzer visualization utility
    visualizer = AnalyzerVisualization()
    
    # Generate dashboard
    dashboard = await visualizer.generate_analyzer_dashboard(SAMPLE_RESULTS)
    
    # Save dashboard
    if dashboard.get('image_base64'):
        import base64
        
        output_dir = Path(__file__).parent / 'output'
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / 'dashboard.png', 'wb') as f:
            f.write(base64.b64decode(dashboard['image_base64']))
        logger.info(f"Saved dashboard to {output_dir / 'dashboard.png'}")


async def main():
    """Run the visualization examples."""
    logger.info("Starting visualization examples")
    
    # Demonstrate basic chart generation
    await demonstrate_basic_charts()
    
    # Demonstrate analyzer visualizations
    await demonstrate_analyzer_visualizations()
    
    # Demonstrate dashboard generation
    await demonstrate_dashboard()
    
    logger.info("Completed visualization examples")


if __name__ == "__main__":
    asyncio.run(main()) 