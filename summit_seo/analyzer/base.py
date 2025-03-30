"""Base analyzer module for SEO analysis."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from ..collector.base import CollectionResult

# Type variable for analyzer input
InputType = TypeVar('InputType')
# Type variable for analyzer output
OutputType = TypeVar('OutputType')

@dataclass
class AnalysisMetadata:
    """Metadata for analysis results."""
    timestamp: datetime
    analyzer_type: str
    version: str = '1.0.0'
    additional_info: Optional[Dict[str, Any]] = None

@dataclass
class AnalysisResult(Generic[OutputType]):
    """Container for analysis results."""
    data: OutputType
    metadata: AnalysisMetadata
    score: float
    issues: List[str]
    warnings: List[str]
    recommendations: List[str]

class AnalyzerError(Exception):
    """Base exception for analyzer errors."""
    pass

class BaseAnalyzer(ABC, Generic[InputType, OutputType]):
    """Abstract base class for SEO analyzers.
    
    This class defines the interface that all SEO analyzers must implement.
    It provides a common structure for analyzing different aspects of SEO
    and generating standardized results.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the analyzer.
        
        Args:
            config: Optional configuration dictionary for customizing analyzer behavior
        """
        self.config = config or {}
        self.error_type = AnalyzerError

    @abstractmethod
    def analyze(self, data: InputType) -> AnalysisResult[OutputType]:
        """Analyze the input data and return results.
        
        Args:
            data: Input data to analyze
            
        Returns:
            AnalysisResult containing the analysis output
            
        Raises:
            AnalyzerError: If analysis fails
        """
        pass

    def validate_input(self, data: InputType) -> None:
        """Validate the input data before analysis.
        
        Args:
            data: Input data to validate
            
        Raises:
            AnalyzerError: If validation fails
        """
        if data is None:
            raise self.error_type("Input data cannot be None")

    def create_metadata(self, analyzer_type: str) -> AnalysisMetadata:
        """Create metadata for the analysis result.
        
        Args:
            analyzer_type: Type of analyzer generating the result
            
        Returns:
            AnalysisMetadata object
        """
        return AnalysisMetadata(
            timestamp=datetime.now(),
            analyzer_type=analyzer_type,
            version=self.config.get('version', '1.0.0'),
            additional_info=self.config.get('additional_info')
        )

    def calculate_score(self, issues: List[str], warnings: List[str]) -> float:
        """Calculate an overall score based on issues and warnings.
        
        Args:
            issues: List of critical issues found
            warnings: List of warnings found
            
        Returns:
            Float score between 0 and 1
        """
        # Start with perfect score
        score = 1.0
        
        # Deduct for issues and warnings
        issue_weight = self.config.get('issue_weight', 0.1)
        warning_weight = self.config.get('warning_weight', 0.05)
        
        score -= len(issues) * issue_weight
        score -= len(warnings) * warning_weight
        
        # Ensure score stays between 0 and 1
        return max(0.0, min(1.0, score))

    def format_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Format an analysis message with optional context.
        
        Args:
            message: Base message to format
            context: Optional context dictionary for message formatting
            
        Returns:
            Formatted message string
        """
        if context:
            try:
                return message.format(**context)
            except KeyError as e:
                raise self.error_type(f"Missing context key in message format: {e}")
            except Exception as e:
                raise self.error_type(f"Failed to format message: {str(e)}")
        return message

    def validate_data(self, data: CollectionResult) -> None:
        """
        Validate the input data before analysis.
        
        Args:
            data: The collected data to validate
            
        Raises:
            AnalyzerError: If data validation fails
        """
        if not data:
            raise self.error_type("No data provided for analysis")
    
    def normalize_score(self, raw_score: float) -> float:
        """
        Normalize a raw score to be between 0 and 1.
        
        Args:
            raw_score: The raw score to normalize
            
        Returns:
            float: Normalized score between 0 and 1
        """
        return max(0.0, min(1.0, raw_score)) 