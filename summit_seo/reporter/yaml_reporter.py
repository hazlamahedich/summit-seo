"""YAML reporter implementation."""

from typing import Any, Dict, Optional, List
from datetime import datetime
from pathlib import Path

import yaml

from .base import BaseReporter, ReportResult, ReportGenerationError

class YAMLReporter(BaseReporter):
    """Reporter that generates reports in YAML format."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the YAML reporter.
        
        Args:
            config: Optional configuration dictionary. Supported keys:
                - default_flow_style: YAML flow style (default: False)
                - indent: Number of spaces for indentation (default: 2)
                - allow_unicode: Whether to allow unicode (default: True)
                - sort_keys: Whether to sort dictionary keys (default: True)
        """
        super().__init__(config)
        
    def validate_config(self) -> None:
        """Validate the reporter configuration.
        
        Raises:
            ValueError: If configuration is invalid.
        """
        if 'indent' in self.config and not isinstance(self.config['indent'], int):
            raise ValueError("Indent must be an integer")
            
    async def generate_report(self, data: Dict[str, Any]) -> ReportResult:
        """Generate a YAML report from the analysis results.
        
        Args:
            data: Dictionary containing analysis results.
        
        Returns:
            ReportResult containing the generated YAML and metadata.
        
        Raises:
            ReportGenerationError: If report generation fails.
        """
        try:
            self._validate_data(data)
            
            # Set YAML dumper options
            yaml_options = {
                'default_flow_style': self.config.get('default_flow_style', False),
                'indent': self.config.get('indent', 2),
                'allow_unicode': self.config.get('allow_unicode', True),
                'sort_keys': self.config.get('sort_keys', True)
            }
            
            # Convert data to YAML
            yaml_content = yaml.dump(data, **yaml_options)
            
            # Get the output file path from the data or use a default
            output_file = data.get('output_file', 'seo_report.yaml')
            
            # If output_file is a Path object, convert to string
            if isinstance(output_file, Path):
                output_file = str(output_file)
            
            # Write the report to the output file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            
            # Create the report result
            result = ReportResult(
                content=yaml_content,
                format='yaml',
                path=output_file,
                metadata={
                    'timestamp': data.get('timestamp', datetime.now().isoformat()),
                    'url': data.get('url', 'Unknown')
                }
            )
            
            return result
            
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate YAML report: {str(e)}") from e
            
    async def generate_batch_report(self, data: List[Dict[str, Any]]) -> ReportResult:
        """Generate a batch YAML report from multiple analysis results.
        
        Args:
            data: List of dictionaries containing analysis results.
        
        Returns:
            ReportResult containing the generated YAML and metadata.
        
        Raises:
            ReportGenerationError: If report generation fails.
        """
        try:
            if not data:
                raise ValueError("No data provided for batch report")
            
            # Aggregate the results
            aggregated_data = {
                'url': 'Multiple URLs',
                'timestamp': datetime.now().isoformat(),
                'urls': [item.get('url', 'Unknown') for item in data],
                'results': {}
            }
            
            # Combine all results
            for item in data:
                if 'results' in item and isinstance(item['results'], dict):
                    for analyzer, result in item['results'].items():
                        if analyzer not in aggregated_data['results']:
                            aggregated_data['results'][analyzer] = []
                        aggregated_data['results'][analyzer].append(result)
            
            # Generate the report
            return await self.generate_report(aggregated_data)
            
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate batch YAML report: {str(e)}") from e 