"""End-to-end tests for the Summit SEO pipeline."""

import os
import pytest
import tempfile
import aiofiles
from pathlib import Path

from summit_seo.processor import ProcessorFactory
from summit_seo.analyzer import AnalyzerFactory
from summit_seo.reporter import ReporterFactory

# Get the path to the resources directory
RESOURCES_DIR = os.path.join(os.path.dirname(__file__), 'resources')

class TestEndToEndPipeline:
    """Tests for the end-to-end SEO analysis pipeline."""
    
    async def load_test_html(self):
        """Load test HTML file content."""
        html_path = os.path.join(RESOURCES_DIR, 'sample.html')
        async with aiofiles.open(html_path, 'r') as f:
            return await f.read()
    
    @pytest.mark.asyncio
    async def test_html_to_pdf_pipeline(self):
        """Test the complete HTML to PDF reporting pipeline."""
        try:
            import reportlab
        except ImportError:
            pytest.skip("ReportLab not installed, skipping PDF test")
        
        # Arrange
        html_content = await self.load_test_html()
        url = 'https://example.com/sample'
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = tmp.name
        
        # Create components
        html_processor = ProcessorFactory.create('html')
        content_analyzer = AnalyzerFactory.create('content')
        pdf_reporter = ReporterFactory.create('pdf', config={
            'output_path': output_path,
            'title': 'End-to-End SEO Analysis'
        })
        
        try:
            # Act
            # Step 1: Process HTML
            processor_result = await html_processor.process(
                data={
                    'html_content': html_content
                }, 
                url=url
            )
            
            # Step 2: Analyze content
            analysis_result = await content_analyzer.analyze(
                processor_result['processed_content'],
                url=url,
                keywords=['SEO testing', 'content analyzer']
            )
            
            # Step 3: Generate report
            report_result = await pdf_reporter.generate_report(analysis_result)
            
            # Assert
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
            assert report_result['format'] == 'pdf'
            assert report_result['file_path'] == output_path
            assert 'generated_at' in report_result
            
        finally:
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    @pytest.mark.asyncio
    async def test_html_to_json_pipeline(self):
        """Test the complete HTML to JSON reporting pipeline."""
        # Arrange
        html_content = await self.load_test_html()
        url = 'https://example.com/sample'
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            output_path = tmp.name
        
        # Create components
        html_processor = ProcessorFactory.create('html')
        content_analyzer = AnalyzerFactory.create('content')
        json_reporter = ReporterFactory.create('json', config={
            'output_path': output_path,
            'pretty_print': True
        })
        
        try:
            # Act
            # Step 1: Process HTML
            processor_result = await html_processor.process(
                data={
                    'html_content': html_content
                },
                url=url
            )
            
            # Step 2: Analyze content
            analysis_result = await content_analyzer.analyze(
                processor_result['processed_content'],
                url=url
            )
            
            # Step 3: Generate report
            report_result = await json_reporter.generate_report(analysis_result)
            
            # Assert
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
            assert report_result['format'] == 'json'
            
            # Verify the content
            async with aiofiles.open(output_path, 'r') as f:
                content = await f.read()
            
            assert 'title' in content
            assert 'meta_description' in content
            assert 'headings' in content
            
        finally:
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    @pytest.mark.asyncio
    async def test_pipeline_with_multiple_processors(self):
        """Test pipeline with multiple processors for a single resource."""
        # Arrange
        html_content = await self.load_test_html()
        url = 'https://example.com/sample'
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            output_path = tmp.name
        
        # Create components
        html_processor = ProcessorFactory.create('html')
        
        # Try to create CSS and JS processors if available
        try:
            css_processor = ProcessorFactory.create('css')
            has_css_processor = True
        except:
            css_processor = None
            has_css_processor = False
        
        try:
            js_processor = ProcessorFactory.create('javascript')
            has_js_processor = True
        except:
            js_processor = None
            has_js_processor = False
        
        content_analyzer = AnalyzerFactory.create('content')
        html_reporter = ReporterFactory.create('html', config={
            'output_path': output_path,
            'title': 'Multi-Processor Analysis'
        })
        
        try:
            # Act
            # Step 1: Process HTML
            html_result = await html_processor.process(
                data={
                    'html_content': html_content
                },
                url=url
            )
            
            additional_data = {}
            
            # Process CSS if available
            if has_css_processor and 'styles' in html_result:
                styles = html_result.get('styles', [])
                if styles:
                    # Take the first stylesheet for simplicity
                    style_content = styles[0].get('content', '')
                    
                    if style_content:
                        css_result = await css_processor.process(
                            data={
                                'css_content': style_content
                            },
                            url=url
                        )
                        additional_data['css_analysis'] = css_result
            
            # Process JavaScript if available
            if has_js_processor and 'scripts' in html_result:
                scripts = html_result.get('scripts', [])
                if scripts:
                    # Take the first script for simplicity
                    script_content = scripts[0].get('content', '')
                    
                    if script_content:
                        js_result = await js_processor.process(
                            data={
                                'javascript_content': script_content
                            },
                            url=url
                        )
                        additional_data['javascript_analysis'] = js_result
            
            # Step 2: Analyze content with additional data
            analysis_result = await content_analyzer.analyze(
                html_result['processed_content'],
                url=url,
                additional_data=additional_data
            )
            
            # Enrich the analysis with processor data for comprehensive reporting
            analysis_result['processor_data'] = {
                'html': html_result
            }
            if has_css_processor and 'css_analysis' in additional_data:
                analysis_result['processor_data']['css'] = additional_data['css_analysis']
            if has_js_processor and 'javascript_analysis' in additional_data:
                analysis_result['processor_data']['javascript'] = additional_data['javascript_analysis']
            
            # Step 3: Generate report
            report_result = await html_reporter.generate_report(analysis_result)
            
            # Assert
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
            assert report_result['format'] == 'html'
            
            # Verify HTML report content
            async with aiofiles.open(output_path, 'r') as f:
                content = await f.read()
            
            assert 'Sample Page for Summit SEO Testing' in content
            
        finally:
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path) 