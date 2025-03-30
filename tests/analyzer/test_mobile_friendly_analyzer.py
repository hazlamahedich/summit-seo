"""Tests for the MobileFriendlyAnalyzer class."""

import pytest
from typing import Dict, Any
from bs4 import BeautifulSoup
from summit_seo.analyzer.mobile_friendly_analyzer import MobileFriendlyAnalyzer
from summit_seo.analyzer.base import AnalysisResult
from summit_seo.analyzer.factory import AnalyzerFactory

# Sample HTML with good mobile-friendliness
MOBILE_FRIENDLY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#4285f4">
    <link rel="apple-touch-icon" href="/icon.png">
    <link rel="manifest" href="/manifest.json">
    <title>Mobile-Friendly Page Example</title>
    <style>
        @media (max-width: 768px) {
            body {
                font-size: 16px;
            }
            .container {
                width: 100%;
                padding: 0 15px;
            }
        }
        .button {
            min-width: 48px;
            min-height: 48px;
            margin: 10px;
        }
        table {
            max-width: 100%;
            overflow-x: auto;
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <nav>
                <button class="button">Menu</button>
                <ul class="nav-items">
                    <li><a href="/" class="button">Home</a></li>
                    <li><a href="/about" class="button">About</a></li>
                    <li><a href="/contact" class="button">Contact</a></li>
                </ul>
            </nav>
        </header>
        <main>
            <h1>Welcome to Our Mobile-Friendly Website</h1>
            <section>
                <h2>About Us</h2>
                <p>This is an example of a mobile-friendly website with responsive design.</p>
                <div class="responsive-image">
                    <img src="example.jpg" alt="Responsive design example" style="max-width: 100%; height: auto;">
                </div>
            </section>
            <section>
                <h2>Our Services</h2>
                <div class="table-responsive">
                    <table>
                        <tr>
                            <th>Service</th>
                            <th>Description</th>
                        </tr>
                        <tr>
                            <td>Web Design</td>
                            <td>Responsive websites that work on all devices</td>
                        </tr>
                        <tr>
                            <td>Mobile Apps</td>
                            <td>Native and hybrid applications</td>
                        </tr>
                    </table>
                </div>
            </section>
            <section>
                <h2>Contact Form</h2>
                <form>
                    <div>
                        <label for="name">Name:</label>
                        <input type="text" id="name" name="name" required style="font-size: 16px; height: 48px;">
                    </div>
                    <div>
                        <label for="email">Email:</label>
                        <input type="email" id="email" name="email" required style="font-size: 16px; height: 48px;">
                    </div>
                    <div>
                        <label for="message">Message:</label>
                        <textarea id="message" name="message" rows="4" style="font-size: 16px;"></textarea>
                    </div>
                    <button type="submit" class="button">Send Message</button>
                </form>
            </section>
        </main>
        <footer>
            <p>&copy; 2025 Mobile-Friendly Example Company</p>
        </footer>
    </div>
</body>
</html>
"""

# Sample HTML with mobile-unfriendliness issues
MOBILE_UNFRIENDLY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <!-- Missing viewport meta tag -->
    <title>Non-Mobile-Friendly Page Example</title>
    <style>
        body {
            font-size: 12px;
            width: 1200px;
            margin: 0 auto;
        }
        .button {
            width: 40px;
            height: 30px;
            margin: 2px;
        }
        .small-text {
            font-size: 8px;
        }
    </style>
</head>
<body>
    <div style="width: 1200px; overflow-x: scroll;">
        <div class="header">
            <div class="nav">
                <a href="/" class="button">Home</a>
                <a href="/about" class="button">About</a>
                <a href="/contact" class="button">Contact</a>
            </div>
        </div>
        <div class="content">
            <div class="welcome" style="font-size: 24px;">Welcome to Our Website</div>
            <div class="about">
                <div style="font-size: 18px;">About Us</div>
                <p>This is a website with mobile-unfriendliness issues.</p>
                <img src="example.jpg" style="width: 800px;">
            </div>
            <div class="services">
                <div style="font-size: 18px;">Our Services</div>
                <table style="width: 1000px;">
                    <tr>
                        <th>Service</th>
                        <th>Description</th>
                        <th>Price</th>
                        <th>Duration</th>
                        <th>Availability</th>
                        <th>Location</th>
                    </tr>
                    <tr>
                        <td>Web Design</td>
                        <td>Fixed-width websites</td>
                        <td>$1000</td>
                        <td>2 weeks</td>
                        <td>Immediate</td>
                        <td>Online</td>
                    </tr>
                </table>
            </div>
            <div class="contact">
                <div style="font-size: 18px;">Contact Form</div>
                <form>
                    <div>
                        Name:
                        <input type="text" name="name" style="width: 200px; font-size: 10px;">
                    </div>
                    <div>
                        Email:
                        <input type="email" name="email" style="width: 200px; font-size: 10px;">
                    </div>
                    <div>
                        Message:
                        <textarea name="message" rows="4" style="width: 300px; font-size: 10px;"></textarea>
                    </div>
                    <div class="button" style="font-size: 10px; width: 60px; height: 25px;">Submit</div>
                </form>
            </div>
        </div>
        <div class="footer">
            <p class="small-text">&copy; 2025 Example Company</p>
        </div>
    </div>
</body>
</html>
"""

@pytest.fixture
def mobile_friendly_analyzer():
    """Create a mobile friendly analyzer instance."""
    return MobileFriendlyAnalyzer()

def test_analyze_mobile_friendly_page(mobile_friendly_analyzer):
    """Test analyzing a page with good mobile-friendliness."""
    result = mobile_friendly_analyzer.analyze(MOBILE_FRIENDLY_HTML)
    
    assert isinstance(result, AnalysisResult)
    assert result.score >= 0.7  # Good score for mobile-friendly page
    assert result.data['mobile_score'] >= 70
    
    # Check for viewport meta tag
    assert not any("viewport meta tag" in issue for issue in result.issues)
    
    # Check that common mobile issues aren't present
    assert not any("fixed width" in issue.lower() for issue in result.issues)
    assert not any("small touch target" in issue.lower() for issue in result.issues)
    assert not any("font size" in issue.lower() for issue in result.issues)
    
    # Verify document has proper mobile-friendly aspects
    assert not any("responsive design" in issue.lower() for issue in result.issues)
    assert not any("small font" in issue.lower() for issue in result.issues)

def test_analyze_mobile_unfriendly_page(mobile_friendly_analyzer):
    """Test analyzing a page with mobile-unfriendliness issues."""
    result = mobile_friendly_analyzer.analyze(MOBILE_UNFRIENDLY_HTML)
    
    assert isinstance(result, AnalysisResult)
    assert result.score < 0.5  # Lower score for mobile-unfriendly page
    assert result.data['mobile_score'] < 50
    assert result.data['has_mobile_issues'] is True
    
    # Check for expected mobile-unfriendliness issues
    assert any("viewport meta tag" in issue for issue in result.issues)
    
    # Check that issues are detected across different categories
    assert result.data['critical_severity_issues'] > 0  # Should have some critical issues
    assert result.data['high_severity_issues'] > 0  # Should have some high severity issues
    
    # Check for specific issue detection
    assert len(result.issues) > 0
    assert len(result.recommendations) > 0
    
    # Check that specific issues are detected in the mobile_issues data
    mobile_issue_names = [issue['name'] for issue in result.data['mobile_issues']]
    assert any("Font Size" in name for name in mobile_issue_names)
    assert any("Fixed Width" in name for name in mobile_issue_names)
    assert any("Responsive Design" in name for name in mobile_issue_names)

def test_analyze_viewport(mobile_friendly_analyzer):
    """Test viewport analysis specifically."""
    html_with_viewport = '<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body>Content</body></html>'
    html_without_viewport = '<html><head></head><body>Content</body></html>'
    
    # Test with viewport meta tag
    result_with_viewport = mobile_friendly_analyzer.analyze(html_with_viewport)
    assert not any("viewport meta tag" in issue for issue in result_with_viewport.issues)
    
    # Test without viewport meta tag
    result_without_viewport = mobile_friendly_analyzer.analyze(html_without_viewport)
    assert any("viewport meta tag" in issue for issue in result_without_viewport.issues)

def test_analyze_touch_targets(mobile_friendly_analyzer):
    """Test touch target analysis specifically."""
    html_good_targets = '<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body><a href="#" style="display:block; width:48px; height:48px;">Link</a></body></html>'
    html_small_targets = '<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body><a href="#" style="display:block; width:20px; height:20px;">Link</a></body></html>'
    
    # Test with good touch targets
    result_good = mobile_friendly_analyzer.analyze(html_good_targets)
    assert not any("touch target" in issue.lower() for issue in result_good.issues)
    
    # Test with small touch targets
    result_small = mobile_friendly_analyzer.analyze(html_small_targets)
    assert any("touch target" in issue.lower() for issue in result_small.issues + result_small.warnings)

def test_analyze_font_sizes(mobile_friendly_analyzer):
    """Test font size analysis specifically."""
    html_good_fonts = '<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body><p style="font-size:16px;">Text</p></body></html>'
    html_small_fonts = '<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body><p style="font-size:8px;">Text</p></body></html>'
    
    # Test with good font sizes
    result_good = mobile_friendly_analyzer.analyze(html_good_fonts)
    assert not any("font size" in issue.lower() for issue in result_good.issues)
    
    # Test with small font sizes
    result_small = mobile_friendly_analyzer.analyze(html_small_fonts)
    assert any("font size" in issue.lower() for issue in result_small.issues + result_small.warnings)

def test_analyze_responsive_design(mobile_friendly_analyzer):
    """Test responsive design analysis specifically."""
    html_responsive = """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @media (max-width: 768px) {
                body { font-size: 16px; }
            }
        </style>
    </head>
    <body>
        <div class="container">Content</div>
    </body>
    </html>
    """
    html_not_responsive = """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
        <div style="width:1000px;">Content</div>
    </body>
    </html>
    """
    
    # Test with responsive design
    result_responsive = mobile_friendly_analyzer.analyze(html_responsive)
    assert not any("responsive design" in issue.lower() for issue in result_responsive.issues)
    
    # Test without responsive design
    result_not_responsive = mobile_friendly_analyzer.analyze(html_not_responsive)
    assert any("fixed width" in issue.lower() or "wide" in issue.lower() for issue in result_not_responsive.issues + result_not_responsive.warnings)

def test_analyze_mobile_meta(mobile_friendly_analyzer):
    """Test mobile meta tags analysis specifically."""
    html_with_meta = """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="theme-color" content="#4285f4">
        <link rel="apple-touch-icon" href="/icon.png">
        <link rel="manifest" href="/manifest.json">
    </head>
    <body>Content</body>
    </html>
    """
    html_without_meta = """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>Content</body>
    </html>
    """
    
    # Test with mobile meta tags
    result_with_meta = mobile_friendly_analyzer.analyze(html_with_meta)
    assert not any("theme color" in warning.lower() for warning in result_with_meta.warnings)
    assert not any("manifest" in warning.lower() for warning in result_with_meta.warnings)
    
    # Test without mobile meta tags
    result_without_meta = mobile_friendly_analyzer.analyze(html_without_meta)
    assert any("theme color" in warning.lower() or "ios" in warning.lower() or "manifest" in warning.lower() for warning in result_without_meta.warnings)

def test_factory_integration():
    """Test integration with AnalyzerFactory."""
    # Get the registered analyzers
    analyzers = AnalyzerFactory.list_analyzers()
    
    # Check if the mobile analyzer is registered
    assert 'mobile' in analyzers
    
    # Create an instance through the factory
    analyzer = AnalyzerFactory.create('mobile')
    assert isinstance(analyzer, MobileFriendlyAnalyzer)
    
    # Test analyzer functionality
    result = analyzer.analyze(MOBILE_FRIENDLY_HTML)
    assert isinstance(result, AnalysisResult)
    assert 'mobile_score' in result.data 