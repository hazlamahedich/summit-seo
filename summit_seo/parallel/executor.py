"""
Parallel Executor Module for Summit SEO

This module provides classes for executing tasks in parallel using different
execution strategies and worker management approaches.
"""

import asyncio
import logging
import time
from collections import deque
from enum import Enum, auto
from functools import partial
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set, Tuple, Union

from summit_seo.parallel.task import Task, TaskPriority, TaskStatus

logger = logging.getLogger(__name__)


class ExecutionStrategy(Enum):
    """Execution strategies for parallel task processing."""
    FIFO = auto()  # First In, First Out
    PRIORITY = auto()  # Priority-based ordering
    DEPENDENCY = auto()  # Dependency-based ordering
    WORK_STEALING = auto()  # Work-stealing strategy
    ADAPTIVE = auto()  # Adaptive strategy that changes based on system load


class WorkerType(Enum):
    """Types of workers for task execution."""
    ASYNCIO = auto()  # AsyncIO-based worker
    THREAD = auto()  # Thread-based worker
    PROCESS = auto()  # Process-based worker


class ParallelExecutor:
    """
    Executes tasks in parallel with different execution strategies.
    
    This class is responsible for managing a pool of workers and executing
    tasks using the specified execution strategy.
    """
    
    def __init__(
        self,
        max_workers: int = 0,
        execution_strategy: ExecutionStrategy = ExecutionStrategy.FIFO,
        worker_type: WorkerType = WorkerType.ASYNCIO,
        task_timeout: Optional[float] = None
    ):
        """
        Initialize the parallel executor.
        
        Args:
            max_workers: Maximum number of workers to use. If 0, use CPU count.
            execution_strategy: Strategy to use for task execution ordering.
            worker_type: Type of workers to use.
            task_timeout: Default timeout for tasks in seconds.
        """
        import multiprocessing
        
        self.max_workers = max_workers if max_workers > 0 else multiprocessing.cpu_count()
        self.execution_strategy = execution_strategy
        self.worker_type = worker_type
        self.task_timeout = task_timeout
        
        # Task queues and tracking
        self._task_queue = asyncio.PriorityQueue()
        self._dependency_graph: Dict[str, Set[str]] = {}  # task_id -> set of dependency task_ids
        self._reverse_dependency_graph: Dict[str, Set[str]] = {}  # task_id -> set of dependent task_ids
        self._task_map: Dict[str, Task] = {}  # task_id -> Task
        self._task_futures: Dict[str, asyncio.Future] = {}  # task_id -> Future
        self._completed_tasks: Set[str] = set()
        self._failed_tasks: Set[str] = set()
        self._running_tasks: Set[str] = set()
        
        # Worker management
        self._workers: List[asyncio.Task] = []
        self._idle_workers: Set[int] = set()
        self._worker_queues: List[asyncio.Queue] = []
        self._work_stealing_enabled = (execution_strategy == ExecutionStrategy.WORK_STEALING)
        
        # Control
        self._running = False
        self._stop_event = asyncio.Event()
        self._tasks_added_event = asyncio.Event()
        
        # Statistics
        self._stats = {
            "tasks_submitted": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_cancelled": 0,
            "tasks_timed_out": 0,
            "work_stealing_transfers": 0,
            "start_time": 0,
            "total_processing_time": 0,
            "max_concurrent_tasks": 0,
        }
        
        # Callback for task status changes
        self._task_callback: Optional[Callable] = None
    
    @property
    def running(self) -> bool:
        """Check if the executor is running."""
        return self._running
    
    async def start(self, task_callback: Optional[Callable] = None):
        """
        Start the executor.
        
        Args:
            task_callback: Callback function for task status changes.
                The callback signature should be:
                callback(task_id, status, result=None, error=None)
        """
        if self._running:
            logger.warning("Executor is already running")
            return
        
        self._running = True
        self._stop_event.clear()
        self._task_callback = task_callback
        self._stats["start_time"] = time.time()
        
        # Set up worker queues for work stealing
        if self._work_stealing_enabled:
            self._worker_queues = [asyncio.Queue() for _ in range(self.max_workers)]
        
        # Start workers
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker_loop(worker_id=i))
            self._workers.append(worker)
            self._idle_workers.add(i)
        
        logger.info(f"Started {self.max_workers} workers with {self.execution_strategy.name} strategy")
    
    async def stop(self):
        """Stop the executor and wait for all workers to complete."""
        if not self._running:
            logger.warning("Executor is not running")
            return
        
        logger.info("Stopping executor...")
        self._running = False
        self._stop_event.set()
        
        # Wait for all workers to complete
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)
            self._workers.clear()
        
        # Calculate total processing time
        self._stats["total_processing_time"] = time.time() - self._stats["start_time"]
        
        logger.info("Executor stopped")
    
    async def submit(self, task: Task) -> asyncio.Future:
        """
        Submit a task for execution.
        
        Args:
            task: The task to execute.
            
        Returns:
            A future that will resolve when the task is complete.
        """
        if not self._running:
            raise RuntimeError("Executor is not running")
        
        # Create a future for this task
        future = asyncio.Future()
        self._task_futures[task.id] = future
        
        # Store the task in the task map
        self._task_map[task.id] = task
        
        # Register dependencies
        if task.dependencies:
            self._dependency_graph[task.id] = set(task.dependencies)
            
            # Update reverse dependency graph
            for dep_id in task.dependencies:
                if dep_id not in self._reverse_dependency_graph:
                    self._reverse_dependency_graph[dep_id] = set()
                self._reverse_dependency_graph[dep_id].add(task.id)
        else:
            self._dependency_graph[task.id] = set()
        
        # If all dependencies are satisfied, add to queue
        if self._are_dependencies_satisfied(task.id):
            await self._enqueue_task(task)
        
        # Signal that new tasks have been added
        self._tasks_added_event.set()
        self._tasks_added_event.clear()
        
        # Update statistics
        self._stats["tasks_submitted"] += 1
        
        return future
    
    async def submit_all(self, tasks: List[Task]) -> List[asyncio.Future]:
        """
        Submit multiple tasks for execution.
        
        Args:
            tasks: The tasks to execute.
            
        Returns:
            A list of futures that will resolve when the tasks are complete.
        """
        return [await self.submit(task) for task in tasks]
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task if it hasn't started executing yet.
        
        Args:
            task_id: The ID of the task to cancel.
            
        Returns:
            True if the task was cancelled, False otherwise.
        """
        if task_id not in self._task_map:
            logger.warning(f"Task {task_id} not found")
            return False
        
        if task_id in self._running_tasks:
            logger.warning(f"Task {task_id} is already running and cannot be cancelled")
            return False
        
        if task_id in self._completed_tasks or task_id in self._failed_tasks:
            logger.warning(f"Task {task_id} has already completed or failed")
            return False
        
        # Remove task from queue (if present)
        # Note: This is inefficient but necessary since asyncio.PriorityQueue doesn't
        # provide a way to remove items
        new_queue = asyncio.PriorityQueue()
        while not self._task_queue.empty():
            priority, tid, t = await self._task_queue.get()
            if tid != task_id:
                await new_queue.put((priority, tid, t))
        self._task_queue = new_queue
        
        # Mark as cancelled and notify callback
        self._stats["tasks_cancelled"] += 1
        
        # Set the future as cancelled
        future = self._task_futures.get(task_id)
        if future and not future.done():
            future.cancel()
        
        # Notify callback if registered
        if self._task_callback:
            await asyncio.create_task(
                self._task_callback(task_id, TaskStatus.CANCELLED)
            )
        
        return True
    
    @property
    def workers(self) -> List[asyncio.Task]:
        """Get the list of worker tasks."""
        return list(self._workers)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the executor.
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            "start_time": self._stats["start_time"],
            "pending_tasks": len(self._task_map) - len(self._completed_tasks) - len(self._failed_tasks) - len(self._running_tasks),
            "current_running": len(self._running_tasks),
            "current_queue_size": self._task_queue.qsize(),
            "tasks_submitted": self._stats["tasks_submitted"],
            "submitted": self._stats["tasks_submitted"],  # Alias for compatibility
            "tasks_completed": self._stats["tasks_completed"],
            "completed": self._stats["tasks_completed"],  # Alias for compatibility
            "tasks_failed": self._stats["tasks_failed"],
            "failed": self._stats["tasks_failed"],  # Alias for compatibility
            "tasks_cancelled": self._stats["tasks_cancelled"],
            "cancelled": self._stats["tasks_cancelled"],  # Alias for compatibility
            "tasks_timed_out": self._stats["tasks_timed_out"],
            "max_concurrent_tasks": self._stats["max_concurrent_tasks"],
            "total_processing_time": self._stats["total_processing_time"],
            "avg_processing_time": (
                self._stats["total_processing_time"] / max(1, self._stats["tasks_completed"])
                if self._stats["tasks_completed"] > 0 else 0.0
            ),
            "work_stealing_transfers": self._stats["work_stealing_transfers"],
        }
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
        futures = [self._task_futures[tid] for tid in task_ids if tid in self._task_futures]
        
        try:
            await asyncio.wait(futures, timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Timeout waiting for tasks: {task_ids}")
        
        results = {}
        for tid in task_ids:
            if tid in self._task_futures:
                future = self._task_futures[tid]
                if future.done():
                    try:
                        results[tid] = future.result()
                    except Exception as e:
                        results[tid] = e
                else:
                    results[tid] = None
            else:
                results[tid] = None
        
        return results
    
    async def wait_all(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for all submitted tasks to complete.
        
        Args:
            timeout: Maximum time to wait in seconds.
            
        Returns:
            True if all tasks completed, False if timeout occurred.
        """
        futures = list(self._task_futures.values())
        if not futures:
            return True
        
        try:
            await asyncio.wait(futures, timeout=timeout)
            return all(future.done() for future in futures)
        except asyncio.TimeoutError:
            return False
    
    async def _worker_loop(self, worker_id: int):
        """
        Main worker loop that processes tasks from the queue.
        
        Args:
            worker_id: ID of this worker.
        """
        logger.debug(f"Worker {worker_id} started")
        
        try:
            while self._running and not self._stop_event.is_set():
                # Try to get a task
                task = await self._get_task(worker_id)
                
                if task is None:
                    # No task available, wait for new tasks or stop event
                    done, pending = await asyncio.wait(
                        [
                            asyncio.create_task(self._stop_event.wait()),
                            asyncio.create_task(self._tasks_added_event.wait()),
                        ],
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    for fut in done:
                        fut.result()  # Check for exceptions
                    for fut in pending:
                        fut.cancel()
                    continue
                
                # Mark worker as busy
                self._idle_workers.discard(worker_id)
                
                # Mark task as running
                task_id = task.id
                self._running_tasks.add(task_id)
                
                # Update max concurrent tasks statistic
                current_concurrent = len(self._running_tasks)
                if current_concurrent > self._stats["max_concurrent_tasks"]:
                    self._stats["max_concurrent_tasks"] = current_concurrent
                
                # Notify task started
                if self._task_callback:
                    await asyncio.create_task(
                        self._task_callback(task_id, TaskStatus.RUNNING)
                    )
                
                # Execute the task with timeout if specified
                task_timeout = task.timeout if task.timeout is not None else self.task_timeout
                try:
                    if task_timeout is not None:
                        result = await asyncio.wait_for(task.coro, timeout=task_timeout)
                    else:
                        result = await task.coro
                    
                    # Mark task as completed
                    self._running_tasks.discard(task_id)
                    self._completed_tasks.add(task_id)
                    
                    # Set result in future
                    future = self._task_futures.get(task_id)
                    if future and not future.done():
                        future.set_result(result)
                    
                    # Notify task completed
                    if self._task_callback:
                        await asyncio.create_task(
                            self._task_callback(task_id, TaskStatus.COMPLETED, result=result)
                        )
                    
                    # Update statistics
                    self._stats["tasks_completed"] += 1
                    
                    # Check if this task was a dependency for other tasks
                    await self._process_completed_dependency(task_id)
                    
                except asyncio.TimeoutError:
                    # Task timed out
                    logger.warning(f"Task {task_id} timed out after {task_timeout}s")
                    
                    # Mark task as failed
                    self._running_tasks.discard(task_id)
                    self._failed_tasks.add(task_id)
                    
                    # Set exception in future
                    error = TimeoutError(f"Task {task_id} timed out after {task_timeout}s")
                    future = self._task_futures.get(task_id)
                    if future and not future.done():
                        future.set_exception(error)
                    
                    # Notify task failed
                    if self._task_callback:
                        await asyncio.create_task(
                            self._task_callback(task_id, TaskStatus.FAILED, error=error)
                        )
                    
                    # Update statistics
                    self._stats["tasks_failed"] += 1
                    self._stats["tasks_timed_out"] += 1
                    
                except Exception as e:
                    # Task failed with exception
                    logger.exception(f"Task {task_id} failed with exception: {e}")
                    
                    # Mark task as failed
                    self._running_tasks.discard(task_id)
                    self._failed_tasks.add(task_id)
                    
                    # Set exception in future
                    future = self._task_futures.get(task_id)
                    if future and not future.done():
                        future.set_exception(e)
                    
                    # Notify task failed
                    if self._task_callback:
                        await asyncio.create_task(
                            self._task_callback(task_id, TaskStatus.FAILED, error=e)
                        )
                    
                    # Update statistics
                    self._stats["tasks_failed"] += 1
                
                # Mark worker as idle
                self._idle_workers.add(worker_id)
        
        except Exception as e:
            logger.exception(f"Worker {worker_id} exited with exception: {e}")
        
        logger.debug(f"Worker {worker_id} stopped")
    
    async def _get_task(self, worker_id: int) -> Optional[Task]:
        """
        Get the next task to execute based on the execution strategy.
        
        Args:
            worker_id: ID of the worker requesting a task.
            
        Returns:
            The next task to execute, or None if no tasks are available.
        """
        # Handle different task acquisition strategies
        if self.execution_strategy == ExecutionStrategy.WORK_STEALING:
            # First try the worker's own queue
            try:
                return await asyncio.wait_for(self._worker_queues[worker_id].get(), timeout=0.01)
            except (asyncio.TimeoutError, asyncio.QueueEmpty):
                pass
            
            # If no task in own queue, try to steal from other workers
            idle_attempts = 0
            while idle_attempts < 3:  # Try a few times before giving up
                # Try to steal from the worker with the most tasks
                most_tasks = -1
                steal_from = -1
                
                for i in range(self.max_workers):
                    if i != worker_id:
                        queue_size = self._worker_queues[i].qsize()
                        if queue_size > most_tasks:
                            most_tasks = queue_size
                            steal_from = i
                
                if most_tasks > 0:
                    try:
                        task = await asyncio.wait_for(self._worker_queues[steal_from].get(), timeout=0.01)
                        self._stats["work_stealing_transfers"] += 1
                        return task
                    except (asyncio.TimeoutError, asyncio.QueueEmpty):
                        pass
                
                # Wait a bit before trying again
                await asyncio.sleep(0.05)
                idle_attempts += 1
            
            # Finally, try the global queue
            try:
                priority, task_id, task = await asyncio.wait_for(self._task_queue.get(), timeout=0.01)
                return task
            except (asyncio.TimeoutError, asyncio.QueueEmpty):
                return None
        
        else:
            # For other strategies, use the global queue
            try:
                priority, task_id, task = await asyncio.wait_for(self._task_queue.get(), timeout=0.01)
                return task
            except (asyncio.TimeoutError, asyncio.QueueEmpty):
                return None
    
    async def _enqueue_task(self, task: Task):
        """
        Add a task to the appropriate queue based on execution strategy.
        
        Args:
            task: The task to add to the queue.
        """
        # Calculate priority value (lower is higher priority)
        priority_value = task.priority.value
        
        # For dependency-based execution, adjust priority based on dependency depth
        if self.execution_strategy == ExecutionStrategy.DEPENDENCY:
            # Tasks with more dependents should run earlier
            dependents = self._reverse_dependency_graph.get(task.id, set())
            priority_value -= len(dependents) * 10
        
        if self.execution_strategy == ExecutionStrategy.WORK_STEALING:
            # Choose a worker with the least tasks
            least_tasks = float('inf')
            target_worker = 0
            
            for i in range(self.max_workers):
                queue_size = self._worker_queues[i].qsize()
                if queue_size < least_tasks:
                    least_tasks = queue_size
                    target_worker = i
            
            # Add to the chosen worker's queue
            await self._worker_queues[target_worker].put(task)
        else:
            # Add to global queue with priority
            await self._task_queue.put((priority_value, task.id, task))
    
    def _are_dependencies_satisfied(self, task_id: str) -> bool:
        """
        Check if all dependencies for a task are satisfied.
        
        Args:
            task_id: The ID of the task to check.
            
        Returns:
            True if all dependencies are satisfied (completed), False otherwise.
        """
        dependencies = self._dependency_graph.get(task_id, set())
        return all(dep_id in self._completed_tasks for dep_id in dependencies)
    
    async def _process_completed_dependency(self, task_id: str):
        """
        Process tasks that were waiting on a completed dependency.
        
        Args:
            task_id: The ID of the completed task.
        """
        # Find tasks that were waiting on this dependency
        dependent_tasks = self._reverse_dependency_graph.get(task_id, set())
        
        for dependent_id in dependent_tasks:
            # If all dependencies are now satisfied, add to queue
            if self._are_dependencies_satisfied(dependent_id):
                dependent_task = self._task_map.get(dependent_id)
                if dependent_task:
                    await self._enqueue_task(dependent_task)
    
    async def get_pending_task_ids(self) -> List[str]:
        """Get IDs of tasks that are pending execution."""
        return [
            task_id for task_id in self._task_map.keys()
            if task_id not in self._completed_tasks
            and task_id not in self._failed_tasks
            and task_id not in self._running_tasks
        ]
    
    async def get_running_task_ids(self) -> List[str]:
        """Get IDs of tasks that are currently running."""
        return list(self._running_tasks)
    
    async def get_completed_task_ids(self) -> List[str]:
        """Get IDs of tasks that have completed successfully."""
        return list(self._completed_tasks)
    
    async def get_failed_task_ids(self) -> List[str]:
        """Get IDs of tasks that have failed."""
        return list(self._failed_tasks) 