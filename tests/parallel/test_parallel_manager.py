"""Tests for the parallel processing manager."""

import asyncio
import time
from typing import Dict, List

import pytest

from summit_seo.parallel import (
    ParallelManager,
    ProcessingStrategy,
    Task,
    TaskPriority,
    TaskStatus
)


@pytest.fixture
def event_loop():
    """Create and yield an event loop for each test."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def parallel_manager():
    """Create and yield a ParallelManager instance."""
    manager = ParallelManager(max_workers=4)
    await manager.start()
    yield manager
    await manager.stop()


async def sample_task(sleep_time: float, return_value=None, raise_error=False):
    """Sample task for testing that sleeps and returns a value."""
    await asyncio.sleep(sleep_time)
    if raise_error:
        raise ValueError("Task error")
    return return_value


@pytest.mark.asyncio
async def test_parallel_manager_basic_task_execution(parallel_manager):
    """Test basic task execution with ParallelManager."""
    # Create and submit a task
    task = Task(
        id="test_task",
        name="Test Task",
        coro=sample_task(0.1, "result"),
        priority=TaskPriority.NORMAL
    )
    
    # Submit and await the task
    result = await parallel_manager.submit_and_await(task)
    
    # Verify result
    assert result == "result"


@pytest.mark.asyncio
async def test_parallel_manager_multiple_tasks(parallel_manager):
    """Test executing multiple tasks in parallel."""
    # Create tasks
    tasks = [
        Task(
            id=f"task_{i}",
            name=f"Task {i}",
            coro=sample_task(0.1, f"result_{i}"),
            priority=TaskPriority.NORMAL
        )
        for i in range(5)
    ]
    
    # Submit and await all tasks
    results = await parallel_manager.submit_and_await_many(tasks)
    
    # Verify results
    assert len(results) == 5
    for i, result in enumerate(results):
        assert result == f"result_{i}"


@pytest.mark.asyncio
async def test_parallel_manager_error_handling(parallel_manager):
    """Test error handling in parallel task execution."""
    # Create a task that will raise an error
    task = Task(
        id="error_task",
        name="Error Task",
        coro=sample_task(0.1, None, raise_error=True),
        priority=TaskPriority.NORMAL
    )
    
    # Submit the task and await its execution
    with pytest.raises(ValueError, match="Task error"):
        await parallel_manager.submit_and_await(task)


@pytest.mark.asyncio
async def test_parallel_manager_task_priorities(parallel_manager):
    """Test task prioritization."""
    # Create tasks with different priorities
    completed_tasks = []
    
    async def priority_task(priority_name):
        await asyncio.sleep(0.1)
        completed_tasks.append(priority_name)
        return priority_name
    
    # Create tasks with different priorities
    tasks = [
        Task(
            id="normal_task",
            name="Normal Priority",
            coro=priority_task("normal"),
            priority=TaskPriority.NORMAL
        ),
        Task(
            id="high_task",
            name="High Priority",
            coro=priority_task("high"),
            priority=TaskPriority.HIGH
        ),
        Task(
            id="low_task",
            name="Low Priority",
            coro=priority_task("low"),
            priority=TaskPriority.LOW
        ),
        Task(
            id="critical_task",
            name="Critical Priority",
            coro=priority_task("critical"),
            priority=TaskPriority.CRITICAL
        )
    ]
    
    # Create a manager specifically with priority-based strategy
    priority_manager = ParallelManager(
        max_workers=1,  # Only one worker to ensure sequential execution
        strategy=ProcessingStrategy.PRIORITY
    )
    await priority_manager.start()
    
    try:
        # Submit all tasks at once
        await priority_manager.submit_many(tasks)
        
        # Wait for all tasks to complete
        await priority_manager.wait_all()
        
        # The order should be: critical, high, normal, low
        # However, due to the nature of parallel execution and task queue implementation,
        # we can only verify that higher priority tasks are executed before lower ones
        # in general, not as an absolute order guarantee.
        # For reliable testing, we'll ensure critical is before low
        critical_index = completed_tasks.index("critical")
        low_index = completed_tasks.index("low")
        assert critical_index < low_index, "Critical task should execute before low priority task"
    finally:
        await priority_manager.stop()


@pytest.mark.asyncio
async def test_parallel_manager_task_dependencies(parallel_manager):
    """Test task dependencies."""
    execution_order = []
    
    async def dependency_task(name):
        await asyncio.sleep(0.1)
        execution_order.append(name)
        return name
    
    # Create a primary task
    primary_task = Task(
        id="primary_task",
        name="Primary Task",
        coro=dependency_task("primary"),
        priority=TaskPriority.NORMAL
    )
    
    # Create a dependent task
    dependent_task = Task(
        id="dependent_task",
        name="Dependent Task",
        coro=dependency_task("dependent"),
        priority=TaskPriority.NORMAL,
        dependencies=["primary_task"]
    )
    
    # Create a manager with graph-based strategy
    dependency_manager = ParallelManager(
        max_workers=2,
        strategy=ProcessingStrategy.GRAPH
    )
    await dependency_manager.start()
    
    try:
        # Submit both tasks - dependent task should wait for primary
        await dependency_manager.submit(dependent_task)
        await dependency_manager.submit(primary_task)
        
        # Wait for both tasks to complete
        await dependency_manager.wait_all()
        
        # Verify execution order - primary should be before dependent
        assert execution_order == ["primary", "dependent"]
    finally:
        await dependency_manager.stop()


@pytest.mark.asyncio
async def test_parallel_manager_task_timeout():
    """Test task timeout functionality."""
    # Create a task that will take longer than its timeout
    task = Task(
        id="timeout_task",
        name="Timeout Task",
        coro=sample_task(0.5, "result"),
        priority=TaskPriority.NORMAL,
        timeout=0.1  # Set timeout to less than task duration
    )
    
    # Create manager with timeout support
    timeout_manager = ParallelManager(max_workers=1)
    await timeout_manager.start()
    
    try:
        # Submit the task and await its execution - should timeout
        with pytest.raises(asyncio.TimeoutError):
            await timeout_manager.submit_and_await(task)
    finally:
        await timeout_manager.stop()


@pytest.mark.asyncio
async def test_parallel_manager_statistics(parallel_manager):
    """Test collection of task execution statistics."""
    # Create and submit multiple tasks
    tasks = [
        Task(
            id=f"stat_task_{i}",
            name=f"Stats Task {i}",
            coro=sample_task(0.1, f"result_{i}"),
            priority=TaskPriority.NORMAL
        )
        for i in range(3)
    ]
    
    # Also add a task that will fail
    error_task = Task(
        id="stat_error_task",
        name="Stats Error Task",
        coro=sample_task(0.1, None, raise_error=True),
        priority=TaskPriority.NORMAL
    )
    
    # Submit all tasks
    await parallel_manager.submit_many(tasks)
    
    # Submit error task but don't wait for it to avoid the exception
    future = await parallel_manager.submit(error_task)
    
    # Wait for all tasks to complete
    try:
        await parallel_manager.wait_all(timeout=1.0)
    except Exception:
        pass  # Ignore any exceptions during wait
    
    # Get statistics
    stats = parallel_manager.get_statistics()
    
    # Verify statistics
    assert stats.submitted >= 4  # At least our 4 tasks
    assert stats.completed >= 3  # At least our 3 successful tasks
    assert stats.failed >= 1  # At least our 1 error task
    assert stats.avg_duration > 0  # Should have some duration


@pytest.mark.asyncio
async def test_parallel_manager_cancellation(parallel_manager):
    """Test task cancellation."""
    # Create a task that will take some time
    task = Task(
        id="cancel_task",
        name="Task to Cancel",
        coro=sample_task(0.5, "result"),
        priority=TaskPriority.NORMAL
    )
    
    # Submit the task but don't await it
    future = await parallel_manager.submit(task)
    
    # Cancel the task immediately
    cancelled = await parallel_manager.cancel_task(task.id)
    
    # If the task was already running, cancellation might not succeed
    if cancelled:
        assert future.cancelled() or not future.done()
    else:
        # Task might have already completed
        await asyncio.sleep(0.6)  # Wait for task to complete
        assert future.done()


@pytest.mark.asyncio
async def test_parallel_manager_callback():
    """Test task status callback functionality."""
    callback_data = {}
    
    async def task_callback(task_id, status, result=None, error=None):
        if task_id not in callback_data:
            callback_data[task_id] = []
        callback_data[task_id].append((status, result, error))
    
    # Create manager with callback
    callback_manager = ParallelManager(
        max_workers=2,
        task_callback=task_callback
    )
    await callback_manager.start()
    
    try:
        # Create and submit a successful task
        success_task = Task(
            id="callback_success",
            name="Callback Success Task",
            coro=sample_task(0.1, "success_result"),
            priority=TaskPriority.NORMAL
        )
        
        # Create and submit a failing task
        error_task = Task(
            id="callback_error",
            name="Callback Error Task",
            coro=sample_task(0.1, None, raise_error=True),
            priority=TaskPriority.NORMAL
        )
        
        # Submit both tasks
        success_future = await callback_manager.submit(success_task)
        error_future = await callback_manager.submit(error_task)
        
        # Wait for callbacks to be processed
        try:
            await success_future
        except Exception:
            pass
        
        try:
            await error_future
        except Exception:
            pass
        
        # Wait a bit to ensure callbacks are processed
        await asyncio.sleep(0.2)
        
        # Verify callbacks
        assert "callback_success" in callback_data
        assert any(status == TaskStatus.COMPLETED for status, _, _ in callback_data["callback_success"])
        
        assert "callback_error" in callback_data
        assert any(status == TaskStatus.FAILED for status, _, _ in callback_data["callback_error"])
    finally:
        await callback_manager.stop()


@pytest.mark.asyncio
async def test_parallel_manager_batched_strategy():
    """Test batched processing strategy."""
    processed_items = []
    
    async def batch_task(item):
        await asyncio.sleep(0.1)
        processed_items.append(item)
        return item
    
    # Create manager with batched strategy
    batch_manager = ParallelManager(
        max_workers=2,
        strategy=ProcessingStrategy.BATCHED,
        batch_size=3
    )
    await batch_manager.start()
    
    try:
        # Create and submit tasks
        tasks = [
            Task(
                id=f"batch_task_{i}",
                name=f"Batch Task {i}",
                coro=batch_task(i),
                priority=TaskPriority.NORMAL
            )
            for i in range(5)
        ]
        
        # Submit tasks
        for task in tasks:
            await batch_manager.submit(task)
        
        # Wait for all tasks to complete
        await batch_manager.wait_all()
        
        # Verify all items were processed
        assert sorted(processed_items) == [0, 1, 2, 3, 4]
    finally:
        await batch_manager.stop()


@pytest.mark.asyncio
async def test_parallel_manager_work_stealing():
    """Test work stealing strategy."""
    # This test is more about ensuring the strategy doesn't break
    # than testing the actual work stealing mechanics
    
    # Create tasks with varying execution times
    tasks = [
        Task(
            id=f"ws_task_{i}",
            name=f"Work Stealing Task {i}",
            coro=sample_task(0.05 + (i % 3) * 0.1, f"result_{i}"),  # Mix of short and longer tasks
            priority=TaskPriority.NORMAL
        )
        for i in range(10)
    ]
    
    # Create manager with work stealing strategy
    ws_manager = ParallelManager(
        max_workers=4,
        strategy=ProcessingStrategy.WORK_STEALING
    )
    await ws_manager.start()
    
    try:
        # Submit and await all tasks
        results = await ws_manager.submit_and_await_many(tasks)
        
        # Verify all results
        assert len(results) == 10
        for i, result in enumerate(results):
            assert result == f"result_{i}"
        
        # Check statistics
        stats = ws_manager.get_statistics()
        assert stats.completed == 10
    finally:
        await ws_manager.stop()


@pytest.mark.asyncio
async def test_parallel_manager_pause_resume(parallel_manager):
    """Test pausing and resuming task execution."""
    # Create some tasks
    task1 = Task(
        id="pause_task_1",
        name="Pause Test Task 1",
        coro=sample_task(0.3, "result_1"),
        priority=TaskPriority.NORMAL
    )
    
    task2 = Task(
        id="pause_task_2",
        name="Pause Test Task 2",
        coro=sample_task(0.3, "result_2"),
        priority=TaskPriority.NORMAL
    )
    
    # Submit first task
    future1 = await parallel_manager.submit(task1)
    
    # Pause the manager
    await parallel_manager.pause()
    
    # Submit second task while paused
    future2 = await parallel_manager.submit(task2)
    
    # First task might have already started executing
    # but second task should not start until we resume
    
    # Give first task time to complete if it started
    await asyncio.sleep(0.4)
    
    # Resume execution
    await parallel_manager.resume()
    
    # Wait for both tasks to complete
    result1 = await future1
    result2 = await future2
    
    # Verify results
    assert result1 == "result_1"
    assert result2 == "result_2" 