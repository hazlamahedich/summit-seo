"""Utility functions for memory management in Summit SEO."""

import gc
import inspect
import os
import pprint
import sys
import threading
import weakref
from collections import deque
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union

from .monitor import MemoryUnit


def get_size(obj: Any, seen: Optional[Set[int]] = None, deep: bool = False) -> int:
    """Get the size of an object in bytes.

    Args:
        obj: The object to get the size of
        seen: Set of already seen object ids, used to avoid cycles
        deep: Whether to perform a deep inspection of object contents

    Returns:
        Size of the object in bytes
    """
    if seen is None:
        seen = set()

    # If object already seen, don't count it again
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)

    # Get size of the object itself
    size = sys.getsizeof(obj)

    # If deep inspection is requested, compute size of contained objects
    if deep:
        if isinstance(obj, dict):
            size += sum(get_size(k, seen, deep) + get_size(v, seen, deep) for k, v in obj.items())
        elif isinstance(obj, (list, tuple, set, frozenset, deque)):
            size += sum(get_size(i, seen, deep) for i in obj)
        elif hasattr(obj, '__dict__'):
            size += get_size(obj.__dict__, seen, deep)
        elif hasattr(obj, '__slots__'):
            for slot_name in obj.__slots__:
                try:
                    size += get_size(getattr(obj, slot_name), seen, deep)
                except AttributeError:
                    pass

    return size


def get_human_readable_size(size_bytes: int, unit: Optional[MemoryUnit] = None) -> str:
    """Convert a size in bytes to a human-readable string.

    Args:
        size_bytes: Size in bytes
        unit: Memory unit to use, or None to auto-select

    Returns:
        Human-readable size string
    """
    if unit is None:
        # Auto-select unit based on size
        if size_bytes < 1024:
            unit = MemoryUnit.BYTES
        elif size_bytes < 1024 * 1024:
            unit = MemoryUnit.KB
        elif size_bytes < 1024 * 1024 * 1024:
            unit = MemoryUnit.MB
        else:
            unit = MemoryUnit.GB

    if unit == MemoryUnit.BYTES:
        return f"{size_bytes} bytes"
    elif unit == MemoryUnit.KB:
        return f"{size_bytes / 1024:.2f} KB"
    elif unit == MemoryUnit.MB:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    elif unit == MemoryUnit.GB:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    else:
        return f"{size_bytes} bytes"


def get_object_references(obj: Any) -> Dict[str, List[Any]]:
    """Get references to the object.

    Args:
        obj: Object to get references for

    Returns:
        Dictionary of reference types and the objects that reference the input object
    """
    referrers = gc.get_referrers(obj)
    result = {"frames": [], "modules": [], "functions": [], "classes": [], "dicts": [], "lists": [],
              "tuples": [], "other": []}

    for referrer in referrers:
        if inspect.isframe(referrer):
            result["frames"].append(referrer)
        elif inspect.ismodule(referrer):
            result["modules"].append(referrer)
        elif inspect.isfunction(referrer) or inspect.ismethod(referrer):
            result["functions"].append(referrer)
        elif inspect.isclass(referrer):
            result["classes"].append(referrer)
        elif isinstance(referrer, dict):
            result["dicts"].append(referrer)
        elif isinstance(referrer, list):
            result["lists"].append(referrer)
        elif isinstance(referrer, tuple):
            result["tuples"].append(referrer)
        else:
            result["other"].append(referrer)

    return result


def find_memory_leaks(iterations: int = 5, collect: bool = True) -> Dict[str, int]:
    """Find potential memory leaks.

    Runs multiple garbage collection cycles and reports objects that weren't collected.

    Args:
        iterations: Number of garbage collection iterations to run
        collect: Whether to run garbage collection before analysis

    Returns:
        Dictionary mapping object types to counts of uncollectable objects
    """
    if collect:
        gc.collect()

    # Get objects before iterations
    objects_before = gc.get_objects()
    type_counts_before = {}
    for obj in objects_before:
        obj_type = type(obj).__name__
        type_counts_before[obj_type] = type_counts_before.get(obj_type, 0) + 1

    # Run multiple garbage collection cycles
    for _ in range(iterations):
        gc.collect()

    # Get objects after iterations
    objects_after = gc.get_objects()
    type_counts_after = {}
    for obj in objects_after:
        obj_type = type(obj).__name__
        type_counts_after[obj_type] = type_counts_after.get(obj_type, 0) + 1

    # Compare counts to find potential leaks
    potential_leaks = {}
    for obj_type, count_after in type_counts_after.items():
        count_before = type_counts_before.get(obj_type, 0)
        diff = count_after - count_before
        if diff > 0:
            potential_leaks[obj_type] = diff

    return potential_leaks


class WeakList:
    """A list-like object that holds weak references to its items."""

    def __init__(self, items=None):
        """Initialize with optional items.

        Args:
            items: Optional initial items
        """
        self._refs = []
        if items:
            for item in items:
                self.append(item)

    def append(self, item: Any) -> None:
        """Append an item using a weak reference.

        Args:
            item: Item to append
        """
        self._refs.append(weakref.ref(item))

    def __iter__(self):
        """Iterate over non-None weak references.

        Yields:
            Referenced objects
        """
        for ref in self._refs[:]:  # Copy to avoid modification during iteration
            obj = ref()
            if obj is not None:
                yield obj
            else:
                # Remove dead references
                self._refs.remove(ref)

    def __len__(self) -> int:
        """Get number of alive references.

        Returns:
            Number of non-None references
        """
        return sum(1 for ref in self._refs if ref() is not None)

    def clear(self) -> None:
        """Clear all references."""
        self._refs.clear()


class CachedProperty:
    """A property that caches its value after first access.

    Like @property but with caching.
    """

    def __init__(self, func: Callable):
        """Initialize with the decorated function.

        Args:
            func: Function to call to compute the property value
        """
        self.func = func
        self.__doc__ = func.__doc__
        self.attrname = None

    def __set_name__(self, owner: Type, name: str) -> None:
        """Set the attribute name when the descriptor is created.

        Args:
            owner: Class that owns this property
            name: Name of this property in the owner class
        """
        self.attrname = name

    def __get__(self, instance: Any, owner: Type) -> Any:
        """Get the property value, computing and caching it if necessary.

        Args:
            instance: Instance to get the property for
            owner: Class that owns this property

        Returns:
            Property value
        """
        if instance is None:
            return self

        if self.attrname is None:
            # Find our name
            for name, attr in owner.__dict__.items():
                if attr is self:
                    self.attrname = name
                    break
            else:
                raise ValueError("Cannot find attribute name")

        # Use leading underscore to store cached value
        cache_name = f"_{self.attrname}"
        if not hasattr(instance, cache_name):
            setattr(instance, cache_name, self.func(instance))
        return getattr(instance, cache_name)

    def __set__(self, instance: Any, value: Any) -> None:
        """Set the cached value directly.

        Args:
            instance: Instance to set the property for
            value: New property value
        """
        if self.attrname is None:
            raise ValueError("Cannot set attribute before it's been accessed")
        
        cache_name = f"_{self.attrname}"
        setattr(instance, cache_name, value)


def memory_optimize_dataclass(cls: Type) -> Type:
    """Optimize a dataclass for memory usage by using slots.

    This decorator adds __slots__ to a dataclass to reduce memory footprint.
    Note that this must be applied after @dataclass.

    Args:
        cls: Dataclass to optimize

    Returns:
        Optimized dataclass
    """
    # Get field names from dataclass
    field_names = [f.name for f in cls.__dataclass_fields__.values()]
    
    # Add __slots__ to the class
    cls.__slots__ = field_names
    
    # Remove __dict__ since we have slots
    if hasattr(cls, "__dict__"):
        delattr(cls, "__dict__")
        
    return cls


def enable_object_pooling(cls: Type, max_size: int = 100) -> Type:
    """Enable object pooling for a class to reduce allocation/deallocation costs.

    Args:
        cls: Class to enable pooling for
        max_size: Maximum pool size

    Returns:
        Modified class with pooling
    """
    # Create a pool for this class
    pool = deque(maxlen=max_size)
    lock = threading.RLock()

    # Save original __new__ and __del__ methods
    original_new = cls.__new__
    original_del = cls.__del__ if hasattr(cls, "__del__") else None

    # Replace __new__ to check pool first
    def pooled_new(cls, *args, **kwargs):
        with lock:
            if not pool:
                # Pool is empty, create a new instance
                instance = original_new(cls)
            else:
                # Get an instance from the pool
                instance = pool.pop()
        
        # Initialize the instance if __init__ is called
        if cls.__init__ is not object.__init__:
            cls.__init__(instance, *args, **kwargs)
        return instance
    
    # Replace __del__ to return to pool instead of deallocating
    def pooled_del(self):
        # Call original __del__ if it exists
        if original_del:
            original_del(self)
        
        # Return to pool if not at capacity
        with lock:
            if len(pool) < max_size:
                # Reset instance state if possible
                if hasattr(self, "reset"):
                    self.reset()
                pool.append(self)
    
    # Replace methods on class
    cls.__new__ = pooled_new
    cls.__del__ = pooled_del
    
    # Add pool management methods
    cls.clear_pool = staticmethod(lambda: pool.clear())
    cls.get_pool_size = staticmethod(lambda: len(pool))
    
    return cls


@lru_cache(maxsize=1024)
def get_memory_usage_factors() -> Dict[str, float]:
    """Calculate memory usage factors for different data structures.
    
    These factors can be used to estimate memory impact of different data choices.
    
    Returns:
        Dictionary mapping data structure names to relative memory factors
    """
    results = {}
    
    # Base size with a single integer
    base_size = sys.getsizeof(0)
    results["int"] = 1.0  # Baseline
    
    # Compare other types
    results["float"] = sys.getsizeof(0.0) / base_size
    results["str_empty"] = sys.getsizeof("") / base_size
    results["str_char"] = sys.getsizeof("a") / base_size
    results["str_10char"] = sys.getsizeof("a" * 10) / base_size
    results["list_empty"] = sys.getsizeof([]) / base_size
    results["dict_empty"] = sys.getsizeof({}) / base_size
    results["set_empty"] = sys.getsizeof(set()) / base_size
    results["tuple_empty"] = sys.getsizeof(()) / base_size
    
    # Compare container overhead with 10 items
    list_10 = [0] * 10
    dict_10 = {i: i for i in range(10)}
    set_10 = set(range(10))
    tuple_10 = tuple(range(10))
    
    results["list_10items"] = sys.getsizeof(list_10) / base_size
    results["dict_10items"] = sys.getsizeof(dict_10) / base_size
    results["set_10items"] = sys.getsizeof(set_10) / base_size
    results["tuple_10items"] = sys.getsizeof(tuple_10) / base_size
    
    # Calculate per-item overhead
    list_100 = [0] * 100
    results["list_per_item"] = (sys.getsizeof(list_100) - sys.getsizeof(list_10)) / 90 / base_size
    
    dict_100 = {i: i for i in range(100)}
    results["dict_per_item"] = (sys.getsizeof(dict_100) - sys.getsizeof(dict_10)) / 90 / base_size
    
    set_100 = set(range(100))
    results["set_per_item"] = (sys.getsizeof(set_100) - sys.getsizeof(set_10)) / 90 / base_size
    
    tuple_100 = tuple(range(100))
    results["tuple_per_item"] = (sys.getsizeof(tuple_100) - sys.getsizeof(tuple_10)) / 90 / base_size
    
    return results


def get_memory_footprint_summary(obj: Any) -> Dict[str, Any]:
    """Get a summary of object's memory footprint.
    
    Args:
        obj: Object to analyze
        
    Returns:
        Dictionary with memory footprint information
    """
    direct_size = sys.getsizeof(obj)
    deep_size = get_size(obj, deep=True)
    
    summary = {
        "object_type": type(obj).__name__,
        "direct_size_bytes": direct_size,
        "deep_size_bytes": deep_size,
        "direct_size_human": get_human_readable_size(direct_size),
        "deep_size_human": get_human_readable_size(deep_size),
        "overhead_factor": deep_size / max(1, direct_size),
    }
    
    # Add container-specific info
    if isinstance(obj, (list, tuple, set, frozenset, dict)):
        summary["container_length"] = len(obj)
        
        if len(obj) > 0:
            summary["per_item_bytes"] = deep_size / len(obj)
            summary["per_item_human"] = get_human_readable_size(deep_size / len(obj))
    
    return summary


def get_detailed_memory_report() -> Dict[str, Any]:
    """Get a detailed memory usage report.
    
    Returns:
        Dictionary with detailed memory usage information
    """
    gc.collect()  # Run garbage collection first
    
    # Get memory usage from various sources
    result = {}
    
    # Get garbage collector statistics
    result["gc_stats"] = {
        "garbage": len(gc.garbage),
        "gc_enabled": gc.isenabled(),
        "gc_counts": gc.get_count(),
        "gc_threshold": gc.get_threshold(),
    }
    
    # Get counts by type
    type_counts = {}
    for obj in gc.get_objects():
        obj_type = type(obj).__name__
        type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
    
    # Sort by count (descending)
    sorted_counts = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
    result["type_counts"] = {t: c for t, c in sorted_counts[:50]}  # Top 50 types
    
    # Get memory usage factors
    result["memory_factors"] = get_memory_usage_factors()
    
    # Get references to common types to check for leaks
    ref_counts = {}
    for type_name in ["list", "dict", "set", "tuple", "str", "int", "float"]:
        type_obj = getattr(__builtins__, type_name)
        instances = [obj for obj in gc.get_objects() if isinstance(obj, type_obj)]
        ref_counts[type_name] = len(instances)
    
    result["reference_counts"] = ref_counts
    
    return result 