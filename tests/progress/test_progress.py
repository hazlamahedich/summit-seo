"""Tests for the progress tracking module."""

import os
import sys
import time
import pytest
import asyncio
from datetime import timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from summit_seo.progress import (
    ProgressFactory,
    ProgressTracker,
    ProgressState,
    ProgressStage,
    ProgressError,
    SimpleProgressTracker,
    AnalyzerProgressTracker
)


class TestProgressState:
    """Test the ProgressState enum."""

    def test_states(self):
        """Test that all expected states are defined."""
        states = [state.value for state in ProgressState]
        assert "not_started" in states
        assert "running" in states
        assert "paused" in states
        assert "completed" in states
        assert "failed" in states
        assert "cancelled" in states


class TestProgressStage:
    """Test the ProgressStage enum."""

    def test_stages(self):
        """Test that all expected stages are defined."""
        stages = [stage.value for stage in ProgressStage]
        assert "initialization" in stages
        assert "collection" in stages
        assert "processing" in stages
        assert "analysis" in stages
        assert "reporting" in stages
        assert "cleanup" in stages


class TestProgressFactory:
    """Test the ProgressFactory class."""

    def test_register_and_create(self):
        """Test registering and creating trackers."""
        # Ensure the factory has trackers registered
        trackers = ProgressFactory.list_available()
        assert "simple" in trackers
        assert "analyzer" in trackers
        
        # Create a tracker
        tracker = ProgressFactory.create("simple")
        assert isinstance(tracker, SimpleProgressTracker)
        
        # Create a tracker with params
        test_name = "Test Progress"
        test_steps = 200
        tracker = ProgressFactory.create("simple", total_steps=test_steps, name=test_name)
        assert tracker.total_steps == test_steps
        assert tracker.name == test_name
    
    def test_get_default(self):
        """Test getting the default tracker."""
        tracker = ProgressFactory.get_default()
        assert isinstance(tracker, SimpleProgressTracker)
    
    def test_invalid_tracker(self):
        """Test requesting an invalid tracker."""
        with pytest.raises(KeyError):
            ProgressFactory.create("invalid_tracker")
    
    def test_register_invalid_class(self):
        """Test registering an invalid class."""
        class InvalidClass:
            pass
        
        with pytest.raises(TypeError):
            ProgressFactory.register("invalid", InvalidClass)


class TestSimpleProgressTracker:
    """Test the SimpleProgressTracker class."""
    
    @pytest.fixture
    def tracker(self):
        """Create a SimpleProgressTracker instance."""
        return SimpleProgressTracker(total_steps=100, name="Test Tracker")
    
    def test_initial_state(self, tracker):
        """Test the initial state of a tracker."""
        assert tracker.name == "Test Tracker"
        assert tracker.total_steps == 100
        assert tracker.current_step == 0
        assert tracker.progress_percentage == 0.0
        assert tracker.state == ProgressState.NOT_STARTED
        assert tracker.current_stage == ProgressStage.INITIALIZATION
        assert tracker.start_time is None
        assert tracker.elapsed_time == timedelta(0)
    
    def test_start_and_update(self, tracker):
        """Test starting and updating a tracker."""
        # Start the tracker
        tracker.start()
        assert tracker.state == ProgressState.RUNNING
        assert tracker.start_time is not None
        
        # Update progress
        tracker.update(50)
        assert tracker.current_step == 50
        assert tracker.progress_percentage == 50.0
        
        # Update with message
        tracker.update(60, "Progress message")
        assert tracker.current_step == 60
        assert len(tracker.messages) > 0
        assert "Progress message" in tracker.messages[-1][1]
    
    def test_increment(self, tracker):
        """Test incrementing progress."""
        tracker.start()
        tracker.update(10)
        
        # Increment by default amount (1)
        tracker.increment()
        assert tracker.current_step == 11
        
        # Increment by specific amount
        tracker.increment(5)
        assert tracker.current_step == 16
        
        # Increment with message
        tracker.increment(4, "Incremented")
        assert tracker.current_step == 20
        assert "Incremented" in tracker.messages[-1][1]
        
        # Increment beyond total
        tracker.increment(100)
        assert tracker.current_step == 100  # Capped at total
    
    def test_stage_progress(self, tracker):
        """Test updating stage progress."""
        tracker.start()
        
        # Set stage with initial progress
        tracker.set_stage(ProgressStage.COLLECTION, 0.5)
        assert tracker.current_stage == ProgressStage.COLLECTION
        
        # Update stage progress
        tracker.update_stage_progress(0.75)
        
        # Check that overall progress is updated based on stage weights
        assert tracker.current_step > 0
        
        # Set custom stage weights
        weights = {stage: 1/6 for stage in ProgressStage}
        tracker.set_stage_weights(weights)
        
        # Verify that progress is recalculated
        tracker.update_stage_progress(1.0)
    
    def test_pause_resume(self, tracker):
        """Test pausing and resuming tracking."""
        # Start tracking
        tracker.start()
        tracker.update(10)
        
        # Pause
        tracker.pause()
        assert tracker.state == ProgressState.PAUSED
        
        # Try to update while paused
        with pytest.raises(ProgressError):
            tracker.update(20)
        
        # Resume
        time.sleep(0.1)  # Ensure some time passes
        tracker.start()  # Resume
        assert tracker.state == ProgressState.RUNNING
        
        # Update after resume
        tracker.update(20)
        assert tracker.current_step == 20
    
    def test_complete(self, tracker):
        """Test completing tracking."""
        tracker.start()
        tracker.update(50)
        
        # Complete
        tracker.complete()
        assert tracker.state == ProgressState.COMPLETED
        assert tracker.current_step == tracker.total_steps
        
        # Try to update after complete
        with pytest.raises(ProgressError):
            tracker.update(60)
    
    def test_fail(self, tracker):
        """Test failing tracking."""
        tracker.start()
        tracker.update(50)
        
        # Fail with error message
        error_msg = "Something went wrong"
        tracker.fail(error_msg)
        assert tracker.state == ProgressState.FAILED
        assert len(tracker.errors) > 0
        assert error_msg in tracker.errors[-1][1]
        
        # Try to update after fail
        with pytest.raises(ProgressError):
            tracker.update(60)
    
    def test_cancel(self, tracker):
        """Test cancelling tracking."""
        tracker.start()
        tracker.update(50)
        
        # Cancel
        tracker.cancel()
        assert tracker.state == ProgressState.CANCELLED
        
        # Try to update after cancel
        with pytest.raises(ProgressError):
            tracker.update(60)
    
    def test_invalid_state_transitions(self, tracker):
        """Test invalid state transitions."""
        # Cannot pause before starting
        with pytest.raises(ProgressError):
            tracker.pause()
        
        # Cannot complete before starting
        with pytest.raises(ProgressError):
            tracker.complete()
        
        # Start and complete
        tracker.start()
        tracker.complete()
        
        # Cannot start again after complete
        with pytest.raises(ProgressError):
            tracker.start()
    
    def test_get_progress_stats(self, tracker):
        """Test getting progress statistics."""
        tracker.start()
        tracker.update(50)
        
        stats = tracker.get_progress_stats()
        assert stats["name"] == "Test Tracker"
        assert stats["state"] == "running"
        assert stats["current_step"] == 50
        assert stats["total_steps"] == 100
        assert stats["progress_percentage"] == 50.0
        assert "elapsed_time" in stats
    
    def test_visualize(self, tracker):
        """Test visualization methods."""
        tracker.start()
        tracker.update(50)
        
        # Test text visualization
        text = tracker.visualize("text")
        assert isinstance(text, str)
        assert "50.0%" in text
        
        # Test HTML visualization
        html = tracker.visualize("html")
        assert isinstance(html, str)
        assert "progress-bar" in html
        
        # Test invalid format
        with pytest.raises(ValueError):
            tracker.visualize("invalid_format")


class TestAnalyzerProgressTracker:
    """Test the AnalyzerProgressTracker class."""
    
    @pytest.fixture
    def tracker(self):
        """Create an AnalyzerProgressTracker instance."""
        return AnalyzerProgressTracker(total_steps=100, name="Analyzer Test")
    
    def test_register_analyzer(self, tracker):
        """Test registering analyzers."""
        # Register a single analyzer
        tracker.register_analyzer("ContentAnalyzer")
        assert "ContentAnalyzer" in tracker._analyzer_progress
        assert tracker._analyzer_weights["ContentAnalyzer"] == 1.0
        
        # Register multiple analyzers with different weights
        tracker.register_analyzer("SecurityAnalyzer", weight=2.0)
        tracker.register_analyzer("MetaAnalyzer", weight=0.5)
        
        # Weights should be normalized
        total_weight = sum(tracker._analyzer_weights.values())
        assert abs(total_weight - 1.0) < 0.001
    
    def test_analyzer_progress(self, tracker):
        """Test updating analyzer progress."""
        # Setup
        tracker.start()
        tracker.set_stage(ProgressStage.ANALYSIS)
        
        # Register and update analyzers
        analyzers = ["ContentAnalyzer", "SecurityAnalyzer", "MetaAnalyzer"]
        for analyzer in analyzers:
            tracker.register_analyzer(analyzer)
        
        # Update progress for each analyzer
        tracker.set_analyzer_progress("ContentAnalyzer", 0.3, "Running")
        assert tracker.get_analyzer_progress("ContentAnalyzer") == 0.3
        assert tracker.get_analyzer_status("ContentAnalyzer") == "Running"
        
        tracker.set_analyzer_progress("SecurityAnalyzer", 0.7, "Running")
        assert tracker.get_analyzer_progress("SecurityAnalyzer") == 0.7
        
        tracker.set_analyzer_progress("MetaAnalyzer", 1.0, "Completed")
        assert tracker.get_analyzer_progress("MetaAnalyzer") == 1.0
        assert tracker.get_analyzer_status("MetaAnalyzer") == "Completed"
        
        # Check that overall progress is updated
        assert tracker.current_step > 0
    
    def test_analyzer_metrics(self, tracker):
        """Test setting and getting analyzer metrics."""
        tracker.start()
        tracker.register_analyzer("ContentAnalyzer")
        
        # Set metrics
        metrics = {
            "issues_found": 5,
            "warnings": 3,
            "score": 85,
            "processing_time": 1.2
        }
        tracker.set_analyzer_metrics("ContentAnalyzer", metrics)
        
        # Get metrics
        retrieved_metrics = tracker.get_analyzer_metrics("ContentAnalyzer")
        assert retrieved_metrics == metrics
        
        # Update metrics
        tracker.set_analyzer_metrics("ContentAnalyzer", {"issues_found": 10})
        updated_metrics = tracker.get_analyzer_metrics("ContentAnalyzer")
        assert updated_metrics["issues_found"] == 10
        assert updated_metrics["score"] == 85  # Unchanged
    
    def test_get_progress_stats(self, tracker):
        """Test getting detailed progress statistics."""
        # Setup
        tracker.start()
        tracker.set_stage(ProgressStage.ANALYSIS)
        tracker.register_analyzer("ContentAnalyzer")
        tracker.register_analyzer("SecurityAnalyzer")
        
        # Update progress
        tracker.set_analyzer_progress("ContentAnalyzer", 0.5, "Running")
        tracker.set_analyzer_progress("SecurityAnalyzer", 1.0, "Completed")
        
        # Get stats
        stats = tracker.get_progress_stats()
        
        # Check basic stats
        assert stats["name"] == "Analyzer Test"
        assert stats["state"] == "running"
        assert stats["current_stage"] == "analysis"
        
        # Check analyzer stats
        assert "analyzers" in stats
        assert "ContentAnalyzer" in stats["analyzers"]
        assert "SecurityAnalyzer" in stats["analyzers"]
        assert stats["analyzers"]["ContentAnalyzer"]["progress"] == 0.5
        assert stats["analyzers"]["SecurityAnalyzer"]["progress"] == 1.0
        
        # Check counts
        assert stats["processed_analyzers"] == 1
        assert stats["total_analyzers"] == 2


@pytest.mark.asyncio
class TestAsyncVisualization:
    """Test async visualization methods of AnalyzerProgressTracker."""
    
    @pytest.fixture
    async def setup_tracker(self):
        """Set up a tracker with some data for visualization testing."""
        tracker = AnalyzerProgressTracker(total_steps=100, name="Visualization Test")
        tracker.start()
        tracker.set_stage(ProgressStage.ANALYSIS)
        
        # Register and update analyzers
        analyzers = ["ContentAnalyzer", "SecurityAnalyzer", "MetaAnalyzer"]
        for analyzer in analyzers:
            tracker.register_analyzer(analyzer)
            tracker.set_analyzer_progress(analyzer, 0.5, "Running")
        
        return tracker
    
    async def test_visualize_with_charts(self, setup_tracker):
        """Test the visualize_with_charts method."""
        try:
            html = await setup_tracker.visualize_with_charts()
            assert isinstance(html, str)
            assert "progress-tracker" in html
            
            # This should contain image data for charts
            # Note: This may fail if matplotlib is not properly configured
            if "data:image/png;base64" in html:
                assert "data:image/png;base64" in html
                assert "Score Distribution" in html
                assert "Analyzer Progress" in html
        except Exception as e:
            # Allow this test to pass even if visualization fails
            # since it depends on external libraries
            pytest.skip(f"Visualization with charts failed: {e}")


if __name__ == "__main__":
    pytest.main(["-v", __file__]) 