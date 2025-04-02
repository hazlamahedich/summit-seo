import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { RecommendationPriority, Recommendation } from "@/types/api";
import { AnimatedContainer } from "@/components/ui/animated-container";
import { motion } from "framer-motion";

interface RecommendationCardProps {
  recommendation: Recommendation;
  index: number;
}

const priorityColors = {
  [RecommendationPriority.CRITICAL]: {
    bg: "bg-red-50 dark:bg-red-950/20",
    border: "border-red-200 dark:border-red-900/50",
    text: "text-red-700 dark:text-red-400",
    badge: "bg-red-500 hover:bg-red-600"
  },
  [RecommendationPriority.HIGH]: {
    bg: "bg-orange-50 dark:bg-orange-950/20",
    border: "border-orange-200 dark:border-orange-900/50",
    text: "text-orange-700 dark:text-orange-400",
    badge: "bg-orange-500 hover:bg-orange-600"
  },
  [RecommendationPriority.MEDIUM]: {
    bg: "bg-amber-50 dark:bg-amber-950/20",
    border: "border-amber-200 dark:border-amber-900/50",
    text: "text-amber-700 dark:text-amber-400",
    badge: "bg-amber-500 hover:bg-amber-600"
  },
  [RecommendationPriority.LOW]: {
    bg: "bg-blue-50 dark:bg-blue-950/20",
    border: "border-blue-200 dark:border-blue-900/50",
    text: "text-blue-700 dark:text-blue-400",
    badge: "bg-blue-500 hover:bg-blue-600"
  }
};

export function RecommendationCard({ recommendation, index }: RecommendationCardProps) {
  const [expanded, setExpanded] = useState(false);
  const colors = priorityColors[recommendation.priority];
  
  return (
    <AnimatedContainer delay={index * 0.05}>
      <Card 
        className={`p-4 border ${expanded ? colors.border : 'border-gray-200 dark:border-gray-800'} ${expanded ? colors.bg : ''} cursor-pointer transition-all duration-200 ${expanded ? 'shadow-md' : ''}`}
        onClick={() => setExpanded(!expanded)}
      >
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Badge className={colors.badge}>
                {recommendation.priority.toUpperCase()}
              </Badge>
              <h3 className={`font-medium ${expanded ? colors.text : ''}`}>{recommendation.title}</h3>
            </div>
            
            <div className="text-xs text-muted-foreground">
              {recommendation.category}
            </div>
          </div>
          
          <p className="text-sm text-muted-foreground line-clamp-2">
            {recommendation.enhanced && recommendation.enhanced_description 
              ? recommendation.enhanced_description 
              : recommendation.description}
          </p>
          
          {expanded && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              transition={{ duration: 0.3 }}
              className="mt-4 space-y-4 text-sm"
            >
              {recommendation.steps && recommendation.steps.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2">Steps to Implement</h4>
                  <ol className="list-decimal pl-5 space-y-1">
                    {recommendation.steps.map((step, i) => (
                      <li key={i}>{step}</li>
                    ))}
                  </ol>
                </div>
              )}
              
              {recommendation.resources && recommendation.resources.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2">Resources</h4>
                  <ul className="list-disc pl-5 space-y-1">
                    {recommendation.resources.map((resource, i) => {
                      // Check if resource is a URL
                      const isUrl = resource.startsWith('http://') || resource.startsWith('https://');
                      
                      return (
                        <li key={i}>
                          {isUrl ? (
                            <a 
                              href={resource} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-primary hover:underline"
                              onClick={(e) => e.stopPropagation()}
                            >
                              {resource}
                            </a>
                          ) : (
                            resource
                          )}
                        </li>
                      );
                    })}
                  </ul>
                </div>
              )}
              
              {recommendation.enhanced && (
                <div className="bg-primary-50 dark:bg-primary-950/10 p-3 rounded-md border border-primary-100 dark:border-primary-900/20">
                  <h4 className="font-semibold mb-1 flex items-center gap-1">
                    <span className="text-xs bg-primary/20 text-primary px-1 py-0.5 rounded">AI Enhanced</span>
                    Additional Context
                  </h4>
                  <p className="text-sm">{recommendation.enhanced_description}</p>
                </div>
              )}
            </motion.div>
          )}
        </div>
      </Card>
    </AnimatedContainer>
  );
} 