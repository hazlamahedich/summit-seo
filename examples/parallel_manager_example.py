#!/usr/bin/env python
"""Example demonstrating the parallel processing capabilities of Summit SEO."""

import asyncio
import logging
import sys
import time
from typing import Dict, List, Optional, Any

from summit_seo import (
    AnalyzerFactory,
    CollectorFactory,
    ProcessorFactory,
    ParallelManager,
    ProcessingStrategy,
    TaskStatus
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("parallel_example")


async def analyze_url(url: str, analyzers: Optional[List[str]] = None) -> Dict[str, Any]:
    """Analyze a URL with specified or all analyzers.
    
    Args:
        url: The URL to analyze.
        analyzers: List of analyzer names to use or None for all.
        
    Returns:
        Dictionary with analysis results.
    """
    logger.info(f"Starting analysis of {url}")
    
    try:
        # Collect data
        collector = CollectorFactory.create('webpage', {})
        collection_result = await collector.collect(url)
        
        # Process data
        processor = ProcessorFactory.create('html', {})
        processing_result = await processor.process(
            {'html_content': collection_result.content},
            url
        )
        
        # Run analyzers
        results = {}
        available_analyzers = AnalyzerFactory.get_registered_analyzers()
        selected_analyzers = analyzers or available_analyzers.keys()
        
        for name in selected_analyzers:
            if name not in available_analyzers:
                logger.warning(f"Analyzer '{name}' not found, skipping")
                continue
            
            analyzer = AnalyzerFactory.create(name, {})
            analysis_result = await analyzer.analyze(processing_result.processed_data)
            results[name] = analysis_result.to_dict()
        
        logger.info(f"Completed analysis of {url}")
        return {
            'url': url,
            'timestamp': collection_result.timestamp.isoformat(),
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Error analyzing {url}: {str(e)}")
        raise


async def analyze_urls_in_parallel(urls: List[str], max_workers: int = 4) -> List[Dict[str, Any]]:
    """Analyze multiple URLs in parallel using the ParallelManager.
    
    Args:
        urls: List of URLs to analyze.
        max_workers: Maximum number of concurrent workers.
        
    Returns:
        List of analysis results.
    """
    # Create and start the ParallelManager
    async with ParallelManager(
        num_workers=max_workers,
        max_tasks_per_worker=1,  # One task per worker
        executor_type='thread',   # Thread-based execution
        strategy=ProcessingStrategy.BATCHED,  # Process in batches
        batch_size=min(10, max_workers)  # Reasonable batch size
    ) as manager:
        # Submit all URL analysis tasks
        tasks = []
        for url in urls:
            task = await manager.submit(
                analyze_url,     # Function to execute
                url,             # URL to analyze
                None,            # Use all analyzers
                name=f"analyze-{url}",  # Task name
                max_retries=1    # Retry once on failure
            )
            tasks.append(task)
            
        # Process tasks until all complete
        total = len(tasks)
        while any(task.status == TaskStatus.PENDING for task in tasks):
            # Process a batch of tasks
            batch_results = await manager.process_tasks()
            
            # Report progress
            completed = sum(1 for task in tasks if task.status == TaskStatus.COMPLETED)
            failed = sum(1 for task in tasks if task.status == TaskStatus.FAILED)
            running = sum(1 for task in tasks if task.status == TaskStatus.RUNNING)
            
            logger.info(f"Progress: {completed}/{total} completed, {failed}/{total} failed, {running}/{total} running")
        
        # Collect results
        results = []
        for task in tasks:
            if task.result and task.result.succeeded:
                # Task completed successfully
                results.append(task.result.result)
            elif task.result and task.result.failed:
                # Task failed
                logger.error(f"Error analyzing {task.name}: {str(task.result.error)}")
                results.append({
                    'url': task.name.replace('analyze-', ''),
                    'error': str(task.result.error) if task.result and task.result.error else "Unknown error"
                })
            else:
                # Task didn't complete (should not happen if we've waited for all tasks)
                results.append({
                    'url': task.name.replace('analyze-', ''),
                    'error': "Task did not complete"
                })
        
        # Report statistics
        stats = manager.get_stats()
        logger.info(f"Processing complete: {stats['completed_task_count']} succeeded, "
                   f"{stats['failed_task_count']} failed")
        logger.info(f"Processing time: {stats['uptime_seconds']:.2f} seconds "
                   f"({stats['tasks_per_second']:.2f} tasks/second)")
        
        return results


async def demonstrate_strategies() -> None:
    """Demonstrate different processing strategies with simple tasks."""
    logger.info("Demonstrating different processing strategies")
    
    # A simple task that sleeps for a specified time
    async def simple_task(task_id: int, sleep_time: float) -> Dict[str, Any]:
        logger.info(f"Starting task {task_id}")
        await asyncio.sleep(sleep_time)
        logger.info(f"Completed task {task_id}")
        return {'task_id': task_id, 'sleep_time': sleep_time}
    
    # 1. Parallel Strategy
    logger.info("\n=== Parallel Strategy ===")
    async with ParallelManager(strategy=ProcessingStrategy.PARALLEL) as manager:
        # Submit 5 tasks with different execution times
        tasks = []
        for i in range(5):
            tasks.append(await manager.submit(simple_task, i, 0.5))
        
        # Process all tasks in parallel
        results = await manager.process_tasks()
        logger.info(f"Processed {len(results)} tasks in parallel")
    
    # 2. Batched Strategy
    logger.info("\n=== Batched Strategy ===")
    async with ParallelManager(
        strategy=ProcessingStrategy.BATCHED,
        batch_size=2
    ) as manager:
        # Submit 5 tasks
        for i in range(5):
            await manager.submit(simple_task, i, 0.5)
        
        # Process in batches of 2
        results = await manager.process_tasks()
        logger.info(f"Processed {len(results)} tasks in batches")
    
    # 3. Priority Strategy
    logger.info("\n=== Priority Strategy ===")
    async with ParallelManager(strategy=ProcessingStrategy.PRIORITY) as manager:
        # Submit tasks with different priorities
        await manager.submit(simple_task, 1, 0.5, priority=1, name="Low Priority")
        await manager.submit(simple_task, 2, 0.5, priority=3, name="High Priority")
        await manager.submit(simple_task, 3, 0.5, priority=2, name="Medium Priority")
        
        # Process in priority order
        results = await manager.process_tasks()
        logger.info(f"Processed {len(results)} tasks by priority")
    
    # 4. Dependency Graph Strategy
    logger.info("\n=== Dependency Graph Strategy ===")
    async with ParallelManager(strategy=ProcessingStrategy.DEPENDENCY_GRAPH) as manager:
        # Create tasks with dependencies
        task1 = await manager.submit(simple_task, 1, 0.5, name="Task 1")
        task2 = await manager.submit(simple_task, 2, 0.5, name="Task 2")
        
        # Task 3 depends on task1 and task2
        task3 = await manager.submit(
            simple_task, 3, 0.5,
            dependencies=[task1, task2],
            name="Task 3 (depends on 1,2)"
        )
        
        # Task 4 depends on task3
        task4 = await manager.submit(
            simple_task, 4, 0.5,
            dependencies=[task3],
            name="Task 4 (depends on 3)"
        )
        
        # Process respecting dependencies
        while any(task.status == TaskStatus.PENDING for task in [task1, task2, task3, task4]):
            results = await manager.process_tasks()
            logger.info(f"Processed a level of tasks: {len(results)} tasks")
        
        logger.info("All tasks in dependency graph processed")


async def main() -> None:
    """Run the parallel processing examples."""
    
    # Demonstrate different processing strategies
    await demonstrate_strategies()
    
    # Analyze a list of URLs in parallel
    urls = [
        "https://www.example.com",
        "https://www.google.com",
        "https://www.github.com",
        "https://www.python.org",
        "https://www.mozilla.org"
    ]
    
    logger.info("\n=== Analyzing URLs in Parallel ===")
    results = await analyze_urls_in_parallel(urls, max_workers=2)
    logger.info(f"Analyzed {len(results)} URLs")
    
    # Print summary of results
    for result in results:
        if 'error' in result:
            logger.info(f"URL: {result['url']} - Error: {result['error']}")
        else:
            analyzers = list(result['results'].keys())
            logger.info(f"URL: {result['url']} - Analyzed with {len(analyzers)} analyzers")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 