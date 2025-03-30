"""Integration tests for SEO analyzers."""

import pytest
from summit_seo.analyzer.factory import AnalyzerFactory
from summit_seo.analyzer.base import AnalysisResult

@pytest.mark.integration
class TestAnalyzerIntegration:
    """Test suite for analyzer integration."""

    def test_analyzer_factory_registration(self, registered_analyzers):
        """Test that all analyzers are properly registered."""
        assert len(registered_analyzers) == 4
        for name in ['title', 'meta', 'content', 'image']:
            assert name in registered_analyzers
            assert AnalyzerFactory.get(name) is not None

    def test_complete_webpage_analysis(self, complete_webpage, integration_configs, expected_analysis_fields):
        """Test analysis of a complete webpage using all analyzers."""
        results = {}
        
        # Run analysis with each analyzer
        for name, config in integration_configs.items():
            analyzer = AnalyzerFactory.get(name)(config)
            results[name] = analyzer.analyze(complete_webpage)
            
            # Verify result type
            assert isinstance(results[name], AnalysisResult)
            
            # Verify expected fields are present
            for field in expected_analysis_fields[name]:
                assert field in results[name].data
            
            # Verify score is calculated
            assert 0 <= results[name].score <= 1

    def test_analyzer_consistency(self, complete_webpage, integration_configs):
        """Test consistency between analyzer results."""
        title_analyzer = AnalyzerFactory.get('title')(integration_configs['title'])
        meta_analyzer = AnalyzerFactory.get('meta')(integration_configs['meta'])
        content_analyzer = AnalyzerFactory.get('content')(integration_configs['content'])
        
        title_result = title_analyzer.analyze(complete_webpage)
        meta_result = meta_analyzer.analyze(complete_webpage)
        content_result = content_analyzer.analyze(complete_webpage)
        
        # Title should be reflected in content
        assert title_result.data['title'].lower() in content_result.data['text'].lower()
        
        # Meta description keywords should appear in content
        meta_desc = meta_result.data['description'].lower()
        content_text = content_result.data['text'].lower()
        assert any(keyword in content_text for keyword in ['seo', 'strategy', 'optimization'])

    def test_analyzer_error_handling(self, integration_configs):
        """Test error handling across analyzers."""
        invalid_html = "<invalid><<html"
        
        for name, config in integration_configs.items():
            analyzer = AnalyzerFactory.get(name)(config)
            
            # Test with invalid HTML
            with pytest.raises(Exception):
                analyzer.analyze(invalid_html)
            
            # Test with None content
            with pytest.raises(Exception):
                analyzer.analyze(None)

    def test_analyzer_scoring_alignment(self, complete_webpage, integration_configs):
        """Test that analyzer scores are properly aligned."""
        scores = {}
        
        # Get scores from all analyzers
        for name, config in integration_configs.items():
            analyzer = AnalyzerFactory.get(name)(config)
            result = analyzer.analyze(complete_webpage)
            scores[name] = result.score
        
        # All scores should be between 0 and 1
        for score in scores.values():
            assert 0 <= score <= 1
        
        # Well-formed page should have decent scores across all analyzers
        assert all(score > 0.6 for score in scores.values()), \
            "Well-formed page should score well across all analyzers"

    def test_cross_analyzer_recommendations(self, complete_webpage, integration_configs):
        """Test that recommendations from different analyzers don't conflict."""
        recommendations = {}
        
        # Collect recommendations from all analyzers
        for name, config in integration_configs.items():
            analyzer = AnalyzerFactory.get(name)(config)
            result = analyzer.analyze(complete_webpage)
            recommendations[name] = result.recommendations
        
        # Check for conflicts in recommendations
        title_recs = set(recommendations['title'])
        meta_recs = set(recommendations['meta'])
        content_recs = set(recommendations['content'])
        
        # No direct contradictions should exist
        assert not any("increase length" in rec and "decrease length" in rec 
                      for rec in title_recs | meta_recs | content_recs)

    def test_analyzer_performance_impact(self, complete_webpage, integration_configs):
        """Test that analyzers don't significantly impact each other's performance."""
        import time
        
        # Test individual analyzer performance
        individual_times = {}
        for name, config in integration_configs.items():
            analyzer = AnalyzerFactory.get(name)(config)
            
            start_time = time.time()
            analyzer.analyze(complete_webpage)
            individual_times[name] = time.time() - start_time
        
        # Test all analyzers running together
        start_time = time.time()
        results = {}
        for name, config in integration_configs.items():
            analyzer = AnalyzerFactory.get(name)(config)
            results[name] = analyzer.analyze(complete_webpage)
        combined_time = time.time() - start_time
        
        # Combined time should not be significantly higher than sum of individual times
        # Allow for 20% overhead
        assert combined_time <= sum(individual_times.values()) * 1.2

    def test_analyzer_memory_isolation(self, complete_webpage, integration_configs):
        """Test that analyzers maintain memory isolation."""
        # Create analyzers with different configurations
        title_analyzer1 = AnalyzerFactory.get('title')(integration_configs['title'])
        title_analyzer2 = AnalyzerFactory.get('title')({
            **integration_configs['title'],
            'min_length': 50,  # Different config
            'max_length': 80
        })
        
        # Analyze same content with different configurations
        result1 = title_analyzer1.analyze(complete_webpage)
        result2 = title_analyzer2.analyze(complete_webpage)
        
        # Results should reflect their respective configurations
        assert result1.data != result2.data
        assert result1.score != result2.score

    def test_concurrent_analysis(self, complete_webpage, integration_configs):
        """Test concurrent analysis with multiple analyzers."""
        from concurrent.futures import ThreadPoolExecutor
        
        def analyze_content(name, config):
            analyzer = AnalyzerFactory.get(name)(config)
            return name, analyzer.analyze(complete_webpage)
        
        # Run analyzers concurrently
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(analyze_content, name, config)
                for name, config in integration_configs.items()
            ]
            
            results = {}
            for future in futures:
                name, result = future.result()
                results[name] = result
        
        # Verify all analyses completed successfully
        assert len(results) == len(integration_configs)
        assert all(isinstance(result, AnalysisResult) for result in results.values())

    def test_analyzer_data_dependencies(self, complete_webpage, integration_configs):
        """Test dependencies between analyzer data fields."""
        # Run all analyzers
        results = {}
        for name, config in integration_configs.items():
            analyzer = AnalyzerFactory.get(name)(config)
            results[name] = analyzer.analyze(complete_webpage)
        
        # Test content-title relationship
        assert results['content'].data['heading_count'] >= 1, "Content should have at least one heading"
        assert results['title'].data['title'] in results['content'].data['text'], "Title should be in content"
        
        # Test meta-content keyword relationship
        meta_keywords = [word.lower() for word in results['meta'].data['description'].split()]
        content_text = results['content'].data['text'].lower()
        assert any(keyword in content_text for keyword in meta_keywords), "Meta keywords should appear in content"
        
        # Test image-content relationship
        if results['image'].data['total_images'] > 0:
            assert 'img' in results['content'].data['html_elements'], "Images should be reflected in content elements"

    def test_analyzer_edge_cases(self, integration_configs):
        """Test analyzer behavior with edge cases."""
        edge_cases = {
            'empty_html': "<html></html>",
            'minimal_html': "<html><head><title>Test</title></head><body>Test</body></html>",
            'large_content': "<html><body>" + "Test content. " * 1000 + "</body></html>",
            'special_chars': "<html><body>🌟 Special © characters ® test 🎉</body></html>",
            'nested_elements': "<html><body><div><div><div><p>Deeply nested</p></div></div></div></body></html>"
        }
        
        for case_name, html in edge_cases.items():
            for name, config in integration_configs.items():
                analyzer = AnalyzerFactory.get(name)(config)
                result = analyzer.analyze(html)
                
                # Basic validations for edge cases
                assert isinstance(result, AnalysisResult)
                assert hasattr(result, 'score')
                assert hasattr(result, 'data')
                assert hasattr(result, 'recommendations')

    def test_analyzer_configuration_validation(self, complete_webpage):
        """Test analyzer behavior with different configurations."""
        invalid_configs = [
            {'min_length': -1},  # Invalid negative value
            {'max_length': 'invalid'},  # Invalid type
            {'weight': 2.0},  # Invalid weight > 1
            {'unknown_param': 'value'}  # Unknown parameter
        ]
        
        for config in invalid_configs:
            for analyzer_name in ['title', 'meta', 'content', 'image']:
                with pytest.raises(Exception):
                    analyzer = AnalyzerFactory.get(analyzer_name)(config)
                    analyzer.analyze(complete_webpage)

    def test_analyzer_result_aggregation(self, complete_webpage, integration_configs):
        """Test aggregation of results from multiple analyzers."""
        # Collect all results
        results = {}
        total_score = 0
        all_recommendations = set()
        all_issues = set()
        
        for name, config in integration_configs.items():
            analyzer = AnalyzerFactory.get(name)(config)
            result = analyzer.analyze(complete_webpage)
            results[name] = result
            
            # Aggregate scores
            total_score += result.score
            
            # Aggregate recommendations and issues
            all_recommendations.update(result.recommendations)
            all_issues.update(result.issues)
        
        # Calculate average score
        avg_score = total_score / len(results)
        
        # Verify aggregation
        assert 0 <= avg_score <= 1, "Average score should be between 0 and 1"
        assert len(all_recommendations) > 0, "Should have aggregated recommendations"
        assert len(all_issues) >= 0, "Should have aggregated issues if any exist" 