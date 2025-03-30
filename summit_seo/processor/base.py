"""Base processor module for data processing."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json

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
    cached: bool = False
    cache_key: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary.
        
        Returns:
            Dictionary representation of the result
        """
        return {
            'url': self.url,
            'processing_time': self.processing_time,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'errors': self.errors,
            'warnings': self.warnings,
            'cached': self.cached,
            'cache_key': self.cache_key
            # Note: processed_data is excluded to avoid large dictionaries
        }

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
            config: Optional configuration dictionary with settings like:
                - batch_size: Size of batches for batch processing (int)
                - max_retries: Maximum number of retries for processing (int)
                - enable_caching: Whether to enable caching (bool)
                - cache_ttl: Cache time to live in seconds (int)
                - cache_type: Type of cache to use ('memory' or 'file') (str)
        """
        self.config = config or {}
        self.validate_config()
        
        # Initialize processing metrics
        self._processed_count = 0
        self._error_count = 0
        self._start_time = None
        
        # Caching configuration
        self.enable_caching = self.config.get('enable_caching', True)
        self.cache_ttl = self.config.get('cache_ttl', 3600)  # 1 hour default
        self.cache_type = self.config.get('cache_type', 'memory')
        
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
        
        This implementation checks the cache first, and only performs processing
        if the result is not found in cache or if caching is disabled.
        
        Args:
            data: Input data dictionary.
            url: URL associated with the data.
            
        Returns:
            ProcessingResult containing processed data and metadata.
            
        Raises:
            ProcessorError: If processing fails.
        """
        # Check cache if enabled
        if self.enable_caching:
            try:
                from ..cache import cache_manager
                
                # Generate cache key
                cache_key = self.generate_cache_key(data, url)
                
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
                    cached_result.cached = True
                    cached_result.cache_key = cache_key
                    
                    return cached_result
                    
            except ImportError:
                # Cache module not available, continue with processing
                pass
            except Exception as e:
                # Log cache error but continue with processing
                import logging
                logging.warning(f"Cache error in {self.__class__.__name__}: {str(e)}")
        
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
        
        # Create processing result
        result = ProcessingResult(
            url=url,
            processed_data=processed_data,
            processing_time=processing_time,
            timestamp=datetime.now(),
            metadata=self._get_metadata(),
            errors=errors,
            warnings=warnings
        )
        
        # Cache result if caching is enabled and no errors occurred
        if self.enable_caching and not errors:
            try:
                from ..cache import cache_manager
                
                cache_key = self.generate_cache_key(data, url)
                
                # Store result in cache
                await cache_manager.set(
                    cache_key,
                    result,
                    ttl=self.cache_ttl,
                    cache_type=self.cache_type,
                    name=self.get_cache_name()
                )
                
                # Update cache key in result
                result.cache_key = cache_key
                
            except ImportError:
                # Cache module not available, skip caching
                pass
            except Exception as e:
                # Log cache error
                import logging
                logging.warning(f"Cache error in {self.__class__.__name__}: {str(e)}")
        
        return result
    
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
            'config': {k: v for k, v in self.config.items() if k not in ('enable_caching', 'cache_ttl', 'cache_type')}
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
    
    def generate_cache_key(self, data: Dict[str, Any], url: str) -> str:
        """Generate a cache key for the input data and URL.
        
        Args:
            data: Input data
            url: URL being processed
            
        Returns:
            Cache key string
        """
        # Use processor class name as prefix
        prefix = self.__class__.__name__
        
        # Hash the URL
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()[:8]
        
        # Hash the input data's keys and structure
        # Note: We avoid hashing the entire data which could be large
        data_keys = sorted(data.keys())
        data_structure = f"{len(data)}:{','.join(data_keys)}"
        data_hash = hashlib.md5(data_structure.encode('utf-8')).hexdigest()[:8]
        
        # Include relevant configuration in cache key
        config_hash = ""
        if self.config:
            # Only include config keys that affect processing results
            processing_config = {k: v for k, v in self.config.items() 
                         if k not in ('enable_caching', 'cache_ttl', 'cache_type', 'batch_size')}
            
            if processing_config:
                config_hash = f":{hashlib.md5(json.dumps(processing_config, sort_keys=True).encode('utf-8')).hexdigest()[:8]}"
        
        return f"{prefix}:{url_hash}:{data_hash}{config_hash}"
    
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