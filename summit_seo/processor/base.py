"""Base processor module for data processing."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ProcessingResult:
    """Data class for processing results."""
    
    url: str
    processed_data: Dict[str, Any]
    processing_time: float
    timestamp: datetime
    metadata: Dict[str, Any]
    errors: List[str]
    warnings: List[str]

class ProcessorError(Exception):
    """Base exception for processor errors."""
    pass

class ValidationError(ProcessorError):
    """Exception raised for validation errors."""
    pass

class TransformationError(ProcessorError):
    """Exception raised for transformation errors."""
    pass

class BaseProcessor(ABC):
    """Base class for data processors."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the processor.
        
        Args:
            config: Optional configuration dictionary.
        """
        self.config = config or {}
        self.validate_config()
        
        # Initialize processing metrics
        self._processed_count = 0
        self._error_count = 0
        self._start_time = None
        
    @property
    def name(self) -> str:
        """Get the processor name."""
        return self.__class__.__name__
    
    @property
    def processed_count(self) -> int:
        """Get the number of processed items."""
        return self._processed_count
    
    @property
    def error_count(self) -> int:
        """Get the number of processing errors."""
        return self._error_count
    
    def validate_config(self) -> None:
        """Validate processor configuration.
        
        Raises:
            ValidationError: If configuration is invalid.
        """
        # Validate common configuration options
        if 'batch_size' in self.config:
            batch_size = self.config['batch_size']
            if not isinstance(batch_size, int) or batch_size < 1:
                raise ValidationError("batch_size must be a positive integer")
        
        if 'max_retries' in self.config:
            max_retries = self.config['max_retries']
            if not isinstance(max_retries, int) or max_retries < 0:
                raise ValidationError("max_retries must be a non-negative integer")
        
        # Allow subclasses to implement additional validation
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Additional configuration validation for subclasses."""
        pass
    
    async def process(self, data: Dict[str, Any], url: str) -> ProcessingResult:
        """Process the input data.
        
        Args:
            data: Input data dictionary.
            url: URL associated with the data.
            
        Returns:
            ProcessingResult containing processed data and metadata.
            
        Raises:
            ProcessorError: If processing fails.
        """
        self._start_time = datetime.now().timestamp()
        errors = []
        warnings = []
        
        try:
            # Validate input data
            self._validate_input(data)
            
            # Process data
            processed_data = await self._process_data(data)
            
            # Validate output
            self._validate_output(processed_data)
            
            self._processed_count += 1
            
        except ValidationError as e:
            errors.append(f"Validation error: {str(e)}")
            self._error_count += 1
            processed_data = {}
            
        except TransformationError as e:
            errors.append(f"Transformation error: {str(e)}")
            self._error_count += 1
            processed_data = {}
            
        except Exception as e:
            errors.append(f"Processing error: {str(e)}")
            self._error_count += 1
            processed_data = {}
        
        processing_time = datetime.now().timestamp() - self._start_time
        
        return ProcessingResult(
            url=url,
            processed_data=processed_data,
            processing_time=processing_time,
            timestamp=datetime.now(),
            metadata=self._get_metadata(),
            errors=errors,
            warnings=warnings
        )
    
    async def process_batch(
        self,
        items: List[Dict[str, Any]]
    ) -> List[ProcessingResult]:
        """Process multiple items in batch.
        
        Args:
            items: List of (data, url) tuples to process.
            
        Returns:
            List of ProcessingResult objects.
        """
        batch_size = self.config.get('batch_size', len(items))
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[self.process(data, url) for data, url in batch],
                return_exceptions=True
            )
            results.extend(batch_results)
        
        return results
    
    def _validate_input(self, data: Dict[str, Any]) -> None:
        """Validate input data.
        
        Args:
            data: Input data dictionary.
            
        Raises:
            ValidationError: If input data is invalid.
        """
        if not isinstance(data, dict):
            raise ValidationError("Input data must be a dictionary")
        
        required_fields = self._get_required_fields()
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )
    
    def _validate_output(self, data: Dict[str, Any]) -> None:
        """Validate processed output data.
        
        Args:
            data: Processed data dictionary.
            
        Raises:
            ValidationError: If output data is invalid.
        """
        if not isinstance(data, dict):
            raise ValidationError("Processed data must be a dictionary")
    
    def _get_metadata(self) -> Dict[str, Any]:
        """Get processor metadata.
        
        Returns:
            Dictionary containing processor metadata.
        """
        return {
            'processor_name': self.name,
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'config': self.config
        }
    
    @abstractmethod
    def _get_required_fields(self) -> List[str]:
        """Get list of required input fields.
        
        Returns:
            List of field names.
        """
        return []
    
    @abstractmethod
    async def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data.
        
        Args:
            data: Input data dictionary.
            
        Returns:
            Processed data dictionary.
            
        Raises:
            TransformationError: If data transformation fails.
        """
        raise NotImplementedError("Subclasses must implement _process_data") 