"""Worker implementations for parallel task execution."""

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, TypeVar, Union
import traceback

from .task import Task, TaskResult, TaskStatus

T = TypeVar('T')  # Type variable for task result
logger = logging.getLogger(__name__)


class Worker:
    """Worker for executing tasks."""
    
    def __init__(
        self,
        worker_id: str,
        max_concurrent_tasks: int = 1,
        executor_type: str = 'thread'
    ):
        """Initialize worker.
        
        Args:
            worker_id: Unique identifier for this worker.
            max_concurrent_tasks: Maximum number of concurrent tasks this worker can handle.
            executor_type: Type of executor to use ('thread' or 'process').
        """
        self.worker_id = worker_id
        self.max_concurrent_tasks = max_concurrent_tasks
        self.executor_type = executor_type
        self.active_tasks: Set[str] = set()
        self.completed_task_count = 0
        self.failed_task_count = 0
        self.is_running = False
        self.start_time = None
        self.executor = None
        
    async def start(self):
        """Start the worker."""
        if self.is_running:
            return
            
        if self.executor_type == 'thread':
            self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_tasks)
        elif self.executor_type == 'process':
            self.executor = ProcessPoolExecutor(max_workers=self.max_concurrent_tasks)
        else:
            raise ValueError(f"Unsupported executor type: {self.executor_type}")
            
        self.is_running = True
        self.start_time = datetime.now()
        logger.info(f"Worker {self.worker_id} started with {self.max_concurrent_tasks} slots")
        
    async def stop(self):
        """Stop the worker."""
        if not self.is_running:
            return
            
        logger.info(f"Worker {self.worker_id} stopping. Completed: {self.completed_task_count}, Failed: {self.failed_task_count}")
        
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None
            
        self.is_running = False
        
    async def execute_task(self, task: Task[T]) -> TaskResult[T]:
        """Execute a single task and return the result.
        
        Args:
            task: Task to execute.
            
        Returns:
            TaskResult with execution results.
        """
        if not self.is_running:
            await self.start()
            
        if len(self.active_tasks) >= self.max_concurrent_tasks:
            raise RuntimeError("Worker at maximum capacity")
            
        self.active_tasks.add(task.id)
        task.status = TaskStatus.RUNNING
        
        # Create task result
        result = TaskResult(
            task_id=task.id,
            status=TaskStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            # Execute the task
            if asyncio.iscoroutinefunction(task.func):
                # If the function is a coroutine function, await it
                task_result = await task.func(*task.args, **task.kwargs)
            else:
                # Execute in thread/process pool
                loop = asyncio.get_event_loop()
                task_result = await loop.run_in_executor(
                    self.executor,
                    lambda: task.func(*task.args, **task.kwargs)
                )
                
            # Update result
            result.result = task_result
            result.status = TaskStatus.COMPLETED
            result.end_time = datetime.now()
            self.completed_task_count += 1
            
        except Exception as e:
            # Handle task failure
            logger.exception(f"Task {task.id} failed: {str(e)}")
            result.error = e
            result.status = TaskStatus.FAILED
            result.end_time = datetime.now()
            
            # Add traceback to metadata
            result.metadata['traceback'] = traceback.format_exc()
            
            if task.retry_count < task.max_retries:
                # Mark for retry
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                result.metadata['retry'] = task.retry_count
            else:
                # No more retries
                task.status = TaskStatus.FAILED
                self.failed_task_count += 1
                
        finally:
            # Clean up
            self.active_tasks.remove(task.id)
            task.result = result
            
        return result
        
    def get_stats(self) -> Dict[str, Any]:
        """Get worker statistics."""
        current_time = datetime.now()
        uptime = (current_time - self.start_time).total_seconds() if self.start_time else 0
        
        return {
            'worker_id': self.worker_id,
            'executor_type': self.executor_type,
            'max_concurrent_tasks': self.max_concurrent_tasks,
            'active_tasks': len(self.active_tasks),
            'completed_task_count': self.completed_task_count,
            'failed_task_count': self.failed_task_count,
            'is_running': self.is_running,
            'uptime_seconds': uptime,
            'tasks_per_second': self.completed_task_count / uptime if uptime > 0 else 0,
        }


class WorkerPool:
    """Pool of workers for executing tasks in parallel."""
    
    def __init__(
        self,
        num_workers: int = 4,
        max_tasks_per_worker: int = 1,
        executor_type: str = 'thread'
    ):
        """Initialize worker pool.
        
        Args:
            num_workers: Number of workers in the pool.
            max_tasks_per_worker: Maximum number of concurrent tasks per worker.
            executor_type: Type of executor to use ('thread' or 'process').
        """
        self.workers: List[Worker] = []
        self.num_workers = num_workers
        self.max_tasks_per_worker = max_tasks_per_worker
        self.executor_type = executor_type
        self.worker_queue = asyncio.Queue()
        self.is_running = False
        
    async def start(self):
        """Start the worker pool."""
        if self.is_running:
            return
            
        # Create and start workers
        for i in range(self.num_workers):
            worker = Worker(
                worker_id=f"worker-{i+1}",
                max_concurrent_tasks=self.max_tasks_per_worker,
                executor_type=self.executor_type
            )
            await worker.start()
            self.workers.append(worker)
            await self.worker_queue.put(worker)
            
        self.is_running = True
        logger.info(f"WorkerPool started with {self.num_workers} workers")
        
    async def stop(self):
        """Stop the worker pool."""
        if not self.is_running:
            return
            
        logger.info("Stopping worker pool")
        for worker in self.workers:
            await worker.stop()
            
        self.is_running = False
        self.workers = []
        
        # Clear the queue
        while not self.worker_queue.empty():
            try:
                self.worker_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
                
    async def get_worker(self) -> Worker:
        """Get an available worker from the pool.
        
        Returns:
            Worker instance to use for task execution.
        """
        if not self.is_running:
            await self.start()
            
        return await self.worker_queue.get()
        
    async def release_worker(self, worker: Worker):
        """Return a worker to the pool.
        
        Args:
            worker: Worker to return to the pool.
        """
        await self.worker_queue.put(worker)
        
    async def execute_task(self, task: Task[T]) -> TaskResult[T]:
        """Execute a task using an available worker.
        
        Args:
            task: Task to execute.
            
        Returns:
            TaskResult with execution results.
        """
        worker = await self.get_worker()
        try:
            return await worker.execute_task(task)
        finally:
            await self.release_worker(worker)
            
    def get_stats(self) -> Dict[str, Any]:
        """Get worker pool statistics."""
        worker_stats = [worker.get_stats() for worker in self.workers]
        
        total_active = sum(stats['active_tasks'] for stats in worker_stats)
        total_completed = sum(stats['completed_task_count'] for stats in worker_stats)
        total_failed = sum(stats['failed_task_count'] for stats in worker_stats)
        
        return {
            'num_workers': self.num_workers,
            'active_workers': len(self.workers),
            'total_active_tasks': total_active,
            'total_completed_tasks': total_completed,
            'total_failed_tasks': total_failed,
            'is_running': self.is_running,
            'workers': worker_stats,
        } 