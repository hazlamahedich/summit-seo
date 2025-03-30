"""Tests for Task and TaskGroup classes."""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from summit_seo.parallel.task import (
    Task, TaskGroup, TaskPriority, TaskResult, TaskStatus, create_task
)


@pytest.fixture
def event_loop():
    """Create an event loop for each test."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


async def sample_coro(value=None, raise_error=False):
    """Sample coroutine for testing."""
    await asyncio.sleep(0.01)
    if raise_error:
        raise ValueError("Test error")
    return value


def sample_func(value=None, raise_error=False):
    """Sample function for testing."""
    if raise_error:
        raise ValueError("Test error")
    return value


class TestTask:
    """Tests for the Task class."""
    
    def test_init(self):
        """Test task initialization."""
        # Create a task with a coroutine
        task = Task(
            id="test_task",
            coro=sample_coro("result"),
            name="Test Task",
            priority=TaskPriority.HIGH,
            dependencies=["dep1", "dep2"],
            timeout=10.0
        )
        
        assert task.id == "test_task"
        assert task.name == "Test Task"
        assert task.priority == TaskPriority.HIGH
        assert task.dependencies == ["dep1", "dep2"]
        assert task.timeout == 10.0
        assert task.status == TaskStatus.PENDING
        assert task.result is None
        assert task.error is None
        assert task.start_time is None
        assert task.end_time is None
        
    def test_equality(self):
        """Test task equality."""
        task1 = Task(id="task1", coro=sample_coro("result"))
        task2 = Task(id="task1", coro=sample_coro("different"))
        task3 = Task(id="task3", coro=sample_coro("result"))
        
        # Equality should be based on ID
        assert task1 == task2
        assert task1 != task3
        
    def test_repr(self):
        """Test task representation."""
        task = Task(id="test_task", coro=sample_coro("result"), name="Test Task")
        
        # Representation should include ID, name, and status
        repr_str = repr(task)
        assert "test_task" in repr_str
        assert "Test Task" in repr_str
        assert "PENDING" in repr_str
        
    @pytest.mark.asyncio
    async def test_run(self):
        """Test running a task."""
        task = Task(id="test_task", coro=sample_coro("result"), name="Test Task")
        
        # Run task
        result = await task.run()
        
        # Check task state
        assert result == "result"
        assert task.status == TaskStatus.COMPLETED
        assert task.result == "result"
        assert task.error is None
        assert task.start_time is not None
        assert task.end_time is not None
        assert task.duration > 0
        
    @pytest.mark.asyncio
    async def test_run_error(self):
        """Test running a task that raises an error."""
        task = Task(id="error_task", coro=sample_coro(raise_error=True), name="Error Task")
        
        # Run task
        with pytest.raises(ValueError, match="Test error"):
            await task.run()
        
        # Check task state
        assert task.status == TaskStatus.FAILED
        assert task.result is None
        assert isinstance(task.error, ValueError)
        assert str(task.error) == "Test error"
        assert task.start_time is not None
        assert task.end_time is not None
        assert task.duration > 0
        
    @pytest.mark.asyncio
    async def test_timeout(self):
        """Test task timeout."""
        async def slow_coro():
            await asyncio.sleep(0.2)
            return "result"
        
        # Create a task with a short timeout
        task = Task(id="timeout_task", coro=slow_coro(), name="Timeout Task", timeout=0.1)
        
        # Run task with timeout
        with pytest.raises(asyncio.TimeoutError):
            await task.run()
        
        # Check task state
        assert task.status == TaskStatus.FAILED
        assert task.result is None
        assert isinstance(task.error, asyncio.TimeoutError)
        assert task.start_time is not None
        assert task.end_time is not None
        assert task.duration > 0
        
    @pytest.mark.asyncio
    async def test_cancel(self):
        """Test cancelling a task."""
        cancel_event = asyncio.Event()
        
        async def cancellable_coro():
            try:
                while not cancel_event.is_set():
                    await asyncio.sleep(0.1)
                return "completed"
            except asyncio.CancelledError:
                return "cancelled"
        
        # Create a task
        task = Task(id="cancel_task", coro=cancellable_coro(), name="Cancel Task")
        
        # Start task but don't await it
        run_task = asyncio.create_task(task.run())
        
        # Give it time to start
        await asyncio.sleep(0.2)
        assert task.status == TaskStatus.RUNNING
        
        # Cancel the task
        cancelled = task.cancel()
        assert cancelled
        assert task.status == TaskStatus.CANCELLED
        
        # Set the event to allow the coroutine to complete
        cancel_event.set()
        
        # Make sure we can cancel the task
        run_task.cancel()
        
        try:
            await run_task
        except asyncio.CancelledError:
            pass  # This is fine, but we don't require it
        
    def test_to_dict(self):
        """Test converting task to dictionary."""
        # Create task with initial state
        task = Task(id="test_task", coro=sample_coro("result"), name="Test Task")
        
        # Get dictionary representation
        task_dict = task.to_dict()
        
        # Check dictionary contents
        assert task_dict["id"] == "test_task"
        assert task_dict["name"] == "Test Task"
        assert task_dict["status"] == "PENDING"
        assert "priority" in task_dict
        assert "dependencies" in task_dict
        assert "created_at" in task_dict
        
        # Update task state
        task.status = TaskStatus.COMPLETED
        task.result = "result"
        task.start_time = datetime.now() - timedelta(seconds=1)
        task.end_time = datetime.now()
        
        # Get updated dictionary
        updated_dict = task.to_dict()
        
        # Check updated dictionary
        assert updated_dict["status"] == "COMPLETED"
        assert updated_dict["result"] == "result"
        assert "start_time" in updated_dict
        assert "end_time" in updated_dict
        assert "duration" in updated_dict


class TestTaskGroup:
    """Tests for the TaskGroup class."""
    
    def test_init(self):
        """Test task group initialization."""
        # Create a task group
        group = TaskGroup(
            id="test_group",
            name="Test Group",
            tasks=[
                Task(id="task1", coro=sample_coro(1), name="Task 1"),
                Task(id="task2", coro=sample_coro(2), name="Task 2")
            ]
        )
        
        assert group.id == "test_group"
        assert group.name == "Test Group"
        assert len(group.tasks) == 2
        assert [task.id for task in group.tasks] == ["task1", "task2"]
        
    def test_add_task(self):
        """Test adding a task to a group."""
        # Create an empty group
        group = TaskGroup(id="test_group", name="Test Group")
        assert len(group.tasks) == 0
        
        # Add tasks
        task1 = Task(id="task1", coro=sample_coro(1), name="Task 1")
        task2 = Task(id="task2", coro=sample_coro(2), name="Task 2")
        
        group.add_task(task1)
        group.add_task(task2)
        
        assert len(group.tasks) == 2
        assert task1 in group.tasks
        assert task2 in group.tasks
        
    def test_remove_task(self):
        """Test removing a task from a group."""
        # Create a group with tasks
        task1 = Task(id="task1", coro=sample_coro(1), name="Task 1")
        task2 = Task(id="task2", coro=sample_coro(2), name="Task 2")
        
        group = TaskGroup(
            id="test_group",
            name="Test Group",
            tasks=[task1, task2]
        )
        
        # Remove a task
        group.remove_task("task1")
        
        assert len(group.tasks) == 1
        assert task1 not in group.tasks
        assert task2 in group.tasks
        
        # Remove non-existent task
        group.remove_task("task3")  # Should not raise error
        assert len(group.tasks) == 1
        
    def test_get_task(self):
        """Test getting a task from a group."""
        # Create a group with tasks
        task1 = Task(id="task1", coro=sample_coro(1), name="Task 1")
        task2 = Task(id="task2", coro=sample_coro(2), name="Task 2")
        
        group = TaskGroup(
            id="test_group",
            name="Test Group",
            tasks=[task1, task2]
        )
        
        # Get tasks
        assert group.get_task("task1") == task1
        assert group.get_task("task2") == task2
        assert group.get_task("task3") is None
        
    def test_has_task(self):
        """Test checking if a group has a task."""
        # Create a group with tasks
        group = TaskGroup(
            id="test_group",
            name="Test Group",
            tasks=[
                Task(id="task1", coro=sample_coro(1), name="Task 1"),
                Task(id="task2", coro=sample_coro(2), name="Task 2")
            ]
        )
        
        # Check task presence
        assert group.has_task("task1")
        assert group.has_task("task2")
        assert not group.has_task("task3")
        
    @pytest.mark.asyncio
    async def test_execute_tasks(self):
        """Test executing all tasks in a group."""
        # Create a group with tasks
        group = TaskGroup(
            id="test_group",
            name="Test Group",
            tasks=[
                Task(id="task1", coro=sample_coro(1), name="Task 1"),
                Task(id="task2", coro=sample_coro(2), name="Task 2")
            ]
        )
        
        # Execute all tasks
        results = await group.execute_tasks()
        
        # Check results
        assert len(results) == 2
        assert 1 in results
        assert 2 in results
        
        # All tasks should be completed
        for task in group.tasks:
            assert task.status == TaskStatus.COMPLETED
            
    @pytest.mark.asyncio
    async def test_execute_tasks_parallel(self):
        """Test executing tasks in parallel."""
        execution_order = []
        
        async def tracked_coro(name, delay):
            await asyncio.sleep(delay)
            execution_order.append(name)
            return name
        
        # Create a group with tasks of different durations
        group = TaskGroup(
            id="test_group",
            name="Test Group",
            tasks=[
                Task(id="task1", coro=tracked_coro("task1", 0.2), name="Task 1"),
                Task(id="task2", coro=tracked_coro("task2", 0.1), name="Task 2")
            ]
        )
        
        # Execute tasks in parallel
        results = await group.execute_tasks(parallel=True)
        
        # Check results
        assert len(results) == 2
        assert "task1" in results
        assert "task2" in results
        
        # Task2 should have finished before Task1 due to shorter delay
        assert execution_order == ["task2", "task1"]
        
    @pytest.mark.asyncio
    async def test_execute_tasks_with_error(self):
        """Test executing tasks where one fails."""
        # Create a group with one failing task
        group = TaskGroup(
            id="test_group",
            name="Test Group",
            tasks=[
                Task(id="task1", coro=sample_coro(1), name="Task 1"),
                Task(id="task2", coro=sample_coro(raise_error=True), name="Task 2")
            ]
        )
        
        # Execute tasks
        with pytest.raises(ValueError, match="Test error"):
            await group.execute_tasks()
            
        # First task should have completed, second failed
        assert group.tasks[0].status == TaskStatus.COMPLETED
        assert group.tasks[1].status == TaskStatus.FAILED
        
    @pytest.mark.asyncio
    async def test_execute_tasks_continue_on_error(self):
        """Test executing tasks with continue_on_error."""
        # Create a group with one failing task
        group = TaskGroup(
            id="test_group",
            name="Test Group",
            tasks=[
                Task(id="task1", coro=sample_coro(1), name="Task 1"),
                Task(id="task2", coro=sample_coro(raise_error=True), name="Task 2"),
                Task(id="task3", coro=sample_coro(3), name="Task 3")
            ]
        )
        
        # Execute tasks with continue_on_error
        results = await group.execute_tasks(continue_on_error=True)
        
        # Should have results for successful tasks
        assert len(results) == 2
        assert 1 in results
        assert 3 in results
        
        # All tasks should have appropriate status
        assert group.tasks[0].status == TaskStatus.COMPLETED
        assert group.tasks[1].status == TaskStatus.FAILED
        assert group.tasks[2].status == TaskStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_create_task_from_coroutine(self):
        """Test creating a task from a coroutine function."""
        task = create_task(
            sample_coro, "value",
            id="test_coro_task",
            name="Test Coro Task",
            priority=TaskPriority.HIGH
        )
        
        assert isinstance(task, Task)
        assert task.id == "test_coro_task"
        assert task.name == "Test Coro Task"
        assert task.priority == TaskPriority.HIGH
        
        # Run the task
        result = await task.run()
        assert result == "value"
        
    @pytest.mark.asyncio
    async def test_create_task_from_function(self):
        """Test creating a task from a regular function."""
        task = create_task(
            sample_func, "value",
            id="test_func_task",
            name="Test Func Task"
        )
        
        assert isinstance(task, Task)
        assert task.id == "test_func_task"
        assert task.name == "Test Func Task"
        
        # Run the task
        result = await task.run()
        assert result == "value" 