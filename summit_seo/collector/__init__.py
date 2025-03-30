"""
Collector module for gathering SEO-related data.

This module provides the base classes and factory for creating and managing
collectors that gather data from various sources for SEO analysis.
"""

from .base import (
    BaseCollector,
    CollectionResult,
    CollectorError,
    RateLimitError,
    CollectionError
)
from .factory import CollectorFactory
from .webpage_collector import WebPageCollector

# Register built-in collectors
CollectorFactory.register('webpage', WebPageCollector)

__all__ = [
    'BaseCollector',
    'CollectionResult',
    'CollectorError',
    'RateLimitError',
    'CollectionError',
    'CollectorFactory',
    'WebPageCollector'
] 