"""
Processor module for data processing and transformation.

This module provides the base classes and factory for creating and managing
processors that transform data between different formats and structures.
"""

from .base import (
    BaseProcessor,
    ProcessingResult,
    ProcessorError,
    ValidationError,
    TransformationError
)
from .factory import ProcessorFactory
from .html_processor import HTMLProcessor
from .javascript_processor import JavaScriptProcessor
from .css_processor import CSSProcessor
from .robotstxt_processor import RobotsTxtProcessor
from .sitemap_processor import SitemapProcessor

# Register processors with the factory
ProcessorFactory.register('html', HTMLProcessor)
ProcessorFactory.register('js', JavaScriptProcessor)
ProcessorFactory.register('css', CSSProcessor)
ProcessorFactory.register('robotstxt', RobotsTxtProcessor)
ProcessorFactory.register('sitemap', SitemapProcessor)

__all__ = [
    'BaseProcessor',
    'ProcessingResult',
    'ProcessorError',
    'ValidationError',
    'TransformationError',
    'ProcessorFactory',
    'HTMLProcessor',
    'JavaScriptProcessor',
    'CSSProcessor',
    'RobotsTxtProcessor',
    'SitemapProcessor'
] 