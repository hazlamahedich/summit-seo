"""Visualization utilities for analyzer results."""

from enum import Enum
from typing import Dict, Any, List, Optional, Union
import logging

from .base import ChartType
from .factory import VisualizationFactory

logger = logging.getLogger(__name__)

class VisualizationType(Enum):
    """Types of visualizations available for analyzer results."""
    SCORE_DISTRIBUTION = "score_distribution"
    ISSUE_SEVERITY = "issue_severity"
    RECOMMENDATION_PRIORITY = "recommendation_priority"
    ANALYZER_METRICS = "analyzer_metrics"
    QUICK_WINS = "quick_wins"
    DASHBOARD = "dashboard"

class AnalyzerVisualization:
    """Utility class for visualizing analyzer results."""
    
    def __init__(self, visualizer_name: str = 'matplotlib', 
                visualizer_config: Optional[Dict[str, Any]] = None):
        """Initialize analyzer visualization.
        
        Args:
            visualizer_name: Name of the visualizer to use.
            visualizer_config: Configuration for the visualizer.
        """
        self.visualizer_name = visualizer_name
        self.visualizer_config = visualizer_config or {}
        self.visualizer = VisualizationFactory.create(visualizer_name, visualizer_config)
    
    async def visualize_score_distribution(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Visualize the score distribution for multiple analyzers.
        
        Args:
            analysis_results: Analysis results from multiple analyzers.
            
        Returns:
            Visualization result.
        """
        # Extract analyzer names and scores
        analyzer_names = []
        scores = []
        
        for analyzer_name, result in analysis_results.items():
            if isinstance(result, dict) and 'score' in result:
                analyzer_names.append(analyzer_name.replace('_analyzer', '').title())
                scores.append(result['score'])
        
        if not analyzer_names:
            logger.warning("No valid scores found in analysis results")
            return {'error': 'No valid scores found'}
        
        # Prepare data for visualization
        data = {
            'x': analyzer_names,
            'y': scores,
            'title': 'Score Distribution by Analyzer',
            'x_label': 'Analyzer',
            'y_label': 'Score',
            'color': 'steelblue'
        }
        
        # Generate bar chart
        return await self.visualizer.generate_chart(data, ChartType.BAR)
    
    async def visualize_issue_severity(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Visualize issue severity distribution.
        
        Args:
            analysis_results: Analysis results from multiple analyzers.
            
        Returns:
            Visualization result.
        """
        # Track severity counts
        severity_counts = {
            'Critical': 0,
            'High': 0,
            'Medium': 0,
            'Low': 0,
            'Info': 0
        }
        
        # Process enhanced recommendations if available
        for analyzer_name, result in analysis_results.items():
            if isinstance(result, dict) and 'enhanced_recommendations' in result:
                for rec in result['enhanced_recommendations']:
                    if isinstance(rec, dict) and 'severity' in rec:
                        severity = rec['severity'].title()
                        if severity in severity_counts:
                            severity_counts[severity] += 1
            
            # Also check if there are legacy recommendations with severity info
            # This is a simplistic approach - in practice would need more complex parsing
            if isinstance(result, dict) and 'issues' in result:
                severity_counts['High'] += len(result['issues'])
            if isinstance(result, dict) and 'warnings' in result:
                severity_counts['Medium'] += len(result['warnings'])
            if isinstance(result, dict) and 'suggestions' in result:
                severity_counts['Low'] += len(result['suggestions'])
        
        # Prepare data for visualization
        data = {
            'values': list(severity_counts.values()),
            'labels': list(severity_counts.keys()),
            'title': 'Issues by Severity',
            'colors': ['#d62728', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a']
        }
        
        # Generate pie chart
        return await self.visualizer.generate_chart(data, ChartType.PIE)
    
    async def visualize_analyzer_metrics(self, analysis_results: Dict[str, Any],
                                      metric_key: str, title: Optional[str] = None) -> Dict[str, Any]:
        """Visualize specific metrics from analyzer results.
        
        Args:
            analysis_results: Analysis results from multiple analyzers.
            metric_key: The key for the metric to visualize.
            title: Optional chart title.
            
        Returns:
            Visualization result.
        """
        # Extract analyzer names and metric values
        analyzer_names = []
        metric_values = []
        
        for analyzer_name, result in analysis_results.items():
            if isinstance(result, dict) and 'metrics' in result and metric_key in result['metrics']:
                analyzer_names.append(analyzer_name.replace('_analyzer', '').title())
                metric_values.append(result['metrics'][metric_key])
        
        if not analyzer_names:
            logger.warning(f"No valid metric '{metric_key}' found in analysis results")
            return {'error': f"No valid metric '{metric_key}' found"}
        
        # Prepare data for visualization
        data = {
            'x': analyzer_names,
            'y': metric_values,
            'title': title or f'{metric_key.replace("_", " ").title()} by Analyzer',
            'x_label': 'Analyzer',
            'y_label': metric_key.replace('_', ' ').title(),
        }
        
        # Generate bar or line chart depending on the data
        chart_type = ChartType.LINE if len(analyzer_names) > 5 else ChartType.BAR
        
        return await self.visualizer.generate_chart(data, chart_type)
    
    async def visualize_recommendation_priority(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Visualize recommendation priority distribution.
        
        Args:
            analysis_results: Analysis results from multiple analyzers.
            
        Returns:
            Visualization result.
        """
        # Track priority counts
        priority_counts = {
            'P0': 0,
            'P1': 0,
            'P2': 0,
            'P3': 0,
            'P4': 0
        }
        
        # Process enhanced recommendations if available
        for analyzer_name, result in analysis_results.items():
            if isinstance(result, dict) and 'enhanced_recommendations' in result:
                for rec in result['enhanced_recommendations']:
                    if isinstance(rec, dict) and 'priority' in rec:
                        priority = rec['priority'].upper()
                        if priority in priority_counts:
                            priority_counts[priority] += 1
        
        # Prepare data for visualization
        data = {
            'x': list(priority_counts.keys()),
            'y': list(priority_counts.values()),
            'title': 'Recommendations by Priority',
            'x_label': 'Priority Level',
            'y_label': 'Count',
            'color': 'darkorange'
        }
        
        # Generate bar chart
        return await self.visualizer.generate_chart(data, ChartType.BAR)
    
    async def visualize_quick_wins(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Visualize quick win recommendations by count.
        
        Args:
            analysis_results: Analysis results from multiple analyzers.
            
        Returns:
            Visualization result.
        """
        # Track quick win counts by analyzer
        analyzer_names = []
        quick_win_counts = []
        
        for analyzer_name, result in analysis_results.items():
            if isinstance(result, dict) and 'enhanced_recommendations' in result:
                quick_wins = 0
                for rec in result['enhanced_recommendations']:
                    if isinstance(rec, dict) and rec.get('quick_win', False):
                        quick_wins += 1
                
                if quick_wins > 0:
                    analyzer_names.append(analyzer_name.replace('_analyzer', '').title())
                    quick_win_counts.append(quick_wins)
        
        if not analyzer_names:
            logger.warning("No quick wins found in analysis results")
            return {'error': 'No quick wins found'}
        
        # Prepare data for visualization
        data = {
            'x': analyzer_names,
            'y': quick_win_counts,
            'title': 'Quick Win Opportunities by Analyzer',
            'x_label': 'Analyzer',
            'y_label': 'Quick Win Count',
            'color': 'forestgreen'
        }
        
        # Generate bar chart
        return await self.visualizer.generate_chart(data, ChartType.BAR)
    
    async def generate_analyzer_dashboard(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive dashboard for analyzer results.
        
        Args:
            analysis_results: Analysis results from multiple analyzers.
            
        Returns:
            Dashboard visualization result.
        """
        # Define chart configurations for the dashboard
        chart_configs = [
            {
                'type': ChartType.BAR.value,
                'title': 'Score Distribution',
                'data': await self._prepare_score_distribution_data(analysis_results),
                'x_label': 'Analyzer',
                'y_label': 'Score'
            },
            {
                'type': ChartType.PIE.value,
                'title': 'Issues by Severity',
                'data': await self._prepare_severity_data(analysis_results)
            },
            {
                'type': ChartType.BAR.value,
                'title': 'Recommendations by Priority',
                'data': await self._prepare_priority_data(analysis_results),
                'x_label': 'Priority',
                'y_label': 'Count'
            },
            {
                'type': ChartType.BAR.value,
                'title': 'Quick Win Opportunities',
                'data': await self._prepare_quick_win_data(analysis_results),
                'x_label': 'Analyzer',
                'y_label': 'Count'
            }
        ]
        
        # Define layout for the dashboard
        layout = {
            'rows': 2,
            'cols': 2,
            'charts': chart_configs
        }
        
        # Generate the dashboard
        return await self.visualizer.generate_dashboard(analysis_results, layout)
    
    # Helper methods for preparing data
    
    async def _prepare_score_distribution_data(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for score distribution visualization."""
        analyzer_names = []
        scores = []
        
        for analyzer_name, result in analysis_results.items():
            if isinstance(result, dict) and 'score' in result:
                analyzer_names.append(analyzer_name.replace('_analyzer', '').title())
                scores.append(result['score'])
        
        return {
            'x': analyzer_names,
            'y': scores,
            'color': 'steelblue'
        }
    
    async def _prepare_severity_data(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for severity visualization."""
        severity_counts = {
            'Critical': 0,
            'High': 0,
            'Medium': 0,
            'Low': 0,
            'Info': 0
        }
        
        for analyzer_name, result in analysis_results.items():
            if isinstance(result, dict) and 'enhanced_recommendations' in result:
                for rec in result['enhanced_recommendations']:
                    if isinstance(rec, dict) and 'severity' in rec:
                        severity = rec['severity'].title()
                        if severity in severity_counts:
                            severity_counts[severity] += 1
            
            # Also check legacy recommendations
            if isinstance(result, dict) and 'issues' in result:
                severity_counts['High'] += len(result['issues'])
            if isinstance(result, dict) and 'warnings' in result:
                severity_counts['Medium'] += len(result['warnings'])
            if isinstance(result, dict) and 'suggestions' in result:
                severity_counts['Low'] += len(result['suggestions'])
        
        return {
            'values': list(severity_counts.values()),
            'labels': list(severity_counts.keys()),
            'colors': ['#d62728', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a']
        }
    
    async def _prepare_priority_data(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for priority visualization."""
        priority_counts = {
            'P0': 0,
            'P1': 0,
            'P2': 0,
            'P3': 0,
            'P4': 0
        }
        
        for analyzer_name, result in analysis_results.items():
            if isinstance(result, dict) and 'enhanced_recommendations' in result:
                for rec in result['enhanced_recommendations']:
                    if isinstance(rec, dict) and 'priority' in rec:
                        priority = rec['priority'].upper()
                        if priority in priority_counts:
                            priority_counts[priority] += 1
        
        return {
            'x': list(priority_counts.keys()),
            'y': list(priority_counts.values()),
            'color': 'darkorange'
        }
    
    async def _prepare_quick_win_data(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for quick win visualization."""
        analyzer_names = []
        quick_win_counts = []
        
        for analyzer_name, result in analysis_results.items():
            if isinstance(result, dict) and 'enhanced_recommendations' in result:
                quick_wins = 0
                for rec in result['enhanced_recommendations']:
                    if isinstance(rec, dict) and rec.get('quick_win', False):
                        quick_wins += 1
                
                if quick_wins > 0:
                    analyzer_names.append(analyzer_name.replace('_analyzer', '').title())
                    quick_win_counts.append(quick_wins)
        
        return {
            'x': analyzer_names,
            'y': quick_win_counts,
            'color': 'forestgreen'
        }
        
    async def create_visualization(self, data: Dict[str, Any], 
                                 visualization_type: VisualizationType,
                                 output_path: Optional[str] = None,
                                 title: Optional[str] = None,
                                 **kwargs) -> Dict[str, Any]:
        """Create a visualization based on the specified type.
        
        Args:
            data: Analysis data to visualize.
            visualization_type: Type of visualization to create.
            output_path: Optional path to save the visualization.
            title: Optional title for the visualization.
            **kwargs: Additional keyword arguments for specific visualizations.
            
        Returns:
            Visualization result.
            
        Raises:
            ValueError: If visualization type is not supported.
        """
        result = None
        
        # Handle different visualization types
        if visualization_type == VisualizationType.SCORE_DISTRIBUTION:
            result = await self.visualize_score_distribution(data.get('results', {}))
        elif visualization_type == VisualizationType.ISSUE_SEVERITY:
            result = await self.visualize_issue_severity(data.get('results', {}))
        elif visualization_type == VisualizationType.RECOMMENDATION_PRIORITY:
            result = await self.visualize_recommendation_priority(data.get('results', {}))
        elif visualization_type == VisualizationType.QUICK_WINS:
            result = await self.visualize_quick_wins(data.get('results', {}))
        elif visualization_type == VisualizationType.ANALYZER_METRICS:
            metric_key = kwargs.get('metric_key')
            if not metric_key:
                raise ValueError("metric_key is required for ANALYZER_METRICS visualization")
            result = await self.visualize_analyzer_metrics(
                data.get('results', {}), 
                metric_key, 
                title=title
            )
        elif visualization_type == VisualizationType.DASHBOARD:
            return await self.create_dashboard(
                data, 
                output_path=output_path, 
                title=title, 
                **kwargs
            )
        else:
            raise ValueError(f"Unsupported visualization type: {visualization_type}")
        
        # Save to file if output path is provided
        if output_path and result and 'chart' in result:
            if hasattr(self.visualizer, 'save_chart'):
                await self.visualizer.save_chart(result['chart'], output_path)
                result['output_path'] = output_path
        
        return result
    
    async def create_dashboard(self, data: Dict[str, Any],
                             output_path: Optional[str] = None,
                             title: str = "Analysis Dashboard",
                             include_findings: bool = False,
                             include_recommendations: bool = False,
                             **kwargs) -> Dict[str, Any]:
        """Create a comprehensive dashboard visualization.
        
        Args:
            data: Analysis data to visualize.
            output_path: Optional path to save the dashboard.
            title: Title for the dashboard.
            include_findings: Whether to include detailed findings.
            include_recommendations: Whether to include recommendations.
            **kwargs: Additional keyword arguments.
            
        Returns:
            Dashboard visualization result.
        """
        # Generate the dashboard
        result = await self.generate_analyzer_dashboard(data.get('results', {}))
        
        # Save to file if output path is provided
        if output_path and result and 'dashboard' in result:
            if hasattr(self.visualizer, 'save_chart'):
                await self.visualizer.save_chart(result['dashboard'], output_path)
                result['output_path'] = output_path
        
        return result 