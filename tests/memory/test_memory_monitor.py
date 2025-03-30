"""Tests for the memory monitor implementation."""

import asyncio
import gc
import pytest
import time
from unittest.mock import MagicMock, patch

from summit_seo.memory.monitor import MemoryLimitExceededError, MemoryMonitor, MemoryUnit, ResourceUsageStats


@pytest.fixture
def memory_monitor():
    """Create a memory monitor for testing."""
    monitor = MemoryMonitor(poll_interval=0.01)
    yield monitor
    # Cleanup
    if monitor._monitoring_thread and monitor._monitoring_thread.is_alive():
        monitor.stop_monitoring()


class TestMemoryMonitor:
    """Tests for the MemoryMonitor class."""
    
    def test_init(self):
        """Test initialization of memory monitor."""
        monitor = MemoryMonitor(poll_interval=0.5)
        
        assert monitor.poll_interval == 0.5
        assert monitor._monitoring_thread is None
        assert not monitor._stop_event.is_set()
        assert not monitor._monitoring_active
        assert len(monitor._usage_history) == 0
        
    def test_start_stop_monitoring(self, memory_monitor):
        """Test starting and stopping monitoring."""
        # Should start inactive
        assert not memory_monitor._monitoring_active
        
        # Start monitoring
        memory_monitor.start_monitoring()
        assert memory_monitor._monitoring_active
        assert memory_monitor._monitoring_thread is not None
        assert memory_monitor._monitoring_thread.is_alive()
        
        # Stop monitoring
        memory_monitor.stop_monitoring()
        assert not memory_monitor._monitoring_active
        assert memory_monitor._stop_event.is_set()
        
        # Wait for thread to exit
        if memory_monitor._monitoring_thread:
            memory_monitor._monitoring_thread.join(timeout=1.0)
        assert not memory_monitor._monitoring_thread.is_alive()
        
    def test_get_current_usage(self, memory_monitor):
        """Test getting current memory usage."""
        # Get current usage
        usage = memory_monitor.get_current_usage()
        
        # Check that the usage stats are valid
        assert isinstance(usage, ResourceUsageStats)
        assert usage.rss > 0
        assert usage.vms > 0
        assert usage.process_id > 0
        assert usage.timestamp > 0
        
    def test_usage_history(self, memory_monitor):
        """Test recording and retrieving usage history."""
        # Start monitoring
        memory_monitor.start_monitoring()
        
        # Wait for some history to accumulate
        time.sleep(0.05)
        
        # Get usage history
        history = memory_monitor.get_usage_history()
        
        # Check that history is being recorded
        assert len(history) > 0
        for usage in history:
            assert isinstance(usage, ResourceUsageStats)
            
        # Stop monitoring
        memory_monitor.stop_monitoring()
        
    def test_get_max_usage(self, memory_monitor):
        """Test getting maximum memory usage."""
        # Start monitoring
        memory_monitor.start_monitoring()
        
        # Create some memory usage to track
        data = [0] * 1000000  # Allocate memory
        
        # Wait for monitoring to capture
        time.sleep(0.05)
        
        # Get maximum usage
        max_usage = memory_monitor.get_max_usage()
        
        # Check that max usage is returned
        assert max_usage is not None
        assert isinstance(max_usage, ResourceUsageStats)
        assert max_usage.rss > 0
        
        # Cleanup
        del data
        memory_monitor.stop_monitoring()
        
    def test_clear_history(self, memory_monitor):
        """Test clearing usage history."""
        # Start monitoring
        memory_monitor.start_monitoring()
        
        # Wait for some history to accumulate
        time.sleep(0.05)
        
        # Verify history exists
        assert len(memory_monitor.get_usage_history()) > 0
        
        # Clear history
        memory_monitor.clear_history()
        
        # Verify history is cleared
        assert len(memory_monitor.get_usage_history()) == 0
        
        # Stop monitoring
        memory_monitor.stop_monitoring()
        
    def test_context_manager(self):
        """Test using memory monitor as a context manager."""
        # Use context manager
        with MemoryMonitor() as monitor:
            assert monitor._monitoring_active
            assert monitor._monitoring_thread is not None
            assert monitor._monitoring_thread.is_alive()
            
            # Create some memory to track
            data = [0] * 1000000
            
            # Wait for monitoring to capture
            time.sleep(0.05)
            
            # Check that history is being recorded
            assert len(monitor.get_usage_history()) > 0
            
            # Cleanup
            del data
            
        # After context, monitoring should be stopped
        assert not monitor._monitoring_active
        
    def test_get_usage_summary(self, memory_monitor):
        """Test getting usage summary."""
        # Start monitoring
        memory_monitor.start_monitoring()
        
        # Create some memory to track
        data = [0] * 1000000
        
        # Wait for monitoring to capture
        time.sleep(0.05)
        
        # Get summary
        summary = memory_monitor.get_usage_summary()
        
        # Check summary structure
        assert "current" in summary
        assert "max" in summary
        assert "min" in summary
        assert "avg" in summary
        assert "samples" in summary
        assert summary["samples"] > 0
        
        # Cleanup
        del data
        memory_monitor.stop_monitoring()
        
    def test_memory_unit_conversion(self):
        """Test memory unit conversion."""
        # Create a mock usage stats
        stats = ResourceUsageStats(
            rss=1024 * 1024,  # 1 MB
            vms=2 * 1024 * 1024,  # 2 MB
            shared=0.5 * 1024 * 1024,  # 0.5 MB
            text=0.1 * 1024 * 1024,  # 0.1 MB
            lib=0,
            data=0,
            dirty=0,
            uss=0,
            pss=0,
            swap=0,
            percent=0,
            cpu_percent=0,
            process_id=1,
            process_name="test",
            timestamp=time.time()
        )
        
        # Test conversion
        assert stats.get_rss(MemoryUnit.BYTES) == 1024 * 1024
        assert stats.get_rss(MemoryUnit.KB) == 1024
        assert stats.get_rss(MemoryUnit.MB) == 1
        assert stats.get_rss(MemoryUnit.GB) == 1 / 1024
        
    def test_force_garbage_collection(self, memory_monitor):
        """Test forcing garbage collection."""
        # Create objects to be collected
        data = [MagicMock() for _ in range(10)]
        weak_refs = [MagicMock() for _ in range(10)]
        
        # Force garbage collection
        collected = memory_monitor.force_garbage_collection()
        
        # Cleanup
        del data
        del weak_refs
        
        # Check that collection was performed
        assert collected >= 0
        
    @patch('psutil.Process')
    def test_memory_limit_exception(self, mock_process):
        """Test memory limit exception."""
        # Mock process to return high memory usage
        mock_process_instance = MagicMock()
        mock_process_instance.memory_info.return_value = MagicMock(
            rss=1024 * 1024 * 1024  # 1 GB
        )
        mock_process.return_value = mock_process_instance
        
        # Test exception creation
        error = MemoryLimitExceededError("Memory limit exceeded", limit_mb=100)
        
        assert "Memory limit exceeded" in str(error)
        assert "100 MB" in str(error)


@pytest.mark.asyncio
async def test_async_with_memory_monitor():
    """Test using memory monitor with async code."""
    monitor = MemoryMonitor(poll_interval=0.01)
    monitor.start_monitoring()
    
    # Run some async code that uses memory
    async def memory_intensive_task():
        data = [0] * 1000000
        await asyncio.sleep(0.05)
        return len(data)
    
    result = await memory_intensive_task()
    
    # Get summary after async operation
    summary = monitor.get_usage_summary()
    
    # Check results
    assert result == 1000000
    assert summary["samples"] > 0
    
    # Cleanup
    monitor.stop_monitoring() 