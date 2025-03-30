"""
Parallel Manager Module for Summit SEO

This module provides the ParallelManager class which serves as the main interface
for parallel processing in the Summit SEO framework.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from summit_seo.parallel.executor import ExecutionStrategy, ParallelExecutor, WorkerType
from summit_seo.parallel.task import Task, TaskPriority, TaskStatus

logger = logging.getLogger(__name__)


class ProcessingStrategy(Enum):
    """
    Strategies for parallel processing.
    
    This enum defines the different strategies that can be used for
    parallel processing of tasks in the Summit SEO framework.
    """
    PARALLEL = auto()  # Simple parallel processing
    BATCHED = auto()   # Batch processing
    PRIORITY = auto()  # Priority-based processing
    GRAPH = auto()     # Dependency graph-based processing
    PRIORITY_GRAPH = auto()  # Priority + dependency graph
    WORK_STEALING = auto()  # Work-stealing queue


@dataclass
class ProcessingStatistics:
    """
    Statistics about parallel processing.
    
    This class holds various statistics about the parallel processing
    system, including number of tasks processed, success rate, etc.
    """
    submitted: int = 0
    completed: int = 0
    failed: int = 0
    cancelled: int = 0
    timed_out: int = 0
    avg_duration: float = 0.0
    max_concurrent: int = 0
    total_duration: float = 0.0
    work_stealing_transfers: int = 0


class ParallelManager:
    """
    Manages parallel processing of tasks.
    
    This class provides a high-level interface for parallel processing
    in the Summit SEO framework. It manages task submission, execution,
    and result collection.
    """
    
    def __init__(
        self,
        max_workers: int = 0,
        strategy: ProcessingStrategy = ProcessingStrategy.PARALLEL,
        worker_type: WorkerType = WorkerType.ASYNCIO,
        task_timeout: Optional[float] = None,
        batch_size: int = 10,
        task_callback: Optional[Callable] = None
    ):
        """
        Initialize the parallel manager.
        
        Args:
            max_workers: Maximum number of workers to use. If 0, use CPU count.
            strategy: Strategy to use for task processing.
            worker_type: Type of workers to use.
            task_timeout: Default timeout for tasks in seconds.
            batch_size: Batch size for BATCHED strategy.
            task_callback: Callback function for task status changes.
                The callback signature should be:
                callback(task_id, status, result=None, error=None)
        """
        self.max_workers = max_workers
        self.strategy = strategy
        self.worker_type = worker_type
        self.task_timeout = task_timeout
        self.batch_size = batch_size
        self.task_callback = task_callback
        
        # Map strategy to executor strategy
        strategy_map = {
            ProcessingStrategy.PARALLEL: ExecutionStrategy.FIFO,
            ProcessingStrategy.BATCHED: ExecutionStrategy.FIFO,
            ProcessingStrategy.PRIORITY: ExecutionStrategy.PRIORITY,
            ProcessingStrategy.GRAPH: ExecutionStrategy.DEPENDENCY,
            ProcessingStrategy.PRIORITY_GRAPH: ExecutionStrategy.DEPENDENCY,  # We'll handle priority in submit
            ProcessingStrategy.WORK_STEALING: ExecutionStrategy.WORK_STEALING,
        }
        
        # Create the executor
        self._executor = ParallelExecutor(
            max_workers=max_workers,
            execution_strategy=strategy_map[strategy],
            worker_type=worker_type,
            task_timeout=task_timeout
        )
        
        # Task management
        self._batches: List[List[Task]] = []
        self._current_batch: List[Task] = []
        self._batch_results: List[List[Any]] = []
        self._task_start_times: Dict[str, float] = {}
        
        # Control flags
        self._running = False
        self._paused = False
        self._session_start_time = 0
    
    async def start(self):
        """Start the parallel manager."""
        if self._running:
            logger.warning("Parallel manager is already running")
            return
        
        self._running = True
        self._paused = False
        self._session_start_time = time.time()
        
        # Start the executor
        await self._executor.start(task_callback=self._handle_task_callback)
        
        logger.info(f"Parallel manager started with strategy: {self.strategy.name}")
    
    async def stop(self):
        """Stop the parallel manager."""
        if not self._running:
            logger.warning("Parallel manager is not running")
            return
        
        logger.info("Stopping parallel manager...")
        
        # Stop the executor
        await self._executor.stop()
        
        self._running = False
        logger.info("Parallel manager stopped")
    
    async def pause(self):
        """Pause task processing."""
        if not self._running:
            logger.warning("Parallel manager is not running")
            return
        
        if self._paused:
            logger.warning("Parallel manager is already paused")
            return
        
        self._paused = True
        logger.info("Parallel manager paused")
    
    async def resume(self):
        """Resume task processing."""
        if not self._running:
            logger.warning("Parallel manager is not running")
            return
        
        if not self._paused:
            logger.warning("Parallel manager is not paused")
            return
        
        self._paused = False
        logger.info("Parallel manager resumed")
    
    async def submit(self, task: Task) -> asyncio.Future:
        """
        Submit a task for execution.
        
        Args:
            task: The task to execute.
            
        Returns:
            A future that will resolve when the task is complete.
        """
        if not self._running:
            raise RuntimeError("Parallel manager is not running")
        
        if self._paused:
            logger.warning("Parallel manager is paused, task will be queued but not executed")
        
        # Record task start time for statistics
        self._task_start_times[task.id] = time.time()
        
        # Handle batched strategy
        if self.strategy == ProcessingStrategy.BATCHED:
            self._current_batch.append(task)
            
            # If batch is full, submit it
            if len(self._current_batch) >= self.batch_size:
                batch = self._current_batch
                self._current_batch = []
                self._batches.append(batch)
                
                # Create and return a future for this task
                future = asyncio.Future()
                
                # Submit the batch
                batch_future = asyncio.create_task(self._process_batch(batch))
                
                # When batch is done, set result in individual futures
                batch_future.add_done_callback(
                    lambda f: self._handle_batch_completion(f, batch, [future])
                )
                
                return future
            else:
                # Batch not full yet, return a pending future
                future = asyncio.Future()
                return future
        else:
            # For PRIORITY_GRAPH strategy, handle priorities more carefully
            if self.strategy == ProcessingStrategy.PRIORITY_GRAPH:
                # Priority is already part of the task, but we may need to adjust
                # based on dependencies in more complex scenarios
                pass
            
            # Submit directly to executor
            return await self._executor.submit(task)
    
    async def submit_many(self, tasks: List[Task]) -> List[asyncio.Future]:
        """
        Submit multiple tasks for execution.
        
        Args:
            tasks: The tasks to execute.
            
        Returns:
            A list of futures that will resolve when the tasks are complete.
        """
        futures = []
        for task in tasks:
            futures.append(await self.submit(task))
        return futures
    
    async def submit_and_await(self, task: Task) -> Any:
        """
        Submit a task and wait for its completion.
        
        Args:
            task: The task to execute.
            
        Returns:
            The result of the task.
        """
        future = await self.submit(task)
        return await future
    
    async def submit_and_await_many(self, tasks: List[Task]) -> List[Any]:
        """
        Submit multiple tasks and wait for all to complete.
        
        Args:
            tasks: The tasks to execute.
            
        Returns:
            A list of results from the tasks.
        """
        futures = await self.submit_many(tasks)
        results = await asyncio.gather(*futures, return_exceptions=True)
        
        # Convert exceptions to results
        return [
            result if not isinstance(result, Exception) else result
            for result in results
        ]
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task if it hasn't started executing yet.
        
        Args:
            task_id: The ID of the task to cancel.
            
        Returns:
            True if the task was cancelled, False otherwise.
        """
        if not self._running:
            raise RuntimeError("Parallel manager is not running")
        
        return await self._executor.cancel_task(task_id)
    
    def get_statistics(self) -> ProcessingStatistics:
        """
        Get statistics about parallel processing.
        
        Returns:
            A ProcessingStatistics object with various statistics.
        """
        if not self._running and self._session_start_time == 0:
            # Return empty statistics if manager has never been started
            return ProcessingStatistics()
        
        # Get statistics from executor
        executor_stats = self._executor.get_statistics()
        
        # Create statistics object
        stats = ProcessingStatistics(
            submitted=executor_stats["tasks_submitted"],
            completed=executor_stats["tasks_completed"],
            failed=executor_stats["tasks_failed"],
            cancelled=executor_stats["tasks_cancelled"],
            timed_out=executor_stats["tasks_timed_out"],
            max_concurrent=executor_stats["max_concurrent_tasks"],
            total_duration=time.time() - self._session_start_time,
            work_stealing_transfers=executor_stats.get("work_stealing_transfers", 0)
        )
        
        # Calculate average duration if any tasks completed
        if stats.completed > 0:
            stats.avg_duration = executor_stats.get("avg_processing_time", 0)
        
        return stats
    
    async def wait_for_tasks(self, task_ids: List[str], timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Wait for specific tasks to complete.
        
        Args:
            task_ids: List of task IDs to wait for.
            timeout: Maximum time to wait in seconds.
            
        Returns:
            Dict mapping task IDs to their results or exceptions.
        """
        if not self._running:
            raise RuntimeError("Parallel manager is not running")
        
        return await self._executor.wait_for_tasks(task_ids, timeout)
    
    async def wait_all(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for all submitted tasks to complete.
        
        Args:
            timeout: Maximum time to wait in seconds.
            
        Returns:
            True if all tasks completed, False if timeout occurred.
        """
        if not self._running:
            raise RuntimeError("Parallel manager is not running")
        
        # For batched strategy, flush any pending batch
        if self.strategy == ProcessingStrategy.BATCHED and self._current_batch:
            batch = self._current_batch
            self._current_batch = []
            self._batches.append(batch)
            await self._process_batch(batch)
        
        return await self._executor.wait_all(timeout)
    
    async def get_pending_tasks(self) -> List[str]:
        """Get IDs of tasks that are pending execution."""
        if not self._running:
            raise RuntimeError("Parallel manager is not running")
        
        return await self._executor.get_pending_task_ids()
    
    async def get_running_tasks(self) -> List[str]:
        """Get IDs of tasks that are currently running."""
        if not self._running:
            raise RuntimeError("Parallel manager is not running")
        
        return await self._executor.get_running_task_ids()
    
    async def _process_batch(self, batch: List[Task]) -> List[Any]:
        """
        Process a batch of tasks.
        
        Args:
            batch: The batch of tasks to process.
            
        Returns:
            A list of results from the tasks.
        """
        # Submit all tasks in the batch
        futures = []
        for task in batch:
            future = await self._executor.submit(task)
            futures.append(future)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*futures, return_exceptions=True)
        
        # Store batch results
        self._batch_results.append(results)
        
        return results
    
    def _handle_batch_completion(
        self, batch_future, batch: List[Task], task_futures: List[asyncio.Future]
    ):
        """
        Handle completion of a batch of tasks.
        
        Args:
            batch_future: The future for the batch processing.
            batch: The batch of tasks.
            task_futures: The futures for individual tasks.
        """
        try:
            # Get batch results
            batch_results = batch_future.result()
            
            # Set results in individual futures
            for task_future, result in zip(task_futures, batch_results):
                if isinstance(result, Exception):
                    task_future.set_exception(result)
                else:
                    task_future.set_result(result)
        except Exception as e:
            # Set exception in all futures
            for task_future in task_futures:
                if not task_future.done():
                    task_future.set_exception(e)
    
    async def _handle_task_callback(
        self, task_id: str, status: TaskStatus, result=None, error=None
    ):
        """
        Handle task status changes.
        
        Args:
            task_id: The ID of the task.
            status: The new status of the task.
            result: The result of the task, if completed.
            error: The error that occurred, if failed.
        """
        # Update task timing statistics
        if status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            if task_id in self._task_start_times:
                start_time = self._task_start_times.pop(task_id)
                duration = time.time() - start_time
                logger.debug(f"Task {task_id} completed in {duration:.2f}s with status {status.name}")
        
        # Call user-provided callback if available
        if self.task_callback:
            await asyncio.create_task(
                self.task_callback(task_id, status, result, error)
            ) 