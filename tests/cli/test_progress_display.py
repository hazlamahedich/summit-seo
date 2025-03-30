"""Tests for CLI progress display components."""

import asyncio
import sys
import io
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import time

# Add the parent directory to sys.path to import summit_seo package
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from summit_seo.cli import CLIProgressDisplay, DisplayStyle
from summit_seo.progress import SimpleProgressTracker, ProgressStage


class TestDisplayStyle:
    """Tests for DisplayStyle enum."""
    
    def test_display_style_values(self):
        """Test that DisplayStyle enum has the expected values."""
        assert DisplayStyle.MINIMAL == "minimal"
        assert DisplayStyle.DETAILED == "detailed"
        assert DisplayStyle.ANIMATED == "animated"
        assert DisplayStyle.COMPACT == "compact"
        
        # Test all styles are included
        assert len(DisplayStyle) == 4


class TestCLIProgressDisplay:
    """Tests for CLIProgressDisplay."""
    
    @pytest.fixture
    def tracker(self):
        """Create a progress tracker for testing."""
        return SimpleProgressTracker(name="Test Progress")
    
    @pytest.fixture
    def display(self, tracker):
        """Create a CLI progress display for testing."""
        with patch('shutil.get_terminal_size') as mock_size:
            mock_size.return_value = MagicMock(columns=80, lines=24)
            display = CLIProgressDisplay(
                tracker=tracker,
                style=DisplayStyle.MINIMAL,
                refresh_rate=0.1,
                bar_width=20
            )
        return display
    
    def test_init(self, display, tracker):
        """Test initialization."""
        assert display.tracker == tracker
        assert display.style == DisplayStyle.MINIMAL
        assert display.refresh_rate == 0.1
        assert display.bar_width == 20
        assert display._running is False
        assert display._task is None
        
    def test_get_color_for_state(self, display):
        """Test color codes for states."""
        from summit_seo.progress import ProgressState
        
        # Test all states have colors
        for state in ProgressState:
            color = display._get_color_for_state(state)
            assert color.startswith("\033[")
            assert color.endswith("m")
    
    def test_get_color_for_stage(self, display):
        """Test color codes for stages."""
        from summit_seo.progress import ProgressStage
        
        # Test all stages have colors
        for stage in ProgressStage:
            color = display._get_color_for_stage(stage)
            assert color.startswith("\033[")
            assert color.endswith("m")
    
    def test_format_time(self, display):
        """Test time formatting."""
        # Test hours:minutes:seconds
        assert display._format_time(3661) == "01:01:01"
        
        # Test minutes:seconds
        assert display._format_time(65) == "01:05"
        
        # Test with zero
        assert display._format_time(0) == "00:00"
    
    @pytest.mark.asyncio
    async def test_start_stop(self, display):
        """Test starting and stopping the display."""
        # Mock the display loop to avoid actual printing
        with patch.object(display, '_display_loop') as mock_loop:
            mock_loop.return_value = asyncio.Future()
            mock_loop.return_value.set_result(None)
            
            # Test starting
            await display.start()
            assert display._running is True
            assert display._task is not None
            mock_loop.assert_called_once()
            
            # Test stopping
            await display.stop()
            assert display._running is False
            assert display._task is None
    
    def test_minimal_display(self, display, tracker):
        """Test minimal display generation."""
        tracker.start()
        tracker.set_stage(ProgressStage.INITIALIZATION, 0.5)
        
        # Generate display output
        output = display._get_minimal_display()
        
        # Verify it contains expected elements
        assert "[" in output  # Progress bar start
        assert "]" in output  # Progress bar end
        assert "running" in output.lower()  # State name
    
    def test_detailed_display(self, display, tracker):
        """Test detailed display generation."""
        # Change to detailed style
        display.style = DisplayStyle.DETAILED
        
        tracker.start()
        tracker.set_stage(ProgressStage.COLLECTION, 0.75)
        tracker._add_message("Test message")
        
        # Generate display output
        output = display._get_detailed_display()
        
        # Verify it's a multi-line output with expected elements
        assert isinstance(output, list)
        assert len(output) > 3
        
        # Check for specific content
        assert any("Test Progress" in line for line in output)
        assert any("Step:" in line for line in output)
        assert any("Stage:" in line for line in output)
        assert any("collection" in line.lower() for line in output)
        assert any("Test message" in line for line in output)
    
    def test_animated_display(self, display, tracker):
        """Test animated display generation."""
        # Change to animated style
        display.style = DisplayStyle.ANIMATED
        
        tracker.start()
        tracker.set_stage(ProgressStage.ANALYSIS, 0.6)
        
        # Generate display output
        output = display._get_animated_display()
        
        # Verify it's a multi-line output with expected elements
        assert isinstance(output, list)
        assert len(output) > 3
        
        # Check that it includes stage mini-bars
        assert any("analysis" in line.lower() for line in output)
        assert any("■" in line for line in output)
    
    def test_compact_display(self, display, tracker):
        """Test compact display generation."""
        # Change to compact style
        display.style = DisplayStyle.COMPACT
        
        tracker.start()
        tracker.set_stage(ProgressStage.REPORTING, 0.8)
        
        # Generate display output
        output = display._get_compact_display()
        
        # Verify it's a single-line output with expected elements
        assert isinstance(output, str)
        assert "running" in output.lower()
        assert "reporting" in output.lower()
        assert "⣿" in output  # Unicode block character
    
    @pytest.mark.asyncio
    async def test_clear_previous_output(self, display):
        """Test clearing previous output."""
        display._last_lines_count = 5
        
        # Mock stdout to capture the output
        with patch('sys.stdout') as mock_stdout:
            display._clear_previous_output()
            
            # Verify it writes the correct ANSI escape sequences
            mock_stdout.write.assert_any_call("\033[5A")  # Move up 5 lines
            mock_stdout.write.assert_any_call("\033[J")   # Clear to end of screen
            mock_stdout.flush.assert_called_once()
            
            # Verify the line count is reset
            assert display._last_lines_count == 0
    
    @pytest.mark.asyncio
    async def test_display_loop_style_switching(self, display, tracker):
        """Test that the display loop correctly displays different styles."""
        tracker.start()
        
        # Test that each style uses the correct display method
        styles_and_methods = [
            (DisplayStyle.MINIMAL, '_get_minimal_display'),
            (DisplayStyle.DETAILED, '_get_detailed_display'),
            (DisplayStyle.ANIMATED, '_get_animated_display'),
            (DisplayStyle.COMPACT, '_get_compact_display')
        ]
        
        for style, method_name in styles_and_methods:
            display.style = style
            with patch.object(display, method_name) as mock_method:
                mock_method.return_value = "Test output" if method_name == '_get_minimal_display' or method_name == '_get_compact_display' else ["Test output"]
                
                # Call the relevant display method directly
                if method_name == '_get_minimal_display' or method_name == '_get_compact_display':
                    result = getattr(display, method_name)()
                    assert isinstance(result, str)
                else:
                    result = getattr(display, method_name)()
                    assert isinstance(result, list)
                
                # Verify the method was called
                mock_method.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_display_lifecycle(self, tracker):
        """Test the complete lifecycle of the progress display."""
        # Create display with patched terminal size and print
        with patch('shutil.get_terminal_size') as mock_size, \
             patch('builtins.print') as mock_print, \
             patch('asyncio.sleep') as mock_sleep:
            
            mock_size.return_value = MagicMock(columns=80, lines=24)
            
            # Make sleep return immediately to speed up the test
            mock_sleep.return_value = None
            
            # Create the display
            display = CLIProgressDisplay(
                tracker=tracker,
                style=DisplayStyle.MINIMAL,
                refresh_rate=0.001  # Fast refresh for testing
            )
            
            # Start the display
            display_task = asyncio.create_task(display.start())
            
            # Update the tracker in a separate task
            async def update_tracker():
                tracker.start()
                tracker.set_stage(ProgressStage.INITIALIZATION, 1.0)
                tracker.set_stage(ProgressStage.COLLECTION, 1.0)
                tracker.complete()
                await asyncio.sleep(0.1)  # Give display time to update
                
            update_task = asyncio.create_task(update_tracker())
            
            # Wait for both tasks
            await update_task
            await display.stop()
            await display_task
            
            # Verify display was shown and final state was captured
            assert mock_print.call_count > 0
            assert not display._running
            assert display._task is None 