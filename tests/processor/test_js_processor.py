"""Tests for the JavaScriptProcessor class."""

import os
import pytest
import aiofiles
from summit_seo.processor.js_processor import JavaScriptProcessor

# Get the path to the resources directory
RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')

class TestJavaScriptProcessor:
    """Test cases for the JavaScriptProcessor."""

    async def load_test_js(self):
        """Load test JavaScript file content."""
        js_path = os.path.join(RESOURCES_DIR, 'sample.js')
        async with aiofiles.open(js_path, 'r') as f:
            return await f.read()

    @pytest.mark.asyncio
    async def test_processor_initialization(self):
        """Test that the processor initializes correctly."""
        processor = JavaScriptProcessor()
        assert processor is not None
        assert processor.processor_type == 'javascript'

    @pytest.mark.asyncio
    async def test_processor_with_default_config(self):
        """Test processing with default configuration."""
        # Arrange
        processor = JavaScriptProcessor()
        js_content = await self.load_test_js()
        
        # Act
        result = await processor.process({
            'js_content': js_content
        })
        
        # Assert
        assert result is not None
        assert 'original_size' in result
        assert 'line_count' in result
        assert 'syntax_valid' in result
        assert result['syntax_valid'] is True
        
    @pytest.mark.asyncio
    async def test_processor_with_custom_config(self):
        """Test processing with custom configuration."""
        # Arrange
        custom_config = {
            'minify': True,
            'count_functions': True,
            'detect_libraries': True,
            'analyze_complexity': True,
            'find_unused_code': True,
            'extract_comments': True,
            'check_best_practices': True
        }
        processor = JavaScriptProcessor(config=custom_config)
        js_content = await self.load_test_js()
        
        # Act
        result = await processor.process({
            'js_content': js_content
        })
        
        # Assert
        assert 'minified_content' in result
        assert 'function_count' in result
        assert 'detected_libraries' in result
        assert 'complexity_analysis' in result
        assert 'unused_code' in result
        assert 'comments' in result
        assert 'best_practices' in result

    @pytest.mark.asyncio
    async def test_function_counting(self):
        """Test that functions are correctly counted."""
        # Arrange
        processor = JavaScriptProcessor(config={'count_functions': True})
        js_content = await self.load_test_js()
        
        # Act
        result = await processor.process({
            'js_content': js_content
        })
        
        # Assert
        assert 'function_count' in result
        function_count = result['function_count']
        
        # Check function types
        assert function_count['named_functions'] >= 2  # fetchData, showError
        assert function_count['anonymous_functions'] >= 1  # IIFE
        assert function_count['arrow_functions'] >= 1  # displayResults
        assert function_count['total'] >= 4

    @pytest.mark.asyncio
    async def test_comment_extraction(self):
        """Test that comments are correctly extracted."""
        # Arrange
        processor = JavaScriptProcessor(config={'extract_comments': True})
        js_content = await self.load_test_js()
        
        # Act
        result = await processor.process({
            'js_content': js_content
        })
        
        # Assert
        assert 'comments' in result
        comments = result['comments']
        
        # Check comment count
        assert comments['count'] > 0
        
        # Check comment types
        assert comments['single_line_count'] > 0
        assert comments['multi_line_count'] > 0
        
        # Check specific comments
        assert any('Sample JavaScript' in comment for comment in comments['comment_list'])
        assert any('Global variables' in comment for comment in comments['comment_list'])
        assert any('Multi-line comment' in comment for comment in comments['comment_list'])

    @pytest.mark.asyncio
    async def test_js_minification(self):
        """Test that JavaScript is correctly minified."""
        # Arrange
        processor = JavaScriptProcessor(config={'minify': True})
        js_content = await self.load_test_js()
        
        # Act
        result = await processor.process({
            'js_content': js_content
        })
        
        # Assert
        assert 'minified_content' in result
        assert 'minified_size' in result
        assert 'size_reduction' in result
        
        # Minified content should be smaller than original
        assert result['minified_size'] < result['original_size']
        assert result['size_reduction'] > 0
        
        # Minified content should not contain unnecessary whitespace
        assert '\n\n' not in result['minified_content']
        assert '  ' not in result['minified_content']

    @pytest.mark.asyncio
    async def test_complexity_analysis(self):
        """Test that complexity analysis is correctly performed."""
        # Arrange
        processor = JavaScriptProcessor(config={'analyze_complexity': True})
        js_content = await self.load_test_js()
        
        # Act
        result = await processor.process({
            'js_content': js_content
        })
        
        # Assert
        assert 'complexity_analysis' in result
        complexity = result['complexity_analysis']
        
        # Check complexity metrics
        assert 'average_cyclomatic_complexity' in complexity
        assert 'max_cyclomatic_complexity' in complexity
        assert 'complex_functions' in complexity
        
        # Check nesting levels
        assert 'max_nesting_level' in complexity
        assert complexity['max_nesting_level'] > 0

    @pytest.mark.asyncio
    async def test_best_practice_checking(self):
        """Test that best practice checking is correctly performed."""
        # Arrange
        processor = JavaScriptProcessor(config={'check_best_practices': True})
        js_content = await self.load_test_js()
        
        # Act
        result = await processor.process({
            'js_content': js_content
        })
        
        # Assert
        assert 'best_practices' in result
        best_practices = result['best_practices']
        
        # Check best practice categories
        assert 'console_usage' in best_practices
        assert 'error_handling' in best_practices
        
        # Our sample has console.log usage
        assert best_practices['console_usage']['count'] > 0
        
        # Our sample has try-catch blocks
        assert best_practices['error_handling']['try_catch_count'] > 0

    @pytest.mark.asyncio
    async def test_missing_required_field(self):
        """Test behavior when required field is missing."""
        # Arrange
        processor = JavaScriptProcessor()
        
        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            await processor.process({})
        
        assert "Missing required field: js_content" in str(excinfo.value) 