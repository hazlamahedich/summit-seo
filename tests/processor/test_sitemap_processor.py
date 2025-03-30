"""Tests for the SitemapProcessor class."""

import os
import pytest
import aiofiles
from summit_seo.processor.sitemap_processor import SitemapProcessor

# Get the path to the resources directory
RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')

class TestSitemapProcessor:
    """Test cases for the SitemapProcessor."""

    async def load_test_sitemap(self):
        """Load test sitemap.xml file content."""
        sitemap_path = os.path.join(RESOURCES_DIR, 'sitemap.xml')
        async with aiofiles.open(sitemap_path, 'r') as f:
            return await f.read()

    @pytest.mark.asyncio
    async def test_processor_initialization(self):
        """Test that the processor initializes correctly."""
        processor = SitemapProcessor()
        assert processor is not None
        assert processor.processor_type == 'sitemap'

    @pytest.mark.asyncio
    async def test_processor_with_default_config(self):
        """Test processing with default configuration."""
        # Arrange
        processor = SitemapProcessor()
        sitemap_content = await self.load_test_sitemap()
        
        # Act
        result = await processor.process({
            'sitemap_content': sitemap_content
        })
        
        # Assert
        assert result is not None
        assert 'original_size' in result
        assert 'urls' in result
        assert len(result['urls']) == 9  # From our test sitemap.xml
        assert 'url_count' in result
        assert result['url_count'] == 9

    @pytest.mark.asyncio
    async def test_processor_with_custom_config(self):
        """Test processing with custom configuration."""
        # Arrange
        custom_config = {
            'validate_urls': True,
            'extract_lastmod': True,
            'extract_changefreq': True,
            'extract_priority': True,
            'check_images': True,
            'analyze_seo': True
        }
        processor = SitemapProcessor(config=custom_config)
        sitemap_content = await self.load_test_sitemap()
        
        # Act
        result = await processor.process({
            'sitemap_content': sitemap_content
        })
        
        # Assert
        assert 'validation_issues' in result
        assert 'lastmod_dates' in result
        assert 'changefreq_data' in result
        assert 'priority_data' in result
        assert 'images' in result
        assert 'seo_issues' in result

    @pytest.mark.asyncio
    async def test_url_extraction(self):
        """Test that URLs are correctly extracted."""
        # Arrange
        processor = SitemapProcessor()
        sitemap_content = await self.load_test_sitemap()
        
        # Act
        result = await processor.process({
            'sitemap_content': sitemap_content
        })
        
        # Assert
        assert len(result['urls']) == 9
        
        # Check specific URLs from our test file
        urls = {url['loc'] for url in result['urls']}
        assert 'https://example.com/' in urls
        assert 'https://example.com/about' in urls
        assert 'https://example.com/blog/article-1' in urls

    @pytest.mark.asyncio
    async def test_validation_issues_detection(self):
        """Test that validation issues are correctly detected."""
        # Arrange
        processor = SitemapProcessor(config={'validate_urls': True})
        sitemap_content = await self.load_test_sitemap()
        
        # Act
        result = await processor.process({
            'sitemap_content': sitemap_content
        })
        
        # Assert
        assert 'validation_issues' in result
        
        # Our test file has intentional invalid URLs, dates, and priorities
        assert any('malformed URL' in issue['description'] 
                   for issue in result['validation_issues'])
        assert any('invalid date format' in issue['description'] 
                   for issue in result['validation_issues'])
        assert any('invalid priority value' in issue['description'] 
                   for issue in result['validation_issues'])

    @pytest.mark.asyncio
    async def test_lastmod_extraction(self):
        """Test that lastmod dates are correctly extracted."""
        # Arrange
        processor = SitemapProcessor(config={'extract_lastmod': True})
        sitemap_content = await self.load_test_sitemap()
        
        # Act
        result = await processor.process({
            'sitemap_content': sitemap_content
        })
        
        # Assert
        assert 'lastmod_dates' in result
        assert 'newest_page' in result['lastmod_dates']
        assert 'oldest_page' in result['lastmod_dates']
        
        # Our newest page in the test file is the homepage
        assert result['lastmod_dates']['newest_page']['url'] == 'https://example.com/'
        assert result['lastmod_dates']['newest_page']['date'] == '2023-06-15T09:13:45+00:00'

    @pytest.mark.asyncio
    async def test_image_extraction(self):
        """Test that images are correctly extracted."""
        # Arrange
        processor = SitemapProcessor(config={'check_images': True})
        sitemap_content = await self.load_test_sitemap()
        
        # Act
        result = await processor.process({
            'sitemap_content': sitemap_content
        })
        
        # Assert
        assert 'images' in result
        
        # Our test file has images in the blog article URL
        blog_article_images = [img for img in result['images'] 
                               if img['page_url'] == 'https://example.com/blog/article-1']
        assert len(blog_article_images) == 2
        
        image_urls = {img['image_url'] for img in blog_article_images}
        assert 'https://example.com/images/article1-hero.jpg' in image_urls
        assert 'https://example.com/images/article1-thumbnail.jpg' in image_urls

    @pytest.mark.asyncio
    async def test_seo_analysis(self):
        """Test that SEO analysis is correctly performed."""
        # Arrange
        processor = SitemapProcessor(config={'analyze_seo': True})
        sitemap_content = await self.load_test_sitemap()
        
        # Act
        result = await processor.process({
            'sitemap_content': sitemap_content
        })
        
        # Assert
        assert 'seo_issues' in result
        
        # Check for SEO issues related to missing priorities and malformed URLs
        assert any('missing priority' in issue['description'].lower() 
                   for issue in result['seo_issues'])
        assert any('malformed url' in issue['description'].lower() 
                   for issue in result['seo_issues'])

    @pytest.mark.asyncio
    async def test_missing_required_field(self):
        """Test behavior when required field is missing."""
        # Arrange
        processor = SitemapProcessor()
        
        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            await processor.process({})
        
        assert "Missing required field: sitemap_content" in str(excinfo.value) 