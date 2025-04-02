import { useState, useMemo } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Recommendation, RecommendationPriority } from "@/types/api";
import { RecommendationCard } from "./recommendation-card";
import { AnimatedContainer } from "@/components/ui/animated-container";
import { Input } from "@/components/ui/input";

interface RecommendationsListProps {
  recommendations: Recommendation[];
  title?: string;
}

type FilterOption = "all" | RecommendationPriority;

export function RecommendationsList({ recommendations, title = "Recommendations" }: RecommendationsListProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterByPriority, setFilterByPriority] = useState<FilterOption>("all");
  
  const filteredRecommendations = useMemo(() => {
    return recommendations.filter(recommendation => {
      // Apply priority filter
      if (filterByPriority !== "all" && recommendation.priority !== filterByPriority) {
        return false;
      }
      
      // Apply search filter
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        return (
          recommendation.title.toLowerCase().includes(searchLower) ||
          recommendation.description.toLowerCase().includes(searchLower) ||
          recommendation.category.toLowerCase().includes(searchLower) ||
          (recommendation.enhanced_description && recommendation.enhanced_description.toLowerCase().includes(searchLower))
        );
      }
      
      return true;
    });
  }, [recommendations, searchTerm, filterByPriority]);

  // Count recommendations by priority
  const priorityCounts = useMemo(() => {
    const counts = {
      [RecommendationPriority.CRITICAL]: 0,
      [RecommendationPriority.HIGH]: 0,
      [RecommendationPriority.MEDIUM]: 0,
      [RecommendationPriority.LOW]: 0,
      total: recommendations.length
    };
    
    recommendations.forEach(recommendation => {
      counts[recommendation.priority]++;
    });
    
    return counts;
  }, [recommendations]);
  
  // Group recommendations by category
  const groupedRecommendations = useMemo(() => {
    const groups: Record<string, Recommendation[]> = {};
    
    filteredRecommendations.forEach(recommendation => {
      const category = recommendation.category;
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push(recommendation);
    });
    
    return groups;
  }, [filteredRecommendations]);
  
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <h2 className="text-xl font-semibold">{title} ({filteredRecommendations.length})</h2>
        
        <div className="w-full md:w-64">
          <Input
            placeholder="Search recommendations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full"
          />
        </div>
      </div>
      
      <div className="flex flex-wrap gap-2">
        <Badge 
          className={`cursor-pointer ${filterByPriority === "all" 
            ? "bg-primary" 
            : "bg-muted hover:bg-muted/80 text-muted-foreground"
          }`}
          onClick={() => setFilterByPriority("all")}
        >
          All ({priorityCounts.total})
        </Badge>
        
        <Badge 
          className={`cursor-pointer ${filterByPriority === RecommendationPriority.CRITICAL 
            ? "bg-red-500" 
            : "bg-red-100 hover:bg-red-200 text-red-700 dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-900/50"
          }`}
          onClick={() => setFilterByPriority(RecommendationPriority.CRITICAL)}
        >
          Critical ({priorityCounts[RecommendationPriority.CRITICAL]})
        </Badge>
        
        <Badge 
          className={`cursor-pointer ${filterByPriority === RecommendationPriority.HIGH 
            ? "bg-orange-500" 
            : "bg-orange-100 hover:bg-orange-200 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400 dark:hover:bg-orange-900/50"
          }`}
          onClick={() => setFilterByPriority(RecommendationPriority.HIGH)}
        >
          High ({priorityCounts[RecommendationPriority.HIGH]})
        </Badge>
        
        <Badge 
          className={`cursor-pointer ${filterByPriority === RecommendationPriority.MEDIUM 
            ? "bg-amber-500" 
            : "bg-amber-100 hover:bg-amber-200 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 dark:hover:bg-amber-900/50"
          }`}
          onClick={() => setFilterByPriority(RecommendationPriority.MEDIUM)}
        >
          Medium ({priorityCounts[RecommendationPriority.MEDIUM]})
        </Badge>
        
        <Badge 
          className={`cursor-pointer ${filterByPriority === RecommendationPriority.LOW 
            ? "bg-blue-500" 
            : "bg-blue-100 hover:bg-blue-200 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 dark:hover:bg-blue-900/50"
          }`}
          onClick={() => setFilterByPriority(RecommendationPriority.LOW)}
        >
          Low ({priorityCounts[RecommendationPriority.LOW]})
        </Badge>
      </div>
      
      {filteredRecommendations.length === 0 ? (
        <Card className="p-6 text-center text-muted-foreground">
          No recommendations match your filters. Try adjusting your search criteria.
        </Card>
      ) : (
        <div className="space-y-6">
          {Object.entries(groupedRecommendations).map(([category, recommendations], groupIndex) => (
            <AnimatedContainer key={category} delay={groupIndex * 0.1}>
              <div className="space-y-3">
                <h3 className="text-lg font-medium">{category} ({recommendations.length})</h3>
                <div className="space-y-2">
                  {recommendations.map((recommendation, index) => (
                    <RecommendationCard 
                      key={recommendation.id} 
                      recommendation={recommendation} 
                      index={index}
                    />
                  ))}
                </div>
              </div>
            </AnimatedContainer>
          ))}
        </div>
      )}
    </div>
  );
} 