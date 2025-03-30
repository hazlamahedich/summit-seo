"""
Parallel Processing Module for Summit SEO

This module provides parallel processing capabilities for Summit SEO,
enabling efficient execution of tasks across multiple workers. It supports
various execution strategies including priority-based, dependency-based,
and work-stealing approaches.
"""

from summit_seo.parallel.executor import (
    ExecutionStrategy,
    ParallelExecutor,
    WorkerType,
)
from summit_seo.parallel.manager import (
    ParallelManager,
    ProcessingStatistics,
    ProcessingStrategy,
)
from summit_seo.parallel.task import (
    Task,
    TaskGroup,
    TaskPriority,
    TaskResult,
    TaskStatus,
    create_task,
)

# Global instance for application-wide use
parallel_manager = None

def initialize_parallel_manager(
    max_workers=0,
    strategy=ProcessingStrategy.PARALLEL,
    **kwargs
):
    """
    Initialize the global parallel manager instance.
    
    Args:
        max_workers: Maximum number of workers to use
        strategy: Processing strategy to use
        **kwargs: Additional arguments for ParallelManager constructor
    
    Returns:
        The initialized ParallelManager instance
    """
    global parallel_manager
    if parallel_manager is None:
        parallel_manager = ParallelManager(
            max_workers=max_workers,
            strategy=strategy,
            **kwargs
        )
    return parallel_manager

def get_parallel_manager():
    """
    Get the global parallel manager instance.
    
    Returns:
        The global ParallelManager instance, or None if not initialized
    """
    return parallel_manager

__all__ = [
    # Classes
    'ExecutionStrategy',
    'ParallelExecutor',
    'ParallelManager',
    'ProcessingStatistics',
    'ProcessingStrategy',
    'Task',
    'TaskGroup',
    'TaskPriority',
    'TaskResult',
    'TaskStatus',
    'WorkerType',
    
    # Functions
    'create_task',
    'initialize_parallel_manager',
    'get_parallel_manager',
    
    # Variables
    'parallel_manager'
] 