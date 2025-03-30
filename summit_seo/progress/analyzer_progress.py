"""Analyzer-specific progress tracker implementation."""

import asyncio
import time
import base64
import io
from datetime import timedelta
from typing import Dict, Optional, Any, Union, List, Tuple, Set

from summit_seo.progress.base import (
    ProgressTracker,
    ProgressState,
    ProgressStage
)
from summit_seo.visualization.analyzer_visualization import AnalyzerVisualization


class AnalyzerProgressTracker(ProgressTracker):
    """Analyzer-specific progress tracker implementation.
    
    This class extends the basic ProgressTracker with analyzer-specific
    tracking features like per-analyzer progress, visualization, and
    detailed metrics.
    """
    
    def __init__(self, total_steps: int = 100, name: str = "Analysis Progress"):
        """Initialize the analyzer progress tracker.
        
        Args:
            total_steps: Total number of steps to track.
            name: Name of the operation being tracked.
        """
        super().__init__(total_steps, name)
        self._analyzer_progress: Dict[str, float] = {}
        self._analyzer_weights: Dict[str, float] = {}
        self._analyzer_status: Dict[str, str] = {}
        self._analyzer_metrics: Dict[str, Dict[str, Any]] = {}
        self._analyzer_order: List[str] = []
        self._processed_analyzers: Set[str] = set()
        self._current_analyzer: Optional[str] = None
        self._progress_history: List[Tuple[float, int]] = []
        self._history_max_size = 20
        self._smoothing_factor = 0.2
        self._last_estimate: Optional[timedelta] = None
        self._visualizer = AnalyzerVisualization()
    
    def register_analyzer(self, analyzer_name: str, weight: float = 1.0) -> None:
        """Register an analyzer for progress tracking.
        
        Args:
            analyzer_name: Name of the analyzer.
            weight: Weight of this analyzer in the overall progress (default: 1.0).
                   Higher weights make this analyzer contribute more to overall progress.
        """
        if analyzer_name in self._analyzer_progress:
            return  # Already registered
            
        self._analyzer_progress[analyzer_name] = 0.0
        self._analyzer_weights[analyzer_name] = weight
        self._analyzer_status[analyzer_name] = "Pending"
        self._analyzer_metrics[analyzer_name] = {}
        self._analyzer_order.append(analyzer_name)
        
        # Normalize weights
        total_weight = sum(self._analyzer_weights.values())
        for name in self._analyzer_weights:
            self._analyzer_weights[name] /= total_weight
    
    def set_analyzer_progress(self, analyzer_name: str, progress: float, 
                              status: Optional[str] = None) -> None:
        """Update progress for a specific analyzer.
        
        Args:
            analyzer_name: Name of the analyzer.
            progress: Progress value between 0.0 and 1.0.
            status: Optional status message for the analyzer.
        """
        if analyzer_name not in self._analyzer_progress:
            self.register_analyzer(analyzer_name)
        
        if progress < 0.0 or progress > 1.0:
            raise ValueError("Progress must be between 0.0 and 1.0")
        
        self._analyzer_progress[analyzer_name] = progress
        
        if status:
            self._analyzer_status[analyzer_name] = status
            
        self._current_analyzer = analyzer_name
        
        # Mark as processed if completed
        if progress >= 1.0 and analyzer_name not in self._processed_analyzers:
            self._processed_analyzers.add(analyzer_name)
            self._add_message(f"Completed analyzer: {analyzer_name}")
        
        # Update overall progress based on weighted analyzer progress
        self._update_overall_progress()
    
    def set_analyzer_metrics(self, analyzer_name: str, metrics: Dict[str, Any]) -> None:
        """Set custom metrics for an analyzer.
        
        Args:
            analyzer_name: Name of the analyzer.
            metrics: Dictionary of metric names to values.
        """
        if analyzer_name not in self._analyzer_progress:
            self.register_analyzer(analyzer_name)
            
        self._analyzer_metrics[analyzer_name].update(metrics)
    
    def _update_overall_progress(self) -> None:
        """Update overall progress based on analyzer progress."""
        # Skip if not in running state
        if self._state != ProgressState.RUNNING:
            return
            
        # Calculate weighted progress
        weighted_progress = sum(
            self._analyzer_progress[name] * self._analyzer_weights[name]
            for name in self._analyzer_progress
        )
        
        # Update stage progress if in analysis stage
        if self._current_stage == ProgressStage.ANALYSIS:
            self.update_stage_progress(weighted_progress)
        
        # Record progress point for estimation
        if self._start_time is not None:
            elapsed = time.time() - self._start_time - self._pause_duration
            self._progress_history.append((elapsed, self._current_step))
            
            # Trim history if it gets too large
            if len(self._progress_history) > self._history_max_size:
                self._progress_history = self._progress_history[-self._history_max_size:]
    
    def get_analyzer_progress(self, analyzer_name: str) -> float:
        """Get progress for a specific analyzer.
        
        Args:
            analyzer_name: Name of the analyzer.
            
        Returns:
            Progress value between 0.0 and 1.0.
        """
        if analyzer_name not in self._analyzer_progress:
            return 0.0
            
        return self._analyzer_progress[analyzer_name]
    
    def get_analyzer_status(self, analyzer_name: str) -> str:
        """Get status for a specific analyzer.
        
        Args:
            analyzer_name: Name of the analyzer.
            
        Returns:
            Status string for the analyzer.
        """
        if analyzer_name not in self._analyzer_status:
            return "Unknown"
            
        return self._analyzer_status[analyzer_name]
    
    def get_analyzer_metrics(self, analyzer_name: str) -> Dict[str, Any]:
        """Get metrics for a specific analyzer.
        
        Args:
            analyzer_name: Name of the analyzer.
            
        Returns:
            Dictionary of metrics for the analyzer.
        """
        if analyzer_name not in self._analyzer_metrics:
            return {}
            
        return self._analyzer_metrics[analyzer_name].copy()
    
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
        # Get basic stats
        stats = {
            "name": self._name,
            "state": self._state.value,
            "current_step": self._current_step,
            "total_steps": self._total_steps,
            "progress_percentage": self.progress_percentage,
            "current_stage": self._current_stage.value,
            "stage_progress": {stage.value: prog for stage, prog in self._stage_progress.items()},
            "elapsed_time": self.elapsed_time.total_seconds(),
            "current_analyzer": self._current_analyzer
        }
        
        # Add analyzer stats
        stats["analyzers"] = {}
        for analyzer_name in self._analyzer_order:
            stats["analyzers"][analyzer_name] = {
                "progress": self._analyzer_progress[analyzer_name],
                "status": self._analyzer_status[analyzer_name],
                "weight": self._analyzer_weights[analyzer_name],
                "metrics": self._analyzer_metrics[analyzer_name]
            }
        
        # Add processed analyzer count
        stats["processed_analyzers"] = len(self._processed_analyzers)
        stats["total_analyzers"] = len(self._analyzer_order)
        
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
    
    async def _get_visualization_images(self) -> Dict[str, str]:
        """Generate visualization images.
        
        Returns:
            Dictionary mapping visualization names to base64-encoded images.
        """
        # Prepare mock analysis data for visualization
        # In a real implementation, this would use actual analyzer data
        mock_data = {
            "analyzers": {
                name: {
                    "score": self._analyzer_progress[name] * 100,
                    "issues": [],
                    "recommendations": []
                }
                for name in self._analyzer_order
            }
        }
        
        # Generate visualizations
        images = {}
        
        # Score distribution
        score_dist_img = await self._visualizer.visualize_score_distribution(mock_data)
        buf = io.BytesIO()
        score_dist_img.save(buf, format="PNG")
        images["score_distribution"] = base64.b64encode(buf.getvalue()).decode("utf-8")
        
        # Progress by analyzer
        metric_data = {
            name: {"progress": self._analyzer_progress[name] * 100}
            for name in self._analyzer_order
        }
        progress_img = await self._visualizer.visualize_analyzer_metrics(
            metric_data, "progress", "Analyzer Progress (%)"
        )
        buf = io.BytesIO()
        progress_img.save(buf, format="PNG")
        images["analyzer_progress"] = base64.b64encode(buf.getvalue()).decode("utf-8")
        
        return images
    
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
            f"Time remaining: {est_str}",
            f"Analyzers: {len(self._processed_analyzers)}/{len(self._analyzer_order)} completed"
        ]
        
        # Add analyzer progress
        if self._analyzer_order:
            lines.append("\nAnalyzer Progress:")
            for analyzer_name in self._analyzer_order:
                progress_pct = self._analyzer_progress[analyzer_name] * 100
                status = self._analyzer_status[analyzer_name]
                progress_bar = "[" + "#" * int(progress_pct / 5) + " " * (20 - int(progress_pct / 5)) + "]"
                lines.append(f"{analyzer_name}: {progress_bar} {progress_pct:.1f}% - {status}")
        
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
        
        # Create analyzer progress HTML
        analyzers_html = ""
        if self._analyzer_order:
            analyzers_html = "<h5 class='mt-4'>Analyzer Progress</h5>"
            for analyzer_name in self._analyzer_order:
                progress_pct = self._analyzer_progress[analyzer_name] * 100
                status = self._analyzer_status[analyzer_name]
                
                # Set color based on progress
                if progress_pct >= 100:
                    bar_color = "#28a745"  # Green
                elif progress_pct > 0:
                    bar_color = "#007bff"  # Blue
                else:
                    bar_color = "#6c757d"  # Gray
                
                analyzers_html += f"""
                <div class='mb-2'>
                    <div class='d-flex justify-content-between'>
                        <span>{analyzer_name}</span>
                        <span>{status}</span>
                    </div>
                    <div class='progress'>
                        <div class='progress-bar' role='progressbar' style='width: {progress_pct}%; background-color: {bar_color}' 
                            aria-valuenow='{progress_pct}' aria-valuemin='0' aria-valuemax='100'>
                            {progress_pct:.1f}%
                        </div>
                    </div>
                </div>
                """
        
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
                <div class='col-md-6'>
                    <p><strong>Analyzers Completed:</strong> {len(self._processed_analyzers)}/{len(self._analyzer_order)}</p>
                </div>
                <div class='col-md-6'>
                    <p><strong>Current Analyzer:</strong> {self._current_analyzer or "None"}</p>
                </div>
            </div>
            {stages_html}
            {analyzers_html}
            {messages_html}
            {errors_html}
        </div>
        """
        
        return html
    
    async def visualize_with_charts(self) -> str:
        """Generate an HTML visualization with embedded charts.
        
        Returns:
            HTML visualization with embedded charts.
        """
        # Get base HTML visualization
        base_html = self._visualize_html()
        
        # Generate visualization images
        try:
            images = await self._get_visualization_images()
            
            # Create charts HTML
            charts_html = "<div class='row mt-4'>"
            
            if "score_distribution" in images:
                charts_html += f"""
                <div class='col-md-6 mb-3'>
                    <div class='card'>
                        <div class='card-header'>
                            <h5 class='card-title'>Score Distribution</h5>
                        </div>
                        <div class='card-body'>
                            <img src='data:image/png;base64,{images["score_distribution"]}' 
                                 class='img-fluid' alt='Score Distribution'>
                        </div>
                    </div>
                </div>
                """
            
            if "analyzer_progress" in images:
                charts_html += f"""
                <div class='col-md-6 mb-3'>
                    <div class='card'>
                        <div class='card-header'>
                            <h5 class='card-title'>Analyzer Progress</h5>
                        </div>
                        <div class='card-body'>
                            <img src='data:image/png;base64,{images["analyzer_progress"]}' 
                                 class='img-fluid' alt='Analyzer Progress'>
                        </div>
                    </div>
                </div>
                """
            
            charts_html += "</div>"
            
            # Insert charts before the closing div
            html = base_html.replace("</div>", f"{charts_html}</div>")
            return html
            
        except Exception as e:
            # Fall back to base HTML if visualization fails
            return base_html 