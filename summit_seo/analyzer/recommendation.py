"""Enhanced recommendation module for SEO analysis."""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union


class RecommendationSeverity(Enum):
    """Severity levels for recommendations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RecommendationPriority(Enum):
    """Priority levels for recommendations."""
    P0 = 0  # Must fix immediately
    P1 = 1  # High priority
    P2 = 2  # Medium priority
    P3 = 3  # Low priority
    P4 = 4  # Nice to have


@dataclass
class Recommendation:
    """Enhanced recommendation with severity, priority, and code examples."""
    # Basic recommendation information
    title: str
    description: str
    
    # Classification attributes
    severity: RecommendationSeverity = RecommendationSeverity.MEDIUM
    priority: RecommendationPriority = RecommendationPriority.P2
    
    # Implementation guidance
    code_example: Optional[str] = None
    steps: List[str] = field(default_factory=list)
    quick_win: bool = False
    
    # Impact assessment
    impact: Optional[str] = None
    difficulty: Optional[str] = "medium"  # easy, medium, hard
    
    # Additional information
    resource_links: List[Dict[str, str]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the recommendation to a dictionary.
        
        Returns:
            Dictionary representation of the recommendation
        """
        return {
            'title': self.title,
            'description': self.description,
            'severity': self.severity.value,
            'priority': self.priority.value,
            'code_example': self.code_example,
            'steps': self.steps,
            'quick_win': self.quick_win,
            'impact': self.impact,
            'difficulty': self.difficulty,
            'resource_links': self.resource_links
        }
    
    @classmethod
    def from_string(cls, recommendation_str: str) -> 'Recommendation':
        """Create a basic recommendation object from a string.
        
        Args:
            recommendation_str: Simple recommendation string
            
        Returns:
            Recommendation object with basic attributes
        """
        return cls(
            title=recommendation_str,
            description=recommendation_str
        )


class RecommendationBuilder:
    """Builder for creating recommendations with fluent API."""
    
    def __init__(self, title: str, description: Optional[str] = None):
        """Initialize the recommendation builder.
        
        Args:
            title: Title of the recommendation
            description: Optional description (defaults to title if not provided)
        """
        self.recommendation = Recommendation(
            title=title,
            description=description or title
        )
    
    def with_severity(self, severity: Union[RecommendationSeverity, str]) -> 'RecommendationBuilder':
        """Set the severity of the recommendation.
        
        Args:
            severity: Severity level (can be enum value or string)
            
        Returns:
            Self for method chaining
        """
        if isinstance(severity, str):
            try:
                severity = RecommendationSeverity(severity)
            except ValueError:
                # Default to MEDIUM if invalid string provided
                severity = RecommendationSeverity.MEDIUM
        
        self.recommendation.severity = severity
        return self
    
    def with_priority(self, priority: Union[RecommendationPriority, int]) -> 'RecommendationBuilder':
        """Set the priority of the recommendation.
        
        Args:
            priority: Priority level (can be enum value or integer 0-4)
            
        Returns:
            Self for method chaining
        """
        if isinstance(priority, int):
            try:
                priority = RecommendationPriority(priority)
            except ValueError:
                # Default to P2 if invalid integer provided
                priority = RecommendationPriority.P2
        
        self.recommendation.priority = priority
        return self
    
    def with_code_example(self, code: str) -> 'RecommendationBuilder':
        """Add a code example to the recommendation.
        
        Args:
            code: Example code that implements the recommendation
            
        Returns:
            Self for method chaining
        """
        self.recommendation.code_example = code
        return self
    
    def with_steps(self, steps: List[str]) -> 'RecommendationBuilder':
        """Add implementation steps to the recommendation.
        
        Args:
            steps: List of steps to implement the recommendation
            
        Returns:
            Self for method chaining
        """
        self.recommendation.steps = steps
        return self
    
    def mark_as_quick_win(self, is_quick_win: bool = True) -> 'RecommendationBuilder':
        """Mark the recommendation as a quick win.
        
        Args:
            is_quick_win: Whether this is a quick win recommendation
            
        Returns:
            Self for method chaining
        """
        self.recommendation.quick_win = is_quick_win
        return self
    
    def with_impact(self, impact: str) -> 'RecommendationBuilder':
        """Add impact assessment to the recommendation.
        
        Args:
            impact: Description of the impact of implementing this recommendation
            
        Returns:
            Self for method chaining
        """
        self.recommendation.impact = impact
        return self
    
    def with_difficulty(self, difficulty: str) -> 'RecommendationBuilder':
        """Set the implementation difficulty of the recommendation.
        
        Args:
            difficulty: Difficulty level (easy, medium, hard)
            
        Returns:
            Self for method chaining
        """
        if difficulty not in ('easy', 'medium', 'hard'):
            difficulty = 'medium'
        
        self.recommendation.difficulty = difficulty
        return self
    
    def with_resource_link(self, title: str, url: str) -> 'RecommendationBuilder':
        """Add a resource link to the recommendation.
        
        Args:
            title: Title of the resource
            url: URL of the resource
            
        Returns:
            Self for method chaining
        """
        self.recommendation.resource_links.append({
            'title': title,
            'url': url
        })
        return self
    
    def build(self) -> Recommendation:
        """Build and return the recommendation.
        
        Returns:
            Built recommendation object
        """
        return self.recommendation


class RecommendationManager:
    """Manager for organizing and prioritizing recommendations."""
    
    def __init__(self):
        """Initialize the recommendation manager."""
        self.recommendations: List[Recommendation] = []
    
    def add(self, recommendation: Recommendation) -> None:
        """Add a recommendation to the manager.
        
        Args:
            recommendation: Recommendation to add
        """
        self.recommendations.append(recommendation)
    
    def add_from_string(self, recommendation_str: str) -> None:
        """Add a recommendation from a simple string.
        
        Args:
            recommendation_str: Simple recommendation string
        """
        self.recommendations.append(Recommendation.from_string(recommendation_str))
    
    def get_priority_ordered(self) -> List[Recommendation]:
        """Get recommendations sorted by priority.
        
        Returns:
            List of recommendations ordered by priority
        """
        return sorted(self.recommendations, key=lambda r: r.priority.value)
    
    def get_severity_ordered(self) -> List[Recommendation]:
        """Get recommendations sorted by severity.
        
        Returns:
            List of recommendations ordered by severity
        """
        # Order: CRITICAL, HIGH, MEDIUM, LOW, INFO
        severity_order = {
            RecommendationSeverity.CRITICAL: 0,
            RecommendationSeverity.HIGH: 1,
            RecommendationSeverity.MEDIUM: 2,
            RecommendationSeverity.LOW: 3,
            RecommendationSeverity.INFO: 4
        }
        return sorted(self.recommendations, key=lambda r: severity_order[r.severity])
    
    def get_quick_wins(self) -> List[Recommendation]:
        """Get all quick win recommendations.
        
        Returns:
            List of quick win recommendations
        """
        return [r for r in self.recommendations if r.quick_win]
    
    def get_by_difficulty(self, difficulty: str) -> List[Recommendation]:
        """Get recommendations by difficulty level.
        
        Args:
            difficulty: Difficulty level to filter by (easy, medium, hard)
            
        Returns:
            List of recommendations with the specified difficulty
        """
        return [r for r in self.recommendations if r.difficulty == difficulty]
    
    def to_list(self) -> List[Dict[str, Any]]:
        """Convert all recommendations to a list of dictionaries.
        
        Returns:
            List of recommendation dictionaries
        """
        return [r.to_dict() for r in self.recommendations] 