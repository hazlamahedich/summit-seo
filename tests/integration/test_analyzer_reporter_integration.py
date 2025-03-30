"""Integration tests for analyzer to reporter workflow."""

import os
import pytest
import tempfile
import aiofiles
from pathlib import Path
from importlib import import_module

from summit_seo.analyzer import AnalyzerFactory
from summit_seo.reporter import ReporterFactory, ReportGenerationError

# Get the path to the resources directory
RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')

class TestAnalyzerReporterIntegration:
    """Tests for the integration between analyzers and reporters."""
    
    async def load_test_html(self):
        """Load test HTML file content."""
        html_path = os.path.join(RESOURCES_DIR, 'sample.html')
        async with aiofiles.open(html_path, 'r') as f:
            return await f.read()
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_content_analyzer_to_json_reporter(self):
        """Test end-to-end workflow from content analyzer to JSON reporter."""
        # Arrange
        html_content = await self.load_test_html()
        analyzer = AnalyzerFactory.create('content')
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            output_path = tmp.name
        
        reporter_config = {
            'output_path': output_path,
            'pretty_print': True
        }
        reporter = ReporterFactory.create('json', config=reporter_config)
        
        try:
            # Act
            # 1. Run the analyzer
            analysis_results = await analyzer.analyze(
                html_content, 
                url='https://example.com/sample',
                keywords=['content analyzer', 'SEO testing', 'Summit SEO']
            )
            
            # 2. Generate the report
            report_result = await reporter.generate_report(analysis_results)
            
            # Assert
            # 1. Check that the file was created
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
            
            # 2. Check that the report result has expected metadata
            assert report_result['format'] == 'json'
            assert report_result['file_path'] == output_path
            
            # 3. Verify file content
            async with aiofiles.open(output_path, 'r') as f:
                json_content = await f.read()
            
            assert 'content_analyzer' in json_content
            assert 'keyword_analysis' in json_content
            assert 'heading_structure' in json_content
            assert 'Summit SEO Test Page' in json_content
            
        finally:
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_content_analyzer_to_html_reporter(self):
        """Test end-to-end workflow from content analyzer to HTML reporter."""
        # Arrange
        html_content = await self.load_test_html()
        analyzer = AnalyzerFactory.create('content')
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            output_path = tmp.name
        
        reporter_config = {
            'output_path': output_path,
            'title': 'SEO Analysis Report',
            'include_css': True
        }
        reporter = ReporterFactory.create('html', config=reporter_config)
        
        try:
            # Act
            # 1. Run the analyzer
            analysis_results = await analyzer.analyze(
                html_content, 
                url='https://example.com/sample'
            )
            
            # 2. Generate the report
            report_result = await reporter.generate_report(analysis_results)
            
            # Assert
            # 1. Check that the file was created
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
            
            # 2. Check that the report result has expected metadata
            assert report_result['format'] == 'html'
            assert report_result['file_path'] == output_path
            
            # 3. Verify file content
            async with aiofiles.open(output_path, 'r') as f:
                report_content = await f.read()
            
            assert '<html' in report_content
            assert '<title>SEO Analysis Report</title>' in report_content
            assert 'Example Website' in report_content
            
        finally:
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_pdf_reporter_with_logo(self):
        """Test PDF reporter with logo integration."""
        # Check if ReportLab is installed
        try:
            import_module('reportlab')
        except ImportError:
            pytest.skip("ReportLab not installed, skipping test")
            
        # Generate a sample logo for testing
        try:
            from tests.resources.reporter.sample_logo import generate_sample_logo
            logo_path = generate_sample_logo()
        except ImportError:
            # Create a basic image file as fallback
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp.write(b'PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7o\xa8d\x00\x00\x00\x16IDAT8Oc\xf8\x0f\x04\x0c\xa3`\x14\x8c\x82Q0\n\x86\x15\x00\x00\x9a+\x01\x90\xf3\xc6O\xc4\x00\x00\x00\x00IEND\xaeB`\x82')
            logo_path = tmp.name
        
        # Arrange
        html_content = await self.load_test_html()
        analyzer = AnalyzerFactory.create('content')
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = tmp.name
        
        reporter_config = {
            'output_path': output_path,
            'title': 'SEO Analysis with Logo',
            'logo_path': logo_path
        }
        reporter = ReporterFactory.create('pdf', config=reporter_config)
        
        try:
            # Act
            # 1. Run the analyzer
            analysis_results = await analyzer.analyze(
                html_content, 
                url='https://example.com/sample'
            )
            
            # 2. Generate the report
            report_result = await reporter.generate_report(analysis_results)
            
            # Assert
            # 1. Check that the file was created
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
            
            # 2. Check that the report result has expected metadata
            assert report_result['format'] == 'pdf'
            assert report_result['file_path'] == output_path
            assert report_result['title'] == 'SEO Analysis with Logo'
            assert 'generated_at' in report_result
            
        finally:
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path)
            if os.path.exists(logo_path) and 'sample_logo.py' not in logo_path:
                os.unlink(logo_path)
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_multiple_analyzers_to_single_report(self):
        """Test collecting data from multiple analyzers into a single report."""
        # Arrange
        html_content = await self.load_test_html()
        content_analyzer = AnalyzerFactory.create('content')
        
        # Create additional analyzer if available
        try:
            meta_analyzer = AnalyzerFactory.create('meta')
        except:
            meta_analyzer = None
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            output_path = tmp.name
        
        reporter = ReporterFactory.create('json', config={'output_path': output_path})
        
        try:
            # Act
            # 1. Run the analyzers
            content_results = await content_analyzer.analyze(html_content, url='https://example.com/sample')
            
            # Prepare combined results
            combined_results = {
                'url': 'https://example.com/sample',
                'content_analysis': content_results
            }
            
            # Add meta analysis if available
            if meta_analyzer:
                meta_results = await meta_analyzer.analyze(html_content, url='https://example.com/sample')
                combined_results['meta_analysis'] = meta_results
            
            # 2. Generate the report
            report_result = await reporter.generate_report(combined_results)
            
            # Assert
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
            
            # Verify the combined report
            async with aiofiles.open(output_path, 'r') as f:
                report_content = await f.read()
            
            assert 'content_analysis' in report_content
            if meta_analyzer:
                assert 'meta_analysis' in report_content
            
        finally:
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path) 