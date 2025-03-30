"""Test cases for the recommendation module."""

import pytest
from summit_seo.analyzer.recommendation import (
    Recommendation,
    RecommendationBuilder,
    RecommendationManager,
    RecommendationSeverity,
    RecommendationPriority
)


class TestRecommendation:
    """Test cases for the Recommendation class."""
    
    def test_recommendation_init(self):
        """Test initializing a recommendation."""
        rec = Recommendation(
            title="Test Recommendation",
            description="This is a test recommendation"
        )
        
        assert rec.title == "Test Recommendation"
        assert rec.description == "This is a test recommendation"
        assert rec.severity == RecommendationSeverity.MEDIUM
        assert rec.priority == RecommendationPriority.P2
        assert rec.code_example is None
        assert rec.steps == []
        assert rec.quick_win is False
        assert rec.impact is None
        assert rec.difficulty == "medium"
        assert rec.resource_links == []
    
    def test_recommendation_to_dict(self):
        """Test converting a recommendation to a dictionary."""
        rec = Recommendation(
            title="Test Recommendation",
            description="This is a test recommendation",
            severity=RecommendationSeverity.HIGH,
            priority=RecommendationPriority.P1
        )
        
        rec_dict = rec.to_dict()
        
        assert rec_dict["title"] == "Test Recommendation"
        assert rec_dict["description"] == "This is a test recommendation"
        assert rec_dict["severity"] == "high"
        assert rec_dict["priority"] == 1
    
    def test_recommendation_from_string(self):
        """Test creating a recommendation from a string."""
        rec = Recommendation.from_string("Simple recommendation")
        
        assert rec.title == "Simple recommendation"
        assert rec.description == "Simple recommendation"


class TestRecommendationBuilder:
    """Test cases for the RecommendationBuilder class."""
    
    def test_builder_init(self):
        """Test initializing a recommendation builder."""
        builder = RecommendationBuilder("Test Recommendation")
        
        assert builder.recommendation.title == "Test Recommendation"
        assert builder.recommendation.description == "Test Recommendation"
    
    def test_builder_with_description(self):
        """Test initializing a builder with a separate description."""
        builder = RecommendationBuilder(
            "Test Recommendation",
            "This is a test recommendation"
        )
        
        assert builder.recommendation.title == "Test Recommendation"
        assert builder.recommendation.description == "This is a test recommendation"
    
    def test_builder_with_severity(self):
        """Test setting severity with the builder."""
        # Test with enum value
        builder1 = RecommendationBuilder("Test").with_severity(RecommendationSeverity.HIGH)
        assert builder1.recommendation.severity == RecommendationSeverity.HIGH
        
        # Test with string value
        builder2 = RecommendationBuilder("Test").with_severity("critical")
        assert builder2.recommendation.severity == RecommendationSeverity.CRITICAL
        
        # Test with invalid string (should default to MEDIUM)
        builder3 = RecommendationBuilder("Test").with_severity("invalid")
        assert builder3.recommendation.severity == RecommendationSeverity.MEDIUM
    
    def test_builder_with_priority(self):
        """Test setting priority with the builder."""
        # Test with enum value
        builder1 = RecommendationBuilder("Test").with_priority(RecommendationPriority.P0)
        assert builder1.recommendation.priority == RecommendationPriority.P0
        
        # Test with integer value
        builder2 = RecommendationBuilder("Test").with_priority(1)
        assert builder2.recommendation.priority == RecommendationPriority.P1
        
        # Test with invalid integer (should default to P2)
        builder3 = RecommendationBuilder("Test").with_priority(99)
        assert builder3.recommendation.priority == RecommendationPriority.P2
    
    def test_builder_with_code_example(self):
        """Test adding a code example with the builder."""
        code = "function test() {\n  return 'example';\n}"
        builder = RecommendationBuilder("Test").with_code_example(code)
        
        assert builder.recommendation.code_example == code
    
    def test_builder_with_steps(self):
        """Test adding steps with the builder."""
        steps = ["Step 1", "Step 2", "Step 3"]
        builder = RecommendationBuilder("Test").with_steps(steps)
        
        assert builder.recommendation.steps == steps
    
    def test_builder_mark_as_quick_win(self):
        """Test marking as quick win with the builder."""
        builder1 = RecommendationBuilder("Test").mark_as_quick_win()
        assert builder1.recommendation.quick_win is True
        
        builder2 = RecommendationBuilder("Test").mark_as_quick_win(False)
        assert builder2.recommendation.quick_win is False
    
    def test_builder_with_impact(self):
        """Test adding impact with the builder."""
        impact = "This will improve security significantly"
        builder = RecommendationBuilder("Test").with_impact(impact)
        
        assert builder.recommendation.impact == impact
    
    def test_builder_with_difficulty(self):
        """Test setting difficulty with the builder."""
        builder1 = RecommendationBuilder("Test").with_difficulty("easy")
        assert builder1.recommendation.difficulty == "easy"
        
        builder2 = RecommendationBuilder("Test").with_difficulty("hard")
        assert builder2.recommendation.difficulty == "hard"
        
        # Test with invalid difficulty (should default to medium)
        builder3 = RecommendationBuilder("Test").with_difficulty("super-hard")
        assert builder3.recommendation.difficulty == "medium"
    
    def test_builder_with_resource_link(self):
        """Test adding a resource link with the builder."""
        builder = RecommendationBuilder("Test").with_resource_link(
            "Example Resource",
            "https://example.com"
        )
        
        assert len(builder.recommendation.resource_links) == 1
        assert builder.recommendation.resource_links[0]["title"] == "Example Resource"
        assert builder.recommendation.resource_links[0]["url"] == "https://example.com"
    
    def test_builder_build(self):
        """Test building a complete recommendation."""
        builder = (RecommendationBuilder("Test Recommendation")
                  .with_severity(RecommendationSeverity.HIGH)
                  .with_priority(RecommendationPriority.P1)
                  .with_code_example("console.log('test');")
                  .with_steps(["Step 1", "Step 2"])
                  .mark_as_quick_win()
                  .with_impact("High impact")
                  .with_difficulty("easy")
                  .with_resource_link("Resource", "https://example.com"))
        
        rec = builder.build()
        
        assert rec.title == "Test Recommendation"
        assert rec.severity == RecommendationSeverity.HIGH
        assert rec.priority == RecommendationPriority.P1
        assert rec.code_example == "console.log('test');"
        assert rec.steps == ["Step 1", "Step 2"]
        assert rec.quick_win is True
        assert rec.impact == "High impact"
        assert rec.difficulty == "easy"
        assert len(rec.resource_links) == 1


class TestRecommendationManager:
    """Test cases for the RecommendationManager class."""
    
    def test_manager_init(self):
        """Test initializing a recommendation manager."""
        manager = RecommendationManager()
        
        assert manager.recommendations == []
    
    def test_manager_add(self):
        """Test adding a recommendation to the manager."""
        manager = RecommendationManager()
        rec = Recommendation(
            title="Test Recommendation",
            description="This is a test recommendation"
        )
        
        manager.add(rec)
        
        assert len(manager.recommendations) == 1
        assert manager.recommendations[0].title == "Test Recommendation"
    
    def test_manager_add_from_string(self):
        """Test adding a recommendation from a string."""
        manager = RecommendationManager()
        
        manager.add_from_string("Simple recommendation")
        
        assert len(manager.recommendations) == 1
        assert manager.recommendations[0].title == "Simple recommendation"
    
    def test_manager_get_priority_ordered(self):
        """Test getting recommendations ordered by priority."""
        manager = RecommendationManager()
        
        # Add recommendations with different priorities
        rec1 = RecommendationBuilder("Rec 1").with_priority(RecommendationPriority.P2).build()
        rec2 = RecommendationBuilder("Rec 2").with_priority(RecommendationPriority.P0).build()
        rec3 = RecommendationBuilder("Rec 3").with_priority(RecommendationPriority.P3).build()
        
        manager.add(rec1)
        manager.add(rec2)
        manager.add(rec3)
        
        # Get priority ordered recommendations
        ordered = manager.get_priority_ordered()
        
        # Should be ordered by priority (P0, P2, P3)
        assert ordered[0].title == "Rec 2"  # P0
        assert ordered[1].title == "Rec 1"  # P2
        assert ordered[2].title == "Rec 3"  # P3
    
    def test_manager_get_severity_ordered(self):
        """Test getting recommendations ordered by severity."""
        manager = RecommendationManager()
        
        # Add recommendations with different severities
        rec1 = RecommendationBuilder("Rec 1").with_severity(RecommendationSeverity.MEDIUM).build()
        rec2 = RecommendationBuilder("Rec 2").with_severity(RecommendationSeverity.CRITICAL).build()
        rec3 = RecommendationBuilder("Rec 3").with_severity(RecommendationSeverity.LOW).build()
        
        manager.add(rec1)
        manager.add(rec2)
        manager.add(rec3)
        
        # Get severity ordered recommendations
        ordered = manager.get_severity_ordered()
        
        # Should be ordered by severity (CRITICAL, MEDIUM, LOW)
        assert ordered[0].title == "Rec 2"  # CRITICAL
        assert ordered[1].title == "Rec 1"  # MEDIUM
        assert ordered[2].title == "Rec 3"  # LOW
    
    def test_manager_get_quick_wins(self):
        """Test getting quick win recommendations."""
        manager = RecommendationManager()
        
        # Add a mix of quick win and regular recommendations
        rec1 = RecommendationBuilder("Rec 1").mark_as_quick_win(True).build()
        rec2 = RecommendationBuilder("Rec 2").build()
        rec3 = RecommendationBuilder("Rec 3").mark_as_quick_win(True).build()
        
        manager.add(rec1)
        manager.add(rec2)
        manager.add(rec3)
        
        # Get quick wins
        quick_wins = manager.get_quick_wins()
        
        # Should only include quick wins
        assert len(quick_wins) == 2
        assert quick_wins[0].title == "Rec 1"
        assert quick_wins[1].title == "Rec 3"
    
    def test_manager_get_by_difficulty(self):
        """Test getting recommendations by difficulty level."""
        manager = RecommendationManager()
        
        # Add recommendations with different difficulty levels
        rec1 = RecommendationBuilder("Rec 1").with_difficulty("easy").build()
        rec2 = RecommendationBuilder("Rec 2").with_difficulty("medium").build()
        rec3 = RecommendationBuilder("Rec 3").with_difficulty("hard").build()
        rec4 = RecommendationBuilder("Rec 4").with_difficulty("easy").build()
        
        manager.add(rec1)
        manager.add(rec2)
        manager.add(rec3)
        manager.add(rec4)
        
        # Get recommendations by difficulty
        easy_recs = manager.get_by_difficulty("easy")
        medium_recs = manager.get_by_difficulty("medium")
        hard_recs = manager.get_by_difficulty("hard")
        
        # Check counts
        assert len(easy_recs) == 2
        assert len(medium_recs) == 1
        assert len(hard_recs) == 1
        
        # Check specific recommendations
        assert "Rec 1" in [r.title for r in easy_recs]
        assert "Rec 4" in [r.title for r in easy_recs]
        assert medium_recs[0].title == "Rec 2"
        assert hard_recs[0].title == "Rec 3"
    
    def test_manager_to_list(self):
        """Test converting all recommendations to a list of dictionaries."""
        manager = RecommendationManager()
        
        # Add some recommendations
        rec1 = RecommendationBuilder("Rec 1").with_severity(RecommendationSeverity.HIGH).build()
        rec2 = RecommendationBuilder("Rec 2").with_priority(RecommendationPriority.P1).build()
        
        manager.add(rec1)
        manager.add(rec2)
        
        # Convert to list of dictionaries
        rec_list = manager.to_list()
        
        # Check the result
        assert len(rec_list) == 2
        assert rec_list[0]["title"] == "Rec 1"
        assert rec_list[0]["severity"] == "high"
        assert rec_list[1]["title"] == "Rec 2"
        assert rec_list[1]["priority"] == 1 