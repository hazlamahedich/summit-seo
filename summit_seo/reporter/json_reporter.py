"""JSON reporter module for Summit SEO."""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseReporter, ReportResult, ReportGenerationError

class JSONReporter(BaseReporter):
    """Reporter for generating JSON reports."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the JSON reporter.
        
        Args:
            config: Optional configuration dictionary.
                   Supported keys:
                   - indent: Number of spaces for indentation (default: 2)
                   - sort_keys: Whether to sort dictionary keys (default: True)
                   - ensure_ascii: Whether to escape non-ASCII characters (default: False)
                   - include_metadata: Whether to include report metadata (default: True)
        """
        super().__init__(config)

    def validate_config(self) -> None:
        """Validate the reporter configuration.
        
        Raises:
            ValueError: If configuration is invalid.
        """
        if 'indent' in self.config and not isinstance(self.config['indent'], int):
            raise ValueError("indent must be an integer")
        
        if 'sort_keys' in self.config and not isinstance(self.config['sort_keys'], bool):
            raise ValueError("sort_keys must be a boolean")
        
        if 'ensure_ascii' in self.config and not isinstance(self.config['ensure_ascii'], bool):
            raise ValueError("ensure_ascii must be a boolean")
        
        if 'include_metadata' in self.config and not isinstance(self.config['include_metadata'], bool):
            raise ValueError("include_metadata must be a boolean")

    def _format_datetime(self, dt: datetime) -> str:
        """Format datetime object as ISO 8601 string.
        
        Args:
            dt: Datetime object to format.
        
        Returns:
            ISO 8601 formatted string.
        """
        return dt.isoformat()

    def _prepare_report_data(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prepare data for JSON serialization.
        
        Args:
            data: Analysis results data.
            metadata: Optional metadata to include.
        
        Returns:
            Dictionary ready for JSON serialization.
        """
        report_data = {
            'url': data['url'],
            'timestamp': data['timestamp'],
            'results': {}
        }
        
        # Format analyzer results
        for analyzer, result in data['results'].items():
            report_data['results'][analyzer] = {
                'score': result['score'],
                'issues': result.get('issues', []),
                'warnings': result.get('warnings', []),
                'suggestions': result.get('suggestions', [])
            }
        
        # Include metadata if configured
        if self.config.get('include_metadata', True) and metadata:
            report_data['metadata'] = metadata
        
        return report_data

    async def generate_report(self, data: Dict[str, Any]) -> ReportResult:
        """Generate a JSON report from the analysis results.
        
        Args:
            data: Dictionary containing analysis results.
        
        Returns:
            ReportResult containing the generated JSON and metadata.
        
        Raises:
            ReportGenerationError: If report generation fails.
        """
        try:
            self._validate_data(data)
            
            metadata = self._create_metadata('json')
            report_data = self._prepare_report_data(
                data,
                metadata.__dict__ if self.config.get('include_metadata', True) else None
            )
            
            json_content = json.dumps(
                report_data,
                indent=self.config.get('indent', 2),
                sort_keys=self.config.get('sort_keys', True),
                ensure_ascii=self.config.get('ensure_ascii', False),
                default=str  # Handle datetime objects
            )
            
            return ReportResult(
                content=json_content,
                metadata=metadata,
                format='json'
            )
            
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate JSON report: {str(e)}")

    async def generate_batch_report(self, data: List[Dict[str, Any]]) -> ReportResult:
        """Generate a JSON report for multiple analysis results.
        
        Args:
            data: List of dictionaries containing analysis results.
        
        Returns:
            ReportResult containing the generated JSON and metadata.
        
        Raises:
            ReportGenerationError: If report generation fails.
        """
        try:
            self._validate_batch_data(data)
            
            metadata = self._create_metadata('json')
            batch_data = {
                'type': 'batch_report',
                'count': len(data),
                'timestamp': self._format_datetime(datetime.utcnow()),
                'results': []
            }
            
            # Process each result
            for item in data:
                result_data = self._prepare_report_data(item)
                batch_data['results'].append(result_data)
            
            # Include metadata if configured
            if self.config.get('include_metadata', True):
                batch_data['metadata'] = metadata.__dict__
            
            json_content = json.dumps(
                batch_data,
                indent=self.config.get('indent', 2),
                sort_keys=self.config.get('sort_keys', True),
                ensure_ascii=self.config.get('ensure_ascii', False),
                default=str  # Handle datetime objects
            )
            
            return ReportResult(
                content=json_content,
                metadata=metadata,
                format='json'
            )
            
        except Exception as e:
            raise ReportGenerationError(
                f"Failed to generate batch JSON report: {str(e)}"
            ) 