"""Visual report generator module for Summit SEO."""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import base64
import time
import jinja2

from summit_seo.visualization import AnalyzerVisualization, ChartType

logger = logging.getLogger(__name__)

class VisualReportGenerator:
    """Generator for visual reports with charts and visualizations."""
    
    # Default report template with visualization sections
    DEFAULT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Analysis Visual Report - {{ data.url }}</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --success-color: #16a34a;
            --warning-color: #ca8a04;
            --error-color: #dc2626;
            --background-color: #f8fafc;
            --text-color: #1e293b;
            --light-bg: #f1f5f9;
            --border-color: #e2e8f0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--background-color);
            margin: 0;
            padding: 0;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        header {
            background-color: var(--primary-color);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        
        h1, h2, h3, h4 {
            margin-top: 0;
        }
        
        header h1 {
            color: white;
            margin-bottom: 0.5rem;
        }
        
        header p {
            margin: 0;
            opacity: 0.9;
        }
        
        .metadata {
            background-color: var(--light-bg);
            padding: 1rem 2rem;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
        }
        
        .metadata-item {
            display: flex;
            flex-direction: column;
        }
        
        .metadata-label {
            font-size: 0.8rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .metadata-value {
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        main {
            padding: 2rem;
        }
        
        .dashboard {
            margin-bottom: 3rem;
        }
        
        .dashboard-title {
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--primary-color);
            color: var(--primary-color);
        }
        
        .chart-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .chart-container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            padding: 1rem;
            transition: transform 0.2s ease-in-out;
        }
        
        .chart-container:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .chart-title {
            text-align: center;
            margin-top: 0;
            margin-bottom: 1rem;
            color: var(--primary-color);
            font-size: 1.2rem;
        }
        
        .chart-image {
            width: 100%;
            height: auto;
            display: block;
        }
        
        .full-width-chart {
            grid-column: 1 / -1;
        }
        
        .analyzer-sections {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 2rem;
        }
        
        .analyzer-section {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            transition: transform 0.2s ease-in-out;
        }
        
        .analyzer-section:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .analyzer-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border-color);
        }
        
        .analyzer-title {
            margin: 0;
            color: var(--primary-color);
        }
        
        .score {
            font-size: 1.2rem;
            font-weight: bold;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            display: inline-block;
        }
        
        .score-high {
            background-color: #dcfce7;
            color: var(--success-color);
        }
        
        .score-medium {
            background-color: #fef9c3;
            color: var(--warning-color);
        }
        
        .score-low {
            background-color: #fee2e2;
            color: var(--error-color);
        }
        
        .issues-container {
            margin-top: 1rem;
        }
        
        .issue-category {
            margin-bottom: 1rem;
        }
        
        .issue-category h4 {
            margin-top: 0;
            margin-bottom: 0.5rem;
            color: var(--secondary-color);
        }
        
        .issues-list, .warnings-list, .suggestions-list {
            list-style-type: none;
            padding-left: 0;
            margin: 0;
        }
        
        .issues-list li, .warnings-list li, .suggestions-list li {
            margin-bottom: 0.5rem;
            padding: 0.5rem;
            border-radius: 4px;
            font-size: 0.9rem;
        }
        
        .issues-list li {
            background-color: #fee2e2;
            color: var(--error-color);
        }
        
        .warnings-list li {
            background-color: #fef9c3;
            color: var(--warning-color);
        }
        
        .suggestions-list li {
            background-color: #dbeafe;
            color: var(--primary-color);
        }
        
        footer {
            background-color: var(--light-bg);
            padding: 2rem;
            text-align: center;
            border-top: 1px solid var(--border-color);
        }
        
        @media (max-width: 768px) {
            .chart-grid {
                grid-template-columns: 1fr;
            }
            
            .analyzer-sections {
                grid-template-columns: 1fr;
            }
            
            .metadata {
                flex-direction: column;
                gap: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>SEO Analysis Visual Report</h1>
            <p>Comprehensive analysis with visualizations</p>
        </header>
        
        <div class="metadata">
            <div class="metadata-item">
                <span class="metadata-label">URL</span>
                <span class="metadata-value">{{ data.url }}</span>
            </div>
            
            <div class="metadata-item">
                <span class="metadata-label">Analysis Date</span>
                <span class="metadata-value">{{ data.timestamp }}</span>
            </div>
            
            <div class="metadata-item">
                <span class="metadata-label">Average Score</span>
                <span class="metadata-value">{{ data.average_score }}%</span>
            </div>
        </div>
        
        <main>
            <!-- Overall Dashboard -->
            <section class="dashboard">
                <h2 class="dashboard-title">Analysis Overview</h2>
                
                <div class="chart-grid">
                    <!-- Score Distribution Chart -->
                    <div class="chart-container">
                        <h3 class="chart-title">Score Distribution by Analyzer</h3>
                        <img class="chart-image" src="{{ charts.score_distribution.data_uri }}" alt="Score Distribution">
                    </div>
                    
                    <!-- Issue Severity Chart -->
                    <div class="chart-container">
                        <h3 class="chart-title">Issues by Severity</h3>
                        <img class="chart-image" src="{{ charts.issue_severity.data_uri }}" alt="Issues by Severity">
                    </div>
                    
                    <!-- Recommendation Priority Chart -->
                    <div class="chart-container">
                        <h3 class="chart-title">Recommendations by Priority</h3>
                        <img class="chart-image" src="{{ charts.recommendation_priority.data_uri }}" alt="Recommendations by Priority">
                    </div>
                    
                    <!-- Quick Wins Chart -->
                    <div class="chart-container">
                        <h3 class="chart-title">Quick Win Opportunities</h3>
                        <img class="chart-image" src="{{ charts.quick_wins.data_uri }}" alt="Quick Win Opportunities">
                    </div>
                </div>
            </section>
            
            <!-- Analyzer Details -->
            <section>
                <h2 class="dashboard-title">Analyzer Details</h2>
                
                <div class="analyzer-sections">
                    {% for analyzer_name, result in data.results.items() %}
                    <div class="analyzer-section">
                        <div class="analyzer-header">
                            <h3 class="analyzer-title">{{ analyzer_name|title }}</h3>
                            
                            {% set score_class = 'score-high' if result.score >= 80 else 'score-medium' if result.score >= 60 else 'score-low' %}
                            <div class="score {{ score_class }}">
                                {{ result.score }}%
                            </div>
                        </div>
                        
                        <div class="issues-container">
                            {% if result.issues %}
                            <div class="issue-category">
                                <h4>Issues</h4>
                                <ul class="issues-list">
                                    {% for issue in result.issues %}
                                    <li>{{ issue }}</li>
                                    {% endfor %}
                                </ul>
                            </div>
                            {% endif %}
                            
                            {% if result.warnings %}
                            <div class="issue-category">
                                <h4>Warnings</h4>
                                <ul class="warnings-list">
                                    {% for warning in result.warnings %}
                                    <li>{{ warning }}</li>
                                    {% endfor %}
                                </ul>
                            </div>
                            {% endif %}
                            
                            {% if result.suggestions %}
                            <div class="issue-category">
                                <h4>Suggestions</h4>
                                <ul class="suggestions-list">
                                    {% for suggestion in result.suggestions %}
                                    <li>{{ suggestion }}</li>
                                    {% endfor %}
                                </ul>
                            </div>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </section>
        </main>
        
        <footer>
            <p>Generated by Summit SEO - A comprehensive SEO analysis tool</p>
        </footer>
    </div>
</body>
</html>
"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the visual report generator.
        
        Args:
            config: Optional configuration dictionary. Supported keys:
                - template_path: Path to custom HTML template
                - template_string: Custom template string
                - visualizer_name: Name of visualizer to use (default: matplotlib)
                - visualizer_config: Configuration for the visualizer
                - include_dashboard: Whether to include the dashboard section
                - include_analyzer_details: Whether to include analyzer details
        """
        self.config = config or {}
        self.template_env = jinja2.Environment(
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        self._load_template()
        
        # Create analyzer visualization
        visualizer_name = self.config.get('visualizer_name', 'matplotlib')
        visualizer_config = self.config.get('visualizer_config', {})
        self.visualization = AnalyzerVisualization(
            visualizer_name=visualizer_name,
            visualizer_config=visualizer_config
        )
    
    def _load_template(self) -> None:
        """Load the HTML template."""
        template_string = self.DEFAULT_TEMPLATE
        
        if self.config.get('template_string'):
            template_string = self.config['template_string']
        elif self.config.get('template_path'):
            with open(self.config['template_path'], 'r') as f:
                template_string = f.read()
        
        self.template = self.template_env.from_string(template_string)
    
    def _validate_data(self, data: Dict[str, Any]) -> None:
        """Validate the data for report generation.
        
        Args:
            data: Dictionary containing analysis results.
            
        Raises:
            ValueError: If data is invalid.
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
            
        if 'results' not in data:
            raise ValueError("Data must contain 'results' key")
            
        if not isinstance(data['results'], dict):
            raise ValueError("Results must be a dictionary")
    
    def _calculate_average_score(self, results: Dict[str, Any]) -> float:
        """Calculate the average score across all analyzers.
        
        Args:
            results: Dictionary of analysis results.
            
        Returns:
            Average score (0-100).
        """
        scores = []
        
        for analyzer_name, result in results.items():
            if isinstance(result, dict) and 'score' in result:
                scores.append(result['score'])
        
        if not scores:
            return 0
            
        return round(sum(scores) / len(scores), 1)
    
    async def _generate_charts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visualization charts for the report.
        
        Args:
            data: Dictionary containing analysis results.
            
        Returns:
            Dictionary of chart data.
        """
        charts = {}
        results = data['results']
        
        # Generate score distribution chart
        try:
            charts['score_distribution'] = await self.visualization.visualize_score_distribution(results)
        except Exception as e:
            logger.warning(f"Failed to generate score distribution chart: {e}")
            charts['score_distribution'] = {'error': str(e)}
        
        # Generate issue severity chart
        try:
            charts['issue_severity'] = await self.visualization.visualize_issue_severity(results)
        except Exception as e:
            logger.warning(f"Failed to generate issue severity chart: {e}")
            charts['issue_severity'] = {'error': str(e)}
        
        # Generate recommendation priority chart
        try:
            charts['recommendation_priority'] = await self.visualization.visualize_recommendation_priority(results)
        except Exception as e:
            logger.warning(f"Failed to generate recommendation priority chart: {e}")
            charts['recommendation_priority'] = {'error': str(e)}
        
        # Generate quick wins chart
        try:
            charts['quick_wins'] = await self.visualization.visualize_quick_wins(results)
        except Exception as e:
            logger.warning(f"Failed to generate quick wins chart: {e}")
            charts['quick_wins'] = {'error': str(e)}
        
        return charts
    
    async def generate_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a visual report from the analysis results.
        
        Args:
            data: Dictionary containing analysis results.
        
        Returns:
            Dictionary containing the generated report.
        
        Raises:
            ValueError: If data is invalid.
        """
        # Validate data
        self._validate_data(data)
        
        # Add timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Calculate average score
        data['average_score'] = self._calculate_average_score(data['results'])
        
        # Generate charts
        charts = await self._generate_charts(data)
        
        # Generate report
        report_html = self.template.render(data=data, charts=charts)
        
        return {
            'html': report_html,
            'charts': charts,
            'timestamp': data['timestamp']
        } 