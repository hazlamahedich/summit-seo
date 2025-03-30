"""Tests for the memory utility functions."""

import gc
import sys
import weakref
from dataclasses import dataclass
from unittest.mock import patch

import pytest

from summit_seo.memory.monitor import MemoryUnit
from summit_seo.memory.utils import (
    CachedProperty, WeakList, enable_object_pooling, find_memory_leaks,
    get_detailed_memory_report, get_human_readable_size, get_memory_footprint_summary,
    get_memory_usage_factors, get_object_references, get_size, memory_optimize_dataclass
)


class TestMemoryUtils:
    """Tests for memory utility functions."""
    
    def test_get_size(self):
        """Test get_size function."""
        # Test with different types
        assert get_size(123) > 0
        assert get_size("hello") > 0
        assert get_size([1, 2, 3]) > 0
        assert get_size({"a": 1, "b": 2}) > 0
        
        # Test with deep inspection
        small_list = [1, 2, 3]
        assert get_size(small_list, deep=True) >= get_size(small_list, deep=False)
        
        # Test with nested structures
        nested = {"a": [1, 2, 3], "b": {"c": 4}}
        assert get_size(nested, deep=True) > get_size(nested, deep=False)
        
        # Test with cycle detection
        cycle_list = []
        cycle_list.append(cycle_list)  # Create a cycle
        
        # This should not cause an infinite loop
        assert get_size(cycle_list, deep=True) > 0
        
    def test_get_human_readable_size(self):
        """Test get_human_readable_size function."""
        # Test with bytes
        assert get_human_readable_size(1023) == "1023 bytes"
        
        # Test with KB
        assert "KB" in get_human_readable_size(1024)
        assert "1.00 KB" in get_human_readable_size(1024, unit=MemoryUnit.KB)
        
        # Test with MB
        assert "MB" in get_human_readable_size(1024 * 1024)
        assert "1.00 MB" in get_human_readable_size(1024 * 1024, unit=MemoryUnit.MB)
        
        # Test with GB
        assert "GB" in get_human_readable_size(1024 * 1024 * 1024)
        assert "1.00 GB" in get_human_readable_size(1024 * 1024 * 1024, unit=MemoryUnit.GB)
        
        # Test with specific unit
        assert "KB" in get_human_readable_size(100, unit=MemoryUnit.KB)
        assert "MB" in get_human_readable_size(100, unit=MemoryUnit.MB)
        
    def test_get_object_references(self):
        """Test get_object_references function."""
        # Create an object
        obj = [1, 2, 3]
        
        # Create references to it
        ref_list = [obj]
        ref_dict = {"obj": obj}
        
        # Get references
        refs = get_object_references(obj)
        
        # Should return a dict with categories
        assert isinstance(refs, dict)
        assert "lists" in refs
        assert "dicts" in refs
        assert "modules" in refs
        
        # Check if our references are found
        assert any(id(ref_list) == id(ref) for ref in refs["lists"])
        
    def test_find_memory_leaks(self):
        """Test find_memory_leaks function."""
        # Create some objects that might appear in leak report
        objs = []
        for _ in range(10):
            objs.append([1, 2, 3])
        
        # Find potential leaks
        leaks = find_memory_leaks(iterations=2)
        
        # Should return a dict mapping types to counts
        assert isinstance(leaks, dict)
        
        # Cleanup
        del objs
        
    def test_weak_list(self):
        """Test WeakList class."""
        # Create objects
        obj1 = [1, 2, 3]
        obj2 = [4, 5, 6]
        
        # Create weak list
        weak_list = WeakList([obj1, obj2])
        
        # Length should be correct
        assert len(weak_list) == 2
        
        # Items should be accessible
        items = list(weak_list)
        assert len(items) == 2
        assert obj1 in items
        assert obj2 in items
        
        # Test weakref behavior
        del obj1
        gc.collect()  # Force garbage collection
        
        # Length should now be 1
        assert len(weak_list) == 1
        
        # Only obj2 should be left
        items = list(weak_list)
        assert len(items) == 1
        assert items[0] == obj2
        
        # Test append
        obj3 = [7, 8, 9]
        weak_list.append(obj3)
        assert len(weak_list) == 2
        
        # Test clear
        weak_list.clear()
        assert len(weak_list) == 0
        
    def test_cached_property(self):
        """Test CachedProperty class."""
        call_count = 0
        
        class TestClass:
            @CachedProperty
            def expensive_property(self):
                nonlocal call_count
                call_count += 1
                return 42
        
        # Create instance
        instance = TestClass()
        
        # Access property multiple times
        value1 = instance.expensive_property
        value2 = instance.expensive_property
        
        # Values should be the same
        assert value1 == value2
        assert value1 == 42
        
        # But only one call should be made
        assert call_count == 1
        
        # Test setting the property
        instance.expensive_property = 99
        assert instance.expensive_property == 99
        assert call_count == 1  # No additional calls
        
    def test_memory_optimize_dataclass(self):
        """Test memory_optimize_dataclass function."""
        # Create a dataclass
        @dataclass
        class TestDataClass:
            x: int = 0
            y: int = 0
        
        # Optimize it
        OptimizedClass = memory_optimize_dataclass(TestDataClass)
        
        # Should have slots
        assert hasattr(OptimizedClass, "__slots__")
        assert "x" in OptimizedClass.__slots__
        assert "y" in OptimizedClass.__slots__
        
        # Should work correctly
        instance = OptimizedClass(10, 20)
        assert instance.x == 10
        assert instance.y == 20
        
    def test_enable_object_pooling(self):
        """Test enable_object_pooling function."""
        # Create a class
        class TestClass:
            def __init__(self, x=0, y=0):
                self.x = x
                self.y = y
                
            def reset(self):
                """Reset the instance state."""
                self.x = 0
                self.y = 0
        
        # Enable pooling
        PooledClass = enable_object_pooling(TestClass, max_size=5)
        
        # Should have pool management methods
        assert hasattr(PooledClass, "clear_pool")
        assert hasattr(PooledClass, "get_pool_size")
        
        # Create and use instances
        instances = []
        for i in range(10):
            instances.append(PooledClass(i, i*2))
            
        # All instances should be initialized correctly
        for i, instance in enumerate(instances):
            assert instance.x == i
            assert instance.y == i*2
            
        # Clear instances to return to pool
        del instances
        gc.collect()
        
        # Pool size should be at most max_size
        assert PooledClass.get_pool_size() <= 5
        
        # Clear pool
        PooledClass.clear_pool()
        assert PooledClass.get_pool_size() == 0
        
    def test_get_memory_usage_factors(self):
        """Test get_memory_usage_factors function."""
        # Get factors
        factors = get_memory_usage_factors()
        
        # Should return a dict with various factors
        assert isinstance(factors, dict)
        assert "int" in factors
        assert "float" in factors
        assert "list_empty" in factors
        assert "dict_empty" in factors
        assert "list_per_item" in factors
        
        # Int should be the baseline
        assert factors["int"] == 1.0
        
        # Lists should have overhead
        assert factors["list_10items"] > factors["list_empty"]
        
    def test_get_memory_footprint_summary(self):
        """Test get_memory_footprint_summary function."""
        # Test with different types
        obj = [1, 2, 3, 4, 5]
        summary = get_memory_footprint_summary(obj)
        
        # Should include basic info
        assert "object_type" in summary
        assert summary["object_type"] == "list"
        assert "direct_size_bytes" in summary
        assert "deep_size_bytes" in summary
        assert "direct_size_human" in summary
        assert "deep_size_human" in summary
        
        # Should include container-specific info
        assert "container_length" in summary
        assert summary["container_length"] == 5
        assert "per_item_bytes" in summary
        assert "per_item_human" in summary
        
    def test_get_detailed_memory_report(self):
        """Test get_detailed_memory_report function."""
        # Get memory report
        report = get_detailed_memory_report()
        
        # Should include several sections
        assert "gc_stats" in report
        assert "type_counts" in report
        assert "memory_factors" in report
        assert "reference_counts" in report
        
        # GC stats should include counts
        assert "gc_counts" in report["gc_stats"]
        assert "gc_threshold" in report["gc_stats"]
        
        # Type counts should be a dict
        assert isinstance(report["type_counts"], dict)
        
        # Reference counts should include common types
        assert "list" in report["reference_counts"]
        assert "dict" in report["reference_counts"]
        assert "str" in report["reference_counts"] 