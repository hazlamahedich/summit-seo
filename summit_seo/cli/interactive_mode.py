"""Interactive CLI mode for Summit SEO.

This module provides an interactive command-line interface for Summit SEO,
allowing users to control analysis operations in real-time through keyboard
commands and receive live updates.
"""

import asyncio
import curses
import sys
import time
from typing import Dict, List, Optional, Any, Callable
from enum import Enum

from summit_seo.analyzer import AnalyzerFactory
from summit_seo.progress.base import ProgressTracker, ProgressState, ProgressStage
from summit_seo.cli.progress_display import DisplayStyle


class InteractiveCommand(str, Enum):
    """Commands available in interactive mode."""
    
    PAUSE = "p"       # Pause the analysis
    RESUME = "r"      # Resume the analysis
    CANCEL = "c"      # Cancel the analysis
    DETAIL = "d"      # Toggle detail level
    HELP = "h"        # Show help
    QUIT = "q"        # Quit interactive mode


class InteractiveModeDisplay:
    """Interactive CLI display with keyboard input handling.
    
    This class provides a curses-based interactive interface that allows
    users to control the analysis process through keyboard commands while
    viewing real-time progress updates.
    """
    
    def __init__(
        self,
        tracker: ProgressTracker,
        refresh_rate: float = 0.1,
        command_handlers: Optional[Dict[InteractiveCommand, Callable]] = None,
    ):
        """Initialize the interactive CLI display.
        
        Args:
            tracker: Progress tracker to visualize.
            refresh_rate: How often to refresh the display (in seconds).
            command_handlers: Dictionary mapping commands to handler functions.
        """
        self.tracker = tracker
        self.refresh_rate = refresh_rate
        self.command_handlers = command_handlers or {}
        
        self._detail_level = 1  # 0: minimal, 1: normal, 2: detailed
        self._running = False
        self._screen = None
        self._help_visible = False
        self._last_key = ""
        self._message = ""
        self._message_timeout = 0
        
    def _init_curses(self) -> None:
        """Initialize curses settings."""
        curses.curs_set(0)  # Hide cursor
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_YELLOW, -1)
        curses.init_pair(3, curses.COLOR_RED, -1)
        curses.init_pair(4, curses.COLOR_BLUE, -1)
        curses.init_pair(5, curses.COLOR_CYAN, -1)
        curses.init_pair(6, curses.COLOR_MAGENTA, -1)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Status bar
    
    def _handle_input(self) -> None:
        """Handle keyboard input."""
        try:
            key = self._screen.getkey()
        except curses.error:
            return
            
        self._last_key = key
        
        # Handle special keys
        if key == "KEY_RESIZE":
            curses.update_lines_cols()
            return
            
        # Handle interactive commands
        try:
            command = InteractiveCommand(key)
            if command in self.command_handlers:
                self.command_handlers[command]()
                self._set_message(f"Command executed: {command.name}")
            
            if command == InteractiveCommand.DETAIL:
                self._detail_level = (self._detail_level + 1) % 3
                self._set_message(f"Detail level: {['Minimal', 'Normal', 'Detailed'][self._detail_level]}")
            elif command == InteractiveCommand.HELP:
                self._help_visible = not self._help_visible
                self._set_message(f"Help {'visible' if self._help_visible else 'hidden'}")
        except ValueError:
            # Not a valid command
            self._set_message(f"Unknown command: {key}")
    
    def _set_message(self, message: str, timeout: float = 3.0) -> None:
        """Set a message to display temporarily."""
        self._message = message
        self._message_timeout = time.time() + timeout
    
    def _draw_header(self, y: int, x: int, width: int) -> int:
        """Draw the header section."""
        title = f"Summit SEO Interactive Analysis"
        self._screen.addstr(y, (width - len(title)) // 2, title, curses.A_BOLD)
        
        # Draw status info
        status_line = f"Status: {self.tracker.state.value.upper()}"
        if self.tracker.state == ProgressState.RUNNING:
            status_attr = curses.color_pair(1)  # Green
        elif self.tracker.state == ProgressState.PAUSED:
            status_attr = curses.color_pair(2)  # Yellow
        elif self.tracker.state in (ProgressState.FAILED, ProgressState.CANCELLED):
            status_attr = curses.color_pair(3)  # Red
        else:
            status_attr = curses.A_NORMAL
            
        self._screen.addstr(y + 1, 2, status_line, status_attr)
        
        # Draw stage info
        stage_line = f"Stage: {self.tracker.current_stage.value}"
        stage_colors = {
            ProgressStage.INITIALIZATION: 5,  # Cyan
            ProgressStage.COLLECTION: 4,      # Blue
            ProgressStage.PROCESSING: 6,      # Magenta
            ProgressStage.ANALYSIS: 2,        # Yellow
            ProgressStage.REPORTING: 1,       # Green
            ProgressStage.CLEANUP: 0          # Normal
        }
        stage_attr = curses.color_pair(stage_colors.get(self.tracker.current_stage, 0))
        self._screen.addstr(y + 1, width - len(stage_line) - 2, stage_line, stage_attr)
        
        return y + 2
    
    def _draw_progress_bar(self, y: int, x: int, width: int) -> int:
        """Draw the progress bar section."""
        percentage = self.tracker.progress_percentage
        bar_width = width - 14  # Account for labels and padding
        filled = int(bar_width * percentage / 100)
        
        # Draw percentage
        self._screen.addstr(y, x, f"{percentage:6.2f}% ", curses.A_BOLD)
        
        # Draw progress bar
        self._screen.addstr(y, x + 8, "[")
        self._screen.addstr(y, x + 9, "█" * filled, curses.color_pair(1))
        self._screen.addstr(y, x + 9 + filled, "░" * (bar_width - filled))
        self._screen.addstr(y, x + 9 + bar_width, "]")
        
        return y + 1
    
    def _draw_details(self, y: int, x: int, width: int) -> int:
        """Draw the details section."""
        if self._detail_level == 0:
            # Minimal details - just current step
            self._screen.addstr(y, x, f"Current: {self.tracker.current_step_name}")
            return y + 1
            
        # Basic details
        elapsed = self.tracker.elapsed_time.total_seconds()
        remaining = self.tracker.get_estimated_time_remaining()
        
        if remaining is not None:
            remaining = remaining.total_seconds()
            self._screen.addstr(y, x, f"Time: {int(elapsed)}s elapsed, {int(remaining)}s remaining")
        else:
            self._screen.addstr(y, x, f"Time: {int(elapsed)}s elapsed")
            
        self._screen.addstr(y, x + width // 2, f"Step: {self.tracker.current_step}/{self.tracker.total_steps}")
        y += 1
        
        # Current operation details
        self._screen.addstr(y, x, f"Current: {self.tracker.current_step_name}", curses.A_BOLD)
        y += 1
        
        if self._detail_level >= 2:
            # Show detailed stage progress
            self._screen.addstr(y, x, "Stage Progress:", curses.A_UNDERLINE)
            y += 1
            
            for stage in ProgressStage:
                progress = self.tracker._stage_progress.get(stage, 0) * 100
                stage_attr = curses.color_pair(0)
                if stage == self.tracker.current_stage:
                    stage_attr = curses.A_BOLD
                    
                if progress > 0:
                    self._screen.addstr(y, x + 2, f"{stage.value}: {progress:.1f}%", stage_attr)
                    y += 1
        
        return y
    
    def _draw_help(self, y: int, x: int, width: int) -> int:
        """Draw the help section."""
        if not self._help_visible:
            return y
            
        self._screen.addstr(y, x, "Commands:", curses.A_UNDERLINE)
        y += 1
        
        commands = [
            (InteractiveCommand.PAUSE.value, "Pause analysis"),
            (InteractiveCommand.RESUME.value, "Resume analysis"),
            (InteractiveCommand.CANCEL.value, "Cancel analysis"),
            (InteractiveCommand.DETAIL.value, "Toggle detail level"),
            (InteractiveCommand.HELP.value, "Show/hide help"),
            (InteractiveCommand.QUIT.value, "Quit interactive mode")
        ]
        
        for key, description in commands:
            self._screen.addstr(y, x + 2, f"{key}", curses.A_BOLD)
            self._screen.addstr(y, x + 4, f"- {description}")
            y += 1
        
        return y + 1
    
    def _draw_status_bar(self, height: int, width: int) -> None:
        """Draw the status bar at the bottom of the screen."""
        status_attr = curses.color_pair(7) | curses.A_BOLD
        
        # Show temporary message if active
        if time.time() < self._message_timeout:
            status_text = self._message
        else:
            analyzer_name = ""
            if hasattr(self.tracker, 'analyzer_name') and self.tracker.analyzer_name:
                analyzer_name = f"Analyzer: {self.tracker.analyzer_name} | "
                
            status_text = f"{analyzer_name}Press h for help | Last key: {self._last_key}"
            
        # Pad or truncate to fit width
        if len(status_text) > width:
            status_text = status_text[:width-3] + "..."
        else:
            status_text = status_text + " " * (width - len(status_text))
            
        self._screen.addstr(height - 1, 0, status_text, status_attr)
    
    def _draw_screen(self) -> None:
        """Draw the complete interactive display."""
        self._screen.clear()
        height, width = self._screen.getmaxyx()
        
        # Draw components
        y = 0
        y = self._draw_header(y, 0, width)
        y += 1  # Add spacing
        y = self._draw_progress_bar(y, 2, width - 4)
        y += 1  # Add spacing
        y = self._draw_details(y, 2, width - 4)
        y += 1  # Add spacing
        y = self._draw_help(y, 2, width - 4)
        
        # Draw status bar at the bottom
        self._draw_status_bar(height, width)
        
        self._screen.refresh()
    
    async def _display_loop(self) -> None:
        """Main display loop."""
        while self._running:
            self._handle_input()
            self._draw_screen()
            await asyncio.sleep(self.refresh_rate)
    
    def start(self) -> None:
        """Start the interactive display."""
        def _curses_main(stdscr):
            self._screen = stdscr
            self._init_curses()
            self._running = True
            
            # Run the display loop
            asyncio.run(self._display_loop())
        
        curses.wrapper(_curses_main)
    
    def stop(self) -> None:
        """Stop the interactive display."""
        self._running = False


class InteractiveMode:
    """Interactive mode controller for Summit SEO CLI.
    
    This class provides a high-level interface for managing interactive CLI mode,
    handling commands, and coordinating between the analysis runner and the
    interactive display.
    """
    
    def __init__(self, analysis_runner):
        """Initialize interactive mode.
        
        Args:
            analysis_runner: The analysis runner instance to control.
        """
        self.runner = analysis_runner
        self.tracker = analysis_runner.progress_tracker
        
        # Set up command handlers
        self.command_handlers = {
            InteractiveCommand.PAUSE: self._handle_pause,
            InteractiveCommand.RESUME: self._handle_resume,
            InteractiveCommand.CANCEL: self._handle_cancel,
            InteractiveCommand.QUIT: self._handle_quit,
        }
        
        self.display = InteractiveModeDisplay(
            tracker=self.tracker,
            command_handlers=self.command_handlers
        )
        
        self._running = False
        self._analysis_task = None
    
    def _handle_pause(self) -> None:
        """Handle pause command."""
        if self.tracker.state == ProgressState.RUNNING:
            self.runner.pause()
    
    def _handle_resume(self) -> None:
        """Handle resume command."""
        if self.tracker.state == ProgressState.PAUSED:
            self.runner.resume()
    
    def _handle_cancel(self) -> None:
        """Handle cancel command."""
        if self.tracker.state in (ProgressState.RUNNING, ProgressState.PAUSED):
            self.runner.cancel()
    
    def _handle_quit(self) -> None:
        """Handle quit command."""
        self.display.stop()
        
    async def start_analysis(self) -> None:
        """Start the analysis process."""
        self._analysis_task = asyncio.create_task(self.runner.run())
        
        # Wait for the analysis to complete
        try:
            await self._analysis_task
        except asyncio.CancelledError:
            # Analysis was cancelled
            pass
    
    def run(self) -> None:
        """Run interactive mode."""
        # Start the analysis in the background
        asyncio.create_task(self.start_analysis())
        
        # Start the interactive display
        self.display.start()


def run_interactive_analysis(analysis_runner):
    """Run an analysis in interactive mode.
    
    Args:
        analysis_runner: The analysis runner to use.
    """
    interactive = InteractiveMode(analysis_runner)
    interactive.run() 