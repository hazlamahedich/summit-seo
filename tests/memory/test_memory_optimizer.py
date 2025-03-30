"""Tests for the memory optimizer implementation."""

import gc
import pytest
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any
from unittest.mock import MagicMock, patch

from summit_seo.memory.optimizer import (
    MemoryOptimizer, OptimizationConfig, OptimizationLevel, OptimizationStrategy,
    StreamingOptimizer, LazyLoader
)
from summit_seo.memory.monitor import MemoryMonitor
from summit_seo.memory.limiter import MemoryLimiter


@pytest.fixture
def memory_optimizer():
    """Create a memory optimizer for testing."""
    monitor = MagicMock(spec=MemoryMonitor)
    limiter = MagicMock(spec=MemoryLimiter)
    optimizer = MemoryOptimizer(
        config=OptimizationConfig(level=OptimizationLevel.MODERATE),
        monitor=monitor,
        limiter=limiter
    )
    return optimizer


class TestOptimizationConfig:
    """Tests for the OptimizationConfig class."""
    
    def test_default_config(self):
        """Test default optimization configuration."""
        config = OptimizationConfig()
        
        # Check default values
        assert config.level == OptimizationLevel.MODERATE
        assert len(config.strategies) > 0
        assert config.max_collection_size == 10000
        assert config.pool_size == 100
        assert config.cache_size == 1000
        assert config.optimize_dataclasses is True
        assert config.enable_gc_optimization is True
        assert config.auto_monitor is True
        assert config.auto_limit is True
        assert 0 <= config.compression_level <= 9
        
    def test_custom_config(self):
        """Test custom optimization configuration."""
        config = OptimizationConfig(
            level=OptimizationLevel.AGGRESSIVE,
            max_collection_size=5000,
            pool_size=50,
            cache_size=500,
            optimize_dataclasses=False,
            enable_gc_optimization=False,
            auto_monitor=False,
            auto_limit=False,
            compression_level=9
        )
        
        # Check custom values
        assert config.level == OptimizationLevel.AGGRESSIVE
        assert config.max_collection_size == 5000
        assert config.pool_size == 50
        assert config.cache_size == 500
        assert config.optimize_dataclasses is False
        assert config.enable_gc_optimization is False
        assert config.auto_monitor is False
        assert config.auto_limit is False
        assert config.compression_level == 9
        
    def test_custom_strategies(self):
        """Test custom optimization strategies."""
        custom_strategies = [
            OptimizationStrategy.SLOTS, 
            OptimizationStrategy.POOLING
        ]
        
        config = OptimizationConfig(
            strategies=custom_strategies
        )
        
        # Check strategies are set correctly
        assert config.strategies == custom_strategies
        assert OptimizationStrategy.SLOTS in config.strategies
        assert OptimizationStrategy.POOLING in config.strategies
        assert OptimizationStrategy.WEAK_REFS not in config.strategies
        
    def test_optimization_level_strategies(self):
        """Test strategies based on optimization level."""
        # Check NONE level (minimal strategies)
        none_config = OptimizationConfig(level=OptimizationLevel.NONE)
        assert len(none_config.strategies) <= 2  # Should have very few
        
        # Check MINIMAL level
        minimal_config = OptimizationConfig(level=OptimizationLevel.MINIMAL)
        assert len(minimal_config.strategies) > len(none_config.strategies)
        
        # Check MODERATE level
        moderate_config = OptimizationConfig(level=OptimizationLevel.MODERATE)
        assert len(moderate_config.strategies) >= len(minimal_config.strategies)
        
        # Check AGGRESSIVE level
        aggressive_config = OptimizationConfig(level=OptimizationLevel.AGGRESSIVE)
        assert len(aggressive_config.strategies) >= len(moderate_config.strategies)
        
        # Check EXTREME level (most strategies)
        extreme_config = OptimizationConfig(level=OptimizationLevel.EXTREME)
        assert len(extreme_config.strategies) >= len(aggressive_config.strategies)
        
    def test_has_strategy(self):
        """Test checking if a strategy is included."""
        strategies = [
            OptimizationStrategy.SLOTS, 
            OptimizationStrategy.POOLING
        ]
        
        config = OptimizationConfig(strategies=strategies)
        
        assert config.has_strategy(OptimizationStrategy.SLOTS)
        assert config.has_strategy(OptimizationStrategy.POOLING)
        assert not config.has_strategy(OptimizationStrategy.CACHING)
        
    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = OptimizationConfig(
            level=OptimizationLevel.AGGRESSIVE,
            max_collection_size=5000
        )
        
        config_dict = config.to_dict()
        
        assert "level" in config_dict
        assert "strategies" in config_dict
        assert "max_collection_size" in config_dict
        assert config_dict["level"] == "AGGRESSIVE"
        assert config_dict["max_collection_size"] == 5000
        assert isinstance(config_dict["strategies"], list)


class TestMemoryOptimizer:
    """Tests for the MemoryOptimizer class."""
    
    def test_init(self):
        """Test initialization of memory optimizer."""
        # Test with default config
        optimizer = MemoryOptimizer()
        
        assert optimizer.config is not None
        assert optimizer.monitor is not None
        assert optimizer.limiter is not None
        
        # Test with custom config
        custom_config = OptimizationConfig(level=OptimizationLevel.MINIMAL)
        optimizer = MemoryOptimizer(config=custom_config)
        
        assert optimizer.config == custom_config
        assert optimizer.config.level == OptimizationLevel.MINIMAL
        
        # Test with custom monitor and limiter
        monitor = MagicMock(spec=MemoryMonitor)
        limiter = MagicMock(spec=MemoryLimiter)
        
        optimizer = MemoryOptimizer(
            config=custom_config,
            monitor=monitor,
            limiter=limiter
        )
        
        assert optimizer.monitor == monitor
        assert optimizer.limiter == limiter
        
    def test_optimize_class_slots(self, memory_optimizer):
        """Test optimizing a class with slots."""
        
        class TestClass:
            def __init__(self, x=0, y=0):
                self.x = x
                self.y = y
                
            def get_sum(self):
                return self.x + self.y
        
        # Optimize class using slots
        OptimizedClass = memory_optimizer.optimize_class(
            TestClass, 
            strategies=[OptimizationStrategy.SLOTS]
        )
        
        # Check slots were added
        assert hasattr(OptimizedClass, "__slots__")
        assert "x" in OptimizedClass.__slots__
        assert "y" in OptimizedClass.__slots__
        
        # Check functionality is preserved
        instance = OptimizedClass(10, 20)
        assert instance.x == 10
        assert instance.y == 20
        assert instance.get_sum() == 30
        
        # Check __dict__ is not created
        assert not hasattr(instance, "__dict__")
        
    def test_optimize_dataclass(self, memory_optimizer):
        """Test optimizing a dataclass."""
        
        @dataclass
        class TestDataClass:
            x: int = 0
            y: int = 0
            
            def get_sum(self):
                return self.x + self.y
        
        # Optimize dataclass
        OptimizedClass = memory_optimizer.optimize_class(
            TestDataClass, 
            strategies=[OptimizationStrategy.SLOTS]
        )
        
        # Check slots were added
        assert hasattr(OptimizedClass, "__slots__")
        
        # Check functionality is preserved
        instance = OptimizedClass(10, 20)
        assert instance.x == 10
        assert instance.y == 20
        assert instance.get_sum() == 30
        
        # Check __dict__ is not created
        assert not hasattr(instance, "__dict__")
        
    def test_optimize_pooling(self, memory_optimizer):
        """Test optimizing a class with object pooling."""
        
        class TestClass:
            def __init__(self, x=0, y=0):
                self.x = x
                self.y = y
                
            def reset(self):
                self.x = 0
                self.y = 0
                
            def get_sum(self):
                return self.x + self.y
        
        # Optimize class using pooling
        OptimizedClass = memory_optimizer.optimize_class(
            TestClass, 
            strategies=[OptimizationStrategy.POOLING]
        )
        
        # Check pooling methods were added
        assert hasattr(OptimizedClass, "get_from_pool")
        assert hasattr(OptimizedClass, "return_to_pool")
        assert hasattr(OptimizedClass, "clear_pool")
        
        # Create and use an instance
        instance = OptimizedClass(10, 20)
        assert instance.get_sum() == 30
        
        # Return to pool and get a new instance
        OptimizedClass.return_to_pool(instance)
        instance2 = OptimizedClass.get_from_pool()
        
        # The pool should have returned a reset instance
        assert instance2.x == 0
        assert instance2.y == 0
        
        # Create multiple instances and clear pool
        instances = [OptimizedClass(i, i*2) for i in range(10)]
        del instances
        gc.collect()  # Force garbage collection to return instances to pool
        
        # Check pool contains instances
        assert OptimizedClass.get_pool_size() > 0
        
        # Clear pool
        OptimizedClass.clear_pool()
        assert OptimizedClass.get_pool_size() == 0
        
    def test_optimize_caching(self, memory_optimizer):
        """Test optimizing a class with method caching."""
        
        class TestClass:
            def __init__(self):
                self.call_count = 0
                
            def expensive_method(self, x):
                self.call_count += 1
                return x * 2
                
            @property
            def expensive_property(self):
                self.call_count += 1
                return 42
        
        # Optimize class using caching
        OptimizedClass = memory_optimizer.optimize_class(
            TestClass, 
            strategies=[OptimizationStrategy.CACHING]
        )
        
        # Create an instance
        instance = OptimizedClass()
        
        # Call method multiple times with same parameter
        result1 = instance.expensive_method(5)
        result2 = instance.expensive_method(5)
        
        # Method should only be called once
        assert result1 == result2 == 10
        assert instance.call_count == 1
        
        # Access property multiple times
        prop1 = instance.expensive_property
        prop2 = instance.expensive_property
        
        # Property should only be computed once
        assert prop1 == prop2 == 42
        assert instance.call_count == 2  # One for method, one for property
        
    def test_optimize_collections(self, memory_optimizer):
        """Test optimizing collections."""
        # Create some large collections
        large_list = list(range(5000))
        large_dict = {i: i*2 for i in range(5000)}
        
        # Optimize collections
        memory_optimizer.optimize_collections([large_list, large_dict])
        
        # List should be limited to max collection size
        assert len(large_list) <= memory_optimizer.config.max_collection_size
        
        # Dictionary should be limited to max collection size
        assert len(large_dict) <= memory_optimizer.config.max_collection_size
        
    def test_cached_result(self, memory_optimizer):
        """Test cached_result decorator."""
        call_count = 0
        
        @memory_optimizer.cached_result()
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # Call function multiple times with same parameter
        result1 = expensive_function(5)
        result2 = expensive_function(5)
        
        # Function should only be called once
        assert result1 == result2 == 10
        assert call_count == 1
        
        # Call with different parameter
        result3 = expensive_function(10)
        
        # Function should be called again
        assert result3 == 20
        assert call_count == 2
        
    def test_compact_data_structure(self, memory_optimizer):
        """Test compacting data structures."""
        # Create nested data structure
        data = {
            "numbers": list(range(1000)),
            "nested": {
                "more_numbers": list(range(1000)),
                "string": "x" * 1000
            },
            "list_of_dicts": [
                {"id": i, "value": i*2} for i in range(1000)
            ]
        }
        
        # Compact the data
        compacted = memory_optimizer.compact_data_structure(data)
        
        # Structure should be preserved but sizes limited
        assert "numbers" in compacted
        assert "nested" in compacted
        assert "list_of_dicts" in compacted
        
        assert len(compacted["numbers"]) <= memory_optimizer.config.max_collection_size
        assert len(compacted["list_of_dicts"]) <= memory_optimizer.config.max_collection_size
        
        # Check nested structures
        assert "more_numbers" in compacted["nested"]
        assert len(compacted["nested"]["more_numbers"]) <= memory_optimizer.config.max_collection_size
        
    @patch('gc.collect')
    def test_optimize_memory_usage(self, mock_collect, memory_optimizer):
        """Test optimize_memory_usage method."""
        # Optimize memory usage
        memory_optimizer.optimize_memory_usage()
        
        # gc.collect should be called
        mock_collect.assert_called()
        
        # Monitor should be used
        memory_optimizer.monitor.get_current_usage.assert_called()
        
    @patch('gc.collect')
    def test_operation_context(self, mock_collect, memory_optimizer):
        """Test operation context manager."""
        # Use operation context
        with memory_optimizer.monitor_operation("test_operation") as op:
            # Do something
            data = [1, 2, 3]
            result = sum(data)
            
        # Monitor start and stop should be called
        memory_optimizer.monitor.get_current_usage.assert_called()
        
        # Context should have usage information
        usage = op.get_usage_summary()
        assert "operation" in usage
        assert usage["operation"] == "test_operation"
        assert "start" in usage
        assert "end" in usage
        assert "duration" in usage
        
    def test_get_optimization_report(self, memory_optimizer):
        """Test getting optimization report."""
        # Get report
        report = memory_optimizer.get_optimization_report()
        
        # Check report structure
        assert "config" in report
        assert "optimized_classes" in report
        assert "optimized_collections" in report
        assert "monitor_stats" in report
        assert "strategies" in report
        
    def test_lazy_load(self, memory_optimizer):
        """Test lazy_load decorator."""
        load_count = 0
        
        class TestClass:
            @property
            def expensive_property(self):
                nonlocal load_count
                load_count += 1
                return "expensive"
            
            @memory_optimizer.lazy_load
            def lazy_prop(self):
                nonlocal load_count
                load_count += 1
                return "lazy"
                
        # Create instance
        instance = TestClass()
        
        # Access regular property (loads immediately)
        assert instance.expensive_property == "expensive"
        assert load_count == 1
        
        # Access lazy property (doesn't load until first access)
        lazy_descriptor = instance.lazy_prop
        assert load_count == 1  # Still only one load
        
        # Actually access the value
        value = lazy_descriptor.value
        assert value == "lazy"
        assert load_count == 2
        
        # Access again (uses cached value)
        value2 = lazy_descriptor.value
        assert value2 == "lazy"
        assert load_count == 2  # No additional load


class TestStreamingOptimizer:
    """Tests for the StreamingOptimizer class."""
    
    def test_init(self):
        """Test initialization of streaming optimizer."""
        optimizer = StreamingOptimizer(chunk_size=1000)
        assert optimizer.chunk_size == 1000
        
    def test_process_iterable(self):
        """Test processing an iterable in chunks."""
        optimizer = StreamingOptimizer(chunk_size=2)
        data = [1, 2, 3, 4, 5]
        
        processed = []
        for chunk in optimizer.process_iterable(data):
            processed.extend(chunk)
            
        assert processed == data
        
    def test_process_large_file(self, tmp_path):
        """Test processing a large file in chunks."""
        # Create a test file
        file_path = tmp_path / "test_file.txt"
        with open(file_path, "w") as f:
            for i in range(100):
                f.write(f"Line {i}\n")
                
        optimizer = StreamingOptimizer(chunk_size=10)
        
        line_count = 0
        for chunk in optimizer.process_file(file_path):
            line_count += len(chunk)
            for line in chunk:
                assert line.strip().startswith("Line ")
                
        assert line_count == 100
        
    def test_process_generator(self):
        """Test processing a generator in chunks."""
        def generate_data(count):
            for i in range(count):
                yield i
                
        optimizer = StreamingOptimizer(chunk_size=3)
        
        processed = []
        for chunk in optimizer.process_generator(generate_data(10)):
            processed.extend(chunk)
            
        assert processed == list(range(10))
        
        
class TestLazyLoader:
    """Tests for the LazyLoader class."""
    
    def test_init(self):
        """Test initialization of lazy loader."""
        def load_func():
            return "data"
            
        loader = LazyLoader(load_func)
        assert loader._loader == load_func
        assert not loader._loaded
        assert loader._value is None
        
    def test_load(self):
        """Test loading data."""
        load_count = 0
        
        def load_func():
            nonlocal load_count
            load_count += 1
            return "data"
            
        loader = LazyLoader(load_func)
        
        # Data should not be loaded yet
        assert not loader._loaded
        assert load_count == 0
        
        # Load data
        value = loader.value
        
        # Data should be loaded now
        assert loader._loaded
        assert load_count == 1
        assert value == "data"
        
        # Access data again (should use cached value)
        value2 = loader.value
        
        # Load function should not be called again
        assert load_count == 1
        assert value2 == "data"
        
    def test_reset(self):
        """Test resetting loader."""
        load_count = 0
        
        def load_func():
            nonlocal load_count
            load_count += 1
            return "data"
            
        loader = LazyLoader(load_func)
        
        # Load data
        value = loader.value
        assert loader._loaded
        assert load_count == 1
        
        # Reset loader
        loader.reset()
        
        # Data should be unloaded
        assert not loader._loaded
        assert loader._value is None
        
        # Load data again
        value2 = loader.value
        
        # Load function should be called again
        assert load_count == 2
        assert value2 == "data" 