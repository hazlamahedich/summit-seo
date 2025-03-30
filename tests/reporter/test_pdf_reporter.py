"""Test cases for PDF reporter functionality."""

import pytest
import os
import tempfile
from datetime import datetime
from summit_seo.reporter.pdf_reporter import PDFReporter
from summit_seo.reporter.base import ReportGenerationError

@pytest.fixture
def sample_report_data() -> dict:
    """Sample SEO analysis data for testing report generation."""
    return {
        'url': 'https://example.com',
        'summary': {
            'score': 85,
            'performance': 90,
            'accessibility': 75,
            'best_practices': 88,
            'seo': 92,
            'overview': 'Overall, the website performs well but has some accessibility issues to address.'
        },
        'warnings': [
            'Missing alt text on 3 images',
            'Contrast ratio too low in navigation links',
            {'type': 'critical', 'message': 'Blocking JavaScript detected in header'}
        ],
        'suggestions': [
            'Add meta description to improve SEO',
            'Consider using WebP image format for better performance',
            {'type': 'medium', 'message': 'Implement lazy loading for below-fold images'}
        ],
        'recommendations': [
            'Implement responsive images using srcset',
            'Add structured data for better rich snippet chances',
            {'type': 'info', 'message': 'Consider implementing a service worker for offline support'}
        ],
        'content_analyzer': {
            'word_count': 1250,
            'reading_time': '5 minutes',
            'heading_structure': {
                'h1_count': 1,
                'h2_count': 5,
                'h3_count': 10,
                'structure_issues': []
            },
            'keyword_density': {
                'primary_keyword': 'example',
                'primary_density': 2.1,
                'secondary_keywords': {
                    'test': 1.5,
                    'sample': 1.2
                }
            },
            'readability': {
                'flesch_kincaid': 65.2,
                'reading_level': 'Standard',
                'sentence_count': 78,
                'avg_sentence_length': 16
            }
        },
        'meta_analyzer': {
            'title': {
                'found': True,
                'content': 'Example Website - Testing',
                'length': 24,
                'issues': []
            },
            'meta_description': {
                'found': False,
                'content': '',
                'issues': ['Missing meta description']
            },
            'canonical': {
                'found': True,
                'url': 'https://example.com'
            }
        }
    }

@pytest.fixture
def temp_output_file():
    """Create a temporary file for PDF output."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        file_path = tmp.name
    
    # Yield the file path
    yield file_path
    
    # Clean up after the test
    if os.path.exists(file_path):
        os.unlink(file_path)

async def test_pdf_reporter_initialization():
    """Test PDF reporter initialization with various configurations."""
    # Default configuration
    reporter = PDFReporter()
    assert reporter.output_path == 'seo_report.pdf'
    assert reporter.title == 'SEO Analysis Report'
    assert reporter.include_charts is True
    assert reporter.include_recommendations is True
    assert reporter.include_details is True
    assert reporter.include_summary is True
    assert reporter.theme == 'default'
    assert reporter.page_size == 'A4'
    assert reporter.logo_path is None
    
    # Custom configuration
    custom_config = {
        'output_path': 'custom_report.pdf',
        'title': 'Custom SEO Report',
        'include_charts': False,
        'include_recommendations': True,
        'include_details': False,
        'include_summary': True,
        'theme': 'dark',
        'page_size': 'Letter'
    }
    
    reporter = PDFReporter(custom_config)
    assert reporter.output_path == custom_config['output_path']
    assert reporter.title == custom_config['title']
    assert reporter.include_charts is custom_config['include_charts']
    assert reporter.include_recommendations is custom_config['include_recommendations']
    assert reporter.include_details is custom_config['include_details']
    assert reporter.include_summary is custom_config['include_summary']
    assert reporter.theme == custom_config['theme']
    assert reporter.page_size == custom_config['page_size']

async def test_validate_config():
    """Test configuration validation."""
    # Valid configurations
    valid_configs = [
        {'include_charts': True},
        {'include_recommendations': False},
        {'include_details': True},
        {'include_summary': False},
        {'theme': 'light'},
        {'page_size': 'Legal'}
    ]
    
    for config in valid_configs:
        reporter = PDFReporter(config)
        for key, value in config.items():
            assert getattr(reporter, key) == value
    
    # Invalid boolean parameters
    invalid_bool_configs = [
        {'include_charts': 'yes'},
        {'include_recommendations': 1},
        {'include_details': 'True'},
        {'include_summary': 0}
    ]
    
    for config in invalid_bool_configs:
        with pytest.raises(ValueError):
            PDFReporter(config)
    
    # Invalid theme
    with pytest.raises(ValueError):
        PDFReporter({'theme': 'invalid-theme'})
    
    # Invalid page size
    with pytest.raises(ValueError):
        PDFReporter({'page_size': 'invalid-size'})

async def test_generate_report_basic(sample_report_data, temp_output_file):
    """Test basic PDF report generation."""
    try:
        from reportlab.lib.pagesizes import A4
    except ImportError:
        pytest.skip("ReportLab library not installed, skipping PDF tests")
    
    config = {
        'output_path': temp_output_file,
        'title': 'Test SEO Report'
    }
    
    reporter = PDFReporter(config)
    result = await reporter.generate_report(sample_report_data)
    
    # Verify the file was created
    assert os.path.exists(temp_output_file)
    assert os.path.getsize(temp_output_file) > 0
    
    # Verify the result contains expected information
    assert result['format'] == 'pdf'
    assert result['file_path'] == temp_output_file
    assert result['file_size'] > 0
    assert result['title'] == 'Test SEO Report'
    assert 'generated_at' in result

async def test_generate_report_with_themes(sample_report_data, temp_output_file):
    """Test PDF report generation with different themes."""
    try:
        from reportlab.lib.pagesizes import A4
    except ImportError:
        pytest.skip("ReportLab library not installed, skipping PDF tests")
    
    # Test all available themes
    themes = ['default', 'dark', 'light']
    
    for theme in themes:
        config = {
            'output_path': temp_output_file,
            'theme': theme
        }
        
        reporter = PDFReporter(config)
        result = await reporter.generate_report(sample_report_data)
        
        # Verify the file was created
        assert os.path.exists(temp_output_file)
        assert os.path.getsize(temp_output_file) > 0

async def test_generate_report_with_different_page_sizes(sample_report_data, temp_output_file):
    """Test PDF report generation with different page sizes."""
    try:
        from reportlab.lib.pagesizes import A4, LETTER, LEGAL
    except ImportError:
        pytest.skip("ReportLab library not installed, skipping PDF tests")
    
    # Test all available page sizes
    page_sizes = ['A4', 'Letter', 'Legal']
    
    for page_size in page_sizes:
        config = {
            'output_path': temp_output_file,
            'page_size': page_size
        }
        
        reporter = PDFReporter(config)
        result = await reporter.generate_report(sample_report_data)
        
        # Verify the file was created
        assert os.path.exists(temp_output_file)
        assert os.path.getsize(temp_output_file) > 0

async def test_generate_report_content_sections(sample_report_data, temp_output_file):
    """Test PDF report generation with different content section configurations."""
    try:
        from reportlab.lib.pagesizes import A4
    except ImportError:
        pytest.skip("ReportLab library not installed, skipping PDF tests")
    
    # Test with all sections enabled
    config_all = {
        'output_path': temp_output_file,
        'include_summary': True,
        'include_recommendations': True,
        'include_details': True,
        'include_charts': True
    }
    
    reporter = PDFReporter(config_all)
    result = await reporter.generate_report(sample_report_data)
    
    assert os.path.exists(temp_output_file)
    size_with_all = os.path.getsize(temp_output_file)
    
    # Test with some sections disabled
    config_minimal = {
        'output_path': temp_output_file,
        'include_summary': True,
        'include_recommendations': False,
        'include_details': False,
        'include_charts': False
    }
    
    reporter = PDFReporter(config_minimal)
    result = await reporter.generate_report(sample_report_data)
    
    assert os.path.exists(temp_output_file)
    size_minimal = os.path.getsize(temp_output_file)
    
    # The file with all sections should be larger than the minimal one
    assert size_with_all > size_minimal

async def test_generate_report_with_missing_data(temp_output_file):
    """Test PDF report generation with missing or incorrect data."""
    try:
        from reportlab.lib.pagesizes import A4
    except ImportError:
        pytest.skip("ReportLab library not installed, skipping PDF tests")
    
    config = {
        'output_path': temp_output_file
    }
    
    reporter = PDFReporter(config)
    
    # Empty data should still generate a report
    empty_data = {}
    result = await reporter.generate_report(empty_data)
    
    assert os.path.exists(temp_output_file)
    assert os.path.getsize(temp_output_file) > 0
    
    # Minimal data should generate a report
    minimal_data = {
        'url': 'https://example.com'
    }
    result = await reporter.generate_report(minimal_data)
    
    assert os.path.exists(temp_output_file)
    assert os.path.getsize(temp_output_file) > 0
    
    # Malformed data should not cause errors
    malformed_data = {
        'summary': 'Not a dictionary',
        'warnings': 'Not a list',
        'random_field': lambda x: x  # Not serializable
    }
    
    result = await reporter.generate_report(malformed_data)
    assert os.path.exists(temp_output_file)
    assert os.path.getsize(temp_output_file) > 0

async def test_error_handling():
    """Test error handling during PDF generation."""
    try:
        from reportlab.lib.pagesizes import A4
    except ImportError:
        pytest.skip("ReportLab library not installed, skipping PDF tests")
    
    # Invalid output path should cause an error
    config = {
        'output_path': '/nonexistent/directory/report.pdf'
    }
    
    reporter = PDFReporter(config)
    
    with pytest.raises(ReportGenerationError):
        await reporter.generate_report({})
    
    # Create a faulty reporter to test error handling
    class FaultyPDFReporter(PDFReporter):
        async def generate_report(self, data):
            raise Exception("Test error")
    
    reporter = FaultyPDFReporter()
    
    with pytest.raises(ReportGenerationError):
        await reporter.generate_report({})

async def test_generate_report_with_logo(sample_report_data, temp_output_file):
    """Test PDF report generation with a logo (if available)."""
    try:
        from reportlab.lib.pagesizes import A4
    except ImportError:
        pytest.skip("ReportLab library not installed, skipping PDF tests")
    
    # Try to find a logo file for testing (create one if needed)
    logo_path = None
    
    # First, check if there's a logo in the tests directory
    possible_logo_paths = [
        os.path.join('tests', 'resources', 'logo.png'),
        os.path.join('tests', 'resources', 'logo.jpg'),
        os.path.join('resources', 'logo.png'),
        os.path.join('resources', 'logo.jpg')
    ]
    
    for path in possible_logo_paths:
        if os.path.exists(path):
            logo_path = path
            break
    
    # If no logo file exists, create a temporary one
    if not logo_path:
        try:
            # Try to create a simple image using PIL if available
            from PIL import Image
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                logo_path = tmp.name
                img = Image.new('RGB', (100, 40), color=(73, 109, 137))
                img.save(logo_path)
        except ImportError:
            pytest.skip("PIL not installed, skipping logo test")
    
    # Now generate a report with the logo
    if logo_path:
        config = {
            'output_path': temp_output_file,
            'logo_path': logo_path
        }
        
        reporter = PDFReporter(config)
        result = await reporter.generate_report(sample_report_data)
        
        # Verify the file was created
        assert os.path.exists(temp_output_file)
        assert os.path.getsize(temp_output_file) > 0
        
        # Clean up temporary logo if we created one
        if logo_path.startswith(tempfile.gettempdir()):
            os.unlink(logo_path)

async def test_comprehensive_report(sample_report_data, temp_output_file):
    """Test a comprehensive report with all features enabled."""
    try:
        from reportlab.lib.pagesizes import A4
    except ImportError:
        pytest.skip("ReportLab library not installed, skipping PDF tests")
    
    # Create a comprehensive configuration
    config = {
        'output_path': temp_output_file,
        'title': 'Comprehensive SEO Analysis',
        'include_charts': True,
        'include_recommendations': True,
        'include_details': True,
        'include_summary': True,
        'theme': 'default',
        'page_size': 'A4'
    }
    
    # Add some extra analyzers to the sample data
    extended_data = sample_report_data.copy()
    extended_data.update({
        'performance_analyzer': {
            'scores': {
                'first_contentful_paint': 1.2,
                'speed_index': 2.1,
                'largest_contentful_paint': 2.5,
                'time_to_interactive': 3.2,
                'total_blocking_time': 0.15,
                'cumulative_layout_shift': 0.1
            },
            'metrics': {
                'total_size': '1.2MB',
                'html_size': '25KB',
                'css_size': '150KB',
                'js_size': '850KB',
                'image_size': '200KB',
                'request_count': 45
            }
        },
        'security_analyzer': {
            'headers': {
                'content_security_policy': 'missing',
                'x_content_type_options': 'present',
                'x_frame_options': 'present',
                'x_xss_protection': 'present',
                'strict_transport_security': 'missing'
            },
            'https': {
                'enabled': True,
                'certificate_valid': True,
                'certificate_expiry': '2024-05-15'
            },
            'vulnerabilities': [
                {'type': 'medium', 'message': 'jQuery version 1.8.3 is outdated and has known vulnerabilities'},
                {'type': 'low', 'message': 'Missing Content-Security-Policy header'}
            ]
        }
    })
    
    reporter = PDFReporter(config)
    result = await reporter.generate_report(extended_data)
    
    # Verify the file was created and has substantial content
    assert os.path.exists(temp_output_file)
    assert os.path.getsize(temp_output_file) > 10000  # Should be at least 10KB with all this data 