"""Matplotlib-based visualizer implementation."""

import io
import base64
from typing import Dict, Any, List, Optional, Union, Tuple
import json
import logging

from .base import BaseVisualizer, ChartType, VisualizationError

logger = logging.getLogger(__name__)

class MatplotlibVisualizer(BaseVisualizer):
    """Visualizer implementation using Matplotlib."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Matplotlib visualizer.
        
        Args:
            config: Optional configuration dictionary. Supported keys:
                - figure_size: Tuple of (width, height) in inches
                - dpi: Dots per inch for rendering
                - style: Matplotlib style sheet name
                - font_size: Base font size
                - colormap: Colormap name
                - output_format: 'png', 'svg', 'pdf', etc.
                - include_base64: Whether to include base64-encoded image
        """
        super().__init__(config)
        self.figure_size = self.config.get('figure_size', (8, 6))
        self.dpi = self.config.get('dpi', 100)
        self.style = self.config.get('style', 'seaborn-v0_8-whitegrid')
        self.font_size = self.config.get('font_size', 10)
        self.colormap = self.config.get('colormap', 'viridis')
        self.output_format = self.config.get('output_format', 'png')
        self.include_base64 = self.config.get('include_base64', True)
    
    def _validate_config(self) -> None:
        """Validate visualizer configuration."""
        if 'figure_size' in self.config and not isinstance(self.config['figure_size'], tuple):
            raise ValueError("figure_size must be a tuple of (width, height)")
            
        if 'dpi' in self.config and not isinstance(self.config['dpi'], int):
            raise ValueError("dpi must be an integer")
            
        if 'font_size' in self.config and not isinstance(self.config['font_size'], (int, float)):
            raise ValueError("font_size must be a number")
            
        if 'output_format' in self.config and self.config['output_format'] not in ('png', 'svg', 'pdf', 'jpg'):
            raise ValueError("output_format must be one of: 'png', 'svg', 'pdf', 'jpg'")
    
    async def generate_chart(self, data: Dict[str, Any], chart_type: ChartType) -> Dict[str, Any]:
        """Generate a chart using Matplotlib.
        
        Args:
            data: Data to visualize.
            chart_type: Type of chart to generate.
            
        Returns:
            Dictionary with chart data.
            
        Raises:
            VisualizationError: If chart generation fails.
        """
        try:
            # We import matplotlib here to avoid making it a hard dependency
            try:
                import matplotlib
                import matplotlib.pyplot as plt
                import numpy as np
                import pandas as pd
            except ImportError:
                raise VisualizationError(
                    "Matplotlib is required for MatplotlibVisualizer. "
                    "Install with 'pip install matplotlib pandas numpy'"
                )
            
            # Use non-interactive backend
            matplotlib.use('Agg')
            
            # Set style
            plt.style.use(self.style)
            
            # Prepare data for the specific chart type
            prepared_data = self._prepare_chart_data(data, chart_type)
            
            # Create figure
            fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
            
            # Generate the appropriate chart
            chart_title = prepared_data.get('title', 'Chart')
            
            if chart_type == ChartType.BAR:
                self._create_bar_chart(ax, prepared_data)
            elif chart_type == ChartType.LINE:
                self._create_line_chart(ax, prepared_data)
            elif chart_type == ChartType.PIE:
                self._create_pie_chart(ax, prepared_data)
            elif chart_type == ChartType.SCATTER:
                self._create_scatter_chart(ax, prepared_data)
            elif chart_type == ChartType.HISTOGRAM:
                self._create_histogram_chart(ax, prepared_data)
            elif chart_type == ChartType.AREA:
                self._create_area_chart(ax, prepared_data)
            else:
                raise VisualizationError(f"Chart type {chart_type} not implemented for Matplotlib visualizer")
            
            # Add title if provided
            if chart_title:
                plt.title(chart_title)
            
            # Add labels if provided
            if 'x_label' in prepared_data:
                plt.xlabel(prepared_data['x_label'])
            if 'y_label' in prepared_data:
                plt.ylabel(prepared_data['y_label'])
            
            # Add legend if needed
            if prepared_data.get('show_legend', True):
                plt.legend()
            
            # Set tight layout
            plt.tight_layout()
            
            # Convert to output format
            buffer = io.BytesIO()
            plt.savefig(buffer, format=self.output_format)
            buffer.seek(0)
            
            # Close the figure to free memory
            plt.close(fig)
            
            result = {
                'chart_type': chart_type.value,
                'format': self.output_format,
            }
            
            # Add base64 encoded image if requested
            if self.include_base64:
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                result['image_base64'] = image_base64
                
                # Add data URI for easy embedding in HTML
                data_uri = f"data:image/{self.output_format};base64,{image_base64}"
                result['data_uri'] = data_uri
            
            return result
            
        except Exception as e:
            logger.exception(f"Error generating {chart_type} chart with Matplotlib")
            raise VisualizationError(f"Failed to generate chart: {str(e)}") from e
    
    async def generate_multiple_charts(self, data: Dict[str, Any], 
                                    chart_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate multiple charts using Matplotlib.
        
        Args:
            data: Data to visualize.
            chart_configs: List of chart configuration dictionaries.
                Each should contain at least 'type' (ChartType).
            
        Returns:
            Dictionary with multiple chart data.
            
        Raises:
            VisualizationError: If chart generation fails.
        """
        try:
            results = []
            
            for config in chart_configs:
                chart_type = ChartType(config['type'])
                chart_data = config.get('data', data)
                
                # Generate individual chart
                chart_result = await self.generate_chart(chart_data, chart_type)
                results.append(chart_result)
            
            return {
                'charts': results,
                'count': len(results)
            }
        
        except Exception as e:
            logger.exception("Error generating multiple charts with Matplotlib")
            raise VisualizationError(f"Failed to generate multiple charts: {str(e)}") from e
    
    async def generate_dashboard(self, data: Dict[str, Any], 
                              layout: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a dashboard with multiple visualizations using Matplotlib.
        
        Args:
            data: Data to visualize.
            layout: Optional layout configuration.
            
        Returns:
            Dictionary with dashboard data.
            
        Raises:
            VisualizationError: If dashboard generation fails.
        """
        try:
            # Import matplotlib here
            try:
                import matplotlib
                import matplotlib.pyplot as plt
                import numpy as np
                import pandas as pd
            except ImportError:
                raise VisualizationError(
                    "Matplotlib is required for MatplotlibVisualizer. "
                    "Install with 'pip install matplotlib pandas numpy'"
                )
            
            # Use non-interactive backend
            matplotlib.use('Agg')
            
            # Set style
            plt.style.use(self.style)
            
            # Get layout configuration or use defaults
            layout = layout or {}
            rows = layout.get('rows', 2)
            cols = layout.get('cols', 2)
            charts = layout.get('charts', [])
            
            if not charts:
                raise VisualizationError("No charts specified in layout")
            
            # Create figure with subplots
            fig, axes = plt.subplots(rows, cols, figsize=(self.figure_size[0] * cols, 
                                                       self.figure_size[1] * rows), 
                                     dpi=self.dpi)
            
            # Convert to 2D array if 1D
            if rows == 1 and cols == 1:
                axes = np.array([[axes]])
            elif rows == 1:
                axes = np.array([axes])
            elif cols == 1:
                axes = np.array([[ax] for ax in axes])
            
            # Generate each chart in its subplot
            for i, chart_config in enumerate(charts):
                if i >= rows * cols:
                    logger.warning(f"Dashboard has more charts than subplots (max: {rows*cols})")
                    break
                
                row = i // cols
                col = i % cols
                ax = axes[row, col]
                
                chart_type = ChartType(chart_config['type'])
                chart_data = chart_config.get('data', data)
                
                # Prepare data
                prepared_data = self._prepare_chart_data(chart_data, chart_type)
                
                # Create the chart
                if chart_type == ChartType.BAR:
                    self._create_bar_chart(ax, prepared_data)
                elif chart_type == ChartType.LINE:
                    self._create_line_chart(ax, prepared_data)
                elif chart_type == ChartType.PIE:
                    self._create_pie_chart(ax, prepared_data)
                elif chart_type == ChartType.SCATTER:
                    self._create_scatter_chart(ax, prepared_data)
                elif chart_type == ChartType.HISTOGRAM:
                    self._create_histogram_chart(ax, prepared_data)
                elif chart_type == ChartType.AREA:
                    self._create_area_chart(ax, prepared_data)
                else:
                    logger.warning(f"Chart type {chart_type} not implemented for Matplotlib visualizer")
                    ax.text(0.5, 0.5, f"Unsupported chart: {chart_type}", 
                           ha='center', va='center', transform=ax.transAxes)
                
                # Add title
                if 'title' in chart_config:
                    ax.set_title(chart_config['title'])
                
                # Add labels
                if 'x_label' in chart_config:
                    ax.set_xlabel(chart_config['x_label'])
                if 'y_label' in chart_config:
                    ax.set_ylabel(chart_config['y_label'])
                
                # Add legend if needed
                if chart_config.get('show_legend', True):
                    ax.legend()
            
            # Hide any unused subplots
            for i in range(len(charts), rows * cols):
                row = i // cols
                col = i % cols
                axes[row, col].axis('off')
            
            # Set tight layout
            plt.tight_layout()
            
            # Convert to output format
            buffer = io.BytesIO()
            plt.savefig(buffer, format=self.output_format)
            buffer.seek(0)
            
            # Close the figure to free memory
            plt.close(fig)
            
            result = {
                'type': 'dashboard',
                'format': self.output_format,
                'layout': {
                    'rows': rows,
                    'cols': cols,
                    'chart_count': len(charts),
                }
            }
            
            # Add base64 encoded image if requested
            if self.include_base64:
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                result['image_base64'] = image_base64
                
                # Add data URI for easy embedding in HTML
                data_uri = f"data:image/{self.output_format};base64,{image_base64}"
                result['data_uri'] = data_uri
            
            return result
            
        except Exception as e:
            logger.exception("Error generating dashboard with Matplotlib")
            raise VisualizationError(f"Failed to generate dashboard: {str(e)}") from e
    
    # Helper methods for specific chart types
    
    def _create_bar_chart(self, ax, data):
        """Create a bar chart on the given axes."""
        x = data.get('x', [])
        y = data.get('y', [])
        
        if len(x) != len(y):
            raise VisualizationError("x and y must have the same length for bar chart")
        
        color = data.get('color', 'steelblue')
        width = data.get('width', 0.8)
        
        ax.bar(x, y, width=width, color=color)
    
    def _create_line_chart(self, ax, data):
        """Create a line chart on the given axes."""
        x = data.get('x', [])
        y = data.get('y', [])
        
        if len(x) != len(y):
            raise VisualizationError("x and y must have the same length for line chart")
        
        color = data.get('color', 'steelblue')
        marker = data.get('marker', 'o')
        line_style = data.get('line_style', '-')
        line_width = data.get('line_width', 2)
        
        ax.plot(x, y, marker=marker, linestyle=line_style, 
               linewidth=line_width, color=color)
    
    def _create_pie_chart(self, ax, data):
        """Create a pie chart on the given axes."""
        values = data.get('values', [])
        labels = data.get('labels', [])
        
        if len(values) != len(labels):
            raise VisualizationError("values and labels must have the same length for pie chart")
        
        explode = data.get('explode', None)
        colors = data.get('colors', None)
        autopct = data.get('autopct', '%1.1f%%')
        
        ax.pie(values, labels=labels, explode=explode, colors=colors,
              autopct=autopct, shadow=data.get('shadow', False))
        ax.axis('equal')
    
    def _create_scatter_chart(self, ax, data):
        """Create a scatter chart on the given axes."""
        x = data.get('x', [])
        y = data.get('y', [])
        
        if len(x) != len(y):
            raise VisualizationError("x and y must have the same length for scatter chart")
        
        color = data.get('color', 'steelblue')
        marker = data.get('marker', 'o')
        alpha = data.get('alpha', 0.7)
        sizes = data.get('sizes', None)
        
        ax.scatter(x, y, s=sizes, alpha=alpha, color=color, marker=marker)
    
    def _create_histogram_chart(self, ax, data):
        """Create a histogram chart on the given axes."""
        values = data.get('values', [])
        bins = data.get('bins', 10)
        color = data.get('color', 'steelblue')
        alpha = data.get('alpha', 0.7)
        
        ax.hist(values, bins=bins, color=color, alpha=alpha)
    
    def _create_area_chart(self, ax, data):
        """Create an area chart on the given axes."""
        x = data.get('x', [])
        y = data.get('y', [])
        
        if len(x) != len(y):
            raise VisualizationError("x and y must have the same length for area chart")
        
        color = data.get('color', 'steelblue')
        alpha = data.get('alpha', 0.3)
        
        ax.fill_between(x, y, color=color, alpha=alpha)
        ax.plot(x, y, color=color) 