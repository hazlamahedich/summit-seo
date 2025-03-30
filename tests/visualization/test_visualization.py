"""Tests for visualization components."""

import pytest
import asyncio
from pathlib import Path
import sys
import base64
import io

# Add the parent directory to sys.path to import summit_seo package
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from summit_seo.visualization import VisualizationFactory, ChartType
from summit_seo.visualization.base import BaseVisualizer, VisualizationError
from summit_seo.visualization.analyzer_visualization import AnalyzerVisualization

# Sample data for testing
SAMPLE_BAR_DATA = {
    'x': ['A', 'B', 'C', 'D'],
    'y': [10, 20, 15, 25],
    'title': 'Test Bar Chart',
    'x_label': 'Categories',
    'y_label': 'Values'
}

SAMPLE_PIE_DATA = {
    'values': [35, 15, 25, 25],
    'labels': ['A', 'B', 'C', 'D'],
    'title': 'Test Pie Chart'
}

SAMPLE_ANALYSIS_RESULTS = {
    "content_analyzer": {
        "score": 80,
        "issues": ["Issue 1", "Issue 2"],
        "warnings": ["Warning 1"],
        "suggestions": ["Suggestion 1", "Suggestion 2"],
        "enhanced_recommendations": [
            {
                "title": "Recommendation 1",
                "severity": "high",
                "priority": "P1",
                "quick_win": True
            },
            {
                "title": "Recommendation 2",
                "severity": "medium",
                "priority": "P2",
                "quick_win": False
            }
        ]
    },
    "security_analyzer": {
        "score": 60,
        "issues": ["Security Issue 1"],
        "warnings": ["Security Warning 1", "Security Warning 2"],
        "suggestions": ["Security Suggestion 1"],
        "enhanced_recommendations": [
            {
                "title": "Security Recommendation 1",
                "severity": "critical",
                "priority": "P0",
                "quick_win": False
            },
            {
                "title": "Security Recommendation 2",
                "severity": "high",
                "priority": "P1",
                "quick_win": True
            }
        ]
    }
}


@pytest.fixture
def matplotlib_visualizer():
    """Create a matplotlib visualizer for testing."""
    return VisualizationFactory.create('matplotlib', {
        'figure_size': (6, 4),
        'dpi': 72,
        'output_format': 'png'
    })


@pytest.fixture
def analyzer_visualization():
    """Create an analyzer visualization utility for testing."""
    return AnalyzerVisualization()


class TestVisualizationFactory:
    """Tests for VisualizationFactory."""

    def test_register_and_create(self):
        """Test registering and creating visualizers."""
        # Test that matplotlib visualizer is registered
        visualizers = VisualizationFactory.get_registered_visualizers()
        assert 'matplotlib' in visualizers
        
        # Test creating a visualizer
        visualizer = VisualizationFactory.create('matplotlib')
        assert visualizer is not None
        
        # Test creating with config
        config = {'figure_size': (8, 6), 'dpi': 100}
        visualizer = VisualizationFactory.create('matplotlib', config)
        assert visualizer.figure_size == (8, 6)
        assert visualizer.dpi == 100
        
        # Test error on invalid name
        with pytest.raises(ValueError):
            VisualizationFactory.create('invalid_visualizer')


class TestMatplotlibVisualizer:
    """Tests for MatplotlibVisualizer."""

    @pytest.mark.asyncio
    async def test_generate_bar_chart(self, matplotlib_visualizer):
        """Test generating a bar chart."""
        result = await matplotlib_visualizer.generate_chart(SAMPLE_BAR_DATA, ChartType.BAR)
        
        assert result is not None
        assert 'chart_type' in result
        assert result['chart_type'] == 'bar'
        assert 'format' in result
        assert result['format'] == 'png'
        
        # Check if base64 image was generated
        assert 'image_base64' in result
        assert len(result['image_base64']) > 0
        
        # Try to decode base64 to ensure it's valid
        image_data = base64.b64decode(result['image_base64'])
        assert len(image_data) > 0
        
        # Check if data URI is present
        assert 'data_uri' in result
        assert result['data_uri'].startswith('data:image/png;base64,')

    @pytest.mark.asyncio
    async def test_generate_pie_chart(self, matplotlib_visualizer):
        """Test generating a pie chart."""
        result = await matplotlib_visualizer.generate_chart(SAMPLE_PIE_DATA, ChartType.PIE)
        
        assert result is not None
        assert 'chart_type' in result
        assert result['chart_type'] == 'pie'
        assert 'format' in result
        assert result['format'] == 'png'
        
        # Check if base64 image was generated
        assert 'image_base64' in result
        assert len(result['image_base64']) > 0

    @pytest.mark.asyncio
    async def test_generate_multiple_charts(self, matplotlib_visualizer):
        """Test generating multiple charts."""
        chart_configs = [
            {'type': 'bar', 'data': SAMPLE_BAR_DATA},
            {'type': 'pie', 'data': SAMPLE_PIE_DATA}
        ]
        
        result = await matplotlib_visualizer.generate_multiple_charts({}, chart_configs)
        
        assert result is not None
        assert 'charts' in result
        assert len(result['charts']) == 2
        assert result['count'] == 2
        
        # Check first chart
        assert result['charts'][0]['chart_type'] == 'bar'
        
        # Check second chart
        assert result['charts'][1]['chart_type'] == 'pie'

    @pytest.mark.asyncio
    async def test_generate_dashboard(self, matplotlib_visualizer):
        """Test generating a dashboard."""
        layout = {
            'rows': 1,
            'cols': 2,
            'charts': [
                {'type': 'bar', 'data': SAMPLE_BAR_DATA, 'title': 'Bar Chart'},
                {'type': 'pie', 'data': SAMPLE_PIE_DATA, 'title': 'Pie Chart'}
            ]
        }
        
        result = await matplotlib_visualizer.generate_dashboard({}, layout)
        
        assert result is not None
        assert 'type' in result
        assert result['type'] == 'dashboard'
        assert 'layout' in result
        assert result['layout']['rows'] == 1
        assert result['layout']['cols'] == 2
        assert result['layout']['chart_count'] == 2
        
        # Check if base64 image was generated
        assert 'image_base64' in result
        assert len(result['image_base64']) > 0

    def test_invalid_configuration(self):
        """Test invalid configuration handling."""
        # Test invalid figure_size
        with pytest.raises(ValueError):
            VisualizationFactory.create('matplotlib', {'figure_size': 'invalid'})
        
        # Test invalid dpi
        with pytest.raises(ValueError):
            VisualizationFactory.create('matplotlib', {'dpi': 'invalid'})
        
        # Test invalid output_format
        with pytest.raises(ValueError):
            VisualizationFactory.create('matplotlib', {'output_format': 'invalid'})
        
        # Test invalid font_size
        with pytest.raises(ValueError):
            VisualizationFactory.create('matplotlib', {'font_size': 'invalid'})


class TestAnalyzerVisualization:
    """Tests for AnalyzerVisualization."""

    @pytest.mark.asyncio
    async def test_visualize_score_distribution(self, analyzer_visualization):
        """Test visualizing score distribution."""
        result = await analyzer_visualization.visualize_score_distribution(SAMPLE_ANALYSIS_RESULTS)
        
        assert result is not None
        assert 'chart_type' in result
        assert result['chart_type'] == 'bar'
        assert 'image_base64' in result
        assert len(result['image_base64']) > 0

    @pytest.mark.asyncio
    async def test_visualize_issue_severity(self, analyzer_visualization):
        """Test visualizing issue severity."""
        result = await analyzer_visualization.visualize_issue_severity(SAMPLE_ANALYSIS_RESULTS)
        
        assert result is not None
        assert 'chart_type' in result
        assert result['chart_type'] == 'pie'
        assert 'image_base64' in result
        assert len(result['image_base64']) > 0

    @pytest.mark.asyncio
    async def test_visualize_recommendation_priority(self, analyzer_visualization):
        """Test visualizing recommendation priority."""
        result = await analyzer_visualization.visualize_recommendation_priority(SAMPLE_ANALYSIS_RESULTS)
        
        assert result is not None
        assert 'chart_type' in result
        assert result['chart_type'] == 'bar'
        assert 'image_base64' in result
        assert len(result['image_base64']) > 0

    @pytest.mark.asyncio
    async def test_visualize_quick_wins(self, analyzer_visualization):
        """Test visualizing quick wins."""
        result = await analyzer_visualization.visualize_quick_wins(SAMPLE_ANALYSIS_RESULTS)
        
        assert result is not None
        assert 'chart_type' in result
        assert result['chart_type'] == 'bar'
        assert 'image_base64' in result
        assert len(result['image_base64']) > 0

    @pytest.mark.asyncio
    async def test_generate_analyzer_dashboard(self, analyzer_visualization):
        """Test generating analyzer dashboard."""
        result = await analyzer_visualization.generate_analyzer_dashboard(SAMPLE_ANALYSIS_RESULTS)
        
        assert result is not None
        assert 'type' in result
        assert result['type'] == 'dashboard'
        assert 'layout' in result
        assert result['layout']['rows'] == 2
        assert result['layout']['cols'] == 2
        assert result['layout']['chart_count'] == 4
        assert 'image_base64' in result
        assert len(result['image_base64']) > 0 