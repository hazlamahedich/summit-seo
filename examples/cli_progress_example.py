#!/usr/bin/env python3
"""Example demonstrating CLI progress display capabilities in Summit SEO."""

import asyncio
import logging
import sys
import time
from pathlib import Path
import random

# Add the parent directory to sys.path to import summit_seo package
sys.path.append(str(Path(__file__).resolve().parent.parent))

from summit_seo.progress import (
    SimpleProgressTracker,
    AnalyzerProgressTracker, 
    ProgressStage,
    ProgressFactory
)
from summit_seo.cli import CLIProgressDisplay, DisplayStyle

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def simulate_progress(tracker, delay_factor=1.0):
    """Simulate progress for demonstration."""
    tracker.start()
    
    # Initialization stage
    tracker.set_stage(ProgressStage.INITIALIZATION, 0.0)
    await asyncio.sleep(0.5 * delay_factor)
    
    for i in range(1, 11):
        tracker.update_stage_progress(i / 10)
        await asyncio.sleep(0.2 * delay_factor)
    
    # Collection stage
    tracker.set_stage(ProgressStage.COLLECTION, 0.0)
    await asyncio.sleep(0.3 * delay_factor)
    
    for i in range(1, 11):
        tracker.update_stage_progress(i / 10)
        
        # Add a message occasionally
        if i % 3 == 0:
            tracker.increment(0, f"Collected {i * 10}% of data")
            
        await asyncio.sleep(0.3 * delay_factor)
    
    # Processing stage
    tracker.set_stage(ProgressStage.PROCESSING, 0.0)
    await asyncio.sleep(0.2 * delay_factor)
    
    for i in range(1, 11):
        tracker.update_stage_progress(i / 10)
        
        # Simulate an error
        if i == 5:
            tracker._add_error("Temporary network error occurred")
        
        await asyncio.sleep(0.2 * delay_factor)
    
    # Analysis stage
    tracker.set_stage(ProgressStage.ANALYSIS, 0.0)
    await asyncio.sleep(0.3 * delay_factor)
    
    for i in range(1, 11):
        tracker.update_stage_progress(i / 10)
        await asyncio.sleep(0.4 * delay_factor)
    
    # Reporting stage
    tracker.set_stage(ProgressStage.REPORTING, 0.0)
    await asyncio.sleep(0.2 * delay_factor)
    
    for i in range(1, 11):
        tracker.update_stage_progress(i / 10)
        await asyncio.sleep(0.2 * delay_factor)
    
    # Cleanup stage
    tracker.set_stage(ProgressStage.CLEANUP, 0.0)
    await asyncio.sleep(0.1 * delay_factor)
    
    for i in range(1, 11):
        tracker.update_stage_progress(i / 10)
        await asyncio.sleep(0.1 * delay_factor)
    
    # Complete
    tracker.complete()


async def demonstrate_minimal_style():
    """Demonstrate minimal progress display style."""
    print("\n=== Minimal Progress Display Style ===\n")
    
    # Create a progress tracker
    tracker = SimpleProgressTracker(name="Minimal Progress Demo")
    
    # Create progress display
    display = CLIProgressDisplay(
        tracker=tracker,
        style=DisplayStyle.MINIMAL,
        refresh_rate=0.1,
        bar_width=30
    )
    
    # Start display
    await display.start()
    
    # Simulate progress
    await simulate_progress(tracker, delay_factor=0.5)
    
    # Stop display
    await display.stop()
    
    print("\nMinimal style demonstration completed.\n")


async def demonstrate_detailed_style():
    """Demonstrate detailed progress display style."""
    print("\n=== Detailed Progress Display Style ===\n")
    
    # Create a progress tracker
    tracker = SimpleProgressTracker(name="Detailed Progress Demo")
    
    # Create progress display
    display = CLIProgressDisplay(
        tracker=tracker,
        style=DisplayStyle.DETAILED,
        refresh_rate=0.1
    )
    
    # Start display
    await display.start()
    
    # Simulate progress
    await simulate_progress(tracker, delay_factor=0.5)
    
    # Stop display
    await display.stop()
    
    print("\nDetailed style demonstration completed.\n")


async def demonstrate_animated_style():
    """Demonstrate animated progress display style."""
    print("\n=== Animated Progress Display Style ===\n")
    
    # Create a progress tracker
    tracker = SimpleProgressTracker(name="Animated Progress Demo")
    
    # Create progress display
    display = CLIProgressDisplay(
        tracker=tracker,
        style=DisplayStyle.ANIMATED,
        refresh_rate=0.1,
        bar_width=40
    )
    
    # Start display
    await display.start()
    
    # Simulate progress
    await simulate_progress(tracker, delay_factor=0.5)
    
    # Stop display
    await display.stop()
    
    print("\nAnimated style demonstration completed.\n")


async def demonstrate_compact_style():
    """Demonstrate compact progress display style."""
    print("\n=== Compact Progress Display Style ===\n")
    
    # Create a progress tracker
    tracker = SimpleProgressTracker(name="Compact Progress Demo")
    
    # Create progress display
    display = CLIProgressDisplay(
        tracker=tracker,
        style=DisplayStyle.COMPACT,
        refresh_rate=0.1
    )
    
    # Start display
    await display.start()
    
    # Simulate progress
    await simulate_progress(tracker, delay_factor=0.5)
    
    # Stop display
    await display.stop()
    
    print("\nCompact style demonstration completed.\n")


async def demonstrate_analyzer_progress():
    """Demonstrate analyzer progress display."""
    print("\n=== Analyzer Progress Display ===\n")
    
    # Create an analyzer progress tracker
    tracker = AnalyzerProgressTracker(name="Multi-Analyzer Progress Demo")
    
    # Register analyzers with different weights
    analyzers = [
        ("ContentAnalyzer", 2.0),
        ("LinkAnalyzer", 1.0),
        ("SecurityAnalyzer", 1.5),
        ("MetaAnalyzer", 1.0),
        ("MobileFriendlyAnalyzer", 1.2),
        ("PerformanceAnalyzer", 1.8)
    ]
    
    for name, weight in analyzers:
        tracker.register_analyzer(name, weight)
    
    # Create progress display
    display = CLIProgressDisplay(
        tracker=tracker,
        style=DisplayStyle.ANIMATED,
        refresh_rate=0.1
    )
    
    # Start tracking and display
    tracker.start()
    await display.start()
    
    # Simulate each analyzer's progress
    for stage in [ProgressStage.INITIALIZATION, ProgressStage.COLLECTION, 
                  ProgressStage.PROCESSING, ProgressStage.ANALYSIS]:
        
        tracker.set_stage(stage, 0.0)
        await asyncio.sleep(0.5)
        
        # Update each analyzer's progress
        for step in range(1, 11):
            for name, _ in analyzers:
                # Random progress that increases over time
                progress = min(1.0, (step / 10) + random.uniform(-0.1, 0.1))
                tracker.set_analyzer_progress(name, progress)
                
                # Add occasional metrics
                if step == 5:
                    tracker.set_analyzer_metrics(name, {
                        "issues_found": random.randint(0, 10),
                        "warnings": random.randint(0, 5),
                        "score": random.randint(50, 100)
                    })
            
            tracker.update_stage_progress(step / 10)
            await asyncio.sleep(0.3)
    
    # Final stages
    for stage in [ProgressStage.REPORTING, ProgressStage.CLEANUP]:
        tracker.set_stage(stage, 0.0)
        
        for step in range(1, 11):
            tracker.update_stage_progress(step / 10)
            await asyncio.sleep(0.2)
    
    # Complete the tracking
    tracker.complete()
    
    # Stop display
    await display.stop()
    
    print("\nAnalyzer progress demonstration completed.\n")


async def main():
    """Run the CLI progress display examples."""
    logger.info("Starting CLI progress display examples")
    
    try:
        # Demonstrate different styles
        await demonstrate_minimal_style()
        await demonstrate_compact_style()
        await demonstrate_detailed_style()
        await demonstrate_animated_style()
        
        # Demonstrate analyzer progress tracking
        await demonstrate_analyzer_progress()
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user.")
    except Exception as e:
        logger.exception(f"Error in examples: {e}")
    
    logger.info("Completed CLI progress display examples")


if __name__ == "__main__":
    asyncio.run(main()) 