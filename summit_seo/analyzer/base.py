"""Base analyzer module for SEO analysis."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from ..collector.base import CollectionResult
from .recommendation import Recommendation, RecommendationManager

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
    cached: bool = False
    cache_key: Optional[str] = None

@dataclass
class AnalysisResult(Generic[OutputType]):
    """Container for analysis results."""
    data: OutputType
    metadata: AnalysisMetadata
    score: float
    issues: List[str]
    warnings: List[str]
    recommendations: List[str]
    # Enhanced recommendations with severity, priority, and implementation guidance
    enhanced_recommendations: List[Recommendation] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary.
        
        Returns:
            Dictionary representation of the result
        """
        return {
            'data': self.data,
            'metadata': {
                'timestamp': self.metadata.timestamp.isoformat(),
                'analyzer_type': self.metadata.analyzer_type,
                'version': self.metadata.version,
                'additional_info': self.metadata.additional_info,
                'cached': self.metadata.cached,
                'cache_key': self.metadata.cache_key
            },
            'score': self.score,
            'issues': self.issues,
            'warnings': self.warnings,
            'recommendations': self.recommendations,
            'enhanced_recommendations': [r.to_dict() for r in self.enhanced_recommendations]
        }
    
    def get_priority_recommendations(self) -> List[Recommendation]:
        """Get recommendations sorted by priority.
        
        Returns:
            List of recommendations ordered by priority (highest first)
        """
        if not self.enhanced_recommendations:
            return []
        
        return sorted(self.enhanced_recommendations, key=lambda r: r.priority.value)
    
    def get_severity_recommendations(self) -> List[Recommendation]:
        """Get recommendations sorted by severity.
        
        Returns:
            List of recommendations ordered by severity (most severe first)
        """
        if not self.enhanced_recommendations:
            return []
        
        # Order: CRITICAL, HIGH, MEDIUM, LOW, INFO
        from .recommendation import RecommendationSeverity
        severity_order = {
            RecommendationSeverity.CRITICAL: 0,
            RecommendationSeverity.HIGH: 1,
            RecommendationSeverity.MEDIUM: 2,
            RecommendationSeverity.LOW: 3,
            RecommendationSeverity.INFO: 4
        }
        return sorted(self.enhanced_recommendations, key=lambda r: severity_order[r.severity])
    
    def get_quick_wins(self) -> List[Recommendation]:
        """Get all quick win recommendations.
        
        Returns:
            List of quick win recommendations
        """
        if not self.enhanced_recommendations:
            return []
        
        return [r for r in self.enhanced_recommendations if r.quick_win]

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
        
        # Caching configuration
        self.enable_caching = self.config.get('enable_caching', True)
        self.cache_ttl = self.config.get('cache_ttl', 3600)  # 1 hour default
        self.cache_type = self.config.get('cache_type', 'memory')
        self.cache_namespace = self.config.get('cache_namespace', 'analyzer')
        
        # Recommendation manager
        self.recommendation_manager = RecommendationManager()

    async def analyze(self, data: InputType) -> AnalysisResult[OutputType]:
        """Analyze the input data and return results.
        
        This implementation checks the cache first, and only performs analysis
        if the result is not found in cache or if caching is disabled.
        
        Args:
            data: Input data to analyze
            
        Returns:
            AnalysisResult containing the analysis output
            
        Raises:
            AnalyzerError: If analysis fails
        """
        # Validate input
        self.validate_input(data)
        
        # Check cache if enabled
        if self.enable_caching:
            try:
                from ..cache import cache_manager
                
                # Generate cache key based on analyzer type and input data
                cache_key = self.generate_cache_key(data)
                
                # Try to get result from cache
                cache_result = await cache_manager.get(
                    cache_key, 
                    cache_type=self.cache_type,
                    name=self.get_cache_name()
                )
                
                if cache_result.hit and not cache_result.expired:
                    # Cache hit, return cached result
                    cached_result = cache_result.value
                    
                    # Update metadata to indicate cached result
                    cached_result.metadata.cached = True
                    cached_result.metadata.cache_key = cache_key
                    
                    return cached_result
                    
            except ImportError:
                # Cache module not available, continue with analysis
                pass
            except Exception as e:
                # Log cache error but continue with analysis
                import logging
                logging.warning(f"Cache error in {self.__class__.__name__}: {str(e)}")
        
        # Perform analysis
        result = await self._analyze(data)
        
        # Cache result if caching is enabled
        if self.enable_caching:
            try:
                from ..cache import cache_manager
                
                cache_key = self.generate_cache_key(data)
                
                # Store result in cache
                await cache_manager.set(
                    cache_key,
                    result,
                    ttl=self.cache_ttl,
                    cache_type=self.cache_type,
                    name=self.get_cache_name()
                )
                
                # Update metadata
                result.metadata.cache_key = cache_key
                
            except ImportError:
                # Cache module not available, skip caching
                pass
            except Exception as e:
                # Log cache error
                import logging
                logging.warning(f"Cache error in {self.__class__.__name__}: {str(e)}")
        
        return result

    @abstractmethod
    async def _analyze(self, data: InputType) -> AnalysisResult[OutputType]:
        """Perform the actual analysis.
        
        This method should be implemented by concrete analyzers.
        
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
        
    def generate_cache_key(self, data: InputType) -> str:
        """Generate a cache key based on analyzer type and input data.
        
        Args:
            data: Input data
            
        Returns:
            Cache key string
        """
        # Use analyzer class name as prefix
        prefix = self.__class__.__name__
        
        # Hash the input data
        if isinstance(data, str):
            # For string data, hash directly
            data_hash = hashlib.md5(data.encode('utf-8')).hexdigest()
        elif hasattr(data, 'to_dict'):
            # If data has to_dict method, use it
            data_dict = data.to_dict()
            data_hash = hashlib.md5(json.dumps(data_dict, sort_keys=True).encode('utf-8')).hexdigest()
        else:
            # For other types, use string representation
            data_hash = hashlib.md5(str(data).encode('utf-8')).hexdigest()
        
        # Add config hash if it would affect analysis results
        config_hash = ""
        if self.config:
            # Only include config keys that affect analysis results
            analysis_config = {k: v for k, v in self.config.items() 
                            if k not in ('enable_caching', 'cache_ttl', 'cache_type', 'cache_namespace')}
            
            if analysis_config:
                config_hash = hashlib.md5(json.dumps(analysis_config, sort_keys=True).encode('utf-8')).hexdigest()[:8]
                return f"{prefix}:{data_hash}:{config_hash}"
        
        return f"{prefix}:{data_hash}"
    
    def get_cache_name(self) -> Optional[str]:
        """Get the cache name based on TTL.
        
        Returns:
            Cache name (short, medium, long) or None for default
        """
        if self.cache_ttl <= 300:  # 5 minutes or less
            return 'short'
        elif self.cache_ttl <= 3600:  # 1 hour or less
            return 'medium'
        elif self.cache_ttl <= 86400:  # 24 hours or less
            return 'long'
        
        return None 