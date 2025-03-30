"""Tests for the SocialMediaAnalyzer class."""

import pytest
from bs4 import BeautifulSoup
from summit_seo.analyzer.social_media_analyzer import SocialMediaAnalyzer
from summit_seo.analyzer.base import AnalyzerError

@pytest.fixture
def social_media_analyzer_config():
    """Test configuration for social media analyzer."""
    return {
        'required_og_tags': ['og:title', 'og:type', 'og:image', 'og:url'],
        'required_twitter_tags': ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image'],
        'check_share_buttons': True,
        'check_facebook_pixel': True,
        'check_twitter_pixel': True,
        'image_min_width': 1200,
        'image_min_height': 630
    }

@pytest.fixture
def complete_html():
    """HTML with complete social media tags and features."""
    return """
    <html>
    <head>
        <!-- Open Graph Tags -->
        <meta property="og:title" content="Complete Social Media Integration Example">
        <meta property="og:type" content="website">
        <meta property="og:url" content="https://example.com/page">
        <meta property="og:image" content="https://example.com/image.jpg">
        <meta property="og:image:width" content="1200">
        <meta property="og:image:height" content="630">
        <meta property="og:description" content="This page demonstrates complete social media integration with all required tags.">
        
        <!-- Twitter Card Tags -->
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:site" content="@example">
        <meta name="twitter:title" content="Complete Twitter Card Example">
        <meta name="twitter:description" content="This page demonstrates complete Twitter Card integration.">
        <meta name="twitter:image" content="https://example.com/twitter-image.jpg">
        
        <!-- Facebook Pixel -->
        <script>
        !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
        n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
        n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
        t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
        document,'script','//connect.facebook.net/en_US/fbevents.js');
        fbq('init', '1234567890');
        fbq('track', 'PageView');
        </script>
        
        <!-- Twitter Pixel -->
        <script>
        !function(e,t,n,s,u,a){e.twq||(s=e.twq=function(){s.exe?s.exe.apply(s,arguments):s.queue.push(arguments);
        },s.version='1.1',s.queue=[],u=t.createElement(n),u.async=!0,u.src='//static.ads-twitter.com/uwt.js',
        a=t.getElementsByTagName(n)[0],a.parentNode.insertBefore(u,a))}(window,document,'script');
        twq('init','twitter-pixel-id');
        twq('track','PageView');
        </script>
    </head>
    <body>
        <!-- Social Share Buttons -->
        <div class="social-share-buttons">
            <a href="https://www.facebook.com/sharer/sharer.php?u=https://example.com" class="facebook-share">Share on Facebook</a>
            <a href="https://twitter.com/intent/tweet?url=https://example.com" class="twitter-share">Share on Twitter</a>
            <a href="https://www.linkedin.com/shareArticle?mini=true&url=https://example.com" class="linkedin-share">Share on LinkedIn</a>
            <a href="https://pinterest.com/pin/create/button/?url=https://example.com" class="pinterest-share">Share on Pinterest</a>
        </div>
        
        <!-- Social Media Profile Links -->
        <div class="social-links">
            <a href="https://facebook.com/example" class="facebook-link">Facebook</a>
            <a href="https://twitter.com/example" class="twitter-link">Twitter</a>
            <a href="https://linkedin.com/company/example" class="linkedin-link">LinkedIn</a>
            <a href="https://instagram.com/example" class="instagram-link">Instagram</a>
            <a href="https://youtube.com/channel/example" class="youtube-link">YouTube</a>
        </div>
    </body>
    </html>
    """

@pytest.fixture
def minimal_html():
    """HTML with minimal social media tags."""
    return """
    <html>
    <head>
        <meta property="og:title" content="Minimal Social Example">
    </head>
    <body>
    </body>
    </html>
    """

@pytest.fixture
def invalid_html():
    """Invalid HTML content that will raise an exception."""
    return None  # This will cause the analyzer to raise an AnalyzerError when processed

@pytest.mark.analyzer
@pytest.mark.unit
class TestSocialMediaAnalyzer:
    """Test suite for SocialMediaAnalyzer."""

    def test_initialization(self, social_media_analyzer_config):
        """Test analyzer initialization with config."""
        analyzer = SocialMediaAnalyzer(social_media_analyzer_config)
        assert analyzer.config == social_media_analyzer_config
        assert analyzer.required_og_tags == social_media_analyzer_config['required_og_tags']
        assert analyzer.required_twitter_tags == social_media_analyzer_config['required_twitter_tags']
        assert analyzer.check_share_buttons is True
        assert analyzer.check_facebook_pixel is True
        assert analyzer.image_min_width == 1200
        assert analyzer.image_min_height == 630

    def test_initialization_default_config(self):
        """Test analyzer initialization with default config."""
        analyzer = SocialMediaAnalyzer()
        assert isinstance(analyzer.config, dict)
        assert analyzer.required_og_tags == analyzer.REQUIRED_OG_TAGS
        assert analyzer.required_twitter_tags == analyzer.REQUIRED_TWITTER_TAGS
        assert analyzer.check_share_buttons is True
        assert analyzer.check_facebook_pixel is True
        assert analyzer.check_twitter_pixel is True

    def test_analyze_complete_html(self, complete_html):
        """Test analysis of HTML with complete social media tags."""
        analyzer = SocialMediaAnalyzer()
        data = {
            'html': complete_html,
            'url': 'https://example.com'
        }
        result = analyzer.analyze(data)
        
        # Check Open Graph data
        assert 'open_graph' in result.data
        assert 'tags' in result.data['open_graph']
        assert len(result.data['open_graph']['tags']) >= 4
        assert 'og:title' in result.data['open_graph']['tags']
        assert 'og:type' in result.data['open_graph']['tags']
        assert 'og:url' in result.data['open_graph']['tags']
        assert 'og:image' in result.data['open_graph']['tags']
        
        # Check Twitter Card data
        assert 'twitter_cards' in result.data
        assert 'tags' in result.data['twitter_cards']
        assert len(result.data['twitter_cards']['tags']) >= 4
        assert 'twitter:card' in result.data['twitter_cards']['tags']
        assert 'twitter:title' in result.data['twitter_cards']['tags']
        assert 'twitter:description' in result.data['twitter_cards']['tags']
        assert 'twitter:image' in result.data['twitter_cards']['tags']
        
        # Check share buttons
        assert 'share_buttons' in result.data
        assert 'platforms' in result.data['share_buttons']
        assert len(result.data['share_buttons']['platforms']) >= 2
        
        # Check social links
        assert 'social_links' in result.data
        assert 'platforms' in result.data['social_links']
        assert len(result.data['social_links']['platforms']) >= 2
        
        # Check social pixels
        assert 'social_pixels' in result.data
        assert result.data['social_pixels']['facebook_pixel'] is True
        assert result.data['social_pixels']['twitter_pixel'] is True
        
        # Check score
        assert result.score > 0.8  # High score for good social media integration

    def test_analyze_minimal_html(self, minimal_html):
        """Test analysis of HTML with minimal social media tags."""
        analyzer = SocialMediaAnalyzer()
        data = {
            'html': minimal_html,
            'url': 'https://example.com'
        }
        result = analyzer.analyze(data)
        
        # Check issues and recommendations
        assert len(result.issues) > 0
        assert len(result.warnings) > 0
        assert len(result.recommendations) > 0
        
        # Check score
        assert result.score < 0.5  # Low score for minimal integration

    def test_analyze_missing_html(self):
        """Test analysis with missing HTML content."""
        analyzer = SocialMediaAnalyzer()
        data = {
            'url': 'https://example.com'
        }
        with pytest.raises(AnalyzerError):
            analyzer.analyze(data)

    def test_analyze_invalid_html(self, invalid_html):
        """Test analysis with invalid HTML content."""
        analyzer = SocialMediaAnalyzer()
        data = {
            'html': invalid_html,
            'url': 'https://example.com'
        }
        with pytest.raises(AnalyzerError):
            analyzer.analyze(data)

    def test_open_graph_analysis(self, complete_html):
        """Test Open Graph tag analysis."""
        analyzer = SocialMediaAnalyzer()
        soup = BeautifulSoup(complete_html, 'html.parser')
        url = 'https://example.com'
        
        result = analyzer._analyze_open_graph(soup, url)
        
        assert 'data' in result
        assert 'tags' in result['data']
        assert len(result['data']['tags']) >= 4
        assert len(result['issues']) == 0
        assert 'og:title' in result['data']['tags']
        assert 'og:type' in result['data']['tags']
        assert 'og:url' in result['data']['tags']
        assert 'og:image' in result['data']['tags']

    def test_twitter_cards_analysis(self, complete_html):
        """Test Twitter Card tag analysis."""
        analyzer = SocialMediaAnalyzer()
        soup = BeautifulSoup(complete_html, 'html.parser')
        url = 'https://example.com'
        
        result = analyzer._analyze_twitter_cards(soup, url)
        
        assert 'data' in result
        assert 'tags' in result['data']
        assert len(result['data']['tags']) >= 4
        assert len(result['issues']) == 0
        assert 'twitter:card' in result['data']['tags']
        assert 'twitter:title' in result['data']['tags']
        assert 'twitter:description' in result['data']['tags']
        assert 'twitter:image' in result['data']['tags']

    def test_share_buttons_analysis(self, complete_html):
        """Test social share buttons analysis."""
        analyzer = SocialMediaAnalyzer()
        soup = BeautifulSoup(complete_html, 'html.parser')
        
        result = analyzer._analyze_share_buttons(soup)
        
        assert 'data' in result
        assert 'platforms' in result['data']
        assert 'count' in result['data']
        assert result['data']['count'] > 0
        assert len(result['issues']) == 0

    def test_social_links_analysis(self, complete_html):
        """Test social media links analysis."""
        analyzer = SocialMediaAnalyzer()
        soup = BeautifulSoup(complete_html, 'html.parser')
        
        result = analyzer._analyze_social_links(soup)
        
        assert 'data' in result
        assert 'platforms' in result['data']
        assert 'links' in result['data']
        assert 'count' in result['data']
        assert result['data']['count'] > 0
        assert len(result['issues']) == 0

    def test_social_pixels_analysis(self, complete_html):
        """Test social media pixels analysis."""
        analyzer = SocialMediaAnalyzer()
        soup = BeautifulSoup(complete_html, 'html.parser')
        
        result = analyzer._analyze_social_pixels(soup)
        
        assert 'data' in result
        assert 'facebook_pixel' in result['data']
        assert 'twitter_pixel' in result['data']
        assert result['data']['facebook_pixel'] is True
        assert result['data']['twitter_pixel'] is True
        assert len(result['issues']) == 0

    def test_score_calculation(self, complete_html, minimal_html):
        """Test social media score calculation."""
        analyzer = SocialMediaAnalyzer()
        
        # Test with complete HTML
        data_complete = {
            'html': complete_html,
            'url': 'https://example.com'
        }
        result_complete = analyzer.analyze(data_complete)
        
        # Test with minimal HTML
        data_minimal = {
            'html': minimal_html,
            'url': 'https://example.com'
        }
        result_minimal = analyzer.analyze(data_minimal)
        
        assert result_complete.score > 0.7  # High score for good integration
        assert result_minimal.score < 0.5  # Low score for minimal integration
        assert result_complete.score > result_minimal.score 