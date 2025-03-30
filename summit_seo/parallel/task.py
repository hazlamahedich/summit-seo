"""
Task Module for Summit SEO Parallel Processing

This module defines the core Task class and related types for the parallel
processing system in Summit SEO.
"""

import asyncio
import inspect
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set, Union


class TaskStatus(Enum):
    """Status of a parallel task."""
    PENDING = auto()    # Task has been created but not started
    SCHEDULED = auto()  # Task has been scheduled for execution
    RUNNING = auto()    # Task is currently running
    COMPLETED = auto()  # Task completed successfully
    FAILED = auto()     # Task failed with an exception
    CANCELLED = auto()  # Task was cancelled before completion
    TIMEOUT = auto()    # Task timed out


class TaskPriority(Enum):
    """Priority levels for parallel tasks."""
    CRITICAL = 0   # Highest priority
    HIGH = 1       # High priority
    MEDIUM = 2     # Medium priority
    NORMAL = 3     # Normal priority
    LOW = 4        # Low priority
    BACKGROUND = 5 # Lowest priority


class TaskResult:
    """
    Result of a parallel task.
    
    This class encapsulates the result of a task execution, including
    success/failure status, result value, and error information.
    """
    
    def __init__(
        self, 
        task_id: str, 
        status: TaskStatus,
        result: Any = None,
        error: Optional[Exception] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ):
        """
        Initialize a task result.
        
        Args:
            task_id: ID of the task
            status: Status of the task
            result: Result value (if task completed successfully)
            error: Exception (if task failed)
            start_time: Time when task started execution
            end_time: Time when task completed execution
        """
        self.task_id = task_id
        self.status = status
        self.result = result
        self.error = error
        self.start_time = start_time
        self.end_time = end_time
    
    @property
    def is_success(self) -> bool:
        """Check if the task completed successfully."""
        return self.status == TaskStatus.COMPLETED
    
    @property
    def is_failure(self) -> bool:
        """Check if the task failed."""
        return self.status in [TaskStatus.FAILED, TaskStatus.TIMEOUT]
    
    @property
    def duration(self) -> Optional[float]:
        """Get the duration of the task execution in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    def get_error_message(self) -> Optional[str]:
        """Get the error message if the task failed."""
        if self.error:
            return str(self.error)
        return None
    
    def __str__(self) -> str:
        """Get string representation of the task result."""
        status_str = self.status.name
        if self.is_success:
            return f"TaskResult({self.task_id}, {status_str})"
        elif self.is_failure:
            return f"TaskResult({self.task_id}, {status_str}, error={self.get_error_message()})"
        else:
            return f"TaskResult({self.task_id}, {status_str})"


class Task:
    """
    Represents a unit of work in the parallel processing system.
    
    A task encapsulates a coroutine or function to be executed, along with
    metadata such as ID, name, priority, dependencies, and timeout.
    """
    
    def __init__(
        self,
        coro: Coroutine,
        id: Optional[str] = None,
        name: Optional[str] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        dependencies: Optional[List[str]] = None,
        timeout: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a task.
        
        Args:
            coro: Coroutine to execute
            id: Task ID (generated if not provided)
            name: Human-readable name for the task
            priority: Task priority
            dependencies: List of task IDs that must complete before this task
            timeout: Timeout for task execution in seconds
            metadata: Additional metadata for the task
        """
        # Ensure we have a coroutine
        if not inspect.iscoroutine(coro):
            raise TypeError("Task requires a coroutine object")
        
        self.coro = coro
        self.id = id or str(uuid.uuid4())
        self.name = name or f"Task-{self.id[:8]}"
        self.priority = priority
        self.dependencies = dependencies or []
        self.timeout = timeout
        self.metadata = metadata or {}
        
        # Status tracking
        self._status = TaskStatus.PENDING
        self._result = None
        self._error = None
        self._start_time = None
        self._end_time = None
        self.created_at = datetime.now()
    
    @property
    def status(self) -> TaskStatus:
        """Get the current status of the task."""
        return self._status
    
    @status.setter
    def status(self, value: TaskStatus):
        """Set the status of the task."""
        self._status = value
        
        # Update timing information
        if value == TaskStatus.RUNNING and not self._start_time:
            self._start_time = time.time()
        elif value in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.TIMEOUT]:
            self._end_time = time.time()
    
    @property
    def result(self):
        """Get the result of the task."""
        return self._result
    
    @result.setter
    def result(self, value):
        """Set the result of the task."""
        self._result = value
        if value is not None:
            self.status = TaskStatus.COMPLETED
    
    @property
    def error(self):
        """Get the error of the task."""
        return self._error
    
    @error.setter
    def error(self, value):
        """Set the error of the task."""
        self._error = value
        if value is not None:
            self.status = TaskStatus.FAILED
    
    @property
    def start_time(self):
        """Get the start time of the task."""
        return self._start_time
    
    @start_time.setter
    def start_time(self, value):
        """Set the start time of the task."""
        self._start_time = value
    
    @property
    def end_time(self):
        """Get the end time of the task."""
        return self._end_time
    
    @end_time.setter
    def end_time(self, value):
        """Set the end time of the task."""
        self._end_time = value
    
    @property
    def duration(self) -> Optional[float]:
        """Get the duration of the task execution in seconds."""
        if self._start_time and self._end_time:
            return self._end_time - self._start_time
        return None

    async def run(self) -> Any:
        """
        Run the task and return the result.
        
        This method executes the task's coroutine, handling timeouts and
        exceptions. It updates the task's status, result, and timing information.
        
        Returns:
            The result of the coroutine execution
            
        Raises:
            Exception: Any exception raised by the coroutine
            asyncio.TimeoutError: If the task execution exceeds the timeout
        """
        self.status = TaskStatus.RUNNING
        
        try:
            if self.timeout:
                # Run with timeout
                result = await asyncio.wait_for(self.coro, timeout=self.timeout)
            else:
                # Run normally
                result = await self.coro
                
            # Update task state
            self._result = result
            self.status = TaskStatus.COMPLETED
            return result
            
        except asyncio.TimeoutError:
            # Handle timeout
            self._error = asyncio.TimeoutError(f"Task {self.id} timed out after {self.timeout}s")
            self.status = TaskStatus.FAILED
            raise self._error
            
        except asyncio.CancelledError:
            # Handle cancellation
            self.status = TaskStatus.CANCELLED
            raise
            
        except Exception as e:
            # Handle other exceptions
            self._error = e
            self.status = TaskStatus.FAILED
            raise
    
    def cancel(self) -> bool:
        """
        Cancel the task if it's running.
        
        Returns:
            True if the task was cancelled, False if it was already completed
        """
        # First set the status to cancelled
        if self.status in [TaskStatus.PENDING, TaskStatus.SCHEDULED, TaskStatus.RUNNING]:
            self.status = TaskStatus.CANCELLED
            # Don't raise the exception here - the test expects future.result() to raise it
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert task to a dictionary representation.
        
        Returns:
            A dictionary representation of the task
        """
        result = {
            "id": self.id,
            "name": self.name,
            "status": self.status.name,
            "priority": self.priority.name,
            "dependencies": self.dependencies,
            "created_at": self.created_at.isoformat() if hasattr(self, 'created_at') else None,
        }
        
        # Add runtime information if available
        if self._start_time:
            if isinstance(self._start_time, datetime):
                result["start_time"] = self._start_time.isoformat()
            else:
                result["start_time"] = datetime.fromtimestamp(self._start_time).isoformat()
                
        if self._end_time:
            if isinstance(self._end_time, datetime):
                result["end_time"] = self._end_time.isoformat()
            else:
                result["end_time"] = datetime.fromtimestamp(self._end_time).isoformat()
                
        if self.duration:
            result["duration"] = self.duration
            
        # Add result or error if completed
        if self.status == TaskStatus.COMPLETED and self._result is not None:
            result["result"] = str(self._result)
        elif self.status == TaskStatus.FAILED and self._error is not None:
            result["error"] = str(self._error)
            
        return result
    
    def __eq__(self, other):
        """
        Check equality based on task ID.
        
        Two tasks are considered equal if they have the same ID.
        """
        if not isinstance(other, Task):
            return NotImplemented
        return self.id == other.id
    
    def __lt__(self, other):
        """
        Compare tasks by priority for priority queue ordering.
        
        Lower priority value means higher priority.
        """
        if not isinstance(other, Task):
            return NotImplemented
        return self.priority.value < other.priority.value
    
    def __repr__(self) -> str:
        """Get detailed representation of the task."""
        return f"Task({self.id}, {self.name}, status={self.status.name})"
    
    def __str__(self) -> str:
        """Get string representation of the task."""
        return f"Task({self.id}, {self.name}, priority={self.priority.name}, status={self.status.name})"


class TaskGroup:
    """
    A group of related tasks that can be managed together.
    
    This class provides functionality for creating and managing groups of
    related tasks, including submitting them together and tracking their
    collective progress.
    """
    
    def __init__(
        self, 
        name: str, 
        id: Optional[str] = None,
        tasks: Optional[List[Task]] = None
    ):
        """
        Initialize a task group.
        
        Args:
            name: Name of the task group
            id: ID of the task group (generated if not provided)
            tasks: Initial list of tasks in the group
        """
        self.name = name
        self.id = id or str(uuid.uuid4())
        self.tasks = list(tasks) if tasks else []
        self.results: Dict[str, Any] = {}
    
    def add_task(self, task: Task):
        """
        Add a task to the group.
        
        Args:
            task: The task to add
        """
        if task not in self.tasks:
            self.tasks.append(task)
    
    def remove_task(self, task_id: str):
        """
        Remove a task from the group by ID.
        
        Args:
            task_id: ID of the task to remove
        """
        self.tasks = [task for task in self.tasks if task.id != task_id]
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of the task to get
            
        Returns:
            The task if found, None otherwise
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def has_task(self, task_id: str) -> bool:
        """
        Check if the group contains a task with the given ID.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            True if the task is in the group, False otherwise
        """
        return any(task.id == task_id for task in self.tasks)
    
    async def execute_tasks(self, parallel: bool = False, continue_on_error: bool = False) -> List[Any]:
        """
        Execute all tasks in the group.
        
        Args:
            parallel: If True, execute tasks in parallel, otherwise sequentially
            continue_on_error: If True, continue executing tasks if some fail
            
        Returns:
            A list of results from all tasks
            
        Raises:
            Exception: If a task fails and continue_on_error is False
        """
        results = []
        results_dict = {}
        
        if parallel:
            # Execute tasks in parallel
            tasks = [task.run() for task in self.tasks]
            try:
                gathered_results = await asyncio.gather(*tasks, return_exceptions=continue_on_error)
                for task, result in zip(self.tasks, gathered_results):
                    if isinstance(result, Exception) and not continue_on_error:
                        raise result
                    results.append(result)
                    results_dict[task.id] = result
                    self.results[task.id] = result
            except Exception as e:
                if not continue_on_error:
                    raise e
        else:
            # Execute tasks sequentially
            for task in self.tasks:
                try:
                    result = await task.run()
                    results.append(result)
                    results_dict[task.id] = result
                    self.results[task.id] = result
                except Exception as e:
                    if not continue_on_error:
                        raise e
        
        # Filter out exceptions if continue_on_error is True
        if continue_on_error:
            results = [r for r in results if not isinstance(r, Exception)]
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task group to a dictionary representation.
        
        Returns:
            A dictionary representation of the task group
        """
        return {
            "id": self.id,
            "name": self.name,
            "tasks": [task.to_dict() for task in self.tasks],
            "results": self.results
        }
    
    def __str__(self) -> str:
        """Get string representation of the task group."""
        return f"TaskGroup({self.id}, {self.name}, tasks={len(self.tasks)})"


def create_task(
    func: Union[Callable, Coroutine],
    *args,
    **kwargs
) -> Task:
    """
    Create a task from a function or coroutine.
    
    This is a helper function to create Task instances from either
    coroutines or regular functions (which will be converted to coroutines).
    
    Args:
        func: Function or coroutine to execute
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments for task creation and function execution
    
    Returns:
        A Task instance
    
    Example:
        # Create a task from a coroutine function
        async def fetch_data(url):
            # ...
            return data
        
        task = create_task(fetch_data, "https://example.com",
                           id="fetch-example", priority=TaskPriority.HIGH)
    """
    # Extract task-specific kwargs
    task_kwargs = {}
    for key in ['id', 'name', 'priority', 'dependencies', 'timeout', 'metadata']:
        if key in kwargs:
            task_kwargs[key] = kwargs.pop(key)
    
    # Handle different types of callables
    if asyncio.iscoroutine(func):
        # Already a coroutine object
        coro = func
    elif inspect.iscoroutinefunction(func):
        # Coroutine function, call it with args
        coro = func(*args, **kwargs)
    else:
        # Regular function, wrap in coroutine
        async def wrapper():
            return func(*args, **kwargs)
        coro = wrapper()
    
    # Create the task
    task = Task(
        coro=coro,
        id=task_kwargs.get('id'),
        name=task_kwargs.get('name'),
        priority=task_kwargs.get('priority', TaskPriority.NORMAL),
        dependencies=task_kwargs.get('dependencies'),
        timeout=task_kwargs.get('timeout'),
        metadata=task_kwargs.get('metadata')
    )
    
    return task 