"""Progress tracking module for Summit SEO.

This module provides components for tracking progress of analysis operations,
estimating completion time, and visualizing progress information.
"""

from summit_seo.progress.base import (
    ProgressTracker, 
    ProgressState,
    ProgressStage,
    ProgressError
)
from summit_seo.progress.factory import ProgressFactory
from summit_seo.progress.simple_tracker import SimpleProgressTracker
from summit_seo.progress.analyzer_progress import AnalyzerProgressTracker

__all__ = [
    'ProgressTracker',
    'ProgressState',
    'ProgressStage',
    'ProgressError',
    'ProgressFactory',
    'SimpleProgressTracker',
    'AnalyzerProgressTracker'
]

# Register all progress trackers with the factory
def _register_trackers():
    from summit_seo.progress.factory import ProgressFactory
    from summit_seo.progress.simple_tracker import SimpleProgressTracker
    from summit_seo.progress.analyzer_progress import AnalyzerProgressTracker
    
    ProgressFactory.register("simple", SimpleProgressTracker)
    ProgressFactory.register("analyzer", AnalyzerProgressTracker)

_register_trackers() 