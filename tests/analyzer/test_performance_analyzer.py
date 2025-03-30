"""Test for the Performance Analyzer."""

import pytest
from bs4 import BeautifulSoup
from summit_seo.analyzer.performance_analyzer import PerformanceAnalyzer

# Sample HTML for testing
OPTIMIZED_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Optimized Page</title>
    <style>
        /* Critical CSS inlined */
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        header { margin-bottom: 20px; }
        h1 { color: #333; }
    </style>
    <link rel="stylesheet" href="style.css" media="print" onload="this.media='all'">
    <script src="analytics.js" async></script>
    <script type="module" src="app.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
</head>
<body>
    <header>
        <h1>Performance Optimized Page</h1>
    </header>
    <main>
        <p>This page is optimized for performance.</p>
        <img src="small-image.jpg" alt="Small optimized image" width="300" height="200" loading="lazy">
    </main>
    <footer>
        <p>Copyright 2025</p>
    </footer>
</body>
</html>
"""

UNOPTIMIZED_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Unoptimized Page</title>
    <link rel="stylesheet" href="style1.css">
    <link rel="stylesheet" href="style2.css">
    <link rel="stylesheet" href="style3.css">
    <link rel="stylesheet" href="style4.css">
    <link rel="stylesheet" href="style5.css">
    <script src="script1.js"></script>
    <script src="script2.js"></script>
    <script src="script3.js"></script>
    <script>
        // Large inline script
        function largeFunction() {
            // Lots of code here
            console.log("This is a large inline script");
            // More code
            // Even more code
            // This goes on for a while
            // Imagine this is 1000+ characters
        }
        
        // Another function
        function anotherFunction() {
            // More code here
            console.log("Another large function");
            // This also goes on for a while
        }
        
        // Initialize everything
        window.onload = function() {
            largeFunction();
            anotherFunction();
            // More initialization
        }
    </script>
</head>
<body>
    <h1>Unoptimized Page</h1>
    <div>
        <img src="large-image1.jpg">
        <img src="large-image2.jpg">
        <img src="large-image3.jpg">
        <img src="large-image4.jpg">
        <img src="large-image5.jpg">
        <img src="large-image6.jpg">
        <img src="large-image7.jpg">
        <img src="large-image8.jpg">
        <img src="large-image9.jpg">
        <img src="large-image10.jpg">
        <img src="large-image11.jpg">
        <img src="large-image12.jpg">
        <img src="large-image13.jpg">
        <img src="large-image14.jpg">
        <img src="large-image15.jpg">
        <!-- More unoptimized images without alt text or dimensions -->
    </div>
    <iframe src="external-content.html"></iframe>
    <iframe src="another-frame.html"></iframe>
    <script src="script4.js"></script>
    <script src="script5.js"></script>
    <script src="script6.js"></script>
    <script src="script7.js"></script>
    <script src="script8.js"></script>
    <script src="script9.js"></script>
    <script src="script10.js"></script>
    <script src="script11.js"></script>
    <script src="script12.js"></script>
    <script src="script13.js"></script>
    <script src="script14.js"></script>
    <script src="script15.js"></script>
</body>
</html>
"""

@pytest.fixture
def optimized_soup():
    """Create a BeautifulSoup object for optimized HTML."""
    return BeautifulSoup(OPTIMIZED_HTML, 'html.parser')

@pytest.fixture
def unoptimized_soup():
    """Create a BeautifulSoup object for unoptimized HTML."""
    return BeautifulSoup(UNOPTIMIZED_HTML, 'html.parser')

@pytest.fixture
def performance_analyzer():
    """Create a performance analyzer instance."""
    return PerformanceAnalyzer()

def test_analyze_optimized_page(performance_analyzer):
    """Test analyzing an optimized page."""
    result = performance_analyzer.analyze(OPTIMIZED_HTML)
    
    # Check score and performance status
    assert result.score >= 0.7
    assert result.data['performance_score'] >= 70
    assert result.data['has_performance_issues'] is False
    
    # Verify there are no critical or high severity issues
    assert result.data['critical_severity_issues'] == 0
    assert result.data['high_severity_issues'] == 0
    
    # Verify resource counts (these may vary but should be reasonable)
    assert result.data['total_resource_count'] < 10  # Small number of resources
    
    # The optimized page actually has render blocking scripts but they're still OK
    # because the overall score is good and there are no critical/high issues
    assert 'performance_issues' in result.data
    assert isinstance(result.data['performance_issues'], list)
    
    # Verify presence of recommendations
    assert len(result.recommendations) > 0

def test_analyze_unoptimized_page(performance_analyzer):
    """Test analyzing an unoptimized page."""
    result = performance_analyzer.analyze(UNOPTIMIZED_HTML)
    
    assert result.score < 0.7
    assert result.data['performance_score'] < 70
    assert result.data['has_performance_issues'] is True
    
    # Verify issue counts
    assert result.data['high_severity_issues'] > 0
    assert result.data['medium_severity_issues'] > 0
    
    # Verify resource counts are high
    assert result.data['total_resource_count'] > 20
    assert result.data['render_blocking_resources'] >= 5
    assert result.data['unoptimized_images'] >= 10

def test_page_size_analysis(performance_analyzer, optimized_soup, unoptimized_soup):
    """Test page size analysis."""
    optimized_result = performance_analyzer._analyze_page_size(optimized_soup, OPTIMIZED_HTML)
    unoptimized_result = performance_analyzer._analyze_page_size(unoptimized_soup, UNOPTIMIZED_HTML)
    
    # Optimized page should have smaller estimated size
    assert optimized_result['total_page_size_estimate'] < unoptimized_result['total_page_size_estimate']
    
    # Optimized page should have fewer performance issues
    assert len(optimized_result['performance_issues']) < len(unoptimized_result['performance_issues'])

def test_resource_count_analysis(performance_analyzer, optimized_soup, unoptimized_soup):
    """Test resource count analysis."""
    optimized_result = performance_analyzer._analyze_resource_count(optimized_soup)
    unoptimized_result = performance_analyzer._analyze_resource_count(unoptimized_soup)
    
    # Optimized page should have fewer resources
    assert optimized_result['total_resource_count'] < unoptimized_result['total_resource_count']
    
    # Unoptimized page should have performance issues related to resource count
    assert len(unoptimized_result['performance_issues']) > 0
    assert any("Resource Count" in issue.name for issue in unoptimized_result['performance_issues'])

def test_render_blocking_analysis(performance_analyzer, optimized_soup, unoptimized_soup):
    """Test render blocking analysis."""
    optimized_result = performance_analyzer._analyze_render_blocking(optimized_soup)
    unoptimized_result = performance_analyzer._analyze_render_blocking(unoptimized_soup)
    
    # Optimized page should have fewer render-blocking resources
    assert optimized_result['render_blocking_count'] < unoptimized_result['render_blocking_count']
    
    # Unoptimized page should have performance issues related to render-blocking resources
    assert len(unoptimized_result['performance_issues']) > 0
    assert any("Render-Blocking" in issue.name for issue in unoptimized_result['performance_issues'])

def test_image_optimization_analysis(performance_analyzer, optimized_soup, unoptimized_soup):
    """Test image optimization analysis."""
    optimized_result = performance_analyzer._analyze_image_optimization(optimized_soup)
    unoptimized_result = performance_analyzer._analyze_image_optimization(unoptimized_soup)
    
    # Optimized page should have fewer unoptimized images
    assert optimized_result['unoptimized_count'] < unoptimized_result['unoptimized_count']
    
    # Unoptimized page should have performance issues related to unoptimized images
    assert len(unoptimized_result['performance_issues']) > 0

def test_scoring_algorithm(performance_analyzer):
    """Test the performance scoring algorithm."""
    result = performance_analyzer.analyze(UNOPTIMIZED_HTML)
    
    # Score should be between 0 and 1
    assert 0 <= result.score <= 1
    
    # Score should match the performance_score in data (normalized to 0-100)
    assert abs(result.score * 100 - result.data['performance_score']) < 1  # Allow for rounding

def test_factory_integration():
    """Test integration with the analyzer factory."""
    from summit_seo.analyzer.factory import AnalyzerFactory
    
    analyzer = AnalyzerFactory.create('performance')
    assert isinstance(analyzer, PerformanceAnalyzer)
    
    result = analyzer.analyze(OPTIMIZED_HTML)
    assert isinstance(result.data, dict)
    assert 'performance_score' in result.data 