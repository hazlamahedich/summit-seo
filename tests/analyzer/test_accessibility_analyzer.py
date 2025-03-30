"""Tests for the AccessibilityAnalyzer class."""

import pytest
from typing import Dict, Any
from bs4 import BeautifulSoup
from summit_seo.analyzer.accessibility_analyzer import AccessibilityAnalyzer
from summit_seo.analyzer.base import AnalysisResult

# Sample HTML with good accessibility
ACCESSIBLE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accessible Page Example</title>
</head>
<body>
    <a href="#main" class="skip-link">Skip to main content</a>
    <header>
        <nav aria-label="Main Navigation">
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/about">About</a></li>
                <li><a href="/contact">Contact</a></li>
            </ul>
        </nav>
    </header>
    <main id="main">
        <h1>Welcome to Our Accessible Website</h1>
        <section>
            <h2>About Us</h2>
            <p>This is an example of an accessible website with proper semantic structure.</p>
            <figure>
                <img src="example.jpg" alt="A person using a computer with assistive technology">
                <figcaption>A person using assistive technology to browse the web</figcaption>
            </figure>
        </section>
        <section>
            <h2>Contact Form</h2>
            <form>
                <div>
                    <label for="name">Name:</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div>
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div>
                    <label for="message">Message:</label>
                    <textarea id="message" name="message" rows="4"></textarea>
                </div>
                <button type="submit">Send Message</button>
            </form>
        </section>
    </main>
    <footer>
        <p>&copy; 2025 Accessible Example Company</p>
    </footer>
</body>
</html>
"""

# Sample HTML with accessibility issues
INACCESSIBLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <div class="header">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
        </div>
    </div>
    <div class="content">
        <div class="welcome">Welcome to Our Website</div>
        <div class="about">
            About Us
            <p>This is a website with accessibility issues.</p>
            <img src="example.jpg">
        </div>
        <div class="contact">
            Contact Form
            <form>
                <div>
                    Name:
                    <input type="text" name="name" required>
                </div>
                <div>
                    Email:
                    <input type="email" name="email" required>
                </div>
                <div>
                    Message:
                    <textarea name="message" rows="4"></textarea>
                </div>
                <div onclick="submitForm()" style="color: #fff; background-color: #007bff;" tabindex="5">Submit</div>
            </form>
        </div>
    </div>
    <div class="footer">
        &copy; 2025 Example Company
    </div>
    <script>
        function submitForm() {
            alert('Form submitted!');
        }
    </script>
</body>
</html>
"""

@pytest.fixture
def accessibility_analyzer():
    """Create an accessibility analyzer instance."""
    return AccessibilityAnalyzer()

def test_analyze_accessible_page(accessibility_analyzer):
    """Test analyzing a page with good accessibility."""
    result = accessibility_analyzer.analyze(ACCESSIBLE_HTML)
    
    assert isinstance(result, AnalysisResult)
    assert result.score >= 0.7  # Good score for accessible page (minor issues ok)
    assert result.data['accessibility_score'] >= 70
    
    # Check for presence of language attribute warning
    assert not any("language attribute" in issue for issue in result.issues)
    
    # Check that common accessibility issues aren't present
    assert not any("alt attributes" in issue for issue in result.issues)
    assert not any("heading" in issue for issue in result.issues)
    
    # Verify document has proper structure
    assert not any("missing main" in warning.lower() for warning in result.warnings)
    assert not any("missing navigation" in warning.lower() for warning in result.warnings)
    assert not any("missing header" in warning.lower() for warning in result.warnings)
    assert not any("missing footer" in warning.lower() for warning in result.warnings)

def test_analyze_inaccessible_page(accessibility_analyzer):
    """Test analyzing a page with accessibility issues."""
    result = accessibility_analyzer.analyze(INACCESSIBLE_HTML)
    
    assert isinstance(result, AnalysisResult)
    assert result.score < 0.5  # Lower score for inaccessible page
    assert result.data['accessibility_score'] < 50
    assert result.data['has_accessibility_issues'] is True
    
    # Check for expected accessibility issues
    assert any("language attribute" in issue for issue in result.issues)
    assert any("main element" in warning.lower() for warning in result.warnings)
    assert any("navigation" in warning.lower() for warning in result.warnings)
    assert any("title" in issue.lower() for issue in result.issues)
    
    # Check for specific issue detection
    assert result.data['critical_severity_issues'] + result.data['high_severity_issues'] > 0
    assert len(result.issues) > 0
    assert len(result.recommendations) > 0
    
    # Verify some specific issues
    assert any("language attribute" in issue for issue in result.issues)
    assert any("alt attributes" in issue for issue in result.issues)
    assert any("form controls without labels" in issue for issue in result.issues)

def test_analyze_language(accessibility_analyzer):
    """Test language analysis specifically."""
    html_with_lang = '<html lang="en"><body>Content</body></html>'
    html_without_lang = '<html><body>Content</body></html>'
    
    # Test with language attribute
    result_with_lang = accessibility_analyzer.analyze(html_with_lang)
    assert not any("language attribute" in issue for issue in result_with_lang.issues)
    
    # Test without language attribute
    result_without_lang = accessibility_analyzer.analyze(html_without_lang)
    assert any("language attribute" in issue for issue in result_without_lang.issues)

def test_analyze_alt_text(accessibility_analyzer):
    """Test alt text analysis specifically."""
    html_with_alt = '<html lang="en"><body><img src="image.jpg" alt="Description"></body></html>'
    html_without_alt = '<html lang="en"><body><img src="image.jpg"></body></html>'
    
    # Test with alt text
    result_with_alt = accessibility_analyzer.analyze(html_with_alt)
    assert not any("without alt" in issue for issue in result_with_alt.issues)
    
    # Test without alt text
    result_without_alt = accessibility_analyzer.analyze(html_without_alt)
    assert any("without alt" in issue for issue in result_without_alt.issues)

def test_analyze_heading_structure(accessibility_analyzer):
    """Test heading structure analysis specifically."""
    html_good_headings = '<html lang="en"><body><h1>Title</h1><h2>Subtitle</h2></body></html>'
    html_skipped_headings = '<html lang="en"><body><h1>Title</h1><h3>Subtitle</h3></body></html>'
    html_no_h1 = '<html lang="en"><body><h2>Subtitle</h2></body></html>'
    
    # Test with good heading structure
    result_good = accessibility_analyzer.analyze(html_good_headings)
    assert not any("heading level" in issue for issue in result_good.issues)
    
    # Test with skipped heading level
    result_skipped = accessibility_analyzer.analyze(html_skipped_headings)
    assert any("heading level" in issue for issue in result_skipped.issues)
    
    # Test with no H1
    result_no_h1 = accessibility_analyzer.analyze(html_no_h1)
    assert any("H1 heading" in issue for issue in result_no_h1.issues)

def test_analyze_form_labels(accessibility_analyzer):
    """Test form label analysis specifically."""
    html_labeled_form = """
    <html lang="en"><body>
        <form>
            <label for="name">Name:</label>
            <input type="text" id="name">
        </form>
    </body></html>
    """
    html_unlabeled_form = """
    <html lang="en"><body>
        <form>
            <span>Name:</span>
            <input type="text" name="name">
        </form>
    </body></html>
    """
    
    # Test with labeled form
    result_labeled = accessibility_analyzer.analyze(html_labeled_form)
    assert not any("without labels" in issue.lower() for issue in result_labeled.issues)
    
    # Test with unlabeled form
    result_unlabeled = accessibility_analyzer.analyze(html_unlabeled_form)
    assert any("without labels" in issue.lower() for issue in result_unlabeled.issues)

def test_analyze_document_structure(accessibility_analyzer):
    """Test document structure analysis specifically."""
    html_semantic = """
    <html lang="en"><body>
        <header><nav>Navigation</nav></header>
        <main><h1>Title</h1></main>
        <footer>Footer</footer>
    </body></html>
    """
    html_non_semantic = """
    <html lang="en"><body>
        <div class="header">Header</div>
        <div class="content">Content</div>
        <div class="footer">Footer</div>
    </body></html>
    """
    
    # Test with semantic structure
    result_semantic = accessibility_analyzer.analyze(html_semantic)
    # Check for main element directly in warnings/issues
    assert not any("main element" in warning.lower() for warning in result_semantic.warnings)
    
    # Test with non-semantic structure
    result_non_semantic = accessibility_analyzer.analyze(html_non_semantic)
    # Check for missing main element warning
    assert any("main element" in warning.lower() for warning in result_non_semantic.warnings)

def test_factory_integration():
    """Test integration with the analyzer factory."""
    from summit_seo.analyzer.factory import AnalyzerFactory
    
    analyzer = AnalyzerFactory.create('accessibility')
    assert isinstance(analyzer, AccessibilityAnalyzer)
    
    result = analyzer.analyze(ACCESSIBLE_HTML)
    assert isinstance(result, AnalysisResult)
    assert isinstance(result.data, dict)
    assert 'accessibility_score' in result.data 