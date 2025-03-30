"""YAML reporter implementation."""

from typing import Any, Dict, Optional
from datetime import datetime

import yaml

from .base import BaseReporter, Report, InputType


class YAMLReporter(BaseReporter[Dict[str, Any]]):
    """Reporter that generates reports in YAML format.
    
    This reporter takes dictionary input data and produces YAML formatted reports.
    It includes options for customizing the YAML output format.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the YAML reporter.
        
        Args:
            config: Optional configuration dictionary that may include:
                - default_flow_style: YAML flow style (default: False)
                - indent: Number of spaces for indentation (default: 2)
                - allow_unicode: Whether to allow unicode (default: True)
                - sort_keys: Whether to sort dictionary keys (default: True)
        """
        super().__init__(config or {})
        self.default_flow_style = self.config.get('default_flow_style', False)
        self.indent = self.config.get('indent', 2)
        self.allow_unicode = self.config.get('allow_unicode', True)
        self.sort_keys = self.config.get('sort_keys', True)

    def generate_report(self, data: Dict[str, Any], report_format: str = 'yaml') -> Report:
        """Generate a YAML report from the input data.
        
        Args:
            data: Dictionary containing the data to be reported
            report_format: Must be 'yaml' (ignored as this is a YAML-specific reporter)
            
        Returns:
            Report object containing the YAML formatted data
            
        Raises:
            ReportingError: If data validation fails
        """
        self.validate_data(data)
        self.validate_format(report_format)
        
        metadata = self.create_metadata(report_type='yaml')
        formatted_data = self.format_data(data)
        
        return Report(
            data=formatted_data,
            metadata=metadata
        )

    def format_data(self, data: Dict[str, Any]) -> str:
        """Format the data as a YAML string.
        
        Args:
            data: Dictionary to be converted to YAML
            
        Returns:
            YAML formatted string
        """
        try:
            return yaml.dump(
                data,
                default_flow_style=self.default_flow_style,
                indent=self.indent,
                allow_unicode=self.allow_unicode,
                sort_keys=self.sort_keys,
                default_style=None,
                Dumper=self._get_yaml_dumper()
            )
        except Exception as e:
            raise self.error_type(f"Failed to format data as YAML: {str(e)}")

    def _get_yaml_dumper(self) -> type:
        """Get a configured YAML Dumper class.
        
        Returns:
            A YAML Dumper class configured to handle datetime objects
        """
        class DatetimeDumper(yaml.SafeDumper):
            pass
        
        def datetime_representer(dumper: yaml.SafeDumper, data: datetime) -> yaml.ScalarNode:
            return dumper.represent_scalar('tag:yaml.org,2002:timestamp', data.isoformat())
        
        DatetimeDumper.add_representer(datetime, datetime_representer)
        return DatetimeDumper 