"""Base classes and interfaces for progress tracking."""

import abc
import enum
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union


class ProgressError(Exception):
    """Base exception class for progress tracking errors."""
    pass


class ProgressState(enum.Enum):
    """Enumeration of possible progress states."""
    NOT_STARTED = "not_started"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProgressStage(enum.Enum):
    """Enumeration of analysis stages for tracking."""
    INITIALIZATION = "initialization"
    COLLECTION = "collection"
    PROCESSING = "processing"
    ANALYSIS = "analysis"
    REPORTING = "reporting"
    CLEANUP = "cleanup"


class ProgressTracker(abc.ABC):
    """Abstract base class for progress tracking implementations.
    
    This class defines the interface for progress tracking components.
    Implementations should handle tracking of progress, time estimation,
    and status reporting for analysis operations.
    """
    
    def __init__(self, total_steps: int = 100, name: str = "Analysis Progress"):
        """Initialize the progress tracker.
        
        Args:
            total_steps: Total number of steps to track.
            name: Name of the operation being tracked.
        """
        self._name = name
        self._total_steps = total_steps
        self._current_step = 0
        self._state = ProgressState.NOT_STARTED
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None
        self._pause_time: Optional[float] = None
        self._pause_duration: float = 0.0
        self._current_stage = ProgressStage.INITIALIZATION
        self._stage_progress: Dict[ProgressStage, float] = {
            stage: 0.0 for stage in ProgressStage
        }
        self._stage_weights: Dict[ProgressStage, float] = {
            ProgressStage.INITIALIZATION: 0.05,
            ProgressStage.COLLECTION: 0.15,
            ProgressStage.PROCESSING: 0.2,
            ProgressStage.ANALYSIS: 0.4,
            ProgressStage.REPORTING: 0.15,
            ProgressStage.CLEANUP: 0.05
        }
        self._messages: List[Tuple[datetime, str]] = []
        self._errors: List[Tuple[datetime, str]] = []
        
    @property
    def name(self) -> str:
        """Get the name of the operation being tracked."""
        return self._name
        
    @property
    def total_steps(self) -> int:
        """Get the total number of steps to track."""
        return self._total_steps
        
    @property
    def current_step(self) -> int:
        """Get the current step."""
        return self._current_step
        
    @property
    def progress_percentage(self) -> float:
        """Get the progress percentage (0-100)."""
        if self._total_steps == 0:
            return 0.0
        return min(100.0, (self._current_step / self._total_steps) * 100.0)
    
    @property
    def state(self) -> ProgressState:
        """Get the current progress state."""
        return self._state
    
    @property
    def current_stage(self) -> ProgressStage:
        """Get the current analysis stage."""
        return self._current_stage
    
    @property
    def start_time(self) -> Optional[datetime]:
        """Get the start time as a datetime object, or None if not started."""
        if self._start_time is None:
            return None
        return datetime.fromtimestamp(self._start_time)
    
    @property
    def elapsed_time(self) -> timedelta:
        """Get the elapsed time as a timedelta object."""
        if self._start_time is None:
            return timedelta(0)
        
        if self._end_time is not None:
            # If completed, use the end time
            elapsed = self._end_time - self._start_time
        elif self._state == ProgressState.PAUSED and self._pause_time is not None:
            # If paused, use the pause time
            elapsed = self._pause_time - self._start_time
        else:
            # Otherwise, use the current time
            elapsed = time.time() - self._start_time
            
        # Subtract any pause duration
        elapsed -= self._pause_duration
        
        return timedelta(seconds=max(0, elapsed))
    
    @property
    def messages(self) -> List[Tuple[datetime, str]]:
        """Get all progress messages."""
        return self._messages.copy()
    
    @property
    def errors(self) -> List[Tuple[datetime, str]]:
        """Get all error messages."""
        return self._errors.copy()
    
    def start(self) -> None:
        """Start or resume progress tracking."""
        if self._state == ProgressState.NOT_STARTED:
            self._start_time = time.time()
            self._state = ProgressState.RUNNING
            self._add_message("Started progress tracking")
        elif self._state == ProgressState.PAUSED and self._pause_time is not None:
            # Resume from pause, add the paused time to total pause duration
            self._pause_duration += time.time() - self._pause_time
            self._pause_time = None
            self._state = ProgressState.RUNNING
            self._add_message("Resumed progress tracking")
        else:
            raise ProgressError(f"Cannot start from current state: {self._state}")
    
    def pause(self) -> None:
        """Pause progress tracking."""
        if self._state != ProgressState.RUNNING:
            raise ProgressError(f"Cannot pause from current state: {self._state}")
        
        self._state = ProgressState.PAUSED
        self._pause_time = time.time()
        self._add_message("Paused progress tracking")
    
    def complete(self) -> None:
        """Mark progress tracking as completed."""
        if self._state not in (ProgressState.RUNNING, ProgressState.PAUSED):
            raise ProgressError(f"Cannot complete from current state: {self._state}")
        
        self._current_step = self._total_steps
        self._state = ProgressState.COMPLETED
        self._end_time = time.time()
        
        if self._state == ProgressState.PAUSED and self._pause_time is not None:
            self._pause_duration += time.time() - self._pause_time
            
        self._add_message("Completed progress tracking")
    
    def cancel(self) -> None:
        """Cancel progress tracking."""
        if self._state in (ProgressState.COMPLETED, ProgressState.FAILED, ProgressState.CANCELLED):
            raise ProgressError(f"Cannot cancel from current state: {self._state}")
        
        self._state = ProgressState.CANCELLED
        self._end_time = time.time()
        
        if self._state == ProgressState.PAUSED and self._pause_time is not None:
            self._pause_duration += time.time() - self._pause_time
            
        self._add_message("Cancelled progress tracking")
    
    def fail(self, error_message: str) -> None:
        """Mark progress tracking as failed with an error message."""
        if self._state in (ProgressState.COMPLETED, ProgressState.FAILED, ProgressState.CANCELLED):
            raise ProgressError(f"Cannot fail from current state: {self._state}")
        
        self._state = ProgressState.FAILED
        self._end_time = time.time()
        
        if self._state == ProgressState.PAUSED and self._pause_time is not None:
            self._pause_duration += time.time() - self._pause_time
            
        self._add_error(error_message)
        self._add_message(f"Failed progress tracking: {error_message}")
    
    def update(self, step: int, message: Optional[str] = None) -> None:
        """Update the current progress step.
        
        Args:
            step: The current step (0 to total_steps).
            message: Optional message to record with the update.
        """
        if self._state != ProgressState.RUNNING:
            raise ProgressError(f"Cannot update from current state: {self._state}")
        
        if step < 0 or step > self._total_steps:
            raise ProgressError(f"Step must be between 0 and {self._total_steps}")
        
        self._current_step = step
        
        if message:
            self._add_message(message)
    
    def increment(self, steps: int = 1, message: Optional[str] = None) -> None:
        """Increment the current progress step.
        
        Args:
            steps: Number of steps to increment by.
            message: Optional message to record with the update.
        """
        if self._state != ProgressState.RUNNING:
            raise ProgressError(f"Cannot increment from current state: {self._state}")
        
        new_step = min(self._total_steps, self._current_step + steps)
        self.update(new_step, message)
    
    def set_stage(self, stage: ProgressStage, progress: float = 0.0) -> None:
        """Set the current analysis stage.
        
        Args:
            stage: The current stage of analysis.
            progress: Progress within this stage (0.0 to 1.0).
        """
        if self._state != ProgressState.RUNNING:
            raise ProgressError(f"Cannot set stage from current state: {self._state}")
        
        if progress < 0.0 or progress > 1.0:
            raise ProgressError("Stage progress must be between 0.0 and 1.0")
        
        self._current_stage = stage
        self._stage_progress[stage] = progress
        self._add_message(f"Moved to stage: {stage.value} ({progress:.1%} complete)")
        
        # Recalculate overall progress based on stage weights
        total_weighted_progress = sum(
            self._stage_progress[s] * self._stage_weights[s]
            for s in ProgressStage
        )
        
        # Update the current step based on weighted progress
        self._current_step = int(total_weighted_progress * self._total_steps)
    
    def update_stage_progress(self, progress: float) -> None:
        """Update progress within the current stage.
        
        Args:
            progress: Progress within this stage (0.0 to 1.0).
        """
        if self._state != ProgressState.RUNNING:
            raise ProgressError(f"Cannot update stage from current state: {self._state}")
        
        if progress < 0.0 or progress > 1.0:
            raise ProgressError("Stage progress must be between 0.0 and 1.0")
        
        self._stage_progress[self._current_stage] = progress
        
        # Recalculate overall progress based on stage weights
        total_weighted_progress = sum(
            self._stage_progress[s] * self._stage_weights[s]
            for s in ProgressStage
        )
        
        # Update the current step based on weighted progress
        self._current_step = int(total_weighted_progress * self._total_steps)
    
    def set_stage_weights(self, weights: Dict[ProgressStage, float]) -> None:
        """Set custom weights for each analysis stage.
        
        Args:
            weights: Dictionary mapping stages to weight values.
                    Weights should sum to 1.0.
        """
        if abs(sum(weights.values()) - 1.0) > 0.001:
            raise ProgressError("Stage weights must sum to 1.0")
        
        # Ensure all stages have a weight
        for stage in ProgressStage:
            if stage not in weights:
                raise ProgressError(f"Missing weight for stage: {stage}")
        
        self._stage_weights = weights.copy()
        
        # Recalculate progress with new weights
        self.update_stage_progress(self._stage_progress[self._current_stage])
    
    def _add_message(self, message: str) -> None:
        """Add a message to the message log.
        
        Args:
            message: Message to add.
        """
        self._messages.append((datetime.now(), message))
    
    def _add_error(self, error: str) -> None:
        """Add an error to the error log.
        
        Args:
            error: Error message to add.
        """
        self._errors.append((datetime.now(), error))
    
    @abc.abstractmethod
    def get_estimated_time_remaining(self) -> Optional[timedelta]:
        """Get the estimated time remaining.
        
        Returns:
            Estimated time remaining as a timedelta, or None if not available.
        """
        pass
    
    @abc.abstractmethod
    def get_progress_stats(self) -> Dict[str, Any]:
        """Get detailed progress statistics.
        
        Returns:
            Dictionary containing detailed progress statistics.
        """
        pass
    
    @abc.abstractmethod
    def visualize(self, format: str = "text") -> Union[str, bytes]:
        """Generate a visualization of the progress.
        
        Args:
            format: Format for the visualization ("text", "html", "image").
            
        Returns:
            Visualization data in the specified format.
        """
        pass 