#!/usr/bin/env python3
"""
Memory-Optimized Parallel Processing Example for Summit SEO

This example demonstrates how to integrate the memory optimization features
with parallel processing to create an efficient and resource-aware analysis pipeline.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional

from summit_seo.analyzer import AnalyzerFactory
from summit_seo.collector import CollectorFactory
from summit_seo.memory import (
    MemoryLimiter, MemoryMonitor, MemoryOptimizer, MemoryUnit,
    OptimizationConfig, OptimizationLevel, OptimizationStrategy
)
from summit_seo.parallel import (
    ParallelManager, ProcessingStrategy, Task, TaskPriority, TaskStatus
)
from summit_seo.processor import ProcessorFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("memory_parallel_example")


async def setup_memory_optimized_environment():
    """Set up memory monitoring and optimization environment."""
    # Create a memory monitor to track resource usage
    monitor = MemoryMonitor(poll_interval=1.0)
    
    # Start monitoring memory usage
    monitor.start_monitoring()
    
    # Create a memory limiter with thresholds
    limiter = MemoryLimiter(monitor=monitor)
    
    # Add warning threshold at 70% of available memory
    limiter.add_threshold(
        limit=70, 
        action="warn",
        limit_unit=MemoryUnit.PERCENT,
        description="Memory usage above 70%"
    )
    
    # Add garbage collection threshold at 80%
    limiter.add_threshold(
        limit=80, 
        action="gc",
        limit_unit=MemoryUnit.PERCENT,
        description="Memory usage above 80%, run garbage collection"
    )
    
    # Add throttling threshold at 90%
    limiter.add_threshold(
        limit=90, 
        action="throttle",
        limit_unit=MemoryUnit.PERCENT,
        description="Memory usage above 90%, throttle processing"
    )
    
    # Start memory limiting
    limiter.start()
    
    # Create memory optimizer with moderate optimization level
    optimizer = MemoryOptimizer(
        config=OptimizationConfig(
            level=OptimizationLevel.MODERATE,
            auto_monitor=False,  # We're using our custom monitor
            auto_limit=False,    # We're using our custom limiter
            max_collection_size=5000,
            cache_size=1000
        ),
        monitor=monitor,
        limiter=limiter
    )
    
    # Log initial memory usage
    usage = monitor.get_current_usage()
    logger.info(f"Initial memory usage: {usage.get_rss(MemoryUnit.MB):.2f} MB")
    
    return monitor, limiter, optimizer


async def memory_aware_task_callback(task_id: str, status: TaskStatus, result=None, error=None):
    """Task callback that checks memory usage and applies throttling if needed."""
    if status == TaskStatus.RUNNING:
        logger.info(f"Task {task_id} is running...")
    elif status == TaskStatus.COMPLETED:
        logger.info(f"Task {task_id} completed successfully")
    elif status == TaskStatus.FAILED:
        logger.error(f"Task {task_id} failed with error: {error}")
    elif status == TaskStatus.CANCELLED:
        logger.warning(f"Task {task_id} was cancelled")


async def analyze_url_with_memory_optimization(
    url: str,
    analyzers: List[str],
    parallel_manager: ParallelManager,
    memory_optimizer: MemoryOptimizer
):
    """Analyze a URL with memory optimization and parallel processing."""
    # Create collector, processor, and analyzers
    collector = CollectorFactory.create("url")
    processor = ProcessorFactory.create("html")
    analyzer_instances = [AnalyzerFactory.create(name) for name in analyzers]
    
    # Apply memory optimization to all components
    with memory_optimizer.monitor_operation(f"analyze_{url}") as op:
        try:
            # Create collection task
            collection_task = Task(
                id=f"collect_{url}",
                coro=collector.collect(url),
                name=f"Collecting {url}",
                priority=TaskPriority.HIGH
            )
            
            # Submit collection task and wait for its completion
            collection_result = await parallel_manager.submit_and_await(collection_task)
            
            # If throttling is necessary, wait for a bit
            await memory_optimizer.limiter.throttle_if_needed()
            
            # Create processing task
            process_task = Task(
                id=f"process_{url}",
                coro=processor.process(collection_result),
                name=f"Processing {url}",
                priority=TaskPriority.MEDIUM,
                dependencies=[collection_task.id]
            )
            
            # Submit processing task and wait for its completion
            processing_result = await parallel_manager.submit_and_await(process_task)
            
            # Create analyzer tasks
            analyzer_tasks = []
            for idx, analyzer in enumerate(analyzer_instances):
                # Optimize each analyzer class
                optimized_analyzer = memory_optimizer.optimize_class(
                    analyzer.__class__,
                    strategies=[
                        OptimizationStrategy.CACHING,
                        OptimizationStrategy.SLOTS
                    ]
                )
                
                # Create task for this analyzer
                analyzer_task = Task(
                    id=f"analyze_{analyzer.__class__.__name__.lower()}_{url}",
                    coro=analyzer.analyze(processing_result),
                    name=f"Analyzing {url} with {analyzer.__class__.__name__}",
                    priority=TaskPriority.NORMAL,
                    dependencies=[process_task.id]
                )
                analyzer_tasks.append(analyzer_task)
            
            # Submit all analyzer tasks and wait for their completion
            analysis_results = await parallel_manager.submit_and_await_many(analyzer_tasks)
            
            # Apply optimization to results collections
            memory_optimizer.optimize_collections([collection_result, processing_result, analysis_results])
            
            # Force memory optimization after all tasks
            memory_optimizer.optimize_memory_usage()
            
            # Return compiled results
            compiled_results = {
                "url": url,
                "analyzers": {
                    analyzer.__class__.__name__: result
                    for analyzer, result in zip(analyzer_instances, analysis_results)
                }
            }
            
            return compiled_results
            
        except Exception as e:
            logger.error(f"Error analyzing {url}: {e}")
            # Force aggressive memory optimization on error
            memory_optimizer.optimize_memory_usage(aggressive=True)
            return {"url": url, "error": str(e)}
        
        finally:
            # Log memory usage for this operation
            logger.info(f"Memory usage for {url}: {op.get_usage_summary()}")


async def main():
    """Run the memory-optimized parallel processing example."""
    logger.info("Starting memory-optimized parallel processing example")
    
    # Set up memory optimization environment
    memory_monitor, memory_limiter, memory_optimizer = await setup_memory_optimized_environment()
    
    try:
        # Create parallel processing manager
        parallel_manager = ParallelManager(
            max_workers=4,
            strategy=ProcessingStrategy.PRIORITY_GRAPH,
            task_callback=memory_aware_task_callback
        )
        
        # URLs to analyze
        urls = [
            "https://www.example.com",
            "https://www.python.org",
            "https://www.wikipedia.org",
            "https://www.github.com",
            "https://www.mozilla.org"
        ]
        
        # Analyzers to use
        analyzers = [
            "security",
            "performance",
            "accessibility",
            "mobilefriendly"
        ]
        
        # Start parallel manager
        await parallel_manager.start()
        
        logger.info(f"Analyzing {len(urls)} URLs with {len(analyzers)} analyzers")
        
        # Process each URL with memory optimization
        tasks = []
        for url in urls:
            task = analyze_url_with_memory_optimization(
                url=url,
                analyzers=analyzers,
                parallel_manager=parallel_manager,
                memory_optimizer=memory_optimizer
            )
            tasks.append(task)
        
        # Wait for all analysis tasks to complete
        results = await asyncio.gather(*tasks)
        
        # Log summary
        logger.info(f"Completed analysis of {len(urls)} URLs")
        
        # Display memory usage statistics
        memory_summary = memory_monitor.get_usage_summary()
        logger.info("Memory usage summary:")
        logger.info(f"  Peak: {memory_summary['max']['rss_mb']:.2f} MB")
        logger.info(f"  Average: {memory_summary['avg']['rss_mb']:.2f} MB")
        logger.info(f"  Current: {memory_summary['current']['rss_mb']:.2f} MB")
        
        # Get optimization report
        optimization_report = memory_optimizer.get_optimization_report()
        logger.info(f"Optimized {len(optimization_report['optimized_classes'])} classes")
        
        # Get parallel processing statistics
        parallel_stats = parallel_manager.get_statistics()
        logger.info("Parallel processing statistics:")
        logger.info(f"  Tasks completed: {parallel_stats.completed}")
        logger.info(f"  Tasks failed: {parallel_stats.failed}")
        logger.info(f"  Average task duration: {parallel_stats.avg_duration:.2f}s")
        logger.info(f"  Peak concurrent tasks: {parallel_stats.max_concurrent}")
        
        # Stop parallel manager
        await parallel_manager.stop()
        
    finally:
        # Cleanup resources
        memory_limiter.stop()
        memory_monitor.stop_monitoring()
        
        logger.info("Memory-optimized parallel processing example completed")


if __name__ == "__main__":
    asyncio.run(main()) 