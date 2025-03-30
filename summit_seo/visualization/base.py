"""Base classes for visualization components."""

import abc
from enum import Enum
from typing import Dict, Any, List, Optional, Union, Tuple

class ChartType(str, Enum):
    """Types of charts supported by the visualization system."""

    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    RADAR = "radar"
    HEATMAP = "heatmap"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"
    AREA = "area"
    DONUT = "donut"
    BUBBLE = "bubble"
    GAUGE = "gauge"
    TREEMAP = "treemap"
    FUNNEL = "funnel"


class VisualizationError(Exception):
    """Base exception for all visualization errors."""
    pass


class BaseVisualizer(abc.ABC):
    """Base class for all visualization components."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the visualizer.
        
        Args:
            config: Optional configuration dictionary.
        """
        self.config = config or {}
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate the visualizer configuration.
        
        Raises:
            ValueError: If configuration is invalid.
        """
        pass  # Override in subclasses
    
    @abc.abstractmethod
    async def generate_chart(self, data: Dict[str, Any], chart_type: ChartType) -> Dict[str, Any]:
        """Generate a chart from the provided data.
        
        Args:
            data: The data to visualize.
            chart_type: The type of chart to generate.
            
        Returns:
            Dictionary with chart data.
            
        Raises:
            VisualizationError: If chart generation fails.
        """
        pass
    
    @abc.abstractmethod
    async def generate_multiple_charts(self, data: Dict[str, Any], 
                                     chart_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate multiple charts from the provided data.
        
        Args:
            data: The data to visualize.
            chart_configs: List of chart configuration dictionaries.
                Each dictionary should contain at least 'type' (ChartType).
            
        Returns:
            Dictionary with multiple chart data.
            
        Raises:
            VisualizationError: If chart generation fails.
        """
        pass
    
    @abc.abstractmethod
    async def generate_dashboard(self, data: Dict[str, Any], 
                               layout: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a dashboard with multiple visualizations.
        
        Args:
            data: The data to visualize.
            layout: Optional layout configuration.
            
        Returns:
            Dictionary with dashboard data.
            
        Raises:
            VisualizationError: If dashboard generation fails.
        """
        pass
    
    def _prepare_chart_data(self, data: Dict[str, Any], 
                           chart_type: ChartType) -> Dict[str, Any]:
        """Prepare data for chart generation.
        
        Args:
            data: The raw data.
            chart_type: The chart type.
            
        Returns:
            Prepared data for chart generation.
        """
        # Default implementation just returns the data
        # Override in subclasses for specific data transformations
        return data
    
    def _get_chart_options(self, chart_type: ChartType) -> Dict[str, Any]:
        """Get default options for a specific chart type.
        
        Args:
            chart_type: The chart type.
            
        Returns:
            Dictionary with chart options.
        """
        # Default implementation returns empty options
        # Override in subclasses for type-specific options
        return {} 