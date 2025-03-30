#!/usr/bin/env python3
"""Example demonstrating the dashboard visualization capabilities of Summit SEO."""

import asyncio
import copy
import logging
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

from summit_seo.visualization import (
    VisualizationFactory,
    AnalyzerVisualization,
    VisualizationType,
    ChartType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample analysis results
SAMPLE_RESULTS = {
    "url": "https://example.com",
    "timestamp": datetime.utcnow().isoformat(),
    "overall_score": 78,
    "results": {
        "seo": {
            "score": 85,
            "analysis": {
                "meta_tags": {
                    "score": 90,
                    "findings": [
                        {"severity": "low", "message": "Missing canonical tag"},
                        {"severity": "info", "message": "Meta description is well optimized"}
                    ]
                },
                "headings": {
                    "score": 80,
                    "findings": [
                        {"severity": "medium", "message": "Missing H1 tag on 3 pages"},
                        {"severity": "low", "message": "Heading hierarchy not optimal"}
                    ]
                }
            }
        },
        "performance": {
            "score": 72,
            "analysis": {
                "load_time": {
                    "score": 65,
                    "findings": [
                        {"severity": "high", "message": "Page load time exceeds 3s"},
                        {"severity": "medium", "message": "Large images not optimized"}
                    ]
                },
                "mobile_speed": {
                    "score": 78,
                    "findings": [
                        {"severity": "medium", "message": "Mobile rendering delays"},
                        {"severity": "low", "message": "CSS not fully optimized for mobile"}
                    ]
                }
            }
        },
        "security": {
            "score": 90,
            "analysis": {
                "https": {
                    "score": 100,
                    "findings": [
                        {"severity": "info", "message": "HTTPS configured correctly"}
                    ]
                },
                "vulnerabilities": {
                    "score": 80,
                    "findings": [
                        {"severity": "medium", "message": "Outdated WordPress plugins found"},
                        {"severity": "low", "message": "Content-Security-Policy header missing"}
                    ]
                }
            }
        },
        "accessibility": {
            "score": 65,
            "analysis": {
                "aria": {
                    "score": 60,
                    "findings": [
                        {"severity": "high", "message": "Missing ARIA labels on form elements"},
                        {"severity": "medium", "message": "Navigation not keyboard accessible"}
                    ]
                },
                "contrast": {
                    "score": 70,
                    "findings": [
                        {"severity": "medium", "message": "Insufficient contrast on primary buttons"},
                        {"severity": "low", "message": "Text size too small in some areas"}
                    ]
                }
            }
        }
    },
    "recommendations": [
        {
            "category": "seo",
            "priority": "high",
            "description": "Add canonical tags to all pages",
            "impact": "Prevent duplicate content issues"
        },
        {
            "category": "performance",
            "priority": "high",
            "description": "Optimize image sizes and formats",
            "impact": "Reduce page load time by 40%"
        },
        {
            "category": "security",
            "priority": "medium",
            "description": "Update outdated WordPress plugins",
            "impact": "Reduce security vulnerabilities"
        },
        {
            "category": "accessibility",
            "priority": "high",
            "description": "Add ARIA labels to all form elements",
            "impact": "Improve accessibility for screen readers"
        }
    ]
}


async def generate_dashboard():
    """Generate a summary dashboard visualization."""
    try:
        logger.info("Generating summary dashboard...")
        
        # File paths for output
        output_dir = Path("examples/output")
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Individual visualization output paths
        score_distribution_path = output_dir / "score_distribution_chart.png"
        recommendation_priority_path = output_dir / "recommendation_priority_chart.png"
        quick_wins_path = output_dir / "quick_wins_chart.png"
        comparison_path = output_dir / "score_comparison_chart.png"
        
        # Dashboard output path
        dashboard_path = output_dir / "summary_dashboard.png"
        
        # Create the visualizer configuration
        visualizer_config = {
            "figure_size": (12, 8),
            "dpi": 100,
            "style": "seaborn-v0_8-whitegrid"
        }
        
        # Create analyzer visualization
        analyzer_viz = AnalyzerVisualization(visualizer_name="matplotlib", 
                                           visualizer_config=visualizer_config)
        
        # First generate individual visualizations
        logger.info("Generating individual visualizations...")
        
        # Score distribution visualization
        try:
            result = await analyzer_viz.create_visualization(
                SAMPLE_RESULTS,
                VisualizationType.SCORE_DISTRIBUTION,
                str(score_distribution_path)
            )
            logger.info(f"Created {VisualizationType.SCORE_DISTRIBUTION.name} visualization at: {score_distribution_path}")
        except Exception as e:
            logger.error(f"Error generating score distribution chart: {e}")
            
        # Recommendation priority visualization
        try:
            result = await analyzer_viz.create_visualization(
                SAMPLE_RESULTS,
                VisualizationType.RECOMMENDATION_PRIORITY,
                str(recommendation_priority_path)
            )
            logger.info(f"Created {VisualizationType.RECOMMENDATION_PRIORITY.name} visualization at: {recommendation_priority_path}")
        except Exception as e:
            logger.error(f"Error generating recommendation priority chart: {e}")
            
        # Quick wins visualization
        try:
            result = await analyzer_viz.create_visualization(
                SAMPLE_RESULTS,
                VisualizationType.QUICK_WINS,
                str(quick_wins_path)
            )
            logger.info(f"Created {VisualizationType.QUICK_WINS.name} visualization at: {quick_wins_path}")
        except Exception as e:
            logger.error(f"Error generating quick wins chart: {e}")
        
        # Try to generate the dashboard as a separate step
        try:
            logger.info("Generating dashboard visualization...")
            
            # Create a simple dashboard layout rather than using the built-in dashboard
            # Create a 2x2 subplot grid
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            fig.suptitle("Website Health Summary Dashboard", fontsize=16)
            
            # Plot 1: Score Distribution (top left)
            categories = list(SAMPLE_RESULTS['results'].keys())
            scores = [SAMPLE_RESULTS['results'][cat]['score'] for cat in categories]
            axes[0, 0].bar(categories, scores, color=['blue', 'green', 'orange', 'red'])
            axes[0, 0].set_title('Category Scores')
            axes[0, 0].set_ylim([0, 100])
            
            # Plot 2: Recommendation Priority (top right)
            priorities = {}
            for rec in SAMPLE_RESULTS.get('recommendations', []):
                priority = rec.get('priority', 'medium')
                priorities[priority] = priorities.get(priority, 0) + 1
            
            if priorities:
                axes[0, 1].pie(
                    priorities.values(), 
                    labels=priorities.keys(),
                    autopct='%1.1f%%', 
                    startangle=90,
                    colors=['red', 'orange', 'green']
                )
                axes[0, 1].set_title('Recommendation Priorities')
            else:
                axes[0, 1].text(0.5, 0.5, 'No recommendations', ha='center')
                
            # Plot 3: Finding Severity (bottom left)
            severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
            for category in SAMPLE_RESULTS['results'].values():
                for analyzer in category.get('analysis', {}).values():
                    for finding in analyzer.get('findings', []):
                        severity = finding.get('severity', 'info').lower()
                        if severity in severity_counts:
                            severity_counts[severity] += 1
                            
            axes[1, 0].bar(
                severity_counts.keys(),
                severity_counts.values(),
                color=['darkred', 'red', 'orange', 'yellow', 'blue']
            )
            axes[1, 0].set_title('Finding Severity Distribution')
            
            # Plot 4: Overall Score Gauge (bottom right)
            from matplotlib.patches import Wedge
            
            def gauge_chart(ax, value, min_val=0, max_val=100, colors=['red', 'orange', 'yellow', 'yellowgreen', 'green']):
                # Ensure value is in range
                value = max(min(value, max_val), min_val)
                
                # Normalize the value
                norm_value = (value - min_val) / (max_val - min_val)
                
                # Draw the gauge
                angles = np.linspace(0, 180, 100)
                
                # Background
                ax.add_patch(Wedge((0.5, 0), 0.4, 0, 180, width=0.1, facecolor='lightgray', edgecolor='gray'))
                
                # Value indicator
                indicator_angle = norm_value * 180
                indicator_color = colors[min(int(norm_value * len(colors)), len(colors) - 1)]
                ax.add_patch(Wedge((0.5, 0), 0.4, 0, indicator_angle, width=0.1, facecolor=indicator_color, edgecolor=None))
                
                # Add text for the value
                ax.text(0.5, 0.2, f"{value:.1f}", ha='center', va='center', fontsize=20, fontweight='bold')
                ax.text(0.5, 0.05, "Overall Score", ha='center', va='center', fontsize=12)
                
                # Add labels for min and max
                ax.text(0.1, 0, f"{min_val}", ha='center', va='center', fontsize=8)
                ax.text(0.9, 0, f"{max_val}", ha='center', va='center', fontsize=8)
                
                # Remove axis
                ax.set_xlim(0, 1)
                ax.set_ylim(-0.5, 0.5)
                ax.axis('off')
            
            gauge_chart(axes[1, 1], SAMPLE_RESULTS['overall_score'])
            axes[1, 1].set_title('Overall Score')
            
            # Adjust layout and save
            plt.tight_layout(rect=[0, 0, 1, 0.96])  # Make room for the title
            plt.savefig(str(dashboard_path), dpi=100)
            plt.close(fig)
            
            logger.info(f"Dashboard generated successfully at: {dashboard_path}")
        except Exception as e:
            logger.error(f"Error generating dashboard: {e}")
            logger.info("Continuing with individual visualizations...")
        
        # Generate comparison visualization
        logger.info("Generating score comparison visualization...")
        comparison_data = {
            "current": SAMPLE_RESULTS,
            "previous": {
                "url": "https://example.com",
                "timestamp": "2025-03-01T00:00:00",
                "overall_score": 65,
                "results": {
                    "seo": {"score": 72},
                    "performance": {"score": 60},
                    "security": {"score": 85},
                    "accessibility": {"score": 55}
                }
            }
        }
        
        # Generate a custom visualization to show score comparison
        try:
            # Using the direct visualizer instead of analyzer_viz since we have a custom format
            visualizer = VisualizationFactory.create("matplotlib", visualizer_config)
            
            # Prepare data for comparison chart
            categories = ['SEO', 'Performance', 'Security', 'Accessibility', 'Overall']
            current_scores = [
                comparison_data['current']['results']['seo']['score'],
                comparison_data['current']['results']['performance']['score'],
                comparison_data['current']['results']['security']['score'],
                comparison_data['current']['results']['accessibility']['score'],
                comparison_data['current']['overall_score']
            ]
            previous_scores = [
                comparison_data['previous']['results']['seo']['score'],
                comparison_data['previous']['results']['performance']['score'],
                comparison_data['previous']['results']['security']['score'],
                comparison_data['previous']['results']['accessibility']['score'],
                comparison_data['previous']['overall_score']
            ]
            
            # Create grouped bar chart data
            x = np.arange(len(categories))
            width = 0.35
            
            # Create figure and axes
            fig, ax = plt.subplots(figsize=(10, 6))
            rects1 = ax.bar(x - width/2, current_scores, width, label='Current')
            rects2 = ax.bar(x + width/2, previous_scores, width, label='Previous')
            
            # Add labels, title and legend
            ax.set_ylabel('Score')
            ax.set_title('Score Improvement Over Time')
            ax.set_xticks(x)
            ax.set_xticklabels(categories)
            ax.legend()
            
            # Save the figure
            fig.tight_layout()
            fig.savefig(str(comparison_path))
            plt.close(fig)
            
            logger.info(f"Created score comparison visualization at: {comparison_path}")
        except Exception as e:
            logger.error(f"Error generating comparison chart: {e}")
        
    except Exception as e:
        logger.exception(f"Error generating visualizations: {e}")
        raise


async def main():
    """Run the dashboard examples."""
    logger.info("Starting dashboard visualization examples...")
    
    # Generate summary dashboard
    await generate_dashboard()
    
    logger.info("Dashboard visualization examples completed!")


if __name__ == "__main__":
    asyncio.run(main()) 