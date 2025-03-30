"""
Summit SEO - A comprehensive SEO analysis tool.
"""

# Base version info
__version__ = "0.3.0"

# Import core components
from . import analyzer
from . import collector
from . import processor
from . import reporter
from . import visualization
from . import progress
from . import cli

# Import commonly used classes for easy access
from .analyzer import AnalyzerFactory, BaseAnalyzer
from .collector import CollectorFactory, BaseCollector
from .processor import ProcessorFactory, BaseProcessor
from .reporter import ReporterFactory, BaseReporter
from .visualization import VisualizationFactory
from .progress import ProgressTracker
from .error_handling import (
    ErrorWithSuggestions,
    ActionableSuggestion,
    ConsoleErrorReporter,
    FileErrorReporter,
    get_suggestion_for_error
)

# Other imports will be exported but not imported at the top level
__all__ = [
    # Version
    '__version__',
    
    # Core factories
    'AnalyzerFactory',
    'CollectorFactory',
    'ProcessorFactory',
    'ReporterFactory',
    'VisualizationFactory',
    
    # Base classes
    'BaseAnalyzer',
    'BaseCollector',
    'BaseProcessor',
    'BaseReporter',
    'ProgressTracker',
    
    # Error handling
    'ErrorWithSuggestions',
    'ActionableSuggestion',
    'ConsoleErrorReporter',
    'FileErrorReporter',
    'get_suggestion_for_error',
    'cache_manager',
    'ParallelManager',
    'parallel_manager',
    'ProcessingStrategy'
]

# Define getter functions to lazily import modules when needed
def get_analyzer_factory():
    from .analyzer import AnalyzerFactory
    return AnalyzerFactory

def get_collector_factory():
    from .collector import CollectorFactory
    return CollectorFactory

def get_processor_factory():
    from .processor import ProcessorFactory
    return ProcessorFactory

def get_reporter_factory():
    from .reporter import ReporterFactory
    return ReporterFactory

def get_cache_factory():
    from .cache import CacheFactory
    return CacheFactory

def get_cache_manager():
    from .cache import cache_manager
    return cache_manager

def get_parallel_manager():
    from .parallel import parallel_manager
    return parallel_manager

def get_parallel_manager_class():
    from .parallel import ParallelManager
    return ParallelManager

def get_processing_strategy():
    from .parallel import ProcessingStrategy
    return ProcessingStrategy

# Setup properties for lazy loading
AnalyzerFactory = property(lambda _: get_analyzer_factory())
CollectorFactory = property(lambda _: get_collector_factory())
ProcessorFactory = property(lambda _: get_processor_factory())
ReporterFactory = property(lambda _: get_reporter_factory())
CacheFactory = property(lambda _: get_cache_factory())
cache_manager = property(lambda _: get_cache_manager())
ParallelManager = property(lambda _: get_parallel_manager_class())
parallel_manager = property(lambda _: get_parallel_manager())
ProcessingStrategy = property(lambda _: get_processing_strategy())
