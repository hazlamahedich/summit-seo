"""Tests for interactive CLI mode."""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from summit_seo.cli.interactive_mode import InteractiveCommand, InteractiveMode, InteractiveModeDisplay
from summit_seo.progress.base import ProgressState


class TestInteractiveMode(unittest.TestCase):
    """Test cases for interactive mode."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock analysis runner
        self.runner = MagicMock()
        self.runner.progress_tracker = MagicMock()
        self.runner.pause = AsyncMock()
        self.runner.resume = AsyncMock()
        self.runner.cancel = AsyncMock()
        self.runner.run = AsyncMock()
    
    @patch('summit_seo.cli.interactive_mode.InteractiveModeDisplay')
    def test_interactive_mode_initialization(self, mock_display):
        """Test interactive mode initialization."""
        # Create interactive mode
        mode = InteractiveMode(self.runner)
        
        # Verify tracker and command handlers are set up correctly
        self.assertEqual(mode.tracker, self.runner.progress_tracker)
        self.assertIn(InteractiveCommand.PAUSE, mode.command_handlers)
        self.assertIn(InteractiveCommand.RESUME, mode.command_handlers)
        self.assertIn(InteractiveCommand.CANCEL, mode.command_handlers)
        self.assertIn(InteractiveCommand.QUIT, mode.command_handlers)
        
        # Verify display was created with correct parameters
        mock_display.assert_called_once_with(
            tracker=self.runner.progress_tracker,
            command_handlers=mode.command_handlers
        )
    
    @patch('summit_seo.cli.interactive_mode.InteractiveModeDisplay')
    def test_pause_command(self, mock_display):
        """Test pause command handler."""
        # Set up mock tracker state
        self.runner.progress_tracker.state = ProgressState.RUNNING
        
        # Create interactive mode and call pause handler
        mode = InteractiveMode(self.runner)
        mode._handle_pause()
        
        # Verify runner's pause method was called
        self.runner.pause.assert_called_once()
    
    @patch('summit_seo.cli.interactive_mode.InteractiveModeDisplay')
    def test_resume_command(self, mock_display):
        """Test resume command handler."""
        # Set up mock tracker state
        self.runner.progress_tracker.state = ProgressState.PAUSED
        
        # Create interactive mode and call resume handler
        mode = InteractiveMode(self.runner)
        mode._handle_resume()
        
        # Verify runner's resume method was called
        self.runner.resume.assert_called_once()
    
    @patch('summit_seo.cli.interactive_mode.InteractiveModeDisplay')
    def test_cancel_command(self, mock_display):
        """Test cancel command handler."""
        # Set up mock tracker state
        self.runner.progress_tracker.state = ProgressState.RUNNING
        
        # Create interactive mode and call cancel handler
        mode = InteractiveMode(self.runner)
        mode._handle_cancel()
        
        # Verify runner's cancel method was called
        self.runner.cancel.assert_called_once()
    
    @patch('summit_seo.cli.interactive_mode.asyncio.create_task')
    @patch('summit_seo.cli.interactive_mode.InteractiveModeDisplay')
    def test_run_method(self, mock_display, mock_create_task):
        """Test run method."""
        # Create interactive mode and call run
        mode = InteractiveMode(self.runner)
        mode.run()
        
        # Verify asyncio.create_task was called
        mock_create_task.assert_called_once()
        
        # Verify display's start method was called
        mock_display.return_value.start.assert_called_once()
    
    @patch('summit_seo.cli.interactive_mode.InteractiveModeDisplay')
    @patch('summit_seo.cli.interactive_mode.asyncio.create_task')
    def test_start_analysis(self, mock_create_task, mock_display):
        """Test that start_analysis is correctly called in run method."""
        # Create spy for the start_analysis method
        with patch.object(InteractiveMode, 'start_analysis', return_value=AsyncMock()) as mock_start:
            # Create interactive mode and call run
            mode = InteractiveMode(self.runner)
            mode.run()
            
            # Check that create_task was called with the result of start_analysis
            mock_create_task.assert_called_once()
            # Verify that our mocked method was used
            mock_start.assert_called_once()


if __name__ == '__main__':
    unittest.main() 