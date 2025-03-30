"""
Analyzer module for SEO analysis.

This module provides analyzers for different aspects of SEO, including
title analysis, meta tags, content, heading structure, links, images, and more.
"""

from .base import (
    BaseAnalyzer,
    AnalysisResult,
    AnalysisMetadata,
    AnalyzerError,
    InputType,
    OutputType
)
from .factory import AnalyzerFactory
from .title_analyzer import TitleAnalyzer
from .meta_analyzer import MetaAnalyzer
from .content_analyzer import ContentAnalyzer
from .heading_structure_analyzer import HeadingStructureAnalyzer
from .link_analyzer import LinkAnalyzer
from .image_analyzer import ImageSEOAnalyzer

# Register concrete analyzers with the factory
AnalyzerFactory.register('title', TitleAnalyzer)
AnalyzerFactory.register('meta', MetaAnalyzer)
AnalyzerFactory.register('content', ContentAnalyzer)
AnalyzerFactory.register('heading_structure', HeadingStructureAnalyzer)
AnalyzerFactory.register('links', LinkAnalyzer)
AnalyzerFactory.register('images', ImageSEOAnalyzer)

__all__ = [
    'BaseAnalyzer',
    'AnalysisResult',
    'AnalysisMetadata',
    'AnalyzerError',
    'AnalyzerFactory',
    'TitleAnalyzer',
    'MetaAnalyzer',
    'ContentAnalyzer',
    'HeadingStructureAnalyzer',
    'LinkAnalyzer',
    'ImageSEOAnalyzer',
    'InputType',
    'OutputType'
] 