"""Base reporter module for Summit SEO."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional, List

@dataclass
class ReportMetadata:
    """Metadata for a generated report."""
    timestamp: datetime
    format: str
    version: str
    generator: str = "Summit SEO Reporter"

@dataclass
class ReportResult:
    """Result of a report generation."""
    content: Any
    metadata: ReportMetadata
    format: str

class ReporterError(Exception):
    """Base exception for reporter errors."""
    pass

class ReportGenerationError(ReporterError):
    """Exception raised when report generation fails."""
    pass

class ReportFormatError(ReporterError):
    """Exception raised when report format is invalid."""
    pass

class BaseReporter(ABC):
    """Base class for all reporters."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the reporter.
        
        Args:
            config: Optional configuration dictionary for the reporter.
        """
        self.config = config or {}
        self.validate_config()

    @abstractmethod
    def validate_config(self) -> None:
        """Validate the reporter configuration.
        
        Raises:
            ValueError: If configuration is invalid.
        """
        pass

    @abstractmethod
    async def generate_report(self, data: Dict[str, Any]) -> ReportResult:
        """Generate a report from the provided data.
        
        Args:
            data: Dictionary containing analysis results.
        
        Returns:
            ReportResult containing the generated report and metadata.
        
        Raises:
            ReportGenerationError: If report generation fails.
            ReportFormatError: If output format is invalid.
        """
        pass

    @abstractmethod
    async def generate_batch_report(self, data: List[Dict[str, Any]]) -> ReportResult:
        """Generate a report for multiple analysis results.
        
        Args:
            data: List of dictionaries containing analysis results.
        
        Returns:
            ReportResult containing the generated report and metadata.
        
        Raises:
            ReportGenerationError: If report generation fails.
            ReportFormatError: If output format is invalid.
        """
        pass

    def _create_metadata(self, format: str) -> ReportMetadata:
        """Create report metadata.
        
        Args:
            format: Output format of the report.
        
        Returns:
            ReportMetadata instance.
        """
        from ... import __version__
        return ReportMetadata(
            timestamp=datetime.utcnow(),
            format=format,
            version=__version__
        )

    def _validate_data(self, data: Dict[str, Any]) -> None:
        """Validate input data structure.
        
        Args:
            data: Dictionary containing analysis results.
        
        Raises:
            ValueError: If data structure is invalid.
        """
        required_fields = {'url', 'timestamp', 'results'}
        if not all(field in data for field in required_fields):
            raise ValueError(
                f"Data must contain all required fields: {required_fields}"
            )
        
        if not isinstance(data['results'], dict):
            raise ValueError("Results must be a dictionary")

    def _validate_batch_data(self, data: List[Dict[str, Any]]) -> None:
        """Validate batch input data structure.
        
        Args:
            data: List of dictionaries containing analysis results.
        
        Raises:
            ValueError: If data structure is invalid.
        """
        if not isinstance(data, list):
            raise ValueError("Batch data must be a list")
        
        if not data:
            raise ValueError("Batch data cannot be empty")
        
        for item in data:
            self._validate_data(item) 