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

# Register reporters with the factory
ReporterFactory.register('json', JSONReporter)
ReporterFactory.register('html', HTMLReporter)
ReporterFactory.register('xml', XMLReporter)
ReporterFactory.register('pdf', PDFReporter)

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
    'PDFReporter'
] 