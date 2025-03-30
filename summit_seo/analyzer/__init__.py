"""
Analyzer package for SEO analysis.

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
from .recommendation import (
    Recommendation,
    RecommendationBuilder,
    RecommendationManager,
    RecommendationSeverity,
    RecommendationPriority
)

# Import all analyzer classes
from .title_analyzer import TitleAnalyzer
from .meta_analyzer import MetaAnalyzer
from .heading_structure_analyzer import HeadingStructureAnalyzer
from .content_analyzer import ContentAnalyzer
from .link_analyzer import LinkAnalyzer
from .image_analyzer import ImageSEOAnalyzer as ImageAnalyzer
from .security_analyzer import SecurityAnalyzer
from .performance_analyzer import PerformanceAnalyzer
from .schema_analyzer import SchemaAnalyzer
from .accessibility_analyzer import AccessibilityAnalyzer
from .mobile_friendly_analyzer import MobileFriendlyAnalyzer
from .social_media_analyzer import SocialMediaAnalyzer

# Create and configure analyzer factory
factory = AnalyzerFactory()

# Register all analyzers with the factory
factory.register('title', TitleAnalyzer)
factory.register('meta', MetaAnalyzer)
factory.register('heading', HeadingStructureAnalyzer)
factory.register('content', ContentAnalyzer)
factory.register('link', LinkAnalyzer)
factory.register('image', ImageAnalyzer)
factory.register('security', SecurityAnalyzer)
factory.register('performance', PerformanceAnalyzer)
factory.register('schema', SchemaAnalyzer)
factory.register('accessibility', AccessibilityAnalyzer)
factory.register('mobile', MobileFriendlyAnalyzer)
factory.register('social', SocialMediaAnalyzer)

__all__ = [
    'BaseAnalyzer',
    'AnalysisResult',
    'AnalysisMetadata',
    'AnalyzerError',
    'AnalyzerFactory',
    'Recommendation',
    'RecommendationBuilder',
    'RecommendationManager',
    'RecommendationSeverity',
    'RecommendationPriority',
    'TitleAnalyzer',
    'MetaAnalyzer',
    'HeadingStructureAnalyzer',
    'ContentAnalyzer',
    'LinkAnalyzer',
    'ImageAnalyzer',
    'SecurityAnalyzer',
    'PerformanceAnalyzer',
    'SchemaAnalyzer',
    'AccessibilityAnalyzer',
    'MobileFriendlyAnalyzer',
    'SocialMediaAnalyzer',
    'factory',
    'InputType',
    'OutputType'
] 