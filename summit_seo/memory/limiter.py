"""Memory limiting functionality for Summit SEO."""

import asyncio
import gc
import logging
import os
import sys
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union

from .monitor import MemoryLimitExceededError, MemoryMonitor, MemoryUnit

logger = logging.getLogger(__name__)


class LimitAction(str, Enum):
    """Actions to take when memory limit is exceeded."""
    
    WARN = "warn"  # Log a warning
    ERROR = "error"  # Raise an error
    GC = "gc"  # Run garbage collection
    THROTTLE = "throttle"  # Throttle processing
    ABORT = "abort"  # Abort current operation


class LimitScope(str, Enum):
    """Scope of memory limit application."""
    
    RSS = "rss"  # Resident set size
    VSS = "vss"  # Virtual memory size
    USS = "uss"  # Unique set size
    PSS = "pss"  # Proportional set size
    TOTAL = "total"  # Total system memory


@dataclass
class MemoryLimit:
    """Memory limits configuration with multiple thresholds."""
    
    soft_limit: int  # Warning threshold
    hard_limit: int  # Error threshold
    critical_limit: int  # Critical threshold that will abort operations
    unit: MemoryUnit = MemoryUnit.MB
    scope: LimitScope = LimitScope.RSS
    
    @property
    def soft_limit_bytes(self) -> int:
        """Get soft limit in bytes."""
        return self._to_bytes(self.soft_limit)
        
    @property
    def hard_limit_bytes(self) -> int:
        """Get hard limit in bytes."""
        return self._to_bytes(self.hard_limit)
        
    @property
    def critical_limit_bytes(self) -> int:
        """Get critical limit in bytes."""
        return self._to_bytes(self.critical_limit)
        
    def _to_bytes(self, value: int) -> int:
        """Convert value to bytes based on unit."""
        if self.unit == MemoryUnit.KB:
            return value * 1024
        elif self.unit == MemoryUnit.MB:
            return value * 1024 * 1024
        elif self.unit == MemoryUnit.GB:
            return value * 1024 * 1024 * 1024
        return value


@dataclass
class MemoryThreshold:
    """Memory usage threshold configuration."""
    
    limit: int  # Limit in bytes
    action: LimitAction  # Action to take when limit is exceeded
    cooldown: float = 5.0  # Cooldown period in seconds
    limit_unit: MemoryUnit = MemoryUnit.BYTES
    description: str = ""  # Description of this threshold
    last_triggered: float = 0.0  # Timestamp when this threshold was last triggered
    
    def is_cooldown_active(self) -> bool:
        """Check if cooldown period is active.
        
        Returns:
            True if cooldown is active
        """
        return (time.time() - self.last_triggered) < self.cooldown
    
    def mark_triggered(self):
        """Mark this threshold as triggered now."""
        self.last_triggered = time.time()
        
    def limit_in_bytes(self) -> int:
        """Get limit in bytes.
        
        Returns:
            Limit converted to bytes
        """
        if self.limit_unit == MemoryUnit.KB:
            return self.limit * 1024
        elif self.limit_unit == MemoryUnit.MB:
            return self.limit * 1024 * 1024
        elif self.limit_unit == MemoryUnit.GB:
            return self.limit * 1024 * 1024 * 1024
        return self.limit


class MemoryLimiter:
    """Memory limiter to enforce memory usage limits."""
    
    def __init__(
        self,
        monitor: Optional[MemoryMonitor] = None,
        poll_interval: float = 1.0,
        auto_start: bool = False
    ):
        """Initialize memory limiter.
        
        Args:
            monitor: Memory monitor to use
            poll_interval: Interval to check memory usage in seconds
            auto_start: Whether to start monitoring automatically
        """
        self.monitor = monitor or MemoryMonitor(poll_interval=poll_interval)
        self.poll_interval = poll_interval
        self.thresholds: List[MemoryThreshold] = []
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._throttle_factor = 1.0  # 1.0 means no throttling
        self._callbacks: Dict[LimitAction, List[Callable]] = {
            action: [] for action in LimitAction
        }
        
        # Start monitoring if requested
        if auto_start:
            self.start()
            
    @property
    def callbacks(self) -> Dict[LimitAction, List[Callable]]:
        """Get the callbacks dictionary.
        
        Returns:
            Dictionary mapping actions to callback lists
        """
        return self._callbacks
        
    def add_threshold(
        self,
        limit: Union[int, float],
        action: Union[LimitAction, str],
        limit_unit: Union[MemoryUnit, str] = MemoryUnit.MB,
        cooldown: float = 5.0,
        description: str = ""
    ) -> None:
        """Add a memory threshold.
        
        Args:
            limit: Memory limit
            action: Action to take when limit is exceeded
            limit_unit: Unit of the limit
            cooldown: Cooldown period in seconds
            description: Description of this threshold
        """
        # Convert string action to enum
        if isinstance(action, str):
            action = LimitAction(action.lower())
            
        # Convert string unit to enum
        if isinstance(limit_unit, str):
            limit_unit = MemoryUnit(limit_unit.upper())
            
        threshold = MemoryThreshold(
            limit=int(limit),
            action=action,
            limit_unit=limit_unit,
            cooldown=cooldown,
            description=description or f"{limit} {limit_unit.name} limit with {action.name} action"
        )
        
        with self._lock:
            self.thresholds.append(threshold)
            # Sort thresholds by limit (ascending)
            self.thresholds.sort(key=lambda t: t.limit_in_bytes())
        
        logger.debug(f"Added memory threshold: {threshold.description}")
        
    def remove_threshold(self, limit: int, limit_unit: Union[MemoryUnit, str] = MemoryUnit.MB) -> bool:
        """Remove a memory threshold.
        
        Args:
            limit: Memory limit to remove
            limit_unit: Unit of the limit
            
        Returns:
            True if threshold was removed
        """
        # Convert string unit to enum
        if isinstance(limit_unit, str):
            limit_unit = MemoryUnit(limit_unit.upper())
            
        with self._lock:
            initial_count = len(self.thresholds)
            self.thresholds = [
                t for t in self.thresholds
                if not (t.limit == limit and t.limit_unit == limit_unit)
            ]
            return len(self.thresholds) < initial_count
        
    def register_callback(self, action: Union[LimitAction, str], callback: Callable) -> None:
        """Register a callback for a specific action.
        
        Args:
            action: Action to register callback for
            callback: Callback function
        """
        # Convert string action to enum
        if isinstance(action, str):
            action = LimitAction(action.lower())
            
        with self._lock:
            self._callbacks[action].append(callback)
        
    def unregister_callback(self, action: Union[LimitAction, str], callback: Callable) -> bool:
        """Unregister a callback for a specific action.
        
        Args:
            action: Action to unregister callback for
            callback: Callback function
            
        Returns:
            True if callback was unregistered
        """
        # Convert string action to enum
        if isinstance(action, str):
            action = LimitAction(action.lower())
            
        with self._lock:
            if callback in self._callbacks[action]:
                self._callbacks[action].remove(callback)
                return True
        return False
        
    def start(self) -> None:
        """Start memory limit monitoring."""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            logger.warning("Memory limiter is already running")
            return
            
        self._stop_event.clear()
        self.monitor.start_monitoring()
        
        # Start monitoring thread
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="MemoryLimiterThread"
        )
        self._monitoring_thread.start()
        
        logger.debug("Memory limiter started")
        
    def stop(self) -> None:
        """Stop memory limit monitoring."""
        if not self._monitoring_thread or not self._monitoring_thread.is_alive():
            logger.warning("Memory limiter is not running")
            return
            
        self._stop_event.set()
        self._monitoring_thread.join(timeout=2.0)
        self.monitor.stop_monitoring()
        
        logger.debug("Memory limiter stopped")
        
    def get_throttle_factor(self) -> float:
        """Get current throttle factor.
        
        Returns:
            Throttle factor (1.0 means no throttling)
        """
        return self._throttle_factor
        
    def should_throttle(self) -> bool:
        """Check if processing should be throttled.
        
        Returns:
            True if processing should be throttled
        """
        return self._throttle_factor < 1.0
        
    @property
    def is_monitoring(self) -> bool:
        """Check if memory monitoring is active.
        
        Returns:
            True if monitoring is active
        """
        return self._monitoring_thread is not None and self._monitoring_thread.is_alive()
        
    def apply_throttling(self, factor: float = 0.5) -> None:
        """Apply throttling to processing.
        
        Args:
            factor: Throttle factor (0-1, lower means more throttling)
        """
        with self._lock:
            self._throttle_factor = max(0.1, min(1.0, factor))
        
        logger.debug(f"Applied throttling with factor {self._throttle_factor}")
        
    def reset_throttling(self) -> None:
        """Reset throttling to normal."""
        with self._lock:
            self._throttle_factor = 1.0
            
        logger.debug("Reset throttling to normal")
        
    async def throttle_if_needed(self) -> None:
        """Apply throttling by sleeping if needed.
        
        This method sleeps based on the throttle factor to slow down processing.
        """
        factor = self.get_throttle_factor()
        if factor < 1.0:
            # Sleep time increases as factor decreases
            sleep_time = (1.0 - factor) * self.poll_interval
            await asyncio.sleep(sleep_time)
            
    def check_memory_usage(self, current_usage: Optional[int] = None) -> List[MemoryThreshold]:
        """Check if any memory thresholds are exceeded.
        
        Args:
            current_usage: Current memory usage in bytes
            
        Returns:
            List of exceeded thresholds
        """
        if current_usage is None:
            usage_stats = self.monitor.get_current_usage()
            current_usage = usage_stats.rss
            
        exceeded_thresholds = []
        
        with self._lock:
            for threshold in self.thresholds:
                if (
                    current_usage >= threshold.limit_in_bytes() and
                    not threshold.is_cooldown_active()
                ):
                    exceeded_thresholds.append(threshold)
                    threshold.mark_triggered()
                    
        return exceeded_thresholds
        
    def _handle_exceeded_threshold(self, threshold: MemoryThreshold, current_usage: int) -> None:
        """Handle an exceeded threshold.
        
        Args:
            threshold: Exceeded threshold
            current_usage: Current memory usage in bytes
        """
        # Format memory values for display
        limit_mb = threshold.limit_in_bytes() / (1024 * 1024)
        usage_mb = current_usage / (1024 * 1024)
        
        # Handle based on action
        if threshold.action == LimitAction.WARN:
            logger.warning(
                f"Memory usage warning: {usage_mb:.2f} MB exceeds threshold of {limit_mb:.2f} MB"
            )
            
        elif threshold.action == LimitAction.ERROR:
            error_msg = f"Memory usage error: {usage_mb:.2f} MB exceeds threshold of {limit_mb:.2f} MB"
            logger.error(error_msg)
            raise MemoryLimitExceededError(error_msg)
            
        elif threshold.action == LimitAction.GC:
            logger.info(
                f"Memory usage triggered GC: {usage_mb:.2f} MB exceeds threshold of {limit_mb:.2f} MB"
            )
            gc.collect()
            
        elif threshold.action == LimitAction.THROTTLE:
            # Calculate throttle factor based on how much we've exceeded the limit
            # The more we exceed, the lower the factor (more throttling)
            excess_ratio = threshold.limit_in_bytes() / max(1, current_usage)
            throttle_factor = max(0.1, min(0.9, excess_ratio))
            
            logger.info(
                f"Memory usage triggered throttling: {usage_mb:.2f} MB exceeds threshold of "
                f"{limit_mb:.2f} MB (throttle factor: {throttle_factor:.2f})"
            )
            
            self.apply_throttling(throttle_factor)
            
        elif threshold.action == LimitAction.ABORT:
            error_msg = f"Memory usage abort: {usage_mb:.2f} MB exceeds threshold of {limit_mb:.2f} MB"
            logger.critical(error_msg)
            
            # Call abort callbacks
            self._trigger_callbacks(threshold.action, current_usage, threshold)
            
            # Raise error to abort
            raise MemoryLimitExceededError(error_msg)
            
        # Trigger callbacks for this action
        self._trigger_callbacks(threshold.action, current_usage, threshold)
        
    def _trigger_callbacks(
        self,
        action: LimitAction,
        current_usage: int,
        threshold: MemoryThreshold
    ) -> None:
        """Trigger registered callbacks for an action.
        
        Args:
            action: Action that was triggered
            current_usage: Current memory usage in bytes
            threshold: Threshold that was exceeded
        """
        callbacks = self._callbacks.get(action, [])
        
        for callback in callbacks:
            try:
                callback(current_usage, threshold)
            except Exception as e:
                logger.error(f"Error in memory limiter callback: {e}")
                
    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        logger.debug("Memory limiter monitoring loop started")
        
        while not self._stop_event.is_set():
            try:
                # Get current memory usage
                usage_stats = self.monitor.get_current_usage()
                current_usage = usage_stats.rss
                
                # Check thresholds
                exceeded_thresholds = self.check_memory_usage(current_usage)
                
                # Handle exceeded thresholds
                for threshold in exceeded_thresholds:
                    try:
                        self._handle_exceeded_threshold(threshold, current_usage)
                    except MemoryLimitExceededError:
                        # Continue monitoring even if an error is raised
                        pass
                    except Exception as e:
                        logger.error(f"Error handling memory threshold: {e}")
                        
                # If no thresholds were exceeded and we're throttling, gradually reduce throttling
                if not exceeded_thresholds and self.should_throttle():
                    # Gradually restore throttle factor
                    current_factor = self.get_throttle_factor()
                    new_factor = min(1.0, current_factor + 0.05)
                    
                    if new_factor > current_factor:
                        self.apply_throttling(new_factor)
                        
            except Exception as e:
                logger.error(f"Error in memory limiter monitoring loop: {e}")
                
            # Sleep until next check
            time.sleep(self.poll_interval)
            
        logger.debug("Memory limiter monitoring loop stopped") 