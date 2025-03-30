"""Tests for the ParallelExecutor class."""

import asyncio
import pytest
import time
from unittest.mock import MagicMock, patch

from summit_seo.parallel.executor import (
    ExecutionStrategy, ParallelExecutor, WorkerType
)
from summit_seo.parallel.task import Task, TaskPriority, TaskStatus


@pytest.fixture
def event_loop():
    """Create an event loop for each test."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
async def parallel_executor():
    """Create a ParallelExecutor for testing."""
    executor = ParallelExecutor(
        max_workers=2,
        execution_strategy=ExecutionStrategy.FIFO,
        worker_type=WorkerType.ASYNCIO
    )
    await executor.start()
    yield executor
    await executor.stop()


async def sample_task(sleep_time: float, return_value=None, raise_error=False):
    """Sample task function for testing."""
    await asyncio.sleep(sleep_time)
    if raise_error:
        raise ValueError("Task error")
    return return_value


class TestParallelExecutor:
    """Tests for the ParallelExecutor class."""
    
    @pytest.mark.asyncio
    async def test_init(self):
        """Test initialization of ParallelExecutor."""
        executor = ParallelExecutor(
            max_workers=4,
            execution_strategy=ExecutionStrategy.PRIORITY,
            worker_type=WorkerType.ASYNCIO
        )
        
        assert executor.max_workers == 4
        assert executor.execution_strategy == ExecutionStrategy.PRIORITY
        assert executor.worker_type == WorkerType.ASYNCIO
        assert not executor.running
        
    @pytest.mark.asyncio
    async def test_start_stop(self):
        """Test starting and stopping the executor."""
        executor = ParallelExecutor(max_workers=2)
        
        # Start executor
        await executor.start()
        assert executor.running
        assert len(executor.workers) == 2
        
        # Stop executor
        await executor.stop()
        assert not executor.running
        assert len(executor.workers) == 0
        
    @pytest.mark.asyncio
    async def test_submit_task(self, parallel_executor):
        """Test submitting a task."""
        # Create a task
        task = Task(
            id="test_task",
            coro=sample_task(0.1, "result"),
            name="Test Task"
        )
        
        # Submit task
        future = await parallel_executor.submit(task)
        assert not future.done()
        
        # Wait for task to complete
        result = await future
        assert result == "result"
        
    @pytest.mark.asyncio
    async def test_submit_all(self, parallel_executor):
        """Test submitting multiple tasks."""
        # Create tasks
        tasks = [
            Task(id=f"task_{i}", coro=sample_task(0.1, i), name=f"Task {i}")
            for i in range(5)
        ]
        
        # Submit all tasks
        futures = await parallel_executor.submit_all(tasks)
        assert len(futures) == 5
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*futures)
        assert results == [0, 1, 2, 3, 4]
        
    @pytest.mark.asyncio
    async def test_task_error(self, parallel_executor):
        """Test handling of task errors."""
        # Create a task that raises an error
        task = Task(
            id="error_task",
            coro=sample_task(0.1, raise_error=True),
            name="Error Task"
        )
        
        # Submit task
        future = await parallel_executor.submit(task)
        
        # Wait for task to complete
        with pytest.raises(ValueError, match="Task error"):
            await future
            
    @pytest.mark.asyncio
    async def test_priority_execution(self):
        """Test priority-based execution strategy."""
        results = []
        
        async def priority_task(priority_value):
            results.append(priority_value)
            return priority_value
        
        # Create executor with priority strategy
        executor = ParallelExecutor(
            max_workers=1,
            execution_strategy=ExecutionStrategy.PRIORITY
        )
        
        await executor.start()
        
        try:
            # Create tasks with different priorities
            tasks = [
                Task(
                    id="low",
                    coro=priority_task("low"),
                    name="Low Priority Task",
                    priority=TaskPriority.LOW
                ),
                Task(
                    id="medium",
                    coro=priority_task("medium"),
                    name="Medium Priority Task",
                    priority=TaskPriority.NORMAL
                ),
                Task(
                    id="high",
                    coro=priority_task("high"),
                    name="High Priority Task",
                    priority=TaskPriority.HIGH
                ),
                Task(
                    id="critical",
                    coro=priority_task("critical"),
                    name="Critical Priority Task",
                    priority=TaskPriority.CRITICAL
                )
            ]
            
            # Submit all tasks
            futures = await executor.submit_all(tasks)
            
            # Wait for all tasks to complete
            await asyncio.gather(*futures)
            
            # The order should be: critical, high, medium, low
            # But due to the asynchronous execution, we can only guarantee
            # that critical is executed before low
            assert results.index("critical") < results.index("low")
            
        finally:
            await executor.stop()
            
    @pytest.mark.asyncio
    async def test_dependency_execution(self):
        """Test dependency-based execution strategy."""
        results = []
        
        async def dependency_task(name):
            results.append(name)
            return name
        
        # Create executor with dependency strategy
        executor = ParallelExecutor(
            max_workers=2,
            execution_strategy=ExecutionStrategy.DEPENDENCY
        )
        
        await executor.start()
        
        try:
            # Create tasks with dependencies
            task_a = Task(
                id="task_a",
                coro=dependency_task("a"),
                name="Task A"
            )
            
            task_b = Task(
                id="task_b",
                coro=dependency_task("b"),
                name="Task B",
                dependencies=["task_a"]
            )
            
            task_c = Task(
                id="task_c",
                coro=dependency_task("c"),
                name="Task C",
                dependencies=["task_b"]
            )
            
            task_d = Task(
                id="task_d",
                coro=dependency_task("d"),
                name="Task D",
                dependencies=["task_a"]
            )
            
            # Submit all tasks
            futures = await executor.submit_all([task_c, task_d, task_b, task_a])
            
            # Wait for all tasks to complete
            await asyncio.gather(*futures)
            
            # Check dependencies were respected
            assert results.index("a") < results.index("b")
            assert results.index("b") < results.index("c")
            assert results.index("a") < results.index("d")
            
        finally:
            await executor.stop()
            
    @pytest.mark.asyncio
    async def test_cancel_task(self, parallel_executor):
        """Test cancelling a task."""
        # Create a task
        task = Task(
            id="long_task",
            coro=sample_task(1.0, "result"),
            name="Long Task"
        )
        
        # Submit task
        future = await parallel_executor.submit(task)
        
        # Cancel task
        cancelled = await parallel_executor.cancel_task("long_task")
        assert cancelled
        
        # Check task was cancelled
        with pytest.raises(asyncio.CancelledError):
            await future
            
    @pytest.mark.asyncio
    async def test_statistics(self, parallel_executor):
        """Test getting statistics."""
        # Create some tasks
        tasks = [
            Task(id=f"task_{i}", coro=sample_task(0.1, i), name=f"Task {i}")
            for i in range(3)
        ]
        
        # Submit all tasks
        futures = await parallel_executor.submit_all(tasks)
        
        # Wait for all tasks to complete
        await asyncio.gather(*futures)
        
        # Get statistics
        stats = parallel_executor.get_statistics()
        
        # Check statistics
        assert stats["submitted"] == 3
        assert stats["completed"] == 3
        assert stats["failed"] == 0
        assert stats["cancelled"] == 0
        
    @pytest.mark.asyncio
    async def test_wait_for_tasks(self, parallel_executor):
        """Test waiting for specific tasks."""
        # Create tasks
        tasks = [
            Task(id=f"task_{i}", coro=sample_task(0.1 * i, i), name=f"Task {i}")
            for i in range(3)
        ]
        
        # Submit all tasks
        futures = await parallel_executor.submit_all(tasks)
        
        # Wait for specific tasks
        result = await parallel_executor.wait_for_tasks(["task_0", "task_1"])
        
        # Check results
        assert "task_0" in result
        assert "task_1" in result
        assert result["task_0"] == 0
        assert result["task_1"] == 1
        
    @pytest.mark.asyncio
    async def test_wait_all(self, parallel_executor):
        """Test waiting for all tasks."""
        # Create tasks
        tasks = [
            Task(id=f"task_{i}", coro=sample_task(0.1, i), name=f"Task {i}")
            for i in range(3)
        ]
        
        # Submit all tasks
        futures = await parallel_executor.submit_all(tasks)
        
        # Wait for all tasks
        completed = await parallel_executor.wait_all()
        assert completed
        
        # Check all futures are done
        for future in futures:
            assert future.done()
            
    @pytest.mark.asyncio
    async def test_timeout(self):
        """Test task timeout."""
        # Create executor with timeout
        executor = ParallelExecutor(
            max_workers=1,
            task_timeout=0.2
        )
        
        await executor.start()
        
        try:
            # Create a task that takes longer than the timeout
            task = Task(
                id="timeout_task",
                coro=sample_task(0.5, "result"),
                name="Timeout Task"
            )
            
            # Submit task
            future = await executor.submit(task)
            
            # Wait for task to complete or timeout
            with pytest.raises(asyncio.TimeoutError):
                await future
                
        finally:
            await executor.stop()
            
    @pytest.mark.asyncio
    async def test_get_task_lists(self, parallel_executor):
        """Test getting task list methods."""
        # Create tasks with different durations
        fast_task = Task(
            id="fast_task",
            coro=sample_task(0.1, "fast"),
            name="Fast Task"
        )
        
        slow_task = Task(
            id="slow_task",
            coro=sample_task(0.3, "slow"),
            name="Slow Task"
        )
        
        # Submit tasks
        await parallel_executor.submit(fast_task)
        await parallel_executor.submit(slow_task)
        
        # Wait a bit for fast task to complete but slow task still running
        await asyncio.sleep(0.2)
        
        # Get task lists
        pending_tasks = await parallel_executor.get_pending_task_ids()
        running_tasks = await parallel_executor.get_running_task_ids()
        completed_tasks = await parallel_executor.get_completed_task_ids()
        
        # The exact state depends on timing, but we can make some assertions
        if "slow_task" in running_tasks:
            assert "fast_task" in completed_tasks
        
        # Wait for all tasks to complete
        await parallel_executor.wait_all()
        
        # Check all tasks are completed
        completed_tasks = await parallel_executor.get_completed_task_ids()
        assert "fast_task" in completed_tasks
        assert "slow_task" in completed_tasks 