#!/usr/bin/env python3
"""Example demonstrating progress tracking functionality.

This script shows how to use the progress tracking module
to monitor and visualize analysis progress.
"""

import os
import sys
import time
import asyncio
import random
from datetime import datetime
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from summit_seo.progress import (
    ProgressFactory,
    ProgressState,
    ProgressStage,
    ProgressError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("progress_example")

# Sample analyzers for demonstration
SAMPLE_ANALYZERS = [
    "ContentAnalyzer",
    "MetaAnalyzer",
    "SecurityAnalyzer",
    "PerformanceAnalyzer",
    "AccessibilityAnalyzer",
    "MobileFriendlyAnalyzer",
    "SchemaAnalyzer",
    "SocialMediaAnalyzer",
    "TitleAnalyzer",
    "ImageAnalyzer"
]

async def simulate_analysis_with_simple_tracker():
    """Simulate analysis with SimpleProgressTracker."""
    logger.info("Starting analysis simulation with SimpleProgressTracker")
    
    # Create a progress tracker
    tracker = ProgressFactory.create("simple", total_steps=100, name="SEO Analysis")
    
    # Start tracking
    tracker.start()
    
    # Simulate initialization stage
    tracker.set_stage(ProgressStage.INITIALIZATION)
    for i in range(5):
        tracker.update_stage_progress(i / 4)
        print(f"\rInitialization: {i+1}/5 steps completed", end="")
        time.sleep(0.5)
    print()
    
    # Simulate collection stage
    tracker.set_stage(ProgressStage.COLLECTION, 0.0)
    for i in range(10):
        tracker.update_stage_progress(i / 9)
        print(f"\rCollection: {i+1}/10 steps completed", end="")
        time.sleep(0.2)
    print()
    
    # Simulate processing stage
    tracker.set_stage(ProgressStage.PROCESSING, 0.0)
    for i in range(20):
        tracker.update_stage_progress(i / 19)
        print(f"\rProcessing: {i+1}/20 steps completed", end="")
        time.sleep(0.1)
    print()
    
    # Simulate analysis stage
    tracker.set_stage(ProgressStage.ANALYSIS, 0.0)
    for i in range(40):
        tracker.update_stage_progress(i / 39)
        if i % 10 == 0:
            print("\nCurrent progress visualization:")
            print(tracker.visualize("text"))
        time.sleep(0.1)
    print()
    
    # Simulate reporting stage
    tracker.set_stage(ProgressStage.REPORTING, 0.0)
    for i in range(15):
        tracker.update_stage_progress(i / 14)
        print(f"\rReporting: {i+1}/15 steps completed", end="")
        time.sleep(0.2)
    print()
    
    # Simulate cleanup stage
    tracker.set_stage(ProgressStage.CLEANUP, 0.0)
    for i in range(5):
        tracker.update_stage_progress(i / 4)
        print(f"\rCleanup: {i+1}/5 steps completed", end="")
        time.sleep(0.3)
    print()
    
    # Complete tracking
    tracker.complete()
    
    # Display final progress
    print("\nFinal progress visualization:")
    print(tracker.visualize("text"))
    
    # Save HTML visualization to file
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    html_output = tracker.visualize("html")
    html_path = output_dir / "simple_progress.html"
    with open(html_path, "w") as f:
        f.write(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Progress Tracking - Simple</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .progress-tracker {{
                    margin: 20px;
                    padding: 15px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }}
                .card.active {{
                    border-color: #007bff;
                    border-width: 2px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="mt-4 mb-4">Progress Tracking Example - Simple Tracker</h1>
                {html_output}
            </div>
        </body>
        </html>
        """)
    
    logger.info(f"HTML visualization saved to {html_path}")
    
    return tracker

async def simulate_analysis_with_analyzer_tracker():
    """Simulate analysis with AnalyzerProgressTracker."""
    logger.info("Starting analysis simulation with AnalyzerProgressTracker")
    
    # Create a progress tracker
    tracker = ProgressFactory.create("analyzer", total_steps=100, name="SEO Analysis")
    
    # Register analyzers with different weights
    for analyzer in SAMPLE_ANALYZERS:
        # Assign higher weights to certain analyzers
        weight = 1.5 if analyzer in ["SecurityAnalyzer", "PerformanceAnalyzer"] else 1.0
        tracker.register_analyzer(analyzer, weight)
    
    # Start tracking
    tracker.start()
    
    # Simulate initialization stage
    tracker.set_stage(ProgressStage.INITIALIZATION)
    for i in range(5):
        tracker.update_stage_progress(i / 4)
        print(f"\rInitialization: {i+1}/5 steps completed", end="")
        time.sleep(0.3)
    print()
    
    # Simulate collection stage
    tracker.set_stage(ProgressStage.COLLECTION, 0.0)
    for i in range(10):
        tracker.update_stage_progress(i / 9)
        print(f"\rCollection: {i+1}/10 steps completed", end="")
        time.sleep(0.2)
    print()
    
    # Simulate processing stage
    tracker.set_stage(ProgressStage.PROCESSING, 0.0)
    for i in range(20):
        tracker.update_stage_progress(i / 19)
        print(f"\rProcessing: {i+1}/20 steps completed", end="")
        time.sleep(0.1)
    print()
    
    # Simulate analysis stage with individual analyzers
    tracker.set_stage(ProgressStage.ANALYSIS, 0.0)
    
    # Process each analyzer
    for analyzer in SAMPLE_ANALYZERS:
        # Simulate varying processing times
        steps = random.randint(5, 15)
        
        print(f"\nProcessing analyzer: {analyzer}")
        tracker.set_analyzer_progress(analyzer, 0.0, "Running")
        
        # Add random metrics
        metrics = {
            "issues_found": random.randint(0, 20),
            "warnings": random.randint(0, 10),
            "score": random.randint(50, 100),
            "processing_time": 0.0
        }
        tracker.set_analyzer_metrics(analyzer, metrics)
        
        # Process steps
        start_time = time.time()
        for step in range(steps):
            progress = (step + 1) / steps
            tracker.set_analyzer_progress(analyzer, progress, "Running")
            
            # Update metrics
            metrics["processing_time"] = round(time.time() - start_time, 2)
            tracker.set_analyzer_metrics(analyzer, metrics)
            
            print(f"\r  Step {step+1}/{steps} - {progress:.1%} complete", end="")
            time.sleep(random.uniform(0.1, 0.3))
        
        # Mark as complete
        tracker.set_analyzer_progress(analyzer, 1.0, "Completed")
        print(f"\r  Completed {analyzer}" + " " * 20)
        
        # Display current progress every few analyzers
        if SAMPLE_ANALYZERS.index(analyzer) % 3 == 2:
            print("\nCurrent progress visualization:")
            print(tracker.visualize("text"))
    
    # Simulate reporting stage
    tracker.set_stage(ProgressStage.REPORTING, 0.0)
    for i in range(15):
        tracker.update_stage_progress(i / 14)
        print(f"\rReporting: {i+1}/15 steps completed", end="")
        time.sleep(0.2)
    print()
    
    # Simulate cleanup stage
    tracker.set_stage(ProgressStage.CLEANUP, 0.0)
    for i in range(5):
        tracker.update_stage_progress(i / 4)
        print(f"\rCleanup: {i+1}/5 steps completed", end="")
        time.sleep(0.3)
    print()
    
    # Complete tracking
    tracker.complete()
    
    # Display final progress
    print("\nFinal progress visualization:")
    print(tracker.visualize("text"))
    
    # Save HTML visualization to file
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    html_output = tracker.visualize("html")
    html_path = output_dir / "analyzer_progress.html"
    with open(html_path, "w") as f:
        f.write(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Progress Tracking - Analyzer</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .progress-tracker {{
                    margin: 20px;
                    padding: 15px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }}
                .card.active {{
                    border-color: #007bff;
                    border-width: 2px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="mt-4 mb-4">Progress Tracking Example - Analyzer Tracker</h1>
                {html_output}
            </div>
        </body>
        </html>
        """)
    
    logger.info(f"HTML visualization saved to {html_path}")
    
    try:
        # Generate enhanced visualization with charts
        chart_html = await tracker.visualize_with_charts()
        chart_path = output_dir / "analyzer_progress_with_charts.html"
        with open(chart_path, "w") as f:
            f.write(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Progress Tracking - Analyzer with Charts</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    .progress-tracker {{
                        margin: 20px;
                        padding: 15px;
                        border-radius: 5px;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    }}
                    .card.active {{
                        border-color: #007bff;
                        border-width: 2px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 class="mt-4 mb-4">Progress Tracking Example - Analyzer with Charts</h1>
                    {chart_html}
                </div>
            </body>
            </html>
            """)
        
        logger.info(f"Enhanced HTML visualization saved to {chart_path}")
    except Exception as e:
        logger.error(f"Failed to generate visualization with charts: {e}")
    
    return tracker

async def main():
    """Main function to run the example."""
    # Create output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    logger.info("Starting progress tracking examples")
    
    # Simulate with simple tracker
    logger.info("Running example with SimpleProgressTracker")
    simple_tracker = await simulate_analysis_with_simple_tracker()
    
    # Pause between examples
    time.sleep(1)
    
    # Simulate with analyzer tracker
    logger.info("Running example with AnalyzerProgressTracker")
    analyzer_tracker = await simulate_analysis_with_analyzer_tracker()
    
    logger.info("Progress tracking examples completed")
    logger.info(f"Output files saved to {output_dir}")

if __name__ == "__main__":
    asyncio.run(main()) 