"""Test cases for Robots.txt processor functionality."""

import pytest
from summit_seo.processor.robotstxt_processor import RobotsTxtProcessor
from summit_seo.processor.base import TransformationError

@pytest.fixture
def sample_robotstxt() -> str:
    """Sample robots.txt content for testing."""
    return """
    User-agent: *
    Disallow: /admin/
    Disallow: /private/
    Allow: /private/public/
    
    User-agent: Googlebot
    Allow: /
    Disallow: /private/
    
    User-agent: Bingbot
    Disallow: /
    
    Sitemap: https://example.com/sitemap.xml
    Sitemap: https://example.com/sitemap2.xml
    
    Crawl-delay: 5
    """

@pytest.fixture
def sample_robotstxt_with_issues() -> str:
    """Sample robots.txt with issues for testing."""
    return """
    User-agent: *
    Disallow: /
    
    User-agent: Googlebot
    Disallow: /private/
    Allow: /private/
    
    User-agent: *
    Disallow: /admin/
    
    Sitemap: invalid-url
    
    Host: example.com
    Host: example.org
    
    Unknown: directive
    """

@pytest.fixture
def invalid_robotstxt_cases() -> list:
    """List of invalid robots.txt content for testing."""
    return [
        None,  # None value
        "",    # Empty string
        "Not a valid robots.txt",  # No directives
        "User-agent: \nDisallow: /",  # Empty user-agent
        "Disallow: /"  # Missing user-agent
    ]

@pytest.fixture
def sample_config() -> dict:
    """Sample configuration for Robots.txt processor."""
    return {
        'validate_directives': True,
        'check_seo_issues': True,
        'evaluate_crawler_access': True,
        'detect_sitemaps': True,
        'extract_crawl_delays': True,
        'check_common_paths': True
    }

async def test_robotstxt_processor_initialization(sample_config):
    """Test Robots.txt processor initialization with configuration."""
    processor = RobotsTxtProcessor(sample_config)
    
    # Verify configuration is properly set
    assert processor.validate_directives == sample_config['validate_directives']
    assert processor.check_seo_issues == sample_config['check_seo_issues']
    assert processor.evaluate_crawler_access == sample_config['evaluate_crawler_access']
    assert processor.detect_sitemaps == sample_config['detect_sitemaps']
    assert processor.extract_crawl_delays == sample_config['extract_crawl_delays']
    assert processor.check_common_paths == sample_config['check_common_paths']

async def test_robotstxt_processor_validate_config():
    """Test configuration validation for Robots.txt processor."""
    # Valid boolean configurations
    valid_configs = [
        {'validate_directives': True},
        {'check_seo_issues': False},
        {'evaluate_crawler_access': True},
        {'detect_sitemaps': False},
        {'extract_crawl_delays': True},
        {'check_common_paths': False}
    ]
    
    for config in valid_configs:
        processor = RobotsTxtProcessor(config)
        for key, value in config.items():
            assert getattr(processor, key) == value
    
    # Invalid configurations
    invalid_configs = [
        {'validate_directives': 'not-a-boolean'},
        {'check_seo_issues': 1},
        {'evaluate_crawler_access': 'yes'},
        {'detect_sitemaps': 0},
        {'extract_crawl_delays': 'True'},
        {'check_common_paths': None}
    ]
    
    for config in invalid_configs:
        with pytest.raises(ValueError):
            RobotsTxtProcessor(config)

async def test_robotstxt_process_valid_content(sample_robotstxt):
    """Test processing valid robots.txt content."""
    processor = RobotsTxtProcessor()
    result = await processor.process({'robotstxt_content': sample_robotstxt})
    
    # Verify no errors occurred
    assert not result.errors
    
    # Check basic result data
    assert 'original_size' in result.processed_data
    assert result.processed_data['original_size'] == len(sample_robotstxt)
    
    # Check directives
    assert 'directives' in result.processed_data
    directives = result.processed_data['directives']
    
    # Verify user-agents were parsed correctly
    assert len(directives['user_agents']) >= 3
    assert '*' in directives['user_agents']
    assert 'googlebot' in directives['user_agents']
    assert 'bingbot' in directives['user_agents']
    
    # Verify disallow rules
    assert '/admin/' in directives['user_agents']['*']['disallow']
    assert '/private/' in directives['user_agents']['*']['disallow']
    
    # Verify allow rules
    assert '/private/public/' in directives['user_agents']['*']['allow']
    
    # Verify sitemaps
    assert 'sitemaps' in result.processed_data
    assert len(result.processed_data['sitemaps']) == 2
    assert 'https://example.com/sitemap.xml' in result.processed_data['sitemaps']
    assert 'https://example.com/sitemap2.xml' in result.processed_data['sitemaps']
    
    # Verify crawl delay
    assert 'crawl_delays' in result.processed_data
    assert result.processed_data['crawl_delays']['*'] == 5

async def test_robotstxt_process_with_issues(sample_robotstxt_with_issues):
    """Test processing robots.txt with issues."""
    processor = RobotsTxtProcessor()
    result = await processor.process({'robotstxt_content': sample_robotstxt_with_issues})
    
    # Should process without errors despite issues
    assert not result.errors
    
    # Check validation issues
    assert 'validation_issues' in result.processed_data
    issues = result.processed_data['validation_issues']
    
    # Should detect duplicate user-agent
    assert any('duplicate' in issue['message'].lower() for issue in issues)
    
    # Should detect invalid sitemap URL
    assert any('invalid sitemap url' in issue['message'].lower() for issue in issues)
    
    # Should detect duplicate host directive
    assert any('multiple host' in issue['message'].lower() for issue in issues)
    
    # Should detect unknown directive
    assert any('unknown directive' in issue['message'].lower() for issue in issues)
    
    # Should detect conflicting rules
    assert any('conflicting' in issue['message'].lower() for issue in issues)

async def test_robotstxt_seo_issues_detection(sample_robotstxt, sample_robotstxt_with_issues):
    """Test detection of SEO issues in robots.txt."""
    processor = RobotsTxtProcessor({'check_seo_issues': True})
    
    # Test with well-formed robots.txt
    result = await processor.process({'robotstxt_content': sample_robotstxt})
    assert 'seo_issues' in result.processed_data
    
    # Test with problematic robots.txt
    result = await processor.process({'robotstxt_content': sample_robotstxt_with_issues})
    assert 'seo_issues' in result.processed_data
    
    seo_issues = result.processed_data['seo_issues']
    
    # Should detect blocking all crawlers
    assert any('block all' in issue['message'].lower() for issue in seo_issues)
    
    # Should detect duplicate directives
    assert any('duplicate' in issue['message'].lower() for issue in seo_issues)

async def test_robotstxt_crawler_access_evaluation(sample_robotstxt):
    """Test evaluation of crawler access in robots.txt."""
    processor = RobotsTxtProcessor({'evaluate_crawler_access': True})
    result = await processor.process({'robotstxt_content': sample_robotstxt})
    
    # Check crawler access results
    assert 'crawler_access' in result.processed_data
    crawler_access = result.processed_data['crawler_access']
    
    # Test specific paths
    googlebot_access = crawler_access.get('googlebot', {})
    assert googlebot_access.get('/private/') is False
    assert googlebot_access.get('/public/') is True
    
    general_access = crawler_access.get('*', {})
    assert general_access.get('/admin/') is False
    assert general_access.get('/private/') is False
    assert general_access.get('/private/public/') is True
    
    bingbot_access = crawler_access.get('bingbot', {})
    assert bingbot_access.get('/') is False

async def test_robotstxt_sitemap_detection(sample_robotstxt):
    """Test detection of sitemaps in robots.txt."""
    processor = RobotsTxtProcessor({'detect_sitemaps': True})
    result = await processor.process({'robotstxt_content': sample_robotstxt})
    
    # Check sitemaps
    assert 'sitemaps' in result.processed_data
    sitemaps = result.processed_data['sitemaps']
    
    assert len(sitemaps) == 2
    assert 'https://example.com/sitemap.xml' in sitemaps
    assert 'https://example.com/sitemap2.xml' in sitemaps

async def test_robotstxt_crawl_delay_extraction(sample_robotstxt):
    """Test extraction of crawl delay from robots.txt."""
    processor = RobotsTxtProcessor({'extract_crawl_delays': True})
    result = await processor.process({'robotstxt_content': sample_robotstxt})
    
    # Check crawl delays
    assert 'crawl_delays' in result.processed_data
    crawl_delays = result.processed_data['crawl_delays']
    
    assert '*' in crawl_delays
    assert crawl_delays['*'] == 5

async def test_robotstxt_common_paths_checking():
    """Test checking access to common paths in robots.txt."""
    robots_txt = """
    User-agent: *
    Disallow: /wp-admin/
    Disallow: /wp-content/
    Disallow: /search
    
    User-agent: Googlebot
    Allow: /wp-content/uploads/
    """
    
    processor = RobotsTxtProcessor({'check_common_paths': True})
    result = await processor.process({'robotstxt_content': robots_txt})
    
    # Check common paths access
    assert 'path_access' in result.processed_data
    path_access = result.processed_data['path_access']
    
    # General agent
    assert path_access['*'].get('/wp-admin/') is False
    assert path_access['*'].get('/wp-content/') is False
    assert path_access['*'].get('/search') is False
    
    # Googlebot
    assert path_access['googlebot'].get('/wp-admin/') is False
    assert path_access['googlebot'].get('/wp-content/') is False
    assert path_access['googlebot'].get('/wp-content/uploads/') is True

async def test_robotstxt_metrics_calculation(sample_robotstxt):
    """Test calculation of metrics from robots.txt."""
    processor = RobotsTxtProcessor()
    result = await processor.process({'robotstxt_content': sample_robotstxt})
    
    # Check metrics
    assert 'metrics' in result.processed_data
    metrics = result.processed_data['metrics']
    
    # Verify metrics calculation
    assert metrics['user_agent_count'] == 3
    assert metrics['disallow_rule_count'] >= 4
    assert metrics['allow_rule_count'] >= 1
    assert metrics['sitemap_count'] == 2
    assert 'average_rules_per_agent' in metrics
    assert 'complexity_score' in metrics

async def test_robotstxt_process_invalid_content(invalid_robotstxt_cases):
    """Test processing invalid robots.txt content."""
    processor = RobotsTxtProcessor()
    
    for invalid_content in invalid_robotstxt_cases:
        if invalid_content is None:
            # None value should raise validation error
            with pytest.raises(Exception):
                await processor.process({})
        else:
            # Empty or invalid content should process but have validation issues
            result = await processor.process({'robotstxt_content': invalid_content})
            if not invalid_content:
                assert result.processed_data.get('is_empty', False)
            else:
                assert result.processed_data['validation_issues']

async def test_robotstxt_missing_required_fields():
    """Test handling of missing required fields."""
    processor = RobotsTxtProcessor()
    
    # Missing robotstxt_content field
    with pytest.raises(Exception):
        await processor.process({'wrong_field': 'content'})

async def test_robotstxt_handle_transformation_error():
    """Test handling of transformation errors."""
    # Create a faulty processor to test error handling
    class FaultyProcessor(RobotsTxtProcessor):
        async def _process_data(self, data):
            raise Exception("Test error")
    
    processor = FaultyProcessor()
    
    # Should raise TransformationError
    with pytest.raises(TransformationError):
        await processor.process({'robotstxt_content': 'User-agent: *\nDisallow: /'})

async def test_robotstxt_complete_process():
    """Test complete processing workflow with all features enabled."""
    robots_txt = """
    User-agent: *
    Disallow: /secret/
    Allow: /public/
    
    User-agent: Googlebot
    Allow: /secret/allowed-for-google/
    Disallow: /noindex/
    
    Sitemap: https://example.com/sitemap.xml
    
    Crawl-delay: 3
    """
    
    config = {
        'validate_directives': True,
        'check_seo_issues': True,
        'evaluate_crawler_access': True,
        'detect_sitemaps': True,
        'extract_crawl_delays': True,
        'check_common_paths': True
    }
    
    processor = RobotsTxtProcessor(config)
    result = await processor.process({'robotstxt_content': robots_txt})
    
    # Verify no errors
    assert not result.errors
    
    # Verify all sections exist
    expected_sections = [
        'directives', 'validation_issues', 'seo_issues', 'crawler_access',
        'sitemaps', 'crawl_delays', 'path_access', 'metrics'
    ]
    
    for section in expected_sections:
        assert section in result.processed_data
    
    # Check specific contents in detail
    directives = result.processed_data['directives']
    assert 'user_agents' in directives
    assert '*' in directives['user_agents']
    assert 'googlebot' in directives['user_agents']
    
    # Verify crawl delay
    assert result.processed_data['crawl_delays']['*'] == 3
    
    # Verify sitemap
    assert 'https://example.com/sitemap.xml' in result.processed_data['sitemaps'] 