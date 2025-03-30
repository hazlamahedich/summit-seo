"""CSV reporter module for Summit SEO."""

import csv
from io import StringIO
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from .base import BaseReporter, ReportResult, ReportGenerationError

class CSVReporter(BaseReporter):
    """Reporter for generating CSV reports."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the CSV reporter.
        
        Args:
            config: Optional configuration dictionary.
                   Supported keys:
                   - delimiter: CSV delimiter (default: ',')
                   - quotechar: Quote character (default: '"')
                   - include_headers: Whether to include headers (default: True)
                   - flatten_lists: Whether to flatten list fields (default: True)
                   - list_separator: Separator for flattened lists (default: ';')
                   - newline: Line ending character (default: '\\n')
        """
        super().__init__(config)

    def validate_config(self) -> None:
        """Validate the reporter configuration.
        
        Raises:
            ValueError: If configuration is invalid.
        """
        if 'delimiter' in self.config and not isinstance(self.config['delimiter'], str):
            raise ValueError("delimiter must be a string")
        
        if 'quotechar' in self.config and not isinstance(self.config['quotechar'], str):
            raise ValueError("quotechar must be a string")
        
        if 'include_headers' in self.config and not isinstance(self.config['include_headers'], bool):
            raise ValueError("include_headers must be a boolean")
        
        if 'flatten_lists' in self.config and not isinstance(self.config['flatten_lists'], bool):
            raise ValueError("flatten_lists must be a boolean")
        
        if 'list_separator' in self.config and not isinstance(self.config['list_separator'], str):
            raise ValueError("list_separator must be a string")

    def _get_csv_writer(self, output: StringIO) -> csv.writer:
        """Create a CSV writer with the configured settings.
        
        Args:
            output: StringIO object to write to.
        
        Returns:
            csv.writer instance.
        """
        return csv.writer(
            output,
            delimiter=self.config.get('delimiter', ','),
            quotechar=self.config.get('quotechar', '"'),
            quoting=csv.QUOTE_MINIMAL,
            lineterminator=self.config.get('newline', '\n')
        )

    def _get_headers(self, data: Dict[str, Any]) -> List[str]:
        """Generate CSV headers from data structure.
        
        Args:
            data: Analysis results data.
        
        Returns:
            List of header strings.
        """
        headers = ['URL', 'Timestamp']
        
        # Add analyzer-specific headers
        for analyzer, result in data['results'].items():
            headers.append(f"{analyzer}_score")
            
            if self.config.get('flatten_lists', True):
                if result.get('issues'):
                    headers.append(f"{analyzer}_issues")
                if result.get('warnings'):
                    headers.append(f"{analyzer}_warnings")
                if result.get('suggestions'):
                    headers.append(f"{analyzer}_suggestions")
        
        return headers

    def _prepare_row(self, data: Dict[str, Any], headers: List[str]) -> List[str]:
        """Prepare a row of data for CSV output.
        
        Args:
            data: Analysis results data.
            headers: List of headers to match.
        
        Returns:
            List of values matching headers.
        """
        row = []
        list_separator = self.config.get('list_separator', ';')
        
        for header in headers:
            if header == 'URL':
                row.append(data['url'])
            elif header == 'Timestamp':
                row.append(data['timestamp'])
            else:
                # Handle analyzer-specific fields
                parts = header.split('_')
                analyzer = '_'.join(parts[:-1])  # Handle analyzers with underscores
                field = parts[-1]
                
                if field == 'score':
                    row.append(str(data['results'][analyzer]['score']))
                elif field in ('issues', 'warnings', 'suggestions'):
                    items = data['results'][analyzer].get(field, [])
                    row.append(list_separator.join(items) if items else '')
        
        return row

    async def generate_report(self, data: Dict[str, Any]) -> ReportResult:
        """Generate a CSV report from the analysis results.
        
        Args:
            data: Dictionary containing analysis results.
        
        Returns:
            ReportResult containing the generated CSV and metadata.
        
        Raises:
            ReportGenerationError: If report generation fails.
        """
        try:
            self._validate_data(data)
            
            output = StringIO()
            writer = self._get_csv_writer(output)
            headers = self._get_headers(data)
            
            # Write headers if configured
            if self.config.get('include_headers', True):
                writer.writerow(headers)
            
            # Write data row
            row = self._prepare_row(data, headers)
            writer.writerow(row)
            
            metadata = self._create_metadata('csv')
            return ReportResult(
                content=output.getvalue(),
                metadata=metadata,
                format='csv'
            )
            
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate CSV report: {str(e)}")

    async def generate_batch_report(self, data: List[Dict[str, Any]]) -> ReportResult:
        """Generate a CSV report for multiple analysis results.
        
        Args:
            data: List of dictionaries containing analysis results.
        
        Returns:
            ReportResult containing the generated CSV and metadata.
        
        Raises:
            ReportGenerationError: If report generation fails.
        """
        try:
            self._validate_batch_data(data)
            
            output = StringIO()
            writer = self._get_csv_writer(output)
            
            # Get all unique headers from all results
            all_headers = set()
            for item in data:
                all_headers.update(self._get_headers(item))
            headers = sorted(list(all_headers))
            
            # Write headers if configured
            if self.config.get('include_headers', True):
                writer.writerow(headers)
            
            # Write data rows
            for item in data:
                row = self._prepare_row(item, headers)
                writer.writerow(row)
            
            metadata = self._create_metadata('csv')
            return ReportResult(
                content=output.getvalue(),
                metadata=metadata,
                format='csv'
            )
            
        except Exception as e:
            raise ReportGenerationError(
                f"Failed to generate batch CSV report: {str(e)}"
            ) 