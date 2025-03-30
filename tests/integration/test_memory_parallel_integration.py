"""Integration tests for memory optimization and parallel processing."""

import asyncio
import pytest
import time
from unittest.mock import MagicMock, patch

from summit_seo.memory import (
    MemoryLimiter, MemoryMonitor, MemoryOptimizer, 
    MemoryUnit, OptimizationConfig, OptimizationLevel
)
from summit_seo.parallel import (
    ParallelManager, ProcessingStrategy, Task, TaskPriority, TaskStatus
)


@pytest.fixture
def event_loop():
    """Create a new event loop for each test."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
async def memory_monitor():
    """Create a memory monitor for testing."""
    monitor = MemoryMonitor(poll_interval=0.1)
    monitor.start_monitoring()
    yield monitor
    monitor.stop_monitoring()


@pytest.fixture
async def memory_limiter(memory_monitor):
    """Create a memory limiter for testing."""
    limiter = MemoryLimiter(monitor=memory_monitor, poll_interval=0.1)
    limiter.add_threshold(
        limit=90,
        action="throttle",
        limit_unit=MemoryUnit.PERCENT,
        description="Throttle at 90% memory usage"
    )
    limiter.add_threshold(
        limit=95,
        action="gc",
        limit_unit=MemoryUnit.PERCENT,
        description="Run GC at 95% memory usage"
    )
    limiter.start()
    yield limiter
    limiter.stop()


@pytest.fixture
async def memory_optimizer(memory_monitor, memory_limiter):
    """Create a memory optimizer for testing."""
    optimizer = MemoryOptimizer(
        config=OptimizationConfig(level=OptimizationLevel.MODERATE),
        monitor=memory_monitor,
        limiter=memory_limiter
    )
    return optimizer


@pytest.fixture
async def parallel_manager():
    """Create a parallel manager for testing."""
    manager = ParallelManager(
        max_workers=4,
        strategy=ProcessingStrategy.PRIORITY_GRAPH
    )
    await manager.start()
    yield manager
    await manager.stop()


async def resource_intensive_task(task_id, memory_size_mb=10, duration=0.1):
    """A resource-intensive task that allocates memory and takes time to execute."""
    # Allocate memory (approximately memory_size_mb)
    data = [0] * (memory_size_mb * 1024 * 1024 // 8)  # Integers are 8 bytes each
    
    # Do some work
    await asyncio.sleep(duration)
    
    # Return a result
    return {
        "task_id": task_id,
        "memory_size_mb": memory_size_mb,
        "duration": duration,
        "data_length": len(data)
    }


@pytest.mark.asyncio
async def test_memory_aware_parallel_processing(memory_optimizer, parallel_manager, memory_monitor):
    """Test parallel processing with memory optimization."""
    # Create a list of tasks with different memory requirements
    tasks = [
        Task(
            id=f"task_{i}",
            coro=resource_intensive_task(f"task_{i}", memory_size_mb=5, duration=0.1),
            name=f"Task {i}",
            priority=TaskPriority.NORMAL
        )
        for i in range(10)
    ]
    
    # Monitor the operation
    with memory_optimizer.monitor_operation("parallel_processing_test") as op:
        # Execute tasks in parallel
        results = await parallel_manager.submit_and_await_many(tasks)
        
        # Check that all tasks completed
        assert len(results) == 10
        for result in results:
            assert "task_id" in result
            assert "memory_size_mb" in result
            assert "duration" in result
    
    # Get memory usage summary
    usage_summary = op.get_usage_summary()
    
    # Verify the operation was tracked
    assert usage_summary["operation"] == "parallel_processing_test"
    assert "start" in usage_summary
    assert "end" in usage_summary
    assert "duration" in usage_summary
    assert "peak_memory" in usage_summary


@pytest.mark.asyncio
async def test_throttling_with_high_memory_usage(memory_optimizer, parallel_manager, memory_limiter):
    """Test that processing gets throttled when memory usage is high."""
    # Mock high memory usage
    with patch.object(memory_limiter, 'should_throttle', return_value=True):
        with patch.object(memory_limiter, 'get_throttle_factor', return_value=0.5):
            start_time = time.time()
            
            # Run a task that should be throttled
            task = Task(
                id="throttled_task",
                coro=resource_intensive_task("throttled_task", memory_size_mb=1, duration=0.1),
                name="Throttled Task"
            )
            
            # Execute with throttling
            result = await parallel_manager.submit_and_await(task)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Task should take longer due to throttling
            assert duration > 0.1
            
            # But the result should still be correct
            assert result["task_id"] == "throttled_task"


@pytest.mark.asyncio
async def test_memory_optimization_during_processing(memory_optimizer, parallel_manager):
    """Test memory optimization during parallel processing."""
    # Create a class to optimize
    class TestData:
        def __init__(self, id, values):
            self.id = id
            self.values = values
            self.extra_data = {}
    
    # Optimize the class
    OptimizedTestData = memory_optimizer.optimize_class(
        TestData,
        strategies=["slots", "pooling"]
    )
    
    # Task that creates and uses optimized objects
    async def optimized_object_task(task_id, count):
        # Create objects
        objects = [
            OptimizedTestData(f"{task_id}_{i}", list(range(100)))
            for i in range(count)
        ]
        
        # Do some work
        await asyncio.sleep(0.1)
        
        # Return a result
        return {
            "task_id": task_id,
            "object_count": len(objects),
            "has_slots": hasattr(objects[0], "__slots__")
        }
    
    # Create tasks
    tasks = [
        Task(
            id=f"opt_task_{i}",
            coro=optimized_object_task(f"opt_task_{i}", 100),
            name=f"Optimized Task {i}"
        )
        for i in range(5)
    ]
    
    # Execute tasks
    results = await parallel_manager.submit_and_await_many(tasks)
    
    # Check results
    assert len(results) == 5
    for result in results:
        assert result["object_count"] == 100
        assert result["has_slots"] is True


@pytest.mark.asyncio
async def test_dependency_based_processing(memory_optimizer, parallel_manager):
    """Test dependency-based task processing with memory optimization."""
    execution_order = []
    
    async def tracked_task(name, dependencies=None, memory_size_mb=1):
        # Allocate some memory
        data = [0] * (memory_size_mb * 1024 * 1024 // 8)
        
        # Record execution order
        execution_order.append(name)
        
        # Do some work
        await asyncio.sleep(0.1)
        
        # Apply memory optimization to free up memory
        if memory_size_mb > 5:
            memory_optimizer.optimize_memory_usage()
        
        return {
            "name": name,
            "dependencies": dependencies or [],
            "memory_allocated": memory_size_mb
        }
    
    # Create tasks with dependencies
    task_a = Task(
        id="task_a",
        coro=tracked_task("task_a", memory_size_mb=5),
        name="Task A"
    )
    
    task_b = Task(
        id="task_b",
        coro=tracked_task("task_b", ["task_a"], memory_size_mb=5),
        name="Task B",
        dependencies=["task_a"]
    )
    
    task_c = Task(
        id="task_c",
        coro=tracked_task("task_c", ["task_b"], memory_size_mb=10),
        name="Task C",
        dependencies=["task_b"]
    )
    
    task_d = Task(
        id="task_d",
        coro=tracked_task("task_d", ["task_a"], memory_size_mb=5),
        name="Task D",
        dependencies=["task_a"]
    )
    
    # Submit tasks in reverse order to test dependency resolution
    results = await parallel_manager.submit_and_await_many([task_c, task_d, task_b, task_a])
    
    # Check that all tasks completed
    assert len(results) == 4
    
    # Check that dependencies were respected in execution order
    assert execution_order.index("task_a") < execution_order.index("task_b")
    assert execution_order.index("task_b") < execution_order.index("task_c")
    assert execution_order.index("task_a") < execution_order.index("task_d")


@pytest.mark.asyncio
async def test_streaming_processing_with_memory_limits(memory_optimizer, parallel_manager):
    """Test processing a stream of tasks with memory limits."""
    from summit_seo.memory import StreamingOptimizer
    
    # Create a streaming optimizer
    streaming_optimizer = StreamingOptimizer(chunk_size=5)
    
    # Generate a lot of tasks
    async def generate_tasks(count):
        for i in range(count):
            yield Task(
                id=f"stream_task_{i}",
                coro=resource_intensive_task(f"stream_task_{i}", memory_size_mb=2, duration=0.05),
                name=f"Stream Task {i}"
            )
    
    # Process tasks in batches
    total_completed = 0
    async for batch in streaming_optimizer.process_generator(generate_tasks(30)):
        # Submit batch
        batch_results = await parallel_manager.submit_and_await_many(batch)
        total_completed += len(batch_results)
        
        # Apply memory optimization after each batch
        memory_optimizer.optimize_memory_usage()
    
    # Verify all tasks were processed
    assert total_completed == 30 