"""Memory management and optimization module for Summit SEO.

This module provides functionality for monitoring and optimizing memory usage
in the Summit SEO analysis pipeline.
"""

from .monitor import MemoryMonitor, ResourceUsageStats, MemoryLimitExceededError
from .profiler import Profiler, ProfileResult, ProfilerConfig
from .limiter import MemoryLimiter, MemoryLimit, LimitScope

# Create singleton instances for global use
memory_monitor = MemoryMonitor()
memory_limiter = MemoryLimiter()

__all__ = [
    'MemoryMonitor',
    'ResourceUsageStats',
    'MemoryLimitExceededError',
    'Profiler',
    'ProfileResult',
    'ProfilerConfig',
    'MemoryLimiter',
    'MemoryLimit',
    'LimitScope',
    'memory_monitor',
    'memory_limiter',
] 