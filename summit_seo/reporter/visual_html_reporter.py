"""Visual HTML reporter module for Summit SEO."""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from .base import BaseReporter, ReportResult, ReportGenerationError
from .html_reporter import HTMLReporter
from .visual_report import VisualReportGenerator

logger = logging.getLogger(__name__)

class VisualHTMLReporter(HTMLReporter):
    """Reporter for generating HTML reports with visualizations."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the visual HTML reporter.
        
        Args:
            config: Optional configuration dictionary.
                   Supported keys from HTMLReporter:
                   - template_path: Path to custom HTML template
                   - template_string: Custom template string
                   - minify: Whether to minify the output HTML
                   
                   Additional keys for VisualHTMLReporter:
                   - visualizer_name: Name of visualizer to use (default: matplotlib)
                   - visualizer_config: Configuration for the visualizer
                   - include_dashboard: Whether to include the dashboard (default: True)
                   - include_analyzer_details: Whether to include analyzer details (default: True)
        """
        # Initialize the base HTMLReporter
        super().__init__(config)
        
        # Create the visual report generator
        visual_config = {
            'visualizer_name': self.config.get('visualizer_name', 'matplotlib'),
            'visualizer_config': self.config.get('visualizer_config', {}),
            'include_dashboard': self.config.get('include_dashboard', True),
            'include_analyzer_details': self.config.get('include_analyzer_details', True)
        }
        
        # If a custom template is provided, pass it to the visual report generator
        if self.config.get('template_path'):
            visual_config['template_path'] = self.config['template_path']
        elif self.config.get('template_string'):
            visual_config['template_string'] = self.config['template_string']
            
        self.visual_report_generator = VisualReportGenerator(visual_config)

    async def generate_report(self, data: Dict[str, Any]) -> ReportResult:
        """Generate a visual HTML report from the analysis results.
        
        Args:
            data: Dictionary containing analysis results.
        
        Returns:
            ReportResult containing the generated HTML and metadata.
        
        Raises:
            ReportGenerationError: If report generation fails.
        """
        try:
            self._validate_data(data)
            
            # Generate the visual report
            report_data = await self.visual_report_generator.generate_report(data)
            html_content = report_data['html']
            
            # Apply minification if configured
            if self.config.get('minify'):
                # Simple minification - remove unnecessary whitespace
                html_content = ' '.join(
                    line.strip()
                    for line in html_content.split('\n')
                    if line.strip()
                )
            
            # Get the output file path from the data or use a default
            output_file = data.get('output_file', 'seo_report.html')
            
            # If output_file is a Path object, convert to string
            if isinstance(output_file, Path):
                output_file = str(output_file)
            
            # Write the report to the output file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Create the report result
            result = ReportResult(
                content={
                    'html': html_content,
                    'output_path': output_file,
                    'visualization_data': report_data
                },
                metadata=self._create_metadata(format='html'),
                format='html'
            )
            
            return result
            
        except Exception as e:
            logger.exception(f"Error generating visual HTML report: {e}")
            raise ReportGenerationError(f"Failed to generate visual HTML report: {str(e)}") from e
    
    async def generate_batch_report(self, data: List[Dict[str, Any]]) -> ReportResult:
        """Generate a batch visual HTML report from multiple analysis results.
        
        Args:
            data: List of dictionaries containing analysis results.
        
        Returns:
            ReportResult containing the generated HTML and metadata.
        
        Raises:
            ReportGenerationError: If report generation fails.
        """
        try:
            if not data:
                raise ValueError("No data provided for batch report")
            
            # Aggregate the results
            aggregated_data = self._aggregate_results(data)
            
            # Generate the report
            return await self.generate_report(aggregated_data)
            
        except Exception as e:
            logger.exception(f"Error generating batch visual HTML report: {e}")
            raise ReportGenerationError(f"Failed to generate batch visual HTML report: {str(e)}") from e 