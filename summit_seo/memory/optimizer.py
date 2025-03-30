"""Memory optimization functionality for Summit SEO."""

import gc
import inspect
import logging
import sys
import threading
import time
import weakref
from dataclasses import is_dataclass
from enum import Enum, auto
from functools import lru_cache, wraps
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, TypeVar, Union, cast

from .limiter import LimitAction, MemoryLimiter
from .monitor import MemoryMonitor, MemoryUnit
from .utils import (
    CachedProperty, WeakList, enable_object_pooling, get_detailed_memory_report,
    get_memory_footprint_summary, get_size, memory_optimize_dataclass
)

logger = logging.getLogger(__name__)
T = TypeVar('T')


class OptimizationStrategy(str, Enum):
    """Memory optimization strategies."""

    SLOTS = "slots"  # Use __slots__ to reduce memory usage
    WEAK_REFS = "weak_refs"  # Use weak references
    POOLING = "pooling"  # Use object pooling
    LAZY_LOADING = "lazy_loading"  # Use lazy loading of attributes
    CACHING = "caching"  # Use caching
    GC_OPTIMIZATION = "gc_optimization"  # Optimize garbage collection
    LIMIT_COLLECTION = "limit_collection"  # Limit size of collections
    COMPRESSION = "compression"  # Use compression
    ON_DEMAND = "on_demand"  # Load only when needed


class OptimizationLevel(Enum):
    """Optimization level for memory operations."""

    NONE = auto()  # No optimization
    MINIMAL = auto()  # Basic optimizations
    MODERATE = auto()  # Moderate optimizations
    AGGRESSIVE = auto()  # Aggressive optimizations
    EXTREME = auto()  # Extreme optimizations


class OptimizationConfig:
    """Configuration for memory optimization."""

    def __init__(
        self,
        level: OptimizationLevel = OptimizationLevel.MODERATE,
        strategies: Optional[List[OptimizationStrategy]] = None,
        max_collection_size: int = 10000,
        pool_size: int = 100,
        cache_size: int = 1000,
        optimize_dataclasses: bool = True,
        enable_gc_optimization: bool = True,
        auto_monitor: bool = True,
        auto_limit: bool = True,
        compression_level: int = 6  # 0-9, higher is more compression
    ):
        """Initialize optimization configuration.

        Args:
            level: Overall optimization level
            strategies: Specific strategies to enable or None for level default
            max_collection_size: Maximum size for collections
            pool_size: Maximum size for object pools
            cache_size: Maximum size for caches
            optimize_dataclasses: Whether to optimize dataclasses
            enable_gc_optimization: Whether to optimize garbage collection
            auto_monitor: Whether to automatically monitor memory usage
            auto_limit: Whether to automatically limit memory usage
            compression_level: Compression level for compression strategy
        """
        self.level = level
        self.strategies = strategies or self._get_default_strategies(level)
        self.max_collection_size = max_collection_size
        self.pool_size = pool_size
        self.cache_size = cache_size
        self.optimize_dataclasses = optimize_dataclasses
        self.enable_gc_optimization = enable_gc_optimization
        self.auto_monitor = auto_monitor
        self.auto_limit = auto_limit
        self.compression_level = compression_level

    def _get_default_strategies(self, level: OptimizationLevel) -> List[OptimizationStrategy]:
        """Get default optimization strategies for a given level.

        Args:
            level: Optimization level

        Returns:
            List of strategies to apply
        """
        if level == OptimizationLevel.NONE:
            return []
        elif level == OptimizationLevel.MINIMAL:
            return [
                OptimizationStrategy.GC_OPTIMIZATION,
                OptimizationStrategy.CACHING
            ]
        elif level == OptimizationLevel.MODERATE:
            return [
                OptimizationStrategy.GC_OPTIMIZATION,
                OptimizationStrategy.CACHING,
                OptimizationStrategy.SLOTS,
                OptimizationStrategy.LIMIT_COLLECTION
            ]
        elif level == OptimizationLevel.AGGRESSIVE:
            return [
                OptimizationStrategy.GC_OPTIMIZATION,
                OptimizationStrategy.CACHING,
                OptimizationStrategy.SLOTS,
                OptimizationStrategy.WEAK_REFS,
                OptimizationStrategy.POOLING,
                OptimizationStrategy.LIMIT_COLLECTION,
                OptimizationStrategy.ON_DEMAND
            ]
        elif level == OptimizationLevel.EXTREME:
            return [
                OptimizationStrategy.GC_OPTIMIZATION,
                OptimizationStrategy.CACHING,
                OptimizationStrategy.SLOTS,
                OptimizationStrategy.WEAK_REFS,
                OptimizationStrategy.POOLING,
                OptimizationStrategy.LIMIT_COLLECTION,
                OptimizationStrategy.COMPRESSION,
                OptimizationStrategy.ON_DEMAND,
                OptimizationStrategy.LAZY_LOADING
            ]
        return []

    def has_strategy(self, strategy: OptimizationStrategy) -> bool:
        """Check if a strategy is enabled.

        Args:
            strategy: Strategy to check

        Returns:
            True if the strategy is enabled
        """
        return strategy in self.strategies

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "level": self.level.name,
            "strategies": [s for s in self.strategies],
            "max_collection_size": self.max_collection_size,
            "pool_size": self.pool_size,
            "cache_size": self.cache_size,
            "optimize_dataclasses": self.optimize_dataclasses,
            "enable_gc_optimization": self.enable_gc_optimization,
            "auto_monitor": self.auto_monitor,
            "auto_limit": self.auto_limit,
            "compression_level": self.compression_level
        }


class MemoryOptimizer:
    """Memory optimizer for reducing memory usage in Summit SEO."""

    def __init__(
        self,
        config: Optional[OptimizationConfig] = None,
        monitor: Optional[MemoryMonitor] = None,
        limiter: Optional[MemoryLimiter] = None
    ):
        """Initialize memory optimizer.

        Args:
            config: Optimization configuration
            monitor: Memory monitor for tracking memory usage
            limiter: Memory limiter for limiting memory usage
        """
        self.config = config or OptimizationConfig()
        self.monitor = monitor
        self.limiter = limiter
        self._optimized_classes: Dict[Type, Set[OptimizationStrategy]] = {}
        self._optimization_lock = threading.RLock()
        
        # Set up monitoring and limiting if requested
        if self.config.auto_monitor and not monitor:
            self.monitor = MemoryMonitor()
            self.monitor.start_monitoring()
            
        if self.config.auto_limit and not limiter and self.monitor:
            self.limiter = MemoryLimiter(monitor=self.monitor)
            self._configure_default_limits()
            self.limiter.start()
            
        # Optimize garbage collection if requested
        if self.config.enable_gc_optimization:
            self._optimize_garbage_collection()
            
    def _configure_default_limits(self):
        """Configure default memory limits based on available memory."""
        if not self.limiter:
            return
            
        # Configure some reasonable default limits
        self.limiter.add_threshold(
            limit=70,
            action=LimitAction.WARN,
            limit_unit=MemoryUnit.PERCENT,
            description="Memory usage above 70%"
        )
        
        self.limiter.add_threshold(
            limit=80,
            action=LimitAction.GC,
            limit_unit=MemoryUnit.PERCENT,
            description="Memory usage above 80%, run garbage collection"
        )
        
        self.limiter.add_threshold(
            limit=90,
            action=LimitAction.THROTTLE,
            limit_unit=MemoryUnit.PERCENT,
            description="Memory usage above 90%, throttle processing"
        )
        
        self.limiter.add_threshold(
            limit=95,
            action=LimitAction.ERROR,
            limit_unit=MemoryUnit.PERCENT,
            description="Memory usage above 95%, raise error"
        )
            
    def _optimize_garbage_collection(self):
        """Optimize garbage collection settings."""
        # Enable garbage collection
        gc.enable()
        
        # Get current thresholds
        thresholds = gc.get_threshold()
        
        # Set more aggressive thresholds based on optimization level
        if self.config.level == OptimizationLevel.AGGRESSIVE:
            gc.set_threshold(700, 10, 5)  # More aggressive collection
        elif self.config.level == OptimizationLevel.EXTREME:
            gc.set_threshold(500, 5, 2)  # Very aggressive collection
            
        logger.debug(f"Garbage collection thresholds: {gc.get_threshold()} (was {thresholds})")
        
    def optimize_class(self, cls: Type[T], strategies: Optional[List[OptimizationStrategy]] = None) -> Type[T]:
        """Optimize a class using the specified or default strategies.

        Args:
            cls: Class to optimize
            strategies: Strategies to apply, or None to use config default

        Returns:
            Optimized class
        """
        if strategies is None:
            strategies = self.config.strategies
            
        with self._optimization_lock:
            # Skip if already optimized with all requested strategies
            if cls in self._optimized_classes:
                existing_strategies = self._optimized_classes[cls]
                if all(s in existing_strategies for s in strategies):
                    return cls
                    
            # Apply each strategy
            for strategy in strategies:
                if strategy == OptimizationStrategy.SLOTS:
                    cls = self._optimize_slots(cls)
                elif strategy == OptimizationStrategy.POOLING:
                    cls = self._optimize_pooling(cls)
                elif strategy == OptimizationStrategy.CACHING:
                    cls = self._optimize_caching(cls)
                    
            # Track optimized classes
            if cls not in self._optimized_classes:
                self._optimized_classes[cls] = set()
            self._optimized_classes[cls].update(strategies)
            
        return cls
        
    def _optimize_slots(self, cls: Type[T]) -> Type[T]:
        """Optimize a class using __slots__.

        Args:
            cls: Class to optimize

        Returns:
            Optimized class
        """
        # Skip if already has slots
        if hasattr(cls, "__slots__"):
            return cls
            
        # For dataclasses, use special optimization
        if is_dataclass(cls):
            return memory_optimize_dataclass(cls)
            
        # For regular classes, add slots based on instance attributes
        attrs = set()
        # Check class namespace for attributes
        for name, value in cls.__dict__.items():
            if not name.startswith('__') and not inspect.isfunction(value) and not inspect.ismethod(value):
                attrs.add(name)
                
        # Don't override existing slots
        if hasattr(cls, "__slots__"):
            return cls
            
        # Create a new class with slots
        namespace = {
            "__slots__": tuple(attrs),
            **{name: getattr(cls, name) for name in dir(cls) if not name.startswith('__')}
        }
        
        # Create new class with slots
        new_cls = type(cls.__name__, cls.__bases__, namespace)
        
        logger.debug(f"Optimized {cls.__name__} with slots: {namespace['__slots__']}")
        
        return cast(Type[T], new_cls)
        
    def _optimize_pooling(self, cls: Type[T]) -> Type[T]:
        """Optimize a class using object pooling.

        Args:
            cls: Class to optimize

        Returns:
            Optimized class with pooling
        """
        # Skip if already pooled
        if hasattr(cls, "clear_pool") and hasattr(cls, "get_pool_size"):
            return cls
            
        return cast(Type[T], enable_object_pooling(cls, max_size=self.config.pool_size))
        
    def _optimize_caching(self, cls: Type[T]) -> Type[T]:
        """Optimize a class by adding caching.

        Args:
            cls: Class to optimize

        Returns:
            Optimized class with caching
        """
        # Find methods that could benefit from caching
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            # Skip magic methods and already cached/decorated methods
            if name.startswith('__') or hasattr(method, '_cached'):
                continue
                
            # Skip methods with side effects or that modify state
            if name.startswith(('set_', 'delete_', 'remove_', 'clear_', 'update_')):
                continue
                
            # If it's a property, consider using CachedProperty
            if isinstance(getattr(cls, name, None), property):
                prop = getattr(cls, name)
                setattr(cls, name, CachedProperty(prop.fget))
                logger.debug(f"Converted property {cls.__name__}.{name} to CachedProperty")
            
            # Otherwise consider adding lru_cache
            elif not name.startswith('_'):  # Skip private methods
                original_method = getattr(cls, name)
                
                @wraps(original_method)
                def cached_method(self, *args, **kwargs):
                    # Create a cache key based on args and kwargs
                    cache_name = f"_cache_{name}"
                    if not hasattr(self, cache_name):
                        setattr(self, cache_name, {})
                    cache = getattr(self, cache_name)
                    
                    # Create a cache key (limited to hashable args)
                    try:
                        key = (args, tuple(sorted(kwargs.items())))
                        if key in cache:
                            return cache[key]
                    except TypeError:
                        # If args are not hashable, fall back to no caching
                        return original_method(self, *args, **kwargs)
                        
                    result = original_method(self, *args, **kwargs)
                    cache[key] = result
                    return result
                    
                cached_method._cached = True  # Mark as cached
                
                # Replace the original method with the cached version
                setattr(cls, name, cached_method)
                logger.debug(f"Added method caching for {cls.__name__}.{name}")
                
        return cls
        
    def optimize_collections(self, collections: List[Any]) -> None:
        """Optimize a list of collections for memory usage.

        Args:
            collections: List of collections to optimize
        """
        # Apply collection size limits if configured
        if OptimizationStrategy.LIMIT_COLLECTION in self.config.strategies:
            for collection in collections:
                if hasattr(collection, "__len__") and len(collection) > self.config.max_collection_size:
                    # Truncate collection if it's too big
                    if isinstance(collection, list):
                        del collection[self.config.max_collection_size:]
                    elif isinstance(collection, dict):
                        keys = list(collection.keys())[self.config.max_collection_size:]
                        for key in keys:
                            del collection[key]
                    elif isinstance(collection, set):
                        items = list(collection)
                        collection.clear()
                        collection.update(items[:self.config.max_collection_size])
                        
                    logger.debug(f"Limited collection size to {self.config.max_collection_size}")
        
    def lazy_load(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator for lazy-loading a value.

        Args:
            func: Function to decorate

        Returns:
            Decorated function that lazily loads its result
        """
        if not OptimizationStrategy.LAZY_LOADING in self.config.strategies:
            return func
            
        # For properties, use CachedProperty
        if isinstance(func, property):
            return CachedProperty(func.fget)
            
        # For regular methods, use lazy loading wrapper
        @wraps(func)
        def lazy_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return lazy_wrapper
        
    def cached_result(self, maxsize: Optional[int] = None) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """Decorator for caching function results.

        Args:
            maxsize: Maximum cache size or None for default

        Returns:
            Decorator function
        """
        if not OptimizationStrategy.CACHING in self.config.strategies:
            # Return a no-op decorator
            return lambda func: func
            
        # Determine max size based on config
        if maxsize is None:
            maxsize = self.config.cache_size
            
        # Return lru_cache decorator
        return lru_cache(maxsize=maxsize)
        
    def optimize_function(self, func: Callable[..., T]) -> Callable[..., T]:
        """Optimize a function using appropriate strategies.

        Args:
            func: Function to optimize

        Returns:
            Optimized function
        """
        if OptimizationStrategy.CACHING in self.config.strategies:
            # Add caching to the function
            return self.cached_result()(func)
        return func
        
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get a report on memory optimization status.

        Returns:
            Dictionary with optimization information
        """
        report = {
            "config": self.config.to_dict(),
            "optimized_classes": {
                cls.__name__: [s for s in strategies]
                for cls, strategies in self._optimized_classes.items()
            },
            "memory_usage": None,
            "memory_limits": None,
            "memory_details": get_detailed_memory_report()
        }
        
        # Add memory monitoring data if available
        if self.monitor:
            report["memory_usage"] = self.monitor.get_usage_summary()
            
        # Add memory limits if available
        if self.limiter:
            report["memory_limits"] = [
                {
                    "limit": threshold.limit,
                    "unit": threshold.limit_unit.name,
                    "action": threshold.action.name,
                    "description": threshold.description
                }
                for threshold in self.limiter.thresholds
            ]
            
        return report
        
    def optimize_memory_usage(self, aggressive: bool = False) -> None:
        """Optimize current memory usage.

        This forces immediate memory optimization operations.

        Args:
            aggressive: Whether to use aggressive optimization
        """
        # Run garbage collection
        gc.collect()
        
        if aggressive:
            # More aggressive cleanup
            gc.collect(2)  # Full collection
            
            # Clear caches if possible
            if hasattr(sys, "getsizeof") and hasattr(sys, "_clear_type_cache"):
                sys._clear_type_cache()
                
            # Free memory buffers
            if hasattr(gc, "mem_free"):
                gc.mem_free()
                
        logger.info(f"Optimized memory usage (aggressive={aggressive})")
        
    def find_memory_intensive_objects(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Find the most memory-intensive objects in the system.

        Args:
            top_n: Number of top memory users to find

        Returns:
            List of top memory users with details
        """
        # Collect information about top memory users
        gc.collect()
        objects = gc.get_objects()
        
        # Calculate size for each object
        object_sizes = []
        seen = set()
        
        for obj in objects:
            # Skip already seen objects
            obj_id = id(obj)
            if obj_id in seen:
                continue
                
            # Skip built-ins and modules
            if isinstance(obj, (type, module)) or obj is None:
                continue
                
            # Get object size
            obj_size = get_size(obj, deep=True)
            
            if obj_size > 1000:  # Skip very small objects
                object_sizes.append((obj, obj_size))
                seen.add(obj_id)
                
        # Sort by size
        object_sizes.sort(key=lambda x: x[1], reverse=True)
        
        # Get top N
        results = []
        for obj, size in object_sizes[:top_n]:
            obj_type = type(obj).__name__
            summary = get_memory_footprint_summary(obj)
            
            # Get additional info based on type
            extra_info = {}
            if isinstance(obj, dict):
                extra_info["length"] = len(obj)
                if len(obj) > 0:
                    key_sample = str(list(obj.keys())[:3])
                    extra_info["keys_sample"] = key_sample
            elif isinstance(obj, (list, tuple, set)):
                extra_info["length"] = len(obj)
                if len(obj) > 0:
                    item_sample = str(list(obj)[:3])
                    extra_info["items_sample"] = item_sample
            elif hasattr(obj, "__dict__"):
                extra_info["attributes"] = len(obj.__dict__)
                
            results.append({
                "type": obj_type,
                "size_bytes": size,
                "size_human": summary["deep_size_human"],
                "extra_info": extra_info
            })
            
        return results
        
    def monitor_operation(self, operation_name: str) -> "OperationContext":
        """Monitor memory usage during an operation.

        Args:
            operation_name: Name of the operation to monitor

        Returns:
            Context manager for monitoring
        """
        if not self.monitor:
            # Create temporary monitor if none exists
            monitor = MemoryMonitor()
            monitor.start_monitoring()
        else:
            monitor = self.monitor
            
        return OperationContext(operation_name, monitor)
        
    def compact_data_structure(self, data: Any) -> Any:
        """Optimize a data structure for memory usage.

        Applies various strategies to reduce memory usage of the data structure.

        Args:
            data: Data structure to optimize

        Returns:
            Optimized data structure
        """
        # Skip if compression strategy is not enabled
        if not OptimizationStrategy.COMPRESSION in self.config.strategies:
            return data
            
        if isinstance(data, dict):
            # For dictionaries, use compact dict implementations if possible
            if hasattr(sys, "_make_compact_dict"):
                return sys._make_compact_dict(data)
            return data
        elif isinstance(data, list):
            # For lists, convert to tuple if possible (immutable and more memory efficient)
            return tuple(data)
        elif isinstance(data, set):
            # For sets, convert to frozenset if possible
            return frozenset(data)
        else:
            # Return original data if no optimization is possible
            return data


class OperationContext:
    """Context manager for monitoring an operation's memory usage."""
    
    def __init__(self, operation_name: str, monitor: MemoryMonitor):
        """Initialize operation context.
        
        Args:
            operation_name: Name of the operation
            monitor: Memory monitor to use
        """
        self.operation_name = operation_name
        self.monitor = monitor
        self.start_time = None
        self.start_usage = None
        self.peak_usage = None
        self.end_usage = None
        
    def __enter__(self):
        """Enter the context manager.
        
        Returns:
            Self
        """
        self.start_time = time.time()
        self.start_usage = self.monitor.get_current_usage()
        
        logger.debug(f"Starting memory monitoring for operation: {self.operation_name}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        self.end_usage = self.monitor.get_current_usage()
        self.peak_usage = self.monitor.get_max_usage()
        duration = time.time() - self.start_time
        
        # Calculate memory difference
        memory_diff = self.end_usage.rss - self.start_usage.rss
        peak_diff = self.peak_usage.rss - self.start_usage.rss if self.peak_usage else 0
        
        # Log memory usage information
        logger.info(
            f"Memory usage for operation '{self.operation_name}': "
            f"started at {self.start_usage.rss / (1024 * 1024):.2f} MB, "
            f"ended at {self.end_usage.rss / (1024 * 1024):.2f} MB, "
            f"diff: {memory_diff / (1024 * 1024):.2f} MB, "
            f"peak: {(self.peak_usage.rss if self.peak_usage else 0) / (1024 * 1024):.2f} MB "
            f"({peak_diff / (1024 * 1024):.2f} MB increase), "
            f"duration: {duration:.2f}s"
        )
        
        # Don't suppress exceptions
        return False
        
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get usage summary for the operation.
        
        Returns:
            Dictionary with usage summary
        """
        if not self.end_usage:
            return {"status": "in_progress", "operation": self.operation_name}
            
        return {
            "operation": self.operation_name,
            "duration_seconds": time.time() - self.start_time,
            "start_memory_mb": self.start_usage.rss / (1024 * 1024),
            "end_memory_mb": self.end_usage.rss / (1024 * 1024),
            "diff_memory_mb": (self.end_usage.rss - self.start_usage.rss) / (1024 * 1024),
            "peak_memory_mb": (self.peak_usage.rss if self.peak_usage else 0) / (1024 * 1024),
            "peak_diff_mb": ((self.peak_usage.rss if self.peak_usage else 0) - self.start_usage.rss) / (1024 * 1024)
        } 