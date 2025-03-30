"""CLI progress display components for Summit SEO."""

import asyncio
import sys
import time
from enum import Enum
from typing import Optional, Dict, Any, List, Tuple
import shutil

from summit_seo.progress.base import ProgressTracker, ProgressState, ProgressStage


class DisplayStyle(str, Enum):
    """Display styles for CLI progress indicators."""
    
    MINIMAL = "minimal"    # Simple one-line progress bar
    DETAILED = "detailed"  # Multi-line progress with stats
    ANIMATED = "animated"  # Animated progress bar with spinner
    COMPACT = "compact"    # Compact single-line status


class CLIProgressDisplay:
    """CLI progress display component for real-time progress visualization.
    
    This class provides user-friendly terminal-based progress indicators
    that can be used to display progress of analysis operations.
    """
    
    _spinner_frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def __init__(
        self, 
        tracker: ProgressTracker,
        style: DisplayStyle = DisplayStyle.DETAILED,
        refresh_rate: float = 0.2,
        show_spinner: bool = True,
        show_time: bool = True,
        show_percentage: bool = True,
        bar_width: int = 40,
        clear_on_complete: bool = False
    ):
        """Initialize the CLI progress display.
        
        Args:
            tracker: Progress tracker to visualize.
            style: Display style to use.
            refresh_rate: How often to refresh the display (in seconds).
            show_spinner: Whether to show a spinner animation.
            show_time: Whether to show elapsed/remaining time.
            show_percentage: Whether to show percentage complete.
            bar_width: Width of the progress bar in characters.
            clear_on_complete: Whether to clear the display when complete.
        """
        self.tracker = tracker
        self.style = style
        self.refresh_rate = refresh_rate
        self.show_spinner = show_spinner
        self.show_time = show_time
        self.show_percentage = show_percentage
        self.bar_width = bar_width
        self.clear_on_complete = clear_on_complete
        
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._spinner_idx = 0
        self._last_update_time = 0
        self._last_lines_count = 0
        self._terminal_width = shutil.get_terminal_size().columns
    
    async def start(self) -> None:
        """Start displaying progress."""
        if self._running:
            return
            
        self._running = True
        self._task = asyncio.create_task(self._display_loop())
    
    async def stop(self) -> None:
        """Stop displaying progress."""
        self._running = False
        if self._task:
            await self._task
            self._task = None
            
        # Clear the display if requested
        if self.clear_on_complete:
            self._clear_previous_output()
    
    def _clear_previous_output(self) -> None:
        """Clear previous output lines."""
        if self._last_lines_count > 0:
            # Move cursor up and clear lines
            sys.stdout.write(f"\033[{self._last_lines_count}A")  # Move cursor up
            sys.stdout.write("\033[J")  # Clear from cursor to end of screen
            sys.stdout.flush()
            self._last_lines_count = 0
    
    def _get_color_for_state(self, state: ProgressState) -> str:
        """Get ANSI color code for progress state."""
        colors = {
            ProgressState.NOT_STARTED: "\033[90m",  # Gray
            ProgressState.RUNNING: "\033[94m",      # Blue
            ProgressState.PAUSED: "\033[93m",       # Yellow
            ProgressState.COMPLETED: "\033[92m",    # Green
            ProgressState.FAILED: "\033[91m",       # Red
            ProgressState.CANCELLED: "\033[90m"     # Gray
        }
        return colors.get(state, "\033[0m")
    
    def _get_color_for_stage(self, stage: ProgressStage) -> str:
        """Get ANSI color code for progress stage."""
        colors = {
            ProgressStage.INITIALIZATION: "\033[96m",  # Cyan
            ProgressStage.COLLECTION: "\033[94m",      # Blue
            ProgressStage.PROCESSING: "\033[95m",      # Magenta
            ProgressStage.ANALYSIS: "\033[93m",        # Yellow
            ProgressStage.REPORTING: "\033[92m",       # Green
            ProgressStage.CLEANUP: "\033[90m"          # Gray
        }
        return colors.get(stage, "\033[0m")
    
    def _format_time(self, seconds: float) -> str:
        """Format time in seconds to a readable string."""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def _get_minimal_display(self) -> str:
        """Generate minimal progress display."""
        # Get basic progress information
        percentage = self.tracker.progress_percentage
        state = self.tracker.state
        color = self._get_color_for_state(state)
        reset = "\033[0m"
        
        # Create progress bar
        bar_fill = int(percentage / 100 * self.bar_width)
        bar = f"[{color}{'#' * bar_fill}{reset}{' ' * (self.bar_width - bar_fill)}]"
        
        # Add spinner if enabled
        spinner = ""
        if self.show_spinner and state == ProgressState.RUNNING:
            spinner = f" {self._spinner_frames[self._spinner_idx % len(self._spinner_frames)]}"
        
        # Add percentage if enabled
        percent_str = ""
        if self.show_percentage:
            percent_str = f" {percentage:.1f}%"
        
        # Add time if enabled
        time_str = ""
        if self.show_time:
            elapsed = self.tracker.elapsed_time.total_seconds()
            estimated = self.tracker.get_estimated_time_remaining()
            
            if estimated is not None:
                time_str = f" {self._format_time(elapsed)}/{self._format_time(estimated.total_seconds())}"
            else:
                time_str = f" {self._format_time(elapsed)}"
        
        # Combine components
        return f"{bar}{spinner}{percent_str}{time_str} {color}{state.value}{reset}"
    
    def _get_detailed_display(self) -> List[str]:
        """Generate detailed progress display."""
        lines = []
        
        # Get basic progress information
        percentage = self.tracker.progress_percentage
        state = self.tracker.state
        stage = self.tracker.current_stage
        color = self._get_color_for_state(state)
        stage_color = self._get_color_for_stage(stage)
        reset = "\033[0m"
        
        # Add title line
        spinner = ""
        if self.show_spinner and state == ProgressState.RUNNING:
            spinner = f" {self._spinner_frames[self._spinner_idx % len(self._spinner_frames)]}"
            
        lines.append(f"{color}{self.tracker.name}{reset}{spinner} {color}[{state.value}]{reset}")
        
        # Create progress bar
        bar_fill = int(percentage / 100 * self.bar_width)
        bar = f"[{color}{'#' * bar_fill}{reset}{' ' * (self.bar_width - bar_fill)}]"
        lines.append(f"{bar} {percentage:.1f}%")
        
        # Add progress details
        lines.append(f"Step: {self.tracker.current_step}/{self.tracker.total_steps}")
        lines.append(f"Stage: {stage_color}{stage.value}{reset} ({self.tracker._stage_progress[stage]:.1%} complete)")
        
        # Add time information
        elapsed = self.tracker.elapsed_time.total_seconds()
        estimated = self.tracker.get_estimated_time_remaining()
        
        lines.append(f"Time elapsed: {self._format_time(elapsed)}")
        if estimated is not None:
            lines.append(f"Time remaining: {self._format_time(estimated.total_seconds())}")
        else:
            lines.append("Time remaining: calculating...")
        
        # Add recent messages
        if self.tracker.messages:
            lines.append("")
            lines.append("Recent messages:")
            for ts, msg in self.tracker.messages[-3:]:
                lines.append(f"  [{ts.strftime('%H:%M:%S')}] {msg}")
        
        # Add recent errors
        if self.tracker.errors:
            lines.append("")
            lines.append(f"\033[91mRecent errors:\033[0m")
            for ts, err in self.tracker.errors[-3:]:
                lines.append(f"  [{ts.strftime('%H:%M:%S')}] \033[91m{err}\033[0m")
        
        return lines
    
    def _get_animated_display(self) -> List[str]:
        """Generate animated progress display."""
        lines = []
        
        # Get basic progress information
        percentage = self.tracker.progress_percentage
        state = self.tracker.state
        color = self._get_color_for_state(state)
        reset = "\033[0m"
        
        # Create animated title with spinner
        spinner = ""
        if self.show_spinner and state == ProgressState.RUNNING:
            spinner = f"{self._spinner_frames[self._spinner_idx % len(self._spinner_frames)]} "
            
        lines.append(f"{spinner}{color}{self.tracker.name}{reset} {color}[{state.value}]{reset}")
        
        # Create animated progress bar with gradient effect
        bar_width = self.bar_width
        bar_fill = int(percentage / 100 * bar_width)
        
        # Create gradient effect based on state
        if state == ProgressState.RUNNING:
            # Blue gradient
            gradient = [f"\033[94m", f"\033[96m", f"\033[94m"]
        elif state == ProgressState.COMPLETED:
            # Green gradient
            gradient = [f"\033[92m", f"\033[97m", f"\033[92m"]
        elif state == ProgressState.FAILED:
            # Red gradient
            gradient = [f"\033[91m", f"\033[93m", f"\033[91m"]
        else:
            # Default gradient matching state color
            gradient = [color, color, color]
        
        # Create bar with gradient
        bar = "["
        for i in range(bar_width):
            if i < bar_fill:
                # Calculate position in gradient
                if i < bar_fill / 3:
                    bar += f"{gradient[0]}#"
                elif i < bar_fill * 2 / 3:
                    bar += f"{gradient[1]}#"
                else:
                    bar += f"{gradient[2]}#"
            else:
                bar += f"{reset} "
        bar += f"{reset}]"
        
        lines.append(f"{bar} {percentage:.1f}%")
        
        # Add stage progress as mini-bars
        stage_lines = []
        for stage in ProgressStage:
            stage_progress = self.tracker._stage_progress[stage]
            stage_bar_width = 10
            stage_fill = int(stage_progress * stage_bar_width)
            stage_color = self._get_color_for_stage(stage)
            stage_active = stage == self.tracker.current_stage
            
            prefix = "➤ " if stage_active else "  "
            stage_bar = f"[{stage_color}{'■' * stage_fill}{reset}{' ' * (stage_bar_width - stage_fill)}]"
            stage_lines.append(f"{prefix}{stage_color}{stage.value:12s}{reset} {stage_bar} {stage_progress:.0%}")
        
        lines.extend(stage_lines)
        
        # Add time information in a compact format
        if self.show_time:
            elapsed = self.tracker.elapsed_time.total_seconds()
            estimated = self.tracker.get_estimated_time_remaining()
            
            time_line = f"⏱  {self._format_time(elapsed)}"
            if estimated is not None:
                time_line += f" (est. {self._format_time(estimated.total_seconds())} remaining)"
            
            lines.append(time_line)
        
        return lines
    
    def _get_compact_display(self) -> str:
        """Generate compact progress display."""
        # Get basic progress information
        percentage = self.tracker.progress_percentage
        state = self.tracker.state
        stage = self.tracker.current_stage
        color = self._get_color_for_state(state)
        reset = "\033[0m"
        
        # Add spinner if enabled
        spinner = ""
        if self.show_spinner and state == ProgressState.RUNNING:
            spinner = f" {self._spinner_frames[self._spinner_idx % len(self._spinner_frames)]}"
        
        # Create small progress indicator
        dots = "⣿" * int(percentage / 10)
        dots += "⣀" * (10 - int(percentage / 10))
        
        # Format message
        return f"{color}{state.value}{reset}{spinner} [{dots}] {percentage:.0f}% - {stage.value}"
    
    async def _display_loop(self) -> None:
        """Main display loop for progress visualization."""
        self._terminal_width = shutil.get_terminal_size().columns
        
        while self._running:
            now = time.time()
            
            # Only update at the specified refresh rate
            if now - self._last_update_time >= self.refresh_rate:
                self._last_update_time = now
                self._spinner_idx += 1
                
                # Clear previous output
                self._clear_previous_output()
                
                # Generate display based on style
                if self.style == DisplayStyle.MINIMAL:
                    output = self._get_minimal_display()
                    print(output)
                    self._last_lines_count = 1
                elif self.style == DisplayStyle.COMPACT:
                    output = self._get_compact_display()
                    print(output)
                    self._last_lines_count = 1
                elif self.style == DisplayStyle.ANIMATED:
                    lines = self._get_animated_display()
                    for line in lines:
                        print(line)
                    self._last_lines_count = len(lines)
                else:  # DETAILED
                    lines = self._get_detailed_display()
                    for line in lines:
                        print(line)
                    self._last_lines_count = len(lines)
                
                # Check if tracker has completed or failed
                if self.tracker.state in (
                    ProgressState.COMPLETED, 
                    ProgressState.FAILED, 
                    ProgressState.CANCELLED
                ):
                    # Display one final update, then stop
                    if not self.clear_on_complete:
                        await asyncio.sleep(0.5)  # Brief pause to show final state
                    break
            
            await asyncio.sleep(0.05)  # Short sleep to avoid high CPU usage 