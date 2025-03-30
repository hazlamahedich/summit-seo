"""
Reporter module for Summit SEO.

This module provides the base classes and factory for creating and managing
reporters that generate reports in various formats.
"""

from .base import (
    BaseReporter,
    ReportResult,
    ReportMetadata,
    ReporterError,
    ReportGenerationError,
    ReportFormatError
)
from .factory import (
    ReporterFactory,
    ReporterFactoryError,
    ReporterRegistrationError,
    ReporterNotFoundError
)
from .html_reporter import HTMLReporter
from .json_reporter import JSONReporter
from .csv_reporter import CSVReporter
from .xml_reporter import XMLReporter
from .pdf_reporter import PDFReporter
from .yaml_reporter import YAMLReporter
from .visual_report import VisualReportGenerator
from .visual_html_reporter import VisualHTMLReporter

# Register reporters with the factory
ReporterFactory.register('HTMLReporter', HTMLReporter)
ReporterFactory.register('JSONReporter', JSONReporter)
ReporterFactory.register('CSVReporter', CSVReporter)
ReporterFactory.register('XMLReporter', XMLReporter)
ReporterFactory.register('PDFReporter', PDFReporter)
ReporterFactory.register('YAMLReporter', YAMLReporter)
ReporterFactory.register('VisualHTMLReporter', VisualHTMLReporter)

__all__ = [
    'BaseReporter',
    'ReportResult',
    'ReportMetadata',
    'ReporterError',
    'ReportGenerationError',
    'ReportFormatError',
    'ReporterFactory',
    'ReporterFactoryError',
    'ReporterRegistrationError',
    'ReporterNotFoundError',
    'HTMLReporter',
    'JSONReporter',
    'CSVReporter',
    'XMLReporter',
    'PDFReporter',
    'YAMLReporter',
    'VisualReportGenerator',
    'VisualHTMLReporter'
] 