"""Tests for the ContentAnalyzer class."""

import os
import pytest
import aiofiles
from summit_seo.analyzer.content_analyzer import ContentAnalyzer

# Get the path to the resources directory
RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')

class TestContentAnalyzer:
    """Test cases for the ContentAnalyzer."""

    async def load_test_html(self):
        """Load test HTML file content."""
        html_path = os.path.join(RESOURCES_DIR, 'sample.html')
        async with aiofiles.open(html_path, 'r') as f:
            return await f.read()

    @pytest.mark.asyncio
    async def test_analyzer_initialization(self):
        """Test that the analyzer initializes correctly."""
        analyzer = ContentAnalyzer()
        assert analyzer is not None

    @pytest.mark.asyncio
    async def test_basic_content_analysis(self):
        """Test basic content analysis functionality."""
        # Arrange
        analyzer = ContentAnalyzer()
        html_content = await self.load_test_html()
        
        # Act
        result = await analyzer.analyze(html_content)
        
        # Assert
        assert result is not None
        assert 'title' in result
        assert result['title'] == 'Sample Page for Summit SEO Testing'
        assert 'meta_description' in result
        assert 'word_count' in result
        assert result['word_count'] > 0
        assert 'paragraph_count' in result
        assert result['paragraph_count'] > 0

    @pytest.mark.asyncio
    async def test_heading_structure_analysis(self):
        """Test heading structure analysis."""
        # Arrange
        analyzer = ContentAnalyzer()
        html_content = await self.load_test_html()
        
        # Act
        result = await analyzer.analyze(html_content)
        
        # Assert
        assert 'headings' in result
        headings = result['headings']
        
        # Check heading counts by level
        assert 'h1_count' in headings
        assert headings['h1_count'] == 1
        assert 'h2_count' in headings
        assert headings['h2_count'] > 0
        assert 'h3_count' in headings
        assert headings['h3_count'] > 0
        
        # Check heading content
        assert 'h1' in headings
        assert 'Welcome to the Summit SEO Test Page' in headings['h1'][0]['text']
        
        # Check hierarchy issues
        assert 'hierarchy_issues' in headings
        
        # Check hierarchy score
        assert 'hierarchy_score' in headings
        assert 0 <= headings['hierarchy_score'] <= 100

    @pytest.mark.asyncio
    async def test_keyword_analysis(self):
        """Test keyword analysis functionality."""
        # Arrange
        analyzer = ContentAnalyzer()
        html_content = await self.load_test_html()
        
        # Act
        result = await analyzer.analyze(html_content, keywords=['content analyzer', 'SEO testing', 'Summit SEO'])
        
        # Assert
        assert 'keyword_analysis' in result
        keyword_analysis = result['keyword_analysis']
        
        # Check keyword occurrences
        assert 'keyword_occurrences' in keyword_analysis
        
        # Check keyword density
        assert 'keyword_density' in keyword_analysis
        
        # Check keyword in important elements
        assert 'keywords_in_title' in keyword_analysis
        assert 'keywords_in_headings' in keyword_analysis
        assert 'keywords_in_meta_description' in keyword_analysis
        
        # Check overall keyword score
        assert 'keyword_score' in keyword_analysis
        assert 0 <= keyword_analysis['keyword_score'] <= 100

    @pytest.mark.asyncio
    async def test_link_analysis(self):
        """Test link analysis functionality."""
        # Arrange
        analyzer = ContentAnalyzer()
        html_content = await self.load_test_html()
        base_url = 'https://example.com'
        
        # Act
        result = await analyzer.analyze(html_content, url=base_url)
        
        # Assert
        assert 'link_analysis' in result
        link_analysis = result['link_analysis']
        
        # Check link counts
        assert 'internal_links' in link_analysis
        assert len(link_analysis['internal_links']) > 0
        assert 'external_links' in link_analysis
        assert len(link_analysis['external_links']) > 0
        
        # Check link attributes
        assert 'nofollow_links' in link_analysis
        
        # Check link distribution
        assert 'link_distribution_score' in link_analysis
        assert 0 <= link_analysis['link_distribution_score'] <= 100

    @pytest.mark.asyncio
    async def test_image_analysis(self):
        """Test image analysis functionality."""
        # Arrange
        analyzer = ContentAnalyzer()
        html_content = await self.load_test_html()
        
        # Act
        result = await analyzer.analyze(html_content)
        
        # Assert
        assert 'image_analysis' in result
        image_analysis = result['image_analysis']
        
        # Check image counts
        assert 'total_images' in image_analysis
        assert image_analysis['total_images'] > 0
        
        # Check alt text analysis
        assert 'images_missing_alt' in image_analysis
        assert 'images_with_alt' in image_analysis
        
        # Check alt text quality score
        assert 'alt_text_score' in image_analysis
        assert 0 <= image_analysis['alt_text_score'] <= 100

    @pytest.mark.asyncio
    async def test_content_to_code_ratio_analysis(self):
        """Test content-to-code ratio analysis."""
        # Arrange
        analyzer = ContentAnalyzer()
        html_content = await self.load_test_html()
        
        # Act
        result = await analyzer.analyze(html_content)
        
        # Assert
        assert 'content_to_code_ratio' in result
        ratio_analysis = result['content_to_code_ratio']
        
        # Check ratio
        assert 'ratio' in ratio_analysis
        assert ratio_analysis['ratio'] > 0
        
        # Check text content size
        assert 'text_content_size' in ratio_analysis
        assert ratio_analysis['text_content_size'] > 0
        
        # Check HTML size
        assert 'html_size' in ratio_analysis
        assert ratio_analysis['html_size'] > 0
        
        # Check ratio score
        assert 'ratio_score' in ratio_analysis
        assert 0 <= ratio_analysis['ratio_score'] <= 100

    @pytest.mark.asyncio
    async def test_structured_data_analysis(self):
        """Test structured data analysis."""
        # Arrange
        analyzer = ContentAnalyzer()
        html_content = await self.load_test_html()
        
        # Act
        result = await analyzer.analyze(html_content)
        
        # Assert
        assert 'structured_data' in result
        structured_data = result['structured_data']
        
        # Check detected schemas
        assert 'detected_schemas' in structured_data
        
        # Check schema.org types
        assert 'schema_types' in structured_data
        assert 'Article' in structured_data['schema_types']
        assert 'Product' in structured_data['schema_types']
        
        # Check schema formats
        assert 'formats' in structured_data
        assert 'json_ld' in structured_data['formats']
        assert 'microdata' in structured_data['formats']

    @pytest.mark.asyncio
    async def test_accessibility_analysis(self):
        """Test accessibility analysis."""
        # Arrange
        analyzer = ContentAnalyzer()
        html_content = await self.load_test_html()
        
        # Act
        result = await analyzer.analyze(html_content)
        
        # Assert
        assert 'accessibility' in result
        accessibility = result['accessibility']
        
        # Check language attribute
        assert 'has_language_attribute' in accessibility
        
        # Check image accessibility
        assert 'images_without_alt' in accessibility
        assert accessibility['images_without_alt'] > 0  # Our sample has an image without alt
        
        # Check form accessibility
        assert 'form_inputs_without_labels' in accessibility
        assert accessibility['form_inputs_without_labels'] > 0  # Our sample has inputs without labels
        
        # Check empty interactive elements
        assert 'empty_buttons' in accessibility
        assert accessibility['empty_buttons'] > 0  # Our sample has an empty button
        
        # Check overall accessibility score
        assert 'accessibility_score' in accessibility
        assert 0 <= accessibility['accessibility_score'] <= 100

    @pytest.mark.asyncio
    async def test_content_freshness_analysis(self):
        """Test content freshness analysis."""
        # Arrange
        analyzer = ContentAnalyzer()
        html_content = await self.load_test_html()
        
        # Act
        result = await analyzer.analyze(html_content)
        
        # Assert
        assert 'content_freshness' in result
        freshness = result['content_freshness']
        
        # Check publication date
        assert 'publication_date' in freshness
        assert freshness['publication_date'] == '2023-06-10'
        
        # Check modification date
        assert 'modification_date' in freshness
        assert freshness['modification_date'] == '2023-06-15'
        
        # Check date references in content
        assert 'date_references' in freshness
        assert len(freshness['date_references']) > 0
        
        # Check overall freshness score
        assert 'freshness_score' in freshness
        assert 0 <= freshness['freshness_score'] <= 100

    @pytest.mark.asyncio
    async def test_content_analysis_warnings_and_suggestions(self):
        """Test warnings and suggestions from content analysis."""
        # Arrange
        analyzer = ContentAnalyzer()
        html_content = await self.load_test_html()
        
        # Act
        result = await analyzer.analyze(html_content)
        
        # Assert
        assert 'warnings' in result
        assert 'suggestions' in result
        
        # Our sample has intentional issues that should generate warnings
        assert len(result['warnings']) > 0
        
        # Our sample should also generate suggestions for improvement
        assert len(result['suggestions']) > 0 