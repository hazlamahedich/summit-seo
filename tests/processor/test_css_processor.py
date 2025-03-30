"""Tests for the CSSProcessor class."""

import os
import pytest
import aiofiles
from summit_seo.processor.css_processor import CSSProcessor

# Get the path to the resources directory
RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')

class TestCSSProcessor:
    """Test cases for the CSSProcessor."""

    async def load_test_css(self):
        """Load test CSS file content."""
        css_path = os.path.join(RESOURCES_DIR, 'sample.css')
        async with aiofiles.open(css_path, 'r') as f:
            return await f.read()

    @pytest.mark.asyncio
    async def test_processor_initialization(self):
        """Test that the processor initializes correctly."""
        processor = CSSProcessor()
        assert processor is not None
        assert processor.processor_type == 'css'

    @pytest.mark.asyncio
    async def test_processor_with_default_config(self):
        """Test processing with default configuration."""
        # Arrange
        processor = CSSProcessor()
        css_content = await self.load_test_css()
        
        # Act
        result = await processor.process({
            'css_content': css_content
        })
        
        # Assert
        assert result is not None
        assert 'original_size' in result
        assert 'line_count' in result
        assert 'selector_analysis' in result
        
    @pytest.mark.asyncio
    async def test_processor_with_custom_config(self):
        """Test processing with custom configuration."""
        # Arrange
        custom_config = {
            'minify': True,
            'analyze_selectors': True,
            'count_media_queries': True,
            'detect_browser_hacks': True,
            'find_unused_selectors': True,
            'analyze_colors': True,
            'detect_duplicates': True
        }
        processor = CSSProcessor(config=custom_config)
        css_content = await self.load_test_css()
        
        # Act
        result = await processor.process({
            'css_content': css_content
        })
        
        # Assert
        assert 'minified_content' in result
        assert 'selector_analysis' in result
        assert 'media_queries' in result
        assert 'browser_hacks' in result
        assert 'unused_selectors' in result
        assert 'color_analysis' in result
        assert 'duplicate_rules' in result

    @pytest.mark.asyncio
    async def test_selector_analysis(self):
        """Test that selectors are correctly analyzed."""
        # Arrange
        processor = CSSProcessor(config={'analyze_selectors': True})
        css_content = await self.load_test_css()
        
        # Act
        result = await processor.process({
            'css_content': css_content
        })
        
        # Assert
        assert 'selector_analysis' in result
        analysis = result['selector_analysis']
        
        # Check selector counts
        assert analysis['total_selectors'] > 0
        assert analysis['class_selectors'] > 0
        assert analysis['id_selectors'] == 0  # Our sample doesn't have ID selectors
        assert analysis['element_selectors'] > 0
        
        # Our test file has pseudo selectors
        assert analysis['pseudo_selectors'] > 0
        
        # Check for specific selectors
        assert 'body' in analysis['selector_list']
        assert '.container' in analysis['selector_list']
        assert 'header h1' in analysis['selector_list']

    @pytest.mark.asyncio
    async def test_media_query_detection(self):
        """Test that media queries are correctly detected."""
        # Arrange
        processor = CSSProcessor(config={'count_media_queries': True})
        css_content = await self.load_test_css()
        
        # Act
        result = await processor.process({
            'css_content': css_content
        })
        
        # Assert
        assert 'media_queries' in result
        media_queries = result['media_queries']
        
        # Check media query count
        assert media_queries['count'] == 1
        
        # Check specific media query
        assert any('max-width: 768px' in query for query in media_queries['queries'])

    @pytest.mark.asyncio
    async def test_browser_hack_detection(self):
        """Test that browser hacks are correctly detected."""
        # Arrange
        processor = CSSProcessor(config={'detect_browser_hacks': True})
        css_content = await self.load_test_css()
        
        # Act
        result = await processor.process({
            'css_content': css_content
        })
        
        # Assert
        assert 'browser_hacks' in result
        browser_hacks = result['browser_hacks']
        
        # Our test file has the *zoom hack
        assert browser_hacks['count'] > 0
        assert any('*zoom' in hack for hack in browser_hacks['hacks'])

    @pytest.mark.asyncio
    async def test_color_analysis(self):
        """Test that colors are correctly analyzed."""
        # Arrange
        processor = CSSProcessor(config={'analyze_colors': True})
        css_content = await self.load_test_css()
        
        # Act
        result = await processor.process({
            'css_content': css_content
        })
        
        # Assert
        assert 'color_analysis' in result
        color_analysis = result['color_analysis']
        
        # Check color count
        assert color_analysis['total_colors'] > 0
        
        # Check specific colors from our test file
        color_values = [color['value'] for color in color_analysis['colors']]
        assert '#ff0000' in color_values  # red
        assert '#00ff00' in color_values  # green
        assert any('rgba' in color and '0, 0, 255' in color for color in color_values)  # blue with opacity

    @pytest.mark.asyncio
    async def test_duplicate_rule_detection(self):
        """Test that duplicate rules are correctly detected."""
        # Arrange
        processor = CSSProcessor(config={'detect_duplicates': True})
        css_content = await self.load_test_css()
        
        # Act
        result = await processor.process({
            'css_content': css_content
        })
        
        # Assert
        assert 'duplicate_rules' in result
        duplicate_rules = result['duplicate_rules']
        
        # Our test file has a duplicate header h1 rule
        assert duplicate_rules['count'] > 0
        assert any('header h1' in duplicate['selector'] for duplicate in duplicate_rules['duplicates'])

    @pytest.mark.asyncio
    async def test_css_minification(self):
        """Test that CSS is correctly minified."""
        # Arrange
        processor = CSSProcessor(config={'minify': True})
        css_content = await self.load_test_css()
        
        # Act
        result = await processor.process({
            'css_content': css_content
        })
        
        # Assert
        assert 'minified_content' in result
        assert 'minified_size' in result
        assert 'size_reduction' in result
        
        # Minified content should be smaller than original
        assert result['minified_size'] < result['original_size']
        assert result['size_reduction'] > 0
        
        # Minified content should not contain newlines or unnecessary spaces
        assert '\n' not in result['minified_content']
        assert '  ' not in result['minified_content']

    @pytest.mark.asyncio
    async def test_missing_required_field(self):
        """Test behavior when required field is missing."""
        # Arrange
        processor = CSSProcessor()
        
        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            await processor.process({})
        
        assert "Missing required field: css_content" in str(excinfo.value) 