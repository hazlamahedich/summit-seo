"""Simple progress tracker implementation."""

import time
import math
from datetime import timedelta
from typing import Dict, Optional, Any, Union, List, Tuple

from summit_seo.progress.base import (
    ProgressTracker, 
    ProgressState,
    ProgressStage
)


class SimpleProgressTracker(ProgressTracker):
    """Simple progress tracker implementation.
    
    This class provides a basic implementation of the ProgressTracker
    interface with linear time estimation.
    """
    
    def __init__(self, total_steps: int = 100, name: str = "Analysis Progress"):
        """Initialize the simple progress tracker.
        
        Args:
            total_steps: Total number of steps to track.
            name: Name of the operation being tracked.
        """
        super().__init__(total_steps, name)
        self._progress_history: List[Tuple[float, int]] = []
        self._history_max_size = 20  # Maximum number of progress data points to store
        self._smoothing_factor = 0.2  # Value between 0 and 1 for EMA calculation
        self._last_estimate: Optional[timedelta] = None
    
    def update(self, step: int, message: Optional[str] = None) -> None:
        """Update the current progress step.
        
        Args:
            step: The current step (0 to total_steps).
            message: Optional message to record with the update.
        """
        # Call parent implementation
        super().update(step, message)
        
        # Record progress point for estimation
        if self._start_time is not None:
            elapsed = time.time() - self._start_time - self._pause_duration
            self._progress_history.append((elapsed, step))
            
            # Trim history if it gets too large
            if len(self._progress_history) > self._history_max_size:
                self._progress_history = self._progress_history[-self._history_max_size:]
    
    def get_estimated_time_remaining(self) -> Optional[timedelta]:
        """Get the estimated time remaining.
        
        Uses an exponential moving average of the progress rate to estimate
        the time remaining to complete the task.
        
        Returns:
            Estimated time remaining as a timedelta, or None if not enough data.
        """
        # Cannot estimate if not started or already done
        if (self._start_time is None or 
            self._state in (ProgressState.COMPLETED, ProgressState.FAILED, ProgressState.CANCELLED)):
            return None
        
        # Need at least 2 progress points to estimate
        if len(self._progress_history) < 2:
            return None
        
        # Calculate steps per second based on recent history
        steps_remaining = self._total_steps - self._current_step
        if steps_remaining <= 0:
            return timedelta(0)
        
        # Get the most recent progress points
        recent_points = self._progress_history[-10:]
        
        # Calculate average rate (steps per second)
        rates = []
        for i in range(1, len(recent_points)):
            time_diff = recent_points[i][0] - recent_points[i-1][0]
            step_diff = recent_points[i][1] - recent_points[i-1][1]
            
            # Avoid division by zero
            if time_diff > 0 and step_diff > 0:
                rate = step_diff / time_diff
                rates.append(rate)
        
        if not rates:
            # Fallback to overall average if we can't calculate recent rates
            first_time, first_step = self._progress_history[0]
            last_time, last_step = self._progress_history[-1]
            time_diff = last_time - first_time
            step_diff = last_step - first_step
            
            if time_diff > 0 and step_diff > 0:
                avg_rate = step_diff / time_diff
            else:
                return None  # Can't estimate
        else:
            avg_rate = sum(rates) / len(rates)
        
        # Estimate time remaining
        estimated_seconds = steps_remaining / avg_rate
        
        # Apply smoothing if we have a previous estimate
        if self._last_estimate is not None:
            last_seconds = self._last_estimate.total_seconds()
            smoothed_seconds = (self._smoothing_factor * estimated_seconds + 
                              (1 - self._smoothing_factor) * last_seconds)
            estimated_seconds = smoothed_seconds
        
        # Store this estimate for future smoothing
        self._last_estimate = timedelta(seconds=estimated_seconds)
        
        return self._last_estimate
    
    def get_progress_stats(self) -> Dict[str, Any]:
        """Get detailed progress statistics.
        
        Returns:
            Dictionary containing detailed progress statistics.
        """
        # Basic stats
        stats = {
            "name": self._name,
            "state": self._state.value,
            "current_step": self._current_step,
            "total_steps": self._total_steps,
            "progress_percentage": self.progress_percentage,
            "current_stage": self._current_stage.value,
            "stage_progress": {stage.value: prog for stage, prog in self._stage_progress.items()},
            "elapsed_time": self.elapsed_time.total_seconds()
        }
        
        # Add estimated time if available
        estimated_time = self.get_estimated_time_remaining()
        if estimated_time is not None:
            stats["estimated_time_remaining"] = estimated_time.total_seconds()
            stats["estimated_completion_percentage"] = min(100, self.progress_percentage)
        else:
            stats["estimated_time_remaining"] = None
            stats["estimated_completion_percentage"] = None
        
        # Add the last few messages
        last_messages = self._messages[-5:] if self._messages else []
        stats["recent_messages"] = [
            {"timestamp": msg[0].isoformat(), "message": msg[1]}
            for msg in last_messages
        ]
        
        # Add the last few errors
        last_errors = self._errors[-5:] if self._errors else []
        stats["recent_errors"] = [
            {"timestamp": err[0].isoformat(), "error": err[1]}
            for err in last_errors
        ]
        
        return stats
    
    def visualize(self, format: str = "text") -> Union[str, bytes]:
        """Generate a visualization of the progress.
        
        Args:
            format: Format for the visualization ("text", "html", "image").
            
        Returns:
            Visualization data in the specified format.
        """
        if format == "text":
            return self._visualize_text()
        elif format == "html":
            return self._visualize_html()
        else:
            raise ValueError(f"Unsupported visualization format: {format}")
    
    def _visualize_text(self) -> str:
        """Generate a text-based progress visualization.
        
        Returns:
            Text representation of the progress.
        """
        # Create progress bar
        progress = int(self.progress_percentage / 2)
        bar = "[" + "#" * progress + " " * (50 - progress) + "]"
        
        # Get time information
        elapsed = self.elapsed_time
        estimated = self.get_estimated_time_remaining()
        
        # Format elapsed time
        elapsed_str = f"{int(elapsed.total_seconds() // 3600):02d}:{int((elapsed.total_seconds() % 3600) // 60):02d}:{int(elapsed.total_seconds() % 60):02d}"
        
        # Format estimated time
        if estimated is not None:
            est_str = f"{int(estimated.total_seconds() // 3600):02d}:{int((estimated.total_seconds() % 3600) // 60):02d}:{int(estimated.total_seconds() % 60):02d}"
        else:
            est_str = "N/A"
        
        # Create the visualization
        lines = [
            f"Progress: {self._name} ({self._state.value})",
            f"{bar} {self.progress_percentage:.1f}%",
            f"Step: {self._current_step}/{self._total_steps}",
            f"Stage: {self._current_stage.value} ({self._stage_progress[self._current_stage]:.1%} complete)",
            f"Time elapsed: {elapsed_str}",
            f"Time remaining: {est_str}"
        ]
        
        # Add recent messages
        if self._messages:
            lines.append("\nRecent messages:")
            for ts, msg in self._messages[-3:]:
                lines.append(f"[{ts.strftime('%H:%M:%S')}] {msg}")
        
        # Add recent errors
        if self._errors:
            lines.append("\nRecent errors:")
            for ts, err in self._errors[-3:]:
                lines.append(f"[{ts.strftime('%H:%M:%S')}] ERROR: {err}")
        
        return "\n".join(lines)
    
    def _visualize_html(self) -> str:
        """Generate an HTML-based progress visualization.
        
        Returns:
            HTML representation of the progress.
        """
        # Get progress percentage
        percentage = self.progress_percentage
        
        # Get time information
        elapsed = self.elapsed_time
        estimated = self.get_estimated_time_remaining()
        
        # Format elapsed time
        elapsed_str = f"{int(elapsed.total_seconds() // 3600):02d}:{int((elapsed.total_seconds() % 3600) // 60):02d}:{int(elapsed.total_seconds() % 60):02d}"
        
        # Format estimated time
        if estimated is not None:
            est_str = f"{int(estimated.total_seconds() // 3600):02d}:{int((estimated.total_seconds() % 3600) // 60):02d}:{int(estimated.total_seconds() % 60):02d}"
        else:
            est_str = "N/A"
        
        # Create color based on state
        state_colors = {
            ProgressState.NOT_STARTED: "#6c757d",  # Gray
            ProgressState.RUNNING: "#007bff",      # Blue
            ProgressState.PAUSED: "#ffc107",       # Yellow
            ProgressState.COMPLETED: "#28a745",    # Green
            ProgressState.FAILED: "#dc3545",       # Red
            ProgressState.CANCELLED: "#6c757d"     # Gray
        }
        color = state_colors[self._state]
        
        # Create messages HTML
        messages_html = ""
        if self._messages:
            messages_html = "<h5>Recent Messages</h5><ul class='list-group'>"
            for ts, msg in self._messages[-5:]:
                messages_html += f"<li class='list-group-item'><small>{ts.strftime('%H:%M:%S')}</small> {msg}</li>"
            messages_html += "</ul>"
        
        # Create errors HTML
        errors_html = ""
        if self._errors:
            errors_html = "<h5 class='text-danger'>Recent Errors</h5><ul class='list-group'>"
            for ts, err in self._errors[-5:]:
                errors_html += f"<li class='list-group-item list-group-item-danger'><small>{ts.strftime('%H:%M:%S')}</small> {err}</li>"
            errors_html += "</ul>"
        
        # Create stage progress HTML
        stages_html = "<div class='row mt-3'>"
        for stage in ProgressStage:
            stage_percentage = self._stage_progress[stage] * 100
            stage_active = stage == self._current_stage
            stage_class = "active" if stage_active else ""
            
            stages_html += f"""
            <div class='col-md-4 mb-2'>
                <div class='card {stage_class}'>
                    <div class='card-body p-2'>
                        <h6 class='card-title'>{stage.value.title()}</h6>
                        <div class='progress'>
                            <div class='progress-bar' role='progressbar' style='width: {stage_percentage}%' 
                                aria-valuenow='{stage_percentage}' aria-valuemin='0' aria-valuemax='100'>
                                {stage_percentage:.1f}%
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """
        stages_html += "</div>"
        
        # Create the HTML visualization
        html = f"""
        <div class='progress-tracker'>
            <h4>{self._name} <span class='badge badge-pill' style='background-color: {color}'>{self._state.value}</span></h4>
            <div class='progress'>
                <div class='progress-bar' role='progressbar' style='width: {percentage}%; background-color: {color}' 
                    aria-valuenow='{percentage}' aria-valuemin='0' aria-valuemax='100'>
                    {percentage:.1f}%
                </div>
            </div>
            <div class='row mt-2'>
                <div class='col-md-6'>
                    <p><strong>Step:</strong> {self._current_step}/{self._total_steps}</p>
                </div>
                <div class='col-md-6'>
                    <p><strong>Current Stage:</strong> {self._current_stage.value}</p>
                </div>
                <div class='col-md-6'>
                    <p><strong>Time Elapsed:</strong> {elapsed_str}</p>
                </div>
                <div class='col-md-6'>
                    <p><strong>Time Remaining:</strong> {est_str}</p>
                </div>
            </div>
            {stages_html}
            {messages_html}
            {errors_html}
        </div>
        """
        
        return html 