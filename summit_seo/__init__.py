"""
Summit SEO - A comprehensive SEO analysis tool.
"""

from .cli import cli
from .analyzer import AnalyzerFactory
from .collector import CollectorFactory
from .processor import ProcessorFactory

__version__ = "0.1.0"
__all__ = ['cli', 'AnalyzerFactory', 'CollectorFactory', 'ProcessorFactory']
