"""Test cases for HTML processor functionality."""

import pytest
from bs4 import BeautifulSoup
from summit_seo.processor.html_processor import HTMLProcessor
from summit_seo.processor.base import TransformationError, ValidationError

async def test_html_processor_initialization(sample_config):
    """Test HTML processor initialization with configuration."""
    processor = HTMLProcessor(sample_config)
    assert processor.parser == sample_config['parser']
    assert processor.clean_whitespace == sample_config['clean_whitespace']
    assert processor.normalize_urls == sample_config['normalize_urls']
    assert processor.remove_comments == sample_config['remove_comments']
    assert processor.extract_metadata == sample_config['extract_metadata']

async def test_validate_config_parser():
    """Test parser configuration validation."""
    # Valid parsers
    valid_parsers = ['html.parser', 'lxml', 'html5lib']
    for parser in valid_parsers:
        processor = HTMLProcessor({'parser': parser})
        assert processor.parser == parser
    
    # Invalid parser
    with pytest.raises(ValueError):
        HTMLProcessor({'parser': 'invalid_parser'})

async def test_validate_config_boolean_options():
    """Test boolean configuration options validation."""
    bool_options = [
        'clean_whitespace',
        'normalize_urls',
        'remove_comments',
        'extract_metadata'
    ]
    
    for option in bool_options:
        # Valid boolean values
        for value in [True, False]:
            processor = HTMLProcessor({option: value})
            assert getattr(processor, option) == value
        
        # Invalid values
        with pytest.raises(ValueError):
            HTMLProcessor({option: 'not_bool'})

async def test_process_valid_html(sample_html):
    """Test processing valid HTML content."""
    processor = HTMLProcessor()
    result = await processor.process(
        {'html_content': sample_html},
        'https://example.com'
    )
    
    assert not result.errors
    assert 'processed_html' in result.processed_data
    assert 'text_content' in result.processed_data
    
    # Verify processed HTML is valid
    soup = BeautifulSoup(result.processed_data['processed_html'], 'html.parser')
    assert soup.find('title')
    assert soup.find_all('h1')

async def test_process_html_with_issues(sample_html_with_issues):
    """Test processing HTML with formatting issues."""
    processor = HTMLProcessor()
    result = await processor.process(
        {'html_content': sample_html_with_issues},
        'https://example.com'
    )
    
    assert not result.errors
    processed_html = result.processed_data['processed_html']
    
    # Check whitespace cleaning
    assert '  Multiple    Spaces  ' not in processed_html
    assert 'Multiple Spaces' in processed_html
    
    # Check comment removal
    assert '<!-- Comment that should be removed -->' not in processed_html

async def test_process_invalid_html(invalid_html_cases):
    """Test processing invalid HTML content."""
    processor = HTMLProcessor()
    
    for html in invalid_html_cases:
        result = await processor.process(
            {'html_content': html},
            'https://example.com'
        )
        
        if html is None:
            assert result.errors
        else:
            assert 'processed_html' in result.processed_data
            assert 'text_content' in result.processed_data

async def test_url_normalization():
    """Test URL normalization functionality."""
    html = """
    <a href="/relative/path">Link</a>
    <a href="https://absolute.com/path">Link</a>
    <img src="/image.jpg">
    <img src="https://example.com/image.jpg">
    <a href="mailto:test@example.com">Email</a>
    <a href="tel:+1234567890">Phone</a>
    <a href="javascript:void(0)">JS</a>
    <a href="#">Anchor</a>
    """
    
    processor = HTMLProcessor({'normalize_urls': True})
    result = await processor.process(
        {'html_content': html, 'url': 'https://base.com'},
        'https://base.com'
    )
    
    processed_html = result.processed_data['processed_html']
    soup = BeautifulSoup(processed_html, 'html.parser')
    
    # Check relative URL normalization
    assert soup.find('a', href='https://base.com/relative/path')
    assert soup.find('img', src='https://base.com/image.jpg')
    
    # Check absolute URLs remain unchanged
    assert soup.find('a', href='https://absolute.com/path')
    assert soup.find('img', src='https://example.com/image.jpg')
    
    # Check special URLs remain unchanged
    assert soup.find('a', href='mailto:test@example.com')
    assert soup.find('a', href='tel:+1234567890')
    assert soup.find('a', href='javascript:void(0)')
    assert soup.find('a', href='#')

async def test_metadata_extraction(sample_html):
    """Test metadata extraction functionality."""
    processor = HTMLProcessor({'extract_metadata': True})
    result = await processor.process(
        {'html_content': sample_html},
        'https://example.com'
    )
    
    metadata = result.processed_data
    
    # Check title extraction
    assert metadata['title'] == 'Test Page'
    
    # Check meta tags
    assert 'meta_tags' in metadata
    assert metadata['meta_tags']['description'] == 'Test description'
    assert metadata['meta_tags']['og:title'] == 'OG Test Title'
    
    # Check headings
    assert 'headings' in metadata
    assert metadata['headings']['h1'] == ['Main Heading']
    assert metadata['headings']['h2'] == ['Sub Heading']
    
    # Check links
    assert 'links' in metadata
    links = metadata['links']
    assert any(link['href'] == '/relative/link' for link in links)
    assert any(link['href'] == 'https://absolute.link' for link in links)
    
    # Check images
    assert 'images' in metadata
    images = metadata['images']
    assert any(img['src'] == '/test.jpg' and img['alt'] == 'Test image' for img in images)
    assert any(img['src'] == 'https://example.com/test.png' and img['alt'] == 'External image' for img in images)

async def test_whitespace_cleaning():
    """Test whitespace cleaning functionality."""
    html = """
    <div>
        Multiple
        Lines    and
        Spaces
    </div>
    <pre>
        Preserve
        Whitespace
    </pre>
    <code>
        Keep
        Formatting
    </code>
    """
    
    processor = HTMLProcessor({'clean_whitespace': True})
    result = await processor.process(
        {'html_content': html},
        'https://example.com'
    )
    
    processed_html = result.processed_data['processed_html']
    
    # Check normal text is cleaned
    assert 'Multiple Lines and Spaces' in processed_html
    
    # Check preserved elements
    soup = BeautifulSoup(processed_html, 'html.parser')
    pre = soup.find('pre').get_text()
    code = soup.find('code').get_text()
    
    assert '\n' in pre
    assert '\n' in code

async def test_comment_removal():
    """Test HTML comment removal functionality."""
    html = """
    <!-- Header comment -->
    <div>Content</div>
    <!-- Footer comment -->
    <!--[if IE]>
    <div>IE specific</div>
    <![endif]-->
    """
    
    processor = HTMLProcessor({'remove_comments': True})
    result = await processor.process(
        {'html_content': html},
        'https://example.com'
    )
    
    processed_html = result.processed_data['processed_html']
    
    assert '<!-- Header comment -->' not in processed_html
    assert '<!-- Footer comment -->' not in processed_html
    assert '<!--[if IE]>' not in processed_html
    assert '<div>Content</div>' in processed_html

async def test_error_handling():
    """Test error handling in HTML processing."""
    processor = HTMLProcessor()
    
    # Missing required field
    result = await processor.process(
        {'wrong_field': 'content'},
        'https://example.com'
    )
    assert result.errors
    assert 'Validation error' in result.errors[0]
    
    # Invalid HTML that might cause parsing errors
    result = await processor.process(
        {'html_content': '<not>valid</html'},
        'https://example.com'
    )
    assert not result.errors  # BeautifulSoup handles invalid HTML gracefully
    
    # None content
    result = await processor.process(
        {'html_content': None},
        'https://example.com'
    )
    assert result.errors
    assert 'Transformation error' in result.errors[0]

async def test_batch_processing(sample_batch_data):
    """Test batch processing of HTML content."""
    processor = HTMLProcessor()
    
    # Prepare HTML batch data
    html_batch = [
        {'html_content': f'<div>Content {i}</div>', 'url': f'https://example.com/page{i}'}
        for i in range(5)
    ]
    
    results = await processor.process_batch(html_batch)
    
    assert len(results) == len(html_batch)
    assert all(not result.errors for result in results)
    assert all('processed_html' in result.processed_data for result in results)

async def test_performance_metrics():
    """Test performance metrics collection."""
    processor = HTMLProcessor()
    
    # Process multiple items
    for i in range(5):
        await processor.process(
            {'html_content': f'<div>Content {i}</div>'},
            f'https://example.com/page{i}'
        )
    
    # Check metrics
    assert processor.processed_count == 5
    assert processor.error_count == 0
    
    # Process invalid item
    await processor.process(
        {'wrong_field': 'content'},
        'https://example.com/error'
    )
    
    assert processor.processed_count == 5
    assert processor.error_count == 1 