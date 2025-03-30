"""Integration tests for processor to analyzer workflow."""

import os
import pytest
import tempfile
import aiofiles
from pathlib import Path

from summit_seo.processor import ProcessorFactory
from summit_seo.analyzer import AnalyzerFactory

# Get the path to the resources directory
RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')

class TestProcessorAnalyzerIntegration:
    """Tests for the integration between processors and analyzers."""
    
    async def load_test_html(self):
        """Load test HTML file content."""
        html_path = os.path.join(RESOURCES_DIR, 'sample.html')
        async with aiofiles.open(html_path, 'r') as f:
            return await f.read()
    
    async def load_test_css(self):
        """Create test CSS content if it doesn't exist."""
        css_path = os.path.join(RESOURCES_DIR, 'processor', 'sample.css')
        
        if not os.path.exists(css_path):
            os.makedirs(os.path.dirname(css_path), exist_ok=True)
            css_content = """
            body {
                font-family: Arial, sans-serif;
                color: #333333;
                line-height: 1.6;
                margin: 0;
                padding: 0;
            }
            
            header {
                background-color: #f5f5f5;
                padding: 20px;
                border-bottom: 1px solid #ddd;
            }
            
            header h1 {
                color: #333333;
                margin: 0;
                font-size: 24px;
            }
            
            /* Duplicate rule for header h1 to test duplicate detection */
            header h1 {
                font-weight: bold;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            /* Using browser hack for IE */
            .ie-fix {
                *zoom: 1;
            }
            
            /* Media query for responsive design */
            @media (max-width: 768px) {
                .container {
                    padding: 10px;
                }
            }
            
            /* Various color formats for testing */
            .color-hex {
                color: #ff0000;
            }
            
            .color-rgb {
                color: rgb(0, 255, 0);
            }
            
            .color-rgba {
                color: rgba(0, 0, 255, 0.5);
            }
            """
            async with aiofiles.open(css_path, 'w') as f:
                await f.write(css_content)
        
        async with aiofiles.open(css_path, 'r') as f:
            return await f.read()
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_html_processor_to_content_analyzer(self):
        """Test workflow from HTML processor to content analyzer."""
        # Arrange
        html_content = await self.load_test_html()
        
        # Create an HTML processor
        html_processor = ProcessorFactory.create('html')
        
        # Create a content analyzer
        content_analyzer = AnalyzerFactory.create('content')
        
        # Act
        # 1. Process the HTML
        processor_result = await html_processor.process({
            'html_content': html_content,
            'url': 'https://example.com/sample'
        })
        
        # 2. Use processor output as input to analyzer
        analyzer_result = await content_analyzer.analyze(
            processor_result['processed_content'],
            url='https://example.com/sample'
        )
        
        # Assert
        assert processor_result['original_size'] > 0
        assert 'headings' in processor_result
        assert 'images' in processor_result
        
        # Verify analyzer received proper content
        assert 'title' in analyzer_result
        assert analyzer_result['title'] == 'Sample Page for Summit SEO Testing'
        assert 'headings' in analyzer_result
        assert 'h1_count' in analyzer_result['headings']
        assert analyzer_result['headings']['h1_count'] == 1
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_css_processor_to_content_analyzer(self):
        """Test workflow from CSS processor to content analysis."""
        # Arrange
        css_content = await self.load_test_css()
        html_content = await self.load_test_html()
        
        # Create processors
        css_processor = ProcessorFactory.create('css')
        html_processor = ProcessorFactory.create('html')
        
        # Create content analyzer
        content_analyzer = AnalyzerFactory.create('content')
        
        # Act
        # 1. Process the CSS
        css_result = await css_processor.process({
            'css_content': css_content
        })
        
        # 2. Process the HTML
        html_result = await html_processor.process({
            'html_content': html_content,
            'url': 'https://example.com/sample'
        })
        
        # 3. Combine CSS analysis with HTML for a comprehensive content analysis
        html_result['css_analysis'] = css_result
        
        # 4. Run analyzer with enhanced data
        analyzer_result = await content_analyzer.analyze(
            html_result['processed_content'],
            url='https://example.com/sample',
            additional_data={'css_analysis': css_result}
        )
        
        # Assert
        # Verify CSS processor output
        assert 'selector_analysis' in css_result
        assert 'original_size' in css_result
        
        # Verify analyzer results
        assert 'title' in analyzer_result
        
        # NOTE: We're testing the flow here - the actual Content Analyzer might not
        # use the CSS analysis yet, but the integration pattern is established
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_multiple_processors_to_analyzer(self):
        """Test using multiple processors with an analyzer."""
        # Arrange
        html_content = await self.load_test_html()
        
        # Create processors
        html_processor = ProcessorFactory.create('html')
        
        # Check if JS processor is available
        try:
            js_processor = ProcessorFactory.create('javascript')
            has_js_processor = True
        except:
            js_processor = None
            has_js_processor = False
        
        # Create analyzer
        content_analyzer = AnalyzerFactory.create('content')
        
        # Act
        # 1. Process HTML
        html_result = await html_processor.process({
            'html_content': html_content,
            'url': 'https://example.com/sample'
        })
        
        # 2. Extract JavaScript if available
        if has_js_processor and 'scripts' in html_result:
            scripts = html_result.get('scripts', [])
            if scripts:
                # Take the first script for simplicity
                script_content = scripts[0].get('content', '')
                
                if script_content:
                    js_result = await js_processor.process({
                        'javascript_content': script_content
                    })
                    
                    # Add JavaScript analysis to additional data
                    additional_data = {
                        'javascript_analysis': js_result
                    }
                else:
                    additional_data = {}
            else:
                additional_data = {}
        else:
            additional_data = {}
        
        # 3. Run analyzer with processed content and additional data
        analyzer_result = await content_analyzer.analyze(
            html_result['processed_content'],
            url='https://example.com/sample',
            additional_data=additional_data
        )
        
        # Assert
        assert 'title' in analyzer_result
        assert 'word_count' in analyzer_result
        
        # Verify the JavaScript was processed if available
        if has_js_processor and 'javascript_analysis' in additional_data:
            assert 'original_size' in additional_data['javascript_analysis'] 