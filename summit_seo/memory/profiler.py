"""Memory profiling functionality for Summit SEO."""

import asyncio
import cProfile
import functools
import io
import os
import pstats
import sys
import time
import tracemalloc
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar, Union
import logging

from .monitor import MemoryMonitor, ResourceUsageStats

logger = logging.getLogger(__name__)
T = TypeVar('T')  # Return type for profiled functions

@dataclass
class ProfilerConfig:
    """Configuration for memory profiler."""
    
    trace_lines: bool = False  # Whether to trace line by line
    trace_alloc: bool = True  # Whether to trace allocations
    capture_profile: bool = False  # Whether to capture CPU profile
    capture_traceback: bool = True  # Whether to capture tracebacks
    max_frames: int = 10  # Maximum traceback frames to capture
    max_snapshots: int = 10  # Maximum number of snapshots to keep
    monitor_memory: bool = True  # Whether to monitor memory during profiling
    monitor_interval: float = 0.1  # Interval for memory monitoring in seconds


@dataclass
class ProfileResult:
    """Result of a memory profiling session."""
    
    # Basic profiling information
    start_time: datetime
    end_time: datetime
    duration: float  # In seconds
    name: str  # Name of the profiled function or block
    
    # Memory usage
    memory_before: Optional[ResourceUsageStats] = None
    memory_after: Optional[ResourceUsageStats] = None
    peak_memory: Optional[ResourceUsageStats] = None
    
    # Tracemalloc info
    top_stats: Optional[List[Tuple[Any, int]]] = None  # Top memory blocks
    memory_diff: Optional[int] = None  # Memory difference in bytes
    
    # CPU profiling
    cpu_profile: Optional[pstats.Stats] = None
    
    # Additional info
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profiling result to dictionary."""
        result = {
            "name": self.name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": self.duration,
            "context": self.context
        }
        
        # Add memory usage if available
        if self.memory_before and self.memory_after:
            result["memory"] = {
                "before_bytes": self.memory_before.rss,
                "after_bytes": self.memory_after.rss,
                "diff_bytes": self.memory_after.rss - self.memory_before.rss,
                "peak_bytes": self.peak_memory.rss if self.peak_memory else None
            }
        
        # Add tracemalloc stats if available
        if self.top_stats:
            result["top_allocations"] = [
                {
                    "traceback": str(frame[0]),
                    "size_bytes": frame[1]
                }
                for frame in self.top_stats
            ]
        
        # Add memory diff if available
        if self.memory_diff is not None:
            result["tracemalloc_diff_bytes"] = self.memory_diff
        
        return result


class Profiler:
    """Memory profiler for tracking memory usage of code blocks."""
    
    def __init__(self, config: Optional[ProfilerConfig] = None):
        """Initialize profiler.
        
        Args:
            config: Configuration for the profiler
        """
        self.config = config or ProfilerConfig()
        self.memory_monitor = MemoryMonitor(poll_interval=self.config.monitor_interval)
        self.snapshots: List[tracemalloc.Snapshot] = []
        self.active_profiling = False
        self.current_snapshot = None
        
    def start(self):
        """Start tracemalloc and memory monitoring."""
        if not tracemalloc.is_tracing():
            tracemalloc.start(self.config.max_frames)
        
        # Take initial snapshot
        self.current_snapshot = tracemalloc.take_snapshot()
        
        if self.config.monitor_memory:
            self.memory_monitor.start_monitoring()
            
        self.active_profiling = True
        logger.debug("Memory profiling started")
        
    def stop(self) -> Optional[tracemalloc.Snapshot]:
        """Stop tracemalloc and memory monitoring.
        
        Returns:
            Final snapshot if available
        """
        snapshot = None
        
        if tracemalloc.is_tracing():
            snapshot = tracemalloc.take_snapshot()
            tracemalloc.stop()
        
        if self.config.monitor_memory:
            self.memory_monitor.stop_monitoring()
            
        self.active_profiling = False
        logger.debug("Memory profiling stopped")
        
        return snapshot
        
    def take_snapshot(self, name: Optional[str] = None) -> tracemalloc.Snapshot:
        """Take a memory snapshot.
        
        Args:
            name: Optional name for the snapshot
            
        Returns:
            Memory snapshot
        """
        snapshot = tracemalloc.take_snapshot()
        
        if name:
            snapshot.name = name
            
        # Add to snapshots list, respecting max size
        self.snapshots.append(snapshot)
        if len(self.snapshots) > self.config.max_snapshots:
            self.snapshots.pop(0)
            
        return snapshot
        
    def compare_snapshots(
        self, 
        snapshot1: tracemalloc.Snapshot, 
        snapshot2: tracemalloc.Snapshot,
        key_type: str = 'traceback',
        limit: int = 10
    ) -> List[Tuple[Any, int]]:
        """Compare two snapshots and return top differences.
        
        Args:
            snapshot1: First snapshot
            snapshot2: Second snapshot
            key_type: Type of key to group by ('traceback', 'lineno', or 'filename')
            limit: Maximum number of results to return
            
        Returns:
            List of tuples containing (traceback, size_diff)
        """
        if key_type == 'lineno':
            key_type = 'lineno'
        elif key_type == 'filename':
            key_type = 'filename'
        else:
            key_type = 'traceback'
            
        stats = snapshot2.compare_to(snapshot1, key_type)
        return stats[:limit]
        
    def profile_block(self, name: str) -> ProfileResult:
        """Profile a block of code using context manager.
        
        Args:
            name: Name for the profiling session
            
        Returns:
            ProfileResult with profiling data
        """
        # Start everything
        cpu_profile = None
        start_time = datetime.now()
        
        # Set up CPU profiling if requested
        if self.config.capture_profile:
            cpu_profile = cProfile.Profile()
            cpu_profile.enable()
        
        # Start memory profiling
        self.start()
        
        # Capture initial memory state
        memory_before = self.memory_monitor.get_current_usage()
        initial_snapshot = self.take_snapshot(f"{name}_start")
        
        return _ProfilingContext(
            profiler=self,
            name=name,
            start_time=start_time,
            memory_before=memory_before,
            initial_snapshot=initial_snapshot,
            cpu_profile=cpu_profile
        )
        
    def profile_function(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator to profile a function.
        
        Args:
            func: Function to profile
            
        Returns:
            Wrapped function
        """
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            """Wrapper for synchronous functions."""
            name = func.__qualname__
            with self.profile_block(name) as profile_result:
                result = func(*args, **kwargs)
                
            # Log profiling result
            logger.debug(f"Profiling {name}: {profile_result.to_dict()}")
            
            return result
            
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            """Wrapper for asynchronous functions."""
            name = func.__qualname__
            with self.profile_block(name) as profile_result:
                result = await func(*args, **kwargs)
                
            # Log profiling result
            logger.debug(f"Profiling {name}: {profile_result.to_dict()}")
            
            return result
            
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper


class _ProfilingContext:
    """Context manager for profiling blocks of code."""
    
    def __init__(
        self,
        profiler: Profiler,
        name: str,
        start_time: datetime,
        memory_before: ResourceUsageStats,
        initial_snapshot: tracemalloc.Snapshot,
        cpu_profile: Optional[cProfile.Profile] = None
    ):
        """Initialize profiling context.
        
        Args:
            profiler: Profiler instance
            name: Name for the profiling session
            start_time: Start time of profiling
            memory_before: Initial memory usage
            initial_snapshot: Initial memory snapshot
            cpu_profile: CPU profiler if enabled
        """
        self.profiler = profiler
        self.name = name
        self.start_time = start_time
        self.memory_before = memory_before
        self.initial_snapshot = initial_snapshot
        self.cpu_profile = cpu_profile
        self.peak_memory = memory_before
        
    def __enter__(self) -> 'ProfileResult':
        """Enter profiling context.
        
        Returns:
            Self for storing profiling result
        """
        # Create initial profile result
        self.profile_result = ProfileResult(
            start_time=self.start_time,
            end_time=self.start_time,  # Will be updated on exit
            duration=0.0,  # Will be updated on exit
            name=self.name,
            memory_before=self.memory_before
        )
        
        return self.profile_result
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit profiling context and finalize profiling."""
        # Capture end time
        end_time = datetime.now()
        
        # Capture final memory state
        memory_after = self.profiler.memory_monitor.get_current_usage()
        peak_memory = self.profiler.memory_monitor.get_max_usage() or memory_after
        
        # Capture final snapshot
        final_snapshot = self.profiler.take_snapshot(f"{self.name}_end")
        
        # Get memory difference using tracemalloc
        top_stats = None
        memory_diff = None
        
        if self.initial_snapshot and final_snapshot:
            top_stats = self.profiler.compare_snapshots(
                self.initial_snapshot,
                final_snapshot
            )
            
            # Calculate total memory difference
            stats = final_snapshot.compare_to(self.initial_snapshot, 'traceback')
            memory_diff = sum(stat.size_diff for stat in stats)
            
        # Finalize CPU profiling if enabled
        cpu_stats = None
        if self.cpu_profile:
            self.cpu_profile.disable()
            
            # Capture CPU profiling stats
            s = io.StringIO()
            ps = pstats.Stats(self.cpu_profile, stream=s).sort_stats('cumulative')
            ps.print_stats(20)  # Top 20 functions
            cpu_stats = ps
            
        # Stop profiling
        self.profiler.stop()
        
        # Update profile result
        self.profile_result.end_time = end_time
        self.profile_result.duration = (end_time - self.start_time).total_seconds()
        self.profile_result.memory_after = memory_after
        self.profile_result.peak_memory = peak_memory
        self.profile_result.top_stats = top_stats
        self.profile_result.memory_diff = memory_diff
        self.profile_result.cpu_profile = cpu_stats
        
        # Add exception info if an exception occurred
        if exc_type:
            self.profile_result.context['exception'] = {
                'type': exc_type.__name__,
                'message': str(exc_val) if exc_val else '',
                'traceback': traceback.format_exception(exc_type, exc_val, exc_tb)
            }
            
        # Don't suppress exceptions
        return False 