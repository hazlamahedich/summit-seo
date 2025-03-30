"""Tests for the memory limiter implementation."""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch

from summit_seo.memory.limiter import (
    LimitAction, LimitScope, MemoryLimit, MemoryLimiter, MemoryThreshold
)
from summit_seo.memory.monitor import MemoryLimitExceededError, MemoryMonitor, MemoryUnit


@pytest.fixture
def memory_monitor():
    """Create a memory monitor for testing."""
    monitor = MagicMock(spec=MemoryMonitor)
    monitor.get_current_usage.return_value = MagicMock(rss=100 * 1024 * 1024)  # 100MB
    return monitor


@pytest.fixture
def memory_limiter(memory_monitor):
    """Create a memory limiter for testing."""
    limiter = MemoryLimiter(monitor=memory_monitor, poll_interval=0.01, auto_start=False)
    return limiter


class TestMemoryThreshold:
    """Tests for the MemoryThreshold class."""
    
    def test_init(self):
        """Test initialization of threshold."""
        threshold = MemoryThreshold(
            limit=1000,
            action=LimitAction.WARN,
            cooldown=5.0,
            limit_unit=MemoryUnit.MB,
            description="Test threshold"
        )
        
        assert threshold.limit == 1000
        assert threshold.action == LimitAction.WARN
        assert threshold.cooldown == 5.0
        assert threshold.limit_unit == MemoryUnit.MB
        assert threshold.description == "Test threshold"
        assert threshold.last_triggered == 0.0
        
    def test_is_cooldown_active(self):
        """Test cooldown check."""
        threshold = MemoryThreshold(
            limit=1000,
            action=LimitAction.WARN,
            cooldown=1.0
        )
        
        # Initially cooldown should not be active
        assert not threshold.is_cooldown_active()
        
        # Mark as triggered
        threshold.mark_triggered()
        
        # Now cooldown should be active
        assert threshold.is_cooldown_active()
        
        # Wait for cooldown to expire
        time.sleep(1.1)
        
        # Cooldown should no longer be active
        assert not threshold.is_cooldown_active()
        
    def test_limit_in_bytes(self):
        """Test conversion of limit to bytes."""
        # Test with bytes
        threshold_bytes = MemoryThreshold(
            limit=1000,
            action=LimitAction.WARN,
            limit_unit=MemoryUnit.BYTES
        )
        assert threshold_bytes.limit_in_bytes() == 1000
        
        # Test with KB
        threshold_kb = MemoryThreshold(
            limit=1000,
            action=LimitAction.WARN,
            limit_unit=MemoryUnit.KB
        )
        assert threshold_kb.limit_in_bytes() == 1000 * 1024
        
        # Test with MB
        threshold_mb = MemoryThreshold(
            limit=1000,
            action=LimitAction.WARN,
            limit_unit=MemoryUnit.MB
        )
        assert threshold_mb.limit_in_bytes() == 1000 * 1024 * 1024
        
        # Test with GB
        threshold_gb = MemoryThreshold(
            limit=1,
            action=LimitAction.WARN,
            limit_unit=MemoryUnit.GB
        )
        assert threshold_gb.limit_in_bytes() == 1 * 1024 * 1024 * 1024


class TestMemoryLimit:
    """Tests for the MemoryLimit class."""
    
    def test_init(self):
        """Test initialization of memory limit."""
        limit = MemoryLimit(
            soft_limit=500,
            hard_limit=1000,
            critical_limit=1500,
            unit=MemoryUnit.MB,
            scope=LimitScope.RSS
        )
        
        assert limit.soft_limit == 500
        assert limit.hard_limit == 1000
        assert limit.critical_limit == 1500
        assert limit.unit == MemoryUnit.MB
        assert limit.scope == LimitScope.RSS
        
    def test_to_bytes(self):
        """Test conversion of limits to bytes."""
        limit = MemoryLimit(
            soft_limit=500,
            hard_limit=1000,
            critical_limit=1500,
            unit=MemoryUnit.MB
        )
        
        assert limit.soft_limit_bytes == 500 * 1024 * 1024
        assert limit.hard_limit_bytes == 1000 * 1024 * 1024
        assert limit.critical_limit_bytes == 1500 * 1024 * 1024


class TestMemoryLimiter:
    """Tests for the MemoryLimiter class."""
    
    def test_init(self, memory_monitor):
        """Test initialization of memory limiter."""
        limiter = MemoryLimiter(
            monitor=memory_monitor,
            poll_interval=2.0,
            auto_start=False
        )
        
        assert limiter.monitor == memory_monitor
        assert limiter.poll_interval == 2.0
        assert not limiter.is_monitoring
        assert limiter.thresholds == []
        assert limiter.callbacks == {
            LimitAction.WARN: [],
            LimitAction.ERROR: [],
            LimitAction.GC: [],
            LimitAction.THROTTLE: [],
            LimitAction.ABORT: []
        }
        
    def test_add_threshold(self, memory_limiter):
        """Test adding a threshold."""
        # Add a threshold
        memory_limiter.add_threshold(
            limit=200,
            action=LimitAction.WARN,
            limit_unit=MemoryUnit.MB,
            cooldown=10.0,
            description="Warning threshold"
        )
        
        # Check threshold was added
        assert len(memory_limiter.thresholds) == 1
        threshold = memory_limiter.thresholds[0]
        assert threshold.limit == 200
        assert threshold.action == LimitAction.WARN
        assert threshold.limit_unit == MemoryUnit.MB
        assert threshold.cooldown == 10.0
        assert threshold.description == "Warning threshold"
        
        # Add another threshold
        memory_limiter.add_threshold(
            limit=300,
            action=LimitAction.ERROR,
            limit_unit=MemoryUnit.MB
        )
        
        # Check second threshold was added
        assert len(memory_limiter.thresholds) == 2
        
        # Add a threshold with string action
        memory_limiter.add_threshold(
            limit=400,
            action="gc",
            limit_unit="MB"
        )
        
        # Check third threshold was added with correct action
        assert len(memory_limiter.thresholds) == 3
        assert memory_limiter.thresholds[2].action == LimitAction.GC
        assert memory_limiter.thresholds[2].limit_unit == MemoryUnit.MB
        
    def test_remove_threshold(self, memory_limiter):
        """Test removing a threshold."""
        # Add thresholds
        memory_limiter.add_threshold(
            limit=200,
            action=LimitAction.WARN,
            limit_unit=MemoryUnit.MB
        )
        
        memory_limiter.add_threshold(
            limit=300,
            action=LimitAction.ERROR,
            limit_unit=MemoryUnit.MB
        )
        
        # Remove the first threshold
        removed = memory_limiter.remove_threshold(
            limit=200,
            limit_unit=MemoryUnit.MB
        )
        
        # Check removal was successful
        assert removed
        assert len(memory_limiter.thresholds) == 1
        assert memory_limiter.thresholds[0].limit == 300
        
        # Try to remove a non-existent threshold
        removed = memory_limiter.remove_threshold(
            limit=400,
            limit_unit=MemoryUnit.MB
        )
        
        # Check removal failed
        assert not removed
        assert len(memory_limiter.thresholds) == 1
        
    def test_register_callback(self, memory_limiter):
        """Test registering a callback."""
        # Create callbacks
        warn_callback = MagicMock()
        error_callback = MagicMock()
        
        # Register callbacks
        memory_limiter.register_callback(LimitAction.WARN, warn_callback)
        memory_limiter.register_callback("error", error_callback)
        
        # Check callbacks were registered
        assert warn_callback in memory_limiter.callbacks[LimitAction.WARN]
        assert error_callback in memory_limiter.callbacks[LimitAction.ERROR]
        
    def test_unregister_callback(self, memory_limiter):
        """Test unregistering a callback."""
        # Create callback
        callback = MagicMock()
        
        # Register callback
        memory_limiter.register_callback(LimitAction.WARN, callback)
        assert callback in memory_limiter.callbacks[LimitAction.WARN]
        
        # Unregister callback
        unregistered = memory_limiter.unregister_callback(LimitAction.WARN, callback)
        
        # Check unregistration was successful
        assert unregistered
        assert callback not in memory_limiter.callbacks[LimitAction.WARN]
        
        # Try to unregister a non-existent callback
        unregistered = memory_limiter.unregister_callback(LimitAction.WARN, callback)
        
        # Check unregistration failed
        assert not unregistered
        
    @patch('gc.collect')
    def test_check_memory_usage(self, mock_collect, memory_limiter, memory_monitor):
        """Test checking memory usage."""
        # Set up memory usage
        memory_monitor.get_current_usage.return_value = MagicMock(rss=250 * 1024 * 1024)  # 250MB
        
        # Add thresholds
        memory_limiter.add_threshold(
            limit=200,
            action=LimitAction.WARN,
            limit_unit=MemoryUnit.MB
        )
        
        memory_limiter.add_threshold(
            limit=300,
            action=LimitAction.GC,
            limit_unit=MemoryUnit.MB
        )
        
        # Register callbacks
        warn_callback = MagicMock()
        gc_callback = MagicMock()
        memory_limiter.register_callback(LimitAction.WARN, warn_callback)
        memory_limiter.register_callback(LimitAction.GC, gc_callback)
        
        # Check memory usage
        exceeded = memory_limiter.check_memory_usage()
        
        # Only the first threshold should be exceeded
        assert len(exceeded) == 1
        assert exceeded[0].limit == 200
        assert exceeded[0].action == LimitAction.WARN
        
        # The warning callback should have been called
        warn_callback.assert_called_once()
        gc_callback.assert_not_called()
        mock_collect.assert_not_called()
        
        # Now exceed both thresholds
        memory_monitor.get_current_usage.return_value = MagicMock(rss=350 * 1024 * 1024)  # 350MB
        
        # Reset callbacks
        warn_callback.reset_mock()
        gc_callback.reset_mock()
        
        # Check memory usage again
        exceeded = memory_limiter.check_memory_usage()
        
        # Both thresholds should be exceeded
        assert len(exceeded) == 2
        
        # Both callbacks should have been called
        warn_callback.assert_called_once()
        gc_callback.assert_called_once()
        
        # gc.collect should have been called for the GC action
        mock_collect.assert_called_once()
        
    def test_throttling(self, memory_limiter):
        """Test throttling functionality."""
        # Initially no throttling
        assert memory_limiter.get_throttle_factor() == 1.0
        assert not memory_limiter.should_throttle()
        
        # Apply throttling
        memory_limiter.apply_throttling(factor=0.5)
        
        # Check throttling was applied
        assert memory_limiter.get_throttle_factor() == 0.5
        assert memory_limiter.should_throttle()
        
        # Reset throttling
        memory_limiter.reset_throttling()
        
        # Check throttling was reset
        assert memory_limiter.get_throttle_factor() == 1.0
        assert not memory_limiter.should_throttle()
        
    @patch('gc.collect')
    def test_handle_exceeded_threshold(self, mock_collect, memory_limiter):
        """Test handling exceeded thresholds."""
        # Create thresholds
        warn_threshold = MemoryThreshold(
            limit=100,
            action=LimitAction.WARN,
            limit_unit=MemoryUnit.MB
        )
        
        error_threshold = MemoryThreshold(
            limit=200,
            action=LimitAction.ERROR,
            limit_unit=MemoryUnit.MB
        )
        
        gc_threshold = MemoryThreshold(
            limit=300,
            action=LimitAction.GC,
            limit_unit=MemoryUnit.MB
        )
        
        throttle_threshold = MemoryThreshold(
            limit=400,
            action=LimitAction.THROTTLE,
            limit_unit=MemoryUnit.MB
        )
        
        # Register callbacks
        warn_callback = MagicMock()
        error_callback = MagicMock()
        gc_callback = MagicMock()
        throttle_callback = MagicMock()
        
        memory_limiter.register_callback(LimitAction.WARN, warn_callback)
        memory_limiter.register_callback(LimitAction.ERROR, error_callback)
        memory_limiter.register_callback(LimitAction.GC, gc_callback)
        memory_limiter.register_callback(LimitAction.THROTTLE, throttle_callback)
        
        # Handle warning threshold
        memory_limiter._handle_exceeded_threshold(warn_threshold, 150 * 1024 * 1024)
        
        # Warning callback should be called
        warn_callback.assert_called_once()
        
        # Handle error threshold
        with pytest.raises(MemoryLimitExceededError):
            memory_limiter._handle_exceeded_threshold(error_threshold, 250 * 1024 * 1024)
        
        # Error callback should be called
        error_callback.assert_called_once()
        
        # Handle GC threshold
        memory_limiter._handle_exceeded_threshold(gc_threshold, 350 * 1024 * 1024)
        
        # GC callback should be called and gc.collect should run
        gc_callback.assert_called_once()
        mock_collect.assert_called_once()
        
        # Handle throttle threshold
        memory_limiter._handle_exceeded_threshold(throttle_threshold, 450 * 1024 * 1024)
        
        # Throttle callback should be called and throttling should be applied
        throttle_callback.assert_called_once()
        assert memory_limiter.get_throttle_factor() < 1.0
        
    @pytest.mark.asyncio
    async def test_throttle_if_needed(self, memory_limiter):
        """Test throttle_if_needed method."""
        # Initially no throttling
        await memory_limiter.throttle_if_needed()
        
        # No wait should have happened
        
        # Apply throttling
        memory_limiter.apply_throttling(factor=0.5)
        
        # With throttling, sleep should happen
        start_time = time.time()
        await memory_limiter.throttle_if_needed()
        elapsed = time.time() - start_time
        
        # Some sleep should have happened
        assert elapsed > 0
        
    @patch('threading.Thread')
    def test_start_stop(self, mock_thread, memory_limiter):
        """Test starting and stopping the limiter."""
        # Start monitoring
        memory_limiter.start()
        
        # Thread should be created and started
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
        assert memory_limiter.is_monitoring
        
        # Stop monitoring
        memory_limiter.stop()
        
        # Monitoring should be stopped
        assert not memory_limiter.is_monitoring 