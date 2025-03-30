#!/usr/bin/env python3
"""Simple test script to verify batch processing works."""

import asyncio
import os
import tempfile
from unittest.mock import patch, MagicMock

from summit_seo.cli.analysis_runner import AnalysisRunner
from summit_seo.cli.progress_display import DisplayStyle
from summit_seo.cli.output_formatter import OutputFormat, set_output_format
from summit_seo.progress.base import ProgressTracker


class TestProgressTracker(ProgressTracker):
    """Test implementation of the abstract ProgressTracker."""
    
    def __init__(self, name="Test", total_steps=1):
        """Initialize the tracker."""
        self.name = name
        self.total_steps = total_steps
        self.current_step = 0
        self.state = "RUNNING"
        self.message = ""
    
    def get_progress_stats(self):
        """Get progress statistics."""
        return {
            "percentage": (self.current_step / self.total_steps) * 100 if self.total_steps else 0,
            "step": self.current_step,
            "total_steps": self.total_steps,
            "state": self.state,
            "message": self.message
        }
    
    def get_estimated_time_remaining(self):
        """Get estimated time remaining."""
        return 0
    
    def visualize(self):
        """Visualize the progress (no-op for tests)."""
        return ""


async def test_batch_mode():
    """Run a simple batch mode test."""
    # Override the ProgressTracker to use our test implementation
    with patch("summit_seo.cli.analysis_runner.ProgressTracker", TestProgressTracker):
        # Set batch mode output formatter
        set_output_format(OutputFormat.BATCH, show_details=True)
        
        # Create a temporary output directory
        output_dir = tempfile.mkdtemp()
        
        # Create a runner with batch mode enabled
        runner = AnalysisRunner(
            url="https://example.com",
            display_style=DisplayStyle.MINIMAL,
            output_path=output_dir,
            batch_mode=True
        )
        
        # Mock the analyzer execution to return test data
        with patch.object(runner, "_setup_components"), \
             patch.object(runner, "_collect_data", return_value={"html": "<html><body>Test</body></html>"}), \
             patch.object(runner, "_process_data", return_value={"processed_data": True}), \
             patch.object(runner, "_analyze_data", return_value=[{"score": 85, "analyzer": "TestAnalyzer"}]), \
             patch.object(runner, "_generate_report", return_value=os.path.join(output_dir, "test_report.html")):
            
            # Run the analysis
            report_path = await runner.run()
            
            # Print success message
            print(f"\nBatch mode test successful! Report path: {report_path}")


if __name__ == "__main__":
    asyncio.run(test_batch_mode()) 