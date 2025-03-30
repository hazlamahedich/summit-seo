"""HTML reporter module for Summit SEO."""

import jinja2
from typing import Dict, Any, List, Optional
from pathlib import Path
from .base import BaseReporter, ReportResult, ReportGenerationError

class HTMLReporter(BaseReporter):
    """Reporter for generating HTML reports."""

    DEFAULT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Analysis Report - {{ data.url }}</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --success-color: #16a34a;
            --warning-color: #ca8a04;
            --error-color: #dc2626;
            --background-color: #f8fafc;
            --text-color: #1e293b;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--background-color);
            margin: 0;
            padding: 2rem;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            padding: 2rem;
        }
        
        h1, h2, h3 {
            color: var(--primary-color);
            margin-top: 0;
        }
        
        .header {
            border-bottom: 2px solid var(--primary-color);
            margin-bottom: 2rem;
            padding-bottom: 1rem;
        }
        
        .metadata {
            color: #64748b;
            font-size: 0.9rem;
            margin-bottom: 2rem;
        }
        
        .analyzer-section {
            margin-bottom: 2rem;
            padding: 1rem;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
        }
        
        .score {
            font-size: 1.2rem;
            font-weight: bold;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            display: inline-block;
            margin-bottom: 1rem;
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
        
        .issues-list, .warnings-list, .suggestions-list {
            list-style-type: none;
            padding-left: 0;
        }
        
        .issues-list li, .warnings-list li, .suggestions-list li {
            margin-bottom: 0.5rem;
            padding: 0.5rem;
            border-radius: 4px;
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
        
        @media (max-width: 768px) {
            body {
                padding: 1rem;
            }
            
            .container {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SEO Analysis Report</h1>
            <div class="metadata">
                <p>URL: {{ data.url }}</p>
                <p>Analysis Date: {{ data.timestamp }}</p>
            </div>
        </div>
        
        {% for analyzer_name, result in data.results.items() %}
        <div class="analyzer-section">
            <h2>{{ analyzer_name|title }} Analysis</h2>
            
            {% set score_class = 'score-high' if result.score >= 80 else 'score-medium' if result.score >= 60 else 'score-low' %}
            <div class="score {{ score_class }}">
                Score: {{ result.score }}%
            </div>
            
            {% if result.issues %}
            <h3>Issues</h3>
            <ul class="issues-list">
                {% for issue in result.issues %}
                <li>{{ issue }}</li>
                {% endfor %}
            </ul>
            {% endif %}
            
            {% if result.warnings %}
            <h3>Warnings</h3>
            <ul class="warnings-list">
                {% for warning in result.warnings %}
                <li>{{ warning }}</li>
                {% endfor %}
            </ul>
            {% endif %}
            
            {% if result.suggestions %}
            <h3>Suggestions</h3>
            <ul class="suggestions-list">
                {% for suggestion in result.suggestions %}
                <li>{{ suggestion }}</li>
                {% endfor %}
            </ul>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the HTML reporter.
        
        Args:
            config: Optional configuration dictionary.
                   Supported keys:
                   - template_path: Path to custom HTML template
                   - template_string: Custom template string
                   - minify: Whether to minify the output HTML
        """
        super().__init__(config)
        self.template_env = jinja2.Environment(
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        self._load_template()

    def validate_config(self) -> None:
        """Validate the reporter configuration.
        
        Raises:
            ValueError: If configuration is invalid.
        """
        if self.config.get('template_path'):
            template_path = Path(self.config['template_path'])
            if not template_path.exists():
                raise ValueError(f"Template file not found: {template_path}")
            if not template_path.is_file():
                raise ValueError(f"Template path is not a file: {template_path}")

    def _load_template(self) -> None:
        """Load the HTML template."""
        template_string = self.DEFAULT_TEMPLATE
        
        if self.config.get('template_string'):
            template_string = self.config['template_string']
        elif self.config.get('template_path'):
            with open(self.config['template_path'], 'r') as f:
                template_string = f.read()
        
        self.template = self.template_env.from_string(template_string)

    async def generate_report(self, data: Dict[str, Any]) -> ReportResult:
        """Generate an HTML report from the analysis results.
        
        Args:
            data: Dictionary containing analysis results.
        
        Returns:
            ReportResult containing the generated HTML and metadata.
        
        Raises:
            ReportGenerationError: If report generation fails.
        """
        try:
            self._validate_data(data)
            html_content = self.template.render(data=data)
            
            if self.config.get('minify'):
                # Simple minification - remove unnecessary whitespace
                html_content = ' '.join(
                    line.strip()
                    for line in html_content.split('\n')
                    if line.strip()
                )
            
            metadata = self._create_metadata('html')
            return ReportResult(
                content=html_content,
                metadata=metadata,
                format='html'
            )
            
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate HTML report: {str(e)}")

    async def generate_batch_report(self, data: List[Dict[str, Any]]) -> ReportResult:
        """Generate an HTML report for multiple analysis results.
        
        Args:
            data: List of dictionaries containing analysis results.
        
        Returns:
            ReportResult containing the generated HTML and metadata.
        
        Raises:
            ReportGenerationError: If report generation fails.
        """
        try:
            self._validate_batch_data(data)
            
            # Create a summary report
            summary_data = {
                'url': 'Batch Analysis Summary',
                'timestamp': data[0]['timestamp'],  # Use first result's timestamp
                'results': self._aggregate_results(data)
            }
            
            return await self.generate_report(summary_data)
            
        except Exception as e:
            raise ReportGenerationError(
                f"Failed to generate batch HTML report: {str(e)}"
            )

    def _aggregate_results(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from multiple analyses.
        
        Args:
            data: List of analysis results.
        
        Returns:
            Dictionary containing aggregated results.
        """
        aggregated = {}
        
        # Get all unique analyzer names
        analyzer_names = {
            name
            for result in data
            for name in result['results'].keys()
        }
        
        for analyzer in analyzer_names:
            # Collect all scores for this analyzer
            scores = []
            all_issues = []
            all_warnings = []
            all_suggestions = []
            
            for result in data:
                if analyzer in result['results']:
                    analyzer_result = result['results'][analyzer]
                    scores.append(analyzer_result['score'])
                    all_issues.extend(analyzer_result.get('issues', []))
                    all_warnings.extend(analyzer_result.get('warnings', []))
                    all_suggestions.extend(analyzer_result.get('suggestions', []))
            
            # Calculate average score
            avg_score = sum(scores) / len(scores) if scores else 0
            
            # Remove duplicates while preserving order
            unique_issues = list(dict.fromkeys(all_issues))
            unique_warnings = list(dict.fromkeys(all_warnings))
            unique_suggestions = list(dict.fromkeys(all_suggestions))
            
            aggregated[analyzer] = {
                'score': round(avg_score, 2),
                'issues': unique_issues,
                'warnings': unique_warnings,
                'suggestions': unique_suggestions
            }
        
        return aggregated 