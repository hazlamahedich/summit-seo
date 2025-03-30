#!/usr/bin/env python3
"""
Memory Optimization Example for Summit SEO

This example demonstrates the memory optimization features in Summit SEO,
including monitoring, optimization, and limiting memory usage.
"""

import asyncio
import logging
import sys
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from summit_seo.memory import (
    MemoryLimiter, MemoryMonitor, MemoryOptimizer, MemoryThreshold, MemoryUnit,
    OptimizationConfig, OptimizationLevel, OptimizationStrategy, Profiler, ProfilerConfig
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("memory_example")


# Example classes for optimization
@dataclass
class SampleData:
    """Sample data class for optimization demonstration."""
    id: int
    name: str
    values: List[float] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)


class DataProcessor:
    """Sample data processor for optimization demonstration."""
    
    def __init__(self, capacity: int = 1000):
        self.cache = {}
        self.capacity = capacity
        self.processed_count = 0
        
    def process(self, data: SampleData) -> Dict:
        """Process the data."""
        # Check cache
        if data.id in self.cache:
            return self.cache[data.id]
            
        # Simulate processing
        result = {
            "id": data.id,
            "name_length": len(data.name),
            "avg_value": sum(data.values) / max(1, len(data.values)),
            "metadata_keys": list(data.metadata.keys())
        }
        
        # Cache result
        if len(self.cache) < self.capacity:
            self.cache[data.id] = result
            
        self.processed_count += 1
        return result


async def demonstrate_memory_monitor():
    """Demonstrate memory monitoring."""
    logger.info("=== Memory Monitor Demonstration ===")
    
    # Create a memory monitor
    monitor = MemoryMonitor(poll_interval=0.1)
    
    # Start monitoring
    monitor.start_monitoring()
    
    try:
        # Create some memory pressure
        logger.info("Creating memory pressure...")
        data = []
        for i in range(5):
            # Allocate 1MB of data
            chunk = [0] * (1024 * 1024 // 8)  # 1MB in 64-bit integers
            data.append(chunk)
            
            # Get current usage
            usage = monitor.get_current_usage()
            logger.info(f"Memory usage after allocation #{i+1}: {usage.get_rss(MemoryUnit.MB):.2f} MB")
            
            # Wait a bit for monitoring
            await asyncio.sleep(0.2)
            
        # Get memory usage summary
        summary = monitor.get_usage_summary()
        logger.info(f"Memory usage summary:")
        logger.info(f"  Current: {summary['current']['rss_mb']:.2f} MB")
        logger.info(f"  Peak: {summary['max']['rss_mb']:.2f} MB")
        logger.info(f"  Average: {summary['avg']['rss_mb']:.2f} MB")
        logger.info(f"  Samples: {summary['samples']}")
        
        # Force garbage collection
        collected = monitor.force_garbage_collection()
        logger.info(f"Forced garbage collection: {collected} objects collected")
        
        # After cleanup
        usage = monitor.get_current_usage()
        logger.info(f"Memory usage after cleanup: {usage.get_rss(MemoryUnit.MB):.2f} MB")
        
    finally:
        # Stop monitoring
        monitor.stop_monitoring()


async def demonstrate_memory_profiler():
    """Demonstrate memory profiling."""
    logger.info("\n=== Memory Profiler Demonstration ===")
    
    # Create a profiler
    config = ProfilerConfig(
        trace_lines=False,
        trace_alloc=True,
        capture_profile=True,
        capture_traceback=True,
        max_frames=10,
        monitor_memory=True
    )
    profiler = Profiler(config)
    
    # Define a function to profile
    def memory_intensive_function():
        """A function that uses memory."""
        # Allocate memory
        data = []
        for i in range(5):
            chunk = [0] * (1024 * 1024 // 8)  # 1MB in 64-bit integers
            data.append(chunk)
            time.sleep(0.1)
        return len(data)
    
    # Profile the function
    with profiler.profile_block("memory_intensive_function") as profile_result:
        result = memory_intensive_function()
        
    # Show profiling results
    logger.info(f"Function result: {result}")
    logger.info(f"Profiling results:")
    logger.info(f"  Duration: {profile_result.duration:.2f} seconds")
    
    if profile_result.memory_before and profile_result.memory_after:
        mb_before = profile_result.memory_before.get_rss(MemoryUnit.MB)
        mb_after = profile_result.memory_after.get_rss(MemoryUnit.MB)
        mb_diff = mb_after - mb_before
        logger.info(f"  Memory before: {mb_before:.2f} MB")
        logger.info(f"  Memory after: {mb_after:.2f} MB")
        logger.info(f"  Memory diff: {mb_diff:.2f} MB")
        
    if profile_result.peak_memory:
        peak_mb = profile_result.peak_memory.get_rss(MemoryUnit.MB)
        logger.info(f"  Peak memory: {peak_mb:.2f} MB")
        
    if profile_result.memory_diff is not None:
        tracemalloc_mb = profile_result.memory_diff / (1024 * 1024)
        logger.info(f"  Tracemalloc memory diff: {tracemalloc_mb:.2f} MB")
        
    # Use profiler as a decorator
    @profiler.profile_function
    def another_function(size):
        """Another function to profile."""
        return [0] * size
        
    # Call the decorated function
    result = another_function(1000000)
    logger.info(f"Decorated function result length: {len(result)}")


async def demonstrate_memory_limiter():
    """Demonstrate memory limiting."""
    logger.info("\n=== Memory Limiter Demonstration ===")
    
    # Create a memory monitor and limiter
    monitor = MemoryMonitor(poll_interval=0.1)
    limiter = MemoryLimiter(monitor=monitor)
    
    # Add memory thresholds
    # These are set low for demonstration purposes
    # In a real application, you'd set them based on available system memory
    current_usage = monitor.get_current_usage().get_rss(MemoryUnit.MB)
    
    # Warning threshold at current + 20MB
    limiter.add_threshold(
        limit=current_usage + 20,
        action="warn",
        limit_unit=MemoryUnit.MB,
        description="Warning threshold"
    )
    
    # GC threshold at current + 40MB
    limiter.add_threshold(
        limit=current_usage + 40,
        action="gc",
        limit_unit=MemoryUnit.MB,
        description="GC threshold"
    )
    
    # Throttle threshold at current + 60MB
    limiter.add_threshold(
        limit=current_usage + 60,
        action="throttle",
        limit_unit=MemoryUnit.MB,
        description="Throttle threshold"
    )
    
    # Start monitoring and limiting
    monitor.start_monitoring()
    limiter.start()
    
    try:
        # Create some memory pressure
        logger.info("Creating memory pressure to trigger thresholds...")
        data = []
        
        for i in range(10):
            # Allocate memory
            chunk = [0] * (10 * 1024 * 1024 // 8)  # 10MB in 64-bit integers
            data.append(chunk)
            
            # Get current usage
            usage = monitor.get_current_usage()
            logger.info(f"Memory usage after allocation #{i+1}: {usage.get_rss(MemoryUnit.MB):.2f} MB")
            
            # Check if throttling is active
            if limiter.should_throttle():
                throttle_factor = limiter.get_throttle_factor()
                logger.info(f"Throttling active with factor: {throttle_factor:.2f}")
                
                # Apply throttling by sleeping
                await limiter.throttle_if_needed()
            
            # Sleep a bit
            await asyncio.sleep(0.2)
            
    except Exception as e:
        logger.error(f"Error during memory pressure test: {e}")
        
    finally:
        # Stop monitoring and limiting
        limiter.stop()
        monitor.stop_monitoring()
        
        # Clear data
        data.clear()
        

async def demonstrate_memory_optimizer():
    """Demonstrate memory optimization."""
    logger.info("\n=== Memory Optimizer Demonstration ===")
    
    # Create a memory optimizer
    config = OptimizationConfig(
        level=OptimizationLevel.AGGRESSIVE,
        max_collection_size=1000,
        pool_size=50,
        cache_size=100,
        auto_monitor=True,
        auto_limit=False
    )
    optimizer = MemoryOptimizer(config=config)
    
    # Optimize a class
    logger.info("Optimizing SampleData class...")
    OptimizedSampleData = optimizer.optimize_class(
        SampleData,
        strategies=[
            OptimizationStrategy.SLOTS,
            OptimizationStrategy.CACHING
        ]
    )
    
    # Optimize another class
    logger.info("Optimizing DataProcessor class...")
    OptimizedDataProcessor = optimizer.optimize_class(
        DataProcessor,
        strategies=[
            OptimizationStrategy.POOLING,
            OptimizationStrategy.CACHING
        ]
    )
    
    # Create instances and use them
    logger.info("Creating and using optimized classes...")
    
    with optimizer.monitor_operation("data_processing") as op:
        processor = OptimizedDataProcessor()
        
        data_list = []
        results = []
        
        # Create and process data
        for i in range(100):
            data = OptimizedSampleData(
                id=i,
                name=f"Sample-{i}",
                values=[float(j) for j in range(10)],
                metadata={"key": f"value-{i}"}
            )
            data_list.append(data)
            
            # Process the data
            result = processor.process(data)
            results.append(result)
            
            # Process it again (should use cache)
            result2 = processor.process(data)
            
        # Optimize collections
        optimizer.optimize_collections([data_list, results])
        
        # Get usage summary
        logger.info(f"Operation usage: {op.get_usage_summary()}")
    
    # Check processor cache
    logger.info(f"Processor processed count: {processor.processed_count}")
    logger.info(f"Processor cache size: {len(processor.cache)}")
    
    # Get memory intensive objects
    logger.info("Finding memory intensive objects...")
    top_objects = optimizer.find_memory_intensive_objects(top_n=5)
    
    for i, obj_info in enumerate(top_objects):
        logger.info(f"Memory object #{i+1}: {obj_info['type']} - {obj_info['size_human']}")
        
    # Get optimization report
    logger.info("Generating optimization report...")
    report = optimizer.get_optimization_report()
    
    logger.info(f"Optimization level: {report['config']['level']}")
    logger.info(f"Optimized classes: {len(report['optimized_classes'])}")
    
    # Force memory optimization
    logger.info("Forcing memory optimization...")
    optimizer.optimize_memory_usage(aggressive=True)


async def main():
    """Run all demonstrations."""
    # Print Python version
    logger.info(f"Python version: {sys.version}")
    
    # Run demonstrations
    await demonstrate_memory_monitor()
    await demonstrate_memory_profiler()
    await demonstrate_memory_limiter()
    await demonstrate_memory_optimizer()
    
    logger.info("\nAll demonstrations completed!")


if __name__ == "__main__":
    asyncio.run(main()) 