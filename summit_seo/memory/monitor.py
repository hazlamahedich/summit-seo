"""Memory monitoring functionality for Summit SEO."""

import gc
import os
import platform
import psutil
import resource
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import logging

logger = logging.getLogger(__name__)

class MemoryUnit(Enum):
    """Units for memory measurement."""
    
    BYTES = auto()
    KB = auto()
    MB = auto()
    GB = auto()


@dataclass
class ResourceUsageStats:
    """Statistics about resource usage."""
    
    # Memory usage
    rss: int  # Resident set size in bytes
    vms: int  # Virtual memory size in bytes
    shared: int  # Shared memory size in bytes
    text: int  # Text segment size in bytes
    data: int  # Data segment size in bytes
    lib: int  # Lib segment size in bytes
    
    # CPU usage
    cpu_percent: float  # CPU usage percentage
    
    # Process info
    pid: int  # Process ID
    num_threads: int  # Number of threads
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self, memory_unit: MemoryUnit = MemoryUnit.MB) -> Dict[str, Any]:
        """Convert statistics to dictionary with specified memory unit.
        
        Args:
            memory_unit: Unit to use for memory values
            
        Returns:
            Dictionary of resource usage statistics
        """
        divisor = {
            MemoryUnit.BYTES: 1,
            MemoryUnit.KB: 1024,
            MemoryUnit.MB: 1024 * 1024,
            MemoryUnit.GB: 1024 * 1024 * 1024
        }[memory_unit]
        
        unit_suffix = {
            MemoryUnit.BYTES: "bytes",
            MemoryUnit.KB: "KB",
            MemoryUnit.MB: "MB",
            MemoryUnit.GB: "GB"
        }[memory_unit]
        
        return {
            f"rss_{unit_suffix}": self.rss / divisor,
            f"vms_{unit_suffix}": self.vms / divisor,
            f"shared_{unit_suffix}": self.shared / divisor,
            f"text_{unit_suffix}": self.text / divisor,
            f"data_{unit_suffix}": self.data / divisor,
            f"lib_{unit_suffix}": self.lib / divisor,
            "cpu_percent": self.cpu_percent,
            "pid": self.pid,
            "num_threads": self.num_threads,
            "timestamp": self.timestamp.isoformat()
        }
        
    @property
    def total_memory(self) -> int:
        """Get total memory usage (RSS) in bytes."""
        return self.rss


class MemoryLimitExceededError(Exception):
    """Exception raised when memory usage exceeds limit."""
    
    def __init__(self, current: int, limit: int, unit: str = "bytes"):
        """Initialize with current memory usage and limit.
        
        Args:
            current: Current memory usage
            limit: Memory limit
            unit: Memory unit (e.g., "bytes", "MB", "GB")
        """
        self.current = current
        self.limit = limit
        self.unit = unit
        super().__init__(
            f"Memory limit exceeded: {current} {unit} > {limit} {unit}"
        )


class MemoryMonitor:
    """Monitor memory usage of the current process."""
    
    def __init__(self, poll_interval: float = 1.0):
        """Initialize memory monitor.
        
        Args:
            poll_interval: Interval in seconds between polling for background monitoring
        """
        self.poll_interval = poll_interval
        self.process = psutil.Process(os.getpid())
        self.history: List[ResourceUsageStats] = []
        self.max_usage: Optional[ResourceUsageStats] = None
        self.monitoring_thread: Optional[threading.Thread] = None
        self.is_monitoring = False
        self.lock = threading.Lock()
        
    def get_current_usage(self) -> ResourceUsageStats:
        """Get current resource usage.
        
        Returns:
            ResourceUsageStats with current usage
        """
        mem_info = self.process.memory_info()
        
        stats = ResourceUsageStats(
            rss=mem_info.rss,
            vms=mem_info.vms,
            shared=getattr(mem_info, 'shared', 0),
            text=getattr(mem_info, 'text', 0),
            data=getattr(mem_info, 'data', 0),
            lib=getattr(mem_info, 'lib', 0),
            cpu_percent=self.process.cpu_percent(),
            pid=self.process.pid,
            num_threads=self.process.num_threads()
        )
        
        with self.lock:
            if not self.max_usage or stats.rss > self.max_usage.rss:
                self.max_usage = stats
        
        return stats
    
    def start_monitoring(self):
        """Start background monitoring thread."""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring thread."""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
            self.monitoring_thread = None
        logger.info("Memory monitoring stopped")
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.is_monitoring:
            try:
                stats = self.get_current_usage()
                with self.lock:
                    self.history.append(stats)
                    # Keep history under reasonable size (last hour at poll_interval)
                    max_history = int(3600 / self.poll_interval)
                    if len(self.history) > max_history:
                        self.history = self.history[-max_history:]
            except Exception as e:
                logger.error(f"Error in memory monitoring: {str(e)}")
            
            time.sleep(self.poll_interval)
    
    def get_history(self, limit: Optional[int] = None) -> List[ResourceUsageStats]:
        """Get history of resource usage.
        
        Args:
            limit: Maximum number of entries to return (most recent first)
            
        Returns:
            List of resource usage statistics
        """
        with self.lock:
            if limit:
                return list(reversed(self.history[-limit:]))
            return list(reversed(self.history))
    
    def get_max_usage(self) -> Optional[ResourceUsageStats]:
        """Get maximum memory usage recorded.
        
        Returns:
            ResourceUsageStats for maximum usage or None if no data
        """
        with self.lock:
            return self.max_usage
    
    def clear_history(self):
        """Clear monitoring history."""
        with self.lock:
            self.history.clear()
            self.max_usage = None
    
    @staticmethod
    def get_system_memory() -> Tuple[int, int]:
        """Get total and available system memory.
        
        Returns:
            Tuple of (total, available) memory in bytes
        """
        mem = psutil.virtual_memory()
        return mem.total, mem.available
    
    def get_memory_summary(self, unit: MemoryUnit = MemoryUnit.MB) -> Dict[str, Any]:
        """Get memory usage summary.
        
        Args:
            unit: Unit for memory values
            
        Returns:
            Dictionary with memory usage summary
        """
        current = self.get_current_usage()
        max_usage = self.get_max_usage()
        total_mem, avail_mem = self.get_system_memory()
        
        divisor = {
            MemoryUnit.BYTES: 1,
            MemoryUnit.KB: 1024,
            MemoryUnit.MB: 1024 * 1024,
            MemoryUnit.GB: 1024 * 1024 * 1024
        }[unit]
        
        unit_str = {
            MemoryUnit.BYTES: "bytes",
            MemoryUnit.KB: "KB",
            MemoryUnit.MB: "MB",
            MemoryUnit.GB: "GB"
        }[unit]
        
        return {
            "current_usage": {
                "rss": current.rss / divisor,
                "vms": current.vms / divisor,
                "unit": unit_str
            },
            "max_usage": {
                "rss": max_usage.rss / divisor if max_usage else 0,
                "vms": max_usage.vms / divisor if max_usage else 0,
                "unit": unit_str
            } if max_usage else None,
            "system_memory": {
                "total": total_mem / divisor,
                "available": avail_mem / divisor,
                "unit": unit_str
            },
            "process_info": {
                "pid": current.pid,
                "num_threads": current.num_threads,
                "cpu_percent": current.cpu_percent
            }
        }
    
    def request_garbage_collection(self) -> Dict[str, Any]:
        """Request garbage collection and return statistics.
        
        Returns:
            Dictionary with garbage collection statistics
        """
        before = self.get_current_usage()
        
        # Collect garbage
        gc.collect()
        
        after = self.get_current_usage()
        
        return {
            "before_gc": {
                "rss_bytes": before.rss,
                "vms_bytes": before.vms
            },
            "after_gc": {
                "rss_bytes": after.rss,
                "vms_bytes": after.vms
            },
            "freed_bytes": {
                "rss": before.rss - after.rss,
                "vms": before.vms - after.vms
            },
            "objects_collected": gc.collect(),
            "timestamp": datetime.now().isoformat()
        }
    
    def __enter__(self):
        """Start monitoring on context enter."""
        self.start_monitoring()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop monitoring on context exit."""
        self.stop_monitoring()
        return False  # Don't suppress exceptions 